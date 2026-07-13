#!/usr/bin/env bash
# Kontrola závislostí pro skill /transcript.
# Vypíše, co je k dispozici a co chybí, a jak chybějící doinstalovat.
# Exit 0 = vše připraveno, 1 = něco chybí.
set -u

MODEL="$HOME/.whisper-models/ggml-large-v3-turbo.bin"
MODEL_URL="https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo.bin"
missing=0

echo "Kontrola závislostí skillu /transcript:"

if command -v ffmpeg >/dev/null 2>&1; then
  echo "  ✓ ffmpeg"
else
  echo "  ✗ ffmpeg — chybí"
  missing=1
fi

if command -v whisper-cli >/dev/null 2>&1; then
  echo "  ✓ whisper.cpp (whisper-cli)"
else
  echo "  ✗ whisper.cpp (whisper-cli) — chybí"
  missing=1
fi

if [ -f "$MODEL" ]; then
  echo "  ✓ model large-v3-turbo"
else
  echo "  ✗ model large-v3-turbo — chybí ($MODEL)"
  missing=1
fi

if [ "$missing" -eq 1 ]; then
  echo ""
  echo "Chybějící části nainstaluj takto:"
  command -v ffmpeg      >/dev/null 2>&1 || echo "  brew install ffmpeg"
  command -v whisper-cli >/dev/null 2>&1 || echo "  brew install whisper-cpp"
  [ -f "$MODEL" ] || echo "  mkdir -p ~/.whisper-models && curl -L -o \"$MODEL\" \"$MODEL_URL\""
  echo ""
  echo "(whisper.cpp a ffmpeg jsou dostupné přes Homebrew — https://brew.sh)"
  exit 1
fi

echo "Vše připraveno."
exit 0
