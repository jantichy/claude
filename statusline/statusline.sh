#!/usr/bin/env bash
# Claude Code status line – globální konfigurace
# Zobrazuje: cwd | model | context bar | 5h limit | týdenní limit | git změny
# U limitů pruh odlišuje vyčerpané nad proporční tempo okna a nevyčerpanou rezervu.

input=$(cat)

# awk čte desetinná čísla podle LC_NUMERIC: v českém locale čeká čárku, z „99.6“
# přečte 99 a procenta se místo zaokrouhlení ořežou, včetně prahů barev.
# LC_ALL by LC_NUMERIC přebilo, proto pryč.
unset LC_ALL
export LC_NUMERIC=C

# ---------------------------------------------------------------------------
# 1. UKAZATEL KONTEXTU A LIMITŮ
# ---------------------------------------------------------------------------
BAR_WIDTH=7
CTX_SPARE_CELLS=3

make_bar() {
  local pct="$1"
  local filled
  filled=$(echo "$pct $BAR_WIDTH" | awk '{printf "%d", int($1 / 100 * $2 + 0.5)}')
  local empty=$(( BAR_WIDTH - filled ))
  local bar=""
  # Vlastní smyčka, ne `seq`: BSD seq při `seq 1 0` počítá dolů a vypíše "1 0",
  # takže prázdný pruh měl dva vyplněné bloky a plný byl o dva znaky delší.
  local i=0
  while [ "$i" -lt "$filled" ]; do bar="${bar}█"; i=$((i + 1)); done
  i=0
  while [ "$i" -lt "$empty" ];  do bar="${bar}░"; i=$((i + 1)); done
  echo "$bar"
}

# Pruh s hranicí: vyčerpané do hranice █, nad ní █ v sytém odstínu barvy
# položky, nevyčerpaný zbytek do hranice ▓ v její tlumené barvě – položka si
# drží jednu barvu. Argumenty: procenta, hranice v kostičkách, barva pruhu, do
# které se po odlišení vrací, a sytý odstín (obojí escape sekvence). Sytý odstín
# je jasná varianta barvy (9x), ne svítivá 3x – ta od 80 % barví celou položku
# a přečerpání by v ní splynulo.
make_split_bar() {
  local pct="$1" pace="$2" base over filled
  base=$(printf '%b' "$3")
  over=$(printf '%b' "$4")
  filled=$(echo "$pct $BAR_WIDTH" | awk '{printf "%d", int($1 / 100 * $2 + 0.5)}')
  local bar="" i=1
  while [ "$i" -le "$BAR_WIDTH" ]; do
    if [ "$i" -le "$filled" ] && [ "$i" -gt "$pace" ]; then
      bar="${bar}${over}█${base}"
    elif [ "$i" -le "$filled" ]; then
      bar="${bar}█"
    elif [ "$i" -le "$pace" ]; then
      bar="${bar}▓"
    else
      bar="${bar}░"
    fi
    i=$((i + 1))
  done
  echo "$bar"
}

# Pruh limitu s proporčním tempem okna jako hranicí: kostička je 1/BAR_WIDTH
# okna (u týdne den). Rozběhnutá kostička tempa se počítá celá – dnešní příděl
# je k dispozici hned. Argumenty: procenta, resets_at (epoch, smí být prázdné),
# délka okna v sekundách, barva pruhu a sytý odstín jako u `make_split_bar`.
make_pace_bar() {
  local pct="$1" reset="$2" window="$3" elapsed pace
  if [ -z "$reset" ]; then make_bar "$pct"; return; fi
  elapsed=$(( window - (reset - $(date +%s)) ))
  if [ "$elapsed" -lt 0 ]; then elapsed=0; fi
  pace=$(( elapsed * BAR_WIDTH / window + 1 ))
  if [ "$pace" -gt "$BAR_WIDTH" ]; then pace=$BAR_WIDTH; fi
  make_split_bar "$pct" "$pace" "$4" "$5"
}

# Zaokrouhlí procenta na celé číslo, poloviny nahoru – stejně jako `make_bar`.
# Ne `printf "%.0f"`: to zaokrouhluje poloviny k sudé (2.5 → 2), takže by číslo
# a pruh u téže hodnoty zaokrouhlovaly každé jinak.
round_pct() {
  echo "$1" | awk '{printf "%d", int($1 + 0.5)}'
}

