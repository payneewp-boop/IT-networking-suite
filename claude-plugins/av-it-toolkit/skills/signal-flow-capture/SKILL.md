---
name: signal-flow-capture
description: >-
  Turns a single room walkthrough into structured Notion records — one Rooms
  page plus one Devices page per box, each carrying a ROOM-DEVICE-PORT label and
  the room relation, with the signal path captured source to destination. Use
  when walking a room and capturing what is in it: "document this room", "we
  just installed the rack in 2145", "trace the signal path", "what's actually in
  that room", "inventory the devices", "map the Dante flows", or when a
  troubleshooting session turns up a room nobody ever wrote down. This captures
  a room into the databases; documentation-writer writes the prose document and
  structured-troubleshooting diagnoses a fault.
---

# Signal Flow Capture

**Before starting, read the bundled environment reference** at
`${CLAUDE_PLUGIN_ROOT}/reference/environment.md`. It defines the tool stack, the
context boundaries, the design priority order, and the Notion database map this
skill writes into.

Capture is the step that fails silently. A room walked but not recorded looks
identical to a room never visited, and the cost lands months later on whoever is
troubleshooting at 7am before a lecture. This skill exists to make one pass
through a room produce records that survive.

## What this skill is not

| If the job is | Use |
|---|---|
| Producing a readable document from records that exist | `documentation-writer` |
| Diagnosing a fault | `structured-troubleshooting` |
| Deciding whether to script something | `automation-advisor` |
| Capturing a room into Rooms + Devices | this skill |

The boundary matters because the failure is asymmetric. Writing prose when
records were needed leaves the room orphaned in Notion; writing records when
prose was needed just means the document comes next.

## The pass

Walk the room once, in signal order. Do not jump to whatever is most visible —
the rack is the interesting part, and it is also where an unlabelled box hides.

1. **Room identity first.** Building and room number as the institution writes
   them, not as people say them. `WALC 2145`, not "the big Wilmeth room".
2. **Sources** — what originates signal. Lectern input plates, wireless
   receivers, room PC, document camera, guest laptop connections.
3. **Processing** — DSP, matrix, scaler, amplifier. Capture the config that is
   *not* obvious from the front panel; that is the part nobody can re-derive.
4. **Destinations** — displays, projectors, speakers, recording or streaming
   feeds, assistive listening.
5. **Control and network last** — touch panel, control processor, VLAN, switch
   and port. This is last in the walk but first in most faults.

## Every device gets a label

The label is the key property of the Devices database, and a device page without
one is unfindable. `ROOM-DEVICE-PORT`, per the shared standard.

Derive it, do not invent it. If the physical label on the box disagrees with the
standard, record what is on the box **and** flag the mismatch — a silently
"corrected" label means the next technician searches for a string that exists
nowhere in the room.

## Set the relation, always

Every Devices page relates to its Rooms page. This is not bookkeeping. An
unrelated page does not surface on the room it concerns, which removes the only
reason to use databases instead of a page tree.

If a config was changed during the walk, it also gets a Config records entry
related to the same device.

## What needs judgment

These are the calls no template makes for you:

- **Unlabelled or unknown box.** Record it with what is observable — make,
  model, rack position, what is plugged into it — and mark it unidentified.
  A row saying "unknown 1RU device, position 7, two Dante ports" is worth far
  more than a gap.
- **Dante.** Capture subscriptions by flow, not just by device presence. Two
  devices on the same network with no subscription between them is a working
  network and a dead signal path, and the records must be able to tell those
  apart.
- **Ambiguity you cannot resolve on site.** Write it down as a question on the
  room page rather than a guess in a device field. A guess is indistinguishable
  from a measurement once it is in the database.
- **Scope.** One room per pass. A second room is a second walkthrough — batching
  is how detail from the first room gets attributed to the second.

For the field-by-field record shapes and the Dante capture table, see
[references/record-shapes.md](references/record-shapes.md).

## Done

The pass is complete when every device in the room has a page with a label and a
room relation, every signal path runs source to destination with no gap you have
not explicitly marked as unknown, and open questions are written on the room page.

Then say what was created and what remains unresolved. A capture with three
flagged unknowns is a success; a capture that looks complete because the gaps
were smoothed over is the failure this skill exists to prevent.
