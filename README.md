# netagent

A small set of **local, read-only** command-line agents for monitoring and
securing a home network. Zero cloud dependencies, no accounts, nothing that
runs outside your LAN. Built for a single household network (tested against a
TP-Link Archer AXE5400, but router-agnostic).

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

```bash
cd netagent
python3 -m pip install -e .      # installs the `netagent` command
```

Or run without installing:

```bash
python3 -m netagent <command>
```

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

## Scheduling

### macOS / Linux (cron)

`crontab -e`, then — adjust the path to wherever you cloned this:

```cron
# Weekly inventory + report, Mondays at 08:00
NETAGENT_HOME=/Users/you/.netagent
0 8 * * 1 cd /path/to/netagent && /usr/bin/python3 -m netagent inventory >> "$NETAGENT_HOME/cron.log" 2>&1
5 8 * * 1 cd /path/to/netagent && /usr/bin/python3 -m netagent audit >> "$NETAGENT_HOME/cron.log" 2>&1
10 8 * * 1 cd /path/to/netagent && /usr/bin/python3 -m netagent report >> "$NETAGENT_HOME/cron.log" 2>&1
```

### Windows (Task Scheduler)

Create a weekly task that runs inventory then report (PowerShell):

```powershell
$py  = "python"
$dir = "C:\path\to\netagent"
$env:NETAGENT_HOME = "$env:USERPROFILE\.netagent"

Register-ScheduledTask -TaskName "netagent-weekly" -Trigger (New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 8am) -Action (New-ScheduledTaskAction -Execute $py -Argument "-m netagent inventory" -WorkingDirectory $dir)
```

Run `audit` and `report` as additional actions/tasks the same way. (For a
one-shot equivalent you can also just chain them in a `.bat` file:
`python -m netagent inventory && python -m netagent audit && python -m netagent report`.)

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
├── data/                    # gitignored — scan history + oui.csv
└── reports/                 # gitignored — dated markdown reports
```

## Notes & limitations

- Device discovery relies on the OS ARP table after a ping sweep. Devices that
  don't respond to ping and haven't recently talked to your machine may not
  appear. This is the trade-off for staying privilege-free; it's plenty for a
  weekly "what's on my network" check.
- Assumes a single `/24`-style home subnet by default. Use `--prefix` if yours
  differs.
- Not a replacement for enterprise tooling (nmap, Wireshark) — it's a
  lightweight, safe, glanceable home dashboard.
