"""Regresní testy skriptu `/next`, který zjišťuje živé session a jejich větve.

`/next` podle výstupu rozhoduje, jestli úkol v rozdělané větvi **nabídne**
(větev je opuštěná), nebo ho **skryje** (ve vedlejším okně nad ní běží session).
Obě chyby jsou tiché: mrtvá session vydávaná za živou schová zapomenutou práci
navždy, a živá vydávaná za mrtvou nabídne druhé session úkol, na kterém už dělá
první – a jejich větve se srazí.

Testují se proto oba směry: záznam po spadlém procesu se nesmí počítat, živý
proces ano, a větev se bere z **posledního** záznamu transcriptu, ne z prvního –
session ve worktree layoutu startuje v kořeni kontejneru a do větve přechází až
během práce. Chybějící registr musí skončit kódem 2, ne prázdným seznamem:
prázdný seznam by tvrdil, že žádná session neběží.

K větvím projektu skript hledá i **poslední opuštěnou session**, kterou `/next`
nabídne k obnovení přes `/resume`. Tady je tvrdý zákaz: session, která běží –
i obnovená v jiném okně –, se mezi opuštěné nesmí dostat nikdy, jinak by se
jedna konverzace otevřela dvakrát.

Spouští se: python3 -m unittest discover -s tests -q
"""
import json
import re
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills" / "next" / "sessions.py"
COLLECT = ROOT / "skills" / "next" / "collect.py"


class LiveSessionsAndBranches(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name)
        self.claude = self.home / ".claude"
        (self.claude / "sessions").mkdir(parents=True)
        # Živý proces, který není předkem skriptu – jako session ve vedlejším okně.
        self.sleeper = subprocess.Popen(["sleep", "60"])

    def tearDown(self):
        self.sleeper.kill()
        self.sleeper.wait()
        self.tmp.cleanup()

    def register(self, pid, sid, transcript_lines=None):
        (self.claude / "sessions" / f"{pid}.json").write_text(json.dumps(
            {"pid": pid, "sessionId": sid, "cwd": "/projekt", "name": sid, "status": "waiting"}))
        if transcript_lines is not None:
            project_dir = self.claude / "projects" / "-projekt"
            project_dir.mkdir(parents=True, exist_ok=True)
            (project_dir / f"{sid}.jsonl").write_text(
                "\n".join(json.dumps(r) for r in transcript_lines) + "\n")

    def run_script(self, *args):
        env = dict(os.environ, HOME=str(self.home))
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True,
                              text=True, env=env)

    def idle(self):
        run = self.run_script("--project", "/projekt")
        self.assertEqual(run.returncode, 0, run.stderr)
        return {s["branch"]: s["session_id"] for s in json.loads(run.stdout)["idle"]}

    def dead_pid(self):
        p = subprocess.Popen(["true"])
        p.wait()
        return p.pid

    def test_branch_taken_from_last_entry(self):
        self.register(self.sleeper.pid, "ziva", [
            {"type": "user", "cwd": "/projekt/main", "gitBranch": "main"},
            {"type": "assistant", "cwd": "/projekt/dph", "gitBranch": "specify-dph"},
            {"type": "attachment"},
        ])
        run = self.run_script()
        self.assertEqual(run.returncode, 0, run.stderr)
        [s] = json.loads(run.stdout)["sessions"]
        self.assertEqual((s["cwd"], s["branch"], s["self"]),
                         ("/projekt/dph", "specify-dph", False))

    def test_entry_of_crashed_process_ignored(self):
        self.register(self.dead_pid(), "mrtva", [{"cwd": "/projekt/x", "gitBranch": "x"}])
        run = self.run_script()
        self.assertEqual(json.loads(run.stdout)["sessions"], [])

    def test_live_session_without_transcript_has_unknown_branch(self):
        self.register(self.sleeper.pid, "bez-transcriptu")
        [s] = json.loads(self.run_script().stdout)["sessions"]
        self.assertIsNone(s["branch"])

    def test_own_session_is_marked(self):
        # Předek skriptu je i tenhle testovací proces.
        self.register(os.getpid(), "ja", [{"cwd": "/projekt", "gitBranch": "main"}])
        [s] = json.loads(self.run_script().stdout)["sessions"]
        self.assertTrue(s["self"])

    def test_abandoned_session_offered_for_resume(self):
        self.register(self.dead_pid(), "stara", [{"cwd": "/projekt/dph", "gitBranch": "specify-dph"}])
        self.assertEqual(self.idle(), {"specify-dph": "stara"})

    def test_live_session_never_abandoned(self):
        # Táž session je i živá (obnovená v jiném okně) – mezi opuštěné nepatří,
        # ani když má v registru i starý záznam po spadlém procesu.
        self.register(self.dead_pid(), "obnovena", [{"cwd": "/projekt/dph", "gitBranch": "specify-dph"}])
        self.register(self.sleeper.pid, "obnovena")
        self.assertEqual(self.idle(), {})

    def test_session_from_other_project_ignored(self):
        self.register(self.dead_pid(), "cizi", [{"cwd": "/jiny/dph", "gitBranch": "specify-dph"}])
        self.assertEqual(self.idle(), {})

    def test_unreadable_registry_entry_is_not_empty_list(self):
        # Nečitelný záznam může patřit běžící session – kdyby se přeskočil,
        # nabídla by se její konverzace k obnovení podruhé.
        self.register(self.dead_pid(), "stara", [{"cwd": "/projekt/dph", "gitBranch": "specify-dph"}])
        (self.claude / "sessions" / "rozbity.json").write_text("{nedopsano")
        run = self.run_script("--project", "/projekt")
        self.assertEqual(run.returncode, 2)
        self.assertEqual(run.stdout, "")

    def test_foreign_project_not_in_project(self):
        (self.claude / "sessions" / f"{self.sleeper.pid}.json").write_text(json.dumps(
            {"pid": self.sleeper.pid, "sessionId": "cizi", "cwd": "/jiny"}))
        [s] = json.loads(self.run_script("--project", "/projekt").stdout)["sessions"]
        self.assertFalse(s["in_project"])

    def test_abandoned_session_carries_start_dir(self):
        self.register(self.dead_pid(), "stara", [
            {"cwd": "/projekt", "gitBranch": "main"},
            {"cwd": "/projekt/dph", "gitBranch": "specify-dph"},
        ])
        run = self.run_script("--project", "/projekt")
        [s] = json.loads(run.stdout)["idle"]
        self.assertEqual((s["start_cwd"], s["cwd"]), ("/projekt", "/projekt/dph"))

    def test_missing_registry_is_not_empty_list(self):
        (self.claude / "sessions").rmdir()
        run = self.run_script()
        self.assertEqual(run.returncode, 2)
        self.assertEqual(run.stdout, "")



