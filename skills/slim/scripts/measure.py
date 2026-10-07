#!/usr/bin/env python3
"""Změří, co se v projektu načítá do každé session, a kde v tom leží místo.

Čtyři režimy:

- `tree [adresář]` – strom načítání: uživatelský `CLAUDE.md`, projektové
  `CLAUDE.md` z adresáře a všech nad ním a rekurzivně jejich `@` importy.
  U každého souboru znaky, hloubku a to, kdo ho importuje; součet proti limitu.
  Nakonec druhá řada: popisy vlastních skillů, které jdou do kontextu taky.
- `sections <soubor>` – rozpad souboru po nadpisech `##` a `###` se znaky
  a počtem značek dokladů (data, „Doloženo“, „Proč:“, „Zrádné“).
- `history <soubor>` – velikost souboru v gitu po dnech, ať je vidět, jak rychle roste.
- `refs [soubor ...]` – graf načítání odkazem: které soubory se nenačítají
  importem, ale pokynem „načti si `cesta`“, a kdo ten pokyn dává. Počet
  načítajících je vodítko, jak často se soubor čte; dvojice načítající → cíl
  jsou hrany rodič → podmíněné dítě, nad kterými se hledají duplicity.

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
LOAD = re.compile(r"[Nn]a(?:čti|čte|čítá|čtou)\b[^\n]{0,240}?")
MD_PATH = re.compile(r"`(~/[^`\s]+\.md)`")
CORPUS = (".claude", "Dev/context")
SKIP = ("/projects/", "/plugins/", "/node_modules/", "/archive/", "superpowers/")
# Záznamy o práci pokyn k načtení jen citují, nedávají ho.
RECORDS = ("decisions.md", "done.md", "todo.md", "backlog.md")
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
        queue.extend(
            (depth + 1, child, short(path))
            for child in imports(read(path), path.parent)
        )
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
    print(
        f"\ncelkem {total} znaků v {len(rows)} souborech · limit {args.limit} · {state}"
    )
    count, chars = skill_descriptions()
    print(
        f"druhá řada: popisy {count} vlastních skillů {chars} znaků "
        "(pluginy, MCP a systémový prompt ukáže /context)"
    )
    return 1 if total > args.limit else 0


def headings(text: str) -> list:
    """Nadpisy `##` a `###` mimo bloky kódu – nadpis v šabloně není sekce."""
    fences = [m.span() for m in FENCE.finditer(text)]
    return [
        m
        for m in HEADING.finditer(text)
        if not any(a <= m.start() < b for a, b in fences)
    ]


def loads(text: str) -> list:
    """Cesty, které text výslovně velí načíst („načti si `~/x.md`“)."""
    found = []
    for line in text.splitlines():
        for match in LOAD.finditer(line):
            tail = line[match.start() : match.start() + 260]
            found += MD_PATH.findall(tail)
    return sorted(set(found))


def corpus() -> list:
    home = Path.home()
    files = []
    for base in CORPUS:
        files += [
            p
            for p in (home / base).rglob("*.md")
            if not any(s in str(p) for s in SKIP) and p.name not in RECORDS
        ]
    return files


def cmd_refs(args) -> int:
    graph = {}
    for path in corpus():
        for target in loads(read(path)):
            graph.setdefault(target, set()).add(short(path))
    wanted = [short(Path(f).expanduser().resolve()) for f in args.files]
    print(f"{'znaků':>7} {'načítá':>6}  soubor  ← kdo velí načíst")
    for target in sorted(graph, key=lambda t: -len(graph[t])):
        if wanted and target not in wanted:
            continue
        path = Path(target).expanduser()
        size = len(read(path)) if path.is_file() else 0
        who = ", ".join(sorted(graph[target]))
        print(f"{size:>7} {len(graph[target]):>6}  {target}  ← {who}")
    return 0


def cmd_sections(args) -> int:
    text = read(Path(args.file))
    marks = headings(text)
    starts = [0] + [m.start() for m in marks]
    names = ["(úvod)"] + [f"{m.group(1)} {m.group(2)}" for m in marks]
    print(f"celkem {len(text)} znaků")
    print(f"{'znaků':>7} {'data':>5} {'dolož':>5} {'proč':>5} {'zrád':>5}  sekce")
    for i, name in enumerate(names):
        end = starts[i + 1] if i + 1 < len(starts) else len(text)
        body = text[starts[i] : end]
        counts = [len(p.findall(body)) for p in MARKERS.values()]
        print(f"{len(body):>7} " + " ".join(f"{c:>5}" for c in counts) + f"  {name}")
    return 0


def cmd_history(args) -> int:
    path = Path(args.file).resolve()
    git = ["git", "-C", str(path.parent)]
    log = subprocess.run(
        git + ["log", "--format=%h %ad", "--date=short", "--", path.name],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split("\n")
    days = {}
    for line in filter(None, log):
        commit, day = line.split()
        days.setdefault(day, commit)
    for day, commit in sorted(days.items())[-args.days :]:
        show = subprocess.run(
            git + ["show", f"{commit}:./{path.name}"], capture_output=True, text=True
        )
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
    refs = sub.add_parser("refs")
    refs.add_argument("files", nargs="*")
    args = parser.parse_args()
    return {
        "tree": cmd_tree,
        "sections": cmd_sections,
        "history": cmd_history,
        "refs": cmd_refs,
    }[args.mode](args)


if __name__ == "__main__":
    sys.exit(main())
