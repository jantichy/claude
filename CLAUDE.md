# Globální konfigurace Claude Code

## Závazná pravidla

Tento soubor obsahuje **závazná pravidla**, kterými se řiď při každém úkolu. Dodržuj ho vždy, stejně jako pravidla psaná přímo v tomto souboru.

- `@~/.claude/RULES.md` – obecná pravidla práce: komunikace s uživatelem, organizace souborů a obsahu, práce se změnami
- `@~/Dev/context/structure/structure.md` – standardní struktura projektu, co patří do kterého souboru a povinnost průběžně je aktualizovat

Když identifikuješ obecné pravidlo platné napříč projekty, u kterého nevadí, že bude veřejně vidět na githubu, navrhni jeho extrakci do `~/.claude/`.

## Doménové znalosti

Aplikují se podmíněně – jen když pracuju v dané doméně. Nejsou to pravidla pro každý úkol, ale soubory znalostí pro konkrétní typy práce.

**Proč odkaz a ne `@import`:** projektový `CLAUDE.md` doménu importuje natvrdo, protože tam platí vždy. Tady je to naopak – naráz platí jedna doména, ne všechny, a `@import` celého seznamu by stál kontext v každé session (samotné `web.md` a `admin.md` mají skoro 500 řádků, `analytics/` je celá knowledge base). Odkaz se dodržuje hůř než import, ale je to vědomá volba: cenu za nespolehlivost platím jen tady, ne v projektech.

- `~/Dev/context/web/web.md` – checklist pro každé webové rozhraní (použitelnost, přístupnost, typografie, formuláře, výkon, GDPR, ...) – načti si ho vždy, když pracuješ na webovém rozhraní
- `~/Dev/context/web/admin.md` – checklist pro administrační a backoffice rozhraní (struktura, seznamy a tabulky, akce a potvrzování, editace, oprávnění, auditní stopa) – načti si ho vždy, když děláš administraci nebo interní nástroj; platí navíc k `~/Dev/context/web/web.md`
- `~/Dev/context/analytics/` – knowledge base pro implementační webovou analytiku (principy, revize měření a katalog nálezů, měřicí architektura, datová vrstva, GTM konvence, consent, features, systémy, consent lišty, platformy, šablony pro vývojáře) – načti si `~/Dev/context/analytics/analytics.md` vždy, když reviduješ, nasazuješ nebo konfiguruješ webové měření, a z něj se prokliknij dál; platí navíc k `~/Dev/context/web/web.md`
- `~/Dev/context/text/text.md` – redakční standard pro psaní textů (stavba textu, obsah, zakázané obraty, stylistika, gramatika, česká typografie) – načti si ho vždy, když píšeš nebo edituješ souvislý text v češtině: článek, newsletter, dokumentaci, obsah webu
- `~/Dev/context/design/design.md` – obecné standardy vizuální tvorby (kontrast a čitelnost, barva a barvoslepost, hierarchie a prázdné místo) – načti si ho vždy, když navrhuješ cokoli vizuálního; v doméně je navíc `~/Dev/context/design/slides.md` – prezentace a slajdy (kolik informace na slajd, nadpis jako tvrzení, tempo, čitelnost v sále, animace, provoz), načti si ho vždy, když děláš nebo reviduješ promítanou prezentaci: školení, přednášku, pitch, prezentaci výsledků. Je to znalost, ne Honzův vizuál – ten drží `~/Dev/context/brand/brand.md`
- `~/Dev/context/worktree/worktree.md` – worktree layout projektu (kontejner s `.bare`, jeden pracovní adresář na větev, založení a dokončení větve) – načti si ho vždy, když zakládáš nebo rušíš větev v projektu s tímhle layoutem
- `~/Dev/context/brand/brand.md` – osobní brand a pozicování Jana Tichého (zastřešení, čím se odlišuje, cílové skupiny, vztah k samostatné značce kurzu AI) – načti si ho vždy, když píšeš cokoli, co Honzu prezentuje navenek: web, prodejní stránku, inzerát, medailonek, bio, nabídku. Je to zdroj pravdy; projekty z něj vychází a drží jen svůj překlad do kanálu
- `~/Dev/context/training/training.md` – jak se staví a vede školení: formáty, didaktický postoj, stavba obsahu, práce se skupinou, udržování obsahu – načti si ho vždy, když připravuješ nebo upravuješ školení, kurz nebo workshop. Co kdy proběhlo, drží evidence ve `~/Dev/context/speaking/`; tahle doména říká, jak se to dělá
- `~/Dev/context/coding/coding.md` – standardy návrhu a psaní kódu (návrh a modelování stavu, rozhraní a guardy, automatika a vnější systémy, naming, git, bezpečnost, ověřování a brány kvality včetně zelené linky a kontraktu příkazů, TypeScript, SQL, frontend) – načti si ho vždy, když navrhuješ datový model nebo píšeš či upravuješ kód

Pozor na zařazení `brand/`: sám o sobě je to **korpus** (fakt o tom, kdo Honza je), ne standard – v `~/Dev/context/CLAUDE.md` je vedený tak. V seznamu výš je proto, že se na rozdíl od zbytku korpusu načítá **podmíněně jako doménová znalost**, protože platí pro každý text mířící ven.

Zbytek korpusu se nenačítá paušálně: `archive/` (všechny Honzovy texty), `compose/` (jeho hlas, spouští se skillem `/compose`), `speaking/` (školení, přednášky, konzultační i školicí klienti, ohlasy) a `organizations/` (profily organizací, se kterými Honza pracuje – kdo tam sedí, kdo co schvaluje, na čem jedou). Sáhni po nich, když potřebuješ doklad nebo data, ne pravidlo. **U `organizations/` platí, že projekt pro konkrétní organizaci si její profil načítá sám** ve svém `CLAUDE.md`. Rozcestník je v `~/Dev/context/CLAUDE.md`.

Když identifikuješ znovupoužitelnou doménovou znalost, která se může hodit ve více projektech, ale měla by zůstat soukromá, protože je citlivá nebo patří do osobního know-how, navrhni její extrakci do `~/Dev/context/`.

------

## Automatické akce

### Autocommit v projektech

Stav autocommitu pro projekt poznáš podle přítomnosti nadpisu `### Autocommit` v projektovém `CLAUDE.md`, kanonicky pod `## Automatické akce`. Nadpis téhle sekce se od něj schválně liší, aby ji detekce nebrala jako přepínač – tenhle soubor mechanismus definuje, nezapíná ho. Kdykoli je v projektu zapnutý autocommit, commituj po každé zásadní ucelené změně (ne po každém dílčím kroku, ale po každém logickém celku). Pokud má repo nastavený nějaký git remote, po commitu hned pushuj.

### Autoprompt v projektech

Stav autopromptu pro projekt poznáš podle přítomnosti nadpisu `### Autoprompt` v projektovém `CLAUDE.md`, kanonicky pod `## Automatické akce`. Stejně jako výše: nadpis téhle sekce se od něj schválně liší, aby ji detekce nebrala jako přepínač. Kdykoli je v projektu zapnutý autoprompt, každý můj prompt se automaticky uloží do `docs/prompts.md` v projektu (přes `UserPromptSubmit` hook).
