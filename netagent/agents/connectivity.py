"""Agent 3 — connectivity: measure packet loss, latency, and jitter over time.

Pings the gateway plus a couple of well-known public IPs (1.1.1.1 / 8.8.8.8) at
a fixed interval for a set duration. This is the one agent that contacts
addresses outside the LAN — but only ICMP echo (ping) to fixed reliability
targets, never a scan or probe. Useful for "is it my Wi-Fi or my ISP".
"""

import statistics
import sys
import time

from .. import net
from ..config import DEFAULT_CONNECTIVITY_TARGETS, LATEST_CONNECTIVITY
from ..util import emit_json, now_iso, print_table, write_json


def _summarize(target, samples):
    sent = len(samples)
    rtts = [s for s in samples if s is not None]
    lost = sent - len(rtts)
    loss_pct = (lost / sent * 100) if sent else 0.0
    avg = statistics.mean(rtts) if rtts else None
    jitter = statistics.pstdev(rtts) if len(rtts) > 1 else 0.0
    lo = min(rtts) if rtts else None
    hi = max(rtts) if rtts else None

    flags = []
    if loss_pct > 2:
        flags.append("HIGH LOSS")
    if avg is not None and hi is not None and hi > avg * 3 and (hi - avg) > 50:
        flags.append("LATENCY SPIKE")

    return {
        "target": target,
        "sent": sent,
        "lost": lost,
        "loss_pct": round(loss_pct, 1),
        "avg_ms": round(avg, 1) if avg is not None else None,
        "min_ms": round(lo, 1) if lo is not None else None,
        "max_ms": round(hi, 1) if hi is not None else None,
        "jitter_ms": round(jitter, 1),
        "flags": flags,
    }


def run(args):
    # In --json mode, keep stdout clean for JSON: progress goes to stderr.
    log = sys.stderr if args.json else sys.stdout

    gateway = net.default_gateway()
    targets = []
    if gateway:
        targets.append(gateway)
    for t in (args.targets or DEFAULT_CONNECTIVITY_TARGETS):
        if t not in targets:
            targets.append(t)

    duration = args.duration
    interval = args.interval
    per_ping_timeout = int(interval * 1000) if interval < 2 else 1500

    print(f"Monitoring {len(targets)} target(s) for {duration}s (every {interval}s):", file=log)
    print(f"  targets: {', '.join(targets)}", file=log)
    print("  (press Ctrl-C to stop early and report partial results)\n", file=log)

    samples = {t: [] for t in targets}
    deadline = time.time() + duration
    rounds = 0
    try:
        while time.time() < deadline:
            for t in targets:
                samples[t].append(net.ping_once(t, timeout_ms=per_ping_timeout))
            rounds += 1
            print(f"\r  pings sent: {rounds} per target", end="", flush=True, file=log)
            remaining = deadline - time.time()
            if remaining > 0:
                time.sleep(min(interval, remaining))
    except KeyboardInterrupt:
        print("\n  stopped early — reporting partial results", file=log)
    print(file=log)

    results = [_summarize(t, samples[t]) for t in targets]

    record = {
        "timestamp": now_iso(),
        "duration_s": duration,
        "interval_s": interval,
        "gateway": gateway,
        "results": results,
    }
    write_json(LATEST_CONNECTIVITY, record)

    if args.json:
        emit_json(record)
        return 0

    print("\n=== Connectivity ===")
    rows = []
    for r in results:
        label = r["target"] + (" (gateway)" if r["target"] == gateway else "")
        rows.append(
            [
                label,
                f"{r['sent']}",
                f"{r['loss_pct']}%",
                f"{r['avg_ms']}" if r["avg_ms"] is not None else "-",
                f"{r['jitter_ms']}",
                f"{r['max_ms']}" if r["max_ms"] is not None else "-",
                ", ".join(r["flags"]) or "ok",
            ]
        )
    print_table(
        ["Target", "Sent", "Loss", "Avg ms", "Jitter", "Max ms", "Status"], rows
    )

    flagged = [r for r in results if r["flags"]]
    if flagged:
        print(f"\n[!] {len(flagged)} target(s) with problems:")
        for r in flagged:
            avg = f"{r['avg_ms']} ms" if r["avg_ms"] is not None else "n/a"
            print(f"    - {r['target']}: {', '.join(r['flags'])} "
                  f"(loss {r['loss_pct']}%, avg {avg})")
        # Heuristic hint: gateway healthy but public targets bad => likely ISP.
        gw = next((r for r in results if r["target"] == gateway), None)
        if gw and not gw["flags"] and flagged:
            print("    Hint: the gateway looks fine but external targets don't — "
                  "this points to your ISP/uplink rather than your Wi-Fi.")
    else:
        print("\nAll targets healthy (<=2% loss, no latency spikes).")
    return 0
