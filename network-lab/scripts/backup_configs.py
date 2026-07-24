#!/usr/bin/env python3
"""
backup_configs.py

Connects to every device listed in devices.yaml over SSH (via Netmiko),
pulls the running config, and saves a timestamped copy locally.

HOW TO RUN
----------
1. On the machine that can reach the lab devices (your PC, or a VM/host
   with a leg into the EVE-NG cloud):
       pip install -r requirements.txt
2. Edit devices.yaml with the real management IPs/creds for your lab.
3. Run:
       python backup_configs.py
4. Backups land in ./backups/<hostname>_<timestamp>.cfg

This is the "automated network configuration backup" piece of the resume
bullet - point a cron job / Windows Task Scheduler at this script to run
it nightly and you have automated, versioned config backups.
"""

import os
import sys
import yaml
import logging
from datetime import datetime
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKUP_DIR = os.path.join(SCRIPT_DIR, "..", "backups")
INVENTORY_FILE = os.path.join(SCRIPT_DIR, "devices.yaml")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("backup")


def load_inventory(path):
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return data.get("devices", [])


def backup_device(device):
    name = device["name"]
    conn_params = {
        "device_type": device["device_type"],
        "host": device["host"],
        "username": device["username"],
        "password": device["password"],
        "secret": device.get("secret", ""),
    }

    log.info(f"Connecting to {name} ({device['host']})...")
    try:
        conn = ConnectHandler(**conn_params)
        conn.enable()

        # ASA and IOS both support "show running-config"
        running_config = conn.send_command("show running-config", read_timeout=60)

        conn.disconnect()

        os.makedirs(BACKUP_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(BACKUP_DIR, f"{name}_{timestamp}.cfg")

        with open(filename, "w") as f:
            f.write(running_config)

        log.info(f"  -> Saved {filename} ({len(running_config)} bytes)")
        return True

    except NetmikoAuthenticationException:
        log.error(f"  -> AUTH FAILED for {name}. Check username/password in devices.yaml")
    except NetmikoTimeoutException:
        log.error(f"  -> TIMEOUT connecting to {name} at {device['host']}. Check reachability/SSH.")
    except Exception as e:
        log.error(f"  -> Unexpected error for {name}: {e}")
    return False


def main():
    devices = load_inventory(INVENTORY_FILE)
    if not devices:
        log.error("No devices found in devices.yaml")
        sys.exit(1)

    log.info(f"Starting backup run for {len(devices)} device(s)...")
    results = {d["name"]: backup_device(d) for d in devices}

    log.info("---- Backup Summary ----")
    for name, ok in results.items():
        log.info(f"  {name}: {'OK' if ok else 'FAILED'}")

    if not all(results.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
