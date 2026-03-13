#!/bin/bash
# Quick smoke test runner

set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$PROJECT_ROOT"

if [ -f ".venv/bin/python" ]; then
  PYTHON_BIN=".venv/bin/python"
else
  PYTHON_BIN="python3"
fi

export MOCK_MODE=true
export PYTHONPATH="$PROJECT_ROOT:${PYTHONPATH:-}"

echo "Running smoke tests..."
$PYTHON_BIN -m pytest -q -m smoke tests/smoke_test.py
echo "Smoke tests passed."
