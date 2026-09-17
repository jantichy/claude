---
name: transcript
description: Skill se použije, když uživatel zadá "/transcript", nebo když chce přepsat zvukové i obrazové nahrávky (MP3, M4A, WAV, AAC, MP4, MOV…) do Markdownu – přepis a strukturované shrnutí schůzky/nahrávky. Přepis běží kompletně lokálně a offline (whisper.cpp). Výsledkem je přepis; má-li se z nahrávky stát trvalá znalost v knowledge base, je na to /learn, který si přepis vyžádá sám.
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, Skill]
---

# Transcript

## Co skill dělá

Lokální, offline přepis nahrávek do Markdownu. Nic neopouští počítač (rozpoznání řeči běží přes [whisper.cpp](https://github.com/ggml-org/whisper.cpp)).

Skill se **nespouští s přepínači**. Volá se cestou k souboru a volným popisem:

```
/transcript ~/Desktop/schuzka.m4a Přepiš mi schůzku s Janou Novákovou nad nastavením intranetu
```

Ten volný popis není dekorace. Vytáhneš z něj jména a názvy do slovníku (krok 3), takže **čím konkrétnější popis, tím míň zkomolených jmen**.

Než se pustíš do práce, projdeš s uživatelem krátkého průvodce. Teprve pak se přepisuje.

**Nahrávku, ze které se má stát znalost, umí `/learn` vzít i rovnou** – přepis si od tebe vyžádá sám a **tři otázky průvodce** (co má vzniknout, model, mluvčí) si zodpoví za uživatele, takže je neopakuj. **Všechno ostatní se ptej dál**, i když zadání přišlo odtamtud: jazyk, **jestli je víc nahrávek jedna rozřezaná schůzka**, **datum nahrávky, když mu metadata odporují**, hranici u dvojjazyčné nahrávky, kolizi jmen i existující výstupy v adresáři. Ty odpovědi `/learn` nemá odkud vzít a tichá volba za uživatele by u existujícího přepisu znamenala přepsat starší práci.

**Přepisem to nemusí končit.** Nese-li nahrávka znalost, která má přežít i po tom, co se přepis zapomene – výklad na školení, konzultace, cizí prezentace –, nabídni v závěru `/learn`: zapracuje ji do znalostní báze místo toho, aby zůstala v samostatném souboru na disku.

## Co skill nedělá

- **Nevytěžuje znalost, jen přepisuje.** Má-li se z nahrávky stát trvalá znalost v knowledge base, je na to `/learn` – ten si přepis vyžádá sám a pak ho rozpustí do existujících textů. Tenhle skill končí souborem na disku.
- **Nepíše text autorovým hlasem.** Shrnutí je věcný výtah z toho, co zaznělo; na psaní textu je `/compose`.
- **Neposílá nic ven.** Rozpoznávání i rozlišení mluvčích běží lokálně. Jediná výjimka je stažení modelu, a to jen jednou.
- **Nepřekládá.** Výstup je v jazyce nahrávky; u dvojjazyčné nahrávky se řeže, ne převádí.

## Jak je to postavené uvnitř

**Rozpoznávání řeči dělá whisper.cpp, rozlišování mluvčích pyannote a řezání ffmpeg – a všechno tohle je implementační detail, ne rozhraní.** Totéž platí pro rozdělení práce mezi skripty v adresáři skillu (jejich soupis drží *Soubory skillu* níž), pro jména proměnných prostředí, kterými se řídí, i pro naměřená nastavení v [`internals.md`](internals.md). Kdyby whisper nahradil jiný rozpoznávač, skripty se slily do jednoho nebo se přepínač přejmenoval, nikdo mimo tenhle adresář to nemá poznat.

**Závazné je naopak tohle a nesmí se změnit tiše:**

- **Nic neopouští počítač.** Celý přepis běží lokálně a offline; je to důvod, proč skill existuje.
- **Tvar výstupu** – přepis a shrnutí v Markdownu podle *Formát souhrnného MD* a *Pravidla shrnutí* níž.
- **Zdrojová nahrávka zůstává nedotčená.** Skill k ní smí jen číst; mezivýstupy se po dokončení uklidí.
- **Průvodce se ptá, místo aby volil za uživatele** – zvlášť tam, kde by tichá volba přepsala existující přepis.

## Vstup a výstup

- **Vstup:** soubory zadané v promptu. Když prompt žádný soubor neuvádí, vezmi všechny nahrávky v aktuálním adresáři. **Je-li jich víc, nejdřív zjisti, jestli to není jedna schůzka rozřezaná na části** – viz krok 1; pak se spojí a dál se pracuje s jedním souborem. Podporované formáty:
  - **zvuk:** `mp3`, `m4a`, `wav`, `aac`, `flac`, `ogg`, `opus`, `m4b`,
  - **video:** `mp4`, `mov`, `m4v`, `mkv`, `webm`, `avi`.

  Video se nijak neliší – zvuková stopa se z něj vytáhne při převodu na WAV a dál se s ní pracuje stejně. **Je to běžný případ, ne výjimka:** záznam hovoru z Meetu nebo Teamsů se stahuje jako MP4. Obraz se nikam nepřenáší; z videa vzniká jen text.

  Když soubor zvukovou stopu nemá, převod na WAV selže a `transcribe.sh` to zapíše jako `### FAILED file-<n> wav-conversion` – ohlas to uživateli a pokračuj dalšími. Když nenajdeš nic, oznam to a skonči.
- **Výstup – vše vzniká v adresáři vstupní nahrávky, nezakládá se žádný podadresář a nic se nikam nepřesouvá:**
  - `<name>.md` – vyčištěný doslovný přepis (viz [Pravidla doslovného přepisu](output.md#pravidla-doslovného-přepisu)),
  - `<name>.srt` – tentýž obsah s časovými značkami, syrový z whisperu,
  - `<name>.vtt` – titulky se značkou `<v Jméno>`, protože SRT pole pro mluvčího nemá. Vzniká **vedle** SRT, jen s rozlišením mluvčích,
  - `<name>.json` – strojově čitelné úseky s časem, mluvčím a textem. Taky jen s rozlišením mluvčích,
  - `YYYYMMDD - Výstižný název.md` – jedno společné shrnutí napříč všemi nahrávkami (viz [Formát souhrnného MD](output.md#formát-souhrnného-md)).

  Které z nich vzniknou, vybere uživatel v průvodci.

  **`<name>` je jméno vstupní nahrávky bez přípony.** U schůzky spojené z několika částí je to jméno, které uživatel zvolil v kroku 1 – sada výstupů je pak jedna jediná, ne jedna na každou původní část.
- **Mezivýstupy** vznikají viditelně v adresáři a **po dokončení se uklidí** (viz krok 10): `<name>.txt` od whisperu, skrytý `.transcript-glossary.md`, `whisper-progress.log`, u spojené schůzky `<name>.wav` z `join.sh` a při rozlišování mluvčích navíc `<name>.wav` (u spojené schůzky k němu ještě `<name>.16k.wav`), `<name>.diarization.json` nebo `<name>.16k.diarization.json` a `.speakers.json`. Zdrojové audio zůstává.

  **Bez rozlišování mluvčích žádný viditelný WAV nevzniká.** `transcribe.sh` si ho v tom případě pojmenuje skrytě (`.<name>.tmp.wav`) a smaže ho hned po zpracování každé nahrávky, ne až v úklidu. **U spojené schůzky to neplatí** – ta je WAV od začátku, protože ho vyrobil `join.sh`, a leží v adresáři až do úklidu bez ohledu na to, jestli se mluvčí rozlišují.

---

## Krok 0 – Příprava

**Tenhle skill neběží nad kódem projektu, takže body 1 až 3 z `~/.claude/skills/PREFLIGHT.md` nahrazuje vlastními předpoklady** – pouští se nad nahrávkou, která leží kdekoliv, často mimo repozitář. Body 4 a 5 odpadají ze stejného důvodu: nic nespouští nad kódem a nesahá na diff větve. Načti si ho přesto; platí z něj závěr o shrnutí zjištěného, než se cokoliv stane. Co je potřeba zjistit místo toho, stojí v kroku 1 níž.

**Kroky místo fází jsou tu schválně.** Výsledkem téhle práce je to, co uživatel naodpovídá v průvodci – model, slovník jmen, co má vzniknout –, takže postup je sled otázek (`~/.claude/skills/SKILLS.md`, *Číslování a názvosloví*).

## Krok 1 – Zjisti si fakta o vstupu

Ještě než se na cokoliv zeptáš, potřebuješ délku a datum – bez délky neumíš nabídnout odhady časů v prvním kroku průvodce.

```bash
ffprobe -v error -show_entries format=duration -of csv=p=0 <audio>
ffprobe -v error -show_entries format_tags=creation_time -of csv=p=0 <audio>
```

Datum `YYYYMMDD` vezmi z metadat, **projdou-li kontrolou níž**. Obvykle je stejné napříč soubory; když ne, vezmi z prvního. Když metadata s datem chybí, použij dnešek.

**Metadatům s datem ale nevěř bez kontroly.** `creation_time` bývá u exportovaných souborů **časem exportu, ne nahrávání** – diktafon, mobil i konferenční nástroj ho přepíšou ve chvíli, kdy soubor posíláš do počítače. Chyba se přitom nijak neprojeví: datum vypadá věrohodně a nikdo ho nezpochybní.

**U částí jedné schůzky to jde ověřit strojově, tak to udělej vždycky** – tedy jakmile uživatel v následujícím podkroku potvrdí, že o rozřezanou schůzku jde. Spočítej **rozpětí mezi nejstarším a nejmladším `creation_time`** a porovnej ho s **délkou nejkratší části**. Je-li rozpětí menší, nemůže jít o čas nahrávání: mezi začátky dvou po sobě jdoucích částí musí uplynout aspoň tolik, kolik trvá ta první z nich. Metadata jsou pak nepoužitelná nejen pro datum, ale **i pro určení pořadí**, a na datum se musíš **zeptat**.

**Neporovnávej rozpětí se součtem délek všech částí.** Vyjde to menší pokaždé, i u naprosto poctivých metadat – rozpětí mezi krajními časy z principu jednu část nepokrývá, takže by kontrola hlásila poplach vždycky a nic by neznamenala.

Doloženo: tři části jedné schůzky nesly časy vzniku v rozmezí 48 sekund, přestože dohromady trvaly 59 minut, a přepis kvůli tomu dostal datum o šest dní vedle.

**Na samostatné nahrávky tuhle kontrolu nepouštěj.** Dvě konzultace vyexportované krátce po sobě ji neprojdou, přestože jejich metadata můžou být v pořádku – kritérium stojí na tom, že části mají na sebe časově navazovat, a to u samostatných nahrávek neplatí.

Kde kontrolu udělat nejde – u jednoho souboru i u samostatných nahrávek – aspoň **řekni nahlas, jaké datum používáš a odkud je**, stejně jako u jazyka. Kdo vidí, že nesedí, ozve se.

**Na datu visí víc než jméno souboru se shrnutím.** Váže se k němu každý relativní údaj, který v hovoru padne („do konce týdne“, „příští čtvrtek“), takže chyba v něm posune všechny termíny v úkolech.

**Je-li nahrávek víc, zjisti délku a datum u každé zvlášť.** Délky potřebuješ hned pro kontrolu metadat níž a obojí pak pro určení pořadí částí.

#### Když je nahrávek víc, zeptej se, jestli je to jedna schůzka

**Víc souborů neznamená víc schůzek.** Nejčastější důvod, proč jich je v adresáři víc, je jedna a tatáž schůzka rozpadlá na části: diktafon se na pár vteřin zastavil, nahrávání se restartovalo, hovor spadl a pokračoval. Taková schůzka se **spojí hned na začátku** a od té chvíle se s ní zachází jako s jednou dlouhou nahrávkou – jeden přepis, jedno SRT, jedna diarizace, jedno shrnutí.

Spojit se to musí **před přepisem, ne po něm**. Diarizace nad částmi zvlášť dá v každé vlastní sadu nálepek, takže `SPEAKER_00` z první části není tentýž člověk jako `SPEAKER_00` z druhé – museli by se pojmenovávat několikrát a stejně by se nedalo spolehlivě říct, kdo z nich je kdo. Nad spojeným zvukem má pyannote navíc na každého mluvčího delší vzorek, takže i samotné rozlišení vyjde stabilněji.

**Automaticky se to nepozná, tak se ptej pokaždé, když vidíš víc než jednu nahrávku.** Délky ani metadata nerozhodnou: dvě samostatné konzultace z jednoho odpoledne vypadají úplně stejně jako jeden rozřezaný call.

| Pořadí | Label | Description |
|---|---|---|
| 1. | `Jedna schůzka na části` | Spojím je do jedné nahrávky – vznikne jeden přepis, jedno SRT a jedna diarizace se společnými mluvčími. |
| 2. | `Samostatné nahrávky` | Každá se přepíše zvlášť a bude mít vlastní přepis. Shrnutí je i tak jedno společné. |

**První v pořadí dej tu možnost, pro kterou něco svědčí** – pro spojení mluví navazující časy vzniku, jména se společným základem a rostoucím číslem nebo to, že jedna část končí uprostřed věty. Nesvědčí-li pro ně nic, dej první `Samostatné nahrávky`.

##### Pořadí částí urči podle jmen, teprve pak podle metadat

Části se spojí přesně v tom pořadí, v jakém je předáš, a **špatné pořadí se nepozná jinak než přečtením přepisu**, kde na sebe věty přestanou navazovat. Urči ho v tomhle pořadí – vyhrává první signál, který je k dispozici:

1. **Číslo ve jméně souboru.** Diktafony nahrávky číslují vzestupně (`Záznam 4`, `Záznam 5`, `Záznam 7`), takže soubory se **společným základem jména a rostoucím číslem** nesou pořadí přímo v sobě. Je to nejspolehlivější signál, protože ho na rozdíl od metadat nepřepíše export. Čísla nemusí jít po sobě – chybějící kus řady znamená jen nahrávku, která se smazala nebo sem nepatří.
2. **`creation_time` z metadat**, ale **jen když projde kontrolou metadat z úvodu kroku 1**. Neprojde-li – tedy leží-li časy blíž u sebe než součet délek –, není to čas nahrávání a o pořadí nevypovídá vůbec nic. Pak ho nepoužívej ani jako druhou volbu.
3. **Zeptej se**, když nesedí ani jedno nebo si oba signály odporují.

**Vypiš výsledné pořadí i s délkami a řekni, podle čeho jsi ho určil.** U bodu 1 stačí, aby se uživatel podíval. **U bodu 2 si pořadí nech potvrdit** – metadata sice kontrolou prošla, ale je to slabší signál než čísla ve jménech. U bodu 3 se bez odpovědi nepokračuje.

**Čísla porovnávej jako čísla, ne jako text.** Lexikograficky se `záznam 10` dostane před `záznam 2` – tohle je jediné řazení podle jména, které je zakázané.

```bash
<skill>/join.sh <workdir> <name> <audio1> <audio2> ...
```

Vypíše cestu ke spojenému souboru a jeho délku. Sám si ověří, že výsledek délkou sedí na součet částí – když ne, nevrátí nic a soubor smaže, protože spojení, které tiše přijde o část, by se jinak poznalo až jako záhadně chybějící kus přepisu. Existující soubor nepřepíše.

**Na `<name>` se zeptej**, protože ho ponesou všechny výstupy až po `<name>.md`. Navrhni jméno adresáře – ten bývá pojmenovaný po schůzce – a nech uživatele potvrdit, nebo napsat vlastní.

**Skončí-li `join.sh` nenulově, nespojuj nic ručně a rozhodni podle důvodu:**

| Co skript hlásí | Co udělej |
|---|---|
| `už existuje` | zeptej se na jiný název, nebo si nech potvrdit smazání toho, co tam leží |
| `nesedí to` (délka proti součtu částí) | **zastav se a řekni to uživateli.** Některá část se nepřevedla celá; spojovat dál by znamenalo přepisovat neúplný zvuk |
| `nepovedlo se převést` | ohlas, která část a že nejspíš nemá zvukovou stopu; zeptej se, jestli ji vynechat, nebo skončit |
| `aspoň dvě nahrávky` | chyba v zadání na tvé straně – předal jsi míň než dva soubory, takže se nemá co spojovat |
| cokoliv jiného | skript vypsal důvod na chybový výstup; **přečti ho a řekni ho uživateli doslova**, nespojuj ručně a nepokoušej se to obejít. U selhání po převodu (`Spojení nahrávek selhalo`, `nedá se přečíst`) si skript spojený soubor sám smazal, takže v adresáři nic nezbylo |

Spojený soubor je **mezivýstup**: zdrojové nahrávky zůstávají nedotčené a úklid v kroku 10 ho smaže. Od téhle chvíle je vstupem **jeden soubor** a všechny další kroky se k němu chovají jako k jediné nahrávce – detekce jazyka, odhad času, přepis, diarizace i úklid.

#### Zjisti jazyk nahrávky

```bash
<skill>/detect-lang.sh <audio>          # vypíše např.:  cs 0.993
```

Whisper má jazyk zakódovaný v modelu a pozná ho ze zvuku dřív, než začne dekódovat slova. Vzorkuje se na **třech místech** (čtvrtina, půlka, tři čtvrtiny), protože začátky bývají pozdravy a šoupání židlí a jeden vzorek zprostředka nepozná nahrávku, která se v půlce přepne do jiného jazyka. U nahrávek **kratších než dvě minuty** stačí jeden vzorek zprostředka. Trvá to zhruba sedm sekund na vzorek, takže se to dělá vždycky.

Podle jistoty se zachovej takhle:

| Výsledek | Co udělej |
|---|---|
| jistota ≥ 0,9, jazyk `cs` | **neptej se a nic nehlas**, jeď dál |
| jistota ≥ 0,9, jiný jazyk | **neptej se, ale řekni to nahlas**: „Detekoval jsem angličtinu, přepisuji anglicky.“ Kdo nesouhlasí, ozve se |
| jistota < 0,9 | **teprve tady se zeptej**, s detekovaným jazykem jako první možností |
| skript selhal | vezmi výchozí `cs` a řekni, že detekce neproběhla |
| výstup obsahuje `mixed:` | **přebíjí všechny řádky výš** – jdi na *Když je nahrávka dvojjazyčná* a zeptej se, i kdyby jistota byla vysoká |

**U víc samostatných nahrávek pusť detekci na každou zvlášť.** Když vyjdou různé jazyky, nespojuj je do jednoho běhu – `transcribe.sh` bere jeden jazyk na celý běh, takže je pusť po skupinách podle jazyka a řekni to uživateli. **U schůzky spojené v předchozím podkroku ji pouštíš jednou, nad spojeným souborem** – tři vzorky pak padnou napříč celým hovorem, ne třikrát do jedné jeho části.

Jazyk pak předej jako `WHISPER_LANG` v kroku 6 a **zapiš ho do `.transcript-glossary.md`**. Neurčuje totiž jen rozpoznávání, ale i to, podle jakých pravidel se v kroku 9 opravuje pravopis a v jakém jazyce vzniká shrnutí.

#### Když je nahrávka dvojjazyčná

`detect-lang.sh` vzorkuje na **třech místech** (čtvrtina, půlka, tři čtvrtiny). Když se vzorky neshodnou, přidá na konec `mixed:cs,en`.

```
en 0.999 mixed:cs,en
```

**Whisper bere jeden jazyk na běh**, takže tohle skill sám nespraví. Musí to ale říct nahlas a nabídnout, co s tím:

1. **Přepsat po částech** – uživatel řekne, kolikátá minuta je zlom, ty nahrávku rozřízneš a pustíš dvakrát, každou část se svým jazykem:

   ```bash
   <skill>/split.sh <workdir> <audio> <cut>     # bod řezu jako MM:SS nebo v sekundách
   ```

   Vypíše cesty obou částí (`<name>-1.*`, `<name>-2.*`), každou na jeden řádek; zlom mimo nahrávku odmítne. **Řez má vlastní skript schválně**, i když je to jen dvojí volání ffmpegu: skripty skillu jsou v oprávněních pokryté jedním wildcardem, kdežto povolit `ffmpeg` napřímo znamená pustit nástroj, který umí přepisovat soubory (`-y`) – na rozdíl od čtecího `ffprobe`. Přepisy pak spojíš do jednoho `<name>.md` s mezinadpisem u zlomu. **Pozor na dvě věci:** časy v SRT druhé části začínají od nuly, takže se nedají použít pro diarizaci ani pro `merge.py`, a části `<name>-1.*` a `<name>-2.*` maže úklid v kroku 10 jmenovitě, takže na ně nezapomeň v jeho seznamu.
2. **Přepsat celé v převažujícím jazyce** a **napsat do poznámky na konci přepisu**, která část je nespolehlivá.

**Nerozhoduj sám, zeptej se.** Skript umí zjistit, *že* se jazyk mění, ale ne *kde* – hranici zná jedině uživatel. Časově se ty varianty skoro neliší (přepisuje se týž objem zvuku, jen se dvakrát načte model); liší se tím, kolik práce je kolem a jestli je přijatelné mít kus přepisu nespolehlivý.

**Krátká vsuvka v jiném jazyce mixed nevyvolá** – tři vzorky ji minou. Když se to stane, projeví se to až při čištění jako pasáž, která nedává smysl.

## Krok 2 – Průvodce, krok první: model

Spočítej odhad běhu pro obě varianty. Tempo drží `rate.py`, který se sám kalibruje podle skutečnosti:

```bash
python3 <skill>/rate.py eta turbo    <duration_seconds>
python3 <skill>/rate.py eta large-v3 <duration_seconds>
```

Zeptej se přes `AskUserQuestion`. **První možnost je vždy ta nejpravděpodobnější**, aby stačil Enter:

| Pořadí | Label | Description |
|---|---|---|
| 1. | `Turbo · ~M:SS` | Výchozí volba. Rychlé, na běžnou mluvu stejně dobré. Se slovníkem jmen zvládne i vlastní jména. |
| 2. | `large-v3 · ~M:SS` | Zhruba 3× pomalejší. Sáhni po něm u špatného zvuku, překřikování nebo když na přesnosti jmen záleží víc než na čase. |

Odhady dosaď skutečné, ne zástupné. Když samostatných nahrávek zpracováváš víc, počítej ze součtu délek; u spojené schůzky je to prostě délka spojeného souboru.

## Krok 3 – Průvodce, krok druhý: slovník jmen

**Postup i šablonu `.transcript-glossary.md` drží [`glossary.md`](glossary.md).** Načti si ho a řiď se jím; do těla skillu nepatří, protože se čte jen tady.

## Krok 4 – Průvodce, krok třetí: co má vzniknout

`AskUserQuestion` s `multiSelect: true`, v tomhle pořadí:

| Pořadí | Label | Description |
|---|---|---|
| 1. | `Doslovný přepis (MD)` | Vyčištěný, bez „ehm“, s kapitolami a opravenými názvy. |
| 2. | `Strukturované shrnutí (MD)` | Témata, závěry, na konci domluvy a úkoly. |
| 3. | `Časovaný přepis (SRT)` | Syrový z whisperu, s časy. Na dohledání místa v nahrávce. |
| 4. | `Rozlišit mluvčí (VTT, JSON)` | Viz níž – jen odhad času, nic víc. |

Když uživatel nevybere nic, ber to jako **první tři**. Rozlišení mluvčích je vždycky vědomá volba, nikdy výchozí stav.

#### Popisek u čtvrté položky

Drž ho holý. Spočítej odhad a napiš jen ten:

```
Přidá ~M:SS.
```

Odhad vezmi z `python3 <skill>/rate.py eta diarize <duration_seconds>`.

**U delší nahrávky připiš, že je to spodní hranice** – tempo diarizace s délkou klesá, takže odhad zkalibrovaný na kratším běhu ten delší podstřelí. Proč a o kolik, drží [`internals.md`](internals.md); hranice „delší“ tam zatím opřená o měření není, naměřené jsou jen dva body.

Jestli diarizační závislosti jsou, zjistíš `<skill>/check-deps.sh --diarize <model z kroku 2>`. **Model do příkazu doplň**, jinak skript zkontroluje výchozí `turbo` a vrátí chybu kvůli němu, i když s pyannote je všechno v pořádku. Tohle je jediné volání kontroly před krokem 5; tam se pak spouští znovu i s modelem, který si uživatel vybral.

**Když pyannote nebo token chybí**, přilep za odhad druhou větu: `Vyžaduje doinstalování pyannote a token na HuggingFace.` Když je všechno na místě, tuhle větu **vynech** – uživatele nezajímá, co má.

#### Když je čtvrtá položka zaškrtnutá, zeptej se na počet mluvčích

Druhá otázka v témže kroku. Pevný počet dělá výrazně míň chyb než automatický odhad a uživatel ho zná:

| Pořadí | Label | Description |
|---|---|---|
| 1. | `Dva` | Nejčastější případ, rozhovor. |
| 2. | `Tři až čtyři` | |
| 3. | `Pět a víc` | |
| 4. | `Ať si to zjistí samo` | Míň přesné, ale nemusíte počítat. |

U „tří až čtyř“ a „pěti a víc“ se doptej na přesné číslo, nebo předej `auto` – rozsah pyannote nebere.

## Krok 5 – Ověř závislosti

Teď naplno, se všemi volbami z průvodce:

```bash
<skill>/check-deps.sh <model>              # bez rozlišení mluvčích
<skill>/check-deps.sh --diarize <model>    # s ním
```

Když skončí nenulově, vypiš uživateli, co chybí, nabídni instalaci (skript vypsal přesné příkazy) a po jeho souhlasu ji proveď. Skill potřebuje:

- **ffmpeg** – `brew install ffmpeg` (převod audia na WAV),
- **python3** – kalibrace tempa i statistika diarizace stojí na něm,
- **whisper.cpp** – `brew install whisper-cpp` (poskytuje `whisper-cli`),
- **model** – `turbo` (~1,5 GB) nebo `large-v3` (~2,9 GB) v `~/.whisper-models/`,
- **VAD model Silero** (~865 kB) – detekce řeči, viz níž,
- **jen pro rozlišení mluvčích:** `pyannote.audio` ve vlastním venv (**1,2 GB**, změřeno po instalaci) a token na HuggingFace v `~/.whisper-models/hf-token` (nebo v proměnné `HF_TOKEN`).

**Diarizaci nikdy nedoinstaluj sám bez řečí.** Kromě velikosti stažení po uživateli chce dvě věci, které za něj nikdo neudělá: založit token a **odsouhlasit licence tří gated repozitářů v prohlížeči** (`check-deps.sh --diarize` je vypíše jmenovitě). Vypiš mu obojí a počkej. Když to odmítne, pokračuj bez rozlišení mluvčích – zbytek skillu funguje beze změny.

Instalace předpokládá [Homebrew](https://brew.sh). Vyvinuto a testováno na macOS.

## Krok 6 – Spusť přepis na pozadí

```bash
WHISPER_MODEL=<turbo|large-v3> \
WHISPER_LANG=<kód jazyka z kroku 1> \
WHISPER_PROMPT="<slovník oddělený čárkami>" \
WHISPER_KEEP_WAV=<0|1> \
<skill>/transcribe.sh <workdir> <workdir>/whisper-progress.log <audio1> <audio2> ...
```

`<workdir>` = adresář vstupní nahrávky. Vzniknou v něm `<name>.txt`, `<name>.srt` a `whisper-progress.log`.

**Skončí-li skript kódem 2 s hláškou o kolizi jmen, ptej se – nerozhoduj sám.** Nastane to, když dvě nahrávky v jednom běhu sdílejí základ jména (`porada.m4a` a `porada.mp4`): výstupy se jmenují podle basename bez přípony, takže by si `.txt` i `.srt` navzájem přepsaly a obě by se přitom ohlásily jako hotové. Skript proto nic nespustí a v logu nechá `### COLLISION <basename>`. (U schůzky spojené v kroku 1 tohle nastat nemůže – do běhu jde jediný soubor.)

Polož **jednu otázku přes `AskUserQuestion`** se dvěma volbami:

- **Zahrnout příponu** – pustíš totéž znovu s `WHISPER_KEEP_EXT=1` a výstupy ponesou i příponu (`porada.m4a.txt`, `porada.mp4.txt`). Zbytek běhu je stejný.
- **Zastavit** – uživatel si nahrávky přejmenuje sám a spustí to znovu. Skonči a řekni, které soubory kolidují.

**Nevybírej za něj ani jedno.** Delší jméno nese celý řetěz až do finálního `<name>.md`, takže je to volba o tom, jak se budou jmenovat výsledné dokumenty – a to ví jen on.

**Skončí-li skript kódem 3, v adresáři už leží výstupy z dřívějška** – `<name>.txt`, `.srt`, `.md`, `.vtt`, `.json` nebo `.wav`. Whisper i ffmpeg přepisují bez ptaní, takže by hodinový přepis zmizel beze stopy; skript proto zase nic nespustí a do logu zapíše `### EXISTING <files>`. Znovu polož **jednu otázku přes `AskUserQuestion`**, tentokrát se třemi volbami:

- **Přepsat** – `WHISPER_ON_EXISTING=overwrite`. Správná volba, když se tatáž nahrávka přepisuje znovu po opravě.
- **Přidat rozlišení** – `WHISPER_ON_EXISTING=suffix`. Nové výstupy dostanou `-2`, `-3` podle prvního volného jména a staré zůstanou ležet.
- **Zastavit** – uživatel si soubory ukliď sám a spustí to znovu. Vypiš, které to jsou.

**Ani tady nevybírej za něj.** Rozdíl mezi „přepsat“ a „nechat vedle“ je rozdíl mezi ztrátou předchozí práce a nepořádkem v adresáři, a co je v tu chvíli menší zlo, ví jen on.

**`WHISPER_KEEP_WAV=1` nastav právě tehdy, když se bude rozlišovat mluvčí.** Diarizace jede nad tímtéž WAV a bez toho by se musel vyrábět znovu. Jinak nech `0`, ať se po sobě uklidí hned. Běh na pozadí upozorní na dokončení (marker `### ALL DONE` v logu).

`WHISPER_CHUNK_MIN` nech nenastavené. Je to náprava podle kroku 7, ne volba pro běžný běh.

**VAD je vždy zapnutý** a není na co se ptát. Vyřazuje ticho, čímž zabíjí celou třídu halucinací („Titulky vytvořil…“, dokola tatáž věta) a zároveň zrychluje běh. Práh je nastavený konzervativně (`-vt 0.35`, `-vp 200`), aby neuřízl tiché mluvčí. Vypnout ho jde přes `WHISPER_VAD=0`, ale sahej po tom jen jako po nápravě podle kroku 7.

Chyba jednoho souboru neshodí zbytek běhu – zapíše se `### FAILED` a pokračuje se dalším. Po doběhnutí zkontroluj, jestli v logu nějaké `### FAILED` není, a **ohlas ho uživateli**. Po běhu po úsecích hledej navíc `### CHUNKSTAT file-N <ok>/<total>`: **soubor s přeskočeným úsekem dostane `### DONE` jako každý jiný**, takže ztráta se jinak nepozná. Nesedí-li obě čísla, řekni uživateli, kolik úseků chybí.

## Krok 7 – Zkontroluj, kolik zvuku se přepsalo

V logu je pro každý úspěšně přepsaný soubor řádek:

```
### SPEECHSTAT <n> <speech_seconds> <total_seconds> <percent>
```

**Pozor, co to číslo je.** Je to součet délek titulků v SRT dělený délkou nahrávky, tedy **kolik zvuku whisper opravdu přepsal** – ne výstup VAD. Stejné číslo vznikne i s `WHISPER_VAD=0`. Nízký podíl proto neukazuje na VAD sám o sobě; může za ním být i tichý mluvčí, šum nebo dlouhé pauzy.

Slouží jako **hrubá pojistka, ne diagnóza**. Když podíl vyjde nezvykle nízko, ohlas ho uživateli s konkrétním číslem a nabídni opakovaný běh s `WHISPER_VAD=0` jako první věc, kterou lze vyloučit. **Nerozhoduj o tom sám** – u nahrávky s dlouhými pauzami je nízký podíl v pořádku. Naměřeno zatím jen na dvou nahrávkách (94 % a 96 % u běžné schůzky dvou lidí), takže žádnou pevnou hranici tenhle skill nestanovuje. **Nepleť si to s čísly u VAD modelu v [`internals.md`](internals.md)** (94,4 % a 96,9 %) – ta jsou z jiného měření, ze dvou nastavení nad jednou a toutéž nahrávkou.

#### Když se v přepisu objeví halucinační smyčka

Dokola tatáž věta, „Titulky vytvořil…“ a podobné nesmysly. VAD a `-sns` je vyřazují už při rozpoznávání a na měřených nahrávkách žádná nevznikla – když se přesto objeví, je **náprava druhý běh po úsecích**:

```bash
WHISPER_CHUNK_MIN=5 <ostatní proměnné jako v kroku 6> <skill>/transcribe.sh …
```

**Pět minut je rozumný začátek, ne doporučená hodnota.** Kratší úsek znamená víc řezů uprostřed vět a víc načtení modelu, delší zase větší ztrátu, když jeden úsek spadne. Pod dvě minuty nechoď – režie načítání modelu by převážila samotný přepis.

Model začíná u každého úseku bez kontextu, takže se smyčka nemá jak šířit dál. **Ta samá volba je jediná záchrana i tehdy, když whisper spadne uprostřed dlouhé nahrávky:** bez ní se ztratí přepis celého souboru, s ní se přeskočí jen postižený úsek (`### CHUNKFAILED file-N i/z` v logu) a zbytek se přepíše.

**Nezapínej to sám a nikdy jako výchozí.** Na každé hranici úseku vzniká řez uprostřed věty – v ostrém testu se okolo něj jedna replika zopakovala nadvakrát. Platí se tím za odstraněnou smyčku, ne za lepší přepis. Zároveň platí, že po takovém běhu **`SPEECHSTAT` klesne o zhruba tolik, kolik zabíraly přeskočené úseky** – nízké číslo je tady informace, ne poplach.

## Krok 8 – Rozliš mluvčí – jen když si to uživatel vybral

Druhý, **samostatný průchod** nad WAV z kroku 6. Když spadne, přepis tím nepřichází vniveč – ohlas selhání a pokračuj krokem 9 bez mluvčích.

```bash
<skill>/diarize.sh <workdir> <workdir>/whisper-progress.log <workdir>/<name>.wav <count|auto>
```

**Jméno WAV ověř, nepredikuj.** Když byl vstupem sám WAV v pracovním adresáři – což u schůzky spojené v kroku 1 platí vždycky, protože `join.sh` vyrábí právě WAV –, dal mu `transcribe.sh` příponu `.16k`; pak se jmenuje `<name>.16k.wav` a `diarize.sh` z něj odvodí `<name>.16k.diarization.json`. **Mění se tím dva soubory z příkazu výš:** cesta k WAV, kterou předáváš `diarize.sh`, i diarizační JSON, který z ní odvodí. **SRT a výstupní základ pro `merge.py` zůstávají** odvozené ze jména vstupní nahrávky.

Do logu přibude `### DIARSTAT <speakers> <segments>` a `### DIARIZE ELAPSED`, ze kterého se kalibruje tempo. Při chybě `### DIARIZE FAILED <reason>`. Když diarizace proběhla, ale statistika se z JSONu nepřečetla, stojí v logu `### DIARSTAT-FAILED <error>` a v `DIARSTAT` je `?` místo čísel – **neuváděj pak počet mluvčích jako nulu**, ta hodnota není známá.

#### Spoj mluvčí s textem

```bash
python3 <skill>/merge.py <workdir>/<name>.srt <workdir>/<name>.diarization.json <workdir>/<name>
```

Vznikne `<name>.json` a `<name>.vtt`. **Oba nesou syrový text z whisperu, ne vyčištěný** – jsou navázané na časové značky, takže přepsat v nich text by je rozešlo s nahrávkou. Vyčištěný text žije jen v `<name>.md`. Neopravuj je ručně.

Přiřazuje se podle **největšího časového překryvu**, protože whisperovy segmenty nekopírují střídání mluvčích. Když je překryv slabý nebo těsný, replika zůstane bez mluvčího – `merge.py` vypíše kolik takových je (`### MERGESTAT <total> <unassigned> <speakers>`).

**Nepřiřazené repliky nedoplňuj odhadem.** Chybné přiřazení vypadá stejně věrohodně jako správné a propíše se až do úkolů ve shrnutí, kde je z něj tvrzení, kdo co slíbil.

#### Zeptej se, kdo je kdo

Až teď, protože dřív nebylo co pojmenovat. Pro každého mluvčího jedna otázka; **návrhy vytáhni z přepisu** – z představování, z oslovování, z toho, kdo o kom mluví ve třetí osobě – a ze slovníku z kroku 3.

**U dvou mluvčích se ptej jednou na dvojici**, ne dvakrát zvlášť. Buď přiřazení sedí, nebo je prohozené – dvě otázky by byly zbytečné kliknutí navíc. Od tří mluvčích výš dej otázku každému.

Vždycky nabídni i možnost nechat mluvčí anonymní. Anonymní mluvčí je lepší než špatně pojmenovaný.

Jména ulož do `<workdir>/.speakers.json` a pusť `merge.py` znovu s `--names`, ať se propíšou do obou výstupů. Zapiš je i do `.transcript-glossary.md`, aby s nimi počítalo čištění i shrnutí.

## Krok 9 – Vyrob výstupy, které si uživatel vybral

**Doslovný přepis.** Pro každou nahrávku zpracuj její `<name>.txt` do `<name>.md` dle [Pravidel doslovného přepisu](output.md#pravidla-doslovného-přepisu). U více nebo delších nahrávek to udělej **paralelně přes subagenty** (jeden na soubor; u spojené schůzky, kde je soubor jediný, rozděl vstup na zhruba stejně velké souvislé části a dej každému agentovi jednu, s překryvem pár vět, ať se na švu neztratí replika. **Rozlišovali-li se mluvčí, dělej řez mezi replikami v `<name>.json`** – ten je nese i se jmény, takže agent dostane rovnou dialog. Jinak děl `<name>.txt` po řádcích. **Nedělej řez podle kapitol:** ty ve vstupu nejsou, mezinadpisy vznikají teprve tím čištěním, které má agent udělat) na **výchozím modelu s `low`** (Volba modelu a effortu podle `~/.claude/RULES.md`, *Model a effort podle úkolu*). Nejlevnější model sem nepatří: oprava přeslechů je úsudek a **vymyšlená věta v přepisu vypadá stejně věrohodně jako správná** – nepozná se jinak než poslechem nahrávky.

**Každému subagentovi předej celý `.transcript-glossary.md`**, ne jen ten výběr, který šel do promptu. Tady platí opak než u whisperu: čím víc kontextu, tím líp. Rozdíl mezi „tohle je zkomolenina, opravím ji“ a „tohle je jejich interní pojem, nechám ho být“ se dá udělat jedině proti úplnému slovníku. Nech si od subagenta vrátit i **stručný brief pro shrnutí** – témata, závěry a kdo co slíbil. Shrnutí pak píšeš z briefů a slovníku, ne z celých přepisů znovu.

Fáze opravy přeslechů zůstává, i když se slovník použil. Slovník zmenší počet chyb, nevynuluje ho – v ostrém běhu prošlo sledované místní jméno zkomolené i s nasazeným promptem.

**Na slovník se proto nedá spolehnout naslepo: jména, na kterých záleží, si v hotovém přepisu ověř.** Projdi je a podívej se, jestli v textu opravdu stojí ve správném tvaru – nestačí, že byla v promptu. Sedí-li špatně soustavně, je na místě slovník přeskládat a nahrávku přepsat znovu; kolik toho složení slovníku rozhodne, drží [`internals.md`](internals.md).

**Doplň slovník o to, co jsi našel při čištění.** Když v přepisu narazíš na termín, který v `.transcript-glossary.md` chybí, dopiš ho tam dřív, než budeš psát shrnutí. Shrnutí pak stojí na stejném slovníku jako přepis.

**[`mishearings.md`](mishearings.md) je při čištění seznam míst, kde se vyplatí dívat pozorně** – ne seznam náhrad ke spuštění. Rozhoduje vždycky věta, ve které slovo stojí; u zkratek se správný tvar liší podle oboru.

**Časovaný přepis.** `<name>.srt` už existuje, vznikl při přepisu. Nech ho ležet vedle `<name>.md`, stejné jméno, jiná přípona. Rozlišení mluvčích ho **nenahrazuje** – `<name>.vtt` a `<name>.json` přibydou vedle něj.

SRT se vyrábí vždycky, protože z něj `transcribe.sh` počítá podíl přepsaného zvuku a `merge.py` bere text pro diarizaci. Když si ho uživatel nevybral, je to mezivýstup a smaže se v úklidu.

**Rozlišení mluvčích mění doslovný přepis na dialog.** Kapitoly a mezinadpisy zůstávají, uvnitř nich se místo odstavců střídají repliky:

```markdown
## Životní cyklus člena

**Tomáš:** Jde o to, že když někdo přijde do AK1, tak je to jasné.

**Jan:** A potom to krystalizuje podle toho, jak vypadají prostory.
```

Repliku bez přiřazeného mluvčího uveď bez jména, ne pod nejbližším mluvčím.

**Shrnutí.** Navrhni uživateli „Výstižný název“ celé nahrávky a **nech si ho odsouhlasit** (ať nemusí nic vymýšlet ani psát), pak zapiš `YYYYMMDD - Výstižný název.md` dle [Formátu souhrnného MD](output.md#formát-souhrnného-md).

## Krok 10 – Úklid

Smaž mezivýstupy: všechny `<name>.txt`, `<name>.wav`, `<name>.16k.wav`, `<name>.diarization.json`, `<name>.16k.diarization.json`, `.speakers.json`, `whisper-progress.log` a `.transcript-glossary.md`. **U spojené schůzky s diarizací leží v adresáři `<name>.wav` i `<name>.16k.wav` zároveň** – první vyrobil `join.sh`, druhý `transcribe.sh`; smaž oba. Ponech zdrojové audio a to, co si uživatel vybral v kroku 4. **Nevybrané výstupy smaž** – když uživatel nechtěl SRT, `<name>.srt` po sobě ukliď, i když mezitím vznikl.

**Zdrojové části spojené schůzky zůstávají** – maže se jen to, co z nich vzniklo.

**Sáhl-li jsi po nápravě z kroku 7 nebo po řezu z kroku 1, ukliď i po nich:** části `<name>-1.*` a `<name>-2.*` ze `split.sh` a prázdné `<name>.txt` / `<name>.srt`, které zůstanou, když se běh po úsecích nepovede ani jednou. Úklid je jmenovitý, takže o souborech, které přibyly nápravou, sám od sebe neví.

**Než slovník smažeš, nabídni přenesení soustavných zkomolenin do [`mishearings.md`](mishearings.md)** – tedy těch, které rozpoznávač dělá u každého, kdo mluví o tomhle oboru, ne jednorázového přeslechu ani jména konkrétní firmy. Kritéria, co tam patří a co ne, drží ten soubor sám.

**Vypiš, co bys doplnil, a zapiš to teprve po odsouhlasení.** `mishearings.md` leží v `~/.claude`, tedy ve verzovaném repozitáři konfigurace, kdežto běh probíhá v adresáři s nahrávkou – zápis bez zeptání by tam po každém přepisu nechal necommitnutou změnu, kterou tam nikdo nečeká a kterou při zapnutém autocommitu posbírá klidně jiná session spolu s něčím nesouvisejícím. Odmítne-li to uživatel, nic nezapisuj a pokračuj; slovník se smaže tak jako tak.

Než slovník smažeš, **vypiš uživateli i termíny, které jsi nechal být** – ty, co modely dávaly konzistentně a vypadají jako interní žargon, a ty, kde je zvuk nesrozumitelný a tvar je tvůj odhad. Ať ví, co má ověřit. Zapiš je i **na konec doslovného přepisu** jako poznámku. Když si uživatel doslovný přepis nevybral, dej tu poznámku na konec shrnutí – nesmí zmizet jen proto, že vznikl jiný výstup.

---

## Krok 11 – Závěr

Vypiš, co vzniklo: u každé nahrávky jméno souboru, délku zdroje a to, které výstupy si uživatel vybral. **Uveď i to, co se nepovedlo nebo přeskočilo** – nízký podíl přepsaného zvuku, nerozlišení mluvčích kvůli chybějícím závislostem, část, která se musela řezat.

**Nese-li nahrávka znalost, která má přežít i po tom, co se přepis zapomene** – výklad na školení, konzultace, cizí prezentace –, nabídni `/learn`.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Přepis je hotový a uklizený, můžeš …`
- `Hotový není – brání tomu: <konkrétní seznam>.`

## Průběžný stav – NEspouštěj automaticky

Opakované časovače zbytečně plýtvají kapacitou. Progress bar vypiš **jen když se uživatel zeptá**, jak to jde:

```bash
python3 <skill>/progress.py <workdir>/whisper-progress.log
```

Ukáže procenta, zpracované a celkové minuty, kolik zbývá, tempo (× realtime) a ETA.

**U běhu po úsecích ukazuje jen dokončené soubory, ne postup uvnitř nahrávky.** Whisper v každém úseku čísluje časy znovu od nuly, takže by se ukazatel na každé hranici vracel zpátky; `progress.py` proto postup uvnitř souboru raději nezapočítá, než aby hlásil nesmysl.

---

## Formát výstupů

**Pravidla doslovného přepisu, formát souhrnného MD i pravidla shrnutí drží [`output.md`](output.md).** Načti si ho, až budeš psát výstup; do těla skillu nepatří, protože během průvodce ani přepisu se nečtou.

## Technické detaily

Naměřené hodnoty, zamítnutá nastavení a vnitřní rozhodnutí drží
**[`internals.md`](internals.md)**. Sáhni tam, když měníš nastavení whisperu nebo
potřebuješ vědět, proč je nějaké číslo zrovna takové – při běžném běhu to číst
nemusíš.

## Soubory skillu

| Soubor | K čemu |
|---|---|
| `check-deps.sh` | kontrola závislostí, volitelně pro konkrétní model |
| `transcribe.sh` | vlastní přepis, řízený proměnnými prostředí; umí i běh po úsecích jako nápravu |
| `common.sh` | cesty k modelům a k VAD, konfigurace diarizace (venv, token, gated repozitáře, název modelu), počet vláken – sourcuje se |
| `rate.py` | odhad a kalibrace tempa (`get`, `eta`, `update`) |
| `progress.py` | progress bar nad logem běhu |
| `detect-lang.sh` | detekce jazyka ze tří vzorků, hlásí i dvojjazyčnost |
| `join.sh` | spojí části jedné schůzky do jedné nahrávky (16 kHz mono WAV) |
| `split.sh` | rozřízne dvojjazyčnou nahrávku na dvě části v zadaném čase |
| `diarize.sh` | volitelný druhý průchod – kdo kdy mluví |
| `diarize.py` | vlastní běh pyannote uvnitř venv |
| `merge.py` | spojí časy z whisperu s mluvčími, vyrobí `.json` a `.vtt` |
| `mishearings.md` | zkomoleniny, které whisper dělá soustavně; čte se v kroku 3, doplňuje v kroku 10 |
| `internals.md` | naměřené hodnoty a vnitřní rozhodnutí – při běhu se nečte |
| `README.md` | popis skillu pro člověka, který ho nezná |
