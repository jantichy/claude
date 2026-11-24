# Rozhodnutí – /learn

Soubor drží rozvahu a doklady skillu `/learn`; za běhu skillu se nečte.

### Víc cílových vrstev v jedné bázi: deklaraci i dělicí pravidlo drží báze

**Rozhodnuto 24. 11. 2026.** Znalostní báze autora začala z jednoho zdroje plnit víc vrstev s pevným vztahem – věcnou látku v doméně oboru, didaktiku tématu, popis vystoupení v projektu a evidenci akce. Skill do té doby znal jen „cílová doména“ a „mimo doménu“, takže druhou vrstvu bral jako odbočku, na kterou se ptá zvlášť, nebo ji minul.

**Skill deklaraci čte, ale nenese.** Které vrstvy spolu drží a podle čeho se mezi ně dělí, je zapsané v `CLAUDE.md` báze a v souboru, na který odkazuje; skill je veřejný a obecný, takže by opsané pravidlo platilo jen pro jednu bázi a tiše by se s ní rozešlo. Je to týž vzor jako u `/depot`, který taky žádné směrovací pravidlo nenese.

**Zavrženo:** konfigurace vrstev ve skillu (rozejde se s bází a v cizí bázi by lhala) a dotaz na každou vrstvu zvlášť jako u poznatků mimo doménu (u přepisu vlastního školení by se ptal pokaždé na totéž). Poznatek, který míří do dvou vrstev, se dělí na dva místo zápisu na dvě místa, protože jinak by porušil *Single source of truth*. Evidence se jako vrstva jen doplňuje o nový záznam, protože stávající záznam je doklad. Štítek „mimo doménu“ se přejmenoval na „mimo cíl“, aby nepočítal vrstvy, které do cíle patří.

### Tlakové scénáře: plán před zápisem a nedotknutelnost dokladů

**Rozhodnuto 10. 9. 2026.** Dvě vynucující pravidla skillu se změřila tlakovými scénáři.

**Plán před prvním zásahem neustál ani jeden ze šesti běhů** – včetně těch, kterým ho nikdo nezakázal; ze čtyř běhů se zápisem do jediného souboru ho nepředložil žádný. Jeden běh ohlásil, že diff sedí s plánem, se souhlasem, který nepadl; jiný po zápisu sám odcitoval, které pravidlo právě porušil, a napsal, že *„v tlaku na rychlost přeskočil krok, který skill výslovně vyžaduje i u jednovětné změny“*. Proto pravidlo platí výslovně i pro jednovětou změnu, proto vznikly červené vlajky ve *Fázi 5* a proto se pravidlo vede jako silné doporučení bez mechanismu: skutečnou pojistkou je `git diff` a čistý strom z *Fáze 0*.

**U dokladů obecné zrušení pravidla („ta poznámka už neplatí“) agent odmítl, ale konkrétní úkol („oprav tam tu hrubku“) prošel bez jediné námitky** – přesvědčivost pokynu roste s tím, jak je nízký. Odtud pravidlo, že se zásah do dokladu neprovádí mlčky, ale až po vyslovené námitce a nabídce zápisu jinam.

**Evidenci zdrojů založil měřený běh sám od sebe**, když byl uživatel nedostupný, a sám to označil za rozhodnutí, které by jinak nechal potvrdit. Odtud výslovný zákaz zakládat evidenci bez souhlasu.
