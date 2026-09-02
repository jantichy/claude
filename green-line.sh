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
# Vydané souhlasy vypíše  --list , odebere  --revoke <projekt> .
# Ten souhlas znamená "spouštěj v tomhle repozitáři jeho vlastní příkazy", ne
# "ty konkrétní příkazy jsem přečetl a jsou neškodné" – `npm test` spustí, co je
# v package.json, a to se neschvaluje. Do cizího repozitáře souhlas nedávej.
#
# Krok, který nejde spustit (chybí nástroj, exit 126/127), NENÍ červená linka:
# hlásí se zvlášť a tah neblokuje – jinak by Claude opravoval kód kvůli rozbitému
# prostředí. Je to jediná větev, která končí exit 1: u ní je mlčení k modelu
# správně, protože opravovat není co.
#
# Všechno ostatní, co se nepovedlo zkontrolovat, končí exit 2. Při exit 1 vidí
# stderr jen uživatel, kdežto shrnutí píše model – a ten by nad neprověřeným
# stavem nechal stát svoje "hotovo".
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

# Přítomnost != funkčnost. Nástroj může být na PATH a přitom nic neumět – typicky
# zástupný stub, který skončí nenulově a nevypíše nic. `command -v` takový stub
# najde, hook by ho použil, `jq` by vracelo prázdno a brána by se tiše vypnula.
# Proto se u parseru neověřuje existence, ale výsledek na známém vstupu.
probe_jq() { [ "$(printf '{"a":1}' | jq -r '.a' 2>/dev/null)" = "1" ]; }

# Na macOS je timeout z coreutils jako gtimeout, na Linuxu jako timeout. Bez
# fallbacku by hook na Linuxu po každém tahu zemřel na "chybí gtimeout" a brána
# by neběžela vůbec – tedy nejhorší možný způsob, jak zjistit, že něco chybí.
TIMEOUT_BIN=""
pick_timeout() {
  if have gtimeout; then TIMEOUT_BIN=gtimeout
  elif have timeout; then TIMEOUT_BIN=timeout
  fi
  [ -n "$TIMEOUT_BIN" ]
}

need_tools() {
  for t in jq git sed shasum mktemp; do have "$t" || die "chybí $t, hook neběží."; done
  pick_timeout || die "chybí gtimeout ani timeout (coreutils), hook neběží."
  probe_jq || die "jq je na PATH, ale nefunguje (nevrátilo očekávaný výstup) – hook neběží."
}

# Markdown bez bloků kódu. Ukázka formátu kontraktu v dokumentaci se jinak čte
# jako kontrakt – a coding.md takovou ukázku obsahuje, takže kdo si ji zkopíruje
# do svého CLAUDE.md, dostane po každém tahu běžící `npm test` a `npx stryker run`,
# aniž by kontrakt vůbec zaváděl. Je to zároveň cesta, kudy jde do repozitáře
# propašovat příkaz schovaný jako dokumentace.
md_body() { awk '/^[[:space:]]*(```|~~~)/ { f = !f; next } !f' "$1"; }

# Kanonická (fyzická) podoba cesty. Bez ní se souhlas vydaný pro cestu přes
# symlink nepotká s během hooku, který ji má rozřešenou – na macOS je takový
# /var -> /private/var, ale stačí i symlinkovaný adresář s projekty. Brána by pak
# mlčky neběžela a jediné, co by uživatel dostal, je hláška "není vydaný souhlas".
canon() { (cd "$1" 2>/dev/null && pwd -P) || printf '%s' "$1"; }

# Klíč je hash CELÉHO řetězce. Dřívější "posledních 40 alfanumerických znaků"
# kolidovalo: /a/con-text a /a/context daly týž klíč, a tím i týž souhlas.
proj_key() { printf '%s' "$1" | sha; }

