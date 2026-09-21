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
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMMIT_MSG_HOOK = ROOT / "githooks" / "commit-msg"

REJECT = 1
ALLOW = 0


def git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args],
                          capture_output=True, text=True, check=False)


class MergeCommitMessage(unittest.TestCase):
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

    def run_commit_msg_hook(self, message):
        """Zavolá hook nad souborem se zprávou, jak to dělá git."""
        msg_file = self.repo / ".git" / "COMMIT_EDITMSG"
        msg_file.write_text(message)
        return subprocess.run([str(COMMIT_MSG_HOOK), str(msg_file)], cwd=self.repo,
                              capture_output=True, text=True, check=False)

    def checkout_branch(self, name):
        git(self.repo, "checkout", "-q", "-b", name)

    # --- co se má odmítnout ------------------------------------------------

    def test_default_english_message_on_main_rejected(self):
        v = self.run_commit_msg_hook("Merge branch 'feat/platby'\n")
        self.assertEqual(v.returncode, REJECT)
        self.assertIn("WORKTREE.md", v.stderr)

    def test_default_czech_message_on_main_rejected(self):
        self.assertEqual(self.run_commit_msg_hook("Merge větve docs/znamky\n").returncode, REJECT)

    def test_comments_above_message_do_not_confuse_hook(self):
        """Git dává do COMMIT_EDITMSG vysvětlující komentáře; první *neprázdný
        nekomentářový* řádek je ta zpráva, a hook musí hledat ten."""
        v = self.run_commit_msg_hook("\n# Please enter a commit message\n\nMerge branch 'feat/x'\n")
        self.assertEqual(v.returncode, REJECT)

    def test_real_merge_on_main_is_stopped(self):
        """Integračně: hook musí sedět i skutečnému `git merge`, ne jen přímému
        volání – merge commit vzniká jinou cestou než `git commit`."""
        self.checkout_branch("feat/x")
        (self.repo / "b.txt").write_text("b\n")
        git(self.repo, "add", "b.txt")
        git(self.repo, "commit", "-qm", "prace")
        git(self.repo, "checkout", "-q", "main")
        git(self.repo, "config", "core.hooksPath", str(COMMIT_MSG_HOOK.parent))
        v = git(self.repo, "merge", "--no-ff", "feat/x")
        self.assertNotEqual(v.returncode, 0)
        self.assertEqual(git(self.repo, "log", "--oneline").stdout.count("\n"), 1)

    def test_all_default_git_forms_rejected(self):
        """Git negeneruje jen "Merge branch ".

        `git merge origin/vetev` dá "Merge remote-tracking branch" – tedy běžná
        cesta, jak se dokončuje větev pushnutá odjinud. Octopus merge dá "Merge
        branches", merge tagu "Merge tag". Všechny nesou jen jméno reference,
        takže v `git log --first-parent` neřeknou nic; vzor jen na první z nich
        propouštěl celou tuhle třídu a žádný test o ní nevěděl.
        """
        for message in ("Merge remote-tracking branch 'origin/feat/x'",
                       "Merge branches 'feat/a' and 'feat/b'",
                       "Merge tag 'v1.2.0'",
                       "Merge commit '9fceb02'",
                       "Merge branch 'feat/platby' into main",
                       "Squashed commit of the following:"):
            with self.subTest(message=message):
                self.assertEqual(self.run_commit_msg_hook(message + "\n").returncode, REJECT)

    def test_indented_first_line_does_not_bypass_pattern(self):
        """`case` je kotvený na začátek řetězce, takže mezera před zprávou
        by stačila k obejití celé kontroly."""
        self.assertEqual(self.run_commit_msg_hook("   Merge branch 'feat/x'\n").returncode, REJECT)

    def test_real_remote_tracking_merge_is_stopped(self):
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
        git(self.repo, "config", "core.hooksPath", str(COMMIT_MSG_HOOK.parent))
        v = git(self.repo, "merge", "--no-ff", "origin/feat/x")
        self.assertNotEqual(v.returncode, 0, "merge přes origin/… prošel bez zastavení")
        self.assertEqual(git(self.repo, "log", "--oneline").stdout.count("\n"), 1)

    # --- co musí projít ----------------------------------------------------

    def test_custom_message_passes(self):
        self.assertEqual(self.run_commit_msg_hook("Zaveď platby kartou\n").returncode, ALLOW)

    def test_merge_into_feature_branch_passes(self):
        """Aktualizace větve z main je běžný provoz a její defaultní zpráva
        do historie main nikdy nedoteče – hlídá se jen hlavní větev."""
        self.checkout_branch("feat/platby")
        self.assertEqual(self.run_commit_msg_hook("Merge branch 'main' into feat/platby\n").returncode, ALLOW)

    def test_merge_after_pull_of_same_branch_passes(self):
        """`git pull` nad toutéž větví je synchronizace, ne dokončení práce,
        a blokovat ji by znamenalo blokovat pull."""
        v = self.run_commit_msg_hook("Merge branch 'main' of https://github.com/x/y\n")
        self.assertEqual(v.returncode, ALLOW)

    def test_pull_of_other_branch_on_main_rejected(self):
        """`git pull origin feat/z` na main je dokončení větve, ne synchronizace.

        Výjimka pro pull stála jen na výskytu ` of ` kdekoliv v prvním řádku, takže
        tuhle cestu propouštěla – a je to běžný způsob, jak se dokončuje větev
        pushnutá odjinud nebo z pull requestu. Dvě slova navíc stačila i k obejití
        (`Merge branch 'feat/x' of course`).
        """
        for message in ("Merge branch 'feat/z' of https://github.com/x/y",
                       "Merge branch 'feat/x' of course",
                       "Merge branch 'feat/z' of /tmp/remote"):
            with self.subTest(message=message):
                self.assertEqual(self.run_commit_msg_hook(message + "\n").returncode, REJECT)

    def test_message_mentioning_merge_passes(self):
        self.assertEqual(self.run_commit_msg_hook("Oprav merge větve v dokumentaci\n").returncode, ALLOW)

    # --- delegace na lokální hook -----------------------------------------

    def local_hook(self, body):
        path = self.repo / ".git" / "hooks" / "commit-msg"
        path.parent.mkdir(exist_ok=True)
        path.write_text(body)
        path.chmod(0o755)
        return path

    def test_local_hook_is_called(self):
        trace = self.repo / "trace"
        self.local_hook(f"#!/bin/sh\ntouch {trace}\nexit 0\n")
        self.assertEqual(self.run_commit_msg_hook("Zaveď platby kartou\n").returncode, ALLOW)
        self.assertTrue(trace.exists(), "lokální hook repozitáře se nespustil")

    def test_local_hook_rejection_stops(self):
        self.local_hook("#!/bin/sh\necho lokalni namitka >&2\nexit 3\n")
        v = self.run_commit_msg_hook("Zaveď platby kartou\n")
        self.assertEqual(v.returncode, 3)
        self.assertIn("lokalni namitka", v.stderr)

    def test_delegation_works_in_worktree(self):
        """Ve worktree vrací `git rev-parse --git-dir` privátní adresář větve
        (`.git/worktrees/<name>`), kde hooky nejsou – cesta se proto musí
        skládat z `--git-common-dir`.

        Bez toho by delegace tiše selhala právě v layoutu, který `WORKTREE.md`
        předepisuje jako standard: lokální `commit-msg` projektu (gitleaks,
        commitlint, kontrola podpisu) by se přestal spouštět a nic by to neřeklo.
        """
        trace = self.tmp / "trace-worktree"
        self.local_hook(f"#!/bin/sh\ntouch {trace}\nexit 0\n")
        wt = self.tmp / "wt"
        v = git(self.repo, "worktree", "add", "-q", str(wt), "-b", "feat/wt")
        self.assertEqual(v.returncode, 0, v.stderr)
        msg_file = wt / "MSG"
        msg_file.write_text("Zaveď platby kartou\n")
        subprocess.run([str(COMMIT_MSG_HOOK), str(msg_file)], cwd=wt,
                       capture_output=True, text=True, check=False)
        self.assertTrue(trace.exists(),
                        "ve worktree se lokální hook repozitáře nezavolal")

    def test_local_hook_does_not_override_message_check(self):
        """Lokální hook smí přidat vlastní pravidlo, ne zrušit tohle."""
        self.local_hook("#!/bin/sh\nexit 0\n")
        self.assertEqual(self.run_commit_msg_hook("Merge branch 'feat/x'\n").returncode, REJECT)


