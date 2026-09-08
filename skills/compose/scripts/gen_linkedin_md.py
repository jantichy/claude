"""Vygeneruje MD soubory linkedinových postů a komentářů po letech.

Zdroj: Shares_*.csv (posty) + Comments_*.csv (komentáře) z oficiálního exportu.
InstantReposts (reposty bez komentáře) se vynechávají. Komentáře jsou řazené
chronologicky mezi posty a nesou odrážku „Odpověď na:" (vlastní URL komentáře
export neobsahuje).
"""
import sys
import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote


def plural(n, one, few, many):
    """České skloňování podle počtu: 1 / 2–4 / 0 a 5 a víc."""
    if n == 1:
        return f"{n} {one}"
    if 2 <= n <= 4:
        return f"{n} {few}"
    return f"{n} {many}"


if len(sys.argv) < 3:
    sys.exit("Použití: gen_linkedin_md.py <adresář s Shares_*.csv a Comments_*.csv> <výstupní adresář> [URL profilu]")
BASE = Path(sys.argv[1])
OUT = Path(sys.argv[2])
PROFIL = f" ({sys.argv[3]})" if len(sys.argv) > 3 else ""

OUT.mkdir(parents=True, exist_ok=True)

def strip_line_quotes(t):
    """LinkedIn balí každý vnitřní řádek víceřádkového pole do uvozovek — odstranit."""
    lines = t.split("\n")
    if len(lines) == 1:
        return t
    out = []
    for i, ln in enumerate(lines):
        if i > 0 and ln.startswith('"'):
            ln = ln[1:]
        if i < len(lines) - 1 and ln.endswith('"'):
            ln = ln[:-1]
        out.append(ln)
    return "\n".join(out)


items = []  # (dt, bullets, text, is_comment)

with next(BASE.glob("Shares_*.csv")).open(encoding="utf-8") as f:
    shares_total = 0
    shares_empty = 0
    for r in csv.DictReader(f):
        shares_total += 1
        text = strip_line_quotes((r["ShareCommentary"] or "")).replace("\r\n", "\n").replace("\r", "\n").strip()
        if not text:
            shares_empty += 1
            continue
        dt = datetime.strptime(r["Date"], "%Y-%m-%d %H:%M:%S")
        bullets = [f"- {unquote(r['ShareLink'])}"]
        if r.get("SharedUrl"):
            bullets.append(f"- Sdílený odkaz: {r['SharedUrl']}")
        items.append((dt, bullets, text, False))

with next(BASE.glob("Comments_*.csv")).open(encoding="utf-8") as f:
    comments_total = 0
    for r in csv.DictReader(f, escapechar="\\"):
        text = strip_line_quotes((r["Message"] or "")).replace("\r\n", "\n").replace("\r", "\n").strip()
        if not text:
            continue
        comments_total += 1
        dt = datetime.strptime(r["Date"], "%Y-%m-%d %H:%M:%S")
        bullets = [f"- Odpověď na: {unquote(r['Link'])}"]
        items.append((dt, bullets, text, True))

items.sort(key=lambda x: x[0])
print(f"shares: {shares_total} (bez textu vynecháno {shares_empty}), komentářů: {comments_total}")

by_year = defaultdict(list)
for it in items:
    by_year[it[0].year].append(it)

for year, ilist in sorted(by_year.items()):
    blocks = []
    n_comments = sum(1 for i in ilist if i[3])
    for dt, bullets, text, _ in ilist:
        stamp = f"{dt.day}. {dt.month}. {dt.year} {dt.strftime('%H:%M')} UTC"
        blocks.append("\n".join([f"### {stamp}"] + bullets) + "\n\n" + text)
    content = (
        f"# LinkedIn – posty a komentáře {year}\n\n"
        f"- **Médium:** LinkedIn{PROFIL}\n"
        f"- **Období:** rok {year}\n"
        f"- **Počet položek:** {len(ilist)} (z toho "
        f"{plural(n_comments, 'komentář', 'komentáře', 'komentářů')} u cizích postů)\n"
        f"- **Zdroj:** oficiální export `{BASE}`\n"
        f"- **Poznámka:** časy jsou v UTC; reposty bez komentáře nejsou zahrnuty; komentáře nemají v exportu vlastní URL – odkaz vede na komentovaný post\n\n"
        f"---\n\n"
        + "\n\n".join(blocks) + "\n"
    )
    (OUT / f"LinkedIn {year}.md").write_text(content, encoding="utf-8")
    print(f"  LinkedIn {year}.md — {len(ilist)} položek ({n_comments} komentářů)")
