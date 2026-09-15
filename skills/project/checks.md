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

Chybí-li projektu něco z toho úplně (typicky testy u nového projektu), **řádek vynech a řekni to** – ať je vidět, co se nebude kontrolovat. Doplní se, až to vznikne.

**Co tím vzniká.** Globální `Stop` hook `~/.claude/verify.sh` od téhle chvíle po každé odpovědi spustí `typecheck`, `lint` a `test` a **nepustí Clauda ukončit práci nad červeným stavem**. Hook je registrovaný jednou v `~/.claude/settings.json`, takže se nikde nic dalšího **neinstaluje** – ale spustit se v projektu ještě nesmí: chybí mu souhlas, viz níž. Vypnout se dá souborem `.claude/no-verify` v projektu nebo proměnnou `CLAUDE_NO_VERIFY=1`.

**Uživatel musí vydat souhlas, jinak průběžná kontrola neběží.** Kontrakt je kód v repozitáři a hook běží mimo permission systém, takže se souhlas dává jednou za projekt. Vypiš uživateli příkaz, ať ho spustí sám – **nespouštěj ho za něj**, tím by celá kontrola ztratila smysl:

```
~/.claude/verify.sh --allow <kořen projektu>
```

Řekni mu u toho pravdu o tom, co schvaluje. Souhlas platí **pro repozitář včetně jeho worktree, ale jen pro ten kontrakt, který právě viděl**: podadresář s vlastním `CLAUDE.md` si ho nepůjčí a změna některého příkazu si vyžádá nové odsouhlasení. Co ty příkazy udělají, ale schválené není – `npm test` spustí, co je v `package.json`. **Vydat souhlas jde jen z terminálu**, takže ho za uživatele nespustí žádný nástroj ani skript. Do cizího naklonovaného repozitáře souhlas nepatří.

Definice a prahy jednotlivých kontrol jsou v `~/Dev/context/coding/quality.md`. Řekni uživateli jednou větou, co se právě zapnulo – ne aby ho to překvapilo, až mu hook poprvé zablokuje konec odpovědi.

**Zapni i kontroly, které se nespouštějí příkazem, ale konfigurací.** Kontrakt říká, *čím* se kontroluje; tyhle určují, *jak přísně*. Bez nich zůstanou prahy z `quality.md` jen napsané a nikdo je neměří:

1. **Přísnost překladače.** Ověř, že konfigurace projektu drží řádek *Přísnost překladače* z tabulky kontrol – u TypeScriptu je to `tsconfig.json`, u ostatních jazyků odpovídající přepínač (Python `mypy --strict`, Go `go vet`, PHP `declare(strict_types=1)` a maximální úroveň statické analýzy). Chybí-li, **navrhni změnu a nech ji potvrdit** – u staršího projektu může zapnutí `strict` vyrobit stovky chyb naráz, takže to nikdy neprováděj rovnou.
2. **Metriky složitosti v lintru.** Prahy z řádku *Metriky složitosti* přenes do konfigurace lintru – v ESLintu jsou to pravidla `complexity`, `max-lines-per-function`, `max-depth`, `max-params`. **Hodnoty opisuj z tabulky, ne odsud:** kdyby stály na dvou místech, rozejdou se. U existujícího projektu jich naráz vyplavou stovky, takže se nabízí nastavit je jako varování – jenže **varování `lint` neshodí, a kontrola se tím vypne**. Je to změkčení prahu, které podle `quality.md` smí schválit **jen člověk a s důvodem zapsaným do `docs/decisions.md`**, a to i s termínem, kdy se přitvrdí. Zeptej se tedy a rozhodnutí nech zapsat; sám to nezměkčuj.
3. **Vlastní pravidla statické analýzy.** Ptej se, jestli projekt má pravidlo, které by šlo zakódovat: do `.semgrep/` patří **projektová znalost, kterou model nemá** – „tenhle ORM pattern u nás nepoužíváme, dělá N+1“, „sem se nesmí volat přímo, jde se přes službu“. **Existuje-li takové pravidlo, adresář založ a rovnou ho tam zapiš** i s poznámkou, k čemu je. Neexistuje-li, nezakládej nic – prázdný adresář pro jistotu je jen další nepořádek.

## CI: co je na průběžnou kontrolu moc pomalé

Průběžná kontrola má strop 60 sekund na příkaz a běží **jen na tomhle stroji a jen se souhlasem**. Obejde ji commit odjinud, z GUI, s `--no-verify` i cizí fork.

CI je proto druhá vrstva, ne zdvojení té první. Běží po každém pushi bez ohledu na to, kdo commituje, a je v ní místo pro to, co se do vteřinového okna nevejde: `build`, `e2e`, `audit`, `gitleaks`, `coverage`, `a11y`, `perf` a mutation testing.

