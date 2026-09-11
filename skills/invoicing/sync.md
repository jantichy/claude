# Synchronizace do timetrackingu klienta

Referenční soubor k režimu `sync` skillu `/invoicing`. Drží **mechaniku zrcadlení a pravidla oken**; postup, kdy se co dělá, je v `SKILL.md`, *Režim `sync`*. Přístupy, tokeny a konkrétní volání do systémů drží `~/Dev/context/business/invoicing.md`, *Vzdálený timetracking klienta* – **sem se nikdy neopisují**, tenhle soubor je veřejný.

## Obsah

- *K čemu to je* – proč se čas vede dvakrát
- *Jednosměrnost* – co je zdroj pravdy a co kopie
- *Otevřené okno* – kdy se do vzdáleného systému smí sahat
- *Uzávěrka dřív než faktura* – klient s vlastní lhůtou
- *Zpětný čas po uzávěrce* – co se přesouvá, co propadá, tvar prefixu a skládání za sebe
- *Co se přenáší* – které záznamy jdou ven a s jakým příznakem
- *Zrcadlení* – čtení obou stran, párovací klíč, co se s čím dělá, co ověřit před zápisem
- *Zápis do deníku* – jediné, co režim ukládá k sobě
- *Hranice* – co režim nesmí

------

## K čemu to je

Někteří klienti chtějí odpracovaný čas i ve **svém** timetrackingu. Honzův primární nástroj je Clockify a **žádný druhý se paralelně neobsluhuje** – opisovat záznamy ručně je práce navíc a rozejde se to hned, jak se v Clockify něco opraví.

Režim `sync` proto vezme Clockify a **udělá z části klientova systému jeho obraz**.

## Jednosměrnost

**Clockify je zdroj pravdy, vzdálený systém je kopie.** Nikdy naopak a nikdy obousměrně.

Plyne z toho všechno ostatní: co v Clockify není, nemá ve vzdáleném systému co dělat; co se v Clockify změní – **včetně pouhého popisku** –, se ve vzdáleném systému opraví; co se v Clockify smaže, se smaže i tam. Ruční zásah přímo ve vzdáleném systému **se nepovažuje za data, ale za odchylku** a příští běh ho srovná.

**Ke klientovi se tím pravidlem zavazuješ:** cílové místo ve vzdáleném systému je vyhrazené pro synchronizovaný čas a nikdo do něj netrackuje ručně. Kde to neplatí, se `sync` nepouští.

## Otevřené okno

**Sahat se smí jen do dosud nevyfakturovaného období.** Vystavením faktury se období **zavírá** a od té chvíle je v obou systémech neměnné – ani přidat, ani opravit, ani smazat.

Je to obecné pravidlo pro každý vzdálený timetracking, ne vlastnost jednoho klienta. Důvod je účetní: doklad tvrdí o období konkrétní počet hodin a zpětná změna podkladu z něj dělá tvrzení, které se nedá doložit.

**Jsou to dvě okna a pletou se snadno.** *Okno zápisu* je tohle – kam se smí sáhnout. *Okno čtení* sahá o tři měsíce dál do minulosti a slouží jen k tomu, aby se našel zpětný a propadlý čas (*Zpětný čas po uzávěrce*). Čtení nikdy neopravňuje k zápisu.

**Hranice se čte odtud, odkud ji čte fakturace** – `~/Dev/context/business/invoicing.md`, *Odkud se ví, co už je vyfakturované*. Vlastní hranici si režim neurčuje.

## Uzávěrka dřív než faktura

Klient může mít lhůtu **kratší**, než je vystavení faktury: „měsíc se uzavírá do třetího pracovního dne měsíce následujícího“. Pak platí ta lhůta, ne datum dokladu.

**Uzávěrka klienta je v jeho souboru v `invoicing/`.** Není-li tam žádná, okno zavírá až faktura.