class PlanAndQueueParsing(unittest.TestCase):
    """Parsery `collect.py`: úkoly plánu a závislost schovaná na konci popisu."""

    def setUp(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("collect", COLLECT)
        self.c = importlib.util.module_from_spec(spec)
        import sys as _sys
        _sys.path.insert(0, str(COLLECT.parent))
        spec.loader.exec_module(self.c)

    def test_plan_counts_tasks_by_heading(self):
        plan = self.c.parse_plan(
            "## Úkol 1\n- [x] krok\n- [x] krok\nKritérium:\n- vrací 200\n"
            "## Úkol 2\n- [x] krok\n- [ ] krok\n")
        self.assertEqual((plan["open"], plan["done"], plan["next"]), (1, 1, ["Úkol 2"]))

    def test_plain_bullet_does_not_keep_plan_open(self):
        plan = self.c.parse_plan("## Úkol\n- [x] krok\n- poznámka\n")
        self.assertEqual(plan["open"], 0)

    def test_dependency_at_end_of_long_description(self):
        long_item = "- [ ] **Úkol.** " + "vata " * 100 + "Čeká na odpověď podpory. Konec."
        [item] = self.c.parse_items([long_item])
        self.assertEqual(item["waits"], "odpověď podpory")


TODO = """# TODO

## Probíhá

- [ ] **Export faktur.** Napojit formát.
- [x] **Hotová věc.** Už je.

## Kola návrhu

### Kolo o DPH

- **Stav:** čeká
- **Větev:** `specify-dph`
- **Čeká na:** nic

### Kolo o fakturaci

- **Stav:** čeká
- **Větev:** `specify-faktury`
- **Čeká na:** Kolo o DPH
"""


class QueueCollection(unittest.TestCase):
    """`collect.py` nad skutečným gitem: worktree kontejner, větve a živé session.

    Hlídá to, kvůli čemu sběr vznikl: obsazená větev se musí poznat i tehdy, když
    ji `--no-merged` nevypíše (čerstvá větev bez commitu), fronta se čte z hlavní
    větve, ne z pracovního adresáře, a kolo s rozběhnutou větví nese stav z ní.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.home = base / "home"
        (self.home / ".claude" / "sessions").mkdir(parents=True)
        self.env = dict(os.environ, HOME=str(self.home), GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
                        GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        self.box = base / "projekt"
        src = base / "src"
        self.git("init", "-q", "-b", "main", str(src))
        (src / "docs").mkdir()
        (src / "docs" / "todo.md").write_text(TODO)
        self.git("-C", str(src), "add", "-A")
        self.git("-C", str(src), "commit", "-q", "-m", "start")
        self.box.mkdir()
        self.git("clone", "-q", "--bare", str(src), str(self.box / ".bare"))
        self.bare = ["--git-dir", str(self.box / ".bare")]
        self.git(*self.bare, "worktree", "add", "-q", str(self.box / "main"), "main")
        # Kolo o DPH se rozhoduje ve větvi s worktree, fakturace má větev bez commitu.
        self.git(*self.bare, "worktree", "add", "-q", "-b", "specify-dph", str(self.box / "dph"), "main")
        vat_todo = self.box / "dph" / "docs" / "todo.md"
        vat_todo.write_text(TODO.replace("- **Stav:** čeká\n- **Větev:** `specify-dph`",
                                    "- **Stav:** rozhoduje se\n- **Větev:** `specify-dph`"))
        self.git("-C", str(self.box / "dph"), "commit", "-qam", "DPH rozhoduje se")
        self.git(*self.bare, "branch", "specify-faktury", "main")
        self.sleeper = subprocess.Popen(["sleep", "60"])

    def tearDown(self):
        self.sleeper.kill()
        self.sleeper.wait()
        self.tmp.cleanup()

    def git(self, *args):
        subprocess.run(["git", *args], check=True, env=getattr(self, "env", None), capture_output=True)

    def session(self, pid, sid, cwd, branch):
        claude = self.home / ".claude"
        (claude / "sessions" / f"{pid}.json").write_text(json.dumps(
            {"pid": pid, "sessionId": sid, "cwd": str(self.box), "name": sid}))
        project_dir = claude / "projects" / "-projekt"
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / f"{sid}.jsonl").write_text(
            json.dumps({"cwd": str(self.box)}) + "\n" + json.dumps({"cwd": cwd, "gitBranch": branch}) + "\n")

    def collect(self):
        run = subprocess.run([sys.executable, str(COLLECT), str(self.box)],
                             capture_output=True, text=True, env=self.env)
        self.assertEqual(run.returncode, 0, run.stderr)
        return json.loads(run.stdout)

    def branches(self):
        return {b["branch"]: b for b in self.collect()["branches"]}

    def dead_pid(self):
        p = subprocess.Popen(["true"])
        p.wait()
        return p.pid

    def test_queue_read_from_main_branch_without_done(self):
        data = self.collect()
        [part] = data["todo"][0]["parts"]
        self.assertEqual([i["title"] for i in part["items"]], ["Export faktur"])
        self.assertEqual([r["status"] for r in data["rounds"]], ["čeká", "čeká"])

    def test_round_carries_state_from_its_branch(self):
        vat_round = self.collect()["rounds"][0]
        self.assertEqual(vat_round["branch_state"], "rozhoduje se")

    def test_round_removed_in_branch_is_merge_pending(self):
        """Blok kola ve větvi zmizel, tedy je zapsané a čeká jen sloučení. Hodnota
        musí být token, podle kterého se rozhoduje, ne věta pro člověka."""
        vat_todo = self.box / "dph" / "docs" / "todo.md"
        text = vat_todo.read_text()
        start = text.index("### Kolo o DPH")
        vat_todo.write_text(text[:start] + text[text.index("### Kolo o fakturaci"):])
        self.git("-C", str(self.box / "dph"), "commit", "-qam", "DPH zapsáno")
        self.assertEqual(self.collect()["rounds"][0]["branch_state"], "merge_pending")

    def test_abandoned_branch_with_session_to_resume(self):
        self.session(self.dead_pid(), "stara", str(self.box / "dph"), "specify-dph")
        b = self.branches()["specify-dph"]
        self.assertEqual((b["state"], b["resume"]["session_id"], b["resume"]["start_cwd"]),
                         ("abandoned", "stara", str(self.box)))
        self.assertEqual(b["rounds"], ["Kolo o DPH"])

    def test_occupied_branch_without_commit(self):
        # `--no-merged` větev bez commitu nevypíše; živá session nad ní ji musí přidat.
        self.session(self.sleeper.pid, "ziva", str(self.box / "faktury"), "specify-faktury")
        b = self.branches()["specify-faktury"]
        self.assertEqual((b["state"], b["session"]), ("occupied", "ziva"))

    def test_run_from_worktree_subdir_finds_container(self):
        run = subprocess.run([sys.executable, str(COLLECT), str(self.box / "dph" / "docs")],
                             capture_output=True, text=True, env=self.env)
        data = json.loads(run.stdout)
        self.assertEqual((data["layout"], Path(data["root"]).resolve(), data["current"]["branch"]),
                         ("worktree", self.box.resolve(), "specify-dph"))

    def test_branch_without_work_not_abandoned(self):
        # Větev bez commitu a bez neuložených změn není zapomenutá práce – buď se
        # nevypíše vůbec, nebo jako prázdná; opuštěná být nesmí.
        # Worktree bez práce je přesně ten případ, kdy se větev vypíše – po sloučení zůstal stát.
        self.git(*self.bare, "worktree", "add", "-q", str(self.box / "faktury"), "specify-faktury")
        self.assertEqual(self.branches()["specify-faktury"]["state"], "empty")

    def test_uncommitted_changes_in_other_worktree_are_work(self):
        self.git(*self.bare, "worktree", "add", "-q", "-b", "export", str(self.box / "export"), "main")
        (self.box / "export" / "novy.txt").write_text("rozdělané")
        b = self.branches()["export"]
        self.assertEqual((b["state"], b["uncommitted"], b["ahead"]), ("abandoned", 1, 0))

    def test_session_without_branch_makes_all_uncertain(self):
        (self.home / ".claude" / "sessions" / f"{self.sleeper.pid}.json").write_text(json.dumps(
            {"pid": self.sleeper.pid, "sessionId": "nova", "cwd": str(self.box)}))
        self.assertEqual({b["state"] for b in self.branches().values()}, {"uncertain"})


class LifecycleLayers(unittest.TestCase):
    """`lifecycle()` rozhoduje, jestli `/next` nabídne chybějící krok cyklu.

    Vrací-li nesmysl, neselže nic – fronta práce jen tiše nabídne krok, který
    neexistuje, nebo zamlčí ten, který chybí. Přesně to se stalo, když se
    rámeček v `RULES.md` rozdělil na dvě vrstvy: funkce vracela syrové řádky
    bloku, takže z odsazeného pokračování osy vycházela „fáze“ jménem
    `/breakdown` a z komentáře pod rámečkem další položka.
    """

    def setUp(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("collect", COLLECT)
        self.c = importlib.util.module_from_spec(spec)
        sys.path.insert(0, str(COLLECT.parent))
        spec.loader.exec_module(self.c)
        # `collect.py` čte `RULES.md` z `$HOME` – tam je za běhu uživatelova
        # konfigurace a to je správně. V testu ale musí jít o **tenhle**
        # repozitář: na CI `$HOME/.claude` neexistuje, takže by `lifecycle()`
        # vrátila prázdno a test by padal na chybějícím souboru místo na vadě.
        self.c.RULES = ROOT / "RULES.md"

    def test_reads_both_layers_from_rules(self):
        out = self.c.lifecycle()
        self.assertEqual(set(out), {"osa", "kontroly"},
            f"z rámečku se přečetly jiné vrstvy než osa a kontroly: {sorted(out)}")
        for layer, steps in out.items():
            self.assertGreaterEqual(len(steps), 5,
                f"vrstva `{layer}` má jen {len(steps)} kroků: {steps}")
            for step in steps:
                self.assertRegex(step, r"^[a-z][a-z-]*$",
                    f"ve vrstvě `{layer}` není jméno kroku, ale `{step}`")

    def test_axis_order_matches_the_frame(self):
        # Osa je řada, takže na jejím pořadí stojí odvození chybějícího kroku.
        # Pořadí se čte z `RULES.md`, ne z konstanty tady – opsaný seznam by se
        # při přidání kroku rozešel a vypadal by přitom pořád platně.
        block = (ROOT / "RULES.md").read_text(encoding="utf-8")
        i = block.index("### Životní cyklus projektu")
        frame = block[block.index("```", i) + 3:]
        frame = frame[:frame.index("```")]
        axis_row = next(r for r in frame.splitlines() if r.split()[:1] == ["Osa"])
        first = re.findall(r"/([a-z][a-z-]*)", axis_row)[0]
        self.assertEqual(self.c.lifecycle()["osa"][0], first,
            "prvním krokem osy je něco jiného než v rámečku")

    def test_comment_under_frame_is_not_a_step(self):
        # Řádek bez kroků vrstvu nezakládá ani neukončuje; braný jako položka
        # by z věty „stojí v mezerách mezi kroky osy…“ udělal krok cyklu.
        for steps in self.c.lifecycle().values():
            self.assertNotIn("stojí", steps)
            self.assertFalse([s for s in steps if " " in s],
                "mezi kroky se dostal celý řádek rámečku")


if __name__ == "__main__":
    unittest.main()
