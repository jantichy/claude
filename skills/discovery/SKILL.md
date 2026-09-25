---
name: discovery
description: Skill se použije, když uživatel zadá "/discovery", nebo chce před psaním zadání zjistit, proč se to má vůbec stavět a do jakého světa produkt vstupuje – jaký problém to komu řeší a čím je doložené, že ho chce řešit, kdo je konkurence, co umí a za kolik, čím se proti nim vymezíme a co je na tom rizikové. Vyrábí docs/demand.md, docs/competition.md a docs/risks.md a předává do specifikace. Hlavní otázka je proč: postavit pečlivě něco, co nikdo nechce, je nejdražší způsob selhání a tenhle krok je místo, kde se má odchytit. Na rozdíl od /specify, který popisuje náš produkt, tenhle skill zkoumá svět venku a je opakovatelný sám o sobě. Nedělá obchodní ani marketingový plán a uživatelský výzkum s živými lidmi nepředstírá.
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, WebSearch, WebFetch]
---

# Discovery

## Co skill dělá

Než se začne psát zadání, zjistí, **proč se to má stavět** a do čeho to vstupuje. Sepíše **tři dokumenty**:

| Dokument | Odpovídá na otázku | K čemu je |
|---|---|---|
| **`docs/demand.md`** | Proč to vůbec stavět – jaký problém to komu řeší, jak ho dnes řeší, co ho to stojí a čím je doložené, že ho chce řešit jinak | Z toho plyne, jestli se do toho vůbec pouštět, a všechno ostatní je pak podřízené tomuhle |
| **`docs/competition.md`** | Kdo to už dělá, co umí, za kolik – a jaká je proti nim naše pozice | Z toho plyne, co produkt musí umět, aby ho někdo vzal, a čím se má lišit |
| **`docs/risks.md`** | Co je na tom rizikové a čím to v produktu mitigujeme | Z toho plyne, co musí být postavené jinak, než by se stavělo bez toho |

**Hlavní z těch tří je první.** Konkurence i rizika se dají dohnat později a chyba v nich se pozná za provozu; **nedoložená poptávka se nepozná nikdy**, protože se projeví jako hotový produkt, který nikdo nepoužívá. Tenhle krok je jediné místo v celém cyklu, kde se na to ještě stojí za pár hodin – od `/specify` dál už každý krok předpokládá, že je rozhodnuto stavět.

V *Životním cyklu projektu* (`~/.claude/RULES.md`) je to druhý krok osy: navazuje na `/project` a předává na `/specify`.

**Je opakovatelný sám o sobě.** Druhý běh nad hotovými dokumenty je aktualizace, ne nový začátek – konkurence se hne bez ohledu na to, jestli se zrovna mění zadání.

## Co skill nedělá

- **Nepíše zadání.** Co náš produkt je, pro koho a co má umět, sepisuje `/specify` do `docs/requirements.md`. Tenhle skill mu dodává vstup, ne závěr.
- **Nezakládá projekt.** Strukturu, git a doménové importy dělá `/project`. Chybí-li, upozorní a nabídne ho.
- **Nedělá obchodní ani marketingový plán.** Žádná finanční projekce, žádný kanálový mix, žádná komunikační strategie. Sbírá jen to, z čeho plynou požadavky na produkt.
- **Nedělá osobní brand ani pozicování autora.** To drží `~/Dev/context/brand/brand.md`; tady jde o pozici produktu proti konkurenčním produktům.
- **Nepředstírá uživatelský výzkum.** Doklad z veřejného zdroje není rozhovor se zákazníkem a nedá se jím nahradit. Skill dohledá, co o problému lidé sami napsali, a sesbírá, co ví uživatel – **nedokáže-li poptávku doložit, řekne to** místo toho, aby ji odvodil (`~/.claude/RULES.md`, *Zapiš i to, co vědomě nemáš*).
- **Nerozhoduje, jestli se to postaví.** Vyrobí verdikt o poptávce s doložením; co s ním, rozhoduje uživatel. Skill jen nedovolí, aby se přes nedoloženou poptávku přešlo mlčky.
- **Neoponuje výsledek.** Posudek čerstvýma očima dělá `/oponent`, kterému se dokumenty předávají stejně jako zadání.
- **Nedělá analytický report z dat.** Na to je `/report`; tady se sbírají fakta o cizích produktech, ne čísla z měření.

## Kdy se přeskakuje

