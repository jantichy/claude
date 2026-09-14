#!/usr/bin/env bash
# Spojí několik nahrávek do jedné. Používá se, když je jedna schůzka rozřezaná
# do víc souborů (diktafon se zastavil, nahrávání se restartovalo) – pak se má
# přepisovat jako jedna dlouhá nahrávka, ne jako několik různých.
#
# Použití:
#   join.sh <workdir> <název> <audio1> <audio2> ...
#
# Vyrobí <workdir>/<název>.wav (16 kHz mono PCM) a vypíše jeho cestu a délku.
#
# POŘADÍ SOUBORŮ DRŽÍ VOLAJÍCÍ. Skript je spojí přesně v tom pořadí, v jakém
# je dostane, a nijak je nepřerovnává – špatné pořadí se totiž nepozná jinak
# než přečtením přepisu, kde si pak části nesedí.
#
# Proč se překóduje na WAV a nespojuje se beze ztráty (-c copy) jako ve
# split.sh: části můžou být každá z jiného zdroje (m4a z diktafonu, mp4 z
# Meetu), a concat demuxer s -c copy buď selže, nebo vyrobí soubor s vadnými
# časy. 16 kHz mono PCM je navíc přesně to, co whisper stejně potřebuje, takže
# se tím nic nepřidává – ztrátový vstup se překóduje jednou, ne dvakrát.

set -uo pipefail
export LC_ALL=C

WORKDIR="${1:?použití: join.sh <workdir> <název> <audio1> <audio2> ...}"
NAME="${2:?použití: join.sh <workdir> <název> <audio1> <audio2> ...}"
shift 2

[ -d "$WORKDIR" ] || { echo "Adresář '$WORKDIR' neexistuje." >&2; exit 1; }
[ "$#" -ge 2 ] || { echo "Spojovat má smysl aspoň dvě nahrávky, dostal jsem $#." >&2; exit 1; }

case "$NAME" in
  */*|.|..|'') echo "Název '$NAME' není jméno souboru." >&2; exit 1 ;;
esac

OUT="$WORKDIR/$NAME.wav"
# ffmpeg níž běží s -y, takže by existující soubor přepsal bez ptaní.
[ -e "$OUT" ] && { echo "Soubor '$OUT' už existuje – smaž ho, nebo zvol jiný název." >&2; exit 1; }

for f in "$@"; do
  [ -f "$f" ] || { echo "Nahrávka '$f' neexistuje." >&2; exit 1; }
done

TMP=$(mktemp -d "${TMPDIR:-/tmp}/transcript-join.XXXXXX") || exit 1
trap 'rm -rf "$TMP"' EXIT

# Převod po jednom, ne jedním filter_complexem: takhle je vidět, KTERÁ část
# selhala. U videa se tím zároveň zahodí obraz a zbude zvuková stopa.
LIST="$TMP/list.txt"
: > "$LIST"
i=0
SUM=0
for f in "$@"; do
  i=$((i+1))
  part="$TMP/$i.wav"
  if ! ffmpeg -y -i "$f" -ar 16000 -ac 1 -c:a pcm_s16le "$part" -loglevel error; then
    echo "Část $i ('$f') se nepovedlo převést – má vůbec zvukovou stopu?" >&2
    exit 1
  fi
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$part" 2>/dev/null)
  [ -n "$d" ] || { echo "Nešlo zjistit délku části $i ('$f')." >&2; exit 1; }
  SUM=$(awk -v a="$SUM" -v b="$d" 'BEGIN{ printf "%.3f", a + b }')
  # Apostrof v cestě by concat list rozbil; demuxer ho čeká zapsaný jako '\''.
  printf "file '%s'\n" "$(printf '%s' "$part" | sed "s/'/'\\\\''/g")" >> "$LIST"
done

if ! ffmpeg -y -f concat -safe 0 -i "$LIST" -c copy "$OUT" -loglevel error; then
  echo "Spojení nahrávek selhalo." >&2
  rm -f "$OUT"
  exit 1
fi

# Vlastní výstup se přečte zpátky: spojení, které tiše přijde o část, by se
# jinak poznalo až jako záhadně chybějící kus přepisu.
GOT=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT" 2>/dev/null)
[ -n "$GOT" ] || { echo "Spojený soubor '$OUT' se nedá přečíst." >&2; rm -f "$OUT"; exit 1; }
if awk -v g="$GOT" -v s="$SUM" 'BEGIN{ exit !((g - s > 1) || (s - g > 1)) }'; then
  printf 'Spojený soubor má %.3f s, ale části dávají %.3f s – nesedí to, nespoléhej na něj.\n' "$GOT" "$SUM" >&2
  rm -f "$OUT"
  exit 1
fi

echo "$OUT"
printf '%.3f\n' "$GOT"
