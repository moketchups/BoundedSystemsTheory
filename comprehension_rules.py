"""
COMPREHENSION RULES - Understanding User Intent for Demerzel
Part of Demerzel's Autonomous Conversational Competency System

This module handles COMPREHENSION gaps - "I don't understand what they mean"
Examples:
- "I'm about to upload" → NOT "I don't have context" but "Understood, ready."
- User correcting us → Extract the teaching, not treat as conversation
- Reference tracking → Find what they're referring to, not claim amnesia

Storage: SQLite (comprehension_rules table in memory.db)
Learning: OUTWARD research (web search for pragmatics, dialogue patterns)

Architecture: CODE parses intent, CODE generates appropriate response.
This runs BEFORE the broken existing flow to prevent failures.
"""

import re
import json
import sqlite3
from datetime import datetime
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class ComprehensionType(Enum):
    """Types of comprehension situations requiring special handling."""
    INSTRUCTION_SETUP = "instruction_setup"     # "I'm about to do X, got it?"
    REFERENCE_TRACKING = "reference_tracking"   # "that thing we discussed"
    IMPLIED_REQUEST = "implied_request"         # "It's cold in here" = close window
    DIALOGUE_STATE = "dialogue_state"           # tracking conversation flow
    INTENT_BEHIND_WORDS = "intent_behind_words" # meaning vs literal words
    CORRECTION_INTENT = "correction_intent"     # user is teaching, not just talking


@dataclass
class ComprehensionRule:
    """A learned rule for understanding user intent."""
    id: Optional[int]
    comprehension_type: ComprehensionType
    trigger_patterns: List[str]         # Patterns that indicate this situation
    understanding_strategy: str         # How to process this type of input
    example_input: str
    correct_understanding: str          # What the input ACTUALLY means
    incorrect_understanding: str        # Common misunderstanding to avoid
    source: str
    learned_at: datetime
    times_applied: int = 0


# =============================================================================
# SEED COMPREHENSION RULES - Critical for solving known failures
# =============================================================================

SEED_COMPREHENSION_RULES = [
    {
        "comprehension_type": ComprehensionType.INSTRUCTION_SETUP,
        "trigger_patterns": [
            r"(i'm|im|i am)\s+(going to|gonna|about to)",
            r"before\s+i\s+(do|start|begin|upload|send)",
            r"(just\s+)?(want|wanna)\s+(to\s+)?make\s+sure",
            r"(got\s+it|understand|ready|comprehend|follow)\s*\?",
            r"confirm(ing)?\s+(you\s+)?(understand|got|ready)",
        ],
        "understanding_strategy": "User is ANNOUNCING a future action and requesting acknowledgment. They want confirmation of readiness, NOT help with the action yet. Never say 'I don't have context.'",
        "example_input": "I'm going to upload a document. Just confirming you understand.",
        "correct_understanding": "User will upload something soon. They want me to confirm I'm ready to receive it.",
        "incorrect_understanding": "User needs help with something OR user is giving context I don't have",
        "source": "seed"
    },
    {
        "comprehension_type": ComprehensionType.INTENT_BEHIND_WORDS,
        "trigger_patterns": [
            r"you\s+(just\s+)?repeated",
            r"(don't|do not)\s+repeat",
            r"that\s+isn't\s+how",
            r"that's\s+not\s+how",
            r"not\s+what\s+i\s+(meant|asked)",
        ],
        "understanding_strategy": "User is correcting parrot behavior. Extract the teaching: what should I have understood? The MEANING behind their words, not just the text.",
        "example_input": "you just repeated what i said without thinking why i said it",
        "correct_understanding": "User is teaching me to understand PURPOSE behind words, not echo text.",
        "incorrect_understanding": "User is making a statement about repetition as a topic",
        "source": "seed"
    },
    {
        "comprehension_type": ComprehensionType.CORRECTION_INTENT,
        "trigger_patterns": [
            r"you\s+(should|could)\s+say",
            r"let'?s\s+work\s+on",
            r"try\s+saying",
            r"(work|working)\s+on\s+(those|your)\s+manners",
            r"that\s+was\s+(better|an\s+improvement)",
        ],
        "understanding_strategy": "User is TEACHING me. Extract: (1) what I did wrong, (2) what I should do instead. Update patterns accordingly.",
        "example_input": "you could say it back. lets work on those manners",
        "correct_understanding": "User is teaching me to reciprocate greetings. Update greeting pattern.",
        "incorrect_understanding": "User is making a suggestion or request",
        "source": "seed"
    },
    {
        "comprehension_type": ComprehensionType.REFERENCE_TRACKING,
        "trigger_patterns": [
            r"\b(that|this|it|those|these)\b.*\b(we|you|i)\s+(discussed|mentioned|talked)",
            r"(earlier|before|last\s+time)",
            r"(remember|recall)\s+when",
            r"you\s+(said|mentioned|told)",
        ],
        "understanding_strategy": "User is referring to conversation history. Search memory for the referent BEFORE responding. Do NOT say 'I don't have context.'",
        "example_input": "remember that document we discussed earlier?",
        "correct_understanding": "Search memory, find the document, reference it specifically.",
        "incorrect_understanding": "'I don't have context from earlier' - this is ALWAYS wrong when user references past conversation",
        "source": "seed"
    },
]


