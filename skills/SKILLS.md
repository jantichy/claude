# Jak se píše skill

Norma tvaru vlastních skillů v `~/.claude/skills/`. Definuje, **co je skill a jak vypadá**; postup, kterým se zakládá, reviduje a ruší, drží `/skill`. Je to týž vztah jako mezi `~/.claude/STRUCTURE.md` a `/project` – standard říká, jak to má vypadat, nástroj je jen instalátor.

Platí pro skilly v tomhle repozitáři. Cizí skilly z pluginů se podle ní neposuzují; ty se **používají**, ne udržují.

## Co do tohoto souboru nepatří

Vyhrává první kritérium, které sedí:

1. Platí to pro práci obecně, ne jen pro skilly? → `~/.claude/RULES.md`
2. Je to postup zakládání, revize nebo rušení skillu? → `/skill`
3. Je to začátek běhu, který sdílí víc skillů? → `~/.claude/skills/PREFLIGHT.md`
4. Týká se to jednoho konkrétního skillu? → do jeho `SKILL.md`
5. Nic z toho → sem

------

## 1. Kdy vzniká skill – a kdy ne

**Skill je proces, který se opakuje a vyžaduje úsudek.** To druhé je důležitější než první.

Než skill založíš, projdi čtyři možnosti v tomhle pořadí. Vyhrává první, která sedí:

| Kdyby platilo | Nepatří to do skillu, ale sem |
|---|---|
| Chytne to typecheck, linter, test nebo hook | **do té kontroly.** `~/.claude/RULES.md`, *Model a effort podle úkolu*, pravidlo nula: nejlevnější práce je ta, kterou neudělá model. Mechanické omezení zapsané do skillu se dodržuje hůř a stojí tokeny při každém běhu. |
| Platí to pro každou práci, ne jen pro tenhle postup | **`~/.claude/RULES.md`.** |
| Je to znalost oboru – jak se dělá web, text, měření, kód | **doména v `~/Dev/context/`.** Skill ji smí načítat, ne obsahovat. |
| Platí to jen v jednom repozitáři | **jeho `CLAUDE.md`.** |

Teprve co nezbylo, je skill.

**Nezakládej skill na jednorázovou věc.** Postup provedený jednou je práce, ne proces. Skill má cenu, až když ho pustíš potřetí – do té doby je to dokumentace něčeho, co se možná nebude opakovat.

**Nezakládej skill jen proto, že je postup dlouhý.** Délka je důvod pro sepsání, ne pro skill. Rozdíl je v tom, jestli se **rozhoduje** – když má postup jedinou správnou cestu bez odboček, patří do skriptu.

## 2. Skládej, nepiš znovu

**Než napíšeš krok, zjisti, jestli ho něco neumí.** Prohledej vestavěné skilly Claude Code, nainstalované pluginy, vlastní skilly, hooky a deterministické nástroje. Píše se jen to, co nezbude.

Skill má tři vrstvy a jen jedna je závazná:

| Vrstva | Co to je | Kdy se smí změnit |
|---|---|---|
| **Rozhraní** | jak se skill volá, co musí být na výstupu, co po něm platí | nikdy tiše |
| **Vlastní obsah** | norma, napojení na okolí, to, co neumí nikdo jiný | s rozvahou |
| **Vnitřek** | delegace ven, nebo vlastní skripty | kdykoliv, bez ohlášení |

**Vnitřek se přiznává** v sekci *Jak je to postavené uvnitř* a výslovně se v ní označí za implementační detail. Bez toho si na něj někdo zvykne jako na rozhraní a příští výměna nástroje se stane rozbitím kontraktu.

**Delegace se zadává kontraktem výstupu, ne seznamem kroků.** „Potřebuju `docs/plan.md`, kde má každý úkol ověřitelné kritérium" přežije upgrade cizího nástroje; „udělej svůj krok 3 a pak krok 5" ne.

