"""Building the current version reproduces its release manifest (slow: package and demo build)."""
from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from tests.unit._util import ROOT, load

fe_lib = load("tools/fe_lib.py")
verify_release = load("tools/verify_release.py")


class ReleaseReproduction(unittest.TestCase):
    def test_current_version_reproduces_its_manifest(self):
        manifest_path = ROOT / "releases" / fe_lib.plugin_version() / "manifest.json"
        if not manifest_path.exists():
            self.skipTest("offline retained release evidence unavailable; the online gate resolves publication status")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(load("tools/build_package.py", "bp_r").main(["--dist", str(base / "dist")]), 0)
                self.assertEqual(load("tools/build_demo.py", "bd_r").main(["--out", str(base / "build" / "demo")]), 0,
                                 output.getvalue())
                problems = verify_release.verify(manifest, base=base)
        self.assertEqual(problems, [])


if __name__ == "__main__":
    unittest.main()
