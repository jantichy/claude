# Konfigurace Claude Code

Moje osobní konfigurace Claude Code – pravidla, skilly, hooky a status line, sdílená pro inspiraci.

- **Slug:** `claude`
- **Repozitář:** https://github.com/jantichy/claude

## Výjimky z obecných pravidel

- **Blok metadat je tady, ne v kořenovém `CLAUDE.md`**, jak jinak velí `~/Dev/context/structure/structure.md`. Kořenový soubor je uživatelský a rozbaluje se do každé session v každém projektu – metadata tohohle repozitáře tam nepatří, mátla by v cizím projektu.
- **`/attack` ani `/release` se tu nikdy nepouštějí.** Repozitář je konfigurace, ne aplikace – není co spustit ani kam nasadit. Osa práce tady končí `/cleanupem`. Zapsáno schválně, ne odvozeno (`~/.claude/RULES.md`, *Zapiš i to, co vědomě nemáš*).
- **Tenhle repozitář má `todo.md`, `done.md` i `decisions.md` v `~/Dev/context/`**, ne u sebe. Platí to pro každý skill, který do nich zapisuje a zároveň se tu pouští – `/review`, `/oponent`, `/consistency`, `/cleanup`. (`/attack` a `/release` se tu nepouštějí vůbec, viz výš.) –, a **neptej se na to pokaždé znovu**:

  | Co | Kam | Jak |
  |---|---|---|
  | odložený nález, zaparkovaný bod | `~/Dev/context/todo.md` | do sekce podle domény, které se týká |
  | rozhodnutí, zamítnutá varianta, vědomá mezera | `~/Dev/context/decisions.md` | tamtéž podle domény; týká-li se rozhodnutí **jednoho skillu**, patří rovnou do jeho `SKILL.md` k místu, kde platí – tam ho příště najde ten, kdo ho potřebuje |
  | záznam dokončeného průchodu (`## Průchody osou`) | `~/Dev/context/done.md` | u `/review` jen když má smysl ho pak číst – jeho čtenářem je `/release`, a ten se tu nepouští. **U `/oponent` vždy:** jeho čtenářem je příští `/oponent`, který podle svého SKILL.md bez seznamu úhlů neví, s čím se má srovnávat |

  Je to jediné místo, kde struktura tohohle repozitáře sahá ven; důvod je, že konfigurační vrstva je téma, které ta znalostní báze už drží. **Pozor: platí to jen pro tenhle repozitář** – proto to stojí tady v projektovém souboru, a ne v kořenovém `CLAUDE.md`, který se rozbaluje do každé session v každém projektu.
- **`docs/` neexistuje.** Repozitář není vyvíjený projekt, ale konfigurace; `todo.md`, `done.md`, `decisions.md` ani `rules.md` nemá a nezakládají se.

## Instrukce pro tenhle repozitář

Projektové instrukce pro práci **v tomhle repozitáři**. Načítají se jen tady, na rozdíl od `~/.claude/CLAUDE.md`, který je uživatelský a jde do každé session v každém projektu.

- Každý skill má v `README.md` svou sekci. Když nějaký přidáš nebo zásadně změníš jeho chování, aktualizuj ji rovnou jako součást té změny – stejný styl a tón jako ostatní sekce (osobní, věcné, s konkrétním přínosem). Nečekej na vyžádání.

## Příkazy

Kontrakt příkazů (`~/Dev/context/coding/coding.md`, *Ověřování a brány kvality*). Zelená linka ho tady najde v `.claude/CLAUDE.md` a příkazy spouští v kořeni repozitáře.

- typecheck: -
- lint: shellcheck --severity=info ./*.sh skills/*/*.sh
- test: python3 -m unittest discover -s tests

`shellcheck` běží se `--severity=info`, ne se `--severity=style`: stylové nálezy jsou preference a brána, která padá na preferenci, se obchází.

`test` pokrývá dvě vrstvy:

- **`tests/test_skills.py` – meta-testy nad konfigurací.** Hlídají, že hlavičky skillů parsují a sedí s adresářem, že popis říká, kdy se skill použije, že režim popsaný v těle je i v `argument-hint`, že odkazy na soubory vedou někam **a že odkaz na sekci míří na skutečný nadpis**, že se skilly odkazují na kroky osy a ne na jejich vnitřky, že kroky osy mají sekci *Co skill nedělá*, že README zná každý skill a nezná žádný zmizelý, a že šablona sekce *Autocommit v projektech* v `/autocommit` sedí se zněním v `CLAUDE.md`. Kroky osy se čtou z `RULES.md`, ne z konstanty v testu, a kontrakt příkazů se parsuje týmž výrazem jako `green-line.sh`. Zvlášť stojí testy **nosných částí**: že `/review` má fázi ověřování nálezů, že zadání agentů mají pole `severity` a `basis` a že datovaný záznam jmenuje `date +%F` – tedy tvar toho, co nese funkci, ne jen tvar hlavičky.
- **`tests/test_green_line.py` – regresní testy zelené linky.** Osmnáct scénářů nad dočasným repozitářem s přesměrovaným `HOME`: souhlas a jeho platnost pro celý repozitář včetně worktree i přes symlink v cestě, rozdíl mezi `exit 1` a `exit 2`, druhý pokus po zablokování, shoda otisku, chybějící nástroj, díra v kontraktu, pomlčka, vypnutá brána, otisk nad neverzovaným adresářem i nad rozpracovaným souborem, `## Příkazy` v bloku kódu, kontrakt v `.claude/`, klíč `cwd` včetně cesty mimo projekt, zámek proti souběhu, `--revoke` s tečkou i lomítkem. Je to jediné místo konfigurace, které něco doopravdy vynucuje, takže jeho tichá regrese je nejdražší, jaká tu může nastat. Používají jen stdlib – brána, která si žádá instalaci balíčku, se v cizím prostředí neprojeví jako nález, ale jako rozbitý nástroj, a ten se obchází.

Pomlčka u `typecheck` znamená **vědomě se neaplikuje**: repozitář je konfigurace, ne program, a nemá co typovat. Kdyby ten řádek chyběl úplně, hook by po každém tahu hlásil, že se něco nezkontrolovalo, a to by byl trvalý šum místo informace.

## Automatické akce

### Autocommit

Autocommit je zapnutý.