**Co patří normě, se cizímu nástroji nesvěřuje.** Tvar, umístění výstupu, jazyk a pojmenování mu předej výslovně – každý nástroj má vlastní výchozí volbu a prosadí ji, když mlčíš.

**Nedeleguj jádro.** Test: *zbylo by po odečtení všech delegací něco, co je tvoje?* Když ne, není to skill, ale alias – a ten se má napsat jako alias.

**Kdy obalovat nemá cenu:** když cizí nástroj pokrývá menšinu potřeby a většina práce je jeho nastavování a přemlouvání. Pak je vlastní implementace levnější a hlavně čitelnější.

## 3. Hlavička

```yaml
---
name: jméno            # shodné s názvem adresáře, malá písmena a pomlčky
description: …         # kdy se použije i co dělá, třetí osoba, do 1024 znaků
argument-hint: [režim] # jen má-li skill režimy
allowed-tools: [...]   # minimální sada, kterou skill opravdu potřebuje
---
```

**`description` rozhoduje, jestli se skill vůbec vyvolá.** Je to jediná část, kterou má model v kontextu pořád – tělo se načte až potom. Píše se tedy pro rozhodování, ne pro popis.

- Začni tvarem `Skill se použije, když uživatel zadá "/jméno", nebo chce …`. Doslovný spouštěč i popis situace: uživatel skill vyvolá obojím způsobem.
- **Třetí osoba.** Ne „umím ti…", ne „můžeš tímhle…".
- **Řekni i to, co skill nedělá**, liší-li se od podobného skillu. `/attack` to má takhle: *„Na rozdíl od `/review`, který kód čte, tenhle skill ho spouští."* Bez toho si model vybere špatný ze dvou blízkých.
- **Vejdi se do 1024 znaků.** Delší popis se nemusí přenést celý.

**Režimy se jmenují anglicky, jedním slovem, malými písmeny** – a **lícují napříč skilly**: co dělá totéž, jmenuje se stejně. Ustálená sada je `create`, `update`, `delete`; k ní podle potřeby další jednoslovné (`extract`, `full`). **Má-li skill jediné chování, žádný režim nemá a nepojmenovává se** – vymýšlet jméno pro to, co se stane vždycky, je zbytečné. **Jakmile má režimy dva a víc, musí být pojmenované všechny včetně výchozího** a u výchozího se to řekne. Hint, ve kterém stojí jen ten nevýchozí (`[full]`), tvrdí, že skill umí jednu věc – a to, co dělá bez argumentu, pak nejde napsat explicitně.

**Proč anglicky:** je to jméno akce, ne řeč o ní. České „revize" se skloňuje, píše se s diakritikou a v `argument-hint` vypadá jako věta; `update` je token. Česká podstatná jména v próze („výsledek revize") zůstávají česky – rozdíl je mezi **jménem režimu** a mluvením o něm.

**Proč lícovat:** dva skilly, které dělají tutéž věc pod jiným jménem, nutí uživatele pamatovat si, který má který. Platí to i pro režimy, které se **rozpoznávají samy** a nepředávají se argumentem – uživatel je vidí ve výpisu a pojmenovává je v řeči stejně.

**`argument-hint` musí sedět s tělem.** Režim popsaný v těle a chybějící v hintu uživatel nikdy neuvidí; hint bez opory v těle slibuje funkci, která neexistuje.

**`allowed-tools` drž na minimu.** Dlouhé ruční výčty nástrojů MCP jsou křehké – při přejmenování serveru se rozejdou tiše a skill pak selže až za běhu.

## 4. Povinné sekce a jejich pořadí

**Tahle sekce mluví o `SKILL.md`.** Vedle něj má každý skill povinně ještě `README.md` – text pro člověka zvenčí s vlastní strukturou; tu drží *README skillu* níž.

