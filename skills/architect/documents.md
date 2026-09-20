# Dokumenty návrhu

Šablony a pravidla psaní pro dokumenty, které vyrábí `/architect`. Průběh – kdy se který píše, co ho spouští, kde jsou schvalovací kontroly – drží `SKILL.md`; tady je jen to, co má vzniknout. Požadavky a produktové podklady tady nejsou: jejich šablonu drží `~/.claude/skills/specify/documents.md`.

**Návrh řešení je sada dokumentů**, ne jeden soubor. `architecture.md` je jeho páteř a šablona níž patří jemu; kdy vzniká vedle něj `model.md`, `transitions.md`, `rules.md` nebo tematický dokument kola, drží `~/.claude/STRUCTURE.md`, *`requirements.md`, `architecture.md`, `plan.md`*. Ty vlastní šablonu nemají a mít nemají – každý z nich je řez toutéž věcí z jiného úhlu a předepsaná kostra by je srovnala do jednoho.

- [Jak se píše](#jak-se-píše) – platí pro všechny dokumenty návrhu
- [`docs/architecture.md`](#docsarchitecturemd) – páteř návrhu řešení

------

## Jak se píše

Česky, věcně, bez omáčky, podle `~/Dev/context/text/text.md` a `~/Dev/context/text/typography.md`. Konkrétně – „rychlé načítání“ je nic, „LCP pod 2,5 s na 4G“ je požadavek. **Bez placeholderů**; co nevíš, patří do *Otevřených otázek* s tím, kdo to má rozhodnout.

------

## `docs/architecture.md`

Vzniká v dialogu s uživatelem, po sekcích a se schválením po každé. Sekci, která pro projekt nedává smysl, vynech – ale **řekni, že jsi ji vynechal a proč**.

**Je-li projekt *aplikace*** (rozlišení drží `~/Dev/context/coding/architecture.md` a zapisuje ho `/project` do sekce *Typ projektu*), **načti si ten standard dřív, než začneš psát.** Nese kontrolní seznam *Minimum hotové aplikace*, proti kterému se návrh posuzuje – a řadu sekcí téhle šablony přímo předepisuje: vrstvy, cestu k datům, hranici transakce kolem cizího systému, souběh, běhy na pozadí. **Na konci projdi ten seznam položku po položce** a u každé řekni, kde je v návrhu vyřešená, nebo že se vědomě nedělá a proč; nevyřešená položka bez zápisu je nedodělek, ne zjednodušení. U *nástroje* se tohle přeskakuje a řekne se to nahlas.

```markdown
# <Lidský název> – návrh řešení

Vychází z [produktové specifikace](requirements.md). Co a proč se staví, je tam;
tady je, jak.

## Zvolený přístup
Jaké varianty byly ve hře, která vyhrála a proč. Zamítnuté i s důvodem.

## Architektura
Komponenty, jejich odpovědnosti a hranice. U každé: co dělá, jak se
používá, na čem závisí.
U aplikace (viz níž) k tomu **vrstvy a směr závislostí** a **jediná cesta
k datům** – kdo skládá objekt „kdo přišel“, kde se otevírá transakce a kde
se nastavuje kontext, kterým se filtrují data. A čím se to vynucuje:
typem, pravidlem lintru, testem, který to zkusí obejít.

## Transakce, souběh a běhy na pozadí
Kde jsou hranice transakcí vůči cizím systémům a co se stane, když volání
uspěje a zápis pak selže. Která místa mají souběh a čím je ošetřený –
v místě zápisu, ne kontrolou před ním. Které běhy jdou na pozadí a jak
jsou přerušitelné.
Vynech u projektu bez trvalých dat a bez cizích systémů.

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
Co se testuje a na jaké úrovni. Co se mockuje – u aplikace s vlastní
databází platí, že se mockuje ven, ne dovnitř (`~/Dev/context/coding/quality.md`),
takže sem patří i to, čím se skutečná databáze v testech poskytne. U každého scénáře a *Varianty* řekni, čím bude
pokrytý – akceptačním testem, jednotkovým, nebo vědomě ničím a proč.
Scénáře ber z `scenarios.md`, vede-li ho projekt; jinak ze sekce *Hlavní
scénáře* v requirements.md.
Dál prahy, které bude projekt držet (pokrytí, mutation score) a čím se měří.
Výchozí hodnoty a nástroje viz `~/Dev/context/coding/quality.md`,
*Kontroly, které nestojí tokeny*.
Zvlášť rozhodni o **generativních testech** – fuzzingu a property-based testech.
Vyplatí se u parserů, validace vstupu, převodů formátů, výpočtů nad rozsahy
a stavových automatů: najdou vstup, na který nikdo nepomyslel, a stojí tokeny
jen jednou. Napiš, kde je projekt bude mít, nebo že je mít nebude a proč –
prázdné místo tady znamená, že se nenapíšou nikdy.

## Ověřování a kontroly
Konkrétní příkazy, které projekt bude mít – `test`, `typecheck`, `lint`,
`build`, `audit`, případně `e2e` a `mutation`.
Je to **záměr, ne kontrakt**: *Kontrakt příkazů* v `CLAUDE.md` musí odpovídat
tomu, co projekt opravdu umí spustit, takže ho zapisuje až ten, kdo to vidí –
první úkol plánu, který příkazy zavede, případně opakovaný běh `/project`.
Řekni i, co se **nebude** kontrolovat automaticky a proč.

## Rizika
Co je na tom nejistého a co by to znamenalo, kdyby se ukázalo jinak.
```
