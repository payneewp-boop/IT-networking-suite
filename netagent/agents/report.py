"""Agent 4 — report: combine the latest agent outputs into a dated markdown file.

Highlights only what changed or needs attention (new devices, audit failures,
degraded links) rather than re-dumping everything.
"""

from ..config import (
    COMMON_PORTS,
    LATEST_AUDIT,
    LATEST_CONNECTIVITY,
    LATEST_INVENTORY,
    REPORTS_DIR,
)
from ..util import emit_json, ensure_dir, now_iso, read_json, today_str


def run(args):
    inv = read_json(LATEST_INVENTORY)
    audit = read_json(LATEST_AUDIT)
    conn = read_json(LATEST_CONNECTIVITY)

    if not any([inv, audit, conn]):
        print(
            "No agent output found in data/. Run `inventory`, `audit`, and "
            "`connectivity` first."
        )
        return 1

    attention = []  # short bullet strings for the top-of-report summary
    body = []

    # --- Devices ---
    if inv:
        new_devices = [d for d in inv["devices"] if d.get("new")]
        body.append("## Devices")
        body.append(f"- {inv.get('device_count', len(inv['devices']))} device(s) on "
                    f"`{inv.get('subnet', '?')}` (scan {inv['timestamp']}).")
        if new_devices:
            attention.append(f"{len(new_devices)} new device(s) on the network")
            body.append(f"- **{len(new_devices)} new since previous scan:**")
            for d in new_devices:
                host = f" ({d['hostname']})" if d.get("hostname") else ""
                body.append(f"  - `{d['ip']}` {d['mac']} — {d.get('vendor') or 'Unknown'}{host}")
        else:
            body.append("- No new devices since the previous scan.")
        body.append("")

    # --- Security audit ---
    if audit:
        counts = audit.get("counts", {})
        fails = [f for f in audit["findings"] if f["severity"] == "FAIL"]
        warns = [f for f in audit["findings"] if f["severity"] == "WARN"]
        body.append("## Security audit")
        body.append(f"- {counts.get('PASS', 0)} pass · {counts.get('WARN', 0)} warn · "
                    f"{counts.get('FAIL', 0)} fail (audit {audit['timestamp']}).")
        if fails:
            attention.append(f"{len(fails)} audit failure(s)")
            body.append("- **Failures:**")
            for f in fails:
                body.append(f"  - {f['check']} — {f['detail']}")
        if warns:
            body.append("- Warnings:")
            for f in warns:
                body.append(f"  - {f['check']} — {f['detail']}")
        if not fails and not warns:
            body.append("- No failures or warnings.")
        body.append("")

    # --- Connectivity ---
    if conn:
        flagged = [r for r in conn["results"] if r.get("flags")]
        body.append("## Connectivity")
        body.append(f"- Monitored {len(conn['results'])} target(s) over "
                    f"{conn.get('duration_s', '?')}s (run {conn['timestamp']}).")
        if flagged:
            attention.append(f"{len(flagged)} connectivity target(s) degraded")
            for r in flagged:
                avg = f"{r['avg_ms']} ms" if r["avg_ms"] is not None else "n/a"
                body.append(f"- **{r['target']}**: {', '.join(r['flags'])} "
                            f"(loss {r['loss_pct']}%, avg {avg}, jitter {r['jitter_ms']} ms)")
        else:
            worst = max(conn["results"], key=lambda r: r.get("loss_pct", 0), default=None)
            detail = ""
            if worst:
                detail = f" (worst loss {worst['loss_pct']}% on {worst['target']})"
            body.append(f"- All targets healthy{detail}.")
        body.append("")

    # --- Assemble ---
    lines = [f"# Home Network Report — {today_str()}", f"_Generated {now_iso()}_", ""]
    lines.append("## Needs attention")
    if attention:
        for item in attention:
            lines.append(f"- [!] {item}")
    else:
        lines.append("- Nothing flagged. Network looks healthy.")
    lines.append("")
    lines.extend(body)

    ensure_dir(REPORTS_DIR)
    path = REPORTS_DIR / f"{today_str()}.md"
    path.write_text("\n".join(lines), encoding="utf-8")

    if getattr(args, "json", False):
        emit_json(
            {
                "date": today_str(),
                "generated": now_iso(),
                "report_path": str(path),
                "attention": attention,
                "inventory": {
                    "timestamp": inv["timestamp"],
                    "device_count": inv.get("device_count", len(inv["devices"])),
                    "new_devices": [d for d in inv["devices"] if d.get("new")],
                } if inv else None,
                "audit": {
                    "timestamp": audit["timestamp"],
                    "counts": audit.get("counts", {}),
                    "failures": [f for f in audit["findings"] if f["severity"] == "FAIL"],
                    "warnings": [f for f in audit["findings"] if f["severity"] == "WARN"],
                } if audit else None,
                "connectivity": {
                    "timestamp": conn["timestamp"],
                    "flagged": [r for r in conn["results"] if r.get("flags")],
                    "results": conn["results"],
                } if conn else None,
            }
        )
        return 0

    print(f"Report written: {path}\n")
    print("Needs attention:")
    if attention:
        for item in attention:
            print(f"  [!] {item}")
    else:
        print("  Nothing flagged. Network looks healthy.")
    return 0
