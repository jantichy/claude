---
name: cleanup
description: Skill se použije, když uživatel zadá "/cleanup", nebo chce před koncem či kompaktací session zapsat všechno, co se v ní domluvilo a zjistilo, do souborů – aby nová session navázala bez ztráty kontextu a nevycházela z něčeho, co už neplatí. Zároveň dohledá témata, která v konverzaci zůstala bez vypořádání, a probere je.
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, Skill]
---

# Cleanup

## Co skill dělá

Uživatel je na konci nějakého problému a chystá se session opustit nebo zkompaktovat. Tvým jediným úkolem je zajistit, že **nic z téhle session nezůstane jen v konverzaci**:

1. **Nic se neztratí** – vše, co se řešilo, na čem jste se dohodli a k čemu jste došli, je zapsané v souborech. Nová session nesmí přijít o žádnou informaci, dohodu, princip, výstup ani závěr.
2. **Nic nezůstalo viset** – žádná otázka, návrh ani upozornění z konverzace nezapadlo bez vypořádání. Co viselo, se probere s uživatelem – ne odloží do závěru jako výčet bez vypořádání.
3. **Nic není nepravdivé** – nová session nesmí vycházet z něčeho, co v průběhu session přestalo platit.
4. **Je to commitnuté** – práce není hotová, dokud sedí jen v pracovním stromu.

Skill je **opakovatelný**. Když ho uživatel spustí podruhé, co je zapsané a v pořádku, projde bez zásahu – druhý průchod slouží jako verifikace.

V *Životním cyklu projektu* (`~/.claude/RULES.md`) je to poslední krok uzavírání – navazuje na `/consistency` a předává na `/attack`, nasazuje-li se. Poslední je i proto, že jako jediný odolá kompaktaci: co zapíše, přežije ztrátu kontextu.

## Co skill nedělá

**Neopakuje, co udělal `/consistency`.** Ten proběhl o krok dřív a prošel soubory dotčené větví (v režimu `full` celý projekt) – jiná otázka, jiný skill; čtenáři bez kontextu se tady ptají na jinou věc – *dá se na dnešní práci navázat?* – a rozpory hledají jen v tom, co dnes přibylo.

Tohle **není** audit projektu ani technická kontrola. Nespouštěj `/consistency`, `/code-review` ani `/code-review ultra` – uživatel je volá zvlášť a před tímhle skillem. **Ani `/attack`**, ten přijde naopak až po tomhle a jako jediný aplikaci spouští, aby ji rozbil. Nespouštěj testy, lint, typecheck ani build a nedělej obecnou revizi souborů nad rámec toho, co ze session vzešlo. **Vlastní kontrola odkazů ve Fázi 6 výjimkou není** – neposuzuje projekt, ale to, co jsi právě zapsal, a běží zlomek vteřiny.

**Výjimka pro dokončení větve:** vybere-li uživatel v závěru *Přimergovat do main*, provedeš postup z `~/.claude/WORKTREE.md`, *Dokončení větve*, celý, i s kontrolami, které předepisuje. Merge sám od sebe neprovádíš.

Druhá výjimka: pokud ze session **víš**, že něco zůstalo rozbité (padající test, nedodělaná změna), vezmi to do Fáze 7 a nech uživatele rozhodnout, co s tím. Netvrď, že je hotovo, když není – ale sám to neověřuj a neopravuj, dokud si to uživatel nevyžádá.

## Jak je to postavené uvnitř

Skill nese jeden vlastní skript: `scripts/links.py` ve Fázi 6 ověří, že relativní odkazy ve změněných Markdownech vedou na existující soubor a kotvy na existující nadpis. Je to **implementační detail, ne rozhraní** – jeho přepínače, výstup i samotná existence se smí změnit bez ohlášení; klidně ho nahradí jiný nástroj nebo git hook. Co se změnit nesmí tiše, je **pravidlo za ním**: mechanické vady hledá deterministický nástroj, ne model (`~/.claude/RULES.md`, *Model a effort podle úkolu*, pravidlo nula), a jeho nálezy se opravují **před** spuštěním čtenářů, ne po něm.

Vynucovací vrstvu k němu drží `tests/test_cleanup.py` – testuje oba směry selhání včetně mutačního testu, který vyřadí vynechávání bloků kódu a ověří, že falešný poplach opravdu vznikne.

Zadání obou čtenářů bez kontextu leží v [`readers.md`](readers.md); **závazné je, že jsou dva a že nemají shell**, ne konkrétní znění otázek.

## Rozsah

**Skill má jediné chování a žádné režimy.** Session se vytěžuje vždycky celá – to je jeho smysl a nedá se to zúžit ani rozšířit. Čtenáři bez kontextu ve Fázi 6 se soustředí na to, čeho se dotkla tahle session; starší dluh v dokumentaci sami neopravují – putuje do Fáze 8, kde se podle kritéria Fáze 7 buď rovnou vyřeší, nebo o něm rozhodne uživatel.

**Audit celé dokumentace sem nepatří** – je to jiná otázka („sedí si projekt sám se sebou?“) a dělá ho `/consistency full` o krok dřív. Dřív tu byl režim `full`, který rozšiřoval čtenáře bez kontextu na celou dokumentaci; zrušen 6. 9. 2026, protože jméno svádělo ke čtení „bez `full` se session neprojde celá“ – a to je přesně naopak.

## Zásady pro celý průběh

