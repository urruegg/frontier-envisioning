# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Agent workflows for the blueprint: the canvas plan as a Copilot Studio workflow (GitHub Copilot harness).

A workflow starts with one trigger, runs typed steps and ends in the desired outcome. The step types are the
nodes of the Copilot Studio workflow designer: Agent, Classify, Extract, Copilot, Human review, Connector,
Function, Variable, If/Else, Loop (and Scope), plus Note for annotations.

  * clean_workflow(wf, agent_refs, rep, who) checks an authored `canvas.workflow` and gives every node an id
  * derive_workflow(agent) proposes a workflow from `canvas.trigger`, `canvas.plan`, `canvas.approval`,
    `canvas.connectors` and `canvas.outcome` (a hypothesis, marked "derived": true)
  * fill_workflows(bp, rep) does both for every agent of the blueprint (used by build_blueprint.py)
Standard library only.
"""
from __future__ import annotations

import re

NODE_TYPES = {
    "agent": ("Agent", "ai"), "classify": ("Classify", "ai"), "extract": ("Extract", "ai"), "copilot": ("Copilot", "ai"),
    "human_review": ("Human review", "human"), "connector": ("Connector", "rule"), "function": ("Function", "rule"),
    "variable": ("Variable", "rule"), "if_else": ("If/Else", "rule"), "loop": ("Loop", "rule"), "scope": ("Scope", "rule"),
    "note": ("Note", "note"), "respond": ("Respond to the agent", "rule"),
}
TRIGGERS = {"manual": "Manual", "recurrence": "Recurrence", "connector": "Connector event",
            "http": "When an HTTP request is received", "agent": "When an agent calls the workflow"}
ALIASES = {"if": "if_else", "ifelse": "if_else", "if/else": "if_else", "if-else": "if_else", "condition": "if_else",
           "human": "human_review", "human review": "human_review", "approval": "human_review", "review": "human_review",
           "request for information": "human_review", "action": "connector", "foreach": "loop", "for each": "loop",
           "group": "scope", "fx": "function", "ai": "agent", "respond to the agent": "respond", "response": "respond"}
TRIGGER_ALIASES = {"schedule": "recurrence", "scheduled": "recurrence", "event": "connector", "automated": "connector",
                   "webhook": "http", "request": "http", "agent calls": "agent", "tool": "agent", "on demand": "manual"}
BRANCHING = ("if_else", "classify", "human_review")
CONTAINERS = ("loop", "scope")

# plan sentence -> node type (first match wins; the default is an Agent step)
RULES = [
    ("connector", r"(write-back|write back|hand .{0,40}? to the workflow|post (a|an|the) |create (a|an|the) (record|row|requisition|ticket|order|case)"
                  r"|update (a|an|the) (record|row|status|work order))"),
    ("human_review", r"\b(approves?|approved by|approval by|confirms?|for confirmation|signs? off|sign-off|asks? the|request (information|details)"
                     r"|collect missing|missing details|takes over)\b"),
    ("loop", r"\b(for each|each (item|line|attachment|file|document|row|invoice|part)|every (item|line|attachment)|repeat)\b"),
    ("classify", r"\b(classif\w*|categori[sz]\w*|triage|route|routing|the channel|which channel|intent)\b"),
    ("extract", r"\b(extract\w*|parse|scan|ocr|transcrib\w*|read the (document|invoice|pdf|form|attachment|contract|delivery note))\b"),
    ("if_else", r"(^(if|when|check (whether|if))\b)|\b(flag\w*|validate|verify|threshold|exceed\w*|outside (the )?(guideline|tolerance|limit)s?)\b"),
    ("function", r"\b(calculat\w*|comput\w*|reconcil\w*|match\w* .{0,60}? against|compare|transform|convert|score)\b"),
    ("variable", r"\b(initiali[sz]e|set the|store|remember)\b"),
    ("copilot", r"\b(research\w*|analy[sz]\w*|summari[sz]\w*|cowork)\b"),
    ("connector", r"\b(send|post|notify|create|update|write|submit|record|log|e-?mail|report status|report .{0,20}? back|get|look up|lookup|fetch|retrieve"
                  r"|read|search|find|check (the )?(catalogues?|catalogs?|contracts?|stock|availability))\b"),
]
TRIGGER_RULES = [
    ("recurrence", r"\b(daily|weekly|monthly|nightly|hourly|every (day|week|month|morning|night)|schedule\w*|calendar day|month-end|period end)\b"),
    ("http", r"\b(webhook|http|api call)\b"),
    ("manual", r"\b(manual\w*|on demand|button)\b"),
    ("agent", r"\b(asks?|describes?|chat\w*|conversation|question|microsoft 365 copilot|copilot chat)\b"),
]
WRITE = re.compile(r"\b(write|create|update|send|submit|post|hand|file|book|pay|order)\w*", re.I)
STOP = {"the", "and", "for", "with", "from", "into", "that", "this", "each", "every", "their", "them", "then", "when", "after",
        "before", "back", "agent", "agents", "workflow", "declared", "action", "actions", "held", "card", "confirmation",
        "confirm", "confirms", "draft", "report"}


def as_list(x):
    if x is None or x == "":
        return []
    return x if isinstance(x, list) else [x]


def node_type(t) -> str | None:
    k = str(t or "").strip().lower()
    k = ALIASES.get(k, k).replace(" ", "_").replace("/", "_").replace("-", "_")
    k = ALIASES.get(k, k)
    return k if k in NODE_TYPES else None


def trigger_type(t) -> str | None:
    k = str(t or "").strip().lower()
    k = TRIGGER_ALIASES.get(k, k)
    return k if k in TRIGGERS else None


def classify_step(text: str) -> str:
    for kind, pat in RULES:
        if re.search(pat, text, re.I):
            return kind
    return "agent"


def classify_trigger(text: str) -> str:
    for kind, pat in TRIGGER_RULES:
        if re.search(pat, text, re.I):
            return kind
    return "connector"


def _words(s) -> set:
    return {w for w in re.findall(r"[a-z0-9]{4,}", str(s or "").lower()) if w not in STOP}


def _best(text, pool):
    """The pool entry that shares the most significant words with the text (or None)."""
    tw, best, score = _words(text), None, 0
    for p in pool:
        n = len(tw & _words(p))
        if n > score:
            best, score = p, n
    return best


def _label(text: str) -> str:
    head = text.split(":", 1)[0].strip()
    return head if ":" in text and 1 < len(head.split()) <= 7 else text.strip()


def _categories(text: str) -> list:
    if ":" not in text:
        return []
    tail = text.split(":", 1)[1]
    parts = [p.strip(" .") for p in re.split(r",\s*|\s+or\s+|\s+and\s+", tail) if p.strip(" .")]
    return [p[:1].upper() + p[1:] for p in parts][:5] if 2 <= len(parts) <= 6 else []


def derive_workflow(a: dict) -> dict | None:
    """A first workflow from the agent's canvas: trigger, one node per plan step, an approval before the first write, the outcome."""
    c = a.get("canvas") if isinstance(a.get("canvas"), dict) else {}
    plan = [str(p).strip() for p in as_list(c.get("plan")) if str(p).strip()]
    if not plan:
        return None
    trig = next((str(t) for t in as_list(c.get("trigger") or a.get("trigger")) if str(t).strip()), "")
    connectors = [str(x) for x in as_list(c.get("connectors") or c.get("tools"))]
    approvals = [str(x) for x in as_list(c.get("approval"))]
    me = a.get("id") or a.get("name")
    steps = []
    for p in plan:
        kind = classify_step(p)
        st = {"type": kind, "label": _label(p), "detail": p}
        if kind == "agent":
            st["agent"] = me
        if kind in ("connector", "human_review", "extract"):
            sysn = _best(p, connectors)
            if sysn:
                st["system"] = sysn
        if kind == "human_review":
            ap = _best(p, approvals)
            if ap:
                st["approver"] = ap
        if kind == "classify":
            cats = _categories(p)
            if cats:
                st["defaults"] = cats
        if kind == "if_else":
            st["defaults"] = ["Yes", "No"]
        steps.append(st)
    if approvals and not any(s["type"] == "human_review" for s in steps):
        at = next((i for i, s in enumerate(steps) if s["type"] == "connector" and WRITE.search(s["detail"])), len(steps))
        steps.insert(at, {"type": "human_review", "label": _label(approvals[0]), "detail": approvals[0], "approver": approvals[0]})
    short = re.sub(r"\s+Agent$", "", str(a.get("name") or "Agent"))
    wf = {"name": f"{short} workflow", "status": "draft", "derived": True,
          "trigger": {"type": classify_trigger(trig) if trig else "manual", "label": trig or TRIGGERS["manual"], "detail": trig},
          "steps": steps, "outcome": str(c.get("outcome") or a.get("outcome") or "")}
    if not wf["trigger"]["detail"]:
        wf["trigger"].pop("detail")
    return wf


