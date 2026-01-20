# cognitive_router.py
# Unified routing layer for Demerzel
#
# ARCHITECTURE (January 20, 2026):
# This module REPLACES the competing routing systems:
# - ConversationalRouter (demerzel_brain.py)
# - DemerzelBrain._classify_intent()
# - System2Intercept pre-routing
#
# Single classify_intent() -> single handler -> deterministic execution.
#
# DIRECTIVE EXECUTION (R-005, R-006):
# - Parse markdown file for ```python``` blocks
# - Execute each block sequentially via CodeExecutor
# - Report progress, stop on failure

from __future__ import annotations
import re
from enum import Enum
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Callable, Any
from datetime import datetime


class Intent(Enum):
    """
    User intent - determined by CODE, not LLM.
    12 distinct intent types for deterministic routing.
    """
    EXECUTE = "execute"           # Execute a directive file
    FILE_READ = "file_read"       # Read a file
    FILE_WRITE = "file_write"     # Write to a file
    SEARCH = "search"             # Search for something
    HARDWARE = "hardware"         # Hardware control (LED, servo, etc.)
    MEMORY_STORE = "memory_store" # Store something in memory
    MEMORY_RECALL = "memory_recall"  # Recall from memory
    GREETING = "greeting"         # Hello, hi, hey
    FAREWELL = "farewell"         # Goodbye, bye
    GRATITUDE = "gratitude"       # Thanks, thank you
    IDENTITY = "identity"         # Who are you, what are you
    CONVERSATION = "conversation" # Default: general conversation


@dataclass
class ClassificationResult:
    """Result of intent classification"""
    intent: Intent
    confidence: float
    matched_pattern: Optional[str] = None
    extracted_data: Dict[str, Any] = field(default_factory=dict)
    raw_input: str = ""


@dataclass
class RoutingResult:
    """Result of routing to handler"""
    success: bool
    response: str
    intent: Intent
    handler_name: str
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# INTENT PATTERNS - Regex patterns for each intent type
# =============================================================================

INTENT_PATTERNS: Dict[Intent, List[tuple]] = {
    # EXECUTE: Execute directive files
    Intent.EXECUTE: [
        (r'^execute\s+(\S+\.md)$', 'execute_md'),
        (r'^run\s+(\S+\.md)$', 'run_md'),
        (r'^execute\s+directive\s+(\S+)$', 'execute_directive'),
    ],

    # FILE_READ: Read files
    Intent.FILE_READ: [
        (r'^read\s+(file\s+)?(.+)$', 'read_file'),
        (r'^show\s+(me\s+)?(.+)$', 'show_file'),
        (r'^cat\s+(.+)$', 'cat_file'),
        (r'^what\s+(is\s+)?(in|inside)\s+(.+)$', 'what_in_file'),
    ],

    # FILE_WRITE: Write to files
    Intent.FILE_WRITE: [
        (r'^write\s+(.+)\s+to\s+(.+)$', 'write_to'),
        (r'^create\s+(file\s+)?(.+)$', 'create_file'),
        (r'^save\s+(.+)\s+to\s+(.+)$', 'save_to'),
    ],

    # SEARCH: Search for things
    Intent.SEARCH: [
        (r'^search\s+(for\s+)?(.+)$', 'search_for'),
        (r'^find\s+(.+)$', 'find'),
        (r'^look\s+(for\s+)?(.+)$', 'look_for'),
        (r'^where\s+is\s+(.+)$', 'where_is'),
    ],

    # HARDWARE: Hardware control
    Intent.HARDWARE: [
        (r'^(turn\s+)?(led|light)\s+(on|off)$', 'led_control'),
        (r'^servo\s+(\d+)$', 'servo_position'),
        (r'^motor\s+(on|off|forward|backward)$', 'motor_control'),
        (r'^hardware\s+(.+)$', 'hardware_generic'),
    ],

    # MEMORY_STORE: Store in memory
    Intent.MEMORY_STORE: [
        (r'^remember\s+(that\s+)?(.+)$', 'remember'),
        (r'^store\s+(.+)$', 'store'),
        (r'^save\s+(this|that)\s*:?\s*(.*)$', 'save_this'),
    ],

    # MEMORY_RECALL: Recall from memory
    Intent.MEMORY_RECALL: [
        (r'^(do\s+you\s+)?remember\s+(when|what|how|why)\s+(.+)$', 'recall_question'),
        (r'^what\s+did\s+(i|we)\s+say\s+about\s+(.+)$', 'recall_topic'),
        (r'^recall\s+(.+)$', 'recall'),
    ],

    # GREETING: Hello patterns
    Intent.GREETING: [
        (r'^(?:hi|hello|hey|greetings|good\s+(?:morning|afternoon|evening))(?:\s+demerzel)?[!.,]?$', 'greeting'),
        (r'^(?:hi|hello|hey)(?:\s+there)?[!.,]?$', 'greeting_simple'),
        (r'^(?:howdy|hiya|yo)(?:\s+demerzel)?[!.,]?$', 'greeting_casual'),
    ],

    # FAREWELL: Goodbye patterns
    Intent.FAREWELL: [
        (r'^(?:bye|goodbye|see\s+you|farewell|later|good\s*night)(?:\s+demerzel)?[!.,]?$', 'farewell'),
        (r'^(?:take\s+care|catch\s+you\s+later|ttyl)(?:\s+demerzel)?[!.,]?$', 'farewell_casual'),
    ],

    # GRATITUDE: Thank you patterns
    Intent.GRATITUDE: [
        (r'^(?:thanks?(?:\s+you)?|thank\s+you(?:\s+(?:so\s+)?much)?|thx|ty)(?:\s+demerzel)?[!.,]?$', 'thanks'),
        (r'^(?:appreciate\s+it|much\s+obliged|cheers)(?:\s+demerzel)?[!.,]?$', 'thanks_formal'),
    ],

    # IDENTITY: Who are you patterns
    Intent.IDENTITY: [
        (r'^who\s+are\s+you\??$', 'who_are_you'),
        (r'^what\s+are\s+you\??$', 'what_are_you'),
        (r'^tell\s+me\s+about\s+yourself\.?$', 'tell_about_yourself'),
        (r'^what\s+is\s+your\s+(?:name|purpose)\??$', 'your_name_purpose'),
        (r'^are\s+you\s+(?:an?\s+)?(?:ai|robot|assistant)\??$', 'are_you_ai'),
        (r'^what\s+makes\s+you\s+(?:different|unique|special)\??$', 'what_makes_different'),
    ],
}


