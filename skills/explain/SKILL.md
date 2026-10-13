---
name: explain
description: Skill se použije, když uživatel zadá "/explain" (volitelně s tím, co vysvětlit), nebo napíše, že nerozumí tomu, co mu Claude právě řekl či na co se ptá – "nechápu", "nerozumím", "vysvětli mi to", "co je varianta B?", "z jakého náhledu?", "co znamená …?". Typicky uprostřed vypořádávání nálezů z /review, /consistency nebo /oponent, kdy otázka odkazovala na věc, kterou uživatel neviděl, používala nevysvětlenou zkratku nebo nabízela varianty bez popisu. Vysvětlí to znovu v jednom až dvou odstavcích: čeho se věc týká, jak je to dnes a proč to nestačí, to všechno na jednom konkrétním příběhu z domény projektu, u každé varianty její důsledek v tom příběhu, a doporučení. Pak položí čekající otázku znovu. Na rozdíl od /oponent, /review a /consistency nic nového nehledá ani nerozhoduje, jen zpřístupní to, co už padlo.
argument-hint: [co vysvětlit]
allowed-tools: [Read, Grep, Glob, AskUserQuestion]
---

# Explain

## Co skill dělá

Krátká náhrada věty „nerozumím, mluvíš na mě moc zkratkovitě“. Vezme poslední otázku nebo tvrzení – případně tu věc, kterou uživatel jmenuje v argumentu (`/explain variantu B`, `/explain ten rozpor`) – a podá ji znovu tak, aby se jí dalo rozumět **bez čehokoliv, co uživatel neviděl**: na jednom konkrétním příběhu, s dnešním stavem, s variantami přehranými na tom příběhu a s doporučením. Čekala-li otázka, položí ji na konci znovu.

**Cíl je srozumitelnost, ne délka.** Jeden až dva odstavce; vysvětlení, které je delší než to, co vysvětluje, většinou jen přesunulo problém jinam.

Režimy nemá. Bez argumentu vysvětluje poslední otázku nebo tvrzení z předchozí odpovědi.

## Co skill nedělá

- **Nehledá nové nálezy ani nepřeposuzuje staré.** To je `/oponent`, `/review` a `/consistency`; tenhle skill jen zpřístupní otázku, kterou položily, a jejich frontu pak nechá pokračovat.
- **Nerozhoduje za uživatele.** Doporučí, ale otázku vrátí jemu.
- **Nezapisuje.** Vyjde-li při vysvětlování najevo, že bylo dřív něco řečeno špatně, opraví to v odpovědi; zápis do souborů dělá práce, ke které se po vysvětlení vrací.

## Fáze 0 – Příprava

`~/.claude/skills/preflight.md` se **nenačítá** – skill nepracuje nad kódem projektu, ale nad konverzací, a kořen, kontrakt ani stav pracovního stromu nepotřebuje. Předpoklad je jediný: **víš, co se vysvětluje.** Určí to argument, jinak poslední otázka nebo tvrzení z předchozí odpovědi. Nejde-li to poznat (dvě otázky naráz, argument nesedí na nic z konverzace), zeptej se jednou větou, co z toho – nehádej.

## Fáze 1 – Co uživateli chybí

Přečti původní text **očima člověka, který vidí jen viditelný text odpovědí** – ne myšlení, ne výstupy nástrojů, ne soubory, které jsi otevřel. Najdi v něm každé místo, které předpokládá něco, co uživatel nemá:

| Co hledat | Příklad |
|---|---|
| Odkaz na nenapsané | „rozpor z kapitoly 13“, „nález 7“, „z náhledu“, „upravená věta“, „§241 bod 3“ |
| Zkratka nebo identifikátor bez vysvětlení | `BEM`, `::part`, `ops_`, `overrideVat`, `CARD_UNDOCUMENTED`, „tick“ |
| Slovo ve významu, který zná jen dokumentace | „mail se *nabízí*“ – míněna nabídka adminovi v hlášce, ne účastníkovi |
| Role nebo věc se dvěma možnými čteními | „Správce“ – pořadatele, nebo provozovatele? |
| Chybějící dnešní stav | ptá se, co dělat s neověřeným DIČ, ale neřekl, že widget DIČ neověřuje – uživatel si myslí, že takový případ nenastane |
| Varianta popsaná jen mechanikou | „otevřít ruční cesty nad PENDING“ – bez toho, co se pak stane zákazníkovi |
| Vyřazená varianta bez důvodu | nejzřejmější kandidát „cache“ mezi volbami chybí a nikdo neřekl proč |
| Skrytá domněnka | „ostatní databáze vypadly“ – kvůli sedmidennímu oknu, které nikdo neodsouhlasil |

