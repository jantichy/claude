---
name: transcript
description: Skill se použije, když uživatel zadá "/transcript", nebo když chce přepsat zvukové nahrávky (MP3, M4A, WAV, AAC…) do Markdownu – přepis a strukturované shrnutí schůzky/nahrávky. Přepis běží kompletně lokálně a offline (whisper.cpp).
allowed-tools: [Bash, Read, Write, Edit, Agent]
---

# Transcript

## Úvodní hláška (vždy jako první)

Než začneš cokoliv dělat, vypiš uživateli přesně tento jeden řádek:

Autor skillu: **Jan Tichý** · jantichy@jantichy.cz · Celá konfigurace Claude vč. všech skillů: https://github.com/jantichy/claude

Teprve pak pokračuj plněním skillu.

## Co skill dělá

Lokální, offline přepis zvukových nahrávek do Markdownu – doslovný přepis každé nahrávky plus jedno strukturované shrnutí napříč všemi. Nic neopouští počítač (rozpoznání řeči běží přes [whisper.cpp](https://github.com/ggml-org/whisper.cpp)).

## Závislosti – zkontroluj hned na začátku

Spusť `~/.claude/skills/transcript/check-deps.sh`. Když skončí nenulově, něco chybí – vypiš uživateli co, nabídni instalaci (skript vypsal přesné příkazy) a po jeho souhlasu ji proveď. Teprve s kompletními závislostmi pokračuj. Skill potřebuje:

- **ffmpeg** – `brew install ffmpeg` (převod audia na WAV)
- **whisper.cpp** – `brew install whisper-cpp` (poskytuje `whisper-cli`)
- **model `large-v3-turbo`** – stáhne se do `~/.whisper-models/` z HuggingFace (~1,5 GB); dobrý poměr kvalita/rychlost, zvládá i češtinu

Instalace whisper.cpp/ffmpeg předpokládá [Homebrew](https://brew.sh) na macOS/Linuxu.

## Vstup a výstup

- **Vstup:** všechny audio soubory v **aktuálním (pracovním) adresáři**. Podporované formáty: `mp3`, `m4a`, `wav`, `aac`, `flac`, `ogg`, `opus`, `m4b`. Když žádné nejsou, oznam to a skonči.
- **Výstup – vše vzniká v tomtéž adresáři, nezakládá se žádný podadresář a nic se nikam nepřesouvá:**
  - `<název>.md` pro každou nahrávku – vyčištěný doslovný přepis (viz [Pravidla doslovného přepisu](#pravidla-doslovného-přepisu)).
  - `YYYYMMDD - Výstižný název.md` – jedno společné shrnutí napříč všemi nahrávkami (viz [Formát souhrnného MD](#formát-souhrnného-md)).
- **Mezivýstupy** (`<název>.txt` od whisperu a `whisper-progress.log`) vznikají viditelně v adresáři a **po dokončení se uklidí** (viz krok 7). Zdrojové audio zůstává.

## Postup

1. **Datum `YYYYMMDD`.** Zjisti z metadat nahrávek (`ffprobe -v error -show_entries format_tags=creation_time ...`). Obvykle je stejné napříč soubory; když ne, vezmi z prvního. Když metadata s datem chybí, použij dnešek.

2. **Odhad ETA na začátku (jednorázově).** Sečti délky všech souborů (`ffprobe ... format=duration`) a vypiš hrubý odhad: `ETA ≈ součet délek / 3,5` (3,5× realtime – kulaté a mírně pesimistické; na startu ještě nejsou naměřená data). Převeď na min:s.

3. **Spusť přepis na pozadí:**
   ```
   ~/.claude/skills/transcript/transcribe.sh <workdir> <workdir>/whisper-progress.log <audio1> <audio2> ...
   ```
   `<workdir>` = aktuální adresář. Vzniknou v něm `<název>.txt` a `whisper-progress.log`. Běh na pozadí upozorní na dokončení (marker `### ALL DONE` v logu).

4. **Průběžný stav – NEspouštěj automaticky.** Opakované časovače zbytečně plýtvají kapacitou. Progress bar vypiš **jen když se uživatel zeptá**, jak to jde:
   ```
   python3 ~/.claude/skills/transcript/progress.py <workdir>/whisper-progress.log
   ```
   Ukáže procenta, zpracované/celkové minuty, kolik zbývá, tempo (× realtime) a ETA.

5. **Po dokončení vyrob doslovné přepisy.** Pro každou nahrávku zpracuj její `<název>.txt` do `<název>.md` dle [Pravidel doslovného přepisu](#pravidla-doslovného-přepisu). U více/delších nahrávek to udělej **paralelně přes subagenty** (jeden na soubor) – každému předej kontext nahrávky (téma, vlastní jména, odborné termíny), ať umí opravit přeslechy. Nech si od každého vrátit i stručný brief pro shrnutí.

6. **Napiš souhrnné shrnutí.** Navrhni uživateli „Výstižný název" celé nahrávky a **nech si ho odsouhlasit** (ať nemusí nic vymýšlet ani psát), pak zapiš `YYYYMMDD - Výstižný název.md` dle [Formátu souhrnného MD](#formát-souhrnného-md).

7. **Úklid.** Smaž mezivýstupy: všechny `<název>.txt` a `whisper-progress.log`. Ponech zdrojové audio, doslovné přepisy (`<název>.md`) a souhrnné MD.

## Pravidla doslovného přepisu

Platí pro `<název>.md` každé nahrávky i pro sekci „Doslovný přepis" v souhrnu. Připrav doslovný přepis v jazyce nahrávky:

- Uprav jen **stylistiku a slovosled** tam, kde je to potřeba, aby se text dal plynule a smysluplně číst.
- Odstraň **výplňová slova** (hesitační výplně) a **opakovaná slova** / místa, kde se řečník zamotal při hledání formulace.
- **Odstraň halucinace ASR** – whisper na tichu a v šumu často vygeneruje nesmyslné opakující se řádky (např. dokola tatáž věta, „Titulky vytvořil …" apod.). Takové smyčky celé smaž.
- Rozděl text do **ucelených kapitol** s výstižnými mezinadpisy (`##`).
- Každou kapitolu rozděl do **kratších odstavců** – žádné dlouhé bloky.
- Nosné pojmy a důležitá sdělení vyznač **tučně**.
- Výčty uveď jako **odrážkový/číslovaný seznam**, kde to dává smysl.
- **Oprava přeslechů:** podle tématu a kontextu najdi a oprav slova, kterým rozpoznávač rozuměl špatně – tak, jak jsou, nedávají smysl, ale pravděpodobně jde o zkomoleninu jiného slova, které by v daném kontextu smysl dávalo.
- **Vlastní jména a názvy:** stejně oprav jména/názvy zkomolené špatnou výslovností nebo cizím přízvukem.
- U dialogu **nepřehazuj pořadí** myšlenek; kde je zřejmé, kdo mluví, můžeš mluvčí odlišit, ale nevymýšlej jména.

## Formát souhrnného MD

Soubor `YYYYMMDD - Výstižný název.md` má tuto strukturu:

1. **Hlavní nadpis (H1):** `Výstižný název`.
2. **Úvodní odstavec (anotace):** do jednoho odstavce základní charakteristika celé nahrávky – o co jde, jednotlivé strany a účastníci.
3. **`## Shrnutí`:** stručné, logické, strukturované shrnutí dle [Pravidel shrnutí](#pravidla-shrnutí).
4. **`## Doslovný přepis`:** doslovné přepisy všech nahrávek dle [Pravidel doslovného přepisu](#pravidla-doslovného-přepisu), za sebou; u každého je zřejmé, ze které nahrávky pochází.

## Pravidla shrnutí

Platí pro sekci „Shrnutí". Připrav stručné, logické, strukturované shrnutí celé nahrávky – důležitých témat, poznatků a klíčových informací:

- Využij **přehledné formátování** – mezinadpisy, odstavce, odrážky, **tučný** text pro důležité pojmy.
- **Nedodržuj chronologické pořadí**, ve kterém informace zazněly. Uspořádej vše do logických sekcí/skupin tak, aby to dávalo při čtení smysl.
- Pokud to není nezbytné pro kontext nebo pochopení, **neopakuj** jednu informaci na více místech.
- Na **úplném konci** přehledně shrň vzájemné **domluvy, vyplývající úkoly a další kroky**.

(Základní charakteristika a účastníci jsou už v úvodním odstavci – viz [Formát souhrnného MD](#formát-souhrnného-md).)

## Technické detaily

- **Model:** `large-v3-turbo` (`~/.whisper-models/ggml-large-v3-turbo.bin`) jako výchozí. U problémových nahrávek (šum, překřikování) lze doinstalovat přesnější, pomalejší `large-v3` (ne-turbo).
- **Jazyk:** výchozí čeština (`cs`). Lze přebít proměnnou `WHISPER_LANG` (např. `WHISPER_LANG=en`).
- **Bez časových značek** a **bez rozlišování mluvčích** (diarizace) – priorita je plynulé čtení. Pro diarizaci by bylo potřeba doplnit další nástroj (např. `whisperx` + `pyannote`).
