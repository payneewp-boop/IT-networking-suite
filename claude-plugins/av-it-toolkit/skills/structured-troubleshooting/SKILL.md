---
name: structured-troubleshooting
description: >-
  Runs an AV/IT fault to ground by isolating the signal chain stage by stage,
  then writes the outcome to the Notion Troubleshooting log with the room
  relation set, plus a Config records entry when a setting was changed. Use when
  something is broken and the cause is unknown: "no audio in 2145", "the
  projector won't sync", "Dante keeps dropping", "it worked yesterday",
  "intermittent", "it only fails during class", or when a fix is already in and
  the session still needs recording. This diagnoses and logs; documentation-
  writer writes the after-the-fact report and signal-flow-capture inventories a
  room that was never documented.
---

# Structured Troubleshooting

**Before starting, read the bundled environment reference** at
`${CLAUDE_PLUGIN_ROOT}/reference/environment.md` for the tool stack, the context
boundaries, and the Notion database map this skill writes into.

Two failures this exists to prevent: changing several things at once and never
learning which one mattered, and fixing a fault that is then never recorded, so
the next occurrence starts from zero.

## Service first, diagnosis second

Institutional AV has a hard constraint most troubleshooting advice ignores: a
class starts at a fixed time. When service must be restored before the fault is
understood, restore it — then **record that you did**, and what state the system
was left in.

An undocumented workaround is worse than the original fault. It looks like a
fix, so nobody investigates, and it fails again during the next lecture.

## Isolate, do not guess

Bisect the signal chain. Confirm good input and good output at one stage, then
move. The point is to halve the suspect region each test, not to work through
devices in the order you happen to reach them.

**One change at a time.** Two simultaneous changes that resolve a fault teach
nothing — you now have a working room and no cause. If you must batch under time
pressure, say so in the log rather than implying a diagnosis you did not make.

**Reverse every change that did not help**, immediately. Fault-finding leaves
debris — a swapped cable, a bumped gain, a changed input. Debris is the source
of the next intermittent.

## What the fault type tells you

| Symptom | Look first at |
|---|---|
| Dead, never worked | Configuration, routing, or an assumption about the design |
| Worked yesterday | What changed — updates, other people's work, a config push |
| Intermittent | Physical: connectors, thermal, cable strain, contention |
| Fails only under load or in class | Network contention, power sequencing, or someone's actual usage differing from your test |
| Fixed by a restart | Nothing yet. A restart clears a symptom and destroys the evidence |

The last row is the one that gets logged as a resolution when it is not one. If
a reboot fixed it and you do not know why, the log entry says exactly that.

## Dante specifics

Dante fails in ways that look like audio faults and are not:

- **Clock.** Confirm the master and check for contention. A clock fight presents
  as intermittent dropouts on multiple devices at once.
- **Subscription vs. presence.** A device visible on the network with no
  subscription is a healthy device and a dead path.
- **Primary/secondary.** Confirm which network a device is actually on, not
  which one it was intended to be on.
- **Latency and sample rate mismatch** between devices on one flow.

Capture the failing state before changing it. A screenshot of the routing at
fault time is evidence; the same screen after a fix is not.

## Escalation

Escalate when the fix would exceed your authority, when a change would affect
rooms beyond this one, or when the fault is in infrastructure another team owns.
Escalation is not failure — but hand over the isolation you already completed, so
the next person does not repeat it.

## Log the session

Every session ends in the **Troubleshooting log** with the room relation set. An
unrelated entry does not surface on the room it concerns.

If a device configuration was changed, it also gets a **Config records** entry
related to the device — including the value it had *before*, which is what a
rollback needs and what people omit.

Unresolved sessions get logged too. "Not reproduced, three tests run, left in
this state" is a real result and saves the next person those three tests.

Field shapes for both: [references/log-entry.md](references/log-entry.md).

## Done

The session is complete when the fault is resolved or explicitly parked, every
unhelpful change has been reversed, the log entry is written with its relation
set, and any config change has its before-value recorded.

Then state what was actually established versus what is still assumption. A
session that ends "restored service, cause unknown, two candidates ruled out" is
an honest result. One that ends "fixed" without a cause is a fault that will be
back.
