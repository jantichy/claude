#!/usr/bin/env bash
# Sdílené definice pro skill /transcript. Sourcuje se, nespouští.

MODELS_DIR="$HOME/.whisper-models"
# shellcheck disable=SC2034  # čtou je skripty, které tenhle soubor sourcují
VAD_MODEL="$MODELS_DIR/ggml-silero-v5.1.2.bin"
# shellcheck disable=SC2034  # dtto
VAD_MODEL_URL="https://huggingface.co/ggml-org/whisper-vad/resolve/main/ggml-silero-v5.1.2.bin"

# Diarizace (volitelná, druhý průchod). Instaluje se zvlášť, viz check-deps.sh --diarize.
# shellcheck disable=SC2034  # čtou je skripty, které tenhle soubor sourcují
DIARIZE_VENV="$MODELS_DIR/venv-diarize"
# shellcheck disable=SC2034  # dtto
DIARIZE_PY="$DIARIZE_VENV/bin/python3"
# shellcheck disable=SC2034  # dtto
DIARIZE_MODEL="pyannote/speaker-diarization-3.1"
# shellcheck disable=SC2034  # dtto
HF_TOKEN_FILE="$MODELS_DIR/hf-token"

# Klíč modelu -> soubor a URL. Klíče: turbo, large-v3
model_file() {
  case "$1" in
    turbo)    echo "$MODELS_DIR/ggml-large-v3-turbo.bin" ;;
    large-v3) echo "$MODELS_DIR/ggml-large-v3.bin" ;;
    *)        echo "" ;;
  esac
}

model_url() {
  case "$1" in
    turbo)    echo "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo.bin" ;;
    large-v3) echo "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3.bin" ;;
    *)        echo "" ;;
  esac
}

# Počet výkonných jader; whisper.cpp má výchozí 4, což je na M-čku málo.
n_threads() {
  local n
  n=$(sysctl -n hw.perflevel0.logicalcpu 2>/dev/null || sysctl -n hw.logicalcpu 2>/dev/null || echo 4)
  [ "$n" -ge 1 ] 2>/dev/null || n=4
  echo "$n"
}
