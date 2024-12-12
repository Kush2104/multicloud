# **Multi-Cloud Networking Project Notes**

## **Introduction**
This project establishes a VXLAN-based connection between AWS and GCP for inter-cloud communication. The primary focus is on configuring VXLAN tunnels, ensuring connectivity, and debugging network issues. Performance benchmarking and network analysis will follow once the setup is functional.

---

## **Setup and Configuration**

### **AWS**
- **Region**: `us-west-2`
- **EC2 Instance**:
  - Created using Pulumi with `t2.micro` instance type.
  - **Public IP**: `34.219.107.212`.
  - **Security Group**:
    - **Inbound Rules**:
      - UDP on port `4789` for VXLAN.
      - ICMP for ping testing.
      - SSH (TCP:22) for management access.
      - HTTP and custom TCP (ports 80, 1234, 5001) for testing.
    - **Outbound Rules**: All traffic allowed.
- **Role in Setup**:
  - Participates as a VXLAN endpoint (VM2).
  - VXLAN interface: `vxlan44`.

### **GCP**
- **Region**: `us-central1-a`
- **VM Instance**:
  - Created using Pulumi with `e2-micro` instance type.
  - **Public IP**: `35.208.82.114`.
  - **Firewall Rules**:
    - Allow TCP traffic on ports `22`, `80`, `1234`, and `5001`.
    - Allow UDP traffic on port `4789` for VXLAN.
    - Allow ICMP for ping testing.
- **Role in Setup**:
  - Acts as the central node for the VXLAN tunnel.
  - VXLAN interface: `vxlan43`.

---

## **Tools Used**
- **Pulumi**: Infrastructure as Code for provisioning resources on AWS and GCP.
- **tcpdump**: Debugging VXLAN traffic.
- **ping**: Connectivity testing.
- **nmap**: Verifying UDP port reachability.

---

## **Observations**

### **Setup Process**
1. **Link API Configuration**:
   - Used a Flask-based `link-api` to manage VM registrations and generate VXLAN scripts.
   - Registered the GCP (`mc-gcp`) VM as the **central node** and AWS VM (`34.219.107.212`) as a VXLAN endpoint.

2. **VXLAN Configuration**:
   - **Scripts**:
     - `setup_central_node.sh` for `mc-gcp`.
     - `setup_vxlan_vm1.sh` and `setup_vxlan_vm2.sh` for VXLAN participants.
   - Configured `vxlan43` on `mc-gcp` with IP `192.168.43.1/24`.
   - Configured `vxlan44` on AWS with IP `192.168.44.1/24`.

3. **Routing**:
   - Added routes between the VXLAN subnets:
     - On AWS: `192.168.43.0/24 via 192.168.44.2`.
     - On GCP: `192.168.44.0/24 via vxlan43`.

---

### **Challenges**
1. **Initial Configuration Errors**:
   - Incorrect IP assigned to `vxlan43` (`192.168.43.2` instead of `192.168.43.1`) caused routing issues.
   - Fixed by manually reassigning the correct IP.

2. **Connectivity Issues**:
   - `ping` between VXLAN interfaces failed:
     - `192.168.43.1 → 192.168.44.1`: No response.
     - Debugging showed no traffic captured on `tcpdump`.

3. **Firewall and NAT Verification**:
   - Firewall rules for UDP port `4789` confirmed to be open on both AWS and GCP.
   - Potential NAT or VXLAN encapsulation issues identified as the next area of focus.

---

## **Next Steps**
1. Verify UDP traffic reachability between AWS and GCP using `nmap`.
2. Debug VXLAN encapsulation and NAT behavior on both VMs.
3. Analyze and resolve potential routing or kernel-level VXLAN issues.


## **Findings and Challenges**

### **1. Current Setup Issues**
1. **No VXLAN Traffic Observed**:
   - Despite correct configurations on VXLAN interfaces (`vxlan43` and `vxlan44`), no traffic is captured via `tcpdump`.
   - UDP port 4789 is open and reachable (verified via `nmap`), but packets do not traverse the VXLAN tunnel.

2. **Public-to-Private IP Mapping**:
   - Traffic from GCP (`10.0.0.2`) to AWS (`10.0.0.119`) is routed through public IPs (`35.208.82.114` and `34.219.107.212`).
   - VXLAN encapsulation over public IPs introduces potential NAT-related issues, complicating packet flow.

3. **Potential NAT Interference**:
   - NAT might be modifying VXLAN packets, breaking the encapsulation.

---

### **2. Why Use Public IPs for VXLAN**
- **Immediate Solution**:
  - Using public IPs allows us to move forward without additional infrastructure for private network interconnectivity (e.g., VPN or VPC peering).
  - Existing firewall rules on AWS and GCP already accommodate public IPs and UDP traffic on port 4789.
  
- **Flexibility**:
  - Public IP-based VXLAN tunnels demonstrate the feasibility of inter-cloud communication without dedicated private networking setups.
  - This is practical for scenarios where interconnect services (e.g., Partner Interconnect or Direct Connect) are unavailable.

---

### **3. Long-Term Considerations**
Using public IPs does not limit future project goals:
1. **Leverage Provider Internal Pipelines**:
   - Future enhancements can integrate GCP’s global backbone and AWS’s private routing.
   - Example: Route GCP Europe traffic through GCP US using its private backbone before sending it to AWS US.

2. **Support Multi-Hop Routing**:
   - VXLAN tunnels can be extended with intermediate nodes to enforce multi-hop traffic flows.

3. **Inter-Cloud Optimizations**:
   - Partner Interconnect (GCP) and Direct Connect (AWS) can be integrated for low-latency, high-performance paths.

---

## **Plan Moving Forward**
### **Step 1: Update VXLAN Configurations**
- Use public IPs as `remote` in VXLAN configurations.
  - **AWS (`vxlan44`)**: Remote IP → `35.208.82.114`.
  - **GCP (`vxlan43`)**: Remote IP → `34.219.107.212`.

### **Step 2: Debug Traffic Flow**
- Monitor `tcpdump` on both VMs for VXLAN packets.
- Use `iperf3` to test UDP performance.

### **Step 3: Document Results**
- Summarize findings, connectivity benchmarks, and performance metrics.

---

### **Rationale for Current Changes**
1. **Progress on VXLAN Setup**:
   - Resolving immediate issues with minimal changes.
   - Ensures the project moves forward without introducing unnecessary complexity.

2. **Alignment with Future Goals**:
   - Using public IPs is a stepping stone.
   - Does not prevent later integration with GCP/AWS private pipelines or inter-cloud optimizations.

---

### **Next Steps**
1. Update VXLAN configurations to use public IPs.
2. Test connectivity and debug traffic flow.
3. Document findings and performance results.