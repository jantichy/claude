---
name: ptydepe
description: Skill se použije, když uživatel zadá "/ptydepe", "/ptydepe suggest" nebo "/ptydepe add <termín>", anebo chce prověřit termíny, které Claude používá, přestože je v oboru nikdo nezná – slova převzatá z náhodné zmínky, z překlepu nebo z doslovného překladu, která se pak rozlezla napříč projekty a dokumentací. Výchozí režim "suggest" takové termíny vytipuje, režim "add" vypořádá jeden z nich. Postup, meze rozsahu a vyloučená místa má skill v těle a jsou závazné – bez jeho načtení se hledání ani náhrada nespouští, protože plošná náhrada umí nevratně přepsat soubory mimo verzování. Na rozdíl od /replace, který přejmenování jen provede, tenhle skill rozhoduje, jestli se má přejmenovat, a pak ho volá.
argument-hint: [suggest | add <termín>]
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Skill, AskUserQuestion]
---

# Ptydepe

## Co skill dělá

Hledá a ruší **neustálené termíny** – slova, která používám, jako by byla zavedená, přestože je nikdo jiný nezná. Vznikají tím, že v konverzaci padne slovo, klidně jen překlepem nebo doslovným překladem, a já ho příště beru jako termín. Rozhodnutí drží `~/.claude/PTYDEPE.md`, který se importuje do každé session.

- **`/ptydepe`** nebo **`/ptydepe suggest`** – **vytipování**. Projede konfiguraci i znalostní bázi a vrátí seřazené kandidáty s četností a běžným protějškem. Nic nemění.
- **`/ptydepe add <termín>`** – **projednání jednoho termínu**. Co znamená, odkud se vzal, čím ho nahradit – nebo že se ponechá. Po schválení náhrada napříč všemi repozitáři, zápis do `PTYDEPE.md`, commit.

Jméno je po umělém jazyce z Havlova *Vyrozumění*: řeč, které nikdo nerozumí, ale všichni předstírají, že ano.

## Co skill nedělá

- **Neprovádí přejmenování sám.** Mechanickou náhradu včetně odvozených a skloňovaných tvarů dělá `/replace`; tenhle skill rozhoduje, **jestli** se má přejmenovat, a pak ho volá.
- **Neaudituje projekt.** Rozpory mezi soubory řeší `/consistency`, srozumitelnost zápisu `/cleanup`. Tady jde výhradně o pojmenování.
- **Neposuzuje obsah.** Jestli dokument dává smysl, řeší `/oponent`.
- **Nesahá na cizí a publikované texty**, ani když jsou verzované – archiv článků, ohlasy, rozbory cizího stylu. Termín v nich není pravidlo, ale doklad, jak to tehdy bylo napsané.
- **Nezakládá projektové glosáře.** `docs/glossary.md` doménových pojmů jednoho projektu (`~/.claude/STRUCTURE.md`) je jiná věc: ten vysvětluje pojmy oboru, tenhle skill ruší vymyšlené.

## Jak je to postavené uvnitř

| Krok | Kdo | Proč zrovna on |
|---|---|---|
| Vytipování kandidátů | **vlastní** | Kritérium *„normálně se tomu říká jinak“* neumí změřit žádný nástroj |
| Inventura výskytů | `git ls-files` + `grep` | Deterministické a nula tokenů |
| Rozhodnutí o náhradě | **vlastní, s uživatelem** | Jádro skillu |
| Náhrada v souborech | **`/replace`**, jednou na každý repozitář | Umí odvozené tvary včetně české skloňované varianty a končí kontrolním průchodem |
| Kontrola shody a repetic | **vlastní** | `/replace` řeší tvary, ne to, že se změnou termínu změnil rod |
| Záznam a ověření | **vlastní** | |

