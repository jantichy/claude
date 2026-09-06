# Konfigurace Claude Code

Moje osobní konfigurace Claude Code – pravidla, skilly, hooky a status line, sdílená pro inspiraci.

- **Slug:** `claude`
- **Repozitář:** https://github.com/jantichy/claude

## Výjimky z obecných pravidel

- **Blok metadat je tady, ne v kořenovém `CLAUDE.md`**, jak jinak velí `~/Dev/context/structure/structure.md`. Kořenový soubor je uživatelský a rozbaluje se do každé session v každém projektu – metadata tohohle repozitáře tam nepatří, mátla by v cizím projektu.
- **`/attack` ani `/release` se tu nikdy nepouštějí.** Repozitář je konfigurace, ne aplikace – není co spustit ani kam nasadit. Životní cyklus tady končí `/cleanupem`. Zapsáno schválně, ne odvozeno (`~/.claude/RULES.md`, *Zapiš i to, co vědomě nemáš*).
- **Tenhle repozitář má `todo.md`, `done.md` i `decisions.md` v `~/Dev/context/`**, ne u sebe. Platí to pro každý skill, který do nich zapisuje a zároveň se tu pouští – `/review`, `/oponent`, `/consistency`, `/cleanup` a `/skill`. (`/attack` a `/release` se tu nepouštějí vůbec, viz výš.) **U `/skill` to platí bezvýhradně**, protože jako jediný nikde jinde běžet nemůže – spravuje skilly, a ty jsou jen tady. A **neptej se na to pokaždé znovu**:

  | Co | Kam | Jak |
  |---|---|---|
  | odložený nález, zaparkovaný bod | `~/Dev/context/todo.md` | do sekce podle domény, které se týká |
  | rozhodnutí, zamítnutá varianta, vědomá mezera | `~/Dev/context/decisions.md` | tamtéž podle domény; týká-li se rozhodnutí **jednoho skillu**, patří rovnou do jeho `SKILL.md` k místu, kde platí – tam ho příště najde ten, kdo ho potřebuje |
  | záznam dokončeného průchodu (`## Průchody životním cyklem`) | `~/Dev/context/done.md` | u `/review` jen když má smysl ho pak číst – jeho čtenářem je `/release`, a ten se tu nepouští. **U `/oponent` vždy:** jeho čtenářem je příští `/oponent`, který podle svého SKILL.md bez seznamu úhlů neví, s čím se má srovnávat |

  Je to jediné místo, kde struktura tohohle repozitáře sahá ven; důvod je, že konfigurační vrstva je téma, které ta znalostní báze už drží. **Pozor: platí to jen pro tenhle repozitář** – proto to stojí tady v projektovém souboru, a ne v kořenovém `CLAUDE.md`, který se rozbaluje do každé session v každém projektu.
- **`docs/` neexistuje.** Repozitář není vyvíjený projekt, ale konfigurace; `todo.md`, `done.md`, `decisions.md` ani `rules.md` nemá a nezakládají se.

## Instrukce pro tenhle repozitář

Projektové instrukce pro práci **v tomhle repozitáři**. Načítají se jen tady, na rozdíl od `~/.claude/CLAUDE.md`, který je uživatelský a jde do každé session v každém projektu.

@~/.claude/skills/SKILLS.md

- **Norma výš platí pro každou cestu ke změně skillu:** ruční úpravu, `/skill` i cizí nástroj typu `skill-creator` nebo `superpowers:writing-skills`. Ty mají vlastní představu o tvaru a prosadí ji, když jim nic neřekneš; tenhle řádek je to, co jim ji přebíjí (`~/.claude/RULES.md`, *Přednost pravidel*). Postup zakládání, revize a rušení drží `/skill`, ne norma.
- **Každý skill má dvě README.** Vlastní `skills/<jméno>/README.md` – vizitku pro člověka zvenčí, na kterou se posílá odkaz –, a k tomu jeden odstavec v kořenovém `README.md` zakončený odkazem na tu vizitku. Tvar obojího drží `skills/SKILLS.md`, *README skillu*, a vynucují ho testy. Když skill přidáš nebo zásadně změníš jeho chování, aktualizuj obojí rovnou jako součást té změny – nečekej na vyžádání.

## Příkazy

Kontrakt příkazů (`~/Dev/context/coding/coding.md`, *Ověřování a brány kvality*). Zelená linka ho tady najde v `.claude/CLAUDE.md` a příkazy spouští v kořeni repozitáře.

