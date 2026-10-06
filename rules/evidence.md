# Zjišťování z dat

Pravidla pro měření, analýzu dat a hledání příčin – dotaz do databáze nebo analytiky, test hypotézy, ladění chyby – a pro přebírání tvrzení z webu. **Odkaz, ne import:** načítá se, když se zjišťuje; spouštěč drží `~/.claude/rules/rules.md`, *Zjišťuj podle pravidel pro práci s daty*.

## Před každým měřením vypiš, co který výsledek rozhodne

Než pustíš dotaz, test nebo jakékoliv zjišťování, napiš **všechny možné výsledky a u každého, co z něj plyne** – které tvrzení potvrzuje, které vylučuje a co se po něm dělá dál. Teprve pak měř. Zkráceně **vidlička**.

- **Patří do ní i větev, která se nehodí.** Vidlička, ve které jedna cesta chybí, dovede k tomu, co v ní zbylo.
- **Píše se nad konkrétním výstupem** – nad sloupcem, který se vrátí, nad číslem, které skočí nebo neskočí –, ne jako seznam hypotéz.
- **Platí i pro měření, které se zdá jednoznačné**; vidlička je pak jen kratší.

Výsledek bez předem daného výkladu se vykládá zpětně podle toho, co se čekalo, a žádná kontrola v datech nepozná, že se závěr ohnul. Vypsání větví navíc odhalí dotaz, který nerozhoduje ani jednu z nich.

## Vyloučení má tři stupně a ke každému patří cesta zpátky

Vyloučená možnost zůstane vyloučená a nikdo se do ní už nepodívá. Proto se při zavírání vyplňují tři věci – zpětně to nejde, protože si nikdo nevzpomene, jestli se měřilo, nebo usuzovalo.

**1. Čím se vylučovalo:**

| Jak | Co to znamená | Co to otevře znovu |
|---|---|---|
| **měřením** | změřil se mechanismus sám, ne jeho následek | že měření bylo užší, než se myslelo |
| **nesouladem podpisu** | „kdyby to byla příčina, viděli bychom X; vidíme Y“ | že očekávaný podpis byl odvozený špatně, nebo že mechanismus umí i jiný |
| **úvahou** | nezměřilo se nic, jen se to nezdálo | jakýkoliv údaj, který se toho dotkne |

Vyloučení úvahou je **odložení** a smí se tak nazvat jen tam, kde by měření stálo víc než celý dopad.

**2. Podmínka, která vyloučení ruší** – konkrétní věta („platí pro tenhle rozsah, jinde neměřeno“, „platí pro dnešní stav, ne pro dobu, o kterou jde“), ne obecná ostražitost.

**3. Po každém novém poznatku, který mění premisu vyloučení, se seznam projde znovu** – v pořadí úvaha → nesoulad podpisu → měření; měření jen tehdy, sahá-li nový poznatek na jeho rozsah.

**Vylučuje se cesta, ne tvrzení.** Mechanismus může vést několika cestami; uzavřít jednu neznamená vyvrátit mechanismus. Cesty pojmenuj dřív, než začneš vylučovat, a u každé drž vlastní stav.

**Nenalezení není doklad neexistence** – věc chybí, nebo ji hledáš špatně (`grep` nad souborem, který vezme za binární, mlčí stejně jako nad souborem bez shody; `grep -a` to obejde). Než z nenalezení uděláš tvrzení, ověř, že by tvůj postup věc našel, kdyby tam byla.

## Než odpovíš z dat, ověř, že v nich ta věc je

Ptá-li se někdo na konkrétní věc – zdroj, kanál, segment, období, metriku –, prvním krokem je najít soubor a sloupec, ve kterém ta věc stojí **pod svým jménem a v tom rozlišení, na které se ptá**. Nenajdeš-li ho, odpověď začíná tím, co v podkladech chybí a jaký podklad by otázku rozhodl – s dimenzí, filtrem, obdobím a metrikou, aby se o něj dalo rovnou požádat.

