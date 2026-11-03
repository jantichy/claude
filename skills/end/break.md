# Zápis přerušené práce

Jak `/end` uloží rozdělanou práci, aby ji nová session dokončila **bez kontextu téhle**. Načítá se jen tehdy, když *Fáze 3* skillu rozdělanou práci najde – běžný úklid ho nečte. Kdy se to stane, drží `/end`, *Fáze 3*; tady je, co se zapisuje, kam, v jakém tvaru a jak se to ověří.

Zapisuje se do `docs/todo.md`, sekce `## Přerušený běh`, na kterou v nové session naváže `/continue` (a `/next` ji nabízí jako první): kde práce leží, co jí musí předcházet, co se už udělalo, **každou zbývající položku celou**, co se vyvrátilo a co se v běhu rozhodlo.

Rozdělanou prací je **fronta kteréhokoliv skillu** – nálezy `/review`, úkoly `/implement`, poznatky `/evaluate` – i **práce mimo skill**: rozepsaný návrh, oprava v půli, rozprava, ve které zbývají otázky.

**Přerušení není místo, kde se zbytek fronty „rychle doklepne“.** Co se do přerušení nevypořádalo, zůstane otevřené; navázání dělá `/continue` v nové session.

## Podklady

1. **Kde práce leží:** větev a pracovní adresář z výstupu `prepare.py`. Ve worktree layoutu (`~/.claude/standards/worktree.md`) je to adresář větve, ne `main/` – a právě to nová session jinak nemá odkud zjistit.
2. **Běhový stav** v `.claude/run/` (`~/.claude/skills/skills.md`, *Běhový stav*), hlásí ho `prepare.py` v `ROZDĚLANÁ PRÁCE`. Nese-li přerušený skill frontu tam, je to výchozí podklad – ale **ne úplný**: kontext kolem položek, doporučení a návaznosti bývají jen v konverzaci.
3. **Existující `## Přerušený běh`.** Leží-li v ní zbytek jiného přerušení, nový blok jde pod něj; starý se nepřepisuje, je to cizí rozdělaná práce.

**Sepiš si, co do zápisu půjde – nejdřív celé, teprve pak piš.** Zápis po kouscích vede k tomu, že se to nejpodstatnější dopíše až na upozornění uživatele.

| Co | Odkud | Proč to nová session potřebuje |
|---|---|---|
| **co práci musí předcházet** | co uživatel ohlásil („nejdřív udělám velkou změnu rozhodnutí“) | bez toho se fronta dojde nad stavem, který mezitím neplatí |
| **necommitnuté soubory rozdělané práce** a co v nich je hotové a co rozbité | `NECOMMITNUTO`, konverzace | bez toho nepozná, co z commitu je záměr a co nedodělek |
| **co se už udělalo** | `COMMITY SESSION`, běhový soubor | jinak nepozná, jestli má před sebou celou frontu, nebo zbytek, a opravené hledá znovu |
| **zbývající položky** | běhový soubor a konverzace | je to vlastní předmět zápisu |
| **rozhodnuté, ale nezapracované položky** | sekce `## Rozhodnuto k zapracování` v `todo.md` | odpověď už padla; bez odkazu na ni se nová session zeptá znovu, nebo ji nezapracuje |
| **co se vyvrátilo nebo uzavřelo** | ověření, odpovědi uživatele | jinak se k tomu vrátí a odpracuje to znovu |
| **co se v běhu rozhodlo** | commity, `decisions.md`, konverzace | zbylé položky na tom stojí a varianty u nich se bez toho čtou jinak |
| **u práce mimo frontu** rozepsaný stav, otevřené otázky a další krok | konverzace | fronta nemusí existovat, otázky ano |
| **co zůstalo neprověřené** | závěr přerušeného skillu | vědomá mezera, která by jinak tiše zmizela |

**Ptej se jen na to, co ví jen uživatel** – typicky pořadí a to, co chystá před pokračováním. Všechno ostatní je v souborech a v konverzaci.

## Kam se zapisuje

Do `docs/todo.md`, sekce `## Přerušený běh` – **první sekce souboru** (`~/.claude/standards/structure.md`, *`todo.md`*). Projekt bez `docs/` ji má v kořenovém `todo.md`; neexistuje-li `todo.md` vůbec, založ ho podle režimu umístění projektu jen s touhle sekcí. **Pod sekcí musí stát nadpis `## `** – `/continue` i `/next` čtou sekci až k dalšímu `## `, takže stojí-li zbytek fronty pod blokem bez vlastního nadpisu, sekce ho celý pohltí a odrážky se začnou číst jako součást přerušení. Má-li `todo.md` položky bez nadpisu sekce, založ nad nimi `## Úkoly`. **Operativní projekt** (`- **Struktura:** CLAUDE.md` v bloku metadat) `todo.md` nemá a nezakládá – sekci zapiš do jeho projektového `CLAUDE.md` jako první `## ` pod blokem metadat (`~/.claude/standards/structure.md`, *Operativní projekt: režim `CLAUDE.md`*); `/continue` i `/next` ji tam najdou a všechno, co tenhle soubor říká o `todo.md`, platí pro ten soubor. Před zápisem si načti `~/Context/Text/typography.md`; zápis je český text.

**Ve worktree layoutu se zápis nezrcadlí do `main/`.** Větev je před mergem a sekce v ní leží tam, kde se v práci pokračuje; do hlavní větve se dostane mergem.

