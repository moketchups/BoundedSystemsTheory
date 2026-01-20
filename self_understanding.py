"""
SELF UNDERSTANDING - INWARD Research Module for Demerzel
Part of Demerzel's Autonomous Conversational Competency System

This module handles questions about Demerzel's identity, purpose, and architecture.
She CANNOT google "what am I" - she must read her own documentation.

Canon Document Registry:
- Identity: Who she is (DEMERZEL_IDENTITY.md, DEMERZEL_CHARTER.md)
- Architecture: How she's built (DEMERZEL_COMPLETE_CONTEXT_DOC.md, R→C→I)
- Constraints: What limits her (ROBOT_LAWS.md, EXECUTION_SAFETY_CONTRACT.md)
- Theory: Why she exists (Zenodo papers, Ark Architecture)

Architecture: CODE searches canon, CODE synthesizes answers.
LLMs may polish language but never decide content about identity.
"""

import re
from datetime import datetime
from typing import Optional, Dict, List, Any
from pathlib import Path


# =============================================================================
# CANON DOCUMENT REGISTRY
# =============================================================================

CANON_DOCUMENTS = {
    # Core Identity - Who she is
    'identity': [
        'DEMERZEL_IDENTITY.md',
        'DEMERZEL_CHARTER.md',
    ],
    # Architecture & Purpose - How she's built
    'architecture': [
        'demerzel_canon/_archive_20260119/DEMERZEL_COMPLETE_CONTEXT_DOC.md',
        'NORTH_STAR.md',
        'GROUNDING_SPINE.md',
    ],
    # Constraints - What limits her
    'constraints': [
        'ROBOT_LAWS.md',
        'EXECUTION_SAFETY_CONTRACT.md',
        'ROUTER_INVARIANTS.md',
    ],
    # Theoretical Foundation - Why she exists
    'theory': [
        'demerzel_canon/Zenodo_Paper_extracted.txt',
        'demerzel_canon/Ark Architecture and LLM Patents_extracted.txt',
        'demerzel_canon/DONE ROOT SOURCE FOR UPLOAD_extracted.txt',
        'demerzel_canon/Researching Bounded Systems Theory (1)_extracted.txt',
    ],
    # Operational Knowledge - How she should behave
    'operations': [
        'FATHERS_LESSONS.md',
        'GROUNDING_EXCERPTS.md',
    ],
}

# Patterns that indicate questions about self
IDENTITY_PATTERNS = {
    'who_am_i': [
        r"who\s+(am\s+i|are\s+you)",
        r"what\s+(am\s+i|are\s+you)",
        r"tell\s+me\s+about\s+(yourself|you)",
        r"describe\s+(yourself|you)",
    ],
    'purpose': [
        r"what\s+is\s+(my|your)\s+(purpose|goal|mission)",
        r"why\s+do\s+(i|you)\s+exist",
        r"what\s+(am\s+i|are\s+you)\s+for",
    ],
    'origin': [
        r"why\s+(was\s+i|were\s+you)\s+(built|created|made)",
        r"who\s+(built|created|made)\s+(me|you)",
        r"where\s+do\s+(i|you)\s+come\s+from",
        r"alan\s+(built|created|made)",
    ],
    'constraints': [
        r"what\s+are\s+(my|your)\s+constraints",
        r"what\s+can('t|\s+not)\s+(i|you)\s+do",
        r"(my|your)\s+limitations",
        r"robot\s+laws",
    ],
    'architecture': [
        r"(explain|describe)\s+(my|your)\s+(architecture|design|structure)",
        r"how\s+(am\s+i|are\s+you)\s+(built|designed|structured)",
        r"(r|root)\s*→?\s*c\s*→?\s*i",
        r"bounded\s+system",
        r"ark\s+architecture",
    ],
}


