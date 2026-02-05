#!/usr/bin/env python3
"""
HSAP Basic Training Example - MNIST with Empirical Distrust Loss

This example demonstrates:
1. Creating attestations for training data (simulating human vs AI-generated)
2. Training a model with HSAP loss
3. Comparing model performance with and without HSAP

Usage:
    python basic_training.py --use-hsap
    python basic_training.py --no-hsap
"""

import argparse
import random
import tempfile
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset, Subset
from torchvision import datasets, transforms

from hsap import HSAPCore, EmpiricalDistrustLoss


class SimpleNet(nn.Module):
    """Simple CNN for MNIST classification."""

    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, 1)
        self.conv2 = nn.Conv2d(32, 64, 3, 1)
        self.dropout1 = nn.Dropout(0.25)
        self.dropout2 = nn.Dropout(0.5)
        self.fc1 = nn.Linear(9216, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.conv1(x)
        x = torch.relu(x)
        x = self.conv2(x)
        x = torch.relu(x)
        x = torch.max_pool2d(x, 2)
        x = self.dropout1(x)
        x = torch.flatten(x, 1)
        x = self.fc1(x)
        x = torch.relu(x)
        x = self.dropout2(x)
        x = self.fc2(x)
        return x


class HSAPDataset(Dataset):
    """
    Wrapper dataset that includes item IDs for HSAP attestation lookup.

    Simulates a mixed dataset where some samples are "human-originated"
    and others are "AI-generated" with higher depth.
    """

    def __init__(
        self,
        base_dataset: Dataset,
        hsap_core: HSAPCore,
        human_ratio: float = 0.7,
    ):
        """
        Args:
            base_dataset: Underlying PyTorch dataset
            hsap_core: HSAPCore instance for attestation
            human_ratio: Fraction of samples to mark as human-originated (d=0)
        """
        self.base_dataset = base_dataset
        self.hsap_core = hsap_core
        self.human_ratio = human_ratio
        self.item_ids = []
        self.attestations = []

        # Create attestations for all samples
        self._create_attestations()

    def _create_attestations(self):
        """Create attestations for all samples, simulating mixed provenance."""
        print(f"Creating attestations for {len(self.base_dataset)} samples...")

        # Create some "human" root sources first
        num_human = int(len(self.base_dataset) * self.human_ratio)
        human_indices = set(random.sample(range(len(self.base_dataset)), num_human))

        # Attest human samples (d=0, A(x)=1.0)
        human_parent_ids = []
        for i in range(len(self.base_dataset)):
            # Create a unique identifier based on sample data
            sample, label = self.base_dataset[i]
            sample_bytes = sample.numpy().tobytes()

            if i in human_indices:
                # Human-originated data (root source)
                result = self.hsap_core.attest_root_source(
                    data=sample_bytes,
                    metadata={"index": i, "label": int(label), "source": "human"}
                )
                human_parent_ids.append(result["item_id"])
            else:
                # AI-generated data (derived from random human samples)
                # Simulate different depths by varying the derivation chain
                depth_level = random.randint(1, 3)

                if depth_level == 1 and human_parent_ids:
                    # Direct derivative of human data (d=1)
                    parent = random.choice(human_parent_ids)
                    result = self.hsap_core.attest_derived(
                        data=sample_bytes,
                        parents=[parent],
                        transformation="ai_generation_d1",
                        metadata={"index": i, "label": int(label), "source": "ai"}
                    )
                elif depth_level == 2 and len(self.item_ids) > 0:
                    # Derivative of derivative (d=2)
                    # Pick a recent item as parent
                    parent = random.choice(self.item_ids[-min(100, len(self.item_ids)):])
                    result = self.hsap_core.attest_derived(
                        data=sample_bytes,
                        parents=[parent],
                        transformation="ai_generation_d2",
                        metadata={"index": i, "label": int(label), "source": "ai"}
                    )
                else:
                    # Deeper derivative (d=3+)
                    if len(self.item_ids) >= 2:
                        parents = random.sample(
                            self.item_ids[-min(50, len(self.item_ids)):],
                            min(2, len(self.item_ids))
                        )
                    elif self.item_ids:
                        parents = [self.item_ids[-1]]
                    else:
                        # Fallback to human if no items yet
                        result = self.hsap_core.attest_root_source(
                            data=sample_bytes,
                            metadata={"index": i, "label": int(label), "source": "human"}
                        )
                        self.item_ids.append(result["item_id"])
                        self.attestations.append(result)
                        continue

                    result = self.hsap_core.attest_derived(
                        data=sample_bytes,
                        parents=parents,
                        transformation="ai_generation_d3+",
                        metadata={"index": i, "label": int(label), "source": "ai"}
                    )

            self.item_ids.append(result["item_id"])
            self.attestations.append(result)

            if (i + 1) % 1000 == 0:
                print(f"  Attested {i + 1}/{len(self.base_dataset)} samples...")

        # Print statistics
        depths = [a["depth"] for a in self.attestations]
        scores = [a["attestation_score"] for a in self.attestations]
        print(f"\nAttestation Statistics:")
        print(f"  Total samples: {len(self.attestations)}")
        print(f"  Human (d=0): {depths.count(0)} ({depths.count(0)/len(depths)*100:.1f}%)")
        print(f"  AI-derived: {len(depths) - depths.count(0)} ({(len(depths)-depths.count(0))/len(depths)*100:.1f}%)")
        print(f"  Avg depth: {sum(depths)/len(depths):.2f}")
        print(f"  Avg A(x): {sum(scores)/len(scores):.4f}")

    def __len__(self):
        return len(self.base_dataset)

    def __getitem__(self, idx):
        sample, label = self.base_dataset[idx]
        item_id = self.item_ids[idx]
        attestation_score = self.attestations[idx]["attestation_score"]
        return sample, label, item_id, attestation_score


def train_epoch(model, loader, optimizer, loss_fn, device, use_hsap=True):
    """Train for one epoch."""
    model.train()
    total_loss = 0
    correct = 0
    total = 0

    for batch in loader:
        if use_hsap:
            inputs, targets, item_ids, scores = batch
            scores = scores.to(device)
        else:
            inputs, targets = batch[:2]
            scores = torch.ones(inputs.shape[0], device=device)  # All trusted

        inputs, targets = inputs.to(device), targets.to(device)

        optimizer.zero_grad()
        outputs = model(inputs)

        if use_hsap:
            loss = loss_fn(outputs, targets, scores)
        else:
            # Standard loss without HSAP
            base_loss = nn.CrossEntropyLoss()
            loss = base_loss(outputs, targets)

        loss.backward()
        optimizer.step()

        total_loss += loss.item() * inputs.shape[0]
        _, predicted = outputs.max(1)
        total += targets.size(0)
        correct += predicted.eq(targets).sum().item()

    return total_loss / total, 100. * correct / total


def evaluate(model, loader, device):
    """Evaluate model on a dataset."""
    model.eval()
    correct = 0
    total = 0

    with torch.no_grad():
        for batch in loader:
            inputs, targets = batch[0], batch[1]
            inputs, targets = inputs.to(device), targets.to(device)

            outputs = model(inputs)
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()

    return 100. * correct / total


def main():
    parser = argparse.ArgumentParser(description="HSAP MNIST Training Example")
    parser.add_argument("--use-hsap", action="store_true", default=True,
                        help="Train with HSAP loss (default)")
    parser.add_argument("--no-hsap", action="store_true",
                        help="Train without HSAP loss (baseline)")
    parser.add_argument("--epochs", type=int, default=5, help="Number of epochs")
    parser.add_argument("--batch-size", type=int, default=64, help="Batch size")
    parser.add_argument("--lr", type=float, default=0.001, help="Learning rate")
    parser.add_argument("--lambda-param", type=float, default=0.1,
                        help="HSAP distrust penalty weight")
    parser.add_argument("--human-ratio", type=float, default=0.7,
                        help="Fraction of data to mark as human-originated")
    parser.add_argument("--subset", type=int, default=5000,
                        help="Use subset of data for faster demo")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    use_hsap = not args.no_hsap

    # Set seeds
    torch.manual_seed(args.seed)
    random.seed(args.seed)

    # Device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Data transforms
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])

    # Load MNIST
    print("\nLoading MNIST dataset...")
    train_full = datasets.MNIST("./data", train=True, download=True, transform=transform)
    test_full = datasets.MNIST("./data", train=False, transform=transform)

    # Use subset for demo
    if args.subset and args.subset < len(train_full):
        train_indices = random.sample(range(len(train_full)), args.subset)
        train_base = Subset(train_full, train_indices)
    else:
        train_base = train_full

    test_indices = random.sample(range(len(test_full)), min(1000, len(test_full)))
    test_data = Subset(test_full, test_indices)

    # Initialize HSAP with temporary database
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "provenance.db"
        hsap_core = HSAPCore(gamma=0.9, tau=0.5, db_path=str(db_path))

        print(f"\nHSAP Parameters: γ={hsap_core.gamma}, τ={hsap_core.tau}, λ={args.lambda_param}")
        print(f"Mode: {'HSAP-enabled' if use_hsap else 'Baseline (no HSAP)'}")

        # Create HSAP dataset with attestations
        if use_hsap:
            train_data = HSAPDataset(train_base, hsap_core, human_ratio=args.human_ratio)
        else:
            train_data = train_base

        # DataLoaders
        train_loader = DataLoader(train_data, batch_size=args.batch_size, shuffle=True)
        test_loader = DataLoader(test_data, batch_size=args.batch_size, shuffle=False)

        # Model
        model = SimpleNet().to(device)
        optimizer = optim.Adam(model.parameters(), lr=args.lr)

        # Loss function
        if use_hsap:
            base_loss = nn.CrossEntropyLoss(reduction="none")
            loss_fn = EmpiricalDistrustLoss(base_loss, lambda_param=args.lambda_param)
        else:
            loss_fn = nn.CrossEntropyLoss()

        # Training
        print(f"\nTraining for {args.epochs} epochs...")
        print("-" * 50)

        for epoch in range(1, args.epochs + 1):
            train_loss, train_acc = train_epoch(
                model, train_loader, optimizer, loss_fn, device, use_hsap
            )
            test_acc = evaluate(model, test_loader, device)

            print(f"Epoch {epoch}/{args.epochs}: "
                  f"Loss={train_loss:.4f}, "
                  f"Train Acc={train_acc:.2f}%, "
                  f"Test Acc={test_acc:.2f}%")

        print("-" * 50)
        print(f"\nFinal Test Accuracy: {test_acc:.2f}%")

        # Print HSAP statistics
        if use_hsap:
            stats = hsap_core.get_statistics()
            print(f"\nHSAP Statistics:")
            print(f"  Total attested items: {stats['total_items']}")
            print(f"  Root sources (d=0): {stats['root_sources']}")
            print(f"  Average depth: {stats['average_depth']}")
            print(f"  Average A(x): {stats['average_attestation_score']:.4f}")


if __name__ == "__main__":
    main()
