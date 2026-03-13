#!/bin/bash
# CI-like local test pipeline

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

echo "Step 1/3: smoke tests"
$PYTHON_BIN -m pytest -q -m smoke tests/smoke_test.py

echo "Step 2/3: unit tests"
$PYTHON_BIN -m pytest -q -m unit tests

echo "Step 3/3: integration tests"
$PYTHON_BIN -m pytest -q -m integration tests/comprehensive_test.py tests/test_langgraph_workflow.py tests/test_api.py

echo "All CI-like tests passed."
