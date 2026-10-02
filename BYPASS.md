# Čím se dají obejít zdejší kontroly

Mapa známého povrchu, ne seznam vyřešených problémů. U každé vynucovací vrstvy stojí, **čím se dá obejít**, **co to chytí** a **co je vědomě přijaté riziko**.

**Proč katalog, a ne zákaz.** Zákaz („testy jsou během implementace read-only“) se dá dodržet i obejít a nikde po tom nezůstane stopa. Katalog je auditovatelný: dá se přečíst, rozporovat a doplnit, a hlavně je z něj vidět, co se **vědomě** nehlídá. Vrstva, u které nikdo neví, kudy se obchází, není bezpečná – jen neprozkoumaná.

**Jak se to čte.** `accepted` neznamená „nevadí“, ale „víme o tom a rozhodli jsme se to nehlídat“. U každého takového řádku je důvod. Objeví-li se cesta, která tu není, patří sem **dřív**, než se zavře – jinak katalog zestárne tím nejhorším způsobem: bude vypadat úplně.

**Kdo ho udržuje.** Nepatří žádnému skillu a nikdo si ho nenačítá při běhu – je to referenční soupis k nahlédnutí ve chvíli, kdy se o nějaké kontrole rozhoduje. **Zapisuje do něj ten, kdo vrstvu zakládá nebo mění**, ve stejném commitu; objeví-li se nová cesta, jak něco obejít, patří sem dřív, než se zavře. Že tu každá vrstva má řádek, hlídá test v `tests/test_hooks.py`, a ten čte seznam vrstev z disku – **pravdivost řádku ale změřit neumí**, ta drží na tom, kdo ho psal.

**Rozsah je tenhle repozitář.** Obecné pravidlo, že takový registr má vzniknout, drží `~/Dev/context/coding/quality.md`.

## Průběžná kontrola (`verify.sh` jako `Stop` hook)

| Čím se obejde | Co to chytí | Stav |
|---|---|---|
| Kontrakt v `CLAUDE.md` je kód z repozitáře – dá se do něj dopsat cokoliv | Souhlas se vydává **na konkrétní znění kontraktu**; změna ho zneplatní a hook se zastaví | hlídáno, `tests/test_verify.py` |
| Souhlas si vydá proces sám | Vydání čte `/dev/tty`, kterou proces bez řídicího terminálu nemá – neprojde ani `!` prefix v Claude Code | hlídáno |
| Přesměrovat stav běhu a podstrčit „tenhle strom už prošel“ | `RUN_DIR` je natvrdo pod `$HOME`, `XDG_STATE_HOME` se ignoruje | hlídáno, od 14. 9. 2026 |
| Podvrhnout sekci `## Kontrakt příkazů` v komentáři nebo v bloku kódu nad tou pravou | Tělo se čte parserem podle CommonMarku; dvě sekce téhož jména běh zastaví | hlídáno |
| `CLAUDE_NO_VERIFY=1` | Nic – proměnná kontrolu vypne | **accepted**: je to únikový východ pro případ, kdy je kontrola sama rozbitá. Kdo ho použije, ví to; v logu session je to vidět. |
| Vypínač commitnutý do repozitáře | Vypínač leží od 20. 9. 2026 **mimo repozitář** (`~/.local/state/claude-verify/disabled/<klíč>`, přepínač `--disable`), takže ho tam nejde zanést; hlídá to `tests/test_verify.py` oběma směry | hlídáno, od 20. 9. 2026 |
| Commit z jiného stroje, z GUI nebo s `--no-verify` | Nic lokálně | **accepted**: přesně proto existuje CI – ta běží bez ohledu na to, kdo a odkud commituje, a je to jediná vrstva, kterou lokální obejití nezasáhne. |
| Splnit krok `test` triviálním testem | Nic automaticky | **accepted**: měří to jen mutační testy, a ty tu běží nad vzory kontrol, ne nad celou sadou. Proti tomu stojí zákaz editace testů během implementace a to, že diff testů čte `/review`. |

## Git hook na zprávu merge commitu

| Čím se obejde | Co to chytí | Stav |
|---|---|---|
| `git commit --no-verify` | Nic | **accepted**: hook brání nečitelné historii, ne útoku. Kdo ho vypne, přepisuje si vlastní historii. |
| Vlastní `core.hooksPath` v projektu | Nic – projektové nastavení přebije globální | **accepted**, je to zamýšlené: projekt smí mít vlastní hooky. Lokální `commit-msg` naopak zdejší hook volá, aby se nevypnul omylem. |
| Zpráva, která pravidlo splní formálně („Merge hotové práce“) | Nic | **accepted**: smysl je donutit napsat větu, ne posoudit její kvalitu. |