**Přelitý čas není rozdíl mezi stranami.** Porovnává-li se Clockify se vzdáleným systémem – ať už v zrcadlení, nebo při kontrole před fakturací –, **počítá se přelitý záznam k datu ze svého prefixu**, ne ke dni, na kterém leží. Bez toho by u každého klienta po přelití vycházel rozdíl, který rozdíl není, a fakturace by se zastavovala pokaždé.

**Pro podklad faktury platí pravý opak a je to schválně.** Datum z prefixu je **výhradně párovací pomůcka**; při sestavování dokladu se přelitý záznam počítá **ke dni, na kterém leží**, tedy do měsíce, do kterého se přelil. Jinak by vypadl ze svého nového měsíce, do starého by ho nepustila uzávěrka a nespadl by na žádnou fakturu.

**Má-li klient uzávěrku, mění se i to, z čeho se počítá doklad:** fakturuje se **to, co je ve vzdáleném systému**, ne co je v Clockify. Je to výjimka z obecného pravidla o zdroji pravdy a **musí být napsaná v dohodě klienta**, jinak neplatí.

Praktický důsledek, který se musí říct nahlas: **selže-li sync, vyjde faktura nižší.** Proto fakturace u takového klienta začíná kontrolou synchronizace – viz `SKILL.md`, *Fáze 1*.

## Zpětný čas po uzávěrce

Čas doplněný do Clockify až po uzávěrce se **nezahazuje automaticky**. Rozhoduje, ke kterému měsíci patří:

| Čas patří do | Co s ním |
|---|---|
| **právě uzavřeného měsíce** | přesune se do **aktuálního měsíce, na jeho první den**, s prefixem v popisu; vyfakturuje se s ním |
| **měsíce ještě staršího** | **propadá** – do vzdáleného systému nejde a nefakturuje se |
| období otevřeného okna | zapíše se normálně na svoje datum |

**Propadlý čas se hledá pod dolní hranou okna, jinak ho není odkud vzít.** Okno zápisu začíná na hranici poslední faktury, ale čas, který má propadnout, je z definice starší – **čtení Clockify proto sahá o tři měsíce dál do minulosti než okno zápisu**. Jsou to dvě různá okna a nesmí se splést: **okno zápisu** říká, kam se smí sáhnout, **okno čtení** jen to, co se vezme v úvahu. Bez toho rozlišení zůstane deník propadlého času navždy prázdný, i když se propadá.

### Tvar prefixu

Pevný, protože se z něj zpětně čte datum:

```
Zpětně vytrackovaný čas za 12. července 2026: <původní popis z Clockify>
```

- **Bez vodicí nuly** ve dni, měsíc **slovem ve druhém pádě**, rok čtyřmístně, pak **dvojtečka a jedna mezera**.
- **Prefix se nikdy nevnořuje.** Přelévá-li se záznam, který prefix už má, původní se **nahradí**, ne obalí.
- **Má-li popis prefix sazby** (`NF `, `SDÍLENÉ ` a další podle klienta), **stojí vpředu a prefix přelití jde až za něj**: `NF Zpětně vytrackovaný čas za 12. července 2026: …`. Klasifikace sazeb se dělá podle toho, čím popis začíná – kdyby ho přelití zakrylo, nefakturovatelný čas by se vyfakturoval a sdílená práce odešla plnou sazbou.

Datum v prefixu je **skutečné datum práce** z Clockify, česky vypsané. Nese dvě funkce naráz: klient vidí, že se nesnažíš propašovat starý čas do nového měsíce, a **režim podle něj ten záznam příště pozná**.

### Skládání za sebe

**Přelité záznamy se v cílovém místě skládají od půlnoci za sebou** – první v 00:00, druhý hned po jeho konci, v pořadí, v jakém práce původně proběhla, a **v každém cílovém místě zvlášť**. Vzdálený systém obvykle nechce jen počet hodin, ale interval od–do; kdyby přelité záznamy začínaly ve stejnou chvíli, klient uvidí překrývající se čas a přestane výkazu věřit.