# Identita REPOZITÁŘE, ne pracovního adresáře. Ve worktree layoutu má každá větev
# vlastní adresář, takže klíč z cesty znamenal nový souhlas na každé nové větvi –
# tedy vypnutou bránu právě tam, kde se pracuje, a funkční na main, kde se
# nepracuje. Sdílený .git je pro všechny worktree téhož repozitáře týž, takže
# souhlas konečně platí pro repozitář, jak celou dobu slibuje.
# Mimo git repozitář se vrací zadaná cesta, aby se chování nezměnilo.
repo_id() {
  d=$(git -C "$1" rev-parse --git-common-dir 2>/dev/null) || { canon "$1"; return; }
  case "$d" in /*) ;; *) d="$1/$d" ;; esac
  canon "$d"
}

# Soubor se souhlasem pro daný pracovní adresář, existuje-li. Souhlasy vydané
# před přechodem na klíč podle repozitáře se při prvním použití přeznačí – bez
# migrace by se změnou klíče brána ze dne na den vypnula ve všech projektech.
allow_file() {
  k=$(proj_key "$(repo_id "$1")")
  if [ -f "$ALLOW_DIR/$k" ]; then printf '%s' "$ALLOW_DIR/$k"; return 0; fi
  old=$(proj_key "$1")
  if [ -f "$ALLOW_DIR/$old" ] && mv "$ALLOW_DIR/$old" "$ALLOW_DIR/$k" 2>/dev/null; then
    printf '%s' "$ALLOW_DIR/$k"; return 0
  fi
  return 1
}

# Adresář, ve kterém se příkazy spustí. U kontraktu v .claude/CLAUDE.md je to
# kořen repozitáře, ne .claude/ – jinak by testy běžely o adresář níž.
proj_for_md() {
  d=$(dirname "$1")
  [ "$(basename "$d")" = ".claude" ] && d=$(dirname "$d")
  printf '%s' "$d"
}

# Kde se hledá kontrakt. Jedna definice pro --allow, --list i běh: dřív měl každý
# vlastní seznam a --list se po přidání .claude/CLAUDE.md nedorovnal, takže tvrdil
# "bez kontraktu" právě o repozitářích, kvůli kterým ta cesta vznikla.
find_contract() {
  for c in "$1/CLAUDE.md" "$1/.claude/CLAUDE.md" "$1/main/CLAUDE.md"; do
    if [ -f "$c" ] && md_body "$c" | grep -q '^## Příkazy'; then printf '%s' "$c"; return 0; fi
  done
  return 1
}

# Sekce ## Příkazy, vždy z těla bez bloků kódu. Jedna definice pro --allow i běh.
contract_section() { md_body "$1" | sed -n '/^## Příkazy/,/^## /p'; }

# --- Výpis a odebrání souhlasu -------------------------------------------------
# Souhlas musí jít i zjistit a odebrat, ne jen vydat: po naklonování cizího
# repozitáře, kterému jsem ho omylem dal, by jinak nebyla cesta zpět.

# Cesta, pro kterou se souhlas hledá. Existuje-li adresář, jde se přes canon: jinak `--revoke .` a `--revoke cesta/`
# nesedly na uložený řetězec a odvolání souhlasu tiše neproběhlo – přičemž hláška
# zněla jako fakt o stavu ("žádný souhlas vydaný nebyl"), ne jako chyba vstupu.
# Neexistující adresář se skládá ručně, aby šel odvolat i souhlas pro smazanou cestu.
norm_path() {
  if [ -d "$1" ]; then canon "$1" && return 0; fi
  p=$1
  case "$p" in /*) ;; *) p="${PWD%/}/${p#./}" ;; esac
  while :; do case "$p" in */) p=${p%/} ;; *) break ;; esac; done
  printf '%s' "$p"
}

