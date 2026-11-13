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
    "[Request interrupted",
)

# Harness zapíše místo promptu, když uživatel zastaví Clauda klávesou Esc. Varianta „for tool use“
# provází zamítnutí nástroje a počítá se jako zamítnutí, ne podruhé jako přerušení.
INTERRUPT = "[Request interrupted by user]"
REJECTION = "The user doesn't want to proceed"

# Přitakání v Claudově textu: „máš pravdu“, „Máš pravdu.“
AGREEMENT = re.compile(r"\bmáš pravdu\b", re.IGNORECASE)

# Ručně zadaný příkaz harness zapíše místo promptu jako
# `<command-message>merge</command-message> <command-name>/merge</command-name>`.
COMMAND = re.compile(r"<command-name>/?([^<\s]+)</command-name>")


def encode(path: Path) -> str:
    # Claude Code nahradí v cestě každý znak mimo [A-Za-z0-9] pomlčkou – i každé písmeno s diakritikou zvlášť.
    return re.sub(r"[^A-Za-z0-9]", "-", str(path))


def moment(stamp: str) -> datetime:
    return datetime.fromisoformat(stamp.replace("Z", "+00:00")).astimezone()


def message_text(record: dict) -> str:
    content = record["message"]["content"]
    if isinstance(content, list):
        content = " ".join(
            part.get("text", "")
            for part in content
            if isinstance(part, dict) and part.get("type") == "text"
        )
    return content


def prompt_text(record: dict) -> str:
    return " ".join(message_text(record).split())[:100]


def command_name(record: dict):
    """Jméno ručně zadaného příkazu (`merge`), nebo None u běžného promptu."""
    found = COMMAND.search(message_text(record))
    return found.group(1) if found else None


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


def asked_questions(record: dict):
    """(id, otázky) pro každé volání `AskUserQuestion`, které záznam odpovědi nese."""
    content = (record.get("message") or {}).get("content")
    if record.get("type") != "assistant" or not isinstance(content, list):
        return
    for part in content:
        if (
            isinstance(part, dict)
            and part.get("type") == "tool_use"
            and part.get("name") == "AskUserQuestion"
        ):
            # Vadné volání, které harness odmítl, nese otázky v jiném tvaru – nic se jím nezeptalo.
            questions = (part.get("input") or {}).get("questions")
            if not isinstance(questions, list):
                questions = []
            yield (
                part.get("id"),
                [q.get("question", "") for q in questions if isinstance(q, dict)],
            )


def answered_questions(record: dict, asked: list) -> list:
    """Otázky, na které uživatel v dialogu odpověděl; zavřený dialog nerozhodl nic."""
    content = record["message"]["content"]
    if content[0].get("is_error"):
        return []
    answers = (record.get("toolUseResult") or {}).get("answers")
    return list(answers) if isinstance(answers, dict) else asked


def tool_result_id(record: dict):
    content = (record.get("message") or {}).get("content")
    if record.get("type") == "user" and isinstance(content, list) and content:
        first = content[0]
        if isinstance(first, dict) and first.get("type") == "tool_result":
            return first.get("tool_use_id")
    return None


def tool_calls(record: dict):
    """(id volání, id zprávy) pro každé volání nástroje v záznamu odpovědi."""
    message = record.get("message") or {}
    content = message.get("content")
    if record.get("type") != "assistant" or not isinstance(content, list):
        return
    for part in content:
        if isinstance(part, dict) and part.get("type") == "tool_use":
            yield part.get("id"), message.get("id")


def skill_calls(record: dict) -> list:
    """Jména skillů, které záznam odpovědi spouští nástrojem `Skill`."""
    content = (record.get("message") or {}).get("content")
    if record.get("type") != "assistant" or not isinstance(content, list):
        return []
    return [
        str((part.get("input") or {}).get("skill"))
        for part in content
        if isinstance(part, dict)
        and part.get("type") == "tool_use"
        and part.get("name") == "Skill"
        and (part.get("input") or {}).get("skill")
    ]


def is_rejection(record: dict) -> bool:
    first = record["message"]["content"][0]
    text = first.get("content")
    if isinstance(text, list):
        text = " ".join(p.get("text", "") for p in text if isinstance(p, dict))
    return bool(first.get("is_error")) and str(text).startswith(REJECTION)


def is_interrupt(record: dict, in_subagent: bool) -> bool:
    if record.get("type") != "user" or record.get("isSidechain") or in_subagent:
        return False
    content = (record.get("message") or {}).get("content")
    if isinstance(content, list):
        content = " ".join(
            p.get("text", "")
            for p in content
            if isinstance(p, dict) and p.get("type") == "text"
        )
    return isinstance(content, str) and content.strip() == INTERRUPT


def agreements(record: dict, in_subagent: bool) -> int:
    """Kolikrát Claude v záznamu odpovědi uživateli přitakal; subagent mluví k Claudovi, ne k němu."""
    content = (record.get("message") or {}).get("content")
    if (
        record.get("type") != "assistant"
        or in_subagent
        or not isinstance(content, list)
    ):
        return 0
    text = " ".join(
        p.get("text", "")
        for p in content
        if isinstance(p, dict) and p.get("type") == "text"
    )
    return len(AGREEMENT.findall(text))


