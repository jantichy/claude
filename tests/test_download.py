"""Testy skriptu `/download`, který plní seznam ke stažení odbavovaný clockworkem.

Seznam čte a odškrtává jiný proces, takže každá vada skriptu je tichá a projeví
se až u clockworku: řádek v jiném tvaru se nestáhne, nepoznaná duplicita se
stáhne dvakrát, položka pod špatným nadpisem skončí v jiné složce a napůl
zapsaný soubor clockwork přečte jako kratší seznam. Testuje se proto obsah
souboru po zápisu, ne jen výstup skriptu – a kde je clockwork na disku, i to,
že zapsaný seznam přečte jeho vlastní parser stejně.

Spouští se: python3 -m unittest discover -s tests -q
"""

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills" / "download" / "add.py"
CLOCKWORK_LISTING = Path(
    "~/Dev/clockwork/src/clockwork/tasks/download/listing.py"
).expanduser()
DRIVE = "https://drive.google.com/file/d/{}/view"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AddToList(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.list = Path(self.tmp.name) / "downloads.md"

    def tearDown(self):
        self.tmp.cleanup()

    def add(self, *items, code=0):
        run = subprocess.run(
            [sys.executable, str(SCRIPT), "--list", str(self.list)],
            input=json.dumps({"items": list(items)}),
            capture_output=True,
            text=True,
        )
        self.assertEqual(run.returncode, code, run.stdout + run.stderr)
        return json.loads(run.stdout)

    def test_new_list_gets_root_and_folder_sections(self):
        out = self.add(
            {"url": "https://example.org/uvod.pdf"},
            {"url": "https://drive.google.com/open?id=A1", "folder": "Kurz"},
            {"url": "https://example.org/b.mp4", "folder": "Kurz", "name": "02 Druhá"},
        )
        self.assertTrue(out["verified"])
        self.assertEqual(
            self.list.read_text(),
            "- [ ] https://example.org/uvod.pdf\n"
            "\n"
            "## Kurz\n"
            f"- [ ] {DRIVE.format('A1')}\n"
            "- [ ] https://example.org/b.mp4 → 02 Druhá\n",
        )

    def test_items_go_to_the_end_of_their_existing_section(self):
        self.list.write_text(
            "# Stahování\n\n## A\n- [x] https://e.org/1 → 1\n\n## B\n- [ ] https://e.org/2\n"
        )
        self.add(
            {"url": "https://e.org/3", "folder": "A"},
            {"url": "https://e.org/0"},
        )
        self.assertEqual(
            self.list.read_text(),
            "# Stahování\n- [ ] https://e.org/0\n\n"
            "## A\n- [x] https://e.org/1 → 1\n- [ ] https://e.org/3\n\n"
            "## B\n- [ ] https://e.org/2\n",
        )

    def test_duplicate_is_found_anywhere_also_downloaded_and_in_other_form(self):
        self.list.write_text(f"## Staré\n- [x] {DRIVE.format('X9')} → a.mp4\n")
        out = self.add(
            {
                "url": "https://drive.google.com/uc?id=X9&export=download",
                "folder": "Nové",
            }
        )
        self.assertEqual(out["added"], [])
        self.assertEqual(out["skipped"][0]["folder"], "Staré")
        self.assertTrue(out["skipped"][0]["done"])
        self.assertNotIn("Nové", self.list.read_text())

    def test_force_adds_again_but_not_twice_in_one_run(self):
        self.list.write_text("- [x] https://e.org/1 → 1\n")
        out = self.add(
            {"url": "https://e.org/1", "force": True},
            {"url": "https://e.org/1", "force": True},
        )
        self.assertEqual(len(out["added"]), 1)
        self.assertEqual(len(out["skipped"]), 1)
        self.assertEqual(self.list.read_text().count("https://e.org/1"), 2)

    def test_what_clockwork_cannot_download_is_rejected_not_written(self):
        out = self.add(
            {"url": "https://drive.google.com/drive/folders/F1?usp=sharing"},
            {"url": "https://drive.google.com/drive/u/0/folders/F2"},
            {"url": "https://docs.google.com/document/d/D1/edit"},
            {"url": "ftp://e.org/a"},
            {"url": "https://e.org/a", "folder": "../ven"},
            {"url": "https://e.org/b", "folder": "/abs"},
            {"url": "https://e.org/c", "name": "a/b"},
        )
        self.assertEqual(len(out["rejected"]), 7, out["rejected"])
        self.assertFalse(self.list.exists(), "nic nepřidáno → soubor nevznikne")

    def test_folder_is_normalized_and_matches_existing_heading(self):
        self.list.write_text("## Kurz/Cvičení\n- [ ] https://e.org/1\n")
        self.add({"url": "https://e.org/2", "folder": "/Kurz/ Cvičení/"})
        self.assertEqual(self.list.read_text().count("## "), 1)

    def test_write_is_refused_when_list_keeps_changing(self):
        module = load(SCRIPT, "download_add")
        self.list.write_text("")
        ticks = iter(range(100))
        with mock.patch.object(module, "snapshot", lambda _p: next(ticks)):
            with self.assertRaises(RuntimeError):
                module.run(self.list, [{"url": "https://e.org/1"}])
        self.assertEqual(self.list.read_text(), "", "nic se nesmí zapsat napůl")

    def test_hand_written_checkbox_shapes_count_as_present(self):
        self.list.write_text(
            "  * [ ] https://e.org/a\n1. [x] https://e.org/b → b\n", encoding="utf-8"
        )
        out = self.add({"url": "https://e.org/a"}, {"url": "https://e.org/b"})
        self.assertEqual(out["added"], [])
        self.assertEqual(len(out["skipped"]), 2)

    def test_code_block_is_neither_present_nor_insertion_point(self):
        self.list.write_text(
            "- [ ] https://e.org/a\n```\n- [ ] https://e.org/b\n## Kurz\n```\n",
            encoding="utf-8",
        )
        out = self.add({"url": "https://e.org/b"}, {"url": "https://e.org/c"})
        self.assertTrue(out["verified"])
        self.assertEqual(
            self.list.read_text(),
            "- [ ] https://e.org/a\n- [ ] https://e.org/b\n- [ ] https://e.org/c\n"
            "```\n- [ ] https://e.org/b\n## Kurz\n```\n",
        )

    @unittest.skipUnless(CLOCKWORK_LISTING.exists(), "clockwork na disku není")
    def test_clockwork_parser_reads_what_was_written(self):
        """Formát je rozhraní dvou repozitářů; rozejití chytí jen čtení jeho parserem."""
        self.add(
            {"url": "https://e.org/root"},
            {
                "url": "https://drive.google.com/open?id=Z",
                "folder": "K/L",
                "name": "Jméno",
            },
        )
        listing = load(CLOCKWORK_LISTING, "clockwork_listing").parse(
            self.list.read_text()
        )
        self.assertEqual(listing.invalid, ())
        self.assertEqual(
            [(e.folder, e.url, e.name, e.done) for e in listing.entries],
            [
                ("", "https://e.org/root", None, False),
                ("K/L", DRIVE.format("Z"), "Jméno", False),
            ],
        )


if __name__ == "__main__":
    unittest.main()