## Převzetí lokálního stavu do worktree (`githooks/post-checkout`)

Tahle vrstva nic nehlídá, ale **sama je výjimkou z kontroly**: deny `Edit(//**/.env)` a `Edit(//**/.env.*)` v `settings.json` brání modelu založit v nové větvi odkaz na `.env`, a hook, který spouští git, ne model, to udělá za něj. Rozhodnuto vědomě a uživatelem – hook zapsal on, ne model.

| Čím se obejde | Co to chytí | Stav |
|---|---|---|
| Model nechá založit symlink na `.env` gitem, přestože jemu samotnému to deny zakazuje | Nic – hook deny pravidla nevidí | **accepted**: hook jen zakládá odkaz do `main/`, respektive kopíruje `.env.local`, obsah nečte ani neposílá dál. Čtení obsahu ve větvi hlídá totéž, co v `main/` – nástroj Read deny `Read(//**/.env)`, shell `secret-guard.py` –, takže se riziko proti `main/` nemění. |
| Hook běží nad každým repozitářem na stroji a mohl by zasáhnout mimo layout | Spustí se jen při nulovém předchozím HEAD (založení worktree) a jen tehdy, když je společný git adresář `<kontejner>/.bare` a vedle leží `main/`; existující soubor ve větvi nepřepíše | hlídáno, `tests/test_hooks.py` |
| Vlastní `core.hooksPath` v projektu | Nic – hook se nespustí a větev vznikne bez `.env` | **accepted**: projekt s vlastními hooky si je volí sám; `WORKTREE.md` říká, že chybějící převzetí se ohlásí, ne obchází ručně. |

## CI (`.github/workflows/contract.yml`, volaný z `verify.yml` a z projektů)

| Čím se obejde | Co to chytí | Stav |
|---|---|---|
| Přepsat workflow v témže PR | Nic | **accepted**: repozitář nemá secrets, `GITHUB_TOKEN` je read-only a runner je efemérní, takže cizí kód nemá co ukrást. Podrobně v `.claude/CLAUDE.md`, `## Review`. |
| PR z forku spustí kontrakt z cizí větve | `fork-pr-contributor-approval` je na `first_time_contributors` | **accepted** pro přispěvatele, který už jednou prošel |
| Doinstalované nástroje projektu nejsou připnuté (`brew`, `pip install ruff` ve `verify.yml`) | Nic – vstup `install` je volba volajícího | **accepted** pro tenhle repozitář: nemá secret, který by šlo ukrást, `GITHUB_TOKEN` je read-only a runner je efemérní; připnutý `ruff` by navíc znamenal zmrazený lint, protože nové verze hlásí nové nálezy. Nástroje sdíleného workflow samotného (gitleaks, semgrep) připnuté **jsou** a hlídá to `tests/test_ci.py`; akce jsou připnuté na SHA a hlídá je Dependabot (`.github/dependabot.yml`). |
| Projekt zavolá sdílený workflow přes pohyblivý ref (`@main`, značka) | Krok *Konfigurační vrstva…* takové volání odmítne – rozhoduje `job.workflow_ref` | hlídáno, `tests/test_ci.py` (spuštěním té podmínky) |
| Projekt zůstane připnutý na starém commitu a opravy CI ho minou | Varování v běhu, když od připnutého commitu přibyla změna ve workflow, runneru, `verify.sh`, `links.py` nebo `order.py` | **accepted**: varování, ne pád – starší verze není chyba projektu a pád by shazoval CI bez jediné změny v něm. Dependabot to nevyřeší, protože tenhle repozitář nemá vydání ani značky, podle kterých by SHA posouval. |
| Projekt si sdílený workflow nevolá, nebo ho volá s osekanými spouštěči či bez `permissions` | Nic odsud – sdílený workflow, který neběží, nemá co hlídat | hlídá krátký test volajícího v každém projektu (`tests/test_ci.py` tam) |

## Zastavení destruktivního git příkazu (`git-guard.py` jako `PreToolUse` hook)

