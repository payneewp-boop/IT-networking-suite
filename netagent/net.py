"""Cross-platform, dependency-free networking primitives.

Everything here uses the standard library and the OS's own tools (ping, arp,
ipconfig/scutil). Nothing requires raw sockets or elevated privileges, which
keeps the tool safe to run as a normal user. All helpers fail soft — on any
error they return an empty/None result rather than raising.
"""

import ipaddress
import platform
import re
import socket
import subprocess
from concurrent.futures import ThreadPoolExecutor

IS_WINDOWS = platform.system() == "Windows"
IS_MAC = platform.system() == "Darwin"

_MAC_SEARCH = re.compile(r"([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}")
_MAC_FULL = re.compile(r"^([0-9a-f]{2}:){5}[0-9a-f]{2}$")


def _run(cmd, timeout=10):
    """Run a command, returning stdout as text (empty string on any failure).

    ``errors="replace"`` guards against Windows tools (ipconfig/route) emitting
    output in the console OEM code page rather than clean UTF-8.
    """
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=timeout,
        )
        return proc.stdout or ""
    except (subprocess.SubprocessError, FileNotFoundError, OSError, ValueError):
        return ""


def _is_ip(value):
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def _norm_mac(value):
    mac = value.strip().lower().replace("-", ":")
    return mac if _MAC_FULL.match(mac) else None


def local_ip():
    """Best-effort local IP via a UDP socket (no packets are actually sent)."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        sock.close()


def default_gateway():
    """Return the default gateway IP, or None if it can't be determined."""
    if IS_WINDOWS:
        out = _run(["route", "print", "0.0.0.0"])
        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 3 and parts[0] == "0.0.0.0" and _is_ip(parts[2]):
                return parts[2]
        # Fallback: parse ipconfig. The gateway line may list an IPv6 address
        # first, so require a full dotted-quad rather than any digit run.
        out = _run(["ipconfig"])
        capturing = False
        for line in out.splitlines():
            if "Default Gateway" in line:
                capturing = True
            if capturing:
                m = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
                if m:
                    return m.group(1)
                # Continuation lines have no label; a new labelled line ends it.
                if ":" in line and "Default Gateway" not in line:
                    capturing = False
        return None

    # Linux: `ip route`; macOS/BSD: `netstat -rn`.
    out = _run(["ip", "route", "show", "default"])
    m = re.search(r"default via ([0-9.]+)", out)
    if m:
        return m.group(1)
    out = _run(["netstat", "-rn"])
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0] in ("default", "0.0.0.0") and _is_ip(parts[1]):
            return parts[1]
    return None


def local_subnet(prefix=24):
    """The IPv4 network containing this host, assuming the given prefix."""
    ip = local_ip()
    return ipaddress.ip_network(f"{ip}/{prefix}", strict=False)


def ping_cmd(host, count=1, timeout_ms=1000):
    """Build a platform-appropriate ping command (flags differ per OS)."""
    if IS_WINDOWS:
        return ["ping", "-n", str(count), "-w", str(timeout_ms), host]
    if IS_MAC:
        # macOS ping: -W is per-packet wait in milliseconds.
        return ["ping", "-c", str(count), "-W", str(timeout_ms), host]
    # Linux ping: -W is per-packet wait in *seconds*.
    secs = max(1, round(timeout_ms / 1000))
    return ["ping", "-c", str(count), "-W", str(secs), host]


def ping_once(host, timeout_ms=1000):
    """Ping a host once. Returns round-trip time in ms, or None if unreachable."""
    out = _run(ping_cmd(host, 1, timeout_ms), timeout=timeout_ms / 1000 + 3)
    if not out:
        return None
    m = re.search(r"time[=<]\s*([\d.]+)\s*ms", out, re.IGNORECASE)
    if m:
        return float(m.group(1))
    return None


def ping_sweep(hosts, workers=64, timeout_ms=800):
    """Ping every host in parallel to populate the ARP table. Returns live IPs."""
    alive = []

    def worker(host):
        return str(host) if ping_once(str(host), timeout_ms) is not None else None

    with ThreadPoolExecutor(max_workers=workers) as pool:
        for result in pool.map(worker, hosts):
            if result:
                alive.append(result)
    return alive


def arp_table():
    """Read the OS ARP/neighbour table. Returns {ip: mac} (normalized)."""
    result = {}
    out = _run(["arp", "-a"])

    if IS_WINDOWS:
        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 2 and _is_ip(parts[0]):
                mac = _norm_mac(parts[1])
                if mac and mac != "00:00:00:00:00:00" and mac != "ff:ff:ff:ff:ff:ff":
                    result[parts[0]] = mac
    else:
        for line in out.splitlines():
            ip_match = re.search(r"\(([0-9.]+)\)", line)
            mac_match = _MAC_SEARCH.search(line)
            if ip_match and mac_match:
                mac = _norm_mac(mac_match.group(0))
                if mac and mac != "00:00:00:00:00:00":
                    result[ip_match.group(1)] = mac

    # Linux fallback when `arp` isn't present.
    if not result and not IS_WINDOWS:
        out = _run(["ip", "neigh"])
        for line in out.splitlines():
            parts = line.split()
            if parts and _is_ip(parts[0]) and "lladdr" in parts:
                mac = _norm_mac(parts[parts.index("lladdr") + 1])
                if mac:
                    result[parts[0]] = mac
    return result


def resolve_hostname(ip):
    """Reverse-DNS lookup. Returns '' if the name can't be resolved."""
    try:
        return socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.gaierror, OSError):
        return ""


def dns_servers():
    """Return the list of configured DNS resolver IPs (IPv4, de-duplicated)."""
    found = []

    if IS_WINDOWS:
        out = _run(["ipconfig", "/all"])
        capturing = False
        for line in out.splitlines():
            if re.search(r"DNS Servers", line):
                capturing = True
                found.extend(re.findall(r"\d+\.\d+\.\d+\.\d+", line))
                continue
            elif capturing:
                stripped = line.strip()
                if re.fullmatch(r"\d+\.\d+\.\d+\.\d+", stripped):
                    found.append(stripped)
                elif re.fullmatch(r"[0-9A-Fa-f:%.]+", stripped):
                    # IPv6 DNS continuation line — skip it but keep reading.
                    continue
                else:
                    # A new labelled field (contains letters/':') ends the block.
                    capturing = False
    elif IS_MAC:
        out = _run(["scutil", "--dns"])
        found.extend(re.findall(r"nameserver\[\d+\]\s*:\s*([0-9.]+)", out))
    else:
        try:
            with open("/etc/resolv.conf", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("nameserver"):
                        parts = line.split()
                        if len(parts) >= 2:
                            found.append(parts[1])
        except OSError:
            pass

    seen = set()
    ordered = []
    for server in found:
        if _is_ip(server) and server not in seen:
            seen.add(server)
            ordered.append(server)
    return ordered


def scan_port(ip, port, timeout=0.5):
    """TCP connect-scan a single port. Returns True if it accepts a connection."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        return sock.connect_ex((ip, port)) == 0
    except OSError:
        return False
    finally:
        sock.close()


def scan_ports(ip, ports, timeout=0.5, workers=32):
    """Connect-scan a list of ports on one host. Returns sorted open ports."""
    open_ports = []

    def worker(port):
        return (port, scan_port(ip, port, timeout))

    with ThreadPoolExecutor(max_workers=workers) as pool:
        for port, is_open in pool.map(worker, ports):
            if is_open:
                open_ports.append(port)
    return sorted(open_ports)
