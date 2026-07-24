# Hybrid Enterprise Network Security & Automation Lab

This matches the EVE-NG topology in your diagram:

```
                          vIOS3 (Core / Transit AS 65000)
                         Gi0/0            Gi0/1
                          |                 |
              10.0.12.0/30            10.0.23.0/30
                          |                 |
      vIOS1 (Site A edge, AS65001)   vIOS2 (Site B edge, AS65002)
         Gi0/0   Gi0/1                  Gi0/0   Gi0/1
                  |                              |
            10.10.1.0/30                   10.20.1.0/30
                  |                              |
             ASAv (outside)                 FortiGate (port1/WAN)
                  |                              |
         Gi0/1.10/.20/.30 (trunk)          port2.40/.50 (trunk)
                  |                              |
              Switch4                        Switch5
        Gi0/1  Gi0/2  Gi0/3              Gi0/1        Gi0/2
         |       |      |                  |            |
       VPC10   VPC11   VPC8              VPC9          Win
      (VLAN20)(VLAN30)(VLAN10)         (VLAN40)     (VLAN50)
```

Site A = ASAv + Switch4 + VPC8/VPC10/VPC11 (behind Cisco ASA)
Site B = FortiGate + Switch5 + VPC9/Win (behind FortiGate)
Core   = vIOS1 / vIOS3 / vIOS2 act as the WAN/ISP backbone between the two sites

VPC11 is flagged red in your diagram — it's used here as the "attacker / red-team"
host in VLAN 30, isolated from the server VLAN, for the threat-simulation bullet
on your resume.

## IP addressing plan

| Segment | Network | Notes |
|---|---|---|
| vIOS1 Gi0/0 – vIOS3 Gi0/0 | 10.0.12.0/30 | vIOS1=.1, vIOS3=.2 |
| vIOS3 Gi0/1 – vIOS2 Gi0/0 | 10.0.23.0/30 | vIOS3=.1, vIOS2=.2 |
| vIOS1 Gi0/1 – ASAv Gi0/0 (outside) | 10.10.1.0/30 | vIOS1=.1, ASA=.2 |
| vIOS2 Gi0/1 – FortiGate port1 (WAN) | 10.20.1.0/30 | vIOS2=.1, Forti=.2 |
| ASAv Gi0/1.10 — VLAN10 (Servers/VPC8) | 192.168.10.0/24 | ASA=.1, VPC8=.10 |
| ASAv Gi0/1.20 — VLAN20 (VPC10) | 192.168.20.0/24 | ASA=.1, VPC10=.10 |
| ASAv Gi0/1.30 — VLAN30 (VPC11, attacker) | 192.168.30.0/24 | ASA=.1, VPC11=.10 |
| FortiGate port2.40 — VLAN40 (VPC9) | 172.16.40.0/24 | Forti=.1, VPC9=.10 |
| FortiGate port2.50 — VLAN50 (Win) | 172.16.50.0/24 | Forti=.1, Win=.10 |
| Loopbacks | 1.1.1.1/32 (vIOS1), 3.3.3.3/32 (vIOS3), 2.2.2.2/32 (vIOS2) | for BGP router-id |

**BGP AS plan:** vIOS1 = AS65001 (Site A), vIOS3 = AS65000 (core/transit), vIOS2 = AS65002 (Site B)
**OSPF:** Process 1, Area 0, run separately on each site (ASA↔vIOS1 and FortiGate↔vIOS2),
redistributed into BGP so the two sites learn each other's LANs across the core.

## Build order (do this in EVE-NG)

1. Power on all nodes, wait for boot.
2. Console into each router/ASA and paste its config from `configs/`.
3. Configure Switch4 and Switch5 (VLANs + trunk/access ports).
4. Configure FortiGate via CLI console (`configs/fortigate.txt`).
5. Set IPs on VPC8, VPC10, VPC11, VPC9, Win (`configs/vpc_hosts.txt`).
6. Verify with the commands in `docs/verification_commands.md`.
7. Run the Python automation from `scripts/` against the Cisco devices.
8. Use `docs/wireshark_traffic_analysis.md` for the packet-capture / threat-sim part.

## Default credentials used throughout these configs
- Cisco enable/login: `admin` / `Cisco@12345`
- FortiGate admin: set your own password on first login (`configs/fortigate.txt` note)
- VPN pre-shared key: `Str0ngVPNkey!`

Change these before you screenshot/demo this, and definitely before putting it on GitHub —
put a placeholder or `.env`-style redaction in your repo instead of the real strings.