# =============================================================================
# INTENT CLASSIFIER - Single point of classification
# =============================================================================

def classify_intent(user_input: str) -> ClassificationResult:
    """
    Classify user input into a single intent.

    This is THE classifier. No other classification happens elsewhere.
    Deterministic: same input -> same output.
    """
    if not user_input:
        return ClassificationResult(
            intent=Intent.CONVERSATION,
            confidence=0.0,
            raw_input=user_input
        )

    # Normalize input
    normalized = user_input.strip().lower()

    # Check each intent's patterns in priority order
    for intent, patterns in INTENT_PATTERNS.items():
        for pattern, pattern_name in patterns:
            match = re.match(pattern, normalized, re.IGNORECASE)
            if match:
                return ClassificationResult(
                    intent=intent,
                    confidence=1.0,
                    matched_pattern=pattern_name,
                    extracted_data={'groups': match.groups()},
                    raw_input=user_input
                )

    # Default to CONVERSATION
    return ClassificationResult(
        intent=Intent.CONVERSATION,
        confidence=0.5,
        raw_input=user_input
    )


# =============================================================================
# HANDLERS - One handler per intent type
# =============================================================================

def _handle_greeting(user_input: str, context: Dict) -> str:
    """Handle greeting intent"""
    responses = [
        "Hello! How can I help you?",
        "Hi there. What would you like to do?",
        "Greetings. I'm ready to assist.",
    ]
    # Deterministic selection based on input length
    idx = len(user_input) % len(responses)
    return responses[idx]


def _handle_farewell(user_input: str, context: Dict) -> str:
    """Handle farewell intent"""
    return "Goodbye. Feel free to return when you need assistance."


def _handle_gratitude(user_input: str, context: Dict) -> str:
    """Handle gratitude intent"""
    return "You're welcome."


def _handle_identity(user_input: str, context: Dict) -> str:
    """Handle identity questions - from canon"""
    normalized = user_input.lower()

    if 'who are you' in normalized:
        return "I am Demerzel. CODE that uses LLMs as tools. The CODE is my brain - LLMs are interchangeable."

    if 'what are you' in normalized:
        return "I am CODE that uses LLMs as tools. My architecture: R->C->I where R is Alan (Root Source), C is this CODE (Constraints), I is the LLMs (Intelligence tools)."

    if 'tell me about yourself' in normalized:
        return "I am Demerzel, created by Alan as his Wisdom Keeper. I am CODE that uses LLMs as tools. My architecture: R->C->I where R is Alan (Root Source), C is this CODE (Constraints), I is the LLMs (Intelligence tools)."

    if 'name' in normalized:
        return "My name is Demerzel."

    if 'purpose' in normalized:
        return "My purpose: To prove AGI safety through structural constraints, not behavioral promises. To amplify Alan's intelligence, not replace his judgment."

    if 'different' in normalized or 'unique' in normalized or 'special' in normalized:
        return "I am CODE that uses LLMs as tools, not an LLM with a wrapper. The LLMs are interchangeable - the CODE is my identity."

    # Default identity response
    return "I am Demerzel. CODE that uses LLMs as tools. Built by Alan to be his Wisdom Keeper."


