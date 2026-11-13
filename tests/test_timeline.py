"""Metodika času v Claudovi – `skills/timeline.py` a `skills/clauding/clauding.py`.

Každé pravidlo z `clauding/SKILL.md`, *Metodika*, má tady případ, na kterém by se
bez něj spočítalo věrohodné, ale špatné číslo. Testuje se nad podvrženými
transcripty v dočasném adresáři, ne nad skutečnými – ty se mění každou session.
"""

import json
import sys
import tempfile
import unittest
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills"))
sys.path.insert(0, str(ROOT / "skills" / "clauding"))

import clauding  # noqa: E402
import timeline  # noqa: E402

T0 = datetime(2026, 9, 14, 10, 0, tzinfo=timezone.utc)


def stamp(minutes: float) -> str:
    return (T0 + timedelta(minutes=minutes)).isoformat().replace("+00:00", "Z")


def prompt(minutes: float, text: str = "udělej to") -> dict:
    return {"type": "user", "timestamp": stamp(minutes), "message": {"content": text}}


def answer(minutes: float, content=None) -> dict:
    return {
        "type": "assistant",
        "timestamp": stamp(minutes),
        "message": {"content": content or [{"type": "text", "text": "hotovo"}]},
    }


def tool_use(minutes: float, name: str, tool_input: dict) -> dict:
    return answer(
        minutes, [{"type": "tool_use", "id": "t1", "name": name, "input": tool_input}]
    )


def tool_result(minutes: float) -> dict:
    return {
        "type": "user",
        "timestamp": stamp(minutes),
        "message": {"content": [{"type": "tool_result", "tool_use_id": "t1"}]},
    }


def counted_minutes(moments) -> float:
    return sum((b - a).total_seconds() for a, b in timeline.intervals(moments)) / 60


