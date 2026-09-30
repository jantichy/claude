#!/usr/bin/env python3
"""Změří, co se v projektu načítá do každé session, a kde v tom leží místo.

Tři režimy:

- `tree [adresář]` – strom načítání: uživatelský `CLAUDE.md`, projektové
  `CLAUDE.md` z adresáře a všech nad ním a rekurzivně jejich `@` importy.
  U každého souboru znaky, hloubku a to, kdo ho importuje; součet proti limitu.
  Nakonec druhá řada: popisy vlastních skillů, které jdou do kontextu taky.
- `sections <soubor>` – rozpad souboru po nadpisech `##` a `###` se znaky
  a počtem značek dokladů (data, „Doloženo“, „Proč:“, „Zrádné“).
- `history <soubor>` – velikost souboru v gitu po dnech, ať je vidět, jak rychle roste.

Počítají se **znaky, ne bajty** – limit Claude Code je ve znacích a u češtiny
dělá rozdíl kolem deseti procent. Import uvnitř bloku kódu nebo v apostrofech
se nepočítá, protože ho Claude Code nevyhodnotí.
"""

import argparse
import re
import subprocess
import sys
from collections import deque
from pathlib import Path

LIMIT = 150_000
MAX_DEPTH = 5
PROJECT_FILES = ("CLAUDE.md", ".claude/CLAUDE.md", "CLAUDE.local.md")
FENCE = re.compile(r"^(```|~~~).*?^\1[^\n]*$", re.S | re.M)
CODE_SPAN = re.compile(r"(`+)(?:(?!\1).)+?\1", re.S)
IMPORT = re.compile(r"(?<![\w`@])@([^\s`)\]>\"']+)")
HEADING = re.compile(r"^(#{2,3}) (.+)$", re.M)
MARKERS = {
    "datum": re.compile(r"\b\d{1,2}\. ?\d{1,2}\. ?20\d\d\b"),
    "doloženo": re.compile(r"Doložen[oa]"),
    "proč": re.compile(r"\*\*Proč\b"),
    "zrádné": re.compile(r"Zrádn[éý]"),
}


def short(path: Path) -> str:
    return str(path).replace(str(Path.home()), "~", 1)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def imports(text: str, base: Path) -> list:
    """Cesty `@` importů, které Claude Code opravdu načte – mimo kód a existující."""
    text = CODE_SPAN.sub("", FENCE.sub("", text))
    found = []
    for raw in IMPORT.findall(text):
        target = Path(raw.rstrip(".,;:")).expanduser()
        if not target.is_absolute():
            target = base / target
        if target.is_file():
            found.append(target.resolve())
    return found


def roots(start: Path) -> list:
    """Soubory, které Claude Code načte sám: uživatelský a projektové CLAUDE.md."""
    result = [Path.home() / ".claude" / "CLAUDE.md"]
    for directory in [start, *start.parents]:
        result += [directory / name for name in PROJECT_FILES]
    return [p.resolve() for p in result if p.is_file()]


def walk(start: Path) -> list:
    """(hloubka, soubor, kdo ho importuje) pro celý strom, bez opakování.

    Prochází se do šířky, takže soubor importovaný přímo i oklikou dostane
    kratší z obou hloubek – ta rozhoduje, jak daleko od paušálu je.
    """
    seen, rows = set(), []
    queue = deque((0, path, "start") for path in roots(start))
    while queue:
        depth, path, parent = queue.popleft()
        if path in seen or depth > MAX_DEPTH:
            continue
        seen.add(path)
        rows.append((depth, path, parent))
        queue.extend((depth + 1, child, short(path)) for child in imports(read(path), path.parent))
    return rows


def skill_descriptions() -> tuple:
    """Počet vlastních skillů a součet znaků jejich `description`."""
    total, count = 0, 0
    for skill in (Path.home() / ".claude" / "skills").glob("*/SKILL.md"):
        match = re.search(r"^description: (.+)$", read(skill), re.M)
        if match:
            total, count = total + len(match.group(1)), count + 1
    return count, total


def cmd_tree(args) -> int:
    rows = walk(Path(args.path).resolve())
    total = 0
    print(f"{'hloubka':>7} {'znaků':>8} {'součet':>8}  soubor  ← importuje")
    for depth, path, parent in rows:
        size = len(read(path))
        total += size
        print(f"{depth:>7} {size:>8} {total:>8}  {short(path)}  ← {parent}")
    state = "NAD LIMITEM" if total > args.limit else "pod limitem"
    print(f"\ncelkem {total} znaků v {len(rows)} souborech · limit {args.limit} · {state}")
    count, chars = skill_descriptions()
    print(f"druhá řada: popisy {count} vlastních skillů {chars} znaků "
          "(pluginy, MCP a systémový prompt ukáže /context)")
    return 1 if total > args.limit else 0


def cmd_sections(args) -> int:
    text = read(Path(args.file))
    marks = list(HEADING.finditer(text))
    starts = [0] + [m.start() for m in marks]
    names = ["(úvod)"] + [f"{m.group(1)} {m.group(2)}" for m in marks]
    print(f"celkem {len(text)} znaků")
    print(f"{'znaků':>7} {'data':>5} {'dolož':>5} {'proč':>5} {'zrád':>5}  sekce")
    for i, name in enumerate(names):
        end = starts[i + 1] if i + 1 < len(starts) else len(text)
        body = text[starts[i]:end]
        counts = [len(p.findall(body)) for p in MARKERS.values()]
        print(f"{len(body):>7} " + " ".join(f"{c:>5}" for c in counts) + f"  {name}")
    return 0


def cmd_history(args) -> int:
    path = Path(args.file).resolve()
    git = ["git", "-C", str(path.parent)]
    log = subprocess.run(git + ["log", "--format=%h %ad", "--date=short", "--", path.name],
                         capture_output=True, text=True, check=True).stdout.split("\n")
    days = {}
    for line in filter(None, log):
        commit, day = line.split()
        days.setdefault(day, commit)
    for day, commit in sorted(days.items())[-args.days:]:
        show = subprocess.run(git + ["show", f"{commit}:./{path.name}"],
                              capture_output=True, text=True)
        print(f"{day} {commit} {len(show.stdout):>8}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="mode", required=True)
    tree = sub.add_parser("tree")
    tree.add_argument("path", nargs="?", default=".")
    tree.add_argument("--limit", type=int, default=LIMIT)
    sections = sub.add_parser("sections")
    sections.add_argument("file")
    history = sub.add_parser("history")
    history.add_argument("file")
    history.add_argument("--days", type=int, default=30)
    args = parser.parse_args()
    return {"tree": cmd_tree, "sections": cmd_sections, "history": cmd_history}[args.mode](args)


if __name__ == "__main__":
    sys.exit(main())
