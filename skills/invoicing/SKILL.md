---
name: invoicing
description: Skill se použije, když uživatel zadá "/invoicing" (volitelně s režimem full nebo preview a se jménem klienta), nebo chce vystavit faktury za odpracovaný čas – sečíst hodiny z timetrackingu za období, vystavit faktury, přiložit PDF faktury i výkazu hodin a nechat rozepsaný mail. Sazby, daňový režim, dohody s klienty a konkrétní volání systémů drží ~/Dev/context/business/, ne tenhle skill. Na rozdíl od /report, který z dat dělá analytický report, tenhle skill vystavuje účetní doklady. Maily nikdy neodesílá, jen zakládá drafty; neúčtuje, nehlídá úhrady ani daňové termíny.
argument-hint: [full|preview] [klient]
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion]
---

# Invoicing

## Co skill dělá

Vystaví faktury za odpracovaný čas a připraví je k odeslání. Za každého klienta sečte hodiny z timetrackingu za období, které ještě není vyfakturované, vystaví fakturu a založí v mailu draft se dvěma přílohami – fakturou a výkazem hodin.

- **`/invoicing full`** (výchozí) – celý průběh až po rozepsané drafty.
- **`/invoicing preview`** – náhled toho, co by se vystavilo. Nic nevystaví, nic nezapíše, nikam nesáhne.

Za režimem smí stát **jméno klienta**. S ním jede skill jen přes něj, bez něj přes všechny, kteří mají soubor v `~/Dev/context/business/invoicing/`.

**Skill je rámec, ne pravidla.** Sazby, daňový režim, agregace, šablony a dohody s jednotlivými klienty žijí v `~/Dev/context/business/invoicing.md` a v souborech klientů vedle něj. Bez nich skill nemá podle čeho fakturovat a neběží.

## Co skill nedělá

- **Neodesílá maily.** Končí draftem. Odeslání dokladu klientovi je nevratná venkovní akce a zůstává na člověku – i tehdy, když si ho uprostřed běhu vyžádá.
- **Nedělá analytické reporty.** Výkaz hodin je příloha dokladu, ne report. Na reporty z dat je `/report`.
- **Neúčtuje.** Nehlídá úhrady, upomínky, DPH přiznání ani kontrolní hlášení. Vystaví doklad a tím jeho práce končí.
- **Nedrží evidenci vystavených faktur.** Zdrojem pravdy je fakturační systém, ne soubor v repozitáři – viz `~/Dev/context/business/invoicing.md`, *Odkud se ví, co už je vyfakturované*.
- **Nepíše profily protistran.** Kdo klient je a kdo v něm rozhoduje, patří do `~/Dev/context/organizations/`; sem jen fakturační dohoda.

## Jak je to postavené uvnitř

| Krok | Kdo | Proč zrovna on |
|---|---|---|
| Odpracovaný čas za období | timetracking – MCP, když je připojený, jinak jeho API | data jsou tam, nemá cenu je někam kopírovat |
| Vystavení dokladu a PDF | fakturační systém – MCP, když je připojený, jinak jeho API | doklad má vzniknout tam, kde ho vidí účetní |
| Draft mailu s přílohami | Gmail MCP, `create_draft` | umí to, a odesílání se schválně nevolá |
| Co se fakturuje a jak | **vlastní jádro** | výjimky u klientů, neúplný výkaz, podezřelé záznamy – tady se rozhoduje |

**Čím se do systémů sahá, je implementační detail a smí se vyměnit bez ohlášení.** Skill mluví o tom, co potřebuje („odpracovaný čas klienta za období“, „vystavený doklad s poznámkou o období“), ne o konkrétních voláních. Přechod na MCP nebo změna API pak není zásah do skillu, ale do `~/Dev/context/business/invoicing.md`, *Přístupy*.

**Závazné a neměnné tiše je:** že se nic nevystaví bez potvrzení, že se mail neodešle, že se hranice fakturovaného období čte ze systému a nikdy neodhaduje, a že se každá dohodnutá odchylka zapíše do deníku výjimek klienta.

------

## Fáze 0 – Pre-flight

Společný začátek je v `~/.claude/skills/PREFLIGHT.md`. **Body 1 až 3 se tady neuplatní** – skill nepracuje nad projektem, pouští se odkudkoli a nesahá na kód. Místo nich:

1. **Načti `~/Dev/context/business/invoicing.md` celý.** Nespoléhej na paměť – sazby a dohody se mění. Chybí-li soubor, řekni to a **skonči**; skill bez něj nemá podle čeho fakturovat.
2. **Zjisti dnešní datum** příkazem `date +%F` (`~/.claude/RULES.md`, *Hodnotu, kterou čte stroj, nepiš – nech ji vyrobit příkazem*).
3. **Ověř přístupy k oběma systémům** dřív, než začneš cokoli počítat – způsobem, který popisuje `~/Dev/context/business/invoicing.md`, *Přístupy*. **Selže-li kterýkoli přístup, skonči a řekni který** – běh, který spočítá podklad a pak nemá čím vystavit, je jen ztracená práce.
4. **Zjisti, jestli není rozdělaný běh z minula** – klient s hotovou fakturou, ale bez draftu. Navaž na něj, nezakládej znovu.

