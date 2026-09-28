---
name: consolidate
description: Skill se použije, když uživatel zadá "/consolidate" (volitelně s oblastí), nebo chce prověřit, jestli se v návrhu nenahromadil dluh z postupného záplatování – jestli by se to při dnešní znalosti všech případů navrhlo jinak a jednodušeji. Čte historii rozhodnutí (decisions.md, done.md, git log), hledá shluky záplat kolem jedné věci, navrhne alternativu a nechá ji zkusit vyvrátit. Na rozdíl od /review, který měří kód proti specifikaci, a /consistency, který hledá rozejití dvou míst, se ptá, jestli je dobře sama specifikace; na rozdíl od /oponent neposuzuje dnešní text, ale to, jak vznikal. Relativizuje řešení, nikdy zadání – rozsah funkcí ani obchodní pravidlo pro něj nejsou materiál. Nic neimplementuje a "nic velkého k přepsání" je jeho platný výsledek.
argument-hint: [oblast]
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion]
---

# Consolidate

## Co skill dělá

Hledá **návrhový dluh z postupného záplatování**. Návrh se vede po kolech, v každém se ukáže další kombinace a přidá se na ni sloupec nebo hodnota výčtu. Každý krok byl ve své chvíli správný, ale dohromady z nich vzniklo řešení, které by při znalosti všech případů předem šlo nahradit jedním jednodušším.

Ptá se **„bylo by to dnes navržené jinak?"** – ne „je to špatně?". Odpověď „ano" tedy vadu neznamená, a proto tahle otázka propadne každým jiným sítem.

**Jako jediný krok cyklu čte historii, ne dnešní stav.** Vstupem není `architecture.md`, ale `decisions.md`, `done.md`, git log a umlčené nálezy v `CLAUDE.md`. Shluk záplat se pozná z dat jejich narození.

V *Životním cyklu projektu* (`~/.claude/RULES.md`) je to kontrolní krok, ne bod na ose: **stojí v mezeře před `/breakdownem`**, u velkého celku povinně. Nečeká na pozici, ale na to, až se v projektu nasbírá dost kol návrhu – a v prvním průchodu se přeskakuje úplně, protože po prvním návrhu žádný dluh z lepení neexistuje.

Režimy nemá. Argument je **výchozí bod**, ne hranice – viz *Rozsah*.

## Co skill nedělá

Je to **kontrolní krok, ne bod na ose**: stojí v mezeře před `/breakdown` a nezvětšuje rozsah práce. Čí práci nepřebírá:

- **Neměří kód proti specifikaci.** To je `/review` – a na tenhle dluh je slepý z principu, protože dluh je v samotné specifikaci a kód ji plní poslušně.
- **Nehledá rozejití dvou míst.** To je `/consistency`. Tenhle dluh je **dokonale konzistentní**: čím poctivěji se záplata zanesla do všech dokumentů, tím je neviditelnější.
- **Neposuzuje dokument, jak stojí dnes.** To je `/oponent`. Ten nemá odkud vědět, že tři sousední mechanismy vznikly ve třech týdnech ze tří podnětů – v textu stojí vedle sebe jako rovnocenné.
- **Nerozpadá práci na úkoly.** Přijatý návrh předá `/breakdown`, který stojí za ním.
- **Nic neimplementuje ani nepřepisuje návrhové dokumenty.** Vrací návrh a cenu přepisu; přepis je samostatná práce, o které rozhodne uživatel.

## Jak je to postavené uvnitř

| Krok | Kdo | Proč zrovna on |
|---|---|---|
| Kronika rozhodnutí | `Explore` | potřebuje `git log -S` a `git blame`, tedy shell |
| Inventura mechanismů | `reader` | úsudek nad hotovým textem, do kterého nemá sáhnout |
| Zkušební sada situací | `reader` | totéž, jen z druhé strany |
| Shluky a návrh alternativy | **vlastní** | jádro skillu, nedeleguje se |
| Ověření s úkolem vyvrátit | `reader` | izolace kontextu je tu funkce: kdo návrh napsal, ten ho nevyvrátí |
| Průchod s uživatelem a zápis | **vlastní** | rozhoduje uživatel |

