---
name: proofread
description: Skill se použije, když uživatel zadá "/proofread" (se souborem, dokumentem Wordu, odkazem na Google Doc či web, nebo s vloženým textem), nebo chce udělat korekturu či redakci hotového textu – opravit pravopis, gramatiku a typografii a vylepšit stavbu, pořadí, skladbu a styl. Česky i anglicky; u angličtiny hledá czenglish, otrocké překlady z češtiny a místa, která by rodilý mluvčí řekl jinak, s předností americké angličtiny. Jednoznačné chyby opraví sám, menší úpravy navrhne ke schválení dávkou, větší přepisy po jednom s variantami; do .docx zapíše všechno jako revize a komentáře. Autorův záměr nepřepisuje a fakta nemění – věcně podezřelá tvrzení ověří odborníkem na téma a nahlásí jako otázku. Pravidla čte z ~/Context/Text/. Na rozdíl od /compose nepíše nový text autorovým hlasem; na rozdíl od /oponent neposuzuje argumentaci, ale jak je text napsaný a jestli v něm nejsou věcné chyby; na rozdíl od /review neprověřuje práci na větvi projektu.
argument-hint: [soubor nebo odkaz]
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent, Skill, AskUserQuestion, WebFetch, mcp__claude_ai_Google_Docs__read_doc, mcp__claude_ai_Google_Docs__update_doc]
---

# Proofread

## Co skill dělá

Korektura a redakce jednoho hotového textu, česky nebo anglicky. Cílem je **celkově lepší text**, ne jen bez hrubek: prochází ho od stavby a pořadí, ve kterém se rozvíjí, přes odstavec a větu až po slovo a sazbu. Vstupem je soubor, dokument Wordu (`.docx`), Google Doc, webová stránka, nebo text vložený do konverzace.

Vedle toho text vždycky přečte odborník na jeho téma a **věcně podezřelá tvrzení nahlásí** – neopraví je, fakt mění jen autor.

Nálezy dělí do tří pater podle toho, čí je rozhodnutí: **jednoznačné opraví sám**, **menší stylistiku navrhne dávkou** ke schválení, **větší přepis předloží po jednom** s variantami. Všechna pravidla – co je chyba a co jen volba – čte z domény `~/Context/Text/`; sám nese jen postup.

**U dokumentu Wordu se nic neschvaluje v konverzaci:** všechna tři patra se zapíšou do dokumentu jako revize a komentáře a autor o nich rozhodne ve Wordu.

Režimy nemá: chová se vždycky stejně a liší se jen tím, kam zapíše výsledek.

## Co skill nedělá

- **Nepíše nový text a nevnucuje autorský hlas.** Psaní Honzovým hlasem je `/compose`; tady se hlas jen chrání před uhlazením.
- **Neposuzuje argumentaci a strategii.** Oponenturu toho, jestli úvaha drží a co nebude fungovat, dělá `/oponent`. Tady se ověřují jen jednotlivá věcná tvrzení – a i ta se jen hlásí jako otázka, nemění.
- **Neprověřuje práci na větvi projektu.** Soulad dokumentace s doménou `Text` jako součást revize hotové práce dělá `/review`; tenhle skill bere jeden text a udělá z něj lepší text.
- **Nenese pravidla jazyka.** Co v doméně chybí, se doplní do `~/Context/Text/` (`/learn`), ne sem.

## Jak je to postavené uvnitř

| Krok | Kdo | Proč zrovna on |
|---|---|---|
| Rozpoznání jazyka, druhu textu a hlasu | vlastní | Rozhoduje, která pravidla platí; nikdo jiný to nezná. |
| Inventář faktů a seznam rozhodnutí | vlastní | Je to měřítko pro kontrolu po zápisu – musí ho držet ten, kdo zapisuje. |
| Průchod stavbou a stylem | agent typu `reader` | Čte text bez kontextu session, jako čtenář, ne jako autor; zápis mu chybí schválně. |
| Průchod jazykem a sazbou | agent typu `reader` | Totéž; odděleně, aby se drobné opravy neztratily v přestavbě. |
| Průchod rodilého mluvčího | agent typu `reader`, jen u textu v cizím jazyce | Czenglish a idiomatičnost jsou u cizího jazyka hlavní důraz; agent, který by je hledal mezi deseti dalšími věcmi, je odbude. |
| Věcná kontrola | agent typu `researcher` | Čte jako odborník na téma a smí si tvrzení ověřit na webu; zápis nemá, takže fakt sám nezmění. |
| Ověření návrhů | agent typu `reader` | Jediný úkol je návrh vyvrátit – hlavně jako možný záměr autora. |
| Třídění do pater, předložení, zápis | vlastní | Hranice pater a dávkové schválení jsou jádro skillu. |
| Čtení a zápis Google Docu | konektor Google Docs | Umí to; zápis jde jen se schválením. |
| Čtení a zápis `.docx` s revizemi a komentáři | `document-skills:docx` | Umí sledované změny, komentáře ukotvené k úseku i kontrolu, že žádná změna neprošla mimo revize. |

