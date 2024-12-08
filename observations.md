# **Multi-Cloud Networking Project Notes**

## **Introduction**
This project establishes connections between AWS and GCP using VXLAN for inter-cloud communication. It focuses on performance benchmarking and understanding latency and bandwidth between different regions.

---

## **Setup and Configuration**
### **AWS**
- **Region**: `us-west-2`
- EC2 instance created using Pulumi.
- Instance type: `t2.micro`
- Security group allows:
  - Outbound traffic: All.
  - Inbound traffic: All temporarily for testing.

### **GCP**
- **Region**: `us-central1-a`
- VM instance created using Pulumi.
- Firewall rules:
  - Allow TCP traffic on port `5201` for `iperf3`.

### **Tools Used**
- **iperf3** for bandwidth and latency testing.
- **traceroute** for analyzing routing paths.

---

## **Observations**
### **1. Bandwidth Testing (AWS ↔ GCP)**
| **Direction**      | **AWS Region**  | **GCP Region**   | **Bandwidth (Mbps)** | **Retransmissions** | **Latency** |
|---------------------|-----------------|------------------|-----------------------|---------------------|-------------|
| **AWS → GCP**       | `us-west-2`     | `us-central1-a`  | 331                   | 98                  | Low         |
| **GCP → AWS**       | `us-central1-a` | `us-west-2`      | 190                   | 0                   | Low         |

#### **Analysis**:
- **AWS → GCP**:
  - Higher bandwidth but initial retransmissions due to connection ramp-up.
  - Stable performance after the first interval.
- **GCP → AWS**:
  - Lower bandwidth but no retransmissions, indicating stability.
  - Likely asymmetry in routing or provider-specific factors.

---

### **2. Routing Analysis**
#### **AWS → GCP (traceroute)**
```
1  100.106.100.163 (100.106.100.163)  23.670 ms
2  240.1.228.12 (240.1.228.12)  1754.128 ms
3  150.222.214.182 (150.222.214.182)  8.322 ms
4  ae1-1414.cr5-sea2.ip4.gtt.net (209.120.222.197)  8.123 ms
5  ae27.cr6-chi1.ip4.gtt.net (89.149.183.70)  62.897 ms
6  google-gw.ip4.gtt.net (199.168.63.62)  47.708 ms
7  30.86.209.35.bc.googleusercontent.com (35.209.86.30)  64.848 ms
```

#### **Observations**: 
* High latency at Hop 2 (~1754 ms), likely due to temporary routing or congestion issues. * Final latency (~64 ms) is reasonable for inter-region communication. 

#### **GCP → AWS (traceroute)**

```
1  * * *
2  chi-b24-link.ip.twelve99.net (62.115.154.242)  18.809 ms
3  sea-b1-link.ip.twelve99.net (62.115.132.155)  61.683 ms
4  sea-b1-link.ip.twelve99.net (62.115.132.155)  61.716 ms
5  108.166.228.79 (108.166.228.79)  72.573 ms
6  52.95.54.176 (52.95.54.176)  69.631 ms
7  ec2-35-89-21-155.us-west-2.compute.amazonaws.com (35.89.21.155)  75.046 ms
```

#### **Observations**: 
* Initial hop responses blocked (`* * *`), possibly due to firewall or NAT. 
* Final latency (~70–75 ms) is slightly higher than AWS → GCP. 
* Routing involves Twelve99 (Telia Carrier) as the primary transit provider.

## **Findings and Challenges** 
### **Key Findings**: 
* Bandwidth asymmetry between AWS → GCP and GCP → AWS. 
* Stable connections with no retransmissions in the reverse direction.
* Differences in routing paths may contribute to latency and bandwidth variations. 

### **Challenges**: 
1. High initial retransmissions in the AWS → GCP direction. 
2. Inconsistent latency at specific hops in both directions. 
3. Limited control over inter-provider routing due to reliance on transit networks.