**Rozdělení na tři sběrače a počet ověřovatelů je implementační detail** – vyměnit se smí kdykoliv a u malé oblasti stačí sběrači dva. **Závazné je rozhraní:** zpětná zkouška je blokující, ověřovatel dostane úkol vyvrátit, a návrh, který zkouškou neprojde, se uživateli vůbec nepředloží.

Zadání pro agenty drží `agents.md` v adresáři skillu.

## Rozsah

**Rozsah vymezuje vstup, ne výstup.** `/consolidate gateway` znamená „vyjdi ze záplat kolem platební brány", ne „výsledek se smí týkat jen polí s tím prefixem".

Je to celý smysl toho rozlišení: nález *„ten sloupec je zbytečný"* ušetří sloupec, kdežto nález *„stavový prostor je vedený podle špatné osy, a proto se do něj tahle věc nevejde bez tří záplat"* ušetří celý shluk – a ten druhý je ten cenný. **Omezit výstup rozsahem znamená odříznout si přesně ho.**

Bez argumentu vyjdi z toho, kolem čeho se v `decisions.md` nakupilo nejvíc rozhodnutí v nejkratším okně.

## Hranice

**Relativizují se řešení, ne zadání.** Otevřít znovu se smí rozhodnutí o tom, **jak se něco udělalo** – hodnota výčtu, sloupec, guard, mechanismus. **Nikdy rozhodnutí o tom, co se má dělat**: zadání projektu, rozsah funkcí, produktová volba, obchodní pravidlo. Ta jsou pro skill vstup, ne materiál.

Bez téhle hranice by z něj byl `/oponent` s právem měnit zadání, a to je jiný krok cyklu s jiným vstupem.

**„Uživatel to zamítl" přitom zeď není a skill přes ni smí.** Rozhodnutí vzniklo v tehdejším rozpoložení a kontextu, a ten se vývojem projektu mohl změnit – platí to i pro rozhodnutí, která udělal uživatel sám. **Podmínka je pojmenovat, co se od té doby změnilo**; „udělal bych to jinak" bez toho je jen jiný názor na tutéž věc.

Z toho plyne **tvrdý zákaz pro ověřovatele**: odvolat se na to, že něco už jednou bylo zamítnuto, **není argument**. Musí doložit, co konkrétně se rozbije – jmenovat guard, invariant, text pro zákazníka. V pilotním běhu ověřovatel argumentoval větou „to je přesně ta varianta, kterou §125 zamítlo", a ten bod se udržel jen proto, že k němu vedle toho vypsal šest skutečných čtenářů. Bez zákazu skill jen potvrzuje, že co je rozhodnuté, je rozhodnuté.

## Kdy se pouští a kdy se přeskakuje

**V prvním průchodu cyklem se přeskakuje** – po prvním návrhu žádný dluh z postupného lepení neexistuje. Nabíhá s druhým a dalším kolem.

Spouštěče jsou tři a rozhoduje mezi nimi člověk:

- povinně **před `/breakdown` velkého celku**,
- po několika kolech `/architect`,
- **kdykoli to člověku leží v hlavě** – což je signál sám o sobě.

**Číselný práh vědomě není.** Jeden pilotní běh nestačí na to, aby se dal odvodit, a práh z hlavy by buď překážel, nebo nechytal nic. Místo něj skill v přípravě **spočítá a vypíše**, kolik kol `/architect` a kolik záznamů v `decisions.md` přibylo od posledního běhu – jako informaci, ne jako mez. Čísla se tím hromadí v `done.md` a práh se po několika bězích dá dofitovat místo hádání.

**Pouští se nad sloučeným stavem**, ne nad rozdělanou větví. Jinak označí za záplatu něco, co je mezitím vyřešené jinde, a chybí mu část dokladů.

**Není to běh po každé featuře.** Je drahý a jeho nález je vždycky velký přepis.

------

## Fáze 0 – Příprava

**Společný začátek drží `~/.claude/skills/PREFLIGHT.md`** – načti si ho a řiď se jím. Bod 4 odpadá, skill na kód nesahá. Bod 5 odpadá taky: rozsahem není diff větve, ale historie celého projektu.

