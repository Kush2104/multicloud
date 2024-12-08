"""An AWS Python Pulumi program"""

import pulumi
import pulumi_aws as aws

config = pulumi.Config()

mcn_vpc_name = config.require("mcn_vpc_name")

mcn_subnet_name = config.require("mcn_subnet_name")
mcn_subnet_ip = config.require("mcn_subnet_ip")
mcn_subnet_region = config.require("mcn_subnet_region")

mcn_security_group_name = config.require("mcn_security_group_name")
mcn_security_group_rules = config.require_object("mcn_security_group_rules")

mcn_vm_name = config.require("mcn_vm_name")
mcn_vm_instance_type = config.require("mcn_vm_instance_type")
mcn_vm_key_name = config.require("mcn_vm_key_name")
mcn_vm_region = config.require("mcn_vm_region")

mcn_vm_startup_script = f"""
#!/bin/bash
sudo sysctl -w net.ipv4.ip_forward=1
echo 'net.ipv4.ip_forward = 1' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
sudo su - root
sudo apt update -y
sudo apt-get install -y iproute2
sudo yum install -y nmap-ncat
sudo yum install -y iperf3
"""

mcn_vpc = aws.ec2.Vpc(
    mcn_vpc_name,
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True
)

mcn_subnet = aws.ec2.Subnet(
    mcn_subnet_name,
    vpc_id=mcn_vpc.id,
    cidr_block=mcn_subnet_ip,
    availability_zone=mcn_subnet_region,
    map_public_ip_on_launch=True
)

mcn_igw = aws.ec2.InternetGateway(
    "user-igw",
    vpc_id=mcn_vpc.id,
)

mcn_route_table = aws.ec2.RouteTable(
    "user-route-table",
    vpc_id=mcn_vpc.id,
    routes=[
        {
            "cidr_block": "0.0.0.0/0",
            "gateway_id": mcn_igw.id
        }
    ],
)

route_table_association = aws.ec2.RouteTableAssociation(
    "user-route-table-association",
    subnet_id=mcn_subnet.id,
    route_table_id=mcn_route_table.id
)

mcn_security_group = aws.ec2.SecurityGroup(
    mcn_security_group_name,
    vpc_id=mcn_vpc.id,
    ingress=mcn_security_group_rules["ingress"],
    egress=mcn_security_group_rules["egress"]
)

ami = aws.ec2.get_ami(most_recent=True,
    owners=["amazon"],
    filters=[{ "name": "name", "values": ["amzn2-ami-hvm-*-x86_64-gp2"] }]
)

mcn_vm = aws.ec2.Instance(
    mcn_vm_name,
    instance_type=mcn_vm_instance_type,
    ami=ami.id,
    vpc_security_group_ids=[mcn_security_group.id],
    subnet_id=mcn_subnet.id,
    user_data=mcn_vm_startup_script,
    associate_public_ip_address=True
)

pulumi.export("public-ip", mcn_vm.public_ip)