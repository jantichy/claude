# Rozhodnutí – /serviceaccount

Rozvaha a doklady ke skillu `/serviceaccount`; za běhu skillu se nečte.

### Klíče se do ukládacího příkazu vypisují jmenovitě, ne maskou

**Rozhodnuto 18. 9. 2026.** Při prvním ostrém běhu zpracoval ukládací příkaz všechno, co ve složce stažených souborů odpovídalo masce, a do jedné položky v Keychainu se tak sešly čtyři klíče, z nichž tři patřily jiným účtům. Proto skill do příkazu vypisuje jmenovitě jen účty, které se právě zakládají.
