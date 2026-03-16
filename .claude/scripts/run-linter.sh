#!/usr/bin/env bash
set -euo pipefail

if command -v ruff >/dev/null 2>&1; then
  ruff check cortex tests || true
fi

exit 0
