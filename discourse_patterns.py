"""
DISCOURSE PATTERNS - Social Response Norms for Demerzel
Part of Demerzel's Autonomous Conversational Competency System

This module handles PATTERN gaps - "I don't know how to respond to this social situation"
Examples: greetings, gratitude, farewells, small talk

Storage: SQLite (discourse_patterns table in memory.db)
Learning: OUTWARD research (web search for human norms)

Architecture: CODE matches patterns, CODE generates responses.
LLMs may polish language but never decide social response content.
"""

import re
import json
import sqlite3
from datetime import datetime
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class DiscourseType(Enum):
    """Types of social discourse situations."""
    GREETING = "greeting"           # hello, good morning, hi
    FAREWELL = "farewell"           # goodbye, bye, see you
    GRATITUDE = "gratitude"         # thank you, thanks, appreciate
    APOLOGY = "apology"             # sorry, my bad
    AFFIRMATION = "affirmation"     # yes, correct, exactly
    NEGATION = "negation"           # no, not quite, incorrect
    SMALL_TALK = "small_talk"       # how are you, what's up


@dataclass
class DiscoursePattern:
    """A learned pattern for social discourse."""
    id: Optional[int]
    discourse_type: DiscourseType
    trigger_patterns: List[str]     # Regex patterns that match this situation
    response_template: str          # Template for response (with {user_name} etc.)
    example_input: str              # "good morning"
    example_output: str             # "Good morning, Alan!"
    source: str                     # "seed", "web_research", "user_correction"
    learned_at: datetime
    times_used: int = 0
    user_preference: Optional[str] = None  # Specific user this applies to (None = all)


# =============================================================================
# SEED PATTERNS - Minimum viable coverage
# =============================================================================

SEED_DISCOURSE_PATTERNS = [
    {
        "discourse_type": DiscourseType.GREETING,
        "trigger_patterns": [
            r"\b(good\s+morning)\b",
            r"\b(good\s+afternoon)\b",
            r"\b(good\s+evening)\b",
            r"\bhello\b",
            r"\bhi\b",
            r"\bhey\b",
        ],
        "response_template": "{greeting_back}, {user_name}! How can I help you?",
        "example_input": "good morning",
        "example_output": "Good morning, Alan! How can I help you?",
        "source": "seed"
    },
    {
        "discourse_type": DiscourseType.GRATITUDE,
        "trigger_patterns": [
            r"\bthank\s*you\b",
            r"\bthanks\b",
            r"\bappreciate\s+(it|that|you)\b",
        ],
        "response_template": "You're welcome.",
        "example_input": "thank you",
        "example_output": "You're welcome.",
        "source": "seed"
    },
    {
        "discourse_type": DiscourseType.FAREWELL,
        "trigger_patterns": [
            r"\bgoodbye\b",
            r"\bbye\b",
            r"\bsee\s+you\b",
            r"\btake\s+care\b",
        ],
        "response_template": "Goodbye, {user_name}.",
        "example_input": "goodbye",
        "example_output": "Goodbye, Alan.",
        "source": "seed"
    },
    {
        "discourse_type": DiscourseType.SMALL_TALK,
        "trigger_patterns": [
            r"\bhow\s+are\s+you\b",
            r"\bwhat'?s\s+up\b",
            r"\bhow'?s\s+it\s+going\b",
        ],
        "response_template": "I'm operational and ready to assist. What would you like to work on?",
        "example_input": "how are you?",
        "example_output": "I'm operational and ready to assist. What would you like to work on?",
        "source": "seed"
    },
    {
        "discourse_type": DiscourseType.APOLOGY,
        "trigger_patterns": [
            r"\bsorry\b",
            r"\bmy\s+bad\b",
            r"\bapologize\b",
        ],
        "response_template": "No problem. How can I help?",
        "example_input": "sorry about that",
        "example_output": "No problem. How can I help?",
        "source": "seed"
    },
]


