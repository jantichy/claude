# Globální konfigurace Claude Code

## Závazná pravidla

Následující soubory obsahují **závazná pravidla**, kterými se řiď při každém úkolu. Dodržuj je vždy, stejně jako pravidla psaná přímo v tomhle souboru.

- @~/.claude/RULES.md – obecná pravidla práce: komunikace s uživatelem, organizace souborů a obsahu, rozhodování a rozsah, práce se změnami
- @~/.claude/PTYDEPE.md – tabulka termínů, na kterých jsme se výslovně dohodli: co se místo čeho používá a v jakém rozsahu. Úvahy, zamítnuté varianty a historii náhrad drží `~/.claude/skills/ptydepe/terms.md`, který se schválně neimportuje – za běhu stačí tabulka
- `~/.claude/STRUCTURE.md` – standardní struktura projektu, co patří do kterého souboru a povinnost průběžně je aktualizovat. **Odkaz, ne import** – je to katalog k nahlédnutí, ne pravidlo pro každou odpověď; načti si ho, než do některého z těch souborů zapíšeš. Kam který zápis míří, říká `RULES.md`, *Kam co zapsat*
- `~/.claude/skills/LIFECYCLE.md` – rozhraní kroků životního cyklu: co který dělá, co po něm platí, proč stojí v tom pořadí. **Odkaz, ne import** – načti si ho, jakmile v některém kroku stojíš; rámeček s pořadím drží `RULES.md`, *Životní cyklus projektu*
- `~/.claude/WORKTREE.md` – worktree layout projektu: kontejner s `.bare`, jeden pracovní adresář na větev, zakládání a dokončení větve. **Odkaz, ne import** – platí jen v projektu s tímhle uspořádáním, kde si ho natáhne rozcestník v kořeni kontejneru; zapíná a ruší ho `/worktree`

Když identifikuješ obecné pravidlo platné napříč projekty, u kterého nevadí, že bude veřejně vidět na githubu, navrhni jeho extrakci do `~/.claude/`.

## Doménové znalosti

Aplikují se podmíněně – jen když pracuju v dané doméně. Nejsou to pravidla pro každý úkol, ale soubory znalostí pro konkrétní typy práce.

**Proč odkaz a ne `@import`:** projektový `CLAUDE.md` doménu importuje natvrdo, protože tam platí vždy. Tady je to naopak – naráz platí jedna doména, ne všechny, a `@import` celého seznamu by stál kontext v každé session (samotné `web.md` a `admin.md` mají skoro 500 řádků, `analytics/` je celá knowledge base). Odkaz se dodržuje hůř než import, ale je to vědomá volba: cenu za nespolehlivost platím jen tady, ne v projektech.

