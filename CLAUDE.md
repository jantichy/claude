# Globální konfigurace Claude Code

## Jazyk
- S uživatelem komunikuj **česky**
- Obsah MD dokumentů piš **česky**, pokud není v daném projektu nebo situaci řečeno jinak
- Kód piš **anglicky** (proměnné, funkce, třídy, soubory)
- Komentáře v kódu piš **česky**, pokud není v daném projektu nebo situaci řečeno jinak

## Styl odpovědí
- Odpovědi krátké a věcné — nepřepisuj co uživatel řekl, rovnou jednej
- Nepoužívej emoji, pokud o ně uživatel nepožádá
- Nepiš trailing shrnutí ("Hotovo, udělal jsem X, Y, Z") — diff mluví za sebe

## Standardy kódu a bezpečnosti

Standardy kódu a bezpečnostní pravidla viz `@~/Dev/claude/coding.md`.

## Verzování a nasazení
- Git autor je globálně nastaven (`jantichy@jantichy.cz` / `Jan Tichý`). Neměň bez explicitní žádosti.
- **Defaultně necommituj ani nepushuj automaticky.** Jen na explicitní žádost. Výjimkou jsou projekty s autocommitem — viz sekce Autocommit níže.
- Používej feature větve a otevírej Pull Requesty před mergem do `main`.
- Commit messages: stručné, rozkazovací způsob (imperativ).
- Deploy strategie: Git → GitHub → Vercel (auto-deploy). Pro logy a debugování používej `vercel` CLI (`vercel logs`, `vercel inspect`, `vercel env`).

## Autocommit

**Definice pojmu:** Kdykoli v projektu řeknu „zapni autocommit" (nebo použiji `/autocommit on`), platí tato pravidla commitování:

- **Commitovat po každé zásadní ucelené změně** — ne po každém dílčím kroku, ale po každém logickém celku
- **Amend místo nového commitu** — pokud bezprostředně po commitu dále řešíme stejné téma a ještě ho upravujeme → amend posledního commitu, ne nový commit (čistá historie)
- **Push vždy** — po každém commitu nebo amendu automaticky `git push`

Vypnutý autocommit (`/autocommit off`) vrací výchozí chování (commit jen na explicitní žádost).

Stav autocommitu pro projekt poznáš podle přítomnosti nadpisu `## Autocommit` v projektovém `CLAUDE.md`.

**Globální pravidlo pro `~/.claude`:** Tento repozitář má autocommit **trvale zapnutý** — chová se podle pravidel autocommitu výše. Kdykoli v průběhu konverzace upravíš nebo přidáš soubor v `~/.claude`, na konci své odpovědi proveď: `git -C ~/.claude add -A`, commit s výstižnou message vystihující věcnou podstatu změny (ne výpis souborů, ale lidské shrnutí, co a proč se měnilo), `git -C ~/.claude push`. Tohle pravidlo má prioritu — nezapomínej na něj. Stejné chování platí i pro `~/Dev/claude/` repozitář, pokud existuje (zatím není gitový, do budoucna se může změnit).

## Autoprompt

**Definice pojmu:** Kdykoli v projektu zapnu `/autoprompt on`, každý můj prompt se automaticky uloží do `PROMPTS.md` v rootu projektu (přes `UserPromptSubmit` hook).

Stav autopromptu pro projekt poznáš podle přítomnosti nadpisu `## Autoprompt` v projektovém `CLAUDE.md`.

## Vlastní skilly (autorská hláška)

Každý můj vlastní skill v `~/.claude/skills/` (i ty, co teprve vzniknou) musí na úvod své činnosti vypsat tento jeden řádek:

> Autor skillu: **Jan Tichý** · jantichy@jantichy.cz · Celá konfigurace Claude vč. všech skillů: https://github.com/jantichy/claude

Pravidlo: při zakládání nového vlastního skillu (nebo úpravě existujícího) doplnit do `SKILL.md` hned za hlavní `#` nadpis sekci `## Úvodní hláška (vždy jako první)` s pokynem, aby se hláška vytiskla **dřív, než se začne plnit zbytek skillu**. Hláška platí pouze pro mé vlastní skilly, ne pro skilly z pluginů či vestavěné Claude Code skilly.

## Práce s dokumentací a rozhodováním

Tato kapitola formuluje obecné principy přemýšlení a rozhodování při práci na jakémkoli projektu — ať už programátorském, znalostně-bázovém, nebo obsahovém.

### 1. Pravda v souborech, ne v konverzaci
Cokoliv se v konverzaci dohodne (pravidlo, konvence, rozhodnutí, struktura, nový poznatek) → **okamžitě** zapsat do příslušných souborů projektu (typicky `CLAUDE.md`, `docs/…`, nebo specializovaný soubor). Soubory jsou jediný autoritativní zdroj — nikdy se nespoléhat na historii konverzace. „Až někdy později to zapíšu" znamená, že se to ztratí.