**Základní kritérium drží `~/.claude/skills/LIFECYCLE.md`** – tam, kde stojí popis tohohle kroku. Neopisuj ho sem: rozhodnutí o přeskakování se ladí napříč celým cyklem a opsaná kopie se s ním tiše rozejde. Níž je jen to, co z obecného kritéria neplyne.

**Rozsah se škrtá po dokumentech, ne celý.** Obecné kritérium mluví o trhu, a trh se týká `competition.md` – ne zbylých dvou:

| Co z projektu platí | Co se dělá |
|---|---|
| Nemá trh, ale má uživatele (interní nástroj, zakázka pro klienta) | `demand.md` a `risks.md` ano, konkurenci vynech – Fázi 3 a Fázi 4 přeskoč |
| Přírůstek do hotového produktu, kde se o „proč“ rozhodlo dřív **a je to zapsané** | Přeskoč celý skill a odkaž na to místo. Není-li to zapsané, rozhodnuto to není |
| Nic z toho | Celý běh |

**`demand.md` se nepřeskakuje kvůli tomu, že produkt nemá trh.** Interní nástroj, který nikdo nepoužívá, a zakázka, kterou si klient zaplatil a jeho lidé ji obcházejí, jsou tentýž způsob selhání jako aplikace bez zákazníků – jen za ni platí někdo jiný. Otázka „kdo ten problém má a jak ho dnes řeší“ platí i tam, kde se o stavbě rozhodlo bez nás; mění se jen to, že verdikt nerozhoduje o zahájení, ale o tom, co se má postavit.

**Hraniční případ je zakázka pro klienta**, která bude mít vlastní uživatele. Konkurence tam nerozhoduje o tom, jestli se to postaví – to už je rozhodnuté –, ale pořád rozhoduje o tom, co lidé od takového produktu čekají. Zeptej se, jestli má smysl; nerozhoduj to za uživatele.

## Zásady pro celý průběh

- **Ptej se postupně a přes tool `AskUserQuestion`** – viz `~/.claude/RULES.md`, *Ptej se postupně, ne všechno najednou*.
- **Žádný údaj bez doložení.** Cena, funkce ani počet zákazníků se nezapisuje bez URL a data zjištění. Viz *Ověření*.
- **Nic si nevymýšlej** – ani jméno konkurenta, ani tarif. Viz `~/.claude/RULES.md`, *Při nejistotě se zeptej*.
- **Zapisuj průběžně**, ve chvíli, kdy fakt dorazí, ne až na konci.
- **Nic neprogramuje.** Zákaz implementace z `/specify` platí tím spíš tady – ještě není ani zadání.

------

## Fáze 0 – Příprava

Postupuj podle `~/.claude/skills/PREFLIGHT.md`. Navíc:

1. **Zjisti, co v projektu už je** – `docs/demand.md`, `docs/competition.md`, `docs/risks.md`, `docs/requirements.md`, `docs/research/`, `README.md`. Z toho urči vstupní bod:

   | Stav | Kde začít |
   |---|---|
   | Ani jeden dokument neexistuje | Fáze 1, celý běh |
   | `demand.md` existuje | Verdikt o poptávce **přečti a potvrď s uživatelem**, nepřepisuj ho. Změnil-li se od minula svět (nový hráč, zaniklý zvyk), je to nález do *Doklady poptávky*, ne nový verdikt z ničeho. |
   | `competition.md` existuje | Aktualizace: **nepřepisuj**, ověř dosavadní údaje a doplň nové. Sekci *Co poměřujeme* jen potvrď. |
   | `requirements.md` už existuje | Zadání se psalo dřív – **z Fáze 1 přeskoč jen otázky na kategorii a odlišení** a odvoď je z něj; otázky na problém a poptávku polož i tak, protože právě na ně zadání neodpovídá. Řekni, co sis odvodil, a nech to potvrdit. |
   | Existuje jen `risks.md` | Zeptej se, jestli se má doplnit i poptávka a konkurence, nebo jde jen o revizi rizik. |

2. **Urči rozsah běhu.** Platí-li *Kdy se přeskakuje*, řekni nahlas, které dokumenty vynecháváš a proč – nezakládej prázdné.

------

## Fáze 1 – Problém a jeho nositel

**Tohle je jádro celého skillu**, ne rozcvička před rešerší. Zároveň z něj vypadne pole hledání, bez kterého by se nedalo hledat: nevíš-li, v jaké kategorii produkt soutěží, najdeš buď všechno, nebo nic.

