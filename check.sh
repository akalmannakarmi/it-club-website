#!/bin/bash
# Full verification for agents.
# Run before finishing ANY change:  bash check.sh
#
# Runs, in order:
#   1. ruff lint + autofix + format
#   2. Django system checks (URLs, models, settings)
#   3. makemigrations --check  (fails if models changed without a migration)
#   4. the Django test suite
#
# Everything runs with DATABASE_MODE=sqlite so it works without Docker/MySQL.
set -e

PY=""
if [ -x "ENV/bin/python" ]; then
  PY="ENV/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PY="python3"
else
  PY="python"
fi

echo "▶ 1/4 ruff (lint + autofix + format)"
bash ruff.sh

echo "▶ 2/4 Django system checks"
DATABASE_MODE=sqlite "$PY" manage.py check

echo "▶ 3/4 Missing migrations?"
DATABASE_MODE=sqlite "$PY" manage.py makemigrations --check --dry-run

echo "▶ 4/4 Tests"
DATABASE_MODE=sqlite "$PY" manage.py test

echo
echo "✔ All checks passed."
