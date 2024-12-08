"""A Google Cloud Python Pulumi program"""

import pulumi
import pulumi_gcp as gcp

config = pulumi.Config()

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
mcn_vm_public_ip_address = gcp.compute.Address(mcn_vm_ip_name, region = mcn_vm_region, network_tier = "STANDARD").address


mcn_vm_startup_script = f"""
sudo su - root
sudo apt update -y
sudo apt-get install -y iproute2
sudo apt install -y netcat-traditional ncat
sudo apt install -y iperf3
sudo sysctl -w net.ipv4.ip_forward=1
echo 'net.ipv4.ip_forward = 1' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
"""

config = pulumi.Config()

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
    metadata = {"startup-script" : mcn_vm_startup_script}
)

pulumi.export("public-ip", mcn_vm_public_ip_address)