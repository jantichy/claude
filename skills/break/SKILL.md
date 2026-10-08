---
name: break
description: Skill se použije, když uživatel zadá "/break", nebo chce rozdělanou práci přerušit uprostřed a ukončit session – "přeruš to", "zapiš, co zbývá, a skončíme", "pokračujeme v nové session" –, anebo když běh jiného skillu narazí na práh kontextu a uživatel přerušení přijme. Zapíše do docs/todo.md, sekce Přerušený běh, všechno, co nová session potřebuje, aby v práci pokračovala bez ztráty čehokoliv podstatného: kde práce leží, co předchází, co se už udělalo, každou zbývající položku i s kontextem, variantami a doporučením, co se vyvrátilo a co se rozhodlo. Zápis přečte zpátky, ověří a commitne a skončí doporučením /cleanup, /clear a /continue, který v nové session na zápis rovnou naváže. Funguje pro frontu kteréhokoliv skillu i pro práci mimo skill. Na rozdíl od /cleanup, který vytěžuje dohody a nevypořádaná témata celé session, tenhle skill ukládá rozdělanou práci jako frontu k navázání; na rozdíl od /continue nic neprovádí, jen připraví, čím se naváže.
allowed-tools: [Read, Glob, Grep, Bash, Edit, Write, AskUserQuestion]
---

# Break

## Co skill dělá

Přeruší rozdělanou práci a uloží ji tak, aby ji nová session dokončila **bez kontextu téhle**. Zapisuje do `docs/todo.md`, sekce `## Přerušený běh`, na kterou v nové session naváže `/continue` (a `/next` ji nabízí jako první): kde práce leží, co jí musí předcházet, co se už udělalo, **každou zbývající položku celou**, co se vyvrátilo a co se v běhu rozhodlo. Pak zápis přečte zpátky, pustí kontrakt příkazů projektu, commitne a skončí blokem *Kudy dál*.

Rozdělanou prací je **fronta kteréhokoliv skillu** – nálezy `/review`, úkoly `/implement`, poznatky `/evaluate` – i **práce mimo skill**: rozepsaný návrh, oprava v půli, rozprava, ve které zbývají otázky. Režimy nemá.

## Co skill nedělá

- **Nevytěžuje session.** Dohody, poznatky a nevypořádaná témata zapisuje `/cleanup`, který běží **za ním** – `/break` ukládá jen rozdělanou práci jako frontu k navázání a `/cleanup` ji pak nepřebírá ani nepřepisuje.
- **Nepokračuje.** Navázání dělá `/continue` v nové session – je to druhá strana téhož předání a čte přesně to, co tenhle skill zapíše. Přehled všeho rozdělaného včetně tohohle sestavuje `/next`.
- **Nerozhoduje ani neopravuje.** Co se do přerušení nevypořádalo, zůstane otevřené – přerušení není místo, kde se zbytek fronty „rychle doklepne“.
- **Nehlídá práh kontextu.** Ten drží `~/.claude/skills/handoff.md`, *Práh kontextu*, a ohlašuje hook `handoff.py`; skill s frontou podle něj přerušení nabídne a na souhlas zavolá tenhle skill.

## Fáze 0 – Příprava

Společný začátek drží `~/.claude/skills/preflight.md`; body 4 a 5 odpadají a necommitnuté změny z bodu 3 nejsou důvod k otázce – bývají samy rozdělanou prací a jdou do zápisu. Navíc:

1. **Urči, kde práce leží:** větev (`git branch --show-current`) a pracovní adresář. Ve worktree layoutu (`~/.claude/standards/worktree.md`) je to adresář větve, ne `main/` – a právě to nová session jinak nemá odkud zjistit.
2. **Najdi běhový stav** v `.claude/run/` (`~/.claude/skills/skills.md`, *Běhový stav*). Nese-li přerušený skill frontu tam, je to výchozí podklad – ale **ne úplný**: kontext kolem položek, doporučení a návaznosti bývají jen v konverzaci.
3. **Podívej se, jestli `## Přerušený běh` už existuje.** Leží-li v ní zbytek jiného přerušení, nový blok jde pod něj; starý se nepřepisuje, je to cizí rozdělaná práce. **Nemá-li starý blok nadpis `### `** (zápis ze starší podoby skillu), nech ho, jak je, a ohlas uživateli, že `/continue` v sekci neodliší, kde končí – takový zápis je přechodný a zmizí, až se jeho fronta dojde.
4. **Prošla-li session kompaktací**, načti nejdřív transcript (`~/.claude/skills/session.md`). Shrnutí z kompaktace je přesně ta parafráze, ve které se detail ztrácí.

## Fáze 1 – Inventura rozdělané práce

Sepiš si, co do zápisu půjde – **nejdřív celé, teprve pak piš**. Zápis po kouscích vede k tomu, že se to nejpodstatnější dopíše až na upozornění uživatele.

