#!/usr/bin/env bash
# Kontrola závislostí pro skill /transcript.
# Vypíše, co je k dispozici a co chybí, a jak chybějící doinstalovat.
#
# Usage:
#   check-deps.sh [model ...]     # model: turbo | large-v3 (výchozí turbo)
#
# Exit 0 = vše připraveno, 1 = něco chybí.
set -u
# shellcheck source=common.sh
. "$(dirname "$0")/common.sh"

MODELS=("$@")
[ "${#MODELS[@]}" -gt 0 ] || MODELS=("turbo")

missing=0
declare -a fixes=()

echo "Kontrola závislostí skillu /transcript:"

if command -v ffmpeg >/dev/null 2>&1; then
  echo "  ✓ ffmpeg"
else
  echo "  ✗ ffmpeg – chybí"
  fixes+=("brew install ffmpeg")
  missing=1
fi

if command -v whisper-cli >/dev/null 2>&1; then
  echo "  ✓ whisper.cpp (whisper-cli)"
else
  echo "  ✗ whisper.cpp (whisper-cli) – chybí"
  fixes+=("brew install whisper-cpp")
  missing=1
fi

for key in "${MODELS[@]}"; do
  f=$(model_file "$key")
  if [ -z "$f" ]; then
    echo "  ✗ neznámý model '$key' (znám: turbo, large-v3)"
    missing=1
  elif [ -f "$f" ]; then
    echo "  ✓ model $key"
  else
    echo "  ✗ model $key – chybí ($f)"
    fixes+=("mkdir -p \"$MODELS_DIR\" && curl -L -o \"$f\" \"$(model_url "$key")\"")
    missing=1
  fi
done

if [ -f "$VAD_MODEL" ]; then
  echo "  ✓ VAD model (Silero)"
else
  echo "  ✗ VAD model (Silero) – chybí ($VAD_MODEL)"
  fixes+=("mkdir -p \"$MODELS_DIR\" && curl -L -o \"$VAD_MODEL\" \"$VAD_MODEL_URL\"")
  missing=1
fi

if [ "$missing" -eq 1 ]; then
  echo ""
  echo "Chybějící části nainstaluj takto:"
  for fix in "${fixes[@]}"; do echo "  $fix"; done
  echo ""
  echo "(whisper.cpp a ffmpeg jsou dostupné přes Homebrew – https://brew.sh)"
  exit 1
fi

echo "Vše připraveno."
exit 0
