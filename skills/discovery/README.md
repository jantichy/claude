# /discovery – co je venku, než začnete stavět

> **Součást životního cyklu projektu.** Tenhle skill patří do ucelené sady skillů, které vedou práci od založení projektu až po nasazení. Jedny tvoří, druhé se starají o to, co už vzniklo – a žádný nedělá práci toho vedle:
>
> **Osa** [`/project`](../project/README.md) → **`/discovery`** → [`/specify`](../specify/README.md) → [`/architect`](../architect/README.md) → [`/breakdown`](../breakdown/README.md) → [`/implement`](../implement/README.md) → [`/release`](../release/README.md) → [`/evaluate`](../evaluate/README.md)
>
> **Kontroly** [`/oponent`](../oponent/README.md) · `/consolidate` · [`/review`](../review/README.md) · [`/consistency`](../consistency/README.md) · [`/attack`](../attack/README.md) · [`/cleanup`](../cleanup/README.md) · [`/merge`](../merge/README.md) – stojí v mezerách mezi kroky osy, některé z nich ve víc mezerách
>
> Projít se nemusí celý – u drobné změny odpadá zadání i plán, u projektu bez kódu nasazení.

Chystáte se postavit produkt. Skill se nejdřív zeptá na otázku, která se snadno přeskočí – **chce to vůbec někdo?** – a nespokojí se s dojmem: dohledá, jestli ten problém lidé někde sami popisují a jestli za jeho řešení dnes platí. Pak teprve zjistí, do čeho vstupujete: kdo to už dělá, co to umí, kolik to stojí a proč by si někdo vybral zrovna vás. Z toho vytřídí, **co váš produkt musí umět, aby ho někdo vzal vážně**, a sepíše, co je na celé věci rizikové a co s tím udělat v návrhu. Pouští se dřív než psaní zadání schválně – aby to, co najde, mohlo zadání ještě změnit.

## Co umí

1. **Nejdřív se ptá na problém, ne na produkt.** Pěti otázkami zjistí, jaký problém řešíte a komu, co ten člověk dělá dneska a co ho to stojí, odkud víte, že to chce řešit, v jaké kategorii tedy soutěžíte a čím se to má lišit.
2. **Poptávku si ověří venku.** Hledá, kde lidé ten problém sami popisují, jestli za jeho řešení dnes někdo platí a kolik lidí ho vůbec hledá. Skončí to **verdiktem o dvou hodnotách** – poptávka doložená, nebo nedoložená, nic mezi tím.
3. **Odděluje doklad od dojmu.** „Myslím, že to lidi chtějí“ a „tři lidé mě o to sami požádali“ jsou v dokumentu dvě různé sekce. Vyjde-li poptávka nedoložená, zastaví se a nabídne tři cesty dál – ověřit ji nejmenším možným pokusem, pokračovat s rizikem zapsaným v registru, nebo pokračovat proto, že o stavbě rozhodl někdo jiný.
4. **Hledá několika směry naráz.** Katalog má patnáct cest ve čtyřech skupinách a vybírá se z něj dvakrát, s odděleným rozpočtem: nejdřív cesty k poptávce (viz bod 2), pak zvlášť ty ostatní – kdo to už dělá (přímí konkurenti, náhradní řešení, sousední kategorie, open source, český trh **a produkty, které to zkusily a skončily**), co lidé chtějí (stížnosti zákazníků, přechod od stávajícího řešení, čekané integrace, terminologie oboru) a co se musí (regulace a povinnosti, jak se v oboru účtuje).
5. **Hledání náhradních řešení nikdy nevynechá.** Je to cesta, na kterou se vždycky zapomene, a bývá za ní největší konkurent.
6. **Nezapíše nic, co nemá zdroj.** Každá cena a každá funkce má odkaz a datum zjištění; co se nedá doložit, vypadne, nebo se označí za neznámé.
7. **Vytřídí z toho tři seznamy** – co musíte mít, protože to má každý; čím se odlišíte a čím je to doložené; kde vědomě zaostanete a proč vám to nevadí.
8. **Sepíše registr rizik** – u každého dopad, pravděpodobnost, čím tomu čelíte a hlavně **co se kvůli tomu v produktu změní**. Riziko, které nic nemění, je jen poznámka.
9. **Dá se pustit znovu.** Za rok se konkurence pohne; druhý běh původní analýzu nepřepíše, ověří ji a doplní.
10. **Pozná, kdy má běžet jen zčásti.** U interního nástroje nebo zakázky pro klienta vynechá konkurenci – trh tam není –, ale poptávku a rizika sepíše i tak: nástroj, který si lidé v organizaci obejdou tabulkou, je totéž selhání jako aplikace bez zákazníků. Celý odpadá jen u přírůstku do hotového produktu, kde je rozhodnutí zapsané odjinud.

