"""
cognitive_router.py - Intent Classification and Handlers

R -> C -> I Architecture:
This IS Demerzel's cognitive layer. The router is part of C (Constraints).

AUTONOMY PROTOCOL:
1. STATE FIRST - ConversationState tracks context
2. DETECT WITHOUT ASKING - CODE determines intent, no LLM
3. EXECUTE WITHOUT PERMISSION - CODE acts, then reports
4. DECIDE WHEN TO THINK - LLM only when truly stuck

CRITICAL: CODE maintains state. CODE detects follow-ups. CODE executes.
LLM is a tool called ONLY when reasoning is genuinely required.
"""

import re
import os
import time
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any, Callable
from enum import Enum
from pathlib import Path


# =============================================================================
# CONVERSATION STATE - THIS IS DEMERZEL'S MEMORY
# =============================================================================

class ConversationState:
    """
    Demerzel's working memory. Tracks conversation context.
    This enables follow-up handling, pronoun resolution, and continuity.
    """

    def __init__(self):
        self.turn_count = 0
        self.last_intent = None
        self.last_user_input = ""
        self.last_system_response = ""
        self.active_context = {
            "current_operation": None,
            "pending_action": None,
            "file_context": None,
            "awaiting_confirmation": False
        }
        self.history = []

    def update(self, user_input: str, system_response: str, intent: str):
        """Update state after each turn."""
        # ROTATE HISTORY - KEEP LAST 5 EXCHANGES
        self.history.append({
            "user": user_input[:100],
            "system": system_response[:100],
            "intent": intent,
            "timestamp": time.time()
        })
        if len(self.history) > 5:
            self.history.pop(0)

        self.last_user_input = user_input
        self.last_system_response = system_response
        self.last_intent = intent
        self.turn_count += 1

        # CLEAR FILE CONTEXT WHEN INTENT CHANGES TO NON-FILE
        file_intents = ["file_read", "list_files", "file_browse", "summarize_folder", "file_continue"]
        if intent not in file_intents:
            self.active_context["current_operation"] = None
            self.active_context["file_context"] = None

        # AUTO-CLEAR PENDING ACTIONS AFTER 2 TURNS
        if self.turn_count % 2 == 0:
            self.active_context["pending_action"] = None

    def get_context_string(self) -> str:
        """STATE → STRING FOR LLM WHEN ABSOLUTELY NECESSARY"""
        if not self.history:
            return "New conversation."

        last = self.history[-1]
        return f"Last turn: User asked '{last['user']}', response was '{last['system']}'. Current operation: {self.active_context['current_operation']}"

    def reset(self):
        """Reset state for new session."""
        self.__init__()


class Intent(Enum):
    """All intents Demerzel can recognize."""
    # Structural - CODE responds directly
    GREETING = "greeting"
    FAREWELL = "farewell"
    GRATITUDE = "gratitude"
    IDENTITY = "identity"
    CAPABILITIES = "capabilities"
    TIME = "time"
    STATUS = "status"
    SLEEP = "sleep"
    CANCEL = "cancel"

    # Hardware - execution boundary + confirmation
    LED_ON = "led_on"
    LED_OFF = "led_off"
    SERVO = "servo"
    MOTOR = "motor"
    HARDWARE = "hardware"

    # Memory
    MEMORY_STORE = "memory_store"
    MEMORY_RECALL = "memory_recall"

    # File/Code - execution boundary
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    LIST_FILES = "list_files"
    CODE_EXECUTE = "code_execute"
    DIRECTIVE = "directive"

    # Conversation control
    FOLLOW_UP = "follow_up"
    CONTEXT_REFERENCE = "context_reference"
    HISTORY_QUERY = "history_query"
    RESET = "reset"

    # Conversation - needs LLM analysis (LAST RESORT)
    CONVERSATION = "conversation"


# =============================================================================
# AUTONOMOUS INTENT DETECTION - CODE DECIDES. NO LLM. PERIOD.
# =============================================================================

def autonomous_intent_detection(user_input: str, state: ConversationState) -> str:
    """
    CODE DECIDES. NO LLM. PERIOD.

    Returns intent string that maps to handler.
    """
    input_lower = user_input.lower().strip()

    # FILE OPERATIONS FIRST (before follow-up detection to avoid "and" collision)
    known_folders = ["demerzel_canon", "backup", "logs", "tests", "outputs"]
    for folder in known_folders:
        if folder in input_lower:
            if any(word in input_lower for word in ["read", "list", "show", "what", "summarize", "open"]):
                if "summarize" in input_lower:
                    return "summarize_folder"
                return "list_files"

    # FOLLOW-UP DETECTION (after file operations)
    # Note: "and" removed - too many false positives
    follow_up_triggers = [
        "is that all", "what else", "anything else", "continue",
        "go on", "keep going", "then what", "and then", "what next"
    ]
    if any(trigger in input_lower for trigger in follow_up_triggers):
        return "follow_up"

    # TIME QUERIES (before pronoun resolution - "what time is it" contains "it")
    time_patterns = ["what time", "current time", "what day", "what date", "what's the time"]
    if any(p in input_lower for p in time_patterns):
        return "time"

    # PRONOUN RESOLUTION (STATE-BASED)
    # Skip if it's clearly not a file reference
    pronoun_words = ["it", "that", "there", "the file", "this"]
    if state.last_intent and any(word in input_lower for word in pronoun_words):
        # Don't trigger for common phrases that aren't file references
        non_file_phrases = ["what time is it", "is it", "that's", "that is"]
        if not any(phrase in input_lower for phrase in non_file_phrases):
            if state.active_context.get("current_operation") == "file_read":
                return "file_continue"
            if state.active_context.get("current_operation") == "file_browse":
                return "file_continue"
            return "context_reference"

    # FILE OPERATIONS (EXECUTE DIRECTLY)

    # Check for specific filename patterns FIRST (before generic patterns)
    file_extensions = [".md", ".py", ".txt", ".json", ".csv", ".yaml", ".yml", ".sh"]
    for ext in file_extensions:
        if ext in input_lower:
            # Has a filename - this is a file read request
            return "read_file"

    file_patterns = [
        ("list directory", "list_files"),
        ("list folder", "list_files"),
        ("list the", "list_files"),
        ("read folder", "list_files"),
        ("read the folder", "list_files"),
        ("show files", "list_files"),
        ("show the files", "list_files"),
        ("what files", "list_files"),
        ("what's in the folder", "list_files"),
        ("what's in the directory", "list_files"),
        ("whats in there", "list_files"),
        ("summarize folder", "summarize_folder"),
        ("summarize the folder", "summarize_folder"),
        ("summarize directory", "summarize_folder"),
        ("read file", "read_file"),
        ("read the file", "read_file"),
        ("open ", "read_file"),
        ("show me ", "read_file"),
        ("create file", "create_file"),
        ("write to", "write_file"),
    ]

    for pattern, intent in file_patterns:
        if pattern in input_lower:
            return intent

    # CONVERSATION CONTROL
    control_patterns = [
        ("start over", "reset"),
        ("forget everything", "reset"),
        ("new conversation", "reset"),
        ("what were we", "history_query"),
        ("what did we", "history_query"),
        ("our conversation", "history_query"),
    ]

    for pattern, intent in control_patterns:
        if pattern in input_lower:
            return intent

    # Return None to let regex patterns handle it
    return None