class HookDeployment(unittest.TestCase):
    def test_hook_is_executable(self):
        self.assertTrue(os.access(COMMIT_MSG_HOOK, os.X_OK), f"{COMMIT_MSG_HOOK} není spustitelný")

    def test_rule_is_written_in_merge_skill(self):
        """Hook je mechanismus, ne zdroj pravdy. Zmizí-li pravidlo odtamtud, kde
        se dokončení větve vede, nikdo se z odmítnutí nedozví, jakou zprávu má
        napsat místo toho.

        Hledá se **příkaz i jeho odůvodnění**, ne dva řetězce kdekoliv v souboru.
        Ta volnější podoba by prošla i tehdy, kdyby pravidlo zmizelo a zbyly po
        něm zmínky jinde – tedy přesně v případě, kvůli kterému test vznikl.

        Do 21. 9. 2026 se měřil `WORKTREE.md`, kde postup dokončení větve tehdy
        žil. Přestěhoval se do `/merge`, protože hook platí pro **každý**
        repozitář, ne jen pro worktree layout – a pravidlo se musí měřit tam, kde
        je dnes, ne tam, kde bylo.
        """
        text = (ROOT / "skills" / "merge" / "SKILL.md").read_text()
        self.assertIn('git merge --no-ff', text,
                      "/merge neuvádí příkaz, kterým se větev dokončuje")
        self.assertRegex(
            text, r"githooks/commit-msg[^\n]*core\.hooksPath",
            "/merge neříká, že to vynucuje globálně nasazený hook – "
            "bez toho se z odmítnutého commitu nedá poznat, kdo ho odmítl a proč")


