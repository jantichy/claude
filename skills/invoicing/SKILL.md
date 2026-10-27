---
name: invoicing
description: Skill se použije, když uživatel zadá "/invoicing" (volitelně s režimem full, preview, recover nebo sync a se jménem klienta), nebo chce vystavit faktury klientům – sestavit doklad podle fakturační dohody klienta z hodin v timetrackingu, paušálů a dalších dohodnutých položek, vystavit faktury, přiložit PDF faktury i výkazu hodin a nechat rozepsaný mail, u předplacených hodin místo faktury odepsat kredit. Režim recover dohledá čas, který se zapomněl natrackovat, a nabídne tipy k doplnění; režim sync přepíše odpracovaný čas z primárního timetrackingu do timetrackingu klienta, má-li klient vlastní. Sazby, daňový režim a volání systémů drží ~/Context/Business/, dohodu s klientem jeho fakturační soubor pod ~/Clients, ne tenhle skill. Na rozdíl od /report nedělá analytický report, ale účetní doklady. Mail neodesílá nikdy – končí draftem a odeslání je vždy uživatelův klik; teprve když uživatel potvrdí, že mail odeslal, označí fakturu ve fakturačním systému za odeslanou. Neúčtuje, nehlídá úhrady ani daňové termíny.
argument-hint: [full|preview|recover|sync] [klient] [období]
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion, Agent]
---

# Invoicing

## Co skill dělá

Vystaví faktury klientům a připraví je k odeslání. **Zadáním faktury je u každého klienta jeho fakturační soubor**, ne timesheet. Podle něj skill za období, které ještě není vyfakturované, sestaví doklad ze všeho, co dohoda předepisuje: z hodin v timetrackingu, měsíčního paušálu, pevné částky, fáze spolupráce nebo dohodnutých položek mimo timetracking. Pak fakturu vystaví a založí v mailu draft se dvěma přílohami – fakturou a výkazem hodin. **Klientovi, který zaplatil hodiny dopředu, místo faktury odepíše hodiny z předplaceného kreditu**, pošle mu do draftu jen výkaz se zbytkem kreditu a ohlásí, až kredit dojde.

- **`/invoicing full`** (výchozí) – celý průběh až po rozepsané drafty.
- **`/invoicing preview`** – náhled toho, co by se vystavilo. Nic nevystaví, nic nezapíše, nikam nesáhne.
- **`/invoicing recover`** – dohledá čas, který se zapomněl natrackovat, a ukáže tipy s doložením. Taky nic nevystaví a **sám od sebe nezapíše ani do timetrackingu, ani do souboru klienta**.
- **`/invoicing sync`** – přepíše odpracovaný čas do timetrackingu klienta, má-li ho klient vyplněný. Nic nevystavuje; **jako jediný režim zapisuje do cizího systému**.

Za režimem smí stát **jméno klienta**. S ním jede skill jen přes něj, bez něj přes všechny, kteří mají **fakturační soubor ve své klientské složce** – kde se hledá, drží *Fáze 0*, bod 4. **Klienta bez vyplněné části *Dohoda* vynech a řekni to** – takový soubor existuje kvůli `recover`, který identifikátory potřebuje dřív, než se začne fakturovat, a fakturovat podle nevyplněné dohody nejde. **Stejně vynech a ohlas klienta, který má ve *Stavu spolupráce* hodnotu `uzavřená`** – fakturovat se mu už nebude a jeho zbylý čas drží deník propadlého času (`~/Context/Business/invoicing.md`, *Soubor klienta*).

**Jen u `recover` smí za jménem klienta stát ještě období** (`2026-05`), kterým se přebije výchozí rozsah. **`sync` období nepřijímá** – to, do čeho smí sáhnout, si určuje sám z otevřeného okna a přebít se nedá.

**Skill je rámec, ne pravidla.** Daňový režim, agregace, šablony a dohody s jednotlivými klienty žijí v `~/Context/Business/invoicing.md` a v souboru `invoicing.md` v klientské složce; **sazebník má vlastní soubor `~/Context/Business/pricing.md`**. Bez nich skill nemá podle čeho fakturovat a neběží.

## Co skill nedělá

- **Neodesílá maily. Nikdy.** Končí draftem a odeslání je vždy uživatelův klik v mailovém klientu. Platí to i proti výslovnému pokynu uprostřed běhu – proč, viz *Fáze 5 – Přílohy a draft*.
- **Nedělá analytické reporty.** Výkaz hodin je příloha dokladu, ne report. Na reporty z dat je `/report`.
- **Neúčtuje.** Nehlídá úhrady, upomínky, DPH přiznání ani kontrolní hlášení. Vystaví doklad a tím jeho práce končí – jediné, co po vystavení ještě udělá, je označit doklad za odeslaný, když to uživatel potvrdí (*Po odeslání*).
- **Nedrží evidenci vystavených faktur.** Zdrojem pravdy je fakturační systém, ne soubor v repozitáři – viz `~/Context/Business/invoicing.md`, *Odkud se ví, co už je vyfakturované*. **Čerpání předplaceného kreditu je jediná evidence, kterou vede** – fakturační systém ho nezná, takže jiné místo není.
- **Netrackuje čas.** Režim `recover` chybějící čas dohledá a ukáže, ale **do timetrackingu nikdy nezapíše** – odhad postavený na úsudku o cizích datech je návrh, ne zjištění. Doplnit ho je uživatelovo rozhodnutí.

  **Zákaz platí na skill, ne na uživatele.** Rozhodne-li se uživatel nechat si výstup uložit do souboru klienta jako dočasný blok k odpracování, je to jeho volba a provede ji jiný krok – `/end` nebo výslovný pokyn –, ne `recover` sám od sebe. Jak se takový blok chová při dalším běhu, drží `~/Context/decisions.md`, *Blok nálezů `recover` se při dalším běhu nahrazuje, ne kupí*.
- **Nesynchronizuje obousměrně.** Režim `sync` píše **jen** do systému klienta a **do Clockify nezapíše nikdy** – zdroj pravdy se neupravuje podle kopie.
- **Nepíše profily protistran.** Kdo klient je a kdo v něm rozhoduje, patří do jeho profilu – u klienta ve složce vedle fakturačního souboru, jinak v `~/Context/Organizations/`; sem jen fakturační dohoda.

