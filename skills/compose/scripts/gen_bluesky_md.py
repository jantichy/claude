"""Vygeneruje MD soubory Bluesky postů po letech.

Formát: pod mezinadpisem (datum a čas) hned URL postu; u odpovědí řádek
„Odpověď na:", u citací „Citace postu:". Navazující vlákna (self-reply řetězy,
typicky značené 🧵 N/M:) jsou sloučená pod jedním mezinadpisem prvního postu —
nejdřív URL všech dílů, pak texty.
"""
import sys
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def plural(n, one, few, many):
    """České skloňování podle počtu: 1 / 2–4 / 0 a 5 a víc."""
    if n == 1:
        return f"{n} {one}"
    if 2 <= n <= 4:
        return f"{n} {few}"
    return f"{n} {many}"


if len(sys.argv) < 3:
    sys.exit("Použití: gen_bluesky_md.py <bluesky_posts.json z parse_bluesky.py> <výstupní adresář>")
SRC = Path(sys.argv[1])
OUT = Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)

THREAD_MARK = re.compile(r"🧵|\b\d+\s*/\s*\d+\s*:")

posts = json.loads(SRC.read_text(encoding="utf-8"))
by_uri = {p["uri"]: p for p in posts}

# Profil vlastníka se odvozuje z URL prvního postu, které vyrobil parse_bluesky.py.
PROFIL = posts[0]["url"].rsplit("/post/", 1)[0] if posts else ""


def at_url(uri):
    parts = uri.replace("at://", "").split("/")
    if len(parts) == 3 and parts[1] == "app.bsky.feed.post":
        return f"https://bsky.app/profile/{parts[0]}/post/{parts[2]}"
    return uri


# --- detekce vláken: řetězy odpovědí sám na sebe ---
root_of = {}


def find_root(p):
    if p["uri"] in root_of:
        return root_of[p["uri"]]
    chain = []
    cur = p
    while True:
        chain.append(cur["uri"])
        parent = cur.get("reply_parent")
        if parent and parent in by_uri and root_of.get(parent) is None and parent not in chain:
            cur = by_uri[parent]
        else:
            break
    root = root_of.get(cur.get("reply_parent"), cur["uri"]) if cur.get("reply_parent") in by_uri else cur["uri"]
    for uri in chain:
        root_of[uri] = root
    return root


for p in posts:
    find_root(p)

groups = defaultdict(list)
for p in posts:
    groups[root_of[p["uri"]]].append(p)

# vlákno = skupina ≥2 postů, kde kořen není odpověď cizímu, NEBO nese 🧵 značku
threads = {}
for root_uri, members in groups.items():
    members.sort(key=lambda p: p["createdAt"])
    root = by_uri[root_uri]
    root_is_reply_to_other = root.get("reply_parent") and root["reply_parent"] not in by_uri
    marked = any(THREAD_MARK.search(m.get("text", "")[:40]) for m in members)
    if len(members) >= 2 and (not root_is_reply_to_other or marked):
        threads[root_uri] = members

in_thread = {m["uri"] for ms in threads.values() for m in ms}


def stamp(created):
    dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
    return f"{dt.day}. {dt.month}. {dt.year} {dt.strftime('%H:%M')} UTC"


def text_block(p):
    lines = [p.get("text", "").strip() or "*(bez textu)*"]
    extra = [u for u in p.get("links", []) if u not in p.get("text", "")]
    if extra:
        lines += ["", "Odkazy: " + " · ".join(dict.fromkeys(extra))]
    return "\n".join(lines)


def fmt_single(p):
    head = [f"### {stamp(p['createdAt'])}", f"- {p['url']}"]
    if p.get("reply_parent"):
        head.append(f"- Odpověď na: {at_url(p['reply_parent'])}")
    if p.get("quote"):
        head.append(f"- Citace postu: {at_url(p['quote'])}")
    return "\n".join(head) + "\n\n" + text_block(p)


def fmt_thread(members):
    root = members[0]
    head = [f"### {stamp(root['createdAt'])}"]
    head += [f"- {m['url']}" for m in members]
    if root.get("reply_parent"):
        head.append(f"- Odpověď na: {at_url(root['reply_parent'])}")
    for m in members:
        if m.get("quote"):
            head.append(f"- Citace postu: {at_url(m['quote'])}")
    return "\n".join(head) + "\n\n" + "\n\n".join(text_block(m) for m in members)


# --- výstup po letech (vlákno se řadí podle prvního postu) ---
items = []
for p in posts:
    if p["uri"] in in_thread:
        if p["uri"] in threads:
            items.append((p["createdAt"], fmt_thread(threads[p["uri"]]), len(threads[p["uri"]]), True))
    else:
        items.append((p["createdAt"], fmt_single(p), 1, False))

by_year = defaultdict(list)
for created, block, n, is_thread in items:
    by_year[created[:4]].append((created, block, n, is_thread))

for year, ilist in sorted(by_year.items()):
    ilist.sort(key=lambda x: x[0])
    n_posts = sum(i[2] for i in ilist)
    n_threads = sum(1 for i in ilist if i[3])
    replies = sum(1 for p in posts if p["createdAt"][:4] == year and p.get("reply_parent"))
    body = "\n\n".join(i[1] for i in ilist)
    content = (
        f"# Bluesky – posty {year}\n\n"
        f"- **Médium:** Bluesky ({PROFIL})\n"
        f"- **Období:** rok {year}\n"
        f"- **Počet postů:** {n_posts} (z toho {plural(replies, 'odpověď', 'odpovědi', 'odpovědí')}; "
        f"{plural(n_threads, 'sloučené vlákno', 'sloučená vlákna', 'sloučených vláken')})\n"
        f"- **Zdroj:** export repozitáře `{SRC}` (AT Protocol)\n"
        f"- **Poznámka:** časy jsou v UTC; reposty bez komentáře nejsou zahrnuty\n\n"
        f"---\n\n"
        f"{body}\n"
    )
    (OUT / f"Bluesky {year}.md").write_text(content, encoding="utf-8")
    print(f"  Bluesky {year}.md — {n_posts} postů, {n_threads} vláken")