- **Dvourychlostní režim.** Jednoznačné a mechanické věci dělej rovnou sám a jen je vypiš. Sporné věci předkládej uživateli jeden po druhém, nikdy víc najednou.
  - **Dělej sám:** zápis jednoznačné dohody na zjevně správné místo, oprava rozbitého odkazu, který tvým zápisem vznikl, dorovnání README / TODO / CLAUDE.md v rozsahu session, commit a push.
  - **Předlož uživateli:** kam co patří, když to není zřejmé; restrukturalizace nebo přesuny souborů; dvě protichůdné informace, kde není jasné, která platí; nedořešené otázky.
  - **Co jde nad rámec session, se neřeší tady**, ale ve Fázi 7 – a u toho, co najdou čtenáři, ve Fázi 8. Rozhoduje o tom kritérium Fáze 7, ne tenhle režim. Jednoznačnou opravu mimo rozsah tedy neodkládej jako „sporné“, jen ji neprováděj uprostřed jiné fáze.
- **Ptej se vždy přes tool `AskUserQuestion`** – mechanika toolu viz `~/.claude/RULES.md`, *Ptej se postupně, ne všechno najednou*.
- Řiď se `~/.claude/RULES.md` (zejména *Pravda v souborech, ne v konverzaci*, *Single source of truth*, *K pravidlům ukládej i „proč“*, *Živá struktura*, *Naming – jedno výstižné slovo*).
- **Nezakládej nové soubory, když to jde bez nich.** Struktura projektu je daná; hledej v ní správné místo. Když žádné neexistuje, zeptej se, než nějaké vytvoříš.
- Tam, kde jsou nezávislé čtecí operace, používej paralelní tool calls.

------

## Fáze 0 – Příprava

**Společný začátek drží `~/.claude/skills/PREFLIGHT.md`** – načti si ho a řiď se jím. Body 4 a 5 odpadají: tenhle skill nesahá na kód a vytěžuje celou session, ne diff větve. U gitu tě navíc zajímá remote, a ten zjišťuj `git remote get-url origin`, ne `git remote` – to druhé vypíše jméno, ne adresu.

Navíc si zjisti tohle:

1. **Základ session** – `git rev-parse HEAD`. Je to commit, na kterém session stála, než cokoliv zapsala; Fáze 6 podle něj skládá seznam změněných souborů a diff pro čtenáře. Zapamatuj si ho hned, protože po prvním commitu autocommitu už ho nezjistíš.
2. **Dokumentační mapa** – jaké soubory jsou v projektu nositeli pravdy. Standardní struktura je `CLAUDE.md`, `README.md` a v `docs/` pětice `todo.md`, `backlog.md`, `done.md`, `decisions.md`, `rules.md`, podle potřeby doplněná o `requirements.md`, `architecture.md` a `plan.md`; k tomu specializované soubory projektu. **Autoritativní je `~/.claude/STRUCTURE.md`** – rozejde-li se s tímhle výčtem, platí on. Zapamatuj si, co je čí doména, a zaznamenej, které ze standardních souborů v projektu chybí.

------

## Fáze 1 – Rekonstrukce session

Tohle je jádro celého skillu: vychází z něj všechno ostatní včetně Fáze 2.

**Jak transcript najít a přečíst, drží `~/.claude/skills/SESSION.md`** – včetně toho, proč se nesmí sáhnout po naposledy modifikovaném souboru a které zprávy se neukládají jako `type: "user"`. Načti si ho a řiď se jím; neopisuj ho sem, potřebuje ho i `/skill` a dvě kopie se rozejdou.

Pak z něj vytěž **sedm kategorií**:

1. **Dohody a rozhodnutí** – na čem jste se shodli. Vždy včetně **„proč“** a **zavržených variant** (viz `~/.claude/RULES.md`, *Rozhodnutí zapisuj i s cestou k nim*): „nejdřív jsme chtěli X, ale kvůli Y jsme zvolili Z“. Samotný závěr bez zdůvodnění je pro příští session málo – nebude vědět, proč to tak je, a hraniční případy vyhodnotí špatně.
2. **Pravidla a konvence**, které v session vznikly nebo se změnily.
3. **Odvedená práce** – co se reálně změnilo v souborech a kódu.
4. **Nedořešené** – odložené úkoly, věci označené „na to se ještě podíváme“, „to necháme na potom“. Tohle je **vědomé** odložení: někdo ho vyslovil. Co propadlo, aniž si toho kdokoli všiml, je kategorie 7.
5. **Postřehy mimo hlavní téma** – všechno, u čeho padlo „ať se to neztratí“, „poznamenej si to“, „to je důležité do budoucna“. Bývá to mimo téma session, a proto to nejčastěji zapadne.
6. **Korekce** – místa, kde uživatel změnil směr, opravil tě nebo něco zavrhl. **Platí vždy poslední verze**, ne ta první. Pozor na dohody, které v půlce session přestaly platit – ty se nesmí zapsat jako platné.
7. **Nevypořádaná témata** – co v konverzaci padlo a nikdy se nedořešilo. Podrobně viz Fáze 2; posíláš-li na transcript subagenta, pouštěj ho na `Explore` – čte transcript přes `jq` a `grep`, takže na typ bez shellu nepatří – a dej mu tuhle kategorii do zadání spolu s ostatními – ať kvůli ní nemusí číst zvlášť. **Opiš mu do zadání i síto z Fáze 2** (ověření proti zbytku transcriptu i práh důležitosti) a nech si u každého kandidáta vrátit, co prověřil. Bez toho vrátí hrubé kandidáty a ty bys je musel proklepávat vlastním čtením transcriptu – tedy udělat práci, kvůli které jsi ho poslal.

