# Verda GPU instance

Creates a [Verda](https://verda.com) GPU instance with an SSH key, a startup script,
and a separate NVMe data volume attached to it, using
[`pulumi-verda`](https://pypi.org/project/pulumi-verda/).

## Prerequisites

- [Pulumi CLI](https://www.pulumi.com/docs/install/)
- Verda API client credentials, created in the Verda console:

  ```bash
  export VERDA_CLIENT_ID=...
  export VERDA_CLIENT_SECRET=...
  ```

- An SSH public key at `~/.ssh/id_ed25519.pub`, or set `publicKeyPath`.

## Deploy

```bash
cd pulumi-verda/examples/gpu-instance
pulumi stack init dev
pulumi up
```

`pulumi up` installs the dependencies from `requirements.txt` into `venv/` on first run.

Once the instance is up:

```bash
$(pulumi stack output ssh)
# on the instance, mount the data volume:
pulumi stack output mount_command
```

## Configuration

| Key | Default | Description |
|---|---|---|
| `name` | `pulumi-gpu` | Hostname and prefix for the key, script and volume |
| `location` | `FIN-01` | Verda location |
| `instanceType` | `1B200.30V` | Instance type |
| `image` | `ubuntu-24.04-cuda-12.8-open-docker` | OS image |
| `volumeSizeGb` | `500` | Data volume size in GB |
| `publicKeyPath` | `~/.ssh/id_ed25519.pub` | SSH public key to install |

```bash
pulumi config set location FIN-03
pulumi config set instanceType 1B200.30V
```

GPU instances are billed per hour while running; `pulumi stack output price_per_hour`
shows the rate.

## Clean up

```bash
pulumi destroy
```
