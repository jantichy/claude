---
name: oponent
description: Skill se použije, když uživatel zadá "/oponent", nebo chce nezávislý oponentský posudek na dokument, který spolu psali – strategii, pozicování, PRD, koncepci, cenotvorbu, datový model, analytickou dokumentaci. Pohled čerstvýma očima z několika úhlů: co nedává smysl, co si odporuje, co nebude fungovat, co chybí.
argument-hint: [dokument]
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, WebSearch, WebFetch]
---

# Oponent

## Co skill dělá

Uživatel má hotový nebo rozpracovaný dokument, na kterém jste spolu dlouho pracovali. Právě proto na něj **nemáš nezávislý pohled** – spoluautor nevidí, co v dokumentu chybí, protože to má v hlavě, a nevidí, co je slabé, protože si to sám odsouhlasil.

Skill proto pošle na dokument **subagenty bez kontextu téhle session**, každého z jiného úhlu, a jejich nálezy s uživatelem probere jeden po druhém.

V ose *Životního cyklu práce* (`~/.claude/RULES.md`) stojí **mimo ni jako volitelný krok** nad dokumentem, který vznikl v `/specify` nebo `/breakdown`. Nedělá se vždycky; u většího projektu se vyplatí.

## Co skill nedělá

- **Není to kontrola kódu.** Na kód je `/review`.
- **Není to kontrola proti standardům.** Na soulad s `~/Dev/context/*` je `/review`.
- **Není to audit vnitřní konzistence projektu.** Na to je `/consistency`. Oponent se ptá „je to dobře vymyšlené?“, ne „sedí to na sebe?“.
- **Nic sám nemění.** Výchozí režim je diskuze. Změny až po schválení jednotlivých nálezů.
- **Nechválí.** Věci, které jsou v pořádku, se nevypisují.

## Vztah k ostatním skillům

| Otázka | Skill |
|---|---|
| Je ten kód správně? | `/review` |
| Odpovídá to mým doménovým standardům? | `/review` |
| Nesedí si něco v projektu navzájem? | `/consistency` |
| **Je to vůbec dobře vymyšlené a bude to fungovat?** | **`/oponent`** |  |
| Je všechno ze session zapsané? | `/cleanup` |

------

## Fáze 0 – Co se oponuje

**Předmět posudku.** Uživatel ho může zadat jako argument (`/oponent docs/requirements.md`, `/oponent 01 až 04`, `/oponent pozicování`). Když ho nezadá, **nabídni mu, co jsi našel** – projdi projekt, vypiš kandidáty (dokumenty, na kterých se v poslední době pracovalo) a nech ho vybrat přes `AskUserQuestion`.

**Zkontroluj, že to má smysl oponovat:**

- **Je to kód?** → přesměruj na `/review` a zastav se.
- **Je to rozpracované torzo?** → zeptej se, jestli má smysl oponovat teď, nebo počkat. Posudek na kostru vygeneruje hlavně nálezy „chybí obsah“, což uživatel ví.
- **Je toho moc?** Nad zhruba pět dokumentů nebo řádově stovky kB se posudek rozmělní. Zeptej se, co je jádro, a oponuj to.

**Načti kontext, který posudek potřebuje:** projektový `CLAUDE.md`, `docs/rules.md` (principy, proti kterým se v projektu rozhoduje) a `docs/decisions.md` (co už bylo rozhodnuto a proč). Bez toho subagenti navrhnou znovu to, co už bylo vědomě zamítnuto – a to je nejotravnější druh oponentury.

------

## Fáze 1 – Volba úhlů pohledu

**Nepouštěj tři stejné kritiky.** Redundantní subagenti najdou třikrát totéž. Diverzita úhlů chytá selhání, která opakování nechytí.

Vyber **čtyři až pět úhlů** z katalogu níž podle sloupce *Kdy zvolit*. Výběr **předlož uživateli přes `AskUserQuestion`** předtím, než kohokoliv pustíš – volby *Pustit tak, jak je* / *Vyměnit jeden úhel* / *Vybrat panel znovu*. **Na odpověď se čeká**; do té doby žádný subagent neběží. Prostý výpis nestačí: další odstavec velí pustit panel jedním voláním, takže by se uživatel k výměně dostal až ve chvíli, kdy čtyři agenti na `xhigh` už pracují (`~/.claude/RULES.md`, *Ptej se postupně*).

