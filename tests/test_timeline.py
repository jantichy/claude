"""Metodika času v Claudovi – `skills/timeline.py` a `skills/clauding/clauding.py`.

Každé pravidlo z `clauding/SKILL.md`, *Metodika*, má tady případ, na kterém by se
bez něj spočítalo věrohodné, ale špatné číslo. Testuje se nad podvrženými
transcripty v dočasném adresáři, ne nad skutečnými – ty se mění každou session.
"""

import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

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

    def test_rounding_is_half_up(self):
        """`round()` by z 2,25 udělal 2,2 – člověk čeká 2,3."""
        self.assertEqual(clauding.number(2.25), "2,3")


if __name__ == "__main__":
    unittest.main()
