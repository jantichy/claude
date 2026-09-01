#!/usr/bin/env bash
# Zelená linka – Stop hook, který nepustí Clauda ukončit tah nad rozbitým projektem.
#
# Čte "Kontrakt příkazů" z projektového CLAUDE.md (sekce "## Příkazy") a spustí
# typecheck, lint a test. Když něco selže, vrátí exit 2 a text jde Claudovi zpátky
# jako pokyn, co dodělat.
#
# Definice viz ~/Dev/context/coding/coding.md, "Ověřování a brány kvality".
#
# Vypíná se v projektu souborem .claude/no-green-line nebo proměnnou
# CLAUDE_NO_GREEN_LINE=1.

set -uo pipefail

INPUT=$(cat)
SESSION=$(printf '%s' "$INPUT" | jq -r '.session_id // "nosession"' 2>/dev/null || echo nosession)
CWD=$(printf '%s' "$INPUT" | jq -r '.cwd // empty' 2>/dev/null)
[ -n "$CWD" ] && cd "$CWD" 2>/dev/null

[ "${CLAUDE_NO_GREEN_LINE:-0}" = "1" ] && exit 0
[ -f .claude/no-green-line ] && exit 0

# Jen v gitovém pracovním stromu.
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0

# Kontrakt příkazů: sekce "## Příkazy" v projektovém CLAUDE.md.
# PROJ je adresář, ve kterém se příkazy spouštějí – tedy ten, kde leží nalezený
# CLAUDE.md. Ve worktree layoutu to je main/, ne kořen kontejneru: tam žádný
# package.json není a příkazy by padaly z úplně jiného důvodu, než skript hlásí.
CLAUDE_MD=""; PROJ=""
for c in "$PWD/CLAUDE.md" "$ROOT/CLAUDE.md" "$ROOT/main/CLAUDE.md"; do
  if [ -f "$c" ] && grep -q '^## Příkazy' "$c"; then
    CLAUDE_MD="$c"; PROJ=$(dirname "$c"); break
  fi
done
[ -z "$CLAUDE_MD" ] && exit 0   # projekt kontrakt nemá – není co spouštět

# Nic rozpracovaného → není co kontrolovat.
[ -z "$(git status --porcelain 2>/dev/null)" ] && exit 0

# Pojistka proti smyčce: po třech zablokováních pustíme dál s varováním.
STATE="${TMPDIR:-/tmp}/claude-green-line-$SESSION"
STAMP=$(git status --porcelain 2>/dev/null | shasum | cut -d' ' -f1)
COUNT=0
if [ -f "$STATE" ]; then
  read -r OLDSTAMP OLDCOUNT < "$STATE" 2>/dev/null || true
  [ "${OLDSTAMP:-}" = "$STAMP" ] && COUNT=${OLDCOUNT:-0}
fi
if [ "$COUNT" -ge 3 ]; then
  echo "Zelená linka: třikrát po sobě neprošla a stav se nemění – pouštím dál, vyřeš to s uživatelem." >&2
  rm -f "$STATE"
  exit 0
fi

# macOS nemá timeout(1); použij gtimeout, když je, jinak běž bez limitu.
# 90 s na příkaz: tři kroky se pak vejdou do timeoutu hooku v settings.json.
# Krok zelené linky, který trvá déle, do ní nepatří – běží po každém tahu.
if command -v timeout >/dev/null 2>&1; then TIMEOUT="timeout 90"
elif command -v gtimeout >/dev/null 2>&1; then TIMEOUT="gtimeout 90"
else TIMEOUT=""; fi

cmd_for() {
  sed -n '/^## Příkazy/,/^## /p' "$CLAUDE_MD" \
    | sed -n "s/^[-*][[:space:]]*$1:[[:space:]]\{1,\}//p" | head -1 | sed 's/[[:space:]]*$//'
}

FAILED=""
for step in typecheck lint test; do
  CMD=$(cmd_for "$step")
  [ -z "$CMD" ] && continue
  if ! OUT=$(cd "$PROJ" && $TIMEOUT bash -lc "$CMD" 2>&1); then
    FAILED="${FAILED}
--- ${step}: ${CMD} ---
$(printf '%s' "$OUT" | tail -40)"
  fi
done

if [ -n "$FAILED" ]; then
  printf '%s %s\n' "$STAMP" "$((COUNT + 1))" > "$STATE"
  {
    echo "Zelená linka není zelená – práci nelze uzavřít. Oprav to, nebo se zeptej uživatele."
    echo "Netvrď, že něco prošlo, bez výstupu příkazu (~/Dev/context/coding/coding.md, Ověřování a brány kvality)."
    echo "$FAILED"
  } >&2
  exit 2
fi

rm -f "$STATE"
exit 0
