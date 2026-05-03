"""Generate AMLSim synthetic data + Indian banking augmentation.

Usage:
    python scripts/generate_data.py --num-accounts 5000 --num-transactions 100000
"""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-accounts", type=int, default=5_000)
    parser.add_argument("--num-transactions", type=int, default=100_000)
    parser.add_argument("--out", default="data/raw/")
    args = parser.parse_args()
    print(f"[scaffold] would generate {args.num_accounts} accounts x {args.num_transactions} txns into {args.out}")


if __name__ == "__main__":
    main()
