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

**Kontext nad otázkou hlídá z transkriptu.** Norma chce nad otázkou textový
blok s titulním řádkem `**[N/celkem] …**` a kontextem. Session ho umí napsat do
bloku thinking místo do odpovědi – uživatel pak místo kontextu vidí jen
jednořádkový souhrn myšlení. Hook proto v transkriptu (`transcript_path`) najde
bloky asistenta od posledního výsledku nástroje nebo zprávy uživatele a zastaví
otázku, mezi nimiž není text s titulním řádkem téhož `N/celkem`. Nečitelný nebo
chybějící transkript otázku propustí.

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
TITLE = re.compile(r"\*\*\[(\d+)/(\d+)\]")


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
        defect = f"`header` je „{header}“, norma chce „Nález N/celkem“ nebo „Položka N/celkem“"
    else:
        n, total = int(m.group(1)), int(m.group(2))
        if 1 <= n <= total:
            return None
        defect = f"`header` „{header}“ má pořadí mimo 1 až {total}"
    return (
        f"{defect}. `celkem` je počet položek, na které se v průchodu ptáš "
        "(~/.claude/skills/findings.md, *Dvě záchytné volby a co znamenají*). "
        "Polož otázku znovu se správným `header` a nad ní titulní řádek **[N/celkem] …**"
    )


def turn_texts(path: str) -> list[str] | None:
    """Texty asistenta od posledního výsledku nástroje nebo zprávy uživatele.

    `None`, když transkript nejde přečíst – pak hook nerozhoduje.
    """
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
    except OSError:
        return None
    texts: list[str] = []
    for line in reversed(lines):
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("type") == "user":
            break
        if row.get("type") != "assistant":
            continue
        content = (row.get("message") or {}).get("content")
        if isinstance(content, list):
            texts += [
                str(c.get("text", ""))
                for c in content
                if isinstance(c, dict) and c.get("type") == "text"
            ]
    return texts


def context_defect(path: str, header: str) -> str | None:
    texts = turn_texts(path)
    if texts is None:
        return None
    wanted = HEADER.match(header.strip()).groups()
    if any(m.groups() == wanted for t in texts for m in TITLE.finditer(t)):
        return None
    return (
        f"nad otázkou chybí v odpovědi text s titulním řádkem **[{wanted[0]}/{wanted[1]}] …** "
        "a kontextem – je-li jen v myšlení, uživatel ho nevidí a dostane jednořádkový "
        "souhrn. Napiš kontext jako text odpovědi a otázku polož znovu"
    )


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
        header = str(q.get("header", ""))
        defect = header_defect(header)
        if not defect and event.get("transcript_path"):
            defect = context_defect(str(event["transcript_path"]), header)
        if defect:
            print(f"findings-guard: {defect}.", file=sys.stderr)
            return BLOCK
    return PASS


if __name__ == "__main__":
    sys.exit(main())
