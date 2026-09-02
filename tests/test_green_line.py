"""Regresní testy zelené linky.

`green-line.sh` je jediné místo celé konfigurace, které něco doopravdy vynucuje –
všechno ostatní je text, který vykonává model. Zároveň je to ~400 řádků bashe
s netriviální logikou: otisk stavu, souhlas podle repozitáře, rozlišení
"test našel chybu" od "test nejde spustit", timeouty, pojistka proti smyčce.

`decisions.md` dokládá, že v té logice už dvakrát byla kritická díra (otisk
nezahrnoval obsah souborů; chybějící nástroj se hlásil jako červená linka).
Selhání je přitom **tiché v nebezpečném směru**: `exit 0` tam, kde má být `exit 2`,
znamená, že se práce uzavře nad červenými testy a nikdo se to nedozví.

Spouští se: python3 -m unittest discover -s tests -q

Schválně jen stdlib – stejný důvod jako u `test_skills.py`. Každý test si staví
vlastní dočasný repozitář a přesměrovaný HOME, takže nesahá na skutečné souhlasy
ani na skutečný běhový stav.
"""
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOOK = ROOT / "green-line.sh"

# Návratové kódy Stop hooku. Rozdíl mezi 1 a 2 je celý smysl téhle vrstvy:
# při 2 dostane výstup MODEL jako pokyn, při 1 jen člověk do transkriptu.
BLOKUJE = 2   # model to uvidí a má na to reagovat
MLCI = 1      # jen pro člověka; model o tom neví
PUSTI = 0     # v pořádku, nebo se vědomě nic nespouští


def git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args],
                          capture_output=True, text=True, check=False)


