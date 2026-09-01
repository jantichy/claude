# Konfigurace Claude Code

Moje osobní konfigurace Claude Code – pravidla, skilly, hooky a status line, sdílená pro inspiraci.

- **Slug:** `claude`
- **Repozitář:** https://github.com/jantichy/claude

## Výjimky z obecných pravidel

- **Blok metadat je tady, ne v kořenovém `CLAUDE.md`**, jak jinak velí `~/Dev/context/structure/structure.md`. Kořenový soubor je uživatelský a rozbaluje se do každé session v každém projektu – metadata tohohle repozitáře tam nepatří, mátla by v cizím projektu.
- **`docs/` neexistuje.** Repozitář není vyvíjený projekt, ale konfigurace; `todo.md`, `done.md`, `decisions.md` ani `rules.md` nemá a nezakládají se.

## Instrukce pro tenhle repozitář

Projektové instrukce pro práci **v tomhle repozitáři**. Načítají se jen tady, na rozdíl od `~/.claude/CLAUDE.md`, který je uživatelský a jde do každé session v každém projektu.

- **Skill je sloveso, jeho výstup podstatné jméno.** `/specify` vyrábí `requirements.md` a `architecture.md`, `/breakdown` vyrábí `plan.md`, `/implement` vyrábí kód. **Žádný skill se nejmenuje stejně jako svůj výstup** – jinak vzniká otázka, jestli je „plan“ věc, nebo činnost. Do té pasti spadl GitHub Spec Kit s `/plan` → `plan.md` a je to důvod, proč se od jeho názvosloví jinde záměrně odchyluju.
- **Žádné zkratky v názvech.** Ani v názvech skillů, ani v názvech souborů, které vyrábějí.
- Každý skill má v `README.md` svou sekci. Když nějaký přidáš nebo zásadně změníš jeho chování, aktualizuj ji rovnou jako součást té změny – stejný styl a tón jako ostatní sekce (osobní, věcné, s konkrétním přínosem). Nečekej na vyžádání.

## Automatické akce

### Autocommit

Autocommit je zapnutý.