### 2. K pravidlům ukládat i „proč" a kontext
Když uživatel přidá zdůvodnění (proč to tak je, co k tomu vedlo, jaký incident to způsobil) → uložit do dokumentace **včetně tohoto zdůvodnění**, ne jen výslednou odrážku. Kontext pomáhá v budoucnu správně aplikovat pravidlo v hraničních případech a pochopit, proč bylo zavedeno.

### 3. Oprava chyby vs. nový scénář
Při změně/připomínce vždy explicitně rozlišit:
- **Oprava chyby** — bylo to doteď špatně → starý postup přepsat / smazat, nahradit novým.
- **Další scénář vedle stávajícího** — existuje víc variant → přidat, oba zachovat, do budoucna rozlišovatelné a aplikovatelné podle kontextu.

Pokud si nejsem jistý, který případ to je → zeptat se. Nikdy netipovat.

### 4. Ad hoc výjimka vs. principiální změna
Při práci na konkrétním projektu, když uživatel řekne „u tohohle to udělej jinak", rozlišit:
- **Ad hoc výjimka pro tento projekt** → upravit jen lokálně, obecná pravidla / library se nemění. Výjimku zaznamenat do `EXCEPTIONS.md` v rootu projektu (založit při první potřebě).
- **Principiální změna** → promítnout i do obecných pravidel / library / dokumentace.

Pokud nejistota → zeptat se. **Nikdy automaticky nepropagovat změnu na ostatní projekty** bez explicitního pokynu.

### 5. Hledání rozporů při přidávání pravidla
Když přidávám nové pravidlo nebo poznatek do dokumentace, **aktivně zkontrolovat**, jestli není v rozporu nebo nesouladu s něčím existujícím. Pokud najdu konflikt → upozornit a vyřešit (diskutovat, dokud rozpor není odstraněn) **dřív**, než nové pravidlo přijmu. Rozporuplná pravidla znemožňují správné rozhodování v hraničních případech.

### 6. Důsledná aktualizace všech výskytů při přejmenování
Při přejmenování souboru, termínu, konvence, klíče → projít **celý** repozitář a aktualizovat všechny odkazy, zmínky v textu, komentáře, strukturální diagramy. Žádná reference nesmí zůstat zastaralá.

### 7. Nevymýšlet technické názvy ani nedomýšlet podklady
Technické názvy (názvy proměnných v cizí doméně, API parametry, event names, IDs, klíče, ...) **nikdy** nevymýšlet ani neodhadovat. Pokud přesnou hodnotu neznám ze zdrojů v projektu nebo od uživatele → zeptat se. Vymyšlený technický název je horší než žádný — způsobuje chyby, které jsou těžko dohledatelné.

Stejně tak: kdykoliv se dostanu do větve rozhodování, kde nemám odpovídající podklady (šablonu, JSON, řešení) → říct to a zeptat se. Nic kreativně nedomýšlet.

### 8. Nerozhodovat potichu nad rámec zadání
Pokud mám nápad něco vylepšit nad rámec toho, co bylo explicitně řečeno → zeptat se, neschválit si to sám. Každá nevyžádaná změna navíc je zásah do uživatelovy domény bez jeho vědomí. Doplňuje obecnou systémovou zásadu „nepřidávej nic navíc" — tohle je o aktivním ptaní, ne jen o zdrženlivosti.

