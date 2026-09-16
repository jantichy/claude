---
name: specify
description: Skill se použije, když uživatel zadá "/specify" (volitelně s režimem auto, create, round nebo close a se jménem kola), nebo chce z nápadu udělat zadání – produktovou specifikaci a návrh řešení nového projektu, aplikace, webu nebo větší feature, ještě než se začne programovat –, případně pokračovat dalším kolem rozpracovaného návrhu. Vede řízený rozhovor otázku po otázce a sepíše docs/requirements.md a docs/architecture.md. Větší záměr nejdřív rozdělí na tematická kola a zapíše je do todo.md, aby šla řešit postupně i souběžně v samostatných větvích, a nakonec je sešije do jednoho návrhu. Navazující kroky jen doporučuje, sám je nevolá.
argument-hint: [auto|create|round|close] [kolo]
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, Skill]
---

# Specify

## Co skill dělá

Uživatel má nápad a chce z něj zadání, podle kterého se dá stavět. Skill ho provede řízeným rozhovorem a sepíše **dva dokumenty** – u návrhu po kolech k nim navíc jeden tematický dokument na kolo (`docs/<téma>.md`):

| Dokument | Odpovídá na otázku | Pro koho |
|---|---|---|
| **`docs/requirements.md`** | Co stavíme a proč | Zadavatel, produkt, obchod – a ty za půl roku |
| **`docs/architecture.md`** | Jak to postavíme | Ten, kdo to bude implementovat |

V *Životním cyklu projektu* (`~/.claude/RULES.md`) je to třetí krok zakládání: navazuje na `/discovery` a předává na `/oponent`.

**Větší záměr se nedělá jedním zátahem, ale po kolech.** Kolo je uzavřený průchod jedním tematickým okruhem návrhu do posledního detailu – DPH, upomínání, administrace, platební brána. Skill záměr na začátku zmapuje, rozdělí na kola a zapíše je do `docs/todo.md`. Každé kolo se pak dá odjet v samostatné session a větvi, souběžně s ostatními. Proč to funguje: témata se prolínají, takže průchod po dokumentech by každý z nich otevřel pětkrát a pokaždé s jiným kusem znalosti v hlavě, kdežto průchod po tématech ho otevře stejněkrát, ale pokaždé s uzavřenou otázkou.

| Režim | Co dělá |
|---|---|
| **`auto`** (výchozí) | pozná, kde návrh je, a zavolá jeden z režimů níž – viz *Fáze 0* |
| **`create`** | zmapuje záměr a buď ho odjede jedním zátahem, nebo ho rozdělí na kola (*Fáze 1–6*) |
| **`round [kolo]`** | odjede jedno kolo; bez jména vypíše zbývající kola a nabídne, čím pokračovat |
| **`close`** | po sloučení všech kol je sešije, vyrobí `architecture.md` a dočistí návrh |

**Kola jsou uvnitř skillu, ne samostatný krok cyklu** – oddělená fáze před `/specify` by do cyklu přidala krok, jehož výstup by `/specify` jen přepisoval. **Režimy `round` a `close` jsou záměrně v tomhle souboru**, přestože ho protáhly přes 300 řádků (rozhodnuto 16. 9. 2026): s `create` a `auto` sdílejí zásady i fáze a vytažené do vedlejšího souboru by se četly jen zčásti.

## Co skill nedělá

- **Nic neprogramuje.** Ani scaffold, ani „jen rychle rozjedu projekt“. Tvrdá kontrola – viz *Zákaz implementace*.
- **Nezakládá projekt.** Strukturu, git, autocommit a doménové importy dělá `/project`. Když chybí, skill na to upozorní a nabídne ho.
- **Nezkoumá konkurenci ani trh.** Kdo to už dělá, za kolik a co je na tom rizikové, zjišťuje `/discovery` do `docs/competition.md` a `docs/risks.md`. Tenhle skill je čte jako hotový vstup – zejména sekci *Co poměřujeme*, na kterou se tedy neptá podruhé.
- **Nepíše implementační plán.** Ten dělá `/breakdown`. Skill ho jen doporučí jako další krok, až je zadání schválené.
- **Neduplikuje `superpowers:brainstorming`.** Dialog, klasifikaci rozsahu i návrh řešení řídí ten skill.
- **Nevolá další kroky, jen je doporučuje.** `/oponent`, `/review`, `/consistency`, `/cleanup` i `/breakdown` jsou samostatné kroky; kdyby je skill pouštěl sám, staly by se jeho součástí. V závěru každého běhu řekne, co a v jakém pořadí pustit.
- **Neslučuje větve sám.** Kdy a jak se větev kola slučuje, drží `~/.claude/WORKTREE.md` – merguje se jen na výslovný pokyn.

## Jak je to postavené uvnitř

**Dialog a návrh řešení dělá `superpowers:brainstorming`, a to je implementační detail, ne rozhraní.** Kdyby ho nahradil jiný nástroj nebo vlastní postup, nikdo se to nemusí dozvědět. **Závazné je to, co po skillu zbude:** dva dokumenty na místech podle `~/.claude/STRUCTURE.md` – produktové požadavky a návrh řešení –, u návrhu po kolech k tomu tematické dokumenty, mapa kol a záznamy kol, vše česky a bez datumových prefixů. Cizímu nástroji se to musí říct výslovně, protože má vlastní výchozí volbu (viz *Přepis výchozí cesty* níž).