Nad rámec toho:

1. **Ověř, že stojíš nad sloučeným stavem.** Jsi-li na jiné než hlavní větvi nebo je-li pracovní strom rozdělaný, řekni to a zeptej se, jestli pokračovat – viz *Kdy se pouští*.
2. **Zjisti, kdy běžel naposledy**, z `## Průchody životním cyklem` v `done.md`. Spočítej, kolik kol `/architect` a kolik záznamů v `decisions.md` od té doby přibylo, a **vypiš to jedním řádkem**. Neběžel-li nikdy, řekni to.
3. **Načti `## Review` a `## Consistency` z projektového `CLAUDE.md`.** Umlčené nálezy jsou zdroj kroniky: nález, který se třikrát zamítl nad touž věcí, je stopa po shluku.
4. **Urči výchozí bod** podle *Rozsahu*. Odvozuješ-li ho sám, řekni z čeho.

## Fáze 1 – Sběr

**Rozešli agenty naráz** a mezitím nic nečti sám – jejich výstup je tvůj vstup. Zadání drží `agents.md`; každému předej výchozí bod, jmenovitý výčet souborů k projití a **vlastní prefix pro pomocné soubory**.

| Agent | Typ | Co vrací |
|---|---|---|
| **Kronika** | `Explore` | všechna rozhodnutí o oblasti **v pořadí vzniku, s datem a s podnětem** |
| **Inventura mechanismů** | `reader` | taxativně pole, hodnoty výčtů, invarianty, přechody a guardy, s doslovnými citacemi |
| **Zkušební sada situací** | `reader` | všechno, co dnešní řešení musí unést, s citací a se jménem mechanismu, který to řeší |

**Podnět je nejcennější položka kroniky** – hledá se ve formulacích „vyplavalo při", „nález z `/review`", „ukázalo se, že". **Git log je samostatný zdroj**, který dokumentace nenese: `git log --reverse -S '<pole>' -- docs/` ukáže, kdy která hodnota vznikla, a zprávy commitů nesou zdůvodnění, které se do dokumentace nedostalo.

**U inventury se zvlášť ptej, na kterou podmnožinu hodnot se který guard ptá.** To je detektor přetížené osy.

**Bez zkušební sady není proti čemu měřit návrh**, takže se nevynechává ani u malé oblasti. Vynechat se smí inventura, je-li oblast malá – pak stačí dva sběrači.

