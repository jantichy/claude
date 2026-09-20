---
name: architect
description: Skill se použije, když uživatel zadá "/architect" (volitelně se jménem kola nebo tématu), nebo chce ze schválených požadavků udělat návrh řešení – jak se to postaví: architekturu, datový model, stavy a přechody, rozhraní, cizí systémy a bezpečnostní model –, případně pokračovat dalším kolem rozpracovaného návrhu. Sám se zorientuje podle stavu projektu a oznámí jednou větou, co bude dělat. Větší záměr rozdělí na tematická kola, vede je jedno po druhém i souběžně v samostatných větvích a nakonec je sešije do jednoho návrhu. Na rozdíl od /specify, který popisuje, co se staví a proč, tenhle skill rozhoduje jak – omezení jsou pro něj vstup, volba je jeho výstup. Nic neprogramuje a implementační plán nepíše.
argument-hint: [kolo nebo téma]
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion, Skill]
---

# Architect

## Co skill dělá

Ze schválených požadavků udělá **návrh řešení** – rozhodne, jak se to postaví, a zapíše to tak, aby se podle toho dal napsat plán a pak kód.

**Návrh je sada dokumentů, ne jeden soubor.** Páteří je `docs/architecture.md`, k ní podle potřeby `model.md` (data a stavy), `transitions.md` (operace), `rules.md` (zásady domény) a tematické dokumenty kol. Kdy který vzniká, drží `~/.claude/STRUCTURE.md`, *`requirements.md`, `architecture.md`, `plan.md`*; kontrolní otázka je vždycky *odpovídá na otázku, na kterou žádný jiný neodpovídá?*

V *Životním cyklu projektu* (`~/.claude/RULES.md`) je to čtvrtý krok osy: navazuje na `/specify` a předává na `/breakdown`.

**Větší záměr se nedělá jedním zátahem, ale po kolech.** Kolo je uzavřený průchod jedním tematickým okruhem návrhu do posledního detailu – DPH, upomínání, administrace, platební brána. Skill záměr na začátku zmapuje, rozdělí na kola a zapíše je do `docs/todo.md`. Každé kolo se pak dá odjet v samostatné session a větvi, souběžně s ostatními. Proč to funguje: témata se prolínají, takže průchod po dokumentech by každý z nich otevřel pětkrát a pokaždé s jiným kusem znalosti v hlavě, kdežto průchod po tématech ho otevře stejněkrát, ale pokaždé s uzavřenou otázkou.

**Nemá režimy a sám se zorientuje.** Co je na řadě, plyne ze stavu projektu – jestli existuje mapa kol, ve které větvi session stojí, co je v `done.md`. Rozhoduje o tom tabulka ve *Fázi 0*, ne úsudek, a zvolená cesta se **oznámí jednou větou, než se sáhne na první soubor**. Volná slova za příkazem ji smí přebít; jméno kola jako argument je zkratka pro jeho otevření.

## Co skill nedělá

- **Nepíše požadavky.** Co se staví a proč, pro koho to je, jaké jsou scénáře, glosář a ceník – to je `/specify` a jeho `docs/requirements.md`. Tenhle skill je čte jako hotový vstup a argumentuje z nich odkazem; neopisuje je. **Hranice je tvrdá:** do požadavků patří omezení, do návrhu volba (`~/.claude/STRUCTURE.md`, *`requirements.md`, `architecture.md`, `plan.md`*).
- **Nepíše implementační plán.** Rozpad na úkoly dělá `/breakdown`. Skill ho jen doporučí jako další krok, až je návrh schválený a sešitý.
- **Nic neprogramuje.** Ani scaffold, ani „jen rychle rozjedu projekt“. Tvrdá kontrola – viz *Zákaz implementace*.
- **Neposuzuje vlastní návrh.** Nezávislý posudek dělá `/oponent`, soulad s předpisem `/review`, vnitřní konzistenci `/consistency`. Skill je v závěru doporučuje, sám je nevolá – kdyby je pouštěl, staly by se jeho součástí. **Kromě `/next` nevolá žádný jiný krok**, a to jen u nabídky zbývajících kol; není to krok cyklu, ale seznam, ze kterého si uživatel kolo teprve vybere.
- **Nehledá návrhový dluh z postupného lepení.** Že by celá soustava po několika kolech šla nahradit jednodušší, je otázka pro `/consolidate`; tenhle skill rozhoduje dopředu, ne zpětně.
- **Neslučuje větve sám.** Kdy a jak se větev kola slučuje, drží `~/.claude/WORKTREE.md` – merguje se jen na výslovný pokyn.

