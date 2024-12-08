"""An AWS Python Pulumi program"""

import pulumi
import pulumi_aws as aws

config = pulumi.Config()

user_vpc_name = config.require("user_vpc_name")

user_subnet_name = config.require("user_subnet_name")
user_subnet_ip = config.require("user_subnet_ip")
user_subnet_region = config.require("user_subnet_region")

user_security_group_name = config.require("user_security_group_name")
user_security_group_rules = config.require_object("user_security_group_rules")

user_vm_name = config.require("user_vm_name")
user_vm_instance_type = config.require("user_vm_instance_type")
user_vm_key_name = config.require("user_vm_key_name")
user_vm_region = config.require("user_vm_region")

user_vm_startup_script = f"""
#!/bin/bash
sudo apt update -y
sudo apt-get install -y iproute2
sudo apt install -y netcat-traditional ncat
sudo apt install -y iperf3
"""


user_vpc = aws.ec2.Vpc(
    user_vpc_name,
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True
)

user_subnet = aws.ec2.Subnet(
    user_subnet_name,
    vpc_id=user_vpc.id,
    cidr_block=user_subnet_ip,
    availability_zone=user_subnet_region,
    map_public_ip_on_launch=True
)

user_igw = aws.ec2.InternetGateway(
    "user-igw",
    vpc_id=user_vpc.id,
)

user_route_table = aws.ec2.RouteTable(
    "user-route-table",
    vpc_id=user_vpc.id,
    routes=[
        {
            "cidr_block": "0.0.0.0/0",
            "gateway_id": user_igw.id
        }
    ],
)

route_table_association = aws.ec2.RouteTableAssociation(
    "user-route-table-association",
    subnet_id=user_subnet.id,
    route_table_id=user_route_table.id
)


user_security_group = aws.ec2.SecurityGroup(
    user_security_group_name,
    vpc_id=user_vpc.id,
    ingress=user_security_group_rules["ingress"],
    egress=user_security_group_rules["egress"]
)

ami = aws.ec2.get_ami(most_recent=True,
    owners=["amazon"],
    filters=[{ "name": "name", "values": ["amzn2-ami-hvm-*-x86_64-gp2"] }]
)

user_vm = aws.ec2.Instance(
    user_vm_name,
    instance_type=user_vm_instance_type,
    ami=ami.id,
    vpc_security_group_ids=[user_security_group.id],
    subnet_id=user_subnet.id,
    user_data=user_vm_startup_script,
    associate_public_ip_address=True
)

pulumi.export("public-ip", user_vm.public_ip)