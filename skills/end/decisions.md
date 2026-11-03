# Rozhodnutí – /end

Rozvaha, měření a historie skillu `/end`. Za běhu se nečte. Starší rozhodnutí o skillu leží v `docs/decisions.md` (kapitoly od *Skill `/end` poběží v subagentovi* po *První ostrý běh zúženého `/end`*).

### `order.py` vznikl, protože ruční srovnání pořadí nevydrželo

**Rozhodnuto 28. 9. 2026.** Pořadí datovaných záznamů v `done.md` a `decisions.md` se rozpadlo počtvrté; ruční srovnání se dělalo třikrát a nevydrželo, protože do těch sekcí zapisují skilly samy a každý se řídí tím, co v souboru zrovna vidí. Skript je sdílený s `/consistency` stejně jako `links.py`, protože skript uvnitř skillu by z cizího skillu volat nesměl.

### Zrychlení: méně kol, kratší závěr, evidence ověřená skriptem

**Rozhodnuto 2. 11. 2026.** Uživateli běh trval 1 až 3 minuty a závěrečný přehled nikdy nečetl.

**Měření** (30 běhů od 25. 10. 2026, rozpis osmi z jednoho projektu): běh bez dotazů 45 až 120 s, z toho 60 až 80 % čas modelu, nástroje 5 až 40 s, `extract.py` 0,07 s. Běh měl 4 až 12 kol a každé stálo 5 až 15 s, protože model nad velkým kontextem končící session znovu prochází a přemýšlí; jen úvodní přemýšlení nad 36 kB `SKILL.md` bralo kolem 15 s. Medián ceny po pásmech velikosti transcriptu 4,84 (600–1200 kB) a 10,28 (nad 1200 kB) jednotky, medián 2 minuty. Delší běhy čekaly na odpověď uživatele nebo souhlas s příkazem. Ve dvou z osmi běhů selhalo první volání `links.py` na špatné argumenty.

**Co se změnilo:**

- **`prepare.py`** dělá jedním voláním, co dřív bralo 2 až 4 kola: transcript, základ session, git, inventuru, očištěný transcript.
- **`finish.py`** dělá jedním voláním kontrolu evidence, odkazů a pořadí; commit a push jdou v témže příkazu, zprávu commitu nese soubor ve scratchpadu místo heredocu.
- **Evidence promptů je kompaktní soubor stavů s úseky** (`1-4 bez zápisu`) místo tabulky, kterou model opisoval celou, a **skript ji ověřuje proti transcriptu v okamžiku závěru**, tedy i s odpověďmi z dialogů úklidu. Dřív počet řádků porovnával model.
- **Závěr ukazuje jen odchylky.** Uživatel rozhodl po skupinách: technické řádky (pokrytí, odkazy, kontrakt, git) jen při selhání; zápisy jednou větou; výsledky fronty, mimo rozsah a odvolané závěry vůbec (osud nese `done.md`); meze jen mimořádné. Nadpis `## Úklid dokončen` zůstal, protože podle něj `cost.py` pozná konec běhu.
- **`SKILL.md` z 36 kB na 25 kB** – ven šla historie, měření a rozbor návrhu podle nové normy skillů.

**Zamítnuto – snížit effort nebo přemýšlení:** hledání nevypořádaných témat stojí na úsudku a hlavička skillu effort nastavit neumí ověřeně. **Zamítnuto – nečíst inventuru ani evidenci:** stojí skoro nic a jsou jádrem záruky úplnosti.

**Odhad:** běh bez dotazů z kolem 90 s na kolem 50 až 60 s. **Ověřit** `skills/cost.py end --since 2026-11-03` po několika ostrých bězích proti mediánům výš; teprve pak se slučoval `/break` – sloučený je od 3. 11. 2026 (`docs/decisions.md`).
