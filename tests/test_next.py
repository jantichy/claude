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
SKILL = ROOT / "skills" / "next" / "SKILL.md"


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
        (self.claude / "sessions" / f"{pid}.json").write_text(
            json.dumps(
                {
                    "pid": pid,
                    "sessionId": sid,
                    "cwd": "/projekt",
                    "name": sid,
                    "status": "waiting",
                }
            )
        )
        if transcript_lines is not None:
            project_dir = self.claude / "projects" / "-projekt"
            project_dir.mkdir(parents=True, exist_ok=True)
            (project_dir / f"{sid}.jsonl").write_text(
                "\n".join(json.dumps(r) for r in transcript_lines) + "\n"
            )

    def run_script(self, *args):
        env = dict(os.environ, HOME=str(self.home))
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            capture_output=True,
            text=True,
            env=env,
        )

    def idle(self):
        run = self.run_script("--project", "/projekt")
        self.assertEqual(run.returncode, 0, run.stderr)
        return {s["branch"]: s["session_id"] for s in json.loads(run.stdout)["idle"]}

    def dead_pid(self):
        p = subprocess.Popen(["true"])
        p.wait()
        return p.pid

    def test_branch_taken_from_last_entry(self):
        self.register(
            self.sleeper.pid,
            "ziva",
            [
                {"type": "user", "cwd": "/projekt/main", "gitBranch": "main"},
                {
                    "type": "assistant",
                    "cwd": "/projekt/dph",
                    "gitBranch": "specify-dph",
                },
                {"type": "attachment"},
            ],
        )
        run = self.run_script()
        self.assertEqual(run.returncode, 0, run.stderr)
        [s] = json.loads(run.stdout)["sessions"]
        self.assertEqual(
            (s["cwd"], s["branch"], s["self"]), ("/projekt/dph", "specify-dph", False)
        )

    def test_entry_of_crashed_process_ignored(self):
        self.register(
            self.dead_pid(), "mrtva", [{"cwd": "/projekt/x", "gitBranch": "x"}]
        )
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
        self.register(
            self.dead_pid(),
            "stara",
            [{"cwd": "/projekt/dph", "gitBranch": "specify-dph"}],
        )
        self.assertEqual(self.idle(), {"specify-dph": "stara"})

    def test_live_session_never_abandoned(self):
        # Táž session je i živá (obnovená v jiném okně) – mezi opuštěné nepatří,
        # ani když má v registru i starý záznam po spadlém procesu.
        self.register(
            self.dead_pid(),
            "obnovena",
            [{"cwd": "/projekt/dph", "gitBranch": "specify-dph"}],
        )
        self.register(self.sleeper.pid, "obnovena")
        self.assertEqual(self.idle(), {})

    def test_session_from_other_project_ignored(self):
        self.register(
            self.dead_pid(), "cizi", [{"cwd": "/jiny/dph", "gitBranch": "specify-dph"}]
        )
        self.assertEqual(self.idle(), {})

    def test_unreadable_registry_entry_is_not_empty_list(self):
        # Nečitelný záznam může patřit běžící session – kdyby se přeskočil,
        # nabídla by se její konverzace k obnovení podruhé.
        self.register(
            self.dead_pid(),
            "stara",
            [{"cwd": "/projekt/dph", "gitBranch": "specify-dph"}],
        )
        (self.claude / "sessions" / "rozbity.json").write_text("{nedopsano")
        run = self.run_script("--project", "/projekt")
        self.assertEqual(run.returncode, 2)
        self.assertEqual(run.stdout, "")

    def test_foreign_project_not_in_project(self):
        (self.claude / "sessions" / f"{self.sleeper.pid}.json").write_text(
            json.dumps({"pid": self.sleeper.pid, "sessionId": "cizi", "cwd": "/jiny"})
        )
        [s] = json.loads(self.run_script("--project", "/projekt").stdout)["sessions"]
        self.assertFalse(s["in_project"])

    def test_abandoned_session_carries_start_dir(self):
        self.register(
            self.dead_pid(),
            "stara",
            [
                {"cwd": "/projekt", "gitBranch": "main"},
                {"cwd": "/projekt/dph", "gitBranch": "specify-dph"},
            ],
        )
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
            "## Úkol 2\n- [x] krok\n- [ ] krok\n"
        )
        self.assertEqual((plan["open"], plan["done"], plan["next"]), (1, 1, ["Úkol 2"]))

    def test_plain_bullet_does_not_keep_plan_open(self):
        plan = self.c.parse_plan("## Úkol\n- [x] krok\n- poznámka\n")
        self.assertEqual(plan["open"], 0)

    def test_dependency_at_end_of_long_description(self):
        long_item = (
            "- [ ] **Úkol.** " + "vata " * 100 + "Čeká na odpověď podpory. Konec."
        )
        [item] = self.c.parse_items([long_item])
        self.assertEqual(item["waits"], "odpověď podpory")

    def test_dependency_as_bold_field(self):
        [item] = self.c.parse_items(
            ["- [ ] **Úkol.** Popis. **Čeká na:** kolo o fakturaci"]
        )
        self.assertEqual(item["waits"], "kolo o fakturaci")

    def test_quoted_dependency_inside_sentence_is_not_dependency(self):
        """Citace *Čeká na: nic* z popisu incidentu není závislost položky.

        Skript ji dřív vytáhl a uřízl na tečce, takže hotová položka vypadala
        jako čekající a model ji odsunul mezi položky, které na něco čekají.
        """
        [item] = self.c.parse_items(
            [
                "- [ ] **Kolo mimo verzi.** Blok v `todo.md` měl *Čeká na: nic*, "
                "ačkoli zadání tu funkci 1. 10. 2026 vyřadilo."
            ]
        )
        self.assertNotIn("waits", item)

    def test_dependency_inside_code_span_is_not_dependency(self):
        """Zápis `**Čeká na rozhodnutí:**` v apostrofech cituje cizí tvar.

        Skript z něj dřív vytáhl útržek věty jako závislost a model pak nad
        nesmyslnou hodnotou přemýšlel a položku odsunul mezi čekající.
        """
        [item] = self.c.parse_items(
            [
                "- [ ] **Ověřit.** Úkol skončí odstavcem `**Čeká na rozhodnutí:**` "
                "a vrácenými změnami."
            ]
        )
        self.assertNotIn("waits", item)

    def test_code_in_dependency_value_is_kept(self):
        [item] = self.c.parse_items(
            ["- [ ] **Úkol.** Popis. Čeká na: `/review` nad větví"]
        )
        self.assertEqual(item["waits"], "`/review` nad větví")

    def test_lowercase_clause_is_not_dependency(self):
        [item] = self.c.parse_items(
            [
                "- [ ] **Dorovnat.** Splnit to nešlo, protože `/consolidate` čeká na pilotní běh."
            ]
        )
        self.assertNotIn("waits", item)

    def test_nothing_is_not_dependency(self):
        for value in ("nic", "–", "**nic**"):
            with self.subTest(value=value):
                [item] = self.c.parse_items([f"- [ ] **Úkol.** Čeká na: {value}"])
                self.assertNotIn("waits", item)

    def test_future_date_after_title_parks_item(self):
        """Odložená položka se do fronty nesmí dostat dřív, než datum nastane.

        Zapisuje ji `/release` pro `/evaluate`, jehož spouštěčem je čas, ne
        výstup předchozího kroku. Nabídnout ji dřív znamená pustit vyhodnocení
        provozu nad daty, která ještě nevznikla – a to je šum vydávaný za nález.
        """
        [item] = self.c.parse_items(
            [
                "- [ ] **Vyhodnotit provoz přes `/evaluate`** – od 2099-10-12. Nasazeno v1.2."
            ]
        )
        self.assertEqual(item["not_before"], "2099-10-12")
        self.assertTrue(item["waiting"])

    def test_past_date_does_not_park_item(self):
        """Druhý směr: po tom dni se položka musí nabízet jako každá jiná.

        Falešné parkování je ta horší polovina – položka nezmizí hlučně, jen se
        nikdy nenabídne, a nikde to nesvítí.
        """
        [item] = self.c.parse_items(["- [ ] **Dávno platí** – od 2020-01-01."])
        self.assertEqual(item["not_before"], "2020-01-01")
        self.assertFalse(item["waiting"])

    def test_date_inside_description_is_not_a_park(self):
        """Datum ve zdůvodnění uprostřed popisu odklad neznamená.

        Proto se hledá jen hned za názvem: první verze prohledávala začátek
        textu a věta „sazba platí od <datum>“ jí položku skryla.
        """
        [item] = self.c.parse_items(
            ["- [ ] **Úkol** – pracuje se na tom, protože sazba platí od 2099-01-01."]
        )
        self.assertNotIn("not_before", item)
        self.assertNotIn("waiting", item)

    def test_item_without_date_has_no_parking_fields(self):
        """Běžná položka nesmí pole vůbec dostat – prázdné pole se čte jako údaj."""
        [item] = self.c.parse_items(["- [ ] **Běžný úkol** – bez data."])
        self.assertNotIn("not_before", item)

    def test_items_above_first_section_are_not_swallowed(self):
        """Fronta psaná bez `## ` nadpisů nesmí zmizet celá.

        `sections()` zahazuje řádky před prvním nadpisem své úrovně, takže
        `todo.md`, který má jen `#` a pod ním rovnou odrážky, dal prázdnou frontu –
        a `/next` pak tvrdil, že projekt nemá co dělat. Je to tichá vada: skript
        skončí kódem 0 a prázdný seznam vypadá jako prázdná fronta. Doloženo
        28. 9. 2026 na `todo.md` repozitáře s konfigurací, kde takhle zmizelo
        přes třicet otevřených položek.
        """
        todo, _, _ = self.c.parse_todo(
            "# Co zbývá\n\nÚvodní odstavec.\n\n- [ ] **První úkol.** Popis.\n"
            "- [x] **Hotové.** Už ne.\n\n### Starší dávka\n\n- [ ] **Druhý úkol.** Popis.\n"
        )
        self.assertEqual(
            [
                (p["subsection"], [i["title"] for i in p["items"]])
                for s in todo
                for p in s["parts"]
            ],
            [(None, ["První úkol"]), ("Starší dávka", ["Druhý úkol"])],
        )

    def test_plain_list_beside_checkboxes_is_commentary(self):
        """Číslovaný nebo odrážkový seznam vedle zaškrtávátek není fronta.

        `todo.md` vedle položek nese i výčty, které k nim něco vysvětlují –
        pořadí, v jakém se mají dělat, nebo výčet kandidátů. Bez zaškrtávátka
        se od položky liší jedině tím, a tak se do fronty počítaly jako úkoly:
        čtyři řádky návodu „čím začít u skillů“ nafoukly zdejší podsekci z 31
        položek na 35. Vada je tichá – nadbytečná položka vypadá jako práce.
        """
        todo, _, _ = self.c.parse_todo(
            "# TODO\n\n- [ ] **Skutečný úkol.** Text.\n\n"
            "**Čím začít (platí pro položky výš).**\n\n"
            "1. **První krok.** Text.\n2. **Druhý krok.** Text.\n"
        )
        self.assertEqual(
            [i["title"] for s in todo for p in s["parts"] for i in p["items"]],
            ["Skutečný úkol"],
        )

    def test_plain_list_without_any_checkbox_stays_a_queue(self):
        """Druhý směr: fronta psaná bez zaškrtávátek se nesmí vyprázdnit.

        Projekty vedou `todo.md` i jako holý seznam a `backlog.md` tak vypadá
        vždycky – pravidlo proto platí jen tam, kde se zaškrtávátka opravdu
        vyskytují, a jinde zůstává starý výklad.
        """
        todo, _, _ = self.c.parse_todo(
            "# TODO\n\n- **První.** Text.\n- **Druhý.** Text.\n"
        )
        self.assertEqual(
            [i["title"] for s in todo for p in s["parts"] for i in p["items"]],
            ["První", "Druhý"],
        )

    def test_interrupted_block_is_one_item(self):
        """Blok `### ` v `## Přerušený běh` je jedna položka, ne podsekce.

        `/end` píše každé přerušení jako blok pod nadpisem `### ` a obecný
        parser v něm viděl podsekci, ve které počítal jen zaškrtávátka – sekce
        vyšla s nulou položek a `/next` ji, ačkoli ji má řadit úplně první,
        nenabídl vůbec. Doloženo 11. 10. 2026 při přerušení migrace disku.
        Výčet zbývající práce uvnitř bloku se za položky fronty počítat nesmí.
        """
        todo, _, _ = self.c.parse_todo(
            "# TODO\n\n## Přerušený běh\n\n"
            "### /review branch – přerušeno 2026-10-08\n\n"
            "Rozdělaná práce, dokončuje se jako první.\n\n"
            "- [ ] **Nález o zámku.** Varianty a doporučení.\n"
            "- [ ] **Nález o mailu.** Varianty.\n\n"
            "**Jak pokračovat:** `/review branch` od začátku. Fronta se dojde podle\n"
            "výčtu výš.\n\n"
            "### Migrace disku – přerušeno 2026-10-11\n\n"
            "**Jak pokračovat:** položkou Přesun klientů. Pak zbytek.\n\n"
            "## Úkoly\n\n- [ ] **Běžný úkol.** Text.\n"
        )
        self.assertEqual(
            [
                (
                    s["section"],
                    [(i["title"], i["text"]) for p in s["parts"] for i in p["items"]],
                )
                for s in todo
            ],
            [
                (
                    "Přerušený běh",
                    [
                        (
                            "/review branch – přerušeno 2026-10-08",
                            "`/review branch` od začátku.",
                        ),
                        (
                            "Migrace disku – přerušeno 2026-10-11",
                            "položkou Přesun klientů.",
                        ),
                    ],
                ),
                ("Úkoly", [("Běžný úkol", "Text.")]),
            ],
        )

    def test_interrupted_section_in_old_shape_keeps_its_items(self):
        """Druhý směr: zápis přerušení odrážkami bez bloků `### ` nezmizí."""
        todo, _, _ = self.c.parse_todo(
            "# TODO\n\n## Přerušený běh\n\n- [ ] **Zbylý nález.** Text.\n"
        )
        self.assertEqual(
            [i["title"] for s in todo for p in s["parts"] for i in p["items"]],
            ["Zbylý nález"],
        )

    def test_sections_still_separate_items_that_have_headings(self):
        """Druhý směr: fronta s `## ` sekcemi se nesmí slít do jedné bezejmenné."""
        todo, _, _ = self.c.parse_todo(
            "# TODO\n\n- [ ] **Nezařazený.** Text.\n\n## Probíhá\n\n- [ ] **V sekci.** Text.\n"
        )
        self.assertEqual(
            [
                (s["section"], [i["title"] for p in s["parts"] for i in p["items"]])
                for s in todo
            ],
            [(None, ["Nezařazený"]), ("Probíhá", ["V sekci"])],
        )


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
        self.env = dict(
            os.environ,
            HOME=str(self.home),
            GIT_AUTHOR_NAME="t",
            GIT_AUTHOR_EMAIL="t@t",
            GIT_COMMITTER_NAME="t",
            GIT_COMMITTER_EMAIL="t@t",
        )
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
        self.git(
            *self.bare,
            "worktree",
            "add",
            "-q",
            "-b",
            "specify-dph",
            str(self.box / "dph"),
            "main",
        )
        vat_todo = self.box / "dph" / "docs" / "todo.md"
        vat_todo.write_text(
            TODO.replace(
                "- **Stav:** čeká\n- **Větev:** `specify-dph`",
                "- **Stav:** rozhoduje se\n- **Větev:** `specify-dph`",
            )
        )
        self.git("-C", str(self.box / "dph"), "commit", "-qam", "DPH rozhoduje se")
        self.git(*self.bare, "branch", "specify-faktury", "main")
        self.sleeper = subprocess.Popen(["sleep", "60"])

    def tearDown(self):
        self.sleeper.kill()
        self.sleeper.wait()
        self.tmp.cleanup()

    def git(self, *args):
        subprocess.run(
            ["git", *args],
            check=True,
            env=getattr(self, "env", None),
            capture_output=True,
        )

    def session(self, pid, sid, cwd, branch):
        claude = self.home / ".claude"
        (claude / "sessions" / f"{pid}.json").write_text(
            json.dumps(
                {"pid": pid, "sessionId": sid, "cwd": str(self.box), "name": sid}
            )
        )
        project_dir = claude / "projects" / "-projekt"
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / f"{sid}.jsonl").write_text(
            json.dumps({"cwd": str(self.box)})
            + "\n"
            + json.dumps({"cwd": cwd, "gitBranch": branch})
            + "\n"
        )

    def collect(self):
        run = subprocess.run(
            [sys.executable, str(COLLECT), str(self.box)],
            capture_output=True,
            text=True,
            env=self.env,
        )
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
        vat_todo.write_text(text[:start] + text[text.index("### Kolo o fakturaci") :])
        self.git("-C", str(self.box / "dph"), "commit", "-qam", "DPH zapsáno")
        self.assertEqual(self.collect()["rounds"][0]["branch_state"], "merge_pending")

    def test_abandoned_branch_with_session_to_resume(self):
        self.session(self.dead_pid(), "stara", str(self.box / "dph"), "specify-dph")
        b = self.branches()["specify-dph"]
        self.assertEqual(
            (b["state"], b["resume"]["session_id"], b["resume"]["start_cwd"]),
            ("abandoned", "stara", str(self.box)),
        )
        self.assertEqual(b["rounds"], ["Kolo o DPH"])

    def test_occupied_branch_without_commit(self):
        # `--no-merged` větev bez commitu nevypíše; živá session nad ní ji musí přidat.
        self.session(
            self.sleeper.pid, "ziva", str(self.box / "faktury"), "specify-faktury"
        )
        b = self.branches()["specify-faktury"]
        self.assertEqual((b["state"], b["session"]), ("occupied", "ziva"))

    def test_session_in_worktree_reporting_main_occupies_its_branch(self):
        """Živá session ve worktree větve obsadí tu větev, i když transcript hlásí `main`.

        Session startuje v kořeni kontejneru a `gitBranch` je větev adresáře, odkud
        se naposled pouštěl git – u práce ve worktree, kde se git volá z kořene,
        tedy hlavní větev. Větev se proto bere z worktree pod `cwd`; jinak se živá
        session u své větve nenajde a ta se nabídne jako opuštěná k rozjetí podruhé.
        """
        self.session(self.sleeper.pid, "ziva", str(self.box / "dph" / "docs"), "main")
        b = self.branches()["specify-dph"]
        self.assertEqual((b["state"], b.get("session")), ("occupied", "ziva"))

    def test_idle_session_in_worktree_reporting_main_resumes_its_branch(self):
        """Opuštěná session ve worktree se nabídne k obnovení u větve toho worktree."""
        self.session(self.dead_pid(), "stara", str(self.box / "dph"), "main")
        b = self.branches()["specify-dph"]
        self.assertEqual(
            (b["state"], b["resume"]["session_id"]), ("abandoned", "stara")
        )

    def test_session_in_container_root_keeps_branch_from_transcript(self):
        """`cwd` mimo každý worktree (kořen kontejneru) nechá větev z transcriptu."""
        self.session(self.sleeper.pid, "ziva", str(self.box), "specify-dph")
        self.assertEqual(self.branches()["specify-dph"]["state"], "occupied")

    def test_clean_main_not_reported_as_occupied(self):
        # Session, která startuje v kořeni kontejneru a vlastní větev si ještě nezaložila,
        # hlásí jako svou hlavní větev. Dokud v ní nic neleží, nesmí se vypsat vůbec –
        # jinak ji `/next` podle vlastního pravidla přestane nabízet.
        self.session(self.sleeper.pid, "bez-vetve", str(self.box), "main")
        self.assertNotIn("main", self.branches())

    def test_main_with_work_stays_reported(self):
        # Druhý směr téhož: leží-li v hlavní větvi neuložená změna, vypsat se musí.
        (self.box / "main" / "rozdelane.txt").write_text("práce")
        self.session(self.sleeper.pid, "bez-vetve", str(self.box), "main")
        b = self.branches()["main"]
        self.assertEqual((b["state"], b["uncommitted"]), ("occupied", 1))

    def test_run_from_worktree_subdir_finds_container(self):
        run = subprocess.run(
            [sys.executable, str(COLLECT), str(self.box / "dph" / "docs")],
            capture_output=True,
            text=True,
            env=self.env,
        )
        data = json.loads(run.stdout)
        self.assertEqual(
            (data["layout"], Path(data["root"]).resolve(), data["current"]["branch"]),
            ("worktree", self.box.resolve(), "specify-dph"),
        )

    def test_branch_without_work_not_abandoned(self):
        # Větev bez commitu a bez neuložených změn není zapomenutá práce – buď se
        # nevypíše vůbec, nebo jako prázdná; opuštěná být nesmí.
        # Worktree bez práce je přesně ten případ, kdy se větev vypíše – po sloučení zůstal stát.
        self.git(
            *self.bare,
            "worktree",
            "add",
            "-q",
            str(self.box / "faktury"),
            "specify-faktury",
        )
        self.assertEqual(self.branches()["specify-faktury"]["state"], "empty")

    def test_uncommitted_changes_in_other_worktree_are_work(self):
        self.git(
            *self.bare,
            "worktree",
            "add",
            "-q",
            "-b",
            "export",
            str(self.box / "export"),
            "main",
        )
        (self.box / "export" / "novy.txt").write_text("rozdělané")
        b = self.branches()["export"]
        self.assertEqual(
            (b["state"], b["uncommitted"], b["ahead"]), ("abandoned", 1, 0)
        )

    def test_session_without_branch_makes_all_uncertain(self):
        (self.home / ".claude" / "sessions" / f"{self.sleeper.pid}.json").write_text(
            json.dumps(
                {"pid": self.sleeper.pid, "sessionId": "nova", "cwd": str(self.box)}
            )
        )
        self.assertEqual({b["state"] for b in self.branches().values()}, {"uncertain"})

    def test_interrupted_run_in_subproject_is_offered(self):
        """Přerušený běh v podprojektu se nabídne i z kořene, zbytek jeho fronty ne.

        `/end` zapisuje do `todo.md` projektu, kde session stojí, u podprojektu
        klientské složky tedy do podsložky – často s vlastním repozitářem, který
        git ignoruje. Příkaz *Fáze 1* ho najde do třetí úrovně, `collect.py` četl jen
        kořen a přerušenou práci, kterou má řadit první, neviděl. Hledá se stejně
        hluboko a se stejnými výjimkami: hlubší soubor ani `node_modules` se
        nečtou, a ostatní úkoly podprojektu patří k jinému projektu.
        """
        block = (
            "# TODO\n\n## Přerušený běh\n\n### {}\n\n"
            "**Jak pokračovat:** položkou Import. Pak zbytek.\n\n"
            "## Úkoly\n\n- [ ] **Úkol podprojektu.** Text.\n"
        )
        for rel, title in (
            ("zakazka/docs", "Migrace – přerušeno 2026-10-12"),
            ("node_modules/balik/docs", "Z node_modules"),
            ("a/b/c", "Příliš hluboko"),
        ):
            (self.box / "main" / rel).mkdir(parents=True)
            (self.box / "main" / rel / "todo.md").write_text(block.format(title))
        todo = self.collect()["todo"]
        items = [
            (s["section"], i) for s in todo for p in s["parts"] for i in p["items"]
        ]
        self.assertEqual(
            [(s, i["title"], i.get("project")) for s, i in items],
            [
                ("Přerušený běh", "Migrace – přerušeno 2026-10-12", "zakazka"),
                ("Probíhá", "Export faktur", None),
            ],
        )
        self.assertEqual(items[0][1]["text"], "položkou Import.")

    def test_interrupted_run_in_branch_worktree_is_offered_once(self):
        """Přerušený běh zapsaný ve worktree větve se najde, blok z hlavní větve jen jednou.

        Ve worktree layoutu zapíše `/end` blok do `todo.md` větve, ve které
        session stála; fronta se přitom čte z hlavní větve, takže blok zůstal
        neviditelný a na přerušenou práci se došlo jen ručním grepem. Blok, který
        leží v hlavní větvi a větev ho smazala nebo zdědila beze změny, se nesmí
        nabídnout dvakrát.
        """
        block = (
            "## Přerušený běh\n\n### {}\n\n**Jak pokračovat:** krokem {}. Pak dál.\n\n"
        )
        main_todo = self.box / "main" / "docs" / "todo.md"
        main_todo.write_text(
            TODO.replace(
                "## Probíhá", block.format("Z hlavní větve", "A") + "## Probíhá"
            )
        )
        self.git("-C", str(self.box / "main"), "commit", "-qam", "přerušeno v main")
        # Větev dph hlavní blok nemá (smazala ho) a nese vlastní.
        vat_todo = self.box / "dph" / "docs" / "todo.md"
        vat_todo.write_text(
            vat_todo.read_text().replace(
                "## Probíhá", block.format("Kroky po sešití", "B") + "## Probíhá"
            )
        )
        self.git("-C", str(self.box / "dph"), "commit", "-qam", "přerušeno ve větvi")
        # Worktree, které hlavní blok zdědilo beze změny, ho nesmí zdvojit.
        self.git(
            *self.bare,
            "worktree",
            "add",
            "-q",
            "-b",
            "kopie",
            str(self.box / "kopie"),
            "main",
        )
        [section] = [
            s for s in self.collect()["todo"] if s["section"] == "Přerušený běh"
        ]
        items = [i for p in section["parts"] for i in p["items"]]
        self.assertEqual(
            [(i["title"], i.get("branch"), i.get("project")) for i in items],
            [("Z hlavní větve", None, None), ("Kroky po sešití", "specify-dph", None)],
        )
        self.assertEqual(items[1]["text"], "krokem B.")


