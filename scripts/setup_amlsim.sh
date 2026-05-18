#!/usr/bin/env bash
# setup_amlsim.sh -- Clone IBM AMLSim and run it with the TRACE.ai config.
#
# Usage:
#   bash scripts/setup_amlsim.sh
#
# Outputs: data/amlsim/{accounts.csv,transactions.csv,alert_accounts.csv}
# which are picked up automatically by generate_from_amlsim() in generator.py.

set -euo pipefail

REPO_URL="https://github.com/IBM/AMLSim.git"
TOOL_DIR="amlsim_tool"
CONFIG="amlsim_config/trace_config.json"
OUT_DIR="data/amlsim"

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "======================================================"
echo " TRACE.ai -- IBM AMLSim setup"
echo "======================================================"

# ── 1. Clone AMLSim if not already present ──────────────────────────────
if [ -d "$TOOL_DIR/.git" ]; then
    echo "[1/4] AMLSim already cloned at $TOOL_DIR, skipping clone."
else
    echo "[1/4] Cloning IBM AMLSim from $REPO_URL ..."
    if ! git clone "$REPO_URL" "$TOOL_DIR"; then
        echo ""
        echo "ERROR: git clone failed. Possible causes:"
        echo "  - No internet access"
        echo "  - GitHub is unreachable from this machine"
        echo ""
        echo "FALLBACK: The sample AMLSim CSVs in data/amlsim/ will be used instead."
        echo "  They contain 50 accounts and 60 transactions covering all typologies."
        echo "  Replace with real AMLSim output when internet is available."
        exit 1
    fi
fi

# ── 2. Check Java ────────────────────────────────────────────────────────
echo "[2/4] Checking Java version..."
java -version 2>&1 | head -1
JAVA_VER=$(java -version 2>&1 | awk -F '"' '/version/ {print $2}' | cut -d. -f1)
if [ "$JAVA_VER" -lt 11 ]; then
    echo "ERROR: Java 11+ required. Found Java $JAVA_VER."
    exit 1
fi

# ── 3. Prepare output directory ──────────────────────────────────────────
echo "[3/4] Preparing output directory: $OUT_DIR"
mkdir -p "$OUT_DIR"

# ── 4. Run AMLSim ────────────────────────────────────────────────────────
echo "[4/4] Running AMLSim with config: $CONFIG"

# AMLSim can be run via Python wrapper or directly via Java JAR.
# Try Python wrapper first; fall back to Java JAR.
PYTHON_SCRIPT="$TOOL_DIR/scripts/run_AMLSim.py"
JAVA_JAR="$TOOL_DIR/jars/AMLSim.jar"
JAVA_JAR_ALT="$TOOL_DIR/target/AMLSim.jar"

if [ -f "$PYTHON_SCRIPT" ]; then
    echo "  Using Python wrapper: $PYTHON_SCRIPT"
    python3 "$PYTHON_SCRIPT" --config "$CONFIG"
elif [ -f "$JAVA_JAR" ]; then
    echo "  Using JAR: $JAVA_JAR"
    java -jar "$JAVA_JAR" "$CONFIG"
elif [ -f "$JAVA_JAR_ALT" ]; then
    echo "  Using JAR: $JAVA_JAR_ALT"
    java -jar "$JAVA_JAR_ALT" "$CONFIG"
else
    echo ""
    echo "ERROR: Cannot find AMLSim runner. Expected one of:"
    echo "  $PYTHON_SCRIPT"
    echo "  $JAVA_JAR"
    echo "  $JAVA_JAR_ALT"
    echo ""
    echo "The repo may need to be built first. From $TOOL_DIR/:"
    echo "  mvn package -DskipTests"
    echo "Then re-run this script."
    exit 1
fi

echo ""
echo "======================================================"
echo " AMLSim run complete!"
echo " Output files:"
ls -lh "$OUT_DIR"/*.csv 2>/dev/null || echo "  (none found -- check AMLSim output path in config)"
echo ""
echo " Now run: python scripts/seed_demo.py"
echo "======================================================"
