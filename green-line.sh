#!/usr/bin/env bash
# Zelená linka – Stop hook, který nepustí Clauda ukončit tah nad rozbitým projektem.
#
# Přečte "Kontrakt příkazů" (sekce "## Příkazy" v projektovém CLAUDE.md) a spustí
# typecheck, lint a test. Když něco selže, vrátí exit 2 a výstup jde Claudovi jako
# pokyn, co dodělat. Definice viz ~/Dev/context/coding/coding.md, "Ověřování a brány
# kvality".
#
# BEZPEČNOST: kontrakt je kód ležící v repozitáři a hooky běží mimo permission
# systém. Proto se v projektu nespustí nic, dokud pro něj člověk jednou nevydá
# souhlas:  green-line.sh --allow <projekt>
# Ten souhlas znamená "spouštěj v tomhle repozitáři jeho vlastní příkazy", ne
# "ty konkrétní příkazy jsem přečetl a jsou neškodné" – `npm test` spustí, co je
# v package.json, a to se neschvaluje. Do cizího repozitáře souhlas nedávej.
#
# Vypnout: .claude/no-green-line v projektu, nebo CLAUDE_NO_GREEN_LINE=1.

set -uo pipefail

LIMIT=60      # strop na krok; tři kroky se vejdou do timeoutu hooku v settings.json
MAX_OUT=200000  # kolik bajtů výstupu si od kroku vezmeme

# Souhlasy leží mimo dosah XDG_STATE_HOME schválně: je to bezpečnostní stav a
# proměnná prostředí se dá nastavit z .envrc nebo z konfigurace editoru.
ALLOW_DIR="$HOME/.local/state/claude-green-line/allowed"
RUN_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/claude-green-line/runs"

die() { echo "Zelená linka: $1" >&2; exit 1; }
have() { command -v "$1" >/dev/null 2>&1; }
sha()  { shasum | cut -d' ' -f1; }   # dostupnost se ověřuje v need_tools

need_tools() {
  for t in jq git sed shasum mktemp gtimeout; do have "$t" || die "chybí $t, hook neběží."; done
}

# Klíč projektu je hash CELÉ cesty. Dřívější "posledních 40 alfanumerických znaků"
# kolidovalo: /a/con-text a /a/context daly týž klíč, a tím i týž souhlas.
proj_key() { printf '%s' "$1" | sha; }

# --- Vydání souhlasu -----------------------------------------------------------
if [ "${1:-}" = "--allow" ]; then
  need_tools
  P=$(cd "${2:-$PWD}" 2>/dev/null && pwd) || die "neznámá cesta: ${2:-$PWD}"
  MD=""
  for c in "$P/CLAUDE.md" "$P/main/CLAUDE.md"; do
    [ -f "$c" ] && grep -q '^## Příkazy' "$c" && { MD="$c"; P=$(dirname "$c"); break; }
  done
  [ -n "$MD" ] || die "v ${2:-$PWD} není CLAUDE.md se sekcí ## Příkazy."
  mkdir -p "$ALLOW_DIR" 2>/dev/null || die "nelze založit $ALLOW_DIR"
  chmod 700 "$(dirname "$ALLOW_DIR")" "$ALLOW_DIR" 2>/dev/null || true
  printf '%s\n' "$P" > "$ALLOW_DIR/$(proj_key "$P")" || die "nelze zapsat souhlas do $ALLOW_DIR"
  [ -s "$ALLOW_DIR/$(proj_key "$P")" ] || die "souhlas se nezapsal."
  SEC=$(sed -n '/^## Příkazy/,/^## /p' "$MD")
  echo "Zelená linka poběží v $P, podle kontraktu v $MD."
  echo
  echo "Po každém tahu spustí:"
  FOUND=""
  for k in typecheck lint test; do
    v=$(printf '%s\n' "$SEC" | sed -n "s/^[[:space:]]*[-*][[:space:]]*$k:[[:space:]]\{1,\}//p" | head -1 | sed 's/[[:space:]]*$//')
    [ -n "$v" ] && { printf '  %-10s %s\n' "$k:" "$v"; FOUND="$v"; }
  done
  [ -z "$FOUND" ] && echo "  (nic – kontrakt nemá typecheck, lint ani test, hook tu nic nespustí)"
  # Ostatní klíče jsou dokumentace pro člověka; zelená linka je nepouští.
  OTHER=$(printf '%s\n' "$SEC" | sed -n 's/^[[:space:]]*[-*][[:space:]]*\([a-zA-Z][a-zA-Z0-9:_-]*\):[[:space:]].*/\1/p' \
          | grep -vxE 'typecheck|lint|test' | paste -sd, - | sed 's/,/, /g')
  [ -n "$OTHER" ] && echo "  Nespouští: $OTHER (jen dokumentace v kontraktu)"
  echo
  echo "Souhlas platí pro REPOZITÁŘ, ne pro ty konkrétní řádky:"
  echo "co ty příkazy udělají, určuje package.json, Makefile nebo konfigurace v tomhle repu"
  echo "a to se neschvaluje. Do cizího naklonovaného repozitáře souhlas nedávej."
  exit 0
