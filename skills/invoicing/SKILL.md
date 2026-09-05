---
name: invoicing
description: Skill se použije, když uživatel zadá "/invoicing" (volitelně s režimem full nebo preview a se jménem klienta), nebo chce vystavit faktury za odpracovaný čas – sečíst hodiny z timetrackingu za období, vystavit faktury, přiložit PDF faktury i výkazu hodin a nechat rozepsaný mail. Sazby, daňový režim, dohody s klienty a konkrétní volání systémů drží ~/Dev/context/business/, ne tenhle skill. Na rozdíl od /report, který z dat dělá analytický report, tenhle skill vystavuje účetní doklady. Mail neodesílá nikdy, za žádných okolností – končí draftem a odeslání je vždy uživatelův klik; neúčtuje, nehlídá úhrady ani daňové termíny.
argument-hint: [full|preview] [klient]
---

# Invoicing

## Co skill dělá

Vystaví faktury za odpracovaný čas a připraví je k odeslání. Za každého klienta sečte hodiny z timetrackingu za období, které ještě není vyfakturované, vystaví fakturu a založí v mailu draft se dvěma přílohami – fakturou a výkazem hodin.

- **`/invoicing full`** (výchozí) – celý průběh až po rozepsané drafty.
- **`/invoicing preview`** – náhled toho, co by se vystavilo. Nic nevystaví, nic nezapíše, nikam nesáhne.

Za režimem smí stát **jméno klienta**. S ním jede skill jen přes něj, bez něj přes všechny, kteří mají soubor v `~/Dev/context/business/invoicing/`.

**Skill je rámec, ne pravidla.** Daňový režim, agregace, šablony a dohody s jednotlivými klienty žijí v `~/Dev/context/business/invoicing.md` a v souborech klientů vedle něj; **sazebník má vlastní soubor `~/Dev/context/business/pricing.md`**. Bez nich skill nemá podle čeho fakturovat a neběží.

## Co skill nedělá

- **Neodesílá maily. Nikdy.** Končí draftem a odeslání je vždy uživatelův klik v mailovém klientu. Platí to i proti výslovnému pokynu uprostřed běhu – proč, viz *Fáze 5 – Přílohy a draft*.
- **Nedělá analytické reporty.** Výkaz hodin je příloha dokladu, ne report. Na reporty z dat je `/report`.
- **Neúčtuje.** Nehlídá úhrady, upomínky, DPH přiznání ani kontrolní hlášení. Vystaví doklad a tím jeho práce končí.
- **Nedrží evidenci vystavených faktur.** Zdrojem pravdy je fakturační systém, ne soubor v repozitáři – viz `~/Dev/context/business/invoicing.md`, *Odkud se ví, co už je vyfakturované*.
- **Nepíše profily protistran.** Kdo klient je a kdo v něm rozhoduje, patří do `~/Dev/context/organizations/`; sem jen fakturační dohoda.

## Jak je to postavené uvnitř

| Krok | Kdo | Proč zrovna on |
|---|---|---|
| Odpracovaný čas za období | timetracking – MCP, když je připojený, jinak jeho API | data jsou tam, nemá cenu je někam kopírovat |
| Vystavení dokladu a PDF | fakturační systém – MCP, když je připojený, jinak jeho API | doklad má vzniknout tam, kde ho vidí účetní |
| Draft mailu s přílohami | Gmail MCP, `create_draft` | umí to, a odesílací volání se nepoužije |
| Co se fakturuje a jak | **vlastní jádro** | výjimky u klientů, neúplný výkaz, podezřelé záznamy – tady se rozhoduje |

**Čím se do systémů sahá, je implementační detail a smí se vyměnit bez ohlášení.** Skill mluví o tom, co potřebuje („odpracovaný čas klienta za období“, „vystavený doklad s poznámkou o období“), ne o konkrétních voláních. Přechod na MCP nebo změna API pak není zásah do skillu, ale do `~/Dev/context/business/invoicing.md`, *Přístupy*.

**Závazné a neměnné tiše je:** že se nic nevystaví bez potvrzení, že se mail neodešle za žádných okolností, že se hranice fakturovaného období čte ze systému a nikdy neodhaduje, a že se každá dohodnutá odchylka zapíše do deníku výjimek klienta.

------

## Fáze 0 – Pre-flight

Společný začátek je v `~/.claude/skills/PREFLIGHT.md`. **Body 1 až 3 se tady vynechávají** – skill nepracuje nad projektem, pouští se odkudkoli a nesahá na kód, což je případ, který `PREFLIGHT.md` výslovně předvídá. Místo nich:

