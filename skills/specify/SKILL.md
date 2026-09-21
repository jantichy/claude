---
name: specify
description: Skill se použije, když uživatel zadá "/specify" (volitelně s tématem), nebo chce z nápadu udělat zadání – produktovou specifikaci nového projektu, aplikace, webu nebo větší feature, ještě než se začne programovat. Vede řízený rozhovor otázku po otázce a sepíše docs/requirements.md, u projektu, který je vede, k tomu scénáře, glosář a ceník. Nejdřív vytěží podklady, které uživatel už má, a pozná, kdy se specifikace psát nemá, protože jde o změnu v existujícím kódu. Na rozdíl od /architect, který rozhoduje, jak se to postaví, tenhle skill popisuje, co se staví a proč – omezení patří sem, volba do návrhu. Nic neprogramuje, návrh řešení ani implementační plán nepíše a navazující kroky jen doporučuje.
argument-hint: [téma]
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion, Skill]
---

# Specify

## Co skill dělá

Uživatel má nápad a chce z něj zadání, podle kterého se dá rozhodovat. Skill ho provede řízeným rozhovorem a sepíše **`docs/requirements.md`** – dokument, který odpovídá na otázku *co stavíme a proč*, a čte ho zadavatel, produkt, obchod i ten, kdo se k tomu za půl roku vrátí.

**Vede-li projekt produktové podklady**, sepíše v témže kroku i `scenarios.md`, `glossary.md` a `pricing.md`. Jsou produktové, ne technické, a vznikají z téhož dialogu; zbylé tři podklady, `demand.md`, `competition.md` a `risks.md`, píše `/discovery`.

V *Životním cyklu projektu* (`~/.claude/RULES.md`) je to třetí krok osy: navazuje na `/discovery` a předává na `/architect`.

**Je to jeden běh a nemá režimy.** Požadavky se sepíšou jednou na začátku; dělení na tematická kola patří návrhu řešení, protože tam se rozhoduje po tématech. Kolo o platební bráně řeší osy, guardy i přechody naráz a rozdělit ho na produktovou a technickou polovinu by znamenalo dvakrát načítat týž kontext.

## Co skill nedělá

- **Nerozhoduje, jak se to postaví.** Architektura, datový model, stavy a přechody, rozhraní, technologie a bezpečnostní model jsou `/architect` a jeho `docs/architecture.md`. **Hranice je tvrdá:** do požadavků patří **omezení**, do návrhu **volba** (`~/.claude/STRUCTURE.md`, *`requirements.md`, `architecture.md`, `plan.md`*). „Musí to běžet na běžném sdíleném hostingu bez placených závislostí“ je omezení a patří sem; „použijeme SQLite, protože…“ je volba a patří do návrhu. Když si nejsi jistý, kam věta patří, ptej se: *změní se, když se změní technologie?* Ano → návrh. Ne → sem.
- **Nezkoumá konkurenci ani trh a neptá se, jestli to někdo chce.** Kdo to už dělá, za kolik, co je na tom rizikové a čím je doložená poptávka, zjišťuje `/discovery` do `docs/demand.md`, `docs/competition.md` a `docs/risks.md`. Tenhle skill je čte jako hotový vstup – zejména sekce *Co poměřujeme* a *Verdikt*, na které se tedy neptá podruhé. **Dorazí-li zadání s nedoloženou poptávkou, není to důvod se zastavit**, ale patří to do `requirements.md` k rozsahu MVP: první verze má být co nejmenší, aby poptávku ověřila.
- **Nezakládá projekt.** Strukturu, git, autocommit a doménové importy dělá `/project`. Když chybí, skill na to upozorní a nabídne ho.
- **Nepíše implementační plán.** Ten dělá `/breakdown`, a to až z hotového návrhu řešení, ne z požadavků.
- **Nic neprogramuje.** Ani scaffold, ani „jen rychle rozjedu projekt“. Tvrdá kontrola – viz *Zákaz implementace*.
- **Neduplikuje `superpowers:brainstorming`.** Klasifikaci rozsahu i doptávání řídí ten skill.
- **Nevolá další kroky, jen je doporučuje.** `/oponent`, `/review`, `/cleanup` i `/architect` jsou samostatné kroky; kdyby je skill pouštěl sám, staly by se jeho součástí. V závěru řekne, co a v jakém pořadí pustit.

## Jak je to postavené uvnitř

**Dialog a klasifikaci rozsahu dělá `superpowers:brainstorming`, a to je implementační detail, ne rozhraní.** Kdyby ho nahradil jiný nástroj nebo vlastní postup, nikdo se to nemusí dozvědět. **Závazné je to, co po skillu zbude:** `docs/requirements.md` a produktové podklady na místech podle `~/.claude/STRUCTURE.md`, česky a bez datumových prefixů.

