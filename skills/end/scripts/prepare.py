#!/usr/bin/env python3
"""Připraví úklid session jedním voláním.

Vrátí všechno, co `/end` potřebuje před prvním zápisem: id session a cestu
k jejímu transcriptu, základ session, větev a remote, necommitnuté soubory,
co se během session změnilo, signály rozdělané práce a inventuru transcriptu.
Očištěný transcript
uloží do scratchpadu jako `end-clean.txt` a stav pro `finish.py` jako
`end-state.json`.

Každé kolo mezi modelem a nástrojem stojí nad velkým kontextem končící
session sekundy, takže co jde zjistit skriptem, zjišťuje se tady naráz.

Použití: prepare.py <scratchpad>   (spouští se v kořeni uklízeného projektu)
Návratový kód: 0 hotovo, 2 chyba volání.
"""

import contextlib
import datetime
import io
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path("~/.claude/skills/end/scripts").expanduser()))
import extract  # noqa: E402

PROJECTS = Path("~/.claude/projects").expanduser()
RUN = Path(".claude/run")
TODOS = ("docs/todo.md", "todo.md", "CLAUDE.md")
DECIDED = "## Rozhodnuto k zapracování"
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"


def git(*args):
    """Výstup gitu, nebo None, když příkaz selže (třeba mimo repozitář)."""
    done = subprocess.run(["git", *args], capture_output=True, text=True)
    return done.stdout.strip() if done.returncode == 0 else None


def session_id(scratchpad):
    """Id je adresář nad `scratchpad` – jediný spolehlivý klíč (`session.md`)."""
    path = Path(scratchpad)
    return path.parent.name if path.name == "scratchpad" else None


def transcript(sid):
    found = sorted(PROJECTS.glob(f"*/{sid}.jsonl"))
    return found[0] if len(found) == 1 else None


def started(rows):
    """Čas prvního záznamu, který `timestamp` má – první řádek ho mít nemusí."""
    for _, record in rows:
        stamp = record.get("timestamp")
        if stamp:
            return datetime.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    return None


def base(start):
    """Commit, na kterém session stála, než cokoliv zapsala.

    Rodič nejstaršího commitu novějšího než začátek session; bez takového
    commitu `HEAD`; u prvního commitu repozitáře prázdný strom.
    """
    log = git("log", "--format=%H %ct")
    if log is None:
        return None
    newer = [
        h
        for h, t in (line.split() for line in log.splitlines())
        if int(t) > start.timestamp()
    ]
    if not newer:
        return git("rev-parse", "HEAD")
    return git("rev-parse", "--verify", "--quiet", f"{newer[-1]}^") or EMPTY_TREE


def report_git(start):
    if git("rev-parse", "--git-dir") is None:
        print("GIT: není to repozitář – odpadá základ session, commit i push")
        return None
    root = base(start)
    print(f"ZÁKLAD SESSION: {root}")
    print(f"VĚTEV: {git('branch', '--show-current') or '(odpojený HEAD)'}")
    print(f"REMOTE: {git('remote', 'get-url', 'origin') or 'žádný'}")
    dirty = git("status", "--porcelain") or ""
    print("NECOMMITNUTO:" + ("\n" + dirty if dirty else " nic"))
    changed = (
        git("log", "--name-only", "--format=%h", f"{root}..HEAD")
        if root != EMPTY_TREE
        else None
    )
    print("COMMITY SESSION:" + ("\n" + changed if changed else " žádné"))
    return root


def section(text, heading):
    """Tělo sekce od nadpisu po další `## `, bez prázdných řádků na okrajích."""
    lines = text.splitlines()
    if heading not in lines:
        return ""
    body = []
    for line in lines[lines.index(heading) + 1 :]:
        if line.startswith("## "):
            break
        body.append(line)
    return "\n".join(body).strip()


def run_files(start):
    """Běhové soubory změněné během session, které `interrupted` nenesou.

    Starší soubor patří běhu jiné session a klíč `interrupted` znamená, že
    přerušení už zapsané je (`~/.claude/skills/skills.md`, *Běhový stav*).
    Nečitelný soubor se hlásí, protože o něm nejde říct, že zapsaný je.
    """
    if not RUN.is_dir():
        return []
    out = []
    for path in sorted(p for p in RUN.iterdir() if p.is_file()):
        if path.stat().st_mtime < start.timestamp():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, UnicodeDecodeError):
            data = None
        if not (isinstance(data, dict) and "interrupted" in data):
            out.append(f"běhový soubor {path}")
    return out


def decided(root):
    """Neprázdná `## Rozhodnuto k zapracování`, do které session zapsala.

    Sekce, která stála beze změny už v základu session, je zapsaná fronta
    jiné session, ne rozdělaná práce téhle.
    """
    out = []
    for name in TODOS:
        path = Path(name)
        if not path.is_file():
            continue
        now = section(path.read_text(encoding="utf-8"), DECIDED)
        before = git("show", f"{root}:./{name}") if root else None
        if now and now != section(before or "", DECIDED):
            out.append(f"{name}: {DECIDED}")
    return out


def unfinished(start, root):
    """Mechanické signály, že session končí uprostřed rozdělané práce."""
    return run_files(start) + decided(root)


def main(argv):
    if len(argv) != 1:
        print("Použití: prepare.py <scratchpad>", file=sys.stderr)
        return 2
    scratchpad = Path(argv[0])
    sid = session_id(scratchpad)
    path = transcript(sid) if sid else None
    if not path:
        print(f"transcript session {sid!r} nenalezen pod {PROJECTS}", file=sys.stderr)
        return 2
    rows = extract.load(path)
    start = started(rows)
    if not rows or not start:
        print(f"{path}: žádné čitelné záznamy", file=sys.stderr)
        return 2
    print(f"SESSION: {sid}\nTRANSCRIPT: {path}\nZAČÁTEK: {start.isoformat()}")
    root = report_git(start)
    signals = unfinished(start, root)
    print("ROZDĚLANÁ PRÁCE:" + ("\n" + "\n".join(signals) if signals else " nic"))
    print(
        f"DONE.MD: {'ano' if Path('docs/done.md').exists() or Path('done.md').exists() else 'ne'}\n"
    )
    clean = io.StringIO()
    with contextlib.redirect_stdout(clean):
        extract.run_filter(rows)
    (scratchpad / "end-clean.txt").write_text(clean.getvalue(), encoding="utf-8")
    state = {"session": sid, "transcript": str(path), "base": root}
    (scratchpad / "end-state.json").write_text(json.dumps(state), encoding="utf-8")
    return extract.run_inventory(rows, path)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