if [ "${1:-}" = "--list" ]; then
  need_tools
  N=0
  for f in "$ALLOW_DIR"/*; do
    [ -f "$f" ] || continue
    P=$(head -1 "$f")
    if [ ! -d "$P" ]; then STATE_TXT="adresář neexistuje"
    elif MD=$(find_contract "$P"); then STATE_TXT="kontrakt v ${MD#"$P"/}"
    else STATE_TXT="bez kontraktu – hook tu nic nespustí"
    fi
    printf '%s\n    %s\n' "$P" "$STATE_TXT"
    N=$((N+1))
  done
  [ "$N" = 0 ] && echo "Souhlas není vydaný pro žádný projekt."
  exit 0
fi

if [ "${1:-}" = "--revoke" ]; then
  need_tools
  [ -n "${2:-}" ] || die "použití: green-line.sh --revoke <projekt>"
  P=$(norm_path "$2")
  N=0
  # Odvolat se musí dát i souhlas zadaný přes jinou větev téhož repozitáře, proto
  # se kromě uložené cesty porovnává i klíč podle repozitáře.
  RKEY=$(proj_key "$(repo_id "$P")")
  for f in "$ALLOW_DIR"/*; do
    [ -f "$f" ] || continue
    STORED=$(head -1 "$f")
    if [ "$STORED" = "$P" ] || [ "$STORED" = "$P/main" ] || [ "$(basename "$f")" = "$RKEY" ]; then
      rm -f "$f" || die "nelze smazat $f"
      echo "Souhlas odebrán: $STORED"
      N=$((N+1))
    fi
  done
  if [ "$N" = 0 ]; then
    echo "Pro $P žádný souhlas vydaný nebyl." >&2
    exit 1
  fi
  exit 0
fi

# --- Vydání souhlasu -----------------------------------------------------------
if [ "${1:-}" = "--allow" ]; then
  need_tools
  P=$(canon "${2:-$PWD}") || die "neznámá cesta: ${2:-$PWD}"
  MD=$(find_contract "$P") || die "v ${2:-$PWD} není CLAUDE.md se sekcí ## Příkazy."
  P=$(proj_for_md "$MD")
  mkdir -p "$ALLOW_DIR" 2>/dev/null || die "nelze založit $ALLOW_DIR"
  chmod 700 "$(dirname "$ALLOW_DIR")" "$ALLOW_DIR" 2>/dev/null || true
  RKEY=$(proj_key "$(repo_id "$P")")
  printf '%s\n' "$P" > "$ALLOW_DIR/$RKEY" || die "nelze zapsat souhlas do $ALLOW_DIR"
  [ -s "$ALLOW_DIR/$RKEY" ] || die "souhlas se nezapsal."
  SEC=$(contract_section "$MD")
  echo "Zelená linka poběží v $P, podle kontraktu v $MD."
  echo
  echo "Po každém tahu spustí:"
  FOUND=""
  for k in typecheck lint test; do
    v=$(printf '%s\n' "$SEC" | sed -n "s/^[[:space:]]*[-*][[:space:]]*$k:[[:space:]]\{1,\}//p" | head -1 | sed 's/[[:space:]]*$//')
    if [ "$v" = "-" ]; then printf '  %-10s %s\n' "$k:" "(neaplikuje se)"
    elif [ -n "$v" ]; then printf '  %-10s %s\n' "$k:" "$v"; FOUND="$v"; fi
  done
  [ -z "$FOUND" ] && echo "  (nic – kontrakt nemá typecheck, lint ani test, hook tu nic nespustí)"
  # Ostatní klíče jsou dokumentace pro člověka; zelená linka je nepouští.
  OTHER=$(printf '%s\n' "$SEC" | sed -n 's/^[[:space:]]*[-*][[:space:]]*\([a-zA-Z][a-zA-Z0-9:_-]*\):[[:space:]].*/\1/p' \
          | grep -vxE 'typecheck|lint|test' | paste -sd, - | sed 's/,/, /g')
  [ -n "$OTHER" ] && echo "  Nespouští: $OTHER (jen dokumentace v kontraktu)"
  echo
  echo "Platí pro celý repozitář včetně jeho worktree – nová větev si o souhlas znovu neříká."
  echo
  echo "Souhlas platí pro REPOZITÁŘ, ne pro ty konkrétní řádky:"
  echo "co ty příkazy udělají, určuje package.json, Makefile nebo konfigurace v tomhle repu"
  echo "a to se neschvaluje. Do cizího naklonovaného repozitáře souhlas nedávej."
  exit 0
fi

# Neznámý přepínač: bez tohohle by hook čekal na stdin a vypadal by jako zaseknutý.
case "${1:-}" in
  "") ;;
  *) die "neznámý přepínač ${1}. Použití: --allow <projekt> | --list | --revoke <projekt>" ;;
esac