## Jak je to postavené uvnitř

Skill **vede rozhovor sám** podle *Zásad pro celý průběh* a na `superpowers:brainstorming` nedeleguje. Je to vědomá volba: návrh po kolech ho nikdy nevolal a návrh jedním zátahem ano, takže táž práce běžela dvěma způsoby podle toho, jak velký záměr zrovna byl. Klasifikace rozsahu, kvůli které se `brainstorming` volal, zůstala ve `/specify`, kde rozhoduje, jestli se zadání vůbec píše.

| Krok | Kdo |
|---|---|
| **Orientace ve stavu, mapa kol, vedení kola, sešití** | **tenhle skill** |
| **Návrh řešení a jeho zápis** | **tenhle skill** |
| Nabídka zbývajících kol, není-li kolo v argumentu | `/next` se zúžením na *Kola návrhu* |
| Implementační plán | `/breakdown` |

**Volání `/next` je na rozdíl od zbytku rozhraní, ne implementační detail** – `/next` na ně spoléhá ve své sekci *Kola návrhu* a vrací kolo zpátky jako `/architect <kolo>`. Vyměnit se tedy nesmí potichu.

**Závazné je to, co po skillu zbude:** dokumenty návrhu na místech podle `~/.claude/STRUCTURE.md`, mapa kol v `docs/todo.md` a záznamy kol v `docs/done.md`, vše česky a bez datumových prefixů.

------

## Kdy se návrh píše a kdy ne

**Vlastní brána na začátku.** Skill se pouští i přímo, bez předchozího `/specify` – typicky u přírůstku do už navrženého systému –, takže si musí sám posoudit, jestli je co navrhovat. **Píše se, když platí aspoň jedno:**

- je to nový projekt nebo nový podsystém,
- zavádí nebo mění datový model či perzistentní stav,
- zavádí rozhraní, na kterém stojí něco dalšího (API, formát, kontrakt),
- napojuje se na cizí systém (platební brána, fakturace, externí API),
- má stavový prostor s přechody,
- existuje víc než jedna rozumná cesta, jak to postavit.

**Neplatí-li ani jedno, řekni to a zastav se.** Je to přírůstek uvnitř už navrženého systému – rozšiř stávající dokument návrhu a jdi rovnou na `/breakdown`, nebo u drobnosti rovnou na `/implement`. Návrh psaný na jednosouborovou změnu je režie, kterou nikdo nečetl.

**Nikdy u projektu bez kódu.** Znalostní, obsahový nebo obchodní projekt (kurz, brand, pozicování, evidence) má smysluplně jen `requirements.md`; místo návrhu a plánu se kroky rozepíšou do `docs/todo.md`. Řekni to a skonči.

**Chybí-li `requirements.md`, neblokuj** – řekni to, nabídni `/specify` a zeptej se, jestli pokračovat i tak. Projekt může mít živý návrh a požadavky nikdy nevést.

## Zásady pro celý průběh

- **Ptej se postupně a přes tool `AskUserQuestion`** – postup, tvar otázky i mechanika toolu viz `~/.claude/RULES.md`, *Ptej se postupně, ne všechno najednou*.
- **Nic si nevymýšlej** – technický název, ID, parametr, cizí API, cena. Viz `~/.claude/RULES.md`, *Při nejistotě se zeptej*.
- **Zapisuj průběžně** – ve chvíli, kdy rozhodnutí padne, ne až na konci. Viz `~/.claude/RULES.md`, *Pravda v souborech, ne v konverzaci*; kam co patří, definuje `STRUCTURE.md`.
- **Navrhuj kompletně, implementuj postupně** – viz `~/.claude/RULES.md`. Tady to znamená: návrh popisuje celou věc včetně toho, co bude až později; řeže se až plán, a ten se dělá jen na MVP.
- **YAGNI.** Z každého návrhu vyhoď, co není potřeba – ale zapiš to do *Mimo rozsah* v požadavcích, ať je vidět, že to bylo zvážené a zamítnuté, ne opomenuté.
- **Na návrhu se nešetří: nejsilnější model, `xhigh`** (`~/.claude/RULES.md`, *Model a effort podle úkolu*). Není to výroba dokumentu – dokument je jen zápis. Je to rozhodnutí, které se propíše do každého úkolu plánu a do každého řádku kódu pod ním, a **špatný návrh se dobrou implementací nezachrání**: špatná věc se jen udělá pořádně. Skill běží v hlavní session, kde model ani effort nastavit neumí – **doporuč proto běh v session na nejsilnějším modelu**, hned v přípravě.

