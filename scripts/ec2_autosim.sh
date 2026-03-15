#!/usr/bin/env bash
# -------------------------------------------------------------------
# EC2 Bootstrap for AutoSIM parameter optimization
#
# Launch a spot instance and run this script to optimize SIMSIV parameters
# on cheap cloud compute. Designed for Amazon Linux 2023 / Ubuntu 22.04+.
#
# Quick start:
#   1. Launch a c7a.8xlarge spot instance (~$0.40/hr spot)
#   2. SSH in, clone repo, run this script:
#
#      git clone https://github.com/kepiCHelaSHen/SIMSIV.git
#      cd SIMSIV
#      bash scripts/ec2_autosim.sh --experiments 2000 --seeds 5 --workers 16
#
#   3. Results land in autosim/journal.jsonl and autosim/best_config.yaml
#   4. scp those files back to your local machine
#
# Instance recommendations:
#   c7a.4xlarge  (16 vCPU)  — good for --workers 8 --seeds 4   (~$0.20/hr spot)
#   c7a.8xlarge  (32 vCPU)  — good for --workers 16 --seeds 5  (~$0.40/hr spot)
#   c7a.16xlarge (64 vCPU)  — good for --workers 32 --seeds 5  (~$0.80/hr spot)
#
# The sim is pure CPU (NumPy). No GPU needed.
# -------------------------------------------------------------------

set -euo pipefail

# -- Defaults (override via CLI flags) ---------------------------------
EXPERIMENTS=1000
SEEDS=5
YEARS=150
POP=500
WORKERS=16
FRESH=""

# -- Parse args --------------------------------------------------------
while [[ $# -gt 0 ]]; do
    case $1 in
        --experiments) EXPERIMENTS="$2"; shift 2 ;;
        --seeds)       SEEDS="$2"; shift 2 ;;
        --years)       YEARS="$2"; shift 2 ;;
        --pop)         POP="$2"; shift 2 ;;
        --workers)     WORKERS="$2"; shift 2 ;;
        --fresh)       FRESH="--fresh"; shift ;;
        *)             echo "Unknown arg: $1"; exit 1 ;;
    esac
done

echo "============================================="
echo "  AutoSIM EC2 Runner"
echo "  Experiments: $EXPERIMENTS"
echo "  Seeds:       $SEEDS"
echo "  Years:       $YEARS"
echo "  Pop:         $POP"
echo "  Workers:     $WORKERS"
echo "============================================="

# -- Install system deps -----------------------------------------------
echo "[1/4] Installing system dependencies..."
if command -v apt-get &>/dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y -qq python3 python3-pip python3-venv
elif command -v dnf &>/dev/null; then
    sudo dnf install -y -q python3 python3-pip
elif command -v yum &>/dev/null; then
    sudo yum install -y -q python3 python3-pip
fi

# -- Set up venv -------------------------------------------------------
echo "[2/4] Setting up Python environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet numpy pandas pyyaml scipy

# -- Verify import works -----------------------------------------------
echo "[3/4] Verifying simulation can import..."
python3 -c "from config import Config; from simulation import Simulation; print('Import OK')"

# -- Run ----------------------------------------------------------------
echo "[4/4] Starting optimization..."
echo "  Log: autosim/journal.jsonl"
echo "  Best: autosim/best_config.yaml"
echo ""

python3 -m autosim.runner \
    --experiments "$EXPERIMENTS" \
    --seeds "$SEEDS" \
    --years "$YEARS" \
    --pop "$POP" \
    --workers "$WORKERS" \
    $FRESH \
    2>&1 | tee "autosim/run_$(date +%Y%m%d_%H%M%S).log"

echo ""
echo "Done. Results:"
echo "  autosim/journal.jsonl"
echo "  autosim/best_config.yaml"
echo ""
echo "To pull results back to your machine:"
echo "  scp -i key.pem ec2-user@<IP>:~/SIMSIV/autosim/best_config.yaml ."
echo "  scp -i key.pem ec2-user@<IP>:~/SIMSIV/autosim/journal.jsonl ."
