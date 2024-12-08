"""A Google Cloud Python Pulumi program"""

import pulumi
import pulumi_gcp as gcp

config = pulumi.Config()

mcn_vm_public_ip_address = "35.208.217.95" # Create a static IP and enter it here


mcn_vpc_name = config.require("mcn_vpc_name")

mcn_subnet_name = config.require("mcn_subnet_name")
mcn_subnet_ip = config.require("mcn_subnet_ip")
mcn_subnet_region = config.require("mcn_subnet_region")

mcn_firewall_name = config.require("mcn_firewall_name")
mcn_firewall_rules = config.require_object("mcn_firewall_rules")

mcn_vm_name = config.require("mcn_vm_name")
mcn_vm_machine_type = config.require("mcn_vm_machine_type")
mcn_vm_zone = config.require("mcn_vm_zone")
mcn_vm_image = config.require("mcn_vm_image")
mcn_vm_ip_name = config.require("mcn_vm_ip_name")
mcn_vm_region = config.require("mcn_vm_region")

with open('app.py', 'r') as file:
    flask_app = file.read()


mcn_vm_startup_script = f"""
#!/bin/bash
sudo apt update -y
sudo apt install -y netcat-traditional ncat
sudo apt install -y iperf3
sudo apt install -y python3
sudo apt install -y python3-flask

sudo mkdir -p /flask_app
sudo chown $(whoami):$(whoami) /flask_app

cat <<'EOF' > /flask_app/app.py
{flask_app}
EOF

sudo chmod +x /flask_app/app.py
nohup python3 /flask_app/app.py &
"""

mcn_vpc = gcp.compute.Network(
    mcn_vpc_name,
    auto_create_subnetworks = False
)


mcn_subnet = gcp.compute.Subnetwork(
    mcn_subnet_name,
    ip_cidr_range = mcn_subnet_ip,
    network = mcn_vpc.id,
    region = mcn_subnet_region
)


mcn_firewall = gcp.compute.Firewall(
    mcn_firewall_name,
    network = mcn_vpc.id,
    allows = mcn_firewall_rules,
    direction = "INGRESS",
    source_ranges = ["0.0.0.0/0"]
)


mcn_vm = gcp.compute.Instance(
    mcn_vm_name,
    machine_type = mcn_vm_machine_type,
    zone = mcn_vm_zone,
    boot_disk = 
    {
        'initializeParams':
        {'image' : mcn_vm_image}
    },
    network_interfaces = 
    [
        {
        'network': mcn_vpc.id,
        'subnetwork' : mcn_subnet.id,
        'accessConfigs' : 
        [
            {
            'nat_ip' : mcn_vm_public_ip_address,
            'network_tier' : "STANDARD"
            }
        ]
        }
    ],
    metadata_startup_script = mcn_vm_startup_script
)

pulumi.export("public-ip", mcn_vm_public_ip_address)