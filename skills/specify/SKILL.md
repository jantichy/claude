---
name: specify
description: Skill se použije, když uživatel zadá "/specify", nebo chce z nápadu udělat zadání – produktovou specifikaci a návrh řešení nového projektu, aplikace, webu nebo větší feature, ještě než se začne programovat. Vede debrief otázku po otázce, sepíše docs/requirements.md a docs/architecture.md a předá to do implementačního plánu.
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, Skill]
---

# Specify

## Co skill dělá

Uživatel má nápad a chce z něj zadání, podle kterého se dá stavět. Skill ho provede debriefem a sepíše **dva dokumenty**:

| Dokument | Odpovídá na otázku | Pro koho |
|---|---|---|
| **`docs/requirements.md`** | Co stavíme a proč | Zadavatel, produkt, obchod – a ty za půl roku |
| **`docs/architecture.md`** | Jak to postavíme | Ten, kdo to bude implementovat |

Pak je předá do implementačního plánu.

## Proč dva dokumenty a ne jeden

Mají **jinou životnost**. Produktový záměr se mění zřídka; technické řešení s každým rozhodnutím o technologii. V jednom souboru se při výměně databáze edituje tentýž dokument, ve kterém stojí popis cílové skupiny – a produktová část se tím postupně obrušuje. Platí tu *Cílová skupina určuje umístění* z `~/.claude/RULES.md`.

**Nerozejdou se, protože se nepřekrývají.** Hranice je tvrdá:

- **Do požadavků patří omezení**, do návrhu řešení **volba**. „Musí to běžet na běžném sdíleném hostingu bez placených závislostí“ je produktové omezení a patří do `requirements.md`. „Použijeme SQLite, protože…“ je volba a patří do `architecture.md`.
- **`requirements.md` nesmí obsahovat architekturu.** Ani „nejspíš to bude na Vercelu“. Jakmile to tam napíšeš, začne se to rozcházet s `architecture.md`.
- **`architecture.md` nesmí obsahovat zdůvodnění produktu.** Argumentuje z požadavků odkazem, neopisuje je.

Když si nejsi jistý, kam věta patří, ptej se: *změní se, když se změní technologie?* Ano → `architecture.md`. Ne → `requirements.md`.

V *Životním cyklu projektu* (`~/.claude/RULES.md`) je to druhý krok zakládání: navazuje na `/project` a předává na `/oponent`.

## Co skill nedělá

- **Nic neprogramuje.** Ani scaffold, ani „jen rychle rozjedu projekt“. Tvrdá brána – viz *Zákaz implementace*.
- **Nezakládá projekt.** Strukturu, git, autocommit a doménové importy dělá `/project`. Když chybí, skill na to upozorní a nabídne ho.
- **Nezkoumá konkurenci ani trh.** Kdo to už dělá, za kolik a co je na tom rizikové, zjišťuje `/discovery` do `docs/competition.md` a `docs/risks.md`. Tenhle skill je čte jako hotový vstup – zejména sekci *Co poměřujeme*, na kterou se tedy neptá podruhé.
- **Nepíše implementační plán.** Ten dělá `/breakdown`. Skill mu jen předá řízení, až je zadání schválené.
- **Neduplikuje `superpowers:brainstorming`.** Dialog, klasifikaci rozsahu i návrh řešení řídí ten skill.

## Vztah k superpowers

| Krok | Kdo ho dělá |
|---|---|
| Klasifikace rozsahu (spike / bounded / architectural) | `superpowers:brainstorming` |
| Doptávání, varianty řešení, návrh, schvalovací brány | `superpowers:brainstorming` |
| **Produktový rámec a sepsání požadavků** | **tenhle skill** |
| Sepsání návrhu řešení | `brainstorming` ho vytvoří, tenhle skill mu určí cíl a tvar |
| Implementační plán | `/breakdown` |
| Realizace plánu | `/implement` |

**Přepis výchozí cesty.** `brainstorming` ukládá design doc do `docs/superpowers/specs/YYYY-MM-DD-<téma>-design.md`. Explicitně přitom respektuje uživatelovu preferenci a ta zní jinak – podle `~/Dev/context/structure/structure.md` jsou v `docs/` jednoslovné anglické názvy bez datumových prefixů, takže cíl je **`docs/architecture.md`**.

