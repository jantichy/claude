#!/usr/bin/env bash
# Přepis audio souborů whisperem (whisper.cpp). Vše vzniká v pracovním adresáři.
#
# Použití:
#   transcribe.sh <workdir> <log_file> <audio1> [<audio2> ...]
#
# Chování řídí proměnné prostředí:
#   WHISPER_MODEL   turbo | large-v3            (výchozí turbo)
#   WHISPER_LANG    kód jazyka                  (výchozí cs)
#   WHISPER_PROMPT  slovník jmen a termínů      (výchozí prázdný)
#   WHISPER_VAD     1 | 0 – detekce řeči        (výchozí 1)
#   WHISPER_KEEP_WAV 1 | 0 – nechat WAV vedle    (výchozí 0; diarizace ho potřebuje)
#   WHISPER_CHUNK_MIN  minuty                   (výchozí 0 = vypnuto)
#
# WHISPER_CHUNK_MIN je ZÁCHRANNÁ BRZDA, ne výchozí režim. Rozřeže nahrávku na
# úseky dané délky a každý přepíše zvlášť, čímž řeší dvě věci naráz:
#   1) halucinační smyčku – model začíná u každého úseku bez kontextu, takže se
#      opakující se text nemůže šířit dál,
#   2) selhání uprostřed dlouhé nahrávky – spadne-li jeden úsek, přeskočí se
#      a zbytek se přepíše (bez chunkingu se ztratí přepis celého souboru).
# Cena je dvojí a obojí je důvod, proč se to nezapíná samo: na každé hranici
# úseku vzniká řez uprostřed věty a model se načítá znovu u každého úseku.
# Kvůli tomu druhému se běh po úsecích nezapočítává do kalibrace tempa.
#
# Pro každý vstup vznikne <workdir>/<název>.txt a <workdir>/<název>.srt.
# SRT vzniká vždy, protože se z něj počítá podíl řeči; když ho volající nechce,
# smaže ho v úklidu.
#
# Do <log_file> se píše průběh, ze kterého čte progress.py:
#   ### DURATION N SECONDS       (délky souborů – pro odhad postupu)
#   ### START zaznam-N HH:MM:SS
#   [HH:MM:SS ...] segmenty       (píše whisper)
#   ### DONE zaznam-N HH:MM:SS
#   ### SPEECHSTAT N SPEECH_S TOTAL_S PERCENT   (podíl přepsaného zvuku,
#                                                NE výstup VAD – vyjde stejně i bez něj)
#   ### FAILED zaznam-N <důvod>   (běh pokračuje dalším souborem)
#   ### CHUNKING zaznam-N <z>     (jen s WHISPER_CHUNK_MIN: začíná běh po úsecích)
#   ### CHUNKFAILED zaznam-N <i>/<z>  (úsek se přeskočil, zbytek se přepsal dál)
#   ### CHUNKSTAT zaznam-N <ok>/<z>   (kolik úseků se povedlo – ohlas ztrátu)
#   ### NOCALIB <důvod>           (tempo tohoto běhu se do kalibrace nezapočítalo)
#   ### ELAPSED AUDIO_S WALL_S   (AUDIO_S = jen úspěšně přepsané soubory)
#   ### ALL DONE
#
# Do téhož logu píše i diarize.sh svoje ### DIARSTAT, ### DIARIZE ELAPSED
# a ### DIARIZE FAILED.
#
# Průběžný stav kdykoli:  python3 progress.py <log_file>

set -uo pipefail
# Česká locale by do čísel dala desetinnou čárku a rozbila awk i rate.py.
export LC_ALL=C
HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source-path=SCRIPTDIR
# shellcheck source=common.sh
. "$HERE/common.sh"

