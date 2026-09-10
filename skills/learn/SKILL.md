---
name: learn
description: Skill se použije, když uživatel zadá "/learn", nebo chce zapracovat, zakomponovat či začlenit nový zdroj poznání – přepis schůzky, školení nebo konzultace, článek, cizí dokumentaci, vlastní poznámky – do existující znalostní báze: doplnit z něj znalosti, obohatit je, rozšířit metodiku nebo se z něj naučit. Zdroj vytěží do posledního detailu a rozpustí ho do stávajících textů na místa, kam věcně patří: doplní, prohloubí, opraví, přestaví jejich strukturu, a chybí-li pro znalost místo úplně, navrhne založit novou doménu. Zdrojem smí být i zvukový či obrazový záznam, obrázek nebo PDF. Na rozdíl od /transcript, jehož výsledkem je přepis, jde tomuhle skillu o znalost v něm – nahrávku si proto jen nechá přepsat a přepis pak vytěžuje; nepřidává ho jako další samostatný soubor a nekopíruje z něj celé pasáže. Rozpory se stávající znalostí předkládá jeden po druhém k rozhodnutí. Doslovné přetisky, citace a datované doklady nepřepisuje nikdy.
argument-hint: [source] [target]
---

# Learn

## Co skill dělá

Vezme zdroj poznání a **zapracuje ho do existující znalostní báze** tak, aby se stal její součástí – ne přílohou. Vstupem je typicky přepis vlastního školení nebo konzultace, ale stejně dobře článek, cizí dokumentace, poznámky – a taky rovnou nahrávka, obrázek nebo PDF (*Fáze 1*).

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
| Čtení obrázků a PDF | vlastní | Vytěžuje se rovnou při čtení, mezikrok navíc by jen ubral kontext |
| Vyříznutí snímků z videa | `ffmpeg` | Jediný krok s vlastním příkazem; volba filtru je detail, závazné je jen to, že se snímky po vytěžení mažou |
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

**Cíl urči dřív, než nahrávku pošleš na přepis.** Z cílové domény vytáhni jména, značky, nástroje a odborné termíny, které v záznamu nejspíš zazní, a předej je jako popis nahrávky – rozpoznávání pak nekomolí právě to, co báze už zná. **Vybírej, nesypej všechno:** slovník má technický strop daný modelem – jeho výši drží `/transcript`, který ho měřil – a při přetečení se uříznou termíny na začátku, a to tiše. Ber tedy to, co v nahrávce opravdu zazní a co se snadno komolí.

**Tři otázky průvodce `/transcriptu` si zodpověz sám a nahlas to oznam.** Je to jediné místo, kde tenhle skill mluví za uživatele, a smí to proto, že odpovědi plynou ze zadání, se kterým `/learn` běží – uživatel by na nich neměl co rozhodovat:

- **vyčištěný doslovný přepis a nic dalšího.** Není to jen úspora času: shrnutí je tu škodlivé, protože co z hovoru vypustí, je přesně to, co má *Fáze 2* najít. **Řekni si o to výslovně** – bez volby vzniknou i shrnutí a časované titulky.
- **rychlejší model rozpoznávání**, tedy výchozí volbu `/transcriptu`. Slovník z domény řeší právě to, kvůli čemu se po pomalejším sahá – komolená vlastní jména –, takže výrazně delší běh nemá co vyvážit.
- **bez rozlišení mluvčích.** Samo se nezapne, ale ani o něj nežádej: vytěžuje se tvrzení, ne kdo je řekl, a do báze se poznatek stejně zapisuje bez identifikace osob (*Fáze 7*). Ušetří to minuty výpočtu i doinstalování závislostí.

**Je-li zdrojem video, zeptej se na obraz dřív, než pošleš zvuk na přepis.** `/transcript` bere jen zvukovou stopu, takže obsah, který zazněl jenom na slajdech, by propadl tiše. Jedna otázka přes `AskUserQuestion`, tři volby:

- **Přiložím slajdy** – vyžádej si cestu. Jsou to obrázky nebo PDF a vytěží se spolu s přepisem v jednom běhu; nedodá-li je hned, nech přepis běžet a počkej na ně před *Fází 2*.
- **Vytáhni je z videa** – vyřízni snímky při změně obrazu do dočasného adresáře **mimo cílovou bázi** a přečti je jako obrázky:

  ```bash
  ffmpeg -i <video> -vf "select='gt(scene,0.3)'" -vsync vfr <tmp>/snimek-%03d.jpg
  ```

  Nevrátí-li to skoro nic, přepni na pevný interval (`fps=1/30`). **Vyjde-li snímků víc než pár desítek, nejdřív je prolistuj a zahoď opakované** – prezentace se vrací na tentýž slajd a číst ho popáté nepřidá nic, jen sní kontext. Po vytěžení snímky **smaž**; na rozdíl od přepisu se k nim nikdo nevrací.
- **Stačí zvuk** – vědomé rozhodnutí obraz zahodit. Zapiš ho do evidence zdroje (*Fáze 8*) jako nevytěženou část, ať je za rok vidět, že záznam nebyl vytěžený celý.

**Na cokoliv dalšího ať se `/transcript` ptá uživatele** – na jazyk, na hranici u dvojjazyčné nahrávky, na kolizi jmen i na existující přepis v adresáři. Ty odpovědi ze zadání `/learn` neplynou a tichá volba by u existujícího přepisu přepsala starší práci.

**Chybí-li nástroje, není to konec** – `/transcript` umí říct, co doinstalovat. **Přepis, který se nezdaří, ale konec je:** nevytěžuj z toho, co se přepsat podařilo, protože neúplný zdroj vypadá jako úplný a *Fáze 2* nemá jak poznat, že jí kus chybí. Je-li nahrávek víc a selže jen jedna, pokračuj ostatními a **řekni jmenovitě, která vypadla**.

**Přepis zůstane ležet vedle nahrávky** pod jejím jménem; mazat ho není co. **Leží-li nahrávka uvnitř cílové báze, platí to beze změny** – jen to řekni nahlas a **přepis commitni samostatně, ještě než sáhneš na obsah báze**. Tím zůstane v platnosti záruka z *Fáze 0*: cesta zpátky přes `git checkout` musí vést k stavu před zásahem do znalostí, ne před přepisem. Druhé vytěžení téhož záznamu, až doména vyroste, je nad textem zadarmo a nad audiem stojí celý přepis znovu – a sporné tvrzení se dohledává v textu, ne přehráváním. V evidenci zdroje (*Fáze 8*) uveď obojí: přepis, ze kterého se vytěžovalo, i cestu k původní nahrávce.

### Když je zdrojem obrázek nebo PDF

**Obrázek i PDF jsou plnohodnotný zdroj** – ať přijdou samy (nafocený flipchart, screenshot, oskenovaný leták, deck ve formátu PDF), nebo jako příloha textového zdroje (slajdy ke školení, schéma v článku). **Přečti je a vytěž z nich poznatky stejně jako z textu** – přeskočit je znamená ztratit to, co je jenom v nich. Vytěžení samo se ničím neliší a řídí ho *Fáze 2* včetně kontroly úplnosti.

**Dlouhé PDF ber po blocích, ne namátkou.** Čtecí nástroj má strop na počet stran v jednom volání, takže dlouhý dokument se musí projít po částech a **je na tobě, aby se prošel celý** – měj u poznatků po ruce, ze které strany který je. Vzít z osmdesátistránkového dokumentu prvních pár desítek stran a tvářit se, že je vytěžený, je nejhorší možná varianta: chybějící znalost nemá kdo poznat, protože zdroj se tváří jako zpracovaný. Totéž platí pro kontrolu úplnosti – agentovi v *Fázi 2* předej celý rozsah, ne první blok.

**Do báze se ale nekopírují.** Znalostní báze je text: grepuje se, vytěžuje dalším během a přestavuje se v ní struktura – příloha, na kterou vede cesta, se při první přestavbě rozejde a její obsah nenajde nikdo. Nese-li obrázek nebo stránka vztah, který věta nezastane – schéma, tok, matice –, **překresli ho do Markdownu**: tabulkou, odrážkovou hierarchií nebo diagramem v `mermaid`.

**Co se překreslit nedá, se popíše a zdroj se ocituje.** Fotka obrazovky, graf s daty, sken rozhraní – z takového obrázku vytěž, co z něj plyne, a do evidence zdroje (*Fáze 8*) zapiš cestu k souboru, ať se dá dohledat. Do báze pak jde závěr, ne obrázek: kdo bude potřebovat originál, najde ho přes evidenci.

