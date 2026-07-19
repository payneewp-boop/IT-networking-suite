"""Agent 2 — audit: read-only local security checklist over inventory devices.

Does NOT touch the router or change any setting. It only observes: connect-scans
common ports on devices already discovered by `inventory`, flags insecure ones,
and reviews the configured DNS resolvers.
"""

from .. import net
from ..config import (
    COMMON_PORTS,
    DATA_DIR,
    INSECURE_PORTS,
    KNOWN_PUBLIC_DNS,
    LATEST_AUDIT,
    LATEST_INVENTORY,
    REPORTS_DIR,
)
from ..util import (
    ensure_dir,
    now_iso,
    print_table,
    read_json,
    today_str,
    write_json,
)


def _load_latest_inventory():
    data = read_json(LATEST_INVENTORY)
    if data:
        return data
    files = sorted(DATA_DIR.glob("inventory-*.json"))
    return read_json(files[-1]) if files else None


def _check_dns(dns, gateway):
    """Return a list of (severity, check, detail) tuples for DNS resolvers."""
    findings = []
    for server in dns:
        if server == gateway:
            findings.append(("PASS", f"DNS {server}", "router — expected"))
        elif server in KNOWN_PUBLIC_DNS:
            findings.append(
                ("WARN", f"DNS {server}", f"public resolver ({KNOWN_PUBLIC_DNS[server]}) — fine if intentional")
            )
        elif server.startswith("127.") or server.startswith("169.254."):
            findings.append(("PASS", f"DNS {server}", "local/stub resolver"))
        else:
            findings.append(
                ("FAIL", f"DNS {server}", "unrecognized resolver — verify this is intentional")
            )
    if not dns:
        findings.append(("WARN", "DNS servers", "could not read DNS configuration"))
    return findings


def _export_markdown(result, counts):
    ensure_dir(REPORTS_DIR)
    path = REPORTS_DIR / f"audit-{today_str()}.md"
    lines = [
        f"# Security Audit — {today_str()}",
        f"_Generated {result['timestamp']}_",
        "",
        f"**Summary:** {counts['PASS']} pass · {counts['WARN']} warn · {counts['FAIL']} fail",
        "",
        "## Findings",
        "",
        "| Result | Check | Detail |",
        "| --- | --- | --- |",
    ]
    for f in result["findings"]:
        lines.append(f"| {f['severity']} | {f['check']} | {f['detail']} |")
    lines += ["", "## Open ports by device", ""]
    any_ports = False
    for d in result["devices"]:
        if d["open_ports"]:
            any_ports = True
            names = ", ".join(f"{p}/{COMMON_PORTS.get(p, '?')}" for p in d["open_ports"])
            host = f" ({d['hostname']})" if d.get("hostname") else ""
            lines.append(f"- `{d['ip']}`{host}: {names}")
    if not any_ports:
        lines.append("- None detected.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def run(args):
    inv = _load_latest_inventory()
    if not inv:
        print("No inventory found. Run `netagent inventory` first.")
        return 1

    gateway = inv.get("gateway")
    ports = sorted(COMMON_PORTS)
    findings = []
    device_results = []

    print(f"Auditing {len(inv['devices'])} device(s) from inventory ({inv['timestamp']})...")
    for d in inv["devices"]:
        open_ports = net.scan_ports(d["ip"], ports, timeout=args.timeout / 1000)
        insecure = [p for p in open_ports if p in INSECURE_PORTS]
        device_results.append({**d, "open_ports": open_ports, "insecure_ports": insecure})
        for p in insecure:
            findings.append(
                ("FAIL", f"{d['ip']} exposes port {p} ({COMMON_PORTS.get(p, '?')})", INSECURE_PORTS[p])
            )

    if not any(dr["insecure_ports"] for dr in device_results):
        checked = ", ".join(str(p) for p in sorted(INSECURE_PORTS))
        findings.append(("PASS", "No insecure ports exposed on the LAN", f"checked: {checked}"))

    dns = net.dns_servers()
    findings.extend(_check_dns(dns, gateway))

    counts = {"PASS": 0, "WARN": 0, "FAIL": 0}
    for severity, _check, _detail in findings:
        counts[severity] = counts.get(severity, 0) + 1

    result = {
        "timestamp": now_iso(),
        "inventory_timestamp": inv["timestamp"],
        "gateway": gateway,
        "dns_servers": dns,
        "counts": counts,
        "findings": [
            {"severity": s, "check": c, "detail": d} for (s, c, d) in findings
        ],
        "devices": device_results,
    }
    write_json(LATEST_AUDIT, result)

    print("\n=== Security Audit ===")
    print_table(["Result", "Check", "Detail"], [[s, c, d] for (s, c, d) in findings])

    print("\nOpen ports by device:")
    port_rows = [
        [
            d["ip"],
            (d.get("hostname") or "-")[:26],
            ", ".join(f"{p}/{COMMON_PORTS.get(p, '?')}" for p in d["open_ports"]),
        ]
        for d in device_results
        if d["open_ports"]
    ]
    if port_rows:
        print_table(["IP", "Hostname", "Open ports"], port_rows)
    else:
        print("  none detected")

    print(
        f"\nSummary: {counts['PASS']} pass, {counts['WARN']} warn, {counts['FAIL']} fail"
    )
    print(
        "Note: router settings (WPA3, admin password, firmware) are not checked "
        "here — review those in the admin panel."
    )

    if args.markdown:
        path = _export_markdown(result, counts)
        print(f"Markdown report: {path}")
    return 0