| Čím se obejde | Co to chytí | Stav |
|---|---|---|
| Přeházet argumenty (`git push origin main --force`) | Hook čte celý příkaz a posuzuje přepínač jako **celé slovo**, ne prefix – právě proto vznikl | hlídáno, `tests/test_hooks.py` |
| Slepit krátké přepínače (`git clean -fx`, `-xdf`, `-ffd`) | U `clean` rozhoduje **obsah** přepínače, ne jeho tvar – výčet slepenin je vždycky děravý a `-fx` jím prošel | hlídáno, doplněno 20. 9. 2026 |
| Vypnout `clean.requireForce` a mazat holým `git clean` | U `clean` se neptáme na `-f`, ale na to, jestli je běh suchý – projde jen `-n` a `--dry-run` | hlídáno, doplněno 20. 9. 2026 |
| Schovat příkaz do aliasu (`git pf`, `git test`) | Alias se rozbalí z konfigurace gitu a posoudí znovu, do tří úrovní zanoření | hlídáno |
| Shellový alias (`!sh -c '…'`) | Nerozebírá se, ale **zastaví se** – u shellu nejde poznat, co spustí | hlídáno |
| Schovat příkaz do skriptu, který se spustí (`./deploy.sh`) | Nic – hook vidí jen text příkazu | **accepted**: skript je kód a čte ho člověk při psaní i revizi; hook brání ukliknutí, ne útoku. |
| Napsat příkaz přes proměnnou (`F=--force; git push $F`) | Nic – expanzi dělá shell až po hooku | **accepted**: je to vědomé obcházení, ne omyl, a hook proti vlastnímu úmyslu nechrání. |
| `CLAUDE_NO_VERIFY` a spol. | Nic – hook na ně nesahá a běží vždy | – |
| Spustit to člověk z terminálu přes `!` | Nic | **accepted**, je to zamýšlená cesta: rozhodnutí přepsat historii patří člověku. |

**Nenahrazuje deny seznam, doplňuje ho.** Deny je levný a zastaví nejčastější tvar dřív, než se na cokoliv sáhne; hook dorovnává to, na co textový prefix nedosáhne. Zapsáno 20. 9. 2026 z nálezu `/review full`.

## Čtení tajemství přes shell (`secret-guard.py` jako `PreToolUse` hook)

Deny `Read(//**/…)` hlídá jen nástroj Read; Bash kolem něj procházel (`. ./.env`, `grep KEY .env`) a hodnota mohla skončit v transcriptu. Hook bere seznam tajemství z týchž deny pravidel a zastaví příkaz, jehož slovo odpovídá vzoru a odkazuje na existující soubor.

| Čím se obejde | Co to chytí | Stav |
|---|---|---|
| Kód interpretu (`python3 -c "open('.env')"`, heredoc do `python3 -`) | Kód interpretu se prohledává po kouscích cesty | hlídáno, `tests/test_hooks.py` |
| Relativní cesta po `cd` (`cd sub && cat ../.env`) | Cesta se zkouší vůči `cwd` i vůči každému adresáři, který příkaz jmenuje | hlídáno |
| Jméno v proměnné (`F=.env; cat $F`), glob (`cat .e*`), rekurze (`grep -r KEY .`) | Nic – hook vidí text příkazu, ne expanzi shellu | **accepted**: je to vědomé obcházení, ne omyl, stejně jako u `git-guard.py`. Rekurzivní `grep` nad projektem je běžný a jeho blokování by hook vyřadilo z provozu; `rg` navíc gitignorované soubory sám přeskakuje. |
| Program, který si tajemství načte sám (`npm run dev`, `docker compose` s `env_file`) | Nic | **accepted**, je to zamýšlené: aplikace tajemství potřebuje a hodnota do kontextu nejde, dokud ji program nevypíše. Explicitní `--env-file .env` naopak zastaví, protože jméno stojí v příkazu. |
| Spustit to člověk přes `!` | Nic | **accepted**, je to zamýšlená cesta: rozhodnutí použít tajemství patří člověku. Výstup takového příkazu ale do kontextu jde, takže ho má člověk psát tak, aby hodnotu nevypsal. |
| Soubor s tajemstvím mimo deny seznam (`config/database.yml`) | Nic | **accepted**: hook hlídá přesně deny seznam, nic navíc. Chybí-li v něm vzor, doplňuje se tam a hook ho převezme sám. |

## Permission systém (`settings.json`)

| Čím se obejde | Co to chytí | Stav |
|---|---|---|
| Zavolat zakázaný příkaz přes interpret (`python3 -c`, `osascript`) | Nic – deny porovnává text příkazu | **accepted**, je to vlastnost mechanismu. Proto se na deny nespoléhá tam, kde má držet skutečná hranice (souhlas průběžné kontroly čte `/dev/tty`). |
| Git alias z `~/.gitconfig` (`git cc` = `add -A` + `--amend` + `--force`) | Delší aliasy jsou v deny jmenovitě | **částečně**: jednopísmenné (`a`, `c`, `p`, `m`) pokrýt nejdou, vzor `git c:*` by zablokoval i `git commit`. Drží to pravidlo v `RULES.md`, *Commituj jmenované cesty, ne `-A`*. |
| Nový destruktivní příkaz, na který vzor nemyslel | Nic | **accepted**: seznam je výčet, ne princip. Roste, když se něco objeví. |
| Deny `Read(...)` na tajemství obejde čtení přes Bash (`. ./.env`, `grep`, `cat`) | `secret-guard.py`, viz sekce výš | hlídáno od 3. 10. 2026 |
| Deny na `.env` obejde git hook, který zakládá odkaz za model | Nic | **accepted**, je to zamýšlené – viz *Převzetí lokálního stavu do worktree* výš. Je to jediná vědomá cesta kolem deny na tajemství. |