**Vlastní úhel** si vymysli, jen když **žádný z katalogu nepokrývá** to, co je na dokumentu specifické. Pak ale: napiš, který katalogový úhel byl nejbližší a čím se od něj tvůj liší; napiš mu **otázky ve stejném tvaru jako v katalogu** (bez nich dorazí k subagentovi holý název a ten pak najde cokoliv); zařaď ho mezi metody, nebo domény. Osvědčí-li se, **navrhni ho doplnit do katalogu** – jinak se poznatek ztratí a příště se vymýšlí znovu a jinak. Úhel, který jde formulovat jako zúžení existujícího na doménu (*Právo → GDPR a consent*), vlastní úhel není.

Sloupec *Web* říká, který úhel dostane ve Fázi 2 svolení hledat zvenku; ostatním se to zakazuje, ať neutíkají od dokumentu.

**Metody – jak se dívat.** Dají se přiložit na jakýkoliv dokument; samy o sobě ale nemají věcnou oporu, proto se metodickému úhlu v zadání vždy určí doména, na kterou se má obořit (*Hraniční případy cenového modelu*, *Pre-mortem uvedení kurzu*).

| Úhel | Ptá se | Kdy zvolit | Web |
|---|---|---|---|
| **Vnitřní rozpor** | Tvrdí dokument někde něco, co jinde popírá? Sedí čísla, výčty a souhrny s obsahem? Nezůstal tam zbytek po zrušeném konceptu? | dokument psaný po částech nebo po několika revizích, kde se mohlo něco přepsat jen zpola |  |
| **Co chybí** | Ne co je špatně, ale co v dokumentu vůbec není. Postupuj ve dvou krocích: **(1)** vypiš hlavní entity a kroky dokumentu a u každého se zeptej, co když nenastane vůbec, nastane víckrát, jen zčásti, spolu s něčím dalším, obráceně, nebo místo něj něco jiného – co z toho dokument neřeší? **(2)** hlaš jen to, bez čeho podle dokumentu nejde jednat ani rozhodnout: nepojmenovaný vlastník, chybějící kritérium, scénář bez odpovědi. Nevypisuj chybějící kapitoly a sekce. | vždy – povinný |  |
| **Předpoklady** | Vypiš předpoklady, na kterých dokument mlčky stojí a nikde je nepojmenovává. Co musí platit, aby závěr plynul z podkladu? U každého: jak se pozná, že neplatí, a co z dokumentu padá s ním. | cokoli, co tvrdí něco o světě – strategie, pozicování, koncepce, cenotvorba |  |
| **Pre-mortem** | Je za osmnáct měsíců a tohle prokazatelně selhalo. Napiš, co se stalo – konkrétní sled událostí, ne obavu. Který předpoklad padl první? Jako jediný úhel smíš skládat příběh napříč doménami: nález, který leží na rozhraní dvou jiných úhlů, jinak nemá majitele. | cokoli, co se bude realizovat – PRD, koncepce, plán, cenotvorba |  |
| **Hraniční případy** | Vezmi pravidla, která dokument stanoví, a zkoušej je na okraji: co když nastane obojí najednou, nic, dvakrát, nebo se to zruší uprostřed? Platí to pro pravidlo obchodní a procesní stejně jako pro vstup programu – souběh dvou slev, přechod na vyšší tarif v půlce období, dvojí nárok téhož zákazníka. Neptej se na chování kódu, ale na to, jestli dokument na ten případ dává odpověď – a jestli dává jen jednu. | datový model, PRD, architektura, cenotvorba, obchodní podmínky – všude, kde dokument stanoví pravidlo s okraji |  |
| **Alternativy a řez** | Splnil by týž cíl jednodušší nebo úplně jiný postup? Které varianty autor zvažoval a proč je zamítl – je to zdůvodnění v dokumentu, nebo jen v jeho hlavě? Co se stane, když se nezmění nic? Která část jde vyškrtnout, aniž zbytek přestane dávat smysl? | cokoli, co navrhuje řešení – PRD, koncepce, architektura, datový model, cenotvorba |  |
| **Cíl a měřitelnost** | Je napsané, čeho to má dosáhnout? Podle čeho se za rok pozná, že to vyšlo, a podle čeho, že ne? Má cíl číslo, práh a termín, nebo je to próza? Co je vědomě mimo rozsah – a je to napsané, nebo se to jen předpokládá? | strategie, pozicování, PRD, plán, analytická dokumentace |  |
| **Zneužití** | Kdo má motiv to obejít – uživatel, konkurent, robot, insider? Co se dá vytěžit z mezery mezi tím, co dokument slibuje, a tím, co vymáhá? Co jde přečíst, změnit nebo získat zadarmo, aniž na to má někdo nárok? Kde dokument předpokládá, že se aktér chová slušně? | všude, kde jsou peníze, osobní údaje, přihlašování nebo cizí vstup |  |
| **Reverzibilita a závislosti** | Které rozhodnutí jde vzít zpátky a které ne? Co stojí návrat – v penězích, v datech, v důvěře? Existuje varianta, která tutéž věc otestuje vratně? Co v dokumentu má datum spotřeby a na čem cizím to stojí – co se stane, když to zdraží, změní podmínky nebo zmizí? | cokoli, co zakládá závazek, schéma, jméno nebo veřejný slib; cokoli postavené na cizí službě |  |
| **Čtenář bez kontextu** | Přečti dokument jako člověk, který u jeho vzniku nebyl. Který termín není nikde definovaný nebo mění význam? Které rozhodnutí je zapsané bez důvodu, takže ho nikdo netroufne změnit? Kde by dva čtenáři odešli s jiným zadáním? Na co dokument odkazuje, aniž to jmenuje? | jakékoli zadání, které bude někdo (člověk i agent) číst bez autorů – requirements, architektura, plán, měřicí dokumentace |  |
| **Skeptik** | Nedůvěřuj ničemu a hledej chyby. Plyne závěr z toho, co mu předchází? Je tvrzení podané jako fakt doopravdy fakt? Nesahej na čísla, právo, provoz ani technologii – ty mají vlastní úhly; ptáš se na logiku argumentace. | záložní volba pro dokument, na který nesedne žádný doménový úhel |  |

