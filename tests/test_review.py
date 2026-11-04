"""Testy kopie projektu, nad kterou pracují ověřovatelé `/review`.

Kopie je jediná hranice mezi ověřovatelem a staršími nálezy: zákaz v zadání
nedržel. Rozbitá hranice mlčí – ověřovatel prostě čte, co číst nemá, a nikdo
to nepozná. Testuje se proto oba směry: co zmizet má, zmizí, a co k ověření
patří, v kopii zůstane beze změny.

Spouští se: python3 -m unittest discover -s tests -q
"""

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = ROOT / "skills" / "review" / "snapshot.py"

TODO = """# Fronta

## Přerušený běh

### /review branch
- nález: chybí kontrola vlastníka → POTVRZENO

## Teď

- [ ] ○ **Úkol, který zůstává**

# Mimo frontu

## Rozhodnuto k zapracování

- **Nález 3** → opravit guardem

```
## Teď
```

## Kola návrhu

- kolo zůstává
"""


def load():
    spec = importlib.util.spec_from_file_location("snapshot", SNAPSHOT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Snapshot(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name) / "project"
        self.project.mkdir()
        git = ["git", "-C", str(self.project)]
        subprocess.run([*git, "init", "-q"], check=True)
        self.write("docs/todo.md", TODO)
        self.write("src/app.py", "print('ahoj')\n")
        self.write(".gitignore", ".venv/\nbuild/\n.claude/run/\n")
        subprocess.run([*git, "add", "."], check=True)
        subprocess.run(
            [*git, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x"],
            check=True,
        )
        self.write("src/new.py", "x = 1\n")
        self.write("src/app.py", "print('změna')\n")
        self.write(".claude/run/review.json", '{"findings": []}')
        self.write("build/out.bin", "artefakt")
        (self.project / ".venv").mkdir()

    def write(self, rel, text):
        path = self.project / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def copy(self):
        dest = Path(self.tmp.name) / "copy"
        out = subprocess.run(
            ["python3", str(SNAPSHOT), str(self.project), str(dest)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(out.returncode, 0, out.stderr)
        return dest

    def test_skryte_sekce_zmizi(self):
        todo = (self.copy() / "docs/todo.md").read_text(encoding="utf-8")
        self.assertNotIn("Přerušený běh", todo)
        self.assertNotIn("POTVRZENO", todo)
        self.assertNotIn("Rozhodnuto k zapracování", todo)
        self.assertNotIn("opravit guardem", todo)

    def test_zbytek_todo_zustane(self):
        """Řez končí nadpisem první i druhé úrovně, ne až dalším skrytým."""
        todo = (self.copy() / "docs/todo.md").read_text(encoding="utf-8")
        self.assertIn("Úkol, který zůstává", todo)
        self.assertIn("# Mimo frontu", todo)
        self.assertIn("kolo zůstává", todo)

    def test_nadpis_v_bloku_kodu_rez_neukonci(self):
        """Jinak by blok kódu vrátil do kopie zbytek skryté sekce."""
        text = load().strip_sections(
            "## Rozhodnuto k zapracování\n```\n## Teď\n```\ntajné\n## Kola\n"
        )
        self.assertEqual(text, "## Kola\n")

    def test_behova_fronta_nalezu_zmizi(self):
        self.assertFalse((self.copy() / ".claude/run").exists())

    def test_pracovni_strom_vcetne_novych_souboru(self):
        dest = self.copy()
        self.assertEqual((dest / "src/app.py").read_text(), "print('změna')\n")
        self.assertTrue((dest / "src/new.py").is_file())

    def test_ignorovane_se_nekopiruje_zavislosti_se_nalinkuji(self):
        dest = self.copy()
        self.assertFalse((dest / "build").exists())
        self.assertTrue((dest / ".venv").is_symlink())
        self.assertEqual((dest / ".venv").resolve(), (self.project / ".venv").resolve())

    def test_existujici_cil_se_neprepise(self):
        dest = Path(self.tmp.name) / "copy"
        dest.mkdir()
        out = subprocess.run(
            ["python3", str(SNAPSHOT), str(self.project), str(dest)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(out.returncode, 2)


if __name__ == "__main__":
    unittest.main()