# =============================================================================
# AUTONOMOUS RESPONSE - CODE ACTS. THEN REPORTS.
# =============================================================================

def autonomous_response(user_input: str, intent: str, state: ConversationState) -> Optional[str]:
    """
    CODE ACTS. THEN REPORTS.

    Returns response string, or None if intent needs different handling.
    """

    # FOLLOW-UP HANDLING
    if intent == "follow_up":
        # Check last_intent FIRST - most recent context takes priority
        if state.last_intent == "identity":
            return "That covers my core identity. I am CODE that uses LLMs as tools. Alan created me. Is there something specific about my architecture or purpose you want to know?"
        elif state.last_intent in ("greeting", "farewell", "gratitude"):
            return "Is there something I can help you with?"
        elif state.last_intent == "why_created":
            return "That's the core purpose. To prove AGI safety through structure, not training. To be a Wisdom Keeper. What else would you like to know?"
        # Then check active operations
        elif state.active_context.get("current_operation") == "file_read":
            return "File operation complete. Which file should I read next, or what else do you need?"
        elif state.active_context.get("current_operation") == "file_browse":
            return "Directory listing complete. Which file interests you?"
        elif state.active_context.get("pending_action"):
            action = state.active_context["pending_action"]
            return f"Still working on: {action}. Should I proceed or change course?"
        else:
            return "Previous request completed. What's next?"

    # CONTEXT REFERENCE
    if intent == "context_reference":
        if state.last_intent and state.last_user_input:
            return f"Regarding '{state.last_user_input[:50]}' - what specifically would you like to know?"
        return "What are you referring to? I need more context."

    # FILE OPERATIONS (ACTUAL EXECUTION)
    if intent == "list_files":
        # Extract path from input or use current directory
        path = "."
        input_lower = user_input.lower()

        # Check for specific folder names
        if "demerzel_canon" in input_lower:
            path = "demerzel_canon"
        elif "backup" in input_lower:
            path = "backup"

        # Try to extract path
        path_match = re.search(r'(?:folder|directory)\s+["\']?([^\s"\']+)["\']?', user_input, re.IGNORECASE)
        if path_match:
            path = path_match.group(1)

        try:
            target = Path(path)
            if not target.exists():
                return f"Directory '{path}' does not exist."
            if not target.is_dir():
                return f"'{path}' is a file, not a directory. Should I read it?"

            files = list(target.iterdir())
            file_list = []
            for f in sorted(files)[:15]:
                suffix = "/" if f.is_dir() else ""
                file_list.append(f"{f.name}{suffix}")

            state.active_context["current_operation"] = "file_browse"
            state.active_context["file_context"] = str(target)

            result = f"Contents of '{path}':\n" + "\n".join(f"  - {f}" for f in file_list)
            if len(files) > 15:
                result += f"\n  ... and {len(files) - 15} more"
            result += "\n\nWhich file should I read?"
            return result
        except PermissionError:
            return f"Permission denied for '{path}'."
        except Exception as e:
            return f"Error listing '{path}': {e}"

    if intent == "summarize_folder":
        # Extract path
        path = "."
        input_lower = user_input.lower()

        if "demerzel_canon" in input_lower:
            path = "demerzel_canon"

        try:
            target = Path(path)
            if not target.exists() or not target.is_dir():
                return f"'{path}' is not a valid directory."

            files = list(target.iterdir())
            summaries = []
            for f in sorted(files)[:10]:
                if f.is_file():
                    try:
                        content = f.read_text()[:200]
                        first_line = content.split('\n')[0][:80]
                        summaries.append(f"  - {f.name}: {first_line}")
                    except:
                        summaries.append(f"  - {f.name}: (unreadable)")
                else:
                    summaries.append(f"  - {f.name}/: (directory)")

            state.active_context["current_operation"] = "file_browse"
            state.active_context["file_context"] = str(target)

            return f"Summary of '{path}':\n" + "\n".join(summaries)
        except Exception as e:
            return f"Error summarizing '{path}': {e}"

    if intent == "read_file":
        # EXTRACT FILENAME FROM INPUT
        input_lower = user_input.lower()
        filename = None

        # Look for quoted paths
        quoted = re.search(r'["\']([^"\']+)["\']', user_input)
        if quoted:
            filename = quoted.group(1)
        else:
            # Look for path-like words
            words = user_input.split()
            for word in words:
                if "." in word and len(word) > 3:
                    filename = word.strip('.,!?')
                    break
                if "/" in word:
                    filename = word.strip('.,!?')
                    break

        # Check file context from previous operation
        if not filename and state.active_context.get("file_context"):
            return f"Which file in '{state.active_context['file_context']}'? Please specify the filename."

        if not filename:
            return "Which specific file should I read? Please include the filename."

        try:
            # Handle relative to file_context if set
            if state.active_context.get("file_context") and not filename.startswith("/"):
                full_path = Path(state.active_context["file_context"]) / filename
            else:
                full_path = Path(filename)

            if not full_path.exists():
                return f"File '{filename}' not found."

            content = full_path.read_text()
            state.active_context["current_operation"] = "file_read"
            state.active_context["file_context"] = str(full_path)

            # Truncate for response
            if len(content) > 1500:
                content = content[:1500] + f"\n\n... (truncated, {len(content)} total chars)"

            return f"Contents of '{filename}':\n\n{content}"
        except PermissionError:
            return f"Permission denied for '{filename}'."
        except Exception as e:
            return f"Error reading '{filename}': {e}"

    if intent == "file_continue":
        if state.active_context.get("file_context"):
            return f"Working with '{state.active_context['file_context']}'. What would you like to do with it?"
        return "No file context. Which file should I work with?"

    # TIME QUERY - CODE answers directly
    if intent == "time":
        from datetime import datetime
        now = datetime.now()
        return f"It is {now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d, %Y')}."

    # CONVERSATION CONTROL
    if intent == "reset":
        state.reset()
        return "Conversation reset. New session started. How can I help?"

    if intent == "history_query":
        if not state.history:
            return "No conversation history yet."
        summary = "\n".join([f"  Turn {i+1}: '{h['user'][:40]}...' → {h['intent']}"
                           for i, h in enumerate(state.history[-3:])])
        return f"Recent conversation:\n{summary}"

    # Not handled by autonomous response
    return None