**Domény – na co se dívat.** Nesou znalost oboru, ale bez metody sbírají povrch.

| Úhel | Ptá se | Kdy zvolit | Web |
|---|---|---|---|
| **Ekonomika provozu** | Sedí čísla? Break-even, cena, marže, kapacita, náklady na provoz. Kdo to bude reálně dělat, jak často a co se stane, když to neudělá? Co vyžaduje ruční zásah? Co se rozbije při desetinásobku a co při desetině? | cenotvorba, strategie, obchodní model, koncepce, PRD, analytická dokumentace | ✔ |
| **Osobní údaje a souhlas** | Co se sbírá, na jakém právním základu a jak dlouho se to drží? Co dokument slibuje uživateli a co ve skutečnosti dělá? Jde výmaz provést, aniž se rozpadne zbytek? | analytická dokumentace, měřicí plán, cokoli s uživatelskými daty | ✔ |
| **Závazky vůči druhé straně** | Spotřebitelské právo, smluvní závazky, daně, autorská práva. Co je napsané tak, že to nejde dodržet? Co slibuje víc, než na co má autor nárok nebo kapacitu? | cenotvorba, obchodní podmínky, nabídka, licence | ✔ |
| **Data a jejich životní cyklus** | Co je klíč záznamu a co se stane, když se změní? Kde je pro každý údaj zdroj pravdy a kdo ho smí přepsat? Co se děje s duplicitou, s historií a se smazáním? Jak se do nového modelu dostanou stará data a jak se z něj dá vycouvat? | datový model, architektura, analytická dokumentace |  |
| **Nepřítomní dotčení** | Koho ještě se to dotkne, i když v dokumentu není? Kdo to musí odsouhlasit a byl u zadání? Komu to přidá práci a kdo se tomu bude bránit – a proč právem? Kdo si po zavedení pohorší oproti dnešku? Kolik lidí to umí a co když ten jeden vypadne? | cokoli pro konkrétní organizaci (profil v `~/Dev/context/organizations/`), cokoli měnícího zaběhaný proces nebo cenu stávajícím klientům |  |
| **Konkurence a trh** | Existuje to už? Čím se to liší? Proč by si zákazník vybral tohle, a ne cizí nabídku nebo to, co používá dneska? Obstojí ta odlišnost, když si ji ověří? (Jestli to má vůbec smysl dělat, řeší *Alternativy a řez* – tebe zajímá volba zákazníka, ne náklad příležitosti autora.) | pozicování, strategie, nový produkt nebo služba | ✔ |
| **Technická proveditelnost** | Dá se to postavit tak, jak je to popsané? Kde je skryté riziko? | architektura, datový model, PRD, analytická dokumentace | ✔ |
| **Cílová skupina** | Čte to očima persony, které se to týká – a ta nezná alternativy, zná jen tenhle text. Rozumí tomu? Věří tomu? Co ji odradí, co v tom nenajde, kde přestane číst? (Srovnání s tím, co nabízí někdo jiný, nech *Konkurenci a trhu* – ten na to má rešerši, ty ne.) | pozicování, prodejní text, PRD, cenotvorba |  |

