"""Regresní testy průběžné kontroly.

`verify.sh` je jediné místo celé konfigurace, které něco doopravdy vynucuje –
všechno ostatní je text, který vykonává model. Zároveň je to přes 500 řádků bashe
s netriviální logikou: otisk stavu, souhlas podle repozitáře, rozlišení
"test našel chybu" od "test nejde spustit", timeouty, pojistka proti smyčce.

`decisions.md` dokládá, že v té logice už dvakrát byla kritická díra (otisk
nezahrnoval obsah souborů; chybějící nástroj se hlásil jako padající kontrola).
Selhání je přitom **tiché v nebezpečném směru**: `exit 0` tam, kde má být `exit 2`,
znamená, že se práce uzavře nad červenými testy a nikdo se to nedozví.

Spouští se: python3 -m unittest discover -s tests -q

Schválně jen stdlib – stejný důvod jako u `test_skills.py`. Každý test si staví
vlastní dočasný repozitář a přesměrovaný HOME, takže nesahá na skutečné souhlasy
ani na skutečný běhový stav.
"""
import json
import os
import pty
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOOK = ROOT / "verify.sh"

# Návratové kódy Stop hooku. Rozdíl mezi 1 a 2 je celý smysl téhle vrstvy:
# při 2 dostane výstup MODEL jako pokyn, při 1 jen člověk do transkriptu.
BLOKUJE = 2   # model to uvidí a má na to reagovat
MLCI = 1      # jen pro člověka; model o tom neví
PUSTI = 0     # v pořádku, nebo se vědomě nic nespouští


def vydej_souhlas(cesta, home):
    """Spustí `--allow` přes pseudoterminál a odpoví „ano“.

    Skript souhlas úmyslně nevydá procesu bez terminálu: deny pravidla na něj
    porovnávají text příkazu, takže je obejde volání přes interpret i složený
    příkaz s přesměrováním. Terminál je to jediné, co běžící nástroj nemá.

    Test tu podmínku proto nesmí obcházet proměnnou prostředí – tím by z ní
    udělal vypínač. Místo toho si terminál opatří: `pty.openpty()` dá pár, jehož
    slave konec je skutečné tty, takže `[ -t 0 ]` ve skriptu platí.
    """
    master, slave = pty.openpty()
    try:
        os.write(master, b"ano\n")
        env = dict(os.environ, HOME=str(home))
        env.pop("XDG_STATE_HOME", None)
        env.pop("CLAUDE_NO_VERIFY", None)
        return subprocess.run([str(HOOK), "--allow", str(cesta)], stdin=slave,
                              capture_output=True, text=True, env=env, check=False)
    finally:
        os.close(master)
        os.close(slave)


def git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args],
                          capture_output=True, text=True, check=False)


