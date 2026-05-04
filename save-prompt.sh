#!/bin/bash
# Sdílený UserPromptSubmit hook pro skill /autoprompt.
# Aktivuje se v projektech, které mají /autoprompt zapnutý — přidává každý
# uživatelský prompt na konec PROMPTS.md v rootu projektu.
set -euo pipefail

# Project root z env (nastaveno Claude Code pro hooky)
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-}"
[ -z "$PROJECT_DIR" ] && exit 0

PROMPTS_FILE="$PROJECT_DIR/PROMPTS.md"
[ -f "$PROMPTS_FILE" ] || exit 0

INPUT=$(cat)
PROMPT=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('prompt', ''))
except Exception:
    pass
" 2>/dev/null || echo "")

[ -z "$PROMPT" ] && exit 0

# Najdi poslední číslo a inkrementuj
LAST_NUM=$(grep -E '^\*\*[0-9]+\.\*\*$' "$PROMPTS_FILE" | tail -1 | grep -oE '[0-9]+' || echo "0")
NEXT_NUM=$((LAST_NUM + 1))

printf '\n---\n\n**%s.**\n%s\n' "$NEXT_NUM" "$PROMPT" >> "$PROMPTS_FILE"