Výsledkem je interní seznam položek. Uživateli zatím nic nepředkládej – kromě kategorie 7, kterou hned probereš ve Fázi 2.

------

## Fáze 2 – Nevypořádaná témata

Nejčastější ztráta v dlouhé konverzaci není zapomenutý zápis, ale **nevypořádané téma**: napsal jsi dlouhou odpověď s několika body, návrhem nebo otázkou, uživatel měl v hlavě něco jiného, chytil se poloviny – a zbytek zůstal bez vypořádání. Nikdo to nezavrhl ani neschválil, jen se to nikdy nedořešilo. Tahle fáze je tu proto, aby se to našlo, dokud je ještě koho se zeptat.

Proto stojí **hned po rekonstrukci session a před zápisem**: rozhodnutí, která tady padnou, mění, co se ve Fázi 3 a 5 zapisuje. Kdyby se ptala až v závěru, uživatel už je duchem pryč a odpoví „to je jedno“.

### Co hledáš

Asymetrii mezi tím, co v konverzaci zaznělo, a tím, na co se reagovalo:

- **Otázka, kterou jsi položil** a uživatel na ni neodpověděl – ani přímo, ani tím, co udělal dál.
- **Návrh nebo varianta**, kterou jsi nabídl, a nikdo ji nepřijal ani nezamítl.
- **Upozornění na riziko, rozpor nebo důsledek**, které zůstalo bez reakce.
- **Vícebodová odpověď, vypořádaná jen zčásti** – tenhle případ je zdaleka nejčastější a nejhůř viditelný, protože navenek vypadá jako vyřízený: odpověď přišla, jen ne na všechno.
- **Uživatelův vlastní bod**, který v jedné zprávě otevřel a v další už se k němu nevrátil.

Rozdíl proti kategorii 4 z Fáze 1: tam jde o **vědomé** odložení, které někdo vyslovil („to necháme na potom“). Tady jde o to, co propadlo, **aniž si toho kdokoli všiml** – a právě proto to nikdo nehledá.

### Jak ověřit, že to opravdu není vypořádané

U každého kandidáta projdi **zbytek transcriptu až do konce** a hledej, jestli se to mezitím nevyřešilo jinudy (**delegoval-li jsi Fázi 1, dělá tohle síto subagent** a ty přebíráš jeho zdůvodnění – nečteš transcript podruhé):

- odpovědí, která přišla později a jinými slovy,
- změnou v souborech, která z otázky udělala fakt,
- pozdějším rozhodnutím, které téma zrušilo jako bezpředmětné.

Nálezem je jen to, co tímhle sítem projde. **Falešný nález je drahý** – nutí uživatele znovu rozhodovat něco, co už rozhodl, a příště začne fázi přeskakovat.

### Práh důležitosti

Nepředkládej řečnické otázky, zdvořilostní nabídky („mám to ještě vypsat?“) ani věci, které by změnily jen kosmetiku. Předkládej to, co by změnilo **obsah souborů, rozhodnutí, rozsah práce**, nebo kvůli čemu by příští session stavěla na neověřeném předpokladu.

Na hranici rozhoduj **ve prospěch předložení** – cena za zbytečnou otázku je jedno kliknutí, cena za zapomenuté rozhodnutí je celá session. Ale seřaď položky od nejdůležitější a **vyjde-li ti jich víc než zhruba pět, máš práh nízko**: projdi je znovu a nech jen ty, u kterých umíš pojmenovat, co se stane, když se nevyřeší.

### Jak to probrat

Nejdřív uživateli řekni, kolik toho viselo (nebo že nic – to je taky výsledek, nemlč o tom). Pak **jednu položku po druhé**, nikdy víc najednou:

```
**[N/celkem] O ČEM TO BYLO**

- **Kdy:** [zhruba kde v konverzaci – čeho se to týkalo]
- **Nevypořádáno:** [citace nebo věrné shrnutí toho, co zůstalo bez odpovědi]
- **Proč není vypořádané:** [co jsi prověřil a proč to nepovažuješ za vyřešené jinudy]
```

Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo – `~/.claude/RULES.md`, *Styl odpovědí*.

Pak se zeptej **přes tool `AskUserQuestion`** – jedno volání na jednu položku, `header` `Téma N/celkem`. Volby dej **věcné, tedy skutečné odpovědi na tu konkrétní otázku** (varianty, které tehdy byly ve hře), ne obecné „zapsat / odložit“. Ke každé položce vždy přidej volbu **„Bezpředmětné“** pro případ, že to uživatel mezitím vyřešil v hlavě nebo o to už nestojí.

### Co s odpovědí

| Odpověď znamená | Co uděláš |
|---|---|
| rozhodnutí | přidej ho jako položku do Fáze 1 (kategorie 1) a normálně zapiš ve Fázi 5 – i se zdůvodněním, které tady padlo |
| „vrátíme se k tomu“ | do `docs/todo.md` s celým kontextem, ne jako holá odrážka |
| „někdy by šlo“, nezávazný nápad | do `docs/backlog.md` – **ne do todo**; hranici drží `~/.claude/STRUCTURE.md`, *`backlog.md`* |
| bezpředmětné | nic nezapisuj; v přehledu ve Fázi 9 to ale uveď, ať je vidět, že se to probralo |
| práce navíc (dodělat kód, přepsat návrh) | to je nad rámec úklidu. Udělej to **jen na výslovný pokyn** a pak pokračuj skillem dál; jinak do `docs/todo.md` (tamtéž) |