**Volání `/replace` je implementační detail, ne rozhraní** – dá se kdykoliv vyměnit za vlastní skript. Závazné je: rozhodnutí se nedělá bez uživatele, starý termín zůstane zapsaný v `PTYDEPE.md` a nikde jinde, a běh končí doloženým kontrolním průchodem.

------

## Fáze 0 – Pre-flight

Společný začátek je v `~/.claude/skills/PREFLIGHT.md`. **Skill neběží nad jedním projektem**, ale nad všemi naráz, takže body 1 až 3 nahrazuje vlastními předpoklady:

1. **Kořeny.** `~/.claude`, `~/Dev/context` a **každý další git repozitář v `~/Dev`**. Posledně jmenované se do rozsahu berou, jen když se v nich termín vyskytuje – zjistí to inventura, ne domněnka.
2. **Přečti `~/.claude/PTYDEPE.md` celý.** Je to zdroj pravdy; termín, který v něm už je, se znovu neprojednává.
3. **Pracovní strom každého dotčeného repozitáře musí být čistý.** Rozpracované změny se s náhradou smíchají a přestane být poznat, co je čí. Vypiš je a zeptej se.
4. **Zjisti režim a termín** z argumentu. Bez argumentu jede `suggest`.

**Co se svými zápisy udělá:** commituje je, v každém dotčeném repozitáři zvlášť a s vlastní zprávou. Bez toho by je posbíral autocommit cizí session spolu s něčím nesouvisejícím.

## Fáze 1 – Volba režimu

| Režim | Pokračuj |
|---|---|
| `suggest` (výchozí) | *Režim `suggest`* níž |
| `add <termín>` | Fáze 2 |

## Fáze 2 – Co ten termín znamená a odkud se vzal

**Nejdřív si ho přečti v kontextu, teprve pak o něm mluv.** Vytáhni **všechny** výskyty i s okolím a odpověz na tři otázky:

1. **Co jím myslím** – jedna věta, konkrétně. Ne „něco jako kontrola“.
2. **Odkud se vzal** – z konverzace, z doslovného překladu, z uživatelova zápisu? Dohledej to; není-li to dohledatelné, řekni to rovnou, místo abys původ domýšlel.
3. **Je zavedený?** Odděleně **anglicky** a **česky** – to se běžně liší a rozhoduje ta druhá odpověď. *Quality gate* je zavedený pojem, česká „brána“ ne.

**„Je to uživatelovo slovo“ není argument pro ponechání.** Do souborů se dostane i to, co uživatel jednou napsal a sám tak nemluví.

## Fáze 3 – Návrh a rozhodnutí

**Vyber jednu náhradu a obhaj ji.** Ne výčet možností – to je odklad rozhodnutí na horší chvíli. K ní přidej **jednu až dvě zvážené a zamítnuté** i s důvodem; příště se pak nezkoumají znovu.

Kritérium je jediné: **rozumí tomu člověk, který k tomu přijde bez slovníku?**

| Kdy | Co s tím |
|---|---|
| Existuje běžný český protějšek | vezmi ho |
| Termín je zavedený anglicky, ne česky | přelož podle zavedené vazby, ne doslova – *surgical strike* je česky „cílený úder“, ne „chirurgický“ |
| Je to metafora, kterou věta vedle stejně vysvětluje | zruš termín a nech ten popis |
| Slovo je běžná čeština v tomhle významu | **ponech** a zapiš proč, ať se to neotevírá znovu |

**Pak se zastav a počkej na souhlas.** Na soubory se v tomtéž tahu nesahá – uživatel si často vybere jinou variantu, nebo ho návrh přivede na třetí, a práce udělaná mezitím se zahazuje. Odpoví-li jen na část návrhu, zbytek je pořád nezodpovězený, ne tiše schválený.

**Technické identifikátory se schvalují zvlášť** – jméno souboru, proměnné prostředí, klíče. Jejich přejmenování je změna chování, ne terminologie: komu běží vypnutá kontrola přes starou proměnnou, tomu se tiše zapne. Schválí-li se, **přestěhuj i stav**, který na starém jméně visí.

