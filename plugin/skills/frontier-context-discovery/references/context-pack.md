# Context pack schema (frontier-context/1.0)

The context pack is a single JSON file. It is the only input the blueprint seed reads, so everything the hypothesis rests on must be in it, cited.

```json
{
 "schema": "frontier-context/1.0",
 "customer": {"name": "", "short": "", "industry": "", "hq": "", "size": "", "languages": [], "src": []},
 "engagement": {"title": "", "scope": "enterprise | function", "function": "", "workshop_date": "", "location": "", "objectives": []},
 "sources": [],
 "facts": [],
 "stakeholders": [],
 "journeys": [],
 "systems": [],
 "kpis": [],
 "constraints": [],
 "ideas": [],
 "decisions": [],
 "actions": [],
 "open_questions": []
}
```

## sources (the evidence register)

| Field | Required | Meaning |
|---|---|---|
| id | yes | E01, E02 … allocated once, never reused |
| type | yes | transcript, meeting, email, chat, file, web, crm, note, workshop |
| title | yes | Meeting subject, email subject, file name or page title |
| date | yes | YYYY-MM-DD |
| source | no | Teams meeting transcript, Outlook, SharePoint, public website … |
| participants | no | Roles (and names for attendees) |
| visibility | yes | `customer` or `internal` (see the playbook) |
| summary | no | Two sentences in your own words |
| quote | no | One short, representative quote (at most 20 words) |

## facts

| Field | Required | Meaning |
|---|---|---|
| id | yes | F001 … |
| category | yes | strategy, pain, metric, kpi, system, data, governance, constraint, stakeholder, idea, decision, action, risk, other |
| statement | yes | One sentence, your words, specific |
| journey | no | Name of the journey it belongs to (must match `journeys[].name`) |
| evidence | yes | `[{"source": "E05", "at": "00:12:31", "quote": "…"}]` |
| confidence | no | high (stated by the owner), medium (second-hand or estimate), low (inferred) |
| visibility | no | inherits the strictest visibility of its sources |

## journeys

`{"name": "Service", "journey_name": "Request-to-Resolution journey", "function": "Field service", "why": "Largest growth lever", "stages": ["Detect & request", "Diagnose", "…"], "leader_role": "Head of Service Operations", "src": ["E05"]}`

3 to 6 journeys for a whole company, 3 to 5 inside one function. Stage names are optional at this point; the blueprint skill completes them.

## stakeholders

`{"name": "", "role": "CIO", "org": "customer | microsoft | partner", "stance": "sponsor | champion | neutral | sceptic", "interests": "", "src": []}`

Roles first. Names only for people who attended or wrote. Interests and stance relate to the initiative, never to personal performance.

## systems, kpis, constraints, ideas, decisions, actions

| List | Shape |
|---|---|
| systems | `{"name": "SAP S/4HANA", "role": "ERP", "journey": "", "notes": "", "src": []}` (no journey = shared by all) |
| kpis | `{"kpi": "", "definition": "", "baseline": "", "target": "", "journey": "", "src": []}` |
| constraints | `{"text": "", "type": "data residency | NDA | works council | licensing | security | regulation", "src": []}` |
| ideas | `{"name": "", "journey": "", "who": "", "src": []}` (ideas the customer or Microsoft already named) |
| decisions | `{"text": "", "date": "", "src": []}` |
| actions | `{"text": "", "owner": "", "due": "", "src": []}` |

## open_questions

`{"q": "", "journey": "", "category": "Business & process | Data | Systems & integration | Governance & risk | Value & KPIs | Adoption & change", "why": ""}`

They become the discovery questions in the blueprint, where the workshop answers them.

## Quality bar

- `context_pack.py validate` returns no errors.
- Every journey has at least one evidenced pain and one number, or the gap is an open question.
- At least one transcript or workshop source; otherwise say the hypothesis rests on secondary material.
