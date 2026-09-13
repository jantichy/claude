"""Regresní testy vrstev, které něco vynucují mimo model – git hooku a CI.

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
import re
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

    def test_vsechny_defaultni_tvary_gitu_neprojdou(self):
        """Git negeneruje jen "Merge branch ".

        `git merge origin/vetev` dá "Merge remote-tracking branch" – tedy běžná
        cesta, jak se dokončuje větev pushnutá odjinud. Octopus merge dá "Merge
        branches", merge tagu "Merge tag". Všechny nesou jen jméno reference,
        takže v `git log --first-parent` neřeknou nic; vzor jen na první z nich
        propouštěl celou tuhle třídu a žádný test o ní nevěděl.
        """
        for zprava in ("Merge remote-tracking branch 'origin/feat/x'",
                       "Merge branches 'feat/a' and 'feat/b'",
                       "Merge tag 'v1.2.0'",
                       "Merge commit '9fceb02'",
                       "Merge branch 'feat/platby' into main"):
            with self.subTest(zprava=zprava):
                self.assertEqual(self.spust(zprava + "\n").returncode, ODMITA)

    def test_odsazeny_prvni_radek_vzor_neobejde(self):
        """`case` je kotvený na začátek řetězce, takže mezera před zprávou
        by stačila k obejití celé kontroly."""
        self.assertEqual(self.spust("   Merge branch 'feat/x'\n").returncode, ODMITA)

    def test_realny_merge_remote_tracking_se_zastavi(self):
        """Integračně tou cestou, kterou to potká uživatel: větev existuje jen
        jako remote-tracking reference a merguje se přes ni."""
        git(self.repo, "checkout", "-q", "-b", "feat/x")
        (self.repo / "b.txt").write_text("b\n")
        git(self.repo, "add", "b.txt")
        git(self.repo, "commit", "-qm", "prace")
        git(self.repo, "checkout", "-q", "main")
        # Remote-tracking referenci lze vyrobit i bez remote serveru.
        git(self.repo, "update-ref", "refs/remotes/origin/feat/x", "feat/x")
        git(self.repo, "branch", "-D", "feat/x")
        git(self.repo, "config", "core.hooksPath", str(HOOK.parent))
        v = git(self.repo, "merge", "--no-ff", "origin/feat/x")
        self.assertNotEqual(v.returncode, 0, "merge přes origin/… prošel bez zastavení")
        self.assertEqual(git(self.repo, "log", "--oneline").stdout.count("\n"), 1)

    # --- co musí projít ----------------------------------------------------

    def test_vlastni_zprava_projde(self):
        self.assertEqual(self.spust("Zaveď platby kartou\n").returncode, PUSTI)

    def test_merge_do_rozdelane_vetve_projde(self):
        """Aktualizace větve z main je běžný provoz a její defaultní zpráva
        do historie main nikdy nedoteče – hlídá se jen hlavní větev."""
        self.vetev("feat/platby")
        self.assertEqual(self.spust("Merge branch 'main' into feat/platby\n").returncode, PUSTI)

    def test_merge_po_pullu_tehoz_branche_projde(self):
        """`git pull` nad toutéž větví je synchronizace, ne dokončení práce,
        a blokovat ji by znamenalo blokovat pull."""
        v = self.spust("Merge branch 'main' of https://github.com/x/y\n")
        self.assertEqual(v.returncode, PUSTI)

    def test_pull_ciziho_branche_na_main_neprojde(self):
        """`git pull origin feat/z` na main je dokončení větve, ne synchronizace.

        Výjimka pro pull stála jen na výskytu ` of ` kdekoliv v prvním řádku, takže
        tuhle cestu propouštěla – a je to běžný způsob, jak se dokončuje větev
        pushnutá odjinud nebo z pull requestu. Dvě slova navíc stačila i k obejití
        (`Merge branch 'feat/x' of course`).
        """
        for zprava in ("Merge branch 'feat/z' of https://github.com/x/y",
                       "Merge branch 'feat/x' of course",
                       "Merge branch 'feat/z' of /tmp/remote"):
            with self.subTest(zprava=zprava):
                self.assertEqual(self.spust(zprava + "\n").returncode, ODMITA)

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

    def test_delegace_funguje_i_ve_worktree(self):
        """Ve worktree vrací `git rev-parse --git-dir` privátní adresář větve
        (`.git/worktrees/<jméno>`), kde hooky nejsou – cesta se proto musí
        skládat z `--git-common-dir`.

        Bez toho by delegace tiše selhala právě v layoutu, který `WORKTREE.md`
        předepisuje jako standard: lokální `commit-msg` projektu (gitleaks,
        commitlint, kontrola podpisu) by se přestal spouštět a nic by to neřeklo.
        """
        stopa = self.tmp / "stopa-worktree"
        self.lokalni_hook(f"#!/bin/sh\ntouch {stopa}\nexit 0\n")
        wt = self.tmp / "wt"
        v = git(self.repo, "worktree", "add", "-q", str(wt), "-b", "feat/wt")
        self.assertEqual(v.returncode, 0, v.stderr)
        soubor = wt / "MSG"
        soubor.write_text("Zaveď platby kartou\n")
        subprocess.run([str(HOOK), str(soubor)], cwd=wt,
                       capture_output=True, text=True, check=False)
        self.assertTrue(stopa.exists(),
                        "ve worktree se lokální hook repozitáře nezavolal")

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


class NasazeniGlobalnihoHooku(unittest.TestCase):
    """Že hook funguje, když ho zavoláš, neznamená, že ho někdo volá.

    `core.hooksPath` je stav stroje, ne repozitáře: nová instalace systému, jiný
    počítač nebo přepsaný `~/.gitconfig` hook odpojí, a nic o tom nedá vědět –
    merge prostě zase začne procházet s defaultní zprávou. Je to přesně ten tichý
    směr selhání, kvůli kterému `~/.claude/RULES.md`, *Ověřitelná kontrola místo
    dojmu*, žádá test k vynucovací vrstvě hned.

    Selhání tu není falešný poplach ani po čerstvém klonu: hook v tu chvíli
    opravdu nasazený není a zpráva říká, čím to napravit.
    """

    def test_hooksPath_miri_na_githooks(self):
        if os.environ.get("CI"):
            self.skipTest("v CI se necommituje, hook tam nemá co dělat")
        # `--global`, ne efektivní hodnota: tu uspokojí i `core.hooksPath` nastavený
        # jen v tomhle repozitáři – a hook by pak neběžel nikde jinde, přestože
        # pravidlo o zprávě merge commitu platí pro všechny projekty.
        v = subprocess.run(["git", "config", "--global", "--get", "core.hooksPath"],
                           capture_output=True, text=True, check=False)
        cesta = Path(v.stdout.strip()).expanduser() if v.stdout.strip() else None
        self.assertEqual(
            cesta, HOOK.parent,
            "git hook není nasazený – `git log --first-parent` se zaplní zprávami "
            "'Merge branch ...'. Naprav příkazem:\n"
            f"    git config --global core.hooksPath {HOOK.parent}")


class PrubeznaKontrolaVCI(unittest.TestCase):
    """CI je jediná kontrola, která běží mimo tenhle stroj.

    Lokální `verify.sh` obejde commit z jiného počítače, z GUI, s `--no-verify`
    i cizí fork – repozitář je veřejný. CI proto pouští týž *Kontrakt příkazů*.

    Do 13. 9. 2026 si ho parsovala sama a ta druhá implementace se s `verify.sh`
    rozešla ve třech vlastnostech naráz (HTML komentáře, dvě sekce téhož jména,
    klíč `cwd`). Testy tu proto hlídají jednu věc: že druhý parser nevznikl znovu.
    """

    WORKFLOW = ROOT / ".github" / "workflows" / "verify.yml"
    KONTRAKT = ROOT / ".claude" / "CLAUDE.md"

    #: Kroky, které do CI patří. Ne všechny klíče kontraktu: `dev` je watch server,
    #: který nikdy neskončí, `cwd` není příkaz. Množinová rovnost s kontraktem by
    #: v prvním projektu s `dev` vyrobila falešný poplach – a falešný poplach je
    #: u vynucovací vrstvy horší směr selhání než propuštěná chyba.
    CI_KROKY = {"typecheck", "lint", "test", "build", "audit", "coverage",
                "a11y", "perf", "mutation"}

    def text(self):
        return self.WORKFLOW.read_text(encoding="utf-8")

    def telo(self):
        """Workflow bez komentářových řádků.

        Testy nad celým souborem si uspokojí vlastní komentář: „volá
        `verify.sh --contract`“ napsané v hlavičce vypadá při hledání řetězce
        stejně jako to volání. Doloženo mutačním ověřením – dvě poškození kódu
        prošla, protože o nich mluvil komentář nad nimi.
        """
        return "\n".join(r for r in self.text().splitlines()
                          if not r.lstrip().startswith("#"))

    def test_workflow_existuje(self):
        self.assertTrue(self.WORKFLOW.exists(), f"chybí {self.WORKFLOW}")

    def test_workflow_ma_spoustece(self):
        """Existence souboru neznamená, že CI běží.

        Osekané `on:` na samotný `workflow_dispatch` nebo `if: false` na jobu jsou
        jednořádkové změny, po kterých se kontroly přestanou spouštět – a `verify.yml`
        v repozitáři dál vypadá platně. Je to tentýž tichý směr selhání, jaký u git
        hooku hlídá `core.hooksPath` (`~/Dev/context/coding/quality.md`, *Vynucovací
        vrstva se testuje jako kód, obousměrně*, třetí odrážka).
        """
        telo = self.telo()
        m = re.search(r"^on:\n((?:[ \t]+\S.*\n)+)", telo, re.M)
        self.assertIsNotNone(m, "ve workflow chybí blok `on:` – CI se nespouští")
        for spoustec in ("push", "pull_request"):
            with self.subTest(spoustec=spoustec):
                self.assertIn(spoustec, m.group(1), f"workflow se nespouští na {spoustec}")
        # (?m) je nutné: bez něj `^` matchuje jen začátek celého řetězce, takže
        # by kontrola `if:` uvnitř souboru nikdy nenašla a byla by zelená vždy.
        self.assertNotRegex(telo, r"(?m)^\s+if:\s", "job je podmíněný `if:` – může se tiše přeskočit")

    def test_kontrakt_cte_pres_verify_sh(self):
        """Jediná implementace parseru. Vlastní by se rozešla, jako se to už stalo."""
        self.assertRegex(self.telo(), r"verify\.sh --contract",
                         "workflow nevolá `verify.sh --contract` – nevznikl tu druhý parser?")

    def test_workflow_si_kontrakt_neparsuje_sam(self):
        """Mutační pojistka k testu výš: parser se pozná podle toho, že si sám
        hledá nadpis sekce nebo řádky `- klíč:` v Markdownu."""
        for vzor in ("## Kontrakt příkazů", "startswith", "re.findall", "python3 - <<"):
            with self.subTest(vzor=vzor):
                self.assertNotIn(vzor, self.telo(),
                                 f"workflow si kontrakt parsuje samo ({vzor})")

    def test_workflow_respektuje_cwd(self):
        """`verify.sh` klíčem cwd mění adresář, kde příkazy běží – typicky ve
        worktree layoutu. CI, která ho ignoruje, pouští něco jiného než lokální
        kontrola a obě si přitom myslí, že měřily totéž."""
        self.assertRegex(self.telo(), r'cwd=\$\(.*kontrakt',
                         "workflow klíč cwd nečte z kontraktu")
        self.assertRegex(self.telo(), r'cd "\$cwd"', "workflow podle cwd nemění adresář")

    def test_workflow_pousti_kroky_patrici_do_CI(self):
        """Klíč, který do CI patří a projekt ho má, se nesmí tiše vynechat."""
        m = re.search(r"for klic in ([a-z0-9 ]+); do", self.telo())
        self.assertIsNotNone(m, "ve workflow se nenašel výčet kroků – změnil se tvar?")
        self.assertEqual(set(m.group(1).split()), self.CI_KROKY,
                         "výčet kroků v CI se rozešel se seznamem v testu")

    def test_workflow_neopisuje_prikazy(self):
        """Kdyby se příkaz do workflow opsal, změna kontraktu by ho minula."""
        v = subprocess.run([str(ROOT / "verify.sh"), "--contract", str(ROOT)],
                           capture_output=True, text=True, check=False,
                           stdin=subprocess.DEVNULL)
        self.assertEqual(v.returncode, 0, v.stderr)
        prikazy = [r.split("\t", 1)[1] for r in v.stdout.splitlines() if "\t" in r]
        self.assertTrue(prikazy, "z kontraktu se nepřečetl jediný příkaz")
        for prikaz in prikazy:
            if prikaz.strip() == "-":
                continue
            with self.subTest(prikaz=prikaz[:40]):
                self.assertNotIn(prikaz, self.telo(),
                                 "workflow má příkaz opsaný, místo aby ho četl z kontraktu")



class MutaceKontrolVCI(unittest.TestCase):
    """Ověřuje, že kontroly workflow opravdu nahlásí poškozený vzor.

    Kontrola, kterou nikdo neviděl selhat, je nedoložené tvrzení a mlčí úplně
    stejně jako ta rozbitá (`~/Dev/context/coding/quality.md`, *Vynucovací vrstva
    se testuje jako kód, obousměrně*). Není to teoretická obava: při zavádění téhle
    sady byly dvě kontroly falešně zelené, protože měřily celý soubor a uspokojil
    je komentář nad kódem, který mutace nechala být.

    Mutuje se kopie v tempu, ne soubor v repozitáři – poškozený workflow, který by
    tam zůstal po spadlém testu, je horší než chybějící test.
    """

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="mutace-ci-"))
        self.puvodni = PrubeznaKontrolaVCI.WORKFLOW.read_text(encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def nahlasi(self, mutace, metoda):
        """Spustí jednu kontrolu nad poškozeným workflow a vrátí, jestli selhala."""
        podvrh = self.tmp / "verify.yml"
        text = mutace(self.puvodni)
        self.assertNotEqual(text, self.puvodni, "mutace se neaplikovala – změnil se tvar workflow?")
        podvrh.write_text(text, encoding="utf-8")
        trida = type("SPodvrhem", (PrubeznaKontrolaVCI,), {"WORKFLOW": podvrh})
        vysledek = unittest.TestResult()
        trida(metoda).run(vysledek)
        return bool(vysledek.failures or vysledek.errors)

    def test_vlastni_parser_kontrakt_shodi(self):
        self.assertTrue(self.nahlasi(
            lambda s: s.replace("./verify.sh --contract .", "grep -A20 Kontrakt .claude/CLAUDE.md"),
            "test_kontrakt_cte_pres_verify_sh"))

    def test_vypadly_krok_kontrola_nahlasi(self):
        self.assertTrue(self.nahlasi(
            lambda s: s.replace("for klic in typecheck lint test", "for klic in typecheck lint"),
            "test_workflow_pousti_kroky_patrici_do_CI"))

    def test_opsany_prikaz_kontrola_nahlasi(self):
        self.assertTrue(self.nahlasi(
            lambda s: s.replace("          set -e\n", "          set -e\n          python3 -m unittest discover -s tests\n"),
            "test_workflow_neopisuje_prikazy"))

    def test_osekane_spoustece_kontrola_nahlasi(self):
        self.assertTrue(self.nahlasi(
            lambda s: s.replace("on:\n  push:\n  pull_request:\n", "on:\n"),
            "test_workflow_ma_spoustece"))

    def test_podmineny_job_kontrola_nahlasi(self):
        self.assertTrue(self.nahlasi(
            lambda s: s.replace("  kontrakt:\n", "  kontrakt:\n    if: false\n"),
            "test_workflow_ma_spoustece"))

    def test_ignorovany_cwd_kontrola_nahlasi(self):
        self.assertTrue(self.nahlasi(
            lambda s: re.sub(r'\n\s+cwd=\$\([^\n]+\n\s+\[ -n "\$cwd" \] && cd "\$cwd"\n', "\n", s),
            "test_workflow_respektuje_cwd"))

    def test_neposkozeny_workflow_projde(self):
        """Pojistka proti obrácené chybě: kdyby kontroly hlásily i nad zdravým
        souborem, byly by ty mutační testy zelené omylem."""
        self.assertFalse(self.nahlasi(lambda s: s + "\n# neškodný komentář\n",
                                      "test_kontrakt_cte_pres_verify_sh"))


if __name__ == "__main__":
    unittest.main()
