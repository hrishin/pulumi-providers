# pulumi-verda

[![pulumi-verda provider](https://github.com/hrishin/pulumi-providers/actions/workflows/pulumi-verda-provider.yml/badge.svg)](https://github.com/hrishin/pulumi-providers/actions/workflows/pulumi-verda-provider.yml)

Pulumi Python SDK for [Verda](https://verda.com) (formerly DataCrunch), generated from the
[Verda Terraform provider](https://registry.terraform.io/providers/verda-cloud/verda/latest)
via `pulumi package add terraform-provider`. Currently pinned to provider
version `1.1.4`.

No Go toolchain required — the Verda Terraform binary is downloaded automatically
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
pip install pulumi-verda
```

For local development from a checkout of this repo:

```bash
pip install -e pulumi-verda/sdk
```

### Verify

```bash
python -c "import pulumi_verda as v; print(v.Instance)"
```

## Usage

Credentials can be passed to the provider explicitly, or picked up from the
`VERDA_CLIENT_ID` / `VERDA_CLIENT_SECRET` environment variables.

```python
import pulumi
import pulumi_verda as verda

provider = verda.Provider(
    "verda",
    client_id="<client-id>",
    client_secret="<client-secret>",
)

key = verda.SshKey(
    "key",
    name="my-key",
    public_key=open("id_ed25519.pub").read(),
    opts=pulumi.ResourceOptions(provider=provider),
)

instance = verda.Instance(
    "gpu",
    hostname="my-gpu",
    description="training box",
    instance_type="1B200.30V",
    image="ubuntu-24.04-cuda-12.8-open-docker",
    location="FIN-01",
    ssh_key_ids=[key.id],
    opts=pulumi.ResourceOptions(provider=provider),
)
```

Key resource classes:

| Class | Description |
|---|---|
| `verda.Provider` | Provider configuration (auth) |
| `verda.Instance` | GPU/CPU instance |
| `verda.Volume` | Block storage volume |
| `verda.VolumeAttachment` | Attach a volume to an instance |
| `verda.SshKey` | SSH public key |
| `verda.StartupScript` | Startup script run on instance creation |
| `verda.Container` | Serverless container deployment |
| `verda.ServerlessJob` | Serverless job deployment |
| `verda.ContainerRegistryCredentials` | Private registry credentials for containers |

## Examples

| Example | Description |
|---|---|
| [`examples/gpu-instance`](examples/gpu-instance/) | GPU instance with an SSH key, startup script and attached data volume |

## Regenerating the SDK

To regenerate after an upstream Terraform provider release:

```bash
# Pin to a specific version and regenerate
make sdk VERSION=1.1.5

# Or just regenerate from the current pinned version
make sdk
```

### Automated updates

The [`pulumi-verda provider`](../.github/workflows/pulumi-verda-provider.yml) workflow:

- Checks the [Terraform registry](https://registry.terraform.io/v1/providers/verda-cloud/verda) for a
  newer version every Monday at 06:00 UTC, and opens a PR that bumps `Makefile` and regenerates
  `sdk/` if one is found.
- Can also be triggered manually via **Actions → pulumi-verda provider → Run workflow**, with an
  optional `version` input to bump to a specific release.
- Validates that the generated SDK imports cleanly on every push to `main` that touches
  `pulumi-verda/**`.

## Publishing to PyPI

Publishing works the same way as [`pulumi-nebius`](../pulumi-nebius/README.md#publishing-to-pypi):

1. Merging a version-bump PR to `main` triggers the `tag-release` job, which tags
   `pulumi-verda-v<version>` and cuts a GitHub Release if that tag doesn't exist yet.
2. The release fires [`pulumi-verda-pypi-publish.yml`](../.github/workflows/pulumi-verda-pypi-publish.yml),
   which builds `sdk/` and uploads it to PyPI via
   [OIDC trusted publishing](https://docs.pypi.org/trusted-publishers/).

**One-time setup:** on PyPI (and optionally TestPyPI), add a *Trusted Publisher* for the
`pulumi-verda` project pointing at this repo, workflow `pulumi-verda-pypi-publish.yml`,
environment `pypi` (or `testpypi`).

### Manual / local

```bash
make dist                                   # build sdist + wheel into sdk/dist/
PYPI_API_TOKEN=pypi-... make publish-test   # upload to TestPyPI
PYPI_API_TOKEN=pypi-... make publish        # upload to PyPI
```

`scripts/patch_pyproject.py` re-applies PyPI metadata (license, authors, URLs, README) to the
generated `sdk/pyproject.toml` after every `make sdk`.

## Directory layout

```
pulumi-verda/
├── Makefile          # sdk / install / bump / dist / publish targets
├── README.md         # this file
├── scripts/          # build, publish, pyproject patching
└── sdk/              # generated Python package (committed)
    ├── pyproject.toml
    └── pulumi_verda/
        ├── pulumi-plugin.json   # tells Pulumi which runtime plugin to use
        ├── instance.py
        ├── volume.py
        ├── ssh_key.py
        └── ...
```

## License

[MIT](../LICENSE)
