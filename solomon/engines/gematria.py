"""
Gematria Engine

Hash function H: Σ* → ℤ mapping strings to integers.
Supports Hebrew (traditional) and English (simple ordinal).

Properties:
- Deterministic: same input always produces same output
- Not collision-resistant: intentional collisions encode semantic relationships
- Digital root reduction reveals 3-6-9 classification
"""

from typing import Dict, List, Optional, Tuple
from ..core.bus import ThreeSixNine


class GematriaEngine:
    """
    Gematria computation engine.

    Supports multiple methods:
    - Hebrew standard (mispar hechrachi)
    - Hebrew ordinal (mispar siduri)
    - English simple (A=1, B=2, ...)
    - English full (A=1, B=2, ... Z=26, then 27, 28, ...)
    """

    # Hebrew letter values (standard gematria)
    HEBREW_VALUES = {
        'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9,
        'י': 10, 'כ': 20, 'ל': 30, 'מ': 40, 'נ': 50, 'ס': 60, 'ע': 70, 'פ': 80, 'צ': 90,
        'ק': 100, 'ר': 200, 'ש': 300, 'ת': 400,
        # Final forms
        'ך': 20, 'ם': 40, 'ן': 50, 'ף': 80, 'ץ': 90,
        # Alternative final form values (some traditions)
        # 'ך': 500, 'ם': 600, 'ן': 700, 'ף': 800, 'ץ': 900,
    }

    # Hebrew ordinal values (1-22)
    HEBREW_ORDINAL = {
        'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9,
        'י': 10, 'כ': 11, 'ל': 12, 'מ': 13, 'נ': 14, 'ס': 15, 'ע': 16, 'פ': 17, 'צ': 18,
        'ק': 19, 'ר': 20, 'ש': 21, 'ת': 22,
        'ך': 11, 'ם': 13, 'ן': 14, 'ף': 17, 'ץ': 18,
    }

    # Known sacred word values (for collision lookup)
    SACRED_WORDS = {
        13: ["אחד (Echad/One)", "אהבה (Ahava/Love)"],
        26: ["יהוה (YHVH/Tetragrammaton)"],
        72: ["חסד (Chesed/Mercy)"],
        86: ["אלהים (Elohim/God)"],
        314: ["שדי (Shaddai/Almighty)"],
        358: ["משיח (Mashiach/Messiah)", "נחש (Nachash/Serpent)"],
        541: ["ישראל (Israel)"],
    }

    def __init__(self):
        self.bus = ThreeSixNine()

    def compute_hebrew(self, text: str, method: str = "standard") -> Dict:
        """
        Compute gematria value for Hebrew text.

        Args:
            text: Hebrew string
            method: "standard" or "ordinal"

        Returns:
            Full analysis including value, digital root, domain
        """
        values = self.HEBREW_VALUES if method == "standard" else self.HEBREW_ORDINAL

        total = 0
        breakdown = []
        for char in text:
            if char in values:
                val = values[char]
                total += val
                breakdown.append((char, val))

        return self._build_result(text, total, breakdown, f"hebrew_{method}")

    def compute_english(self, text: str, method: str = "simple") -> Dict:
        """
        Compute gematria value for English text.

        Args:
            text: English string
            method: "simple" (A=1..Z=26) or "ordinal" (same as simple)

        Returns:
            Full analysis
        """
        total = 0
        breakdown = []
        for char in text.upper():
            if 'A' <= char <= 'Z':
                val = ord(char) - ord('A') + 1
                total += val
                breakdown.append((char, val))

        return self._build_result(text, total, breakdown, f"english_{method}")

    def compute(self, text: str) -> Dict:
        """
        Auto-detect language and compute gematria.
        """
        # Check if primarily Hebrew
        hebrew_chars = sum(1 for c in text if c in self.HEBREW_VALUES)
        english_chars = sum(1 for c in text.upper() if 'A' <= c <= 'Z')

        if hebrew_chars > english_chars:
            return self.compute_hebrew(text)
        else:
            return self.compute_english(text)

    def _build_result(
        self,
        text: str,
        total: int,
        breakdown: List[Tuple[str, int]],
        method: str
    ) -> Dict:
        """Build the full result dictionary."""
        dr = ThreeSixNine.digital_root(total)
        classification = ThreeSixNine.classify_value(total)

        # Check for known sacred word collisions
        collisions = self.SACRED_WORDS.get(total, [])

        return {
            "input": text,
            "method": method,
            "value": total,
            "breakdown": breakdown,
            "digital_root": dr,
            "domain": classification["domain"],
            "interpretation": classification["interpretation"],
            "collisions": collisions,
            "analysis": self._interpret(total, dr, collisions)
        }

    def _interpret(self, value: int, dr: int, collisions: List[str]) -> str:
        """Generate natural language interpretation."""
        parts = [f"Gematria value: {value}"]
        parts.append(f"Digital root: {dr}")

        if dr == 9:
            parts.append("Unity domain - complete, aligned.")
        elif dr in (3, 6):
            parts.append("Flux domain - transitional, mediating.")
        else:
            parts.append("Material domain - grounded, actionable.")

        if collisions:
            parts.append(f"Shares value with: {', '.join(collisions)}")

        return " ".join(parts)

    def find_collisions(self, value: int) -> List[str]:
        """Find known words with the same gematria value."""
        return self.SACRED_WORDS.get(value, [])

    def compare(self, text1: str, text2: str) -> Dict:
        """Compare gematria of two texts."""
        result1 = self.compute(text1)
        result2 = self.compute(text2)

        return {
            "text1": result1,
            "text2": result2,
            "same_value": result1["value"] == result2["value"],
            "same_digital_root": result1["digital_root"] == result2["digital_root"],
            "same_domain": result1["domain"] == result2["domain"],
            "sum": result1["value"] + result2["value"],
            "sum_dr": ThreeSixNine.digital_root(result1["value"] + result2["value"])
        }
