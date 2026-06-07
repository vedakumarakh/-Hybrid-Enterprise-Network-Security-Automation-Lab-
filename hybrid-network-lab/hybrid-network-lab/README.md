# Hybrid Enterprise Network Security and Automation Lab

A hands-on enterprise network security lab simulating a real-world hybrid infrastructure with on-premise firewalls, core routing, and AWS cloud connectivity. Built to demonstrate skills in network security engineering, firewall policy design, MPLS/BGP routing, VPN configuration, and Python/Ansible automation.

---

## Architecture

```
                         INTERNET
                             |
                     [ISP Router - WAN]
                      203.0.113.0/30
                             |
                    ┌────────┴────────┐
                    │                 │
             [Cisco ASA FW]    [FortiGate FW]
              192.168.10.1      192.168.30.1
                    │                 │
              ┌─────┴─────┐    ┌──────┴──────┐
           [Inside LAN]  [DMZ] [Internal]  [DMZ2]
                    │
         [Cisco IOS-XR Core Router]
           BGP AS65001 | MPLS LDP
                    │
           ┌────────┴────────┐
      [OSPF Area 0]    [Site-to-Site VPN]
                             │
                    ┌────────┴────────┐
                [AWS VPC]       [Branch Office]
                10.0.1.0/24     (Simulated)
```

---

## What This Lab Covers

| Area | Technologies |
|---|---|
| Firewall Security | Cisco ASA, Fortinet FortiGate, ACLs, Zone-based policies |
| Routing | OSPF, BGP (eBGP/iBGP), MPLS LDP, L3VPN |
| VPN | IKEv2 Site-to-Site VPN, IPSec, AWS VPN Gateway |
| Network Segmentation | VLANs, DMZ architecture, Security zones |
| Automation | Python (Netmiko/boto3), Ansible playbooks |
| Monitoring | SNMP, Syslog, CloudWatch, Custom Python health checks |

---

## Repository Structure

```
hybrid-network-lab/
├── configs/
│   ├── cisco-asa/
│   │   └── asa-firewall-base.cfg        # ASA base security config
│   ├── cisco-ios-xr/
│   │   └── core-router-config.cfg       # IOS-XR OSPF/BGP/MPLS config
│   └── fortinet/
│       └── fortigate-policy.cfg         # FortiGate UTM firewall policies
├── automation/
│   ├── ansible/
│   │   ├── inventory.ini                # Device inventory
│   │   ├── backup-configs.yml           # Automated config backup playbook
│   │   └── vlan-security-audit.yml      # VLAN security audit playbook
│   └── python/
│       ├── network_health_monitor.py    # SSH-based device health checker
│       ├── vpn_tunnel_monitor.py        # VPN tunnel monitor with email alerts
│       └── requirements.txt             # Python dependencies
├── diagrams/
│   └── topology.md                      # Network topology diagram
├── docs/
│   └── lab-setup-guide.md               # Step-by-step EVE-NG lab setup
├── screenshots/                         # Add your lab screenshots here
└── README.md
```

---

## Key Configurations

### Cisco ASA Firewall
- **3-zone architecture**: Outside (trust 0) → DMZ (trust 50) → Inside (trust 100)
- **ACL policies**: Deny-all inbound default, explicit allow for HTTPS/HTTP only
- **IKEv2 Site-to-Site VPN** to AWS VPC with AES-256/SHA-256
- **Deep Packet Inspection**: HTTP, DNS, FTP, SIP inspection via MPF
- **SSH hardening**: Version 2, restricted to management subnet only

### Cisco IOS-XR Router
- **OSPF Area 0** for internal routing with route redistribution
- **eBGP AS65001** peering with ISP upstream and MPLS VPN CE
- **MPLS LDP** enabled for L2/L3 VPN services
- **QoS Policy**: Voice (30% priority) → Critical Data (40%) → Best Effort (30%)
- **VRF ENTERPRISE-VPN** for L3VPN customer isolation

### Fortinet FortiGate
- **6 firewall policies** covering all traffic flows
- **UTM inspection** on internal-to-internet traffic (AV + IPS + Web Filter)
- **Geo-blocking** for high-risk countries (CN, RU, KP, IR)
- **IPS sensor** with signature-based threat detection
- **IPSec VPN** to AWS with IKEv2/AES-256

---

## Automation Scripts

### Python: Network Health Monitor
```bash
pip install -r automation/python/requirements.txt
python automation/python/network_health_monitor.py
```
Connects via SSH (Netmiko) to all devices, runs health checks (BGP state, interface status, VPN tunnels), and generates timestamped reports.

### Python: VPN Tunnel Monitor
```bash
export GMAIL_APP_PASSWORD="your-app-password"
python automation/python/vpn_tunnel_monitor.py
```
Polls VPN tunnel state every 60 seconds. Sends email alert when tunnel goes down and recovery alert when it comes back up.

### Ansible: Configuration Backup
```bash
ansible-playbook -i automation/ansible/inventory.ini automation/ansible/backup-configs.yml
```
Backs up running configs from all devices with timestamps. Stores in `backups/YYYY-MM-DD/` folder.

### Ansible: VLAN Security Audit
```bash
ansible-playbook -i automation/ansible/inventory.ini automation/ansible/vlan-security-audit.yml
```
Audits VLAN configuration, checks for trunk mismatches and native VLAN issues, generates audit report.

---

## Lab Setup (EVE-NG)

### Prerequisites
- EVE-NG Community or Pro (Ubuntu 22.04 VM recommended)
- Cisco ASA 9.x qcow2 image
- Cisco IOS-XR 7.x qcow2 image
- FortiGate 7.x qcow2 image
- Python 3.10+ and Ansible 9.x on management host

### Quick Start
1. Import device images into EVE-NG (`/opt/unetlab/addons/qemu/`)
2. Create a new lab in EVE-NG and add the devices
3. Connect devices as per topology diagram
4. Apply configs from `configs/` directory to each device via console
5. Verify connectivity using ping/traceroute between zones
6. Run Python health monitor to validate all connections

See [docs/lab-setup-guide.md](docs/lab-setup-guide.md) for detailed step-by-step instructions.

---

## Security Findings Demonstrated

| Finding | Severity | Remediation Applied |
|---|---|---|
| Open SSH from any IP | High | Restricted SSH to mgmt subnet only |
| Default admin credentials | High | Changed on all devices, MFA enabled |
| DMZ can reach internal LAN | Critical | Explicit deny policy added on both ASA and FortiGate |
| No VPN encryption standard | High | Enforced AES-256/SHA-256 IKEv2 on all tunnels |
| No traffic inspection | Medium | UTM enabled on FortiGate, MPF on ASA |
| Missing geo-blocking | Medium | Geo-block policy for high-risk countries |

---

## Skills Demonstrated

- Enterprise firewall policy design (Cisco ASA + Fortinet FortiGate)
- MPLS L2/L3VPN provisioning and troubleshooting (Cisco IOS-XR)
- Site-to-site IKEv2 VPN with AWS integration
- Python network automation with Netmiko and boto3
- Ansible playbooks for config backup and compliance auditing
- Network monitoring, SNMP, and syslog integration
- Security zone architecture (DMZ, trust levels, ACL design)

---

## Author

**Vedakumara K H**  
NOC System Engineer | Bharti Airtel  
CCNA | CCNP | AWS Solutions Architect – Associate  
📧 vedakumarakh@gmail.com  
🔗 [LinkedIn](https://linkedin.com/in/your-profile) | [GitHub](https://github.com/vedakumarakh)