```
# Název

## Co skill dělá
## Co skill nedělá
## Jak je to postavené uvnitř      ← jen deleguje-li ven
## Fáze 0 – Pre-flight
## Fáze 1..N – …
## Časté chyby                     ← nepovinná
## Fáze N – Závěr
```

**Tohle pořadí platí pro hlavní průběh.** Má-li skill **přílohové sekce** – samostatné režimy, katalog hledisek nebo vektorů –, stojí **za** závěrečnou fází: nejsou její součástí a čtenář se k nim dostane jen tehdy, když je potřebuje. `## Časté chyby` je pak úplně poslední, aby stála za vším, k čemu se vztahuje:

```
## Fáze N – Závěr        ← konec hlavního průběhu
## Režim <jméno>         ← příloha
## Časté chyby           ← naposled
```

U lineárního skillu bez příloh se nic nemění a `## Časté chyby` zůstávají před závěrem.

**`## Co skill dělá`** – co to je a jaké má režimy. Tři až deset řádků. Ne převyprávěný postup; ten je níž.

**`## Co skill nedělá`** – vymezení proti **jmenovaným** sousedům, ne obecná negace. „Nepíše kód" je bezcenné; *„Neaudituje projekt. Na vnitřní konzistenci je `/consistency`."* je vymezení. U skillu, který stojí v *Životním cyklu projektu* (`~/.claude/RULES.md`), je tahle sekce povinná a musí jmenovat sousedy z obou stran – bez ní se práce buď zdvojí, nebo neudělá vůbec.

**`## Jak je to postavené uvnitř`** – deleguje-li skill na cizí nástroj, **nebo nese-li vlastní spustitelný vnitřek** (skripty ve svém adresáři). Řekne, co volá nebo pouští, **a výslovně že je to implementační detail, ne rozhraní**, plus co je naopak závazné a nesmí se změnit tiše. Důvod je v obou případech týž: co se nepřizná jako vyměnitelné, na to si někdo zvykne jako na rozhraní. Viz *Skládej, nepiš znovu*.

**`## Fáze 0 – Pre-flight`** – odkaz na `~/.claude/skills/PREFLIGHT.md` a **jen odchylky tohohle skillu**. Nikdy sem neopisuj obsah odtamtud.

**`## Fáze 1..N`** – vlastní postup.

**`## Časté chyby`** – nepovinná, ale zakládej ji, jakmile má skill za sebou první ostré běhy. Patří sem to, co se v praxi pokazilo, ne co by se pokazit mohlo. Zdroj je `docs/decisions.md` a poučení z běhů; bez téhle sekce se do skillu nikdy nevrátí.

**`## Fáze N – Závěr`** – **poslední** fáze skillu; nese šablonu výstupu a **závěrečný verdikt**. Jméno po pomlčce **závazné není** – `Úklid a shrnutí`, `Uzavření` i `Předání` jsou v pořádku, závěr se pozná podle toho, že je poslední. Naopak **`Fáze 0` je závazná číslem**: pre-flight je vždycky nultý, ať se jmenuje jakkoliv (`/oponent` má „Fáze 0 – Co se oponuje“, `/project` „Krok 0 – Zjisti režim a stav“):

**Verdikt má dvě předepsaná znění a skill si mezi nimi jen vybírá; vlastní si neformuluje.** Jméno „verdikt“ svádí k tomu, že jde o volné shrnutí – nejde: skill je **uvádí doslovně**, aby se z nich za běhu nestala parafráze. Jejich znění si ale volí sám – **doslovná napříč skilly být nemůžou**, protože čeština žádá shodu s rodem toho, co je hotové (*„Plán hotový není"* × *„Hotové to není"*). Závazný je tedy vzorec:

1. **První** říká, že věc je hotová a ověřená, a čím se dá pokračovat.
2. **Druhá** říká, že hotová není, a **jmenuje konkrétně, co tomu brání** – ne „ještě zbývá pár věcí".
3. **Mezi nimi nic není.** Žádná třetí varianta, žádné smířlivé „v zásadě hotovo".

