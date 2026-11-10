# ADR-0023: Digital feedback loop on the Overview, animated in SVG, with official Microsoft names only

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-09 |
| Author | Original author not recorded; Copilot AI-assisted maintenance |
| Status | Proposed |
| Scope | Digital feedback loop decision; document revision, not product version |
| References | [ADR catalogue](README.md), [Product requirements](../prd.md), [Solution design](../solution-design.md) |

**Status:** Proposed (8 November 2026)

## Context
The Overview has to explain the data-driven part of the Frontier hypothesis in the customer's context: which signals exist, which actions agents propose and who approves them, and how outcomes are measured and fed back. An Innovation Hub showcase presented this as an animated loop around Microsoft IQ; it also used layer names that are not Microsoft's. Customers and colleagues must be able to look up every capability the blueprint names.

## Decision
- **Model.** Microsoft's digital feedback loop with its four official areas (Engage customers, Optimize operations, Empower employees, Transform products) around Microsoft IQ with its four official layers (Work IQ, Fabric IQ, Foundry IQ, Web IQ). Per area: signals with their layer, actions with agents and the approving person, outcomes with the journey KPIs and value-case assumptions, a workshop question and a verdict (`loop:<area>`). Data in `feedback_loop`; `canon.py` derives it from the journeys and every build completes it without overwriting; the skill tailors it from Work IQ context and transcripts.
- **Rendering.** One SVG drawn by the renderer; the motion is SVG SMIL (`animateMotion` with key points), not a script timer, so the showcase's Content-Security-Policy needs no change and a hidden tab costs nothing. A button pauses it (`pauseAnimations`), `prefers-reduced-motion` keeps it still, print hides the moving parts; the panel repeats every fact as text.
- **Terminology.** Only official Microsoft names. The canon carries the sources; the build warns about any other "… IQ" name, an unknown layer, area or journey.

## Consequences
The loop is a hypothesis per area and is confirmed in the workshop like agents and use cases. No new product icon is added: the IQ layers use neutral line glyphs, and products keep the existing icons until the official icon sets replace the deck copies (E-02, D-07). A new Microsoft IQ layer means a canon and renderer update with its source.

## Alternatives considered
A static diagram (does not show the flow from signal to outcome); a script-driven animation (timers in the renderer, more code to test, runs while hidden); CSS motion paths (one rule per path, harder to sequence); an embedded video or Lottie file (not self-contained, not data-driven).
