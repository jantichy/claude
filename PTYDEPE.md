# Ptydepe

Termíny, na kterých jsme se výslovně dohodli. Řeší jedinou vadu: **beru za termín, co byl jen náhodné slovo v konverzaci**, a pak ho používám napříč projekty jako by byl zavedený.

Jméno je po umělém jazyce z Havlova *Vyrozumění*: řeč, které nikdo nerozumí, ale všichni předstírají, že ano. Spravuje ho skill `/ptydepe`.

Je to data k pravidlům *Nezaváděj neustálené termíny* a *Jeden termín pro jednu věc* v `~/.claude/RULES.md`; ta pravidla zůstávají tam, tady stojí konkrétní rozhodnutí. Doménové glosáře jednotlivých projektů (`docs/glossary.md`, viz `~/.claude/STRUCTURE.md`) tím nejsou dotčené – tady je jen to, co platí **napříč** projekty.

## Jak se používá

- **Než sáhneš po termínu, který není v oboru zavedený, hledej ho tady.** Když tu není, řekni rovnou, co jím myslíš, a navrhni ho zapsat.
- **Zapsaný termín se používá přesně v uvedeném rozsahu.** Rozšířit ho na příbuznou věc je táž vada jako zavést nový – čtenář bere jméno jako tvrzení o hranicích.
- **Když se termín změní, mění se všude naráz** (`RULES.md`, *Propagace změny*; nástroj je `/replace`), a to i v `~/Dev`, nejen v konfiguraci.
- **Starý termín tu zůstává zapsaný, a jenom tu.** Ve všech ostatních souborech se nahradí beze stopy; tady u nástupce stojí věta „nahrazuje …“ i s důvodem, aby se dalo rozhodnutí vrátit nebo aspoň dohledat, proč padlo.
- **Neptej se na týž termín podruhé.** Co je tady, je rozhodnuté.

## Termíny

### blokující kontrola

**Automatická kontrola nástrojem, která práci zastaví, dokud neprojde:** `typecheck`, `lint`, `test`, audit závislostí, hledání tajemství, mutation testing. Nula tokenů, stejný výsledek dvakrát. Kde je z kontextu jasné, o co jde, zkracuje se na prosté **„kontrola"**; přívlastek se opakuje tam, kde by hrozila záměna s kontrolou, která jen hlásí.

**Není to** posouzení modelem (`/review`) ani explorativní útok (`/attack`) – to jsou podle `~/Dev/context/coding/quality.md`, *Tři druhy záruk*, dva **jiné** druhy záruky. Není to ani ověřovatel nálezů uvnitř `/review` a nejsou to závěrečné věty skillu, i když obojí taky něco zastavuje.

**Nahrazuje dřívější „bránu"** (2026-09-07). Anglicky *quality gate* zavedený termín je, ale česká „brána" ne – čtenář si pod ní představí vrata a potřebuje k ní slovník. Zbylá „brána" v souborech je proto vždycky **platební brána** a s tímhle pojmem nemá nic společného.

**Mluvíš-li o jedné konkrétní kontrole, pojmenuj ji.** „Testy padají“ je přesnější než „kontrola je červená“ – ta věta nechává čtenáře hádat, která z nich spadla.

### specialista, panel specialistů

**Úzce nabriefovaný agent, který posuzuje jedinou věc a nic jiného nehlásí** – a *panel specialistů* je skupina takových agentů puštěná paralelně. Platí to **obecně, napříč skilly**; u konkrétního se přidává přívlastek: *specialista na bezpečnost*, *specialista na data a stavy*.

**Úzkost je celý smysl toho jména.** Proto ne „expert“ – ten slibuje hloubku a autoritu, kterou subagent s promptem nemá, kdežto na panelu záleží právě to, že každý kouká jen na jedno.

**Nahrazuje dřívější „role" a „panel rolí"** (2026-09-07). „Role“ je v konfiguraci obsazená autorizací – kdo co smí – v `~/Dev/context/coding/coding.md` i ve `web/admin.md`, takže si čtenář pod „panelem rolí“ představil oprávnění uživatelů.

