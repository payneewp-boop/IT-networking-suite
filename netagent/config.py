"""Static configuration: paths, port lists, known-good DNS resolvers.

Paths default to the current working directory so the tool keeps its data next
to wherever you run it. Override the root with the NETAGENT_HOME env var.
"""

import os
from pathlib import Path

APP_NAME = "netagent"

BASE_DIR = Path(os.environ.get("NETAGENT_HOME", Path.cwd()))
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
OUI_CACHE = DATA_DIR / "oui.csv"

# Stable pointers to the most recent output of each agent (read by `report`).
LATEST_INVENTORY = DATA_DIR / "latest_inventory.json"
LATEST_AUDIT = DATA_DIR / "latest_audit.json"
LATEST_CONNECTIVITY = DATA_DIR / "latest_connectivity.json"

# Ports checked during the audit. Local TCP connect-scan only — never external.
COMMON_PORTS = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    139: "NetBIOS",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    631: "IPP/Printing",
    3389: "RDP",
    5900: "VNC",
    8080: "HTTP-alt",
    8443: "HTTPS-alt",
    9100: "JetDirect/Printer",
}

# Ports that are risky to have exposed on a home LAN, with the reason.
INSECURE_PORTS = {
    21: "FTP — unencrypted file transfer",
    23: "Telnet — plaintext remote login (high risk)",
    25: "SMTP — possible open mail relay",
    139: "NetBIOS — legacy SMB, frequent malware target",
    5900: "VNC — remote desktop, often unencrypted",
}

# Public resolvers treated as "expected if intentional" rather than suspicious.
KNOWN_PUBLIC_DNS = {
    "1.1.1.1": "Cloudflare",
    "1.0.0.1": "Cloudflare",
    "8.8.8.8": "Google",
    "8.8.4.4": "Google",
    "9.9.9.9": "Quad9",
    "149.112.112.112": "Quad9",
    "208.67.222.222": "OpenDNS",
    "208.67.220.220": "OpenDNS",
}

# Reliability targets for the connectivity agent (gateway is added at runtime).
DEFAULT_CONNECTIVITY_TARGETS = ["1.1.1.1", "8.8.8.8"]