Zeptej se **na pět věcí, jednu po druhé**:

1. **Jaký problém to řeší** a komu ho řeší – čí je to dnes bolest a jak často na ni narazí.
2. **Co ten člověk dělá dneska**, když to nemá, a **co ho to stojí** – čas, peníze, chyby, ztracené zákazníky. Nejsilnější konkurent bývá tabulka, papír nebo zvyk, ne jiná aplikace, a útrata za dnešní řešení je první měřitelná stopa poptávky.
3. **Odkud víš, že to chce řešit** – koho se uživatel ptal, kdo si postěžoval, kdo si to vyžádal, kdo za to dnes platí. **„Nikoho, přišlo mi to jako dobrý nápad“ je legitimní odpověď** a zapíše se doslova; nedoložená poptávka je stav, který se zaznamenává, ne vada, kterou je potřeba zamluvit.
4. **V jaké kategorii produktu tedy soutěžíme** – jak by to člověk hledal, kdyby to hledal.
5. **Čím se to má hrubě lišit**, pokud už uživatel představu má. Nemá-li, je to v pořádku – od toho je zbytek skillu.

**Dojem není doklad a nesmí se na něj přepsat.** Odpověď typu „myslím, že to lidi chtějí“ se zapíše jako dojem i s tím, čí je; teprve URL, číslo nebo jmenovaný člověk, který o to požádal, je doklad. Rozdíl se stírá tiše a právě na něm stojí celý verdikt ve Fázi 2.

**Není to specifikace.** Neptej se na persony, funkce, MVP ani technologii – to je práce `/specify` a dělá se **až po** tomhle skillu schválně, aby ji analýza mohla ovlivnit.

**Zápis jde na dvě místa:** odpovědi 1 až 3 do `docs/demand.md` (sekce *Problém a jeho nositel*, *Dnešní řešení*, první doklady), odpovědi 4 a 5 do `docs/competition.md` jako úvodní sekce `## Co poměřujeme`. `/specify` obojí čte jako hotový vstup a na totéž se neptá podruhé.

------

## Fáze 2 – Doklady poptávky

**Pusť subagenty na blok *Poptávka*** z `~/.claude/skills/discovery/paths.md` – **2 až 3 cesty, *Hlas problému* je povinná**. Je to vlastní rozpočet, ne část rozpočtu pro konkurenční rešerši: hledá se, co o problému říkají **lidé**, ne co nabízejí produkty.

**Typem `researcher`, výchozí model, `low`.** Je to sběr s vynuceným tvarem výstupu a jeho chyba se pozná levně: doklad bez URL se zahodí hned pod tímhle odstavcem.

**Ověř nálezy stejným sítem jako ve Fázi 3** – vypadne, co nemá `basis` s funkční URL; co má nízkou jistotu u nosného údaje, buď doověř přes `WebFetch`, nebo zapiš jako neznámé; duplicity mezi agenty slouč. Navíc přísněji na jednu věc: **doklad musí mluvit o problému, ne o kategorii produktu**. Článek „deset nejlepších nástrojů na X“ dokládá, že někdo píše o nástrojích, ne že někdo má ten problém. Stížnost člověka, který popisuje, jak to dnes obchází, doklad je.

Sepiš `docs/demand.md`:

```markdown
# Proč to stavíme

## Problém a jeho nositel
<co to je, koho to potká, jak často, co ho to stojí – z Fáze 1>

## Dnešní řešení
<čím to lidé řeší teď a proč jim to nestačí>

## Doklady poptávky
- <co přesně dokládá> – <URL a datum zjištění, nebo „od uživatele: <kdo a kdy to řekl>“>

## Dojmy bez dokladu
- <tvrzení> – <čí dojem to je>

## Co by verdikt vyvrátilo
<jaké zjištění by znamenalo nestavět – konkrétně, aby se to dalo příště ověřit>

## Verdikt
**Poptávka doložená** – <čím>
**Poptávka nedoložená** – <co chybí a jakým nejmenším pokusem by se to dalo zjistit>
```

**Verdikt má dvě hodnoty a žádnou mezi nimi.** „Spíš doložená“ znamená nedoložená – je to táž hranice jako u závěrečného verdiktu každého skillu.

