# Kontrakt příkazů a kontrolní vrstvy

Podrobnosti ke kroku 12 v `SKILL.md`: šablona sekce `## Kontrakt příkazů`, co se zapnutím vzniká, jak se dává souhlas, které kontroly se nastavují konfigurací a jak se zakládá CI.

**Které vrstvy projekt vůbec má a co do které patří, drží `~/Dev/context/coding/quality.md`, *Vrstvy kontroly a co do které patří*.** Přečti si ji dřív, než začneš – rozhoduje se podle ní, ne podle typu projektu z kroku 11.

Zapiš do projektového `CLAUDE.md` sekci `## Kontrakt příkazů`:

```markdown
## Kontrakt příkazů

- test:      npm test
- typecheck: npm run typecheck
- lint:      npm run lint
- build:     npm run build
- dev:       npm run dev
- e2e:       npx playwright test
- coverage:  npm run coverage
- audit:     npm audit --omit=dev
- mutation:  npx stryker run
```

Zapisuj **jen ty klíče, které projekt opravdu umí spustit** – vymyšlený příkaz je horší než chybějící. U klíče, který chybí, napiš pod seznam, co tím odpadne: bez `dev` nemá `/attack` co spustit, bez `e2e` neproběhne průchod aplikací před nasazením, bez `coverage` neporovná `/review` pokrytí s prahem.

**Má-li projekt formátovač, přidej klíč `format`** – příkaz nad jedním souborem, který projde i nad typem souboru, jaký neumí (`npx prettier --write --ignore-unknown`; formátovač, který bere každý soubor jako svůj, jako `ruff format`, se zabalí do filtru přípony). Pouští ho po každé editaci `PostToolUse` hook; zavádí se jedním commitem, který naformátuje celý repozitář (`~/Dev/context/coding/quality.md`, *Formátování po editaci*).

Chybí-li projektu něco z toho úplně (typicky testy u nového projektu), **řádek vynech a řekni to** – ať je vidět, co se nebude kontrolovat. Doplní se, až to vznikne.

**Co tím vzniká.** Globální `Stop` hook `~/.claude/verify.sh` od téhle chvíle po každé odpovědi spustí `typecheck`, `lint` a `test` a **nepustí Clauda ukončit práci nad červeným stavem**. Hook je registrovaný jednou v `~/.claude/settings.json`, takže se nikde nic dalšího **neinstaluje** – ale spustit se v projektu ještě nesmí: chybí mu souhlas, viz níž. Vypnout se dá přepínačem `~/.claude/verify.sh --disable <project>`, který si stav drží mimo repozitář, nebo proměnnou `CLAUDE_NO_VERIFY=1` – soubor v projektu se k tomu nepoužívá, protože by se commitnul a vypnul kontrolu v každém klonu (`~/Dev/context/coding/quality.md`, *Průběžná kontrola*).

**Uživatel musí vydat souhlas, jinak průběžná kontrola neběží.** Kontrakt je kód v repozitáři a hook běží mimo permission systém, takže se souhlas dává jednou za projekt. Vypiš uživateli příkaz, ať ho spustí sám – **nespouštěj ho za něj**, tím by celá kontrola ztratila smysl:

```
~/.claude/verify.sh --allow <project-root>
```

Řekni mu u toho pravdu o tom, co schvaluje. Souhlas platí **pro repozitář včetně jeho worktree, ale jen pro ten kontrakt, který právě viděl**: podadresář s vlastním `CLAUDE.md` si ho nepůjčí a změna některého příkazu si vyžádá nové odsouhlasení. Co ty příkazy udělají, ale schválené není – `npm test` spustí, co je v `package.json`. **Vydat souhlas jde jen z terminálu**, takže ho za uživatele nespustí žádný nástroj ani skript. Do cizího naklonovaného repozitáře souhlas nepatří.

Definice a prahy jednotlivých kontrol jsou v `~/Dev/context/coding/quality.md`. Řekni uživateli jednou větou, co se právě zapnulo – ne aby ho to překvapilo, až mu hook poprvé zablokuje konec odpovědi.

**Zapni i kontroly, které se nespouštějí příkazem, ale konfigurací.** Kontrakt říká, *čím* se kontroluje; tyhle určují, *jak přísně*. Bez nich zůstanou prahy z `quality.md` jen napsané a nikdo je neměří:

