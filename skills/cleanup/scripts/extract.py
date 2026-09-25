#!/usr/bin/env python3
"""Vytáhne z transcriptu session to, co se dá vytěžit, a spočítá, co ne.

Transcript je z devíti desetin technický balast: hooky, upomínky na tokeny,
snímky promptu, výpisy nástrojů a skillů. Měřeno 26. 9. 2026 na transcriptu
o 3,0 MB, ze kterého je vytěžitelného textu 234 kB, tedy **8 %**. Čtení
surového souboru proto stojí řádově víc než čtení téhož obsahu očištěného –
a stojí to znovu při každém dalším průchodu.

Skript má dva režimy:

- **`filter`** vypíše očištěný transcript. Každý řádek začíná číslem řádku
  původního `.jsonl`, aby se citace daly ověřit `sed -n`em nebo grepem – bez
  toho by se ztratila doložitelnost, na které stojí celý úklid.
- **`inventory`** vypíše, co v transcriptu je, rozdělené na **čtené** a
  **nečtené** kategorie, s počty a velikostmi. Je to podklad pro meze běhu:
  bez něj se hranice vytěžení přiznává odhadem, a co se nepřiznalo, nezjistí
  nikdo. Navíc vypíše číslovaný seznam uživatelských promptů – ty jsou kotvy
  evidence, protože u každého se dá odškrtnout, jestli se z něj něco zapsalo.

**Co se nečte a proč:**

- **Bloky myšlení** – v transcriptu jsou zapsané prázdné. Změřeno 26. 9. 2026
  na šesti transcriptech: pět z nich mělo 0 kB při desítkách až stovkách
  bloků, jeden 12,8 kB na 302 bloků. Není to tedy volba, ale vlastnost
  formátu: ten obsah tam není. Inventura to i tak vypíše, aby bylo vidět,
  kolik bloků se minulo.
- **Výstupy `Read`, `Grep`, `Glob`** – jejich obsahem jsou soubory, které se
  čtou přímo ze zdroje, kde jsou navíc aktuální.
- **Hooky, upomínky, snímky promptu, výpisy nástrojů** – balast bez obsahu.
- **Obrázky** – z transcriptu se vytěžit nedají.

**Transcript není nadmnožina kontextu ve všem.** Navíc má to, co kompaktace
z kontextu vyhodila – proto `inventory` počítá kompaktace. **Ale velký výstup
nástroje je v něm uříznutý stejně jako v kontextu** a plná verze leží
v `tool-results/<id>.txt`; inventura proto ty cesty vypíše, protože u měřicí
session tam bývá celá podstata.

Použití: extract.py filter|inventory <transcript.jsonl>
Návratový kód: 0 hotovo, 2 chyba volání.
"""

import json
import re
import sys
from collections import Counter

# Nástroje, jejichž výstup nese obsah, který nikde jinde není. Zprávy
# subagentů a stažené stránky sem patří právě proto, že zmizí se session.
CONTENT_TOOLS = ("Bash", "Agent", "Task", "WebFetch", "WebSearch", "mcp__")
SKIPPED_TOOLS = ("Read", "Grep", "Glob")
# Attachmenty, které nesou obsah od uživatele, ne technický balast.
CONTENT_ATTACHMENTS = ("queued_command",)
# Velký výstup nástroje se do transcriptu uloží **stejně uříznutý jako do
# kontextu** a plná verze leží v samostatném souboru. Transcript tedy není
# nadmnožina kontextu ve všem – tady mají oba stejnou díru a podstata měřicí
# session může být právě v ní. Ověřeno 26. 9. 2026.
PERSISTED = re.compile(r"Full output saved to:\s*(\S+)")


def load(path):
    """Vrátí [(číslo řádku, záznam)]; nečitelné řádky přeskočí."""
    rows = []
    with open(path, encoding="utf-8", errors="replace") as handle:
        for number, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append((number, json.loads(line)))
            except ValueError:
                continue
    return rows


def blocks(record):
    """Bloky obsahu záznamu jako seznam dictů; string obalí do textu."""
    content = (record.get("message") or {}).get("content")
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    if isinstance(content, list):
        return [b for b in content if isinstance(b, dict)]
    return []


def tool_names(rows):
    """Mapa id volání nástroje → jméno, aby se výsledek dal zařadit."""
    names = {}
    for _, record in rows:
        for block in blocks(record):
            if block.get("type") == "tool_use":
                names[block.get("id")] = block.get("name") or "?"
    return names


def result_text(block):
    """Text výsledku nástroje; struktury složí do jednoho řetězce."""
    content = block.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content if isinstance(b, dict))
    return ""


def classify(record, block, names):
    """Vrátí (kategorie, čte se, text) pro jeden blok záznamu."""
    kind = block.get("type")
    role = (record.get("message") or {}).get("role")
    if kind == "thinking":
        return "myšlení", False, ""
    if kind == "text":
        if role != "user":
            return "odpověď", True, block.get("text", "")
        # Vsuvka je záznam s rolí uživatele, který uživatel nenapsal: výpis
        # skillu, zpráva subagenta, upozornění harnessu. Pozná se podle
        # `isMeta` – ověřeno na třech transcriptech 26. 9. 2026. Čte se
        # (nese nálezy agentů), ale kotva evidence to není.
        label = "vsuvka" if record.get("isMeta") else "uživatel"
        return label, True, block.get("text", "")
    if kind == "tool_result":
        name = names.get(block.get("tool_use_id"), "?")
        if name.startswith(SKIPPED_TOOLS):
            return f"výstup {name}", False, ""
        if name.startswith(CONTENT_TOOLS):
            return f"výstup {name}", True, result_text(block)
        return f"výstup {name}", False, ""
    return None, False, ""