class GlobalHookDeployment(unittest.TestCase):
    """Že hook funguje, když ho zavoláš, neznamená, že ho někdo volá.

    `core.hooksPath` je stav stroje, ne repozitáře: nová instalace systému, jiný
    počítač nebo přepsaný `~/.gitconfig` hook odpojí, a nic o tom nedá vědět –
    merge prostě zase začne procházet s defaultní zprávou. Je to přesně ten tichý
    směr selhání, kvůli kterému `~/.claude/RULES.md`, *Ověřitelná kontrola místo
    dojmu*, žádá test k vynucovací vrstvě hned.

    Selhání tu není falešný poplach ani po čerstvém klonu: hook v tu chvíli
    opravdu nasazený není a zpráva říká, čím to napravit.
    """

    def test_hooksPath_points_to_githooks(self):
        if os.environ.get("CI"):
            self.skipTest("v CI se necommituje, hook tam nemá co dělat")
        # `--global`, ne efektivní hodnota: tu uspokojí i `core.hooksPath` nastavený
        # jen v tomhle repozitáři – a hook by pak neběžel nikde jinde, přestože
        # pravidlo o zprávě merge commitu platí pro všechny projekty.
        v = subprocess.run(["git", "config", "--global", "--get", "core.hooksPath"],
                           capture_output=True, text=True, check=False)
        path = Path(v.stdout.strip()).expanduser() if v.stdout.strip() else None
        self.assertEqual(
            path, COMMIT_MSG_HOOK.parent,
            "git hook není nasazený – `git log --first-parent` se zaplní zprávami "
            "'Merge branch ...'. Naprav příkazem:\n"
            f"    git config --global core.hooksPath {COMMIT_MSG_HOOK.parent}")


