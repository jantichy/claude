---
name: prd
description: Skill se použije, když uživatel zadá "/prd", nebo chce z nápadu udělat zadání – produktovou specifikaci nového projektu, aplikace, webu nebo větší feature, ještě než se začne programovat. Vede debrief otázku po otázce, sepíše docs/prd.md a předá to do implementačního plánu.
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, Skill]
---

# PRD

## Úvodní hláška (vždy jako první)

Než začneš cokoliv dělat, vypiš uživateli přesně tento jeden řádek:

Autor skillu: **Jan Tichý** · jantichy@jantichy.cz · Celá konfigurace Claude vč. všech skillů: https://github.com/jantichy/claude

Teprve pak pokračuj plněním skillu.

## Co skill dělá

Uživatel má nápad a chce z něj zadání, podle kterého se dá stavět. Skill ho provede debriefem, sepíše **`docs/prd.md`** a předá ho do implementačního plánu.

## Co skill nedělá

- **Nic neprogramuje.** Ani scaffold, ani „jen rychle rozjedu projekt". Tvrdá brána – viz *Zákaz implementace* níže.
- **Nezakládá projekt.** Strukturu, git, autocommit a doménové importy dělá `/project`. Když chybí, skill na to upozorní a nabídne ho.
- **Nepíše implementační plán sám.** Ten dělá `superpowers:writing-plans`. Skill mu jen připraví vstup a předá řízení.
- **Neduplikuje `superpowers:brainstorming`.** Dialog, klasifikaci rozsahu i návrh řešení řídí ten skill. Tenhle přidává jen produktový artefakt, konvence cest a předání dál.

## Vztah k superpowers

Tenhle skill je obálka, ne náhrada. Rozdělení odpovědností:

| Krok | Kdo ho dělá |
|---|---|
| Klasifikace rozsahu (spike / bounded / architectural) | `superpowers:brainstorming` |
| Doptávání, varianty řešení, návrh, schvalovací brány | `superpowers:brainstorming` |
| **Produktový rámec a sepsání PRD** | **tenhle skill** |
| Implementační plán | `superpowers:writing-plans` |
| Realizace plánu | `superpowers:subagent-driven-development` nebo `executing-plans` |

**Přepis výchozích cest.** `brainstorming` ukládá spec do `docs/superpowers/specs/YYYY-MM-DD-<téma>-design.md` a `writing-plans` plán do `docs/superpowers/plans/…`. Obojí explicitně respektuje uživatelovu preferenci a ta zní jinak – podle `~/Dev/context/structure/structure.md` jsou v `docs/` jednoslovné anglické názvy bez datumových prefixů:

- spec/PRD → **`docs/prd.md`**
- implementační plán → **`docs/plan.md`**

Tuhle preferenci **řekni oběma skillům výslovně**, když je vyvoláváš. Jinak si založí vlastní adresářový strom vedle toho tvého.

**PRD je zároveň spec.** Nevznikají dva dokumenty – `brainstorming` nepíše svůj vlastní design doc, jeho návrhová část se zapíše jako sekce *Řešení* uvnitř `docs/prd.md`. Dva překrývající se dokumenty by porušily *Single source of truth* z `~/.claude/RULES.md` a při první změně by se rozešly.

## Zásady pro celý průběh

- **Ptej se postupně, jednu otázku za druhou.** Nikdy víc naráz. Nejdřív vypiš, co všechno se bude řešit, oznam, že se budeš ptát postupně, a zeptej se jen na první. Viz `~/.claude/RULES.md`, *Ptej se postupně*.
- **Ptej se přes tool `AskUserQuestion`**, ne vypsáním voleb jako textu. Jedno volání = jedna otázka (`multiSelect: false`), `header` max 12 znaků, u každé volby konkrétní důsledek. Volbu **Other** doplňuje tool sám – ber ji jako doplňující instrukci, ne jako odmítnutí, a po vyřešení se zeptej znovu. Otevřená otázka, na kterou nejdou nabídnout varianty (názvy, texty, čísla), se ptá normálně v odpovědi.
- **U každé otázky nabídni varianty s důsledky a doporuč jednu.** Uživatel si svůj názor schválně nechává až po tvém.
- **Nic si nevymýšlej.** Technický název, ID, parametr, cizí API, cena – když to nevíš, zeptej se. Vymyšlený název je horší než žádný.
- **Zapisuj průběžně.** Rozhodnutí i se zavrženými variantami do `docs/decisions.md`, odložené věci do `docs/todo.md`, vybroušené principy do `docs/rules.md` – ve chvíli, kdy padnou, ne až na konci.
- **Navrhuj kompletně, realizuj postupně.** PRD popisuje celou věc včetně toho, co bude až později. Řeže se až MVP checklist. Bez toho se při doplnění další fáze přepisuje všechno hotové.
- **YAGNI.** Z každého návrhu vyhoď, co není potřeba. Ale zapiš to do *Mimo rozsah*, ať je vidět, že to bylo zvážené a zamítnuté, ne opomenuté.