| Krok | Kdo ho dělá |
|---|---|
| Klasifikace rozsahu (spike / bounded / architectural) | `superpowers:brainstorming` |
| Doptávání a schvalovací kontroly v dialogu | `superpowers:brainstorming` |
| **Produktový rámec a sepsání požadavků** | **tenhle skill** |
| **Scénáře, glosář a ceník** | **tenhle skill** |
| Návrh řešení | `/architect` |
| Implementační plán | `/breakdown` |

**Přepis výchozí cesty.** `brainstorming` ukládá svůj výstup do `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`. Explicitně přitom respektuje uživatelovu preferenci a ta zní jinak – podle `~/.claude/STRUCTURE.md` jsou v `docs/` jednoslovné anglické názvy bez datumových prefixů. **Řekni mu to výslovně**, když ho vyvoláváš, jinak si založí vlastní adresářový strom vedle toho tvého. A řekni mu taky, že **návrhovou část v tomhle běhu nepíše vůbec** – ta patří `/architect`.

## Zásady pro celý průběh

- **Ptej se postupně a přes tool `AskUserQuestion`** – postup, tvar otázky i mechanika toolu viz `~/.claude/RULES.md`, *Ptej se postupně, ne všechno najednou*.
- **Nic si nevymýšlej** – technický název, ID, parametr, cizí API, cena. Viz `~/.claude/RULES.md`, *Při nejistotě se zeptej*.
- **Zapisuj průběžně** – ve chvíli, kdy rozhodnutí padne, ne až na konci. Viz `~/.claude/RULES.md`, *Pravda v souborech, ne v konverzaci*; kam co patří, definuje `STRUCTURE.md`.
- **Navrhuj kompletně, implementuj postupně** – viz `~/.claude/RULES.md`. Tady to znamená: požadavky popisují celou věc včetně toho, co bude až později; řeže se až plán, a ten se dělá jen na MVP.
- **YAGNI.** Z každého záměru vyhoď, co není potřeba – ale zapiš to do *Mimo rozsah*, ať je vidět, že to bylo zvážené a zamítnuté, ne opomenuté.

------

## Zákaz implementace

**Dokud není zadání hotové a schválené, nesmí vzniknout ani řádek produkčního kódu.** Žádný scaffold, žádné `npm create`, žádná databáze, žádné „jen si ověřím, že to jde“.

Výjimka je jediná: **ověřovací pokus**, když na odpovědi stojí rozhodnutí v zadání („zvládne to hosting?“, „má to API tenhle endpoint?“). Pak řekni dopředu, co zkoušíš a proč, výsledek použij jako podklad a **kód zahoď** – označ ho jako jednorázový a nenechávej ho v projektu.

| Myšlenka | Realita |
|---|---|
| „Zadání je jasné, začnu rovnou“ | Když je jasné, sepsání trvá deset minut. Když ne, právě proto se píše. |
| „Udělám scaffold, ať máme na čem stavět“ | Scaffold zamkne tech stack dřív, než se rozhodl. |
| „Uživatel mi řekl ‚udělej to‘“ | Řekl `/specify`. Kdyby chtěl kód, řekl by to. |

------

## Fáze 0 – Příprava

**Společný začátek drží `~/.claude/skills/PREFLIGHT.md`** – načti si ho a řiď se jím. Body 4 a 5 odpadají: tenhle skill nesahá na kód a pracuje nad nápadem, ne nad diffem větve.

Navíc si zjisti tohle:

1. **Zkontroluj strukturu.** Existují standardní soubory `todo.md`, `backlog.md`, `done.md`, `decisions.md`, `rules.md` (v `docs/`, nebo v kořeni podle režimu)? Chybí-li, **nezakládej je potichu** – vypiš, co chybí, a nabídni `/project`. Pokračuj až pak; specifikace bez místa, kam zapisovat rozhodnutí, je poloviční práce. **Chybějící `backlog.md` sám o sobě neblokuje** – není kam zapisovat, ale je co číst; zmiň ho ve výpisu a pokračuj (*Fáze 1*, bod 5 s tím počítá).

   **Přečti si i `## Struktura a dokumentace` v `CLAUDE.md`** – jsou-li tam vypsané *Produktové podklady*, projekt se zavázal je vést. **Tenhle skill z nich píše tři** – `scenarios.md`, `glossary.md` a `pricing.md`; `demand.md`, `competition.md` a `risks.md` patří `/discovery`. Chybí-li ty tři, přestože jsou zapsané, **nabídni `/discovery`**: bez poptávky, konkurence a rizik se píše zadání naslepo.
