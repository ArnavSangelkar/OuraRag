#!/usr/bin/env bash
set -euo pipefail
source .venv/bin/activate
python -m app.cli sync --days ${1:-120}
