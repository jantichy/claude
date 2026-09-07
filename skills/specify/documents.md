# Dokumenty zadání

Šablony a pravidla psaní pro dokumenty, které vyrábí `/specify`. Průběh – kdy se který píše, co ho spouští, kde jsou schvalovací kontroly – drží `SKILL.md`; tady je jen to, co má vzniknout.

- [Jak se píše](#jak-se-píše) – platí pro všechny dokumenty
- [`docs/requirements.md`](#docsrequirementsmd) – produktová specifikace
- [`docs/architecture.md`](#docsarchitecturemd) – návrh řešení
- [Scénáře, glosář a ceník](#scénáře-glosář-a-ceník) – tři z *Produktových podkladů*

------

## Jak se píše

Česky, věcně, bez omáčky, podle `~/Dev/context/text/text.md` a `~/Dev/context/text/typography.md`. Konkrétně – „rychlé načítání“ je nic, „LCP pod 2,5 s na 4G“ je požadavek. **Bez placeholderů**; co nevíš, patří do *Otevřených otázek* s tím, kdo to má rozhodnout.

Platí to pro všechny dokumenty na téhle stránce stejně.

------

## `docs/requirements.md`

Sekci, která pro projekt nedává smysl, vynech – ale **řekni, že jsi ji vynechal a proč**.

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

------

## `docs/architecture.md`

Vzniká v dialogu s uživatelem, po sekcích a se schválením po každé. Sekci, která pro projekt nedává smysl, vynech a řekni proč – stejně jako u požadavků.

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
*Ověřování a kontroly kvality*.
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

------

## Scénáře, glosář a ceník

Tři z pěti *Produktových podkladů*, které projekt vede volitelně – zbylé dva, `competition.md` a `risks.md`, píše `/discovery` a šablonu tady nemají. Kdy se píšou a podle čeho se pozná, že je projekt vede, říká `SKILL.md`; **co který dokument je a k čemu slouží, drží `~/.claude/STRUCTURE.md`, *Produktové podklady***. Tady je jen tvar a to, co platí při psaní.

**`docs/scenarios.md`** – jeden scénář na tenhle tvar, včetně okrajových a chybových cest:

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

**Píše se jako postup, ne jako příběh**, a nešetří se okrajovými cestami – čte to i ten, kdo podle toho testuje nebo píše nápovědu. **Zaniká tím sekce *Hlavní scénáře* v `requirements.md`** a nahradí ji odkaz; v požadavcích zůstává **proč a pro koho**, tady **jak to člověk provede**.

**`docs/glossary.md`** – u každého pojmu český název, název v kódu, význam a **čím se liší od pojmu, se kterým se plete**. To poslední je hlavní obsah, ne doplněk. **Rozšiřuje se ještě při návrhu řešení** – entita, která v něm dostane jméno, ho má mít i tady.

**`docs/pricing.md`** – každá věta v něm je funkce, kterou pak někdo musí naprogramovat, takže **každý tarif i limit patří zároveň do *MVP*, nebo do *Mimo rozsah***. Zůstane-li jen tady, nikdo ho nepostaví.
