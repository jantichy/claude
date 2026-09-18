#!/usr/bin/env python3
"""Ověří, že odkazy v zadaných Markdownech vedou někam.

Hledá dvě vady, které jinak musí najít čtenář bez kontextu ve /cleanup –
a které jsou přitom mechanické, takže na ně podle ~/.claude/RULES.md,
*Model a effort podle úkolu*, pravidla nula nemá chodit model:

1. relativní odkaz na soubor, který neexistuje,
2. kotva (#fragment), ke které v cílovém souboru není nadpis.

Vyloučeno je schválně:

- **bloky kódu** – jak při hledání odkazů, tak při sbírání nadpisů. Ukázky
  nesou zástupné symboly (`<name>`) a šablony výstupu začínají řádkem
  `## Něco`, který nadpis dokumentu není. Falešný poplach je ta horší
  polovina selhání: kontrolu, která křičí na správný text, si člověk vypne.
- **absolutní cesty a `~/`** – míří mimo repozitář, takže jejich platnost
  nezávisí na tomhle projektu a v cizím prostředí by hlásily nesmysly.
- **http, https, mailto** – ověřit je znamená jít na síť, což je jiná
  úloha s jinou cenou a jinými režimy selhání.

Použití: links.py <soubor.md> [...]
Návratový kód: 0 čisto, 1 nálezy, 2 chyba volání.
"""

import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote

LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
FENCE = re.compile(r"^\s*(```|~~~)")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*$")
EXTERNAL = ("http://", "https://", "mailto:", "tel:", "ftp://", "//")


def outside_fences(text):
    """Vrátí [(číslo řádku, text)] pro řádky mimo ohraničené bloky kódu."""
    rows, fence = [], None
    for number, line in enumerate(text.splitlines(), 1):
        mark = FENCE.match(line)
        if fence is None and mark:
            fence = mark.group(1)
        elif fence is not None and mark and mark.group(1) == fence:
            fence = None
        elif fence is None:
            rows.append((number, line))
    return rows


def slug(text):
    """Slug nadpisu podle GitHubu: bez značek, malými, mezery na pomlčky."""
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[*_~]", "", text).strip().lower()
    kept = [c for c in text if c.isalnum() or c in " -_" or unicodedata.combining(c)]
    return "".join(kept).replace(" ", "-")


def anchors(path):
    """Množina slugů nadpisů souboru; prázdná, nejde-li přečíst."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return set()
    found = set()
    for _, line in outside_fences(text):
        match = HEADING.match(line)
        if match:
            found.add(slug(match.group(2)))
    return found


def split_target(raw):
    """Rozdělí cíl odkazu na cestu a kotvu, bez titulku v uvozovkách."""
    target = raw.strip()
    if " " in target and target[-1] in "\"'":
        target = target[: target.index(" ")].strip()
    target = target.strip("<>")
    path, _, anchor = target.partition("#")
    return path, unquote(anchor)


def skip(path, anchor):
    """Cíle, které se schválně neověřují – viz docstring modulu."""
    if not path and not anchor:
        return True
    return path.startswith(EXTERNAL) or path.startswith(("/", "~"))


def check_link(source, number, raw, cache):
    """Vrátí text nálezu, nebo None, je-li odkaz v pořádku."""
    path, anchor = split_target(raw)
    if skip(path, anchor):
        return None
    target = (source.parent / path).resolve() if path else source
    if not target.exists():
        return f"{source}:{number}: {raw.strip()} – soubor neexistuje"
    if not anchor or target.is_dir() or target.suffix.lower() != ".md":
        return None
    if target not in cache:
        cache[target] = anchors(target)
    if slug(anchor) not in cache[target]:
        return f"{source}:{number}: {raw.strip()} – v cíli není nadpis „{anchor}“"
    return None


def check(paths):
    """Projde soubory a vrátí seznam nálezů."""
    findings, cache = [], {}
    for name in paths:
        source = Path(name)
        try:
            text = source.read_text(encoding="utf-8")
        except OSError as error:
            findings.append(f"{source}: nelze přečíst – {error}")
            continue
        for number, line in outside_fences(text):
            for raw in LINK.findall(line):
                finding = check_link(source, number, raw, cache)
                if finding:
                    findings.append(finding)
    return findings


def main(argv):
    if not argv:
        print(__doc__.strip().splitlines()[-2], file=sys.stderr)
        return 2
    findings = check(argv)
    for finding in findings:
        print(finding)
    if not findings:
        print(f"Odkazy v pořádku. Zkontrolováno souborů: {len(argv)}.")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
