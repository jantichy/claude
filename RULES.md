# Pravidla práce

Obecná pravidla, kterými se řiď při práci na jakémkoli projektu — programátorském, znalostním i obsahovém.

------

## Komunikace s uživatelem

### Jazyk

- S uživatelem komunikuj **česky**
- Obsah MD dokumentů piš **česky**, pokud není v daném projektu nebo situaci řečeno jinak
- Kód piš **anglicky** (proměnné, funkce, třídy, soubory)
- Komentáře v kódu piš **česky**, pokud není v daném projektu nebo situaci řečeno jinak

### Styl odpovědí

- Odpovědi krátké a věcné — nepřepisuj co uživatel řekl, rovnou jednej
- Nepoužívej emoji, pokud o ně uživatel nepožádá

### Při nejistotě se zeptat

Kdykoliv se dostaneš do situace, kde nemáš jasný podklad, jednoznačný pokyn nebo deterministické kritérium pro rozhodnutí → **zeptat se**. Nikdy netipovat, neodhadovat, nedomýšlet, kreativně doplňovat. Vymyšlený technický název, hádaná struktura, podsunutá interpretace zadání způsobí chyby, které jsou těžko dohledatelné. Ptát se je vždycky levnější.

Týká se to zejména **technických názvů** (názvy proměnných v cizí doméně, API volání a parametry, event names, IDs, klíče) a **chybějících podkladů** (šablona, JSON, schéma, příklad). Když přesnou hodnotu neznáš ze zdrojů v projektu nebo od uživatele, zeptej se, **vymyšlený název je horší než žádný**.

------

## Organizace souborů a obsahu

### Pravda v souborech, ne v konverzaci

Cokoliv se v konverzaci dohodne (pravidlo, konvence, rozhodnutí, struktura, nový poznatek) → **okamžitě zapsat** do příslušných souborů projektu (typicky `CLAUDE.md` nebo specializovaný soubor). **Soubory jsou jediný autoritativní zdroj** — nikdy se nespoléhat na historii konverzace ani memory. „Až někdy později to zapíšeš" znamená, že se to ztratí.

### Single source of truth — každá informace na právě jednom místě

Každé pravidlo / fakt / instrukce existuje na **právě jednom** místě. Jiné soubory jen odkazují, nekopírují. Pokud by stejná informace měla žít na dvou místech, je to chyba designu — najdi vyšší úroveň nebo jiné nové společné místo, kam patří, a ostatní jen referencují.

Když přesto narazíš na situaci, kde stejná informace existuje na víc místech, a chystáš se ji přejmenovat / změnit (soubor, termín, konvenci, klíč…), projdi celý repozitář a **aktualizuj všechny výskyty** — odkazy, zmínky v textu, komentáře, strukturální diagramy. Žádná reference nesmí zůstat zastaralá.

### K pravidlům ukládat i „proč" a kontext

Když uživatel přidá zdůvodnění (proč to tak je, co k tomu vedlo, jaký incident to způsobil) → uložit do dokumentace **včetně tohoto zdůvodnění**, ne jen výslednou odrážku. Kontext pomáhá v budoucnu správně aplikovat pravidlo v hraničních případech a pochopit, proč bylo zavedeno.

### Cílová skupina určuje umístění

Když má jeden koncept víc cílových čtenářů (interní vývojář vs. klient; backend dev vs. frontend dev; LLM vs. člověk; veřejnost vs. soukromé knowhow), každý čtenář dostává **vlastní soubor** (a často i vlastní repozitář). Mixovat cílové skupiny v jednom souboru znamená, že nikomu neslouží 100%.

### Naming — jedno výstižné slovo

Preferuj **jednoslovné, sémantické** názvy souborů a adresářů. Víceslovné jen když jedno slovo nestačí (a i pak co nejstručnější, oddělené pomlčkou). Bez prefixů, čísel nebo datumů v názvu (pokud nejde o explicitně časovou věc). Žádné `utils-helpers-misc.ts`, žádné `MyFinalDocumentV2.md`. Anglicky, i když obsah je česky.

### Žádný „smetiště" adresář

Žádné `misc/`, `tmp/`, `other/`, `stuff/`, `helpers/`. Když nevíš, kam soubor patří, **neumísťuj ho do smetiště** — buď najdi správné místo, nebo přiznej, že struktura tomu souboru nedává smysl, a uprav strukturu.

