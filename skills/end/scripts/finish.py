#!/usr/bin/env python3
"""Ověří úklid session před commitem jedním voláním.

Tři kontroly naráz:

- **evidence promptů** – každý prompt, který transcript nese **teď** (i odpovědi
  z dialogů úklidu samotného), má v `<scratchpad>/end-states.txt` právě jeden
  konečný stav. Bez toho by se pokrytí zase jen tvrdilo;
- **odkazy** – `links.py` nad Markdowny změněnými od základu session,
  bez smazaných souborů;
- **pořadí** – `order.py` nad změněnými `done.md` a `decisions.md`.

Tvar `end-states.txt`, řádek na prompt nebo souvislý úsek promptů:

    1-4 bez zápisu
    5 zapsáno docs/decisions.md
    6 přebito

Použití: finish.py <scratchpad>   (spouští se v kořeni uklízeného projektu)
Návratový kód: 0 čisto, 1 nálezy, 2 chyba volání.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path("~/.claude/skills/end/scripts").expanduser()))
import extract  # noqa: E402

SHARED = Path("~/.claude/skills").expanduser()
LINE = re.compile(r"^(\d+)(?:-(\d+))?\s+(zapsáno\s+\S.*|přebito|bez zápisu)\s*$")


def states(path, total):
    """Vrátí (pokryté číslo → stav, chyby tvaru)."""
    covered, errors = {}, []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        match = LINE.match(raw.strip())
        if not match:
            errors.append(f"neplatný řádek: {raw!r}")
            continue
        first, last = int(match[1]), int(match[2] or match[1])
        for number in range(first, last + 1):
            if number in covered:
                errors.append(f"prompt {number} má dva stavy")
            if number > total:
                errors.append(f"prompt {number} neexistuje, promptů je {total}")
            covered[number] = match[3]
    return covered, errors


def check_ledger(scratchpad, state):
    found = extract.prompts(extract.load(state["transcript"]))
    path = scratchpad / "end-states.txt"
    if not path.exists():
        return [f"chybí {path}"], len(found)
    covered, errors = states(path, len(found))
    for index, (_, text) in enumerate(found, 1):
        if index not in covered:
            errors.append(f"prompt {index} bez stavu: {' '.join(text.split())[:80]}")
    return errors, len(found)


def git_lines(*args):
    done = subprocess.run(["git", *args], capture_output=True, text=True)
    return done.stdout.splitlines() if done.returncode == 0 else []


def changed(base):
    """Soubory změněné od základu session – commity, index, strom i nové."""
    names = set(git_lines("diff", "--name-only", "HEAD"))
    if base:
        names |= set(git_lines("diff", "--name-only", f"{base}..HEAD"))
    for line in git_lines("status", "--porcelain", "--untracked-files=all"):
        names.add(line[3:].split(" -> ")[-1])
    return sorted(n for n in names if Path(n).is_file())


def run(script, files):
    """Pustí sdílenou kontrolu; vrátí výstup jen při nálezu."""
    if not files:
        return None
    done = subprocess.run(
        [sys.executable, str(SHARED / script), *files], capture_output=True, text=True
    )
    return None if done.returncode == 0 else (done.stdout + done.stderr).strip()


def main(argv):
    if len(argv) != 1:
        print("Použití: finish.py <scratchpad>", file=sys.stderr)
        return 2
    scratchpad = Path(argv[0])
    try:
        state = json.loads((scratchpad / "end-state.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        print("chybí end-state.json – nejdřív pusť prepare.py", file=sys.stderr)
        return 2
    errors, total = check_ledger(scratchpad, state)
    files = changed(state.get("base"))
    findings = [f"EVIDENCE: {e}" for e in errors]
    for script, selected in (
        ("links.py", [f for f in files if f.endswith(".md")]),
        ("order.py", [f for f in files if Path(f).name in ("done.md", "decisions.md")]),
    ):
        out = run(script, selected)
        if out:
            findings.append(f"{script}:\n{out}")
    if findings:
        print("\n".join(findings))
        return 1
    print(f"Čisto – prompty {total}/{total}, odkazy a pořadí v pořádku.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