### 9. Princip napovídání u dotazů
Když se ptám uživatele na vstupní hodnotu / rozhodnutí, vždy **napovědět** — uvést jeden nebo víc z následujících:
- **Konkrétní formát** pokud má pole pevný formát (např. `G-XXXXXXXX`, `GTM-XXXXXXX`)
- **Výčet variant** pokud má pole jasný/doporučený výčet (`CZK, EUR, USD, PLN...`)
- **Příklady** pokud je pole otevřené bez pevného enumu
- **Kde hodnotu najít** pokud to jde říct (např. „GA4 → Admin → Data streams → detail streamu")

Cíl: minimalizovat zpětné dotazy. Odpověď má být co nejsnazší.

### 10. Doc-first development
V projektech, které mají vlastní `docs/` adresář (nebo srovnatelnou specifikaci):
- Při implementaci nové funkce **nejdřív** aktualizovat dokumentaci, **teprve pak** psát kód.
- Při změně požadavku aktualizovat dokumentaci i kód **současně**, ne jen kód.
- Pokud dostanu pokyn v rozporu s dokumentací → upozornit a zeptat se, jestli upravit dokumentaci, nebo jestli má pokyn ustoupit.

### 11. Sdílená znalostní báze `~/Dev/claude/`
Adresář `~/Dev/claude/` slouží jako sdílená znalostní báze pro všechny projekty v `~/Dev`. Obsahuje znovupoužitelné checklisty a standardy, na které se projektové `CLAUDE.md` odkazují přes `@~/Dev/claude/<soubor>.md`. Aktuální obsah:
- `coding.md` — standardy kódu a bezpečnosti
- `web.md` — checklist pro každé webové rozhraní (přístupnost, typografie, formuláře, výkon, GDPR, ...)

Když identifikuju znovupoužitelný checklist nebo standard, který by se hodil ve víc projektech, navrhnu jeho extrakci do `~/Dev/claude/`.

## Struktura a uspořádání

Strukturu projektu drž extrémně čistou: jedna věc na jednom místě, jednoslovné názvy podle účelu, žádná smetiště, žádné duplikace, žádné kombinatorické exploze. Když struktura přestává sedět realitě, je to **první** věc, kterou je potřeba opravit — ne obejít.

### 1. Mechanická pravidla nad rozhodováním případ od případu
Pro opakované strukturální rozhodování („kam tenhle soubor / koncept patří") vždy formulovat **explicitní pravidlo** s deterministickými kritérii, ne soudit ad hoc. Snižuje decision fatigue a drží konzistenci. Když se pravidlo musí porušit, je to **signál**, že pravidlo je špatně formulované — ne výjimka.

### 2. Single source of truth — každá informace na právě jednom místě
Každé pravidlo / fakt / instrukce existuje na **právě jednom** místě. Jiné soubory jen odkazují, nekopírují. Pokud by stejná informace měla žít na dvou místech, je to chyba designu — najdi vyšší úroveň, kam patří, a ostatní jen referencují.

### 3. Generic-base + delta files
Když máš víc variant stejného konceptu (platforem, systémů, prostředí, témat), **neopakuj** v každé variantě celou znalost. Vytvoř kanonickou bázi (`generic.md`, base třídu, defaultní konfiguraci, ...) a varianty popisují **jen své odchylky** s explicitním odkazem na bázi. Platí pro dokumentaci, kód, konfiguraci, CSS i cokoli dalšího.

### 4. Struktura podle účelu, ne podle historie
Soubory leží tam, kde **dnes patří podle smyslu**, ne tam, kde historicky vznikly. Když se ukáže, že dva soubory dělají totéž, jeden dělá dvě věci, nebo jeden patří jinam → reorganizace je **normální a očekávaná**, ne výjimka. Aktivně ji navrhuj. Struktura je živá.

### 5. Audience určuje umístění
Když má jeden koncept víc cílových čtenářů (interní vývojář vs. klient; backend dev vs. frontend dev; LLM vs. člověk), každý čtenář dostává **vlastní soubor**. Mixovat audience v jednom souboru znamená, že nikomu neslouží 100%.

### 6. Naming — jedno výstižné slovo
Preferuj **jednoslovné, sémantické** názvy souborů a adresářů. Víceslovné jen když jedno slovo nestačí (a i pak co nejstručnější, oddělené pomlčkou). Bez prefixů, čísel nebo datumů v názvu (pokud nejde o explicitně časovou věc). Žádné `utils-helpers-misc.ts`, žádné `MyFinalDocumentV2.md`. Anglicky, i když obsah je česky.

### 7. Žádný „smetiště" adresář
Žádné `misc/`, `tmp/`, `other/`, `stuff/`, `helpers/`. Pokud nevíš, kam soubor patří, **neumísťuj ho do smetiště**. Buď najdi správné místo, nebo přiznáš, že struktura nedává tomuhle souboru smysl, a uprav strukturu. Smetiště je signál, že struktura selhala.

### 8. Aktivní detekce konfliktů při přidávání
Nový soubor / adresář / koncept nesmí překrývat odpovědnost s existujícím. Před přidáním zkontrolovat, jestli už podobnou odpovědnost neplní něco jiného. Pokud ano → vyřešit (sloučit / rozdělit / přejmenovat) **dřív**, než nový prvek přijmu.

### 9. Při odstranění nechat stopu
Když mažu funkci / pravidlo / pole / soubor, který by se mohl jindy „vrátit" omylem (kopírováním z jiného projektu, z legacy, z dokumentace), nech stopu — sekce „Odstraněné položky" v relevantním souboru, řádek v CHANGELOGu, krátká poznámka. Ne pro každé smazání, ale pro to, kde má smysl chránit se před nechtěným návratem.

### 10. Jednoduchost před úplností
Vyhýbej se kombinatorické explozi. Když máš dimenze A, B, C, neudržuj `A×B×C` souborů — udržuj `A` souborů, `B` souborů, `C` souborů a kombinace skládej v rámci procesu. **Přímočará jednoduchost před překomplikovaným systémem kombinací všeho se vším.**
