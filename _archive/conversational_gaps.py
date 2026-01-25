"""
CONVERSATIONAL GAPS - Foundation Module for Discourse Learning
Part of Demerzel's Autonomous Conversational Competency System

This module provides:
1. GapType enum - Classification of failure types
2. ResearchDirection enum - INWARD (canon) vs OUTWARD (web)
3. ConversationalGapDetector - Post-hoc failure detection
4. SelfDetector - Autonomous failure detection (no human needed)
5. GapQueue - Prioritized queue with deduplication and decay

Architecture: CODE detects gaps, CODE routes research, CODE learns.
LLMs are tools for research execution, not decision-makers.
"""

import re
import json
from datetime import datetime
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class GapType(Enum):
    """Classification of conversational failures."""
    PATTERN_GAP = "pattern_gap"           # "I don't know how to respond" (social norms)
    COMPREHENSION_GAP = "comprehension_gap"  # "I don't understand what they mean" (intent/pragmatics)
    CAPABILITY_GAP = "capability_gap"      # "I understand but genuinely can't do this" (structural)


class ResearchDirection(Enum):
    """Where to look for answers."""
    OUTWARD = "outward"   # Web search for human norms, external knowledge
    INWARD = "inward"     # Read own canon for self-understanding
    NONE = "none"         # No research needed (capability gap, or already known)


# Patterns that indicate questions about Demerzel's identity/purpose
IDENTITY_TRIGGER_PATTERNS = [
    r"who\s+(am\s+i|are\s+you)",
    r"what\s+(am\s+i|are\s+you)",
    r"what\s+is\s+(my|your)\s+(purpose|goal|mission)",
    r"why\s+(was\s+i|were\s+you)\s+(built|created|made)",
    r"what\s+are\s+(my|your)\s+constraints",
    r"(explain|describe)\s+(my|your)\s+(architecture|design)",
    r"(r|root)\s*→?\s*c\s*→?\s*i",
    r"robot\s+laws",
    r"alan\s+(built|created|made)",
    r"bounded\s+system",
    r"ark\s+architecture",
]


class SelfDetector:
    """
    Demerzel detects her own failures by comparing input TYPE to response TYPE.
    If they don't match expected patterns, something went wrong.

    This is the key to autonomy - no human feedback needed for basic failures.
    """

    # Expected response types for each input type
    EXPECTED_RESPONSE_MAP = {
        'greeting': {
            'should_contain': [],  # Greeting words vary
            'should_not_contain': ['acknowledged', 'understood', 'i understand'],
            'response_type': 'reciprocal_greeting',
        },
        'gratitude': {
            'should_contain': ['welcome', 'glad', 'happy', 'of course'],
            'should_not_contain': ['acknowledged', 'understood'],
            'response_type': 'acknowledgment_warm',
        },
        'instruction_setup': {
            'should_contain': ['ready', 'understood', 'go ahead', 'waiting', 'receive'],
            'should_not_contain': ["don't have context", 'no context', 'clarify', "i don't understand"],
            'response_type': 'readiness_confirmation',
        },
        'farewell': {
            'should_contain': ['goodbye', 'bye', 'take care', 'see you'],
            'should_not_contain': ['acknowledged'],
            'response_type': 'reciprocal_farewell',
        },
        'question': {
            'should_contain': [],  # Varies by question
            'should_not_contain': [],  # Can't generalize
            'response_type': 'answer_or_honest_unknown',
        },
    }

    # Patterns to classify input type
    GREETING_PATTERNS = ['hello', 'hi', 'good morning', 'good afternoon', 'good evening', 'hey']
    GRATITUDE_PATTERNS = ['thank', 'thanks', 'appreciate']
    FAREWELL_PATTERNS = ['goodbye', 'bye', 'see you', 'take care']
    INSTRUCTION_SETUP_PATTERNS = [
        r"(i'm|im|i am)\s+(going to|gonna|about to)",
        r"before\s+i\s+(do|start|begin|upload|send)",
        r"(just\s+)?(want|wanna)\s+(to\s+)?make\s+sure",
        r"(got\s+it|understand|ready|comprehend|follow)\s*\?",
        r"confirm(ing)?\s+(you\s+)?(understand|got|ready)",
    ]

    def detect_mismatch(self, user_input: str, response: str) -> Optional[Dict]:
        """
        Self-detect if response mismatches expected type.
        Returns failure info if mismatch detected, None if OK.
        """
        input_type = self._classify_input_type(user_input)

        if input_type not in self.EXPECTED_RESPONSE_MAP:
            return None  # Unknown input type, can't self-detect

        expected = self.EXPECTED_RESPONSE_MAP[input_type]
        response_lower = response.lower()

        # Check for forbidden patterns (high confidence)
        for forbidden in expected['should_not_contain']:
            if forbidden in response_lower:
                return {
                    'detected_by': 'self_detection',
                    'input_type': input_type,
                    'failure_reason': f"Response contains forbidden pattern: '{forbidden}'",
                    'expected_type': expected['response_type'],
                    'confidence': 0.9,
                }

        # Check if expected patterns are missing (lower confidence)
        if expected['should_contain']:
            has_expected = any(exp in response_lower for exp in expected['should_contain'])
            if not has_expected:
                return {
                    'detected_by': 'self_detection',
                    'input_type': input_type,
                    'failure_reason': f"Response missing expected patterns for {input_type}",
                    'expected_type': expected['response_type'],
                    'confidence': 0.6,
                }

        return None  # No mismatch detected

    def _classify_input_type(self, user_input: str) -> str:
        """Classify what type of input this is."""
        input_lower = user_input.lower()

        # Greeting
        if any(g in input_lower for g in self.GREETING_PATTERNS):
            return 'greeting'

        # Gratitude
        if any(t in input_lower for t in self.GRATITUDE_PATTERNS):
            return 'gratitude'

        # Farewell
        if any(f in input_lower for f in self.FAREWELL_PATTERNS):
            return 'farewell'

        # Instruction setup
        if any(re.search(p, input_lower) for p in self.INSTRUCTION_SETUP_PATTERNS):
            return 'instruction_setup'

        # Question
        if '?' in user_input:
            return 'question'

        return 'unknown'