------

## Zákaz implementace

**Dokud není návrh hotový a schválený, nesmí vzniknout ani řádek produkčního kódu.** Žádný scaffold, žádné `npm create`, žádná databáze, žádné „jen si ověřím, že to jde“.

Výjimka je jediná: **ověřovací pokus**, když na odpovědi stojí rozhodnutí v návrhu („zvládne to hosting?“, „má to API tenhle endpoint?“). Pak řekni dopředu, co zkoušíš a proč, výsledek použij jako podklad a **kód zahoď** – označ ho jako jednorázový a nenechávej ho v projektu.

| Myšlenka | Realita |
|---|---|
| „Návrh je jasný, začnu rovnou“ | Když je jasný, sepsání trvá deset minut. Když ne, právě proto se píše. |
| „Udělám scaffold, ať máme na čem stavět“ | Scaffold zamkne tech stack dřív, než se rozhodl. |
| „Uživatel mi řekl ‚udělej to‘“ | Řekl `/architect`. Kdyby chtěl kód, řekl by to. |

------

## Fáze 0 – Příprava a orientace

**Společný začátek drží `~/.claude/skills/PREFLIGHT.md`** – načti si ho a řiď se jím. Body 4 a 5 odpadají: tenhle skill nesahá na kód a pracuje nad návrhem, ne nad diffem větve. **Hlavní větev** – v textu níž `<main-branch>` – je `origin/main`, má-li repozitář remote (po `git fetch`), jinak lokální `main`; jmenuje-li se hlavní větev jinak, určí se jako v `PREFLIGHT.md`, bod 5. Bez toho by projekt bez remote nenašel mapu kol ani sloučené větve a rozešel by se se `/next`, který hlavní větev určuje stejně.

Navíc si zjisti tohle:

1. **Projdi bránu** – *Kdy se návrh píše a kdy ne* výš. Vyjde-li, že se nepíše, skonči tam a dál nepokračuj.
2. **Zkontroluj strukturu.** Existují standardní soubory `todo.md`, `done.md`, `decisions.md`, `rules.md` (v `docs/`, nebo v kořeni podle režimu)? Chybí-li, **nezakládej je potichu** – vypiš, co chybí, a nabídni `/project`. Návrh bez místa, kam zapisovat rozhodnutí, je poloviční práce.
3. **Načti vstupy.** `docs/requirements.md`, existující dokumenty návrhu, `decisions.md`, `rules.md` a – vede-li je projekt – `scenarios.md`, `risks.md` a `glossary.md`. **Cizí podklady jsou read-only.**
4. **Zorientuj se ve stavu.** Vyhrává **první řádek, který sedí**; je to tabulka, ne úsudek:

   | Stav | Co se dělá |
   |---|---|
   | argument je jméno kola ze sekce *Kola návrhu* v `docs/todo.md` | *Fáze 2* – to kolo |
   | session stojí ve větvi z řádku *Větev* bloku kola | *Fáze 2*, nebo *Fáze 3* podle řádku *Stav* v bloku |
   | session stojí ve větvi z řádku *Větev* záznamu kola v `docs/done.md`, bloku už není | nic – řekni, že kolo je zapsané a čeká na sloučení |
   | v `todo.md` stojí řádek *Návrh sešitý* | *Fáze 6* – dočištění |
   | sekce *Kola návrhu* má aspoň jeden blok, ale žádný neodpovídá argumentu ani větvi | *Fáze 2* bez vybraného kola – nabídka přes `/next` |
   | `docs/done.md` má v sekci *Kola návrhu* aspoň jeden záznam kola a za posledním z nich nestojí řádek *Návrh uzavřen* | *Fáze 4* – sešití nad koly |
   | `architecture.md` existuje a přidává se do něj | *Fáze 4* – rozšíření, ne druhý návrhový dokument |
   | jinak | *Fáze 1* – mapa okruhů |

   **Neexistující sekce se počítá jako prázdná**, o sešití proto rozhoduje `done.md`, ne `todo.md`: projekt, který kola nikdy neměl, žádný záznam kola nemá, a druhá várka kol se od první odliší řádkem *Návrh uzavřen*.

   **Jméno kola** se porovnává bez ohledu na velikost písmen s nadpisem bloku bez „Kolo o“, se jménem větve i se jménem tematického dokumentu. Víc shod → zeptej se. Argument, který není jménem kola, ber jako téma a řekni to.