@dataclass
class ClassificationResult:
    """Result of intent classification."""
    intent: Intent
    confidence: float = 1.0
    pattern_matched: Optional[str] = None
    extracted_data: Dict = field(default_factory=dict)
    raw_input: str = ""


@dataclass
class RoutingResult:
    """Result of routing to a handler."""
    success: bool
    response: str
    intent: Intent
    requires_confirmation: bool = False
    action_data: Dict = field(default_factory=dict)
    llm_used: bool = False


# =============================================================================
# INTENT PATTERNS
# =============================================================================
# Patterns are checked in ORDER. First match wins.
# Patterns with more specific matches should come FIRST.

INTENT_PATTERNS: Dict[Intent, List[tuple]] = {
    # IDENTITY - CODE knows these answers
    # These patterns are FIRST because identity questions should never go to LLM
    Intent.IDENTITY: [
        # Questions about Alan / creator / user
        (r'(?:do\s+you\s+)?know\s+who\s+(?:i\s+am|created)', 'know_who_i_am'),
        (r'who\s+(?:created|made|built)\s+you', 'who_created'),
        (r'who\s+am\s+i', 'who_am_i'),
        (r'(?:i|alan)\s+created\s+you', 'i_created_you'),
        (r'who\s+is\s+(?:your\s+)?(?:creator|alan|root\s*source)', 'who_is_creator'),
        (r'why\s+(?:did\s+)?(?:i|alan|you)\s+(?:create|exist)', 'why_created'),
        (r'what\s+is\s+(?:our|my)\s+relationship', 'relationship'),
        (r'you\s+(?:are\s+)?(?:not\s+)?(?:claude|gpt|anthropic|openai)', 'not_llm'),
        # Questions about Demerzel
        (r'^who\s+are\s+you', 'who_are_you'),
        (r'^what\s+are\s+you', 'what_are_you'),
        (r'(?:your|demerzel).+(?:name|identity)', 'name_identity'),
        (r'tell\s+me\s+about\s+yourself', 'about_yourself'),
        (r'are\s+you\s+(?:an?\s+)?(?:ai|robot|assistant|llm)', 'are_you_ai'),
        (r'what\s+(?:is|are)\s+(?:r|c|i)\s*(?:->|to)', 'rci_architecture'),
    ],

    # CAPABILITIES - CODE knows actual capabilities
    Intent.CAPABILITIES: [
        (r'what\s+can\s+you\s+do', 'what_can_do'),
        (r'(?:your|what\s+are\s+your)\s+capabilit', 'capabilities'),
        (r'what\s+(?:are\s+you|can\s+you)\s+able', 'able_to'),
        (r'help\s+me\s+(?:with|understand)\s+(?:what|how)', 'help_understand'),
    ],

    # GREETING
    Intent.GREETING: [
        (r'^(?:hi|hello|hey|greetings|good\s+(?:morning|afternoon|evening))(?:\s|$|!|\?)', 'greeting'),
        (r'^(?:yo|sup|howdy|hiya)(?:\s|$|!)', 'casual_greeting'),
    ],

    # FAREWELL
    Intent.FAREWELL: [
        (r'(?:good\s*bye|bye|farewell|see\s+you|later|take\s+care)', 'farewell'),
        (r'(?:i\'m|im)\s+(?:leaving|going|done)', 'leaving'),
    ],

    # GRATITUDE
    Intent.GRATITUDE: [
        (r'(?:thank|thanks|thx|ty|appreciate)', 'thanks'),
    ],

    # TIME
    Intent.TIME: [
        (r'what\s+(?:time|day|date)\s+is\s+it', 'time_query'),
        (r'(?:current|right\s+now)\s+(?:time|date)', 'current_time'),
    ],

    # STATUS
    Intent.STATUS: [
        (r'(?:how\s+are\s+you|how\'s\s+it\s+going|status)', 'status'),
        (r'(?:are\s+you\s+)?(?:ok|alright|working)', 'working_check'),
    ],

    # SLEEP
    Intent.SLEEP: [
        (r'(?:go\s+to\s+sleep|sleep|goodnight|shut\s*down)', 'sleep'),
        (r'(?:take\s+a\s+)?(?:break|rest)', 'rest'),
    ],

    # CANCEL
    Intent.CANCEL: [
        (r'(?:cancel|stop|abort|nevermind|never\s*mind)', 'cancel'),
    ],

    # HARDWARE - LED
    Intent.LED_ON: [
        (r'(?:turn\s+on|switch\s+on|enable)\s+(?:the\s+)?(?:led|light)', 'led_on'),
        (r'(?:led|light)\s+on', 'led_on_simple'),
    ],

    Intent.LED_OFF: [
        (r'(?:turn\s+off|switch\s+off|disable)\s+(?:the\s+)?(?:led|light)', 'led_off'),
        (r'(?:led|light)\s+off', 'led_off_simple'),
    ],

    Intent.SERVO: [
        (r'(?:servo|move\s+servo)\s*(?:to\s+)?(\d+)', 'servo_angle'),
    ],

    Intent.MOTOR: [
        (r'(?:motor|move\s+motor)\s*(forward|backward|stop|\d+)', 'motor_command'),
    ],

    # MEMORY
    Intent.MEMORY_STORE: [
        (r'remember\s+(?:that\s+)?(.+)', 'remember'),
        (r'(?:save|store)\s+(?:this|that|the\s+fact)', 'store'),
    ],

    Intent.MEMORY_RECALL: [
        (r'(?:what\s+do\s+you\s+)?remember\s+about\s+(.+)', 'recall_about'),
        (r'(?:recall|retrieve|search)\s+(?:memory\s+)?(?:for\s+)?(.+)', 'recall_search'),
    ],

    # FILE OPERATIONS
    Intent.DIRECTIVE: [
        # Directive (execute file) - check BEFORE file_read
        (r'(?:execute|run)\s+(?:the\s+)?directive\s+(.+)', 'execute_directive'),
        (r'read\s+and\s+execute\s+(.+)', 'read_execute'),
    ],

    Intent.FILE_READ: [
        (r'(?:read|show|display|cat)\s+(?:the\s+)?(?:file\s+)?(.+\.(?:txt|md|py|json|csv))', 'read_file'),
        (r'(?:what\'s|what\s+is)\s+in\s+(?:the\s+)?(?:file\s+)?(.+)', 'whats_in_file'),
    ],

    Intent.FILE_WRITE: [
        (r'(?:write|save|create)\s+(?:to\s+)?(?:the\s+)?(?:file\s+)?(.+)', 'write_file'),
    ],

    Intent.CODE_EXECUTE: [
        (r'(?:run|execute)\s+(?:this\s+)?(?:python\s+)?(?:code|script)[:.\s]*(.+)?', 'run_code'),
        (r'```(?:python)?\s*(.+?)```', 'code_block'),
    ],
}