------

## Fáze 3 – Konfrontace se soubory

Pro **každou** položku z Fáze 1 ověři čtením souborů, jestli už je zapsaná a v jakém stavu:

- **OK** – je zapsaná na správném místě a ve správném znění → neřeš
- **Chybí** – nikde není → zapiš
- **Zastaralá** – je zapsaná, ale ve znění, které už neplatí → přepiš
- **Špatné místo** – je zapsaná jinde, než kam podle struktury patří → přesuň
- **Duplicitní** – je na víc místech → nech na jednom, ostatní ať jen odkazují

**Kam co patří** (odvoď od skutečné struktury projektu, tohle je obecné vodítko). Obsah jednotlivých souborů definuje `~/.claude/STRUCTURE.md` – tahle tabulka je jen obrácený pohled od položky k souboru, ne druhá definice:

| Typ položky | Cílové místo |
|---|---|
| Pravidla, konvence, jak se v projektu pracuje | projektový `CLAUDE.md` |
| Rozhodnutí a jejich zdůvodnění, zavržené varianty | `docs/decisions.md` |
| Obecné principy a hranice, ve kterých se projekt pohybuje | `docs/rules.md` |
| Úkoly a odložené věci, u kterých je rozhodnuto, že se udělají | `docs/todo.md` |
| Nezávazný nápad, o kterém se nerozhodlo | `docs/backlog.md` |
| Hotové úkoly | `docs/done.md` |
| Otevřené otázky čekající na rozhodnutí uživatele | `docs/todo.md` jako běžná položka |
| Změny dotýkající se toho, co projekt je, umí a jak se používá – **popis pro člověka**, nikdy pokyn pro Clauda | `README.md` |
| Doménová specifika (model, procesy, katalogy) | příslušný soubor v `docs/` |
| Cokoliv v Memory | **přesuň do projektového `CLAUDE.md`**, pokud projekt nemá explicitně povolenou Memory |

Zvlášť projdi hlavní soubory – `README.md`, `docs/todo.md`, `docs/backlog.md`, `docs/done.md`, `docs/decisions.md`, `docs/rules.md` a `CLAUDE.md` (projektový i vnořené) – a ověř, jestli se do nich promítlo, co ze session vzešlo, a jestli v nich nezůstalo pravidlo, které v session přestalo platit. **Jen v rozsahu session**, ne jako obecná revize obsahu.

Když u položky není jasné, kam patří, **zeptej se** – ale až ve Fázi 5, v jednom společném průchodu, ne rozsypaně.

------

## Fáze 4 – Ověř, že průběžná aktualizace opravdu proběhla

`~/.claude/STRUCTURE.md` ukládá udržovat sadu souborů **průběžně během celé session, bez vyžádání**. Tahle fáze ověřuje, jestli se to skutečně dělo. Je to **opačný pohled než Fáze 3**: tam ověřuješ, kam patří položky, které jsi vytěžil; tady ověřuješ, jestli nezůstala nesplněná povinnost.

Neber jako samozřejmé, že aktualizace proběhla. **Empiricky se na ni zapomíná** – proto tenhle krok existuje a proto se nedá odbýt.

### Postup

1. **Zjisti, kdy se každý ze souborů naposledy měnil.** U projektu s gitem `git log --oneline -3 -- <file>` a `git status`; jinak čas modifikace. Zajímá tě, jestli se soubor během téhle session vůbec dotkl.

   ```
   CLAUDE.md  README.md  docs/todo.md  docs/backlog.md  docs/done.md  docs/decisions.md  docs/rules.md
   ```

   Má-li projekt zadání, přidej k nim `docs/requirements.md`, `docs/architecture.md` a `docs/plan.md`. **Vede-li projekt produktové podklady** – poznáš z `## Struktura a dokumentace` v `CLAUDE.md` –, přidej i je: `docs/competition.md`, `docs/risks.md`, `docs/scenarios.md`, `docs/glossary.md`, `docs/pricing.md`. Zapsaný podklad, který dosud nevznikl, **není nález** – je to závazek čekající na svůj krok; nález je zapsaný podklad, kterému se během session rozešel obsah se skutečností. Má-li projekt kód, ověř i **`## Kontrakt příkazů`** v `CLAUDE.md` (*Kontrakt příkazů*) – přibyl-li během session příkaz, kterým se něco spouští, patří tam.
   Neexistují-li, přeskoč je – nezakládají se tady.

2. **Projdi celou session znovu** – celý transcript z Fáze 1, ne jen vytěžený seznam – a u každého souboru se ptej, co do něj **mělo** během session přibýt. **Šel-li na transcript subagent ve Fázi 1, pošli ho i sem**, s tabulkou níž v zadání; hlavní session transcript v ruce nemá a nemá si ho brát, jinak je delegace k ničemu.

   | Soubor | Co v session zakládá povinnost zápisu |
   |---|---|
   | `CLAUDE.md` | vzniklo nebo se změnilo pravidlo, konvence, způsob práce v projektu |
   | `README.md` | změnilo se, co projekt je, umí nebo jak se spouští; zároveň ověř, že v něm nezůstal normativní pokyn pro Clauda – ten patří do `CLAUDE.md` nebo `docs/`, viz `~/.claude/STRUCTURE.md` |
   | `docs/todo.md` | něco se odložilo, zaparkovalo, označilo „později“ – a je rozhodnuto, že se to udělá |
   | `docs/backlog.md` | padl nápad, o kterém se nerozhodlo, že se udělá; **zvlášť ověř, že takový nápad neskončil v `todo.md`** |
   | `docs/done.md` | ověř, že v `todo.md` nezbylo nic hotového – přesouvá se průběžně, tohle je jen záchranná síť |
   | `docs/decisions.md` | padlo rozhodnutí, zvolila se varianta, něco se zamítlo, změnil se názor |
   | `docs/rules.md` | vybrousil se princip, hranice, „takhle to v tomhle projektu děláme vždycky“ |
   | `docs/requirements.md` | změnil se produktový záměr – co se staví, pro koho, co je v MVP a co mimo rozsah |
   | `docs/architecture.md` | změnil se návrh řešení – architektura, datový model, stavy, technologie, bezpečnostní model |