## Jak je to postavené uvnitř

| Krok | Kdo | Proč zrovna on |
|---|---|---|
| Odpracovaný čas za období | timetracking – MCP, když je připojený, jinak jeho API | data jsou tam, nemá cenu je někam kopírovat |
| Vystavení dokladu a PDF | fakturační systém – MCP, když je připojený, jinak jeho API | doklad má vzniknout tam, kde ho vidí účetní |
| Draft mailu s přílohami | Gmail MCP, `create_draft` | umí to, a odesílací volání se nepoužije |
| Zápis času do systému klienta | jeho API, s tokenem v Keychainu | klient chce čas u sebe a ručně se to nepřepisuje |
| Stopy práce pro `recover` | mail, kalendář, chat, hovory, git, session Clauda, historie prohlížeče, sdílené dokumenty s klientem | jinde po zapomenutém čase stopa nezůstala |
| Co se fakturuje a jak | **vlastní jádro** | výjimky u klientů, neúplný výkaz, podezřelé záznamy – tady se rozhoduje |

**Čím se do systémů sahá, je implementační detail a smí se vyměnit bez ohlášení.** Skill mluví o tom, co potřebuje („odpracovaný čas klienta za období“, „vystavený doklad s poznámkou o období“), ne o konkrétních voláních. Přechod na MCP nebo změna API pak není zásah do skillu, ale do `~/Context/Business/invoicing.md`, *Přístupy*.

**Závazné a neměnné tiše je:** že se nic nevystaví bez potvrzení, že se mail neodešle za žádných okolností, že se doklad označí za odeslaný jen na uživatelovo potvrzení, že se hranice fakturovaného období čte ze systému a nikdy neodhaduje, a že se každá dohodnutá odchylka zapíše do deníku výjimek klienta.

------

## Fáze 0 – Příprava

Společný začátek je v `~/.claude/skills/preflight.md`. **Body 1 až 3 se tady vynechávají** – skill nepracuje nad projektem, pouští se odkudkoli a nesahá na kód, což je případ, který `preflight.md` výslovně předvídá. Místo nich:

1. **Načti `~/Context/Business/invoicing.md` celý** a k němu **`~/Context/Business/pricing.md`**. Nespoléhej na paměť – sazby a dohody se mění. Chybí-li `invoicing.md`, řekni to a **skonči**; skill bez něj nemá podle čeho fakturovat. `pricing.md` drží sazebník pro klienty, kteří vlastní sazbu zapsanou nemají.
2. **Zjisti dnešní datum** příkazem `date +%F` (`~/.claude/standards/rules.md`, *Hodnotu, kterou čte stroj, nepiš – nech ji vyrobit příkazem*).
3. **Ověř přístupy k timetrackingu i fakturačnímu systému** dřív, než začneš cokoliv počítat – způsobem, který popisuje `~/Context/Business/invoicing.md`, *Přístupy*. **Selže-li kterýkoli přístup, skonči a řekni který** – běh, který spočítá podklad a pak nemá čím vystavit, je jen ztracená práce. **Projdi zároveň seznam `~/Context/Business/invoicing.md`, *Co ještě není vyplněné*** – je nadřazený a nese i blokátory, které se jinak projeví až uprostřed běhu nebo po vystavení dokladu. Nedořešená položka není důvod skončit, ale **musí zaznít předem**, ne ve chvíli, kdy už doklad existuje.
4. **Urči rozsah.** Rozsahem je klient z argumentu, nebo všichni, kdo mají `~/Clients/<Client>/invoicing.md`. Klient se jmenuje podle své složky; jméno z argumentu s ní porovnej bez ohledu na velikost písmen. **Jinde se soubor klienta nehledá** – každý fakturovaný klient má klientskou složku a druhé umístění by se muselo pamatovat. V `~/Context/Business/invoicing/` leží jen odkaz pro člověka. Bod 5 i závěr přípravy s rozsahem počítají, proto se určuje už tady.
5. **Zjisti, jestli není rozdělaný běh z minula** – klient s hotovou fakturou, ale bez draftu. Poznáš to tak, že poslední faktura klienta ve fakturačním systému **už nese poznámku s obdobím**, ale v mailu k ní není draft. Navaž na něj, nezakládej znovu.

Na konci shrň, co jsi zjistil: kolik klientů je v záběru, do jakých systémů se sáhne a v jakém režimu se jede.

## Fáze 1 – Období

**Období se každému klientovi počítá zvlášť** a nikdy se neodhaduje:

1. Vytáhni ze systému **poslední fakturu tomu klientovi** – které faktury se za ni nepočítají, drží `~/Context/Business/invoicing.md`, *Odkud se ví, co už je vyfakturované* – a přečti z ní konec fakturovaného období. **Žádná tam není?** Pak se tomu klientovi ještě nikdy nefakturovalo a hranici drží **soubor klienta** – deník výjimek nebo dohoda. Přečti ho; není-li tam, zeptej se a odpověď do deníku zapiš (v režimu `full`; v `preview` se nezapisuje nic). **Nepleť si to s prázdným obdobím** – to je stav, kdy fakturovat není co, ne kdy se ještě nezačalo.
2. Začátek nového období je **následující den**, konec je konec posledního uzavřeného měsíce. **Zbývají-li nevyfakturované hodiny i v běžícím měsíci, zeptej se přes `AskUserQuestion`**, jestli období ukončit posledním uzavřeným měsícem, nebo dneškem – druhá možnost je právě skončená práce, která na konec měsíce nečeká. Volba určí obě data ve *Fázi 4*.
3. **Chybí-li v poslední faktuře záznam o období, nejdřív hledej v souboru klienta** – v dohodě a v deníku výjimek. **Je-li tam, neptej se**; je to předem daná odpověď. Není-li, **zeptej se, od kdy počítat**, a odpověď zapiš **do deníku výjimek** (v režimu `full`; v `preview` se nezapisuje nic). Neodvozuj hranici z data vystavení ani ze zaplacených hodin – obojí je jinde než skutečná hranice.

   **Do staré faktury nezapisuj nic.** Poznámka znamená období, které ten doklad pokrývá, a faktura bez ní bývá z jiné etapy spolupráce; zápis odvozený z dneška by o ní tvrdil nepravdu. Zdůvodnění drží `~/Context/decisions.md`, *Do staré faktury bez poznámky se hranice nedopisuje*.

