"""Generate synthetic banking data + build the transaction graph.

Usage:
    python scripts/generate_data.py [--accounts N] [--transactions N] [--out data/sample]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from trace.data.generator import generate
from trace.graph.builder import build_graph, save_graph


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accounts", type=int, default=5_000)
    parser.add_argument("--transactions", type=int, default=100_000)
    parser.add_argument("--out", default="data/sample")
    parser.add_argument("--graph-out", default="data/processed/graph.pkl")
    args = parser.parse_args()

    out_dir = Path(args.out)
    graph_path = Path(args.graph_out)

    print(f"Generating {args.accounts} accounts x {args.transactions} transactions...")
    accounts, transactions = generate(
        num_accounts=args.accounts,
        num_transactions=args.transactions,
        seed=42,
        output_dir=out_dir,
    )

    fraud_count = sum(1 for t in transactions if t.fraud_label)
    print(f"Generated {len(accounts)} accounts, {len(transactions)} transactions")
    print(f"Fraud transactions: {fraud_count} ({100 * fraud_count / len(transactions):.2f}%)")

    fraud_types: dict[str, int] = {}
    for t in transactions:
        if t.fraud_type:
            fraud_types[t.fraud_type] = fraud_types.get(t.fraud_type, 0) + 1
    for ftype, count in sorted(fraud_types.items()):
        print(f"  {ftype}: {count}")

    print("\nBuilding NetworkX graph...")
    g = build_graph(accounts, transactions)
    print(f"Graph: {g.number_of_nodes()} nodes, {g.number_of_edges()} edges")

    print(f"Saving graph to {graph_path}...")
    save_graph(g, graph_path)
    print(f"CSV written to {out_dir}/")
    print("Done.")


if __name__ == "__main__":
    main()