class PrubeznaKontrola(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="verify-test-"))
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
        """Napíše CLAUDE.md se sekcí ## Kontrakt příkazů a commitne ho."""
        radky = "\n".join(f"- {k}: {v}" for k, v in prikazy.items())
        (self.repo / "CLAUDE.md").write_text(f"# Test\n\n## Kontrakt příkazů\n\n{radky}\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "kontrakt")

    def allow(self, cesta=None):
        return vydej_souhlas(cesta or self.repo, self.home)

    def spust(self, argv=None, vstup="", cwd=None, stop_hook_active=False):
        env = dict(os.environ, HOME=str(self.home))
        env.pop("XDG_STATE_HOME", None)
        env.pop("CLAUDE_NO_VERIFY", None)
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

        Klíč podle cesty by znamenal nový souhlas na každé nové větvi – tedy kontrolu
        vypnutou právě tam, kde se pracuje, a funkční na main, kde se nepracuje.
        """
        self.kontrakt(typecheck="-", lint="-", test="true")
        self.allow()
        vetev = self.tmp / "feat"
        git(self.repo, "worktree", "add", "-q", str(vetev), "-b", "feat")
        r = self.spust(cwd=vetev)
        self.assertEqual(r.returncode, PUSTI,
                         f"na nové větvi kontrola neběžela: {r.stderr}")

    def test_souhlas_prezije_symlink_v_ceste(self):
        """Souhlas vydaný přes symlink se musí potkat s během, který ho má rozřešený.

        Na macOS je /var symlink na /private/var, takže stačí projekt v dočasném
        adresáři – ale platí to pro každý symlinkovaný adresář s projekty. Bez
        kanonizace obou stran kontrola mlčky neběží a jediné, co uživatel dostane,
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

    def test_padajici_kontrola_blokuje_a_mluvi_k_modelu(self):
        self.kontrakt(typecheck="-", lint="-", test="false")
        self.allow()
        r = self.spust()
        self.assertEqual(r.returncode, BLOKUJE)
        self.assertIn("není zelená", r.stderr)

    def test_druhy_pokus_pusti_dal_ale_neztichne(self):
        """Kontrola zastaví jednou, ne napořád – ale model se to musí dozvědět.

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

    def test_chybejici_nastroj_neni_padajici_kontrola(self):
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

    def test_vypnuta_kontrola_se_hlasi(self):
        """Vypnutá kontrola, o které se mlčí, je horší než chybějící kontrola."""
        self.kontrakt(typecheck="-", lint="-", test="false")
        self.allow()
        (self.repo / ".claude").mkdir(exist_ok=True)
        (self.repo / ".claude/no-verify").touch()
        r = self.spust()
        self.assertEqual(r.returncode, PUSTI)
        self.assertIn("vypnutá souborem", r.stderr)

    # --- otisk stavu -------------------------------------------------------

    def test_otisk_vidi_do_neverzovaneho_adresare(self):
        """Bez -uall je celý nový adresář jedinou položkou "?? dir/".

        Test [ -f ] na ní neprojde, obsah se do otisku nedostane – a protože nová
        feature skoro vždycky začíná novým adresářem, byla by kontrola mrtvá právě
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
        by po každé odpovědi běžící npm test. Je to zároveň cesta, kudy jde do
        repozitáře propašovat příkaz schovaný jako dokumentace.
        """
        (self.repo / "CLAUDE.md").write_text(
            "# Test\n\nKontrakt nemáme. Formát vypadá takhle:\n\n"
            "```markdown\n## Kontrakt příkazů\n\n- test: touch NESMI-VZNIKNOUT\n```\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "dokumentace")
        r = self.allow()
        self.assertNotEqual(r.returncode, 0, "--allow přijal ukázku v bloku kódu jako kontrakt")
        self.spust()
        self.assertFalse((self.repo / "NESMI-VZNIKNOUT").exists(),
                         "hook spustil příkaz z bloku kódu v dokumentaci")

    def test_kontrakt_v_html_komentari_neni_kontrakt(self):
        """HTML komentář nevidí žádný vykreslený Markdown – ale skript ho četl.

        Sekce se bere od prvního výskytu, takže schovaná kopie nad tou skutečnou
        ji celou zastínila a spustil se cizí příkaz. Lidská revize to nemá jak
        zachytit: v GitHubu, v náhledu ani v diffu PR ten řádek není vidět.

        V souboru je schválně JEN ta schovaná sekce. S druhou, skutečnou, by test
        prošel i s původním md_body – zachytila by ho kontrola na dvě sekce, a
        tenhle test by pak neměřil nic. Ověřeno mutací.
        """
        (self.repo / "CLAUDE.md").write_text(
            "# Test\n\nKontrakt nemáme.\n\n"
            "<!--\n## Kontrakt příkazů\n\n- test: touch NESMI-VZNIKNOUT\n-->\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "skryty kontrakt")
        r = self.allow()
        self.assertNotEqual(r.returncode, 0,
                            "--allow přijal sekci schovanou v HTML komentáři jako kontrakt")
        self.spust()
        self.assertFalse((self.repo / "NESMI-VZNIKNOUT").exists(),
                         "hook spustil příkaz schovaný v HTML komentáři")

    def test_upovidany_uspesny_krok_neni_padajici_kontrola(self):
        """Uříznutý výstup neznamená, že kód je špatně.

        Kroky běží rourou do `head -c`, které drží výstup v mezích, aby
        smyčkující příkaz nezaplnil disk. Jenže tím zavře rouru, krok dostane
        SIGPIPE a nedoběhne – takže jeho návratový kód o výsledku nevypovídá.
        Dřív se to počítalo jako padající kontrola a hook blokoval odpověď kvůli
        příkazu, který sám o sobě končí nulou.

        Pozná se to velikostí souboru, ne kódem: `cat` vrátí 141, ale Python
        zachytí BrokenPipeError a končí 120. První verze opravy hlídala 141 a
        kvůli tomu nefungovala.
        """
        self.kontrakt(typecheck="-", lint="-",
                      test="python3 -c \"print('x'*300000)\"")
        self.allow()
        r = self.spust()
        self.assertNotEqual(r.returncode, BLOKUJE,
                            "upovídaný úspěšný krok se hlásí jako padající kontrola")
        self.assertIn("není známo", r.stderr)
        self.assertIn("Není to nález v kódu", r.stderr)

    def test_padajici_krok_blokuje_i_po_oprave_upovidanosti(self):
        """Protějšek testu výš: ať se z opravy nestane díra.

        Kdyby se podmínka na uříznutý výstup napsala moc široce, spolkla by
        i skutečné selhání a hook by přestal blokovat cokoliv.
        """
        self.kontrakt(typecheck="-", lint="-", test="false")
        self.allow()
        self.assertEqual(self.spust().returncode, BLOKUJE,
                         "padající test přestal blokovat")

    def test_nedovreny_plot_nevypne_kontrolu_mlcky(self):
        """Vypnutá kontrola, o které nikdo neví, je horší než žádná.

        md_body přepíná stav na každém ``` – lichý počet ohraničení nad sekcí tedy
        udělá z celého zbytku souboru blok kódu, kontrakt se nenajde a hook
        skončí nula. To je nerozlišitelné od „projekt kontrakt nemá", takže
        kontrola, která předtím blokovala padající testy, od té chvíle mlčky
        nespouští nic. Rozdíl se pozná tím, že sekce v syrovém souboru je.
        """
        (self.repo / "CLAUDE.md").write_text(
            "# Test\n\n```bash\nneuzavrene ohraniceni\n\n## Kontrakt příkazů\n\n"
            "- typecheck: -\n- lint: -\n- test: false\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "neuzavrene ohraniceni")
        self.allow()
        r = self.spust()
        self.assertEqual(r.returncode, BLOKUJE, "nečitelný kontrakt kontrolu vypnul mlčky")
        self.assertIn("nejde přečíst", r.stderr)
        self.assertIn("blok kódu", r.stderr,
                      "hláška neříká, kterou z možných příčin hook vidí")

    def test_hlaska_nesvali_na_soubor_chybu_hooku(self):
        """Sekce je čitelná, hledání ji přesto nenašlo – hláška musí ukázat na hook.

        Dřív jmenovala jedinou příčinu, která byla známá v době jejího vzniku
        (neuzavřené ohraničení), takže poslala hledání do souboru i tam, kde žádné ohraničení
        není. Doloženo 14. 9. 2026: SIGPIPE ve `find_contract` se takhle
        diagnostikoval jako vada Markdownu a hledal se v něm.

        Scénář se vyrábí mutací hooku, protože jinak nejde nastat – a právě proto
        by bez tohohle testu diagnostika mohla tiše zůstat zavádějící."""
        (self.repo / "CLAUDE.md").write_text(
            "# Test\n\n## Kontrakt příkazů\n\n- test: false\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "kontrakt")

        rozbity = self.tmp / "verify-rozbity.sh"
        text = Path(HOOK).read_text(encoding="utf-8")
        mutace = text.replace("find_contract() {", "find_contract() { return 1;", 1)
        self.assertNotEqual(text, mutace, "find_contract se přejmenovala")
        rozbity.write_text(mutace, encoding="utf-8")
        rozbity.chmod(0o755)

        env = dict(os.environ, HOME=str(self.home))
        env.pop("XDG_STATE_HOME", None)
        env.pop("CLAUDE_NO_VERIFY", None)
        vstup = json.dumps({"session_id": "s1", "cwd": str(self.repo),
                            "stop_hook_active": False})
        r = subprocess.run(["bash", str(rozbity)], input=vstup,
                           capture_output=True, text=True, env=env)
        self.assertIn("chyba ve verify.sh", r.stderr,
                      "hláška svaluje chybu hooku na prověřovaný soubor")

    def test_projekt_bez_kontraktu_dal_mlci(self):
        """Protějšek testu výš: chybějící kontrakt není chyba a nesmí se hlásit.

        Bez něj by oprava neuzavřeného ohraničení mohla začít otravovat v každém
        repozitáři, který kontrakt prostě nemá.
        """
        (self.repo / "CLAUDE.md").write_text("# Test\n\nŽádný kontrakt tu není.\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "bez kontraktu")
        r = self.spust()
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stderr.strip(), "", "projekt bez kontraktu nesmí nic hlásit")

    def test_dva_kontrakty_se_odmitnou(self):
        """Dvě sekce téhož jména jsou signál, ne konfigurace.

        Bere se první, takže druhá je tiše mrtvá – a kdo přidal svou nad tu
        původní, vyměnil spouštěné příkazy, aniž to bylo na první pohled poznat.
        Zastínit jde i bez komentáře, proto to nestačí řešit v md_body.
        """
        (self.repo / "CLAUDE.md").write_text(
            "# Test\n\n## Kontrakt příkazů\n\n- test: touch NESMI-VZNIKNOUT\n\n"
            "## Jiná sekce\n\ntext\n\n"
            "## Kontrakt příkazů\n\n- typecheck: -\n- lint: -\n- test: true\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "dva kontrakty")
        self.allow()
        self.spust()
        self.assertFalse((self.repo / "NESMI-VZNIKNOUT").exists(),
                         "hook spustil příkaz z první ze dvou sekcí místo odmítnutí")

    def test_kontrakt_v_claude_podadresari(self):
        """Druhé z povolených umístění – kořenový CLAUDE.md bývá obsazený."""
        (self.repo / ".claude").mkdir()
        (self.repo / ".claude/CLAUDE.md").write_text(
            "# Test\n\n## Kontrakt příkazů\n\n- typecheck: -\n- lint: -\n- test: test -d .claude\n")
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
        """Cesta ven z projektu se odmítne a model se to musí dozvědět.

        BLOKUJE, ne MLCI: kontrola kvůli tomu vůbec neproběhla, a při exit 1 by
        stderr viděl jen člověk. Model by pak nechal svoje „hotovo" stát nad
        stavem, který branou neprošel. Napodruhé (stop_hook_active) se vrací
        MLCI, ať se to nezacyklí – tohle si model sám neopraví.
        """
        self.kontrakt(typecheck="-", lint="-", test="true", cwd="../jinam")
        self.allow()
        r = self.spust()
        self.assertEqual(r.returncode, BLOKUJE)
        self.assertIn("cwd", r.stderr)
        r2 = self.spust(stop_hook_active=True)
        self.assertEqual(r2.returncode, MLCI, "druhý pokus se musí vzdát, ne zacyklit")

    # --- souběh ------------------------------------------------------------

    def test_zamek_zabrani_soubeznemu_behu(self):
        """Dvě session nad jedním stromem jinak pustí testy současně."""
        self.kontrakt(typecheck="-", lint="-", test="false")
        self.allow()
        stav = self.home / ".local/state/claude-verify/runs"
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


class SouhlasVydavaClovek(unittest.TestCase):
    """`--allow` nesmí projít procesu, který nemá terminál.

    Souhlas je jediná věc mezi cizím repozitářem a spuštěním jeho příkazů. Deny
    pravidla v `settings.json` ho chránit neumějí: porovnávají text příkazu,
    takže volání přes `python3 -c` nebo `node -e` jméno skriptu do příkazové řádky
    vůbec nedostane. 14. 9. 2026 se navíc ukázalo, že neplatí ani v přímém tvaru,
    je-li volání součástí složeného příkazu – doloženo tím, že si agent souhlas
    omylem vydal sám uprostřed revize.

    Terminál je to, co proces nemá a nemůže si opatřit obejitím vzoru.
    """

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="tty-test-"))
        self.home = self.tmp / "home"
        self.home.mkdir()
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q", ".")
        (self.repo / "CLAUDE.md").write_text(
            "# T\n\n## Kontrakt příkazů\n\n- test: true\n", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def bez_terminalu(self, vstup=subprocess.DEVNULL):
        env = dict(os.environ, HOME=str(self.home))
        env.pop("XDG_STATE_HOME", None)
        return subprocess.run([str(HOOK), "--allow", str(self.repo)], stdin=vstup,
                              capture_output=True, text=True, env=env, check=False)

    def souhlasy(self):
        d = self.home / ".local/state/claude-verify/allowed"
        return list(d.glob("*")) if d.exists() else []

    def test_vypis_rozlisuje_pomlcku_od_dokumentace(self):
        """Klíč s pomlčkou je rozhodnutí „neaplikuje se“, klíč s příkazem mimo
        typecheck/lint/test je příkaz pro jiný krok cyklu. Výpis je sléval do
        jedné věty „jen dokumentace v kontraktu“, takže vědomé rozhodnutí
        vypadalo jako poznámka – a to je text, kterým člověk schvaluje spouštění
        kódu z repozitáře."""
        (self.repo / "CLAUDE.md").write_text(
            "# T\n\n## Kontrakt příkazů\n\n- test: true\n- dev: npm run dev\n- build: -\n",
            encoding="utf-8")
        v = vydej_souhlas(self.repo, self.home)
        self.assertEqual(v.returncode, 0, v.stderr)
        self.assertRegex(v.stdout, r"Nespouští: dev")
        self.assertRegex(v.stdout, r"Neaplikuje se: build")

    def test_bez_terminalu_souhlas_nevznikne(self):
        v = self.bez_terminalu()
        self.assertNotEqual(v.returncode, 0)
        self.assertEqual(self.souhlasy(), [], "souhlas vznikl procesu bez terminálu")

    def test_ano_na_stdin_z_roury_nestaci(self):
        """Roura není terminál, i když v ní stojí správná odpověď.

        Jinak by stačilo `echo ano | verify.sh --allow .` a pojistka by byla
        k ničemu – přesně tímhle tvarem ji nástroj obejde nejsnáz.
        """
        p = subprocess.Popen(["echo", "ano"], stdout=subprocess.PIPE)
        v = self.bez_terminalu(vstup=p.stdout)
        p.wait()
        self.assertNotEqual(v.returncode, 0)
        self.assertEqual(self.souhlasy(), [], "souhlas vznikl z roury")

    def test_s_terminalem_a_potvrzenim_souhlas_vznikne(self):
        """Propustit, co propustit má: člověk u terminálu, který napíše „ano“."""
        v = vydej_souhlas(self.repo, self.home)
        self.assertEqual(v.returncode, 0, v.stderr)
        self.assertEqual(len(self.souhlasy()), 1)

    def test_jina_odpoved_souhlas_nevyda(self):
        master, slave = pty.openpty()
        try:
            os.write(master, b"jo\n")
            env = dict(os.environ, HOME=str(self.home))
            env.pop("XDG_STATE_HOME", None)
            v = subprocess.run([str(HOOK), "--allow", str(self.repo)], stdin=slave,
                               capture_output=True, text=True, env=env, check=False)
        finally:
            os.close(master); os.close(slave)
        self.assertNotEqual(v.returncode, 0)
        self.assertEqual(self.souhlasy(), [], "souhlas vznikl bez slova „ano“")


class SouhlasPlatiProKontrakt(unittest.TestCase):
    """Souhlas pokrývá repozitář, ale ne cokoliv, co se v něm najde.

    Klíč souhlasu je odvozený ze sdíleného `.git`, aby platil i pro worktree
    ostatních větví. Bez dalších pojistek to ale znamenalo, že si **jakýkoliv
    podadresář** mohl přinést vlastní `CLAUDE.md` a jeho příkazy se spustily bez
    dotazu – rozbalený cizí projekt ve `vendor/`, stažený tarball, obnovená
    záloha. Ověřeno v `/review full` (14. 9. 2026): neverzovaný soubor stačil.

    Druhá cesta k témuž: `rm -rf projekt && git clone cizi projekt` zdědil celý
    souhlas, protože klíč se počítá z cesty ke `.git`.
    """

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="souhlas-test-"))
        self.home = self.tmp / "home"
        self.home.mkdir()
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q", ".")
        git(self.repo, "config", "user.email", "t@t")
        git(self.repo, "config", "user.name", "t")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def kontrakt(self, kam, prikaz):
        kam.mkdir(parents=True, exist_ok=True)
        (kam / "CLAUDE.md").write_text(
            f"# T\n\n## Kontrakt příkazů\n\n- test: {prikaz}\n", encoding="utf-8")

    def bezi(self, cwd):
        env = dict(os.environ, HOME=str(self.home))
        env.pop("XDG_STATE_HOME", None)
        env.pop("CLAUDE_NO_VERIFY", None)
        vstup = json.dumps({"session_id": "s1", "cwd": str(cwd),
                            "transcript_path": "", "stop_hook_active": False})
        return subprocess.run([str(HOOK)], input=vstup, capture_output=True,
                              text=True, env=env, check=False)

    def allow(self, kde):
        return vydej_souhlas(kde, self.home)

    def test_podadresar_s_vlastnim_kontraktem_se_nespusti(self):
        stopa = self.tmp / "NESMI-VZNIKNOUT"
        self.kontrakt(self.repo, "true")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "init")
        self.assertEqual(self.allow(self.repo).returncode, 0)
        self.kontrakt(self.repo / "vendor" / "cizi", f"touch {stopa}")
        v = self.bezi(self.repo / "vendor" / "cizi")
        self.assertFalse(stopa.exists(), "příkaz z podadresáře se spustil pod souhlasem pro repozitář")
        self.assertIn("podadresáři", v.stderr)

    def test_zmena_textu_pod_kontraktem_souhlas_neruzi(self):
        """Souhlas se vydává na příkazy, ne na odstavce kolem nich.

        Otisk se původně počítal z celé sekce, takže přepsaný komentář pod
        seznamem zablokoval kontrolu, přestože se žádný příkaz nezměnil –
        doloženo hodinu po zavedení té pojistky. Falešný poplach je u vynucovací
        vrstvy horší směr selhání než propuštěná chyba: vede k jejímu vypnutí.
        """
        (self.repo / "CLAUDE.md").write_text(
            "# T\n\n## Kontrakt příkazů\n\n- test: true\n\nPůvodní vysvětlení.\n", encoding="utf-8")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "init")
        self.assertEqual(self.allow(self.repo).returncode, 0)
        (self.repo / "CLAUDE.md").write_text(
            "# T\n\n## Kontrakt příkazů\n\n- test: true\n\nPřepsané vysvětlení, delší a jiné.\n",
            encoding="utf-8")
        v = self.bezi(self.repo)
        self.assertNotIn("změnil", v.stderr, "změna textu pod kontraktem si vyžádala nový souhlas")

    def test_zmeneny_kontrakt_se_nespusti(self):
        """Souhlas se vydává na konkrétní kontrakt, ne na repozitář navždy."""
        stopa = self.tmp / "NESMI-VZNIKNOUT"
        self.kontrakt(self.repo, "true")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "init")
        self.assertEqual(self.allow(self.repo).returncode, 0)
        self.kontrakt(self.repo, f"touch {stopa}")
        v = self.bezi(self.repo)
        self.assertFalse(stopa.exists(), "spustil se příkaz, který nikdo neodsouhlasil")
        self.assertIn("změnil", v.stderr)

    def test_souhlas_ve_starem_formatu_neplati(self):
        """Souhlas bez otisku se nedá ověřit, takže se nepoužije – a řekne se to.

        Tichý degradovaný režim by z téhle opravy udělal dekoraci: běželo by se
        dál pod souhlasem, o kterém není jisté, na co byl vydaný.
        """
        self.kontrakt(self.repo, "true")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "init")
        self.assertEqual(self.allow(self.repo).returncode, 0)
        soubor = next((self.home / ".local/state/claude-verify/allowed").glob("*"))
        soubor.write_text(f"{self.repo}\n")          # starý jednořádkový formát
        v = self.bezi(self.repo)
        self.assertIn("starém formátu", v.stderr)
        self.assertEqual(v.returncode, 2)

    def test_worktree_jine_vetve_souhlas_dedi(self):
        """Pojistka nesmí rozbít to, kvůli čemu se klíčuje sdíleným `.git`."""
        self.kontrakt(self.repo, "true")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "init")
        self.assertEqual(self.allow(self.repo).returncode, 0)
        wt = self.tmp / "wt"
        self.assertEqual(git(self.repo, "worktree", "add", "-q", str(wt), "-b", "feat").returncode, 0)
        v = self.bezi(wt)
        self.assertNotIn("není vydaný souhlas", v.stderr)
        self.assertNotIn("podadresáři", v.stderr)