**Řekni mu to výslovně**, když ho vyvoláváš. Jinak si založí vlastní adresářový strom vedle toho tvého. Totéž platí pro plán, ale ten už si hlídá `/breakdown`.

**Zadání pro plán je `docs/architecture.md`**, ne `requirements.md`. Plán argumentuje z návrhu řešení; požadavky jdou jako doplňkový kontext, aby bylo vidět, proč se to staví. O předání se stará `/breakdown`.

## Zásady pro celý průběh

- **Ptej se postupně a přes tool `AskUserQuestion`** – postup, tvar otázky i mechanika toolu viz `~/.claude/RULES.md`, *Ptej se postupně, ne všechno najednou*.
- **Nic si nevymýšlej** – technický název, ID, parametr, cizí API, cena. Viz `~/.claude/RULES.md`, *Při nejistotě se zeptej*.
- **Zapisuj průběžně** – ve chvíli, kdy rozhodnutí padne, ne až na konci. Viz `~/.claude/RULES.md`, *Pravda v souborech, ne v konverzaci*; kam co patří, definuje `structure.md`.
- **Navrhuj kompletně, realizuj postupně** – viz `~/.claude/RULES.md`. Tady to znamená: požadavky i návrh řešení popisují celou věc včetně toho, co bude až později; řeže se až plán, a ten se dělá jen na MVP.
- **YAGNI.** Z každého návrhu vyhoď, co není potřeba – ale zapiš to do *Mimo rozsah*, ať je vidět, že to bylo zvážené a zamítnuté, ne opomenuté.

------

## Zákaz implementace

**Dokud není návrh hotový a schválený, nesmí vzniknout ani řádek produkčního kódu.** Žádný scaffold, žádné `npm create`, žádná databáze, žádné „jen si ověřím, že to jde“.

Výjimka je jediná: **ověřovací sonda**, když na odpovědi stojí rozhodnutí v návrhu („zvládne to hosting?“, „má to API tenhle endpoint?“). Pak řekni dopředu, co zkoušíš a proč, výsledek použij jako podklad a **kód zahoď** – označ ho jako jednorázový a nenechávej ho v projektu.

| Myšlenka | Realita |
|---|---|
| „Zadání je jasné, začnu rovnou“ | Když je jasné, sepsání trvá deset minut. Když ne, právě proto se píše. |
| „Udělám scaffold, ať máme na čem stavět“ | Scaffold zamkne tech stack dřív, než se rozhodl. |
| „Uživatel mi řekl ‚udělej to'“ | Řekl `/specify`. Kdyby chtěl kód, řekl by to. |

------

## Fáze 0 – Pre-flight

1. **Kořen projektu.** Pracovní adresář, případně kořen repozitáře. Ve worktree layoutu (`~/Dev/context/worktree/worktree.md`) je projektem pracovní adresář větve – dokumenty patří do `main/docs/`, ne do kořene kontejneru.
2. **Přečti projektový `CLAUDE.md`** – metadata projektu, typ projektu, paměťová politika, `### Autocommit`, `## Výjimky z obecných pravidel`.
3. **Zkontroluj strukturu.** Existují standardní soubory `todo.md`, `done.md`, `decisions.md`, `rules.md` (v `docs/`, nebo v kořeni podle režimu)? Chybí-li, **nezakládej je potichu** – vypiš, co chybí, a nabídni `/project`. Pokračuj až pak; specifikace bez místa, kam zapisovat rozhodnutí, je poloviční práce.
   **Přečti si i `## Struktura a dokumentace` v `CLAUDE.md`** – jsou-li tam vypsané *Produktové podklady*, projekt se zavázal je vést a ty je máš naplnit (viz Fáze 3a). Chybí-li `docs/competition.md` a `docs/risks.md`, přestože jsou zapsané, **nabídni `/discovery`**: bez konkurence a rizik se píše zadání naslepo.
