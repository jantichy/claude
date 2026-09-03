---
name: transcript
description: Skill se použije, když uživatel zadá "/transcript", nebo když chce přepsat zvukové nahrávky (MP3, M4A, WAV, AAC…) do Markdownu – přepis a strukturované shrnutí schůzky/nahrávky. Přepis běží kompletně lokálně a offline (whisper.cpp).
---

# Transcript

## Co skill dělá

Lokální, offline přepis zvukových nahrávek do Markdownu. Nic neopouští počítač (rozpoznání řeči běží přes [whisper.cpp](https://github.com/ggml-org/whisper.cpp)).

Skill se **nespouští s přepínači**. Volá se cestou k souboru a volným popisem:

```
/transcript ~/Desktop/schuzka.m4a Přepiš mi schůzku s Janou Novákovou nad nastavením intranetu
```

Ten volný popis není dekorace. Vytáhneš z něj jména a názvy do slovníku (krok 3), takže **čím konkrétnější popis, tím míň zkomolených jmen**.

Než se pustíš do práce, projdeš s uživatelem krátkého průvodce. Teprve pak se přepisuje.

## Vstup a výstup

- **Vstup:** soubory zadané v promptu. Když prompt žádný soubor neuvádí, vezmi všechny audio soubory v aktuálním adresáři. Podporované formáty: `mp3`, `m4a`, `wav`, `aac`, `flac`, `ogg`, `opus`, `m4b`. Když nenajdeš nic, oznam to a skonči.
- **Výstup – vše vzniká v adresáři vstupní nahrávky, nezakládá se žádný podadresář a nic se nikam nepřesouvá:**
  - `<název>.md` – vyčištěný doslovný přepis (viz [Pravidla doslovného přepisu](#pravidla-doslovného-přepisu)),
  - `<název>.srt` – tentýž obsah s časovými značkami, syrový z whisperu,
  - `<název>.vtt` – titulky se značkou `<v Jméno>`, protože SRT pole pro mluvčího nemá. Vzniká **vedle** SRT, jen s rozlišením mluvčích,
  - `<název>.json` – strojově čitelné úseky s časem, mluvčím a textem. Taky jen s rozlišením mluvčích,
  - `YYYYMMDD - Výstižný název.md` – jedno společné shrnutí napříč všemi nahrávkami (viz [Formát souhrnného MD](#formát-souhrnného-md)).

  Které z nich vzniknou, vybere uživatel v průvodci.
- **Mezivýstupy** vznikají viditelně v adresáři a **po dokončení se uklidí** (viz krok 10): `<název>.txt` od whisperu, `.transcript-glossary.md`, `whisper-progress.log` a při rozlišování mluvčích navíc `<název>.wav` a `<název>.diarization.json`. Zdrojové audio zůstává.

  **Bez rozlišování mluvčích žádný viditelný WAV nevzniká.** `transcribe.sh` si ho v tom případě pojmenuje skrytě (`.<název>.tmp.wav`) a smaže ho hned po zpracování každé nahrávky, ne až v úklidu.

---

## Postup

### 1. Zjisti si fakta o vstupu

Ještě než se na cokoli zeptáš, potřebuješ délku a datum – bez délky neumíš nabídnout odhady časů v prvním kroku průvodce.

```bash
ffprobe -v error -show_entries format=duration -of csv=p=0 <audio>
ffprobe -v error -show_entries format_tags=creation_time -of csv=p=0 <audio>
```

Datum `YYYYMMDD` vezmi z metadat. Obvykle je stejné napříč soubory; když ne, vezmi z prvního. Když metadata s datem chybí, použij dnešek.

#### Zjisti jazyk nahrávky

```bash
<skill>/detect-lang.sh <audio>          # vypíše např.:  cs 0.993
```

Whisper má jazyk zakódovaný v modelu a pozná ho ze zvuku dřív, než začne dekódovat slova. Vzorek se bere **zprostřed** nahrávky, protože začátky bývají pozdravy a šoupání židlí. Trvá to jednotky sekund, takže se to dělá vždycky.

Podle jistoty se zachovej takhle:

| Výsledek | Co udělej |
|---|---|
| jistota ≥ 0,9, jazyk `cs` | **neptej se a nic nehlas**, jeď dál |
| jistota ≥ 0,9, jiný jazyk | **neptej se, ale řekni to nahlas**: „Detekoval jsem angličtinu, přepisuji anglicky.“ Kdo nesouhlasí, ozve se |
| jistota < 0,9 | **teprve tady se zeptej**, s detekovaným jazykem jako první možností |
| skript selhal | vezmi výchozí `cs` a řekni, že detekce neproběhla |

Jazyk pak předej jako `WHISPER_LANG` v kroku 6 a **zapiš ho do `.transcript-glossary.md`**. Neurčuje totiž jen rozpoznávání, ale i to, podle jakých pravidel se v kroku 9 opravuje pravopis a v jakém jazyce vzniká shrnutí.

**Co detekce nevyřeší:** dvojjazyčnou schůzku. Whisper bere jeden jazyk na běh, takže když se v půlce přepne z češtiny do angličtiny, druhá polovina dopadne špatně. Detekce to nezhorší, ale ani nespraví. Když to na nahrávce poznáš, řekni to uživateli.

### 2. Průvodce, krok první: model

Spočítej odhad běhu pro obě varianty. Tempo drží `rate.py`, který se sám kalibruje podle skutečnosti:

```bash
python3 <skill>/rate.py eta turbo    <délka_v_sekundách>
python3 <skill>/rate.py eta large-v3 <délka_v_sekundách>
```

Zeptej se přes `AskUserQuestion`. **První možnost je vždy ta nejpravděpodobnější**, aby stačil Enter:

| Pořadí | Label | Description |
|---|---|---|
| 1. | `Turbo · ~M:SS` | Výchozí volba. Rychlé, na běžnou mluvu stejně dobré. Se slovníkem jmen zvládne i vlastní jména. |
| 2. | `large-v3 · ~M:SS` | Zhruba 3× pomalejší. Sáhni po něm u špatného zvuku, překřikování nebo když na přesnosti jmen záleží víc než na čase. |

Odhady dosaď skutečné, ne zástupné. Když nahrávek zpracováváš víc, počítej ze součtu délek.

### 3. Průvodce, krok druhý: slovník jmen

**Tohle je nejcennější krok celého skillu.** Whisper dostane seznam vlastních jmen a termínů předem (`--prompt`) a přestane je komolit už při rozpoznávání. Oprava dodatečně je principiálně slabší, protože vymyšlená oprava vypadá stejně věrohodně jako správná.

Návrhy sestav ze tří zdrojů:

1. **volný popis v promptu** – jména, firmy a produkty, které uživatel sám napsal,
2. **kontext projektu**, ve kterém běžíš – `CLAUDE.md`, `docs/`, `README.md`, názvy v `content/`,
3. **předchozí komunikace v téhle session**.

Rozděl je do **tří domén** a nabídni je jako jednu otázku s `multiSelect: true`. Konkrétní termíny vypiš v `description` každé možnosti, ať uživatel vidí, co odsouhlasuje:

| Pořadí | Label | Co do ní patří |
|---|---|---|
| 1. | `Jména lidí` | účastníci, kolegové, zmínění lidé |
| 2. | `Značky, produkty, weby` | firmy, nástroje, domény, názvy prostorů |
| 3. | `Odborné termíny` | žargon oboru, interní pojmy, zkratky |

Volbu „Other“ doplní `AskUserQuestion` samo – tudy uživatel dopíše, co jsi netrefil.

Prázdnou skupinu vůbec nenabízej. Když nemáš návrh ani do jedné, otázku přeskoč a zeptej se rovnou na vlastní termíny.

#### Rešerši dělej naplno, do promptu dej málo

Tyhle dvě věci se pletou, a je to rozdíl mezi dobrým a špatným výsledkem.

**Rešerši dělej naplno.** Vytěž ze zdrojů úplně všechno – klidně stovky jmen, názvů, zkratek a interních pojmů. Nic nezahazuj.

**Do `WHISPER_PROMPT` dej nejvýš deset položek**, seřazených podle důležitosti, nejdůležitější první. Whisperův initial prompt má **klesající účinnost směrem k pozdějším položkám**: naměřeno na 31minutové české schůzce – slovník o osmi termínech opravil sledované místní jméno 6× ze 6, tentýž běh se slovníkem o jednadvaceti termínech, kde bylo totéž jméno až páté, spadl na 0 ze 4. Delší seznam je horší než kratší, ne lepší.

Vybírej podle toho, co v nahrávce **opravdu zazní často a co se snadno komolí**. Obecná slova, která model umí sám, do promptu nepatří.

Vybraných deset slep čárkami do jednoho řetězce a předej jako `WHISPER_PROMPT`.

#### Zbytek rešerše si ulož

Všechno ostatní, co jsi našel, zapiš do `<workdir>/.transcript-glossary.md`:

```markdown
# Kontextový slovník – <název nahrávky>

## V promptu whisperu (10)
Nazev.cz, Značka, interní pojem, místní jméno, …

## Jména lidí
Jana Nováková, Petr Svoboda, …

## Značky, produkty, weby, místa
Nazev.cz, Značka, s. r. o., …

## Odborné a interní termíny
zkratky oboru, interní pojmy, názvy rolí a útvarů, …

## Zdroje
prompt / docs/structure.md / session
```

Tenhle soubor je vstup pro čištění v kroku 9. **Deset položek stačí whisperu, ale tobě při čištění ne** – tam potřebuješ úplný kontext, abys poznal, co je zkomolenina a co interní žargon. Bez něj hádáš.

### 4. Průvodce, krok třetí: co má vzniknout

`AskUserQuestion` s `multiSelect: true`, v tomhle pořadí:

| Pořadí | Label | Description |
|---|---|---|
| 1. | `Doslovný přepis (MD)` | Vyčištěný, bez „ehm“, s kapitolami a opravenými názvy. |
| 2. | `Strukturované shrnutí (MD)` | Témata, závěry, na konci domluvy a úkoly. |
| 3. | `Časovaný přepis (SRT)` | Syrový z whisperu, s časy. Na dohledání místa v nahrávce. |
| 4. | `Rozlišit mluvčí (VTT, JSON)` | Viz níže – jen odhad času, nic víc. |

Když uživatel nevybere nic, ber to jako **první tři**. Rozlišení mluvčích je vždycky vědomá volba, nikdy výchozí stav.

#### Popisek u čtvrté položky

Drž ho holý. Spočítej odhad a napiš jen ten:

```
Přidá ~M:SS.
```

Odhad vezmi z `python3 <skill>/rate.py eta diarize <délka_v_sekundách>`.

**Když pyannote nebo token chybí** (zjistíš předem přes `check-deps.sh --diarize`), přilep za odhad druhou větu: `Vyžaduje doinstalování pyannote a token na HuggingFace.` Když je všechno na místě, tuhle větu **vynech** – uživatele nezajímá, co má.

#### Když je čtvrtá položka zaškrtnutá, zeptej se na počet mluvčích

Druhá otázka v témže kroku. Pevný počet dělá výrazně míň chyb než automatický odhad a uživatel ho zná:

| Pořadí | Label | Description |
|---|---|---|
| 1. | `Dva` | Nejčastější případ, rozhovor. |
| 2. | `Tři až čtyři` | |
| 3. | `Pět a víc` | |
| 4. | `Ať si to zjistí samo` | Míň přesné, ale nemusíte počítat. |

U „tří až čtyř“ a „pěti a víc“ se doptej na přesné číslo, nebo předej `auto` – rozsah pyannote nebere.

### 5. Ověř závislosti

Až teď, protože model už znáš:

```bash
<skill>/check-deps.sh <model>              # bez rozlišení mluvčích
<skill>/check-deps.sh --diarize <model>    # s ním
```

Když skončí nenulově, vypiš uživateli, co chybí, nabídni instalaci (skript vypsal přesné příkazy) a po jeho souhlasu ji proveď. Skill potřebuje:

- **ffmpeg** – `brew install ffmpeg` (převod audia na WAV),
- **whisper.cpp** – `brew install whisper-cpp` (poskytuje `whisper-cli`),
- **model** – `turbo` (~1,5 GB) nebo `large-v3` (~2,9 GB) v `~/.whisper-models/`,
- **VAD model Silero** (~865 kB) – detekce řeči, viz níže,
- **jen pro rozlišení mluvčích:** `pyannote.audio` ve vlastním venv (~2,5 GB kvůli PyTorch) a token na HuggingFace.

**Diarizaci nikdy nedoinstaluj sám bez řečí.** Kromě velikosti stažení po uživateli chce dvě věci, které za něj nikdo neudělá: založit token a **odsouhlasit licenci gated modelu v prohlížeči**. Vypiš mu obojí a počkej. Když to odmítne, pokračuj bez rozlišení mluvčích – zbytek skillu funguje beze změny.

Instalace předpokládá [Homebrew](https://brew.sh). Vyvinuto a testováno na macOS.

### 6. Spusť přepis na pozadí

```bash
WHISPER_MODEL=<turbo|large-v3> \
WHISPER_LANG=<kód jazyka z kroku 1> \
WHISPER_PROMPT="<slovník oddělený čárkami>" \
WHISPER_KEEP_WAV=<0|1> \
<skill>/transcribe.sh <workdir> <workdir>/whisper-progress.log <audio1> <audio2> ...
```

`<workdir>` = adresář vstupní nahrávky. Vzniknou v něm `<název>.txt`, `<název>.srt` a `whisper-progress.log`.

**`WHISPER_KEEP_WAV=1` nastav právě tehdy, když se bude rozlišovat mluvčí.** Diarizace jede nad tímtéž WAV a bez toho by se musel vyrábět znovu. Jinak nech `0`, ať se po sobě uklidí hned. Běh na pozadí upozorní na dokončení (marker `### ALL DONE` v logu).

**VAD je vždy zapnutý** a není na co se ptát. Vyřazuje ticho, čímž zabíjí celou třídu halucinací („Titulky vytvořil…“, dokola tatáž věta) a zároveň zrychluje běh. Práh je nastavený konzervativně (`-vt 0.35`, `-vp 200`), aby neuřízl tiché mluvčí. Vypnout ho jde přes `WHISPER_VAD=0`, ale sahej po tom jen jako po nápravě podle kroku 7.

Chyba jednoho souboru neshodí zbytek běhu – zapíše se `### FAILED` a pokračuje se dalším. Po doběhnutí zkontroluj, jestli v logu nějaké `### FAILED` není, a **ohlas ho uživateli**.

### 7. Zkontroluj, kolik zvuku VAD pustil dál

V logu je pro každý soubor řádek:

```
### VADSTAT <n> <sekund_řeči> <celkem_sekund> <procent>
```

U mluveného slova čekej zhruba 60 až 90 %. **Když podíl klesne pod 40 %**, je pravděpodobné, že VAD ukrojil tichého mluvčího. Ohlas to uživateli s konkrétním číslem a nabídni opakovaný běh s `WHISPER_VAD=0`. Nerozhoduj o tom sám – u nahrávky s dlouhými pauzami může být nízký podíl v pořádku.

### 8. Rozliš mluvčí – jen když si to uživatel vybral

Druhý, **samostatný průchod** nad WAV z kroku 6. Když spadne, přepis tím nepřichází vniveč – ohlas selhání a pokračuj krokem 9 bez mluvčích.

```bash
<skill>/diarize.sh <workdir> <workdir>/whisper-progress.log <workdir>/<název>.wav <počet|auto>
```

Do logu přibude `### DIARSTAT <mluvčích> <úseků>` a `### DIARIZE ELAPSED`, ze kterého se kalibruje tempo. Při chybě `### DIARIZE FAILED <důvod>`.

#### Spoj mluvčí s textem

```bash
python3 <skill>/merge.py <workdir>/<název>.srt <workdir>/<název>.diarization.json <workdir>/<název>
```

Vznikne `<název>.json` a `<název>.vtt`. **Oba nesou syrový text z whisperu, ne vyčištěný** – jsou navázané na časové značky, takže přepsat v nich text by je rozešlo s nahrávkou. Vyčištěný text žije jen v `<název>.md`. Neopravuj je ručně.

Přiřazuje se podle **největšího časového překryvu**, protože whisperovy segmenty nekopírují střídání mluvčích. Když je překryv slabý nebo těsný, replika zůstane bez mluvčího – `merge.py` vypíše kolik takových je (`### MERGESTAT <celkem> <nepřiřazeno> <mluvčích>`).

**Nepřiřazené repliky nedoplňuj odhadem.** Chybné přiřazení vypadá stejně věrohodně jako správné a propíše se až do úkolů ve shrnutí, kde je z něj tvrzení, kdo co slíbil.

#### Zeptej se, kdo je kdo

Až teď, protože dřív nebylo co pojmenovat. Pro každého mluvčího jedna otázka; **návrhy vytáhni z přepisu** – z představování, z oslovování, z toho, kdo o kom mluví ve třetí osobě – a ze slovníku z kroku 3.

**U dvou mluvčích se ptej jednou na dvojici**, ne dvakrát zvlášť. Buď přiřazení sedí, nebo je prohozené – dvě otázky by byly zbytečné kliknutí navíc. Od tří mluvčích výš dej otázku každému.

Vždycky nabídni i možnost nechat mluvčí anonymní. Anonymní mluvčí je lepší než špatně pojmenovaný.

Jména ulož do dočasného JSON a pusť `merge.py` znovu s `--names`, ať se propíšou do obou výstupů. Zapiš je i do `.transcript-glossary.md`, aby s nimi počítalo čištění i shrnutí.

### 9. Vyrob výstupy, které si uživatel vybral

**Doslovný přepis.** Pro každou nahrávku zpracuj její `<název>.txt` do `<název>.md` dle [Pravidel doslovného přepisu](#pravidla-doslovného-přepisu). U více nebo delších nahrávek to udělej **paralelně přes subagenty** (jeden na soubor) na **výchozím modelu s `low`** (Volba modelu a effortu podle `~/.claude/RULES.md`, *Model a effort podle úkolu*). Nejlevnější model sem nepatří: oprava přeslechů je úsudek a **vymyšlená věta v přepisu vypadá stejně věrohodně jako správná** – nepozná se jinak než poslechem nahrávky.

**Každému subagentovi předej celý `.transcript-glossary.md`**, ne jen těch deset položek z promptu. Tady platí opak než u whisperu: čím víc kontextu, tím líp. Rozdíl mezi „tohle je zkomolenina, opravím ji“ a „tohle je jejich interní pojem, nechám ho být“ se dá udělat jedině proti úplnému slovníku. Nech si od subagenta vrátit i stručný brief pro shrnutí.

Fáze opravy přeslechů zůstává, i když se slovník použil. Slovník zmenší počet chyb, nevynuluje ho – v ostrém běhu prošlo sledované místní jméno zkomolené i s nasazeným promptem.

**Doplň slovník o to, co jsi našel při čištění.** Když v přepisu narazíš na termín, který v `.transcript-glossary.md` chybí, dopiš ho tam dřív, než budeš psát shrnutí. Shrnutí pak stojí na stejném slovníku jako přepis.

**Časovaný přepis.** `<název>.srt` už existuje, vznikl při přepisu. Nech ho ležet vedle `<název>.md`, stejné jméno, jiná přípona. Rozlišení mluvčích ho **nenahrazuje** – `<název>.vtt` a `<název>.json` přibydou vedle něj.

SRT se vyrábí vždycky, protože z něj `merge.py` bere text. Když si ho uživatel nevybral, je to mezivýstup a smaže se v úklidu, i kdyby se mluvčí rozlišovali.

**Rozlišení mluvčích mění doslovný přepis na dialog.** Kapitoly a mezinadpisy zůstávají, uvnitř nich se místo odstavců střídají repliky:

```markdown
## Životní cyklus člena

**Tomáš:** Jde o to, že když někdo přijde do AK1, tak je to jasné.

**Jan:** A potom to krystalizuje podle toho, jak vypadají prostory.
```

Repliku bez přiřazeného mluvčího uveď bez jména, ne pod nejbližším mluvčím.

**Shrnutí.** Navrhni uživateli „Výstižný název“ celé nahrávky a **nech si ho odsouhlasit** (ať nemusí nic vymýšlet ani psát), pak zapiš `YYYYMMDD - Výstižný název.md` dle [Formátu souhrnného MD](#formát-souhrnného-md).

### 10. Úklid

Smaž mezivýstupy: všechny `<název>.txt`, `<název>.wav` (nebo `<název>.16k.wav`, když byl vstup sám WAV), `<název>.diarization.json`, `whisper-progress.log` a `.transcript-glossary.md`. Ponech zdrojové audio a to, co si uživatel vybral v kroku 4. **Nevybrané výstupy smaž** – když uživatel nechtěl SRT, `<název>.srt` po sobě ukliď, i když mezitím vznikl.

Než slovník smažeš, **vypiš uživateli termíny, které jsi nechal být** – ty, co modely dávaly konzistentně a vypadají jako interní žargon, a ty, kde je zvuk nesrozumitelný a tvar je tvůj odhad. Ať ví, co má ověřit. Zapiš je i **na konec doslovného přepisu** jako poznámku. Když si uživatel doslovný přepis nevybral, dej tu poznámku na konec shrnutí – nesmí zmizet jen proto, že vznikl jiný výstup.

---

## Průběžný stav – NEspouštěj automaticky

Opakované časovače zbytečně plýtvají kapacitou. Progress bar vypiš **jen když se uživatel zeptá**, jak to jde:

```bash
python3 <skill>/progress.py <workdir>/whisper-progress.log
```

Ukáže procenta, zpracované a celkové minuty, kolik zbývá, tempo (× realtime) a ETA.

---

## Pravidla doslovného přepisu

Platí pro `<název>.md` každé nahrávky i pro sekci „Doslovný přepis“ v souhrnu. Připrav doslovný přepis v jazyce nahrávky:

- Uprav jen **stylistiku a slovosled** tam, kde je to potřeba, aby se text dal plynule a smysluplně číst.
- **Oprav pravopis a gramatiku** podle pravidel jazyka nahrávky. Rozpoznávač neumí i/y ve shodě přísudku s podmětem, plete si tvary, které znějí stejně, a sází interpunkci od oka. Mluvčí to neřekl špatně – špatně to zapsal model, takže to není zásah do jeho projevu, ale oprava chyby přepisu. Typicky: „mrtvoli“ místo **mrtvoly**, čárky ve vedlejších větách, velká písmena u vlastních jmen. **Které pravidlo použít, řekne jazyk zjištěný v kroku 1**, ne domněnka, že jde o češtinu. U češtiny platí `~/Dev/context/text/text.md`, sekce *Gramatika a pravopis* a *Typografie*; u jiného jazyka jeho vlastní konvence – anglický text má anglické uvozovky a anglickou interpunkci, ne české.
- **Nespisovné tvary a hovorovou mluvu ale nech být.** „Bysme“, „vokno“, „dycky“ nebo „démoni“ místo demonstrátorů jsou to, jak lidé mluví, a do doslovného přepisu patří. Opravuje se chyba zápisu, ne mluvčí.
- Odstraň **výplňová slova** (hesitační výplně) a **opakovaná slova** / místa, kde se řečník zamotal při hledání formulace.
- **Odstraň halucinace ASR** – i s VAD se občas objeví nesmyslné opakující se řádky (dokola tatáž věta, „Titulky vytvořil …“). Takové smyčky celé smaž.
- Rozděl text do **ucelených kapitol** s výstižnými mezinadpisy (`##`).
- Každou kapitolu rozděl do **kratších odstavců** – žádné dlouhé bloky.
- Nosné pojmy a důležitá sdělení vyznač **tučně**.
- Výčty uveď jako **odrážkový/číslovaný seznam**, kde to dává smysl.
- **Oprava přeslechů:** podle tématu a kontextu najdi a oprav slova, kterým rozpoznávač rozuměl špatně – tak, jak jsou, nedávají smysl, ale pravděpodobně jde o zkomoleninu jiného slova, které by v daném kontextu smysl dávalo.
- **Vlastní jména a názvy:** stejně oprav jména a názvy zkomolené špatnou výslovností nebo cizím přízvukem. Slovník z kroku 3 je pro tuhle opravu závazný zdroj správných tvarů.
- **České jméno v cizojazyčné nahrávce piš česky.** Když v anglicky mluveném záznamu zazní české jméno, firma nebo místo, rozpoznávač ho přepíše foneticky tak, jak to vyslovil cizinec – „Novak“, „Yarda“, „Brno“ jako „Burno“, „Škoda“ jako „Skoda“. Vrať mu **původní český tvar i s diakritikou**, i když je zbytek věty anglicky. Platí to oběma směry a je to jediná oprava, kterou děláš i tam, kde přepsané slovo dává v cizím jazyce zdánlivě smysl.
- **Neopravuj to, čemu jen nerozumíš.** Když stejné podivné slovo dává model opakovaně a konzistentně, je to nejspíš interní žargon, ne přeslech. Nech ho být, případně se zeptej.
- U dialogu **nepřehazuj pořadí** myšlenek; kde je zřejmé, kdo mluví, můžeš mluvčí odlišit, ale nevymýšlej jména.
- **Mluvčího nehádej.** S diarizací ber nálepky z `<název>.json` a repliku, která tam mluvčího nemá, nech bez jména. Bez diarizace mluvčí rozlišuj jen tam, kde to plyne přímo z textu. Špatné přiřazení je horší než chyba ve slově – překlep čtenář pozná, „Tomáš slíbil, že to dodá“ ne.

## Formát souhrnného MD

**Celý souhrnný dokument piš v jazyce nahrávky**, který jsi zjistil v kroku 1 – včetně nadpisu, anotace a názvů sekcí. Anglicky mluvená schůzka nemá mít české shrnutí.

Soubor `YYYYMMDD - Výstižný název.md` má tuto strukturu:

1. **Hlavní nadpis (H1):** `Výstižný název`.
2. **Úvodní odstavec (anotace):** do jednoho odstavce základní charakteristika celé nahrávky – o co jde, jednotlivé strany a účastníci.

**Nadpis i anotace jsou tvůj vlastní text**, ne přepis. Platí pro ně jazyková pravidla ze sekce [Pravidla shrnutí](#pravidla-shrnutí) stejně jako pro sekci „Shrnutí“ – ani jedno z nich nespadá pod [Pravidla doslovného přepisu](#pravidla-doslovného-přepisu).
3. **`## Shrnutí`:** stručné, logické, strukturované shrnutí dle [Pravidel shrnutí](#pravidla-shrnutí).
4. **`## Doslovný přepis`:** doslovné přepisy všech nahrávek dle [Pravidel doslovného přepisu](#pravidla-doslovného-přepisu), za sebou; u každého je zřejmé, ze které nahrávky pochází. Tuhle sekci vynech, když si uživatel doslovný přepis nevybral.

## Pravidla shrnutí

Platí pro sekci „Shrnutí“. Připrav stručné, logické, strukturované shrnutí celé nahrávky – důležitých témat, poznatků a klíčových informací:

- Využij **přehledné formátování** – mezinadpisy, odstavce, odrážky, **tučný** text pro důležité pojmy.
- **Nedodržuj chronologické pořadí**, ve kterém informace zazněly. Uspořádej vše do logických sekcí a skupin tak, aby to dávalo při čtení smysl.
- Pokud to není nezbytné pro kontext nebo pochopení, **neopakuj** jednu informaci na více místech.
- Na **úplném konci** přehledně shrň vzájemné **domluvy, vyplývající úkoly a další kroky**.
- **Když běžela diarizace, piš ke každému úkolu majitele.** Je to hlavní důvod, proč se rozlišení mluvčích vůbec zapíná: bez něj se dá napsat „dodat seznam“, s ním „**Tomáš** dodá seznam“. U rozhodnutí stejně tak uveď, kdo co navrhl a kdo souhlasil, když to z přepisu plyne. Kde mluvčí chybí nebo je nejistý, majitele **nedoplňuj odhadem** – radši úkol bez majitele než přisouzený špatnému člověku.
- **Pravopis, gramatika a typografie platí i tady.** Shrnutí není doslovný přepis, ale tvůj vlastní text, takže se na něj pravidla z [Pravidel doslovného přepisu](#pravidla-doslovného-přepisu) nevztahují sama od sebe – drž je vědomě. Pozor hlavně na termíny přebrané z přepisu: chybu opravenou v přepisu snadno zopakuješ ve shrnutí, protože ho píšeš z téhož podkladu. Přesně takhle v ostrém běhu prošly „mrtvoli“ do souhrnného dokumentu, zatímco v přepisu už byly opravené.

(Základní charakteristika a účastníci jsou už v úvodním odstavci – viz [Formát souhrnného MD](#formát-souhrnného-md).)

---

## Technické detaily

- **Modely:** `turbo` (`ggml-large-v3-turbo.bin`) a `large-v3` (`ggml-large-v3.bin`) v `~/.whisper-models/`. Naměřeno na Apple M1 nad 31 minutami české schůzky: turbo 5,4× realtime, `large-v3` 1,67× realtime, tedy 3,2× pomaleji. Rozdíl v textu byl 13 % slov, ale drtivou většinou šlo o vatu („jo“, „to“, „jako“); rozhodující rozdíl je ve vlastních jménech a řídkých slovech, kde `large-v3` vyhrává. **Slovník jmen ten rozdíl smaže spolehlivěji než volba modelu** – turbo s osmipoložkovým slovníkem porazilo `large-v3` bez slovníku a bylo přitom 3,6× rychlejší.
- **Délka promptu rozhoduje.** Tentýž zvuk, tentýž model: slovník o 8 termínech dal sledované vlastní jméno 6× ze 6 správně, slovník o 21 termínech 0 ze 4. Účinnost initial promptu klesá s pořadím položky, takže **krátký a seřazený slovník je lepší než dlouhý**. Proto strop deseti položek v kroku 3.
- **Kalibrace ETA:** `rate.py` drží `~/.whisper-models/rate.json` s naměřeným tempem pro každý model zvlášť. Po každém běhu se hodnota posune k realitě (EWMA, α = 0,35), takže odhady sedí na konkrétní stroj. Výchozí hodnoty jsou z M1. **Běhy pod dvě minuty zvuku se do kalibrace nepočítají** – dominuje u nich načtení modelu a tempo vyjde nesmyslně nízké (25s vzorek srazil naměřených 5,96× na 4,75×).
- **Jazyk:** výchozí čeština (`cs`). Lze přebít proměnnou `WHISPER_LANG`.
- **Vlákna:** `transcribe.sh` bere počet výkonných jader ze `sysctl`, ne whisperovské výchozí čtyři.
- **Potlačení neřečových tokenů:** `-sns`, zapnuto vždy. Druhá pojistka vedle VAD.
- **Rozlišení mluvčích** je volitelný druhý průchod přes `pyannote/speaker-diarization-3.1` ve vlastním venv. Zapíná se v průvodci, výchozí stav je vypnuto. Naměřeno na Apple M1: **7,13× realtime**, tedy 31,4 minuty zvuku za 4:24 – zhruba stejně dlouho jako přepis turbem.
- **Gated repozitáře jsou tři**, ne jeden: kromě `speaker-diarization-3.1` ještě `segmentation-3.0` a `speaker-diarization-community-1`. Seznam se mezi verzemi pyannote mění, proto `diarize.sh` při selhání vytáhne z chyby konkrétní repozitář (`### DIARIZE FAILED gated:<repo>`). Kontrola v `check-deps.sh` sahá na `config.yaml`, ne na `/api/models/` – **metadata gated repa jsou veřejná, takže endpoint vrací 200 i bez přístupu** a kontrola by byla falešně pozitivní.
- **Bere se `exclusive_speaker_diarization`**, ne `speaker_diarization`. Je podle dokumentace pyannote určená právě pro navázání na přepis, protože neobsahuje překrývající se úseky.
- **Nepřiřazené repliky jsou v pořádku.** Na 31minutové schůzce dvou lidí zůstalo bez mluvčího 21 replik ze 426 (5 %) a byly to skoro výhradně krátké přitakávací vsuvky („jo, jo, jo“, „to asi ne“). Delší věcné repliky mluvčího dostaly všechny.
- **Zarovnání po slovech (WhisperX) skill záměrně neřeší.** Táhlo by s sebou faster-whisper, který na Apple Silicon nemá Metal backend a běží jen na CPU, takže by se celý přepis řádově zpomalil. Cenou je, že na rychlých výměnách („jasně, jasně“) bude přiřazení mluvčích plavat. Bereme to vědomě: na dlouhých replikách, ze kterých se dělají úkoly ve shrnutí, se lidé nepřekřikují.

## Soubory skillu

| Soubor | K čemu |
|---|---|
| `check-deps.sh` | kontrola závislostí, volitelně pro konkrétní model |
| `transcribe.sh` | vlastní přepis, řízený proměnnými prostředí |
| `common.sh` | cesty k modelům, počet vláken – sourcuje se |
| `rate.py` | odhad a kalibrace tempa (`get`, `eta`, `update`) |
| `progress.py` | progress bar nad logem běhu |
| `detect-lang.sh` | detekce jazyka ze vzorku zprostřed nahrávky |
| `diarize.sh` | volitelný druhý průchod – kdo kdy mluví |
| `diarize.py` | vlastní běh pyannote uvnitř venv |
| `merge.py` | spojí časy z whisperu s mluvčími, vyrobí `.json` a `.vtt` |
