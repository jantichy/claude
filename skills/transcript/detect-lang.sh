#!/usr/bin/env bash
# Detekce jazyka nahrávky ještě před přepisem.
#
# Použití:
#   detect-lang.sh <audio> [model]     # model: turbo | large-v3 (výchozí turbo)
#
# Vypíše na stdout:  cs 0.993              (všechny vzorky se shodly)
#              nebo:  en 0.999 mixed:cs,en  (nahrávka je dvojjazyčná)
# Exit 0 = detekováno, 1 = nepovedlo se (volající pak vezme výchozí jazyk).
#
# Whisper má jazyk zakódovaný v modelu a pozná ho ze zvuku dřív, než začne
# dekódovat slova (`-dl` skončí hned po detekci). Na Apple M1 to trvá ~7 s na
# vzorek, z toho většinu zabere načtení modelu.
#
# Vzorkuje se na TŘECH místech (čtvrtina, půlka, tři čtvrtiny). Jeden vzorek
# ze začátku je nespolehlivý, protože začátky bývají pozdravy a šoupání židlí;
# a jeden vzorek zprostředka zase nepozná schůzku, která se v půlce přepne do
# jiného jazyka. Whisper bere jeden jazyk na běh, takže takovou nahrávku
# nespraví – ale je rozdíl mezi špatným přepisem a špatným přepisem, o kterém
# se ví. U nahrávek kratších než dva vzorky stačí jeden vzorek zprostředka.

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

# U krátké nahrávky by se tři vzorky překrývaly, takže nepřinesou nic navíc.
if awk -v d="$dur" -v s="$SAMPLE_S" 'BEGIN{ exit !(d < 4*s) }'; then
  POSITIONS="0.5"
else
  POSITIONS="0.25 0.5 0.75"
fi

# mktemp vyrobí soubor bez přípony; ffmpeg chce .wav, tak k němu vyrobíme
# druhé jméno a mažeme obě, ať po sobě nic nezůstane.
tmp_base=$(mktemp -t translang)
tmp="$tmp_base.wav"
trap 'rm -f "$tmp_base" "$tmp"' EXIT

langs=""
best_lang=""
best_p=0

for pos in $POSITIONS; do
  start=$(awk -v d="$dur" -v s="$SAMPLE_S" -v p="$pos" \
    'BEGIN{ m = d*p - s/2; print (m > 0 ? int(m) : 0) }')

  ffmpeg -v error -y -ss "$start" -t "$SAMPLE_S" -i "$AUDIO" \
    -ar 16000 -ac 1 -c:a pcm_s16le "$tmp" 2>/dev/null || continue

  out=$(whisper-cli -m "$MODEL" -l auto -dl -f "$tmp" 2>&1 | grep -o "auto-detected language: .*")
  [ -n "$out" ] || continue

  # "auto-detected language: cs (p = 0.993131)" -> kód jazyka a pravděpodobnost
  lang=$(echo "$out" | awk '{ gsub(/[()]/, "", $0); print $3 }')
  p=$(echo "$out" | awk '{ gsub(/[()]/, "", $0); print $6 }')
  [ -n "$lang" ] || continue
  [ -n "$p" ] || p=0

  langs="$langs $lang"
  if awk -v a="$p" -v b="$best_p" 'BEGIN{ exit !(a > b) }'; then
    best_lang="$lang"
    best_p="$p"
  fi
done

[ -n "$best_lang" ] || exit 1

uniq_langs=$(echo "$langs" | tr ' ' '\n' | grep -v '^$' | sort -u | paste -sd, -)
case "$uniq_langs" in
  *,*) echo "$best_lang $best_p mixed:$uniq_langs" ;;
  *)   echo "$best_lang $best_p" ;;
esac
