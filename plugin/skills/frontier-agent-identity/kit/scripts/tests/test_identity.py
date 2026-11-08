# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Unit tests for the identity package: python -m unittest discover -s scripts/tests -v

The stamping tests build a synthetic unpacked solution from the config at run time, so they work for
any customer's names and publisher prefix."""
import base64
import html
import json
import re
import shutil
import struct
import subprocess  # nosec B404 - runs this package's own scripts with the current interpreter
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))
import identity_lib as L  # noqa: E402


def run(*args):
    return subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True)  # nosec B603


def png_size(path: Path):
    head = path.read_bytes()[:24]
    return struct.unpack(">II", head[16:24])


class NamingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg, cls.palette = L.load_config(ROOT)
        cls.prod = L.prod_env(cls.cfg)
        cls.postfixes = [L.env(cls.cfg, e).get("postfix") or e for e in L.nonprod_envs(cls.cfg)]

    def test_display_names_fit_the_limit(self):
        limit = self.cfg["naming"]["maxDisplayLength"]
        for a in self.cfg["agents"]:
            for env, name in a["derived"]["displayName"].items():
                self.assertLessEqual(len(name), limit, f"{a['id']} {env} {name}")

    def test_production_is_clean_and_test_builds_are_marked(self):
        for a in self.cfg["agents"]:
            n = a["derived"]["displayName"]
            for p in self.postfixes:
                self.assertNotRegex(n[self.prod], rf"\b{re.escape(p)}\b", n[self.prod])
            for e in L.nonprod_envs(self.cfg):
                expected = n[self.prod] + " " + (L.env(self.cfg, e).get("postfix") or e) if L.is_scoped(a) else n[self.prod]
                self.assertEqual(n[e], expected)

    def test_technical_names_are_environment_neutral(self):
        words = "|".join(re.escape(w.lower()) for w in self.postfixes + [self.prod])
        for a in self.cfg["agents"]:
            d = a["derived"]
            for key in ("schemaName", "solutionUniqueName", "envVarPrefix", "slug"):
                if d.get(key):
                    self.assertNotRegex(d[key].lower(), rf"(?:^|[_\-])({words})$", f"{a['id']} {key}")

    def test_names_are_unique(self):
        names = [a["derived"]["displayName"][self.prod].lower() for a in self.cfg["agents"]]
        self.assertEqual(len(names), len(set(names)))

    def test_colour_contrast(self):
        for jid, j in self.palette["journeys"].items():
            self.assertGreaterEqual(L.contrast(j["background"], j["glyph"]), 4.5, jid)
        for e in L.nonprod_envs(self.cfg):
            m = self.palette["environments"][e]
            self.assertGreaterEqual(L.contrast(m["band"], m["label"]), 4.5, e)

    def test_validator_passes(self):
        r = run(SCRIPTS / "validate_identity.py", "--root", ROOT)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class IconTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg, cls.palette = L.load_config(ROOT)
        cls.lib = L.load_glyphs(ROOT)

    def test_icon_sizes(self):
        for a in self.cfg["agents"]:
            folder = ROOT / "agents" / a["derived"]["slug"] / "identity"
            self.assertEqual(png_size(folder / "color-192.png"), (192, 192), a["id"])
            self.assertEqual(png_size(folder / "color-32.png"), (32, 32), a["id"])
            self.assertEqual(png_size(folder / "outline-32.png"), (32, 32), a["id"])

    def test_rendering_is_deterministic(self):
        a = self.cfg["agents"][0]
        prod = L.prod_env(self.cfg)
        first = L.icon_png(self.cfg, self.palette, self.lib, a, prod, 192)
        self.assertEqual(first, L.icon_png(self.cfg, self.palette, self.lib, a, prod, 192))
        on_disk = (ROOT / "agents" / a["derived"]["slug"] / "identity" / "color-192.png").read_bytes()
        self.assertEqual(first, on_disk, "icons on disk are out of date - run scripts/build_identity_assets.py")


