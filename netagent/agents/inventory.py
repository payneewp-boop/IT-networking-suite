"""Agent 1 — inventory: discover devices on the local subnet and flag new ones."""

import ipaddress

from .. import net, oui
from ..config import DATA_DIR, LATEST_INVENTORY
from ..util import (
    now_iso,
    print_table,
    read_json,
    timestamp_slug,
    write_csv,
    write_json,
)

_FIELDS = ["ip", "mac", "hostname", "vendor", "is_gateway", "new"]


def _previous_inventory_file():
    """Most recent timestamped inventory snapshot, if any (excludes pointer)."""
    files = sorted(DATA_DIR.glob("inventory-*.json"))
    return files[-1] if files else None


def _ip_sort_key(ip):
    try:
        return tuple(int(part) for part in ip.split("."))
    except ValueError:
        return (0,)


def run(args):
    print("Detecting network...")
    gateway = net.default_gateway()
    ip = net.local_ip()
    try:
        subnet = net.local_subnet(args.prefix)
    except ValueError as exc:
        print(f"Could not determine subnet: {exc}")
        return 1

    print(f"  Local IP: {ip}")
    print(f"  Gateway:  {gateway or 'unknown'}")
    print(f"  Subnet:   {subnet}")

    hosts = list(subnet.hosts())
    if len(hosts) > 1024:
        print(
            f"  Subnet has {len(hosts)} addresses — too large to sweep safely.\n"
            f"  Narrow it with --prefix (e.g. --prefix 24). Aborting."
        )
        return 1

    print(f"Pinging {len(hosts)} addresses to populate the ARP table (~30s)...")
    net.ping_sweep(hosts, timeout_ms=args.timeout)

    print("Reading ARP table...")
    arp = net.arp_table()
    if not arp:
        print(
            "  No devices found in the ARP table. This can happen if the ping\n"
            "  sweep was blocked by a firewall or the interface is idle. Try\n"
            "  re-running, or check that you're connected to the network."
        )

    oui.ensure_oui_db()

    # Load previous snapshot BEFORE writing the new one, for the new-device diff.
    prev = read_json(_previous_inventory_file()) if _previous_inventory_file() else None
    prev_macs = {d["mac"] for d in prev["devices"]} if prev else set()

    devices = []
    for dip, mac in sorted(arp.items(), key=lambda kv: _ip_sort_key(kv[0])):
        try:
            if ipaddress.ip_address(dip) not in subnet:
                continue
        except ValueError:
            continue
        devices.append(
            {
                "ip": dip,
                "mac": mac,
                "hostname": net.resolve_hostname(dip),
                "vendor": oui.lookup(mac),
                "is_gateway": dip == gateway,
                # Only flag as new when we actually have a prior scan to compare.
                "new": bool(prev_macs) and mac not in prev_macs,
            }
        )

    record = {
        "timestamp": now_iso(),
        "gateway": gateway,
        "subnet": str(subnet),
        "device_count": len(devices),
        "devices": devices,
    }

    slug = timestamp_slug()
    json_path = DATA_DIR / f"inventory-{slug}.json"
    csv_path = DATA_DIR / f"inventory-{slug}.csv"
    write_json(json_path, record)
    write_csv(csv_path, devices, _FIELDS)
    write_json(LATEST_INVENTORY, record)

    print(f"\nFound {len(devices)} device(s) on {subnet}:\n")
    rows = [
        [
            d["ip"],
            d["mac"],
            (d["vendor"] or "-")[:24],
            (d["hostname"] or "-")[:26],
            "gateway" if d["is_gateway"] else ("NEW" if d["new"] else ""),
        ]
        for d in devices
    ]
    if rows:
        print_table(["IP", "MAC", "Vendor", "Hostname", "Note"], rows)

    new_devices = [d for d in devices if d["new"]]
    if new_devices:
        print(f"\n[!] {len(new_devices)} NEW device(s) since the last scan:")
        for d in new_devices:
            print(f"    - {d['ip']}  {d['mac']}  {d['vendor'] or 'Unknown vendor'}")
    elif prev_macs:
        print("\nNo new devices since the last scan.")

    print(f"\nSaved snapshot: {json_path}")
    print(f"Saved CSV:      {csv_path}")
    return 0
