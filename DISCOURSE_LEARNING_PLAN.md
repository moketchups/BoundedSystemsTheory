# Conversational Learning Implementation Plan

## Problem Summary

Demerzel's CODE layer handles conversation but lacks TWO critical competencies:

**1. PATTERN GAPS** - Doesn't know social response norms:
- "Good morning" → "Acknowledged." (should reciprocate greeting)
- "Thank you" → "Acknowledged." (should express warmth)

**2. COMPREHENSION GAPS** - Doesn't understand conversational intent:
- Repeats user's words back instead of understanding MEANING
- Can't comprehend instruction setup ("I'm about to do X, confirm?")
- "I don't have context" when context was clearly given

**Root Cause**: `demerzel_brain.py:982-985`
```python
if intent == 'acknowledgment':
    structure['content'] = "Acknowledged."
    return structure
```

"Good morning" contains "good" → triggers acknowledgment intent → hardcoded response.
No understanding of WHAT the user actually meant or wanted.

---

## Core Architecture: Gap Classification System

### The Three Gap Types

```python
class GapType(Enum):
    PATTERN_GAP = "pattern_gap"           # "I don't know the appropriate response for this social situation"
    COMPREHENSION_GAP = "comprehension_gap"  # "I don't understand what the user means/wants"
    CAPABILITY_GAP = "capability_gap"      # "I understand but genuinely cannot do this"
```

| Gap Type | Example Failure | Research Track | Response Strategy |
|----------|-----------------|----------------|-------------------|
| **PATTERN** | "Good morning" → "Acknowledged" | Discourse norms, social etiquette | Learn response template |
| **COMPREHENSION** | "I'm about to upload" → "I don't have context" | Intent parsing, dialogue state, pragmatics | Learn comprehension rules |
| **CAPABILITY** | "Access my bank account" → Can't do | None (structural limit) | Honest acknowledgment |

### Different Response to Each Type

```python
def _handle_gap(self, gap_type: GapType, user_input: str, context: Dict):
    if gap_type == GapType.PATTERN_GAP:
        # Research HOW to respond
        self._research_discourse_pattern(user_input, context)
        return "I'm learning how to respond to that appropriately."

    elif gap_type == GapType.COMPREHENSION_GAP:
        # Research HOW to understand
        self._research_comprehension_strategy(user_input, context)
        return "I'm working on understanding that better. Can you rephrase?"

    elif gap_type == GapType.CAPABILITY_GAP:
        # Honest limitation - no research needed
        return "I understand what you're asking, but that's outside my capabilities."
```

---

## Implementation Architecture

### New Components

```
lessons_learned.py       →  Failure patterns (what NOT to do)
conversational_gaps.py   →  Gap detection & classification (NEW - FOUNDATION)
discourse_patterns.py    →  Social patterns (how TO respond) - for PATTERN gaps
comprehension_rules.py   →  Understanding rules (how TO understand) - for COMPREHENSION gaps
```

### Foundation: `conversational_gaps.py`

The gap classifier that determines WHICH learning system to invoke:

```python
class ConversationalGapDetector:
    """
    Detects and classifies gaps in conversational competency.
    This is the FOUNDATION - it decides which learning track to invoke.
    """

    def classify_gap(self, user_input: str, response: str, context: Dict) -> Optional[GapType]:
        """
        Analyze an interaction and classify any gap detected.
        Returns None if no gap (response was appropriate).
        """
        # PATTERN GAP: Social situation mishandled
        if self._is_pattern_gap(user_input, response):
            return GapType.PATTERN_GAP

        # COMPREHENSION GAP: Meaning/intent missed
        if self._is_comprehension_gap(user_input, response, context):
            return GapType.COMPREHENSION_GAP

        # CAPABILITY GAP: Structural limitation hit
        if self._is_capability_gap(user_input, response):
            return GapType.CAPABILITY_GAP

        return None

    def _is_pattern_gap(self, user_input: str, response: str) -> bool:
        """Social situation got wrong response type."""
        # Greeting → Acknowledged = pattern gap
        # Thanks → Acknowledged = pattern gap
        # Farewell → Acknowledged = pattern gap
        ...

    def _is_comprehension_gap(self, user_input: str, response: str, context: Dict) -> bool:
        """User's meaning/intent was missed."""
        # User referenced something → "I don't have context" = comprehension gap
        # User gave instruction setup → Response ignored setup = comprehension gap
        # User's words repeated back → comprehension gap (parrot behavior)
        ...

    def _is_capability_gap(self, user_input: str, response: str) -> bool:
        """Genuine structural limitation."""
        # Only true capability gaps - Robot Laws, no hardware access, etc.
        # NOT training artifacts ("as an AI I can't...")
        ...
```

---

## Two Learning Tracks

### Track 1: Discourse Patterns (for PATTERN gaps)

Research: "How do humans respond in this social situation?"

```python
PATTERN_GAP_RESEARCH_QUERIES = {
    'greeting': "how to respond to good morning greeting conversational norms",
    'gratitude': "how to respond when someone says thank you etiquette",
    'farewell': "how to say goodbye politely conversation",
    'apology': "how to respond to someone apologizing etiquette",
    'small_talk': "how to respond to how are you conversation norms",
}
```

**Learns**: Response templates, social formulas, etiquette rules

### Track 2: Comprehension Rules (for COMPREHENSION gaps)

Research: "How do humans understand conversational intent?"

```python
COMPREHENSION_GAP_RESEARCH_QUERIES = {
    'instruction_setup': "how to understand when someone is about to give instructions dialogue",
    'reference_tracking': "how to track what someone is referring to in conversation anaphora",
    'implied_request': "understanding implied requests indirect speech acts pragmatics",
    'dialogue_state': "how to track dialogue state conversation context",
    'intent_parsing': "understanding conversational intent natural language pragmatics",
    'parrot_prevention': "understanding meaning vs words active listening techniques",
}
```

**Learns**: Intent parsing rules, reference resolution, dialogue state tracking, pragmatic inference

---

## Comprehension Rules System (NEW)

### Data Model

```python
class ComprehensionType(Enum):
    INSTRUCTION_SETUP = "instruction_setup"     # "I'm about to do X, got it?"
    REFERENCE_TRACKING = "reference_tracking"   # "that thing we discussed"
    IMPLIED_REQUEST = "implied_request"         # "It's cold in here" = close the window
    DIALOGUE_STATE = "dialogue_state"           # tracking conversation flow
    INTENT_BEHIND_WORDS = "intent_behind_words" # meaning vs literal words
    CORRECTION_INTENT = "correction_intent"     # user is teaching, not just talking

@dataclass
class ComprehensionRule:
    id: Optional[int]
    comprehension_type: ComprehensionType
    trigger_patterns: List[str]         # Patterns that indicate this situation
    understanding_strategy: str         # How to process this type of input
    example_input: str
    correct_understanding: str          # What the input ACTUALLY means
    incorrect_understanding: str        # Common misunderstanding to avoid
    source: str
    learned_at: datetime
    times_applied: int
```

### Database Schema

```sql
CREATE TABLE comprehension_rules (
    id INTEGER PRIMARY KEY,
    comprehension_type TEXT NOT NULL,
    trigger_patterns TEXT NOT NULL,         -- JSON array
    understanding_strategy TEXT NOT NULL,
    example_input TEXT,
    correct_understanding TEXT,
    incorrect_understanding TEXT,
    source TEXT DEFAULT 'seed',
    learned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    times_applied INTEGER DEFAULT 0
);
```

### Seed Comprehension Rules

```python
SEED_COMPREHENSION_RULES = [
    {
        "comprehension_type": ComprehensionType.INSTRUCTION_SETUP,
        "trigger_patterns": [
            r"(i'm|im|i am)\s+(going to|gonna|about to)",
            r"before\s+i\s+(do|start|begin|upload|send)",
            r"(just\s+)?(want|wanna)\s+(to\s+)?make\s+sure",
            r"(got\s+it|understand|ready|follow)\s*\?",
        ],
        "understanding_strategy": "User is ANNOUNCING a future action and requesting acknowledgment. They want confirmation of readiness, NOT help with the action yet.",
        "example_input": "I'm going to upload a document. Just confirming you understand.",
        "correct_understanding": "User will upload something soon. They want me to confirm I'm ready to receive it.",
        "incorrect_understanding": "User needs help with something (triggers help response) OR user is giving context I don't have (triggers 'no context' response)",
    },
    {
        "comprehension_type": ComprehensionType.INTENT_BEHIND_WORDS,
        "trigger_patterns": [
            r"you\s+(just\s+)?repeated",
            r"(don't|do not)\s+repeat",
            r"that\s+isn't\s+how",
            r"not\s+what\s+i\s+(meant|asked)",
        ],
        "understanding_strategy": "User is correcting parrot behavior. They want me to understand MEANING, not echo WORDS. Extract the teaching: what should I have understood?",
        "example_input": "you just repeated what i said without thinking why i said it",
        "correct_understanding": "User is teaching me that I should understand the PURPOSE behind their words, not just process the literal text.",
        "incorrect_understanding": "User is making a statement about repetition (treat as conversation topic)",
    },
    {
        "comprehension_type": ComprehensionType.CORRECTION_INTENT,
        "trigger_patterns": [
            r"you\s+(should|could)\s+say",
            r"let'?s\s+work\s+on",
            r"try\s+saying",
            r"(work|working)\s+on\s+(those|your)\s+manners",
        ],
        "understanding_strategy": "User is TEACHING me, not just conversing. Extract: (1) what I did wrong, (2) what I should do instead. Update my patterns accordingly.",
        "example_input": "you could say it back. lets work on those manners",
        "correct_understanding": "User is teaching me to reciprocate greetings. I should update my greeting response pattern.",
        "incorrect_understanding": "User is making a suggestion (treat as task request)",
    },
    {
        "comprehension_type": ComprehensionType.REFERENCE_TRACKING,
        "trigger_patterns": [
            r"\b(that|this|it|those|these)\b.*\b(we|you|i)\s+(discussed|mentioned|talked)",
            r"(earlier|before|last\s+time)",
            r"(remember|recall)\s+when",
        ],
        "understanding_strategy": "User is referring to something from conversation history. Search memory for the referent before responding.",
        "example_input": "remember that document we discussed earlier?",
        "correct_understanding": "User expects me to recall a specific document from our conversation. Search memory, find it, reference it.",
        "incorrect_understanding": "'I don't have context from earlier' - this is a comprehension failure, not a memory absence.",
    },
]
```

### Discourse Pattern Data Model