| Krok | Kdo ho dělá |
|---|---|
| Klasifikace rozsahu (spike / bounded / architectural) | `superpowers:brainstorming` |
| Doptávání, varianty řešení, návrh, schvalovací kontroly | `superpowers:brainstorming` |
| **Produktový rámec a sepsání požadavků** | **tenhle skill** |
| **Mapa kol, vedení kola, sešití kol** | **tenhle skill** – kolo `brainstorming` nevolá, rozhovor vede samo podle *Zásad pro celý průběh* |
| Sepsání návrhu řešení | `brainstorming` ho vytvoří, tenhle skill mu určí cíl a tvar |
| Implementační plán | `/breakdown` |
| Implementace plánu | `/implement` |

**Přepis výchozí cesty.** `brainstorming` ukládá design doc do `docs/superpowers/specs/YYYY-MM-DD-<téma>-design.md`. Explicitně přitom respektuje uživatelovu preferenci a ta zní jinak – podle `~/.claude/STRUCTURE.md` jsou v `docs/` jednoslovné anglické názvy bez datumových prefixů, takže cíl je **`docs/architecture.md`**.

**Řekni mu to výslovně**, když ho vyvoláváš. Jinak si založí vlastní adresářový strom vedle toho tvého. Totéž platí pro plán, ale ten už si hlídá `/breakdown`.

**Zadání pro plán je `docs/architecture.md`**, ne `requirements.md`. Plán argumentuje z návrhu řešení; požadavky jdou jako doplňkový kontext, aby bylo vidět, proč se to staví. O předání se stará `/breakdown`.

## Proč dva dokumenty a ne jeden

Mají **jinou životnost**. Produktový záměr se mění zřídka; technické řešení s každým rozhodnutím o technologii. V jednom souboru se při výměně databáze edituje tentýž dokument, ve kterém stojí popis cílové skupiny – a produktová část se tím postupně obrušuje. Platí tu *Cílová skupina určuje umístění* z `~/.claude/RULES.md`.

**Nerozejdou se, protože se nepřekrývají.** Hranice je tvrdá:

- **Do požadavků patří omezení**, do návrhu řešení **volba**. „Musí to běžet na běžném sdíleném hostingu bez placených závislostí“ je produktové omezení a patří do `requirements.md`. „Použijeme SQLite, protože…“ je volba a patří do `architecture.md`.
- **`requirements.md` nesmí obsahovat architekturu.** Ani „nejspíš to bude na Vercelu“. Jakmile to tam napíšeš, začne se to rozcházet s `architecture.md`.
- **`architecture.md` nesmí obsahovat zdůvodnění produktu.** Argumentuje z požadavků odkazem, neopisuje je.

Když si nejsi jistý, kam věta patří, ptej se: *změní se, když se změní technologie?* Ano → `architecture.md`. Ne → `requirements.md`.

## Zásady pro celý průběh

- **Ptej se postupně a přes tool `AskUserQuestion`** – postup, tvar otázky i mechanika toolu viz `~/.claude/RULES.md`, *Ptej se postupně, ne všechno najednou*.
- **Nic si nevymýšlej** – technický název, ID, parametr, cizí API, cena. Viz `~/.claude/RULES.md`, *Při nejistotě se zeptej*.
- **Zapisuj průběžně** – ve chvíli, kdy rozhodnutí padne, ne až na konci. Viz `~/.claude/RULES.md`, *Pravda v souborech, ne v konverzaci*; kam co patří, definuje `STRUCTURE.md`.
- **Navrhuj kompletně, implementuj postupně** – viz `~/.claude/RULES.md`. Tady to znamená: požadavky i návrh řešení popisují celou věc včetně toho, co bude až později; řeže se až plán, a ten se dělá jen na MVP.
- **YAGNI.** Z každého návrhu vyhoď, co není potřeba – ale zapiš to do *Mimo rozsah*, ať je vidět, že to bylo zvážené a zamítnuté, ne opomenuté.

------

## Zákaz implementace

**Dokud není návrh hotový a schválený, nesmí vzniknout ani řádek produkčního kódu.** Žádný scaffold, žádné `npm create`, žádná databáze, žádné „jen si ověřím, že to jde“.

Výjimka je jediná: **ověřovací pokus**, když na odpovědi stojí rozhodnutí v návrhu („zvládne to hosting?“, „má to API tenhle endpoint?“). Pak řekni dopředu, co zkoušíš a proč, výsledek použij jako podklad a **kód zahoď** – označ ho jako jednorázový a nenechávej ho v projektu.

| Myšlenka | Realita |
|---|---|
| „Zadání je jasné, začnu rovnou“ | Když je jasné, sepsání trvá deset minut. Když ne, právě proto se píše. |
| „Udělám scaffold, ať máme na čem stavět“ | Scaffold zamkne tech stack dřív, než se rozhodl. |
| „Uživatel mi řekl ‚udělej to‘“ | Řekl `/specify`. Kdyby chtěl kód, řekl by to. |

------

## Fáze 0 – Příprava

**Společný začátek drží `~/.claude/skills/PREFLIGHT.md`** – načti si ho a řiď se jím. Body 4 a 5 odpadají: tenhle skill nesahá na kód a pracuje nad nápadem, ne nad diffem větve.

Navíc si zjisti tohle:

1. **Zkontroluj strukturu.** Existují standardní soubory `todo.md`, `backlog.md`, `done.md`, `decisions.md`, `rules.md` (v `docs/`, nebo v kořeni podle režimu)? Chybí-li, **nezakládej je potichu** – vypiš, co chybí, a nabídni `/project`. Pokračuj až pak; specifikace bez místa, kam zapisovat rozhodnutí, je poloviční práce. **Chybějící `backlog.md` sám o sobě neblokuje** – není kam zapisovat, ale je co psát; zmiň ho ve výpisu a pokračuj (Fáze 1, bod 5 s tím počítá).
   **Přečti si i `## Struktura a dokumentace` v `CLAUDE.md`** – jsou-li tam vypsané *Produktové podklady*, projekt se zavázal je vést. **Tenhle skill z nich píše tři** – `scenarios.md`, `glossary.md` a `pricing.md` (Fáze 3a); `competition.md` a `risks.md` patří `/discovery`. Chybí-li ty dva, přestože jsou zapsané, **nabídni `/discovery`**: bez konkurence a rizik se píše zadání naslepo.
