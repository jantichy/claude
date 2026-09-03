#!/usr/bin/env bash
# Detekce jazyka nahrávky ještě před přepisem.
#
# Použití:
#   detect-lang.sh <audio> [model]     # model: turbo | large-v3 (výchozí turbo)
#
# Vypíše na stdout dvě hodnoty oddělené mezerou:  cs 0.993
# Exit 0 = detekováno, 1 = nepovedlo se (volající pak vezme výchozí jazyk).
#
# Whisper má jazyk zakódovaný v modelu a pozná ho ze zvuku dřív, než začne
# dekódovat slova (`-dl` skončí hned po detekci). Na Apple M1 to trvá ~7 s,
# z toho většinu zabere načtení modelu.
#
# Vzorek se bere ZPROSTŘED nahrávky. Začátky bývají pozdravy, ticho a šoupání
# židlí, takže detekce z prvních sekund je zbytečně nespolehlivá.

set -uo pipefail
export LC_ALL=C
HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source-path=SCRIPTDIR
# shellcheck source=common.sh
. "$HERE/common.sh"

AUDIO="${1:?použití: detect-lang.sh <audio> [model]}"
MODEL="$(model_file "${2:-turbo}")"
SAMPLE_S=30

[ -n "$MODEL" ] && [ -f "$MODEL" ] || exit 1
[ -f "$AUDIO" ] || exit 1

dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$AUDIO" 2>/dev/null)
[ -n "$dur" ] || exit 1

# Střed nahrávky; u krátkých souborů prostě od začátku.
start=$(awk -v d="$dur" -v s="$SAMPLE_S" 'BEGIN{ m = d/2 - s/2; print (m > 0 ? int(m) : 0) }')

# mktemp vyrobí soubor bez přípony; ffmpeg chce .wav, tak k němu vyrobíme
# druhé jméno a mažeme obě, ať po sobě nic nezůstane.
tmp_base=$(mktemp -t translang)
tmp="$tmp_base.wav"
trap 'rm -f "$tmp_base" "$tmp"' EXIT

ffmpeg -v error -y -ss "$start" -t "$SAMPLE_S" -i "$AUDIO" \
  -ar 16000 -ac 1 -c:a pcm_s16le "$tmp" 2>/dev/null || exit 1

out=$(whisper-cli -m "$MODEL" -l auto -dl -f "$tmp" 2>&1 | grep -o "auto-detected language: .*")
[ -n "$out" ] || exit 1

# "auto-detected language: cs (p = 0.993131)" -> pole 3 a 6 po odstranění závorek
echo "$out" | awk '{ gsub(/[()]/, "", $0); print $3, $6 }'
