---
name: cleanup
description: Skill se použije, když uživatel zadá "/cleanup", nebo chce před koncem či kompaktací session zapsat všechno, co se v ní domluvilo a zjistilo, do souborů – aby nová session navázala bez ztráty kontextu a nevycházela z něčeho, co už neplatí.
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion]
---

# Cleanup

## Úvodní hláška (vždy jako první)

Než začneš cokoliv dělat, vypiš uživateli přesně tento jeden řádek:

Autor skillu: **Jan Tichý** · jantichy@jantichy.cz · Celá konfigurace Claude vč. všech skillů: https://github.com/jantichy/claude

Teprve pak pokračuj plněním skillu.

## Co skill dělá

Uživatel je na konci nějakého problému a chystá se session opustit nebo zkompaktovat. Tvým jediným úkolem je zajistit, že **nic z téhle session nezůstane jen v konverzaci**:

1. **Nic se neztratí** – vše, co se řešilo, na čem jste se dohodli a k čemu jste došli, je zapsané v souborech. Nová session nesmí přijít o žádnou informaci, dohodu, princip, výstup ani závěr.
2. **Nic není nepravdivé** – nová session nesmí vycházet z něčeho, co v průběhu session přestalo platit.
3. **Je to commitnuté** – práce není hotová, dokud sedí jen v pracovním stromu.

Skill je **opakovatelný**. Když ho uživatel spustí podruhé, co je zapsané a v pořádku, projde bez zásahu – druhý průchod slouží jako verifikace.

## Co skill nedělá

Tohle **není** audit projektu ani technická brána. Nespouštěj `/consistency`, `/code-review` ani `/ultrareview` – uživatel je volá zvlášť a před tímhle skillem. Nespouštěj testy, lint, typecheck ani build a nedělej obecnou revizi souborů nad rámec toho, co ze session vzešlo.

Jediná výjimka: pokud ze session **víš**, že něco zůstalo rozbité (padající test, nedodělaná změna), uveď to ve verdiktu ve Fázi 5. Netvrď, že je hotovo, když není – ale sám to neověřuj a neopravuj.

## Zásady pro celý průběh

- **Dvourychlostní režim.** Jednoznačné a mechanické věci dělej rovnou sám a jen je vypiš. Sporné věci předkládej uživateli jeden po druhém, nikdy víc najednou.
  - **Dělej sám:** zápis jednoznačné dohody na zjevně správné místo, oprava rozbitého odkazu, který tvým zápisem vznikl, dorovnání README / TODO / CLAUDE.md v rozsahu session, commit a push.
  - **Předlož uživateli:** kam co patří, když to není zřejmé; restrukturalizace nebo přesuny souborů; dvě protichůdné informace, kde není jasné, která platí; nedořešené otázky; cokoliv, co jde nad rámec toho, co v session padlo.
- **Ptej se vždy přes tool `AskUserQuestion`**, nikdy ne vypsáním voleb jako textu v odpovědi. Uživatel si tak vybírá šipkami a Enterem, místo aby psal písmena. Jedno volání = jedna otázka (`multiSelect: false`), `header` max 12 znaků, `description` u každé volby konkrétně říká, co se stane. Volbu **Other** doplňuje tool sám – uživatel přes ni napíše vlastní instrukci nebo se doptá; ber to jako doplňující instrukci k dané položce, ne jako odmítnutí, a po vyřešení se zeptej znovu.
- Řiď se `~/.claude/RULES.md` (zejména *Pravda v souborech, ne v konverzaci*, *Single source of truth*, *K pravidlům ukládat i „proč"*, *Živá struktura*, *Žádný „smetiště" adresář*).
- **Nezakládej nové soubory, když to jde bez nich.** Struktura projektu je daná; hledej v ní správné místo. Když žádné neexistuje, zeptej se, než nějaké vytvoříš.
- Tam, kde jsou nezávislé čtecí operace, používej paralelní tool calls.