# Naformátuje počet tokenů: 1234567 → "1.2M", 49883 → "50k", 999 → "999"
fmt_tokens() {
  echo "$1" | awk '{
    n = $1
    if (n >= 1000000) {
      v = n / 1000000
      if (v == int(v)) printf "%dM", v
      else printf "%.1fM", v
    } else if (n >= 1000) {
      printf "%dk", int(n / 1000 + 0.5)
    } else {
      printf "%d", n
    }
  }'
}

# Číslo z JSONu, nebo náhrada. Hodnota ze vstupu se NIKDY nesmí dostat rovnou do
# `$(( ))`: bash tam obsah proměnné vyhodnocuje jako výraz rekurzivně, takže
# `a[$(příkaz)]` v číselném poli spustí ten příkaz. Ověřeno – status line běží
# po každé odpovědi, permission systém na ni nesahá a jediné, co ji dělí od
# spuštění cizího kódu, je důvěra ve tvar vstupu. Ta stačit nemá.
num() {
  case "$1" in
    ''|*[!0-9]*) printf '%s' "${2:-0}" ;;
    *)           printf '%s' "$1" ;;
  esac
}

# Context window (tokeny)
ctx_used=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
ctx_size=$(echo "$input" | jq -r '.context_window.context_window_size // empty')
ctx_in=$(num "$(echo "$input" | jq -r '.context_window.current_usage.input_tokens // 0')")
ctx_cc=$(num "$(echo "$input" | jq -r '.context_window.current_usage.cache_creation_input_tokens // 0')")
ctx_cr=$(num "$(echo "$input" | jq -r '.context_window.current_usage.cache_read_input_tokens // 0')")
ctx_used_tokens=$(( ctx_in + ctx_cc + ctx_cr ))
# Rate limits – 5h session a 7day týdenní
five_pct=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
five_reset=$(num "$(echo "$input" | jq -r '.rate_limits.five_hour.resets_at // empty')" "")
week_pct=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')
week_reset=$(num "$(echo "$input" | jq -r '.rate_limits.seven_day.resets_at // empty')" "")

ctx_part=""
usage_part=""

if [ -n "$ctx_used" ]; then
  ctx_int=$(round_pct "$ctx_used")
  # Barva: zelená < 60 %, tlumená žlutá < 80 %, žlutá < 85 %, červená >= 85 %.
  # Přečerpané kostičky mají jasnou variantu téže barvy.
  if [ "$ctx_int" -ge 85 ]; then
    color="\033[31m"     # svítivá červená
    ctx_over="\033[22;91m"
  elif [ "$ctx_int" -ge 80 ]; then
    color="\033[33m"     # svítivá žlutá
    ctx_over="\033[22;93m"
  elif [ "$ctx_int" -ge 60 ]; then
    color="\033[2;33m"   # tlumená žlutá
    ctx_over="\033[22;93m"
  else
    color="\033[2;32m"   # tlumená zelená
    ctx_over="\033[22;92m"
  fi
  # Prvních CTX_SPARE_CELLS kostiček je prostor, ve kterém se dá pracovat
  # (u 1M okna zhruba 430k); co je nad ně, je kontext přetažený.
  bar=$(make_split_bar "$ctx_used" "$CTX_SPARE_CELLS" "$color" "$ctx_over")
  reset="\033[0m"
  if [ -n "$ctx_size" ] && [ "$ctx_used_tokens" -gt 0 ]; then
    used_str=$(fmt_tokens "$ctx_used_tokens")
    size_str=$(fmt_tokens "$ctx_size")
    ctx_part=$(printf "${color}Context: %s/%s [%s] %d%%${reset}" "$used_str" "$size_str" "$bar" "$ctx_int")
  else
    ctx_part=$(printf "${color}Context: [%s] %d%%${reset}" "$bar" "$ctx_int")
  fi
fi

