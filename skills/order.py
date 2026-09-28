#!/usr/bin/env python3
"""Ověří, že datované záznamy v Markdownu jdou vzestupně – nejstarší nahoře.

`~/.claude/STRUCTURE.md` (*`done.md`*, *`decisions.md`*) žádá nejstarší zápis
nahoře a nový na konec sekce. Zdůvodnění je provozní: připsat na konec je
jediný způsob zápisu, který nejde udělat špatně, protože nevyžaduje hledat
správné místo.

**Bez kontroly to nevydrží.** Do sekcí zapisují skilly samy a každý se řídí
tím, co v souboru zrovna vidí, takže jeden obrácený zápis stačí, aby ho další
napodobily. Naměřeno 28. 9. 2026: *Průchody životním cyklem* se rozešly
počtvrté (2 zlomy), *Odvedená práce* měla 9 zlomů a `decisions.md` 2. Ruční
srovnání se do té doby dělalo třikrát a pokaždé se to vrátilo.

Záznamem je odrážka na nulovém odsazení nebo nadpis `### `; datum se bere
**z jeho prvního řádku**, takže datum ve vnořené poznámce ani v textu pod
záznamem nic neznamená. Nedatované záznamy se přeskakují – sekce mívá úvodní
odrážku a záznam bez data není vada pořadí.

Vyloučeno je schválně:

- **bloky kódu** – ukázka zápisu uvnitř nich není záznam. Falešný poplach je
  ta horší polovina selhání: kontrolu, která křičí na správný text, si člověk
  vypne a pak nehlídá nic.
- **české datum** (`27. 9. 2026`) – v textu záznamu odkazuje na to, kdy se něco
  stalo, ne kdy se to zapsalo. Hledá se jen ISO tvar.

Použití: order.py <soubor.md> [...]
Návratový kód: 0 čisto, 1 nálezy, 2 chyba volání.
"""

import re
import sys
from pathlib import Path

DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
FENCE = re.compile(r"^\s*(```|~~~)")
SECTION = re.compile(r"^## +(.*?)\s*#*$")
RECORD = re.compile(r"^(?:[-*] |### )")


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


def records(text):
    """[(sekce, číslo řádku, datum)] pro datované záznamy nejvyšší úrovně."""
    out, section = [], None
    for number, line in outside_fences(text):
        heading = SECTION.match(line)
        if heading:
            section = heading.group(1)
            continue
        if not RECORD.match(line):
            continue
        found = DATE.search(line)
        if found:
            out.append((section, number, found.group(0)))
    return out


def breaks(entries):
    """Dvojice sousedních záznamů, kde datum klesne."""
    return [(a, b) for a, b in zip(entries, entries[1:]) if b[1] < a[1]]


def check(paths):
    """Nálezy: jeden na sekci, ne na záznam.

    Hlásit každý záznam pod nejvyšším dosud viděným datem znamená u sekce
    s jedním obráceným zápisem nahoře vypsat celý soubor – a takový výstup
    nikdo nedočte, takže se kontrola přestane pouštět. Sekce je zároveň
    jednotka, ve které se pořadí opravuje.
    """
    findings = []
    for path in paths:
        try:
            text = Path(path).read_text(encoding="utf-8")
        except OSError as error:
            findings.append(f"{path}: nelze přečíst – {error}")
            continue
        sections = {}
        for section, number, date in records(text):
            sections.setdefault(section, []).append((number, date))
        for section, entries in sections.items():
            found = breaks(entries)
            if not found:
                continue
            (first_line, first_date), (next_line, next_date) = found[0]
            where = f", sekce *{section}*" if section else ""
            findings.append(
                f"{path}{where}: {len(found)} × klesá datum mezi sousedními záznamy "
                f"z {len(entries)} – poprvé na řádku {next_line} ({next_date} pod "
                f"{first_date} z řádku {first_line}). Nejstarší patří nahoru, nový na konec.")
    return findings


def main(argv):
    if not argv:
        print("Použití: order.py <soubor.md> [...]", file=sys.stderr)
        return 2
    findings = check(argv)
    for finding in findings:
        print(finding)
    if not findings:
        print(f"Pořadí záznamů v pořádku. Zkontrolováno souborů: {len(argv)}.")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
