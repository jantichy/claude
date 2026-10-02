#!/usr/bin/env python3
"""Ověří workflow, kterým projekt volá sdílené CI (`contract.yml`).

Sdílený workflow uhlídá skoro všechno zevnitř – jen ne to, jestli se vůbec
spustí a s jakým tokenem. To rozhoduje volající soubor v projektu, a kdyby si
každý projekt tyhle kontroly nesl v kopii, rozešly by se jako dřív celé CI.
Projekt proto pouští tenhle skript ze svého testu, lokálně z `~/.claude`,
v CI z klonu připnutého commitu (`CLAUDE_CONFIG`).

Hlídá:

1. volání `contract.yml` – z jiného repozitáře připnuté na 40místný SHA,
   z tohohle lokální cestou,
2. spouštěče `push` a `pull_request` bez zužujícího filtru – osekané `on:`
   vypne CI tiše a soubor dál vypadá platně,
3. job bez `if:` a bez `continue-on-error`,
4. `permissions: contents: read` a žádné právo k zápisu – volaný workflow
   oprávnění dědí, takže tady se rozhoduje o tokenu celého běhu.

Komentářové řádky se ignorují: věta o volání v komentáři nesmí vypadat jako
volání.

Použití: caller.py <workflow.yml>
Návratový kód: 0 v pořádku, 1 nálezy, 2 chyba volání.
"""

import re
import sys
from pathlib import Path

USES = re.compile(
    r"(?m)^\s+uses:\s*(?:\./\.github/workflows/contract\.yml"
    r"|jantichy/claude/\.github/workflows/contract\.yml@[0-9a-f]{40})\s*$"
)
NARROWING = ("branches", "branches-ignore", "paths", "paths-ignore", "tags")


def body(text):
    return (
        "\n".join(r for r in text.splitlines() if not r.lstrip().startswith("#")) + "\n"
    )


def trigger_problems(b):
    on = re.search(r"(?m)^on:\n((?:[ \t]+\S.*\n)+)", b)
    if not on:
        return ["chybí blok `on:` – CI se nespouští"]
    found = [
        f"nespouští se na {t}"
        for t in ("push", "pull_request")
        if not re.search(rf"(?m)^\s+{t}:", on.group(1))
    ]
    found += [
        f"spouštěče jsou zúžené filtrem `{n}:`"
        for n in NARROWING
        if f"{n}:" in on.group(1)
    ]
    return found


def problems(text):
    b = body(text)
    found = []
    if not USES.search(b):
        found.append("nevolá contract.yml – nebo ho volá bez připnutí na 40místný SHA")
    found += trigger_problems(b)
    if re.search(r"(?m)^ {4}if:\s", b):
        found.append("job je podmíněný `if:` – může se tiše přeskočit")
    if "continue-on-error" in b:
        found.append("`continue-on-error` spolkne selhání")
    if not re.search(r"(?m)^permissions:\n\s+contents: read\s*$", b):
        found.append("chybí `permissions: contents: read`")
    if re.search(r"(?m)^\s*[a-z][a-z-]*:[ \t]*(write|write-all)[ \t]*$", b):
        found.append("workflow si nárokuje zápis")
    return found


def main(argv):
    if len(argv) != 2:
        print(__doc__.strip().splitlines()[-3], file=sys.stderr)
        return 2
    path = Path(argv[1])
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"{path}: nelze přečíst – {e}", file=sys.stderr)
        return 2
    found = problems(text)
    for p in found:
        print(f"{path}: {p}")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
