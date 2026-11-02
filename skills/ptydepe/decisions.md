# Rozhodnutí – /ptydepe

Soubor drží rozvahu a doklady skillu `/ptydepe`; za běhu skillu se nečte.

### Časté chyby z ostrých běhů

**Rozhodnuto 7. 9. 2026.** Všechny položky sekce *Časté chyby* se při ostrých bězích opravdu staly. Fronta kandidátů si přepsala vlastní položku dvakrát po sobě; po změně rodu „úhel“ → „hledisko“ zůstalo v původním tvaru jedenáct přívlastků; obhajoba termínu z paměti místo ze souborů vyrobila tabulku tří vrstev, kterou zdrojový dokument nikdy neobsahoval. Přepsání 1 120 souborů mimo verzování popisuje `docs/decisions.md`.

### Na čistý strom se nečeká

**Rozhodnuto 11. 9. 2026.** Nad `~/.claude` běží souběžné session skoro pořád, takže tvrdý požadavek na čistý strom by buď zablokoval každý běh, nebo se začal mlčky obcházet – a to druhé je horší, protože se pak přestane obcházet vědomě. Jinde ten důvod neplatí, ale pravidlo se kvůli tomu neštěpí: blokující je i tam jen průnik s rozsahem, a ten se posuzuje stejně. **Zamítnuto – nechat tvrdý požadavek a ptát se pokaždé.**

### Doklad o cizím souboru se cituje z grepu, i u preventivního zápisu

**Rozhodnuto 11. 9. 2026.** Heslo *hlavička* dokládalo zavedenost protějšku odkazem na `/autocommit`, který ve skutečnosti mluví o něčem jiném – doklad byl vymyšlený z paměti. Odtud pravidlo, že ani u preventivního zápisu se z paměti neberou fakta o cizích souborech.