class ZelenaLinka(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="green-line-test-"))
        self.home = self.tmp / "home"
        self.home.mkdir()
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q", ".")
        git(self.repo, "config", "user.email", "t@t")
        git(self.repo, "config", "user.name", "t")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # --- pomocné -----------------------------------------------------------

    def kontrakt(self, **prikazy):
        """Napíše CLAUDE.md se sekcí ## Příkazy a commitne ho."""
        radky = "\n".join(f"- {k}: {v}" for k, v in prikazy.items())
        (self.repo / "CLAUDE.md").write_text(f"# Test\n\n## Příkazy\n\n{radky}\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "kontrakt")

    def allow(self, cesta=None):
        return self.spust(["--allow", str(cesta or self.repo)], vstup=None)

    def spust(self, argv=None, vstup="", cwd=None, stop_hook_active=False):
        env = dict(os.environ, HOME=str(self.home))
        env.pop("XDG_STATE_HOME", None)
        env.pop("CLAUDE_NO_GREEN_LINE", None)
        if vstup is not None:
            vstup = json.dumps({"session_id": "s1",
                                "cwd": str(cwd or self.repo),
                                "stop_hook_active": stop_hook_active})
        return subprocess.run(["bash", str(HOOK), *(argv or [])],
                              input=vstup, capture_output=True, text=True, env=env)

    def klic(self):
        """Klíč projektu počítaný stejně jako ve skriptu: sha1 kanonického
        sdíleného .git. Odvozovat ho z existujících souborů nejde – červený běh
        stav neukládá."""
        common = git(self.repo, "rev-parse", "--git-common-dir").stdout.strip()
        cesta = Path(common) if common.startswith("/") else self.repo / common
        return subprocess.run(["shasum"], input=str(cesta.resolve()),
                              capture_output=True, text=True).stdout.split()[0]

    # --- souhlas -----------------------------------------------------------

    def test_bez_souhlasu_nespusti_nic(self):
        """Kontrakt je kód z repozitáře a hooky běží mimo permission systém."""
        self.kontrakt(test="touch NESMI-VZNIKNOUT")
        r = self.spust()
        self.assertEqual(r.returncode, MLCI)
        self.assertIn("není vydaný souhlas", r.stderr)
        self.assertFalse((self.repo / "NESMI-VZNIKNOUT").exists(),
                         "hook spustil příkaz z repozitáře, pro který nebyl vydaný souhlas")

    def test_souhlas_plati_pro_repozitar_vcetne_worktree(self):
        """Ve worktree layoutu má každá větev vlastní adresář.

        Klíč podle cesty by znamenal nový souhlas na každé nové větvi – tedy bránu
        vypnutou právě tam, kde se pracuje, a funkční na main, kde se nepracuje.
        """
        self.kontrakt(typecheck="-", lint="-", test="true")
        self.allow()
        vetev = self.tmp / "feat"
        git(self.repo, "worktree", "add", "-q", str(vetev), "-b", "feat")
        r = self.spust(cwd=vetev)
        self.assertEqual(r.returncode, PUSTI,
                         f"na nové větvi brána neběžela: {r.stderr}")

    def test_souhlas_prezije_symlink_v_ceste(self):
        """Souhlas vydaný přes symlink se musí potkat s během, který ho má rozřešený.

        Na macOS je /var symlink na /private/var, takže stačí projekt v dočasném
        adresáři – ale platí to pro každý symlinkovaný adresář s projekty. Bez
        kanonizace obou stran brána mlčky neběží a jediné, co uživatel dostane,
        je hláška "není vydaný souhlas".
        """
        self.kontrakt(typecheck="-", lint="-", test="true")
        odkaz = self.tmp / "odkaz"
        odkaz.symlink_to(self.repo)
        self.allow(odkaz)                       # souhlas přes symlink
        r = self.spust(cwd=self.repo.resolve())  # běh přes skutečnou cestu
        self.assertEqual(r.returncode, PUSTI,
                         f"souhlas se nepotkal kvůli symlinku v cestě: {r.stderr}")

    # --- exit kódy ---------------------------------------------------------

    def test_cervena_linka_blokuje_a_mluvi_k_modelu(self):
        self.kontrakt(typecheck="-", lint="-", test="false")
        self.allow()
        r = self.spust()
        self.assertEqual(r.returncode, BLOKUJE)
        self.assertIn("není zelená", r.stderr)

    def test_druhy_pokus_pusti_dal_ale_neztichne(self):
        """Brána zastaví jednou, ne napořád – ale model se to musí dozvědět.

        Při exit 1 by svoje "hotovo" nechal stát nad stavem, který zelený není.
        """
        self.kontrakt(typecheck="-", lint="-", test="false")
        self.allow()
        self.spust()
        r = self.spust(stop_hook_active=True)
        self.assertEqual(r.returncode, BLOKUJE)
        self.assertIn("ani napodruhé", r.stderr)

    def test_nad_tymz_stavem_se_uz_neptame(self):
        """Jinak by se práce zasekla na chybě, kterou model opravit nedokáže."""
        self.kontrakt(typecheck="-", lint="-", test="false")
        self.allow()
        self.spust()
        self.spust(stop_hook_active=True)
        r = self.spust(stop_hook_active=True)
        self.assertEqual(r.returncode, PUSTI)

    def test_chybejici_nastroj_neni_cervena_linka(self):
        """Blokovat by znamenalo hnát model opravovat kód, který za to nemůže."""
        self.kontrakt(typecheck="-", lint="-", test="prikaz-ktery-neexistuje-xyz")
        self.allow()
        r = self.spust()
        self.assertEqual(r.returncode, MLCI)
        self.assertIn("neopravuj kód", r.stderr)

    def test_dira_v_kontraktu_se_hlasi_modelu(self):
        """Nezkontrolovaný krok musí do shrnutí, a to píše model."""
        self.kontrakt(test="true")
        self.allow()
        r = self.spust()
        self.assertEqual(r.returncode, BLOKUJE)
        self.assertIn("nekontrolovalo se", r.stderr)

    def test_pomlcka_mlci(self):
        """Vědomé rozhodnutí se nehlásí jako díra v kontraktu."""
        self.kontrakt(typecheck="-", lint="-", test="true")
        self.allow()
        r = self.spust()
        self.assertEqual(r.returncode, PUSTI)
        self.assertEqual(r.stderr.strip(), "")

    # --- vypnutí -----------------------------------------------------------

    def test_vypnuta_brana_se_hlasi(self):
        """Vypnutá brána, o které se mlčí, je horší než chybějící brána."""
        self.kontrakt(typecheck="-", lint="-", test="false")
        self.allow()
        (self.repo / ".claude").mkdir(exist_ok=True)
        (self.repo / ".claude/no-green-line").touch()
        r = self.spust()
        self.assertEqual(r.returncode, PUSTI)
        self.assertIn("vypnutá souborem", r.stderr)

    # --- otisk stavu -------------------------------------------------------

    def test_otisk_vidi_do_neverzovaneho_adresare(self):
        """Bez -uall je celý nový adresář jedinou položkou "?? dir/".

        Test [ -f ] na ní neprojde, obsah se do otisku nedostane – a protože nová
        feature skoro vždycky začíná novým adresářem, byla by brána mrtvá právě
        tam, kde se pracuje.
        """
        self.kontrakt(typecheck="-", lint="-", test="test ! -f nove/spatne.txt")
        self.allow()
        (self.repo / "nove").mkdir()
        (self.repo / "nove/dobre.txt").write_text("ok\n")
        self.assertEqual(self.spust().returncode, PUSTI, "výchozí stav měl být zelený")
        (self.repo / "nove/spatne.txt").write_text("rozbito\n")
        self.assertEqual(self.spust().returncode, BLOKUJE,
                         "změna uvnitř neverzovaného adresáře se do otisku nepromítla")

    def test_otisk_vidi_zmenu_rozpracovaneho_souboru(self):
        """Porcelain vypíše " M soubor" stejně pro první i desátou úpravu."""
        self.kontrakt(typecheck="-", lint="-", test="test ! -s data.txt")
        self.allow()
        (self.repo / "data.txt").write_text("")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "data")
        self.assertEqual(self.spust().returncode, PUSTI)
        (self.repo / "data.txt").write_text("rozbito\n")
        self.assertEqual(self.spust().returncode, BLOKUJE)

    # --- kontrakt ----------------------------------------------------------

    def test_prikazy_v_bloku_kodu_nejsou_kontrakt(self):
        """Ukázka formátu v dokumentaci se nesmí stát kontraktem.

        coding.md takovou ukázku obsahuje; kdo si ji zkopíruje do CLAUDE.md, dostal
        by po každém tahu běžící npm test. Je to zároveň cesta, kudy jde do
        repozitáře propašovat příkaz schovaný jako dokumentace.
        """
        (self.repo / "CLAUDE.md").write_text(
            "# Test\n\nKontrakt nemáme. Formát vypadá takhle:\n\n"
            "```markdown\n## Příkazy\n\n- test: touch NESMI-VZNIKNOUT\n```\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "dokumentace")
        r = self.allow()
        self.assertNotEqual(r.returncode, 0, "--allow přijal ukázku v bloku kódu jako kontrakt")
        self.spust()
        self.assertFalse((self.repo / "NESMI-VZNIKNOUT").exists(),
                         "hook spustil příkaz z bloku kódu v dokumentaci")

    def test_kontrakt_v_claude_podadresari(self):
        """Druhé z povolených umístění – kořenový CLAUDE.md bývá obsazený."""
        (self.repo / ".claude").mkdir()
        (self.repo / ".claude/CLAUDE.md").write_text(
            "# Test\n\n## Příkazy\n\n- typecheck: -\n- lint: -\n- test: test -d .claude\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "kontrakt")
        self.allow()
        self.assertEqual(self.spust().returncode, PUSTI,
                         "příkazy neběžely v kořeni repozitáře, ale v .claude/")

    def test_cwd_posouva_kde_prikazy_bezi(self):
        """Monorepo a projekt, kde se nespouští z kořene."""
        (self.repo / "packages/api").mkdir(parents=True)
        (self.repo / "packages/api/ZNACKA").touch()
        self.kontrakt(typecheck="-", lint="-", test="test -f ZNACKA", cwd="packages/api")
        self.allow()
        self.assertEqual(self.spust().returncode, PUSTI,
                         "příkaz neběžel v adresáři z klíče cwd")

    def test_cwd_mimo_projekt_se_odmitne(self):
        self.kontrakt(typecheck="-", lint="-", test="true", cwd="../jinam")
        self.allow()
        r = self.spust()
        self.assertEqual(r.returncode, MLCI)
        self.assertIn("cwd", r.stderr)

    # --- souběh ------------------------------------------------------------

    def test_zamek_zabrani_soubeznemu_behu(self):
        """Dvě session nad jedním stromem jinak pustí testy současně."""
        self.kontrakt(typecheck="-", lint="-", test="false")
        self.allow()
        stav = self.home / ".local/state/claude-green-line/runs"
        stav.mkdir(parents=True, exist_ok=True)
        (stav / f"{self.klic()}.lock").mkdir()
        r = self.spust()
        self.assertEqual(r.returncode, PUSTI)
        self.assertIn("v jiné session", r.stderr)

    # --- odvolání souhlasu -------------------------------------------------

    def test_revoke_snese_tecku_i_lomitko(self):
        """Odvolání, které tiše neproběhne, je bezpečnostní funkce selhávající
        směrem k "povoleno" – a hláška zněla jako fakt o stavu, ne jako chyba."""
        self.kontrakt(typecheck="-", lint="-", test="true")
        for argument in [".", str(self.repo) + "/"]:
            with self.subTest(argument=argument):
                self.allow()
                r = subprocess.run(["bash", str(HOOK), "--revoke", argument],
                                   capture_output=True, text=True, cwd=str(self.repo),
                                   env=dict(os.environ, HOME=str(self.home)))
                self.assertEqual(r.returncode, 0, f"--revoke {argument} neuspěl: {r.stderr}")


if __name__ == "__main__":
    unittest.main()
