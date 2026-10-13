#!/usr/bin/env python3
# Společné jádro pro čas strávený v Claudovi: z transcriptů sessions, z `history.jsonl` a z gitu
# složí proud událostí a nad ním intervaly aktivity. Používá ho `/clauding` nad všemi sessions
# a `/invoicing recover` přes `invoicing/activity.py` nad projekty jednoho klienta.
#
# Metodiku a důvody drží `clauding/SKILL.md`, *Metodika*. Tady je jen její provedení – pravidlo,
# které by se změnilo jen v jednom ze dvou skriptů, by dalo dvě odpovědi na tutéž otázku.

import json
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

CLAUDE = Path.home() / ".claude"
PROJECTS = CLAUDE / "projects"
HISTORY = CLAUDE / "history.jsonl"

# Delší mezera mezi dvěma sousedními událostmi je pauza, kratší se počítá celá.
GAP = timedelta(minutes=20)

# Příkaz v popředí bez zadaného timeoutu smí běžet dvě minuty. Co je v mezeře do jeho výsledku
# navíc, nečekal Claude na příkaz, ale příkaz na schválení.
BASH_TIMEOUT_MS = 120_000

HARNESS_PREFIXES = (
    "<task-notification>",
    "<system-reminder>",
    "<local-command-",
    "Caveat:",
)


def encode(path: Path) -> str:
    # Claude Code nahradí v cestě každý znak mimo [A-Za-z0-9] pomlčkou – i každé písmeno s diakritikou zvlášť.
    return re.sub(r"[^A-Za-z0-9]", "-", str(path))


def moment(stamp: str) -> datetime:
    return datetime.fromisoformat(stamp.replace("Z", "+00:00")).astimezone()


def prompt_text(record: dict) -> str:
    content = record["message"]["content"]
    if isinstance(content, list):
        content = " ".join(
            part.get("text", "")
            for part in content
            if isinstance(part, dict) and part.get("type") == "text"
        )
    return " ".join(content.split())[:100]


def is_prompt(record: dict, in_subagent: bool) -> bool:
    # Zpráva, kterou napsal uživatel – ne výsledek nástroje, ne zpráva uvnitř subagenta a ne to,
    # co do konverzace vložil harness sám (dokončený agent na pozadí, připomínka).
    if (
        record.get("type") != "user"
        or record.get("isSidechain")
        or record.get("isMeta")
        or in_subagent
    ):
        return False
    content = record.get("message", {}).get("content")
    if isinstance(content, list):
        if not any(
            isinstance(part, dict) and part.get("type") == "text" for part in content
        ):
            return False
    elif not isinstance(content, str):
        return False
    return not prompt_text(record).startswith(HARNESS_PREFIXES)


def project_dirs(prefixes=None):
    """Adresáře s transcripty; s prefixy jen ty, které pod některý z nich spadají."""
    codes = None if prefixes is None else [encode(p) for p in prefixes]
    for project in sorted(PROJECTS.iterdir()):
        if not project.is_dir():
            continue
        if codes is None or any(
            project.name == c or project.name.startswith(c + "-") for c in codes
        ):
            yield project


def records(log: Path):
    try:
        lines = log.open(encoding="utf-8", errors="replace")
    except OSError:
        return  # soubor zmizel mezi výpisem adresáře a čtením – běžící úklid
    with lines:
        for line in lines:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict):
                yield record


def foreground_bash(record: dict):
    """(id, limit v ms) pro každé volání Bashe v popředí, které záznam odpovědi nese."""
    content = (record.get("message") or {}).get("content")
    if record.get("type") != "assistant" or not isinstance(content, list):
        return
    for part in content:
        if not (isinstance(part, dict) and part.get("type") == "tool_use"):
            continue
        tool_input = part.get("input") or {}
        if part.get("name") == "Bash" and not tool_input.get("run_in_background"):
            yield part.get("id"), tool_input.get("timeout") or BASH_TIMEOUT_MS


def tool_result_id(record: dict):
    content = (record.get("message") or {}).get("content")
    if record.get("type") == "user" and isinstance(content, list) and content:
        first = content[0]
        if isinstance(first, dict) and first.get("type") == "tool_result":
            return first.get("tool_use_id")
    return None


