# infra

Infrastructure that runs alongside `netagent` but is not part of the Python
package. Currently one thing: **Uptime Kuma**, self-hosted availability
monitoring.

## Nothing with a credential goes in this directory

This repository is public (MIT). `docker-compose.yml` is safe to publish because
Uptime Kuma keeps all of its configuration — monitors, notification tokens, SMTP
passwords — inside its own Docker volume, never in the compose file.

That stops being true the moment someone adds an `environment:` entry with a
token in it. If a service here ever needs a secret, put it in a `.env` file next
to the compose file and add that file to `.gitignore` — do not inline it.

## What this is for, and what it is not

Two layers, deliberately separate:

| | Uptime Kuma | `netagent` |
|---|---|---|
| Question it answers | Is it down **right now**? | What **changed** this week? |
| Cadence | Continuous, 60-second checks | Weekly, run by hand or scheduled |
| Output | An alert while it matters | A dated markdown report |
| Scope | A handful of endpoints you name | The whole local subnet |

They are complementary. Kuma will not tell you a new device appeared on the
network; `netagent inventory` will not tell you the storefront went down at 2am.

`netagent`'s four commands, for reference: `inventory` (subnet scan) → `audit`
(ports/DNS over that inventory) → `connectivity` (loss/latency/jitter) →
`report` (rolls the three into a dated summary). See the top-level README.

## Choosing a host

The machine needs to be **always on** — a monitor that sleeps when you close a
laptop reports outages that did not happen and misses ones that did. Check, in
this order:

1. **Does it stay on and reach the network unattended?** Not "can it be left
   on" — does it survive a power blip and come back without a login.
2. **Does it already run Docker, or can it?** Most NAS units and any Linux box
   can. If installing Docker is a project of its own, that is a signal to pick
   a different host.
3. **Is it on the same network segment as what it watches?** Monitoring the home
   gateway from outside the home tells you about your ISP, not your gateway.
4. **Will you notice if the host itself dies?** Nothing here monitors the
   monitor. See "The external backstop" below.

### If the host is Windows

It works, with a caveat worth knowing before you commit: **Docker Desktop does
not reliably start headless.** It expects a logged-in desktop session, so a
machine that reboots overnight can come back with the monitoring stack down and
nothing to tell you.

Two ways around it, in order of preference:

- Run the container under **WSL2 with systemd enabled** (`systemd=true` in
  `/etc/wsl.conf`), which starts without a desktop session.
- Pick a different host. A cheap always-on Linux box is less work than fighting
  Docker Desktop's startup behaviour indefinitely.

## Running it

```bash
cd infra
docker compose up -d
docker compose ps          # STATUS should reach "healthy" within ~3 minutes
```

Then open `http://<host>:3001` and create the admin account. Do that promptly —
until it exists, anyone who can reach the port can claim it.

The image ships its own healthcheck, so `docker compose ps` reporting `healthy`
means the app is actually answering, not merely that the process is alive. The
first check is deferred three minutes to allow for startup; before that it reads
`starting`, which is not a fault.

## The starting monitor set

Four, in the order they earn their place:

| Monitor | Type | Why |
|---|---|---|
| `https://thestacksbookshop.com` | HTTP(s) | Revenue stops when this does |
| Certificate expiry on that host | HTTP(s), cert notification on | A silent expiry takes the site down with no warning |
| DNS for `thestacksbookshop.com` | DNS | Resolution can fail while the origin is fine |
| Home gateway (its LAN address) | Ping | Separates "my network" from "their service" |

Resist adding more at first. A monitor you have learned to ignore is worse than
no monitor — it trains you to dismiss the notification channel that matters.

## Notifications

Use **Gmail** via SMTP. It is already licensed, needs no new account, and lands
where mail is already read. In Uptime Kuma: Settings → Notifications → SMTP.

Gmail requires an **app password**, not the account password, and 2FA must be on
to create one. That app password lives in Uptime Kuma's volume — it must not end
up in this directory.

Send the test notification before saving. An untested alert path is the same
class of mistake as an untested backup.

## The external backstop

A monitor inside the network cannot tell you the network is down, because the
alert cannot get out. That is not a flaw in this setup, it is a property of
where it runs.

So add **one** external check as well: UptimeRobot's free tier, watching the
storefront only. Two monitors in different failure domains. It costs nothing and
covers the case this stack structurally cannot.

## Upgrading

```bash
docker compose pull && docker compose up -d
```

The pinned tag means this is a deliberate act, not something that happens to
you. Bump the version in `docker-compose.yml`, read the release notes for
breaking changes, then pull. The data volume persists across upgrades.

## Backing it up

The `uptime-kuma-data` volume holds every monitor definition and notification
credential. Rebuilding it by hand is an hour of tedious work and you will forget
one. When the Kopia backup exists, include it:

```bash
docker compose stop
docker run --rm -v uptime-kuma_uptime-kuma-data:/data -v "$PWD":/out \
  alpine tar czf /out/uptime-kuma-data.tgz -C /data .
docker compose start
```

Stopping first matters — Uptime Kuma writes SQLite, and a copy taken mid-write
can restore into a corrupt database.