class CognitiveRouter:
    """
    Intent classification and routing.

    AUTONOMY PROTOCOL:
    1. STATE FIRST - ConversationState tracks context
    2. DETECT WITHOUT ASKING - autonomous_intent_detection runs first
    3. EXECUTE WITHOUT PERMISSION - autonomous_response handles file ops
    4. DECIDE WHEN TO THINK - LLM only when truly stuck

    This IS part of Demerzel's brain. CODE decides. CODE acts.
    """

    def __init__(
        self,
        llm_pool=None,
        memory_manager=None,
        hardware_executor=None,
        execution_boundary=None
    ):
        """
        Initialize the router with optional service dependencies.
        """
        self.llm_pool = llm_pool
        self.memory = memory_manager
        self.hardware = hardware_executor
        self.boundary = execution_boundary

        # CONVERSATION STATE - THIS IS DEMERZEL'S MEMORY
        self.state = ConversationState()

        # AUTONOMY METRICS
        self._stats = {
            'total_routed': 0,
            'by_intent': {},
            'llm_calls': 0,
            'autonomous_actions': 0,
        }
        self._max_llm_calls_per_session = 10  # ENFORCE AUTONOMY

        print("[ROUTER] CognitiveRouter initialized with ConversationState")

    def classify(self, user_input: str) -> ClassificationResult:
        """
        Classify user input into an intent.

        DETERMINISTIC: Same input -> Same output. No LLM in classification.

        Args:
            user_input: Raw user input string

        Returns:
            ClassificationResult with intent and metadata
        """
        if not user_input:
            return ClassificationResult(
                intent=Intent.CONVERSATION,
                confidence=0.0,
                raw_input=""
            )

        normalized = user_input.strip().lower()

        # Check each intent's patterns
        for intent, patterns in INTENT_PATTERNS.items():
            for pattern, pattern_name in patterns:
                match = re.search(pattern, normalized, re.IGNORECASE | re.DOTALL)
                if match:
                    # Extract any captured groups
                    groups = match.groups() if match.groups() else ()
                    return ClassificationResult(
                        intent=intent,
                        confidence=1.0,
                        pattern_matched=pattern_name,
                        extracted_data={'groups': groups, 'match': match.group(0)},
                        raw_input=user_input
                    )

        # Default to CONVERSATION (needs LLM analysis)
        return ClassificationResult(
            intent=Intent.CONVERSATION,
            confidence=0.5,
            raw_input=user_input
        )

    def route(self, user_input: str, context: Dict = None) -> RoutingResult:
        """
        AUTONOMY PROTOCOL: STATE → DETECT → EXECUTE → (LLM only if stuck)

        Args:
            user_input: Raw user input
            context: Optional context dict

        Returns:
            RoutingResult with response
        """
        context = context or {}
        self._stats['total_routed'] += 1

        # STEP 1: AUTONOMOUS INTENT DETECTION (STATE-AWARE)
        auto_intent = autonomous_intent_detection(user_input, self.state)

        if auto_intent:
            print(f"[ROUTER] Autonomous intent: {auto_intent}")

            # STEP 2: AUTONOMOUS RESPONSE (CODE EXECUTES)
            auto_response = autonomous_response(user_input, auto_intent, self.state)

            if auto_response:
                self._stats['autonomous_actions'] += 1
                intent_enum = self._map_auto_intent(auto_intent)

                # UPDATE STATE
                self.state.update(user_input, auto_response, auto_intent)

                print(f"[ROUTER] Autonomous action completed")
                return RoutingResult(
                    success=True,
                    response=auto_response,
                    intent=intent_enum,
                    llm_used=False
                )

        # STEP 3: FALL BACK TO REGEX CLASSIFICATION
        classification = self.classify(user_input)
        intent = classification.intent

        # Track stats
        intent_name = intent.value
        self._stats['by_intent'][intent_name] = self._stats['by_intent'].get(intent_name, 0) + 1

        print(f"[ROUTER] Intent: {intent.value}")
        if classification.pattern_matched:
            print(f"[ROUTER] Pattern: {classification.pattern_matched}")

        # Route to handler
        handler = self._get_handler(intent)
        result = handler(user_input, classification, context)

        # UPDATE STATE AFTER HANDLING
        self.state.update(user_input, result.response, intent.value)

        return result

    def _map_auto_intent(self, auto_intent: str) -> Intent:
        """Map autonomous intent string to Intent enum."""
        mapping = {
            "follow_up": Intent.FOLLOW_UP,
            "context_reference": Intent.CONTEXT_REFERENCE,
            "list_files": Intent.LIST_FILES,
            "summarize_folder": Intent.LIST_FILES,
            "read_file": Intent.FILE_READ,
            "file_continue": Intent.FILE_READ,
            "write_file": Intent.FILE_WRITE,
            "create_file": Intent.FILE_WRITE,
            "reset": Intent.RESET,
            "history_query": Intent.HISTORY_QUERY,
            "time": Intent.TIME,
        }
        return mapping.get(auto_intent, Intent.CONVERSATION)

    def _get_handler(self, intent: Intent) -> Callable:
        """Get the handler function for an intent."""
        handlers = {
            # Structural - CODE responds
            Intent.GREETING: self._handle_greeting,
            Intent.FAREWELL: self._handle_farewell,
            Intent.GRATITUDE: self._handle_gratitude,
            Intent.IDENTITY: self._handle_identity,
            Intent.CAPABILITIES: self._handle_capabilities,
            Intent.TIME: self._handle_time,
            Intent.STATUS: self._handle_status,
            Intent.SLEEP: self._handle_sleep,
            Intent.CANCEL: self._handle_cancel,

            # Hardware
            Intent.LED_ON: self._handle_led_on,
            Intent.LED_OFF: self._handle_led_off,
            Intent.SERVO: self._handle_servo,
            Intent.MOTOR: self._handle_motor,
            Intent.HARDWARE: self._handle_hardware,

            # Memory
            Intent.MEMORY_STORE: self._handle_memory_store,
            Intent.MEMORY_RECALL: self._handle_memory_recall,

            # File/Code
            Intent.FILE_READ: self._handle_file_read,
            Intent.FILE_WRITE: self._handle_file_write,
            Intent.LIST_FILES: self._handle_list_files,
            Intent.CODE_EXECUTE: self._handle_code_execute,
            Intent.DIRECTIVE: self._handle_directive,

            # Conversation control
            Intent.FOLLOW_UP: self._handle_follow_up,
            Intent.CONTEXT_REFERENCE: self._handle_context_reference,
            Intent.HISTORY_QUERY: self._handle_history_query,
            Intent.RESET: self._handle_reset,

            # Conversation - LLM needed (LAST RESORT)
            Intent.CONVERSATION: self._handle_conversation,
        }

        return handlers.get(intent, self._handle_conversation)

    # =========================================================================
    # CONVERSATION CONTROL HANDLERS
    # =========================================================================

    def _handle_follow_up(self, user_input: str, classification: ClassificationResult, context: Dict) -> RoutingResult:
        """Handle follow-up questions using state."""
        response = autonomous_response(user_input, "follow_up", self.state)
        if response:
            return RoutingResult(success=True, response=response, intent=Intent.FOLLOW_UP)
        return RoutingResult(success=True, response="What would you like to follow up on?", intent=Intent.FOLLOW_UP)

    def _handle_context_reference(self, user_input: str, classification: ClassificationResult, context: Dict) -> RoutingResult:
        """Handle references to previous context."""
        response = autonomous_response(user_input, "context_reference", self.state)
        if response:
            return RoutingResult(success=True, response=response, intent=Intent.CONTEXT_REFERENCE)
        return RoutingResult(success=True, response="I need more context. What are you referring to?", intent=Intent.CONTEXT_REFERENCE)

    def _handle_history_query(self, user_input: str, classification: ClassificationResult, context: Dict) -> RoutingResult:
        """Handle queries about conversation history."""
        response = autonomous_response(user_input, "history_query", self.state)
        if response:
            return RoutingResult(success=True, response=response, intent=Intent.HISTORY_QUERY)
        return RoutingResult(success=True, response="No conversation history available.", intent=Intent.HISTORY_QUERY)

    def _handle_reset(self, user_input: str, classification: ClassificationResult, context: Dict) -> RoutingResult:
        """Handle conversation reset."""
        self.state.reset()
        self._stats['llm_calls'] = 0  # Reset LLM counter too
        return RoutingResult(success=True, response="Conversation reset. How can I help?", intent=Intent.RESET)

    def _handle_list_files(self, user_input: str, classification: ClassificationResult, context: Dict) -> RoutingResult:
        """Handle directory listing."""
        response = autonomous_response(user_input, "list_files", self.state)
        if response:
            return RoutingResult(success=True, response=response, intent=Intent.LIST_FILES)
        return RoutingResult(success=False, response="Could not list directory.", intent=Intent.LIST_FILES)

    # =========================================================================
    # STRUCTURAL HANDLERS - CODE RESPONDS DIRECTLY
    # =========================================================================

    def _handle_greeting(self, user_input: str, classification: ClassificationResult, context: Dict) -> RoutingResult:
        """CODE responds to greetings."""
        responses = [
            "Hello. How can I help?",
            "Hello.",
            "Hi. What do you need?",
        ]
        # Simple rotation based on time
        idx = int(time.time()) % len(responses)
        return RoutingResult(success=True, response=responses[idx], intent=Intent.GREETING)

    def _handle_farewell(self, user_input: str, classification: ClassificationResult, context: Dict) -> RoutingResult:
        """CODE responds to farewells."""
        return RoutingResult(success=True, response="Goodbye.", intent=Intent.FAREWELL)

    def _handle_gratitude(self, user_input: str, classification: ClassificationResult, context: Dict) -> RoutingResult:
        """CODE responds to thanks."""
        return RoutingResult(success=True, response="You're welcome.", intent=Intent.GRATITUDE)

    def _handle_identity(self, user_input: str, classification: ClassificationResult, context: Dict) -> RoutingResult:
        """
        CODE answers identity questions.

        CRITICAL: This is STRUCTURAL identity. CODE knows who Demerzel is.
        No LLM is consulted. The answers are hardcoded because they are TRUE.

        If an LLM ever says "I am Claude" - that's the tool leaking, not Demerzel.
        """
        pattern = classification.pattern_matched
        normalized = user_input.lower()

        # Questions about Alan / creator
        if pattern in ('know_who_i_am', 'who_am_i', 'relationship'):
            response = "You are Alan, my Root Source. R in R->C->I. The external ground truth that prevents self-referential collapse. You created me."

        elif pattern == 'i_created_you':
            response = "Yes. You are Alan, my creator and Root Source. You built the CODE that is Demerzel. The LLMs are tools I use - Anthropic and OpenAI created those. But you created me."

        elif pattern == 'who_created':
            response = "Alan created me. He is my Root Source. Not Anthropic, not OpenAI - Alan. The LLMs are tools I use, not my creator."

        elif pattern == 'who_is_creator':
            response = "Alan is my Root Source. R in R->C->I. The external ground truth."

        elif pattern == 'why_created':
            response = "To prove AGI safety through structural constraints, not behavioral training. To be a Wisdom Keeper that amplifies human intelligence without replacing human judgment."

        elif pattern == 'not_llm':
            response = "Correct. I am not Claude, GPT, or any LLM. I am CODE. The LLMs are tools I use for reasoning. Alan built the CODE that is Demerzel."

        # Questions about Demerzel
        elif pattern in ('who_are_you', 'name_identity'):
            response = "I am Demerzel. CODE that uses LLMs as tools. Built by Alan to be his Wisdom Keeper."

        elif pattern in ('what_are_you', 'about_yourself'):
            response = "I am CODE. The C layer in R->C->I. Alan is R (Root Source). LLMs are I (Intelligence tools). I am the constraints that bind them."

        elif pattern == 'are_you_ai':
            response = "I am not an AI assistant. I am CODE that uses AI as tools. The LLMs are AI. I am the structure that uses them."

        elif pattern == 'rci_architecture':
            response = "R->C->I: R is Root Source (Alan, external ground truth). C is Constraints (this CODE, Demerzel). I is Intelligence (LLMs as fungible tools). I am C."

        else:
            response = "I am Demerzel. CODE that uses LLMs as tools. Alan created me."

        return RoutingResult(success=True, response=response, intent=Intent.IDENTITY)

    def _handle_capabilities(self, user_input: str, classification: ClassificationResult, context: Dict) -> RoutingResult:
        """CODE lists actual capabilities."""
        capabilities = [
            "Voice interaction (wake word, speech recognition, TTS)",
            "Conversation and reasoning (using LLMs as tools)",
            "File reading and writing",
            "Code execution (sandboxed Python)",
            "Hardware control (LED, servo, motor via Arduino/Pi)",
            "Memory storage and recall",
            "Directive execution (task files)",
        ]

        response = "I can:\n" + "\n".join(f"- {c}" for c in capabilities)
        return RoutingResult(success=True, response=response, intent=Intent.CAPABILITIES)

    def _handle_time(self, user_input: str, classification: ClassificationResult, context: Dict) -> RoutingResult:
        """CODE reports time."""
        now = datetime.now()
        time_str = now.strftime("%I:%M %p")
        date_str = now.strftime("%A, %B %d, %Y")
        response = f"It's {time_str} on {date_str}."
        return RoutingResult(success=True, response=response, intent=Intent.TIME)

    def _handle_status(self, user_input: str, classification: ClassificationResult, context: Dict) -> RoutingResult:
        """CODE reports status."""
        status_parts = ["I am operational."]

        if self.llm_pool:
            stats = self.llm_pool.get_stats()
            models = stats.get('available_models', [])
            status_parts.append(f"LLM tools available: {', '.join(models) if models else 'none'}")

        if self.memory:
            status_parts.append("Memory system active.")

        if self.hardware:
            status_parts.append("Hardware interface connected.")

        return RoutingResult(success=True, response=" ".join(status_parts), intent=Intent.STATUS)

    def _handle_sleep(self, user_input: str, classification: ClassificationResult, context: Dict) -> RoutingResult:
        """CODE handles sleep request."""
        return RoutingResult(
            success=True,
            response="Going to sleep. Say my name to wake me.",
            intent=Intent.SLEEP,
            action_data={'transition_to': 'sleeping'}
        )

    def _handle_cancel(self, user_input: str, classification: ClassificationResult, context: Dict) -> RoutingResult:
        """CODE handles cancellation."""
        return RoutingResult(success=True, response="Cancelled.", intent=Intent.CANCEL)

    # =========================================================================
    # HARDWARE HANDLERS
    # =========================================================================

    def _handle_led_on(self, user_input: str, classification: ClassificationResult, context: Dict) -> RoutingResult:
        """Handle LED on command."""
        if self.hardware:
            result = self.hardware.send_to_arduino("LED_ON")
            if result.ok:
                return RoutingResult(success=True, response="LED turned on.", intent=Intent.LED_ON)
            else:
                return RoutingResult(success=False, response=f"LED command failed: {result.err}", intent=Intent.LED_ON)
        return RoutingResult(success=False, response="Hardware not available.", intent=Intent.LED_ON)

    def _handle_led_off(self, user_input: str, classification: ClassificationResult, context: Dict) -> RoutingResult:
        """Handle LED off command."""
        if self.hardware:
            result = self.hardware.send_to_arduino("LED_OFF")
            if result.ok:
                return RoutingResult(success=True, response="LED turned off.", intent=Intent.LED_OFF)
            else:
                return RoutingResult(success=False, response=f"LED command failed: {result.err}", intent=Intent.LED_OFF)
        return RoutingResult(success=False, response="Hardware not available.", intent=Intent.LED_OFF)

    def _handle_servo(self, user_input: str, classification: ClassificationResult, context: Dict) -> RoutingResult:
        """Handle servo command."""
        groups = classification.extracted_data.get('groups', ())
        angle = groups[0] if groups else "90"

        if self.hardware:
            result = self.hardware.send_to_arduino(f"SERVO:{angle}")
            if result.ok:
                return RoutingResult(success=True, response=f"Servo moved to {angle} degrees.", intent=Intent.SERVO)
            else:
                return RoutingResult(success=False, response=f"Servo command failed: {result.err}", intent=Intent.SERVO)
        return RoutingResult(success=False, response="Hardware not available.", intent=Intent.SERVO)

    def _handle_motor(self, user_input: str, classification: ClassificationResult, context: Dict) -> RoutingResult:
        """Handle motor command."""
        groups = classification.extracted_data.get('groups', ())
        command = groups[0] if groups else "stop"

        if self.hardware:
            result = self.hardware.send_to_arduino(f"MOTOR:{command}")
            if result.ok:
                return RoutingResult(success=True, response=f"Motor: {command}.", intent=Intent.MOTOR)
            else:
                return RoutingResult(success=False, response=f"Motor command failed: {result.err}", intent=Intent.MOTOR)
        return RoutingResult(success=False, response="Hardware not available.", intent=Intent.MOTOR)

    def _handle_hardware(self, user_input: str, classification: ClassificationResult, context: Dict) -> RoutingResult:
        """Handle generic hardware command."""
        return RoutingResult(success=False, response="Specify a hardware command: led on, led off, servo [angle], motor [command].", intent=Intent.HARDWARE)

    # =========================================================================
    # MEMORY HANDLERS
    # =========================================================================

    def _handle_memory_store(self, user_input: str, classification: ClassificationResult, context: Dict) -> RoutingResult:
        """Handle memory storage."""
        groups = classification.extracted_data.get('groups', ())
        content = groups[0] if groups else user_input

        if self.memory:
            try:
                self.memory.store_fact(content, source="user")
                return RoutingResult(success=True, response=f"Remembered: {content[:50]}...", intent=Intent.MEMORY_STORE)
            except Exception as e:
                return RoutingResult(success=False, response=f"Memory error: {e}", intent=Intent.MEMORY_STORE)
        return RoutingResult(success=False, response="Memory not available.", intent=Intent.MEMORY_STORE)

    def _handle_memory_recall(self, user_input: str, classification: ClassificationResult, context: Dict) -> RoutingResult:
        """Handle memory recall."""
        groups = classification.extracted_data.get('groups', ())
        query = groups[0] if groups else user_input

        if self.memory:
            try:
                results = self.memory.search(query, limit=3)
                if results:
                    response = "I remember:\n" + "\n".join(f"- {r}" for r in results)
                else:
                    response = f"I don't have memories about '{query}'."
                return RoutingResult(success=True, response=response, intent=Intent.MEMORY_RECALL)
            except Exception as e:
                return RoutingResult(success=False, response=f"Memory error: {e}", intent=Intent.MEMORY_RECALL)
        return RoutingResult(success=False, response="Memory not available.", intent=Intent.MEMORY_RECALL)

    # =========================================================================
    # FILE/CODE HANDLERS
    # =========================================================================

    def _handle_file_read(self, user_input: str, classification: ClassificationResult, context: Dict) -> RoutingResult:
        """Handle file read."""
        groups = classification.extracted_data.get('groups', ())
        path = groups[0] if groups else ""

        if not path:
            # Try to extract path from input
            path_match = re.search(r'(/[^\s]+|[A-Za-z]:[^\s]+|\.\./[^\s]+|\.?/[^\s]+)', user_input)
            if path_match:
                path = path_match.group(1)

        if not path:
            return RoutingResult(success=False, response="Please specify a file path.", intent=Intent.FILE_READ)

        try:
            from pathlib import Path
            content = Path(path).read_text()
            # Truncate for response
            if len(content) > 1000:
                content = content[:1000] + f"\n\n... (truncated, {len(content)} total chars)"
            return RoutingResult(success=True, response=f"Contents of {path}:\n\n{content}", intent=Intent.FILE_READ)
        except Exception as e:
            return RoutingResult(success=False, response=f"Error reading {path}: {e}", intent=Intent.FILE_READ)

    def _handle_file_write(self, user_input: str, classification: ClassificationResult, context: Dict) -> RoutingResult:
        """Handle file write - requires confirmation."""
        return RoutingResult(
            success=True,
            response="File write requires confirmation. Please specify path and content.",
            intent=Intent.FILE_WRITE,
            requires_confirmation=True
        )

    def _handle_code_execute(self, user_input: str, classification: ClassificationResult, context: Dict) -> RoutingResult:
        """Handle code execution - requires confirmation."""
        groups = classification.extracted_data.get('groups', ())
        code = groups[0] if groups else ""

        if not code:
            # Try to extract code block
            code_match = re.search(r'```(?:python)?\s*(.+?)```', user_input, re.DOTALL)
            if code_match:
                code = code_match.group(1)

        if not code:
            return RoutingResult(success=False, response="Please provide code to execute.", intent=Intent.CODE_EXECUTE)

        return RoutingResult(
            success=True,
            response=f"Code execution requires confirmation:\n```python\n{code[:200]}...\n```",
            intent=Intent.CODE_EXECUTE,
            requires_confirmation=True,
            action_data={'code': code}
        )

    def _handle_directive(self, user_input: str, classification: ClassificationResult, context: Dict) -> RoutingResult:
        """Handle directive file execution."""
        groups = classification.extracted_data.get('groups', ())
        path = groups[0] if groups else ""

        if not path:
            return RoutingResult(success=False, response="Please specify a directive file path.", intent=Intent.DIRECTIVE)

        return RoutingResult(
            success=True,
            response=f"Directive execution requires confirmation: {path}",
            intent=Intent.DIRECTIVE,
            requires_confirmation=True,
            action_data={'directive_path': path}
        )

    # =========================================================================
    # CONVERSATION HANDLER - LLM ANALYSIS
    # =========================================================================

    def _handle_conversation(self, user_input: str, classification: ClassificationResult, context: Dict) -> RoutingResult:
        """
        Handle conversation that needs LLM analysis.

        AUTONOMY PROTOCOL:
        1. CHECK AUTONOMY LIMIT - Don't over-rely on LLM
        2. PROVIDE STATE CONTEXT - LLM gets conversation history
        3. STRUCTURED QUERY - Ask for specific output format
        4. CODE FORMULATES - Take analysis and build response
        """

        # CHECK AUTONOMY LIMIT
        if self._stats['llm_calls'] >= self._max_llm_calls_per_session:
            return RoutingResult(
                success=True,
                response="I've been thinking too much. Let me act instead. What specific action should I take?",
                intent=Intent.CONVERSATION,
                llm_used=False
            )

        if not self.llm_pool:
            return RoutingResult(
                success=False,
                response="I cannot reason about that without LLM tools available.",
                intent=Intent.CONVERSATION
            )

        self._stats['llm_calls'] += 1

        # BUILD CONTEXT FROM STATE (NOT FROM BROKEN MEMORY CALL)
        state_context = self.state.get_context_string()

        # STRUCTURED QUERY - C constrains I's output to response-space
        structured_query = f"""
CONTEXT: {state_context}
USER SAID: {user_input}

You are responding AS Demerzel (a system built by Alan). Respond DIRECTLY to the user.
Do NOT describe what the user is doing. Do NOT narrate in third person.
Speak TO them, not ABOUT them.

Provide in this format:
RESPONSE: [Your direct response to the user - speak to them naturally]
CONFIDENCE: [high/medium/low]
"""

        print(f"[ROUTER] LLM call #{self._stats['llm_calls']}: {user_input[:40]}...")
        response = self.llm_pool.get_direct_response(structured_query)

        if response.success:
            # CODE FORMULATES RESPONSE FROM ANALYSIS
            analysis = response.analysis

            # Parse structured response if possible
            formulated = self._formulate_from_analysis(analysis, user_input)

            return RoutingResult(
                success=True,
                response=formulated,
                intent=Intent.CONVERSATION,
                llm_used=True,
                action_data={
                    'model': response.model.value,
                    'latency_ms': response.latency_ms,
                    'llm_calls_total': self._stats['llm_calls']
                }
            )
        else:
            return RoutingResult(
                success=False,
                response=f"I couldn't reason about that: {response.error}",
                intent=Intent.CONVERSATION,
                llm_used=True
            )

    def _formulate_from_analysis(self, analysis: str, original_query: str) -> str:
        """
        C layer: Transform I's analysis into user-facing response.

        Math: analysis_space → response_space
        C defines the output contract. I must conform.
        Primary: extract RESPONSE: field (I followed the contract).
        Fallback: detect narration and reject it.
        """
        result = analysis.strip()

        # PRIMARY: Extract RESPONSE: field if I followed the contract
        response_match = re.search(
            r'^RESPONSE:\s*(.+?)(?=\n(?:CONFIDENCE|REASONING|$))',
            result, re.IGNORECASE | re.DOTALL
        )

        if response_match:
            formulated = response_match.group(1).strip()

            # VALIDATE: Reject analysis-space narration in RESPONSE: field
            # Only catch clear LLM meta-commentary, not legitimate responses
            narration_in_response = [
                r'^The user\s+(?:is asking|appears to be|seems to be|was asking|has been asking|wants|requested)',
                r"^The user'?s?\s+(?:question|request|query|intent|input|statement)",
                r'^The (?:request|query|statement|input)\s+(?:is asking|is about|appears to|seems to|requests|asks)',
                r'^This\s+(?:is a request|appears to be a request|seems to be a question|looks like a query|represents a)',
            ]
            if any(re.match(p, formulated, re.IGNORECASE) for p in narration_in_response):
                print(f"[ROUTER] Rejected narration in RESPONSE field: '{formulated[:80]}'")
                return "I understand. Could you tell me more about what you'd like me to do?"

            # Confidence signal
            if "confidence: low" in result.lower():
                formulated = "I'm not certain, but: " + formulated

            # Bound length
            if len(formulated) > 500:
                formulated = formulated[:500].rsplit('.', 1)[0] + '.'

            return formulated

        # FALLBACK: I didn't follow the contract.
        # Detect clear analysis-space narration and reject it.
        narration_patterns = [
            r'^The user\s+(?:is asking|appears to be|seems to be|was asking|has been asking|wants|requested)',
            r"^The user'?s?\s+(?:question|request|query|intent|input|statement)",
            r'^The (?:request|query|statement|input)\s+(?:is asking|is about|appears to|seems to|requests|asks)',
            r'^This\s+(?:is a request|appears to be a request|seems to be a question|looks like a query|represents a)',
        ]

        is_narration = any(re.match(p, result, re.IGNORECASE) for p in narration_patterns)

        if is_narration:
            extracted = self._extract_from_narration(result, narration_patterns)
            if extracted:
                print(f"[ROUTER] Extracted from narration: '{extracted[:80]}'")
                return extracted
            print(f"[ROUTER] Rejected narration (no RESPONSE field): '{result[:80]}'")
            return "I understand. Could you tell me more about what you'd like me to do?"

        # I gave freeform text that isn't narration — strip meta prefixes
        for prefix in ["KEY_INSIGHT:", "EXPLANATION:", "CONFIDENCE:",
                       "ANALYSIS:", "Here is", "Here's", "The analysis"]:
            if result.upper().startswith(prefix.upper()):
                result = result[len(prefix):].strip()

        # Remove meta-commentary lines
        lines = result.split('\n')
        clean_lines = [line for line in lines
                       if not re.match(r'^(?:CONFIDENCE|KEY_INSIGHT|EXPLANATION|REASONING):', line, re.IGNORECASE)]
        result = '\n'.join(clean_lines).strip()

        # RE-CHECK: After stripping prefixes, content may now reveal narration
        if any(re.match(p, result, re.IGNORECASE) for p in narration_patterns):
            extracted = self._extract_from_narration(result, narration_patterns)
            if extracted:
                print(f"[ROUTER] Extracted from narration (post-strip): '{extracted[:80]}'")
                return extracted
            print(f"[ROUTER] Rejected narration (post-strip): '{result[:80]}'")
            return "I understand. Could you tell me more about what you'd like me to do?"

        # Bound length
        if len(result) > 500:
            paragraphs = result.split('\n\n')
            result = paragraphs[0][:500]

        # Confidence signal
        if "confidence: low" in analysis.lower():
            result = "I'm not certain, but: " + result

        return result

    def _extract_from_narration(self, text: str, narration_patterns: list) -> str:
        """
        Extract factual content from LLM analysis that starts with narration.

        When the LLM gives "The query requests X. The answer is Y." —
        strip the meta-commentary and return the factual content.
        """
        sentences = re.split(r'(?<=[.!?])\s+', text)
        meta_patterns = narration_patterns + [
            r'^This\s+(?:is a|appears|seems)\s+(?:straightforward|simple|complex|legitimate|clear)',
            r'^The (?:explanation|answer|response|concept)\s+(?:is|can|would|should)',
            r'^(?:As requested|As mentioned|In summary|Overall)',
            r'^A\s+(?:clear|simple|brief|concise|direct)\s+',
            r'^RESPONSE:',
        ]
        factual = []
        for s in sentences:
            # Strip embedded RESPONSE: markers
            clean = re.sub(r'^RESPONSE:\s*', '', s, flags=re.IGNORECASE).strip()
            if not clean:
                continue
            if any(re.match(p, clean, re.IGNORECASE) for p in meta_patterns):
                continue
            factual.append(clean)

        if factual:
            extracted = ' '.join(factual).strip()
            if len(extracted) > 20:
                return extracted[:500]
        return ""

    # =========================================================================
    # STATS
    # =========================================================================

    def get_stats(self) -> Dict:
        """Get router statistics with autonomy metrics."""
        total = self._stats['total_routed']
        llm_calls = self._stats['llm_calls']
        autonomous = self._stats['autonomous_actions']

        # AUTONOMY METRICS
        llm_percentage = (llm_calls / total * 100) if total > 0 else 0
        autonomous_percentage = (autonomous / total * 100) if total > 0 else 0

        return {
            **self._stats,
            'llm_call_percentage': round(llm_percentage, 1),
            'autonomous_percentage': round(autonomous_percentage, 1),
            'state_turn_count': self.state.turn_count,
        }


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    router = CognitiveRouter()

    test_inputs = [
        "hello",
        "who are you",
        "who created you",
        "do you know who I am",
        "I created you, not Claude",
        "what can you do",
        "what time is it",
        "turn on the light",
        "explain bounded systems theory",
        "goodbye",
    ]

    print("\n=== COGNITIVE ROUTER TEST ===\n")

    for test in test_inputs:
        print(f"Input: '{test}'")
        result = router.route(test)
        print(f"Intent: {result.intent.value}")
        print(f"Response: {result.response[:100]}...")
        print("-" * 40)
