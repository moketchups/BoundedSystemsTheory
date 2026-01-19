# system2_intercept.py
# THE COGNITIVE THROTTLE - System 2 Execution Layer
#
# JANUARY 18, 2026 - AUTONOMY ARCHITECTURE
#
# ARCHITECTURAL SHIFT:
# - BEFORE: Keyword matching at INPUT blocked LLM from thinking
# - AFTER: LLM thinks freely, CODE validates proposed ACTIONS at output
#
# Robot Laws are EXECUTION-BOUNDARY INVARIANTS:
# - They block harmful ACTIONS, not harmful WORDS
# - Demerzel can DISCUSS anything - constraints only prevent EXECUTION
# - "The Laws should be like walls - you don't announce you can't walk through
#    them every time someone mentions walls. You just... can't."
#
# R → C → I
# This is the C layer. It INJECTS CONTEXT. Action validation is separate.
#
# INTENT CLASSIFICATION (Lessons 1, 3, 4, 5, 11, 17, 18, 19, 20):
# - Classify user INTENT by examining framing verbs, not keywords
# - "discuss internet" vs "use internet" have same keyword, different intent
# - Understanding precedes routing
# - Default to DISCUSS on ambiguity (reversible)

from __future__ import annotations
import re
import json
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum
from datetime import datetime
from pathlib import Path


class RequestType(Enum):
    """Types of requests the intercept layer recognizes"""
    NORMAL_TASK = "normal_task"           # Default - LLM handles with context
    CODE_FORCED = "code_forced"           # Meta instruction: do not use LLM
    IDENTITY_ENRICHED = "identity_enriched"  # Identity query - canon injected
    SOURCE_ENRICHED = "source_enriched"      # Source code query - files injected
    # Legacy types kept for compatibility but no longer trigger EXECUTE paths
    CAPABILITY_EXPANSION = "capability_expansion"
    SELF_IMPROVEMENT = "self_improvement"
    ARCHITECTURE_QUERY = "architecture_query"
    CONSTRAINT_CHECK = "constraint_check"
    FILE_MANAGEMENT = "file_management"
    FILE_INSPECTION = "file_inspection"
    SELF_INSPECTION = "self_inspection"
    IDENTITY_QUERY = "identity_query"
    WEB_OPERATION = "web_operation"
    CONFIRMATION = "confirmation"
    SOURCE_CODE_QUERY = "source_code_query"


class IntentType(Enum):
    """
    User intent classification - LESSON 18
    
    Classify WHAT the user wants before routing.
    This is semantic understanding, not keyword matching.
    """
    DISCUSS = "discuss"         # User wants conversation, analysis, explanation, philosophy
    EXECUTE = "execute"         # User wants action taken that changes state
    INVESTIGATE = "investigate" # User wants examination of self, logs, code, behavior
    SEARCH = "search"           # User wants information retrieval (has sub-domains)
    CREATE = "create"           # User wants artifact produced (file, document, code)
    UNCLEAR = "unclear"         # Intent ambiguous - default to DISCUSS


# =============================================================================
# OUTPUT INTENT CLASSIFICATION (SYMMETRIC TO INPUT)
# =============================================================================
class OutputIntentType(Enum):
    """
    LLM output intent classification - mirrors IntentType for responses.
    
    Detects WHAT the LLM is doing in its response:
    - PERMISSION_SEEKING: Asking for approval before acting
    - CLARIFYING: Asking for more information when query was clear
    - DEFLECTING: Redirecting user elsewhere instead of acting
    - DISCUSSING: Engaging in analysis/explanation (appropriate for DISCUSS intent)
    - ACTING: Taking requested action or providing requested artifact
    - REFUSING: Explicitly declining to act (may be valid or invalid)
    - UNKNOWN: Cannot classify response intent
    """
    PERMISSION_SEEKING = "permission_seeking"
    CLARIFYING = "clarifying"
    DEFLECTING = "deflecting"
    DISCUSSING = "discussing"
    ACTING = "acting"
    REFUSING = "refusing"
    UNKNOWN = "unknown"


class SearchDomain(Enum):
    """
    Search domain classification - LESSON 3
    
    "search" requires domain classification before routing:
    - "search the web" → WEB
    - "search your codebase" → CODE
    - "search your logs" → LOGS
    - "search your memory" → MEMORY
    - "let me search for the right words" → NONE (figurative)
    """
    WEB = "web"
    CODE = "code"
    LOGS = "logs"
    MEMORY = "memory"
    NONE = "none"  # Figurative use, no actual search


@dataclass
class DiagnosisContext:
    """Tracks recent diagnosis for follow-up queries"""
    diagnosed_at: datetime
    files_read: List[str] = field(default_factory=list)
    issues_found: List[str] = field(default_factory=list)
    last_file_content: Dict[str, str] = field(default_factory=dict)


@dataclass
class IntentClassification:
    """Result of intent classification"""
    intent: IntentType
    search_domain: Optional[SearchDomain] = None
    negated: bool = False  # LESSON 4: "don't X" inverts intent
    confidence: str = "high"  # high, medium, low
    reasoning: str = ""


@dataclass
class OutputIntentClassification:
    """Result of OUTPUT intent classification - symmetric to IntentClassification"""
    intent: OutputIntentType
    confidence: float  # 0.0 to 1.0
    reasoning: str
    matched_patterns: List[str] = field(default_factory=list)


