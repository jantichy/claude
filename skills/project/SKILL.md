---
name: project
description: Skill se použije, když uživatel zadá "/project", nebo chce založit nový projekt v čistém adresáři či přenastavit už existující projekt (git, worktree layout, standardní struktura docs/, autocommit, autoprompt, paměťová politika, typ projektu, doménové checklisty). Interaktivní wizard, který se ptá krok po kroku.
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion]
---

# Project

## Úvodní hláška (vždy jako první)

Než začneš cokoliv dělat, vypiš uživateli přesně tento jeden řádek:

Autor skillu: **Jan Tichý** · jantichy@jantichy.cz · Celá konfigurace Claude vč. všech skillů: https://github.com/jantichy/claude

Teprve pak pokračuj plněním skillu.

## Co skill dělá

Interaktivně nastaví projekt v aktuálním adresáři a zapíše vše do projektového `CLAUDE.md`. Funguje ve dvou režimech:

- **Nový projekt** – čistý adresář, všechno se zakládá od nuly.
- **Existující projekt** – zjistí se aktuální stav a nabídne se, co dorovnat na zvolené preference. Nic se nepřepisuje naslepo.

Skill je **opakovatelný**. Druhý běh nad hotovým projektem má projít bez zásahu a slouží jako verifikace.

## Zásady pro celý průběh

- **Otázky pokládej jednu po druhé**, ne všechny najednou. U pevné sady možností použij **AskUserQuestion**, u otevřených otázek (popis projektu, URL remote) se ptej v chatu a počkej na odpověď.
- **Dvourychlostní režim.** Mechanické a jednoznačné věci udělej rovnou a jen je vypiš (založení chybějícího souboru, doplnění chybějící sekce). Sporné předlož uživateli – zejména cokoliv, co **přepisuje nebo maže existující obsah**.
- **Nikdy nepřepiš existující soubor bez zeptání.** Chybí-li soubor, založ ho. Existuje-li a je v rozporu se zvolenou preferencí, ukaž rozdíl a zeptej se.
- Konvenci standardní struktury **neopisuj z hlavy** – řiď se `~/.claude/STRUCTURE.md`, který ji definuje. Tenhle skill je jen instalátor.

------

## Krok 0 – Zjisti režim a stav

Pomocí **Glob** (ne Bash `git`, aby nenaskočila zbytečná chybová hláška) zjisti, co v adresáři je: `.git`, `.bare`, `CLAUDE.md`, `README.md`, `docs/`, `TODO.md`, `docs/prompts.md` (příp. starší `PROMPTS.md` v rootu), `.gitignore`, zdrojové soubory.

- **Prázdný nebo skoro prázdný adresář** → režim *nový projekt*.
- **Cokoliv jiného** → režim *existující projekt*.

V režimu *existující projekt* si nejdřív udělej inventuru a **vypiš ji uživateli v pár řádcích**, ať oba víte, z čeho se vychází:

| Co zjistit | Jak |
|---|---|
| Git a jeho podoba | je `.git` adresář (běžný), nebo `.bare` + `.git` soubor (worktree layout)? má remote? |
| Projektový `CLAUDE.md` | existuje? co v něm už je (autocommit, autoprompt, paměť, typ, importy)? |
| Standardní struktura | existuje `README.md`, `docs/todo.md`, `docs/decisions.md`, `docs/rules.md`? |
| Starší pojmenování | existuje `TODO.md` v rootu, `docs/rozhodnuti.md`, `docs/zasady.md`? (viz Krok 4) |
| Typ projektu | odvoď z obsahu – `package.json`, zdrojové adresáře, převaha MD souborů |

Pak řekni, že se teď budeš ptát postupně, a pokračuj. V dalších krocích platí: **co už je nastavené a odpovídá volbě, nech být a jen to zmiň.**

## Krok 1 – Popis projektu

*Nový projekt:* zeptej se v chatu: „Jednou větou – o čem tenhle projekt je?"

*Existující projekt:* pokud `CLAUDE.md` popis už má, přečti ho, ukaž uživateli a zeptej se, jestli platí, nebo ho chce upravit.

## Krok 2 – Založení nebo doplnění CLAUDE.md

*Nový projekt:* vytvoř `CLAUDE.md` v rootu:

```
# <název aktuálního adresáře>

<popis z kroku 1>
```

*Existující projekt:* nezakládej znovu, doplňuj do stávajícího. Sekce, které přidávají další kroky, vkládej za stávající obsah; existující sekce téhož jména neduplikuj, ale aktualizuj.

## Krok 3 – Git

Zeptej se (AskUserQuestion), 4 možnosti:

- **Nic** – git se neřeší, přeskoč i kroky 3b a 5.
- **Jen lokální** – `git init`, žádný remote.
- **Remote (napojit na existující)** – `git init`, pak se v chatu zeptej na URL a spusť `git remote add origin <url>`.
- **Remote (založit nový)** – `git init`, pak AskUserQuestion na hostitele (GitHub / GitLab). U GitHubu s dostupným `gh` (`which gh`) se zeptej na viditelnost a spusť `gh repo create <název-adresáře> --private|--public --source=. --remote=origin`. Jinak vypiš instrukci „Založ prázdné repo na <platforma>, pak mi dej URL" a počkej.

