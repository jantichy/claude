# Globální konfigurace Claude Code

## Závazná pravidla

Tento soubor obsahuje **závazná pravidla**, kterými se řiď při každém úkolu. Dodržuj ho vždy, stejně jako pravidla psaná přímo v tomto souboru.

- `@~/.claude/RULES.md` – obecná pravidla práce: komunikace s uživatelem, organizace souborů a obsahu, práce se změnami
- `@~/Dev/context/structure/structure.md` – standardní struktura projektu: `CLAUDE.md`, `README.md`, `docs/todo.md`, `docs/decisions.md`, `docs/rules.md` a povinnost průběžně je aktualizovat

Když identifikuješ obecné pravidlo platné napříč projekty, u kterého nevadí, že bude veřejně vidět na githubu, navrhni jeho extrakci do `~/.claude/`.

## Doménové znalosti

Aplikují se podmíněně – jen když pracuju v dané doméně. Nejsou to pravidla pro každý úkol, ale soubory znalostí pro konkrétní typy práce.

- `~/Dev/context/web/web.md` – checklist pro každé webové rozhraní (použitelnost, přístupnost, typografie, formuláře, výkon, GDPR, ...) – načti si ho vždy, když pracuješ na webovém rozhraní
- `~/Dev/context/admin/admin.md` – checklist pro administrační a backoffice rozhraní (struktura, seznamy a tabulky, akce a potvrzování, editace, oprávnění, auditní stopa) – načti si ho vždy, když děláš administraci nebo interní nástroj; platí navíc k `~/Dev/context/web/web.md`
- `~/Dev/context/analytics/` – knowledge base pro implementační webovou analytiku (principy, revize měření a katalog nálezů, měřicí architektura, datová vrstva, GTM konvence, consent, features, systémy, consent lišty, platformy, šablony pro vývojáře) – načti si `~/Dev/context/analytics/analytics.md` vždy, když reviduješ, nasazuješ nebo konfiguruješ webové měření, a z něj se prokliknij dál; platí navíc k `~/Dev/context/web/web.md`
- `~/Dev/context/text/text.md` – redakční standard pro psaní textů (stavba textu, obsah, zakázané obraty, stylistika, gramatika, česká typografie) – načti si ho vždy, když píšeš nebo edituješ souvislý text v češtině: článek, newsletter, dokumentaci, obsah webu
- `~/Dev/context/worktrees/worktrees.md` – worktree layout projektu (kontejner s `.bare`, jeden pracovní adresář na větev, založení a dokončení větve) – načti si ho vždy, když zakládáš nebo rušíš větev v projektu s tímhle layoutem
- `~/Dev/context/coding/coding.md` – standardy návrhu a psaní kódu (návrh a modelování stavu, rozhraní a guardy, automatika a vnější systémy, naming, git, bezpečnost, TypeScript, SQL, frontend) – načti si ho vždy, když navrhuješ datový model nebo píšeš či upravuješ kód

Když identifikuješ znovupoužitelný doménový standard nebo checklist, který se může hodit ve více projektech, ale měl by zůstat soukromý, protože je citlivý nebo patří do osobního know-how, navrhni jeho extrakci do `~/Dev/context/`.

------

## Automatické akce

### Autocommit v projektech

Stav autocommitu pro projekt poznáš podle přítomnosti nadpisu `### Autocommit` v projektovém `CLAUDE.md`, kanonicky pod `## Automatické akce`. Nadpis téhle sekce se od něj schválně liší, aby ji detekce nebrala jako přepínač – tenhle soubor mechanismus definuje, nezapíná ho. Kdykoli je v projektu zapnutý autocommit, commituj po každé zásadní ucelené změně (ne po každém dílčím kroku, ale po každém logickém celku). Pokud má repo nastavený nějaký git remote, po commitu hned pushuj.

### Autoprompt v projektech

Stav autopromptu pro projekt poznáš podle přítomnosti nadpisu `### Autoprompt` v projektovém `CLAUDE.md`, kanonicky pod `## Automatické akce`. Stejně jako výše: nadpis téhle sekce se od něj schválně liší, aby ji detekce nebrala jako přepínač. Kdykoli je v projektu zapnutý autoprompt, každý můj prompt se automaticky uloží do `docs/prompts.md` v projektu (přes `UserPromptSubmit` hook).

------

## Platí jen pro repozitář `~/.claude`

- Každý skill má v `README.md` svou sekci. Když nějaký přidáš nebo zásadně změníš jeho chování, aktualizuj ji rovnou jako součást té změny – stejný styl a tón jako ostatní sekce (osobní, věcné, s konkrétním přínosem). Nečekej na vyžádání.
