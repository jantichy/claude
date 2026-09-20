# Kdo o nálezu rozhoduje

Jedno kritérium pro všechny skilly, které nálezy nejen hlásí, ale i opravují. Stojí mimo ně, protože **hranice mezi „opravím sám“ a „rozhodne uživatel“ musí být napříč skilly tatáž** – jinak si týž nález v `/review` vyžádá otázku a v `/consistency` se opraví mlčky, a uživatel nemá jak odhadnout, co ho v kterém běhu čeká.

Závažnost nálezu je jiná otázka a drží ji `~/.claude/skills/SEVERITY.md`. **Stupeň neurčuje, kdo rozhoduje:** kritický nález s jedinou zjevnou opravou se opraví rovnou, nízký s dvěma obhajitelnými podobami jde k uživateli.

## Osa není „jak riskantní“, ale „je z čeho vybírat“

**Ptej se jedině tehdy, když má oprava víc obhajitelných podob a volba mezi nimi je uživatelova.** Nic jiného otázku neodůvodňuje – ani to, že zásah mění strukturu, ani že je ho hodně, ani že se ti do něj nechce.

| Skupina | Kritérium | Co s ní |
|---|---|---|
| **Mechanické** | oprava nemění chování ani strukturu: překlep, typografie, mrtvý odkaz, zastaralý počet proti jednoznačnému zdroji, pozůstatek po dokončeném přejmenování | oprav rovnou, vypiš jedním řádkem na nález |
| **Jednoznačné** | oprava chování nebo strukturu mění, ale má **právě jednu zjevně správnou podobu** – dorovnání toho, co už je rozhodnuté jinde, doplnění chybějícího kusu, jehož tvar určuje okolí | oprav rovnou, vypiš **i s tím, co se změnilo a proč** |
| **Sporné** | oprava má víc obhajitelných podob; nebo chybí údaj, který ví jen uživatel; nebo je zásah nevratný, sahá mimo repozitář či do cizího systému; nebo **si netroufáš** | zeptej se, jeden nález = jedna otázka |

**Váhání je odpověď.** Nepřemlouvej se, že nález do prvních dvou skupin „nejspíš patří“ – patří tam jen to, u čeho je to zřejmé na první pohled.

**Objem důvod k dotazu není.** Zdlouhavá, ale jednoznačná oprava se dělá, ne předkládá; naopak jednořádková změna pravidla se předkládá, i když trvá vteřinu. Rozhoduje, čí je to rozhodnutí, ne kolik je s ním práce.

## Volby v otázce jsou varianty řešení, ne „teď nebo později“

**Vyjdou-li ti volby *Opravit / Odložit / Přeskočit*, je to doklad, že nález mezi sporné nepatří.** U takové trojice je odpověď předem známá – odložit opravu, kterou umíš udělat hned, nechce nikdo, a nechat vadu vyhnít taky ne. Otázka tedy nic nerozhoduje a stojí pozornost, kterou pak uživatel nemá na otázky, kde na jeho odpovědi opravdu záleží.

**Sporný nález se proto ptá na podobu opravy:** „nese to pole API, nebo si to widget bere z vlastního kontextu?“, „loguje se to do `UserLogu`, nebo se ta mez pojmenuje?“. Volby jsou konkrétní a u každé stojí, co se stane.

**Odložit a přeskočit zůstávají**, ale jako volby vedle variant, ne místo nich – a u nálezu, který se odložit doopravdy může, protože závisí na něčem nehotovém.

## Přehled na začátku vyčísluje obojí

**Kolik se opraví rovnou a kolik doopravdy zbývá na rozhodnutí** – to druhé číslo je jediné, které uživateli říká, jak dlouhý bude interaktivní průchod. Report, který vypíše „mechanických 12, sporných 40“ a pak se u třiceti z těch čtyřiceti nemá na co ptát, to číslo nadsazuje a průchod působí dráž, než je.

## Kdo ji používá

`/review`, `/consistency`, `/attack`, `/audit` a `/cleanup` – ten u položek mimo rozsah i u nálezů čtenářů, kde platí táž hranice jako u vlastních nálezů. `/oponent` se k ní hlásí taky, i když ji dodržoval odjakživa: jeho volby jsou varianty řešení už od začátku.

**Skill si nad tímhle kritériem podává vlastní doménové čtení** – `/attack` má sporných skoro všechno, protože každý jeho nález mění chování běžící aplikace, kdežto `/consistency` má většinu jednoznačnou, protože srovnává dvě místa, z nichž jedno je zdroj. **Stavět vlastní hranici vedle téhle se ale nesmí**; přibude-li další skill, který nálezy opravuje, odkáže sem taky a **neopisuje si ji** (`~/.claude/RULES.md`, *Single source of truth*).

**Výjimka pro zadání subagentů:** text, který jde agentovi bez kontextu session, si potřebné části **opisuje celé**, protože odkaz do souboru, který nemá načtený, je mrtvý. Platí to jen na zadání, ne na tělo skillu – a u tohohle kritéria to bude potřeba zřídka, protože rozhoduje hlavní session, ne agent.

## Proč to vzniklo

**Zadal uživatel 20. 9. 2026** uprostřed `/consistency full`, po jedenácti otázkách, ze kterých ani jedna nenabízela volbu: *„když jsou ty opravy takhle jednoznačné a není se mezi čím rozhodovat (a dáváš mi stejně jen na výběr, jestli opravit hned nebo opravit později nebo se na to vykašlat a nechat to špatně), tak se mě ani neptej a hned to všechno oprav“*. Ze 37 nálezů označených za sporné jich 18 po té větě padlo bez jediné otázky.

**Chyba byla v ose, ne v pečlivosti.** Dosavadní kritérium znělo „je oprava bezriziková a nemění chování?“, což je otázka o **zásahu**. Ptát se má ale podle toho, jestli existuje **volba** – a ta dvě kritéria se rozcházejí přesně u nálezů, které něco mění a přitom je jasné jak. Těch je v dokumentačním projektu většina.
