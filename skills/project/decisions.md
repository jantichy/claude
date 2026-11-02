# Rozhodnutí – /project

Rozvaha a doklady ke skillu `/project`; za běhu skillu se nečte.

### Připnuté akce v CI se zakládají spolu s Dependabotem s povinným `cooldown`

**Rozhodnuto 15. 9. 2026.** Pohyblivou značku akce může její majitel kdykoliv přesměrovat a doložené útoky na dodavatelský řetěz (trivy-action, kics-github-action) šly přesně touhle cestou; proto se akce připínají na commit. Připnutí bez Dependabota by ale zmrazilo i chyby, takže se zakládá spolu s ním.

`cooldown` je povinný, protože semgrep pravidlem `dependabot-missing-cooldown` shodí CI konfiguraci, která ho nemá – doloženo týž den.

Proč se při zavádění Dependabota prochází i `## Review` v `CLAUDE.md` a registr obcházení: zamítnutí nepřipnutých akcí z 13. 9. 2026, které stálo na argumentu „bez Dependabota to zastará“, přežilo v obou místech i poté, co se Dependabot zavedl.
