# Konfigurace Claude Code

Moje osobní konfigurace Claude Code – pravidla, skilly, hooky a status line, sdílená pro inspiraci.

- **Slug:** `claude`
- **Repozitář:** https://github.com/jantichy/claude

## Výjimky z obecných pravidel

- **Blok metadat je tady, ne v kořenovém `CLAUDE.md`**, jak jinak velí `~/.claude/STRUCTURE.md`. Kořenový soubor je uživatelský a rozbaluje se do každé session v každém projektu – metadata tohohle repozitáře tam nepatří, mátla by v cizím projektu.
- **`/attack` ani `/release` se tu nikdy nepouštějí.** Repozitář je konfigurace, ne aplikace – není co spustit ani kam nasadit. Životní cyklus tady končí `/cleanupem`. Zapsáno schválně, ne odvozeno (`~/.claude/RULES.md`, *Zapiš i to, co vědomě nemáš*).
- **Tenhle repozitář má `todo.md`, `backlog.md`, `done.md` i `decisions.md` v `~/Dev/context/`**, ne u sebe. Platí to pro každý skill, který do nich zapisuje a zároveň se tu pouští – `/review`, `/oponent`, `/consistency`, `/cleanup`, `/implement` a `/skill`. (`/attack` a `/release` se tu nepouštějí vůbec, viz výš.) **U `/skill` to platí bezvýhradně**, protože jako jediný nikde jinde běžet nemůže – spravuje skilly, a ty jsou jen tady. A **neptej se na to pokaždé znovu**:

  | Co | Kam | Jak |
  |---|---|---|
  | odložený nález, zaparkovaný bod | `~/Dev/context/todo.md` | do sekce podle domény, které se týká |
  | nezávazný nápad, o kterém se nerozhodlo | `~/Dev/context/backlog.md` | tamtéž podle domény; hranici proti todo drží `~/.claude/STRUCTURE.md`, *`backlog.md`* |
  | rozhodnutí, zamítnutá varianta, vědomá mezera | `~/Dev/context/decisions.md` | tamtéž podle domény; týká-li se rozhodnutí **jednoho skillu**, patří rovnou do jeho `SKILL.md` k místu, kde platí – tam ho příště najde ten, kdo ho potřebuje |
  | záznam dokončeného průchodu (`## Průchody životním cyklem`) | `~/Dev/context/done.md` | u `/review` jen když má smysl ho pak číst – jeho čtenářem je `/release`, a ten se tu nepouští. **U `/oponent` vždy:** jeho čtenářem je příští `/oponent`, který podle svého SKILL.md bez seznamu hledisek neví, s čím se má srovnávat |

  Je to jediné místo, kde struktura tohohle repozitáře sahá ven; důvod je, že konfigurační vrstva je téma, které ta znalostní báze už drží. **Pozor: platí to jen pro tenhle repozitář** – proto to stojí tady v projektovém souboru, a ne v kořenovém `CLAUDE.md`, který se rozbaluje do každé session v každém projektu.
- **`docs/` neexistuje.** Repozitář není vyvíjený projekt, ale konfigurace; `todo.md`, `backlog.md`, `done.md`, `decisions.md` ani `rules.md` nemá a nezakládají se.

## Instrukce pro tenhle repozitář

Projektové instrukce pro práci **v tomhle repozitáři**. Načítají se jen tady, na rozdíl od `~/.claude/CLAUDE.md`, který je uživatelský a jde do každé session v každém projektu.

@~/.claude/skills/SKILLS.md

- **Norma výš platí pro každou cestu ke změně skillu:** ruční úpravu, `/skill` i cizí nástroj typu `skill-creator` nebo `superpowers:writing-skills`. Ty mají vlastní představu o tvaru a prosadí ji, když jim nic neřekneš; tenhle řádek je to, co jim ji přebíjí (`~/.claude/RULES.md`, *Přednost pravidel*). Postup zakládání, revize a rušení drží `/skill`, ne norma.
- **Každý skill má dvě README.** Vlastní `skills/<jméno>/README.md` psané pro člověka zvenčí, na které se posílá odkaz, a k tomu jeden odstavec v kořenovém `README.md`, jehož nadpis na ně odkazuje. Tvar obojího drží `skills/SKILLS.md`, *README skillu*, a vynucují ho testy. Když skill přidáš nebo zásadně změníš jeho chování, aktualizuj obojí rovnou jako součást té změny – nečekej na vyžádání.