**Volání agentů a konektoru je implementační detail, ne rozhraní** – vyměnit se smí kdykoliv. Závazné je: tři patra a jejich hranice (u `.docx` jejich převod na revize a komentáře), že se nezmění fakt ani citace, že se nic nad první patro nezapíše bez schválení, a kontrola po zápisu.

**Zadání pro agenty drží [`agents.md`](agents.md).** Načti si ho ve chvíli, kdy agenty pouštíš.

## Zásady pro celý průběh

**Tři patra.** Patro určuje, kdo rozhoduje – ne závažnost (`~/.claude/skills/severity.md`) a ne objem práce:

| Patro | Kritérium | Co s ním |
|---|---|---|
| **1 – jednoznačné** | pravopis, gramatika, typografie s **jedinou** správnou podobou podle pravidla; a ověřeně to není záměr | oprav rovnou, bez ptaní |
| **2 – menší stylistika** | slovo nebo věta: vata, kalk, czenglish, pasivum, nominální styl, slovosled, kolokace – víc správných podob, smysl i hlas zůstávají | navrhni s doporučeným přepisem a pravidlem, schvaluje se **dávkou** |
| **3 – větší přepis** | pořadí, přestavba odstavce nebo celé stavby, škrt teze či odstavce, změna hlasu nebo rejstříku, **cokoliv, co může být záměrem nebo autorovou osobitostí** | předlož **po jednom** s variantami a doporučením; nic se neopraví samo |

**U dokumentu Wordu rozhoduje autor ve Wordu, ne v konverzaci.** Revize jde jednotlivě přijmout i odmítnout, takže schválení nahrazuje sama:

| Patro | V `.docx` |
|---|---|
| 1 | revize |
| 2 | revize; pravidlo, o které se opírá, jako komentář u ní, není-li důvod zřejmý z opravy samé |
| 3 | **komentář** u úseku s variantami a doporučením; text se nepřepíše |
| věcné pochybnosti, otázky na autora | komentář u úseku |

Hranice pater tím neslábne: co by jinde potřebovalo otázku, nesmí se v dokumentu objevit jako revize, protože přijmout všechno jedním kliknutím je ve Wordu běžné.

**Pokyn „rovnou to oprav“ se týká jen prvního patra.** Ani spěch, ani „jde to dneska ven“ nepovyšuje přestavbu nebo škrt na jednoznačnou opravu – právě tady agent bez skillu maže autorovu tezi a ptá se, až když je smazaná.

**Než opravíš cokoliv, ověř, že to není záměr.** Chybný tvar uvedený jako ukázka („ne *vyjímka*, ale *výjimka*“), přímá řeč, nářečí, hříčka, vlastní jméno, značka, název produktu. Nejde-li záměr z kontextu vyloučit, oprava jednoznačná není a jde o patro výš. Místo, které necháš kvůli záměru, jednou větou zmíň.

**Fakta jsou nedotknutelná.** Čísla, data, jména, citace, kód, cesty a cíle odkazů se nemění ani při přestavbě věty; tvrzení nesmí zmizet ani posunout smysl. Rozpor dvou údajů v textu i věcně podezřelé tvrzení je **otázka na autora**, ne oprava – i když je chyba zjevná.

**Citace si nechává svou podobu.** Slova a překlepy v doslovné citaci se nemění; co se na ní smí upravit při sazbě, drží `~/Context/Text/typography.md`, *Kde se nesází*. **Jazyková varianta textu se řídí pravidlem, ne citací:** britský pravopis v citaci nepřepíná na britštinu zbytek textu.

