# Migrace podprojektů pod klientskou složku

**Dočasný soubor.** Slouží jen jednorázové migraci struktury disku – přesunu existujících projektů z `~/Dev` pod klientské složky v `~/Projekty`. Až bude krok 3 té migrace hotový u všech klientů (`~/.claude/docs/todo.md`, *Migrace na novou strukturu disku*), soubor se smaže celý i s odkazem z [`client.md`](client.md), *Převod*. Do skillu se neslučuje: postup, který se po migraci už nikdy nepoužije, by ho jen nafukoval.

Ověřený je na FAVI (11. 10. 2026): tři repozitáře, 247 commitů, sloučené do `~/Projekty/Favi`.

## Kdy

Klientská složka už existuje, je to git repozitář a `/project` v ní proběhl. Podprojekt **nesplňuje** kritérium vlastního repozitáře z `client.md`, *Podprojekt* – nemá vlastní nasazení, CI, cizí remote ani se nepředává samostatně –, takže patří do repozitáře klienta. Splňuje-li ho, přesouvá se celý i s `.git` a jde do `.gitignore` klientské složky; tenhle postup se na něj nepoužije.

## Předpoklady – ověř u každého zdrojového repozitáře

- **pracovní strom je čistý** (`git status --short`), stash prázdný,
- **jediná větev a žádné worktree** (`git branch -a`, `git worktree list`). Má-li víc větví nebo worktree layout, **zastav se a rozhodni s uživatelem** – postup níž převádí jen `main`,
- **neběží v něm session** – nejnovější `*.jsonl` v jeho složce v `~/.claude/projects/` není z posledních minut,
- jméno podsložky v klientské složce potvrdil uživatel (FAVI: `~/Dev/favi` → `reporting/`).

## Postup

1. **Nástroj:** `brew install git-filter-repo`, není-li.
2. **Přepis historie do podsložky** – na klonu ve scratchpadu, originál se nedotkne:

   ```bash
   git clone -q --no-local ~/Dev/<project> <scratch>/<sub>
   git -C <scratch>/<sub> filter-repo --quiet --force --to-subdirectory-filter <sub>
   ```

   Ověř, že počet commitů sedí s originálem a mimo `<sub>/` nezůstal žádný soubor (`git ls-files | grep -vc "^<sub>/"`).
3. **Sloučení do klientského repozitáře:**

   ```bash
   git fetch -q <scratch>/<sub> main:import/<sub>
   git merge -q --allow-unrelated-histories -m "Projekt <sub> přesunutý pod klientskou složku i s historií" import/<sub>
   git branch -q -D import/<sub>
   ```

   Data commitů zůstanou původní – `/invoicing` je dál najde (`activity.py` čte `git log --all` z klientské složky).
4. **Porovnání s originálem:** `diff -rq -x .git -x .DS_Store -x __pycache__ ~/Dev/<project> <Client>/<sub>`. Dva známé rozdíly nejsou ztráta:
   - **prázdný adresář** git nenese – v novém chybí,
   - **konce řádků** u souborů s CRLF, je-li `core.autocrlf=input`. Ověř, že se liší jen `\r` (`cmp <(tr -d '\r' < a) <(tr -d '\r' < b)`), a zdrojová data zkopíruj s původními bajty (`cp -p`) – podklady v `research/` se nemění. Git je pak vidí jako změněné jen podle stat, věcný diff je prázdný.

   Cokoliv jiného je chyba – zastav se.
5. **Složky session logů** přejmenuj s adresářem, jinak projekt přijde o historii a `/invoicing` o stopy práce: `mv -n ~/.claude/projects/<old> ~/.claude/projects/<new>`, kde jméno je cesta s `/` nahrazeným `-` (`-Users-honza-Dev-favi` → `-Users-honza-Projekty-Favi-reporting`). Nové jméno nesmí existovat.
6. **Starý adresář do Koše**, ne `rm`: `mv -n ~/Dev/<project> ~/.Trash/dev-<project>-<date>` (`date +%F`). Vysype ho uživatel.
7. **Podprojektový `CLAUDE.md` zeštíhli** o to, co dědí z kořene klientské složky – profil, autocommit a paměťovou politiku přebít nejde (`client.md`, *Podprojekt*):
   - pryč: `## Autocommit`, `## Paměť`, import profilu, doménové importy shodné s kořenem (odlišné zůstanou), úvodní kontext, který opakuje profil;
   - pryč: **`## Kontrakt příkazů`** – průběžná kontrola čte kontrakt jen z kořene repozitáře a session spuštěná v podsložce by na něm spadla. Kontrolu podprojektu buď přenes do kořenového kontraktu (cesty s `<sub>/`), nebo ji nech spouštět ručně – **zeptej se**, a rozhodnutí i se zavrženou variantou zapiš do `decisions.md` podprojektu;
   - pryč: verzovaný `.claude/settings.local.json` – v podsložce se nenačte;
   - zůstává: popis, zadání, typ projektu, struktura a vlastní standardní soubory podprojektu. Chybí-li blok metadat, doplň aspoň nadpis, popisek a slug.

   Ověř diffem, že zmizelo jen zamýšlené.
8. **Kořenový `CLAUDE.md`:** sekce `## Podprojekty` s jedním řádkem na podsložku a větou, že nový podprojekt je podsložka, ne nový repozitář.
9. **`invoicing.md`, pole *Projekty*:** jediná cesta klientské složky; dřívější cesty jen jako „dřív `~/Dev/…`“ u popisu podsložky. Ověř spuštěním `activity.py <od> <do> ~/Projekty/<Client>`, že vrací bloky ze všech podsložek.
10. **Profil:** sekce *Projekty* odpadá, jakmile v ní nic mimo složku nezbude.
11. **Odkazy na starou cestu:** smyčka z `client.md`, *Převod*, bod 4, se vzory `-F -e 'Dev/<project>'`. **Ne `-E` s `\b`** – `git grep` ho nepodporuje a vrátí prázdno, které vypadá jako čistý výsledek. Živé odkazy přepiš, historické záznamy (`done.md`, `decisions.md`, protokoly dřívějších běhů) nech.
12. **Commit jmenovanými cestami** v klientské složce i v každém dalším dotčeném repozitáři (`client.md`, *Zápis mimo projekt*).
