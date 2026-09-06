"""Vygeneruje MD soubory facebookových postů po letech podle konvence archivu.

Zdroj: your_posts__check_ins__photos_and_videos_1.json z oficiálního exportu.
Bere jen příspěvky s textem (beztextová sdílení a fotky se vynechávají).
Pozor: FB export kóduje UTF-8 jako latin-1 escapy — nutná oprava (mojibake).
FB export neobsahuje URL jednotlivých příspěvků.
"""
import sys
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

if len(sys.argv) < 3:
    sys.exit("Použití: gen_facebook_md.py <your_posts__…_1.json> <výstupní adresář> [URL profilu]")
SRC = Path(sys.argv[1])
OUT = Path(sys.argv[2])
PROFIL = f" ({sys.argv[3]})" if len(sys.argv) > 3 else ""

OUT.mkdir(parents=True, exist_ok=True)


def fix(s):
    try:
        return s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


data = json.load(SRC.open())

items = []
skipped = 0
for p in data:
    ts = p.get("timestamp")
    texts = [fix(d["post"]).replace("\r\n", "\n").replace("\r", "\n").strip()
             for d in p.get("data", []) if "post" in d and fix(d["post"]).strip()]
    if not ts or not texts:
        skipped += 1
        continue
    dt = datetime.fromtimestamp(ts, timezone.utc)

    bullets = []
    for att in p.get("attachments", []):
        for ad in att.get("data", []):
            ec = ad.get("external_context") or {}
            url = fix(ec.get("url", ""))
            name = fix(ec.get("name", ""))
            if url and url not in ("facebook.com",):
                bullets.append(f"- Sdílený odkaz: {url}" + (f" ({name})" if name else ""))
            pl = ad.get("place") or {}
            if pl.get("name"):
                bullets.append(f"- Místo: {fix(pl['name'])}")
    bullets = list(dict.fromkeys(bullets))

    items.append((dt, bullets, "\n\n".join(texts)))

items.sort(key=lambda x: x[0])
print(f"celkem s textem: {len(items)}, vynecháno bez textu: {skipped}")

by_year = defaultdict(list)
for it in items:
    by_year[it[0].year].append(it)

for year, ilist in sorted(by_year.items()):
    blocks = []
    for dt, bullets, text in ilist:
        stamp = f"{dt.day}. {dt.month}. {dt.year} {dt.strftime('%H:%M')} UTC"
        head = [f"### {stamp}"] + bullets
        blocks.append("\n".join(head) + "\n\n" + text)
    content = (
        f"# Facebook – příspěvky {year}\n\n"
        f"- **Médium:** Facebook{PROFIL}\n"
        f"- **Období:** rok {year}\n"
        f"- **Počet příspěvků:** {len(ilist)}\n"
        f"- **Zdroj:** oficiální export `{SRC}`\n"
        f"- **Poznámka:** časy jsou v UTC; beztextová sdílení, fotky bez popisu a check-iny bez textu nejsou zahrnuty; export neobsahuje URL jednotlivých příspěvků\n\n"
        f"---\n\n"
        + "\n\n".join(blocks) + "\n"
    )
    (OUT / f"Facebook {year}.md").write_text(content, encoding="utf-8")
    print(f"  Facebook {year}.md — {len(ilist)} příspěvků")
