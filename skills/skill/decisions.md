# Rozhodnutí – /skill

Soubor drží rozvahu a doklady skillu `/skill`; za běhu skillu se nečte.

### Revize si nezapisuje, proti čemu se revidovalo naposledy

**Rozhodnuto 4. 9. 2026.** Nabízelo se zapsat datum poslední revize a příště projít jen to, co se od té doby v normě změnilo. **Zamítnuto.** Stav skillu je odvoditelný z toho, jak vypadá teď, kdežto zapsaný otisk je tvrzení, které nikdo neověřuje. Hlavně by ale zúžil revizi na diff normy, a tím minul přesně ten případ, kvůli kterému revize vznikla – rozejití, které se nikdy nepropsalo, protože ho tehdy nikdo nezpropagoval.

### Vyvolání nainstalovaného skillu se neměří skriptem `run_eval.py`

**Rozhodnuto 6. 9. 2026.** Skript ze `skill-creatoru` registruje popis jako dočasný slash command a hledá volání toho dočasného jména; model přitom zavolá skutečný nainstalovaný skill, takže se správné vyvolání počítá jako propadlé. Ověřeno na `/compose`: 8/16, všech osm propadů byly pozitivní případy, a kontrolní běh s maximálně dotěrným popisem dal 0/2 – měřil nástroj, ne popis. Odtud měření na skutečném kanálu přes `claude -p --output-format stream-json`.

### Měřicí běh s kladným výčtem nástrojů, ne se zákazem

**Rozhodnuto 30. 10. 2026.** Při měření vyvolání `/download` se měřený skill spustil doopravdy a do skutečné fronty stahování přibyla vymyšlená adresa. **Zamítnuto – `--disallowedTools Bash Edit Write`:** vyjmenované nástroje sice drží i proti `allowed-tools` skillu, jenže model sám hledá „jiný nástroj“, kterým zápis udělat, a zbytek sady i MCP servery mu zůstávají. Ověřeno dočasným skillem, který zapisuje přes Bash: bez omezení zapsal, s `--tools Skill,Read --strict-mcp-config` vyvolání proběhlo a soubor nevznikl.