2. **Existující podklady.** Projdi, co v projektu už je – zadání, brief, zápis ze schůzky, starý systém, exporty, `docs/research/`. **Cizí podklady jsou read-only** – kopírovat si z nich do projektu smíš a máš, zapisovat do nich nikdy.
3. **Režim `auto` rozhodne, kam jít.** Vyhrává první řádek, který sedí:

   | Stav | Režim |
   |---|---|
   | argument je jméno kola ze sekce *Kola návrhu* v `docs/todo.md` | `round` s tím kolem – `/specify DPH` je totéž co `/specify round DPH` |
   | session stojí ve větvi, kterou uvádí blok kola na řádku *Větev* | `round` s tím kolem – rozpozná, jestli se rozhoduje, nebo zapisuje před sloučením |
   | sekce *Kola návrhu* má aspoň jeden blok | `round` bez jména – nabídka zbývajících kol |
   | `docs/done.md` má v sekci *Kola návrhu* aspoň jeden záznam kola a za posledním z nich nestojí řádek *Návrh uzavřen* | `close` |
   | jinak | `create` – vstupní bod podle bodu 4 |

   **Neexistující sekce se počítá jako prázdná**, o `close` proto rozhoduje `done.md`, ne `todo.md`: projekt, který kola nikdy neměl, žádný záznam kola nemá, a druhá várka kol se od první odliší řádkem *Návrh uzavřen*.

   **Jméno kola** se porovnává bez ohledu na velikost písmen s nadpisem bloku bez „Kolo o“, se jménem větve i se jménem tematického dokumentu. Víc shod → zeptej se. Jméno režimu má přednost před jménem kola, proto se kolo nesmí jmenovat `auto`, `create`, `round` ani `close`. Argument, který není jménem kola ani režimu, ber jako téma pro `create` a řekni to. Zvolený režim oznam jednou větou, ať se dá opravit.

5. **Větev.** Běží-li projekt ve worktree layoutu a session stojí v `main/` nebo ve větvi, která s režimem nesouvisí, nabídni založení větve podle `~/.claude/WORKTREE.md`, *Založení větve*, **dřív, než cokoliv zapíšeš**: `create` do `docs/specify`, kolo do větve z řádku *Větev*, `close` do `docs/close`. Existuje-li větev toho jména z dřívější várky, přidej příponu `-2`.

4. **Urči vstupní bod** – jen pro režim `create`, ostatní režimy mají vlastní přípravu. **Má-li sekce *Kola návrhu* bloky, `create` nepokračuj:** návrh běží po kolech a nabídka tabulky níž by vedla k psaní `architecture.md` uprostřed kol – řekni to a nabídni `round`. Skill se dá spustit i uprostřed – neběží vždycky celý:

   | Stav | Kde začít |
   |---|---|
   | `requirements.md` ani `architecture.md` neexistují | Fáze 1, celý běh |
   | `requirements.md` existuje, `architecture.md` ne | Zeptej se: **navázat návrhem řešení**, nebo revidovat požadavky? Tohle je běžný případ – produkt se schválí dnes, návrh se dělá jindy. Při navázání **projdi Fázi 2 i tak** – `brainstorming` musíš vyvolat, jinak nemá kdo návrh vytvořit; jen mu místo produktových otázek předej hotové `docs/requirements.md` jako zadání a rovnou jdi na varianty řešení. |
   | Existují oba | Jde o revizi, nebo o novou část projektu? Při revizi **nepřepisuj** – rozšiř a přeformuluj stávající. |
   | `architecture.md` existuje a přidává se feature | Rozšiř ho. **Nezakládej druhý návrhový dokument** – jeden systém, jeden návrh. |

------

## Fáze 1 – Nultý krok: vytěž, co už uživatel má

**Než se na cokoliv zeptáš**, vyzvi ho, ať přiloží nebo nakopíruje všechno, co k tomu má – i nestrukturovaně. Zápis ze schůzky, poznámky, starý dokument, screenshoty, konkurenční web, mail od klienta.

0. **Nejdřív si přečti, co v projektu už je** – zejména `docs/competition.md` a `docs/risks.md` od `/discovery`, a `docs/backlog.md` a `docs/todo.md` (viz bod 5). Sekce *Co poměřujeme* odpovídá na to, jaký problém řešíme a komu; *Naše pozice a odlišení* říká, co produkt musí umět a čím se liší; rizika říkají, co musí být postavené jinak. **Na nic z toho se neptej znovu** – shrň to a nech potvrdit.
1. **Originály ulož** do projektu (`docs/research/`), ať se dají dohledat.
2. **Sám si z nich zodpověz co nejvíc.** Cokoliv, co z podkladů plyne, se už neptej.
3. **Vypiš souhrn, co sis z toho odvodil**, ať to uživatel jedním pohledem potvrdí nebo opraví.
4. **Doptávej se jen na zbytek** – a na věci, kde si nejsi jistý.
5. **Projdi `docs/backlog.md` a vytěž z něj, co do tohohle zadání patří.** Je to zásobník nezávazných nápadů (`~/.claude/STRUCTURE.md`, *`backlog.md`*) a tohle je jediné místo, kde se čte – nápad, který nikdo neprojde teď, tam bude ležet dál a nikomu se nepřipomene.

   Postup: vypiš položky, které se s tématem zadání překrývají nebo ho přirozeně rozšiřují, u každé jednou větou proč. Pak se **zeptej přes `AskUserQuestion`, jednu položku na volání** – *Zařadit do zadání* / *Nechat v backlogu* / *Zahodit*. Zařazenou položku **přesuň z backlogu do rozpracovaného zadání**, ať neleží na dvou místech; zahozenou smaž a měla-li odůvodnění, zapiš ho do `docs/decisions.md`.

   **Nezařazuj nic sám.** Backlog je seznam toho, o čem se nerozhodlo – rozhodnutí je uživatelovo, ne tvoje. Je-li backlog prázdný nebo v projektu není, řekni to jednou větou a jeď dál. Projdi stejným pohledem i `docs/todo.md`: co v něm leží k tématu zadání, patří do specifikace, ne vedle ní.

