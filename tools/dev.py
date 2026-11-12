#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Developer task runner for the Frontier Envisioning repository (cross-platform, standard library only).

  python tools/dev.py <command> [<command> ...] [--strict]

Commands
  doctor          tools found on this machine and what each gate needs
  setup           install the development dependencies (pip, npm, Playwright Chromium)
  template        assemble src/renderer into the plugin's blueprint template
  lint            compile all Python, repository rules, ruff and eslint (when installed)
  docs            validate active documentation metadata, local links, catalogues and sprint records
  scan            customer-neutrality scan of the repository (and of dist/ and build/ archives when present)
  test            unit tests (pytest when installed, else unittest); 'test-all' adds the slow pipeline tests
  selftest        the plugin's end-to-end self-test against the Caldova examples
  package         build the plugin package into dist/ (and refresh plugin/install/plugin-install.json)
  demo            build the Caldova demo into build/demo (blueprint, identity kit, catalogue)
  docs-demo       regenerate the tracked offline Caldova HTML and five documentation images
  verify-release  compare dist/ and build/demo with releases/<version>/manifest.json
  dom             core and explicitly acknowledged Preview fixture tests in a headless DOM
  site            assemble the showcase site into build/site (SITE_AUTH_MODE / SITE_AUTH_TENANT_ID)
  serve           serve build/site on http://127.0.0.1:4173 with the hosting headers
  e2e             core and Preview browser tests on an isolated local site (Playwright)
  bundle          the complete release bundle into dist/
  bump X.Y.Z      set a new version everywhere (see tools/bump_version.py)
  precommit       gate L0: template drift, lint, docs, neutrality
  check           gate L1: L0 + test + selftest + package + demo + verify-release + dom + archive scan
  ci              what the L1 workflow runs: check --strict

