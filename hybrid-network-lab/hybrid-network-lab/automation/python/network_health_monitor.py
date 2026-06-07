#!/usr/bin/env python3
"""
============================================================
Network Health Monitor - Hybrid Enterprise Security Lab
Project: Hybrid Enterprise Network Security Lab
Author: Vedakumara K H
Description:
    Connects to network devices via SSH (Netmiko),
    runs health checks, and generates a monitoring report.
    Simulates real NOC-style monitoring automation.
============================================================
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List

from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException

# ── Logging Setup ────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/network-monitor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ── Device Inventory ─────────────────────────────────────────
DEVICES = [
    {
        "device_type": "cisco_xr",
        "host": "192.168.1.1",
        "username": "admin",
        "password": "Admin@123",
        "port": 22,
        "name": "CORE-RTR-01"
    },
    {
        "device_type": "cisco_asa",
        "host": "192.168.10.2",
        "username": "admin",
        "password": "cisco123",
        "port": 22,
        "name": "ASA-FW-01"
    }
]

# ── Health Check Commands per device type ────────────────────
HEALTH_COMMANDS = {
    "cisco_xr": [
        "show interfaces brief",
        "show bgp summary",
        "show ospf neighbor",
        "show mpls ldp neighbor",
        "show logging last 20",
    ],
    "cisco_asa": [
        "show interface ip brief",
        "show crypto ikev2 sa",
        "show conn count",
        "show threat-detection statistics",
        "show logging | last 20",
    ]
}

# ── Thresholds ───────────────────────────────────────────────
THRESHOLDS = {
    "max_bgp_prefixes": 1000,
    "min_ospf_neighbors": 1,
    "max_connections": 5000,
}


def connect_to_device(device: Dict) -> ConnectHandler:
    """Establish SSH connection to a network device."""
    logger.info(f"Connecting to {device['name']} ({device['host']})...")
    connection = ConnectHandler(
        device_type=device["device_type"],
        host=device["host"],
        username=device["username"],
        password=device["password"],
        port=device["port"],
    )
    logger.info(f"Connected to {device['name']} successfully.")
    return connection


def run_health_checks(connection: ConnectHandler, device_type: str) -> Dict:
    """Run all health check commands and return output dict."""
    results = {}
    commands = HEALTH_COMMANDS.get(device_type, [])
    for cmd in commands:
        logger.info(f"Running: {cmd}")
        output = connection.send_command(cmd)
        results[cmd] = output
    return results


def parse_bgp_status(bgp_output: str) -> Dict:
    """Parse BGP summary output and extract neighbor states."""
    neighbors = []
    lines = bgp_output.strip().split("\n")
    for line in lines:
        if any(state in line for state in ["Established", "Active", "Idle", "Connect"]):
            parts = line.split()
            if len(parts) >= 3:
                neighbors.append({
                    "neighbor": parts[0],
                    "state": parts[-1],
                    "prefixes": parts[3] if len(parts) > 3 else "N/A"
                })
    return {"neighbors": neighbors, "count": len(neighbors)}


def check_interface_status(interface_output: str) -> List[Dict]:
    """Check for any down interfaces."""
    down_interfaces = []
    lines = interface_output.strip().split("\n")
    for line in lines:
        if "down" in line.lower() or "Down" in line:
            parts = line.split()
            if parts:
                down_interfaces.append({
                    "interface": parts[0],
                    "status": "DOWN",
                    "line": line.strip()
                })
    return down_interfaces


def generate_report(device_name: str, health_data: Dict, report_dir: str) -> str:
    """Generate a health check report for a device."""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(report_dir, f"{device_name}-health-{timestamp}.txt")

    bgp_output = health_data.get("show bgp summary", "")
    interface_output = health_data.get(
        "show interfaces brief",
        health_data.get("show interface ip brief", "")
    )

    bgp_status = parse_bgp_status(bgp_output)
    down_interfaces = check_interface_status(interface_output)

    report_lines = [
        "=" * 60,
        f"Network Health Report - {device_name}",
        f"Generated: {datetime.utcnow().isoformat()} UTC",
        "=" * 60,
        "",
        "BGP STATUS:",
        f"  Active Neighbors: {bgp_status['count']}",
    ]
    for neighbor in bgp_status["neighbors"]:
        status_flag = "✓" if neighbor["state"] == "Established" else "✗"
        report_lines.append(
            f"  {status_flag} {neighbor['neighbor']} → {neighbor['state']} (Prefixes: {neighbor['prefixes']})"
        )

    report_lines += [
        "",
        "INTERFACE STATUS:",
        f"  Down interfaces found: {len(down_interfaces)}",
    ]
    for iface in down_interfaces:
        report_lines.append(f"  ✗ {iface['interface']} is DOWN")

    report_lines += [
        "",
        "RAW OUTPUT:",
        "-" * 40,
    ]
    for cmd, output in health_data.items():
        report_lines += [f"\n[{cmd}]", output, ""]

    report_content = "\n".join(report_lines)

    os.makedirs(report_dir, exist_ok=True)
    with open(report_path, "w") as f:
        f.write(report_content)

    logger.info(f"Report saved: {report_path}")
    return report_path


def main():
    """Main entry point — connect to all devices and run health checks."""
    os.makedirs("logs", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    summary = []

    for device in DEVICES:
        device_name = device["name"]
        try:
            connection = connect_to_device(device)
            health_data = run_health_checks(connection, device["device_type"])
            report_path = generate_report(device_name, health_data, "reports")
            connection.disconnect()

            summary.append({
                "device": device_name,
                "status": "SUCCESS",
                "report": report_path
            })

        except NetmikoAuthenticationException:
            logger.error(f"Authentication failed for {device_name}")
            summary.append({"device": device_name, "status": "AUTH_FAILED"})

        except NetmikoTimeoutException:
            logger.error(f"Connection timed out for {device_name}")
            summary.append({"device": device_name, "status": "TIMEOUT"})

        except Exception as e:
            logger.error(f"Unexpected error for {device_name}: {e}")
            summary.append({"device": device_name, "status": "ERROR", "error": str(e)})

    # Save summary JSON
    summary_path = f"reports/summary-{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    logger.info(f"\nAll devices processed. Summary: {summary_path}")
    for s in summary:
        status_icon = "✓" if s["status"] == "SUCCESS" else "✗"
        logger.info(f"  {status_icon} {s['device']} → {s['status']}")


if __name__ == "__main__":
    main()
