# Jak se píše skill

Norma tvaru vlastních skillů v `~/.claude/skills/`. Definuje, **co je skill a jak vypadá**; postup, kterým se zakládá, reviduje a ruší, drží `/skill`. Je to týž vztah jako mezi `~/Dev/context/structure/structure.md` a `/project` – standard říká, jak to má vypadat, nástroj je jen instalátor.

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
| Chytne to typecheck, linter, test nebo hook | **do té brány.** `~/.claude/RULES.md`, *Model a effort podle úkolu*, pravidlo nula: nejlevnější práce je ta, kterou neudělá model. Mechanické omezení zapsané do skillu se dodržuje hůř a stojí tokeny při každém běhu. |
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
| **Vnitřek** | delegace ven | kdykoliv, bez ohlášení |

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

**Režimy se jmenují anglicky, jedním slovem, malými písmeny** – a **lícují napříč skilly**: co dělá totéž, jmenuje se stejně. Ustálená sada je `create`, `update`, `delete`; k ní podle potřeby další jednoslovné (`extract`, `full`). Výchozí režim se vyjmenovává taky, aby ho šlo napsat explicitně.

**Proč anglicky:** je to jméno akce, ne řeč o ní. České „revize" se skloňuje, píše se s diakritikou a v `argument-hint` vypadá jako věta; `update` je token. Česká podstatná jména v próze („výsledek revize") zůstávají česky – rozdíl je mezi **jménem režimu** a mluvením o něm.

**Proč lícovat:** dva skilly, které dělají tutéž věc pod jiným jménem, nutí uživatele pamatovat si, který má který. Platí to i pro režimy, které se **rozpoznávají samy** a nepředávají se argumentem – uživatel je vidí ve výpisu a pojmenovává je v řeči stejně.

**`argument-hint` musí sedět s tělem.** Režim popsaný v těle a chybějící v hintu uživatel nikdy neuvidí; hint bez opory v těle slibuje funkci, která neexistuje.

**`allowed-tools` drž na minimu.** Dlouhé ruční výčty nástrojů MCP jsou křehké – při přejmenování serveru se rozejdou tiše a skill pak selže až za běhu.

## 4. Povinné sekce a jejich pořadí

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

**Tohle pořadí platí pro hlavní průběh.** Má-li skill **přílohové sekce** – samostatné režimy, katalog úhlů nebo vektorů –, stojí **za** závěrečnou fází: nejsou její součástí a čtenář se k nim dostane jen tehdy, když je potřebuje. `## Časté chyby` je pak úplně poslední, aby stála za vším, k čemu se vztahuje:

```
## Fáze N – Závěr        ← konec hlavního průběhu
## Režim <jméno>         ← příloha
## Časté chyby           ← naposled
```

U lineárního skillu bez příloh se nic nemění a `## Časté chyby` zůstávají před závěrem.

**`## Co skill dělá`** – co to je a jaké má režimy. Tři až deset řádků. Ne převyprávěný postup; ten je níž.

**`## Co skill nedělá`** – vymezení proti **jmenovaným** sousedům, ne obecná negace. „Nepíše kód" je bezcenné; *„Neaudituje projekt. Na vnitřní konzistenci je `/consistency`."* je vymezení. U skillu, který stojí v ose *Životního cyklu práce* (`~/.claude/RULES.md`), je tahle sekce povinná a musí jmenovat sousedy z obou stran – bez ní se práce buď zdvojí, nebo neudělá vůbec.

**`## Jak je to postavené uvnitř`** – jen deleguje-li skill na cizí nástroj. Řekne, co volá, **a výslovně že je to implementační detail, ne rozhraní**, plus co je naopak závazné a nesmí se změnit tiše. Viz *Skládej, nepiš znovu*.

**`## Fáze 0 – Pre-flight`** – odkaz na `~/.claude/skills/PREFLIGHT.md` a **jen odchylky tohohle skillu**. Nikdy sem neopisuj obsah odtamtud.

**`## Fáze 1..N`** – vlastní postup.

**`## Časté chyby`** – nepovinná, ale zakládej ji, jakmile má skill za sebou první ostré běhy. Patří sem to, co se v praxi pokazilo, ne co by se pokazit mohlo. Zdroj je `docs/decisions.md` a poučení z běhů; bez téhle sekce se do skillu nikdy nevrátí.

**`## Fáze N – Závěr`** – **poslední** fáze skillu; nese šablonu výstupu a **dvě koncové věty**. Jméno po pomlčce **závazné není** – `Úklid a shrnutí`, `Uzavření` i `Předání` jsou v pořádku, závěr se pozná podle toho, že je poslední. Naopak **`Fáze 0` je závazná číslem**: pre-flight je vždycky nultý, ať se jmenuje jakkoliv (`/oponent` má „Fáze 0 – Co se oponuje“, `/project` „Krok 0 – Zjisti režim a stav“):

Skill je **uvádí doslovně**, aby se z nich za běhu nestala parafráze. Jejich znění si ale volí sám – **doslovná napříč skilly být nemůžou**, protože čeština žádá shodu s rodem toho, co je hotové (*„Plán hotový není"* × *„Hotové to není"*). Závazný je tedy vzorec:

1. **První** říká, že věc je hotová a ověřená, a čím se dá pokračovat.
2. **Druhá** říká, že hotová není, a **jmenuje konkrétně, co tomu brání** – ne „ještě zbývá pár věcí".
3. **Mezi nimi nic není.** Žádná třetí varianta, žádné smířlivé „v zásadě hotovo".

```
Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `<Věc> je hotová a ověřená, můžeš …`
- `<Věc> hotová není – brání tomu: <konkrétní seznam>.`
```

Skill s vlastním koncem pro některý režim (rušení, zamítnutí) smí mít druhou dvojici, ale musí splňovat týž vzorec.

Ty dvě věty jsou celá bezpečnostní pojistka skillu: nutí odlišit „udělal jsem kroky" od „výsledek platí". Bez nich končí každý běh smířlivým odstavcem, ze kterého nejde poznat, jestli se dá pokračovat.

## 5. Číslování a názvosloví

**„Fáze" je norma.** Číslují se od nuly (`Fáze 0 – Pre-flight`) a čísla se nemění bezdůvodně – odkazuje se na ně napříč skilly.

**Číslují se plochou vzestupnou řadou, bez písmen.** `0, 1, 2, 3…`, ne `1, 1b, 2`. Čtenář bere číslování jako tvrzení o vztazích, takže `1b`, které o vztahu k `1` nic neříká, lže.

**Písmenná podfáze je v souladu jen tam, kde sdružuje tematicky příbuzné podkroky téhož kroku.** Kritérium je ostré: písmena jen tehdy, když by jinak jeden krok musel vyrábět **dva samostatné výstupy**. Tak to má `/specify` s `Fází 3a` (produktová specifikace) a `3b` (návrh řešení) – dva dokumenty jednoho zadání.

Není to výjimka, ale splněné kritérium: co mu vyhoví, revize nesahá; co mu nevyhoví, je nedodělek a **opraví se**.

**„Krok" jen u interaktivních průvodců**, kterými uživatel prochází jeden po druhém a může se kdykoliv zastavit. Dnes je to `/project`. Skill, který volí „krok", to musí ve svých zásadách zdůvodnit.

**Neodkazuj se dovnitř jiného skillu.** Potřebuješ-li tentýž postup jako soused, patří ten postup do `PREFLIGHT.md` nebo do doménové znalosti – ne do odkazu na jeho fázi. Cizí fáze se přečíslují a odkaz tiše ukáže jinam.

**Jeden termín pro jednu věc** (`~/.claude/RULES.md`, *Jeden termín pro jednu věc*). Ve skillech to platí navíc **napříč nimi**, ne jen uvnitř jednoho: skilly se čtou jeden po druhém v jedné ose a rozdílné pojmenování téhož kroku vypadá jako rozdílný krok.

## 6. Délka a progresivní odhalení

| Mez | Co dělat |
|---|---|
| do 300 řádků | v pořádku |
| 300–500 řádků | zvaž rozdělení, řekni to při revizi |
| nad 500 řádků | **rozděl** |

Tělo `SKILL.md` se načte celé, jakmile se skill vyvolá – včetně větví, které v tom běhu neplatí. Kontext, který tím spotřebuješ, chybí na vlastní práci.

**Co se vytahuje do vedlejších souborů:** zadání pro agenty, katalogy úhlů a vektorů, dlouhé referenční tabulky, šablony výstupů, skripty.

**Vedlejší soubory leží jednu úroveň hluboko** od `SKILL.md`, v jeho adresáři, a odkazuje se na ně **přímo z něj**. Odkaz na odkaz se čte jen zčásti – model si soubor namátkou prohlédne místo aby ho přečetl celý, a vezme si z něj polovinu.

**Soubor nad 100 řádků začíná obsahem**, ať je z náhledu vidět celý rozsah.

## 7. Jak se píše text uvnitř

**Nepiš, co model už ví.** Vysvětlovat, co je PDF, git nebo HTTP, je zbytečné. Ptej se u každého odstavce: *nese to informaci, kterou nemá?*

**Jedna doporučená cesta, ne výčet možností.** „Použij X; u zvláštního případu Y" je návod. „Můžeš X, nebo Y, nebo Z" je odklad rozhodnutí na horší chvíli.

**Ke každému pravidlu „proč".** Bez důvodu se pravidlo při prvním konfliktu obejde, protože nikdo neví, co se tím ztratí. `~/.claude/RULES.md`, *K pravidlům ukládej i „proč“* – totéž platí uvnitř skillu.

**Konkrétní příklad místo abstraktního.** Ne „ověř formát", ale ukázka správného a špatného tvaru.

**Žádné časově citlivé údaje.** Jména modelů, verze nástrojů a „nově od…" zestárnou tiše. Piš role, ne jména – `~/.claude/RULES.md`, *Model a effort podle úkolu*, to dělá takhle.

**Česky**, podle `~/Dev/context/text/text.md`. Anglicky zůstávají jen názvy souborů, příkazy a technické identifikátory.

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

------

## Co se nepřebírá zvenčí

`superpowers:writing-skills` i `skill-creator` mají vlastní představu o tvaru skillu a obě se od téhle liší. **Tvar je vždycky odsud**; cizí nástroje se volají na měření a vytěžení, ne na rozhodnutí, jak má skill vypadat. Podrobně `/skill`, *Jak je to postavené uvnitř*.
