#!/bin/bash
# Exit on error
set -e

echo "Running ruff lint..."
ruff check .

echo "Auto-fixing issues..."
ruff check . --fix

echo "Formatting code..."
ruff format .

echo "Ruff completed successfully"