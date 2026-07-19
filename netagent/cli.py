"""Command-line entry point: `netagent <inventory|audit|connectivity|report>`."""

import argparse

from .agents import audit, connectivity, inventory, report


def build_parser():
    parser = argparse.ArgumentParser(
        prog="netagent",
        description="Local home-network monitoring & security agents "
                    "(read-only, LAN-only).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_inv = sub.add_parser(
        "inventory", help="Scan the local subnet and list connected devices."
    )
    p_inv.add_argument("--prefix", type=int, default=24,
                       help="Subnet prefix length to scan (default: 24).")
    p_inv.add_argument("--timeout", type=int, default=800,
                       help="Per-host ping timeout in ms (default: 800).")
    p_inv.add_argument("--json", action="store_true",
                       help="Emit the result as JSON to stdout (progress goes to stderr).")
    p_inv.set_defaults(func=inventory.run)

    p_audit = sub.add_parser(
        "audit", help="Run the local security checklist over inventory devices."
    )
    p_audit.add_argument("--timeout", type=int, default=500,
                         help="Per-port connect timeout in ms (default: 500).")
    p_audit.add_argument("--markdown", action="store_true",
                         help="Also export a markdown report to reports/.")
    p_audit.add_argument("--json", action="store_true",
                         help="Emit the result as JSON to stdout (progress goes to stderr).")
    p_audit.set_defaults(func=audit.run)

    p_conn = sub.add_parser(
        "connectivity",
        help="Ping reliability targets and report loss/latency/jitter.",
    )
    p_conn.add_argument("--duration", type=int, default=300,
                        help="Total monitoring duration in seconds (default: 300).")
    p_conn.add_argument("--interval", type=float, default=2.0,
                        help="Seconds between pings (default: 2).")
    p_conn.add_argument("--targets", nargs="*",
                        help="Override targets (the gateway is always included).")
    p_conn.add_argument("--json", action="store_true",
                        help="Emit the result as JSON to stdout (progress goes to stderr).")
    p_conn.set_defaults(func=connectivity.run)

    p_report = sub.add_parser(
        "report", help="Combine the latest agent outputs into a dated markdown report."
    )
    p_report.add_argument("--json", action="store_true",
                          help="Also emit the combined summary as JSON to stdout.")
    p_report.set_defaults(func=report.run)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args) or 0
    except KeyboardInterrupt:
        print("\nInterrupted.")
        return 130
    except PermissionError as exc:
        print(f"Permission error: {exc}")
        print("This tool is designed to run without elevated privileges. Check your "
              "OS firewall or run from a normal user shell.")
        return 1
    except Exception as exc:  # noqa: BLE001 - fail gracefully, never crash
        print(f"Error: {exc}")
        return 1
