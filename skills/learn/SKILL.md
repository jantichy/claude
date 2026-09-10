---
name: learn
description: Skill se použije, když uživatel zadá "/learn", nebo chce zapracovat, zakomponovat či začlenit nový zdroj poznání – přepis schůzky, školení nebo konzultace, článek, cizí dokumentaci, vlastní poznámky – do existující znalostní báze: doplnit z něj znalosti, obohatit je, rozšířit metodiku nebo se z něj naučit. Zdroj vytěží do posledního detailu a rozpustí ho do stávajících textů na místa, kam věcně patří: doplní, prohloubí, opraví, přestaví jejich strukturu, a chybí-li pro znalost místo úplně, navrhne založit novou doménu. Zdrojem smí být i zvukový či obrazový záznam – ten si nechá přepsat /transcriptem – a obrázek či PDF, které vytěží do textu. Na rozdíl od /transcript, který nahrávku přepisuje, tenhle skill přepis vytěžuje; nepřidává ho jako další samostatný soubor a nekopíruje z něj celé pasáže. Rozpory se stávající znalostí předkládá jeden po druhém k rozhodnutí. Doslovné přetisky, citace a datované doklady nepřepisuje nikdy.
argument-hint: [source] [target]
---

# Learn

## Co skill dělá

Vezme jeden zdroj poznání a **zapracuje ho do existující znalostní báze** tak, aby se stal její součástí – ne přílohou. Vstupem je typicky přepis vlastního školení nebo konzultace, ale stejně dobře článek, cizí dokumentace nebo poznámky.

Skill se **nespouští s přepínači**, ale s volným popisem, ze kterého vyčte zdroj i cíl. `argument-hint` proto jmenuje `[source] [target]` jako **dvě věci, které v tom popisu mají zaznít**, ne jako dvě poziční hodnoty:

```
/learn vezmi ~/Desktop/skoleni.md a zakomponuj to do znalostí v analytics
```

Práce má tři těžiště: **vyčerpávající vytěžení** zdroje, **rozlišení skutečného rozporu** od zjednodušení a **zápis na správná místa** stávající struktury. Před prvním zásahem předloží celý plán.

## Co skill nedělá

- **Nepřepisuje nahrávky sám.** Vlastní rozpoznávání řeči v sobě nemá – je-li zdrojem záznam, nechá ho přepsat `/transcript`em a pracuje s výsledkem (*Fáze 1*).
- **Nepíše nový text autorovým hlasem.** To je `/compose`. Tenhle skill formuluje stylem cílové báze, ne stylem autora.
- **Neaudituje bázi.** Vnitřní konzistenci celku řeší `/consistency` – tenhle skill se dívá jen na místa, kterých se zdroj dotkl. Po velké přestavbě ho v závěru doporučí.
- **Nepřejmenovává termín napříč bází.** Vyjde-li z nové znalosti, že se něco jmenuje špatně, je to práce pro `/replace`, a jde-li o termín platný napříč projekty, pro `/ptydepe`.
- **Nezakládá znalostní bázi.** Přijde do hotového repozitáře; zakládat projekt umí `/project`. Novou **doménu uvnitř** existující báze navrhnout smí – ale jen navrhnout, sám ji nezaloží.
- **Nesahá na doklady a citace.** Doslovný přetisk, datovaný záznam ani evidence se nepřepisují, ani když je uživatel jmenuje jako cíl – viz *Fáze 3*.

## Jak je to postavené uvnitř

| Krok | Kdo | Proč zrovna on |
|---|---|---|
| Přepis nahrávky na text | `/transcript` | Umí lokální přepis i slovník jmen; sem pak přichází text jako každý jiný |
| Vytěžení poznatků ze zdroje | vlastní | Rozhoduje o všem dalším a musí být úplné – první průchod se nedeleguje |
| Kontrola úplnosti vytěžení | vlastní, izolovaný agent | Kdo seznam psal, hledá v něm právě to, co už tam dal |
| Zmapování cílové báze | vestavěný `Explore` | Umí projet mnoho souborů a vrátit závěr, ne výpisy |
| Rozlišení rozporu od zjednodušení | vlastní | Jádro skillu, neumí to nikdo jiný |
| Zápis a přestavba | vlastní | Jádro skillu |
| Přejmenování termínu napříč bází | `/replace`, `/ptydepe` | Umí projet všechny výskyty včetně názvů souborů a rozhodnout, jestli se má přejmenovat |
| Audit po velké přestavbě | `/consistency` | Doporučí se v závěru, uvnitř se nevolá |