- `~/Dev/context/web/web.md` – checklist pro každé webové rozhraní (použitelnost, přístupnost, typografie, formuláře, výkon, GDPR, …) – načti si ho vždy, když pracuješ na webovém rozhraní
- `~/Dev/context/web/admin.md` – checklist pro administrační a backoffice rozhraní (struktura, seznamy a tabulky, akce a potvrzování, editace, oprávnění, auditní stopa) – načti si ho vždy, když děláš administraci nebo interní nástroj; platí navíc k `~/Dev/context/web/web.md`
- `~/Dev/context/analytics/` – knowledge base pro implementační webovou analytiku (principy, revize měření a katalog nálezů, měřicí architektura, datová vrstva, GTM konvence, consent, features, systémy, consent lišty, platformy, šablony pro vývojáře) – načti si `~/Dev/context/analytics/analytics.md` vždy, když reviduješ, nasazuješ nebo konfiguruješ webové měření, a z něj se prokliknij dál; platí navíc k `~/Dev/context/web/web.md`
- `~/Dev/context/text/text.md` – redakční standard pro psaní textů (stavba textu, obsah, zakázané obraty, stylistika, gramatika, text odkazu, sjednocené psaní slov) – načti si ho vždy, když píšeš nebo edituješ souvislý text v češtině: článek, newsletter, dokumentaci, obsah webu
- `~/Dev/context/text/typography.md` – česká typografie (interpunkce a znaky, mezery, čísla, jednotky, datum a čas, výčty, ustálené zápisy jmen) – načti si ji vždy, když sázíš český text – tedy spolu s `text.md`, ale i tam, kde souvislý text nevzniká: slajd, popisek grafu, mikrocopy, dokumentaci
- `~/Dev/context/design/design.md` – obecné standardy vizuální tvorby (kontrast a čitelnost, barva a barvoslepost, hierarchie a prázdné místo) – načti si ho vždy, když navrhuješ cokoli vizuálního; v doméně je navíc `~/Dev/context/design/slides.md` – prezentace a slajdy (kolik informace na slajd, nadpis jako tvrzení, tempo, čitelnost v sále, animace, provoz), načti si ho vždy, když děláš nebo reviduješ promítanou prezentaci: školení, přednášku, pitch, prezentaci výsledků. Je to znalost, ne Honzův vizuál – ten drží `~/Dev/context/brand/brand.md`
- `~/Dev/context/brand/brand.md` – osobní brand a pozicování Jana Tichého (zastřešení, čím se odlišuje, cílové skupiny, vztah k samostatné značce kurzu AI) – načti si ho vždy, když píšeš cokoli, co Honzu prezentuje navenek: web, prodejní stránku, inzerát, medailonek, bio, nabídku. Je to zdroj pravdy; projekty z něj vychází a drží jen svůj překlad do kanálu
- `~/Dev/context/training/training.md` – jak se staví a vede školení: formáty, didaktický postoj, stavba obsahu, práce se skupinou, udržování obsahu – načti si ho vždy, když připravuješ nebo upravuješ školení, kurz nebo workshop. Co kdy proběhlo, drží evidence ve `~/Dev/context/speaking/`; tahle doména říká, jak se to dělá
- `~/Dev/context/business/business.md` – obchodní stránka práce: dnes fakturace (sazby, daňový režim, dohody s klienty, deník výjimek k obdobím, stopy práce pro dohledání nenatrackovaného času) – načti si ji vždy, když vystavuješ faktury, řešíš, za co a kolik se účtuje, nebo dohledáváš čas, který se zapomněl natrackovat; řídí ji skill `/invoicing`, který sám žádná čísla neobsahuje
- `~/Dev/context/coding/coding.md` – standardy návrhu a psaní kódu (návrh a modelování stavu, rozhraní a guardy, automatika a vnější systémy, naming, git, bezpečnost, TypeScript, SQL, frontend) – načti si ho vždy, když navrhuješ datový model nebo píšeš či upravuješ kód; v doméně je navíc `~/Dev/context/coding/quality.md` – ověřování a kontroly kvality (kontrakt příkazů, průběžná kontrola, prahy kontrol, závislosti, stupňování autonomie, bezpečnostní audit), načti si ho, když zakládáš nebo přenastavuješ projekt, pouštíš revizi či nasazení, nebo rozhoduješ, jestli je práce hotová. Při běžném psaní kódu stačí `coding.md`

Pozor na zařazení `brand/`: sám o sobě je to **korpus** (fakt o tom, kdo Honza je), ne standard – v `~/Dev/context/CLAUDE.md` je vedený tak. V seznamu výš je proto, že se na rozdíl od zbytku korpusu načítá **podmíněně jako doménová znalost**, protože platí pro každý text mířící ven.

Zbytek korpusu se nenačítá paušálně: `archive/` (všechny Honzovy texty), `compose/` (jeho hlas, spouští se skillem `/compose`), `speaking/` (školení, přednášky, konzultační i školicí klienti, ohlasy) a `organizations/` (profily organizací, se kterými Honza pracuje – kdo tam sedí, kdo co schvaluje, na čem jedou). Sáhni po nich, když potřebuješ doklad nebo data, ne pravidlo. **U `organizations/` platí, že projekt pro konkrétní organizaci si její profil načítá sám** ve svém `CLAUDE.md`. Rozcestník je v `~/Dev/context/CLAUDE.md`.

- **Znalostní báze psaní:** `~/Dev/context/compose/`, archiv textů `~/Dev/context/archive/`. Čte je skill `/compose` – tenhle řádek je jediné místo, kde ty cesty stojí, takže se po přesunu opravují tady, ne ve skillu.

Když identifikuješ znovupoužitelnou doménovou znalost, která se může hodit ve více projektech, ale měla by zůstat soukromá, protože je citlivá nebo patří do osobního know-how, navrhni její extrakci do `~/Dev/context/`.

