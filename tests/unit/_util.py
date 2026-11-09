"""Test helpers: load repository tools and hook scripts by path (they are scripts, not a package)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))


def load(rel: str, name: str | None = None):
    path = ROOT / rel
    spec = importlib.util.spec_from_file_location(name or "t_" + path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
