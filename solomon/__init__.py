"""
Solomon's Temple - Admin Console for Bounded Systems

"And Solomon built the Temple."

The demons answered. Now we build.
"""

from .core.bus import ThreeSixNine
from .core.logger import ConsoleLogger
from .engines.gematria import GematriaEngine
from .engines.iching import IChingOracle
from .engines.gates import GatesNavigator
from .engines.phoenix import PhoenixTracker
from .engines.archetypes import ArchetypeAnalyzer
from .engines.geometry import SacredGeometry
from .engines.biological import BiologicalDecoder

__version__ = "1.0.0"
__all__ = [
    "ThreeSixNine", "ConsoleLogger",
    "GematriaEngine", "IChingOracle", "GatesNavigator", "PhoenixTracker",
    "ArchetypeAnalyzer", "SacredGeometry", "BiologicalDecoder"
]
