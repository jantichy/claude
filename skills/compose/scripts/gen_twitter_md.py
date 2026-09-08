"""Vygeneruje MD soubory tweetů po letech podle konvence archivu.

Zdroj: data/tweets.js (+ note-tweet.js s plnými texty dlouhých tweetů)
z oficiálního Twitter exportu. Čisté retweety (RT @…) se vynechávají.
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
    sys.exit("Použití: gen_twitter_md.py <adresář data/ z rozbaleného exportu> <výstupní adresář>")
BASE = Path(sys.argv[1])
OUT = Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)

THREAD_MARK = re.compile(r"🧵|\b\d+\s*/\s*\d+\s*:")
STATUS_URL = re.compile(r"https?://(?:www\.)?(?:twitter|x)\.com/(\w+)/status(?:es)?/(\d+)")


def load(name):
    raw = (BASE / name).read_text(encoding="utf-8")
    return json.loads(raw[raw.index("["):])


# Vlastníka účtu čti z account.js, ne z prvního výskytu v datech — export je plný
# cizích identifikátorů (zmínky, odpovědi) a hádaný vlastník rozbije detekci vláken.
_account = load("account.js")[0]["account"]
ME = _account["username"]
MY_ID = _account["accountId"]


tweets_raw = [t["tweet"] for t in load("tweets.js")]
notes = [n["noteTweet"] for n in load("note-tweet.js")]

# plné texty dlouhých tweetů — párování podle času (±2 s)
notes_by_ts = {}
for n in notes:
    ts = datetime.fromisoformat(n["createdAt"].replace("Z", "+00:00")).timestamp()
    notes_by_ts[ts] = n["core"]["text"]


def parse_dt(s):
    return datetime.strptime(s, "%a %b %d %H:%M:%S %z %Y")


posts = []
n_rt = 0
for t in tweets_raw:
    text = t["full_text"]
    if text.startswith("RT @"):
        n_rt += 1
        continue
    dt = parse_dt(t["created_at"])

    # dlouhé tweety: nahradit zkrácený text plným z note-tweet
    for delta in (0, 1, -1, 2, -2):
        if dt.timestamp() + delta in notes_by_ts:
            text = notes_by_ts[dt.timestamp() + delta]
            break

    quotes = []
    for u in t.get("entities", {}).get("urls", []):
        exp = u.get("expanded_url") or u["url"]
        text = text.replace(u["url"], exp)
        m = STATUS_URL.match(exp)
        if m:
            quotes.append(f"https://x.com/{m.group(1)}/status/{m.group(2)}")
    for m_ent in t.get("entities", {}).get("media", []):
        text = text.replace(m_ent["url"], m_ent.get("display_url", m_ent["url"]))

    reply_url = None
    if t.get("in_reply_to_status_id_str"):
        screen = t.get("in_reply_to_screen_name") or "i/web"
        reply_url = f"https://x.com/{screen}/status/{t['in_reply_to_status_id_str']}"

    posts.append({
        "id": t["id_str"],
        "url": f"https://x.com/{ME}/status/{t['id_str']}",
        "dt": dt,
        "text": text.strip(),
        "reply_parent_id": t.get("in_reply_to_status_id_str"),
        "reply_parent_is_mine": t.get("in_reply_to_user_id_str") == MY_ID,
        "reply_url": reply_url,
        "quotes": quotes,
    })

posts.sort(key=lambda p: p["dt"])
by_id = {p["id"]: p for p in posts}

# --- vlákna: řetězy odpovědí sám na sebe ---
root_of = {}
for p in posts:
    chain = [p["id"]]
    cur = p
    while cur["reply_parent_is_mine"] and cur["reply_parent_id"] in by_id and cur["reply_parent_id"] not in chain:
        nxt = by_id[cur["reply_parent_id"]]
        if nxt["id"] in root_of:
            chain.append(root_of[nxt["id"]])
            break
        chain.append(nxt["id"])
        cur = nxt
    root = chain[-1]
    for cid in chain:
        root_of[cid] = root_of.get(root, root)

groups = defaultdict(list)
for p in posts:
    groups[root_of[p["id"]]].append(p)

threads = {}
for root_id, members in groups.items():
    members.sort(key=lambda p: p["dt"])
    root = by_id[root_id]
    root_is_reply_to_other = root["reply_parent_id"] and not (root["reply_parent_is_mine"] and root["reply_parent_id"] in by_id)
    marked = any(THREAD_MARK.search(m["text"][:40]) for m in members)
    if len(members) >= 2 and (not root_is_reply_to_other or marked):
        threads[root_id] = members

in_thread = {m["id"] for ms in threads.values() for m in ms}


def stamp(dt):
    return f"{dt.day}. {dt.month}. {dt.year} {dt.strftime('%H:%M')} UTC"


def fmt(p_or_members):
    members = p_or_members if isinstance(p_or_members, list) else [p_or_members]
    root = members[0]
    head = [f"### {stamp(root['dt'])}"]
    head += [f"- {m['url']}" for m in members]
    if root["reply_url"] and not (root["reply_parent_is_mine"] and root["reply_parent_id"] in by_id):
        head.append(f"- Odpověď na: {root['reply_url']}")
    for m in members:
        for q in m["quotes"]:
            head.append(f"- Citace postu: {q}")
    texts = "\n\n".join(m["text"] or "*(bez textu)*" for m in members)
    return "\n".join(head) + "\n\n" + texts


items = []
for p in posts:
    if p["id"] in in_thread:
        if p["id"] in threads:
            items.append((p["dt"], fmt(threads[p["id"]]), len(threads[p["id"]]), True))
    else:
        items.append((p["dt"], fmt(p), 1, False))

by_year = defaultdict(list)
for dt, block, n, is_thread in items:
    by_year[dt.year].append((dt, block, n, is_thread))

total = 0
for year, ilist in sorted(by_year.items()):
    ilist.sort(key=lambda x: x[0])
    n_posts = sum(i[2] for i in ilist)
    n_threads = sum(1 for i in ilist if i[3])
    replies = sum(1 for p in posts if p["dt"].year == year and p["reply_parent_id"])
    total += n_posts
    body = "\n\n".join(i[1] for i in ilist)
    content = (
        f"# Twitter – tweety {year}\n\n"
        f"- **Médium:** Twitter/X (https://x.com/{ME}, účet @{ME})\n"
        f"- **Období:** rok {year}\n"
        f"- **Počet tweetů:** {n_posts} (z toho {plural(replies, 'odpověď', 'odpovědi', 'odpovědí')}; "
        f"{plural(n_threads, 'sloučené vlákno', 'sloučená vlákna', 'sloučených vláken')})\n"
        f"- **Zdroj:** oficiální export `{BASE}`\n"
        f"- **Poznámka:** časy jsou v UTC; čisté retweety bez komentáře nejsou zahrnuty; zkrácené t.co odkazy jsou nahrazeny plnými URL\n\n"
        f"---\n\n"
        f"{body}\n"
    )
    (OUT / f"Twitter {year}.md").write_text(content, encoding="utf-8")
    print(f"  Twitter {year}.md — {n_posts} tweetů, {n_threads} vláken")

print(f"celkem: {total} tweetů (vynecháno {n_rt} čistých RT)")