------

## Fáze 0 – Pre-flight

Zjisti kontext, ve kterém pracuješ:

1. **Kořen projektu** – pracovní adresář, případně kořen gitového repozitáře.
2. **Projektový `CLAUDE.md`** – přečti celý. Zajímá tě zejména `### Autocommit`, `## Výjimky z obecných pravidel` a paměťová politika (píše se do Memory, nebo výhradně do `CLAUDE.md`?).
3. **Git** – je to repozitář? Má remote? Aktuální větev, `git status`.
4. **Dokumentační mapa** – jaké soubory jsou v projektu nositeli pravdy: `README.md`, `CLAUDE.md`, `TODO.md`, `docs/*`, specializované soubory. Zapamatuj si, co je čí doména.

Zjištěné shrň uživateli do tří až pěti řádků, ať ví, s čím pracuješ, a pokračuj.

------

## Fáze 1 – Rekonstrukce session

Tohle je jádro celého skillu. Všechno ostatní je servis kolem něj.

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

Zvlášť projdi hlavní soubory – `README.md`, všechna `TODO` (nejen to v rootu) a `CLAUDE.md` (projektový i vnořené) – a ověř, jestli se do nich promítlo, co ze session vzešlo, a jestli v nich nezůstalo pravidlo, které v session přestalo platit. **Jen v rozsahu session**, ne jako obecná revize obsahu.

Když u položky není jasné, kam patří, **zeptej se** – ale až ve Fázi 3, v jednom společném průchodu, ne rozsypaně.

------

## Fáze 3 – Zápis

1. **Mechanické zápisy proveď rovnou.** Po dokončení vypiš stručný seznam: co bylo dopsáno, kam, a jednou větou proč.

2. **Sporné položky předlož jednu po druhé.** Nejdřív položku vypiš:

```
---
[N/celkem] NÁZEV POLOŽKY

Z session: [co v session padlo, případně citace]
Stav: [chybí / zastaralé / špatné místo / duplicita / nejasné zařazení]

Návrh: [konkrétně co kam zapsat nebo jak přepsat – ne vágně „doplnit dokumentaci"]
```

   Pak se zeptej **přes tool `AskUserQuestion`** (viz Zásady výše) – jedno volání na jednu položku, `header` `Položka N/celkem`, `question` shrnuje položku jednou větou, volby **Zapsat** / **Odložit** / **Přeskočit**. U položky s nejasným zařazením nabídni místo toho **konkrétní cílové soubory** jako volby (např. `CLAUDE.md` / `docs/rozhodnuti.md` / `TODO.md`) – je to rychlejší než se ptát dvakrát.

3. **Piš tak, aby to bylo čisté, jasné, systematické, čitelné a přímočaré.** Když při zápisu narazíš na to, že okolní text je rozbředlý, redundantní nebo si protiřečí, přestrukturuj ho – to je smyslem úklidu, ne zásah nad rámec zadání.

4. **Průběžně commituj**, pokud má projekt zapnutý autocommit.

------

## Fáze 4 – Fresh-reader verifikace

Ověř, že to, co jsi právě zapsal, **dává smysl někomu bez kontextu téhle session**. Není to audit celé dokumentace – zajímá tě, jestli nová session naváže na dnešní práci.

Spusť subagenta s tímto zadáním (doplň absolutní cestu k repozitáři, pořadí souborů ke čtení podle dokumentační mapy z Fáze 0 a **stručné shrnutí toho, co se v session řešilo a kam se to zapsalo**):