## Tvar bloku

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
5. **Rozhodnuté v běhu** – stručně, s odkazem na místo, kde rozhodnutí žije. **Rozhodnuté a nezapracované položky průchodu po kolech se neopisují** – leží v `## Rozhodnuto k zapracování` (`~/.claude/skills/findings.md`, *Průchod jde po kolech*) a blok na ni jen odkáže i s počtem položek; druhá kopie by se s ní rozešla při první zapracované položce.
6. **Jak pokračovat** – poslední odstavec bloku, uvozený **doslova** návěstím `**Jak pokračovat:**`. **Jeho první věta je jediná první akce**, kterou `/continue` provede bez dalšího úsudku: buď skill i s přesným argumentem (`/review branch od začátku`), nebo položka, kterou se začne, jménem z výčtu výš (*„položkou Volba objednatele po zrušení akce“*). Ne „pokračovat v review“, ne výčet dvou možností – co nejde provést jako první krok, tam nepatří. **Musí-li předcházet krok uživatele** (změna rozhodnutí), první akcí je to, čím se pokračuje **po něm** – ten krok stojí v úvodní větě a `/continue` se na něj zeptá sám, než začne. U průchodu po kolech platí pořadí kola: nejdřív zbylé otázky, teprve pak zapracování všeho z `## Rozhodnuto k zapracování`; nezbyla-li otázka, je první akcí právě to zapracování. Za ní: podle čeho se fronta dojde, co udělat s položkou, kterou předcházející krok zneplatní, kdy smazat běhový soubor, tenhle blok a prázdnou sekci, a co zůstalo neprověřené.

**Předávej doslova, neparafrázuj.** Strukturovaný výstup agentů a znění nálezů jdou do zápisu tak, jak jsou; parafráze ztratí právě ten detail, kvůli kterému položka vznikla, a ztratí ho tiše, protože shrnutí vypadá úplně (`~/.claude/standards/delegation.md`, *Velké průzkumné úkoly deleguj*).

**Poučení z chyby zapiš v rozsahu její příčiny, ne jako plošný zákaz.** Selhala-li v běhu jedna třída oprav (vrácený commit, odmítnutá oprava), napiš, která třída to byla a proč – „rozpor dvou odborných pravidel se bral jako jednoznačný“ –, a nech třídění skillu platit pro ostatní. Nová session plní zápis doslova, takže zákaz širší než příčina („bez souhlasu se nic neopravuje“) přebije pravidlo skillu a přinutí ji ptát se i na mrtvý odkaz.

Běhový soubor v `.claude/run/` **nech ležet** a poznač do něj klíčem `interrupted` cestu k zápisu (`"interrupted": "docs/todo.md"`). Podle toho klíče přerušený skill na startu pozná, že autoritou je zápis, ne běhový soubor (`~/.claude/skills/skills.md`, *Běhový stav*), a příští `/end` ho přestane hlásit jako rozdělanou práci. Smaže ho až session, která frontu dojde.

## Ověření a commit

1. **Přečti blok zpátky a spočítej v něm položky** – musí jich být tolik, kolik jich ve frontě zbývalo (`~/.claude/standards/rules.md`, *Co jsi vygeneroval, přečti zpátky, než to ohlásíš jako hotové*). Nesedí-li to, doplň chybějící; nehlas přerušení s polovinou fronty.
2. **Pusť krok kontraktu, který prověřuje dokumentaci** – týž, který *Fáze 7* pouští za commitem úklidu. Projekty mívají kontroly tvaru dokumentace – holé odkazy, kotvy, formát výčtu – a zápis na ně narazí stejně jako každý jiný text. Selže-li na zápisu, oprav zápis, ne kontrolu. Selže-li na rozdělané práci, nic neopravuj – výsledek patří do *Jak pokračovat* jako stav, ve kterém se navazuje. Chybí-li kontrakt, řekni to v závěru.
3. **Commitni jmenovitě soubor se zápisem** (`todo.md`, v operativním projektu `CLAUDE.md`; bez gitu řekni, že se necommitovalo nic) a pushni, je-li remote. Rozdělanou práci ne, tu commitne *Fáze 7* zvlášť. **Zápis se commitne hned, ještě před frontou rozhodnutí** – kdyby úklid uprostřed ptaní spadl nebo ho uživatel zavřel, fronta už je v gitu.

**Pokyn ke spěchu zkracuje odpověď, ne ověření.** Čtení zpátky a commit odcházejícího uživatele nezdrží a ověřený zápis je to, s čím odchází.

**Průchod přerušeného skillu se do `done.md` nezapisuje.** `~/.claude/skills/passes.md` vede jen dokončené běhy a `/release` z nich čte, jestli kontrola proběhla – přerušený běh dokončený není. Zapíše ho až session, která frontu dojde. Řádek průchodu `/end` se píše jako vždy.

## Časté chyby

- **Zápis jde po kouscích a doplňuje se na upozornění.** Napoprvé chybělo doporučení u položek, vyvrácené nálezy, rozhodnuté body a úvodní věta s prioritou a větví – a uživatel o ně musel říct dvakrát. Inventura je proto celá dřív než první zápis.
- **Blok nemá nadpis nebo *Jak pokračovat* nezačíná jednou akcí.** `/continue` pak neví, kde blok končí a čím začít, a místo navázání se ptá – tedy přesně to zdržení, kvůli kterému vznikl.
- **Položka nese jen jméno, ne kontext.** „Nález 8 – delete\* při LINK“ nová session nerozhodne; potřebuje selhání, místo, varianty a doporučení.
- **Zapomene se, co předchází.** Chystá-li uživatel změnu, která frontu zreviduje, musí stát v první větě – jinak se fronta dojde nad stavem, který už neplatí.
- **Zápis neprojde kontrolou projektu.** Holé odkazy na kapitolu rozhodnutí v zápisu shodily test tvaru dokumentace; proto se pouští kontrakt, ne jen čtení zpátky.
