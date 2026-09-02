---
name: oponent
description: Skill se použije, když uživatel zadá "/oponent", nebo chce nezávislý oponentský posudek na dokument, který spolu psali – strategii, pozicování, PRD, koncepci, cenotvorbu, datový model, analytickou dokumentaci. Pohled čerstvýma očima z několika úhlů: co nedává smysl, co si odporuje, co nebude fungovat, co chybí.
argument-hint: [dokument]
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, WebSearch, WebFetch]
---

# Oponent

## Co skill dělá

Uživatel má hotový nebo rozpracovaný dokument, na kterém jste spolu dlouho pracovali. Právě proto na něj **nemáš nezávislý pohled** – spoluautor nevidí, co v dokumentu chybí, protože to má v hlavě, a nevidí, co je slabé, protože si to sám odsouhlasil.

Skill proto pošle na dokument **subagenty bez kontextu téhle session**, každého z jiného úhlu, a jejich nálezy s uživatelem probere jeden po druhém.

V ose *Životního cyklu práce* (`~/.claude/RULES.md`) je to **třetí krok zakládání**: navazuje na `/specify` a předává na `/breakdown`. Do osy patří proto, že jinak návrh neměří nikdo – `/review` ověřuje kód proti specifikaci, ale samotnou specifikaci nikdo proti ničemu, takže vada v ní projde celou osou jako korektní. Přeskakuje se stejným pravidlem jako každý jiný krok: drobná změna uvnitř navrženého systému posudek nepotřebuje, nový systém nebo nový podsystém ano – a přeskočení se řekne nahlas i s důvodem.

## Co skill nedělá

- **Není to kontrola kódu.** Na kód je `/review`.
- **Není to kontrola proti standardům.** Na soulad s `~/Dev/context/*` je `/review`.
- **Není to audit vnitřní konzistence projektu.** Na to je `/consistency`. Oponent se ptá „je to dobře vymyšlené?“, ne „sedí to na sebe?“.
- **Nic sám nemění.** Výchozí režim je diskuze. Změny až po schválení jednotlivých nálezů.
- **Nechválí.** Věci, které jsou v pořádku, se nevypisují.

**Vědomé volby, ať je nikdo neřeší znovu** (`~/.claude/RULES.md`, *Zapiš i to, co vědomě nemáš*):

- **Úhel *Vnitřní rozpor* se s `/consistency` částečně překrývá a je to přijatá cena.** Ano, „sedí čísla a výčty“ najde i `/consistency`. Ale oponentura běží i nad dokumentem, který `/consistency` nevidí (cizí podklad, text mimo projekt), a rozpor mezi dvěma tvrzeními ve věci samé je jiná práce než rozpor mezi součtem a tabulkou. Nález se vrací při každé oponentuře skillu; není to omyl, je to volba.
- **Katalog se jednou vědomě zmenšil z devatenácti na sedmnáct** a ty úhly nepatří zpátky: *Hraniční případy* splynuly s *Co chybí* (byl to týž generátor okrajů dvakrát), *Skeptik* s *Předpoklady* (tatáž otázka zprava a zleva) a *Technická proveditelnost* s *Daty* (měla nejchudší zadání a nad datovým modelem sahala po témže). Navrhne-li je někdo znovu jako „chybějící pokrytí“, tohle je odpověď.
- **Katalog nemá strop na počet úhlů.** Brzdou je jen kontrola překryvu při přidávání (viz Fáze 1). Tvrdý strop by nutil vyhodit úhel pokaždé, když nějaký skutečně chybí – a chybějící úhel nevrátí nula nálezů, ale neexistenci.

## Vztah k ostatním skillům

| Otázka | Skill |
|---|---|
| Je ten kód správně? | `/review` |
| Odpovídá to mým doménovým standardům? | `/review` |
| Nesedí si něco v projektu navzájem? | `/consistency` |
| **Je to vůbec dobře vymyšlené a bude to fungovat?** | **`/oponent`** |
| Je všechno ze session zapsané? | `/cleanup` |

------

## Fáze 0 – Co se oponuje

**Předmět posudku.** Uživatel ho může zadat jako argument (`/oponent docs/requirements.md`, `/oponent 01 až 04`, `/oponent pozicování`). Když ho nezadá, **nabídni mu, co jsi našel** – projdi projekt, vypiš kandidáty (dokumenty, na kterých se v poslední době pracovalo) a nech ho vybrat přes `AskUserQuestion`.

**Nejdřív se podívej, jestli neexistuje `.claude/run/oponent.json`** – přerušený běh. Vzniká na konci Fáze 4; nabídni navázání dřív, než začneš cokoliv počítat znovu.

