"""Regresní testy `envkeys.py`, který vypíše klíče v `.env` bez hodnot.

Skript je jediná cesta k tajemství, kterou `secret-guard.py` pouští, takže
jeho vada je přesně ta, kvůli které hook existuje: hodnota v kontextu a v
transcriptu. Hlídá se proto hlavně to, co **nesmí** vyjít ven – hodnota, ani
její kus, ani nerozebraný řádek, ve kterém by mohla stát. Stav klíče je až
druhá polovina.

Spouští se: python3 -m unittest discover -s tests -q
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "hooks" / "envkeys.py"
SECRET = "sk-live-7f3a9c"


class EnvKeys(unittest.TestCase):
    def run_script(self, content):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / ".env"
            path.write_text(content, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(SCRIPT), str(path)],
                capture_output=True,
                text=True,
                check=False,
            )

    def test_values_never_leave(self):
        """Hodnota nevyjde ven v žádném tvaru zápisu ani v nerozebraném řádku."""
        done = self.run_script(
            f"A={SECRET}\n"
            f'export B="{SECRET}" # komentář\n'
            f"C='{SECRET}'\n"
            f"{SECRET} bez rovnítka\n"
            f"D = {SECRET}\n"
        )
        self.assertEqual(0, done.returncode, done.stderr)
        self.assertNotIn("7f3a9c", done.stdout + done.stderr)
        self.assertIn("řádek 4", done.stdout)

    def test_states(self):
        """Prázdný, zástupný a vyplněný klíč se rozliší."""
        done = self.run_script(
            '# komentář\n\nEMPTY=\nQUOTED_EMPTY=""\nPH=changeme\nPH2=<token>\n'
            "PH3=your_api_key\nREAL=abc123\n"
        )
        lines = dict(line.split("\t") for line in done.stdout.splitlines())
        self.assertEqual(
            {
                "EMPTY": "prázdný",
                "QUOTED_EMPTY": "prázdný",
                "PH": "zástupný",
                "PH2": "zástupný",
                "PH3": "zástupný",
                "REAL": "vyplněný",
            },
            lines,
        )

    def test_missing_file_is_call_error(self):
        """Chybějící soubor je chyba volání (2), ne prázdný výsledek."""
        done = subprocess.run(
            [sys.executable, str(SCRIPT), "/neexistuje/.env"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(2, done.returncode)


if __name__ == "__main__":
    unittest.main()
