#!/usr/bin/env python3
"""Připíše položky do seznamu ke stažení, který odbavuje clockwork – bez duplicit a atomicky.

Formát seznamu je rozhraní clockworku (`~/Dev/clockwork/docs/architecture.md`,
*Úloha `download`*): položka `- [ ] <adresa>` nebo `- [ ] <adresa> → <jméno>`,
cílová složka je nadpis `## <cesta>` relativně k `~/Downloads`, položky před
prvním nadpisem jdou rovnou do `~/Downloads`. Clockwork soubor čte souběžně
a hotové řádky odškrtává, takže se nikdy nesmí potkat s napůl zapsaným souborem:
skript zapisuje dočasný soubor ve stejné složce a nahradí jím seznam přes
`os.replace`, celé pod zámkem seznamu sdíleným s clockworkem (`.<seznam>.lock`).

Použití: `add.py [--list SOUBOR]` a na stdin JSON

    {"items": [{"url": "…", "folder": "Kurz/Cvičení", "name": "…", "force": false}]}

`folder` chybí nebo je prázdný → kořen `~/Downloads`; `name` jen na pokyn uživatele;
`force` přidá adresu, i když v seznamu už je. Výstup je jeden řádek JSON:
`added`, `skipped` (duplicita i s tím, kde stojí a jestli je stažená), `rejected`
(co clockwork stáhnout neumí nebo co nejde zapsat) a `verified` – že se po zápisu
každá přidaná položka v souboru opravdu najde. Kód 1 znamená, že zápis selhal.
"""

import argparse
import fcntl
import json
import os
import re
import sys
import tempfile
import unicodedata
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

DEFAULT_LIST = Path("~/Downloads/downloads.md").expanduser()

# Tytéž tvary, které čte clockwork (`tasks/download/listing.py` a `source.py`):
# kdyby se rozešly, skript by duplicitu přehlédl, nebo zapsal řádek, který clockwork nepřečte.
ENTRY = re.compile(r"^- \[( |x|X)\] (\S+)(?:\s+(?:→|->)\s+(.*\S|\s))?\s*$")
HEADING = re.compile(r"^## (.*\S|\s)\s*$")
DRIVE_HOSTS = frozenset({"drive.google.com", "docs.google.com"})
FILE_PATH = re.compile(r"^/file/d/([^/]+)")
FOLDER_PATH = re.compile(r"^/drive/(?:u/\d+/)?folders/[^/]+")
GOOGLE_DOC = re.compile(r"^/(document|spreadsheets|presentation|forms|drawings)/")
ATTEMPTS = 3


def drive_id(url: str) -> str | None:
    """ID souboru z odkazu na Google Drive, jinak `None`."""
    parts = urlsplit(url)
    if parts.hostname not in DRIVE_HOSTS:
        return None
    if match := FILE_PATH.match(parts.path):
        return match.group(1)
    if parts.path in ("/open", "/uc"):
        ids = parse_qs(parts.query).get("id")
        return ids[0] if ids else None
    return None


def normalize(url: str) -> str:
    """Soubor na Google Drive v jedné podobě, ostatní adresy beze změny – jako clockwork."""
    file_id = drive_id(url)
    return f"https://drive.google.com/file/d/{file_id}/view" if file_id else url


def unsupported(url: str) -> str | None:
    """Proč clockwork adresu nestáhne, nebo `None`, když ji stáhnout umí."""
    parts = urlsplit(url)
    if (
        parts.scheme not in ("http", "https")
        or not parts.hostname
        or re.search(r"\s", url)
    ):
        return "adresa není http ani https"
    if parts.hostname == "drive.google.com" and FOLDER_PATH.match(parts.path):
        return "složka na Google Drive – rozbal ji"
    if parts.hostname == "docs.google.com" and GOOGLE_DOC.match(parts.path):
        return "dokument Google nejde stáhnout jako soubor"
    return None


def folder_path(folder: str | None) -> str | None:
    """Cílová složka jako nadpis seznamu, `""` pro kořen, `None` když jít nesmí."""
    if not folder:
        return ""
    parts = [
        unicodedata.normalize("NFC", p.strip())
        for p in folder.strip().strip("/").split("/")
    ]
    if folder.strip().startswith("/") or any(p in ("", ".", "..") for p in parts):
        return None
    if any(ord(c) < 32 or c == ":" for p in parts for c in p):
        return None
    return "/".join(parts)


def parse(lines: list[str]) -> tuple[dict, dict]:
    """Rozdělí seznam na sekce a posbírá adresy, které v něm už jsou.

    Vrací `sections` (složka → index nadpisu, kořen má `-1`) a `present`
    (normalizovaná adresa → (složka, staženo)) – kdekoliv v souboru, čekající i odškrtnuté.
    """
    sections, present, current = {"": -1}, {}, ""
    for i, line in enumerate(lines):
        if heading := HEADING.match(line):
            current = folder_path(heading.group(1)) or heading.group(1)
            sections.setdefault(current, i)
        elif entry := ENTRY.match(line):
            present.setdefault(
                normalize(entry.group(2)), (current, entry.group(1) != " ")
            )
    return sections, present


