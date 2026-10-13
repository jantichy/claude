#!/usr/bin/env python3
"""Stop a SessionStart hook: přenese pracovní adresář přes `/clear`.

Když se session uprostřed práce přesune do podadresáře – typicky do worktree
větve, kterou sama založila –, `/clear` ji vrátí do adresáře, ve kterém se
`claude` spustil. Nová session pak neví, že se pracovalo ve větvi, a status
line ukazuje kořen projektu. Hook sám adresář session změnit neumí, proto
nové session jen řekne, kde se pracovalo, a přepnutí nechá na modelu –
podmíněně, protože po `/clear` se často začíná úplně jiné téma.

- `Stop`: po každé odpovědi uloží `cwd` session pod klíč terminálové záložky.
  ID session se při `/clear` mění, záložka zůstává.
- `SessionStart` s `source: clear`: přečte uložený adresář, a liší-li se od
  toho, ve kterém nová session začala, vloží do kontextu pokyn k přepnutí.

Bez proměnné záložky (`ITERM_SESSION_ID`, `TERM_SESSION_ID`) hook mlčí: klíč
podle projektu by spojil dvě záložky nad týmž repozitářem a jedna by druhou
poslala do cizí větve. Jakákoliv chyba skončí potichu nulou. Oba směry –
že pokyn přijde a že nepřijde tam, kam nemá – testuje `tests/test_hooks.py`.
"""

import json
import os
import re
import shlex
import sys
from pathlib import Path

STATE_DIR = Path.home() / ".local" / "state" / "claude-workdir"


def tab_key():
    tab = os.environ.get("ITERM_SESSION_ID") or os.environ.get("TERM_SESSION_ID")
    return re.sub(r"[^A-Za-z0-9_-]", "_", tab) if tab else None


def instruction(saved, cwd):
    return (
        f"Před `/clear` se v téhle záložce terminálu pracovalo v adresáři "
        f"`{saved}`, nová session ale začala v `{cwd}`. Pokud z první zprávy "
        f"uživatele není zjevné, že začíná úplně jiné téma, které s prací "
        f"v `{saved}` nesouvisí, přepni se tam (`cd {shlex.quote(saved)}`) dřív, než začneš "
        f"cokoliv dělat, a pracuj dál tam. Je-li to zjevné, zůstaň v `{cwd}`."
    )


def main():
    data = json.load(sys.stdin)
    key = tab_key()
    cwd = data.get("cwd")
    if not key or not cwd:
        return
    state_file = STATE_DIR / f"{key}.json"
    event = data.get("hook_event_name")

    if event == "Stop":
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        state_file.write_text(json.dumps({"cwd": cwd}), encoding="utf-8")
        return

    if event != "SessionStart" or data.get("source") != "clear":
        return
    saved = json.loads(state_file.read_text(encoding="utf-8")).get("cwd")
    if not saved or saved == cwd or not os.path.isdir(saved):
        return
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": instruction(saved, cwd),
                }
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