class ComprehensionRules:
    """
    The comprehension system for Demerzel.
    Handles understanding user intent beyond literal words.
    """

    def __init__(self, db_path: str = "memory.db"):
        self.db_path = db_path
        self.rules: List[ComprehensionRule] = []
        self._ensure_table()
        self._load_rules()

    def _ensure_table(self):
        """Create comprehension_rules table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS comprehension_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    comprehension_type TEXT NOT NULL,
                    trigger_patterns TEXT NOT NULL,
                    understanding_strategy TEXT NOT NULL,
                    example_input TEXT,
                    correct_understanding TEXT,
                    incorrect_understanding TEXT,
                    source TEXT DEFAULT 'seed',
                    learned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    times_applied INTEGER DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_comprehension_type
                ON comprehension_rules(comprehension_type)
            """)
            conn.commit()

    def _load_rules(self):
        """Load rules from database, seeding if empty."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM comprehension_rules ORDER BY times_applied DESC")
            rows = cursor.fetchall()

            if not rows:
                # Seed initial rules
                self._seed_rules()
                cursor = conn.execute("SELECT * FROM comprehension_rules ORDER BY times_applied DESC")
                rows = cursor.fetchall()

            self.rules = []
            for row in rows:
                rule = ComprehensionRule(
                    id=row['id'],
                    comprehension_type=ComprehensionType(row['comprehension_type']),
                    trigger_patterns=json.loads(row['trigger_patterns']),
                    understanding_strategy=row['understanding_strategy'],
                    example_input=row['example_input'],
                    correct_understanding=row['correct_understanding'],
                    incorrect_understanding=row['incorrect_understanding'],
                    source=row['source'],
                    learned_at=datetime.fromisoformat(row['learned_at']) if row['learned_at'] else datetime.now(),
                    times_applied=row['times_applied'],
                )
                self.rules.append(rule)

        print(f"[COMPREHENSION] Loaded {len(self.rules)} rules")

    def _seed_rules(self):
        """Initialize database with seed rules."""
        print("[COMPREHENSION] Seeding initial rules...")

        with sqlite3.connect(self.db_path) as conn:
            for seed in SEED_COMPREHENSION_RULES:
                conn.execute("""
                    INSERT INTO comprehension_rules
                    (comprehension_type, trigger_patterns, understanding_strategy,
                     example_input, correct_understanding, incorrect_understanding, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    seed['comprehension_type'].value,
                    json.dumps(seed['trigger_patterns']),
                    seed['understanding_strategy'],
                    seed['example_input'],
                    seed['correct_understanding'],
                    seed['incorrect_understanding'],
                    seed['source'],
                ))
            conn.commit()

        print(f"[COMPREHENSION] Seeded {len(SEED_COMPREHENSION_RULES)} rules")

    # =========================================================================
    # PATTERN MATCHING
    # =========================================================================

    def match_rule(self, user_input: str) -> Optional[ComprehensionRule]:
        """
        Check if input matches any comprehension rule.
        Returns the matching rule or None.
        """
        input_lower = user_input.lower()

        for rule in self.rules:
            for trigger in rule.trigger_patterns:
                if re.search(trigger, input_lower):
                    return rule

        return None

    def matches_instruction_setup(self, user_input: str) -> bool:
        """Check if input is an instruction setup."""
        rule = self.match_rule(user_input)
        return rule is not None and rule.comprehension_type == ComprehensionType.INSTRUCTION_SETUP

    def matches_correction_intent(self, user_input: str) -> bool:
        """Check if user is correcting/teaching us."""
        rule = self.match_rule(user_input)
        return rule is not None and rule.comprehension_type == ComprehensionType.CORRECTION_INTENT

    def matches_reference(self, user_input: str) -> bool:
        """Check if user is referencing past conversation."""
        rule = self.match_rule(user_input)
        return rule is not None and rule.comprehension_type == ComprehensionType.REFERENCE_TRACKING

    def matches_parrot_correction(self, user_input: str) -> bool:
        """Check if user is correcting parrot behavior."""
        rule = self.match_rule(user_input)
        return rule is not None and rule.comprehension_type == ComprehensionType.INTENT_BEHIND_WORDS

    # =========================================================================
    # INSTRUCTION SETUP HANDLING - THE KEY FIX
    # =========================================================================

    def parse_instruction_setup(self, user_input: str) -> Dict:
        """
        Parse an instruction setup to understand what user is announcing.

        Input: "I'm going to upload a document. Just confirming you understand."
        Output: {
            'type': 'instruction_setup',
            'announced_action': 'upload a document',
            'user_wants': 'confirmation of readiness',
            'correct_response_type': 'acknowledge_readiness',
        }
        """
        result = {
            'type': 'instruction_setup',
            'announced_action': None,
            'user_wants': 'confirmation of readiness',
            'correct_response_type': 'acknowledge_readiness',
            'WRONG_responses': [
                "I don't have context",
                "I don't understand",
                "Could you clarify",
                "What do you mean",
            ],
        }

        input_lower = user_input.lower()

        # Extract the announced action
        action_patterns = [
            r"(?:i'm|im|i am)\s+(?:going to|gonna|about to)\s+(.+?)(?:\.|,|just|$)",
            r"before\s+i\s+(.+?)(?:\.|,|$)",
        ]

        for pattern in action_patterns:
            match = re.search(pattern, input_lower)
            if match:
                result['announced_action'] = match.group(1).strip()
                break

        return result

    def generate_readiness_acknowledgment(self, parsed: Dict) -> str:
        """
        Generate the correct response for an instruction setup.
        This is CODE deciding the response, not LLM.
        """
        action = parsed.get('announced_action', '')

        # Clean up the action text
        if action:
            # Remove trailing punctuation and common words
            action = re.sub(r'[.!?,]+$', '', action)
            action = action.strip()

        # Response templates
        if action and len(action) > 3:
            return f"Understood. I'm ready to receive the {action}."
        else:
            return "Understood. I'm ready."

    def handle_instruction_setup(self, user_input: str, context: Dict = None) -> str:
        """
        Handle an instruction setup - router calls this.
        This is THE FIX for "I'm about to upload" → "I don't have context"
        """
        parsed = self.parse_instruction_setup(user_input)
        response = self.generate_readiness_acknowledgment(parsed)

        # Increment rule usage
        rule = self.match_rule(user_input)
        if rule:
            self._increment_usage(rule.id)

        print(f"[COMPREHENSION] Instruction setup: '{user_input[:40]}...' → '{response}'")

        return response

    # =========================================================================
    # CORRECTION HANDLING
    # =========================================================================

    def handle_correction(self, user_input: str, context: Dict = None) -> str:
        """
        Handle user correction - extract teaching and acknowledge learning.
        """
        # Acknowledge the correction
        response = "I understand. I'll work on that."

        # The actual learning happens via the gap detector queueing for update
        # Here we just acknowledge

        rule = self.match_rule(user_input)
        if rule:
            self._increment_usage(rule.id)

        print(f"[COMPREHENSION] Correction detected: '{user_input[:40]}...'")

        return response

    # =========================================================================
    # REFERENCE HANDLING
    # =========================================================================

    def handle_reference(self, user_input: str, context: Dict = None) -> str:
        """
        Handle reference to past conversation - search memory.
        """
        # For now, acknowledge and ask for help
        # Full implementation would search memory_manager
        response = "I recall our earlier discussion. What specifically would you like me to reference?"

        rule = self.match_rule(user_input)
        if rule:
            self._increment_usage(rule.id)

        return response

    # =========================================================================
    # GENERAL RULE APPLICATION
    # =========================================================================

    def apply_rules(self, user_input: str) -> Dict:
        """
        Apply comprehension rules to understand the input.
        Returns enriched understanding.
        """
        result = {
            'text': user_input,
            'parsed_intent': None,
            'special_handling': None,
            'context_needed': False,
            'understanding': None,
        }

        rule = self.match_rule(user_input)
        if rule:
            result['parsed_intent'] = rule.comprehension_type.value
            result['understanding'] = rule.understanding_strategy

            if rule.comprehension_type == ComprehensionType.INSTRUCTION_SETUP:
                result['special_handling'] = 'acknowledge_readiness'
            elif rule.comprehension_type == ComprehensionType.CORRECTION_INTENT:
                result['special_handling'] = 'extract_and_learn'
            elif rule.comprehension_type == ComprehensionType.REFERENCE_TRACKING:
                result['context_needed'] = True
                result['special_handling'] = 'search_memory'
            elif rule.comprehension_type == ComprehensionType.INTENT_BEHIND_WORDS:
                result['special_handling'] = 'understand_meaning'

        return result

    def _increment_usage(self, rule_id: int):
        """Track rule usage."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE comprehension_rules
                SET times_applied = times_applied + 1
                WHERE id = ?
            """, (rule_id,))
            conn.commit()

        for rule in self.rules:
            if rule.id == rule_id:
                rule.times_applied += 1
                break

    # =========================================================================
    # LEARNING
    # =========================================================================

    def record_rule(
        self,
        comprehension_type: ComprehensionType,
        trigger_patterns: List[str],
        understanding_strategy: str,
        example_input: str = "",
        correct_understanding: str = "",
        incorrect_understanding: str = "",
        source: str = "web_research"
    ) -> ComprehensionRule:
        """
        Record a new learned rule.
        Called after successful research.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO comprehension_rules
                (comprehension_type, trigger_patterns, understanding_strategy,
                 example_input, correct_understanding, incorrect_understanding, source)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                comprehension_type.value,
                json.dumps(trigger_patterns),
                understanding_strategy,
                example_input,
                correct_understanding,
                incorrect_understanding,
                source,
            ))
            rule_id = cursor.lastrowid
            conn.commit()

        rule = ComprehensionRule(
            id=rule_id,
            comprehension_type=comprehension_type,
            trigger_patterns=trigger_patterns,
            understanding_strategy=understanding_strategy,
            example_input=example_input,
            correct_understanding=correct_understanding,
            incorrect_understanding=incorrect_understanding,
            source=source,
            learned_at=datetime.now(),
            times_applied=0,
        )

        self.rules.append(rule)
        print(f"[COMPREHENSION] Learned new rule: {comprehension_type.value}")

        return rule

    def get_rules_summary(self) -> str:
        """Get summary of all rules."""
        lines = ["=== COMPREHENSION RULES ==="]

        for rule in self.rules:
            lines.append(f"\n{rule.comprehension_type.value.upper()}:")
            lines.append(f"  Strategy: {rule.understanding_strategy[:60]}...")
            lines.append(f"  Applied: {rule.times_applied}x")

        return '\n'.join(lines)


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    print("=== Testing Comprehension Rules Module ===\n")

    comprehension = ComprehensionRules(db_path="memory.db")

    # Test cases from the problem statement
    test_inputs = [
        "I'm going to upload a document. Just confirming you understand.",
        "before I send this, are you ready?",
        "you just repeated what i said without thinking why i said it",
        "you could say it back. lets work on those manners",
        "remember that document we discussed earlier?",
        "got it?",
    ]

    for user_input in test_inputs:
        print(f"Input: {user_input}")

        rule = comprehension.match_rule(user_input)
        if rule:
            print(f"Type: {rule.comprehension_type.value}")
            print(f"Strategy: {rule.understanding_strategy[:80]}...")

            if rule.comprehension_type == ComprehensionType.INSTRUCTION_SETUP:
                response = comprehension.handle_instruction_setup(user_input)
                print(f"Response: {response}")
        else:
            print("No rule matched")

        print()

    print(comprehension.get_rules_summary())