Tvar toho záznamu i důvod, proč se dělá takhle, drží `~/Context/Business/invoicing.md`, *Odkud se ví, co už je vyfakturované*.

**Má-li soubor klienta sekci *Předplacený kredit* se zbytkem nad nulou, je to druhý zdroj hranice** a platí pozdější z obou: konec posledního měsíce v evidenci, nebo konec období z poznámky poslední faktury. Faktura předplatby poznámku nenese, takže by se jinak ptal krok 3 na něco, co evidence ví. **Období se u kreditu dělí po kalendářních měsících** – každý uzavřený měsíc je jeden řádek odpisu; běžící měsíc se neodpisuje, ani když v něm je čas. Mechaniku drží `~/Context/Business/invoicing.md`, *Jak se vyplňuje doklad*, *Předplacený kredit*.

**Vyjde-li období delší než jeden kalendářní měsíc** – typicky když se fakturace dohání zpětně –, poznamenej si to a **rozhodne se o tom ve *Fázi 3***. Nenastavuj takové období mlčky: mění text položky, znění mailu i to, co uvidí klient na dokladu.

**Klienta vynech, jen když mu podle jeho souboru za období nepatří na doklad nic**, a řekni to. Faktura na nula hodin je chyba, ne prázdná faktura. Prázdný timetracking ale k vynechání nestačí. Paušál, pevná částka nebo čekající položka mimo timetracking (*Fáze 2*) vyrobí doklad i bez jediné hodiny.

**Hlídej zákonnou lhůtu na vystavení.** Je to **15 dnů od DUZP** (`~/Context/Business/invoicing.md`, *Datum vystavení a DUZP*) – žádný „15. den následujícího měsíce“, ten by u období končícího uprostřed měsíce sliboval víc, než zákon dává. DUZP je konec fakturovaného období, takže se to dá spočítat hned tady.

**Přesáhne-li prodleva 14 dnů, je to blokující otázka ve *Fázi 4***, ne poznámka na okraj – viz tam.

**Má-li klient vlastní timetracking, zkontroluj tady synchronizaci** – v `full` i v `preview`. Porovnej odpracovaný čas v Clockify za období s tím, co je v cílových místech u klienta – **stejným porovnáním po klíčích, jaké dělá `sync`** (`~/.claude/skills/invoicing/sync.md`, *Zrcadlení*), ne součtem hodin. Součet je slabší: chybějící a přebývající záznam téže délky se vyruší a kontrola ohlásí shodu, přestože doklad vyjde rozepsaný na nesprávné projekty. **Vypiš rozdíl jako dva seznamy – chybí a přebývá – na každé cílové místo**; součet uveď jen jako doplněk.

- **Sedí to** → pokračuj a napiš jednou větou, že sedí. **Přelitý čas přitom není rozdíl** – počítá se k datu ze svého prefixu (`sync.md`, *Uzávěrka dřív než faktura*).
- **Rozchází se to** → **zastav se a zeptej se**, jestli má napřed proběhnout `sync`. Sám ho nespouštěj: je to zápis do systému klienta a mění částku na faktuře.
- **Fakturuje-li se tomu klientovi z jeho systému** (dohoda to musí říkat výslovně), je rozdíl **blokující** – čas, který se tam nedostal, se nevyfakturuje. Řekni částku, o kterou jde, ne jen počet hodin.
- **Je-li okno u klienta už zavřené** (uplynula jeho uzávěrka), sync rozdíl nesrovná a **řekni to rovnou** – zbývá jen přesunout čas do dalšího měsíce podle `sync.md`, *Zpětný čas po uzávěrce*.

## Fáze 2 – Podklad

**Doklad se skládá podle souboru klienta, ne podle timesheetu.** Přečti soubor celý, ne jen sazbu: *Dohodu*, *Položky mimo timetracking*, *Předplacený kredit* i deník výjimek. Pak z něj sestav seznam toho, co za období patří na doklad. Timetracking je jen jeden z možných zdrojů a u některých klientů žádný:

- **Model fakturace** určuje základ dokladu. Může to být hodinovka podle skutečných hodin, pevná částka, částky po fázích nebo měsíční paušál (`~/Context/Business/invoicing.md`, *Jak se vyplňuje doklad*). **Neodvozuj ho z toho, že v timetrackingu jsou hodiny**, protože ty se logují i u paušálů. Není-li model zapsaný, zeptej se a odpověď rovnou zapiš. U paušálu se hodiny do částky nesčítají.
- **Kombinace se nevylučují.** Klient může mít paušál a hodiny nad něj, hodinovku a k ní jednorázovou položku, nebo různé sazby podle projektu či prefixu. Na doklad patří všechno, co dohoda za tohle období předepisuje.
- **Ujednání, které nezapadá do žádného kroku skillu, nevynechávej.** Uveď ho ve *Fázi 3* mezi body *K rozhodnutí* i s tím, jak bys ho promítl na doklad. Skill nemá rozhodnout, že se ho dohoda netýká, jen proto, že pro ni nemá připravený krok.

Kde jsou hodiny součástí dokladu, vytáhni odpracovaný čas za období a **aplikuj pravidla v tomhle pořadí**: obecná z `~/Context/Business/invoicing.md`, *Z timetrackingu na fakturu*, pak dohoda v souboru klienta, která je přebíjí.

**Fakturuje-li se klientovi z jeho systému**, ber podklad odtamtud, ne z Clockify (`~/.claude/skills/invoicing/sync.md`, *Uzávěrka dřív než faktura*). **Neřiď se přitom příznakem fakturovatelnosti ve vzdáleném systému** – ten odpovídá na otázku klienta, ne na otázku faktury. Třídy sazeb rozliš stejně jako v Clockify, tedy podle prefixů v popisu.

**Podezřelé záznamy nikdy neřeš potichu.** Odlož je do zvláštního seznamu a nechej rozhodnout ve *Fázi 3*:

- záznam bez popisu nebo s popisem, ze kterého nejde poznat, co to bylo
- běžící časovač
- položka delší než dvanáct hodin
- záznam mimo fakturované období
- projekt, který nemá soubor klienta