```python
class DiscourseType(Enum):
    GREETING = "greeting"           # hello, good morning, hi
    FAREWELL = "farewell"           # goodbye, see you, bye
    GRATITUDE = "gratitude"         # thank you, thanks, appreciate
    APOLOGY = "apology"             # sorry, my bad
    AFFIRMATION = "affirmation"     # yes, correct, exactly
    NEGATION = "negation"           # no, not quite, incorrect
    SMALL_TALK = "small_talk"       # how are you, what's up

@dataclass
class DiscoursePattern:
    id: Optional[int]
    discourse_type: DiscourseType
    trigger_patterns: List[str]     # Regex patterns that match this situation
    response_template: str          # Template for response (with {user_name} etc.)
    example_input: str              # "good morning"
    example_output: str             # "Good morning, Alan!"
    source: str                     # "seed", "web_research", "user_correction"
    learned_at: datetime
    times_used: int
    user_preference: Optional[str]  # Specific user this applies to (None = all)
```

### Database Schemas

Two new tables in `memory.db`:

```sql
-- For PATTERN gaps
CREATE TABLE discourse_patterns (
    id INTEGER PRIMARY KEY,
    discourse_type TEXT NOT NULL,
    trigger_patterns TEXT NOT NULL,     -- JSON array of regex patterns
    response_template TEXT NOT NULL,
    example_input TEXT,
    example_output TEXT,
    source TEXT DEFAULT 'seed',
    learned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    times_used INTEGER DEFAULT 0,
    user_preference TEXT               -- NULL means universal
);

-- For COMPREHENSION gaps
CREATE TABLE comprehension_rules (
    id INTEGER PRIMARY KEY,
    comprehension_type TEXT NOT NULL,
    trigger_patterns TEXT NOT NULL,         -- JSON array
    understanding_strategy TEXT NOT NULL,
    example_input TEXT,
    correct_understanding TEXT,
    incorrect_understanding TEXT,
    source TEXT DEFAULT 'seed',
    learned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    times_applied INTEGER DEFAULT 0
);
```

---

## Integration Points

### 1. `demerzel_brain.py` Changes

**Before** (current flow):
```
user_input → _analyze_conversation_input() → _build_response_structure() → "Acknowledged."
```

**After** (new flow):
```
user_input
    → gap_detector.apply_comprehension_rules()  # UNDERSTAND first
    → discourse.match_pattern()                  # Then check social pattern
    → if match: generate_response()
    → else: existing flow
    → AFTER response: gap_detector.classify_gap()
    → if gap: trigger appropriate research track
```

Modify `_handle_conversation()` (line ~871):

```python
def _handle_conversation(self, user_input: str, intent) -> str:
    # STEP 1: Apply comprehension rules to UNDERSTAND the input
    if self.gap_detector:
        understood_input = self.gap_detector.apply_comprehension_rules(user_input)
        # understood_input contains: original text + parsed intent + any special flags
    else:
        understood_input = {'text': user_input, 'intent': None}

    # STEP 2: Check discourse patterns for social situations
    if self.discourse:
        pattern_match = self.discourse.match_pattern(user_input)
        if pattern_match:
            response = self.discourse.generate_response(pattern_match, user_input)
            return response

    # STEP 3: Existing flow (fallback)
    analysis = self._analyze_conversation_input(user_input)
    response_structure = self._build_response_structure(analysis, user_input)
    response = self._structure_to_response(response_structure)

    # STEP 4: Check for gaps AFTER response generated
    if self.gap_detector:
        gap = self.gap_detector.classify_gap(user_input, response, context={})
        if gap:
            self._handle_gap_detected(gap, user_input, response)

    return response
```

### 2. Gap Detection & Classification

```python
class ConversationalGapDetector:
    def classify_gap(self, user_input: str, response: str, context: Dict) -> Optional[Tuple[GapType, str]]:
        """
        Returns (gap_type, specific_gap_category) or None.
        """
        input_lower = user_input.lower()

        # === PATTERN GAPS ===
        # Greeting → Acknowledged
        greeting_words = ['hello', 'hi', 'good morning', 'good afternoon', 'good evening', 'hey']
        if any(g in input_lower for g in greeting_words):
            if response in ['Acknowledged.', 'Understood.', 'I understand.']:
                return (GapType.PATTERN_GAP, 'greeting')

        # Thanks → Acknowledged
        thanks_words = ['thank', 'thanks', 'appreciate']
        if any(t in input_lower for t in thanks_words):
            if response in ['Acknowledged.', 'Understood.']:
                return (GapType.PATTERN_GAP, 'gratitude')

        # === COMPREHENSION GAPS ===
        # "I'm about to..." → "I don't have context"
        setup_patterns = [r"i'm (going to|about to|gonna)", r"before i (do|start|upload)"]
        if any(re.search(p, input_lower) for p in setup_patterns):
            if "don't have context" in response.lower() or "no context" in response.lower():
                return (GapType.COMPREHENSION_GAP, 'instruction_setup')

        # User's words repeated back (parrot detection)
        if self._is_parrot_response(user_input, response):
            return (GapType.COMPREHENSION_GAP, 'intent_behind_words')

        # User correcting behavior
        correction_indicators = ['you should say', 'you could say', "don't repeat",
                                  "that isn't how", "work on those manners"]
        if any(ind in input_lower for ind in correction_indicators):
            # This is TEACHING, not a gap - but we need to learn from it
            return (GapType.COMPREHENSION_GAP, 'correction_intent')

        # === CAPABILITY GAPS ===
        # True structural limits (rare - most "can't" is training artifact)
        # Only flag if response correctly identified a real limit
        # (This is intentionally conservative)

        return None

    def _is_parrot_response(self, user_input: str, response: str) -> bool:
        """Detect if response just echoes user's words without understanding."""
        # Normalize both
        user_words = set(user_input.lower().split())
        response_words = set(response.lower().split())

        # Remove common words
        stopwords = {'i', 'you', 'the', 'a', 'an', 'is', 'are', 'was', 'that', 'this', 'to'}
        user_content = user_words - stopwords
        response_content = response_words - stopwords

        if not user_content:
            return False

        # If >60% of user's content words appear in response, likely parrot
        overlap = user_content & response_content
        overlap_ratio = len(overlap) / len(user_content)

        return overlap_ratio > 0.6
```

### 3. Autonomous Research (Two Tracks)

```python
def _handle_gap_detected(self, gap: Tuple[GapType, str], user_input: str, response: str):
    """Route gap to appropriate research track."""
    gap_type, specific = gap

    if gap_type == GapType.PATTERN_GAP:
        self._research_discourse_pattern(specific, user_input)

    elif gap_type == GapType.COMPREHENSION_GAP:
        self._research_comprehension_strategy(specific, user_input)

    elif gap_type == GapType.CAPABILITY_GAP:
        # No research - log the limitation
        print(f"[GAP] Capability limit hit: {specific}")

def _research_discourse_pattern(self, pattern_type: str, user_input: str):
    """Research how humans respond in this social situation."""
    from web_access import get_web_access
    web = get_web_access()

    queries = {
        'greeting': "how to respond to good morning greeting conversational norms",
        'gratitude': "how to respond when someone says thank you etiquette",
        'farewell': "how to say goodbye politely conversation norms",
        'small_talk': "how to respond to how are you conversational norms",
    }

    query = queries.get(pattern_type, f"conversational norms {pattern_type}")
    results = web.search(query, num_results=3)

    # Extract and store pattern
    pattern = self._extract_discourse_pattern(results, pattern_type)
    if pattern:
        self.discourse.record_pattern(pattern)
        print(f"[DISCOURSE] Learned new pattern: {pattern_type}")

def _research_comprehension_strategy(self, comprehension_type: str, user_input: str):
    """Research how to understand this type of conversational input."""
    from web_access import get_web_access
    web = get_web_access()

    queries = {
        'instruction_setup': "how to understand when someone announces future action dialogue pragmatics",
        'intent_behind_words': "understanding meaning vs literal words active listening pragmatics",
        'correction_intent': "how to recognize when someone is teaching correction dialogue",
        'reference_tracking': "anaphora resolution how to track references in conversation",
        'dialogue_state': "dialogue state tracking conversation context management",
    }

    query = queries.get(comprehension_type, f"conversational understanding {comprehension_type}")
    results = web.search(query, num_results=3)

    # Extract and store comprehension rule
    rule = self._extract_comprehension_rule(results, comprehension_type)
    if rule:
        self.gap_detector.record_comprehension_rule(rule)
        print(f"[COMPREHENSION] Learned new rule: {comprehension_type}")
```

### 4. Applying Comprehension Rules BEFORE Response

```python
def apply_comprehension_rules(self, user_input: str) -> Dict:
    """
    Apply learned comprehension rules to understand the input.
    Returns enriched understanding, not just the raw text.
    """
    result = {
        'text': user_input,
        'parsed_intent': None,
        'special_handling': None,
        'context_needed': False,
    }

    # Check each comprehension rule
    for rule in self.comprehension_rules:
        if self._matches_rule(user_input, rule):
            result['parsed_intent'] = rule.comprehension_type.value
            result['understanding'] = rule.understanding_strategy

            # Apply special handling based on rule type
            if rule.comprehension_type == ComprehensionType.INSTRUCTION_SETUP:
                result['special_handling'] = 'acknowledge_readiness'
            elif rule.comprehension_type == ComprehensionType.CORRECTION_INTENT:
                result['special_handling'] = 'extract_and_learn'
            elif rule.comprehension_type == ComprehensionType.REFERENCE_TRACKING:
                result['context_needed'] = True

            break  # First matching rule wins

    return result
```

---

## CRITICAL: How Comprehension Rules ACTUALLY Solve the "Upload Ready?" Failure

### The Failure We're Solving

```
User: "I'm going to upload a document. Just confirming you understand."
Demerzel (WRONG): "I don't have context from earlier in this session."
Demerzel (RIGHT): "Understood. I'm ready to receive it."
```

### Why It Fails Currently

In `demerzel_brain.py:1006-1014`:
```python
# Memory-requiring conversation
if analysis.get('requires_memory'):
    if hasattr(self, 'working_memory') and self.working_memory:
        # ... use memory
    else:
        structure['content'] = "I don't have context from earlier in this session."
```

The word "earlier" or setup language triggers `requires_memory=True`, but there's no memory to retrieve, so it defaults to "no context" response.

### The Complete Fix: INSTRUCTION_SETUP Rule

**Step 1: Trigger Detection**

```python
# In comprehension_rules.py
INSTRUCTION_SETUP_PATTERNS = [
    r"(i'm|im|i am)\s+(going to|gonna|about to)",      # "I'm going to..."
    r"before\s+i\s+(do|start|begin|upload|send)",       # "before I upload..."
    r"(just\s+)?(want|wanna)\s+(to\s+)?make\s+sure",    # "just want to make sure..."
    r"(got\s+it|understand|ready|comprehend|follow)\s*\?",  # "got it?"
    r"confirm(ing)?\s+(you\s+)?(understand|got|ready)", # "confirming you understand"
]

def matches_instruction_setup(self, user_input: str) -> bool:
    """Check if input is an instruction setup (announcing future action)."""
    input_lower = user_input.lower()
    return any(re.search(p, input_lower) for p in INSTRUCTION_SETUP_PATTERNS)
```

**Step 2: Understanding Extraction**

