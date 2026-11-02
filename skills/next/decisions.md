# Rozhodnutí – /next

Soubor drží rozvahu a doklady skillu `/next`; za běhu skillu se nečte.

### Tvar výpisu: od kontextu k výběru, položky bez tučného písma a s kolečkem velikosti

**Rozhodnuto 16. 9. 2026.** Pořadí výpisu – poznámky, práce jinde, čekající položky a teprve nakonec nabídka těsně nad otázkou – i tvar položky (kolečko velikosti a název, bez tučného písma, bez stavu „připravené“ a bez velikosti slovem) si výslovně vyžádal uživatel. Výpis se čte očima, ne jako tabulka, a slova navíc na každém řádku ho zahlcovala. **Zamítnuto – barevné kuličky jako znak velikosti:** uživatel je odmítl jako moc křiklavé; obyčejný textový znak přebírá barvu textu terminálu.

### `ListAgents` obsazenost větví nenahradí

**Rozhodnuto 20. 9. 2026.** Ověřeno, že nástroj `ListAgents` vypisuje běžící session na stroji, ale jen jejich jméno, stav a stáří – ne větev ani adresář projektu. Rozhodnutí *nabídnout, nebo skrýt* stojí právě na větvi, takže registr i transcript čte dál vlastní skript `sessions.py`.

### Hlavní větev se nevypisuje jen kvůli živé session

**Rozhodnuto 28. 9. 2026.** Session, která ve worktree layoutu startuje v kořeni kontejneru a vlastní větev si ještě nezaložila, hlásí jako svou hlavní větev. Hlavní větev se proto vypisovala jako `occupied` a skill ji podle vlastního pravidla přestal nabízet – stačilo druhé otevřené okno nad projektem a práce mířící do hlavní větve zmizela z nabídky. Oprava: skript vypíše hlavní větev jedině tehdy, když v ní opravdu něco leží (commit nad hlavní referencí nebo neuložená změna v jejím worktree). Hlídají to dva testy v obou směrech.
