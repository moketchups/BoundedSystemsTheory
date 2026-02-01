"""
Sacred Geometry Engine

Mathematical patterns underlying form:
- Phi (φ) - Golden Ratio: 1.618033988749895
- Fibonacci sequence
- Platonic solids
- Seed of Life / Flower of Life
- Vesica Piscis

All integrated through 3-6-9 bus.
"""

import math
from typing import Dict, List, Tuple, Optional
from ..core.bus import ThreeSixNine


class SacredGeometry:
    """
    Analyze numbers and patterns through sacred geometry.

    Core constants:
    - φ (Phi): Golden Ratio = (1 + √5) / 2 ≈ 1.618
    - π (Pi): Circle constant ≈ 3.14159
    - e: Natural logarithm base ≈ 2.71828
    - √2: Diagonal of unit square ≈ 1.414
    """

    # Fundamental constants
    PHI = (1 + math.sqrt(5)) / 2  # 1.618033988749895
    PHI_INVERSE = PHI - 1         # 0.618033988749895
    PI = math.pi
    E = math.e
    SQRT_2 = math.sqrt(2)
    SQRT_3 = math.sqrt(3)
    SQRT_5 = math.sqrt(5)

    # Platonic solids: (name, faces, vertices, edges, dual)
    PLATONIC_SOLIDS = {
        "tetrahedron": {
            "faces": 4,
            "vertices": 4,
            "edges": 6,
            "face_shape": "triangle",
            "dual": "tetrahedron",  # Self-dual
            "element": "Fire",
            "platonic_number": 1
        },
        "hexahedron": {  # Cube
            "faces": 6,
            "vertices": 8,
            "edges": 12,
            "face_shape": "square",
            "dual": "octahedron",
            "element": "Earth",
            "platonic_number": 2
        },
        "octahedron": {
            "faces": 8,
            "vertices": 6,
            "edges": 12,
            "face_shape": "triangle",
            "dual": "hexahedron",
            "element": "Air",
            "platonic_number": 3
        },
        "dodecahedron": {
            "faces": 12,
            "vertices": 20,
            "edges": 30,
            "face_shape": "pentagon",
            "dual": "icosahedron",
            "element": "Ether/Spirit",
            "platonic_number": 4
        },
        "icosahedron": {
            "faces": 20,
            "vertices": 12,
            "edges": 30,
            "face_shape": "triangle",
            "dual": "dodecahedron",
            "element": "Water",
            "platonic_number": 5
        }
    }

    # Sacred patterns
    PATTERNS = {
        "vesica_piscis": {
            "description": "Two circles of equal radius intersecting at center",
            "ratio": "Width:Height = 1:√3",
            "significance": "Birth, creation, the womb of creation"
        },
        "seed_of_life": {
            "description": "7 overlapping circles in sixfold symmetry",
            "circles": 7,
            "significance": "Seven days of creation, fundamental pattern"
        },
        "flower_of_life": {
            "description": "19 circles in hexagonal arrangement",
            "circles": 19,
            "significance": "Contains all Platonic solids, fundamental geometry"
        },
        "metatrons_cube": {
            "description": "13 circles with connecting lines",
            "circles": 13,
            "significance": "Contains all Platonic solids as 2D projections"
        },
        "sri_yantra": {
            "description": "9 interlocking triangles (4 up, 5 down)",
            "triangles": 9,
            "significance": "Union of masculine and feminine, cosmos"
        }
    }

    def __init__(self):
        self.bus = ThreeSixNine()

    def fibonacci(self, n: int) -> List[int]:
        """Generate first n Fibonacci numbers."""
        if n <= 0:
            return []
        if n == 1:
            return [0]
        if n == 2:
            return [0, 1]

        seq = [0, 1]
        for i in range(2, n):
            seq.append(seq[-1] + seq[-2])
        return seq

    def analyze_fibonacci(self, n: int = 20) -> Dict:
        """
        Analyze Fibonacci sequence through 3-6-9 lens.

        The Fibonacci sequence has a 24-number repeating pattern
        in its digital roots.
        """
        seq = self.fibonacci(n)
        digital_roots = [self.bus.digital_root(x) for x in seq if x > 0]

        # Count by domain
        domains = {"material": 0, "flux": 0, "unity": 0}
        for dr in digital_roots:
            classification = self.bus.classify_value(dr)
            domains[classification["domain"]] += 1

        # Phi approximations
        phi_approximations = []
        for i in range(2, len(seq)):
            if seq[i-1] > 0:
                ratio = seq[i] / seq[i-1]
                error = abs(ratio - self.PHI)
                phi_approximations.append({
                    "n": i,
                    "ratio": f"{seq[i]}/{seq[i-1]}",
                    "value": round(ratio, 6),
                    "error": round(error, 6)
                })

        return {
            "sequence": seq,
            "digital_roots": digital_roots,
            "domain_distribution": domains,
            "phi_approximations": phi_approximations[-5:],  # Last 5
            "convergence_to_phi": round(seq[-1] / seq[-2], 10) if len(seq) > 1 else None,
            "three_six_nine": {
                "sequence_sum_dr": self.bus.digital_root(sum(seq)),
                "note": "Fibonacci digital roots repeat with period 24"
            }
        }

    def golden_ratio_analysis(self, value: float) -> Dict:
        """
        Analyze a value's relationship to Phi (golden ratio).
        """
        # Check if value is close to phi or phi-related
        phi_multiple = value / self.PHI
        phi_power = math.log(value) / math.log(self.PHI) if value > 0 else None

        # Phi relationships
        relationships = []

        # Check if close to phi^n for small n
        for n in range(-5, 6):
            phi_n = self.PHI ** n
            if abs(value - phi_n) < 0.001:
                relationships.append(f"≈ φ^{n}")

        # Check fibonacci ratio
        fib = self.fibonacci(30)
        for i in range(2, len(fib)):
            if abs(value - fib[i] / fib[i-1]) < 0.0001:
                relationships.append(f"≈ F({i})/F({i-1})")

        # Golden angle (137.5°)
        golden_angle = 360 * (1 - 1/self.PHI)  # ≈ 137.507°
        if abs(value - golden_angle) < 0.1:
            relationships.append("≈ Golden Angle (137.5°)")

        return {
            "value": value,
            "phi": self.PHI,
            "phi_inverse": self.PHI_INVERSE,
            "value_over_phi": round(phi_multiple, 6),
            "log_phi_of_value": round(phi_power, 6) if phi_power else None,
            "is_golden": abs(value - self.PHI) < 0.0001,
            "relationships": relationships,
            "three_six_nine": self.bus.classify_value(int(value * 1000))  # Scale for DR
        }

    def get_solid(self, name: str) -> Dict:
        """Get information about a Platonic solid."""
        name_lower = name.lower()
        if name_lower == "cube":
            name_lower = "hexahedron"

        if name_lower not in self.PLATONIC_SOLIDS:
            return {"error": f"Unknown solid: {name}"}

        solid = self.PLATONIC_SOLIDS[name_lower].copy()
        solid["name"] = name_lower

        # Euler's formula: V - E + F = 2
        euler = solid["vertices"] - solid["edges"] + solid["faces"]
        solid["euler_check"] = euler == 2

        # 3-6-9 analysis
        solid["three_six_nine"] = {
            "faces": self.bus.classify_value(solid["faces"]),
            "vertices": self.bus.classify_value(solid["vertices"]),
            "edges": self.bus.classify_value(solid["edges"])
        }

        return solid

    def analyze_number(self, n: int) -> Dict:
        """
        Comprehensive sacred geometry analysis of a number.
        """
        result = {
            "number": n,
            "digital_root": self.bus.digital_root(n),
            "domain": self.bus.classify_value(n)["domain"]
        }

        # Fibonacci check
        fib = self.fibonacci(50)
        if n in fib:
            fib_index = fib.index(n)
            result["fibonacci"] = {
                "is_fibonacci": True,
                "index": fib_index,
                "ratio_to_previous": round(n / fib[fib_index-1], 6) if fib_index > 0 else None
            }
        else:
            result["fibonacci"] = {"is_fibonacci": False}

        # Prime check
        result["is_prime"] = self._is_prime(n)

        # Perfect number check (equals sum of proper divisors)
        divisors = [i for i in range(1, n) if n % i == 0]
        result["is_perfect"] = sum(divisors) == n if n > 1 else False

        # Triangular number check: n = k(k+1)/2
        # Solve: k² + k - 2n = 0 → k = (-1 + √(1+8n))/2
        discriminant = 1 + 8 * n
        sqrt_disc = math.sqrt(discriminant)
        if sqrt_disc == int(sqrt_disc):
            k = (-1 + sqrt_disc) / 2
            if k == int(k) and k > 0:
                result["triangular"] = {"is_triangular": True, "index": int(k)}
            else:
                result["triangular"] = {"is_triangular": False}
        else:
            result["triangular"] = {"is_triangular": False}

        # Square number check
        sqrt_n = math.sqrt(n)
        result["is_square"] = sqrt_n == int(sqrt_n)

        # Platonic solid numbers
        for solid_name, solid in self.PLATONIC_SOLIDS.items():
            if n in [solid["faces"], solid["vertices"], solid["edges"]]:
                result["platonic_connection"] = {
                    "solid": solid_name,
                    "property": "faces" if n == solid["faces"] else "vertices" if n == solid["vertices"] else "edges"
                }
                break

        return result

    def _is_prime(self, n: int) -> bool:
        """Check if n is prime."""
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        for i in range(3, int(math.sqrt(n)) + 1, 2):
            if n % i == 0:
                return False
        return True

    def vesica_piscis(self) -> Dict:
        """Calculate vesica piscis properties."""
        # Two unit circles intersecting at centers
        # Width (minor axis) = 1 (radius)
        # Height (major axis) = √3
        return {
            "pattern": "vesica_piscis",
            "description": self.PATTERNS["vesica_piscis"]["description"],
            "properties": {
                "radius": 1,
                "width": 1,
                "height": round(self.SQRT_3, 6),
                "ratio": f"1:√3 ≈ 1:{round(self.SQRT_3, 4)}",
                "area": round((2 * math.pi / 3) - (self.SQRT_3 / 2), 6)
            },
            "significance": self.PATTERNS["vesica_piscis"]["significance"],
            "three_six_nine": {
                "height_dr": self.bus.digital_root(int(self.SQRT_3 * 1000)),
                "note": "√3 ≈ 1.732, integral to sacred geometry"
            }
        }

    def flower_of_life(self) -> Dict:
        """Flower of Life pattern analysis."""
        return {
            "pattern": "flower_of_life",
            "description": self.PATTERNS["flower_of_life"]["description"],
            "structure": {
                "center_circle": 1,
                "first_ring": 6,
                "total_circles": 19,
                "symmetry": "sixfold",
                "contains": ["Seed of Life", "Tree of Life", "Metatron's Cube", "All Platonic Solids"]
            },
            "mathematical_properties": {
                "hexagonal_packing": True,
                "efficiency": round(math.pi / (2 * self.SQRT_3), 4),  # ≈ 0.9069
                "circles_per_ring": [1, 6, 12]  # Core + rings
            },
            "three_six_nine": {
                "19_dr": self.bus.digital_root(19),
                "6_symmetry": self.bus.classify_value(6),
                "note": "19 circles, 6-fold symmetry, encodes all Platonic solids"
            }
        }

    def constants(self) -> Dict:
        """Return sacred geometry constants with 3-6-9 analysis."""
        constants = {
            "phi": {
                "value": round(self.PHI, 10),
                "name": "Golden Ratio",
                "symbol": "φ",
                "definition": "(1 + √5) / 2",
                "properties": ["φ² = φ + 1", "1/φ = φ - 1", "φ = 1 + 1/φ"]
            },
            "pi": {
                "value": round(self.PI, 10),
                "name": "Pi",
                "symbol": "π",
                "definition": "Circumference / Diameter",
                "properties": ["Transcendental", "Normal (conjectured)"]
            },
            "e": {
                "value": round(self.E, 10),
                "name": "Euler's Number",
                "symbol": "e",
                "definition": "lim (1 + 1/n)^n as n → ∞",
                "properties": ["Transcendental", "d/dx(e^x) = e^x"]
            },
            "sqrt_2": {
                "value": round(self.SQRT_2, 10),
                "name": "Square Root of 2",
                "symbol": "√2",
                "definition": "Diagonal of unit square",
                "properties": ["Irrational", "First proven irrational number"]
            },
            "sqrt_3": {
                "value": round(self.SQRT_3, 10),
                "name": "Square Root of 3",
                "symbol": "√3",
                "definition": "Height of equilateral triangle with side 2",
                "properties": ["Irrational", "Vesica Piscis ratio"]
            },
            "sqrt_5": {
                "value": round(self.SQRT_5, 10),
                "name": "Square Root of 5",
                "symbol": "√5",
                "definition": "Related to Golden Ratio: φ = (1 + √5)/2",
                "properties": ["Irrational", "Pentagon diagonal"]
            }
        }

        # Add 3-6-9 analysis for each
        for key, const in constants.items():
            # Scale to integer for DR analysis
            scaled = int(const["value"] * 10000)
            constants[key]["three_six_nine"] = self.bus.classify_value(scaled)

        return constants

    def stats(self) -> Dict:
        """Return statistics about the sacred geometry system."""
        return {
            "constants": list(self.constants().keys()),
            "platonic_solids": list(self.PLATONIC_SOLIDS.keys()),
            "patterns": list(self.PATTERNS.keys()),
            "golden_ratio": round(self.PHI, 6),
            "fibonacci_period_in_dr": 24,
            "vesica_ratio": f"1:√3 ≈ 1:{round(self.SQRT_3, 4)}",
            "platonic_summary": {
                "total": 5,
                "euler_formula": "V - E + F = 2",
                "only_regular_convex_polyhedra": True
            }
        }