**Slabý signál se hlásí, jen když se nakupí.** Položka, kterou doména označuje jako slabý signál (jedno slovo typické pro strojový text, jedno abstraktum), sama o sobě nález není.

## Fáze 0 – Příprava

Společný začátek je v `~/.claude/skills/preflight.md`. **Body 1 až 3 z něj platí jen u vstupu, který je soubor v git repozitáři** – vložený text, Google Doc ani web v projektu neleží. U souboru navíc:

- **Má-li soubor necommitnuté změny**, řekni to a zeptej se, jestli je nejdřív commitnout. Zápis korektury se jinak slije s rozpracovanou prací a nepůjde vrátit samostatně.
- **Commit korektury** se řídí autocommitem projektu, ve kterém soubor leží; skill sám necommituje v cizím repozitáři bez autocommitu.

Ověř, že existuje `~/Context/Text/text.md`. Chybí-li, řekni to a skonči – bez pravidel by se korigovalo podle dojmu.

## Fáze 1 – Vstup a rozpoznání

1. **Načti text celý.** Soubor přes `Read`; `.docx` přes `document-skills:docx`; Google Doc přes `mcp__claude_ai_Google_Docs__read_doc`; web přes `WebFetch` s pokynem vrátit hlavní text doslova. **Text z webu prošel převodem**, takže drobnosti sazby (uvozovky, pomlčky, mezery) nemusí sedět s originálem – typografické nálezy z webu hlas jako nejisté. Vložený text ber z konverzace.
2. **Urči jazyk.** Smíšený text (český článek s anglickou citací) se posuzuje po úsecích, každý podle svého jazyka.
3. **Urči druh textu a kanál:** článek, newsletter, veřejná dokumentace, interní pracovní text, rozhraní, slajd, mail, příspěvek na sociální síť; publikovaný výstup, nebo zdrojový Markdown.
4. **Urči téma, obor a cílovou skupinu.** Odborný a komunitní text má vlastní slovník: termín, žargon i anglicismus, který se v oboru čtenáře běžně píše, není vada, i když by v obecném jazyce byl (`~/Context/Text/text.md`, *Stylistika*). Zavedené termíny textu zapiš do seznamu rozhodnutí v *Fázi 2*, ať je průchody nehlásí.
5. **Urči hlas:** Honzův (jeho web, `~/Context/Archive/`, podpis, první osoba v jeho tématech), firemní a neosobní, nebo cizí autor. Na hlasu stojí, které pravidla stylistiky platí (`~/Context/Text/text.md`, *Stylistika*).
6. **Vyber pravidla a načti je celá:**

   | Kdy | Co |
   |---|---|
   | vždycky | `~/Context/Text/text.md`, `~/Context/Text/phrases.md`, `~/Context/Text/typography.md` |
   | text v jiném jazyce | jeho podadresář v `~/Context/Text/` – každý jeho soubor; má přednost před bází a říká, co z ní neplatí |
   | rozhraní | `~/Context/Text/copy.md` |
   | slajd | `~/Context/Design/slides.md` |
   | Honzův hlas | `~/Context/Compose/style.md` – co je typické pro jeho hlas, není vada; jeho anti-patterny vada jsou |

   **Chybí-li pro jazyk textu podadresář**, řekni to: korigovat se dá jen podle obecné báze a typografie toho jazyka zůstane nezkontrolovaná.
7. **Ohlas rozpoznané jednou větou** – jazyk, druh, obor a cílová skupina, hlas, načtená pravidla. Je-li hlas, druh nebo cílová skupina nejistá tak, že by to změnilo platná pravidla, **zeptej se jednou otázkou** a jinak pokračuj.

## Fáze 2 – Inventář

Než se cokoliv navrhne, sepiš si do scratchpadu dvě věci. Jsou měřítkem pro *Fázi 6*, takže se nepíšou z paměti, ale z textu:

- **Inventář faktů:** každé číslo, datum, jméno, citace, odkaz a každé věcné tvrzení, jedno na řádek, doslovně.
- **Seznam rozhodnutí k dokumentu:** jazyková varianta, jak se v textu píšou jména a termíny, **oborový slovník, který se nemá opravovat**, zápis čísel a dat, oslovení. Kde se text sám se sebou rozchází, zvol podobu podle pravidla; nerozhoduje-li pravidlo, podle převažujícího výskytu – a zapiš, že to je volba.

## Fáze 3 – Průchody