**Volání cizích nástrojů je implementační detail, ne rozhraní.** Vyměnit se smí kdykoliv. Závazné je: nic ze zdroje se neztratí, plán se předloží před prvním zásahem, rozpory se rozhodují po jednom a doklady se nepřepisují.

------

## Fáze 0 – Příprava

Společný začátek je v `~/.claude/skills/PREFLIGHT.md`. Odchylky:

1. **Kořenem projektu je cílová znalostní báze, ne adresář se zdrojem.** Stojíš-li ve zdrojovém adresáři, kořen podle přípravy nic neurčuje – cíl se bere ze zadání (*Fáze 1*).
2. **Kontrakt příkazů se nevyžaduje.** Znalostní báze nemá kód a `Fáze 4` přípravy odpadá; řekni to nahlas.
3. **Stav pracovního stromu ověř důkladně.** Skill přepisuje existující soubory, takže rozpracovaná změna v cíli se s jeho zásahem smíchá k nerozeznání. Je-li strom špinavý, nabídni commit **dřív, než se cokoliv začne**. Ten čistý strom je jediná cesta zpátky: ukáže-li se výsledek jako špatný, zahazuje se `git checkout`, ne ručním opravováním.
4. **Zjisti, jestli má cíl zapnutý autocommit.** Má-li ho, tvůj zápis se commitne – řekni dopředu, že se tak stane, a v závěru uveď, co jsi commitnul.

## Fáze 1 – Zdroj a cíl

Volný popis za `/learn` nese obojí. Co v něm chybí, doplň z adresáře, ve kterém stojíš – zpravidla je to právě jedna z těch dvou stran.

**Zdroj** načti celý, ne namátkou. Je-li jich víc, zpracuj je v jednom běhu společně: dvě části téhož školení nemají vznikat jako dva nesouvisející zápisy.

**Cíl** rozhoduje o rozsahu a určuje se ze zadání:

| Zadání | Co udělej |
|---|---|
| Jmenuje konkrétní doménu („do `analytics`“) | Ber to jako svolení. **Neptej se znovu.** |
| Jmenuje jen bázi („do znalostí v `context`“) | Urči doménu sám z obsahu zdroje a **nech ji potvrdit** přes `AskUserQuestion`, s odůvodněním, proč zrovna tu |
| Nejmenuje nic | Urči bázi i doménu a nech potvrdit obojí najednou |

**Uvnitř zadané domény si vybíráš soubory a sekce sám** – to je celá práce skillu, ne rozhodnutí uživatele.

### Když je zdrojem nahrávka

Zvukový i obrazový záznam je **platný vstup, ne důvod k odmítnutí** – všechny formáty, které bere `/transcript`. Nech si ho přepsat a dál pracuj s přepisem jako s kterýmkoliv jiným textem.

**Cíl urči dřív, než nahrávku pošleš na přepis.** Z cílové domény vytáhni jména, značky, nástroje a odborné termíny, které v záznamu nejspíš zazní, a předej je jako popis nahrávky – rozpoznávání pak nekomolí právě to, co báze už zná. Je to jediná věc, kterou o té nahrávce víš předem, a nikdo jiný ji nemá.

Zadání je **kontrakt výstupu, ne seznam cizích kroků**:

- **vyčištěný doslovný přepis** do Markdownu a nic jiného. Shrnutí ani časované titulky vytěžení nepřispějí – shrnutí je navíc škodlivé, protože to, co z hovoru vypustí, je přesně to, co má *Fáze 2* najít.
- **bez rozlišení mluvčích.** Vytěžuje se tvrzení, ne kdo je řekl, a do báze se poznatek stejně zapisuje bez identifikace osob (*Fáze 7*). Diarizace by přidala minuty výpočtu i závislosti kvůli údaji, který se zahodí.

**Přepis zůstane ležet vedle nahrávky** pod jejím jménem; mazat ho není co. Druhé vytěžení téhož záznamu, až doména vyroste, je nad textem zadarmo a nad audiem stojí celý přepis znovu – a sporné tvrzení se dohledává v textu, ne přehráváním. V evidenci zdroje (*Fáze 8*) uveď obojí: přepis, ze kterého se vytěžovalo, i cestu k původní nahrávce.