MODEL_KEY="${WHISPER_MODEL:-turbo}"
LANG_CODE="${WHISPER_LANG:-cs}"
PROMPT="${WHISPER_PROMPT:-}"
USE_VAD="${WHISPER_VAD:-1}"
KEEP_WAV="${WHISPER_KEEP_WAV:-0}"
CHUNK_MIN="${WHISPER_CHUNK_MIN:-0}"
# Překlep by jinak tiše spadl do normálního běhu – a to je u nápravy, kterou
# volající sahá po nefunkčním přepisu, ta nejhorší možná porucha.
case "$CHUNK_MIN" in
  *[!0-9]*|'')
    echo "WHISPER_CHUNK_MIN musí být celé číslo minut, dostal jsem '$CHUNK_MIN'." >&2
    exit 2 ;;
esac

MODEL="$(model_file "$MODEL_KEY")"
if [ -z "$MODEL" ] || [ ! -f "$MODEL" ]; then
  echo "Model '$MODEL_KEY' není k dispozici. Spusť check-deps.sh $MODEL_KEY" >&2
  exit 2
fi

WORKDIR="$1"; LOG="$2"; shift 2
: > "$LOG"

THREADS="$(n_threads)"

# Přepínače whisperu společné pro všechny soubory
# -ml 80 -sow: strop délky titulku a dělení po slovech. Bez -sow řeže whisper
# uprostřed slova („na přednáš“ / „ky, že jo“); s ním je text slovo za slovem
# totožný s během bez -ml, mění se jedině zalomení.
declare -a WOPTS=(-m "$MODEL" -l "$LANG_CODE" -t "$THREADS" -otxt -osrt -sns -np -ml 80 -sow)
[ -n "$PROMPT" ] && WOPTS+=(--prompt "$PROMPT" --carry-initial-prompt)
if [ "$USE_VAD" = "1" ] && [ -f "$VAD_MODEL" ]; then
  # Práh níž než výchozích 0.50 a delší doběh, ať VAD neuřízne tiché mluvčí.
  WOPTS+=(--vad -vm "$VAD_MODEL" -vt 0.35 -vp 200)
fi

# Posune časové značky v SRT o offset a přečísluje segmenty od zadaného čísla.
# Číslo segmentu se pozná podle pozice (první řádek po prázdném), ne podle tvaru –
# samostatné číslo může být i text repliky.
shift_srt() {
  awk -v off="$2" -v n="$3" '
    BEGIN { expect_num = 1 }
    /^\r?$/ { print; expect_num = 1; next }
    expect_num && /^[0-9]+\r?$/ { print n++; expect_num = 0; next }
    /-->/ {
      split($1, a, /[:,]/); split($3, b, /[:,]/)
      s = a[1]*3600 + a[2]*60 + a[3] + off
      e = b[1]*3600 + b[2]*60 + b[3] + off
      printf "%02d:%02d:%02d,%s --> %02d:%02d:%02d,%s\n",
             s/3600, (s%3600)/60, s%60, a[4], e/3600, (e%3600)/60, e%60, b[4]
      expect_num = 0; next
    }
    { print; expect_num = 0 }
  ' "$1"
}