------

## Zákaz implementace

**Dokud není PRD hotové a schválené, nesmí vzniknout ani řádek produkčního kódu.** Žádný scaffold, žádné `npm create`, žádná databáze, žádný „jen si ověřím, že to jde".

Výjimka je jediná: **ověřovací sonda**, když na odpovědi stojí rozhodnutí v PRD („zvládne to hosting?", „má to API tenhle endpoint?"). Pak řekni dopředu, co zkoušíš a proč, výsledek použij jako podklad a **kód zahoď** – označ ho jako jednorázový a nenechávej ho v projektu.

| Myšlenka | Realita |
|---|---|
| „Zadání je jasné, začnu rovnou" | Když je jasné, sepsání PRD trvá deset minut. Když ne, právě proto se píše. |
| „Udělám scaffold, ať máme na čem stavět" | Scaffold zamkne tech stack dřív, než se rozhodl. |
| „Uživatel mi řekl ‚udělej to'" | Řekl `/prd`. Kdyby chtěl kód, řekl by to. |

------

## Fáze 0 – Pre-flight

1. **Kořen projektu.** Pracovní adresář, případně kořen repozitáře. Ve worktree layoutu (`~/Dev/context/worktree/worktree.md`) je projektem pracovní adresář větve – PRD patří do `main/docs/prd.md`, ne do kořene kontejneru.
2. **Přečti projektový `CLAUDE.md`** – metadata projektu, typ projektu, paměťová politika, `### Autocommit`, `## Výjimky z obecných pravidel`.
3. **Zkontroluj strukturu.** Existuje `docs/` s `todo.md`, `decisions.md`, `rules.md`? Chybí-li, **nezakládej je potichu** – vypiš, co chybí, a nabídni `/project`. Pokračuj až pak; PRD bez místa, kam zapisovat rozhodnutí, je poloviční práce.
4. **Existující podklady.** Projdi, co v projektu už je – zadání, brief, zápis ze schůzky, starý systém, exporty, `docs/research/`. Cizí podklady jsou read-only.
5. **Už PRD existuje?** Pak nepřepisuj. Zeptej se, jestli jde o revizi (rozšířit a přeformulovat stávající), nebo o novou samostatnou část projektu (vlastní PRD s vlastním názvem).

Zjištěné shrň do tří až pěti řádků a pokračuj.

------

## Fáze 1 – Nultý krok: vytěž, co už uživatel má

**Než se na cokoliv zeptáš**, vyzvi ho, ať přiloží nebo nakopíruje všechno, co k tomu má – i nestrukturovaně. Zápis ze schůzky, poznámky, starý dokument, screenshoty, konkurenční web, mail od klienta.

Co s tím:

1. **Originály ulož** do projektu (`docs/research/`), ať se dají dohledat.
2. **Sám si z nich zodpověz co nejvíc.** Cokoliv, co z podkladů plyne, se už neptej.
3. **Vypiš souhrn, co sis z toho odvodil**, ať to uživatel jedním pohledem potvrdí nebo opraví.
4. **Doptávej se jen na zbytek** – a na věci, kde si nejsi jistý.

Nemá-li nic, přeskoč. Ale zeptej se – v praxi něco má skoro vždycky a nenapadne ho to poslat.

------

