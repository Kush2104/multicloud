"""A Google Cloud Python Pulumi program"""

import pulumi
import pulumi_gcp as gcp

config = pulumi.Config()

user_vpc_name = config.require("user_vpc_name")

user_subnet_name = config.require("user_subnet_name")
user_subnet_ip = config.require("user_subnet_ip")
user_subnet_region = config.require("user_subnet_region")

user_firewall_name = config.require("user_firewall_name")
user_firewall_rules = config.require_object("user_firewall_rules")

user_vm_name = config.require("user_vm_name")
user_vm_machine_type = config.require("user_vm_machine_type")
user_vm_zone = config.require("user_vm_zone")
user_vm_image = config.require("user_vm_image")
user_vm_ip_name = config.require("user_vm_ip_name")
user_vm_region = config.require("user_vm_region")
user_vm_public_ip_address = gcp.compute.Address(user_vm_ip_name, region = user_vm_region, network_tier = "STANDARD").address

user_vm_startup_script = f"""
sudo apt update -y
sudo apt-get install -y iproute2
sudo apt install -y netcat-traditional ncat
sudo apt install -y iperf3
"""

config = pulumi.Config()

user_vpc = gcp.compute.Network(
    user_vpc_name,
    auto_create_subnetworks = False
)


user_subnet = gcp.compute.Subnetwork(
    user_subnet_name,
    ip_cidr_range = user_subnet_ip,
    network = user_vpc.id,
    region = user_subnet_region
)


user_firewall = gcp.compute.Firewall(
    user_firewall_name,
    network = user_vpc.id,
    allows = user_firewall_rules,
    direction = "INGRESS",
    source_ranges = ["0.0.0.0/0"]
)


user_vm = gcp.compute.Instance(
    user_vm_name,
    machine_type = user_vm_machine_type,
    zone = user_vm_zone,
    boot_disk = 
    {
        'initializeParams':
        {'image' : user_vm_image}
    },
    network_interfaces = 
    [
        {
        'network': user_vpc.id,
        'subnetwork' : user_subnet.id,
        'accessConfigs' : 
        [
            {
            'nat_ip' : user_vm_public_ip_address,
            'network_tier' : "STANDARD"
            }
        ]
        }
    ],
    metadata = {"startup-script" : user_vm_startup_script}
)

pulumi.export("public-ip", user_vm_public_ip_address)