#!/usr/bin/env bash
# Build the pulumi_nebius sdist + wheel for PyPI into sdk/dist/.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

rm -rf sdk/dist sdk/build sdk/*.egg-info
python3 -m pip install --quiet --upgrade build twine
python3 -m build sdk
python3 -m twine check sdk/dist/*

echo "Built:"
ls -1 sdk/dist
