#!/usr/bin/env bash
# Kontrola závislostí pro skill /transcript.
# Vypíše, co je k dispozici a co chybí, a jak chybějící doinstalovat.
#
# Usage:
#   check-deps.sh [--diarize] [model ...]   # model: turbo | large-v3 (výchozí turbo)
#
# --diarize navíc zkontroluje volitelný druhý průchod (pyannote). Ten se sám
# doinstalovat nedá: licenci gated modelu musí člověk odklikat v prohlížeči.
#
# Exit 0 = vše připraveno, 1 = něco chybí.
set -u
# shellcheck source-path=SCRIPTDIR
# shellcheck source=common.sh
. "$(dirname "$0")/common.sh"

WANT_DIARIZE=0
ARGS=()
for a in "$@"; do
  case "$a" in
    --diarize) WANT_DIARIZE=1 ;;
    *)         ARGS+=("$a") ;;
  esac
done

MODELS=("${ARGS[@]+"${ARGS[@]}"}")
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

if [ "$WANT_DIARIZE" -eq 1 ]; then
  if [ -x "$DIARIZE_PY" ] && "$DIARIZE_PY" -c "import pyannote.audio" 2>/dev/null; then
    echo "  ✓ pyannote (rozlišení mluvčích)"
  else
    echo "  ✗ pyannote (rozlišení mluvčích) – chybí"
    fixes+=("python3 -m venv \"$DIARIZE_VENV\" && \"$DIARIZE_VENV/bin/pip\" install -q pyannote.audio")
    missing=1
  fi

  if [ -n "${HF_TOKEN:-}" ] || [ -s "$HF_TOKEN_FILE" ]; then
    echo "  ✓ HuggingFace token"
  else
    echo "  ✗ HuggingFace token – chybí ($HF_TOKEN_FILE)"
    fixes+=("token z https://huggingface.co/settings/tokens ulož do $HF_TOKEN_FILE")
    fixes+=("a odsouhlas licenci na https://huggingface.co/$DIARIZE_MODEL (nutné, jinak se model nestáhne)")
    missing=1
  fi
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