def insertion_point(lines: list[str], start: int) -> int:
    """Index za poslední položkou sekce, která začíná za řádkem `start`."""
    end = start + 1
    while end < len(lines) and not HEADING.match(lines[end]):
        end += 1
    point = start + 1
    for i in range(start + 1, end):
        if ENTRY.match(lines[i]):
            point = i + 1
    if start == -1 and point == 0:
        # Kořen bez položek: nad první nadpis, ne nad úvodní text, který tam autor má.
        point = end
        while point > 0 and not lines[point - 1].strip():
            point -= 1
    return point


def render(url: str, name: str | None) -> str:
    return f"- [ ] {url} → {name}" if name else f"- [ ] {url}"


def triage(items: list[dict], present: dict) -> tuple[list, list, list]:
    """Rozdělí položky na přidané, přeskočené (duplicita) a odmítnuté."""
    added, skipped, rejected, seen = [], [], [], set()
    for item in items:
        url = str(item.get("url", "")).strip()
        folder = folder_path(item.get("folder"))
        name = (item.get("name") or "").strip() or None
        reason = unsupported(url)
        if not reason and folder is None:
            reason = "cílová složka není relativní cesta pod ~/Downloads"
        if not reason and name and ("/" in name or ":" in name):
            reason = "požadované jméno obsahuje / nebo :"
        if reason:
            rejected.append({"url": url, "reason": reason})
            continue
        key = normalize(url)
        if key in seen or (key in present and not item.get("force")):
            where, done = present.get(key, (folder, False))
            skipped.append({"url": url, "folder": where, "done": done})
            continue
        seen.add(key)
        added.append({"url": key, "folder": folder, "name": name})
    return added, skipped, rejected


def insert(lines: list[str], added: list[dict]) -> list[str]:
    """Vloží přidané položky na konec jejich sekce; chybějící sekci založí na konci souboru."""
    out = list(lines)
    for folder in dict.fromkeys(a["folder"] for a in added):
        rows = [render(a["url"], a["name"]) for a in added if a["folder"] == folder]
        sections, _ = parse(out)  # indexy se posouvají s každým vložením, proto znovu
        if folder in sections:
            point = insertion_point(out, sections[folder])
            if point < len(out) and HEADING.match(out[point]):
                rows = rows + [""]  # kořen těsně nad nadpisem: oddělit prázdným řádkem
            out[point:point] = rows
            continue
        while out and not out[-1].strip():
            out.pop()
        out += ([""] if out else []) + [f"## {folder}"] + rows
    return out


def write_atomic(path: Path, lines: list[str]) -> None:
    path = Path(os.path.realpath(path))  # seznam jako odkaz: nahradit cíl, odkaz zůstane
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def snapshot(path: Path) -> tuple | None:
    try:
        st = path.stat()
    except FileNotFoundError:
        return None
    return st.st_mtime_ns, st.st_size


@contextmanager
def locked(path: Path) -> Iterator[None]:
    """Zámek seznamu sdílený s clockworkem: `flock` na `.<seznam>.lock` vedle seznamu.

    Kontrola otisku sama nestačí – clockwork mezi ní a `os.replace` zapisuje dočasný soubor
    a řádek připsaný v tom okně by jeho odškrtnutí smazalo.
    """
    fd = os.open(path.with_name(f".{path.name}.lock"), os.O_RDWR | os.O_CREAT, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


def run(path: Path, items: list[dict]) -> dict:
    """Načte seznam, vybere, co přidat, a zapíše pod zámkem; změnil-li se soubor, zkusí znovu."""
    with locked(path):
        return _attempts(path, items)


def _attempts(path: Path, items: list[dict]) -> dict:
    for _ in range(ATTEMPTS):
        before = snapshot(path)
        text = path.read_text(encoding="utf-8") if before else ""
        lines = text.splitlines()
        _, present = parse(lines)
        added, skipped, rejected = triage(items, present)
        if added:
            out = insert(lines, added)
            if snapshot(path) != before:
                continue  # clockwork nebo autor do souboru právě zapsal
            write_atomic(path, out)
        return {
            "list": str(path),
            "added": added,
            "skipped": skipped,
            "rejected": rejected,
            "verified": verify(path, added),
        }
    raise RuntimeError(f"{path} se měnil při každém z {ATTEMPTS} pokusů o zápis")


def verify(path: Path, added: list[dict]) -> bool:
    """Najde se každá přidaná položka v zapsaném souboru pod svou složkou?"""
    if not added:
        return True
    current, found = "", set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if heading := HEADING.match(line):
            current = folder_path(heading.group(1)) or heading.group(1)
        elif (entry := ENTRY.match(line)) and entry.group(1) == " ":
            found.add((current, entry.group(2), entry.group(3)))
    return all((a["folder"], a["url"], a["name"]) in found for a in added)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--list", type=Path, default=DEFAULT_LIST)
    args = parser.parse_args()
    try:
        items = json.load(sys.stdin)["items"]
        result = run(args.list.expanduser(), items)
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["verified"] else 1


if __name__ == "__main__":
    sys.exit(main())