class StampTests(unittest.TestCase):
    def setUp(self):
        self.cfg, _ = L.load_config(ROOT)
        self.pp = [a for a in self.cfg["agents"] if a["derived"]["schemaName"]]
        if not self.pp:
            self.skipTest("no Copilot Studio agents in the config")
        self.prod = L.prod_env(self.cfg)
        self.nonprod = L.nonprod_envs(self.cfg)
        self.tmp = Path(tempfile.mkdtemp())
        sol = self.tmp / "solution"
        first = self.pp[0]["derived"]
        dev_name = first["displayName"][self.nonprod[0]] if self.nonprod else first["displayName"][self.prod]
        self.bot = self._bot(sol, first["schemaName"], dev_name)
        self.bot2 = None
        if len(self.pp) > 1:
            second = self.pp[1]["derived"]
            manifest = html.escape(json.dumps({"teams": {"colorIcon": "", "outlineIcon": "", "shortDescription": "synthetic test value"}}), quote=False)
            self.bot2 = self._bot(sol, second["schemaName"] + "_x7Q", second["displayName"][self.prod] + " old",
                                  f"<applicationmanifestinformation>{manifest}</applicationmanifestinformation>")
        self._bot(sol, "cr000_LegacyAgent", "Legacy agent")

    def _bot(self, sol, schema, name, extra=""):
        folder = sol / "bots" / schema
        folder.mkdir(parents=True)
        p = folder / "bot.xml"
        p.write_text(f'<bot schemaname="{schema}"><name>{html.escape(name)}</name><iconbase64>AAAA</iconbase64>{extra}</bot>', encoding="utf-8")
        return p

    def tearDown(self):
        shutil.rmtree(getattr(self, "tmp", Path("/nonexistent")), ignore_errors=True)

    def name_of(self, path):
        return html.unescape(re.search(r"<name>(.*?)</name>", path.read_text(encoding="utf-8")).group(1))

    def test_dry_run_changes_nothing(self):
        before = self.bot.read_text(encoding="utf-8")
        r = run(SCRIPTS / "stamp_identity.py", "--env", self.prod, "--solution-dir", self.tmp / "solution", "--root", ROOT)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(before, self.bot.read_text(encoding="utf-8"))
        self.assertIn("would stamp", r.stdout)

    def test_apply_test_then_production(self):
        d = self.pp[0]["derived"]
        if self.nonprod:
            env = self.nonprod[-1]
            r = run(SCRIPTS / "stamp_identity.py", "--env", env, "--solution-dir", self.tmp / "solution", "--root", ROOT, "--apply")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual(self.name_of(self.bot), d["displayName"][env])
            icon = (ROOT / "agents" / d["slug"] / "identity" / f"color-192{L.env_suffix(self.cfg, env)}.png").read_bytes()
            self.assertIn(base64.b64encode(icon).decode(), self.bot.read_text(encoding="utf-8"))
        r = run(SCRIPTS / "stamp_identity.py", "--env", self.prod, "--solution-dir", self.tmp / "solution", "--root", ROOT, "--apply")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.name_of(self.bot), d["displayName"][self.prod])
        if self.bot2:
            self.assertEqual(self.name_of(self.bot2), self.pp[1]["derived"]["displayName"][self.prod])

    def test_manifest_icons_updated_when_present(self):
        if not self.bot2:
            self.skipTest("needs two Copilot Studio agents")
        run(SCRIPTS / "stamp_identity.py", "--env", self.prod, "--solution-dir", self.tmp / "solution", "--root", ROOT, "--apply")
        xml = self.bot2.read_text(encoding="utf-8")
        manifest = json.loads(html.unescape(re.search(r"<applicationmanifestinformation>(.*?)</applicationmanifestinformation>", xml, re.S).group(1)))
        outline = (ROOT / "agents" / self.pp[1]["derived"]["slug"] / "identity" / "outline-32.png").read_bytes()
        self.assertEqual(manifest["teams"]["outlineIcon"], base64.b64encode(outline).decode())
        self.assertEqual(manifest["teams"]["shortDescription"], "synthetic test value")

    def test_strict_fails_on_unknown_agent(self):
        r = run(SCRIPTS / "stamp_identity.py", "--env", self.prod, "--solution-dir", self.tmp / "solution", "--root", ROOT, "--strict")
        self.assertEqual(r.returncode, 2, r.stdout)


if __name__ == "__main__":
    unittest.main()
