# /release – nasazení jako vědomý úkon, ne vedlejší efekt

> **Součást životního cyklu projektu.** Tenhle skill patří do ucelené sady deseti skillů, které vedou práci od založení projektu až po nasazení. Každý má svůj krok a žádný nedělá práci toho vedle:
>
> [`/project`](../project/README.md) → [`/specify`](../specify/README.md) → [`/oponent`](../oponent/README.md) → [`/breakdown`](../breakdown/README.md) → [`/implement`](../implement/README.md) → [`/review`](../review/README.md) → [`/consistency`](../consistency/README.md) → [`/cleanup`](../cleanup/README.md) → [`/attack`](../attack/README.md) → **`/release`**
>
> Projít se nemusí celá – u drobné změny odpadá zadání i plán, u projektu bez kódu nasazení.

Nasadí hotovou práci do produkce: projde brány předtím, ošetří migrace databáze, nechá si nasazení výslovně potvrdit, ověří výsledek na produkční adrese a **ví, jak se vrátit zpátky**. Chyba v repozitáři se opraví commitem, chyba v produkci se opravuje před lidmi, kteří na to koukají – proto je nasazení samostatný krok se svými pravidly, ne poslední bod nějakého jiného postupu.

## Co umí

1. **Nasadí to, co řeknete** – výchozí je hlavní větev, ale zvládne i konkrétní větev, tag nebo jednotlivý commit. Nic se přitom nepřeskakuje.
2. **Zjistí si sám, jak se projekt nasazuje** – z jeho instrukcí, z konfigurace nasazovací platformy, z nastavení kontejneru nebo skriptu. Když to nikde není, zeptá se a odpověď rovnou zapíše, aby se příště neptal.
3. **Brány před nasazením:** čistý pracovní strom, zelená linka, produkční build, průchod aplikací, audit závislostí, hledání tajemství v repozitáři a kontrola, že nová proměnná prostředí je nastavená i v produkci.
4. **Ověří, jestli práce vůbec prošla revizí** – nehádá to a neptá se, čte to ze záznamu a ukáže, co od té doby přibylo a co tedy nikdo neprověřil.
5. **Migrace databáze řeší dopředu kompatibilně** – po krocích, mezi kterými funguje stará i nová verze kódu.
6. **Jedna potvrzovací otázka nad kompletním přehledem** – co, kam, jaké brány prošly, jaké migrace, jak se vrátit zpátky a co se bude sledovat.
7. **Ověření po nasazení na produkční adrese** – načtení, hlavní scénář celý včetně odeslání formuláře, data, chybové logy a u webu i to, jestli měření skutečně odesílá očekávané události.
8. **Sledovací okno s konkrétním koncem.** Nasazení nekončí ve chvíli, kdy aplikace odpoví.

## Proč zrovna tenhle

- **Nikdy se nespustí sám.** Ani jako pokračování jiné práce, ani proto, že jste na začátku dlouhého sezení řekli „a nasaď to" – to byl záměr, ne potvrzení.
- **Odděluje integrační a nasazovací větev.** Nasazovací platformy si po založení projektu nastaví jako produkční hlavní větev, takže každý přimergovaný kus jde rovnou ven. Skill to řeší povýšením do samostatné větve – hlavní větev pak zůstává místem, kde se integruje, a každý merge do ní dostane vlastní adresu na proklikání.
- **Návrat musí existovat dřív, než se nasadí.** Neumíte-li odpovědět na otázku „jak se za deset minut vrátíme", nenasazuje se.
- **Ví, že kód se vrátí, ale data ne.** Nasazujete-li starší stav, než je v produkci, řekne to nahlas a data vyřeší zvlášť.
- **Během okna se nic nemaže ani nepřejmenovává.** Odebraný sloupec znamená, že návrat kódu shodí aplikaci na datech, která nová verze zapsala – a máte rozbito na obou stranách.
- **Neopravuje.** Najde-li brána problém, skončí a pošle to zpátky. Oprava dělaná v předvečer nasazení je přesně ta, která spadne.
- **Sledovací okno má vlastníka.** Celá třída chyb se projeví až později – doplňování dat, cache, chyba, která nastane až na produkčním objemu. Okno se zavírá výslovnou větou, ne tichem, a nasazení do té doby není hotové.
- **Chyba, která projde vším, se zapisuje.** U každého takového případu musí vzniknout nová brána, nebo výslovné rozhodnutí, že se ta třída chyb hlídat nebude. Jinak se soustava učí jen z chyb, které už chytat umí.

## Jak se to používá

```
/release              # nasadí hlavní větev
/release v1.4.0       # nasadí konkrétní tag
```

Skill projde brány, ukáže přehled, počká na potvrzení, nasadí, ověří a otevře sledovací okno.

## Ukázka výstupu

```
## Připraveno k nasazení

**Co:** 7 commitů · objednávky, mailing · v1.4.0
**Nasazuje se:** main → production
**Kam:** produkce, https://example.cz
**Brány:** zelená linka ✅ · build ✅ · e2e ✅ · review ✅ · attack ✅ · audit ✅ · tajemství ✅
**Migrace:** expand krok 1, záloha z 14:32
**Návrat:** revert commitu a nový build (~4 min)
**Po nasazení sleduji:** chybovost a konverzní události, do druhého dne
```

## Co nedělá

- **Neopravuje ani nedodělává.**
- **Nerozhoduje o obsahu vydání.** Nasazuje se to, co je na větvi; vybírat commity na poslední chvíli je cesta k nasazení půlky funkce.
- **Nezakládá infrastrukturu.** Nastavení prostředí, domén a proměnných je jednorázová práce, ne součást každého vydání.
- **Nepřenastavuje produkční větev sám.** Řekne to a nabídne jako samostatný krok – zásah do infrastruktury uprostřed vydání nedělá.

## Jak si ho nainstalovat

Nechte to na Claudovi. Otevřete si Claude Code a napište mu:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/release a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.

Skill se odkazuje na **moje soukromé standardy** pro kód a analytiku a na strukturu projektové dokumentace – **řekněte Claudovi, ať ty odkazy nahradí vašimi, nebo je smaže**. Aby brány měly co spouštět, potřebuje projekt mít v instrukcích zapsané, čím se u něj pouštějí testy, build, průchod aplikací a audit závislostí – i s tím vám Claude pomůže.


**Nebo celou sadu naráz.** Chcete-li místo jednoho skillu rovnou celý životní cyklus, napište mu tohle:

> Jdi na https://github.com/jantichy/claude/tree/main/skills a nainstaluj mi do `~/.claude/skills/` celý životní cyklus: project, specify, oponent, breakdown, implement, review, consistency, cleanup, attack a release. U každého si přečti README a řekni mi, co k nim potřebuju doplnit.

---

### Požadavky a omezení

Git a přístup k nasazovacímu prostředí. Nastavení oddělené nasazovací větve je popsané pro Vercel, Netlify a Cloudflare Pages; pro vlastní server nebo kontejner se použije příkaz zapsaný v instrukcích projektu – skill si deploy příkaz nikdy nevymýšlí, protože špatně odhadnutý cíl přepíše cizí web. Kontrola tajemství v repozitáři je volitelná a potřebuje `gitleaks`.
