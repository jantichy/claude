# Konfigurace Claude Code

Tohle je moje osobní konfigurace [Claude Code](https://docs.claude.com/en/docs/claude-code), kterou tu sdílím pro inspiraci. Třeba tu najdete něco užitečného i pro vaši práci. Budu rád i za jakékoliv vaše nápady a připomínky, napište mi na e-mail [jantichy@jantichy.cz](mailto:jantichy@jantichy.cz)!

Co bych z celého repozitáře vypíchl, aby to neuteklo vaší pozornosti?

## [`CLAUDE.md`](CLAUDE.md) – hlavní soubor s instrukcemi

Na tomhle souboru je zajímavé hlavně to, že v něm skoro nic není 😉. Většina instrukcí je dekomponovaná do dalších .md souborů. Všimněte si, že mezi nimi rozlišuju ty, které obsahují kritické body společné pro všechny projekty a mají se použít vždy, a ty, které se načtou jen když je to podle situace potřeba. Brutálně se tím šetří kontextové okno.

## [`RULES.md`](RULES.md) – struktura a pořádek pod kontrolou

Kdo mě zná, tak ví, že jsem hodně citlivý na strukturovanost a čistotu návrhu. [OCD](https://cs.wikipedia.org/wiki/Obsedantn%C4%9B-kompulzivn%C3%AD_porucha) hadr neasi. A opravdu hodně trpím tím, jakých svévolností se dovede Claude v projektu dopustit, když se chvíli nehlídá. Tenhle soubor ho drží na uzdě napříč všemi mými projekty. Vedlejší efekt je, že mu pak většinu věcí stačí říct jenom jednou. A co se nevychytá tady, to dotáhne do dokonalosti skill `/consistency`.

## [`/consistency`](skills/consistency/) – ultimátní skill proti bordelu

Kompletní audit projektu na vnitřní konzistenci a pořádek: protichůdné instrukce, duplicity, zapomenuté zbytky po smazaných částech, mrtvý kód, drift mezi vrstvami. Nálezy roztřídí od kritických po kosmetické. Co má jen jedno správné řešení – rozbitý odkaz, nepoužitý import, počet v textu nesedící s tabulkou – opraví rovnou a jen mi to vypíše. O sporných se mnou mluví jednu po druhé.

## [`/review`](skills/review/) – panel nezávislých pohledů na hotovou práci

Prověří hotovou práci před uzavřením, a to ze tří stran naráz. Nejdřív nástroje, které nestojí ani token a nehalucinují: testy, lint, audit závislostí, scan tajemství, statická analýza. Pak paralelní panel agentů, kde každý má jediný úhel pohledu – korektnost, bezpečnost, data a stavy, provoz, testy, moje doménové standardy. Agent, který má hledat všechno, nenajde nic; agent s jedním checklistem jde do hloubky.

Třetí vrstva je ta, na které to celé stojí: každý nález dostane nezávislého ověřovatele, jehož úkolem je ho **vyvrátit**. Bez ní by mě panel zavalil nálezy, které jen věrohodně znějí, a po třetím falešném bych ho přestal pouštět. Vyvrácené se ani nezobrazí. Když jsem ho poprvé pustil na vlastní práci, ze 43 nálezů tři nepřežily ověření – a mezi zbytkem byla chyba, kvůli které mi celá zelená linka tiše neběžela.

## [`/oponent`](skills/oponent/) – oponentura na to, co nejde otestovat

Na kód mám `/review`. Ale na dokument, který s Claudem píšu tři dny – pozicování, cenotvorbu, datový model – jsem neměl nic, a je to přesně ten typ práce, kde se nejvíc zmýlím: Claude je spoluautorem, takže na něj nemá nezávislý pohled o nic víc než já.

Skill to obchází tím, že na dokument pošle agenty, kteří **nemají z naší session žádný kontext** a čtou jenom soubory. Každý dostane jiný úhel: jeden hledá vnitřní rozpory, druhý nejslabší předpoklad, třetí to čte očima cílové skupiny, další počítá ekonomiku. Každý nález musí mít konkrétní důsledek („při 20 000 účastnících vyjde ruční párování na 300 hodin“), ne obecnou obavu. Zapisují se i zamítnuté námitky – jinak by je příští oponentura našla znovu jako nové.

## [`/cleanup`](skills/cleanup/) – ať po mně zůstane čisto a jasno

Když mám dlouho otevřenou session a chystám se odejít nebo zkompaktovat, tíží mě pokaždé totéž: neztratí se něco? Skill projde celou session – včetně části, kterou už compact vyhodil z kontextu – a všechno, na čem jsme se dohodli, zapíše tam, kam to patří, i s důvody a zavrženými variantami.

Pak to nejlepší: pošle na projekt agenta bez jakéhokoli kontextu, který čte jen repozitář, jako by se do projektu zaučoval. Ten mi řekne, jestli z dokumentace jde na dnešní práci navázat a kde bych musel hádat. Nakonec commitne a dá jednoznačný verdikt: můžeš jít, nebo tohle ještě zbývá.

## [`/autocommit`](skills/autocommit/) – každá změna hned do Gitu

Zapne pro daný projekt režim, kdy Claude po každém logickém celku automaticky commituje. A pokud je nastavený remote, taky pushuje. Nehodí se do všech projektů, ale tam, kde mám hromadu rychlých iterací, mi to šetří desítky až stovky commit instrukcí za den.

## [`/autoprompt`](skills/autoprompt/) – ukládá všechny prompty

Zapne pro projekt automatické logování všech mých promptů na jedno snadno přístupné a čitelné místo, do souboru `prompts.md` v projektu (ve worktree layoutu si sám najde `main/`, aby log skončil ve gitu, a ne v kontejneru, ze kterého by se nedal commitnout). Při zapnutí dokonce backfilluje historii ze session souborů, takže získám kompletní záznam i zpětně. Ač to na první pohled nevypadá, dříve či později to opravdu doceníte. Pro sledování, jak se projekt vyvíjel, pro učení se vlastních anti-patternů v promptech, překvapivě často tam pošlete Clauda, aby si z toho něco zpětně vytahal nebo naučil…

## [`/project`](skills/project/) – projekt nastavený na pár kliknutí

Kdykoli zakládám projekt, řeším pořád dokola totéž: jak se ta věc lidsky jmenuje, git a remote, autocommit, autoprompt, jaký je to typ projektu. Skill se na to postupně zeptá a rovnou to nastaví, včetně `README.md`, `.gitignore` a standardní struktury. Umí i projekty, které už existují – udělá inventuru a dorovná je na moje dnešní preference, nikdy nepřepíše soubor bez zeptání.

Dvě věci na něm mám nejradši. Umí **worktree layout** – kontejner s `.bare` a jedním podadresářem na větev – včetně toho nejzrádnějšího detailu: kořen kontejneru není pracovní strom, takže se v něm nedá commitnout, a projektové soubory proto patří do `main/`. A vyplní **metadata projektu**, která se propíšou do `README.md` i do Repository details na GitHubu – ten popisek pod názvem repa, co se nedá nastavit souborem a roky mi proto všude chyběl.

## [`/specify`](skills/specify/) – z nápadu zadání, než se sáhne na kód

Pokaždé, když jsem zakládal něco nového, psal jsem tu samou zprávu: teď ještě neprogramuj, nejdřív se mě postupně vyptej, pak z toho udělej zadání a teprve pak plán. Skill z toho dělá jeden příkaz a vyrábí **dva dokumenty**: `requirements.md` odpovídá na otázku co stavíme a proč, `architecture.md` na otázku jak.

Že jsou dva, a ne jeden, je hlavní rozhodnutí za ním – mají jinou životnost. Produktový záměr se mění zřídka, technické řešení s každou úvahou o technologii; v jednom souboru by se při výměně databáze editoval tentýž dokument, kde stojí popis cílové skupiny. Hranici mezi nimi má skill popsanou tvrdě, včetně testu, kam která věta patří: *změní se to, když vyměním databázi?*

A má v sobě brzdu proti tomu, co Claudovi jde nejhůř odpustit: než je zadání schválené, nesmí vzniknout ani řádek kódu, ani scaffold.

## [`/breakdown`](skills/breakdown/) a [`/implement`](skills/implement/) – plán a jeho odpracování

Dva tenké články řetězu: `/breakdown` vyrobí ze zadání `docs/plan.md` – seřazený seznam úkolů, kde každý má konkrétní soubory, kód testu a ověřitelné kritérium – a `/implement` ho odpracuje úkol po úkolu. Na pozadí obojí řídí [superpowers](https://github.com/obra/superpowers).

Proč pro to mít vlastní skilly, když jde volat rovnou je? **Protože čím ten krok uvnitř je, je jeho implementační detail.** Až to jednou vyměním za něco jiného, nechci si přeučovat, jak se volá. Obálky navíc dělají věci, které cizí skilly neřeší: vynucují moje cesty v `docs/`, odmítnou se spustit bez schváleného zadání, u navazování na rozdělaný plán nevěří zaškrtávátkům a ověří, jestli odškrtnuté úkoly opravdu existují v kódu.

Plán je zároveň jediné místo, kde si testy přečtu **dřív, než existuje kód** – potom už je posuzuju podle toho, jestli procházejí.

## [`/release`](skills/release/) – nasazení jako vědomý úkon, ne vedlejší efekt

Používám platformy, které nasazují automaticky po pushnutí do produkční větve, a ty si po založení projektu nastaví jako produkční `main`. To znamená, že každá přimergovaná feature jde rovnou na produkci. Skill z toho nedělá danost, ale chybu, kterou má smysl narovnat: nasazovací větev se **oddělí od integrační**. `main` zůstane tím, čím má být, a produkci mění jedině vědomé povýšení do větve `production`.

Před ním hlídá čistý strom, zelenou linku, produkční build, audit závislostí a jestli vůbec proběhlo `/review`. Zvlášť řeší **migrace**: dopředu kompatibilně, tedy nejdřív se jen přidává a odebírá se až v dalším vydání – jinak by rollback kódu shodil aplikaci na datech, která zapsala nová verze. A nepustí mě dál, dokud neumí odpovědět, jak se za deset minut vrátit zpátky.

Tři věci dělá schválně nepohodlně: nikdy se nespustí sám, nic neopravuje, a po nasazení ověřuje na produkční URL. Nasazeno není totéž co funguje.

## [`/replace`](skills/replace/) – přejmenovat něco a fakt všude

Když jsem si nechal projít historii svých promptů, tohle vyskočilo jako úplně nejčastější věc, kterou vypisuju znovu a znovu: 91 promptů obsahuje „přejmenuj / sjednoť / nahraď všude“.

Skill řeší přesně to, na čem obyčejný find-replace selhává: hledá **odvozené tvary** včetně české skloňované varianty, které bývá v dokumentaci nejvíc a grep na základní tvar ji nenajde. Sahá i na názvy souborů a adresářů, přesouvá přes `git mv`, ať se neztratí historie, a hlídá pořadí – delší tvary před kratšími, jinak z `marketId` vznikne nesmysl. A nikdy nekončí provedením: povinný poslední krok je kontrolní průchod na starý tvar, který musí vrátit nulu. Zapomenutý výskyt se totiž vrací měsíce později jako záhada.

## [`/report`](skills/report/) – data do jednoho souboru, co jde poslat komukoliv

Několikrát do měsíce potřebuju z dat – export z GA4, CSV ze souhlasů, výsledek dotazu do BigQuery – udělat něco, co pošlu klientovi. Skill z toho dělá jeden interaktivní HTML soubor, který jde otevřít dvojklikem odkudkoliv, a hlídá věci, na kterých jsem se opakovaně spálil: žádné CDN, aby to fungovalo offline i za pět let, `charset=utf-8` hned na začátku, protože diakritika se nerozsype u mě, ale až u příjemce, a datum vygenerování zapsané natvrdo.

Než report pustí ven, projde **hotový soubor** na dvě věci: jestli v něm nezůstaly osobní údaje a jestli tam neutekly přístupové údaje. To druhé je zrádnější, protože to tam nikdo nedává vědomě – proteče to samo z výpočetního skriptu nebo ze screenshotu administrace. A když něco najde, nesmí to potichu smazat: musí říct, že totéž je nejspíš i v gitu a že ty údaje patří rotovat.

## [`/compose`](skills/compose/) – texty, co znějí jako já

Napíše článek, post na sociální sítě nebo vlákno mým hlasem a stylem – ne obecnou AI-češtinou. Táhne to ze znalostní báze mého psaní (styl, ustálené obraty, jejich horní mez, ať to nesklouzne do parodie) a k tématu si navíc dohledá pár nejpodobnějších textů z archivu jako živé vzory. Moje názory a pointy si ale nikdy nevymýšlí – ty musím dodat sám.

## [`/transcript`](skills/transcript/) – nahrávky na přepis a chytré shrnutí

Hodím do složky pár zvukových nahrávek (schůzka, rozhovor, hlasová poznámka) a tenhle skill z nich udělá pořádek: každou přepíše do Markdownu a k tomu napíše jedno strukturované shrnutí napříč všemi – s tématy, klíčovými poznatky a hlavně soupisem domluv a úkolů na konci. Celý přepis běží **lokálně a offline** přes [whisper.cpp](https://github.com/ggml-org/whisper.cpp), takže žádná nahrávka neopustí můj počítač – u citlivých firemních schůzek k nezaplacení. Doslovný přepis navíc rovnou uhladí: vyhází „ehm“, odstraní halucinace rozpoznávače, opraví přeslechnuté názvy podle kontextu a rozseká text do kapitol s nadpisy. Na začátku si sám ověří, že má vše potřebné nainstalované, takže si ho můžete rovnou zkopírovat a spustit.

## [`statusline.sh`](statusline.sh) – krásná a užitečná status line

Jednořádková status line, která mi ukazuje všechno, co potřebuju průběžně vidět: aktuální model, zaplnění kontextového okna, čerpání 5hodinového i týdenního limitu, aktuální adresář i stav Gitu. Vizualizace ukazuje čerpání pomocí teploměru, procent i zbývajícího času. Navíc mění barvy, čím je okno plnější nebo limit vyčerpanější, tím jasněji příslušná položka svítí.

![Status line](statusline.png)

## [`iterm-notify.sh`](iterm-notify.sh) – záložka, která si řekne o pozornost

Když Claude doběhne nebo se na něco ptá, obarví se mi záložka iTermu do modra. Zní to jako drobnost, ale při práci ve víc záložkách naráz je to přesně to, co potřebuju – nemusím přepínat a koukat, jestli už. Nejlepší je na tom detail, který mi dělal radost: záložka se odbarví sama ve chvíli, kdy na ni přepnu. Hlídá to watcher na pozadí, který se zeptá iTermu přes AppleScript, jestli je zrovna aktivní ta moje session – a jakmile je, uklidí barvu a skončí. Když je záložka aktivní už v momentě, kdy Claude doskončí, neobarví se vůbec, protože bych to stejně viděl. Napojené na tři hooky: `UserPromptSubmit` barvu maže, `Notification` a `Stop` ji rozsvítí. Funguje jen v iTerm2.

## [`green-line.sh`](green-line.sh) – nad rozbitým projektem se práce neuzavře

Nejlevnější věc z celého repozitáře a možná nejužitečnější. Je to `Stop` hook: než Claude ukončí tah, spustí typecheck, lint a testy, a když něco padá, **nepustí ho skončit** – dostane zpátky výstup a musí to dořešit. Rozdíl proti instrukci v pravidlech je zásadní: instrukce se dá zracionalizovat, skript ne.

Jedna výjimka, kterou přiznávám rovnou: když **druhý pokus nad týmž stavem** taky neprojde, hook pustí dál a nahlas to řekne. Nekonečná smyčka je horší než rozbitý build – ale znamená to, že brána je tvrdá jednou, ne napořád.

Skript přitom **nic neví o mém projektu** – přečte si sekci `## Příkazy` v jeho `CLAUDE.md` a spustí, co tam stojí. Je registrovaný jednou globálně a v projektu bez kontraktu neudělá nic.

Bezpečnostní vrstva, na kterou jsem přišel až při review vlastní práce: ten kontrakt je **kód ležící v repozitáři** a hooky se na povolení neptají. Naklonovat cizí projekt by stačilo k tomu, aby se mi spustilo, co si tam někdo napsal. Skript proto v projektu nespustí nic, dokud pro něj nevydám souhlas (`--allow`), a říká u toho na rovinu, co ten souhlas znamená: platí pro repozitář, ne pro ty konkrétní řádky. `npm test` spustí, co je v `package.json`, a to se neschvaluje.

## [`settings.json`](settings.json) – průběžně laděné permissions

Allowlist/denylist/asklist se snažím držet ve vyváženém poměru „bezpečnost vs. flow“. Cíl je nemuset odklikávat každou trivialitu, ale zároveň nenechat bez kontroly moc bezpečnostních děr. Tohle je vždycky lavírování na hraně a občas tu jdu vědomě lehce za hranu – ve prospěch svého pohodlí a na úkor středně rizikových operací. Takže si to k sobě rozhodně nekopírujte bezhlavě, ale můžete to vzít čistě inspiračně pro porovnání s vlastním nastavením.

## Než si odsud něco vezmete

Tohle je obsah mého `~/.claude`, ne balíček k instalaci. Když si budete něco kopírovat, počítejte s pár věcmi:

- **Absolutní cesty.** `settings.json` i skilly mají natvrdo `/Users/honza/…` – v hoocích, ve statusline, v permissions. Přepište je na své, jinak vám budou tiše selhávat.
- **Předpoklady.** Plugin [superpowers](https://github.com/obra/superpowers) – `/specify`, `/breakdown` a `/implement` jsou obálky nad ním a bez něj neběží; ostatní skilly ho nepotřebují. Dál macOS s [Homebrew](https://brew.sh), `jq` (bez něj nefunguje statusline, zelená linka ani dva hooky, které kontrolují uložené soubory), `coreutils` kvůli `gtimeout` (zelená linka jím hlídá strop na krok a zabíjí celou procesní skupinu, aby po zabitém testu nezůstal běžet watch-mode runner) a iTerm2 (na něj je navázané barvení záložky přes `iterm-notify.sh` – na jiném terminálu ty tři hooky selžou).
- **Část znalostí v repu není.** Skilly se opírají o soukromý adresář `~/Dev/context/` a odkazují do něj – `/compose` čte `compose/` a `archive/`, `/specify` a `/breakdown` se řídí `structure/structure.md`, `/implement` a `/review` stojí na `coding/coding.md` (jsou v něm brány kvality i jejich prahy) a jeho deterministická vrstva navíc počítá s `gitleaks`, `semgrep` a `shellcheck` – bez nich se ty kroky přeskočí a skill to nahlásí. Doménové znalosti žijí v `~/Dev/context/`, kde má každá doména vlastní adresář (`coding/`, `web/` včetně `admin.md`, `analytics/`, `text/`, `design/` včetně `slides.md`, `training/`, `worktree/`, `structure/`, `brand/`, `organizations/`) – odkazuje na ně `CLAUDE.md` a většinu z nich používá skill `/review`, který bez nich odvede jen půlku práce. To je moje soukromé know-how a osobní archiv, takže je tu nenajdete – ty skilly jsou k mání jako kostra, ne jako hotová věc.
- **Berte to po částech.** `RULES.md` funguje samostatně a použitelný je nejspíš hned. Skilly si projděte a upravte. `settings.json` si rozhodně proberte řádek po řádku – kromě permissions v něm jsou i hooky, statusline, pluginy a osobní nastavení modelu a jazyka.
- **Licence.** Všechno tady je pod [MIT](LICENSE) – berte si, co chcete, jen si to nechte na vlastní triko.
