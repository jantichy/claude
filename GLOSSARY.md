# Glosář

Termíny, na kterých jsme se výslovně dohodli. Řeší jedinou vadu: **beru za termín, co byl jen náhodné slovo v konverzaci**, a pak ho používám napříč projekty jako by byl zavedený.

Je to data k pravidlům *Nezaváděj neustálené termíny* a *Jeden termín pro jednu věc* v `~/.claude/RULES.md`; ta pravidla zůstávají tam, tady stojí konkrétní rozhodnutí. Doménové glosáře jednotlivých projektů (`docs/glossary.md`, viz `~/.claude/STRUCTURE.md`) tím nejsou dotčené – tady je jen to, co platí **napříč** projekty.

## Jak se používá

- **Než sáhneš po termínu, který není v oboru zavedený, hledej ho tady.** Když tu není, řekni rovnou, co jím myslíš, a navrhni ho zapsat.
- **Zapsaný termín se používá přesně v uvedeném rozsahu.** Rozšířit ho na příbuznou věc je táž vada jako zavést nový – čtenář bere jméno jako tvrzení o hranicích.
- **Když se termín změní, mění se všude naráz** (`RULES.md`, *Propagace změny*; nástroj je `/replace`), a to i v `~/Dev`, nejen v konfiguraci.
- **Neptej se na týž termín podruhé.** Co je tady, je rozhodnuté.

## Termíny

### brána

**Používej – ale jen v tomhle rozsahu.** Deterministická kontrola nástrojem, která práci zastaví, dokud neprojde: `typecheck`, `lint`, `test`, audit, gitleaks, mutation testing. Nula tokenů, stejný výsledek dvakrát.

**Není to** posouzení modelem (`/review`) ani explorativní útok (`/attack`) – to jsou podle `~/Dev/context/coding/quality.md`, *Tři druhy záruk*, dva **jiné** druhy záruky, ne brány. Není to ani ověřovatel nálezů uvnitř `/review` a nejsou to koncové věty skillu, i když obojí taky něco zastavuje.

**Původ:** termín je Honzův, z `~/Dev/context/coding/quality.md` (*Ověřování a brány kvality*). Sporné nebylo slovo, ale to, že jsem ho rozšiřoval na cokoliv, co brzdí.

**Mluvíš-li o jedné konkrétní bráně, pojmenuj ji.** „Testy padají“ je přesnější než „brána je červená“ – ta věta nechává čtenáře hádat, která ze tří vrstev spadla.
