---
name: project
description: Skill se použije, když uživatel zadá "/project", nebo chce založit/nastavit nový projekt v čistém adresáři (git, autocommit, autoprompt, paměťová politika, typ projektu, README/gitignore). Interaktivní wizard, který se ptá krok po kroku.
allowed-tools: [Read, Write, Edit, Glob, Bash, AskUserQuestion]
---

# Project (nový projekt wizard)

## Úvodní hláška (vždy jako první)

Než začneš cokoliv dělat, vypiš uživateli přesně tento jeden řádek:

Autor skillu: **Jan Tichý** · jantichy@jantichy.cz · Celá konfigurace Claude vč. všech skillů: https://github.com/jantichy/claude

Teprve pak pokračuj plněním skillu.

## Co skill dělá

Interaktivně nastaví nový projekt v aktuálním adresáři — git, autocommit, autoprompt, paměťová politika, typ projektu, README/gitignore — a zapíše vše do projektového `CLAUDE.md`. Otázky pokládej **jednu po druhé**, ne všechny najednou. U otázek s pevnou sadou možností použij **AskUserQuestion**, u otevřených otázek (popis projektu, URL remote) se ptej normálně v chatu a počkej na odpověď.

## Postup

### Krok 0 — Sanity check

Pomocí **Glob** (ne Bash `git`, aby nenaskočila zbytečná chybová hláška) zjisti, jestli v aktuálním adresáři už existuje `.git` nebo `CLAUDE.md`. Pokud ano, upozorni uživatele, že adresář nevypadá jako čistý nový projekt, a zeptej se (AskUserQuestion), jestli přesto pokračovat, nebo skončit. Pokud skončit → skonči bez dalších kroků.

### Krok 1 — Popis projektu

Zeptej se v chatu (obyčejná otázka, ne AskUserQuestion): "Jednou větou — o čem tenhle projekt je?" Odpověď použij jako úvodní popis v CLAUDE.md.

### Krok 2 — Založení CLAUDE.md

Vytvoř `CLAUDE.md` v projekt rootu s tímto obsahem (název adresáře jako nadpis, popis z kroku 1):

```
# <název aktuálního adresáře>

<popis z kroku 1>
```

Do tohoto souboru budeš postupně přidávat sekce podle dalších kroků.

### Krok 3 — Git

Zeptej se (AskUserQuestion), jedna otázka, 4 možnosti:
- **Nic** — git se vůbec neřeší, přeskoč i krok 4 (gitignore).
- **Jen lokální** — `git init`, žádný remote.
- **Remote (napojit na existující)** — `git init`, pak se v chatu zeptej na URL existujícího remote repozitáře, a spusť `git remote add origin <url>`.
- **Remote (založit nový)** — `git init`, pak AskUserQuestion na hostitele (GitHub / GitLab). Pokud GitHub a je dostupný `gh` CLI (`which gh`), zeptej se AskUserQuestion na viditelnost (soukromý/veřejný) a spusť `gh repo create <název-adresáře> --private|--public --source=. --remote=origin` (bez push, jen založení a napojení). Pokud `gh`/`glab` není dostupný nebo je zvoleno GitLab bez CLI, vypiš instrukci: "Založ prázdné repo na <platforma>, pak mi dej URL" — počkej na URL v chatu a spusť `git remote add origin <url>`.

Pokud padla jiná volba než "Nic", proveď `git init` (přes Bash), pokud ještě není inicializováno.

### Krok 4 — .gitignore a README.md

Pokud v kroku 3 padla jiná volba než "Nic": založ `.gitignore` s tímto jádrem (uprav/dopiš podle zjevného stacku projektu, pokud už jsou v adresáři nějaké soubory):

```
.DS_Store
.env
.env.local
node_modules/
dist/
build/
.next/
out/
.vercel
*.log
.idea/
.vscode/
```

Vždy (bez ohledu na volbu gitu) založ minimální `README.md`:

```
# <název aktuálního adresáře>

<popis z kroku 1>
```

Do CLAUDE.md přidej pravidlo:

```
## Dokumentace

`README.md` průběžně aktualizuj a přepisuj podle toho, jak se projekt vyvíjí — má vždy odpovídat aktuálnímu stavu.
```

### Krok 5 — Autocommit

Zeptej se (AskUserQuestion): zapnout autocommit? Ano/Ne. Pokud ano, proveď stejné kroky jako skill `/autocommit on` (viz `~/.claude/skills/autocommit/SKILL.md`, sekce `on`): doplň globální `~/.claude/CLAUDE.md` o `### Autocommit` (pokud tam chybí) a přidej sekci `### Autocommit` do projektového CLAUDE.md pod `## Automatické akce`.

### Krok 6 — Autoprompt

Zeptej se (AskUserQuestion): zapnout autoprompt? Ano/Ne. Pokud ano, proveď stejné kroky jako skill `/autoprompt on` (viz `~/.claude/skills/autoprompt/SKILL.md`, sekce `on`): globální CLAUDE.md, projektová sekce `### Autoprompt`, hook do `.claude/settings.local.json`, založení `PROMPTS.md`. Backfill historie (krok 5 z autoprompt skillu) přeskoč — u nového projektu není co dohledávat.

### Krok 7 — Paměťová politika

Zeptej se (AskUserQuestion): "Má Claude v tomto projektu ukládat poznatky do trvalé Memory, nebo vše explicitně do lokálních .md souborů?" Možnosti: **Jen lokální .md soubory (doporučeno)** / **Normální chování (Memory povolena)**.

Pokud "Jen lokální .md soubory", přidej do CLAUDE.md sekci:

```
## Paměť

Neukládej nic do trvalé Memory (`~/.claude/projects/.../memory/`). Vše, na čem se domluvíme — rozhodnutí, kontext, poznámky — ukládej explicitně do tohoto souboru nebo dalších tematických .md souborů v projektu. Ty jsou jediný zdroj pravdy pro tento projekt, i když harness bude nabádat k zápisu do Memory.
```

Pokud druhá volba, nic nezapisuj (výchozí chování).

### Krok 8 — Typ projektu

Zeptej se (AskUserQuestion), jedna otázka, 5 možností: **Vývoj** / **Web** / **Psaní a obsah** / **Data a výzkum** / **Ostatní**.

Do CLAUDE.md vždy přidej sekci `## Typ projektu` s krátkým popisem podle volby a proveď případné dodatečné kroky:

- **Vývoj**: text "Vývojářský projekt — postupuj podle standardního postupu návrhu a implementace (brainstorming → PRD/design → implementační plán → implementace), viz superpowers skilly." Navíc založ `docs/` (prázdný adresář, případně `docs/.gitkeep`) a `TODO.md`:
  ```
  # TODO

  Žijící seznam úkolů. Nedokončené položky nahoře, hotové přesouvej do sekce Hotovo dole — nikdy nemaž.

  ## Hotovo
  ```
  a do CLAUDE.md přidej pravidlo: "Před implementací nové funkce nejdřív aktualizuj příslušný dokument v `docs/` (doc-first). Necháváš `docs/` jako zdroj pravdy pro zadání a rozhodnutí."
- **Web**: text "Webové rozhraní — obsah, struktura, šablony, ne klasický PRD/implementační proces." Do CLAUDE.md přidej: "Při každé úpravě webového rozhraní projdi checklist `~/dev/claude/WEB.md` (použitelnost, přístupnost, typografie, formuláře, výkon, GDPR...)."
- **Psaní a obsah**: text "Projekt zaměřený na psaní/obsah, ne na vývoj software — bez PRD/implementačního procesu."
- **Data a výzkum**: text "Jednorázová datová/výzkumná analýza — bez PRD procesu, výstupem jsou zjištění/report, ne nasazovaný kód."
- **Ostatní**: text "Projekt mimo výše uvedené kategorie." (bez dalších kroků)

### Krok 9 — Závěrečný souhrn

Vypiš přehledně, co všechno bylo založeno/zapnuto (git + remote pokud ano, .gitignore, README.md, autocommit, autoprompt, paměťová politika, typ projektu + případné extra soubory) a potvrď, že `CLAUDE.md` je hotové a projekt připravený k práci.
