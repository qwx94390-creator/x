#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

if [[ ! -f config.local.yaml ]]; then
  cp config.yaml config.local.yaml
  echo "Created config.local.yaml. Please fill notification settings if needed."
fi

python run_bot.py --config config.local.yaml --once

echo "Run continuously with:"
echo "  source .venv/bin/activate && python run_bot.py --config config.local.yaml --interval 5"
