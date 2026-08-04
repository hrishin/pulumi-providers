#!/usr/bin/env bash
# Upload sdk/dist/* to PyPI (default) or TestPyPI (--test).
#
# Local/manual use only. CI publishes via OIDC trusted publishing
# (see .github/workflows/pulumi-nebius-pypi-publish.yml) and does not call
# this script. Requires PYPI_API_TOKEN: an API token starting with "pypi-",
# scoped to this project, from https://pypi.org/manage/account/token/ (or
# https://test.pypi.org/manage/account/token/ for --test).
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

repository_url="https://upload.pypi.org/legacy/"
if [[ "${1:-}" == "--test" ]]; then
  repository_url="https://test.pypi.org/legacy/"
fi

: "${PYPI_API_TOKEN:?Set PYPI_API_TOKEN to a PyPI/TestPyPI API token}"

if ! compgen -G "sdk/dist/*" > /dev/null; then
  echo "sdk/dist/ is empty -- run scripts/build.sh (or 'make dist') first" >&2
  exit 1
fi

python3 -m twine upload \
  --repository-url "$repository_url" \
  --username __token__ \
  --password "$PYPI_API_TOKEN" \
  sdk/dist/*
