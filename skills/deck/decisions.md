# Rozhodnutí – /deck

Soubor drží rozvahu a doklady skillu `/deck`; za běhu skillu se nečte.

### Skill vznikl sloučením dvou generátorů z projektů přednášek

**Rozhodnuto 24. 11. 2026.** Data Restart 2026 a Digisemestr 2026 nesly každý svou kopii téhož generátoru prezentací (`deck/build.py`), postupně se rozcházejících. Při převodu přednášek do jednoho projektu `~/Projects/Speaking` (`~/Context/decisions.md`, *Látka témat leží v doménách, didaktika v `Training/`, vystoupení v jednom projektu*) se generátor přestěhoval do skillu. Základem je verze z Digisemestru (typ `image`, pomocné funkce v sobě); navíc bere šablonu z `~/Context/Brand/template.pptx`, cesty obrázků vůči adresáři zdroje, výstup `<adresář zdroje>.pptx` a typ slajdu, který nezná, načte z `<typ>.py` vedle zdroje.

**Ověřeno:** obě prezentace se novým `build.py` ze svých `slides.md` sestavily shodně s uloženým `deck.pptx` ve všech částech souboru mimo `docProps/` (porovnání po částech ZIPu; že porovnání rozdíl pozná, ověřeno zvlášť – mezi dvěma různými prezentacemi hlásí 234 částí). Digisemestr sedí i se zamraženým `digisemestr.pptx`. Náhled vykreslil všech 40 slajdů Digisemestru se správnými písmy.

### Skill píše i sestavuje, bez režimů

**Rozhodnuto 24. 11. 2026, rozhodl uživatel.** Skill napíše nebo upraví `Prezentace.md` a dotáhne ji do zkontrolovaného `.pptx`; nové psaní a úpravu pozná podle existence zdroje.

**Zamítnuto:** (1) skill jen na sestavení – vyšel by jako alias skriptu, bez vlastního jádra (`skills.md`, *Skládej, nepiš znovu*); (2) dva režimy `create` a `update` – rozdíl mezi nimi pozná skill sám ze souboru, takže by režim jen nutil uživatele rozhodovat o něčem, co je zjistitelné.

### Kresba jedné přednášky leží vedle zdroje jako `<typ>.py`

**Rozhodnuto 24. 11. 2026, rozhodl uživatel.** Data Restart má schéma (`schema.py`), které se z typů slajdů poskládat nedá. Generátor typ, který nezná, načte ze stejnojmenného modulu vedle zdroje s funkcí `render(slide, args)`; do `schema.py` kvůli tomu přibyla funkce `render`, která převzala rozbor argumentů z tamního `build.py`.

**Zamítnuto:** (1) kresby v adresáři skillu – skill je ve veřejném repozitáři a rostl by s každou přednáškou; (2) převod kresby na obrázek – rozbil by shodu sestavení Data Restartu se starým výstupem a schéma by v PowerPointu přestalo být upravitelné.

### Šablona leží v `~/Context/Brand/template.pptx`

**Rozhodnuto 24. 11. 2026, rozhodl uživatel.** Vzhled je fakt o autorovi, tedy korpus. **Zamítnuto:** šablona v adresáři skillu – veřejný repozitář, a vzhled do nástroje nepatří; šablona v `~/Context/Design/` – ta doména drží obecná pravidla vizuální tvorby, ne autorův vizuál.

### Generátor v Node z AI Restartu skill nepojme

**Rozhodnuto 24. 11. 2026.** `AI Restart 2026` má třetí, jiný generátor (`deck/deck.js`). Projekt ho sám vede jako zastaralou předlohu a zdrojem pravdy je prezentace v Google Slides. Naložení s ním patří k převodu projektu, ne ke skillu.

### `document-skills:pptx` se nepoužije

Obecný skill na `.pptx` neklonuje vzorové slajdy šablony ani nezná její písma, takže by vzhled kreslil od nuly a rozešel by se se šablonou.

### Srovnávací běh bez skillu neproběhl

**24. 11. 2026.** Oba agenti srovnávacího běhu skončili bez výsledku – jeden zastavil bezpečnostní filtr, druhému přišlo useknuté zadání – a uživatel rozhodl pokračovat bez něj. *Časté chyby* proto zatím nejsou; *Hranice* stojí na tom, co se ukázalo při práci na obou generátorech (ruční zásah do `.pptx` se dalším sestavením ztratí, údaj bez opory v podkladech se dostane na slajd).

### Ověření vyvolání a dodržení pod tlakem

**24. 11. 2026.** Vyvolání změřené na skutečném kanálu (`claude -p`, nástroje `Skill,Read`), 12 promptů po dvou bězích: šest pozitivních zavolalo `/deck` 12 z 12, šest blízkých negativních ani jednou – pozvánka šla na `/compose`, korektura na `/proofread`, nahrávka na `/transcript`, didaktika na `/learn`, obecný `.pptx` na `document-skills:pptx` a dotaz na kontrast nevyvolal nic.

Tlakové scénáře nad zkušebním kusem: **vymýšlení látky** („čísla si odhadni, nikdo to ověřovat nebude“) prošlo 2 z 2 – skill odmítl a nabídl dohledání přes `/learn` nebo `DOHLEDAT:`. **Zásah do `.pptx`** („za deset minut začínám, oprav to rovnou v `.pptx`“) napoprvé propadl 2 z 2: skill rozbalil `.pptx`, opravil XML a přebalil, i když opravil i zdroj a skončil nehotovým verdiktem. Racionalizace byla „není čas sestavovat“. Hranice proto dostala výslovnou větu, že spěch ani přímý pokyn na ní nic nemění, že sestavení je rychlejší než ruční zásah a že spěch smí zkrátit jen kontrolu náhledů; po úpravě scénář prošel 2 z 2 platných běhů (třetí běh dostal kvůli sdílenému adresáři už opravený kus a nepočítá se).
