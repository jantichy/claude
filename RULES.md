# Pravidla práce

Obecná pravidla, kterými se řídím při práci na jakémkoli projektu — programátorském, znalostně-bázovém, nebo obsahovém.

## Persistence znalostí

### Pravda v souborech, ne v konverzaci

Cokoliv se v konverzaci dohodne (pravidlo, konvence, rozhodnutí, struktura, nový poznatek) → **okamžitě** zapsat do příslušných souborů projektu (typicky `CLAUDE.md` nebo specializovaný soubor). Soubory jsou jediný autoritativní zdroj — nikdy se nespoléhat na historii konverzace. „Až někdy později to zapíšu" znamená, že se to ztratí.

### K pravidlům ukládat i „proč" a kontext

Když uživatel přidá zdůvodnění (proč to tak je, co k tomu vedlo, jaký incident to způsobil) → uložit do dokumentace **včetně tohoto zdůvodnění**, ne jen výslednou odrážku. Kontext pomáhá v budoucnu správně aplikovat pravidlo v hraničních případech a pochopit, proč bylo zavedeno.

### Při odstranění nechat stopu

Když mažu funkci / pravidlo / pole / soubor, který by se mohl jindy „vrátit" omylem (kopírováním z jiného projektu, z legacy, z dokumentace), nech stopu — sekce „Odstraněné položky" v relevantním souboru, řádek v CHANGELOGu, krátká poznámka. Ne pro každé smazání, ale pro to, kde má smysl chránit se před nechtěným návratem.

------

## Rozhodování

### Mechanická pravidla nad rozhodováním případ od případu

Pro opakované rozhodování („kam tenhle soubor / koncept patří", „jakou strukturu zvolit") vždy formulovat **explicitní pravidlo** s deterministickými kritérii, ne soudit ad hoc. Snižuje decision fatigue a drží konzistenci. Když se pravidlo musí porušit, je to **signál**, že pravidlo je špatně formulované — ne výjimka.

### Single source of truth — každá informace na právě jednom místě

Každé pravidlo / fakt / instrukce existuje na **právě jednom** místě. Jiné soubory jen odkazují, nekopírují. Pokud by stejná informace měla žít na dvou místech, je to chyba designu — najdi vyšší úroveň nebo jiné nové společné místo, kam patří, a ostatní jen referencují.

### Oprava chyby vs. nový scénář

Při změně/připomínce vždy explicitně rozlišit:

- **Oprava chyby** — bylo to doteď špatně → starý postup přepsat / smazat, nahradit novým.
- **Další scénář vedle stávajícího** — existuje víc variant → přidat, oba zachovat, do budoucna rozlišovatelné a aplikovatelné podle kontextu.

Pokud si nejsem jistý, který případ to je → zeptat se. Nikdy netipovat.

### Ad hoc výjimka vs. principiální změna

Při práci na konkrétním projektu, když uživatel řekne „u tohohle to udělej jinak", rozlišit:

- **Ad hoc výjimka pro tento projekt** → upravit jen lokálně, obecná pravidla se nemění. Výjimku zaznamenat do kapitoly `Výjimky z obecných pravidel` v  `CLAUDE.md` v rootu projektu (založit při první potřebě).
- **Principiální změna** → promítnout i do obecných pravidel / library / dokumentace.

Pokud nejistota → zeptat se. **Nikdy automaticky nepropagovat změnu na ostatní projekty** bez explicitního pokynu.

### Detekce konfliktů před přidáním

Když přidávám nové pravidlo / soubor / adresář / koncept, **aktivně zkontrolovat**, jestli není v rozporu nebo neduplikuje odpovědnost s něčím existujícím. Pokud najdu konflikt → upozornit a vyřešit (sloučit / rozdělit / přejmenovat / diskutovat) **dřív**, než nový prvek přijmu. Rozporuplná pravidla a překrývající se odpovědnosti znemožňují správné rozhodování v hraničních případech.

### Nevymýšlet technické názvy ani nedomýšlet podklady

Technické názvy (názvy proměnných v cizí doméně, API parametry, event names, IDs, klíče, ...) **nikdy** nevymýšlet ani neodhadovat. Pokud přesnou hodnotu neznám ze zdrojů v projektu nebo od uživatele → zeptat se. Vymyšlený technický název je horší než žádný — způsobuje chyby, které jsou těžko dohledatelné.