**Pak zjisti, jestli nad tímhle předmětem oponentura už neběžela** – `docs/done.md`, sekce `## Průchody osou`. Najdeš-li záznam, přečti z něj panel úhlů a počty nálezů: Fáze 1 z toho vyjde při volbě úhlů a Fáze 6 podle toho pozná, jestli smí srovnávat počty. Porovnej i hash s aktuálním – `git log --oneline <zapsaný hash>..HEAD` ukáže, co se od té doby změnilo.

**Zkontroluj, že to má smysl oponovat:**

- **Je to kód?** → přesměruj na `/review` a zastav se.
- **Je to rozpracované torzo?** → zeptej se, jestli má smysl oponovat teď, nebo počkat. Posudek na kostru vygeneruje hlavně nálezy „chybí obsah“, což uživatel ví.
- **Je toho moc?** Nad zhruba pět dokumentů nebo řádově stovky kB se posudek rozmělní. Zeptej se, co je jádro, a oponuj to.

**Načti kontext, který posudek potřebuje:** projektový `CLAUDE.md`, `docs/rules.md` (principy, proti kterým se v projektu rozhoduje) a `docs/decisions.md` (co už bylo rozhodnuto a proč). Bez toho subagenti navrhnou znovu to, co už bylo vědomě zamítnuto – a to je nejotravnější druh oponentury.

**Na soubory ale nespoléhej.** Oponentura se často pouští hned po `/specify`, tedy v kroku 2 osy – kdežto rozhodnutí z debriefu zapisuje `/cleanup` až v kroku 7. `decisions.md` je v tu chvíli skoro prázdný, ačkoliv se v téhle session vědomě zamítla spousta věcí. **Projdi proto session a to, co jste zavrhli, vypiš do zadání oponentů** jako samostatný blok *Vědomě zamítnuté* – i s důvodem, ne jen výčtem. Bez toho první běh předloží nálezy, které umíš vyvrátit z hlavy, a druhý už nespustíš.

**Nemá-li projekt `docs/`** (konfigurační repozitář, samostatný dokument mimo projekt, text v knowledge base), řekni to nahlas a veď posudek bez nich: kontextem je pak projektový `CLAUDE.md` a příslušná doména v `~/Dev/context/`, a přijatá i zamítnutá rozhodnutí jdou tam, kam patří v tom projektu – ne do založeného `docs/`.

------

## Fáze 1 – Volba úhlů pohledu

**Nepouštěj stejné kritiky.** Redundantní subagenti najdou tolikrát totéž, kolik jich pustíš. Diverzita úhlů chytá selhání, která opakování nechytí.

Vyber **čtyři až pět úhlů** z katalogu níž podle sloupce *Spouštěč*. Je to **vlastnost dokumentu, ne jeho typ** – „PRD“ nebo „cenotvorba“ by propustily skoro celý katalog a filtr by nefiltroval; „slibuje výsledek“ nebo „sbírají se údaje o lidech“ se dá ověřit v textu, který máš před sebou. Výběr **předlož uživateli přes `AskUserQuestion`** předtím, než kohokoliv pustíš – volby *Pustit tak, jak je* / *Vyměnit jeden úhel* / *Vybrat panel znovu*. **Na odpověď se čeká**; do té doby žádný subagent neběží. Prostý výpis nestačí: další odstavec velí pustit panel jedním voláním, takže by se uživatel k výměně dostal až ve chvíli, kdy čtyři agenti na `xhigh` už pracují (`~/.claude/RULES.md`, *Ptej se postupně*).

**Vlastní úhel** si vymysli, jen když **žádný z katalogu nepokrývá** to, co je na dokumentu specifické. Pak ale: napiš, který katalogový úhel byl nejbližší a čím se od něj tvůj liší; napiš mu **otázky ve stejném tvaru jako v katalogu** (bez nich dorazí k subagentovi holý název a ten pak najde cokoliv); zařaď ho mezi metody, nebo domény. Osvědčí-li se, **navrhni ho doplnit do katalogu** – jinak se poznatek ztratí a příště se vymýšlí znovu a jinak. Před přidáním ale **porovnej jeho otázky se sloupcem *Ptá se* u všech stávajících úhlů**: sdílí-li s některým víc než jednu otázku, do katalogu nepatří jako nový řádek, ale jako zúžení nebo doplněk toho stávajícího (`~/.claude/RULES.md`, *Detekce konfliktů před přidáním*). Katalog roste snadno a nic ho samo nezmenšuje. Úhel, který jde formulovat jako zúžení existujícího na doménu (*Právo → GDPR a consent*), vlastní úhel není.

Sloupec *Web* říká, který úhel dostane ve Fázi 2 svolení hledat zvenku; ostatním se to zakazuje, ať neutíkají od dokumentu.

