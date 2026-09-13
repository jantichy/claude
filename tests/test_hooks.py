"""Regresní testy git hooku, který hlídá zprávu merge commitu.

`githooks/commit-msg` je vedle `verify.sh` druhé místo konfigurace, které něco
doopravdy vynucuje – zbytek je text, který vykonává model. Je přitom nasazený
přes globální `core.hooksPath`, takže běží nad **každým** repozitářem na stroji:
falešný poplach tam neblokuje jeden skill, ale běžnou práci v cizím projektu.

Nebezpečné směry jsou proto dva a testují se oba. Propuštěná defaultní zpráva
znamená, že se do historie main dostane řádek, který o větvi neřekne nic –
tedy přesně to, kvůli čemu hook vznikl. Zablokovaný legitimní merge (aktualizace
větve z main, merge po `git pull`) znamená, že si ho člověk při první kolizi
vypne, a pak nehlídá nic.

Třetí testovaná věc je delegace: globální `core.hooksPath` vypne lokální
`.git/hooks`, takže hook musí zavolat lokální `commit-msg`, pokud v repozitáři je.
Bez toho by nasazení tiše odstřihlo hooky cizích projektů.

Spouští se: python3 -m unittest discover -s tests -q

Schválně jen stdlib – stejný důvod jako u `test_verify.py`.
"""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOOK = ROOT / "githooks" / "commit-msg"

ODMITA = 1
PUSTI = 0


def git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args],
                          capture_output=True, text=True, check=False)


class ZpravaMergeCommitu(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="hooks-test-"))
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q", "-b", "main", ".")
        git(self.repo, "config", "user.email", "t@t")
        git(self.repo, "config", "user.name", "t")
        (self.repo / "a.txt").write_text("a\n")
        git(self.repo, "add", "a.txt")
        git(self.repo, "commit", "-qm", "init")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # --- pomocné -----------------------------------------------------------

    def spust(self, zprava):
        """Zavolá hook nad souborem se zprávou, jak to dělá git."""
        soubor = self.repo / ".git" / "COMMIT_EDITMSG"
        soubor.write_text(zprava)
        return subprocess.run([str(HOOK), str(soubor)], cwd=self.repo,
                              capture_output=True, text=True, check=False)

    def vetev(self, jmeno):
        git(self.repo, "checkout", "-q", "-b", jmeno)

    # --- co se má odmítnout ------------------------------------------------

    def test_defaultni_anglicka_zprava_na_main_neprojde(self):
        v = self.spust("Merge branch 'feat/platby'\n")
        self.assertEqual(v.returncode, ODMITA)
        self.assertIn("WORKTREE.md", v.stderr)

    def test_defaultni_ceska_zprava_na_main_neprojde(self):
        self.assertEqual(self.spust("Merge větve docs/znamky\n").returncode, ODMITA)

    def test_komentare_nad_zpravou_hook_nezmatou(self):
        """Git dává do COMMIT_EDITMSG vysvětlující komentáře; první *neprázdný
        nekomentářový* řádek je ta zpráva, a hook musí hledat ten."""
        v = self.spust("\n# Please enter a commit message\n\nMerge branch 'feat/x'\n")
        self.assertEqual(v.returncode, ODMITA)

    def test_realny_merge_na_main_se_zastavi(self):
        """Integračně: hook musí sedět i skutečnému `git merge`, ne jen přímému
        volání – merge commit vzniká jinou cestou než `git commit`."""
        self.vetev("feat/x")
        (self.repo / "b.txt").write_text("b\n")
        git(self.repo, "add", "b.txt")
        git(self.repo, "commit", "-qm", "prace")
        git(self.repo, "checkout", "-q", "main")
        git(self.repo, "config", "core.hooksPath", str(HOOK.parent))
        v = git(self.repo, "merge", "--no-ff", "feat/x")
        self.assertNotEqual(v.returncode, 0)
        self.assertEqual(git(self.repo, "log", "--oneline").stdout.count("\n"), 1)

    # --- co musí projít ----------------------------------------------------

    def test_vlastni_zprava_projde(self):
        self.assertEqual(self.spust("Zaveď platby kartou\n").returncode, PUSTI)

    def test_merge_do_rozdelane_vetve_projde(self):
        """Aktualizace větve z main je běžný provoz a její defaultní zpráva
        do historie main nikdy nedoteče – hlídá se jen hlavní větev."""
        self.vetev("feat/platby")
        self.assertEqual(self.spust("Merge branch 'main' into feat/platby\n").returncode, PUSTI)

    def test_merge_po_pullu_projde(self):
        """`git pull` vyrobí zprávu s ' of <url>'. Je to synchronizace téže
        větve, ne dokončení práce, a blokovat ji by znamenalo blokovat pull."""
        v = self.spust("Merge branch 'main' of https://github.com/x/y\n")
        self.assertEqual(v.returncode, PUSTI)

    def test_zprava_zminujici_merge_uvnitr_projde(self):
        self.assertEqual(self.spust("Oprav merge větve v dokumentaci\n").returncode, PUSTI)

    # --- delegace na lokální hook -----------------------------------------

    def lokalni_hook(self, telo):
        cesta = self.repo / ".git" / "hooks" / "commit-msg"
        cesta.parent.mkdir(exist_ok=True)
        cesta.write_text(telo)
        cesta.chmod(0o755)
        return cesta

    def test_lokalni_hook_se_zavola(self):
        stopa = self.repo / "stopa"
        self.lokalni_hook(f"#!/bin/sh\ntouch {stopa}\nexit 0\n")
        self.assertEqual(self.spust("Zaveď platby kartou\n").returncode, PUSTI)
        self.assertTrue(stopa.exists(), "lokální hook repozitáře se nespustil")

    def test_nesouhlas_lokalniho_hooku_zastavi(self):
        self.lokalni_hook("#!/bin/sh\necho lokalni namitka >&2\nexit 3\n")
        v = self.spust("Zaveď platby kartou\n")
        self.assertEqual(v.returncode, 3)
        self.assertIn("lokalni namitka", v.stderr)

    def test_lokalni_hook_neprebiji_kontrolu_zpravy(self):
        """Lokální hook smí přidat vlastní pravidlo, ne zrušit tohle."""
        self.lokalni_hook("#!/bin/sh\nexit 0\n")
        self.assertEqual(self.spust("Merge branch 'feat/x'\n").returncode, ODMITA)


class NasazeniHooku(unittest.TestCase):
    def test_hook_je_spustitelny(self):
        self.assertTrue(os.access(HOOK, os.X_OK), f"{HOOK} není spustitelný")

    def test_pravidlo_je_zapsane_ve_worktree_md(self):
        """Hook je mechanismus, ne zdroj pravdy. Zmizí-li pravidlo z WORKTREE.md,
        nikdo se z odmítnutí nedozví, jakou zprávu má napsat místo toho."""
        text = (ROOT / "WORKTREE.md").read_text()
        self.assertIn("--no-ff", text)
        self.assertIn("githooks/commit-msg", text)


if __name__ == "__main__":
    unittest.main()
