# Glosář

Termíny, na kterých jsme se výslovně dohodli. Řeší jedinou vadu: **beru za termín, co byl jen náhodné slovo v konverzaci**, a pak ho používám napříč projekty jako by byl zavedený.

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

### seznam, který musí přesně sedět

**Výjimka zapsaná do seznamu, který test porovnává se skutečností v obou směrech.** V seznamu nesmí chybět nic, co pravidlo porušuje, ani zůstat nic, co se už opravilo – proto opravená a nevyškrtnutá položka shodí testy stejně jako nová regrese. Bez toho by výjimka tiše přežila dokončenou migraci a přestala cokoliv měřit. Používá to `MIGRACE` v `~/.claude/tests/test_skills.py`.

**Nahrazuje dřívější „ráčnu"** (2026-09-07). Anglicky *ratchet* zavedené je, ale česká „ráčna“ ne – a metafora nesla jen půlku významu: ráčna brání couvnutí, ale nevynutí, aby se seznam škrtal. **Neříkej tomu ani „porovnání na rovnost“ nebo „zamčené na rovnost“** – to je programátorský žargon pro shodu dvou množin a čtenář z něj nepozná, co se s čím porovnává.

### README skillu

**Text pro člověka zvenčí, na který se posílá odkaz, když se skill někomu doporučuje.** Tvar drží `~/.claude/skills/SKILLS.md`, *README skillu*.

**Neříkej mu „vizitka"** (2026-09-07). „README“ je zavedené jméno přesně pro tenhle soubor a metafora nic nepřidávala – že je psaný pro člověka zvenčí, stojí v normě vedle. Česká „vizitka“ je navíc obsazená: znamená jednostránkový firemní web, a v tom významu v `~/Dev/context` dál zůstává.

### průběžná kontrola

**Mechanismus, který po každém tahu pouští blokující kontroly z kontraktu příkazů a nepustí tah skončit, dokud padají.** Vynucuje ho `Stop` hook, ne dobrá vůle. Stav se popisuje barvou: kontrola je zelená, nebo padá.

**Nahrazuje dřívější „zelenou linku"** (2026-09-07). „Linka“ byl nejspíš překlad *pipeline*, ale v češtině je *zelená linka* pevně obsazená bezplatným telefonním číslem podpory – kdo repozitář vidí poprvé, přečte si to takhle, protože jiný význam v jazyce není. Starý termín navíc znamenal dvě věci naráz (stav i mechanismus) a `quality.md` to musel vyvracet větou „je to stav, ne krok“.

**Anglicky je to `verify`** – `verify.sh`, `tests/test_verify.py`, vypínače `.claude/no-verify` a `CLAUDE_NO_VERIFY`. Zvoleno podle `git commit --no-verify`, kde to znamená totéž: přeskoč kontroly.

### závěrečné věty

**Dvě věty, kterými musí skill povinně skončit** – jedna říká, že věc je hotová a ověřená a čím se dá pokračovat, druhá že hotová není a co konkrétně tomu brání. Mezi nimi není nic; vzorec drží `~/.claude/skills/SKILLS.md`, *Povinné sekce a jejich pořadí*.

**Nahrazuje dřívější „koncové věty"** (2026-09-07). „Koncový“ se česky pojí s uživatelem, stanicí nebo stavem – s něčím na konci řady. Věta na konci textu je závěrečná, a stojí navíc v sekci `Fáze N – Závěr`.

**Neříkej tomu „verdikt“.** Vystihovalo by to účel, ale svádělo by k tomu, že si znění smí skill formulovat volně – a to je právě ta volnost, kterou pravidlo zakazuje.

### hledisko

**Jeden kritický pohled, se kterým `/oponent` pouští jednoho paralelního agenta** – *Co chybí*, *Předpoklady a argumentace*, *Pre-mortem* a dalších čtrnáct v katalogu skillu.

**Nahrazuje dřívější „úhel"** (2026-09-07). „Úhel pohledu“ je česky správně, ale samotný počitatelný „úhel“ („vyber pět úhlů“) nutí čtenáře doplnit si umazané slovo. „Hledisko“ znamená totéž jedním slovem a skloňuje se bez berličky. Pozor na rod: „úhel“ je mužský, „hledisko“ střední, takže se mění i shoda („nevybraný úhel“ → „nevybrané hledisko“).

**Obdoba u sousedních skillů se ale nesjednocuje:** `/attack` má **vektory útoku** a `/review` **role**. Je to strukturně totéž – jedno zadání na jednoho agenta –, ale věcně tři různé věci, a *vektor útoku* je navíc zavedený bezpečnostní termín.

### pozůstatek

**Zbytek po zásahu do textu, který přestal platit.** Dvě situace: odkaz zůstal na sekci, která se mezitím přejmenovala, nebo věta tvrdí něco, co v cílovém souboru už není. Hledá je `/cleanup` po každé session, `/consistency` u staršího dluhu.

**Nahrazuje dřívější „viséc" / „viséci" / „viséce"** (2026-09-07). To slovo v češtině neexistuje – vzniklo z „zůstalo to viset" a začalo se skloňovat. Sloveso je v pořádku, podstatné jméno byl výmysl.

**Nejsou to nedodělané konce.** Ta práce je dodělaná, jen ji rozbil zásah jinde – proto „loose ends“ ani „nedotažené konce“ nesedí.

### vata

**Text, který nic nepřidává:** hodnotící adjektiva („úžasný“, „skvělý“), zdvořilostní obraty, motivační moudra, úvod o tom, že autor chce něco sdělit. Termín i katalog konkrétních případů drží `~/Dev/context/text/text.md`, *Vata a zakázané obraty*.

**Neříkej tomu „voda"** (2026-09-07). V češtině to zavedené není – je to nejspíš kalk z ruského *вода*. „Vata“ je zavedená a stojí v redakčním standardu jako název sekce, takže druhé jméno pro tutéž věc jen tříští termín.
