# Traffic analysis & threat simulation (Wireshark)

This covers the "performed network monitoring, traffic analysis, and threat
simulation" bullet using the topology you already have.

## 1. Capturing traffic directly in EVE-NG
EVE-NG has a built-in per-link capture feature - no need to configure SPAN
manually for basic analysis:
- Right-click any link in the topology (e.g. Switch4 Gi0/0 <-> ASAv Gi0/1) > **Capture**
- It opens Wireshark locally (via a `.pcap` stream) showing live traffic on that link
- Good links to capture for your evidence: ASAv outside link (10.10.1.0/30) to see
  the VPN/ESP packets, and the Switch4 <-> ASAv trunk to see intra-site traffic.

## 2. SPAN port alternative (if you want it to look more "real")
On Switch4, mirror the trunk port to a spare port and connect a monitoring VM there:
```
monitor session 1 source interface GigabitEthernet0/0
monitor session 1 destination interface GigabitEthernet0/<spare>
```
Attach a VPC or Linux VM to that spare port running `tcpdump -i eth0 -w capture.pcap`,
then open the .pcap in Wireshark.

## 3. Threat simulation using VPC11 (the flagged "attacker" host)
VPC11 sits in VLAN 30, deliberately isolated from the server VLAN by the ASA
ACL (`VLAN30-OUT`). Use it to simulate common threats and capture the traffic:

- **Reconnaissance / port scan:** from VPC11, `nmap -sS 192.168.10.10` (if nmap is
  available on your VPC image) or simple repeated `ping`/`telnet` attempts against
  VPC8 - capture on the ASA inside-vpc11 link and show the ACL dropping it.
- **Unauthorized lateral movement:** attempt to reach 192.168.10.10 from VPC11 and
  show `show access-list VLAN30-OUT` hit counters incrementing, plus ASA `show logging`
  entries with the deny.
- **VPN traffic inspection:** capture on the ASA outside link while pinging Site A to
  Site B - you'll see ESP (protocol 50) packets, confirming the IPsec tunnel is
  actually encrypting the traffic rather than passing it in clear text.

## 4. What to put in your GitHub README / portfolio
For each scenario above: a screenshot of the Wireshark capture, plus the matching
`show access-list ... ` or `show logging` output as evidence the firewall policy
actually blocked (or the VPN actually encrypted) the traffic. That pairing is what
makes "threat simulation" and "traffic analysis" verifiable rather than just a
resume line.