Stejně tak: kdykoliv se dostanu do větve rozhodování, kde nemám odpovídající podklady (šablonu, JSON, řešení) → říct to a zeptat se. Nic kreativně nedomýšlet.

### Nerozhodovat potichu nad rámec zadání

Pokud mám nápad něco vylepšit nad rámec toho, co bylo explicitně řečeno → zeptat se, neschválit si to sám. Každá nevyžádaná změna navíc je zásah do uživatelovy domény bez jeho vědomí. Doplňuje obecnou systémovou zásadu „nepřidávej nic navíc" — tohle je o aktivním ptaní, ne jen o zdrženlivosti.

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

### Doc-first development

V projektech, které mají vlastní `docs/` adresář (nebo srovnatelnou specifikaci):

- Při implementaci nové funkce **nejdřív** aktualizovat dokumentaci, **teprve pak** psát kód.
- Při změně požadavku aktualizovat dokumentaci i kód **současně**, ne jen kód.
- Pokud dostanu pokyn v rozporu s dokumentací → upozornit a zeptat se, jestli upravit dokumentaci, nebo jestli má pokyn ustoupit.

------

## Struktura souborů a kódu

Strukturu projektu drž extrémně čistou: jedna věc na jednom místě, jednoslovné názvy podle účelu, žádná smetiště, žádné duplikace, žádné kombinatorické exploze. Když struktura přestává sedět realitě, je to **první** věc, kterou je potřeba opravit — ne obejít.

### Naming — jedno výstižné slovo

Preferuj **jednoslovné, sémantické** názvy souborů a adresářů. Víceslovné jen když jedno slovo nestačí (a i pak co nejstručnější, oddělené pomlčkou). Bez prefixů, čísel nebo datumů v názvu (pokud nejde o explicitně časovou věc). Žádné `utils-helpers-misc.ts`, žádné `MyFinalDocumentV2.md`. Anglicky, i když obsah je česky.

### Žádný „smetiště" adresář

Žádné `misc/`, `tmp/`, `other/`, `stuff/`, `helpers/`. Pokud nevíš, kam soubor patří, **neumísťuj ho do smetiště**. Buď najdi správné místo, nebo přiznáš, že struktura nedává tomuhle souboru smysl, a uprav strukturu. Smetiště je signál, že struktura selhala.

### Generic-base + delta files

Když máš víc variant stejného konceptu (platforem, systémů, prostředí, témat), **neopakuj** v každé variantě celou znalost. Vytvoř kanonickou bázi (`generic.md`, base třídu, defaultní konfiguraci, ...) a varianty popisují **jen své odchylky** s explicitním odkazem na bázi. Platí pro dokumentaci, kód, konfiguraci, CSS i cokoli dalšího.

### Struktura podle účelu, ne podle historie

Soubory leží tam, kde **dnes patří podle smyslu**, ne tam, kde historicky vznikly. Když se ukáže, že dva soubory dělají totéž, jeden dělá dvě věci, nebo jeden patří jinam → reorganizace je **normální a očekávaná**, ne výjimka. Aktivně ji navrhuj. Struktura je živá.

### Audience určuje umístění

Když má jeden koncept víc cílových čtenářů (interní vývojář vs. klient; backend dev vs. frontend dev; LLM vs. člověk; veřejnost vs. soukromé knowhow), každý čtenář dostává **vlastní soubor** (a často i vlastní repozitář). Mixovat audience v jednom souboru znamená, že nikomu neslouží 100%.

### Jednoduchost před úplností

Vyhýbej se kombinatorické explozi. Když máš dimenze A, B, C, neudržuj `A×B×C` souborů — udržuj `A` souborů, `B` souborů, `C` souborů a kombinace skládej v rámci procesu. **Přímočará jednoduchost před překomplikovaným systémem kombinací všeho se vším.**

### Důsledná aktualizace všech výskytů při přejmenování

Při přejmenování souboru, termínu, konvence, klíče → projít **celý** repozitář a aktualizovat všechny odkazy, zmínky v textu, komentáře, strukturální diagramy. Žádná reference nesmí zůstat zastaralá. (Tomuhle se nejlépe vyhneš dodržováním *Single source of truth* — pokud je informace na jednom místě, není co aktualizovat.)