# Přepis po úsecích. Vrací 0, když se přepsal aspoň jeden úsek.
# Selhaný úsek se přeskočí – právě kvůli tomu tenhle režim existuje.
transcribe_chunked() {
  local wav="$1" outbase="$2" idx="$3" dur="$4"
  local len=$((CHUNK_MIN * 60))
  local total start i=0 ok=0 failed=0 counter=1 cdir
  total=$(awk -v d="$dur" -v l="$len" 'BEGIN{ printf "%d", (d + l - 1) / l }')
  # Neznámá nebo nulová délka by dala nula úseků a tichý prázdný výstup.
  [ "$total" -ge 1 ] 2>/dev/null || total=1
  cdir=$(mktemp -d "${TMPDIR:-/tmp}/transcript-chunks.XXXXXX") || return 1

  # Sklápí se do dočasných souborů a na cílové se sahá až po úspěchu. Jinak by
  # neúspěšný druhý běh smazal přepis, který vznikl při tom prvním – a právě
  # jako druhý běh se tenhle režim používá.
  local out_txt="$cdir/all.txt" out_srt="$cdir/all.srt"
  : > "$out_txt"
  : > "$out_srt"
  echo "### CHUNKING zaznam-$idx $total" >> "$LOG"

  while [ "$i" -lt "$total" ]; do
    start=$((i * len))
    i=$((i + 1))
    # -ss před -i seekuje rychle; WAV je PCM, takže -c copy nic nepřekóduje.
    if ! ffmpeg -y -ss "$start" -t "$len" -i "$wav" -c copy "$cdir/c.wav" -loglevel error 2>>"$LOG"; then
      echo "### CHUNKFAILED zaznam-$idx $i/$total" >> "$LOG"
      failed=$((failed + 1))
      continue
    fi
    if whisper-cli "${WOPTS[@]}" -f "$cdir/c.wav" -of "$cdir/c" >> "$LOG" 2>&1; then
      [ -f "$cdir/c.txt" ] && cat "$cdir/c.txt" >> "$out_txt"
      if [ -f "$cdir/c.srt" ]; then
        shift_srt "$cdir/c.srt" "$start" "$counter" >> "$out_srt"
        counter=$(( counter + $(grep -c -- '-->' "$cdir/c.srt") ))
      fi
      ok=1
    else
      echo "### CHUNKFAILED zaznam-$idx $i/$total" >> "$LOG"
      failed=$((failed + 1))
    fi
    rm -f "$cdir/c.wav" "$cdir/c.txt" "$cdir/c.srt"
  done

  # VAD si k úseku přidává doběh (-vp 200), takže poslední segment úseku může
  # začít až za jeho hranicí – a první segment dalšího úseku pak začíná o setiny
  # dřív než on. Na 31minutové nahrávce to nastalo jednou ze 702 segmentů.
  # Přehrávači je to jedno, ale merge.py řadí a přiřazuje podle času, tak ať
  # jsou značky neklesající. Vzor musí být ukotvený na tvar časovky: samotné
  # „-->“ se vyskytne i v textu repliky a ten se nesmí přepsat.
  awk '
    function fmt(t,   h, m, sec, ms) {
      h = int(t / 3600); m = int((t % 3600) / 60); sec = int(t % 60)
      ms = int((t - int(t)) * 1000 + 0.5)
      return sprintf("%02d:%02d:%02d,%03d", h, m, sec, ms)
    }
    /^[0-9][0-9]:[0-9][0-9]:[0-9][0-9],[0-9][0-9][0-9] --> [0-9][0-9]:[0-9][0-9]:[0-9][0-9],[0-9][0-9][0-9]/ {
      split($1, a, /[:,]/); split($3, b, /[:,]/)
      s = a[1]*3600 + a[2]*60 + a[3] + a[4]/1000
      e = b[1]*3600 + b[2]*60 + b[3] + b[4]/1000
      # Posunout začátek na konec předchozího titulku, ale jen když tím titulek
      # nezmizí – drobný překryv je pořád lepší než nulová délka.
      if (s < prev_end && prev_end < e) s = prev_end
      prev_end = e
      print fmt(s) " --> " fmt(e); next
    }
    { print }
  ' "$out_srt" > "$out_srt.fixed" && mv "$out_srt.fixed" "$out_srt"

  # Kolik úseků se povedlo. Volající to hlásí uživateli – soubor s přeskočeným
  # úsekem dostane `### DONE` jako každý jiný, takže bez tohohle by se ztráta
  # poznala jedině z podílu přepsaného zvuku.
  echo "### CHUNKSTAT zaznam-$idx $((total - failed))/$total" >> "$LOG"

  if [ "$ok" = "1" ]; then
    mv "$out_txt" "$outbase.txt"
    mv "$out_srt" "$outbase.srt"
  fi
  rm -rf "$cdir"
  [ "$ok" = "1" ]
}

