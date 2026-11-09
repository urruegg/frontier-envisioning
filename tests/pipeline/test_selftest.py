"""The plugin's end-to-end self-test (slow: about a minute)."""
from __future__ import annotations

import contextlib
import io
import unittest

from tests.unit._util import load


class PluginSelfTest(unittest.TestCase):
    def test_all_checks_pass(self):
        selftest = load("tools/selftest.py", "selftest_p")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = selftest.main()
        self.assertEqual(code, 0, buf.getvalue()[-2000:])
        self.assertIn("ALL PASSED", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
