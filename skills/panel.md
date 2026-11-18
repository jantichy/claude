# Panel s ověřením

Společná mechanika skillů, které pošlou na dokument panel agentů bez kontextu session a jejich nálezy nechají vyvrátit dřív, než je ukážou uživateli – `/oponent` a `/legal`. Skill se sem odkazuje a u sebe drží jen to, co má vlastní: katalog hledisek, zadání pro člena panelu, odchylky v typu agenta a místo, kam ukládá ověřený seznam.

- [Co do tohoto souboru nepatří](#co-do-tohoto-souboru-nepatří)
- [Inventura předmětu](#inventura-předmětu)
- [Spuštění panelu](#spuštění-panelu)
- [Ověření nálezů](#ověření-nálezů)
- [Konsolidace](#konsolidace)
- [Ověřený seznam na disku](#ověřený-seznam-na-disku)

## Co do tohoto souboru nepatří

- **Katalog hledisek a zadání člena panelu** – nesou doménu skillu, takže patří do něj.
- **Kdo o nálezu rozhoduje, jak vypadá jeho výpis a jak jde průchod** – `~/.claude/skills/findings.md`.
- **Škála závažnosti** – `~/.claude/skills/severity.md`.
- **Panel `/review`** – ten měří proti pravidlu a pouští vlastní specialisty i nástroje; jeho mechaniku drží on sám.

## Inventura předmětu

**Než pustíš panel, vyrob si inventuru předmětu příkazem** – u Markdownu nadpisy (`grep -n '^#' <cesty>`), u smlouvy články nebo body, jak je dokument čísluje – a **zapamatuj si jejich počet**. Proti němu se v *Konsolidaci* vykazuje, kolik z předmětu který člen panelu doopravdy prošel. Neodhaduj to (`~/.claude/standards/rules.md`, *Hodnotu, kterou čte stroj, nepiš – nech ji vyrobit příkazem*).

**Proč:** zadání „přečti dokument celý“ nic neměří – a posudek, který pokryl třetinu předmětu, vypadá stejně věrohodně jako úplný, protože nálezy v něm jsou pravé; chybí jen ty ostatní.

## Spuštění panelu

Pusť členy panelu **paralelně, jedním voláním s víc tool calls**. Každý dostane vlastní hledisko a **žádný kontext z téhle session** – to je celý smysl.

**Kontext projektu dostane cestou k souboru, ne opsaný.** Agent si ho přečte z disku sám, v okamžiku běhu. Opis do zadání je snímek a rozejde se se souborem, který se mezitím změnil – posudek pak hájí verzi, kterou už nikdo nemá.

**Nejsilnější model, `xhigh`** (`~/.claude/standards/delegation.md`, *Model a effort podle úkolu*). Posudek je verifikace, ne sběr: slabý model námitku nevymyslí ani neobhájí, jen zdvořile přizvukuje tomu, co má před sebou – a posudek, který všechno schválí, je horší než žádný, protože dodá falešnou jistotu.

**Typ agenta** volí skill podle svého katalogu; výchozí je `reader`, s rešerší na webu `researcher` (`~/.claude/skills/skills.md`, *Model, effort a delegace*). Oba nemají shell, takže do dokumentu nesáhnou.

**Zadání člena panelu** píše skill, ale vždycky v něm stojí tohle:

- **Úvodní řádek `PROŠEL JSEM: <části, které opravdu přečetl>`** – jmenovitě, ne „vše“. Neúplný posudek je platný výsledek, zamlčeně neúplný ne. Nenašel-li nic, je to stejně platný výsledek jako nález, ale ten řádek napíše i tak: bez něj se prázdný posudek nedá odlišit od toho, že agent spadl.
- **U každého nálezu kde, co, proč to vadí, návrh a závažnost.** *Kde* je místo v dokumentu, ideálně citace; *proč to vadí* je konkrétní důsledek, ne obecná obava; *návrh* jsou dvě až tři varianty, nebo přiznání, že řešení nemá a jde o otázku k rozhodnutí; *závažnost* podle `~/.claude/skills/severity.md`.
- **Hledá výhradně ze svého hlediska** a k ostatním nepřebíhá – pokrývají je jiní.
- **Co je v pořádku, nepíše.** Žádné shrnutí kladů.
- **Nenavrhuje znovu, co je vědomě zamítnuté** – v `decisions.md` nebo v bloku *Vědomě zamítnuté* zadání –, leda výslovně jako revizi rozhodnutí se zdůvodněním, který jeho předpoklad neplatí.
- **Neopírá nález o neověřené tvrzení.**

## Ověření nálezů

**Nálezy z panelu nejsou závěry, ale tvrzení.** Člen panelu bez kontextu vyrobí i nález, který stojí na tom, co nemohl vědět – a nález, který nevyrobí nic, vypadá jako selhání běhu, takže tlak na produkci je vestavěný. Kdyby se falešné vyřazovaly až v konsolidaci, dělal by to spoluautor, tedy ten jediný aktér, jehož slepotu má panel obcházet.

**Deduplikuj ještě před ověřením**, ne až po něm: tři ověřovatelé na jednu věc jsou trojnásobná cena za tutéž odpověď. **Dva nálezy jsou tentýž**, když míří na totéž místo dokumentu a navrhují změnit touž věc – formulace i závažnost se lišit můžou. Sloučený nález si ponech v obou zněních a poznamenej, která hlediska ho našla; je to signál závažnosti.

Na každý nález se závažností **KRITICKÉ a STŘEDNÍ** pošli **samostatného ověřovatele** – paralelně, v čerstvém kontextu, který nevidí ani panel, ani tvou konverzaci. **Nejsilnější model, `xhigh`**, i u nálezu z levného hlediska: slabý ověřovatel nález nepotvrdí ani nevyvrátí, jen přizvukuje, a z ověření se stane razítko.

**Typ ověřovatele podle toho, na čem nález stojí:** opírá-li se o vnější zdroj (URL, dokumentace, ceník, předpis), nebo přišel-li z hlediska s rešerší, jede na `researcher`; jinak na `reader`. Nález o vnějším faktu by `reader` bez webu vrátil jako NEOVĚŘITELNÉ a ověření by tiše odpadlo právě u tvrzení, která autor dokumentu sám ověřit nejde. Skill smí určit přísnější typ, potřebuje-li doklad, který ani `researcher` nedá.

**Strop: nejvýš 12 ověřovatelů na běh.** Bez něj roste nejdražší část běhu lineárně s počtem nálezů. Přes strop se ověřují **nejdřív všechny KRITICKÉ**, teprve pak STŘEDNÍ; co se nevejde, jde do průchodu označené jako **`neověřeno`** a spočítá se v souhrnu. Tiché vynechání ne – neověřený nález se od ověřeného musí poznat.

**Ověřovatel má tentýž kontext jako panel** – to není jeho výhoda. Rozdíl je jinde: **nemá zadané hledisko**, a tím ani tlak nález vrátit. Člen panelu, který nic nenajde, vypadá jako selhání; ověřovatel, který nález vyvrátí, odvedl práci. Ta asymetrie je celý mechanismus.

```
Ověřuješ jedno tvrzení nezávislého posudku. Nemáš kontext z předchozích rozhovorů.

DOKUMENT: <absolutní cesty>
KONTEXT PROJEKTU: <cesty k souborům – přečti je z disku>
VĚDOMĚ ZAMÍTNUTÉ V TÉHLE PRÁCI: <výčet i s důvody>
<další řádky rámce, které skill předává celému panelu>

NÁLEZ K OVĚŘENÍ: <kde, co, proč to vadí, návrh, závažnost>

Tvůj úkol není nález potvrdit, ale pokusit se ho vyvrátit. Ptej se:
- Stojí na tom, co v dokumentu doopravdy je? Ověř citaci.
- Opírá-li se o vnější zdroj, říká ten zdroj opravdu, co nález tvrdí? Otevři ho, nehádej.
- Neřeší to dokument někde jinde, kde se posudek nedíval?
- Neplyne z kontextu projektu, že to tak je schválně?
- Je důsledek doložený, nebo je to obecná obava?
- Sedí navržená závažnost, nebo je nafouknutá?

Vrať: POTVRZENO / VYVRÁCENO / PŘEKVALIFIKOVÁNO NA <závažnost> / NEOVĚŘITELNÉ, jednou
větou proč, kde <závažnost> je jen KRITICKÉ, STŘEDNÍ nebo NÍZKÉ – jinou škálu
nepoužívej, a u vyvráceného doklad – citaci z dokumentu, kontextu nebo zdroje, která ho boří.
NEOVĚŘITELNÉ vrať, stojí-li nález na faktu, který v dokumentu ani kontextu není a nedá se
dohledat, a napiš, co chybí – je to stejně platná odpověď jako vyvrácení.

Do žádného souboru nezapisuj.
```

**NEOVĚŘITELNÉ jde do průchodu jako `neověřeno`**, stejně jako nález nad stropem – nezahazuje se ani nepotvrzuje.

**NÍZKÉ nálezy se neověřují** – ne kvůli ceně, ale protože se nevypořádávají jednotlivě: jdou na konci jedním blokem, takže na nich nestojí rozhodnutí, které by ověření chránilo. **Vyvrácené zahoď a spočítej je do souhrnu**; kolik jich bylo, se říká nahlas.

**Výsledky ověření hlas obsahem, ne značkou.** Identifikátory, pod kterými se nálezy vracejí od agentů, uživatel nikdy neviděl (`~/.claude/standards/rules.md`, *Interní značky ven nepatří*).

## Konsolidace

**Nejdřív pokrytí, teprve pak nálezy.** U každého člena panelu si z úvodního řádku vezmi, co prošel, a porovnej s inventurou. **Posudek bez toho řádku není čistý výsledek, ale selhání běhu** – pusť ho znovu, a nepovede-li se to podruhé, řekni nahlas, že jeho pokrytí není doložené. Hledisko, které prošlo výrazně méně než ostatní, **uveď v přehledu jmenovitě**: jeho mlčení nic netvrdí.

Pak nálezy:

1. **Duplicity už jsou sloučené** – zůstává poznamenat, že nález našla dvě hlediska nezávisle.
2. **Vyvrácené vyřadil ověřovatel, ne ty.** Sám nefiltruj: nález, u kterého máš pochybnost, ale ověřením prošel, předlož s poznámkou. Tichý filtr je přesně to, co má panel obcházet.
3. **Vyřaď už rozhodnuté.** Nález, který navrhuje zamítnutou variantu bez nového argumentu, zahoď a **řekni, kolik jsi jich zahodil a proč**.
4. **Seřaď podle závažnosti**, ne podle pořadí v dokumentu.
5. **Vypiš přehled** – všechny nálezy jednou větou, očíslované, se závažností. Uživatel musí vidět, co ho čeká, než se ho začneš ptát. **Přehledem ale odpověď nekonči** – první otázka průchodu jde v téže odpovědi (`~/.claude/skills/findings.md`, *Ohlášená akce patří do téže odpovědi*).

## Ověřený seznam na disku

**Hotovou frontu ulož na disk dřív, než začne průchod**, a průběžně do ní zapisuj stav každého nálezu (`accepted`, `rejected`, `deferred`, `open`). Kam, určuje skill.

**Proč to není zdržení:** ověřený seznam je nejdražší artefakt celého běhu – stojí panel i ověřovatele na nejsilnějším modelu. Průchod s ním pak dlouze pracuje v hlavní session, tedy přesně tam, kde kontext dochází nejrychleji, protože do něj natekly výstupy všech agentů. Bez zápisu znamená kompaktace uprostřed průchodu, že se celý běh platí znovu.

**Na startu se proto podívej, jestli seznam z přerušeného běhu neexistuje**, a nabídni navázání dřív, než začneš cokoliv počítat znovu – i s tím, kolik nálezů zbývá. Změnil-li se mezitím posuzovaný dokument, řekni to: část nálezů může být neaktuální.
