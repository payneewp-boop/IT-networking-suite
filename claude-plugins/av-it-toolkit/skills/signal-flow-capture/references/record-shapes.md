# Record shapes

Field-level detail for the two databases this skill writes. Read when actually
filling records; the SKILL.md body carries the walk order and the judgment calls.

## Contents

- Rooms page
- Devices page
- Signal path table
- Dante capture
- Config records entry
- Fields deliberately left out

## Rooms page

| Field | What goes in it | Notes |
|---|---|---|
| Name | Building + room as the institution writes it | `WALC 2145`. Not the colloquial name. |
| Context | Institutional AV / Home IT / The Stacks | Changes what "good" means; see environment.md |
| Devices | Relation | Set from either side; verify it appears on both |
| Signal paths | The table below | Inline on the page |
| Open questions | Anything unresolved on site | Empty is a claim that nothing was ambiguous |
| Captured | Date of the walk | A record's age is most of its trustworthiness |

## Devices page

| Field | What goes in it | Notes |
|---|---|---|
| Label | `ROOM-DEVICE-PORT` | Key property. Never omit. |
| Physical label | What is actually printed on the box | Only when it differs from the standard |
| Make / Model | As on the nameplate | Not the marketing name |
| Rack position | RU, counted top down | Omit for non-rack devices rather than guessing |
| Room | Relation | Required — an unrelated page is orphaned |
| Network | IP, MAC, VLAN, switch and port | Whatever is observable |
| Role | Source / processing / destination / control | Matches the walk order |
| Unidentified | Checkbox | Set it rather than leaving the page out |

## Signal path table

One row per path, source to destination. A path with an unknown middle is still
a row — mark the gap.

| From | Connector / format | Through | To | Channel |
|---|---|---|---|---|
| Lectern HDMI plate | HDMI | Matrix in 3 | Projector 1 | — |
| Wireless RX A | Dante | DSP ch 5-6 | Ceiling array | 5-6 |

Format is the column that gets skipped and is most often the answer: analog,
AES, Dante, HDMI, HDBaseT, NDI. Say which.

## Dante capture

Device presence is not signal flow. Capture subscriptions, because two devices
on the same network with no subscription between them is a working network and a
dead path — and the records must distinguish those.

| Transmitter | TX channel | Receiver | RX channel | Subscribed |
|---|---|---|---|---|

Also record: sample rate, latency setting, clock master, and whether the device
is on the primary or secondary network. A clock master nobody wrote down is a
recurring outage waiting for a reboot to expose it.

## Config records entry

Only when something was changed during the walk. Relate it to the device *and*
the room.

Capture what was changed, what it was before, why, and who authorized it. The
before-value is the one people omit and the one a rollback needs.

## Fields deliberately left out

- **Serial numbers** — asset management owns these; duplicating them creates a
  second copy that silently disagrees with the first.
- **Firmware versions** — true on the day of capture and stale within a quarter.
  Record it in Config records when a change is made, where it is dated.
- **Photographs as a substitute for fields** — attach them freely, but a photo
  of a rack is not searchable and does not satisfy the label requirement.