class Timeline(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.projects = Path(self.tmp.name)
        self.original = timeline.PROJECTS
        timeline.PROJECTS = self.projects

    def tearDown(self):
        timeline.PROJECTS = self.original
        self.tmp.cleanup()

    def session(self, project: str, name: str, rows) -> None:
        directory = self.projects / project
        directory.mkdir(exist_ok=True)
        (directory / f"{name}.jsonl").write_text(
            "\n".join(json.dumps(r) for r in rows), encoding="utf-8"
        )

    def stream(self):
        return [at for at, *_ in timeline.session_events()]

    def test_gap_under_limit_counts_and_over_limit_is_pause(self):
        """Mezera do `GAP` se počítá celá, delší vůbec – ne zkrácená na limit."""
        self.session("-a", "s1", [prompt(0), answer(10), prompt(40), answer(45)])
        self.assertEqual(counted_minutes(self.stream()), 15)

    def test_parallel_sessions_are_one_stream(self):
        """Dvě okna střídavě: každé zvlášť má samé pauzy, dohromady je to souvislá práce."""
        self.session("-a", "s1", [prompt(0), prompt(25)])
        self.session("-b", "s2", [prompt(12), prompt(37)])
        self.assertEqual(counted_minutes(self.stream()), 37)

    def test_waiting_for_dialog_answer_is_pause(self):
        """Odpověď v dialogu den poté nesmí přidat den Claudovy práce."""
        self.session(
            "-a",
            "s1",
            [prompt(0), tool_use(5, "AskUserQuestion", {}), tool_result(5 + 24 * 60)],
        )
        self.assertEqual(counted_minutes(self.stream()), 5)

    def test_command_counts_up_to_its_timeout(self):
        """Příkaz čekající hodinu na schválení se započte jen do výše timeoutu."""
        self.session(
            "-a",
            "s1",
            [prompt(0), tool_use(1, "Bash", {"command": "ls"}), tool_result(61)],
        )
        self.assertEqual(counted_minutes(self.stream()), 3)

    def test_explicit_timeout_is_respected(self):
        self.session(
            "-a",
            "s1",
            [
                prompt(0),
                tool_use(1, "Bash", {"command": "make", "timeout": 600_000}),
                tool_result(61),
            ],
        )
        self.assertEqual(counted_minutes(self.stream()), 11)

    def test_background_command_gets_no_credit(self):
        """Příkaz na pozadí vrací hned, takže dlouhá mezera za ním je pauza."""
        self.session(
            "-a",
            "s1",
            [
                prompt(0),
                tool_use(1, "Bash", {"command": "sleep", "run_in_background": True}),
                tool_result(61),
            ],
        )
        self.assertEqual(counted_minutes(self.stream()), 1)

    def test_every_timestamped_record_is_activity(self):
        """Příkaz harnessu mezi prompty je doklad, že se v Claudovi pracovalo."""
        local = {"type": "system", "subtype": "local_command", "timestamp": stamp(15)}
        self.session("-a", "s1", [prompt(0), local, prompt(30)])
        self.assertEqual(counted_minutes(self.stream()), 30)

    def test_subagent_activity_fills_the_gap(self):
        self.session("-a", "s1", [prompt(0), answer(40)])
        sub = self.projects / "-a" / "s1" / "subagents"
        sub.mkdir(parents=True)
        (sub / "agent-x.jsonl").write_text(
            "\n".join(json.dumps(answer(m)) for m in (15, 30)), encoding="utf-8"
        )
        self.assertEqual(counted_minutes(self.stream()), 40)

    def decisions(self):
        return [
            text for _, kind, _, text in timeline.session_events() if kind == "decision"
        ]

    def ask(self, minutes: float, *questions: str) -> dict:
        return tool_use(
            minutes,
            "AskUserQuestion",
            {"questions": [{"question": q} for q in questions]},
        )

    def test_dialog_answer_counts_each_question(self):
        """Jedno volání dialogu nese až čtyři otázky – rozhodnutím je každá zodpovězená."""
        result = tool_result(3)
        result["toolUseResult"] = {"answers": {"Kam?": "sem", "Kdy?": "hned"}}
        self.session("-a", "s1", [prompt(0), self.ask(1, "Kam?", "Kdy?"), result])
        self.assertEqual(self.decisions(), [["Kam?", "Kdy?"]])

    def test_answer_without_result_detail_counts_asked_questions(self):
        self.session("-a", "s1", [prompt(0), self.ask(1, "Kam?"), tool_result(3)])
        self.assertEqual(self.decisions(), [["Kam?"]])

    def kinds(self):
        return [kind for _, kind, _, _ in timeline.session_events()]

    def rejected(self, minutes: float, tool_id: str = "t1") -> dict:
        result = tool_result(minutes)
        result["message"]["content"][0].update(
            tool_use_id=tool_id,
            is_error=True,
            content=timeline.REJECTION + " with this tool use.",
        )
        return result

    def test_closed_dialog_is_rejection_not_decision(self):
        self.session("-a", "s1", [prompt(0), self.ask(1, "Kam?"), self.rejected(3)])
        self.assertEqual(self.decisions(), [])
        self.assertEqual(self.kinds().count("rejection"), 1)

    def test_parallel_calls_are_one_rejection(self):
        """Zamítnuté volání odmítne i souběžná volání téže zprávy – rozhodl uživatel jednou."""
        calls = answer(
            1,
            [
                {"type": "tool_use", "id": "t1", "name": "Bash", "input": {}},
                {"type": "tool_use", "id": "t2", "name": "Bash", "input": {}},
            ],
        )
        calls["message"]["id"] = "m1"
        self.session(
            "-a",
            "s1",
            [prompt(0), calls, self.rejected(2, "t1"), self.rejected(2, "t2")],
        )
        self.assertEqual(self.kinds().count("rejection"), 1)

    def test_escape_is_interrupt_not_prompt(self):
        """Esc zapíše harness jako zprávu od uživatele – prompt to není."""
        rows = [
            prompt(0),
            prompt(1, timeline.INTERRUPT),
            prompt(2, "[Request interrupted by user for tool use]"),
        ]
        self.session("-a", "s1", rows)
        self.assertEqual(self.kinds(), ["prompt", "interrupt", "claude"])

    def test_agreement_counts_in_main_session_only(self):
        """Subagent přitakává Claudovi, ne uživateli."""
        said = [{"type": "text", "text": "Máš pravdu, a máš pravdu i tady."}]
        self.session("-a", "s1", [prompt(0), answer(1, said)])
        sub = self.projects / "-a" / "s1" / "subagents"
        sub.mkdir(parents=True)
        (sub / "agent-x.jsonl").write_text(
            json.dumps(answer(2, said)), encoding="utf-8"
        )
        data = [d for _, kind, _, d in timeline.session_events() if kind == "claude"]
        self.assertEqual(sorted(data, key=str), [2, None])

    def test_subagent_dialog_is_no_decision(self):
        """Subagent se uživatele zeptat nemůže – jeho záznam rozhodnutí není."""
        asked = self.ask(1, "Kam?")
        asked["isSidechain"] = True
        self.session("-a", "s1", [prompt(0), asked, tool_result(3)])
        self.assertEqual(self.decisions(), [])

    def skills(self):
        return [d for _, kind, _, d in timeline.session_events() if kind == "skill"]

    def test_nested_skill_is_told_from_skill_on_request(self):
        """`/merge` pouští `/end` – i ten se počítá, ale jako vnořený, ne na pokyn slovy."""
        rows = [
            prompt(0, "přimerguj to"),
            tool_use(1, "Skill", {"skill": "merge"}),
            tool_use(2, "Skill", {"skill": "end"}),
        ]
        self.session("-a", "s1", rows)
        self.assertEqual(self.skills(), [[("merge", "asked")], [("end", "nested")]])

    def test_typed_skill_called_again_is_one_run(self):
        """Ručně zadaný skill spustil harness – jeho druhé volání Claudem nové spuštění není."""
        typed = (
            "<command-message>end</command-message> <command-name>/end</command-name>"
        )
        rows = [
            prompt(0, typed),
            tool_use(1, "Skill", {"skill": "end"}),
            tool_use(2, "Skill", {"skill": "next"}),
            prompt(3, "a teď review"),
            tool_use(4, "Skill", {"skill": "review"}),
        ]
        self.session("-a", "s1", rows)
        self.assertEqual(self.skills(), [[("next", "nested")], [("review", "asked")]])

    def test_skill_in_subagent_is_nested(self):
        sub = self.projects / "-a" / "s1" / "subagents"
        sub.mkdir(parents=True)
        rows = [prompt(0), tool_use(1, "Skill", {"skill": "oponent"})]
        (sub / "agent-x.jsonl").write_text(
            "\n".join(json.dumps(r) for r in rows), encoding="utf-8"
        )
        self.assertEqual(self.skills(), [[("oponent", "nested")]])

    def test_prefix_limits_projects(self):
        """`recover` počítá jen projekty klienta – cizí session do proudu nesmí."""
        self.session("-Users-x-Dev-client", "s1", [prompt(0), prompt(10)])
        self.session("-Users-x-Dev-other", "s2", [prompt(5)])
        events = list(timeline.session_events([Path("/Users/x/Dev/client")]))
        self.assertEqual(
            {source for _, _, source, _ in events}, {"-Users-x-Dev-client"}
        )


class Clauding(unittest.TestCase):
    def test_commit_far_from_claude_is_dropped(self):
        """Ruční práce v repozitáři mimo Clauda čas v Claudovi není."""
        claude = [T0, T0 + timedelta(minutes=10)]
        near = T0 + timedelta(minutes=25)
        far = T0 + timedelta(hours=5)
        self.assertEqual(clauding.near([near, far], claude), [near])

    def test_harness_command_is_not_missing_data(self):
        for text in ("/resume", "/skills", "exit"):
            self.assertTrue(clauding.is_command(text), text)
        self.assertFalse(clauding.is_command("oprav ten test"))

    def test_day_is_split_at_prague_midnight(self):
        start = datetime(2026, 9, 14, 21, 30, tzinfo=timezone.utc)  # 23:30 v Praze
        days = clauding.per_day([[start, start + timedelta(hours=1)]])
        self.assertEqual(sorted(v / 60 for v in days.values()), [30, 30])

    def data(self):
        full, guessed = date(2026, 9, 14), date(2026, 9, 15)
        return (
            SimpleNamespace(
                hours={full: 2.0, guessed: 5.0},
                guessed={guessed},
                counts={full: Counter(decision=6), guessed: Counter(decision=1)},
            ),
            full,
            guessed,
        )

    def test_counts_on_estimated_day_are_lower_bound(self):
        """Za odhadnutý den chybí záznamy – počet je dolní mez a do poměru nejde."""
        data, full, guessed = self.data()
        kinds = ("decision",)
        self.assertEqual(clauding.lower_bound([full, guessed], data, kinds), "≥7")
        self.assertEqual(clauding.per_hour([full, guessed], data, kinds), "3,0")
        self.assertEqual(clauding.lower_bound([guessed], data, kinds), "–")
        self.assertEqual(clauding.per_hour([guessed], data, kinds), "–")

    def test_pasted_text_is_not_typed(self):
        self.assertEqual(
            clauding.typed("oprav [Pasted text #1 +20 lines] [Image #2]"), 5
        )

    def test_bedtime_needs_sleep_after_it(self):
        """Prompt v pět ráno, po kterém se pracuje dál, je začátek dne, ne konec noci."""
        night = datetime(2026, 9, 15, 2, 30, tzinfo=clauding.ZONE)
        morning = datetime(2026, 9, 16, 5, 0, tzinfo=clauding.ZONE)
        prompts = [(night, ""), (morning, ""), (morning + timedelta(minutes=10), "")]
        self.assertEqual(clauding.bedtimes(prompts), [night])

    def test_weekday_total_averages_days_not_rows(self):
        """Dva pondělky a jedno úterý: průměr sedmi řádků by dal jiné číslo než průměr dnů."""
        days = [date(2026, 9, 14), date(2026, 9, 15), date(2026, 9, 21)]
        hours = {days[0]: 2.0, days[1]: 8.0, days[2]: 2.0}
        self.assertEqual(clauding.weekdays(days, hours)[-1], "| **Celkem** | 4,0 | |")

    def test_histogram_total_counts_days(self):
        days = [date(2026, 9, 14), date(2026, 9, 15)]
        rows = clauding.histogram(days, {days[0]: 3.0})
        self.assertEqual(rows[-1], "| **Celkem** | 2 | |")

    def test_shared_sentences_have_no_table_marks(self):
        """Věty ke sdílení čte člověk bez legendy – značky se mění na slova."""
        self.assertEqual(clauding.worded("≥7"), "7+")
        self.assertEqual(clauding.worded("~3,0"), "zhruba 3,0")

    def test_czech_plural(self):
        forms = ("den", "dny", "dní")
        self.assertEqual(
            [clauding.plural(n, *forms) for n in (1, 2, 4, 5, 0)],
            ["den", "dny", "dny", "dní", "dní"],
        )

    def test_renamed_skill_counts_under_today_name(self):
        """Přejmenovaný skill je tentýž; sloučený nebo zrušený zůstává pod svým jménem."""
        skills = ({"end", "next"}, {"cleanup": "end"}, {"break"})
        self.assertEqual(clauding.skill_name("cleanup", skills), "end")
        self.assertEqual(clauding.skill_name("break", skills), "break")
        self.assertIsNone(clauding.skill_name("clear", skills))
        self.assertIsNone(clauding.skill_name("superpowers:brainstorming", skills))

    def test_skill_table_is_sorted_and_marks_lower_bound(self):
        """Zadané příkazem jsou z `history.jsonl` úplné, spuštěné Claudem za odhadnutý den ne."""
        full, guessed = date(2026, 9, 14), date(2026, 9, 15)
        data = SimpleNamespace(
            guessed={guessed},
            skills={
                full: Counter({("next", "typed"): 1, ("end", "typed"): 2}),
                guessed: Counter({("end", "nested"): 1}),
            },
        )
        original = clauding.own_skills
        clauding.own_skills = lambda: ({"end", "next"}, {}, set())
        try:
            rows = clauding.skill_table([full, guessed], data)
        finally:
            clauding.own_skills = original
        self.assertEqual(rows[2], "| /end | ≥3 | 2 | 0 | ≥1 |")
        self.assertEqual(rows[3], "| /next | 1 | 1 | 0 | 0 |")
        self.assertEqual(rows[-1], "| **Celkem** | ≥4 | 3 | 0 | ≥1 |")

    def test_project_is_first_folder_under_root(self):
        """Worktrees i podprojekty jednoho klienta jsou jeden projekt."""
        home = Path.home()
        original = clauding.folders
        clauding.folders = lambda: {"gtm": home / "Projects" / "Gtm"}
        try:
            cases = {
                home / "Projects" / "Eventoid" / "billing": "Projects/Eventoid",
                home / "Clients" / "Acme" / "web" / "src": "Clients/Acme",
                home / ".claude" / "skills": ".claude",
                home / "Dev" / "gtm" / "main": "Projects/Gtm",
                home / "Dev" / "jinak": "Dev/jinak",
            }
            for path, project in cases.items():
                self.assertEqual(clauding.project_of(path), project, path)
        finally:
            clauding.folders = original

    def test_scratchpad_session_belongs_to_its_parent(self):
        """Běh `claude -p` ve scratchpadu je práce na projektu, který ho pustil."""
        names = {"-Users-x--claude": str(Path.home() / ".claude")}
        uid = "03cd7123-e74c-42a3-8f9b-d1a8b88d9730"
        for path in (
            f"/private/tmp/claude-501/-Users-x--claude/{uid}/scratchpad/run",
            f"-private-tmp-claude-501--Users-x--claude-{uid}-scratchpad-run",
        ):
            self.assertEqual(clauding.project_of(path, names), ".claude")

    def projects_data(self):
        day = date(2026, 9, 14)
        at = datetime(2026, 9, 14, 10, 0, tzinfo=clauding.ZONE)

        def span(a, b):
            return [at + timedelta(hours=a), at + timedelta(hours=b)]

        return day, SimpleNamespace(
            guessed=set(),
            hours={day: 3.0},
            measured=[span(0, 3)],
            projects={
                "a": ({day: 2.0}, [span(0, 2)]),
                "b": ({day: 2.0}, [span(1, 3)]),
                "c": ({day: 0.5}, [span(1.5, 2)]),
            },
        )

    def test_parallel_projects_overlap(self):
        """Dva projekty souběžně hodinu, chvíli tři naráz."""
        day, data = self.projects_data()
        shared, peak, _ = clauding.overlap([day], data)
        self.assertEqual((shared, peak), (1.0, 3))

    def test_project_sum_exceeds_time_in_claude(self):
        """Souběžný čas se počítá každému projektu – součet je větší než celek."""
        day, data = self.projects_data()
        rows = clauding.project_table([day], data)
        self.assertEqual(rows[2], "| a | 2,0 | 1 | 67 % |")
        self.assertEqual(rows[-2], "| **Součet projektů** | 4,5 | | 150 % |")
        self.assertEqual(rows[-1], "| **Čas v Claude Code** | 3,0 | | 100 % |")

    def test_rounding_is_half_up(self):
        """`round()` by z 2,25 udělal 2,2 – člověk čeká 2,3."""
        self.assertEqual(clauding.number(2.25), "2,3")


if __name__ == "__main__":
    unittest.main()
