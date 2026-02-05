"""
HSAP PyTorch Integration - Training integration for HSAP-compliant models.

Implements:
- D7: Empirical Distrust Loss L_HSAP = L_base + λΣ(1-A(x))·ℓ(θ,x)
- HSAPTrainer for integrating HSAP into training loops
"""

from hsap.pytorch.loss import EmpiricalDistrustLoss
from hsap.pytorch.trainer import HSAPTrainer

__all__ = [
    "EmpiricalDistrustLoss",
    "HSAPTrainer",
]
