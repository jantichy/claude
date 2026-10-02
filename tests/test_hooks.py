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
POST_CHECKOUT_HOOK = ROOT / "githooks" / "post-checkout"

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
        self.assertIn("skills/merge/SKILL.md", v.stderr)

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


class WorktreeLocalState(unittest.TestCase):
    """`githooks/post-checkout` převezme při založení worktree lokální stav z `main/`.

    Pravidlo drží `WORKTREE.md`, *Lokální stav se bere z `main/`*; hook ho vykonává,
    protože model ho vykonat nesmí – deny `Edit(//**/.env*)` zastaví i `ln -s`.

    Nebezpečné směry jsou dva. Hook, který mlčí, vrátí stav, kdy větev vznikne bez
    `.env` a nikdo si toho nevšimne. Hook, který zasáhne jinam, běží nad **každým**
    repozitářem na stroji: založí odkaz mimo kontejner, nebo přepíše trackovaný
    soubor větve. Testují se oba.

    Hook se v testu volá přes `-c core.hooksPath`, ne přes globální konfiguraci –
    měří se hook z pracovní kopie, ne ten, který je zrovna nasazený.
    """

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="post-checkout-test-")).resolve()
        seed = self.tmp / "seed"
        seed.mkdir()
        git(seed, "init", "-q", "-b", "main", ".")
        git(seed, "config", "user.email", "t@t")
        git(seed, "config", "user.name", "t")
        (seed / ".env.example").write_text("TRACKED=1\n")
        git(seed, "add", ".env.example")
        git(seed, "commit", "-qm", "init")
        self.container = self.tmp / "project"
        self.container.mkdir()
        subprocess.run(["git", "clone", "-q", "--bare", str(seed), str(self.container / ".bare")],
                       capture_output=True, check=True)
        (self.container / ".git").write_text("gitdir: ./.bare\n")
        self.add_worktree("main", "main", new_branch=False)
        self.main = self.container / "main"
        (self.main / ".env").write_text("SECRET=x\n")
        (self.main / ".env.production").write_text("SECRET=y\n")
        (self.main / ".env.local").write_text("PORT=3000\n")
        (self.main / ".env.example").write_text("LOCAL=changed\n")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def add_worktree(self, directory, branch, new_branch=True, repo=None):
        # Worktree vzniká vedle `main/` v kontejneru, u obyčejného repozitáře vedle něj.
        target = self.container / directory if repo is None else repo.parent / directory
        repo = repo or self.container
        args = ["-c", f"core.hooksPath={POST_CHECKOUT_HOOK.parent}",
                "worktree", "add", "-q", str(target)]
        args += ["-b", branch] if new_branch else [branch]
        v = git(repo, *args)
        self.assertEqual(v.returncode, 0, v.stderr)
        return v

    def test_env_is_symlinked_relatively(self):
        self.add_worktree("payments", "feat/payments")
        for name in (".env", ".env.production"):
            link = self.container / "payments" / name
            self.assertTrue(link.is_symlink(), f"{name} se do větve nesymlinkoval")
            self.assertEqual(os.readlink(link), f"../main/{name}",
                             "odkaz není relativní, přesun kontejneru by ho rozbil")

    def test_env_local_is_copied_not_linked(self):
        """Do `.env.local` si větev píše vlastní `PORT` – přes symlink by ho
        přepsala v `main/` i ve všech ostatních větvích."""
        self.add_worktree("payments", "feat/payments")
        local = self.container / "payments" / ".env.local"
        self.assertTrue(local.is_file() and not local.is_symlink(),
                        ".env.local není samostatná kopie")

    def test_tracked_file_is_not_overwritten(self):
        self.add_worktree("payments", "feat/payments")
        example = self.container / "payments" / ".env.example"
        self.assertFalse(example.is_symlink(), "trackovaný soubor větve nahradil odkaz do main/")
        self.assertEqual(example.read_text(), "TRACKED=1\n")

    def test_node_modules_is_never_symlinked(self):
        """Symlink by `npm install` ve větvi přepsal balíčky v `main/`. Klon jde
        jen na APFS; jinde hook adresář vynechá a řekne to."""
        (self.main / "node_modules" / "pkg").mkdir(parents=True)
        (self.main / "node_modules" / "pkg" / "index.js").write_text("x\n")
        self.add_worktree("payments", "feat/payments")
        nm = self.container / "payments" / "node_modules"
        self.assertFalse(nm.is_symlink(), "node_modules je symlink do main/")
        if nm.exists():
            self.assertTrue((nm / "pkg" / "index.js").is_file(), "klon node_modules je neúplný")

    def test_plain_checkout_does_nothing(self):
        """Přepnutí větve v existujícím worktree není založení – předchozí HEAD
        není nulový."""
        self.add_worktree("payments", "feat/payments")
        wt = self.container / "payments"
        (wt / ".env").unlink()
        v = git(wt, "-c", f"core.hooksPath={POST_CHECKOUT_HOOK.parent}",
                "checkout", "-q", "-b", "feat/other")
        self.assertEqual(v.returncode, 0, v.stderr)
        self.assertFalse((wt / ".env").exists(), "hook zasáhl při obyčejném checkoutu")

    def test_ordinary_repository_is_left_alone(self):
        """Hook běží nad každým repozitářem – mimo kontejner nesmí založit nic,
        ani když vedle leží adresář jménem `main`."""
        repo = self.tmp / "plain" / "repo"
        repo.parent.mkdir()
        subprocess.run(["git", "clone", "-q", str(self.tmp / "seed"), str(repo)],
                       capture_output=True, check=True)
        (repo / ".env").write_text("SECRET=x\n")
        (self.tmp / "plain" / "main").mkdir()
        (self.tmp / "plain" / "main" / ".env").write_text("SECRET=x\n")
        self.add_worktree("feature", "feat/x", repo=repo)
        self.assertFalse((self.tmp / "plain" / "feature" / ".env").exists(),
                         "hook převzal .env mimo worktree layout")

    def test_local_hook_is_delegated(self):
        """Globální `core.hooksPath` vypne lokální `post-checkout` projektu;
        hook ho proto musí zavolat sám, jinak ho tiše odstřihne."""
        trace = self.tmp / "trace"
        hook = self.container / ".bare" / "hooks" / "post-checkout"
        hook.parent.mkdir(exist_ok=True)
        hook.write_text(f"#!/bin/sh\ntouch {trace}\nexit 0\n")
        hook.chmod(0o755)
        self.add_worktree("payments", "feat/payments")
        self.assertTrue(trace.exists(), "lokální post-checkout se nezavolal")


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
            raw = Path(h.get("command", "").split()[0]).expanduser()
            path = self.in_repo(raw)
            with self.subTest(hook=str(path)):
                if ".claude" not in raw.parts and not path.is_file():
                    # Hook mimo tenhle repozitář je uživatelův lokální soubor
                    # (status line v `~/.config`), ne jeho součást. Na cizím
                    # stroji tam není a být nemá – hlásit to jako vadu by byl
                    # falešný poplach na každém pushi, a ten si člověk vypne.
                    self.skipTest(f"hook {raw} leží mimo repozitář a na tomhle stroji není")
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


