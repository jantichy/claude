# Rozhodnutí – /architect

Soubor drží rozvahu a doklady skillu `/architect`; za běhu skillu se nečte.

### Návrh zapisuje objem, na který se staví, a pojistky proti němu měří

**Rozhodnuto 6. 11. 2026.** Měřítko přiměřenosti (`~/Context/Coding/coding.md`, *Obrana a pojistka úměrně riziku*) se opírá o objem zapsaný „v návrhu projektu“ a `/oponent` i `/consolidate` ho odtamtud čtou, ale šablona `architecture.md` na něj neměla místo a `/architect` se na něj neptal. Pojistky pod hranou tak vznikaly už v návrhu a odebírat je musela až oponentura. Šablona proto dostala sekci *Objem, na který se staví* (odhad, datum, spouštěč revize), *Fáze 4* ji plní z *Nefunkčních požadavků* nebo dotazem a sebe-revize má bod *Přiměřenost*.

**Zamítnuto:** (1) jen kontrola v sebe-revizi bez zápisu – objem by se nikam nezapsal a `/oponent` s `/consolidate` by jeho chybění hlásily dál; (2) objem jako vstup, který píše `/specify` do požadavků – znamenalo by to přepsat `coding.md`, `/oponent` i `/consolidate`, které ho shodně čekají v návrhu, a `/architect` ho z požadavků stejně přebírá, když tam stojí.
