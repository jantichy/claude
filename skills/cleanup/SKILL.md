---
name: cleanup
description: Skill se použije, když uživatel zadá "/cleanup" nebo "/cleanup full", nebo chce před koncem či kompaktací session zapsat všechno, co se v ní domluvilo a zjistilo, do souborů – aby nová session navázala bez ztráty kontextu a nevycházela z něčeho, co už neplatí.
argument-hint: [full]
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion]
---

# Cleanup

## Co skill dělá

Uživatel je na konci nějakého problému a chystá se session opustit nebo zkompaktovat. Tvým jediným úkolem je zajistit, že **nic z téhle session nezůstane jen v konverzaci**:

1. **Nic se neztratí** – vše, co se řešilo, na čem jste se dohodli a k čemu jste došli, je zapsané v souborech. Nová session nesmí přijít o žádnou informaci, dohodu, princip, výstup ani závěr.
2. **Nic není nepravdivé** – nová session nesmí vycházet z něčeho, co v průběhu session přestalo platit.
3. **Je to commitnuté** – práce není hotová, dokud sedí jen v pracovním stromu.

Skill je **opakovatelný**. Když ho uživatel spustí podruhé, co je zapsané a v pořádku, projde bez zásahu – druhý průchod slouží jako verifikace.

## Co skill nedělá

Tohle **není** audit projektu ani technická brána. Nespouštěj `/consistency`, `/code-review` ani `/code-review ultra` – uživatel je volá zvlášť a před tímhle skillem. Nespouštěj testy, lint, typecheck ani build a nedělej obecnou revizi souborů nad rámec toho, co ze session vzešlo.

Jediná výjimka: pokud ze session **víš**, že něco zůstalo rozbité (padající test, nedodělaná změna), uveď to ve verdiktu ve Fázi 5. Netvrď, že je hotovo, když není – ale sám to neověřuj a neopravuj.

## Rozsah fresh-reader kontroly

- **`/cleanup`** (výchozí) – fresh-reader ve Fázi 4 se soustředí na to, čeho se dotkla tahle session. Nálezy mimo její rozsah jen vypíše jako doporučení, neopravuje je.
- **`/cleanup full`** – fresh-reader projde celou dokumentaci projektu bez omezení na session a nálezy se řeší všechny. Použij, jen když uživatel napíše `full`.

Rozsah ovlivňuje **výhradně Fázi 4**. Fáze 1–3 vytěžují session vždy celou – to je smysl skillu a nedá se zúžit ani rozšířit.

## Zásady pro celý průběh

- **Dvourychlostní režim.** Jednoznačné a mechanické věci dělej rovnou sám a jen je vypiš. Sporné věci předkládej uživateli jeden po druhém, nikdy víc najednou.
  - **Dělej sám:** zápis jednoznačné dohody na zjevně správné místo, oprava rozbitého odkazu, který tvým zápisem vznikl, dorovnání README / TODO / CLAUDE.md v rozsahu session, commit a push.
  - **Předlož uživateli:** kam co patří, když to není zřejmé; restrukturalizace nebo přesuny souborů; dvě protichůdné informace, kde není jasné, která platí; nedořešené otázky; cokoliv, co jde nad rámec toho, co v session padlo.
- **Ptej se vždy přes tool `AskUserQuestion`** – mechanika toolu viz `~/.claude/RULES.md`, *Ptej se postupně, ne všechno najednou*.
- Řiď se `~/.claude/RULES.md` (zejména *Pravda v souborech, ne v konverzaci*, *Single source of truth*, *K pravidlům ukládej i „proč“*, *Živá struktura*, *Naming – jedno výstižné slovo*).
- **Nezakládej nové soubory, když to jde bez nich.** Struktura projektu je daná; hledej v ní správné místo. Když žádné neexistuje, zeptej se, než nějaké vytvoříš.
- Tam, kde jsou nezávislé čtecí operace, používej paralelní tool calls.

------

## Fáze 0 – Pre-flight

Zjisti kontext, ve kterém pracuješ:

1. **Kořen projektu** – pracovní adresář, případně kořen gitového repozitáře.
2. **Projektový `CLAUDE.md`** – přečti celý. Zajímá tě zejména `### Autocommit`, `## Výjimky z obecných pravidel` a paměťová politika (píše se do Memory, nebo výhradně do `CLAUDE.md`?).
3. **Git** – je to repozitář? Má remote? Aktuální větev, `git status`.
4. **Dokumentační mapa** – jaké soubory jsou v projektu nositeli pravdy. Standardní struktura je `CLAUDE.md`, `README.md` a v `docs/` čtveřice `todo.md`, `done.md`, `decisions.md`, `rules.md`, podle potřeby doplněná o `requirements.md`, `architecture.md` a `plan.md`; k tomu specializované soubory projektu. **Autoritativní je `~/Dev/context/structure/structure.md`** – rozejde-li se s tímhle výčtem, platí on. Zapamatuj si, co je čí doména, a zaznamenej, které ze standardních souborů v projektu chybí.

Zjištěné shrň uživateli do tří až pěti řádků, ať ví, s čím pracuješ, a pokračuj.

------

## Fáze 1 – Rekonstrukce session

Tohle je jádro celého skillu. Všechno ostatní je servis kolem něj.

**Kritické:** nepracuj jen s tím, co máš právě v kontextu. Pokud už session prošla kompaktací, první polovina konverzace je z kontextu pryč – a přesně tam bývají uzavřené dohody, o které tu jde.

1. **Najdi transcript aktuální session.** Leží v `~/.claude/projects/<slug-pracovního-adresáře>/<session-id>.jsonl`, kde slug vznikne z absolutní cesty nahrazením `/` a `.` pomlčkami (`/Users/honza/Dev/score` → `-Users-honza-Dev-score`). Když si nejsi jistý, který soubor je ten aktuální, vezmi v tom adresáři naposledy modifikovaný `.jsonl` a ověř si obsah proti tomu, co si z konverzace pamatuješ.

2. **Projdi ho od úplného začátku.** Zajímají tě uživatelovy prompty i tvoje odpovědi. U dlouhé session (řádově stovky kB a víc) na to pošli subagenta, ať ti kontext nesnědla surová data – předej mu cestu k souboru a seznam kategorií níže a nech si vrátit strukturovaný výtah.

   **Pozor na zprávy poslané uprostřed běžícího tahu.** Ty **nejsou** uložené jako `type: "user"`, ale jako `type: "queue-operation"` s `operation: "enqueue"` a textem v poli `content`. Kdo filtruje jen `type=="user"`, tiše o ně přijde – a přitom to bývají důležité dovětky („ještě ať to udělá i…“). Vytáhni je vždy taky:
   ```
   jq -r 'select(.type=="queue-operation" and .operation=="enqueue") | .content' <transcript>
   ```
   Stejná past hrozí u `type: "attachment"`. Když si nejsi jistý, že máš všechno, projdi si rozložení `.type` v souboru (`grep -o '"type":"[a-z_-]*"' <transcript> | sort | uniq -c`) a ověř, že jsi nic nevynechal.

3. **Vytěž šest kategorií:**

   1. **Dohody a rozhodnutí** – na čem jste se shodli. Vždy včetně **„proč“** a **zavržených variant** (viz `~/.claude/RULES.md`, *Rozhodnutí zapisuj i s cestou k nim*): „nejdřív jsme chtěli X, ale kvůli Y jsme zvolili Z“. Samotný závěr bez zdůvodnění je pro příští session málo – nebude vědět, proč to tak je, a hraniční případy vyhodnotí špatně.
   2. **Pravidla a konvence**, které v session vznikly nebo se změnily.
   3. **Odvedená práce** – co se reálně změnilo v souborech a kódu.
   4. **Nedořešené** – odložené úkoly, věci označené „na to se ještě podíváme“, „to necháme na potom“.
   5. **Postřehy mimo hlavní osu** – všechno, u čeho padlo „ať se to neztratí“, „poznamenej si to“, „to je důležité do budoucna“. Bývá to mimo téma session, a proto to nejčastěji zapadne.
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

**Kam co patří** (odvoď od skutečné struktury projektu, tohle je obecné vodítko). Obsah jednotlivých souborů definuje `~/Dev/context/structure/structure.md` – tahle tabulka je jen obrácený pohled od položky k souboru, ne druhá definice:

| Typ položky | Cílové místo |
|---|---|
| Pravidla, konvence, jak se v projektu pracuje | projektový `CLAUDE.md` |
| Rozhodnutí a jejich zdůvodnění, zavržené varianty | `docs/decisions.md` |
| Obecné principy a hranice, ve kterých se projekt pohybuje | `docs/rules.md` |
| Úkoly a odložené věci | `docs/todo.md` |
| Hotové úkoly | `docs/done.md` |
| Otevřené otázky čekající na rozhodnutí uživatele | `docs/todo.md` jako běžná položka |
| Změny dotýkající se toho, co projekt je, umí a jak se používá – **popis pro člověka**, nikdy pokyn pro Clauda | `README.md` |
| Doménová specifika (model, procesy, katalogy) | příslušný soubor v `docs/` |
| Cokoliv v Memory | **přesuň do projektového `CLAUDE.md`**, pokud projekt nemá explicitně povolenou Memory |

Zvlášť projdi hlavní soubory – `README.md`, `docs/todo.md`, `docs/done.md`, `docs/decisions.md`, `docs/rules.md` a `CLAUDE.md` (projektový i vnořené) – a ověř, jestli se do nich promítlo, co ze session vzešlo, a jestli v nich nezůstalo pravidlo, které v session přestalo platit. **Jen v rozsahu session**, ne jako obecná revize obsahu.

Když u položky není jasné, kam patří, **zeptej se** – ale až ve Fázi 3, v jednom společném průchodu, ne rozsypaně.

------

## Fáze 2b – Ověř, že průběžná aktualizace opravdu proběhla

`~/Dev/context/structure/structure.md` ukládá udržovat sadu souborů **průběžně během celé session, bez vyžádání**. Tahle fáze ověřuje, jestli se to skutečně dělo. Je to **opačný pohled než Fáze 2**: tam ověřuješ, kam patří položky, které jsi vytěžil; tady ověřuješ, jestli nezůstala nesplněná povinnost.

Neber jako samozřejmé, že aktualizace proběhla. **Empiricky se na ni zapomíná** – proto tenhle krok existuje a proto se nedá odbýt.

### Postup

1. **Zjisti, kdy se každý ze souborů naposledy měnil.** U projektu s gitem `git log --oneline -3 -- <soubor>` a `git status`; jinak čas modifikace. Zajímá tě, jestli se soubor během téhle session vůbec dotkl.

   ```
   CLAUDE.md  README.md  docs/todo.md  docs/done.md  docs/decisions.md  docs/rules.md
   ```

   Má-li projekt zadání, přidej k nim `docs/requirements.md`, `docs/architecture.md` a `docs/plan.md`. Má-li projekt kód, ověř i **`## Příkazy`** v `CLAUDE.md` (*Kontrakt příkazů*) – přibyl-li během session příkaz, kterým se něco spouští, patří tam.
   Neexistují-li, přeskoč je – nezakládají se tady.

2. **Projdi celou session znovu** – celý transcript z Fáze 1, ne jen vytěžený seznam – a u každého souboru se ptej, co do něj **mělo** během session přibýt:

   | Soubor | Co v session zakládá povinnost zápisu |
   |---|---|
   | `CLAUDE.md` | vzniklo nebo se změnilo pravidlo, konvence, způsob práce v projektu |
   | `README.md` | změnilo se, co projekt je, umí nebo jak se spouští; zároveň ověř, že v něm nezůstal normativní pokyn pro Clauda – ten patří do `CLAUDE.md` nebo `docs/`, viz `~/Dev/context/structure/structure.md` |
   | `docs/todo.md` | něco se odložilo, zaparkovalo, označilo „později“ |
   | `docs/done.md` | ověř, že v `todo.md` nezbylo nic hotového – přesouvá se průběžně, tohle je jen záchranná síť |
   | `docs/decisions.md` | padlo rozhodnutí, zvolila se varianta, něco se zamítlo, změnil se názor |
   | `docs/rules.md` | vybrousil se princip, hranice, „takhle to v tomhle projektu děláme vždycky“ |
   | `docs/requirements.md` | změnil se produktový záměr – co se staví, pro koho, co je v MVP a co mimo rozsah |
   | `docs/architecture.md` | změnil se návrh řešení – architektura, datový model, stavy, technologie, bezpečnostní model |
   | `CLAUDE.md` → `## Příkazy` | přibyl nebo se změnil příkaz na testy, lint, build nebo audit |
   | `docs/plan.md` | odpracovaly se úkoly (odškrtnout), nebo se plán rozešel se skutečností |

