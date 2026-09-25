# Konfigurace Claude Code

[![Kontroly](https://github.com/jantichy/claude/actions/workflows/verify.yml/badge.svg)](https://github.com/jantichy/claude/actions/workflows/verify.yml)

Tohle je moje osobní konfigurace [Claude Code](https://docs.claude.com/en/docs/claude-code), kterou tu sdílím pro inspiraci. Třeba tu najdete něco užitečného i pro vaši práci. Budu rád i za jakékoliv vaše nápady a připomínky, napište mi na e-mail [jantichy@jantichy.cz](mailto:jantichy@jantichy.cz)!

Co bych z celého repozitáře vypíchl, aby to neuteklo vaší pozornosti?

## Instrukce

### [`CLAUDE.md`](CLAUDE.md) – hlavní soubor s instrukcemi

Na tomhle souboru je zajímavé hlavně to, že v něm skoro nic není. Většina instrukcí je rozdělená do dalších .md souborů. Všimněte si, že mezi nimi rozlišuju ty, které obsahují kritické body společné pro všechny projekty a mají se použít vždy, a ty, které se načtou, jen když je to podle situace potřeba. Šetří to kontextové okno.

### [`RULES.md`](RULES.md) – struktura a pořádek pod kontrolou

Obecná pravidla práce napříč všemi projekty: jak se mnou Claude komunikuje, jak organizuje soubory a obsah, jak rozhoduje a kde končí rozsah zadání, jak zachází se změnami. Je tu i rámeček s životním cyklem projektu – od `/project` až po `/release` –, jehož podrobnosti drží [`skills/LIFECYCLE.md`](skills/LIFECYCLE.md). A tabulka, podle které se vybírá model a effort pro každý typ úkolu: na návrhu a na ověřování nálezů se nešetří, mechanický sběr jede levně, a **levný model se vyplatí jen tam, kde se jeho chyba pozná levně**.

### [`STRUCTURE.md`](STRUCTURE.md) – každý projekt vypadá uvnitř stejně

Konvence, kterou drží každý můj projekt: co je v `CLAUDE.md`, co v `README.md` a co v `docs/` – tedy kam patří úkol, kam nezávazný nápad, kam rozhodnutí i s variantami, které jsem zavrhl, a kam záznam o hotové práci. Díky ní se dá vejít do libovolného projektu a hned vědět, kde co hledat – a vědí to i skilly, kterých do těch souborů zapisuje půl tuctu. Zakládá ji `/project`, čte ji většina ostatních.

### [`PTYDEPE.md`](PTYDEPE.md) – termíny, které znamenají to, co si myslíme

Claude si zvykne na slovo, které v konverzaci padlo jednou a třeba omylem, a začne ho používat napříč projekty, jako by to byl zavedený pojem. Tenhle soubor je proti tomu: tabulka, co se místo čeho používá a v jakém rozsahu. Nejcennější je vždycky ten rozsah – termín se nejčastěji nekazí tím, že by se přejmenoval, ale tím, že se tiše rozšíří na příbuznou věc. Je to schválně jen tabulka: soubor se načítá do každé session, takže důvody a historie náhrad leží stranou, u skillu `/ptydepe`.

### [`skills/LIFECYCLE.md`](skills/LIFECYCLE.md) – co je čí krok

Životní cyklus projektu podrobně: co který krok dělá, co po něm platí a proč stojí zrovna v tom pořadí. Hlídá hlavně to, aby si dva kroky nedělaly tutéž práci – u věci, kterou kontrolují tři, ji nakonec neudělá pořádně žádný. Načítá se, až když se v některém kroku opravdu stojí; v `RULES.md` zůstal rámeček s pořadím a pravidla, která platí i mimo cyklus.

### [`WORKTREE.md`](WORKTREE.md) – několik rozdělaných věcí vedle sebe

Pravidla uspořádání, ve kterém má každá rozdělaná větev vlastní adresář na disku, takže nad projektem může běžet několik session naráz, aniž si přepisují soubory. Popisuje, co kde leží, jak se větev zakládá, proč se v hlavním adresáři nepracuje a proč v kořeni takového projektu přestane fungovat git. Zapnout a zrušit to umí [`/worktree`](skills/worktree/), ale samotná pravidla jsou tady – čte je totiž i příprava a většina ostatních skillů, tedy i ten, kdo `/worktree` nainstalovaný nemá.

### [`skills/SKILLS.md`](skills/SKILLS.md) – norma, jak vypadá skill

Norma tvaru vlastních skillů: kdy skill vůbec zakládat a kdy to patří jinam, co musí být v hlavičce, jaké sekce a v jakém pořadí, jak dlouhý smí být, jak se vybírá model a typ agenta a co musí mít obě README. Stojí na pravidle **skládej, nepiš znovu** – než napíšeš krok, zjisti, jestli ho neumí vestavěný skill, plugin nebo hook, a jestli ho nejde jen obalit tak, aby se ta implementace dala později vyměnit beze změny volání.

### [`skills/PREFLIGHT.md`](skills/PREFLIGHT.md) – společný začátek běhu

Kořen projektu, worktree layout, co se čte z projektového `CLAUDE.md`, stav pracovního stromu, průběžná kontrola a určení rozsahu z gitu. Čtrnáct skillů to mělo každý svoje, což je nejhrubší porušení „single source of truth“, jakého jsem se v téhle konfiguraci dopustil. Teď je to sepsané na jednom místě a skill si má psát jen svoje odchylky. Převedená je celá sada a nové skilly vznikají rovnou podle normy. Výčet, kdo je kde, tady schválně není: rozešel by se po každém dalším převodu.

### [`skills/SESSION.md`](skills/SESSION.md) – jak se čte nahraná konverzace

Claude Code ukládá každou session do souboru a dvěma skillům se z něj vytěžuje: `/cleanup` z něj bere dohody, `/skill` to, co se při ladění vyladilo. Drží pasti, které stojí celý výtěžek – že se nesmí sáhnout po naposledy změněném souboru (nad projektem běžívají dvě session naráz) a že zpráva poslaná uprostřed rozepsané odpovědi se neukládá jako uživatelská, takže ji běžný filtr přeskočí.

### [`skills/SEVERITY.md`](skills/SEVERITY.md) – jak vážné to je, měří všichni stejně

Pět skillů hlásí nálezy a každý z jiného světa: chyba v kódu, rozbitá aplikace, rozejitá dokumentace, námitka k návrhu, vada na cizím webu. Stupeň u nich musí znamenat totéž, jinak se nálezy z různých běhů nedají porovnat ani seřadit. Původní trojice to nezvládla, protože míchala dvě osy – nejvyšší stupeň mluvil o naléhavosti, nejnižší o povaze nálezu –, takže jí audit cizího webu utekl a zavedl si vlastní. Dnes stojí celá na jedné ose a každý skill si nad ní podává vlastní čtení.

### [`BYPASS.md`](BYPASS.md) – čím se dají obejít vlastní kontroly

Mapa známého povrchu: u každé vrstvy, která tu něco vynucuje – průběžná kontrola, oba git hooky, CI, permission systém, status line –, stojí čím se dá obejít, co to chytí a co je vědomě přijaté riziko. Většina řádků je „accepted“ a u každého je důvod. Zákaz se totiž dá obejít i dodržet a nikde po tom nezůstane stopa, kdežto katalog se dá přečíst a rozporovat. Kompletnost hlídá test, který seznam vrstev čte z disku, takže nová vrstva bez řádku shodí testy.

## Skilly životního cyklu projektu

Následující skilly tvoří jeden životní cyklus od založení projektu po vyhodnocení provozu nasazené věci. **Jsou to dvě vrstvy, ne jedna řada.** Nejdřív jdou kroky **osy**, které něco tvoří – vyrobí soubor, kód nebo nasazení – a stojí tu v pořadí, ve kterém se pouštějí: od `/project` po `/evaluate`. Za nimi **kontrolní kroky** od `/oponent` po `/merge`; ty nezvětšují rozsah práce, jen se starají o to, co už vzniklo – měří to, uklízejí to a uzavírají –, a stojí v mezerách mezi kroky osy, některé z nich ve víc mezerách naráz, takže je nečti jako pokračování té řady. Projít se nemusí celý – u drobné změny odpadá zadání i plán, u projektu bez kódu nasazení i vyhodnocení provozu.

### [`/project`](skills/project/) – projekt nastavený na pár kliknutí

Zeptá se postupně na všechno, co se u nového projektu řeší pokaždé znovu – název, git a remote, uspořádání na disku, dokumentační strukturu, autocommit, typ projektu, spouštěcí příkazy, kontrolní vrstvy včetně CI, doménové checklisty – a rovnou to nastaví. Umí i projekty, které už existují, a hlavně se k nim po čase vrátit: pozná svůj vlastní otisk a místo otázek projde projekt proti tomu, jak standardy vypadají dnes. Tím řeší nepříjemnou vlastnost celé téhle vrstvy – konfigurace se vyvíjí dál, ale projekt založený loni zůstane stát a sám o tom neřekne.

### [`/discovery`](skills/discovery/) – co je venku, než začnete stavět

Nejdřív zjistí, jestli to má kdo chtít: kdo ten problém má, jak ho dnes řeší, co ho to stojí a čím je doložené, že ho chce řešit jinak – a skončí to verdiktem o dvou hodnotách, doklady oddělenými od dojmů. Pak teprve zjistí, do jakého světa produkt vstupuje: kdo to už dělá, co to umí a za kolik, čím to lidé řeší dneska, když na to nemají nástroj, a na co si u stávajících řešení stěžují. Z toho vytřídí, co produkt musí umět, aby ho někdo vzal vážně, a čím se dá odlišit – ale jen tak, aby to šlo doložit. K tomu sepíše registr rizik, ve kterém má každá položka povinné pole *co se kvůli tomu v produktu změní*. Běží před zadáním, aby to, co najde, mohlo zadání ještě změnit.

### [`/specify`](skills/specify/) – z nápadu zadání, než se sáhne na kód

Vyptá se mě na záměr a udělá z něj `requirements.md` – dokument, který odpovídá na otázku *co stavíme a proč*, a k němu scénáře, glosář a ceník, vede-li je projekt. Jak se to postaví, nerozhoduje: hranici drží tvrdě, včetně testu, kam která věta patří – *změní se to, když vyměním databázi?* Ano → návrh, ne → sem. Dokud není zadání schválené, nesmí vzniknout ani řádek kódu, ani scaffold. A pozná, kdy se specifikace psát nemá, protože jde o změnu v existujícím kódu.

### [`/architect`](skills/architect/) – rozhodnout, jak se to postaví

Ze schválených požadavků udělá návrh řešení – architekturu, data, stavy a přechody, rozhraní, cizí systémy, bezpečnostní model. **Není to jeden dokument, ale sada**, a nový přibývá jen tehdy, když odpovídá na otázku, na kterou žádný jiný neodpovídá. Větší záměr rozdělí na tematická kola, která jdou řešit i souběžně v samostatných větvích, a návrh nad celkem sešije až z jejich výsledku. Nemá režimy – ze stavu projektu sám pozná, co je na řadě, a než sáhne na první soubor, jednou větou to oznámí.

### [`/breakdown`](skills/breakdown/) – ze zadání implementační plán

Vyrobí ze schváleného zadání `docs/plan.md` – seřazený seznam úkolů velikosti pár minut, kde každý má konkrétní soubory, hotový kód testu a příkaz, kterým se ověří, že je hotový. Plán se předkládá ke schválení, protože je to poslední levné místo, kde se dá otočit.

### [`/implement`](skills/implement/) – odpracování plánu úkol po úkolu

Projde plán od začátku do konce, u každého úkolu test, kód, průběžná kontrola a commit. Umí navázat na rozdělaný plán a nevěří přitom zaškrtávátkům – ověří si v kódu, že odškrtnuté úkoly opravdu existují a procházejí. Nabídne tři režimy podle toho, jak často se do toho chci dívat.

### [`/release`](skills/release/) – nasazení jako vědomý úkon, ne vedlejší efekt

Nasadí do produkce přes **oddělenou nasazovací větev**, takže `main` zůstane integrační a merge feature nic nenasazuje. Před nasazením projde kontroly, zvlášť řeší migrace dopředu kompatibilně a nikdy se nespustí sám. A tím nekončí: poslední fází je **sledovací okno** s konkrétním koncem, protože celá třída chyb se projeví až později. Dokud okno neuplyne a někdo ho výslovně neuzavře, nasazení není hotové.

### [`/evaluate`](skills/evaluate/) – co provoz říká o hotové věci

Za pár týdnů po nasazení nikdo neví, jestli tu věc někdo používá, kde lidé odpadli, ani že si dvakrát napsali o totéž. Tenhle skill sebere čísla ze zdrojů, které projekt doopravdy má – databáze, logy, maily –, u každého poznatku zapíše, odkud se to ví a jak se to dá přepočítat, a **nepustí vás dřív, než se o každém rozhodne**: úkol, nápad, nebo vědomé „tohle dělat nebudeme“ i s důvodem. Najde přitom i to, co nespadlo, jako odmítnutou akci nebo vypršelý limit. Zjistí-li, že se neměří nic, je to jeho výsledek, ne selhání.

### [`/oponent`](skills/oponent/) – oponentura na to, co nejde otestovat

Pošle na hotový dokument agenty, kteří **nemají z naší session žádný kontext** a čtou jenom soubory, každého z jiného hlediska. V cyklu stojí třikrát – za průzkumem, za zadáním a za návrhem –, protože jinak ty vrstvy neměří nikdo: `/review` ověřuje kód proti specifikaci, ale samotnou specifikaci nikdo proti ničemu. Každou závažnou námitku pak dostane ověřovatel s jediným úkolem – **vyvrátit ji**.

### [`/review`](skills/review/) – panel nezávislých pohledů na hotovou práci

Prověří hotovou práci před uzavřením ze tří stran: nejdřív nástroje projektu, pak paralelní panel agentů, kde každý má jediné hledisko – korektnost, bezpečnost, data a stavy, provoz a chyby, testy, agentní infrastruktura, moje doménové standardy –, a nakonec ověřovatele, jehož úkolem je nález **vyvrátit**. Co ověření nepřežije, se mi vůbec nezobrazí.

### [`/consistency`](skills/consistency/) – skill proti bordelu v projektu

Audit vnitřní konzistence: protichůdné instrukce, duplicity, zapomenuté zbytky po smazaných částech, mrtvý kód, rozejití mezi vrstvami. Jednoznačné opravy udělá rovnou, o sporných se mnou mluví jednu po druhé. A pamatuje si, co jsem rozhodl neopravovat – jen do chvíle, než se ten kód změní.

### [`/attack`](skills/attack/) – zkusit aplikaci rozbít

Zvedne aplikaci lokálně a pošle na ni agenty, kteří ji zkouší rozbít – každý s jedním vektorem: nesmyslné vstupy, přeskočené a zopakované kroky, cizí ID v adrese, mezní data, výpadek sítě uprostřed odesílání. Na rozdíl od `/review`, který kód čte, tenhle ho spouští. Každý nález musí mít reprodukční postup a každá oprava regresní test; útočí se výhradně na lokální instanci nad testovacími daty, a že tomu tak opravdu je, se dokládá příkazem, ne slibem.

### [`/cleanup`](skills/cleanup/) – ať po mně zůstane čisto a jasno

Před opuštěním nebo zkompaktováním session přečte celou konverzaci – včetně části, kterou už compact vyhodil z kontextu – a zapíše všechno dohodnuté tam, kam to patří, i s důvody a zavrženými variantami. Pak hledá druhou věc: co v konverzaci zůstalo viset bez vypořádání, a probere to se mnou, dokud je koho se ptát. Celé to těžké čtení a zápis přitom dělá subagent, ne hlavní session: transcript leží na disku a kontext session k té práci není potřeba, takže běh stojí zlomek toho, co dřív. Na konec pošle na projekt dva agenty bez kontextu – jeden řekne, jestli z dokumentace jde na dnešní práci navázat, druhý hledá rozpory a zbytky po přepisování v tom, co přibylo na větvi –, a nabídne, co dál: ve větvi i rovnou merge. Čtou na pozadí, takže se na ně nečeká.

### [`/merge`](skills/merge/) – dokončení větve, ne jeden příkaz

„Přimerguj to“ vypadá jako jediný příkaz, ale je to postup, ve kterém se dá přijít o práci – nejčastěji tak, že se dvě větve rozejdou obsahově, ne textově, merge projde bez konfliktu a rozbitý stav vznikne poprvé až na hlavní větvi, kde na něm stojí všichni ostatní. Tenhle skill to dělá obráceně: hlavní větev nejdřív přihraje do té pracovní, tam nechá vyřešit konflikty a pustí kontroly projektu, a do hlavní pustí jen to, co prošlo. Pak slučuje se zprávou, která říká, co větev přinesla, a uklízí – ale až po ověřeném mergi, nikdy souběžně s ním. Zavoláte ho sami, nebo ho vyberete z nabídky na konci `/cleanup`, aby se nemusel psát ručně – sám od sebe se nespustí nikdy.

## Skilly mimo životní cyklus

Tyhle se pouštějí podle potřeby, nezávisle na fázi projektu. Jsou seřazené abecedně.

### [`/audit`](skills/audit/) – audit cizího webu proti mojí vlastní metodice

Zaudituje cizí web v zadané oblasti – analytiku, SEO, použitelnost, přístupnost – proti postupu a katalogu typických nálezů, které mám sepsané ve své znalostní bázi. Web opravdu spustí a projde, práci rozdělí několika nezávislým pohledům a každý nález pak nechá někoho jiného zkusit vyvrátit opakovaným průchodem, takže ven jde jen to, co obstálo. Sám žádnou odbornou znalost nenese.

### [`/autocommit`](skills/autocommit/) – každá změna hned do Gitu

Zapne pro daný projekt režim, kdy Claude po každém logickém celku automaticky commituje, a pokud je nastavený remote, taky pushuje. Nehodí se do všech projektů, ale tam, kde mám hromadu rychlých iterací, mi to šetří desítky až stovky commit instrukcí za den.

### [`/compose`](skills/compose/) – texty, co znějí jako já

Napíše článek, post na sociální sítě nebo vlákno mým hlasem a stylem – ne obecnou AI-češtinou. Táhne to ze znalostní báze mého psaní a k tématu si dohledá nejpodobnější texty z archivu jako živé vzory. Tu bázi umí i postavit: `collect` provede posbíráním všeho, co člověk kdy napsal – exporty ze sociálních sítí, články z webů, zálohy po webech, které už nestojí –, a `profile` z toho vydestiluje popis hlasu a později ho doplňuje o to, co přibylo. Moje názory a pointy si ale nikdy nevymýšlí, ty musím dodat sám.

### [`/depot`](skills/depot/) – stažený soubor doputuje tam, kam patří, a rovnou se zpracuje

Řeknu mu soubor nebo celou dávku z Downloads a on pozná, o jaký podklad jde, uloží ho na správné místo pod správným názvem a hned spustí, co po tom má následovat – přepis nahrávky, vytěžení do knowledge base, zápis do evidence. Rozsah je přesně to, co zadám: neuklízí okolí, nic nepřepíše a při kolizi se zeptá místo toho, aby přilepil `(1)`. Konkrétní pravidla, co kam patří, v tomhle repozitáři nejsou – skill je jen rámec a tabulku si čte z mojí privátní knowledge base.

### [`/diagram`](skills/diagram/) – datový model jako mapa, na kterou se dá kliknout

Z dokumentace navrženého modelu nakreslí interaktivní stránku: ER diagram všech tabulek, ve kterém po kliknutí vidím popis entity, vazby, sloupce a constrainty, a stavový prostor s přechody mezi stavy. Žije jako soukromý artefakt a při dalším zavolání se překreslí na stejném odkazu, klidně z jiné rozdělané větve. Nekreslí nic, co v dokumentaci není, a do projektu nezapisuje.

### [`/invoicing`](skills/invoicing/) – faktury na konci měsíce bez ručního sčítání

Sečte hodiny z timetrackingu po klientech, ukáže mi, co napočítal a co je mu podezřelé, vystaví faktury a nechá v mailu rozepsaný draft s fakturou a výkazem hodin v příloze. **Odeslat ho musím vždycky já** – tvrdá stopka, která platí i tehdy, když ho o odeslání sám uprostřed běhu poprosím. Umí i opačný směr: dohledat čas, který jsem si zapomněl natrackovat. Sazby a dohody s klienty v tomhle repozitáři nejsou, skill je jen rámec.

### [`/learn`](skills/learn/) – nová znalost dovnitř té staré, ne vedle ní

Vezme přepis školení, článek, poznámky, ale i rovnou nahrávku, obrázek nebo PDF a zapracuje je do mojí knihovny know-how – rozebere zdroj na jednotlivé poznatky a rozpustí je na místa, kam patří, klidně i s přestavbou textu kolem. Rozliší přitom skutečný rozpor od toho, že jsem na školení něco jen řekl jednodušeji, a ptá se opravdu jen tam, kde neví. Metodiku přepisuje volně, ručně psané texty jen doplňuje a doslovných přetisků se nedotkne.

### [`/next`](skills/next/) – s čím pokračovat, když se k projektu vrátím

Na začátku session posbírá všechno, co v projektu čeká – seznam úkolů, zbytek plánu, kola rozpracovaného návrhu, rozdělané větve a necommitnuté změny –, vypíše zvlášť, na čem se právě pracuje v jiné session, nabídne pokračování v zapomenutých větvích, zbytek seřadí podle závislostí, u každého úkolu řekne, v čem spočívá a jak je velký, a nejaktuálnější mi nabídne k výběru. Po výběru se do toho rovnou pustí. Nahrazuje dlouhý prompt, který jsem psal do každé nové session.

### [`/ptydepe`](skills/ptydepe/) – slova, kterým rozumíme jenom my dva

Claude si z konverzace odnese slovo, které jsem použil jednou a třeba omylem, a začne ho používat jako zavedený pojem – napříč projekty, v dokumentaci, v názvech souborů. Tenhle skill takové termíny vyhledá, projedná se mnou jeden po druhém, a co odsouhlasím, nahradí ve všech repozitářích naráz. Skončit umí i tím, že se v textech nic nepřepíše – slovo je běžná čeština a **ponechá se**, nebo se používá český protějšek a to cizí se **zakáže preventivně**, ať se nezačne zavádět. Dohodnuté náhrady pak drží [`PTYDEPE.md`](PTYDEPE.md), takže se totéž slovo neotevírá za měsíc znovu.

### [`/replace`](skills/replace/) – přejmenovat něco a fakt všude

Přejmenuje pojem napříč projektem včetně **odvozených tvarů** a české skloňované varianty, kterou grep na základní tvar nenajde. Sahá i na názvy souborů a adresářů, přesouvá přes `git mv`, ať se neztratí historie, a hlídá pořadí – delší tvary před kratšími. Povinný poslední krok je kontrolní průchod na starý tvar, který musí vrátit nulu.

### [`/report`](skills/report/) – data do jednoho souboru, co jde poslat komukoliv

Z exportu z GA4, CSV nebo výsledku dotazu do BigQuery udělá jeden interaktivní HTML soubor, který jde otevřít dvojklikem odkudkoliv: žádné CDN, aby fungoval offline i za pět let, a datum vygenerování zapsané natvrdo. Než ho pustí ven, projde hotový soubor na osobní údaje a na přístupové údaje, které do reportu protečou samy z výpočetního skriptu nebo ze screenshotu administrace.

### [`/scenarios`](skills/scenarios/) – situace, na které se v návrhu zapomnělo

Projde konverzace nad projektem, které se od minule nevytěžily, a doplní z nich chybějící uživatelské scénáře. Řeší tichou vadu, která vzniká při každém kole návrhu: rozhodne se, jak se má systém v nějaké situaci chovat, zapíše se to do modelu – a scénář k té situaci nikdo nedopíše. Seznam situací pak vypadá úplně a není, takže se proti němu nedá ověřit, co nový návrh rozbil.

### [`/serviceaccount`](skills/serviceaccount/) – strojový přístup ke klientským systémům

Připraví service account pro přístup do klientské analytiky nebo Tag Manageru: odvodí z rozpracovaného projektu, o koho jde, poskládá jméno podle konvence tak, aby z něj byl vidět rozsah přístupu, a sepíše žádost o oprávnění pro klienta. Řeší past, kterou je snadné přehlédnout – jméno účtu je neměnné, takže oprava znamená znovu obtěžovat klienta.

### [`/skill`](skills/skill/) – skilly, které se samy udržují

Zakládá nové skilly proti normě, vytěží skill z rozdělané konverzace, **prožene existující skilly revizí** a umí skill i zrušit včetně všech stop. Revize je ten důvod, proč vznikl: norma se posouvá dál, ale hotové skilly zůstanou stát a samy o tom neřeknou. Klade přitom otázku, kterou nepoloží nikdo jiný – *nevzniklo mezitím něco, co tenhle skill dělá ručně?*

### [`/transcript`](skills/transcript/) – nahrávky na přepis a chytré shrnutí

Ze zvukových i obrazových nahrávek udělá čitelný přepis a strukturované shrnutí se soupisem domluv a úkolů na konci; na vyžádání rozliší i mluvčí, takže úkoly mají majitele. Přepis běží **lokálně a offline**, takže nahrávka neopustí můj počítač. Než začne, podstrčí rozpoznávači jména a názvy, které v nahrávce padnou – ta pak nekomolí lidi ani firmy. Leží-li v adresáři víc souborů, zeptá se, jestli to není **jedna schůzka rozřezaná na části** – diktafon se zastavil, spadl hovor –, a spojí ji ještě před přepisem: vznikne jeden souvislý přepis a jedno rozlišení mluvčích místo několika oddělených, mezi kterými by se stejní lidé nedali spárovat. A když se rozpoznávač uprostřed dlouhé nahrávky zakousne, umí ji dopřepsat po úsecích: problémový kus přeskočí a o zbytek nepřijdu.

### [`/worktree`](skills/worktree/) – každá rozdělaná větev ve vlastním adresáři

Přepne projekt do uspořádání, kde má každá rozdělaná větev vlastní adresář, takže nad ním může běžet několik session naráz, aniž si přepisují soubory. Umí to i zpátky. Přeskládává `.git`, tedy to nejcitlivější v repozitáři – proto nejdřív zálohuje, na konci porovná a smaže zálohu, teprve když porovnání vyjde. Pravidla, jak se v takovém projektu pracuje, si nainstaluje rovnou do něj, takže platí od začátku každé session, aniž ho člověk volá.

## Hooky, skripty a nastavení

### [`statusline.sh`](statusline.sh) – všechno podstatné na jednom řádku

Jednořádková status line, která mi ukazuje všechno, co potřebuju průběžně vidět: aktuální model, zaplnění kontextového okna, čerpání 5hodinového i týdenního limitu, aktuální adresář i stav Gitu. Čerpání vizualizuje teploměrem, procenty i zbývajícím časem a mění barvy podle toho, jak je na tom blízko limitu.

![Status line](statusline.png)

### [`verify.sh`](verify.sh) – nad rozbitým projektem se práce neuzavře

`Stop` hook, který před ukončením odpovědi spustí typecheck, lint a testy, a když něco padá, **nepustí Clauda skončit** – dostane zpátky výstup a musí to dořešit. Rozliší přitom nalezenou chybu od kroku, který vůbec nejde spustit, i od kontraktu, co se nedá přečíst, ať se nespuštěná kontrola nevydává za „prošlo všechno“. O projektu sám nic neví: přečte si sekci `## Kontrakt příkazů` v jeho `CLAUDE.md` a spustí, co tam stojí, takže se registruje jednou globálně a v projektu bez kontraktu neudělá nic. Ten kontrakt je ale kód ležící v repozitáři, takže v něm hook nespustí nic, dokud pro něj nevydám souhlas – a ten jde vydat jen ze samostatného okna terminálu.

### [`git-guard.py`](git-guard.py) – nevratný příkaz zastavený dřív, než se spustí

`PreToolUse` hook, který čte celý příkaz, ne jeho začátek. Seznam zakázaných příkazů v `settings.json` totiž porovnává jen prefix, takže `git push --force` zachytí, kdežto `git push origin main --force` projde – a to je tvar, který člověk napíše častěji. Aliasy si rozbalí z konfigurace gitu, takže vlastní zkratka hook neobejde. Zastavuje to, po čem práci nejde vrátit: přepsání vzdálené historie, zahození necommitnutých změn, smazání větve, reflogu nebo stashe, úklid netrackovaných souborů a `gc --prune`. Suchý běh propouští.

### [`agents/`](agents/) – posuzovatel, který nemá čím zapisovat

Definice dvou typů subagentů, kterými si skilly vyžádají posudek – sedm z nich to dělá. Liší se jedinou věcí: jestli agent smí na web. Ani jeden nemá shell, takže posudek nemůže sáhnout na to, co posuzuje. Berte si je spolu se skilly; bez nich musí skill sáhnout po náhradní cestě, kterou pro ten případ popisuje.

### [`githooks/`](githooks/) – historie main jako jeden řádek na větev

`commit-msg` hook, který nad hlavní větví odmítne výchozí zprávu `Merge branch 'feat/payments'` a vyžádá si shrnutí odvedené práce. Díky tomu ukazuje `git log --first-parent` každou zamergovanou větev jako jeden řádek, který něco říká, a dílčí commity zůstanou dostupné pod ním. Aktualizace rozdělané větve ani merge po `git pull` mu nepřekážejí. Nasazený je globálně přes `core.hooksPath`, takže platí ve všech repozitářích na stroji.

### [`tests/`](tests/) – testy nad konfigurací, ne nad kódem

Testy nad textem, který nikdo nespouští, a nad vrstvami, které tu něco doopravdy vynucují: hlídají režim popsaný v těle skillu a chybějící v jeho hlavičce, odkaz na soubor nebo sekci, co mezitím zmizela, skill bez README – a k tomu průběžnou kontrolu, oba git hooky, status line a CI, kde tichá regrese stojí nejvíc. Zvlášť pak skripty skillů tam, kde hrozí ztráta dat. Běží v průběžné kontrole po každé odpovědi, jen na standardní knihovně Pythonu a bez instalace; tytéž příkazy pouští i [GitHub Actions](.github/workflows/verify.yml), protože lokální kontrolu obejde commit z jiného stroje, z GUI nebo cizí fork.

### [`settings.json`](settings.json) – průběžně laděné permissions

Allowlist/denylist/asklist se snažím držet ve vyváženém poměru mezi bezpečností a plynulostí práce. Cíl je nemuset odklikávat každou trivialitu, ale zároveň nenechat bez kontroly moc bezpečnostních děr. Tohle je vždycky lavírování na hraně a občas tu jdu vědomě lehce za hranu – ve prospěch svého pohodlí a na úkor středně rizikových operací. Takže si to k sobě rozhodně nekopírujte bezhlavě, ale můžete to vzít čistě inspiračně pro porovnání s vlastním nastavením.

## Než si odsud něco vezmete

Tohle je obsah mého `~/.claude`, ne balíček k instalaci. Když si budete něco kopírovat, počítejte s pár věcmi:

- **Absolutní cesty.** `settings.json` i skilly mají natvrdo `/Users/honza/…` – v hoocích, ve statusline, v permissions. Přepište je na své, jinak vám budou tiše selhávat.
- **Předpoklady.** Rozpadají se na tři skupiny:

  - **Povinné pro průběžnou kontrolu.** `shellcheck` a `ruff` tvoří dohromady `lint` v kontraktu tohohle repozitáře, takže bez nich hlásí kontrola po každé odpovědi nespustitelný krok. Totéž platí pro `swiftc` z vývojářských nástrojů Xcode, na kterém stojí `typecheck` – na macOS bývá po ruce, ale bez něj se hlásí stejně. `ruff` běží jen na chybová pravidla, ne na styl.
  - **Obecné.** macOS s [Homebrew](https://brew.sh), `jq` a `coreutils` kvůli `gtimeout`. Plugin [superpowers](https://github.com/obra/superpowers), na kterém stojí `/specify`, `/breakdown` a `/implement`.
  - **Pro jednotlivé skilly.** `/skill` potřebuje `skill-creator`; bez něj mu odpadne režim `extract` a celá měřicí část. `/audit` stojí na pluginu [chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp) a na Chromu. `/compose` potřebuje Python 3 a u Bluesky balíček `cbor2`. `/transcript` má vlastní sadu navíc: `ffmpeg`, `whisper-cpp` a stažené modely, u rozlišení mluvčích k tomu `pyannote.audio` ve vlastním venv, účet a token na HuggingFace a **ruční odsouhlasení licencí tří gated repozitářů v prohlížeči** – to je jediný předpoklad v celém repozitáři, který nejde zautomatizovat. Velikosti a přesné příkazy drží [jeho `SKILL.md`](skills/transcript/SKILL.md).

  `gitleaks` a `semgrep` jsou volitelné jen lokálně: bez prvního sáhne `/review` po slabší grep-heuristice, bez druhého příslušná kontrola odpadne. **V CI volitelné nejsou**, workflow si je doinstaluje a jejich nález shodí běh. Každý skill si na chybějící kusy posvítí sám a napíše je do výpisu *Nezkontrolováno*.
- **Část znalostí v repu není.** Skilly se opírají o soukromý adresář `~/Dev/context/` s doménovými standardy (`coding/`, `web/`, `analytics/`, `advertising/`, `text/`, `design/`, `training/` a další) a odkazují do něj. To je moje soukromé know-how a osobní archiv, takže ho tu nenajdete – ty skilly jsou k mání jako kostra, ne jako hotová věc.
- **Berte to po částech.** `RULES.md` funguje samostatně a použitelný je nejspíš hned. Skilly si projděte a upravte. `settings.json` si rozhodně proberte řádek po řádku – kromě permissions v něm jsou i hooky, statusline, pluginy a osobní nastavení modelu a jazyka.
- **Licence.** Všechno tady je pod [MIT](LICENSE) – berte si, co chcete, jen si to nechte na vlastní triko.
