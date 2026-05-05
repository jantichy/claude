# Globální konfigurace Claude Code

## Závazná pravidla a standardy

Tyto soubory obsahují **závazná pravidla**, kterými se řiď při každém úkolu. Dodržuj je vždy, stejně jako pravidla psaná přímo v tomto souboru.

- `@~/.claude/RULES.md` — obecná pravidla práce: persistence znalostí, rozhodování, komunikace, struktura souborů a kódu
- `@~/.claude/CODING.md` — standardy psaní kódu a bezpečnosti

Když identifikuješ obecné pravidlo platné napříč projekty, u kterého nevadí, že bude veřejně vidět na githubu, navrhni jeho extrakci do `~/.claude/`.

## Doménové znalosti

Aplikují se podmíněně — jen když pracuju v dané doméně. Nejsou to pravidla pro každý úkol, ale soubory znalostí pro konkrétní typy práce.

- `@~/dev/claude/WEB.md` — checklist pro každé webové rozhraní (použitelnost, přístupnost, typografie, formuláře, výkon, GDPR, ...)

Když identifikuješ znovupoužitelný doménový standard nebo checklist, který se může hodit ve více projektech, ale měl by zůstat soukromý, protože je citlivý nebo patří do osobního know-how, navrhni jeho extrakci do `~/dev/claude/`. 

------

## Git a commitování

- Git autor je globálně nastaven (`jantichy@jantichy.cz` / `Jan Tichý`). Neměň bez explicitní žádosti.
- Necommituj ani nepushuj automaticky. Jen na explicitní žádost nebo v projektech s autocommitem.
- Používej feature větve a otevírej Pull Requesty před mergem do `main`.
- Commit messages: stručné, rozkazovací způsob (imperativ).

## Automatické akce

### Autocommit

Stav autocommitu pro projekt poznáš podle přítomnosti nadpisu `### Autocommit` v projektovém `CLAUDE.md`. Kdykoli je v projektu zapnutý autocommit, commituj po každé zásadní ucelené změně (ne po každém dílčím kroku, ale po každém logickém celku). Pokud má repo nastavený nějaký git remote, po commitu hned pushuj.

### Autoprompt

Stav autopromptu pro projekt poznáš podle přítomnosti nadpisu `### Autoprompt` v projektovém `CLAUDE.md`. Kdykoli je v projektu zapnutý autoprompt, každý můj prompt se automaticky uloží do `PROMPTS.md` v rootu projektu (přes `UserPromptSubmit` hook).