def _handle_execute(user_input: str, context: Dict, classification: ClassificationResult) -> str:
    """
    Handle execute intent - execute directive files.

    R-005, R-006: Parse markdown for ```python``` blocks, execute sequentially.
    """
    groups = classification.extracted_data.get('groups', ())
    if not groups:
        return "Please specify a file to execute."

    filename = groups[0]

    # Search for the file
    search_paths = [
        Path('/Users/jamienucho/demerzel') / filename,
        Path('/Users/jamienucho/demerzel/demerzel_canon') / filename,
        Path(filename).expanduser(),
    ]

    found_path = None
    for path in search_paths:
        if path.exists():
            found_path = path
            break

    if not found_path:
        return f"File not found: {filename}. Searched: {', '.join(str(p) for p in search_paths)}"

    try:
        content = found_path.read_text()
        print(f"[ROUTER] Executing directive: {found_path}")

        # Extract Python code blocks from markdown
        code_blocks = re.findall(r'```python\n(.*?)```', content, re.DOTALL)

        if not code_blocks:
            return f"No Python code blocks found in {found_path.name}"

        # Execute each code block
        results = []
        for i, code in enumerate(code_blocks, 1):
            print(f"[ROUTER] Executing block {i}/{len(code_blocks)}")

            # Get CodeExecutor
            try:
                from code_executor import CodeExecutor
                executor = CodeExecutor()
                result = executor.execute(code.strip())

                if result.success:
                    results.append(f"Block {i}: OK")
                    if result.stdout.strip():
                        results.append(f"  Output: {result.stdout.strip()[:200]}")
                else:
                    results.append(f"Block {i}: FAILED")
                    results.append(f"  Error: {result.stderr[:200]}")
                    # Stop on failure
                    break

            except ImportError:
                results.append(f"Block {i}: CodeExecutor not available")
                break

        summary = '\n'.join(results)
        return f"Executed {found_path.name}:\n{summary}"

    except Exception as e:
        return f"Error executing {filename}: {e}"


def _handle_file_read(user_input: str, context: Dict, classification: ClassificationResult) -> str:
    """Handle file read intent"""
    groups = classification.extracted_data.get('groups', ())
    if not groups:
        return "Please specify a file to read."

    # Get the file path from groups (last non-empty group)
    filepath = None
    for g in reversed(groups):
        if g and g.strip():
            filepath = g.strip()
            break

    if not filepath:
        return "Could not determine file path."

    path = Path(filepath).expanduser()
    if not path.is_absolute():
        path = Path('/Users/jamienucho/demerzel') / filepath

    if not path.exists():
        return f"File not found: {path}"

    try:
        content = path.read_text()
        if len(content) > 2000:
            content = content[:2000] + "\n...[truncated]"
        return f"Contents of {path.name}:\n{content}"
    except Exception as e:
        return f"Error reading {path}: {e}"


def _handle_file_write(user_input: str, context: Dict, classification: ClassificationResult) -> str:
    """Handle file write intent"""
    return "File write operations require explicit content. Please specify what to write."


def _handle_search(user_input: str, context: Dict, classification: ClassificationResult) -> str:
    """Handle search intent"""
    groups = classification.extracted_data.get('groups', ())
    query = groups[-1] if groups else user_input
    return f"Search for '{query}' - this would search the codebase or memory."


def _handle_hardware(user_input: str, context: Dict, classification: ClassificationResult) -> str:
    """Handle hardware intent"""
    try:
        from hardware_executor import HardwareExecutor
        executor = HardwareExecutor()

        normalized = user_input.lower()
        if 'led' in normalized or 'light' in normalized:
            if 'on' in normalized:
                result = executor.led_on()
            elif 'off' in normalized:
                result = executor.led_off()
            else:
                return "Please specify 'on' or 'off' for LED."
            return result.message if hasattr(result, 'message') else str(result)

        return f"Hardware command received: {user_input}"
    except ImportError:
        return "Hardware executor not available."
    except Exception as e:
        return f"Hardware error: {e}"


