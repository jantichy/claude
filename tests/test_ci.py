"""Testy nad sdíleným CI.

CI je jediná vrstva, která běží mimo tenhle stroj. Lokální `verify.sh` obejde
commit z jiného počítače, z GUI, s `--no-verify` i cizí fork – repozitář je
veřejný. Od 2. 10. 2026 je CI napsané jednou: `.github/workflows/contract.yml`
volají připnutý na SHA všechny projekty s kontraktem a lokální cestou i tenhle
repozitář (`verify.yml`). Dřív si ho každý projekt nesl v kopii a kopie se
rozešly – vlastní workflow tohohle repozitáře byl nakonec slabší než ty
v projektech.

Hlídá se tu, že nevznikl druhý parser kontraktu, že se příkazy neopsaly, že je
připnuté všechno, co si CI stahuje, že volání přes pohyblivý ref neprojde a že
runner umí zčervenat. Testy volajícího workflow v projektech jsou krátké a
leží v každém projektu zvlášť – hlídají jen to, co sdílený workflow zevnitř
uhlídat nemůže: spouštěče, oprávnění tokenu a připnutí.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REUSABLE = ROOT / ".github" / "workflows" / "contract.yml"
CALLER = ROOT / ".github" / "workflows" / "verify.yml"
RUNNER = ROOT / ".github" / "run-contract.sh"

#: Kroky, které do CI patří. Ne všechny klíče kontraktu: `dev` je watch server,
#: který nikdy neskončí, `cwd` není příkaz. Množinová rovnost s kontraktem by
#: v projektu s `dev` vyrobila falešný poplach – a falešný poplach je
#: u vynucovací vrstvy horší směr selhání než propuštěná chyba.
CI_STEPS = {"typecheck", "lint", "test", "build", "e2e", "audit", "coverage",
            "a11y", "perf", "mutation"}


def without_comments(path):
    """Workflow bez komentářových řádků.

    Test nad celým souborem si uspokojí vlastní komentář: věta „volá
    `verify.sh --contract`“ v hlavičce vypadá při hledání řetězce stejně jako
    to volání. Doloženo mutačním ověřením – dvě poškození prošla, protože
    o nich mluvil komentář nad nimi.
    """
    text = path.read_text(encoding="utf-8")
    return "\n".join(r for r in text.splitlines() if not r.lstrip().startswith("#"))


class ReusableWorkflow(unittest.TestCase):
    """Sdílený workflow, který pouští kontrakt projektu."""

    WORKFLOW = REUSABLE

    def body(self):
        return without_comments(self.WORKFLOW)

    def test_is_callable(self):
        self.assertRegex(self.body(), r"(?m)^on:\n\s+workflow_call:",
                         "workflow nejde volat z jiného repozitáře – chybí `on: workflow_call`")

    def test_job_is_not_conditional(self):
        """Jen úroveň jobu (4 mezery). Krok smí být podmíněný legitimně –
        doinstalování nástrojů běží jen tam, kde projekt nějaké chce."""
        self.assertNotRegex(self.body(), r"(?m)^ {4}if:\s",
                            "job je podmíněný `if:` – může se tiše přeskočit")

    def test_does_not_swallow_failures(self):
        self.assertNotIn("continue-on-error", self.body(),
                         "krok nebo job má `continue-on-error` – selhání se spolkne")

    def test_contract_read_via_verify_sh(self):
        self.assertRegex(self.body(), r'verify\.sh" --contract',
                         "workflow nevolá `verify.sh --contract` – nevznikl tu druhý parser?")

    def test_does_not_parse_contract(self):
        """Bílá listina místo černé: jméno zdroje kontraktu ve workflow nemá co
        dělat a do `contract.tsv` se zapisuje jedinkrát – tím, co vypsal
        `verify.sh`. Černou listinu řetězců obešel v projektu přidaný `awk`."""
        self.assertNotIn("CLAUDE.md", self.body(),
                         "workflow sahá na CLAUDE.md – kontrakt se čte jen přes verify.sh")
        writes = len(re.findall(r'>\s*"?\$RUNNER_TEMP/contract\.tsv', self.body()))
        self.assertEqual(1, writes, f"do contract.tsv se zapisuje {writes}×")

    def test_tools_come_from_pinned_commit(self):
        """Jeden SHA v `uses:` připíná workflow i nástroje. Kdyby se klonovala
        hlava repozitáře, projekt by připnul workflow, ale `verify.sh` a runner
        by se mu pod rukama měnily."""
        body = self.body()
        self.assertRegex(body, r"WORKFLOW_SHA:\s*\$\{\{ job\.workflow_sha \}\}")
        self.assertRegex(body, r"WORKFLOW_REPOSITORY:\s*\$\{\{ job\.workflow_repository \}\}")
        self.assertRegex(body, r'checkout --quiet "\$WORKFLOW_SHA"',
                         "klon konfigurační vrstvy se nepřepíná na připnutý commit")
        self.assertRegex(body, r'"\$RUNNER_TEMP/claude/\.github/run-contract\.sh"',
                         "runner se nebere z klonu připnutého commitu")
        self.assertRegex(body, r'CLAUDE_CONFIG=\$RUNNER_TEMP/claude"? >> "\$GITHUB_ENV"',
                         "testy projektů nedostanou skripty z připnutého commitu")

    def test_moving_ref_is_rejected(self):
        """Volání přes `@main` musí CI shodit – měřeno spuštěním té podmínky."""
        m = re.search(r'ref="\$\{WORKFLOW_REF##\*@\}"\n(.*?\n\s+fi\n)', self.body(), re.S)
        self.assertIsNotNone(m, "kontrola pohyblivého ref se nenašla – změnil se tvar?")
        script = 'ref="${WORKFLOW_REF##*@}"\n' + m.group(1)
        cases = {
            ("jantichy/claude/.github/workflows/contract.yml@refs/heads/main", "jantichy/eventoid"): 1,
            ("jantichy/claude/.github/workflows/contract.yml@v1", "jantichy/eventoid"): 1,
            ("jantichy/claude/.github/workflows/contract.yml@" + "a" * 40, "jantichy/eventoid"): 0,
            # Vlastní repozitář volá lokální cestou, tam je workflow i nástroj v témže commitu.
            ("jantichy/claude/.github/workflows/contract.yml@refs/heads/main", "jantichy/claude"): 0,
        }
        for (ref, caller), expected in cases.items():
            with self.subTest(ref=ref[-20:], caller=caller):
                env = {**os.environ, "WORKFLOW_REF": ref, "WORKFLOW_REPOSITORY": "jantichy/claude",
                       "CALLER": caller}
                done = subprocess.run(["sh", "-c", script], env=env, capture_output=True,
                                      text=True, encoding="utf-8", errors="replace", check=False)
                self.assertEqual(expected, done.returncode, done.stdout + done.stderr)

    def test_downloads_are_pinned(self):
        """Co si CI stahuje mimo `uses:`, musí mít konkrétní verzi."""
        body = self.body()
        for url in re.findall(r"https://github\.com/[\w.-]+/[\w.-]+/releases/download/(\S+)", body):
            with self.subTest(url=url[:60]):
                self.assertNotIn("latest", url, "vydání se stahuje z pohyblivého `latest`")
        versions = re.findall(r"^\s*([A-Z][A-Z0-9_]*_VERSION):\s*(\S+)", body, re.MULTILINE)
        self.assertTrue(versions, "žádná proměnná s verzí – přesunula se jinam?")
        for name, value in versions:
            with self.subTest(variable=name):
                self.assertNotRegex(value, r"^(latest|main|\$)", f"verze v `{name}` není konkrétní")
        for package in re.findall(r"pip install[^\n]*", body):
            for token in package.replace("pip install", "").split():
                if token.startswith("-"):
                    continue
                name = re.sub(r"[=<>!~].*$", "", token)
                if not re.fullmatch(r"[A-Za-z][\w.-]*", name):
                    continue
                with self.subTest(package=name):
                    self.assertRegex(package, rf"{re.escape(name)}==[\d.]+",
                                     f"balíček `{name}` se instaluje bez připnuté verze")

    def test_actions_pinned_to_commit(self):
        uses = re.findall(r"^\s*-?\s*uses:\s*(\S+)", self.body(), re.M)
        self.assertTrue(uses, "workflow nepoužívá žádnou akci – opravdu?")
        for u in uses:
            with self.subTest(uses=u):
                self.assertRegex(u, r"@[0-9a-f]{40}$", f"akce `{u}` není připnutá na commit")

    def test_checkout_fetches_full_history(self):
        self.assertRegex(self.body(), r"fetch-depth:\s*0",
                         "checkout nestahuje celou historii – gitleaks by hledal v mělkém klonu")

    def test_security_steps_are_present(self):
        for step, invocation in (("gitleaks", '"$RUNNER_TEMP/gitleaks" detect'),
                                 ("semgrep", "semgrep --config")):
            with self.subTest(step=step):
                self.assertIn(invocation, self.body(), f"ve workflow se nespouští krok {step}")
        self.assertNotIn("--quiet --error", self.body(),
                         "semgrep s `--quiet` nerozliší nulu nálezů od nuly prohledaných souborů")

    def test_does_not_copy_commands(self):
        """Kdyby se příkaz z kontraktu do workflow opsal, změna kontraktu by ho minula."""
        v = subprocess.run([str(ROOT / "verify.sh"), "--contract", str(ROOT)],
                           capture_output=True, text=True, check=False, stdin=subprocess.DEVNULL)
        self.assertEqual(v.returncode, 0, v.stderr)
        commands = [r.split("\t", 1)[1] for r in v.stdout.splitlines() if "\t" in r]
        self.assertTrue(commands, "z kontraktu se nepřečetl jediný příkaz")

        def squeeze(text):
            return " ".join(text.split())

        body = squeeze(self.body() + "\n" + without_comments(CALLER))
        for command in commands:
            if command.strip() == "-":
                continue
            with self.subTest(command=command[:40]):
                self.assertNotIn(squeeze(command), body,
                                 "workflow má příkaz opsaný, místo aby ho četl z kontraktu")

    def test_runner_runs_ci_steps(self):
        m = re.search(r"for key in ([a-z0-9 ]+); do", RUNNER.read_text(encoding="utf-8"))
        self.assertIsNotNone(m, "v runneru se nenašel výčet kroků – změnil se tvar?")
        self.assertEqual(set(m.group(1).split()), CI_STEPS,
                         "výčet kroků v CI se rozešel se seznamem v testu")

    def test_runner_honors_cwd(self):
        body = RUNNER.read_text(encoding="utf-8")
        self.assertRegex(body, r"cwd=\$\(.*contract", "runner klíč cwd nečte z kontraktu")
        self.assertRegex(body, r'if \[ -n "\$cwd" \]; then\s*\n\s*cd "\$cwd"',
                         "runner nemění adresář podle cwd jednou podmínkou `[ -n ]`")


CALLER_CHECK = ROOT / ".github" / "caller.py"


def check_caller(path):
    """Pustí sdílenou kontrolu volajícího workflow, jak ji pouštějí projekty."""
    done = subprocess.run([sys.executable, str(CALLER_CHECK), str(path)],
                          capture_output=True, text=True, check=False)
    return done.returncode, done.stdout + done.stderr


class CallerWorkflow(unittest.TestCase):
    """Volající workflow – tenhle vlastní i ten v každém projektu.

    Kontrolu drží `.github/caller.py`, ne tahle třída: projekty ji pouštějí ze
    svých testů, takže tady se měří ona, ne její kopie.
    """

    def test_own_caller_passes(self):
        code, out = check_caller(CALLER)
        self.assertEqual(0, code, out)

    def test_checker_rejects_and_accepts(self):
        """Oba směry selhání: zastaví, co má, a propustí, co má."""
        good = CALLER.read_text(encoding="utf-8")
        pinned = good.replace("uses: ./.github/workflows/contract.yml",
                              "uses: jantichy/claude/.github/workflows/contract.yml@" + "0" * 40)
        cases = {
            "lokální volání": (good, 0),
            "připnuté volání z projektu": (pinned, 0),
            "neškodný komentář": (good + "\n# uses: nic\n", 0),
            "volání přes @main": (good.replace("uses: ./.github/workflows/contract.yml",
                                               "uses: jantichy/claude/.github/workflows/contract.yml@main"), 1),
            "volání jen v komentáři": (good.replace("    uses: ./.github", "    # uses: ./.github"), 1),
            "osekané spouštěče": (good.replace("on:\n  push:\n  pull_request:\n", "on:\n  workflow_dispatch:\n"), 1),
            "filtr větví": (good.replace("  push:\n", "  push:\n    branches: [ nikdy ]\n"), 1),
            "podmíněný job": (good.replace("  contract:\n", "  contract:\n    if: false\n"), 1),
            "continue-on-error": (good.replace("  contract:\n", "  contract:\n    continue-on-error: true\n"), 1),
            "bez permissions": (good.replace("permissions:\n  contents: read\n", ""), 1),
            "zápis": (good.replace("  contents: read\n", "  contents: read\n  pull-requests: write\n"), 1),
        }
        with tempfile.TemporaryDirectory() as tmp:
            for name, (text, expected) in cases.items():
                with self.subTest(case=name):
                    if expected:
                        self.assertNotEqual(text, good, "mutace se neaplikovala – změnil se tvar workflow?")
                    path = Path(tmp) / "verify.yml"
                    path.write_text(text, encoding="utf-8")
                    code, out = check_caller(path)
                    self.assertEqual(expected, code, out)

    def test_checker_reports_unreadable_file(self):
        code, _ = check_caller(Path("/nonexistent/verify.yml"))
        self.assertEqual(2, code)


class WorkflowMutation(unittest.TestCase):
    """Kontroly nad workflow musí nahlásit poškozený vzor.

    Kontrola, kterou nikdo neviděl selhat, je nedoložené tvrzení
    (`~/Dev/context/coding/quality.md`, *Vynucovací vrstva se testuje jako kód,
    obousměrně*). Mutuje se kopie v tempu, ne soubor v repozitáři.
    """

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="mutation-ci-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def reports(self, cls, mutation, method):
        original = cls.WORKFLOW.read_text(encoding="utf-8")
        text = mutation(original)
        self.assertNotEqual(text, original, "mutace se neaplikovala – změnil se tvar workflow?")
        fake = self.tmp / cls.WORKFLOW.name
        fake.write_text(text, encoding="utf-8")
        result = unittest.TestResult()
        type("WithFake", (cls,), {"WORKFLOW": fake})(method).run(result)
        return bool(result.failures or result.errors)

    def test_own_parser_is_reported(self):
        self.assertTrue(self.reports(ReusableWorkflow,
            lambda s: s.replace('"$RUNNER_TEMP/claude/verify.sh" --contract .',
                                "grep -A20 Kontrakt CLAUDE.md"),
            "test_contract_read_via_verify_sh"))

    def test_head_instead_of_pinned_commit_is_reported(self):
        self.assertTrue(self.reports(ReusableWorkflow,
            lambda s: s.replace('git -C "$RUNNER_TEMP/claude" checkout --quiet "$WORKFLOW_SHA"\n', ""),
            "test_tools_come_from_pinned_commit"))

    def test_disabled_ref_guard_is_reported(self):
        self.assertTrue(self.reports(ReusableWorkflow,
            lambda s: s.replace("            exit 1\n          fi\n          git clone",
                                "          fi\n          git clone"),
            "test_moving_ref_is_rejected"))

    def test_quiet_semgrep_is_reported(self):
        self.assertTrue(self.reports(ReusableWorkflow,
            lambda s: s.replace("semgrep --config p/owasp-top-ten --error",
                                "semgrep --config p/owasp-top-ten --quiet --error"),
            "test_security_steps_are_present"))

    def test_unpinned_semgrep_is_reported(self):
        self.assertTrue(self.reports(ReusableWorkflow,
            lambda s: s.replace("semgrep==1.177.0", "semgrep"),
            "test_downloads_are_pinned"))

    def test_conditional_job_is_reported(self):
        self.assertTrue(self.reports(ReusableWorkflow,
            lambda s: s.replace("  contract:\n    runs-on:", "  contract:\n    if: false\n    runs-on:"),
            "test_job_is_not_conditional"))

    def test_intact_workflows_pass(self):
        """Pojistka proti obrácené chybě: kdyby kontroly hlásily i nad zdravým
        souborem, byly by mutační testy zelené omylem."""
        self.assertFalse(self.reports(ReusableWorkflow, lambda s: s + "\n# neškodný komentář\n",
                                      "test_tools_come_from_pinned_commit"))


class TestRunner(unittest.TestCase):
    """Že runner umí zčervenat – měřeno spuštěním, ne čtením.

    Tahle třída vznikla 18. 9. 2026 z nálezu `/review full`, který doložil
    přehráním, že 6 způsobů, jak CI trvale zezelenat (`exit 0`,
    `continue-on-error`, `sh -c "$command" || true`, obalení smyčky `if false`,
    prázdný kontrakt, smazané `set -e`), prošlo **všemi** devíti textovými
    kontrolami nad workflow. Textová kontrola hlídá známé způsoby; sedmý
    nepozná. Spuštění měří účinek.

    Testují se oba směry selhání, jak to `~/Dev/context/coding/quality.md` žádá
    od každé vynucovací vrstvy: že runner propustí, co propustit má, i že
    zastaví, co zastavit má. Falešný poplach je tu ta horší polovina – runner,
    který padá na čistém kontraktu, si někdo při první kolizi vypne.
    """

    def run_with(self, contract):
        """Spustí runner nad podvrženým kontraktem a vrátí návratový kód."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "contract.tsv"
            path.write_text(contract, encoding="utf-8")
            done = subprocess.run([str(RUNNER), str(path)], capture_output=True,
                                  text=True, check=False, stdin=subprocess.DEVNULL)
            return done.returncode, done.stdout + done.stderr

    def test_runner_exists_and_is_executable(self):
        self.assertTrue(RUNNER.exists(), f"chybí {RUNNER}")
        self.assertTrue(os.access(RUNNER, os.X_OK), f"{RUNNER} není spustitelný")

    def test_all_dashes_pass(self):
        """Kontrakt ze samých pomlček je dnešní stav projektu – musí projít,
        a musí se o každém přeskočeném klíči ozvat.

        Ta druhá půlka je tu od 21. 9. 2026 z nálezu `/consistency full`.
        Pomlčku má 8 z 10 klíčů, takže kdyby ten `echo` zmizel, CI by o osmi
        krocích mlčela a celá sada by zůstala zelená – tedy táž vada, jakou
        u druhé větve přeskočení hlídá `test_missing_key_is_not_silent`.
        """
        contract = "".join(f"{k}\t-\n" for k in sorted(CI_STEPS))
        code, out = self.run_with(contract)
        self.assertEqual(0, code, f"runner shodil kontrakt ze samých pomlček:\n{out}")
        for key in sorted(CI_STEPS):
            with self.subTest(key=key):
                self.assertIn(f"{key} – projekt ho vědomě nemá", out,
                              "vědomě přeskočený krok se neozval")

    def test_failing_command_turns_red(self):
        """Jediný padající příkaz musí shodit celý běh."""
        code, out = self.run_with("lint\t-\ntest\tfalse\n")
        self.assertEqual(1, code, f"runner propustil padající příkaz:\n{out}")

    def test_failure_is_reported_for_every_step(self):
        """Padne-li krok uprostřed, běh pokračuje a spadne až na konci.

        Kdyby skončil prvním selháním, jedna chyba by zakryla všechny ostatní
        a opravovalo by se po jedné napříč několika běhy CI.
        """
        code, out = self.run_with("lint\tfalse\ntest\ttrue\naudit\tfalse\n")
        self.assertEqual(1, code, out)
        self.assertIn("lint selhal", out)
        self.assertIn("audit selhal", out)

    def test_missing_key_is_not_silent(self):
        """Klíč, který projekt nemá, se přeskočí – ale nahlas.

        Tichý přeskok je k nerozeznání od kontroly, která proběhla a nic
        nenašla: 3 nespuštěné kroky se pak čtou jako 3 čisté výsledky.
        """
        code, out = self.run_with("lint\t-\n")
        self.assertEqual(0, code, out)
        self.assertIn("test – není v kontraktu", out)

    def test_empty_contract_does_not_pass_silently(self):
        """Prázdný kontrakt je jeden ze 6 doložených způsobů, jak CI
        zezelenat. Runner sám o sobě nemá jak poznat, že měl co spouštět –
        ale musí to být vidět ve výstupu, ne jako mlčky zelený běh."""
        code, out = self.run_with("")
        self.assertEqual(0, code, out)
        for key in sorted(CI_STEPS):
            with self.subTest(key=key):
                self.assertIn(f"{key} – není v kontraktu", out)

    def test_relative_contract_survives_cwd(self):
        """Kontrakt zadaný relativní cestou musí runner najít i po přepnutí adresáře.

        Smyčka čte kontrakt znovu, až **po** `cd "$cwd"` – relativní cesta by se
        po přepnutí nenašla a se `set -e` by skript spadl na něčem, co vypadá
        jako chyba jinde. Dnešní použití to nezasahuje (workflow předává
        absolutní `$RUNNER_TEMP` a projekt klíč `cwd` nemá), takže je to past,
        ne porucha – a pasti se hlídají spuštěním, ne přečtením. Doloženo
        čtenářem bez kontextu 19. 9. 2026.
        """
        with tempfile.TemporaryDirectory() as tmp:
            elsewhere = Path(tmp) / "elsewhere"
            elsewhere.mkdir()
            (Path(tmp) / "contract.tsv").write_text(
                f"cwd\t{elsewhere}\nlint\t-\ntest\tfalse\n", encoding="utf-8")
            done = subprocess.run([str(RUNNER), "contract.tsv"], cwd=tmp,
                                  capture_output=True, text=True, check=False,
                                  stdin=subprocess.DEVNULL)
        output = done.stdout + done.stderr
        self.assertEqual(1, done.returncode,
                         f"runner s relativní cestou a cwd neskončil na padajícím příkazu:\n{output}")
        self.assertIn("test selhal", output, output)

    def test_unreadable_contract_is_an_error(self):
        """Chybějící soubor nesmí projít jako „nic ke spuštění“."""
        with tempfile.TemporaryDirectory() as tmp:
            done = subprocess.run([str(RUNNER), str(Path(tmp) / "není.tsv")],
                                  capture_output=True, text=True, check=False,
                                  stdin=subprocess.DEVNULL)
        self.assertEqual(1, done.returncode, done.stdout + done.stderr)



if __name__ == "__main__":
    unittest.main()
