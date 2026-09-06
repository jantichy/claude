"""Vytáhne posty z Bluesky CAR exportu (AT Protocol repo) včetně rkeys z MST.

CAR v1: [varint délka][blok], první blok je CBOR hlavička s roots.
Blok = CID (v1: varint verze, varint kodek, multihash 0x12 0x20 + 32 B) + DAG-CBOR data.
Rkey každého záznamu je v MST stromu: commit blok (did+sig+data) → root MST uzel,
uzly mají 'l' (levý podstrom) a 'e' (entries s prefixovou kompresí klíčů).
"""
import io
import json
import sys
from pathlib import Path

import cbor2

if len(sys.argv) < 3:
    sys.exit("Použití: parse_bluesky.py <repo.car> <výstupní bluesky_posts.json> [handle]")
SRC = Path(sys.argv[1])
HANDLE = sys.argv[3] if len(sys.argv) > 3 else None


def read_varint(f):
    shift = 0
    result = 0
    while True:
        b = f.read(1)
        if not b:
            return None
        result |= (b[0] & 0x7F) << shift
        if not (b[0] & 0x80):
            return result
        shift += 7


def iter_blocks(path):
    """Vrací (cid_bytes, codec, data) pro každý blok CAR souboru."""
    with path.open("rb") as f:
        header_len = read_varint(f)
        f.read(header_len)
        while True:
            length = read_varint(f)
            if length is None:
                break
            block = f.read(length)
            bio = io.BytesIO(block)
            start = bio.tell()
            read_varint(bio)  # verze CID
            codec = read_varint(bio)
            read_varint(bio)  # hash fn
            hash_len = read_varint(bio)
            bio.read(hash_len)
            cid_bytes = block[start:bio.tell()]
            yield cid_bytes, codec, bio.read()


def tag_to_cid_bytes(tag):
    """CBOR tag 42 (IPLD link) -> raw CID bytes (bez multibase 0x00 prefixu)."""
    return tag.value[1:] if tag is not None else None


def load_repo(path=SRC):
    """Vrací (did, {klíč 'kolekce/rkey': záznam})."""
    blocks = {}
    commit = None
    for cid, codec, data in iter_blocks(path):
        if codec != 0x71:
            continue
        try:
            obj = cbor2.loads(data)
        except Exception:
            continue
        blocks[cid] = obj
        if isinstance(obj, dict) and "did" in obj and "sig" in obj and "data" in obj:
            commit = obj

    assert commit, "commit blok nenalezen"
    records = {}

    def walk(node_cid_bytes):
        node = blocks.get(node_cid_bytes)
        if not isinstance(node, dict) or "e" not in node:
            return
        if node.get("l") is not None:
            walk(tag_to_cid_bytes(node["l"]))
        prev_key = b""
        for entry in node["e"]:
            key = prev_key[: entry["p"]] + entry["k"]
            prev_key = key
            val_cid = tag_to_cid_bytes(entry["v"])
            if val_cid in blocks:
                records[key.decode()] = blocks[val_cid]
            if entry.get("t") is not None:
                walk(tag_to_cid_bytes(entry["t"]))

    walk(tag_to_cid_bytes(commit["data"]))
    return commit["did"], records


def at_uri_to_url(uri):
    """at://did/collection/rkey -> https://bsky.app/profile/did/post/rkey"""
    parts = uri.replace("at://", "").split("/")
    if len(parts) == 3 and parts[1] == "app.bsky.feed.post":
        return f"https://bsky.app/profile/{parts[0]}/post/{parts[2]}"
    return uri


if __name__ == "__main__":
    did, records = load_repo()
    print("DID:", did)
    # Handle se dá dohledat na https://plc.directory/<did>; bez něj URL nese DID,
    # což Bluesky rozumí taky. Vlastníka nikdy nehádej z prvního DID v exportu —
    # ten patří cizímu sledovanému účtu.
    if not HANDLE:
        print("handle nezadán – URL ponesou DID")
    posts = []
    for key, rec in records.items():
        if not key.startswith("app.bsky.feed.post/"):
            continue
        rkey = key.split("/", 1)[1]
        embed = rec.get("embed", {})
        quote_uri = None
        et = embed.get("$type", "")
        if et == "app.bsky.embed.record":
            quote_uri = embed.get("record", {}).get("uri")
        elif et == "app.bsky.embed.recordWithMedia":
            quote_uri = embed.get("record", {}).get("record", {}).get("uri")
        links = []
        for f in rec.get("facets", []):
            for feat in f.get("features", []):
                if feat.get("$type") == "app.bsky.richtext.facet#link":
                    links.append(feat["uri"])
        ext = embed.get("external", {})
        if isinstance(ext, dict) and ext.get("uri"):
            links.append(ext["uri"])
        posts.append({
            "rkey": rkey,
            "url": f"https://bsky.app/profile/{HANDLE or did}/post/{rkey}",
            "uri": f"at://{did}/app.bsky.feed.post/{rkey}",
            "createdAt": rec.get("createdAt", ""),
            "text": rec.get("text", ""),
            "reply_parent": (rec.get("reply") or {}).get("parent", {}).get("uri"),
            "quote": quote_uri,
            "links": links,
        })
    posts.sort(key=lambda p: p["createdAt"])
    out = Path(sys.argv[2])
    out.write_text(json.dumps(posts, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"posts: {len(posts)} -> {out}")
