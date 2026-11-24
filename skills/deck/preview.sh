#!/bin/zsh
# Sestaví prezentaci a vykreslí náhledy: PDF, PNG po slajdech a přehled po čtyřech vedle sebe.
# Spuštění: zsh ~/.claude/skills/deck/preview.sh <Prezentace.md>   (vypíše adresář s náhledy)
#
# Headless LibreOffice nevidí písma z ~/Library/Fonts, proto dostane vlastní profil s písmy šablony:
# Roboto se zkopíruje z ~/Library/Fonts, Playfair Display a Roboto Mono se stáhnou z google/fonts.
# Profil i náhledy jsou per zdroj, aby se dvě souběžná vykreslení nepraly o zámek LibreOffice.
set -e
SKILL=${0:A:h}
[[ -n $1 && -f $1 ]] || { print -u2 "Chybí zdroj prezentace: ${1:-(nezadán)}"; exit 1; }
SRC=${1:A}
for tool in uv soffice pdftoppm magick; do
  command -v $tool >/dev/null || { print -u2 "Chybí nástroj $tool"; exit 1; }
done
TMP=${TMPDIR:-/tmp}
KEY=$(print -rn -- $SRC | shasum | cut -c1-8)
PROFILE=$TMP/deck-lo-$KEY
OUT=$TMP/deck-preview-$KEY
FONTS=$PROFILE/user/fonts

mkdir -p $FONTS
[[ -f $FONTS/Roboto-Bold.ttf ]] || cp ~/Library/Fonts/Roboto-{Regular,Bold}.ttf $FONTS/
[[ -f $FONTS/PlayfairDisplay.ttf ]] || curl -sSfL -o $FONTS/PlayfairDisplay.ttf \
  "https://raw.githubusercontent.com/google/fonts/main/ofl/playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf"
[[ -f $FONTS/RobotoMono.ttf ]] || curl -sSfL -o $FONTS/RobotoMono.ttf \
  "https://raw.githubusercontent.com/google/fonts/main/ofl/robotomono/RobotoMono%5Bwght%5D.ttf"

rm -rf $OUT && mkdir -p $OUT
uv run -q $SKILL/build.py $SRC $OUT/deck.pptx >/dev/null
cd $OUT
soffice -env:UserInstallation=file://$PROFILE --headless --convert-to pdf deck.pptx >/dev/null 2>&1
pdftoppm -r 40 -png deck.pdf p
magick montage p-*.png -tile 4x -geometry +4+4 -background '#888' sheet.png
echo "$OUT ($(ls p-*.png | wc -l | tr -d ' ') slajdů, přehled sheet.png)"