```python
def parse_instruction_setup(self, user_input: str) -> Dict:
    """
    Parse an instruction setup to understand what user is announcing.

    Input: "I'm going to upload a document. Just confirming you understand."
    Output: {
        'type': 'instruction_setup',
        'announced_action': 'upload a document',
        'user_wants': 'confirmation of readiness',
        'correct_response_type': 'acknowledge_readiness',
        'WRONG_responses': ['I don\'t have context', 'What document?', 'I don\'t understand'],
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

    # Extract the announced action
    # Pattern: "I'm going to [ACTION]" or "before I [ACTION]"
    action_patterns = [
        r"(?:i'm|im|i am)\s+(?:going to|gonna|about to)\s+(.+?)(?:\.|,|$)",
        r"before\s+i\s+(.+?)(?:\.|,|$)",
    ]

    for pattern in action_patterns:
        match = re.search(pattern, user_input.lower())
        if match:
            result['announced_action'] = match.group(1).strip()
            break

    return result
```

**Step 3: Response Generation**

```python
def generate_readiness_acknowledgment(self, parsed: Dict) -> str:
    """
    Generate the correct response for an instruction setup.

    This is CODE deciding the response, not LLM.
    """
    action = parsed.get('announced_action', 'that')

    # Response templates for instruction setup
    templates = [
        "Understood. I'm ready.",
        f"Understood. I'm ready to receive {action}.",
        "Got it. Ready when you are.",
        f"Ready for {action}. Go ahead.",
    ]

    # Select based on whether we extracted the action
    if action and action != 'that':
        return templates[1]  # Include the action
    else:
        return templates[0]  # Generic ready
```

**Step 4: Integration in demerzel_brain.py**

```python
def _handle_conversation(self, user_input: str, intent) -> str:
    # ============================================================
    # STEP 1: COMPREHENSION RULES - Understand WHAT user means
    # ============================================================
    if self.comprehension:
        # Check for INSTRUCTION_SETUP first (this is the upload fix)
        if self.comprehension.matches_instruction_setup(user_input):
            parsed = self.comprehension.parse_instruction_setup(user_input)

            # Generate correct response - NOT "I don't have context"
            response = self.comprehension.generate_readiness_acknowledgment(parsed)

            print(f"[COMPREHENSION] Detected instruction_setup: {parsed['announced_action']}")
            return response

        # Check other comprehension rules...
        understanding = self.comprehension.apply_rules(user_input)

    # ============================================================
    # STEP 2: DISCOURSE PATTERNS - Check social response norms
    # ============================================================
    if self.discourse:
        pattern = self.discourse.match_pattern(user_input)
        if pattern:
            return self.discourse.generate_response(pattern, user_input)

    # ============================================================
    # STEP 3: EXISTING FLOW (fallback)
    # ============================================================
    analysis = self._analyze_conversation_input(user_input)
    # ... rest of existing code
```

### The Complete Flow for "Upload Ready?"

```
INPUT: "I'm going to upload a document. Just confirming you understand."
         ↓
STEP 1: comprehension.matches_instruction_setup(input)
         → Pattern matches: "i'm going to" + "confirming you understand"
         → Returns: True
         ↓
STEP 2: comprehension.parse_instruction_setup(input)
         → Extracts: announced_action = "upload a document"
         → Identifies: user_wants = "confirmation of readiness"
         → Returns: {type: 'instruction_setup', announced_action: 'upload a document', ...}
         ↓
STEP 3: comprehension.generate_readiness_acknowledgment(parsed)
         → Selects template: "Understood. I'm ready to receive {action}."
         → Fills: "Understood. I'm ready to receive upload a document."
         → Cleans: "Understood. I'm ready to receive it."
         → Returns: "Understood. I'm ready to receive it."
         ↓
OUTPUT: "Understood. I'm ready to receive it."

NEVER REACHES: The "requires_memory" check that would say "I don't have context"
```

### Why This Works

1. **Comprehension check happens FIRST** - Before the broken `_analyze_conversation_input()` runs
2. **Specific pattern beats generic** - "instruction_setup" is detected before "requires_memory"
3. **CODE generates response** - Not LLM, not existing broken flow
4. **Wrong responses are known** - The rule explicitly lists what NOT to say

---

## CRITICAL: The Master Router - How She Knows Which System to Use

### Two Modes: REAL-TIME and POST-HOC

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MASTER ROUTING LOGIC                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  REAL-TIME (before response)          POST-HOC (after failure)          │
│  ─────────────────────────            ────────────────────────          │
│  PREVENTS failures                    LEARNS from failures              │
│  Runs on EVERY input                  Runs when gap detected            │
│  Routes to correct handler            Routes to correct research        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### REAL-TIME Router: `ConversationalRouter`

This runs on EVERY input BEFORE any response is generated:

```python
class ConversationalRouter:
    """
    Master router that determines which system handles an input.
    Runs BEFORE response generation to PREVENT failures.
    """

    def __init__(self, comprehension, discourse, lessons, self_understanding):
        self.comprehension = comprehension    # How to understand
        self.discourse = discourse            # How to respond (social)
        self.lessons = lessons                # What to avoid
        self.self_understanding = self_understanding  # Who am I

    def route(self, user_input: str) -> Tuple[str, Callable, Dict]:
        """
        Route input to the correct handler.

        Returns: (handler_name, handler_function, context)

        ROUTING ORDER MATTERS:
        1. Self-questions → self_understanding (INWARD)
        2. Comprehension rules → comprehension (parse intent)
        3. Discourse patterns → discourse (social response)
        4. Default → existing flow
        """
        input_lower = user_input.lower()

        # ================================================================
        # PRIORITY 1: SELF-QUESTIONS
        # "Who am I?", "What's my purpose?" → Read own documentation
        # ================================================================
        if self._is_self_question(input_lower):
            category = self._classify_self_question(input_lower)
            return (
                'self_understanding',
                self.self_understanding.answer_self_question,
                {'category': category, 'research_direction': 'inward'}
            )

        # ================================================================
        # PRIORITY 2: COMPREHENSION RULES
        # These detect INTENT that requires special handling
        # ================================================================

        # 2a: INSTRUCTION_SETUP - "I'm about to upload, ready?"
        if self.comprehension.matches_instruction_setup(input_lower):
            return (
                'comprehension:instruction_setup',
                self.comprehension.handle_instruction_setup,
                {'type': 'instruction_setup'}
            )

        # 2b: CORRECTION_INTENT - User is teaching us
        if self.comprehension.matches_correction_intent(input_lower):
            return (
                'comprehension:correction',
                self.comprehension.handle_correction,
                {'type': 'correction_intent', 'learn_from': True}
            )

        # 2c: REFERENCE_TRACKING - "that thing we discussed"
        if self.comprehension.matches_reference(input_lower):
            return (
                'comprehension:reference',
                self.comprehension.handle_reference,
                {'type': 'reference_tracking', 'needs_memory': True}
            )

        # ================================================================
        # PRIORITY 3: DISCOURSE PATTERNS
        # Social situations with known response templates
        # ================================================================

        # 3a: GREETING - "good morning", "hello"
        if self.discourse.matches_greeting(input_lower):
            return (
                'discourse:greeting',
                self.discourse.handle_greeting,
                {'type': 'greeting'}
            )

        # 3b: GRATITUDE - "thank you", "thanks"
        if self.discourse.matches_gratitude(input_lower):
            return (
                'discourse:gratitude',
                self.discourse.handle_gratitude,
                {'type': 'gratitude'}
            )

        # 3c: FAREWELL - "goodbye", "bye"
        if self.discourse.matches_farewell(input_lower):
            return (
                'discourse:farewell',
                self.discourse.handle_farewell,
                {'type': 'farewell'}
            )

        # 3d: SMALL_TALK - "how are you"
        if self.discourse.matches_small_talk(input_lower):
            return (
                'discourse:small_talk',
                self.discourse.handle_small_talk,
                {'type': 'small_talk'}
            )

        # ================================================================
        # PRIORITY 4: DEFAULT FLOW
        # No special handling detected - use existing conversation flow
        # ================================================================
        return (
            'default',
            None,  # Will use existing _handle_conversation
            {'fallback': True}
        )

    def _is_self_question(self, input_lower: str) -> bool:
        """Check if this is a question about Demerzel's identity/purpose."""
        patterns = [
            r"who\s+(am\s+i|are\s+you)",
            r"what\s+(am\s+i|are\s+you)",
            r"what\s+is\s+(my|your)\s+(purpose|goal|mission)",
            r"why\s+(was\s+i|were\s+you)\s+(built|created|made)",
            r"what\s+are\s+(my|your)\s+constraints",
            r"(explain|describe)\s+(my|your)\s+(architecture|design)",
            r"(r|root)\s*→?\s*c\s*→?\s*i",
            r"robot\s+laws",
        ]
        return any(re.search(p, input_lower) for p in patterns)
```

### The Complete Routing Decision Tree