Žádost o data je plnohodnotná odpověď. Zástupný údaj smí zaznít jen označený jako zástupný, až za větou o tom, co chybí, a s tím, v čem se od ptané věci liší – kanál není zdroj, kategorie není produkt, celek není segment. Zástupný výpočet vypadá jako výsledek a nejistota u něj vůbec nevznikne, proto se to kontroluje mechanicky na začátku.

## Měř to, co tvrzení tvrdí, na tom, o čem to tvrdí

Vyloučení i potvrzení platí, jen když měření sedí na tvrzení ve třech věcech naráz:

- **Veličina.** Kolik lidí pravidlo odmítne, není totéž jako jestli se podle odmítnutí něco děje.
- **Populace.** Vada vázaná na část celku je v průměru přes celek neviditelná; test na zbytku ji nevyvrací.
- **Surové proti dopočítanému.** Tvrzení „chybu dělá zpracování na druhé straně“ nesmí vyvracet hodnota, kterou si ta strana sama dopočítala. Z názvu pole se to nepozná – ověř na případu, kde víš, co se poslalo.

Čísla takového měření jsou správná, jen odpovídají na jinou otázku – a zavřou větev, do které se nikdo nevrátí.

## Než pole použiješ v podmínce, vypiš jeho hodnoty

Před filtrem, agregací nebo výčtem vypiš, jaké hodnoty v poli doopravdy jsou, s počty. Jinak se filtruje podle podoby, ve které se nález čeká – a podmínka, která nesedne na nic, vypadá jako nález (prázdnota uložená zástupným řetězcem, podřetězec, který propustí nečitelný zápis). Platí na každé vrstvě: dotaz do databáze, parametry požadavku, klíče v JSONu, konfigurace, stavy v evidenci.

## Tvrzení z webu je jen tvrzení, dokud skript nepřečte stránku

Odkaz, který vrátí agent, je tvrzení, a jeho „ověřil jsem to“ taky – agent umí vymyslet věrohodnou citaci i adresu. **Než tvrzení z webu skončí v souboru** (rešerše, `competition.md`, znalostní báze, kód), ověř ho skriptem: zapiš pole `{"id", "url", "quote"}` nástrojem Write do scratchpadu a pusť `python3 ~/.claude/skills/sources.py --batch <soubor> --compact`. URL ani text stránky na příkazovou řádku nepatří, shell v nich spustí `$(...)`. Odpověď v konverzaci smí tvrzení předat i neověřené, ale označené jako hlášení agenta.

- **HTTP 200 není ověření.** Paywall, přihlašovací zeď i stránka „nenalezeno“ odpovídají 200 vlastním obsahem a vymyšlená adresa se často přesměruje na nesouvisející stránku.
- **Přečtená stránka (`REACHED…`) teprve otevírá posouzení**, jestli úryvek tvrzení opravdu nese. `REACHED_QUOTE_MISSING` je důvod stránku přečíst, ne důkaz podvrhu.
- **Každý jiný verdikt znamená „neověřeno (důvod)“**, nikdy „nepodložené“ ani „nepravdivé“ – nikdo stránku nečetl.
- **U každého tvrzení stojí, odkud se ví:** *změřeno* (spustil jsi to, nebo je to doložené přesně pro tenhle případ), *doloženo* (někdo to postavil nebo zjistil a napsal o tom – s URL), *úsudek* (tvoje odvození, ne nález). Nižší stupeň se za vyšší nevydává; neobsahuje-li rešerše doporučení, řekni to, místo abys ho odvodil.
- **Tvrzení bez zdroje se nezahazuje ani nedoplňuje**, hlásí se jako „bez ověřitelného zdroje“. Domyšlená URL je horší než žádná, protože na ni čtenář klikne.
- **Zařazení je slabší než fakt.** Agent spolehlivěji sesbírá, co produkt umí, než ho správně zařadí („X je nejbližší konkurent Y“, „X je lídr trhu“). Zařazení ověř nad primárními zdroji – že ty dvě věci opravdu dělají totéž.

Bez toho se do dokumentu dostane odkaz, který vypadá doloženě, a nikdo ho už nezpochybní.
