# Konfigurace Claude Code

Moje osobní konfigurace Claude Code – pravidla, skilly, hooky a status line, sdílená pro inspiraci.

- **Slug:** `claude`
- **Repozitář:** https://github.com/jantichy/claude

## Výjimky z obecných pravidel

- **Blok metadat je tady, ne v kořenovém `CLAUDE.md`**, jak jinak velí `~/Dev/context/structure/structure.md`. Kořenový soubor je uživatelský a rozbaluje se do každé session v každém projektu – metadata tohohle repozitáře tam nepatří, mátla by v cizím projektu.
- **`docs/` neexistuje.** Repozitář není vyvíjený projekt, ale konfigurace; `todo.md`, `done.md`, `decisions.md` ani `rules.md` nemá a nezakládají se.

## Instrukce pro tenhle repozitář

Projektové instrukce pro práci **v tomhle repozitáři**. Načítají se jen tady, na rozdíl od `~/.claude/CLAUDE.md`, který je uživatelský a jde do každé session v každém projektu.

- Každý skill má v `README.md` svou sekci. Když nějaký přidáš nebo zásadně změníš jeho chování, aktualizuj ji rovnou jako součást té změny – stejný styl a tón jako ostatní sekce (osobní, věcné, s konkrétním přínosem). Nečekej na vyžádání.

## Příkazy

Kontrakt příkazů (`~/Dev/context/coding/coding.md`, *Ověřování a brány kvality*). Zelená linka ho tady najde v `.claude/CLAUDE.md` a příkazy spouští v kořeni repozitáře.

- typecheck: -
- lint: shellcheck --severity=info ./*.sh skills/*/*.sh
- test: python3 -m unittest discover -s tests

`shellcheck` běží se `--severity=info`, ne se `--severity=style`: stylové nálezy jsou preference a brána, která padá na preferenci, se obchází.

`test` jsou **meta-testy nad konfigurační vrstvou** (`tests/test_skills.py`): hlídají, že hlavičky skillů parsují a sedí s adresářem, že režim popsaný v těle je i v `argument-hint`, že odkazy na soubory vedou někam, že se skilly odkazují na kroky osy a ne na jejich vnitřky, že kroky osy mají sekci *Co skill nedělá* a že README zná každý skill. Používají jen stdlib – brána, která si žádá instalaci balíčku, se v cizím prostředí neprojeví jako nález, ale jako rozbitý nástroj, a ten se obchází.

Pomlčka u `typecheck` znamená **vědomě se neaplikuje**: repozitář je konfigurace, ne program, a nemá co typovat. Kdyby ten řádek chyběl úplně, hook by po každém tahu hlásil, že se něco nezkontrolovalo, a to by byl trvalý šum místo informace.

## Automatické akce

### Autocommit

Autocommit je zapnutý.