## Proč zrovna tenhle

- **Začíná otázkou, jestli to má kdo chtít.** Postavit pečlivě něco, co nikdo nepotřebuje, je nejdražší způsob, jak práce selže – a pozná se to až na konci, kdy už se s tím nedá nic dělat.
- **Hledá i to, co není software.** Nejsilnější konkurent bývá tabulka nebo zvyk, a ten se v seznamu konkurenčních produktů nikdy neobjeví.
- **Dívá se i na to, co selhalo.** Produkty, které v kategorii skončily, jsou nejlevnější zdroj rizik – ta rizika už někdo zaplatil.
- **Fakta bez zdroje zahazuje.** Vymyšlená cena o řád vedle je horší než prázdné místo – postaví se na ní rozhodnutí a nikdo ji nezpochybní, protože vypadá doloženě.
- **Končí seznamem požadavků, ne prezentací.** Výstupem není přehled trhu k prolistování, ale konkrétní věty o tom, co váš produkt musí umět.
- **Odlišení musí být ověřitelné.** „Jednodušší a rychlejší“ neprojde; projde jen tvrzení, které jde ověřit u konkurence.
- **Stojí před zadáním, ne za ním.** Analýza, která dorazí po schválené specifikaci, se buď ignoruje, nebo znamená přepis všeho.

## Jak se to používá

```
/discovery
```

Zeptá se na pět věcí o tom, co chcete stavět, ověří poptávku, pak pošle na rešerši několik nezávislých hledání a výsledek s vámi projde. Skončí třemi dokumenty v `docs/` a nabídne, že na ně pustí nezávislý posudek.

## Ukázka výstupu

```markdown
## Verdikt
**Poptávka doložená** – ve třech účetních skupinách si na to za půl roku
postěžovalo 40 lidí, dvě agentury to dnes dělají ručně za 1 500 Kč měsíčně.

## Co by verdikt vyvrátilo
Kdyby se ukázalo, že těch 40 stížností jsou lidé, kteří to řeší jednou za rok
a zaplatit za to nechtějí.

## Naše pozice a odlišení

### Co musíme mít
- Export do XML pro účetní systémy – má to všech pět srovnávaných řešení
- Přístup pro víc lidí s rozlišením práv – bez toho nás nevezme nikdo nad tři lidi

### Čím se lišíme
- Zákazník objedná bez zakládání účtu
  *Doloženo: u všech pěti srovnávaných vyžaduje objednávka registraci (ověřeno 2026-09-06)*

### Kde vědomě zaostáváme
- Mobilní aplikace nebude. Konkurence ji má, ale ve stížnostech uživatelů
  se objevuje jen okrajově a stojí to celý zbytek rozpočtu.
```

## Co nedělá

- Nepíše zadání ani specifikaci produktu – to je práce dalšího kroku.
- Nerozhoduje za vás, jestli se to postaví. Doloží poptávku, nebo řekne, že doložená není; co s tím, je na vás.
- Nepředstírá uživatelský výzkum – doklad z veřejného zdroje není rozhovor se zákazníkem.
- Nedělá obchodní ani marketingový plán, finanční projekci ani komunikační strategii.
- Neposuzuje výsledek čerstvýma očima; na to navazuje samostatný posudek.
- Nedělá analytický report z vašich dat – sbírá fakta o cizích produktech.

## Jak si ho nainstalovat

Nechte to na Claudovi. Otevřete si Claude Code a napište mu:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/discovery
> a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.
> Z https://github.com/jantichy/claude/tree/main/agents k tomu vezmi
> i definice typů subagentů do `~/.claude/agents/`.

Skill předpokládá, že projekt má kam zapisovat – chybí-li `docs/`, upozorní na to a nezaloží nic potichu. Odkazuje se na obecná pravidla práce a na standard struktury projektu; bez nich funguje, ale ptá se víc.

**Nebo celou sadu naráz.** Chcete-li místo jednoho skillu rovnou celý životní cyklus, napište mu tohle:

> Jdi na https://github.com/jantichy/claude/tree/main/skills a nainstaluj mi do `~/.claude/skills/` celý životní cyklus: project, discovery, specify, architect, breakdown, implement, release, evaluate, oponent, review, consistency, attack, cleanup a merge. Z https://github.com/jantichy/claude/tree/main/agents k tomu vezmi i definice typů subagentů do `~/.claude/agents/`. U každého si přečti README a řekni mi, co k nim potřebuju doplnit.

---

### Požadavky a omezení

Přístup na web pro vyhledávání. Rešerše běží na levnějším modelu, syntéza a rizika na nejsilnějším, takže cena je střední. Skill hledá veřejně dostupné údaje – co konkurence nezveřejňuje (skutečné ceny po slevě, počty zákazníků), nezjistí a nebude předstírat, že ano.
