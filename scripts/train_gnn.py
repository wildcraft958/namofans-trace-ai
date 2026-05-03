"""Train GraphSAGE classifier on AMLSim. Run on Kaggle T4 (free tier).

Usage:
    python scripts/train_gnn.py --epochs 50 --hidden 64
"""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--hidden", type=int, default=64)
    parser.add_argument("--data", default="data/processed/amlsim.pyg")
    parser.add_argument("--out", default="models/graphsage.pt")
    args = parser.parse_args()
    print(f"[scaffold] would train GraphSAGE with hidden={args.hidden} for {args.epochs} epochs")


if __name__ == "__main__":
    main()
