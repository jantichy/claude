# Globální konfigurace Claude Code

## Závazná pravidla a standardy

Tyto soubory obsahují **závazná pravidla**, kterými se řiď při každém úkolu. Dodržuj je vždy, stejně jako pravidla psaná přímo v tomto souboru.

- `@~/.claude/RULES.md` — obecná pravidla práce: persistence znalosti, rozhodování, komunikace, struktura souborů a kódu
- `@~/.claude/CODING.md` — standardy psaní kódu a bezpečnosti

## Doménové znalosti

Aplikují se podmíněně — jen když pracuju v dané doméně. Nejsou to pravidla pro každý úkol, ale soubory znalostí pro konkrétní typy práce.

- `@~/dev/claude/web.md` — checklist pro každé webové rozhraní (použitelnost, přístupnost, typografie, formuláře, výkon, GDPR, ...)

## Jazyk

- S uživatelem komunikuj **česky**
- Obsah MD dokumentů piš **česky**, pokud není v daném projektu nebo situaci řečeno jinak
- Kód piš **anglicky** (proměnné, funkce, třídy, soubory)
- Komentáře v kódu piš **česky**, pokud není v daném projektu nebo situaci řečeno jinak

## Styl odpovědí

- Odpovědi krátké a věcné — nepřepisuj co uživatel řekl, rovnou jednej
- Nepoužívej emoji, pokud o ně uživatel nepožádá

## Git a commitování

### Verzování a nasazení

- Git autor je globálně nastaven (`jantichy@jantichy.cz` / `Jan Tichý`). Neměň bez explicitní žádosti.
- Necommituj ani nepushuj automaticky. Jen na explicitní žádost nebo v projektech s autocommitem.
- Používej feature větve a otevírej Pull Requesty před mergem do `main`.
- Commit messages: stručné, rozkazovací způsob (imperativ).

### Autocommit

Stav autocommitu pro projekt poznáš podle přítomnosti nadpisu `## Autocommit` v projektovém `CLAUDE.md`. Kdykoli je v projektu zapnutý autocommit, commituj po každé zásadní ucelené změně (ne po každém dílčím kroku, ale po každém logickém celku). Pokud má repo nastavený nějaký git remote, ihned po commitu rovněž pushuj — pokud žádný remote nastavený není, stačí jen commit (lokální verzování).

### Autoprompt

Stav autopromptu pro projekt poznáš podle přítomnosti nadpisu `## Autoprompt` v projektovém `CLAUDE.md`. Kdykoli je v projektu zapnutý autoprompt, každý můj prompt se automaticky uloží do `PROMPTS.md` v rootu projektu (přes `UserPromptSubmit` hook).

## Repozitáře `~/.claude` a `~/dev/claude/`

Mám dvě související lokace pro globální Claude konfiguraci a knowhow:

- **`~/.claude/`** — **veřejný** GitHub repozitář (inspirační pro ostatní). Obsahuje konfiguraci Claude Code, hooks, skilly, settings a obecná závazná pravidla (`RULES.md`, `CODING.md`).
- **`~/dev/claude/`** — **soukromý** repozitář s doménovým knowhow, které nepatří ven (`web.md` a další). Projekty z `~/dev` na něj odkazují přes `@~/dev/claude/<soubor>.md`.

Hranice: pokud je obsah obecný a hodí se ostatním pro inspiraci → `~/.claude/`. Pokud je to moje osobní knowhow nebo doménový checklist, který nechci sdílet → `~/dev/claude/`. Pokud nejistota → zeptej se.

Když identifikuju znovupoužitelný checklist nebo standard, který by se hodil ve víc projektech, navrhnu jeho extrakci — do `~/.claude/` pokud je obecný, do `~/dev/claude/` pokud je doménový a soukromý.

**Autocommit pro `~/.claude`:** Tento repozitář má autocommit **trvale zapnutý** podle pravidel v sekci „Autocommit" výše. Kdykoli v průběhu konverzace upravíš nebo přidáš soubor v `~/.claude`, na konci své odpovědi proveď: `git -C ~/.claude add -A`, commit s výstižnou message vystihující věcnou podstatu změny (ne výpis souborů, ale lidské shrnutí, co a proč se měnilo), `git -C ~/.claude push`. Tohle pravidlo má prioritu — nezapomínej na něj.

