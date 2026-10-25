#!/usr/bin/env bash
# Build the pulumi_verda sdist + wheel for PyPI into sdk/dist/.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

rm -rf sdk/dist sdk/build sdk/*.egg-info

# Use uv if available (no separate venv needed); fall back to python3 -m build
if command -v uv >/dev/null 2>&1; then
  uv build sdk --out-dir sdk/dist
  uv tool run twine check sdk/dist/*
else
  python3 -m pip install --quiet --upgrade build twine
  python3 -m build sdk
  python3 -m twine check sdk/dist/*
fi

echo "Built:"
ls -1 sdk/dist