**Fakta si ověř u zdroje, ne v paměti.** Odkazoval-li původní text na soubor, nález nebo rozhodnutí, otevři ho (`Read`, `Grep`) – vysvětlení se často opírá právě o detail, který byl v kontextu jen zkrácený. Ukáže-li se, že původní tvrzení bylo nadsazené nebo mylné, **řekni to jednou větou** jako součást vysvětlení; dvakrát se to v praxi stalo a přiznání pomohlo víc než obhajoba.

## Fáze 2 – Vysvětlení

**Piš ho do textu odpovědi, nikdy jen do myšlení.** Uživatel myšlení nevidí; „vysvětlil jsem“ bez napsaného textu je pro něj prázdná odpověď (`~/.claude/standards/rules.md`, *Ptej se postupně, ne všechno najednou*). V devíti z patnácti případů, ze kterých skill vznikl, se stalo právě tohle.

Stavba – v tomhle pořadí, ale jako souvislý text, ne jako formulář s nadpisy:

1. **Čeho se to týká** – jednou větou, slovy domény, ne jménem souboru nebo pole.
2. **Jeden konkrétní příběh.** Postavy se jmény, datum, částka, co kdo udělal: *„Akademie pořádá školení GA4 21. 9. Jan si ho objednal, Petra na něm přednáší jako host. Akademie akci zruší…“* Vezmi ho z domény projektu; je-li vymyšlený, nemusíš to říkat, ale musí být realistický. **Jeden příběh pro celé vysvětlení** – každá varianta se přehraje na něm, ne na novém.
3. **Jak je to dnes** v tom příběhu a **proč to nestačí** – kde přesně se to v příběhu pokazí nebo rozejde.
4. **Varianty přehrané na příběhu** – u každé, co se v něm stane (Jan dostane mail, Petra ne; zákazník zaplatí o 2 100 Kč víc), a jednou větou, proč ji nechtít, případně v čem je naopak lepší. Varianty mohou být krátký seznam, je-li jich víc než dvě.
5. **Doporučení** a jeho důvod, opřený o příběh.

**Co ve výstupu nesmí být:**

- odkaz na cokoliv, co uživatel neviděl – buď to řekni obsahem, nebo odkaz vynech;
- zkratka, identifikátor nebo interní značka bez vysvětlení – kód smí zůstat, jen když vedle něj stojí, co znamená (`overrideVat`, tedy ruční přepsání DPH adminem);
- termín, který se v oboru nepoužívá (`~/.claude/standards/ptydepe.md`) – nahraď ho prostým popisem;
- obecná věta tam, kde jde říct konkrétní případ.

**Nevysvětluj, co uživatel zná.** Mezera je v tom, co předpokládal původní text, ne v základech oboru – kdo se ptá „co je BEM“, nepotřebuje vysvětlovat CSS.

## Časté chyby

Ze skutečných případů, ze kterých skill vznikl:

- **Vysvětlení zůstane v myšlení a odpověď je jen dialog.** Uživatel pak cituje souhrn „vysvětlil jsem…“ a ptá se, kde to je.
- **Otázka se po „nerozumím“ jen přeformuluje** – nová volba v dialogu, ale pořád bez příběhu a bez dnešního stavu. Uživatel pak vybírá podle doporučení, ne podle porozumění.
- **Varianty se vysvětlí, ale každá na jiném příkladu.** Nedají se porovnat; srovnatelné jsou jen na témže příběhu.
- **Obhajuje se původní tvrzení**, i když při ověření vyšlo, že bylo nadsazené.

## Fáze 3 – Závěr

**Čekala-li otázka, polož ji hned za vysvětlením znovu přes `AskUserQuestion`.** Tentokrát mířenou na situaci z příběhu (*„Má se adminovi po odebrání Petry ze zrušené akce ukázat odkaz na mail stejně jako u Jana?“*) a s variantami, jejichž `label` i `description` nepoužívají nic, co vysvětlení nezavedlo. Výběr z variant je pro uživatele pohodlnější než psát odpověď, a teď už ví, na co se ho ptáš. Nečekala-li žádná otázka, vrať se k práci, u které jste byli.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím – stojí-li za vysvětlením dialog, řekni ji těsně před ním:

- `Vysvětlení je hotové a ověřené proti <zdroji>, pokračujeme <otázkou níž / tím, u čeho jsme byli>.`
- `Vysvětlení hotové není – brání tomu: <co nevím a kde by se to dalo zjistit>.`
