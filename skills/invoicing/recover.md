# Dohledání nenatrackovaného času

Referenční soubor k režimu `recover` skillu `/invoicing`. Drží **katalog zdrojů a heuristiky**; postup, kdy se co dělá, je v `SKILL.md`, *Režim `recover`*. Přístupy, tokeny a konkrétní volání do systémů drží `~/Dev/context/business/invoicing.md`, *Stopy práce* – **sem se nikdy neopisují**, tenhle soubor je veřejný.

## Obsah

- *Co je stopa* – jednotka, se kterou celý režim pracuje
- *Katalog zdrojů* – co z kterého jde vyčíst a jak silný to je signál
- *Výlučné a sdílené zdroje* – proč se seznam URL dělí na dva
- *Tři třídy jistoty* – jak se z stop dělá odhad hodin
- *Odevzdaný výstup jako stopa* – jak se z hotového výsledku usuzuje na práci, která mu předcházela
- *Deduplikace* – proč se stopy nesčítají
- *Zadání pro sběrače* – co dostane agent a co musí vrátit
- *Ověření nálezů* – povinná vrstva, která tip vyvrací
- *Výstup*

------

## Co je stopa

**Stopa** je jeden doložený okamžik nebo interval, kdy se něco dělo. Nese vždycky pět věcí:

| Pole | Co v něm je |
|---|---|
| `zdroj` | mail, kalendář, Slack, git, Claude Code, prohlížeč |
| `od`, `do` | čas; u bodové stopy je `do` prázdné |
| `basis` | **doslovný** úryvek nebo název – předmět mailu, titulek schůzky, první řádek commitu |
| `odkaz` | kam se dá kliknout a ověřit to |
| `vylucnost` | `vylucna` / `sdilena` podle *Výlučné a sdílené zdroje* |

**Stopa není nález.** Nález vzniká až tím, že se stopa nepotká se záznamem v Clockify a přežije ověření. Míchat obojí znamená ukázat uživateli výpis logu a nechat práci na něm.

## Katalog zdrojů

Kvalita signálu je to jediné, co u zdroje rozhoduje – **nese sám o sobě délku?**

| Zdroj | Co dá | Signál |
|---|---|---|
| **Kalendář** | titulek, začátek, konec, účastníci, délka v minutách | **nejlepší** – délka je v datech, neodhaduje se |
| **Hovory** (Zoom, Teams) | čas a délka hovoru, případně nahrávka | **nejlepší** – totéž, a navíc se to opravdu konalo |
| **Slack** | čas zprávy, autor, **obsah** | silný – obsah často délku přímo říká, viz níž |
| **Claude Code** | timestampy zpráv v `~/.claude/projects/<projekt>/*.jsonl` | silný – souvislá session je skutečný interval u klávesnice |
| **Git** | author date commitu, první řádek zprávy | střední – ukazuje konec práce, ne její začátek |
| **Prohlížeč** | navštívená URL, čas návštěvy **a doba na stránce** | střední – u výlučné URL použitelné, u sdílené ne |
| **Sdílené dokumenty** | zápisy ze schůzek, **odevzdané výstupy**, zmínky o tom, co bylo dodáno | silný – nese obsah i hotové výsledky, viz *Odevzdaný výstup jako stopa* |
| **Mail** | čas odeslání, předmět, obsah | slabý – odeslání je špička ledovce, ne práce sama |

**Kalendář se čte skriptem `~/.claude/skills/invoicing/calendar.swift`** a čtyři věci z něj vypadávají dřív, než se z nich stane stopa. Všechny čtyři vyrobily falešný nález při prvním ostrém běhu, takže to nejsou hypotézy:

- **Celodenní události** – narozeniny, svozy odpadu, dovolené. Nesou délku 1439 minut a udělaly by z každého dne fakturovatelný den.
- **Odmítnuté schůzky** – nekonaly se. Poznají se podle příznaku `odmitnuta`, ne podle toho, že v kalendáři jsou.
- **Duplicitní záznamy na týž čas** – táž schůzka bývá v kalendáři několikrát: přijatá z víc stran, nebo ležící ve dvou kalendářích téhož účtu. Slévají se **podle času, ne podle názvu** – tentýž hovor se v obou kopiích běžně jmenuje jinak.
- **Zasedačky mezi účastníky** – adresy typu `…@resource.calendar.google.com` jsou místnosti, ne lidé. Podle protistrany se schůzka pozná jen z adres skutečných účastníků.