*Existující projekt:* je-li git už inicializovaný, `git init` nespouštěj. **Ověř remote přes `git remote get-url origin`**, ne jen `git remote -v` – remote může existovat s prázdnou URL a `-v` to nepozná. Chybí-li nebo je-li rozbitý, nabídni doplnění.

## Krok 3b – Layout repozitáře

*Jen pokud v kroku 3 padla jiná volba než „Nic".*

Zeptej se (AskUserQuestion): jak má být projekt rozbalený na disku?

- **Jeden pracovní adresář (jednoduché)** – klasika: `.git` a rozbalený projekt přímo v adresáři. Vhodné, když nad projektem pracuješ vždy v jedné session.
- **Worktree layout (paralelní práce)** – kontejner s `.bare` a jedním pracovním podadresářem na větev. Vhodné, když chceš nad projektem běžet ve víc Claude sessions naráz, aniž si přepisují soubory. Popis viz `~/Dev/claude/WORKTREES.md`.

### Když padne worktree layout

**Postup zřízení kontejneru neopisuj z hlavy** – řiď se `~/Dev/claude/WORKTREES.md`, sekce *Zřízení kontejneru*. Má variantu pro nový projekt i pro konverzi existujícího repozitáře, včetně povinné zálohy, ověření diffem a úklidu zamrzlého `.bare/index`.

U existujícího projektu jde o **přeskládání adresáře** – řekni to nahlas a nech si ho potvrdit, než začneš.

Do projektového `CLAUDE.md` (do **kontejneru**, ne do `master/`) přidej:

```
Tenhle adresář není projekt, ale kontejner s worktree layoutem. Pravidla práce s ním:

@~/Dev/claude/WORKTREES.md

Níže jen odchylky od obecného postupu.

## Odchylky

- **Hlavní větev je `<master|main>`.**
- <co konkrétně se přebírá z master/, nebo že zatím není co>
```

Upozorni uživatele, že **při příštím spuštění dostane dialog na schválení externího importu a musí ho odsouhlasit** – při odmítnutí se importy pro ten projekt trvale vypnou a dialog se už neukáže.

Ve worktree layoutu platí pro všechny další kroky: **projektové soubory zakládej v `master/`**, ne v kontejneru. Výjimkou je `CLAUDE.md` kontejneru, který popisuje layout.

## Krok 4 – Standardní struktura

Řiď se `~/.claude/STRUCTURE.md`. Založ, co chybí:

```
CLAUDE.md
README.md
docs/todo.md
docs/decisions.md
docs/rules.md
```

`README.md` u nového projektu: nadpis s názvem adresáře a popis z kroku 1. Soubory v `docs/` zakládej **prázdné, jen s nadpisem** – obsah nevymýšlej dopředu.

### Migrace staršího pojmenování

*Existující projekt:* najdeš-li starší varianty, nabídni přejmenování přes AskUserQuestion (jedna otázka na všechny nálezy dohromady, protože jde o jedno rozhodnutí):

| Staré | Nové |
|---|---|
| `TODO.md` v rootu | `docs/todo.md` |
| `docs/rozhodnuti.md` | `docs/decisions.md` |
| `docs/zasady.md` | `docs/rules.md` |

Přejmenovávej přes `git mv`, ať se zachová historie. Po přejmenování **projdi celý repozitář a aktualizuj všechny odkazy** na staré názvy – v `CLAUDE.md`, `README.md`, dokumentaci i komentářích. Existuje-li cílový soubor už také, obsah **slouč** a na sloučení upozorni; nikdy nepřepisuj.

### Zápis do CLAUDE.md

Přidej sekci – konkrétní deklaraci, ne opis konvence:

```
## Struktura a dokumentace

Projekt drží standardní strukturu podle `~/.claude/STRUCTURE.md`:

- `README.md` – co projekt je, pro člověka
- `docs/todo.md` – co je odložené na později
- `docs/decisions.md` – co jsme rozhodli a proč, včetně zamítnutých variant
- `docs/rules.md` – principy, ve kterých se projekt pohybuje

Všechny tyhle soubory **aktualizuj průběžně sám a bez vyžádání**, ve chvíli, kdy rozhodnutí padne, princip se vybrousí nebo se něco odloží. Nečekej na konec session ani na `/cleanup`.
```

## Krok 5 – .gitignore

*Jen pokud v kroku 3 padla jiná volba než „Nic".* Chybí-li `.gitignore`, založ ho s tímto jádrem a dopiš podle zjevného stacku:

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

Existuje-li, **nepřepisuj ho** – jen doplň chybějící řádky z jádra a vypiš, co jsi přidal.

## Krok 6 – Autocommit