## Fáze 4 – Inventura a vyloučení

**Inventuru nikdy nezkracuj.** `cut`, `head` ani `-m` na výstupu grepu znamenají, že výskyt dál na řádku neuvidíš – a pak se objeví až po commitu.

1. **Jede se výhradně přes `git ls-files`.** Nikdy `rglob` ani `find` přes adresář: `~/.claude` obsahuje transkripty session, cache a paměť, které v `.gitignore` sice jsou, ale rekurzivnímu skriptu to nevadí a přepíše je.
2. **Najdi legitimní významy téhož slova** a soubory, kde stojí, vyluč jmenovitě. Stává se to skoro pokaždé: „brána“ byla i platební, „vizitka“ i firemní web, „osa“ i časová.
3. **Vyluč publikované a cizí texty** – `~/Dev/context/archive/`, `compose/_analysis/`, ohlasy ve `speaking/`.
4. **Vyluč vlastní frontu kandidátů.** Seznam termínů k projednání obsahuje ten termín jako položku a náhrada by si přepsala vlastní zadání.
5. **Ověř, že slovo nemá v některém souboru opačný význam.** Stalo se: týž termín označoval jinde vadu, ne přednost, a plošná náhrada by z toho udělala nesmysl.

Vypiš přehled ke schválení: počet výskytů, soubory, vyloučená místa a proč.

## Fáze 5 – Náhrada

**Pusť `/replace` jednou na každý dotčený repozitář**, se starým a novým tvarem a se seznamem vyloučených míst. Odvozené a skloňované tvary jsou jeho práce, ne tvoje.

Pak zkontroluj to, co `/replace` neumí, protože to není o tvarech:

- **Shodu rodu.** Změní-li se rod, mění se přívlastky i vztažná zájmena: *„každý má jediný hledisko“* místo *„jediné“*. Projdi diff a hledej mužské koncovky před novým slovem středního rodu.
- **Repetice.** Náhrada vyrobí věty typu *„vypnutá kontrola se hlásí: kontrola, o které nikdo neví… tváří se jako kontrola“*. Ty se přepisují celé, ne slovem.
- **Vazby, které přestaly sedět.** *„opravy zanášejí nové pozůstatky“* – pozůstatky se nezanášejí, zůstávají.
- **Popisky a názvy.** Opisuje-li se termín v próze slovesem (*„nic nezůstalo viset“*), je to v pořádku – ale tam, kde totéž slovo stojí jako **jméno věci**, ne. Projdi `header` u `AskUserQuestion`, popisky polí v šablonách výstupu a nadpisy kroků a ověř, že pojmenovávají podstatným jménem. *„Viselo 4/4“* jako název kroku ve formuláři nepojmenovává nic, ale gramaticky je věta okolo v pořádku, takže náhrada projde a vidí se to až v běžícím formuláři.

## Fáze 6 – Záznam

**Do `~/.claude/PTYDEPE.md`** zapiš nový termín: co znamená, co jím naopak není, a větu **„nahrazuje dřívější …“ i s důvodem**. Starý termín zůstává zapsaný **tady a jenom tady** – jinde se nahradil beze stopy –, aby se dalo rozhodnutí vrátit nebo aspoň dohledat, proč padlo.

**Skončilo-li to ponecháním**, do `PTYDEPE.md` nepatří nic. Zapiš rozhodnutí i se zamítnutými variantami do `decisions.md` podle `~/.claude/STRUCTURE.md` – jinak se termín otevře znovu při příští revizi.

## Fáze 7 – Závěr

Ověř a **dolož příkazem**, ne dojmem: kontrolní průchod na starý tvar a příkazy z kontraktu každého dotčeného repozitáře.