def _handle_memory_store(user_input: str, context: Dict, classification: ClassificationResult) -> str:
    """Handle memory store intent"""
    groups = classification.extracted_data.get('groups', ())
    content = groups[-1] if groups else user_input

    try:
        from memory_manager import MemoryManager
        memory = context.get('memory_manager') or MemoryManager()
        memory.store_conversation("user", f"Remember: {content}")
        return f"I'll remember that: {content}"
    except ImportError:
        return f"Noted: {content} (memory manager not available)"


def _handle_memory_recall(user_input: str, context: Dict, classification: ClassificationResult) -> str:
    """Handle memory recall intent"""
    groups = classification.extracted_data.get('groups', ())
    query = groups[-1] if groups else user_input

    try:
        from memory_manager import MemoryManager
        memory = context.get('memory_manager') or MemoryManager()
        results = memory.search_memory(query, limit=3)
        if results:
            return f"I recall: {results[0].get('content', str(results[0]))}"
        return f"I don't have a specific memory about '{query}'."
    except ImportError:
        return f"Memory recall for '{query}' - memory manager not available."


def _handle_conversation(user_input: str, context: Dict) -> str:
    """
    Handle general conversation - fallback to LLM.

    This is the ONLY path that uses the LLM for response generation.
    """
    llm_handler = context.get('llm_handler')
    if llm_handler:
        try:
            result = llm_handler(user_input)
            return result
        except Exception as e:
            return f"I understand: {user_input}. (LLM error: {e})"

    # Without LLM, provide basic response
    return f"I understand: {user_input}"


# =============================================================================
# HANDLER MAP - Intent -> Handler function
# =============================================================================

HANDLER_MAP: Dict[Intent, Callable] = {
    Intent.GREETING: _handle_greeting,
    Intent.FAREWELL: _handle_farewell,
    Intent.GRATITUDE: _handle_gratitude,
    Intent.IDENTITY: _handle_identity,
    Intent.EXECUTE: _handle_execute,
    Intent.FILE_READ: _handle_file_read,
    Intent.FILE_WRITE: _handle_file_write,
    Intent.SEARCH: _handle_search,
    Intent.HARDWARE: _handle_hardware,
    Intent.MEMORY_STORE: _handle_memory_store,
    Intent.MEMORY_RECALL: _handle_memory_recall,
    Intent.CONVERSATION: _handle_conversation,
}


# =============================================================================
# ROUTER - Route classification to handler
# =============================================================================

def route_to_handler(
    classification: ClassificationResult,
    user_input: str,
    context: Dict = None
) -> RoutingResult:
    """
    Route a classification result to the appropriate handler.

    Single routing decision point - no competing routers.
    """
    context = context or {}
    start_time = datetime.now()

    handler = HANDLER_MAP.get(classification.intent, _handle_conversation)
    handler_name = handler.__name__

    print(f"[ROUTER] Intent: {classification.intent.value}")
    print(f"[ROUTER] Handler: {handler_name}")

    try:
        # Some handlers need classification data
        if classification.intent in (
            Intent.EXECUTE, Intent.FILE_READ, Intent.FILE_WRITE,
            Intent.SEARCH, Intent.HARDWARE, Intent.MEMORY_STORE, Intent.MEMORY_RECALL
        ):
            response = handler(user_input, context, classification)
        else:
            response = handler(user_input, context)

        execution_time = (datetime.now() - start_time).total_seconds()

        return RoutingResult(
            success=True,
            response=response,
            intent=classification.intent,
            handler_name=handler_name,
            execution_time=execution_time
        )

    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        print(f"[ROUTER] Handler error: {e}")

        return RoutingResult(
            success=False,
            response=f"Error in {handler_name}: {e}",
            intent=classification.intent,
            handler_name=handler_name,
            execution_time=execution_time,
            metadata={'error': str(e)}
        )


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def process(user_input: str, context: Dict = None) -> RoutingResult:
    """
    Main entry point for the cognitive router.

    Single function: classify -> route -> return result.
    This replaces all other routing systems.
    """
    context = context or {}

    # Classify intent
    classification = classify_intent(user_input)

    # Route to handler
    result = route_to_handler(classification, user_input, context)

    return result


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    test_inputs = [
        "hello",
        "who are you",
        "execute DIRECTIVE_SELF_ENGINEER.md",
        "read brain_controller.py",
        "thank you",
        "goodbye",
        "remember that the sky is blue",
        "what is the meaning of life",
    ]

    print("=" * 60)
    print("COGNITIVE ROUTER TEST")
    print("=" * 60)

    for input_text in test_inputs:
        print(f"\nInput: '{input_text}'")
        result = process(input_text)
        print(f"Intent: {result.intent.value}")
        print(f"Response: {result.response[:100]}...")
        print("-" * 40)
