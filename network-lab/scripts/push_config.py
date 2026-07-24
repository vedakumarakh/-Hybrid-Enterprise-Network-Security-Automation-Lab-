#!/usr/bin/env python3
"""
push_config.py

Pushes a set of standardized configuration lines to multiple Cisco IOS
devices in one shot - the "reduced manual provisioning effort for
repetitive tasks" bullet on the resume. Example use case here: rolling
out an NTP server and a login banner to every router at once, instead
of doing it by hand on each console.

HOW TO RUN
----------
    pip install -r requirements.txt
    python push_config.py

Edit CONFIG_LINES below to whatever repetitive change you need to push
(e.g. a new ACL line, a syslog server, a new local user, updated SNMP
community, etc.) and it fans out to every IOS device in devices.yaml.

NOTE: This only targets device_type "cisco_ios" entries by default,
since ASA config syntax mode differs slightly - see ASA_CONFIG_LINES
below for pushing to the ASA specifically.
"""

import yaml
import logging
from netmiko import ConnectHandler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("push")

INVENTORY_FILE = "devices.yaml"

# Example repetitive provisioning task: standardize NTP + banner across all routers
CONFIG_LINES = [
    "ntp server 192.168.10.10",          # point at a lab NTP source, adjust as needed
    "logging host 192.168.10.10",
    "banner exec ^ Managed by Network Automation - unauthorized access prohibited ^",
]

# Example: push an object/ACL tweak to the ASA specifically
ASA_CONFIG_LINES = [
    "logging host inside-servers 192.168.10.10",
]


def load_inventory(path):
    with open(path) as f:
        return yaml.safe_load(f).get("devices", [])


def push_to_device(device, lines):
    conn_params = {
        "device_type": device["device_type"],
        "host": device["host"],
        "username": device["username"],
        "password": device["password"],
        "secret": device.get("secret", ""),
    }
    log.info(f"Pushing config to {device['name']} ({device['host']})...")
    conn = ConnectHandler(**conn_params)
    conn.enable()
    output = conn.send_config_set(lines)
    conn.save_config()  # runs 'write memory' / 'copy run start' equivalent
    conn.disconnect()
    log.info(f"  -> Done. Device output:\n{output}")


def main():
    devices = load_inventory(INVENTORY_FILE)

    for device in devices:
        try:
            if device["device_type"] == "cisco_ios":
                push_to_device(device, CONFIG_LINES)
            elif device["device_type"] == "cisco_asa":
                push_to_device(device, ASA_CONFIG_LINES)
        except Exception as e:
            log.error(f"Failed to push to {device['name']}: {e}")


if __name__ == "__main__":
    main()
