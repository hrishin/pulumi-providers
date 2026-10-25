PROVIDER_VERSION ?= 1.1.4
PROVIDER_NAME    := verda
TF_REGISTRY      := registry.terraform.io/verda-cloud/verda
PYTHON           := python3

# Scratch project used to drive `pulumi package add`
SCRATCH_DIR := /tmp/pulumi-verda-scratch

.DEFAULT_GOAL := sdk

# ── Generate Python SDK ────────────────────────────────────────────────────────
# Downloads the Terraform provider binary at runtime via pulumi-terraform-provider
# (no Go compilation required) and generates sdk/ from its embedded schema.
#
# Usage:  make sdk              — regenerate from current PROVIDER_VERSION
#         make sdk VERSION=x.y.z

.PHONY: sdk
sdk:
	@[ -n "$(VERSION)" ] && $(MAKE) _bump VERSION=$(VERSION) || true
	rm -rf $(SCRATCH_DIR)
	mkdir -p $(SCRATCH_DIR)
	printf 'name: verda-scratch\nruntime: python\n' > $(SCRATCH_DIR)/Pulumi.yaml
	cd $(SCRATCH_DIR) && pulumi package add terraform-provider \
	    $(TF_REGISTRY) $(PROVIDER_VERSION) 2>&1 \
	    | grep -v "^warning:" | grep -v "^error: linking package" || true
	rm -rf sdk
	cp -r $(SCRATCH_DIR)/sdks/verda sdk
	rm -rf $(SCRATCH_DIR)
	$(PYTHON) scripts/patch_pyproject.py
	@echo "SDK generated: sdk/pulumi_verda/  (version $(PROVIDER_VERSION))"

# ── Install Python SDK into the active venv ────────────────────────────────────

.PHONY: install
install: sdk
	$(PYTHON) -m pip install -e sdk
	@echo "pulumi_verda $(PROVIDER_VERSION) installed."

# ── Full pipeline ──────────────────────────────────────────────────────────────

.PHONY: all
all: install
	@echo "Done. pulumi_verda $(PROVIDER_VERSION) ready."

# ── Version bump (internal) ───────────────────────────────────────────────────
# Updates Makefile pin and pyproject.toml version string.

.PHONY: _bump
_bump:
	@[ -n "$(VERSION)" ] || (echo "Usage: make sdk VERSION=x.y.z"; exit 1)
	sed -i 's/^PROVIDER_VERSION ?= .*/PROVIDER_VERSION ?= $(VERSION)/' Makefile

# ── Convenience target for CI ─────────────────────────────────────────────────

.PHONY: bump
bump:
	@[ -n "$(VERSION)" ] || (echo "Usage: make bump VERSION=x.y.z"; exit 1)
	$(MAKE) _bump VERSION=$(VERSION)
	@echo "Version pinned to $(VERSION). Run 'make sdk' to regenerate."

# ── Build & publish to PyPI ────────────────────────────────────────────────────
# publish/publish-test are for local/manual use; CI publishes via OIDC trusted
# publishing (see .github/workflows/pulumi-verda-pypi-publish.yml) instead.

.PHONY: dist
dist:
	scripts/build.sh

.PHONY: publish-test
publish-test: dist
	scripts/publish.sh --test

.PHONY: publish
publish: dist
	scripts/publish.sh