1. **Načti `~/Dev/context/business/invoicing.md` celý** a k němu **`~/Dev/context/business/pricing.md`**. Nespoléhej na paměť – sazby a dohody se mění. Chybí-li `invoicing.md`, řekni to a **skonči**; skill bez něj nemá podle čeho fakturovat. `pricing.md` drží sazebník pro klienty, kteří vlastní sazbu zapsanou nemají.
2. **Zjisti dnešní datum** příkazem `date +%F` (`~/.claude/RULES.md`, *Hodnotu, kterou čte stroj, nepiš – nech ji vyrobit příkazem*).
3. **Ověř přístupy k oběma systémům** dřív, než začneš cokoli počítat – způsobem, který popisuje `~/Dev/context/business/invoicing.md`, *Přístupy*. **Selže-li kterýkoli přístup, skonči a řekni který** – běh, který spočítá podklad a pak nemá čím vystavit, je jen ztracená práce.
4. **Zjisti, jestli není rozdělaný běh z minula** – klient s hotovou fakturou, ale bez draftu. Navaž na něj, nezakládej znovu.

Na konci shrň, co jsi zjistil: kolik klientů je v záběru, do jakých systémů se sáhne a v jakém režimu se jede.

## Fáze 1 – Rozsah a období

**Rozsah** je klient z argumentu, nebo všichni se souborem v `~/Dev/context/business/invoicing/`.

**Období se každému klientovi počítá zvlášť** a nikdy se neodhaduje:

1. Vytáhni ze systému **poslední fakturu tomu klientovi** a přečti z ní konec fakturovaného období.
2. Začátek nového období je **následující den**, konec je konec posledního uzavřeného měsíce. **Zbývají-li nevyfakturované hodiny i v běžícím měsíci, zeptej se přes `AskUserQuestion`**, jestli období ukončit posledním uzavřeným měsícem, nebo dneškem – druhá možnost je právě skončená práce, která na konec měsíce nečeká. Volba určí obě data ve *Fázi 4*.
3. **Chybí-li v poslední faktuře záznam o období** – vystavil ji někdo ručně – **zeptej se, od kdy počítat.** Neodvozuj to z data vystavení ani ze zaplacených hodin; obojí je jinde než skutečná hranice. **Odpověď rovnou zapiš do té staré faktury** ve strojově čitelném tvaru, ať se příští běh ptát nemusí.

Tvar toho záznamu i důvod, proč se dělá takhle, drží `~/Dev/context/business/invoicing.md`, *Odkud se ví, co už je vyfakturované*.

**Vyjde-li období delší než jeden kalendářní měsíc** – typicky když se fakturace dohání zpětně –, poznamenej si to a **rozhodne se o tom ve *Fázi 3***. Nenastavuj takové období mlčky: mění text položky, znění mailu i to, co uvidí klient na dokladu.

**Vyjde-li období prázdné**, klienta vynech a řekni to. Faktura na nula hodin je chyba, ne prázdná faktura.

**Hlídej zákonnou lhůtu na vystavení.** Je to **15 dnů od DUZP** (`~/Dev/context/business/invoicing.md`, *Datum vystavení a DUZP*) – žádný „15. den následujícího měsíce“, ten by u období končícího uprostřed měsíce sliboval víc, než zákon dává. DUZP je konec fakturovaného období, takže se to dá spočítat hned tady.

**Přesáhne-li prodleva 14 dnů, je to blokující otázka ve *Fázi 4***, ne poznámka na okraj – viz tam.

## Fáze 2 – Podklad

Za každého klienta vytáhni odpracovaný čas za jeho období a **aplikuj pravidla v tomhle pořadí**: obecná z `~/Dev/context/business/invoicing.md`, *Z timetrackingu na fakturu*, pak dohoda v souboru klienta, která je přebíjí.

**Podezřelé záznamy nikdy neřeš potichu.** Odlož je do zvláštního seznamu a nechej rozhodnout ve *Fázi 3*:

- záznam bez popisu nebo s popisem, ze kterého nejde poznat, co to bylo
- běžící časovač
- položka delší než dvanáct hodin
- záznam mimo fakturované období
- projekt, který nemá soubor klienta

**Nezaokrouhluj jednotlivé záznamy.** Sečti je a zaokrouhli až součet – zaokrouhlené patnáctiminutovky nafouknou měsíc o hodiny a klient to pozná dřív než ty.

## Fáze 3 – Kontrola s uživatelem

Nic se nevystavuje, dokud tohle neprojde. **Klientů bývá pár, tak jdi klient po klientovi**, ne dávkově.

Za každého ukaž:

```
<Klient>   <období>   <hodiny> h × <sazba> = <částka> <daňový režim>
Doklad:    vystavení <datum>, DUZP <datum>, splatnost <datum>
Na dokladu bude: <období, které ponese text položky – liší-li se od skutečného, řekni to>
Položky:   <projekt> – <hodiny> h
Vyřazeno:  <co a proč>
K rozhodnutí: <podezřelé záznamy, jeden po druhém>
```