class ConversationalGapDetector:
    """
    Detects and classifies gaps in conversational competency.
    This is the POST-HOC detector - runs after response to detect failures.
    """

    def __init__(self):
        self.self_detector = SelfDetector()

    def classify_gap(
        self,
        user_input: str,
        response: str,
        context: Dict = None
    ) -> Optional[Tuple[GapType, str, str]]:
        """
        Analyze an interaction and classify any gap detected.

        Returns: (gap_type, specific_category, research_direction) or None
        """
        input_lower = user_input.lower()
        response_lower = response.lower()

        # First try self-detection (autonomous)
        mismatch = self.self_detector.detect_mismatch(user_input, response)
        if mismatch:
            input_type = mismatch['input_type']
            # Map input type to gap type
            if input_type in ['greeting', 'gratitude', 'farewell']:
                return (GapType.PATTERN_GAP, input_type, 'outward')
            elif input_type == 'instruction_setup':
                return (GapType.COMPREHENSION_GAP, 'instruction_setup', 'outward')

        # Additional pattern-based detection

        # PATTERN GAP: Greeting → Acknowledged
        greeting_words = ['hello', 'hi', 'good morning', 'good afternoon', 'good evening', 'hey']
        if any(g in input_lower for g in greeting_words):
            if 'acknowledged' in response_lower or response_lower.strip() == 'acknowledged.':
                return (GapType.PATTERN_GAP, 'greeting', 'outward')

        # PATTERN GAP: Thanks → Acknowledged
        thanks_words = ['thank', 'thanks', 'appreciate']
        if any(t in input_lower for t in thanks_words):
            if 'acknowledged' in response_lower:
                return (GapType.PATTERN_GAP, 'gratitude', 'outward')

        # COMPREHENSION GAP: "I'm about to..." → "I don't have context"
        setup_patterns = [r"i'm (going to|about to|gonna)", r"before i"]
        if any(re.search(p, input_lower) for p in setup_patterns):
            if "don't have context" in response_lower or "no context" in response_lower:
                return (GapType.COMPREHENSION_GAP, 'instruction_setup', 'outward')

        # COMPREHENSION GAP: Parrot behavior
        if self._is_parrot_response(user_input, response):
            return (GapType.COMPREHENSION_GAP, 'intent_behind_words', 'outward')

        # COMPREHENSION GAP: User correcting us
        correction_words = ['you should say', "don't repeat", "that isn't how", "that's not how"]
        if any(c in input_lower for c in correction_words):
            return (GapType.COMPREHENSION_GAP, 'correction_intent', 'outward')

        # CAPABILITY GAP: True structural limitation (rare)
        if 'cannot' in response_lower and 'robot law' in response_lower:
            return (GapType.CAPABILITY_GAP, 'structural_limit', 'none')

        return None

    def _is_parrot_response(self, user_input: str, response: str) -> bool:
        """Detect if response just echoes user's words without understanding."""
        user_words = set(user_input.lower().split())
        response_words = set(response.lower().split())

        # Remove common stopwords
        stopwords = {'i', 'you', 'the', 'a', 'an', 'is', 'are', 'was', 'that', 'this', 'to', 'it', 'of', 'and'}
        user_content = user_words - stopwords
        response_content = response_words - stopwords

        if not user_content:
            return False

        # If >60% of user's content words appear in response, likely parrot
        overlap = user_content & response_content
        overlap_ratio = len(overlap) / len(user_content)

        return overlap_ratio > 0.6

    def classify_research_direction(
        self,
        gap_type: GapType,
        user_input: str
    ) -> Tuple[ResearchDirection, str]:
        """
        Determine whether to research INWARD (canon) or OUTWARD (web).
        Returns (direction, specific_category).
        """
        input_lower = user_input.lower()

        # IDENTITY questions → ALWAYS INWARD
        if any(re.search(p, input_lower) for p in IDENTITY_TRIGGER_PATTERNS):
            # Determine which canon category
            if any(w in input_lower for w in ['who', 'what am', 'identity']):
                return (ResearchDirection.INWARD, 'identity')
            elif any(w in input_lower for w in ['architecture', 'r→c→i', 'design', 'structure']):
                return (ResearchDirection.INWARD, 'architecture')
            elif any(w in input_lower for w in ['constraint', 'law', 'rule', 'boundary']):
                return (ResearchDirection.INWARD, 'constraints')
            elif any(w in input_lower for w in ['why', 'purpose', 'theory', 'bounded']):
                return (ResearchDirection.INWARD, 'theory')
            else:
                return (ResearchDirection.INWARD, 'identity')

        # PATTERN gaps → OUTWARD (human norms)
        if gap_type == GapType.PATTERN_GAP:
            return (ResearchDirection.OUTWARD, 'discourse_norms')

        # COMPREHENSION gaps → depends on subject
        if gap_type == GapType.COMPREHENSION_GAP:
            if any(w in input_lower for w in ['myself', 'my own', 'i should', 'i am']):
                return (ResearchDirection.INWARD, 'operations')
            return (ResearchDirection.OUTWARD, 'pragmatics')

        # CAPABILITY gaps → no research
        if gap_type == GapType.CAPABILITY_GAP:
            return (ResearchDirection.NONE, 'structural_limit')

        return (ResearchDirection.OUTWARD, 'general')