# Součet délek řečových úseků v SRT – kolik zvuku se opravdu přepisovalo.
speech_seconds() {
  awk -F' --> ' '
    /-->/ {
      split($1, a, /[:,]/); split($2, b, /[:,]/)
      s = a[1]*3600 + a[2]*60 + a[3] + a[4]/1000
      e = b[1]*3600 + b[2]*60 + b[3] + b[4]/1000
      if (e > s) total += e - s
    }
    END { printf "%.1f", total + 0 }
  ' "$1" 2>/dev/null || echo 0
}

# 1) délky do logu
n=0
declare -a DURATIONS=()
for f in "$@"; do
  n=$((n+1))
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f" 2>/dev/null)
  [ -n "$d" ] || d=0
  DURATIONS+=("$d")
  echo "### DURATION $n $d" >> "$LOG"
done

# 2) přepis – chyba jednoho souboru neshodí zbytek běhu
wall_start=$(date +%s)
n=0
# Do kalibrace jde jen zvuk, který se opravdu přepsal. Bez toho by selhaný běh
# (hodina zvuku, pár sekund běhu) zapsal tempo v řádu stovek × realtime.
ok_audio=0
for f in "$@"; do
  n=$((n+1))
  base=$(basename "$f"); base="${base%.*}"
  # Skrytý název jen u dočasného WAV; ten, který má přežít pro diarizaci, je vidět.
  if [ "$KEEP_WAV" = "1" ]; then
    wav="$WORKDIR/$base.wav"
    # Vstup už může BÝT tenhle soubor (nahrávka je WAV a leží v pracovním adresáři).
    # Bez téhle pojistky by ffmpeg přepisoval vlastní vstup a nevznikl by přepis.
    [ "$wav" = "$f" ] && wav="$WORKDIR/$base.16k.wav"
  else
    wav="$WORKDIR/.${base}.tmp.wav"
  fi

  file_dur="${DURATIONS[$((n-1))]}"

  if ! ffmpeg -y -i "$f" -ar 16000 -ac 1 -c:a pcm_s16le "$wav" >>"$LOG" 2>&1; then
    echo "### FAILED zaznam-$n prevod-na-wav" >> "$LOG"
    rm -f "$wav"
    continue
  fi

  echo "### START zaznam-$n $(date +%H:%M:%S)" >> "$LOG"
  if [ "$CHUNK_MIN" -gt 0 ] 2>/dev/null; then
    transcribe_chunked "$wav" "$WORKDIR/$base" "$n" "$file_dur"
    rc=$?
  else
    whisper-cli "${WOPTS[@]}" -f "$wav" -of "$WORKDIR/$base" >> "$LOG" 2>&1
    rc=$?
  fi
  if [ "$rc" -eq 0 ]; then
    echo "### DONE zaznam-$n $(date +%H:%M:%S)" >> "$LOG"
    ok_audio=$(awk -v a="$ok_audio" -v b="$file_dur" 'BEGIN{printf "%.3f", a+b}')
    srt="$WORKDIR/$base.srt"
    if [ -f "$srt" ]; then
      sp=$(speech_seconds "$srt")
      pct=$(awk -v s="$sp" -v d="$file_dur" 'BEGIN{ printf "%.0f", (d>0 ? 100*s/d : 0) }')
      echo "### SPEECHSTAT $n $sp $file_dur $pct" >> "$LOG"
    fi
  else
    echo "### FAILED zaznam-$n whisper" >> "$LOG"
  fi
  [ "$KEEP_WAV" = "1" ] || rm -f "$wav"
done
wall=$(( $(date +%s) - wall_start ))

echo "### ELAPSED $ok_audio $wall" >> "$LOG"
# Běh po úsecích se do kalibrace neposílá. Načítá model znovu u každého úseku,
# takže jeho tempo je nafouklé o něco, co v normálním běhu není – EWMA by tím
# stáhla odhad dolů i pro všechny běžné přepisy.
if [ "$CHUNK_MIN" -gt 0 ]; then
  echo "### NOCALIB beh-po-usecich" >> "$LOG"
else
  python3 "$HERE/rate.py" update "$MODEL_KEY" "$ok_audio" "$wall" 2>/dev/null || true
fi
echo "### ALL DONE" >> "$LOG"
