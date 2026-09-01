#!/usr/bin/env bash
# Zelená linka – Stop hook, který nepustí Clauda ukončit tah nad rozbitým projektem.
#
# Čte "Kontrakt příkazů" z projektového CLAUDE.md (sekce "## Příkazy") a spustí
# typecheck, lint a test. Když něco selže, vrátí exit 2 a text jde Claudovi zpátky
# jako pokyn, co dodělat.
#
# Definice viz ~/Dev/context/coding/coding.md, "Ověřování a brány kvality".
#
# Vypíná se souborem .claude/no-green-line (v adresáři projektu nebo v cwd)
# nebo proměnnou CLAUDE_NO_GREEN_LINE=1.

set -uo pipefail

LIMIT=60          # strop na jeden krok; 3 × 60 s + režie se vejde do timeoutu hooku (320 s)
MAX_FAILS=3       # po kolika marných pokusech nad týmž stavem pustit dál

INPUT=$(cat)
if command -v jq >/dev/null 2>&1; then
  SESSION=$(printf '%s' "$INPUT" | jq -r '.session_id // "nosession"' 2>/dev/null || echo nosession)
  CWD=$(printf '%s' "$INPUT" | jq -r '.cwd // empty' 2>/dev/null)
else
  # Bez jq neumíme přečíst cwd ani session – radši nahlas nic nedělat, než dělat naslepo.
  echo "Zelená linka: chybí jq, hook neběží. Doinstaluj ho (brew install jq)." >&2
  exit 1
fi
[ -n "$CWD" ] && cd "$CWD" 2>/dev/null

[ "${CLAUDE_NO_GREEN_LINE:-0}" = "1" ] && exit 0

# Kontrakt příkazů: sekce "## Příkazy" v projektovém CLAUDE.md.
# PROJ je adresář, ve kterém se příkazy spouštějí – tedy ten, kde leží nalezený
# CLAUDE.md. Ve worktree layoutu (~/Dev/context/worktree/worktree.md) stojí session
# často v kořeni kontejneru, který sám pracovní strom NENÍ – git tam selže a
# package.json tam nikdy neleží. Proto se hledá i v main/ a git operace pak běží
# v PROJ, ne tam, kde je cwd.
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || true)

CLAUDE_MD=""; PROJ=""
for c in "$PWD/CLAUDE.md" "$PWD/main/CLAUDE.md" "${ROOT:-/nonexistent}/CLAUDE.md" "${ROOT:-/nonexistent}/main/CLAUDE.md"; do
  if [ -f "$c" ] && grep -q '^## Příkazy' "$c"; then
    CLAUDE_MD="$c"; PROJ=$(dirname "$c"); break
  fi
done
[ -z "$CLAUDE_MD" ] && exit 0   # projekt kontrakt nemá – není co spouštět

# Vypínač se hledá až teď, protože až teď víme, kde projekt je.
[ -f "$PROJ/.claude/no-green-line" ] && exit 0
[ -f "$PWD/.claude/no-green-line" ] && exit 0

# Bez pracovního stromu se nedá zjistit, co se změnilo – a pak není co kontrolovat.
git -C "$PROJ" rev-parse --show-toplevel >/dev/null 2>&1 || exit 0

# --- Otisk stavu ---------------------------------------------------------------
# Bere HEAD i rozpracované změny. Commitnutá práce tedy otisk mění stejně jako
# necommitnutá: v projektu se zapnutým autocommitem je strom na konci tahu čistý
# a podmínka "jsou tu rozpracované změny" by bránu tiše vypnula.
sig() {
  local head dirty
  head=$(git -C "$PROJ" rev-parse HEAD 2>/dev/null || echo nohead)
  dirty=$(git -C "$PROJ" status --porcelain 2>/dev/null)
  if command -v shasum >/dev/null 2>&1; then
    printf '%s\n%s' "$head" "$dirty" | shasum | cut -d' ' -f1
  elif command -v cksum >/dev/null 2>&1; then
    printf '%s\n%s' "$head" "$dirty" | cksum | tr -d ' '
  else
    printf '%s-%s' "$head" "$(printf '%s' "$dirty" | wc -c | tr -d ' ')"
  fi
}
SIG=$(sig)

# Stav patří mimo repozitář – ~/.claude je git a stavové soubory by se commitovaly.
STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/claude-green-line"
mkdir -p "$STATE_DIR" 2>/dev/null || true
chmod 700 "$STATE_DIR" 2>/dev/null || true
# Jméno stavu odvozené ze session i z cesty projektu, ať stav nepřeteče mezi projekty.
SESSION_SAFE=$(printf '%s' "$SESSION" | tr -cd 'A-Za-z0-9._-'); [ -n "$SESSION_SAFE" ] || SESSION_SAFE=nosession
PROJ_KEY=$(printf '%s' "$PROJ" | tr -cd 'A-Za-z0-9' | tail -c 40)
STATE="$STATE_DIR/$SESSION_SAFE-$PROJ_KEY"