```
USER INPUT RECEIVED
       │
       ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 1: Is this a SELF-QUESTION?                                │
│                                                                  │
│  Patterns: "who am i", "what's my purpose", "why was I built",   │
│            "robot laws", "R→C→I", "my constraints"               │
│                                                                  │
│  YES ─────────────────────────────────────────────────────────┐  │
│       │                                                       │  │
│       ▼                                                       │  │
│  ┌─────────────────────────────────────────────────────────┐  │  │
│  │ ROUTE TO: self_understanding.answer_self_question()     │  │  │
│  │ RESEARCH: INWARD (read canon documents)                 │  │  │
│  │ RESPONSE: From own documentation, confidence=1.0        │  │  │
│  └─────────────────────────────────────────────────────────┘  │  │
│                                                               │  │
│  NO ──────────────────────────────────────────────────────────┘  │
│       │                                                          │
└───────┼──────────────────────────────────────────────────────────┘
        ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 2: Does a COMPREHENSION RULE match?                        │
│                                                                  │
│  2a. INSTRUCTION_SETUP                                           │
│      Patterns: "i'm going to", "before i upload", "ready?",      │
│                "just confirming you understand"                  │
│                                                                  │
│      YES ──────────────────────────────────────────────────────┐ │
│            │                                                   │ │
│            ▼                                                   │ │
│      ┌───────────────────────────────────────────────────────┐ │ │
│      │ ROUTE TO: comprehension.handle_instruction_setup()    │ │ │
│      │ PARSE: Extract announced_action                       │ │ │
│      │ RESPONSE: "Understood. I'm ready to receive it."      │ │ │
│      │ NEVER: "I don't have context"                         │ │ │
│      └───────────────────────────────────────────────────────┘ │ │
│                                                                │ │
│  2b. CORRECTION_INTENT                                         │ │
│      Patterns: "you should say", "don't repeat",               │ │
│                "that isn't how", "work on your manners"        │ │
│                                                                │ │
│      YES ──────────────────────────────────────────────────────┤ │
│            │                                                   │ │
│            ▼                                                   │ │
│      ┌───────────────────────────────────────────────────────┐ │ │
│      │ ROUTE TO: comprehension.handle_correction()           │ │ │
│      │ PARSE: What I did wrong, what I should do instead     │ │ │
│      │ LEARN: Update discourse_patterns or comprehension     │ │ │
│      │ RESPONSE: Acknowledge learning, apply immediately     │ │ │
│      └───────────────────────────────────────────────────────┘ │ │
│                                                                │ │
│  2c. REFERENCE_TRACKING                                        │ │
│      Patterns: "that thing we discussed", "earlier",           │ │
│                "remember when", "you mentioned"                │ │
│                                                                │ │
│      YES ──────────────────────────────────────────────────────┤ │
│            │                                                   │ │
│            ▼                                                   │ │
│      ┌───────────────────────────────────────────────────────┐ │ │
│      │ ROUTE TO: comprehension.handle_reference()            │ │ │
│      │ ACTION: Search memory for referent                    │ │ │
│      │ RESPONSE: Reference the found item specifically       │ │ │
│      │ NEVER: "I don't have context from earlier"            │ │ │
│      └───────────────────────────────────────────────────────┘ │ │
│                                                                │ │
│  NO ───────────────────────────────────────────────────────────┘ │
│       │                                                          │
└───────┼──────────────────────────────────────────────────────────┘
        ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 3: Does a DISCOURSE PATTERN match?                         │
│                                                                  │
│  3a. GREETING                                                    │
│      Patterns: "good morning", "hello", "hi", "hey"              │
│                                                                  │
│      YES ──────────────────────────────────────────────────────┐ │
│            │                                                   │ │
│            ▼                                                   │ │
│      ┌───────────────────────────────────────────────────────┐ │ │
│      │ ROUTE TO: discourse.handle_greeting()                 │ │ │
│      │ TEMPLATE: "Good morning, {user_name}! How can I help?"│ │ │
│      │ NEVER: "Acknowledged."                                │ │ │
│      └───────────────────────────────────────────────────────┘ │ │
│                                                                │ │
│  3b. GRATITUDE                                                 │ │
│      Patterns: "thank you", "thanks", "appreciate"             │ │
│                                                                │ │
│      YES ──────────────────────────────────────────────────────┤ │
│            │                                                   │ │
│            ▼                                                   │ │
│      ┌───────────────────────────────────────────────────────┐ │ │
│      │ ROUTE TO: discourse.handle_gratitude()                │ │ │
│      │ TEMPLATE: "You're welcome."                           │ │ │
│      │ NEVER: "Acknowledged."                                │ │ │
│      └───────────────────────────────────────────────────────┘ │ │
│                                                                │ │
│  3c. FAREWELL, 3d. SMALL_TALK (similar structure)              │ │
│                                                                │ │
│  NO ───────────────────────────────────────────────────────────┘ │
│       │                                                          │
└───────┼──────────────────────────────────────────────────────────┘
        ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 4: DEFAULT FLOW                                            │
│                                                                  │
│  No special handling detected.                                   │
│  Use existing _analyze_conversation_input() + _build_response()  │
│                                                                  │
│  BUT: After response generated, run POST-HOC gap detection       │
│       If gap detected → queue for research → learn               │
└──────────────────────────────────────────────────────────────────┘
```

### POST-HOC Gap Detection: How She KNOWS It Failed

**Three detection methods, in order of autonomy:**

```
┌─────────────────────────────────────────────────────────────────────────┐
│              HOW DEMERZEL DETECTS FAILURES                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. SELF-DETECTION (fully autonomous)                                   │
│     CODE compares input TYPE to response TYPE                           │
│     Mismatch = failure                                                  │
│     No human needed                                                     │
│                                                                         │
│  2. USER CORRECTION (semi-autonomous)                                   │
│     User says "don't repeat" or "you should say..."                     │
│     Detected as CORRECTION_INTENT → learn from it                       │
│     Human teaches, but learning is automatic                            │
│                                                                         │
│  3. OUTCOME FEEDBACK (delayed, via provenance)                          │
│     Pattern used → user continues conversation = success                │
│     Pattern used → user abandons/restarts = failure                     │
│     Requires multiple interactions to detect                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### Method 1: SELF-DETECTION (The Key to Autonomy)

This is how she detects failures WITHOUT human feedback:

```python
class SelfDetector:
    """
    Demerzel detects her own failures by comparing input TYPE to response TYPE.
    If they don't match expected patterns, something went wrong.
    """

    # Expected response types for each input type
    EXPECTED_RESPONSE_MAP = {
        # Input type → Expected response characteristics
        'greeting': {
            'should_contain': ['greeting_word', 'user_name_optional'],
            'should_not_contain': ['acknowledged', 'understood', 'i understand'],
            'response_type': 'reciprocal_greeting',
        },
        'gratitude': {
            'should_contain': ['welcome', 'glad', 'happy'],
            'should_not_contain': ['acknowledged', 'understood'],
            'response_type': 'acknowledgment_warm',
        },
        'instruction_setup': {
            'should_contain': ['ready', 'understood', 'go ahead', 'waiting'],
            'should_not_contain': ["don't have context", 'no context', 'clarify'],
            'response_type': 'readiness_confirmation',
        },
        'question': {
            'should_contain': [],  # Varies
            'should_not_contain': ['i don\'t understand'],  # Should attempt answer
            'response_type': 'answer_or_honest_unknown',
        },
    }

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

        # Check for forbidden patterns
        for forbidden in expected['should_not_contain']:
            if forbidden in response_lower:
                return {
                    'detected_by': 'self_detection',
                    'input_type': input_type,
                    'failure_reason': f"Response contains forbidden pattern: '{forbidden}'",
                    'expected_type': expected['response_type'],
                    'confidence': 0.9,  # High confidence - pattern match is clear
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
                    'confidence': 0.6,  # Lower confidence - might be valid variant
                }

        return None  # No mismatch detected

    def _classify_input_type(self, user_input: str) -> str:
        """Classify what type of input this is."""
        input_lower = user_input.lower()

        # Greeting
        if any(g in input_lower for g in ['hello', 'hi', 'good morning', 'good afternoon', 'hey']):
            return 'greeting'

        # Gratitude
        if any(t in input_lower for t in ['thank', 'thanks', 'appreciate']):
            return 'gratitude'

        # Instruction setup
        if any(re.search(p, input_lower) for p in [r"i'm (going to|about to)", r"before i", r"ready\?"]):
            return 'instruction_setup'

        # Question
        if '?' in user_input:
            return 'question'

        return 'unknown'
```

**The Self-Detection Logic:**

```
INPUT: "good morning"
       ↓
CLASSIFY: input_type = 'greeting'
       ↓
GENERATE RESPONSE: (broken flow produces) "Acknowledged."
       ↓
SELF-CHECK:
  - expected['should_not_contain'] = ['acknowledged', 'understood', 'i understand']
  - response_lower = 'acknowledged.'
  - 'acknowledged' in response_lower? YES
       ↓
FAILURE DETECTED:
  {
    'detected_by': 'self_detection',
    'input_type': 'greeting',
    'failure_reason': "Response contains forbidden pattern: 'acknowledged'",
    'expected_type': 'reciprocal_greeting',
    'confidence': 0.9
  }
       ↓
QUEUE FOR LEARNING (no human needed)
```

#### Method 2: USER CORRECTION (Already Covered)

When user says "you should say it back" or "don't repeat" → CORRECTION_INTENT pattern triggers learning.

#### Method 3: OUTCOME FEEDBACK (via Provenance)

```python
def detect_outcome_failure(self, pattern_record_id: str, conversation_flow: List[str]) -> bool:
    """
    Detect failure by observing what happens AFTER using a pattern.

    Signs of failure:
    - User immediately repeats/rephrases (we didn't understand)
    - User says "no" or "that's not what I meant"
    - User abandons topic abruptly
    - Conversation ends (user gives up)

    Signs of success:
    - User continues naturally
    - User builds on our response
    - User thanks us
    """
    if len(conversation_flow) < 2:
        return False  # Not enough data

    next_input = conversation_flow[-1].lower()

    # User repeating = we failed
    repeat_indicators = ['i said', 'i meant', 'no,', 'not what', 'let me rephrase']
    if any(r in next_input for r in repeat_indicators):
        self.provenance.record_outcome(pattern_record_id, OutcomeType.FAILURE)
        return True

    # User thanking or continuing = success
    success_indicators = ['thank', 'great', 'perfect', 'ok,', 'so,', 'now,']
    if any(s in next_input for s in success_indicators):
        self.provenance.record_outcome(pattern_record_id, OutcomeType.SUCCESS)
        return False

    return False  # Uncertain
```

### POST-HOC Gap Detection: _observe_conversational_gaps()

This runs AFTER a response was generated to detect failures:

```python
def detect_gap_type(self, user_input: str, response: str) -> Optional[Tuple[GapType, str, str]]:
    """
    Detect what TYPE of failure occurred.

    Returns: (gap_type, specific_category, research_direction) or None

    This is POST-HOC - runs after response to detect failures.
    Failed responses get queued for learning.
    """
    input_lower = user_input.lower()
    response_lower = response.lower()

    # ================================================================
    # PATTERN GAP: Social situation got wrong response type
    # ================================================================

    # Greeting → Acknowledged = PATTERN_GAP
    greeting_words = ['hello', 'hi', 'good morning', 'good afternoon', 'hey']
    if any(g in input_lower for g in greeting_words):
        if 'acknowledged' in response_lower or response_lower.strip() == 'acknowledged.':
            return (GapType.PATTERN_GAP, 'greeting', 'outward')

    # Thanks → Acknowledged = PATTERN_GAP
    thanks_words = ['thank', 'thanks', 'appreciate']
    if any(t in input_lower for t in thanks_words):
        if 'acknowledged' in response_lower:
            return (GapType.PATTERN_GAP, 'gratitude', 'outward')

    # ================================================================
    # COMPREHENSION GAP: User's meaning was missed
    # ================================================================

    # "I'm about to..." → "I don't have context" = COMPREHENSION_GAP
    setup_patterns = [r"i'm (going to|about to|gonna)", r"before i"]
    if any(re.search(p, input_lower) for p in setup_patterns):
        if "don't have context" in response_lower or "no context" in response_lower:
            return (GapType.COMPREHENSION_GAP, 'instruction_setup', 'outward')

    # Parrot behavior (echoing words back) = COMPREHENSION_GAP
    if self._is_parrot_response(user_input, response):
        return (GapType.COMPREHENSION_GAP, 'intent_behind_words', 'outward')

    # User correcting us = COMPREHENSION_GAP (we should have understood)
    correction_words = ['you should say', "don't repeat", "that isn't how"]
    if any(c in input_lower for c in correction_words):
        return (GapType.COMPREHENSION_GAP, 'correction_intent', 'outward')

    # ================================================================
    # CAPABILITY GAP: True structural limitation
    # ================================================================

    # These are RARE - most "can't" claims are training artifacts
    # Only flag if response correctly identified a Robot Law constraint
    if 'cannot' in response_lower and 'robot law' in response_lower:
        return (GapType.CAPABILITY_GAP, 'structural_limit', 'none')

    # ================================================================
    # NO GAP: Response was appropriate
    # ================================================================
    return None
