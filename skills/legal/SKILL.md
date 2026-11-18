---
name: legal
description: Skill se použije, když uživatel zadá "/legal" (volitelně s režimem review nebo counter a s dokumentem), nebo chce právní oponenturu smlouvy, NDA, obchodních podmínek, smluvního ustanovení či obchodního rozhodnutí – připomínkovat smlouvu, zjistit, na čem v ní prodělá, co v ní chybí a co neobstojí, anebo vypořádat protinávrh, který vrátila protistrana. Za určenou stranu pošle na dokument panel nezávislých hledisek včetně advokáta protistrany, nálezy nechá vyvrátit, probere je s uživatelem jeden po druhém a teprve pak zapíše revize a komentáře do kopie Wordu, interní pracovní soubor a koncept průvodního mailu. Režim counter porovná vrácenou verzi s odeslanou a posuzuje jen nové a změněné. Není to posudek advokáta a nic neodesílá. Na rozdíl od /oponent, který posuzuje, jestli je dokument dobře vymyšlený, tenhle skill hájí jednu stranu v právním rámci; na rozdíl od /proofread neopravuje jazyk.
argument-hint: [review|counter] [dokument]
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, Skill]
---

# Legal

## Co skill dělá

Právní oponentura smlouvy, obchodních podmínek, jednoho smluvního ustanovení nebo obchodního rozhodnutí **za jednu určenou stranu**. Na dokument pošle panel agentů bez kontextu session, každého z jiného hlediska, a povinně mezi nimi **advokáta protistrany**. Nálezy nechá vyvrátit, s uživatelem je projde jeden po druhém a teprve potom zapíše výstupy: revize a komentáře do kopie dokumentu, interní pracovní soubor a koncept průvodního mailu.

Dva režimy:

- **`review`** (výchozí) – první kolo nad dokumentem, ať je náš, nebo cizí.
- **`counter`** – protinávrh. Protistrana vrátila dokument. Skill ho porovná s verzí, kterou jsme odeslali, roztřídí rozdíly a panel pustí jen na nové a změněné pasáže.

Který režim platí, pozná skill z pracovního souboru vedle dokumentu (*Fáze 0*). Argument ho jen vynutí.

## Co skill nedělá

- **Neposuzuje, jestli je dokument dobře vymyšlený.** To dělá `/oponent`, který žádnou stranu nehájí a nad smlouvou se nepouští. Tenhle skill se ptá, kdo na textu prodělá a co z něj neobstojí.
- **Neopravuje jazyk ani typografii.** Korekturu dělá `/proofread`. Formulace se tu mění jen tam, kde mění význam.
- **Nezařazuje příchozí soubory.** Dokument z `~/Downloads` nejdřív uloží `/depot` na jeho místo. Teprve tam vzniknou výstupy.
- **Nezapisuje do Wordu sám.** Revize, komentáře i porovnání verzí dělá `document-skills:docx`, tenhle skill mu jen předá zadání.
- **Nenahrazuje advokáta a nic neodesílá.** Verdikt to řekne výslovně. Mail zůstane konceptem a revize kopií.
- **Nezmírňuje vyjednávací linii sám.** Každý ústupek je rozhodnutí uživatele.

## Jak je to postavené uvnitř

| Krok | Kdo | Proč zrovna on |
|---|---|---|
| Zařazení dokumentu z `~/Downloads` | `/depot` | Ví, kam který podklad patří. |
| Rámec, volba hledisek, mapa souvislostí, průchod nálezy, koncept mailu | **vlastní** | Hájí určenou stranu proti jejím mantinelům a nikdo jiný to neumí. |
| Posudky panelu | agenti `reader` a `researcher` podle katalogu | Posuzují hotový text a nemají shell, takže do dokumentu nesáhnou. |
| Ověření nálezu opřeného o předpis | agent `Explore` | Doslovné znění předpisu dá jen `curl` (`~/Context/Legal/legal.md`). Webový nástroj `researcher` vrátí jen krátké úryvky. |
| Ověření ostatních nálezů | `reader`, `researcher` | Stejně jako u `/oponent`. |
| Porovnání verzí v `counter`, revize a komentáře do `.docx` | `document-skills:docx` | Umí revize, komentáře, přijetí revizí a kontrolu, že je každá změna revizí. |