**Druhá dávka téhož měsíce nezačíná znovu od půlnoci**, ale **navazuje za poslední přelitý záznam, který v tom cílovém místě na tom dni už leží**. Zapomenutý čas se doplňuje průběžně, takže přelití proběhne za měsíc klidně třikrát – a bez tohohle pravidla by se dávky navzájem překryly.

**Propadlý čas se nemaže z Clockify** a ve výpisu se vypíše jmenovitě i se součtem. Je to nefakturovaná práce, ne omyl, a Honza má právo vidět, kolik ho ta prodleva stála.

## Co se přenáší

**Rozsah určuje soubor klienta, ne režim.** Výchozí je, že jde ven **všechen čas na projektech toho klienta** – tedy i nefakturovatelný a jinak sazbený –, protože klient má u sebe vidět celý objem odvedené práce. Chce-li klient jen část, stojí to v jeho souboru.

**Příznak fakturovatelnosti se odvozuje podle pravidla klienta, ne podle prefixu v popisu.** U klienta, který sám přeúčtovává práci dál, závisí na tom, jestli je projekt klientský, nebo interní – v interním nemůže vzniknout fakturovatelný čas vůbec. **Pravidlo patří do souboru klienta a bez něj se příznak nedomýšlí**; „co nemá prefix, je fakturovatelné“ je nejběžnější případ, ne zákon.

**Příznak fakturovatelnosti ve vzdáleném systému je informace pro klienta, ne rozhodnutí o faktuře.** Záznam může být ve vzdáleném systému non-billable a přesto se fakturovat – typicky práce s jinou sazbou. **Podklad faktury se proto skládá podle prefixů v popisu**, stejně jako by se skládal z Clockify; brát ven jen billable záznamy znamená tiše zahodit část výdělku.

## Zrcadlení

Režim si **nedrží žádný stav** – žádnou mapovací tabulku, žádné ID v poznámce. Pokaždé si přečte obě strany a srovná je. Stav, který se rozejde, je horší než jeho absence, a u kopie se rozejde vždycky.

**Zrcadlí se každá dvojice projekt → cílové místo zvlášť**, ne všechna cílová místa jako jedna hromada. Bez toho by záznam ležící v nesprávném tasku vyšel jako shoda – počty by seděly – a zůstal tam napořád, s cizím příznakem fakturovatelnosti a v nesprávné položce na dokladu.

### Čtení obou stran

1. **Načti Clockify** za okno čtení, jen projekty toho klienta.
2. **Načti vzdálený systém** za totéž okno, jen z cílových míst ze souboru klienta, a **z výsledku ponech jen Honzovy záznamy, ověřené z dat** – filtr v dotazu se může tiše ignorovat a pak by se mazala cizí práce.
3. **Obě čtení rozšiř o den na obou stranách okna a ořízni až lokálně.** Obě API filtrují podle UTC a obojí ukládá lokální čas, takže záznam z časů kolem půlnoci padne v dotazu do jiného dne. **Na každé straně má to opomenutí jiný a stejně drahý následek:** ve vzdáleném systému se existující záznam nenajde a založí se podruhé, v Clockify se protějšek nenajde a kopie se smaže.

   **Rozšíření slouží výhradně k párování, nikdy jako rozsah pro zápis a mazání.** Záznam, který leží mimo okno zápisu, se jen započítá do porovnání; sahat se na něj nesmí.

4. **Převáděj časy podle pásma `Europe/Prague` a posun počítej k okamžiku každého záznamu**, nikdy jako konstantu. Doložený posun `+2 h` platí pro letní čas; po přechodu na zimní je to `+1 h` a pevně zadaná konstanta by rozhodila každý záznam po 25. říjnu o hodinu – tedy i jeho zařazení do dne.