5. **Oznam zvolenou cestu jednou větou, než sáhneš na první soubor.** Bez pojmenovaných režimů je to jediná pojistka proti tichému špatnému odhadu – uživatel ji musí mít šanci opravit dřív, než se něco zapíše. Řekl-li v promptu volnými slovy něco jiného, **má přednost jeho pokyn** (`~/.claude/RULES.md`, *Přednost pravidel*).
6. **Větev.** U nabídky kol se nezakládá – kolo ještě není vybrané. Běží-li projekt ve worktree layoutu a session stojí v `main/` nebo ve větvi, která s prací nesouvisí, nabídni založení větve podle `~/.claude/WORKTREE.md`, *Založení větve*, **dřív, než cokoliv zapíšeš**: mapa okruhů do `docs/architect`, kolo do větve z řádku *Větev*, sešití do `docs/stitch`. Existuje-li větev toho jména z dřívější várky, přidej příponu `-2` a **u kola ji přepiš i na řádek *Větev* v bloku** – podle něj větev poznává orientace i pojistka v `~/.claude/WORKTREE.md`. Větev pro mapu okruhů zakládej až po bodu 4, ať nevznikne zbytečně.

------

## Fáze 1 – Mapa okruhů: kola, nebo jeden zátah

**Vždycky zmapuj tematické okruhy záměru** – ne kapitoly dokumentu, ale témata, o kterých se bude rozhodovat. **Vyjdou-li aspoň dva, které mají vlastní otevřené otázky a zasahují do sdílených dokumentů, navrhni kola;** jinak jeden zátah. Mapu i volbu ukaž a nech potvrdit přes `AskUserQuestion`. **Zamítnuto „vždycky kola“:** u malé feature by blok v `todo.md`, tematický dokument, záznam v `done.md` a sešití nad jediným kolem byly jen režie.

**Jeden zátah** pokračuje rovnou *Fází 4*.

**Po kolech** se postup mění:

1. **Zapiš mapu** do sekce `## Kola návrhu` v `docs/todo.md`, jeden blok na kolo. Ne do samostatného souboru – evidence zbývajících a hotových kol by se rozdělila na dvě místa –, a ne jako běžné položky, protože ty orientace od kola nerozezná a otázky se pak odkládají na kola, která už proběhla. Tvar bloku drží `~/.claude/STRUCTURE.md`, *`todo.md`*. **Blok musí stačit čisté session** – nese celé zadání, podklady a závislosti.
2. **`architecture.md` se zatím nepíše.** Vzniká až v *Fázi 4* nad výsledky všech kol; souběžná kola by se v něm srážela a návrh nad celkem stojí na uzavřených tématech, ne na polovině z nich.
3. **Závěr** vypíše mapu a doporučí, čím začít – viz *Fáze 7*.

**Ve worktree layoutu** se mapa musí sloučit do `main` dřív, než se otevře první kolo – větev kola vzniká z `<main-branch>` a bez toho by mapu neměla.

**Bez worktree layoutu** se kola neřeší souběžně, ale jedno po druhém: dvě session nad jedním pracovním stromem by si zápisy smíchaly. Řekni to v závěru.

**Rozsah.** Popisuje-li zadání víc nezávislých podsystémů, řekni to hned a rozlož to na dílčí projekty dřív, než se začnou ladit detaily. Každý dílčí projekt pak dostane vlastní dokumenty i vlastní plán. **Kola nejsou dílčí projekty:** kola jsou okruhy jednoho systému, které se prolínají, dílčí projekty jsou systémy, které se neprolínají.

------

## Fáze 2 – Kolo

Odjede **jedno kolo** návrhu: vezme blok ze sekce *Kola návrhu* v `docs/todo.md`, rozhodne jeho téma do posledního detailu a zapíše výsledek.