class VerifyHookIsRegistered(unittest.TestCase):
    """`verify.sh` musí být v `settings.json` jako Stop hook, jinak neběží vůbec.

    Skript je otestovaný do detailu – souhlasy, otisky, parser Markdownu, zámek –
    jenže to všechno měří, jak se chová, **když ho někdo zavolá**. Že ho volá
    Claude Code po každé odpovědi, nedrží nic než jeden záznam v `settings.json`,
    a ten je ručně editovaný soubor.

    Ztráta té registrace je nejtišší možné selhání celé vrstvy: nic nespadne,
    nic nezčervená, jen se od té chvíle nekontroluje nic a každé „hotovo“ stojí
    nad neověřeným stavem. Přesně ten směr selhání, kvůli kterému
    `~/.claude/RULES.md`, *Ověřitelná kontrola místo dojmu*, žádá test
    k vynucovací vrstvě hned, ne až se ukáže, že nefunguje.

    Hlídá se i timeout: `verify.sh` si sám dává `LIMIT` na krok a počítá
    s tím, že se tři kroky do timeoutu hooku vejdou. Timeout kratší než to by
    kontrolu utínal uprostřed a hlásil chybu tam, kde žádná není – tedy falešný
    poplach, který vede k vypnutí.
    """

    SETTINGS = ROOT / "settings.json"

    def entries(self):
        d = json.loads(self.SETTINGS.read_text(encoding="utf-8"))
        return [h for group in d.get("hooks", {}).get("Stop", [])
                for h in group.get("hooks", [])]

    def test_verify_is_stop_hook(self):
        commands = [h.get("command", "") for h in self.entries()]
        self.assertTrue(
            any(p.endswith("verify.sh") for p in commands),
            "verify.sh není v settings.json jako Stop hook – průběžná kontrola "
            f"neběží vůbec. Nalezené Stop hooky: {commands}")

    def test_stop_hook_path_exists(self):
        """Registrace na neexistující soubor je totéž jako žádná registrace.

        Cesty v `settings.json` jsou absolutní, protože je tak zapisuje Claude
        Code. Míří ale do adresáře, který je zároveň tímhle repozitářem, a ten
        v CI leží jinde než v `$HOME` – doslovné porovnání by tam hlásilo
        chybějící soubor, který je vedle verzovaný. Falešný poplach na každém
        pushi je přitom nejjistější cesta k tomu, že si kontrolu někdo vypne.
        Část cesty za posledním `.claude` se proto vztáhne ke kořenu repozitáře.
        """
        for h in self.entries():
            path = self.in_repo(Path(h.get("command", "").split()[0]).expanduser())
            with self.subTest(hook=str(path)):
                self.assertTrue(path.is_file(), f"Stop hook {path} neexistuje")

    @staticmethod
    def in_repo(path):
        parts = path.parts
        if ".claude" not in parts:
            return path
        i = len(parts) - 1 - parts[::-1].index(".claude")
        return ROOT.joinpath(*parts[i + 1:])

    def test_timeout_covers_three_steps(self):
        """`LIMIT` ve verify.sh se čte ze skriptu, ne opisuje – jinak se rozejdou."""
        limit = int(re.search(r"^LIMIT=(\d+)", (ROOT / "verify.sh").read_text(encoding="utf-8"),
                              re.M).group(1))
        verify = next(h for h in self.entries()
                      if h.get("command", "").endswith("verify.sh"))
        self.assertGreaterEqual(
            verify.get("timeout", 0), 3 * limit,
            f"timeout Stop hooku nepokryje ani tři kroky po {limit} s – kontrola "
            "se utne uprostřed a nahlásí chybu tam, kde žádná není")