**Metody – jak se dívat.** Dají se přiložit na jakýkoliv dokument; samy o sobě ale nemají věcnou oporu, proto se metodickému úhlu v zadání vždy určí doména, na kterou se má obořit (*Hraniční případy cenového modelu*, *Pre-mortem uvedení kurzu*).

| Úhel | Ptá se | Spouštěč | Web |
|---|---|---|---|
| **Vnitřní rozpor** | Tvrdí dokument někde něco, co jinde popírá? Sedí čísla, výčty a souhrny s obsahem? Nezůstal tam zbytek po zrušeném konceptu? | dokument vznikal po částech nebo prošel revizemi – je kde nechat zbytek po zrušeném konceptu |  |
| **Co chybí** | Ne co je špatně, ale co v dokumentu vůbec není a co na jeho okrajích nemá odpověď. **(1)** Vypiš hlavní entity, kroky a pravidla dokumentu a u každého se zeptej, co když nenastane vůbec, nastane víckrát, jen zčásti, spolu s něčím dalším, obráceně, nebo místo něj něco jiného – souběh dvou slev, přechod na vyšší tarif v půlce období, dvojí nárok téhož zákazníka, zrušení uprostřed. Platí to pro pravidlo obchodní a procesní stejně jako pro vstup programu. **(2)** Hlaš jen to, bez čeho podle dokumentu nejde jednat ani rozhodnout: nepojmenovaný vlastník, chybějící kritérium, scénář bez odpovědi. Neptej se na chování kódu, ale na to, jestli dokument na ten případ dává odpověď – a jestli dává jen jednu. Nevypisuj chybějící kapitoly a sekce. | vždy – povinný |  |
| **Předpoklady a argumentace** | Plyne závěr z toho, co mu předchází? Vypiš předpoklady, na kterých dokument mlčky stojí a nikde je nepojmenovává – co musí platit, aby závěr platil? U každého: jak se pozná, že neplatí, a co z dokumentu padá s ním. Je tvrzení podané jako fakt doopravdy fakt? Nesahej na čísla, právo, data ani technologii – ty mají vlastní úhly. | dokument něco tvrdí o světě, o lidech nebo o budoucnosti a opírá o to závěr; a jako záložní volba, když nesedí žádná doména |  |
| **Pre-mortem** | Je za osmnáct měsíců a tohle prokazatelně selhalo. Napiš, co se stalo – konkrétní sled událostí, ne obavu. Který předpoklad padl první? Jako jediný úhel smíš skládat příběh napříč doménami: nález, který leží na rozhraní dvou jiných úhlů, jinak nemá majitele. | z dokumentu se bude něco realizovat a stojí to na jednom hlavním scénáři |  |
| **Alternativy a řez** | Splnil by týž cíl jednodušší nebo úplně jiný postup? Které varianty autor zvažoval a proč je zamítl – je to zdůvodnění v dokumentu, nebo jen v jeho hlavě? Co se stane, když se nezmění nic? Která část jde vyškrtnout, aniž zbytek přestane dávat smysl? | dokument navrhuje řešení a nejmenuje varianty, které autor zvažoval a zavrhl |  |
| **Cíl a měřitelnost** | Je napsané, čeho to má dosáhnout? Podle čeho se za rok pozná, že to vyšlo, a podle čeho, že ne? Má cíl číslo, práh a termín, nebo je to próza? Co je vědomě mimo rozsah – a je to napsané, nebo se to jen předpokládá? | dokument si klade cíl nebo slibuje výsledek |  |
| **Zneužití** | Kdo má motiv to obejít – uživatel, konkurent, robot, insider? Co se dá vytěžit z mezery mezi tím, co dokument slibuje, a tím, co vymáhá? Co jde přečíst, změnit nebo získat zadarmo, aniž na to má někdo nárok? Kde dokument předpokládá, že se aktér chová slušně? | jsou ve hře peníze, osobní údaje, přihlašování nebo cizí vstup |  |
| **Reverzibilita** | Které rozhodnutí jde vzít zpátky a které ne? Co stojí návrat – v penězích, v datech, v důvěře? Ví dokument sám o sobě, že je někde jednosměrný? Existuje varianta, která tutéž věc otestuje vratně? | zakládá schéma, jméno, závazek nebo veřejný slib – něco, co se pak těžko bere zpět |  |
| **Čtenář bez kontextu** | Přečti dokument jako člověk, který u jeho vzniku nebyl. Který termín není nikde definovaný nebo mění význam? Které rozhodnutí je zapsané bez důvodu, takže ho nikdo netroufne změnit? Kde by dva čtenáři odešli s jiným zadáním? Na co dokument odkazuje, aniž to jmenuje? | dokument bude někdo vykonávat bez autorů – člověk i agent |  |

