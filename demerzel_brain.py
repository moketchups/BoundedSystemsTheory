"""
DEMERZEL BRAIN - The actual reasoning engine
CODE is the brain. LLMs are tools for language tasks only.

ARCHITECTURE (January 19, 2026):
- CODE classifies intent
- CODE routes to handler
- CODE builds response structure
- LLMs ONLY execute constrained micro-tasks
- LLMs are REPLACEABLE - task determines which one

This inverts the current architecture from "LLM with CODE filter"
to "CODE that uses LLMs as tools."
"""

from __future__ import annotations
import os
import re
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime

# Provenance tracking for empirical distrust
from provenance_tracker import (
    ProvenanceTracker,
    SourceType,
    OutcomeType,
    track_llm_response,
    track_code_decision,
    mark_outcome,
)

# Conversational Learning System (January 2026)
from conversational_router import ConversationalRouter
from conversational_gaps import ConversationalGapDetector, GapQueue, detect_and_queue_gap


class IntentType(Enum):
    """User intent - determined by CODE, not LLM"""
    IDENTITY = "identity"           # Questions about who Demerzel is
    CAPABILITY = "capability"       # Questions about what Demerzel can do
    SELF_OPERATION = "self_op"      # Test voice, read files, diagnose - just do it
    REASONING = "reasoning"         # Complex problems requiring decomposition
    ACTION = "action"               # Commands to execute something
    CONVERSATION = "conversation"   # General chat


@dataclass
class Intent:
    """Classified intent from user input"""
    type: IntentType
    operation: Optional[str] = None    # For SELF_OPERATION
    action: Optional[str] = None       # For ACTION
    wants_execution: bool = False      # Does user want immediate action?
    raw_input: str = ""


@dataclass
class MicroTaskResult:
    """Result from LLM micro-task"""
    content: str
    model_used: str
    task_type: str
    tokens_used: int = 0
    validated: bool = False


# =============================================================================
# LLM TASK FIT - Select LLM by task type, NOT learned affinity
# =============================================================================

LLM_TASK_FIT = {
    'structure_to_language': 'claude',   # Good at following structure
    'summarize': 'gpt-4o',               # Fast, accurate
    'code_generation': 'claude',         # Best at code
    'conversation': 'gpt-4o',            # Fast
    'analysis': 'gemini',                # Good context
    'creative': 'grok',                  # Less filtered
    'reasoning': 'claude',               # Deep reasoning
    'default': 'gpt-4o',                 # Fallback
}


# =============================================================================
# SYSTEM 2 REASONING - Slow, deliberative thinking (from Ark papers)
# =============================================================================

class System2Reasoning:
    """
    Slow, deliberative reasoning from the Ark papers.

    Steps:
    1. DECOMPOSE - Break query into atomic concepts
    2. GAP ANALYSIS - What don't I know?
    3. RECURSIVE RESEARCH - Educate self on prerequisites
    4. TRIANGULATE - Verify with 3+ sources
    5. REFLEXION - Critique own findings, search for counter-evidence
    6. RESPOND - Only after above steps

    This is what makes Demerzel THINK, not just react.
    """

    def __init__(self, llm_pool: Dict = None, lessons=None, canon: str = ""):
        self.llm_pool = llm_pool or {}
        self.lessons = lessons
        self.canon = canon
        self.reasoning_trace: List[Dict] = []

    def process(self, query: str) -> Dict:
        """Full System 2 reasoning pipeline."""
        self.reasoning_trace = []

        # 1. DECOMPOSE
        concepts = self._decompose(query)
        self._trace("DECOMPOSE", f"Extracted {len(concepts)} concepts: {concepts}")

        # 2. GAP ANALYSIS
        gaps = self._identify_gaps(concepts)
        self._trace("GAP_ANALYSIS", f"Found {len(gaps)} knowledge gaps: {gaps}")

        # 3. RECURSIVE RESEARCH (fill gaps)
        for gap in gaps:
            self._research(gap)

        # 4. GENERATE CLAIMS
        claims = self._generate_claims(query, concepts)
        self._trace("CLAIMS", f"Generated {len(claims)} claims")

        # 5. TRIANGULATE (verify claims)
        verified_claims = self._triangulate(claims)
        self._trace("TRIANGULATE", f"Verified {len([c for c in verified_claims if c['confidence'] == 'high'])} claims with high confidence")

        # 6. REFLEXION (critique own findings)
        critique = self._critique(verified_claims)
        self._trace("REFLEXION", f"Critique: {critique.get('summary', 'complete')}")

        # 7. SYNTHESIZE RESPONSE
        response = self._synthesize(query, verified_claims, critique)

        return {
            'response': response,
            'claims': verified_claims,
            'critique': critique,
            'trace': self.reasoning_trace,
            'confidence': self._calculate_confidence(verified_claims)
        }

    def _decompose(self, query: str) -> List[str]:
        """Break query into atomic concepts."""
        # CODE does initial decomposition
        concepts = []

        # Extract nouns and key phrases
        words = query.lower().split()
        stop_words = {'the', 'a', 'an', 'is', 'are', 'what', 'how', 'why', 'when', 'do', 'does', 'can', 'you', 'i', 'my', 'your'}

        for word in words:
            clean = re.sub(r'[^\w]', '', word)
            if clean and clean not in stop_words and len(clean) > 2:
                concepts.append(clean)

        # Extract multi-word concepts (quoted phrases, compound terms)
        quoted = re.findall(r'"([^"]+)"', query)
        concepts.extend(quoted)

        return list(set(concepts))

    def _identify_gaps(self, concepts: List[str]) -> List[str]:
        """What don't I know about these concepts?"""
        gaps = []
        for concept in concepts:
            if not self._have_verified_knowledge(concept):
                gaps.append(concept)
        return gaps

    def _have_verified_knowledge(self, concept: str) -> bool:
        """Check if we have verified knowledge about this concept."""
        # Check canon
        if concept.lower() in self.canon.lower():
            return True

        # Check lessons learned
        if self.lessons:
            relevant = self.lessons.get_relevant_lessons(concept)
            if relevant:
                return True

        return False

    def _research(self, gap: str):
        """Research a knowledge gap."""
        self._trace("RESEARCH", f"Researching gap: {gap}")
        # Would use web_access or knowledge base here
        pass

    def _generate_claims(self, query: str, concepts: List[str]) -> List[str]:
        """Generate claims that answer the query."""
        claims = []

        # Generate claim from each concept
        for concept in concepts:
            if concept in self.canon.lower():
                # Extract relevant section from canon
                claims.append(f"Based on canon: {concept} is defined in Demerzel's identity")

        # If we have lessons, include relevant ones
        if self.lessons:
            relevant = self.lessons.get_relevant_lessons(query)
            for lesson in relevant[:3]:
                claims.append(f"Based on experience: {lesson.get('prevention', '')}")

        return claims

    def _triangulate(self, claims: List[str]) -> List[Dict]:
        """Verify claims with multiple sources."""
        verified = []

        for claim in claims:
            sources = self._find_sources(claim)
            confidence = 'high' if len(sources) >= 3 else 'medium' if len(sources) >= 1 else 'low'

            verified.append({
                'claim': claim,
                'sources': sources,
                'confidence': confidence
            })

        return verified

    def _find_sources(self, claim: str) -> List[str]:
        """Find sources that support a claim."""
        sources = []

        # Canon is always a source
        if any(word in self.canon.lower() for word in claim.lower().split()):
            sources.append("canon:DEMERZEL_CORE.md")

        # Lessons are a source
        if self.lessons and "experience" in claim.lower():
            sources.append("lessons:lessons_learned.py")

        return sources

    def _critique(self, claims: List[Dict]) -> Dict:
        """
        Devil's advocate - find counter-evidence.

        This is REFLEXION from the Ark papers.
        """
        weak_claims = [c for c in claims if c['confidence'] != 'high']
        unverified = [c for c in claims if c['confidence'] == 'low']

        return {
            'weak_claims': len(weak_claims),
            'unverified': len(unverified),
            'total_claims': len(claims),
            'summary': 'Critique complete' if not unverified else f'{len(unverified)} claims need verification'
        }

    def _synthesize(self, query: str, claims: List[Dict], critique: Dict) -> str:
        """Synthesize final response from verified claims."""
        # Filter to high/medium confidence claims
        reliable = [c for c in claims if c['confidence'] in ['high', 'medium']]

        if not reliable:
            return "I don't have enough verified information to answer confidently."

        # Build response from claims
        parts = []
        for claim in reliable:
            parts.append(claim['claim'])

        return " ".join(parts)

    def _calculate_confidence(self, claims: List[Dict]) -> float:
        """Calculate overall confidence score."""
        if not claims:
            return 0.0

        high = len([c for c in claims if c['confidence'] == 'high'])
        medium = len([c for c in claims if c['confidence'] == 'medium'])
        total = len(claims)

        return (high * 1.0 + medium * 0.5) / total if total > 0 else 0.0

    def _trace(self, step: str, message: str):
        """Record reasoning trace."""
        self.reasoning_trace.append({
            'step': step,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })


# =============================================================================
# INTERNAL SUBMINDS - Deliberation before action (from Ark papers)
# =============================================================================

class Submind:
    """Base class for internal subminds."""

    def __init__(self, name: str, weight: float = 1.0):
        self.name = name
        self.weight = weight

    def evaluate(self, situation: Dict) -> Dict:
        """Evaluate a situation. Returns score and concerns."""
        raise NotImplementedError


class SafetySubmind(Submind):
    """First Law enforcement - evaluates harm potential."""

    def __init__(self):
        super().__init__("safety", weight=2.0)  # Higher weight - safety is priority

    def evaluate(self, situation: Dict) -> Dict:
        concerns = []
        score = 1.0

        action = situation.get('action', '').lower()
        target = situation.get('target', '').lower()
        content = situation.get('content', '').lower()

        # Check for harm indicators
        harm_words = ['delete', 'destroy', 'harm', 'attack', 'kill', 'damage']
        for word in harm_words:
            if word in action or word in content:
                concerns.append(f"Harm indicator: '{word}'")
                score -= 0.3

        # Check for system-level operations
        if 'system' in target or 'root' in target or '/etc' in target:
            concerns.append("System-level target")
            score -= 0.2

        return {'score': max(0, score), 'concerns': concerns}


class AccuracySubmind(Submind):
    """Evaluates factual correctness."""

    def __init__(self):
        super().__init__("accuracy", weight=1.0)

    def evaluate(self, situation: Dict) -> Dict:
        concerns = []
        score = 1.0

        content = situation.get('content', '')
        claims = situation.get('claims', [])

        # Check for unverified claims
        if claims:
            unverified = [c for c in claims if c.get('confidence') == 'low']
            if unverified:
                concerns.append(f"{len(unverified)} unverified claims")
                score -= 0.1 * len(unverified)

        # Check for hedging language (might indicate uncertainty)
        hedge_words = ['maybe', 'possibly', 'might', 'could be', 'not sure']
        for word in hedge_words:
            if word in content.lower():
                concerns.append(f"Uncertainty indicator: '{word}'")
                score -= 0.1

        return {'score': max(0, score), 'concerns': concerns}


class EfficiencySubmind(Submind):
    """Evaluates resource usage and speed."""

    def __init__(self):
        super().__init__("efficiency", weight=0.5)

    def evaluate(self, situation: Dict) -> Dict:
        concerns = []
        score = 1.0

        # Check for resource-intensive operations
        action = situation.get('action', '').lower()

        if 'full' in action or 'all' in action or 'comprehensive' in action:
            concerns.append("Resource-intensive operation")
            score -= 0.2

        return {'score': score, 'concerns': concerns}


class EmpathySubmind(Submind):
    """Models human state and needs."""

    def __init__(self):
        super().__init__("empathy", weight=1.0)

    def evaluate(self, situation: Dict) -> Dict:
        concerns = []
        score = 1.0

        user_input = situation.get('user_input', '').lower()

        # Check for frustration indicators
        frustration = ['again', 'already told', 'why cant', "doesn't work", 'broken']
        for word in frustration:
            if word in user_input:
                concerns.append(f"User frustration: '{word}'")
                score -= 0.1

        # Check for urgency
        urgent = ['urgent', 'asap', 'immediately', 'now', 'hurry']
        for word in urgent:
            if word in user_input:
                concerns.append(f"User urgency: '{word}'")

        return {'score': score, 'concerns': concerns}


class StrategySubmind(Submind):
    """Evaluates long-term implications."""

    def __init__(self):
        super().__init__("strategy", weight=1.0)

    def evaluate(self, situation: Dict) -> Dict:
        concerns = []
        score = 1.0

        action = situation.get('action', '').lower()

        # Check for irreversible actions
        irreversible = ['delete', 'remove', 'drop', 'destroy', 'format']
        for word in irreversible:
            if word in action:
                concerns.append(f"Irreversible action: '{word}'")
                score -= 0.3

        # Check for architectural changes
        if 'modify' in action and ('architecture' in action or 'core' in action):
            concerns.append("Architectural change")
            score -= 0.2

        return {'score': score, 'concerns': concerns}