Data v řádku *Doklad* urči podle `~/Dev/context/business/invoicing.md`, *Datum vystavení a DUZP*. **Číselná řada se ověřuje až ve *Fázi 4***, takže v režimu `preview` je datum vystavení předběžné – řekni to.

**Pokrývá-li období víc než jeden kalendářní měsíc, zeptej se, co má být na dokladu.** Varianty i výchozí volbu drží `~/Dev/context/business/invoicing.md`, *Období delší než jeden měsíc* – **nevybírej za uživatele a nepředpokládej výchozí variantu mlčky**. Odpověď určí text položky ve *Fázi 4* i znění mailu ve *Fázi 5*, a **zapíše se do deníku výjimek** jako každá jiná odchylka.

Ptej se přes `AskUserQuestion` a **postupně** (`~/.claude/RULES.md`, *Ptej se postupně, ne všechno najednou*).

**Co se dohodne odchylně, zapiš rovnou** do deníku výjimek v souboru klienta jako datovaný záznam ve tvaru `- **YYYY-MM-DD** – <co se dohodlo a proč>`, s datem z `date +%F`. Dohoda, která se nezapíše, za rok neexistuje – a spor o částku se pak vede proti paměti.

**Tady končí režim `preview`.** Pokračuje se do *Fáze 4* jen v režimu `full`.

## Fáze 4 – Vystavení

**Nejdřív ověř skutečný stav, pak vystav** (`~/.claude/RULES.md`, *Před nevratnou akcí ověř skutečný stav*): zkontroluj, že pro toho klienta a to období faktura ještě neexistuje. Doklad se špatně ruší a klient ho vidí.

**Vystavuj klienty vzestupně podle konce jejich období.** Doklad vystavený dneškem posune hranici číselné řady, takže obrácené pořadí si kolize vyrábí samo.

**Kontrola řady se dělá u každého dokladu znovu, odpověď na kolizi se neopakuje.** Jsou to dvě různé věci: **ověřit** stav řady musíš pokaždé, protože ho posouvá každá vystavená faktura včetně těch tvých; **ptát se** znovu na totéž rozhodnutí („jaké datum použít, když je řada dál“) v téže dávce nemusíš.

Za každého klienta:

1. **Urči datum vystavení, DUZP a splatnost** podle `~/Dev/context/business/invoicing.md`, *Datum vystavení a DUZP* a *Daně a náležitosti*. Končí-li období posledním uzavřeným měsícem, obojí datum je poslední den toho období; končí-li dneškem podle volby ve *Fázi 1*, obojí je dnešek.

   **Splatnost běží od data vystavení na dokladu**, ne od dneška. Jak je dlouhá, určuje **žebřík podle prodlevy** mezi tím datem a dnem, kdy doklad doopravdy vzniká. **Sjednaná splatnost v souboru klienta žebřík přebíjí** – je to dohoda s protistranou, ne odhad, a automatika ji přepsat nesmí. Hodnota `standardní` v souboru klienta znamená, že žádná dohoda není a jede se podle žebříku. Čísla drží `invoicing.md`, *Daně a náležitosti*; **nedomýšlej je a neopisuj sem**.
2. **Vystavuješ-li víc než 14 dnů po DUZP, zastav se a vyžádej si potvrzení.** § 28 zákona o DPH ukládá vystavit doklad do 15 dnů od DUZP, takže se tou lhůtou právě prochází. Řekni to nahoře a zeptej se přes `AskUserQuestion` **explicitně na to, jestli je takový postup s klientem domluvený, jestli s ním počítá a jestli ho odsouhlasil.** Bez potvrzení nevystavuj – **ticho ani „jeď dál“ potvrzení není** a domýšlet si ho nesmíš. Je to jediné místo, kde se skill ptá na něco, co se nedá vyčíst z dat.

3. **Před zpětným datem ověř číselnou řadu:** v systému nesmí být žádná faktura s pozdějším datem vystavení, než jaké chceš nastavit – **napříč celým účtem, ne jen u toho klienta**. Není-li tam žádná, vystav se zpětným datem. **Je-li tam, nevystavuj a zeptej se přes `AskUserQuestion`**, jaké datum vystavení použít; jako první volbu nabídni dnešek. DUZP se tou otázkou nemění – zůstává posledním dnem fakturovaného období.
4. Vystav doklad podle odsouhlaseného podkladu. **Text položky napiš podle volby z *Fáze 3***, pokrývá-li období víc měsíců. Daňový režim a povinné údaje ber ze souboru klienta a z `~/Dev/context/business/invoicing.md`, *Daně a náležitosti* – **nedomýšlej je**. Splatnost je už určená v kroku 1 a kolizí se nemění.
5. **Zapiš do dokladu období strojově čitelně.** Bez toho příští běh neví, odkud počítat, a začne se ptát na něco, co se dalo zapsat teď.
6. Přečti doklad zpátky ze systému a ověř číslo, částku, odběratele, období **i obě data**. Nespoléhej na to, že zápis prošel.