**Domény – na co se dívat.** Nesou znalost oboru, ale bez metody sbírají povrch.

| Úhel | Ptá se | Spouštěč | Web |
|---|---|---|---|
| **Ekonomika provozu** | Sedí čísla? Break-even, cena, marže, kapacita, náklady na provoz. Kdo to bude reálně dělat, jak často a co se stane, když to neudělá? Co vyžaduje ruční zásah? Co se rozbije při desetinásobku a co při desetině? | jsou v něm čísla, ceny, kapacity nebo opakovaná ruční práce | ✔ |
| **Osobní údaje a souhlas** | Co se sbírá, na jakém právním základu a jak dlouho se to drží? Co dokument slibuje uživateli a co ve skutečnosti dělá? Jde výmaz provést, aniž se rozpadne zbytek? | sbírají se údaje o lidech | ✔ |
| **Závazky vůči druhé straně** | Spotřebitelské právo, smluvní závazky, daně, autorská práva. Co je napsané tak, že to nejde dodržet? Co slibuje víc, než na co má autor nárok nebo kapacitu? | dokument něco slibuje protistraně – zákazníkovi, klientovi, dodavateli | ✔ |
| **Data a proveditelnost** | Dá se to postavit tak, jak je to popsané? Co je klíč záznamu a co se stane, když se změní? Kde je pro každý údaj zdroj pravdy a kdo ho smí přepsat? Co se děje s duplicitou, s historií a se smazáním? Jak se do nového modelu dostanou stará data a jak se z něj dá vycouvat? Kde je v tom skryté technické riziko – co dokument popisuje jako samozřejmé, a přitom to nikdo nepostavil? | popisuje záznamy a jejich klíče, nebo něco, co se má postavit | ✔ |
| **Nepřítomní dotčení** | Koho ještě se to dotkne, i když v dokumentu není? Kdo to musí odsouhlasit a byl u zadání? Komu to přidá práci a kdo se tomu bude bránit – a proč právem? Kdo si po zavedení pohorší oproti dnešku? Kolik lidí to umí a co když ten jeden vypadne? | provedení závisí na někom, kdo u zadání nebyl, nebo se tím někomu mění zaběhnutý postup či cena |  |
| **Závislosti a datum spotřeby** | Na čem cizím to stojí – služba, sazba, právní úprava, nástroj, jeden člověk? Co se stane, když to zdraží, změní podmínky nebo zmizí? Co v dokumentu má datum spotřeby a ví se o tom? Jak vypadá druhý rok provozu? | stojí to na cizí službě, ceníku, sazbě nebo předpisu | ✔ |
| **Konkurence a trh** | Existuje to už? Čím se to liší? Proč by si zákazník vybral tohle, a ne cizí nabídku nebo to, co používá dneska? Obstojí ta odlišnost, když si ji ověří? (Jestli to má vůbec smysl dělat, řeší *Alternativy a řez* – tebe zajímá volba zákazníka, ne náklad příležitosti autora.) | něco se má prodávat nebo vymezovat vůči alternativám | ✔ |
| **Cílová skupina** | Čte to očima persony, které se to týká – a ta nezná alternativy, zná jen tenhle text. Rozumí tomu? Věří tomu? Co ji odradí, co v tom nenajde, kde přestane číst? (Srovnání s tím, co nabízí někdo jiný, nech *Konkurenci a trhu* – ten na to má rešerši, ty ne.) | text má někoho oslovit, přesvědčit nebo mu něco vysvětlit |  |

**Pravidla výběru:**