2. **Existující podklady.** Projdi, co v projektu už je – zadání, brief, zápis ze schůzky, starý systém, exporty, `docs/research/`. **Cizí podklady jsou read-only** – kopírovat si z nich do projektu smíš a máš, zapisovat do nich nikdy.
3. **Urči vstupní bod.** Skill se dá spustit i uprostřed – neběží vždycky celý:

   | Stav | Kde začít |
   |---|---|
   | `requirements.md` neexistuje | *Fáze 1*, celý běh |
   | `requirements.md` existuje a přidává se feature | Rozšiř ho. **Nezakládej druhý dokument požadavků** – jeden produkt, jedno zadání. |
   | `requirements.md` existuje a jde o revizi | **Nepřepisuj** – rozšiř a přeformuluj stávající. |
   | `requirements.md` existuje a uživatel chce návrh řešení | Sem nepatří. Řekni to a nabídni `/architect`. |

4. **Větev.** Běží-li projekt ve worktree layoutu a session stojí v `main/` nebo ve větvi, která se zadáním nesouvisí, nabídni založení větve `docs/specify` podle `~/.claude/WORKTREE.md`, *Založení větve*, **dřív, než cokoliv zapíšeš**. Existuje-li větev toho jména z dřívějška, přidej příponu `-2`. Zakládej ji až po bodu 3, ať nevznikne zbytečně.

------

## Fáze 1 – Nultý krok: vytěž, co už uživatel má

**Než se na cokoliv zeptáš**, vyzvi ho, ať přiloží nebo nakopíruje všechno, co k tomu má – i nestrukturovaně. Zápis ze schůzky, poznámky, starý dokument, screenshoty, konkurenční web, mail od klienta.

0. **Nejdřív si přečti, co v projektu už je** – zejména `docs/demand.md`, `docs/competition.md` a `docs/risks.md` od `/discovery`, a `docs/backlog.md` a `docs/todo.md` (viz bod 5). `demand.md` odpovídá na to, proč to stavíme a čím je to doložené; sekce *Co poměřujeme* na to, jaký problém řešíme a komu; *Naše pozice a odlišení* říká, co produkt musí umět a čím se liší; rizika říkají, co musí být postavené jinak. **Na nic z toho se neptej znovu** – shrň to a nech potvrdit.
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

- co ses dozvěděl z podkladů v *Fázi 1*,
- že se má ptát přes `AskUserQuestion`, jednu otázku na volání,
- že **návrhovou část nepíše vůbec** – ta patří `/architect`, a to až po schválení požadavků.

**Co udělat s klasifikací:**

| Cesta | Co dělat |
|---|---|
| **Architectural** | Normální běh skillu. Tohle je jeho případ. |
| **Bounded** | Specifikace nedává smysl – je to změna v existujícím kódu. **Řekni to a zastav se.** Nabídni pokračovat rovnou přes `brainstorming` (krátký návrh v chatu → schválení → implementace). Nenech se zatlačit do psaní specifikace na jednosouborovou změnu. |
| **Spike** | Totéž – výstupem je odpověď, ne dokument. Zastav se a nabídni ověřovací pokus. |

**Rozsah.** Popisuje-li zadání víc nezávislých podsystémů, řekni to hned a rozlož to na dílčí projekty dřív, než se začnou ladit detaily. Každý dílčí projekt pak dostane vlastní dokumenty i vlastní plán.

------

## Fáze 3 – Produktová specifikace

Zapiš do **`docs/requirements.md`**. Šablona je v `~/.claude/skills/specify/documents.md`, `docs/requirements.md`; pravidla psaní tamtéž v sekci *Jak se píše*. **Přečti si ten soubor celý, než začneš psát** – platí pro požadavky i pro produktové podklady.

### Scénáře, glosář a ceník

Tři z *Produktových podkladů*, které projekt vede volitelně (`## Struktura a dokumentace` v `CLAUDE.md`, viz *Fáze 0*). Vede-li projekt některý z téhle trojice, **sepiš ho v tomhle kroku spolu s požadavky**: všechny tři jsou produktové, ne technické, a vznikají z téhož dialogu. Šablony a pravidla drží `~/.claude/skills/specify/documents.md`; definici toho, co který dokument je, `~/.claude/STRUCTURE.md`, *Produktové podklady*.

**Nevede-li projekt žádný z nich, nic nezakládej** a jdi rovnou na kontrolu. Zdá-li se ti přitom, že by se některý hodil, řekni to jednou větou a nech rozhodnout – závazek vede `CLAUDE.md`, ne tenhle běh.

**Glosář se ještě rozroste.** Entita, která dostane jméno až v návrhu řešení, do něj přibude v `/architect` – tady se zakládá, neuzavírá.

------

## Fáze 4 – Sebe-revize a oponentura

Běží **po každém dokumentu zvlášť**, ne až na konci.

**Sebe-revize** (rozšíření *Spec Self-Review* z brainstormingu):

