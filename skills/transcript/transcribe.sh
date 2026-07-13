#!/usr/bin/env bash
# Přepis audio souborů whisperem (whisper.cpp). Vše vzniká v pracovním adresáři.
#
# Usage:
#   transcribe.sh <workdir> <log_file> <audio1> [<audio2> ...]
#
# Pro každý vstup vznikne <workdir>/<název_bez_přípony>.txt (surový přepis).
# Do <log_file> se píše průběh, ze kterého čte progress.py:
#   ### DURATION N SECONDS      (délky souborů — pro odhad postupu)
#   ### START zaznam-N HH:MM:SS
#   [HH:MM:SS ...] segmenty      (píše whisper)
#   ### DONE zaznam-N HH:MM:SS
#   ### ALL DONE
#
# Průběžný stav kdykoli:  python3 progress.py <log_file>

set -e
MODEL="$HOME/.whisper-models/ggml-large-v3-turbo.bin"
LANG_CODE="${WHISPER_LANG:-cs}"   # jazyk lze přebít proměnnou WHISPER_LANG
WORKDIR="$1"; LOG="$2"; shift 2
: > "$LOG"

# 1) délky do logu
n=0
for f in "$@"; do
  n=$((n+1))
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
  echo "### DURATION $n $d" >> "$LOG"
done

# 2) přepis
n=0
for f in "$@"; do
  n=$((n+1))
  base=$(basename "$f"); base="${base%.*}"
  wav="$WORKDIR/.${base}.tmp.wav"
  ffmpeg -y -i "$f" -ar 16000 -ac 1 -c:a pcm_s16le "$wav" 2>/dev/null
  echo "### START zaznam-$n $(date +%H:%M:%S)" >> "$LOG"
  whisper-cli -m "$MODEL" -l "$LANG_CODE" -f "$wav" -otxt -of "$WORKDIR/$base" -np >> "$LOG" 2>&1
  echo "### DONE zaznam-$n $(date +%H:%M:%S)" >> "$LOG"
  rm -f "$wav"
done
echo "### ALL DONE" >> "$LOG"