**Dlouhá návštěva v prohlížeči není dlouhá práce.** Doba na stránce se dá číst, ale záložka nechaná otevřená přes noc vyrobí desítky hodin – v reálných datech se našla návštěva dlouhá 58 hodin. **Mez a způsob čtení drží `~/Dev/context/business/invoicing.md`, *Stopy práce***; nevymýšlej si vlastní.

**Než porovnáš čas z kalendáře s časem odjinud, ověř pásmo.** Skript vypisuje **místní** čas s offsetem; zpráva v chatu („dáme to ve 12:30“) je taky místní, ale záznam v jiném systému nemusí být. Posunutý čas nevypadá jako chyba, ale jako **jiná událost** – a tím se z potvrzené schůzky stane falešný nález chybějících hodin. Stalo se to při prvním ostrém běhu.

**Obsah je nadřazený času.** Věta „koukal jsem na to, dělal jsem na tom asi tři hodiny“ je **doložená délka**, i když ji nese jednominutová zpráva na Slacku. Časy říkají *kdy*, obsah často *kolik* – a když se rozejdou, vyhrává obsah. Zdroj, ze kterého se čte jen razítko, je promarněný.

**Odchozí, ne příchozí.** Mail od klienta a zpráva od klienta nejsou Honzova práce. Sbírá se **to, co odeslal on**; příchozí zpráva se hodí nanejvýš jako kontext, proč ta práce vznikla.

**Claude Code nese i obsah.** Když v `~/Dev` není adresář pojmenovaný po klientovi, neznamená to, že se pro něj nepracovalo – práce mohla proběhnout v session jiného projektu. Hledej i **jméno klienta a jeho identifikátory v obsahu sessions**, ne jen v názvu adresáře.

## Výlučné a sdílené zdroje

Seznam URL u klienta se dělí na dva druhy a **s každým se pracuje jinak**:

- **Výlučné** – návštěva sama o sobě znamená práci pro toho klienta: jeho web, weby jeho zákazníků, jeho property v analytických nástrojích.
- **Sdílené** – nástroj, který Honza používá i jinde nebo jednou bude: obecné AI nástroje, dokumentace, editory. **Sdílená stopa sama nález nevyrábí.** Buď posílí nález, který ve stejném okně už stojí na výlučné stopě, nebo se ukáže jako *indicie* s výslovnou poznámkou, že zdroj je sdílený.

**Nejsou to domény, ale vzory URL.** Nejsilnější stopy bývají uvnitř sdíleného hosta: property v analytice, kontejner ve správci značek, projekt v timetrackingu. Host je sdílený, ID v cestě výlučné. Porovnávej celé URL, ne jen doménu – jinak vypadne to nejpřesnější, co seznam má.

**Najdeš-li tutéž URL vedenou jako výlučnou u dvou klientů, ohlas to a ani u jednoho z ní nález nedělej.** Přesně tak se pozná, že se z výlučného zdroje stal sdílený. Spoléhat na to, že si toho někdo včas všimne, znamená fakturovat cizí čas.

## Tři třídy jistoty

Každý nález patří do jedné z nich a **třída se vypisuje**, protože rozhoduje, jestli se dá odhad použít:

| Třída | Kdy | Odhad hodin |
|---|---|---|
| **doložený** | stopa nese délku – schůzka, hovor, věta o počtu hodin | ta délka |
| **odvozený** | souvislý shluk stop – série commitů, session, řada zpráv | od první do poslední stopy; **řekni, jak to vyšlo** |
| **indicie** | jedna osamělá stopa, nebo jen sdílené zdroje | **žádný** – řekne se, že se toho dne něco dělo a v timetrackingu je prázdno |

**U indicie se počet hodin nedomýšlí.** Jeden mail může být pět minut i osm hodin práce a odhad je v tu chvíli výmysl s číslem. Číslo se pamatuje líp než výhrada, se kterou přišlo.

**Souvislý shluk** je řada stop, mezi kterými není mezera delší než hodina. Delší mezera dělá dva shluky, ne jeden dlouhý interval – jinak by oběd uprostřed dne vyrobil fakturovatelnou hodinu.

## Odevzdaný výstup jako stopa

**Práce se nepozná jen z evidence, ale i z toho, co po ní zbylo.** Věta „ten den jste podle kalendáře měli schůzku a v Clockify nemáš nic“ je nejsnazší nález, ne jediný. Stejně dobře doloženým dokladem o odvedené práci je **hotový výstup** – sepsaný dokument, analýza, rozpad metodiky, revize, návrh –, protože ten sám o sobě nemohl vzniknout bez času.