| `docs/competition.md` | zjistilo se něco o konkurenci nebo se posunulo, čím se proti ní vymezujeme |
| `docs/risks.md` | objevilo se riziko, nebo se změnilo, čím mu čelíme; **zvlášť ověř pole *Promítnutí do produktu*** – rozhodlo-li se v session něco kvůli riziku, patří to tam |
| `docs/scenarios.md` | přibyla, změnila se nebo zanikla cesta, kterou uživatel produktem projde – včetně chybové |
| `docs/glossary.md` | zavedl se, přejmenoval nebo upřesnil pojem; **pozor i na pojem, který se v session začal používat mimoděk** |
| `docs/pricing.md` | změnil se tarif, limit, chování po expiraci nebo cokoliv, co z toho plyne pro produkt |
   | `CLAUDE.md` → `## Kontrakt příkazů` | přibyl nebo se změnil příkaz na testy, lint, build nebo audit |
   | `docs/plan.md` | odpracovaly se úkoly (odškrtnout), nebo se plán rozešel se skutečností |

3. **Porovnej s tím, co v souborech skutečně je.** Nestačí, že se soubor během session změnil – ověř, že obsahuje **všechno**, co tam podle bodu 2 patří.

4. **Chybějící doplň zpětně z celé session.** Ne jen holé odrážky – ve stejné kvalitě, jako by to bylo zapsané v okamžiku, kdy to padlo:
   - u rozhodnutí i **proč**, jaké varianty byly ve hře a proč padly,
   - u odložených věcí **celou úvahu**, ne jen název,
   - u principů **obecnou formulaci**, ne popis jednoho případu.

   Zároveň **přeformuluj**, co bylo zapsáno ve spěchu nebo se od té doby posunulo. Platí poslední verze, ne první.

5. **Nahlas výsledek** – i když je čistý:

   ```
   **Průběžná aktualizace**

   - docs/decisions.md – 3 rozhodnutí doplněna zpětně
   - docs/todo.md – OK
   - docs/backlog.md – 2 nápady doplněny
   - docs/rules.md – 1 princip doplněn
   - CLAUDE.md – OK
   - README.md – OK
   ```

   Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo – `~/.claude/RULES.md`, *Styl odpovědí*.

   **Jen ten výpis, žádný komentář k němu** – ani když jsi doplňoval hodně. Nehodnoť, nekomentuj a nezdůvodňuj; co se doplnilo, je v seznamu.

### Když soubory neexistují

Chybí-li některý ze standardních souborů úplně, **nezakládej ho tady potichu**. Vypiš, které chybí, a nabídni spuštění `/project`, který strukturu doplní celou a konzistentně. Výjimka: má-li session obsah, který do chybějícího souboru jednoznačně patří, soubor založ a obsah zapiš – jinak by se ztratil.

Nedává-li standardní struktura pro tenhle projekt smysl (jednorázový scratch, cizí read-only repozitář), konstatuj to jednou větou a fázi přeskoč.

------

## Fáze 5 – Zápis

1. **Mechanické zápisy proveď rovnou.** Po dokončení vypiš stručný seznam: co bylo dopsáno, kam, a jednou větou proč.

2. **Sporné položky předlož jednu po druhé.** Nejdřív položku vypiš:

```
**[N/celkem] NÁZEV POLOŽKY**

- **Z session:** [co v session padlo, případně citace]
- **Stav:** [chybí / zastaralé / špatné místo / duplicita / nejasné zařazení]
- **Návrh:** [konkrétně co kam zapsat nebo jak přepsat – ne vágně „doplnit dokumentaci“]
```

   Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo – `~/.claude/RULES.md`, *Styl odpovědí*.

   Pak se zeptej **přes tool `AskUserQuestion`** (viz Zásady výš) – jedno volání na jednu položku, `header` `Položka N/celkem`, `question` shrnuje položku jednou větou, volby **Zapsat** / **Odložit** / **Přeskočit**. U položky s nejasným zařazením nabídni místo toho **konkrétní cílové soubory** jako volby (např. `CLAUDE.md` / `docs/decisions.md` / `docs/todo.md` / `docs/backlog.md`) – je to rychlejší než se ptát dvakrát.

3. **Piš tak, aby to bylo čisté, jasné, systematické, čitelné a přímočaré.** Když při zápisu narazíš na to, že okolní text je rozbředlý, redundantní nebo si protiřečí, přestrukturuj ho – to je smyslem úklidu, ne zásah nad rámec zadání.

4. **Průběžně commituj**, pokud má projekt zapnutý autocommit.

------

## Fáze 6 – Kontrola odkazů a spuštění čtenářů bez kontextu