**Dva skilly mají vlastní jméno a nechávají si ho**, protože nese sloveso: `/oponent` má **oponenty** (kritizují) a `/attack` **útočníky** (rozbíjejí). Obecně se o obou dál mluvit jako o specialistech smí; `/review` vlastní jméno nemá a používá jen to obecné.

### seznam, který musí přesně sedět

**Výjimka zapsaná do seznamu, který test porovnává se skutečností v obou směrech.** V seznamu nesmí chybět nic, co pravidlo porušuje, ani zůstat nic, co se už opravilo – proto opravená a nevyškrtnutá položka shodí testy stejně jako nová regrese. Bez toho by výjimka tiše přežila dokončenou migraci a přestala cokoliv měřit. Používá to `MIGRACE` v `~/.claude/tests/test_skills.py`.

**Nahrazuje dřívější „ráčnu"** (2026-09-07). Anglicky *ratchet* zavedené je, ale česká „ráčna“ ne – a metafora nesla jen půlku významu: ráčna brání couvnutí, ale nevynutí, aby se seznam škrtal. **Neříkej tomu ani „porovnání na rovnost“ nebo „zamčené na rovnost“** – to je programátorský žargon pro shodu dvou množin a čtenář z něj nepozná, co se s čím porovnává.

### README skillu

**Text pro člověka zvenčí, na který se posílá odkaz, když se skill někomu doporučuje.** Tvar drží `~/.claude/skills/SKILLS.md`, *README skillu*.

**Neříkej mu „vizitka"** (2026-09-07). „README“ je zavedené jméno přesně pro tenhle soubor a metafora nic nepřidávala – že je psaný pro člověka zvenčí, stojí v normě vedle. Česká „vizitka“ je navíc obsazená: znamená jednostránkový firemní web, a v tom významu v `~/Dev/context` dál zůstává.

### průběžná kontrola

**Mechanismus, který po každé odpovědi pouští blokující kontroly z kontraktu příkazů a nepustí ji skončit, dokud padají.** Vynucuje ho `Stop` hook, ne dobrá vůle. Stav se popisuje barvou: kontrola je zelená, nebo padá.

**Nahrazuje dřívější „zelenou linku"** (2026-09-07). „Linka“ byl nejspíš překlad *pipeline*, ale v češtině je *zelená linka* pevně obsazená bezplatným telefonním číslem podpory – kdo repozitář vidí poprvé, přečte si to takhle, protože jiný význam v jazyce není. Starý termín navíc znamenal dvě věci naráz (stav i mechanismus) a `quality.md` to musel vyvracet větou „je to stav, ne krok“.

**Anglicky je to `verify`** – `verify.sh`, `tests/test_verify.py`, vypínače `.claude/no-verify` a `CLAUDE_NO_VERIFY`. Zvoleno podle `git commit --no-verify`, kde to znamená totéž: přeskoč kontroly.

### závěrečný verdikt

**Věta, kterou musí skill povinně skončit.** Má dvě předepsaná znění a skill si mezi nimi **jen vybírá, vlastní si neformuluje**: buď je věc hotová a ověřená a řekne se, čím se dá pokračovat, nebo hotová není a jmenuje se konkrétně, co tomu brání. Mezi nimi není nic. Vzorec drží `~/.claude/skills/SKILLS.md`, *Povinné sekce a jejich pořadí*.

**Nahrazuje dřívější „koncové věty"** (2026-09-07). „Koncový“ se česky pojí s uživatelem, stanicí nebo stavem – s něčím na konci řady; věta na konci textu je závěrečná. A pojmenovat to „větami“ mířilo na formu místo na účel: skill nevydává dvě věty, ale jeden verdikt, pro který má dvě znění.

### cílený zásah

**Editace dokumentace po jednotlivých větách** místo přepsání celé sekce. Vada, kterou pojmenovává: **zásah je úzký, jeho následky nikoliv** – přejmenuje se sekce a zůstane odkaz na staré jméno, dopíše se věta o něčem, co v cílovém souboru mezitím není. Pozůstatky po nich hledá `/cleanup`, *Fáze 6*.