class PermissionRuleSyntax(unittest.TestCase):
    """Pravidlo v `permissions`, které nikdy nezabere, vypadá stejně jako to funkční.

    Claude Code zná dvě syntaxe: prefix `Bash(příkaz:*)` a wildcard
    `Bash(a*b)`. Smíchané (`Bash(*verify.sh --allow:*)`) se čte jako prefix,
    takže `*` na začátku je doslovný znak a pravidlo nechytí nic. Deny
    na souhlas `verify.sh` takhle nedrželo od svého vzniku a nikdo si toho
    nevšiml, protože nefunkční deny mlčí stejně jako funkční.

    Testují se oba směry: kontrola musí chytit smíchaný tvar, ale nesmí hlásit
    čistý prefix ani čistý wildcard – jinak by kvůli ní někdo syntaxi rozbil.
    Třetí test ověřuje, že deny na souhlas skutečně pokryje volání s cestou
    i bez ní; porovnání napodobuje wildcard, kde `*` znamená cokoliv.
    """

    SETTINGS = ROOT / "settings.json"

    @staticmethod
    def is_mixed(rule):
        m = re.fullmatch(r"\w+\((.*)\)", rule)
        return bool(m) and m.group(1).endswith(":*") and "*" in m.group(1)[:-2]

    @staticmethod
    def wildcard_matches(rule, command):
        m = re.fullmatch(r"Bash\((.*)\)", rule)
        if not m or m.group(1).endswith(":*"):
            return False
        pattern = ".*".join(re.escape(p) for p in m.group(1).split("*"))
        return re.fullmatch(pattern, command) is not None

    def permissions(self):
        d = json.loads(self.SETTINGS.read_text(encoding="utf-8"))
        return d.get("permissions", {})

    def test_no_rule_mixes_wildcard_with_prefix(self):
        perms = self.permissions()
        for kind in ("allow", "deny", "ask"):
            for rule in perms.get(kind, []):
                with self.subTest(kind=kind, rule=rule):
                    self.assertFalse(
                        self.is_mixed(rule),
                        f"{kind} pravidlo {rule} míchá `*` s koncovým `:*` – čte se jako "
                        "doslovný prefix a nezabere nikdy. Napiš ho jako wildcard bez `:`")

    def test_checker_distinguishes_valid_forms(self):
        self.assertTrue(self.is_mixed("Bash(*verify.sh --allow:*)"))
        self.assertTrue(self.is_mixed("Bash(/a/*.sh:*)"))
        self.assertFalse(self.is_mixed("Bash(git log:*)"))
        self.assertFalse(self.is_mixed("Bash(*verify.sh --allow*)"))
        self.assertFalse(self.is_mixed("Read(/Users/honza/.claude/**)"))

    def test_verify_consent_is_denied_in_every_form(self):
        deny = self.permissions().get("deny", [])
        for command in ("verify.sh --allow .",
                        "~/.claude/verify.sh --allow /Users/honza/Dev/x",
                        "/Users/honza/.claude/verify.sh --revoke .",
                        "./verify.sh --revoke ."):
            with self.subTest(command=command):
                self.assertTrue(
                    any(self.wildcard_matches(r, command) for r in deny),
                    f"deny v settings.json nezastaví `{command}`")
        self.assertFalse(any(self.wildcard_matches(r, "~/.claude/verify.sh") for r in deny),
                         "deny zastavuje i samotnou kontrolu, ne jen souhlas")


