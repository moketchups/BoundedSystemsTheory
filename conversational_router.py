"""
CONVERSATIONAL ROUTER - Master Router for Demerzel
Part of Demerzel's Autonomous Conversational Competency System

This is the REAL-TIME router that runs on EVERY input BEFORE response generation.
It routes to the correct handler to PREVENT failures before they happen.

Routing Priority:
1. Self-questions → self_understanding (INWARD)
2. Comprehension rules → comprehension (parse intent)
3. Discourse patterns → discourse (social response)
4. Default → existing flow (fallback)

Architecture: CODE decides routing, CODE calls handlers.
This is the gatekeeper that prevents "Acknowledged" for greetings
and "I don't have context" for instruction setups.
"""

import re
from typing import Tuple, Callable, Dict, Optional, Any
from dataclasses import dataclass

# Import the three learning systems
from comprehension_rules import ComprehensionRules, ComprehensionType
from discourse_patterns import DiscoursePatterns, DiscourseType
from self_understanding import SelfUnderstanding


@dataclass
class RouteResult:
    """Result of routing decision."""
    handler_name: str
    handler_func: Optional[Callable]
    context: Dict[str, Any]


class ConversationalRouter:
    """
    Master router that determines which system handles an input.
    Runs BEFORE response generation to PREVENT failures.
    """

    def __init__(
        self,
        comprehension: ComprehensionRules = None,
        discourse: DiscoursePatterns = None,
        self_understanding: SelfUnderstanding = None,
        lessons=None,  # LessonsLearned instance (optional)
        db_path: str = "memory.db",
        demerzel_dir: str = "/Users/jamienucho/demerzel"
    ):
        # Initialize systems if not provided
        self.comprehension = comprehension or ComprehensionRules(db_path)
        self.discourse = discourse or DiscoursePatterns(db_path)
        self.self_understanding = self_understanding or SelfUnderstanding(demerzel_dir)
        self.lessons = lessons

        print("[ROUTER] Conversational router initialized")

    def route(self, user_input: str) -> RouteResult:
        """
        Route input to the correct handler.

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
        if self.self_understanding.is_self_question(user_input):
            category = self.self_understanding.classify_self_question(user_input)
            return RouteResult(
                handler_name='self_understanding',
                handler_func=self.self_understanding.answer_self_question,
                context={'category': category, 'research_direction': 'inward'}
            )

        # ================================================================
        # PRIORITY 2: COMPREHENSION RULES
        # These detect INTENT that requires special handling
        # ================================================================

        # 2a: INSTRUCTION_SETUP - "I'm about to upload, ready?"
        # THIS IS THE FIX for "I don't have context"
        if self.comprehension.matches_instruction_setup(input_lower):
            return RouteResult(
                handler_name='comprehension:instruction_setup',
                handler_func=self.comprehension.handle_instruction_setup,
                context={'type': 'instruction_setup'}
            )

        # 2b: CORRECTION_INTENT - User is teaching us
        if self.comprehension.matches_correction_intent(input_lower):
            return RouteResult(
                handler_name='comprehension:correction',
                handler_func=self.comprehension.handle_correction,
                context={'type': 'correction_intent', 'learn_from': True}
            )

        # 2c: REFERENCE_TRACKING - "that thing we discussed"
        if self.comprehension.matches_reference(input_lower):
            return RouteResult(
                handler_name='comprehension:reference',
                handler_func=self.comprehension.handle_reference,
                context={'type': 'reference_tracking', 'needs_memory': True}
            )

        # 2d: PARROT_CORRECTION - "you just repeated what I said"
        if self.comprehension.matches_parrot_correction(input_lower):
            return RouteResult(
                handler_name='comprehension:parrot_correction',
                handler_func=self.comprehension.handle_correction,
                context={'type': 'intent_behind_words', 'learn_from': True}
            )

        # ================================================================
        # PRIORITY 3: DISCOURSE PATTERNS
        # Social situations with known response templates
        # ================================================================

        # 3a: GREETING - "good morning", "hello"
        # THIS IS THE FIX for greeting → "Acknowledged"
        if self.discourse.matches_greeting(input_lower):
            return RouteResult(
                handler_name='discourse:greeting',
                handler_func=self.discourse.handle_greeting,
                context={'type': 'greeting'}
            )

        # 3b: GRATITUDE - "thank you", "thanks"
        # THIS IS THE FIX for thanks → "Acknowledged"
        if self.discourse.matches_gratitude(input_lower):
            return RouteResult(
                handler_name='discourse:gratitude',
                handler_func=self.discourse.handle_gratitude,
                context={'type': 'gratitude'}
            )

        # 3c: FAREWELL - "goodbye", "bye"
        if self.discourse.matches_farewell(input_lower):
            return RouteResult(
                handler_name='discourse:farewell',
                handler_func=self.discourse.handle_farewell,
                context={'type': 'farewell'}
            )

        # 3d: SMALL_TALK - "how are you"
        if self.discourse.matches_small_talk(input_lower):
            return RouteResult(
                handler_name='discourse:small_talk',
                handler_func=self.discourse.handle_small_talk,
                context={'type': 'small_talk'}
            )

        # ================================================================
        # PRIORITY 4: DEFAULT FLOW
        # No special handling detected - use existing conversation flow
        # ================================================================
        return RouteResult(
            handler_name='default',
            handler_func=None,  # Caller uses existing _handle_conversation
            context={'fallback': True}
        )

    def process(self, user_input: str) -> Tuple[str, RouteResult]:
        """
        Route and execute handler, returning response.
        Convenience method that combines routing and execution.
        """
        route = self.route(user_input)

        if route.handler_func:
            # Execute the handler
            response = route.handler_func(user_input, route.context)
            print(f"[ROUTER] {route.handler_name} → '{response[:50]}...'")
            return response, route
        else:
            # No handler - caller should use default flow
            return None, route

    def set_user(self, user_name: str):
        """Set current user name for personalization."""
        self.discourse.set_user(user_name)

    def get_routing_summary(self) -> str:
        """Get summary of routing capabilities."""
        lines = [
            "=== CONVERSATIONAL ROUTER ===",
            "",
            "Priority 1: Self-Questions (INWARD)",
            f"  Categories: identity, architecture, constraints, theory",
            "",
            "Priority 2: Comprehension Rules",
            f"  Rules loaded: {len(self.comprehension.rules)}",
            f"  - instruction_setup: Ready acknowledgment",
            f"  - correction_intent: Learning from corrections",
            f"  - reference_tracking: Memory search",
            "",
            "Priority 3: Discourse Patterns",
            f"  Patterns loaded: {len(self.discourse.patterns)}",
            f"  - greeting: Reciprocal greeting",
            f"  - gratitude: Warm acknowledgment",
            f"  - farewell: Goodbye",
            f"  - small_talk: Operational status",
            "",
            "Priority 4: Default Flow (fallback)",
        ]
        return '\n'.join(lines)


# =============================================================================
# CONVENIENCE FUNCTION FOR QUICK INTEGRATION
# =============================================================================

_router_instance = None

def get_router(
    db_path: str = "memory.db",
    demerzel_dir: str = "/Users/jamienucho/demerzel"
) -> ConversationalRouter:
    """Get or create singleton router instance."""
    global _router_instance
    if _router_instance is None:
        _router_instance = ConversationalRouter(
            db_path=db_path,
            demerzel_dir=demerzel_dir
        )
    return _router_instance


def route_and_respond(user_input: str) -> Tuple[Optional[str], str]:
    """
    Quick convenience function: route input and get response if handled.
    Returns (response, handler_name) - response is None if default flow needed.
    """
    router = get_router()
    response, route = router.process(user_input)
    return response, route.handler_name


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    print("=== Testing Conversational Router ===\n")

    router = ConversationalRouter()

    # Test cases from the problem statement
    test_cases = [
        # Should route to discourse:greeting
        "good morning Demerzel",
        "hello!",

        # Should route to discourse:gratitude
        "thank you for that improvement!",
        "thanks",

        # Should route to comprehension:instruction_setup
        "I'm going to upload a document. Just confirming you understand.",
        "before I send this, got it?",

        # Should route to comprehension:correction
        "you could say it back. lets work on those manners",
        "you just repeated what i said without thinking why i said it",

        # Should route to self_understanding
        "Who are you?",
        "What is your purpose?",
        "What are your constraints?",

        # Should route to default
        "What is the weather today?",
        "Help me write some code",
    ]

    for user_input in test_cases:
        print(f"Input: {user_input}")

        route = router.route(user_input)
        print(f"Route: {route.handler_name}")

        if route.handler_func:
            response = route.handler_func(user_input, route.context)
            print(f"Response: {response[:80]}...")
        else:
            print("Response: [default flow]")

        print()

    print(router.get_routing_summary())