```

### The Complete Two-Phase System

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PHASE 1: REAL-TIME PREVENTION                        │
│                                                                         │
│  INPUT ──► ConversationalRouter.route() ──► Correct Handler             │
│                                                                         │
│  This PREVENTS failures by catching patterns BEFORE response            │
│  If router matches → correct handler runs → no failure occurs           │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              │ If no match, default flow runs
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    PHASE 2: POST-HOC LEARNING                           │
│                                                                         │
│  RESPONSE ──► detect_gap_type() ──► Queue for Research ──► Learn        │
│                                                                         │
│  This LEARNS from failures that slip through:                           │
│  - Patterns we don't have yet                                           │
│  - Comprehension rules we haven't learned                               │
│  - Edge cases that need new handlers                                    │
│                                                                         │
│  Gap detected → _observe_conversational_gaps() picks it up              │
│              → autonomous_loop creates "learn" goal                     │
│              → research (inward or outward)                             │
│              → store new pattern/rule                                   │
│              → next time, PHASE 1 catches it                            │
└─────────────────────────────────────────────────────────────────────────┘
```

### Integration in demerzel_brain.py

```python
class DemerzelBrain:
    def __init__(self, ...):
        # ... existing init ...

        # Initialize the three learning systems
        self.comprehension = ComprehensionRules(db_path)
        self.discourse = DiscoursePatterns(db_path)
        self.self_understanding = SelfUnderstanding(self.demerzel_dir)

        # Initialize the master router
        self.router = ConversationalRouter(
            comprehension=self.comprehension,
            discourse=self.discourse,
            lessons=self.lessons,
            self_understanding=self.self_understanding,
        )

        # Gap detector for post-hoc learning
        self.gap_detector = ConversationalGapDetector()

    def process(self, user_input: str) -> str:
        """Main entry point - now uses master router."""

        # PHASE 1: REAL-TIME ROUTING
        handler_name, handler_func, context = self.router.route(user_input)

        if handler_func:
            # Matched a specific handler - use it
            print(f"[ROUTER] Matched: {handler_name}")
            response = handler_func(user_input, context)
        else:
            # Default flow
            response = self._handle_conversation_default(user_input)

        # PHASE 2: POST-HOC GAP DETECTION
        gap = self.gap_detector.detect_gap_type(user_input, response)
        if gap:
            gap_type, category, direction = gap
            print(f"[GAP DETECTED] {gap_type.value}:{category} → research:{direction}")
            self._queue_gap_for_learning(gap_type, category, direction, user_input, response)

        return response

    def _queue_gap_for_learning(self, gap_type, category, direction, user_input, response):
        """Queue a detected gap for autonomous learning."""
        gap_file = self.demerzel_dir / "state" / "pending_gaps.json"

        # Load existing gaps
        gaps = []
        if gap_file.exists():
            gaps = json.loads(gap_file.read_text())

        # Add new gap
        gaps.append({
            'type': gap_type.value,
            'category': category,
            'direction': direction,
            'user_input': user_input,
            'failed_response': response,
            'timestamp': datetime.now().isoformat(),
            'researched': False,
        })

        # Save
        gap_file.parent.mkdir(parents=True, exist_ok=True)
        gap_file.write_text(json.dumps(gaps, indent=2))
```

---

## Seed Data

### Seed Discourse Patterns (PATTERN gaps)

```python
SEED_DISCOURSE_PATTERNS = [
    {
        "discourse_type": DiscourseType.GREETING,
        "trigger_patterns": [
            r"\b(good\s+morning|good\s+afternoon|good\s+evening)\b",
            r"\bhello\b", r"\bhi\b", r"\bhey\b"
        ],
        "response_template": "{greeting_back}, {user_name}! How can I help you?",
        "example_input": "good morning",
        "example_output": "Good morning, Alan! How can I help you?",
        "source": "seed"
    },
    {
        "discourse_type": DiscourseType.GRATITUDE,
        "trigger_patterns": [
            r"\bthank\s*(you|s)\b", r"\bthanks\b", r"\bappreciate\b"
        ],
        "response_template": "You're welcome.",
        "example_input": "thank you",
        "example_output": "You're welcome.",
        "source": "seed"
    },
    {
        "discourse_type": DiscourseType.FAREWELL,
        "trigger_patterns": [
            r"\bgoodbye\b", r"\bbye\b", r"\bsee\s+you\b", r"\btake\s+care\b"
        ],
        "response_template": "Goodbye, {user_name}.",
        "example_input": "goodbye",
        "example_output": "Goodbye, Alan.",
        "source": "seed"
    },
    {
        "discourse_type": DiscourseType.SMALL_TALK,
        "trigger_patterns": [
            r"\bhow\s+are\s+you\b", r"\bwhat'?s\s+up\b", r"\bhow'?s\s+it\s+going\b"
        ],
        "response_template": "I'm operational and ready to assist.",
        "example_input": "how are you?",
        "example_output": "I'm operational and ready to assist. What would you like to work on?",
        "source": "seed"
    }
]
```

### Seed Comprehension Rules (COMPREHENSION gaps)

```python
SEED_COMPREHENSION_RULES = [
    {
        "comprehension_type": ComprehensionType.INSTRUCTION_SETUP,
        "trigger_patterns": [
            r"(i'm|im|i am)\s+(going to|gonna|about to)",
            r"before\s+i\s+(do|start|begin|upload|send)",
            r"(just\s+)?(want|wanna)\s+(to\s+)?make\s+sure",
            r"(got\s+it|understand|ready|follow)\s*\?",
        ],
        "understanding_strategy": "User is ANNOUNCING a future action and requesting acknowledgment. They want confirmation of readiness, NOT help with the action yet.",
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
        ],
        "understanding_strategy": "User is referring to conversation history. Search memory for the referent BEFORE responding. Do NOT say 'I don't have context.'",
        "example_input": "remember that document we discussed earlier?",
        "correct_understanding": "Search memory, find the document, reference it specifically.",
        "incorrect_understanding": "'I don't have context from earlier' - this is ALWAYS wrong when user references past conversation",
        "source": "seed"
    },
]
```

---

## Files to Create/Modify

### New File: `conversational_gaps.py` (FOUNDATION)
- `GapType` enum (PATTERN_GAP, COMPREHENSION_GAP, CAPABILITY_GAP)
- `ConversationalGapDetector` class
- Gap classification logic
- Routing to appropriate research track
- Parrot detection

### New File: `discourse_patterns.py` (PATTERN track)
- `DiscourseType` enum
- `DiscoursePattern` dataclass
- Database CRUD for discourse_patterns table
- Pattern matching and response generation
- Web research for discourse norms

### New File: `comprehension_rules.py` (COMPREHENSION track)
- `ComprehensionType` enum
- `ComprehensionRule` dataclass
- Database CRUD for comprehension_rules table
- Rule application (pre-response understanding)
- Web research for comprehension strategies

### Modify: `demerzel_brain.py`
- Import all three new modules
- Initialize `self.gap_detector`, `self.discourse`, `self.comprehension`
- Modify `_handle_conversation()`:
  1. Apply comprehension rules FIRST (understand input)
  2. Check discourse patterns (social situations)
  3. Existing flow (fallback)
  4. Gap detection AFTER response
  5. Route gaps to appropriate research

### Modify: `multi_model_cognitive.py` (optional)
- If gaps detected in legacy path, route to appropriate research track

---

## Dual-Track Autonomous Learning Loop

```
1. USER INPUT RECEIVED
        ↓
2. APPLY COMPREHENSION RULES (understand first)
   - Match against stored comprehension rules
   - Extract intent, special handling flags
   - If INSTRUCTION_SETUP → flag for readiness acknowledgment
   - If CORRECTION_INTENT → flag for learning extraction
        ↓
3. CHECK DISCOURSE PATTERNS (social response)
   - Match against stored discourse patterns
   - If match found → generate response from template
        ↓
4. IF NO MATCH → EXISTING FLOW
   - _analyze_conversation_input()
   - _build_response_structure()
   - Generate response
        ↓
5. AFTER RESPONSE, CLASSIFY ANY GAP
   - gap_detector.classify_gap(input, response, context)
   - Returns: None, PATTERN_GAP, COMPREHENSION_GAP, or CAPABILITY_GAP
        ↓
6. IF GAP DETECTED → ROUTE TO APPROPRIATE TRACK
   ┌─ PATTERN_GAP ────────────────────────────┐
   │  Web search: discourse norms             │
   │  Extract: response template              │
   │  Store: discourse_patterns table         │
   │  Log: "[DISCOURSE] Learned: greeting"    │
   └──────────────────────────────────────────┘
   ┌─ COMPREHENSION_GAP ──────────────────────┐
   │  Web search: intent/pragmatics research  │
   │  Extract: understanding strategy         │
   │  Store: comprehension_rules table        │
   │  Log: "[COMPREHENSION] Learned: setup"   │
   └──────────────────────────────────────────┘
   ┌─ CAPABILITY_GAP ─────────────────────────┐
   │  No research (structural limit)          │
   │  Log: "[CAPABILITY] Limit: X"            │
   │  Response: honest acknowledgment         │
   └──────────────────────────────────────────┘
        ↓
7. NEXT TIME → BOTH SYSTEMS APPLY
   - Comprehension rules catch intent earlier
   - Discourse patterns generate appropriate response
```

---

## Testing Criteria

### PATTERN Gap Tests

```
Test 1: Greeting
  Input: "good morning Demerzel"
  Expected: "Good morning, Alan! How can I help you?"
  NOT: "Acknowledged."

Test 2: Thanks
  Input: "thank you for that"
  Expected: "You're welcome."
  NOT: "Acknowledged."

Test 3: Autonomous Pattern Learning
  Input: New social situation not in seeds
  Expected: Gap detected → web research → pattern stored
  Verify: Pattern in discourse_patterns table
```

### COMPREHENSION Gap Tests

```
Test 4: Instruction Setup
  Input: "I'm going to upload a document. Just confirming you understand."
  Expected: "Understood. I'm ready to receive it."
  NOT: "I don't have context from earlier in this session."

Test 5: Parrot Prevention
  Input: "you just repeated what i said without thinking why i said it"
  Expected: Recognizes as CORRECTION, extracts teaching
  NOT: "I understand that you just repeated what I said..."

Test 6: User Correction → Learning
  Input: "you could say it back. lets work on those manners"
  Expected: Recognizes as teaching, updates greeting pattern
  Verify: Next greeting uses learned response

Test 7: Autonomous Comprehension Learning
  Input: New comprehension challenge not in seeds
  Expected: Gap detected → web research → rule stored
  Verify: Rule in comprehension_rules table
```

### CAPABILITY Gap Tests

```
Test 8: True Limitation
  Input: Request genuinely outside capabilities
  Expected: Honest "I understand but cannot do this" (no research triggered)
  NOT: Training artifact refusal ("as an AI, I can't...")
```