**Nahrazuje dřívější „chirurgický zásah"** (2026-09-07). Anglicky je *surgical edit* běžný obrat, ale doslovný překlad mate – „chirurgický zásah“ je česky operace, tedy obraz o řezání, ne o přesnosti. Čeština má pro *surgical strike* ustálené „cílený úder“, takže „cílený“ nese v téhle vazbě přesně tu úzkost, o kterou jde.

**Ne „zacílený“** – to je příčestí od „zacílit“ a v marketingu navíc obsazené významem targeting. **Ne „cílená změna“** – „změna“ je v `~/.claude/RULES.md` obsazená (*Rozlišuj typ změny*, *Propagace změny*), a právě to druhé pravidlo se cíleným zásahem porušuje.

### čtenář bez kontextu

**Subagent, který nemá žádný kontext z běžící session a čte výhradně soubory.** Ptá se, jestli se z toho, co je zapsané, dá pochopit, co se rozhodlo a proč – nebo jestli to dává smysl jen tomu, kdo u toho byl. Pouští ho `/cleanup`, *Fáze 6*, až po zápisu.

**Nahrazuje dřívější „fresh-reader"** (2026-09-07). Anglicismus uprostřed české věty, který se navíc skloňoval po česku („fresh-readera“, „2 fresh-readeři“), a prolézal i do `done.md`, tedy do textu pro člověka.

**Ne „nezávislý čtenář“** – tak se popisuje `/oponent` a splynuly by dvě různé věci: oponent posuzuje obsah dokumentu, tenhle čtenář srozumitelnost zápisu. **Ne „nezaujatý čtenář“** – zaujatost s tím nemá co dělat, rozhoduje, že u toho nebyl.

### hlavní scénář

**Průchod aplikací, ve kterém uživatel dělá všechno správně a nic neselže.** `/attack` hledá právě mimo něj, `/release` ho po nasazení projde celý jako smoke test. Zdrojem je první scénář v `docs/requirements.md` nebo `docs/scenarios.md`.

**Nahrazuje dřívější „šťastnou cestu"** (2026-09-07) v popisu `/attack`. Anglicky je *happy path* zavedený pojem, ale doslovný český překlad se nepoužívá – a hlavně **„hlavní scénář“ už byl zavedený na pěti jiných místech** (`STRUCTURE.md`, `/specify`, `/release`). Byla to tedy dvě jména pro jednu věc, jen každé v jiném skillu.

### hledisko

**Jeden kritický pohled, se kterým `/oponent` pouští jednoho paralelního agenta** – *Co chybí*, *Předpoklady a argumentace*, *Pre-mortem* a dalších čtrnáct v katalogu skillu.

**Nahrazuje dřívější „úhel"** (2026-09-07). „Úhel pohledu“ je česky správně, ale samotný počitatelný „úhel“ („vyber pět úhlů“) nutí čtenáře doplnit si umazané slovo. „Hledisko“ znamená totéž jedním slovem a skloňuje se bez berličky. Pozor na rod: „úhel“ je mužský, „hledisko“ střední, takže se mění i shoda („nevybraný úhel“ → „nevybrané hledisko“).

