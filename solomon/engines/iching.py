"""
I Ching Oracle

Entropy measurement system with H ≈ 1.75 bits per line.
Uses yarrow stalk probability distribution (non-uniform).

Line values:
- 6 (Old Yin): 1/16 probability - changing yin
- 7 (Young Yang): 5/16 probability - stable yang
- 8 (Young Yin): 7/16 probability - stable yin
- 9 (Old Yang): 3/16 probability - changing yang
"""

import random
import math
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from ..core.bus import ThreeSixNine


class IChingOracle:
    """
    I Ching oracle implementing yarrow stalk probability distribution.

    Entropy per line: H ≈ 1.749 bits (vs 2 bits for uniform)
    Total hexagram entropy: H ≈ 10.5 bits (vs 12 bits for uniform)
    """

    # Yarrow stalk probabilities
    PROBABILITIES = {
        6: 1/16,   # Old Yin (changing)
        7: 5/16,   # Young Yang (stable)
        8: 7/16,   # Young Yin (stable)
        9: 3/16,   # Old Yang (changing)
    }

    # Line properties
    LINE_PROPERTIES = {
        6: {"yin_yang": "yin", "changing": True, "symbol": "---x---", "name": "Old Yin"},
        7: {"yin_yang": "yang", "changing": False, "symbol": "-------", "name": "Young Yang"},
        8: {"yin_yang": "yin", "changing": False, "symbol": "--- ---", "name": "Young Yin"},
        9: {"yin_yang": "yang", "changing": True, "symbol": "---o---", "name": "Old Yang"},
    }

    # Hexagram data (King Wen sequence)
    HEXAGRAMS = {
        1: {"name": "Qian", "english": "The Creative", "trigrams": ("Heaven", "Heaven")},
        2: {"name": "Kun", "english": "The Receptive", "trigrams": ("Earth", "Earth")},
        3: {"name": "Zhun", "english": "Difficulty at the Beginning", "trigrams": ("Water", "Thunder")},
        4: {"name": "Meng", "english": "Youthful Folly", "trigrams": ("Mountain", "Water")},
        5: {"name": "Xu", "english": "Waiting", "trigrams": ("Water", "Heaven")},
        6: {"name": "Song", "english": "Conflict", "trigrams": ("Heaven", "Water")},
        7: {"name": "Shi", "english": "The Army", "trigrams": ("Earth", "Water")},
        8: {"name": "Bi", "english": "Holding Together", "trigrams": ("Water", "Earth")},
        9: {"name": "Xiao Chu", "english": "Small Taming", "trigrams": ("Wind", "Heaven")},
        10: {"name": "Lu", "english": "Treading", "trigrams": ("Heaven", "Lake")},
        11: {"name": "Tai", "english": "Peace", "trigrams": ("Earth", "Heaven")},
        12: {"name": "Pi", "english": "Standstill", "trigrams": ("Heaven", "Earth")},
        13: {"name": "Tong Ren", "english": "Fellowship", "trigrams": ("Heaven", "Fire")},
        14: {"name": "Da You", "english": "Great Possession", "trigrams": ("Fire", "Heaven")},
        15: {"name": "Qian", "english": "Modesty", "trigrams": ("Earth", "Mountain")},
        16: {"name": "Yu", "english": "Enthusiasm", "trigrams": ("Thunder", "Earth")},
        17: {"name": "Sui", "english": "Following", "trigrams": ("Lake", "Thunder")},
        18: {"name": "Gu", "english": "Work on the Decayed", "trigrams": ("Mountain", "Wind")},
        19: {"name": "Lin", "english": "Approach", "trigrams": ("Earth", "Lake")},
        20: {"name": "Guan", "english": "Contemplation", "trigrams": ("Wind", "Earth")},
        21: {"name": "Shi He", "english": "Biting Through", "trigrams": ("Fire", "Thunder")},
        22: {"name": "Bi", "english": "Grace", "trigrams": ("Mountain", "Fire")},
        23: {"name": "Bo", "english": "Splitting Apart", "trigrams": ("Mountain", "Earth")},
        24: {"name": "Fu", "english": "Return", "trigrams": ("Earth", "Thunder")},
        25: {"name": "Wu Wang", "english": "Innocence", "trigrams": ("Heaven", "Thunder")},
        26: {"name": "Da Chu", "english": "Great Taming", "trigrams": ("Mountain", "Heaven")},
        27: {"name": "Yi", "english": "Nourishment", "trigrams": ("Mountain", "Thunder")},
        28: {"name": "Da Guo", "english": "Great Exceeding", "trigrams": ("Lake", "Wind")},
        29: {"name": "Kan", "english": "The Abysmal", "trigrams": ("Water", "Water")},
        30: {"name": "Li", "english": "The Clinging", "trigrams": ("Fire", "Fire")},
        31: {"name": "Xian", "english": "Influence", "trigrams": ("Lake", "Mountain")},
        32: {"name": "Heng", "english": "Duration", "trigrams": ("Thunder", "Wind")},
        33: {"name": "Dun", "english": "Retreat", "trigrams": ("Heaven", "Mountain")},
        34: {"name": "Da Zhuang", "english": "Great Power", "trigrams": ("Thunder", "Heaven")},
        35: {"name": "Jin", "english": "Progress", "trigrams": ("Fire", "Earth")},
        36: {"name": "Ming Yi", "english": "Darkening of the Light", "trigrams": ("Earth", "Fire")},
        37: {"name": "Jia Ren", "english": "The Family", "trigrams": ("Wind", "Fire")},
        38: {"name": "Kui", "english": "Opposition", "trigrams": ("Fire", "Lake")},
        39: {"name": "Jian", "english": "Obstruction", "trigrams": ("Water", "Mountain")},
        40: {"name": "Xie", "english": "Deliverance", "trigrams": ("Thunder", "Water")},
        41: {"name": "Sun", "english": "Decrease", "trigrams": ("Mountain", "Lake")},
        42: {"name": "Yi", "english": "Increase", "trigrams": ("Wind", "Thunder")},
        43: {"name": "Guai", "english": "Breakthrough", "trigrams": ("Lake", "Heaven")},
        44: {"name": "Gou", "english": "Coming to Meet", "trigrams": ("Heaven", "Wind")},
        45: {"name": "Cui", "english": "Gathering Together", "trigrams": ("Lake", "Earth")},
        46: {"name": "Sheng", "english": "Pushing Upward", "trigrams": ("Earth", "Wind")},
        47: {"name": "Kun", "english": "Oppression", "trigrams": ("Lake", "Water")},
        48: {"name": "Jing", "english": "The Well", "trigrams": ("Water", "Wind")},
        49: {"name": "Ge", "english": "Revolution", "trigrams": ("Lake", "Fire")},
        50: {"name": "Ding", "english": "The Cauldron", "trigrams": ("Fire", "Wind")},
        51: {"name": "Zhen", "english": "The Arousing", "trigrams": ("Thunder", "Thunder")},
        52: {"name": "Gen", "english": "Keeping Still", "trigrams": ("Mountain", "Mountain")},
        53: {"name": "Jian", "english": "Development", "trigrams": ("Wind", "Mountain")},
        54: {"name": "Gui Mei", "english": "The Marrying Maiden", "trigrams": ("Thunder", "Lake")},
        55: {"name": "Feng", "english": "Abundance", "trigrams": ("Thunder", "Fire")},
        56: {"name": "Lu", "english": "The Wanderer", "trigrams": ("Fire", "Mountain")},
        57: {"name": "Xun", "english": "The Gentle", "trigrams": ("Wind", "Wind")},
        58: {"name": "Dui", "english": "The Joyous", "trigrams": ("Lake", "Lake")},
        59: {"name": "Huan", "english": "Dispersion", "trigrams": ("Wind", "Water")},
        60: {"name": "Jie", "english": "Limitation", "trigrams": ("Water", "Lake")},
        61: {"name": "Zhong Fu", "english": "Inner Truth", "trigrams": ("Wind", "Lake")},
        62: {"name": "Xiao Guo", "english": "Small Exceeding", "trigrams": ("Thunder", "Mountain")},
        63: {"name": "Ji Ji", "english": "After Completion", "trigrams": ("Water", "Fire")},
        64: {"name": "Wei Ji", "english": "Before Completion", "trigrams": ("Fire", "Water")},
    }

    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
        self.bus = ThreeSixNine()

    def cast_line(self) -> int:
        """Cast a single line using yarrow stalk probability distribution."""
        r = random.random()
        cumulative = 0
        for value, prob in self.PROBABILITIES.items():
            cumulative += prob
            if r < cumulative:
                return value
        return 8  # Fallback (shouldn't reach)

    def cast_hexagram(self, question: Optional[str] = None) -> Dict:
        """
        Cast a full hexagram (6 lines).

        Returns complete reading with primary hexagram, changing lines,
        and resulting hexagram if there are changes.
        """
        lines = [self.cast_line() for _ in range(6)]

        # Convert to binary for hexagram lookup
        primary_binary = self._lines_to_binary(lines)
        primary_number = self._binary_to_hexagram_number(primary_binary)

        # Find changing lines and compute resulting hexagram
        changing_positions = [i + 1 for i, line in enumerate(lines) if line in (6, 9)]
        has_changes = len(changing_positions) > 0

        if has_changes:
            # Transform old yin (6) to yang, old yang (9) to yin
            transformed = []
            for line in lines:
                if line == 6:
                    transformed.append(7)  # Old yin becomes young yang
                elif line == 9:
                    transformed.append(8)  # Old yang becomes young yin
                else:
                    transformed.append(line)
            resulting_binary = self._lines_to_binary(transformed)
            resulting_number = self._binary_to_hexagram_number(resulting_binary)
        else:
            resulting_number = None

        # Calculate entropy
        entropy_bits = self._calculate_entropy(lines)

        # Build result
        result = {
            "question": question,
            "lines": lines,
            "line_details": [self.LINE_PROPERTIES[l] for l in lines],
            "primary_hexagram": {
                "number": primary_number,
                **self.HEXAGRAMS.get(primary_number, {"name": "Unknown", "english": "Unknown"})
            },
            "changing_lines": changing_positions,
            "has_changes": has_changes,
            "entropy": {
                "bits": entropy_bits,
                "theoretical_max": 12.0,
                "yarrow_expected": 10.494,
                "interpretation": self._interpret_entropy(entropy_bits)
            }
        }

        if resulting_number:
            result["resulting_hexagram"] = {
                "number": resulting_number,
                **self.HEXAGRAMS.get(resulting_number, {"name": "Unknown", "english": "Unknown"})
            }

        # 3-6-9 analysis
        result["three_six_nine"] = {
            "primary": self.bus.classify_value(primary_number),
            "lines_sum": sum(lines),
            "lines_sum_analysis": self.bus.classify_value(sum(lines))
        }

        result["interpretation"] = self._interpret_reading(result)

        return result

    def _lines_to_binary(self, lines: List[int]) -> str:
        """Convert line values to binary string (yin=0, yang=1)."""
        binary = ""
        for line in lines:
            if line in (6, 8):  # Yin
                binary += "0"
            else:  # Yang (7, 9)
                binary += "1"
        return binary

    def _binary_to_hexagram_number(self, binary: str) -> int:
        """
        Convert binary representation to King Wen hexagram number.
        This requires the lookup table mapping binary to King Wen sequence.
        """
        # Binary to decimal (lower trigram first)
        decimal = int(binary, 2)
        # Map to King Wen number (simplified - actual mapping is complex)
        # For now, use a direct mapping table
        binary_to_king_wen = self._get_binary_mapping()
        return binary_to_king_wen.get(binary, decimal + 1)

    def _get_binary_mapping(self) -> Dict[str, int]:
        """Get binary string to King Wen number mapping."""
        # This is the actual Fu Xi to King Wen mapping
        return {
            "111111": 1, "000000": 2, "010001": 3, "100010": 4,
            "010111": 5, "111010": 6, "000010": 7, "010000": 8,
            "110111": 9, "111011": 10, "000111": 11, "111000": 12,
            "111101": 13, "101111": 14, "000100": 15, "001000": 16,
            "011001": 17, "100110": 18, "000011": 19, "110000": 20,
            "101001": 21, "100101": 22, "100000": 23, "000001": 24,
            "111001": 25, "100111": 26, "100001": 27, "011110": 28,
            "010010": 29, "101101": 30, "011100": 31, "001110": 32,
            "111100": 33, "001111": 34, "101000": 35, "000101": 36,
            "110101": 37, "101011": 38, "010100": 39, "001010": 40,
            "100011": 41, "110001": 42, "011111": 43, "111110": 44,
            "011000": 45, "000110": 46, "011010": 47, "010110": 48,
            "011101": 49, "101110": 50, "001001": 51, "100100": 52,
            "110100": 53, "001011": 54, "001101": 55, "101100": 56,
            "110110": 57, "011011": 58, "110010": 59, "010011": 60,
            "110011": 61, "001100": 62, "010101": 63, "101010": 64,
        }

    def _calculate_entropy(self, lines: List[int]) -> float:
        """Calculate actual entropy of the cast lines."""
        # Shannon entropy based on yarrow probabilities
        entropy = 0
        for line in lines:
            p = self.PROBABILITIES[line]
            entropy -= p * math.log2(p) if p > 0 else 0
        return round(entropy, 3)

    def _interpret_entropy(self, bits: float) -> str:
        """Interpret entropy value."""
        if bits < 9:
            return "Low entropy - highly determined state"
        elif bits < 10:
            return "Below expected - some constraint present"
        elif bits < 11:
            return "Normal range - typical yarrow distribution"
        else:
            return "High entropy - significant uncertainty"

    def _interpret_reading(self, result: Dict) -> str:
        """Generate natural language interpretation."""
        primary = result["primary_hexagram"]
        parts = [f"Hexagram {primary['number']}: {primary['english']} ({primary['name']})"]

        if result["has_changes"]:
            positions = result["changing_lines"]
            parts.append(f"Changing lines at position(s): {', '.join(map(str, positions))}")
            resulting = result["resulting_hexagram"]
            parts.append(f"Transforms to: {resulting['english']} ({resulting['name']})")

        domain = result["three_six_nine"]["primary"]["domain"]
        if domain == "unity":
            parts.append("3-6-9: Unity domain - complete alignment")
        elif domain == "flux":
            parts.append("3-6-9: Flux domain - transition in progress")
        else:
            parts.append("3-6-9: Material domain - grounded for action")

        return " | ".join(parts)

    @staticmethod
    def calculate_theoretical_entropy() -> Dict:
        """Calculate theoretical entropy of yarrow stalk distribution."""
        h_line = 0
        for value, p in IChingOracle.PROBABILITIES.items():
            if p > 0:
                h_line -= p * math.log2(p)

        return {
            "entropy_per_line": round(h_line, 4),
            "entropy_per_hexagram": round(h_line * 6, 4),
            "fair_coin_per_line": 1.0,
            "fair_coin_per_hexagram": 6.0,
            "four_outcome_max_per_line": 2.0,
            "four_outcome_max_per_hexagram": 12.0,
            "information_lost_to_structure": round(12 - h_line * 6, 4)
        }