```
Jsi vývojář, který **poprvé** přichází k projektu. Nemáš žádný kontext z předchozích rozhovorů – máš jen repozitář.

REPOZITÁŘ: <absolutní cesta>

Předchozí session řešila: <shrnutí témat a seznam souborů, do kterých se zapisovalo>

Přečti si v tomhle pořadí (jako by ses do projektu zaučoval):
<seznam souborů v pořadí od obecného ke konkrétnímu>

Referenční archivy a generovaný obsah (<vyjmenuj, typicky docs/research/, PROMPTS.md, runtime adresáře>) nečti celé.

Soustřeď se na oblasti, kterých se dotýkala poslední session. ODPOVĚZ NA TYTO OTÁZKY:

**A. Co bych měl dělat dál?** Je z dokumentace jednoznačné, jaký je další krok? Kdyby ti někdo řekl „pokračuj", věděl bys jak?

**B. Rozumím tomu, co se nedávno rozhodlo?** Popiš vlastními slovy, co se v projektu naposledy změnilo a proč. Kde jsi musel hádat nebo dohledávat?

**C. Rozpory a nepravdy.** Tvrdí někde dokumentace něco, co jinde popírá? Zvlášť sleduj počty (sedí čísla v textu se skutečným obsahem tabulek a seznamů?), názvy souborů, cest a sekcí, hodnoty výčtů, co je v rozsahu a co ne, co je vyřešené a co otevřené.

**D. Chybějící kontext.** Předpokládá se něco jako známé, ale nikde to není vysvětlené? Odkazuje se na rozhodnutí, jehož zdůvodnění chybí?

**E. Zastaralé zbytky.** Věty typu „viz níže" / „zatím" / „odloženo" / „zvažuje se", které už neplatí. Odkazy na sekce, soubory nebo pojmy, které neexistují nebo se jmenují jinak. Do dokumentace se zasahovalo chirurgicky, takže hrozí zbytky po zrušených konceptech a viséci v křížových odkazech – aktivně je hledej.

**F. Co bych se musel zeptat?** Konkrétní otázky, na které bys nenašel odpověď.

VÝSTUP: Strukturovaná odpověď na A–F. U každého nálezu uveď soubor a sekci. Buď konkrétní a **nešetři kritikou**. Pokud je něco v pořádku, nepiš to.

Nezapisuj do žádného souboru.
```

**Zpracování nálezů:**

- Nálezy, které se týkají téhle session, vrať do Fáze 3 a oprav – mechanické sám, sporné s uživatelem.
- Nálezy mimo rozsah session (starší dluh v dokumentaci) **neopravuj** – vypiš je ve verdiktu jako doporučení pustit `/consistency`.
- Pokud byly opravy netriviální (přepisovala se struktura, měnil se obsah více souborů), **pusť druhého fresh-readera** nad opraveným stavem. Důvod: opravy samy zanášejí nové viséce – přejmenuješ sekci a zapomeneš odkaz, doplníš větu o něčem, co v cílovém souboru mezitím není.

------

## Fáze 5 – Git a závěr

**Git:**

- `git status` musí být **čistý** – žádné rozpracované ani neotrackované soubory. Co tam být nemá, patří do `.gitignore`; co tam patří, se commitne.
- Všechno **commitnuté** s výstižnými zprávami.
- Když má repozitář remote, všechno **pushnuté**.
- Ověř výsledek znovu (`git status`, `git log origin/<větev>..HEAD`) – ne že to jen předpokládej.

**Přehled:**

```
## Úklid dokončen

**Zapsáno ze session**
- N položek doplněno / M přepsáno / K přesunuto
- [stručný seznam: co, kam]

**Fresh-reader**
- [verdikt a co z něj vzešlo]

**Git**
- Pracovní strom: [čistý / co zbývá]
- Commity: N, push: [ano / repozitář nemá remote]

**Odložené položky**
- [seznam, nebo „žádné"]

**Mimo rozsah úklidu**
- [rozbité věci známé ze session, nálezy na starší dluh – nebo „žádné"]
```

Zakonči **jednoznačným verdiktem** – jednou z těchto dvou vět, nikdy ničím vágním mezi tím:

- `Ze session je všechno zapsané, můžeš ji opustit nebo zkompaktovat.`
- `Zapsané zatím není všechno – brání tomu: <konkrétní seznam>.`
