"""
HSAP Trainer - Training loop wrapper for HSAP-compliant model training.

Integrates HSAP attestation checking and Empirical Distrust Loss
into standard PyTorch training workflows.
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field

from hsap.core.attestation import HSAPCore
from hsap.pytorch.loss import EmpiricalDistrustLoss


@dataclass
class HSAPTrainingMetrics:
    """Metrics tracked during HSAP training."""
    epoch: int = 0
    train_loss: float = 0.0
    base_loss: float = 0.0
    distrust_penalty: float = 0.0
    avg_attestation_score: float = 0.0
    compliant_ratio: float = 0.0
    samples_processed: int = 0


class HSAPTrainer:
    """
    Training wrapper that integrates HSAP into PyTorch training loops.

    Features:
    - Automatic attestation score lookup for batches
    - EmpiricalDistrustLoss integration
    - Training metrics tracking
    - Optional filtering of non-compliant data
    """

    def __init__(
        self,
        model: nn.Module,
        optimizer: torch.optim.Optimizer,
        hsap_core: HSAPCore,
        base_loss: nn.Module,
        lambda_param: float = 0.1,
        device: Optional[torch.device] = None,
        filter_non_compliant: bool = False,
    ):
        """
        Initialize HSAPTrainer.

        Args:
            model: PyTorch model to train
            optimizer: Optimizer for training
            hsap_core: HSAPCore instance for attestation lookups
            base_loss: Base loss function (e.g., nn.CrossEntropyLoss)
            lambda_param: Weight for distrust penalty (λ)
            device: Device to train on. Auto-detected if None.
            filter_non_compliant: If True, skip non-compliant samples during training
        """
        self.model = model
        self.optimizer = optimizer
        self.hsap_core = hsap_core
        self.lambda_param = lambda_param
        self.filter_non_compliant = filter_non_compliant

        # Set device
        if device is None:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.device = device
        self.model.to(device)

        # Create HSAP loss
        self.loss_fn = EmpiricalDistrustLoss(base_loss, lambda_param)

        # Metrics tracking
        self.metrics_history: List[HSAPTrainingMetrics] = []
        self.current_epoch = 0

    def get_attestation_scores(self, item_ids: List[str]) -> torch.Tensor:
        """
        Get attestation scores for a batch of items.

        Args:
            item_ids: List of item identifiers

        Returns:
            Tensor of attestation scores
        """
        scores = self.hsap_core.get_scores_batch(item_ids)
        return torch.tensor(scores, dtype=torch.float32, device=self.device)

    def train_step(
        self,
        inputs: torch.Tensor,
        targets: torch.Tensor,
        item_ids: List[str],
    ) -> Tuple[float, Dict[str, float]]:
        """
        Execute a single training step with HSAP loss.

        Args:
            inputs: Input tensor (batch_size, ...)
            targets: Target tensor (batch_size, ...)
            item_ids: List of item IDs for attestation lookup

        Returns:
            Tuple of (loss_value, metrics_dict)
        """
        self.model.train()

        # Get attestation scores
        attestation_scores = self.get_attestation_scores(item_ids)

        # Filter non-compliant if requested
        if self.filter_non_compliant:
            compliant_mask = attestation_scores > self.hsap_core.tau
            if compliant_mask.sum() == 0:
                return 0.0, {"skipped": True, "reason": "no_compliant_samples"}

            inputs = inputs[compliant_mask]
            targets = targets[compliant_mask]
            attestation_scores = attestation_scores[compliant_mask]
            item_ids = [id for id, c in zip(item_ids, compliant_mask.tolist()) if c]

        # Move to device
        inputs = inputs.to(self.device)
        targets = targets.to(self.device)

        # Forward pass
        self.optimizer.zero_grad()
        outputs = self.model(inputs)

        # Compute HSAP loss
        loss = self.loss_fn(outputs, targets, attestation_scores)

        # Backward pass
        loss.backward()
        self.optimizer.step()

        # Compute metrics
        with torch.no_grad():
            avg_score = attestation_scores.mean().item()
            compliant_ratio = (attestation_scores > self.hsap_core.tau).float().mean().item()

        metrics = {
            "loss": loss.item(),
            "avg_attestation_score": avg_score,
            "compliant_ratio": compliant_ratio,
            "batch_size": len(item_ids),
        }

        return loss.item(), metrics

    def train_epoch(
        self,
        dataloader: DataLoader,
        id_fn: Callable[[Any], List[str]],
    ) -> HSAPTrainingMetrics:
        """
        Train for one epoch.

        Args:
            dataloader: PyTorch DataLoader yielding (inputs, targets, ...)
            id_fn: Function to extract item IDs from a batch.
                   Signature: id_fn(batch) -> List[str]

        Returns:
            HSAPTrainingMetrics for this epoch
        """
        self.model.train()
        self.current_epoch += 1

        total_loss = 0.0
        total_score = 0.0
        total_compliant = 0.0
        total_samples = 0

        for batch in dataloader:
            # Extract inputs, targets, and IDs
            if len(batch) == 2:
                inputs, targets = batch
                item_ids = id_fn(batch)
            elif len(batch) >= 3:
                inputs, targets = batch[0], batch[1]
                item_ids = id_fn(batch)
            else:
                raise ValueError("Batch must have at least 2 elements (inputs, targets)")

            loss, metrics = self.train_step(inputs, targets, item_ids)

            if "skipped" not in metrics:
                batch_size = metrics["batch_size"]
                total_loss += loss * batch_size
                total_score += metrics["avg_attestation_score"] * batch_size
                total_compliant += metrics["compliant_ratio"] * batch_size
                total_samples += batch_size

        # Compute epoch metrics
        if total_samples > 0:
            epoch_metrics = HSAPTrainingMetrics(
                epoch=self.current_epoch,
                train_loss=total_loss / total_samples,
                avg_attestation_score=total_score / total_samples,
                compliant_ratio=total_compliant / total_samples,
                samples_processed=total_samples,
            )
        else:
            epoch_metrics = HSAPTrainingMetrics(
                epoch=self.current_epoch,
                samples_processed=0,
            )

        self.metrics_history.append(epoch_metrics)
        return epoch_metrics

    def train(
        self,
        dataloader: DataLoader,
        id_fn: Callable[[Any], List[str]],
        epochs: int = 10,
        verbose: bool = True,
    ) -> List[HSAPTrainingMetrics]:
        """
        Train for multiple epochs.

        Args:
            dataloader: PyTorch DataLoader
            id_fn: Function to extract item IDs from batch
            epochs: Number of epochs to train
            verbose: Whether to print progress

        Returns:
            List of HSAPTrainingMetrics for all epochs
        """
        metrics_list = []

        for epoch in range(epochs):
            metrics = self.train_epoch(dataloader, id_fn)
            metrics_list.append(metrics)

            if verbose:
                print(
                    f"Epoch {metrics.epoch}: "
                    f"loss={metrics.train_loss:.4f}, "
                    f"avg_A(x)={metrics.avg_attestation_score:.4f}, "
                    f"compliant={metrics.compliant_ratio:.1%}"
                )

        return metrics_list

    def evaluate(
        self,
        dataloader: DataLoader,
        id_fn: Callable[[Any], List[str]],
    ) -> Dict[str, float]:
        """
        Evaluate model on a dataset.

        Args:
            dataloader: PyTorch DataLoader for evaluation
            id_fn: Function to extract item IDs from batch

        Returns:
            Dictionary of evaluation metrics
        """
        self.model.eval()

        total_loss = 0.0
        total_score = 0.0
        total_correct = 0
        total_samples = 0

        with torch.no_grad():
            for batch in dataloader:
                if len(batch) >= 2:
                    inputs, targets = batch[0], batch[1]
                    item_ids = id_fn(batch)
                else:
                    raise ValueError("Batch must have at least 2 elements")

                inputs = inputs.to(self.device)
                targets = targets.to(self.device)
                attestation_scores = self.get_attestation_scores(item_ids)

                outputs = self.model(inputs)
                loss = self.loss_fn(outputs, targets, attestation_scores)

                # Compute accuracy for classification
                if outputs.dim() > 1 and outputs.shape[1] > 1:
                    predictions = outputs.argmax(dim=1)
                    total_correct += (predictions == targets).sum().item()

                batch_size = inputs.shape[0]
                total_loss += loss.item() * batch_size
                total_score += attestation_scores.mean().item() * batch_size
                total_samples += batch_size

        metrics = {
            "eval_loss": total_loss / total_samples if total_samples > 0 else 0,
            "avg_attestation_score": total_score / total_samples if total_samples > 0 else 0,
            "samples": total_samples,
        }

        if total_correct > 0:
            metrics["accuracy"] = total_correct / total_samples

        return metrics


def train_with_hsap(
    model: nn.Module,
    train_loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    hsap_core: HSAPCore,
    base_loss: nn.Module,
    id_fn: Callable[[Any], List[str]],
    epochs: int = 10,
    lambda_param: float = 0.1,
    device: Optional[torch.device] = None,
    verbose: bool = True,
) -> List[HSAPTrainingMetrics]:
    """
    Convenience function to train a model with HSAP loss.

    Args:
        model: PyTorch model to train
        train_loader: Training DataLoader
        optimizer: Optimizer
        hsap_core: HSAPCore instance
        base_loss: Base loss function
        id_fn: Function to extract item IDs from batch
        epochs: Number of training epochs
        lambda_param: Distrust penalty weight
        device: Training device
        verbose: Print progress

    Returns:
        List of training metrics for each epoch
    """
    trainer = HSAPTrainer(
        model=model,
        optimizer=optimizer,
        hsap_core=hsap_core,
        base_loss=base_loss,
        lambda_param=lambda_param,
        device=device,
    )

    return trainer.train(
        dataloader=train_loader,
        id_fn=id_fn,
        epochs=epochs,
        verbose=verbose,
    )