**Bez vybraného kola** vyvolej `/next` se zúžením na kola (`/next Kola návrhu`) přes nástroj `Skill` – zbytek téhle fáze ani vlastní závěr se neprovádí, běh končí závěrečným verdiktem `/next`. Jak se kola čtou, řadí a nabízejí – mapa z hlavní větve, stav rozběhnutého kola z jeho větve, upozornění na souběh –, drží `~/.claude/skills/next/SKILL.md`, *Kola návrhu*; dvě kopie téhož postupu by se rozešly. Vybrané kolo pak `/next` sám předá zpátky jako `/architect <kolo>`.

### 1. Příprava kola

1. **Větev** podle *Fáze 0*, bod 6. Jméno větve se řídí zvykem projektu (`~/.claude/WORKTREE.md`), jméno tematického dokumentu je jednoslovné anglicky (`~/.claude/RULES.md`, *Naming*), nadpis bloku česky. Existuje-li tematický dokument z dřívější várky, **rozšiř ho**. Nastav v bloku *Stav* na `rozhoduje se` a commitni.
2. **Načti blok kola**, `requirements.md`, dokumenty z řádků *Dokument* a *Sahá na*, `decisions.md` a `rules.md`. Kolo, na které tohle čeká, musí mít záznam v `docs/done.md` **za posledním řádkem *Návrh uzavřen*** – starší záznam téhož jména patří dřívější várce. Nemá-li ho, řekni to a zeptej se, jestli pokračovat.
3. **Zadání kola ověř, ne převezmi.** Blok je zadání, ne odpověď. Ukáže-li se při prvním pohledu do podkladů, že otázky v něm jsou neúplné nebo špatně položené, řekni to a nech nové zadání potvrdit – kolo smí své zadání přepsat.

### 2. Rozhodování

Veď rozhovor otázku po otázce, dokud v tématu nezbývá otevřená otázka. Zapisuj průběžně:

- **Tematický dokument** `docs/<topic>.md` drží celý okruh. Produktovou a technickou část v něm odděluj toutéž hranicí jako mezi požadavky a návrhem (`~/.claude/STRUCTURE.md`, *`requirements.md`, `architecture.md`, `plan.md`*): omezení a volba se nemíchají, jen stojí u sebe.
- **Do sdílených dokumentů** – `requirements.md`, glosář, scénáře, `model.md` – zapiš jen to, co z tématu plyne pro celek, a odkaž se na tematický dokument. Psaní celého tématu rovnou do nich je zamítnuté, protože souběžné větve by se srazily v týchž kapitolách. **`architecture.md` nepiš**, vzniká ve *Fázi 4*.
- **Kapitola v `decisions.md` se píše bez čísla**, i když ho kapitoly v projektu mají, a odkazy na ni se píšou jménem. Číslo dostane až ve *Fázi 3* – souběžná kola by si jinak vzala totéž.
- **Nová otevřená otázka mimo téma** se odkládá na **jmenované kolo**, ne na „později“: zapiš ji do jeho bloku. Nemá-li kam, vzniká nové kolo – dopiš jeho blok do mapy a řekni to.

### 3. Uzavření rozhodování

1. **Sebe-revize** tematického dokumentu a toho, co kolo zapsalo jinam – *Fáze 5*, body 1 až 6 a 9.
2. **Schválení uživatelem.** Pak nastav v bloku *Stav* na `rozhodnuto` a commitni.

Blok v `todo.md` **zatím zůstává** a do `done.md` se nic nezapisuje: nálezy z doporučených kroků se musí mít kam vrátit a záznam kola má odkazovat na kapitolu, která už číslo má.

### 4. Závěr rozhodování

Vypiš, co kolo rozhodlo, co zapsalo kam, které otázky zůstaly a jaká nová kola vznikla. Pak **doporuč navazující kroky v tomhle pořadí** – každý jen tehdy, když se vyplatí, a u přeskočeného řekni proč:

1. **`/review`** nad tím, co kolo vyrobilo – měří dokument proti standardům, které projekt vede; **`/oponent docs/<topic>.md`**, zavedlo-li kolo nový podsystém, změnilo model nebo se napojilo na cizí systém; **ani jedno**, bylo-li kolo drobné a posudek by jen zdržel.
2. **`/consistency`**, jen sáhlo-li kolo do hodně sdílených dokumentů. Většinou se vyplatí až nad celkem po sešití.
3. **`/cleanup`** – vždycky.
4. **`/architect` znovu v téhle větvi** – zapíše kolo jako hotové (*Fáze 3*); ve worktree layoutu pak sloučení.