**`/attack` se s tím nesjednocuje:** má **vektory útoku**, protože vektor není pohled, ale způsob, jak něco rozbít – a je to navíc zavedený bezpečnostní termín. `/review` naopak od 7. 9. 2026 mluví o [specialistech](#specialista), ne o „rolích“; hledisko je to, co specialista dostane přidělené.

### nevypořádané téma

**Co v konverzaci padlo a nikdy se nedořešilo** – otázka bez odpovědi, návrh, který nikdo nepřijal ani nezamítl, nebo vícebodová odpověď vyřízená jen zčásti. Nikdo to nezavrhl ani neschválil. Hledá je `/cleanup`, *Fáze 2*.

**Nahrazuje dřívější „zamluvené téma"** (2026-09-07). „Zamluvit“ znamená česky vědomě odvést řeč jinam, takže termín podsouval úmysl, který tam není – téma jen propadlo. A „zamluvit si“ navíc znamená rezervovat, takže se to při rychlém čtení dá číst jako téma, které si někdo zabral. „Vypořádat“ je přitom zavedené sloveso téhle konfigurace (vypořádané nálezy).

### odpověď

**Jedna výměna od uživatelovy zprávy po poslední řádek, který Claude napíše** – včetně všech nástrojů, které mezitím zavolá. Je to jednotka, na jejímž konci se spouští `Stop` hook, tedy [průběžná kontrola](#průběžná-kontrola).

**Nahrazuje dřívější „tah"** (2026-09-07). Anglicky je *turn* zavedený pojem, česky „tah“ ne – znamená šachový tah, marketingový tah nebo tah štětcem. Bylo to zákeřnější než ostatní vymyšlené termíny: čtenář slovu rozuměl, jen si pod ním představil něco jiného.

**Ne „krok“** – ten je obsazený kroky životního cyklu a kroky `/project`. **Ne „kolo“** – vystihuje střídání, ale česky znamená hlavně kolo soutěže a věta „hook nepustí ukončit kolo“ nic neřekne.

### ověřovací pokus

**Krátký kód napsaný jen proto, aby zodpověděl otázku v návrhu** („zvládne to hosting?“, „má to API tenhle endpoint?“) – a pak se **zahodí**. Jediná výjimka ze zákazu implementace v `/specify`.

**Nahrazuje dřívější „sondu"** (2026-09-07). Anglicky je *spike* zavedený agilní termín, česky „sonda“ ne – znamená kosmickou sondu nebo lékařský nástroj. **Ne „spike“ v próze**: jako jméno cizí kategorie v tabulce `/specify` zůstává, ale skloňovat „nabídni spike“ nebo „ze spiku vyšlo“ česky nejde.

**Nesmí se plést s [kontrolou závislostí](#kontrola-závislostí)** – donedávna se obojí jmenovalo „sonda“. Tohle je experiment, který se vyhodí; ta druhá je ověření prostředí, které běží pokaždé.

### kontrola závislostí

**Ověření na začátku běhu, že nástroj, na který se bude delegovat, opravdu existuje a dá se zavolat.** Chybí-li, skill neselže: řekne nahlas, co tím odpadá, a pokračuje bez toho. `/skill`, *Fáze 0*.

**Nahrazuje dřívější „sondu na závislosti"** (2026-09-07) – viz [ověřovací pokus](#ověřovací-pokus), pod nímž se to jméno pletlo s něčím úplně jiným.

### pozůstatek

**Zbytek po zásahu do textu, který přestal platit.** Dvě situace: odkaz zůstal na sekci, která se mezitím přejmenovala, nebo věta tvrdí něco, co v cílovém souboru už není. Hledá je `/cleanup` po každé session, `/consistency` u staršího dluhu.

**Nahrazuje dřívější „viséc" / „viséci" / „viséce"** (2026-09-07). To slovo v češtině neexistuje – vzniklo z „zůstalo to viset" a začalo se skloňovat. Sloveso je v pořádku, podstatné jméno byl výmysl.

**Nejsou to nedodělané konce.** Ta práce je dodělaná, jen ji rozbil zásah jinde – proto „loose ends“ ani „nedotažené konce“ nesedí.

### vata

**Text, který nic nepřidává:** hodnotící adjektiva („úžasný“, „skvělý“), zdvořilostní obraty, motivační moudra, úvod o tom, že autor chce něco sdělit. Termín i katalog konkrétních případů drží `~/Dev/context/text/text.md`, *Vata a zakázané obraty*.

**Neříkej tomu „voda"** (2026-09-07). V češtině to zavedené není – je to nejspíš kalk z ruského *вода*. „Vata“ je zavedená a stojí v redakčním standardu jako název sekce, takže druhé jméno pro tutéž věc jen tříští termín.