OPERATIVE_CLAUDE = """# Firma

- **Slug:** `firma`
- **Struktura:** CLAUDE.md

## Přerušený běh

### Přejmenování smluv – přerušeno 2026-10-29

**Jak pokračovat:** dokončit plán přesunu v adresáři `Smlouvy`. Pak zbytek.

## Smlouvy

- **Bod u tématu.** Patří k zápisu o tématu, ne do fronty.

## Otevřené body

- **Doplnit výpis za září.** Text.
"""


class OperativeProject(unittest.TestCase):
    """`collect.py` nad operativním projektem, který má jen `CLAUDE.md` a často ani git.

    `/end` v něm zapisuje přerušení do `CLAUDE.md`, protože `todo.md` tam
    nevzniká; sběr, který četl jen `todo.md` a bez gitu skončil chybou, ho
    neviděl. Hlídá se i opačný směr: soubory v adresáři patří uživateli, takže
    jeho `plan.md` se nesmí vydávat za implementační plán, a adresář bez
    deklarace režimu dál chybou končí.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name) / "firma"
        (self.dir / "Smlouvy").mkdir(parents=True)
        (self.dir / "plan.md").write_text("- [ ] Úkol uživatele\n")

    def tearDown(self):
        self.tmp.cleanup()

    def collect(self, cwd):
        return subprocess.run(
            [sys.executable, str(COLLECT)],
            capture_output=True,
            text=True,
            cwd=cwd,
            env=dict(os.environ, GIT_CEILING_DIRECTORIES=self.tmp.name),
        )

    def test_queue_read_from_claude_md_without_git(self):
        (self.dir / "CLAUDE.md").write_text(OPERATIVE_CLAUDE)
        run = self.collect(self.dir / "Smlouvy")
        self.assertEqual(run.returncode, 0, run.stderr)
        data = json.loads(run.stdout)
        self.assertEqual((data["layout"], data["docs"]), ("none", "CLAUDE.md"))
        self.assertEqual(
            [
                (s["section"], i["title"])
                for s in data["todo"]
                for p in s["parts"]
                for i in p["items"]
            ],
            [
                ("Přerušený běh", "Přejmenování smluv – přerušeno 2026-10-29"),
                ("Otevřené body", "Doplnit výpis za září"),
            ],
        )
        self.assertIsNone(data["plan"])
        self.assertEqual(data["branches"], [])

    def test_directory_without_declaration_is_not_a_project(self):
        (self.dir / "CLAUDE.md").write_text(
            OPERATIVE_CLAUDE.replace("CLAUDE.md\n", "docs/\n", 1)
        )
        run = self.collect(self.dir)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("není git repozitář", run.stderr)


class LifecycleLayers(unittest.TestCase):
    """`lifecycle()` rozhoduje, jestli `/next` nabídne chybějící krok cyklu.

    Vrací-li nesmysl, neselže nic – fronta práce jen tiše nabídne krok, který
    neexistuje, nebo zamlčí ten, který chybí. Přesně to se stalo, když se
    rámeček v `~/.claude/standards/rules.md` rozdělil na dvě vrstvy: funkce vracela syrové řádky
    bloku, takže z odsazeného pokračování osy vycházela „fáze“ jménem
    `/breakdown` a z komentáře pod rámečkem další položka.
    """

    def setUp(self):
        import importlib.util

        spec = importlib.util.spec_from_file_location("collect", COLLECT)
        self.c = importlib.util.module_from_spec(spec)
        sys.path.insert(0, str(COLLECT.parent))
        spec.loader.exec_module(self.c)
        # `collect.py` čte `~/.claude/standards/rules.md` z `$HOME` – tam je za běhu uživatelova
        # konfigurace a to je správně. V testu ale musí jít o **tenhle**
        # repozitář: na CI `$HOME/.claude` neexistuje, takže by `lifecycle()`
        # vrátila prázdno a test by padal na chybějícím souboru místo na vadě.
        self.c.RULES = ROOT / "standards" / "rules.md"

    def test_reads_both_layers_from_rules(self):
        out = self.c.lifecycle()
        self.assertEqual(
            set(out),
            {"osa", "kontroly"},
            f"z rámečku se přečetly jiné vrstvy než osa a kontroly: {sorted(out)}",
        )
        for layer, steps in out.items():
            self.assertGreaterEqual(
                len(steps), 5, f"vrstva `{layer}` má jen {len(steps)} kroků: {steps}"
            )
            for step in steps:
                self.assertRegex(
                    step,
                    r"^[a-z][a-z-]*$",
                    f"ve vrstvě `{layer}` není jméno kroku, ale `{step}`",
                )

    def test_axis_order_matches_the_frame(self):
        # Osa je řada, takže na jejím pořadí stojí odvození chybějícího kroku.
        # Pořadí se čte z `~/.claude/standards/rules.md`, ne z konstanty tady – opsaný seznam by se
        # při přidání kroku rozešel a vypadal by přitom pořád platně.
        block = (ROOT / "standards" / "rules.md").read_text(encoding="utf-8")
        i = block.index("### Životní cyklus projektu")
        frame = block[block.index("```", i) + 3 :]
        frame = frame[: frame.index("```")]
        axis_row = next(r for r in frame.splitlines() if r.split()[:1] == ["Osa"])
        first = re.findall(r"/([a-z][a-z-]*)", axis_row)[0]
        self.assertEqual(
            self.c.lifecycle()["osa"][0],
            first,
            "prvním krokem osy je něco jiného než v rámečku",
        )

    def test_comment_under_frame_is_not_a_step(self):
        # Řádek bez kroků vrstvu nezakládá ani neukončuje; braný jako položka
        # by z věty „stojí v mezerách mezi kroky osy…“ udělal krok cyklu.
        for steps in self.c.lifecycle().values():
            self.assertNotIn("stojí", steps)
            self.assertFalse(
                [s for s in steps if " " in s],
                "mezi kroky se dostal celý řádek rámečku",
            )


class OutputBudget(unittest.TestCase):
    """`fit_budget` rozhoduje, jestli se výstup vejde do kontextu modelu.

    Selhává tiše a ve svůj prospěch: harness výstup nad stropem nezahodí, ale
    uloží do souboru a modelu dá náhled – takže `/next` vypadá, že proběhl,
    a přitom si data dolovává zpátky dalšími voláními. Přesně to se stalo
    29. 9. 2026 nad frontou o 74 položkách: 39 kB, useknuto, běh 4:30 místo
    půl minuty. Testují se oba směry: nad rozpočtem se krátit musí, pod ním
    se krátit nesmí – zbytečně zkrácený popis vezme skillu podklad pro nabídku.
    """

    def setUp(self):
        import importlib.util

        spec = importlib.util.spec_from_file_location("collect_budget", COLLECT)
        self.c = importlib.util.module_from_spec(spec)
        sys.path.insert(0, str(COLLECT.parent))
        spec.loader.exec_module(self.c)

    def result_with(self, count, text_len):
        items = [
            {"title": f"Polozka {i}", "text": "x" * text_len, "done": False}
            for i in range(count)
        ]
        return {
            "todo": [
                {"section": "Fronta", "parts": [{"subsection": None, "items": items}]}
            ]
        }

    def test_small_queue_keeps_full_texts(self):
        result = self.result_with(5, self.c.TEXT_LIMIT)
        self.assertIsNone(
            self.c.fit_budget(result),
            "krátilo se, přestože se výstup do rozpočtu vešel",
        )
        for item in result["todo"][0]["parts"][0]["items"]:
            self.assertEqual(
                len(item["text"]),
                self.c.TEXT_LIMIT,
                "popis se zkrátil u fronty, která je pod rozpočtem",
            )

    def test_large_queue_fits_into_budget(self):
        result = self.result_with(300, self.c.TEXT_LIMIT)
        self.assertGreater(
            self.c.encoded_size(result),
            self.c.BUDGET,
            "testovací fronta rozpočet vůbec nepřekročila, test by neměřil nic",
        )
        limit = self.c.fit_budget(result)
        self.assertLessEqual(
            self.c.encoded_size(result),
            self.c.BUDGET,
            f"výstup zůstal nad rozpočtem i po zkrácení na {limit}",
        )
        self.assertIn(
            limit, self.c.TEXT_STEPS, f"vrácený limit `{limit}` není z `TEXT_STEPS`"
        )

    def test_titles_survive_every_step(self):
        # Název je jediné, z čeho skill sestaví jednořádkový výpis; zmizet nesmí
        # ani v kroku, kde se popisy zahazují celé.
        result = self.result_with(4000, self.c.TEXT_LIMIT)
        self.assertEqual(
            self.c.fit_budget(result),
            0,
            "fronta téhle velikosti se musí dostat až na zahození popisů",
        )
        items = result["todo"][0]["parts"][0]["items"]
        self.assertEqual(len(items), 4000, "zkrácení ubralo položky, ne jen popisy")
        for item in items:
            self.assertTrue(item["title"], "položka přišla o název")
            self.assertNotIn("text", item, "popis zůstal i v kroku, který je zahazuje")


BLOCK = "## Přerušený běh\n\n### {}\n\n**Jak pokračovat:** krokem A.\n\n## Další\n\n- Mimo.\n"


def find_command():
    """Příkaz *Fáze 1* vytažený ze `SKILL.md` – skill ho pouští doslova."""
    [cmd] = re.findall(r"```bash\n(.+?)\n```", SKILL.read_text(), re.S)
    return cmd


SORTED_TODO = (
    "# Fronta\n\n## Přerušený běh\n\n### Review – přerušeno 2026-11-03\n\n**Jak pokračovat:** `/review`.\n\n## Teď\n\n"
    + "".join(f"- [ ] ◐ **Úkol {n}.** Popis {n}.\n" for n in range(1, 13))
    + "- [ ] ○ **Čekající.** Čeká na odpověď podpory.\n\n## Později\n\n- [ ] ● **Velký.** Popis.\n"
)


class SortedQueue(unittest.TestCase):
    """Srovnaný `todo.md` čte `collect.py` mechanicky: pořadí i velikost nese soubor.

    Vrátí jen vrchol fronty a zbytek jako počet, protože výpis celé fronty byl
    největší položka času běhu. Chyba je tichá v obou směrech: nesrovnaný soubor
    zkrácený na vrchol by ukázal náhodné pořadí jako prioritu, a srovnaný, který
    se nezkrátí, vrátí běh na dřívějších 36 s.
    """

    def setUp(self):
        import importlib.util

        sys.path.insert(0, str(COLLECT.parent))
        spec = importlib.util.spec_from_file_location("collect", COLLECT)
        self.c = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.c)

    def parsed(self, text=SORTED_TODO):
        return self.c.parse_todo(text)[0]

    def test_size_is_read_and_stripped_from_title(self):
        items = self.c.queue_items(self.parsed())
        self.assertEqual((items[0]["title"], items[0]["size"]), ("Úkol 1", "◐"))

    def test_sorted_file_is_not_legacy(self):
        self.assertIsNone(self.c.legacy_shape(self.parsed(), SORTED_TODO))

    def test_unsized_item_makes_file_legacy(self):
        text = SORTED_TODO.replace("- [ ] ◐ **Úkol 3.**", "- [ ] **Úkol 3.**")
        self.assertEqual(
            self.c.legacy_shape(self.parsed(text), text),
            ["1 z 14 položek bez velikosti"],
        )

    def test_plain_bullets_make_file_legacy(self):
        text = "# Fronta\n\n## Teď\n\n- ◐ **Jedna.** Text.\n"
        self.assertIn(
            "položky nejsou zaškrtávátka", self.c.legacy_shape(self.parsed(text), text)
        )

    def test_special_section_needs_no_size_and_takes_no_slot(self):
        text = SORTED_TODO.replace(
            "## Teď\n",
            "## Parkované v session\n\n- [ ] **Bod bez velikosti.**\n\n## Teď\n",
        )
        todo = self.c.parse_todo(text)[0]
        self.assertIsNone(self.c.legacy_shape(todo, text))
        todo = self.c.top_of_queue(todo)
        parked = next(s for s in todo if s["section"] == "Parkované v session")
        self.assertEqual(len(parked["parts"][0]["items"]), 1)
        now = next(s for s in todo if s["section"] == "Teď")
        self.assertEqual(now["more"], 2)

    def test_decided_answers_are_plain_bullets_and_kept(self):
        text = (
            SORTED_TODO
            + "\n# Mimo frontu\n\n## Rozhodnuto k zapracování\n\n### /review – dávka\n\n- N1: přijato.\n"
        )
        todo = self.c.top_of_queue(self.c.parse_todo(text)[0])
        decided = next(s for s in todo if s["section"] == "Rozhodnuto k zapracování")
        self.assertEqual(
            [i["title"] for p in decided["parts"] for i in p["items"]], ["N1: přijato."]
        )
        self.assertIsNone(self.c.legacy_shape(self.c.parse_todo(text)[0], text))

    def test_missing_queue_heading_makes_file_legacy(self):
        text = SORTED_TODO.replace("# Fronta\n", "# TODO\n")
        self.assertIn(
            "chybí nadpis `# Fronta`",
            self.c.legacy_shape(self.c.parse_todo(text)[0], text),
        )

    def test_checkbox_outside_work_bands_does_not_hide_plain_items(self):
        text = "# Fronta\n\n## Parkované v session\n\n- [ ] Bod.\n\n## Teď\n\n- **Holá.** Text.\n"
        todo = self.c.parse_todo(text)[0]
        self.assertEqual([i["title"] for i in self.c.queue_items(todo)], ["Holá"])
        self.assertIn("položky nejsou zaškrtávátka", self.c.legacy_shape(todo, text))

    def test_nested_checklist_does_not_hide_plain_items(self):
        text = "# TODO\n\n## Úkoly\n\n- **Položka.** Text.\n  - [ ] krok\n"
        items = self.c.queue_items(self.c.parse_todo(text)[0])
        self.assertEqual([i["title"] for i in items], ["Položka"])

    def test_top_keeps_limit_in_file_order_and_counts_rest(self):
        todo = self.c.top_of_queue(self.parsed())
        now = next(s for s in todo if s["section"] == "Teď")
        titles = [i["title"] for p in now["parts"] for i in p["items"]]
        self.assertEqual(titles[:10], [f"Úkol {n}" for n in range(1, 11)])
        self.assertEqual(now["more"], 2)
        later = next(s for s in todo if s["section"] == "Později")
        self.assertEqual((later["parts"], later["more"]), ([], 1))

    def test_waiting_item_does_not_take_a_slot(self):
        todo = self.c.top_of_queue(self.parsed())
        items = self.c.queue_items(todo)
        waiting = [i for i in items if i.get("waits")]
        self.assertEqual([i["title"] for i in waiting], ["Čekající"])
        self.assertNotIn("text", waiting[0])
        self.assertEqual(len(items), 11)

    def test_interrupted_run_is_kept_whole(self):
        todo = self.c.top_of_queue(self.parsed(), limit=0)
        self.assertEqual(
            [
                i["title"]
                for s in todo
                if s["section"] == "Přerušený běh"
                for p in s["parts"]
                for i in p["items"]
            ],
            ["Review – přerušeno 2026-11-03"],
        )

    def test_cli_cuts_sorted_queue_unless_all(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            env = dict(
                os.environ,
                GIT_CEILING_DIRECTORIES=tmp,
                GIT_AUTHOR_NAME="t",
                GIT_AUTHOR_EMAIL="t@t",
                GIT_COMMITTER_NAME="t",
                GIT_COMMITTER_EMAIL="t@t",
            )
            (d / "docs").mkdir()
            (d / "docs" / "todo.md").write_text(
                SORTED_TODO.split("## Teď")[0].split("## Přerušený běh")[0]
                + "## Teď"
                + SORTED_TODO.split("## Teď")[1]
            )
            subprocess.run(
                ["git", "init", "-q", "-b", "main", str(d)], check=True, env=env
            )
            subprocess.run(["git", "-C", str(d), "add", "-A"], check=True, env=env)
            subprocess.run(
                ["git", "-C", str(d), "commit", "-q", "-m", "x"], check=True, env=env
            )

            def count(*flags):
                out = subprocess.run(
                    [sys.executable, str(COLLECT), *flags, str(d)],
                    capture_output=True,
                    text=True,
                    check=True,
                    env=env,
                ).stdout
                data = json.loads(out)
                return data["legacy"], len(self.c.queue_items(data["todo"]))

            self.assertEqual(count(), (None, 11))
            self.assertEqual(count("--all"), (None, 14))


class FindInterrupted(unittest.TestCase):
    """Příkaz, kterým `/next` hledá zápis přerušené práce, než postaví nabídku.

    Chyba je tichá v obou směrech. Nenajde-li příkaz zápis, který existuje,
    skill postaví nabídku a přerušená práce zůstane ležet – hlídá se proto
    zápis v `CLAUDE.md` operativního projektu bez gitu, kam ho `/end` píše,
    protože `todo.md` takový projekt nemá, i zápis v `docs/todo.md` běžného
    repozitáře. A nepustí-li bez zápisu `collect.py`, skill nemá z čeho stavět
    a musí ho volat znovu – tedy kolo navíc, kterému se příkaz vyhýbá.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.env = dict(
            os.environ,
            GIT_CEILING_DIRECTORIES=self.tmp.name,
            GIT_AUTHOR_NAME="t",
            GIT_AUTHOR_EMAIL="t@t",
            GIT_COMMITTER_NAME="t",
            GIT_COMMITTER_EMAIL="t@t",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def run_in(self, cwd):
        run = subprocess.run(
            ["bash", "-c", find_command()],
            cwd=cwd,
            capture_output=True,
            text=True,
            env=self.env,
        )
        self.assertEqual(run.returncode, 0, run.stderr)
        return run.stdout

    def test_claude_md_of_operative_project_without_git(self):
        d = self.base / "firma"
        d.mkdir()
        (d / "CLAUDE.md").write_text(
            "# Firma\n\n- **Struktura:** CLAUDE.md\n\n" + BLOCK.format("Smlouvy")
        )
        out = self.run_in(d)
        self.assertRegex(out, r"(?m)^==> .*/firma/CLAUDE\.md$")
        self.assertIn("### Smlouvy", out)
        self.assertNotIn("Mimo.", out)

    def test_todo_in_git_repository_still_found(self):
        d = self.base / "repo"
        (d / "docs").mkdir(parents=True)
        (d / "docs" / "todo.md").write_text("# TODO\n\n" + BLOCK.format("Review"))
        (d / "CLAUDE.md").write_text("# Repo\n\n- **Struktura:** docs/\n")
        subprocess.run(["git", "init", "-q", str(d)], check=True, env=self.env)
        out = self.run_in(d)
        self.assertEqual(out.count("==> "), 1, out)
        self.assertIn("docs/todo.md", out)
        self.assertIn("### Review", out)

    def test_without_interruption_falls_through_to_collect(self):
        d = self.base / "repo"
        (d / "docs").mkdir(parents=True)
        (d / "docs" / "todo.md").write_text("# TODO\n\n## Úkoly\n\n- [ ] Něco.\n")
        subprocess.run(
            ["git", "init", "-q", "-b", "main", str(d)], check=True, env=self.env
        )
        subprocess.run(
            ["git", "-C", str(d), "commit", "-q", "--allow-empty", "-m", "x"],
            check=True,
            env=self.env,
        )
        out = self.run_in(d)
        self.assertNotIn("==> ", out)
        self.assertEqual(Path(json.loads(out)["root"]).resolve(), d.resolve())


if __name__ == "__main__":
    unittest.main()