Nemá-li nic, přeskoč. Ale zeptej se – v praxi něco má skoro vždycky a nenapadne ho to poslat.

------

## Fáze 2 – Klasifikace a dialog

**Vyvolej `superpowers:brainstorming`.** Předej mu:

- co ses dozvěděl z podkladů ve Fázi 1,
- že se má ptát přes `AskUserQuestion`, jednu otázku na volání,
- že **návrhovou část zapíše do `docs/architecture.md`**, ne do `docs/superpowers/specs/`, a až ve Fázi 3b – tedy po schválení produktové části. Rozhodne-li mapa okruhů níž o kolech, návrhovou část v tomhle běhu **nepíše vůbec**; řekni mu to, jakmile to padne.

**Co udělat s klasifikací:**

| Cesta | Co dělat |
|---|---|
| **Architectural** | Normální běh skillu. Tohle je jeho případ. |
| **Bounded** | Specifikace nedává smysl – je to změna v existujícím kódu. **Řekni to a zastav se.** Nabídni pokračovat rovnou přes `brainstorming` (krátký návrh v chatu → schválení → implementace). Nenech se zatlačit do psaní specifikace na jednosouborovou změnu. |
| **Spike** | Totéž – výstupem je odpověď, ne dokument. Zastav se a nabídni ověřovací pokus. |

### Mapa okruhů: kola, nebo jeden zátah

**Vždycky zmapuj tematické okruhy záměru** – ne kapitoly dokumentu, ale témata, o kterých se bude rozhodovat. **Vyjdou-li aspoň dva, které mají vlastní otevřené otázky a zasahují do sdílených dokumentů, navrhni kola;** jinak jeden zátah. Mapu i volbu ukaž a nech potvrdit přes `AskUserQuestion`. Kritérium stojí tady, ne v klasifikaci `brainstormingu`, protože ta je implementační detail. **Zamítnuto „vždycky kola“:** u malé feature by blok v `todo.md`, tematický dokument, záznam v `done.md` a `close` nad jediným kolem byly jen režie.

**Jeden zátah** pokračuje Fází 3a a 3b jako dosud.

**Po kolech** se postup mění:

1. **Zapiš mapu** do sekce `## Kola návrhu` v `docs/todo.md`, jeden blok na kolo. Ne do samostatného souboru – evidence zbývajících a hotových kol by se rozdělila na dvě místa –, a ne jako běžné položky, protože ty `auto` od kola nerozezná a otázky se pak odkládají na kola, která už proběhla. Tvar bloku drží `~/.claude/STRUCTURE.md`, *`todo.md`*. **Blok musí stačit čisté session** – nese celé zadání, podklady a závislosti. Otevřené otázky, které k tématu kola patří, přesuň do jeho bloku.
2. **Fáze 3a sepíše `requirements.md` za celek** – proč, pro koho, hrubé *MVP*, *Mimo rozsah*, omezení. Detail okruhů nechá kolům a v sekcích, které doplní kolo, na ně odkáže jménem.
3. **Fáze 3b se přeskakuje.** `architecture.md` vznikne až v režimu `close` nad výsledky všech kol; souběžná kola by se v něm srážela a návrh řešení stojí na schválených požadavcích celku, ne na polovině kol.
4. **Závěr** vypíše mapu a doporučí, čím začít – viz *Fáze 6*.

**Ve worktree layoutu** se mapa s `requirements.md` musí sloučit do `main` dřív, než se otevře první kolo – větev kola vzniká z `origin/main` a bez toho by mapu neměla. Větev pro `create` zakládá už *Fáze 0*, bod 5, protože Fáze 1 zapisuje dřív, než padne rozhodnutí o kolech.

**Bez worktree layoutu** se kola neřeší souběžně, ale jedno po druhém: dvě session nad jedním pracovním stromem by si zápisy smíchaly. Skill to v závěru řekne.

**Rozsah.** Popisuje-li zadání víc nezávislých podsystémů, řekni to hned a rozlož to na dílčí projekty dřív, než se začnou ladit detaily. Každý dílčí projekt pak dostane vlastní dokumenty i vlastní plán. **Kola nejsou dílčí projekty:** kola jsou okruhy jednoho systému, které se prolínají, dílčí projekty jsou systémy, které se neprolínají.

**Projekt bez kódu.** Je-li to znalostní, obsahový nebo obchodní projekt (kurz, brand, pozicování, evidence), `requirements.md` dává smysl, ale **návrh řešení ani `writing-plans` ne** – ty předpokládají kód, testy a commity. Skonči po Fázi 3a a místo plánu nabídni postupný rozpis kroků do `docs/todo.md`.

------

## Fáze 3a – Produktová specifikace

Zapiš do **`docs/requirements.md`**. Šablona je v `~/.claude/skills/specify/documents.md`, `docs/requirements.md`; pravidla psaní tamtéž v sekci *Jak se píše*. **Přečti si ten soubor celý, než začneš psát** – platí pro oba dokumenty i pro produktové podklady.