4. **Existující podklady.** Projdi, co v projektu už je – zadání, brief, zápis ze schůzky, starý systém, exporty, `docs/research/`. **Cizí podklady jsou read-only** – kopírovat si z nich do projektu smíš a máš, zapisovat do nich nikdy.
5. **Urči vstupní bod.** Skill se dá spustit i uprostřed – neběží vždycky celý:

   | Stav | Kde začít |
   |---|---|
   | `requirements.md` ani `architecture.md` neexistují | Fáze 1, celý běh |
   | `requirements.md` existuje, `architecture.md` ne | Zeptej se: **navázat návrhem řešení**, nebo revidovat požadavky? Tohle je běžný případ – produkt se schválí dnes, návrh se dělá jindy. Při navázání **projdi Fázi 2 i tak** – `brainstorming` musíš vyvolat, jinak nemá kdo návrh vytvořit; jen mu místo produktových otázek předej hotové `docs/requirements.md` jako zadání a rovnou jdi na varianty řešení. |
   | Existují oba | Jde o revizi, nebo o novou část projektu? Při revizi **nepřepisuj** – rozšiř a přeformuluj stávající. |
   | `architecture.md` existuje a přidává se feature | Rozšiř ho. **Nezakládej druhý návrhový dokument** – jeden systém, jeden návrh. |

Zjištěné shrň do tří až pěti řádků a pokračuj.

------

## Fáze 1 – Nultý krok: vytěž, co už uživatel má

**Než se na cokoliv zeptáš**, vyzvi ho, ať přiloží nebo nakopíruje všechno, co k tomu má – i nestrukturovaně. Zápis ze schůzky, poznámky, starý dokument, screenshoty, konkurenční web, mail od klienta.

0. **Nejdřív si přečti, co v projektu už je** – zejména `docs/competition.md` a `docs/risks.md` od `/discovery`. Sekce *Co poměřujeme* odpovídá na to, jaký problém řešíme a komu; *Naše pozice a odlišení* říká, co produkt musí umět a čím se liší; rizika říkají, co musí být postavené jinak. **Na nic z toho se neptej znovu** – shrň to a nech potvrdit.
1. **Originály ulož** do projektu (`docs/research/`), ať se dají dohledat.
2. **Sám si z nich zodpověz co nejvíc.** Cokoliv, co z podkladů plyne, se už neptej.
3. **Vypiš souhrn, co sis z toho odvodil**, ať to uživatel jedním pohledem potvrdí nebo opraví.
4. **Doptávej se jen na zbytek** – a na věci, kde si nejsi jistý.

Nemá-li nic, přeskoč. Ale zeptej se – v praxi něco má skoro vždycky a nenapadne ho to poslat.

------

## Fáze 2 – Klasifikace a dialog

**Vyvolej `superpowers:brainstorming`.** Předej mu:

- co ses dozvěděl z podkladů ve Fázi 1,
- že se má ptát přes `AskUserQuestion`, jednu otázku na volání,
- že **návrhovou část zapíše do `docs/architecture.md`**, ne do `docs/superpowers/specs/`, a až ve Fázi 3b – tedy po schválení produktové části.

**Co udělat s klasifikací:**

| Cesta | Co dělat |
|---|---|
| **Architectural** | Normální běh skillu. Tohle je jeho případ. |
| **Bounded** | Specifikace nedává smysl – je to změna v existujícím kódu. **Řekni to a zastav se.** Nabídni pokračovat rovnou přes `brainstorming` (krátký návrh v chatu → schválení → implementace). Nenech se zatlačit do psaní specifikace na jednosouborovou změnu. |
| **Spike** | Totéž – výstupem je odpověď, ne dokument. Zastav se a nabídni sondu. |

**Rozsah.** Popisuje-li zadání víc nezávislých podsystémů, řekni to hned a rozlož to na dílčí projekty dřív, než se začnou ladit detaily. Každý dílčí projekt pak dostane vlastní dokumenty i vlastní plán.

**Projekt bez kódu.** Je-li to znalostní, obsahový nebo obchodní projekt (kurz, brand, pozicování, evidence), `requirements.md` dává smysl, ale **návrh řešení ani `writing-plans` ne** – ty předpokládají kód, testy a commity. Skonči po Fázi 3a a místo plánu nabídni postupný rozpis kroků do `docs/todo.md`.

------

## Fáze 3a – Produktová specifikace

Zapiš do **`docs/requirements.md`**. Sekci, která pro projekt nedává smysl, vynech, ale **řekni, že jsi ji vynechal a proč**:

```markdown
# <Lidský název> – produktová specifikace

<Jedna věta, co to je. Shodná s popiskem v CLAUDE.md.>

## Proč to děláme
Jaký problém to řeší, čí, a co se stane, když to neuděláme.

## Pro koho to je
Persony. U každé: kdo to je, co od toho čeká, čeho se bojí, co ji odradí.
Sekundární persony odděl a řekni, čím jsou omezené.

## Co to je
Popis produktu ze strany uživatele.

## Hlavní scénáře
Co člověk s produktem reálně dělá, od začátku do konce. Čitelně, jako příběh.
Hlavní scénáře nahoře, okrajové pod čarou – ale popsané.
**Vede-li projekt `scenarios.md`, tahle sekce zaniká** a nahradí ji odkaz na něj.

## User stories
Jako <persona> chci <co>, abych <proč>. Seskupené podle oblastí.

## Varianty a rozhodovací větve
Kde má scénář víc podob, vypiš je taxativně a řekni, čím se mezi nimi volí.
Tohle je nejčastější místo, kde se zadání později rozpadne.

## Omezení
Co návrh nesmí porušit: rozpočet, provozní prostředí, závislosti, které
nejsou přípustné, jazyky, legislativa, termín. Omezení, ne volby řešení.

## Nefunkční požadavky
Výkon, dostupnost, bezpečnost, osobní údaje a GDPR, přístupnost,
lokalizace, provoz a zálohy. Jen to, co má reálné důsledky.

## MVP
Zaškrtávací seznam toho, co musí být v první verzi. Řež agresivně.
Každá položka je ověřitelná – ne „hotová registrace“, ale co konkrétně umí.

## Mimo rozsah
Co vědomě neděláme a proč. Musí být neprázdné.
Sem patří i to, co bylo v návrhu a vyhodilo se – ať to nikdo nevymyslí znovu.

## Jak poznáme, že to funguje
Success metrics. Konkrétní, měřitelné, s cílovou hodnotou a termínem.

## Otevřené otázky
Co ještě není rozhodnuté a co to blokuje.
```

**Jak psát:** česky, věcně, bez omáčky, typografie podle `~/Dev/context/text/text.md`. Konkrétně – „rychlé načítání“ je nic, „LCP pod 2,5 s na 4G“ je požadavek. Bez placeholderů; co nevíš, patří do *Otevřených otázek* s tím, kdo to má rozhodnout.

### Produktové podklady

Vede-li projekt některý z nich (`## Struktura a dokumentace` v `CLAUDE.md`, viz Fáze 0), **sepiš ho v tomhle kroku spolu s požadavky** – všechny tři jsou produktové, ne technické, a vznikají z téhož dialogu. Definici drží `~/Dev/context/structure/structure.md`, *Produktové podklady*.

**`docs/scenarios.md`** – taxativní seznam toho, co uživatel s produktem dělá. Každý scénář krok za krokem od začátku do konce, včetně okrajových a chybových cest:

```markdown
## <Číslo a jméno scénáře>

**Kdo:** <persona z requirements.md>
**Kdy a proč:** <spouštěč – co se stalo, že to člověk dělá>
**Předpoklady:** <co musí platit, aby mohl začít>

1. <krok – co udělá uživatel>
2. <krok – co na to systém>
...

**Konec:** <jak pozná, že je hotovo>
**Kde to může selhat:** <odbočky a chybové cesty, každá s tím, co se stane>
```

**Píše se pro tři čtenáře, které `requirements.md` neobsluhuje:** toho, kdo ověřuje, že produkt umí, co má; toho, kdo z toho píše nápovědu a FAQ; a testování na skutečných lidech po dokončení. Proto je to postup, ne příběh – a proto se nešetří okrajovými cestami.

**Zaniká tím sekce *Hlavní scénáře* v `requirements.md`** a nahradí ji odkaz. Dva seznamy scénářů se rozejdou při první změně rozsahu (`~/.claude/RULES.md`, *Single source of truth*). V požadavcích zůstává **proč a pro koho**, ve scénářích **jak to člověk provede**.

**`docs/glossary.md`** – u každého pojmu: jak se jmenuje česky, jak v kódu, co znamená a **čím se liší od pojmu, se kterým se plete**. To poslední je hlavní obsah; slovník bez rozlišení blízkých pojmů nic neřeší. Zakládá se tady, ale **rozšiřuje se ve Fázi 3b** při datovém modelu – entita, která v návrhu dostane jméno, ho má mít i tady.