**Volání agentů i nástrojů je implementační detail, ne rozhraní.** Závazné je tohle: posuzuje se za stranu určenou v rámci, každý nález před předložením projde ověřením a nic se nezapíše bez rozhodnutí uživatele. Revize nesou jméno určené v rámci a interní pracovní soubor ani ústupky nejdou ven.

## Zásady pro celý průběh

- **Pracovní soubor je interní a nikdy nejde ven.** Nese naše meze, ústupky a pasti. Komentáře ve Wordu a mail čte protistrana, takže z nich nesmí vyčíst nic z toho.
- **Kontext se čte z disku v okamžiku běhu, ne z paměti session.** Platí to pro `decisions.md` projektu, mantinely i předchozí kolo. Snímek v kontextu bývá starší než soubor a posudek pak hájí verzi, kterou už nikdo nemá.
- **Výstupy leží vedle dokumentu a nikde jinde.** Žádné kopie do scratchpadu ani do cizích adresářů, protože podle zapsaného místa se pozná režim příštího kola.
- **Ústupek nikdy nevznikne mimochodem.** Ani ve formulaci revize, ani ve variantě otázky, ani v mailu. Kde hledisko navrhne měkčí znění, předloží se jako varianta k rozhodnutí.

## Fáze 0 – Příprava

**Skill nemusí běžet nad projektem, takže body 1 až 3 z `~/.claude/skills/preflight.md` nahrazuje vlastními předpoklady.** Dokument může ležet v klientské složce, v `~/Documents` i v projektu. Body 4 a 5 odpadají, protože nespouští kód a nepracuje s diffem větve. Závěr přípravy, tedy shrnutí zjištěného, platí.

1. **Dokument.** Vezmi ho z argumentu. Bez argumentu nabídni kandidáty (nejnovější `.docx` a `.pdf` v pracovním adresáři a v `~/Downloads`) přes `AskUserQuestion`. **Leží-li v `~/Downloads`, pusť nejdřív `/depot`** a dál pracuj s cestou, kam ho uložil.
2. **Režim.** Ve složce dokumentu hledej `*.legal.md`. Jde o pracovní soubor předchozího kola a jeho tvar drží [`outputs.md`](outputs.md). Má-li v deníku kol zapsané odeslání a dokument je jiný soubor než ten odeslaný, je to **`counter`**. Bez pracovního souboru je to **`review`**. Má-li pracovní soubor otevřené nálezy (stav `open`), je to přerušený běh a nabídni navázání dřív, než začneš cokoliv počítat znovu (`~/.claude/skills/panel.md`, *Ověřený seznam na disku*).
3. **Kontext.** Projektový `CLAUDE.md` a `docs/decisions.md` nejbližšího projektu nad dokumentem, jsou-li. Z rozhovoru v téhle session vypiš, co se vědomě zamítlo, i s důvodem. Půjde to do bloku *Vědomě zamítnuté* v zadání agentů.
4. **Doména.** Načti si `~/Context/Legal/legal.md` a `~/Context/Business/business.md`. Z něj se prokliknij k mantinelům, které se týkají druhu dokumentu, u mlčenlivosti k `nda.md`. Další preference hledej v `~/Context/Legal/`. Nenajdeš-li pro druh dokumentu mantinely žádné, řekni to: panel pak nemá podle čeho měřit naši stranu a doménová hlediska musí tu mezeru pokrýt.
5. **Zápis.** Leží-li dokument v git repozitáři, výstupy se commitují podle jeho autocommitu. U GitHub remote nejdřív ověř `gh repo view --json visibility`. **Je-li repozitář veřejný, zastav se a zeptej se**, protože pracovní soubor do veřejného repozitáře nesmí. Mimo git se nic necommituje a řekni to.

## Fáze 1 – Rámec posudku

Bez rámce posuzuje každé hledisko za jinou stranu a k jinému dni. Urči:

- **Naši stranu** – kdo jsme ve smlouvě a koho hájíme.
- **Protistranu** – kdo to je, jestli je podnikatel, nebo spotřebitel, a odkud je.
- **Rozhodné právo** – podle volby práva ve smlouvě, jinak podle toho, čím se smlouva bez volby řídí. Chybí-li volba práva, je to první nález.
- **Rozhodný den** – k jakému dni se právo posuzuje, obvykle k podpisu nebo k začátku plnění. Na budoucí účinnost novel pamatuje `~/Context/Legal/legal.md`, *Kdy se to přeověřuje*.
- **Autora revizí** – jméno, pod kterým revize a komentáře půjdou protistraně. Výchozí je `git config --global user.name`. Na agentovi to nenechávej.