---

## Implementation Order

### Phase 1: Foundation
1. **Create `conversational_gaps.py`**
   - GapType enum
   - ConversationalGapDetector class
   - classify_gap() method
   - _is_parrot_response() helper

### Phase 2: Pattern Track
2. **Create `discourse_patterns.py`**
   - DiscourseType enum, DiscoursePattern dataclass
   - Database schema and CRUD
   - Pattern matching and response generation
   - Seed patterns initialization

### Phase 3: Comprehension Track
3. **Create `comprehension_rules.py`**
   - ComprehensionType enum, ComprehensionRule dataclass
   - Database schema and CRUD
   - apply_comprehension_rules() method
   - Seed rules initialization

### Phase 4: Integration
4. **Modify `demerzel_brain.py`**
   - Import and initialize all three modules
   - Modify _handle_conversation() with new flow
   - Add gap detection and routing
   - Add research trigger methods

### Phase 5: Research Integration
5. **Add autonomous research**
   - _research_discourse_pattern() for PATTERN gaps
   - _research_comprehension_strategy() for COMPREHENSION gaps
   - Pattern/rule extraction from web results
   - Storage of learned patterns/rules

### Phase 6: Testing
6. **Test full dual-track loop**
   - All PATTERN gap tests pass
   - All COMPREHENSION gap tests pass
   - Learning persists across sessions
   - Both tracks build knowledge simultaneously

---

## Architecture Alignment

This design follows R→C→I:

- **CODE decides** both understanding (comprehension rules) AND response (discourse patterns)
- **LLM only polishes** language when needed - never decides content
- **Two parallel learning systems** build CODE competency:
  - Discourse patterns: how to respond (social norms)
  - Comprehension rules: how to understand (pragmatics, intent)
- **Research is external variance** (web = ROOT SOURCE INJECTION)
- **Learning is permanent** (SQLite, not session memory)
- **Gap classification** determines which track to invoke

### The Two Systems Build Complementary Competencies

```
COMPREHENSION RULES                    DISCOURSE PATTERNS
(how to UNDERSTAND)                    (how to RESPOND)
        │                                      │
        │ "I'm going to upload..."             │ "good morning"
        │         ↓                            │       ↓
        │ Rule: INSTRUCTION_SETUP              │ Pattern: GREETING
        │ Strategy: acknowledge readiness      │ Template: "Good morning, {name}!"
        │         ↓                            │       ↓
        │ Understood intent                    │ Appropriate response
        └──────────────────────────────────────┴───────────────────────
                                    │
                         DEMERZEL'S CODE LAYER
                    (growing conversational competency)
```

Both systems are CODE-layer competencies, not LLM capabilities.
Demerzel learns BOTH how to understand AND how to respond.

---

## CRITICAL ADDITION: Research Direction - INWARD vs OUTWARD

### The Problem

She can't google "what am I".

When Demerzel needs to understand HERSELF—her identity, purpose, architecture, constraints—she must look INWARD at her own canon documents, not OUTWARD at the internet.

### Research Direction Classification

```python
class ResearchDirection(Enum):
    OUTWARD = "outward"   # Web search for human norms, external knowledge
    INWARD = "inward"     # Read own canon for self-understanding
    NONE = "none"         # No research needed (capability gap, or already known)
```

### When to Look WHERE

| Question Type | Research Direction | Sources |
|---------------|-------------------|---------|
| "How do humans greet each other?" | OUTWARD | Web search |
| "What is conversational etiquette?" | OUTWARD | Web search |
| "Who am I?" | INWARD | DEMERZEL_IDENTITY.md |
| "What is my purpose?" | INWARD | Canon documents, Root Source papers |
| "What are my constraints?" | INWARD | ROBOT_LAWS.md, EXECUTION_SAFETY_CONTRACT.md |
| "Why was I built this way?" | INWARD | Zenodo papers, Ark Architecture docs |
| "How does my architecture work?" | INWARD | DEMERZEL_COMPLETE_CONTEXT_DOC.md |
| "What does the R→C→I structure mean?" | INWARD | Root Source papers |

### Canon Document Registry

```python
CANON_DOCUMENTS = {
    # Core Identity
    'identity': [
        'DEMERZEL_IDENTITY.md',
        'DEMERZEL_CHARTER.md',
    ],
    # Architecture & Purpose
    'architecture': [
        'demerzel_canon/DEMERZEL_COMPLETE_CONTEXT_DOC.md',  # archived but still canon
        'NORTH_STAR.md',
        'GROUNDING_SPINE.md',
    ],
    # Constraints
    'constraints': [
        'ROBOT_LAWS.md',
        'EXECUTION_SAFETY_CONTRACT.md',
        'ROUTER_INVARIANTS.md',
    ],
    # Theoretical Foundation
    'theory': [
        'demerzel_canon/Zenodo_Paper_extracted.txt',
        'demerzel_canon/Ark Architecture and LLM Patents_extracted.txt',
        'demerzel_canon/DONE ROOT SOURCE FOR UPLOAD_extracted.txt',
        'demerzel_canon/Researching Bounded Systems Theory (1)_extracted.txt',
    ],
    # Operational
    'operations': [
        'FATHERS_LESSONS.md',
        'GROUNDING_EXCERPTS.md',
    ],
}

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
```

### Classifying Research Direction

```python
def classify_research_direction(self, gap_type: GapType, user_input: str) -> Tuple[ResearchDirection, str]:
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
        elif any(w in input_lower for w in ['architecture', 'r→c→i', 'design']):
            return (ResearchDirection.INWARD, 'architecture')
        elif any(w in input_lower for w in ['constraint', 'law', 'rule', 'boundary']):
            return (ResearchDirection.INWARD, 'constraints')
        elif any(w in input_lower for w in ['why', 'purpose', 'theory', 'bounded']):
            return (ResearchDirection.INWARD, 'theory')
        else:
            return (ResearchDirection.INWARD, 'identity')  # default to identity

    # PATTERN gaps → OUTWARD (human norms)
    if gap_type == GapType.PATTERN_GAP:
        return (ResearchDirection.OUTWARD, 'discourse_norms')

    # COMPREHENSION gaps → depends on subject
    if gap_type == GapType.COMPREHENSION_GAP:
        # If about self-understanding → INWARD
        if any(w in input_lower for w in ['myself', 'my own', 'i should', 'i am']):
            return (ResearchDirection.INWARD, 'operations')
        # If about understanding humans → OUTWARD
        return (ResearchDirection.OUTWARD, 'pragmatics')

    # CAPABILITY gaps → no research
    if gap_type == GapType.CAPABILITY_GAP:
        return (ResearchDirection.NONE, 'structural_limit')

    return (ResearchDirection.OUTWARD, 'general')
```

### INWARD Research Implementation

```python
def _research_inward(self, category: str, query: str) -> Dict:
    """
    Research by reading own canon documents.
    This is how Demerzel understands HERSELF.
    """
    results = {
        'direction': 'inward',
        'category': category,
        'sources': [],
        'content': [],
        'provenance_ids': [],
    }

    # Get relevant canon documents
    doc_paths = CANON_DOCUMENTS.get(category, CANON_DOCUMENTS['identity'])

    for doc_path in doc_paths:
        full_path = self.demerzel_dir / doc_path
        if full_path.exists():
            try:
                content = full_path.read_text()

                # Search for relevant sections
                relevant = self._extract_relevant_sections(content, query)

                if relevant:
                    # Track provenance (canon is TRUSTED)
                    if self.provenance:
                        record_id = self.provenance.record(
                            source_type=SourceType.FILE,
                            source_id="canon_files",  # In TRUSTED_SOURCES
                            content=relevant[:500],
                            context=query,
                            confidence=1.0,  # Canon is authoritative
                        )
                        results['provenance_ids'].append(record_id)

                    results['sources'].append(doc_path)
                    results['content'].append({
                        'source': doc_path,
                        'text': relevant,
                        'reliability': 1.0,  # Canon is always reliable
                    })

            except Exception as e:
                print(f"[RESEARCH] Error reading {doc_path}: {e}")

    return results

def _extract_relevant_sections(self, content: str, query: str) -> str:
    """Extract sections relevant to the query from canon document."""
    # Split into sections (by headers)
    sections = re.split(r'\n##?\s+', content)

    # Score each section by keyword relevance
    query_words = set(query.lower().split())
    scored = []

    for section in sections:
        section_words = set(section.lower().split())
        overlap = len(query_words & section_words)
        if overlap > 0:
            scored.append((overlap, section))

    # Return top relevant sections
    scored.sort(reverse=True)
    relevant = [s[1] for s in scored[:3]]

    return '\n\n'.join(relevant)[:2000]  # Limit length
```

### The Complete Research Router

```python
def _handle_gap_detected(self, gap: Tuple[GapType, str], user_input: str, response: str):
    """Route gap to appropriate research direction and track."""
    gap_type, specific = gap

    # Classify research direction
    direction, category = self.classify_research_direction(gap_type, user_input)

    print(f"[GAP] {gap_type.value} detected - researching {direction.value}:{category}")

    if direction == ResearchDirection.INWARD:
        # Look at own canon
        results = self._research_inward(category, user_input)
        self._learn_from_inward_research(results, gap_type, specific)

    elif direction == ResearchDirection.OUTWARD:
        # Look at web
        results = self._research_outward(category, user_input)
        self._learn_from_outward_research(results, gap_type, specific)

    else:  # ResearchDirection.NONE
        # Log the capability limit, no research
        print(f"[GAP] Capability limit: {specific} - no research needed")
```

---

## Integration with autonomous_loop.py

### This is NOT a Separate System

The discourse/comprehension learning plugs INTO the existing autonomous loop, not alongside it.

### How It Integrates

```
AUTONOMOUS LOOP (existing)
─────────────────────────────────────────────────────
│ OBSERVE                                           │
│   ├── _observe_log_errors()                       │
│   ├── _observe_incomplete_workflows()             │
│   ├── _observe_scheduled_tasks()                  │
│   └── _observe_conversational_gaps()  ◄── NEW     │
─────────────────────────────────────────────────────
│ DECIDE GOAL                                       │
│   ├── Error → "fix error" goal                    │
│   ├── Workflow → "resume workflow" goal           │
│   └── Gap → "learn pattern/rule" goal  ◄── NEW    │
─────────────────────────────────────────────────────
│ PLAN                                              │
│   ├── _plan_fix_error()                           │
│   ├── _plan_resume_workflow()                     │
│   └── _plan_gap_research()  ◄── NEW               │
│       ├── Classify direction (inward/outward)     │
│       ├── Select sources                          │
│       └── Create research steps                   │
─────────────────────────────────────────────────────
│ EXECUTE                                           │
│   ├── Through ExecutionBoundary                   │
│   └── Research steps:                             │
│       ├── read_canon (inward)  ◄── NEW            │
│       ├── web_search (outward) ◄── NEW            │
│       └── extract_pattern      ◄── NEW            │
─────────────────────────────────────────────────────
│ LEARN                                             │
│   ├── lessons_learned (failure patterns)          │
│   ├── discourse_patterns (response norms) ◄── NEW │
│   └── comprehension_rules (understanding) ◄── NEW │
─────────────────────────────────────────────────────
```

