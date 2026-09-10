---
name: specify
description: Skill se použije, když uživatel zadá "/specify", nebo chce z nápadu udělat zadání – produktovou specifikaci a návrh řešení nového projektu, aplikace, webu nebo větší feature, ještě než se začne programovat. Vede řízený rozhovor otázku po otázce, sepíše docs/requirements.md a docs/architecture.md a předá to do implementačního plánu.
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, Skill]
---

# Specify

## Co skill dělá

Uživatel má nápad a chce z něj zadání, podle kterého se dá stavět. Skill ho provede řízeným rozhovorem a sepíše **dva dokumenty**:

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

V *Životním cyklu projektu* (`~/.claude/RULES.md`) je to třetí krok zakládání: navazuje na `/discovery` a předává na `/oponent`.

## Co skill nedělá

- **Nic neprogramuje.** Ani scaffold, ani „jen rychle rozjedu projekt“. Tvrdá kontrola – viz *Zákaz implementace*.
- **Nezakládá projekt.** Strukturu, git, autocommit a doménové importy dělá `/project`. Když chybí, skill na to upozorní a nabídne ho.
- **Nezkoumá konkurenci ani trh.** Kdo to už dělá, za kolik a co je na tom rizikové, zjišťuje `/discovery` do `docs/competition.md` a `docs/risks.md`. Tenhle skill je čte jako hotový vstup – zejména sekci *Co poměřujeme*, na kterou se tedy neptá podruhé.
- **Nepíše implementační plán.** Ten dělá `/breakdown`. Skill mu jen předá řízení, až je zadání schválené.
- **Neduplikuje `superpowers:brainstorming`.** Dialog, klasifikaci rozsahu i návrh řešení řídí ten skill.

## Vztah k superpowers

| Krok | Kdo ho dělá |
|---|---|
| Klasifikace rozsahu (spike / bounded / architectural) | `superpowers:brainstorming` |
| Doptávání, varianty řešení, návrh, schvalovací kontroly | `superpowers:brainstorming` |
| **Produktový rámec a sepsání požadavků** | **tenhle skill** |
| Sepsání návrhu řešení | `brainstorming` ho vytvoří, tenhle skill mu určí cíl a tvar |
| Implementační plán | `/breakdown` |
| Implementace plánu | `/implement` |

**Přepis výchozí cesty.** `brainstorming` ukládá design doc do `docs/superpowers/specs/YYYY-MM-DD-<téma>-design.md`. Explicitně přitom respektuje uživatelovu preferenci a ta zní jinak – podle `~/.claude/STRUCTURE.md` jsou v `docs/` jednoslovné anglické názvy bez datumových prefixů, takže cíl je **`docs/architecture.md`**.

**Řekni mu to výslovně**, když ho vyvoláváš. Jinak si založí vlastní adresářový strom vedle toho tvého. Totéž platí pro plán, ale ten už si hlídá `/breakdown`.

**Zadání pro plán je `docs/architecture.md`**, ne `requirements.md`. Plán argumentuje z návrhu řešení; požadavky jdou jako doplňkový kontext, aby bylo vidět, proč se to staví. O předání se stará `/breakdown`.

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

1. **Kořen projektu.** Pracovní adresář, případně kořen repozitáře. Ve worktree layoutu (`~/.claude/WORKTREE.md`) je projektem pracovní adresář větve – dokumenty patří do `main/docs/`, ne do kořene kontejneru.
2. **Přečti projektový `CLAUDE.md`** – metadata projektu, typ projektu, paměťová politika, `## Autocommit`, `## Výjimky z obecných pravidel`.
3. **Zkontroluj strukturu.** Existují standardní soubory `todo.md`, `backlog.md`, `done.md`, `decisions.md`, `rules.md` (v `docs/`, nebo v kořeni podle režimu)? Chybí-li, **nezakládej je potichu** – vypiš, co chybí, a nabídni `/project`. Pokračuj až pak; specifikace bez místa, kam zapisovat rozhodnutí, je poloviční práce. **Chybějící `backlog.md` sám o sobě neblokuje** – není kam zapisovat, ale je co psát; zmiň ho ve výpisu a pokračuj (Fáze 1, bod 5 s tím počítá).
   **Přečti si i `## Struktura a dokumentace` v `CLAUDE.md`** – jsou-li tam vypsané *Produktové podklady*, projekt se zavázal je vést. **Tenhle skill z nich píše tři** – `scenarios.md`, `glossary.md` a `pricing.md` (Fáze 3a); `competition.md` a `risks.md` patří `/discovery`. Chybí-li ty dva, přestože jsou zapsané, **nabídni `/discovery`**: bez konkurence a rizik se píše zadání naslepo.
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
- že **návrhovou část zapíše do `docs/architecture.md`**, ne do `docs/superpowers/specs/`, a až ve Fázi 3b – tedy po schválení produktové části.

**Co udělat s klasifikací:**

| Cesta | Co dělat |
|---|---|
| **Architectural** | Normální běh skillu. Tohle je jeho případ. |
| **Bounded** | Specifikace nedává smysl – je to změna v existujícím kódu. **Řekni to a zastav se.** Nabídni pokračovat rovnou přes `brainstorming` (krátký návrh v chatu → schválení → implementace). Nenech se zatlačit do psaní specifikace na jednosouborovou změnu. |
| **Spike** | Totéž – výstupem je odpověď, ne dokument. Zastav se a nabídni ověřovací pokus. |