def _ids(wf: dict) -> None:
    n = [0]

    def walk(steps):
        for s in steps:
            if not isinstance(s, dict):
                continue
            n[0] += 1
            s.setdefault("id", f"n{n[0]}")
            walk(as_list(s.get("steps")) if s.get("type") in CONTAINERS else [])
            for b in as_list(s.get("branches")):
                if isinstance(b, dict):
                    walk(as_list(b.get("steps")))
    walk(as_list(wf.get("steps")))


def clean_workflow(wf: dict, refs: set, rep, who: str) -> dict | None:
    """Check an authored workflow; unknown node and trigger types fall back with a warning."""
    if not isinstance(wf, dict):
        rep.warn(f"{who}: canvas.workflow must be an object; ignored")
        return None
    tr = wf.get("trigger")
    if isinstance(tr, str):
        tr = {"label": tr}
    if not isinstance(tr, dict):
        tr = {}
    tt = trigger_type(tr.get("type"))
    if tr.get("type") and not tt:
        rep.warn(f"{who}: workflow trigger type {tr.get('type')!r} unknown (use {', '.join(TRIGGERS)}); treated as a connector event")
    tr["type"] = tt or classify_trigger(str(tr.get("label") or ""))
    tr.setdefault("label", TRIGGERS[tr["type"]])
    wf["trigger"] = tr

    def check(steps, where, depth):
        out = []
        for s in as_list(steps):
            if isinstance(s, str):
                s = {"label": s}
            if not isinstance(s, dict):
                continue
            k = node_type(s.get("type")) if s.get("type") else None
            if s.get("type") and not k:
                rep.warn(f"{who}: workflow node type {s.get('type')!r} unknown (use {', '.join(NODE_TYPES)}); shown as an Agent step")
            s["type"] = k or classify_step(str(s.get("label") or s.get("detail") or ""))
            if not s.get("label"):
                s["label"] = NODE_TYPES[s["type"]][0]
            if s.get("agent") and str(s["agent"]) not in refs:
                rep.warn(f"{who}: workflow step {s['label'][:40]!r} names an unknown agent {s['agent']!r}")
            if s["type"] in CONTAINERS:
                if depth > 1:
                    rep.warn(f"{who}: a {s['type']} inside a {where} is drawn flat")
                s["steps"] = check(s.get("steps"), s["type"], depth + 1)
            if s.get("branches") is not None:
                if s["type"] not in BRANCHING:
                    rep.warn(f"{who}: branches on a {NODE_TYPES[s['type']][0]} node are ignored (If/Else, Classify and Human review branch)")
                    s.pop("branches")
                else:
                    bs = []
                    for b in as_list(s.get("branches")):
                        if isinstance(b, str):
                            b = {"label": b}
                        if not isinstance(b, dict) or not b.get("label"):
                            continue
                        b["steps"] = check(b.get("steps"), "branch", depth + 1)
                        if b.get("then") not in (None, "continue", "end"):
                            rep.warn(f"{who}: branch {b['label']!r} then must be continue or end")
                            b["then"] = "continue"
                        bs.append(b)
                    s["branches"] = bs
            if s.get("defaults") is not None:
                s["defaults"] = [str(x) for x in as_list(s.get("defaults"))]
            out.append(s)
        return out
    wf["steps"] = check(wf.get("steps"), "workflow", 0)
    if not wf["steps"]:
        rep.warn(f"{who}: workflow has no steps")
    _ids(wf)
    return wf


