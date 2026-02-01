"""
231 Gates Navigator

The complete graph K₂₂ on 22 Hebrew letters.
C(22,2) = 231 edges = gates.

Properties (verified by 5 demons):
- All vertices have degree 21 (odd)
- No Eulerian path exists
- Minimum traversal: 231 + 11 = 242 edge crossings
- 3-7-12 partition: Mothers, Doubles, Simples
"""

from typing import Dict, List, Optional, Set, Tuple
from itertools import combinations
from ..core.bus import ThreeSixNine


class GatesNavigator:
    """
    Navigate the 231 Gates of Sefer Yetzirah.

    The 22 Hebrew letters form a complete graph K₂₂.
    Each edge is a "gate" - a transition between states.
    """

    # The 22 Hebrew letters in traditional order
    LETTERS = [
        'א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט', 'י', 'כ',
        'ל', 'מ', 'נ', 'ס', 'ע', 'פ', 'צ', 'ק', 'ר', 'ש', 'ת'
    ]

    # Final forms mapping (sofit letters) → regular forms
    FINAL_FORMS = {
        'ך': 'כ',  # final kaf
        'ם': 'מ',  # final mem
        'ן': 'נ',  # final nun
        'ף': 'פ',  # final pe
        'ץ': 'צ',  # final tsade
    }

    # Letter classifications (Sefer Yetzirah)
    MOTHERS = {'א', 'מ', 'ש'}  # 3 - Elements: Air, Water, Fire
    DOUBLES = {'ב', 'ג', 'ד', 'כ', 'פ', 'ר', 'ת'}  # 7 - Planets, Opposites
    SIMPLES = {'ה', 'ו', 'ז', 'ח', 'ט', 'י', 'ל', 'נ', 'ס', 'ע', 'צ', 'ק'}  # 12 - Zodiac

    @classmethod
    def normalize_letter(cls, letter: str) -> str:
        """Convert final forms to regular forms."""
        return cls.FINAL_FORMS.get(letter, letter)

    # Letter meanings and correspondences
    CORRESPONDENCES = {
        # Mothers (Elements)
        'א': {"name": "Aleph", "meaning": "Ox", "element": "Air", "category": "mother"},
        'מ': {"name": "Mem", "meaning": "Water", "element": "Water", "category": "mother"},
        'ש': {"name": "Shin", "meaning": "Tooth", "element": "Fire", "category": "mother"},
        # Doubles (Planets)
        'ב': {"name": "Bet", "meaning": "House", "planet": "Saturn", "category": "double"},
        'ג': {"name": "Gimel", "meaning": "Camel", "planet": "Jupiter", "category": "double"},
        'ד': {"name": "Dalet", "meaning": "Door", "planet": "Mars", "category": "double"},
        'כ': {"name": "Kaf", "meaning": "Palm", "planet": "Sun", "category": "double"},
        'פ': {"name": "Pe", "meaning": "Mouth", "planet": "Venus", "category": "double"},
        'ר': {"name": "Resh", "meaning": "Head", "planet": "Mercury", "category": "double"},
        'ת': {"name": "Tav", "meaning": "Mark", "planet": "Moon", "category": "double"},
        # Simples (Zodiac)
        'ה': {"name": "He", "meaning": "Window", "zodiac": "Aries", "category": "simple"},
        'ו': {"name": "Vav", "meaning": "Hook", "zodiac": "Taurus", "category": "simple"},
        'ז': {"name": "Zayin", "meaning": "Weapon", "zodiac": "Gemini", "category": "simple"},
        'ח': {"name": "Chet", "meaning": "Fence", "zodiac": "Cancer", "category": "simple"},
        'ט': {"name": "Tet", "meaning": "Serpent", "zodiac": "Leo", "category": "simple"},
        'י': {"name": "Yod", "meaning": "Hand", "zodiac": "Virgo", "category": "simple"},
        'ל': {"name": "Lamed", "meaning": "Goad", "zodiac": "Libra", "category": "simple"},
        'נ': {"name": "Nun", "meaning": "Fish", "zodiac": "Scorpio", "category": "simple"},
        'ס': {"name": "Samekh", "meaning": "Prop", "zodiac": "Sagittarius", "category": "simple"},
        'ע': {"name": "Ayin", "meaning": "Eye", "zodiac": "Capricorn", "category": "simple"},
        'צ': {"name": "Tsade", "meaning": "Hook", "zodiac": "Aquarius", "category": "simple"},
        'ק': {"name": "Qof", "meaning": "Needle", "zodiac": "Pisces", "category": "simple"},
    }

    def __init__(self):
        self.bus = ThreeSixNine()
        self._build_graph()

    def _build_graph(self):
        """Build the K₂₂ complete graph."""
        self.gates: Dict[Tuple[str, str], int] = {}
        gate_num = 1
        for i, letter1 in enumerate(self.LETTERS):
            for letter2 in self.LETTERS[i+1:]:
                # Store both orderings pointing to same gate
                self.gates[(letter1, letter2)] = gate_num
                self.gates[(letter2, letter1)] = gate_num
                gate_num += 1

    def get_letter_info(self, letter: str) -> Dict:
        """Get full information about a letter."""
        if letter not in self.CORRESPONDENCES:
            return {"error": f"Unknown letter: {letter}"}

        info = self.CORRESPONDENCES[letter].copy()
        info["letter"] = letter
        info["index"] = self.LETTERS.index(letter) + 1
        info["connections"] = 21  # K₂₂ means each vertex connects to all others

        # 3-6-9 classification of letter index
        info["three_six_nine"] = self.bus.classify_value(info["index"])

        return info

    def get_gate(self, letter1: str, letter2: str) -> Dict:
        """Get information about a specific gate (edge between two letters)."""
        if letter1 not in self.LETTERS or letter2 not in self.LETTERS:
            return {"error": "Invalid letter(s)"}

        if letter1 == letter2:
            return {"error": "A gate connects two different letters"}

        # Normalize order
        key = tuple(sorted([letter1, letter2]))
        gate_num = self.gates.get((key[0], key[1]))

        info1 = self.CORRESPONDENCES[letter1]
        info2 = self.CORRESPONDENCES[letter2]

        # Determine gate type based on letter categories
        cat1 = info1["category"]
        cat2 = info2["category"]

        if cat1 == cat2:
            gate_type = f"intra-{cat1}"
        else:
            gate_type = f"{cat1}-{cat2}"

        return {
            "gate_number": gate_num,
            "letters": [letter1, letter2],
            "letter1_info": info1,
            "letter2_info": info2,
            "gate_type": gate_type,
            "three_six_nine": self.bus.classify_value(gate_num),
            "interpretation": self._interpret_gate(letter1, letter2, info1, info2)
        }

    def _interpret_gate(self, l1: str, l2: str, info1: Dict, info2: Dict) -> str:
        """Generate interpretation for a gate."""
        parts = [f"Gate {l1}-{l2}: {info1['name']}-{info2['name']}"]

        # Category relationship
        if info1["category"] == info2["category"]:
            parts.append(f"Both {info1['category']}s - same domain")
        else:
            parts.append(f"{info1['category'].title()} to {info2['category'].title()} - cross-domain")

        # Specific correspondences
        if "element" in info1:
            parts.append(f"{info1['element']}")
        elif "planet" in info1:
            parts.append(f"{info1['planet']}")
        elif "zodiac" in info1:
            parts.append(f"{info1['zodiac']}")

        if "element" in info2:
            parts.append(f"to {info2['element']}")
        elif "planet" in info2:
            parts.append(f"to {info2['planet']}")
        elif "zodiac" in info2:
            parts.append(f"to {info2['zodiac']}")

        return " | ".join(parts)

    def get_transitions(self, letter: str) -> Dict:
        """Get all possible transitions from a letter (all 21 connected gates)."""
        if letter not in self.LETTERS:
            return {"error": f"Unknown letter: {letter}"}

        transitions = []
        for other in self.LETTERS:
            if other != letter:
                gate = self.get_gate(letter, other)
                transitions.append({
                    "to": other,
                    "gate_number": gate["gate_number"],
                    "gate_type": gate["gate_type"]
                })

        return {
            "from": letter,
            "from_info": self.get_letter_info(letter),
            "transition_count": 21,
            "transitions": transitions
        }

    def find_path(self, start: str, end: str) -> Dict:
        """
        Find path between two letters.
        In K₂₂, any two letters are directly connected (1 step),
        but we can also find meaningful multi-step paths.
        """
        if start not in self.LETTERS or end not in self.LETTERS:
            return {"error": "Invalid letter(s)"}

        if start == end:
            return {"error": "Start and end must be different"}

        # Direct path (always exists in complete graph)
        direct_gate = self.get_gate(start, end)

        # Find category-respecting path if different categories
        start_info = self.CORRESPONDENCES[start]
        end_info = self.CORRESPONDENCES[end]

        paths = [{
            "type": "direct",
            "path": [start, end],
            "gates": [direct_gate["gate_number"]],
            "length": 1
        }]

        # If different categories, find path through intermediary
        if start_info["category"] != end_info["category"]:
            # Find a letter that shares category with neither
            categories = {"mother", "double", "simple"}
            other_cat = categories - {start_info["category"], end_info["category"]}
            if other_cat:
                other_cat = other_cat.pop()
                # Pick first letter of that category
                for letter in self.LETTERS:
                    if self.CORRESPONDENCES[letter]["category"] == other_cat:
                        gate1 = self.get_gate(start, letter)
                        gate2 = self.get_gate(letter, end)
                        paths.append({
                            "type": "via_third_category",
                            "path": [start, letter, end],
                            "gates": [gate1["gate_number"], gate2["gate_number"]],
                            "length": 2,
                            "via_category": other_cat
                        })
                        break

        return {
            "start": start,
            "end": end,
            "start_info": start_info,
            "end_info": end_info,
            "paths": paths,
            "note": "In K₂₂, all letters directly connect. Multi-step paths are symbolic."
        }

    def analyze_word(self, word: str) -> Dict:
        """
        Analyze a word as a path through the gates.
        Each consecutive letter pair is a gate traversal.
        """
        # Normalize final forms and filter to Hebrew letters
        letters = []
        for c in word:
            normalized = self.normalize_letter(c)
            if normalized in self.LETTERS:
                letters.append(normalized)

        if len(letters) < 2:
            return {"error": "Need at least 2 Hebrew letters"}

        traversals = []
        gates_used = []

        for i in range(len(letters) - 1):
            gate = self.get_gate(letters[i], letters[i+1])
            traversals.append({
                "from": letters[i],
                "to": letters[i+1],
                "gate": gate["gate_number"],
                "type": gate["gate_type"]
            })
            gates_used.append(gate["gate_number"])

        # 3-6-9 analysis of path
        gates_sum = sum(gates_used)

        return {
            "word": word,
            "letters": letters,
            "path_length": len(letters) - 1,
            "traversals": traversals,
            "gates_used": gates_used,
            "unique_gates": len(set(gates_used)),
            "three_six_nine": {
                "gates_sum": gates_sum,
                "analysis": self.bus.classify_value(gates_sum)
            }
        }

    def graph_stats(self) -> Dict:
        """Return statistics about the K₂₂ graph."""
        # Count gates by type
        intra_mother = 3  # C(3,2)
        intra_double = 21  # C(7,2)
        intra_simple = 66  # C(12,2)
        mother_double = 3 * 7  # 21
        mother_simple = 3 * 12  # 36
        double_simple = 7 * 12  # 84

        total = intra_mother + intra_double + intra_simple + mother_double + mother_simple + double_simple

        return {
            "vertices": 22,
            "edges": 231,
            "vertex_degree": 21,
            "is_complete": True,
            "has_eulerian_path": False,
            "reason": "All 22 vertices have odd degree (21)",
            "minimum_traversal": 242,
            "partition": {
                "mothers": 3,
                "doubles": 7,
                "simples": 12
            },
            "gate_counts": {
                "intra_mother": intra_mother,
                "intra_double": intra_double,
                "intra_simple": intra_simple,
                "mother_double": mother_double,
                "mother_simple": mother_simple,
                "double_simple": double_simple,
                "total": total
            },
            "verification": total == 231
        }