**Záznam, jehož popisek začíná `NF `, se vyřazuje bez ptaní** – je to jediný strojový signál, kterým se v timetrackingu značí nefakturovatelný čas (`~/Context/Business/invoicing.md`, *Z timetrackingu na fakturu*). Neoznačený záznam, který se podle popisku fakturovat nemá, ale **nevyřazuj sám** – patří mezi podezřelé výš.

**Má-li klient v dohodě očekávaný měsíční rozsah, porovnej ho se součtem.** Liší-li se řádově, **řekni to ve *Fázi 3*** a nabídni pustit napřed `recover` – po vystavení faktury se nenatrackovaný čas doplnit nedá, protože hranice období se posune a starší záznamy spadnou pod ni (`~/Context/Business/invoicing.md`, *Z timetrackingu na fakturu*).

**Sekci *Položky mimo timetracking* přečti vždycky, u každého klienta a v každém režimu.** Patří do ní dohodnuté položky, které na doklad přijdou bez podkladu v timetrackingu (`~/Context/Business/invoicing.md`, *Jak se vyplňuje doklad*, *Položky mimo timetracking*). **Chybí-li sekce, řekni to ve *Fázi 3*.** Nepředpokládej, že je prázdná. U každé položky rozhodni:

- **Měsíc položky spadá do fakturovaného období** → položka jde na doklad.
- **Měsíc je pozdější** → položka čeká. Ve *Fázi 3* ji uveď jako čekající.
- **Měsíc je dřívější než začátek období** → položka se vynechala. Patří mezi body *K rozhodnutí*.

**Zadá-li uživatel položku přímo v běhu, nejdřív ji zapiš do té sekce** ve tvaru podle šablony a commitni ji. Teprve potom s ní počítej. V `preview` ji nezapisuj a na konci řekni, že zapsaná není.

**Nezaokrouhluj jednotlivé záznamy.** Sečti je a zaokrouhli až součet – zaokrouhlené patnáctiminutovky nafouknou měsíc o hodiny a klient to pozná dřív než ty. **Na jakou jednotku a kterým směrem, drží `~/Context/Business/invoicing.md`, *Z timetrackingu na fakturu*** – neurčuj to sám.

## Fáze 3 – Kontrola s uživatelem

Nic se nevystavuje, dokud tohle neprojde. **Klientů bývá pár, tak jdi klient po klientovi**, ne dávkově.

Za každého ukaž:

```
**<Klient>** · <období> · <celková částka> <daňový režim>

- **Doklad:** vystavení <datum>, DUZP <datum>, splatnost <datum>
- **Na dokladu bude:** <období, které ponese text položky – liší-li se od skutečného, řekni to>
- **Položky:** <každá položka dokladu na řádek – text, který se vytiskne, množství × cena = částka a odkud je: timetracking, paušál, položka mimo timetracking, jiné ujednání>
- **Čeká:** <položky mimo timetracking odložené na pozdější měsíc, s tím měsícem>, nebo „nic“
- **Vyřazeno:** <co a proč>
- **K rozhodnutí:** <podezřelé záznamy, jeden po druhém>
```

Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo – `~/.claude/standards/rules.md`, *Styl odpovědí*.

**Klient s kreditem dostane místo dokladu odpis**, řádek na každý měsíc:

```
**<Klient>** · kredit · <měsíc> · <hodiny> h · zbývá <před> h → <po> h
```

**Vyčerpá-li se kredit, řekni to jako první věc u klienta, ne v řádku** – od toho měsíce se fakturuje, a přečerpané hodiny toho měsíce ukaž v běžném bloku výš jako doklad. Otázka na delší období se u odepsaných měsíců neklade; doklad nevzniká.

**Řádek *Položky* ukazuje texty, které se doopravdy vytisknou na doklad**, ne názvy projektů – slož je už tady podle `~/Context/Business/invoicing.md`, *Z timetrackingu na fakturu*. Je to jediné místo v celém běhu, kde se dělá **subjektivní úsudek** (zobecnění popisků z timetrackingu), takže se nesmí schovat až do *Fáze 4*.

Data v řádku *Doklad* urči podle `~/Context/Business/invoicing.md`, *Datum vystavení a DUZP*. **Číselná řada se ověřuje až ve *Fázi 4***, takže v režimu `preview` je datum vystavení předběžné – a s ním i **splatnost**, protože se z něj počítá. Řekni to.

**Pokrývá-li období víc než jeden kalendářní měsíc, zeptej se, co má být na dokladu.** Varianty i výchozí volbu drží `~/Context/Business/invoicing.md`, *Období delší než jeden měsíc* – **nevybírej za uživatele a nepředpokládej výchozí variantu mlčky**. **Je-li odpověď předem zapsaná v deníku výjimek klienta, neptej se znovu** – potvrzení k § 28 ve *Fázi 4* to ale neruší. Odpověď určí text položky ve *Fázi 4* i znění mailu ve *Fázi 5*, a **zapíše se do deníku výjimek** jako každá jiná odchylka.

Ptej se přes `AskUserQuestion` a **postupně** (`~/.claude/standards/rules.md`, *Ptej se postupně, ne všechno najednou*).

**Co se dohodne odchylně, zapiš rovnou** do deníku výjimek v souboru klienta jako datovaný záznam ve tvaru `- **YYYY-MM-DD** – <co se dohodlo a proč>`, s datem z `date +%F`. **Zápis rovnou commitni** – `~/Context/` má zapnutý autocommit a rozpracovaný soubor by jinak posbírala jiná session pod nesouvisející hlavičkou. Dohoda, která se nezapíše, za rok neexistuje – a spor o částku se pak vede proti paměti.

**Tady končí režim `preview`.** Pokračuje se do *Fáze 4* jen v režimu `full`.

## Fáze 4 – Vystavení

**Nejdřív ověř skutečný stav, pak vystav** (`~/.claude/standards/rules.md`, *Před nevratnou akcí ověř skutečný stav*): zkontroluj, že pro toho klienta a to období faktura ještě neexistuje. Doklad se špatně ruší a klient ho vidí.