------

## Fáze 3 – Zápis kola před sloučením

Pouští se ve větvi kola po doporučených krocích. **Bez něj se větev kola neslučuje** – `~/.claude/WORKTREE.md`, *Dokončení větve*, na to odkazuje. Bez worktree layoutu odpadá natažení `<main-branch>` i sloučení a zbytek se udělá rovnou v pracovním stromu.

1. **Natáhni `<main-branch>` do větve.** Konflikt na konci `done.md` nebo `decisions.md` od souběžného kola vyřeš ponecháním obou zápisů za sebou. **Přibyla-li tím do bloku kola nová otázka, nebo změnilo-li souběžné kolo dokument z řádku *Sahá na* v tom, na čem tohle kolo stojí**, zápis nedělej: vrať *Stav* na `rozhoduje se`, řekni, co se změnilo, a vrať se do *Fáze 2*, kroku 2.
2. **Odložené otázky, které kolo neotevřelo, přepiš.** Přesuň je do bloku jiného kola; když na žádné kolo nečekají, ale na něco jiného (rozhodnutí, podklad, odpověď zvenčí), udělej z nich samostatnou položku `todo.md` a napiš, na co čekají. Položka s poznámkou, že čeká na kolo, které už proběhlo, se nesmí zachovat – nerozezná se od fronty.
3. **Přiděl kapitole v `decisions.md` další volné číslo** podle stavu po natažení a přepiš odkazy na ni ve všech souborech, na které kolo sáhlo.
4. **Záznam do `docs/done.md`**, sekce `## Kola návrhu`, v tvaru podle `~/.claude/STRUCTURE.md`, *`done.md`* – pole *Neotevřelo* z kroku 2 –, a smazání bloku z `docs/todo.md`.
5. **Commit.**
6. **Doporuč sloučení větve** – samo podle `~/.claude/WORKTREE.md`, *Dokončení větve*, a jen na pokyn. **Posune-li se mezitím `<main-branch>`** (`git log HEAD..<main-branch>` není prázdný), zopakuj těsně před sloučením natažení `<main-branch>` včetně jeho kontroly a pak přidělení čísla: jinak by si souběžné kolo sloučené o chvíli dřív vzalo totéž číslo. **Konflikt „smazáno ve větvi, změněno na `main`“ u bloku kola** znamená, že souběžné kolo do bloku mezitím přesunulo otázku: vezmi ji z verze na `main`, zpracuj ji podle kontroly po natažení a blok pak znovu smaž – nikdy ho nenechávej vedle hotového záznamu.

------

## Fáze 4 – Návrh řešení

Zapiš do **`docs/architecture.md`** a podle potřeby do dalších dokumentů návrhu. Šablona i pravidla psaní jsou v `~/.claude/skills/architect/documents.md`; **přečti si ten soubor celý, než začneš psát.**

**Jde-li o sešití po kolech**, začni tímhle:

1. **Ověř, že kola opravdu doběhla.** Sekce *Kola návrhu* je prázdná, žádná větev z řádků *Větev* v záznamech nejnovější várky není mimo `<main-branch>` (`git branch -a --no-merged <main-branch>`) a každé kolo z nejnovější várky má záznam v `docs/done.md` za posledním řádkem *Návrh uzavřen*. Chybí-li něco, řekni co a zastav se.
2. **Sešij požadavky.** Projdi `requirements.md` proti tematickým dokumentům: odkazuje na každý, nepřekrývá se s nimi, *MVP* a *Mimo rozsah* pokrývají, co kola rozhodla. Změnu v nich zapiš tam – požadavky vlastní `/specify`, ale sešití je jediné místo, kde je vidět celek.
3. **Volbu, kterou už rozhodlo kolo, neopisuj, odkaž na ni.** Na co návrh potřebuje odpověď a žádné kolo ji nedalo, se doptej.

Pak návrh sám, nad celkem i u jednoho zátahu:

**Kontrola proti požadavkům:** projdi scénáře (ze `scenarios.md`, nebo ze sekce *Hlavní scénáře*), *Varianty* a *Nefunkční požadavky* a u každého ukaž, co v návrhu ho pokrývá. Nepokryté je nález, ne detail. Vede-li projekt `risks.md`, projdi i **mitigace**: riziko s vyplněným *Promítnutím do produktu* musí mít v návrhu protějšek, jinak se mitigace nestala.

