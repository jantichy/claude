# Předání dál

Čím každý běh skončí a co se stane, když práce nedojde do konce, protože kontext nabyl. Sdílené pravidlo pro skilly životního cyklu – obě vrstvy, osu i kontroly (`~/.claude/standards/rules.md`, *Životní cyklus projektu*).

Řeší dvě vady, které mají týž původ: **běh skončí a není vidět, co dál**, a **běh se vleče do kontextu, ve kterém už nemá běžet**. Obojí stojí na jednom prahu, proto to drží jeden soubor, ne dva.

- [Blok Kudy dál](#blok-kudy-dál)
- [Řetěz, který nepatří do téhle session](#řetěz-který-nepatří-do-téhle-session)
- [Práh kontextu](#práh-kontextu)
- [Přerušení dlouhého průchodu](#přerušení-dlouhého-průchodu)

## Co do tohoto souboru nepatří

Vyhrává první kritérium, které sedí:

1. Je to rozhraní kroku cyklu – co krok dělá, co po něm platí, který soused stojí kde? → `~/.claude/standards/lifecycle.md`
2. Rozhoduje to o **jednom nálezu** – kdo o něm rozhoduje, jak se předkládá, jaké má volby? → `~/.claude/skills/findings.md`
3. Platí to pro práci obecně, ne jen pro konec běhu? → `~/.claude/standards/rules.md`
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

**Každý odchod ze session začíná `/cleanup`, bezpodmínečně.** Odchodem je `/clear`, `/compact`, nová session, zavření okna i `/merge`; odrážka, která kterýkoliv z nich jmenuje, jmenuje `/cleanup` před ním. **Nepodmiňuj ho tím, jestli „zbylo něco nezapsaného“** – právě to zjišťuje až `/cleanup` a skill, který se na to ptá sám sebe, odpoví „ne“ a session zahodí i s tím, co nezapsal. **Mezi `/cleanup` a odchodem nesmí stát jiná práce než `/merge`**, jinak ji zase nikdo nezapíše. `/merge` jde za `/cleanup` a před `/clear`: do hlavní větve má jít i to, co úklid zapsal, a sám nic nezapisuje, takže druhý `/cleanup` nepotřebuje.

Úplný výčet řetězů – jiná pořadí nedávají smysl. **Bez větví `/merge` odpadá**: pracuje se rovnou v hlavní větvi a do ní práci dostane commit a push, které dělá `/cleanup` sám. Řádky, které se liší jen mergem, tam proto splývají:

| Situace | S větví | Bez větví |
|---|---|---|
| další krok patří do téhle session | `/X` | `/X` |
| další krok v nové session, práce na věci pokračuje | `/cleanup` → `/clear` → `/X` | `/cleanup` → `/clear` → `/X` |
| věc je hotová a dál se nic nedělá | `/cleanup` → `/merge` | `/cleanup` |
| věc je hotová a další krok běží nad hlavní větví | `/cleanup` → `/merge` → `/clear` → `/X` | `/cleanup` → `/clear` → `/X` |
| ještě musí v nové session proběhnout kontrola | `/cleanup` → `/clear` → `/X`, merge až po jejím `/cleanup` | `/cleanup` → `/clear` → `/X` |
| přerušený průchod frontou | `/cleanup` → `/clear` → `/next` | `/cleanup` → `/clear` → `/next` |
| rozdělaná úvaha, která se zapsat nedá | `/cleanup` → `/compact` | `/cleanup` → `/compact` |
| konec práce | `/cleanup` → zavřít okno; je-li větev hotová, `/merge` před tím | `/cleanup` → zavřít okno |

**Který sloupec platí, rozhoduje ověřitelný stav, ne dojem:** stojí-li session na jiné než hlavní větvi (`git branch --show-current`), platí *S větví*. Odrážka ve skillu, která jmenuje `/merge`, ho proto vždy podmiňuje tím, že práce na větvi stojí.

```
- `/cleanup`, pak `/clear`, a `/consistency` až v nové session – kontext je na <N>k
- `/cleanup`, pak `/merge` – větev je hotová
- `/cleanup`, pak `/merge`, pak `/clear`, a `/next` až v nové session v `<container>/main` – větev je hotová
```

**Kdy krok do téhle session nepatří** – stačí jedno:

| Důvod | Proč |
|---|---|
| **Kontext je nad prahem** | viz *Práh kontextu* níž |
| **Je to posudek toho, co tahle session právě vyrobila** | session, která návrh obhajovala, je na něj zaujatá a nález odmítne snáz (`~/.claude/standards/rules.md`, *Dlouhá session je dražší než dvě krátké*). Tenhle důvod platí vždy, nezávisle na běhu – `/oponent` nad dokumentem, který krok osy právě napsal, nebo `/review` za `/implement` –, takže ho skill píše do své odrážky rovnou celým řetězem |
| **Krok nedědí nic z rozmyšleného tady** | soubory si nová session načte znovu a levně; platí se jen kontext rozpravy, a ten ten krok nepotřebuje |

**Řekni, kde ta práce leží.** `/clear` vyprázdní konverzaci v běžící session, ale **neukončí ji** – pracovní adresář zůstane ten samý, takže po něm nikam přecházet netřeba a odrážka to nemá komplikovat. Co odrážka **má** nést, je jméno adresáře, kde práce leží, stojí-li projekt ve worktree layoutu (`~/.claude/standards/worktree.md`): jeden pracovní adresář na větev znamená, že v jiném okně je session jinde, a `cd` do správného worktree je pak jediná věc, kterou nová session nemá odkud zjistit. **Po `/merge` je to `<container>/main`**, protože merge pracovní adresář větve smaže a práce nad sloučeným stavem leží v hlavní větvi.

```
- `/cleanup`, pak `/clear`, a `/consistency` až v nové session – zůstáváš v `<cesta k worktree>`, clear adresář nemění
```

**Neprodlužuj to, když krok patří sem.** Řetěz `/cleanup → /clear → nová session` u kroku, který má proběhnout hned, je zbytečná režie: start session stojí načtení `CLAUDE.md` a všech jeho importů. Kontrolní krok nad malou změnou v čerstvé session se pouští tady.

------

## Práh kontextu

Rozhoduje **absolutní velikost kontextu**, ne to, kolik z něj sežral start projektu – na cenu i na to, jak spolehlivě model vidí pravidla z první poloviny okna, se velký startovní kontext nezohledňuje. V projektu, který startuje na 200k, má proto session prostě kratší život.

| Session | Co s tím |
|---|---|
| **do 300k a do 150 volání** | komfortní pásmo, neřeší se nic |
| **nad 300k** nebo **nad 150 volání** | **nabídni přerušení** – dlouhý průchod nedokončuj, nové velké téma neotevírej |
| **nad 400k** | přerušení už **nenabízej, doporuč ho rovnou** i s řetězem; pokračování tady je volba uživatele, ne výchozí stav |

Volání se počítají jen v hlavní session, ne v subagentech, a obojí se měří od poslední kompaktace.

**Překročení prahu ti ohlásí hook `~/.claude/hooks/handoff.py`** – při odeslání zprávy uživatelem vloží do kontextu naměřený údaj, a to u každého prahu jednou. Na jeho hlášku nabídni, respektive doporuč, přerušení hned v té odpovědi, i mimo skill. **Bez hlášky velikost nehádej:** běží-li dlouhý průchod uvnitř jedné odpovědi, kde hook nemá kdy změřit, opři rozhodnutí o délku běhu – panel specialistů s ověřováním a průchod přes dvacet nálezů se do 300k nevejde – a řekni, že je to odhad z rozsahu, ne měřený údaj (`~/.claude/standards/rules.md`, *Hodnotu, kterou čte stroj, nepiš*).

**`/compact` nedoporučuj jako první volbu.** Rozhoduje v něm model, co si zapamatuje, a zahodí právě to, co nikdo nezapsal do souboru. Správná cesta je `/cleanup` → `/clear`, protože po úklidu je pravda v souborech a nová session si ji načte celou. `/compact` zbývá na případ, kdy je rozdělaná jedna úvaha, která se zapsat nedá.

------

## Přerušení dlouhého průchodu

Platí pro každý běh, který **prochází frontu jedna položka po druhé** – nálezy `/review`, `/consistency`, `/attack`, `/oponent`, `/consolidate`, poznatky `/evaluate`, frontu rozhodnutí `/cleanup`, úkoly `/implement`, sporné nálezy `/audit`.

Dva skilly s vlastní frontou tu vědomě **nejsou** – ten, který rozpouští nový zdroj do znalostní báze, a ten, který vytahuje scénáře ze starých konverzací. Jejich fronta bývá krátká a pravidlo, které se nikdy neuplatní, je jen text k údržbě (`decisions.md`, 28. 9. 2026).

**Nabídni přerušení, jakmile kontext překročí práh a ve frontě zbývají aspoň dvě položky.** Ne po každé položce – **jednou za práh**, jinak se z připomínky stane šum a přestane se čítat.

Jednou odrážkou, ne otázkou přes `AskUserQuestion`: kolik položek zbývá, kde kontext je, a že zbytek se uloží celý. Souhlas je uživatelův.

### Kdo zápis dělá

**Řekne-li uživatel ano, zbytek fronty uloží skill [`/break`](break/SKILL.md)** a běh tím končí. Co se zapisuje, kam, jak se zápis ověří a čím odpověď skončí, drží on – tady zůstává jen to, **kdy** se přerušení nabízí. Přerušený skill pak vlastní závěr nevydává: hotový není a závěr `/break` ho nahrazuje.
