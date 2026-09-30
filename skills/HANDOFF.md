# Předání dál

Čím každý běh skončí a co se stane, když práce nedojde do konce, protože kontext nabyl. Sdílené pravidlo pro skilly životního cyklu – obě vrstvy, osu i kontroly (`~/.claude/RULES.md`, *Životní cyklus projektu*).

Řeší dvě vady, které mají týž původ: **běh skončí a není vidět, co dál**, a **běh se vleče do kontextu, ve kterém už nemá běžet**. Obojí stojí na jednom prahu, proto to drží jeden soubor, ne dva.

- [Blok Kudy dál](#blok-kudy-dál)
- [Řetěz, který nepatří do téhle session](#řetěz-který-nepatří-do-téhle-session)
- [Práh kontextu](#práh-kontextu)
- [Přerušení dlouhého průchodu](#přerušení-dlouhého-průchodu)

## Co do tohoto souboru nepatří

Vyhrává první kritérium, které sedí:

1. Je to rozhraní kroku cyklu – co krok dělá, co po něm platí, který soused stojí kde? → `~/.claude/skills/LIFECYCLE.md`
2. Rozhoduje to o **jednom nálezu** – kdo o něm rozhoduje, jak se předkládá, jaké má volby? → `~/.claude/skills/FINDINGS.md`
3. Platí to pro práci obecně, ne jen pro konec běhu? → `~/.claude/RULES.md`
4. Nic z toho → sem

------

## Blok Kudy dál

**Každý běh skončí blokem `**Kudy dál**` a ten je úplně poslední věc v odpovědi** – stojí **za** závěrečným verdiktem. Verdikt tvrdí, jestli je věc hotová; tenhle blok říká, co se s tím dělá. Jsou to dvě různé věci a slévat je do jedné věty znamená, že navigace zůstane u jednoduchých případů a u složitých se vypustí.

**Tvar:** popisek `**Kudy dál**`, pod ním odrážky, **jedna cesta jedna odrážka na samostatném řádku**. Úsečně, bez odůvodňujících odstavců.

```
**Kudy dál**

- <nejpravděpodobnější a nejpotřebnější další krok>
- <volitelně před tím: krok, který smí předcházet, ale nezbytný není>
- <další rovnocenná cesta, existuje-li>
```

**Pravidla, podle kterých se ten seznam skládá:**

- **První odrážka je ta jedna nejpotřebnější cesta**, ne výčet. Vede-li dál jediný rozumný krok, ať je v bloku jediná odrážka.
- **Rovnocenné možnosti vypiš všechny**, každou vlastní odrážkou. Nevybírej za uživatele tam, kde se vybrat nedá.
- **Volitelný předkrok stojí pod tím nezbytným**, ne nad ním, a je označený jako volitelný. Typicky `/oponent` nad rozsáhlým dokumentem: smí předcházet, ale nezbytný není, a kdyby stál první, vypadá jako povinnost.
- **Blok nikdy není prázdný.** Nevede-li dál nic, řekne se to i s důvodem – „tady osa cyklu v tomhle projektu končí, protože se nenasazuje“ je platná odrážka, mlčení ne.
- **Neptej se na to přes `AskUserQuestion`.** Je to doporučení, ne rozhodnutí, které by běh potřeboval, aby mohl skončit – a otázka na konci hotového běhu nutí uživatele kliknout, i když chtěl jen vidět, že je hotovo. Kde otázka na konci dnes je, zruší se.

**Proč to nese verdikt nedostatečně:** verdikt má předepsaná dvě znění a v hotovém z nich bývá „můžeš na `/breakdown`“. To funguje, dokud je ten další krok jeden a patří do téhle session. Jakmile jsou dva, nebo jakmile se mezi ně vejde ukončení session, věta to neunese a navigace z ní tiše vypadne.

------

## Řetěz, který nepatří do téhle session

**Odrážka, jejíž krok nemá běžet v téhle session, nesmí být jen jméno skillu.** Vypíše se celý řetěz včetně ukončení session, jinak si ho uživatel spustí tady – a přesně to je chyba, kterou to má odchytit.

```
- `/cleanup`, pak `/clear`, a `/consistency` až v nové session – kontext je na <N>k
- `/cleanup`, pak `/merge` – větev je hotová
```

**Kdy krok do téhle session nepatří** – stačí jedno:

| Důvod | Proč |
|---|---|
| **Kontext je nad prahem** | viz *Práh kontextu* níž |
| **Je to posudek toho, co tahle session právě vyrobila** | session, která návrh obhajovala, je na něj zaujatá a nález odmítne snáz (`~/.claude/RULES.md`, *Dlouhá session je dražší než dvě krátké*) |
| **Krok nedědí nic z rozmyšleného tady** | soubory si nová session načte znovu a levně; platí se jen kontext rozpravy, a ten ten krok nepotřebuje |

**Řekni, kde ta práce leží.** `/clear` vyprázdní konverzaci v běžící session, ale **neukončí ji** – pracovní adresář zůstane ten samý, takže po něm nikam přecházet netřeba a odrážka to nemá komplikovat. Co odrážka **má** nést, je jméno adresáře, kde práce leží, stojí-li projekt ve worktree layoutu (`~/.claude/WORKTREE.md`): jeden pracovní adresář na větev znamená, že v jiném okně je session jinde, a `cd` do správného worktree je pak jediná věc, kterou nová session nemá odkud zjistit.

```
- `/cleanup`, pak `/clear`, a `/consistency` až v nové session – zůstáváš v `<cesta k worktree>`, clear adresář nemění
```

**Neprodlužuj to, když krok patří sem.** Řetěz `/cleanup → /clear → nová session` u kroku, který má proběhnout hned, je zbytečná režie: start session stojí načtení `CLAUDE.md` a všech jeho importů. Kontrolní krok nad malou změnou v čerstvé session se pouští tady.

------

## Práh kontextu

Rozhoduje **absolutní velikost kontextu**, ne to, kolik z něj sežral start projektu – na cenu i na to, jak spolehlivě model vidí pravidla z první poloviny okna, se velký startovní kontext nezohledňuje. V projektu, který startuje na 200k, má proto session prostě kratší život.

| Kontext | Co s tím |
|---|---|
| **do 300k** | komfortní pásmo, neřeší se nic |
| **nad 300k** | **nabídni přerušení** – dlouhý průchod nedokončuj, nové velké téma neotevírej |
| **nad 400k** | přerušení už **nenabízej, doporuč ho rovnou** i s řetězem; pokračování tady je volba uživatele, ne výchozí stav |

**Velikost kontextu nehádej.** Není-li po ruce údaj, který ji říká, opři rozhodnutí o délku běhu – panel specialistů s ověřováním a průchod přes dvacet nálezů se do 300k nevejde – a řekni, že je to odhad z rozsahu, ne měřený údaj (`~/.claude/RULES.md`, *Hodnotu, kterou čte stroj, nepiš*).

**`/compact` nedoporučuj jako první volbu.** Rozhoduje v něm model, co si zapamatuje, a zahodí právě to, co nikdo nezapsal do souboru. Správná cesta je `/cleanup` → `/clear`, protože po úklidu je pravda v souborech a nová session si ji načte celou. `/compact` zbývá na případ, kdy je rozdělaná jedna úvaha, která se zapsat nedá.

------

## Přerušení dlouhého průchodu

Platí pro každý běh, který **prochází frontu jedna položka po druhé** – nálezy `/review`, `/consistency`, `/attack`, `/oponent`, `/consolidate`, poznatky `/evaluate`, frontu rozhodnutí `/cleanup`, úkoly `/implement`, sporné nálezy `/audit`.

Dva skilly s vlastní frontou tu vědomě **nejsou** – ten, který rozpouští nový zdroj do znalostní báze, a ten, který vytahuje scénáře ze starých konverzací. Jejich fronta bývá krátká a pravidlo, které se nikdy neuplatní, je jen text k údržbě (`decisions.md`, 28. 9. 2026).

**Nabídni přerušení, jakmile kontext překročí práh a ve frontě zbývají aspoň dvě položky.** Ne po každé položce – **jednou za práh**, jinak se z připomínky stane šum a přestane se čítat.

Jednou odrážkou, ne otázkou přes `AskUserQuestion`: kolik položek zbývá, kde kontext je, a že zbytek se uloží celý. Souhlas je uživatelův.

### Co se zapisuje

Řekne-li uživatel ano, **zbytek fronty se uloží do `todo.md`, do sekce `## Přerušený běh`** (`~/.claude/STRUCTURE.md`, *`todo.md`*), a teprve pak se běh ukončí.

**Uloží se celý nález, ne jeho jméno.** Nová session nemá kontext, ve kterém nález vznikl, a položka, ze které se nedá rozhodnout, je horší než žádná – tváří se jako zadání a není. U každé zbývající položky proto jde do zápisu:

- **co je špatně** – nález celou větou, ne značkou a ne zkratkou (`~/.claude/RULES.md`, *Interní značky ven nepatří*)
- **čím je doložený** – `basis`, nebo lokace či reprodukční postup, nese-li je schéma toho skillu místo něj
- **závažnost** podle `~/.claude/skills/SEVERITY.md`
- **varianty řešení i s důsledkem každé**, včetně obou záchytných voleb podle `~/.claude/skills/FINDINGS.md` – tedy to, co by se bylo uživatele zeptalo tady
- **cesta a řádek**, kde se to opravuje, a co se tím ještě rozbije
- **co už se v tomhle běhu rozhodlo** o sousedních nálezech, závisí-li na tom volba u tohohle

**Předávej to doslova, neparafrázuj** – parafráze je přesně to místo, kde se ztratí detail, kvůli kterému nález vznikl, a ztratí se tiše, protože shrnutí vypadá úplně (`~/.claude/DELEGATION.md`, *Velké průzkumné úkoly deleguj*).

**Zapiš i to, co se v tomhle běhu už vypořádalo** – jedním řádkem nad položkami, s počtem opravených a zamítnutých. Bez toho nová session neví, jestli má před sebou celou frontu nebo její zbytek, a nemá jak poznat, že nález, který v souborech nenachází, je opravený.

### Co se pak řekne

Závěr běhu zůstane obvyklý – šablona i verdikt. V něm se přiznají **nevypořádané položky**, protože přerušený běh hotový není. Blok `**Kudy dál**` pak nese řetěz:

```
**Kudy dál**

- `/cleanup`, pak `/clear`, a v nové session `/next` – zbývajících <N> nálezů tam leží první
```

**Ověř, že se to uložilo, než to ohlásíš.** Načti sekci zpátky a zkontroluj, že v ní je tolik položek, kolik jich ve frontě zbývalo (`~/.claude/RULES.md`, *Co jsi vygeneroval, přečti zpátky, než to ohlásíš jako hotové*). Ohlášené přerušení s polovinou zapsaných nálezů je tichá ztráta práce – a pozná se až za týden, kdy si na ty nálezy nikdo nevzpomene.
