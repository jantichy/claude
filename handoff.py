#!/usr/bin/env python3
"""UserPromptSubmit hook: řekne modelu, že session překročila práh délky.

Práh drží `skills/HANDOFF.md`, *Práh kontextu*, a dokud stál jen v textu,
nedodržel se: model velikost kontextu nevidí – ukazuje ji status line člověku –
a volání nepočítá, takže práh odhadoval z dojmu. Tenhle hook ho proto měří
z transcriptu session a při odeslání zprávy uživatelem vloží do kontextu
hlášku s naměřeným údajem.

**Každý práh se ohlásí jednou za session.** Pod prahem hook mlčí, takže
do kontextu nevkládá nic; nad ním se ozve právě jednou, jinak se z připomínky
stane šum. Co už zaznělo, drží stavový soubor pod `$HOME` (stejně jako
`verify.sh`). Kompaktace kontext zmenší a počítání začíná znovu: velikost
kontextu i počet volání se měří od poslední kompaktace a ohlášené prahy se
počítají zvlášť pro každý její úsek.

Hook nikdy nezastaví zprávu: jakákoliv chyba skončí potichu nulou, protože
nečitelný transcript nesmí zablokovat práci. Oba směry selhání – že mlčí nad
prahem a že se ozve pod ním nebo podruhé – testuje `tests/test_hooks.py`.
"""

import json
import os
import sys
from pathlib import Path

# Hodnoty musí sedět s tabulkou v `skills/HANDOFF.md`, *Práh kontextu*;
# hlídá to `tests/test_hooks.py`.
CONTEXT_OFFER = 300_000
CONTEXT_RECOMMEND = 400_000
CALLS_OFFER = 150

STATE_DIR = Path.home() / ".local" / "state" / "claude-handoff"

OFFER = (
    "Podle `~/.claude/skills/HANDOFF.md`, *Práh kontextu*, jednou nabídni "
    "`/cleanup` a pokračování v nové session – s tím, co by se zapsalo a kde "
    "by se navázalo. Rozhoduje uživatel."
)
RECOMMEND = (
    "Podle `~/.claude/skills/HANDOFF.md`, *Práh kontextu*, přerušení už "
    "nenabízej, ale doporuč rovnou: `/cleanup`, `/clear` a pokračování "
    "v nové session. Pokračování tady je volba uživatele, ne výchozí stav."
)


def measure(transcript):
    """Vrátí (kontext, volání, kompaktace) hlavní větve od poslední kompaktace."""
    context = calls = compactions = 0
    with open(transcript, encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if entry.get("isSidechain"):
                continue
            if entry.get("subtype") == "compact_boundary":
                compactions += 1
                context = calls = 0
                continue
            if entry.get("type") != "assistant":
                continue
            message = entry.get("message") or {}
            usage = message.get("usage") or {}
            total = sum(
                usage.get(k) or 0
                for k in (
                    "input_tokens",
                    "cache_read_input_tokens",
                    "cache_creation_input_tokens",
                )
            )
            if total:
                context = total
            for block in message.get("content") or []:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    calls += 1
    return context, calls, compactions


def crossed(context, calls):
    """Prahy, které session právě teď překračuje: (klíč, naměřený údaj)."""
    out = []
    if context >= CONTEXT_RECOMMEND:
        out.append(
            (
                "context-recommend",
                f"Kontext session je {context // 1000}k tokenů, "
                f"nad prahem {CONTEXT_RECOMMEND // 1000}k.",
            )
        )
    elif context >= CONTEXT_OFFER:
        out.append(
            (
                "context-offer",
                f"Kontext session je {context // 1000}k tokenů, "
                f"nad prahem {CONTEXT_OFFER // 1000}k.",
            )
        )
    if calls >= CALLS_OFFER:
        out.append(
            (
                "calls-offer",
                f"Session má {calls} volání nástrojů, nad prahem {CALLS_OFFER}.",
            )
        )
    return out


def main():
    data = json.load(sys.stdin)
    session = data.get("session_id")
    transcript = data.get("transcript_path")
    if not session or not transcript or not os.path.isfile(transcript):
        return
    context, calls, compactions = measure(transcript)
    hits = crossed(context, calls)
    if not hits:
        return

    state_file = STATE_DIR / f"{Path(session).name}.json"
    try:
        fired = set(json.loads(state_file.read_text(encoding="utf-8")))
    except (OSError, ValueError):
        fired = set()
    fresh = [(k, m) for k, m in hits if f"{k}@{compactions}" not in fired]
    # Doporučení nad 400k obsahuje i nabídku, takže nabídka po něm už nezazní.
    if any(k == "context-recommend" for k, _ in fresh):
        fired.add(f"context-offer@{compactions}")
    if not fresh:
        return
    keys = {k for k, _ in fresh}
    fired |= {f"{k}@{compactions}" for k in keys}
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(sorted(fired)), encoding="utf-8")

    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": " ".join(m for _, m in fresh)
                    + " "
                    + (RECOMMEND if "context-recommend" in keys else OFFER),
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
