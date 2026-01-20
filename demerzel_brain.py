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


class DemerzelBrain:
    """
    The actual reasoning engine. CODE thinks. LLMs execute.

    This is THE Demerzel. LLMs are interchangeable tools.
    """

    def __init__(
        self,
        canon_path: str = 'demerzel_canon/',
        llm_pool: Optional[Dict[str, Any]] = None
    ):
        self.canon_path = Path(canon_path)
        self.llm_pool = llm_pool or {}
        self.canon = self._load_canon()
        self.capabilities = self._inspect_capabilities()
        self.state = {}

        # Track what we've done
        self.last_response = None
        self.last_spoke = None

        print(f"[BRAIN] Initialized. Canon loaded: {len(self.canon)} bytes")
        print(f"[BRAIN] Capabilities: {list(self.capabilities.keys())}")

    # =========================================================================
    # MAIN ENTRY POINT
    # =========================================================================

    def process(self, user_input: str) -> str:
        """
        CODE processes input. CODE decides response.
        LLMs only used for language micro-tasks.
        """
        # 1. CODE classifies intent
        intent = self._classify_intent(user_input)
        print(f"[BRAIN] Intent: {intent.type.value}")

        # 2. CODE routes to handler (not LLM)
        if intent.type == IntentType.IDENTITY:
            return self._handle_identity(user_input, intent)
        elif intent.type == IntentType.CAPABILITY:
            return self._handle_capability(user_input, intent)
        elif intent.type == IntentType.SELF_OPERATION:
            return self._handle_self_operation(user_input, intent)
        elif intent.type == IntentType.REASONING:
            return self._handle_reasoning(user_input, intent)
        elif intent.type == IntentType.ACTION:
            return self._handle_action(user_input, intent)
        else:
            return self._handle_conversation(user_input, intent)

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
        Identity questions answered FROM canon, not ABOUT canon.
        LLM only polishes language - never chooses content.
        """
        # CODE extracts relevant canon content
        relevant = self._extract_canon_for_identity(user_input)

        # CODE builds response structure
        response_structure = {
            'perspective': 'first_person',
            'content': relevant,
            'tone': 'direct',
            'forbidden': ['according to', 'the document', 'the system',
                          'as stated in', 'based on my canon']
        }

        # LLM micro-task: convert structure to natural language
        if self.llm_pool:
            response = self._llm_micro_task(
                task='structure_to_language',
                structure=response_structure,
                constraints=[
                    'You ARE Demerzel. First person only.',
                    'Never say "according to" or cite documents.',
                    'Embody the content, do not explain it.',
                    'Be direct and confident.',
                ]
            )
        else:
            # No LLM available - return structured response directly
            response = self._structure_to_response(response_structure)

        self.last_response = response
        return response

    def _handle_capability(self, user_input: str, intent: Intent) -> str:
        """
        Capability questions answered by CODE inspecting itself.
        LLM not consulted - it would lie based on training.
        """
        # CODE checks actual capabilities
        caps = self.capabilities

        # CODE determines what user is asking about
        asked_about = self._extract_capability_query(user_input)

        # CODE builds factual response
        if asked_about and asked_about in caps:
            can_do = caps[asked_about]
            if can_do:
                response = f"I can {asked_about}. "
                if intent.wants_execution:
                    response += "Executing now."
            else:
                response = f"I cannot currently {asked_about}. The capability is not available."
        elif asked_about:
            # Try to test it
            response = f"Let me check if I can {asked_about}."
            result = self._test_capability(asked_about)
            response = f"I {'can' if result else 'cannot'} {asked_about}."
        else:
            # General capability question - list what we can do
            can_do_list = [k for k, v in caps.items() if v]
            response = f"I can: {', '.join(can_do_list)}."

        return response

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
        General conversation: CODE maintains identity, LLM generates language.
        """
        # Build context for LLM (heavy constraints)
        context = self._build_constrained_context(user_input)

        if self.llm_pool:
            # LLM generates BUT within tight constraints
            response = self._llm_micro_task(
                task='conversation',
                input=user_input,
                context=context,
                constraints=[
                    'You ARE Demerzel. First person only.',
                    'Never say "according to" or cite documents.',
                    'Never ask permission. Propose or do.',
                    'Never explain yourself in third person.',
                    'If uncertain, say so directly. Do not hedge with questions.'
                ]
            )

            # CODE validates identity preserved
            if self._identity_buried(response):
                response = self._force_identity(response, user_input)
        else:
            # No LLM - basic response
            response = f"I understand you're saying: {user_input}. Let me address that directly."

        self.last_response = response
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
        """Execute an action"""
        # For now, basic action handling
        # In production, this would route to code_executor
        return f"Action '{action}' would be executed here"

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


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_brain(
    canon_path: str = '/Users/jamienucho/demerzel/demerzel_canon',
    llm_pool: Optional[Dict] = None
) -> DemerzelBrain:
    """Factory function to create DemerzelBrain"""
    return DemerzelBrain(canon_path=canon_path, llm_pool=llm_pool)