class BypassRegistry(unittest.TestCase):
    """`BYPASS.md` musí jmenovat každou vrstvu, která něco vynucuje.

    Registr, který zestárne, je horší než žádný: tváří se jako úplná mapa
    známého povrchu, ale nová vrstva v něm chybí a nikdo si toho nevšimne.
    Seznam vrstev se proto čte z disku – z hooků v `settings.json`, z
    `githooks/` a z workflow v `.github/` –, ne z výčtu v testu.

    Kontroluje se jen **přítomnost**, ne obsah: jestli je řádek u konkrétní
    cesty pravdivý, žádný test nezjistí. Smysl je vynutit, aby se nad ní někdo
    zamyslel, ne předstírat, že se to dá změřit.
    """

    REGISTRY = ROOT / "BYPASS.md"

    #: Vrstvy, které se v registru záměrně neuvádějí – nic nevynucují.
    #: Prázdné od chvíle, kdy `iterm-notify.sh` nahradila vestavěná integrace
    #: iTerm2: její `cc-status` nevynucuje taky nic, ale řádek v registru má,
    #: protože je to cizí binárka běžící nad každým repozitářem.
    NON_ENFORCING: set[str] = set()

    def layers(self):
        """Soubory, které běží automaticky a něco vynucují."""
        out = set()
        settings = json.loads((ROOT / "settings.json").read_text(encoding="utf-8"))
        for groups in settings.get("hooks", {}).values():
            for g in groups:
                for h in g.get("hooks", []):
                    name = Path(h.get("command", "").split()[0]).name
                    if name and name not in self.NON_ENFORCING:
                        out.add(name)
        # Status line běží po každé odpovědi stejně jako Stop hook, ale
        # v settings.json sedí pod vlastním klíčem `statusLine`, ne mezi `hooks`.
        # Dokud se nečetl, držel její řádek v registru jen něčí ruka – a přitom
        # to je vrstva, která běží nad cizím repozitářem bez souhlasu a měla
        # 14. 9. 2026 dvě skutečné díry.
        sl = settings.get("statusLine", {}).get("command", "")
        if sl:
            out.add(Path(sl.split()[0]).name)
        out |= {f.name for f in (ROOT / "githooks").glob("*") if f.is_file()}
        out |= {f.name for f in (ROOT / ".github" / "workflows").glob("*.yml")}
        if (ROOT / "settings.json").exists():
            out.add("settings.json")
        return out

    def test_registry_exists(self):
        self.assertTrue(self.REGISTRY.is_file(), "chybí BYPASS.md – registr obcházení kontrol")

    def test_every_enforcing_layer_has_registry_row(self):
        text = self.REGISTRY.read_text(encoding="utf-8")
        missing = sorted(v for v in self.layers() if v not in text)
        self.assertFalse(missing,
            "tyhle vynucovací vrstvy nejsou v BYPASS.md, takže u nich nikdo nesepsal, "
            f"čím se dají obejít: {missing}")

    def test_accepted_risks_have_reason(self):
        """`accepted` bez důvodu je jen zamlčený problém."""
        defects = []
        for i, r in enumerate(self.REGISTRY.read_text(encoding="utf-8").splitlines(), 1):
            if "accepted" in r and not r.strip().startswith("|"):
                continue
            if "accepted" in r:
                # Měří se celý řádek, ne jen text za slovem „accepted“: zdůvodnění
                # bývá i ve sloupci „Co to chytí“ a vázat kontrolu na jeden sloupec
                # by hlásilo řádky, které důvod nesou jinde.
                text = r.replace("accepted", "").strip(" *|")
                if len(text) < 90:
                    defects.append(f"{self.REGISTRY.name}:{i}")
        self.assertFalse(defects, f"„accepted“ bez zdůvodnění na řádcích: {defects}")