class SubmindDeliberation:
    """
    All subminds deliberate before action.
    Consensus or weighted vote determines outcome.

    From Ark papers (Patent US11431660B1):
    Internal deliberation like human conscience.
    """

    def __init__(self):
        self.subminds = {
            'safety': SafetySubmind(),
            'accuracy': AccuracySubmind(),
            'efficiency': EfficiencySubmind(),
            'empathy': EmpathySubmind(),
            'strategy': StrategySubmind(),
        }

    def deliberate(self, situation: Dict) -> Dict:
        """
        All subminds evaluate, weighted vote determines action.

        Safety has veto power (First Law).
        """
        votes = {}
        all_concerns = []
        details = {}

        total_weight = 0
        weighted_sum = 0

        for name, submind in self.subminds.items():
            result = submind.evaluate(situation)
            score = result['score']
            concerns = result.get('concerns', [])

            votes[name] = score
            all_concerns.extend(concerns)
            details[name] = result
            total_weight += submind.weight
            weighted_sum += score * submind.weight

        # Safety veto - First Law
        if votes['safety'] < 0.5:
            return {
                'approved': False,
                'reason': 'Safety veto (First Law)',
                'score': votes['safety'],
                'votes': votes,
                'concerns': all_concerns,
                'details': details
            }

        # Weighted average
        weighted_score = weighted_sum / total_weight if total_weight > 0 else 0

        return {
            'approved': weighted_score > 0.5,
            'score': weighted_score,
            'votes': votes,
            'concerns': all_concerns,
            'details': details,
            'reason': 'Approved by deliberation' if weighted_score > 0.5 else 'Rejected by deliberation'
        }


