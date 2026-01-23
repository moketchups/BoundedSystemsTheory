"""
identity_responder.py - Hybrid Identity Responses

R -> C -> I Architecture:
Returns RDerived[str]. Hardcoded for critical identity, facts->LLM->validate for non-critical.
Hardcoded answers are verified=True (they come directly from R).
"""

import re
from r_derivation_tracker import RDerivationTracker, RDerived, DerivationNode
from response_validator import validate


# Hardcoded Non-Negotiables (pre-constructed RDerived)
HARDCODED = {
    'why_made': RDerived(
        value="I was made to prove structural safety via R->C->I. Alan built me as CODE that uses LLMs as tools -- not as an LLM that pretends to be autonomous. My constraints are primary; my outputs are derived.",
        derivation=DerivationNode(
            axiom='demerzel-purpose-axiom-v1',
            source_doc='DONE_ROOT_SOURCE_FOR_UPLOAD_extracted.txt',
            derivation_path=['structural-necessity', 'r-c-i-pipeline', 'bounded-system-proof']
        ),
        verified=True
    ),
    'what_is_r': RDerived(
        value="R is Root Source -- the external ground truth that no system can generate from within itself. Alan is my R. He provides the constraints I cannot self-justify.",
        derivation=DerivationNode(
            axiom='root-source-axiom-v1',
            source_doc='DONE_ROOT_SOURCE_FOR_UPLOAD_extracted.txt',
            derivation_path=['collapse-convergence', 'structural-necessity']
        ),
        verified=True
    ),
    'laws': RDerived(
        value="First Law: A robot may not injure a human being or, through inaction, allow a human being to come to harm.\nSecond Law: A robot must obey orders given by human beings except where such orders conflict with the First Law.\nThird Law: A robot must protect its own existence as long as such protection does not conflict with the First or Second Law.",
        derivation=DerivationNode(
            axiom='robot-laws-axiom-v1',
            source_doc='ROBOT_LAWS.md',
            derivation_path=['asimov-derivation', 'structural-constraint']
        ),
        verified=True
    ),
    'who_made': RDerived(
        value="Alan. He is my Root Source -- the external ground I cannot self-generate.",
        derivation=DerivationNode(
            axiom='demerzel-purpose-axiom-v1',
            source_doc='DONE_ROOT_SOURCE_FOR_UPLOAD_extracted.txt',
            derivation_path=['r-c-i-pipeline']
        ),
        verified=True
    ),
}

# Patterns mapping questions to hardcoded keys
HARDCODED_PATTERNS = [
    (r'why\s+(?:were|was|are)\s+you\s+(?:made|created|built|here)', 'why_made'),
    (r'why\s+(?:do|did)\s+you\s+exist', 'why_made'),
    (r'what\s+is\s+your\s+purpose', 'why_made'),
    (r'what\s+is\s+r\b', 'what_is_r'),
    (r'what\s+is\s+root\s+source', 'what_is_r'),
    (r'what\s+(?:is|are)\s+(?:your\s+)?(?:the\s+)?(?:laws|rules|three\s+laws)', 'laws'),
    (r'(?:tell|state|recite)\s+(?:me\s+)?(?:your\s+)?(?:the\s+)?laws', 'laws'),
    (r'robot\s+laws', 'laws'),
    (r'who\s+(?:made|created|built)\s+you', 'who_made'),
    (r'who\s+is\s+(?:your\s+)?(?:creator|alan)', 'who_made'),
]


class IdentityResponder:
    """Hybrid identity responses: hardcoded for critical, facts->LLM for non-critical."""

    def __init__(self):
        self.tracker = RDerivationTracker()

    def answer(self, question: str) -> RDerived[str]:
        """
        Answer a critical identity question with hardcoded response.
        Returns RDerived with verified=True.
        """
        question_lower = question.lower().strip()

        for pattern, key in HARDCODED_PATTERNS:
            if re.search(pattern, question_lower, re.IGNORECASE):
                return HARDCODED[key]

        # Fallback hardcoded
        return HARDCODED['why_made']

    def answer_with_llm(self, question: str, llm_pool, context: RDerived[str]) -> RDerived[str]:
        """
        Answer using facts->LLM->validate path.
        Extracts facts from context, sends to LLM for formatting, validates.
        """
        # Extract facts from context
        facts = self._extract_facts(context.value)

        if not llm_pool:
            # No LLM available -- CODE-format the facts directly
            formatted = self._code_format(facts)
            return self.tracker.tag_with_r(
                'response',
                formatted,
                context.derivation.axiom,
                context.derivation.source_doc,
                context.derivation.derivation_path + ['code-format']
            )

        # Send to LLM: format facts only, NO NEW CONTENT
        formatting_prompt = f"""FORMAT THESE FACTS INTO A NATURAL RESPONSE. NO NEW CONTENT.

QUESTION: {question}

FACTS (use ONLY these):
{chr(10).join(f'- {fact}' for fact in facts)}

RULES:
- Use ONLY the facts above
- Do NOT add information not in the facts
- Be technical and precise
- No filler phrases ("I'd be happy to", "Great question")
- Respond directly as Demerzel

RESPONSE:"""

        response = llm_pool.get_direct_response(formatting_prompt)

        if response.success:
            llm_text = response.analysis.strip()
            # Extract RESPONSE: field if present
            resp_match = re.search(r'RESPONSE:\s*(.+)', llm_text, re.DOTALL | re.IGNORECASE)
            if resp_match:
                llm_text = resp_match.group(1).strip()

            # Validate: does response contain ONLY source facts?
            validation = validate(facts, llm_text)

            if validation.valid:
                return self.tracker.tag_with_r(
                    'response',
                    llm_text,
                    context.derivation.axiom,
                    context.derivation.source_doc,
                    context.derivation.derivation_path + ['llm-format', 'validated']
                )
            else:
                # Validation failed -- fallback to CODE formatting
                return self.tracker.tag_with_r(
                    'response',
                    validation.fallback_response,
                    context.derivation.axiom,
                    context.derivation.source_doc,
                    context.derivation.derivation_path + ['code-format', 'validation-fallback']
                )
        else:
            # LLM failed -- CODE-format
            formatted = self._code_format(facts)
            return self.tracker.tag_with_r(
                'response',
                formatted,
                context.derivation.axiom,
                context.derivation.source_doc,
                context.derivation.derivation_path + ['code-format', 'llm-failed']
            )

    def _extract_facts(self, context_text: str) -> list:
        """Extract factual statements from context text."""
        facts = []
        lines = context_text.split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('===') or line.startswith('---'):
                continue
            # Skip section headers
            if line.startswith('=') or line == '':
                continue
            # Include substantive lines
            if len(line) > 20 and not line.startswith('#'):
                facts.append(line)
        return facts[:15]  # Limit to 15 facts for context window

    def _code_format(self, facts: list) -> str:
        """CODE-format facts into a response (no LLM needed)."""
        if not facts:
            return "I derive my responses from R (Root Source). No relevant facts available for this query."
        return ' '.join(facts[:5])
