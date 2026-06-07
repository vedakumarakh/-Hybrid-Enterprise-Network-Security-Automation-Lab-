# Lab Setup Guide — EVE-NG

## Step 1: Install EVE-NG

Download EVE-NG Community OVA from https://www.eve-ng.net/index.php/download/  
Import into VMware Workstation or VirtualBox.  
Minimum specs: 8GB RAM, 4 vCPUs, 50GB disk.

## Step 2: Import Device Images

SSH into EVE-NG VM and upload the following images:

```bash
# Cisco ASA
mkdir -p /opt/unetlab/addons/qemu/asav-9.x/
# Upload asav991-1.qcow2 to this folder
/opt/unetlab/wrappers/unl_wrapper -a fixpermissions

# Cisco IOS-XR
mkdir -p /opt/unetlab/addons/qemu/iosxrv-7.x/
# Upload iosxrv9k-7.x.x.qcow2 to this folder

# FortiGate
mkdir -p /opt/unetlab/addons/qemu/fortinet-7.x/
# Upload fortios.qcow2 to this folder
```

## Step 3: Create the Lab Topology

1. Open EVE-NG web interface (http://your-eve-ng-ip)
2. Create new lab: `hybrid-enterprise-security-lab`
3. Add nodes:
   - 1x Cisco ASA (asav-9.x)
   - 1x Cisco IOS-XR (iosxrv-7.x)
   - 1x FortiGate (fortinet-7.x)
   - 2x Linux Ubuntu (for endpoints)
4. Connect nodes as per topology diagram
5. Add network bridges for WAN simulation

## Step 4: Apply Configurations

Connect to each device console and paste configs:

```bash
# For Cisco ASA
# Open console → paste contents of configs/cisco-asa/asa-firewall-base.cfg

# For Cisco IOS-XR
# Open console → paste contents of configs/cisco-ios-xr/core-router-config.cfg

# For FortiGate
# Open console → paste contents of configs/fortinet/fortigate-policy.cfg
```

## Step 5: Verify Connectivity

```bash
# From ASA - ping inside host
ping 192.168.10.10

# From IOS-XR - check BGP
show bgp summary

# From IOS-XR - check OSPF
show ospf neighbor

# From IOS-XR - check MPLS
show mpls ldp neighbor

# From FortiGate CLI - check VPN
get vpn ipsec tunnel summary
```

## Step 6: Run Automation Scripts

```bash
# Install dependencies
pip install -r automation/python/requirements.txt

# Run health monitor
python automation/python/network_health_monitor.py

# Run VPN monitor
python automation/python/vpn_tunnel_monitor.py

# Run Ansible backup
ansible-playbook -i automation/ansible/inventory.ini automation/ansible/backup-configs.yml
```

## Troubleshooting

| Issue | Fix |
|---|---|
| EVE-NG nodes won't start | Check image path and permissions with `fixpermissions` |
| SSH connection refused | Verify SSH is enabled on device and mgmt IP is correct |
| Ansible auth failure | Double-check inventory.ini credentials match device config |
| VPN tunnel not forming | Check IKEv2 policy match on both ends, verify PSK |