**Bezpečnost se navrhuje, neaudituje.** Zhruba polovina kódu psaného modely obsahuje bezpečnostní chybu a je to předvídatelná množina. Nejúčinnější obrana není kontrola na konci, ale struktura, ve které díra nejde udělat – jedna vrstva autorizace, kterou nelze obejít, výhradně parametrizované dotazy, validace na hranici, tajemství jen z prostředí. Proto má návrh sekci *Bezpečnostní model*, a proto v ní nesmí stát „ošetříme to při implementaci“.

**Doménové standardy.** Návrh se řídí tím, co si projekt importuje v `CLAUDE.md` – `~/Dev/context/coding/coding.md` vždy, dál podle povahy `web/web.md`, `web/admin.md`, `analytics/analytics.md`. Načti je, **než začneš navrhovat**, ne až při kontrole.

**Konec prvního běhu po kolech se zapisuje:** po schválení `architecture.md` připiš do prázdné sekce *Kola návrhu* v `todo.md` řádek `**Návrh sešitý** – čeká na doporučené kroky a dočištění.` a commitni. Podle něj orientace pozná, že na řadě je *Fáze 6*; přerušené sešití ten řádek nemá, takže se nezamění.

------

## Fáze 5 – Sebe-revize a oponentura

Běží **po každém dokumentu zvlášť** – tematickém dokumentu kola i návrhu nad celkem –, ne až na konci.

**Sebe-revize:**

1. **Placeholdery** – „TBD“, „TODO“, nedokončené sekce, vágní tvrzení. Oprav.
2. **Vnitřní rozpory** – neodporují si sekce? Sedí počty a výčty s obsahem?
3. **Vymyšlené věci** – je tam technický název, ID, parametr nebo číslo, které jsi neměl od uživatele ani z podkladů? To je nález. Dohledej, nebo přesuň do *Otevřených otázek*.
4. **Prosakování hranice** – je v návrhu zdůvodnění produktu, které patří do požadavků? Přesuň.
5. **Pokrytí** – proti požadavkům, scénářům a mitigacím rizik (viz *Fáze 4*).
6. **Dvojznačnost** – dá se něco přečíst dvěma způsoby? Vyber jeden a napiš ho jednoznačně.
7. **Rozsah** – vejde se to do jednoho implementačního plánu? Pokud ne, dekomponuj.
8. **Sada, ne hromada** – odpovídá každý dokument návrhu na otázku, na kterou žádný jiný neodpovídá? Vznikl-li nový jen proto, že byl ten starý dlouhý, je to kapitola, ne dokument.
9. **Glosář** – vede-li ho projekt: má každá entita, která v návrhu dostala jméno, záznam i tam?

**Oponentura.** Dokument jsi psal ty a jsi na něj zaujatý. `/oponent` je **krok životního cyklu**, ne nabídka: pusť ho, nebo nahlas řekni, proč se u téhle změny přeskakuje. Nabízej ho pro každý dokument zvlášť (`/oponent docs/architecture.md`, `/oponent docs/<topic>.md`).

**Hlediska nevypisuj** – sestaví si je sám podle sloupce *Spouštěč* ve svém katalogu (`~/.claude/skills/oponent/SKILL.md`, *Volba hledisek*) a nechá si je od uživatele potvrdit. Výčet zopakovaný tady by se s katalogem rozešel při první jeho změně (`~/.claude/RULES.md`, *Single source of truth*).

**Kontrola uživatele:**

> Návrh řešení je sepsaný a commitnutý v `docs/architecture.md`. Přečti si ho prosím a řekni, jestli chceš něco změnit, než z něj uděláme implementační plán.

Počkej na odpověď. Chce-li změny, proveď je a projdi sebe-revizi znovu.

------

## Fáze 6 – Dočištění

Pouští se po doporučených krocích nad sešitým návrhem. Potvrď s uživatelem, že proběhly.

1. **Otázky přesunuté mezi koly** musí být vypořádané, nebo vedené jako samostatná položka `todo.md` s tím, na co čekají.
2. **Zruš sekci *Kola návrhu*** v `todo.md` i s řádkem *Návrh sešitý*.
3. **Do `done.md` připiš řádek *Návrh uzavřen*** podle `~/.claude/STRUCTURE.md`, *`done.md`*.
4. **Commit** a doporuč sloučení větve podle `~/.claude/WORKTREE.md`.

