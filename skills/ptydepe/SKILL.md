---
name: ptydepe
description: Skill se použije, když uživatel zadá "/ptydepe", "/ptydepe suggest" nebo "/ptydepe add <termín>", anebo chce prověřit termíny, které Claude používá, přestože je v oboru nikdo nezná – slova převzatá z náhodné zmínky, z překlepu nebo z doslovného překladu, která se pak rozlezla napříč projekty a dokumentací. Výchozí režim "suggest" takové termíny vytipuje, režim "add" vypořádá jeden z nich. Postup, meze rozsahu a vyloučená místa má skill v těle a jsou závazné – bez jeho načtení se hledání ani náhrada nespouští, protože plošná náhrada umí nevratně přepsat soubory mimo verzování. Na rozdíl od /replace, který přejmenuje na zadání a v jednom projektu, tenhle skill rozhoduje, jestli se má přejmenovat, a jede přes všechny repozitáře naráz.
argument-hint: [suggest | add <termín>]
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion]
---

# Ptydepe

## Co skill dělá

Hledá a ruší **neustálené termíny** – slova, která používám, jako by byla zavedená, přestože je nikdo jiný nezná. Vznikají tím, že v konverzaci padne slovo, klidně jen překlepem nebo doslovným překladem, a já ho příště beru jako termín. Dohodnuté náhrady drží tabulka v `~/.claude/PTYDEPE.md`, která se importuje do každé session; rozvahu, proč který termín padl, drží `terms.md` v adresáři skillu.

- **`/ptydepe`** nebo **`/ptydepe suggest`** – **vytipování**. Projede konfiguraci i znalostní bázi a vrátí seřazené kandidáty s četností a běžným protějškem. Nic nemění.
- **`/ptydepe add <termín>`** – **projednání jednoho termínu**. Co znamená, odkud se vzal, čím ho nahradit – nebo že se ponechá. Po schválení náhrada napříč všemi repozitáři, zápis do `PTYDEPE.md` i do `terms.md`, commit.

Jméno je po umělém jazyce z Havlova *Vyrozumění*: řeč, které nikdo nerozumí, ale všichni předstírají, že ano.

## Co skill nedělá

- **Nepřejmenovává na zadání.** `/replace` dostane starý a nový tvar a provede to; tenhle skill nejdřív **rozhoduje, jestli se má přejmenovat vůbec**, a teprve pak nahrazuje – a to napříč všemi repozitáři, ne v jednom projektu.
- **Neaudituje projekt.** Rozpory mezi soubory řeší `/consistency`, srozumitelnost zápisu `/cleanup`. Tady jde výhradně o pojmenování.
- **Neposuzuje obsah.** Jestli dokument dává smysl, řeší `/oponent`.
- **Nesahá na cizí a publikované texty**, ani když jsou verzované – archiv článků, ohlasy, rozbory cizího stylu. Termín v nich není pravidlo, ale doklad, jak to tehdy bylo napsané.
- **Nezakládá projektové glosáře.** `docs/glossary.md` doménových pojmů jednoho projektu (`~/.claude/STRUCTURE.md`) je jiná věc: ten vysvětluje pojmy oboru, tenhle skill ruší vymyšlené.

## Jak je to postavené uvnitř

**Skill si dělá všechno sám**, delegace na `/replace` se neosvědčila a 7. 9. 2026 vypadla: umí odvozené tvary, ale ne to, co náhradu termínu doopravdy komplikuje – změnu rodu a s ní shodu přívlastků, homonyma, opačné významy a repetice, které náhrada vyrobí. Ve třiadvaceti termínech jednoho dne nebyl použitelný ani jednou.

**Náhrada se proto píše jako mapa frází, ne jako záměna slova.** Ke každé vazbě se starým termínem se napíše její nová podoba i se shodou (*„vyber čtyři až pět úhlů“* → *„vyber čtyři až pět hledisek“*), a teprve ta mapa se pustí přes soubory z `git ls-files`. Je to pracnější než `sed` a je to schválně: plošná záměna slova rozbije každou větu, kde se změnil rod nebo kde slovo znamená něco jiného.

**Závazné je** rozhodnutí, ne mechanika: náhrada se nedělá bez uživatele, starý termín zůstane zapsaný v `terms.md` a nikde jinde, a běh končí doloženým kontrolním průchodem. Jak se ta náhrada technicky provede, je implementační detail.

------

## Fáze 0 – Příprava

