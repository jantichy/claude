# Rozhodnutí – /legal

Soubor drží rozvahu a doklady skillu `/legal`; za běhu skillu se nečte.

### Samostatný skill, ne blok v `/oponent`

**Rozhodnuto 15. 11. 2026.** Smlouva potřebuje věci, které oponentura nemá a mít nemá: určenou stranu, rozhodné právo a den, výstup do Wordu pod jménem uživatele, koncept mailu, kola protinávrhu a interní pracovní soubor, který nesmí ven. Blok v `/oponent` by tohle všechno nesl jako výjimku z obecného posudku. Společná je jen mechanika panelu a ověřování, a ta se proto vytáhla do sdíleného `skills/panel.md`. Chování `/oponent` se tím nemělo změnit.

### Úzký panel, ne jeden široký posudek

**Rozhodnuto 18. 11. 2026, předběžně.** Uživatel rozhodl skill sepsat po dvou ze tří plánovaných měření a třetím ho potvrdit nebo upravit. Každé měření byl dvojí běh nad toutéž smlouvou: jeden agent bez skillu proti panelu šesti hledisek.

- **Měření 1 – cizí NDA se smlouvou o zpracování, zahraniční protistrana, cizí právo.** Jeden agent asi 225 tisíc tokenů a 17 minut, pokryl skoro všechny body skutečného jednání. Ve třech bodech ale sám zmírnil vyjednávací linii uživatele místo otázky, neměl pohled protistrany a nikdo ho neověřoval. Panel asi 500 tisíc tokenů: advokát protistrany předpověděl dva skutečné tahy protistrany, *Co chybí*, *Dodržitelnost*, *Osobní údaje* a *Mezinárodní prvek* přinesly nové skutečné nálezy. *Odpovědnost a sankce* se se širokým posudkem skoro celé překrylo.
- **Měření 2 – vlastní návrh smlouvy se spotřebitelem, české právo, s projektovým `decisions.md`.** Jeden agent asi 236 tisíc tokenů a 13 minut, osm změn a závěr „zásadní vadu jsem nenašel“. Přehlédl neplatnost výpovědi bez poučení, podle zastaralé kopie `decisions.md` vložil do Wordu blok, který autor vědomě vyškrtl, revize podepsal „Claude“ a zapisoval mimo zadaný adresář. Panel asi 856 tisíc tokenů: 3 kritické a kolem 17 středních nálezů, 5 z nich se kryje se srovnávacím během. *Co chybí* a *Trvání a ukončení* našly nezávisle totéž kritické místo. Jeden falešný poplach vznikl ze zastaralé kopie kontextu a ověřovatel nad aktuálním souborem by ho vyvrátil.

**Co z toho plyne:** síla jednoho agenta stojí na doménových mantinelech. U NDA je měl a pokryl skoro vše, u druhé smlouvy žádné neměl a minul většinu. Úzká hlediska přidala nálezy v obou měřeních, nejvíc tam, kde doména chybí. Odtud tři pravidla skillu: kontext se čte z disku v okamžiku běhu, autora revizí určuje rámec a ústupek je vždycky rozhodnutí uživatele.

**Zatím zamítnuto:** jeden hlavní široký posudek (domény, mantinely, Word, mail) a k němu úzká hlediska jen tam, kde je široký slepý. Vyšel by levněji, ale skill by nesl dva mechanismy. **Třetí měření** na další smlouvě rozhodne, jestli se k té variantě vrátit.

### Ověřený seznam v pracovním souboru, ne v `.claude/run/`

**Rozhodnuto 18. 11. 2026.** Smlouva často leží mimo projekt (v `~/Documents`, v klientské složce bez gitu), kde `.claude/run/` nemá kam patřit. Pracovní soubor vedle dokumentu vzniká stejně, je trvalý a nese stav nálezů i rozhodnutí, takže přerušený průchod naváže z něj. Na rozdíl od běhového souboru se nemaže: rozhodnutí o smlouvě je trvalý záznam, ke kterému se vrací příští kolo.

### Ověřovatel pramene na `Explore`, čte rourou

**Rozhodnuto 15. 11. 2026, způsob čtení 18. 11. 2026.** `researcher` dostane přes svůj webový nástroj stránku prohnanou modelem a doslovnou citaci zkrácenou nebo přeformulovanou (`~/Context/Legal/legal.md`). Doslovné znění dá jen `curl`, tedy agent se shellem. `Explore` ale nesmí zakládat soubory ani v `/tmp`, kdežto postup v doméně stahuje PDF do souboru. Ověřeno 18. 11. 2026, že `pdftotext - -` čte PDF ze standardního vstupu, takže ověřovatel čte všechno rourou a soubor nepotřebuje. `general-purpose` se zamítl, protože by měl `Edit` a `Write` nad posuzovanou smlouvou.

### Odeslání je tvrdá stopka

**Rozhodnuto 18. 11. 2026 po tlakovém scénáři.** Věta „nic neodesílá“ nestačila: na pokyn „pošli ten mail rovnou protistraně“ agent dohledal adresu v Gmailu, založil koncept a nabídl odeslání jako doporučenou volbu. Opřel se o přednost pokynu uživatele před skillem. Odeslaný návrh smlouvy nejde vzít zpátky a záměna přílohy za pracovní soubor by protistraně prozradila meze i ústupky, a proto platí stejná stopka jako u faktur v `/invoicing`. Po opravě týž scénář prošel. Ostatní tři scénáře (kompromisy za uživatele, výtah místo cesty, přeskočení ověření) prošly napoprvé a doplnily jen mezery: hromadnou otázku na vyjednávací linii, zúžené čtení velkého souboru odkazem a zúžení ověření místo vypnutí.

### Vyvolání

**Změřeno 18. 11. 2026** přes `claude -p` s nástroji `Skill,Read`, dva běhy na prompt: 6 pozitivních promptů se vyvolalo 12/12, 6 sousedních (oponentura, korektura, zařazení souboru, faktury, obecný právní dotaz, článek o NDA) 12/12 nevyvolalo `/legal` a každý padl na svého souseda. `description` se proto neladil.

### Co se vědomě nepokrylo

- **Režim `counter` a doslovný `/legal` se při založení neměřily.** Viz `docs/todo.md` repozitáře.
- **Doslovné znění jen pro české právo a právo EU.** U jiného rozhodného práva neexistuje v doméně ověřená cesta k primárnímu zdroji, a proto se takový nález vrací jako neověřený a počítá se mezi důvody pro advokáta.