**Zakládá se, když je projekt na hostingu, který CI umí** (typicky GitHub). Nemá-li remote nebo běží-li jen lokálně, krok přeskoč a řekni to.

Workflow **nesmí opisovat příkazy z kontraktu ani si ho parsovat samo**. Opsaný seznam se po první změně rozejde a vypadá přitom platně (`~/.claude/RULES.md`, *Neopisuj seznam, který má vlastní zdroj pravdy*). Druhý parser je horší ještě o stupeň, protože se rozejde v detailech, které nikdo neporovnává.

Kontrakt vypíše **`~/.claude/verify.sh --contract <projekt>`** ve tvaru `klíč<tab>příkaz`. Je to tentýž kód, který příkazy spouští lokálně, takže umí i filtraci HTML komentářů, pojistku proti dvěma sekcím téhož jména a klíč `cwd`.

**Na runneru `verify.sh` není**, takže ho tam workflow musí dostat: buď ho projekt stáhne (`curl -fsSL https://raw.githubusercontent.com/jantichy/claude/main/verify.sh`), nebo si ho nese ve vlastním repozitáři. Stažení připni na konkrétní commit, ne na `main` – jinak si do CI pouštíš cizí skript, který se může kdykoliv změnit.

Hotovou a ověřenou podobu má `~/.claude/.github/workflows/verify.yml`; **vezmi ji jako předlohu a uprav čtyři věci**:

1. **Runner.** `ubuntu-latest`, pokud projekt nepotřebuje macOS (Swift, Xcode) – je rychlejší a u privátního repozitáře levnější.
2. **Nástroje.** Doinstaluj, co kontrakt opravdu volá; na runneru není nic z Homebrew. Nedeklarovaná lokální závislost je tu nejčastější příčina prvního červeného běhu.
3. **Klíče.** Výčet ve workflow je **jmenovaný seznam kroků, které do CI patří** – vedle `typecheck`, `lint` a `test` i `build`, `e2e`, `audit`, `coverage`, `a11y`, `perf` a `mutation`. Průběžná kontrola je nepouští, CI ano. **Nedělej z něj rovnost s kontraktem:** ten smí nést i klíče, které se nespouštějí (`dev` je watch server, který nikdy neskončí, `cwd` není příkaz), a kontrola, která na nich zčervená, je falešný poplach – tedy ten horší směr selhání.

4. **Kroky mimo kontrakt.** `gitleaks` a `semgrep` nejsou příkazy projektu, takže v kontraktu nestojí a smyčka přes něj je nepustí – do CI ale patří, protože jsou deterministické, rychlé a jejich nález je vždy kritický. Zapiš je do workflow jako samostatné kroky a doinstaluj je v něm; bez toho tvrdí katalog kontrol něco, co žádná cesta nezařídí.

**Napiš k tomu test, který ověří, že se workflow s kontraktem nerozešlo** – že pouští právě jeho klíče a žádný příkaz si neopisuje. Je to vynucovací vrstva jako každá jiná (`~/Dev/context/coding/quality.md`, *Vynucovací vrstva se testuje jako kód, obousměrně*); předloha je v `~/.claude/tests/test_hooks.py`.

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

**Ekosystémů přidej tolik, kolik jich projekt má** – `npm`, `composer`, `gomod`, `pip` podle manifestu. `github-actions` patří ke každému projektu s workflow.

**Co pod něj nespadá:** nástroje instalované v shellu (`brew install`, `curl | tar`) a skripty stažené za běhu. Dependabot do shellu nevidí, takže ty zůstávají ruční – a nástroje ze správce balíčků se nepřipínají vůbec, protože připnutý linter znamená zmrazené kontroly.

**Bez remote to nemá smysl** – je to služba GitHubu. U projektu bez remote krok přeskoč a řekni to.

**Neplatí to jen na nové projekty.** Najdeš-li v existujícím workflow nepřipnuté akce, je to nález: buď se připnou a přibude Dependabot, nebo se zapíše, proč ne. Vědomé zamítnutí, které stojí na argumentu „bez Dependabota to zastará“, padá ve chvíli, kdy se Dependabot zavede – **projdi tedy i `## Review` v `CLAUDE.md` a registr obcházení**, jestli tam takový záznam neleží; doloženo 15. 9. 2026, kdy zamítnutí z 13. 9. přežilo v obou.

**Badge do `README.md`** – u veřejného repozitáře je to jediné místo, kde je stav vidět zvenčí.

**Nasazuje se projekt někam?** Zjisti to (`vercel.json`, `netlify.toml`, `.github/workflows/`) a najdeš-li automatické nasazení z produkční větve, zapiš to do `## Nasazení` v `CLAUDE.md` i s upozorněním, že **merge do produkční větve je samotné nasazení** – detail řeší `/release`.
