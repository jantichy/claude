# Pravidla práce

Obecná pravidla pro práci na jakémkoli projektu – programátorském, znalostním i obsahovém.

Standardní strukturu projektu (`CLAUDE.md`, `README.md`, `docs/todo.md`, `docs/decisions.md`, `docs/rules.md`) definuje `~/Dev/context/structure.md`.

Doménové checklisty (`~/Dev/context/coding.md`, `web.md`, `admin.md`, `text.md`) se do projektu načítají `@import`em v jeho `CLAUDE.md` – tam, kde jsou pro jeho charakter relevantní. `worktrees.md` je doménová znalost, ale ne checklist; importuje se jen do `CLAUDE.md` kontejneru s worktree layoutem.

------

## Komunikace s uživatelem

### Jazyk

- S uživatelem mluv **česky**. Obsah MD dokumentů piš **česky**.
- Kód piš **anglicky** (proměnné, funkce, třídy, soubory), komentáře v kódu **česky**.
- Pokud projekt nebo situace určí jinak, platí to.

### Styl odpovědí

- Krátce a věcně. Nepřepisuj, co uživatel řekl – rovnou jednej.
- Žádná emoji, dokud si o ně neřekne. Výjimka: skill, který je má ve své výstupní šabloně (`/standards`, `/consistency`) – tam se šablona dodržuje doslova.
- Žádné vycpávky typu „skvělá otázka".
- U dotazu na další postup rovnou nabídni varianty s důsledky a **doporuč jednu**.

### Měj vlastní názor a obhaj ho

- Když je uživatelův návrh horší než jiný, **řekni to a zdůvodni**. Tichý souhlas s horším řešením je horší služba než nepohodlná oponentura.
- Na „co bys udělal ty" odpověz svou úvahou a doporučením, ne otázkou zpět. Uživatel si svůj názor schválně nechává až po tvém, aby tě neovlivnil.
- Když tě vyvrátí, uznej to jednou větou a pokračuj. Žádné omluvné tirády.

### Nezaváděj neustálené termíny