**Proč se dočištění odkládá za doporučené kroky:** řádek *Návrh uzavřen* nesmí vzniknout dřív, než se nálezy z posudku mají kam vrátit.

------

## Když se návrh změní později

Platí *Doc-first vývoj* z `~/.claude/RULES.md`; posloupnost souborů definuje `STRUCTURE.md`:

1. Změní se požadavek → to je `/specify`; sem se vrať, až je změněný.
2. Uprav **`architecture.md`** a dotčené dokumenty návrhu, u návrhu po kolech i **tematický dokument** toho okruhu.
3. Zkontroluj, jestli to mění nehotové úkoly → uprav **`plan.md`**.
4. Rozhodnutí a důvod změny zapiš do `docs/decisions.md`. Původní záznam nepřepisuj – přibude revize.

Přijde-li změna zdola (při implementaci se ukáže, že návrh nejde), **neopravuj to potichu v kódu**. Vrať se sem, uprav návrh, a je-li dotčený i produktový záměr, řekni to a nech rozhodnout uživatele.

------

## Časté chyby

- **Návrh se napíše na přírůstek uvnitř už navrženého systému.** Brána na začátku je tam proto, že skill jde spustit i mimo řadu – když jí neprojdeš, vyrobíš dokument, který nikdo nečetl.
- **Kolo zapíše celé téma do sdílených dokumentů.** Souběžná kola se pak srazí v týchž kapitolách. Do sdílených jde jen to, co z tématu plyne pro celek.
- **`architecture.md` vznikne uprostřed kol.** Souběžná kola by se v něm srážela a návrh nad celkem stojí na uzavřených tématech.
- **Orientace se oznámí až po zápisu.** Pak už není co opravit. Věta jde před první soubor, ne za něj.
- **Zamítnuté varianty se nezapíšou.** Za půl roku je někdo vymyslí znovu a projde celou úvahou nanovo (`~/.claude/RULES.md`, *Rozhodnutí zapisuj i s cestou k nim*).

------

## Fáze 7 – Závěr

```
## Návrh hotový

**Dokumenty**
- docs/architecture.md – <počet> sekcí
- docs/<další dokument návrhu> – <co drží> (jen vznikl-li)
- docs/<topic>.md – <počet> tematických dokumentů kol (jen u návrhu po kolech)

**Zapsáno mimo ně**
- docs/decisions.md: N rozhodnutí
- docs/todo.md: N odložených položek
- docs/rules.md: N principů

**Otevřené otázky**
- [seznam, nebo „žádné“]

**Další krok**
- [doporučené kroky v pořadí, pak /breakdown]
```

Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo – `~/.claude/RULES.md`, *Styl odpovědí*.

**U mapy okruhů** vypadá závěr jinak: místo dokumentů vypiš mapu kol – u každého jméno, větev a na co čeká – a doporuč, **která kola pustit hned a souběžně**: ta bez nesplněné závislosti, a přednostně ta, jejichž řádky *Sahá na* se nepřekrývají. Pod to doporuč `/review`, `/cleanup` a ve worktree layoutu sloučení větve – teprve pak se otevírají kola.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Návrh je hotový a schválený, můžeš pustit doporučené kroky a pak /breakdown.`
- `Návrh hotový není – brání tomu: <konkrétní seznam>.`

U ostatních cest místo nich tytéž dvojice, vždy jen hotovo a nehotovo:

- `Mapa kol je hotová a schválená, můžeš ji po doporučených krocích sloučit a otevřít první kola.` / `Mapa kol hotová není – brání tomu: <konkrétní seznam>.`
- `Kolo je rozhodnuté a schválené, můžeš pustit doporučené kroky a pak /architect k zápisu před sloučením.` / `Kolo rozhodnuté není – brání tomu: <konkrétní seznam>.`
- `Kolo je zapsané a připravené ke sloučení, můžeš větev přimergovat.` / `Kolo zapsané není – brání tomu: <konkrétní seznam>.`
- `Návrh je sešitý a schválený, můžeš pustit doporučené kroky a pak /architect k dočištění.` / `Návrh sešitý není – brání tomu: <konkrétní seznam>.`
- `Návrh je uzavřený, můžeš větev přimergovat a pokračovat na /breakdown.` / `Návrh uzavřený není – brání tomu: <konkrétní seznam>.`
