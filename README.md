# netagent

[![CI](https://github.com/payneewp-boop/IT-networking-suite/actions/workflows/ci.yml/badge.svg)](https://github.com/payneewp-boop/IT-networking-suite/actions/workflows/ci.yml)

A small set of **local, read-only** command-line agents for monitoring and
securing a home network. Zero cloud dependencies, no accounts, nothing that
runs outside your LAN. Built for a single household network (against a
TP-Link Archer AXE5400, but router-agnostic). **Primary target: Windows**;
also runs on macOS and Linux.

Four agents, one CLI:

| Command | What it does |
| --- | --- |
| `netagent inventory` | Scans your subnet, lists every device (IP, MAC, hostname, vendor), saves a timestamped snapshot, and flags **new** devices since the last scan. |
| `netagent audit` | Read-only security checklist over the inventory: local port scan, flags insecure ports (Telnet/FTP/…), and reviews your configured DNS servers. |
| `netagent connectivity` | Pings the gateway + 1.1.1.1 + 8.8.8.8 over time and reports packet loss / latency / jitter. Helps answer "is it my Wi-Fi or my ISP?" |
| `netagent report` | Rolls the latest output of the other three into a dated markdown summary, highlighting only what changed or needs attention. |

## Design & safety

- **Read-only and observational.** It never logs into the router or changes any
  setting. Router security (WPA3, admin password, firmware) is yours to check in
  the admin panel.
- **LAN-only scanning.** Discovery and port scans only touch your own subnet.
  The single exception is `connectivity`, which *pings* (ICMP echo) fixed public
  reliability targets — it never scans or probes them.
- **No elevated privileges.** Everything uses standard OS tools (`ping`, `arp`,
  `ipconfig`/`scutil`) and normal TCP sockets — no raw sockets, no `sudo`.
- **Stdlib only.** No third-party Python packages. Requires Python **3.8+**.
- **Fails gracefully.** If a scan can't run (missing tool, blocked ICMP,
  permission issue) it prints a clear message instead of crashing.

## Install

```bat
cd netagent
python -m pip install -e .       :: installs the `netagent` command
```

Or run without installing:

```bat
python -m netagent <command>
```

(On macOS/Linux use `python3` instead of `python`. After `pip install -e .`
the `netagent` command works the same on every platform.)

All data is written under the current working directory:

- `data/` — timestamped scan snapshots (JSON + CSV) and the one-time MAC vendor
  database. **Gitignored.**
- `reports/` — dated markdown reports. **Gitignored.**

Set `NETAGENT_HOME` to keep this data somewhere fixed regardless of where you
run the command:

```bash
export NETAGENT_HOME="$HOME/.netagent"
```

### MAC vendor database

On its first run, `inventory` downloads the public IEEE OUI list (~4 MB) once
into `data/oui.csv` and uses it locally from then on. If you're offline, vendor
names simply show as blank/`Unknown` and everything else still works.

## Usage

```bash
# 1. Discover devices (run this first — the others build on it)
netagent inventory
netagent inventory --prefix 24 --timeout 800    # tune subnet size / ping timeout

# 2. Security audit over the discovered devices
netagent audit
netagent audit --markdown                        # also writes reports/audit-<date>.md

# 3. Connectivity / reliability check (default 5 minutes)
netagent connectivity
netagent connectivity --duration 120 --interval 1
netagent connectivity --targets 1.1.1.1 9.9.9.9  # gateway is always included

# 4. Weekly summary of everything above
netagent report
```

Typical weekly rhythm: `inventory` → `audit` → `connectivity` → `report`.

### JSON output

Every agent accepts `--json`, which prints its structured result to **stdout**
as JSON while all progress/status text goes to **stderr**. This makes the output
safe to pipe or redirect for scripting:

```bat
netagent inventory --json > scan.json
netagent audit --json | jq ".findings[] | select(.severity==\"FAIL\")"
netagent connectivity --duration 60 --json > link.json
netagent report --json > summary.json
```

(The human-readable tables are still saved to `data/` and `reports/` as usual;
`--json` only changes what's printed to the terminal.)

## Scheduling

### Windows (Task Scheduler)

The simplest reliable approach: put the weekly run in a small batch file, then
point one scheduled task at it. Save this as `run-weekly.bat` in the project
folder (edit the two paths):

```bat
@echo off
set NETAGENT_HOME=%USERPROFILE%\.netagent
cd /d C:\path\to\netagent
python -m netagent inventory
python -m netagent audit
python -m netagent report
```

Register it to run every Monday at 08:00 (PowerShell, one line):

```powershell
Register-ScheduledTask -TaskName "netagent-weekly" `
  -Trigger (New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 8am) `
  -Action  (New-ScheduledTaskAction -Execute "C:\path\to\netagent\run-weekly.bat")
```

Or configure it through the Task Scheduler GUI: **Create Basic Task → Weekly →
Start a program →** `run-weekly.bat`. Run the batch file once by hand first so
the one-time OUI download happens interactively.

### macOS / Linux (cron)

`crontab -e`, then — adjust the path to wherever you cloned this:

```cron
# Weekly inventory + audit + report, Mondays at 08:00
NETAGENT_HOME=/Users/you/.netagent
0 8 * * 1 cd /path/to/netagent && /usr/bin/python3 -m netagent inventory >> "$NETAGENT_HOME/cron.log" 2>&1
5 8 * * 1 cd /path/to/netagent && /usr/bin/python3 -m netagent audit >> "$NETAGENT_HOME/cron.log" 2>&1
10 8 * * 1 cd /path/to/netagent && /usr/bin/python3 -m netagent report >> "$NETAGENT_HOME/cron.log" 2>&1
```

## Tests

A stdlib-only (`unittest`) suite mocks `arp` / `ipconfig` / `route` / `ping`
output, so the parsers are verified across Windows, macOS, and Linux formats
without touching the real system. Run from the project root:

```bat
python -m unittest discover
```

CI runs this suite on every push and pull request across Windows, macOS, and
Linux (and on the minimum supported Python, 3.8) via
[`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## Project layout

```
netagent/
├── pyproject.toml           # console entry point: netagent = netagent.cli:main
├── README.md
├── netagent/
│   ├── cli.py               # argparse, dispatches the four subcommands
│   ├── config.py            # paths, common-ports list, known DNS resolvers
│   ├── net.py               # gateway/subnet detection, ping, ARP, DNS, port scan
│   ├── oui.py               # MAC → vendor lookup (one-time local cache)
│   ├── util.py              # timestamps, JSON/CSV I/O, terminal tables
│   └── agents/
│       ├── inventory.py     # Agent 1
│       ├── audit.py         # Agent 2
│       ├── connectivity.py  # Agent 3
│       └── report.py        # Agent 4
├── tests/                   # unittest suite (mocks arp/ipconfig/route/ping)
├── data/                    # gitignored — scan history + oui.csv
└── reports/                 # gitignored — dated markdown reports
```

## Notes & limitations

- Device discovery relies on the OS ARP table after a ping sweep. Devices that
  don't respond to ping and haven't recently talked to your machine may not
  appear. This is the trade-off for staying privilege-free; it's plenty for a
  weekly "what's on my network" check.
- Assumes a single `/24`-style home subnet by default (it derives the range
  from your IP, not the real netmask). Use `--prefix` if yours differs.
- Parsing assumes an **English-language OS**: it keys off strings like
  "Default Gateway", "DNS Servers", and "time=" in command output. On a
  non-English Windows install those may not match, which shows up as a missing
  gateway/DNS or pings counted as loss. English is the primary supported locale.
- The `audit` DNS check treats anything that isn't your router or a well-known
  public resolver as a **warning**, not a failure — it's often just your ISP's
  DNS handed out by DHCP. Confirm unfamiliar resolvers yourself.
- Historical snapshots in `data/` accumulate over time; prune old
  `inventory-*.json` / `.csv` files if the folder grows.
- Not a replacement for enterprise tooling (nmap, Wireshark) — it's a
  lightweight, safe, glanceable home dashboard.
