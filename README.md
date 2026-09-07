# Konfigurace Claude Code

Tohle je moje osobní konfigurace [Claude Code](https://docs.claude.com/en/docs/claude-code), kterou tu sdílím pro inspiraci. Třeba tu najdete něco užitečného i pro vaši práci. Budu rád i za jakékoliv vaše nápady a připomínky, napište mi na e-mail [jantichy@jantichy.cz](mailto:jantichy@jantichy.cz)!

Co bych z celého repozitáře vypíchl, aby to neuteklo vaší pozornosti?

## Instrukce

### [`CLAUDE.md`](CLAUDE.md) – hlavní soubor s instrukcemi

Na tomhle souboru je zajímavé hlavně to, že v něm skoro nic není 😉. Většina instrukcí je dekomponovaná do dalších .md souborů. Všimněte si, že mezi nimi rozlišuju ty, které obsahují kritické body společné pro všechny projekty a mají se použít vždy, a ty, které se načtou jen když je to podle situace potřeba. Brutálně se tím šetří kontextové okno.

### [`RULES.md`](RULES.md) – struktura a pořádek pod kontrolou

Obecná pravidla práce napříč všemi projekty: jak se mnou Claude komunikuje, jak organizuje soubory a obsah, jak rozhoduje a kde končí rozsah zadání, jak zachází se změnami. Je tu i celý životní cyklus projektu – od `/project` až po `/release` –, který říká, co je čí krok a co který krok naopak dělat nemá. A tabulka, podle které se vybírá model a effort pro každý typ úkolu: na návrhu a na ověřování nálezů se nešetří, mechanický sběr jede levně, a **levný model se vyplatí jen tam, kde se jeho chyba pozná levně**.

### [`STRUCTURE.md`](STRUCTURE.md) – každý projekt vypadá uvnitř stejně

Konvence, kterou drží každý můj projekt: co je v `CLAUDE.md`, co v `README.md` a co v `docs/` – tedy kam patří úkol, kam nezávazný nápad, kam rozhodnutí i s variantami, které jsem zavrhl, a kam záznam o hotové práci. Díky ní se dá vejít do libovolného projektu a hned vědět, kde co hledat; a hlavně vědí kam zapsat i skilly, kterých je na to půl tuctu. Zakládá ji `/project`, ale nepatří jemu – čte ji devět dalších skillů a každý si z ní bere něco jiného.

### [`PTYDEPE.md`](PTYDEPE.md) – termíny, které znamenají to, co si myslíme

Claude si zvykne na slovo, které v konverzaci padlo jednou a třeba omylem, a začne ho používat napříč projekty, jako by to byl zavedený pojem. Tenhle soubor je proti tomu: každý termín, na kterém jsme se dohodli, tu má zapsané, co znamená, v jakém rozsahu platí a co se jím naopak neoznačuje. Nejcennější je vždycky ta poslední část – termín se nejčastěji nekazí tím, že by se přejmenoval, ale tím, že se tiše rozšíří na příbuznou věc.

### [`WORKTREE.md`](WORKTREE.md) – několik rozdělaných věcí vedle sebe

Pravidla uspořádání, ve kterém má každá rozdělaná větev vlastní adresář na disku, takže nad projektem může běžet několik sessions naráz, aniž si přepisují soubory. Popisuje, co kde leží, jak se větev zakládá a dokončuje, proč se v hlavním adresáři nepracuje a proč v kořeni takového projektu přestane fungovat git. Zapnout a zrušit to umí [`/worktree`](skills/worktree/), ale samotná pravidla jsou tady – čte je totiž i příprava a většina ostatních skillů, tedy i ten, kdo `/worktree` nainstalovaný nemá.

### [`skills/SKILLS.md`](skills/SKILLS.md) – norma, jak vypadá skill

Dlouho jsem tvar svých skillů nikde zapsaný neměl – vymyslel jsem ho jednou a pak ho u každého dalšího skillu opsal, což z něj dělá zvyk, ne standard. Tohle je jeho sepsání a zároveň revize: co obstálo (vymezení proti **jmenovanému** sousedovi, ověřovatel, jehož úkolem je nález vyvrátit, jednoznačný závěrečný verdikt), co byla jen setrvačnost (příprava opsaná v každém skillu zvlášť) a co chybělo (sekce s častými chybami, mez délky, progresivní odhalení do vedlejších souborů). Je tu i pravidlo, které mi dlouho unikalo, přestože jsem ho už dvakrát použil: **skládej, nepiš znovu** – než napíšeš krok, zjisti, jestli ho neumí vestavěný skill, plugin nebo hook, a jestli ho nejde jen obalit tak, aby se ta implementace dala později vyměnit beze změny volání.

### [`skills/PREFLIGHT.md`](skills/PREFLIGHT.md) – společný začátek běhu

Kořen projektu, worktree layout, co se čte z projektového `CLAUDE.md`, stav pracovního stromu, průběžná kontrola a určení rozsahu z gitu. Čtrnáct skillů to mělo každý svoje, což je nejhrubší porušení „single source of truth", jakého jsem se v téhle konfiguraci dopustil. Teď je to sepsané na jednom místě a skill si má psát jen svoje odchylky. **Převádějí se postupně** – nové skilly už vznikají rovnou podle něj, zbytek čeká, až ho proženu `/skill update`. Výčet, kdo je kde, tady schválně není: rozešel by se po každém dalším převodu.

## Skilly životního cyklu projektu

Následující skilly tvoří jeden životní cyklus od založení projektu po nasazení a jdou tu v pořadí, ve kterém se pouštějí. Projít se nemusí celý – u drobné změny odpadá zadání i plán, u projektu bez kódu i nasazení.

### [`/project`](skills/project/) – projekt nastavený na pár kliknutí

Zeptá se postupně na všechno, co se u nového projektu řeší pokaždé znovu – název, git a remote, uspořádání na disku, dokumentační strukturu, autocommit, typ projektu, spouštěcí příkazy, doménové checklisty – a rovnou to nastaví. Umí i projekty, které už existují, a hlavně se k nim po čase vrátit: pozná svůj vlastní otisk a místo otázek projde projekt proti tomu, jak standardy vypadají dnes. Tím řeší nepříjemnou vlastnost celé téhle vrstvy – konfigurace se vyvíjí dál, ale projekt založený loni zůstane stát a sám o tom neřekne.

### [`/discovery`](skills/discovery/) – co je venku, než začnete stavět

Zjistí, do jakého světa produkt vstupuje: kdo to už dělá, co to umí a za kolik, čím to lidé řeší dneska, když na to nemají nástroj, a na co si u stávajících řešení stěžují. Z toho vytřídí, co produkt musí umět, aby ho někdo vzal vážně, a čím se dá odlišit – ale jen tak, aby to šlo doložit. K tomu sepíše registr rizik, ve kterém má každá položka povinné pole *co se kvůli tomu v produktu změní*. Stojí před zadáním schválně: analýza, která dorazí až po schválené specifikaci, se buď ignoruje, nebo znamená přepis všeho.

### [`/specify`](skills/specify/) – z nápadu zadání, než se sáhne na kód

Vyptá se mě na záměr a udělá z něj **dva dokumenty**: `requirements.md` odpovídá na otázku co stavíme a proč, `architecture.md` na otázku jak. Hranici mezi nimi drží tvrdě, včetně testu, kam která věta patří: *změní se to, když vyměním databázi?* A dokud není zadání schválené, nesmí vzniknout ani řádek kódu, ani scaffold.

### [`/oponent`](skills/oponent/) – oponentura na to, co nejde otestovat

Pošle na hotový dokument agenty, kteří **nemají z naší session žádný kontext** a čtou jenom soubory, každého z jiného hlediska. Je to krok mezi zadáním a plánem, protože jinak návrh neměří nikdo: `/review` ověřuje kód proti specifikaci, ale samotnou specifikaci nikdo proti ničemu. Každou závažnou námitku pak dostane ověřovatel s jediným úkolem – **vyvrátit ji**.

### [`/breakdown`](skills/breakdown/) – ze zadání implementační plán

Vyrobí ze schváleného zadání `docs/plan.md` – seřazený seznam úkolů velikosti pár minut, kde každý má konkrétní soubory, hotový kód testu a příkaz, kterým se ověří, že je hotový. Plán se předkládá ke schválení, protože je to poslední levné místo, kde se dá otočit.

### [`/implement`](skills/implement/) – odpracování plánu úkol po úkolu

Projde plán od začátku do konce, u každého úkolu test, kód, průběžná kontrola a commit. Umí navázat na rozdělaný plán a nevěří přitom zaškrtávátkům – ověří si v kódu, že odškrtnuté úkoly opravdu existují a procházejí. Nabídne tři režimy podle toho, jak často se do toho chci dívat.

### [`/review`](skills/review/) – panel nezávislých pohledů na hotovou práci

Prověří hotovou práci před uzavřením ze tří stran: nejdřív nástroje projektu, pak paralelní panel agentů, kde každý má jediné hledisko – korektnost, bezpečnost, data a stavy, provoz, testy, agentní infrastruktura, moje doménové standardy –, a nakonec ověřovatele, jehož úkolem je nález **vyvrátit**. Co ověření nepřežije, se mi vůbec nezobrazí.

### [`/consistency`](skills/consistency/) – ultimátní skill proti bordelu

Audit vnitřní konzistence: protichůdné instrukce, duplicity, zapomenuté zbytky po smazaných částech, mrtvý kód, drift mezi vrstvami. Jednoznačné opravy udělá rovnou, o sporných se mnou mluví jednu po druhé. A pamatuje si, co jsem rozhodl neopravovat – jen do chvíle, než se ten kód změní.

### [`/cleanup`](skills/cleanup/) – ať po mně zůstane čisto a jasno

Před opuštěním nebo zkompaktováním session přečte celou konverzaci – včetně části, kterou už compact vyhodil z kontextu – a zapíše všechno dohodnuté tam, kam to patří, i s důvody a zavrženými variantami. Pak hledá druhou věc: co v konverzaci zůstalo viset bez vypořádání, a probere to se mnou, dokud je koho se ptát. Na konec pošle na projekt agenta bez kontextu, který řekne, jestli z dokumentace jde na dnešní práci navázat.

### [`/attack`](skills/attack/) – zkusit aplikaci rozbít

Zvedne aplikaci lokálně a pošle na ni agenty, kteří ji zkouší rozbít – každý s jedním vektorem: nesmyslné vstupy, přeskočené a zopakované kroky, cizí ID v adrese, mezní data, výpadek sítě uprostřed odesílání. Na rozdíl od `/review`, který kód čte, tenhle ho spouští. Každý nález musí mít reprodukční postup a každá oprava regresní test; útočí se výhradně na lokální instanci nad testovacími daty, a že tomu tak opravdu je, se dokládá příkazem, ne slibem.

### [`/release`](skills/release/) – nasazení jako vědomý úkon, ne vedlejší efekt

Nasadí do produkce přes **oddělenou nasazovací větev**, takže `main` zůstane integrační a merge feature nic nenasazuje. Před nasazením projde kontroly, zvlášť řeší migrace dopředu kompatibilně a nikdy se nespustí sám. A tím nekončí: poslední fází je **sledovací okno** s konkrétním koncem, protože celá třída chyb se projeví až později. Dokud okno neuplyne a někdo ho výslovně neuzavře, nasazení není hotové.

## Skilly mimo životní cyklus

Tyhle se pouštějí podle potřeby, nezávisle na fázi projektu. Jsou seřazené abecedně.

### [`/autocommit`](skills/autocommit/) – každá změna hned do Gitu

Zapne pro daný projekt režim, kdy Claude po každém logickém celku automaticky commituje, a pokud je nastavený remote, taky pushuje. Nehodí se do všech projektů, ale tam, kde mám hromadu rychlých iterací, mi to šetří desítky až stovky commit instrukcí za den.

### [`/compose`](skills/compose/) – texty, co znějí jako já

Napíše článek, post na sociální sítě nebo vlákno mým hlasem a stylem – ne obecnou AI-češtinou. Táhne to ze znalostní báze mého psaní a k tématu si dohledá nejpodobnější texty z archivu jako živé vzory. Tu bázi umí i postavit: `collect` provede posbíráním všeho, co člověk kdy napsal – exporty ze sociálních sítí, články z webů, zálohy po webech, které už nestojí –, a `profile` z toho vydestiluje popis hlasu a později ho doplňuje o to, co přibylo. Moje názory a pointy si ale nikdy nevymýšlí, ty musím dodat sám.

### [`/invoicing`](skills/invoicing/) – faktury na konci měsíce bez ručního sčítání

Sečte hodiny z timetrackingu po klientech, ukáže mi, co napočítal a co je mu podezřelé, vystaví faktury a nechá v mailu rozepsaný draft s fakturou a výkazem hodin v příloze. **Odeslat ho musím vždycky já** – tvrdá stopka, která platí i tehdy, když ho o odeslání sám uprostřed běhu poprosím. Umí i opačný směr: dohledat čas, který jsem si zapomněl natrackovat. Sazby a dohody s klienty v tomhle repozitáři nejsou, skill je jen rámec.

### [`/ptydepe`](skills/ptydepe/) – slova, kterým rozumíme jenom my dva

Claude si z konverzace odnese slovo, které jsem použil jednou a třeba omylem, a začne ho používat jako zavedený pojem – napříč projekty, v dokumentaci, v názvech souborů. Tenhle skill takové termíny vyhledá, projedná se mnou jeden po druhém, a co odsouhlasím, nahradí ve všech repozitářích naráz. Rozhodnutí i s důvodem pak drží [`PTYDEPE.md`](PTYDEPE.md), takže se totéž slovo nezavádí za měsíc znovu.

### [`/replace`](skills/replace/) – přejmenovat něco a fakt všude

Přejmenuje pojem napříč projektem včetně **odvozených tvarů** a české skloňované varianty, kterou grep na základní tvar nenajde. Sahá i na názvy souborů a adresářů, přesouvá přes `git mv`, ať se neztratí historie, a hlídá pořadí – delší tvary před kratšími. Povinný poslední krok je kontrolní průchod na starý tvar, který musí vrátit nulu.

### [`/report`](skills/report/) – data do jednoho souboru, co jde poslat komukoliv

Z exportu z GA4, CSV nebo výsledku dotazu do BigQuery udělá jeden interaktivní HTML soubor, který jde otevřít dvojklikem odkudkoliv: žádné CDN, aby fungoval offline i za pět let, a datum vygenerování zapsané natvrdo. Než ho pustí ven, projde hotový soubor na osobní údaje a na přístupové údaje, které do reportu proteču samy z výpočetního skriptu nebo ze screenshotu administrace.

### [`/skill`](skills/skill/) – skilly, které se samy udržují

Zakládá nové skilly proti normě, vytěží skill z rozdělané konverzace, **prožene existující skilly revizí** a umí skill i zrušit včetně všech stop. Revize je ten důvod, proč vznikl: norma se posouvá dál, ale hotové skilly zůstanou stát a samy o tom neřeknou. Klade přitom otázku, kterou nepoloží nikdo jiný – *nevzniklo mezitím něco, co tenhle skill dělá ručně?*

### [`/transcript`](skills/transcript/) – nahrávky na přepis a chytré shrnutí

Ze zvukových i obrazových nahrávek udělá čitelný přepis a strukturované shrnutí se soupisem domluv a úkolů na konci; na vyžádání rozliší i mluvčí, takže úkoly mají majitele. Přepis běží **lokálně a offline**, takže nahrávka neopustí můj počítač. Než začne, podstrčí rozpoznávači jména a názvy, které v nahrávce padnou – ta pak nekomolí lidi ani firmy. A když se rozpoznávač uprostřed dlouhé nahrávky zakousne, umí ji dopřepsat po úsecích: problémový kus přeskočí a o zbytek nepřijdu.

### [`/worktree`](skills/worktree/) – každá rozdělaná větev ve vlastním adresáři

Přepne projekt do uspořádání, kde má každá rozdělaná větev vlastní adresář, takže nad ním může běžet několik sessions naráz, aniž si přepisují soubory. Umí to i zpátky. Přeskládává `.git`, tedy to nejcitlivější v repozitáři – proto nejdřív zálohuje, na konci porovná a smaže zálohu, teprve když porovnání vyjde. Pravidla, jak se v takovém projektu pracuje, si nainstaluje rovnou do něj, takže platí od začátku každé session, aniž ho člověk volá.

## Hooky, skripty a nastavení

### [`statusline.sh`](statusline.sh) – krásná a užitečná status line

Jednořádková status line, která mi ukazuje všechno, co potřebuju průběžně vidět: aktuální model, zaplnění kontextového okna, čerpání 5hodinového i týdenního limitu, aktuální adresář i stav Gitu. Čerpání vizualizuje teploměrem, procenty i zbývajícím časem a mění barvy podle toho, jak je na tom blízko limitu.

![Status line](statusline.png)

### [`iterm-notify.sh`](iterm-notify.sh) – záložka, která si řekne o pozornost

Když Claude doběhne nebo se na něco ptá, obarví se záložka iTermu do modra, a jakmile na ni přepnu, barva sama zmizí. Je-li záložka aktivní už ve chvíli, kdy Claude doskončí, neobarví se vůbec. Napojené na tři hooky: `UserPromptSubmit` barvu maže, `Notification` a `Stop` ji rozsvítí. Funguje jen v iTerm2.

### [`verify.sh`](verify.sh) – nad rozbitým projektem se práce neuzavře

`Stop` hook, který před ukončením odpovědi spustí typecheck, lint a testy, a když něco padá, **nepustí Clauda skončit** – dostane zpátky výstup a musí to dořešit. O projektu nic neví: přečte si sekci `## Kontrakt příkazů` v jeho `CLAUDE.md` a spustí, co tam stojí, takže je registrovaný jednou globálně a v projektu bez kontraktu neudělá nic. A protože je ten kontrakt kód ležící v repozitáři, nespustí v něm nic, dokud pro něj nevydám souhlas (`--allow`) – ten platí pro **celý repozitář včetně jeho worktree**, takže nová větev si o něj neříká znovu. Rozlišuje přitom dvě různé věci: **test, který našel chybu**, odpověď zablokuje, kdežto **krok, který vůbec nejde spustit**, jen ohlásí – tam není co opravovat na kódu, ale na prostředí.

### [`tests/`](tests/) – testy nad konfigurací, ne nad kódem

Skilly a pravidla jsou z velké části text, který nikdo nespouští, takže se jejich vady projeví až za běhu a obvykle tiše: režim popsaný v těle skillu, který chybí v jeho hlavičce, odkaz na soubor nebo sekci, co mezitím zmizela, skill bez vlastního README. Kde skill vlastní skripty má – `/compose` je má –, testy hlídají aspoň to, že se přeloží a že si cíl neodvozují ze svého umístění. Druhá sada testuje **průběžnou kontrolu** – jediné místo v celé konfiguraci, které něco doopravdy vynucuje, a tedy to, kde tichá regrese stojí nejvíc. Obojí stojí nula tokenů a běží v průběžné kontrole po každé odpovědi. Jen standardní knihovna Pythonu, žádná instalace.

### [`settings.json`](settings.json) – průběžně laděné permissions

Allowlist/denylist/asklist se snažím držet ve vyváženém poměru „bezpečnost vs. flow“. Cíl je nemuset odklikávat každou trivialitu, ale zároveň nenechat bez kontroly moc bezpečnostních děr. Tohle je vždycky lavírování na hraně a občas tu jdu vědomě lehce za hranu – ve prospěch svého pohodlí a na úkor středně rizikových operací. Takže si to k sobě rozhodně nekopírujte bezhlavě, ale můžete to vzít čistě inspiračně pro porovnání s vlastním nastavením.

## Než si odsud něco vezmete

Tohle je obsah mého `~/.claude`, ne balíček k instalaci. Když si budete něco kopírovat, počítejte s pár věcmi:

- **Absolutní cesty.** `settings.json` i skilly mají natvrdo `/Users/honza/…` – v hoocích, ve statusline, v permissions. Přepište je na své, jinak vám budou tiše selhávat.
- **Předpoklady.** Plugin [superpowers](https://github.com/obra/superpowers), na kterém stojí `/specify`, `/breakdown` a `/implement`. **`/skill` k tomu potřebuje `skill-creator`** – bez něj mu odpadne režim `extract` a celá měřicí část; sám si na to posvítí a řekne, co se tím neověřilo. Dál macOS s [Homebrew](https://brew.sh), `jq`, `coreutils` kvůli `gtimeout` a iTerm2 kvůli barvení záložky. **`shellcheck` a `ruff` jsou tady povinné** – dohromady tvoří `lint` v kontraktu tohohle repozitáře, takže bez nich hlásí průběžná kontrola po každé odpovědi nespustitelný krok. `ruff` běží jen na chybová pravidla, ne na styl. Volitelné jsou `gitleaks` a `semgrep`: bez prvního sáhne `/review` po slabší grep-heuristice, bez druhého příslušná kontrola odpadne – a skill to v obou případech napíše do výpisu *Nezkontrolováno*. **`/compose` potřebuje Python 3** na převod exportů ze sociálních sítí a u Bluesky k tomu balíček `cbor2`. **`/transcript` má vlastní sadu navíc:** `ffmpeg`, `whisper-cpp` a stažené modely, u rozlišení mluvčích k tomu `pyannote.audio` ve vlastním venv, účet a token na HuggingFace a **ruční odsouhlasení licencí tří gated repozitářů v prohlížeči** – to je jediný předpoklad v celém repozitáři, který nejde zautomatizovat. Velikosti a přesné příkazy drží [jeho `SKILL.md`](skills/transcript/SKILL.md); skill si na chybějící kusy posvítí sám.
- **Část znalostí v repu není.** Skilly se opírají o soukromý adresář `~/Dev/context/` s doménovými standardy (`coding/`, `web/`, `analytics/`, `text/`, `design/`, `training/` a další) a odkazují do něj. To je moje soukromé know-how a osobní archiv, takže ho tu nenajdete – ty skilly jsou k mání jako kostra, ne jako hotová věc.
- **Berte to po částech.** `RULES.md` funguje samostatně a použitelný je nejspíš hned. Skilly si projděte a upravte. `settings.json` si rozhodně proberte řádek po řádku – kromě permissions v něm jsou i hooky, statusline, pluginy a osobní nastavení modelu a jazyka.
- **Licence.** Všechno tady je pod [MIT](LICENSE) – berte si, co chcete, jen si to nechte na vlastní triko.