def log_events(log: Path, in_subagent: bool):
    """(okamžik, druh, text) pro každý záznam s časem v jednom transcriptu.

    Aktivitou je **každý** záznam s časem, nejen prompt a odpověď: příkaz harnessu,
    spuštěné hooky i shrnutí po návratu jsou doklad, že se v Claudovi něco dělo.
    K tomu umělá událost na konci povoleného běhu příkazu, jehož výsledek přišel
    později – tím se doba běhu započte a zbytek mezery zůstane pauzou.
    """
    running = {}
    for record in records(log):
        stamp = record.get("timestamp")
        if not stamp:
            continue
        at = moment(stamp)
        for tool_id, limit in foreground_bash(record):
            running[tool_id] = at + timedelta(milliseconds=limit)
        allowed_end = running.pop(tool_result_id(record), None)
        if allowed_end is not None and allowed_end < at:
            yield allowed_end, "claude", None
        if is_prompt(record, in_subagent):
            yield at, "prompt", prompt_text(record)
        else:
            yield at, "claude", None


def session_events(prefixes=None, start=None, end=None):
    """(okamžik, druh, zdroj, text) ze všech transcriptů, volitelně omezené na projekty a období."""
    for project in project_dirs(prefixes):
        for log in project.rglob("*.jsonl"):
            in_subagent = "subagents" in log.parts
            for at, kind, text in log_events(log, in_subagent):
                if (start is None or start <= at) and (end is None or at < end):
                    yield at, kind, project.name, text


def transcript_sessions() -> set:
    """Id sessions, které mají transcript – podle nich se pozná den bez úplných dat."""
    return {log.stem for log in PROJECTS.glob("*/*.jsonl")}


def history_prompts():
    """(okamžik, id session, pracovní adresář, text) pro každý prompt z `history.jsonl`.

    Sahá dál do minulosti než transcripty, protože ho úklid starých sessions nemaže.
    """
    for record in records(HISTORY):
        stamp = record.get("timestamp")
        if isinstance(stamp, (int, float)):
            yield (
                datetime.fromtimestamp(stamp / 1000).astimezone(),
                record.get("sessionId"),
                record.get("project"),
                record.get("display") or "",
            )


def working_dirs() -> set:
    """Každý adresář, ve kterém kdy běžela session – z transcriptů i z `history.jsonl`."""
    dirs = {project for _, _, project, _ in history_prompts() if project}
    for log in PROJECTS.glob("*/*.jsonl"):
        for record in records(log):
            if record.get("cwd"):
                dirs.add(record["cwd"])
                break
    return dirs


def repository(path: Path):
    """Kořen repozitáře, ve kterém cesta leží, nebo None."""
    if not path.is_dir():
        return None
    top = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
    )
    return top.stdout.strip() if top.returncode == 0 else None


def git_events(prefix: Path, start=None, end=None, own=False):
    """(okamžik, "commit", repozitář, předmět) pro commity repozitáře, ve kterém prefix leží.

    `own` omezí commity na autora nastaveného v tom repozitáři – v cizím repozitáři,
    kde pracuje víc lidí, by jinak cizí commit vypadal jako vlastní práce.
    """
    top = repository(prefix)
    if top is None:
        return
    command = ["git", "-C", top, "log", "--all", "--format=%aI%x09%s"]
    if own:
        email = subprocess.run(
            ["git", "-C", top, "config", "user.email"], capture_output=True, text=True
        ).stdout.strip()
        if not email:
            return
        command.append(f"--author={email}")
    log = subprocess.run(command, capture_output=True, text=True).stdout
    for line in log.splitlines():
        stamp, _, subject = line.partition("\t")
        at = datetime.fromisoformat(stamp).astimezone()
        if (start is None or start <= at) and (end is None or at < end):
            yield at, "commit", top, subject


def intervals(moments) -> list:
    """Sloučené intervaly [od, do] nad seřazeným proudem okamžiků podle pravidla mezery."""
    merged = []
    previous = None
    for at in sorted(moments):
        if previous is not None and at - previous <= GAP:
            if merged and merged[-1][1] >= previous:
                merged[-1][1] = max(merged[-1][1], at)
            else:
                merged.append([previous, at])
        previous = at
    return merged