# Přidej rate limit info pokud je k dispozici
if [ -n "$five_pct" ]; then
  five_int=$(round_pct "$five_pct")
  if [ "$five_int" -ge 80 ]; then
    limit_color="\033[35m"    # svítivá magenta
  else
    limit_color="\033[2;35m"  # tlumená magenta
  fi
  bar5=$(make_pace_bar "$five_pct" "$five_reset" 18000 "$limit_color" "\033[22;95m")
  # Vypočítat zbývající čas do resetu limitu
  if [ -n "$five_reset" ]; then
    now=$(date +%s)
    remaining=$(( five_reset - now ))
    if [ "$remaining" -lt 0 ]; then remaining=0; fi
    hh=$(( remaining / 3600 ))
    mm=$(( (remaining % 3600) / 60 ))
    five_label=$(printf "%02d:%02d" "$hh" "$mm")
  else
    five_label="5h"   # fallback pokud data ještě nejsou k dispozici
  fi
  if [ -n "$usage_part" ]; then
    usage_part=$(printf "%s  ${limit_color}Usage: %s [%s] %d%%\033[0m" "$usage_part" "$five_label" "$bar5" "$five_int")
  else
    usage_part=$(printf "${limit_color}Usage: %s [%s] %d%%\033[0m" "$five_label" "$bar5" "$five_int")
  fi
fi

# Přidej týdenní rate limit info pokud je k dispozici
if [ -n "$week_pct" ]; then
  week_int=$(round_pct "$week_pct")
  if [ "$week_int" -ge 80 ]; then
    week_color="\033[36m"    # svítivá cyan
  else
    week_color="\033[2;36m"  # tlumená cyan
  fi
  barw=$(make_pace_bar "$week_pct" "$week_reset" 604800 "$week_color" "\033[22;96m")
  # Vypočítat zbývající čas do resetu týdenního limitu ve formátu Xd H:MM
  if [ -n "$week_reset" ]; then
    now=$(date +%s)
    w_remaining=$(( week_reset - now ))
    if [ "$w_remaining" -lt 0 ]; then w_remaining=0; fi
    w_days=$(( w_remaining / 86400 ))
    w_hh=$(( (w_remaining % 86400) / 3600 ))
    w_mm=$(( (w_remaining % 3600) / 60 ))
    week_label=$(printf "%dd %d:%02d" "$w_days" "$w_hh" "$w_mm")
  else
    week_label="7d"   # fallback pokud data ještě nejsou k dispozici
  fi
  # Bez 5h limitu (Ultra) nese „Usage“ týdenní, jinak ho má 5h limit před ním
  if [ -n "$five_pct" ]; then
    week_name="Weekly"
  else
    week_name="Usage"
  fi
  if [ -n "$usage_part" ]; then
    usage_part=$(printf "%s  ${week_color}%s: %s [%s] %d%%\033[0m" "$usage_part" "$week_name" "$week_label" "$barw" "$week_int")
  else
    usage_part=$(printf "${week_color}%s: %s [%s] %d%%\033[0m" "$week_name" "$week_label" "$barw" "$week_int")
  fi
fi

# ---------------------------------------------------------------------------
# 2. MODEL A EFFORT
# ---------------------------------------------------------------------------
model_name=$(echo "$input" | jq -r '.model.display_name // .model.id // "unknown"')
model_short=$(echo "$model_name" | sed 's/Claude //i' | sed 's/ (.*)//')
effort_level=$(echo "$input" | jq -r '.effort.level // empty')
if [ -n "$effort_level" ]; then
  model_short="$model_short $effort_level"
fi

# Barva modelu: Opus = cyan (svítivější základ), ostatní = modrá.
# Intenzita roste s effort levelem; Opus má gradient posunutý výš,
# takže Opus medium vizuálně koresponduje se Sonnet xhigh.
case "$model_short" in
  Opus*)
    case "$effort_level" in
      max|xhigh)   model_color="\033[96m"   ;;  # bright cyan
      high|medium) model_color="\033[36m"   ;;  # cyan
      low)         model_color="\033[2;36m" ;;  # dim cyan
      *)           model_color="\033[36m"   ;;  # default - cyan
    esac
    ;;
  *)
    case "$effort_level" in
      max)        model_color="\033[1;94m" ;;  # bold bright blue
      xhigh)      model_color="\033[94m"   ;;  # bright blue
      high)       model_color="\033[34m"   ;;  # blue
      low|medium) model_color="\033[2;34m" ;;  # dim blue
      *)          model_color="\033[34m"   ;;  # default - blue
    esac
    ;;
esac

