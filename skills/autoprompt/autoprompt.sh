#!/bin/bash
# Sdílený UserPromptSubmit hook pro skill /autoprompt.
# Aktivuje se v projektech, které mají /autoprompt zapnutý – přidává každý
# uživatelský prompt na konec docs/prompts.md v projektu.
set -euo pipefail

# Project root z env (nastaveno Claude Code pro hooky)
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-}"
[ -z "$PROJECT_DIR" ] && exit 0

# Worktree layout (viz ~/Dev/context/worktree/worktree.md): kořen kontejneru není pracovní
# strom, takže cokoli v něm by nešlo commitnout. Log patří do worktree hlavní větve.
TARGET_DIR="$PROJECT_DIR"
if [ -d "$PROJECT_DIR/.bare" ]; then
    MAIN_BRANCH=$(git --git-dir="$PROJECT_DIR/.bare" symbolic-ref --short HEAD 2>/dev/null || true)
    if [ -n "$MAIN_BRANCH" ]; then
        MAIN_WT=$(git --git-dir="$PROJECT_DIR/.bare" worktree list --porcelain 2>/dev/null \
            | awk -v b="refs/heads/$MAIN_BRANCH" '/^worktree /{w=substr($0,10)} /^branch /{if ($2==b) {print w; exit}}')
        [ -n "$MAIN_WT" ] && [ -d "$MAIN_WT" ] && TARGET_DIR="$MAIN_WT"
    fi
fi

# Umístění standardních souborů má dva režimy (viz structure.md, Dva režimy
# umístění). Existující log vždycky vyhrává, ať se nerozdvojí; jinak se režim
# pozná podle toho, kde leží todo.md / decisions.md.
if [ -f "$TARGET_DIR/docs/prompts.md" ]; then
    PROMPTS_FILE="$TARGET_DIR/docs/prompts.md"
elif [ -f "$TARGET_DIR/prompts.md" ]; then
    PROMPTS_FILE="$TARGET_DIR/prompts.md"
elif [ -f "$TARGET_DIR/todo.md" ] || [ -f "$TARGET_DIR/decisions.md" ]; then
    PROMPTS_FILE="$TARGET_DIR/prompts.md"
else
    PROMPTS_FILE="$TARGET_DIR/docs/prompts.md"
fi
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
