"""
Biological Decoder

Dermatoglyphics (fingerprint/palm patterns) as genetic markers.
Scientific validation: Down syndrome detection, chromosomal abnormalities.

Pattern categories:
- Loops (ulnar/radial)
- Whorls
- Arches (plain/tented)
- Composites

Ridge count and pattern correlation with genetic traits.
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
from ..core.bus import ThreeSixNine


class PatternType(Enum):
    """Dermatoglyphic pattern types"""
    ARCH_PLAIN = "arch_plain"
    ARCH_TENTED = "arch_tented"
    LOOP_ULNAR = "loop_ulnar"
    LOOP_RADIAL = "loop_radial"
    WHORL_PLAIN = "whorl_plain"
    WHORL_CENTRAL = "whorl_central"
    WHORL_DOUBLE = "whorl_double"
    COMPOSITE = "composite"


class BiologicalDecoder:
    """
    Analyze dermatoglyphic patterns and biological markers.

    Scientific basis:
    - Fingerprints form weeks 10-24 of fetal development
    - Pattern influenced by genetics AND intrauterine environment
    - Down syndrome: excess ulnar loops, simian crease
    - Validated diagnostic marker for chromosomal conditions
    """

    # Pattern frequencies in general population
    PATTERN_FREQUENCIES = {
        PatternType.LOOP_ULNAR: 0.65,      # Most common
        PatternType.WHORL_PLAIN: 0.25,
        PatternType.ARCH_PLAIN: 0.05,
        PatternType.LOOP_RADIAL: 0.03,
        PatternType.ARCH_TENTED: 0.01,
        PatternType.WHORL_DOUBLE: 0.005,
        PatternType.WHORL_CENTRAL: 0.003,
        PatternType.COMPOSITE: 0.002
    }

    # Ridge count correlations
    RIDGE_COUNT_NORMS = {
        "total_finger": {"mean": 145, "std": 51, "range": (0, 300)},
        "single_finger_loop": {"mean": 12, "std": 5, "range": (0, 30)},
        "single_finger_whorl": {"mean": 15, "std": 6, "range": (0, 35)}
    }

    # Pattern-element correspondences (traditional palmistry mapped to elements)
    PATTERN_ELEMENTS = {
        PatternType.ARCH_PLAIN: {"element": "Earth", "quality": "Grounded, practical"},
        PatternType.ARCH_TENTED: {"element": "Fire/Earth", "quality": "Driven stability"},
        PatternType.LOOP_ULNAR: {"element": "Water", "quality": "Adaptable, flowing"},
        PatternType.LOOP_RADIAL: {"element": "Air", "quality": "Mental flexibility"},
        PatternType.WHORL_PLAIN: {"element": "Fire", "quality": "Individualistic, focused"},
        PatternType.WHORL_CENTRAL: {"element": "Fire+", "quality": "Intense focus"},
        PatternType.WHORL_DOUBLE: {"element": "Fire/Air", "quality": "Dual nature"},
        PatternType.COMPOSITE: {"element": "Mixed", "quality": "Complex integration"}
    }

    # Finger correspondences
    FINGERS = {
        "thumb": {"planet": "Venus", "represents": "Will, logic"},
        "index": {"planet": "Jupiter", "represents": "Ambition, leadership"},
        "middle": {"planet": "Saturn", "represents": "Responsibility, boundaries"},
        "ring": {"planet": "Sun/Apollo", "represents": "Creativity, expression"},
        "pinky": {"planet": "Mercury", "represents": "Communication, commerce"}
    }

    # Palm mounts
    MOUNTS = {
        "venus": {"location": "Base of thumb", "excess": "Sensuality", "deficient": "Coldness"},
        "jupiter": {"location": "Below index", "excess": "Pride", "deficient": "Low ambition"},
        "saturn": {"location": "Below middle", "excess": "Melancholy", "deficient": "Irresponsible"},
        "apollo": {"location": "Below ring", "excess": "Vanity", "deficient": "No creativity"},
        "mercury": {"location": "Below pinky", "excess": "Talkative", "deficient": "Shy"},
        "mars_positive": {"location": "Inside thumb", "excess": "Aggression", "deficient": "Cowardice"},
        "mars_negative": {"location": "Under mercury", "excess": "Passive aggression", "deficient": "No resilience"},
        "luna": {"location": "Opposite thumb", "excess": "Imagination", "deficient": "No intuition"}
    }

    # Major palm lines
    LINES = {
        "life": {
            "location": "Curves around thumb",
            "indicates": "Vitality, major life changes",
            "scientific": "No correlation with lifespan (myth)"
        },
        "head": {
            "location": "Horizontal across upper palm",
            "indicates": "Thinking style, mental approach",
            "scientific": "Correlates with some cognitive patterns"
        },
        "heart": {
            "location": "Horizontal across top",
            "indicates": "Emotional nature, relationships",
            "scientific": "No validated correlation"
        },
        "fate": {
            "location": "Vertical up center",
            "indicates": "Life path, external influences",
            "scientific": "Present in ~50% of hands"
        },
        "simian": {
            "location": "Single crease (head+heart fused)",
            "indicates": "Intensity, single-mindedness",
            "scientific": "Associated with Down syndrome (diagnostic marker)"
        }
    }

    def __init__(self):
        self.bus = ThreeSixNine()

    def analyze_pattern(self, pattern_type: str) -> Dict:
        """Analyze a single dermatoglyphic pattern."""
        try:
            pattern = PatternType(pattern_type.lower())
        except ValueError:
            return {"error": f"Unknown pattern type: {pattern_type}"}

        freq = self.PATTERN_FREQUENCIES.get(pattern, 0)
        element_info = self.PATTERN_ELEMENTS.get(pattern, {})

        return {
            "pattern": pattern.value,
            "frequency": freq,
            "rarity": "Common" if freq > 0.1 else "Uncommon" if freq > 0.01 else "Rare",
            "element": element_info.get("element", "Unknown"),
            "quality": element_info.get("quality", "Unknown"),
            "three_six_nine": self.bus.classify_value(int(freq * 1000))
        }

    def analyze_hand(self, patterns: Dict[str, str]) -> Dict:
        """
        Analyze a complete hand of fingerprint patterns.

        Args:
            patterns: {"thumb": "loop_ulnar", "index": "whorl_plain", ...}
        """
        results = {}
        element_counts = {}
        pattern_counts = {}

        for finger, pattern_str in patterns.items():
            if finger not in self.FINGERS:
                continue

            try:
                pattern = PatternType(pattern_str.lower())
            except ValueError:
                results[finger] = {"error": f"Unknown pattern: {pattern_str}"}
                continue

            element_info = self.PATTERN_ELEMENTS.get(pattern, {})
            finger_info = self.FINGERS.get(finger, {})

            element = element_info.get("element", "Unknown")
            element_counts[element] = element_counts.get(element, 0) + 1
            pattern_counts[pattern.value] = pattern_counts.get(pattern.value, 0) + 1

            results[finger] = {
                "pattern": pattern.value,
                "element": element,
                "quality": element_info.get("quality"),
                "finger_planet": finger_info.get("planet"),
                "finger_represents": finger_info.get("represents")
            }

        # Calculate pattern diversity
        unique_patterns = len(pattern_counts)

        # Dominant element
        dominant_element = max(element_counts, key=element_counts.get) if element_counts else "None"

        # Pattern ID sum for 3-6-9
        pattern_id_sum = sum(
            list(PatternType).index(PatternType(p)) + 1
            for p in patterns.values()
            if p.lower() in [pt.value for pt in PatternType]
        )

        return {
            "fingers": results,
            "pattern_counts": pattern_counts,
            "element_distribution": element_counts,
            "dominant_element": dominant_element,
            "pattern_diversity": unique_patterns,
            "interpretation": self._interpret_hand(element_counts, pattern_counts),
            "three_six_nine": self.bus.classify_value(pattern_id_sum)
        }

    def _interpret_hand(self, elements: Dict, patterns: Dict) -> str:
        """Generate interpretation from hand analysis."""
        parts = []

        # Element balance
        if len(elements) == 1:
            elem = list(elements.keys())[0]
            parts.append(f"Strong {elem} emphasis - highly focused nature.")
        elif "Fire" in elements and "Water" in elements:
            parts.append("Fire-Water dynamic: passion balanced by adaptability.")
        elif "Earth" in elements and "Air" in elements:
            parts.append("Earth-Air combination: practical thinking.")

        # Pattern emphasis
        loop_count = sum(1 for p in patterns.keys() if "loop" in p)
        whorl_count = sum(1 for p in patterns.keys() if "whorl" in p)
        arch_count = sum(1 for p in patterns.keys() if "arch" in p)

        if loop_count >= 4:
            parts.append("Loop dominance suggests adaptability and social orientation.")
        elif whorl_count >= 3:
            parts.append("Multiple whorls indicate strong individuality and focus.")
        elif arch_count >= 2:
            parts.append("Arch presence suggests grounded, practical approach.")

        return " ".join(parts) if parts else "Balanced pattern distribution."

    def analyze_ridge_count(self, total_count: int) -> Dict:
        """Analyze total ridge count."""
        norm = self.RIDGE_COUNT_NORMS["total_finger"]

        z_score = (total_count - norm["mean"]) / norm["std"]

        if z_score < -2:
            category = "Very low"
        elif z_score < -1:
            category = "Low"
        elif z_score < 1:
            category = "Average"
        elif z_score < 2:
            category = "High"
        else:
            category = "Very high"

        return {
            "total_ridge_count": total_count,
            "population_mean": norm["mean"],
            "z_score": round(z_score, 2),
            "category": category,
            "interpretation": f"Ridge count {category.lower()} compared to population mean.",
            "three_six_nine": self.bus.classify_value(total_count)
        }

    def get_finger_info(self, finger: str) -> Dict:
        """Get information about a specific finger."""
        if finger.lower() not in self.FINGERS:
            return {"error": f"Unknown finger: {finger}"}

        info = self.FINGERS[finger.lower()].copy()
        info["finger"] = finger.lower()

        # Index for 3-6-9
        finger_index = list(self.FINGERS.keys()).index(finger.lower()) + 1
        info["three_six_nine"] = self.bus.classify_value(finger_index)

        return info

    def get_mount_info(self, mount: str) -> Dict:
        """Get information about a palm mount."""
        mount_lower = mount.lower().replace(" ", "_")
        if mount_lower not in self.MOUNTS:
            return {"error": f"Unknown mount: {mount}"}

        info = self.MOUNTS[mount_lower].copy()
        info["mount"] = mount_lower

        return info

    def get_line_info(self, line: str) -> Dict:
        """Get information about a palm line."""
        line_lower = line.lower()
        if line_lower not in self.LINES:
            return {"error": f"Unknown line: {line}"}

        info = self.LINES[line_lower].copy()
        info["line"] = line_lower

        return info

    def check_markers(self, features: Dict) -> Dict:
        """
        Check for diagnostic markers.

        Args:
            features: {
                "simian_crease": True/False,
                "pattern_type_dominant": "loop_ulnar",
                "sydney_line": True/False,
                ...
            }
        """
        markers = []
        risk_factors = []

        # Simian crease
        if features.get("simian_crease"):
            markers.append({
                "marker": "Simian crease",
                "significance": "Single transverse palmar crease",
                "associations": ["Down syndrome", "Fetal alcohol syndrome", "Also normal variant (1-2% population)"]
            })
            risk_factors.append("Simian crease present")

        # Sydney line
        if features.get("sydney_line"):
            markers.append({
                "marker": "Sydney line",
                "significance": "Heart line extends to edge of palm",
                "associations": ["Rubella syndrome", "Leukemia correlation studied"]
            })
            risk_factors.append("Sydney line present")

        # Excessive ulnar loops (>8 of 10 fingers)
        ulnar_count = features.get("ulnar_loop_count", 0)
        if ulnar_count > 8:
            markers.append({
                "marker": "Ulnar loop dominance",
                "significance": f"{ulnar_count}/10 ulnar loops",
                "associations": ["Down syndrome marker", "May indicate chromosomal variation"]
            })
            risk_factors.append(f"High ulnar loop count ({ulnar_count})")

        # Low total ridge count
        ridge_count = features.get("total_ridge_count")
        if ridge_count and ridge_count < 50:
            markers.append({
                "marker": "Low ridge count",
                "significance": f"Total ridge count: {ridge_count}",
                "associations": ["Down syndrome (lower average)", "Turner syndrome"]
            })
            risk_factors.append(f"Low ridge count ({ridge_count})")

        return {
            "markers_found": len(markers),
            "markers": markers,
            "risk_factors": risk_factors,
            "note": "Dermatoglyphic markers are screening indicators, not diagnostic. Consult medical professional.",
            "three_six_nine": self.bus.classify_value(len(markers))
        }

    def stats(self) -> Dict:
        """Return statistics about the biological decoder."""
        return {
            "pattern_types": len(PatternType),
            "fingers_tracked": len(self.FINGERS),
            "palm_mounts": len(self.MOUNTS),
            "palm_lines": len(self.LINES),
            "scientific_basis": [
                "Fingerprints form weeks 10-24 fetal development",
                "Pattern influenced by genetics + intrauterine environment",
                "Dermatoglyphics validated for Down syndrome screening",
                "Used in forensics (unique identification)"
            ],
            "pattern_frequencies": {
                p.value: f for p, f in self.PATTERN_FREQUENCIES.items()
            },
            "most_common": "loop_ulnar (65%)",
            "rarest": "composite (0.2%)"
        }