Společný začátek je v `~/.claude/skills/PREFLIGHT.md`. **Skill neběží nad jedním projektem**, ale nad všemi naráz, takže body 1 až 3 nahrazuje vlastními předpoklady:

1. **Kořeny.** `~/.claude`, `~/Dev/context` a **každý další git repozitář v `~/Dev`**. Posledně jmenované se do rozsahu berou, jen když se v nich termín vyskytuje – zjistí to inventura, ne domněnka.
2. **Zjisti, co je už rozhodnuté** – termín, který v tom seznamu je, ať nahrazený, nebo vědomě ponechaný, se znovu neprojednává. Kolik k tomu potřebuješ přečíst, se liší podle režimu: `suggest` si vystačí s `~/.claude/PTYDEPE.md` a **s *Obsahem*** `terms.md` v adresáři skillu, protože k vytipování kandidátů stačí jména; `add` čte **oba soubory celé**, protože rozhoduje o termínu a potřebuje k tomu úvahy i zamítnuté varianty. Rozvaha roste s každým vypořádaným termínem, takže tahat ji do běhu, který ji nepoužije, je táž vada, kvůli které se 10. 9. 2026 dělila sama tabulka.
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
| Jednoslovný protějšek nese jen půlku významu | **nahraď popisem, ne slovem** – heslo pak zní celou větou („seznam, který musí přesně sedět“). Je to legitimní výsledek, ne nouzové řešení |
| Slovo je běžná čeština v tomhle významu | **ponech** a zapiš proč, ať se to neotevírá znovu |
| Termín je zároveň **identifikátor v kódu** nebo klíčové slovo jazyka | **ponech.** Přeložit běžný text, zatímco kód dál říká původní jméno, vyrobí dvě jména pro jednu věc – `guard` je klíčové slovo Swiftu i pole ve schématu nálezu |

**Pak se zastav a počkej na souhlas.** Na soubory se v téže odpovědi nesahá – uživatel si často vybere jinou variantu, nebo ho návrh přivede na třetí, a práce udělaná mezitím se zahazuje. Odpoví-li jen na část návrhu, zbytek je pořád nezodpovězený, ne tiše schválený.

**Technické identifikátory se schvalují zvlášť** – jméno souboru, proměnné prostředí, klíče. Jejich přejmenování je změna chování, ne terminologie: komu běží vypnutá kontrola přes starou proměnnou, tomu se tiše zapne. Schválí-li se, **přestěhuj i stav**, který na starém jméně visí.

## Fáze 4 – Inventura a vyloučení

**Inventuru nikdy nezkracuj.** `cut`, `head` ani `-m` na výstupu grepu znamenají, že výskyt dál na řádku neuvidíš – a pak se objeví až po commitu.

1. **Jede se výhradně přes `git ls-files`.** Nikdy `rglob` ani `find` přes adresář: `~/.claude` obsahuje transkripty session, cache a paměť, které v `.gitignore` sice jsou, ale rekurzivnímu skriptu to nevadí a přepíše je.
2. **Najdi legitimní významy téhož slova** a soubory, kde stojí, vyluč jmenovitě. Stává se to skoro pokaždé: „brána“ byla i platební, „vizitka“ i firemní web, „osa“ i časová.
3. **Vyluč publikované a cizí texty** – `~/Dev/context/archive/`, `compose/_analysis/`, ohlasy ve `speaking/`.
4. **Vyluč vlastní frontu kandidátů.** Seznam termínů k projednání obsahuje ten termín jako položku a náhrada by si přepsala vlastní zadání.
5. **Vyluč `~/.claude/PTYDEPE.md` a `skills/ptydepe/terms.md`.** Starý tvar v nich stojí schválně – v levém sloupci tabulky a ve větě „nahrazuje dřívější …“. Náhrada by z rozhodnutí udělala tautologii a nikdo by pak nezjistil, co se čím nahradilo.
6. **Ověř, že slovo nemá v některém souboru opačný význam.** Stalo se: týž termín označoval jinde vadu, ne přednost, a plošná náhrada by z toho udělala nesmysl.

Vypiš přehled ke schválení: počet výskytů, soubory, vyloučená místa a proč.

## Fáze 5 – Náhrada

**Sestav mapu frází, ne seznam slov.** Ke každé vazbě, ve které se starý termín vyskytuje, napiš její novou podobu i se shodou – vytáhni si je předem (`grep` na okolí termínu) a projdi je očima. Teprve pak mapu pusť přes soubory z `git ls-files`.

