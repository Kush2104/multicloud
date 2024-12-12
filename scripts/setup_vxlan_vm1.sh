#!/bin/bash

# Create VXLAN interface
sudo ip link add vxlan43 type vxlan id 43 dstport 4789 remote 35.208.82.114 local 35.208.82.114
sudo ip addr add 192.168.43.1/24 dev vxlan43
sudo ip link set up dev vxlan43

# Verify VXLAN interface
sudo ip link show vxlan43
sudo ip addr show dev vxlan43

# Add route to VXLAN network
sudo ip route add 192.168.43.0/24 dev vxlan43

sudo ip route add 192.168.44.0/24 via 192.168.44.1 dev vxlan43