**Pravidla výběru:**

- Úhel *Co chybí* ber jako **povinný**, ať je dokument jakýkoliv. Druhý povinný úhel schválně nemáme: dva pevné sloty ze čtyř by z volby podle povahy dokumentu udělaly ozdobu.
- Vyber **aspoň jednu položku z každého bloku**. Samé domény dají tři audity a nula oponentur; samé metody tři obecné kritiky bez věcné opory.
- Metodický úhel pouštěj **vždy s určenou doménou** – vypiš ji do jeho zadání. Metoda bez domény je slepá.
- **Kolik jich pustit podle rozsahu předmětu:** čtyři u jednoho dokumentu zhruba do 15 kB, pět nad tím nebo když je dokumentů víc. Je-li předmět velký (blíží se hranici z Fáze 0), dělí se **úhel × podmnožina dokumentů**, ne jen úhel – jinak čte každý agent celý objem a dělba škáluje jen jedním směrem.
- **Volbu dolož.** U každého zvoleného úhlu napiš jednou větou, co konkrétně v dokumentu tě k němu vedlo, a jmenuj **jeden úhel, který jsi vědomě nevzal, a proč**. Nevybraný úhel totiž nevrátí nula nálezů, ale neexistenci – a ta neprojde žádným počítadlem ve Fázi 4 ani ve verdiktu. Volbu přitom dělá ten, kdo dokument spoluautorsky psal, takže je to jediné místo, kde má jeho slepota volnou ruku (`~/.claude/RULES.md`, *Zapiš i to, co vědomě nemáš*).

------

## Fáze 2 – Nezávislé posudky

Pusť subagenty **paralelně, jedním voláním s víc tool calls**. Každý dostane vlastní úhel a **žádný kontext z téhle session** – to je celý smysl.

**Nejsilnější model, `xhigh`** (Volba modelu a effortu podle `~/.claude/RULES.md`, *Model a effort podle úkolu*.) Oponentura je verifikace, ne sběr: slabý model námitku nevymyslí ani neobhájí, jen zdvořile přizvukuje tomu, co má před sebou – a posudek, který všechno schválí, je horší než žádný, protože dodá falešnou jistotu.

Zadání pro každého (doplň úhel, cesty a projektový kontext):

```
Jsi nezávislý oponent. Nemáš žádný kontext z předchozích rozhovorů – máš jen ty soubory,
které si přečteš. Autor dokumentu tě neslyší, takže nemá smysl být ohleduplný.

DOKUMENT: <absolutní cesty>
KONTEXT PROJEKTU (přečti, ale neoponuj to): <CLAUDE.md, docs/rules.md, docs/decisions.md>

TVŮJ ÚHEL POHLEDU: <úhel a jeho otázky ze sloupce *Ptá se*>

Přečti dokument celý a hledej výhradně ze svého úhlu. Ostatní úhly pokrývají jiní
oponenti – nepřebíhej k nim.

U KAŽDÉHO NÁLEZU UVEĎ:
- **Kde** – soubor a sekce, ideálně citace věty, které se to týká
- **Co** – jednou větou, co je špatně
- **Proč to vadí** – konkrétní důsledek, ne obecná obava. „Nebude to škálovat“ je nic;
  „při 20 000 účastnících vyjde ruční párování na 300 hodin práce“ je nález.
- **Návrh** – dvě až tři konkrétní varianty řešení, ne jedna. Nemáš-li řešení, řekni to
  a označ nález jako otázku k rozhodnutí.
- **Závažnost** – KRITICKÉ / STŘEDNÍ / KOSMETICKÉ, stejná škála jako v `/review` a `/consistency`, ať jdou nálezy z různých skillů porovnat. U oponentury se čte jako síla námitky: **KRITICKÉ** boří předpoklad, na kterém dokument stojí; **STŘEDNÍ** mění závěr nebo rozsah; **KOSMETICKÉ** zpřesňuje.

PRAVIDLA:
- Co je v pořádku, nepiš. Žádné shrnutí kladů, žádné „jinak je to dobře promyšlené“.
- Nenavrhuj to, co je v docs/decisions.md už vědomě zamítnuté. Přečti si to nejdřív.
  Výjimka: myslíš-li si, že to rozhodnutí bylo chybné, řekni to výslovně jako revizi
  rozhodnutí a zdůvodni, který jeho předpoklad neplatí.
- Neopírej nález o neověřené tvrzení. Stojí-li na faktu, ověř ho.
- Nešetři kritikou. Ale kritizuj dokument, ne autora.
- Nenavrhuj přeformulování textu kvůli stylu – od toho tu nejsi.

Do žádného souboru nezapisuj.
```