class SettingsFormat(unittest.TestCase):
    """`settings.json` drží přesně ten tvar, ve kterém ho zapisuje Claude Code.

    Soubor se opakovaně přeformátoval na taby se zarovnanými hodnotami – pokaždé
    spolu s tím, jak se do něj vracel plugin GitKraken. Diff pak měl stovky
    řádků a jediná věcná změna se v něm ztratila. Kanonický tvar (dvě mezery,
    bez escapování diakritiky, koncový řádek) je ten, který vyrobí sám Claude
    Code, takže jeho vlastní zápis kontrolu neshodí a cizí přeformátování ano.

    Testují se oba směry: kontrola musí chytit taby i zarovnání, ale nesmí
    hlásit soubor v kanonickém tvaru.
    """

    SETTINGS = ROOT / "settings.json"

    @staticmethod
    def is_canonical(text):
        return json.dumps(json.loads(text), indent=2, ensure_ascii=False) + "\n" == text

    def test_settings_is_canonical(self):
        text = self.SETTINGS.read_text(encoding="utf-8")
        self.assertTrue(
            self.is_canonical(text),
            "settings.json není v kanonickém tvaru (odsazení dvěma mezerami). "
            "Něco ho přeformátovalo – porovnej parsovaný obsah s HEAD, ať se v diffu "
            "neztratí věcná změna, a formátování vrať nebo commitni zvlášť")

    def test_checker_distinguishes_formats(self):
        data = {"permissions": {"allow": ["Grep", "Read(~/Dev/**)"]}, "model": "opus", "note": "čeština"}
        self.assertTrue(self.is_canonical(json.dumps(data, indent=2, ensure_ascii=False) + "\n"))
        self.assertFalse(self.is_canonical(json.dumps(data, indent="\t", ensure_ascii=False) + "\n"),
                         "kontrola propustila odsazení taby")
        self.assertFalse(self.is_canonical(json.dumps(data, indent=2) + "\n"),
                         "kontrola propustila escapovanou diakritiku")
        aligned = json.dumps(data, indent=2, ensure_ascii=False).replace('"model": ', '"model":    ') + "\n"
        self.assertFalse(self.is_canonical(aligned), "kontrola propustila zarovnané hodnoty")


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


