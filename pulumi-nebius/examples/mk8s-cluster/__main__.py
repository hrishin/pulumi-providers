"""Nebius Managed Kubernetes cluster with a CPU node group and an optional GPU node group."""
import pulumi
import pulumi_nebius as nebius

config = pulumi.Config()
project_id = config.require("projectId")
subnet_id = config.require("subnetId")
name = config.get("name") or "pulumi-mk8s"
# Leave unset to use the backend default Kubernetes version.
k8s_version = config.get("k8sVersion")

cpu_platform = config.get("cpuPlatform") or "cpu-d3"
cpu_preset = config.get("cpuPreset") or "4vcpu-16gb"
cpu_nodes = config.get_int("cpuNodes") or 2

# GPU node group is only created when gpuNodes > 0.
gpu_platform = config.get("gpuPlatform") or "gpu-h100-sxm"
gpu_preset = config.get("gpuPreset") or "1gpu-16vcpu-200gb"
gpu_nodes = config.get_int("gpuNodes") or 0

# Authenticates with the active profile from the Nebius CLI (`nebius profile create`).
provider = nebius.Provider("nebius", profile=nebius.ProviderProfileArgs())
opts = pulumi.ResourceOptions(provider=provider)

cluster = nebius.Mk8sV1Cluster(
    "cluster",
    parent_id=project_id,
    name=name,
    control_plane=nebius.Mk8sV1ClusterControlPlaneArgs(
        subnet_id=subnet_id,
        version=k8s_version,
        etcd_cluster_size=3,
        endpoints=nebius.Mk8sV1ClusterControlPlaneEndpointsArgs(
            public_endpoint=nebius.Mk8sV1ClusterControlPlaneEndpointsPublicEndpointArgs(),
        ),
    ),
    opts=opts,
)

nebius.Mk8sV1NodeGroup(
    "cpu",
    parent_id=cluster.id,
    name=f"{name}-cpu",
    version=k8s_version,
    fixed_node_count=cpu_nodes,
    template=nebius.Mk8sV1NodeGroupTemplateArgs(
        resources=nebius.Mk8sV1NodeGroupTemplateResourcesArgs(
            platform=cpu_platform,
            preset=cpu_preset,
        ),
        boot_disk=nebius.Mk8sV1NodeGroupTemplateBootDiskArgs(
            size_gibibytes=64,
            type="NETWORK_SSD",
        ),
        network_interfaces=[
            nebius.Mk8sV1NodeGroupTemplateNetworkInterfaceArgs(subnet_id=subnet_id),
        ],
    ),
    opts=opts,
)

if gpu_nodes > 0:
    nebius.Mk8sV1NodeGroup(
        "gpu",
        parent_id=cluster.id,
        name=f"{name}-gpu",
        version=k8s_version,
        fixed_node_count=gpu_nodes,
        template=nebius.Mk8sV1NodeGroupTemplateArgs(
            resources=nebius.Mk8sV1NodeGroupTemplateResourcesArgs(
                platform=gpu_platform,
                preset=gpu_preset,
            ),
            boot_disk=nebius.Mk8sV1NodeGroupTemplateBootDiskArgs(
                size_gibibytes=256,
                type="NETWORK_SSD",
            ),
            # Boot image with NVIDIA drivers preinstalled.
            gpu_settings=nebius.Mk8sV1NodeGroupTemplateGpuSettingsArgs(drivers_preset="cuda13.0"),
            network_interfaces=[
                nebius.Mk8sV1NodeGroupTemplateNetworkInterfaceArgs(subnet_id=subnet_id),
            ],
        ),
        opts=opts,
    )

pulumi.export("cluster_id", cluster.id)
pulumi.export(
    "public_endpoint",
    cluster.status.apply(lambda s: s.control_plane.endpoints.public_endpoint if s and s.control_plane and s.control_plane.endpoints else None),
)
