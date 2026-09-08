# Documentation Templates

Copy the exact section structure for the document type you're producing. Keep
headings even when a section is short — an empty "Rollback" heading tells the
reader it was considered. Fill every bracket; if a field genuinely doesn't
apply, write "N/A" rather than deleting it.

## Table of contents
- [Generic section set](#generic-section-set)
- [SOP / work instruction](#sop--work-instruction)
- [Runbook](#runbook)
- [Troubleshooting guide](#troubleshooting-guide)
- [Decision tree](#decision-tree)
- [KB article](#kb-article)
- [Incident report](#incident-report)
- [Change record](#change-record)
- [AV documentation set](#av-documentation-set)
- [Revision history block](#revision-history-block)

---

## Generic section set

The default backbone when no specialized template fits:

```
Purpose
Scope
Requirements
Procedure
Verification
Troubleshooting
References
Revision History
```

## SOP / work instruction

```
# [Document Title]

## Purpose
## Scope
## Required Tools
## Prerequisites
## Procedure
1. [Action verb + specific, observable step]
2. ...
## Verification Steps
## Expected Results
## Common Issues
## Troubleshooting
## Escalation Path
## Revision History
```

Rules: numbered, sequential steps; each step starts with an action verb; each
critical step has an observable success condition. Add **⚠ Warning** and
**ℹ Note** callouts inline where a step is risky or easily misread.

## Runbook

For recurring operational tasks (startup, shutdown, maintenance, scheduled jobs):

```
# [Runbook Title]

## When to Run This
## Preconditions / Safety Checks
## Steps
1. ...
## Verification
## Rollback / Abort
## Escalation Path
## Revision History
```

## Troubleshooting guide

```
# [Issue Title]

## Issue Summary
## Symptoms
## Environment
## Impact
## Diagnostic Steps
1. [Test] → [Expected result] → [If not, go to step N / see cause X]
## Test Results
## Root Cause
## Resolution
## Preventive Recommendations
## Lessons Learned
```

Structure diagnostic steps as observations with branches, not a flat list —
each step should narrow the fault. This is signal-flow thinking applied to
writing: isolate the stage, confirm good input, confirm good output, move on.

## Decision tree

Use for fast triage when the path depends on conditions:

```
If [Condition A]:
    → Perform [Action A]

If [Condition B]:
    → Perform [Action B]

If [Condition C]:
    → Escalate to [owner/tier]

Else:
    → [Default action]
```

Keep conditions mutually exclusive and observable. End every branch in an action
or an escalation — never a dead end.

## KB article

Optimized for fast lookup and searchability:

```
# [Title]

**Issue:**
**Symptoms:**
**Cause:**
**Resolution:**
**Prevention:**
**Related Resources:**
**Keywords:** [comma-separated search terms]
```

The goal is fast problem resolution — front-load the fix, keep prose minimal, and
choose keywords a stressed technician would actually search.

## Incident report

```
# Incident Report — [ID / short title]

## Summary
## Timeline
| Time | Event / Action | By |
|------|----------------|----|
## Impact
## Root Cause
## Resolution
## Preventive Actions
## Lessons Learned
## Revision History
```

## Change record

```
# Change Record — [ID / short title]

## What Changed
## Why It Changed
## Approved By
## Risks
## Rollback Procedure
## Validation Steps
## Date / Owner
## Revision History
```

## AV documentation set

Emphasize consistency and maintainability across these. When producing any of
them, capture enough that the room can be rebuilt or handed off cold.

- **Signal-flow document** — source → processing → destination for each path;
  note connector type, format (analog/AES/Dante), and channel. A table or a
  left-to-right diagram both work; label every hop.
- **Rack layout** — RU-by-RU list top to bottom: device, model, U-height, power
  feed, purpose. Include front and rear where cabling matters.
- **Cable-labeling standard** — the naming scheme itself (e.g.
  `SRC-DEST-SIGNAL-##`), plus examples and where labels go on each end.
- **Device inventory** — table: name/hostname, make/model, location, IP/MAC,
  firmware, serial, warranty, owner.
- **Configuration / DSP record** — settings that aren't obvious from the device:
  input gain, routing, presets, DSP blocks, control config, and *why* each
  non-default value was chosen.
- **AV network documentation** — VLANs, switch/port map, Dante vs. control vs.
  management separation, DHCP scopes, and any QoS in play.
- **Room-readiness checklist** — pre-event verification a non-expert can run:
  power, display, audio, mics, source switching, control, network.
- **Commissioning record** — what was installed, tested, the test results, sign-
  off, and handoff notes for the operator.

**Device inventory table skeleton:**

```
| Name | Make/Model | Location | IP / MAC | Firmware | Serial | Owner |
|------|-----------|----------|----------|----------|--------|-------|
```

## Revision history block

Append to any document that will change over time:

```
## Revision History
| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | YYYY-MM-DD | [name] | Initial version |
```