### Scénáře, glosář a ceník

Tři z *Produktových podkladů*, které projekt vede volitelně (`## Struktura a dokumentace` v `CLAUDE.md`, viz Fáze 0) – zbylé dva, `competition.md` a `risks.md`, píše `/discovery`. Vede-li projekt některý z téhle trojice, **sepiš ho v tomhle kroku spolu s požadavky**: všechny tři jsou produktové, ne technické, a vznikají z téhož dialogu. Šablony a pravidla drží `~/.claude/skills/specify/documents.md`; definici toho, co který dokument je, `~/.claude/STRUCTURE.md`, *Produktové podklady*.

**Nevede-li projekt žádný z nich, nic nezakládej** a jdi rovnou na kontrolu. Zdá-li se ti přitom, že by se některý hodil, řekni to jednou větou a nech rozhodnout – závazek vede `CLAUDE.md`, ne tenhle běh.

**Kontrola uživatele.** Po sebe-revizi (Fáze 4) napiš:

> Požadavky jsou sepsané a commitnuté v `docs/requirements.md`. Přečti si ho prosím a řekni, jestli chceš něco změnit, než se pustíme do návrhu řešení.

U návrhu po kolech končí věta „…, než otevřeme první kola.“

**Počkej na odpověď.** Bez výslovného souhlasu nepokračuj na 3b – návrh postavený na neschváleném zadání se zahazuje celý.

------

## Fáze 3b – Návrh řešení

**Na návrhu se nešetří: nejsilnější model, `xhigh`.** Volba modelu a effortu podle `~/.claude/RULES.md`, *Model a effort podle úkolu*. Tohle není výroba dokumentu – dokument je jen zápis. Je to rozhodnutí, které se propíše do každého úkolu plánu a do každého řádku kódu pod ním, a **špatný návrh se dobrou implementací nezachrání**: špatná věc se jen udělá pořádně. Zápis hotového rozhodnutí do šablony už chytrý být nemusí.


**Píše se, když platí aspoň jedno:**

- je to nový projekt nebo nový podsystém,
- zavádí nebo mění datový model či perzistentní stav,
- zavádí rozhraní, na kterém stojí něco dalšího (API, formát, kontrakt),
- napojuje se na cizí systém (platební kontrola, fakturace, externí API),
- má stavový prostor s přechody,
- existuje víc než jedna rozumná cesta, jak to postavit.

**Nepíše se, když** je to přírůstek uvnitř už navrženého systému – pak rozšiř stávající `architecture.md`. A **nikdy** u projektu bez kódu.

Přeskočíš-li ho, **řekni to i s důvodem** a jako zadání pro plán použij `requirements.md`.

**U návrhu po kolech se tady nepíše ani nepřeskakuje** – vzniká v režimu `close`, a do té doby není zadání pro plán vůbec.

Návrh vytvoří `brainstorming` v dialogu s uživatelem – po sekcích, se schválením po každé. Zapiš do **`docs/architecture.md`**; šablona i pravidla psaní jsou v `~/.claude/skills/specify/documents.md`.

**Kontrola proti požadavkům:** projdi scénáře (ze `scenarios.md`, nebo ze sekce *Hlavní scénáře*), *Varianty* a *Nefunkční požadavky* a u každého ukaž, co v návrhu ho pokrývá. Nepokryté je nález, ne detail. Vede-li projekt `risks.md`, projdi i **mitigace**: riziko s vyplněným *Promítnutím do produktu* musí mít v návrhu protějšek, jinak se mitigace nestala.

**Bezpečnost se navrhuje, neaudituje.** Zhruba polovina kódu psaného modely obsahuje bezpečnostní chybu a je to předvídatelná množina. Nejúčinnější obrana není kontrola na konci, ale struktura, ve které díra nejde udělat – jedna vrstva autorizace, kterou nelze obejít, výhradně parametrizované dotazy, validace na hranici, tajemství jen z prostředí. Proto má návrh sekci *Bezpečnostní model*, a proto v ní nesmí stát „ošetříme to při implementaci“.

**Doménové standardy.** Návrh se řídí tím, co si projekt importuje v `CLAUDE.md` – `~/Dev/context/coding/coding.md` vždy, dál podle povahy `web/web.md`, `web/admin.md`, `analytics/analytics.md`. Načti je, než začneš navrhovat, ne až při kontrole.

------

## Fáze 4 – Sebe-revize a oponentura

Běží **po každém dokumentu zvlášť** – požadavcích, návrhu řešení i tematickém dokumentu kola –, ne až na konci.

**Sebe-revize** (rozšíření *Spec Self-Review* z brainstormingu):

1. **Placeholdery** – „TBD“, „TODO“, nedokončené sekce, vágní požadavky. Oprav.
2. **Vnitřní rozpory** – neodporují si sekce? Sedí počty a výčty s obsahem?
3. **Vymyšlené věci** – je tam technický název, ID, parametr nebo číslo, které jsi neměl od uživatele ani z podkladů? To je nález. Dohledej, nebo přesuň do *Otevřených otázek*.
4. **Prosakování hranice** – je v `requirements.md` architektura nebo volba technologie? Je v `architecture.md` zdůvodnění produktu? Přesuň.
5. **Pokrytí** – u návrhu proti požadavkům (viz 3b), u požadavků proti tomu, co padlo v dialogu.
6. **Dvojznačnost** – dá se něco přečíst dvěma způsoby? Vyber jeden a napiš ho jednoznačně.
7. **Rozsah** – vejde se to do jednoho implementačního plánu? Pokud ne, dekomponuj.
8. **Mimo rozsah není prázdné** (jen `requirements.md`) – prázdná sekce znamená, že se neřezalo.
9. **Scénáře, glosář a ceník** – vede-li je projekt: nezůstal v `requirements.md` druhý seznam scénářů vedle `scenarios.md`? Má každý scénář popsanou aspoň jednu cestu, kde může selhat? Rozlišuje glosář pojmy, které se pletou, nebo je to jen výčet? Je každý limit z `pricing.md` v *MVP*, nebo v *Mimo rozsah*?

