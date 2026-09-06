#!/usr/bin/env bash
# Rozřízne nahrávku na dvě části v zadaném čase. Používá se u dvojjazyčné
# nahrávky, kde se každá část přepisuje se svým jazykem (whisper bere jeden
# jazyk na běh).
#
# Použití:
#   split.sh <workdir> <audio> <zlom>       # zlom ve tvaru MM:SS nebo v sekundách
#
# Vyrobí <workdir>/<název>-1.<přípona> a <název>-2.<přípona> a vypíše jejich
# cesty, každou na jeden řádek. Kóduje se beze ztráty (-c copy), takže je to
# rychlé a nezhoršuje to zvuk před přepisem.
#
# Zlom drží uživatel: skript umí nahrávku rozříznout, ale ne poznat kde.

set -uo pipefail
export LC_ALL=C

WORKDIR="${1:?použití: split.sh <workdir> <audio> <zlom>}"
AUDIO="${2:?použití: split.sh <workdir> <audio> <zlom>}"
CUT="${3:?použití: split.sh <workdir> <audio> <zlom>}"

[ -f "$AUDIO" ] || { echo "Nahrávka '$AUDIO' neexistuje." >&2; exit 1; }
[ -d "$WORKDIR" ] || { echo "Adresář '$WORKDIR' neexistuje." >&2; exit 1; }

# MM:SS i HH:MM:SS převedeme na sekundy, ať se dá počítat s délkou.
case "$CUT" in
  *:*) CUT_S=$(awk -F: '{ s=0; for (i=1; i<=NF; i++) s = s*60 + $i; print s }' <<<"$CUT") ;;
  *)   CUT_S="$CUT" ;;
esac

DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$AUDIO" 2>/dev/null)
[ -n "$DUR" ] || { echo "Nešlo zjistit délku nahrávky." >&2; exit 1; }

# Zlom mimo nahrávku by vyrobil prázdnou druhou část, a ta by se poznala až
# jako záhadně prázdný přepis.
if awk -v c="$CUT_S" -v d="$DUR" 'BEGIN{ exit !(c <= 0 || c >= d) }'; then
  printf 'Zlom %s s je mimo nahrávku (délka %.0f s).\n' "$CUT_S" "$DUR" >&2
  exit 1
fi

BASE=$(basename "$AUDIO"); EXT="${BASE##*.}"; BASE="${BASE%.*}"
OUT1="$WORKDIR/$BASE-1.$EXT"
OUT2="$WORKDIR/$BASE-2.$EXT"

ffmpeg -y -i "$AUDIO" -t "$CUT_S" -c copy "$OUT1" -loglevel error || exit 1
ffmpeg -y -ss "$CUT_S" -i "$AUDIO" -c copy "$OUT2" -loglevel error || exit 1

echo "$OUT1"
echo "$OUT2"