- Úhel *Co chybí* ber jako **povinný**, ať je dokument jakýkoliv. Druhý povinný úhel schválně nemáme: dva pevné sloty ze čtyř by z volby podle povahy dokumentu udělaly ozdobu.
- Vyber **aspoň jednu položku z každého bloku**. Samé domény dají audit a nula oponentur; samé metody obecné kritiky bez věcné opory.
- **Úhly nerozšiřuj, aby jich stačilo pustit míň.** Vypadá to lákavě – širší úhel přece pokryje víc –, jenže kapacitu neurčuje šířka zadání, ale výstup agenta: ten vrátí pět až deset nálezů, ať má zadání úzké nebo široké. Rozšířením se počet nálezů nezvedne, jen se rozptýlí jejich původ, a přibude riziko úhlu, který „najde cokoliv“. Chybí-li ti pokrytí, přidej úhel, nebo rozšiř jeho *Spouštěč* – nerozmazávej úhel, který máš.
- Metodický úhel pouštěj **vždy s určenou doménou** – vypiš ji do jeho zadání. Metoda bez domény je slepá.
- **Kolik jich pustit podle rozsahu předmětu:** čtyři u jednoho dokumentu zhruba do 15 kB, pět nad tím nebo když je dokumentů víc. Je-li předmět velký (blíží se hranici z Fáze 0), dělí se **úhel × podmnožina dokumentů**, ne jen úhel – jinak čte každý agent celý objem a dělba škáluje jen jedním směrem.
- **Běžela-li už oponentura nad tímhle předmětem** (Fáze 0 to zjistila z `docs/done.md`), **začni jejím panelem**. Nález, který se vrátí ve stejném úhlu, znamená, že se neopravil; nález, který zmizel s vyměněným úhlem, neznamená nic. Vyměnit úhel smíš, ale řekni, který a proč – Fáze 6 pak počty nesrovnává.
- **Sedí-li spouštěč na víc úhlů, než máš slotů**, ber ty, kde by chyba stála nejvíc – ne ty, kde se nález hledá nejsnáz.
- **Volbu dolož.** U každého zvoleného úhlu napiš jednou větou, co konkrétně v dokumentu tě k němu vedlo, a jmenuj **jeden úhel, který jsi vědomě nevzal, a proč**. Nevybraný úhel totiž nevrátí nula nálezů, ale neexistenci – a ta neprojde žádným počítadlem ve Fázi 4 ani ve verdiktu. Volbu přitom dělá ten, kdo dokument spoluautorsky psal, takže je to jediné místo, kde má jeho slepota volnou ruku (`~/.claude/RULES.md`, *Zapiš i to, co vědomě nemáš*).

------

## Fáze 2 – Nezávislé posudky

Pusť subagenty **paralelně, jedním voláním s víc tool calls**. Každý dostane vlastní úhel a **žádný kontext z téhle session** – to je celý smysl.

**Nejsilnější model, `xhigh`** (Volba modelu a effortu podle `~/.claude/RULES.md`, *Model a effort podle úkolu*.) Oponentura je verifikace, ne sběr: slabý model námitku nevymyslí ani neobhájí, jen zdvořile přizvukuje tomu, co má před sebou – a posudek, který všechno schválí, je horší než žádný, protože dodá falešnou jistotu.

Zadání pro každého (doplň úhel, cesty a projektový kontext):

```
Jsi nezávislý oponent. Nemáš žádný kontext z předchozích rozhovorů – máš jen ty soubory,
které si přečteš. Autor dokumentu tě neslyší, takže nemá smysl být ohleduplný.

DOKUMENT: <absolutní cesty>
KONTEXT PROJEKTU (přečti, ale neoponuj to): <CLAUDE.md, docs/rules.md, docs/decisions.md>
VĚDOMĚ ZAMÍTNUTÉ V TÉHLE PRÁCI (nenavrhuj znovu bez nového argumentu): <výčet i s důvody>

TVŮJ ÚHEL POHLEDU: <úhel a jeho otázky ze sloupce *Ptá se*>

Přečti dokument celý a hledej výhradně ze svého úhlu. Ostatní úhly pokrývají jiní
oponenti – nepřebíhej k nim.

U KAŽDÉHO NÁLEZU UVEĎ:
- **Kde** – soubor a sekce, ideálně citace věty, které se to týká
- **Co** – jednou větou, co je špatně
- **Proč to vadí** – konkrétní důsledek, ne obecná obava. „Nebude to škálovat“ je nic;
  „při 20 000 účastnících vyjde ruční párování na 300 hodin práce“ je nález.
- **Návrh** – dvě až tři konkrétní varianty řešení, ne jedna. Nemáš-li řešení, řekni to
  a označ nález jako otázku k rozhodnutí.
- **Závažnost** – KRITICKÉ / STŘEDNÍ / KOSMETICKÉ, stejná škála jako v `/review` a `/consistency`, ať jdou nálezy z různých skillů porovnat. U oponentury se čte jako síla námitky: **KRITICKÉ** boří předpoklad, na kterém dokument stojí; **STŘEDNÍ** mění závěr nebo rozsah; **KOSMETICKÉ** zpřesňuje.

PRAVIDLA:
- Co je v pořádku, nepiš. Žádné shrnutí kladů, žádné „jinak je to dobře promyšlené“.
- Nenavrhuj to, co je v docs/decisions.md nebo v bloku VĚDOMĚ ZAMÍTNUTÉ výš už zavržené. Přečti si obojí nejdřív.
  Výjimka: myslíš-li si, že to rozhodnutí bylo chybné, řekni to výslovně jako revizi
  rozhodnutí a zdůvodni, který jeho předpoklad neplatí.
- Neopírej nález o neověřené tvrzení. Stojí-li na faktu, ověř ho.
- Nešetři kritikou. Ale kritizuj dokument, ne autora.
- Nenavrhuj přeformulování textu kvůli stylu – od toho tu nejsi.

Do žádného souboru nezapisuj.
```

