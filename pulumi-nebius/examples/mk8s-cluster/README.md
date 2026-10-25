# Nebius Managed Kubernetes cluster

Creates a [Nebius MK8s](https://docs.nebius.com/kubernetes) cluster with a public
control-plane endpoint, a CPU node group, and an optional GPU node group, using
[`pulumi-nebius`](https://pypi.org/project/pulumi-nebius/).

## Prerequisites

- [Pulumi CLI](https://www.pulumi.com/docs/install/)
- [Nebius CLI](https://docs.nebius.com/cli) with an active profile (`nebius profile create`).
  The program authenticates with that profile.
- A project ID and an existing subnet ID:

  ```bash
  nebius iam project list
  nebius vpc subnet list --parent-id <project-id>
  ```

## Deploy

```bash
cd pulumi-nebius/examples/mk8s-cluster
pulumi stack init dev
pulumi config set projectId project-...
pulumi config set subnetId vpcsubnet-...
pulumi up
```

`pulumi up` installs the dependencies from `requirements.txt` into `venv/` on first run.

Then fetch a kubeconfig:

```bash
nebius mk8s cluster get-credentials --id $(pulumi stack output cluster_id) --external
kubectl get nodes
```

## Configuration

| Key | Default | Description |
|---|---|---|
| `projectId` | — (required) | Nebius project ID |
| `subnetId` | — (required) | Subnet for the control plane and nodes |
| `name` | `pulumi-mk8s` | Cluster name; node groups are suffixed `-cpu` / `-gpu` |
| `k8sVersion` | backend default | Kubernetes version, e.g. `1.31` |
| `cpuPlatform` / `cpuPreset` | `cpu-d3` / `4vcpu-16gb` | CPU node shape |
| `cpuNodes` | `2` | CPU node count |
| `gpuNodes` | `0` | GPU node count; the GPU node group is only created when > 0 |
| `gpuPlatform` / `gpuPreset` | `gpu-h100-sxm` / `1gpu-16vcpu-200gb` | GPU node shape (platform availability varies by region) |

For example, to add one H100 node:

```bash
pulumi config set gpuNodes 1
pulumi up
```

## Clean up

```bash
pulumi destroy
```