**Sekce *Co by verdikt vyvrátilo* je povinná i u doložené poptávky.** Bez ní se z verdiktu stane tvrzení, které nejde zpochybnit, a druhý běh skillu nemá co měřit.

**Vyjde-li verdikt nedoložený, zastav se a zeptej** přes `AskUserQuestion`. Tři varianty a každá má cenu:

- **Zastavit** a poptávku nejdřív ověřit – nejmenší pokus z verdiktu (oslovit pět lidí z cílové skupiny, nabídnout to někomu ručně, vystavit stránku a měřit zájem).
- **Pokračovat s vědomím rizika** – pak se to zapíše do `docs/risks.md` jako riziko a *Promítnutí do produktu* u něj znamená zmenšit první verzi tak, aby se poptávka ověřila co nejdřív.
- **Pokračovat, protože o stavbě rozhodl někdo jiný** (zakázka, interní zadání) – zapíše se, kdo rozhodl, a verdikt pak neřídí, jestli stavět, ale co stavět.

**Mlčky přes nedoloženou poptávku neprocházej.** Je to jediné místo celého cyklu, kde tahle otázka zazní – od `/specify` dál už se všude předpokládá, že je rozhodnuto.

------

## Fáze 3 – Rešerše konkurence

**Pusť subagenty paralelně, jedním voláním s víc tool calls.** Každý dostane jinou cestu hledání – redundantní agenti najdou tolikrát totéž, kolik jich pustíš.

**Typem `researcher`** (`subagent_type`). Zadání zní prohledat web a vrátit JSON, takže agent nemá co spouštět ani kam zapisovat – a typ bez shellu je jediné, čím ta hranice doopravdy drží; věta v zadání ne (`~/.claude/skills/SKILLS.md`, *Model, effort a delegace*).

**Výchozí model, `low`** (`~/.claude/RULES.md`, *Model a effort podle úkolu*). Je to sběr s vynuceným tvarem výstupu a jeho chyba se pozná levně: údaj bez URL zahodí *Ověření* hned pod tímhle odstavcem. Na `xhigh` běží až syntéza a rizika, kde se chyba násobí do zadání.

**Cesty, pravidla výběru i zadání pro agenty drží `~/.claude/skills/discovery/paths.md`.** Přečti si ho celý a řiď se jím: je v něm katalog cest ve čtyřech blocích, pravidla, kolik jich pustit a která je povinná, a šablony zadání podle toho, co cesta vrací. **Blok *Poptávka* se tady nepouští** – ten patří Fázi 2 a má vlastní rozpočet.

### Ověření

**Nálezy se nezapisují rovnou.** Projdi je a zahoď:

- co nemá `basis` s funkční URL,
- co má `confidence: nízká` u ceny nebo klíčové funkce – buď údaj ověř sám přes `WebFetch`, nebo ho zapiš jako neznámý,
- duplicity mezi agenty – týž produkt našlo víc cest, sloučí se do jednoho záznamu.

**Co ověření nepřežije, se do dokumentu nedostane.** Vymyšlený konkurent nebo cena o řád vedle je horší než prázdné místo: postaví se na tom rozhodnutí o produktu a nikdo ho nezpochybní, protože vypadá doloženě.

Zapiš do `docs/competition.md` a **u každého údaje nech datum zjištění** (`date +%F`, ne z hlavy – `~/.claude/RULES.md`, *Hodnotu, kterou čte stroj, nepiš*). Ceny stárnou a bez data se nepozná, co je čerstvé.

------

## Fáze 4 – Pozice a odlišení

**Nejsilnější model, `xhigh`.** Tady se z dat stává rozhodnutí, které se propíše do MVP a do každého úkolu pod ním – přesně ten případ, kdy se na úsudku nešetří.

Projdi nálezy s uživatelem a sepiš závěr do sekce `## Naše pozice a odlišení` v témž souboru. Tři skupiny, každá jako seznam:

