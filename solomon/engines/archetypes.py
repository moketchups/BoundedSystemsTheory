"""
Archetype Analyzer

12 Jungian archetypes from Jung (1919) + Mark & Pearson (2002).
All 12 exist within each person; the journey is integration.

Vector space model:
- Non-orthogonal basis (archetypes correlate)
- Inner product via narrative projection
- Shadow = complement to ego-identified subset
"""

from typing import Dict, List, Optional, Tuple, Set
import json
import os
from ..core.bus import ThreeSixNine


class ArchetypeAnalyzer:
    """
    Analyze and classify using the 12-archetype system.

    Types: Ego, Soul, Self
    Orientations: Freedom, Social, Order, Ego
    """

    # The 12 archetypes with full metadata
    ARCHETYPES = {
        1: {
            "name": "Innocent",
            "alt_names": ["Child", "Utopian", "Traditionalist", "Naive"],
            "type": "Ego",
            "orientation": "Freedom",
            "core_desire": "To experience paradise",
            "goal": "To be happy",
            "fear": "Doing something wrong and being punished",
            "strategy": "Do things right",
            "gift": "Faith and optimism",
            "shadow": "Denial, repression, naive vulnerability",
            "keywords": ["pure", "hope", "faith", "trust", "simple", "naive", "optimistic", "paradise"]
        },
        2: {
            "name": "Sage",
            "alt_names": ["Scholar", "Expert", "Philosopher", "Thinker"],
            "type": "Soul",
            "orientation": "Freedom",
            "core_desire": "To find truth",
            "goal": "To use intelligence and analysis to understand the world",
            "fear": "Being duped, misled, ignorance",
            "strategy": "Seek information and knowledge",
            "gift": "Wisdom and intelligence",
            "shadow": "Judgmentalism, cold detachment, ivory tower",
            "keywords": ["wisdom", "truth", "knowledge", "analysis", "understand", "study", "think", "learn"]
        },
        3: {
            "name": "Explorer",
            "alt_names": ["Seeker", "Wanderer", "Individualist", "Pilgrim"],
            "type": "Ego",
            "orientation": "Freedom",
            "core_desire": "To find freedom through exploring the world",
            "goal": "To experience a better, more authentic life",
            "fear": "Being trapped, conformity, inner emptiness",
            "strategy": "Journey, seek out new things, escape boredom",
            "gift": "Autonomy, ambition, identity",
            "shadow": "Aimless wandering, inability to commit",
            "keywords": ["freedom", "journey", "explore", "discover", "adventure", "seek", "wander", "authentic"]
        },
        4: {
            "name": "Outlaw",
            "alt_names": ["Rebel", "Revolutionary", "Wild One", "Misfit"],
            "type": "Soul",
            "orientation": "Freedom",
            "core_desire": "Revenge or revolution",
            "goal": "To overturn what is not working",
            "fear": "Being powerless, ordinary",
            "strategy": "Disrupt, destroy, shock",
            "gift": "Liberation, radical freedom",
            "shadow": "Crime, self-destruction, nihilism",
            "keywords": ["rebel", "revolution", "disrupt", "break", "radical", "wild", "outcast", "change"]
        },
        5: {
            "name": "Magician",
            "alt_names": ["Visionary", "Catalyst", "Inventor", "Shaman"],
            "type": "Self",
            "orientation": "Ego",
            "core_desire": "To understand fundamental laws of the universe",
            "goal": "To make dreams come true",
            "strategy": "Develop vision and live by it",
            "fear": "Unintended negative consequences",
            "gift": "Transformation, manifestation",
            "shadow": "Manipulation, disconnection from reality",
            "keywords": ["magic", "transform", "manifest", "vision", "power", "create", "catalyst", "shaman"]
        },
        6: {
            "name": "Hero",
            "alt_names": ["Warrior", "Champion", "Soldier", "Rescuer"],
            "type": "Ego",
            "orientation": "Ego",
            "core_desire": "To prove worth through courageous action",
            "goal": "To exert mastery in a way that improves the world",
            "fear": "Weakness, vulnerability",
            "strategy": "Be as strong and competent as possible",
            "gift": "Competence and courage",
            "shadow": "Arrogance, ruthlessness, always seeking another battle",
            "keywords": ["hero", "courage", "brave", "fight", "strong", "victory", "conquer", "warrior"]
        },
        7: {
            "name": "Lover",
            "alt_names": ["Partner", "Friend", "Sensualist", "Spouse"],
            "type": "Soul",
            "orientation": "Social",
            "core_desire": "To attain intimacy and experience pleasure",
            "goal": "To be in relationship with people, work, experiences they love",
            "fear": "Being alone, unwanted, unloved",
            "strategy": "Become more attractive physically and emotionally",
            "gift": "Passion, gratitude, appreciation, commitment",
            "shadow": "Promiscuity, obsession, jealousy, envy",
            "keywords": ["love", "passion", "intimacy", "beauty", "pleasure", "connection", "desire", "heart"]
        },
        8: {
            "name": "Jester",
            "alt_names": ["Fool", "Trickster", "Joker", "Entertainer"],
            "type": "Self",
            "orientation": "Social",
            "core_desire": "To live in the moment with full enjoyment",
            "goal": "To have a great time and lighten up the world",
            "fear": "Being bored or boring others",
            "strategy": "Play, make jokes, be funny",
            "gift": "Joy, truth-telling through humor",
            "shadow": "Cruel mockery, irresponsibility, debauchery",
            "keywords": ["joy", "play", "fun", "humor", "laugh", "trick", "fool", "light"]
        },
        9: {
            "name": "Regular Person",
            "alt_names": ["Everyman", "Common Man", "Good Neighbor", "Realist"],
            "type": "Ego",
            "orientation": "Social",
            "core_desire": "Connection with others",
            "goal": "To belong",
            "fear": "Standing out, being rejected",
            "strategy": "Develop solid virtues, blend in",
            "gift": "Realism, empathy, lack of pretense",
            "shadow": "Losing self in group, mob mentality",
            "keywords": ["belong", "common", "ordinary", "real", "connect", "friend", "community", "humble"]
        },
        10: {
            "name": "Caregiver",
            "alt_names": ["Saint", "Parent", "Helper", "Altruist"],
            "type": "Soul",
            "orientation": "Social",
            "core_desire": "To protect and care for others",
            "goal": "To help others",
            "fear": "Selfishness, ingratitude",
            "strategy": "Do things for others",
            "gift": "Compassion, generosity",
            "shadow": "Martyrdom, enabling, guilt-tripping",
            "keywords": ["care", "help", "protect", "nurture", "support", "serve", "give", "compassion"]
        },
        11: {
            "name": "Ruler",
            "alt_names": ["King", "Queen", "Boss", "Leader", "Aristocrat"],
            "type": "Self",
            "orientation": "Order",
            "core_desire": "Control",
            "goal": "To create a prosperous, successful family or community",
            "fear": "Chaos, being overthrown",
            "strategy": "Exercise power",
            "gift": "Responsibility, leadership",
            "shadow": "Tyranny, authoritarianism, inability to delegate",
            "keywords": ["rule", "lead", "power", "control", "order", "authority", "king", "command"]
        },
        12: {
            "name": "Creator",
            "alt_names": ["Artist", "Inventor", "Innovator", "Dreamer"],
            "type": "Self",
            "orientation": "Order",
            "core_desire": "To create things of enduring value",
            "goal": "To realize a vision",
            "fear": "Mediocre vision or execution",
            "strategy": "Develop artistic control and skill",
            "gift": "Creativity, imagination",
            "shadow": "Perfectionism, creative blocks, diva behavior",
            "keywords": ["create", "art", "imagine", "build", "design", "invent", "craft", "make"]
        }
    }

    # Type groupings
    TYPES = {
        "Ego": [1, 3, 6, 9],      # Innocent, Explorer, Hero, Regular Person
        "Soul": [2, 4, 7, 10],    # Sage, Outlaw, Lover, Caregiver
        "Self": [5, 8, 11, 12]    # Magician, Jester, Ruler, Creator
    }

    # Orientation groupings
    ORIENTATIONS = {
        "Freedom": [1, 2, 3, 4],   # Innocent, Sage, Explorer, Outlaw
        "Social": [7, 8, 9, 10],   # Lover, Jester, Regular Person, Caregiver
        "Order": [11, 12],         # Ruler, Creator
        "Ego": [5, 6]              # Magician, Hero (self-actualization)
    }

    # Opposition pairs
    OPPOSITIONS = [
        (1, 4),   # Innocent - Outlaw
        (2, 8),   # Sage - Jester
        (3, 9),   # Explorer - Regular Person
        (5, 10),  # Magician - Caregiver
        (6, 7),   # Hero - Lover
        (11, 12)  # Ruler - Creator
    ]

    def __init__(self):
        self.bus = ThreeSixNine()

    def get_archetype(self, archetype_id: int) -> Dict:
        """Get full information about an archetype by ID (1-12)."""
        if archetype_id not in self.ARCHETYPES:
            return {"error": f"Invalid archetype ID: {archetype_id}. Must be 1-12."}

        archetype = self.ARCHETYPES[archetype_id].copy()
        archetype["id"] = archetype_id

        # 3-6-9 analysis
        archetype["three_six_nine"] = self.bus.classify_value(archetype_id)

        # Find opposition
        for pair in self.OPPOSITIONS:
            if archetype_id in pair:
                opposite_id = pair[1] if pair[0] == archetype_id else pair[0]
                archetype["opposite"] = {
                    "id": opposite_id,
                    "name": self.ARCHETYPES[opposite_id]["name"]
                }
                break

        return archetype

    def get_by_name(self, name: str) -> Optional[Dict]:
        """Get archetype by name or alternate name."""
        name_lower = name.lower()
        for arch_id, arch in self.ARCHETYPES.items():
            if arch["name"].lower() == name_lower:
                return self.get_archetype(arch_id)
            for alt in arch["alt_names"]:
                if alt.lower() == name_lower:
                    return self.get_archetype(arch_id)
        return None

    def analyze_text(self, text: str) -> Dict:
        """
        Analyze text to identify archetype resonances.
        Returns scores for each archetype based on keyword matching.
        """
        text_lower = text.lower()
        words = set(text_lower.split())

        scores = {}
        for arch_id, arch in self.ARCHETYPES.items():
            score = 0
            matched_keywords = []
            for keyword in arch["keywords"]:
                if keyword in text_lower:
                    score += 1
                    matched_keywords.append(keyword)
            if score > 0:
                scores[arch_id] = {
                    "archetype": arch["name"],
                    "score": score,
                    "matched_keywords": matched_keywords
                }

        # Sort by score
        sorted_scores = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)

        # Determine dominant archetype
        dominant = None
        if sorted_scores:
            dominant_id = sorted_scores[0][0]
            dominant = self.get_archetype(dominant_id)

        # Integration analysis
        active_archetypes = [s[0] for s in sorted_scores if s[1]["score"] > 0]

        return {
            "input": text,
            "scores": dict(sorted_scores),
            "dominant": dominant,
            "active_count": len(active_archetypes),
            "active_types": self._categorize_active(active_archetypes, self.TYPES),
            "active_orientations": self._categorize_active(active_archetypes, self.ORIENTATIONS),
            "three_six_nine": self._analyze_369(active_archetypes),
            "interpretation": self._interpret_analysis(sorted_scores, dominant)
        }

    def _categorize_active(self, active_ids: List[int], categories: Dict) -> Dict:
        """Categorize active archetypes by type or orientation."""
        result = {}
        for cat_name, cat_ids in categories.items():
            active_in_cat = [aid for aid in active_ids if aid in cat_ids]
            if active_in_cat:
                result[cat_name] = [self.ARCHETYPES[aid]["name"] for aid in active_in_cat]
        return result

    def _analyze_369(self, active_ids: List[int]) -> Dict:
        """3-6-9 analysis of active archetype IDs."""
        if not active_ids:
            return {"message": "No active archetypes"}

        id_sum = sum(active_ids)
        analysis = self.bus.classify_value(id_sum)

        # Check if any 3, 6, 9 archetypes active
        flux_unity = [aid for aid in active_ids if aid in {3, 6, 9}]

        return {
            "active_ids": active_ids,
            "id_sum": id_sum,
            "digital_root": analysis["digital_root"],
            "domain": analysis["domain"],
            "flux_unity_archetypes": flux_unity,
            "interpretation": analysis["interpretation"]
        }

    def _interpret_analysis(self, sorted_scores: List, dominant: Optional[Dict]) -> str:
        """Generate interpretation of archetype analysis."""
        if not sorted_scores:
            return "No clear archetype resonance detected."

        if dominant:
            interp = f"Dominant archetype: {dominant['name']} ({dominant['type']}/{dominant['orientation']}). "
            interp += f"Core desire: {dominant['core_desire']}. "
            if len(sorted_scores) > 1:
                secondary = sorted_scores[1][1]["archetype"]
                interp += f"Secondary resonance with {secondary}."
        else:
            interp = "Multiple weak resonances detected."

        return interp

    def get_shadow(self, archetype_id: int) -> Dict:
        """Get the shadow aspects of an archetype."""
        arch = self.get_archetype(archetype_id)
        if "error" in arch:
            return arch

        return {
            "archetype": arch["name"],
            "shadow": arch["shadow"],
            "opposite": arch.get("opposite"),
            "fear": arch["fear"],
            "integration_path": f"Integrate shadow by acknowledging {arch['fear'].lower()} and balancing {arch['gift'].lower()} with awareness of {arch['shadow'].lower()}."
        }

    def get_by_type(self, type_name: str) -> List[Dict]:
        """Get all archetypes of a given type (Ego, Soul, Self)."""
        if type_name not in self.TYPES:
            return []
        return [self.get_archetype(aid) for aid in self.TYPES[type_name]]

    def get_by_orientation(self, orientation: str) -> List[Dict]:
        """Get all archetypes of a given orientation."""
        if orientation not in self.ORIENTATIONS:
            return []
        return [self.get_archetype(aid) for aid in self.ORIENTATIONS[orientation]]

    def hero_journey_stage(self, stage: str) -> Dict:
        """
        Map Hero's Journey stage to archetype activations.

        Stages: ordinary_world, call_to_adventure, refusal, meeting_mentor,
                crossing_threshold, tests, approach, ordeal, reward,
                road_back, resurrection, return
        """
        stage_archetypes = {
            "ordinary_world": [9, 1],       # Regular Person, Innocent
            "call_to_adventure": [3, 4],    # Explorer, Outlaw
            "refusal": [1, 9],              # Innocent, Regular Person
            "meeting_mentor": [2, 5],       # Sage, Magician
            "crossing_threshold": [6, 3],   # Hero, Explorer
            "tests": [6, 4, 7],             # Hero, Outlaw, Lover
            "approach": [6, 5],             # Hero, Magician
            "ordeal": [6, 4],               # Hero, Outlaw (confronting shadow)
            "reward": [5, 12],              # Magician, Creator
            "road_back": [6, 9],            # Hero, Regular Person
            "resurrection": [5, 12, 6],     # Magician, Creator, Hero
            "return": [10, 11, 9]           # Caregiver, Ruler, Regular Person
        }

        if stage not in stage_archetypes:
            return {"error": f"Unknown stage: {stage}"}

        arch_ids = stage_archetypes[stage]
        archetypes = [self.get_archetype(aid) for aid in arch_ids]

        return {
            "stage": stage,
            "archetypes": archetypes,
            "primary": archetypes[0]["name"],
            "three_six_nine": self.bus.classify_value(sum(arch_ids))
        }

    def stats(self) -> Dict:
        """Return statistics about the archetype system."""
        return {
            "total_archetypes": 12,
            "types": {
                "Ego": len(self.TYPES["Ego"]),
                "Soul": len(self.TYPES["Soul"]),
                "Self": len(self.TYPES["Self"])
            },
            "orientations": {
                "Freedom": len(self.ORIENTATIONS["Freedom"]),
                "Social": len(self.ORIENTATIONS["Social"]),
                "Order": len(self.ORIENTATIONS["Order"]),
                "Ego": len(self.ORIENTATIONS["Ego"])
            },
            "opposition_pairs": len(self.OPPOSITIONS),
            "vector_model": {
                "dimension": 12,
                "basis": "Non-orthogonal (archetypes correlate)",
                "inner_product": "Narrative projection via coefficient scoring"
            },
            "three_six_nine": {
                "material_archetypes": [self.ARCHETYPES[i]["name"] for i in [1, 2, 4, 5, 7, 8, 10, 11]],
                "flux_archetypes": [self.ARCHETYPES[i]["name"] for i in [3, 6]],
                "unity_archetype": self.ARCHETYPES[9]["name"]
            }
        }