--strict (and CI=true) turns missing optional tools (ruff, eslint, PyYAML, happy-dom) into failures.
"""
from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fe_lib import BUILD, DEMO_DIR, DEMO_HTML_NAME, DIST, PLUGIN, ROOT, call_main, load_module, run, tracked_files, which  # noqa: E402

TOOLS = ROOT / "tools"
STRICT = False
RESULTS: list[tuple[str, str, float]] = []


class GateFailure(Exception):
    pass


def step(name):
    def deco(fn):
        def wrapper(*a, **k):
            print(f"\n=== {name}", flush=True)
            t0 = time.time()
            try:
                status = fn(*a, **k) or "ok"
            except GateFailure as e:
                RESULTS.append((name, f"FAILED: {e}", time.time() - t0))
                raise
            RESULTS.append((name, status, time.time() - t0))
            return status
        return wrapper
    return deco


def tool(name: str, argv: list[str]) -> int:
    code, out = call_main(load_module(TOOLS / f"{name}.py", f"fe_{name}"), argv)
    print(out.rstrip())
    return code


def optional_missing(what: str, hint: str) -> str:
    if STRICT:
        raise GateFailure(f"{what} is required in strict mode ({hint})")
    print(f"skipped: {what} not installed ({hint})")
    return f"skipped ({what} missing)"


def node_modules(pkg: str) -> bool:
    return (ROOT / "node_modules" / pkg / "package.json").exists()


def npx() -> str | None:
    return which("npx") or which("npx.cmd")


def browser_env() -> dict[str, str]:
    return {"PLAYWRIGHT_BROWSERS_PATH": os.environ.get("PLAYWRIGHT_BROWSERS_PATH") or str(BUILD / "playwright-browsers")}


# --------------------------------------------------------------------------- commands
@step("template drift (src/renderer -> blueprint template)")
def cmd_template_check():
    if tool("assemble_template", ["--check"]):
        raise GateFailure("the blueprint template is not assembled from src/renderer")


def cmd_template():
    return tool("assemble_template", [])


@step("lint")
def cmd_lint():
    bad = []
    for p in tracked_files():
        if p.suffix == ".py":
            try:
                compile(p.read_text(encoding="utf-8"), str(p), "exec", dont_inherit=True)
            except SyntaxError as e:
                bad.append(f"{p.relative_to(ROOT)}:{e.lineno}: {e.msg}")
    for b in bad:
        print("SYNTAX " + b)
    if bad:
        raise GateFailure(f"{len(bad)} Python files do not compile")
    if tool("check_repo", ["--strict"] if STRICT else []):
        raise GateFailure("repository rules")
    notes = []
    ruff = which("ruff")
    if ruff:
        if run([ruff, "check", "."]):
            raise GateFailure("ruff")
    else:
        notes.append(optional_missing("ruff", "pip install -r requirements-dev.txt"))
    if (ROOT / ".agents" / "skills" / "superpowers.lock.json").exists() and tool("superpowers", ["verify"]):
        raise GateFailure("vendored Superpowers skills differ from their lock file")
    if node_modules("eslint") and which("node"):
        if run(["node", str(ROOT / "node_modules" / "eslint" / "bin" / "eslint.js"), "src/renderer", "tests/dom", "tests/e2e"]):
            raise GateFailure("eslint")
    else:
        notes.append(optional_missing("eslint", "npm install"))
    return "; ".join(notes) or "ok"


@step("customer-neutrality scan")
def cmd_scan():
    if tool("neutrality", ["scan"]):
        raise GateFailure("customer names found")
    targets = [str(p) for p in sorted(DIST.glob("*.zip"))] + ([str(BUILD)] if BUILD.exists() else [])
    if targets and tool("neutrality", ["scan", "--zips", *targets]):
        raise GateFailure("customer names found in built artefacts")


@step("documentation metadata, links and traceability")
def cmd_docs():
    if tool("check_docs", ["--strict"] if STRICT else []):
        raise GateFailure("documentation contract")


@step("unit tests")
def cmd_test(include_slow: bool = False):
    folders = ["tests/unit"] + (["tests/pipeline"] if include_slow else [])
    try:
        import pytest  # noqa: F401
        code = run([sys.executable, "-m", "pytest", "-q", *folders])
    except ImportError:
        if STRICT:
            raise GateFailure("pytest is required in strict mode (pip install -r requirements-dev.txt)")
        code = 0
        for f in folders:
            code |= run([sys.executable, "-m", "unittest", "discover", "-s", f, "-t", ".", "-p", "test_*.py"])
    if code:
        raise GateFailure("tests failed")


@step("plugin self-test")
def cmd_selftest():
    if run([sys.executable, "-B", str(TOOLS / "selftest.py")]):
        raise GateFailure("self-test failed")


@step("package")
def cmd_package():
    spec = PLUGIN / "install" / "plugin-install.json"
    before = spec.read_bytes() if spec.exists() else b""
    if tool("build_package", ["--dist", str(DIST)]):
        raise GateFailure("package build")
    if STRICT and spec.read_bytes() != before:
        raise GateFailure("plugin/install/plugin-install.json was stale: run python tools/dev.py package and commit it")


@step("Caldova demo")
def cmd_demo():
    if run([sys.executable, "-B", str(TOOLS / "build_demo.py")]):
        raise GateFailure("demo build")


@step("documentation demo drift")
def cmd_docs_demo_check():
    if tool("build_docs_demo", ["--check", "--demo", str(DEMO_DIR)]):
        raise GateFailure("documentation demo is stale; run python tools/dev.py docs-demo")


def cmd_docs_demo():
    if tool("build_docs_demo", []):
        raise GateFailure("documentation demo generation failed")


@step("release reproduction")
def cmd_verify_release():
    if tool("verify_release", []):
        raise GateFailure("the build does not reproduce the release manifest")


def prepare_preview_fixture() -> Path:
    preview = BUILD / "demo-finops-preview"
    if tool("build_demo", [
        "--out", str(preview), "--with-finops-preview", "--acknowledge-finops-preview",
    ]):
        raise GateFailure("explicit FinOps Preview test fixture failed")
    return preview


@step("DOM tests (happy-dom)")
def cmd_dom():
    if not which("node"):
        return optional_missing("node", "install Node.js 22 or later")
    if not node_modules("happy-dom"):
        return optional_missing("happy-dom", "npm install")
    if not (DEMO_DIR / DEMO_HTML_NAME).exists():
        cmd_demo()
    preview = prepare_preview_fixture()
    files = [str(p.relative_to(ROOT)) for p in sorted((ROOT / "tests" / "dom").glob("*.test.mjs"))]
    if run(["node", "--test", *files], env={
        "BLUEPRINT_HTML": str(DEMO_DIR / DEMO_HTML_NAME),
        "BLUEPRINT_PREVIEW_HTML": str(preview / DEMO_HTML_NAME),
    }):
        raise GateFailure("DOM tests failed")


@step("showcase site")
def cmd_site():
    if not (DEMO_DIR / DEMO_HTML_NAME).exists():
        cmd_demo()
    if tool("build_site", []):
        raise GateFailure("site build")


def cmd_serve():
    return run([sys.executable, "-B", str(TOOLS / "serve_site.py")])


@step("browser tests (Playwright)")
def cmd_e2e():
    if not node_modules("@playwright/test"):
        return optional_missing("@playwright/test", "npm install && npx playwright install chromium")
    if not (DEMO_DIR / DEMO_HTML_NAME).exists():
        cmd_demo()
    preview = prepare_preview_fixture()
    test_site = BUILD / "site-e2e"
    if tool("build_site", [
        "--out", str(test_site), "--preview-demo", str(preview), "--auth", "none",
    ]):
        raise GateFailure("isolated browser-test site build")
    cli = ROOT / "node_modules" / "@playwright" / "test" / "cli.js"
    cmd = ["node", str(cli), "test"] if cli.exists() else [npx() or "npx", "playwright", "test"]
    if run(cmd, env={**browser_env(), "FRONTIER_SITE_DIR": str(test_site)}):
        raise GateFailure("browser tests failed")


@step("release bundle")
def cmd_bundle():
    if tool("build_release", ["--dist", str(DIST)]):
        raise GateFailure("bundle")


def cmd_doctor():
    rows = []

    def probe(cmd):
        try:
            return subprocess.run(cmd, capture_output=True, text=True, timeout=20).stdout.strip().splitlines()[0]
        except (OSError, IndexError, subprocess.SubprocessError):
            return ""
    rows.append(("python", platform.python_version(), "all gates (3.11 or later)"))
    rows.append(("node", probe(["node", "-e", "process.stdout.write(process.version)"]) if which("node") else "", "DOM and browser tests (22 or later)"))
    for name, need in [("git", "everything"), ("gh", "bootstrap, issues, releases"), ("az", "Bicep build, Azure login"),
                       ("azd", "showcase provisioning and deployment"), ("ruff", "Python lint (L0)"), ("copilot", "Copilot CLI with Superpowers")]:
        rows.append((name, "found" if which(name) else "", need))
    for mod, need in [("pytest", "test runner (L1)"), ("yaml", "YAML validation (L0)")]:
        try:
            __import__(mod)
            rows.append((mod, "found", need))
        except ImportError:
            rows.append((mod, "", need))
    for pkg, need in [("happy-dom", "DOM tests (L1)"), ("eslint", "renderer lint (L0)"), ("@playwright/test", "browser tests (L2)")]:
        rows.append((pkg, "found" if node_modules(pkg) else "", need))
    sp = ROOT / ".agents" / "skills" / "superpowers.lock.json"
    home = Path(os.environ.get("COPILOT_HOME") or Path.home() / ".copilot") / "skills" / "brainstorming"
    rows.append(("superpowers", "vendored" if sp.exists() else ("personal" if home.exists() else ""), "engineering method (see docs)"))
    w = max(len(r[0]) for r in rows)
    for name, status, need in rows:
        print(f"{name:<{w}}  {status or 'MISSING':<22}  {need}")
    return 0


def cmd_setup():
    code = run([sys.executable, "-m", "pip", "install", "-r", "requirements-dev.txt"])
    npm = which("npm") or which("npm.cmd")
    if npm:
        code |= run([npm, "ci" if (ROOT / "package-lock.json").exists() else "install", "--no-audit", "--no-fund"])
        args = ["playwright", "install", "chromium"] + (["--with-deps"] if platform.system() == "Linux" and os.environ.get("CI") else [])
        code |= run([npx() or "npx", *args], env=browser_env())
    else:
        print("npm not found: install Node.js 22 or later for the DOM and browser tests")
    return code


def summary() -> None:
    print("\n=== summary")
    for name, status, secs in RESULTS:
        print(f"{status[:60]:<60}  {secs:6.1f}s  {name}")


def main(argv=None) -> int:
    global STRICT
    argv = list(sys.argv[1:] if argv is None else argv)
    STRICT = "--strict" in argv or os.environ.get("CI", "").lower() == "true"
    argv = [a for a in argv if a != "--strict"]
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(__doc__)
        return 0
    if argv[0] == "bump":
        return tool("bump_version", argv[1:])
    simple = {"doctor": cmd_doctor, "setup": cmd_setup, "template": cmd_template, "serve": cmd_serve}
    gated = {"lint": cmd_lint, "docs": cmd_docs, "scan": cmd_scan, "test": cmd_test, "test-all": lambda: cmd_test(True),
             "selftest": cmd_selftest, "package": cmd_package, "demo": cmd_demo, "verify-release": cmd_verify_release,
             "dom": cmd_dom, "site": cmd_site, "e2e": cmd_e2e, "bundle": cmd_bundle, "docs-demo": cmd_docs_demo,
             "precommit": lambda: [cmd_template_check(), cmd_lint(), cmd_docs(), cmd_scan()],
             "check": lambda: [cmd_template_check(), cmd_lint(), cmd_docs(), cmd_scan(), cmd_test(include_slow=True), cmd_selftest(), cmd_package(),
                               cmd_demo(), cmd_docs_demo_check(), cmd_verify_release(), cmd_dom(), cmd_scan()]}
    if argv[0] == "ci":
        STRICT = True
        argv = ["check"]
    code = 0
    try:
        for cmd in argv:
            if cmd in simple:
                code |= int(simple[cmd]() or 0)
            elif cmd in gated:
                gated[cmd]()
            else:
                print(f"unknown command {cmd!r}\n")
                print(__doc__)
                return 2
    except GateFailure as e:
        summary()
        print(f"\nGATE FAILED: {e}")
        return 1
    if RESULTS:
        summary()
        print("\nALL GATES PASSED" if not code else "")
    return code


if __name__ == "__main__":
    sys.exit(main())
