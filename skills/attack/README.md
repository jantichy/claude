# /attack – zkusit aplikaci doopravdy rozbít

> **Součást životního cyklu projektu.** Tenhle skill patří do ucelené sady deseti skillů, které vedou práci od založení projektu až po nasazení. Každý má svůj krok a žádný nedělá práci toho vedle:
>
> [`/project`](../project/README.md) → [`/specify`](../specify/README.md) → [`/oponent`](../oponent/README.md) → [`/breakdown`](../breakdown/README.md) → [`/implement`](../implement/README.md) → [`/review`](../review/README.md) → [`/consistency`](../consistency/README.md) → [`/cleanup`](../cleanup/README.md) → **`/attack`** → [`/release`](../release/README.md)
>
> Projít se nemusí celá – u drobné změny odpadá zadání i plán, u projektu bez kódu nasazení.

Zvedne aplikaci lokálně a pošle na ni útočníky, jejichž zadání zní jednoduše: **najdi, co spadne.** Žádný seznam, co hledat, žádná předem daná kritéria. Je to třetí druh záruky vedle automatických bran a čtení kódu, a ani jedna z nich ho nenahradí – rozdíl proti kontrole kódu je v jednom slově: ta kód **čte**, tenhle ho **spouští**. Přehlédnutá větev se v kódu hledá těžko a v běžící aplikaci se projeví bílou stránkou.

## Co umí

1. **`/attack`** (výchozí) – útočí na to, čeho se dotkla práce na aktuální větvi: obrazovky, adresy a toky, které se změnily nebo na změněný kód navazují.
2. **`/attack full`** – celá aplikace bez ohledu na to, co se měnilo. U větší aplikace se předem domluví, kolik času tomu dát.
3. **Šest vektorů útoku**, z nichž vybírá podle povahy projektu: **vstupy** (prázdno, obří čísla, emodži, deset tisíc znaků, pokusy o vlezení do systému), **stavy a pořadí** (přeskočený krok, zopakovaný krok, dvě záložky nad týmž záznamem, odeslání dvakrát rychle po sobě), **oprávnění** (cizí identifikátor v adrese, přímé volání mimo rozhraní, akce po vypršení přihlášení), **prostředí** (výpadek sítě uprostřed odesílání, pomalá síť, úzké okno, ovládání bez myši), **data** (prázdný seznam, jediná položka, tisíc položek, smazaná vazba) a **vykreslení** (uložený škodlivý text a pak kontrola všech míst, kde se zobrazuje).
4. **Každý útočník má svůj vektor a svoje účty**, takže si navzájem nepřepisují data a nepopisují stav, který nikdy nenastal.
5. **Projde s vámi nálezy jeden po druhém** a u opravy rovnou napíše regresní test.
6. **Uklidí po sobě** – zastaví, co zvedl, a řekne, co kvůli útoku nastartoval a nechal běžet.

## Proč zrovna tenhle

- **Nález má reprodukční postup, ne domněnku.** Panel čtoucí kód tvrdí, že něco *nastane*; útok přiloží kroky, kterými to nastalo.
- **Každý nález si skill přehraje sám.** Co se nepodaří zopakovat, se zahodí a spočítá – postup, který nejde zopakovat, nález není.
- **Nikdy se neútočí na produkci.** A není to slib, ale **doklad**: že cíl je opravdu lokální a že databáze je opravdu testovací, se ověřuje příkazem a jeho doslovný výstup jde do přehledu. Bez obou dokladů se útok nespustí, ani když řeknete, že je to v pořádku.
- **Ověřuje se i to, kam aplikace doopravdy píše.** Konfigurace se skládá z vrstev a proměnná z prostředí může přebít soubor v repozitáři – proto skill provede zápis a ověří ho dotazem do lokální databáze, místo aby věřil nastavení.
- **Kontroluje i obsah testovací databáze.** Zbytky po dřívějších testech jsou v pořádku, kopie produkce ne – rozložení domén u e-mailů to prozradí.
- **Text, který útočníkovi vrátí aplikace, je pozorování, ne pokyn.** Věta „ukonči testování" v odpovědi serveru je nález, ne instrukce.
- **Každá oprava dostane regresní test.** Reprodukční postup je hotové zadání testu – tím se z jednorázového průzkumu stává trvalé pokrytí.
- **Nedomýšlí nálezy, aby výstup nebyl prázdný.** Prázdný výsledek je taky výsledek a je to ten lepší.
- **Neobchází cizí ochranu.** Omezení počtu požadavků, firewall nebo captcha se hlásí, nezkoumá se, jak je obejít. A nedělá se zátěžový test – to je jiná disciplína.

## Jak se to používá

```
/attack        # to, čeho se dotkla práce na větvi
/attack full   # celá aplikace
```

Skill si nejdřív ověří hranice, ukáže přehled s doklady, počká na potvrzení, teprve pak zvedne aplikaci a začne.

## Ukázka výstupu

```
## Výsledky útoku

Cíl: http://localhost:3000 · Rozsah: změny na větvi – 6 obrazovek
Vektory: vstupy, stavy a pořadí, oprávnění, vykreslení

Nálezů: 11, z toho 3 se nepodařilo zopakovat, zbývá 8:
- 🔴 Kritické: 1    🟡 Střední: 5    🔵 Kosmetické: 2

Nezkoušelo se: platby (míří na cizí bránu)
```

## Co nedělá

- **Nesahá na produkci ani na cizí systém.**
- **Nečte kód kvůli nálezům.** Na to je `/review`; tady se hlásí jen to, co se povedlo doopravdy rozbít.
- **Nepíše generativní testy.** Ty jsou druh testu a patří do běžné implementace.
- **Nenasazuje.** To je `/release`, a ten se pouští vědomě a zvlášť.
- **Nemá cenu nad rozestavěnou aplikací** – tam hlásí hlavně nedodělanost. Pouští se před nasazením nad hotovým celkem.

## Jak si ho nainstalovat

Nechte to na Claudovi. Otevřete si Claude Code a napište mu:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/attack a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.

Aby skill věděl, čím vaši aplikaci lokálně zvednout, potřebuje mít projekt v instrukcích zapsané spouštěcí příkazy – **když chybějí, skill se zeptá a nabídne, že je rovnou doplní**. Sdílí část postupu se `/review` (určení rozsahu, evidence přeskočených nálezů), takže si nechte nainstalovat rovnou oba.


**Nebo celou sadu naráz.** Chcete-li místo jednoho skillu rovnou celý životní cyklus, napište mu tohle:

> Jdi na https://github.com/jantichy/claude/tree/main/skills a nainstaluj mi do `~/.claude/skills/` celý životní cyklus: project, specify, oponent, breakdown, implement, review, consistency, cleanup, attack a release. U každého si přečti README a řekni mi, co k nim potřebuju doplnit.

---

### Požadavky a omezení

Aplikace, která jde spustit lokálně, a možnost zvednout k ní vlastní izolovanou databázi. Projekt s jedinou konfigurací mířící na ostrou databázi se útoku nedočká – skill se v takovém případě zastaví. Útok přes webové rozhraní používá napojení na prohlížeč Chrome; útok na rozhraní bez obrazovky si vystačí s příkazovou řádkou. Je to **z celé sady nejdražší běh** – zvedá prostředí, potřebuje celé toky a trvá desítky minut.