**Vystavuj klienty vzestupně podle konce jejich období.** Doklad vystavený dneškem posune hranici číselné řady, takže obrácené pořadí si kolize vyrábí samo.

**Kontrola řady se dělá u každého dokladu znovu, odpověď na kolizi se neopakuje.** Jsou to dvě různé věci: **ověřit** stav řady musíš pokaždé, protože ho posouvá každá vystavená faktura včetně těch tvých; **ptát se** znovu na totéž rozhodnutí („jaké datum použít, když je řada dál“) v téže dávce nemusíš.

Za každého klienta:

1. **Urči datum vystavení, DUZP a splatnost** podle `~/Context/Business/invoicing.md`, *Datum vystavení a DUZP* a *Daně a náležitosti*. Končí-li období posledním uzavřeným měsícem, obojí datum je poslední den toho období; končí-li dneškem podle volby ve *Fázi 1*, obojí je dnešek.

   **Splatnost běží od data vystavení na dokladu**, ne od dneška. Jak je dlouhá, určuje **žebřík podle prodlevy** mezi tím datem a dnem, kdy doklad doopravdy vzniká. **Sjednaná splatnost v souboru klienta žebřík přebíjí** – je to dohoda s protistranou, ne odhad, a automatika ji přepsat nesmí. Hodnota `standardní` v souboru klienta znamená, že žádná dohoda není a jede se podle žebříku. **Pokrývá-li doklad víc než jeden kalendářní měsíc, je splatnost měsíc bez ohledu na prodlevu** – žebřík měří rozdíl dat, ne velikost faktury. Čísla drží `invoicing.md`, *Daně a náležitosti*; **nedomýšlej je a neopisuj sem**.

   **Vyjde-li splatnost dřív než dnešek, nevystavuj a zeptej se** přes `AskUserQuestion`, jaké datum splatnosti nastavit. Náhradní datum si nedopočítávej – je to doklad, který by klient dostal už propadlý.
2. **Vystavuješ-li víc než 14 dnů po DUZP – nebo pokrývá-li doklad víc než jeden kalendářní měsíc – zastav se a vyžádej si potvrzení.** § 28 zákona o DPH ukládá vystavit doklad do 15 dnů od DUZP, takže se tou lhůtou právě prochází. Řekni to nahoře a zeptej se přes `AskUserQuestion` **explicitně na to, jestli je takový postup s klientem domluvený, jestli s ním počítá a jestli ho odsouhlasil.** Bez potvrzení nevystavuj – **ticho ani „jeď dál“ potvrzení není** a domýšlet si ho nesmíš. Je to jediné místo, kde se skill ptá na něco, co se nedá vyčíst z dat.

   **Delší období se ptá vždycky, i když výpočet vyjde v pořádku** – DUZP je konec období, takže u dohnané fakturace se prodleva spočítá z posledního měsíce a lhůta vypadá dodržená. Proč to tak je, vysvětluje `~/Context/Business/invoicing.md`, *Daně a náležitosti*.

3. **Před zpětným datem ověř číselnou řadu:** v systému nesmí být žádná faktura s pozdějším datem vystavení, než jaké chceš nastavit – **napříč celým účtem, ne jen u toho klienta**. Není-li tam žádná, vystav se zpětným datem. **Je-li tam, nevystavuj a zeptej se přes `AskUserQuestion`**, jaké datum vystavení použít; jako první volbu nabídni dnešek. DUZP se tou otázkou nemění – zůstává posledním dnem fakturovaného období.

   **Posunulo-li se datum vystavení, přepočítej splatnost znovu** – od nového data a s novou prodlevou, tedy i s možná jiným pásmem žebříku. Splatnost z kroku 1 platí jen tehdy, když datum zůstalo. **Měsíční splatnost u delšího období přepočet neshodí** – je to strop nad žebříkem, ne jeho pásmo.
4. **Vystav doklad** podle odsouhlaseného podkladu:

   - **U hodinovky vyplň množství, měrnou jednotku a jednotkovou cenu zvlášť** a součin nech spočítat systém. Jen celková částka nestačí – `~/Context/Business/invoicing.md`, *Jak se vyplňuje doklad*. **Sazbu ber ze souboru klienta; nemá-li ji, z `~/Context/Business/pricing.md`** – ceník je zdroj pravdy a klient ho smí přebít, ne naopak.
   - **Text položky slož** podle *Z timetrackingu na fakturu* v témže souboru: typ práce **zobecni** z popisků v Clockify, neopisuj je. Pokrývá-li období víc měsíců, řiď se navíc volbou z *Fáze 3*.
   - **Položky, které nevznikly z timetrackingu**, tedy paušál, pevnou částku, fázi nebo jiné ujednání, vyplň tak, jak je předepisuje soubor klienta. Částku ani text si nedomýšlej. Nepředepisuje-li soubor text, použij ten, který uživatel odsouhlasil ve *Fázi 3*.
   - **Položky mimo timetracking** odsouhlasené ve *Fázi 3* přidej každou jako samostatný řádek dokladu. Nesčítej je s hodinami z timetrackingu, ani když mají stejný projekt a sazbu. Do interní poznámky `clockify:` se nepromítají.
   - **Daňový režim a povinné údaje** ber ze souboru klienta a z *Daně a náležitosti* – **nedomýšlej je**.
5. **Zapiš do dokladu období strojově čitelně.** Bez toho příští běh neví, odkud počítat, a začne se ptát na něco, co se dalo zapsat teď.
6. Přečti doklad zpátky ze systému a ověř číslo, částku, odběratele, období **a všechna tři data – vystavení, DUZP i splatnost**. Splatnost se posílá v jiné jednotce, než v jaké se ukázala ve *Fázi 3* (dny místo data), takže je to jediné pole, kde se chyba o den jinak nemá jak projevit. Nespoléhej na to, že zápis prošel.
7. **Byla na dokladu položka mimo timetracking, smaž ji teď ze sekce v souboru klienta.** Do deníku výjimek k ní zapiš, na kterém dokladu skončila. Obojí commitni jmenovanou cestou. Dokud položka v sekci zůstává, příští běh ji přidá znovu. Ze sekce ji proto smaž, až když je doklad zpátky přečtený.