# --- Vstup ---------------------------------------------------------------------
INPUT=$(cat)
have jq || die "chybí jq, hook neběží."
CWD=$(printf '%s' "$INPUT" | jq -r '.cwd // empty' 2>/dev/null)
SESSION=$(printf '%s' "$INPUT" | jq -r '.session_id // "nosession"' 2>/dev/null | tr -cd 'A-Za-z0-9._-')
[ -n "$SESSION" ] || SESSION=nosession
# Když cwd neexistuje, nepokračovat "někde jinde" – našel by se cizí projekt.
if [ -n "$CWD" ]; then cd "$CWD" 2>/dev/null || die "adresář $CWD neexistuje."; fi

# Vypnutá brána se hlásí, nemlčí: brána, o které nikdo neví, že neběží, je horší
# než chybějící brána – tváří se jako kontrola, která neprobíhá.
if [ "${CLAUDE_NO_GREEN_LINE:-0}" = "1" ]; then
  echo "Zelená linka: vypnutá proměnnou CLAUDE_NO_GREEN_LINE, nespustil jsem nic." >&2
  exit 0
fi

# --- Kde je projekt ------------------------------------------------------------
# Ve worktree layoutu stojí session často v kořeni kontejneru, který sám pracovní
# strom není – proto se hledá i v main/ a příkazy pak běží tam, ne v cwd.
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || true)
CLAUDE_MD=$(find_contract "$PWD" || find_contract "${ROOT:-/nonexistent}") || exit 0
PROJ=$(canon "$(proj_for_md "$CLAUDE_MD")")

for d in "$PROJ" "$PWD"; do
  if [ -f "$d/.claude/no-green-line" ]; then
    echo "Zelená linka: vypnutá souborem $d/.claude/no-green-line, nespustil jsem nic." >&2
    exit 0
  fi
done

need_tools
[ -d "$ALLOW_DIR" ] && [ ! -O "$ALLOW_DIR" ] && die "$ALLOW_DIR nepatří tobě, nespouštím nic."

KEY=$(proj_key "$(repo_id "$PROJ")")
if ! allow_file "$PROJ" >/dev/null; then
  {
    echo "Zelená linka: pro $PROJ není vydaný souhlas, nespustil jsem nic."
    echo "Kontrakt je kód z repozitáře. Projdi si ho a jestli tomu repozitáři věříš:"
    echo "  ~/.claude/green-line.sh --allow $PROJ"
    contract_section "$CLAUDE_MD" \
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
SECTION=$(contract_section "$CLAUDE_MD")
[ -n "$SECTION" ] || die "sekci ## Příkazy se nepodařilo přečíst z $CLAUDE_MD."
cmd_for() {
  printf '%s\n' "$SECTION" | sed -n "s/^[[:space:]]*[-*][[:space:]]*$1:[[:space:]]\{1,\}//p" \
    | head -1 | sed 's/[[:space:]]*$//'
}

# --- Otisk stavu ---------------------------------------------------------------
# HEAD i rozpracované změny: v projektu se zapnutým autocommitem je strom na konci
# tahu čistý, takže "jsou tu rozpracované změny" by bránu tiše vypnulo.
#
# Musí zahrnovat OBSAH, ne jen jména: `git status --porcelain` vypíše " M soubor"
# stejně pro první i desátou úpravu téhož souboru. Se samotným porcelainem tedy
# platilo, že po první zelené kontrole šlo tentýž rozpracovaný soubor libovolně
# rozbít a hook to prohlásil za "tenhle stav už prošel" a pustil dál.
# -uall rozbalí neverzované adresáře na jednotlivé soubory. Bez něj je celý nový
# adresář jedinou položkou "?? dir/", test [ -f ] na ní neprojde a obsah se do
# otisku vůbec nedostane – takže po první zelené kontrole šlo do něj psát cokoliv
# a hook to prohlásil za "tenhle stav už prošel". Nová feature přitom skoro vždycky
# začíná novým adresářem, tedy brána byla mrtvá právě tam, kde se pracuje.
# -z navíc vypíná kvotování cest, čímž odpadá ruční ořezávání uvozovek, po kterém
# soubor s escapovaným znakem ve jméně z otisku vypadl.
STATUS=""; NCHANGED=0; CONTENT=""
PATHS=()
while IFS= read -r -d '' rec; do
  st=${rec:0:2}
  p=${rec:3}
  STATUS="$STATUS$st $p
"
  NCHANGED=$((NCHANGED + 1))
  PATHS+=("$p")
  # U přejmenování a kopie následuje druhá cesta jako samostatný záznam. Bere se
  # taky – která z dvojice je zdroj a která cíl, se mezi verzemi gitu lišilo,
  # a hashovat obě je levnější než se v tom spoléhat na verzi.
  case "$st" in
    R*|C*) if IFS= read -r -d '' src; then STATUS="$STATUS   $src
