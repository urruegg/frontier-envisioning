"""Core demos never enable FinOps implicitly; Preview demos require acknowledgement."""
import contextlib
import io
import tempfile
import unittest
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
    def capture(self, arguments):
        module = load("tools/build_demo.py")
        with tempfile.TemporaryDirectory() as directory, \
                mock.patch.object(module, "load_module", return_value=PreviewGuard), \
                mock.patch.object(module.subprocess, "run", side_effect=StopAtInvocation) as run:
            with self.assertRaises(StopAtInvocation):
                module.main(["--out", str(Path(directory) / "demo"), *arguments])
            return run.call_args.args[0]

    def test_core_command_has_ontology_but_no_finops(self):
        command = self.capture([])
        self.assertIn("--ontology", command)
        self.assertNotIn("--finops", command)
        self.assertNotIn("--acknowledge-finops-preview", command)

    def test_preview_command_forwards_enablement_and_ack(self):
        command = self.capture(["--with-finops-preview", "--acknowledge-finops-preview"])
        self.assertIn("--finops", command)
        self.assertIn("--acknowledge-finops-preview", command)

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