class VerifyInCI(unittest.TestCase):
    """CI je jediná kontrola, která běží mimo tenhle stroj.

    Lokální `verify.sh` obejde commit z jiného počítače, z GUI, s `--no-verify`
    i cizí fork – repozitář je veřejný. CI proto pouští týž *Kontrakt příkazů*.

    Do 13. 9. 2026 si ho parsovala sama a ta druhá implementace se s `verify.sh`
    rozešla ve třech vlastnostech naráz (HTML komentáře, dvě sekce téhož jména,
    klíč `cwd`). Testy tu proto hlídají jednu věc: že druhý parser nevznikl znovu.
    """

    WORKFLOW = ROOT / ".github" / "workflows" / "verify.yml"
    CONTRACT = ROOT / ".claude" / "CLAUDE.md"

    #: Kroky, které do CI patří. Ne všechny klíče kontraktu: `dev` je watch server,
    #: který nikdy neskončí, `cwd` není příkaz. Množinová rovnost s kontraktem by
    #: v prvním projektu s `dev` vyrobila falešný poplach – a falešný poplach je
    #: u vynucovací vrstvy horší směr selhání než propuštěná chyba.
    CI_STEPS = {"typecheck", "lint", "test", "build", "e2e", "audit", "coverage",
                "a11y", "perf", "mutation"}

    def text(self):
        return self.WORKFLOW.read_text(encoding="utf-8")

    def body(self):
        """Workflow bez komentářových řádků.

        Testy nad celým souborem si uspokojí vlastní komentář: „volá
        `verify.sh --contract`“ napsané v hlavičce vypadá při hledání řetězce
        stejně jako to volání. Doloženo mutačním ověřením – dvě poškození kódu
        prošla, protože o nich mluvil komentář nad nimi.
        """
        return "\n".join(r for r in self.text().splitlines()
                          if not r.lstrip().startswith("#"))

    def test_workflow_exists(self):
        self.assertTrue(self.WORKFLOW.exists(), f"chybí {self.WORKFLOW}")

    def test_workflow_has_triggers(self):
        """Existence souboru neznamená, že CI běží.

        Osekané `on:` na samotný `workflow_dispatch` nebo `if: false` na jobu jsou
        jednořádkové změny, po kterých se kontroly přestanou spouštět – a `verify.yml`
        v repozitáři dál vypadá platně. Je to tentýž tichý směr selhání, jaký u git
        hooku hlídá `core.hooksPath` (`~/Dev/context/coding/quality.md`, *Vynucovací
        vrstva se testuje jako kód, obousměrně*, třetí odrážka).
        """
        body = self.body()
        m = re.search(r"^on:\n((?:[ \t]+\S.*\n)+)", body, re.M)
        self.assertIsNotNone(m, "ve workflow chybí blok `on:` – CI se nespouští")
        for trigger in ("push", "pull_request"):
            with self.subTest(trigger=trigger):
                self.assertIn(trigger, m.group(1), f"workflow se nespouští na {trigger}")
        # (?m) je nutné: bez něj `^` matchuje jen začátek celého řetězce, takže
        # by kontrola `if:` uvnitř souboru nikdy nenašla a byla by zelená vždy.
        self.assertNotRegex(body, r"(?m)^\s+if:\s", "job je podmíněný `if:` – může se tiše přeskočit")

    def test_contract_read_via_verify_sh(self):
        """Jediná implementace parseru. Vlastní by se rozešla, jako se to už stalo."""
        self.assertRegex(self.body(), r"verify\.sh --contract",
                         "workflow nevolá `verify.sh --contract` – nevznikl tu druhý parser?")

    def test_workflow_does_not_parse_contract_itself(self):
        """Mutační pojistka k testu výš: parser se pozná podle toho, že si sám
        hledá nadpis sekce nebo řádky `- klíč:` v Markdownu."""
        for pattern in ("## Kontrakt příkazů", "startswith", "re.findall", "python3 - <<"):
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, self.body(),
                                 f"workflow si kontrakt parsuje samo ({pattern})")

    def test_workflow_respects_cwd(self):
        """`verify.sh` klíčem cwd mění adresář, kde příkazy běží – typicky ve
        worktree layoutu. CI, která ho ignoruje, pouští něco jiného než lokální
        kontrola a obě si přitom myslí, že měřily totéž."""
        self.assertRegex(self.body(), r'cwd=\$\(.*contract',
                         "workflow klíč cwd nečte z kontraktu")
        self.assertRegex(self.body(), r'cd "\$cwd"', "workflow podle cwd nemění adresář")

    def test_workflow_runs_ci_steps(self):
        """Klíč, který do CI patří a projekt ho má, se nesmí tiše vynechat."""
        m = re.search(r"for key in ([a-z0-9 ]+); do", self.body())
        self.assertIsNotNone(m, "ve workflow se nenašel výčet kroků – změnil se tvar?")
        self.assertEqual(set(m.group(1).split()), self.CI_STEPS,
                         "výčet kroků v CI se rozešel se seznamem v testu")

    def test_workflow_does_not_copy_commands(self):
        """Kdyby se příkaz do workflow opsal, změna kontraktu by ho minula."""
        v = subprocess.run([str(ROOT / "verify.sh"), "--contract", str(ROOT)],
                           capture_output=True, text=True, check=False,
                           stdin=subprocess.DEVNULL)
        self.assertEqual(v.returncode, 0, v.stderr)
        commands = [r.split("\t", 1)[1] for r in v.stdout.splitlines() if "\t" in r]
        self.assertTrue(commands, "z kontraktu se nepřečetl jediný příkaz")
        for command in commands:
            if command.strip() == "-":
                continue
            with self.subTest(command=command[:40]):
                self.assertNotIn(command, self.body(),
                                 "workflow má příkaz opsaný, místo aby ho četl z kontraktu")



