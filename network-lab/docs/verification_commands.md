# Verification commands

Run these after all configs are applied, to confirm everything is actually working
(and to screenshot for your GitHub README / portfolio).

## OSPF (on ASAv and vIOS1, or FortiGate and vIOS2)
```
show ospf neighbor          (ASA)
show ip ospf neighbor       (IOS)
show ip route ospf          (IOS)
```
FortiGate:
```
get router info ospf neighbor
get router info routing-table ospf
```

## BGP (on vIOS1, vIOS3, vIOS2)
```
show ip bgp summary
show ip bgp
show ip route bgp
```
You should see vIOS1 and vIOS2 each learning the other site's LAN prefixes
(192.168.10/20/30.0/24 and 172.16.40/50.0/24) via BGP, redistributed from OSPF.

## VLAN / trunking (Switch4, Switch5)
```
show vlan brief
show interfaces trunk
show interfaces status
```

## Site-to-site VPN
ASA:
```
show crypto ikev2 sa
show crypto ipsec sa
```
FortiGate:
```
get vpn ipsec tunnel summary
diagnose vpn ike gateway list
diagnose vpn tunnel list
```
Bring the tunnel up by generating "interesting traffic" first, e.g. ping from
VPC8 (192.168.10.10) to VPC9 (172.16.40.10) - the SAs won't show until traffic
matching the phase2 selectors crosses.

## End-to-end reachability
From VPC8 (Site A): `ping 172.16.40.10` (should succeed, encrypted over the VPN)
From VPC11 (attacker VLAN): `ping 192.168.10.10` (should FAIL - blocked by
the ASA `VLAN30-OUT` ACL, and should show up in the ASA logs: `show logging`)

## Firewall policy hit counters
ASA: `show access-list VLAN30-OUT` (watch the "hitcnt" increment when VPC11 pings VPC8)
FortiGate: `get firewall policy` / check the log viewer under Log & Report > Forward Traffic
