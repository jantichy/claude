---
name: scenarios
description: Skill se použije, když uživatel zadá "/scenarios", nebo chce z dřívějších konverzací nad projektem vytáhnout uživatelské scénáře, které v nich zazněly nebo ke kterým diskuze mířila, a doplnit je do docs/scenarios.md. Projde uzavřené session, u každé nechá vypsat každou situaci i s doslovnou citací, pak je sám profiltruje proti už zapsaným scénářům a chybějící zapíše do správné kapitoly. Na rozdíl od /cleanup, který vytěžuje právě běžící session a zapisuje dohody, tenhle skill jde zpětně přes hromadu už uzavřených konverzací a zajímají ho jen situace lidí. Návrh nedělá a nerozhoduje – co v konverzaci nezaznělo, si nevymýšlí.
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep, Agent, AskUserQuestion]
---

# Scénáře z konverzací

## Co skill dělá

Projde konverzace nad projektem, které se od minule nevytěžily, a doplní z nich chybějící uživatelské scénáře do `docs/scenarios.md`.

Řeší jedinou vadu, a ta je tichá: **kolo návrhu rozhodne, jak se má systém v nějaké situaci chovat, zapíše to do modelu nebo do katalogu přechodů – a scénář k té situaci nikdo nedopíše.** Scénáře pak vypadají úplně a nejsou, takže se proti nim nedá ověřit, co nový návrh rozbil.

Režimy nemá. **První běh v projektu vezme všechny session, každý další jen ty, které přibyly od posledního běhu.**

## Co skill nedělá

- **Nevytěžuje běžící session.** To dělá `/cleanup` na jejím konci – a dělá to jinak: zapisuje dohody a rozhodnutí do všech souborů projektu. Tenhle skill jde zpětně přes uzavřené konverzace a sahá jen na `scenarios.md`.
- **Nezakládá scénáře z návrhu.** Zakládá je `/specify` ve svém kole, z rozhovoru se zadavatelem. Tenhle skill dopisuje to, co se do nich při tom kole nedostalo.
- **Neaudituje `scenarios.md`.** Rozpory mezi scénáři a modelem, mrtvé odkazy a rozejité počty řeší `/consistency`.
- **Nerozhoduje o produktu.** Narazí-li na situaci, na kterou odpověď není, zapíše scénář i s tím, že pokrytá není – nevymýšlí, jak by se to mělo chovat.

## Jak je to postavené uvnitř

| Krok | Kdo | Proč zrovna on |
|---|---|---|
| Určení rozsahu – které session ještě nebyly | **vlastní** | Čte poslední záznam vytěžení v `done.md` a časové značky transcriptů. Neumí to nikdo. |
| Vytěžení jedné session | subagent, jeden na session | Transcript má megabajty; do hlavní session se nevejde a nemá co dělat v jejím kontextu. |
| Filtrování, ověření a zařazení | **vlastní** | Jádro. Agent pozná, že se o něčem mluvilo; nepozná, jestli to je scénář a jestli pořád platí. |
| Zápis do `scenarios.md` | **vlastní** | Jádro. |
| Kontrola objemu po zápisu | **vlastní**, příkazem | `grep -c '^#### '` před a po. Nula tokenů. |

**Typ subagenta je výchozí, ne `reader`, a je to vědomé.** Agent musí pouštět `jq` nad JSONL a zapsat dlouhý strukturovaný výstup do souboru; `reader` nemá shell a `Explore` nemá `Write`. Hranice se tu tedy nepředstírá – v zadání proto stojí, že do repozitáře projektu nesmí sáhnout, a **stojí to tam jako pokyn, ne jako mechanismus**.

**Vyměnitelné je to, jak se transcript čte a čím se dělí práce.** Závazné je, že agent vrací ke každé situaci **doslovnou citaci s číslem řádku**, že filtrování zůstává v hlavní session a že se do `scenarios.md` nezapíše nic, co neprošlo ověřením proti souboru.

## Rozsah

**Scénář je situace člověka** – jeho problém, cíl nebo potřeba a to, čeho v ní chce dosáhnout. Úplnou definici i formát drží **úvod `docs/scenarios.md` toho projektu**; načti si ho a řiď se jím, neopisuj ho sem. Bez něj nepoznáš, co se do souboru pouští a co ne.

**Vytěžují se konverzace, ne soubory projektu.** Položka, která se do session dostala tím, že ji nějaký nástroj vypsal z `todo.md` nebo ze zásobníku, **není nález** – je to obsah, který v projektu už je. Poznáš ji podle toho, že u ní není nic rozhodnutého a citace vede do výstupu nástroje, ne do řeči člověka.

## Fáze 0 – Příprava

Společný začátek je v `~/.claude/skills/PREFLIGHT.md`. Navíc:

1. **Ověř, že projekt vede `docs/scenarios.md`.** Nevede-li ho, řekni to a skonči – zakládá ho `/specify`, ne tenhle skill.
2. **Přečti jeho úvod celý** (viz *Rozsah*) a **vypiš jeho kapitoly i s čísly řádků**: `grep -n '^\(## \|### \|#### \)' docs/scenarios.md`. Je to zároveň vstupní počet scénářů pro *Fázi 6*.
3. **Mechaniku hledání a čtení transcriptů drží `~/.claude/skills/SESSION.md`.** Načti si ji – zvlášť pasti formátu, bez kterých agenti tiše přijdou o část konverzace.
4. **Změny patří na vlastní větev.** Je-li projekt ve worktree layoutu, založ ji podle `~/.claude/WORKTREE.md` – běh sahá na jeden soubor, ale zapisuje do něj desítky míst naráz.

## Fáze 1 – Které session se vytěžují

**Rozsah se nehádá, zjišťuje se.**

1. **Najdi poslední záznam vytěžení** v `docs/done.md`. Nenajdeš-li žádný, je to první běh a rozsahem jsou **všechny** session projektu.
2. **Vypiš transcripty i s jejich skutečným časovým rozsahem.** Datum změny souboru nestačí – session se dopisuje, takže ukazuje konec, ne začátek. Čti první a poslední časovou značku z obsahu:

   ```
   for f in ~/.claude/projects/<slug>/*.jsonl; do
     echo "$(grep -o '"timestamp":"[^"]*"' "$f" | head -1) $(du -h "$f" | cut -f1) $f"
   done | sort
   ```

3. **Odečti, co se už vytěžilo**, i to, co se vědomě zahodilo – takové rozhodnutí je taky v `done.md` a **neobnovuj ho** bez ptaní.
4. **Vypiš uživateli výsledný seznam** s počtem session a jejich souhrnným objemem, ať vidí rozsah dřív, než se rozešle práce.

**Session tvořená jediným příkazem bez konverzace se vynechá** – pozná se podle velikosti pod ~100 kB nebo podle toho, že je v ní jen `/clear`. Řekni to nahlas i s počtem, ať je poznat, že se nezapomněla.

## Fáze 2 – Podklad pro agenty

Do scratchpadu připrav dva soubory:

- **Zadání** – vezmi `~/.claude/skills/scenarios/brief.md` a doplň do něj to, co je v tomhle projektu jiné: čím se projekt zabývá, kdo v konverzacích vystupuje za aktéry, jak vypadají jeho scénáře. Agent běží bez kontextu téhle session, takže **si musí nést všechno opsané** (`~/.claude/RULES.md`, *Single source of truth*, výjimka pro subagenty).
- **Seznam už zapsaných scénářů** – `grep -n '^#\{2,4\} ' docs/scenarios.md`. Slouží jen k tomu, aby agent u zjevné shody připsal `podobné: <nadpis>`; **filtrovat podle něj nesmí**.

## Fáze 3 – Rozeslání

**Jeden agent na jednu session.** Výchozí model session, **ne nejlevnější** – agent musí poznat, která dohoda později přestala platit, a jeho chybu nepoznáš jinak než tím, že si ten transcript přečteš sám (`~/.claude/RULES.md`, *Model a effort podle úkolu*).

Každému předej: cestu k zadání, cestu k seznamu zapsaných scénářů, **svůj** transcript i s jeho velikostí a datem, jméno výstupního souboru `out-<id>.md` a **vlastní prefix pro pomocné soubory**.

**Prefix není kosmetika.** Agenti sdílejí jeden scratchpad a bez něj si přepíšou mezivýstupy pod stejnými jmény; doloženo opakovaně v jednom běhu, kdy jeden agent chvíli četl cizí transcript a poznal to jen náhodou. Do zadání proto patří i pokyn **ověřit, že v pomocném souboru je opravdu jeho transcript**.

**Návratová hodnota je krátká:** počty po kategoriích, plochý seznam nadpisů s kategorií a hodnotou `podobné`, a témata session. Plný seznam s citacemi zůstává v souboru – do kontextu hlavní session se nevejde a nepotřebuje tam být.

**Souběh agentů má strop.** Narazíš-li na něj, drž si frontu a doplňuj do uvolněných míst; nespouštěj dávku a nečekej, až doběhne celá.

## Fáze 4 – Filtrování a ověření

**Tohle je jádro a nedeleguje se.** Agent dělá úplnost, ty děláš zařazení – a jen tak se jeho chyba pozná levně.