**Měsíc krytý kreditem se nevystavuje, ale odepíše:** připiš do evidence v souboru klienta řádek `| <YYYY-MM> | <hodiny> h | <zbývá> h |` za posledním měsícem, přečti tabulku zpátky a ověř, že zbytek je předchozí zbytek minus odpis. **Zápis commitni jmenovanou cestou** v klientské složce a pushni, má-li remote – je to tatáž povinnost jako u deníku výjimek ve *Fázi 3*. Přečerpané hodiny měsíce, kdy kredit došel, se vystaví podle kroků výš.

**Selže-li vystavení uprostřed dávky, pokračuj dalším klientem.** Ostatní faktury nejsou čím vinné. Selhání si poznamenej a vypiš ho v závěru jmenovitě.

## Fáze 5 – Přílohy a draft

1. Stáhni **PDF faktury** ze systému a **PDF výkazů hodin** z timetrackingu. **Nejdřív si ale ověř v dohodě klienta, které přílohy chce** – klient, který má odpracovaný čas u sebe (`sync`), může mít výkazy vypnuté; pak se nestahují vůbec a v mailu se místo nich odkáže tam, kde ty časy jsou. **Výkaz je jeden na projekt a měsíc** – žádná podmínka podle počtu projektů se neposuzuje; u klienta s jedním projektem z toho vyjde jeden výkaz sám. Konkrétní požadavky i důvod, proč se delší období nedá stáhnout vcelku, drží `~/Context/Business/invoicing.md`, *Přístupy*.

   **Každou přílohu přejmenuj** podle `~/Context/Business/invoicing.md`, *Pojmenování příloh*. Strojový název z obou systémů se nepřikládá – klient si doklad zakládá do účetnictví a musí ho podle jména najít.
2. **Ověř oba soubory, než je přiložíš:** nejsou prázdné a období ve výkazu sedí se **skutečným fakturovaným obdobím** – tedy s tím, co je v interní poznámce dokladu, ne nutně s tím, co je vytištěné na položce. Prázdná nebo posunutá příloha je horší než žádná – klient ji vezme jako doklad.

   **U delšího období se výkaz s textem položky schválně rozchází.** Nese-li doklad podle volby z *Fáze 3* formálně jen poslední měsíc, výkaz pokrývá celý rozsah – a je to správně, ne chyba k opravě. Kontrolou tady prochází shoda se **skutečným** obdobím; kdyby se porovnávalo s dokladem, guard by u té největší faktury zastavil právě ten stav, který má být.
3. Sestav mail podle `~/Context/Business/invoicing.md`, *Šablona mailu*. Adresáta i **oslovení a podpis** vezmi ze souboru klienta – je to tam povinné pole a **neodhaduje se z profilu ani z předchozí korespondence**. Rozhoduje vztah ke konkrétnímu adresátovi dokladu, ne k firmě.

   **Nese-li doklad u delšího období formálně jen poslední měsíc, musí skutečný rozsah zaznít v mailu** – je to jediné místo, kde se ho klient dozví. Vynechat ho tam znamená poslat doklad, ze kterého nejde poznat, za co se platí.
   **Odpis z kreditu dostane draft taky** – stejným postupem, jen bez faktury: přílohou jsou výkazy za odepsané měsíce a text i předmět drží `~/Context/Business/invoicing.md`, *Mail k odpisu z kreditu*. Hodiny a zbytek do něj ber z řádků, které ses do evidence právě zapsal a přečetl zpátky. **Měsíc s nulou draft nedostane.**
4. **Založ draft a tím skonči.** Odeslání nenabízej a nikdy ho neprováděj – ani jako poslední krok, ani jako laskavost.

**Tvrdá stopka: požádá-li uživatel uprostřed běhu o odeslání, neodesílej.** Řekni, že draft je hotový a odeslání je na něm, a jmenuj, kde ho najde. Neptej se na potvrzení – potvrzovací otázka je jen delší cesta k témuž a svádí k tomu ji odklepnout.

**Proč to přebíjí i výslovný pokyn.** Vypadá to jako rozpor s pravidlem, že potvrzený požadavek uživatele je jeho rozhodnutí (`~/.claude/standards/rules.md`, *Přednost pravidel*, bod 1). Není: tenhle zákaz **je** uživatelovo rozhodnutí, jen učiněné předem a s chladnou hlavou. Proto „pošli to, spěchám“ uprostřed běhu neruší předchozí volbu – je to přesně ta situace, kvůli které si ji nastavil. Zrušit ji jde jedině změnou tohohle skillu, ne pobídkou za běhu.

**Drží to mechanismus, ne jen tenhle text.** Odesílací nástroje Gmailu (`send_message`, `reply`, `forward`, obojí `trash_*`) jsou od 8. 9. 2026 v `deny` v `~/.claude/settings.json`, takže je nelze zavolat ani omylem, ani po pobídce. `create_draft` zakázaný není – ten skill potřebuje.

**Hranice vede u odeslání a nevratného zásahu, ne u konceptu.** Povolené zůstávají nástroje pracující s koncepty a štítky (`create_draft`, `update_draft`, `list_drafts`, značkování): skill je potřebuje a jejich následek jde vzít zpět. Zakázané je to, co pošle poštu ven nebo nevratně sáhne na cizí zprávu. Je to vědomá čára, ne výčet toho, co padlo do oka.

**Nezkoušej to řešit přes `allowed-tools` v hlavičce.** Podle dokumentace Claude Code to pole nástroje **neomezuje**, jen předschvaluje: *„It does not restrict which tools are available: every tool remains callable.“* Skill hlavičku kdysi měl, zrušil ji commit 622fa4f s odůvodněním, že „zakazoval Gmail MCP“ – jenže nic nezakazoval, jen se pak na `create_draft` doptával. Vrátit ji tedy zákaz nezajistí; jedinou hranicí je `deny` (`~/.claude/standards/rules.md`, *Přednost pravidel*: kde má hranice držet, tam k ní patří mechanismus).

## Fáze 6 – Závěr