**Volitelně rešerše.** Úhlu, který má v katalogu ve sloupci *Web* ✔, dej výslovné svolení hledat na webu. U ostatních to zakaž, ať neutíkají od dokumentu.

------

## Fáze 3 – Ověření nálezů

**Nálezy z panelu nejsou závěry, ale tvrzení.** Oponent bez kontextu vyrobí i nález, který stojí na tom, co nemohl vědět – a nález, který nevyrobí nic, vypadá jako selhání běhu, takže tlak na produkci je vestavěný. Kdyby se falešné vyřazovaly až v konsolidaci, dělal by to spoluautor, tedy ten jediný aktér, jehož slepotu má celý skill obcházet. To je přesně ten tichý filtr, který si Fáze 4 zakazuje – jenže bez téhle fáze nemá čím ho nahradit.

**Deduplikuj ještě před ověřením**, ne až po něm (Fáze 4, bod 1). Úhly se překrývají, takže tentýž problém přijde dvakrát jinými slovy a tři ověřovatelé na jednu věc jsou trojnásobná cena za tutéž odpověď.

Na každý nález se závažností **KRITICKÉ a STŘEDNÍ** pošli **samostatného ověřovatele** – paralelně, v čerstvém kontextu, který nevidí ani panel, ani tvou konverzaci. **Nejsilnější model, `xhigh`**, i u nálezu z levného úhlu: slabý ověřovatel nález nepotvrdí ani nevyvrátí, jen přizvukuje tomu, co má před sebou, a z ověření se stane razítko.

**Ověřovatel dostane projektový kontext, který oponentům chybí** – `CLAUDE.md`, `docs/rules.md`, `docs/decisions.md`. To je rozdíl oproti `/review`: tam se ověřuje pozorování o kódu, tady tvrzení o dokumentu, a nejčastější důvod falešného nálezu je právě kontext, který oponent neměl. Ověřovatel ho má a rozhodne strojově to, co by jinak odhadl spoluautor.

```
Ověřuješ jedno tvrzení nezávislého oponenta. Nemáš kontext z předchozích rozhovorů.

DOKUMENT: <absolutní cesty>
KONTEXT PROJEKTU: <CLAUDE.md, docs/rules.md, docs/decisions.md>

NÁLEZ K OVĚŘENÍ: <kde, co, proč to vadí, návrh, závažnost>

Tvůj úkol není nález potvrdit, ale pokusit se ho vyvrátit. Ptej se:
- Stojí na tom, co v dokumentu doopravdy je? Ověř citaci.
- Neřeší to dokument někde jinde, kde se oponent nedíval?
- Neplyne z kontextu projektu, že to tak je schválně?
- Je důsledek doložený, nebo je to obecná obava? („Nebude to škálovat“ je nic.)
- Sedí navržená závažnost, nebo je nafouknutá?

Vrať: POTVRZENO / VYVRÁCENO / PŘEKVALIFIKOVÁNO NA <závažnost>, jednou větou proč,
a u vyvráceného doklad – citaci z dokumentu nebo kontextu, která ho boří.

Do žádného souboru nezapisuj.
```

**KOSMETICKÉ nálezy se neověřují** – ověření by stálo víc než jejich vyřízení. **Vyvrácené zahoď a spočítej je do souhrnu**; kolik jich bylo, se říká nahlas, ne potichu.

------

## Fáze 4 – Konsolidace

Než cokoliv předložíš, nálezy **zpracuj**:

1. **Duplicity už jsou sloučené** – dedup proběhl před ověřením (Fáze 3). Zůstává jen poznamenat u nálezu, že ho našli dva oponenti z různých úhlů; je to signál závažnosti.
2. **Vyvrácené nálezy vyřadil ověřovatel**, ne ty. Sám nefiltruj: nález, u kterého máš pochybnost, ale ověřením prošel, předlož s poznámkou. Tichý filtr je přesně to, co má tenhle skill obcházet, a spoluautor je ten poslední, kdo ho má dělat.
3. **Vyřaď už rozhodnuté.** Nález, který navrhuje zamítnutou variantu bez nového argumentu, zahoď a **řekni, kolik jsi jich zahodil a proč** – ne potichu.
4. **Seřaď podle závažnosti**, ne podle pořadí v dokumentu.
5. **Vypiš přehled** – všechny nálezy jednou větou, očíslované, se závažností. Uživatel musí vidět, co ho čeká, než se ho začneš ptát.

