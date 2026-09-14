# Kontextový slovník

Jak se staví `.transcript-glossary.md` – seznam jmen, značek a termínů, který se podstrkuje whisperu, aby je nekomolil. Vytažené ze `SKILL.md`, protože se to čte jen v kroku 3 průvodce; naměřené hodnoty k účinnosti drží [`internals.md`](internals.md).

- [Jak se slovník sestavuje](#jak-se-slovník-sestavuje)
- [Šablona souboru](#šablona-souboru)

## Jak se slovník sestavuje

**Tohle je nejcennější krok celého skillu.** Whisper dostane seznam vlastních jmen a termínů předem (`--prompt`) a přestane je komolit už při rozpoznávání. Oprava dodatečně je principiálně slabší, protože vymyšlená oprava vypadá stejně věrohodně jako správná.

Návrhy sestav ze čtyř zdrojů:

1. **volný popis v promptu** – jména, firmy a produkty, které uživatel sám napsal,
2. **kontext projektu**, ve kterém běžíš – `CLAUDE.md`, `docs/`, `README.md`, názvy v `content/`,
3. **předchozí komunikace v téhle session**,
4. **[`mishearings.md`](mishearings.md)** – zkomoleniny, které whisper dělá soustavně u každého, kdo mluví o daném oboru. Vezmi jen oddíl odpovídající oboru a jazyku nahrávky. **Do promptu jde správný tvar, nikdy zkomolenina** – tu by se model naučil.

Rozděl je do **tří domén** a nabídni je jako jednu otázku s `multiSelect: true`. Konkrétní termíny vypiš v `description` každé možnosti, ať uživatel vidí, co odsouhlasuje:

| Pořadí | Label | Co do ní patří |
|---|---|---|
| 1. | `Jména lidí` | účastníci, kolegové, zmínění lidé |
| 2. | `Značky, produkty, weby` | firmy, nástroje, domény, názvy prostorů |
| 3. | `Odborné termíny` | žargon oboru, interní pojmy, zkratky |

Volbu „Other“ doplní `AskUserQuestion` samo – tudy uživatel dopíše, co jsi netrefil.

Prázdnou skupinu vůbec nenabízej. Když nemáš návrh ani do jedné, otázku přeskoč a zeptej se rovnou na vlastní termíny.

#### Rešerši dělej naplno, do promptu vybírej

Tyhle dvě věci se pletou, a je to rozdíl mezi dobrým a špatným výsledkem.

**Rešerši dělej naplno.** Vytěž ze zdrojů úplně všechno – klidně stovky jmen, názvů, zkratek a interních pojmů. Nic nezahazuj.

**Do `WHISPER_PROMPT` vyber to, co v nahrávce opravdu zazní**, seřazené podle důležitosti. Vybírej podle dvou věcí naráz: **jak často to padne** a **jak snadno se to komolí**. Obecná slova, která model umí sám, do promptu nepatří – neuškodí, ale místo zabírají.

**Počet položek pravidlem omezený není.** Dřív tu stálo „nejvýš deset“ s odůvodněním, že delší seznam ředí účinek, a **měření to vyvrátilo** (tabulka sedmi běhů je v [`internals.md`](internals.md)). Platí jedině **technický strop whisperu: `n_text_ctx/2`, tedy 224 tokenů.** `n_text_ctx` je 448 u turba i u `large-v3` – ověřeno výpisem whisperu při načtení obou modelů, takže strop je pro obě volby stejný. Změřeno na češtině: jednadvacet termínů (306 znaků) zabere 123 tokenů, takže se vejde **zhruba 38 termínů**.

**Přeteče-li prompt, whisper zahodí jeho začátek**, ne konec – v kódu `prompt_past0.assign(… + (n - n_tokens), … + n)`, tedy „use only the last N tokens“. Řazení podle důležitosti od nejdůležitějšího tedy pomůže jen tehdy, když se slovník do stropu vejde; při přetečení by usekl přesně to, na čem záleží. **Drž se proto bezpečně pod hranicí** místo spoléhání na pořadí.

Ořez je v našem řetězu **tichý**: whisper na něj varuje, ale `transcribe.sh` běží s `-np`, které výpis potlačí.

To je strop daný modelem, ne doporučení: **složení celého seznamu rozhoduje víc než jeho délka a nedá se odhadnout dopředu.** Dva jednadvacetipoložkové slovníky nad touž nahrávkou daly 5/5 a 0/5.

Vybrané položky slep čárkami do jednoho řetězce a předej jako `WHISPER_PROMPT`.

#### Zbytek rešerše si ulož

Všechno ostatní, co jsi našel, zapiš do `<workdir>/.transcript-glossary.md`:

```markdown
# Kontextový slovník – <název nahrávky>

## Jazyk
cs (detekováno v kroku 1, jistota 0,99)

## Mluvčí
(doplní krok 8, když se rozlišují)

## V promptu whisperu
Nazev.cz, Značka, interní pojem, místní jméno, …

## Jména lidí
Jana Nováková, Petr Svoboda, …

## Značky, produkty, weby, místa
Nazev.cz, Značka, s. r. o., …

## Odborné a interní termíny
zkratky oboru, interní pojmy, názvy rolí a útvarů, …

## Zdroje
prompt / docs/structure.md / session
```

Tenhle soubor je vstup pro čištění v kroku 9. **Whisperu dáváš výběr, tobě při čištění to nestačí** – tam potřebuješ úplný kontext, abys poznal, co je zkomolenina a co interní žargon. Bez něj hádáš.