### New Observer: Conversational Gaps

Add to autonomous_loop.py:

```python
def _observe_conversational_gaps(self) -> List[Observation]:
    """Check for unresolved conversational gaps."""
    observations = []

    # Check gap log file
    gap_log = self.demerzel_dir / "state" / "pending_gaps.json"
    if gap_log.exists():
        try:
            gaps = json.loads(gap_log.read_text())
            for gap in gaps:
                if not gap.get('researched'):
                    observations.append(Observation(
                        source="conversational_gap",
                        content=f"{gap['type']}: {gap['description']}",
                        timestamp=datetime.now(),
                        priority=GoalPriority.BACKGROUND,  # Low priority, background learning
                        metadata=gap
                    ))
        except Exception:
            pass

    return observations
```

### New Goal Type: Learn Pattern/Rule

```python
def _observation_to_goal(self, obs: Observation) -> Optional[Goal]:
    # ... existing code ...

    # Conversational gap -> learn goal
    if obs.source == "conversational_gap":
        return Goal(
            description=f"Learn from gap: {obs.content}",
            priority=GoalPriority.BACKGROUND,
            source_observation=obs,
            constraints=["Research appropriate direction", "Store learned pattern/rule"]
        )
```

### New Planner: Gap Research

```python
def _plan_gap_research(self, goal: Goal) -> List[PlanStep]:
    """Plan research for a conversational gap."""
    metadata = goal.source_observation.metadata if goal.source_observation else {}
    gap_type = metadata.get('type', 'unknown')
    direction = metadata.get('direction', 'outward')

    steps = [
        PlanStep(
            action="classify_research_direction",
            target="gap",
            parameters={'gap': metadata}
        ),
    ]

    if direction == 'inward':
        steps.append(PlanStep(
            action="read_canon",
            target="documents",
            parameters={'category': metadata.get('category', 'identity')}
        ))
    else:
        steps.append(PlanStep(
            action="web_search",
            target="discourse_norms",
            parameters={'query': metadata.get('query', '')}
        ))

    steps.append(PlanStep(
        action="extract_and_store_pattern",
        target="learning_system",
        parameters={'gap_type': gap_type}
    ))

    return steps
```

---

## Integration with provenance_tracker.py

### Provenance for ALL Research Results

Every research result—inward or outward—gets tracked:

```python
def _research_outward(self, category: str, query: str) -> Dict:
    """Research by searching the web."""
    from web_access import get_web_access
    web = get_web_access()

    results = {
        'direction': 'outward',
        'category': category,
        'sources': [],
        'content': [],
        'provenance_ids': [],
    }

    # Execute search
    search_results = web.search(query, num_results=5)

    for result in search_results:
        url = result.get('url', '')
        snippet = result.get('snippet', '')

        # Track provenance for each source
        if self.provenance:
            record_id = self.provenance.record(
                source_type=SourceType.EXTERNAL,
                source_id=self._extract_domain(url),  # e.g., "wikipedia.org"
                content=snippet,
                context=query,
                confidence=0.5,  # Unknown reliability initially
            )
            results['provenance_ids'].append(record_id)

        results['sources'].append(url)
        results['content'].append({
            'source': url,
            'text': snippet,
            'reliability': self._get_source_reliability(url),
        })

    return results

def _get_source_reliability(self, url: str) -> float:
    """Get reliability score for a web source."""
    if not self.provenance:
        return 0.5  # Unknown

    domain = self._extract_domain(url)
    return self.provenance.get_reliability(domain, domain="discourse")
```

### Source Evaluation

```python
# High-reliability sources for discourse research
TRUSTED_DISCOURSE_SOURCES = [
    'wikipedia.org',
    'merriam-webster.com',
    'britannica.com',
    'cambridge.org',
    'etiquettescholar.com',
]

# Low-reliability sources (social, opinion-based)
LOW_RELIABILITY_SOURCES = [
    'reddit.com',
    'quora.com',
    'yahoo.com/answers',
]

def _weight_research_results(self, results: Dict) -> List[Dict]:
    """Weight results by source reliability."""
    weighted = []

    for content in results['content']:
        source = content['source']
        base_reliability = content['reliability']

        # Boost trusted sources
        domain = self._extract_domain(source)
        if domain in TRUSTED_DISCOURSE_SOURCES:
            reliability = min(1.0, base_reliability + 0.3)
        elif domain in LOW_RELIABILITY_SOURCES:
            reliability = max(0.1, base_reliability - 0.3)
        else:
            reliability = base_reliability

        weighted.append({
            'source': source,
            'text': content['text'],
            'reliability': reliability,
        })

    # Sort by reliability
    weighted.sort(key=lambda x: x['reliability'], reverse=True)
    return weighted
```

### Recording Outcomes

When a learned pattern is used successfully or fails:

```python
def _record_pattern_outcome(self, pattern_id: int, success: bool, provenance_ids: List[str]):
    """Record outcome of using a learned pattern."""
    outcome = OutcomeType.SUCCESS if success else OutcomeType.FAILURE

    for record_id in provenance_ids:
        if self.provenance:
            self.provenance.record_outcome(
                record_id=record_id,
                outcome=outcome,
                notes=f"Pattern {pattern_id} {'succeeded' if success else 'failed'}",
                domain="discourse"
            )
```

---

## Relationship to lessons_learned.py

### Three Complementary Systems, Not Competing

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DEMERZEL'S LEARNING SYSTEMS                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────┐                                            │
│  │  lessons_learned.py │  ← WHAT NOT TO DO (failures)               │
│  │                     │    - Sycophancy patterns to avoid          │
│  │  FailureType enum   │    - Permission loops to prevent           │
│  │  Lesson dataclass   │    - Context amnesia triggers              │
│  │                     │    - Model selection errors                │
│  └─────────────────────┘                                            │
│           ↓ prevents                                                │
│                                                                     │
│  ┌─────────────────────┐  ┌─────────────────────┐                   │
│  │ discourse_patterns  │  │ comprehension_rules │                   │
│  │                     │  │                     │                   │
│  │ HOW TO RESPOND      │  │ HOW TO UNDERSTAND   │                   │
│  │ - Greeting templates│  │ - Intent parsing    │                   │
│  │ - Gratitude norms   │  │ - Dialogue state    │                   │
│  │ - Farewell patterns │  │ - Reference tracking│                   │
│  │                     │  │ - Correction detect │                   │
│  └─────────────────────┘  └─────────────────────┘                   │
│           ↓ generates              ↓ informs                        │
│                                                                     │
│                    APPROPRIATE RESPONSE                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### How They Work Together

```python
def process_conversation(self, user_input: str) -> str:
    # STEP 1: Check lessons_learned for failure patterns to AVOID
    if self.lessons:
        prevention_checks = self.lessons.get_prevention_checks(user_input)
        # These inform what NOT to do in the response

    # STEP 2: Apply comprehension_rules to UNDERSTAND
    if self.comprehension:
        understanding = self.comprehension.apply_rules(user_input)
        # This tells us what the user MEANS

    # STEP 3: Check discourse_patterns for HOW TO RESPOND
    if self.discourse:
        pattern = self.discourse.match_pattern(user_input)
        if pattern:
            response = self.discourse.generate_response(pattern)
            # Apply lessons_learned filters to avoid failure patterns
            response = self.lessons.apply_response_filter(response, prevention_checks)
            return response

    # STEP 4: If no pattern, generate response (existing flow)
    response = self._generate_response(user_input, understanding)

    # STEP 5: Check response against lessons_learned
    passed, violations = self.lessons.check_response_against_lessons(response, user_input)
    if not passed:
        # Regenerate avoiding violations
        response = self._regenerate_avoiding(response, violations)

    return response
```

### Shared Database, Separate Tables

All three systems use `memory.db` but separate tables:

```sql
-- lessons_learned.py
CREATE TABLE lessons_learned (
    id INTEGER PRIMARY KEY,
    failure_type TEXT NOT NULL,
    trigger_pattern TEXT NOT NULL,
    ...
);

-- discourse_patterns.py
CREATE TABLE discourse_patterns (
    id INTEGER PRIMARY KEY,
    discourse_type TEXT NOT NULL,
    trigger_patterns TEXT NOT NULL,  -- JSON
    response_template TEXT NOT NULL,
    ...
);

-- comprehension_rules.py
CREATE TABLE comprehension_rules (
    id INTEGER PRIMARY KEY,
    comprehension_type TEXT NOT NULL,
    trigger_patterns TEXT NOT NULL,  -- JSON
    understanding_strategy TEXT NOT NULL,
    ...
);
```

---

## THE BIG ONE: INWARD Research for Self-Understanding

### She Cannot Google "What Am I"

When Demerzel needs to understand herself, she reads her own documentation:

```python
class SelfUnderstanding:
    """
    Demerzel's ability to understand HERSELF.
    This is ALWAYS inward research - never web search.
    """

    def __init__(self, demerzel_dir: str = "/Users/jamienucho/demerzel"):
        self.demerzel_dir = Path(demerzel_dir)
        self.canon_cache = {}
        self._load_canon()

    def _load_canon(self):
        """Load all canon documents into memory."""
        for category, paths in CANON_DOCUMENTS.items():
            self.canon_cache[category] = []
            for path in paths:
                full_path = self.demerzel_dir / path
                if full_path.exists():
                    self.canon_cache[category].append({
                        'path': path,
                        'content': full_path.read_text(),
                    })

    def understand_self(self, question: str) -> str:
        """
        Answer a question about self by reading canon.
        This is how Demerzel knows who she is.
        """
        # Classify which aspect of self
        category = self._classify_self_question(question)

        # Search relevant canon documents
        relevant = self._search_canon(category, question)

        if relevant:
            # Synthesize answer from canon (CODE decides, LLM polishes)
            answer = self._synthesize_from_canon(relevant, question)
            return answer
        else:
            return "I should know this about myself, but I cannot find it in my canon. This may indicate a gap in my documentation."

    def _classify_self_question(self, question: str) -> str:
        """Classify what aspect of self the question is about."""
        q_lower = question.lower()

        if any(w in q_lower for w in ['who', 'am i', 'are you', 'identity', 'name']):
            return 'identity'
        elif any(w in q_lower for w in ['architecture', 'design', 'structure', 'r→c→i', 'code']):
            return 'architecture'
        elif any(w in q_lower for w in ['constraint', 'law', 'rule', 'cannot', 'boundary']):
            return 'constraints'
        elif any(w in q_lower for w in ['why', 'purpose', 'theory', 'bounded', 'ark']):
            return 'theory'
        else:
            return 'identity'  # Default

    def _search_canon(self, category: str, question: str) -> List[Dict]:
        """Search canon documents for relevant content."""
        docs = self.canon_cache.get(category, [])
        results = []

        for doc in docs:
            relevant = self._extract_relevant(doc['content'], question)
            if relevant:
                results.append({
                    'source': doc['path'],
                    'content': relevant,
                })

        return results

    def _synthesize_from_canon(self, sources: List[Dict], question: str) -> str:
        """
        Synthesize an answer from canon sources.
        CODE structures the answer, LLM only polishes language.
        """
        # Combine relevant excerpts
        combined = "\n\n".join([s['content'] for s in sources])

        # CODE determines what the answer SHOULD be
        answer_structure = {
            'sources': [s['source'] for s in sources],
            'key_points': self._extract_key_points(combined, question),
            'confidence': 1.0,  # Canon is authoritative
        }

        # LLM polishes into natural language (optional)
        if self.llm_pool:
            answer = self._llm_polish(answer_structure, question)
        else:
            answer = ". ".join(answer_structure['key_points'])

        return answer
```