### Když je zdrojem obrázek nebo PDF

**Obrázek i PDF jsou plnohodnotný zdroj** – ať přijdou samy (nafocený flipchart, screenshot, oskenovaný leták, deck ve formátu PDF), nebo jako příloha textového zdroje (slajdy ke školení, schéma v článku). **Přečti je a vytěž z nich poznatky stejně jako z textu** – přeskočit je znamená ztratit to, co je jenom v nich.

**Dlouhé PDF ber po částech, ne namátkou.** Čtou se nejvýš dvě desítky stran naráz a u delšího dokumentu se rozsah stran musí uvést – projdi ho tedy celý po blocích a v seznamu poznatků měj po ruce, ze které strany který je. Vzít z osmdesátistránkového dokumentu prvních dvacet stran a tvářit se, že je vytěžený, je ta nejhorší varianta: chybějící znalost nemá kdo poznat, protože zdroj tvrdí, že zpracovaný je.

**Do báze se ale nekopírují.** Znalostní báze je text: grepuje se, vytěžuje dalším během a přestavuje se v ní struktura – příloha, na kterou vede cesta, se při první přestavbě rozejde a její obsah nenajde nikdo. Nese-li obrázek nebo stránka vztah, který věta nezastane – schéma, tok, matice –, **překresli ho do Markdownu**: tabulkou, odrážkovou hierarchií nebo diagramem v `mermaid`. Do báze pak vstoupí obsah obrázku, ne odkaz na něj.

Je to totéž rozhodnutí, jaké dělá `/transcript` u videa: obraz se nikam nepřenáší, vzniká z něj text.

## Fáze 2 – Vytěžení zdroje

**Nejsilnější model, `xhigh`** (`~/.claude/RULES.md`, *Model a effort podle úkolu*). Poznatek, který tady propadne, se už nikdy nenajde: zdroj příště nemusí existovat a nikdo nebude vědět, že chybí.

Projdi zdroj a vypiš **očíslovaný seznam poznatků**. Jeden poznatek = jedno tvrzení, které se dá samostatně použít nebo popřít. Číslo mu zůstane po celý běh a odkazuje se na něj ve všech dalších fázích.

Vytěžuj **taxativně, ne výběrově**. Patří sem i to, co ti připadá samozřejmé, protože samozřejmé je to tobě a ne bázi:

- pravidla, postupy, prahy, čísla, jména nástrojů a jejich verze,
- **důvody a zdůvodnění** – „proč“ je cennější než „co“ a ztrácí se první,
- výjimky, okrajové případy a to, co nefunguje,
- pořadí kroků a co na čem závisí,
- rozhodnutí, která v hovoru padla, i zavržené varianty.

**Z hovoru ber jen tvrzení, které v něm obstálo.** Co někdo nadhodil a druhá strana to vzápětí opravila nebo odmítla, poznatek není – v přepisu to poznáš z průběhu hovoru, ne z nálepky u repliky. Zapsat omyl, který na místě padl, je horší než ho vynechat: v bázi po něm nezůstane stopa, že to byl omyl.

**Nekopíruj formulace.** Poznatek zapiš jako tvrzení, ne jako citát – citát se pak nedá zapracovat do cizí věty.

Pak **kontrola úplnosti**: pošli izolovanému agentovi – **výchozí model session, `high`**, protože hledat, co v seznamu chybí, je úsudek, ne výpis – zdroj a hotový seznam s jediným úkolem – *co ve zdroji je a v seznamu chybí?* Nesmí vidět, jak seznam vznikal, jinak hledá právě to, co už v něm je. Co najde, doplň a **kontrolu opakuj**, dokud se nevrátí prázdná. **Vrátí-li nálezy i potřetí, přestaň a řekni to** i s tím, co poslední kolo našlo – v tu chvíli je chyba ve způsobu, jakým poznatky formuluješ, a další kolo ji neopraví.

## Fáze 3 – Zmapování cíle

Nastuduj cílovou doménu: strukturu souborů, jak se v ní člení obsah, jakým jazykem a jakými termíny mluví. U rozsáhlé báze na to pošli `Explore`.