Na konci shrň, co jsi zjistil: kolik klientů je v záběru, do jakých systémů se sáhne a v jakém režimu se jede.

## Fáze 1 – Rozsah a období

**Rozsah** je klient z argumentu, nebo všichni se souborem v `~/Dev/context/business/invoicing/`.

**Období se každému klientovi počítá zvlášť** a nikdy se neodhaduje:

1. Vytáhni ze systému **poslední fakturu tomu klientovi** a přečti z ní konec fakturovaného období.
2. Začátek nového období je **následující den**, konec je konec posledního uzavřeného měsíce.
3. **Chybí-li v poslední faktuře záznam o období** – vystavil ji někdo ručně – **zeptej se, od kdy počítat.** Neodvozuj to z data vystavení ani ze zaplacených hodin; obojí je jinde než skutečná hranice.

Tvar toho záznamu i důvod, proč se dělá takhle, drží `~/Dev/context/business/invoicing.md`, *Odkud se ví, co už je vyfakturované*.

**Vyjde-li období prázdné**, klienta vynech a řekni to. Faktura na nula hodin je chyba, ne prázdná faktura.

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
Položky:   <projekt> – <hodiny> h
Vyřazeno:  <co a proč>
K rozhodnutí: <podezřelé záznamy, jeden po druhém>
```

Ptej se přes `AskUserQuestion` a **postupně** (`~/.claude/RULES.md`, *Ptej se postupně, ne všechno najednou*).

**Co se dohodne odchylně, zapiš rovnou** do deníku výjimek v souboru klienta jako datovaný záznam ve tvaru `- **YYYY-MM-DD** – <co se dohodlo a proč>`, s datem z `date +%F`. Dohoda, která se nezapíše, za rok neexistuje – a spor o částku se pak vede proti paměti.

**Tady končí režim `preview`.** Pokračuje se do *Fáze 4* jen v režimu `full`.

## Fáze 4 – Vystavení

**Nejdřív ověř skutečný stav, pak vystav** (`~/.claude/RULES.md`, *Před nevratnou akcí ověř skutečný stav*): zkontroluj, že pro toho klienta a to období faktura ještě neexistuje. Doklad se špatně ruší a klient ho vidí.

Za každého klienta:

1. Vystav doklad podle odsouhlaseného podkladu. Daňový režim, splatnost a povinné údaje ber ze souboru klienta a z `~/Dev/context/business/invoicing.md`, *Daně a náležitosti* – **nedomýšlej je**.
2. **Zapiš do dokladu období strojově čitelně.** Bez toho příští běh neví, odkud počítat, a začne se ptát na něco, co se dalo zapsat teď.
3. Přečti doklad zpátky ze systému a ověř číslo, částku, odběratele a období. Nespoléhej na to, že zápis prošel.

**Selže-li vystavení uprostřed dávky, pokračuj dalším klientem.** Ostatní faktury nejsou čím vinné. Selhání si poznamenej a vypiš ho v závěru jmenovitě.

## Fáze 5 – Přílohy a draft

1. Stáhni **PDF faktury** ze systému a **PDF výkazu hodin** z timetrackingu za totéž období.
2. **Ověř oba soubory, než je přiložíš:** nejsou prázdné a období ve výkazu sedí s obdobím na faktuře. Prázdná nebo posunutá příloha je horší než žádná – klient ji vezme jako doklad.
3. Sestav mail podle `~/Dev/context/business/invoicing.md`, *Šablona mailu*. Adresáta a tón vezmi z dohody klienta a z jeho profilu v `~/Dev/context/organizations/`.
4. **Založ draft. Neodesílej.** Ani na vyžádání uprostřed běhu – draft je hotový výstup a odeslání je jedno kliknutí, kdežto odeslaná faktura se nevrací.

## Fáze 6 – Závěr

```
## Fakturace <období>

| Klient | Období | Hodiny | Částka | Doklad | Draft |
|---|---|---|---|---|---|
| … | … | … | … | <číslo> | ano / ne |

**Zapsané dohody**
- <klient>: <co přibylo do deníku výjimek>, nebo „nic“

**Nevyřízené**
- <klient>: <co selhalo a kde to zůstalo stát>, nebo „nic“

**Nezkontrolováno**
- <co se neověřilo a proč>, nebo „nic“
```

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Faktury jsou vystavené a ověřené, drafty čekají v mailu – můžeš je odeslat.`
- `Hotové to není – brání tomu: <konkrétní seznam>.`

------

## Režim `preview`

Doběhne *Fází 3* a tam skončí. **Nevystaví doklad, nezaloží draft a nezapíše ani do deníku výjimek** – náhled, po kterém zůstane stopa, není náhled.

K čemu je: zjistit před koncem měsíce, kolik toho je, jestli sedí hodiny, a jestli v timetrackingu nechybí nebo nepřebývá něco, co se má srovnat dřív, než vznikne doklad.

Vypiš tutéž tabulku jako v závěru, sloupce *Doklad* a *Draft* vynech, a přidej seznam toho, co by ještě chtělo rozhodnout.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Náhled je hotový a nic se nevystavilo – až to bude sedět, pusť /invoicing full.`
- `Náhled hotový není – brání tomu: <konkrétní seznam>.`