Ověř, že to, co jsi právě zapsal, **dává smysl někomu bez kontextu téhle session**. Není to audit celé dokumentace – zajímá tě, jestli nová session naváže na dnešní práci (viz *Rozsah* výš).

**Na nic z téhle fáze se nečeká naprázdno.** Mechanické vady najde skript za zlomek vteřiny, úsudek dostanou dva paralelní čtenáři – a ti běží na pozadí, zatímco odbavuješ Fázi 7. Vypořádají se až ve Fázi 8.

### 1. Mechanická kontrola odkazů

Pusť ji nad Markdowny, kterých se session dotkla:

```sh
python3 ~/.claude/skills/cleanup/scripts/links.py <změněné .md soubory>
```

Seznam vezmi z gitu, a to ze **tří** míst, ať ti nic neuteče: `git diff --name-only HEAD` (pracovní strom **i index** – samotné `git diff` to, co je ve stage, neukáže), `git diff --name-only <základ session>..HEAD` (commity, které mezitím udělal autocommit) a `git status --porcelain --untracked-files=all` (nové soubory). Filtruj na `*.md` a seznam sjednoť. **Základ session** je commit, na kterém stála `HEAD`, než session poprvé zapsala – zapamatuj si ho ve Fázi 0. Rozbitý odkaz a kotva bez nadpisu jsou mechanické vady – hledat je čtením přes model je ta nejdražší možná cesta (`~/.claude/RULES.md`, *Model a effort podle úkolu*, pravidlo nula).

**Nálezy oprav rovnou**, ještě před spuštěním čtenářů: jsou jednoznačné a spadají pod *Dělej sám* ze zásad. Zároveň tím čtenářům ušetříš úsudek nad tím, co je už vyřízené – proto o tom mají obě zadání větu.

Skript **neumí posoudit smysl** a vědomě nekontroluje externí odkazy ani absolutní cesty; co přesně vynechává a proč, stojí v jeho docstringu.

**Čistý výsledek je jedině `0`.** `1` znamená nálezy, `2` chybu volání – tu neber jako čisto: oprav volání a pusť skript znovu. **Nezměnil-li se žádný Markdown, krok přeskoč nahlas** a do přehledu napiš, že kontrola odkazů neběžela, protože nebylo co kontrolovat; skript bez argumentů vrátí právě `2` a tenhle případ je z nich nejčastější.

**Skript vidí jen změněné soubory.** Odkaz, který na dnes přejmenovanou sekci míří z jiného souboru, proto neprověří – proto je v zadání čtenářů věta, že takový odkaz hledat mají.

### 2. Dva čtenáři, oba paralelně a na pozadí

Zadání obou drží [`readers.md`](readers.md) – *Čtenář navazitelnosti* čte dokumentaci od obecného ke konkrétnímu, *Čtenář pozůstatků* dostane diff dnešní práce. Tamtéž stojí, proč jsou dva, jaký model a effort mají a co dělat, když typ `reader` v instalaci není.

Čtenář pozůstatků nemá shell, takže si diff nevyrobí – **připrav mu ho do souboru** ve scratchpadu a v zadání mu předej cestu:

```sh
git diff <základ session>..HEAD -- '*.md' > <scratchpad>/cleanup-diff.txt
```

Nejsou-li změny session commitnuté, vezmi `git diff` bez rozsahu; je-li základ nejistý, radši přibal víc – čtenáři vadí chybějící kontext víc než nadbytečný.

**Spusť oba jedním blokem** jako podagenty typu `reader`, tedy `subagent_type: "reader"`, a **nečekej na ně**. Nenastavuje se pro to nic zvláštního: `Agent` vrací řízení sám od sebe, jakmile agenta předá, a výsledek dorazí později jako notifikace o dokončení úlohy. Stačí tedy po zavolání pokračovat další prací – rovnou Fází 7. Ověřeno 19. 9. 2026.

**Jedeš-li náhradní cestou** ze [`readers.md`](readers.md) (samostatný proces `claude -p`), tenhle krok neplatí – ta blokuje, takže by se čekalo tady i ve Fázi 8. Pusť čtenáře až na začátku Fáze 8 a Fázi 7 odbav bez nich.

**Dva čtenáři nejsou panel agentů ve smyslu `~/.claude/skills/SKILLS.md`, *Ověřovací vrstva*, a ověřovatele proto nemají.** Norma míří na panel specialistů, kde ověřit nález znamená zopakovat jeho práci – tam je ověřovatel jediná obrana proti tomu, aby agent našel problém za každou cenu. Zdejší nálezy mají tvar „na tomhle místě stojí X, na tamtom Y“, takže je hlavní session ověří u zdroje jedním čtením, a to i musí (Fáze 8). Ověřovatel navíc by přidal třetí běh agenta na konec úklidu, kde už ho nejde schovat za nic interaktivního – zpomalil by tedy právě to, kvůli čemu tahle fáze vznikla. **Přibude-li sem třetí agent, je potřeba tohle posoudit znovu**; rozhodnuto 19. 9. 2026.

**Fáze 7 jim mění stav pod rukama** – opravuje věci mimo rozsah, takže nález, který dorazí, může být mezitím vyřízený. Než ho ve Fázi 8 předložíš, ověř, že pořád platí; neplatné zahoď mlčky a nepiš o nich.