Text se čte **po vrstvách shora dolů**: stavba a logika (pointa nahoře, pořadí, kostra nadpisů, návaznost odstavců, opakování), odstavec a věta (stylistika, vata, nominální styl, stopy strojového textu), u cizího jazyka idiomatičnost (co by rodilý mluvčí řekl jinak), slovo (pravopis, gramatika, kolokace), sazba. Pořadí rozhoduje o tom, co se pak provede: oprava čárky v odstavci, který se přestaví, se zahodí.

**Krátký text do 300 slov projdi sám** všemi vrstvami – panel by stál víc, než přinese. **Delší text** rozešli agentům typu `reader` paralelně podle [`agents.md`](agents.md): jeden na stavbu a styl, druhý na jazyk a sazbu, **u textu v cizím jazyce třetí jako rodilý mluvčí** na czenglish a idiomatičnost, každý s cestou k textu, seznamem pravidel z *Fáze 1*, oborem a cílovou skupinou, hlasem a seznamem rozhodnutí. Model a effort podle `~/.claude/standards/delegation.md`, *Model a effort podle úkolu* – kontrola proti doménovým znalostem.

**Věcnou kontrolu pusť vždycky**, u krátkého i dlouhého textu a v každém jazyce: jeden agent typu `researcher` podle [`agents.md`](agents.md) jako odborník na téma a cílovou skupinu z *Fáze 1*, na výchozím modelu s `high`. Text bez věcných tvrzení (báseň, pozvánka bez údajů) ji nepotřebuje – pak to řekni.

**Text předávej souborem ve scratchpadu**, ne v zadání; u vloženého textu, Docu a webu ho tam nejdřív ulož. Prefix souboru odvoď ze jména vstupu.

## Fáze 4 – Třídění a ověření

1. **Sluč nálezy** všech průchodů a odstraň duplicity. Nález ve stejném úseku, který leží pod návrhem třetího patra, si poznamenej jako závislý – platí, jen když se přestavba odmítne.
2. **Zařaď každý nález do patra** podle *Zásad pro celý průběh*. Agent patro navrhuje, rozhoduješ ty; při váhání vždycky vyšší patro.
3. **Ověř návrhy druhého a třetího patra i nálezy věcné kontroly** u delšího textu jedním agentem typu `reader` podle [`agents.md`](agents.md), na nejsilnějším modelu s `xhigh` – ověřování nálezů. Jeho úkol je návrh vyvrátit: je to záměr, mění to smysl nebo fakt, porušuje to hlas, je původní znění podle pravidla v pořádku? Co ověření nepřežije, se nepředkládá. U krátkého textu projdi tytéž otázky sám.
4. **U prvního patra ověř záměr sám** – každý nález proti okolní větě. Ověřovatel na ně nejde: jednoznačná oprava se nevyvrací, jen se zkontroluje, že je opravdu jednoznačná.

## Fáze 5 – Předložení

**U `.docx` se fáze přeskakuje** – nic se nepředkládá, všechna patra jdou do dokumentu v *Fázi 6*.

**Pořadí: třetí patro, pak druhé.** Přestavba mění úseky, nad kterými stojí menší návrhy, a dávka předložená před ní by se schvalovala naslepo.

**Třetí patro po jednom** přes `AskUserQuestion`. Před otázkou v textu: kterého místa se týká (doslovná citace úseku), co je na něm dnes a proč to nestačí, s odkazem na pravidlo. Volby jsou podoby přepisu – doporučená první – a vždycky i **ponechat původní**, protože tady je zachování autorova znění obhajitelná podoba řešení, ne odklad. Rozhodnutí si zapisuj, než položíš další otázku.

**Druhé patro dávkou**, jako číslovaný seznam v běžném Markdownu:

```
**Menší úpravy ke schválení** – odpověz „vše“, nebo vyjmenuj čísla, která nechceš.

1. „<původní úsek>“ → „<návrh>“ – <pravidlo, jednou větou>
2. …
```

Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo – `~/.claude/standards/rules.md`, *Styl odpovědí*. Odpověď „vše kromě 3 a 7“ je úplné rozhodnutí. Ptá-li se uživatel k položce, vysvětli ji a dávku znovu nepředkládej celou – jen to, co zůstalo otevřené.

**První patro se nepředkládá** – provede se a vypíše v závěru.

## Fáze 6 – Zápis a kontrola

