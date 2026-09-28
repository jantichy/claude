# /consolidate – hledá dluh, který vznikl postupným lepením

> **Součást životního cyklu projektu.** Tenhle skill patří do ucelené sady skillů, které vedou práci od založení projektu až po vyhodnocení provozu. Jedny tvoří, druhé se starají o to, co už vzniklo – a žádný nedělá práci toho vedle:
>
> **Osa** [`/project`](../project/README.md) → [`/discovery`](../discovery/README.md) → [`/specify`](../specify/README.md) → [`/architect`](../architect/README.md) → [`/breakdown`](../breakdown/README.md) → [`/implement`](../implement/README.md) → [`/release`](../release/README.md) → [`/evaluate`](../evaluate/README.md)
>
> **Kontroly** [`/oponent`](../oponent/README.md) · **`/consolidate`** · [`/review`](../review/README.md) · [`/consistency`](../consistency/README.md) · [`/attack`](../attack/README.md) · [`/cleanup`](../cleanup/README.md) · [`/merge`](../merge/README.md) – stojí v mezerách mezi kroky osy, některé z nich ve víc mezerách
>
> Projít se nemusí celý – u drobné změny odpadá zadání i plán, u projektu bez kódu nasazení i vyhodnocení provozu.

Návrh se obvykle nerodí naráz. Vede se po kolech, v každém vyplave další případ, na který se přidá sloupec nebo další hodnota do výčtu – a každý ten krok je ve své chvíli správný. Po půl roce z nich ale bývá řešení, které by se při znalosti všech případů předem dalo nahradit jedním jednodušším. Tenhle skill takové shluky hledá, navrhne k nim alternativu a pak ji nechá někoho zkusit rozbít, aby se z úklidu nestala regrese. Hodí se před rozpadem velkého celku do úkolů a kdykoli vám leží v hlavě, že jste to měli udělat jinak.

## Co umí

1. **Přečte historii, ne dnešní stav.** Vychází ze zápisů o tom, co se kdy rozhodlo, z historie verzí a ze zamítnutých připomínek. Shluk záplat se pozná z dat jejich narození – z hotového dokumentu to vidět není, protože tam všechny mechanismy stojí vedle sebe jako rovnocenné.
2. **Jde adresně po čtyřech vzorech.** Po jednom poli, kterým se postupně řešily různé věci, až odpovídá na víc otázek naráz; po téže situaci řešené pokaždé jiným způsobem; po řetězu oprav, kde si každá vynutila další; a po slepých místech, ze kterých vede ven vždycky jen další podmínka.
3. **Dostopuje řetěz na první článek.** Neopravuje poslední záplatu, ale říká, co se mělo rozhodnout na začátku, aby těch pět navazujících nebylo potřeba.
4. **Ke každému návrhu vypíše, co dnešek zvládá a čím to zvládne nová varianta.** Bez toho výpisu se návrh vůbec nepředloží.
5. **Nechá každý návrh zkusit vyvrátit** někým, kdo ho nepsal a má za úkol ho položit.
6. **Vedlejší vady hlásí zvlášť.** Při ověřování obvykle vypadnou skutečné chyby v dnešním řešení – ty jdou ven jako normální nálezy se závažností.
7. **Umí skončit tím, že není co přepisovat.** Je to plnohodnotný výsledek, ne nepovedený běh.

## Proč zrovna tenhle

- **Ptá se jako jediný „bylo by to dnes navržené jinak?“.** Ostatní kontroly se ptají „je to špatně?“ – a na tuhle otázku zní odpověď „ne“, takže dluh propadne každým jiným sítem.
- **Čím poctivěji se záplata zanesla všude, tím je neviditelnější.** Kontrola hledající rozpory tenhle dluh nenajde nikdy, protože je dokonale bezrozporný.
- **Nevyrábí regrese převlečené za úklid.** Kdo dostane zadání „navrhni to elegantněji“, vždycky něco navrhne – a bude to působit čistěji právě proto, že nezná zatáčky, kvůli kterým dnešní řešení vzniklo. Proti tomu stojí povinná zpětná zkouška: každý doložený případ z minulosti se projde položku po položce.
- **Nepřepisuje zadání.** Otevřít znovu se smí rozhodnutí o tom, jak se něco udělalo. Nikdy o tom, co se má dělat – rozsah funkcí ani obchodní pravidlo jsou pro něj vstup.
- **Dřívější zamítnutí není argument.** Ani vaše. Kdo chce návrh položit, musí jmenovat, co konkrétně se rozbije – jinak by skill jen potvrzoval, že co je rozhodnuté, je rozhodnuté.

