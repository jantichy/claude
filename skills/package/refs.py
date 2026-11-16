#!/usr/bin/env python3
"""Mapa odkazů pro `/package`: co zadané soubory potřebují a co v hotovém balíčku vede ven.

Grep z hlavy minul odkaz schovaný za jiným vzorem a zbytek po úpravě nenašel vůbec,
proto se odkazy hledají tímhle skriptem a ne ručně. Skript nic nemění, jen vypisuje.

Použití:

    refs.py scan SOUBOR…   odchozí odkazy zadaných souborů (adresář = všechny textové soubory v něm)
    refs.py check ADRESÁŘ [--term SLOVO…]   co v hotovém balíčku vede ven nebo je osobní

Výstup je JSON na stdout. `scan` vrací `refs`: u každého odkazu soubor, řádek, cíl,
druh (`path` – absolutní cesta, `relative` – cesta vůči souboru, `skill` – zmínka
o vlastním skillu, `agent` – zmínka o vlastním typu agenta) a jestli cíl existuje.
`check` vrací `findings` stejného tvaru s druhy `absolute` (absolutní cesta),
`unresolved` (relativní odkaz bez cíle v balíčku), `skill` (zmínka o skillu, který
v balíčku není), `agent`, `term` (výskyt zadaného slova) a `reserved` (soubor se
jménem vyhrazeným jiným nástrojem). Kód 1 znamená, že `check` něco našel.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

HOME = Path.home()
CLAUDE = HOME / ".claude"
TEXT_SUFFIXES = {".md", ".py", ".sh", ".json", ".txt", ".yaml", ".yml", ".toml"}
# Jména, která čtou jiné AI nástroje jako svoje instrukce; na souborovém systému bez
# rozlišení velikosti písmen je najdou i v malých písmenech.
RESERVED = {
    "agents.md",
    "gemini.md",
    "copilot-instructions.md",
    ".cursorrules",
    ".windsurfrules",
}

# Obecná místa Claude Code, která smí jmenovat INSTALL.md: nejsou autorova, platí
# u každého příjemce. Jinde v balíčku se hlásí i ona – cesta se volí až při instalaci.
GENERIC = re.compile(
    r"(?:~|\$HOME|%USERPROFILE%)[/\\]\.claude(?:[/\\](?:skills|agents|CLAUDE\.md))?[/\\]?"
)


def generic_location(target):
    return GENERIC.fullmatch(target) is not None


ABSOLUTE = re.compile(
    r"(?:~|\$HOME|%USERPROFILE%|/Users/[^/\s`]+|/home/[^/\s`]+|[A-Za-z]:\\Users\\[^\\\s`]+)"
    r"[/\\][^\s`'\"<>)\]|,;*]*"
)
MD_LINK = re.compile(r"\]\(([^)\s#]+)(?:#[^)]*)?\)")
TICKED_FILE = re.compile(r"`([\w./-]+\.(?:md|py|sh|json|txt|ya?ml|toml))`")
SKILL = re.compile(r"(?<![\w/.~-])/([a-z][a-z0-9-]+)\b")
TICKED = re.compile(r"`([a-z][a-z0-9-]+)`")


def text_files(paths):
    for p in paths:
        p = Path(p).expanduser()
        if p.is_dir():
            for f in sorted(p.rglob("*")):
                if (
                    f.is_file()
                    and f.suffix in TEXT_SUFFIXES
                    and "__pycache__" not in f.parts
                ):
                    yield f
        elif p.is_file():
            yield p


def lines(f):
    try:
        return f.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return []


def own_skills():
    root = CLAUDE / "skills"
    return (
        {d.name for d in root.iterdir() if (d / "SKILL.md").is_file()}
        if root.is_dir()
        else set()
    )


def own_agents():
    root = CLAUDE / "agents"
    return {f.stem for f in root.glob("*.md")} if root.is_dir() else set()


def expand(target):
    t = target.rstrip(".:")
    for prefix in ("~", "$HOME", "%USERPROFILE%"):
        if t.startswith(prefix):
            return HOME / t[len(prefix) :].lstrip("/\\")
    return Path(t)


def relative_targets(line):
    for m in MD_LINK.finditer(line):
        if not re.match(r"[a-z]+:", m.group(1)):
            yield m.group(1)
    for m in TICKED_FILE.finditer(line):
        if not m.group(1).startswith(("~", "/")):
            yield m.group(1)


def resolve_relative(target, base, root):
    for d in (base, root):
        candidate = (d / target).resolve()
        if candidate.exists():
            return candidate
    return None


def scan(paths):
    skills, agents = own_skills(), own_agents()
    refs = []
    for f in text_files(paths):
        for n, line in enumerate(lines(f), 1):
            here = {"file": str(f), "line": n}
            for m in ABSOLUTE.finditer(line):
                target = m.group(0).rstrip(".:")
                refs.append(
                    {
                        **here,
                        "target": target,
                        "kind": "path",
                        "exists": expand(target).exists(),
                    }
                )
            for target in relative_targets(line):
                hit = resolve_relative(target, f.parent, CLAUDE)
                refs.append(
                    {
                        **here,
                        "target": target,
                        "kind": "relative",
                        "exists": hit is not None,
                        "resolved": str(hit) if hit else None,
                    }
                )
            for m in SKILL.finditer(line):
                if m.group(1) in skills:
                    refs.append(
                        {**here, "target": m.group(1), "kind": "skill", "exists": True}
                    )
            for m in TICKED.finditer(line):
                if m.group(1) in agents:
                    refs.append(
                        {**here, "target": m.group(1), "kind": "agent", "exists": True}
                    )
    return refs


def check_line(line, f, root, names, terms):
    """Co na jednom řádku balíčku vede ven nebo je osobní."""
    skills, agents = names
    for m in ABSOLUTE.finditer(line):
        if not (f.name == "INSTALL.md" and generic_location(m.group(0))):
            yield "absolute", m.group(0)
    for target in relative_targets(line):
        hit = resolve_relative(target, f.parent, root)
        if hit is None or root not in hit.parents:
            yield "unresolved", target
    yield from (
        ("skill", m.group(1)) for m in SKILL.finditer(line) if m.group(1) in skills
    )
    yield from (
        ("agent", m.group(1)) for m in TICKED.finditer(line) if m.group(1) in agents
    )
    for term in terms:
        # Kmen se hledá jen na začátku slova: „Rohl“ má najít „Rohlík“, ne „prohlašuje“.
        if re.search(r"(?<!\w)" + re.escape(term), line, re.IGNORECASE):
            yield "term", term


def check(root, terms):
    root = Path(root).expanduser().resolve()
    packaged = {p.parent.name for p in root.rglob("SKILL.md")}
    names = (own_skills() - packaged, own_agents())
    findings = [
        {
            "file": str(f.relative_to(root)),
            "line": 0,
            "target": f.name,
            "kind": "reserved",
        }
        for f in root.rglob("*")
        if f.is_file() and f.name.lower() in RESERVED
    ]
    for f in text_files([root]):
        rel = str(f.relative_to(root))
        for n, line in enumerate(lines(f), 1):
            for kind, target in check_line(line, f, root, names, terms):
                findings.append(
                    {"file": rel, "line": n, "target": target, "kind": kind}
                )
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("scan")
    s.add_argument("paths", nargs="+")
    c = sub.add_parser("check")
    c.add_argument("root")
    c.add_argument("--term", action="append", default=[])
    args = parser.parse_args()
    if args.command == "scan":
        json.dump({"refs": scan(args.paths)}, sys.stdout, ensure_ascii=False, indent=1)
        return 0
    if not os.path.isdir(os.path.expanduser(args.root)):
        print(f"Adresář {args.root} neexistuje.", file=sys.stderr)
        return 2
    findings = check(args.root, args.term)
    json.dump({"findings": findings}, sys.stdout, ensure_ascii=False, indent=1)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
