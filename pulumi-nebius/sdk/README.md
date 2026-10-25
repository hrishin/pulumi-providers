# pulumi-nebius

[![pulumi-nebius provider](https://github.com/hrishin/pulumi-providers/actions/workflows/pulumi-nebius-provider.yml/badge.svg)](https://github.com/hrishin/pulumi-providers/actions/workflows/pulumi-nebius-provider.yml)

Pulumi Python SDK for [Nebius AI Cloud](https://nebius.com), generated from the
[Nebius Terraform provider](https://registry.terraform.io/providers/nebius/nebius/latest)
via `pulumi package add terraform-provider`. Currently pinned to provider
version `0.6.37`.

No Go toolchain required — the Nebius Terraform binary is downloaded automatically
by the `pulumi-terraform-provider` runtime plugin on first use.

## Prerequisites

- Python 3.9+
- [Pulumi CLI](https://www.pulumi.com/docs/install/) ≥ 3.165.0
- An active Python virtual environment

## Installation

### 1. Activate your venv

```bash
source .venv/bin/activate        # from repo root
```

### 2. Install the Pulumi runtime plugin (one-time per machine)

```bash
pulumi plugin install resource terraform-provider 1.2.1
```

### 3. Install the Python SDK

```bash
pip install pulumi-nebius
```

For local development from a checkout of this repo:

```bash
pip install -e pulumi-nebius/sdk
```

### Verify

```bash
python -c "import pulumi_nebius as n; print(n.Mk8sV1Cluster)"
```

## Usage

```python
import pulumi_nebius as nebius

provider = nebius.Provider(
    "nebius",
    service_account_id="<sa-id>",
    service_account_authorized_key=open("sa-key.json").read(),
)

network = nebius.VpcV1Network(
    "network",
    metadata=nebius.ResourceMetadataArgs(
        parent_id="<project-id>",
        name="my-network",
    ),
    opts=pulumi.ResourceOptions(provider=provider),
)

subnet = nebius.VpcV1Subnet(
    "subnet",
    metadata=nebius.ResourceMetadataArgs(
        parent_id="<project-id>",
        name="my-subnet",
    ),
    spec=nebius.VpcV1SubnetSpecArgs(
        network_id=network.id,
        cidr_blocks=["10.0.0.0/24"],
    ),
    opts=pulumi.ResourceOptions(provider=provider),
)

cluster = nebius.Mk8sV1Cluster(
    "cluster",
    metadata=nebius.ResourceMetadataArgs(
        parent_id="<project-id>",
        name="my-cluster",
    ),
    spec=nebius.Mk8sV1ClusterSpecArgs(
        k8s_version="1.30",
        control_plane=nebius.Mk8sV1ClusterSpecControlPlaneArgs(
            subnet_id=subnet.id,
        ),
    ),
    opts=pulumi.ResourceOptions(provider=provider),
)
```

Key resource classes:

| Class | Description |
|---|---|
| `nebius.Provider` | Provider configuration (auth) |
| `nebius.Mk8sV1Cluster` | Managed Kubernetes cluster |
| `nebius.Mk8sV1NodeGroup` | Node group within a cluster |
| `nebius.VpcV1Network` | VPC network |
| `nebius.VpcV1Subnet` | Subnet |
| `nebius.VpcV1SecurityGroup` | Security group |
| `nebius.IamV1ServiceAccount` | IAM service account |
| `nebius.IamV1AccessPermit` | IAM role binding |
| `nebius.ComputeV1Instance` | Compute instance |
| `nebius.ComputeV1GpuCluster` | GPU cluster |

## Examples

| Example | Description |
|---|---|
| [`examples/mk8s-cluster`](examples/mk8s-cluster/) | Managed Kubernetes cluster with a CPU node group and an optional GPU node group |

## Regenerating the SDK

To regenerate after an upstream Terraform provider release:

```bash
# Pin to a specific version and regenerate
make sdk VERSION=0.6.38

# Or just regenerate from the current pinned version
make sdk
```

### Automated updates

The [`pulumi-nebius provider`](../.github/workflows/pulumi-nebius-provider.yml) workflow:

- Checks the [Terraform registry](https://registry.terraform.io/v1/providers/nebius/nebius) for a
  newer version every Monday at 06:00 UTC, and opens a PR that bumps `Makefile` and regenerates
  `sdk/` if one is found.
- Can also be triggered manually via **Actions → pulumi-nebius provider → Run workflow**, with an
  optional `version` input to bump to a specific release.
- Validates that the generated SDK imports cleanly on every push to `main` that touches
  `pulumi-nebius/**`.

## Publishing to PyPI

`pip install pulumi-nebius` is served from PyPI as a normal pre-built package (in addition to
the zero-install `pulumi package add terraform-provider registry.terraform.io/nebius/nebius`
path, which generates an SDK locally and needs nothing published at all).

### Automated

1. The `pulumi-nebius provider` workflow bumps `Makefile`/regenerates `sdk/` and opens a PR (as
   described above).
2. Merging that PR to `main` triggers the `tag-release` job, which tags `pulumi-nebius-v<version>`
   and cuts a GitHub Release — but only if that tag doesn't already exist, so it's a no-op on
   unrelated pushes.
3. The release publish fires [`pulumi-nebius-pypi-publish.yml`](../.github/workflows/pulumi-nebius-pypi-publish.yml),
   which builds `sdk/` and uploads it to PyPI via
   [OIDC trusted publishing](https://docs.pypi.org/trusted-publishers/) — no long-lived API token
   is stored in this repo.

**One-time setup** (needs PyPI/GitHub account access, not code):
- On PyPI (and optionally TestPyPI) → project settings → *Trusted Publishers* → add a publisher
  pointing at this repo, workflow `pulumi-nebius-pypi-publish.yml`, environment `pypi` (or
  `testpypi`).
- In GitHub → repo Settings → Environments, create the `pypi` environment (and `testpypi` if
  used) and optionally add required reviewers there for a manual approval gate before anything
  actually publishes.

### Manual / local

```bash
make dist                                   # build sdist + wheel into sdk/dist/
PYPI_API_TOKEN=pypi-... make publish-test   # upload to TestPyPI
PYPI_API_TOKEN=pypi-... make publish        # upload to PyPI
```

`scripts/build.sh` and `scripts/publish.sh` back these targets directly if you want more control.
You can also trigger a TestPyPI dry run from CI without cutting a release: **Actions →
pulumi-nebius PyPI publish → Run workflow → target: testpypi**.

Because `make sdk` regenerates `sdk/` from scratch on every run, PyPI-facing metadata can't live
in the generated `pyproject.toml` directly. `scripts/patch_pyproject.py` re-applies it after every
regeneration (called automatically as the last step of `make sdk`):
- adds `license`, `license-files`, `authors`, `classifiers`, and this repo's URLs
- bumps `[build-system] requires` to `setuptools>=77.0.3` — the codegen'd `>=61.0` floor predates
  [PEP 639](https://peps.python.org/pep-0639/) SPDX `license = "MIT"` support
- copies `LICENSE` and `README.md` into `sdk/` so they land in the built distribution and PyPI
  gets a real long description instead of a blank one

## Directory layout

```
pulumi-nebius/
├── Makefile          # sdk / install / bump targets
├── README.md         # this file
└── sdk/              # generated Python package (committed)
    ├── pyproject.toml
    └── pulumi_nebius/
        ├── pulumi-plugin.json   # tells Pulumi which runtime plugin to use
        ├── mk8s_v1_cluster.py
        ├── mk8s_v1_node_group.py
        ├── vpc_v1_*.py
        ├── iam_v1_*.py
        └── ...                  # 100+ resource & data-source modules
```

## License

[MIT](../LICENSE)