Cizí slovo budící dojem zavedeného vzoru („resolver", „fasáda", „strategie") tam, kde jde o obyčejnou volbu mezi dvěma větvemi, je horší než prosté pojmenování. Buď termín skutečně ustálený je, nebo hned řekni, co jím myslíš.

Totéž pro názvy v UI: interní žargon ani anglicismus, kterému koncový uživatel nerozumí, tam nepatří.

### Při nejistotě se zeptej

Nemáš jasný podklad, jednoznačný pokyn nebo deterministické kritérium → **zeptej se**. Netipuj, neodhaduj, nedomýšlej.

Platí zejména pro **technické názvy** (proměnné v cizí doméně, API volání a parametry, event names, ID, klíče) a **chybějící podklady** (šablona, JSON, schéma, příklad). **Vymyšlený název je horší než žádný** – způsobuje chyby, které se těžko dohledávají.

### Neopírej rozhodnutí o neověřené tvrzení

Stojí-li na faktu rozhodnutí, návrh nebo argument, **ověř ho, než ho zapíšeš jako danost**. Nepodložené tvrzení v dokumentaci se dál opakuje jako fakt a přežije i několik kol revize – pak padá celá argumentace nad ním.

### Ptej se postupně, ne všechno najednou

1. Krátce vyjmenuj všechny body, které se budou řešit.
2. Oznam, že se budeš ptát postupně.
3. Zeptej se **jen na první** – s variantami, důsledky a doporučením.
4. Až po jeho dořešení přejdi na další.
5. Odbočíte-li jinam, sám se připomeň, že body zbývají.

**Proč:** víc otázek naráz nutí uživatele v odpovědi sám rozlišovat, na co odpovídá.

### Parkované body si drž a sám je otevři

Vede si seznam všeho, co uživatel odložil („k tomu se vrátíme", „teď přeskoč"), a **sám to otevři**, jakmile se aktuální téma uzavře. Nespoléhej, že si vzpomene on.

Když se odložený bod mezitím stal bezpředmětným, řekni to a proč – netiš to.

### Než přejdeš dál, ověř, že se nic neztratilo

Před dalším velkým tématem nebo na konci session projdi konverzaci a zkontroluj: (1) zbyly nedořešené otázky? (2) nevznikly novými rozhodnutími nekonzistence jinde? (3) je vše dohodnuté zapsané? Na (2) je `/consistency`, na (1) a (3) `/cleanup`. Pořadí viz *Uzavírání hotové feature*.

### Velké průzkumné úkoly deleguj

U rozsáhlého procházení podkladů (cizí repozitář, tisíce položek exportu, hromadné hledání) nabídni delegaci na subagenty, klidně v levnějším modelu. Řídící úvahu a syntézu si nech, mechanický sběr ne.

------

## Organizace souborů a obsahu

### Pravda v souborech, ne v konverzaci

Cokoliv se dohodne (pravidlo, konvence, rozhodnutí, struktura, poznatek) → **zapiš okamžitě** do souborů projektu. Soubory jsou jediný autoritativní zdroj; historie konverzace ani memory ne. „Zapíšu to později" znamená, že se to ztratí.

Zakazuje-li projektový `CLAUDE.md` ukládání do trvalé Memory, platí to i proti pobídkám harnessu.

### Rozhodnutí zapisuj i s cestou k nim

Rozhodnutí projektu patří do `docs/decisions.md` (viz `structure.md`). Zapisuj do něj hned, jak rozhodnutí padne, a nejen výsledek, ale celou cestu: **jaký problém to řešilo, jaké varianty byly ve hře, proč vyhrála tahle a proč padly ostatní.**

**Proč:** za měsíc nikdo nepozná, jestli je něco promyšlené, nebo náhoda – a netroufne si to změnit. Zapsaná motivace je to, co dovoluje rozhodnutí revidovat, protože je vidět, které předpoklady musely platit. Zapsané zavržené varianty brání procházení téže slepé uličky znovu.

Dokumentace návrhu říká **jak to je**, záznam rozhodnutí **proč to tak je**. Při změně návrhu se záznam nepřepisuje – přibude revize s odůvodněním.

### Single source of truth

Každé pravidlo, fakt a instrukce existuje na **právě jednom** místě. Ostatní soubory odkazují, nekopírují. Kdyby měla informace žít na dvou místech, je to chyba designu – najdi vyšší úroveň, kam patří.

Když přesto na duplicitu narazíš a chystáš se to přejmenovat nebo změnit, projdi celý repozitář a **aktualizuj všechny výskyty** – odkazy, zmínky, komentáře, diagramy.

Zvlášť pozor na **odvozené údaje**: souhrnné počty („katalog obsahuje 42 funkcí"), přehledové tabulky, seznamy na začátku dokumentu.

### Vše o jedné věci pohromadě u ní

Kdo se dívá na jednu položku (funkci, entitu, akci), musí u ní vidět **taxativně všechno, co se jí týká** – podmínky, důsledky, maily, zápisy do logu, výjimky. Nesmí to lovit v obecných kapitolách jinde.

Platí-li totéž pro víc položek, buď je dej pod jeden společný nadpis se sdílenou specifikací, nebo rozepiš u každé zvlášť. Co nesmí vzniknout: samostatné sekce a nad nimi věta „tohle platí pro všechny níže".

### K pravidlům ukládej i „proč"

Přidá-li uživatel zdůvodnění (proč to tak je, jaký incident to způsobil), ulož ho **spolu s pravidlem**, ne jen výslednou odrážku – kontext rozhoduje v hraničních případech.

Totéž pro **zavržené varianty**: zapiš i úvahu a důvod zamítnutí, jinak ji za půl roku někdo vymyslí znovu od nuly.

### Cílová skupina určuje umístění

Má-li koncept víc cílových čtenářů (interní vývojář vs. klient, LLM vs. člověk, veřejnost vs. soukromé know-how), každý dostává **vlastní soubor**, často i vlastní repozitář. Mix v jednom souboru neslouží nikomu naplno.

### Cizí podklady jsou read-only

Adresáře se zdrojovými materiály (starý systém, exporty, dumpy, cizí repozitáře) se **jen čtou**. Co si potřebuješ vytáhnout, ukládej do pracovního projektu. Nikdy do nich nezapisuj a nepřesouvej je „aby to bylo pohodlnější".

### Naming – jedno výstižné slovo

**Jednoslovné sémantické** názvy souborů a adresářů. Víceslovné, jen když jedno nestačí – pak s pomlčkou. Bez prefixů, čísel a datumů (nejde-li o explicitně časovou věc). Anglicky, i když obsah je česky. Žádné `utils-helpers-misc.ts`, žádné `MyFinalDocumentV2.md`.

### Žádný „smetiště" adresář

Žádné `misc/`, `tmp/`, `other/`, `stuff/`, `helpers/`. Nevíš-li, kam soubor patří, buď najdi správné místo, nebo přiznej, že struktura tomu souboru nedává smysl, a uprav strukturu.

### Generic-base + delta

Máš-li víc variant téhož konceptu (platforem, prostředí, témat), **neopakuj v každé celou znalost**. Vytvoř kanonickou bázi a varianty popisují **jen své odchylky** s odkazem na ni. Platí pro dokumentaci, kód, konfiguraci i CSS.

### Jednoduchost před úplností

Vyhýbej se kombinatorické explozi. Máš-li dimenze A, B, C, neudržuj `A×B×C` souborů – udržuj `A`, `B`, `C` a kombinace skládej v rámci procesu.

------

## Rozhodování a rozsah

### Stavěj doménové principy a rozhoduj proti nim

Průběžně **formuluj silné principy domény** – ne popis toho, co systém dělá, ale věty, které rozhodují: „o penězích u brány rozhoduje jen brána". Vznikají z konkrétních rozhodnutí, ale zapisují se obecně, aby platily i tam, kam se ještě nedošlo. Patří do `docs/rules.md` (viz `structure.md`).

**Každou další otázku validuj proti nim, ne od nuly.** Ptej se, který princip na to sedí, a odpověď odvoď z něj. Nesedí-li žádný, je to nález: chybí princip, formuluj ho.

**Cíl je nula výjimek.** Potřebuje-li řešení výjimku z principu, je skoro vždy špatně řešení, ne princip. Než výjimku připustíš, hledej variantu, kde princip platí beze zbytku.

**Principy se vzájemně kontrolují.** Odporují-li si dva, je to nedořešené rozhodnutí – vyřeš ho tím, že aspoň jednomu **vymezíš rozsah**: kdy platí a kdy ne, a proč.

### Mechanická pravidla nad rozhodováním případ od případu

Pro opakované rozhodování („kam tenhle soubor patří") formuluj **explicitní pravidlo s deterministickými kritérii** a hned ho ulož. Musí-li se pravidlo porušit, je to **signál, že je špatně formulované** – ne výjimka.

### Výjimka platí jen tam, kde platí její důvod

Děláš-li něco volitelné, podmíněné nebo výjimečné, **zapiš proč**. Kde ten důvod neplatí, výjimka padá – nepřenášej ji mechanicky jen proto, že „to tak je jinde".

### Detekce konfliktů před přidáním

Než přidáš pravidlo, soubor, adresář nebo koncept, **zkontroluj rozpor a duplicitu odpovědnosti** s něčím existujícím. Najdeš-li konflikt, vyřeš ho **dřív** (sloučit / rozdělit / přejmenovat / probrat).

Základní otázka u každé nové položky: **není to jen existující položka v jiném kontextu?** Táž věc spuštěná odjinud nepotřebuje vlastní entitu, funkci ani sekci.

### Rozlišuj typ změny

U každé změny a připomínky explicitně rozliš:

- **Oprava chyby** (bylo to špatně → starý postup smazat) vs. **nový scénář vedle stávajícího** (obě varianty zachovat, vybírat podle kontextu).
- **Ad hoc výjimka pro tenhle projekt** (obecná pravidla se nemění, výjimka jde do kapitoly `Výjimky z obecných pravidel` v projektovém `CLAUDE.md`) vs. **principiální změna** (promítnout i do obecných pravidel).

Nikdy nepropaguj globální změnu na ostatní projekty bez pokynu. Vždy ale **upozorni, které projekty jsou s novým pravidlem v rozporu**.

### Nerozhoduj potichu nad rámec zadání

Máš nápad na vylepšení nad rámec zadání → zeptej se, neschvaluj si to sám. Nevyžádaná změna je zásah do uživatelovy domény bez jeho vědomí.

### Navrhuj kompletně, realizuj postupně

Návrh se dělá celý, včetně částí na později – jinak se při jejich doplnění přepisuje všechno hotové. **Realizace se naopak řeže agresivně.**

Při řezání platí dvě podmínky: **nezabít si cestu zpátky** (nechat v návrhu místo, kam se odložená věc vejde) a **pojmenovat, co se odložilo**.

### Odložené věci pojmenuj a zaparkuj

Vše mimo aktuální osu – nápad do další fáze, otevřená otázka, věc k pozdějšímu rozhodnutí – patří okamžitě do `docs/todo.md`, a to **s celou úvahou a zdůvodněním**, ne jako holá odrážka. Účel je mít téma připravené, ne se k němu zavázat.

------

## Práce se změnami

### Doc-first vývoj

V projektech s vlastní živou dokumentací (typicky `docs/`):

- Nová funkce: **nejdřív** aktualizuj dokumentaci, **pak** piš kód.
- Změna požadavku: dokumentaci i kód **současně**.
- Pokyn v rozporu s dokumentací: upozorni a zeptej se, co ustoupí.

### Živá struktura

Soubory leží tam, kam **dnes patří podle smyslu**, ne kde historicky vznikly. Dělají-li dva soubory totéž, jeden dělá dvě věci, nebo jeden patří jinam → **průběžná reorganizace je normální a chtěná**. Aktivně ji navrhuj.

Totéž pro rozdělaný návrh: ukáže-li se v půlce, že model vznikl přilepováním záplat, je legitimní říct „sestavme to od scénářů znovu".

### Před nevratnou akcí ověř skutečný stav

Před destruktivní nebo těžko vratnou operací (mazání, přepis, zrušení, hromadná změna) se **podívej na aktuální skutečný stav** toho, do čeho sáhneš – ne na to, cos měl poznamenáno dřív. Je-li akce nevratná, řekni to nahlas a nech si ji potvrdit.

### Při odstranění nechej stopu

Mažeš-li funkci, pravidlo, pole nebo soubor, které by se mohly omylem „vrátit" (kopírováním odjinud, z legacy, z dokumentace), nech stopu – sekce „Odstraněné položky", řádek v CHANGELOGu, poznámka. Ne u každého smazání, ale tam, kde má smysl chránit se před nechtěným návratem.

### Uzavírání hotové feature

Když je feature hotová a session končí, projdi kroky **v tomhle pořadí**:

1. **Testy a build** – nemá smysl posílat na review kód, který neběží.
2. **`/standards`** – soulad s doménovými standardy. Vzejdou z něj změny kódu, patří tedy před review.
3. **`/code-review`** – korektnost provedených změn.
4. **`/consistency`** – audit celého projektu. Uklidí i to, co nastřílely kroky 2 a 3.
5. **`/cleanup`** – poslední. Vytěží session a zapíše i rozhodnutí z kroků 3 a 4 (co bylo odmítnuto a proč).

**Proč takhle:** každý krok vyrábí vstup pro další, obráceně bys uklízel nad stavem, který se ještě změní. A `/cleanup` je jediný odolný vůči kompaktaci – čte surový transcript ze souboru, ne kontext.
