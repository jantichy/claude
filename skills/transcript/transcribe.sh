#!/usr/bin/env bash
# Přepis audio souborů whisperem (whisper.cpp). Vše vzniká v pracovním adresáři.
#
# Použití:
#   transcribe.sh <workdir> <log_file> <audio1> [<audio2> ...]
#
# Chování řídí proměnné prostředí:
#   WHISPER_MODEL   turbo | large-v3            (výchozí turbo)
#   WHISPER_LANG    kód jazyka                  (výchozí cs)
#   WHISPER_PROMPT  slovník jmen a termínů      (výchozí prázdný)
#   WHISPER_VAD     1 | 0 – detekce řeči        (výchozí 1)
#   WHISPER_KEEP_WAV 1 | 0 – nechat WAV vedle    (výchozí 0; diarizace ho potřebuje)
#
# Pro každý vstup vznikne <workdir>/<název>.txt a <workdir>/<název>.srt.
# SRT vzniká vždy, protože se z něj počítá podíl řeči; když ho volající nechce,
# smaže ho v úklidu.
#
# Do <log_file> se píše průběh, ze kterého čte progress.py:
#   ### DURATION N SECONDS       (délky souborů – pro odhad postupu)
#   ### START zaznam-N HH:MM:SS
#   [HH:MM:SS ...] segmenty       (píše whisper)
#   ### DONE zaznam-N HH:MM:SS
#   ### VADSTAT N SPEECH_S TOTAL_S PERCENT
#   ### FAILED zaznam-N <důvod>   (běh pokračuje dalším souborem)
#   ### ELAPSED AUDIO_S WALL_S
#   ### ALL DONE
#
# Průběžný stav kdykoli:  python3 progress.py <log_file>

set -uo pipefail
# Česká locale by do čísel dala desetinnou čárku a rozbila awk i rate.py.
export LC_ALL=C
HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source-path=SCRIPTDIR
# shellcheck source=common.sh
. "$HERE/common.sh"

MODEL_KEY="${WHISPER_MODEL:-turbo}"
LANG_CODE="${WHISPER_LANG:-cs}"
PROMPT="${WHISPER_PROMPT:-}"
USE_VAD="${WHISPER_VAD:-1}"
KEEP_WAV="${WHISPER_KEEP_WAV:-0}"

MODEL="$(model_file "$MODEL_KEY")"
if [ -z "$MODEL" ] || [ ! -f "$MODEL" ]; then
  echo "Model '$MODEL_KEY' není k dispozici. Spusť check-deps.sh $MODEL_KEY" >&2
  exit 2
fi

WORKDIR="$1"; LOG="$2"; shift 2
: > "$LOG"

THREADS="$(n_threads)"

# Přepínače whisperu společné pro všechny soubory
declare -a WOPTS=(-m "$MODEL" -l "$LANG_CODE" -t "$THREADS" -otxt -osrt -sns -np)
[ -n "$PROMPT" ] && WOPTS+=(--prompt "$PROMPT" --carry-initial-prompt)
if [ "$USE_VAD" = "1" ] && [ -f "$VAD_MODEL" ]; then
  # Práh níž než výchozích 0.50 a delší doběh, ať VAD neuřízne tiché mluvčí.
  WOPTS+=(--vad -vm "$VAD_MODEL" -vt 0.35 -vp 200)
fi

# Součet délek řečových úseků v SRT – kolik zvuku se opravdu přepisovalo.
speech_seconds() {
  awk -F' --> ' '
    /-->/ {
      split($1, a, /[:,]/); split($2, b, /[:,]/)
      s = a[1]*3600 + a[2]*60 + a[3] + a[4]/1000
      e = b[1]*3600 + b[2]*60 + b[3] + b[4]/1000
      if (e > s) total += e - s
    }
    END { printf "%.1f", total + 0 }
  ' "$1" 2>/dev/null || echo 0
}

# 1) délky do logu
n=0
total_audio=0
for f in "$@"; do
  n=$((n+1))
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f" 2>/dev/null)
  [ -n "$d" ] || d=0
  echo "### DURATION $n $d" >> "$LOG"
  total_audio=$(awk -v a="$total_audio" -v b="$d" 'BEGIN{printf "%.3f", a+b}')
done

# 2) přepis – chyba jednoho souboru neshodí zbytek běhu
wall_start=$(date +%s)
n=0
for f in "$@"; do
  n=$((n+1))
  base=$(basename "$f"); base="${base%.*}"
  # Skrytý název jen u dočasného WAV; ten, který má přežít pro diarizaci, je vidět.
  if [ "$KEEP_WAV" = "1" ]; then
    wav="$WORKDIR/$base.wav"
    # Vstup už může BÝT tenhle soubor (nahrávka je WAV a leží v pracovním adresáři).
    # Bez téhle pojistky by ffmpeg přepisoval vlastní vstup a nevznikl by přepis.
    [ "$wav" = "$f" ] && wav="$WORKDIR/$base.16k.wav"
  else
    wav="$WORKDIR/.${base}.tmp.wav"
  fi

  if ! ffmpeg -y -i "$f" -ar 16000 -ac 1 -c:a pcm_s16le "$wav" >>"$LOG" 2>&1; then
    echo "### FAILED zaznam-$n prevod-na-wav" >> "$LOG"
    rm -f "$wav"
    continue
  fi

  echo "### START zaznam-$n $(date +%H:%M:%S)" >> "$LOG"
  if whisper-cli "${WOPTS[@]}" -f "$wav" -of "$WORKDIR/$base" >> "$LOG" 2>&1; then
    echo "### DONE zaznam-$n $(date +%H:%M:%S)" >> "$LOG"
    srt="$WORKDIR/$base.srt"
    if [ -f "$srt" ]; then
      dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f" 2>/dev/null)
      [ -n "$dur" ] || dur=0
      sp=$(speech_seconds "$srt")
      pct=$(awk -v s="$sp" -v d="$dur" 'BEGIN{ printf "%.0f", (d>0 ? 100*s/d : 0) }')
      echo "### VADSTAT $n $sp $dur $pct" >> "$LOG"
    fi
  else
    echo "### FAILED zaznam-$n whisper" >> "$LOG"
  fi
  [ "$KEEP_WAV" = "1" ] || rm -f "$wav"
done
wall=$(( $(date +%s) - wall_start ))

echo "### ELAPSED $total_audio $wall" >> "$LOG"
python3 "$HERE/rate.py" update "$MODEL_KEY" "$total_audio" "$wall" 2>/dev/null || true
echo "### ALL DONE" >> "$LOG"
