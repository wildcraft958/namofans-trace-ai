"""Train the Temporal Graph Network (TGN) AML classifier.

Usage:
    python scripts/train_tgn.py [--accounts N] [--txns N] [--epochs N] [--seed N]

Generates the synthetic dataset, builds the transaction graph, trains TGN,
and reports train/test AUC.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Ensure project src is on path when run as a script
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT / "src"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Train TGN fraud classifier")
    parser.add_argument("--accounts", type=int, default=5_000, help="Number of synthetic accounts")
    parser.add_argument("--txns", type=int, default=100_000, help="Number of synthetic transactions")
    parser.add_argument("--epochs", type=int, default=None, help="Override training epochs")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed")
    parser.add_argument("--amlsim", type=str, default=None, metavar="DIR",
                        help="Use real IBM AMLSim output directory instead of synthetic data")
    args = parser.parse_args()

    if args.epochs is not None:
        import trace.detection.tgn_classifier as tgn_mod
        tgn_mod._EPOCHS = args.epochs

    print("=" * 60)
    print("  TRACE.ai — TGN Classifier Training")
    print("=" * 60)
    if args.amlsim:
        print(f"  data source : IBM AMLSim ({args.amlsim})")
    else:
        print(f"  accounts   : {args.accounts:,}")
        print(f"  transactions: {args.txns:,}")
        print(f"  seed       : {args.seed}")
    print()

    # ── 1. Load data ──────────────────────────────────────────────────────────
    from trace.graph.builder import build_graph

    import pandas as pd

    if args.amlsim:
        from pathlib import Path
        from trace.data.amlsim_loader import load as amlsim_load
        print(f"[1/3] Loading IBM AMLSim data from {args.amlsim} ...")
        t0 = time.time()
        result = amlsim_load(Path(args.amlsim))
        if result is None:
            raise RuntimeError(f"No valid AMLSim CSVs found in {args.amlsim}")
        accounts, transactions = result
        g = build_graph(accounts, transactions)
        print(f"      Done in {time.time() - t0:.1f}s  |  nodes={g.number_of_nodes():,}  edges={g.number_of_edges():,}")

        all_account_ids = list(g.nodes())
        # Fraud label comes from kyc_risk=HIGH (isFraud=1 in AMLSim)
        fraud_set = {a.account_id for a in accounts if a.kyc_risk == "HIGH"}
    else:
        from trace.data.generator import generate
        print("[1/3] Generating synthetic banking dataset...")
        t0 = time.time()
        accounts, transactions = generate(
            num_accounts=args.accounts,
            num_transactions=args.txns,
            seed=args.seed,
        )
        g = build_graph(accounts, transactions)
        print(f"      Done in {time.time() - t0:.1f}s  |  nodes={g.number_of_nodes():,}  edges={g.number_of_edges():,}")

        all_account_ids = list(g.nodes())
        fraud_set = {a for a in all_account_ids if str(a).startswith("RING-")}

    # ── 2. Build labels ───────────────────────────────────────────────────────
    print("[2/3] Building fraud labels...")
    labels = pd.Series(
        {a: (1 if a in fraud_set else 0) for a in all_account_ids},
        name="fraud",
    )
    # Minimal feature_df — tgn_classifier.train() only uses labels; feature_df is
    # accepted for API compatibility but not used for TGN training.
    feature_df = pd.DataFrame(index=all_account_ids)

    print(f"      Fraud accounts: {int(labels.sum())} / {len(labels)}")

    # ── 3. Train TGN ──────────────────────────────────────────────────────────
    print("[3/3] Training TGN classifier...")
    t1 = time.time()
    try:
        from trace.detection import tgn_classifier
        _model, train_auc, test_auc = tgn_classifier.train(
            feature_df=feature_df,
            labels=labels,
            graph=g,
            transactions=transactions,
            save=True,
        )
    except Exception as exc:
        print(f"\n[ERROR] TGN training failed: {exc}")
        print("        XGBoost fallback is still available via gnn_classifier.py")
        raise

    elapsed = time.time() - t1
    print()
    print("=" * 60)
    print(f"  Training complete in {elapsed:.1f}s")
    print(f"  Train AUC : {train_auc:.4f}")
    print(f"  Test AUC  : {test_auc:.4f}")
    print("=" * 60)


if __name__ == "__main__":
    main()
