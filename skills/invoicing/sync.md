# Synchronizace do timetrackingu klienta

Referenční soubor k režimu `sync` skillu `/invoicing`. Drží **mechaniku zrcadlení a pravidla oken**; postup, kdy se co dělá, je v `SKILL.md`, *Režim `sync`*. Přístupy, tokeny a konkrétní volání do systémů drží `~/Dev/context/business/invoicing.md`, *Vzdálený timetracking klienta* – **sem se nikdy neopisují**, tenhle soubor je veřejný.

## Obsah

- *K čemu to je* – proč se čas vede dvakrát
- *Jednosměrnost* – co je zdroj pravdy a co kopie
- *Otevřené okno* – kdy se do vzdáleného systému smí sahat
- *Uzávěrka dřív než faktura* – klient s vlastní lhůtou
- *Zpětný čas po uzávěrce* – co se přesouvá a co propadá
- *Co se přenáší* – které záznamy jdou ven a s jakým příznakem
- *Zrcadlení* – jak se pozná, co přidat, upravit a smazat
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

**Hranice se čte odtud, odkud ji čte fakturace** – `~/Dev/context/business/invoicing.md`, *Odkud se ví, co už je vyfakturované*. Vlastní hranici si režim neurčuje.

## Uzávěrka dřív než faktura

Klient může mít lhůtu **kratší**, než je vystavení faktury: „měsíc se uzavírá do třetího pracovního dne měsíce následujícího“. Pak platí ta lhůta, ne datum dokladu.

**Uzávěrka klienta je v jeho souboru v `invoicing/`.** Není-li tam žádná, okno zavírá až faktura.

**Přelitý čas není rozdíl mezi stranami.** Porovnává-li se Clockify se vzdáleným systémem – ať už v zrcadlení, nebo při kontrole před fakturací –, **počítá se přelitý záznam k datu ze svého prefixu**, ne ke dni, na kterém leží. Bez toho by u každého klienta po přelití vycházel rozdíl, který rozdíl není, a fakturace by se zastavovala pokaždé.

**Má-li klient uzávěrku, mění se i to, z čeho se počítá doklad:** fakturuje se **to, co je ve vzdáleném systému**, ne co je v Clockify. Je to výjimka z obecného pravidla o zdroji pravdy a **musí být napsaná v dohodě klienta**, jinak neplatí.

Praktický důsledek, který se musí říct nahlas: **selže-li sync, vyjde faktura nižší.** Proto fakturace u takového klienta začíná kontrolou synchronizace – viz `SKILL.md`, *Fáze 1*.

## Zpětný čas po uzávěrce

Čas doplněný do Clockify až po uzávěrce se **nezahazuje automaticky**. Rozhoduje, ke kterému měsíci patří:

| Čas patří do | Co s ním |
|---|---|
| **právě uzavřeného měsíce** | přesune se do **aktuálního měsíce, na jeho první den**, s prefixem v popisu; vyfakturuje se s ním |
| **měsíce ještě staršího** | **propadá** – do vzdáleného systému nejde a nefakturuje se |
| období otevřeného okna | zapíše se normálně na svoje datum |

**Prefix je povinný a má pevný tvar:**

```
Zpětně vytrackovaný čas za 12. července 2026: <původní popis z Clockify>
```

Datum v prefixu je **skutečné datum práce** z Clockify, česky vypsané. Nese dvě funkce naráz: klient vidí, že se nesnažíš propašovat starý čas do nového měsíce, a **režim podle něj ten záznam příště pozná** – bez prefixu by ho zrcadlení bralo jako přebytek a smazalo by ho.

**Přelité záznamy se v cílovém místě skládají od půlnoci za sebou.** První začíná v 00:00, druhý hned po jeho konci, třetí po něm – v pořadí, v jakém práce **původně proběhla**, a **v každém cílovém místě zvlášť**. Vzdálený systém obvykle nechce jen počet hodin, ale interval od–do; kdyby přelité záznamy začínaly všechny ve stejnou chvíli, klient uvidí překrývající se čas a přestane výkazu věřit.

**Propadlý čas se nemaže z Clockify** a ve výpisu se vypíše jmenovitě i se součtem. Je to nefakturovaná práce, ne omyl, a Honza má právo vidět, kolik ho ta prodleva stála.

## Co se přenáší

**Rozsah určuje soubor klienta, ne režim.** Výchozí je, že jde ven **všechen čas na projektech toho klienta** – tedy i nefakturovatelný a jinak sazbený –, protože klient má u sebe vidět celý objem odvedené práce. Chce-li klient jen část, stojí to v jeho souboru.

**Příznak fakturovatelnosti se odvozuje podle pravidla klienta, ne podle prefixu v popisu.** U klienta, který sám přeúčtovává práci dál, závisí na tom, jestli je projekt klientský, nebo interní – v interním nemůže vzniknout fakturovatelný čas vůbec. **Pravidlo patří do souboru klienta a bez něj se příznak nedomýšlí**; „co nemá prefix, je fakturovatelné“ je nejběžnější případ, ne zákon.

**Příznak fakturovatelnosti ve vzdáleném systému je informace pro klienta, ne rozhodnutí o faktuře.** Záznam může být ve vzdáleném systému non-billable a přesto se fakturovat – typicky práce s jinou sazbou. **Podklad faktury se proto skládá podle prefixů v popisu**, stejně jako by se skládal z Clockify; brát ven jen billable záznamy znamená tiše zahodit část výdělku.

## Zrcadlení

Režim si **nedrží žádný stav** – žádnou mapovací tabulku, žádné ID v poznámce. Pokaždé si přečte obě strany a srovná je. Stav, který se rozejde, je horší než jeho absence, a u kopie se rozejde vždycky.