**Oponentura.** Dokument jsi psal ty a jsi na něj zaujatý. `/oponent` je **krok životního cyklu**, ne nabídka: pusť ho, nebo nahlas řekni, proč se u téhle změny přeskakuje. Nabízej ho pro každý dokument zvlášť (`/oponent docs/requirements.md`, `/oponent docs/architecture.md`), protože panel hledisek se pro požadavky a pro návrh řešení liší.

**Hlediska nevypisuj** – sestaví si je sám podle sloupce *Spouštěč* ve svém katalogu (`~/.claude/skills/oponent/SKILL.md`, *Volba hledisek*) a nechá si je od uživatele potvrdit. Výčet zopakovaný tady by se s katalogem rozešel při první jeho změně (`~/.claude/RULES.md`, *Single source of truth*).

**Kontrola uživatele** – po požadavcích (viz 3a) i po návrhu řešení:

> Návrh řešení je sepsaný a commitnutý v `docs/architecture.md`. Přečti si ho prosím a řekni, jestli chceš něco změnit, než z něj uděláme implementační plán.

Počkej na odpověď. Chce-li změny, proveď je a projdi sebe-revizi znovu.

------

## Fáze 5 – Předání do plánu

Po schválení návrhu **doporuč `/breakdown`**, který ze zadání udělá `docs/plan.md` – sám ho nevolej (*Co skill nedělá*). Ten si sám najde zadání i kontext a ohlídá rozsah, takže mu nic předávat nemusíš. **U návrhu po kolech** se doporučuje až v závěru `close`.

**Sám plán nepiš.** Ani „ať se to nemusí volat zvlášť“. Rozpad na úkoly má vlastní pravidla, vlastní kontrolu pokrytí MVP a vlastní schvalovací kontrolu.

**U projektu bez kódu** `/breakdown` nedoporučuj – rozepiš kroky do `docs/todo.md`.

Celý řetěz i s tím, co následuje po implementaci, je v `~/.claude/skills/LIFECYCLE.md`.

------

## Když se zadání změní později

Platí *Doc-first vývoj* z `~/.claude/RULES.md`; posloupnost souborů definuje `STRUCTURE.md`:

1. Změní se požadavek → uprav **`requirements.md`**, u návrhu po kolech i **tematický dokument** dotčeného okruhu, a s tím **`scenarios.md`**, vede-li ho projekt. Změněný požadavek skoro vždycky mění nějaký scénář; scénář, který zůstal, ale už nejde provést, je horší než chybějící.
2. Zkontroluj, jestli to mění návrh → uprav **`architecture.md`**.
3. Zkontroluj, jestli to mění nehotové úkoly → uprav **`plan.md`**.
4. Rozhodnutí a důvod změny zapiš do `docs/decisions.md`. Původní záznam nepřepisuj – přibude revize.

Přijde-li změna zdola (při implementaci se ukáže, že návrh nejde), **neopravuj to potichu v kódu**. Vrať se do návrhu řešení, uprav ho, a je-li dotčený i produktový záměr, řekni to a nech rozhodnout uživatele.

------

## Fáze 6 – Závěr

```
## Zadání hotové

**Dokumenty**
- docs/requirements.md – <počet> sekcí
- docs/architecture.md – <počet> sekcí (nebo „přeskočeno: <důvod>“)
- docs/scenarios.md – <počet> scénářů (jen vede-li je projekt)
- docs/glossary.md – <počet> pojmů (jen vede-li je projekt)
- docs/pricing.md – <počet> tarifů (jen vede-li je projekt)

**Zapsáno mimo ně**
- docs/decisions.md: N rozhodnutí
- docs/todo.md: N odložených položek
- docs/backlog.md: N nápadů vytaženo do zadání, M ponecháno
- docs/rules.md: N principů

**Otevřené otázky**
- [seznam, nebo „žádné“]

**Další krok**
- [/breakdown / u projektu bez kódu rozpis kroků do docs/todo.md]
```

Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo – `~/.claude/RULES.md`, *Styl odpovědí*.

**U návrhu po kolech** vypadá závěr jinak: místo `architecture.md` vypiš mapu kol – u každého jméno, větev a na co čeká – a doporuč, **která kola pustit hned a souběžně**: ta bez nesplněné závislosti, a přednostně ta, jejichž řádky *Sahá na* se nepřekrývají. Pod to doporuč `/oponent docs/requirements.md`, `/cleanup` a ve worktree layoutu sloučení větve – teprve pak se otevírají kola; `/breakdown` ne, ten přijde až po `close`.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Zadání je hotové a schválené, můžeme na implementační plán.`
- `Zadání hotové není – brání tomu: <konkrétní seznam>.`

U návrhu po kolech místo nich:

- `Mapa kol je hotová a schválená, můžeš ji po doporučených krocích sloučit a otevřít první kola.`
- `Mapa kol hotová není – brání tomu: <konkrétní seznam>.`

------

## Režim `round`

Odjede **jedno kolo** návrhu: vezme blok ze sekce *Kola návrhu* v `docs/todo.md`, rozhodne jeho téma do posledního detailu a zapíše výsledek. Zásady pro celý průběh a *Zákaz implementace* platí beze změny. Na rozhodování v kole se nešetří stejně jako na návrhu řešení (*Fáze 3b*); kolo ale běží v hlavní session, kde model ani effort skill nastavit neumí – **doporuč proto kolo pustit v session na nejsilnějším modelu**.

Kolo má **dva běhy ve své větvi**: rozhodování (kroky 1–4) a zápis před sloučením (krok 5), mezi nimi doporučené kroky. **Rozliší je řádek *Stav* v bloku kola**: `rozhodnuto` znamená, že je kolo schválené a na řadě je zápis. Proběhly-li doporučené kroky, poznáš z `## Průchody životním cyklem` v `docs/done.md`; chybí-li tam, zeptej se, jestli je uživatel vědomě přeskočil. Po zápisu blok neexistuje – ve větvi kola pak `auto` pozná kolo podle řádku *Větev* v jeho záznamu v `done.md` a řekne, že čeká na sloučení.