1. **Placeholdery** – „TBD“, „TODO“, nedokončené sekce, vágní požadavky. Oprav.
2. **Vnitřní rozpory** – neodporují si sekce? Sedí počty a výčty s obsahem?
3. **Vymyšlené věci** – je tam technický název, ID, parametr nebo číslo, které jsi neměl od uživatele ani z podkladů? To je nález. Dohledej, nebo přesuň do *Otevřených otázek*.
4. **Prosakování hranice** – je v `requirements.md` architektura nebo volba technologie? Ani „nejspíš to bude na Vercelu“. Přesuň to do *Otevřených otázek*, nebo zahoď – jakmile to tam zůstane, začne se to rozcházet s návrhem.
5. **Pokrytí** – proti tomu, co padlo v dialogu.
6. **Dvojznačnost** – dá se něco přečíst dvěma způsoby? Vyber jeden a napiš ho jednoznačně.
7. **Rozsah** – vejde se to do jednoho implementačního plánu? Pokud ne, dekomponuj.
8. **Mimo rozsah není prázdné** – prázdná sekce znamená, že se neřezalo.
9. **Scénáře, glosář a ceník** – vede-li je projekt: nezůstal v `requirements.md` druhý seznam scénářů vedle `scenarios.md`? Má každý scénář popsanou aspoň jednu cestu, kde může selhat? Rozlišuje glosář pojmy, které se pletou, nebo je to jen výčet? Je každý limit z `pricing.md` v *MVP*, nebo v *Mimo rozsah*?

**Oponentura.** Dokument jsi psal ty a jsi na něj zaujatý. `/oponent` je **krok životního cyklu**, ne nabídka: pusť ho, nebo nahlas řekni, proč se u téhle změny přeskakuje.

**Hlediska nevypisuj** – sestaví si je sám podle sloupce *Spouštěč* ve svém katalogu (`~/.claude/skills/oponent/SKILL.md`, *Volba hledisek*) a nechá si je od uživatele potvrdit. Výčet zopakovaný tady by se s katalogem rozešel při první jeho změně (`~/.claude/RULES.md`, *Single source of truth*).

**Kontrola uživatele:**

> Požadavky jsou sepsané a commitnuté v `docs/requirements.md`. Přečti si je prosím a řekni, jestli chceš něco změnit, než se pustíme do návrhu řešení.

**Počkej na odpověď.** Bez výslovného souhlasu nedoporučuj další krok – návrh postavený na neschváleném zadání se zahazuje celý.

------

## Fáze 5 – Předání do návrhu

Po schválení požadavků **doporuč `/architect`**, který z nich udělá návrh řešení – sám ho nevolej (*Co skill nedělá*). Ten si sám najde zadání i kontext, rozhodne, jestli se záměr povede jedním zátahem nebo po tematických kolech, a ohlídá rozsah, takže mu nic předávat nemusíš.

**Sám návrh nepiš.** Ani „ať se to nemusí volat zvlášť“. Rozhodování o řešení má vlastní pravidla, vlastní kontrolu proti scénářům a rizikům a vlastní schvalovací kontrolu.

**U projektu bez kódu** `/architect` ani `/breakdown` nedoporučuj – je-li to znalostní, obsahový nebo obchodní projekt (kurz, brand, pozicování, evidence), `requirements.md` dává smysl, ale návrh řešení a plán předpokládají kód, testy a commity. Rozepiš místo nich kroky do `docs/todo.md`.

Celý řetěz i s tím, co následuje po implementaci, je v `~/.claude/skills/LIFECYCLE.md`.

------

## Když se zadání změní později

Platí *Doc-first vývoj* z `~/.claude/RULES.md`; posloupnost souborů definuje `STRUCTURE.md`:

1. Změní se požadavek → uprav **`requirements.md`** a s ním **`scenarios.md`**, vede-li ho projekt. Změněný požadavek skoro vždycky mění nějaký scénář; scénář, který zůstal, ale už nejde provést, je horší než chybějící.
2. Zkontroluj, jestli to mění návrh → to je `/architect`.
3. Rozhodnutí a důvod změny zapiš do `docs/decisions.md`. Původní záznam nepřepisuj – přibude revize.

Přijde-li změna zdola (při implementaci se ukáže, že návrh nejde), **neopravuj to potichu v kódu**. Vrať se do návrhu řešení, a je-li dotčený i produktový záměr, teprve pak sem.

------

## Fáze 6 – Závěr

```
## Zadání hotové

**Dokumenty**
- docs/requirements.md – <počet> sekcí
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
- [/oponent docs/requirements.md, /cleanup, pak /architect; u projektu bez kódu rozpis kroků do docs/todo.md]
```

Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo – `~/.claude/RULES.md`, *Styl odpovědí*.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Zadání je hotové a schválené, můžeme na návrh řešení.`
- `Zadání hotové není – brání tomu: <konkrétní seznam>.`