3. **Porovnej s tím, co v souborech skutečně je.** Nestačí, že se soubor během session změnil – ověř, že obsahuje **všechno**, co tam podle bodu 2 patří.

4. **Chybějící doplň zpětně z celé session.** Ne jen holé odrážky – ve stejné kvalitě, jako by to bylo zapsané v okamžiku, kdy to padlo:
   - u rozhodnutí i **proč**, jaké varianty byly ve hře a proč padly,
   - u odložených věcí **celou úvahu**, ne jen název,
   - u principů **obecnou formulaci**, ne popis jednoho případu.

   Zároveň **přeformuluj**, co bylo zapsáno ve spěchu nebo se od té doby posunulo. Platí poslední verze, ne první.

5. **Nahlas výsledek** – i když je čistý:

   ```
   Průběžná aktualizace: docs/decisions.md – 3 rozhodnutí doplněna zpětně
                         docs/todo.md      – OK
                         docs/rules.md     – 1 princip doplněn
                         CLAUDE.md         – OK
                         README.md         – OK
   ```

   Doplňoval-li jsi hodně, řekni to uživateli otevřeně jako selhání průběžné aktualizace, ne jako běžnou práci úklidu. Je to informace o tom, že mechanismus nefungoval.

### Když soubory neexistují

Chybí-li některý ze standardních souborů úplně, **nezakládej ho tady potichu**. Vypiš, které chybí, a nabídni spuštění `/project`, který strukturu doplní celou a konzistentně. Výjimka: má-li session obsah, který do chybějícího souboru jednoznačně patří, soubor založ a obsah zapiš – jinak by se ztratil.

Nedává-li standardní struktura pro tenhle projekt smysl (jednorázový scratch, cizí read-only repozitář), konstatuj to jednou větou a fázi přeskoč.

------

## Fáze 3 – Zápis

1. **Mechanické zápisy proveď rovnou.** Po dokončení vypiš stručný seznam: co bylo dopsáno, kam, a jednou větou proč.

2. **Sporné položky předlož jednu po druhé.** Nejdřív položku vypiš:

```
---
[N/celkem] NÁZEV POLOŽKY

Z session: [co v session padlo, případně citace]
Stav: [chybí / zastaralé / špatné místo / duplicita / nejasné zařazení]

Návrh: [konkrétně co kam zapsat nebo jak přepsat – ne vágně „doplnit dokumentaci“]
```

   Pak se zeptej **přes tool `AskUserQuestion`** (viz Zásady výše) – jedno volání na jednu položku, `header` `Položka N/celkem`, `question` shrnuje položku jednou větou, volby **Zapsat** / **Odložit** / **Přeskočit**. U položky s nejasným zařazením nabídni místo toho **konkrétní cílové soubory** jako volby (např. `CLAUDE.md` / `docs/decisions.md` / `docs/todo.md`) – je to rychlejší než se ptát dvakrát.

3. **Piš tak, aby to bylo čisté, jasné, systematické, čitelné a přímočaré.** Když při zápisu narazíš na to, že okolní text je rozbředlý, redundantní nebo si protiřečí, přestrukturuj ho – to je smyslem úklidu, ne zásah nad rámec zadání.

4. **Průběžně commituj**, pokud má projekt zapnutý autocommit.

------

## Fáze 4 – Fresh-reader verifikace

Ověř, že to, co jsi právě zapsal, **dává smysl někomu bez kontextu téhle session**. Ve výchozím rozsahu to není audit celé dokumentace – zajímá tě, jestli nová session naváže na dnešní práci. V režimu `full` naopak projdi dokumentaci celou (viz *Rozsah fresh-reader kontroly* výše) a v zadání pro subagenta vynech řádek se shrnutím session i větu o soustředění se na poslední session.

Spusť subagenta s tímto zadáním (doplň absolutní cestu k repozitáři, pořadí souborů ke čtení podle dokumentační mapy z Fáze 0 a **stručné shrnutí toho, co se v session řešilo a kam se to zapsalo**):