**Volitelně rešerše.** Úhlu, který má v katalogu ve sloupci *Web* ✔, dej výslovné svolení hledat na webu. U ostatních to zakaž, ať neutíkají od dokumentu.

------

## Fáze 3 – Ověření nálezů

**Nálezy z panelu nejsou závěry, ale tvrzení.** Oponent bez kontextu vyrobí i nález, který stojí na tom, co nemohl vědět – a nález, který nevyrobí nic, vypadá jako selhání běhu, takže tlak na produkci je vestavěný. Kdyby se falešné vyřazovaly až v konsolidaci, dělal by to spoluautor, tedy ten jediný aktér, jehož slepotu má celý skill obcházet. To je přesně ten tichý filtr, který si Fáze 4 zakazuje – jenže bez téhle fáze nemá čím ho nahradit.

**Deduplikuj ještě před ověřením**, ne až po něm: tři ověřovatelé na jednu věc jsou trojnásobná cena za tutéž odpověď. **Dva nálezy jsou tentýž**, když míří na totéž místo dokumentu a navrhují změnit touž věc – formulace i závažnost se lišit můžou. Sloučený nález si ponech v obou zněních a poznamenej, které úhly ho našly; Fáze 4 s tím dál pracuje jako se signálem závažnosti.

Na každý nález se závažností **KRITICKÉ a STŘEDNÍ** pošli **samostatného ověřovatele** – paralelně, v čerstvém kontextu, který nevidí ani panel, ani tvou konverzaci. **Nejsilnější model**, i u nálezu z levného úhlu: slabý ověřovatel nález nepotvrdí ani nevyvrátí, jen přizvukuje tomu, co má před sebou, a z ověření se stane razítko. (Effort mu předepsat nejde – `Agent` bere parametr `model`, ale ne `effort`. Proč a co by to zavřelo, stojí v `~/.claude/skills/review/SKILL.md`, *Fáze 3*; neopisuju to sem podruhé.)

**Strop na počet ověřovatelů: nejvýš 12 na běh.** Bez něj roste nejdražší část běhu lineárně s počtem nálezů a panel pěti úhlů vrátí klidně třicet nálezů, tedy třicet agentů na nejsilnějším modelu. Přes strop se ověřují **nejdřív všechny KRITICKÉ**, teprve pak STŘEDNÍ; co se nevejde, jde do Fáze 5 označené jako **`neověřeno`** a spočítá se v souhrnu. Tiché vynechání ne – neověřený nález se od ověřeného musí poznat. (Strop je nižší než v `/review`, protože tam ho odlehčuje deterministická vrstva, která část nálezů odčerpá bez ověřování; tady žádná není.)

**Ověřovatel má tentýž kontext jako oponenti** – to není jeho výhoda a nedělej z toho výhodu. Rozdíl je jinde: ověřovatel **nemá zadaný úhel**, a tím pádem ani tlak vrátit nález. Oponent, který ze svého úhlu nic nenajde, vypadá jako selhání běhu; ověřovatel, který nález vyvrátí, odvedl práci. Ta asymetrie je celý mechanismus, ne přístup k souborům.

```
Ověřuješ jedno tvrzení nezávislého oponenta. Nemáš kontext z předchozích rozhovorů.

DOKUMENT: <absolutní cesty>
KONTEXT PROJEKTU: <CLAUDE.md, docs/rules.md, docs/decisions.md>
VĚDOMĚ ZAMÍTNUTÉ V TÉHLE PRÁCI: <výčet i s důvody>

NÁLEZ K OVĚŘENÍ: <kde, co, proč to vadí, návrh, závažnost>

Tvůj úkol není nález potvrdit, ale pokusit se ho vyvrátit. Ptej se:
- Stojí na tom, co v dokumentu doopravdy je? Ověř citaci.
- Neřeší to dokument někde jinde, kde se oponent nedíval?
- Neplyne z kontextu projektu, že to tak je schválně?
- Je důsledek doložený, nebo je to obecná obava? („Nebude to škálovat“ je nic.)
- Sedí navržená závažnost, nebo je nafouknutá?

Vrať: POTVRZENO / VYVRÁCENO / PŘEKVALIFIKOVÁNO NA <závažnost>, jednou větou proč,
a u vyvráceného doklad – citaci z dokumentu nebo kontextu, která ho boří.

Do žádného souboru nezapisuj.
```

