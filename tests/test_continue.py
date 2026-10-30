"""Regresní testy příkazu, kterým `/continue` hledá zápis přerušené práce.

Příkaz stojí v `skills/continue/SKILL.md` a skill ho pouští doslova, takže se
testuje vytažený odtamtud, ne jeho opis. Chyba je tichá: prázdný výstup skill
čte jako „navázat není na co“ a přerušená práce zůstane ležet. Hlídá se proto
zápis v `CLAUDE.md` operativního projektu bez gitu – `/break` ho tam píše,
protože `todo.md` takový projekt nemá – i to, že se dál najde zápis v
`docs/todo.md` běžného repozitáře.

Spouští se: python3 -m unittest discover -s tests -q
"""

import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "continue" / "SKILL.md"

BLOCK = "## Přerušený běh\n\n### {}\n\n**Jak pokračovat:** krokem A.\n\n## Další\n\n- Mimo.\n"


def command():
    [cmd] = re.findall(r"```bash\n(.+?)\n```", SKILL.read_text(), re.S)
    return cmd


class FindInterrupted(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.env = dict(
            os.environ,
            GIT_CEILING_DIRECTORIES=self.tmp.name,
            GIT_AUTHOR_NAME="t",
            GIT_AUTHOR_EMAIL="t@t",
            GIT_COMMITTER_NAME="t",
            GIT_COMMITTER_EMAIL="t@t",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def run_in(self, cwd):
        run = subprocess.run(
            ["bash", "-c", command()],
            cwd=cwd,
            capture_output=True,
            text=True,
            env=self.env,
        )
        self.assertEqual(run.returncode, 0, run.stderr)
        return run.stdout

    def test_claude_md_of_operative_project_without_git(self):
        d = self.base / "firma"
        d.mkdir()
        (d / "CLAUDE.md").write_text(
            "# Firma\n\n- **Struktura:** CLAUDE.md\n\n" + BLOCK.format("Smlouvy")
        )
        out = self.run_in(d)
        self.assertRegex(out, r"(?m)^==> .*/firma/CLAUDE\.md$")
        self.assertIn("### Smlouvy", out)
        self.assertNotIn("Mimo.", out)

    def test_todo_in_git_repository_still_found(self):
        d = self.base / "repo"
        (d / "docs").mkdir(parents=True)
        (d / "docs" / "todo.md").write_text("# TODO\n\n" + BLOCK.format("Review"))
        (d / "CLAUDE.md").write_text("# Repo\n\n- **Struktura:** docs/\n")
        subprocess.run(["git", "init", "-q", str(d)], check=True, env=self.env)
        out = self.run_in(d)
        self.assertEqual(out.count("==> "), 1, out)
        self.assertIn("docs/todo.md", out)
        self.assertIn("### Review", out)


if __name__ == "__main__":
    unittest.main()
