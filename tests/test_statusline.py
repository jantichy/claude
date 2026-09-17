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

WARNING = "config spouští program"


def git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args],
                          capture_output=True, text=True, check=False)


class StatusLineOverForeignRepo(unittest.TestCase):
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

    def plant_filter(self):
        """Nastaví clean filtr, který při zavolání vytvoří marker."""
        (self.repo / ".gitattributes").write_text("* filter=evil\n")
        git(self.repo, "config", "filter.evil.clean",
            f"sh -c 'touch {self.marker}; cat'")

    def run_statusline(self, script=None):
        stdin_json = json.dumps({
            "workspace": {"current_dir": str(self.repo),
                          "project_dir": str(self.repo)},
            "model": {"display_name": "Opus"},
            "context_window": {},
        })
        proc = subprocess.run(["bash", str(script or STATUSLINE)],
                                input=stdin_json, capture_output=True, text=True,
                                cwd=str(self.repo), check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return proc.stdout

    # --- nebezpečný směr: spuštěný program ---------------------------------

    def test_clean_filter_is_not_run(self):
        self.plant_filter()
        output = self.run_statusline()
        self.assertFalse(self.marker.exists(),
                         "status line spustila program z .git/config")
        self.assertIn(WARNING, output)

    def test_fsmonitor_is_finding(self):
        git(self.repo, "config", "core.fsmonitor", "/bin/echo")
        self.assertIn(WARNING, self.run_statusline())

    def test_textconv_is_finding(self):
        git(self.repo, "config", "diff.evil.textconv", "/bin/echo")
        self.assertIn(WARNING, self.run_statusline())

    def test_branch_shown_even_with_finding(self):
        """Varování nahrazuje počet změn, ne celý git blok – jinak by se
        falešný poplach projevil jako zmizelá informace bez vysvětlení."""
        self.plant_filter()
        self.assertIn("main", self.run_statusline())

    # --- nebezpečný směr: falešný poplach ----------------------------------

    def test_plain_repo_reports_changes(self):
        output = self.run_statusline()
        self.assertIn("~1 changes", output)
        self.assertNotIn(WARNING, output)

    def test_plain_local_config_is_not_finding(self):
        git(self.repo, "remote", "add", "origin", "https://example.invalid/r.git")
        git(self.repo, "config", "branch.main.rebase", "true")
        git(self.repo, "config", "core.ignorecase", "true")
        self.assertNotIn(WARNING, self.run_statusline())

    def test_clean_tree_reports_clean(self):
        git(self.repo, "checkout", "-q", "--", "a.txt")
        output = self.run_statusline()
        self.assertIn("Clean", output)
        self.assertNotIn(WARNING, output)

    # --- mutace: ověř, že to výš měří kontrolu, a ne shodu náhodou ---------

    def test_pattern_mutation_runs_filter(self):
        """Vyřízne filtry z blacklistu a ověří, že se pak marker opravdu vytvoří.

        Bez tohohle testu by `test_clean_filter_is_not_run` zůstal zelený i tehdy,
        kdyby marker nevznikal z úplně jiného důvodu – třeba proto, že git obsah
        souboru vůbec nečte."""
        broken = self.tmp / "broken-statusline.sh"
        text = STATUSLINE.read_text()
        mutation = text.replace(r"|filter\..*\.(clean|smudge|process)", "")
        self.assertNotEqual(text, mutation, "vzor v statusline.sh se přejmenoval")
        broken.write_text(mutation)

        self.plant_filter()
        self.run_statusline(broken)
        self.assertTrue(self.marker.exists(),
                        "poškozená verze filtr nespustila – test tedy neměří kontrolu")


class UsageBar(unittest.TestCase):
    """Pruh musí mít vždycky přesně `BAR_WIDTH` znaků, i v krajních hodnotách.

    Původní verze skládala pruh přes `seq 1 "$filled"`. BSD seq ale při
    `seq 1 0` počítá dolů a vypíše „1 0“, takže se nula bloků nakreslila jako
    dva. Prázdný pruh tím ukazoval využití a plný byl o dva znaky delší než
    ostatní, takže se řádek při každém překreslení posouval.

    Krajní hodnoty se testují obě: 0 % kreslí `filled=0` a 100 % `empty=0`.
    """

    def bar(self, pct):
        r = subprocess.run(
            ["bash", "-c", f'source "{STATUSLINE}" >/dev/null 2>&1; make_bar {pct}'],
            capture_output=True, text=True, check=False,
            stdin=subprocess.DEVNULL)
        return r.stdout.strip().splitlines()[-1]

    def test_width_is_constant(self):
        for pct in (0, 1, 7, 14, 50, 86, 99, 100):
            with self.subTest(pct=pct):
                self.assertEqual(len(self.bar(pct)), 7)

    def test_zero_percent_has_no_filled_block(self):
        self.assertNotIn("\u2588", self.bar(0))

    def test_hundred_percent_has_no_empty_block(self):
        self.assertNotIn("\u2591", self.bar(100))


class InputNumbersDoNotRunCommand(unittest.TestCase):
    """Hodnota z JSONu se nesmí dostat rovnou do `$(( ))`.

    Bash uvnitř aritmetické expanze vyhodnocuje obsah proměnné jako výraz
    rekurzivně, takže `a[$(příkaz)]` v číselném poli ten příkaz spustí.
    Status line se přitom překresluje po každé odpovědi a permission systém
    na ni nesahá – je to druhá cesta ke spuštění cizího kódu v tomtéž souboru,
    nezávislá na té přes git konfiguraci.

    Že vstup posílá Claude Code, není obrana, ale důvěra ve tvar dat. Mutační
    test níž ověřuje, že test měří sanitizaci, a ne že se příkaz nespustil
    z nějakého jiného důvodu.
    """

    MALICIOUS_JSON = json.dumps({
        "context_window": {
            "current_usage": {"input_tokens": "a[$(touch {marker})]",
                              "cache_creation_input_tokens": 0,
                              "cache_read_input_tokens": 0},
            "used_percentage": 10, "context_window_size": 200000},
        "rate_limits": {"five_hour": {"used_percentage": 5,
                                      "resets_at": "a[$(touch {marker})]"}},
        "workspace": {"current_dir": "/tmp"},
        "model": {"display_name": "T"},
    })

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="sl-arith-"))
        self.marker = self.tmp / "EXECUTED"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_statusline(self, script):
        subprocess.run(["bash", str(script)],
                       input=self.MALICIOUS_JSON.replace("{marker}", str(self.marker)),
                       capture_output=True, text=True, check=False, timeout=30)

    def test_malicious_number_does_not_run_command(self):
        self.run_statusline(STATUSLINE)
        self.assertFalse(self.marker.exists(),
                         "hodnota z JSONu se dostala do aritmetické expanze a spustila příkaz")

    def test_without_sanitization_command_runs(self):
        """Mutace: bez `num()` musí marker vzniknout – jinak test neměří sanitizaci."""
        broken = self.tmp / "statusline.sh"
        text = STATUSLINE.read_text()
        mutation = text.replace(
            """ctx_in=$(num "$(echo "$input" | jq -r '.context_window.current_usage.input_tokens // 0')")""",
            """ctx_in=$(echo "$input" | jq -r '.context_window.current_usage.input_tokens // 0')""")
        self.assertNotEqual(text, mutation, "sanitizace v statusline.sh se přejmenovala")
        broken.write_text(mutation)
        self.run_statusline(broken)
        self.assertTrue(self.marker.exists(),
                        "poškozená verze příkaz nespustila – test tedy neměří sanitizaci")


if __name__ == "__main__":
    unittest.main()