**U každého souboru urči, jak hluboko se do něj smí sáhnout.** Bez konfigurace, podle toho, na co ten text odpovídá:

| Povaha souboru | Odpovídá na | Co se smí |
|---|---|---|
| **Metodika** – návod, princip, standard, checklist postupu | *jak se něco dělá* | Přeformulovat, přeskládat, přejmenovat sekce, sloučit i rozdělit. Přestavba **souborů** se potvrzuje – viz *Fáze 5* |
| **Fakta a hotové formulace** – profily osob a organizací, ceníky, medailonky, texty určené k použití | *co platí* | Jen doplnit a opravit nesprávné. **Nepřestavovat a nepřeformulovávat** to, co je správně – někdo to psal ručně a čte to očima |
| **Doklad** – doslovný přetisk, citace, datovaný záznam události, evidence, log | *co se stalo, co kdo řekl* | **Nic.** Znalost se z něj jen odvozuje a zapisuje jinam |

**Kritérium je povaha textu, ne jméno adresáře** – doklad může ležet uvnitř metodické domény a naopak.

**Říká-li ale cílová báze sama, kam se nesahá, platí to nad tvým úsudkem.** Znalostní báze mívá ve svém `CLAUDE.md` jmenovaná místa, která jsou doslovné přetisky nebo historické artefakty a nemění se ani kvůli typografii. **Přečti si ho a ber ten výčet jako závazný**; není to konfigurace, kterou by si skill zaváděl, ale zapsané rozhodnutí, které tam bylo dřív než on.

**Nejasnou povahu neodhaduj** – zeptej se, a to dřív než v plánu. Je to jediné místo, kde špatný odhad znamená nevratnou škodu.

**Nenajdeš-li pro poznatky vhodné místo, není to tvoje chyba – je to nález.** Znalostní báze nemusí mít doménu pro všechno, o čem se dá mluvit. Necpi obsah tam, kam nepatří, jen aby se někam vešel; **navrhni založit novou** – v plánu, jako každou jinou přestavbu struktury (*Fáze 5*).

## Fáze 4 – Konfrontace

Každý poznatek postav proti tomu, co báze říká dnes, a zařaď ho. **Tohle je jádro skillu a rozhoduje o tom, na co se bude uživatel ptát.**

| Zařazení | Poznáš podle | Co s tím |
|---|---|---|
| **Nové** | Báze o tom nemá nic | Zapracuj |
| **Doplnění** | Báze to má, zdroj přidává další případ, výjimku nebo detail | Zapracuj k tomu, co tam je |
| **Prohloubení** | Báze to má nastřelené jednou větou, zdroj to rozebírá | Rozšiř – zdroj je tu ten přesnější |
| **Zjednodušení** | Zdroj říká hrubší verzi toho, co báze má přesněji | **Není rozpor.** Bázi nech být; zvaž jen, jestli se zjednodušená formulace nehodí jako úvodní věta pro pochopení |
| **Zúžení** | Zdroj mluví jen o jedné variantě z několika | **Není rozpor.** Zařaď jako konkrétní případ pod obecnější pravidlo |
| **Překonání** | Rozdíl plyne prokazatelně z toho, že se svět venku pohnul – nová verze nástroje, změněné API, zrušená funkce | Aktualizuj a **nech stopu**, co platilo dřív. Není-li ta prokazatelnost, je to rozpor |
| **Rozpor** | Obě tvrzení míří na tutéž věc za týchž podmínek a nemohou platit obě | **Do *Fáze 6*.** Neřeš sám |

**Test na rozpor je jediný: jednal by čtenář ve stejné situaci podle každé verze jinak?** Když ne – protože jedno je obecnější, hrubší, novější nebo platí jinde – rozpor to není a **nehlas ho**. Falešný rozpor stojí uživatele rozhodnutí, které nemá co rozhodovat, a po třetím takovém přestane odpovědi číst.

**Druhý test, když si nejsi jistý:** *odkud ten rozdíl plyne?* Z hloubky, z rozsahu nebo z času → zapracuj sám. Ze samotného tvrzení → zeptej se.

**Poznatky mimo zadanou doménu neztrácej.** Patří-li poznatek zřetelně jinam, posbírej je a v plánu předlož **jedním dotazem za celou skupinu**, jestli je zapracovat i tam. Bez souhlasu se mimo zadaný cíl nesahá.

