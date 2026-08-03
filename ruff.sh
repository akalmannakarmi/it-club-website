#!/bin/bash
# Exit on error
set -e

# Prefer the venv's ruff (ENV/), fall back to whatever is on PATH
RUFF=""
if [ -x "ENV/bin/ruff" ]; then
  RUFF="ENV/bin/ruff"
elif command -v ruff >/dev/null 2>&1; then
  RUFF="ruff"
else
  echo "ERROR: ruff not found. Install requirements: pip install -r requirements.txt"
  exit 1
fi

echo "Running ruff lint..."
"$RUFF" check .

echo "Auto-fixing issues..."
"$RUFF" check . --fix

echo "Formatting code..."
"$RUFF" format .

echo "Ruff completed successfully"