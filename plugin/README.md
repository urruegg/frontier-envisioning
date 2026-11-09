# Frontier Envisioning — plugin for Copilot Cowork

**Version 1.6.0 · Microsoft Innovation Hub Switzerland · 8 November 2026**

Envision any customer as a Frontier company — **human-led, agent-operated**. The plugin gathers what you already know about a customer from your meetings, workshop transcripts, mail, Teams chats and files (Work IQ), turns it into an interactive **Frontier Company Blueprint** that follows the Innovation Hub journey (Part 1 Vision, Part 2 Design, with the Agent Factory, the landing zone, architecture decisions and IT readiness), captures the workshop's verdicts inside that blueprint, writes the PRD, solution design and architecture decisions for the first agents to build, and gives every agent a **brand identity**: names per environment, colours from the customer's own brand and icons in the Microsoft 365 sizes.

---

## Install it in Copilot Cowork (two minutes)

1. **Download** `frontier-envisioning-plugin-1.6.0.zip`. Keep it zipped.
2. **Open Copilot Cowork** and start a new chat.
3. **Attach the zip** to the chat and type:

   > **Install the Frontier PlugIn**

4. **Approve** when Cowork asks to save the skills to your OneDrive (`Documents/Cowork/skills`). Cowork checks the package and confirms the five skills it installed.
5. **Start a new chat** and try one of these:

   > Build the Frontier blueprint demo for Caldova
   >
   > Build the identity kit demo for Caldova
   >
   > Prepare the Frontier envisioning for *your customer*, workshop on *date*

That's all. New chats pick the skills up once OneDrive has synced (usually a minute or two).

| To… | Do this |
|---|---|
| Update to a newer version | Same steps with the newer zip: attach it and say **Install the Frontier PlugIn** |
| Remove the plugin | Say **Delete the frontier skills**, or delete the seven `frontier-…` folders in OneDrive `Documents/Cowork/skills` |
| Roll it out to everyone in your organisation | Give the same zip to your Microsoft 365 admin: it is also a Microsoft 365 app package (see "Organisation roll-out" below) |

---

## What you can ask

| Say | You get |
|---|---|
| "Build the Frontier blueprint demo for Caldova" | The demo blueprint of Caldova Industrial AG, a fictitious company, with its agent identity kit, to see what the plugin produces |
| "Prepare the Frontier envisioning for *customer*, workshop on *date*" | The whole preparation: context pack, blueprint, customer version, workshop agenda and key questions |
| "Gather the customer context for *customer*" | A context pack and an evidence log: every fact with its source (meeting, transcript, mail, chat, file, web) |
| "Analyse the workshop transcript for *customer*" | New evidence from the workshop added to the context pack |
| "Build the Frontier blueprint for *customer*" | `<Customer> Frontier Company Blueprint.html` with the Agent identity page, and `<Customer> - agent identity package v1.0.zip` (a proposal until the customer approves the names; attach a customer deck or template for their colours) |
| "Update the blueprint with the workshop feedback" (attach the exported feedback file) | The next blueprint version with the workshop's verdicts and answers |
| "Make the customer-ready version" | The blueprint without Microsoft-internal sources |
| "Write the PRD and solution design for the *customer* MVP" | PRD, solution design and architecture decision records |
| "Create the agent identity kit for *customer*" | `<Customer> - agent identity package v1.0.zip`: naming convention with DEV/TEST names, one colour per journey from the customer's brand, icons per agent and environment, identity cards, catalogue, and the scripts and pipeline templates for the customer's repository |
| "Build the identity kit demo for Caldova" | The demo identity kit for Caldova's 33 agents, the Agent Factory included (fictitious brand) |
| "Build the value case for *customer*" | Business value in CHF per use case (value tree, NPV, ROI, payback, break-even), shown in the use cases and the matrix, with the assumptions to clarify in the workshop |
| "What will the *customer* agents cost per month?" | The FinOps page: cost per agent (Copilot Credits, licences, Azure, people), purchase options, credit-cost sensitivity and guardrails |
| "Update the value case with the workshop feedback" (attach the exported feedback file) | The workshop's verdicts on the assumptions applied, recalculated, with a change log |
| "Show the agent identity in the blueprint" | The Agent identity page: naming rule, journey colours, DEV/TEST bands, agent family, MVP identity sheet and all names per environment |
| "Prepare the IT readiness and architecture design workshop for *customer*" | The IT readiness page and `it-readiness.md`: preparation items with owners, readiness checks, builder workstation, questions and decisions for IT; the landing zone and the ADRs to decide |
| "Show the digital feedback loop for *customer*" | The Overview's feedback loop: per area (engage customers, optimize operations, empower employees, transform products) the signals with their Microsoft IQ layer, the actions with the agents and who approves, and the outcomes with KPIs and value hypotheses |
| "Show the workflow of the *agent*" | The agent's workflow as in the Copilot Studio workflow designer: the trigger, each step as a designer node (Agent, Classify, Extract, Copilot, Human review, Connector, If/Else, Loop and more), the branches and the desired outcome; derived from the plan until you refine it |
| "Show the Agent Factory for *customer*" | The Agent Factory journey: how every agent moves from hypothesis to validated, designed, ready for build, build, release and operate, with GitHub Copilot, evaluations and human approval |
| "What is next in the *customer* envisioning?" | Where the engagement stands and the next two actions |

