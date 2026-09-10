# /ptydepe – revize slov, kterým rozumíte jenom vy dva

Claude si z konverzace odnese slovo, které jste použili jednou a třeba omylem, a začne ho používat jako zavedený pojem – napříč projekty, v dokumentaci, v názvech souborů. Po půl roce máte konfiguraci psanou jazykem, kterému rozumí jen ta jedna session, ve které vznikl. Tenhle skill takové termíny vyhledá, projedná s vámi jeden po druhém a schválenou náhradu provede úplně všude.

Jméno je po umělém jazyce z Havlova *Vyrozumění*: řeč, které nikdo nerozumí, ale všichni předstírají, že ano.

## Co umí

1. **`/ptydepe`** nebo **`/ptydepe suggest`** (výchozí) – **vytipuje kandidáty.** Projede vaše soubory a vrátí seřazený seznam: kolikrát se termín vyskytuje, kde vznikl a **čemu se tak běžně říká**. Nic nemění.
2. **`/ptydepe add <termín>`** – **projedná jeden termín.** Řekne, co jím myslí a odkud ho má, navrhne jednu náhradu i se zamítnutými variantami, počká na vaše rozhodnutí – a teprve pak ji provede ve všech repozitářích naráz, zapíše do slovníku a commitne.
3. **Umí skončit i tím, že se nic nemění.** Je-li slovo běžná čeština, zapíše se rozhodnutí *ponechat* i s důvodem, aby se to samé neotvíralo za měsíc znovu.

## Proč zrovna tenhle

- **Rozhoduje, ne jen přejmenovává.** Nejtěžší část není náhrada, ale odpověď na otázku, jestli je termín zavedený – a odděleně anglicky a česky, protože se to běžně liší.
- **Nechodí přes soubory, které nejsou ve verzování.** Čte výhradně to, co zná git, takže se nedotkne historie konverzací, cache ani paměti.
- **Hlídá věci, na kterých plošná náhrada ztroskotá:** stejné slovo v jiném významu, změněný rod a s ním shoda přívlastků, věty, ve kterých náhrada vyrobí trojí opakování téhož slova, a popisky ve formulářích, kde po náhradě zbude sloveso místo názvu.
- **Nechá po sobě dohledatelnou stopu.** Starý termín zůstane zapsaný u svého nástupce i s důvodem, proč padl – na jediném místě, jinde zmizí beze zbytku.
- **Nezačne opravovat, dokud nerozhodnete.** Návrh končí otázkou, ne prací.

## Jak se to používá

```
/ptydepe                 # co všechno je podezřelé
/ptydepe add zelená linka   # projedná a nahradí jeden termín
```

## Ukázka výstupu

Z režimu `suggest`:

```
- **brána** – 142× ve 29 souborech · coding/quality.md · běžně: quality gate, blokující kontrola
- **zelená linka** – 150× ve 29 souborech · coding/quality.md · běžně: zelené CI, green build
- **ráčna** – 16× v 8 souborech · tests/test_skills.py · běžně: ratchet (česky nezavedené)
```

Ze `add`, po dokončení:

```
## zelená linka → průběžná kontrola

**Rozsah:** 150 výskytů ve 29 souborech, repozitáře: ~/.claude, ~/Dev/context
**Vyloučeno:** archiv publikovaných textů
**Ručně přepsané věty:** 8 – repetice po náhradě

**Ověřeno**
- Kontrolní průchod: grep na starý tvar → 0 výskytů mimo slovník termínů
- Kontrakt: testy repozitáře OK, shellcheck 0
```

## Co nedělá

- **Nepřejmenovává na zadání** – to umí [`/replace`](../replace/README.md). Tenhle skill nejdřív rozhoduje, jestli se má přejmenovat vůbec.
- **Neaudituje projekt ani nekontroluje, jestli dokumentace dává smysl.** Jde výhradně o pojmenování.
- **Nesahá na publikované a cizí texty**, ani když jsou ve verzování. Termín v archivu článku je doklad, ne pravidlo.
- **Nezakládá slovníček pojmů vaší domény.** To je jiná věc: ten vysvětluje pojmy oboru, tenhle skill ruší vymyšlené.

## Jak si ho nainstalovat

> Jdi na https://github.com/jantichy/claude/tree/main/skills/ptydepe
> a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.

Skill si vede slovník rozhodnutých termínů na dvou místech: tabulku náhrad v `~/.claude/PTYDEPE.md` a rozvahu k nim v `terms.md` u sebe. Obojí si vytvoří sám při prvním běhu, ale **tabulku si musíte naimportovat do svého `~/.claude/CLAUDE.md`**, jinak o dohodnutých termínech Claude v dalších sessions neví a začne je zavádět znovu. Rozvaha se schválně neimportuje – do každé session by rostla s každým dalším termínem.

---

### Požadavky a omezení

Git – bez verzování skill nepozná, které soubory smí číst a měnit. Náhrada běží nad každým repozitářem zvlášť, takže rozsah je omezený na to, co máte lokálně naklonované. Jazykové posouzení („je tenhle termín zavedený?“) je odhad modelu, ne měření; proto se každý návrh předkládá ke schválení a nikdy se neprovádí sám.
