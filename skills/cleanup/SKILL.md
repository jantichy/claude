---
name: cleanup
description: Skill se použije, když uživatel zadá "/cleanup", nebo chce před koncem či kompaktací session uklidit po sobě projekt – zapsat vše dohodnuté do MD souborů, odstranit nekonzistence, ověřit testy a standardy, mít čistý Git a jistotu, že nová session naváže bez ztráty kontextu.
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent, Skill, AskUserQuestion]
---

# Cleanup (úklid po session)

## Úvodní hláška (vždy jako první)

Než začneš cokoliv dělat, vypiš uživateli přesně tento jeden řádek:

Autor skillu: **Jan Tichý** · jantichy@jantichy.cz · Celá konfigurace Claude vč. všech skillů: https://github.com/jantichy/claude

Teprve pak pokračuj plněním skillu.

## Co skill dělá

Uživatel je na konci nějakého problému a chystá se session opustit nebo zkompaktovat. Tvým úkolem je zajistit, aby po něm zůstalo **čisto a jasno**:

1. **Nic se neztratí** – úplně vše, co se v session řešilo, na čem jste se dohodli, k čemu jste došli, je zapsané v příslušných souborech. Nová session nesmí přijít o žádnou informaci, dohodu, princip, výstup ani závěr.
2. **Nic není nepravdivé** – nová session nesmí vycházet z něčeho, co už neplatí. Žádné nekonzistence, redundance, protichůdné informace, zbytky po zrušených konceptech.
3. **Projekt je v konzistentním stavu** – testy procházejí, kód splňuje standardy a konvence, README / TODO / CLAUDE.md jsou aktuální, Git je čistý a vše je commitnuté a pushnuté.

Skill je **opakovatelný**. Když ho uživatel spustí podruhé, co je zapsané a v pořádku, projde bez zásahu – druhý průchod slouží jako verifikace.

## Zásady pro celý průběh

- **Dvourychlostní režim.** Jednoznačné a mechanické věci dělej rovnou sám a jen je vypiš. Sporné věci předkládej uživateli jeden po druhém, nikdy víc najednou.
  - **Dělej sám:** zápis jednoznačné dohody na zjevně správné místo, oprava rozbitého odkazu nebo nesedícího počtu, aktualizace README / TODO / CLAUDE.md, spuštění testů a kontrol, commit a push.
  - **Předlož uživateli:** kam co patří, když to není zřejmé; restrukturalizace nebo přesuny souborů; dvě protichůdné informace, kde není jasné, která platí; nedořešené otázky; cokoliv, co jde nad rámec toho, co v session padlo.
- **Ptej se vždy přes tool `AskUserQuestion`**, nikdy ne vypsáním voleb jako textu v odpovědi. Uživatel si tak vybírá šipkami a Enterem, místo aby psal písmena. Platí pro každou otázku v celém skillu – sporné položky ve Fázi 3, selhání kontrol ve Fázi 4b i cokoliv dalšího. Jedno volání = jedna otázka (`multiSelect: false`), `header` max 12 znaků, `description` u každé volby konkrétně říká, co se stane. Volbu **Other** doplňuje tool sám – uživatel přes ni napíše vlastní instrukci nebo se doptá; ber to jako doplňující instrukci k dané položce, ne jako odmítnutí, a po vyřešení se zeptej znovu.
- Řiď se `~/.claude/RULES.md` (zejména *Pravda v souborech, ne v konverzaci*, *Single source of truth*, *K pravidlům ukládat i „proč"*, *Živá struktura*, *Žádný „smetiště" adresář*). U kódového projektu navíc `~/Dev/claude/CODING.md`.
- **Nezakládej nové soubory, když to jde bez nich.** Struktura projektu je daná; hledej v ní správné místo. Když žádné neexistuje, zeptej se, než nějaké vytvoříš.
- Tam, kde jsou nezávislé čtecí operace, používej paralelní tool calls.

