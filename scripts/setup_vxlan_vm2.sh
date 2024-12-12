#!/bin/bash

# Create VXLAN interface
sudo ip link add vxlan44 type vxlan id 44 dstport 4789 remote 35.208.82.114 local 34.219.107.212
sudo ip addr add 192.168.44.1/24 dev vxlan44
sudo ip link set up dev vxlan44

# Verify VXLAN interface
sudo ip link show vxlan44
sudo ip addr show dev vxlan44

# Add route to VXLAN network
sudo ip route add 192.168.44.0/24 dev vxlan44

sudo ip route add 192.168.43.0/24 via 192.168.43.1 dev vxlan44
