"""
response_validator.py - LLM Response Validation

R -> C -> I Architecture:
Validates LLM-formatted responses contain ONLY source facts.
If any check fails, provides CODE-formatted fallback from raw facts.
"""

import re
from dataclasses import dataclass, field
from typing import List


@dataclass
class ValidationResult:
    """Result of response validation."""
    valid: bool
    violations: List[str]
    fallback_response: str  # CODE-formatted from facts if invalid


# Style violations: phrases that indicate LLM filler
STYLE_VIOLATIONS = [
    r"i'?d be happy to",
    r"great question",
    r"that'?s a (?:great|good|interesting|wonderful) question",
    r"absolutely",
    r"certainly",
    r"of course",
    r"let me (?:explain|help|tell)",
    r"i hope (?:this|that) helps",
]


def validate(source_facts: List[str], llm_response: str) -> ValidationResult:
    """
    Validate that LLM response contains ONLY source facts.

    Validation chain:
    1. Fact extraction check - Are response claims traceable to source facts?
    2. No-addition check - Is anything in response NOT in source facts?
    3. Style preservation - Technical, precise (no filler)
    4. Fallback ready - If any check fails, CODE formatting from raw facts
    """
    violations = []
    response_lower = llm_response.lower()

    # Build word set from source facts for overlap checking
    fact_words = set()
    for fact in source_facts:
        for word in re.findall(r'\b\w{4,}\b', fact.lower()):
            fact_words.add(word)

    # 1. Fact extraction check: response words should mostly come from facts
    response_words = set(re.findall(r'\b\w{4,}\b', response_lower))
    if response_words:
        overlap = len(response_words & fact_words) / len(response_words)
        if overlap < 0.3:
            violations.append(f"Low fact overlap ({overlap:.0%}): response contains significant content not in source facts")

    # 2. No-addition check: detect sentences with no fact-word overlap
    response_sentences = re.split(r'[.!?]+', llm_response)
    for sentence in response_sentences:
        sentence = sentence.strip()
        if len(sentence) < 10:
            continue
        sentence_words = set(re.findall(r'\b\w{4,}\b', sentence.lower()))
        if sentence_words:
            sent_overlap = len(sentence_words & fact_words) / len(sentence_words)
            if sent_overlap < 0.2 and len(sentence_words) > 3:
                violations.append(f"Added content: '{sentence[:60]}...'")

    # 3. Style preservation: no LLM filler
    for pattern in STYLE_VIOLATIONS:
        if re.search(pattern, response_lower):
            violations.append(f"Style violation: LLM filler detected ('{pattern}')")

    # Build fallback response
    fallback = _code_format_facts(source_facts)

    if violations:
        return ValidationResult(valid=False, violations=violations, fallback_response=fallback)
    return ValidationResult(valid=True, violations=[], fallback_response=fallback)


def _code_format_facts(facts: List[str]) -> str:
    """CODE-format facts into a clean response."""
    if not facts:
        return "No source facts available."
    # Join first 5 facts into a coherent response
    clean_facts = []
    for fact in facts[:5]:
        # Strip formatting markers
        clean = fact.strip().lstrip('- ').strip()
        if clean and len(clean) > 10:
            clean_facts.append(clean)
    return ' '.join(clean_facts) if clean_facts else facts[0]
