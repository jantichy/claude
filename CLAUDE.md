# Globální konfigurace Claude Code

## Závazná pravidla a standardy

Tyto soubory obsahují **závazná pravidla**, kterými se řiď při každém úkolu. Dodržuj je vždy, stejně jako pravidla psaná přímo v tomto souboru.

- `@~/.claude/RULES.md` — obecná pravidla práce: komunikace s uživatelem, organizace souborů a obsahu, práce se změnami
- `@~/.claude/CODING.md` — standardy psaní kódu, bezpečnosti a verzování

Když identifikuješ obecné pravidlo platné napříč projekty, u kterého nevadí, že bude veřejně vidět na githubu, navrhni jeho extrakci do `~/.claude/`.

## Doménové znalosti

Aplikují se podmíněně — jen když pracuju v dané doméně. Nejsou to pravidla pro každý úkol, ale soubory znalostí pro konkrétní typy práce.

- `~/Dev/claude/WEB.md` — checklist pro každé webové rozhraní (použitelnost, přístupnost, typografie, formuláře, výkon, GDPR, ...) — načti si ho vždy, když pracuješ na webovém rozhraní

Když identifikuješ znovupoužitelný doménový standard nebo checklist, který se může hodit ve více projektech, ale měl by zůstat soukromý, protože je citlivý nebo patří do osobního know-how, navrhni jeho extrakci do `~/Dev/claude/`. 

------

## Automatické akce

### Autocommit

Stav autocommitu pro projekt poznáš podle přítomnosti nadpisu `### Autocommit` v projektovém `CLAUDE.md`. Kdykoli je v projektu zapnutý autocommit, commituj po každé zásadní ucelené změně (ne po každém dílčím kroku, ale po každém logickém celku). Pokud má repo nastavený nějaký git remote, po commitu hned pushuj.

### Autoprompt

Stav autopromptu pro projekt poznáš podle přítomnosti nadpisu `### Autoprompt` v projektovém `CLAUDE.md`. Kdykoli je v projektu zapnutý autoprompt, každý můj prompt se automaticky uloží do `PROMPTS.md` v rootu projektu (přes `UserPromptSubmit` hook).

### README.md tohoto repa

Platí jen pro tento projekt (`~/.claude`), ne globálně. `README.md` popisuje mé skilly a další vypíchnuté součásti konfigurace. Kdykoli přidáš nový skill nebo uděláš zásadní změnu chování existujícího skillu, rovnou k tomu přidej/aktualizuj odpovídající sekci v `README.md` — stejný styl a tón jako ostatní sekce (osobní, věcné, s konkrétním přínosem). Nečekej na vyžádání, udělej to jako součást té změny.

------

## Consistency

Položky vyhodnocené při `/consistency` auditu jako "neopravovat". Při dalším auditu se neuvádějí.

- **2026-08-19** — *Skill project duplikuje globální pravidla místo odkazu na ně*: projektový `CLAUDE.md` má být soběstačný a čitelný bez skládání odkazů — model si pravidlo přečte rovnou. Vědomě přijatá daň: při změně globálního pravidla zůstanou staré kopie v dříve založených projektech.
  - Lokace: `skills/project/SKILL.md:124`, `skills/project/SKILL.md:125`