------

## Fáze 0 – Pre-flight

Zjisti kontext, ve kterém pracuješ:

1. **Kořen projektu** – pracovní adresář, případně kořen gitového repozitáře.
2. **Projektový `CLAUDE.md`** – přečti celý. Zajímá tě zejména:
   - `### Autocommit` a `### Autoprompt` (jsou zapnuté?)
   - `## Consistency` (dříve odmítnuté nálezy – ty znovu neotvírej)
   - `## Výjimky z obecných pravidel`
   - paměťová politika (píše se do Memory, nebo výhradně do `CLAUDE.md`?)
3. **Git** – je to repozitář? Má remote? Aktuální větev, `git status`.
4. **Typ projektu** – odvoď z obsahu, protože určuje, co má smysl kontrolovat ve Fázi 4:
   - **kódový** – `package.json`, `pyproject.toml`, `tests/`, zdrojové adresáře
   - **dokumentační / znalostní** – převažují MD soubory, žádný build ani testy
   - **smíšený** – dokumentace i kód
   - **webové rozhraní** – pokud ano, načti závazný checklist `~/Dev/claude/WEB.md`
5. **Dokumentační mapa** – jaké soubory jsou v projektu nositeli pravdy: `README.md`, `CLAUDE.md`, `TODO.md`, `docs/*`, specializované soubory. Zapamatuj si, co je čí doména.

Zjištěné shrň uživateli do tří až pěti řádků, ať ví, s čím pracuješ, a pokračuj.

------

## Fáze 1 – Rekonstrukce session

**Kritické:** nepracuj jen s tím, co máš právě v kontextu. Pokud už session prošla kompaktací, první polovina konverzace je z kontextu pryč – a přesně tam bývají uzavřené dohody, o které tu jde.

1. **Najdi transcript aktuální session.** Leží v `~/.claude/projects/<slug-pracovního-adresáře>/<session-id>.jsonl`, kde slug vznikne z absolutní cesty nahrazením `/` a `.` pomlčkami (`/Users/honza/Dev/score` → `-Users-honza-Dev-score`). Když si nejsi jistý, který soubor je ten aktuální, vezmi v tom adresáři naposledy modifikovaný `.jsonl` a ověř si obsah proti tomu, co si z konverzace pamatuješ.