class Session:
    """Stav jednoho transcriptu, ze kterého se pozná, jakého druhu je další záznam."""

    def __init__(self, in_subagent: bool):
        self.in_subagent = in_subagent
        self.running, self.asking, self.calls = {}, {}, {}
        self.rejected = set()
        # Skilly běžící v odpovědi na poslední prompt; ručně zadaný čeká na své první volání.
        self.turn, self.typed = [], None

    def remember(self, record: dict, at: datetime) -> None:
        for tool_id, limit in foreground_bash(record):
            self.running[tool_id] = at + timedelta(milliseconds=limit)
        self.calls.update(tool_calls(record))
        if not self.in_subagent and not record.get("isSidechain"):
            self.asking.update(asked_questions(record))

    def rejection(self, result_id) -> bool:
        # Zamítnuté volání odmítne i ostatní souběžná volání téže zprávy – zamítnutí je jedno.
        message = self.calls.pop(result_id, None)
        if message is not None and message in self.rejected:
            return False
        self.rejected.add(message)
        return True

    def classify(self, record: dict, result_id):
        """(druh, data) záznamu; viz `log_events`."""
        asked = self.asking.pop(result_id, None)
        if result_id is not None and is_rejection(record):
            return (
                ("rejection", None) if self.rejection(result_id) else ("claude", None)
            )
        self.calls.pop(result_id, None)
        if is_interrupt(record, self.in_subagent):
            return "interrupt", None
        if is_prompt(record, self.in_subagent):
            self.typed = command_name(record)
            self.turn = [self.typed] if self.typed else []
            return "prompt", prompt_text(record)
        if asked is not None:
            return "decision", answered_questions(record, asked)
        invoked = self.invoked(record)
        if invoked:
            return "skill", invoked
        return "claude", agreements(record, self.in_subagent) or None

    def invoked(self, record: dict) -> list:
        """(jméno, původ) pro každý skill, který záznam spouští; viz `log_events`."""
        found = []
        for name in skill_calls(record):
            if name == self.typed:
                # Ručně zadaný skill už spustil harness – Claude ho jen zavolal podruhé.
                self.typed = None
                continue
            nested = self.turn or self.in_subagent or record.get("isSidechain")
            found.append((name, "nested" if nested else "asked"))
            self.turn.append(name)
        return found


def log_events(log: Path, in_subagent: bool):
    """(okamžik, druh, data) pro každý záznam s časem v jednom transcriptu.

    Aktivitou je **každý** záznam s časem, nejen prompt a odpověď: příkaz harnessu,
    spuštěné hooky i shrnutí po návratu jsou doklad, že se v Claudovi něco dělo.
    K tomu umělá událost na konci povoleného běhu příkazu, jehož výsledek přišel
    později – tím se doba běhu započte a zbytek mezery zůstane pauzou.

    Druhy a jejich data:

    - `prompt` – zpráva od uživatele, data jsou začátek jejího textu,
    - `decision` – odpověď v dialogu `AskUserQuestion`, data jsou zodpovězené otázky,
    - `rejection` – zamítnuté volání nástroje nebo zavřený dialog, jedno na Claudovu zprávu,
    - `interrupt` – uživatel zastavil Clauda klávesou Esc,
    - `skill` – Claude spustil skill nástrojem `Skill`; data jsou dvojice (jméno, původ), kde
      původ `asked` je na pokyn slovy a `nested` uvnitř jiného skillu nebo subagenta,
    - `claude` – cokoliv jiného; data jsou počet přitakání „máš pravdu“, nebo None.
    """
    session = Session(in_subagent)
    for record in records(log):
        stamp = record.get("timestamp")
        if not stamp:
            continue
        at = moment(stamp)
        session.remember(record, at)
        result_id = tool_result_id(record)
        allowed_end = session.running.pop(result_id, None)
        if allowed_end is not None and allowed_end < at:
            yield allowed_end, "claude", None
        yield (at, *session.classify(record, result_id))


def session_events(prefixes=None, start=None, end=None):
    """(okamžik, druh, zdroj, data) ze všech transcriptů, volitelně omezené na projekty a období."""
    for at, kind, source, data, _ in tagged_events(prefixes, start, end):
        yield at, kind, source, data


def tagged_events(prefixes=None, start=None, end=None):
    """Totéž jako `session_events`, navíc id session – u subagenta té, která ho pustila."""
    for project in project_dirs(prefixes):
        for log in project.rglob("*.jsonl"):
            in_subagent = "subagents" in log.parts
            # Subagent leží v `<projekt>/<id session>/subagents/…`, agent workflow o dvě úrovně hlouběji.
            session = log.relative_to(project).parts[0] if in_subagent else log.stem
            for at, kind, text in log_events(log, in_subagent):
                if (start is None or start <= at) and (end is None or at < end):
                    yield at, kind, project.name, text, session


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