**KOSMETICKÉ nálezy se neověřují** – ne proto, že by ověření bylo drahé (stojí strojový čas), ale proto, že se ani nevypořádávají jednotlivě: jdou ve Fázi 5 jedním blokem, takže na nich nestojí žádné rozhodnutí, které by ověření chránilo. **Vyvrácené zahoď a spočítej je do souhrnu**; kolik jich bylo, se říká nahlas, ne potichu.

------

## Fáze 4 – Konsolidace

Než cokoliv předložíš, nálezy **zpracuj**:

1. **Duplicity už jsou sloučené** – dedup proběhl před ověřením (Fáze 3). Zůstává jen poznamenat u nálezu, že ho našli dva oponenti z různých úhlů; je to signál závažnosti.
2. **Vyvrácené nálezy vyřadil ověřovatel**, ne ty. Sám nefiltruj: nález, u kterého máš pochybnost, ale ověřením prošel, předlož s poznámkou. Tichý filtr je přesně to, co má tenhle skill obcházet, a spoluautor je ten poslední, kdo ho má dělat.
3. **Vyřaď už rozhodnuté.** Nález, který navrhuje zamítnutou variantu bez nového argumentu, zahoď a **řekni, kolik jsi jich zahodil a proč** – ne potichu.
4. **Seřaď podle závažnosti**, ne podle pořadí v dokumentu.
5. **Vypiš přehled** – všechny nálezy jednou větou, očíslované, se závažností. Uživatel musí vidět, co ho čeká, než se ho začneš ptát.

### Ověřený seznam zapiš na disk, než půjdeš dál

Hotovou frontu ulož do **`.claude/run/oponent.json`** (`~/Dev/context/structure/structure.md`, *Běhový stav skillů*; adresář patří do `.gitignore`). Formát: `{"created": "<datum a čas>", "predmet": [...], "uhly": [...], "nalezy": [{...nález..., "overeno": true/false, "status": "open"}]}`.

**Proč to není zdržení:** tenhle seznam je nejdražší artefakt celého běhu – stojí panel i ověřovatele na nejsilnějším modelu. Fáze 5 s ním pak dlouze interaguje **v hlavní session**, tedy přesně tam, kde kontext dochází nejrychleji, protože do něj předtím natekly výstupy všech agentů. Bez zápisu znamená kompaktace uprostřed průchodu, že se celý běh platí znovu.

**Na startu skillu** (Fáze 0) se proto podívej, jestli `.claude/run/oponent.json` už neexistuje. Existuje-li, **nabídni navázání** místo nového běhu – a řekni, kolik nálezů v něm zbývá nevypořádaných. Změnil-li se od té doby oponovaný dokument, řekni to a zeptej se: část nálezů může být neaktuální.

**Průběžně do něj zapisuj stav** každého nálezu (`prijato`, `zamitnuto`, `odlozeno`, `open`), jak jimi procházíš. Po dokončení Fáze 6 soubor smaž.

Panel je v tom souboru jen po dobu běhu; **trvale přežije v řádku, který Fáze 6 zapisuje do `docs/done.md`** – z něj vychází příští oponentura při volbě úhlů.

------

## Fáze 5 – Průchod nálezy

Podle `~/.claude/RULES.md` (*Ptej se postupně, ne všechno najednou*) projdi nálezy **jeden po druhém**, od nejzávažnějšího. **Jednotlivě jen KRITICKÉ a STŘEDNÍ** – kosmetické jdou nakonec jedním blokem (viz níž).

**KOSMETICKÉ nálezy neprocházej po jednom.** Vypiš je naráz jako očíslovaný seznam a zeptej se jedním voláním: *Zapracovat všechny* / *Projít po jednom* / *Zahodit všechny* / *Vrátit se k tomu později*. Dialog na každý z nich zvlášť stojí to nejdražší v celém běhu – tvoje rozhodnutí – a kupuje za něj zpřesnění. Neprošly navíc ověřením (Fáze 3), takže by se za ně platilo rozhodování bez protistrany. (Bez ověření jdou dál i nálezy nad stropem – ty se ale procházejí jednotlivě, protože jsou závažné; jen se u nich řekne, že ověřené nejsou.)

U každého nejdřív vypiš:

```
---
[N/celkem] 🔴/🟡/🔵 NÁZEV NÁLEZU
Našel: <úhel, případně „2 oponenti nezávisle“>

Kde: <soubor, sekce, citace>
Co: <jednou větou>
Proč to vadí: <konkrétní důsledek>

Varianty řešení:
A) <…> – důsledek
B) <…> – důsledek
C) Nechat být – <proč to může být v pořádku>

Doporučuji: <jedna z nich a proč>
```

