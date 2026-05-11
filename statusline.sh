#!/usr/bin/env bash
# Claude Code status line – globální konfigurace
# Zobrazuje: context bar | model | cwd | git změny | čas session

input=$(cat)

# ---------------------------------------------------------------------------
# 1. CONTEXT / RATE LIMIT PROGRESS BAR
# ---------------------------------------------------------------------------
BAR_WIDTH=7

make_bar() {
  local pct="$1"
  local filled=$(echo "$pct $BAR_WIDTH" | awk '{printf "%d", int($1 / 100 * $2 + 0.5)}')
  local empty=$(( BAR_WIDTH - filled ))
  local bar=""
  for i in $(seq 1 $filled); do bar="${bar}█"; done
  for i in $(seq 1 $empty);  do bar="${bar}░"; done
  echo "$bar"
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

# Context window (tokeny)
ctx_used=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
ctx_size=$(echo "$input" | jq -r '.context_window.context_window_size // empty')
ctx_in=$(echo "$input" | jq -r '.context_window.current_usage.input_tokens // 0')
ctx_cc=$(echo "$input" | jq -r '.context_window.current_usage.cache_creation_input_tokens // 0')
ctx_cr=$(echo "$input" | jq -r '.context_window.current_usage.cache_read_input_tokens // 0')
ctx_used_tokens=$(( ctx_in + ctx_cc + ctx_cr ))
# Rate limits – 5h session a 7day týdenní
five_pct=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
five_reset=$(echo "$input" | jq -r '.rate_limits.five_hour.resets_at // empty')
week_pct=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')
week_reset=$(echo "$input" | jq -r '.rate_limits.seven_day.resets_at // empty')

usage_part=""

if [ -n "$ctx_used" ]; then
  bar=$(make_bar "$ctx_used")
  ctx_int=$(echo "$ctx_used" | awk '{printf "%.0f", $1}')
  # Barva: zelená < 60 %, žlutá < 85 %, červená >= 85 %
  if [ "$ctx_int" -ge 85 ]; then
    color="\033[31m"     # svítivá červená
  elif [ "$ctx_int" -ge 80 ]; then
    color="\033[33m"     # svítivá žlutá
  elif [ "$ctx_int" -ge 60 ]; then
    color="\033[2;33m"   # tlumená žlutá
  else
    color="\033[2;32m"   # tlumená zelená
  fi
  reset="\033[0m"
  if [ -n "$ctx_size" ] && [ "$ctx_used_tokens" -gt 0 ]; then
    used_str=$(fmt_tokens "$ctx_used_tokens")
    size_str=$(fmt_tokens "$ctx_size")
    usage_part=$(printf "${color}Context: %s/%s [%s] %d%%${reset}" "$used_str" "$size_str" "$bar" "$ctx_int")
  else
    usage_part=$(printf "${color}Context: [%s] %d%%${reset}" "$bar" "$ctx_int")
  fi
fi

# Přidej rate limit info pokud je k dispozici
if [ -n "$five_pct" ]; then
  five_int=$(echo "$five_pct" | awk '{printf "%.0f", $1}')
  bar5=$(make_bar "$five_pct")
  if [ "$five_int" -ge 80 ]; then
    limit_color="\033[35m"    # svítivá magenta
  else
    limit_color="\033[2;35m"  # tlumená magenta
  fi
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
    usage_part=$(printf "%s  ${limit_color}Limit: %s [%s] %d%%\033[0m" "$usage_part" "$five_label" "$bar5" "$five_int")
  else
    usage_part=$(printf "${limit_color}Limit: %s [%s] %d%%\033[0m" "$five_label" "$bar5" "$five_int")
  fi
fi

# Přidej týdenní rate limit info pokud je k dispozici
if [ -n "$week_pct" ]; then
  week_int=$(echo "$week_pct" | awk '{printf "%.0f", $1}')
  barw=$(make_bar "$week_pct")
  if [ "$week_int" -ge 80 ]; then
    week_color="\033[36m"    # svítivá cyan
  else
    week_color="\033[2;36m"  # tlumená cyan
  fi
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
  if [ -n "$usage_part" ]; then
    usage_part=$(printf "%s  ${week_color}Weekly: %s [%s] %d%%\033[0m" "$usage_part" "$week_label" "$barw" "$week_int")
  else
    usage_part=$(printf "${week_color}Weekly: %s [%s] %d%%\033[0m" "$week_label" "$barw" "$week_int")
  fi
fi

# ---------------------------------------------------------------------------
# 2. MODEL
# ---------------------------------------------------------------------------
model_name=$(echo "$input" | jq -r '.model.display_name // .model.id // "unknown"')
model_short=$(echo "$model_name" | sed 's/Claude //i' | sed 's/ (.*)//')
effort_level=$(echo "$input" | jq -r '.effort.level // empty')
if [ -n "$effort_level" ]; then
  model_short="$model_short $effort_level"
fi

# Barva modelu: Opus = cyan (svítivější baseline), ostatní = modrá.
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
# 3. PRACOVNÍ ADRESÁŘ (zkrácený – max 4 segmenty od konce)
# ---------------------------------------------------------------------------
cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // empty')
if [ -z "$cwd" ]; then cwd=$(pwd); fi
# Zkrátit na posledních 3 složky, předřadit ~ pokud je v $HOME
home_prefix="${HOME}"
if [[ "$cwd" == "$home_prefix"* ]]; then
  cwd="~${cwd#$home_prefix}"
fi
# Max 4 segmenty
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
project_dir=$(echo "$input" | jq -r '.workspace.project_dir // empty')
if [ -z "$project_dir" ]; then project_dir="$cwd"; fi
# Rozvinout ~ pokud je potřeba
project_dir_real=$(echo "$project_dir" | sed "s|^~|$HOME|")

if [ -d "$project_dir_real" ] && git -C "$project_dir_real" rev-parse --git-dir >/dev/null 2>&1; then
  changed=$(git -C "$project_dir_real" diff --stat HEAD 2>/dev/null | tail -1 | grep -oE '[0-9]+ file' | grep -oE '[0-9]+')
  unstaged=$(git -C "$project_dir_real" diff --name-only 2>/dev/null | wc -l | tr -d ' ')
  staged=$(git -C "$project_dir_real" diff --cached --name-only 2>/dev/null | wc -l | tr -d ' ')
  total=$(( unstaged + staged ))
  if [ "$total" -gt 0 ]; then
    git_part=$(printf "\033[33mGit: ~%d changes\033[0m" "$total")
  else
    git_part=$(printf "\033[2;32mGit: Clean\033[0m")
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
append "$usage_part"
[ -n "$git_part" ] && append "$git_part"

printf "%b\n" "$line"