```
## <starý> → <nový>

**Rozsah:** <N> výskytů v <M> souborech, repozitáře: <seznam>
**Vyloučeno:** <kde a proč, nebo „nic">
**Ručně přepsané věty:** <kolik a proč – shoda, repetice>

**Ověřeno**
- Kontrolní průchod: <příkaz a co vrátil>
- Kontrakt: <příkazy a návratové kódy, nebo „repozitář nemá">

**Zapsáno**
- PTYDEPE.md · decisions.md · commity v <repozitářích>
```

Vypiš to jako **Markdown, ne jako blok kódu** (`~/.claude/RULES.md`, *Styl odpovědí*).

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Termín je vypořádaný a ověřený, starý tvar se mimo PTYDEPE.md nevyskytuje.`
- `Termín vypořádaný není – brání tomu: <konkrétní seznam>.`

------

## Režim `suggest`

Vytipuje kandidáty. **Nic nemění a na nic se neptá** – výstupem je seznam k projednání.

**Kritérium je jediné a zní: normálně se tomu říká jinak.** Hledej tedy termín, který:

- **nemá oporu v oboru** – v angličtině ano, v češtině ne (*ratchet* → „ráčna“), nebo nikde,
- **je doslovný překlad**, který v češtině znamená něco jiného („chirurgický zásah“),
- **má v češtině obsazený jiný význam** („zelená linka“ je telefon podpory, „zamluvit“ je rezervovat),
- **je anglicismus skloňovaný po česku** („fresh-readera“, „2 fresh-readeři“),
- **pojmenovává formu místo účelu** („dvě věty“ místo „verdikt“),
- **není slovo, jen tvar odvozený ze slovesa** („viséc“ z „zůstalo to viset“).

**Nehledej podle vlastního pocitu, co zní divně.** Ten tě zradí: „brána“ i „zelená linka“ vypadaly jako moje výmysly a byly z uživatelových souborů, zatímco běžně vypadající „vizitka“ termín byl. **Spolehlivější síto je četnost bez definice** – slovo, které se používá často a nikde není vysvětlené, si buď každý vykládá po svém, nebo se zavedlo bokem.

Výstup seřaď podle četnosti a u každého uveď, **čemu se tak běžně říká**. Bez toho je to jen seznam podezření, ke kterému se nedá nic rozhodnout.

```
<termín>   <N>× v <M> souborech   <kde vznikl>   běžně: <protějšek>
```

Na konci nabídni **zapsání fronty do souboru**. Seznam v konverzaci nepřežije kompaktaci a práce by se rozjela znovu od nuly.

## Časté chyby

Všechny z ostrých běhů, každá se opravdu stala:

- **Skript jel rekurzivně přes adresář místo přes `git ls-files`** a přepsal 1 120 transkriptů, cache a souborů historie. Nevratné, protože nejsou v gitu.
- **Inventura zkrácená `cut -c1-230`** minula polovinu výskytů – ty, které stály dál na řádku. Objevily se až po commitu.
- **Fronta kandidátů si přepsala vlastní položku**, protože nebyla vyloučená z náhrady. Dvakrát po sobě.
- **Náhrada zasáhla homonymum** – „platební brána“ se změnila na „platební kontrolu“ ve větě o penězích.
- **Změna rodu rozbila shodu.** „Úhel“ je mužský, „hledisko“ střední, a jedenáct přívlastků zůstalo v původním tvaru.
- **Termín se obhajoval z paměti místo ze souborů.** Vznikla tím tabulka tří vrstev, kterou zdrojový dokument nikdy neobsahoval.
- **Náhrada se začala dělat před souhlasem.** Uživatel se rozhodl jinak a muselo se to vracet.
- **Náhrada minula popisky ve formuláři.** Podstatné jméno se v `/cleanup` nahradilo všude, ale v `header`u a v šabloně zbyl tvar odvozený ze slovesa: krok se jmenoval „Viselo 4/4“. Prošlo to kontrolním průchodem i testy a všimlo si toho až oko nad běžícím formulářem.
