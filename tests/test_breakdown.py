"""Regresní testy skriptu `/breakdown`, který hledá v plánu soubory zakázané v `permissions.deny`.

Obě chyby jsou drahé: propuštěný `credentials.py` zasekne implementaci až
uprostřed, kdy zápis zablokuje harness a přejmenování se musí propsat do plánu
i návrhu; falešný poplach donutí přejmenovat soubor, na který zákaz nemíří.
Testují se proto oba směry.

Spouští se: python3 -m unittest discover -s tests -q
"""

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills" / "breakdown" / "denied.py"

spec = importlib.util.spec_from_file_location("denied", SCRIPT)
denied = importlib.util.module_from_spec(spec)
spec.loader.exec_module(denied)

DENY = [
    "Bash(git clean:*)",
    "Read(//**/.env)",
    "Read(//**/*.key)",
    "Read(//**/.ssh/*)",
    "Edit(//**/*credentials*)",
    "Edit(//**/*secrets*)",
    "Read(secrets.json)",
    "Read(~/notes/*.md)",
    "Read(vault/**)",
]


class DeniedPaths(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name).resolve()
        self.home, self.root = base / "home", base / "proj"
        (self.home / ".claude").mkdir(parents=True)
        (self.root / ".claude").mkdir(parents=True)
        settings = {"permissions": {"deny": DENY}}
        (self.home / ".claude" / "settings.json").write_text(json.dumps(settings))

    def tearDown(self):
        self.tmp.cleanup()

    def hits(self, text):
        return [p for p, _ in denied.denied(text, self.root, self.home)]

    def test_catches_files_the_deny_list_blocks(self):
        plan = (
            "Založ `src/credentials.py`, `tests/test_credentials.py` a `tests/test_secrets.py`; "
            "konfigurace v `.env`, klíč v `certs/api.key`, `deploy/.ssh/config`, `secrets.json` "
            "a `lib/vault/keys.txt`."
        )
        self.assertEqual(
            self.hits(plan),
            [
                "src/credentials.py",
                "tests/test_credentials.py",
                "tests/test_secrets.py",
                ".env",
                "certs/api.key",
                "deploy/.ssh/config",
                "secrets.json",
                "lib/vault/keys.txt",
            ],
        )

    def test_passes_files_no_rule_targets(self):
        plan = (
            "Založ `src/keychain.py`, `tests/test_leaks.py`, `docs/plan.md`, "
            "`src/generated.py` a `.env.example.md`; volá `load()` a `python3 -m unittest`."
        )
        self.assertEqual(self.hits(plan), [])

    def test_writing_plans_path_forms(self):
        """Tvary, kterými `writing-plans` cesty zapisuje: rozsah řádků a závorky."""
        plan = (
            "- Modify: `certs/api.key:3`\n"
            "- Modify: `config/.env:12-30`\n"
            "- Create: `app/(auth)/credentials/page.tsx`\n"
        )
        self.assertEqual(
            self.hits(plan),
            ["certs/api.key", "config/.env", "app/(auth)/credentials/page.tsx"],
        )

    def test_file_under_denied_directory(self):
        self.assertEqual(
            self.hits("Založ `config/secrets/db.yml`."), ["config/secrets/db.yml"]
        )

    def test_write_rule_never_matches(self):
        """Claude Code vzor `Write(…)` přijme, ale nevyhodnotí – zákazem není."""
        user = {"permissions": {"deny": ["Write(//**/*.py)"]}}
        (self.home / ".claude" / "settings.json").write_text(json.dumps(user))
        self.assertEqual(self.hits("Založ `src/app.py`."), [])

    def test_slash_pattern_is_relative_to_its_settings_file(self):
        """`/` v uživatelském nastavení míří do `~/.claude`, v projektovém do projektu."""
        user = {"permissions": {"deny": ["Edit(/generated/**)"]}}
        (self.home / ".claude" / "settings.json").write_text(json.dumps(user))
        self.assertEqual(self.hits("Výstup `generated/model.py`."), [])
        self.assertEqual(
            self.hits("Výstup `~/.claude/generated/model.py`."),
            ["~/.claude/generated/model.py"],
        )
        (self.root / ".claude" / "settings.json").write_text(json.dumps(user))
        self.assertEqual(
            self.hits("Výstup `generated/model.py`."), ["generated/model.py"]
        )

    def test_bare_pattern_stays_inside_project(self):
        self.assertEqual(self.hits("Mimo projekt `~/other/vault/a.txt`."), [])
        self.assertEqual(self.hits("V projektu `a/vault/a.txt`."), ["a/vault/a.txt"])

    def test_dot_dot_is_normalized(self):
        self.assertEqual(
            self.hits("Poznámky v `~/notes/../notes/a.md`."), ["~/notes/../notes/a.md"]
        )

    def test_home_pattern_matches_only_home(self):
        self.assertEqual(
            self.hits("Poznámky v `~/notes/todo.md`."), ["~/notes/todo.md"]
        )
        self.assertEqual(self.hits("Poznámky v `notes/todo.md`."), [])

    def test_project_settings_are_read_too(self):
        local = {"permissions": {"deny": ["Edit(//**/*.pem)"]}}
        (self.root / ".claude" / "settings.local.json").write_text(json.dumps(local))
        self.assertEqual(self.hits("Certifikát `tls/server.pem`."), ["tls/server.pem"])

    def test_broken_settings_file_is_skipped(self):
        (self.root / ".claude" / "settings.json").write_text("{nejde")
        self.assertEqual(self.hits("`src/credentials.py`"), ["src/credentials.py"])


class CommandLine(unittest.TestCase):
    def run_script(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args], capture_output=True, text=True
        )

    def test_missing_plan_exits_2(self):
        self.assertEqual(self.run_script("/nonexistent/plan.md").returncode, 2)

    def test_wrong_arguments_exit_2(self):
        self.assertEqual(self.run_script().returncode, 2)

    def test_clean_plan_exits_0(self):
        with tempfile.TemporaryDirectory() as d:
            plan = Path(d) / "plan.md"
            plan.write_text("Založ `src/keychain.py`.")
            self.assertEqual(self.run_script(str(plan), d).returncode, 0)


if __name__ == "__main__":
    unittest.main()
