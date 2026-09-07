# Kontrakt příkazů, zelená linka a kontroly kvality

Podrobnosti ke kroku 12 v `SKILL.md`: šablona sekce `## Příkazy`, co se zapnutím vzniká, jak se dává souhlas a které kontroly se nastavují konfigurací.

Zapiš do projektového `CLAUDE.md` sekci `## Příkazy`:

```markdown
## Příkazy

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

**Co tím vzniká.** Globální `Stop` hook `~/.claude/green-line.sh` od téhle chvíle po každém tahu spustí `typecheck`, `lint` a `test` a **nepustí Clauda ukončit práci nad červeným stavem**. Hook je registrovaný jednou v `~/.claude/settings.json`, takže se nikde nic dalšího **neinstaluje** – ale spustit se v projektu ještě nesmí: chybí mu souhlas, viz níž. Vypnout se dá souborem `.claude/no-green-line` v projektu nebo proměnnou `CLAUDE_NO_GREEN_LINE=1`.

**Uživatel musí vydat souhlas, jinak linka neběží.** Kontrakt je kód v repozitáři a hook běží mimo permission systém, takže se souhlas dává jednou za projekt. Vypiš uživateli příkaz, ať ho spustí sám – **nespouštěj ho za něj**, tím by celá kontrola ztratila smysl:

```
~/.claude/green-line.sh --allow <kořen projektu>
```

Řekni mu u toho pravdu o tom, co schvaluje: souhlas platí **pro repozitář, ne pro ty konkrétní řádky**. `npm test` spustí, co je v `package.json`, a to se neschvaluje. Do cizího naklonovaného repozitáře souhlas nepatří.

Definice a prahy jednotlivých kontrol jsou v `~/Dev/context/coding/quality.md`. Řekni uživateli jednou větou, co se právě zapnulo – ne aby ho to překvapilo, až mu hook poprvé zablokuje konec tahu.

**Zapni i kontroly, které se nespouštějí příkazem, ale konfigurací.** Kontrakt říká, *čím* se kontroluje; tyhle určují, *jak přísně*. Bez nich zůstanou prahy z `quality.md` jen napsané a nikdo je neměří:

1. **Přísnost překladače.** Ověř, že konfigurace projektu drží řádek *Přísnost překladače* z tabulky kontrol – u TypeScriptu je to `tsconfig.json`, u ostatních jazyků odpovídající přepínač (Python `mypy --strict`, Go `go vet`, PHP `declare(strict_types=1)` a maximální úroveň statické analýzy). Chybí-li, **navrhni změnu a nech ji potvrdit** – u staršího projektu může zapnutí `strict` vyrobit stovky chyb naráz, takže to nikdy neprováděj rovnou.
2. **Metriky složitosti v lintru.** Prahy z řádku *Metriky složitosti* přenes do konfigurace lintru – v ESLintu jsou to pravidla `complexity`, `max-lines-per-function`, `max-depth`, `max-params`. **Hodnoty opisuj z tabulky, ne odsud:** kdyby stály na dvou místech, rozejdou se. U existujícího projektu jich naráz vyplavou stovky, takže se nabízí nastavit je jako varování – jenže **varování `lint` neshodí, a kontrola se tím vypne**. Je to změkčení prahu, které podle `quality.md` smí schválit **jen člověk a s důvodem zapsaným do `docs/decisions.md`**, a to i s termínem, kdy se přitvrdí. Zeptej se tedy a rozhodnutí nech zapsat; sám to nezměkčuj.
3. **Vlastní pravidla statické analýzy.** Ptej se, jestli projekt má pravidlo, které by šlo zakódovat: do `.semgrep/` patří **projektová znalost, kterou model nemá** – „tenhle ORM pattern u nás nepoužíváme, dělá N+1“, „sem se nesmí volat přímo, jde se přes službu“. **Existuje-li takové pravidlo, adresář založ a rovnou ho tam zapiš** i s poznámkou, k čemu je. Neexistuje-li, nezakládej nic – prázdný adresář pro jistotu je jen další nepořádek.

**Nasazuje se projekt někam?** Zjisti to (`vercel.json`, `netlify.toml`, `.github/workflows/`) a najdeš-li automatické nasazení z produkční větve, zapiš to do `## Nasazení` v `CLAUDE.md` i s upozorněním, že **merge do produkční větve je samotné nasazení** – detail řeší `/release`.