"; PATHS+=("$src"); fi ;;
  esac
done < <(git -C "$PROJ" status --porcelain=v1 -z --untracked-files=all 2>/dev/null)

if [ "$NCHANGED" -le 200 ]; then
  # Hash obsahu každého vyjmenovaného souboru. Smazané a nečitelné se přeskočí –
  # jejich zmizení už je vidět v porcelainu.
  for f in ${PATHS+"${PATHS[@]}"}; do
    [ -f "$PROJ/$f" ] || continue
    CONTENT="$CONTENT$(git -C "$PROJ" hash-object -- "$f" 2>/dev/null || echo unreadable) $f
"
  done
else
  # Přes dvě stě změněných souborů: hashování by stálo víc než kontrola sama.
  # Otisk se pak nedá spolehlivě porovnat, takže se kontrola pustí pokaždé.
  CONTENT="many-$NCHANGED-$(date +%s 2>/dev/null || echo x)"
fi
SIG=$(printf '%s\n%s\n%s' "$(git -C "$PROJ" rev-parse HEAD 2>/dev/null || echo nohead)" \
                          "$STATUS" "$CONTENT" | sha)

mkdir -p "$RUN_DIR" 2>/dev/null || die "nelze založit $RUN_DIR"
# Stav je klíčovaný projektem, ne session: o tom, jestli je strom zelený, rozhoduje
# otisk stromu, a ten je pro obě session týž. Dřív si každá platila tutéž kontrolu
# zvlášť.
STATE="$RUN_DIR/$KEY"
# Zámek proti souběhu. Dvě session, které skončí tah zároveň, jinak pustí testy
# nad jedním stromem současně: kolize na portu, na testovací databázi, na dist/ –
# a hlavně obojí přeteče LIMIT, oba kroky dostanou 124 a obě session dostanou
# červenou nad kódem, který je v pořádku.
LOCK="$RUN_DIR/$KEY.lock"
find "$RUN_DIR" -maxdepth 1 -type d -name '*.lock' -mmin +10 -exec rm -rf {} + 2>/dev/null || true
if ! mkdir "$LOCK" 2>/dev/null; then
  echo "Zelená linka: kontrola tohohle projektu běží v jiné session, nespouštím ji podruhé." >&2
  exit 0
fi
trap 'rmdir "$LOCK" 2>/dev/null' EXIT INT TERM
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
# Jeden trap na obojí: druhý `trap ... EXIT` by ten první tiše přepsal a zámek
# by po doběhnutí zůstal ležet, takže by se brána v dalším tahu přeskočila.
trap 'rm -f "$TMP"; rmdir "$LOCK" 2>/dev/null' EXIT INT TERM

