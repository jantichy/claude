# Šablona `INSTALL.md`

Kostra, kterou `/package` vyplní pro každý balíček. Místa ve špičatých závorkách doplň, sekce bez obsahu vynech celé i s nadpisem. **Žádná cesta z autorova disku do ní nepatří** – ani jako informace, odkud soubor pochází. Obecná místa Claude Code (složka se skilly, s agenty, uživatelský `CLAUDE.md`) jmenovat smí, protože jsou stejná u každého příjemce.

```
# Instalace: <název balíčku>

Návod pro Clauda, který balíček instaluje. Uživateli na začátku jednou větou řekni, co budeš dělat, a na konci, co musí udělat sám.

## Co to je

<2–4 věty: co balíček umí a komu se hodí. U skillu jak se spouští.>

Balíček je **samostatný**: všechno, na co jeho soubory odkazují, leží v něm. Odkazy mezi soubory jsou relativní – vedou vždycky od souboru, ve kterém stojí. <U skillu: Je psaný pro Claude Code (CLI, desktop nebo web), protože stojí na <subagentech / souborech na disku / skriptech>. Běžíš-li v chatu claude.ai bez Claude Code, řekni to uživateli dřív, než začneš.>

## Obsah

| Cesta | Co to je |
|---|---|
| `<cesta v balíčku>` | <co to je a kdo to čte> |

## Postup

1. **Zjisti, co uživatel má.** Podívej se do složky Claude Code (`~/.claude/`, na Windows `%USERPROFILE%\.claude\`): jaké má skilly, jestli má vlastní soubory se znalostmi nebo pravidly a kde, a jestli už něco ze <skillu / domény> nemá pod stejným jménem.
2. **Zeptej se, kam co uložit.** Navrhni výchozí umístění a nech ho potvrdit nebo změnit:
   <po řádku za každou část balíčku, např.:>
   - **<skill>** – do složky se skilly (`~/.claude/skills/<jméno>/`, na Windows `%USERPROFILE%\.claude\skills\<jméno>\`). Celý adresář i s podadresáři.
   - **<doména>** – výchozí je <s balíčkem skillu, který ji čte / do složky, kde uživatel drží svoje znalosti>. <Má-li ji něco načítat i mimo skill: navrhni import do jeho `CLAUDE.md`.>
3. **Zkopíruj soubory na schválená místa.** Co tam už je, nepřepisuj – ukaž rozdíl a zeptej se.
4. **Srovnej odkazy s umístěním.** Zůstaly-li části balíčku vůči sobě tak, jak jsou v něm, relativní odkazy platí a nic se nemění. Rozdělil-li je uživatel jinam, přepiš každý odkaz, který mezi nimi vede, na novou cestu. Pak **ověř, že každý odkaz v nainstalovaných souborech vede na existující soubor** – jinak se instalace nehlásí jako hotová.
5. **Doinstaluj závislosti**, které v balíčku být nemůžou. Nejdřív ověř, jestli je uživatel nemá:
   <po odrážce za každou závislost:>
   - **<nástroj>** – k čemu je a co bez něj nepůjde. Instalace: Windows `<winget …>`, macOS `<brew …>`, Linux `<apt …>`. <Plugin: přes `/plugin`, marketplace `<…>`. Konektor: v nastavení claude.ai, uživatel ho připojí sám.>
6. **Ověř** v nové session (skill se načte až v ní): <konkrétní zkušební úkol a podle čeho se pozná, že prošel>.
7. **Řekni uživateli**, co je kde nainstalované, co jsi při tom změnil, na co ses ptal a jak rozhodl, a co musí udělat sám.

## Na co dát pozor

- <omezení a záměrné chování, které by příjemce mohl brát jako chybu>
```

Vypisuj ho jako soubor do balíčku, ne do konverzace.