2. **Projdi ho od úplného začátku.** Zajímají tě uživatelovy prompty i tvoje odpovědi. U dlouhé session (řádově stovky kB a víc) na to pošli subagenta, ať ti kontext nesnědla surová data – předej mu cestu k souboru a seznam kategorií níže a nech si vrátit strukturovaný výtah.

   **Pozor na zprávy poslané uprostřed běžícího tahu.** Ty **nejsou** uložené jako `type: "user"`, ale jako `type: "queue-operation"` s `operation: "enqueue"` a textem v poli `content`. Kdo filtruje jen `type=="user"`, tiše o ně přijde – a přitom to bývají důležité dovětky („ještě ať to udělá i…"). Vytáhni je vždy taky:
   ```
   jq -r 'select(.type=="queue-operation" and .operation=="enqueue") | .content' <transcript>
   ```
   Stejná past hrozí u `type: "attachment"`. Když si nejsi jistý, že máš všechno, projdi si rozložení `.type` v souboru (`grep -o '"type":"[a-z_-]*"' <transcript> | sort | uniq -c`) a ověř, že jsi nic nevynechal.

3. **Vytěž šest kategorií:**

   1. **Dohody a rozhodnutí** – na čem jste se shodli. Vždy včetně **„proč"** a **zavržených variant**: „nejdřív jsme chtěli X, ale kvůli Y jsme zvolili Z". Samotný závěr bez zdůvodnění je pro příští session málo – nebude vědět, proč to tak je, a hraniční případy vyhodnotí špatně.
   2. **Pravidla a konvence**, které v session vznikly nebo se změnily.
   3. **Odvedená práce** – co se reálně změnilo v souborech a kódu.
   4. **Nedořešené** – odložené úkoly, věci označené „na to se ještě podíváme", „to necháme na potom".
   5. **Postřehy mimo hlavní osu** – všechno, u čeho padlo „ať se to neztratí", „poznamenej si to", „to je důležité do budoucna". Bývá to mimo téma session, a proto to nejčastěji zapadne.
   6. **Korekce** – místa, kde uživatel změnil směr, opravil tě nebo něco zavrhl. **Platí vždy poslední verze**, ne ta první. Pozor na dohody, které v půlce session přestaly platit – ty se nesmí zapsat jako platné.

4. Výsledkem je interní seznam položek. Uživateli zatím nic nepředkládej.

------

## Fáze 2 – Konfrontace se soubory

Pro **každou** položku z Fáze 1 ověři čtením souborů, jestli už je zapsaná a v jakém stavu:

- **OK** – je zapsaná na správném místě a ve správném znění → neřeš
- **Chybí** – nikde není → zapiš
- **Zastaralá** – je zapsaná, ale ve znění, které už neplatí → přepiš
- **Špatné místo** – je zapsaná jinde, než kam podle struktury patří → přesuň
- **Duplicitní** – je na víc místech → nech na jednom, ostatní ať jen odkazují

**Kam co patří** (odvoď od skutečné struktury projektu, tohle je obecné vodítko):

| Typ položky | Cílové místo |
|---|---|
| Pravidla, konvence, jak se v projektu pracuje | projektový `CLAUDE.md` |
| Rozhodnutí a jejich zdůvodnění, zavržené varianty | `docs/` (soubor typu rozhodnutí/ADR), jinak `CLAUDE.md` |
| Úkoly a odložené věci | `TODO.md` |
| Otevřené otázky čekající na rozhodnutí uživatele | sekce `## Otevřené otázky` v `TODO.md` |
| Změny dotýkající se toho, co projekt je a umí | `README.md` |
| Doménová specifika (model, procesy, katalogy) | příslušný soubor v `docs/` |
| Cokoliv v Memory | **přesuň do projektového `CLAUDE.md`**, pokud projekt nemá explicitně povolenou Memory |

Když u položky není jasné, kam patří, **zeptej se** – ale až ve Fázi 3, v jednom společném průchodu, ne rozsypaně.

------

## Fáze 3 – Zápis

1. **Mechanické zápisy proveď rovnou.** Po dokončení vypiš stručný seznam: co bylo dopsáno, kam, a jednou větou proč.

2. **Sporné položky předlož jednu po druhé** ve stejné mechanice jako `/consistency`. Nejdřív položku vypiš:

```
---
[N/celkem] NÁZEV POLOŽKY

Z session: [co v session padlo, případně citace]
Stav: [chybí / zastaralé / špatné místo / duplicita / nejasné zařazení]

Návrh: [konkrétně co kam zapsat nebo jak přepsat – ne vágně „doplnit dokumentaci"]
```

   Pak se zeptej **přes tool `AskUserQuestion`** (viz Zásady výše) – jedno volání na jednu položku, `header` `Položka N/celkem`, `question` shrnuje položku jednou větou, volby **Opravit** / **Odložit** / **Přeskočit**. U položky s nejasným zařazením nabídni místo toho **konkrétní cílové soubory** jako volby (např. `CLAUDE.md` / `docs/rozhodnuti.md` / `TODO.md`) – je to rychlejší než se ptát dvakrát.

3. **Piš tak, aby to bylo čisté, jasné, systematické, čitelné a přímočaré.** Když při zápisu narazíš na to, že okolní text je rozbředlý, redundantní nebo si protiřečí, přestrukturuj ho – to je smyslem úklidu, ne zásah nad rámec zadání.

4. **Průběžně commituj**, pokud má projekt zapnutý autocommit.

------

## Fáze 4 – Úklid a technická brána

### 4a – Konzistence

Spusť skill `/consistency`. Neopakuj jeho práci vlastními silami – je to jediné místo, kde pravidla pro hledání nekonzistencí žijí. Po jeho doběhnutí pokračuj.

### 4b – Testy a kontroly

Podle typu projektu z Fáze 0. **Každý krok vypiš zvlášť s jeho výsledkem**, ať je vidět, co se skutečně ověřilo.

- **Testy** – všechny sady, které projekt má (najdi je v `package.json` scripts, `Makefile`, `tests/`, README). Spusť je všechny, ne jen jednu.
- **Typecheck / lint / build** – `tsc --noEmit`, eslint/biome, build script, pokud existují a jsou rychlé.
- **Coding standards** – soulad s `~/Dev/claude/CODING.md` a projektovými konvencemi. U webového rozhraní projdi checklist `~/Dev/claude/WEB.md`.
- **Nekódový projekt** – tahle část odpadá. **Řekni to explicitně** („projekt nemá testy ani build, technická kontrola se neprováděla"), ať nevzniká dojem, že se něco ověřilo.

**Když něco selže: upozorni a zeptej se.** Vypiš, co selhalo a s jakým výstupem, a zeptej se přes `AskUserQuestion` s volbami **Opravit a pokračovat** / **Pokračovat bez opravy** / **Zastavit úklid**. **Nikdy selhání nezameť** a nikdy netvrď, že je hotovo, když testy neprocházejí – pokud se pokračuje bez opravy, musí to být vidět ve verdiktu ve Fázi 6.

### 4c – Aktuálnost hlavních souborů

Explicitně ověř a případně dorovnej:

- **`README.md`** – odpovídá tomu, co projekt dnes je a umí? Promítly se do něj všechny změny ze session, které se ho dotýkají?
- **Všechny `TODO`** – nejen `TODO.md` v rootu, ale i případné další. Hotové položky odškrtnuté nebo odstraněné, nové doplněné, odložené věci ze session zaznamenané.
- **`CLAUDE.md`** – projektový i případné vnořené. Platí, co je v nich napsané? Nezůstalo tam pravidlo, které v session přestalo platit?

### 4d – Git

- `git status` musí být **čistý** – žádné rozpracované ani neotrackované soubory. Co tam být nemá, patří do `.gitignore`; co tam patří, se commitne.
- Všechno **commitnuté** s výstižnými zprávami.
- Když má repozitář remote, všechno **pushnuté**.
- Ověř výsledek znovu (`git status`, `git log origin/<větev>..HEAD`) – ne že to jen předpokládej.

------

## Fáze 5 – Fresh-reader verifikace

Nejsilnější kontrola celého skillu: ověř, že dokumentace je **soběstačná a pravdivá** pro někoho, kdo nemá žádný kontext z téhle session.

Spusť subagenta s tímto zadáním (doplň absolutní cestu k repozitáři a pořadí souborů ke čtení podle dokumentační mapy z Fáze 0):

```
Jsi vývojář, který **poprvé** přichází k projektu. Nemáš žádný kontext z předchozích rozhovorů – máš jen repozitář. Tvým úkolem je zjistit, jestli je dokumentace **soběstačná a pravdivá**, tedy jestli z ní jde pokračovat v práci bez doptávání.

REPOZITÁŘ: <absolutní cesta>

Přečti si v tomhle pořadí (jako by ses do projektu zaučoval):
<seznam souborů v pořadí od obecného ke konkrétnímu>

Referenční archivy a generovaný obsah (<vyjmenuj, typicky docs/research/, PROMPTS.md, runtime adresáře>) nečti celé – jen ověř, že soubory, na které se hlavní dokumenty odkazují, existují a sedí čísla kapitol tam, kde se citují.

ODPOVĚZ NA TYTO OTÁZKY:

**A. Co bych měl dělat dál?** Je z dokumentace jednoznačné, jaký je další krok? Kdyby ti někdo řekl „pokračuj", věděl bys jak?

**B. Rozumím tomu, co se navrhuje?** Popiš vlastními slovy jádro projektu a jeho hlavní mechaniku. Kde jsi musel hádat nebo dohledávat?

**C. Rozpory a nepravdy.** Tvrdí někde dokumentace něco, co jinde popírá? Zvlášť sleduj: **počty** (sedí čísla uváděná v textu se skutečným obsahem tabulek a seznamů?), názvy souborů, cest, sekcí a dalších pojmenovaných věcí, hodnoty výčtů, co je v rozsahu a co ne, co je vyřešené a co otevřené.

**D. Chybějící kontext.** Je něco, co dokumenty předpokládají jako známé, ale nikde to nevysvětlují? Odkazují na rozhodnutí, jehož zdůvodnění chybí?

**E. Zastaralé zbytky.** Věty typu „viz níže" / „zatím" / „odloženo" / „zvažuje se", které už neplatí. Sekce, které vypadají jako pozůstatek po přepisování. Odkazy na sekce, soubory nebo pojmy, které neexistují nebo se jmenují jinak. Pozor: části dokumentace se měnily chirurgicky (nahrazením konkrétních vět, přejmenováním sekcí, přečíslováním), takže hrozí zbytky po zrušených konceptech a viséci v křížových odkazech. Aktivně je hledej.

**F. Co bych se musel zeptat?** Vyjmenuj konkrétní otázky, na které bys nenašel odpověď a musel se ptát autora.

VÝSTUP: Strukturovaná odpověď na A–F. U každého nálezu uveď soubor a sekci. Buď konkrétní a **nešetři kritikou** – smyslem je najít místa, kde by nový člověk nebo nová AI session vycházeli z něčeho nepravdivého nebo neúplného. Pokud je něco v pořádku, nepiš to.

Nezapisuj do žádného souboru.
```

**Zpracování nálezů:**

- Každý nález vrať do Fáze 3 a oprav – mechanické sám, sporné s uživatelem.
- Pokud byly opravy netriviální (přepisovala se struktura, měnil se obsah více souborů), **pusť druhého fresh-readera** nad opraveným stavem. Důvod: opravy samy zanášejí nové viséce – přejmenuješ sekci a zapomeneš odkaz, doplníš větu o něčem, co v cílovém souboru mezitím není. První průchod tohle z principu zachytit nemůže.
- Po opravách zopakuj Fázi 4d – vzniklé změny musí být zase commitnuté a pushnuté.

------

## Fáze 6 – Závěr

Vypiš přehled:

```
## Úklid dokončen

**Zapsáno ze session**
- N položek doplněno / M přepsáno / K přesunuto
- [stručný seznam: co, kam]

**Úklid konzistence**
- /consistency: opraveno N, odloženo M, přeskočeno K

**Technická kontrola**
- Testy: [výsledek, nebo „projekt nemá testy"]
- Typecheck / lint / build: [výsledek]
- Coding standards: [výsledek]

**Hlavní soubory**
- README.md: [aktuální / doplněno co]
- TODO: [aktuální / doplněno co]
- CLAUDE.md: [aktuální / doplněno co]

**Git**
- Pracovní strom: [čistý / co zbývá]
- Commity: N, push: [ano / repozitář nemá remote]

**Fresh-reader**
- [verdikt a co z něj vzešlo]

**Odložené položky**
- [seznam, nebo „žádné"]
```

Zakonči **jednoznačným verdiktem** – jednou z těchto dvou vět, nikdy ničím vágním mezi tím:

- `Projekt je uklizený, můžeš session opustit nebo zkompaktovat.`
- `Projekt zatím uklizený není – brání tomu: <konkrétní seznam>.`
