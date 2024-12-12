#!/bin/bash

# Enable IP forwarding
sudo sysctl -w net.ipv4.ip_forward=1
echo 'net.ipv4.ip_forward = 1' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# VM1 VXLAN interface
sudo ip link add vxlan43 type vxlan id 43 dstport 4789 remote 35.208.82.114 local 35.208.82.114
sudo ip addr add 192.168.43.1/24 dev vxlan43
sudo ip link set up dev vxlan43

# VM2 VXLAN interface
sudo ip link add vxlan44 type vxlan id 44 dstport 4789 remote 34.219.107.212 local 35.208.82.114
sudo ip addr add 192.168.44.1/24 dev vxlan44
sudo ip link set up dev vxlan44

# Add routes for VXLAN networks

sudo ip route add 192.168.43.0/24 dev vxlan43

sudo ip route add 192.168.44.0/24 dev vxlan44