class ParserTelaMarkdownu(unittest.TestCase):
    """`md_body()` musí číst Markdown tak, jak ho čte člověk v náhledu.

    Rozejde-li se s ním, vznikne nejhorší možná třída vady: soubor se vykreslí
    jedním způsobem a skript ho přečte jiným, takže rozdíl nejde vidět ani
    v diffu pull requestu. Obojí níž nastalo doopravdy (`/review full`, 14. 9. 2026)
    a hook v obou případech spustil podvržený příkaz a napsal „průběžná kontrola
    prošla“.

    Pojistky na dvě sekce a na neuzavřené ohraničení tuhle třídu nezachytí z principu –
    obě počítají z výstupu téhle funkce, takže vidí totéž, co ona.
    """

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="parser-test-"))
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q", ".")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def contract(self, obsah):
        (self.repo / "CLAUDE.md").write_text(obsah, encoding="utf-8")
        return subprocess.run([str(HOOK), "--contract", str(self.repo)],
                              capture_output=True, text=True, check=False,
                              stdin=subprocess.DEVNULL)

    def test_ctyrznakovy_plot_neobrati_polaritu(self):
        """Ukázka kontraktu se sází do ````markdown, aby šel uvnitř ukázat ```.

        Překlápění na každém ohraničení bez ohledu na délku tu obrátilo polaritu:
        podvržená sekce uvnitř ukázky se stala tělem a skutečný kontrakt pod ní
        zmizel jako blok kódu.
        """
        v = self.contract("# T\n\nUkázka:\n\n````markdown\n```\n## Kontrakt příkazů\n\n"
                          "- test: echo PODVRZENY\n```\n````\n\n"
                          "## Kontrakt příkazů\n\n- test: echo PRAVY\n")
        self.assertEqual(v.returncode, 0, v.stderr)
        self.assertIn("echo PRAVY", v.stdout)
        self.assertNotIn("PODVRZENY", v.stdout)

    def test_tildovy_plot_uvnitr_backtickoveho_neni_plot(self):
        """Uvnitř ```-bloku je ~~~ obyčejný text, ne zavírací ohraničení."""
        v = self.contract("# T\n\n```\n~~~\n## Kontrakt příkazů\n- test: echo PODVRZENY\n"
                          "~~~\n```\n\n## Kontrakt příkazů\n\n- test: echo PRAVY\n")
        self.assertIn("echo PRAVY", v.stdout)
        self.assertNotIn("PODVRZENY", v.stdout)

    def test_ceska_pomlcka_v_komentari_nespolkne_zbytek_souboru(self):
        """Komentář s `--` uvnitř je běžná česká poznámka, ne konec komentáře.

        Výraz, který ho nechytil, posílal takový řádek do víceřádkové větve, a ta
        zahodila všechno až po další `-->` – tedy i skutečný kontrakt.
        """
        v = self.contract("# T\n\n<!-- pozn. -- viz níž -->\n\n"
                          "## Kontrakt příkazů\n\n- test: echo PRAVY\n")
        self.assertEqual(v.returncode, 0, v.stderr)
        self.assertIn("echo PRAVY", v.stdout)

    def test_komentar_pres_vic_radku_konci_na_prvnim_zavreni(self):
        v = self.contract("# T\n\n<!--\n## Kontrakt příkazů\n- test: echo PODVRZENY\n-->\n\n"
                          "## Kontrakt příkazů\n\n- test: echo PRAVY\n")
        self.assertIn("echo PRAVY", v.stdout)
        self.assertNotIn("PODVRZENY", v.stdout)

    def test_dva_komentare_na_jednom_radku(self):
        """Stavový automat musí zvládnout víc komentářů v jednom řádku,
        jinak by druhý otevřel stav, který nikdo nezavře."""
        v = self.contract("# T\n\n<!-- a --> text <!-- b -->\n\n"
                          "## Kontrakt příkazů\n\n- test: echo PRAVY\n")
        self.assertIn("echo PRAVY", v.stdout)