## Kontrakt příkazů

Kontrakt příkazů (`~/Dev/context/coding/quality.md`). Průběžná kontrola ho tady najde v `.claude/CLAUDE.md` a příkazy spouští v kořeni repozitáře.

- typecheck: swiftc -typecheck skills/*/*.swift
- lint: shellcheck -x --severity=info ./*.sh skills/*/*.sh && ruff check --isolated --select F,E9,C901 --config 'lint.mccabe.max-complexity = 10' skills/*/*.py skills/*/scripts/*.py tests/*.py
- test: python3 -m unittest discover -s tests

`shellcheck` běží se `--severity=info`, ne se `--severity=style`: stylové nálezy jsou preference a kontrola, která padá na preferenci, se obchází. **Ze stejného důvodu má `ruff` jen `--select F,E9,C901`** – nedefinovaná jména, nepoužité importy, syntaktické chyby a cyklomatická složitost, tedy vady a jeden měřitelný práh, ne názory. `C901` je tu od 8. 9. 2026 s prahem 10 podle `~/Dev/context/coding/quality.md`; do té doby se neměřila vůbec a pět funkcí ho překračovalo (nejvíc `progress.py` s 19). Práh se **nesnižuje kvůli tomu, že překáží** – to smí jen člověk a se zápisem do rozhodnutí. Výchozí sada by tu hlásila pořadí importů a závorky navíc; `--isolated` navíc zajistí, že se nechytí cizí konfigurace odněkud z domovského adresáře. Python přibyl do repozitáře 6. 9. 2026 se skripty `/compose`. **Od 7. 9. 2026 lint kryje i `tests/`** – je to největší Python v repozitáři a nekontroloval ho nikdo, přestože je to zároveň jediná vrstva, která tu něco doopravdy vynucuje. Běh testů sám chytí syntaktickou chybu, ale ne nepoužitý import ani překlep ve jménu uvnitř větve, která se zrovna nevykonala.

`test` pokrývá dvě vrstvy:

- **`tests/test_skills.py` – meta-testy nad konfigurací.** Hlídají **hlavičku a odkazy**: že hlavička parsuje a sedí s adresářem, že `description` říká, kdy se skill použije, a vejde se do 1024 znaků, že režim popsaný v těle je i v `argument-hint`, že odkazy na soubory vedou někam a odkaz na sekci míří na skutečný nadpis – včetně vnitroskillových odkazů na vlastní fáze i kroky, písmenných podkroků a celých výčtů čísel –, a že se skilly odkazují na kroky životního cyklu, ne na jejich vnitřky. Hlídají **soulad s normou** `skills/SKILLS.md`: povinné sekce a jejich pořadí včetně toho, kde smí stát `Časté chyby`, odkaz na `skills/PREFLIGHT.md`, závěrečný verdikt, mez délky a zákaz odkazu dovnitř fáze jiného skillu; vynucuje se to tím, že **seznam `MIGRACE` musí přesně sedět se skutečností**, takže opravený a nevyškrtnutý skill shodí testy stejně jako regrese. Hlídají **nosné části** – že `/review` má fázi ověřování nálezů, `/cleanup` fázi na nevypořádaná témata, že zadání agentů nesou `severity` a `basis`, že datovaný záznam jmenuje `date +%F`, že žádný skill neopisuje pořadí kroků cyklu šipkami místo odkazu do `RULES.md` a že `.claude/run/` je v `.gitignore`. Hlídají **šablony výstupu**: že každý blok kódu, jehož obsah jde do konverzace, nese pokyn vypsat ho jako Markdown – s jmenovitým seznamem bloků, které se místo toho zapisují do souboru, a ten **musí přesně sedět**. Hlídají **README skillů**: že každý skill má `README.md` s povinnými sekcemi ve správném pořadí, instalací psanou jako pokyn pro Clauda, rámečkem cyklu a hromadnou instalací u kroků cyklu (a bez nich mimo něj), pojmenovanými všemi režimy z `argument-hint` včetně výchozího, dodrženou mezí délky a relativními odkazy, které vedou na existující soubor; kořenové README zná každý skill a nezná žádný zmizelý. Hlídají **kanonický tvar autocommitu**: že projektový `CLAUDE.md` tohohle repozitáře nese přepínač pod `## Autocommit` i s importem pravidel ze skillu, že nestojí pod zastřešující sekcí a že se definice mechanizmu nevrátila do globálního `CLAUDE.md`. Hlídají **skripty ve skillech** (`skills/*/*.py` i `skills/*/scripts/*.py`) a nad tím vším stojí **mutační testy**, které poškodí vzor a ověří, že kontrola nález opravdu nahlásí. Kroky životního cyklu se čtou z `RULES.md`, povinné sekce README z normy a kontrakt příkazů se parsuje týmž výrazem jako `verify.sh` – žádný z těch seznamů nestojí v testu natvrdo.

  **Proč která kontrola existuje, drží docstring toho testu, ne tenhle výčet.** Odůvodnění opsané na dvě místa se rozejde a ta trvanlivější kopie bývá ta horší: jedna oprava změní chování skillu a druhé místo dál vysvětluje kontrolu selháním, které už nastat nemůže. Zdejší popis proto říká jen *co* se hlídá; *proč* si přečti u testu.
- **`tests/test_verify.py` – regresní testy průběžné kontroly.** Dvaadvacet scénářů nad dočasným repozitářem s přesměrovaným `HOME`: souhlas a jeho platnost pro celý repozitář včetně worktree i přes symlink v cestě, rozdíl mezi `exit 1` a `exit 2`, druhý pokus po zablokování, shoda otisku, chybějící nástroj, díra v kontraktu, pomlčka, vypnutá kontrola, otisk nad neverzovaným adresářem i nad rozpracovaným souborem, `## Kontrakt příkazů` v bloku kódu i v HTML komentáři, dvě sekce téhož jména, nedovřený plot, kontrakt v `.claude/`, klíč `cwd` včetně cesty mimo projekt, zámek proti souběhu, `--revoke` s tečkou i lomítkem. Je to jediné místo konfigurace, které něco doopravdy vynucuje, takže jeho tichá regrese je nejdražší, jaká tu může nastat. Používají jen stdlib – kontrola, která si žádá instalaci balíčku, se v cizím prostředí neprojeví jako nález, ale jako rozbitý nástroj, a ten se obchází.

`typecheck` tu **dlouho stála pomlčka** s odůvodněním, že repozitář je konfigurace, ne program. To přestalo platit ve chvíli, kdy k `/invoicing` přibyl `calendar.swift` – od té chvíle tu ležel program, který nečetla žádná kontrola, a překlep v něm by se poznal až uprostřed ostré fakturace. Dnes proto `typecheck` pouští `swiftc -typecheck` nad všemi swiftovými skripty ve skillech (na Python ve `skills/` je test v `tests/`, ne tahle kontrola); běží kolem dvou vteřin a nic neinstaluje, protože Swift je na macOS součástí vývojářských nástrojů.

**Kdyby Swift z repozitáře jednou zmizel, vrať pomlčku**, ne prázdný řádek: chybějící klíč hook po každé odpovědi hlásí jako nezkontrolovaný krok, a to je trvalý šum místo informace.

## Review

Nálezy vyhodnocené jako „neopravovat“. Při dalším běhu se neuvádějí, dokud se
nezmění kód, kterého se týkají.

- **2026-09-08** · `eccc756` · *Plugin gitkraken-hooks vidí provoz session a smí rozhodovat o oprávněních* (zdroj: review, podklad: OWASP – integrita a data v pohybu): Vědomě nainstalovaný nástroj od známého dodavatele, ne podvržený kód. Egress mimo stroj se **neprokázal**: běžící hook procesy nemají podle `lsof` jediný TCP socket, broadcast míří na lokálně registrovaného agenta (`gk agents register --address http://127.0.0.1:1234`) a v logu je 104× „no decision“, protože žádný registrovaný není. Zbývá tedy „lokální proces téhož uživatele vidí obsah session“, což je popis toho, co plugin dělá, ne vada konfigurace. Zůstává vědomě přijaté riziko: binárka má `AUTO_UPDATE=true`, takže se ta důvěra obnovuje s každou verzí bez revize, a `PermissionRequest` hook by povolení udělit uměl, kdyby agent registrovaný byl. Zruší se vypnutím pluginu v `settings.json`.
  - Lokace: settings.json (`enabledPlugins`), plugins/marketplaces/gitkraken/plugins/gitkraken-hooks/hooks/hooks.json

## Autocommit

Autocommit je zapnutý.

@~/.claude/skills/autocommit/autocommit.md