**Co není přenositelná znalost** – specifika jednoho klienta, dohody, osobní věci, historky – **nezapracovávej**, ale odlož si to do seznamu pro závěr i s důvodem. Rozdíl mezi „posoudil jsem a nepatří to tam“ a „přehlédl jsem to“ musí být vidět.

## Fáze 5 – Plán

**Předlož celý plán najednou, dřív než se sáhne na první soubor.**

```
## Plán zapracování – <zdroj> → <cíl>

**Poznatků:** <N> · nové <n> · doplnění <n> · prohloubení <n> · zúžení <n> · překonání <n> · zjednodušení <n> · rozpory <n> · mimo doménu <n> · nezapracováno <n>

Součet **musí dát <N>** – všech sedm zařazení z *Fáze 4* plus poznatky mířící mimo doménu a nepřenositelné. Zjednodušení se nezapracovává a přesto není „nezapracováno“: báze už tu znalost má lépe.

**Zásahy do obsahu**
- `<soubor>` › *<sekce>* – <typ zásahu>, poznatky <čísla>
- …

**Přestavba struktury** *(je-li potřeba)*
- <co se založí, přesune, sloučí nebo zruší – včetně případné nové domény>

**K rozhodnutí**
- <N> rozporů – proberu je po jednom v další fázi
- <N> poznatků míří mimo zadanou doménu, do `<doména>`

**Nezapracuje se**
- <co a proč>
```

Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo – `~/.claude/RULES.md`, *Styl odpovědí*.

**Přestavba struktury se potvrzuje zvlášť** – zakládání, přesun, sloučení nebo zrušení souboru, a v krajním případě i **založení celé nové domény**, když se pro znalost nenašlo místo nikde. Nestačí ji vyjmenovat: napiš, **jak to má vypadat po přestavbě, proč a v čem se nová znalost do stávající struktury nevejde**, a nech to potvrdit přes `AskUserQuestion`. U nové domény přidej, čím se vymezuje proti nejbližší stávající – jinak z ní bude druhé místo na totéž.

Přeskládání uvnitř jednoho souboru potvrzení nepotřebuje – u metodiky je to běžná práce.

Nech plán odsouhlasit. Teprve pak dál.

## Fáze 6 – Rozpory

Proberte rozpory **jeden po druhém**, v pořadí, ve kterém na sebe navazují – od obecnějších ke konkrétnějším, ať pozdější rozhodnutí staví na dřívějším.

U každého napiš **podstatu rozporu vlastními slovy** a **ocituj obě verze**, když to bez citace není jasné. Pak se zeptej přes `AskUserQuestion` a **nabídni rovnou hotová řešení**, ne otevřenou otázku:

- **Platí nová verze** – stávající text se přepíše, protože zdroj je novější nebo přesnější.
- **Platí stávající** – poznatek se zahodí, protože zdroj zjednodušil nebo se mýlil.
- **Platí obojí, za jiných podmínek** – obě verze zůstanou a **vymezí se jim rozsah**, kdy která platí.

U každé volby napiš, co se stane s textem. Odpověď zapiš rovnou do plánu, ať se na totéž neptáš podruhé.

## Fáze 7 – Zápis

Zapisuj podle odsouhlaseného plánu. Platí přitom:

- **Mluv jazykem báze, ne zdroje.** Termíny, styl i typografii ber z cílové domény; zdroj je materiál, ne předloha.
- **Jeden termín pro jednu věc** (`~/.claude/RULES.md`). Pojmenovává-li zdroj jinak něco, co báze už zná, použij jméno báze. Ukáže-li se, že jméno v bázi je špatně, **nepřejmenovávej to sám** – je to práce pro `/replace`, u termínu napříč projekty pro `/ptydepe`.
- **Poznatek jde na jedno místo.** Patří-li zdánlivě na dvě, jedno z nich je to pravé a druhé na ně odkazuje – `~/.claude/RULES.md`, *Single source of truth*.
- **Zdůvodnění zapisuj spolu s pravidlem.** Bez „proč“ se pravidlo při první kolizi obejde.
- **Ukliď po sobě.** Přejmenuješ-li sekci nebo přesuneš obsah, projdi odkazy na ně, souhrnné počty a přehledové tabulky – `~/.claude/RULES.md`, *Propagace změny*.
- **Odliš jisté od tipnutého.** Co ve zdroji zaznělo s „tuším“ nebo „myslím“, **nezapisuj do báze jako fakt** – patří to do fronty úkolů jako věc k ověření. Mluvené slovo nejistotu nese často a v zápisu po ní nezůstane stopa.
- **Vypusť identifikaci konkrétního případu.** Jména klientů a osob, měřicí identifikátory, URL a čísla z jedné zakázky do znalosti nepatří – zůstává **vzorec, který se opakuje**. Bez toho se z báze stane archiv zakázek.
- **Zdroje se nedotýkej.** Je to cizí podklad a zůstává, kde je.

