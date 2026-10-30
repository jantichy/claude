"""Regresní testy měření kontextu, podle kterého `/autopilot` končí běh.

Skill pracuje bez uživatele, takže hook `handoff.py` – který se ozve jen při
zprávě uživatele – ho na práh neupozorní. Jedinou mezí běhu je skript
`skills/autopilot/context.py`. Oba směry selhání jsou tiché: měření, které
vrátí nulu, nechá běh jet do plného okna; práh, který se rozejde s hookem,
ukončí běh jinde, než slibuje `handoff.md`. A nejde-li změřit vůbec, skript
musí selhat hlučně, jinak by skill běžel bez meze.

Spouští se: python3 -m unittest discover -s tests -q
"""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills" / "autopilot" / "context.py"
HOOK = ROOT / "hooks" / "handoff.py"


def threshold():
    spec = importlib.util.spec_from_file_location("handoff", HOOK)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.CONTEXT_RECOMMEND


class AutopilotContext(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp(prefix="autopilot-test-"))
        self.dir = self.home / ".claude" / "projects" / "-tmp-project"
        self.dir.mkdir(parents=True)
        hooks = self.home / ".claude" / "hooks"
        hooks.mkdir()
        shutil.copy(HOOK, hooks / "handoff.py")

    def tearDown(self):
        shutil.rmtree(self.home, ignore_errors=True)

    def write(self, session, contexts):
        lines = [
            {
                "type": "assistant",
                "message": {
                    "content": [{"type": "tool_use", "name": "Bash"}],
                    "usage": {"input_tokens": 0, "cache_read_input_tokens": c},
                },
            }
            for c in contexts
        ]
        (self.dir / f"{session}.jsonl").write_text(
            "".join(json.dumps(x) + "\n" for x in lines)
        )

    def run_script(self, session):
        env = {**os.environ, "HOME": str(self.home)}
        env.pop("CLAUDE_CODE_SESSION_ID", None)
        if session:
            env["CLAUDE_CODE_SESSION_ID"] = session
        r = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        return r.returncode, json.loads(r.stdout)

    def test_under_threshold_continues(self):
        """Pod prahem skript vrátí poslední naměřený kontext a `over` false."""
        self.write("s1", [50_000, 120_000])
        code, out = self.run_script("s1")
        self.assertEqual(code, 0)
        self.assertEqual(out["context"], 120_000)
        self.assertFalse(out["over"])

    def test_over_threshold_stops(self):
        """Na prahu z `handoff.py` a nad ním skript vrátí `over` true."""
        limit = threshold()
        self.write("s2", [limit - 1, limit])
        code, out = self.run_script("s2")
        self.assertEqual(code, 0)
        self.assertEqual(out["threshold"], limit)
        self.assertTrue(out["over"])

    def test_threshold_is_the_hook_one(self):
        """Práh je týž jako doporučení přerušení v hooku, ne vlastní číslo."""
        self.write("s3", [1])
        _, out = self.run_script("s3")
        self.assertEqual(out["threshold"], threshold())

    def test_missing_session_fails_loudly(self):
        """Bez ID session skript selže, místo aby hlásil nulový kontext."""
        code, out = self.run_script(None)
        self.assertEqual(code, 1)
        self.assertIn("error", out)

    def test_missing_hook_fails_loudly(self):
        """Bez `handoff.py` skript selže – práh i měření se berou odtamtud."""
        self.write("s4", [1])
        (self.home / ".claude" / "hooks" / "handoff.py").unlink()
        code, out = self.run_script("s4")
        self.assertEqual(code, 1)
        self.assertIn("error", out)

    def test_missing_transcript_fails_loudly(self):
        """Neznámá session selže, místo aby hlásila nulový kontext."""
        code, out = self.run_script("neexistuje")
        self.assertEqual(code, 1)
        self.assertIn("error", out)


if __name__ == "__main__":
    unittest.main()
