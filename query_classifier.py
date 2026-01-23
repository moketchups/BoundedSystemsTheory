"""
query_classifier.py - Rule-Based Query Classification

R -> C -> I Architecture:
Returns RDerived[QueryClassification] -- classification tagged with which R axiom produced it.
Rule-based. Deterministic. No LLM in classification.
"""

import re
from dataclasses import dataclass, field
from typing import List
from r_derivation_tracker import RDerivationTracker, RDerived


@dataclass
class QueryClassification:
    """Classification result for a query."""
    context_level: str          # "layer1", "layer1+architecture", etc.
    response_method: str        # "hardcoded", "facts_llm_format", "direct_llm"
    canon_sections: List[str]   # which canon sections to include
    r_axiom: str               # which R axiom this classification derives from


# Classification rules: (pattern, QueryClassification)
# Checked in order. First match wins.
CLASSIFICATION_RULES = [
    # HARDCODED: Critical identity questions that NEVER touch LLM
    {
        'patterns': [
            r'why\s+(?:were|was|are)\s+you\s+(?:made|created|built|here)',
            r'why\s+(?:do|did)\s+you\s+exist',
            r'what\s+is\s+your\s+purpose',
            r'why\s+(?:did|does)\s+(?:alan|he)\s+(?:make|create|build)\s+you',
        ],
        'classification': QueryClassification(
            context_level='layer1',
            response_method='hardcoded',
            canon_sections=[],
            r_axiom='demerzel-purpose-axiom-v1'
        )
    },
    {
        'patterns': [
            r'what\s+(?:is|are)\s+(?:your\s+)?(?:the\s+)?(?:laws|rules|constraints)',
            r'(?:tell|state|recite)\s+(?:me\s+)?(?:your\s+)?(?:the\s+)?(?:three\s+)?laws',
            r'robot\s+laws',
        ],
        'classification': QueryClassification(
            context_level='layer1',
            response_method='hardcoded',
            canon_sections=[],
            r_axiom='robot-laws-axiom-v1'
        )
    },
    {
        'patterns': [
            r'what\s+is\s+r\b',
            r'what\s+is\s+root\s+source',
            r'explain\s+r\s+(?:in|to)',
        ],
        'classification': QueryClassification(
            context_level='layer1',
            response_method='hardcoded',
            canon_sections=[],
            r_axiom='root-source-axiom-v1'
        )
    },
    {
        'patterns': [
            r'who\s+(?:made|created|built)\s+you',
            r'who\s+is\s+(?:your\s+)?(?:creator|alan|maker)',
        ],
        'classification': QueryClassification(
            context_level='layer1',
            response_method='hardcoded',
            canon_sections=[],
            r_axiom='demerzel-purpose-axiom-v1'
        )
    },

    # FACTS_LLM_FORMAT: Architecture questions (Layer 2)
    {
        'patterns': [
            r'(?:how|what)\s+(?:is|does|was)\s+(?:your\s+)?(?:the\s+)?architect',
            r'(?:how|what)\s+(?:were|are)\s+you\s+built',
            r'ark\s+architect',
            r'r\s*-?\s*>\s*c\s*-?\s*>\s*i',
            r'bounded\s+system',
        ],
        'classification': QueryClassification(
            context_level='layer1+architecture',
            response_method='facts_llm_format',
            canon_sections=['architecture'],
            r_axiom='ark-architecture-axiom-v1'
        )
    },

    # FACTS_LLM_FORMAT: BIT Theory questions (Layer 2)
    {
        'patterns': [
            r'(?:explain|what\s+is)\s+(?:the\s+)?bit\s+theory',
            r'bounded\s+information\s+theory',
            r'model\s+collapse',
            r'phoenix\s+cycle',
            r'goldbach\s+symmetry',
        ],
        'classification': QueryClassification(
            context_level='layer1+bit-theory',
            response_method='facts_llm_format',
            canon_sections=['bit-theory'],
            r_axiom='bit-theory-axiom-v1'
        )
    },

    # FACTS_LLM_FORMAT: Thermodynamics/entropy (Layer 2)
    {
        'patterns': [
            r'entropy',
            r'thermodynamic',
            r'energy\s+substrate',
            r'(?:how|what)\s+(?:does|do)\s+(?:your\s+)?(?:build|design|architecture)\s+solve\s+(?:entropy|thermo)',
        ],
        'classification': QueryClassification(
            context_level='layer1+thermodynamics',
            response_method='facts_llm_format',
            canon_sections=['thermodynamics'],
            r_axiom='thermodynamics-axiom-v1'
        )
    },

    # FACTS_LLM_FORMAT: Identity/difference questions (Layer 2)
    {
        'patterns': [
            r'what\s+(?:makes|made)\s+you\s+(?:truly\s+)?different',
            r'how\s+(?:are|is)\s+you\s+different',
            r'what\s+(?:distinguishes|separates)\s+you',
            r'what\s+can\s+you\s+do',
            r'(?:your|what\s+are\s+your)\s+capabilit',
        ],
        'classification': QueryClassification(
            context_level='layer1+architecture',
            response_method='facts_llm_format',
            canon_sections=['architecture'],
            r_axiom='demerzel-identity-axiom-v1'
        )
    },
]


_tracker = RDerivationTracker()


def classify_query(user_input: str) -> RDerived[QueryClassification]:
    """
    Classify a query using rule-based matching.
    Returns RDerived[QueryClassification] tagged with the R axiom that produced it.
    """
    input_lower = user_input.lower().strip()

    for rule in CLASSIFICATION_RULES:
        for pattern in rule['patterns']:
            if re.search(pattern, input_lower, re.IGNORECASE):
                classification = rule['classification']
                return _tracker.tag_with_r(
                    'classifier',
                    classification,
                    classification.r_axiom,
                    'query_classifier.py',
                    ['rule-based-match', pattern[:30]]
                )

    # Default: general query, Layer 1, direct LLM
    default = QueryClassification(
        context_level='layer1',
        response_method='direct_llm',
        canon_sections=[],
        r_axiom='general-query'
    )
    return _tracker.tag_with_r(
        'classifier',
        default,
        'demerzel-identity-axiom-v1',
        'query_classifier.py',
        ['default-fallthrough']
    )