Jsou dvě podoby a obě se hledají v obsahu, ne v razítkách:

- **Vidíš výstup samotný** – karta ve sdíleném dokumentu, příloha mailu, odkaz na soubor.
- **Vidíš zmínku, že byl odevzdán** – zápis ze schůzky říká „Honza poslal rozpad pixelu“, mail klienta děkuje za dodaný dokument. Výstup nevidíš, ale **jeho existence je doložená**.

### Čím se liší od ostatních stop

**Je retrospektivní.** Ostatní stopa říká *tehdy se pracovalo*; výstup říká *někdy předtím se pracovalo* a neříká kdy. Datum odevzdání je tedy **konec intervalu, ne interval sám** – a proto z něj nikdy nevzniká řádek v tabulce s hodinami.

Postup je vždycky tenhle:

1. **Urči okno,** ve kterém výstup musel vzniknout: od poslední doložené stopy k témuž tématu (schůzka, kde se zadal, předchozí verze, zpráva „pustím se do toho“) do data odevzdání. Není-li žádná, ber **14 dní zpět** a řekni to.
2. **Sečti, co je v tom okně v Clockify** – na projektu klienta i jinde.
3. **Odhadni dolní mez práce,** kterou ten výstup musel stát: **kolik nejméně**, ne kolik typicky. Rozhoduje rozsah a povaha – několik normostran vlastního textu k cizí metodice není půlhodina, ale ani se z toho nedá dělat den.
4. **Porovnej.** Sedí-li to, mlč – výstup je pokrytý. Je-li v okně **prázdno nebo řádově méně**, vzniká **otázka na Honzu**, ne nález.

### Ptej se, nepočítej

Výsledkem je otázka v tomhle tvaru: **co to je, kdy to bylo odevzdáno, kolik je na to v okně natrackováno, kolik to podle tebe nejméně muselo stát a proč si to myslíš.** Nikdy ne samotné číslo.

> Karta *FAVI pixel změny* (~540 řádků, stávající funkčnost i návrh změn) je v dokumentu k 17. 6. V Clockify je mezi 6. a 17. 6. na FAVI 2,5 h a z toho většina padne na schůzku. Sepsat tohle stálo řádově hodiny. Nezapomněl sis natrackovat práci na tom dokumentu?

**Číslo se do součtu nikdy nepočítá** a do tabulky nálezů takový případ nepatří – patří pod ni, do *Otázek k rozsahu*. Důvod je týž jako u indicie: odhad práce z výsledku je úsudek o tom, jak dlouho někomu jinému trvalo psaní, a **číslo se pamatuje líp než výhrada, se kterou přišlo**. Rozdíl je, že u indicie se neptáš na nic, tady se ptáš na konkrétní věc – a odpovědět umí jen ten, kdo ji psal.

### Kdy to nález není

Pět případů, které vypadají stejně a prací nejsou. Projdi je dřív, než se zeptáš:

- **Výstup není Honzův.** Export textu autorství neukazuje. U zápisu ze schůzky to nevadí, u dokumentu ano – doloží se mailem, kterým ho poslal, nebo zmínkou v zápisu.
- **Práce je natrackovaná dřív, než sahá okno.** Dokument psaný na etapy před měsícem. Než se zeptáš, **rozšiř okno** a podívej se, jestli se tam ta práce neschovala.
- **Vznikl na schůzce.** Zápis ze schůzky sepsaný během ní není práce navíc; je to ta schůzka.
- **Je převzatý.** Šablona, cizí podklad, výstup nástroje. Vlastní práce je pak jen to, co k němu přibylo.
- **Rozsah klame.** Dlouhý dokument slepený z citací a odkazů stál míň než stránka vlastní úvahy. Posuzuje se **vlastní text**, ne délka souboru.

## Deduplikace

**Stopy se nesčítají.** Mail o schůzce, ta schůzka v kalendáři a zpráva na Slacku hodinu po ní jsou **jedna práce**, ne tři. Bez tohohle pravidla režim spolehlivě nadhodnocuje – a jednou nafouknutý odhad zabije důvěru ve všechny ostatní.

Postup: stopy se seřadí podle času, slijí do shluků podle pravidla o hodinové mezeře, a **teprve shluk je kandidát na nález**. Ve výstupu se u něj vyjmenují všechny zdroje, ze kterých vznikl – čtenář tak vidí, že tři zdroje mluví o jedné věci, a ne že jsou to tři věci.

## Zadání pro sběrače