Co jde vyčíst z dokumentu a kontextu, vyčti a předlož **najednou jako návrh k potvrzení** přes `AskUserQuestion`. Ptej se jen na to, co zjistit nejde. Potvrzený rámec zapiš do pracovního souboru hned, ne až se zápisem výstupů.

## Fáze 2 – Co se změnilo

*Jen v režimu `counter`.*

1. **Náš návrh.** Z odeslané verze přijmi všechny naše revize. Vznikne text, který jsme protistraně navrhli.
2. **Jejich verze.** Vrátila-li protistrana revize, vypiš je. Pak porovnej **čistý text** jejich verze po přijetí všech revizí s naším návrhem. Tím se chytí i **tichá změna bez revize**, tedy nejzrádnější tah, protože ji nikdo nečte.
3. **Jejich mail.** Vyžádej si průvodní mail protistrany (vložený text, nebo soubor do `~/Downloads`).

Oba kroky porovnání deleguj na `document-skills:docx` s kontraktem výstupu: seznam rozdílů, u každého článek, naše znění, jejich znění a jestli šla změna jako revize. Každý rozdíl pak roztřiď:

| Třída | Co to je | Co s tím |
|---|---|---|
| **převzaté** | přijali náš návrh beze změny | jen se zapíše do deníku kol |
| **mimo meze** | jejich změna jde za mantinel naší strany | jde na panel |
| **vrácená past** | vrátili znění, které jsme minule označili za past | jde na panel, u nálezu stojí odkaz na minulé kolo |
| **nové** | text, který v našem návrhu nebyl, včetně tiché změny | jde na panel, u tiché změny s poznámkou, že nešla jako revize |
| **rozpor mailu a textu** | mail tvrdí něco, co v textu není, nebo naopak | jde rovnou mezi nálezy, je to fakt, ne názor |

**Inventurou pro panel jsou v `counter` jen pasáže ze tříd *mimo meze*, *vrácená past* a *nové*.** Panel nad převzatým textem by znovu otevíral, co už je dohodnuté.

## Fáze 3 – Volba hledisek

Katalog s otázkami, spouštěči a typem agenta drží [`perspectives.md`](perspectives.md). Vybírej podle **vlastnosti dokumentu, ne jeho typu**, tedy podle sloupce *Spouštěč*.

- **Povinně *Advokát protistrany* a *Co chybí*.** První předpoví, co protistrana napadne, odmítne nebo zneužije. Druhé najde, co v textu není a podle dispozitivní úpravy dopadne proti nám.
- **K nim tři až pět dalších**, aspoň jedno z metod a aspoň jedno z domén. Šest hledisek je výchozí počet. Pět stačí u jednoho ustanovení nebo krátkého dokumentu. Sedm dej u mezinárodního prvku nebo nad 15 kB textu.
- ***Vlastní mantinely* ber vždy, když pro druh dokumentu nějaké mantinely existují** (*Fáze 0*, bod 4).
- **Každé hledisko kope za naši stranu**, i to metodické.
- **Volbu dolož.** U každého hlediska jedna věta, co v dokumentu k němu vedlo. Jmenuj aspoň jedno, které jsi vědomě nevzal, a proč.

Panel předlož přes `AskUserQuestion` dřív, než kohokoliv pustíš. Volby jsou *Pustit tak, jak je*, *Vyměnit jedno hledisko* a *Vybrat panel znovu*. Řekni u toho, že běh stojí stovky tisíc tokenů. **Na odpověď se čeká.**

## Fáze 4 – Posudky panelu

Inventuru předmětu, spuštění panelu a jeho model drží `~/.claude/skills/panel.md`, *Inventura předmětu* a *Spuštění panelu*. Inventurou jsou tu články a body dokumentu, jak je dokument sám čísluje. V `counter` jsou to jen pasáže, které vybrala *Fáze 2*.

Zadání pro advokáta protistrany i pro ostatní hlediska drží [`briefs.md`](briefs.md). Typ agenta určuje sloupec *Typ* v katalogu.

## Fáze 5 – Ověření

