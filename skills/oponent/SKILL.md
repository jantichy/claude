---
name: oponent
description: Skill se použije, když uživatel zadá "/oponent", nebo chce nezávislý oponentský posudek na dokument, který spolu psali – strategii, pozicování, PRD, koncepci, cenotvorbu, datový model, analytickou dokumentaci. Pohled čerstvýma očima z několika úhlů: co nedává smysl, co si odporuje, co nebude fungovat, co chybí.
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, WebSearch, WebFetch]
---

# Oponent

## Co skill dělá

Uživatel má hotový nebo rozpracovaný dokument, na kterém jste spolu dlouho pracovali. Právě proto na něj **nemáš nezávislý pohled** – spoluautor nevidí, co v dokumentu chybí, protože to má v hlavě, a nevidí, co je slabé, protože si to sám odsouhlasil.

Skill proto pošle na dokument **subagenty bez kontextu téhle session**, každého z jiného úhlu, a jejich nálezy s uživatelem probere jeden po druhém.

## Co skill nedělá

- **Není to kontrola kódu.** Na kód je `/code-review`.
- **Není to kontrola proti standardům.** Na soulad s `~/Dev/context/*` je `/review`.
- **Není to audit vnitřní konzistence projektu.** Na to je `/consistency`. Oponent se ptá „je to dobře vymyšlené?“, ne „sedí to na sebe?“.
- **Nic sám nemění.** Výchozí režim je diskuze. Změny až po schválení jednotlivých nálezů.
- **Nechválí.** Věci, které jsou v pořádku, se nevypisují.

## Vztah k ostatním skillům

| Otázka | Skill |
|---|---|
| Je ten kód správně? | `/code-review` |
| Odpovídá to mým doménovým standardům? | `/review` |
| Nesedí si něco v projektu navzájem? | `/consistency` |
| **Je to vůbec dobře vymyšlené a bude to fungovat?** | **`/oponent`** |
| Je všechno ze session zapsané? | `/cleanup` |

------

## Fáze 0 – Co se oponuje

**Předmět posudku.** Uživatel ho může zadat jako argument (`/oponent docs/requirements.md`, `/oponent 01 až 04`, `/oponent pozicování`). Když ho nezadá, **nabídni mu, co jsi našel** – projdi projekt, vypiš kandidáty (dokumenty, na kterých se v poslední době pracovalo) a nech ho vybrat přes `AskUserQuestion`.

**Zkontroluj, že to má smysl oponovat:**

- **Je to kód?** → přesměruj na `/code-review` a zastav se.
- **Je to rozpracované torzo?** → zeptej se, jestli má smysl oponovat teď, nebo počkat. Posudek na kostru vygeneruje hlavně nálezy „chybí obsah“, což uživatel ví.
- **Je toho moc?** Nad zhruba pět dokumentů nebo řádově stovky kB se posudek rozmělní. Zeptej se, co je jádro, a oponuj to.

**Načti kontext, který posudek potřebuje:** projektový `CLAUDE.md`, `docs/rules.md` (principy, proti kterým se v projektu rozhoduje) a `docs/decisions.md` (co už bylo rozhodnuto a proč). Bez toho subagenti navrhnou znovu to, co už bylo vědomě zamítnuto – a to je nejotravnější druh oponentury.

------

## Fáze 1 – Volba úhlů pohledu

**Nepouštěj tři stejné kritiky.** Redundantní subagenti najdou třikrát totéž. Diverzita úhlů chytá selhání, která opakování nechytí.

Vyber **tři až pět úhlů podle povahy dokumentu** z katalogu níž – nebo si vymysli vlastní, sedne-li to líp. Výběr **vypiš uživateli** předtím, než je pustíš, ať může jeden vyměnit.