Sběr běží **paralelně, jeden agent na zdroj**. Není to kvůli rychlosti, ale kvůli kontextu: surová data ze schránky a z historie prohlížeče by hlavní session zahltila a na vlastní úsudek by nezbylo místo.

Každý agent dostane: **klienta, období, své identifikátory ze souboru klienta** (a jen je), a vrací **pole stop**, nic jiného. Neuvažuje o hodinách, nesrovnává s Clockify a nedělá závěry – to je práce hlavní session, která jako jediná vidí všechny zdroje najednou.

```json
{
  "zdroj": "slack",
  "od": "2026-08-14T09:12:00+02:00",
  "do": null,
  "basis": "\"tak jsem se v tom hrabal celý dopoledne, ten feed je fakt rozbitej\"",
  "odkaz": "https://…",
  "vylucnost": "vylucna"
}
```

**Sběrač, který vidí obsah** – dokument, chat, mail –, vrací i **odevzdané výstupy a zmínky o nich**: název, datum, rozsah vlastního textu a to, komu se odevzdal. Bez rozsahu se dolní mez práce odhadnout nedá a hlavní session by se pro něj musela vracet ke zdroji.

**Agent, který nemá přístup, to řekne** a vrátí prázdné pole s důvodem. Nedostupný zdroj se ve výstupu vypíše jako slepé místo – bez toho by věta „nic dalšího jsem nenašel“ znamenala pokaždé něco jiného.

## Ověření nálezů

**Povinná vrstva** (`~/.claude/skills/SKILLS.md`, *Ověřovací vrstva*). Panel požádaný o hledání mezer nějakou najde vždycky; po třetím falešném tipu se režim přestane pouštět, což je horší než ho nemít.

Ověřovatel dostane jediný úkol: **nález vyvrátit**. Projde tyhle otázky a stačí jedno „ano“:

1. **Není ten čas v Clockify pod jiným projektem?** Pak nechybí, jen je špatně zařazený – a to je jiná diagnóza s jiným řešením.
2. **Je stopa opravdu o tomhle klientovi?** Přeposlaný mail, zmínka v cizí konverzaci, sdílená URL bez opory.
3. **Není to už vyfakturované?** Období mimo rozsah.
4. **Nese ta stopa vůbec práci?** Automatický commit, kalendářní událost, která se nekonala, otevřená záložka na pozadí.
5. **Není to soukromý čas?** Víkend a večer nálezem samy o sobě nejsou, ale vyžadují silnější doložení než pracovní dopoledne.

**Otázka k rozsahu se ověřuje taky**, jen se jinak vyvrací: neptá se „stalo se to?“, ale „není ta práce vidět jinde nebo jindy?“. Ověřovatel projde pět případů z *Kdy to nález není*; **stačí jeden a otázka se nepokládá**.

**Co ověření nepřežije, se neukáže.** Vyvrácené nálezy se vypíšou jen v souhrnném počtu, ne jednotlivě – jinak si je uživatel přečte a rozhodnutí se tím vrátí zpátky k němu.

## Výstup

Tabulka seřazená **od nejjistějšího**, protože podle ní se odshora doplňuje do timetrackingu:

```
| Den | Odhad | Třída | Zdroje | Doložení |
|---|---|---|---|---|
| 2026-08-14 | 3 h | doložený | slack | „dělal jsem na tom asi tři hodiny“ |
| 2026-08-19 | 1,5 h | odvozený | git, claude code | 6 commitů 14:02–15:31 |
| 2026-08-22 | – | indicie | mail | odeslána nabídka; v Clockify ten den nic |
```

Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo – `~/.claude/RULES.md`, *Styl odpovědí*.

Pod tabulku patří čtyři věci, každá i když je prázdná:

- **Natrackováno jinam** – nálezy z otázky 1 ověřovatele, tedy čas k přesunu, ne k doplnění.
- **Slepá místa** – zdroje, na které se nesáhlo, a proč.
- **Otázky k rozsahu** – odevzdané výstupy, ke kterým v okně před nimi natrackovaná práce chybí. Každá jako otázka podle *Odevzdaný výstup jako stopa*, ne jako číslo.
- **Součet** – zvlášť za doložené a odvozené; **indicie se do součtu nepočítají**, protože nemají číslo.

**Nic se nikam nezapisuje.** Ani do Clockify, ani do souboru klienta. Odhad postavený na úsudku o cizích datech je návrh, ne zjištění, a rozhodnutí patří tomu, kdo tu práci odvedl.
