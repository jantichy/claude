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
  nikdo. Navíc vypíše číslovaný seznam uživatelských promptů – ty se
  odškrtávají v evidenci, protože u každého se dá říct, jestli se z něj něco
  zapsalo. Prompt je i slash příkaz a zpráva s vloženým obsahem, které
  harness balí do značek. **Prompt je i odpověď z dialogu `AskUserQuestion`** – výběr
  nabídnuté volby stejně jako *Other* s vlastním textem: rozhodnutí z nabídky
  mívá větší dopad než dovětek v promptu a evidence, která ho mine, hlásí
  čistý výsledek, přestože nic neměřila.

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
from pathlib import Path

# Nástroje, jejichž výstup nese obsah, který nikde jinde není. Zprávy
# subagentů a stažené stránky sem patří právě proto, že zmizí se session.
CONTENT_TOOLS = ("Bash", "Agent", "Task", "WebFetch", "WebSearch", "mcp__")
SKIPPED_TOOLS = ("Read", "Grep", "Glob")
# Dialog s volbami: jeho výstup je rozhodnutí uživatele, tedy prompt.
DIALOG_TOOL = "AskUserQuestion"
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


def dialog_answers(record, block):
    """Odpovědi z dialogu jako texty „otázka → odpověď“, jeden na otázku.

    Strukturu nese `toolUseResult` záznamu: `answers` mapuje otázku na
    zvolenou odpověď (u *Other* na vlastní text) a `annotations` k ní přidává
    poznámku. Chybí-li, vrátí se surový text výsledku – dialog se tak nikdy
    tiše neztratí, jen se hůř čte.
    """
    result = record.get("toolUseResult")
    answers = result.get("answers") if isinstance(result, dict) else None
    if not isinstance(answers, dict) or not answers:
        text = result_text(block).strip()
        return [text] if text else []
    notes = result.get("annotations") or {}
    texts = []
    for question, answer in answers.items():
        text = f"{question} → {answer}"
        note = (
            (notes.get(question) or {}).get("notes")
            if isinstance(notes, dict)
            else None
        )
        if note:
            text += f" (poznámka: {note})"
        texts.append(text)
    return texts


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
        # (nese nálezy agentů), ale prompt do evidence to není.
        label = "vsuvka" if record.get("isMeta") else "uživatel"
        return label, True, block.get("text", "")
    if kind == "tool_result":
        name = names.get(block.get("tool_use_id"), "?")
        if name == DIALOG_TOOL:
            return "dialog", True, "\n".join(dialog_answers(record, block))
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
    """Cesty k plným výstupům, které se do transcriptu nevešly.

    Hlásí se jen cesta, která na disku **opravdu je**. Vzor se totiž chytí
    i na text, který marker jen cituje – a to není okrajový případ: session
    nad konfigurační vrstvou čte soubory, které ten marker popisují, takže
    `<cesta>` ze zástupného symbolu v dokumentaci se do inventury dostala
    hned prvním během (28. 9. 2026). Fantom je tišší, než vypadá: skill si
    ho poctivě připíše do *Mezí běhu* jako nepřečtený podklad, a tím si
    nadsadí přiznanou díru. Ověření navíc chytí i opačný případ – odložený
    výstup, který mezitím někdo smazal, se dnes hlásí jako čitelný.
    """
    found = []
    for number, record in rows:
        for block in blocks(record):
            if block.get("type") != "tool_result":
                continue
            match = PERSISTED.search(result_text(block))
            if match and Path(match.group(1)).expanduser().exists():
                found.append((number, match.group(1)))
    return found


def compactions(rows):
    """Počet kompaktací – podle nich se pozná, co v kontextu už není."""
    return sum(
        1
        for _, r in rows
        if r.get("isCompactSummary") or (r.get("compactMetadata") is not None)
    )


#: Hlášky harnessu, které mají tvar uživatelského textu, ale nikdo je nenapsal.
HARNESS_NOTES = ("[Request interrupted", "[SYSTEM")
#: Značky, do kterých harness balí text, **který napsal uživatel**: slash
#: příkaz i s argumenty, vložený obsah a příkaz shellu za vykřičníkem. Ostatní
#: značky – `<system-reminder>`, `<local-command-stdout>`, `<task-notification>`
#: a hlášky hooků – vkládá harness sám, takže se za prompt nepočítají.
USER_TAGS = (
    "command-name",
    "command-message",
    "command-args",
    "pasted_content",
    "bash-input",
)
TAG = re.compile(r"<([\w-]+)")
COMMAND = re.compile(r"<command-name>(.*?)</command-name>", re.S)
COMMAND_ARGS = re.compile(r"<command-args>(.*?)</command-args>", re.S)


