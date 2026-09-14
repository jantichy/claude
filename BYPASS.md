# Čím se dají obejít zdejší kontroly

Mapa známého povrchu, ne seznam vyřešených problémů. U každé vynucovací vrstvy stojí, **čím se dá obejít**, **co to chytí** a **co je vědomě přijaté riziko**.

**Proč katalog, a ne zákaz.** Zákaz („testy jsou během implementace read-only“) se dá dodržet i obejít a nikde po tom nezůstane stopa. Katalog je auditovatelný: dá se přečíst, rozporovat a doplnit, a hlavně je z něj vidět, co se **vědomě** nehlídá. Vrstva, u které nikdo neví, kudy se obchází, není bezpečná – jen neprozkoumaná.

**Jak se to čte.** `accepted` neznamená „nevadí“, ale „víme o tom a rozhodli jsme se to nehlídat“. U každého takového řádku je důvod. Objeví-li se cesta, která tu není, patří sem **dřív**, než se zavře – jinak katalog zestárne tím nejhorším způsobem: bude vypadat úplně.

**Rozsah je tenhle repozitář.** Obecné pravidlo, že takový registr má vzniknout, drží `~/Dev/context/coding/quality.md`.

## Průběžná kontrola (`verify.sh` jako `Stop` hook)

| Čím se obejde | Co to chytí | Stav |
|---|---|---|
| Kontrakt v `CLAUDE.md` je kód z repozitáře – dá se do něj dopsat cokoliv | Souhlas se vydává **na konkrétní znění kontraktu**; změna ho zneplatní a hook se zastaví | hlídáno, `tests/test_verify.py` |
| Souhlas si vydá proces sám | Vydání čte `/dev/tty`, kterou proces bez řídicího terminálu nemá – neprojde ani `!` prefix v Claude Code | hlídáno |
| Přesměrovat stav běhu a podstrčit „tenhle strom už prošel“ | `RUN_DIR` je natvrdo pod `$HOME`, `XDG_STATE_HOME` se ignoruje | hlídáno, od 14. 9. 2026 |
| Podvrhnout sekci `## Kontrakt příkazů` v komentáři nebo v bloku kódu nad tou pravou | Tělo se čte parserem podle CommonMarku; dvě sekce téhož jména běh zastaví | hlídáno |
| `CLAUDE_NO_VERIFY=1` | Nic – proměnná kontrolu vypne | **accepted**: je to únikový východ pro případ, kdy je kontrola sama rozbitá. Kdo ho použije, ví to; v logu session je to vidět. |
| Commit z jiného stroje, z GUI nebo s `--no-verify` | Nic lokálně | **accepted**: přesně proto existuje CI – ta běží bez ohledu na to, kdo a odkud commituje, a je to jediná vrstva, kterou lokální obejití nezasáhne. |
| Splnit krok `test` triviálním testem | Nic automaticky | **accepted**: měří to jen mutační testy, a ty tu běží nad vzory kontrol, ne nad celou sadou. Proti tomu stojí zákaz editace testů během implementace a to, že diff testů čte `/review`. |

## Git hook na zprávu merge commitu

| Čím se obejde | Co to chytí | Stav |
|---|---|---|
| `git commit --no-verify` | Nic | **accepted**: hook brání nečitelné historii, ne útoku. Kdo ho vypne, přepisuje si vlastní historii. |
| Vlastní `core.hooksPath` v projektu | Nic – projektové nastavení přebije globální | **accepted**, je to zamýšlené: projekt smí mít vlastní hooky. Lokální `commit-msg` naopak zdejší hook volá, aby se nevypnul omylem. |
| Zpráva, která pravidlo splní formálně („Merge hotové práce“) | Nic | **accepted**: smysl je donutit napsat větu, ne posoudit její kvalitu. |

## CI (`.github/workflows/verify.yml`)

| Čím se obejde | Co to chytí | Stav |
|---|---|---|
| Přepsat workflow v témže PR | Nic | **accepted**: repozitář nemá secrets, `GITHUB_TOKEN` je read-only a runner je efemérní, takže cizí kód nemá co ukrást. Podrobně v `.claude/CLAUDE.md`, `## Review`. |
| PR z forku spustí kontrakt z cizí větve | `fork-pr-contributor-approval` je na `first_time_contributors` | **accepted** pro přispěvatele, který už jednou prošel |
| Akce nejsou připnuté na SHA | Nic | **accepted**: repozitář nemá secret, který by šlo ukrást, a připnutí bez Dependabota znamená akce, které za půl roku zastarají. Plné zdůvodnění v `.claude/CLAUDE.md`, `## Review`. |

## Permission systém (`settings.json`)

| Čím se obejde | Co to chytí | Stav |
|---|---|---|
| Zavolat zakázaný příkaz přes interpret (`python3 -c`, `osascript`) | Nic – deny porovnává text příkazu | **accepted**, je to vlastnost mechanismu. Proto se na deny nespoléhá tam, kde má držet skutečná hranice (souhlas průběžné kontroly čte `/dev/tty`). |
| Git alias z `~/.gitconfig` (`git cc` = `add -A` + `--amend` + `--force`) | Delší aliasy jsou v deny jmenovitě | **částečně**: jednopísmenné (`a`, `c`, `p`, `m`) pokrýt nejdou, vzor `git c:*` by zablokoval i `git commit`. Drží to pravidlo v `RULES.md`, *Commituj jmenované cesty*. |
| Nový destruktivní příkaz, na který vzor nemyslel | Nic | **accepted**: seznam je výčet, ne princip. Roste, když se něco objeví. |

## Status line (`statusline.sh`)

| Čím se obejde | Co to chytí | Stav |
|---|---|---|
| Cizí `.git/config` s `filter.*.clean` spustí program při čtení souborů | Konfigurace se před čtením prohledá a při nálezu se počet změn nevypíše | hlídáno, `tests/test_statusline.py` |
| Hodnota z JSONu vyhodnocená jako aritmetický výraz | Číselné vstupy projdou přes `num()` | hlídáno, od 14. 9. 2026 |
| Jiný git mechanismus spouštějící program, na který blacklist nemyslí | Nic | **accepted**: blacklist je výčet. Proti tomu stojí, že status line nespouští nic jiného než čtecí `git` příkazy. |
