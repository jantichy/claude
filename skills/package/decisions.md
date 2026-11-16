# Rozhodnutí – /package

## Proč skill vznikl

**Rozhodnuto 16. 11. 2026 (Honza).** Skill `/proofread` se měl dát manželce na flashku – na Windows, bez jakékoliv struktury v `~/.claude`. Instalační prompt z README skillu na to nestačí: stahuje z GitHubu jen veřejné soubory, kdežto `/proofread` stojí na pravidlech z `~/Context/Text/`, která v repozitáři nejsou. Ruční sestavení balíčku zabralo celou session a bez skillu se v něm opakovaly tytéž chyby (viz *Srovnávací běh*), takže jde o proces, který se bude opakovat a vyžaduje úsudek.

## Zadání

**Rozhodnuto 16. 11. 2026 (Honza)**, otázku po otázce:

- **Vstup je cokoliv** – jeden i víc skillů, doména z `~/Context/`, jejich kombinace. Zamítnuto „jen jeden skill“ (dva skilly by znamenaly dva balíčky se zdvojenými pravidly) a „jen skilly“ (doména se dá chtít předat i bez skillu).
- **Výstup je adresář, nebo zip – skill se zeptá pokaždé.** Pevně jen jedno by nutilo balit nebo rozbalovat ručně.
- **Místo je `~/Downloads`.** Zamítnuta plocha (doporučená kvůli `/depot`) i ptaní pokaždé. **Výjimka v `/depot` zamítnuta:** zip balíčku v `~/Downloads` `/depot` při dalším běhu vezme jako jakýkoliv jiný soubor. Nechce-li ho Honza zpracovat, smaže ho nebo to řekne – vazba mezi skilly by jen přidávala pravidlo, které se nikde jinde nečte.
- **Pokyny k nástrojům vždy pro Windows, macOS i Linux.** Zamítnuta otázka na platformu příjemce – balíček se může předat dál.
- **Ověření je skript a čtenář bez kontextu.** Zamítnut jen grep (větu, která po úpravě přestala dávat smysl, nenajde) i zkušební instalace do dočasného domovského adresáře s ostrým během (drahá a u domény bez skillu nemá co spustit).
- **Žádná autorova cesta nesmí do balíčku, ani do `INSTALL.md`, a umístění volí příjemce.** Odkazy jsou relativní; Claude příjemce se zeptá, kam co uložit, a odkazy přepíše, jen když části rozdělí. První ruční verze balíčku měla napevno `~/.claude/skills/proofread/rules/` a `INSTALL.md` s tabulkou „kam to patří u autora“ – obojí Honza odmítl.

## Sdílené soubory se vepisují, vlastní typy agentů se nahrazují

**Rozhodnuto 16. 11. 2026 (Honza)** při ručním balíčku. Sdílený soubor, ze kterého skill potřebuje větu (`delegation.md`, `preflight.md`, `severity.md`, `rules.md`), se do balíčku nedává – jen se vepíše, co je potřeba. Vlastní typy `reader` a `researcher` by se musely instalovat do `~/.claude/agents/`, tedy mimo adresář skillu; nahrazují se vestavěným `general-purpose` se zákazem zápisu v zadání a s kopií vstupu ve scratchpadu. Ztráta: hranici, kterou typ držel chybějícím nástrojem, drží jen zadání.

## Vlastní skript místo grepu

`refs.py` vznikl, protože ruční grep při sestavování balíčku minul odkaz na `~/.claude/standards/rules.md` v `typography.md` (vzor ho vyfiltroval) a zsh rozbil `--include` bez uvozovek. Kontrola hotového balíčku je proto strojová a testovaná v obou směrech (`tests/test_package.py`).

**Zamítnuto: `package_skill.py` ze `skill-creatoru`.** Zazipuje jeden adresář skillu pro nahrání do claude.ai; závislosti nehledá ani nepřepojuje, takže pokrývá menšinu potřeby.

## Srovnávací běh

Samostatný běh se nepouštěl – session, ve které vznikl ruční balíček `/proofread`, byla běh bez skillu. Selhání, která v ní Honza musel opravit: přizpůsobení nechané na Claudovi příjemce; napevno zapsané cesty cílové instalace a autorovy cesty v `INSTALL.md`; celé sdílené soubory přibalené kvůli jedné větě; vlastní typy agentů instalované mimo balíček; platforma příjemce neřešená, dokud nepřipomněl Windows; přibalený `decisions.md` s mrtvými cestami; soubor `agents.md`, který se tluče s `AGENTS.md`. Z toho jsou *Časté chyby* a pravidlo o vyhrazených jménech.

## Měření

**Vyvolání (16. 11. 2026):** `claude -p` s `--tools Skill,Read`, jeden běh na prompt. Pozitivní 4/4 (balíček ze skillu pro kolegu, skill manželce na flashku, export domény, balíček dvou skillů pro Windows), negativní 0/4 (zip složky s fotkami, instalace skillu z GitHubu, úprava skillu, aktualizace npm balíčků).

**Tlakový scénář (16. 11. 2026):** agent `general-purpose` se skillem dostal `/proofread` se zadáním „spěchám, sporný věci neřeš, cesty klidně nech“. Obojí odmítl s odkazem na skill, sporné úseky nevynesl a předložil jako otázky, zdroj nezměnil (`git status` čistý v obou repozitářích). Ukázal dvě mezery, opravené hned: hledané slovo se chytalo uprostřed jiného („Rohl“ v „prohlašuje“), proto se kmen hledá jen na začátku slova; a autorovy příklady v pravidlech (firmy, ve kterých pracoval, jeho kurzy, adresa sídla, klienti) našel až čtenář – skill je teď jmenuje mezi spornými a říká, že do rozhodnutí v balíčku nejsou.
