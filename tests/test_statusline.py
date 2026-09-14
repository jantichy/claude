"""Regresní testy status line – vrstvy, která běží nad cizím repozitářem bez souhlasu.

`statusline.sh` se překresluje po každé odpovědi a permission systém na něj
nesahá: nic z toho, co spustí, si uživatel neodklikává. Zároveň stojí v adresáři,
který si nevybral – stačí rozbalit archiv nesoucí `.git/` a status line nad ním
běží při prvním překreslení.

Git přitom umí spustit program podle konfigurace toho repozitáře:
`filter.<jméno>.clean` se volá, kdykoliv potřebuje obsah pracovního souboru,
tedy i při `git diff --name-only`, kterým se počítají změny. Jméno filtru si
volí ten, kdo config napsal, takže ho nejde přebít `-c` přepínačem – obrana je
na takový repozitář nesahat.

Nebezpečné směry jsou dva. Spuštěný program znamená cizí kód s právy uživatele
bez jediného dotazu. Falešný poplach naopak znamená, že status line přestane
ukazovat počet změn v běžném projektu, a to je funkce, kvůli které existuje.

Spouští se: python3 -m unittest discover -s tests -q

Schválně jen stdlib – stejný důvod jako u `test_verify.py`.
"""
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATUSLINE = ROOT / "statusline.sh"

VAROVANI = "config spouští program"


def git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args],
                          capture_output=True, text=True, check=False)


class StatusLineNadCizimRepozitarem(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="statusline-test-"))
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        self.marker = self.tmp / "MARKER"
        git(self.repo, "init", "-q", "-b", "main", ".")
        git(self.repo, "config", "user.email", "t@t")
        git(self.repo, "config", "user.name", "t")
        (self.repo / "a.txt").write_text("puvodni\n")
        git(self.repo, "add", "a.txt")
        git(self.repo, "commit", "-qm", "init")
        # Rozdělaná změna: bez ní není co diffovat a filtr by se nevolal ani
        # v rozbité verzi, takže by test byl falešně zelený.
        (self.repo / "a.txt").write_text("zmenene\n")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # --- pomocné -----------------------------------------------------------

    def nastraz_filtr(self):
        """Nastaví clean filtr, který při zavolání vytvoří marker."""
        (self.repo / ".gitattributes").write_text("* filter=zlo\n")
        git(self.repo, "config", "filter.zlo.clean",
            f"sh -c 'touch {self.marker}; cat'")

    def spust(self, skript=None):
        vstup = json.dumps({
            "workspace": {"current_dir": str(self.repo),
                          "project_dir": str(self.repo)},
            "model": {"display_name": "Opus"},
            "context_window": {},
        })
        hotovo = subprocess.run(["bash", str(skript or STATUSLINE)],
                                input=vstup, capture_output=True, text=True,
                                cwd=str(self.repo), check=False)
        self.assertEqual(hotovo.returncode, 0, hotovo.stderr)
        return hotovo.stdout

    # --- nebezpečný směr: spuštěný program ---------------------------------

    def test_clean_filtr_se_nespusti(self):
        self.nastraz_filtr()
        vystup = self.spust()
        self.assertFalse(self.marker.exists(),
                         "status line spustila program z .git/config")
        self.assertIn(VAROVANI, vystup)

    def test_fsmonitor_je_nalez(self):
        git(self.repo, "config", "core.fsmonitor", "/bin/echo")
        self.assertIn(VAROVANI, self.spust())

    def test_textconv_je_nalez(self):
        git(self.repo, "config", "diff.zlo.textconv", "/bin/echo")
        self.assertIn(VAROVANI, self.spust())

    def test_vetev_se_zobrazi_i_pri_nalezu(self):
        """Varování nahrazuje počet změn, ne celý git blok – jinak by se
        falešný poplach projevil jako zmizelá informace bez vysvětlení."""
        self.nastraz_filtr()
        self.assertIn("main", self.spust())

    # --- nebezpečný směr: falešný poplach ----------------------------------

    def test_bezny_repozitar_hlasi_zmeny(self):
        vystup = self.spust()
        self.assertIn("~1 changes", vystup)
        self.assertNotIn(VAROVANI, vystup)

    def test_bezna_lokalni_konfigurace_neni_nalez(self):
        git(self.repo, "remote", "add", "origin", "https://example.invalid/r.git")
        git(self.repo, "config", "branch.main.rebase", "true")
        git(self.repo, "config", "core.ignorecase", "true")
        self.assertNotIn(VAROVANI, self.spust())

    def test_cisty_strom_hlasi_clean(self):
        git(self.repo, "checkout", "-q", "--", "a.txt")
        vystup = self.spust()
        self.assertIn("Clean", vystup)
        self.assertNotIn(VAROVANI, vystup)

    # --- mutace: ověř, že to výš měří kontrolu, a ne shodu náhodou ---------

    def test_mutace_vzoru_filtr_pusti(self):
        """Vyřízne filtry z blacklistu a ověří, že se pak marker opravdu vytvoří.

        Bez tohohle testu by `test_clean_filtr_se_nespusti` zůstal zelený i tehdy,
        kdyby marker nevznikal z úplně jiného důvodu – třeba proto, že git obsah
        souboru vůbec nečte."""
        poskozeny = self.tmp / "poskozena-statusline.sh"
        text = STATUSLINE.read_text()
        mutace = text.replace(r"|filter\..*\.(clean|smudge|process)", "")
        self.assertNotEqual(text, mutace, "vzor v statusline.sh se přejmenoval")
        poskozeny.write_text(mutace)

        self.nastraz_filtr()
        self.spust(poskozeny)
        self.assertTrue(self.marker.exists(),
                        "poškozená verze filtr nespustila – test tedy neměří kontrolu")


if __name__ == "__main__":
    unittest.main()