5. **Ověř, že jsi obě strany dočetl celé.** Clockify stránkuje parametrem `page`, vzdálený systém podle `meta.page.hasMore`; **nedočtená stránka se neprojeví jako chyba, ale jako chybějící záznamy**. A **kontroluj návratový kód i HTTP status** – `curl` bez `--fail` vrací nulu i na `401`, takže vypršelý token vypadá jako prázdná strana.

   **Prázdná strana se přijme jen proti odpovědi `200` s vlastním údajem o nule** (`count == 0`), ne proti prázdnému poli. Pro jistotu zopakuj dotaz – ale ber to jako doplněk, ne jako hlavní obranu: trvalá chyba (zneplatněný token, špatné ID tasku, odebraná práva) vrátí dvakrát totéž a shoda dvou chyb není doklad.

   **Nedá-li se dočtení doložit, nemaž nic.** Zakládat se smí, mazat ne – chybějící protějšek může být jen nenačtená stránka.

### Párovací klíč

Klíč je **cílové místo, datum, čas začátku a délka v minutách**.

- **Délka i čas se zaokrouhlují na celé minuty aritmeticky**, na obou stranách stejně. Clockify měří na vteřiny, vzdálený systém je neumí – bez společného pravidla by se klíč rozcházel pořád dokola a záznamy by se mazaly a zakládaly při každém běhu.
- **U přelité dvojice se klíč krátí na obou stranách** na **datum práce a délku**, bez času začátku a bez cílového místa dne. Datum se bere z prefixu kopie a ze skutečného data zdroje. Krátit jen jednu stranu nestačí: zdroj prefix nemá, takže by se plný klíč se zkráceným nikdy nepotkal a přelití by se opakovalo při každém běhu.
- **Opakuje-li se klíč**, obě strany se uvnitř skupiny seřadí podle času začátku a **páruje se po pořadí**. Nejdřív se dorovnají počty, teprve pak se porovnávají popisy a příznaky.

### Co se s čím dělá

| Stav | Akce |
|---|---|
| klíč jen v Clockify | **založ** ve vzdáleném systému |
| klíč na obou stranách, liší se popis | **uprav popis** |
| klíč na obou stranách, liší se příznak fakturovatelnosti | **oprav příznak** – `PATCH`em, klíč se tím nemění |
| klíč na obou stranách, popis i příznak sedí | nedělej nic |
| klíč jen ve vzdáleném systému, **uvnitř okna zápisu** | **smaž** |
| klíč jen ve vzdáleném systému, **mimo okno zápisu** | **ohlas, nesahej** |

**U přelitého záznamu se porovnává a zapisuje `prefix + popis z Clockify`, nikdy holý popis.** Popisy se totiž liší vždycky – kopie prefix má, zdroj ne –, takže naivní porovnání spustí úpravu při každém běhu a zápisem holého popisu by prefix zmizel. S ním by zmizel zkrácený klíč i ochrana před smazáním a záznam by se při dalším běhu smazal jako přebytek. **Prefix je při úpravě nedotknutelný**, a **chybí-li prefix u záznamu ležícího na prvním dni měsíce, je to nález, ne data.**

**Změna času nebo délky není úprava, ale smazání a nový záznam** – klíč se rozpadl. **Zakládej dřív, než mažeš:** duplikát po přerušeném běhu srovná příští běh, kdežto smazaný záznam už nemá odkud vzít, a padne-li mezitím uzávěrka, propadne.

**Smazat přelitý záznam smíš jedině tehdy, když se jeho zdroj v Clockify našel a liší se mu délka** – pak jde o pár smazání a založení. **Nenašel-li se zdroj vůbec, nemaž.** Jeho práce pochází z uzavřeného měsíce, který se nemusí číst celý, takže chybějící protějšek neznamená, že v Clockify není; **ohlas to jednou větou** a nech rozhodnout.

### Než zapíšeš

**Porovnej počty se zdrojem.** Má-li se založit víc záznamů nebo víc hodin, než kolik jich za okno vyšlo z Clockify, **zastav se a zeptej** – takový rozdíl nevzniká prací, ale chybou ve čtení.

**Znovu načti vzdálený systém těsně před zápisem** a dávku zahoď, liší-li se od snímku, ze kterého ses rozhodoval. Mezitím mohlo běžet druhé sezení.

