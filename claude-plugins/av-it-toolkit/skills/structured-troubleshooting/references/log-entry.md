# Log entry shapes

Field detail for the two databases a troubleshooting session writes. Read when
filling the entry; SKILL.md carries the method and the judgment calls.

## Contents

- Troubleshooting log entry
- Config records entry
- Writing the timeline
- What not to record

## Troubleshooting log entry

| Field | What goes in it | Notes |
|---|---|---|
| Title | Symptom as reported, not as diagnosed | "No audio from lectern mic in WALC 2145" |
| Room | Relation | **Required.** An unrelated entry is orphaned |
| Devices | Relation | Every device touched, not only the culprit |
| Reported by | Who raised it | Their description of the symptom is evidence |
| First observed | When it started, if known | "Worked yesterday" is a different fault from "never worked" |
| Symptom | What was observable | Separate from what you concluded |
| Tests run | The isolation sequence, in order | Including the ones that ruled things out |
| Root cause | The mechanism | Empty is honest when unknown. Do not fill it with the fix |
| Resolution | What was actually done | Say if it was a workaround |
| State left in | Only when not fully restored | The field that prevents the next surprise |
| Status | Resolved / Workaround / Not reproduced / Parked / Escalated | |
| Config changed | Relation to Config records | Set when anything was changed |

**Root cause and resolution are different fields and mean different things.**
"Replaced the cable" is a resolution. "Connector strain at the lectern grommet,
from the cable being pulled each time the podium moves" is a cause — and it is
the one that stops the fault recurring in the next room with the same podium.

## Config records entry

Required whenever a setting was changed, even a change that did not fix anything
and was reverted.

| Field | Notes |
|---|---|
| Device | Relation. Use the ROOM-DEVICE-PORT label |
| Room | Relation |
| Setting | What was changed, specifically enough to find again |
| Before | The old value. Omitted more than any other field; needed by every rollback |
| After | The new value |
| Reason | Link to the troubleshooting entry |
| Authorized by | For institutional context, when it is not your own call |

A reverted change still gets an entry. Someone reading the device history needs
to know it was tried and ruled out, or they will try it again.

## Writing the timeline

Order matters more than prose. A numbered sequence of test, expected, observed
lets the next person resume mid-way:

```
1. Lectern mic -> DSP input meter        expect signal    observed: none
2. Swapped to spare mic                  expect signal    observed: none
3. DSP input gain / phantom power        expect 48V on    observed: off
```

Step 3 is the finding. Steps 1 and 2 are why it is trustworthy — without them
the entry is a guess that happened to be right.

## What not to record

- **Credentials of any kind.** Not in the entry, not in a screenshot, not in an
  attached config export. Note that a credential was rotated, never its value.
- **Speculation in the root-cause field.** Put candidates in the tests section
  marked unconfirmed. A guess in a cause field becomes fact within a month.
- **Personal identifying detail about the reporter** beyond who to follow up
  with — the log is a technical record, not an incident file about a person.