- typecheck: swiftc -typecheck skills/*/*.swift
- lint: shellcheck -x --severity=info ./*.sh skills/*/*.sh && ruff check --isolated --select F,E9 skills/*/scripts/*.py tests/*.py
- test: python3 -m unittest discover -s tests

`shellcheck` běží se `--severity=info`, ne se `--severity=style`: stylové nálezy jsou preference a brána, která padá na preferenci, se obchází. **Ze stejného důvodu má `ruff` jen `--select F,E9`** – nedefinovaná jména, nepoužité importy a syntaktické chyby, tedy vady, ne názory. Výchozí sada by tu hlásila pořadí importů a závorky navíc; `--isolated` navíc zajistí, že se nechytí cizí konfigurace odněkud z domovského adresáře. Python přibyl do repozitáře 6. 9. 2026 se skripty `/compose`. **Od 7. 9. 2026 lint kryje i `tests/`** – je to největší Python v repozitáři a nekontroloval ho nikdo, přestože je to zároveň jediná vrstva, která tu něco doopravdy vynucuje. Běh testů sám chytí syntaktickou chybu, ale ne nepoužitý import ani překlep ve jménu uvnitř větve, která se zrovna nevykonala.

`test` pokrývá dvě vrstvy:

- **`tests/test_skills.py` – meta-testy nad konfigurací.** Hlídají, že hlavičky skillů parsují a sedí s adresářem, že popis říká, kdy se skill použije, že režim popsaný v těle je i v `argument-hint`, že odkazy na soubory vedou někam **a že odkaz na sekci míří na skutečný nadpis** – včetně vnitroskillových odkazů na vlastní fáze **i kroky**, které tvar s cestou nemají, a rozbité tedy jinou branou neprojdou; hlídají se i písmenné podkroky a **celé výčty čísel** za jedním „krok“, protože dávka náhrad při přečíslování přepsala jen první z nich –, že se skilly odkazují na kroky životního cyklu a ne na jejich vnitřky, že kroky životního cyklu mají sekci *Co skill nedělá*, že README zná každý skill a nezná žádný zmizelý, a že šablona sekce *Autocommit v projektech* v `/autocommit` sedí se zněním v `CLAUDE.md`. Kroky životního cyklu se čtou z `RULES.md`, ne z konstanty v testu, a kontrakt příkazů se parsuje týmž výrazem jako `green-line.sh`. Od zavedení normy `skills/SKILLS.md` hlídají navíc **soulad skillů s ní** – povinné sekce **a jejich vzájemné pořadí** včetně toho, kde smí stát `Časté chyby` – u lineárního skillu před závěrem, u skillu s přílohovými sekcemi naposled –, odkaz na `skills/PREFLIGHT.md`, koncové věty, mez délky, zákaz odkazu dovnitř fáze jiného skillu a limit 1024 znaků na `description`. Vynucuje se to **ráčnou**: množina skillů mimo normu se musí *rovnat* seznamu `MIGRACE`, takže opravený skill, který se ze seznamu nevyškrtne, shodí testy stejně jako regrese – jinak by výjimka tiše přežila dokončenou migraci a přestala cokoliv měřit. Zvlášť stojí testy **nosných částí**: že `/review` má fázi ověřování nálezů, že `/cleanup` má fázi dohledávající zamluvená témata, že zadání agentů mají pole `severity` a `basis`, že datovaný záznam jmenuje `date +%F` a že `.claude/run/` je v `.gitignore` – běhový stav skillů se mění po každém tahu a nesmí skončit v gitu. Od zavedení normy *README skillu* k tomu přibyla **vrstva vizitek**: že každý skill má vlastní `README.md`, že v něm jsou povinné sekce, že se instalace píše jako pokyn pro Clauda s odkazem do repozitáře, že skill ze životního cyklu nese rámeček s celým cyklem i hromadnou instalaci a skill mimo něj naopak ne, že **každý režim z `argument-hint` je v README pojmenovaný** – včetně výchozího, který jinak nejde napsat explicitně –, že se README vejde do meze délky a že na tu vizitku odkazuje kořenové README. Je to tvar toho, co nese funkci, ne jen tvar hlavičky. Zvlášť stojí i **skripty ve skillech** (`skills/*/scripts/`): přeloží se a neodvozují cíl z vlastního umístění – to druhé je vada, kterou lint nevidí a která by se projevila až zápisem vedle skillu místo do archivu. **Nad tím vším stojí mutační testy**: poškodí vzorový skill a ověří, že kontrola nález opravdu nahlásí – kontrola, která nic nechytá, projde jinak stejně tiše jako ta funkční.
- **`tests/test_green_line.py` – regresní testy zelené linky.** Osmnáct scénářů nad dočasným repozitářem s přesměrovaným `HOME`: souhlas a jeho platnost pro celý repozitář včetně worktree i přes symlink v cestě, rozdíl mezi `exit 1` a `exit 2`, druhý pokus po zablokování, shoda otisku, chybějící nástroj, díra v kontraktu, pomlčka, vypnutá brána, otisk nad neverzovaným adresářem i nad rozpracovaným souborem, `## Příkazy` v bloku kódu, kontrakt v `.claude/`, klíč `cwd` včetně cesty mimo projekt, zámek proti souběhu, `--revoke` s tečkou i lomítkem. Je to jediné místo konfigurace, které něco doopravdy vynucuje, takže jeho tichá regrese je nejdražší, jaká tu může nastat. Používají jen stdlib – brána, která si žádá instalaci balíčku, se v cizím prostředí neprojeví jako nález, ale jako rozbitý nástroj, a ten se obchází.

`typecheck` tu **dlouho stála pomlčka** s odůvodněním, že repozitář je konfigurace, ne program. To přestalo platit ve chvíli, kdy k `/invoicing` přibyl `calendar.swift` – od té chvíle tu ležel program, který nečetla žádná brána, a překlep v něm by se poznal až uprostřed ostré fakturace. Dnes proto `typecheck` pouští `swiftc -typecheck` nad všemi swiftovými skripty ve skillech (na Python ve `skills/*/scripts/` je test v `tests/`, ne tahle brána); běží kolem dvou vteřin a nic neinstaluje, protože Swift je na macOS součástí vývojářských nástrojů.

**Kdyby Swift z repozitáře jednou zmizel, vrať pomlčku**, ne prázdný řádek: chybějící klíč hook po každém tahu hlásí jako nezkontrolovaný krok, a to je trvalý šum místo informace.

## Automatické akce

### Autocommit

Autocommit je zapnutý.