```
## Fakturace <období>

| Klient | Období | Hodiny | Částka | Vystaveno | Doklad | Draft |
|---|---|---|---|---|---|---|
| … | … | … | … | <datum> | <číslo> | ano / ne |

**Zapsané dohody**
- <klient>: <co přibylo do deníku výjimek>, nebo „nic“

**Kredit**
- <klient>: odepsáno <hodiny> h za <měsíce>, zbývá <h> h, draft s timesheetem ano / ne – nebo „vyčerpán, od <měsíc> se fakturuje“

**Nevyřízené**
- <klient>: <co selhalo a kde to zůstalo stát>, nebo „nic“

**Nezkontrolováno**
- <co se neověřilo a proč>, nebo „nic“
```

Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo – `~/.claude/standards/rules.md`, *Styl odpovědí*.

Blok *Kredit* vynech, nemá-li ho žádný klient v záběru. Klient, kterému se jen odepisovalo, do tabulky nepatří – doklad nevznikl.

Ve sloupci *Vystaveno* uveď datum vystavení; **liší-li se od DUZP** kvůli kolizi v číselné řadě, uveď obojí – jinak po běhu nezůstane stopa, že se datum posunulo jinam, než pravidlo předepisuje.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Faktury jsou vystavené a ověřené, drafty čekají v mailu – můžeš je odeslat. Až je odešleš, napiš mi a označím je ve Fakturoidu za odeslané.`
- `Hotové to není – brání tomu: <konkrétní seznam>.`

## Po odeslání – označení za odeslanou

**Spouští to jen uživatelovo potvrzení, že mail odeslal** – v téže session po závěru, nebo později větou typu „20260007 je odeslaná“. Neodvozuj to sám ze stavu mailu (zmizelý draft, zpráva v Odeslaných): draft mohl uživatel smazat a poslat doklad jinou cestou, nebo ho neposlat vůbec.

Je to protějšek tlačítka *Pouze označit za odeslanou* ve Fakturoidu: systém nic neodešle, jen přestane doklad vést jako neodeslaný. **S odesíláním mailu to nemá nic společného** a zákaz z *Fáze 5* tím nijak neslábne – odeslání dál dělá jen uživatel, tenhle krok jen zapíše, že se stalo.

1. **Urči, které doklady potvrzení pokrývá.** Jmenuje-li uživatel čísla nebo klienty, jen ty. Řekne-li jen „odesláno“ a draftů vzniklo v běhu víc, zeptej se, které – ne každý draft musel odejít.
2. **Přečti stav dokladu.** Označuje se jen doklad ve stavu `open`. Je-li v jiném (`sent`, `paid`, `overdue`, `cancelled`, `uncollectible`), nesahej na něj a řekni, v jakém je – zaplacený doklad přepnutý zpátky by lhal.
3. **Označ ho** voláním z `~/Context/Business/invoicing.md`, *Ověřené požadavky na Fakturoid*.
4. **Přečti doklad zpátky** a ověř, že stav je `sent`. Vrátí-li systém chybu nebo stav nesedí, vypiš to u dokladu jmenovitě; ostatní doklady tím nejsou čím vinné.

Výstup je jedna věta na doklad: číslo, klient, nový stav.

------

## Režim `preview`

Doběhne *Fází 3* a tam skončí. **Nevystaví doklad, nezaloží draft a nezapíše ani do deníku výjimek, ani do evidence kreditu, ani do položek mimo timetracking** – náhled, po kterém zůstane stopa, není náhled.

K čemu je: zjistit před koncem měsíce, kolik toho je, jestli sedí hodiny, a jestli v timetrackingu nechybí nebo nepřebývá něco, co se má srovnat dřív, než vznikne doklad.

Vypiš tutéž tabulku jako v závěru, sloupce *Doklad* a *Draft* vynech, a přidej seznam toho, co by ještě chtělo rozhodnout. U sloupce *Vystaveno* připomeň, že **číselná řada se v náhledu neověřuje** – při ostrém běhu se datum může posunout.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Náhled je hotový a nic se nevystavilo – až to bude sedět, pusť /invoicing full.`
- `Náhled hotový není – brání tomu: <konkrétní seznam>.`

------

## Režim `recover`

Dohledá **čas, který se zapomněl natrackovat**, a ukáže tipy s doložením. Nevystavuje, nezakládá draft a **sám od sebe nezapisuje do timetrackingu ani do souboru klienta** – viz *Co skill nedělá*, kde je i to, čím se od toho liší blok uložený na uživatelův pokyn.

**Proběhl-li nad klientem `recover` už dřív**, přečti si jeho blok dřív, než začneš – ne abys z něj opisoval, ale abys na konci uměl říct, co z něj po dnešním ověření padlo. **Vyvrácený nález z minula je nejcennější výstup, jaký druhý běh má**: ukazuje, která třída doložení neobstojí, a proto se vypisuje jmenovitě (výjimka ze zákazu v `recover.md`, *Ověření nálezů*).

**Jméno je `recover` a nepřejmenovává se.** Zvažovalo se `restore` a `rescue`; obojí zamítnuto, protože slibuje, že se něco opraví – a tenhle režim nic nezapisuje. `reconcile` je odborně přesnější, ale česky se o něm nedá mluvit, a `gaps` pojmenovává výstup místo akce.

Katalog zdrojů, heuristiky a tvar zadání pro sběrače drží `~/.claude/skills/invoicing/recover.md`. Přístupy a identifikátory drží `~/Context/Business/invoicing.md`, *Stopy práce*. **Tenhle režim si zdroje nevymýšlí** – sáhne jen na ty, které má klient vyjmenované; na ostatní se nedívá a vypíše je jako slepá místa.

1. **Příprava.** Načti soubor klienta a z něj sekci *Stopy práce*. **Chybí-li, skonči a řekni to** – bez identifikátorů nemá režim kde hledat a plošné hledání jména klienta napříč schránkou vyrábí falešné tipy. Ověř dostupnost každého vyjmenovaného zdroje a **nedostupné si poznamenej jako slepé místo**, neignoruj je.
2. **Rozsah.** Výchozí je **nevyfakturované období** – hranici zjisti stejně jako v *Fázi 1*, tedy z poslední faktury, a konec je dnešek. Stojí-li za režimem měsíc nebo datum (`/invoicing recover <klient> 2026-05`), platí ten; **řekni v takovém případě nahlas, že už vyfakturované období se dohnat nedá** a slouží jen k poznání, kolik času systematicky uniká.
3. **Sběr.** Pusť sběrače paralelně, jeden na zdroj, se zadáním z `recover.md`, *Zadání pro sběrače*. Vracejí stopy, ne závěry.
4. **Srovnání.** Slij stopy do shluků, porovnej je se záznamy v Clockify a odděl tři výsledky: **chybí** (v Clockify není nic), **natrackováno jinam** (čas je tam pod jiným projektem), **sedí** (nález nevzniká).

   **Odevzdané výstupy se srovnávají obráceně** – ne proti dni, kdy stopa leží, ale proti oknu **před** ním: hotový dokument dokládá práci, která mu předcházela. Postup a to, proč z toho nevzniká číslo, ale otázka, drží `recover.md`, *Odevzdaný výstup jako stopa*.
