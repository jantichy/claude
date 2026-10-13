---
name: clauding
description: Skill se použije, když uživatel zadá "/clauding" (volitelně s režimem day, week nebo month a s obdobím), nebo se ptá, kolik času strávil v Claude Code – za den, týden, měsíc či celou dobu, kolik hodin denně v průměru, který den byl nejdelší, jak se práce rozkládá do dnů v týdnu a hodin dne. Spočítá to z transcriptů všech sessions, z history.jsonl a z vlastních commitů slitých do jednoho proudu událostí, takže souběžné sessions se nesčítají a čekání na Claudovu práci se počítá. Vypíše součet hodin, průměr na kalendářní i na aktivní den po obdobích a k tomu zajímavosti; dny, pro které transcript chybí, odhadne a označí. Na rozdíl od /invoicing recover nehledá čas k fakturaci pro klienta a nic nedoplňuje do timetrackingu. Nic nezapisuje.
argument-hint: [day|week|month] [období]
allowed-tools: [Bash]
---

# Clauding

## Co skill dělá

Spočítá, kolik času se strávilo v Claude Code, a vypíše to po obdobích. Za každé období součet hodin, průměr na kalendářní den, průměr na aktivní den a počet aktivních dnů; pod tabulkou nejdelší den, nejdelší blok v kuse, nejdelší řadu dnů po sobě, rozložení dnů podle počtu hodin, průměr podle dne v týdnu a rozložení podle hodiny dne.

Tři režimy, liší se jen členěním tabulky:

- **`/clauding month`** – po měsících. **Výchozí**, bez období vypíše celou historii.
- **`/clauding week`** – po týdnech od pondělí do neděle.
- **`/clauding day`** – po dnech.

Za režimem volitelně období česky: „září“, „posledních 14 dní“, „od 1. 9.“, „minulý týden“.

## Co skill nedělá

- **Nehledá čas k fakturaci.** Dohledat nenatrackovanou práci pro klienta je `/invoicing recover`. Oba počítají nad týmž jádrem a týmž pravidlem mezery, ale `recover` jen nad projekty jednoho klienta a s commity jako stopou práce i mimo Clauda.
- **Neměří cenu běhu.** Kolik tokenů stojí běh skillu, počítá `skills/cost.py`; tady jde o čas, ne o spotřebu.
- **Neopakuje vestavěný `/stats`.** Ten ukazuje počty zpráv a sessions ze `stats-cache.json`, čas v něm není.
- **Nic nezapisuje** – ani do projektu, ani do timetrackingu.

## Jak je to postavené uvnitř

| Krok | Kdo | Proč zrovna on |
|---|---|---|
| Výklad režimu a období | vlastní | převod české řeči na data je úsudek |
| Proud událostí a intervaly | `skills/timeline.py` | sdílené jádro – totéž pravidlo počítá i `/invoicing recover` |
| Součty, průměry, odhad a zajímavosti | `clauding.py` | deterministický výpočet nad 3–4 GB transcriptů; model by ho dělal pomaleji a s chybou |
| Výpis | vlastní | odpověď na konkrétní dotaz nad tabulkou |

**Oba skripty jsou implementační detail, ne rozhraní** – jejich jména, parametry i rozdělení práce se smějí změnit bez ohlášení. **Závazná je *Metodika* níž a tvar výstupu:** tabulka se součtem a oběma průměry, zajímavosti a značka odhadu. Změna metodiky se dělá v `timeline.py` a v této sekci zároveň, protože jinak by `/clauding` a `/invoicing recover` odpovídaly na tutéž otázku jinak.

## Metodika

Měří se **čas v Claudovi**, ne čas u klávesnice: čekání, než Claude doběhne, je čas strávený s ním.