**Proč zrovna během Fáze 7:** ta je interaktivní, takže se v ní stejně čeká na uživatele. Čekání na čtenáře se za ten čas schová celé a běh se o něj zkrátí. Kdyby Fáze 7 byla prázdná (žádné položky mimo rozsah), přejdi rovnou na Fázi 8 a tam na čtenáře počkej – to je jediný případ, kdy se čeká.

------

## Fáze 7 – Naložení s tím, co by zůstalo mimo rozsah

Sem patří všechno, co bys jinak jen vypsal do sekce *Mimo rozsah úklidu* a nechal být: rozbité věci známé ze session, starší dluh, na který jsi narazil při zápisu, odložené nálezy. **Vypsat a nechat být je nepřijatelné** – uživatel session vzápětí zavře a položky zmizí s ní. **Nálezy čtenářů sem nepatří**, ti v tuhle chvíli teprve běží a vypořádají se ve Fázi 8 podle téhož kritéria.

**Celý postup drží [`out-of-scope.md`](out-of-scope.md)** – čím se dělí položky k vyřešení rovnou od těch, o kterých rozhoduje uživatel, šablony výpisu i volby k jednotlivým položkám. Přečti si ho celý a řiď se jím; co se s položkami stalo, patří pak do přehledu ve Fázi 9.

------

## Fáze 8 – Vypořádání nálezů čtenářů

Sem dorazí, co našli čtenáři z Fáze 6. **Nedorazili-li ještě, počkej na ně** – bez nich nemá fáze co vypořádat a přeskočit ji znamená zahodit celý smysl Fáze 6. **Vrátil-li některý chybu nebo nic**, pusť ho jednou znovu; selže-li podruhé, napiš do přehledu, že jeho část zůstala nezkontrolovaná, a pokračuj – netvrď, že kontrola proběhla.

**Než s nálezem cokoliv uděláš, ověř, že pořád platí** – Fáze 7 mezitím sahala na soubory a část nálezů mohla vyřešit. Neplatné zahoď mlčky; hlásit nález, který už neexistuje, je totéž jako hlásit falešný poplach.

- **Nálezy, které se týkají téhle session**, oprav – mechanické sám, sporné předlož uživateli po jednom jako ve Fázi 7.
- **Nálezy mimo rozsah session** (starší dluh v dokumentaci) projdi kritériem z [`out-of-scope.md`](out-of-scope.md), bodu 2: co má jednu zjevně správnou podobu, oprav rovnou a vypiš; o zbytku nech rozhodnout uživatele. Fáze 7 už proběhla, takže se rozhoduje tady a stejným způsobem – a **do přehledu jdou tyhle položky do téhož seznamu** *Mimo rozsah úklidu* jako ty z Fáze 7, ne stranou.
- **Byly-li opravy netriviální** (přepisovala se struktura, měnil se obsah více souborů), pusť **znovu čtenáře pozůstatků** – jen jeho, ne oba, a **vyrob mu nový diff**: ten z Fáze 6 opravy z Fází 7 a 8 neobsahuje, takže by hledal v zastaralém podkladu. Opravy samy zanechávají nové pozůstatky, ale navazitelnost se jimi nemění, takže druhý průchod celou dokumentací by byl čekání bez zisku. Tenhle běh už na pozadí schovat nejde, protože po něm nic dalšího nezbývá; proto se pouští jen tehdy, když opravy opravdu byly netriviální.

------

## Fáze 9 – Git a závěr

**Zapiš průchod do `docs/done.md`, sekce `## Průchody životním cyklem`** (`~/.claude/STRUCTURE.md`, *`done.md`*). Čtenářem je **příští `/cleanup`**, který jinak nepozná, co zůstalo mimo rozsah úklidu a jak se s tím naložilo – a bude se na totéž ptát znovu.

```
- **YYYY-MM-DD** · `/cleanup` · `<short HEAD>` · N nevypořádaných témat (X rozhodnuto, Y bezpředmětných) · mimo rozsah: <co a jak se s tím naložilo>
```

Datum vyrob `date +%F` a hash `git rev-parse --short HEAD`. **Nemá-li projekt `done.md`, krok přeskoč nahlas** – nezakládá se kvůli jednomu řádku.

**Git:**

- `git status` musí být **čistý** – žádné rozpracované ani neotrackované soubory. Co tam být nemá, patří do `.gitignore`; co tam patří, se commitne.
- *Worktree layout:* `git status` pouštěj ve worktree větve, ne v kořeni kontejneru – tam by spadl na `must be run in a work tree`. Navíc zkontroluj `git -C <container>/main status`: v `main/` nemá být nic rozpracovaného – když je, ohlas to.
- Všechno **commitnuté** s výstižnými zprávami.
- Když má repozitář remote (zjistil jsi ho ve Fázi 0), všechno **pushnuté**.
- Ověř výsledek znovu (`git status`, `git log origin/<branch>..HEAD`) – ne že to jen předpokládej.

**Přehled:**

