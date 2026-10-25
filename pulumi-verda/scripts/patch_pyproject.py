#!/usr/bin/env python3
"""Patch metadata into the codegen'd sdk/pyproject.toml.

`pulumi package add terraform-provider` overwrites sdk/pyproject.toml on every
`make sdk` run, so PyPI-facing metadata (license, authors, classifiers, our
repo URL) can't live in the generated file directly. This script re-applies it
after each regeneration; see the `sdk` target in ../Makefile.
"""
import pathlib
import re
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
PYPROJECT = ROOT / "sdk" / "pyproject.toml"

REPO_URL = "https://github.com/hrishin/pulumi-providers"
UPSTREAM_REPOSITORY_URL = "https://github.com/verda-cloud/terraform-provider-verda"

EXTRA_PROJECT_FIELDS = """  license = "MIT"
  license-files = ["LICENSE"]
  authors = [{ name = "Hrishikesh Shinde", email = "hello@hrishi.dev" }]
  classifiers = [
    "Programming Language :: Python :: 3",
    "Intended Audience :: Developers",
    "Operating System :: OS Independent",
    "Topic :: Software Development :: Build Tools",
  ]
"""

# PEP 639 SPDX `license = "..."` strings require setuptools >= 77.0.3; the
# codegen'd file pins an older floor that predates that support.
MIN_SETUPTOOLS = 'requires = ["setuptools>=61.0"]'
MIN_SETUPTOOLS_PATCHED = 'requires = ["setuptools>=77.0.3"]'


def main() -> None:
    # `pyproject.toml`'s `readme = "README.md"` field points at sdk/README.md,
    # and `license-files` needs sdk/LICENSE -- neither is produced by codegen,
    # so copy both in from the repo root.
    shutil.copyfile(ROOT / "README.md", ROOT / "sdk" / "README.md")
    shutil.copyfile(ROOT.parent / "LICENSE", ROOT / "sdk" / "LICENSE")

    text = PYPROJECT.read_text()

    if "license = " not in text:
        text, count = re.subn(
            r'(  description = ".*"\n)',
            r"\1" + EXTRA_PROJECT_FIELDS,
            text,
            count=1,
        )
        if count == 0:
            raise SystemExit(f"could not find description field to anchor on in {PYPROJECT}")

    text = text.replace(
        f'Repository = "{UPSTREAM_REPOSITORY_URL}"',
        f'Repository = "{REPO_URL}"\n'
        f'    Homepage = "{REPO_URL}/tree/main/pulumi-verda"\n'
        f'    "Bug Tracker" = "{REPO_URL}/issues"',
    )

    text = text.replace(MIN_SETUPTOOLS, MIN_SETUPTOOLS_PATCHED)

    PYPROJECT.write_text(text)
    print(f"patched {PYPROJECT}")


if __name__ == "__main__":
    main()
