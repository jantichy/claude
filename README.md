# Konfigurace Claude Code

Tohle je moje osobní konfigurace [Claude Code](https://docs.claude.com/en/docs/claude-code), kterou tu sdílím pro inspiraci. Třeba tu najdete něco užitečného i pro vaši práci. Budu rád i za jakékoliv vaše nápady a připomínky, napište mi na e-mail [jantichy@jantichy.cz](mailto:jantichy@jantichy.cz)!

Co bych z celého repozitáře vypíchl, aby to neuteklo vaší pozornosti?

## Instrukce

### [`CLAUDE.md`](CLAUDE.md) – hlavní soubor s instrukcemi

Na tomhle souboru je zajímavé hlavně to, že v něm skoro nic není 😉. Většina instrukcí je dekomponovaná do dalších .md souborů. Všimněte si, že mezi nimi rozlišuju ty, které obsahují kritické body společné pro všechny projekty a mají se použít vždy, a ty, které se načtou jen když je to podle situace potřeba. Brutálně se tím šetří kontextové okno.

### [`RULES.md`](RULES.md) – struktura a pořádek pod kontrolou

Obecná pravidla práce napříč všemi projekty: jak se mnou Claude komunikuje, jak organizuje soubory a obsah, jak zachází se změnami. Je tu i celá osa životního cyklu práce – od `/project` až po `/release` – která říká, co je čí krok a co který krok naopak dělat nemá.

## Skilly, jak jdou po sobě

Následující skilly tvoří jednu osu od založení projektu po nasazení. Nemusí se projít celá – u drobné změny odpadá zadání i plán, u projektu bez kódu i nasazení.

### [`/project`](skills/project/) – projekt nastavený na pár kliknutí

Postupně se zeptá na všechno, co se u nového projektu řeší pokaždé znovu – lidský název, git a remote, autocommit, autoprompt, typ projektu, kontrakt příkazů – a rovnou to nastaví včetně `README.md`, `.gitignore` a standardní struktury. Umí i projekty, které už existují: udělá inventuru a dorovná je na moje dnešní preference, nikdy nepřepíše soubor bez zeptání. Zvládá i **worktree layout**, tedy kontejner s `.bare` a jedním podadresářem na větev.

### [`/specify`](skills/specify/) – z nápadu zadání, než se sáhne na kód

Vyptá se mě na záměr a udělá z něj **dva dokumenty**: `requirements.md` odpovídá na otázku co stavíme a proč, `architecture.md` na otázku jak. Hranici mezi nimi drží tvrdě, včetně testu, kam která věta patří: *změní se to, když vyměním databázi?* A dokud není zadání schválené, nesmí vzniknout ani řádek kódu, ani scaffold.

### [`/oponent`](skills/oponent/) – oponentura na to, co nejde otestovat

Nezávislý posudek dokumentu, který jsem psal s Claudem – pozicování, cenotvorby, datového modelu. Pošle na něj agenty, kteří **nemají z naší session žádný kontext** a čtou jenom soubory; každý s jiným úhlem: vnitřní rozpory, nejslabší předpoklad, pohled cílové skupiny, ekonomika. Zamítnuté námitky se zapisují, aby je příští oponentura nenašla znovu jako nové.

### [`/breakdown`](skills/breakdown/) a [`/implement`](skills/implement/) – plán a jeho odpracování

`/breakdown` vyrobí ze zadání `docs/plan.md` – seřazený seznam úkolů, kde každý má konkrétní soubory, kód testu a ověřitelné kritérium – a `/implement` ho odpracuje úkol po úkolu, každý do zelené linky a do commitu. Na pozadí obojí řídí [superpowers](https://github.com/obra/superpowers); moje obálky navíc vynucují cesty v `docs/`, odmítnou se spustit bez schváleného zadání a u rozdělaného plánu nevěří zaškrtávátkům, ale ověří si v kódu, že odškrtnuté úkoly opravdu existují.

### [`/review`](skills/review/) – panel nezávislých pohledů na hotovou práci

Prověří hotovou práci před uzavřením ze tří stran: nejdřív nástroje projektu (testy, lint, audit závislostí, scan tajemství, statická analýza), pak paralelní panel agentů, kde každý má jediný úhel pohledu – korektnost, bezpečnost, data a stavy, provoz, testy, moje doménové standardy – a nakonec ověřovatele, jehož úkolem je nález **vyvrátit**. Co ověření nepřežije, se mi vůbec nezobrazí.

### [`/consistency`](skills/consistency/) – ultimátní skill proti bordelu

Kompletní audit projektu na vnitřní konzistenci: protichůdné instrukce, duplicity, zapomenuté zbytky po smazaných částech, mrtvý kód, drift mezi vrstvami. Nálezy roztřídí od kritických po kosmetické, jednoznačné opravy udělá rovnou a o sporných se mnou mluví jednu po druhé.

### [`/cleanup`](skills/cleanup/) – ať po mně zůstane čisto a jasno

Před opuštěním nebo zkompaktováním session projde celou konverzaci – včetně části, kterou už compact vyhodil z kontextu – a zapíše všechno dohodnuté tam, kam to patří, i s důvody a zavrženými variantami. Pak pošle na projekt agenta bez kontextu, který ověří, jestli z dokumentace jde na dnešní práci navázat, commitne a dá jednoznačný verdikt: můžeš jít, nebo tohle ještě zbývá.

### [`/attack`](skills/attack/) – zkusit aplikaci rozbít

Zvedne aplikaci lokálně a pošle na ni agenty, kteří ji zkouší rozbít – každý s jedním vektorem: nesmyslné vstupy, přeskočené a zopakované kroky, cizí ID v adrese, mezní data, výpadek sítě uprostřed odesílání. Na rozdíl od `/review`, který kód čte, tenhle ho spouští. Každý nález musí mít reprodukční postup a každá oprava regresní test. Pouštím ho před nasazením, ne po každé feature, a útočí se výhradně na lokální instanci nad testovacími daty.

### [`/release`](skills/release/) – nasazení jako vědomý úkon, ne vedlejší efekt

Nasadí do produkce přes **oddělenou nasazovací větev** `production`, takže `main` zůstane integrační a merge feature nic nenasazuje. Před nasazením hlídá čistý strom, zelenou linku, produkční build, audit závislostí a jestli proběhlo `/review` a `/attack`; zvlášť řeší **migrace** dopředu kompatibilně, aby rollback kódu neshodil aplikaci na datech nové verze. Nikdy se nespustí sám, nic neopravuje a po nasazení ověřuje na produkční URL.

## Skilly mimo osu

Tyhle se pouštějí podle potřeby, nezávisle na fázi projektu.

### [`/autocommit`](skills/autocommit/) – každá změna hned do Gitu

Zapne pro daný projekt režim, kdy Claude po každém logickém celku automaticky commituje, a pokud je nastavený remote, taky pushuje. Nehodí se do všech projektů, ale tam, kde mám hromadu rychlých iterací, mi to šetří desítky až stovky commit instrukcí za den.

### [`/autoprompt`](skills/autoprompt/) – ukládá všechny prompty

Zapne pro projekt automatické logování všech mých promptů do souboru `prompts.md` a při zapnutí backfilluje i historii ze session souborů, takže mám kompletní záznam zpětně. Ač to na první pohled nevypadá, dříve či později to opravdu doceníte – pro sledování, jak se projekt vyvíjel, i pro učení se vlastních anti-patternů v promptech.

### [`/replace`](skills/replace/) – přejmenovat něco a fakt všude

Přejmenuje pojem napříč projektem včetně **odvozených tvarů** a české skloňované varianty, kterou grep na základní tvar nenajde. Sahá i na názvy souborů a adresářů, přesouvá přes `git mv`, ať se neztratí historie, a hlídá pořadí – delší tvary před kratšími. Povinný poslední krok je kontrolní průchod na starý tvar, který musí vrátit nulu.

### [`/report`](skills/report/) – data do jednoho souboru, co jde poslat komukoliv

Z exportu z GA4, CSV nebo výsledku dotazu do BigQuery udělá jeden interaktivní HTML soubor, který jde otevřít dvojklikem odkudkoliv: žádné CDN, aby fungoval offline i za pět let, `charset=utf-8` hned na začátku a datum vygenerování zapsané natvrdo. Než ho pustí ven, projde hotový soubor na osobní údaje a na přístupové údaje, které do reportu proteču samy z výpočetního skriptu nebo ze screenshotu administrace.

### [`/compose`](skills/compose/) – texty, co znějí jako já

Napíše článek, post na sociální sítě nebo vlákno mým hlasem a stylem – ne obecnou AI-češtinou. Táhne to ze znalostní báze mého psaní a k tématu si dohledá nejpodobnější texty z archivu jako živé vzory. Moje názory a pointy si ale nikdy nevymýšlí, ty musím dodat sám.

### [`/transcript`](skills/transcript/) – nahrávky na přepis a chytré shrnutí

Ze složky zvukových nahrávek udělá pořádek: každou přepíše do Markdownu a k tomu napíše jedno strukturované shrnutí napříč všemi, se soupisem domluv a úkolů na konci. Přepis běží **lokálně a offline** přes [whisper.cpp](https://github.com/ggml-org/whisper.cpp), takže nahrávka neopustí můj počítač. Text rovnou uhladí – vyhází „ehm“, odstraní halucinace rozpoznávače, opraví přeslechnuté názvy a rozseká to do kapitol.

## Hooky, skripty a nastavení

### [`statusline.sh`](statusline.sh) – krásná a užitečná status line

Jednořádková status line, která mi ukazuje všechno, co potřebuju průběžně vidět: aktuální model, zaplnění kontextového okna, čerpání 5hodinového i týdenního limitu, aktuální adresář i stav Gitu. Čerpání vizualizuje teploměrem, procenty i zbývajícím časem a mění barvy podle toho, jak je na tom blízko limitu.

![Status line](statusline.png)

### [`iterm-notify.sh`](iterm-notify.sh) – záložka, která si řekne o pozornost

Když Claude doběhne nebo se na něco ptá, obarví se záložka iTermu do modra, a jakmile na ni přepnu, barva sama zmizí. Je-li záložka aktivní už ve chvíli, kdy Claude doskončí, neobarví se vůbec. Napojené na tři hooky: `UserPromptSubmit` barvu maže, `Notification` a `Stop` ji rozsvítí. Funguje jen v iTerm2.

### [`green-line.sh`](green-line.sh) – nad rozbitým projektem se práce neuzavře

`Stop` hook, který před ukončením tahu spustí typecheck, lint a testy, a když něco padá, **nepustí Clauda skončit** – dostane zpátky výstup a musí to dořešit. O projektu nic neví: přečte si sekci `## Příkazy` v jeho `CLAUDE.md` a spustí, co tam stojí, takže je registrovaný jednou globálně a v projektu bez kontraktu neudělá nic. Protože je ten kontrakt kód ležící v repozitáři a hooky se na povolení neptají, nespustí v projektu nic, dokud pro něj nevydám souhlas (`--allow`, výpis `--list`, odebrání `--revoke`). Každý krok má strop 60 sekund a když neprojde ani druhý pokus nad týmž stavem, hook pustí dál a nahlas to řekne.

### [`settings.json`](settings.json) – průběžně laděné permissions

Allowlist/denylist/asklist se snažím držet ve vyváženém poměru „bezpečnost vs. flow“. Cíl je nemuset odklikávat každou trivialitu, ale zároveň nenechat bez kontroly moc bezpečnostních děr. Tohle je vždycky lavírování na hraně a občas tu jdu vědomě lehce za hranu – ve prospěch svého pohodlí a na úkor středně rizikových operací. Takže si to k sobě rozhodně nekopírujte bezhlavě, ale můžete to vzít čistě inspiračně pro porovnání s vlastním nastavením.

## Než si odsud něco vezmete

Tohle je obsah mého `~/.claude`, ne balíček k instalaci. Když si budete něco kopírovat, počítejte s pár věcmi:

- **Absolutní cesty.** `settings.json` i skilly mají natvrdo `/Users/honza/…` – v hoocích, ve statusline, v permissions. Přepište je na své, jinak vám budou tiše selhávat.
- **Předpoklady.** Plugin [superpowers](https://github.com/obra/superpowers), na kterém stojí `/specify`, `/breakdown` a `/implement`. Dál macOS s [Homebrew](https://brew.sh), `jq`, `coreutils` kvůli `gtimeout` a iTerm2 kvůli barvení záložky. Volitelně `gitleaks`, `semgrep` a `shellcheck` – bez nich se příslušné kroky `/review` přeskočí a skill to nahlásí.
- **Část znalostí v repu není.** Skilly se opírají o soukromý adresář `~/Dev/context/` s doménovými standardy (`coding/`, `web/`, `analytics/`, `text/`, `design/`, `training/`, `structure/` a další) a odkazují do něj. To je moje soukromé know-how a osobní archiv, takže ho tu nenajdete – ty skilly jsou k mání jako kostra, ne jako hotová věc.
- **Berte to po částech.** `RULES.md` funguje samostatně a použitelný je nejspíš hned. Skilly si projděte a upravte. `settings.json` si rozhodně proberte řádek po řádku – kromě permissions v něm jsou i hooky, statusline, pluginy a osobní nastavení modelu a jazyka.
- **Licence.** Všechno tady je pod [MIT](LICENSE) – berte si, co chcete, jen si to nechte na vlastní triko.
