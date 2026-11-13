# Rozhodnutí o `/clauding`

## Počty spuštění skillů

**Rozhodnuto 13. 11. 2026.** Tabulka spuštění vlastních skillů za celé období, rozdělená podle toho, jak se skill spustil. Podnětem byla otázka, kolikrát se který skill volal včetně vnořených volání (`/merge` pouští `/end`).

- **Dva zdroje, ne jeden.** Zadané příkazem se berou z `history.jsonl`, protože ten úklid sessions nemaže a pokrývá celou historii; volání nástroje Skill jen z transcriptů, jinde je není kde vzít. Zavrženo: obojí z transcriptů – zadané příkazy by za odhadnuté dny zbytečně klesly na dolní mez.
- **Zdvojení zadaného příkazu a volání nástroje se ošetřuje, i když je vzácné.** Při zavedení se ze 768 volání nástroje jen 3 kryla s příkazem zadaným v téže odpovědi; harness zadaný skill spouští sám a nástroj nevolá.
- **Přejmenování ano, sloučení ne.** Přejmenovaný skill (`cleanup` → `end`, `spec` → `specify`, `propagate` → `replace`) git pozná jako přejmenování `SKILL.md` a je to tentýž skill. Sloučený (`break` do `end`, `continue` do `next`) byl jiný skill; připočítat ho k cílovému by nafouklo jeho číslo o volání, která dělala něco jiného. Zavrženo: ruční tabulka starých jmen v kódu – rozešla by se s dalším přejmenováním, kdežto git ho zachytí sám.
- **Jen vlastní skilly.** Skilly z pluginů a příkazy harnessu se nepočítají – otázka zněla na vlastní skilly a `/clear` nebo `/compact` by obsadily první místa, aniž by o práci cokoliv řekly.
- **Volání v subagentovi je vnořené.** Subagenta pouští práce, ne uživatel, takže na pokyn slovy být nemůže.
- **Na pokyn slovy zahrnuje i skill zmíněný uprostřed promptu.** Harness v takovém případě Claudovi připomene, že skill existuje, a ten ho spustí nástrojem; od „přimerguj to“ se to v transcriptu nerozliší a pro otázku „kolikrát běžel“ to rozlišovat není potřeba.