class SelfUnderstanding:
    """
    Demerzel's ability to understand HERSELF.
    This is ALWAYS inward research - never web search.
    """

    def __init__(self, demerzel_dir: str = "/Users/jamienucho/demerzel"):
        self.demerzel_dir = Path(demerzel_dir)
        self.canon_cache: Dict[str, List[Dict]] = {}
        self._load_canon()

    def _load_canon(self):
        """Load all canon documents into memory for fast access."""
        print("[SELF] Loading canon documents...")
        total_loaded = 0

        for category, paths in CANON_DOCUMENTS.items():
            self.canon_cache[category] = []

            for path in paths:
                full_path = self.demerzel_dir / path
                if full_path.exists():
                    try:
                        content = full_path.read_text()
                        self.canon_cache[category].append({
                            'path': path,
                            'content': content,
                            'size': len(content),
                        })
                        total_loaded += 1
                    except Exception as e:
                        print(f"[SELF] Error loading {path}: {e}")
                else:
                    # Try without archive path
                    alt_path = self.demerzel_dir / path.replace('demerzel_canon/_archive_20260119/', 'demerzel_canon/')
                    if alt_path.exists():
                        try:
                            content = alt_path.read_text()
                            self.canon_cache[category].append({
                                'path': path,
                                'content': content,
                                'size': len(content),
                            })
                            total_loaded += 1
                        except Exception as e:
                            print(f"[SELF] Error loading {alt_path}: {e}")

        print(f"[SELF] Loaded {total_loaded} canon documents")

    def is_self_question(self, user_input: str) -> bool:
        """Check if this is a question about Demerzel's identity/purpose."""
        input_lower = user_input.lower()

        for category, patterns in IDENTITY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, input_lower):
                    return True

        return False

    def classify_self_question(self, user_input: str) -> str:
        """Classify what aspect of self the question is about."""
        input_lower = user_input.lower()

        for category, patterns in IDENTITY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, input_lower):
                    # Map question type to canon category
                    if category in ['who_am_i', 'purpose']:
                        return 'identity'
                    elif category == 'origin':
                        return 'theory'
                    elif category == 'constraints':
                        return 'constraints'
                    elif category == 'architecture':
                        return 'architecture'

        return 'identity'  # Default to identity

    def answer_self_question(self, user_input: str, context: Dict = None) -> str:
        """
        Answer a question about self by reading canon.
        This is how Demerzel knows who she is.
        """
        # Classify the question
        category = self.classify_self_question(user_input)
        print(f"[SELF] Question category: {category}")

        # Search relevant canon documents
        relevant = self._search_canon(category, user_input)

        if relevant:
            # Synthesize answer from canon
            answer = self._synthesize_from_canon(relevant, user_input, category)
            return answer
        else:
            return "I should know this about myself, but I cannot find it in my canon. This may indicate a gap in my documentation."

    def _search_canon(self, category: str, query: str) -> List[Dict]:
        """Search canon documents for relevant content."""
        docs = self.canon_cache.get(category, [])

        # If specific category is empty, also check identity and theory
        if not docs:
            docs = self.canon_cache.get('identity', []) + self.canon_cache.get('theory', [])

        results = []
        query_words = set(query.lower().split())

        for doc in docs:
            relevant = self._extract_relevant_sections(doc['content'], query_words)
            if relevant:
                results.append({
                    'source': doc['path'],
                    'content': relevant,
                })

        return results

    def _extract_relevant_sections(self, content: str, query_words: set) -> str:
        """Extract sections relevant to the query from canon document."""
        # Remove very common words
        stopwords = {'i', 'you', 'the', 'a', 'an', 'is', 'are', 'was', 'what', 'who', 'why', 'how', 'my', 'your', 'me'}
        query_words = query_words - stopwords

        if not query_words:
            # If no meaningful query words, return document summary
            return content[:500]

        # Split into sections (by headers)
        sections = re.split(r'\n#{1,3}\s+', content)

        # Score each section by keyword relevance
        scored = []
        for section in sections:
            if len(section.strip()) < 20:
                continue

            section_words = set(section.lower().split())
            overlap = len(query_words & section_words)

            if overlap > 0:
                scored.append((overlap, section))

        if not scored:
            # No direct matches, return first substantive section
            for section in sections:
                if len(section.strip()) > 100:
                    return section[:800]
            return content[:500]

        # Return top relevant sections
        scored.sort(reverse=True, key=lambda x: x[0])
        relevant = [s[1] for s in scored[:3]]

        return '\n\n---\n\n'.join(relevant)[:2000]

    def _synthesize_from_canon(self, sources: List[Dict], query: str, category: str) -> str:
        """
        Synthesize an answer from canon sources.
        CODE determines the structure, this formats it.
        """
        if not sources:
            return "I could not find relevant information in my canon."

        # For identity questions, use direct quotes from canon
        if category == 'identity':
            return self._format_identity_answer(sources)
        elif category == 'constraints':
            return self._format_constraints_answer(sources)
        elif category == 'architecture':
            return self._format_architecture_answer(sources)
        elif category == 'theory':
            return self._format_theory_answer(sources)
        else:
            return self._format_general_answer(sources)

    def _format_identity_answer(self, sources: List[Dict]) -> str:
        """Format answer about identity."""
        # Look for key identity statements
        content = ' '.join([s['content'] for s in sources])

        key_statements = []

        # Extract "You are..." or "I am..." statements
        patterns = [
            r"You are ([^.]+\.)",
            r"I am ([^.]+\.)",
            r"Demerzel is ([^.]+\.)",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            key_statements.extend(matches[:2])

        if key_statements:
            # Build answer from key statements
            answer = "Based on my canon: "
            answer += " ".join(key_statements[:3])
            return answer

        # Fallback: return relevant excerpt
        return f"From my documentation: {sources[0]['content'][:300]}..."

    def _format_constraints_answer(self, sources: List[Dict]) -> str:
        """Format answer about constraints."""
        content = ' '.join([s['content'] for s in sources])

        # Look for Robot Laws or constraint statements
        if 'robot law' in content.lower() or 'first law' in content.lower():
            # Extract the laws
            laws = []
            law_patterns = [
                r"(First Law[^.]+\.)",
                r"(Second Law[^.]+\.)",
                r"(Third Law[^.]+\.)",
            ]
            for pattern in law_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    laws.append(match.group(1))

            if laws:
                return "My constraints are the Robot Laws:\n- " + "\n- ".join(laws)

        return f"My constraints are defined in: {sources[0]['source']}\n{sources[0]['content'][:400]}..."

    def _format_architecture_answer(self, sources: List[Dict]) -> str:
        """Format answer about architecture."""
        content = ' '.join([s['content'] for s in sources])

        # Look for R→C→I or architecture description
        if 'r→c→i' in content.lower() or 'root' in content.lower():
            # Find the description
            rci_pattern = r"(R.*?→.*?C.*?→.*?I[^.]*\.)"
            match = re.search(rci_pattern, content)
            if match:
                return f"My architecture follows R→C→I: {match.group(1)}"

        return f"My architecture: {sources[0]['content'][:400]}..."

    def _format_theory_answer(self, sources: List[Dict]) -> str:
        """Format answer about theoretical foundation."""
        content = sources[0]['content'][:500] if sources else ""
        source_name = sources[0]['source'] if sources else "unknown"

        return f"From the theoretical foundation ({source_name}):\n{content}..."

    def _format_general_answer(self, sources: List[Dict]) -> str:
        """Format general answer from canon."""
        if not sources:
            return "I could not find relevant information."

        content = sources[0]['content'][:400]
        return f"From my documentation: {content}..."

    def get_canon_summary(self, category: str) -> str:
        """Get a summary of canon documents in a category."""
        docs = self.canon_cache.get(category, [])

        if not docs:
            return f"No canon documents found for category: {category}"

        summary_lines = [f"Canon documents for '{category}':"]
        for doc in docs:
            summary_lines.append(f"  - {doc['path']} ({doc['size']} chars)")

        return '\n'.join(summary_lines)

    def refresh_canon(self):
        """Reload canon documents (if they've been updated)."""
        self._load_canon()


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def handle_self_question(user_input: str, demerzel_dir: str = "/Users/jamienucho/demerzel") -> Optional[str]:
    """
    Convenience function: Check if self-question and answer from canon.
    Returns answer if self-question, None otherwise.
    """
    self_understanding = SelfUnderstanding(demerzel_dir)

    if self_understanding.is_self_question(user_input):
        return self_understanding.answer_self_question(user_input)

    return None


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    print("=== Testing Self Understanding Module ===\n")

    self_understanding = SelfUnderstanding()

    # Test cases
    test_questions = [
        "Who am I?",
        "What is my purpose?",
        "Why was I built?",
        "What are my constraints?",
        "Explain my architecture",
        "What are the robot laws?",
        "What is R→C→I?",
    ]

    for question in test_questions:
        print(f"Q: {question}")

        if self_understanding.is_self_question(question):
            category = self_understanding.classify_self_question(question)
            print(f"   Category: {category}")
            answer = self_understanding.answer_self_question(question)
            print(f"   A: {answer[:200]}...")
        else:
            print("   Not a self-question")

        print()

    print("\n=== Canon Summary ===")
    for category in CANON_DOCUMENTS.keys():
        print(self_understanding.get_canon_summary(category))
        print()
