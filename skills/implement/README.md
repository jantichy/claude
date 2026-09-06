# /implement – odpracovat plán úkol po úkolu, ne jedním velkým skokem

> **Součást životního cyklu projektu.** Tenhle skill patří do ucelené sady deseti skillů, které vedou práci od založení projektu až po nasazení. Každý má svůj krok a žádný nedělá práci toho vedle:
>
> [`/project`](../project/README.md) → [`/specify`](../specify/README.md) → [`/oponent`](../oponent/README.md) → [`/breakdown`](../breakdown/README.md) → **`/implement`** → [`/review`](../review/README.md) → [`/consistency`](../consistency/README.md) → [`/cleanup`](../cleanup/README.md) → [`/attack`](../attack/README.md) → [`/release`](../release/README.md)
>
> Projít se nemusí celá – u drobné změny odpadá zadání i plán, u projektu bez kódu nasazení.

Vezme hotový implementační plán a projde ho od začátku do konce: u každého úkolu test, kód, ověření a commit. Nikdy nejde dál, dokud projektu neběží typová kontrola, linter a testy. Umí navázat na rozdělaný plán, a **nevěří přitom zaškrtávátkům** – ověří si v kódu, že odškrtnuté úkoly opravdu existují a procházejí, protože plán mohl zůstat odškrtnutý po přerušené práci.

## Co umí

1. **Tři režimy práce**, mezi kterými se na začátku vybírá:
   - **po úkolech se čtením mezi nimi** *(doporučený)* – na každý úkol jde čerstvý pracovník, který nevidí předchozí konverzaci, a mezi úkoly se výsledek zkontroluje;
   - **v jednom kuse s kontrolními body** – rychlejší a s menší režií, vhodné na krátký plán;
   - **bez zastávek až do splnění cíle** – nejsamostatnější, nabídne se **jen když je splněných pět podmínek** a nikdy se nezapne sám.
2. **Zelená linka po každém úkolu.** Úkol není hotový napsaným kódem, ale tím, že projektu všechno běží.
3. **Ověření skutečného stavu před navázáním** na rozdělaný plán.
4. **Levné mezikontroly** po každé skupině souvisejících úkolů, v čerstvém pohledu.
5. **Průběžný zápis mimo kód** – co se cestou rozhodlo, včetně zavržených variant; co se dodělalo, se přesune mezi hotové.
6. **Zastaví se, když plán neplatí**, a rozliší, jak hluboko problém sahá – jestli jde o překlep v úkolu, o vadu návrhu, nebo o to, že chceme něco jiného.

## Proč zrovna tenhle

- **Testy jsou jen ke čtení.** Nesedí-li test s implementací, první hypotéza je, že je špatně kód. Změna testu je samostatný zásah, který se ohlásí a schválí – nikdy tichá součást úkolu. Vypnutí testu nebo zeslabení kontroly je chyba, i když je pak zeleno.
- **Netvrdí, že to prošlo, bez doložení.** Do souhrnu patří příkaz a jeho výsledek, ne věta „testy procházejí". Co se zkontrolovat nedalo, se vypíše jako nezkontrolované.
- **Nedodělává, co v plánu není.** Nápad, který cestou vznikne, jde mezi odložené věci i s celou úvahou, ne rovnou do kódu.
- **Nikdy neodškrtne úkol, aby se dalo pokračovat.** Zablokovaný úkol zůstane neodškrtnutý i s důvodem.
- **Samostatnost se stupňuje, nezapíná.** Nejvolnější režim je přiznaná výměna – míň přerušení za horší bezpečnostní profil – a má povinné pojistky: strop na iterace, zvlášť hlídané změny v testech a povinnou revizi po doběhnutí.
- **Nezačne nad rozdělanou prací ani nad červeným stavem** – jinak by nešlo poznat, co rozbil kdo.

## Jak se to používá

```
/implement
```

Skill si najde plán, ověří stav projektu, nechá vás vybrat režim a pak jede úkol po úkolu až do konce plánu.

## Ukázka výstupu

```
## Realizace hotová

**Plán:** docs/plan.md – 14/14 úkolů
**Režim:** po úkolech
**Commity:** 14

**Odchylky od plánu**
- úkol 6: název souboru v plánu neseděl, opraveno v plánu i v kódu

**Zelená linka:** npm test → 0

**Další krok:** /review
```

## Co nedělá

- **Nemění plán potichu.** Ukáže-li se, že je špatně, zastaví se a řekne, jak hluboko problém sahá.
- **Neuzavírá práci.** Revize, audit konzistence a úklid jsou samostatné kroky po tomhle.
- **Nehledá si práci navíc.** Je-li plán odpracovaný, řekne to a skončí.

## Jak si ho nainstalovat

Nechte to na Claudovi. Otevřete si Claude Code a napište mu:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/implement a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.

Skill je **obálka nad pluginem [superpowers](https://github.com/obra/superpowers)** – ten potřebujete mít nainstalovaný, klidně o to Clauda požádejte zároveň. Sám k němu přidává volbu režimu, ověření skutečného stavu proti plánu, pravidla kolem testů a podmínky pro nejsamostatnější režim.


**Nebo celou sadu naráz.** Chcete-li místo jednoho skillu rovnou celý životní cyklus, napište mu tohle:

> Jdi na https://github.com/jantichy/claude/tree/main/skills a nainstaluj mi do `~/.claude/skills/` celý životní cyklus: project, specify, oponent, breakdown, implement, review, consistency, cleanup, attack a release. U každého si přečti README a řekni mi, co k nim potřebuju doplnit.

---

### Požadavky a omezení

Plugin superpowers. Projekt potřebuje mít v instrukcích zapsané, čím se pouštějí testy, typová kontrola a linter – bez toho by realizace běžela bez brány a skill se zastaví a nabídne to doplnit. Nejsamostatnější režim navíc předpokládá, že je zelená linka vynucená automaticky, ne jen doporučená.
