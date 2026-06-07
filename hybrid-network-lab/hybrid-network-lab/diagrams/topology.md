# Network Topology - Hybrid Enterprise Security Lab

## Architecture Overview

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
              (Inside/Outside)  (Internal/DMZ)
                    │                 │
              ┌─────┴─────┐    ┌──────┴──────┐
              │           │    │             │
           [Inside]     [DMZ] [Internal]   [DMZ2]
         192.168.10.0 192.168.20.0 192.168.30.0 192.168.40.0
              │
     [Core IOS-XR Router]
       192.168.1.1 / Lo0: 1.1.1.1
       BGP AS 65001
       MPLS LDP enabled
              │
        ┌─────┴─────┐
        │           │
   [OSPF Area 0] [MPLS VPN]
   Internal LAN   L3VPN CE
                      │
                  [Site-to-Site VPN]
                      │
               ┌──────┴──────┐
               │             │
          [AWS VPC]     [Branch Office]
          10.0.1.0/24  (Simulated)

## Simulated in EVE-NG
- Cisco ASA 9.x image
- Cisco IOS-XR 7.x image  
- FortiGate 7.x VM image
- Ubuntu 22.04 as endpoints
- AWS VPC simulated via GRE tunnel

## VLANs
| VLAN | Name        | Subnet            | Purpose                  |
|------|-------------|-------------------|--------------------------|
| 10   | MANAGEMENT  | 10.0.0.0/24       | Network device mgmt      |
| 20   | SERVER      | 192.168.10.0/24   | Internal servers (ASA)   |
| 30   | USER        | 192.168.30.0/24   | End-user LAN (FortiGate) |
| 40   | DMZ         | 192.168.20.0/24   | DMZ servers              |
| 100  | VPN-TRANSIT | 10.10.10.0/30     | VPN PE-CE link           |

## Security Zones
| Zone       | Device     | Trust Level | Policy                          |
|------------|------------|-------------|---------------------------------|
| Outside    | ASA        | 0 (untrust) | Deny all inbound by default     |
| DMZ        | ASA/Forti  | 50 (medium) | Limited internet, no LAN access |
| Inside     | ASA        | 100 (trust) | Full outbound, no inbound       |
| Internal   | FortiGate  | 80 (high)   | UTM-inspected internet access   |
| Management | Both       | 90 (high)   | SSH/SNMP restricted to mgmt net |
```