**The blueprint** is one HTML file that works offline. Open it in Edge or Chrome (the OneDrive preview does not run it) and use the arrow keys to move through fourteen views along the Innovation Hub journey:

- **Part 1 Vision:** Overview, with the **digital feedback loop** (animated: how the customer's signals become actions with human approval and measured outcomes through Microsoft IQ: Work IQ, Fabric IQ, Foundry IQ, Web IQ) · Org model (human leaders, lead agents and specialist agents, revealed step by step) · Blueprint · Journeys, including the **Agent Factory** (DevSecOps from hypothesis to operate) · **Attendees** (who contributed what)
- **Part 2 Design:** Agents (trigger canvas, the **workflow** from trigger to outcome in the Copilot Studio designer style, seven declarations, role profile, identity) · Agent identity · Target architecture (**landing zone** along CAF, WAF and Responsible AI; layers; flows; **ADRs**) · Use cases (problem statement, business value, feasibility) · **IT readiness** · FinOps
- **Workshop:** Discovery (take notes live) · Roadmap · Evidence

Agent identity icons and Microsoft product icons make each part easy to read. Notes and verdicts stay in your browser until you export them from Discovery; give the exported file back to Cowork to merge.

---

## What is in the package

```
frontier-envisioning-plugin-1.6.0.zip
├── README.md                         this guide
├── MIT.md                            the licence (MIT)
├── THIRD-PARTY-NOTICES.md            Microsoft product icons and other material not covered by MIT
├── manifest.json, color.png, outline.png    Microsoft 365 app package (organisation roll-out)
├── install/
│   ├── plugin-install.json           release file list with checksums
│   └── prepare_install.py            package check and install plan (used by Cowork)
└── skills/
    ├── frontier-envisioning/         runs the engagement end to end
    ├── frontier-context-discovery/   Work IQ and transcripts → cited context pack
    ├── frontier-blueprint/           the blueprint template, demo data, build and merge scripts
    ├── frontier-solution-design/     PRD, solution design and ADRs
    ├── frontier-agent-identity/      agent names, colours and icons: identity kit, renderer, validate and stamp scripts
    ├── frontier-value-case/          business value in CHF: value tree, assumption register, NPV, ROI, workshop merge
    └── frontier-finops/              agent costs in CHF: credits, licences, Azure, people, purchase options, guardrails
```

---

## For Copilot Cowork: how to install this plugin

Follow these steps when a user uploads this zip and asks to install it ("Install the Frontier PlugIn", "install the frontier plugin", "set up this plugin"). Do not score, rewrite or rename the skills: they were validated before release.

1. **Extract** the uploaded zip from `input/` into `working/frontier-plugin/`, keeping the folder structure (Python `zipfile`; do not repack it).
2. **Check** the package and get the plan:
   `python working/frontier-plugin/install/prepare_install.py --root working/frontier-plugin`
   It verifies every file against `install/plugin-install.json` and prints JSON with `verified`, `problems` and, per skill, `source`, `destination`, `files` and `status` (new, update or reinstall). If `verified` is false, stop: tell the user which problem was found and ask them to upload the original zip again.
3. **Install** each skill in the plan into the user's skills folder, one call per skill:
   `CopyArtifact(surface="user", source="working/frontier-plugin/skills/<name>", destination="skills/<name>", recursive=true, overwrite=true)`
   The first call shows the user an approval card. If the user declines, stop and say that nothing was installed.
4. **Confirm the copy**: each result's `copied` count must equal the plan's `files` for that skill. "source folder not visible yet" means the extracted files are still uploading: wait a few seconds and repeat the same call. A short count means the publish is incomplete: repeat the same call (it is idempotent with `overwrite=true`).
5. **Report** in two or three lines: the plugin name and version, the five skills (new or updated), that new chats pick them up once OneDrive has synced (OneDrive folder `Documents/Cowork/skills`), and three prompts to start with: "Build the Frontier blueprint demo for Caldova", "Build the identity kit demo for Caldova" and "Prepare the Frontier envisioning for <customer>".

---

## Organisation roll-out

The same zip is a Microsoft 365 app package (`manifest.json` with five agent skills, colour and outline icons). A Microsoft 365 admin can upload it to the organisation's catalogue. Some catalogues also require builder metadata (`packageMetadata.json` with builder name, environment id, creator id and owners); the admin adds it for their tenant. Validate the package first: in Cowork, attach the zip and say "validate my plugin package".

---

## Data handling

- Cowork works only with your own mailbox, calendar, chats and files, plus content shared with you.
- Every source is marked Microsoft-internal or customer-shareable. The customer-ready version removes internal sources and refuses to build if listed internal terms remain.
- Use real customer data only under an NDA or with the customer's consent. Transcripts are cited with timestamps and short quotes.
- No agent in a blueprint decides about people; such use cases name the person who decides.
- Agent identity colours come from the customer's own brand sources (each with a source); without one, the blueprint colours are used and flagged. Logos are included only where the customer's brand rules allow it.
- Caldova Industrial AG in the demo is fictitious (the same fictitious company as the HR Frontier design sample).

---

## License

MIT License — see `MIT.md`. Copyright (c) 2026 Urs Rüegg. You may use, copy, modify and share the plugin, including for commercial work, as long as the copyright and licence notice stay with it; it comes without warranty. Every script carries an `SPDX-License-Identifier: MIT` header and every skill declares `license: MIT`.

The Microsoft product icons in the blueprint template are Microsoft trademarks and are **not** covered by the MIT licence: use them only in architecture diagrams, training and documentation, unaltered (see `THIRD-PARTY-NOTICES.md`). Microsoft product names are trademarks of Microsoft Corporation. The HAIRO model and the hybrid-organisation blueprint that inspired the org model are Journai's showcase (journai.ch). Caldova Industrial AG is fictitious. Blueprints you build with the plugin contain your customers' information: they are your work products, not part of the licensed software.

---

## For developers

The repository starting point (`frontier-envisioning-github-repo-1.6.0.zip`, to import into GitHub) holds the plugin, the blueprint renderer sources (`src/renderer/`), the tools, the tests and `docs/prd-and-solution-design.md` (PRD and solution design of this plugin). One task runner covers the quality gates: `check` runs the template drift check, lint, the customer-neutrality scan, the unit tests, the self-test (every script end to end against the Caldova examples), the package build, the Caldova demo, the release reproduction and the browser DOM tests; `package` builds this zip and writes `install/plugin-install.json`.

```
python tools/dev.py check
python tools/dev.py package
```

Scripts use the Python standard library only, read their inputs as data and never call the network.