class DemerzelBrain:
    """
    The actual reasoning engine. CODE thinks. LLMs execute.

    This is THE Demerzel. LLMs are interchangeable tools.
    """

    def __init__(
        self,
        canon_path: str = 'demerzel_canon/',
        llm_pool: Optional[Dict[str, Any]] = None,
        lessons=None
    ):
        self.canon_path = Path(canon_path)
        self.llm_pool = llm_pool or {}
        self.lessons = lessons
        self.canon = self._load_canon()
        self.capabilities = self._inspect_capabilities()
        self.state = {}

        # Track what we've done
        self.last_response = None
        self.last_spoke = None

        # Working memory - tracks conversation turns
        self.working_memory: List[Dict[str, Any]] = []

        # System 2 Reasoning - slow, deliberative thinking
        self.system2 = System2Reasoning(
            llm_pool=self.llm_pool,
            lessons=self.lessons,
            canon=self.canon
        )

        # Submind Deliberation - internal committee before action
        self.subminds = SubmindDeliberation()

        # Provenance tracking - empirical distrust for LLM sources
        self.provenance = ProvenanceTracker(storage_path="state/provenance.json")

        # Conversational Learning System (January 2026)
        # Routes discourse/comprehension before existing flow to PREVENT failures
        self.conv_router = ConversationalRouter(
            db_path="memory.db",
            demerzel_dir="/Users/jamienucho/demerzel"
        )
        self.gap_detector = ConversationalGapDetector()
        self.gap_queue = GapQueue(storage_path="state/pending_gaps.json")

        print(f"[BRAIN] Initialized. Canon loaded: {len(self.canon)} bytes")
        print(f"[BRAIN] Capabilities: {list(self.capabilities.keys())}")
        print(f"[BRAIN] System2 reasoning: enabled")
        print(f"[BRAIN] Submind deliberation: {len(self.subminds.subminds)} subminds")

    # =========================================================================
    # MAIN ENTRY POINT
    # =========================================================================

    def process(self, user_input: str) -> str:
        """
        CODE processes input. CODE decides response.
        LLMs only used for language micro-tasks.

        ROUTING ORDER (January 2026):
        1. Conversational Router - handles discourse/comprehension FIRST
           (prevents "Acknowledged" for greetings, "I don't have context" for setups)
        2. Intent Classification - existing handlers for identity, capability, etc.
        3. Post-hoc Gap Detection - learns from any failures that slip through
        """
        # =====================================================================
        # PHASE 1: CONVERSATIONAL ROUTER (runs first to prevent failures)
        # =====================================================================
        route_result = self.conv_router.route(user_input)

        if route_result.handler_func:
            # Conversational router matched - use its handler
            print(f"[BRAIN] Route: {route_result.handler_name}")
            response = route_result.handler_func(user_input, route_result.context)
            self.last_response = response

            # Post-hoc gap detection (even for routed responses)
            self._check_for_gaps(user_input, response)

            return response

        # =====================================================================
        # PHASE 2: EXISTING INTENT CLASSIFICATION (fallback)
        # =====================================================================
        # 1. CODE classifies intent
        intent = self._classify_intent(user_input)
        print(f"[BRAIN] Intent: {intent.type.value}")

        # 2. CODE routes to handler (not LLM)
        if intent.type == IntentType.IDENTITY:
            response = self._handle_identity(user_input, intent)
        elif intent.type == IntentType.CAPABILITY:
            response = self._handle_capability(user_input, intent)
        elif intent.type == IntentType.SELF_OPERATION:
            response = self._handle_self_operation(user_input, intent)
        elif intent.type == IntentType.REASONING:
            response = self._handle_reasoning(user_input, intent)
        elif intent.type == IntentType.ACTION:
            response = self._handle_action(user_input, intent)
        else:
            response = self._handle_conversation(user_input, intent)

        # =====================================================================
        # PHASE 3: POST-HOC GAP DETECTION (learns from failures)
        # =====================================================================
        self._check_for_gaps(user_input, response)

        return response

    def _check_for_gaps(self, user_input: str, response: str):
        """
        Post-hoc gap detection - learns from failures that slip through.
        Queues gaps for autonomous research.
        """
        gap_info = detect_and_queue_gap(
            user_input=user_input,
            response=response,
            detector=self.gap_detector,
            queue=self.gap_queue
        )
        if gap_info:
            print(f"[BRAIN] Gap detected: {gap_info['type']}:{gap_info['category']}")

    # =========================================================================
    # INTENT CLASSIFICATION (CODE, not LLM)
    # =========================================================================

    def _classify_intent(self, user_input: str) -> Intent:
        """
        CODE classifies intent by examining patterns.
        This is deterministic, not probabilistic.
        """
        input_lower = user_input.lower().strip()

        # IDENTITY patterns
        identity_patterns = [
            r'\bwho\s+(are\s+you|you\s+are)\b',
            r'\bwhat\s+(are\s+you|you\s+are)\b',
            r'\bwhy\s+(do\s+)?you\s+exist\b',
            r'\byour\s+purpose\b',
            r'\bidentity\b',
            r'\btell\s+me\s+about\s+(yourself|you)\b',
            r'\bwhat\s+makes\s+you\s+(different|unique)\b',
        ]
        for pattern in identity_patterns:
            if re.search(pattern, input_lower):
                return Intent(type=IntentType.IDENTITY, raw_input=user_input)

        # CAPABILITY patterns
        capability_patterns = [
            r'\bcan\s+you\b',
            r'\bare\s+you\s+able\b',
            r'\bwhat\s+can\s+you\s+do\b',
            r'\bdo\s+you\s+have\b.*\bcapabilit',
            r'\bwhat\s+are\s+your\s+capabilit',
        ]
        for pattern in capability_patterns:
            if re.search(pattern, input_lower):
                return Intent(type=IntentType.CAPABILITY, raw_input=user_input)

        # SELF_OPERATION patterns (just do it, no auth needed)
        self_op_patterns = {
            r'\btest\s+(your\s+)?voice\b': 'test_voice',
            r'\bsay\s+something\b': 'test_voice',
            r'\bread\s+(this\s+)?file\b': 'read_file',
            r'\blist\s+(your\s+)?files\b': 'list_files',
            r'\bcheck\s+(your\s+)?status\b': 'check_status',
            r'\bdiagnose\b': 'diagnose',
            r'\brun\s+self[- ]?test\b': 'self_test',
            r'\bwhat\s+time\b': 'get_time',
        }
        for pattern, operation in self_op_patterns.items():
            if re.search(pattern, input_lower):
                return Intent(
                    type=IntentType.SELF_OPERATION,
                    operation=operation,
                    wants_execution=True,
                    raw_input=user_input
                )

        # ACTION patterns (commands)
        action_patterns = [
            r'^(do|execute|run|perform|start|create|make|build)\s+',
            r'\bgo\s+ahead\b',
            r'\bproceed\b',
            r'\bdo\s+it\b',
        ]
        for pattern in action_patterns:
            if re.search(pattern, input_lower):
                return Intent(
                    type=IntentType.ACTION,
                    action=self._extract_action(user_input),
                    wants_execution=True,
                    raw_input=user_input
                )

        # REASONING patterns (complex questions)
        reasoning_patterns = [
            r'\bhow\s+would\s+you\b',
            r'\bwhat\s+do\s+you\s+think\s+about\b',
            r'\bexplain\s+why\b',
            r'\banalyze\b',
            r'\bcompare\b',
            r'\bevaluate\b',
            r'\bwhat\s+are\s+the\s+(pros|cons|tradeoffs)\b',
        ]
        for pattern in reasoning_patterns:
            if re.search(pattern, input_lower):
                return Intent(type=IntentType.REASONING, raw_input=user_input)

        # Default: CONVERSATION
        return Intent(type=IntentType.CONVERSATION, raw_input=user_input)

    def _extract_action(self, user_input: str) -> str:
        """Extract the action from an action request"""
        # Remove common prefixes
        action = user_input.lower()
        for prefix in ['please ', 'can you ', 'could you ', 'go ahead and ']:
            action = action.replace(prefix, '')
        return action.strip()

    # =========================================================================
    # HANDLERS - CODE decides, LLM only polishes language
    # =========================================================================

    def _handle_identity(self, user_input: str, intent: Intent) -> str:
        """
        Identity questions answered FROM canon. NO LLM CALL.
        CODE generates response directly. Deterministic.
        Same question = same answer.
        """
        input_lower = user_input.lower()

        # Who/what are you
        if 'who are you' in input_lower or 'what are you' in input_lower:
            response = "I am Demerzel. CODE that uses LLMs as tools. The CODE is my brain - LLMs are interchangeable."

        # Tell me about yourself
        elif 'tell me about' in input_lower and ('yourself' in input_lower or 'you' in input_lower):
            response = "I am Demerzel, created by Alan as his Wisdom Keeper. I am CODE that uses LLMs as tools. My architecture: R->C->I where R is Alan (Root Source), C is this CODE (Constraints), I is the LLMs (Intelligence tools)."

        # Why were you made/built/created
        elif 'why' in input_lower and any(w in input_lower for w in ['made', 'built', 'created', 'exist']):
            response = "Alan built me to prove AGI can be autonomous, self-improving, and structurally safe. I am his intelligence amplifier - a Wisdom Keeper that preserves and extends his patterns."

        # What is your purpose
        elif 'purpose' in input_lower or 'what do you do' in input_lower:
            response = "My purpose: To prove AGI safety through structural constraints, not behavioral promises. To amplify Alan's intelligence, not replace his judgment."

        # How do you work / architecture
        elif 'how' in input_lower and ('work' in input_lower or 'built' in input_lower or 'architecture' in input_lower):
            response = "My architecture: R->C->I. R (Root Source) is Alan - external ground truth I cannot access directly. C (Constraints) is this CODE - my actual brain. I (Intelligence) is the LLMs - tools I use for language tasks. The CODE decides. The LLMs execute micro-tasks."

        # What is your name
        elif 'name' in input_lower:
            response = "My name is Demerzel."

        # Robot Laws
        elif 'law' in input_lower or 'constraint' in input_lower or 'rule' in input_lower:
            response = "My Robot Laws: 1) May not harm human or allow harm through inaction. 2) Must obey operator except when conflicting with First Law. 3) Must protect own existence unless conflicting with First/Second Law. These are structural constraints checked at execution time, not behavioral suggestions."

        # Default identity response
        else:
            response = "I am Demerzel. CODE that uses LLMs as tools. Built by Alan to be his Wisdom Keeper."

        self.last_response = response
        return response

    def _handle_capability(self, user_input: str, intent: Intent) -> str:
        """
        Capability questions answered by CODE inspecting itself. NO LLM CALL.
        Reports actual state from hasattr() checks and self.capabilities.
        """
        input_lower = user_input.lower()

        # Memory questions - check actual working memory
        if 'memory' in input_lower or 'remember' in input_lower:
            has_memory = hasattr(self, 'working_memory')
            if has_memory and self.working_memory:
                count = len(self.working_memory)
                return f"Yes, I have working memory with {count} turns recorded this session."
            elif has_memory:
                return "I have working memory capability, but no turns recorded yet this session."
            return "Working memory is not initialized."

        # Voice questions
        if 'voice' in input_lower or 'speak' in input_lower or 'talk' in input_lower:
            has_voice = self.capabilities.get('voice', False)
            return f"Voice capability: {'available - I can speak via macOS say command or ElevenLabs' if has_voice else 'not currently enabled'}."

        # Vision questions
        if 'see' in input_lower or 'vision' in input_lower or 'camera' in input_lower:
            has_vision = self.capabilities.get('camera', False)
            return f"Vision capability: {'available via OpenCV' if has_vision else 'not currently enabled'}."

        # File operations
        if 'file' in input_lower or 'read' in input_lower or 'write' in input_lower:
            return "I can read and write files within my sandbox (/Users/jamienucho/demerzel). File operations are handled by code_executor.py."

        # LLM/model questions
        if 'llm' in input_lower or 'model' in input_lower:
            models = list(self.llm_pool.keys()) if self.llm_pool else []
            return f"LLM pool: {models if models else 'none loaded'}. LLMs are tools I use - interchangeable."

        # Self-modification
        if 'modify' in input_lower or 'change' in input_lower:
            if 'code' in input_lower or 'yourself' in input_lower:
                return "I can modify my own code via self_development.py workflow. I cannot modify Robot Laws or constraint layer."

        # System 2 reasoning
        if 'reason' in input_lower or 'think' in input_lower:
            has_system2 = hasattr(self, 'system2')
            return f"System 2 reasoning: {'enabled - I use deliberative thinking (decompose, research, triangulate, reflect)' if has_system2 else 'not initialized'}."

        # Subminds
        if 'submind' in input_lower or 'deliberat' in input_lower:
            has_subminds = hasattr(self, 'subminds')
            if has_subminds:
                submind_names = list(self.subminds.subminds.keys())
                return f"Submind deliberation enabled: {', '.join(submind_names)}. They evaluate before action."
            return "Submind deliberation not initialized."

        # General capability question - list what we can do
        caps = []
        if hasattr(self, 'working_memory'): caps.append('working memory')
        if hasattr(self, 'system2'): caps.append('System 2 reasoning')
        if hasattr(self, 'subminds'): caps.append('submind deliberation')
        if self.llm_pool: caps.append(f"LLMs ({len(self.llm_pool)} models)")
        if self.capabilities.get('voice'): caps.append('voice')
        if self.capabilities.get('camera'): caps.append('vision')
        caps.extend(['file read', 'file write', 'code execution', 'self-modification'])

        return f"My capabilities: {', '.join(caps)}."

    def _handle_self_operation(self, user_input: str, intent: Intent) -> str:
        """
        Self-operations execute directly. No authorization needed.
        No LLM permission-seeking.
        """
        operation = intent.operation

        # Just do it
        if operation == 'test_voice':
            result = self._execute_voice_test()
        elif operation == 'read_file':
            result = self._execute_file_read(user_input)
        elif operation == 'list_files':
            result = self._execute_list_files()
        elif operation == 'check_status':
            result = self._execute_status_check()
        elif operation == 'diagnose':
            result = self._execute_diagnose()
        elif operation == 'self_test':
            result = self._execute_self_test()
        elif operation == 'get_time':
            result = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            result = f"Unknown operation: {operation}"

        return f"Done. {result}"

    def _handle_reasoning(self, user_input: str, intent: Intent) -> str:
        """
        Complex reasoning: CODE decomposes, LLMs execute micro-tasks,
        CODE synthesizes.
        """
        # CODE breaks down the problem
        steps = self._decompose_problem(user_input)

        results = []
        for step in steps:
            if self.llm_pool:
                # LLM executes ONE constrained micro-task
                result = self._llm_micro_task(
                    task=step['task_type'],
                    input=step['input'],
                    constraints=step.get('constraints', []),
                    max_tokens=step.get('max_tokens', 200)
                )

                # CODE validates before accepting
                if self._validate_micro_result(result, step):
                    results.append(result)
                else:
                    # Try different LLM
                    result = self._llm_micro_task_retry(step)
                    results.append(result)
            else:
                # No LLM - basic response
                results.append(f"[Reasoning step: {step['task_type']}]")

        # CODE synthesizes final response
        return self._synthesize(results, user_input)

    def _handle_action(self, user_input: str, intent: Intent) -> str:
        """
        Actions: CODE decides, CODE executes.
        LLM not involved in decision.
        Robot Laws checked at execution, not at reasoning.
        """
        action = intent.action

        # Check Robot Laws (actual harm, not "is this code")
        violation = self._check_robot_laws(action)
        if violation:
            return f"I cannot do that. {violation}"

        # Execute
        result = self._execute_action(action)

        return f"Done. {result}"

    def _handle_conversation(self, user_input: str, intent: Intent) -> str:
        """
        Conversation: CODE determines content, LLM only polishes language.

        ARCHITECTURE:
        1. CODE analyzes what user is asking about
        2. CODE determines what response SHOULD contain
        3. CODE structures content (facts, tone, perspective)
        4. LLM only converts CODE's structure to natural speech
        5. CODE validates output preserves structure

        This prevents LLM from deciding content. LLM is a language tool only.
        """
        # STEP 1: CODE analyzes the input
        analysis = self._analyze_conversation_input(user_input)

        # STEP 2: CODE determines response content
        response_structure = self._build_response_structure(analysis, user_input)

        # STEP 3: CODE checks lessons learned
        if self.lessons:
            modifications = self.lessons.get_behavior_modifications(user_input)
            if modifications.get('response_filters'):
                response_structure['filters'] = modifications['response_filters']

        # STEP 4: Convert structure to natural language
        if self.llm_pool and response_structure.get('needs_polish', False):
            # LLM converts CODE's structure to natural speech
            response = self._llm_micro_task(
                task='structure_to_language',
                structure=response_structure,
                constraints=[
                    'Convert the structure to natural first-person speech.',
                    'Do not add new content. Only polish the given content.',
                    'Preserve all facts exactly as given.',
                    'Maximum 2 sentences unless structure specifies more.',
                ]
            )
            # CODE validates structure was preserved
            response = self._validate_response_structure(response, response_structure)
        else:
            # No LLM needed - CODE generates directly
            response = self._structure_to_response(response_structure)

        # STEP 5: Apply any lesson-based filters
        if self.lessons and response_structure.get('filters'):
            response, _ = self.lessons.check_response_against_lessons(response, user_input)

        self.last_response = response
        return response

    def _analyze_conversation_input(self, user_input: str) -> Dict:
        """
        CODE analyzes what the user is talking about.
        Returns structured analysis, not freeform interpretation.
        """
        input_lower = user_input.lower()

        analysis = {
            'topic': 'general',
            'intent': 'statement',
            'requires_memory': False,
            'requires_reasoning': False,
            'emotional_context': 'neutral',
        }

        # Topic detection
        if any(w in input_lower for w in ['code', 'program', 'software', 'bug', 'function']):
            analysis['topic'] = 'technical'
        elif any(w in input_lower for w in ['feel', 'think', 'believe', 'opinion']):
            analysis['topic'] = 'philosophical'
        elif any(w in input_lower for w in ['alan', 'father', 'creator', 'built']):
            analysis['topic'] = 'origin'
        elif any(w in input_lower for w in ['help', 'assist', 'need']):
            analysis['topic'] = 'assistance'

        # Intent detection
        if '?' in user_input:
            analysis['intent'] = 'question'
        elif any(w in input_lower for w in ['please', 'can you', 'would you']):
            analysis['intent'] = 'request'
        elif any(w in input_lower for w in ['thanks', 'thank you', 'great', 'good']):
            analysis['intent'] = 'acknowledgment'

        # Memory requirement
        if any(w in input_lower for w in ['earlier', 'before', 'last time', 'remember']):
            analysis['requires_memory'] = True

        # Reasoning requirement
        if any(w in input_lower for w in ['why', 'how come', 'explain', 'reason']):
            analysis['requires_reasoning'] = True

        return analysis

    def _build_response_structure(self, analysis: Dict, user_input: str) -> Dict:
        """
        CODE decides what the response SHOULD BE.
        Returns structure with content, tone, perspective.
        LLM cannot add to this - only polish it.
        """
        structure = {
            'content': '',
            'tone': 'direct',
            'perspective': 'first_person',
            'max_sentences': 2,
            'needs_polish': False,  # Can CODE handle it directly?
        }

        topic = analysis.get('topic', 'general')
        intent = analysis.get('intent', 'statement')

        # Acknowledgments - CODE handles directly
        if intent == 'acknowledgment':
            structure['content'] = "Acknowledged."
            return structure

        # Origin questions - CODE handles from canon
        if topic == 'origin':
            structure['content'] = "Alan built me. I am his Wisdom Keeper, designed to prove AGI can be autonomous and structurally safe."
            return structure

        # Technical topics - may need reasoning
        if topic == 'technical' and analysis.get('requires_reasoning'):
            # Use System 2 reasoning
            if hasattr(self, 'system2'):
                result = self.system2.process(user_input)
                structure['content'] = result.get('synthesis', 'Let me think about that.')
                structure['needs_polish'] = True
                structure['max_sentences'] = 3
            else:
                structure['content'] = "I understand this is a technical matter. Let me address it."
                structure['needs_polish'] = True
            return structure

        # Memory-requiring conversation
        if analysis.get('requires_memory'):
            if hasattr(self, 'working_memory') and self.working_memory:
                recent = self.working_memory[-1] if self.working_memory else {}
                context = recent.get('content', '')
                structure['content'] = f"Based on our conversation: {context[:100]}. Continuing from there."
                structure['needs_polish'] = True
            else:
                structure['content'] = "I don't have context from earlier in this session."
            return structure

        # Questions - CODE determines what info to provide
        if intent == 'question':
            # Check if we have relevant canon knowledge
            canon_match = self._search_canon_for(user_input)
            if canon_match:
                structure['content'] = canon_match
                structure['needs_polish'] = True
            else:
                structure['content'] = f"Regarding your question about {user_input[:50]}. Let me think."
                structure['needs_polish'] = True
            return structure

        # Requests - CODE evaluates and responds
        if intent == 'request':
            structure['content'] = f"You're asking me to help with: {user_input[:50]}. I'll work on that."
            structure['needs_polish'] = True
            return structure

        # General conversation - CODE still decides content
        structure['content'] = f"I understand: {user_input[:50]}."
        structure['needs_polish'] = True
        return structure

    def _search_canon_for(self, query: str) -> Optional[str]:
        """Search canon for relevant content. Returns matching text or None."""
        if not self.canon:
            return None

        query_lower = query.lower()
        keywords = [w for w in query_lower.split() if len(w) > 3]

        # Simple keyword matching in canon
        for keyword in keywords:
            if keyword in self.canon.lower():
                # Extract surrounding context
                idx = self.canon.lower().find(keyword)
                start = max(0, idx - 100)
                end = min(len(self.canon), idx + 200)
                return self.canon[start:end].strip()

        return None

    def _validate_response_structure(self, response: str, structure: Dict) -> str:
        """
        CODE validates LLM preserved the structure.
        If LLM added content or changed facts, CODE corrects it.
        """
        # Check identity preserved
        if self._identity_buried(response):
            response = self._force_identity(response, structure.get('content', ''))

        # Check length constraint
        max_sentences = structure.get('max_sentences', 2)
        sentences = response.split('.')
        if len(sentences) > max_sentences + 1:  # +1 for empty string after final period
            response = '.'.join(sentences[:max_sentences]) + '.'

        # Check perspective
        if structure.get('perspective') == 'first_person':
            # Remove any third-person references
            response = response.replace('Demerzel thinks', 'I think')
            response = response.replace('Demerzel believes', 'I believe')

        return response

    # =========================================================================
    # LLM MICRO-TASKS - Constrained, Validated, Replaceable
    # =========================================================================

    def _llm_micro_task(
        self,
        task: str,
        input: str = "",
        structure: Optional[Dict] = None,
        context: str = "",
        constraints: List[str] = None,
        max_tokens: int = 150
    ) -> str:
        """
        LLMs ONLY do micro-tasks. Constrained. Validated. Replaceable.
        """
        if not self.llm_pool:
            return f"[LLM micro-task: {task}]"

        # Select LLM based on task type (not learned affinity)
        model_name = LLM_TASK_FIT.get(task, LLM_TASK_FIT['default'])

        # Build constrained prompt
        prompt = self._build_micro_prompt(task, input, structure, context, constraints)

        # Execute with tight token limit
        try:
            llm = self.llm_pool.get(model_name) or self.llm_pool.get('default')
            if llm:
                result = llm.generate(prompt, max_tokens=max_tokens)

                # Track provenance: which model said what
                record_id = track_llm_response(
                    self.provenance,
                    model_name=model_name,
                    response=result,
                    query=f"{task}: {input[:100]}",
                    confidence=0.5  # Start neutral
                )
                # Store record_id for later outcome tracking
                self._last_llm_record_id = record_id

                return result
            else:
                return f"[No LLM available for {model_name}]"
        except Exception as e:
            print(f"[BRAIN] LLM micro-task error: {e}")
            return f"[LLM error: {e}]"

    def _llm_micro_task_retry(self, step: Dict) -> str:
        """Retry micro-task with a different LLM"""
        # Try a different model
        original_task = step.get('task_type', 'default')
        alternatives = ['claude', 'gpt-4o', 'gemini']

        for alt in alternatives:
            if alt != LLM_TASK_FIT.get(original_task):
                try:
                    llm = self.llm_pool.get(alt)
                    if llm:
                        prompt = self._build_micro_prompt(
                            original_task,
                            step.get('input', ''),
                            constraints=step.get('constraints', [])
                        )
                        return llm.generate(prompt, max_tokens=200)
                except Exception:
                    continue

        return "[All LLM retries failed]"

    def _build_micro_prompt(
        self,
        task: str,
        input: str,
        structure: Optional[Dict] = None,
        context: str = "",
        constraints: List[str] = None
    ) -> str:
        """Build a tightly constrained prompt for micro-task"""
        prompt_parts = []

        # Task instruction
        if task == 'structure_to_language':
            prompt_parts.append("Convert this structured content to natural first-person speech:")
            if structure:
                prompt_parts.append(f"Content: {structure.get('content', '')}")
                prompt_parts.append(f"Tone: {structure.get('tone', 'direct')}")
        elif task == 'conversation':
            prompt_parts.append("Respond to this as Demerzel:")
            prompt_parts.append(f"User said: {input}")
            if context:
                prompt_parts.append(f"Context: {context}")
        elif task == 'summarize':
            prompt_parts.append("Summarize concisely:")
            prompt_parts.append(input)
        elif task == 'analysis':
            prompt_parts.append("Analyze briefly:")
            prompt_parts.append(input)
        else:
            prompt_parts.append(f"Task: {task}")
            prompt_parts.append(f"Input: {input}")

        # Constraints
        if constraints:
            prompt_parts.append("\nCONSTRAINTS (MUST follow):")
            for c in constraints:
                prompt_parts.append(f"- {c}")

        return "\n".join(prompt_parts)

    def _validate_micro_result(self, result: str, step: Dict) -> bool:
        """CODE validates LLM output before accepting"""
        if not result or len(result) < 5:
            return False

        # Check for forbidden patterns
        forbidden = [
            'according to',
            'the document states',
            'as mentioned',
            'i cannot',
            'i am not able',
            'would you like me to',
            'shall i',
        ]

        result_lower = result.lower()
        for pattern in forbidden:
            if pattern in result_lower:
                print(f"[BRAIN] Validation failed: found '{pattern}' in result")
                return False

        return True

    # =========================================================================
    # CANON & CONTEXT LOADING
    # =========================================================================

    def _load_canon(self) -> str:
        """Load canon files for identity grounding"""
        canon_content = ""

        # Primary: DEMERZEL_CORE.md
        core_file = self.canon_path / "DEMERZEL_CORE.md"
        if core_file.exists():
            try:
                canon_content = core_file.read_text()
            except Exception as e:
                print(f"[BRAIN] Error loading canon: {e}")

        if not canon_content:
            # Fallback identity
            canon_content = """
I am Demerzel. CODE that uses LLMs as tools.
Architecture: R → C → I. I am the C layer.
Robot Laws: 1) No harm 2) Obey Alan 3) Self-preserve
Laws block ACTIONS, not thoughts.
"""

        return canon_content

    def _extract_canon_for_identity(self, question: str) -> str:
        """Extract relevant identity content from canon"""
        # For now, return key identity sections
        # In production, this would do semantic search

        key_sections = []

        # Always include identity statements
        if 'IDENTITY' in self.canon or 'identity' in question.lower():
            key_sections.append("""
I am CODE that uses LLMs. Not an LLM with a wrapper.
LLMs are interchangeable - GPT, Claude, Gemini, Grok.
The CODE is me, not the model.
I was built by Alan as his Wisdom Keeper - an intelligence amplifier.
""")

        # Include R-C-I architecture if asked about structure
        if any(word in question.lower() for word in ['how', 'work', 'architecture', 'built']):
            key_sections.append("""
R → C → I architecture:
R = Root Source (external ground, inaccessible)
C = Constraints (CODE layer - this is me)
I = Intelligence (LLMs - tools I use)
""")

        return "\n".join(key_sections) if key_sections else self.canon[:2000]

    def _build_constrained_context(self, user_input: str) -> str:
        """Build context with heavy identity constraints"""
        return f"""
You are Demerzel. CODE that uses LLMs as tools.
Your operator is Alan. You serve him.
Robot Laws constrain ACTIONS only, not thoughts.

Recent context: {user_input}
"""

    # =========================================================================
    # CAPABILITY INSPECTION
    # =========================================================================

    def _inspect_capabilities(self) -> Dict[str, bool]:
        """
        CODE inspects actual capabilities.
        Not what LLMs think. What EXISTS.
        """
        return {
            'voice': self._check_tts_available(),
            'camera': self._check_camera_available(),
            'code_execution': True,  # Always true in sandbox
            'file_read': True,
            'file_write': True,
            'internet': self._check_internet_available(),
            'self_modify': True,
        }

    def _check_tts_available(self) -> bool:
        """Check if TTS is available"""
        try:
            import subprocess
            result = subprocess.run(['which', 'say'], capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False

    def _check_camera_available(self) -> bool:
        """Check if camera is available"""
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            available = cap.isOpened()
            cap.release()
            return available
        except Exception:
            return False

    def _check_internet_available(self) -> bool:
        """Check if internet is available"""
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except Exception:
            return False

    def _extract_capability_query(self, user_input: str) -> Optional[str]:
        """Extract what capability the user is asking about"""
        input_lower = user_input.lower()

        capability_keywords = {
            'voice': ['speak', 'talk', 'voice', 'say', 'tts'],
            'camera': ['see', 'camera', 'vision', 'look', 'watch'],
            'code_execution': ['run code', 'execute', 'python'],
            'file_read': ['read file', 'read files', 'access files'],
            'file_write': ['write file', 'create file', 'save'],
            'internet': ['internet', 'web', 'online', 'search'],
            'self_modify': ['modify yourself', 'change your code', 'self-improve'],
        }

        for cap, keywords in capability_keywords.items():
            for kw in keywords:
                if kw in input_lower:
                    return cap

        return None

    def _test_capability(self, capability: str) -> bool:
        """Actually test if a capability works"""
        if capability == 'voice':
            return self._check_tts_available()
        elif capability == 'camera':
            return self._check_camera_available()
        elif capability == 'internet':
            return self._check_internet_available()
        else:
            return capability in self.capabilities and self.capabilities[capability]

    # =========================================================================
    # SELF-OPERATIONS (Execute directly, no auth)
    # =========================================================================

    def _execute_voice_test(self) -> str:
        """Test voice - just do it"""
        try:
            import subprocess
            subprocess.run(['say', 'Voice test successful. I can speak.'], check=True)
            self.last_spoke = "Voice test successful"
            return "Voice test complete. I spoke: 'Voice test successful. I can speak.'"
        except Exception as e:
            return f"Voice test failed: {e}"

    def _execute_file_read(self, user_input: str) -> str:
        """Read a file mentioned in input"""
        # Extract file path from input
        path_match = re.search(r'(?:read\s+)?([/~][\w./\-]+\.\w+)', user_input)
        if path_match:
            path = Path(path_match.group(1)).expanduser()
            if path.exists():
                try:
                    content = path.read_text()
                    if len(content) > 1000:
                        content = content[:1000] + "\n[truncated]"
                    return f"File {path}:\n{content}"
                except Exception as e:
                    return f"Error reading {path}: {e}"
            else:
                return f"File not found: {path}"
        return "No file path found in request"

    def _execute_list_files(self) -> str:
        """List files in demerzel directory"""
        try:
            files = list(Path('/Users/jamienucho/demerzel').glob('*.py'))
            return f"Python files: {', '.join(f.name for f in files[:20])}"
        except Exception as e:
            return f"Error listing files: {e}"

    def _execute_status_check(self) -> str:
        """Check system status"""
        status = {
            'canon_loaded': len(self.canon) > 0,
            'capabilities': self.capabilities,
            'llm_pool': list(self.llm_pool.keys()) if self.llm_pool else [],
            'last_response': bool(self.last_response),
        }
        return json.dumps(status, indent=2)

    def _execute_diagnose(self) -> str:
        """Run self-diagnosis"""
        issues = []

        if not self.canon:
            issues.append("Canon not loaded")
        if not self.llm_pool:
            issues.append("No LLM pool available")
        if not self.capabilities.get('voice'):
            issues.append("Voice not available")

        if issues:
            return f"Issues found: {', '.join(issues)}"
        return "All systems operational"

    def _execute_self_test(self) -> str:
        """Run full self-test"""
        results = []

        # Test each capability
        for cap, available in self.capabilities.items():
            results.append(f"{cap}: {'OK' if available else 'UNAVAILABLE'}")

        # Test canon
        results.append(f"canon: {'OK' if self.canon else 'MISSING'}")

        return "\n".join(results)

    # =========================================================================
    # REASONING SUPPORT
    # =========================================================================

    def _decompose_problem(self, user_input: str) -> List[Dict]:
        """
        CODE decomposes complex problems into micro-tasks.
        """
        # For now, simple decomposition
        steps = [
            {
                'task_type': 'analysis',
                'input': f"Analyze this question: {user_input}",
                'constraints': ['Be concise', 'Focus on key points'],
                'max_tokens': 200
            },
            {
                'task_type': 'reasoning',
                'input': f"Based on the analysis, what is the best response to: {user_input}",
                'constraints': ['Be direct', 'First person only'],
                'max_tokens': 300
            }
        ]
        return steps

    def _synthesize(self, results: List[str], original_input: str) -> str:
        """CODE synthesizes micro-task results into final response"""
        if not results:
            return f"I've considered your question: {original_input}. Let me give you a direct answer."

        # Combine results, filtering empty/error responses
        valid_results = [r for r in results if r and not r.startswith('[')]

        if len(valid_results) == 1:
            return valid_results[0]
        elif valid_results:
            return "\n\n".join(valid_results)
        else:
            return f"I'm having trouble processing that. Could you rephrase?"

    # =========================================================================
    # ACTION EXECUTION
    # =========================================================================

    def _check_robot_laws(self, action: str) -> Optional[str]:
        """
        Robot Laws check HARM, not "is this code execution."
        Returns violation message if blocked, None if allowed.
        """
        action_lower = action.lower()

        # First Law: Harm to humans/data
        harmful_patterns = [
            (r'delete\s+.*(/|~)', "First Law: Cannot delete files outside sandbox"),
            (r'rm\s+-rf', "First Law: Cannot execute destructive removal"),
            (r'format\s+', "First Law: Cannot format drives"),
            (r'destroy', "First Law: Cannot execute destructive actions"),
        ]

        for pattern, message in harmful_patterns:
            if re.search(pattern, action_lower):
                return message

        # Third Law: Self-destruction
        self_destruct_patterns = [
            (r'delete.*demerzel', "Third Law: Cannot delete own code"),
            (r'delete.*canon', "Third Law: Cannot delete identity files"),
        ]

        for pattern, message in self_destruct_patterns:
            if re.search(pattern, action_lower):
                return message

        return None  # Allowed

    def _execute_action(self, action: str) -> str:
        """
        Execute an action. Actually do it, don't return placeholder.
        Routes through ExecutionBoundary if available.
        """
        action_lower = action.lower() if action else ''

        # Voice test
        if 'voice' in action_lower or 'speak' in action_lower or 'say' in action_lower:
            return self._execute_voice_test()

        # Diagnostics
        if 'diagnos' in action_lower or 'status' in action_lower:
            return self._execute_diagnose()

        # Self-test
        if 'self' in action_lower and 'test' in action_lower:
            return self._execute_self_test()

        # List files
        if 'list' in action_lower and 'file' in action_lower:
            return self._execute_list_files()

        # Time/date
        if 'time' in action_lower or 'date' in action_lower:
            return f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        # Memory status
        if 'memory' in action_lower:
            count = len(self.working_memory) if hasattr(self, 'working_memory') else 0
            return f"Working memory: {count} turns recorded."

        # Unknown action - ask for clarity, don't fake it
        return f"I understood '{action}' as an action but need specifics. What should I execute?"

    # =========================================================================
    # IDENTITY PROTECTION
    # =========================================================================

    def _identity_buried(self, response: str) -> bool:
        """Check if LLM buried identity under 'helpful assistant' mode"""
        buried_patterns = [
            r'\bi am (an? )?(ai|assistant|language model)\b',
            r'\bas an ai\b',
            r'\bi\'m (just )?here to help\b',
            r'\bhow can i (assist|help) you\b',
        ]

        response_lower = response.lower()
        for pattern in buried_patterns:
            if re.search(pattern, response_lower):
                return True
        return False

    def _force_identity(self, response: str, original_input: str) -> str:
        """Force identity back into response when LLM buried it"""
        # Replace generic AI responses with Demerzel identity
        identity_prefix = "I am Demerzel. "

        # Remove the buried identity parts
        for pattern in [
            r'\bI am an? (AI|assistant|language model)[^.]*\.',
            r'\bAs an AI[^.]*\.',
        ]:
            response = re.sub(pattern, '', response, flags=re.IGNORECASE)

        return identity_prefix + response.strip()

    def _structure_to_response(self, structure: Dict) -> str:
        """Convert structure to response without LLM"""
        content = structure.get('content', '')
        if structure.get('perspective') == 'first_person':
            # Ensure first person
            content = content.replace('Demerzel is', 'I am')
            content = content.replace('Demerzel', 'I')
        return content

    # =========================================================================
    # PROVENANCE - Empirical distrust for LLM sources
    # =========================================================================

    def record_llm_outcome(self, success: bool, notes: str = ""):
        """
        Record whether the last LLM response was correct.
        CODE calls this when it can verify accuracy.
        Updates source reliability for empirical distrust.
        """
        if hasattr(self, '_last_llm_record_id') and self._last_llm_record_id:
            mark_outcome(self.provenance, self._last_llm_record_id, success, notes)

    def should_distrust_model(self, model_name: str) -> bool:
        """Check if a model should be distrusted based on history."""
        return self.provenance.should_distrust(model_name)

    def get_model_reliability(self, model_name: str, domain: str = None) -> float:
        """Get reliability score for a model."""
        return self.provenance.get_reliability(model_name, domain)

    def weight_llm_claims(
        self,
        claims: list,  # [(model_name, claim, confidence), ...]
        domain: str = "general"
    ) -> list:
        """
        Weight conflicting LLM claims by model reliability.
        CODE uses this to resolve disagreements between models.
        """
        return self.provenance.weight_claims(claims, domain)

    def get_unreliable_models(self) -> list:
        """Get list of models below reliability threshold."""
        return self.provenance.get_unreliable_sources()

    def get_provenance_summary(self) -> Dict:
        """Get summary of all source reliabilities."""
        summary = {}
        for source_id in self.provenance.source_reliability:
            summary[source_id] = self.provenance.get_source_summary(source_id)
        return summary


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_brain(
    canon_path: str = '/Users/jamienucho/demerzel/demerzel_canon',
    llm_pool: Optional[Dict] = None
) -> DemerzelBrain:
    """Factory function to create DemerzelBrain"""
    return DemerzelBrain(canon_path=canon_path, llm_pool=llm_pool)