**Selže-li vystavení uprostřed dávky, pokračuj dalším klientem.** Ostatní faktury nejsou čím vinné. Selhání si poznamenej a vypiš ho v závěru jmenovitě.

## Fáze 5 – Přílohy a draft

1. Stáhni **PDF faktury** ze systému a **PDF výkazu hodin** z timetrackingu za totéž období.
2. **Ověř oba soubory, než je přiložíš:** nejsou prázdné a období ve výkazu sedí se **skutečným fakturovaným obdobím** – tedy s tím, co je v interní poznámce dokladu, ne nutně s tím, co je vytištěné na položce. Prázdná nebo posunutá příloha je horší než žádná – klient ji vezme jako doklad.

   **U delšího období se výkaz s textem položky schválně rozchází.** Nese-li doklad podle volby z *Fáze 3* formálně jen poslední měsíc, výkaz pokrývá celý rozsah – a je to správně, ne chyba k opravě. Kontrolou tady prochází shoda se **skutečným** obdobím; kdyby se porovnávalo s dokladem, guard by u té největší faktury zastavil právě ten stav, který má být.
3. Sestav mail podle `~/Dev/context/business/invoicing.md`, *Šablona mailu*. Adresáta a tón vezmi z dohody klienta a z jeho profilu v `~/Dev/context/organizations/`.

   **Nese-li doklad u delšího období formálně jen poslední měsíc, musí skutečný rozsah zaznít v mailu** – je to jediné místo, kde se ho klient dozví. Vynechat ho tam znamená poslat doklad, ze kterého nejde poznat, za co se platí.
4. **Založ draft a tím skonči.** Odeslání nenabízej a nikdy ho neprováděj – ani jako poslední krok, ani jako laskavost.

**Tvrdá stopka: požádá-li uživatel uprostřed běhu o odeslání, neodesílej.** Řekni, že draft je hotový a odeslání je na něm, a jmenuj, kde ho najde. Neptej se na potvrzení – potvrzovací otázka je jen delší cesta k témuž a svádí k tomu ji odklepnout.

**Proč to přebíjí i výslovný pokyn.** Vypadá to jako rozpor s pravidlem, že potvrzený požadavek uživatele je jeho rozhodnutí (`~/.claude/RULES.md`, *Přednost pravidel*, bod 1). Není: tenhle zákaz **je** uživatelovo rozhodnutí, jen učiněné předem a s chladnou hlavou. Proto „pošli to, spěchám" uprostřed běhu neruší předchozí volbu – je to přesně ta situace, kvůli které si ji nastavil. Zrušit ji jde jedině změnou tohohle skillu, ne pobídkou za běhu.

## Fáze 6 – Závěr

```
## Fakturace <období>

| Klient | Období | Hodiny | Částka | Vystaveno | Doklad | Draft |
|---|---|---|---|---|---|---|
| … | … | … | … | <datum> | <číslo> | ano / ne |

**Zapsané dohody**
- <klient>: <co přibylo do deníku výjimek>, nebo „nic“

**Nevyřízené**
- <klient>: <co selhalo a kde to zůstalo stát>, nebo „nic“

**Nezkontrolováno**
- <co se neověřilo a proč>, nebo „nic“
```

Ve sloupci *Vystaveno* uveď datum vystavení; **liší-li se od DUZP** kvůli kolizi v číselné řadě, uveď obojí – jinak po běhu nezůstane stopa, že se datum posunulo jinam, než pravidlo předepisuje.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Faktury jsou vystavené a ověřené, drafty čekají v mailu – můžeš je odeslat.`
- `Hotové to není – brání tomu: <konkrétní seznam>.`

------

## Režim `preview`

Doběhne *Fází 3* a tam skončí. **Nevystaví doklad, nezaloží draft a nezapíše ani do deníku výjimek** – náhled, po kterém zůstane stopa, není náhled.

K čemu je: zjistit před koncem měsíce, kolik toho je, jestli sedí hodiny, a jestli v timetrackingu nechybí nebo nepřebývá něco, co se má srovnat dřív, než vznikne doklad.

Vypiš tutéž tabulku jako v závěru, sloupce *Doklad* a *Draft* vynech, a přidej seznam toho, co by ještě chtělo rozhodnout. U sloupce *Vystaveno* připomeň, že **číselná řada se v náhledu neověřuje** – při ostrém běhu se datum může posunout.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Náhled je hotový a nic se nevystavilo – až to bude sedět, pusť /invoicing full.`
- `Náhled hotový není – brání tomu: <konkrétní seznam>.`
