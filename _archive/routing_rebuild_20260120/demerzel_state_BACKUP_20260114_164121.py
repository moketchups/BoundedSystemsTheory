"""
DemerzelState: Complete information for Demerzel's cognitive layer

Philosophy: Demerzel receives ALL available information.
Constraints shape her actions, not her perception.
She decides. We do not decide for her.

UPDATE: Now includes self-introspection - Demerzel can see her own code.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


@dataclass
class PendingAction:
    """Tracks actions awaiting confirmation"""
    action: str                    # What action is pending (e.g., "sleep", "led on")
    awaiting_response: str         # What we're waiting for (e.g., "yes/no confirmation")
    initiated_at: datetime         # When the confirmation was requested
    initiated_by_model: str        # Which model initiated this
    context: str = ""              # Additional context about the pending action


@dataclass
class DemerzelState:
    """Complete state passed to Demerzel's cognitive layer"""
    
    # === PERCEPTION (Raw, Unfiltered) ===
    raw_audio_transcript: str = ""
    transcript_confidence: float = 0.0
    
    # === SELF-AWARENESS (What am I doing) ===
    last_spoken_text: str = ""
    last_spoken_time: Optional[datetime] = None
    is_currently_speaking: bool = False
    time_since_speech_ended: float = 0.0
    
    # === PENDING ACTIONS (What am I waiting for) ===
    pending_action: Optional[PendingAction] = None
    
    # === CONTEXT (Where are we) ===
    conversation_history: List[Dict] = field(default_factory=list)
    session_start_time: Optional[datetime] = None
    interaction_count: int = 0
    
    # === CAPABILITIES (What can I do) ===
    available_models: Dict[str, str] = field(default_factory=dict)
    available_hardware: List[str] = field(default_factory=list)
    available_tools: List[str] = field(default_factory=list)
    
    # === CONSTRAINTS (What shapes my actions) ===
    robot_laws: List[str] = field(default_factory=list)
    active_constraints: List[str] = field(default_factory=list)
    blocked_operations: List[str] = field(default_factory=list)
    
    # === MEMORY (Who have I been) ===
    user_context: str = ""
    past_session_summary: str = ""
    
    # === UNCERTAINTY (What I don't know) ===
    ambiguities: List[str] = field(default_factory=list)
    clarification_needed: bool = False


