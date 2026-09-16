#!/usr/bin/env python3
"""Vypíše živé session Claude Code a k větvím projektu poslední opuštěnou session.

`/next` podle toho rozliší větev, nad kterou je právě otevřená session ve vedlejším
okně (úkol se **nesmí** nabídnout), od větve, která zůstala rozdělaná a opuštěná
(nabídne se pokračování i s ID session pro `/resume`). Session ve worktree layoutu
startuje v kořeni kontejneru, takže pracovní adresář procesu větev neprozradí –
prozradí ji až poslední zpráva v transcriptu, která nese `cwd` a `gitBranch`.

Zdroje (formát Claude Code, oficiálně nedokumentovaný – proto výstup nese i to,
co se přečíst nepodařilo, a nikdy si nic nedomýšlí):

- `~/.claude/sessions/<pid>.json` – registr spuštěných session (`pid`, `sessionId`,
  `cwd` startu, `name`, `status`). Soubor po spadlém procesu může zůstat, takže
  se živost ověřuje signálem 0.
- `~/.claude/projects/*/<sessionId>.jsonl` – transcript; bere se poslední záznam
  s `gitBranch`.

Použití: `sessions.py [--project <kořen projektu nebo kontejneru>]`

Výstup: JSON na stdout.
- `sessions` – živé session: `pid`, `session_id`, `name`, `status`, `start_cwd`,
  `cwd`, `branch` (null, když se nedala zjistit), `self` (session, ze které se
  skript spustil) a s `--project` i `in_project` (start nebo poslední zpráva
  leží v projektu – stejně pojmenovaná větev cizího repozitáře se nepočítá).
- `idle` – jen s `--project`: pro každou větev poslední session, jejíž poslední
  zpráva leží v projektu a **která neběží** (`session_id`, `start_cwd` – adresář
  první zprávy, odkud se session obnovuje –, `cwd`, `branch`, `updated` jako Unix
  čas). Session, která je živá – i obnovená přes `/resume` v jiném okně –, sem
  nepatří nikdy.

Návratový kód 2, když registr neexistuje **nebo se některý jeho záznam nedá
přečíst** – nečitelný záznam může patřit běžící session, takže by se jinak mohla
nabídnout k obnovení. `/next` pak bere všechny větve jako obsazené a řekne to.
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# Kolik bajtů od konce transcriptu se čte. Poslední záznam s větví bývá v posledních
# pár zprávách; celý soubor mívá desítky megabajtů.
TAIL_BYTES = 512 * 1024


def alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        # Proces existuje, jen patří jinému uživateli.
        return True
    return True


def ancestors() -> set:
    """PID všech předků tohohle procesu – mezi nimi je session, která skript pustila."""
    out, pid = set(), os.getpid()
    while pid > 1:
        out.add(pid)
        try:
            ppid = subprocess.run(["ps", "-o", "ppid=", "-p", str(pid)],
                                  capture_output=True, text=True, check=True).stdout.strip()
            pid = int(ppid)
        except (subprocess.CalledProcessError, ValueError):
            break
    return out


def last_location(transcript: Path):
    """Vrátí (cwd, gitBranch) z posledního záznamu, který větev nese."""
    with transcript.open("rb") as f:
        f.seek(0, os.SEEK_END)
        f.seek(max(0, f.tell() - TAIL_BYTES))
        lines = f.read().decode("utf-8", errors="replace").splitlines()
    for line in reversed(lines):
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(entry, dict) and entry.get("gitBranch"):
            return entry.get("cwd"), entry["gitBranch"]
    return None, None


class Unreadable(Exception):
    pass


def first_cwd(transcript: Path):
    """Adresář první zprávy, která ho nese – tam session startovala."""
    with transcript.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(entry, dict) and entry.get("cwd"):
                return entry["cwd"]
    return None


def live_sessions(home: Path) -> list:
    mine = ancestors()
    out = []
    for path in sorted((home / "sessions").glob("*.json")):
        try:
            record = json.loads(path.read_text())
            pid = int(record["pid"])
        except (json.JSONDecodeError, KeyError, ValueError, TypeError, OSError) as err:
            raise Unreadable(f"záznam {path} nejde přečíst: {err}")
        if not alive(pid):
            continue
        sid = record.get("sessionId")
        found = sorted(home.glob(f"projects/*/{sid}.jsonl")) if sid else []
        cwd, branch = last_location(found[0]) if found else (None, None)
        out.append({"pid": pid, "session_id": sid, "name": record.get("name"),
                    "status": record.get("status"), "start_cwd": record.get("cwd"),
                    "cwd": cwd, "branch": branch, "self": pid in mine})
    return out


def inside(path, project: Path) -> bool:
    if not path:
        return False
    p = Path(path)
    return p == project or project in p.parents


def idle_sessions(home: Path, project: Path, live_ids: set) -> list:
    """Poslední neběžící session pro každou větev projektu."""
    latest = {}
    for transcript in home.glob("projects/*/*.jsonl"):
        sid = transcript.stem
        if sid in live_ids:
            continue
        cwd, branch = last_location(transcript)
        if not branch or not inside(cwd, project):
            continue
        updated = transcript.stat().st_mtime
        if branch not in latest or updated > latest[branch]["updated"]:
            latest[branch] = {"session_id": sid, "start_cwd": first_cwd(transcript),
                              "cwd": cwd, "branch": branch, "updated": int(updated)}
    return sorted(latest.values(), key=lambda s: s["branch"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project")
    args = parser.parse_args()
    home = Path.home() / ".claude"
    if not (home / "sessions").is_dir():
        print(f"registr session {home / 'sessions'} neexistuje", file=sys.stderr)
        return 2
    try:
        result = {"sessions": live_sessions(home)}
    except Unreadable as err:
        print(err, file=sys.stderr)
        return 2
    if args.project:
        project = Path(args.project).resolve()
        for s in result["sessions"]:
            s["in_project"] = inside(s["start_cwd"], project) or inside(s["cwd"], project)
        live_ids = {s["session_id"] for s in result["sessions"] if s["session_id"]}
        result["idle"] = idle_sessions(home, project, live_ids)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