# Adresář, ve kterém se kroky spustí. Monorepo a projekt, kde příkazy nejsou
# v kořeni, se jinak nemají jak deklarovat: buď se do kořene napíše příkaz, který
# pustí všechno (a přeteče LIMIT po každém tahu), nebo se kontrakt nenapíše vůbec.
WORKDIR="$PROJ"
CWD_KEY=$(cmd_for cwd)
if [ -n "$CWD_KEY" ] && [ "$CWD_KEY" != "-" ]; then
  case "$CWD_KEY" in
    /*|*..*) die "kontrakt v $CLAUDE_MD má cwd mimo projekt: $CWD_KEY" ;;
  esac
  [ -d "$PROJ/$CWD_KEY" ] || die "kontrakt v $CLAUDE_MD ukazuje cwd na $CWD_KEY, ten adresář neexistuje."
  WORKDIR="$PROJ/$CWD_KEY"
fi

run() {
  # timeout bez --foreground schválně: pak běží krok ve vlastní procesní skupině
  # a signál dostane celá, takže po zabitém kroku nezůstanou viset vnukové
  # (npm → node → vitest). S --foreground přežijí a drží otevřenou rouru.
  # head -c drží výstup v mezích – smyčkující příkaz jinak zaplní disk.
  ( cd "$WORKDIR" && "$TIMEOUT_BIN" --kill-after=5 "$LIMIT" bash -c "$1" 2>&1 ) \
    | head -c "$MAX_OUT" > "$TMP"
  return "${PIPESTATUS[0]}"
}

FAILED=""; SKIPPED=""; BROKEN=""
for step in typecheck lint test; do
  CMD=$(cmd_for "$step")
  # Pomlčka znamená "tenhle krok se v projektu neaplikuje" – vědomé rozhodnutí,
  # ne díra v kontraktu, takže se nehlásí jako nezkontrolované.
  [ "$CMD" = "-" ] && continue
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
    # "Test našel chybu" a "test nejde spustit" jsou různé stavy. První je
    # informace pro Clauda – má co opravovat. Druhý je rozbité prostředí:
    # blokovat tah by ho hnalo opravovat kód, který za to nemůže.
    # 127 = příkaz neexistuje, 126 = existuje, ale nejde spustit.
    if [ "$RC" = "127" ] || [ "$RC" = "126" ]; then
      BROKEN="${BROKEN}
--- ${step}: ${CMD} ---
${BODY}"
      continue
    fi
    FAILED="${FAILED}
--- ${step}: ${CMD} ---
${BODY}"
  fi
done

note_skipped() { [ -n "$SKIPPED" ] && echo "Nekontrolovalo se: $SKIPPED (chybí v kontraktu příkazů)."; }
note_broken() {
  [ -n "$BROKEN" ] && { echo "Tyhle kroky nejde spustit – chybí nástroj, nebo je špatně kontrakt v $CLAUDE_MD."
                        echo "Není to červená linka: neopravuj kód, oprav prostředí nebo kontrakt."
                        echo "$BROKEN"; }
}

if [ -n "$FAILED" ]; then
  if [ "$STOP_ACTIVE" = "true" ]; then
    # Druhý pokus v řadě nad týmž problémem: dál už jen otravujeme.
    printf '%s %s\n' "${OK_SIG:--}" "$SIG" > "$STATE" 2>/dev/null || true
    # exit 2, ne 1: při exit 1 jde stderr jen uživateli a model o tom neví, takže
    # svoje "hotovo" nechá stát nad stavem, který branou neprošel. Zacyklit to
    # nemůže – SKIP_SIG je pro tenhle stav uložený a další volání skončí exit 0.
    { echo "Zelená linka neprošla ani napodruhé – pouštím dál, ale NENÍ to zelené."
      echo "Neopravuj to potřetí. Nehlas práci jako hotovou a napiš uživateli, co zbývá."
      note_skipped; note_broken; echo "$FAILED"; } >&2
    exit 2
  fi
  { echo "Zelená linka není zelená – práci nelze uzavřít. Oprav to, nebo se zeptej uživatele."
    echo "Netvrď, že něco prošlo, bez výstupu příkazu."
    note_skipped; note_broken; echo "$FAILED"; } >&2
  exit 2
fi

printf '%s %s\n' "$SIG" "-" > "$STATE" 2>/dev/null || true
if [ -n "$BROKEN" ]; then
  # Nespuštěný krok se nezapočítá jako "prošlo": stav se neuloží jako zelený,
  # jinak by po opravě prostředí brána mlčela, protože otisk už zná.
  printf '%s %s\n' "-" "-" > "$STATE" 2>/dev/null || true
  { note_broken; note_skipped; } >&2
  exit 1
fi
if [ -n "$SKIPPED" ]; then
  # exit 2 ze stejného důvodu jako výš: díra v kontraktu musí do shrnutí, a to
  # píše model. Stav je uložený jako zelený, takže další volání skončí exit 0.
  { echo "Zelená linka prošla, ale nekontrolovalo se: $SKIPPED (chybí v kontraktu v $CLAUDE_MD)."
    echo "Do shrnutí to napiš jako nezkontrolované. Netvrď, že prošlo všechno."; } >&2
  exit 2
fi
exit 0