class SecretGuard(unittest.TestCase):
    """`secret-guard.py` zastaví Bash příkaz, který čte existující tajemství.

    Deny `Read(//**/.env)` hlídá jen nástroj Read; shell kolem něj prošel
    (`. ./.env`, `grep KEY .env`) a hodnota mohla skončit v transcriptu. Oba
    směry se testují: propuštěné čtení vrací díru, falešný poplach nad
    dokumentací nebo zprávou commitu, která `.env` jen zmiňuje, vede k vypnutí
    hooku, který běží před každým příkazem.
    """

    GUARD = ROOT / "secret-guard.py"

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="secret-guard-test-")).resolve()
        (self.tmp / "sub").mkdir()
        (self.tmp / ".env").write_text("")
        (self.tmp / ".env.example").write_text("")
        (self.tmp / "id_ed25519").write_text("")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_guard(self, command):
        event = json.dumps({"tool_name": "Bash", "cwd": str(self.tmp),
                            "tool_input": {"command": command}})
        return subprocess.run([sys.executable, str(self.GUARD)], input=event,
                              capture_output=True, text=True, check=False)

    def assertBlocked(self, command):
        done = self.run_guard(command)
        self.assertEqual(2, done.returncode, f"nezastaveno: {command!r}")
        self.assertIn("secret-guard", done.stderr)

    def assertAllowed(self, command):
        done = self.run_guard(command)
        self.assertEqual(0, done.returncode, f"falešný poplach nad {command!r}: {done.stderr}")

    def test_shell_reads_are_blocked(self):
        """Tvary, kterými tajemství četla skutečná session, a jejich příbuzní."""
        for command in ["set -a; . ./.env; set +a; curl -s -u x https://api.example",
                        "K=$(grep '^MAILGUN_KEY=' .env | cut -d= -f2-)",
                        "source .env",
                        "cat < .env",
                        "cp .env /tmp/x",
                        "cd sub && cat ../.env",
                        f"cat {self.tmp}/.env",
                        "head -c 100 id_ed25519"]:
            with self.subTest(command=command):
                self.assertBlocked(command)

    def test_interpreter_code_is_read(self):
        for command in ["python3 -c \"print(open('.env').read())\"",
                        "python3 - <<'EOF'\nprint(open('.env').read())\nEOF"]:
            with self.subTest(command=command):
                self.assertBlocked(command)

    def test_metadata_only_commands_pass(self):
        """Ověřit, že hook převzal `.env` do větve, musí jít bez obsahu."""
        for command in ["ls -la .env", "test -e .env && echo ok", "stat .env",
                        "git add .env.example", "git status --short"]:
            with self.subTest(command=command):
                self.assertAllowed(command)

    def test_mentions_are_not_reads(self):
        """Zmínka o `.env` v dokumentaci nebo ve zprávě commitu není čtení."""
        for command in ["grep -n '\\.env' README.md",
                        "git commit -m 'oprava .env'",
                        "git commit -q -F - <<'EOF'\nhook symlinkuje .env do main\nEOF",
                        "echo .env"]:
            with self.subTest(command=command):
                self.assertAllowed(command)

    def test_missing_file_passes(self):
        """Bez existujícího souboru není co uniknout – a padala by i každá zmínka."""
        self.assertAllowed("cat .env.production")

    def test_patterns_come_from_deny_list(self):
        """Seznam tajemství je jen v `settings.json`; opsaný výčet by se rozešel."""
        import ast
        tree = ast.parse(self.GUARD.read_text(encoding="utf-8"))
        doc = ast.get_docstring(tree, clean=False)
        literals = [n.value for n in ast.walk(tree)
                    if isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value != doc]
        self.assertFalse([v for v in literals if re.fullmatch(r"\.env.*|\*\.pem|.*id_rsa.*", v)],
                         "secret-guard.py nese vlastní výčet tajemství místo deny seznamu")

    def test_registered_as_pretooluse(self):
        settings = json.loads((ROOT / "settings.json").read_text(encoding="utf-8"))
        commands = [h.get("command", "")
                    for g in settings.get("hooks", {}).get("PreToolUse", [])
                    for h in g.get("hooks", [])]
        self.assertTrue(any("secret-guard.py" in c for c in commands),
                        "secret-guard.py není mezi PreToolUse hooky")


