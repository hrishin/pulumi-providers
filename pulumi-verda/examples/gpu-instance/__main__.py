"""Verda GPU instance with an SSH key, startup script and attached data volume."""
import os

import pulumi
import pulumi_verda as verda

config = pulumi.Config()
name = config.get("name") or "pulumi-gpu"
location = config.get("location") or "FIN-01"
instance_type = config.get("instanceType") or "1B200.30V"
image = config.get("image") or "ubuntu-24.04-cuda-12.8-open-docker"
volume_size = config.get_int("volumeSizeGb") or 500
public_key_path = os.path.expanduser(config.get("publicKeyPath") or "~/.ssh/id_ed25519.pub")

# Credentials are read from VERDA_CLIENT_ID / VERDA_CLIENT_SECRET.

ssh_key = verda.SshKey(
    "key",
    name=f"{name}-key",
    public_key=open(public_key_path).read().strip(),
)

startup = verda.StartupScript(
    "startup",
    name=f"{name}-startup",
    script="""#!/bin/bash
set -euo pipefail
nvidia-smi > /var/log/nvidia-smi-boot.log 2>&1 || true
""",
)

data = verda.Volume(
    "data",
    name=f"{name}-data",
    size=volume_size,
    type="NVMe_Shared",
    location=location,
)

instance = verda.Instance(
    "gpu",
    hostname=name,
    description="GPU instance managed by Pulumi",
    instance_type=instance_type,
    image=image,
    location=location,
    ssh_key_ids=[ssh_key.id],
    startup_script_id=startup.id,
)

attachment = verda.VolumeAttachment(
    "data",
    volume_id=data.id,
    instance_id=instance.id,
)

pulumi.export("ip", instance.ip)
pulumi.export("ssh", instance.ip.apply(lambda ip: f"ssh root@{ip}"))
pulumi.export("price_per_hour", instance.price_per_hour)
pulumi.export("mount_command", attachment.mount_command)