| Co | Odkud | Proč to nová session potřebuje |
|---|---|---|
| **co práci musí předcházet** | co uživatel ohlásil („nejdřív udělám velkou změnu rozhodnutí“) | bez toho se fronta dojde nad stavem, který mezitím neplatí |
| **necommitnuté soubory rozdělané práce** a co v nich je hotové a co rozbité | `git status --porcelain`, konverzace | bez toho nepozná, co z commitu je záměr a co nedodělek |
| **co se už udělalo** | `git log` běhu, běhový soubor | jinak nepozná, jestli má před sebou celou frontu, nebo zbytek, a opravené hledá znovu |
| **zbývající položky** | běhový soubor a konverzace | je to vlastní předmět zápisu |
| **co se vyvrátilo nebo uzavřelo** | ověření, odpovědi uživatele | jinak se k tomu vrátí a odpracuje to znovu |
| **co se v běhu rozhodlo** | commity, `decisions.md`, konverzace | zbylé položky na tom stojí a varianty u nich se bez toho čtou jinak |
| **u práce mimo frontu** rozepsaný stav, otevřené otázky a další krok | konverzace | fronta nemusí existovat, otázky ano |
| **co zůstalo neprověřené** | závěr přerušeného skillu | vědomá mezera, která by jinak tiše zmizela |

**Ptej se jen na to, co ví jen uživatel** – typicky pořadí a to, co chystá před pokračováním. Všechno ostatní je v souborech a v konverzaci.

## Fáze 2 – Zápis

Do `docs/todo.md`, sekce `## Přerušený běh` – **první sekce souboru** (`~/.claude/standards/structure.md`, *`todo.md`*). Projekt bez `docs/` ji má v kořenovém `todo.md`; neexistuje-li `todo.md` vůbec, založ ho podle režimu umístění projektu jen s touhle sekcí. Před zápisem si načti `~/Dev/context/text/typography.md`; zápis je český text.

**Každé přerušení je samostatný blok pod nadpisem `### <práce> – přerušeno <YYYY-MM-DD>`** (datum z `date +%F`), třeba `### /review branch – přerušeno 2026-10-08`. Nadpis je hranice bloku, podle které `/continue` pozná, kolik přerušení v sekci leží a kde které končí; bez něj se dva bloky pod sebou slijí v jeden.

**Pořadí bloku je pevné**, protože nová session ho čte shora a musí se rozhodnout dřív, než dočte:

1. **Úvodní věta s prioritou:** že jde o rozdělanou práci, která se dokončuje **jako první**, ve které větvi a v jakém pracovním adresáři leží a v jakém pořadí se pokračuje – předcházející krok, pak fronta, pak teprve cokoliv dalšího.
2. **Co přerušilo a co se udělalo:** který skill nebo práce, kdy (`date +%F`), proč přerušeno, počty a **commit u každé vypořádané položky**. K tomu necommitnuté soubory rozdělané práce, každý s tím, co v něm je hotové a co rozbité.
3. **Zbývající položky**, každá jednou odrážkou a **celá**:
   - co je špatně, celou větou – bez interních značek, které uživatel nikdy neviděl (`~/.claude/standards/rules.md`, *Interní značky ven nepatří*)
   - čím je to doložené a kde to je – soubor a místo; **čísla řádků se po zápisech posunou**, proto u nich stojí, že se hledá podle textu
   - závažnost podle `~/.claude/skills/severity.md`, je-li to nález
   - **varianty i s důsledkem každé**, u nálezu včetně obou záchytných voleb podle `~/.claude/skills/findings.md`; úkol nebo otevřená otázka mají jen své varianty
   - **doporučení i s důvodem** – to, co by se uživateli řeklo tady; bez něj nová session doporučuje od nuly a jinak. Nevzniklo-li ještě, protože se položka nepředložila, sestav ho, jak by ho skill předložil – je to příprava, ne rozhodnutí. Chybí-li k němu podklad, napiš, co chybí, a nevymýšlej ho
   - návaznost na to, co se v běhu rozhodlo, i na sousední položky
4. **Vyvrácené a uzavřené** – každé s tím, o co se vyvrácení opírá, a s vedlejším postřehem, zbyl-li.
5. **Rozhodnuté v běhu** – stručně, s odkazem na místo, kde rozhodnutí žije.
6. **Jak pokračovat** – poslední odstavec bloku, uvozený **doslova** návěstím `**Jak pokračovat:**`. **Jeho první věta je jediná první akce**, kterou `/continue` provede bez dalšího úsudku: buď skill i s přesným argumentem (`/review branch od začátku`), nebo položka, kterou se začne, jménem z výčtu výš (*„položkou Volba objednatele po zrušení akce“*). Ne „pokračovat v review“, ne výčet dvou možností – co nejde provést jako první krok, tam nepatří. **Musí-li předcházet krok uživatele** (změna rozhodnutí), první akcí je to, čím se pokračuje **po něm** – ten krok stojí v úvodní větě a `/continue` se na něj zeptá sám, než začne. Za ní: podle čeho se fronta dojde, co udělat s položkou, kterou předcházející krok zneplatní, kdy smazat běhový soubor, tenhle blok a prázdnou sekci, a co zůstalo neprověřené.