Deduplikaci, ověřovatele, jejich strop i zadání drží `~/.claude/skills/panel.md`, *Ověření nálezů*. Odchylky:

- **Do zadání ověřovatele jde i rámec** (naše strana, protistrana, rozhodné právo, rozhodný den).
- **Nález, který stojí na znění předpisu nebo rozhodnutí soudu, ověřuje `Explore`** podle doplňku k zadání ověřovatele v [`briefs.md`](briefs.md). Ověřovatel si text stáhne `curl` z primárního zdroje a cituje ho doslova. `researcher` by z webového nástroje dostal jen úryvek nebo parafrázi a potvrdil by tvrzení, které nečetl.
- **Ověřovatel bez doslovné citace pramene vrací NEOVĚŘITELNÉ**, ne POTVRZENO. Nález pak jde do průchodu jako `neověřeno` a ve verdiktu se počítá mezi důvody pro advokáta.

## Fáze 6 – Konsolidace a mapa souvislostí

Pokrytí, pořadí zpracování a přehled drží `~/.claude/skills/panel.md`, *Konsolidace*. Ověřený seznam se ukládá **do pracovního souboru**, do sekce nálezů daného kola. Je to trvalý zápis vedle dokumentu a přežije kompaktaci i konec session. Dokument přitom často leží mimo projekt, kde by `.claude/run/` nemělo kam patřit.

**Před přehledem sestav mapu souvislostí.** Nálezy smlouvy na sobě visí. Smluvní pokuta souvisí se stropem odpovědnosti, definice důvěrné informace s výjimkami a dobou trvání, výpověď se zálohou. U každého nálezu zapiš, se kterými souvisí a jak:

- **podmiňuje** – rozhodnutí o jednom mění druhý,
- **vylučuje** – obě změny naráz nedávají smysl,
- **směna** – ústupek v jednom se dá vyměnit za druhý.

Mapa určí **pořadí témat v průchodu**, aby uživatel rozhodoval související nálezy po sobě. Dá podklad k vyjednávací linii v mailu. Do pracovního souboru jde jako sekce *Mapa souvislostí*.

## Fáze 7 – Průchod nálezy

Průchod drží `~/.claude/skills/findings.md`, *Průchod jde po kolech*, i se záchytnými volbami a hromadným schválením nízkých nálezů. Přerušení při ptaní nabízí `~/.claude/skills/handoff.md`, *Přerušení dlouhého průchodu*. Odchylky:

- **Rozhodnutí se zapisuje do pracovního souboru**, ke stavu nálezu, ne do `docs/todo.md`. Rozhodnutí o smlouvě patří k ní.
- **Věcné varianty jsou znění, ne směr.** Obvykle jde o *Požadovat <naše znění>* a *Ustoupit na <záložní znění>*. Obě znění jsou celá, aby uživatel rozhodoval o textu, který půjde ven. **Silnější varianta stojí první, i když ji panel označil za těžko prosaditelnou.** Jak se k ní protistrana postaví, napiš do kontextu nálezu.
- **Záchytné volby** znamenají: *Neopravovat* = ustanovení zůstane beze změny a důvod jde do pracovního souboru; *Zapsat do todo* = odloží se do `docs/todo.md` projektu, kde dokument leží, a bez projektu do sekce *Odloženo* pracovního souboru.
- **U každého nálezu řekni souvislosti z mapy** a u nálezu s ověřeným pramenem i míru jistoty.
- **Zapracování dělá hlavní session sama.** Je to zápis výstupů v *Fázi 8* nad jedním dokumentem, ne dávky v pomocných worktree.

## Fáze 8 – Zápis výstupů

Bez uživatele a bez otázek, podle rozhodnutí v pracovním souboru. Tvar všech výstupů, jejich jména a umístění drží [`outputs.md`](outputs.md).