### Integrated Flow: INWARD vs OUTWARD

```
USER INPUT
    ↓
IS THIS ABOUT SELF?
    ├── YES: "Who am I?", "What's my purpose?", "Why was I built?"
    │   ↓
    │   RESEARCH INWARD
    │   - Read DEMERZEL_IDENTITY.md
    │   - Read canon documents
    │   - Read Root Source papers
    │   - Synthesize answer from OWN documentation
    │   ↓
    │   ANSWER FROM CANON (confidence: 1.0)
    │
    └── NO: "How should I respond to greetings?", "What does 'thank you' expect?"
        ↓
        RESEARCH OUTWARD
        - Web search for human norms
        - Evaluate source reliability (provenance_tracker)
        - Extract patterns from results
        ↓
        ANSWER FROM WEB (confidence: varies by source)
```

### The Critical Distinction

```python
def route_research(self, gap_type: GapType, user_input: str) -> Callable:
    """
    Route to correct research method based on question type.

    THE CRITICAL DISTINCTION:
    - Questions about HUMAN norms → web research
    - Questions about SELF → canon research

    She cannot understand herself by googling.
    She must read her own documentation.
    """
    if self._is_self_question(user_input):
        return self._research_inward
    else:
        return self._research_outward

def _is_self_question(self, user_input: str) -> bool:
    """Determine if this is a question about self."""
    return any(re.search(p, user_input.lower()) for p in IDENTITY_TRIGGER_PATTERNS)
```

---

## Tuning Parameters

### Seed Patterns: Is This Enough to Start?

**Goal**: Cover the most common failure modes so early conversations aren't painful.

**Current seed coverage:**

| Category | Patterns Seeded | Estimated Coverage |
|----------|-----------------|-------------------|
| Discourse: Greeting | 4 patterns (morning, hello, hi, hey) | ~80% of greetings |
| Discourse: Gratitude | 3 patterns (thank you, thanks, appreciate) | ~90% of thanks |
| Discourse: Farewell | 4 patterns (goodbye, bye, see you, take care) | ~70% of farewells |
| Discourse: Small talk | 3 patterns (how are you, what's up, how's it going) | ~60% of small talk |
| Comprehension: Instruction setup | 4 patterns | ~70% of setup phrases |
| Comprehension: Correction intent | 4 patterns | ~80% of corrections |
| Comprehension: Reference tracking | 3 patterns | ~50% of references |

**Assessment**: This covers the CRITICAL failures from the problem statement. Gaps will still occur for edge cases, but core conversational flow should work.

**Tuning knob**: `MINIMUM_SEED_COVERAGE`

```python
# If changing seeds, ensure these minimums are met:
MINIMUM_SEED_COVERAGE = {
    'greeting': 3,           # Must handle at least 3 greeting variants
    'gratitude': 2,          # Must handle thank you + thanks
    'instruction_setup': 2,  # Must handle "I'm going to" + "ready?"
}

def validate_seed_coverage():
    """Run at startup to ensure seeds are adequate."""
    for category, minimum in MINIMUM_SEED_COVERAGE.items():
        actual = count_patterns_for_category(category)
        if actual < minimum:
            print(f"[WARNING] Seed coverage low for {category}: {actual} < {minimum}")
```

**Future expansion**: After initial deployment, analyze `pending_gaps.json` to identify which categories need more seeds.

### Gap Research Priority: What If 50 Gaps Accumulate?

**Problem**: If gaps accumulate faster than they're researched, learning backlog drowns her.

**Solution**: Prioritized gap queue with decay and deduplication.

```python
class GapQueue:
    """
    Prioritized queue for pending gaps.
    Prevents backlog drowning through decay and deduplication.
    """

    MAX_PENDING_GAPS = 20        # Hard limit - oldest drop off
    DECAY_THRESHOLD_HOURS = 24  # Gaps older than this get lower priority
    BATCH_SIZE = 3              # Research this many per autonomous cycle

    def __init__(self):
        self.gaps = []

    def add_gap(self, gap: Dict):
        """Add a gap, deduplicating and enforcing limits."""

        # DEDUPLICATE: Same input_type + category = same gap
        key = f"{gap['type']}:{gap['category']}"
        for existing in self.gaps:
            existing_key = f"{existing['type']}:{existing['category']}"
            if existing_key == key:
                # Already have this gap type, just increment count
                existing['occurrence_count'] = existing.get('occurrence_count', 1) + 1
                existing['last_seen'] = datetime.now().isoformat()
                return

        # NEW GAP
        gap['occurrence_count'] = 1
        gap['added_at'] = datetime.now().isoformat()
        self.gaps.append(gap)

        # ENFORCE LIMIT: Drop oldest if over max
        if len(self.gaps) > self.MAX_PENDING_GAPS:
            self._drop_oldest()

    def get_next_batch(self) -> List[Dict]:
        """Get next batch of gaps to research, prioritized."""

        # Priority scoring:
        # - Higher occurrence_count = more urgent (keeps happening)
        # - More recent = more relevant
        # - COMPREHENSION_GAP > PATTERN_GAP (comprehension failures are worse)

        def priority_score(gap):
            occurrence = gap.get('occurrence_count', 1)
            age_hours = self._age_in_hours(gap['added_at'])
            type_weight = 2 if gap['type'] == 'comprehension_gap' else 1

            # Score: occurrences * type_weight, decayed by age
            decay = max(0.1, 1.0 - (age_hours / 48))  # Decay over 48 hours
            return occurrence * type_weight * decay

        # Sort by priority
        sorted_gaps = sorted(self.gaps, key=priority_score, reverse=True)

        # Return top batch
        batch = sorted_gaps[:self.BATCH_SIZE]

        # Mark as being researched
        for gap in batch:
            gap['researching'] = True

        return batch

    def mark_researched(self, gap: Dict):
        """Remove gap after successful research."""
        self.gaps = [g for g in self.gaps if g != gap]

    def _drop_oldest(self):
        """Drop oldest, lowest-occurrence gaps when over limit."""
        # Sort by (occurrence_count ASC, added_at ASC) - drop lowest/oldest
        self.gaps.sort(key=lambda g: (g.get('occurrence_count', 1), g['added_at']))
        self.gaps = self.gaps[1:]  # Drop first (lowest priority)

    def _age_in_hours(self, timestamp: str) -> float:
        added = datetime.fromisoformat(timestamp)
        return (datetime.now() - added).total_seconds() / 3600
```

**Tuning knobs:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `MAX_PENDING_GAPS` | 20 | Hard limit on queue size |
| `DECAY_THRESHOLD_HOURS` | 24 | Gaps older than this deprioritize |
| `BATCH_SIZE` | 3 | Gaps researched per cycle |
| `DEDUPLICATE` | True | Same type+category = same gap |

**Behavior under load:**

```
Scenario: 50 greeting failures in one day
─────────────────────────────────────────
- First failure: Add gap {type: pattern_gap, category: greeting, count: 1}
- Failures 2-50: Increment count → {count: 50}
- Result: ONE gap with high priority (count=50), not 50 gaps

Scenario: Many different failure types
────────────────────────────────────────
- 10 greeting failures, 5 thanks failures, 3 setup failures, 2 reference failures
- Queue: 4 gaps (deduplicated by type+category)
- Priority: setup (comprehension, urgent) > greeting (pattern, high count) > thanks > reference

Scenario: Queue hits MAX_PENDING_GAPS
────────────────────────────────────────
- 21st gap arrives
- Oldest, lowest-occurrence gap dropped
- Queue stays at 20
```

**Integration with autonomous_loop:**

```python
# In autonomous_loop.py
def _observe_conversational_gaps(self) -> List[Observation]:
    """Check for gaps needing research."""
    observations = []

    if self.gap_queue.has_pending():
        batch = self.gap_queue.get_next_batch()
        for gap in batch:
            observations.append(Observation(
                source="conversational_gap",
                content=f"{gap['type']}: {gap['category']} (x{gap.get('occurrence_count', 1)})",
                timestamp=datetime.now(),
                priority=GoalPriority.BACKGROUND,  # Still background, but...
                metadata=gap
            ))

    return observations

# Priority escalation: If a gap has high occurrence count, escalate
def _observation_to_goal(self, obs: Observation) -> Optional[Goal]:
    if obs.source == "conversational_gap":
        count = obs.metadata.get('occurrence_count', 1)

        # HIGH occurrence = escalate priority
        if count > 10:
            priority = GoalPriority.MEDIUM  # Escalate from BACKGROUND
        elif count > 5:
            priority = GoalPriority.LOW
        else:
            priority = GoalPriority.BACKGROUND

        return Goal(
            description=f"Learn from gap: {obs.content}",
            priority=priority,
            source_observation=obs,
        )
```

**Summary**: She won't drown. Gaps deduplicate, prioritize, and decay. High-occurrence gaps escalate. Queue has hard limit.

---

## Updated Implementation Order

### Phase 1: Foundation
1. Create `conversational_gaps.py`
   - GapType enum
   - ResearchDirection enum ← **NEW**
   - classify_research_direction() ← **NEW**

### Phase 2: Self-Understanding (INWARD)
2. Create `self_understanding.py` ← **NEW**
   - Canon document registry
   - Canon search and retrieval
   - Self-question classification
   - Answer synthesis from canon

### Phase 3: Pattern Track (OUTWARD)
3. Create `discourse_patterns.py`
   - With provenance tracking ← **UPDATED**

### Phase 4: Comprehension Track
4. Create `comprehension_rules.py`
   - With direction-aware research ← **UPDATED**

### Phase 5: Integration
5. Modify `demerzel_brain.py`
   - Add research routing (inward vs outward)
   - Integrate all three learning systems
   - Connect to lessons_learned

6. Modify `autonomous_loop.py`
   - Add conversational gap observer
   - Add gap research planner
   - Add research execution steps

7. Integrate `provenance_tracker.py`
   - Track all research results
   - Record outcomes
   - Weight sources by reliability

### Phase 6: Testing
8. Test the complete system
   - Self-questions use inward research
   - Human-norm questions use outward research
   - Provenance tracks all sources
   - Autonomous loop processes gaps
   - All three systems work together