| Úhel | Ptá se |
|---|---|
| **Vnitřní rozpor** | Tvrdí dokument někde něco, co jinde popírá? Sedí čísla, výčty a souhrny s obsahem? Nezůstal tam zbytek po zrušeném konceptu? |
| **Skeptik** | Proč to nebude fungovat? Který předpoklad je nejslabší a co se stane, když neplatí? |
| **Cílová skupina** | Čte to očima persony, které se to týká. Rozumí tomu? Koupí si to? Co ji odradí? Co v tom nenajde? |
| **Ekonomika** | Sedí čísla? Break-even, cena, kapacita, náklady na provoz. Co se stane při desetinásobku a při desetině? |
| **Právo a compliance** | Osobní údaje, spotřebitelské právo, daně, autorská práva, smluvní závazky. Co je napsané tak, že to nejde dodržet? |
| **Provoz** | Kdo to bude reálně dělat, jak často a co se stane, když to neudělá? Co vyžaduje ruční zásah a neškáluje? |
| **Konkurence a trh** | Existuje to už? Čím se to liší? Proč by si někdo vybral tohle? |
| **Co chybí** | Ne co je špatně, ale co v dokumentu vůbec není a mělo by být. Nejcennější a nejhůř se hledá. |
| **Technická proveditelnost** | Dá se to postavit tak, jak je to popsané? Kde je skryté riziko? |
| **Hraniční případy** | Co se stane, když je vstup prázdný, obojí najednou, uprostřed zrušené, dvakrát za sebou? |

**Pravidlo:** úhel *Vnitřní rozpor* a *Co chybí* ber jako povinné, ať je dokument jakýkoliv. Zbytek podle povahy.

------

## Fáze 2 – Nezávislé posudky

Pusť subagenty **paralelně, jedním voláním s víc tool calls**. Každý dostane vlastní úhel a **žádný kontext z téhle session** – to je celý smysl.

Zadání pro každého (doplň úhel, cesty a projektový kontext):

```
Jsi nezávislý oponent. Nemáš žádný kontext z předchozích rozhovorů – máš jen ty soubory,
které si přečteš. Autor dokumentu tě neslyší, takže nemá smysl být ohleduplný.

DOKUMENT: <absolutní cesty>
KONTEXT PROJEKTU (přečti, ale neoponuj to): <CLAUDE.md, docs/rules.md, docs/decisions.md>

TVŮJ ÚHEL POHLEDU: <úhel a jeho otázky z katalogu>

Přečti dokument celý a hledej výhradně ze svého úhlu. Ostatní úhly pokrývají jiní
oponenti – nepřebíhej k nim.

U KAŽDÉHO NÁLEZU UVEĎ:
- **Kde** – soubor a sekce, ideálně citace věty, které se to týká
- **Co** – jednou větou, co je špatně
- **Proč to vadí** – konkrétní důsledek, ne obecná obava. „Nebude to škálovat" je nic;
  „při 20 000 účastnících vyjde ruční párování na 300 hodin práce" je nález.
- **Návrh** – dvě až tři konkrétní varianty řešení, ne jedna. Nemáš-li řešení, řekni to
  a označ nález jako otázku k rozhodnutí.
- **Závažnost** – zásadní / důležité / drobnost

PRAVIDLA:
- Co je v pořádku, nepiš. Žádné shrnutí kladů, žádné „jinak je to dobře promyšlené".
- Nenavrhuj to, co je v docs/decisions.md už vědomě zamítnuté. Přečti si to nejdřív.
  Výjimka: myslíš-li si, že to rozhodnutí bylo chybné, řekni to výslovně jako revizi
  rozhodnutí a zdůvodni, který jeho předpoklad neplatí.
- Neopírej nález o neověřené tvrzení. Stojí-li na faktu, ověř ho.
- Nešetři kritikou. Ale kritizuj dokument, ne autora.
- Nenavrhuj přeformulování textu kvůli stylu – od toho tu nejsi.

Do žádného souboru nezapisuj.
```

**Volitelně rešerše.** Má-li úhel smysl podepřít fakty zvenku (konkurence, ceny, právní úprava, technická omezení), dej tomu subagentovi výslovně svolení hledat na webu. U ostatních to zakaž, ať neutíkají od dokumentu.

------

## Fáze 3 – Konsolidace

Než cokoliv předložíš, nálezy **zpracuj**:

1. **Slouč duplicity.** Když stejnou věc našli dva oponenti z různých úhlů, je to jeden nález – ale poznamenej, že ho našli dva. Je to signál závažnosti.
2. **Vyřaď falešné.** Nález stojící na nepochopení kontextu, který subagent neměl, zahoď – ale **jen když si jsi jistý**. Když ne, nech ho a předlož ho s poznámkou. Tichý filtr je přesně to, co má tenhle skill obcházet.
3. **Vyřaď už rozhodnuté.** Nález, který navrhuje zamítnutou variantu bez nového argumentu, zahoď a **řekni, kolik jsi jich zahodil a proč** – ne potichu.
4. **Seřaď podle závažnosti**, ne podle pořadí v dokumentu.
5. **Vypiš přehled** – všechny nálezy jednou větou, očíslované, se závažností. Uživatel musí vidět, co ho čeká, než se ho začneš ptát.

------

## Fáze 4 – Průchod nálezy

Podle `~/.claude/RULES.md` (*Ptej se postupně, ne všechno najednou*) projdi nálezy **jeden po druhém**, od nejzávažnějšího.

U každého nejdřív vypiš:

```
---
[N/celkem] NÁZEV NÁLEZU        (zásadní / důležité / drobnost)
Našel: <úhel, případně „2 oponenti nezávisle">

Kde: <soubor, sekce, citace>
Co: <jednou větou>
Proč to vadí: <konkrétní důsledek>

Varianty řešení:
A) <…> – důsledek
B) <…> – důsledek
C) Nechat být – <proč to může být v pořádku>

Doporučuji: <jedna z nich a proč>
```

Pak se zeptej **přes `AskUserQuestion`** – jedno volání na jeden nález, `header` `Nález N/celkem`, volby jsou **konkrétní varianty řešení**, ne „Opravit / Odložit / Přeskočit“ – u oponentského nálezu existuje víc věcných cest a „opravit“ neříká kterou. Vždy nech mezi volbami i **Nechat být**.

(V `/consistency` a `/review` je to naopak správně: tam má nález jedno navrhované řešení a volby jsou *Opravit / Odložit / Přeskočit*, u hromadných nálezů navíc *Rozbalit*.)

**Zpracování odpovědi:**

- **Přijato** → zapracuj do dokumentu rovnou a zapiš rozhodnutí do `docs/decisions.md`.
- **Zamítnuto** → zapiš do `docs/decisions.md` **taky**, i s důvodem. Zamítnutý nález je cenný záznam – brání tomu, aby ho příští oponentura našla znovu jako nový.
- **Odloženo** → do `docs/todo.md`, ve tvaru podle `~/.claude/RULES.md`, *Odložené věci pojmenuj a zaparkuj*.

**Odbočky.** Uživatel u nálezu často rozvine úvahu, která zasáhne jinam. Tu úvahu zapiš celou – bývá cennější než původní nález. Pak se vrať k seznamu a pokračuj; sám si hlídej, které nálezy zbývají.

------

## Fáze 5 – Závěr

**Opakované spuštění.** Skill je určený k opakování nad revidovanou verzí. Když ho uživatel spustí znovu:

- **Nález, který se vrátil**, znamená, že se neopravil, jen přeformuloval. Řekni to výslovně.
- **Míň nálezů** znamená, že se to lepší. **Víc** znamená, že revize otevřela nové problémy – taky to řekni.

Ve verdiktu:

```
## Oponentura hotová

**Předmět:** <dokumenty>
**Úhly:** <seznam>

**Nálezy:** N celkem – X zásadních, Y důležitých, Z drobností
- Zapracováno: N
- Zamítnuto: N (zapsáno do decisions.md i s důvodem)
- Odloženo: N (todo.md)
- Vyřazeno před předložením: N (<proč>)

**Nejzávažnější, co z toho vzešlo**
- <jedna až tři věty – co to reálně změnilo>
```

Zakonči jednou z těchto vět:

- `Všechny nálezy jsou vypořádané, dokument je po oponentuře.`
- `Vypořádané nejsou: <konkrétní seznam>.`

Nikdy nekonči tím, že je dokument „v dobrém stavu“ – to není verdikt oponenta, ale autora.