def fill_workflows(bp: dict, rep) -> dict:
    """Check every authored workflow and derive one for every agent with a plan but no workflow."""
    agents = []
    for d in as_list(bp.get("domains")):
        if isinstance(d, dict):
            agents += [a for a in ([d.get("orchestrator")] + as_list(d.get("agents"))) if isinstance(a, dict)]
    refs = {str(a.get(k)) for a in agents for k in ("id", "name") if a.get(k)}
    out = {"authored": 0, "derived": 0, "nodes": 0}
    for a in agents:
        c = a.get("canvas")
        if not isinstance(c, dict):
            continue
        who = f"agent {a.get('id') or a.get('name')}"
        wf0 = c.get("workflow")
        if "workflow" in c and not (isinstance(wf0, dict) and wf0.get("derived")):
            wf = clean_workflow(wf0, refs, rep, who)
            if wf is None:
                c.pop("workflow")
                continue
            out["authored"] += 1
        else:
            wf = derive_workflow(a)
            if wf is None:
                c.pop("workflow", None)
                continue
            _ids(wf)
            c["workflow"] = wf
            out["derived"] += 1
        out["nodes"] += _count(c["workflow"]["steps"])
    return out


def _count(steps) -> int:
    n = 0
    for s in as_list(steps):
        if isinstance(s, dict):
            n += 1 + _count(s.get("steps") if s.get("type") in CONTAINERS else []) + sum(_count(b.get("steps")) for b in as_list(s.get("branches")) if isinstance(b, dict))
    return n