class GapQueue:
    """
    Prioritized queue for pending gaps.
    Prevents backlog drowning through decay and deduplication.
    """

    MAX_PENDING_GAPS = 20        # Hard limit - oldest drop off
    DECAY_THRESHOLD_HOURS = 24   # Gaps older than this get lower priority
    BATCH_SIZE = 3               # Research this many per autonomous cycle

    def __init__(self, storage_path: str = "state/pending_gaps.json"):
        self.storage_path = Path(storage_path)
        self.gaps: List[Dict] = []
        self._load()

    def add_gap(self, gap: Dict):
        """Add a gap, deduplicating and enforcing limits."""
        # DEDUPLICATE: Same type + category = same gap
        key = f"{gap.get('type', 'unknown')}:{gap.get('category', 'unknown')}"

        for existing in self.gaps:
            existing_key = f"{existing.get('type', 'unknown')}:{existing.get('category', 'unknown')}"
            if existing_key == key:
                # Already have this gap type, just increment count
                existing['occurrence_count'] = existing.get('occurrence_count', 1) + 1
                existing['last_seen'] = datetime.now().isoformat()
                self._save()
                return

        # NEW GAP
        gap['occurrence_count'] = 1
        gap['added_at'] = datetime.now().isoformat()
        gap['last_seen'] = datetime.now().isoformat()
        gap['researched'] = False
        self.gaps.append(gap)

        # ENFORCE LIMIT: Drop oldest if over max
        if len(self.gaps) > self.MAX_PENDING_GAPS:
            self._drop_oldest()

        self._save()

    def has_pending(self) -> bool:
        """Check if there are pending gaps to research."""
        return any(not g.get('researched', False) for g in self.gaps)

    def get_next_batch(self) -> List[Dict]:
        """Get next batch of gaps to research, prioritized."""
        pending = [g for g in self.gaps if not g.get('researched', False)]

        if not pending:
            return []

        # Priority scoring
        def priority_score(gap):
            occurrence = gap.get('occurrence_count', 1)
            age_hours = self._age_in_hours(gap.get('added_at', datetime.now().isoformat()))
            type_weight = 2 if gap.get('type') == 'comprehension_gap' else 1

            # Score: occurrences * type_weight, decayed by age
            decay = max(0.1, 1.0 - (age_hours / 48))
            return occurrence * type_weight * decay

        # Sort by priority
        sorted_gaps = sorted(pending, key=priority_score, reverse=True)

        # Return top batch
        return sorted_gaps[:self.BATCH_SIZE]

    def mark_researched(self, gap: Dict):
        """Mark gap as researched (successful learning)."""
        for g in self.gaps:
            if (g.get('type') == gap.get('type') and
                g.get('category') == gap.get('category')):
                g['researched'] = True
                g['researched_at'] = datetime.now().isoformat()
                break
        self._save()

    def remove_gap(self, gap: Dict):
        """Remove a gap completely."""
        self.gaps = [
            g for g in self.gaps
            if not (g.get('type') == gap.get('type') and
                   g.get('category') == gap.get('category'))
        ]
        self._save()

    def get_stats(self) -> Dict:
        """Get queue statistics."""
        pending = [g for g in self.gaps if not g.get('researched', False)]
        researched = [g for g in self.gaps if g.get('researched', False)]

        return {
            'total': len(self.gaps),
            'pending': len(pending),
            'researched': len(researched),
            'total_occurrences': sum(g.get('occurrence_count', 1) for g in pending),
        }

    def _drop_oldest(self):
        """Drop oldest, lowest-occurrence gaps when over limit."""
        # Sort by (occurrence_count ASC, added_at ASC) - drop lowest/oldest
        self.gaps.sort(key=lambda g: (g.get('occurrence_count', 1), g.get('added_at', '')))
        self.gaps = self.gaps[1:]  # Drop first (lowest priority)

    def _age_in_hours(self, timestamp: str) -> float:
        try:
            added = datetime.fromisoformat(timestamp)
            return (datetime.now() - added).total_seconds() / 3600
        except:
            return 0

    def _load(self):
        """Load gaps from storage."""
        try:
            if self.storage_path.exists():
                self.gaps = json.loads(self.storage_path.read_text())
        except Exception as e:
            print(f"[GAP_QUEUE] Load error: {e}")
            self.gaps = []

    def _save(self):
        """Save gaps to storage."""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            self.storage_path.write_text(json.dumps(self.gaps, indent=2))
        except Exception as e:
            print(f"[GAP_QUEUE] Save error: {e}")


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def detect_and_queue_gap(
    user_input: str,
    response: str,
    detector: ConversationalGapDetector = None,
    queue: GapQueue = None
) -> Optional[Dict]:
    """
    Convenience function: detect gap and queue for learning.
    Returns gap info if detected, None otherwise.
    """
    if detector is None:
        detector = ConversationalGapDetector()
    if queue is None:
        queue = GapQueue()

    gap_result = detector.classify_gap(user_input, response)

    if gap_result:
        gap_type, category, direction = gap_result
        gap_info = {
            'type': gap_type.value,
            'category': category,
            'direction': direction,
            'user_input': user_input[:200],  # Truncate for storage
            'failed_response': response[:200],
            'timestamp': datetime.now().isoformat(),
        }
        queue.add_gap(gap_info)
        print(f"[GAP] Detected {gap_type.value}:{category} → queued for {direction} research")
        return gap_info

    return None


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    print("=== Testing Conversational Gaps Module ===\n")

    detector = ConversationalGapDetector()
    queue = GapQueue(storage_path="state/test_gaps.json")

    # Test cases from the problem statement
    test_cases = [
        ("good morning Demerzel", "Acknowledged."),
        ("thank you for that improvement!", "Acknowledged."),
        ("I'm going to upload a document. Just confirming you understand.", "I don't have context from earlier in this session."),
        ("you just repeated what i said without thinking why i said it", "I understand that you just repeated what I said without thinking why."),
    ]

    for user_input, response in test_cases:
        print(f"Input: {user_input}")
        print(f"Response: {response}")

        gap = detector.classify_gap(user_input, response)
        if gap:
            gap_type, category, direction = gap
            print(f"GAP DETECTED: {gap_type.value}:{category} → research:{direction}")
        else:
            print("No gap detected")
        print()

    print(f"\nQueue stats: {queue.get_stats()}")