## Časté chyby

- **Zdroj skončí jako nový soubor.** Je to nejsnazší cesta a vypadá jako práce, ale znalost tím do báze nevstoupí – zůstane vedle ní a nikdo ji nenajde. Zapracovat znamená rozpustit.
- **Zjednodušení se nahlásí jako rozpor.** Školení říká věci hruběji schválně. Rozpor je jen tam, kde by čtenář jednal ve stejné situaci jinak.
- **Lidsky psaný text se přeorá celý.** Profil, ceník nebo medailonek někdo psal ručně a pozná to na první pohled. Doplňuje se, nepřestavuje.
- **Vytěží se jen to hlavní.** Detaily, prahy a hlavně důvody vypadají jako vata, dokud zdroj existuje. Pak zmizí a nikdo neví, že chyběly.
- **Formulace se opíší ze zdroje.** Citát z hovoru se do metodiky nevejde a rozbije jí styl.

## Fáze 8 – Inventura a závěr

**Nejdřív si ověř vlastní práci**, teprve pak hlas hotovo (`~/.claude/RULES.md`, *Co jsi vygeneroval, přečti zpátky*):

1. **Každý poznatek má své místo, nebo důvod, proč ho nemá.** Projdi číslovaný seznam z *Fáze 2* celý – nezapracovaný poznatek bez důvodu je ztracená znalost.
2. **Nic se neztratilo z toho, co v bázi bylo.** Projdi `git diff` a u každého smazaného kusu textu si odpověz, kam se jeho obsah přesunul. Grep nestačí – `~/.claude/RULES.md`, *Mazání ověř diffem, ne grepem*.
3. **Soubory se dají přečíst** – odkazy vedou někam, nadpisy navazují.

**Pak zapiš řádek do evidence zdrojů.** Vede-li cílová doména soupis záznamů, ze kterých se vytěžovalo, **doplň ho**: odkud zdroj je (cesta do archivu, URL, u nahrávky cesta k záznamu **i** k přepisu), co se z něj vzalo a do kterých souborů, a co v něm zůstalo otevřené k ověření. Nevede-li ho, **nabídni ho založit** – jako každou jinou změnu struktury (*Fáze 5*).

**Proč, když se zdroj sám nikam nekopíruje:** bez toho řádku nejde u sporného tvrzení dohledat, odkud pochází, a hlavně nejde záznam projít **podruhé**, až doména vyroste a najde v něm víc, než co se z něj vzalo napoprvé. Commit message ani jedno nezastane – nikdo v ní ty dvě věci nehledá.

```
## Zapracováno

- **Zdroj:** <cesta> · **Cíl:** <doména>
- **Poznatků:** <N>, z toho zapracováno <n>

**Kam to šlo**
- `<soubor>` › *<sekce>* – poznatky <čísla>, <typ zásahu>

**Rozhodnuté rozpory**
- <o co šlo> → <jak jsi rozhodl>

**Nezapracováno**
- <co a proč – patří jinam, není to přenositelná znalost, zamítnuto v rozporu>

**Evidence zdroje**
- <kam se zapsal řádek, nebo „doména evidenci nevede">

**Změny**
- <výstup `git diff --stat`> · <commitnuto / v pracovním stromu>
```

Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo – `~/.claude/RULES.md`, *Styl odpovědí*.

Došlo-li na přestavbu struktury, doporuč v závěru `/consistency` – přeskládání souborů rozejde odkazy i mimo dotčenou doménu.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Znalost je zapracovaná a ověřená, můžeš pokračovat dalším zdrojem.`
- `Zapracovaná není – brání tomu: <konkrétní seznam>.`