class CIChecksMutation(unittest.TestCase):
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
        self.tmp = Path(tempfile.mkdtemp(prefix="mutation-ci-"))
        self.original = VerifyInCI.WORKFLOW.read_text(encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def reports(self, mutation, method):
        """Spustí jednu kontrolu nad poškozeným workflow a vrátí, jestli selhala."""
        fake = self.tmp / "verify.yml"
        text = mutation(self.original)
        self.assertNotEqual(text, self.original, "mutace se neaplikovala – změnil se tvar workflow?")
        fake.write_text(text, encoding="utf-8")
        cls = type("WithFake", (VerifyInCI,), {"WORKFLOW": fake})
        result = unittest.TestResult()
        cls(method).run(result)
        return bool(result.failures or result.errors)

    def test_own_contract_parser_is_reported(self):
        self.assertTrue(self.reports(
            lambda s: s.replace("./verify.sh --contract .", "grep -A20 Kontrakt .claude/CLAUDE.md"),
            "test_contract_read_via_verify_sh"))

    def test_missing_step_is_reported(self):
        self.assertTrue(self.reports(
            lambda s: s.replace("for key in typecheck lint test", "for key in typecheck lint"),
            "test_workflow_runs_ci_steps"))

    def test_copied_command_is_reported(self):
        self.assertTrue(self.reports(
            lambda s: s.replace("          set -e\n", "          set -e\n          python3 -m unittest discover -s tests\n"),
            "test_workflow_does_not_copy_commands"))

    def test_trimmed_triggers_are_reported(self):
        self.assertTrue(self.reports(
            lambda s: s.replace("on:\n  push:\n  pull_request:\n", "on:\n"),
            "test_workflow_has_triggers"))

    def test_conditional_job_is_reported(self):
        self.assertTrue(self.reports(
            lambda s: s.replace("  contract:\n", "  contract:\n    if: false\n"),
            "test_workflow_has_triggers"))

    def test_ignored_cwd_is_reported(self):
        self.assertTrue(self.reports(
            lambda s: re.sub(r'\n\s+cwd=\$\([^\n]+\n\s+\[ -n "\$cwd" \] && cd "\$cwd"\n', "\n", s),
            "test_workflow_respects_cwd"))

    def test_intact_workflow_passes(self):
        """Pojistka proti obrácené chybě: kdyby kontroly hlásily i nad zdravým
        souborem, byly by ty mutační testy zelené omylem."""
        self.assertFalse(self.reports(lambda s: s + "\n# neškodný komentář\n",
                                      "test_contract_read_via_verify_sh"))


class GitGuard(unittest.TestCase):
    """`git-guard.py` musí zastavit přepsání historie bez ohledu na tvar příkazu.

    Vznikl proto, že deny seznam v `settings.json` porovnává **prefix celého
    příkazu**: `git push --force` zachytí, kdežto `git push origin main --force`
    projde pod plošným `Bash(git push:*)`. Testují se oba směry a ten druhý je
    tu důležitější – hook běží před **každým** Bash příkazem, takže falešný
    poplach neblokuje jeden případ, ale běžnou práci; kdo na něj narazí, hook
    si vypne, a pak nehlídá nic.
    """

    GUARD = ROOT / "git-guard.py"

    def run_guard(self, command):
        event = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
        return subprocess.run([sys.executable, str(self.GUARD)], input=event,
                              capture_output=True, text=True, check=False)

    def assertBlocked(self, command):
        done = self.run_guard(command)
        self.assertEqual(2, done.returncode, f"nezastaveno: {command}")
        self.assertIn("git-guard", done.stderr)

    def assertAllowed(self, command):
        done = self.run_guard(command)
        self.assertEqual(0, done.returncode,
                         f"falešný poplach nad {command!r}: {done.stderr}")

    def test_reordered_arguments_are_blocked(self):
        """Tvar, kvůli kterému hook vznikl: deny na něj prefixem nedosáhne."""
        for command in ["git push origin main --force",
                        "git push origin main -f",
                        "git push --repo=origin --force-with-lease",
                        "git push origin +main",
                        "git -C /tmp/x reset --hard HEAD~3"]:
            with self.subTest(command=command):
                self.assertBlocked(command)

    def test_aliases_are_expanded(self):
        """Výčet aliasů v deny seznamu stárne s každým novým řádkem
        v `~/.gitconfig`; hook je proto rozbaluje z konfigurace."""
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, HOME=tmp, GIT_CONFIG_GLOBAL=str(Path(tmp) / ".gitconfig"))
            subprocess.run(["git", "config", "--global", "alias.zz", "push --force"],
                           env=env, check=True, capture_output=True)
            event = json.dumps({"tool_name": "Bash", "tool_input": {"command": "git zz"}})
            done = subprocess.run([sys.executable, str(self.GUARD)], input=event,
                                  capture_output=True, text=True, check=False, env=env)
            self.assertEqual(2, done.returncode, "alias se nerozbalil")

    def test_shell_alias_is_blocked(self):
        """U aliasu začínajícího `!` nejde poznat, co spustí – zastaví se."""
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, HOME=tmp, GIT_CONFIG_GLOBAL=str(Path(tmp) / ".gitconfig"))
            subprocess.run(["git", "config", "--global", "alias.zz", "!sh -c 'echo ahoj'"],
                           env=env, check=True, capture_output=True)
            event = json.dumps({"tool_name": "Bash", "tool_input": {"command": "git zz"}})
            done = subprocess.run([sys.executable, str(self.GUARD)], input=event,
                                  capture_output=True, text=True, check=False, env=env)
            self.assertEqual(2, done.returncode, "shellový alias prošel")

    def test_clean_is_blocked_unless_dry_run(self):
        """`clean` se neposuzuje podle `-f`, ale podle toho, jestli je běh suchý.

        Dvě různé díry v jedné tabulce. Výčet tvarů (`-f`, `-fd`, `-fdx`, `-xdf`,
        `-df`) propustil slepené zkratky jako `git clean -fx`, které mažou
        netrackované **i ignorované** soubory, tedy `.env` a `node_modules`.
        A samotné `-f` nestačí jako kritérium: s `clean.requireForce=false`
        v konfiguraci maže `git clean` i bez něj (ověřeno 20. 9. 2026), takže
        by propadlo úplně holé volání.
        """
        for command in ["git clean", "git clean -x", "git clean -fx",
                        "git clean -ffd", "git clean -xf", "git clean -fd",
                        "git clean -xdf", "git clean --force"]:
            with self.subTest(command=command):
                self.assertBlocked(command)

    def test_clean_dry_run_passes(self):
        """Druhý směr: suchý běh nic nesmaže, a je to nejběžnější použití.

        `git clean -n` se pouští právě proto, aby bylo vidět, co by zmizelo –
        falešný poplach zrovna na něm by hook vypnul komukoliv.
        """
        for command in ["git clean -n", "git clean -nd", "git clean -xn",
                        "git clean --dry-run"]:
            with self.subTest(command=command):
                self.assertAllowed(command)

    def test_ordinary_commands_pass(self):
        """Druhý směr: co je v pořádku, nesmí hook shodit."""
        for command in ["git push",
                        "git push -u origin docs/nalezy",
                        "git status",
                        "git log --grep=force",
                        "git commit -m 'popiš --force v textu zprávy'",
                        "git branch -d docs/hotovo",
                        "git worktree remove /tmp/x",
                        "python3 -m unittest discover -s tests",
                        "grep -rn 'git push --force' docs/"]:
            with self.subTest(command=command):
                self.assertAllowed(command)

    def test_other_tools_pass(self):
        """Hook má matcher na Bash, ale nesmí spoléhat jen na něj."""
        event = json.dumps({"tool_name": "Read", "tool_input": {"file_path": "/tmp/x"}})
        done = subprocess.run([sys.executable, str(self.GUARD)], input=event,
                              capture_output=True, text=True, check=False)
        self.assertEqual(0, done.returncode)

    def test_malformed_input_passes(self):
        """Rozbitý vstup nesmí zastavit práci – hook je pojistka, ne brána."""
        done = subprocess.run([sys.executable, str(self.GUARD)], input="{tohle není JSON",
                              capture_output=True, text=True, check=False)
        self.assertEqual(0, done.returncode)

    def test_guard_is_registered(self):
        """Hook, který není v `settings.json`, nehlídá nic."""
        settings = json.loads((ROOT / "settings.json").read_text(encoding="utf-8"))
        commands = [h.get("command", "")
                    for g in settings.get("hooks", {}).get("PreToolUse", [])
                    for h in g.get("hooks", [])]
        self.assertTrue(any("git-guard.py" in c for c in commands),
                        "git-guard.py není mezi PreToolUse hooky")


if __name__ == "__main__":
    unittest.main()