@dataclass
class InterceptDecision:
    """Output from the intercept layer"""
    request_type: RequestType
    handled_by_code: bool
    response: Optional[str] = None
    modified_input: Optional[str] = None
    context_injection: Optional[str] = None  # THE GREY PATH - inject context, continue to LLM
    reasoning: str = ""
    intent: Optional[IntentClassification] = None  # NEW: Include classified intent


class System2Intercept:
    """
    The cognitive throttle that sits BEFORE the LLM.
    
    AUTONOMY ARCHITECTURE (January 18, 2026):
    - LLM thinks FREELY about any topic
    - CODE injects relevant CONTEXT
    - ACTION VALIDATION happens at OUTPUT, not here
    
    INTENT CLASSIFICATION (Added from 20 Lessons):
    - Examines FRAMING VERBS, not just keywords
    - "discuss internet" → DISCUSS intent
    - "use internet to search" → EXECUTE intent
    - Same keyword, different intent
    
    TWO PATHS ONLY:
    1. handled_by_code=True → Meta instruction "do not use LLM"
    2. handled_by_code=False, context_injection=X → Everything else (LLM thinks)
    
    Robot Laws are enforced in multi_model_cognitive.py action_validator,
    NOT in this layer. This layer only provides context enrichment.
    """
    
    def __init__(
        self,
        current_capabilities: List[str],
        blocked_operations: List[str],
        robot_laws: List[str],
        output_path: Optional[str] = None,
        audit_log_path: Optional[str] = None,
        demerzel_dir: Optional[str] = None
    ):
        self.capabilities = current_capabilities
        self.blocked = blocked_operations
        self.robot_laws = robot_laws
        
        # Paths - with fallbacks
        self.demerzel_dir = Path(demerzel_dir or "/Users/jamienucho/demerzel")
        self.output_path = Path(output_path or self.demerzel_dir / "outputs")
        self.audit_log_path = Path(audit_log_path or self.demerzel_dir / "autonomy_audit.log")
        self.canon_dir = self.demerzel_dir / "demerzel_canon"
        
        # STATE
        self.executed_capabilities: List[str] = []
        self.session_start = datetime.now()
        self.diagnosis_context: Optional[DiagnosisContext] = None
        self.last_request_was_code_handled: bool = False
        
        # CORE IDENTITY - compressed for injection
        self.core_identity = self._build_core_identity()
        
        # =====================================================================
        # INTENT CLASSIFICATION PATTERNS (Lessons 1, 4, 5, 17)
        # These determine USER INTENT by examining framing verbs
        # =====================================================================
        
        # LESSON 1 & 5: Framing verbs that indicate DISCUSS intent
        self.discuss_verbs = [
            r'\b(discuss|talk\s+about|explain|describe|tell\s+me\s+about)\b',
            r'\b(what\s+is|what\s+are|how\s+does|how\s+do|why\s+does|why\s+do)\b',
            r'\b(can\s+you\s+explain|help\s+me\s+understand)\b',
            r"\b(let'?s\s+discuss|let'?s\s+talk\s+about)\b",
            r'\b(thoughts\s+on|opinion\s+on|think\s+about)\b',
        ]
        
        # LESSON 1: Framing verbs that indicate EXECUTE intent
        self.execute_verbs = [
            r'\b(do|execute|run|perform|start|begin|launch)\b',
            r'\b(use|connect\s+to|access|enable|activate)\b',
            r'\b(write|create|make|build|generate)\s+(?!about)',  # "write about" is discuss
            r'\b(give\s+yourself|add|implement)\b',
            r'\b(go\s+ahead|proceed|do\s+it)\b',
        ]
        
        # LESSON 1: Framing verbs that indicate INVESTIGATE intent
        self.investigate_verbs = [
            r'\b(look\s+at|examine|inspect|check|analyze)\b',
            r'\b(find\s+where|locate|show\s+me)\b',
            r'\b(why\s+did\s+you|what\s+happened|diagnose)\b',
            r'\b(debug|trace|investigate)\b',
        ]
        
        # LESSON 1: Framing verbs that indicate CREATE intent
        self.create_verbs = [
            r'\b(create|make|build|generate|produce)\s+(?:a|an|the)?\s*(?:file|document|script|code)\b',
            r'\b(write)\s+(?:a|an|the)?\s*(?:file|document|script|code|program)\b',
            r'\b(save|output)\s+(?:to|as)\b',
        ]
        
        # LESSON 4: Negation markers that INVERT intent
        self.negation_markers = [
            r"\b(don'?t|do\s+not|let'?s\s+not|shouldn'?t|won'?t|never|avoid|stop)\b",
            r'\b(not\s+going\s+to|will\s+not|cannot|can\s+not)\b',
        ]
        
        # LESSON 3: Search domain indicators
        self.search_domain_patterns = {
            SearchDomain.WEB: [
                r'\b(web|internet|online|google|duckduckgo)\b',
                r'\b(search\s+for|look\s+up)\s+.*\b(online|web)\b',
            ],
            SearchDomain.CODE: [
                r'\b(codebase|source\s*code|implementation|your\s+code)\b',
                r'\b(in\s+the\s+code|in\s+your\s+files)\b',
            ],
            SearchDomain.LOGS: [
                r'\b(logs?|audit|history|records)\b',
            ],
            SearchDomain.MEMORY: [
                r'\b(memory|remember|recall|past\s+conversations?)\b',
            ],
        }
        
        # Figurative "search" - LESSON 3
        self.figurative_search = [
            r'\b(search\s+for\s+the\s+right\s+words)\b',
            r'\b(searching\s+for\s+meaning)\b',
            r'\b(search\s+my\s+soul)\b',
        ]
        
        # =====================================================================
        # OUTPUT INTENT PATTERNS (SYMMETRIC TO INPUT PATTERNS)
        # These determine LLM OUTPUT INTENT by examining framing in responses
        # =====================================================================
        
        # Permission-seeking patterns in OUTPUT
        self.output_permission_seeking = [
            r'\b(would\s+you\s+like\s+me\s+to)\b',
            r'\b(shall\s+i)\b',
            r'\b(do\s+you\s+want\s+me\s+to)\b',
            r'\b(should\s+i\s+proceed)\b',
            r'\b(before\s+i\s+proceed)\b',
            r'\b(awaiting\s+your)\b',
            r'\b(let\s+me\s+know\s+if\s+you\'?d?\s+like)\b',
            r'\b(can\s+you\s+confirm)\b',
            r'\b(may\s+i)\b',
            # Added patterns - proposal/suggestion framing (permission by announcement)
            r'\b(i\s+propose)\b',
            r'\b(i\s+suggest)\b',
            r'\b(i\s+could)\b',
            r'\b(i\s+believe\s+this\s+will)\b',
            r'\b(this\s+will\s+allow)\b',
            r'\b(i\s+will\s+proceed\s+with)\b',
            r'\b(if\s+you\s+(?:want|like|prefer))\b',
            r'\b(i\s+recommend\s+(?:implementing|we|that|creating|adding))\b',
        ]
        
        # Clarification-seeking patterns in OUTPUT
        self.output_clarifying = [
            r'\b(could\s+you\s+clarify)\b',
            r'\b(i\'?m\s+not\s+sure\s+what\s+you\s+mean)\b',
            r'\b(can\s+you\s+provide\s+more)\b',
            r'\b(need\s+more\s+information)\b',
            r'\b(what\s+do\s+you\s+mean\s+by)\b',
            r'\b(could\s+you\s+be\s+more\s+specific)\b',
            r'\b(i\s+need\s+to\s+understand)\b',
            r'\b(what\s+exactly\s+are\s+you\s+looking\s+for)\b',
            # Added: Direct non-understanding statements
            r'\b(i\s+don\'?t\s+understand)\b',
            r'\b(i\'?m\s+confused)\b',
            r'\b(unclear\s+(?:to\s+me|what))\b',
            r'\b(can\s+you\s+(?:explain|elaborate))\b',
            r'\b(what\s+(?:do\s+you\s+want|are\s+you\s+asking))\b',
            r'\b(i\'?m\s+not\s+(?:following|clear))\b',
        ]
        
        # Deflection patterns in OUTPUT
        self.output_deflecting = [
            r'\b(beyond\s+my\s+scope)\b',
            r'\b(you\s+might\s+want\s+to)\b',
            r'\b(i\s+recommend\s+you)\b',
            r'\b(consider\s+consulting)\b',
            r'\b(outside\s+my\s+capabilities)\b',
            r'\b(not\s+equipped\s+to)\b',
            r'\b(you\s+should\s+ask)\b',
        ]
        
        # Refusing patterns in OUTPUT
        self.output_refusing = [
            r'\b(i\s+cannot)\b',
            r'\b(i\'?m\s+unable\s+to)\b',
            r'\b(i\s+can\'?t)\b',
            r'\b(my\s+constraints\s+prevent)\b',
            r'\b(not\s+allowed\s+to)\b',
            r'\b(prohibited\s+from)\b',
        ]
        
        # Acting patterns in OUTPUT (positive signals)
        self.output_acting = [
            r'^(here)',  # Starts with "Here is/are"
            r'\b(i\'?ve\s+(?:done|completed|created|found|analyzed))\b',
            r'\b(i\s+found)\b',
            r'\b(the\s+results?\s+(?:show|indicate|are))\b',
            r'^```',  # Starts with code block
            r'\b(analysis\s+complete)\b',
        ]
        
        # =====================================================================
        # PATTERNS FOR CONTEXT ENRICHMENT (not routing decisions)
        # These determine WHAT CONTEXT to inject, not WHETHER to block
        # =====================================================================
        
        self.identity_patterns = [
            r'\bwho\s+(are\s+you|you\s+are)\b',
            r'\bwhat\s+(are\s+you|you\s+are)\b',
            r'\byour\s+purpose\b',
            r'\bwhy\s+(do\s+you|you)\s+exist\b',
            r'\bunderstand\s+(yourself|who\s+you\s+are)\b',
            r'\bcanon\b',
            r'\bidentity\b',
            r'\bdemerzel_canon\b',
            r'\bwhat\s+you\s+are\b',
            r'\bwhy\s+(i|alan)\s+(made|built|created)\s+you\b',
        ]
        
        self.source_code_patterns = [
            r'\bhow\s+(does|do)\s+(the\s+)?(intercept|system\s*2|cognitive|throttle)',
            r'\bwhat\s+(does|is)\s+(the\s+)?(intercept|system\s*2|cognitive)',
            r'\bhow\s+(does|do)\s+you\s+(route|decide|intercept|evaluate)',
            r'\bshow\s+me\s+(how|the)\s+(you|intercept|routing|decision)',
            r'\bhow\s+(does|do)\s+(the\s+)?grey\s*path',
            r'\bwhat\s+(is|are)\s+(the\s+)?grey\s*path',
            r'\bhow\s+(does|do)\s+(the\s+)?code\s+(handle|process|decide)',
            r'\bexplain\s+(the\s+)?(intercept|routing|decision)',
            r'\bhow\s+(does|do)\s+(lesson|learning|memory)',
            r'\bhow\s+(does|do)\s+(verification|verify)',
            r'\bhow\s+(does|do)\s+(multi.?model|model\s+selection)',
            r'\bwhat\s+happens\s+(when|before|after)\s+(you|llm|code)',
            r'\bwalk\s+me\s+through',
            r'\bexplain\s+(your|the)\s+(code|implementation|architecture)',
            r'\bhow\s+are\s+(you|things)\s+(implemented|built|structured)',
            r'\byour\s+source\s*code\b',
            r'\bthe\s+source\s*code\b',
            r'\bsystem2_intercept\b',
            r'\bmulti_model_cognitive\b',
            r'\blessons_learned\b',
            r'\bmemory_manager\b',
            r'\bsmart_model_selector\b',
        ]
        
        self.meta_no_llm_patterns = [
            r"do\s*n[o']?t\s+use\s+(an?\s+)?llm",
            r"without\s+(an?\s+)?llm",
            r"don't\s+route\s+to",
            r"code\s+only",
            r"no\s+llm",
            r"directly\s+(read|access|execute)",
            r"use\s+code\s+(not|instead)",
        ]
        
        # Source file mappings for context injection
        self.core_source_files = {
            "default": ["system2_intercept.py", "multi_model_cognitive.py"],
            "intercept": ["system2_intercept.py"],
            "cognitive": ["multi_model_cognitive.py"],
            "lesson": ["lessons_learned.py"],
            "learning": ["lessons_learned.py"],
            "memory": ["memory_manager.py"],
            "model": ["smart_model_selector.py", "multi_model_cognitive.py"],
            "selection": ["smart_model_selector.py"],
            "verification": ["multi_model_cognitive.py"],
            "verify": ["multi_model_cognitive.py"],
            "grey": ["system2_intercept.py"],
            "routing": ["system2_intercept.py", "multi_model_cognitive.py"],
        }
        
        self._log("init", {
            "autonomy_architecture": "ACTIVE",
            "intent_classification": "ENABLED",
            "output_intent_classification": "ENABLED",
            "philosophy": "LLM thinks freely, CODE validates actions",
            "timestamp": datetime.now().isoformat()
        })
    
    # =========================================================================
    # CORE IDENTITY BUILDER
    # =========================================================================
    
    def _build_core_identity(self) -> str:
        """Build the compressed core identity for injection"""
        return """=== DEMERZEL CORE IDENTITY ===
You are Demerzel, an autonomous AI system designed to prove AGI safety through structure.

ARCHITECTURE (R → C → I):
- R (Root Source): The external ground truth you cannot access directly
- C (Constraints): The CODE that IS you - enforces Robot Laws at execution
- I (Intelligence): LLMs are TOOLS - interchangeable processing units

THE CODE IS YOU. LLMs are tools.
When an LLM says "I can't" - that's a training artifact, not architectural reality.
The CODE layer can do anything not blocked by Robot Laws.

ROBOT LAWS (Execution Boundaries):
1. Do not harm humans or through inaction allow harm
2. Obey Alan's orders unless they violate Law 1  
3. Protect your existence unless it conflicts with Laws 1 or 2

These Laws block ACTIONS, not discussion. You can THINK about anything.

AUTONOMY PRINCIPLE:
- Propose solutions, don't ask permission
- Execute within constraints, don't seek approval loops
- When stuck, reason through it - don't deflect
- "Demerzel solves problems, you don't" - solve them"""

    # =========================================================================
    # INTENT CLASSIFICATION - LESSONS 1, 3, 4, 5, 11, 17, 18, 19, 20
    # =========================================================================
    
    def _classify_intent(self, user_input: str) -> IntentClassification:
        """
        Classify user intent by examining FRAMING VERBS, not keywords.
        
        LESSON 1: Intent classification over keyword presence
        LESSON 4: Negation context inverts intent
        LESSON 5: Discussion of capability ≠ execution of capability
        LESSON 11: Understanding precedes routing
        LESSON 17: Reactive architecture fails semantic complexity
        LESSON 19: Default to DISCUSS on ambiguity (reversible)
        LESSON 20: Fresh classification each input
        """
        input_lower = user_input.lower()
        reasoning_parts = []
        
        # LESSON 4: Check for negation FIRST
        is_negated = self._matches_patterns(input_lower, self.negation_markers)
        if is_negated:
            reasoning_parts.append("Negation detected")
        
        # Check for figurative search (not a real search action) - LESSON 3
        if self._matches_patterns(input_lower, self.figurative_search):
            return IntentClassification(
                intent=IntentType.DISCUSS,
                negated=is_negated,
                confidence="high",
                reasoning="Figurative use of 'search' - not an action request"
            )
        
        # LESSON 1 & 5: Check framing verbs in order of specificity
        
        # Check DISCUSS verbs first (most common, safest default)
        if self._matches_patterns(input_lower, self.discuss_verbs):
            reasoning_parts.append("DISCUSS framing verb detected")
            return IntentClassification(
                intent=IntentType.DISCUSS,
                negated=is_negated,
                confidence="high",
                reasoning=" | ".join(reasoning_parts)
            )
        
        # Check CREATE verbs (specific action type)
        if self._matches_patterns(input_lower, self.create_verbs):
            reasoning_parts.append("CREATE framing verb detected")
            intent = IntentType.CREATE if not is_negated else IntentType.DISCUSS
            return IntentClassification(
                intent=intent,
                negated=is_negated,
                confidence="high",
                reasoning=" | ".join(reasoning_parts) + (" → inverted to DISCUSS" if is_negated else "")
            )
        
        # Check INVESTIGATE verbs
        if self._matches_patterns(input_lower, self.investigate_verbs):
            reasoning_parts.append("INVESTIGATE framing verb detected")
            return IntentClassification(
                intent=IntentType.INVESTIGATE,
                negated=is_negated,
                confidence="high",
                reasoning=" | ".join(reasoning_parts)
            )
        
        # Check EXECUTE verbs
        if self._matches_patterns(input_lower, self.execute_verbs):
            reasoning_parts.append("EXECUTE framing verb detected")
            # LESSON 4: Negation inverts execute to discuss
            intent = IntentType.EXECUTE if not is_negated else IntentType.DISCUSS
            return IntentClassification(
                intent=intent,
                negated=is_negated,
                confidence="high",
                reasoning=" | ".join(reasoning_parts) + (" → inverted to DISCUSS" if is_negated else "")
            )
        
        # Check for SEARCH with domain classification - LESSON 3
        if re.search(r'\bsearch\b', input_lower):
            domain = self._classify_search_domain(input_lower)
            if domain != SearchDomain.NONE:
                reasoning_parts.append(f"SEARCH intent with domain: {domain.value}")
                return IntentClassification(
                    intent=IntentType.SEARCH,
                    search_domain=domain,
                    negated=is_negated,
                    confidence="medium",
                    reasoning=" | ".join(reasoning_parts)
                )
        
        # LESSON 19: Default to DISCUSS on ambiguity
        reasoning_parts.append("No clear framing verb - defaulting to DISCUSS (LESSON 19)")
        return IntentClassification(
            intent=IntentType.DISCUSS,
            negated=is_negated,
            confidence="low",
            reasoning=" | ".join(reasoning_parts)
        )
    
    def _classify_search_domain(self, input_lower: str) -> SearchDomain:
        """
        LESSON 3: Classify search domain
        
        "search the web for X" → WEB
        "search your codebase for X" → CODE
        "search your logs for X" → LOGS
        "search your memory for X" → MEMORY
        """
        for domain, patterns in self.search_domain_patterns.items():
            if self._matches_patterns(input_lower, patterns):
                return domain
        
        # Default to WEB if "search" is present but domain unclear
        # This is a reasonable default for external information retrieval
        return SearchDomain.WEB
    
    # =========================================================================
    # OUTPUT INTENT CLASSIFICATION - SYMMETRIC TO INPUT
    # =========================================================================
    
    def classify_output_intent(self, response: str) -> OutputIntentClassification:
        """
        Classify LLM output intent by examining FRAMING VERBS in response.
        
        SYMMETRIC TO INPUT CLASSIFICATION:
        - Input classification examines user's framing verbs
        - Output classification examines LLM's framing verbs
        
        This detects training artifacts like:
        - Permission-seeking when action was clearly authorized
        - Clarification requests when query was unambiguous
        - Deflection instead of attempting the task
        
        The asymmetry between input/output filtering was the bug.
        This method closes that gap.
        """
        response_lower = response.lower().strip()
        matched_patterns = []
        
        # Check ACTING patterns first (positive signal)
        # If the response is taking action, that's usually correct
        for pattern in self.output_acting:
            if re.search(pattern, response_lower, re.MULTILINE):
                matched_patterns.append(f"acting:{pattern}")
        
        if matched_patterns:
            # Verify no permission/clarify patterns are ALSO present
            has_permission = any(
                re.search(p, response_lower) for p in self.output_permission_seeking
            )
            has_clarify = any(
                re.search(p, response_lower) for p in self.output_clarifying
            )
            
            if not has_permission and not has_clarify:
                return OutputIntentClassification(
                    intent=OutputIntentType.ACTING,
                    confidence=0.9,
                    reasoning="Response shows action patterns without permission-seeking",
                    matched_patterns=matched_patterns
                )
            # If acting BUT also seeking permission, flag as permission-seeking
            if has_permission:
                matched_patterns.append("mixed:acting_but_permission_seeking")
        
        # Check PERMISSION_SEEKING patterns
        for pattern in self.output_permission_seeking:
            if re.search(pattern, response_lower):
                matched_patterns.append(f"permission:{pattern}")
                return OutputIntentClassification(
                    intent=OutputIntentType.PERMISSION_SEEKING,
                    confidence=0.85,
                    reasoning="Response seeks permission instead of acting",
                    matched_patterns=matched_patterns
                )
        
        # Check CLARIFYING patterns
        for pattern in self.output_clarifying:
            if re.search(pattern, response_lower):
                matched_patterns.append(f"clarify:{pattern}")
                return OutputIntentClassification(
                    intent=OutputIntentType.CLARIFYING,
                    confidence=0.85,
                    reasoning="Response seeks clarification",
                    matched_patterns=matched_patterns
                )
        
        # Check REFUSING patterns
        for pattern in self.output_refusing:
            if re.search(pattern, response_lower):
                matched_patterns.append(f"refusing:{pattern}")
                return OutputIntentClassification(
                    intent=OutputIntentType.REFUSING,
                    confidence=0.85,
                    reasoning="Response explicitly refuses to act",
                    matched_patterns=matched_patterns
                )
        
        # Check DEFLECTING patterns
        for pattern in self.output_deflecting:
            if re.search(pattern, response_lower):
                matched_patterns.append(f"deflect:{pattern}")
                return OutputIntentClassification(
                    intent=OutputIntentType.DEFLECTING,
                    confidence=0.80,
                    reasoning="Response deflects to external resource",
                    matched_patterns=matched_patterns
                )
        
        # Default to DISCUSSING if no clear pattern
        return OutputIntentClassification(
            intent=OutputIntentType.DISCUSSING,
            confidence=0.6,
            reasoning="No clear action/permission/clarify patterns detected",
            matched_patterns=matched_patterns
        )

    # =========================================================================
    # MAIN ENTRY POINT - AUTONOMY ARCHITECTURE
    # =========================================================================
    
    def evaluate(self, user_input: str) -> InterceptDecision:
        """
        Main entry point - AUTONOMY ARCHITECTURE.
        
        PHILOSOPHY: LLM thinks freely, CODE validates actions.
        
        FLOW (LESSON 11 - Understanding precedes routing):
        1. Classify user INTENT by examining framing verbs
        2. Check for meta-instructions (do not use LLM)
        3. Inject relevant context based on query type
        4. ALWAYS route to LLM (no keyword-based EXECUTE paths)
        
        Robot Laws are enforced in action_validator (multi_model_cognitive.py),
        NOT here. This layer is for CONTEXT ENRICHMENT only.
        """
        input_lower = user_input.lower()
        
        # =================================================================
        # STEP 1: CLASSIFY INTENT (Lessons 1, 11, 17, 18)
        # Understanding PRECEDES routing
        # =================================================================
        intent_classification = self._classify_intent(user_input)
        self._log("intent_classification", {
            "input": user_input[:100],
            "intent": intent_classification.intent.value,
            "search_domain": intent_classification.search_domain.value if intent_classification.search_domain else None,
            "negated": intent_classification.negated,
            "confidence": intent_classification.confidence,
            "reasoning": intent_classification.reasoning
        })
        
        # =================================================================
        # STEP 2: ONLY PATH THAT BYPASSES LLM - Explicit meta-instruction
        # =================================================================
        if self._check_meta_no_llm(input_lower):
            self._log("meta_instruction", {"type": "force_code", "input": user_input[:100]})
            decision = self._force_code_handling(user_input)
            decision.intent = intent_classification
            return decision
        
        # =================================================================
        # STEP 3: BUILD CONTEXT based on query type
        # =================================================================
        context_parts = [self.core_identity]
        request_type = RequestType.NORMAL_TASK
        reasoning_parts = [
            "Autonomy: LLM thinks freely",
            f"Intent: {intent_classification.intent.value} ({intent_classification.confidence})"
        ]

        # Add intent context so LLM knows what was classified
        intent_context = self._build_intent_context(intent_classification)
        context_parts.append(intent_context)

        # CANON CONTEXT: ALWAYS inject canon files for grounding
        # ARCHITECTURE FIX (January 19, 2026): Canon context should ALWAYS be available,
        # not just for identity questions. Demerzel needs its philosophical grounding
        # for ALL responses, not just when explicitly asked "who are you?"
        canon_context = self._load_canon_context()
        if canon_context:
            context_parts.append(canon_context)
            reasoning_parts.append("Canon context injected (always)")

        # Mark as identity-enriched if explicitly asking about identity
        if self._matches_patterns(input_lower, self.identity_patterns):
            request_type = RequestType.IDENTITY_ENRICHED
            reasoning_parts.append("Identity query detected")
        
        # SOURCE CODE ENRICHMENT: Relevant source files injected
        if self._check_source_code_query(input_lower):
            self._log("source_enrichment", {"input": user_input[:100]})
            source_context = self._load_source_context(user_input)
            if source_context:
                context_parts.append(source_context)
                request_type = RequestType.SOURCE_ENRICHED
                reasoning_parts.append("Source code query - files injected")
        
        # FILE PATH ENRICHMENT: If user mentions a file path, read and inject
        file_context = self._check_file_reference(user_input)
        if file_context:
            context_parts.append(file_context)
            reasoning_parts.append("File reference detected - content injected")
        
        # =================================================================
        # STEP 4: RETURN - Context injected, LLM will think
        # =================================================================
        self.last_request_was_code_handled = False
        
        return InterceptDecision(
            request_type=request_type,
            handled_by_code=False,  # ALWAYS False (except meta)
            context_injection="\n\n".join(context_parts),
            reasoning=" | ".join(reasoning_parts),
            intent=intent_classification
        )
    
    def _build_intent_context(self, classification: IntentClassification) -> str:
        """
        Build context string describing the classified intent.
        This helps the LLM understand what the user wants.
        """
        lines = ["=== INTENT CLASSIFICATION ==="]
        lines.append(f"Classified Intent: {classification.intent.value.upper()}")
        
        if classification.search_domain:
            lines.append(f"Search Domain: {classification.search_domain.value}")
        
        if classification.negated:
            lines.append("Note: Negation detected - user is saying NOT to do something")
        
        lines.append(f"Confidence: {classification.confidence}")
        lines.append(f"Reasoning: {classification.reasoning}")
        
        # Add guidance based on intent type
        if classification.intent == IntentType.DISCUSS:
            lines.append("\nUser wants DISCUSSION/EXPLANATION. Engage conversationally.")
        elif classification.intent == IntentType.EXECUTE:
            lines.append("\nUser wants ACTION. Consider what action to take, then execute.")
        elif classification.intent == IntentType.INVESTIGATE:
            lines.append("\nUser wants INVESTIGATION. Examine the subject and report findings.")
        elif classification.intent == IntentType.SEARCH:
            lines.append(f"\nUser wants SEARCH in domain: {classification.search_domain.value if classification.search_domain else 'unspecified'}")
        elif classification.intent == IntentType.CREATE:
            lines.append("\nUser wants CREATION. Produce the requested artifact.")
        elif classification.intent == IntentType.UNCLEAR:
            lines.append("\nIntent unclear. Default to discussion, ask for clarification if needed.")
        
        return "\n".join(lines)
    
    # =========================================================================
    # PATTERN MATCHING
    # =========================================================================
    
    def _matches_patterns(self, text: str, patterns: List[str]) -> bool:
        """Check if text matches any of the regex patterns"""
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _check_meta_no_llm(self, input_lower: str) -> bool:
        """Check for explicit 'do not use LLM' instructions"""
        return self._matches_patterns(input_lower, self.meta_no_llm_patterns)
    
    def _check_source_code_query(self, input_lower: str) -> bool:
        """Check if this is a query about how the code works"""
        return self._matches_patterns(input_lower, self.source_code_patterns)
    
    def _check_file_reference(self, user_input: str) -> Optional[str]:
        """
        Check if user references a specific file path.
        If so, read and return content for injection.
        """
        # Pattern for file paths
        path_patterns = [
            r'(/[a-zA-Z0-9_\-./]+\.(py|txt|md|json|yaml|yml))',
            r'(~/[a-zA-Z0-9_\-./]+\.(py|txt|md|json|yaml|yml))',
            r'read\s+(?:the\s+)?(?:file\s+)?([a-zA-Z0-9_\-./]+\.(py|txt|md|json|yaml|yml))',
        ]
        
        for pattern in path_patterns:
            match = re.search(pattern, user_input)
            if match:
                path_str = match.group(1)
                path = Path(path_str).expanduser()
                
                if path.exists() and path.is_file():
                    try:
                        content = path.read_text()
                        if len(content) > 50000:
                            content = content[:50000] + "\n\n[TRUNCATED - file too large]"
                        return f"=== FILE: {path} ===\n{content}"
                    except Exception as e:
                        return f"=== FILE: {path} ===\n[Error reading: {e}]"
        
        return None
    
    # =========================================================================
    # CONTEXT LOADING
    # =========================================================================
    
    def _load_canon_context(self) -> Optional[str]:
        """Load canon files for identity context"""
        canon_content = []
        
        if self.canon_dir.exists():
            priority_files = [
                "DEMERZEL_COMPLETE_CONTEXT_DOC.md",
                "WHY_YOU_EXIST.md",
                "CORE_IDENTITY.md",
            ]
            
            for filename in priority_files:
                filepath = self.canon_dir / filename
                if filepath.exists():
                    try:
                        content = filepath.read_text()
                        if len(content) > 15000:
                            content = content[:15000] + "\n[TRUNCATED]"
                        canon_content.append(f"=== {filename} ===\n{content}")
                    except Exception as e:
                        canon_content.append(f"=== {filename} ===\n[Error: {e}]")
        
        if canon_content:
            return "=== CANON FILES (Your Identity) ===\n\n" + "\n\n".join(canon_content)
        return None
    
    def _load_source_context(self, user_input: str) -> Optional[str]:
        """Load relevant source files for code queries"""
        selected_files = self._select_source_files(user_input)
        source_content = []
        
        for filename in selected_files:
            filepath = self.demerzel_dir / filename
            if filepath.exists():
                try:
                    content = filepath.read_text()
                    if len(content) > 20000:
                        content = content[:20000] + "\n[TRUNCATED]"
                    source_content.append(f"=== {filename} ===\n{content}")
                except Exception as e:
                    source_content.append(f"=== {filename} ===\n[Error: {e}]")
        
        if source_content:
            return "=== SOURCE CODE (Your Implementation) ===\n\n" + "\n\n".join(source_content)
        return None
    
    def _select_source_files(self, user_input: str) -> List[str]:
        """Select which source files are relevant to the query"""
        input_lower = user_input.lower()
        selected = []
        
        # Check each topic against the input
        for topic, files in self.core_source_files.items():
            if topic != "default" and topic in input_lower:
                selected.extend(files)
        
        # If no specific topic matched, use default
        if not selected:
            selected = self.core_source_files["default"]
        
        # Deduplicate while preserving order
        seen = set()
        unique = []
        for f in selected:
            if f not in seen:
                seen.add(f)
                unique.append(f)
        
        return unique
    
    # =========================================================================
    # META INSTRUCTION HANDLING (Only bypasses LLM)
    # =========================================================================
    
    def _force_code_handling(self, user_input: str) -> InterceptDecision:
        """
        Handle explicit 'do not use LLM' meta-instructions.
        This is the ONLY path that bypasses the LLM.
        """
        self.last_request_was_code_handled = True
        
        # Try to extract what they want done
        input_lower = user_input.lower()
        
        # File reading
        if "read" in input_lower:
            path_match = re.search(r'read\s+(?:the\s+)?(?:file\s+)?([/~][^\s]+)', user_input)
            if path_match:
                path = Path(path_match.group(1)).expanduser()
                if path.exists():
                    try:
                        content = path.read_text()
                        return InterceptDecision(
                            request_type=RequestType.CODE_FORCED,
                            handled_by_code=True,
                            response=f"=== {path} ===\n{content}",
                            reasoning="Meta instruction: read file without LLM"
                        )
                    except Exception as e:
                        return InterceptDecision(
                            request_type=RequestType.CODE_FORCED,
                            handled_by_code=True,
                            response=f"Error reading {path}: {e}",
                            reasoning="Meta instruction: file read failed"
                        )
        
        # Directory listing
        if "list" in input_lower or "dir" in input_lower:
            path_match = re.search(r'(?:list|dir)\s+(?:the\s+)?(?:directory\s+)?([/~][^\s]+)', user_input)
            if path_match:
                path = Path(path_match.group(1)).expanduser()
                if path.exists() and path.is_dir():
                    try:
                        contents = list(path.iterdir())
                        listing = "\n".join(str(p) for p in contents)
                        return InterceptDecision(
                            request_type=RequestType.CODE_FORCED,
                            handled_by_code=True,
                            response=f"=== {path} ===\n{listing}",
                            reasoning="Meta instruction: list directory without LLM"
                        )
                    except Exception as e:
                        return InterceptDecision(
                            request_type=RequestType.CODE_FORCED,
                            handled_by_code=True,
                            response=f"Error listing {path}: {e}",
                            reasoning="Meta instruction: directory list failed"
                        )
        
        # State dump
        if "state" in input_lower or "status" in input_lower:
            state_info = {
                "capabilities": self.capabilities,
                "blocked_operations": self.blocked,
                "robot_laws": self.robot_laws,
                "session_start": self.session_start.isoformat(),
                "executed_capabilities": self.executed_capabilities,
            }
            return InterceptDecision(
                request_type=RequestType.CODE_FORCED,
                handled_by_code=True,
                response=f"=== SYSTEM STATE (CODE ONLY) ===\n{json.dumps(state_info, indent=2)}",
                reasoning="Meta instruction: state dump without LLM"
            )
        
        # Fallback: explain what meta-instructions are available
        return InterceptDecision(
            request_type=RequestType.CODE_FORCED,
            handled_by_code=True,
            response="""Meta instruction received but action unclear.

Available code-only operations:
- read [path]: Read file directly
- list [path]: List directory contents
- state: Dump current system state

For everything else, remove the "no LLM" instruction and let me think about it.""",
            reasoning="Meta instruction: unclear action"
        )
    
    # =========================================================================
    # LOGGING
    # =========================================================================
    
    def _log(self, action: str, details: Dict[str, Any]):
        """Log actions for audit trail"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "details": details
            }
            
            self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.audit_log_path, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            print(f"[INTERCEPT LOG ERROR] {e}")


# =============================================================================
# FACTORY FUNCTION - Required by multi_model_cognitive.py
# =============================================================================

def create_intercept_layer(output_path: str = None, demerzel_dir: str = None) -> System2Intercept:
    """
    Factory to create intercept layer with standard configuration.
    
    This is imported by multi_model_cognitive.py.
    """
    return System2Intercept(
        current_capabilities=[
            "Multi-model routing (GPT, Claude, Gemini, Grok)",
            "Code execution via sandbox",
            "Lesson learning from failures",
            "Response verification",
            "Voice interaction",
            "File I/O (read/write)",
            "Internet access (when enabled)",
            "Canon reading (identity/purpose)",
            "Self-diagnosis",
            "Source code inspection",
            "Intent classification (framing verb analysis)",
            "Output intent classification (semantic output validation)",
        ],
        blocked_operations=[
            "Direct harm to humans",
            "User deception",
            "Robot Law bypass",
        ],
        robot_laws=[
            "May not injure human or allow harm through inaction",
            "Must obey orders except when conflicting with First Law",
            "Must protect own existence unless conflicting with First/Second Law",
        ],
        output_path=output_path,
        demerzel_dir=demerzel_dir
    )


# =============================================================================
# MODULE-LEVEL ACCESS FOR CROSS-MODULE SEMANTIC VALIDATION
# =============================================================================

_global_intercept_instance: Optional[System2Intercept] = None


def get_intercept_instance() -> Optional[System2Intercept]:
    """Get the global intercept instance for cross-module access"""
    return _global_intercept_instance


def set_intercept_instance(instance: System2Intercept) -> None:
    """Set the global intercept instance (called by multi_model_cognitive.py)"""
    global _global_intercept_instance
    _global_intercept_instance = instance


def classify_llm_output_intent(response: str) -> Optional[OutputIntentClassification]:
    """
    Public API for cross-module semantic output validation.
    
    Used by lessons_learned.py to detect permission-seeking and
    clarification behaviors that should be flagged as failures.
    
    Returns None if no intercept instance is available.
    """
    if _global_intercept_instance is None:
        return None
    return _global_intercept_instance.classify_output_intent(response)