## Fáze 2 – Vytěžení zdroje

**Nejsilnější model, `xhigh`** (`~/.claude/RULES.md`, *Model a effort podle úkolu*). Poznatek, který tady propadne, se už nikdy nenajde: zdroj příště nemusí existovat a nikdo nebude vědět, že chybí.

Projdi zdroj a vypiš **očíslovaný seznam poznatků**. Není-li zdrojem text, platí to beze změny – přepis, oskenovaná stránka i slajd se vytěžují stejně, jen se k nim čte podle *Fáze 1*. Jeden poznatek = jedno tvrzení, které se dá samostatně použít nebo popřít. Číslo mu zůstane po celý běh a odkazuje se na něj ve všech dalších fázích.

Vytěžuj **taxativně, ne výběrově**. Patří sem i to, co ti připadá samozřejmé, protože samozřejmé je to tobě a ne bázi:

- pravidla, postupy, prahy, čísla, jména nástrojů a jejich verze,
- **důvody a zdůvodnění** – „proč“ je cennější než „co“ a ztrácí se první,
- výjimky, okrajové případy a to, co nefunguje,
- pořadí kroků a co na čem závisí,
- rozhodnutí, která v hovoru padla, i zavržené varianty.

**Z hovoru ber jen tvrzení, které v něm obstálo.** Co někdo nadhodil a druhá strana to vzápětí opravila nebo odmítla, poznatek není – v přepisu to poznáš z průběhu hovoru, ne z nálepky u repliky. Zapsat omyl, který na místě padl, je horší než ho vynechat: v bázi po něm nezůstane stopa, že to byl omyl.

**Nekopíruj formulace.** Poznatek zapiš jako tvrzení, ne jako citát – citát se pak nedá zapracovat do cizí věty.

Pak **kontrola úplnosti**: pošli izolovanému agentovi – **výchozí model session, `high`**, protože hledat, co v seznamu chybí, je úsudek, ne výpis – zdroj v úplném rozsahu – u nahrávky přepis, u PDF všechny strany, u videa se slajdy obojí – a hotový seznam s jediným úkolem – *co ve zdroji je a v seznamu chybí?* Nesmí vidět, jak seznam vznikal, jinak hledá právě to, co už v něm je. Co najde, doplň a **kontrolu opakuj**, dokud se nevrátí prázdná. **Vrátí-li nálezy i potřetí, přestaň a řekni to** i s tím, co poslední kolo našlo – v tu chvíli je chyba ve způsobu, jakým poznatky formuluješ, a další kolo ji neopraví.

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

**Pak zapiš řádek do evidence zdrojů.** Vede-li cílová doména soupis záznamů, ze kterých se vytěžovalo, **doplň ho**: odkud zdroj je (cesta do archivu, URL, u nahrávky cesta k záznamu **i** k přepisu), co se z něj vzalo a do kterých souborů, co v něm zůstalo otevřené k ověření, a **co se z něj vědomě nevytěžilo** – zahozený obraz videa, obrázek, který se nedal překreslit. To poslední je nejcennější řádek: říká, že se k záznamu vyplatí vrátit. Nevede-li ho, **nabídni ho založit** – jako každou jinou změnu struktury (*Fáze 5*). **Odmítne-li se, nevytěžená část se tím neztrácí:** vypíšeš ji v závěru mezi nezapracovaným, protože jinak by o ní nevěděl nikdo.

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
- <co se ze zdroje vědomě nevytěžilo – zahozený obraz videa, nepřekreslitelný obrázek – nebo „celý zdroj vytěžen">

**Změny**
- <výstup `git diff --stat`> · <commitnuto / v pracovním stromu>
```

Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo – `~/.claude/RULES.md`, *Styl odpovědí*.

Došlo-li na přestavbu struktury, doporuč v závěru `/consistency` – přeskládání souborů rozejde odkazy i mimo dotčenou doménu.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Znalost je zapracovaná a ověřená, můžeš pokračovat dalším zdrojem.`
- `Zapracovaná není – brání tomu: <konkrétní seznam>.`

