"""Small shared helpers: timestamps, JSON/CSV I/O, terminal tables."""

import csv
import json
import sys
from datetime import datetime
from pathlib import Path


def emit_json(record):
    """Print a structured record as JSON to stdout (for --json mode)."""
    json.dump(record, sys.stdout, indent=2, default=str)
    sys.stdout.write("\n")


def now_iso():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def today_str():
    return datetime.now().strftime("%Y-%m-%d")


def timestamp_slug():
    return datetime.now().strftime("%Y%m%dT%H%M%S")


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, data):
    ensure_dir(path.parent)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def read_json(path: Path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def write_csv(path: Path, rows, fieldnames):
    ensure_dir(path.parent)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def print_table(headers, rows):
    """Print a simple left-aligned text table. rows is a list of sequences."""
    cols = len(headers)
    widths = [len(str(h)) for h in headers]
    for row in rows:
        for i in range(cols):
            widths[i] = max(widths[i], len(str(row[i])))

    def fmt(vals):
        return "  ".join(str(v).ljust(widths[i]) for i, v in enumerate(vals))

    print(fmt(headers))
    print("  ".join("-" * widths[i] for i in range(cols)))
    for row in rows:
        print(fmt(row))