fi

# --- Vstup ---------------------------------------------------------------------
INPUT=$(cat)
have jq || die "chybí jq, hook neběží."
CWD=$(printf '%s' "$INPUT" | jq -r '.cwd // empty' 2>/dev/null)
SESSION=$(printf '%s' "$INPUT" | jq -r '.session_id // "nosession"' 2>/dev/null | tr -cd 'A-Za-z0-9._-')
[ -n "$SESSION" ] || SESSION=nosession
# Když cwd neexistuje, nepokračovat "někde jinde" – našel by se cizí projekt.
if [ -n "$CWD" ]; then cd "$CWD" 2>/dev/null || die "adresář $CWD neexistuje."; fi

[ "${CLAUDE_NO_GREEN_LINE:-0}" = "1" ] && exit 0

# --- Kde je projekt ------------------------------------------------------------
# Ve worktree layoutu stojí session často v kořeni kontejneru, který sám pracovní
# strom není – proto se hledá i v main/ a příkazy pak běží tam, ne v cwd.
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || true)
CLAUDE_MD=""; PROJ=""
for c in "$PWD/CLAUDE.md" "$PWD/main/CLAUDE.md" "${ROOT:-/nonexistent}/CLAUDE.md" "${ROOT:-/nonexistent}/main/CLAUDE.md"; do
  if [ -f "$c" ] && grep -q '^## Příkazy' "$c" 2>/dev/null; then CLAUDE_MD="$c"; PROJ=$(dirname "$c"); break; fi
done
[ -z "$CLAUDE_MD" ] && exit 0   # projekt kontrakt nemá – není co spouštět

[ -f "$PROJ/.claude/no-green-line" ] && exit 0
[ -f "$PWD/.claude/no-green-line" ] && exit 0

need_tools
[ -d "$ALLOW_DIR" ] && [ ! -O "$ALLOW_DIR" ] && die "$ALLOW_DIR nepatří tobě, nespouštím nic."

KEY=$(proj_key "$PROJ")
if [ ! -f "$ALLOW_DIR/$KEY" ]; then
  {
    echo "Zelená linka: pro $PROJ není vydaný souhlas, nespustil jsem nic."
    echo "Kontrakt je kód z repozitáře. Projdi si ho a jestli tomu repozitáři věříš:"
    echo "  ~/.claude/green-line.sh --allow $PROJ"
    sed -n '/^## Příkazy/,/^## /p' "$CLAUDE_MD" \
      | sed -n 's/^[[:space:]]*[-*][[:space:]]*\([a-zA-Z][a-zA-Z0-9:_-]*\):[[:space:]]\{1,\}/  \1: /p' || true
  } >&2
  exit 1
fi

# Rozlišit "není to repozitář" (v pořádku, mlčky ven) od "git nefunguje" (nahlas):
# rozbitý git by jinak bránu tiše vypnul a nikdo by se to nedozvěděl.
git --version >/dev/null 2>&1 || die "git nefunguje, hook neběží."
git -C "$PROJ" rev-parse --show-toplevel >/dev/null 2>&1 || exit 0   # není to repozitář

# --- Kontrakt: přečíst JEDNOU -------------------------------------------------
# Dřív se soubor četl znovu pro každý krok, takže mezi kontrolou a spuštěním bylo
# okno, ve kterém šel obsah vyměnit.
SECTION=$(sed -n '/^## Příkazy/,/^## /p' "$CLAUDE_MD")
[ -n "$SECTION" ] || die "sekci ## Příkazy se nepodařilo přečíst z $CLAUDE_MD."
cmd_for() {
  printf '%s\n' "$SECTION" | sed -n "s/^[[:space:]]*[-*][[:space:]]*$1:[[:space:]]\{1,\}//p" \
    | head -1 | sed 's/[[:space:]]*$//'
}

# --- Otisk stavu ---------------------------------------------------------------
# HEAD i rozpracované změny: v projektu se zapnutým autocommitem je strom na konci
# tahu čistý, takže "jsou tu rozpracované změny" by bránu tiše vypnulo.
SIG=$(printf '%s\n%s' "$(git -C "$PROJ" rev-parse HEAD 2>/dev/null || echo nohead)" \
                      "$(git -C "$PROJ" status --porcelain 2>/dev/null)" | sha)

