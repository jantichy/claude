#!/usr/bin/env bash
# Diarizace – druhý, volitelný průchod nad WAV z transcribe.sh. Zjistí, kdo kdy mluví.
#
# Použití:
#   diarize.sh <workdir> <log_file> <wav> [počet_mluvčích]
#
# Počet mluvčích: číslo, nebo "auto". Pevné číslo dělá výrazně míň chyb.
#
# Vznikne <workdir>/<název>.diarization.json – syrové úseky bez textu:
#   {"num_speakers": 2, "turns": [{"start": 0.0, "end": 4.2, "speaker": "SPEAKER_00"}, …]}
# Text se k nim přiřadí až v merge.py.
#
# Do <log_file> se připisuje:
#   ### DIARIZE START HH:MM:SS
#   ### DIARIZE DONE HH:MM:SS
#   ### DIARSTAT <mluvčích> <úseků>
#   ### DIARIZE FAILED <důvod>      (přepis tím nepřichází vniveč)
#   ### DIARIZE ELAPSED <audio_s> <wall_s>
#
# Selhání tohohle skriptu NESMÍ shodit už hotový přepis – volající pokračuje dál
# bez rozlišených mluvčích a řekne to uživateli.

set -uo pipefail
export LC_ALL=C
HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source-path=SCRIPTDIR
# shellcheck source=common.sh
. "$HERE/common.sh"

WORKDIR="$1"; LOG="$2"; WAV="$3"; NSPK="${4:-auto}"

fail() {
  echo "### DIARIZE FAILED $1" >> "$LOG"
  exit 3
}

[ -x "$DIARIZE_PY" ] || fail "chybi-venv"
[ -f "$WAV" ]        || fail "chybi-wav"

TOKEN="${HF_TOKEN:-}"
[ -n "$TOKEN" ] || { [ -f "$HF_TOKEN_FILE" ] && TOKEN="$(tr -d '[:space:]' < "$HF_TOKEN_FILE")"; }
[ -n "$TOKEN" ] || fail "chybi-hf-token"

base=$(basename "$WAV"); base="${base%.*}"
OUT="$WORKDIR/$base.diarization.json"
audio_s=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$WAV" 2>/dev/null)
[ -n "$audio_s" ] || audio_s=0

echo "### DIARIZE START $(date +%H:%M:%S)" >> "$LOG"
wall_start=$(date +%s)

HF_TOKEN="$TOKEN" DIAR_WAV="$WAV" DIAR_OUT="$OUT" DIAR_NSPK="$NSPK" DIAR_MODEL="$DIARIZE_MODEL" \
  "$DIARIZE_PY" "$HERE/diarize.py" >> "$LOG" 2>&1 || fail "pyannote"

wall=$(( $(date +%s) - wall_start ))
[ -f "$OUT" ] || fail "bez-vystupu"

read -r spk turns < <(python3 -c "
import json
d = json.load(open('$OUT'))
print(d.get('num_speakers', 0), len(d.get('turns', [])))
" 2>/dev/null || echo "0 0")

{
  echo "### DIARIZE DONE $(date +%H:%M:%S)"
  echo "### DIARSTAT $spk $turns"
  echo "### DIARIZE ELAPSED $audio_s $wall"
} >> "$LOG"
python3 "$HERE/rate.py" update diarize "$audio_s" "$wall" 2>/dev/null || true