class PluginHooks(unittest.TestCase):
    """Plugin smí do session přidat hooky, a registr o nich dosud nevěděl.

    `BYPASS.md` má evidovat každou vrstvu, která běží automaticky, ale test,
    který to vynucuje, čte jen `settings.json`, `githooks/` a `.github/`.
    Plugin přitom nese vlastní `hooks/hooks.json` a zapíná se jedním řádkem
    v `enabledPlugins` – tedy vrstva, kterou registr nezná a nikdo neměří.

    Doloženo 27. 9. 2026 na `gitkraken-hooks`: v pracovní kopii se objevil
    zapnutý, přestože se **18. 9. 2026 po měření vědomě vypnul** (164× volal
    binárku, kterou nikdo neposlouchal, hook na 21 událostech,
    `PermissionRequest` s timeoutem 24 hodin). Bylo to už třetí kolo téhož –
    8. 9. vypršelo umlčení nálezu, 18. 9. se vypnul, 27. 9. byl zpátky – a to
    je práh, po kterém rozhodnutí potřebuje mechanismus, ne zápis.
    """

    SETTINGS = ROOT / "settings.json"

    def enabled(self):
        d = json.loads(self.SETTINGS.read_text(encoding="utf-8"))
        return [name for name, on in d.get("enabledPlugins", {}).items() if on]

    def test_gitkraken_hooks_stays_off(self):
        """Rozhodnutí z 18. 9. 2026 se obrátilo dvakrát; potřetí to má spadnout.

        Míří na jméno schválně: obecná kontrola níž mlčí, když plugin na disku
        není, takže po smazání by zapnutí v `settings.json` nehlídalo nic –
        a právě tou cestou se to vrátilo.
        """
        for name in self.enabled():
            self.assertNotIn("gitkraken", name.lower(),
                "gitkraken-hooks je zapnutý, přestože ho decisions.md "
                "(2026-09-18) vypnul po měření. Zapnul se sám, nebo to byl "
                "záměr? Je-li to záměr, přepiš rozhodnutí i tenhle test.")

    def test_enabled_plugin_with_hooks_is_in_bypass_registry(self):
        """Zapnutý plugin s vlastními hooky musí být v registru obcházení.

        **Mlčí, když plugin na disku není** – `plugins/` je v `.gitignore`,
        takže v CI se nemá co měřit a tvrdit tam cokoliv by byl falešný
        poplach. Je to tedy lokální ochrana, ne záruka, a proto vedle ní stojí
        jmenovitá kontrola výš.
        """
        registry = (ROOT / "BYPASS.md").read_text(encoding="utf-8").lower()
        for name in self.enabled():
            short = name.split("@")[0]
            hooks = list((ROOT / "plugins").glob(f"*/*/{short}/*/hooks/hooks.json"))
            hooks += list((ROOT / "plugins").glob(f"*/*/{short}/hooks/hooks.json"))
            if not hooks:
                continue
            with self.subTest(plugin=name):
                self.assertIn(short.lower(), registry,
                    f"plugin {name} přináší {hooks[0]} – tedy vrstvu, která "
                    "běží automaticky –, ale v BYPASS.md o něm není řádek. "
                    "Registr, který zestárne, je horší než žádný.")


if __name__ == "__main__":
    unittest.main()