1. **Sestav výsledné znění**: schválené přestavby, schválené menší úpravy, všechny opravy prvního patra, které neleží v zahozeném úseku. U `.docx` všechna patra podle tabulky v *Zásadách pro celý průběh*.
2. **Zapiš podle vstupu:**

   | Vstup | Zápis |
   |---|---|
   | soubor | `Edit` po úsecích, ne přepis celého souboru – diff pak ukáže jen změny |
   | vložený text | celé opravené znění do odpovědi |
   | Google Doc | **nejdřív vypiš seznam změn a nech si zápis potvrdit** – Doc není v gitu a zápis nejde vrátit diffem. Pak `mcp__claude_ai_Google_Docs__update_doc` po úsecích. Neumí-li nástroj cílený zápis, neřeš to přepisem celého dokumentu – řekni to a dej opravené znění k ručnímu vložení |
   | web | nezapisuje se; opravené znění do odpovědi |
   | `.docx` | přes `document-skills:docx` přímo do dokumentu – každá změna je revize, takže jde odmítnout. Kontrakt: revize i komentáře pod autorem `Claude`; komentář ukotvený k úseku, kterého se týká; revize a komentáře, které v dokumentu už jsou, zůstanou beze změny; formátování textu se zachová. **Před zápisem si ulož kopii originálu do scratchpadu** a po zápisu pusť kontrolu, že každá změna je revize pod autorem `Claude`; neprojde-li, vrať originál a řekni to – změna mimo revize je v přijatém zobrazení neviditelná |

3. **Přečti výsledek znovu celý** – u `.docx` znění s přijatými revizemi – a ověř:
   - **inventář faktů sedí** – každá položka je ve výsledku a znamená totéž; nesedí-li, oprav to a řekni to,
   - **žádná nová vada** – zdvojený údaj po přestavbě, rozbitá návaznost, typografie a pravopis nově napsaných vět,
   - **seznam rozhodnutí platí** v celém textu.

   Najdeš-li vadu, kterou zanesla korektura sama, oprav ji – je to první patro.

## Časté chyby

- **„Rovnou oprav“ se vezme jako souhlas se vším.** Škrt teze, závěru a přepis hlasu se provedou, otázky přijdou až po nich. Nad prvním patrem se bez schválení nezapisuje nikdy.
- **Záměrná ukázka se škrtne jako odbočka.** „S tématem nesouvisí“ je úsudek o obsahu – patří do třetího patra, ne do opravy.
- **Citace přepne jazykovou variantu celého textu.** Britský pravopis v citovaném regulátorovi neznamená britský text.
- **Přestavba zdvojí údaj.** Pointa vytažená nahoru zůstane i na původním místě; bez kontroly po zápisu to nikdo neuvidí.
- **Idiomatičtější znamená jiný smysl.** *I can say that* není *in my experience* – přepis kvůli plynulosti nesmí posunout tvrzení.

## Fáze 7 – Závěr

```
## Korektura hotová

- **Text:** <soubor / Google Doc / web / vložený text> – <jazyk>, <druh>, <obor a cílová skupina>, <hlas>
- **Pravidla:** <načtené soubory>
- **Spotřeba:** [N agentů: X průchodů, Y ověřovatelů · na jakém modelu a effortu]

**Opraveno rovnou** – <počet>
- „<původně>“ → „<opraveno>“ – <pravidlo>

**Schválené úpravy** – <počet menších, počet přestaveb; u `.docx` místo toho: <N> revizí, <N> komentářů k rozhodnutí ve Wordu>

**Ponecháno záměrně**
- „<úsek>“ – <proč: ukázka, citace, oborový slovník, hlas>

**Věcné pochybnosti**
- „<tvrzení>“ – <co je podle oboru jinak> – <zdroj, nebo „odborný úsudek, neověřeno“>

**Otázky na autora**
- <rozpor údajů, chybějící doklad – co skill nerozhodne, nebo „žádné“>

**Nezkontrolováno**
- <co a proč, nebo „nic“>
```

Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo – `~/.claude/standards/rules.md`, *Styl odpovědí*. Řádek *Spotřeba* jen tehdy, když běželi agenti.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Text je opravený a ověřený, můžeš ho použít.` – u `.docx`: `Korektura je v dokumentu jako revize a komentáře a je ověřená, můžeš ji projít ve Wordu.`
- `Text opravený není – brání tomu: <konkrétní seznam>.`