def extra_rows(number, record):
    """Zprávy poslané uprostřed odpovědi – jinak se tiše přehlédnou."""
    if record.get("type") == "queue-operation" and record.get("operation") == "enqueue":
        return [(number, "ve frontě", record.get("content") or "")]
    if record.get("type") == "attachment":
        attachment = record.get("attachment") or {}
        if attachment.get("type") in CONTENT_ATTACHMENTS:
            text = attachment.get("prompt") or attachment.get("command") or ""
            if not isinstance(text, str):
                text = json.dumps(text, ensure_ascii=False)
            return [(number, "ve frontě", text)]
    return []


def persisted(rows):
    """Cesty k plným výstupům, které se do transcriptu nevešly."""
    found = []
    for number, record in rows:
        for block in blocks(record):
            if block.get("type") != "tool_result":
                continue
            match = PERSISTED.search(result_text(block))
            if match:
                found.append((number, match.group(1)))
    return found


def compactions(rows):
    """Počet kompaktací – podle nich se pozná, co v kontextu už není."""
    return sum(1 for _, r in rows if r.get("isCompactSummary")
               or (r.get("compactMetadata") is not None))


def written_by_user(text):
    """Napsal to uživatel, nebo to do fronty vložil harness?

    Do fronty padají i notifikace o dokončení úlohy a zprávy subagentů. Mají
    tvar značky nebo hlášky systému, takže se poznají podle prvního znaku –
    uživatelův text značkou nezačíná.
    """
    text = text.strip()
    return bool(text) and not text.startswith("<") and not text.startswith("[SYSTEM")


def walk(rows):
    """Projde záznamy a vrátí (čtené řádky, počty kategorií, velikosti)."""
    names = tool_names(rows)
    kept, counts, sizes = [], Counter(), Counter()
    for number, record in rows:
        for label, text in [(lab, txt) for _, lab, txt in extra_rows(number, record)]:
            counts[label] += 1
            sizes[label] += len(text)
            kept.append((number, label, text))
        for block in blocks(record):
            label, readable, text = classify(record, block, names)
            if label is None:
                continue
            counts[label] += 1
            sizes[label] += len(text) if readable else 0
            if readable and text.strip():
                kept.append((number, label, text))
    return kept, counts, sizes


def run_filter(rows):
    """Vypíše očištěný transcript s čísly řádků původního souboru."""
    kept, _, _ = walk(rows)
    for number, label, text in kept:
        print(f"[{number}] {label.upper()}:")
        print(text.rstrip())
        print()
    return 0


def prompts(rows):
    """Co uživatel v session skutečně napsal – kotvy evidence.

    Patří sem prompty bez `isMeta` a zprávy poslané uprostřed odpovědi, které
    přicházejí jinou cestou (`queue-operation`) a snadno se přehlédnou. Naopak
    sem nepatří vsuvky s rolí uživatele, které nenapsal on.
    """
    found = []
    for number, record in rows:
        for _, _, text in extra_rows(number, record):
            if written_by_user(text):
                found.append((number, text.strip()))
        if (record.get("message") or {}).get("role") != "user" or record.get("isMeta"):
            continue
        for block in blocks(record):
            if block.get("type") != "text":
                continue
            if written_by_user(block.get("text", "")):
                found.append((number, block.get("text", "").strip()))
    return sorted(found)


def run_inventory(rows, path):
    """Vypíše, co v transcriptu je, a co z toho se čte."""
    _, counts, sizes = walk(rows)
    read = {k: v for k, v in counts.items() if sizes[k] or k in ("uživatel", "vsuvka", "odpověď", "ve frontě")}
    skip = {k: v for k, v in counts.items() if k not in read}
    print(f"INVENTURA: {path}")
    print(f"záznamů v souboru: {len(rows)}\n")
    print("ČTE SE:")
    total = 0
    for key in sorted(read, key=lambda k: -sizes[k]):
        total += sizes[key]
        print(f"  {counts[key]:5}× {key:24}{sizes[key] / 1024:9.1f} kB")
    print(f"  {'':5}  {'celkem':24}{total / 1024:9.1f} kB")
    print("\nNEČTE SE (patří do mezí běhu):")
    for key in sorted(skip, key=lambda k: -counts[k]):
        print(f"  {counts[key]:5}× {key}")
    cuts = compactions(rows)
    print(f"\nKOMPAKTACÍ: {cuts}"
          + ("  – část konverzace už v kontextu není, čti očištěný transcript celý"
             if cuts else "  – celý obsah je i v kontextu, stačí podle kotev projít jeho"))
    saved = persisted(rows)
    print(f"\nODLOŽENÝCH VÝSTUPŮ: {len(saved)} – uříznuté v transcriptu i v kontextu, plné jsou tady:")
    for number, path in saved:
        print(f"  [{number}] {path}")
    found = prompts(rows)
    print(f"\nUŽIVATELSKÝCH PROMPTŮ: {len(found)} – kotvy evidence, každý musí být odškrtnutý")
    for index, (number, text) in enumerate(found, 1):
        first = " ".join(text.split())[:100]
        print(f"  {index:3}. [{number}] {first}")
    return 0


def main(argv):
    if len(argv) != 2 or argv[0] not in ("filter", "inventory"):
        print("Použití: extract.py filter|inventory <transcript.jsonl>", file=sys.stderr)
        return 2
    mode, path = argv
    try:
        rows = load(path)
    except OSError as error:
        print(f"nelze přečíst {path}: {error}", file=sys.stderr)
        return 2
    if not rows:
        print(f"{path}: žádné čitelné záznamy", file=sys.stderr)
        return 2
    return run_filter(rows) if mode == "filter" else run_inventory(rows, path)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