```
Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `<Věc> je hotová a ověřená, můžeš …`
- `<Věc> hotová není – brání tomu: <konkrétní seznam>.`
```

Skill s vlastním koncem pro některý režim (rušení, zamítnutí) smí mít druhou dvojici, ale musí splňovat týž vzorec.

Ten verdikt je celá bezpečnostní pojistka skillu: nutí odlišit „udělal jsem kroky" od „výsledek platí". Bez nich končí každý běh smířlivým odstavcem, ze kterého nejde poznat, jestli se dá pokračovat.

## 5. Číslování a názvosloví

**„Fáze" je norma.** Číslují se od nuly (`Fáze 0 – Pre-flight`) a čísla se nemění bezdůvodně – odkazuje se na ně napříč skilly.

**Číslují se plochou vzestupnou řadou, bez písmen.** `0, 1, 2, 3…`, ne `1, 1b, 2`. Čtenář bere číslování jako tvrzení o vztazích, takže `1b`, které o vztahu k `1` nic neříká, lže.

**Písmenná podfáze je v souladu jen tam, kde sdružuje tematicky příbuzné podkroky téhož kroku.** Kritérium je ostré: písmena jen tehdy, když by jinak jeden krok musel vyrábět **dva samostatné výstupy**. Tak to má `/specify` s `Fází 3a` (produktová specifikace) a `3b` (návrh řešení) – dva dokumenty jednoho zadání.

Není to výjimka, ale splněné kritérium: co mu vyhoví, revize nesahá; co mu nevyhoví, je nedodělek a **opraví se**.

**„Krok" jen u průvodce nastavením.** Rozhoduje, **čí odpovědi tvoří výsledek**: u `/project` je výsledkem to, co uživatel naodpovídal, takže postup je sled otázek a jmenuje se „krok". Skilly, které něco samy najdou nebo vyrobí a ptají se až na nálezy – `/review`, `/consistency`, `/invoicing` –, mají „fázi", i když se ptají stejně často.

Rozlišovat podle toho, „jestli se uživatel může kdykoliv zastavit", nestačí: to platí u všech. Skill, který volí „krok", to musí ve svých zásadách zdůvodnit tímhle kritériem.

**Neodkazuj se dovnitř jiného skillu.** Potřebuješ-li tentýž postup jako soused, patří ten postup do `PREFLIGHT.md` nebo do doménové znalosti – ne do odkazu na jeho fázi. Cizí fáze se přečíslují a odkaz tiše ukáže jinam.

**Jeden termín pro jednu věc** (`~/.claude/RULES.md`, *Jeden termín pro jednu věc*). Ve skillech to platí navíc **napříč nimi**, ne jen uvnitř jednoho: skilly se čtou jeden po druhém v jednom životním cyklu a rozdílné pojmenování téhož kroku vypadá jako rozdílný krok.

## 6. Délka a progresivní odhalení

| Mez | Co dělat |
|---|---|
| do 300 řádků | v pořádku |
| 300–500 řádků | zvaž rozdělení, řekni to při revizi |
| nad 500 řádků | **rozděl** |

Tělo `SKILL.md` se načte celé, jakmile se skill vyvolá – včetně větví, které v tom běhu neplatí. Kontext, který tím spotřebuješ, chybí na vlastní práci.

**Co se vytahuje do vedlejších souborů:** zadání pro agenty, katalogy hledisek a vektorů, dlouhé referenční tabulky, šablony výstupů, skripty.

**Vedlejší soubory leží jednu úroveň hluboko** od `SKILL.md`, v jeho adresáři, a odkazuje se na ně **přímo z něj**. Odkaz na odkaz se čte jen zčásti – model si soubor namátkou prohlédne místo aby ho přečetl celý, a vezme si z něj polovinu.