Pak zkontroluj to, co ani ta nejlepší mapa nezachytí, protože to není o tvarech:

- **Shodu rodu.** Změní-li se rod, mění se přívlastky i vztažná zájmena: *„každý má jediný hledisko“* místo *„jediné“*. Projdi diff a hledej mužské koncovky před novým slovem středního rodu.
- **Repetice.** Náhrada vyrobí věty typu *„vypnutá kontrola se hlásí: kontrola, o které nikdo neví… tváří se jako kontrola“*. Ty se přepisují celé, ne slovem.
- **Vazby, které přestaly sedět.** *„opravy zanášejí nové pozůstatky“* – pozůstatky se nezanášejí, zůstávají.
- **Popisky a názvy.** Opisuje-li se termín v běžném textu slovesem (*„nic nezůstalo viset“*), je to v pořádku – ale tam, kde totéž slovo stojí jako **jméno věci**, ne. Projdi `header` u `AskUserQuestion`, popisky polí v šablonách výstupu a nadpisy kroků a ověř, že pojmenovávají podstatným jménem. *„Viselo 4/4“* jako název kroku ve formuláři nepojmenovává nic, ale gramaticky je věta okolo v pořádku, takže náhrada projde a vidí se to až v běžícím formuláři.

## Fáze 6 – Záznam

**Zapisuje se na dvě místa a obojí je povinné.** Rozdělené jsou proto, že `PTYDEPE.md` jde do každé session a rostl by s každým termínem, kdežto důvody potřebuje jen ten, kdo rozhoduje:

- **`~/.claude/PTYDEPE.md`** – jeden řádek tabulky: starý tvar, nový tvar, rozsah a meze. Nic víc; odůvodnění sem nepatří.
- **`~/.claude/skills/ptydepe/terms.md`** – heslo s celou rozvahou (a řádek do jeho *Obsahu*): co termín znamená, co jím naopak není, a věta **„nahrazuje dřívější …“ i s důvodem**. Starý termín zůstává zapsaný **tady** – jinde se nahradil beze stopy –, aby se dalo rozhodnutí vrátit nebo aspoň dohledat, proč padlo. **Čtyři druhy míst, kde vědomě zůstává i jinde**, vypisuje `terms.md`, *Jak se to zapisuje*; heslo je u sebe vždycky jmenuje.

**Neexistuje-li některý z nich, založ ho:** `PTYDEPE.md` s nadpisem, sekcí *Jak se používá* a prázdnou tabulkou, `terms.md` s nadpisem, sekcí *Jak se to zapisuje*, sekcí *Obsah* a prázdnými sekcemi *Termíny* a *Ponechané termíny*. Bez toho by první běh neměl kam zapsat.

**Nebylo-li co nahradit, zapiš to stejně** – je to **preventivní zápis** a pravidlo pro něj drží `terms.md`, *Jak se to zapisuje*. Pro běh z toho plyne jediné: *Fáze 7* vypíše u rozsahu i u ručně přepsaných vět nulu a je to platný výsledek, ne prázdný běh.

**Skončilo-li to ponecháním**, do `PTYDEPE.md` nepatří nic – tabulka říká, co se čím nahrazuje. Zapiš rozhodnutí i se zamítnutými variantami do sekce *Ponechané termíny* v `terms.md` **a přidej ho do jeho *Obsahu***, jinak se termín otevře znovu při příští revizi.

## Fáze 7 – Závěr

Ověř a **dolož příkazem**, ne dojmem: kontrolní průchod na starý tvar a příkazy z kontraktu každého dotčeného repozitáře.

```
## <starý> → <nový>

- **Rozsah:** <N> výskytů v <M> souborech, repozitáře: <seznam>
- **Vyloučeno:** <kde a proč, nebo „nic">
- **Ručně přepsané věty:** <kolik a proč – shoda, repetice>

**Ověřeno**
- Kontrolní průchod: <příkaz a co vrátil>
- Kontrakt: <příkazy a návratové kódy, nebo „repozitář nemá">

**Zapsáno**
- PTYDEPE.md · terms.md · commity v <repozitářích>
```

Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo – `~/.claude/RULES.md`, *Styl odpovědí*.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Termín je vypořádaný a ověřený, starý tvar se mimo PTYDEPE.md, terms.md a vědomě vyloučená místa nevyskytuje.`
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
- **<termín>** – <N>× v <M> souborech · <kde vznikl> · běžně: <protějšek>
```

Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo – `~/.claude/RULES.md`, *Styl odpovědí*.

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
