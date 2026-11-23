# Rozhodnutí – /project

Rozvaha a doklady ke skillu `/project`; za běhu skillu se nečte.

### Připnuté akce v CI se zakládají spolu s Dependabotem s povinným `cooldown`

**Rozhodnuto 15. 9. 2026.** Pohyblivou značku akce může její majitel kdykoliv přesměrovat a doložené útoky na dodavatelský řetěz (trivy-action, kics-github-action) šly přesně touhle cestou; proto se akce připínají na commit. Připnutí bez Dependabota by ale zmrazilo i chyby, takže se zakládá spolu s ním.

`cooldown` je povinný, protože semgrep pravidlem `dependabot-missing-cooldown` shodí CI konfiguraci, která ho nemá – doloženo týž den.

Proč se při zavádění Dependabota prochází i `## Review` v `CLAUDE.md` a registr obcházení: zamítnutí nepřipnutých akcí z 13. 9. 2026, které stálo na argumentu „bez Dependabota to zastará“, přežilo v obou místech i poté, co se Dependabot zavedl.

### Dvojvolby se ptají naráz, zaškrtnutá volba zapíná

**Rozhodnuto 23. 11. 2026.** Layout na disku, umístění dokumentace, autocommit a paměťová politika se ptaly čtyřmi samostatnými otázkami, každá s jedinou volbou ano/ne. Teď je to jedna otázka s `multiSelect` hned po gitu (krok 3, *Přepínače*) a kroky 4, 5, 9 a 10 ji jen provádějí; v operativním projektu totéž pro git a autocommit.

**Každá volba zapíná, co jmenuje** (*Worktree layout*, *Podadresář docs místo kořene*, *Zapnout autocommit*, *MDčka místo Memory*), i když to znamená zaškrtávat doporučené hodnoty. `AskUserQuestion` volbu předvybrat neumí, a zaškrtnutí má být vědomé rozhodnutí. U existujícího projektu se proto potvrzuje, co by výběr proti dnešku vypnul.

**Zamítnuto – formulovat volby jako odchylku od výchozího stavu**, aby prázdný výběr byl vždy bezpečný (*Povolit trvalou Memory* místo *MDčka místo Memory*): uživatel to odmítl. Princip „nezaškrtnout je vždy bezpečné“ neplatí univerzálně a schovává rozhodnutí do výchozího stavu, o kterém se nepřemýšlí.

**Zamítnuto – nechat otázky samostatně kvůli tomu, že předvybrat nejde:** čtyři kliknutí za sebou nesou čtyři bity rozhodnutí a nejvíc zdržují.