1. **Události ze všech sessions se slijí do jednoho proudu** a mezery se měří nad ním, ne v každé session zvlášť. Kdo pracuje v několika oknech naráz, má v každém z nich dlouhé mezery, i když celou dobu pracuje – po sessions by se mu nezapočetlo nic.
2. **Událostí je každý záznam s časem**: prompt, Claudova odpověď, výsledek nástroje, odpověď v dialogu, příkaz harnessu, spuštěný hook, záznam subagenta i workflow. Příkaz `/clear` nebo otevření session je stejný doklad, že se v Claudovi něco dělo, jako prompt. Sessions spuštěné přes `claude -p` se počítají taky.
3. **Mezera do 20 minut mezi dvěma sousedními událostmi se počítá celá, delší je pauza.** Hodnota je společná s `/invoicing recover` a drží ji `timeline.GAP`.
4. **Běh příkazu v popředí se započte do výše svého timeoutu** (bez zadaného dvě minuty). Co je v mezeře do jeho výsledku navíc, čekalo na schválení, a pro to platí bod 3 – jinak by se příkaz, který ráno čekal na schválení od večera, započetl jako noc práce.
5. **Vlastní commit je událost, jen když leží do 20 minut od aktivity v Claudovi.** Commit uprostřed práce ji prodlouží; ruční práce v repozitáři mimo Clauda čas v Claudovi není.
6. **Dny se dělí podle pražského času**, interval přes půlnoc se rozdělí.
7. **Den, pro který chybí transcript, se odhadne.** Úklid starých sessions transcripty maže, `history.jsonl` s prompty ne. Pozná se podle skutečného promptu z `history.jsonl`, jehož session transcript nemá (příkaz harnessu typu `/resume` nebo `exit` transcript nezakládá, takže se nepočítá). Na takový den se spočte týmž pravidlem čas jen z promptů a commitů a vynásobí se **koeficientem**: poměrem plné metody a metody jen z promptů na dnech, kde jsou obě sady dat. Koeficient se počítá při každém běhu, takže se s každým dalším dnem zpřesní a nikdy se nerozejde s daty. Chybí-li jen část sessions dne, platí větší z obou hodnot. Odhadnutý den nese značku `~`; rozložení podle hodiny dne a nejdelší blok se z něj nepočítají, protože prompty samy neříkají, kdy Claude doběhl.
8. **Aktivní den** je den s nenulovým časem. Průměr na kalendářní den dělí počtem dnů období, u běžícího jen do dneška; průměr na aktivní den počtem aktivních dnů.

## Fáze 0 – Příprava

Společný začátek je v `~/.claude/skills/preflight.md`. **Body 1 až 3 se vynechávají**: skill nad projektem neběží, pouští se odkudkoliv a nic nezapisuje, takže kořen, kontrakt ani stav pracovního stromu nepotřebuje. Místo nich jediný předpoklad – existuje `~/.claude/projects/` nebo `~/.claude/history.jsonl`. Nejsou-li ani jedno, není z čeho počítat; řekni to a skonči.

## Fáze 1 – Režim a období

Režim vezmi z argumentu. **Chybí-li a období je zadané**, zvol ho podle jeho délky – do 31 dnů `day`, do půl roku `week`, jinak `month`: tabulka pak má rozumný počet řádků. Bez režimu i období platí `month` přes celou historii.

Období převeď na `--since` a `--until` ve tvaru `YYYY-MM-DD`, obě meze včetně. **Dnešní datum vezmi z `date +%F`**, ne z hlavy – „posledních 14 dní“ i „tento měsíc“ se od něj počítají. Příklady:

- „září“ → `--since 2026-09-01 --until 2026-09-30` (rok nejbližšího minulého nebo běžícího září)
- „posledních 14 dní“ → 13 dní zpátky až dnešek
- „minulý týden“ → pondělí až neděle předchozího týdne
- „od 1. 9.“ → jen `--since`

Nejde-li období jednoznačně určit („minule“, „v létě“ bez roku, kde jsou dva kandidáti), zeptej se jednou větou na jeho meze; netipuj, protože tabulka za špatné období vypadá stejně věrohodně jako za správné.

## Fáze 2 – Výpočet

```sh
python3 ~/.claude/skills/clauding/clauding.py <režim> [--since YYYY-MM-DD] [--until YYYY-MM-DD]
```

Běží desítky sekund – čte všechny transcripty. **Selže-li, zastav se a vypiš chybu i s návratovým kódem**; nepočítej nic ručně místo skriptu. Ruční výpočet nad transcripty je přesně ta cesta, na které se ztrácí souběh sessions a čekání na odpověď v dialogu se počítá jako Claudova práce.

## Časté chyby

Ze session, ve které skill vznikl – každá z nich dala věrohodné, ale špatné číslo:

- **Mezery po sessions místo nad společným proudem.** Práce ve dvou oknech střídavě se pak rozpadne na samé pauzy.
- **Čekání na odpověď v dialogu se započte jako Claudova práce.** Otázka, na kterou uživatel odpoví druhý den, by přidala desítky hodin.
- **Commit se počítá bez ohledu na Clauda.** Staré repozitáře pak posunou začátek historie o roky dřív, než Claude existoval.
- **Den se označí za odhad kvůli příkazu harnessu.** `/resume` nebo `exit` v session, která nic nezapsala, transcript nemá – a jediný takový záznam by udělal odhad z celého dne.

## Fáze 3 – Závěr

Výstup skriptu je hotový Markdown. **Vypiš ho beze změny** – nezaokrouhluj jinak, nepřepočítávej a nevynechávej poznámku o odhadu, protože bez ní vypadá odhad jako změřené číslo. Ptal-li se uživatel na konkrétní věc („kolik jsem byl v Claudovi včera“), odpověz nad tabulkou jednou větou s číslem z ní.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Čas je spočítaný a ověřený skriptem, můžeš se zeptat na jiné období nebo členění.`
- `Čas spočítaný není – brání tomu: <konkrétní seznam>.`