def user_text(text):
    """Text promptu, jak ho uživatel napsal, nebo None, vložil-li ho harness.

    Do fronty i do záznamů s rolí uživatele padají notifikace o dokončení
    úlohy, zprávy subagentů, výstupy lokálních příkazů a upomínky. Mají tvar
    značky nebo hlášky systému, takže rozhoduje začátek textu: bez značky je to
    prompt, se značkou jen tehdy, je-li to značka z `USER_TAGS`. Slash příkaz se
    vrátí jako `/jméno argumenty`, aby se v evidenci četl tak, jak se psal.
    Přerušení běhu je zvláštní případ: čte se jako věta, ale je to záznam
    o akci, ne obsah k zapsání.
    """
    text = text.strip()
    if not text or text.startswith(HARNESS_NOTES):
        return None
    if not text.startswith("<"):
        return text
    tag = TAG.match(text)
    if not tag or tag.group(1) not in USER_TAGS:
        return None
    command = COMMAND.search(text)
    if not command:
        return text
    args = COMMAND_ARGS.search(text)
    return (
        " ".join(
            part.strip() for part in (command.group(1), args.group(1) if args else "")
        ).strip()
        or text
    )


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
    """Co uživatel v session skutečně napsal – prompty do evidence.

    Patří sem prompty bez `isMeta` včetně slash příkazů a vloženého obsahu, za
    prompt se počítá i zpráva poslaná uprostřed odpovědi, která přichází jinou
    cestou (`queue-operation`) a snadno se přehlédne, a každá odpověď z dialogu.
    Naopak sem nepatří vsuvky s rolí uživatele, které nenapsal on.

    **Stejný text dvakrát jsou dva prompty.** Dvě odpovědi „ano“ na dvě různé
    otázky jsou dvě rozhodnutí; jediné, co se tu slučuje, je zpráva z fronty
    se svým vlastním doručením (`Queue`).
    """
    names = tool_names(rows)
    queue = Queue()
    found, turn = [], 0
    for number, record in rows:
        role = (record.get("message") or {}).get("role")
        turn += role == "assistant"
        for text in queue.texts(record):
            found.append((number, text, None))
        if role != "user" or record.get("isMeta"):
            continue
        for block in blocks(record):
            if block.get("type") == "text":
                text = queue.delivered(block.get("text", ""))
                if text:
                    found.append((number, text, turn))
            elif (
                block.get("type") == "tool_result"
                and names.get(block.get("tool_use_id")) == DIALOG_TOOL
            ):
                found.extend((number, t, None) for t in dialog_answers(record, block))
    return sorted(drop_drafts(found))


class Queue:
    """Páruje zprávu z fronty s jejím doručením.

    Zpráva poslaná uprostřed odpovědi je v transcriptu **dvakrát**: jako
    `queue-operation` při zařazení a jako `queued_command` při doručení. Bez
    párování by evidence žádala dva řádky na jednu větu a poměr by nikdy
    nesedl (odhaleno prvním ostrým během 26. 9. 2026). Páruje se **jen zařazení
    s doručením** – dřív se slučoval každý stejný text a druhé „ano“ na jinou
    otázku z inventury tiše vypadlo.
    """

    def __init__(self):
        self.pending = Counter()

    def texts(self, record):
        """Prompty ze záznamu fronty; doručení už spočítané zprávy přeskočí."""
        found = []
        for _, _, raw in extra_rows(0, record):
            text = user_text(raw)
            if not text:
                continue
            if record.get("type") == "queue-operation":
                self.pending[flat(text)] += 1
                found.append(text)
            elif not self.consume(text):
                found.append(text)
        return found

    def delivered(self, raw):
        """Text promptu, nebo None, je-li to doručení zprávy z fronty."""
        text = user_text(raw)
        return None if not text or self.consume(text) else text

    def consume(self, text):
        key = flat(text)
        if self.pending[key]:
            self.pending[key] -= 1
            return True
        return False


def flat(text):
    """Text bez rozdílů v bílých znacích – podle něj se porovnává."""
    return " ".join(text.split())


def drop_drafts(found):
    """Zahodí prompt, který je jen rozepsanou verzí jiného.

    Harness uloží prompt i ve stavu před doplněním, a to pod **jiným**
    `promptId`, takže podle něj se to rozlišit nedá (ověřeno 26. 9. 2026).
    Kratší verze je prefixem delší a nenese nic, co by v ní nebylo – zůstává
    proto ta delší. Bez toho by evidence žádala dva řádky na jednu větu
    a poměr by nikdy nesedl.

    **Rozepsaná verze se pozná i podle toho, že na ni nikdo neodpověděl:**
    slučují se jen prompty bez odpovědi mezi sebou (`turn`). Prompt, na který
    přišla odpověď, je samostatný, i když ho další prompt doslova opakuje
    a rozvádí – typicky opakovaně vložený a postupně upravovaný text. Zprávy
    z fronty a odpovědi z dialogu (`turn` None) se nikdy neslučují.
    """
    texts = [(number, flat(text), text, turn) for number, text, turn in found]
    kept = []
    for number, short, text, turn in texts:
        if turn is not None and any(
            other_turn == turn and other.startswith(short) and other != short
            for _, other, _, other_turn in texts
        ):
            continue
        kept.append((number, text))
    return kept


def run_inventory(rows, path):
    """Vypíše, co v transcriptu je, a co z toho se čte."""
    _, counts, sizes = walk(rows)
    read = {
        k: v
        for k, v in counts.items()
        if sizes[k] or k in ("uživatel", "vsuvka", "odpověď", "ve frontě", "dialog")
    }
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
    print(
        f"\nKOMPAKTACÍ: {cuts}"
        + (
            "  – část konverzace už v kontextu není, čti očištěný transcript celý"
            if cuts
            else "  – celý obsah je i v kontextu, stačí podle promptů projít jeho"
        )
    )
    saved = persisted(rows)
    print(
        f"\nODLOŽENÝCH VÝSTUPŮ: {len(saved)} – uříznuté v transcriptu i v kontextu, plné jsou tady:"
    )
    for number, path in saved:
        print(f"  [{number}] {path}")
    found = prompts(rows)
    print(
        f"\nUŽIVATELSKÝCH PROMPTŮ: {len(found)} – každý musí být v evidenci odškrtnutý"
    )
    for index, (number, text) in enumerate(found, 1):
        first = " ".join(text.split())[:100]
        print(f"  {index:3}. [{number}] {first}")
    return 0


def main(argv):
    if len(argv) != 2 or argv[0] not in ("filter", "inventory"):
        print(
            "Použití: extract.py filter|inventory <transcript.jsonl>", file=sys.stderr
        )
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