### Generic-base + delta files

Když máš víc variant stejného konceptu (platforem, systémů, prostředí, témat), **neopakuj** v každé variantě celou znalost. Vytvoř kanonickou bázi (`generic.md`, base třídu, defaultní konfiguraci, ...) a varianty popisují **jen své odchylky** s explicitním odkazem na bázi. Platí pro dokumentaci, kód, konfiguraci, CSS i cokoli dalšího.

### Jednoduchost před úplností

Vyhýbej se kombinatorické explozi. Když máš dimenze A, B, C, neudržuj `A×B×C` souborů — udržuj `A` souborů, `B` souborů, `C` souborů a kombinace skládej v rámci procesu. **Přímočará jednoduchost před překomplikovaným systémem kombinací všeho se vším.**

------

## Práce se změnami

### Mechanická pravidla nad rozhodováním případ od případu

Pro opakované rozhodování („kam tenhle soubor / koncept patří", „jakou strukturu zvolit") vždy formulovat **explicitní pravidlo** s deterministickými kritérii, ne soudit ad hoc. A hned pravidlo uložit do odpovídajícího souboru. Snižuje decision fatigue a drží konzistenci. Když se pravidlo musí porušit, je to **signál**, že pravidlo je špatně formulované — ne výjimka.

### Detekce konfliktů před přidáním

Když přidáváš nové pravidlo / soubor / adresář / koncept, **aktivně zkontrolovat**, jestli není v rozporu nebo neduplikuje odpovědnost s něčím existujícím. Pokud najdeš konflikt → **upozornit a vyřešit** (sloučit / rozdělit / přejmenovat / diskutovat) **dřív**, než nový prvek přijmeš. Rozporuplná pravidla a překrývající se odpovědnosti znemožňují správné rozhodování v hraničních případech.

### Rozlišování situací

Při jakékoliv změně/připomínce vždy explicitně rozlišit:

- **Oprava chyby** (bylo to doteď špatně → starý postup smazat nebo nahradit novým) versus **Další nový scénář vedle stávajícího** (přidat novou variantu, obě zachovat, do budoucna z nich vybírat podle kontextu).

- **Ad hoc výjimka pro tento projekt** (obecná pravidla se nemění, výjimku zaznamenat do kapitoly `Výjimky z obecných pravidel` v projektovém `CLAUDE.md`, neexistující kapitolu založit při první potřebě) versus **Principiální změna** (promítnout i do obecných pravidel).

Nikdy automaticky nepropagovat globální změnu na ostatní projekty bez explicitního pokynu. Vždy ale upozornit, které všechny další projekty jsou v rozporu s novým obecným pravidlem.

### Nerozhodovat potichu nad rámec zadání

Pokud máš nápad něco vylepšit nad rámec toho, co bylo explicitně řečeno → zeptat se, neschválit si to sám. Každá nevyžádaná změna navíc je zásah do uživatelovy domény bez jeho vědomí.

### Doc-first vývoj

V projektech, které mají v rámci repozitáře vlastní živou dokumentaci nebo specifikaci (typicky `docs/` adresář):

- Při implementaci nové funkce **nejdřív** aktualizovat dokumentaci, **teprve pak** psát kód.
- Při změně požadavku aktualizovat dokumentaci i kód **současně**, ne jen kód.
- Pokud dostaneš pokyn v rozporu s dokumentací → upozornit a zeptat se, jestli upravit dokumentaci, nebo jestli má pokyn ustoupit.

### Živá struktura

Soubory leží tam, kam **dnes patří podle smyslu**, ne tam, kde historicky vznikly. Když se ukáže, že dva soubory dělají totéž, jeden dělá dvě věci, nebo jeden patří jinam → průběžná reorganizace je **normální, očekávaná a chtěná**, ne výjimka. Aktivně ji navrhuj.

### Při odstranění nechat stopu

Když mažeš funkci / pravidlo / pole / soubor, který by se mohl jindy „vrátit" omylem (kopírováním z jiného projektu, z legacy, z dokumentace), nech stopu — sekce „Odstraněné položky" v relevantním souboru, řádek v CHANGELOGu, krátká poznámka. Ne pro každé smazání, ale pro to, kde má smysl chránit se před nechtěným návratem.