**`docs/pricing.md`** – ne ceník pro web, ale **soupis toho, co z cenového modelu plyne pro produkt**: co který tarif smí, kde jsou limity a co se stane při jejich dosažení, jak vypadá trial a co po něm, jak se přechází nahoru a dolů, co se stane po expiraci a co s daty. Každá z těch vět je funkce, kterou pak někdo musí naprogramovat, takže **každá patří i do *MVP* nebo do *Mimo rozsah***.

**Nevede-li projekt žádný z nich, nic nezakládej** a jdi rovnou na bránu. Zdá-li se ti přitom, že by se některý hodil, řekni to jednou větou a nech rozhodnout – závazek vede `CLAUDE.md`, ne tenhle běh.

**Brána uživatele.** Po sebe-revizi (Fáze 4) napiš:

> Požadavky jsou sepsané a commitnuté v `docs/requirements.md`. Přečti si ho prosím a řekni, jestli chceš něco změnit, než se pustíme do návrhu řešení.

**Počkej na odpověď.** Bez výslovného souhlasu nepokračuj na 3b – návrh postavený na neschváleném zadání se zahazuje celý.

------

## Fáze 3b – Návrh řešení

**Na návrhu se nešetří: nejsilnější model, `xhigh`.** Volba modelu a effortu podle `~/.claude/RULES.md`, *Model a effort podle úkolu*. Tohle není výroba dokumentu – dokument je jen zápis. Je to rozhodnutí, které se propíše do každého úkolu plánu a do každého řádku kódu pod ním, a **špatný návrh se dobrou implementací nezachrání**: špatná věc se jen udělá pořádně. Zápis hotového rozhodnutí do šablony už chytrý být nemusí.


**Píše se, když platí aspoň jedno:**

- je to nový projekt nebo nový podsystém,
- zavádí nebo mění datový model či perzistentní stav,
- zavádí rozhraní, na kterém stojí něco dalšího (API, formát, kontrakt),
- napojuje se na cizí systém (platební brána, fakturace, externí API),
- má stavový prostor s přechody,
- existuje víc než jedna rozumná cesta, jak to postavit.

**Nepíše se, když** je to přírůstek uvnitř už navrženého systému – pak rozšiř stávající `architecture.md`. A **nikdy** u projektu bez kódu.

Přeskočíš-li ho, **řekni to i s důvodem** a jako zadání pro plán použij `requirements.md`.

Návrh vytvoří `brainstorming` v dialogu s uživatelem – po sekcích, se schválením po každé. **Jak psát platí stejně jako u `requirements.md`** (viz výš): česky, věcně, bez omáčky, typografie podle `~/Dev/context/text/text.md`, bez placeholderů. Zapiš do **`docs/architecture.md`**:

```markdown
# <Lidský název> – návrh řešení

Vychází z [produktové specifikace](requirements.md). Co a proč se staví, je tam;
tady je, jak.

## Zvolený přístup
Jaké varianty byly ve hře, která vyhrála a proč. Zamítnuté i s důvodem.

## Architektura
Komponenty, jejich odpovědnosti a hranice. U každé: co dělá, jak se
používá, na čem závisí.

## Datový model
Entity, vztahy, klíčová pole. U netriviálních i důvod, proč zrovna takhle.

## Stavy a přechody
Je-li tam stavový prostor: taxativně stavy, přechody mezi nimi, podmínky
a co se v každém přechodu děje. Vše o jednom přechodu pohromadě u něj.

## Datové toky
Co odkud kam teče, kdo to iniciuje a co se stane, když to selže.

## Rozhraní
Veřejné API, formáty, kontrakty vůči okolí. Přesné názvy a typy.

## Cizí systémy
Na co se to napojuje, co od toho očekáváme a co dělat, když to nefunguje.

## Chybové stavy
Co může selhat, jak se to pozná a co se stane pak.

## Bezpečnostní model
Kde se autorizuje a proč to nejde obejít. Jak se validuje vstup a na které
hranici. Kde žijí tajemství. Co se loguje a co se logovat nesmí.
Na konci **jmenný seznam citlivých oblastí** – přihlášení, oprávnění, platby,
nahrávání souborů, osobní údaje, mazání dat, odesílání pošty ven. Změna v nich
se nemerguje bez lidského pohledu na diff; `/review` na ně sahá přísněji.

## Technologie
Konkrétní volba a proč – proti omezením z requirements.md.

## Testovací strategie
Co se testuje a na jaké úrovni. U každého scénáře a *Varianty* řekni, čím bude
pokrytý – akceptačním testem, jednotkovým, nebo vědomě ničím a proč.
Scénáře ber z `scenarios.md`, vede-li ho projekt; jinak ze sekce *Hlavní
scénáře* v requirements.md.
Dál prahy, které bude projekt držet (pokrytí, mutation score) a čím se měří.
Výchozí hodnoty a nástroje viz `~/Dev/context/coding/coding.md`,
*Ověřování a brány kvality*.
Zvlášť rozhodni o **generativních testech** – fuzzingu a property-based testech.
Vyplatí se u parserů, validace vstupu, převodů formátů, výpočtů nad rozsahy
a stavových automatů: najdou vstup, na který nikdo nepomyslel, a stojí tokeny
jen jednou. Napiš, kde je projekt bude mít, nebo že je mít nebude a proč –
prázdné místo tady znamená, že se nenapíšou nikdy.

## Ověřování a brány
Konkrétní příkazy, které projekt bude mít – `test`, `typecheck`, `lint`,
`build`, `audit`, případně `e2e` a `mutation`.
Je to **záměr, ne kontrakt**: *Kontrakt příkazů* v `CLAUDE.md` musí odpovídat
tomu, co projekt opravdu umí spustit, takže ho zapisuje až ten, kdo to vidí –
první úkol plánu, který příkazy zavede, případně opakovaný běh `/project`.
Řekni i, co se **nebude** kontrolovat automaticky a proč.

## Rizika
Co je na tom nejistého a co by to znamenalo, kdyby se ukázalo jinak.
```

**Kontrola proti požadavkům:** projdi scénáře (ze `scenarios.md`, nebo ze sekce *Hlavní scénáře*), *Varianty* a *Nefunkční požadavky* a u každého ukaž, co v návrhu ho pokrývá. Nepokryté je nález, ne detail. Vede-li projekt `risks.md`, projdi i **mitigace**: riziko s vyplněným *Promítnutím do produktu* musí mít v návrhu protějšek, jinak se mitigace nestala.

**Bezpečnost se navrhuje, neaudituje.** Zhruba polovina kódu psaného modely obsahuje bezpečnostní chybu a je to předvídatelná množina. Nejúčinnější obrana není kontrola na konci, ale struktura, ve které díra nejde udělat – jedna vrstva autorizace, kterou nelze obejít, výhradně parametrizované dotazy, validace na hranici, tajemství jen z prostředí. Proto má návrh sekci *Bezpečnostní model*, a proto v ní nesmí stát „ošetříme to při implementaci“.

**Doménové standardy.** Návrh se řídí tím, co si projekt importuje v `CLAUDE.md` – `~/Dev/context/coding/coding.md` vždy, dál podle povahy `web/web.md`, `web/admin.md`, `analytics/analytics.md`. Načti je, než začneš navrhovat, ne až při kontrole.

------

## Fáze 4 – Sebe-revize a oponentura

Běží **po každém z obou dokumentů zvlášť**, ne až na konci.

**Sebe-revize** (rozšíření *Spec Self-Review* z brainstormingu):

1. **Placeholdery** – „TBD“, „TODO“, nedokončené sekce, vágní požadavky. Oprav.
2. **Vnitřní rozpory** – neodporují si sekce? Sedí počty a výčty s obsahem?
3. **Vymyšlené věci** – je tam technický název, ID, parametr nebo číslo, které jsi neměl od uživatele ani z podkladů? To je nález. Dohledej, nebo přesuň do *Otevřených otázek*.
4. **Prosakování hranice** – je v `requirements.md` architektura nebo volba technologie? Je v `architecture.md` zdůvodnění produktu? Přesuň.
5. **Pokrytí** – u návrhu proti požadavkům (viz 3b), u požadavků proti tomu, co padlo v dialogu.
6. **Dvojznačnost** – dá se něco přečíst dvěma způsoby? Vyber jeden a napiš ho jednoznačně.
7. **Rozsah** – vejde se to do jednoho implementačního plánu? Pokud ne, dekomponuj.
8. **Mimo rozsah není prázdné** (jen `requirements.md`) – prázdná sekce znamená, že se neřezalo.
9. **Produktové podklady** – vede-li je projekt: nezůstal v `requirements.md` druhý seznam scénářů vedle `scenarios.md`? Má každý scénář popsanou aspoň jednu cestu, kde může selhat? Rozlišuje glosář pojmy, které se pletou, nebo je to jen výčet? Je každý limit z `pricing.md` v *MVP*, nebo v *Mimo rozsah*?

