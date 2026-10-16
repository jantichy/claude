#!/usr/bin/env python3
"""PreToolUse hook: zastaví otázku na nález, jejíž `header` nemá tvar z normy.

`skills/findings.md` předepisuje `header` `Nález N/celkem`, u položky, která
nálezem není, `Položka N/celkem`. Test v `tests/test_skills.py` hlídá jen text
skillů, ne to, co session doopravdy vypíše – a session normu umí minout i se
správně napsaným skillem: dá do `header` název tématu a uživatel ztratí přehled,
kolik otázek ho ještě čeká.

**Otázku na položku pozná podle záchytné volby**, ne podle toho, který skill
běží: `Neopravovat` (vada), `Zapsat do backlogu` (nová práce) a `Bezpředmětné`
(nevypořádané téma v `/end`) se v jiné otázce nenabízejí. `Zapsat do todo`
signálem není – nabízí ho i hromadná otázka `/oponent` nad nízkými nálezy,
která jedna položka není. Otázka bez záchytné volby (rozsah běhu, výběr
výstupů, rozpor v `/learn`) se nekontroluje; eviduje to `standards/bypass.md`.

Vrací 2 a důvod na stderr, což je pro PreToolUse zastavení nástroje.
"""

import json
import re
import sys

BLOCK = 2
PASS = 0

TRIGGERS = {"Neopravovat", "Zapsat do backlogu", "Bezpředmětné"}
HEADER = re.compile(r"^(?:Nález|Položka) (\d+)/(\d+)$")
RECOMMENDED = re.compile(r"\s*\(Recommended\)\s*$")


def is_item(question: dict) -> bool:
    labels = {
        RECOMMENDED.sub("", str(o.get("label", ""))).strip()
        for o in question.get("options", [])
        if isinstance(o, dict)
    }
    return bool(labels & TRIGGERS)


def header_defect(header: str) -> str | None:
    m = HEADER.match(header.strip())
    if not m:
        return f"`header` je „{header}“, norma chce „Nález N/celkem“ nebo „Položka N/celkem“"
    n, total = int(m.group(1)), int(m.group(2))
    if not 1 <= n <= total:
        return f"`header` „{header}“ má pořadí mimo 1 až {total}"
    return None


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        return PASS
    if event.get("tool_name") != "AskUserQuestion":
        return PASS
    questions = (event.get("tool_input") or {}).get("questions") or []
    for q in questions:
        if not isinstance(q, dict) or not is_item(q):
            continue
        defect = header_defect(str(q.get("header", "")))
        if defect:
            print(
                f"findings-guard: {defect}. `celkem` je počet položek, na které "
                "se v průchodu ptáš (~/.claude/skills/findings.md, *Dvě záchytné "
                "volby a co znamenají*). Polož otázku znovu se správným `header` "
                "a nad ní titulní řádek **[N/celkem] …**.",
                file=sys.stderr,
            )
            return BLOCK
    return PASS


if __name__ == "__main__":
    sys.exit(main())