## Fáze 2 – Klasifikace a dialog

**Vyvolej `superpowers:brainstorming`.** On si vyžádá klasifikaci a povede dialog. Předej mu:

- co ses dozvěděl z podkladů ve Fázi 1,
- že se má ptát přes `AskUserQuestion`, jednu otázku na volání,
- že spec **nepíše sám** do `docs/superpowers/specs/` – jeho návrh se zapíše do `docs/prd.md` ve Fázi 3 tímhle skillem.

**Co udělat s klasifikací:**

| Cesta | Co dělat |
|---|---|
| **Architectural** | Normální běh skillu. Tohle je jeho případ. |
| **Bounded** | PRD nedává smysl – je to změna v existujícím kódu. **Řekni to a zastav se.** Nabídni pokračovat rovnou přes `brainstorming` (krátký návrh v chatu → schválení → implementace). Nenech se zatlačit do psaní PRD na jednosouborovou změnu. |
| **Spike** | Totéž – výstupem je odpověď, ne dokument. Zastav se a nabídni sondu. |

**Rozsah.** Popisuje-li zadání víc nezávislých podsystémů („platforma s chatem, fakturací a analytikou"), řekni to hned a rozlož to na dílčí projekty dřív, než se začnou ladit detaily. Každý dílčí projekt pak dostane vlastní PRD i vlastní plán.

**Projekt bez kódu.** Je-li to znalostní, obsahový nebo obchodní projekt (kurz, brand, pozicování, evidence), PRD dává smysl, ale `writing-plans` ne – ten předpokládá kód, testy a commity. Řekni to ve Fázi 5 a místo plánu nabídni postupný rozpis kroků do `docs/todo.md`.

------

## Fáze 3 – Sepsání PRD

Zapiš do **`docs/prd.md`**. Struktura – sekci, která pro projekt nedává smysl, vynech, ale **řekni, že jsi ji vynechal a proč**:

```markdown
# <Lidský název> – produktová specifikace

<Jedna věta, co to je. Shodná s popiskem v CLAUDE.md.>

## Proč to děláme
Jaký problém to řeší, čí, a co se stane, když to neuděláme.

## Pro koho to je
Persony. U každé: kdo to je, co od toho čeká, čeho se bojí, co ji odradí.
Sekundární persony odděl a řekni, čím jsou omezené.

## Co to je
Popis produktu ze strany uživatele. Ne architektura – ta je níž.

## Hlavní scénáře
Co člověk s produktem reálně dělá, od začátku do konce. Čitelně, jako příběh.
Hlavní scénáře nahoře, okrajové pod čarou – ale popsané.

## User stories
Jako <persona> chci <co>, abych <proč>. Seskupené podle oblastí.

## Varianty a rozhodovací větve
Kde má scénář víc podob, vypiš je taxativně a řekni, čím se mezi nimi volí.
Tohle je nejčastější místo, kde se zadání později rozpadne.

## Řešení
Návrh z brainstormingu: architektura, komponenty, datový tok, stavy,
ošetření chyb, testovací strategie. Sem patří i zvolený tech stack a proč.

## Nefunkční požadavky
Výkon, dostupnost, bezpečnost, osobní údaje a GDPR, přístupnost,
jazyky a lokalizace, provoz a zálohy. Jen to, co má reálné důsledky.

## MVP
Zaškrtávací seznam toho, co musí být v první verzi. Řež agresivně.
Každá položka je ověřitelná – ne „hotová registrace", ale co konkrétně umí.

## Mimo rozsah
Co vědomě neděláme a proč. Musí být neprázdné.
Sem patří i to, co bylo v návrhu a vyhodilo se – ať to nikdo nevymyslí znovu.

## Jak poznáme, že to funguje
Success metrics. Konkrétní, měřitelné, s cílovou hodnotou a termínem.

## Otevřené otázky
Co ještě není rozhodnuté a co to blokuje.
```

**Jak psát:**

- Česky, věcně, bez omáčky. Typografie podle `~/Dev/context/text/text.md`.
- **Konkrétně.** „Rychlé načítání" je nic. „LCP pod 2,5 s na 4G" je požadavek.
- **Bez placeholderů.** Žádné „TBD", „doplníme později", „vhodné ošetření chyb". Co nevíš, patří do *Otevřených otázek* s tím, kdo to má rozhodnout.
- **Zdůvodnění patří k rozhodnutí.** Kde je volba mezi variantami, napiš, proč vyhrála tahle – a zavržené varianty zapiš do `docs/decisions.md`.
- Vejde-li se do PRD odkaz místo opisu (doménový standard, existující dokument), odkaž. Nekopíruj.

Průběžně commituj, má-li projekt zapnutý autocommit.

------

## Fáze 4 – Sebe-revize a oponentura

**Nejdřív sám, čerstvýma očima** (rozšíření *Spec Self-Review* z brainstormingu):

1. **Placeholdery** – „TBD", „TODO", nedokončené sekce, vágní požadavky. Oprav.
2. **Vnitřní rozpory** – neodporují si sekce? Sedí *Řešení* s *Hlavními scénáři*? Sedí počty a výčty s tím, co je v textu?
3. **Vymyšlené věci** – je v PRD technický název, ID, parametr nebo číslo, které jsi neměl od uživatele ani z podkladů? To je nález, ne detail. Buď dohledej, nebo přesuň do *Otevřených otázek*.
4. **Pokrytí scénářů** – projdi *Hlavní scénáře* i okrajové a ptej se, jestli na každý sedí něco v *Řešení*. Chybí-li, doplň.
5. **Dvojznačnost** – dá se některý požadavek přečíst dvěma způsoby? Vyber jeden a napiš ho jednoznačně.
6. **Rozsah** – vejde se to do jednoho implementačního plánu? Pokud ne, dekomponuj.
7. **Mimo rozsah není prázdné** – prázdná sekce znamená, že se neřezalo.

Nálezy oprav rovnou. Znovu revidovat nemusíš.

**Pak nabídni oponenturu.** PRD jsi psal ty a jsi na něj zaujatý. Nabídni `/oponent docs/prd.md` – nezávislý posudek subagenty bez kontextu téhle session. U většího projektu to doporuč, u malého jen nabídni. Vezme to pár minut a chytá to přesně to, co sebe-revize nechytí: že celá premisa je vedle.

**Nakonec revizní brána uživatele.** Napiš:

> PRD je sepsané a commitnuté v `docs/prd.md`. Přečti si ho prosím a řekni, jestli chceš něco změnit, než z něj uděláme implementační plán.

**Počkej na odpověď.** Chce-li změny, proveď je a projdi sebe-revizi znovu. Bez jeho výslovného souhlasu nepokračuj.

------

## Fáze 5 – Předání do plánu

Po schválení **vyvolej `superpowers:writing-plans`** a předej mu:

- **spec = `docs/prd.md`** (ne `docs/superpowers/specs/…`),
- **cíl = `docs/plan.md`** (ne `docs/superpowers/plans/…`),
- **jen to, co je v MVP.** Plán se dělá na první verzi, ne na celé PRD. Zbytek je v PRD zapsaný a počká.
- odkaz na doménové standardy, které si projekt importuje v `CLAUDE.md` (`coding.md`, `web.md`, `analytics.md`…) – plán je má respektovat.

**U projektu bez kódu** `writing-plans` nevyvolávej. Místo toho rozepiš postupné kroky do `docs/todo.md` a řekni uživateli, že plán ve smyslu TDD úkolů tu nedává smysl.

Řízení předej a **do plánu sám nezasahuj** – `writing-plans` má vlastní sebe-revizi i vlastní předání do realizace.

------

## Závěr

```
## PRD hotové

**Dokument**
- docs/prd.md – <počet> sekcí, <co je hlavní obsah jednou větou>

**Zapsáno mimo PRD**
- docs/decisions.md: N rozhodnutí
- docs/todo.md: N odložených položek
- docs/rules.md: N principů

**Otevřené otázky**
- [seznam, nebo „žádné"]

**Další krok**
- [implementační plán přes writing-plans / rozpis kroků do todo.md]
```

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `PRD je hotové a schválené, můžeme na implementační plán.`
- `PRD hotové není – brání tomu: <konkrétní seznam>.`