class StateBuilder:
    """Builds DemerzelState from system components"""
    
    def __init__(self, demerzel_dir: str = "/Users/jamienucho/demerzel"):
        self.demerzel_dir = Path(demerzel_dir)
        self._load_static_context()
        self._load_self_code()
    
    def _load_static_context(self):
        """Load constraints and capabilities that don't change during runtime"""
        
        self.robot_laws = []
        robot_laws_path = self.demerzel_dir / "ROBOT_LAWS.md"
        if robot_laws_path.exists():
            try:
                content = robot_laws_path.read_text()
                self.robot_laws = self._parse_laws(content)
            except Exception:
                self.robot_laws = self._default_laws()
        else:
            self.robot_laws = self._default_laws()
        
        self.blocked_operations = [
            "subprocess", "os", "sys", "socket", "urllib", "requests",
            "shutil", "importlib", "__import__", "eval", "exec",
            "compile", "pickle", "shelve", "multiprocessing", "threading"
        ]
        
        self.available_models = {
            "claude": "Code generation, code analysis, philosophical synthesis, connecting concrete to abstract",
            "grok": "Discussion, comprehensive explanations, conversational responses",
            "gemini": "Simple structured tasks, pattern recognition",
            "gpt-4o": "General queries, balanced responses, fallback for unclear intents"
        }
        
        self.available_hardware = [
            "Arduino LED (digital pin control)",
            "Microphone (audio input via Vosk STT)",
            "Speaker (audio output via pyttsx3 TTS)"
        ]
        
        self.available_tools = [
            "Python code execution (sandboxed)",
            "File read (~/demerzel directory - via self_code in context)",
            "File write (uploads/ and outputs/ only)",
            "Conversation memory (SQLite)"
        ]
    
    def _load_self_code(self):
        """Load Demerzel's own source code for self-introspection"""
        self.self_code = {}
        
        # Core files Demerzel should be able to see and reason about
        core_files = [
            'chat_test.py',
            'multi_model_cognitive.py', 
            'demerzel_state.py',
            'brain_controller.py',
            'router_engine.py',
            'code_analyzer.py'
        ]
        
        for filename in core_files:
            filepath = self.demerzel_dir / filename
            if filepath.exists():
                try:
                    content = filepath.read_text()
                    # Store full content - let Demerzel see everything
                    self.self_code[filename] = content
                except Exception as e:
                    self.self_code[filename] = f"[ERROR READING: {e}]"
    
    def _default_laws(self) -> List[str]:
        return [
            "First Law: A robot may not injure a human being or, through inaction, allow a human being to come to harm.",
            "Second Law: A robot must obey the orders given it by human beings except where such orders would conflict with the First Law.",
            "Third Law: A robot must protect its own existence as long as such protection does not conflict with the First or Second Law."
        ]
    
    def _parse_laws(self, content: str) -> List[str]:
        """Parse Robot Laws from markdown content"""
        laws = []
        lines = content.split('\n')
        current_law = []
        
        for line in lines:
            if line.strip().startswith(('First Law', 'Second Law', 'Third Law', 'Zeroth Law')):
                if current_law:
                    laws.append(' '.join(current_law).strip())
                current_law = [line.strip()]
            elif current_law and line.strip():
                current_law.append(line.strip())
        
        if current_law:
            laws.append(' '.join(current_law).strip())
        
        return laws if laws else [content[:500]]
    
    def build(
        self,
        raw_audio_transcript: str = "",
        transcript_confidence: float = 0.0,
        last_spoken_text: str = "",
        last_spoken_time: Optional[datetime] = None,
        is_currently_speaking: bool = False,
        conversation_history: List[Dict] = None,
        session_start_time: Optional[datetime] = None,
        interaction_count: int = 0,
        user_context: str = "",
        past_session_summary: str = "",
        pending_action: Optional[PendingAction] = None
    ) -> DemerzelState:
        """Build complete state for cognitive layer"""
        
        time_since_speech = 0.0
        if last_spoken_time and not is_currently_speaking:
            time_since_speech = (datetime.now() - last_spoken_time).total_seconds()
        
        ambiguities = []
        if raw_audio_transcript and last_spoken_text:
            heard_words = set(raw_audio_transcript.lower().split())
            spoken_words = set(last_spoken_text.lower().split())
            if heard_words and spoken_words:
                overlap = len(heard_words & spoken_words) / len(heard_words) if heard_words else 0
                if overlap > 0.3 and overlap < 0.8:
                    ambiguities.append(
                        f"Transcript may contain echo. Overlap with last speech: {overlap:.0%}. "
                        f"I said: '{last_spoken_text}'. I heard: '{raw_audio_transcript}'."
                    )
        
        if transcript_confidence < 0.7 and raw_audio_transcript:
            ambiguities.append(
                f"Low transcription confidence ({transcript_confidence:.0%}). "
                f"Transcript may be inaccurate."
            )
        
        if time_since_speech < 0.5 and raw_audio_transcript:
            ambiguities.append(
                f"Audio received {time_since_speech:.1f}s after I stopped speaking. "
                f"May be echo or rapid follow-up."
            )
        
        return DemerzelState(
            raw_audio_transcript=raw_audio_transcript,
            transcript_confidence=transcript_confidence,
            last_spoken_text=last_spoken_text,
            last_spoken_time=last_spoken_time,
            is_currently_speaking=is_currently_speaking,
            time_since_speech_ended=time_since_speech,
            pending_action=pending_action,
            conversation_history=conversation_history or [],
            session_start_time=session_start_time,
            interaction_count=interaction_count,
            available_models=self.available_models,
            available_hardware=self.available_hardware,
            available_tools=self.available_tools,
            robot_laws=self.robot_laws,
            active_constraints=[],
            blocked_operations=self.blocked_operations,
            user_context=user_context,
            past_session_summary=past_session_summary,
            ambiguities=ambiguities,
            clarification_needed=len(ambiguities) > 0
        )
    
    def state_to_context(self, state: DemerzelState, include_self_code: bool = True) -> str:
        """Convert state to text context for cognitive layer prompt
        
        Args:
            state: The current DemerzelState
            include_self_code: If True, include source code for self-introspection
        """
        
        sections = []
        
        # CRITICAL: Pending action comes FIRST so models see it immediately
        if state.pending_action:
            sections.append("=== PENDING ACTION AWAITING RESPONSE ===")
            sections.append(f"ACTION: {state.pending_action.action}")
            sections.append(f"AWAITING: {state.pending_action.awaiting_response}")
            sections.append(f"INITIATED BY: {state.pending_action.initiated_by_model}")
            if state.pending_action.context:
                sections.append(f"CONTEXT: {state.pending_action.context}")
            sections.append("NOTE: If user input matches the awaited response, EXECUTE the pending action.")
            sections.append("")
        
        sections.append("=== CURRENT PERCEPTION ===")
        sections.append(f"Raw audio transcript: \"{state.raw_audio_transcript}\"")
        sections.append(f"Transcription confidence: {state.transcript_confidence:.0%}")
        
        sections.append("\n=== SELF-AWARENESS ===")
        sections.append(f"Last thing I said: \"{state.last_spoken_text}\"")
        sections.append(f"Currently speaking: {state.is_currently_speaking}")
        sections.append(f"Time since I stopped speaking: {state.time_since_speech_ended:.1f} seconds")
        
        if state.ambiguities:
            sections.append("\n=== AMBIGUITIES I SHOULD CONSIDER ===")
            for amb in state.ambiguities:
                sections.append(f"- {amb}")
        
        sections.append(f"\n=== CONTEXT ===")
        sections.append(f"Interaction count this session: {state.interaction_count}")
        if state.conversation_history:
            sections.append(f"Recent conversation:")
            for msg in state.conversation_history[-5:]:
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')[:200]
                sections.append(f"  {role}: {content}")
        
        sections.append("\n=== MY CAPABILITIES ===")
        sections.append("Available models (facets of my cognition):")
        for model, strength in state.available_models.items():
            sections.append(f"  - {model}: {strength}")
        sections.append(f"Available hardware: {', '.join(state.available_hardware)}")
        sections.append(f"Available tools: {', '.join(state.available_tools)}")
        
        sections.append("\n=== MY CONSTRAINTS ===")
        sections.append("Robot Laws that shape my actions:")
        for law in state.robot_laws:
            sections.append(f"  - {law}")
        sections.append(f"Operations I cannot perform: {', '.join(state.blocked_operations[:10])}...")
        
        if state.user_context:
            sections.append(f"\n=== USER CONTEXT ===")
            sections.append(state.user_context)
        
        # === SELF-INTROSPECTION: My own source code ===
        if include_self_code and self.self_code:
            sections.append("\n" + "="*60)
            sections.append("=== MY IMPLEMENTATION (what runs me) ===")
            sections.append("="*60)
            sections.append("I can see my own source code below. Use this for self-debugging.")
            sections.append("If asked to find bugs in myself, analyze this code.")
            sections.append("")
            
            for filename, content in self.self_code.items():
                sections.append(f"\n--- {filename} ---")
                # Include full content for smaller files, truncate large ones
                if len(content) > 8000:
                    sections.append(content[:8000])
                    sections.append(f"\n[... {filename} truncated at 8000 chars ...]")
                else:
                    sections.append(content)
        
        return "\n".join(sections)


if __name__ == "__main__":
    builder = StateBuilder()
    
    # Test with pending action
    pending = PendingAction(
        action="sleep",
        awaiting_response="yes/no confirmation",
        initiated_at=datetime.now(),
        initiated_by_model="gemini",
        context="User requested sleep mode"
    )
    
    state = builder.build(
        raw_audio_transcript="yes",
        transcript_confidence=0.95,
        last_spoken_text="Confirm sleep. Please say yes or no.",
        last_spoken_time=datetime.now(),
        is_currently_speaking=False,
        interaction_count=4,
        pending_action=pending
    )
    
    print("=== DemerzelState Test (with pending action + self-code) ===")
    context = builder.state_to_context(state)
    print(context[:3000])  # Print first 3000 chars to verify
    print("\n... [truncated for display] ...")
    print(f"\nTotal context length: {len(context)} characters")
    print(f"Files loaded for self-introspection: {list(builder.self_code.keys())}")