------

## Fáze 5 – Průchod nálezy

Podle `~/.claude/RULES.md` (*Ptej se postupně, ne všechno najednou*) projdi nálezy **jeden po druhém**, od nejzávažnějšího.

U každého nejdřív vypiš:

```
---
[N/celkem] 🔴/🟡/🔵 NÁZEV NÁLEZU
Našel: <úhel, případně „2 oponenti nezávisle“>

Kde: <soubor, sekce, citace>
Co: <jednou větou>
Proč to vadí: <konkrétní důsledek>

Varianty řešení:
A) <…> – důsledek
B) <…> – důsledek
C) Nechat být – <proč to může být v pořádku>

Doporučuji: <jedna z nich a proč>
```

Pak se zeptej **přes `AskUserQuestion`** – jedno volání na jeden nález, `header` `Nález N/celkem`, volby jsou **konkrétní varianty řešení**, ne „Opravit / Odložit / Přeskočit“ – u oponentského nálezu existuje víc věcných cest a „opravit“ neříká kterou. Vždy nech mezi volbami i **Nechat být** a **Vrátit se k tomu později**.

**Která volba znamená který stav** (bez toho nejde odpověď zpracovat):

| Volba | Stav |
|---|---|
| kterákoliv věcná varianta (A, B, C…) | **Přijato** |
| Nechat být | **Zamítnuto** |
| Vrátit se k tomu později | **Odloženo** |

Tool má strop čtyři volby, takže věcných variant nabízej **nejvýš dvě** – zbylá dvě místa patří *Nechat být* a *Vrátit se k tomu později*. Je-li rozumných cest víc, vyber dvě nejsilnější a ostatní zmiň v popisu nálezu.

(V `/consistency` a `/review` je to naopak správně: tam má nález jedno navrhované řešení a volby jsou *Opravit / Odložit / Přeskočit*, u hromadných nálezů navíc *Rozbalit*.)

**Zpracování odpovědi:**

- **Přijato** → zapracuj do dokumentu rovnou a zapiš rozhodnutí do `docs/decisions.md`.
- **Zamítnuto** → zapiš do `docs/decisions.md` **taky**, i s důvodem. Zamítnutý nález je cenný záznam – brání tomu, aby ho příští oponentura našla znovu jako nový.
- **Odloženo** → do `docs/todo.md`, ve tvaru podle `~/.claude/RULES.md`, *Odložené věci pojmenuj a zaparkuj*.

**Odbočky.** Uživatel u nálezu často rozvine úvahu, která zasáhne jinam. Tu úvahu zapiš celou – bývá cennější než původní nález. Pak se vrať k seznamu a pokračuj; sám si hlídej, které nálezy zbývají.

------

## Fáze 6 – Závěr

**Opakované spuštění.** Skill je určený k opakování nad revidovanou verzí. Když ho uživatel spustí znovu:

- **Nález, který se vrátil**, znamená, že se neopravil, jen přeformuloval. Řekni to výslovně.
- **Míň nálezů** znamená, že se to lepší, a **víc**, že revize otevřela nové problémy – ale jen tehdy, **běžel-li stejný panel úhlů**. Panel se nikam nezapisuje, takže to zpravidla nevíš: pak počty nesrovnávej a řekni místo toho, které úhly běžely teď.

Ve verdiktu:

```
## Oponentura hotová

**Předmět:** <dokumenty>
**Úhly:** <seznam>

**Nálezy:** N celkem – 🔴 X kritických, 🟡 Y středních, 🔵 Z kosmetických
- Zapracováno: N
- Zamítnuto: N (zapsáno do decisions.md i s důvodem)
- Odloženo: N (todo.md)
- Vyvráceno při ověření: N (nezobrazeno)
- Vyřazeno před předložením: N (<proč>)

**Nejzávažnější, co z toho vzešlo**
- <jedna až tři věty – co to reálně změnilo>
```

Zakonči jednou z těchto vět:

- `Všechny nálezy jsou vypořádané, dokument je po oponentuře.`
- `Vypořádané nejsou: <konkrétní seznam>.`

Nikdy nekonči tím, že je dokument „v dobrém stavu“ – to není verdikt oponenta, ale autora.