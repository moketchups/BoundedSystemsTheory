"""
Phoenix Cycle Tracker

138-year periodicity in civilizational reset events.
Based on Archaix research (Jason Breshears).

The Phoenix cycle models collapse + regeneration as a dynamical system.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, date
from ..core.bus import ThreeSixNine


class PhoenixTracker:
    """
    Track position in the 138-year Phoenix cycle.

    Historical correlates suggest major events cluster around
    specific years in the cycle.
    """

    CYCLE_LENGTH = 138  # years

    # Reference point: 1902 was a Phoenix year
    REFERENCE_YEAR = 1902

    # Historical Phoenix years (working backwards and forwards from 1902)
    PHOENIX_YEARS = [
        # Ancient
        -1386, -1248, -1110, -972, -834, -696, -558, -420, -282, -144, -6,
        # Common Era
        132, 270, 408, 546, 684, 822, 960, 1098, 1236, 1374, 1512, 1650, 1788, 1926,
        # Recent
        1902, 2040, 2178
    ]

    # Major historical events at or near Phoenix years
    HISTORICAL_CORRELATES = {
        1902: ["Mt. Pelée eruption (Martinique)", "Geopolitical realignments"],
        1764: ["Beast of Gévaudan", "British Empire expansion phase"],
        1626: ["Wanggongchang explosion (Beijing)", "Ming Dynasty destabilization"],
        1488: ["Climate anomalies recorded", "Pre-Columbian contact period"],
        1350: ["Black Death aftermath", "Seismic activity surge"],
        1212: ["Mediterranean seismic sequence", "Children's Crusade"],
        # Projected
        2040: ["Next Phoenix year", "Projected reset window"],
    }

    # Cycle phases (as fraction of 138-year period)
    PHASES = {
        "dormant": (0.0, 0.15),      # Years 0-21: System recovering
        "growth": (0.15, 0.45),       # Years 21-62: Expansion phase
        "peak": (0.45, 0.65),         # Years 62-90: Maximum complexity
        "tension": (0.65, 0.85),      # Years 90-117: Stress accumulation
        "trigger": (0.85, 1.0),       # Years 117-138: Reset window
    }

    def __init__(self):
        self.bus = ThreeSixNine()

    def get_cycle_position(self, year: int) -> Dict:
        """
        Get position of a year within the Phoenix cycle.

        Returns phase, years until next Phoenix, and historical correlates.
        """
        # Calculate offset from reference
        offset = year - self.REFERENCE_YEAR

        # Position in current cycle (0-137)
        cycle_position = offset % self.CYCLE_LENGTH
        if cycle_position < 0:
            cycle_position += self.CYCLE_LENGTH

        # Which cycle number (can be negative for ancient dates)
        cycle_number = offset // self.CYCLE_LENGTH

        # Nearest Phoenix years
        prev_phoenix = self.REFERENCE_YEAR + (cycle_number * self.CYCLE_LENGTH)
        next_phoenix = prev_phoenix + self.CYCLE_LENGTH

        if year >= next_phoenix:
            prev_phoenix = next_phoenix
            next_phoenix += self.CYCLE_LENGTH

        # Years until next Phoenix
        years_to_phoenix = next_phoenix - year

        # Current phase
        phase_fraction = cycle_position / self.CYCLE_LENGTH
        current_phase = "unknown"
        for phase_name, (start, end) in self.PHASES.items():
            if start <= phase_fraction < end:
                current_phase = phase_name
                break

        # 3-6-9 analysis
        year_dr = self.bus.classify_value(year)
        position_dr = self.bus.classify_value(cycle_position)

        return {
            "year": year,
            "cycle_position": cycle_position,
            "cycle_number": cycle_number,
            "phase": current_phase,
            "phase_fraction": round(phase_fraction, 3),
            "previous_phoenix": prev_phoenix,
            "next_phoenix": next_phoenix,
            "years_to_phoenix": years_to_phoenix,
            "years_from_phoenix": cycle_position,
            "three_six_nine": {
                "year": year_dr,
                "position": position_dr
            },
            "interpretation": self._interpret_position(current_phase, years_to_phoenix, phase_fraction)
        }

    def _interpret_position(self, phase: str, years_to: int, fraction: float) -> str:
        """Generate interpretation of cycle position."""
        interpretations = {
            "dormant": "Recovery phase. System rebuilding after previous reset. Low activity.",
            "growth": "Expansion phase. Complexity increasing. New structures emerging.",
            "peak": "Maximum complexity. System at full expression. Stability apparent.",
            "tension": "Stress accumulation. Cracks forming. Pressure building.",
            "trigger": "Reset window approaching. High sensitivity to perturbation."
        }

        base = interpretations.get(phase, "Unknown phase")

        if years_to <= 5:
            base += f" ALERT: {years_to} years to Phoenix."
        elif years_to <= 20:
            base += f" Approaching trigger window ({years_to} years)."

        return base

    def get_historical_correlates(self, year: int, window: int = 10) -> Dict:
        """
        Find historical Phoenix events near a given year.
        """
        nearby = []

        for phoenix_year, events in self.HISTORICAL_CORRELATES.items():
            if abs(phoenix_year - year) <= window:
                nearby.append({
                    "phoenix_year": phoenix_year,
                    "distance": phoenix_year - year,
                    "events": events
                })

        # Also find the theoretical Phoenix years near this date
        pos = self.get_cycle_position(year)
        theoretical = [pos["previous_phoenix"], pos["next_phoenix"]]

        return {
            "query_year": year,
            "window": window,
            "nearby_phoenix_events": nearby,
            "theoretical_phoenix_years": theoretical
        }

    def compare_years(self, year1: int, year2: int) -> Dict:
        """
        Compare two years' positions in the Phoenix cycle.
        """
        pos1 = self.get_cycle_position(year1)
        pos2 = self.get_cycle_position(year2)

        # Same position in cycle?
        same_position = pos1["cycle_position"] == pos2["cycle_position"]

        # Same phase?
        same_phase = pos1["phase"] == pos2["phase"]

        # Calculate the offset
        year_diff = year2 - year1
        cycle_diff = year_diff / self.CYCLE_LENGTH

        return {
            "year1": pos1,
            "year2": pos2,
            "year_difference": year_diff,
            "cycle_difference": round(cycle_diff, 2),
            "same_cycle_position": same_position,
            "same_phase": same_phase,
            "position_difference": pos2["cycle_position"] - pos1["cycle_position"],
            "resonance": abs(year_diff) % self.CYCLE_LENGTH == 0
        }

    def project_forward(self, from_year: int, cycles: int = 3) -> List[Dict]:
        """
        Project forward from a given year through multiple cycles.
        """
        projections = []
        current_pos = self.get_cycle_position(from_year)

        for i in range(cycles):
            phoenix_year = current_pos["next_phoenix"] + (i * self.CYCLE_LENGTH)
            projections.append({
                "cycle": i + 1,
                "phoenix_year": phoenix_year,
                "years_from_now": phoenix_year - from_year,
                "three_six_nine": self.bus.classify_value(phoenix_year)
            })

        return projections

    def find_resonant_years(self, target_year: int, range_start: int, range_end: int) -> List[Dict]:
        """
        Find years in a range that share the same cycle position as target.
        """
        target_pos = self.get_cycle_position(target_year)
        target_position = target_pos["cycle_position"]

        resonant = []
        for year in range(range_start, range_end + 1):
            pos = self.get_cycle_position(year)
            if pos["cycle_position"] == target_position:
                resonant.append({
                    "year": year,
                    "cycle_position": pos["cycle_position"],
                    "phase": pos["phase"],
                    "correlates": self.HISTORICAL_CORRELATES.get(year, [])
                })

        return resonant

    def current_position(self) -> Dict:
        """Get current position in the Phoenix cycle."""
        current_year = datetime.now().year
        return self.get_cycle_position(current_year)

    def cycle_stats(self) -> Dict:
        """Return statistics about the Phoenix cycle."""
        current = self.current_position()

        return {
            "cycle_length": self.CYCLE_LENGTH,
            "reference_year": self.REFERENCE_YEAR,
            "current_year": datetime.now().year,
            "current_position": current["cycle_position"],
            "current_phase": current["phase"],
            "next_phoenix": current["next_phoenix"],
            "years_remaining": current["years_to_phoenix"],
            "known_phoenix_years": len(self.PHOENIX_YEARS),
            "documented_correlates": len(self.HISTORICAL_CORRELATES),
            "phases": list(self.PHASES.keys()),
            "mathematical_model": {
                "type": "Relaxation oscillator with forced periodicity",
                "period": "T = 138 years",
                "angular_frequency": "ω = 2π/138 ≈ 0.0455 rad/year"
            }
        }
