# Rozhodnutí o `/clauding`

## Počty spuštění skillů

**Rozhodnuto 13. 11. 2026.** Tabulka spuštění vlastních skillů za celé období, rozdělená podle toho, jak se skill spustil. Podnětem byla otázka, kolikrát se který skill volal včetně vnořených volání (`/merge` pouští `/end`).

- **Dva zdroje, ne jeden.** Zadané příkazem se berou z `history.jsonl`, protože ten úklid sessions nemaže a pokrývá celou historii; volání nástroje Skill jen z transcriptů, jinde je není kde vzít. Zavrženo: obojí z transcriptů – zadané příkazy by za odhadnuté dny zbytečně klesly na dolní mez.
- **Zdvojení zadaného příkazu a volání nástroje se ošetřuje, i když je vzácné.** Při zavedení se ze 768 volání nástroje jen 3 kryla s příkazem zadaným v téže odpovědi; harness zadaný skill spouští sám a nástroj nevolá.
- **Přejmenování ano, sloučení ne.** Přejmenovaný skill (`cleanup` → `end`, `spec` → `specify`, `propagate` → `replace`) git pozná jako přejmenování `SKILL.md` a je to tentýž skill. Sloučený (`break` do `end`, `continue` do `next`) byl jiný skill; připočítat ho k cílovému by nafouklo jeho číslo o volání, která dělala něco jiného. Zavrženo: ruční tabulka starých jmen v kódu – rozešla by se s dalším přejmenováním, kdežto git ho zachytí sám.
- **Jen vlastní skilly.** Skilly z pluginů a příkazy harnessu se nepočítají – otázka zněla na vlastní skilly a `/clear` nebo `/compact` by obsadily první místa, aniž by o práci cokoliv řekly.
- **Volání v subagentovi je vnořené.** Subagenta pouští práce, ne uživatel, takže na pokyn slovy být nemůže.
- **Na pokyn slovy zahrnuje i skill zmíněný uprostřed promptu.** Harness v takovém případě Claudovi připomene, že skill existuje, a ten ho spustí nástrojem; od „přimerguj to“ se to v transcriptu nerozliší a pro otázku „kolikrát běžel“ to rozlišovat není potřeba.

## Čas po projektech

**Rozhodnuto 13. 11. 2026.** Kolik času připadá na každý projekt zvlášť a kolik projektů je rozdělaných naráz.

- **Projekt je první podsložka pod kořeny, ne git repozitář ani adresář session.** Repozitář by nechal podprojekty klienta zvlášť a smazaný adresář by už nezařadil; adresář session by rozdělil projekt po větvích a souběh dvou větví by vypadal jako souběh projektů.
- **Paralelizace je poměr součtu hodin po projektech k celkovému času.** Vyjde jako průměrný počet projektů rozdělaných naráz a nepotřebuje žádné vlastní pravidlo. Měří rozdělanou práci, ne pozornost – to je v souladu s tím, že skill měří čas v Claudovi, ne u klávesnice.
- **Přestěhované projekty se párují podle jména automaticky.** První návrh nechával staré cesty pod `~/Dev` pod starým jménem, protože srovnání jen názvů adresářů s transcripty nenašlo žádný protějšek. Mylně: cestu `~/Dev/...` nese i `history.jsonl`, ze kterého je odhad starších dnů, a z 65 starých projektů jich 34 (68 % jejich promptů) protějšek téhož jména má. Bez párování by se jeden projekt rozpadl na novější čas a starší odhad ve dvou řádcích. Zavrženo: ruční seznam přejmenování – musel by se udržovat při každém stěhování; jinak přejmenované projekty proto zůstávají pod starým jménem.
- **Adresář s transcripty se při stěhování přejmenovává, záznamy v něm ne.** Proto se projekt bere z názvu adresáře porovnaného se složkami na disku, ne z cesty v záznamu.
- **Scratchpad session patří projektu, který ji pustil.** Bez toho tvořily běhy `claude -p` při měření skillů 180 hodin samostatného „projektu“ a nadsazovaly souběh.
- **Jména projektů stojí v zajímavostech všechna, i klientská.** Rozhodl uživatel: věta je nejinformativnější a před sdílením ji projde sám. Zavrženo: anonymizovat klienty a věta bez jmen.