```
## Úklid dokončen

**Zapsáno ze session**
- N položek doplněno / M přepsáno / K přesunuto
- [stručný seznam: co, kam]

**Nevypořádaná témata**
- [N probráno, s jakým výsledkem – nebo „žádná“]

**Kontrola odkazů a čtenáři bez kontextu**
- [nálezy skriptu, verdikt obou čtenářů a co z nich vzešlo]
- Čtenáři: 2 (`reader`, [model]), ověřeni čtením zdroje v hlavní session – [N nálezů, M vyvráceno]

**Git**
- Pracovní strom: [čistý / co zbývá]
- Commity: N, push: [ano / repozitář nemá remote]

**Odložené položky**
- [co se odložilo z vlastního úklidu – Fáze 2 a 5 –, nebo „žádné“]

**Mimo rozsah úklidu**
- [seznam z Fází 7 a 8 a u každé položky, jak se s ní naložilo: vyřešeno rovnou / vyřešeno na přání / todo / backlog / zahozeno – nebo „žádné“]
- Položka z Fáze 7 nebo 8 patří sem, i když skončila v `todo.md`; do *Odložených položek* se nekopíruje.

**Další krok:** /attack a /release, nasazuje-li se – co dál s větví a session, rozhodne otázka za verdiktem
```

Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo – `~/.claude/RULES.md`, *Styl odpovědí*.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Ze session je všechno zapsané, můžeš pokračovat, zkompaktovat i odejít.`
- **Stojíš-li ve worktree větve** (`~/.claude/WORKTREE.md`), tedy v kontejneru s `.bare` a mimo `main/`: `Ze session je všechno zapsané. Větev <jméno> zůstává otevřená – můžeš pokračovat, zkompaktovat, nebo ji přimergovat do main.` Je-li ze session známé něco rozbitého nebo nedodělaného, použij místo ní `Ze session je všechno zapsané. Větev <jméno> zůstává otevřená – merge zatím brání: <konkrétní seznam>.` a merge v otázce níž nenabízej. Totéž platí, zjistil-li Git výš rozpracovaný `main/`, nebo stojí-li v `## Nasazení` projektového `CLAUDE.md`, že se z `main` automaticky nasazuje – merge by tam byl nasazení a patří `/release`.
- `Zapsané zatím není všechno – brání tomu: <konkrétní seznam>.`

**Nenabízej „opustit session“ jako jedinou cestu.** Zápis je hotový, ale to neznamená, že je hotová práce: uživatel klidně pokračuje dál v téže session a `/cleanup` mu jen zajistil, že ho kompaktace nepřipraví o kontext. Ve worktree layoutu to platí dvojnásob – „můžeš odejít“ tam neodpovídá na otázku, kterou má uživatel v hlavě, totiž co s tou větví.

**Že merge přichází v úvahu, musí zaznít explicitně** – vedle pokračování a kompaktace. Věta ručí jen za zápis ze session; jestli merge smí projít (větev kola návrhu, rozpracovaný `main/`, konflikt), ověří až postup v `~/.claude/WORKTREE.md`, *Dokončení větve*, a proto v ní nestojí „bez obav“. Uživatel má v hlavě otázku „můžu to zavřít, nebo tam něco visí?“ a mlčení o mergi ji nezodpoví; „dokončit větev“ je vágní a nechává ho hádat, jestli něco nepřehlédl.

### Co dál

**Verdikt je poslední věta textu; hned za ním, skončil-li běh jednou z prvních dvou vět, polož otázku `AskUserQuestion`** s textem `Co dál? (/compact, /clear a /exit zadej sám)` a těmito volbami v tomhle pořadí – merge první, protože po úklidu ve větvi je nejčastější:

| Volba | Kdy se nabízí | Co se po ní stane |
|---|---|---|
| **Přimergovat do main** | jen ve worktree větve, tedy v kontejneru s `.bare` a mimo `main/`, a jen když verdikt nepojmenoval nic, co merge brání | provedeš *Dokončení větve* z `~/.claude/WORKTREE.md` |
| **Pokračovat v práci** | vždy | nic – čekáš na další zadání |
| **Další kolo úklidu** | vždy | pustíš `/cleanup` znovu nástrojem `Skill` |

**Proč otázka, a ne rovnou merge:** `/cleanup` se pouští i před kompaktací uprostřed rozdělané větve, takže automatický merge by jednou poslal do `main` nedodělanou práci. Uživatel přitom po úklidu podle vlastních slov (16. 9. 2026) mergoval skoro vždycky, a ruční příkaz navíc byl jen tření. Zavržené varianty (16. 9. 2026): **režim `/cleanup merge`** – záměr by se řekl předem, ale uživatel by si režim musel pamatovat, kdežto otázka stojí jeden stisk; **samostatný krok životního cyklu pro dokončení větve** – merge navazuje právě na úklid a vlastní krok by jen přidal příkaz, který se pouští pokaždé hned po něm. **Vybraná volba je výslovný pokyn** ve smyslu `~/.claude/WORKTREE.md`, *Větev žije, dokud uživatel neřekne jinak* – bez ní merge neprovádíš, nepřipravuješ ani nevypisuješ příkazy.

**Proč `/compact`, `/clear` a `/exit` nejsou volby:** jsou to vestavěné příkazy Claude Code a skill je spustit neumí. Volba, po které by následovalo jen „teď to napiš sám“, je krok navíc; stačí je jmenovat v textu otázky. Ukončit session natvrdo přes shell se nesmí – utrhla by se rozepsaná historie.

**Proč jen ve worktree layoutu:** jen tam je dokončení větve popsané postupem a `main/` má vlastní pracovní adresář. V běžném repozitáři by merge znamenal přepnout pracovní strom, ve kterém může pracovat jiná session.

**Merge se nikam dál nezapisuje.** Záznam průchodu v `done.md` vznikl před otázkou a nese hash úklidu; merge commit se zprávou shrnující práci je záznam sám o sobě a do `main/` se kvůli němu nic dalšího necommituje.

**Skončil-li běh třetí větou** (zapsané není všechno), otázku nepokládej: další krok je odstranit to, co zápisu brání, a merge by šel přes nevypořádanou práci.