1. **Revize.** U `.docx` vznikne **kopie** s revizemi a komentáři pod autorem z rámce. Deleguj to na `document-skills:docx` a předej mu cestu, autora, seznam změn s přesným zněním a texty komentářů. Výsledek ověř jeho validátorem s `--author` a `--original`, aby žádná změna neprošla bez revize. Originál se nemění. U jiného formátu vznikne tabulka v Markdownu.
2. **Komentáře jsou pro protistranu.** Zdůvodňují změnu argumentem, který obstojí před ní. Nesmí v nich být naše meze, záložní znění ani to, co jsme ochotni pustit.
3. **Pracovní soubor.** Dopiš rozhodnutí, navržená a záložní znění, pasti, mapu souvislostí a řádek do deníku kol. Odeslání do deníku napiš až ve chvíli, kdy uživatel řekne, že dokument odeslal. Do té doby tam stojí *připraveno*.
4. **Koncept průvodního mailu.** Shrne hlavní požadované změny a jejich důvody v jazyce korespondence. Neprozradí ústupky ani pořadí, ve kterém jsme ochotni ustupovat. Neodesílá se.
5. **Zpětné čtení.** Otevři vzniklé soubory a ověř: počet revizí odpovídá počtu přijatých změn, každý komentář je ukotvený u textu, v komentářích ani v mailu není nic ze sekcí pracovního souboru, které ven nesmí. Selže-li cokoliv, zastav se a řekni to i s místem.

**Obecná mez.** Vyplynula-li z posudku zásada, která platí i pro příští smlouvu stejného druhu, navrhni ji zapsat do `~/Context/Legal/`, u mlčenlivosti do `~/Context/Business/nda.md`. Je to zápis do domény, takže jen s potvrzením.

## Časté chyby

- **Ústupek mimochodem.** Požadavek uživatele se v revizi rovnou napíše měkčeji, protože „první kolo nemá být konfrontační“. Navenek je to rozumný kompromis, ve skutečnosti rozhodnutí, které skillu nepatří, a protistrana pak vyjednává od už sníženého základu.
- **Kontext ze zastaralé kopie.** Výtah z `decisions.md` vložený do zadání vrátí do smlouvy blok, který autor mezitím vědomě vyškrtl. Panel pak hlásí falešný poplach a revize ho propašuje do textu.
- **Autor revizí nechaný na agentovi.** Revize pak jdou jednou pod jménem uživatele a jindy pod „Claude“, a protistrana vidí, kdo text psal.
- **Zápis mimo místo dokumentu.** Výstupy rozházené po jiných adresářích rozbijí rozpoznání režimu v příštím kole.
- **Jeden široký posudek místo panelu.** Kde pro druh smlouvy chybí mantinely, minul jeden agent většinu podstatného. Úzká hlediska to místo našla nezávisle na sobě.

## Fáze 9 – Závěr

```
## Právní oponentura hotová

- **Dokument:** <cesta>
- **Režim:** <review / counter, kolo N>
- **Rámec:** <naše strana> proti <protistrana> · <rozhodné právo> · k <rozhodný den>
- **Hlediska:** <seznam>
- **Panel:** A hledisek → B nálezů hrubě → C po dedupu → D ověřeno, E neověřeno
- **Pokrytí dokumentu:** N z M článků [· hledisko s nejmenším pokrytím a kolik prošlo]
- **Spotřeba:** [N agentů: X hledisek, Y ověřovatelů · na jakém modelu a effortu]

**Nálezy:** N celkem – 🔴 X kritických, 🟡 Y středních, 🔵 Z nízkých
- Požadujeme změnu: N
- Ústupek na záložní znění: N
- Beze změny: N
- Odloženo: N
- Vyvráceno při ověření: N (nezobrazeno)
- Neověřeno: N

**Výstupy**
- Revize: <cesta> – autor <jméno>, validátor: <výsledek>
- Pracovní soubor: <cesta> – interní, ven nejde
- Koncept mailu: <cesta> – neodesláno

**Advokát:** Tohle není posudek advokáta. <Vyplatil by se kvůli: vysoká hodnota smlouvy / cizí rozhodné právo / klíčový bod bez ověřeného pramene – a který. Nebo: žádný z těch důvodů tu nenastal.>
```

Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo (`~/.claude/standards/rules.md`, *Styl odpovědí*).

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Posudek je hotový a vypořádaný, revize a koncept mailu jsou připravené – odešleš je sám.`
- `Posudek hotový není – brání tomu: <konkrétní seznam>.`

**Kudy dál** je poslední blok odpovědi, za verdiktem. Tvar drží `~/.claude/skills/handoff.md`. Odtud vede:

- až protistrana odpoví, `/legal counter` nad její verzí,
- advokát, uvedl-li verdikt důvod pro něj,
- zápis obecné meze do domény, navrhla-li ji *Fáze 8*.