# ---------------------------------------------------------------------------
# 3. PRACOVNÍ ADRESÁŘ (celá cesta do 4 segmentů, jinak poslední 3)
# ---------------------------------------------------------------------------
cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // empty')
if [ -z "$cwd" ]; then cwd=$(pwd); fi
# Předřadit ~, pokud je cesta v $HOME
home_prefix="${HOME}"
if [[ "$cwd" == "$home_prefix"* ]]; then
  cwd="~${cwd#"$home_prefix"}"
fi
# Do 4 segmentů vypsat celou cestu, delší zkrátit na poslední 3
short_cwd=$(echo "$cwd" | awk -F'/' '{
  n = NF
  if (n <= 4) { print $0 }
  else {
    out = "…"
    for (i = n-2; i <= n; i++) out = out "/" $i
    print out
  }
}')

# ---------------------------------------------------------------------------
# 4. GIT ZMĚNY V SESSION (počet změněných souborů)
# ---------------------------------------------------------------------------
git_part=""
verify_part=""
project_dir=$(echo "$input" | jq -r '.workspace.project_dir // empty')
if [ -z "$project_dir" ]; then project_dir="$cwd"; fi
# Rozvinout ~ pokud je potřeba
project_dir_real="${project_dir/#\~/$HOME}"
cwd_real="${cwd/#\~/$HOME}"

# Změny se počítají v adresáři, ve kterém se pracuje (cwd), ne v kořeni projektu.
# U worktree layoutu je kořen projektu bare repo – to nemá working tree a jeho
# index si drží zastaralý stav, takže by statusline hlásil trvale falešný počet.
git_root_candidate="$cwd_real"
[ -d "$git_root_candidate" ] || git_root_candidate="$project_dir_real"

# Git nesmí spustit nic, co si nastaví adresář, ve kterém zrovna stojíme:
# core.fsmonitor v .git/config je cesta k programu a git ho zavolá při refreshi
# indexu, tedy i při `git diff`. Stačí tedy rozbalit cizí archiv a stát v něm –
# status line se překreslí a program běží s právy uživatele, bez jakéhokoli souhlasu.
# safe.directory nechrání: uplatní se jen u repozitáře patřícího jinému uživateli,
# a rozbalený archiv patří tomu, kdo ho rozbalil.
git_ro() { git -c core.fsmonitor= -c core.hooksPath=/dev/null -c core.pager=cat "$@"; }

# Vypnout dva klíče v `git_ro` nestačí: konfigurace repozitáře umí gitu předepsat
# program ke spuštění i pod jménem, které nejde předem uhodnout. `filter.<name>.clean`
# se volá pokaždé, když git potřebuje obsah pracovního souboru – tedy i při
# `git diff --name-only` –, a `<name>` si volí ten, kdo config napsal, takže ho
# nejde přebít `-c` přepínačem. Totéž platí pro `diff.<name>.textconv`.
# Jediná spolehlivá obrana je na takový repozitář nesahat. Čtení samotné
# konfigurace nic nespouští, takže se smí udělat napřed.
#
# Vzniká tím falešný poplach nad repozitářem, který si lokálně nastavil git-lfs:
# jeho `filter.lfs.clean` je legitimní. Přijímá se vědomě – rozlišovat podle
# hodnoty by znamenalo, že útočníkovi stačí pojmenovat svůj filtr `lfs`. Cena je
# nízká, protože varování nahrazuje jen počet změn; jméno větve se zjišťuje
# ze `symbolic-ref`, který obsah souborů nečte, a zobrazuje se dál.
config_runs_program() {
  { git_ro -C "$1" config --local --list 2>/dev/null
    git_ro -C "$1" config --worktree --list 2>/dev/null; } \
    | cut -d= -f1 \
    | grep -qiE '^(core\.(fsmonitor|hookspath|alternaterefscommand)|filter\..*\.(clean|smudge|process)|diff\.external|diff\..*\.(command|textconv))$'
}

