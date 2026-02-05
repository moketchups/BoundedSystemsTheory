"""
HSAP Empirical Distrust Loss - PyTorch loss function implementing D7.

D7: L_HSAP = L_base + λΣ(1-A(x))·ℓ(θ,x)

This loss function penalizes low-attestation data during training,
ensuring models remain grounded in human-originated content.
"""

import torch
import torch.nn as nn
from typing import Optional, Union, List


class EmpiricalDistrustLoss(nn.Module):
    """
    Empirical Distrust Loss implementing L_HSAP = L_base + λΣ(1-A(x))·ℓ(θ,x).

    This loss function modifies standard training by:
    1. Computing the base loss ℓ(θ,x) for each sample
    2. Weighting each sample's loss by (1 - A(x)) where A(x) is attestation score
    3. Adding penalty term λ·Σ(1-A(x))·ℓ(θ,x) to encourage learning from
       high-attestation (human-originated) data

    Higher attestation scores (closer to 1.0) = lower penalty = more trusted
    Lower attestation scores (closer to 0.0) = higher penalty = less trusted
    """

    def __init__(
        self,
        base_loss: nn.Module,
        lambda_param: float = 0.1,
        reduction: str = "mean",
    ):
        """
        Initialize EmpiricalDistrustLoss.

        Args:
            base_loss: Base loss function (e.g., nn.CrossEntropyLoss, nn.MSELoss).
                       Must support reduction='none' for per-sample losses.
            lambda_param: Weight for the distrust penalty term (λ).
                         Higher values = stronger penalty for low-attestation data.
                         Default 0.1 provides moderate regularization.
            reduction: How to reduce the final loss ('mean', 'sum', or 'none').
        """
        super().__init__()

        if lambda_param < 0:
            raise ValueError("lambda_param must be non-negative")
        if reduction not in ("mean", "sum", "none"):
            raise ValueError("reduction must be 'mean', 'sum', or 'none'")

        self.base_loss = base_loss
        self.lambda_param = lambda_param
        self.reduction = reduction

        # Store the original reduction setting
        self._original_reduction = getattr(base_loss, "reduction", None)

    def forward(
        self,
        predictions: torch.Tensor,
        targets: torch.Tensor,
        attestation_scores: Union[torch.Tensor, List[float]],
    ) -> torch.Tensor:
        """
        Compute HSAP-weighted loss.

        L_HSAP = L_base + λ·Σ(1-A(x))·ℓ(θ,x)

        Args:
            predictions: Model predictions (batch_size, ...)
            targets: Ground truth targets (batch_size, ...)
            attestation_scores: Per-sample attestation scores A(x).
                               Shape (batch_size,) with values in [0, 1].
                               Can be a list of floats or a torch.Tensor.

        Returns:
            HSAP-weighted loss value
        """
        # Convert attestation scores to tensor if needed
        if isinstance(attestation_scores, list):
            attestation_scores = torch.tensor(
                attestation_scores,
                dtype=predictions.dtype,
                device=predictions.device,
            )

        # Ensure attestation scores are on the same device
        attestation_scores = attestation_scores.to(predictions.device)

        # Validate batch sizes match
        batch_size = predictions.shape[0]
        if attestation_scores.shape[0] != batch_size:
            raise ValueError(
                f"Batch size mismatch: predictions={batch_size}, "
                f"attestation_scores={attestation_scores.shape[0]}"
            )

        # Compute per-sample base loss
        # Temporarily set reduction to 'none' to get per-sample losses
        if hasattr(self.base_loss, "reduction"):
            original_reduction = self.base_loss.reduction
            self.base_loss.reduction = "none"

        per_sample_loss = self.base_loss(predictions, targets)

        # Restore original reduction
        if hasattr(self.base_loss, "reduction"):
            self.base_loss.reduction = original_reduction

        # Handle multi-dimensional losses (e.g., for images)
        # Reduce to per-sample scalar if needed
        if per_sample_loss.dim() > 1:
            per_sample_loss = per_sample_loss.view(batch_size, -1).mean(dim=1)

        # Compute distrust weights: (1 - A(x))
        # High attestation (A(x) ≈ 1) → low weight → sample trusted
        # Low attestation (A(x) ≈ 0) → high weight → sample distrusted
        distrust_weights = 1.0 - attestation_scores

        # Compute base loss (mean of per-sample losses)
        base_loss_value = per_sample_loss.mean()

        # Compute distrust penalty: λ·Σ(1-A(x))·ℓ(θ,x)
        distrust_penalty = self.lambda_param * (distrust_weights * per_sample_loss).mean()

        # Final HSAP loss
        hsap_loss = base_loss_value + distrust_penalty

        if self.reduction == "none":
            # Return per-sample losses with distrust weighting
            return per_sample_loss + self.lambda_param * distrust_weights * per_sample_loss
        elif self.reduction == "sum":
            return hsap_loss * batch_size
        else:  # mean
            return hsap_loss

    def extra_repr(self) -> str:
        """String representation for printing."""
        return f"lambda_param={self.lambda_param}, reduction={self.reduction}"


class HSAPCrossEntropyLoss(EmpiricalDistrustLoss):
    """
    Convenience class for HSAP-weighted CrossEntropyLoss.

    Commonly used for classification tasks.
    """

    def __init__(
        self,
        lambda_param: float = 0.1,
        weight: Optional[torch.Tensor] = None,
        label_smoothing: float = 0.0,
    ):
        """
        Initialize HSAP CrossEntropyLoss.

        Args:
            lambda_param: Distrust penalty weight
            weight: Per-class weights for imbalanced datasets
            label_smoothing: Label smoothing factor
        """
        base_loss = nn.CrossEntropyLoss(
            weight=weight,
            reduction="none",
            label_smoothing=label_smoothing,
        )
        super().__init__(base_loss, lambda_param)


class HSAPMSELoss(EmpiricalDistrustLoss):
    """
    Convenience class for HSAP-weighted MSELoss.

    Commonly used for regression tasks.
    """

    def __init__(self, lambda_param: float = 0.1):
        """
        Initialize HSAP MSELoss.

        Args:
            lambda_param: Distrust penalty weight
        """
        base_loss = nn.MSELoss(reduction="none")
        super().__init__(base_loss, lambda_param)
