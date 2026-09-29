#!/usr/bin/env python3
# Složí z session logů Clauda a z gitu bloky aktivity od–do – zdroj stop práce pro `/invoicing recover`.
#
# Použití:  python3 activity.py 2026-09-01 2026-09-30 ~/Dev/favi ~/Dev/veneti ~/Documents/Projekty/Favi
#           python3 activity.py --gap 30 2026-09-01 2026-09-30 ~/Dev/veneti
#
# Cesta je **prefix**, ne jeden projekt: `~/Documents/Projekty/Favi` pokryje i všechny
# projekty v jeho podadresářích. Session logy se hledají podle zakódovaného jména cesty
# v `~/.claude/projects/`, takže se najdou i tehdy, když adresář na disku už neexistuje.
# Git se čte jen z cest, které na disku jsou a jsou to repozitáře.
#
# Bloky se dělí podle mezery mezi dvěma sousedními záznamy; delší mezera než `--gap`
# minut blok ukončí. Výstup je JSON, jeden blok na položku, časy v místním pásmu.

import argparse
import json
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

PROJECTS = Path.home() / ".claude" / "projects"


def encode(path: Path) -> str:
    # Claude Code nahradí v cestě každý znak mimo [A-Za-z0-9] pomlčkou – i každé písmeno s diakritikou zvlášť.
    return re.sub(r"[^A-Za-z0-9]", "-", str(path))


HARNESS_PREFIXES = ("<task-notification>", "<system-reminder>", "<local-command-", "Caveat:")


def is_prompt(record: dict, in_subagent: bool) -> bool:
    # Zpráva, kterou napsal uživatel – ne výsledek nástroje, ne zpráva uvnitř subagenta a ne to,
    # co do konverzace vložil harness sám (dokončený agent na pozadí, připomínka). Ty nesou
    # roli `user`, ale u klávesnice přitom nikdo být nemusel.
    if record.get("type") != "user" or record.get("isSidechain") or record.get("isMeta") or in_subagent:
        return False
    content = record.get("message", {}).get("content")
    if isinstance(content, list):
        if not any(isinstance(part, dict) and part.get("type") == "text" for part in content):
            return False
    elif not isinstance(content, str):
        return False
    return not prompt_text(record).startswith(HARNESS_PREFIXES)


def prompt_text(record: dict) -> str:
    content = record["message"]["content"]
    if isinstance(content, list):
        content = " ".join(part.get("text", "") for part in content if isinstance(part, dict) and part.get("type") == "text")
    return " ".join(content.split())[:100]


def session_events(prefix: Path, start: datetime, end: datetime):
    code = encode(prefix)
    for project in sorted(PROJECTS.iterdir()):
        if not project.is_dir() or not (project.name == code or project.name.startswith(code + "-")):
            continue
        for log in project.rglob("*.jsonl"):
            in_subagent = "subagents" in log.parts
            for line in log.open(encoding="utf-8", errors="replace"):
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                stamp = record.get("timestamp")
                if not stamp:
                    continue
                moment = datetime.fromisoformat(stamp.replace("Z", "+00:00")).astimezone()
                if not start <= moment < end:
                    continue
                if is_prompt(record, in_subagent):
                    yield moment, "prompt", project.name, prompt_text(record)
                else:
                    yield moment, "claude", project.name, None


def git_events(prefix: Path, start: datetime, end: datetime):
    if not prefix.is_dir():
        return
    top = subprocess.run(["git", "-C", str(prefix), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if top.returncode != 0:
        return
    log = subprocess.run(
        ["git", "-C", str(prefix), "log", "--all", "--format=%aI%x09%s"],
        capture_output=True, text=True, check=True,
    ).stdout
    for line in log.splitlines():
        stamp, _, subject = line.partition("\t")
        moment = datetime.fromisoformat(stamp).astimezone()
        if start <= moment < end:
            yield moment, "commit", top.stdout.strip(), subject


def main():
    parser = argparse.ArgumentParser(description="Bloky aktivity ze session logů Clauda a z gitu.")
    parser.add_argument("--gap", type=int, default=20, help="mezera v minutách, která ukončí blok (výchozí 20)")
    parser.add_argument("since", help="od YYYY-MM-DD včetně")
    parser.add_argument("until", help="do YYYY-MM-DD včetně")
    parser.add_argument("paths", nargs="+", help="cesty k projektům klienta; každá platí i pro podadresáře")
    args = parser.parse_args()

    start = datetime.fromisoformat(args.since).astimezone()
    end = datetime.fromisoformat(args.until).astimezone() + timedelta(days=1)
    gap = timedelta(minutes=args.gap)

    events = []
    for raw in args.paths:
        prefix = Path(raw).expanduser().resolve()
        events += session_events(prefix, start, end)
        events += git_events(prefix, start, end)
    events.sort(key=lambda event: event[0])

    blocks = []
    for moment, kind, source, text in events:
        if not blocks or moment - blocks[-1]["_end"] > gap:
            blocks.append({"_start": moment, "_end": moment, "prompts": 0, "claude": 0, "commits": 0,
                           "sources": set(), "first_prompts": [], "commit_subjects": []})
        block = blocks[-1]
        block["_end"] = moment
        block["sources"].add(source)
        if kind == "prompt":
            block["prompts"] += 1
            if len(block["first_prompts"]) < 3:
                block["first_prompts"].append(text)
        elif kind == "commit":
            block["commits"] += 1
            if len(block["commit_subjects"]) < 5:
                block["commit_subjects"].append(text)
        else:
            block["claude"] += 1

    output = []
    for block in blocks:
        start_at, end_at = block.pop("_start"), block.pop("_end")
        output.append({
            "start": start_at.isoformat(timespec="minutes"),
            "end": end_at.isoformat(timespec="minutes"),
            "minutes": round((end_at - start_at).total_seconds() / 60),
            **{key: sorted(value) if isinstance(value, set) else value for key, value in block.items()},
        })
    print(json.dumps({"gap_minutes": args.gap, "blocks": output}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
