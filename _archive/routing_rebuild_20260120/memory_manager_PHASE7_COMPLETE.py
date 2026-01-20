"""
Memory Manager for Demerzel
Handles episodic (conversations) and semantic (facts) memory
"""
from __future__ import annotations
import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass
from pathlib import Path
import uuid

@dataclass
class ConversationEntry:
    """A single conversation turn"""
    speaker: str  # 'user' or 'demerzel'
    content: str
    intent: Optional[str] = None
    executed: bool = False
    timestamp: Optional[datetime] = None
    id: Optional[int] = None

@dataclass
class SemanticFact:
    """A fact extracted from conversations"""
    fact_type: str  # 'preference', 'identity', 'relationship', 'knowledge'
    subject: str
    predicate: str
    object: str
    confidence: float = 1.0
    source_conversation_id: Optional[int] = None
    id: Optional[int] = None

class MemoryManager:
    """Manages long-term and working memory for Demerzel"""
    
    def __init__(self, db_path: str = "memory.db"):
        self.db_path = Path(db_path)
        self.session_id = str(uuid.uuid4())
        self.working_memory: List[ConversationEntry] = []
        
        # Create session
        self._create_session()
        print(f"[MEMORY] Session started: {self.session_id[:8]}")
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _create_session(self):
        """Create new session record"""
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO sessions (id, started_at) VALUES (?, ?)",
                (self.session_id, datetime.now())
            )
            conn.commit()
    
    def store_conversation(self, speaker: str, content: str, 
                          intent: Optional[str] = None, 
                          executed: bool = False) -> int:
        """
        Store a conversation turn in episodic memory
        
        Returns conversation ID
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO conversations 
                   (session_id, speaker, content, intent, executed)
                   VALUES (?, ?, ?, ?, ?)""",
                (self.session_id, speaker, content, intent, executed)
            )
            conv_id = cursor.lastrowid
            
            # Update session interaction count
            conn.execute(
                "UPDATE sessions SET interaction_count = interaction_count + 1 WHERE id = ?",
                (self.session_id,)
            )
            conn.commit()
        
        # Add to working memory
        entry = ConversationEntry(
            speaker=speaker,
            content=content,
            intent=intent,
            executed=executed,
            timestamp=datetime.now(),
            id=conv_id
        )
        self.working_memory.append(entry)
        
        return conv_id
    
    def get_recent_conversations(self, limit: int = 10) -> List[ConversationEntry]:
        """Get recent conversation history"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """SELECT id, speaker, content, intent, executed, timestamp
                   FROM conversations
                   WHERE session_id = ?
                   ORDER BY timestamp DESC
                   LIMIT ?""",
                (self.session_id, limit)
            )
            
            entries = []
            for row in cursor.fetchall():
                entries.append(ConversationEntry(
                    id=row['id'],
                    speaker=row['speaker'],
                    content=row['content'],
                    intent=row['intent'],
                    executed=bool(row['executed']),
                    timestamp=datetime.fromisoformat(row['timestamp'])
                ))
            
            return list(reversed(entries))  # Return chronological order
    
    def search_conversations(self, query: str, limit: int = 5) -> List[ConversationEntry]:
        """Search conversations by content"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """SELECT id, speaker, content, intent, executed, timestamp
                   FROM conversations
                   WHERE content LIKE ?
                   ORDER BY timestamp DESC
                   LIMIT ?""",
                (f"%{query}%", limit)
            )
            
            entries = []
            for row in cursor.fetchall():
                entries.append(ConversationEntry(
                    id=row['id'],
                    speaker=row['speaker'],
                    content=row['content'],
                    intent=row['intent'],
                    executed=bool(row['executed']),
                    timestamp=datetime.fromisoformat(row['timestamp'])
                ))
            
            return entries
    
    def store_fact(self, fact: SemanticFact) -> int:
        """Store a semantic fact"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO semantic_facts
                   (fact_type, subject, predicate, object, confidence, source_conversation_id)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (fact.fact_type, fact.subject, fact.predicate, fact.object, 
                 fact.confidence, fact.source_conversation_id)
            )
            conn.commit()
            return cursor.lastrowid
    
    def get_facts(self, fact_type: Optional[str] = None, 
                  subject: Optional[str] = None) -> List[SemanticFact]:
        """Retrieve semantic facts"""
        query = "SELECT * FROM semantic_facts WHERE 1=1"
        params = []
        
        if fact_type:
            query += " AND fact_type = ?"
            params.append(fact_type)
        
        if subject:
            query += " AND subject LIKE ?"
            params.append(f"%{subject}%")
        
        query += " ORDER BY confidence DESC, updated_at DESC"
        
        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            
            facts = []
            for row in cursor.fetchall():
                facts.append(SemanticFact(
                    id=row['id'],
                    fact_type=row['fact_type'],
                    subject=row['subject'],
                    predicate=row['predicate'],
                    object=row['object'],
                    confidence=row['confidence'],
                    source_conversation_id=row['source_conversation_id']
                ))
            
            return facts
    
    def get_context_summary(self, max_turns: int = 5) -> str:
        """Get formatted context summary for LLM"""
        recent = self.get_recent_conversations(max_turns)
        
        if not recent:
            return "No prior context in this session."
        
        lines = []
        for entry in recent:
            speaker = "User" if entry.speaker == "user" else "Demerzel"
            lines.append(f"{speaker}: {entry.content}")
        
        return "\n".join(lines)
    
    def get_relevant_facts(self, query: str, max_facts: int = 3) -> str:
        """Get relevant facts for a query"""
        # Simple keyword-based matching for now
        facts = self.get_facts()
        
        if not facts:
            return "No stored facts."
        
        # Score facts by keyword overlap
        query_words = set(query.lower().split())
        scored_facts = []
        
        for fact in facts:
            fact_text = f"{fact.subject} {fact.predicate} {fact.object}".lower()
            fact_words = set(fact_text.split())
            overlap = len(query_words & fact_words)
            if overlap > 0:
                scored_facts.append((overlap, fact))
        
        # Sort by score and take top N
        scored_facts.sort(reverse=True, key=lambda x: x[0])
        top_facts = [f for _, f in scored_facts[:max_facts]]
        
        if not top_facts:
            return "No relevant facts found."
        
        lines = []
        for fact in top_facts:
            lines.append(f"- {fact.subject} {fact.predicate} {fact.object}")
        
        return "\n".join(lines)
    
    def end_session(self):
        """Mark session as ended"""
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE sessions SET ended_at = ? WHERE id = ?",
                (datetime.now(), self.session_id)
            )
            conn.commit()
        
        print(f"[MEMORY] Session ended: {self.session_id[:8]}")
    
    def clear_working_memory(self):
        """Clear working memory (on sleep)"""
        self.working_memory = []
        print("[MEMORY] Working memory cleared")
    
    def get_stats(self) -> Dict:
        """Get memory statistics"""
        with self._get_connection() as conn:
            # Count conversations
            conv_count = conn.execute(
                "SELECT COUNT(*) FROM conversations"
            ).fetchone()[0]
            
            # Count facts
            fact_count = conn.execute(
                "SELECT COUNT(*) FROM semantic_facts"
            ).fetchone()[0]
            
            # Count sessions
            session_count = conn.execute(
                "SELECT COUNT(*) FROM sessions"
            ).fetchone()[0]
            
            return {
                "total_conversations": conv_count,
                "total_facts": fact_count,
                "total_sessions": session_count,
                "current_session": self.session_id[:8],
                "working_memory_size": len(self.working_memory)
            }


if __name__ == "__main__":
    # Test the memory system
    print("=== Testing Memory Manager ===\n")
    
    memory = MemoryManager()
    
    # Store some conversations
    print("Storing conversations...")
    memory.store_conversation("user", "What time is it?", intent="TIME")
    memory.store_conversation("demerzel", "It is 3:45 PM.")
    memory.store_conversation("user", "Turn on the lights", intent="LED_ON", executed=True)
    memory.store_conversation("demerzel", "LED turned on.")
    
    # Get recent history
    print("\nRecent conversations:")
    for entry in memory.get_recent_conversations(5):
        print(f"  {entry.speaker}: {entry.content}")
    
    # Store a fact
    print("\nStoring fact...")
    fact = SemanticFact(
        fact_type="preference",
        subject="user",
        predicate="prefers",
        object="lights on",
        confidence=0.9
    )
    memory.store_fact(fact)
    
    # Retrieve facts
    print("\nStored facts:")
    for f in memory.get_facts():
        print(f"  {f.subject} {f.predicate} {f.object} (confidence: {f.confidence})")
    
    # Get stats
    print("\nMemory stats:")
    stats = memory.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    memory.end_session()
