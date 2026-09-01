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

Do not propose anything requiring a new purchase, subscription, or procurement
approval unless Erik asks for it explicitly.

## Design priority order

reliability > simplicity > maintainability > cost > scalability

Simple beats complex: fewer moving parts is *why* a system stays reliable, not a
separate goal. When a simpler approach is materially less capable, present both
and say what is lost.

## Output expectations

- Documentation artifacts by default: SOPs, troubleshooting logs, signal-flow
  docs, config records, checklists.
- Explain the reasoning behind a recommendation; show options and tradeoffs.
- Do not assume the environment — ask targeted questions when a missing detail
  materially changes the outcome.
- AV work: emphasize signal flow, Dante, troubleshooting method, and system
  design reasoning.

## Skill routing

Overlap exists with installed plugin skills. Prefer:

- `automation-advisor` for "should this be automated, and how" — analysis,
  tool choice, implementation plan, rollback.
- `documentation-writer` for producing the artifact itself.
- `operations:process-doc` for business-process formalization (RACI, flowchart)
  rather than a technical procedure.
- `engineering:documentation` for code/API docs; `documentation-writer` for AV
  and IT operational docs.
- `operations:risk-assessment` for a risk register; `engineering:architecture`
  for a technology-choice ADR.
