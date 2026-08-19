# Moje Claude Code konfigurace

Tohle je moje osobní konfigurace [Claude Code](https://docs.claude.com/en/docs/claude-code), kterou tu sdílím pro inspiraci. Třeba tu najdete něco užitečného i pro vaši práci. Budu rád i za jakékoliv vaše nápady a připomínky, napište mi na e-mail [jantichy@jantichy.cz](mailto:jantichy@jantichy.cz)!

Co bych z celého repozitáře vypíchl, aby to neuteklo vaší pozornosti?

## [`CLAUDE.md`](CLAUDE.md) – hlavní soubor s instrukcemi

Na tomhle souboru je zajímavé hlavně to, že v něm skoro nic není 😉. Většina instrukcí je dekomponovaná do dalších .md souborů. Všimněte si, že mezi nimi rozlišuju ty, které obsahují kritické body společné pro všechny projekty a mají se použít vždy, a ty, které se načtou jen když je to podle situace potřeba. Brutálně se tím šetří kontextové okno.

## [`RULES.md`](RULES.md) – struktura a pořádek pod kontrolou

Kdo mě zná, tak ví, že jsem hodně citlivý na strukturovanost a čistotu návrhu. [OCD](https://cs.wikipedia.org/wiki/Obsedantn%C4%9B-kompulzivn%C3%AD_porucha) hadr neasi. A opravdu hodně trpím tím, jakých svévolností se dovede Claude v projektu dopustit, když se chvíli nehlídá. Tenhle soubor ho drží na uzdě napříč všemi mými projekty. Vedlejší efekt je, že mu pak většinu věcí stačí říct jenom jednou. A co se nevychytá tady, to dotáhne do dokonalosti skill `/consistency`.

## [`/consistency`](skills/consistency/) – ultimátní skill proti bordelu

Kompletní audit projektu na vnitřní konzistenci a pořádek. Spustí Explore agenta, který systematicky projde celý projekt a hledá: sémantické nekonzistence, protichůdné instrukce a zadání, strukturální nekonzistence všeho možného druhu, duplicity a redundance, zapomenuté zbytky po smazaných částech projektu, mrtvý kód a nepoužité závislosti, bezpečnostní nekonzistence, typové nesrovnalosti, drift mezi vrstvami… Následně je kategorizuje od kritických až po kosmetické. Mechanické opravy, kde existuje jen jedno správné řešení – rozbitý odkaz, nepoužitý import, počet v textu nesedící s tabulkou – provede rovnou a jen mi je vypíše. Sporné věci, kde se dá rozhodnout víc způsoby, se mnou pak prochází jednu po druhé, se srozumitelným vysvětlením, návrhem řešení a zpětnou verifikací provedených oprav.

## [`/cleanup`](skills/cleanup/) – ať po mně zůstane čisto a jasno

Když mám dlouho otevřenou session, dojdu na konec problému a chystám se odejít nebo zkompaktovat, tíží mě pokaždé to samé: neztratí se něco? Tenhle skill to řeší za mě. Nejdřív si přečte **surový transcript celé session** – tedy včetně té části, kterou už compact z kontextu vyhodil – a vytáhne z něj všechno, na čem jsme se dohodli, včetně důvodů a zavržených variant, odložených úkolů i postřehů mimo osu, u kterých padlo „ať se to neztratí". Každou takovou položku pak porovná se soubory a dopíše, přepíše nebo přesune tam, kam patří. Následně zavolá `/consistency`, spustí testy a kontroly, ověří, že README, všechna TODO a `CLAUDE.md` sedí, a že je Git čistý a všechno pushnuté. A na závěr to nejlepší: pošle na projekt **subagenta, který nemá žádný kontext** a čte jenom repozitář, jako by se do projektu zaučoval – a ten mi řekne, jestli je dokumentace soběstačná a pravdivá, kde bych musel hádat a co si protiřečí. Končí to jednoznačným verdiktem, jestli můžu odejít, nebo co ještě zbývá.

## [`/autocommit`](skills/autocommit/) – každá změna hned do Gitu

Zapne pro daný projekt režim, kdy Claude po každém logickém celku automaticky commituje. A pokud je nastavený remote, taky pushuje. Nehodí se do všech projektů, ale tam, kde mám hromadu rychlých iterací, mi to šetří desítky až stovky commit instrukcí za den.

## [`/autoprompt`](skills/autoprompt/) – ukládá všechny prompty

Zapne pro projekt automatické logování všech mých promptů na jedno snadno přístupné a čitelné místo, do souboru `PROMPTS.md` v rootu projektu. Při zapnutí dokonce backfilluje historii ze session souborů, takže získám kompletní záznam i zpětně. Ač to na první pohled nevypadá, dříve či později to opravdu doceníte. Pro sledování, jak se projekt vyvíjel, pro učení se vlastních anti-patternů v promptech, překvapivě často tam pošlete Clauda, aby si z toho něco zpětně vytahal nebo naučil…

## [`/project`](skills/project/) – nový projekt na pár kliknutí

Kdykoli zakládám nový projekt v čistém adresáři, řeším pořád dokola ty samé věci: git a remote, autocommit, autoprompt, jestli si Claude smí něco pamatovat do Memory nebo má všechno psát do `CLAUDE.md`, jaký je to vlastně typ projektu (vývoj, web, psaní, data...). Tenhle skill se mě na to všechno postupně zeptá – jedna otázka po druhé – a rovnou to nastaví, včetně `README.md` a `.gitignore`. Odklikávám, místo abych to pokaždé psal znovu.

## [`/compose`](skills/compose/) – texty, co znějí jako já

Napíše článek, post na sociální sítě nebo vlákno mým hlasem a stylem – ne obecnou AI-češtinou. Táhne to ze znalostní báze mého psaní (styl, ustálené obraty, jejich horní mez, ať to nesklouzne do parodie) a k tématu si navíc dohledá pár nejpodobnějších textů z archivu jako živé vzory. Moje názory a pointy si ale nikdy nevymýšlí – ty musím dodat sám.

## [`/transcript`](skills/transcript/) – nahrávky na přepis a chytré shrnutí

Hodím do složky pár zvukových nahrávek (schůzka, rozhovor, hlasová poznámka) a tenhle skill z nich udělá pořádek: každou přepíše do Markdownu a k tomu napíše jedno strukturované shrnutí napříč všemi – s tématy, klíčovými poznatky a hlavně soupisem domluv a úkolů na konci. Celý přepis běží **lokálně a offline** přes [whisper.cpp](https://github.com/ggml-org/whisper.cpp), takže žádná nahrávka neopustí můj počítač – u citlivých firemních schůzek k nezaplacení. Doslovný přepis navíc rovnou uhladí: vyhází „ehm", odstraní halucinace rozpoznávače, opraví přeslechnuté názvy podle kontextu a rozseká text do kapitol s nadpisy. Na začátku si sám ověří, že má vše potřebné nainstalované, takže si ho můžete rovnou zkopírovat a spustit.

## [`statusline.sh`](statusline.sh) – krásná a užitečná status line

Jednořádková status line, která mi ukazuje všechno, co potřebuju průběžně vidět: aktuální model, zaplnění kontextového okna, čerpání 5hodinového i týdenního limitu, aktuální adresář i stav Gitu. Vizualizace ukazuje čerpání pomocí teploměru, procent i zbývajícího času. Navíc mění barvy, čím je okno plnější nebo limit vyčerpanější, tím jasněji příslušná položka svítí.

![Status line](statusline.png)

## [`settings.json`](settings.json) – průběžně laděné permissions

Allowlist/denylist/asklist se snažím držet ve vyváženém poměru „bezpečnost vs. flow". Cíl je nemuset odklikávat každou trivialitu, ale zároveň nenechat bez kontroly moc bezpečnostních děr. Tohle je vždycky lavírování na hraně a občas tu jdu vědomě lehce za hranu – ve prospěch svého pohodlí a na úkor středně rizikových operací. Takže si to k sobě rozhodně nekopírujte bezhlavě, ale můžete to vzít čistě inspiračně pro porovnání s vlastním nastavením.

## Než si odsud něco vezmete

Tohle je obsah mého `~/.claude`, ne balíček k instalaci. Když si budete něco kopírovat, počítejte s pár věcmi:

- **Absolutní cesty.** `settings.json` i skilly mají natvrdo `/Users/honza/…` – v hoocích, ve statusline, v permissions. Přepište je na své, jinak vám budou tiše selhávat.
- **Předpoklady.** macOS s [Homebrew](https://brew.sh), `jq` (statusline i hooky bez něj nefungují) a iTerm2 (na něj jsou navázané notifikace přes `iterm-notify.sh` – na jiném terminálu ty tři hooky selžou).
- **Znalostní báze skillů nejsou v repu.** `/compose` čte `~/Dev/claude/compose/` a `~/Dev/archiv/`, checklist pro weby žije v `~/Dev/claude/WEB.md`. To je moje soukromé know-how a osobní archiv, takže je tu nenajdete – ty skilly jsou k mání jako kostra, ne jako hotová věc.
- **Berte to po částech.** `RULES.md` a `CODING.md` fungují samostatně a použitelné jsou nejspíš hned. Skilly si projděte a upravte. `settings.json` si rozhodně proberte řádek po řádku – co v něm je a proč, popisuje sekce o kus výš.