1. **Přísnost překladače.** Ověř, že konfigurace projektu drží řádek *Přísnost překladače* z tabulky kontrol – u TypeScriptu je to `tsconfig.json`, u ostatních jazyků odpovídající přepínač (Python `mypy --strict`, Go `go vet`, PHP `declare(strict_types=1)` a maximální úroveň statické analýzy). Chybí-li, **navrhni změnu a nech ji potvrdit** – u staršího projektu může zapnutí `strict` vyrobit stovky chyb naráz, takže to nikdy neprováděj rovnou.
2. **Metriky složitosti v lintru.** Prahy z řádku *Metriky složitosti* přenes do konfigurace lintru – v ESLintu jsou to pravidla `complexity`, `max-lines-per-function`, `max-depth`, `max-params`. **Hodnoty opisuj z tabulky, ne odsud:** kdyby stály na dvou místech, rozejdou se. U existujícího projektu jich naráz vyplavou stovky, takže se nabízí nastavit je jako varování – jenže **varování `lint` neshodí, a kontrola se tím vypne**. Je to změkčení prahu, které podle `quality.md` smí schválit **jen člověk a s důvodem zapsaným do `docs/decisions.md`**, a to i s termínem, kdy se přitvrdí. Zeptej se tedy a rozhodnutí nech zapsat; sám to nezměkčuj.
3. **Vlastní pravidla statické analýzy.** Ptej se, jestli projekt má pravidlo, které by šlo zakódovat: do `.semgrep/` patří **projektová znalost, kterou model nemá** – „tenhle ORM pattern u nás nepoužíváme, dělá N+1“, „sem se nesmí volat přímo, jde se přes službu“. **Existuje-li takové pravidlo, adresář založ a rovnou ho tam zapiš** i s poznámkou, k čemu je. Neexistuje-li, nezakládej nic – prázdný adresář pro jistotu je jen další nepořádek.

## CI: co je na průběžnou kontrolu moc pomalé

Průběžná kontrola má strop 90 sekund na příkaz a běží **jen na tomhle stroji a jen se souhlasem**. Obejde ji commit odjinud, z GUI, s `--no-verify` i cizí fork.

CI je proto druhá vrstva, ne zdvojení té první. Běží po každém pushi bez ohledu na to, kdo commituje, a je v ní místo pro to, co se do vteřinového okna nevejde: `build`, `e2e`, `audit`, `gitleaks`, `coverage`, `a11y`, `perf` a mutation testing.

**Zakládá se, když je projekt na hostingu, který CI umí** (typicky GitHub). Nemá-li remote nebo běží-li jen lokálně, krok přeskoč a řekni to.

Workflow **nesmí opisovat příkazy z kontraktu ani si ho parsovat samo**. Opsaný seznam se po první změně rozejde a vypadá přitom platně (`~/.claude/RULES.md`, *Single source of truth*). Druhý parser je horší ještě o stupeň, protože se rozejde v detailech, které nikdo neporovnává.

Kontrakt vypíše **`~/.claude/verify.sh --contract <project>`** ve tvaru `key<tab>command`. Je to tentýž kód, který příkazy spouští lokálně, takže umí i filtraci HTML komentářů, pojistku proti dvěma sekcím téhož jména a klíč `cwd`.

**CI je napsané jednou a projekt ho jen volá.** Sdílený workflow `~/.claude/.github/workflows/contract.yml` pouští gitleaks, semgrep a kontrakt přes `verify.sh --contract` a runner `.github/run-contract.sh`. Projekt si do `.github/workflows/verify.yml` zapíše jen volání, **připnuté na 40místný SHA commitu** v `jantichy/claude` – dnešní hlavu zjistíš `git -C ~/.claude rev-parse origin/main`:

```yaml
name: Kontroly

on:
  push:
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  contract:
    uses: jantichy/claude/.github/workflows/contract.yml@<sha>
    with:
      install: python3 -m pip install --quiet ruff==0.16.7
```

Ten jeden SHA připíná workflow i nástroje: job si `jantichy/claude` naklonuje přesně v téhle verzi (`job.workflow_sha`) a proměnnou `CLAUDE_CONFIG` nastaví na ten klon. Volání přes `@main` nebo značku workflow odmítne. Projekt **nekopíruje workflow, runner ani jejich testy** – dřív to dělal a kopie se rozešly.

Volání se liší jen vstupy:

1. **`runs-on`** – výchozí `ubuntu-latest`; `macos-latest` jen tam, kde to kontrakt vyžaduje (Swift, Xcode).
2. **`install`** – shell, který doinstaluje, co kontrakt volá; na runneru není nic z Homebrew. Nedeklarovaná lokální závislost je nejčastější příčina prvního červeného běhu.
3. **`python-version`** – výchozí `3.12`.

**Klíče, které do CI patří**, drží runner jako jmenovaný seznam – vedle `typecheck`, `lint` a `test` i `build`, `e2e`, `audit`, `coverage`, `a11y`, `perf` a `mutation`. Rovnost s kontraktem to schválně není: `dev` je watch server, který nikdy neskončí, a kontrola, která na něm zčervená, je falešný poplach; `format` soubory přepisuje, nic nekontroluje.

