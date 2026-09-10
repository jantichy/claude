# Ptydepe

Termíny, na kterých jsme se výslovně dohodli. Řeší jedinou vadu: **beru za termín, co byl jen náhodné slovo v konverzaci**, a pak ho používám napříč projekty, jako by bylo zavedené. Jméno je po umělém jazyce z Havlova *Vyrozumění*: řeč, které nikdo nerozumí, ale všichni předstírají, že ano.

Je to data k pravidlům *Nezaváděj neustálené termíny* a *Jeden termín pro jednu věc* v `~/.claude/RULES.md`. Doménové glosáře projektů (`docs/glossary.md`) tím nejsou dotčené – tady je jen to, co platí **napříč** projekty.

## Jak se používá

- **Levý sloupec se nepoužívá, pravý ano** – v odpovědi, v dokumentaci, v kódu i v řeči o něm.
- **Termín platí přesně v uvedeném rozsahu.** Rozšířit ho na příbuznou věc je táž vada jako zavést nový.
- **Chystáš-li se použít termín, který v oboru zavedený není a není ani tady**, řekni rovnou, co jím myslíš, a navrhni ho zapsat.
- **Neptej se na týž termín podruhé.** Co je tady, je rozhodnuté.

**Proč tenhle soubor neobsahuje důvody:** importuje se do každé session, takže by rostl v kontextu s každým dalším termínem. Úvahy, zamítnuté varianty, historii náhrad i rozhodnutí, že se termín **ponechává**, drží `~/.claude/skills/ptydepe/terms.md`, který se neimportuje nikam a čte ho `/ptydepe`. Sáhni tam, když se rozhoduje o termínu samotném – ne když ho jen používáš.

## Termíny

| Nepoužívej | Používej | Rozsah a meze |
|---|---|---|
| baseline (stav, se kterým se srovnává) | konvence projektu | co je v projektu dohodnuto – `rules.md`, glosář, sekce `CLAUDE.md`; čte to `/consistency` |
| baseline (běh bez skillu) | srovnávací běh | spuštění agenta na úkol dřív, než se skill napíše, aby bylo vidět, jak selže |
| brána | blokující kontrola | automatická kontrola nástrojem, která práci zastaví; kde je to jasné, stačí „kontrola“. **Platební brána** tím dotčená není |
| debrief | řízený rozhovor | vytažení zadání z uživatele otázku po otázce (`/specify`, `/skill`) |
| drift | rozejití | dvě místa, která spolu mají držet, se tiše rozešla. Jednotlivý nález je **odchylka**. Anglická jména konkrétních vad (*lockfile drift*) zůstávají |
| explorer | průzkumník | agent, který u velkého rozsahu zmapuje, co se kde mění, a předá mapu specialistům |
| fan-out | rozeslání práce agentům | puštění několika agentů paralelně na jeden úkol; deleguje se kvůli kontextu, ne kvůli úspoře |
| fresh-reader | čtenář bez kontextu | subagent, který nezná session a čte jen soubory. **Ne** „nezávislý čtenář“ (tak se popisuje `/oponent`) ani „nezaujatý“ |
| chirurgický zásah | cílený zásah | editace dokumentace po jednotlivých větách. **Ne** „zacílený“, **ne** „cílená změna“ |
| koncové věty | závěrečný verdikt | povinná závěrečná věta skillu – hotovo a čím pokračovat, nebo co tomu brání |
| pre-flight | příprava | `Fáze 0` každého skillu. Soubor se dál jmenuje `PREFLIGHT.md` |
| próza (proti struktuře) | souvislý text | nestrukturovaný zápis tam, kde se čeká tabulka, seznam, kritérium |
| próza (proti identifikátoru) | běžný text | česká věta tam, kde stojí proti jménu režimu, klíči, poli. **Ne** „volný text“ |
| ráčna | seznam, který musí přesně sedět | výjimka v seznamu, který test porovnává se skutečností v obou směrech |
| role, panel rolí | specialista, panel specialistů | úzce nabriefovaný agent posuzující jedinou věc. `/oponent` má **oponenty**, `/attack` **útočníky** – ta jména si nechávají |
| skeptik | ověřovatel | agent, jehož jediný úkol je nález vyvrátit. **Výjimka:** *Skeptik* je jméno zrušeného hlediska `/oponent` |
| sonda (experiment) | ověřovací pokus | kód napsaný jen kvůli zodpovězení otázky v návrhu, pak se zahodí |
| sonda na závislosti | kontrola závislostí | ověření na začátku běhu, že nástroj, na který se deleguje, existuje |
| stub | rozcestník | tenký `CLAUDE.md` v kořeni worktree kontejneru. **Ne** „ukazatel“ |
| šťastná cesta | hlavní scénář | průchod, kde uživatel dělá všechno správně a nic neselže |
| tabulka švů | tabulka delegací | inventura v `/skill`: u každého kroku odpověď „umí to už něco?“ |
| tah | odpověď | jedna výměna od uživatelovy zprávy po poslední řádek Clauda. **Ne** „krok“, **ne** „kolo“ |
| úhel | hledisko | jeden kritický pohled, se kterým `/oponent` pouští agenta. `/attack` má **vektory útoku** a nesjednocuje se |
| viséc, viséci | pozůstatek | zbytek po zásahu do textu, který přestal platit – odkaz na přejmenovanou sekci, věta o něčem, co už není |
| vizitka | README skillu | text pro člověka zvenčí. „Vizitka“ dál znamená jednostránkový firemní web |
| voda | vata | text, který nic nepřidává. Katalog drží `~/Dev/context/text/text.md` |
| zamluvené téma | nevypořádané téma | co v konverzaci padlo a nikdy se nedořešilo; hledá je `/cleanup` |
| zelená linka | průběžná kontrola | mechanismus, který po každé odpovědi pouští blokující kontroly. Anglicky `verify` |