1. **Načti Clockify** za otevřené okno, jen projekty toho klienta.
2. **Načti vzdálený systém** za totéž okno **rozšířené o den na obou stranách**, **jen z cílových míst** vyjmenovaných v souboru klienta, a **z výsledku ponech jen záznamy pod Honzovým účtem**. Ověř to z dat, ne z filtru dotazu – filtr, který se tiše ignoruje, vrací cizí práci a ta by se pak mazala.

   **Den navíc na každé straně je proti časovým pásmům.** Vzdálený systém běžně filtruje podle UTC a ukládá lokální čas, takže záznam z půlnoci padne do předchozího dne a přesně ohraničený dotaz ho minie. **Nenajde-li zrcadlení existující záznam, založí ho podruhé** – a duplikát v cizím systému je horší než chybějící kopie, protože se fakturuje.
3. **Vrátilo-li čtení vzdáleného systému nulu, zopakuj dotaz.** Shodnou-li se obě odpovědi na nule, je prázdno skutečné a pokračuje se; **liší-li se, zastav se a řekni to** – jedna z odpovědí je nespolehlivá a neví se která.

   **Proč zrovna tady:** zrcadlení čte prázdnou odpověď jako „v cizím systému nic není“ a **založí všechno znovu**. U klienta, který se fakturuje ze svého systému, se takový duplikát rovnou vyfakturuje. Jedno volání navíc za běh je proti tomu levné. Doloženo 10. 9. 2026: při prvním ostrém běhu vrátil dotaz na rozsah, ve kterém záznam prokazatelně ležel, prázdné tělo – a při opakování s odstupem prošel, aniž by šlo o vyčerpaný limit.

4. **Spočítej klíč** u každého záznamu na obou stranách: **datum a čas začátku, délka v minutách**.

   **Záznam s prefixem má klíč jiný – jen datum z prefixu a délku, bez času začátku.** Přelití mu čas začátku schválně přepisuje (skládá se od půlnoci), takže by se s protějškem v Clockify nikdy neshodl a zrcadlení by ho vyhodnotilo jako přebytek ke smazání. Datum se bere **z prefixu**, ne z toho, na kterém záznam leží.
5. **Srovnej jako množiny** – klíč se může opakovat, takže se porovnávají počty, ne existence.

| Stav | Akce |
|---|---|
| klíč jen v Clockify | **založ** ve vzdáleném systému |
| klíč na obou stranách, liší se popis | **uprav popis** |
| klíč na obou stranách, popis sedí | nedělej nic |
| klíč jen ve vzdáleném systému | **smaž** |

**Změna času nebo délky není úprava, ale smazání a nový záznam** – klíč se rozpadl. Vypadá to hrubě, ale je to jediné chování, které nepotřebuje pamatovat, co bylo dřív.

**Záznam s prefixem se nemaže nikdy**, ani když se mu protějšek nenajde. Leží sice v otevřeném okně, ale jeho práce pochází z **uzavřeného** měsíce – a ten se z Clockify nemusí vůbec číst, takže chybějící protějšek neznamená, že v Clockify není. Popis se u něj opravit smí, smazat ne.

**Mimo otevřené okno se nemaže ani neupravuje nic**, i kdyby se strany rozcházely. Rozdíl v uzavřeném období se **ohlásí** a nechá být.

## Zápis do deníku

**Přelitý a propadlý čas se zapisuje do souboru klienta**, jeden řádek na běh, do jeho *Deníku přelitého a propadlého času*. Prázdný běh se nezapisuje.

Je to jediné, co režim ukládá mimo vzdálený systém, a má to jediný důvod: **obojí je jinak neviditelné.** Přelitý čas se na faktuře objeví v jiném měsíci, než ve kterém vznikl, a propadlý se neobjeví nikde – po roce to nevysvětlí ani Honza, ani doklad.

Zapisuje se **datum běhu vyrobené příkazem `date +%F`**, kolik hodin se přelilo a odkud, kolik propadlo a za které dny, a **částka, o kterou propadnutím přišel**. Bez částky je to poznámka; s částkou je to důvod příště nečekat.

## Hranice

- **Do Clockify se nezapisuje nikdy.** Zdroj pravdy se neupravuje podle kopie, ani „ať to sedí“.
- **Nemaže se nic, co nepatří Honzovi**, a nic mimo cílová místa ze souboru klienta. Než se smaže cokoliv, musí sedět obojí.
- **Mazání se ukazuje předem.** Založení a úprava proběhnou samy, ale **smazání je zásah do systému klienta** – vypíše se, co a proč, a čeká se na potvrzení. U prvního ostrého běhu na klientovi se potvrzuje celá dávka, ne jen mazání.
- **Přenáší čas, ne peníze.** Do vzdáleného systému jde délka, popis a příznak – **nikdy sazba ani částka**. Kolik ta práce stojí, patří na fakturu; klient má u sebe vidět objem, ne ceník.
- **Nefakturuje ani nepočítá.** Vrací, co udělal; hodiny sečte fakturace.
- **Do souboru klienta zapisuje jedinou věc** – deník přelitého a propadlého času. Dohodu, cílová místa ani uzávěrku si sám nepřepisuje; rozejde-li se s nimi skutečnost, je to nález k rozhodnutí.
- **Cizí čas v cílovém místě se nechává být.** Cílový task bývá sdílený s lidmi u klienta, takže cizí záznamy jsou běžný stav, ne nález; rozhoduje jedině `userId`. **Ohlas ho jen jednou, jako informaci** – a jako podezření na špatné ID cílového místa ho ber teprve tehdy, když tam **není ani jeden** Honzův záznam a přitom tam nějaký být má.
