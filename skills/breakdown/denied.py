#!/usr/bin/env python3
"""Najde v plánu soubory, na které Claude podle `permissions.deny` nesmí sáhnout.

Plán, který založí `credentials.py`, se zasekne až uprostřed implementace, kdy
zápis zablokuje zákaz `Edit(//**/*credentials*)` – a přejmenování se pak musí
propsat do plánu i návrhu. Skript to chytí ještě v plánu.

Čte `permissions.deny` z `~/.claude/settings.json` a z `.claude/settings.json`
a `.claude/settings.local.json` projektu, bere vzory `Read` a `Edit` – vzor
`Write(…)` Claude Code nevyhodnocuje nikdy – a porovná je s cestami souborů
v plánu (text v apostrofech s příponou nebo lomítkem, bez rozsahu řádků
`:12-30`). Vzory čte jako Claude Code: `//` je kořen disku, `~/` domovský
adresář, `/` adresář, ke kterému patří soubor nastavení (u uživatelského
`~/.claude`), holý vzor a `./` adresář projektu; holé jméno a holé
`<adresář>/**` platí v jakékoliv hloubce pod ním, `**` jsou libovolné
adresáře, `*` nepřeskočí `/` a zakázaný adresář zakazuje i všechno pod sebou.

Použití: denied.py PLAN [PROJECT_ROOT]
Výstup: řádek `<cesta>\t<vzor>` za každý zachycený soubor; kód 1, je-li co
hlásit, 0 bez nálezu, 2 při chybném volání.
"""

import json
import os
import re
import sys
from pathlib import Path

TOOLS = ("Read", "Edit")
RULE = re.compile(r"^(%s)\((.+)\)$" % "|".join(TOOLS))
PATH = re.compile(r"`([^`\s]+)`")
LINES = re.compile(r":\d+(?:-\d+)?$")


def glob_regex(pattern):
    """Převede vzor na regulární výraz nad cestou bez počátečního lomítka."""
    out, i = "", 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out, i = out + "(?:.*/)?", i + 3
        elif pattern.startswith("**", i):
            out, i = out + ".*", i + 2
        elif pattern[i] == "*":
            out, i = out + "[^/]*", i + 1
        elif pattern[i] == "?":
            out, i = out + "[^/]", i + 1
        else:
            out, i = out + re.escape(pattern[i]), i + 1
    return re.compile(out + "$")


def anchored(pattern, base, root, home):
    """Vzor jako absolutní cesta bez počátečního lomítka."""
    if pattern.startswith("//"):
        rest, at = pattern[2:], ""
    elif pattern.startswith("~/"):
        rest, at = pattern[2:], str(home)
    elif pattern.startswith("/"):
        rest, at = pattern[1:], str(base)
    elif pattern.startswith("./"):
        rest, at = pattern[2:], str(root)
    else:
        rest, at = pattern, str(root)
        core = rest.rstrip("/").removesuffix("/**")
        if "/" not in core:
            rest = "**/" + rest
    rest = rest.rstrip("/")
    return (at.strip("/") + "/" + rest).lstrip("/")


def deny_rules(root, home):
    rules = []
    for f, base in (
        (home / ".claude" / "settings.json", home / ".claude"),
        (root / ".claude" / "settings.json", root),
        (root / ".claude" / "settings.local.json", root),
    ):
        try:
            deny = json.loads(f.read_text()).get("permissions", {}).get("deny", [])
        except (OSError, ValueError):
            continue
        for r in deny:
            m = RULE.match(r)
            if m:
                rx = glob_regex(anchored(m.group(2), base, root, home))
                rules.append((r, rx))
    return rules


def plan_paths(text):
    """Cesty souborů v plánu: text v apostrofech s příponou nebo lomítkem."""
    seen = []
    for m in PATH.finditer(text):
        p = LINES.sub("", m.group(1).rstrip(".,;")).rstrip(":")
        if ("/" in p or re.search(r"\.[A-Za-z0-9]+$", p)) and p not in seen:
            seen.append(p)
    return seen


def absolute(p, root, home):
    if p.startswith("~/"):
        full = str(home / p[2:])
    elif p.startswith("/"):
        full = p
    else:
        full = str(root / p.removeprefix("./"))
    return os.path.normpath(full).lstrip("/")


def denied(text, root, home):
    rules = deny_rules(root, home)
    hits = []
    for p in plan_paths(text):
        target = absolute(p, root, home)
        # Zakázaný adresář zakazuje i všechno pod sebou.
        parts = target.split("/")
        candidates = ["/".join(parts[: i + 1]) for i in range(len(parts))]
        hit = next((r for r, rx in rules if any(rx.match(c) for c in candidates)), None)
        if hit:
            hits.append((p, hit))
    return hits


def main(argv):
    if len(argv) not in (2, 3):
        print(__doc__.strip().splitlines()[0], file=sys.stderr)
        return 2
    plan = Path(argv[1])
    root = Path(argv[2] if len(argv) == 3 else ".").resolve()
    try:
        text = plan.read_text()
    except OSError as e:
        print(f"plán nejde přečíst: {e}", file=sys.stderr)
        return 2
    hits = denied(text, root, Path.home())
    for p, rule in hits:
        print(f"{p}\t{rule}")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