**Předávej doslova, neparafrázuj.** Strukturovaný výstup agentů a znění nálezů jdou do zápisu tak, jak jsou; parafráze ztratí právě ten detail, kvůli kterému položka vznikla, a ztratí ho tiše, protože shrnutí vypadá úplně (`~/.claude/standards/delegation.md`, *Velké průzkumné úkoly deleguj*).

**Ve worktree layoutu se zápis nezrcadlí do `main/`.** Větev je před mergem a sekce v ní leží tam, kde se v práci pokračuje; do hlavní větve se dostane mergem.

Běhový soubor v `.claude/run/` **nech ležet** a poznač do něj, že je přerušený a kde je zápis. Smaže ho až session, která frontu dojde.

## Fáze 3 – Ověření

1. **Přečti blok zpátky a spočítej v něm položky** – musí jich být tolik, kolik jich ve frontě zbývalo (`~/.claude/standards/rules.md`, *Co jsi vygeneroval, přečti zpátky, než to ohlásíš jako hotové*). Nesedí-li to, doplň chybějící; nehlas přerušení s polovinou fronty.
2. **Pusť kontrakt příkazů projektu** (`## Kontrakt příkazů` v jeho `CLAUDE.md`). Projekty mívají kontroly tvaru dokumentace – holé odkazy, kotvy, formát výčtu – a zápis na ně narazí stejně jako každý jiný text. Selže-li na zápisu, oprav zápis, ne kontrolu. Selže-li na rozdělané práci, nic neopravuj – výsledek patří do *Jak pokračovat* jako stav, ve kterém se navazuje. Chybí-li kontrakt, řekni to a v závěru uveď, že se nic nespustilo.
3. **Commitni jmenovitě `todo.md`** – rozdělanou práci ne, tu commitne `/cleanup`, který jde po tomhle skillu – a pushni, má-li projekt autocommit (`~/.claude/skills/autocommit/autocommit.md`).

**Pokyn ke spěchu zkracuje odpověď, ne ověření.** Čtení zpátky a commit odcházejícího uživatele nezdrží a ověřený zápis je to, s čím odchází.

**Průchod do `done.md` se nezapisuje.** `~/.claude/skills/passes.md` vede jen dokončené běhy a `/release` z nich čte, jestli kontrola proběhla – přerušený běh dokončený není. Zapíše ho až session, která frontu dojde.

## Časté chyby

- **Zápis jde po kouscích a doplňuje se na upozornění.** Napoprvé chybělo doporučení u položek, vyvrácené nálezy, rozhodnuté body a úvodní věta s prioritou a větví – a uživatel o ně musel říct dvakrát. Inventura z *Fáze 1* je proto celá dřív než první zápis.
- **Blok nemá nadpis nebo *Jak pokračovat* nezačíná jednou akcí.** `/continue` pak neví, kde blok končí a čím začít, a místo navázání se ptá – tedy přesně to zdržení, kvůli kterému vznikl.
- **Položka nese jen jméno, ne kontext.** „Nález 8 – delete\* při LINK“ nová session nerozhodne; potřebuje selhání, místo, varianty a doporučení.
- **Zapomene se, co předchází.** Chystá-li uživatel změnu, která frontu zreviduje, musí stát v první větě – jinak se fronta dojde nad stavem, který už neplatí.
- **Zápis neprojde kontrolou projektu.** Holé odkazy na kapitolu rozhodnutí v zápisu shodily test tvaru dokumentace; proto se pouští kontrakt, ne jen čtení zpátky.

## Fáze 4 – Závěr

```
## Přerušeno

- **Práce:** <skill a rozsah, nebo popis práce mimo skill>
- **Leží:** větev `<branch>`, `<pracovní adresář>`
- **Zapsáno:** `<cesta k todo.md>`, `## Přerušený běh` – <N> položek z <N> zbývajících · běhový soubor `<cesta>` ponechán, existuje-li
- **Před pokračováním:** <co musí předcházet, nebo „nic“>
- **Ověřeno:** <příkazy kontraktu a návratové kódy, nebo „kontrakt chybí“> · commit `<hash>`
```

Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo – `~/.claude/standards/rules.md`, *Styl odpovědí*.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Rozdělaná práce je zapsaná a ověřená, můžeš ukončit session.`
- `Rozdělaná práce zapsaná není – brání tomu: <konkrétní seznam>.`

Přerušený skill svůj vlastní verdikt nevydává – hotový není a tenhle závěr ho nahrazuje.

**Kudy dál** je poslední blok odpovědi, za verdiktem – tvar drží `~/.claude/skills/handoff.md`, řádek *přerušený průchod frontou* v tabulce řetězů:

- `/cleanup`, pak `/clear`, a v nové session `/continue` – naváže rovnou na zápis; zůstáváš v `<pracovní adresář>`, clear adresář nemění