**Oponentura.** Dokument jsi psal ty a jsi na něj zaujatý. `/oponent` je **krok životního cyklu**, ne nabídka: pusť ho, nebo nahlas řekni, proč se u téhle změny přeskakuje. Nabízej ho pro každý dokument zvlášť (`/oponent docs/requirements.md`, `/oponent docs/architecture.md`), protože panel úhlů se pro požadavky a pro návrh řešení liší.

**Úhly nevypisuj** – sestaví si je sám podle sloupce *Spouštěč* ve svém katalogu (`~/.claude/skills/oponent/SKILL.md`, *Fáze 1*) a nechá si je od uživatele potvrdit. Výčet zopakovaný tady by se s katalogem rozešel při první jeho změně (`~/.claude/RULES.md`, *Single source of truth*).

**Brána uživatele** – po požadavcích (viz 3a) i po návrhu řešení:

> Návrh řešení je sepsaný a commitnutý v `docs/architecture.md`. Přečti si ho prosím a řekni, jestli chceš něco změnit, než z něj uděláme implementační plán.

Počkej na odpověď. Chce-li změny, proveď je a projdi sebe-revizi znovu.

------

## Fáze 5 – Předání do plánu

Po schválení návrhu předej řízení na **`/breakdown`**, který ze zadání udělá `docs/plan.md`. Ten si sám najde zadání i kontext a ohlídá rozsah – nemusíš mu nic předávat ručně, jen ho vyvolej.

**Sám plán nepiš.** Ani „ať se to nemusí volat zvlášť“. Rozpad na úkoly má vlastní pravidla, vlastní kontrolu pokrytí MVP a vlastní schvalovací bránu.

**U projektu bez kódu** `/breakdown` nevyvolávej – rozepiš kroky do `docs/todo.md`.

Celý řetěz i s tím, co následuje po realizaci, je v `~/.claude/RULES.md`, *Životní cyklus projektu*.

------

## Když se zadání změní později

Platí *Doc-first vývoj* z `~/.claude/RULES.md`; posloupnost souborů definuje `structure.md`:

1. Změní se požadavek → uprav **`requirements.md`** a s ním **`scenarios.md`**, vede-li ho projekt. Změněný požadavek skoro vždycky mění nějaký scénář; scénář, který zůstal, ale už nejde provést, je horší než chybějící.
2. Zkontroluj, jestli to mění návrh → uprav **`architecture.md`**.
3. Zkontroluj, jestli to mění nehotové úkoly → uprav **`plan.md`**.
4. Rozhodnutí a důvod změny zapiš do `docs/decisions.md`. Původní záznam nepřepisuj – přibude revize.

Přijde-li změna zdola (při implementaci se ukáže, že návrh nejde), **neopravuj to potichu v kódu**. Vrať se do návrhu řešení, uprav ho, a je-li dotčený i produktový záměr, řekni to a nech rozhodnout uživatele.

------

## Závěr

```
## Zadání hotové

**Dokumenty**
- docs/requirements.md – <počet> sekcí
- docs/architecture.md – <počet> sekcí   (nebo „přeskočeno: <důvod>“)
- docs/scenarios.md – <počet> scénářů    (jen vede-li je projekt)
- docs/glossary.md – <počet> pojmů       (jen vede-li je projekt)
- docs/pricing.md – <počet> tarifů       (jen vede-li je projekt)

**Zapsáno mimo ně**
- docs/decisions.md: N rozhodnutí
- docs/todo.md: N odložených položek
- docs/rules.md: N principů

**Otevřené otázky**
- [seznam, nebo „žádné“]

**Další krok**
- [/breakdown / u projektu bez kódu rozpis kroků do docs/todo.md]
```

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Zadání je hotové a schválené, můžeme na implementační plán.`
- `Zadání hotové není – brání tomu: <konkrétní seznam>.`