5. **Ověření.** Každý kandidát projde ověřovatelem, jehož úkolem je ho **vyvrátit** – `recover.md`, *Ověření nálezů*. Co ověření nepřežije, se nezobrazí.
6. **Výstup.** Tabulka podle `recover.md`, *Výstup*, a pod ní natrackováno jinam, slepá místa, otázky k rozsahu a součet – **v tomhle pořadí**, které závazně drží `recover.md`.

**Nefakturovatelný čas se dohledává taky.** Nemá cenu pro fakturu, ale má ji pro přehled o tom, kolik práce se do klienta doopravdy vlilo – označ ho a do součtu nepočítej.

**Nespouštěj `recover` uprostřed `full`.** Je to samostatný běh: fakturace stojí na tom, co v timetrackingu je, kdežto recover na úsudku o tom, co v něm chybí. Smíchat obojí znamená vystavit doklad na odhad.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Dohledávání je hotové a nálezy ověřené – doplnit je do timetrackingu musíš ty.`
- `Dohledání hotové není – brání tomu: <konkrétní seznam>.`

## Režim `sync`

Přepíše odpracovaný čas z Clockify do timetrackingu klienta. **Jediný režim, který zapisuje do cizího systému**, a jediný, který něco maže.

**Pouští se jen u klienta, který má v souboru vyplněný vzdálený timetracking.** Nemá-li ho, skonči a řekni to – ne jako chybu, ale jako fakt, že tenhle klient svůj timetracking nechce.

Mechaniku, pravidla oken a tvar prefixu drží `~/.claude/skills/invoicing/sync.md`. Přístupy, tokeny a konkrétní volání drží `~/Context/Business/invoicing.md`, *Vzdálený timetracking klienta*.

1. **Příprava.** Načti soubor klienta: cílová místa, uzávěrku a to, jestli se z jeho systému fakturuje. **Nemá-li cílové místo žádný projekt klienta, skonči** – bez něj není kam psát a hádat se nesmí. **Chybí-li jen u některého projektu, přeskoč ten projekt** a vypiš ho jmenovitě i s hodinami, které se kvůli tomu nesynchronizovaly; zbytek proběhne. Zastavit celý běh kvůli jednomu projektu znamená u klienta s uzávěrkou nechat propadnout i čas, který cíl má. **Ověř přístup do vzdáleného systému** podle `~/Context/Business/invoicing.md`, *Vzdálený timetracking klienta* – tenhle režim do něj jako jediný zapisuje, a *Fáze 0* ho neověřuje.
2. **Okno.** Urči otevřené okno stejně jako *Fáze 1*, tedy od konce posledního vyfakturovaného období. **Má-li klient uzávěrku, zkrať okno podle ní** a řekni, který měsíc se tím zavřel.
3. **Načtení obou stran.** Obě strany za okno čtení **rozšířené o den na obou stranách** (proti posunu časových pásem), vzdálený systém **jen z cílových míst**. Z výsledku ponech **jen Honzovy záznamy, ověřené z dat** – filtr v dotazu se může tiše ignorovat a pak by se mazala cizí práce. **Ověř, že jsi obě strany dočetl celé** – stránkování i HTTP status; prázdná strana se přijímá jen proti odpovědi `200` s nulovým počtem, ne proti prázdnému poli. **Nedá-li se dočtení doložit, smíš zakládat, ale ne mazat.** Pojistky drží `sync.md`, *Čtení obou stran*, a žádná se nevynechává.
4. **Srovnání.** Zrcadli **každou dvojici projekt → cílové místo zvlášť** a spočítej, co založit, co upravit, kde opravit příznak a co smazat (`sync.md`, *Párovací klíč* a *Co se s čím dělá*). Zvlášť odděl **zpětný čas po uzávěrce**: co patří do právě uzavřeného měsíce, přesuň na první den aktuálního s povinným prefixem; co je starší, **propadá** a jen se vypíše.
5. **Potvrzení.** Porovnej počty se zdrojem (`sync.md`, *Než zapíšeš*) a ukaž souhrn – kolik založit, kolik upravit, **co smazat jmenovitě**. Teprve pak zapisuj, a to **v pořadí: nejdřív zakládání, pak mazání**. **Mazání bez potvrzení neproběhne nikdy**; u klienta, který se fakturuje ze svého systému, se potvrzuje **celá dávka pokaždé**, jinde při prvním běhu.
6. **Zápis a kontrola.** Proveď to, znovu načti vzdálený systém a **ověř, že strany sedí**. Neohlašuj hotovo z návratových kódů zápisu.
7. **Deník.** Přelilo se nebo propadlo něco? Zapiš jeden řádek do *Deníku přelitého a propadlého času* v souboru klienta (`sync.md`, *Zápis do deníku*). Prázdný běh se nezapisuje.

**Výstup** je tabulka *založeno / upraveno / smazáno / propadlo* a pod ní součet hodin na obou stranách. **Propadlý čas se vypisuje jmenovitě i s částkou, o kterou přišel** – je to jediné místo, kde se to Honza dozví.

**`sync` se nespouští uvnitř `full` ani `preview` sám od sebe.** Fakturace ho jen **nabídne**, když se strany rozejdou (*Fáze 1*), a čeká na rozhodnutí.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Synchronizace hotová a ověřená – <X> založeno, <Y> upraveno, <Z> smazáno.`
- `Synchronizace hotová, ale <N> h za <měsíc> propadlo po uzávěrce – nevyfakturuje se.`
- `Nesynchronizoval jsem nic, protože <důvod>.`