mkdir -p "$RUN_DIR" 2>/dev/null || die "nelze založit $RUN_DIR"
STATE="$RUN_DIR/$SESSION-$KEY"
find "$RUN_DIR" -maxdepth 1 -type f -mmin +240 -delete 2>/dev/null || true
: > "$STATE.test" 2>/dev/null || die "do $RUN_DIR nejde zapsat, hook by běžel bez pojistky."
rm -f "$STATE.test"

OK_SIG=""; SKIP_SIG=""
[ -f "$STATE" ] && read -r OK_SIG SKIP_SIG < "$STATE" 2>/dev/null || true
[ "${OK_SIG:-}" = "$SIG" ] && exit 0     # tenhle stav už prošel
[ "${SKIP_SIG:-}" = "$SIG" ] && exit 0   # nad tímhle stavem jsme se už vzdali

# Pojistka proti smyčce: Claude Code posílá stop_hook_active, když tah pokračuje
# kvůli předchozímu zablokování. Vlastní počítadlo tohle nikdy netrefilo, protože
# otisk stavu se mění každou editací.
STOP_ACTIVE=$(printf '%s' "$INPUT" | jq -r '.stop_hook_active // false' 2>/dev/null)

# --- Spuštění kroků ------------------------------------------------------------
TMP=$(mktemp "${TMPDIR:-/tmp}/green-line.XXXXXX") || die "nelze založit dočasný soubor."
trap 'rm -f "$TMP"' EXIT INT TERM

run() {
  # gtimeout bez --foreground schválně: pak běží krok ve vlastní procesní skupině
  # a signál dostane celá, takže po zabitém kroku nezůstanou viset vnukové
  # (npm → node → vitest). S --foreground přežijí a drží otevřenou rouru.
  # head -c drží výstup v mezích – smyčkující příkaz jinak zaplní disk.
  ( cd "$PROJ" && gtimeout --kill-after=5 "$LIMIT" bash -c "$1" 2>&1 ) \
    | head -c "$MAX_OUT" > "$TMP"
  return "${PIPESTATUS[0]}"
}

FAILED=""; SKIPPED=""
for step in typecheck lint test; do
  CMD=$(cmd_for "$step")
  [ -z "$CMD" ] && { SKIPPED="${SKIPPED:+$SKIPPED, }$step"; continue; }
  run "$CMD"; RC=$?
  if [ "$RC" -ne 0 ]; then
    # RC se bere hned po volání: uvnitř `if ! run …` by $? byl vždycky 0
    # a diagnostika timeoutu by se nikdy nezobrazila.
    BODY=$(tail -40 "$TMP")
    N=$(wc -l < "$TMP" | tr -d ' ')
    [ "$N" -gt 40 ] && BODY="(zobrazeno posledních 40 ze $N řádků)
$BODY"
    [ ! -s "$TMP" ] && BODY="(příkaz skončil kódem $RC bez výstupu)"
    if [ "$RC" = "124" ] || [ "$RC" = "137" ]; then
      BODY="(krok nedoběhl do ${LIMIT} s a byl ukončen – do zelené linky patří jen to, co je rychlé)
$BODY"
    fi
    FAILED="${FAILED}
--- ${step}: ${CMD} ---
${BODY}"
  fi
done

note_skipped() { [ -n "$SKIPPED" ] && echo "Nekontrolovalo se: $SKIPPED (chybí v kontraktu příkazů)."; }

if [ -n "$FAILED" ]; then
  if [ "$STOP_ACTIVE" = "true" ]; then
    # Druhý pokus v řadě nad týmž problémem: dál už jen otravujeme.
    printf '%s %s\n' "${OK_SIG:--}" "$SIG" > "$STATE" 2>/dev/null || true
    { echo "Zelená linka neprošla ani napodruhé – pouštím dál, vyřeš to s uživatelem."
      note_skipped; echo "$FAILED"; } >&2
    exit 1
  fi
  { echo "Zelená linka není zelená – práci nelze uzavřít. Oprav to, nebo se zeptej uživatele."
    echo "Netvrď, že něco prošlo, bez výstupu příkazu."
    note_skipped; echo "$FAILED"; } >&2
  exit 2
fi

printf '%s %s\n' "$SIG" "-" > "$STATE" 2>/dev/null || true
if [ -n "$SKIPPED" ]; then
  echo "Zelená linka prošla, ale nekontrolovalo se: $SKIPPED (chybí v kontraktu v $CLAUDE_MD)." >&2
  exit 1
fi
exit 0
