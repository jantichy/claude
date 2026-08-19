#!/bin/bash
# Barvení záložky iTerm2 podle stavu Claude Code.
# Volá se s argumentem: working | waiting | done

SESSION_KEY=$(printf '%s' "$ITERM_SESSION_ID" | tr -c 'a-zA-Z0-9' '_')
PIDFILE="/tmp/claude-tab-watcher-${SESSION_KEY}.pid"
CLAUDE_PID=$PPID

# Najdi TTY iTerm session — hook subprocess nemá vlastní controlling TTY.
find_iterm_tty() {
  local pid=$PPID
  local tty_name
  for _ in 1 2 3 4 5; do
    tty_name=$(ps -p "$pid" -o tty= 2>/dev/null | tr -d ' ')
    if [[ -n "$tty_name" && "$tty_name" != "?"* ]]; then
      echo "/dev/$tty_name"
      return 0
    fi
    pid=$(ps -p "$pid" -o ppid= 2>/dev/null | tr -d ' ')
    [[ -z "$pid" || "$pid" == "1" ]] && break
  done
  return 1
}

ITERM_TTY=$(find_iterm_tty)

write_tty() {
  [[ -n "$ITERM_TTY" ]] && printf '%s' "$1" > "$ITERM_TTY" 2>/dev/null
}

set_tab_color() {
  write_tty "$(printf '\033]6;1;bg;red;brightness;%d\a\033]6;1;bg;green;brightness;%d\a\033]6;1;bg;blue;brightness;%d\a' "$1" "$2" "$3")"
}

reset_tab_color() {
  write_tty $'\033]6;1;bg;*;default\a'
}

active_session_id() {
  osascript 2>/dev/null <<'EOF'
tell application "System Events"
  set frontApp to name of first application process whose frontmost is true
end tell
if frontApp is not "iTerm2" then
  return "no"
end if
tell application "iTerm2"
  try
    return unique id of current session of current tab of current window
  on error
    return "no"
  end try
end tell
EOF
}

is_this_tab_active() {
  local active_id my_uuid
  active_id=$(active_session_id)
  my_uuid="${ITERM_SESSION_ID##*:}"
  [[ -n "$my_uuid" && "$active_id" == "$my_uuid" ]]
}

spawn_focus_watcher() {
  # Pokud už pro tuto session běží starý watcher, ukončit ho.
  if [[ -f "$PIDFILE" ]]; then
    local old_pid
    old_pid=$(cat "$PIDFILE" 2>/dev/null)
    [[ -n "$old_pid" ]] && kill "$old_pid" 2>/dev/null
    rm -f "$PIDFILE"
  fi

  (
    trap 'rm -f "$PIDFILE"' EXIT
    while kill -0 "$CLAUDE_PID" 2>/dev/null; do
      sleep 1
      if is_this_tab_active; then
        reset_tab_color
        exit 0
      fi
    done
  ) </dev/null >/dev/null 2>&1 &

  printf '%s' "$!" > "$PIDFILE"
  disown 2>/dev/null
}

do_attention() {
  if is_this_tab_active; then
    reset_tab_color
  else
    set_tab_color 170 200 230
    spawn_focus_watcher
  fi
}

case "$1" in
  working)
    reset_tab_color
    ;;
  waiting|done)
    do_attention
    ;;
esac
