"""Regresní testy měřicího skriptu `/slim`.

Skript rozhoduje, co se počítá do paušálu, takže chyba v něm se promítne do
každého návrhu. Hlídají se oba směry: import v bloku kódu nebo v apostrofech
Claude Code nevyhodnotí a počítat se nesmí, skutečný import naopak ano – včetně
relativní cesty, rekurze a toho, že se tentýž soubor nezapočítá dvakrát.
"""

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location(
    "measure", ROOT / "skills/slim/scripts/measure.py"
)
measure = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(measure)


class Imports(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        for name in ("a.md", "b.md", "c.md"):
            (self.dir / name).write_text(name, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def found(self, text):
        return [p.name for p in measure.imports(text, self.dir)]

    def test_plain_import_counts(self):
        self.assertEqual(self.found("- @a.md – popis\n@b.md"), ["a.md", "b.md"])

    def test_code_span_is_not_import(self):
        self.assertEqual(
            self.found("ukázka `@a.md`, `` `@b.md` `` a `viz @c.md tady`"), []
        )

    def test_fenced_block_is_not_import(self):
        self.assertEqual(self.found("```\n@a.md\n```\n@c.md"), ["c.md"])

    def test_missing_file_is_not_import(self):
        self.assertEqual(self.found("@neni.md a e-mail jan@example.cz"), [])

    def test_trailing_punctuation_is_stripped(self):
        self.assertEqual(self.found("viz @a.md."), ["a.md"])


class Walk(unittest.TestCase):
    def test_shortest_depth_and_dedupe(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp).resolve() / "project"
            (project / "docs").mkdir(parents=True)
            (project / "CLAUDE.md").write_text(
                "@docs/x.md\n@docs/y.md", encoding="utf-8"
            )
            (project / "docs/x.md").write_text("@y.md", encoding="utf-8")
            (project / "docs/y.md").write_text("list", encoding="utf-8")
            rows = [
                (d, p.name) for d, p, _ in measure.walk(project) if project in p.parents
            ]
            # y.md je importovaný přímo i přes x.md; platí kratší hloubka a jen jednou.
            self.assertEqual(rows, [(0, "CLAUDE.md"), (1, "x.md"), (1, "y.md")])


class Sections(unittest.TestCase):
    def test_markers_are_counted(self):
        body = "## A\nDoloženo 6. 9. 2026.\n**Proč:** protože.\n## B\nnic"
        counts = [
            len(p.findall(body.split("## B")[0])) for p in measure.MARKERS.values()
        ]
        self.assertEqual(counts, [1, 1, 1, 0])


if __name__ == "__main__":
    unittest.main()
