# Rozhodnutí – /project

Rozvaha a doklady ke skillu `/project`; za běhu skillu se nečte.

### Připnuté akce v CI se zakládají spolu s Dependabotem s povinným `cooldown`

**Rozhodnuto 15. 9. 2026.** Pohyblivou značku akce může její majitel kdykoliv přesměrovat a doložené útoky na dodavatelský řetěz (trivy-action, kics-github-action) šly přesně touhle cestou; proto se akce připínají na commit. Připnutí bez Dependabota by ale zmrazilo i chyby, takže se zakládá spolu s ním.

`cooldown` je povinný, protože semgrep pravidlem `dependabot-missing-cooldown` shodí CI konfiguraci, která ho nemá – doloženo týž den.

Proč se při zavádění Dependabota prochází i `## Review` v `CLAUDE.md` a registr obcházení: zamítnutí nepřipnutých akcí z 13. 9. 2026, které stálo na argumentu „bez Dependabota to zastará“, přežilo v obou místech i poté, co se Dependabot zavedl.

### Dvojvolby se ptají naráz, nezaškrtnutá volba je výchozí stav

**Rozhodnuto 23. 11. 2026.** Layout na disku, umístění dokumentace, autocommit a paměťová politika se ptaly čtyřmi samostatnými otázkami, každá s jedinou volbou ano/ne. Teď je to jedna otázka s `multiSelect` hned po gitu (krok 3, *Přepínače*) a kroky 4, 5, 9 a 10 ji jen provádějí; v operativním projektu totéž pro git a autocommit.

`AskUserQuestion` neumí volbu předvybrat, takže zaškrtávátko nemůže nést „ano“ jako výchozí. Řeší se to formulací: každá volba je odchylka od výchozího stavu – u nového projektu od doporučené hodnoty, u existujícího od dnešního –, takže prázdný výběr je vždy bezpečný. Proto se volba paměti jmenuje *Povolit trvalou Memory*, ne *Jen lokální .md*: doporučená hodnota je nezaškrtnutá.

**Zamítnuto – nechat otázky samostatně kvůli tomu, že předvybrat nejde:** čtyři kliknutí za sebou nesou čtyři bity rozhodnutí a nejvíc zdržují; s formulací přes odchylku zaškrtávátko funguje i bez výchozího stavu.
