# Globální konfigurace Claude Code

## Závazná pravidla a standardy

Tyto soubory obsahují **závazná pravidla**, kterými se řídím při každém úkolu. Nejsou to referenční checklisty „pro inspiraci" — dodržuj je vždy, stejně jako pravidla psaná přímo v tomto souboru.

- `@~/.claude/RULES.md` — obecná pravidla práce: persistence znalosti, rozhodování, komunikace, struktura souborů a kódu
- `@~/.claude/CODING.md` — standardy psaní kódu a bezpečnosti

## Doménové checklisty

Aplikují se podmíněně — jen když pracuju v dané doméně. Nejsou to pravidla pro každý úkol, ale kontrolní seznamy pro konkrétní typy práce.

- `@~/Dev/claude/web.md` — checklist pro každé webové rozhraní (přístupnost, typografie, formuláře, výkon, GDPR, ...)

## Jazyk

- S uživatelem komunikuj **česky**
- Obsah MD dokumentů piš **česky**, pokud není v daném projektu nebo situaci řečeno jinak
- Kód piš **anglicky** (proměnné, funkce, třídy, soubory)
- Komentáře v kódu piš **česky**, pokud není v daném projektu nebo situaci řečeno jinak

## Styl odpovědí

- Odpovědi krátké a věcné — nepřepisuj co uživatel řekl, rovnou jednej
- Nepoužívej emoji, pokud o ně uživatel nepožádá
- Nepiš trailing shrnutí ("Hotovo, udělal jsem X, Y, Z") — diff mluví za sebe

## Git a commitování

### Verzování a nasazení

- Git autor je globálně nastaven (`jantichy@jantichy.cz` / `Jan Tichý`). Neměň bez explicitní žádosti.
- **Defaultně necommituj ani nepushuj automaticky.** Jen na explicitní žádost. Výjimkou jsou projekty s autocommitem — viz níže.
- Používej feature větve a otevírej Pull Requesty před mergem do `main`.
- Commit messages: stručné, rozkazovací způsob (imperativ).
- Deploy strategie: Git → GitHub → Vercel (auto-deploy). Pro logy a debugování používej `vercel` CLI (`vercel logs`, `vercel inspect`, `vercel env`).

### Autocommit

**Definice pojmu:** Kdykoli v projektu řeknu „zapni autocommit" (nebo použiji `/autocommit on`), platí tato pravidla commitování:

- **Commitovat po každé zásadní ucelené změně** — ne po každém dílčím kroku, ale po každém logickém celku
- **Amend místo nového commitu** — pokud bezprostředně po commitu dále řešíme stejné téma a ještě ho upravujeme → amend posledního commitu, ne nový commit (čistá historie)
- **Push vždy** — po každém commitu nebo amendu automaticky `git push`

Vypnutý autocommit (`/autocommit off`) vrací výchozí chování (commit jen na explicitní žádost).

Stav autocommitu pro projekt poznáš podle přítomnosti nadpisu `## Autocommit` v projektovém `CLAUDE.md`.

### Autoprompt

**Definice pojmu:** Kdykoli v projektu zapnu `/autoprompt on`, každý můj prompt se automaticky uloží do `PROMPTS.md` v rootu projektu (přes `UserPromptSubmit` hook).

Stav autopromptu pro projekt poznáš podle přítomnosti nadpisu `## Autoprompt` v projektovém `CLAUDE.md`.

## Repozitáře `~/.claude` a `~/Dev/claude/`

Mám dvě související lokace pro globální Claude konfiguraci a knowhow:

- **`~/.claude/`** — **veřejný** GitHub repozitář (inspirační pro ostatní). Obsahuje konfiguraci Claude Code, hooks, skilly, settings a obecná závazná pravidla (`RULES.md`, `CODING.md`).
- **`~/Dev/claude/`** — **soukromý** repozitář s doménovým knowhow, které nepatří ven (`web.md` a další). Projekty z `~/Dev` na něj odkazují přes `@~/Dev/claude/<soubor>.md`.

Hranice: pokud je obsah obecný a hodí se ostatním pro inspiraci → `~/.claude/`. Pokud je to moje osobní knowhow nebo doménový checklist, který nechci sdílet → `~/Dev/claude/`. Pokud nejistota → zeptej se.

**Autocommit pro `~/.claude`:** Tento repozitář má autocommit **trvale zapnutý** podle pravidel v sekci „Autocommit" výše. Kdykoli v průběhu konverzace upravíš nebo přidáš soubor v `~/.claude`, na konci své odpovědi proveď: `git -C ~/.claude add -A`, commit s výstižnou message vystihující věcnou podstatu změny (ne výpis souborů, ale lidské shrnutí, co a proč se měnilo), `git -C ~/.claude push`. Tohle pravidlo má prioritu — nezapomínej na něj.

Repozitář `~/Dev/claude/` se z hlediska autocommitu chová jako jakýkoli jiný projekt — řídí se přítomností sekce `## Autocommit` ve svém vlastním `CLAUDE.md`.

Když identifikuju znovupoužitelný checklist nebo standard, který by se hodil ve víc projektech, navrhnu jeho extrakci — do `~/.claude/` pokud je obecný, do `~/Dev/claude/` pokud je doménový a soukromý.
