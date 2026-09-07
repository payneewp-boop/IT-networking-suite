# Environment Reference

Shared context for every skill in `av-it-toolkit`. Read this before recommending
a tool, a script, or a document format.

## Contexts

| Context | What dominates | Review |
|---|---|---|
| Institutional AV (Purdue) | Reliability, standards conformance | Assume others will review and maintain it |
| Home IT | Cost, simplicity | Solo-maintained |
| The Stacks (mobile bookshop) | Cost, simplicity | Solo-maintained |

State which context is assumed whenever it changes the recommendation.

## Available tooling

Already licensed and installed — recommend from this list first:

- Gmail
- Google Sheets / Google Forms / Apps Script
- Excel (incl. Power Query)
- Command Prompt, batch scripts
- PowerShell
- Python
- Notion (system of record — see below)

Do not propose anything requiring a new purchase, subscription, or procurement
approval unless Erik asks for it explicitly. This includes metered Anthropic API
usage: the Agent SDK bills separately from interactive Claude Code, so scheduled
or unattended work must be built from Task Scheduler plus scripts, not from
model calls.

## Design priority order

reliability > simplicity > maintainability > cost > scalability

Simple beats complex: fewer moving parts is *why* a system stays reliable, not a
separate goal. When a simpler approach is materially less capable, present both
and say what is lost.

## System of record

Notion is the system of record for all durable AV documentation. This supersedes
Google Drive. Drive is read-only legacy access — do not write new documentation
there.

### Database map

| Artifact | Destination database |
|---|---|
| Room documentation | Rooms |
| Device records | Devices |
| Config changes | Config records |
| Troubleshooting outcomes | Troubleshooting log |
| Procedures, checklists | SOPs / checklists |

Rooms, Devices, Config records, and Troubleshooting log are related to each
other. Always set the relation when writing. An unrelated page is orphaned and
will not surface on the device or room it concerns — which defeats the reason
for using databases instead of a page tree.

Device labels follow the ROOM-DEVICE-PORT standard. The label is the key
property of the Devices database; never write a device page without it.

### Exception: working state stays on disk

`dev/plan.md`, `dev/context.md`, and `dev/tasks.md` are local files and do not go
to Notion. A local re-read is deterministic and cannot fail mid-session; a Notion
fetch is a network round trip that can.

Rule: if it will matter in six months, it belongs in Notion. If it is scaffolding
for the current task, it stays in `dev/`. Promote durable decisions from
`dev/plan.md` to Notion when a thread wraps up.

### Migration

Do not bulk-migrate from Drive. Move a room's documents when that room is next
worked on, verifying content as it moves. A bulk move would fill the new system
of record with unverified content, which defeats the point of designating one.

## Output expectations

- Documentation artifacts by default: SOPs, troubleshooting logs, signal-flow
  docs, config records, checklists.
- Durable artifacts are written to the Notion database named in the map above,
  not to a loose file. Name the destination when producing one.
- Explain the reasoning behind a recommendation; show options and tradeoffs.
- Do not assume the environment — ask targeted questions when a missing detail
  materially changes the outcome.
- AV work: emphasize signal flow, Dante, troubleshooting method, and system
  design reasoning.

## Skill routing

Overlap exists with installed plugin skills. Prefer:

- `automation-advisor` for "should this be automated, and how" — analysis,
  tool choice, implementation plan, rollback. Advisory output; no durable
  artifact, so nothing is written to Notion.
- `documentation-writer` for producing the artifact itself. Writes to SOPs /
  checklists, or to Rooms for room-level documentation.
- `structured-troubleshooting` for fault diagnosis. Session outcomes are written
  to the Troubleshooting log with the room relation set; a device configuration
  changed during the session also gets a Config records entry.
- `operations:process-doc` for business-process formalization (RACI, flowchart)
  rather than a technical procedure.
- `engineering:documentation` for code/API docs; `documentation-writer` for AV
  and IT operational docs.
- `operations:risk-assessment` for a risk register; `engineering:architecture`
  for a technology-choice ADR.