### Bez jména kola: nabídka

Vypiš všechna zbývající kola – jméno, na co čeká a jestli už má větev (`git branch -a`; existující větev z řádku *Větev* znamená kolo rozběhnuté jinde, případně hotové a čekající na sloučení). **Bez worktree layoutu** rozběhnuté kolo poznat nejde – řekni to. Pak přes `AskUserQuestion` nabídni **několik nejbližších**: nejdřív kola bez nesplněné závislosti, mezi nimi ta, na která čeká nejvíc dalších kol nebo nejvíc odložených otázek. U každé volby řekni, do kterých sdílených dokumentů kolo sahá a jestli se to kříží s rozběhnutým kolem – **souběh tím neblokuj, jen na něj upozorni**.

### 1. Příprava kola

1. **Větev** podle *Fáze 0*, bod 5. Jméno větve se řídí zvykem projektu (`~/.claude/WORKTREE.md`), jméno tematického dokumentu je jednoslovné anglicky (`~/.claude/RULES.md`, *Naming*), nadpis bloku česky. Existuje-li tematický dokument z dřívější várky, **rozšiř ho**. Nastav v bloku *Stav* na `rozhoduje se` a commitni.
2. **Načti blok kola**, `requirements.md`, dokumenty z řádků *Dokument* a *Sahá na*, `decisions.md` a `rules.md`. Kolo, na které tohle čeká, musí mít záznam v `docs/done.md` **za posledním řádkem *Návrh uzavřen*** – starší záznam téhož jména patří dřívější várce. Nemá-li ho, řekni to a zeptej se, jestli pokračovat.
3. **Zadání kola ověř, ne převezmi.** Blok je zadání, ne odpověď. Ukáže-li se při prvním pohledu do podkladů, že otázky v něm jsou neúplné nebo špatně položené, řekni to a nech nové zadání potvrdit – kolo smí své zadání přepsat.

### 2. Rozhodování

Veď rozhovor otázku po otázce, dokud v tématu nezbývá otevřená otázka. Zapisuj průběžně:

- **Tematický dokument** `docs/<téma>.md` drží celý okruh; produktovou a technickou část odděluj stejnou hranicí jako `requirements.md` a `architecture.md` (*Proč dva dokumenty a ne jeden*).
- **Do sdílených dokumentů** – `requirements.md`, glosář, scénáře, model – zapiš jen to, co z tématu plyne pro celek, a odkaž se na tematický dokument. Psaní celého tématu rovnou do nich je zamítnuté, protože souběžné větve by se srazily v týchž kapitolách. **`architecture.md` nepiš**, vzniká v `close`.
- **Kapitola v `decisions.md` se píše bez čísla**, i když ho kapitoly v projektu mají, a odkazy na ni se píšou jménem. Číslo dostane až v kroku 5 – souběžná kola by si jinak vzala totéž.
- **Nová otevřená otázka mimo téma** se odkládá na **jmenované kolo**, ne na „později“: zapiš ji do jeho bloku. Nemá-li kam, vzniká nové kolo – dopiš jeho blok do mapy a řekni to.

### 3. Uzavření rozhodování

1. **Sebe-revize** tematického dokumentu a toho, co kolo zapsalo jinam – body 1–6 a 9 z *Fáze 4*.
2. **Schválení uživatelem**, stejně jako u požadavků ve *Fázi 3a*. Pak nastav v bloku *Stav* na `rozhodnuto` a commitni.

Blok v `todo.md` **zatím zůstává** a do `done.md` se nic nezapisuje: nálezy z doporučených kroků se musí mít kam vrátit a záznam kola má odkazovat na kapitolu, která už číslo má.

### 4. Závěr rozhodování

Vypiš, co kolo rozhodlo, co zapsalo kam, které otázky zůstaly a jaká nová kola vznikla. Pak **doporuč navazující kroky v tomhle pořadí** – každý jen tehdy, když se vyplatí, a u přeskočeného řekni proč:

