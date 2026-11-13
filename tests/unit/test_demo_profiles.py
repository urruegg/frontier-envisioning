"""Core demos never enable FinOps implicitly; Preview demos require acknowledgement."""
import contextlib
import io
import json
import re
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

from tests.unit._util import load


class PreviewDenied(ValueError):
    pass


class PreviewGuard:
    FinOpsPreviewError = PreviewDenied

    @staticmethod
    def require_preview_ack(acknowledged):
        if acknowledged is not True:
            raise PreviewDenied("Grounding and model are not GA; acknowledgement is required.")
        return {"maturity": "preview"}


class StopAtInvocation(Exception):
    pass


class DemoProfiles(unittest.TestCase):
    def capture(self, arguments, *, default_output=False):
        module = load("tools/build_demo.py")
        with tempfile.TemporaryDirectory() as directory, \
                mock.patch.object(module, "load_module", return_value=PreviewGuard), \
                mock.patch.object(module.shutil, "rmtree"), \
                mock.patch.object(module.subprocess, "run", side_effect=StopAtInvocation) as run:
            with self.assertRaises(StopAtInvocation):
                try:
                    module.main([*([] if default_output else ["--out", str(Path(directory) / "demo")]), *arguments])
                except SystemExit as exc:
                    self.fail(f"demo mode was refused before wrapper invocation: {exc.code}")
            return run.call_args.args[0]

    def test_core_command_has_ontology_but_no_finops(self):
        command = self.capture([])
        self.assertIn("--ontology", command)
        self.assertNotIn("--finops", command)
        self.assertNotIn("--agent-finops", command)
        self.assertNotIn("--acknowledge-finops-preview", command)

    def test_preview_command_forwards_enablement_and_ack(self):
        command = self.capture(["--with-finops-preview", "--acknowledge-finops-preview"])
        self.assertIn("--finops", command)
        self.assertIn("--acknowledge-finops-preview", command)

    def test_baseline_command_is_separate_dated_and_keeps_original_core_inputs(self):
        module = load("tools/build_demo.py")
        command = self.capture(["--with-finops-baseline", "--acknowledge-finops-preview"], default_output=True)
        self.assertEqual(Path(command[command.index("--out-dir") + 1]),
                         module.ROOT / "build" / "demo-agent-finops-preview")
        self.assertNotIn("--finops", command)
        self.assertIn("--acknowledge-finops-preview", command)
        for key in ("data", "value", "ontology", "identity-config", "palette"):
            self.assertEqual(command[command.index("--" + key) + 1], str(module.EXAMPLES[key]))
        source = Path(command[command.index("--agent-finops") + 1])
        self.assertEqual(source.name, "caldova-agent-baseline.json")
        authored = json.loads(source.read_text(encoding="utf-8"))
        self.assertEqual(command[command.index("--as-of") + 1], authored["baseline"]["as_of"])

    def test_invalid_baseline_modes_preserve_existing_and_absent_outputs(self):
        module = load("tools/build_demo.py")
        cases = [
            (["--with-finops-baseline"], "not GA"),
            (["--with-finops-baseline", "--with-finops-preview", "--acknowledge-finops-preview"], "not allowed"),
            (["--acknowledge-finops-preview"], "requires"),
        ]
        for flags, message in cases:
            for existing in (False, True):
                with self.subTest(flags=flags, existing=existing), tempfile.TemporaryDirectory() as directory:
                    out = Path(directory) / "demo"
                    if existing:
                        out.mkdir()
                        (out / "keep").write_bytes(b"untouched")
                    text = io.StringIO()
                    with mock.patch.object(module.subprocess, "run") as run, \
                            contextlib.redirect_stdout(text), contextlib.redirect_stderr(text):
                        try:
                            code = module.main(["--out", str(out), *flags])
                        except SystemExit as exc:
                            code = exc.code
                    self.assertEqual(code, 2)
                    self.assertIn(message, text.getvalue())
                    run.assert_not_called()
                    self.assertEqual(list(out.iterdir()) if out.exists() else [], [out / "keep"] if existing else [])
                    if existing:
                        self.assertEqual((out / "keep").read_bytes(), b"untouched")

    def test_core_rejects_unexpected_successor_summary(self):
        module = load("tools/build_demo.py")
        result = subprocess.CompletedProcess([], 0, stdout=json.dumps({"agent_finops": {"records": 1}}), stderr="")
        text = io.StringIO()
        with tempfile.TemporaryDirectory() as directory, \
                mock.patch.object(module.subprocess, "run", return_value=result), contextlib.redirect_stdout(text):
            self.assertEqual(module.main(["--out", str(Path(directory) / "core"), "--no-png"]), 1)
        self.assertIn("core demo unexpectedly produced optional FinOps", text.getvalue())

    def test_baseline_cannot_replace_the_reserved_core_or_legacy_fixture(self):
        module = load("tools/build_demo.py")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for output in (root / "build/demo", root / "build/demo-finops-preview"):
                with self.subTest(output=output):
                    output.mkdir(parents=True)
                    sentinel = output / "keep"
                    sentinel.write_bytes(b"existing fixture")
                    text = io.StringIO()
                    with mock.patch.object(module, "ROOT", root), \
                            mock.patch.object(module, "DEMO_DIR", root / "build/demo"), \
                            mock.patch.object(module.subprocess, "run") as run, contextlib.redirect_stdout(text):
                        code = module.main(["--out", str(output), "--with-finops-baseline",
                                            "--acknowledge-finops-preview"])
                    self.assertEqual(code, 2, text.getvalue())
                    self.assertEqual(sentinel.read_bytes(), b"existing fixture")
                    run.assert_not_called()

    def test_relative_output_from_other_cwd_is_resolved_once(self):
        module = load("tools/build_demo.py")

        def wrapper(command, **kwargs):
            output = Path(command[command.index("--out-dir") + 1])
            if not output.is_absolute():
                output = Path(kwargs["cwd"]) / output
            kit = output / "identity/kit"
            kit.mkdir(parents=True)
            catalogue = kit / "catalog.html"
            catalogue.write_text("<p>fixture</p>", encoding="utf-8")
            archive = output / "identity.zip"
            with zipfile.ZipFile(archive, "w") as package:
                package.writestr("kit/catalog.html", catalogue.read_bytes())
            (output / module.DEMO_HTML_NAME).write_text("<p>baseline fixture</p>", encoding="utf-8")
            return subprocess.CompletedProcess(command, 0, stdout=json.dumps({
                "identity": {"kit": str(kit), "zip": str(archive), "catalogue": str(catalogue),
                             "tests": "passed", "validation": {"errors": []}, "without_identity": []},
            }), stderr="")

        with tempfile.TemporaryDirectory() as directory:
            root, caller = Path(directory) / "repo", Path(directory) / "caller"
            caller.mkdir()
            reserved = [root / "build/demo", root / "build/demo-finops-preview"]
            for path in reserved:
                path.mkdir(parents=True)
                (path / "keep").write_bytes(b"original fixture")
            for relative in ("build/demo", "different-output"):
                with self.subTest(relative=relative):
                    messages = io.StringIO()
                    with contextlib.chdir(caller), mock.patch.object(module, "ROOT", root), \
                            mock.patch.object(module, "DEMO_DIR", reserved[0]), \
                            mock.patch.object(module.subprocess, "run", side_effect=wrapper) as run, \
                            contextlib.redirect_stdout(messages):
                        code = module.main(["--out", relative, "--no-png", "--with-finops-baseline",
                                            "--acknowledge-finops-preview"])
                    self.assertEqual(code, 0, messages.getvalue())
                    output = (caller / relative).resolve()
                    self.assertEqual(run.call_args.args[0][run.call_args.args[0].index("--out-dir") + 1], str(output))
                    self.assertEqual(run.call_args.kwargs["cwd"], root)
                    self.assertEqual(json.loads(messages.getvalue())["out"], str(output))
                    self.assertEqual(json.loads((output / "build-report.json").read_text(encoding="utf-8"))["status"], "built")
                    for path in reserved:
                        self.assertEqual(list(path.iterdir()), [path / "keep"])
                        self.assertEqual((path / "keep").read_bytes(), b"original fixture")

    def test_relative_reserved_output_from_other_cwd_refuses_before_cleanup(self):
        module = load("tools/build_demo.py")
        with tempfile.TemporaryDirectory() as directory:
            root, caller = Path(directory) / "repo", Path(directory) / "caller"
            caller.mkdir()
            reserved = root / "build/demo"
            reserved.mkdir(parents=True)
            (reserved / "keep").write_bytes(b"original fixture")
            with contextlib.chdir(caller), mock.patch.object(module, "ROOT", root), \
                    mock.patch.object(module, "DEMO_DIR", reserved), \
                    mock.patch.object(module.subprocess, "run") as run, contextlib.redirect_stdout(io.StringIO()):
                code = module.main(["--out", "../repo/build/demo", "--no-png", "--with-finops-baseline",
                                    "--acknowledge-finops-preview"])
            self.assertEqual(code, 2)
            run.assert_not_called()
            self.assertEqual(list(reserved.iterdir()), [reserved / "keep"])
            self.assertEqual((reserved / "keep").read_bytes(), b"original fixture")

    def test_real_baseline_fixture_is_a_dated_derivative_not_viewer_consent(self):
        module = load("tools/build_demo.py")
        sources = {p: p.read_bytes() for p in module.EXAMPLES.values()}
        text = io.StringIO()
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(text), contextlib.redirect_stderr(text):
            out = Path(directory) / "baseline"
            try:
                code = module.main(["--out", str(out), "--no-png", "--with-finops-baseline",
                                    "--acknowledge-finops-preview"])
            except SystemExit as exc:
                code = exc.code
            self.assertEqual(code, 0, text.getvalue())
            summary = json.loads((out / "build-report.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["profile"], "agent-finops-preview")
            html = (out / module.DEMO_HTML_NAME).read_text(encoding="utf-8")
            data = json.loads(re.search(r'<script[^>]+id="bp-data"[^>]*>(.*?)</script>', html, re.S)[1])
            self.assertNotIn("finops", data)
            view = data["agent_finops"]
            self.assertEqual(view["schema"], "frontier-agent-finops-view/1.0")
            self.assertEqual(view["as_of"], "2026-11-12")
            self.assertEqual(view["audience"], "internal")
            self.assertIs(view["financial_permission"], False)
            self.assertIn("not GA", view["notice"])
            self.assertEqual(len(view["records"]), 1)
            report = view["records"][0]
            self.assertEqual(report["forecast_kind"], "estimate")
            self.assertFalse(report["handover"]["ready"])
            self.assertEqual(report["scenarios"]["expected"]["annual_recurring"]["amount"], "1320.00")
            self.assertEqual(report["scenarios"]["expected"]["annual_recurring"]["status"], "provisional")
            self.assertNotRegex(json.dumps(view), r'"(?:preview_acknowledged|viewer_acknowledged)"\s*:\s*true')
            self.assertNotRegex(html, r'<(?:script|link)[^>]+(?:src|href)\s*=\s*["\']https?://')
        self.assertEqual(sources, {p: p.read_bytes() for p in sources})

    def test_unacknowledged_preview_fails_without_deleting_output(self):
        module = load("tools/build_demo.py")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "demo"
            output.mkdir()
            existing = output / "good.txt"
            existing.write_text("good", encoding="utf-8")
            messages = io.StringIO()
            with mock.patch.object(module, "load_module", return_value=PreviewGuard), \
                    mock.patch.object(module.subprocess, "run") as run, \
                    contextlib.redirect_stdout(messages), contextlib.redirect_stderr(messages):
                try:
                    code = module.main(["--out", str(output), "--with-finops-preview"])
                except SystemExit as error:
                    code = error.code
            self.assertEqual(code, 2)
            self.assertIn("not GA", messages.getvalue())
            self.assertEqual(existing.read_text(), "good")
            run.assert_not_called()

    def test_core_release_date_step_does_not_require_finops(self):
        module = load("tools/build_demo.py")
        summary = {"value_finops": {"finops": None}, "notes": []}
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(module, "load_module") as run:
            code = module.build_at_release_date(Path(directory), summary, "2026-11-11")
        self.assertEqual(code, 0)
        run.assert_not_called()
