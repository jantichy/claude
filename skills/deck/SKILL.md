---
name: deck
description: Skill se použije, když uživatel zadá "/deck" (volitelně s přednáškou, školením, webinářem nebo akcí), nebo chce napsat, upravit či sestavit prezentaci k přednášce, školení nebo webináři v ~/Projects/Speaking – připravit slajdy z popisu přednášky, školení či webináře, didaktiky a látky ve znalostní bázi, předělat existující slajdy, opravit přetékající text nebo vyrobit .pptx v autorově šabloně. Napíše nebo upraví zdroj Prezentace.md, sestaví z něj PowerPoint nad šablonou, vykreslí náhledy a zkontroluje je. Pro prezentace v ~/Projects/Speaking má přednost před obecnou prací se soubory .pptx. Látku si nevymýšlí – co v podkladech chybí, jde nejdřív přes /learn. Na rozdíl od /compose nepíše souvislý text autorovým hlasem a na rozdíl od /proofread nedělá korekturu hotového textu; prezentaci, jejímž originálem je Google Slides, nestaví a do hotového .pptx nesahá.
argument-hint: [přednáška, školení, webinář nebo akce]
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion]
---

# Deck

## Co skill dělá

Napíše nebo upraví prezentaci přednášky, školení, webináře či akce v `~/Projects/Speaking` a dotáhne ji do hotového `.pptx`. Zdrojem pravdy je `Prezentace.md` vedle popisu přednášky, školení, webináře nebo akce: skill ho napíše z jejich popisu, didaktiky tématu a látky z domén, sestaví z něj PowerPoint nad autorovou šablonou, vykreslí náhledy a zkontroluje je proti pravidlům slajdů. Co na náhledu nesedí, opraví ve zdroji a sestaví znovu.

Režimy nemá. Jestli se prezentace píše nově, nebo upravuje, pozná podle toho, jestli `Prezentace.md` už existuje.

## Co skill nedělá

- **Nevymýšlí látku.** Co v doménách chybí, jde nejdřív přes `/learn` do `~/Context` a na slajd až odtamtud.
- **Nepíše souvislý text autorovým hlasem.** Článek, anotaci nebo pozvánku píše `/compose`.
- **Nedělá korekturu hotového textu.** Na tu je `/proofread`; tenhle skill drží sazbu jen na slajdech, které sám píše.
- **Nestaví v Google Slides.** Postup pro ně drží `~/Context/Design/google-slides.md`, ne skill.
- **Nepřepisuje nahrávky.** Přepis akce dělá `/transcript`.
- **Nerozhoduje, co přednáška, školení nebo webinář obsahuje.** Výběr modulů, cílovka a délka stojí v jejich popisu; skill z nich prezentaci staví, ne je mění.

## Jak je to postavené uvnitř

| Krok | Kdo | Proč zrovna on |
|---|---|---|
| Psaní a úprava `Prezentace.md` | vlastní | výběr z látky a didaktiky pro jedno publikum neumí nikdo jiný |
| Sestavení `.pptx` | `build.py` v adresáři skillu | klonuje vzorové slajdy šablony, takže okraje, písma a odrážky sedí se šablonou |
| Náhled | `preview.sh` v adresáři skillu | sestaví prezentaci, vykreslí ji v LibreOffice s písmy šablony a složí přehled |
| Kontrola náhledů | vlastní | posuzuje slajd proti `~/Context/Design/slides.md`, což skript nezměří |

`document-skills:pptx` se nepoužije: neklonuje vzorové slajdy šablony a nezná její písma.

**Skripty jsou implementační detail**, smí se vyměnit kdykoliv. Závazné je: formát zdroje v `format.md`, šablona v `~/Context/Brand/template.pptx`, výstup `<adresář zdroje>.pptx` vedle zdroje a to, že prezentace se dá kdykoliv znovu sestavit ze zdroje.

## Hranice

Platí ve všech fázích a pod tlakem termínu taky:

- **Do `.pptx` se nesahá, ani ve spěchu a ani na výslovné „oprav to rovnou v `.pptx`“.** Každá úprava jde do `Prezentace.md` a prezentace se sestaví znovu – ruční zásah do `.pptx` příští sestavení tiše smaže. Spěch na tom nic nemění: sestavení trvá vteřiny a je rychlejší než rozbalovat a přebalovat soubor. **Spěch smí zkrátit jen kontrolu náhledů** – pak ji přeskoč, řekni to a skonči nehotovým verdiktem. Uživateli řekni jednou větou, že oprava šla přes zdroj, protože je to rychlejší a nic se neztratí.
- **Existující `.pptx` bez `Prezentace.md` vedle se nepřepisuje.** Je to originál odjinud, ne výstup skillu; sestavení by ho zničilo. Zeptej se, co s ním.
- **Látka se nevymýšlí.** Údaj, který v podkladech není, nepíšeš jako fakt: buď ho zapíše `/learn`, nebo zůstane v poznámkách jako `DOHLEDAT:`. Věta bez opory v podkladech na slajdu je chyba, kterou publikum nepozná a řečník ji odříká.
- **Prezentace s originálem v Google Slides se nestaví.** Popis akce to říká řádkem o originálu; sestavený `.pptx` by se rozešel s tím, co se opravdu promítá.

## Fáze 0 – Příprava

Společný začátek je v `~/.claude/skills/preflight.md`. Odchylky:

1. **Kořenem je `~/Projects/Speaking`**, i když session stojí jinde – přednášky, školení, webináře i akce leží tam. Jejich pojmenování drží jeho `CLAUDE.md`.
2. **Kontrola závislostí:** `uv`, `soffice`, `pdftoppm` a `magick` (`command -v`) a šablona `~/Context/Brand/template.pptx`. Chybí-li náhledové nástroje, sestavit jde, ale kontrola náhledů odpadá – řekni to a zapiš do závěru jako nezkontrolované. Chybí-li `uv` nebo šablona, skonči.
3. **Načti domény:** `~/Context/Design/slides.md`, `~/Context/Design/design.md`, `~/Context/Brand/visual.md`, `~/Context/Text/typography.md`, `~/Context/Training/training.md`, a jde-li v poznámkách o souvislý text, `~/Context/Text/text.md`. Didaktiku tématu načti až ve *Fázi 2*, kdy je jasné, o jaké téma jde.
4. **Načti `format.md`** z adresáře skillu – bez něj nevíš, co který typ slajdu nese.

## Fáze 1 – Přednáška, školení, webinář nebo akce

Najdi v `~/Projects/Speaking` adresář podle argumentu. Bez argumentu, nebo sedí-li víc adresářů, se zeptej přes `AskUserQuestion` s přednáškami, školeními, webináři a akcemi jako variantami.

- **Přednáška, školení nebo webinář** má `<název>.md` a `Prezentace.md` je jeho hlavní prezentace.
- **Akce** má `<akce>.md`. Vlastní `Prezentace.md` dostane, jen když se pro ni generuje vlastní prezentace; jinak se promítá prezentace přednášky, školení nebo webináře, pod kterou akce leží. Říká-li popis akce, že originálem je Google Slides, skonči podle *Hranic*.

Existuje-li `Prezentace.md`, jde o úpravu: přečti ho celý a měň jen to, co zadání žádá. Neexistuje-li, píše se nová. Leží-li v adresáři `.pptx` bez `Prezentace.md`, zastav se podle *Hranic*.

## Fáze 2 – Podklady

Přečti popis přednášky, školení nebo webináře (u akce i popis akce s odchylkami od něj). Z něj plyne cílovka, délka a moduly v pořadí. Pak načti didaktiku tématu `~/Context/Training/<téma>.md` a látku z domén, na kterou moduly vedou.

