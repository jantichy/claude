#!/usr/bin/env python3
"""Změří kontext běžící session a řekne, jestli je nad prahem pro `/autopilot`.

Hook `handoff.py` práh hlásí jen při zprávě uživatele, a ta v autonomním běhu
nepřijde – session tak přeleze práh a nikdo to neohlásí. Skill se proto ptá
sám, po každém úkolu, tímhle skriptem. Měření i práh se berou z `handoff.py`,
ať se nerozejdou: jinak by skill a hook hlásily nad touž session různá čísla.

Transcript se hledá podle `CLAUDE_CODE_SESSION_ID`, které Claude Code předává
do prostředí shellu. Výstup je jeden řádek JSON; nejde-li změřit, skript to
řekne s návratovým kódem 1 a skill se nerozjede, místo aby běžel bez meze.

Spouští se: python3 ~/.claude/skills/autopilot/context.py
"""

import importlib.util
import json
import os
import sys
from pathlib import Path

HOOK = Path.home() / ".claude" / "hooks" / "handoff.py"


def load_handoff():
    spec = importlib.util.spec_from_file_location("handoff", HOOK)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def transcript(session):
    found = sorted((Path.home() / ".claude" / "projects").glob(f"*/{session}.jsonl"))
    return found[0] if found else None


def fail(message):
    print(json.dumps({"error": message}, ensure_ascii=False))
    sys.exit(1)


def main():
    session = os.environ.get("CLAUDE_CODE_SESSION_ID")
    if not session:
        fail("V prostředí chybí CLAUDE_CODE_SESSION_ID – neběží to v Claude Code.")
    path = transcript(session)
    if not path:
        fail(f"Transcript session {session} se nenašel pod ~/.claude/projects/.")
    try:
        handoff = load_handoff()
    except OSError:
        fail(f"Nejde načíst {HOOK}, odkud se bere měření i práh.")
    context, calls, compactions = handoff.measure(path)
    threshold = handoff.CONTEXT_RECOMMEND
    print(
        json.dumps(
            {
                "context": context,
                "threshold": threshold,
                "over": context >= threshold,
                "calls": calls,
                "compactions": compactions,
            }
        )
    )


if __name__ == "__main__":
    main()
