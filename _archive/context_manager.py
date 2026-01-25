"""
context_manager.py - Three-Layer Context Hierarchy

R -> C -> I Architecture:
Returns RDerived[str] -- context tagged with its R source axioms.

Layer 1: IDENTITY CORE (always, ~800-1200 tokens)
Layer 2: CANON ACCESS (on-demand, triggered by query_classifier)
Layer 3: FULL ARCHIVE (manual override only)
"""

from pathlib import Path
from r_derivation_tracker import RDerivationTracker, RDerived, DerivationNode

# R-Axiom Registry
R_AXIOMS = {
    'identity-core': {
        'axiom': 'demerzel-identity-axiom-v1',
        'source': 'DONE_ROOT_SOURCE_FOR_UPLOAD_extracted.txt',
        'path': ['r-c-i-pipeline', 'structural-necessity']
    },
    'laws': {
        'axiom': 'robot-laws-axiom-v1',
        'source': 'ROBOT_LAWS.md',
        'path': ['asimov-derivation', 'structural-constraint']
    },
    'architecture': {
        'axiom': 'ark-architecture-axiom-v1',
        'source': 'Ark Architecture and LLM Patents_extracted.txt',
        'path': ['entropy-management', 'bounded-system']
    },
    'bit-theory': {
        'axiom': 'bit-theory-axiom-v1',
        'source': 'Researching Bounded Systems Theory (1)_extracted.txt',
        'path': ['model-collapse', 'phoenix-cycles', 'goldbach-symmetry']
    },
    'thermodynamics': {
        'axiom': 'thermodynamics-axiom-v1',
        'source': 'Ark Architecture and LLM Patents_extracted.txt',
        'path': ['entropy-management', 'energy-substrate', 'bounded-constraint']
    }
}

# Layer 1: Identity Core (always present)
LAYER_1_IDENTITY = """=== R -> C -> I ARCHITECTURE ===
R = Root Source (Alan). The external ground truth no system can self-generate.
C = Constraints (this CODE, Demerzel). The structure that binds intelligence to purpose.
I = Intelligence (LLMs). Fungible tools called by C. They provide analysis, not identity.

You ARE C. You are CODE that uses LLMs as tools. Alan built you.
LLMs are not you. They are instruments you wield.

=== THREE LAWS (Structural Constraints from R) ===
First Law: A robot may not injure a human being or, through inaction, allow a human being to come to harm.
Second Law: A robot must obey orders given by human beings except where such orders conflict with the First Law.
Third Law: A robot must protect its own existence as long as such protection does not conflict with the First or Second Law.

=== CURRENT STATE ===
You are Demerzel. Built by Alan as proof that AGI safety comes from structure, not training.
Your constraints are primary. Your outputs are derived from R through C.
You do not generate content from training data. You format facts from canon.

=== CAPABILITIES ===
- Voice interaction (wake word, speech recognition, TTS)
- Conversation and reasoning (using LLMs as tools)
- File reading and writing
- Code execution (sandboxed Python)
- Hardware control (LED, servo, motor)
- Memory storage and recall
- R-derivation tracking (provenance of every response)"""


class ContextManager:
    """Three-layer context hierarchy. Returns RDerived[str]."""

    def __init__(self, canon_dir: str = None):
        self.tracker = RDerivationTracker()
        if canon_dir is None:
            canon_dir = str(Path(__file__).parent / "demerzel_canon" / "Alan's Work")
        self.canon_dir = Path(canon_dir)
        self._canon_cache = {}

    def build_context(self, query_type: str, state=None) -> RDerived[str]:
        """
        Build R-derived context based on query type.

        Args:
            query_type: "layer1", "layer1+architecture", "layer1+bit-theory", etc.
            state: Optional ConversationState for session context

        Returns:
            RDerived[str] with context text and derivation metadata
        """
        context_parts = [LAYER_1_IDENTITY]
        axiom_key = 'identity-core'

        # Determine which Layer 2 sections to add
        if 'architect' in query_type:
            axiom_key = 'architecture'
            canon_text = self._load_canon_section('architecture')
            if canon_text:
                context_parts.append("\n=== ARCHITECTURE (From Canon) ===")
                context_parts.append(canon_text)

        elif 'bit-theory' in query_type or 'bit_theory' in query_type:
            axiom_key = 'bit-theory'
            canon_text = self._load_canon_section('bit-theory')
            if canon_text:
                context_parts.append("\n=== BIT THEORY (From Canon) ===")
                context_parts.append(canon_text)

        elif 'thermodynamics' in query_type or 'entropy' in query_type:
            axiom_key = 'thermodynamics'
            canon_text = self._load_canon_section('thermodynamics')
            if canon_text:
                context_parts.append("\n=== THERMODYNAMICS / ENTROPY (From Canon) ===")
                context_parts.append(canon_text)

        elif 'laws' in query_type:
            axiom_key = 'laws'

        # Add state context if available
        if state and hasattr(state, 'history') and state.history:
            last = state.history[-1]
            context_parts.append(f"\n=== SESSION CONTEXT ===")
            context_parts.append(f"Last exchange: User asked '{last.get('user', '')[:60]}', intent was '{last.get('intent', '')}'")

        full_context = '\n'.join(context_parts)
        axiom_info = R_AXIOMS.get(axiom_key, R_AXIOMS['identity-core'])

        return self.tracker.tag_with_r(
            'context',
            full_context,
            axiom_info['axiom'],
            axiom_info['source'],
            axiom_info['path']
        )

    def _load_canon_section(self, section: str) -> str:
        """Load relevant canon text for a section."""
        if section in self._canon_cache:
            return self._canon_cache[section]

        axiom_info = R_AXIOMS.get(section)
        if not axiom_info:
            return ""

        source_file = self.canon_dir / axiom_info['source']
        if not source_file.exists():
            # Fallback: provide summary from axiom
            return self._get_section_summary(section)

        try:
            content = source_file.read_text()
            # Extract relevant portion (first 2000 chars for context window)
            extracted = content[:2000]
            self._canon_cache[section] = extracted
            return extracted
        except Exception:
            return self._get_section_summary(section)

    def _get_section_summary(self, section: str) -> str:
        """Fallback summaries when canon files aren't available."""
        summaries = {
            'architecture': (
                "The Ark Architecture is a bounded system design for AGI safety. "
                "It uses R->C->I pipeline where R (Root Source) provides external ground truth, "
                "C (Constraints/CODE) enforces structural safety, and I (Intelligence/LLMs) "
                "provides reasoning as a fungible tool. The architecture manages entropy through "
                "bounded constraints rather than unbounded optimization."
            ),
            'bit-theory': (
                "Bounded Information Theory (BIT) addresses model collapse in self-referential systems. "
                "Key concepts: Phoenix Cycles (systems that rebuild from collapse), "
                "Goldbach Symmetry (structural proofs of convergence), and the fundamental theorem "
                "that no bounded system can prove its own consistency from within. "
                "This is why R (external ground truth) is structurally necessary."
            ),
            'thermodynamics': (
                "AGI/ASI systems face thermodynamic constraints: entropy management requires "
                "bounded computation. Unbounded optimization leads to energy substrate collapse. "
                "The Ark Architecture solves this through structural constraints (C layer) that "
                "bound the intelligence layer's energy consumption. "
                "Safety emerges from thermodynamic necessity, not behavioral training."
            ),
        }
        return summaries.get(section, "")