- **Co musíme mít**, protože to má každý a bez toho nás nikdo nevezme vážně. Tohle je nejcennější výstup celého skillu – jsou to požadavky, na které by se jinak přišlo až po spuštění.

  **Stav „máme to, nebo ne“ se u každého řádku ověřuje proti návrhu, ne odhaduje.** Běží-li skill nad projektem, který už návrh má – `docs/model.md`, `docs/transitions.md`, `docs/architecture.md` –, **otevři ho a najdi tu funkci**, než napíšeš, že chybí. Totéž platí pro každý nález, který odsud odchází do `docs/todo.md`.

  **Proč se na to musí upozorňovat:** celý tenhle krok se dívá ven a jeho vstupem jsou podklady o trhu, ne dokumentace vlastního řešení. Nález tvaru *„tohle systém nemá“* proto vzniká z toho, co skill **nevidí**, a vypadá doloženě, protože doložená je ta půlka o konkurenci. **Vymyšlený požadavek stojí víc než vynechaný:** dostane se do fronty jako práce, projde řezem MVP a rozhoduje se o něm znovu, přestože je hotový.

  **Doloženo 25. 9. 2026** v rezervačním systému: z osmi řádků se stavem **nemá** byly dva neplatné – volba mezi zálohovkou a daňovým dokladem, kterou drží zděděné nastavení `document`, a vynechání platebního kroku u nulové ceny, které řeší `payFree` a stav `FREE_PAID`. Obojí bylo rozhodnuté měsíce předtím a našlo se až při práci na té položce. **Zbylé nálezy platily**, takže to není argument proti kroku, ale proti psaní stavu zpaměti.
- **Co děláme jinak** a proč si kvůli tomu někdo vybere nás. U každého bodu **řekni, čím je to doložené** – co v rešerši ukazuje, že to konkurence nemá nebo dělá špatně. Odlišení bez opory v datech je přání, ne pozice.
- **Kde vědomě zaostáváme** a proč nám to nevadí. Neprázdné: prázdná skupina znamená, že se tvrdí „budeme lepší ve všem“, což neplatí nikdy.

**Nepiš marketingové claimy.** „Nejjednodušší nástroj na trhu“ není pozice; „jako jediný umí vystavit fakturu bez toho, aby si zákazník založil účet“ je pozice, protože se dá ověřit.

**Sporná místa předlož uživateli**, ne aby je odklikl, ale aby rozhodl. Ptáš se na volbu, ne na potvrzení.

------

## Fáze 5 – Registr rizik

Sepiš `docs/risks.md`. **Není to SWOT** – silné stránky a příležitosti už drží *Naše pozice a odlišení*, tady jsou slabiny a hrozby.

**Odkud rizika brát** – projdi všech pět zdrojů, ne jen ten první:

1. **Z rešerše** – konkurent, který to umí líp; nízká bariéra vstupu; velký hráč, který to může přidat jako funkci.
2. **Z povahy produktu** – na čem stojí, co musí platit, aby to fungovalo, kde závisí na někom cizím.
3. **Z pole hledání** – co jsme ve Fázi 1 předpokládali a co se stane, když ten předpoklad neplatí.
4. **Z toho, co uživatel sám ví** a zatím neřekl. Zeptej se: *čeho se na tom projektu bojíš?* Odpověď bývá přesnější než cokoliv, co se dá vyhledat.
5. **Z verdiktu o poptávce.** Skončila-li Fáze 2 nedoloženou poptávkou, je to **riziko s nejvyšším dopadem a zapisuje se první**; *Promítnutí do produktu* u něj není volitelné a znamená zmenšit první verzi tak, aby se poptávka ověřila dřív, než se postaví zbytek. Vyšla-li doložená, patří sem místo toho to, co ji může zneplatnit – ze sekce *Co by verdikt vyvrátilo*.

U každého rizika:

```markdown
### <Riziko jednou větou>

- **Dopad:** co se stane, když nastane – konkrétně, ne „bylo by to špatné“
- **Pravděpodobnost:** vysoká / střední / nízká, i s tím, z čeho to soudíme
- **Mitigace:** čím tomu čelíme
- **Promítnutí do produktu:** co se kvůli tomu v návrhu změnilo nebo přibylo
```

**Pole *Promítnutí do produktu* je smysl celého souboru.** Bez něj je to seznam obav, který nikoho nezavazuje a nikdo ho nečte. Vyjde-li prázdné, jsou dvě možnosti a obě se musí napsat: buď se produkt kvůli tomu riziku změní – pak to patří do zadání a `/specify` to tam ponese –, nebo riziko **vědomě přijímáme** a napíše se proč (`~/.claude/RULES.md`, *Zapiš i to, co vědomě nemáš*).

**Rizika technického řešení sem nepatří** – „nezvládne to zátěž“, „ta knihovna může skončit“. Ta jdou do sekce *Rizika* v `docs/architecture.md`, protože závisí na zvolené technologii, a ta se ještě nevybrala. Hranice je táž jako mezi požadavky a návrhem: sem produkt a trh, tam řešení.

