"""MAC vendor (OUI) lookup backed by a one-time local cache of the IEEE list.

The database is downloaded once into data/oui.csv on first use, then read
locally forever after. No cloud service or account is involved — this is a
single fetch of a public file. If the download fails (offline, etc.), vendor
lookups degrade gracefully to '' and everything else keeps working.
"""

import csv
import urllib.request

from .config import OUI_CACHE
from .util import ensure_dir

# Official IEEE OUI registry (public, ~4 MB). Format columns:
#   Registry, Assignment, Organization Name, Organization Address
OUI_URL = "https://standards-oui.ieee.org/oui/oui.csv"

_cache = None


def ensure_oui_db(quiet=False):
    """Download the OUI database once if it isn't already cached locally."""
    if OUI_CACHE.exists() and OUI_CACHE.stat().st_size > 0:
        return True
    ensure_dir(OUI_CACHE.parent)
    if not quiet:
        print("Fetching MAC vendor database (one-time, ~4 MB)...")
    try:
        request = urllib.request.Request(OUI_URL, headers={"User-Agent": "netagent"})
        with urllib.request.urlopen(request, timeout=30) as response:
            data = response.read()
        if not data:
            raise ValueError("empty response")
        OUI_CACHE.write_bytes(data)
        return True
    except Exception as exc:  # noqa: BLE001 - any failure degrades to no vendors
        if not quiet:
            print(f"  Could not download OUI database ({exc}).")
            print("  Vendor lookups will show 'Unknown'; re-run later with network access.")
        return False


def _load():
    global _cache
    if _cache is not None:
        return _cache
    _cache = {}
    if not OUI_CACHE.exists():
        return _cache
    try:
        with open(OUI_CACHE, newline="", encoding="utf-8", errors="replace") as f:
            reader = csv.reader(f)
            next(reader, None)  # header
            for row in reader:
                if len(row) >= 3:
                    prefix = row[1].strip().upper()
                    if len(prefix) == 6:
                        _cache[prefix] = row[2].strip()
    except (OSError, csv.Error):
        pass
    return _cache


def lookup(mac):
    """Return the vendor name for a MAC address, or '' if unknown."""
    if not mac:
        return ""
    prefix = mac.replace(":", "").replace("-", "").upper()[:6]
    return _load().get(prefix, "")
