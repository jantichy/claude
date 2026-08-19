# Globální konfigurace Claude Code

## Závazná pravidla a standardy

Tento soubor obsahuje **závazná pravidla**, kterými se řiď při každém úkolu. Dodržuj je vždy, stejně jako pravidla psaná přímo v tomto souboru.

- `@~/.claude/RULES.md` – obecná pravidla práce: komunikace s uživatelem, organizace souborů a obsahu, práce se změnami

Když identifikuješ obecné pravidlo platné napříč projekty, u kterého nevadí, že bude veřejně vidět na githubu, navrhni jeho extrakci do `~/.claude/`.

## Doménové znalosti

Aplikují se podmíněně – jen když pracuju v dané doméně. Nejsou to pravidla pro každý úkol, ale soubory znalostí pro konkrétní typy práce.

- `~/Dev/claude/WEB.md` – checklist pro každé webové rozhraní (použitelnost, přístupnost, typografie, formuláře, výkon, GDPR, ...) – načti si ho vždy, když pracuješ na webovém rozhraní
- `~/Dev/claude/CODING.md` – standardy psaní kódu, bezpečnosti a verzování (naming, git, bezpečnost, TypeScript, SQL, frontend) – načti si ho vždy, když píšeš nebo upravuješ kód

Když identifikuješ znovupoužitelný doménový standard nebo checklist, který se může hodit ve více projektech, ale měl by zůstat soukromý, protože je citlivý nebo patří do osobního know-how, navrhni jeho extrakci do `~/Dev/claude/`. 

------

## Automatické akce

### Autocommit

Stav autocommitu pro projekt poznáš podle přítomnosti nadpisu `### Autocommit` v projektovém `CLAUDE.md`. Kdykoli je v projektu zapnutý autocommit, commituj po každé zásadní ucelené změně (ne po každém dílčím kroku, ale po každém logickém celku). Pokud má repo nastavený nějaký git remote, po commitu hned pushuj.

### Autoprompt

Stav autopromptu pro projekt poznáš podle přítomnosti nadpisu `### Autoprompt` v projektovém `CLAUDE.md`. Kdykoli je v projektu zapnutý autoprompt, každý můj prompt se automaticky uloží do `PROMPTS.md` v rootu projektu (přes `UserPromptSubmit` hook).

------

## Platí jen pro repozitář `~/.claude`

- Každý skill má v `README.md` svou sekci. Když nějaký přidáš nebo zásadně změníš jeho chování, aktualizuj ji rovnou jako součást té změny – stejný styl a tón jako ostatní sekce (osobní, věcné, s konkrétním přínosem). Nečekej na vyžádání.