**Chybí-li látka k modulu**, nepiš ho. Vypiš, co chybí, a navrhni `/learn` se zdrojem, je-li nějaký známý. Zbytek prezentace psát smíš, chybějící modul zůstane jako mezislajd s poznámkou `DOHLEDAT:`.

## Fáze 3 – Zdroj prezentace

Piš nebo uprav `Prezentace.md` podle `format.md` a pravidel `~/Context/Design/slides.md` – rozsah a tempo z délky přednášky, školení nebo webináře, nadpis jako tvrzení, jedna myšlenka na slajd. Co řečník řekne, patří do poznámek `>`, ne na slajd. Česká sazba podle `typography.md` platí i na slajdu.

**Kresba** – schéma, které se z typů slajdů poskládat nedá – vzniká jako `<typ>.py` vedle zdroje podle `format.md`, *Kresba jedné prezentace*. Napřed zkus vestavěný typ; kresba je kód, který se s každou úpravou šablony musí ověřit znovu.

## Fáze 4 – Sestavení a náhled

```bash
zsh ~/.claude/skills/deck/preview.sh "<adresář>/Prezentace.md"
```

Vypíše adresář s náhledy a počet slajdů. Skončí-li chybou, oprav zdroj podle hlášky (typ slajdu, počet bloků, chybějící obrázek) a pusť znovu.

## Fáze 5 – Kontrola náhledů

Prohlédni přehled `sheet.png`, pak jednotlivé slajdy `p-*.png` tam, kde je na přehledu něco podezřelého, a u nově napsaných slajdů vždycky. Na každém hledej:

- **přetékání** – text, který se dotkne okraje karty nebo vyjede z plochy,
- **kontrast a čitelnost** podle `~/Context/Design/design.md`,
- **test odolnosti** – obě otázky z `~/Context/Design/slides.md`, *Test odolnosti*,
- body *Checklistu před odevzdáním* tamtéž, které jdou na náhledu posoudit.

Nález oprav ve `Prezentace.md` a vrať se do *Fáze 4*. Kontrola končí, až poslední kolo nenajde nic.

Pak sestav výsledek vedle zdroje:

```bash
uv run ~/.claude/skills/deck/build.py "<adresář>/Prezentace.md"
```

Vypíše cestu k `<adresář>.pptx`. Commit se řídí pravidly projektu.

## Časté chyby

- **Spěšná oprava přímo v `.pptx`.** Na „za deset minut začínám, oprav to rovnou v `.pptx`“ se nabízí `.pptx` rozbalit, přepsat text v XML a zabalit zpátky – vypadá to jako nejrychlejší cesta. Zdroj vedle přitom zůstane s chybou a příští sestavení ji do prezentace vrátí. Správně je opravit `Prezentace.md` a sestavit znovu, i ve spěchu (*Hranice*).
- **„Opraveno“ podle toho, že se soubor dá otevřít.** Platný ZIP a nalezený text ještě neznamenají, že slajd vypadá dobře. Bez prohlédnutého náhledu je to nehotový verdikt, i když šlo o dvě písmena.

## Fáze 6 – Závěr

```
## Prezentace

- **Zdroj:** <cesta>/Prezentace.md – <N> slajdů
- **Prezentace:** <cesta>/<adresář>.pptx
- **Náhledy:** <adresář s náhledy>

**Kontrola**
- Sestavení: <příkaz a návratový kód>
- Náhledy: <kolik kol, co se opravilo, nebo „bez nálezu“>
- Otevřené `DOHLEDAT:` <počet a u kterých slajdů, nebo „žádné“>

**Nezkontrolováno**
- <co a proč, nebo „nic“>
```

Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo – `~/.claude/standards/rules.md`, *Styl odpovědí*. Cesty piš celé od kořene disku.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Prezentace je hotová a zkontrolovaná, můžeš ji promítnout: <cesta k .pptx>.`
- `Prezentace hotová není – brání tomu: <konkrétní seznam>.`

Otevřené `DOHLEDAT:`, přeskočená kontrola náhledů i modul bez látky patří do druhé věty.