1. **Slož kandidáty ze všech výstupů** a vyber ty, u kterých agent napsal `podobné: nic`. Ostatní přejdi; u nich agent shodu našel a ověří se až tehdy, když nadpis sedí a obsah ne.
2. **Každého kandidáta ověř proti souboru**, ne proti seznamu nadpisů – scénář může být pod jiným jménem. Grepni klíčová slova v `scenarios.md`, a když nic, ještě v `todo.md`, `backlog.md` a `decisions.md`.
3. **Projeď ho definicí z úvodu souboru.** Úkol, přejmenování ani úprava rozhraní scénář nejsou. Pojmenuj u každého člověka a jeho potřebu; nejde-li to, vypadává.
4. **Obrácené rozhodnutí ber vážně.** Vrátil-li agent řádek o tom, že se totéž rozhodlo dvakrát, platí poslední stav a **ověř si ho v dokumentaci**, ne v jeho výtahu.
5. **Vypiš uživateli, co ti zbylo** – po kapitolách, jednou větou u každého. Teprve pak zapisuj.

## Fáze 5 – Zápis

**Zapisuj podle formátu, který drží úvod `scenarios.md`**, a do té kapitoly a části (běžné situace proti okrajovým případům), kam scénář patří.

- **Nezakládej kapitolu bez ptaní.** Nová kapitola je zásah do struktury dokumentu, ne doplnění položky.
- **Situaci, kterou systém nepokrývá, zapiš i tak** – a doplň ji do závěrečné kapitoly *Co pokryté není*, ať se dá dohledat z obou stran.
- **Zamítnutou situaci nezapisuj jako scénář**, pokud o zamítnutí nemáš doklad v `decisions.md`; je to nález pro uživatele, ne hotové rozhodnutí.

**Nikdy neřež podle nadpisů.** Vkládá se mezi existující scénáře a jediné riziko běhu je, že se s novým textem odnese kus starého. Řez „od nadpisu k nejbližšímu nadpisu“ už v tomhle souboru jednou snědl třetinu jeho obsahu a testy zůstaly zelené (`~/.claude/RULES.md`, *Mazání ověř diffem, ne grepem*).

## Fáze 6 – Kontrola objemu

**Spočítej scénáře před zásahem a po něm** a ověř, že rozdíl sedí s počtem zapsaných:

```
grep -c '^#### ' docs/scenarios.md
```

Nesedí-li, **zastav se a najdi proč** – neopravuj naslepo. Pak pusť příkazy z *Kontraktu příkazů* projektu a načti změněná místa zpátky (`~/.claude/RULES.md`, *Co jsi vygeneroval, přečti zpátky*).

**Zapiš záznam běhu do `docs/done.md`** – datum, počet vytěžených session a jejich rozsah, počet přibylých scénářů a co se vědomě nevytěžilo. Bez něj nemá příští běh podle čeho určit rozsah a projede všechno znovu.

## Fáze 7 – Závěr

## Scénáře vytěženy

- **Rozsah:** <N> session, <od>–<do>, <objem>; vynecháno <N> prázdných
- **Nalezeno:** <N> situací, z toho <N> bez existujícího protějšku
- **Zapsáno:** <N> scénářů – <kapitola>: <N>, …
- **Nezapsáno:** <N> – <důvod po skupinách>

**Panel:** <N> agentů, <model>, z toho ověřovatelé: 0

**Ověřeno**
- Počet scénářů: <před> → <po>, přírůstek sedí / nesedí
- Kontrakt: <výstup a návratový kód>

**Nevytěženo**
- <co a proč, nebo „nic">

Vypisuj to jako Markdown, ne jako blok kódu, a řádky nezalamuj natvrdo.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Scénáře jsou vytěžené a zapsané, můžeš pokračovat dalším kolem návrhu.`
- `Scénáře vytěžené nejsou – brání tomu: <konkrétní seznam>.`

## Časté chyby

- **Vezme se výstup nástroje za nález.** Session, která začíná `/next`, obsahuje vypsanou frontu z `todo.md`; agent ji vypíše jako desítky „naznačených situací“. Poznáš to podle toho, že u všech stojí `rozhodnuto: nic`.
- **Filtrování se deleguje.** Agent, který má rozhodnout, jestli je jeho nález nový, odpoví ano – nemá totiž jak vědět, že je táž věc v souboru pod jiným jménem.
- **Rozsah se určí podle data změny souboru.** Transcript se dopisuje, takže datum ukazuje konec session, ne její začátek; běh pak minul konverzaci, která začala před posledním vytěžením a skončila po něm.
- **Zapíše se scénář bez člověka.** „Zavést sloupec“ a „přidat tlačítko“ scénáře nejsou; jsou to nanejvýš důsledky něčí nenaplněné potřeby a patří do `todo.md`.
- **Zapomene se záznam do `done.md`.** Příští běh pak nemá odkud vědět, kam se došlo, a projede tytéž konverzace znovu.
