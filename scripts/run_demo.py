"""Full demo startup: generate data -> train model -> start API server.

Usage:
    python scripts/run_demo.py              # start server (generates data if needed)
    python scripts/run_demo.py --reseed     # force regenerate data + retrain
    python scripts/run_demo.py --port 8000  # custom port
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

_GRAPH_PATH = Path("data/processed/graph.pkl")
_ALERTS_PATH = Path("data/processed/alerts.json")


def main() -> None:
    parser = argparse.ArgumentParser(description="TRACE.ai demo server")
    parser.add_argument("--reseed", action="store_true", help="Force regenerate data + retrain")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()

    print("=" * 60)
    print("TRACE.ai  --  Anti Money Laundering Detection System")
    print("=" * 60)

    if args.reseed or not _GRAPH_PATH.exists() or not _ALERTS_PATH.exists():
        print("\nRunning seed pipeline...")
        result = subprocess.run(
            [sys.executable, "scripts/seed_demo.py"],
            check=False,
        )
        if result.returncode != 0:
            print("seed_demo.py failed. Check logs above.")
            sys.exit(1)
    else:
        print(f"\nUsing existing data: {_GRAPH_PATH}, {_ALERTS_PATH}")

    print(f"\nStarting FastAPI server on http://{args.host}:{args.port}")
    print("  /docs          -- Interactive API docs")
    print("  /health        -- Health check")
    print("  /graph         -- Full graph visualization data")
    print("  /alerts        -- Alert list")
    print("  /investigate   -- NL copilot")
    print("  /ws/alerts     -- WebSocket real-time stream")
    print("\nPress Ctrl+C to stop.\n")

    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "trace.api.main:app",
        "--host", args.host,
        "--port", str(args.port),
        "--workers", str(args.workers),
        "--reload",
    ])


if __name__ == "__main__":
    main()