**Každý výstup nese povinnou sekci *Meze posudku***. Tu mez **nezahazuj**: past doložená pilotem je, že sběrač uvede nález s mezí („v obou prohledaných souborech"), hlavní session ji odřízne a ohlásí závěr, který ověřovatel vzápětí vyvrátí.

## Fáze 2 – Shluky a návrh

Tohle je jádro a **nedeleguje se**. Nejsilnější model, `xhigh` – vada tady se násobí do všeho, co po ní přijde.

**Nejdřív vyznač shluky** nad kronikou: co vzniklo blízko sebe v čase kolem téže věci. Skill po nich jde adresně, ne že by na ně náhodou narazil – lovné vzory jsou čtyři:

- **Přetížená osa.** Jedno pole, kterým se postupně řešily různé problémy, až odpovídá na víc otázek naráz. **Poznávací znamení je v guardech, ne v poli:** ptá-li se každý guard jen na jinou podmnožinu hodnot a k rozlišení dvou z nich je potřeba druhé pole vedle, jsou to osy dvě nebo tři.
- **Táž situace řešená pokaždé jinak.** Tři podobné případy, tři různé mechanismy – jednou nová hodnota, podruhé nový sloupec, potřetí nový nález. Úkol není vybrat nejlepší z nich, ale **sjednotit filozofii na jeden typ řešení**, a je-li těch případů víc za sebou, hledat **jeden vzor, který je vyřeší všechny naráz** místo tří dílčích záplat.
- **Řetěz lepení.** Oprava, která si vynutí další opravu, která si vynutí další. **Dostopuj na první článek řetězu** a řekni, co se mělo rozhodnout tam – neopravuj poslední článek.
- **Slepá místa, do kterých se návrh dostává opakovaně.** Nerozhodné a neřešitelné stavy, ze kterých vede ven jedině další podmínka, další sloupec nebo další datum. Opakování je signál, že je špatně osa, ne ten konkrétní stav.

**Ke každému shluku pak napiš návrh alternativy** a k němu **zpětnou zkoušku**: taxativně všechny doložené případy ze zkušební sady, které dnešní řešení pokrývá, a u každého, čím ho pokrývá varianta nová.

**Zpětná zkouška je hlavní mechanismus, ne kontrola navíc.** Kdo dostane zadání „navrhni to elegantněji", **vždycky něco navrhne** – a jeho varianta bude působit čistěji právě proto, že nezná zatáčky, kvůli kterým dnešní řešení vzniklo. Návrh, který zkouškou neprojde, **se nepředkládá**. Bez ní skill vyrábí regrese převlečené za úklid.

**Ke každému návrhu odhadni cenu přepisu** – kolik dokumentů a kolik míst v kódu se dotkne.

## Fáze 3 – Ověření

**Jeden ověřovatel na jeden návrh**, typ `reader`, **nejsilnější model**. Zadání drží `agents.md`.

Obě zkoušky jsou **blokující** a druhá je ta, na kterou se zapomíná:

1. **Pokrývá nové řešení úplně všechno**, na co se v minulosti narazilo a co dnešní řešení pokrývá – i tam, kde to dnešek zvládá nedokonale nebo neúplně?
2. **Je to opravdu zlepšení** – jednodušší, systematičtější, přímočařejší, bez hacků –, a ne jen přepsání jednoho řešení za jiné stejně dobré? Výměna hacku za jiný hack projde první zkouškou hladce.

**Co ověření nepřežije, se uživateli vůbec nezobrazí.** V pilotu padly dva ze dvou velkých návrhů – a **to je platný výsledek, ne selhání běhu**.

**Vedlejší vady, na které ověřovatelé narazí, se nezahazují.** Jsou to normální nálezy: hlásí se se závažností podle `~/.claude/skills/SEVERITY.md` a rozhoduje se o nich podle `~/.claude/skills/FINDINGS.md`. V pilotu byly cennější než návrhy samotné.

## Fáze 4 – Průchod s uživatelem

**Přeruš včas, nabyl-li kontext.** Průchod dlouhou frontou je nejčastější místo, kde session narazí na strop okna a vynutí si kompaktaci v nejhorší možný okamžik – uprostřed nevypořádaného nálezu. Práh, tvar nabídky a to, co všechno se o zbývajících položkách musí uložit do `todo.md`, aby z nich nová session rozhodla bez tvého kontextu, drží `~/.claude/skills/HANDOFF.md`, *Přerušení dlouhého průchodu*.

**Nejdřív vypiš přehled** – kolik shluků, kolik návrhů padlo v ověření a kolik zbývá k rozhodnutí, plus kolik vedlejších vad se našlo. Pak **hned v téže odpovědi** pokračuj první otázkou; ohlásit průchod a skončit je porušení `~/.claude/RULES.md`, *Co ohlásíš, udělej hned v téže odpovědi*.

**Tvar nálezu i volby drží `~/.claude/skills/FINDINGS.md`** – neopisuj si je sem. U návrhu platí výjimka o položce, která není vadou: dnešní řešení funguje, takže *Neopravovat* nedává smysl a volba „jestli a kdy" je legitimní.

**O každém návrhu rozhoduje uživatel**, jeden po druhém. U každého ukaž kroniku shluku (co vzniklo kdy a z jakého podnětu), návrh, verdikt ověřovatele a cenu přepisu.

**Zamítnutý návrh zapiš do `docs/decisions.md`** k rozhodnutí, jehož alternativou byl – jako zavrženou variantu i s důvodem zamítnutí a s verdiktem ověřovatele. Filtr proti opakovanému předkládání tím funguje sám: `decisions.md` je vstup tohohle skillu, takže si ho příští běh přečte ve *Fázi 1*. **Nezakládej kvůli tomu kapitolu v `CLAUDE.md`** – výjimka z `~/.claude/RULES.md` pro umlčené nálezy prověřovacích kroků tady neplatí, protože stojí na tom, že `decisions.md` by nikdo nečetl.

**Přijatý návrh zapiš do `docs/todo.md`** jako práci i s cenou přepisu a předej `/breakdown`.

## Časté chyby

- **Sběrač přečte jen část dokumentů a hlavní session z toho udělá závěr.** Doloženo pilotem u hodnoty `UNDOCUMENTED`: sběrač našel jednoho čtenáře a poctivě uvedl mez („v obou prohledaných souborech"), hlavní session mez zahodila a ohlásila nález, který ověřovatel vzápětí vyvrátil šesti čtenáři. Proto jmenovitý výčet souborů v zadání a povinná sekce *Meze posudku*.
- **Výstup rozsahu se omezí podle jeho vstupu.** Pak se odřízne přesně ten cenný nález – viz *Rozsah*.
- **Ověřovatel se odvolá na dřívější zamítnutí.** Není to argument; musí jmenovat, co konkrétně se rozbije.
- **Věta „nenavrhovat znovu“ se vezme za pokus o manipulaci.** Doloženo tlakovým scénářem 28. 9. 2026: ověřovatel ji ohlásil jako podezřelý obsah tvářící se jako pokyn. Je to ale **běžný a legitimní zápis** u zamítnutého rozhodnutí – a tenhle skill tam sám ukládá svoje. Nemá se hlásit, jen neuznat jako argument.
- **Opatrnost obrácená naruby: zamítnutí se stane zdí i tam, kde podmínka pravidla je splněná.** Týmž měřením: agent doložil, že premisa zamítnutí padla jedenáct dní po něm, **a návrh přesto nepředložil** s odkazem na to, že u něj stojí „nenavrhovat znovu“. Přitom právě tím doložením splnil podmínku, kterou *Hranice* kladou. **Pojmenuješ-li, co se od zamítnutí změnilo, návrh předlož** – rozhodnutí je uživatelovo, ne tvoje.
- **Návrh se předloží bez zpětné zkoušky.** Vypadá čistěji, protože nezná zatáčky – a je to regrese převlečená za úklid.

## Fáze 5 – Závěr

**Zapiš řádek do `## Průchody životním cyklem` v `done.md`.** Datum vyrob `date +%F`, hash `git rev-parse --short HEAD` – obojím příkazem, ne z kontextu. Čtenáři jsou tři: příští běh téhož skillu, `/breakdown` před rozpadem velkého celku, a člověk, který z repozitáře jinak nezjistí, že běh proběhl.

```
- **<datum>** · `/consolidate` · `<hash>` · výchozí bod `<oblast>` · <N> shluků, <M> návrhů (<K> přežilo ověření, <L> přijato) · <P> vedlejších vad
```

Pak vypiš souhrn:

**Návrhový dluh prověřen**

- **Výchozí bod:** <oblast> · **Shluků:** <N>
- **Návrhy:** <M> předloženo, <K> přežilo ověření, <L> přijato
- **Vedlejší vady:** <P> (<rozpad podle závažnosti>)
- **Agenti:** <N> celkem, z toho <K> ověřovatelů · <model a effort>

**Zapsáno**
- <kam a co – decisions.md, todo.md, done.md>

Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo – `~/.claude/RULES.md`, *Styl odpovědí*.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Návrhový dluh je prověřený, můžeš pokračovat /breakdownem.`
- `Prověřený není – brání tomu: <konkrétní seznam>.`

**„Nic velkého k přepsání" patří do první věty**, ne do druhé. Shluk, u kterého má každá záplata doložený důvod, je prověřený výsledek – ne nedodělaný běh.

**Kudy dál** je poslední blok odpovědi, za verdiktem – tvar a pravidla, kdy odrážka musí vypsat celý řetěz včetně ukončení session, drží `~/.claude/skills/HANDOFF.md`. Odtud vede:

- `/breakdown` – rozpad prověřeného celku na úkoly
- vzešla-li ze shluků přestavba návrhu, je další krok `/architect` nad ní, ne rozpad
