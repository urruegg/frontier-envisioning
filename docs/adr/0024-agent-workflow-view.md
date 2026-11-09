# ADR-0024: Agent workflow drawn like the Copilot Studio workflow designer, derived from the plan until authored

**Status:** Proposed (8 November 2026)

## Context
The trigger canvas lists an agent's plan as numbered sentences. Builders and customers think in the Copilot Studio workflow designer (powered by the GitHub Copilot harness): a trigger, typed nodes (Agent, Classify, Extract, Copilot, Human review, Connector, Function, Variable, If/Else, Loop, Note), branches and an outcome. The hypothesis has to show the deterministic workflow around the agent, where AI is used and where people decide, in the same terms the build team uses on Microsoft Learn, before anything is built.

## Decision
- **Model.** `canvas.workflow` per agent: a trigger with the designer's trigger types (Manual, Recurrence, Connector event, When an HTTP request is received, When an agent calls the workflow), ordered steps with the designer's node types (plus Scope and Respond to the agent), branches of If/Else, Classify and Human review that rejoin or end, notes, and the desired outcome.
- **Derived until authored.** `workflow.py` derives a first workflow from the canvas plan by rule (keyword rules per node type; a Human review before the first write when the plan has none), marks it `derived` and re-derives it on every build; an authored workflow is checked, never overwritten. The build warns about unknown node or trigger types, unknown agents, branches on a non-branching node and nested containers.
- **Rendering.** Drawn by the renderer as one SVG on a dark canvas, full width under the trigger canvas: the Add panel as legend and highlighter, a properties panel per node, zoom and fit, an overview that folds the flow into rows and the single designer row. The node glyphs are the plugin's own drawings; Microsoft product icons (agent identity icons, Copilot Studio, Microsoft 365 Copilot, connector systems) come from the existing icon assets only. Nodes are focusable in flow order; print switches to a light canvas.
- **Design.** The solution-design scaffold writes each MVP workflow as the build table of the process design.

## Consequences
The workflow is a hypothesis like the rest of the blueprint: derived ones say so in the bar and are refined in the workshop; the scaffold carries the same structure into the design. AI steps are marked as variable, following Microsoft Learn ("results can vary when actions use AI"). A new designer node or trigger type means a change in `workflow.py`, the renderer and the schema reference, with its Learn source. The view is not a Copilot Studio export: it cannot be imported into the designer, and a later prototype pack can generate one from the same data.

## Alternatives considered
A list of steps only (does not show branches, AI versus deterministic steps or the outcome); a static image per agent (not data-driven, drifts from the canvas); embedding screenshots or Microsoft's own designer icons (not licensed for reuse, not data-driven); a generic flowchart library (external code, does not fit the self-contained HTML); generating real Copilot Studio workflow definitions now (needs a tenant and the solution format; planned with the prototype pack).