**Rozsah.** Popisuje-li zadání víc nezávislých podsystémů, řekni to hned a rozlož to na dílčí projekty dřív, než se začnou ladit detaily. Každý dílčí projekt pak dostane vlastní dokumenty i vlastní plán.

**Projekt bez kódu.** Je-li to znalostní, obsahový nebo obchodní projekt (kurz, brand, pozicování, evidence), `requirements.md` dává smysl, ale **návrh řešení ani `writing-plans` ne** – ty předpokládají kód, testy a commity. Skonči po Fázi 3a a místo plánu nabídni postupný rozpis kroků do `docs/todo.md`.

------

## Fáze 3a – Produktová specifikace

Zapiš do **`docs/requirements.md`**. Šablona je v `~/.claude/skills/specify/documents.md`, `docs/requirements.md`; pravidla psaní tamtéž v sekci *Jak se píše*. **Přečti si ten soubor celý, než začneš psát** – platí pro oba dokumenty i pro produktové podklady.


### Scénáře, glosář a ceník

Tři z *Produktových podkladů*, které projekt vede volitelně (`## Struktura a dokumentace` v `CLAUDE.md`, viz Fáze 0) – zbylé dva, `competition.md` a `risks.md`, píše `/discovery`. Vede-li projekt některý z téhle trojice, **sepiš ho v tomhle kroku spolu s požadavky**: všechny tři jsou produktové, ne technické, a vznikají z téhož dialogu. Šablony a pravidla drží `~/.claude/skills/specify/documents.md`; definici toho, co který dokument je, `~/.claude/STRUCTURE.md`, *Produktové podklady*.

**Nevede-li projekt žádný z nich, nic nezakládej** a jdi rovnou na kontrolu. Zdá-li se ti přitom, že by se některý hodil, řekni to jednou větou a nech rozhodnout – závazek vede `CLAUDE.md`, ne tenhle běh.

**Kontrola uživatele.** Po sebe-revizi (Fáze 4) napiš:

> Požadavky jsou sepsané a commitnuté v `docs/requirements.md`. Přečti si ho prosím a řekni, jestli chceš něco změnit, než se pustíme do návrhu řešení.

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

Návrh vytvoří `brainstorming` v dialogu s uživatelem – po sekcích, se schválením po každé. Zapiš do **`docs/architecture.md`**; šablona i pravidla psaní jsou v `~/.claude/skills/specify/documents.md`.

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
9. **Scénáře, glosář a ceník** – vede-li je projekt: nezůstal v `requirements.md` druhý seznam scénářů vedle `scenarios.md`? Má každý scénář popsanou aspoň jednu cestu, kde může selhat? Rozlišuje glosář pojmy, které se pletou, nebo je to jen výčet? Je každý limit z `pricing.md` v *MVP*, nebo v *Mimo rozsah*?

**Oponentura.** Dokument jsi psal ty a jsi na něj zaujatý. `/oponent` je **krok životního cyklu**, ne nabídka: pusť ho, nebo nahlas řekni, proč se u téhle změny přeskakuje. Nabízej ho pro každý dokument zvlášť (`/oponent docs/requirements.md`, `/oponent docs/architecture.md`), protože panel hledisek se pro požadavky a pro návrh řešení liší.

**Hlediska nevypisuj** – sestaví si je sám podle sloupce *Spouštěč* ve svém katalogu (`~/.claude/skills/oponent/SKILL.md`, *Fáze 1*) a nechá si je od uživatele potvrdit. Výčet zopakovaný tady by se s katalogem rozešel při první jeho změně (`~/.claude/RULES.md`, *Single source of truth*).

**Kontrola uživatele** – po požadavcích (viz 3a) i po návrhu řešení:

> Návrh řešení je sepsaný a commitnutý v `docs/architecture.md`. Přečti si ho prosím a řekni, jestli chceš něco změnit, než z něj uděláme implementační plán.

Počkej na odpověď. Chce-li změny, proveď je a projdi sebe-revizi znovu.

------

## Fáze 5 – Předání do plánu

Po schválení návrhu předej řízení na **`/breakdown`**, který ze zadání udělá `docs/plan.md`. Ten si sám najde zadání i kontext a ohlídá rozsah – nemusíš mu nic předávat ručně, jen ho vyvolej.

**Sám plán nepiš.** Ani „ať se to nemusí volat zvlášť“. Rozpad na úkoly má vlastní pravidla, vlastní kontrolu pokrytí MVP a vlastní schvalovací kontrolu.

**U projektu bez kódu** `/breakdown` nevyvolávej – rozepiš kroky do `docs/todo.md`.

Celý řetěz i s tím, co následuje po implementaci, je v `~/.claude/skills/LIFECYCLE.md`.

------

## Když se zadání změní později

Platí *Doc-first vývoj* z `~/.claude/RULES.md`; posloupnost souborů definuje `STRUCTURE.md`:

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

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Zadání je hotové a schválené, můžeme na implementační plán.`
- `Zadání hotové není – brání tomu: <konkrétní seznam>.`