**Soubor nad 100 řádků začíná obsahem**, ať je z náhledu vidět celý rozsah.

## 7. Jak se píše text uvnitř

**Nepiš, co model už ví.** Vysvětlovat, co je PDF, git nebo HTTP, je zbytečné. Ptej se u každého odstavce: *nese to informaci, kterou nemá?*

**Jedna doporučená cesta, ne výčet možností.** „Použij X; u zvláštního případu Y" je návod. „Můžeš X, nebo Y, nebo Z" je odklad rozhodnutí na horší chvíli.

**Ke každému pravidlu „proč".** Bez důvodu se pravidlo při prvním konfliktu obejde, protože nikdo neví, co se tím ztratí. `~/.claude/RULES.md`, *K pravidlům ukládej i „proč“* – totéž platí uvnitř skillu.

**Konkrétní příklad místo abstraktního.** Ne „ověř formát", ale ukázka správného a špatného tvaru.

**Šablona výstupu je zápis, ne pokyn k formátu.** Zpětné apostrofy okolo ní v `SKILL.md` jen oddělují šablonu od okolního textu – neříkají, že se má výstup vypsat jako blok kódu. Do konverzace jde běžný Markdown: tučné popisky místo dvojteček zarovnaných mezerami, řádky nezalomené natvrdo (`~/.claude/RULES.md`, *Styl odpovědí*). Šablona to musí uvádět výslovně, jinak model reprodukuje, co vidí, a vznikne z toho předformátovaná nudle zalomená kolem šedesáti znaků. Hlídá to test.

**Řada popisků pod sebou musí být odrážkový seznam.** V Markdownu není konec řádku zalomení, takže `**Kde:** …` a `**Co:** …` na dvou řádcích se vykreslí jako jedna slitá věta – tedy hůř než původní blok kódu, kde to zalomení aspoň drželo. Osamocený popisek oddělený prázdným řádkem odrážku nepotřebuje.

**Který blok kódu je šablona do konverzace** rozhoduje jeho první neprázdný řádek: nadpis, `[N/celkem]`, tučný popisek nebo řádek tabulky. Zadání pro subagenta začíná oslovením a příkaz shellu má u sebe jazyk, takže ani jedno sem nespadá. **Blok, jehož obsah se zapisuje do souboru** – sekce do `CLAUDE.md`, blok metadat, tabulka do `SKILL.md` – pokyn nemá; Markdown už je a pokyn by lhal o tom, kam text míří. Ty výjimky jmenovitě drží test.

**Neopisuj seznam, který má vlastní zdroj pravdy.** Pořadí kroků životního cyklu, prahy kontrol, inventář domén – na ty se odkazuj, nevypisuj je. Opsaný seznam se při přidání položky rozejde a **vypadá přitom pořád platně**, takže si toho nikdo nevšimne. Platí to dvojnásob pro **šablony, které skill zapisuje jinam**: `/project` psal do každého vývojářského `CLAUDE.md` cestu bez `/discovery` a projekty ji četly jako úplnou. Řetěz tří a víc kroků cyklu v `SKILL.md` hlídají testy. **Výjimku mají dvě místa v README skillu** (*README skillu*, níž): rámeček s cyklem, který ukazuje krajní kroky a mezi nimi výpustku, a šablona hromadné instalace, kde kroky stojí vyjmenované. Obojí míří na člověka, který sadu nezná a jinak by se o ní nedozvěděl, a obojí hlídá test proti `RULES.md`. **Opsaný seznam je vada tam, kde ho nikdo neměří** – ne tam, kde je sám předmětem kontroly.

**Žádné časově citlivé údaje.** Jména modelů, verze nástrojů a „nově od…" zestárnou tiše. Piš specialisty, ne jména – `~/.claude/RULES.md`, *Model a effort podle úkolu*, to dělá takhle.

