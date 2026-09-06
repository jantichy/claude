# /discovery – co je venku, než začnete stavět

> **Součást životního cyklu projektu.** Tenhle skill patří do ucelené sady jedenácti skillů, které vedou práci od založení projektu až po nasazení. Každý má svůj krok a žádný nedělá práci toho vedle:
>
> [`/project`](../project/README.md) → **`/discovery`** → [`/specify`](../specify/README.md) → [`/oponent`](../oponent/README.md) → [`/breakdown`](../breakdown/README.md) → [`/implement`](../implement/README.md) → [`/review`](../review/README.md) → [`/consistency`](../consistency/README.md) → [`/cleanup`](../cleanup/README.md) → [`/attack`](../attack/README.md) → [`/release`](../release/README.md)
>
> Projít se nemusí celá – u drobné změny odpadá zadání i plán, u projektu bez kódu nasazení.

Chystáte se postavit produkt a chcete vědět, do čeho vstupujete: kdo to už dělá, co to umí, kolik to stojí a proč by si někdo vybral zrovka vás. Skill to zjistí, vytřídí z toho, **co váš produkt musí umět, aby ho někdo vzal vážně**, a sepíše, co je na celé věci rizikové a co s tím udělat v návrhu. Pouští se dřív než psaní zadání schválně – aby to, co najde, mohlo zadání ještě změnit.

## Co umí

1. **Nejdřív si vymezí pole.** Čtyřmi otázkami zjistí, jaký problém řešíte, komu, v jaké kategorii tedy soutěžíte a čím se to má lišit. Bez toho by hledal buď všechno, nebo nic.
2. **Hledá pěti různými směry naráz** – přímé konkurenty, náhradní řešení (tabulka, papír, zvyk), sousední kategorie, které to můžou pohltit, stížnosti skutečných zákazníků a lokální český trh.
3. **Nezapíše nic, co nemá zdroj.** Každá cena a každá funkce má odkaz a datum zjištění; co se nedá doložit, vypadne, nebo se označí za neznámé.
4. **Vytřídí z toho tři seznamy** – co musíte mít, protože to má každý; čím se odlišíte a čím je to doložené; kde vědomě zaostanete a proč vám to nevadí.
5. **Sepíše registr rizik** – u každého dopad, pravděpodobnost, čím tomu čelíte a hlavně **co se kvůli tomu v produktu změní**. Riziko, které nic nemění, je jen poznámka.
6. **Dá se pustit znovu.** Za rok se konkurence pohne; druhý běh původní analýzu neprepíše, ověří ji a doplní.
7. **Pozná, kdy nemá běžet** – u interního nástroje, přírůstku do hotového produktu nebo aplikace na zakázku řekne, že to nemá trh, a skončí. Rizika sepsat nabídne i tak.

## Proč zrovna tenhle

- **Hledá i to, co není software.** Nejsilnější konkurent bývá tabulka nebo zvyk, a ten se v seznamu konkurenčních produktů nikdy neobjeví.
- **Fakta bez zdroje zahazuje.** Vymyšlená cena o řád vedle je horší než prázdné místo – postaví se na ní rozhodnutí a nikdo ji nezpochybní, protože vypadá doloženě.
- **Končí seznamem požadavků, ne prezentací.** Výstupem není přehled trhu k prolistování, ale konkrétní věty o tom, co váš produkt musí umět.
- **Odlišení musí být ověřitelné.** „Jednodušší a rychlejší" neprojde; projde jen tvrzení, které jde ověřit u konkurence.
- **Stojí před zadáním, ne za ním.** Analýza, která dorazí po schválené specifikaci, se buď ignoruje, nebo znamená přepis všeho.

## Jak se to používá

```
/discovery
```

Zeptá se na čtyři věci o tom, co chcete stavět, pak pošle na rešerši několik nezávislých hledání a výsledek s vámi projde. Skončí dvěma dokumenty v `docs/` a nabídne, že na ně pustí nezávislý posudek.

## Ukázka výstupu

```markdown
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
- Nedělá obchodní ani marketingový plán, finanční projekci ani komunikační strategii.
- Neposuzuje výsledek čerstvýma očima; na to navazuje samostatný posudek.
- Nedělá analytický report z vašich dat – sbírá fakta o cizích produktech.

## Jak si ho nainstalovat

Řekněte svému Claudovi:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/discovery
> a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.

Skill předpokládá, že projekt má kam zapisovat – chybí-li `docs/`, upozorní na to a nezaloží nic potichu. Odkazuje se na obecná pravidla práce a na standard struktury projektu; bez nich funguje, ale ptá se víc.

**Nebo celou sadu naráz.** Chcete-li místo jednoho skillu rovnou celý životní cyklus, napište mu tohle:

> Jdi na https://github.com/jantichy/claude/tree/main/skills a nainstaluj mi do `~/.claude/skills/` celý životní cyklus: project, discovery, specify, oponent, breakdown, implement, review, consistency, cleanup, attack a release. U každého si přečti README a řekni mi, co k nim potřebuju doplnit.

---

### Požadavky a omezení

Přístup na web pro vyhledávání. Rešerše běží na levnějším modelu, syntéza a rizika na nejsilnějším, takže cena je střední. Skill hledá veřejně dostupné údaje – co konkurence nezveřejňuje (skutečné ceny po slevě, počty zákazníků), nezjistí a nebude předstírat, že ano.