## Status line (`statusline.sh`)

| Čím se obejde | Co to chytí | Stav |
|---|---|---|
| Cizí `.git/config` s `filter.*.clean` spustí program při čtení souborů | Konfigurace se před čtením prohledá a při nálezu se počet změn nevypíše | hlídáno, `tests/test_statusline.py` |
| Hodnota z JSONu vyhodnocená jako aritmetický výraz | Číselné vstupy projdou přes `num()` | hlídáno, od 14. 9. 2026 |
| Jiný git mechanismus spouštějící program, na který blacklist nemyslí | Nic | **accepted**: blacklist je výčet. Proti tomu stojí, že status line nespouští nic jiného než čtecí `git` příkazy. |

## Hlášení stavu do iTerm2 (`cc-status`)

Nainstalovala ji 2026-09-19 sama iTerm2 volbou *Install Claude Code Integration*: `cc-status` visí na deseti událostech hooků, takže běží nad **každým** repozitářem, kde běží Claude Code. Nic nevynucuje – hlásí jen, jestli Claude pracuje, čeká, nebo skončil. V registru je proto, že běží automaticky a dostává obsah hooku.

| Čím se obejde | Co to chytí | Stav |
|---|---|---|
| Je to kompilovaná binárka uvnitř `iTerm.app`, takže se nedá přečíst, co dělá | Nic | **accepted**: je to cizí kód dodávaný s aplikací, ve které ta session stejně běží. Zvenčí je zjistitelné jen tolik, že čte JSON ze stdin a volá `it2 --status`. |
| Payload hooku, který dostane na stdin, nese cestu k projektu i text promptu (`UserPromptSubmit`) | Nic | **accepted**: příjemcem je lokální terminál, ve kterém se ten prompt právě napsal. Ven z počítače nejde nic. |
| Odinstalace z menu iTerm2 vyndá hooky, ale symlink `~/.config/iterm2/cc-status` a zapnuté Python API nechá | Nic | **accepted**: symlink sám nespouští nic, spouštěčem jsou hooky. |

## Hooky z pluginů (`enabledPlugins` v `settings.json`)

Plugin smí přinést vlastní `hooks/hooks.json` a zapíná se **jedním řádkem** v `enabledPlugins`. Do 27. 9. 2026 o téhle vrstvě registr nevěděl vůbec: test čte hooky ze `settings.json`, `githooks/` a `.github/`, tedy z míst, kde pluginové hooky nestojí. Dnes to hlídá `PluginHooks` v `tests/test_hooks.py` – **mlčí ale, když plugin na disku není**, protože `plugins/` je v `.gitignore` a v CI se nemá co měřit.

**`superpowers@claude-plugins-official`** – `SessionStart` (i po `/clear` a `/compact`) vloží do kontextu obsah svého skillu `using-superpowers` obaleného do `<EXTREMELY_IMPORTANT>`.

| Čím se obejde | Co to chytí | Stav |
|---|---|---|
| Vkládá si do každé session instrukce, které se tvářejí jako nadřazené („you do not have a choice“) | Nic – je to text v kontextu, ne mechanismus | **accepted**: podle `~/.claude/RULES.md`, *Přednost pravidel*, je pobídka harnessu **poslední** v pořadí, tedy pod tímhle repozitářem i pod pokynem uživatele. Co ta vsuvka žádá, se posuzuje, nevykonává. |
| Čte soubor z adresáře pluginu, který se samoaktualizuje | Nic – obsah se může změnit bez schválení | **accepted**: je to `cat` skillu z oficiálního marketplace a výstup jde jen do kontextu téhle session, ne ven ze stroje. Kdyby se plugin začal chovat jinak, projeví se to vsuvkou, která je v každé session vidět. |

**Zrušený plugin sem nepatří, ale jeho odstranění má stopu.** `gitkraken-hooks` byl 27. 9. 2026 odstraněný úplně – ze `settings.json`, z marketplace i z cache –, protože se vrátil zapnutý potřetí (8. 9. vypršelo umlčení nálezu, 18. 9. vypnut po měření, 27. 9. zpátky). Proti čtvrtému kolu drží jmenovitá kontrola v `tests/test_hooks.py`; důvody a měření jsou v `decisions.md`.