```
Jsi vývojář, který **poprvé** přichází k projektu. Nemáš žádný kontext z předchozích rozhovorů – máš jen repozitář.

REPOZITÁŘ: <absolutní cesta>

Předchozí session řešila: <shrnutí témat a seznam souborů, do kterých se zapisovalo>

Přečti si v tomhle pořadí (jako by ses do projektu zaučoval):
<seznam souborů v pořadí od obecného ke konkrétnímu>

Referenční archivy a generovaný obsah (<vyjmenuj, typicky docs/research/, docs/prompts.md, runtime adresáře>) nečti celé.

Soustřeď se na oblasti, kterých se dotýkala poslední session. ODPOVĚZ NA TYTO OTÁZKY:
<v režimu `full` tenhle odstavec vynech – procházej dokumentaci celou>

**A. Co bych měl dělat dál?** Je z dokumentace jednoznačné, jaký je další krok? Kdyby ti někdo řekl „pokračuj“, věděl bys jak?

**B. Rozumím tomu, co se nedávno rozhodlo?** Popiš vlastními slovy, co se v projektu naposledy změnilo a proč. Kde jsi musel hádat nebo dohledávat?

**C. Rozpory a nepravdy.** Tvrdí někde dokumentace něco, co jinde popírá? Zvlášť sleduj počty (sedí čísla v textu se skutečným obsahem tabulek a seznamů?), názvy souborů, cest a sekcí, hodnoty výčtů, co je v rozsahu a co ne, co je vyřešené a co otevřené.

**D. Chybějící kontext.** Předpokládá se něco jako známé, ale nikde to není vysvětlené? Odkazuje se na rozhodnutí, jehož zdůvodnění chybí?

**E. Zastaralé zbytky.** Věty typu „viz níže“ / „zatím“ / „odloženo“ / „zvažuje se“, které už neplatí. Odkazy na sekce, soubory nebo pojmy, které neexistují nebo se jmenují jinak. Do dokumentace se zasahovalo chirurgicky, takže hrozí zbytky po zrušených konceptech a viséci v křížových odkazech – aktivně je hledej.

**F. Co bych se musel zeptat?** Konkrétní otázky, na které bys nenašel odpověď.

VÝSTUP: Strukturovaná odpověď na A–F. U každého nálezu uveď soubor a sekci. Buď konkrétní a **nešetři kritikou**. Pokud je něco v pořádku, nepiš to.

Nezapisuj do žádného souboru.
```

**Zpracování nálezů:**

- Nálezy, které se týkají téhle session, vrať do Fáze 3 a oprav – mechanické sám, sporné s uživatelem.
- Nálezy mimo rozsah session (starší dluh v dokumentaci) ve výchozím režimu **neopravuj** – vypiš je ve verdiktu jako doporučení pustit `/consistency`. V režimu `full` je řeš stejně jako ostatní.
- Pokud byly opravy netriviální (přepisovala se struktura, měnil se obsah více souborů), **pusť druhého fresh-readera** nad opraveným stavem. Důvod: opravy samy zanášejí nové viséce – přejmenuješ sekci a zapomeneš odkaz, doplníš větu o něčem, co v cílovém souboru mezitím není.

------

## Fáze 5 – Git a závěr

**Git:**

- `git status` musí být **čistý** – žádné rozpracované ani neotrackované soubory. Co tam být nemá, patří do `.gitignore`; co tam patří, se commitne.
- *Worktree layout:* `git status` pouštěj ve worktree větve, ne v kořeni kontejneru – tam by spadl na `must be run in a work tree`. Navíc zkontroluj `git -C <kontejner>/main status`: hook autopromptu tam nechává rozepsaný `docs/prompts.md`, který se commituje právě tady (`git -C <kontejner>/main commit -m "Zaznamenej prompty" docs/prompts.md`). Nic jiného v `main/` rozpracované být nemá – když ano, ohlas to.
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
- [seznam, nebo „žádné“]

**Mimo rozsah úklidu**
- [rozbité věci známé ze session, nálezy na starší dluh – nebo „žádné“]
```

Zakonči **jednoznačným verdiktem** – jednou z těchto dvou vět, nikdy ničím vágním mezi tím:

- `Ze session je všechno zapsané, můžeš ji opustit nebo zkompaktovat.`
- `Zapsané zatím není všechno – brání tomu: <konkrétní seznam>.`