# Úklid: stavy starší než čtyři hodiny nemají co říct k dnešnímu běhu.
find "$STATE_DIR" -type f -mmin +240 -delete 2>/dev/null || true

OK_SIG=""; FAIL_SIG=""; FAILS=0
if [ -f "$STATE" ]; then
  read -r OK_SIG FAIL_SIG FAILS < "$STATE" 2>/dev/null || true
  case "${FAILS:-}" in ''|*[!0-9]*) FAILS=0;; esac
fi

# Tenhle stav už jednou prošel – nic se od té doby nezměnilo, není co spouštět.
[ -n "${OK_SIG:-}" ] && [ "$OK_SIG" = "$SIG" ] && exit 0

save() { printf '%s %s %s\n' "${1:--}" "${2:--}" "${3:-0}" > "$STATE" 2>/dev/null || true; }

# --- Čtení kontraktu -----------------------------------------------------------
cmd_for() {
  sed -n '/^## Příkazy/,/^## /p' "$CLAUDE_MD" \
    | sed -n "s/^[[:space:]]*[-*][[:space:]]*\**$1\**:[[:space:]]\{1,\}//p" | head -1 | sed 's/[[:space:]]*$//'
}

# --- Spuštění se stropem -------------------------------------------------------
# timeout(1) na macOS chybí a gtimeout z coreutils nemusí být nainstalovaný, takže
# strop si hlídáme sami. Bez něj by zaseknutý watch-mode runner držel hook až do
# jeho vlastního timeoutu a výsledek kontroly by se zahodil.
LAST_OUT=""
run_limited() {
  local cmd="$1" out rc pid waited=0
  out=$(mktemp "${TMPDIR:-/tmp}/green-line.XXXXXX")
  ( cd "$PROJ" && bash -c "$cmd" ) >"$out" 2>&1 &
  pid=$!
  while kill -0 "$pid" 2>/dev/null; do
    if [ "$waited" -ge "$LIMIT" ]; then
      kill -TERM "$pid" 2>/dev/null; sleep 2; kill -KILL "$pid" 2>/dev/null
      echo "(krok byl ukončen po ${LIMIT} s – do zelené linky patří jen to, co doběhne rychle)" >> "$out"
      break
    fi
    sleep 1; waited=$((waited + 1))
  done
  wait "$pid" 2>/dev/null; rc=$?
  LAST_OUT=$(cat "$out"); rm -f "$out"
  return $rc
}

FAILED=""; SKIPPED=""
for step in typecheck lint test; do
  CMD=$(cmd_for "$step")
  if [ -z "$CMD" ]; then SKIPPED="${SKIPPED:+$SKIPPED, }$step"; continue; fi
  if ! run_limited "$CMD"; then
    BODY=$(printf '%s' "$LAST_OUT" | tail -40)
    LINES=$(printf '%s' "$LAST_OUT" | wc -l | tr -d ' ')
    if [ "$LINES" -gt 40 ]; then BODY="(ořezáno, celkem $LINES řádků)
$BODY"; fi
    if [ -z "$LAST_OUT" ]; then BODY="(příkaz skončil chybou bez výstupu)"; fi
    FAILED="${FAILED}
--- ${step}: ${CMD} ---
${BODY}"
  fi
done

if [ -n "$FAILED" ]; then
  if [ "${FAIL_SIG:-}" = "$SIG" ]; then FAILS=$((FAILS + 1)); else FAILS=1; fi
  if [ "$FAILS" -ge "$MAX_FAILS" ]; then
    # Exit 1 schválně: při exit 0 by tuhle hlášku neviděl nikdo, ani model, ani člověk.
    save "-" "-" 0
    {
      echo "Zelená linka: ${MAX_FAILS}× po sobě neprošla a stav se nemění – pouštím dál."
      echo "Vyřeš to s uživatelem, nebo bránu vypni souborem .claude/no-green-line."
      echo "$FAILED"
    } >&2
    exit 1
  fi
  save "${OK_SIG:--}" "$SIG" "$FAILS"
  {
    echo "Zelená linka není zelená – práci nelze uzavřít. Oprav to, nebo se zeptej uživatele."
    echo "Netvrď, že něco prošlo, bez výstupu příkazu (~/Dev/context/coding/coding.md, Ověřování a brány kvality)."
    if [ -n "$SKIPPED" ]; then echo "Nekontrolovalo se: $SKIPPED (chybí v kontraktu příkazů)."; fi
    echo "$FAILED"
  } >&2
  exit 2
fi

save "$SIG" "-" 0

# Prošlo, ale ne všechno – to se musí říct, jinak vzniká dojem plné kontroly.
if [ -n "$SKIPPED" ]; then
  echo "Zelená linka prošla, ale nekontrolovalo se: $SKIPPED (chybí v kontraktu příkazů v $CLAUDE_MD)." >&2
  exit 1
fi
exit 0
