# Glosář

Termíny, na kterých jsme se výslovně dohodli. Řeší jedinou vadu: **beru za termín, co byl jen náhodné slovo v konverzaci**, a pak ho používám napříč projekty jako by byl zavedený.

Je to data k pravidlům *Nezaváděj neustálené termíny* a *Jeden termín pro jednu věc* v `~/.claude/RULES.md`; ta pravidla zůstávají tam, tady stojí konkrétní rozhodnutí. Doménové glosáře jednotlivých projektů (`docs/glossary.md`, viz `~/.claude/STRUCTURE.md`) tím nejsou dotčené – tady je jen to, co platí **napříč** projekty.

## Jak se používá

- **Než sáhneš po termínu, který není v oboru zavedený, hledej ho tady.** Když tu není, řekni rovnou, co jím myslíš, a navrhni ho zapsat.
- **Zapsaný termín se používá přesně v uvedeném rozsahu.** Rozšířit ho na příbuznou věc je táž vada jako zavést nový – čtenář bere jméno jako tvrzení o hranicích.
- **Když se termín změní, mění se všude naráz** (`RULES.md`, *Propagace změny*; nástroj je `/replace`), a to i v `~/Dev`, nejen v konfiguraci.
- **Neptej se na týž termín podruhé.** Co je tady, je rozhodnuté.

## Termíny

### blokující kontrola

**Automatická kontrola nástrojem, která práci zastaví, dokud neprojde:** `typecheck`, `lint`, `test`, audit závislostí, hledání tajemství, mutation testing. Nula tokenů, stejný výsledek dvakrát. Kde je z kontextu jasné, o co jde, zkracuje se na prosté **„kontrola"**; přívlastek se opakuje tam, kde by hrozila záměna s kontrolou, která jen hlásí.

**Není to** posouzení modelem (`/review`) ani explorativní útok (`/attack`) – to jsou podle `~/Dev/context/coding/quality.md`, *Tři druhy záruk*, dva **jiné** druhy záruky. Není to ani ověřovatel nálezů uvnitř `/review` a nejsou to koncové věty skillu, i když obojí taky něco zastavuje.

**Nahrazuje dřívější „bránu"** (2026-09-07). Anglicky *quality gate* zavedený termín je, ale česká „brána" ne – čtenář si pod ní představí vrata a potřebuje k ní slovník. Zbylá „brána" v souborech je proto vždycky **platební brána** a s tímhle pojmem nemá nic společného.

**Mluvíš-li o jedné konkrétní kontrole, pojmenuj ji.** „Testy padají“ je přesnější než „kontrola je červená“ – ta věta nechává čtenáře hádat, která z nich spadla.

### pozůstatek

**Zbytek po zásahu do textu, který přestal platit.** Dvě situace: odkaz zůstal na sekci, která se mezitím přejmenovala, nebo věta tvrdí něco, co v cílovém souboru už není. Hledá je `/cleanup` po každé session, `/consistency` u staršího dluhu.

**Nahrazuje dřívější „viséc" / „viséci" / „viséce"** (2026-09-07). To slovo v češtině neexistuje – vzniklo z „zůstalo to viset" a začalo se skloňovat. Sloveso je v pořádku, podstatné jméno byl výmysl.

**Nejsou to nedodělané konce.** Ta práce je dodělaná, jen ji rozbil zásah jinde – proto „loose ends“ ani „nedotažené konce“ nesedí.