**Seřaď podle dopadu**, ne podle pořadí, v jakém tě napadla.

------

## Fáze 6 – Předání

**Sebe-revize** – projdi všechny tři dokumenty:

1. **Doložení** – má každý faktický údaj URL a datum? Údaj bez opory přesuň mezi otevřené otázky, do *Dojmů bez dokladu*, nebo smaž.
2. **Prosakování hranice** – není v `competition.md` popis našeho produktu? Není v `risks.md` technické riziko? Nestojí v `demand.md` doklad, který mluví o kategorii produktu místo o problému? Přesuň.
3. **Neprázdnost** – má *Kde vědomě zaostáváme* aspoň jednu položku? Má každé riziko vyplněné *Promítnutí do produktu*? Má `demand.md` vyplněné *Co by verdikt vyvrátilo*?
4. **Verdikt** – je v `demand.md` jedna ze dvou hodnot, ne něco mezi? Je u nedoložené poptávky zapsané, jak uživatel rozhodl dál, i s důvodem?
5. **Vymyšlené věci** – je tam jméno, číslo nebo tvrzení, které jsi neměl od uživatele ani ze zdroje? To je nález.

**Oponentura.** Nabídni `/oponent docs/demand.md docs/competition.md docs/risks.md` – rešerši psal ten, kdo si zároveň přeje, aby produkt vyšel, a to je přesně ta zaujatost, kterou má posudek chytat.

**Její nálezy podléhají témuž ověření jako *Co musíme mít*** (Fáze 4). Posudek dostane jen tyhle tři dokumenty, takže o vlastním návrhu neví nic a řekne *„není rozhodnuté“* i tam, kde rozhodnuté je. Než nález zapíšeš do `docs/todo.md`, dohledej ho v návrhu. **Rizika patří do posudku taky**, protože je to ze všech tří dokument, kde se nejvíc tvrdí a nejmíň dokládá: pravděpodobnost i *Promítnutí do produktu* jsou úsudek, ne údaj s URL. Panel hledisek si sestaví sám.

**Předání.** Po schválení nabídni `/specify`. Ten si dokumenty najde sám a **nebude se ptát na to, co je v nich** – zejména sekce *Co poměřujeme* a *Verdikt* bere jako hotový vstup.

------

## Fáze 7 – Závěr

```
## Discovery hotová

**Dokumenty**
- docs/demand.md – verdikt: <doložená | nedoložená>, <počet> dokladů, <počet> dojmů bez dokladu
- docs/competition.md – <počet> konkurentů, <počet> ověřených údajů
- docs/risks.md – <počet> rizik (<počet> promítnutých do produktu, <počet> přijatých)

- **Spotřeba:** [N agentů: X na poptávku, Y na konkurenci · na jakém modelu a effortu]

**Proč to stavíme**
- <problém jednou větou a kdo ho má>
- <čím je poptávka doložená, nebo co k doložení chybí a jak uživatel rozhodl dál>

**Co z toho plyne pro produkt**
- Musíme mít: <počet> položek
- Odlišujeme se: <počet> položek
- Vědomě zaostáváme: <počet> položek

**Zahozeno při ověření**
- <počet> nálezů bez doložení

**Otevřené otázky**
- [seznam, nebo „žádné“]

**Další krok**
- [/oponent nad demand.md, competition.md a risks.md / /specify]
```

Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo – `~/.claude/RULES.md`, *Styl odpovědí*.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Podklady jsou hotové a ověřené, poptávka je doložená – můžeme na zadání.`
- `Podklady hotové nejsou – brání tomu: <konkrétní seznam>.`

**Vyšla-li poptávka nedoložená, platí pořád hotové znění** – zjištění je výsledek, ne nedodělek –, ale musí to být v něm vidět i s tím, jak uživatel rozhodl:

- `Podklady jsou hotové a ověřené, poptávka doložená není – <co chybí>. Rozhodls <zastavit a ověřit ji | pokračovat s rizikem, které je v risks.md první>.`

Běželo-li se bez konkurence, protože projekt nemá trh, platí druhá dvojice:

- `Poptávka a rizika jsou hotové a ověřené, konkurenci jsme vynechali – <důvod>. Můžeme na zadání.`
- `Podklady hotové nejsou – brání tomu: <konkrétní seznam>.`
