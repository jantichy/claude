#!/bin/bash
# Sestaví prezentaci a vykreslí náhledy: PDF, PNG po slajdech a přehled po čtyřech vedle sebe.
# Spuštění: bash ~/.claude/skills/deck/preview.sh <Prezentace.md>   (vypíše adresář s náhledy)
#
# Headless LibreOffice nevidí písma z ~/Library/Fonts, proto dostane vlastní profil s písmy šablony:
# Roboto se zkopíruje z ~/Library/Fonts, Playfair Display a Roboto Mono se stáhnou z google/fonts.
# Profil i náhledy jsou per zdroj, aby se dvě souběžná vykreslení nepraly o zámek LibreOffice.
set -e
SKILL=$(cd "$(dirname "$0")" && pwd -P)
[[ -n $1 && -f $1 ]] || { echo "Chybí zdroj prezentace: ${1:-(nezadán)}" >&2; exit 1; }
SRC=$(cd "$(dirname "$1")" && pwd -P)/$(basename "$1")
for tool in uv soffice pdftoppm magick; do
  command -v "$tool" >/dev/null || { echo "Chybí nástroj $tool" >&2; exit 1; }
done
TMP=${TMPDIR:-/tmp}
TMP=${TMP%/}
KEY=$(printf '%s' "$SRC" | shasum | cut -c1-8)
PROFILE=$TMP/deck-lo-$KEY
OUT=$TMP/deck-preview-$KEY
FONTS=$PROFILE/user/fonts

mkdir -p "$FONTS"
[[ -f $FONTS/Roboto-Bold.ttf ]] || cp ~/Library/Fonts/Roboto-{Regular,Bold}.ttf "$FONTS/"
[[ -f $FONTS/PlayfairDisplay.ttf ]] || curl -sSfL -o "$FONTS/PlayfairDisplay.ttf" \
  "https://raw.githubusercontent.com/google/fonts/main/ofl/playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf"
[[ -f $FONTS/RobotoMono.ttf ]] || curl -sSfL -o "$FONTS/RobotoMono.ttf" \
  "https://raw.githubusercontent.com/google/fonts/main/ofl/robotomono/RobotoMono%5Bwght%5D.ttf"

rm -rf "$OUT" && mkdir -p "$OUT"
uv run -q "$SKILL/build.py" "$SRC" "$OUT/deck.pptx" >/dev/null
cd "$OUT"
soffice "-env:UserInstallation=file://$PROFILE" --headless --convert-to pdf deck.pptx >/dev/null 2>&1
pdftoppm -r 40 -png deck.pdf p
magick montage p-*.png -tile 4x -geometry +4+4 -background '#888' sheet.png
shopt -s nullglob
pages=(p-*.png)
echo "$OUT (${#pages[@]} slajdů, přehled sheet.png)"
