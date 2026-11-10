# Bounded sticky navigation for the workflow legend

Date: 2026-11-09

Work item: [urruegg/frontier-envisioning#4](https://github.com/urruegg/frontier-envisioning/issues/4).
The user approved the recommended correction. Readiness/approval labels remain
human-only; none is applied by this work.

## Problem and verified cause

On the Agents page at 1440px, scrolling to the workflow makes its legend
intersect the sticky agent list. The legend's centre hits the agent list instead
of the intended control. At 1024px, the existing responsive static positioning
avoids this. Disabling sticky in diagnostic memory also removes the overlap.

The agent list and the full-width workflow currently share a multi-row grid.
The list's sticky containing block therefore extends through the workflow.

## Approved correction

Add an upper grid containing only agent navigation and the selected-agent
summary/trigger canvas. Keep workflow and remaining detail rows as siblings
below that upper containing block. Navigation remains sticky while the summary
is visible, but cannot extend into the workflow row.

Reuse the existing two-column/responsive grid rules. Preserve agent switching,
node controls, full-width workflow, keyboard access, mobile flow and printing.
Do not raise z-index or globally disable sticky as a symptom fix.

## Version and build boundary

Bump to the unreleased patch 1.6.1 before renderer edits. Regenerate the template
and installation inventory through the task runner. Preserve every historical
release record and the archived 1.6.0 product.

Identity-generation inputs do not change. The 1.6.1 preview may explicitly reuse
the guarded original identity raster profile using the 1.6.0 record as provenance
when no 1.6.1 record exists. If a 1.6.1 record does exist, its identity hash is
authoritative and must match. No other future version inherits this preview
permission. All generated-input and asset checks remain mandatory.

This is preview build policy, not publication of a release or creation of
expected release hashes.

## Acceptance

- DOM proves the sticky list is bounded by the upper summary grid, not the
  workflow-containing grid.
- At 1440px after scrolling, legend/header and navigation do not intersect.
- Pointer hit-tests and real clicks reach legend controls, highlight the intended
  node types and leave the selected agent unchanged.
- The upper navigation remains sticky and supports agent switching.
- At 1024px, responsive layout and keyboard activation remain correct.
- Preview raster reuse rejects unsupported versions and any conflicting current
  release record.
- Strict L1 and the browser suite pass; screenshots show the correction.
- Historical records/fixture bytes and server settings are unchanged.

Deliver a separate patch branch and draft PR with evidence. Do not merge,
change protected ownership/guardrails, tag, publish or deploy.
