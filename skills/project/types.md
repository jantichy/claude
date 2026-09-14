# Typy projektu

Katalog ke kroku 11 v `SKILL.md`: jak se na typ ptát, co která volba znamená a co se z ní zapisuje do projektového `CLAUDE.md`. Vytažené ze `SKILL.md`, aby se do něj nemusel načítat pokaždé – rozhoduje se podle něj jednou za projekt.

- [Jak se ptát](#jak-se-ptát)
- [Co se zapisuje do `CLAUDE.md`](#co-se-zapisuje-do-claudemd)
- [U typu Vývoj se ptej ještě na aplikaci versus nástroj](#u-typu-vývoj-se-ptej-ještě-na-aplikaci-versus-nástroj)

## Jak se ptát

**Kroky životního cyklu do popisu typu nevypisuj**, odkaz na *Životní cyklus projektu* v `~/.claude/RULES.md` stačí. Je to zvláštní případ obecného pravidla *Neopisuj seznam, který má vlastní zdroj pravdy* (`~/.claude/skills/SKILLS.md`, *Jak se píše text uvnitř*), kde stojí i to, čím se vykoupilo.

Typů je šest, ale AskUserQuestion bere najednou nejvýš čtyři volby. Ptej se proto ve dvou úrovních – nejdřív na oblast, pak na typ uvnitř ní. Uživatel klikne nejvýš dvakrát a žádný typ se neztratí.

**První otázka** (AskUserQuestion): „Čeho se projekt hlavně týká?“ Tři volby:

| Volba | Co následuje |
|---|---|
| Vývoj software a webů | druhá otázka: **Vývoj** / **Web** |
| Analytika | druhá otázka: **Nasazení webové analytiky** / **Data a výzkum** |
| Obsah | typ je rovnou **Psaní a obsah**, druhá otázka odpadá |

Oblasti jsou schválně dělené podle **povahy práce, ne podle použité technologie** – vývoj software a webů je stavění, analytika je měření a vyhodnocování, obsah je psaní. Až přibude další typ, patří do té oblasti, jejíž povahu sdílí; pokud do žádné, je to signál, že chybí čtvrtá oblast, ne že se má nacpat do nejbližší.

**Až se oblasti zaplní.** Dvouúrovňová otázka má strop 16 typů (4 oblasti × 4 typy). Až na něj narazíš, nepřidávej třetí úroveň – přejdi na **N kol po čtyřech**: jedno kolo na každou oblast, `multiSelect: true`, uvozené „Co všechno z oblasti <oblast> pro tenhle projekt platí? Když nic, nic nezaškrtávej.“ Kol může být libovolně mnoho, takže limit AskUserQuestion přestane omezovat.

Ta změna má důsledek, který je potřeba unést vědomě: projekt tím přestane mít jeden typ a bude mít **sadu typů** – klidně prázdnou (= **Ostatní**), klidně **Vývoj** i **Web** zároveň. Do `CLAUDE.md` pak nelep popisy pod sebe mechanicky: slož je do jednoho odstavce a **vyřeš rozpory**. „Vývoj“ předepisuje proces zadání a plánu, „Web“ ho výslovně nechce – když padnou oba, rozhodni podle hlavní náplně projektu a napiš jen to, co platí.

Volbu „Ostatní“ mezi možnosti **nedávej** – AskUserQuestion ji nabízí sám jako „Other“. Když ji uživatel použije, typ je **Ostatní** a druhá otázka odpadá.

Do `CLAUDE.md` přidej sekci `## Typ projektu` s krátkým popisem:

- **Vývoj** – „Vývojářský projekt – postupuj podle *Životního cyklu projektu* v `~/.claude/RULES.md`, celého a v pořadí, které tam stojí.“ Navíc přidej pravidlo: „Před implementací nové funkce nejdřív aktualizuj příslušný dokument v `docs/` (doc-first).“ **A polož doplňující otázku podle odstavce níž.**
- **Web** – „Webové rozhraní – obsah, struktura, šablony, ne proces zadání a plánu.“
- **Nasazení webové analytiky** – „Implementace měření na cizím webu – revize existujícího nastavení, měřicí plán, GTM, GA4, consent, reklamní systémy. Výstupem je funkční a doložitelné měření plus dokumentace, ne aplikační kód.“ Navíc přidej pravidlo: „Každá změna v měření musí být před publikováním ověřená v Preview/DebugView a po nasazení znovu na produkci; do `docs/decisions.md` patří i to, co se měřit záměrně nebude a proč.“
- **Psaní a obsah** – „Projekt zaměřený na psaní a obsah, ne na vývoj software – bez procesu zadání a plánu.“
- **Data a výzkum** – „Jednorázová datová/výzkumná analýza – výstupem jsou zjištění a report, ne nasazovaný kód.“
- **Ostatní** – „Projekt mimo výš uvedené kategorie.“

### U typu Vývoj se ptej ještě na aplikaci versus nástroj

`~/Dev/context/coding/architecture.md` rozlišuje dvě úrovně a **ptá se na následek chyby, ne na velikost projektu**. Polož tedy ještě jednu otázku (AskUserQuestion, dvě volby) a **návrh odpověz sám** z toho, co jsi o projektu zjistil – uživatel ho jen potvrdí:

| Volba | Kdy na ni sedí |
|---|---|
| **aplikace** | platí aspoň jedno: data přežijí běh a někdo se o ně opírá; přistupuje k tomu víc lidí nebo rolí; tečou přes to peníze nebo osobní údaje; sahá to na cizí systém |
| **nástroj** | nic z toho – skript, generátor, jednorázová migrace |

**Při pochybnosti je to aplikace**, a řekni to uživateli nahlas; náklad na dodržení standardu je menší než na jeho dodatečné zavedení.

Do popisu typu v `CLAUDE.md` pak připoj jednu z vět:

- aplikace – „Je to **aplikace** ve smyslu `~/Dev/context/coding/architecture.md` – platí celý, včetně kontrolního seznamu *Minimum hotové aplikace*. Chybějící položka toho seznamu je nedodělek, ne zjednodušení; vědomá výjimka patří do `docs/decisions.md` i s důvodem.“
- nástroj – „Je to **nástroj** ve smyslu `~/Dev/context/coding/architecture.md` – platí z něj jen sekce *Co platí i pro nástroj*. Splní-li projekt některé kritérium aplikace (druhá role, první platba, cizí systém, uživatel kromě autora), úroveň se zvedne a návrh se dorovná tehdy, ne později.“

**Soubor se neimportuje**, jen odkazuje – ze stejného důvodu jako `quality.md` (viz `checklists.md`). Odkaz v projektovém `CLAUDE.md` ale platí v každé session, protože ten se rozbaluje celý.