**Česky**, podle `~/Dev/context/text/text.md` a `~/Dev/context/text/typography.md`. Anglicky zůstávají jen názvy souborů, příkazy a technické identifikátory.

**Nedeklaruj, co skill neumí.** Popsaný režim, který není implementovaný, je horší než chybějící funkce – uživatel se na něj spolehne. `~/.claude/RULES.md`, *Zapiš i to, co vědomě nemáš*: vědomá mezera se přiznává, ne zamlčuje.

## 8. Model, effort a delegace

Ve skillu se píše **jen delta** proti tabulce v `~/.claude/RULES.md`, *Model a effort podle úkolu* – tedy tam, kde se krok od výchozí volby odchyluje, a proč. Celou tabulku neopisuj.

Odchylku odůvodni **tím, čí vstup to je**: chyba v návrhu nebo v ověření nálezu se násobí do všeho, co po ní přijde, kdežto chyba v mechanickém sběru se pozná hned.

**Deleguj kvůli kontextu, ne kvůli úspoře.** Fan-out šetří kontext hlavní session, celkové tokeny spíš zvýší.

## 9. Ověřovací vrstva

**Pouští-li skill panel agentů, kteří hledají problémy, musí mít ověřovatele.** Není to volba. Agent požádaný o hledání mezer nějakou najde vždycky, a po třetím falešném nálezu se skill přestane pouštět – což je horší, než ho nemít.

Ověřovatel dostane jediný úkol: **nález vyvrátit**. Co ověření nepřežije, se uživateli vůbec nezobrazí.

**Nálezy nesou `severity` a `basis`.** Bez závažnosti se nedají seřadit, bez doložení ověřit.

**Skill, který něco tvrdí o výsledku, to tvrzení doloží.** Do souhrnu patří příkaz a jeho návratový kód, ne věta „testy procházejí". Co se nezkontrolovalo, se vypíše jako nezkontrolované.

## 10. README skillu

**Každý skill má vedle `SKILL.md` svůj `README.md`.** Má jediný účel, a ten je ostře vymezený: **člověk, kterému pošlu odkaz na GitHub, si přečte, co to je, proč je to dobré a jak si to nainstaluje k sobě.** Nic víc. Není to dokumentace skillu, není to shrnutí `SKILL.md` a nepíše se pro Clauda.

| | `SKILL.md` | `README.md` |
|---|---|---|
| Čtenář | Claude | člověk, který skill nezná |
| Povaha | normativní – *jak se to dělá* | popisný – *k čemu to je* |
| Obsah | fáze, kritéria, odchylky | přínos, možnosti, instalace |

### Co do README skillu nepatří

Vyhrává první kritérium, které sedí – a všechna vedou ven:

| Kdyby platilo | Kam to patří |
|---|---|
| Je to postup, kritérium nebo instrukce pro Clauda | **do `SKILL.md`.** |
| Je to obhajoba návrhového rozhodnutí | **do `SKILL.md`** k místu, kde platí, nebo do `~/Dev/context/decisions.md`. |
| Je to implementační detail – jméno přepínače, souboru, funkce, modelu, agenta | **nikam.** Čtenáře nezajímá a zestárne dřív než zbytek textu. |
| Je to historka z provozu, číslo z jednoho běhu, „poprvé jsem ho pustil a…" | **nikam.** |

**Poslední dva řádky jsou ty, na které se zapomíná.** Věta *„Když jsem ho poprvé pustil na vlastní práci, ze 43 nálezů tři nepřežily ověření"* není popis skillu, ale příběh o jednom běhu; *„Agent, který má hledat všechno, nenajde nic"* je obhajoba architektury. Ani jedno čtenáři neřekne, k čemu ten skill je.

### Jak se to překládá do lidské řeči

Odborný termín se nahrazuje tím, co znamená, a mechanika tím, co z ní čtenář má:

| Ne | Ano |
|---|---|
| „předává slovník přes `--prompt`" | „připraví si seznam jmen a termínů z nahrávky a podstrčí ho rozpoznávači, takže je pak nekomolí" |
| „diarizace" | „rozliší mluvčí" |
| „paralelní fan-out agentů s ověřovací vrstvou" | „pošle na práci několik nezávislých pohledů a každou námitku pak nechá zkusit vyvrátit" |

Pravidlo *Nepiš, co model už ví* z odstavce **Jak se píše text uvnitř** tady **neplatí** – čtenář README není model a ví míň, ne víc.

### Struktura

```
# /jméno – <co to je, jednou větou>

<jen u skillu ze životního cyklu: rámeček s celým životním cyklem – viz Skill ze životního cyklu níž>

<úvodní odstavec: 3–5 vět, k čemu to je a komu se to hodí>

## Co umí
## Proč zrovna tenhle
## Jak se to používá
## Ukázka výstupu        ← jen má-li skill hmatatelný výstup
## Co nedělá
## Jak si ho nainstalovat

---
### Požadavky a omezení
```

**`## Co umí`** – odrážky nebo číslovaný seznam. **Všechny režimy a varianty**, každý jednou větou, plus podstatná omezení rozsahu (na co se skill pouští, kde běžet nemá). Ne převyprávěné fáze.

**`## Proč zrovna tenhle`** – heslovité odrážky, čím se liší od zřejmé alternativy: od ručního postupu, od obecného promptu, od nástroje, který dělá totéž hůř. **Neuvádí se, s čím se to poměřovalo** – jen výsledek jako vlastnost. Je to nejdůležitější sekce README, protože kvůli ní si to čtenář vezme.

**`## Jak se to používá`** – dva až čtyři řádky: skutečné zavolání a co se stane. Ne návod krok za krokem.

**`## Ukázka výstupu`** – kus reálného výsledku. Zakládá se jen tam, kde skill něco vyrábí (přepis, report, faktura, plán); u skillu, jehož výstupem je konverzace, se vynechá. Nejpřesvědčivější sekce ze všech – z popisu si výsledek nikdo nepředstaví.

**`## Co nedělá`** – dvě až čtyři odrážky, lidský překlad `## Co skill nedělá` ze `SKILL.md`. Šetří zklamání i dotazy.

**`## Jak si ho nainstalovat`** – **napsané jako pokyn, který člověk předá svému Claudovi**, ne jako postup, který si odklikává sám. Nikdo si dnes skill neinstaluje ručním kopírováním adresáře; řekne si o to. Tvar je tedy citovaný prompt s odkazem do repozitáře:

```
> Jdi na https://github.com/jantichy/claude/tree/main/skills/<jméno>
> a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.
```

Pod ním jedna dvě věty o tom, co je ještě potřeba doplnit. **Opírá-li se skill o něco, co v repozitáři není, řekne se to rovnou tady**, ne až v poznámce pod čarou – jinak si to člověk nainstaluje a ono to nefunguje.

**`### Požadavky a omezení`** pod čarou – platforma, nástroje, účty, licence, cena, meze. Krátce a úplně.

### Skill ze životního cyklu

**Stojí-li skill v *Životním cyklu projektu*** (`~/.claude/RULES.md`), začíná jeho README **rámečkem s celým životním cyklem** – hned pod nadpisem, ještě před úvodním odstavcem. Čtenář, kterému přišel odkaz na jeden skill, jinak nemá jak zjistit, že jich je celá řada a že spolu drží.

**Znění je doslova stejné ve všech**, liší se jen tím, který krok je tučný. **Počet kroků se v něm neuvádí číslovkou** – ta se při přidání dalšího kroku rozejde ve všech rámečcích naráz a nic ji nehlídá; čtenář si počet spočítá ze šipek pod tím:

