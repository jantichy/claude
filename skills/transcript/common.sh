#!/usr/bin/env bash
# Sdílené definice pro skill /transcript. Sourcuje se, nespouští.

MODELS_DIR="$HOME/.whisper-models"
VAD_MODEL="$MODELS_DIR/ggml-silero-v5.1.2.bin"
VAD_MODEL_URL="https://huggingface.co/ggml-org/whisper-vad/resolve/main/ggml-silero-v5.1.2.bin"
RATE_FILE="$MODELS_DIR/rate.json"

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