**Test volajícího workflow** si projekt nese, ale jen jako volání sdílené kontroly – co se uvnitř hlídá (spouštěče bez filtrů, `permissions: contents: read`, job bez `if:`, připnuté volání), drží `~/.claude/.github/caller.py`:

```python
CONFIG = Path(os.environ.get("CLAUDE_CONFIG", Path.home() / ".claude"))

def test_ci_caller(self):
    done = subprocess.run([sys.executable, str(CONFIG / ".github" / "caller.py"),
                           str(ROOT / ".github" / "workflows" / "verify.yml")],
                          capture_output=True, text=True, check=False)
    self.assertEqual(0, done.returncode, done.stdout + done.stderr)
```

Stejně se v testech projektu dostane k `skills/links.py` a `order.py` – přes `CLAUDE_CONFIG`, ne přes kopii. **V CI chybějící skript test shodí, nepřeskočí** (`os.environ.get("CI")`): zelený běh, který nic nezkontroloval, se od kontroly nepozná.

**Po změně sdíleného CI se SHA v projektech posouvá ručně.** Dependabot to neudělá, protože `jantichy/claude` nemá vydání ani značky; workflow proto vypíše varování, když od připnutého commitu přibyla změna ve workflow, runneru, `verify.sh`, `links.py` nebo `order.py`.

## Dependabot: podmínka toho, aby připínání dávalo smysl

**Co je v CI staženo za běhu, patří připnout na konkrétní commit** – `uses: actions/checkout@v5` je pohyblivá značka, kterou může majitel akce kdykoliv přesměrovat jinam, a doložené útoky na dodavatelský řetěz (trivy-action, kics-github-action) šly přesně touhle cestou.

**Připnutí samo o sobě je ale jednosměrná sázka:** commit se nezmění pod rukama, jenže zmrazí i chyby, které v něm jsou. Proto se **zakládá spolu s `.github/dependabot.yml`** – ten sleduje, co je připnuté, a sám otevře pull request, jakmile vyjde novější verze. Bez něj je poctivější značka než SHA, které za půl roku nikdo neaktualizuje.

```yaml
version: 2
updates:
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: monthly
    cooldown:
      default-days: 7
```

**`cooldown` není volitelný.** Bez něj Dependabot navrhne aktualizaci na balíček zveřejněný před hodinou – a čerstvě publikovaná verze je typická cesta útoku na dodavatelský řetěz, protože škodlivý balíček bývá stažen dřív, než si toho někdo všimne. Týden odstupu aktualizace nezastaví, jen je posune za okno, ve kterém se to stihne odhalit. Semgrep to hlídá pravidlem `dependabot-missing-cooldown`, takže konfigurace bez něj shodí CI – doloženo 15. 9. 2026.

**Ekosystémů přidej tolik, kolik jich projekt má** – `npm`, `composer`, `gomod`, `pip` podle manifestu. `github-actions` patří k workflow, které samo používá akce; **projekt, jehož workflow jen volá sdílený `contract.yml`, ho nepotřebuje** – akce uvnitř hlídá Dependabot v `~/.claude` a SHA volání Dependabot posouvat neumí (viz výš). Nemá-li projekt ani žádný jiný ekosystém, `dependabot.yml` nezakládá.

**Co pod něj nespadá:** nástroje instalované v shellu (`brew install`, `curl | tar`) a skripty stažené za běhu. Dependabot do shellu nevidí, takže ty zůstávají ruční – a nástroje ze správce balíčků se nepřipínají vůbec, protože připnutý linter znamená zmrazené kontroly.

**Bez remote to nemá smysl** – je to služba GitHubu. U projektu bez remote krok přeskoč a řekni to.

**Neplatí to jen na nové projekty.** Najdeš-li v existujícím workflow nepřipnuté akce, je to nález: buď se připnou a přibude Dependabot, nebo se zapíše, proč ne. Vědomé zamítnutí, které stojí na argumentu „bez Dependabota to zastará“, padá ve chvíli, kdy se Dependabot zavede – **projdi tedy i `## Review` v `CLAUDE.md` a registr obcházení**, jestli tam takový záznam neleží; doloženo 15. 9. 2026, kdy zamítnutí z 13. 9. přežilo v obou.

**Badge do `README.md`** – u veřejného repozitáře je to jediné místo, kde je stav vidět zvenčí.

**Nasazuje se projekt někam?** Zjisti to (`vercel.json`, `netlify.toml`, `.github/workflows/`) a najdeš-li automatické nasazení z produkční větve, zapiš to do `## Nasazení` v `CLAUDE.md` i s upozorněním, že **merge do produkční větve je samotné nasazení** – detail řeší `/release`.
