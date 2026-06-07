#!/usr/bin/env python3
"""
============================================================
VPN Tunnel Monitor - Hybrid Enterprise Security Lab
Project: Hybrid Enterprise Network Security Lab
Author: Vedakumara K H
Description:
    Monitors site-to-site VPN tunnel status on Cisco ASA
    and Fortinet FortiGate. Sends alert email if tunnel goes down.
    Simulates real NOC incident response automation.
============================================================
"""

import smtplib
import time
import logging
import json
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from netmiko import ConnectHandler

# ── Logging ───────────────────────────────────────────────────
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/vpn-monitor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────
POLL_INTERVAL = 60          # seconds between checks
ALERT_EMAIL   = "vedakumarakh@gmail.com"
SMTP_SERVER   = "smtp.gmail.com"
SMTP_PORT     = 587

ASA_DEVICE = {
    "device_type": "cisco_asa",
    "host": "192.168.10.2",
    "username": "admin",
    "password": "cisco123",
    "port": 22,
    "name": "ASA-FW-01"
}

TUNNEL_PEERS = [
    {"peer": "52.x.x.x",  "description": "AWS VPC VPN Tunnel",       "expected_state": "MM_ACTIVE"},
    {"peer": "10.10.10.2", "description": "Branch Office VPN Tunnel", "expected_state": "MM_ACTIVE"},
]


# ── Core Functions ────────────────────────────────────────────

def check_vpn_tunnels(connection: ConnectHandler) -> list:
    """Check VPN tunnel states on Cisco ASA."""
    output = connection.send_command("show crypto ikev2 sa")
    results = []

    for tunnel in TUNNEL_PEERS:
        peer = tunnel["peer"]
        if peer in output:
            # Find state in output line
            for line in output.split("\n"):
                if peer in line:
                    state = "MM_ACTIVE" if "MM_ACTIVE" in line else "DOWN"
                    results.append({
                        "peer": peer,
                        "description": tunnel["description"],
                        "state": state,
                        "expected": tunnel["expected_state"],
                        "healthy": state == tunnel["expected_state"],
                        "raw_line": line.strip()
                    })
                    break
        else:
            results.append({
                "peer": peer,
                "description": tunnel["description"],
                "state": "MISSING",
                "expected": tunnel["expected_state"],
                "healthy": False,
                "raw_line": "Peer not found in IKEv2 SA table"
            })

    return results


def send_alert(subject: str, body: str):
    """Send email alert for tunnel down event."""
    try:
        msg = MIMEMultipart()
        msg["From"]    = ALERT_EMAIL
        msg["To"]      = ALERT_EMAIL
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        # NOTE: Use app password for Gmail, not your actual password
        # Set GMAIL_APP_PASSWORD as environment variable
        app_password = os.environ.get("GMAIL_APP_PASSWORD", "")
        if not app_password:
            logger.warning("GMAIL_APP_PASSWORD not set — email alert skipped")
            return

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(ALERT_EMAIL, app_password)
            server.sendmail(ALERT_EMAIL, ALERT_EMAIL, msg.as_string())
            logger.info(f"Alert email sent: {subject}")

    except Exception as e:
        logger.error(f"Failed to send alert email: {e}")


def log_tunnel_status(results: list):
    """Log tunnel status to JSON file for historical tracking."""
    os.makedirs("reports", exist_ok=True)
    log_file = "reports/vpn-tunnel-history.json"

    history = []
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            history = json.load(f)

    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "tunnels": results
    }
    history.append(entry)

    # Keep last 1000 entries only
    history = history[-1000:]

    with open(log_file, "w") as f:
        json.dump(history, f, indent=2)


def monitor_loop():
    """Main monitoring loop — polls every POLL_INTERVAL seconds."""
    logger.info("Starting VPN tunnel monitoring...")
    logger.info(f"Monitoring {len(TUNNEL_PEERS)} tunnel(s) every {POLL_INTERVAL}s")

    alert_sent = {}  # Track which tunnels have already been alerted

    while True:
        try:
            logger.info("Connecting to ASA for tunnel check...")
            connection = ConnectHandler(**{k: v for k, v in ASA_DEVICE.items() if k != "name"})
            results = check_vpn_tunnels(connection)
            connection.disconnect()

            log_tunnel_status(results)

            for tunnel in results:
                peer = tunnel["peer"]
                if tunnel["healthy"]:
                    status_icon = "✓"
                    if alert_sent.get(peer):
                        # Tunnel recovered — send recovery alert
                        send_alert(
                            subject=f"[RECOVERY] VPN Tunnel UP: {tunnel['description']}",
                            body=(
                                f"VPN Tunnel has RECOVERED.\n\n"
                                f"Peer: {peer}\n"
                                f"Description: {tunnel['description']}\n"
                                f"State: {tunnel['state']}\n"
                                f"Time: {datetime.utcnow().isoformat()} UTC\n"
                            )
                        )
                        alert_sent[peer] = False
                else:
                    status_icon = "✗"
                    if not alert_sent.get(peer):
                        # First detection of tunnel down — send alert
                        send_alert(
                            subject=f"[ALERT] VPN Tunnel DOWN: {tunnel['description']}",
                            body=(
                                f"VPN Tunnel is DOWN!\n\n"
                                f"Peer: {peer}\n"
                                f"Description: {tunnel['description']}\n"
                                f"State: {tunnel['state']} (expected: {tunnel['expected']})\n"
                                f"Raw output: {tunnel['raw_line']}\n"
                                f"Time: {datetime.utcnow().isoformat()} UTC\n\n"
                                f"Action Required: Check IKEv2 SA on ASA-FW-01 immediately.\n"
                            )
                        )
                        alert_sent[peer] = True

                logger.info(
                    f"  {status_icon} {tunnel['description']} ({peer}) → {tunnel['state']}"
                )

        except Exception as e:
            logger.error(f"Monitoring error: {e}")

        logger.info(f"Next check in {POLL_INTERVAL}s...\n")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    monitor_loop()