## Jak se to používá

```
/consolidate gateway
```

Argument je **výchozí bod, ne hranice výsledku**: „vyjdi ze záplat kolem platební brány“, ne „výsledek se smí týkat jen brány“. Právě ten rozdíl rozhoduje – nález „ten sloupec je zbytečný“ ušetří sloupec, kdežto nález „celý stavový prostor je vedený podle špatné osy“ ušetří celý shluk. Bez argumentu si výchozí bod najde sám tam, kde se nakupilo nejvíc rozhodnutí v nejkratším čase.

Pak rozešle několik nezávislých pohledů na sběr podkladů, sám nad nimi vyznačí shluky a napíše návrhy, nechá je zkusit vyvrátit a s tím, co přežije, za vámi přijde jeden po druhém.

## Ukázka výstupu

**Návrhový dluh prověřen**

- **Výchozí bod:** platební brána · **Shluků:** 3
- **Návrhy:** 2 předloženy, 0 přežilo ověření, 0 přijato
- **Vedlejší vady:** 2 (1 střední, 1 nízká)
- **Agenti:** 5 celkem, z toho 2 ověřovatelé

U obou shluků má každá záplata doložený důvod a navržená alternativa neunesla případ, kvůli kterému dnešní řešení vzniklo. Cennější je to, co vypadlo mimochodem: při ověřování se ukázalo, že jeden ze stavů nemá pokrytý návrat z nedokončené platby.

## Co nedělá

- **Neměří kód proti zadání** a nehledá chyby v implementaci – dluh, který hledá, je v samotném zadání a kód ho plní poslušně.
- **Neposuzuje, jestli je návrh dobrý** tak, jak stojí dnes. Zajímá ho výhradně to, jak vznikal.
- **Nic nepřepisuje ani neimplementuje.** Vrací návrh a odhad, kolik by přepis stál; co se s tím stane, rozhodujete vy.
- **Nepouští se po každé změně.** Je drahý a jeho nález je vždycky velký přepis – v prvním kole návrhu nemá co najít.

## Jak si ho nainstalovat

Řekněte svému Claudovi:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/consolidate
> a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.
> Z https://github.com/jantichy/claude/tree/main/agents k tomu vezmi
> i definice typů subagentů do `~/.claude/agents/`.

Skill se opírá o to, že projekt někde vede zápisy o svých rozhodnutích – bez nich nemá z čeho postavit kroniku a zbude mu jen historie verzí. Odkazuje se i na moje soukromé standardy pro strukturu projektu a pro škálu závažnosti nálezů; ty odkazy ať Claude nahradí vašimi, nebo je smaže.

**Nebo celou sadu naráz.** Chcete-li místo jednoho skillu rovnou celý životní cyklus, napište mu tohle:

> Jdi na https://github.com/jantichy/claude/tree/main/skills a nainstaluj mi do `~/.claude/skills/` celý životní cyklus: project, discovery, specify, architect, breakdown, implement, release, evaluate, oponent, consolidate, review, consistency, attack, cleanup a merge. Z https://github.com/jantichy/claude/tree/main/agents k tomu vezmi i definice typů subagentů do `~/.claude/agents/`. U každého si přečti README a řekni mi, co k nim potřebuju doplnit.

---

### Požadavky a omezení

Git kvůli čtení historie – bez něj skillu zbude jen to, co je zapsané v dokumentaci, a přijde o zdůvodnění ze zpráv commitů. Projekt musí vést evidenci rozhodnutí; nad projektem bez ní se skill rozjede, ale kronika bude chudá a řekne to. Běh je drahý: rozesílá tři až pět nezávislých pohledů a ke každému návrhu ještě jeden ověřovací, ten na nejsilnějším modelu. Pouští se nad sloučeným stavem, ne nad rozdělanou větví.