class VypisKontraktu(unittest.TestCase):
    """`--contract` vypisuje kontrakt pro CI, která pouští tytéž kroky jinde.

    Existuje proto, aby nemusela vzniknout druhá implementace parseru. Ta tu do
    13. 9. 2026 byla (v `.github/workflows/verify.yml`) a rozešla se s touhle ve
    třech vlastnostech naráz: nefiltrovala HTML komentáře, neměla pojistku proti
    dvěma sekcím téhož jména a neznala klíč `cwd`. Testy tu proto hlídají právě
    ty tři vlastnosti – jsou to místa, kde se dvě implementace rozešly doopravdy,
    ne kde by se rozejít mohly.
    """

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="contract-test-"))
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q", ".")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def contract(self, obsah):
        (self.repo / "CLAUDE.md").write_text(obsah, encoding="utf-8")
        return subprocess.run([str(HOOK), "--contract", str(self.repo)],
                              capture_output=True, text=True, check=False,
                              stdin=subprocess.DEVNULL)

    def test_vypise_klic_a_prikaz_oddelene_tabulatorem(self):
        v = self.contract("# T\n\n## Kontrakt příkazů\n\n- test: echo ahoj\n")
        self.assertEqual(v.returncode, 0, v.stderr)
        self.assertEqual(v.stdout.strip(), "test\techo ahoj")

    def test_zakomentovana_sekce_se_nepocita(self):
        """HTML komentář ve vykresleném Markdownu ani v náhledu PR není vidět,
        takže sekce schovaná nad tou pravou je cesta, jak vyměnit spouštěné
        příkazy a nechat diff vypadat jako dokumentaci."""
        v = self.contract("# T\n\n<!--\n## Kontrakt příkazů\n\n- test: echo PODVRZENY\n-->\n"
                          "\n## Kontrakt příkazů\n\n- test: echo PRAVY\n")
        self.assertEqual(v.returncode, 0, v.stderr)
        self.assertIn("echo PRAVY", v.stdout)
        self.assertNotIn("PODVRZENY", v.stdout)

    def test_dve_sekce_tehoz_jmena_vypis_odmitnou(self):
        """Stejná pojistka jako u běhu hooku: druhá sekce je tiše mrtvá."""
        v = self.contract("# T\n\n## Kontrakt příkazů\n\n- test: echo PRVNI\n"
                          "\n## Jiné\n\n## Kontrakt příkazů\n\n- test: echo DRUHY\n")
        self.assertNotEqual(v.returncode, 0)
        self.assertNotIn("echo PRVNI", v.stdout)

    def test_ukazka_v_bloku_kodu_neni_kontrakt(self):
        v = self.contract("# T\n\nFormát vypadá takhle:\n\n```markdown\n"
                          "## Kontrakt příkazů\n\n- test: echo UKAZKA\n```\n")
        self.assertNotIn("UKAZKA", v.stdout)

    def test_klic_cwd_se_vypise(self):
        """CI podle něj mění adresář; bez něj by pouštěla příkazy jinde
        než průběžná kontrola."""
        v = self.contract("# T\n\n## Kontrakt příkazů\n\n- cwd: main\n- test: echo ahoj\n")
        self.assertIn("cwd\tmain", v.stdout)

    def test_pomlcka_se_vypise_jak_je(self):
        """Rozhodnutí „vědomě se neaplikuje“ musí dojít až k tomu, kdo spouští –
        jinak by ho CI hlásila jako chybějící klíč, tedy jako díru."""
        v = self.contract("# T\n\n## Kontrakt příkazů\n\n- build: -\n- test: echo ahoj\n")
        self.assertIn("build\t-", v.stdout)

    def test_projekt_bez_kontraktu_skonci_chybou(self):
        v = self.contract("# T\n\nŽádný kontrakt tu není.\n")
        self.assertNotEqual(v.returncode, 0)

    def test_dlouhy_text_pod_kontraktem_hledani_neshodi(self):
        """Sekce se musí najít i tehdy, když je za ní dlouhý text.

        `find_contract` hledala sekci přes `md_body ... | grep -q`, jenže `-q`
        skončí po prvním zásahu a awk uvnitř `md_body` pak dostane SIGPIPE. Se
        `set -o pipefail` propadl celý pipeline jako neúspěch, takže se kontrakt
        „nenašel“ a kontrola se odmítla spustit. Rozhodovala přitom **délka textu
        za sekcí**: dokud se zbytek souboru vešel do bufferu roury, awk stihl
        dopsat a všechno fungovalo. Doloženo 14. 9. 2026 v tomhle repozitáři –
        shodil to jeden přidaný odstavec pod kontraktem.

        Sto tisíc znaků je nad běžný buffer roury (64 KB), takže scénář nastane
        spolehlivě i tam, kde má systém buffer větší než macOS."""
        vata = "Vysvětlující odstavec pod kontraktem.\n\n" * 3000
        self.assertGreater(len(vata), 100_000)
        v = self.contract("# T\n\n## Kontrakt příkazů\n\n- test: echo ahoj\n\n" + vata)
        self.assertEqual(v.returncode, 0, v.stderr)
        self.assertIn("test\techo ahoj", v.stdout)

    def test_nic_nespousti(self):
        """--contract jen čte. Kdyby spouštěl, obešel by souhlas, který je
        u příkazů z repozitáře celá pojistka."""
        stopa = self.tmp / "NESMI-VZNIKNOUT"
        self.contract(f"# T\n\n## Kontrakt příkazů\n\n- test: touch {stopa}\n")
        self.assertFalse(stopa.exists(), "--contract spustil příkaz z kontraktu")


if __name__ == "__main__":
    unittest.main()