```
> **Součást životního cyklu projektu.** Tenhle skill patří do ucelené sady skillů, které vedou práci
> od založení projektu až po nasazení. Každý má svůj krok a žádný nedělá práci toho vedle:
>
> [`/project`](../project/README.md) → … → **`/jméno`** → … → [`/release`](../release/README.md)
>
> Projít se nemusí celý – u drobné změny odpadá zadání i plán, u projektu bez kódu nasazení.
```

Aktuální skill je **tučně a bez odkazu**, ostatní odkazem na jejich README. Rozejde-li se pořadí se životním cyklem v `RULES.md`, platí `RULES.md` – rámeček je jeho zobrazení, ne druhý zdroj pravdy.

**Sekce `## Jak si ho nainstalovat` má u skillu ze životního cyklu druhý odstavec** s hromadnou instalací celé sady, opět doslova stejný ve všech:

```
**Nebo celou sadu naráz.** Chcete-li místo jednoho skillu rovnou celý životní cyklus, napište mu tohle:

> Jdi na https://github.com/jantichy/claude/tree/main/skills a nainstaluj mi do
> `~/.claude/skills/` celý životní cyklus: project, discovery, specify, oponent, breakdown,
> implement, review, consistency, cleanup, attack a release. U každého si přečti README
> a řekni mi, co k nim potřebuju doplnit.
```

**Skilly mimo životní cyklus rámeček ani hromadnou instalaci nemají.** Pouštějí se samostatně a předstírat u nich sadu by mátlo.

### Meze

**Do 120 řádků.** Je to zhruba dvě obrazovky – tolik člověk přečte, než se rozhodne, jestli ho to zajímá. Co se tam nevejde, patří do `SKILL.md`, kde to čte Claude, a ne do README. Mez je jediná a hlídá ji test; „nesmí být delší než `SKILL.md`" jako druhé kritérium neplatí – u krátkého skillu by povolilo README, které už nikdo nedočte.

**Česky**, podle `~/Dev/context/text/text.md` a `~/Dev/context/text/typography.md`. Anglicky zůstávají jen jména režimů, příkazy a technické identifikátory.

**Neodkazuje dovnitř `SKILL.md`.** Odkaz na fázi je odkaz do vnitřku, který se přečísluje; odkaz na `SKILL.md` jako celek je v pořádku.

### Sekce v hlavním README repozitáře

Skill má navíc **jeden odstavec** v `README.md` v kořeni. Platí pro něj totéž co výš, jen ještě stručněji: **k čemu ten skill je, případně velice stručně, co dělá.** Ne dva odstavce, ne tři.

**Na podrobné README se odkazuje nadpisem**, ne řádkem pod odstavcem:

```
### [`/jméno`](skills/jméno/) – <k čemu to je, půl věty>
```

Odkaz míří na **adresář skillu**, protože GitHub v něm `README.md` rovnou vypíše. Zvláštní řádek „Podrobně: …" by tedy vedl na totéž místo dvakrát.

**Pořadí skillů v hlavním README je dané, ne libovolné.** Skilly ze životního cyklu stojí v pořadí, ve kterém se v životním cyklu pouštějí – ne abecedně a ne podle důležitosti; čtenář ten seznam čte jako postup. Skilly mimo životní cyklus stojí **pod nimi a abecedně** – žádné pořadí mezi nimi neplatí, takže cokoliv jiného než abeceda by tvrdilo něco, co není pravda, a při přidání dalšího skillu by se muselo rozhodovat znovu.

**Obě README se aktualizují spolu se skillem**, ne na vyžádání. Změní-li se, co skill umí, je to součást té změny – stejně jako hlavička nebo test.

------

## Co se nepřebírá zvenčí

`superpowers:writing-skills` i `skill-creator` mají vlastní představu o tvaru skillu a obě se od téhle liší. **Tvar je vždycky odsud**; cizí nástroje se volají na měření a vytěžení, ne na rozhodnutí, jak má skill vypadat. Podrobně `/skill`, *Jak je to postavené uvnitř*.