if [ -d "$git_root_candidate" ] \
   && git_ro -C "$git_root_candidate" rev-parse --git-dir >/dev/null 2>&1 \
   && [ "$(git_ro -C "$git_root_candidate" rev-parse --is-bare-repository 2>/dev/null)" = "false" ]; then
  # Výsledek posledního běhu průběžné kontroly. Čte se jen stav, který si vede
  # hooks/verify.sh: soubor pojmenovaný hashem cesty ke sdílenému .git (jeho
  # proj_key a repo_id) s řádkem "OK_SIG SKIP_SIG". Po průchodu "<otisk> -",
  # po druhém selhání v řadě SKIP_SIG s otiskem, u nespustitelného kroku "- -".
  # První selhání hook nezapíše a status line pak ukazuje předchozí stav – je to
  # přijaté, výsledek se schválně nikam dalšího nezapisuje. Jméno padajícího kroku
  # hook neukládá. Bez souboru (projekt bez kontraktu, běh starší než 4 hodiny,
  # které hook maže) se položka neukazuje.
  common_dir=$(git_ro -C "$git_root_candidate" rev-parse --git-common-dir 2>/dev/null)
  case "$common_dir" in /*) ;; *) common_dir="$git_root_candidate/$common_dir" ;; esac
  common_dir=$( (cd "$common_dir" 2>/dev/null && pwd -P) )
  if [ -n "$common_dir" ]; then
    verify_state="$HOME/.local/state/claude-verify/runs/$(printf '%s' "$common_dir" | shasum | cut -d' ' -f1)"
    if [ -f "$verify_state" ]; then
      ok_sig=""; skip_sig=""
      read -r ok_sig skip_sig < "$verify_state" 2>/dev/null || true
      if [ -n "$skip_sig" ] && [ "$skip_sig" != "-" ]; then
        verify_part=$(printf "\033[31m✗ failed\033[0m")
      elif [ "$ok_sig" = "-" ]; then
        verify_part=$(printf "\033[33m⚠ can't run\033[0m")
      elif [ -n "$ok_sig" ]; then
        verify_part=$(printf "\033[2;32m✓ ok\033[0m")
      fi
    fi
  fi
  # Jméno větve; u odpojené HEAD krátký hash, v prázdném repozitáři fallback "Git"
  branch=$(git_ro -C "$git_root_candidate" symbolic-ref --quiet --short HEAD 2>/dev/null)
  if [ -z "$branch" ]; then
    branch=$(git_ro -C "$git_root_candidate" rev-parse --short HEAD 2>/dev/null)
  fi
  if [ -z "$branch" ]; then branch="Git"; fi
  if config_runs_program "$git_root_candidate"; then
    git_part=$(printf "\033[31m%s: ⚠ config spouští program\033[0m" "$branch")
  else
    unstaged=$(git_ro -C "$git_root_candidate" diff --name-only 2>/dev/null | wc -l | tr -d ' ')
    staged=$(git_ro -C "$git_root_candidate" diff --cached --name-only 2>/dev/null | wc -l | tr -d ' ')
    total=$(( unstaged + staged ))
    # Commity, které nejsou na upstreamu – selhaný push autocommitu jinak nikdo
    # neuvidí. rev-list čte jen reference a objekty, obsah pracovních souborů ne.
    # Větev bez upstreamu nic neukazuje.
    ahead=$(num "$(git_ro -C "$git_root_candidate" rev-list --count '@{upstream}..HEAD' 2>/dev/null)")
    ahead_part=""
    if [ "$ahead" -gt 0 ]; then ahead_part=$(printf " ↑%d" "$ahead"); fi
    if [ "$total" -gt 0 ]; then
      git_part=$(printf "\033[33m%s: ~%d changes%s\033[0m" "$branch" "$total" "$ahead_part")
    else
      git_part=$(printf "\033[2;32m%s: Clean%s\033[0m" "$branch" "$ahead_part")
    fi
  fi
fi

# ---------------------------------------------------------------------------
# VÝSLEDNÝ ŘÁDEK
# ---------------------------------------------------------------------------
sep=$(printf "\033[90m│\033[0m")

line=""

append() {
  local part="$1"
  if [ -n "$part" ]; then
    if [ -n "$line" ]; then
      line="$line $sep $part"
    else
      line="$part"
    fi
  fi
}

append "$(printf "\033[2;33m%s\033[0m" "$short_cwd")"
append "$(printf "${model_color}%s\033[0m" "$model_short")"
append "$ctx_part"
append "$usage_part"
append "$verify_part"
[ -n "$git_part" ] && append "$git_part"

# %s, ne %b: jednotlivé části si svoje \033 rozvinuly samy ve formátu vlastního
# printf, takže druhé rozvinutí nic nepřidá – jen by vyhodnotilo zpětná lomítka,
# která přišla z názvu adresáře nebo větve, tedy z prověřovaného repozitáře.
printf '%s\n' "$line"