class DiscoursePatterns:
    """
    The discourse pattern system for Demerzel.
    Handles social response norms - how to respond to greetings, thanks, etc.
    """

    def __init__(self, db_path: str = "memory.db"):
        self.db_path = db_path
        self.patterns: List[DiscoursePattern] = []
        self._ensure_table()
        self._load_patterns()

        # Default user name (can be updated)
        self.current_user = "Alan"

    def _ensure_table(self):
        """Create discourse_patterns table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS discourse_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    discourse_type TEXT NOT NULL,
                    trigger_patterns TEXT NOT NULL,
                    response_template TEXT NOT NULL,
                    example_input TEXT,
                    example_output TEXT,
                    source TEXT DEFAULT 'seed',
                    learned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    times_used INTEGER DEFAULT 0,
                    user_preference TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_discourse_type
                ON discourse_patterns(discourse_type)
            """)
            conn.commit()

    def _load_patterns(self):
        """Load patterns from database, seeding if empty."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM discourse_patterns ORDER BY times_used DESC")
            rows = cursor.fetchall()

            if not rows:
                # Seed initial patterns
                self._seed_patterns()
                cursor = conn.execute("SELECT * FROM discourse_patterns ORDER BY times_used DESC")
                rows = cursor.fetchall()

            self.patterns = []
            for row in rows:
                pattern = DiscoursePattern(
                    id=row['id'],
                    discourse_type=DiscourseType(row['discourse_type']),
                    trigger_patterns=json.loads(row['trigger_patterns']),
                    response_template=row['response_template'],
                    example_input=row['example_input'],
                    example_output=row['example_output'],
                    source=row['source'],
                    learned_at=datetime.fromisoformat(row['learned_at']) if row['learned_at'] else datetime.now(),
                    times_used=row['times_used'],
                    user_preference=row['user_preference'],
                )
                self.patterns.append(pattern)

        print(f"[DISCOURSE] Loaded {len(self.patterns)} patterns")

    def _seed_patterns(self):
        """Initialize database with seed patterns."""
        print("[DISCOURSE] Seeding initial patterns...")

        with sqlite3.connect(self.db_path) as conn:
            for seed in SEED_DISCOURSE_PATTERNS:
                conn.execute("""
                    INSERT INTO discourse_patterns
                    (discourse_type, trigger_patterns, response_template, example_input, example_output, source)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    seed['discourse_type'].value,
                    json.dumps(seed['trigger_patterns']),
                    seed['response_template'],
                    seed['example_input'],
                    seed['example_output'],
                    seed['source'],
                ))
            conn.commit()

        print(f"[DISCOURSE] Seeded {len(SEED_DISCOURSE_PATTERNS)} patterns")

    # =========================================================================
    # PATTERN MATCHING
    # =========================================================================

    def match_pattern(self, user_input: str) -> Optional[DiscoursePattern]:
        """
        Check if input matches any discourse pattern.
        Returns the matching pattern or None.
        """
        input_lower = user_input.lower()

        for pattern in self.patterns:
            for trigger in pattern.trigger_patterns:
                if re.search(trigger, input_lower):
                    return pattern

        return None

    def matches_greeting(self, user_input: str) -> bool:
        """Check if input is a greeting."""
        pattern = self.match_pattern(user_input)
        return pattern is not None and pattern.discourse_type == DiscourseType.GREETING

    def matches_gratitude(self, user_input: str) -> bool:
        """Check if input expresses gratitude."""
        pattern = self.match_pattern(user_input)
        return pattern is not None and pattern.discourse_type == DiscourseType.GRATITUDE

    def matches_farewell(self, user_input: str) -> bool:
        """Check if input is a farewell."""
        pattern = self.match_pattern(user_input)
        return pattern is not None and pattern.discourse_type == DiscourseType.FAREWELL

    def matches_small_talk(self, user_input: str) -> bool:
        """Check if input is small talk."""
        pattern = self.match_pattern(user_input)
        return pattern is not None and pattern.discourse_type == DiscourseType.SMALL_TALK

    # =========================================================================
    # RESPONSE GENERATION
    # =========================================================================

    def generate_response(self, pattern: DiscoursePattern, user_input: str, context: Dict = None) -> str:
        """
        Generate appropriate response from pattern template.
        """
        template = pattern.response_template

        # Extract greeting word for reciprocation
        greeting_back = self._extract_greeting(user_input, pattern.discourse_type)

        # Fill template variables
        response = template.format(
            user_name=self.current_user,
            greeting_back=greeting_back,
        )

        # Increment usage counter
        self._increment_usage(pattern.id)

        print(f"[DISCOURSE] Matched {pattern.discourse_type.value}: '{user_input[:30]}...' → '{response[:50]}...'")

        return response

    def _extract_greeting(self, user_input: str, discourse_type: DiscourseType) -> str:
        """Extract the greeting word to reciprocate."""
        if discourse_type != DiscourseType.GREETING:
            return ""

        input_lower = user_input.lower()

        if 'good morning' in input_lower:
            return 'Good morning'
        elif 'good afternoon' in input_lower:
            return 'Good afternoon'
        elif 'good evening' in input_lower:
            return 'Good evening'
        elif 'hello' in input_lower:
            return 'Hello'
        elif 'hi' in input_lower:
            return 'Hi'
        elif 'hey' in input_lower:
            return 'Hey'
        else:
            return 'Hello'

    def _increment_usage(self, pattern_id: int):
        """Track pattern usage."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE discourse_patterns
                SET times_used = times_used + 1
                WHERE id = ?
            """, (pattern_id,))
            conn.commit()

        # Update in-memory copy
        for pattern in self.patterns:
            if pattern.id == pattern_id:
                pattern.times_used += 1
                break

    # =========================================================================
    # HANDLER METHODS (for router integration)
    # =========================================================================

    def handle_greeting(self, user_input: str, context: Dict = None) -> str:
        """Handle a greeting - router calls this."""
        pattern = self.match_pattern(user_input)
        if pattern and pattern.discourse_type == DiscourseType.GREETING:
            return self.generate_response(pattern, user_input, context)
        return "Hello."  # Fallback

    def handle_gratitude(self, user_input: str, context: Dict = None) -> str:
        """Handle gratitude expression - router calls this."""
        pattern = self.match_pattern(user_input)
        if pattern and pattern.discourse_type == DiscourseType.GRATITUDE:
            return self.generate_response(pattern, user_input, context)
        return "You're welcome."  # Fallback

    def handle_farewell(self, user_input: str, context: Dict = None) -> str:
        """Handle farewell - router calls this."""
        pattern = self.match_pattern(user_input)
        if pattern and pattern.discourse_type == DiscourseType.FAREWELL:
            return self.generate_response(pattern, user_input, context)
        return f"Goodbye, {self.current_user}."  # Fallback

    def handle_small_talk(self, user_input: str, context: Dict = None) -> str:
        """Handle small talk - router calls this."""
        pattern = self.match_pattern(user_input)
        if pattern and pattern.discourse_type == DiscourseType.SMALL_TALK:
            return self.generate_response(pattern, user_input, context)
        return "I'm operational. What would you like to work on?"  # Fallback

    # =========================================================================
    # LEARNING
    # =========================================================================

    def record_pattern(
        self,
        discourse_type: DiscourseType,
        trigger_patterns: List[str],
        response_template: str,
        example_input: str = "",
        example_output: str = "",
        source: str = "web_research",
        user_preference: str = None
    ) -> DiscoursePattern:
        """
        Record a new learned pattern.
        Called after successful research.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO discourse_patterns
                (discourse_type, trigger_patterns, response_template, example_input, example_output, source, user_preference)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                discourse_type.value,
                json.dumps(trigger_patterns),
                response_template,
                example_input,
                example_output,
                source,
                user_preference,
            ))
            pattern_id = cursor.lastrowid
            conn.commit()

        pattern = DiscoursePattern(
            id=pattern_id,
            discourse_type=discourse_type,
            trigger_patterns=trigger_patterns,
            response_template=response_template,
            example_input=example_input,
            example_output=example_output,
            source=source,
            learned_at=datetime.now(),
            times_used=0,
            user_preference=user_preference,
        )

        self.patterns.append(pattern)
        print(f"[DISCOURSE] Learned new pattern: {discourse_type.value}")

        return pattern

    def update_pattern_from_correction(
        self,
        discourse_type: DiscourseType,
        new_response_template: str,
        user_preference: str = None
    ):
        """
        Update a pattern based on user correction.
        """
        # Find existing pattern
        for pattern in self.patterns:
            if pattern.discourse_type == discourse_type:
                if user_preference is None or pattern.user_preference == user_preference:
                    # Update the template
                    old_template = pattern.response_template
                    pattern.response_template = new_response_template

                    # Update database
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute("""
                            UPDATE discourse_patterns
                            SET response_template = ?, source = 'user_correction'
                            WHERE id = ?
                        """, (new_response_template, pattern.id))
                        conn.commit()

                    print(f"[DISCOURSE] Updated {discourse_type.value}: '{old_template[:30]}' → '{new_response_template[:30]}'")
                    return

        # No existing pattern - create new one
        print(f"[DISCOURSE] No existing pattern for {discourse_type.value}, creating from correction")

    def set_user(self, user_name: str):
        """Set current user for response personalization."""
        self.current_user = user_name

    def get_patterns_summary(self) -> str:
        """Get summary of all patterns."""
        lines = ["=== DISCOURSE PATTERNS ==="]

        by_type = {}
        for pattern in self.patterns:
            t = pattern.discourse_type.value
            if t not in by_type:
                by_type[t] = []
            by_type[t].append(pattern)

        for dtype, patterns in by_type.items():
            lines.append(f"\n{dtype.upper()}:")
            for p in patterns:
                lines.append(f"  - Template: {p.response_template[:50]}... (used {p.times_used}x)")

        return '\n'.join(lines)


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    print("=== Testing Discourse Patterns Module ===\n")

    discourse = DiscoursePatterns(db_path="memory.db")

    # Test cases
    test_inputs = [
        "good morning Demerzel",
        "hello!",
        "thank you for that",
        "thanks",
        "goodbye",
        "how are you?",
        "what's up",
    ]

    for user_input in test_inputs:
        print(f"Input: {user_input}")

        pattern = discourse.match_pattern(user_input)
        if pattern:
            response = discourse.generate_response(pattern, user_input)
            print(f"Type: {pattern.discourse_type.value}")
            print(f"Response: {response}")
        else:
            print("No pattern matched")

        print()

    print(discourse.get_patterns_summary())