Pak se zeptej **přes `AskUserQuestion`** – jedno volání na jeden nález, `header` `Nález N/celkem`, volby jsou **konkrétní varianty řešení**, ne „Opravit / Odložit / Přeskočit“ – u oponentského nálezu existuje víc věcných cest a „opravit“ neříká kterou. Vždy nech mezi volbami i **Nechat být** a **Vrátit se k tomu později**.

**Která volba znamená který stav** (bez toho nejde odpověď zpracovat):

| Volba | Stav |
|---|---|
| kterákoliv věcná varianta (A, B, C…) | **Přijato** |
| Nechat být | **Zamítnuto** |
| Vrátit se k tomu později | **Odloženo** |

Tool má strop čtyři volby, takže věcných variant nabízej **nejvýš dvě** – zbylá dvě místa patří *Nechat být* a *Vrátit se k tomu později*. Je-li rozumných cest víc, vyber dvě nejsilnější a ostatní zmiň v popisu nálezu.

(V `/consistency` a `/review` je to naopak správně: tam má nález jedno navrhované řešení a volby jsou *Opravit / Odložit / Přeskočit*, u hromadných nálezů navíc *Rozbalit*.)

**Zpracování odpovědi:**

- **Přijato** → zapracuj do dokumentu rovnou a zapiš rozhodnutí do `docs/decisions.md`.
- **Zamítnuto** → zapiš do `docs/decisions.md` **taky**, i s důvodem. Zamítnutý nález je cenný záznam – brání tomu, aby ho příští oponentura našla znovu jako nový.
- **Odloženo** → do `docs/todo.md`, ve tvaru podle `~/.claude/RULES.md`, *Odložené věci pojmenuj a zaparkuj*.

**Odbočky.** Uživatel u nálezu často rozvine úvahu, která zasáhne jinam. Tu úvahu zapiš celou – bývá cennější než původní nález. Pak se vrať k seznamu a pokračuj; sám si hlídej, které nálezy zbývají.

------

## Fáze 6 – Závěr

**Opakované spuštění.** Skill je určený k opakování nad revidovanou verzí. Když ho uživatel spustí znovu:

- **Nález, který se vrátil**, znamená, že se neopravil, jen přeformuloval. Řekni to výslovně.
- **Míň nálezů** znamená, že se to lepší, a **víc**, že revize otevřela nové problémy – ale jen tehdy, **běžel-li stejný panel úhlů**. Zjistíš to ze záznamu předchozího běhu (viz níž); nenajdeš-li ho, počty nesrovnávej a řekni místo toho, které úhly běžely teď.

Ve verdiktu:

```
## Oponentura hotová

**Předmět:** <dokumenty>
**Úhly:** <seznam>
**Panel:** A oponentů → B nálezů hrubě → C po dedupu → D ověřeno, E neověřeno

**Nálezy:** N celkem – 🔴 X kritických, 🟡 Y středních, 🔵 Z kosmetických
- Zapracováno: N
- Zamítnuto: N (zapsáno do decisions.md i s důvodem)
- Odloženo: N (todo.md)
- Vyvráceno při ověření: N (nezobrazeno)
- Neověřeno kvůli stropu: N
- Vyřazeno před předložením: N (<proč>)

**Nejzávažnější, co z toho vzešlo**
- <jedna až tři věty – co to reálně změnilo>
```

Nakonec **zapiš průchod do `docs/done.md`, sekce `## Průchody osou`** (`~/Dev/context/structure/structure.md`, *`done.md`*) a **smaž `.claude/run/oponent.json`**:

```
- **YYYY-MM-DD** · `/oponent` · `<short HEAD>` · <předmět> · úhly: <seznam> · N nálezů (X zapracováno, Y zamítnuto, Z odloženo)
```

Datum vyrob `date +%F`, hash `git rev-parse --short HEAD` – obojí příkazem (`~/.claude/RULES.md`, *Hodnotu, kterou čte stroj, nepiš – nech ji vyrobit příkazem*). **Ten řádek je jediné, co z běhu přežije**: bez seznamu úhlů neví příští oponentura, s čím se má srovnávat, a bez hashe nepozná, jestli se předmět od té doby vůbec změnil. Nemá-li projekt `done.md` (viz Fáze 0, režim bez `docs/`), řekni nahlas, že se záznam nezapsal a srovnání s příštím během nebude možné.

Zakonči jednou z těchto vět:

- `Všechny nálezy jsou vypořádané, dokument je po oponentuře.`
- `Vypořádané nejsou: <konkrétní seznam>.`

Nikdy nekonči tím, že je dokument „v dobrém stavu“ – to není verdikt oponenta, ale autora.
