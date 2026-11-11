# Rozhodnutí – /next

Soubor drží rozvahu a doklady skillu `/next`; za běhu skillu se nečte.

### Tvar výpisu: od kontextu k výběru, položky bez tučného písma a s kolečkem velikosti

**Rozhodnuto 16. 9. 2026.** Pořadí výpisu – poznámky, práce jinde, čekající položky a teprve nakonec nabídka těsně nad otázkou – i tvar položky (kolečko velikosti a název, bez tučného písma, bez stavu „připravené“ a bez velikosti slovem) si výslovně vyžádal uživatel. Výpis se čte očima, ne jako tabulka, a slova navíc na každém řádku ho zahlcovala. **Zamítnuto – barevné kuličky jako znak velikosti:** uživatel je odmítl jako moc křiklavé; obyčejný textový znak přebírá barvu textu terminálu.

### `ListAgents` obsazenost větví nenahradí

**Rozhodnuto 20. 9. 2026.** Ověřeno, že nástroj `ListAgents` vypisuje běžící session na stroji, ale jen jejich jméno, stav a stáří – ne větev ani adresář projektu. Rozhodnutí *nabídnout, nebo skrýt* stojí právě na větvi, takže registr i transcript čte dál vlastní skript `sessions.py`.

### Hlavní větev se nevypisuje jen kvůli živé session

**Rozhodnuto 28. 9. 2026.** Session, která ve worktree layoutu startuje v kořeni kontejneru a vlastní větev si ještě nezaložila, hlásí jako svou hlavní větev. Hlavní větev se proto vypisovala jako `occupied` a skill ji podle vlastního pravidla přestal nabízet – stačilo druhé otevřené okno nad projektem a práce mířící do hlavní větve zmizela z nabídky. Oprava: skript vypíše hlavní větev jedině tehdy, když v ní opravdu něco leží (commit nad hlavní referencí nebo neuložená změna v jejím worktree). Hlídají to dva testy v obou směrech.

### Fronty podprojektů: vlastní celá, ostatní souhrnem

**Rozhodnuto 11. 11. 2026.** `collect.py` bral jen `todo.md` v kořeni repozitáře, takže session spuštěná v podsložce podprojektu bez vlastního `todo.md` dostala jen kořenovou frontu a položka odložená k datu v podprojektu se nepřipomněla nikde. Fronta nejbližšího podprojektu, ve kterém session stojí, se teď bere jako vlastní (jen vrchol, jako u kořene) a řadí se před kořenovou; ostatní podprojekty dostanou počet a první položku; položka odložená k datu se vrací z každého podprojektu, jakmile její den nastal. **Proč ne celé fronty všech podprojektů:** čtení souborů stojí milisekundy (hledání `todo.md` ve stromu 10 ms proti 1,6 s celého `collect.py`), zpomaluje výstup – větší JSON a delší výpis, který generuje model. **Zamítnuto – jen nejbližší projekt:** nevyřeší session v podsložce bez vlastního `todo.md`. **Zamítnuto – nechat jak je.** Podprojekty se čtou z worktree, kde session stojí (z kořene kontejneru z worktree hlavní větve), stejně jako přerušené běhy; přerušené běhy z nich dál nese sekce `Přerušený běh`, ne `projects`.

**Session v mezilehlé složce** (doplněno při `/end` téže session) bere za vlastní jediný nejbližší podprojekt pod sebou – zadání („ve kterém session stojí nebo nad kterým stojí“) myslelo oba směry. Leží-li jich v téže hloubce víc, zůstanou souhrnem, protože mezi nimi není jak vybrat.

**Hloubka hledání zůstává tři úrovně** (rozhodnuto při `/end` téže session) – stejně jako příkaz *Fáze 1*. Hlubší podprojekt (`a/b/docs/todo.md`) se nenajde ani pro přerušený běh, ani pro frontu; kdo v něm pracuje, spustí `/next` přímo v něm. **Zamítnuto – zvýšit o úroveň:** uživatel to nechtěl.