**Souběžný běh nad týmž klientem se nepouští.** Na začátku běhu založ značku běhu (klient, PID, čas) v `.claude/run/`, na konci ji zruš; najdeš-li čerstvou cizí značku, **skonči a řekni to**. Dvě sezení si navzájem nevidí rozdělanou práci a obě čtou stav před ní – výsledkem jsou duplikáty, nebo hůř dávka mazání odklepnutá jedním stiskem.

## Zápis do deníku

**Přelitý a propadlý čas se zapisuje do souboru klienta**, jeden řádek na běh, do jeho *Deníku přelitého a propadlého času*. Prázdný běh se nezapisuje.

Je to jediné, co režim ukládá mimo vzdálený systém, a má to jediný důvod: **obojí je jinak neviditelné.** Přelitý čas se na faktuře objeví v jiném měsíci, než ve kterém vznikl, a propadlý se neobjeví nikde – po roce to nevysvětlí ani Honza, ani doklad.

Zapisuje se **datum běhu vyrobené příkazem `date +%F`**, kolik hodin se přelilo a odkud, kolik propadlo a za které dny, a **částka, o kterou propadnutím přišel**. Bez částky je to poznámka; s částkou je to důvod příště nečekat.

## Když běh selže uprostřed

**Nedělej nic zvláštního – pusť ho znovu.** Zrcadlení nemá stav, takže druhý běh vidí, co první stihl zapsat, a dorovná zbytek; opakované spuštění nad týmiž daty nic nezdvojí.

**Zakládá se dřív, než se maže**, právě kvůli tomu (*Zrcadlení*, *Co se s čím dělá*). Přerušení mezi obojím tak zanechá duplikát, ne díru – a duplikát se dá srovnat, kdežto smazaný čas po uzávěrce propadne. **Přerušený běh proto zopakuj ještě před uzávěrkou klienta**, ne „někdy“.

**Výjimka je částečně přelitá dávka.** Přelité záznamy se skládají od půlnoci za sebou, takže po přerušení uprostřed navazuje druhý běh na jiný čas, než by vyšel napoprvé. Na párování to nemá vliv – to jde přes datum v prefixu a délku –, ale **pořadí v cílovém místě už nemusí odpovídat pořadí práce**. Je to kosmetika, ne chyba k opravě; přerovnávat to znamená mazat a zakládat znovu.

## Hranice

- **Do Clockify se nezapisuje nikdy.** Zdroj pravdy se neupravuje podle kopie, ani „ať to sedí“.
- **Nemaže se nic, co nepatří Honzovi**, a nic mimo cílová místa ze souboru klienta. Než se smaže cokoliv, musí sedět obojí.
- **U klienta, který se fakturuje ze svého systému, se potvrzuje celá dávka pokaždé**, ne jen při prvním běhu. Co se tam založí, to se vyfakturuje – zápis je tedy zásah do podkladu faktury, ne jen do cizí evidence.
- **Mazání se ukazuje předem.** Založení a úprava proběhnou samy, ale **smazání je zásah do systému klienta** – vypíše se, co a proč, a čeká se na potvrzení. U prvního ostrého běhu na klientovi se potvrzuje celá dávka, ne jen mazání.
- **Přenáší čas, ne peníze.** Do vzdáleného systému jde délka, popis a příznak – **nikdy sazba ani částka**. Kolik ta práce stojí, patří na fakturu; klient má u sebe vidět objem, ne ceník.
- **Nefakturuje ani nepočítá.** Vrací, co udělal; hodiny sečte fakturace.
- **Do souboru klienta zapisuje jedinou věc** – deník přelitého a propadlého času. Dohodu, cílová místa ani uzávěrku si sám nepřepisuje; rozejde-li se s nimi skutečnost, je to nález k rozhodnutí.
- **Cizí čas v cílovém místě se nechává být.** Cílový task bývá sdílený s lidmi u klienta, takže cizí záznamy jsou běžný stav, ne nález; rozhoduje jedině `userId`. **Ohlas ho jen jednou, jako informaci** – a jako podezření na špatné ID cílového místa ho ber teprve tehdy, když tam **není ani jeden** Honzův záznam a přitom tam nějaký být má.
