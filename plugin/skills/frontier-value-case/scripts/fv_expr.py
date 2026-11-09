# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Safe formulas for the value case and the FinOps model (shared by frontier-value-case and frontier-finops).

Formulas are arithmetic over named variables: numbers, names, + - * / **, parentheses, min(), max(),
ceil() and floor(). Nothing is executed: the expression is parsed and walked. Variables come from the
assumption register (ids such as ASS-001), from numbers, or from other formulas.
"""
from __future__ import annotations

import ast
import math
import re

_FUNCS = {"min": min, "max": max, "ceil": math.ceil, "floor": math.floor}
ASS_ID = re.compile(r"^ASS-\d{2,4}$")


class MissingInput(Exception):
    """An assumption has no value yet (inputs still to collect)."""

    def __init__(self, ids):
        self.ids = sorted(set(ids))
        super().__init__("no value yet for " + ", ".join(self.ids))


def evaluate(expr, env: dict) -> float:
    if isinstance(expr, bool):
        raise ValueError("booleans are not numbers")
    if isinstance(expr, (int, float)):
        return float(expr)
    return _ev(ast.parse(str(expr), mode="eval").body, env)


def _ev(n, env):
    if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool):
        return float(n.value)
    if isinstance(n, ast.Name):
        if n.id not in env:
            raise KeyError(n.id)
        return float(env[n.id])
    if isinstance(n, ast.BinOp):
        a, b = _ev(n.left, env), _ev(n.right, env)
        if isinstance(n.op, ast.Add):
            return a + b
        if isinstance(n.op, ast.Sub):
            return a - b
        if isinstance(n.op, ast.Mult):
            return a * b
        if isinstance(n.op, ast.Div):
            return a / b if b else 0.0
        if isinstance(n.op, ast.Pow) and abs(b) <= 10:
            return a ** b
    if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.USub, ast.UAdd)):
        v = _ev(n.operand, env)
        return -v if isinstance(n.op, ast.USub) else v
    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in _FUNCS and not n.keywords and n.args:
        return float(_FUNCS[n.func.id](*[_ev(x, env) for x in n.args]))
    raise ValueError("unsupported formula element: " + ast.dump(n)[:80])


def names(expr) -> list[str]:
    if isinstance(expr, (int, float)):
        return []
    return sorted({x.id for x in ast.walk(ast.parse(str(expr), mode="eval")) if isinstance(x, ast.Name)} - set(_FUNCS))


def register_of(*docs) -> dict:
    """One assumption register from several documents (value.json, finops.json); ids must be unique."""
    reg = {}
    for doc in docs:
        for a in (doc or {}).get("assumptions", []) or []:
            if a.get("id") in reg:
                raise ValueError(f"duplicate assumption id {a.get('id')}")
            reg[a["id"]] = a
    return reg


def value_of(a: dict, scenario: str = "base", overrides: dict | None = None) -> float:
    if overrides and a["id"] in overrides:
        return float(overrides[a["id"]])
    v = a.get(scenario)
    if v is None:
        v = a.get("base")
    if v is None:
        raise MissingInput([a["id"]])
    return float(v)


def resolve(spec: dict, register: dict, scenario: str = "base", overrides: dict | None = None,
            var_overrides: dict | None = None) -> dict:
    """Variables -> numbers. A variable is a number, an assumption id or a formula over other variables."""
    env, pending, missing = {}, {}, []
    for name, s in (spec or {}).items():
        if var_overrides and name in var_overrides:
            env[name] = float(var_overrides[name])
        elif isinstance(s, (int, float)) and not isinstance(s, bool):
            env[name] = float(s)
        elif isinstance(s, str) and ASS_ID.match(s):
            if s not in register:
                raise ValueError(f"variable {name} refers to {s}, which is not in the assumption register")
            try:
                env[name] = value_of(register[s], scenario, overrides)
            except MissingInput as exc:
                missing += exc.ids
        else:
            pending[name] = s
    if missing:
        raise MissingInput(missing)
    while pending:
        progressed = False
        for name, s in list(pending.items()):
            try:
                env[name] = evaluate(s, env)
            except KeyError:
                continue
            pending.pop(name)
            progressed = True
        if not progressed:
            raise ValueError("cannot resolve variables: " + ", ".join(sorted(pending)))
    return env


def assumptions_in(spec: dict, register: dict) -> list[str]:
    """Assumption ids a variable set depends on (directly or through formulas)."""
    ids = set()
    for s in (spec or {}).values():
        if isinstance(s, str) and ASS_ID.match(s) and s in register:
            ids.add(s)
    return sorted(ids)