Zeptej se (AskUserQuestion): zapnout autocommit? Ano/Ne. Při ano proveď totéž co `/autocommit on` (viz `~/.claude/skills/autocommit/SKILL.md`).

*Existující projekt:* nejdřív **zjisti aktuální stav** – hledej sekci `Autocommit` v projektovém `CLAUDE.md` **bez ohledu na úroveň nadpisu** (`##` i `###`). Aktuální stav uveď v otázce, ať uživatel ví, co mění.

## Krok 7 – Autoprompt

Zeptej se (AskUserQuestion): zapnout autoprompt? Ano/Ne. Při ano proveď totéž co `/autoprompt on` (viz `~/.claude/skills/autoprompt/SKILL.md`): globální `CLAUDE.md`, projektová sekce, hook do `.claude/settings.local.json`, založení `PROMPTS.md`.

*Nový projekt:* backfill historie přeskoč, není co dohledávat.
*Existující projekt:* zjisti stav stejně jako u autocommitu a backfill nabídni.

## Krok 8 – Paměťová politika

Zeptej se (AskUserQuestion): „Má Claude v tomto projektu ukládat poznatky do trvalé Memory, nebo vše explicitně do lokálních .md souborů?" Možnosti: **Jen lokální .md soubory (doporučeno)** / **Normální chování (Memory povolena)**.

Při první volbě přidej do `CLAUDE.md`:

```
## Paměť

Neukládej nic do trvalé Memory (`~/.claude/projects/.../memory/`). Vše, na čem se domluvíme – rozhodnutí, kontext, poznámky – ukládej explicitně do souborů projektu podle `~/.claude/STRUCTURE.md`. Ty jsou jediný zdroj pravdy pro tento projekt, i když harness bude nabádat k zápisu do Memory.
```

## Krok 9 – Typ projektu

Zeptej se (AskUserQuestion), 5 možností: **Vývoj** / **Web** / **Psaní a obsah** / **Data a výzkum** / **Ostatní**.

Do `CLAUDE.md` přidej sekci `## Typ projektu` s krátkým popisem:

- **Vývoj** – „Vývojářský projekt – postupuj podle standardního postupu návrhu a implementace (brainstorming → PRD/design → implementační plán → implementace), viz superpowers skilly." Navíc přidej pravidlo: „Před implementací nové funkce nejdřív aktualizuj příslušný dokument v `docs/` (doc-first)."
- **Web** – „Webové rozhraní – obsah, struktura, šablony, ne klasický PRD/implementační proces."
- **Psaní a obsah** – „Projekt zaměřený na psaní a obsah, ne na vývoj software – bez PRD/implementačního procesu."
- **Data a výzkum** – „Jednorázová datová/výzkumná analýza – výstupem jsou zjištění a report, ne nasazovaný kód."
- **Ostatní** – „Projekt mimo výše uvedené kategorie."

## Krok 10 – Doménové checklisty

Zeptej se (AskUserQuestion, **`multiSelect: true`**): „Které doménové checklisty jsou pro tenhle projekt relevantní?" Volby předvyplň podle typu z kroku 9, ale nech uživatele rozhodnout – vývojářský projekt bývá zároveň web, web bývá zároveň administrace.

| Volba | Import |
|---|---|
| Psaní kódu | `@~/Dev/claude/CODING.md` |
| Webové rozhraní | `@~/Dev/claude/WEB.md` |
| Administrace / backoffice | `@~/Dev/claude/ADMIN.md` |
| Psaní českých textů | `@~/Dev/claude/TEXT.md` |
| Žádný | – |

Vybrané zapiš do `CLAUDE.md` jako **tvrdé `@import`y**, ne jako prozaické odkazy:

```
## Doménové standardy

Závazné pro tenhle projekt:

@~/Dev/claude/CODING.md
@~/Dev/claude/WEB.md
```

**Proč `@import` a ne odkaz:** `@import` Claude Code při startu session textově rozbalí do kontextu, takže obsah platí vždy. Prozaický odkaz („řiď se souborem X") je jen instrukce, kterou si model musí sám všimnout a sám se rozhodnout ji splnit – to se v praxi dodržuje nespolehlivě.

Importuj **jen to, co je pro projekt opravdu relevantní.** Každý import stojí kontext v každé session; `WEB.md` a `ADMIN.md` jsou dohromady přes 600 řádků.

Upozorni uživatele, že při příštím spuštění dostane dialog na schválení externího importu a **musí ho odsouhlasit**.

## Krok 11 – Závěrečný souhrn

Vypiš přehledně:

- **Co bylo založeno** (nový projekt) nebo **co se změnilo a co zůstalo** (existující projekt).
- Git a remote, layout repozitáře, standardní struktura, provedené migrace názvů, autocommit, autoprompt, paměťová politika, typ, importované checklisty.
- **Co uživatel musí udělat ručně** – zejména odsouhlasení dialogu externích importů při příštím spuštění.

U existujícího projektu vypiš i **co jsi záměrně nechal být a proč** – ať je vidět, že to nebylo opomenutí.