1. **`/oponent docs/<téma>.md`**, zavedlo-li kolo nový podsystém, změnilo model nebo se napojilo na cizí systém; **`/review`**, sáhlo-li kolo na testy nebo kontroly, které projekt nad dokumentací vede (kód kolo nepíše, *Zákaz implementace*); **ani jedno**, bylo-li kolo drobné a posudek by jen zdržel.
2. **`/consistency`**, jen sáhlo-li kolo do hodně sdílených dokumentů. Většinou se vyplatí až nad celkem po `close`.
3. **`/cleanup`** – vždycky.
4. **`/specify` znovu v téhle větvi** – zapíše kolo jako hotové (krok 5); ve worktree layoutu pak sloučení.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Kolo je rozhodnuté a schválené, můžeš pustit doporučené kroky a pak /specify k zápisu před sloučením.`
- `Kolo rozhodnuté není – brání tomu: <konkrétní seznam>.`

### 5. Zápis před sloučením

Pouští se ve větvi kola po doporučených krocích. **Bez něj se větev kola neslučuje** – `~/.claude/WORKTREE.md`, *Dokončení větve*, na to odkazuje. Bez worktree layoutu odpadá natažení `origin/main` i sloučení a zbytek se udělá rovnou v pracovním stromu.

1. **Natáhni `origin/main` do větve.** Konflikt na konci `done.md` nebo `decisions.md` od souběžného kola vyřeš ponecháním obou zápisů za sebou. **Přibyla-li tím do bloku kola nová otázka, nebo změnilo-li souběžné kolo dokument z řádku *Sahá na* v tom, na čem tohle kolo stojí**, zápis nedělej: vrať *Stav* na `rozhoduje se`, řekni, co se změnilo, a vrať se ke kroku 2.
2. **Odložené otázky, které kolo neotevřelo, přepiš.** Přesuň je do bloku jiného kola; když na žádné kolo nečekají, ale na něco jiného (rozhodnutí, podklad, odpověď zvenčí), udělej z nich samostatnou položku `todo.md` a napiš, na co čekají. Položka s poznámkou, že čeká na kolo, které už proběhlo, se nesmí zachovat – nerozezná se od fronty.
3. **Přiděl kapitole v `decisions.md` další volné číslo** podle stavu po natažení a přepiš odkazy na ni ve všech souborech, na které kolo sáhlo.
4. **Záznam do `docs/done.md`**, sekce `## Kola návrhu`, v tvaru podle `~/.claude/STRUCTURE.md`, *`done.md`* – pole *Neotevřelo* z kroku 2 –, a smazání bloku z `docs/todo.md`.
5. **Commit.**
6. **Doporuč sloučení větve** – samo podle `~/.claude/WORKTREE.md`, *Dokončení větve*, a jen na pokyn. **Posune-li se mezitím `origin/main`** (`git log HEAD..origin/main` není prázdný), zopakuj natažení `origin/main` a přidělení čísla těsně před sloučením: jinak by si souběžné kolo sloučené o chvíli dřív vzalo totéž číslo a konflikt by se řešil v `main/`, kde se nepracuje.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Kolo je zapsané a připravené ke sloučení, můžeš větev přimergovat.`
- `Kolo zapsané není – brání tomu: <konkrétní seznam>.`

------

## Režim `close`

Pouští se, **až jsou všechna kola sloučená** – sekce *Kola návrhu* v `todo.md` je prázdná nebo neexistuje. Větev podle *Fáze 0*, bod 5. Jeho hlavní práce je **návrh řešení nad celkem**; kola ho záměrně nepsala. **Má dva běhy jako kolo:** sešití (kroky 1–3 a závěr), pak doporučené kroky, a nakonec dočištění (krok 4) – řádek *Návrh uzavřen* nesmí vzniknout dřív, než se nálezy z posudku mají kam vrátit. Druhý běh `auto` pozná podle toho, že větev už mění `architecture.md` proti `origin/main`; potvrď s uživatelem, že doporučené kroky proběhly.

1. **Ověř, že kola opravdu doběhla.** Sekce *Kola návrhu* je prázdná, žádná větev z řádků *Větev* v záznamech nejnovější várky není mimo `origin/main` (`git branch -a --no-merged origin/main`) a každé kolo z nejnovější várky má záznam v `docs/done.md` za posledním řádkem *Návrh uzavřen*. Chybí-li něco, řekni co a zastav se.
2. **Sešij požadavky.** Projdi `requirements.md` proti tematickým dokumentům: odkazuje na každý, nepřekrývá se s nimi, *MVP* a *Mimo rozsah* pokrývají, co kola rozhodla. Kontroly z *Fáze 4* platí nad celkem.
3. **Vyrob `architecture.md`** podle *Fáze 3b* – existuje-li z dřívější várky, **rozšiř ho**, druhý návrh nezakládej – z požadavků a technických částí tematických dokumentů. Volbu, kterou už rozhodlo kolo, **neopisuj, odkaž na ni**; na co návrh potřebuje odpověď a žádné kolo ji nedalo, se doptej. Kontrola uživatele jako ve *Fázi 4*.
4. **Dočisti** – ve druhém běhu, po doporučených krocích. Otázky přesunuté mezi koly musí být vypořádané, nebo vedené jako samostatná položka `todo.md` s tím, na co čekají. Zruš prázdnou sekci *Kola návrhu* v `todo.md` a do `done.md` připiš řádek *Návrh uzavřen* podle `~/.claude/STRUCTURE.md`, *`done.md`*.
5. **Závěr prvního běhu** vypíše dokumenty jako *Fáze 6* a doporučí v tomhle pořadí: `/oponent docs/architecture.md`, `/consistency` nad celým projektem, `/cleanup` a `/specify` znovu v téhle větvi. **Závěr druhého běhu** doporučí sloučení větve podle `~/.claude/WORKTREE.md` – **a teprve po něm `/breakdown`** jako další krok životního cyklu.

**Proč až tady a ne v kolech:** souběžná kola by se v jednom návrhu srážela a návrh řešení stojí na schválených požadavcích celku. **Zamítnuto** i uzavření složené do posledního kola – běželo by ve větvi dřív, než jsou ostatní větve sloučené.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Návrh je sešitý a schválený, můžeš pustit doporučené kroky a pak /specify k dočištění.`
- `Návrh je uzavřený, můžeš větev přimergovat a pokračovat na /breakdown.`
- `Návrh sešitý není – brání tomu: <konkrétní seznam>.`

První věta patří prvnímu běhu, druhá druhému.
