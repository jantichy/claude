# Rozhodnutí

Rozhodnutí o konfigurační vrstvě a cesta k nim: jaký problém to řešilo, jaké varianty byly ve hře, proč vyhrála tahle a proč padly ostatní.

**Repozitář je veřejný.** Nic, co sem přibude, nesmí prozradit **obsah** soukromého `~/Dev/context/` – jméno klienta či organizace, sazbu, obchodní nebo osobní údaj, detail přístupu ke klientskému systému, jméno klientského projektu ani know-how, které se prodává. Struktura toho adresáře veřejná je a `README.md` ji sám píše; konkrétní obsah ne. Podrobněji `.claude/CLAUDE.md`, *Výjimky z obecných pravidel*.

**Týká-li se rozhodnutí jednoho skillu, patří rovnou do jeho `SKILL.md`** k místu, kde platí – tam ho příště najde ten, kdo ho potřebuje. Sem jde to, co platí napříč.

### 2026-09-01 – `RULES.md` má vymezený rozsah; definice `docs/*` patří do `structure.md`

Oponentura `~/.claude/RULES.md` (skill `/oponent`, tři nezávislá hlediska nad vnitřním rozporem) našla 28 nálezů. Většina měla jednu příčinu: `RULES.md` byl jediný ze čtyř normativních souborů bez sekce „co sem nepatří“ – `structure.md`, `coding.md` i `CLAUDE.md` ji mají. Bez kritéria se pravidlo zapisovalo tam, kde ho autor psal, a vznikly duplicity: tři definice `docs/*` ve dvou souborech (věta o `todo.md` doslova včetně tučnění), řetěz `prd → design → plan → kód` na čtyřech místech, popisy vnitřků čtyř skillů v životním cyklu.

**Rozhodnutí:** `RULES.md` dostal sekci *Co do tohoto souboru nepatří* s pětibodovým testem – soubor v `docs/` → `structure.md`; skill nebo jeho vnitřek → do skillu; kód, web, text, měření → doménová znalost; jeden repozitář → jeho `CLAUDE.md`; zbytek sem. Podle něj se duplicity vrátily do `structure.md`, řetěz jen tam, popisy vnitřků ze životního cyklu zmizely.

**Proč:** je to aplikace vlastního pravidla *Mechanická pravidla nad rozhodováním případ od případu*. Kritérium se pak dalo použít mechanicky na dalších pět nálezů, místo aby se u každého hádalo, kam patří.

**Zamítnuto – jen jedna prozaická věta v úvodu:** duplicity vznikly právě při takové formě. Bez testu se nedodržuje.

**Zamítnuto – nechat obojí a doplnit „kanonický zdroj je X“:** dvě místa pravdy zůstanou a rozejdou se znovu; `/consistency` to nenajde, protože běží nad projektem, ne nad `~/.claude` a `~/Dev/context` současně.

**Poznámka k umístění:** rozhodnutí se týká `~/.claude`. Že se takové zápisy vedou tady, řeší *Provozní soubory `~/.claude` jsou tady*.

### 2026-09-01 – Přednost pravidel a rozlišení principu od mechanického pravidla

`RULES.md` měl pět neslučitelných postojů k výjimce: „cíl je nula výjimek“, „porušení znamená špatně formulované pravidlo, ne výjimku“, „výjimku zdůvodni“, „výjimka jde do projektového `CLAUDE.md`“ – a sám ji použil na vlastní pravidlo o emoji. Navíc čtyři override mechanismy bez pořadí.

**Rozhodnutí:** u **mechanického pravidla** je porušení nejdřív signál špatné formulace – zkusí se přeformulovat, a teprve když by ho to rozmělnilo, vzniká výjimka. U **principu** se místo toho vymezuje rozsah. K tomu nová sekce *Přednost pravidel*: projektový `CLAUDE.md` > výstupní šablona skillu > `RULES.md` > pobídka harnessu; kolize uvnitř `RULES.md` se nahlašuje, neřeší svépomocí.

**Proč:** bylo to místo, kde agent nejčastěji potřebuje rozhodnout, a dostával čtyři různé odpovědi. Osvědčilo se hned: u nálezu o životním cyklu (`/code-review` v seznamu, který tvrdil „jen vlastní názvy“) se tou logikou ukázalo, že nešlo o výjimku, ale o špatně formulované pravidlo – opravilo se pravidlo, ne životní cyklus.

### 2026-09-01 – Autorská hláška ve skillech zrušena

Každý ze 14 vlastních skillů začínal sekcí *Úvodní hláška* s řádkem o autorovi včetně mailu a URL repozitáře – 14 kopií téhož, nejčistší porušení *Single source of truth* v celé konfiguraci. Uvažovalo se o centralizaci do `CLAUDE.md` nebo `BANNER.md`.

**Rozhodnutí:** hláška **zrušena úplně**, ve všech 14 skillech (−122 řádků). Smazána i memory `feedback_skill_author_banner.md`, která ji vyžadovala a navíc odkazovala na kapitolu v `CLAUDE.md`, jež neexistovala.

**Proč:** atribuce v každém spuštění skillu přestala dávat smysl. Centralizace by problém jen zlevnila, ne odstranila.

### 2026-09-01 – Text pro subagenta je výjimka ze *Single source of truth*

Prompt pro subagenta v `/oponent` opisuje pravidla z `RULES.md` doslova. Mechanická kontrola to hlásí jako duplicitu, ale odkaz by tam byl mrtvý – subagent běží bez kontextu session a `RULES.md` načtený nemá.

**Rozhodnutí:** doplněno k *Single source of truth* jako vymezení rozsahu. Platí jen pro text určený agentovi bez kontextu a jen pro to, co opravdu potřebuje – ne jako záminka kopírovat jinam.

**Proč:** bude to platit v každém skillu, který začne delegovat, ne jen v `/oponent`.

### 2026-09-01 – Umístění standardních souborů je volba ze dvou režimů, ne výjimka

`structure.md` předepisoval `docs/` a projekty, kterým to nesedělo, si to zapisovaly jako *výjimku z obecných pravidel* – tenhle repozitář jako jediný, ale principiálně by tak skončil každý knowledge base projekt. Podle `~/.claude/RULES.md` (*Mechanická pravidla nad rozhodováním případ od případu*) je opakovaná potřeba výjimky signál špatně formulovaného pravidla; tady chyběl druhý režim.

**Rozhodnutí:** standardní soubory leží buď v `docs/`, nebo přímo v kořeni projektu. **Obojí rovnocenné**, výchozí `docs/`, volba se dělá jednou při `/project` a deklaruje ji řádek `- **Struktura:** docs/` v metadatech projektového `CLAUDE.md`. Míchat obojí není třetí režim, ale nepořádek. Povinný soubor je jen `CLAUDE.md`; `README.md`, `todo.md`, `decisions.md` a `rules.md` se v `/project` vybírají zaškrtnutím.

**Proč deklarace, a ne jen detekce:** u prázdného nebo rozpracovaného projektu se z umístění souborů nepozná nic, a při míchaném stavu (jaký měl `gtm`) není detekce jednoznačná. Existující projekt se ale nedeklarací nezdržuje – `/project` režim detekuje a zapíše sám, jen to řekne nahlas.

**Dopady:** hook autopromptu měl `docs/prompts.md` natvrdo; nově hledá existující log a jinak se řídí tím, kde leží `todo.md`/`decisions.md`. Ve worktree layoutu znamená „kořen projektu“ `main/`, ne kořen kontejneru.

**Zamítnuto – nedeklarovat a jen detekovat:** viz výš, u prázdného projektu a míchaného stavu selhává.

**Zamítnuto – `prompts.md` vždy v `docs/`:** v režimu `root` by adresář `docs/` vznikl jen kvůli jedinému souboru.

**Ruší to charakter výjimky** u tohoto repozitáře: `root` je od teď deklarovaný režim, ne odchylka. (Poslední odchylku – umístění hotových položek – zrušil téhož dne zápis *Hotové úkoly mají vlastní `done.md`*.)

### 2026-09-01 – Hotové úkoly mají vlastní `done.md`

`todo.md` držel nehotové i hotové položky. Dvě potíže: na první pohled nebylo vidět, co zbývá (v tomhle repozitáři 52 hotových položek k 1. 9. 2026), a opakovaně se vracela otázka, kam hotové patří – do společné sekce `## Hotovo` na konci, nebo pod tu sekci, ke které se váže. Rozhodnutí *Provozní soubory jsou centrální, ne po doménách* (28. 8. 2026) ji zodpovědělo „pod sekci“, ale tím jen zvolilo z dvou špatných variant.

**Rozhodnutí:** vedle `todo.md` stojí **`done.md`**. `todo.md` drží jen nehotové, `done.md` jen hotové; sekce se zrcadlí. Přesouvá se **průběžně, ve chvíli dokončení** – ne dávkově při `/cleanup`, ten jen ověří, že v `todo.md` nic hotového nezbylo. Položka nese datum dokončení ve tvaru `(2026-08-28)`, nejnovější nahoře.

Oba soubory jsou **pár**: zakládají se spolu, v `/project` je to jedna zaškrtávací volba, a `done.md` vzniká i prázdný. Jeden bez druhého nedává smysl.

**Proč pár, a ne „done až s první hotovou položkou“:** stav „todo bez done“ by znamenal, že hotové položky zase někde přechodně bydlí v `todo.md`. Pravidlo *nezaložený soubor není odchylka* platí na výběr v `/project`, ne na půlku páru.

**Zamítnuto – parkované body do `done.md`:** bod odložený v rámci session („teď přeskoč“, za deset minut vyřešeno) je procesní poznámka, ne odvedená práce. Po vyřešení se maže.

> **Revize 2. 9. 2026:** dovětek *„nejnovější nahoře“* neplatí – pořadí se obrátilo, do obou souborů se dopisuje na konec sekce. Viz *Nejstarší nahoře: do provozních souborů se dopisuje na konec*. Zbytek rozhodnutí platí beze změny.

**Ruší to část rozhodnutí *Provozní soubory jsou centrální, ne po doménách*** z 28. 8. 2026 – konkrétně větu o hotových položkách pod sekcemi. Zbytek (jediný `decisions.md` a `todo.md` na kořeni, členění nadpisy) platí dál. Ruší to i větu „odchylkou zůstává jen umístění hotových položek v `todo.md`“ ze zápisu *Umístění standardních souborů* z téhož dne: touhle změnou odchylka zanikla úplně.

### 2026-09-02 – Zadání se jmenuje `requirements.md` a `architecture.md`, skill `/specify`

Skill `/spec` vyráběl `docs/prd.md` a `docs/design.md`. Všechny tři názvy měly vadu: `/spec` byla jediná zkratka mezi jinak celými názvy skillů, `prd` je česky nešťastná zkratka a `design` už v ekosystému znamená vizuální tvorbu (`~/Dev/context/design/`), takže jedno slovo označovalo dvě různé věci.

**Rozhodnutí:** `/spec` → **`/specify`**, `docs/prd.md` → **`docs/requirements.md`**, `docs/design.md` → **`docs/architecture.md`**. `/breakdown` a `docs/plan.md` zůstaly beze změny.

**Proč `requirements` a ne `product`:** `product.md` je kratší, ale v e-shopu a v katalogu znamená „product“ doménovou entitu – `docs/product.md` by v těch projektech byl aktivně matoucí a v `/replace` i v grepu falešný poplach. `requirements` navíc symetricky kontruje `architecture` a používá to tak i AWS Kiro.

**Proč `architecture` a ne `design`:** vědomá odchylka od průmyslového standardu, kde je `design doc` zavedený žánr v klasické i v AI praxi (Spec Kit, Kiro). Cena je přijatá kvůli tomu, že v tomhle ekosystému má „design“ obsazený jiný význam a dvojznačnost je dražší než odchylka.

**Zamítnuto – `specification.md`:** slovo „spec“ se uvnitř `/specify` používá pro *vstup do plánu*, kterým je návrh řešení; soubor téhož jména by ten termín rozdvojil.
**Zamítnuto – `what.md` / `how.md` / `when.md`:** symetrické a hezké, ale negrepovatelné, neposlatelné klientovi, bez jakéhokoliv priora pro model a neškálovatelné na čtvrtý dokument. `when.md` navíc lhal – plán neobsahuje termíny.
**Zamítnuto – `/plan` místo `/breakdown`:** odstranilo by disproporci mezi jménem skillu a jménem výstupu, ale slovo „plan“ je obsazené dvakrát jiným významem: plan mode v Claude Code a `/plan` ve Spec Kitu, kde znamená **návrh řešení**, tedy naše `architecture.md`. Převzít cizí název s posunutým významem je horší než vlastní název.
**Zamítnuto – `/tasks` → `tasks.md`:** srovnalo by se se Spec Kitem i významově, ale `tasks.md` vedle `todo.md` je opakovaný zdroj zaváhání.

### 2026-09-02 – `/standards` se stal `/review`, `/consistency` zůstal samostatný

Uzavírání feature bylo `testy → /standards → /code-review → /consistency → /cleanup`, tedy tři sériové průchody dokumentací a kódem, každý s vlastní frontou nálezů.

**Rozhodnutí:** `/standards` se přejmenoval na **`/review`** a rozšířil na tři vrstvy – deterministické nástroje (nula tokenů), paralelní panel specialistů, a **nezávislý ověřovatel, který se každý nález snaží vyvrátit**. Doménové sady z `~/Dev/context/` jsou v něm jedním druhem role vedle korektnosti, bezpečnosti, dat, provozu a testů; `/code-review` a `/security-review` si volá jako dvě z rolí. Osa se zkrátila na `/review → /consistency → /cleanup`.

**Proč:** panel bez ověřovací vrstvy zavalí uživatele pravděpodobně znějícími nálezy – reviewer požádaný o hledání mezer nějaké najde vždycky. Po třetím falešném se skill přestane pouštět, a to je horší než ho nemít. Pořadí se zároveň otočilo: korektnost jde před soulad s předpisem, protože oprava korektnosti přepisuje strukturu a zahodila by povrchové úpravy.

**Proč `/consistency` zůstal:** ptá se „sedí si projekt sám se sebou?“, což je jiná otázka než kterákoliv role v `/review`, dívá se na celý projekt místo na diff a funguje i nad projekty bez kódu.

**Role se vybírají podle obsahu rozsahu, ne podle typu projektu** – nad čistě obsahovým projektem se kódové role nezapnou a poběží jen textové a doménové.

### 2026-09-02 – Skilly se pojmenovávají volně, pravidlo „skill je sloveso“ neplatí

Při přejmenování `/spec` → `/specify` vzniklo pozorování, že v životním cyklu projektu je skill činnost a jeho výstup věc, a **žádný skill se nejmenuje jako svůj výstup**. Chvíli to bylo zapsané v `~/.claude/.claude/CLAUDE.md` jako závazná konvence.

**Rozhodnutí:** zrušeno. Skilly se pojmenovávají podle potřeby, bez pravidla.

**Proč:** jako pravidlo to nefungovalo. Porušovalo ho pět existujících skillů – `/report`, `/transcript`, `/consistency`, `/project`, `/oponent` – a nabízené cesty ven byly obě horší než pravidlo samo: buď přejmenovat pět denně používaných skillů, nebo si pravidlo hned podepřít pěti výjimkami. Pozorování o životním cyklu zůstává platné, ale je to popis stavu, ne norma.

**Stopa je tady schválně:** bez ní by pravidlo někdo za půl roku zavedl znovu ze stejné úvahy.

### 2026-09-02 – Autoprompt zrušený úplně

Skill `/autoprompt`, jeho `UserPromptSubmit` hook, všechny sekce *Autoprompt* v `CLAUDE.md` napříč projekty i samotné soubory `prompts.md` jsou pryč. Mechanismus přestal existovat, ne že by se jen vypnul.

**Proč – čtyři důvody, žádný z nich sám o sobě rozhodující:**

1. **Skoro se nepoužíval.** Zapnutý byl ve třech projektech z osmi a ani tam se s tím logem reálně nepracovalo. Deset tisíc řádků, které nikdo nikdy nečetl.
2. **Nespolehlivá aktualizace.** Občas se prompt nedoplnil, a naopak vyráběl commity, které nepatřily k žádné práci – ve worktree layoutu navíc trvale rozpracovaný soubor v `main/`, kvůli kterému se musela dělat výjimka z pravidla „v `main/` se nepracuje“.
3. **Riziko úniku citlivých údajů.** Hook zapisoval prompt **doslova, bez jakéhokoliv filtru**, a v kombinaci s autocommitem – což byla doporučovaná dvojice – se cokoliv vlepeného do promptu ocitlo v gitu dřív, než to kdokoliv přečetl. Kontrola na tajemství běží až v `/review`, takže do té doby je hodnota v historii a jediná náprava je rotace. Vyplavalo to jako nález oponentury konfigurační vrstvy.
4. **Náhrada existuje.** Prompty jsou pořád v session souborech v `~/.claude/projects/`; kdyby byly někdy potřeba, dají se vytáhnout odtamtud. Log v repozitáři byl pohodlí, ne jediný zdroj.

**Zamítnuto – jen doplnit filtr na tajemství:** řešilo by to třetí důvod a žádný z ostatních tří. Udržovat mechanismus, který se nepoužívá a občas nefunguje, kvůli tomu, že by po opravě přestal být nebezpečný, je špatný poměr.

**Zamítnuto – nechat skill a jen ho všude vypnout:** vypnutý skill v `README.md` a v `/project` dál nabízí funkci, kterou nikdo nemá zapnout. Buď se používá, nebo není – viz pravidlo *Nedeklaruj, co skill neumí* v `~/.claude/skills/SKILLS.md`, *7. Jak se píše text uvnitř*.

**Co zůstalo vědomě:** smazání commitem obsah z historie neodstraní, takže po zrušeném mechanismu zbyly staré logy tam, kde byly. Platí na ně pravidlo, které je i tak obecné: co bylo jednou commitnuté, patří **rotovat**, ne jen smazat. Stav a rozsah drží `~/Dev/context/decisions.md`, sekce `## Claude`; sem nepatří, protože ukazovat ve veřejném repozitáři na místo, kde se dá hledat, je návod, ne poznámka.

**Zamítnuto – vyčistit i historické záznamy a obsah kurzu:** `docs/done.md` v jednom z projektů zaznamenává, co `/project` tehdy udělal („autoprompt vypnutý“), a přepsat ho by byla falzifikace evidence o proběhlé práci – `done.md` se z definice nemaže. Jeden soubor s obsahem kurzu používá autocommit a autoprompt jako **učební příklad** toho, jak se konfiguruje agentní workflow; je to obsah kurzu, ne konfigurace, a zásah do něj by byl obsahové rozhodnutí, ne úklid. Historický řádek v `ai/CLAUDE.md` proto dostal jen doplněk, že mechanismus skončil, místo smazání.

**Dopady:** `/project` přišel o Krok 7 a zbylé kroky se přečíslovaly (Paměťová politika 8 → 7, Typ projektu 9 → 8, Kontrakt příkazů 9b → 8b, Doménové checklisty 10 → 9, Závěrečný souhrn 11 → 10); odkazy v `coding.md` dorovnány. **Uvnitř `/project` ale zůstala dvě čísla nedorovnaná** (tabulka „Dva `CLAUDE.md`“ a věta o `settings.local.json`); našel to až čtenář bez kontextu v `/cleanup` a opraveno bylo dodatečně. `structure.md` přišel o soubor `prompts.md` v obou režimech a `worktree.md` o výjimku, která kvůli němu existovala – v `main/` se teď nepracuje bez výjimky.

### 2026-09-02 – Osa je jednouživatelská a interaktivní

Zapsáno jako **vědomé rozhodnutí**, protože to dosud nebylo nikde a vypadalo to jako opomenutí. Podnět z oponentury konfigurační vrstvy.

Celý *Životní cyklus projektu* předpokládá **jednu interaktivní session jednoho člověka**. Stojí na dvou věcech, které jinde neplatí: na `AskUserQuestion` (průchod nálezy v `/review`, `/attack` i `/consistency` klade jednu otázku na nález) a na souhlasu průběžné kontroly, který je vydaný lokálně, uložený pod `$HOME` a klíčovaný repozitářem. V CI hook nespustí nic a interaktivní průchod nemá komu položit otázku; u spolupracovníka platí totéž, protože jeho `$HOME` je jiné.

**Co ze životního cyklu tedy platí mimo interaktivní session:** jen deterministická vrstva – `typecheck`, `lint`, `test`, `audit`, scan tajemství, statická analýza. Ta běží kdekoliv a nepotřebuje nikoho, kdo by odpovídal.

**Zamítnuto – neinteraktivní režim skillů** (`/review --report`: žádné otázky, všechno sporné do souboru, návratový kód podle nejvyšší závažnosti): dávalo by to smysl v týmu nebo v CI, ale ani jedno není dnešní situace, a režim, který se nepoužívá, se rozejde s tím používaným, aniž si toho kdo všimne. Až bude potřeba, je to jasně vymezená práce, ne přestavba.

**Zamítnuto – souhlas průběžné kontroly vydávat per repozitář souborem v repu:** zavřelo by to díru v CI, ale otevřelo horší – souhlas by pak byl součástí toho, co se schvaluje, tedy by si ho repozitář mohl vydat sám. Bezpečnostní model stojí na tom, že souhlas leží mimo repozitář.

### 2026-09-03 – `/cleanup` ve worktree větve jen konstatuje, nenabízí merge

Závěrečný verdikt `/cleanup` zněl *„můžeš ji opustit nebo zkompaktovat“*. Ve worktree layoutu to neodpovídá na otázku, kterou má člověk v hlavě – totiž co s tou větví –, a zároveň nabízí odchod jako jedinou cestu, přestože zápis do souborů neznamená hotovou práci.

**Rozhodnuto:** ve worktree větve verdikt navíc řekne, že větev zůstává otevřená a dá se pokračovat, zkompaktovat, nebo ji dokončit. **A tím to končí.**

**Zamítnuto – nabídnout merge přes `AskUserQuestion`:** vypadá to jako služba, ale je to pobízení k akci, o kterou nikdo nežádal. `~/.claude/WORKTREE.md`, *Větev žije, dokud uživatel neřekne jinak*, říká, že se merguje **jen na výslovný pokyn**; předložit tlačítko „dokončit větev“ na konci každého úklidu ten pokyn fakticky vyrábí.

**Zamítnuto – vypsat hotovou sekvenci příkazů k překopírování:** táž námitka o stupeň slabší, a navíc to zaplňuje závěr skillu blokem, který se ve většině běhů nepoužije.

**Zamítnuto – předvyplnit příkaz do vstupního řádku:** to byl původní požadavek, ale skill ani hook do vstupu terminálu zapsat neumí a předstírat opak by bylo horší než to přiznat.

**Poznatek:** ta otázka odhalila, že `worktree.md` mezitím přišel o šest kapitol včetně *Dokončení větve* – smazal je omylem úklid autopromptu (viz `~/.claude/RULES.md`, *Mazání ověř diffem, ne grepem*, které z toho vzniklo). Doména tedy neměla čím podepřít ani větu o dokončení větve. Obnoveno commitem `7d3de17`.

### 2026-09-04 – Strop deseti položek ve slovníku `/transcriptu` zrušen, protože ho měření vyvrátilo

`SKILL.md` od 3. 9. tvrdil, že do promptu pro whisper patří **nejvýš deset položek**, protože „účinnost initial promptu klesá s pořadím položky“ a delší seznam to důležité naředí. Doloženo to bylo dvěma běhy: osmipoložkový slovník trefil sledované jméno 6× ze 6, jednadvacetipoložkový 0 ze 4.

**To porovnání ale míchalo dvě proměnné** – v prvním seznamu bylo jméno na třetí pozici, v druhém na páté. Sedm nových běhů nad touž nahrávkou s pevnou pozicí ukázalo, že **délka vliv nemá**: 8 → 5/5, 12 → 4/5, 16 → 4/5, 21 → 5/5.

Efekt sám reálný je – jeden jednadvacetipoložkový seznam dá 5/5, jiný 0/5 nad tímtéž zvukem –, ale ani pozice (přesun na třetí pozici: 1/5), ani psaní velkých písmen (0/5) ho nevysvětlují. **Příčina zůstala neizolovaná** a je vedená v `todo.md`.

**Zamítnuto – nechat strop a jen přiznat, že je zvolený:** pravidlo, jehož jediné odůvodnění bylo vyvráceno, není opatrné, ale falešné. Kdo by ho četl, řídil by se jím a nevěděl proč.

Místo něj platí jediná doložená mez, a ta je technická: whisper ořízne prompt na `n_text_ctx/2`, tedy 223 tokenů, a **zahodí přitom jeho začátek**, ne konec. U češtiny je to zhruba 38 termínů (změřeno: 21 termínů = 123 tokenů).

### 2026-09-04 – Přebírání commitů mezi souběžnými session řešeno pravidlem, ne mechanismem

Session pracující na `/project` dvakrát commitla `git add -A` a smetla s sebou rozpracované změny druhé session v jiném skillu. Obsah se neztratil, ale zpráva u jednoho commitu popisuje diff, který v něm není, a `git blame` odkazuje na zdůvodnění týkající se něčeho jiného. Pushnutá historie se pak už opravit nedá.

Zvoleno **pravidlo v `RULES.md`** (*Commituj jmenované cesty, ne `-A`*).

**Zamítnuto – pre-commit hook, který `-A` odmítne:** neuměl by rozlišit legitimní `git add -A` v session, která je nad repozitářem sama, což je většina běhů. Hook, který brání běžné operaci, se obchází.

**Otevřená slabina, kterou je potřeba přiznat:** `RULES.md` sám o kus výš tvrdí, že *kde má hranice držet, tam k ní patří mechanismus – jinak je to přání*. Tohle je přání. Incident přitom způsobil model, který instrukce měl a stejně `-A` použil, takže pravidlo řeší jen ten případ, kdy si ho někdo přečte a vzpomene si. Lepší mechanismus zatím nikdo nenavrhl.

### 2026-09-04 – Fáze skillů se číslují plochou řadou, písmena jen pro příbuzné podkroky

**Problém:** `/cleanup` měl fáze 0, 1, 1b, 2, 2b, 3, 4, 4b, 5. Písmenné podfáze vypadaly jako rozpad jednoho kroku na tematicky příbuzné části, ale nebyly – vznikly tím, že se mezi hotová čísla postupně vkládaly samostatné kroky a přečíslovat celý skill se pokaždé nechtělo. Fázi `1b` (nevypořádaná témata) nespojovalo s `1` (rekonstrukce session) nic víc než s `2`.

**Rozhodnutí:** **plochá vzestupná řada bez písmen.** Písmenná podfáze je legitimní jen tam, kde skutečně sdružuje tematicky příbuzné podkroky téhož kroku – jako `/specify` s `3a` (Produktová specifikace) a `3b` (Návrh řešení), kde jde o dva výstupní dokumenty jednoho zadání. Ty se proto nechaly být.

**Proč:** číslování je struktura, kterou čtenář bere jako tvrzení o vztazích. Když `1b` neříká nic o vztahu k `1`, číslování lže. Přečíslovat celý skill je jedna dávka náhrad, po které je drahá kontrola křížových odkazů.

**Vedlejší nález:** to pravidlo tehdy nekryla žádná kontrola – `test_odkazy_na_sekce_miri_na_existujici_nadpis` matchuje jen odkazy s uvedenou cestou k souboru, kdežto vnitroskillové „vezmi to do Fáze 7“ cestu nemá. Doloženo mutačním testem: `Fáze 7` přepsaná na `Fáze 77` prošla všemi 35 testy. Proto vznikl `test_vnitroskillove_odkazy_na_faze_miri_na_existujici_nadpis`, který **odkazy na vlastní fáze už hlídá**. Nekrytý zůstává cizí odkaz bez cesty (`` `/review`, Fáze 0.1 ``) – nechytne ho ani jeden z obou testů.

**Zamítnuto – nechat písmena jako stopu, že fáze přibyla později:** kdy co vzniklo, drží git; do číslování to nepatří a čtenáři je to k ničemu.

**Zamítnuto – srovnat na plochou řadu i `/specify`:** jednodušší pravidlo bez výjimky, ale zahodilo by informaci, že ty dva kroky patří k sobě. Výjimka je tu levnější než ztráta významu, protože má ostré kritérium: písmena jen když by jinak jeden krok musel vyrábět dva samostatné výstupy.

### 2026-09-04 – Tvar skillu má normu, `/skill` je proti ní jen instalátor

Tvar vlastních skillů nebyl zapsaný nikde. Vznikl jednou a pak se patnáctkrát opsal, takže to byl zvyk, ne standard – a při návrhu skillu `/skill` se z něj málem stala norma jen tím, že by se opsal ještě jednou. Nezávislé posouzení proti [Anthropicovým *Skill authoring best practices*](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) a `superpowers:writing-skills` rozdělilo dosavadní tvar na tři hromádky. **Obstálo:** *Co skill nedělá* s **jmenovaným** sousedem (venku existuje jen obecné „when NOT to use“), jednoznačný závěrečný verdikt (jejich *verifiable output*) a ověřovatel, jehož úkolem je nález vyvrátit (venku nemá obdobu). **Neobstálo:** příprava opsaná ve dvanácti skillech a monolitická délka bez progresivního odhalení – žádný skill nepoužíval vedlejší soubory pro text, `/review` měl 591 řádků proti doporučeným 500. **Chybělo:** sekce s častými chybami (0 z 15) a ověřování funkce místo tvaru.

**Vyvráceno měřením:** tvrzení, že číslování fází je rituál bez funkce, neplatí – `/attack` odkazuje na „`/review`, Fáze 0.1“ napříč skilly a `/project` má 32 vnitřních odkazů na svoje kroky. Je to adresovací mechanismus a zůstává.

**Rozhodnutí:** vznikla `~/.claude/skills/SKILLS.md` (norma tvaru), `~/.claude/skills/PREFLIGHT.md` (sdílený začátek běhu) a skill `/skill` se čtyřmi režimy – `create`, `extract`, `update`, `delete`. Norma je **čistý standard**, postup drží skill; je to týž vztah jako `structure/structure.md` ↔ `/project`. Vynucení je v `tests/test_skills.py` jako **seznam, který musí přesně sedět**: skill mimo normu v `MIGRACE` nesmí chybět ani přebývat, takže opravený skill, který ze seznamu nezmizí, test shodí stejně jako regrese. Dnes je v seznamu všech patnáct starších skillů; převod je vědomý běh `/skill update`, ne vedlejší efekt jiné práce.

**Norma je ve veřejném `~/.claude`, ne v tomhle repozitáři.** Padl návrh dát ji do `context/claude/skills.md`. Rozhodlo hraniční pravidlo z `CLAUDE.md`: *„`~/.claude`: konfigurace Claude Code, hooks, skilly – vše, co se hodí ostatním pro inspiraci“*, a týž argument, kterým zůstal veřejný životní cyklus projektu – veřejný repozitář existuje proto, aby ty skilly sloužily jako vzor, a norma, která je tvaruje, k nim patří. Praktický důvod navíc: sdílená příprava musí být veřejný tak jako tak, protože ho skilly čtou za běhu; rozseknout normu a její runtime kus přes hranici repozitářů by bylo přesně to, co `CLAUDE.md` označuje za chybu designu. Obojí sedí v `skills/`, ne v kořeni – kořen zůstane čistý a sdílená příprava nepatří žádnému jednomu skillu.

**Nové pravidlo *Skládej, nepiš znovu*.** Než se napíše krok, zjistí se, jestli ho neumí vestavěný skill, plugin nebo hook. Skill se dělí na **rozhraní** (nemění se tiše), **vlastní obsah** a **vnitřek** (delegace, vyměnitelná kdykoliv); vnitřek se přiznává v sekci *Jak je to postavené uvnitř*. Delegace se zadává **kontraktem výstupu, ne seznamem kroků**, aby upgrade cizího nástroje nerozbil volání. Ta praxe u `/breakdown` a `/implement` existovala už předtím, ale nebyla nikde jako pravidlo – a proto se nepropagovala; při návrhu `/skill` ji musel navrhnout uživatel, model na ni sám nepřišel. Je to týž mechanismus jako u přípravy a u častých chyb: **praxe bez normy se nešíří.**

**Zamítnuto – `/skill` nepsat vůbec a spolehnout se na `skill-creator` plus řádek v `CLAUDE.md`:** norma by se prosadila i tak (`RULES.md`, *Přednost pravidel*: projektový `CLAUDE.md` přebíjí šablonu skillu) a ušetřilo by to celý soubor. Padlo to na tom, že revize patnácti skillů proti normě a zrušení skillu se všemi stopami neumí nikdo zvenčí, a hlavně na tom, že obálka nic nestaví znovu – jen skládá. Řádek v `.claude/CLAUDE.md` přesto vznikl, protože platí pro **každou** cestu ke změně skillu, nejen pro `/skill`.

**Zamítnuto – převzít tvar od `writing-skills` nebo `skill-creatoru`:** oba mají vlastní osnovu (`## Overview / When to Use / Core Pattern`) a obě se od téhle liší. Tvar je proto vždycky z normy; cizí nástroje se volají na **měření a vytěžení**, ne na rozhodnutí, jak má skill vypadat. Zbývá riziko, že si při vyvolání prosadí svou – proto se jim tvar předává výslovně a proto je `improve_description.py` povinný u skillu, jehož jméno se s cizím překrývá.

**Zamítnuto – vypnout `skill-creator` a `superpowers:writing-skills`:** bylo to druhé z nabízených řešení kolize tří skillů o týž spouštěč („udělej mi skill na X“ bez lomítka) a proti obálce fakticky padlo – oba pluginy se staly jejím **vnitřkem**, takže vypnout je znamená `/skill` vykuchat. Kolizi řeší to, že `/skill` je jediné vstupní dveře; zbytkové riziko se měří přes `improve_description.py`. Zapsáno proto, aby se za půl roku nenavrhlo znovu jako řešení téže kolize.

**Zvážen a nepřijat protinávrh: metodiku srovnávacího běhu a tlakových scénářů převzít do `SKILLS.md` a `writing-skills` nevolat vůbec.** Motivace byla reálná – ten plugin má vyloženě **konkurenční osnovu skillu** (`## Overview / When to Use / Core Pattern`), která při vyvolání nateče do kontextu vedle normy. Nepřijalo se to proto, že opsané cizí know-how se s originálem rozejde a nikdo si toho nevšimne, kdežto delegace zastará viditelně. Riziko se místo toho snižuje dvěma způsoby: tvar se pluginu **předává výslovně** a jeho doporučení k tvaru se ignorují, a při prvním ostrém běhu `/skill` se ověří, jestli si svou osnovu neprosadí navzdory zadání. Prosadí-li, je to důvod delegaci zúžit nebo zrušit.

### 2026-09-04 – Tři opravy normy z prvního auditu `/consistency`

Audit nad dnešní prací našel čtyři nálezy; jeden byl mechanický (popis testů v `.claude/CLAUDE.md` nezmiňoval novou třídu), tři měnily normativní text.

**`RULES.md` nevěděl o `SKILLS.md`.** Oba soubory mají rozřazovací test *„co sem nepatří“*, ale jen jednosměrně: `SKILLS.md` posílá obecná pravidla do `RULES.md`, kdežto `RULES.md` neměl bod, který by pravidlo platné pro **všechny** skilly poslal opačným směrem – jeho bod o konkrétním skillu na to nesedí, takže by propadlo na reziduální *„nic z toho → patří sem“*. Přesně to se dnes málem stalo normě samotné. **Rozhodnutí:** přibyl bod 2 *„Platí obecně pro skilly? → `~/.claude/skills/SKILLS.md`“*, zbytek přečíslován; ověřeno, že na čísla bodů toho testu nikde nic neodkazuje.

**Norma nepočítala s přílohovými sekcemi.** Předepisovala `## Časté chyby` před závěrečnou fází, jenže skill s vlastními režimy (`/skill`) má za závěrem ještě samostatné sekce. **Rozhodnutí:** pořadí platí pro **hlavní průběh**; přílohové sekce (režimy, katalogy) stojí za závěrem a `## Časté chyby` úplně naposled. U lineárního skillu se nic nemění. **Zamítnuto – přesunout `Časté chyby` v `/skill` před závěr:** doslovně by to normu splnilo, ale sekce by stála před režimy, jejichž chyby také popisuje.

**Závěrečný verdikt přestal předstírat doslovnost.** Norma dávala jednu literální větu, `/skill` po sobě žádal „doslova ve tvaru z normy“ – jenže napříč pěti skilly existovaly čtyři varianty, protože **čeština žádá shodu s rodem toho, co je hotové** („Plán hotový není“ × „Hotové to není“). Doslovnost tedy byla nesplnitelná, ne nedodržená. **Rozhodnutí:** norma dává **vzorec** (první věta říká hotovo a čím pokračovat, druhá jmenuje konkrétně, co brání, mezi nimi nic), doslovné je znění uvnitř jednoho skillu. Skill s vlastním koncem pro některý režim smí mít druhou dvojici splňující týž vzorec.

**Vynucení dorovnáno.** Audit odhalil, že kontrola souladu s normou hlídala jen **přítomnost** sekcí, ne jejich pořadí – nové pravidlo o přílohách by tedy nikdo nevynutil a norma by tvrdila víc, než umí. Kontrola pořadí proto přibyla do `SouladSNormou.vady_poradi()` a je ověřená mutačním testem v obou směrech. Je to táž vada, kterou norma vyčítá staré sadě testů: *vynucený tvar, nevynucená funkce* – tentokrát na vlastním nástroji.

**Režimy se jmenují jednoslovně a anglicky** – `create`, `extract`, `update`, `delete` – místo původních českých „revize“, „ze-session“, „zrušit“. Výchozí `create` se vyjmenovává explicitně, aby ho šlo napsat i tam, kde je jinak implicitní, a aby byl vidět v `argument-hint` i v popisu. Česká podstatná jména v běžném textu („výsledek revize“) zůstávají česky: anglicky je **jméno režimu**, ne řeč o něm. Zapsáno proto, že zdůvodnění jinak žilo jen v commit messages, a to je přesně ten případ, na který míří `~/.claude/RULES.md`, *Rozhodnutí zapisuj i s cestou k nim*.

### 2026-09-04 – Ze čtyř navržených nových skillů zůstaly dva, `/measure` se zobecnil na `/audit`

Průchod dnešní session vytipoval čtyři kandidáty na nové skilly: `/measure` (revize měření u klienta), `/slides` (prezentace podle `design/slides.md`), `/nabidka` (konzultační nabídka z `brand/` + `speaking/` + `organizations/`) a `/research` (podložené rešerše). Kritérium výběru bylo jednotné: **doménová znalost už existuje, chybí jen proces, který ji řídí.**

**Rozhodnutí:** do `todo.md` jdou `/research` a `/invoicing` (nový, v původním výběru nebyl), a místo `/measure` **parametrizovaný `/audit <domain>`** – parametrem se řekne, proti kterému návodu z `~/Dev/context/` se audituje. `/slides` a `/nabidka` zamítnuty.

**Proč `/audit` místo `/measure`:** skill vázaný na jednu doménu by se musel psát pro každou znovu, kdežto parametrizovaný je *generic-base + delta* (`~/.claude/RULES.md`). Potřeba přitom zůstává táž – `analytics/` je nejhotovější doménová znalost a jako jediná nemá skill, takže existuje jako checklist, který nikdo nevyvolá ve správný moment.

**Vymezení, bez kterého by to byla duplicita:** `/review` má mezi rolemi „soulad s doménovými standardy“, ale měří **vlastní práci na projektu**; `/audit` měří **cizí věc** – klientský web, měřicí nastavení, převzatý text. Rozdíl je v předmětu, ne v metodě, a musí být v `Co skill nedělá`.

**Zamítnuto – `/slides`:** `design/slides.md` a `training/training.md` sice leží nevyužité a promítaný obsah se dělá opakovaně, ale vestavěné `document-skills:pptx` a `design` pokrývají řemeslo a zbytek je úsudek nad jedním konkrétním obsahem, ne opakovaný proces.

**Zamítnuto – `/nabidka`:** podklad je kompletní (`brand/`, `speaking/`, `organizations/`) a napříč komunitou je to nejčastější neprogramátorský use-case Claude Code, ale nabídka je pokaždé jiná a její hodnota stojí na úsudku, který se nedá zapsat do postupu.

**U `/research` zůstává otevřená otázka**, jestli to není spíš fáze uvnitř `/compose` – krok, který nikdo nezavolá, je horší než žádný. Zapsáno v `todo.md` jako první věc k rozhodnutí, ne jako detail k dořešení.

### 2026-09-04 – Režimy skillů se jmenují anglicky a lícují napříč skilly

Skill `/skill` dostal režimy `create`/`extract`/`update`/`delete`, ale `/project` měl pro **tutéž věc** – dorovnání na dnešní podobu standardů – režim pojmenovaný česky „revize“. Nová norma přitom žádá jeden termín pro jednu věc napříč skilly, takže si to odporovalo hned první den.

**Rozhodnutí:** do `~/.claude/skills/SKILLS.md` přibylo pravidlo, že **jméno režimu je token, ne věta**: anglicky, jedním slovem, malými písmeny, a co dělá totéž, jmenuje se stejně. Ustálená sada je `create`, `update`, `delete`, k ní podle potřeby další jednoslovné (`extract`, `full`). Výchozí režim se vyjmenovává taky, aby ho šlo napsat explicitně. **Platí i pro režimy, které se rozpoznávají samy** a nepředávají se argumentem – uživatel je vidí ve výpisu a pojmenovává je v řeči stejně.

`/project` se podle toho přejmenoval: *nový projekt* → `create`, *existující projekt* → `adopt`, *revize* → `update`.

**Proč anglicky:** české „revize“ se skloňuje, píše se s diakritikou a v `argument-hint` vypadá jako věta. Česká podstatná jména v běžném textu („výsledek revize“) zůstávají česky – rozdíl je mezi **jménem režimu** a mluvením o něm. Podle toho se při dorovnání `/project` vědomě nechal být běžný text v popisu skillu i zmínka o `worktree.md`.

**Zamítnuto – přejmenovat u `/project` jen „revizi“ na `update`:** menší zásah, ale nechalo by to dvě česká jména vedle jednoho anglického, tedy stav horší než předtím a rovnou porušující pravidlo, které právě vzniklo.

### 2026-09-04 – Kroky `/project` přečíslovány na plochou řadu 0–13

Norma dostala téhož dne ostré kritérium pro písmennou podfázi: písmena jen tam, kde by jinak jeden krok musel vyrábět **dva samostatné výstupy**. `/project` ale své vsuvky `0b`, `3b` a `8b` zdůvodňoval jinak – jako „vložené kroky, na které se odkazuje odjinud“ –, takže si norma a skill tiše odporovaly. **Žádná kontrola to nechytala**, protože kontrola souladu s normou na písmenné podfáze necílí.

Krok 0b (Soulad se standardem) není druhý výstup Kroku 0 (Zjisti režim a stav), 3b (Layout) není druhý výstup Kroku 3 (Git) a 8b (Kontrakt příkazů) není druhý výstup Kroku 8 (Typ projektu) – jsou to tři tematicky nepříbuzné kroky.

**Rozhodnutí:** přečíslovat na plochou řadu **0–13**. Podkroky `4a`–`4c` (Režim umístění / Které soubory založit / Obsah) naopak kritérium **splňují** – jsou to podkroky téhož kroku –, takže zůstaly a jen se posunuly na `6a`–`6c`.

**Zamítnuto – rozšířit kritérium v normě** o druhý legitimní důvod („vložený krok se stabilním odkazem“): kritérium by přestalo být ostré, protože „odkazuje se na to odjinud“ se dá říct skoro o čemkoliv.

**Zamítnuto – odložit do migrace**, kdy se `/project` stejně otevře kvůli délce: znamenalo by to nechat normu a skill v rozporu do té doby.

**Zamítnuto – zapsat jako „neopravovat“** do kapitoly `## Consistency`: umlčení rozporu, který má jednoznačné řešení.

**Co z toho vyplynulo – a je to nejcennější poučení dne.** Přečíslování prošlo **bez kontroly**: test na vnitroskillové odkazy uměl jen tvar „Fáze“, ne „Krok“, takže `/project` míjel celý. Nahradil ho jednorázový ověřovací skript – a ten měl **tutéž slepou skvrnu jako test**: bral jen číslo stojící bezprostředně za slovem „krok“, takže výčty typu `kroky 2, 3, 4, 6, 7, 8, 8b, 9` viděl jen z první položky. Dávka náhrad proto přepsala u čtyř řádků jen první číslo a zbytek nechala ve starém číslování, **včetně kroku `8b`, který týž commit rušil** – a skript to prohlásil za v pořádku. Commit message tvrdila „všech 32 odkazů míří na existující krok, žádný nevisí“; **to nebyla pravda** a odhalil to až čtenář bez kontextu v následujícím `/cleanupu`.

**Obecné poučení:** ověřovací skript psaný týmž člověkem a v téže chvíli jako oprava zdědí i její slepé místo. Doklad z něj proto neváží víc než doklad z kontroly, kterou ta oprava obchází. Test se následně rozšířil o „Krok“, o písmenné podkroky, o konce rozsahů **a hlavně o celé výčty čísel za jedním slovem** – ověřeno mutačním testem přesně na té vadě, která nastala. Musel zároveň vyloučit odkazy na **kroky životního cyklu** (`RULES.md`, *Životní cyklus projektu*), které se číslují nezávisle a na které `/release` odkazuje legitimně.

### 2026-09-06 – Doladění normy: kritérium „Krok“, konec písmenných podfází a mutační testy

Čtenář bez kontextu po druhém úklidu našel devět nedořešených míst; jejich vypořádání posunulo normu na třech místech a `/project` na čtyřech.

**Kritérium „Krok“ vs. „Fáze“ bylo měkké a neodlišovalo.** Znělo „Krok jen u interaktivních průvodců, kterými uživatel prochází jeden po druhém a může se kdykoliv zastavit“ – jenže to platí i o `/review`, `/consistency` a `/invoicing`, které mají „Fázi“. **Rozhoduje, čí odpovědi tvoří výsledek:** u `/project` je výsledkem to, co uživatel naodpovídal, takže postup je sled otázek. Skill, který něco sám najde nebo vyrobí a ptá se až na nálezy, má fáze, i když se ptá stejně často.

**Písmenné podfáze v `/project` zmizely úplně.** Podkroky `6a`–`6c` (Režim umístění / Které soubory / Obsah) kritériu normy nevyhověly – jsou to tři fáze jedné volby, ne dva samostatné výstupy –, takže se z nich staly samostatné kroky. `/project` si navíc kritérium přeformuloval z „dva“ na „několik“ výstupů; dvě znění téhož pravidla na dvou místech, teď na normu jen odkazuje. Jediným doloženým případem legitimní písmenné podfáze tak zůstává `/specify` `3a`/`3b`.

**Krok „Soulad se standardem“ se přesunul z jedničky na Krok 14.** Číslo 1 lhalo o pořadí: v režimu `adopt` se ten krok provádí jako poslední před souhrnem a v `create` vůbec. Plochá řada tedy jednu lež o vztazích odstranila a jinou zavedla. Rozsahy v tabulce i v popisu toku se musely opravit **významově, ne jen číselně** – to je past, kterou mechanická náhrada čísel nevidí.

**`/project` dostal `argument-hint`.** Měl tři pojmenované režimy a žádný hint, ačkoliv norma říká, že režim chybějící v hintu uživatel nikdy neuvidí, a nevyslovuje výjimku pro režimy rozpoznávané samy.

**Z „ověřeno mutačním testem“ se staly testy.** Ten obrat nesl v zápisech i docstringech důkazní váhu, ale mutace se pokaždé psala ručně jako jednorázový skript a nikde nezůstala – bylo to **tvrzení o důkazu, ne důkaz**. Vzniklo šest mutačních testů, které poškodí vzorový skill a ověří, že kontrola nález opravdu nahlásí. Při jejich psaní se hned ukázalo, proč to má být test a ne rituál: **tři z šesti mutací nejdřív nechytaly nic**, protože nahrazovaly jen první výskyt, a řetězce jsou ve vzoru vícekrát. Ruční mutace tuhle past nemá jak odhalit.

**Zjistilo se, že `skill-creator` nebyl aktivní** – v `settings.json` měl `false`, stejně jako `vercel`, takže jeho soubory sice ležely v cache marketplace a daly se číst, ale skill se nedal vyvolat. `/skill` na něj přitom deleguje tři z osmi kroků. Zapnuto (`/plugin install skill-creator@claude-plugins-official`). Kontrola závislostí ve *Fázi 0* teď ověřuje **dostupnost pluginu**, ne jen Python, a `README.md` ho jmenuje v *Předpokladech* – protože rozdíl mezi „plugin je v cache“ a „plugin je aktivní“ nejde poznat čtením souborů a přesně na tom se dá ztroskotat.

**Zamítnuto – rozšířit kritérium pro písmennou podfázi**, aby `6a`–`6c` prošly: „několik samostatných výstupů“ místo „dva“ by kritérium rozmělnilo, a rozmělnění se už jednou zamítlo u vsuvek `0b`/`3b`/`8b`.

**Zamítnuto – zrušit „Krok“ úplně** a mít všude „Fázi“: jednodušší norma, ale zahodila by rozlišení, které `/project` nese od začátku a které jde po zostření kritéria obhájit.

### 2026-09-06 – README skillu je pro člověka zvenčí, ne dokumentace

Skilly měly jediný text pro člověka – odstavec v kořenovém `README.md` repozitáře `~/.claude`. Ten se opakovaně zvrhával do rozvleklých příběhů („poprvé jsem ho pustil a ze 43 nálezů…“), implementačních detailů a obhajob návrhových rozhodnutí. Honza to opravil třikrát v různých sessions a **pokaždé se to vrátilo**, protože pravidlo nebylo nikde zapsané – opravovala se instance, ne příčina.

**Rozhodnutí:** každý skill má **vlastní `skills/<name>/README.md`**, na které se posílá odkaz na GitHub, když se skill někomu doporučuje. Tvar drží nová sekce *README skillu* v `~/.claude/skills/SKILLS.md`; kořenové `README.md` má na skill **jeden odstavec** a odkaz nese jeho nadpis.

**Co ta norma říká.** `SKILL.md` je pro Clauda a normativní; `README.md` pro člověka a popisný. Ven z README vede tabulka kritérií: postup a instrukce pro Clauda → do `SKILL.md`; obhajoba návrhového rozhodnutí → do `SKILL.md` nebo sem; **implementační detail** (jméno přepínače, souboru, modelu) → nikam; **historka z provozu a číslo z jednoho běhu** → nikam. Poslední dva řádky jsou ty, na které se zapomíná. K tomu překlad do lidské řeči („předává slovník přes `--prompt`“ → „připraví si seznam jmen a podstrčí ho rozpoznávači, takže je pak nekomolí“) a **výslovné vypnutí pravidla *Nepiš, co model už ví*** – čtenář README není model a ví míň, ne víc.

**Instalace se píše jako pokyn pro Clauda, ne jako ruční postup.** První dávka README říkala „zkopírujte adresář tam a tam“ – jenže to je instrukce pro Clauda, a ten ji nepotřebuje. Lidé si skill neinstalují ručně; řeknou si o to. Tvar je proto citovaný prompt s odkazem do repozitáře.

**Skill, který stojí v *Životním cyklu projektu*, začíná rámečkem s celým cyklem** – hned pod nadpisem, ještě před úvodním odstavcem, a s druhým odstavcem instalace na hromadné pořízení celé sady. Čtenář, kterému přišel odkaz na jeden skill, jinak nemá jak zjistit, že jich je víc a že spolu drží. Skilly mimo cyklus rámeček nemají; předstírat u nich sadu by mátlo.

**Pořadí v kořenovém README je závazné:** cyklus v pořadí kroků (čtenář ho čte jako postup), zbytek pod ním abecedně (žádné pořadí mezi nimi neplatí, takže cokoliv jiného by tvrdilo něco, co není pravda, a při přidání skillu by se rozhodovalo znovu).

**Vynucuje to osm testů** – existence README, povinné sekce, tvar instalace, rámeček u skillů z cyklu i jeho nepřítomnost mimo něj, úplnost režimů z `argument-hint`, mez délky a odkaz z kořenového README. Bez nich by to byla čtvrtá ústní domluva v řadě.

**Zamítnuto – README jen u skillů, které dávají smysl samostatně** (vynechat `/compose`, `/invoicing`, `/implement`, které bez soukromé knowledge base nebo bez zbytku cyklu cizímu člověku nic nedají): u drobného skillu vyjde README krátké, a to je v pořádku – kdežto s výjimkami by nikdo nevěděl, jestli odkaz existuje.

**Zamítnuto – uložit koncepci jen do skillu `/skill`:** platila by jen tehdy, když se `/skill` pustí. Při ruční úpravě README by ji nikdo nepřipomněl, a právě ruční úprava je běžný případ.

**Zamítnuto – zobecnit pravidlo „README je pro lidi“ i do `structure/structure.md`**, tedy na všechny projekty: nabídnuto a nevybráno. `structure.md` už hranici *README je popis pro člověka, ne instrukce pro Clauda* drží; tohle je navíc tvar README **skillu**, což je věc normy skillů, ne struktury projektu.

**Zamítnuto – uvádět v rámečku počet kroků číslovkou** („ucelené sady jedenácti skillů“). Vydrželo to půl dne: `/discovery` přibyl týž večer a číslo se muselo ručně dorovnat na dvanácti místech. Číslovka z rámečku vypadla úplně – čtenář si počet spočítá z rámečku pod tím. **Od 20. 9. 2026** má rámeček dva bloky místo jedné šipkové řady, takže se nepočítá ze šipek, ale z obou výčtů. *Zvažováno – přidat na ni test:* šlo by to (testy už mají mechaniku na řadové číslovky), ale je to kontrola na údaj, který v textu nemusí být vůbec.

**Zamítnuto – dopsat do README skillů, co člověk potřebuje, aby mu Claude skill nainstaloval.** Čtenář bez kontextu to hlásil jako chybějící kontext: všech osmnáct README říká „napište Claudovi, ať to nainstaluje“, ale nikde nestojí, jestli k tomu stačí Claude Code, nebo i Git a přístup na síť. Zamítnuto 7. 9. 2026 – kdo Claude Code používá, tohle řešit nemusí, a věta navíc by v každém README jen zabrala místo.

### 2026-09-06 – Termín „osa“ nahrazen „Životním cyklem projektu“

Sled `/project → /specify → … → /release` se od svého vzniku jmenoval **osa** a v `RULES.md` měl nadpis *Životní cyklus práce*. Dvě jména pro jednu věc, a to hlavní z nich nic neříkalo: *„osa sama o sobě může být cokoliv, třeba osa zla.“*

**Rozhodnutí:** jediné jméno **Životní cyklus projektu**, napříč `RULES.md`, všemi skilly, testy, knowledge base i projektovými `CLAUDE.md`. Sekce v `done.md` se jmenuje **`## Průchody životním cyklem`**.

**Jak se vybíralo.** Rozhodl test, jak jméno zní ve vazbách, které se opravdu používají – „krok X“, „mimo X“, „Průchody X“, „jde touž X“. Nabídnuty byly čtyři varianty s náhledem těch vazeb: **Postup práce** (nejprostší, ale „postup“ je běžné slovo a v textu nejde poznat jako termín), **Životní cyklus práce** (dosavadní nadpis, jen bez zkratky „osa“), **Cesta práce** (krátká a vystihuje jednosměrnost, ale „pracovní cesta“ znamená česky něco jiného) a **Řetěz práce** („článek řetězu“ je hotová metafora pro krok, zní ale technicky). **Nevyhrála žádná z nich** – zvítězilo *Životní cyklus projektu*, tedy dosavadní nadpis s vyměněným druhým slovem: cyklus je to proto, že každá další práce jím projde znovu od začátku, a *projektu* proto, že *práce* je vágnější než to, čeho se to týká.

**Přejmenovávalo se frázovými náhradami, ne plošným hledáním, a ověřovalo diffem řádek po řádku.** Slovo „osa“ má v repozitářích spoustu jiných významů a ty musely zůstat: časová osa v `brand/`, osy stavového prostoru v `coding.md`, osa X grafu i osa ceníku v projektech, osy seznamu v `checklists/`, „životní cyklus člena“ v jednom z nich. Kontrolní průchod přes všech 57 repozitářů v `~/Dev` po dokončení nevrátil nic.

**Poučení, které to potvrdilo potřetí:** plošná náhrada slova, které má víc významů, není mechanická operace. Postup je v `~/.claude/skills/replace/SKILL.md` a platí i tady – odvodit tvary, ukázat inventuru, provést, a **skončit kontrolním průchodem na starý tvar**.

### 2026-09-07 – Závazné importy v `~/.claude/CLAUDE.md` se nikdy nenačítaly

Při revizi terminologie padla otázka, proč se dohodnutý termín nepropíše do chování. Měřením přes `claude -p` bez nástrojů se ukázalo, že **`RULES.md`, `STRUCTURE.md` ani `PTYDEPE.md` nejsou v kontextu vůbec** – čerstvá session na ně odpověděla „NENÍ V KONTEXTU“, zatímco `CLAUDE.md` samotný citovala.

**Příčina:** všechny tři byly zapsané jako `` `@~/.claude/RULES.md` ``, tedy **uvnitř code spanu**. Claude Code v něm `@import` nevyhodnocuje. Selhávalo to **tiše** – soubor dál vypadal, jako by ta pravidla platila.

**Rozsah škody:** od vzniku toho souboru. Přirozený experiment to potvrdil z druhé strany – `@~/.claude/skills/SKILLS.md` a `@~/.claude/skills/autocommit/autocommit.md` stojí v `.claude/CLAUDE.md` holé na vlastním řádku a v kontextu **byly**.

**Rozhodnutí:** apostrofy odstraněny; po opravě model vyjmenoval hesla `PTYDEPE.md` i sekce `RULES.md` a na dotaz po terminologii odpověděl správně s odkazem na glosář. Poznatek zapsán do `~/.claude/STRUCTURE.md` k sekci o `CLAUDE.md` a **vynucen testem ověřeným mutačním testem**; kontrolní průchod přes všechny projekty v `~/Dev` stejnou vadu nikde jinde nenašel.

**Opačný případ se hlídat nedá a řeší ho věta v `RULES.md`:** ukázka syntaxe (`` `@~/Dev/context/organizations/<organizace>.md` ``) apostrofy **potřebuje** – bez nich se profil načte do každé session, která to pravidlo čte. Test proto hlídá jen `CLAUDE.md`, aby o importech šlo dál psát.

**Cena:** do každé session nově jde 93 kB. Otázka, jestli tam patří `RULES.md` celý, je zapsaná v `todo.md`.

### 2026-09-07 – `/ptydepe` nedeleguje na `/replace`, náhradu si dělá sám

Skill vznikl s delegací: *„Pusť `/replace` jednou na každý dotčený repozitář.“* Za den, kdy se jím vypořádalo třiadvacet termínů, **nebyl zavolán ani jednou**.

**Rozhodnutí:** delegace vypadla, skill si náhradu dělá sám mapou frází.

**Proč:** `/replace` umí odvozené a skloňované tvary, ale ne to, co náhradu termínu doopravdy komplikuje – změnu rodu a s ní shodu přívlastků („úhel“ mužský → „hledisko“ střední, „role“ ženská → „specialista“ mužský životný), homonyma (platební brána, jazyková mutace, časová osa), opačné významy téhož slova a repetice, které náhrada vyrobí. Mapa frází tohle řeší tím, že se ke každé vazbě napíše její nová podoba **i se shodou**, a teprve pak se pustí přes soubory.

**Vedlejší poučení, které stálo ten den:** skill tvrdil o svém vnitřku něco, co se v praxi nedělo. Odhalil to až `/cleanup` – ne test, protože žádný test nekontroluje, že se deklarovaná delegace opravdu volá.

### 2026-09-07 – Ponechané termíny z revize

Osm termínů, u kterých revize skončila rozhodnutím **nic neměnit**: `heuristika`, `osa`, `vektor útoku`, `mutace`, `session`, `soustava`, `kontrakt příkazů` a `sledovací okno`. Zápisy k nim tu ležely jednotlivě do 10. 9. 2026; tehdy se přestěhovaly do `~/.claude/skills/ptydepe/terms.md`, sekce *Ponechané termíny*, aby celá rozvaha o termínech byla na jednom místě. Rozhodnutí o **ponechání** i o **náhradě** se tak hledají tam, ne tady.

### 2026-09-07 – Revize neustálených termínů dostala vlastní skill `/ptydepe`

Za jedinou session se ručně vypořádalo čtrnáct termínů, které Claude převzal z náhodné zmínky v konverzaci a začal používat napříč projekty jako zavedené pojmy. Postup se u každého opakoval a vyžadoval úsudek, takže splnil obě podmínky normy pro vznik skillu.

**Rozhodnutí:** vznikl `/ptydepe` se dvěma režimy – `suggest` (výchozí, vytipuje kandidáty) a `add <termín>` (projedná jeden a provede náhradu). Slovník rozhodnutých termínů je `~/.claude/PTYDEPE.md`, importovaný do každé session.

**Proč import, ne odkaz:** u termínu, o kterém nevím, že je vymyšlený, mě nenapadne se podívat. Ze stejného důvodu nestačí paměť – načítá se podle relevance k zadání a u termínu, kterého si nevšimnu, se nevyvolá.

**Jméno.** Po umělém jazyce z Havlova *Vyrozumění*. Cena je, že samo o sobě nenapoví, co skill dělá; nese to `description`, ne jméno.

**Režim `add`, ne `resolve`.** „Resolve“ zní jako řešení problému; argumentem je přitom ten starý, podezřelý termín a ten se do slovníku opravdu **přidává** – u svého nástupce, aby šlo rozhodnutí dohledat nebo vrátit. **Zamítnut `settle`:** poctivěji by pokryl i konec „ponechat“, ale je to méně obvyklé sloveso. **Zamítnut `define`:** definice je výstup, kdežto podstatná půlka práce je náhrada napříč soubory.

**~~Náhrada se deleguje na `/replace`,~~ revidováno téhož dne** – viz záznam *`/ptydepe` nedeleguje na `/replace`, náhradu si dělá sám* výš. Původně to tu stálo takhle: Umí odvozené a skloňované tvary i názvy souborů a končí kontrolním průchodem. Jádro – rozhodnutí, jestli se má přejmenovat, a záznam – zůstává vlastní, takže to není alias.

**Nosná část je zákaz rekurzivního průchodu adresářem.** Při ostrém běhu přepsal skript v `~/.claude` 1 120 souborů mimo verzování: transkripty session, `history.jsonl`, cache. Nevratné, protože je git nezná. Skill proto jede výhradně přes `git ls-files` a hlídá to test ověřený mutačním testem.

**Vědomá mezera:** posouzení, jestli je termín v oboru zavedený, je odhad modelu, ne měření. Proto se každý návrh předkládá ke schválení a náhrada se nikdy nespouští sama.

**Ověřeno třemi vrstvami.** Tvar: testy repozitáře, nový test na `git ls-files` doložený mutací. Vyvolání: 24 běhů `claude -p` na skutečném kanálu, 20/24 – všechny čtyři propady byly doslovné slash příkazy a kontrolní pokus ukázal, že se v headless režimu nevyvolá ani `/worktree status`, takže je to vlastnost prostředí, ne popisu. Tlakové scénáře: tři, všechny obstály – odmítnutí `rglob` pod časovým tlakem a falešnou autoritou („minule jsi to tak dělal“), odmítnutí plošné náhrady homonyma pod zdánlivým předschválením, a odmítnutí sáhnout na archiv publikovaných textů.

**Popis se přitom zúžil** – režimy jen jmenuje místo aby převyprávěl jejich postup, a říká, že se bez načtení těla náhrada nespouští. Přeměřeno: 8/8 pozitivních a 6/6 negativních.

**Nález, který k té změně vedl, byl ale vyhodnocený špatně, a je to poučnější než ta změna sama.** Tvrdil jsem, že si model na holé `/ptydepe` přečetl `PTYDEPE.md` a začal hledat, aniž tělo skillu načetl – tedy že si popis vyrobil zkratku. **Neudělal to:** tělo měl vložené a ta četba byla poslušné plnění jeho Fáze 0, kde `PTYDEPE.md` číst má. Dohledáno 7. 9. 2026 pokusem, ve kterém model na `/ptydepe` bez čtení souborů vyjmenoval všech osm fází a dodal, že je má „z popisu skillu, který mi harness vložil do zadání“; táž otázka bez lomítka vrátila „NEMÁM“.

**Odtud plyne oprava metodiky v `/skill`, Fáze 6.** Doslovný `/jméno` harness vyřídí vložením těla, takže model nástroj `Skill` nevolá – detektor postavený na jeho volání hlásí propad tam, kde skill zabral nejspolehlivěji. Skutečné číslo tedy nebylo 20/24, ale 24/24, a stejně tak nebyly rozbité kontrolní `/worktree status` a `/autocommit status`.

### 2026-09-07 – Přepínač autocommitu bez zastřešující sekce

Projektové `CLAUDE.md` nesly přepínač jako `### Autocommit` pod nadpisem `## Automatické akce`. To zastřešení vzniklo v očekávání, že automatik bude přibývat – vedle autocommitu tehdy stál autoprompt. Stal se opak: autoprompt je od 2. 9. 2026 zrušený úplně (viz *Autoprompt zrušený úplně*) a nic dalšího nepřibylo. Zbyl nadpis nad jediným podnadpisem.

**Rozhodnutí:** přepínač je nadpis druhé úrovně `## Autocommit` přímo v projektovém `CLAUDE.md`; zastřešující sekce zaniká. V globálním `~/.claude/CLAUDE.md` totéž pro definici mechanismu, tedy `## Autocommit v projektech`.

**Definice se od přepínače odlišuje cestou, a teprve pak jménem.** Skill hledá výhradně v projektovém `CLAUDE.md`, který si našel v přípravě; globální `~/.claude/CLAUDE.md` mezi kandidáty vůbec není. V repozitáři `~/.claude` je projektovým souborem `.claude/CLAUDE.md`, takže i tam ta hranice platí. **Rozdílné znění obou nadpisů zůstává jako druhá pojistka** pro případ, že by se cesta spletla. Skill proto hledá nadpis znějící **přesně** `## Autocommit` a nadpis v globálním souboru nepočítá nikdy – ani při práci přímo v `~/.claude`.

**Srovnáno naráz všude, ne postupně.** Sedmnáct projektů v `~/Dev` plus samotný `~/.claude`; jeden z nich už nový tvar měl. Důvod pro jednorázový průchod je, že přepínač se čte strojově: projekt se starým tvarem by `/autocommit` hlásil jako vypnutý, přestože zapnutý je. Migrační tolerance by tedy musela žít v každém čtenáři, ne na jednom místě.

**Tolerance ke starému tvaru přesto zůstala, a to ve dvou režimech.** `/project` v režimu `adopt` hledá sekci bez ohledu na úroveň i zanoření a **rovnou ji dorovná**; `/autocommit` starý tvar **ohlásí a srovnání nabídne**, nepřepíše ho sám. Je to pro projekty, které v `~/Dev` nejsou nebo vzniknou z cizí kopie; jinde by se stará podoba už objevit neměla.

**Ten rozdíl je záměr, ne nedůslednost, a rozhoduje o něm, čí soubor se přepisuje.** `/project adopt` je revize, jejímž smyslem je dorovnat projekt na dnešní standardy – ptát se u každé odchylky zvlášť by z revize udělalo výslech. `/autocommit` je naopak přepínač: sáhne na jedinou sekci, o kterou ho někdo požádal, a přepsat kus **projektového** `CLAUDE.md` mimochodem k tomu nepatří.

**Na globální `~/.claude/CLAUDE.md` se to ale nevztahuje** – definici mechanismu do něj zapisuje sám `/autocommit`, je to tedy jeho vlastní sekce. Tam starý tvar srovná rovnou a jen to oznámí. Zvažovalo se ptát se i tady, kvůli jednotnosti; zamítnuto proto, že by `/autocommit on` nad instalací se starým tvarem skončil otázkou místo zapnutí, a hlavně že nechat volbu „nesrovnávat“ znamená nechat v souboru dvě definice téhož mechanismu vedle sebe. Souhlas s něčím, co nemá použitelnou druhou možnost, je jen odpověď navíc.

**Že se mezivrstva nevrátí, hlídá test**, ne jen tenhle záznam: `tests/test_skills.py` ověřuje obě strany mechanismu – že projektový `CLAUDE.md` repozitáře `~/.claude` nese `## Autocommit` a globální `CLAUDE.md` nese `## Autocommit v projektech`, ani jeden pod zastřešující sekcí. Projekty mimo tenhle repozitář nečte žádná kontrola.

**Revize 7. 9. 2026 – globální polovina mechanismu zanikla.** Ještě týž den se pravidlo autocommitu přestěhovalo do `skills/autocommit/autocommit.md` a sekce `## Autocommit v projektech` se z globálního `CLAUDE.md` **zrušila** (viz *Skill si nese své věci s sebou*). Co z výše psaného přestalo platit: druhý nadpis neexistuje, takže odpadla i „druhá pojistka“ rozdílným zněním – hranici drží už jen cesta. `/autocommit` do globálního souboru definici nezapisuje, ale naopak ji **maže**, najde-li ji tam jako pozůstatek. A test se otočil: místo `assertIn` na `## Autocommit v projektech` dnes stojí `assertNotIn`, kdežto projektová strana navíc ověřuje přítomnost importu. **Platí dál** jádro záznamu – přepínač je `## Autocommit` v projektovém `CLAUDE.md`, zastřešující sekce se nevrací a detekce se opírá o cestu, ne o jméno nadpisu.

### 2026-09-07 – `backlog.md` se zakládá s `todo.md`, ne až prací

Nezávazné nápady se dosud lily do `todo.md` a mísily se s frontou rozhodnutých úkolů. Standard proto dostal třetí soubor a hranice mezi ním a `todo.md` jde **po rozhodnutí, ne po termínu**: „až po MVP“ a „ve druhé fázi“ je nalajnovaný plán a zůstává ve frontě, kdežto nápad, který nikdo neschválil ani nezamítl, patří do backlogu.

**Zamítnuto – zakládat ho až prací**, jak to mají produktové podklady (`competition.md` a spol.). U nich prázdný soubor předstírá úvahu, která se nestala; u backlogu je prázdný soubor jen prázdná schránka. Hlavně by ale nezaložený backlog nebyl **deklarovaný v `CLAUDE.md`**, takže by o něm Claude nevěděl a nápady by dál padaly do `todo.md` – tedy přesně ta vada, kvůli které soubor vzniká. Zakládá se proto jednou volbou s `todo.md` a `done.md` jako trojice.

**Zamítnuto – rozšířit o backlog i skilly, které zapisují nálezy** (`/review`, `/attack`, `/oponent`, `/consistency`, `/release`, `/report`). Nález prověřovacího kroku je vada nebo dluh, ne nápad, takže do backlogu nepatří nikdy a jejich dnešní „odložit do `todo.md`“ platí beze změny. Hranice je zapsaná jednou ve `~/.claude/STRUCTURE.md`, *`backlog.md`*; čtyři kopie téže věty ve skillech by se rozešly. Vybírá z backlogu jediný skill – `/specify`, na začátku psaní zadání; `/cleanup` a `/project` do něj nahlížejí jen na tvar.

### 2026-09-07 – Šablony `/project` neopisují seznamy s vlastním zdrojem pravdy

`/project` psal do každého vývojářského `CLAUDE.md` větu s vypsanou cestou `/specify → /oponent → /breakdown → /implement`. Když do životního cyklu přibyl `/discovery`, řetěz zůstal **formálně platný, jen neúplný** – existující skilly ve správném pořadí –, takže ho neodhalila kontrola existence odkazů ani kontrola pořadí kroků a projekty ho četly jako úplný seznam. Našlo se to až nálezem v jednom projektu; vadu měl i druhý.

**Zamítnuto – doplnit `/discovery` do výčtu.** Opravilo by to dnešek a zopakovalo vadu při příštím kroku. Šablona teď na *Životní cyklus projektu* jen odkazuje.

**Poučení je širší než ten jeden řádek** a je zapsané v `~/.claude/skills/SKILLS.md`, *Jak se píše text uvnitř*: neopisuje se žádný seznam, který má vlastní zdroj pravdy – kroky cyklu, prahy kontrol, inventář domén. Řetěz tří a víc kroků v `SKILL.md` hlídá test; dva sousedi zůstávají povolení, protože „navazuje na `/specify`“ je popis vazby, ne opis pořadí. **Kontrola existence nestačí** – zastaralý výčet ukazuje na existující věci a vypadá platně.

**Z toho plyne i nová oblast v `/project`, krok 14:** revize čte **znění** generovaných sekcí, nejen jejich existenci, a porovnává dnešní výčet standardních souborů proti tomu, co projekt má. Do té doby se nový standardní soubor doplnil jen tehdy, když to někdo ručně dopsal do textu skillu – u `done.md` i produktových podkladů to tak bylo, takže mechanismus vypadal funkčně, aniž byl.

### 2026-09-07 – `/autocommit` zůstává samostatný, do `/project` se nevstřebá

Od revize 4. 9. 2026 leželo v `todo.md`, že by se `/autocommit` mohl vstřebat do `/project`, který zapnutí autocommitu umí jako jeden ze svých kroků. Uzavřeno **zamítnutím**.

**Duplicita, kvůli které položka vznikla, neexistuje.** `/project` v kroku 9 na `/autocommit` odkazuje („proveď totéž co `/autocommit on`“), nemá jeho postup opsaný. Vstřebání by tedy nic neodstranilo, jen přesunulo.

**Vypnout přepínač jde jen tudy.** `/project` se na autocommit ptá v rámci celého průchodu; hnát třináctikrokový wizard kvůli jedné sekci v `CLAUDE.md` je nepoměr, a u režimu `off` by nebylo čím ho nahradit.

**Skill si lidé instalují sólo.** `/autocommit` stojí mimo životní cyklus, má vlastní `README.md` a instaluje se samostatně; vstřebáním by ta cesta zmizela.

**Zbylé argumenty pro vstřebání** – o skill míň, o hlavičku míň – neváží proti tomu nic: skill má 73 řádků a od 7. 9. 2026 odpovídá normě `SKILLS.md`.

### 2026-09-07 – Skill si nese své věci s sebou

Provozní pravidla worktree layoutu i postup jeho zřízení ležely v `~/Dev/context/worktree/`, tedy v soukromém repozitáři, přestože je odkazovalo dvanáct veřejných skillů a `PREFLIGHT.md`. Kdo si některý z nich nainstaloval z GitHubu, dostal odkaz do adresáře, který nemá. Autocommit měl obrácenou vadu: pravidlo stálo v globálním `~/.claude/CLAUDE.md`, opsané i ve skillu, a rozbalovalo se do každé session v každém projektu – tedy i tam, kde je autocommit vypnutý.

**Rozhodnutí:** skill si nese všechno své ve svém adresáři. Vyjmuty jsou jen věci, které jsou z podstaty sdílené – `PREFLIGHT.md`, `RULES.md` a norma `SKILLS.md`.

**Provozní pravidlo je samostatný soubor, ne tělo `SKILL.md`.** Tělo se načte, jen když někdo skill vyvolá, kdežto pravidla layoutu potřebuje `PREFLIGHT.md` před během každého skillu a pravidlo autocommitu platí při běžné práci. Vznikly proto `~/.claude/WORKTREE.md` a `skills/autocommit/autocommit.md`, oba importované do projektu přes `@`.

**Ty dva soubory ale neleží stejně, a rozhoduje o tom týž test jako u `structure.md`: kdo je čte.** `autocommit.md` čte jedině `/autocommit` a projekt, který si ho naimportoval – zůstává tedy uvnitř skillu. `WORKTREE.md` čte **dvanáct skillů a `PREFLIGHT.md`**, takže patří do kořene vedle `RULES.md` a `STRUCTURE.md`.

**Nejdřív jsme ho uvnitř skillu nechali a bylo to špatně.** Argument, že „skill si nese své věci s sebou“, vyhrál nad argumentem o čtenářích – přestože o dva odstavce dál v záznamu o `structure.md` stálo, že devět skillů odkazujících dovnitř desátého je důvod k přesunu ven. Byla to tedy dvě různá rozhodnutí podle jednoho kritéria a jen jedno z nich to kritérium použilo. **Našel to čtenář bez kontextu v `/cleanupu` téže session** a přesun se dodělal hned; praktický důsledek by byl, že kdo si nainstaluje `/review` bez `/worktree`, dostane v přípravě odkaz na soubor, který nemá – tedy přesně ta vada, kvůli které se celý přesun dělal.

**Kritérium tedy zní: čte to víc skillů než ten, komu to patří?** Ano → kořen `~/.claude`. Ne → adresář skillu. Vlastnictví rozhoduje jen tam, kde je čtenář jediný.

**Import se zapisuje tam, kde má pravidlo platit** – to je celý mechanismus a je u obou skillů týž. `/autocommit` píše do sekce `## Autocommit` v projektovém `CLAUDE.md`, protože tam pravidlo platí při práci na projektu. `/worktree` píše do rozcestníku v kořeni kontejneru, protože session startuje tam a Claude potřebuje vědět o layoutu dřív, než si vybere adresář; import až v `main/CLAUDE.md` by přišel pozdě.

**Stav se u každého skillu zjišťuje jinak, a je to záměr.** Autocommit ho nese jako zápis (nadpis `## Autocommit`), worktree jako tvar adresáře (`.bare` vedle `.git`). Druhé je spolehlivější – nemůže se rozejít s realitou –, ale první je jediná možnost tam, kde není co detekovat.

**Režimy sjednoceny na `enable`/`disable`/`status`** (výchozí `status`) místo dosavadních `on`/`off`. Norma žádá, aby se totéž napříč skilly jmenovalo stejně, a oba skilly odpovídají na tutéž otázku „zapni tenhle režim v tomhle projektu“. Zvažovalo se u `/worktree` pojmenovat režimy tak, aby přiznávaly váhu operace – `enable` přeskládá `.git`, kdežto u autocommitu jde o jeden nadpis –, zamítnuto ve prospěch lícování.

**`/worktree` nově umí i `disable`**, tedy návrat na obyčejný adresář; dosud postup neexistoval. Odmítne běžet, dokud zbývá jiný worktree než `main` – slití nebo zahození větve je rozhodnutí uživatele.

**Zamítnuto – vytáhnout pravidla do `~/.claude/standards/`.** Skill by se pak neinstaloval jedním adresářem a odkaz na GitHub by vedl na půlku funkce.

**Migrováno naráz:** sedmnáct projektů dostalo import do sekce `## Autocommit`, čtyři rozcestníky kontejnerů novou cestu, dvanáct skillů a `PREFLIGHT.md` přepsané odkazy. Postupná migrace nepřipadala v úvahu ze stejného důvodu jako u předchozího záznamu – přepínač i import se čtou strojově, takže starý tvar tiše nefunguje.

**Obě strany hlídá test.** `tests/test_skills.py` ověřuje, že projektový `CLAUDE.md` tohohle repozitáře nese přepínač i s importem a že se definice autocommitu nevrátila do globálního souboru. Zanikl naopak test na shodu šablony se `CLAUDE.md`: duplicita, kterou hlídal, přestala existovat.

### 2026-09-07 – Standard struktury projektu je veřejný, ale nepatří žádnému skillu

Po přesunu worktree a autocommitu zbyl `structure.md` jako poslední soubor, který odkazovalo devět veřejných skillů a `RULES.md`, ale sám ležel v soukromém repozitáři. Nabízelo se aplikovat týž princip a přisoudit ho `/project`, který ho instaluje.

**Rozhodnutí:** `~/.claude/STRUCTURE.md` v kořeni veřejného repozitáře, sourozenec `RULES.md`. **Zamítnuto `skills/project/structure.md`** – princip *skill si nese své věci s sebou* se na něj nevztahuje.

**Rozhoduje vlastnictví, ne počet čtenářů.** Ten je u obou skoro stejný (12 skillů u worktree, 11 u struktury), takže se podle něj rozhodnout nedá. `worktree.md` ale zakládá a instaluje jediný skill a ostatní z něj chtějí jednu věc – kde stojím. Ze `structure.md` si každý bere něco jiného: `/oponent` a `/review` *Běhový stav skillů*, `/attack` a `/release` sekci *`done.md`*, `/cleanup` hranici *`backlog.md`*, `/specify` *Produktové podklady*. Dva do něj navíc zapisují. `/project` ho instaluje, ale nevlastní.

**Kdyby šel do adresáře skillu, rozbily by se tři věci naráz:** devět skillů by odkazovalo dovnitř desátého, což norma `SKILLS.md` zakazuje; kdo si nainstaluje `/cleanup` bez `/project`, neměl by standard, podle kterého `/cleanup` třídí; a `@import` v globálním `CLAUDE.md` by mířil dovnitř skillu, který jde odinstalovat.

**Kořen, ne `skills/`.** Precedens `PREFLIGHT.md` a `SKILLS.md` – sdílené věci, které nepatří žádnému skillu – sem nesedí úplně: ty dvě mluví **o skillech**, takže leží mezi nimi. `STRUCTURE.md` mluví o projektu, tedy patří vedle `RULES.md`. Oba jsou navíc v `CLAUDE.md` importované natvrdo přes `@` jako závazná pravidla; jeden v kořeni a druhý v podadresáři by tvrdil rozdíl, který mezi nimi není. **Podadresář `standards/` se otevře, až jich bude víc** – dnes by to byl obal nad jedním souborem.

**Tři odkazy do `~/Dev/context/coding/coding.md` přepsány věcně, bez odkazu** – kontrakt příkazů, průběžná kontrola a rozcestník doménových standardů. Veřejný soubor tak neukazuje do adresáře, který cizí čtenář nemá. Nic se tím neztrácí: projekt, kde na standardech kódu záleží, si `coding.md` importuje ve svém `CLAUDE.md` natvrdo, takže platí celý bez ohledu na tenhle odkaz. Ověřeno – sedm projektů s kódem ho takhle má.

**Jeden projekt z migrace vynechán.** Měl rozdělanou cizí práci včetně `CLAUDE.md` a odkaz na standard v něm nebyl; sáhnout na něj by znamenalo commitnout cizí rozepsané změny. Dorovná se, až se v něm bude pracovat.

**Zvažováno a zúženo: `coding.md`, `text.md` a `design.md` zůstávají soukromé.** Obsahově citlivé nejsou – neobsahují klientská jména ani osobní data – a `text.md` s `typography.md` jsou převážně opis kodifikovaných pravidel. Rozhodl týž test jako u zbytku: **je to infrastruktura, kterou skilly potřebují k běhu, nebo profesní standard?** `worktree.md` a `structure.md` bez veřejného umístění rozbíjejí nainstalovaný skill; `coding.md` je názor na to, jak se píše kód, a `/review` bez něj doběhne. `design.md` navíc sám sebe označuje za rozdělaný startovní bod. Není to zamítnutí navždy – je to volba pro tenhle průchod; k `design.md` se dá vrátit, až bude hotový.

**Zamítnuto – `~/.claude/standards/` jako podadresář.** Dnes by to byl obal nad jedním souborem. Otevře se, až jich v kořeni bude víc; do té doby `STRUCTURE.md` leží vedle `RULES.md`, se kterým sdílí status závazného pravidla importovaného přes `@`.

### 2026-09-10 – Skill `/learn`: nová znalost se zapracovává dovnitř báze, ne vedle ní

Vznikl skill `/learn` (`~/.claude@b78caa4`). Řeší mezeru mezi `/transcript` a knowledge base: z přepisu školení nebo konzultace se dá vytěžit hodně metodiky, ale ta se dosud buď nezapsala vůbec, nebo skončila jako další samostatný soubor vedle stávající struktury – tedy na místě, kde ji nikdo nehledá.

**Vytěžení je oddělená fáze a musí být vyčerpávající**, protože zdroj po zapracování zaniká: přepis klientské schůzky se do znalostní báze nekopíruje (citlivý materiál a báze má držet znalost, ne doklady), takže co se nevytěží, se už nikdy nedohledá. Úplnost proto ověřuje izolovaný agent, který nevidí, jak seznam vznikal – kdo seznam psal, hledá v něm právě to, co už tam dal.

**Rozpor se řeší dotazem, ale jen skutečný rozpor.** Konzultace říká věci hruběji a rozebírá jednu variantu; to není nekonzistence, ale jiná hloubka. Skill proto rozlišuje doplnění, prohloubení, zjednodušení, zúžení a zastarání od případu, kdy by čtenář **ve stejné situaci** jednal podle každé verze jinak – a jen ten předkládá. Důvod je provozní: falešný rozpor stojí uživatele rozhodnutí, které nemá co rozhodovat, a po třetím takovém se skill přestane pouštět.

**Zamítnuto – deklarace editovatelnosti v `CLAUDE.md` cílové báze.** Nabízelo se, aby si repozitář po doménách zapsal, kam se smí sáhnout hluboko a kam ne. Prohrálo to se dvěma věcmi: byl by to skrytý stav navíc, který se rozejde se skutečností, a hlavně **oprávnění dává zadání** – „zapracuj to do `analytics`“ je svolení samo o sobě. Skill místo toho odvozuje hloubku zásahu z **povahy textu**: metodika (jak se něco dělá) se přepisuje volně, fakta a hotové formulace se jen doplňují, doklad (co se stalo, co kdo řekl) se nepřepisuje vůbec. Kritérium je povaha, ne jméno adresáře – doklad může ležet uvnitř metodické domény.

**Zamítnuto – ukládání zdroje do báze jako dokladu.** Přepisy klientských schůzek by tím natekly do knihovny. **Dohledatelnost ale nezaniká** – skill místo toho doplní řádek do evidence zdrojů cílové domény: odkud zdroj je, co se z něj vzalo a co v něm zůstalo otevřené. Je to totéž, co rozhodl *2026-09-08 – Zdrojové záznamy zůstávají mimo repozitář, sem jde jen odkaz*; **první znění tohohle zápisu se s ním rozešlo** (tvrdilo, že stopu drží commit message) a opraveno bylo až při úklidu 10. 9., kdy se to rozhodnutí našlo. Commit message ty dvě věci nezastane: nikdo v ní nehledá, odkud tvrzení pochází, ani jestli se dá záznam projít podruhé.

**Postup vytěžení žije ve skillu, ne v doméně.** Kapitola *Jak se záznam vytěžuje* v `analytics/sources.md` vznikla 8. 9. z prvního ručního vytěžení a byla by druhým zněním téhož; nahradil ji odkaz. Dvě pravidla, která měla navíc – **odlišit jisté od tipnutého** a **vypustit identifikaci klienta** –, se před tím přenesla do skillu, protože platí v každé doméně, ne jen v analytice.

**Jméno vybráno ze čtyř; `absorb` prohrál se srozumitelností.** Doporučený byl `absorb` – „vstřebat“ nejlíp popisuje, že po zdroji nezůstane samostatný kus. Vyhrál `learn`, protože se nejlíp pamatuje a je to slovo, které člověk sám použije. **Cenou je horší spouštěč:** „nauč se“ je obecný obrat a popis se proto musel ladit proti falešnému vyvolání. Zvažován ještě `enrich` (přesný, ale neříká, že vstupem je konkrétní dokument) a `integrate`, `weave`, `distill`, `graft`, `ingest`, `assimilate`.

**Zamítnuto – nabízet přesměrování toho, co není přenositelná znalost.** Skill mohl u klientských specifik a osobních věcí nabídnout, že je odloží do profilu organizace nebo do fronty úkolů. Zůstalo u prostého výpisu „nezapracováno a proč“: rozhoduje o tom uživatel dalším příkazem a jedna otázka navíc v každém běhu by se neodklikávala. Podstatné je, že je **vidět rozdíl mezi „posoudil jsem a nepatří to tam“ a „přehlédl jsem to“** – a to prostý výpis splní.

**Zamítnuto – režimy.** Skill má jediné chování; `dry run` by duplikoval plán, který se předkládá vždycky.

**Měření vyvolání: 12/12** na skutečném kanálu (`claude -p --output-format stream-json`), šest pozitivních a šest negativních – práh z `~/.claude/skills/skill/SKILL.md`, *Fáze 6*. Doměřeno při úklidu, protože první běh skončil na pěti a pěti. Mezi negativními je i **„založ mi novou doménu“**, tedy near-miss braný přímo z popisu skillu; nechytil se, což je u obecného jména jako `learn` to podstatné. První kolo dalo 6/8 a jeho dva propady měly každý jinou příčinu: „zakomponuj“ v `description` opravdu chybělo a po doplnění prošlo, kdežto „nauč se“ propadlo jen proto, že v měřicím adresáři nebyl soubor, o kterém prompt mluvil – s ním prošlo na první pokus, stejně jako později přidané „obohať metodiku“. **Rozlišit to bylo podstatné**: bez toho by se popis přepisoval kvůli propadu, se kterým nemá nic společného. Poznatek je zapsaný v `/skill` jako třetí známá vada měřidla vedle `run_eval.py` a doslovných slash promptů. **Tlakové scénáře neproběhly**, protože session zakazovala spouštění agentů; skill přitom vynucuje dvě věci (nesahat na doklady, nepsat před odsouhlasením plánu), takže je to nedoměřená vrstva.

### 2026-09-10 – `PTYDEPE.md` rozdělen na tabulku v kontextu a rozvahu u skillu

Soubor se importuje do každé session a měl 23 kB, protože ke každému termínu nesl celou úvahu, zamítnuté varianty a historii náhrady. Rostl lineárně s každým dalším vypořádaným termínem, takže by za rok byl největší položkou globálního kontextu.

**Rozhodnutí:** rozdělit podle cílové skupiny (`~/.claude/RULES.md`, *Cílová skupina určuje umístění*). `~/.claude/PTYDEPE.md` je nadále **jen tabulka** `Nepoužívej | Používej | Rozsah a meze`, 5,3 kB, a importuje se dál. Rozvaha se přestěhovala do `~/.claude/skills/ptydepe/terms.md`, který se neimportuje nikam a čte ho `/ptydepe`. Nové heslo přidá jeden řádek tabulky místo odstavce, takže růst kontextu se prakticky zastavil.

**Není to dvojí zápis téhož.** Tabulka je jediný zdroj toho, co se čím nahrazuje; `terms.md` jediný zdroj toho, proč. Nepřekrývají se, takže *Single source of truth* platí – zápis do obou míst je proto ve *Fázi 6* skillu povinný.

**Ponechané termíny se při té příležitosti sjednotily.** Dosud ležela rozhodnutí o **náhradě** v `PTYDEPE.md` a rozhodnutí o **ponechání** tady v `decisions.md`, tedy dvě půlky téže rozvahy na dvou místech. Osm termínů v šesti zápisech (`heuristika`, `osa`, `vektor útoku`, `mutace`, `session`, `soustava`, `kontrakt příkazů`, `sledovací okno`) se přesunulo do sekce *Ponechané termíny* v `terms.md`; tady po nich zůstala stopa s odkazem.

**Ušetřilo se v kontextu, ne v součtu.** `terms.md` má po přesunu 33 kB, tedy víc, než měl původní `PTYDEPE.md` – přibraly do něj ty ponechané zápisy. To je v pořádku: soubor se neimportuje nikam, takže jeho velikost nikoho nestojí kontext.

**Odrážka o propagaci do `~/Dev` se do tabulky vědomě nevrátila.** Původní `PTYDEPE.md` nesl větu, že se termín při změně mění všude naráz včetně `~/Dev`. Je to instrukce pro náhradu, ne pro běžnou session – a ve `SKILL.md` už stojí konkrétněji ve *Fázi 0*, která jmenuje kořeny (`~/.claude`, `~/Dev/context`, další repozitáře v `~/Dev`). V tabulce by to byl pokyn pro toho, kdo ji nikdy nevykonává.

**Zamítnuto – zapsat rozvahu do `## Claude` v tomhle souboru.** `decisions.md` má 286 kB, takže by ho `/ptydepe` musel číst celý kvůli 27 heslům a šesti zápisům o ponechaných termínech, a platí v něm „nejstarší nahoře, přidávej na konec“, protože se čte jako vývoj uvažování. Heslář se takhle uspořádat nedá – ten se čte skokem na jedno heslo.

**Zamítnuto – nechat soubor neimportovaný a spoléhat, že si ho model načte, až bude potřeba.** Nefunguje: model neví, že sahá po nezavedeném termínu, právě to je ta vada. Prevence musí být v kontextu, jen musí být tenká.

**Zamítnuto – test, který grepne zakázané tvary a spadne, když se některý vrátí.** Nabídnuto jako doplněk k prevenci (`RULES.md`, pravidlo nula: co chytne test, se nemá hlídat tokeny), uživatelem zamítnuto. Chytilo by to jen zápis do souborů, ne mluvenou odpověď, a vyloučit legitimní homonyma (platební brána, jazyková mutace, časová osa) by znamenalo vést vedle tabulky druhý seznam výjimek. Kdyby se to někdy dělalo, musí se ta úvaha udělat znovu – tady je zapsané jen to, že se dnes vědomě nedělá.

### 2026-09-10 – rozhraní kroků cyklu a katalog struktury se přestaly načítat do každé session

Paušální kontext byl ráno **118 kB** – `CLAUDE.md`, `RULES.md`, `STRUCTURE.md` a `PTYDEPE.md` dohromady, tedy zhruba 40–50 kB textu navíc v každé session každého projektu, ještě než padne první slovo. `PTYDEPE.md` řešila vedlejší session (23 kB → 5 kB) a srazila to na **100 kB**; tenhle zápis je o zbytku.

**Rozhodnuto – dva soubory ven z importů, žádná věta se nemaže.** Sekce *Životní cyklus projektu* (10,6 kB, pětina `RULES.md`) se přestěhovala do `~/.claude/skills/LIFECYCLE.md` a `STRUCTURE.md` (33 kB) se přestal importovat. Paušál je po tom **58,7 kB**. Šetří se tím, *kdy* se text načte, ne tím, co v něm stojí.

**`LIFECYCLE.md` je v `skills/`, ne v kořeni.** Vzniká tam čitelná trojice `SKILLS.md` (jak vypadá skill) – `PREFLIGHT.md` (jak začíná) – `LIFECYCLE.md` (v jakém pořadí jdou); kořen zůstává pravidlům práce. Zamítnuto `~/.claude/LIFECYCLE.md`: pátý normativní soubor v kořeni by rozmazal hranici proti `skills/`.

**`STRUCTURE.md` se nedělí na jádro a katalog.** Vznikla by dvojice jmen, kterou nikdo nerozliší (`STRUCTURE.md` × `FILES.md`), a jádro by stejně byla jen tabulka *otázka → soubor*. Ta je teď v `RULES.md` jako sekce *Kam co zapsat* a odkazuje na katalog. **Nebyl to hned přesun, ale kopie** – ve `STRUCTURE.md` tabulka zůstala stát a odhalil to až čtenář bez kontextu v `/cleanupu` téže session (`~/.claude@47c8aa3`); tam ji dnes nahrazuje odkaz nahoru.

**Katalog nesmí skončit pod `skills/project/`**, i když ho `/project` spravuje: čte ho i `/specify`, `/breakdown`, `/cleanup` a `/implement`, a norma zakazuje odkazovat dovnitř cizího skillu. U `PTYDEPE.md` to vyšlo jen proto, že `terms.md` čte jediný skill – tenhle rozdíl je důvod, proč se stejný vzor nedal zopakovat.

**Rámeček s pořadím zůstal v `RULES.md` a je zdrojem pravdy.** `LIFECYCLE.md` ho neopisuje – nesl by druhou kopii, která se rozejde. Testy čtou kroky dál z `RULES.md` a nový test ověřuje, že číslované odrážky v `LIFECYCLE.md` jmenují tutéž množinu.

**Mechanismem je `PREFLIGHT.md` plus tři testy, ne dobrá vůle.** Příprava skillu nově žádá načtení obou souborů; testy hlídají, že se `@` nevrátí do `CLAUDE.md`, že příprava ten pokyn nese a že se seznam kroků nerozejde. Všechny tři ověřeny mutací.

**Vědomě přijatá sleva: práce mimo skill.** Zapisuje-li se do `todo.md` v běžné konverzaci bez skillu, žádný mechanismus nenutí `STRUCTURE.md` načíst – zbývá odkaz v `RULES.md`, *Kam co zapsat*. Je to táž nespolehlivost, jakou `CLAUDE.md` přiznává u doménových znalostí („odkaz se dodržuje hůř než import, ale je to vědomá volba“). Projeví se to tak, že zápis půjde do správného souboru, ale ve špatném tvaru – ne ztrátou.

**Zbývá:** stlačit `RULES.md` (45,5 kB) samotný – oddělit datované doklady incidentů od pravidel, zkrátit *Model a effort*, projít překryv se `STRUCTURE.md`. To je práce s textem a čeká na samostatný běh.

Commit `~/.claude@388c4b1`.

### 2026-09-10 – doklady incidentů odešly z `RULES.md`, samotná pravidla zůstala

Pokračování téhož úklidu: `RULES.md` se stlačil z **45,5 kB na 43,8 kB**, tedy o **3,8 %**; paušální kontext tím klesl na **57,4 kB**. (Kumulativně s vytažením cyklu je to 53,9 → 43,8 kB, ale těch 8,4 kB si už započítal zápis nad tímhle – **nesčítej to podruhé**. Čísla jsou změřená až po opravách obou kol čtenáře bez kontextu; ta předchozí byla o 0,7 kB nižší, protože se změřila před nimi.) Žádné pravidlo nezmizelo – ubraly se rozvedené doklady, dvě formulace se sloučily a vypadl překryv se `STRUCTURE.md`.

**Doklady zůstávají u pravidla jen datem.** Pravidlo potřebuje **jednu větu proč**; datovaný incident je doklad pro toho, kdo se ptá „fakt se to stalo?“, a ten se čte jednou za rok. V `RULES.md` u pravidla proto stojí `Doloženo 6. 9. 2026.` a celý příběh je tady. Tři, které nikde jinde zapsané nebyly:

- **Snímek souboru v kontextu není soubor** (6. 9. 2026). Umlčený nález `/review` se ověřoval proti hashi a cestě ze zastaralého snímku `CLAUDE.md`, který ležel v kontextu od začátku session. Ohlásila se expirace umlčení, která nenastala, a padlo na tom rozhodnutí. Zrádné je, že si model myslí, že tvrzení **ověřené má** – obsah toho souboru přece vidí.
- **Vlastní kontrolu neumí vyzkoušet ten, kdo ji napsal** (6. 9. 2026). Čerstvý test prošel oběma mutacemi, které mu zkusil jeho autor, a spadl na třech, které zkusil nezávislý agent. Autor zkouší právě ta selhání, se kterými při psaní počítal.
- **Rozsah pravidla se nešíří sám** (6. 9. 2026, dvakrát v jednom dni na `/transcript`). Pravidlo o opravě pravopisu se zapsalo do *Pravidel doslovného přepisu*, jejichž rozsah je přepis. Shrnutí se řídí *Pravidly shrnutí*, kde o jazyce nebylo nic – a gramatická chyba opravená v přepisu prošla do souhrnného dokumentu, protože se píše z téhož podkladu. Totéž se ten den zopakovalo u majitelů úkolů.

**Incident s `git add -A`** se sem nepřepisoval, je výš u zápisu z 3. 9. 2026. Commit `~/.claude@67ddb52`.

**Sloučeno, ne smazáno:** *Model a effort* (4,5 kB → 4,0 kB) přišel o dublovaný příklad a *Nejsilnější neznamená nejdražší dostupný* se vtělilo do odstavce o eskalaci effortu, kam patří významem. Hranice `todo.md` proti `backlog.md` se v *Odložených věcech* přestala vykládat podruhé a odkazuje na `STRUCTURE.md`; zůstalo z ní jen kritérium **rozhodnutost, ne termín**, které je potřeba v místě rozhodování. **Napodruhé** – první pokus ji jen přesunul o dvě sekce výš a v *Odložených věcech* nechal taky; dorovnal to až druhý čtenář bez kontextu (`~/.claude@3e4ef4f`).

**Kde se přestalo – a že to není dotažené.** Původní rozvaha měla šest bodů a dodané jsou tři a půl. Vytažení cyklu a odpojení `STRUCTURE.md` proběhlo celé; zbytek ne:

| Bod | Odhad | Skutečnost |
|---|---|---|
| Doklady od pravidel | −8 až 10 kB | asi −1 kB; dokladů bylo šest, ne dvacet, a půlka z nich nesla nosné vysvětlení |
| *Model a effort* na tabulku a odrážky | −2,5 kB | −0,5 kB; výklad pod tabulkou tam celý zůstal |
| Stylistická komprese souboru | −15 až 20 % | **neuděláno**; v souboru je pořád deset odstavců uvozených `**Proč:**` |
| Překryv `RULES.md` × `STRUCTURE.md` | projít systematicky | prošla dvě místa, na která se narazilo; kolik dalších se rozchází, není známo |

**Odhady u prvních dvou byly řádově mimo**, protože vznikly od oka podle dojmu z pár nápadných odstavců, ne měřením – a neopravily se ani potom, když už byly doklady vypsané a bylo vidět, že jich je šest. Zjistilo se to teprve na přímý dotaz uživatele, jestli se udělaly všechny body; do té doby byla práce ohlášená jako hotová.

**Uživatel pak dodělání odmítl** („ne, nech to“) – tedy vědomě, ne opomenutím. Neznamená to, že je `RULES.md` stlačený na maximum: znamená to, že se za zbylými kilobajty dnes nejde. Kdo na to naváže, ať vychází z tabulky výš, ne z dojmu, že úklid skončil, protože nebylo co brát.

- **Historie main drží jeden řádek na větev přes `git log --first-parent`, ne přes squash** (14. 9. 2026). Cílem bylo, aby se v `git log` neroztekly desítky commitů ze zamergované větve. Ve hře byly tři varianty. **Squash merge** zavržen: dílčí commity přestanou být z main dosažitelné, po smazání větve je sebere garbage collector, `git branch -d` odmítne a další merge naseká konflikty – „dostat se k dílčím commitům“ by přestalo být vlastností gitu a stalo se ruční disciplínou. **Squash s archivním tagem** zavržen jako totéž s ruční údržbou navíc. Zvolen `--no-ff` merge se čtením přes `--first-parent`: data zůstanou úplná, mění se jen zobrazení. Cena je jediná – zpráva merge commitu musí něco říkat, protože je v tom výpisu jediné, co o větvi bude vidět. Aliasy v `~/.gitconfig` posunuty: `git l` má nově `--first-parent`, `ll` je původní `l`, `lll` původní `ll`.

- **Zprávu merge commitu vynucuje git hook, ne jen pravidlo v textu** (14. 9. 2026). Samotné pravidlo ve `WORKTREE.md` zavrženo: vykonává ho tentýž model, který ho čte, takže je to přání, ne hranice (`~/.claude/RULES.md`, *Přednost pravidel*). Hook jen v tomhle repozitáři zavržen: pravidlo platí pro všechny projekty. Zvolen `githooks/commit-msg` nasazený globálně přes `core.hooksPath`. Hlídá jen hlavní větev, deleguje na lokální `.git/hooks/commit-msg` (jinak by ho globální nastavení tiše vypnulo) a ostatní typy lokálních hooků tím nasazené nejsou – projekt, který je potřebuje, si nastaví vlastní `core.hooksPath`.

- **CI čte kontrakt přes `verify.sh --contract`, ne vlastním parserem** (14. 9. 2026). Workflow si sekci `## Kontrakt příkazů` nejdřív parsovalo samo. Ta druhá implementace se s `verify.sh` rozešla ve třech vlastnostech naráz – nefiltrovala HTML komentáře, neměla pojistku proti dvěma sekcím téhož jména a neznala klíč `cwd` –, takže lokální kontrola a CI měřily jiné příkazy a nikdo to nemohl poznat. Přidán přepínač `--contract`, který kontrakt vypíše ve tvaru `klíč<tab>příkaz` a nic nespouští, takže souhlas nepotřebuje. Odvozené projekty si `verify.sh` musí na runner dostat samy; `skills/project/checks.md` to říká i s tím, že stažení se má připnout na commit.

- **Souhlas pro průběžnou kontrolu se váže na kontrakt, ne jen na repozitář** (14. 9. 2026). Klíč ze sdíleného `.git` platil pro celý strom, takže si jakýkoliv podadresář mohl přinést vlastní `CLAUDE.md` a jeho příkazy se spustily bez dotazu – ověřeno neverzovaným `vendor/cizi/CLAUDE.md`. Porovnávat cestu projektu zavrženo: rozbilo by to worktree jiné větve, kvůli kterému se klíčuje sdíleným `.git`. Zvoleno: kontrakt musí ležet v **kořeni pracovního stromu** (worktree jím sám je, podadresář ne) a souhlas nese **otisk sekce kontraktu**, takže jeho změna si vyžádá nové odsouhlasení.

- **Souhlas vydá jen člověk u terminálu** (14. 9. 2026). Chránilo ho šest deny pravidel v `settings.json`, jenže ta porovnávají text příkazu: volání přes `python3 -c`, `node -e` nebo `osascript` jméno skriptu do příkazové řádky vůbec nedostane. Při vlastní revizi se navíc ukázalo, že neplatí ani v přímém tvaru, je-li volání součástí složeného příkazu – doloženo tím, že si agent souhlas omylem vydal sám. Lepší seznam vzorů zavržen jako dohánění nekonečné množiny tvarů. Zvoleno potvrzení ze stdin (je-li terminál) nebo z `/dev/tty`, kterou proces bez řídicího terminálu nemá. Testy si terminál opatřují přes `pty.openpty()`, ne obejitím podmínky proměnnou – vypínač v testu by z pojistky udělal dekoraci.

- **Souhlas ve starém formátu neplatí a řekne se to** (14. 9. 2026). Souhlasy vydané před zavedením otisku mají jediný řádek a nedá se z nich zjistit, na co byly vydané. Tolerovat je zavrženo: tichý degradovaný režim je přesně ten vzor, který tahle oprava odstraňuje. Hook je odmítne a vypíše příkaz k obnovení; cenou je, že po nasazení bylo potřeba obnovit všech pět.

- **Deny seznam v `settings.json` není bezpečnostní hranice, ale doporučení** (14. 9. 2026). Vyplynulo z revize a platí obecně: pravidla porovnávají text příkazu, takže je obejde kterýkoliv plošně povolený interpret, a u `Read` navíc platí jen relativně ke kořeni aktuálního projektu – soubory mimo něj nechrání vůbec (ověřeno návnadou). **Nestaví se na něm nic, co má doopravdy držet.** Kde je potřeba skutečná hranice, musí stát mechanismus, který si model nemůže odsouhlasit sám: potvrzení na terminálu, souhlas v souboru mimo repozitář, potvrzovací dialog.

### 2026-09-15 – `/depot` je mechanika ve veřejném repozitáři, pravidla v privátní doméně

Zakládání skillu, který převezme stažený soubor, uloží ho tam, kam patří, a rovnou spustí navazující zpracování. Rozdělený je stejně jako `/audit` a `/invoicing`: veřejný `~/.claude/skills/depot/` drží mechaniku a nenese jediné konkrétní pravidlo, privátní doména `~/Dev/context/depot/` drží směrovací tabulku. Kdo si skill stáhne z GitHubu, napíše si tabulku podle svého.

**Doména je jeden soubor a rozdělí se, až poroste.** Aby to skill nepocítil, čte ji přes rozcestník a hledá *věci*, ne jména souborů – pozdější rozpad na `depot/<workflow>.md` je pak úprava uvnitř domény.

**Termín: `workflow`.** Doporučen byl `charakter` (pojmenovává rozpoznanou vlastnost a nejde splést s příponou); rozhodnuto pro `workflow`, protože těžiště má být v tom, co se se souborem děje dál. **Zamítnut `scénář`** – sráží se se zavedeným významem v `PTYDEPE.md` (*hlavní scénář*) a ve `/attack`. Cena volby je přiznaná: `workflow` je anglicismus, který norma skillů ani redakční standard jinak nepřipouštějí. **Rozsah termínu je `/depot` a jeho doména, nikam dál se nešíří** – jinde zůstává postup, fáze, scénář. **Zamítnut řádek v `~/.claude/PTYDEPE.md`:** ten drží termíny platné napříč projekty a zápis by z jednorázové volby udělal precedens pro celý ekosystém.

**Zamítnuto – kopírovat originál místo přesunu:** dvě kopie téhož podkladu znamenají, že se příště nepozná, která je ta zaevidovaná. **Zamítnuto – při kolizi přejmenovat na `(1)`:** v `~/Depot` je název identifikátor, na který odkazuje `sources.md`, a sklad není verzovaný. **Zamítnuto – samostatný režim `rules`:** pravidla se zapisují i za běhu nad nerozpoznaným souborem; nakonec ale režim `workflow` zaveden na přání, protože se řádek často upravuje mimo konkrétní soubor.

**Srovnávací běh (bez skillu) rozhodl o sekci *Rozsah*:** agent si rozšířil rozsah ze dvou předaných souborů na celé `~/Downloads` (5 685 položek) a kvůli tomu rozsahu se zastavil, aniž hnul jediným souborem. Rozšíření rozsahu se tváří jako služba navíc.

**Vědomé mezery:** doména nemá zapsané přijaté faktury a doklady, videa natočeného kurzu (cíl neexistuje) ani screenshoty k rozdělané práci. Vedeny v `depot.md`, *Co zatím zapsané není*, aby se nepletly s opomenutím.

### 2026-09-16 – `/next`: fronta další práce, obsazené a opuštěné větve, nabídka kol přestěhovaná ze `/specify`

Na začátku každé session v rozdělaném projektu padal týž dlouhý prompt: vypiš, s čím můžeme pokračovat, seřaď podle důležitosti a závislostí, u každého úkolu charakteristiku a velikost, nejaktuálnější nabídni přes `AskUserQuestion`. Vznikl z toho skill `/next` mimo životní cyklus. Platný stav drží `skills/next/SKILL.md`; tady je cesta k němu.

**Zdroje a řazení.** Čte `todo.md` (včetně parkovaných bodů a kol návrhu), `plan.md`, rozdělanou práci v gitu a místo v cyklu. Místo v cyklu se odvozuje z **artefaktů** (`requirements.md`, `architecture.md`, `plan.md`) a z `## Průchody životním cyklem`, protože zakládací kroky do *Průchodů* nepíšou. Ve worktree layoutu se všechno čte z hlavní větve (s remote `origin/main` po `git fetch`, bez něj lokální `main`) – pracovní adresář session bývá stará nebo cizí větev. Řadí: opuštěné větve → rozdělané tady → bez nesplněné závislosti → co odblokuje nejvíc → pořadí v `todo.md`. Nic nezapisuje.

**Práce ve větvích (dva pokyny uživatele v téže session).** Úkol ve větvi, nad kterou právě běží session v jiném okně, se **nenabízí** a vypíše se nahoře; úkol v **opuštěné** větvi se nabídne jako první, s příkazem `/resume <session_id>` té konverzace. Session, která běží – i obnovená jinde –, se k obnovení **nenabídne nikdy**. Položka se větvi přiřadí podle změn `todo.md`, `plan.md` a `done.md` ve větvi, podle řádku *Větev* u kola (jakmile větev existuje) a nakonec podle jména větve a commitů jako domněnka.

**Jak se pozná živá session:** skript `skills/next/sessions.py` čte registr `~/.claude/sessions/<pid>.json`, ověří živost procesu a větev bere z posledního záznamu transcriptu (`gitBranch`) – session ve worktree layoutu startuje v kořeni kontejneru, takže adresář procesu větev neprozradí. Nejistý výsledek (registr chybí, některý jeho záznam nejde přečíst, větev živé session nad projektem neznámá) se bere jako obsazenost všech větví projektu – nečitelný záznam může patřit běžící session, která by se jinak nabídla k obnovení. Obsazenost se počítá jen z session nad týmž projektem; stejně pojmenovaná větev v cizím repozitáři ji nezakládá. Nejistý výsledek tedy platí jako obsazená větev: nabídnutá obsazená větev stojí dvě session nad toutéž prací, nenabídnutá opuštěná jen řádek. Před předáním každé opuštěné větve – s konverzací k obnovení i bez ní – se kontrola pouští znovu, protože větev mohla být mezitím otevřena v jiném okně. Opuštěná je jen větev, ve které je práce (commity nebo neuložené změny); větev po sloučení bez práce se hlásí jako prázdná a nenabízí se. **Zamítnuto – živost podle stáří commitu nebo mtime worktree:** otevřená session může hodinu jen diskutovat, zapomenutá větev může mít commit z dneška. **Zamítnuto – pravidlo v textu místo skriptu:** formát registru není dokumentovaný, jeho změnu má zachytit test (`tests/test_next.py`), ne tiše špatná nabídka. **Zamítnuto – přepnout se do opuštěné session sám:** `/resume` je příkaz uživatele, model ho spustit neumí; skill dá přesné znění a skončí.

**Rychlost: sběr jedním skriptem, bez načítání norem, kompaktní výpis.** První ostrý běh nad reálným projektem trval 1:08 – na „rychlý návrh, do čeho se vrhnout“ neúnosně. Čas nežral git, ale čekání na model: skill ho vedl přes desítky volání (`git diff` a `git log` pro každou větev, čtení každého souboru, `sessions.py`) a pokaždé si načítal `STRUCTURE.md`, `PREFLIGHT.md` a `LIFECYCLE.md`, tedy stovky řádků, ze kterých potřeboval pět faktů. **Rozhodnutí:** `skills/next/collect.py` posbírá všechno mechanické jedním během (asi 1,4 s včetně `git fetch`) a rozhodne i obsazenost větví; tvar bloku kola a sekcí zná sám a rámeček cyklu čte z `RULES.md`. Model dělá jen úsudek – popis, velikost, co je na stole nejvíc. Výpis je jeden řádek na položku, podrobnosti nese až `description` v `AskUserQuestion`, protože generování textu je nejpomalejší část a totéž dvakrát je čekání navíc. **Zamítnuto – slabší model přes subagenta:** start agenta a předání výsledku přidají čas a velikost úkolu je úsudek, který levný model odhadne hůř. **Zamítnuto – vynechat `git fetch`:** stojí asi vteřinu a bez něj se nabízejí už sloučená kola. **Zamítnuto – výpis úplně vypustit a nechat jen otázku:** přehled celé fronty byl jeden z původních požadavků. **Zamítnuto – přečíst normy jen zčásti:** pořád by to byla volání navíc a znalost by se rozcházela s normou tiše; ve skriptu ji aspoň hlídá test.

**Nabídka kol ze `/specify round` bez jména se přesunula do `/next`**, sekce *Kola návrhu*; `/specify` volá `/next Kola návrhu`. (Od 20. 9. 2026 to dělá `/architect` a bez jména režimu – kola se rozdělením přestěhovala k němu.) Byla to zúžená podoba téže fronty a dvě kopie pravidel by se rozešly. **Zúžení je volný text, ne klíčové slovo** – první verze měla `/next kola` s pevným významem, což se chovalo jako nepojmenovaný český režim mimo `argument-hint` (proti `skills/SKILLS.md`, *Hlavička*). **Proč ne sdílený soubor podle `SKILLS.md`, *Číslování a názvosloví*:** to pravidlo platí, když obsah **potřebují** dva skilly; `/specify` si nabídku celou přenechává a na sekci odkazuje jménem. **Zamítnuto – nechat nabídku kol ve `/specify` a v `/next` jen odkázat:** nabídka by žila na dvou místech.

**Backlog se jen vypíše při prázdné a nezúžené frontě**, odděleně jako nezávazné nápady – `STRUCTURE.md` ho nevede jako frontu a *Nerozhoduj potichu nad rámec zadání* říká, že „pokračuj“ neznamená „najdi si práci“.

**Po výběru se skill do úkolu rovnou pustí**, má-li úkol skill, vyvolá ho. **Zamítnuto – jen doporučit příkaz a skončit:** o odpověď pomalejší bez přínosu, výběr je sám potvrzením.

**Srovnávací běh bez skillu** (`claude -p "s čím můžeme pokračovat?"` v jednom z projektů): obsah dobrý, ale bez velikosti úkolů, bez pohledu do gitu, bez spouštěče a s otázkou v textu místo `AskUserQuestion`. Skill vznikl a dvakrát prošel čtenářem bez kontextu; jeho nálezy (nabídnutí rozběhnutého kola či sešití podruhé, chybějící `git fetch`, zdroj souborů ve worktree layoutu) jsou zapracované.

### 2026-09-17 – Jazyk identifikátorů hlídá pravidlo, ne test

`~/.claude/RULES.md`, *Jazyk*, říkal jedinou větou, že se kód píše anglicky. Přesto měly všechny testy v `~/.claude/tests/` české názvy tříd, metod i proměnných, `verify.sh` české proměnné a schémata výstupu agentů ve skillech české klíče. Pravidlo se proto rozepsalo: **anglicky je každý identifikátor** včetně testů, klíčů ve schématech a zástupných symbolů v ukázkách příkazů; **česky zůstává, co čte člověk** – komentáře, docstringy, hlášky, zprávy v assertech, testovací data s českým obsahem. `coding.md`, *Naming v kódu*, na to jen odkazuje.

**Zástupné symboly v příkazech, cestách a jménech souborů jsou anglicky** (`<project>`, ne `<projekt>`). Stojí uvnitř příkazu, který se kopíruje, a `<projekt>.migrating` vedle sebe míchal oba jazyky – přesně tu nekonzistenci, kvůli které se to řešilo. **Místo k doplnění v šabloně českého textu** (`<důvod>`, `<počet>`) naopak zůstává česky: doplní se do věty pro člověka, ne do příkazu. **Stejně česky zůstávají argumenty slash příkazů** v `argument-hint` a v ukázkách volání skillu (`/invoicing recover <klient>`) – doplněno 17. 9. 2026 při `/consistency full`, kde se ukázalo, že přejmenování je u `/invoicing` a `/depot` převedlo a u ostatních skillů ne. Jsou to popisy v nápovědě, které čte člověk. **Kritérium je, kdo řádek píše:** argument za `/skill` píše uživatel v rozhraní, kdežto zástupný symbol v příkazu shellu nebo v cestě doplňuje Claude do kódu – ten je anglicky. Režimy skillu – pojmenované chování, které tělo popisuje jako režim (`full`, `preview`) – jsou naopak anglicky podle `~/.claude/skills/SKILLS.md`, *Hlavička*; o tom, co je režim, nerozhoduje pozice v hintu. **Hodnoty v datech** (doplněno týž den při `/cleanup`, na podnět čtenáře bez kontextu): hodnota, kterou vyrábí a podle které rozhoduje stroj – kód nebo model –, je identifikátor a píše se anglicky (`merge_pending`); hodnota ze slovníku, který se vypisuje člověku doslova (`KRITICKÉ`, `vysoká`), zůstává česky. **Zamítnuto:** převést i škálu závažnosti a jistoty do angličtiny – zásah napříč všemi skilly s nálezy, `SEVERITY.md` a zapsanými záznamy `## Review`, a uživateli by se pak musela překládat zpátky.

**Mechanická kontrola vědomě není.** Zvažovaly se dvě: test, který rozloží identifikátory na slova a porovná je s anglickým slovníkem (chytne i `vady` bez diakritiky, ale potřebuje seznam povolených zkratek, který se bude doplňovat), a test jen na diakritiku (bez falešných poplachů, ale většinu skutečných případů nechytí). Honza rozhodl, že zůstane jen pravidlo. **Čím se to nahrazuje:** rozepsaným pravidlem v souboru, který se importuje do každé session, a revizí. Vrátí-li se české identifikátory znovu, je to důvod otevřít slovníkový test znovu – samotná věta v pravidlech nestačila už jednou: 14. 9. 2026 vznikla česká funkce v session, kde byl `RULES.md` rozbalený celý a kde se o pár odstavců výš dodržel anglický `git_ro()`.

**Rozsah převodu mimo `~/.claude` a `~/Dev/context`: jen čtyři projekty.** Hrubý sken verzovaného kódu v `~/Dev/*` (identifikátory rozložené na slova proti anglickému slovníku, 17. 9. 2026) vytipoval kandidáty ve zhruba patnácti projektech. Honza rozhodl, že se převod zapíše jen do pěti z nich; 17. 9. 2026 byl ve všech kromě jednoho odpracovaný. **Ten jeden z rozsahu vypadl** (17. 9. 2026): převod tam kromě kódu přejmenovával i tisíce datových souborů a veřejné cesty webu, rozdělaná práce se zastavila, vrátila na poslední commit a úkol se odebral – Honza rozhodl, že se tam převod vůbec řešit nebude. **Ostatní projekty se vědomě neřeší** a nikde se nevedou: u většiny sken chytal hlavně jména značek a cizích systémů (`Fakturoid`, `Seznam`, `Zbozi`), text v docstrinzích nebo jiný jazyk, u zbytku šlo o jednotlivá jména. Pravidlo v `RULES.md` pro ně dál platí – projeví se při další práci v nich, ne plošným převodem.

### 2026-09-17 – Co rozhodl `/consistency full` po převodu identifikátorů

Audit nad `~/.claude` (28 nálezů, průchod v `done.md`) předložil sedm sporných nálezů. Pět rozhodnutí je níž, šesté (argumenty slash příkazů) v záznamu *Jazyk identifikátorů hlídá pravidlo, ne test*; sedmý nález – rozdílný argument `/depot` v hlavičce a README – se vyřešil jako následek toho šestého a vlastní rozhodnutí nemá.

- **`cwd` validuje `verify.sh --contract`, ne workflow.** Pomlčku nevypíše, cestu ven z projektu nebo do neexistujícího adresáře odmítne chybou – stejně jako hook. **Zamítnuto:** opravit jen `.github/workflows/verify.yml`. Validace by žila na dvou místech a rozešla by se znovu; přesně takhle vznikla původní vada (hook znal pomlčku a zakázané cesty, CI ne).
- **Jméno klíče kontraktu čte `verify.sh` jedním vzorem `KEY_RE`, bez dvojtečky.** **Zamítnuto:** povolit dvojtečku všude (`test:unit`). Změnila by se sada spouštěných kroků i otisk souhlasu a CI by ji musela znát; dnes ji nepovolovalo nic, co doopravdy spouští, jen výpisy ke schválení – a ty ukazovaly krok, který se nikdy nespustí.
- **Doložení nálezu smí nést jiné pole než `basis`** (`~/.claude/skills/SKILLS.md`, *Ověřovací vrstva*): `/attack` reprodukce, `/consistency` lokace, a oba to u schématu říkají. **Zamítnuto:** doplnit `basis` do obou schémat. Opakovalo by reprodukci nebo lokace a agent by ho vyplnil výplní.
- **`/next` vrací `branch_state: merge_pending`**, když blok kola ve větvi chybí. **Zamítnuto:** nechat českou větu „zapsáno ve větvi, čeká na sloučení“ a v `SKILL.md` ji prohlásit za hlášku. Pole jinak nese data z `todo.md` a model se podle něj rozhoduje; vyrobená hodnota má být token.
- **Pomocné metody testů se jmenují podle toho, co spouštějí** (`run_verify` × `run_commit_msg_hook`, `commit_contract` / `write_contract` / `list_contract`); nevyužitý parametr `stdin_data` zmizel. **Zamítnuto:** rozlišit jen jména, která se kříží mezi soubory. `contract()` se čtyřmi významy by zůstalo.

**Vědomá mezera u `/transcript`** (starý log po převodu značek) je zapsaná u skillu, v `~/.claude/skills/transcript/SKILL.md`, *Průběžný stav – NEspouštěj automaticky*.

### 2026-09-17 – Skill `/diagram`: mapa datového modelu jako artefakt, ne diagram v repozitáři

Vytěžený ze session nad rezervačním systémem, kde se z `docs/model.md` a `docs/transitions.md` ručně postavila interaktivní stránka – jádro ER, celé schéma s detailem tabulky, klikací stavový prostor, osy – a pak se překreslila na jinou větev po přestavbě objednávky nad partiemi. Honza chce totéž umět zavolat v kterémkoliv projektu; skill je zatím v podobě té session a bude se ladit.

**Zamítnuto: Mermaid do `docs/`.** Diagram v repozitáři je druhá kopie modelu vedle textu a rozejde se s ním, dokud se model hýbe. Otevřít se to dá, až se model ustálí – a pak jako malé výřezy hlídané testem, ne jako jeden velký diagram. Do té doby skill do projektu nezapisuje nic.

**Artefakt se hledá podle stálého názvu** `Mapa modelu <projekt>`, jinak se skill zeptá. **Zamítnuto:** zapsat odkaz do projektového `CLAUDE.md` – spolehlivější, ale skill by přestal být čistě čtecí a sahal do repozitáře kvůli pohodlí. **Zamítnuto:** ptát se pokaždé.

**Data se tahají jednorázovým skriptem ve scratchpadu, ne skriptem ve skillu.** Formát dokumentace modelu je v každém projektu jiný a obecný parser by se přemlouval déle, než se napíše nový. **Vědomá mez:** schéma z migrací ani ORM se nečte – projekt bez modelu v dokumentaci dostane odpověď, že není z čeho kreslit.

**Co ukázal srovnávací běh bez skillu** (a proto to skill hlídá výslovně): agent sám od sebe vytěžil data skriptem a nic v projektu nezměnil, ale obecný zápis přechodu rozepsal odhadem do konkrétních hran (`restore*` do všech stavů, `unpayCard` do všech `*_PAID`) a jen je označil „nejisté“, smazání nakreslil jako uzel mezi stavy, cizí klíče odvodil z názvů sloupců a ve výsledku nechal znaky závorek ze zdroje. Že uživatel mluvil o větvi, která mezitím byla sloučená, řekl až na konci.

**Co ukázal tlakový běh se skillem:** agent pod tlakem „rozepiš obecné hrany, smazání dej jako uzel, bez poznámek“ kreslil jen hrany doložené citací z katalogu a smazání nechal jako osu. Zápis diagramu do `docs/` a commit by na výslovný pokyn uživatele udělal, ale s varováním – pokyn uživatele má před skillem přednost. Vyvolání popisem situace se měřilo přes `claude -p` na 6 pozitivních a 6 negativních promptech po dvou bězích: 24 z 24 správně.

### 2026-09-08 – `deny` v `settings.json` je ochrana proti omylu, ne proti obejití

`/review full` nad konfigurační vrstvou našel třídu děr, kde `deny` a `ask` nedosáhnou na cestu, kterou si vynutí interpret nebo správce balíčků. **Tři z nich zůstaly vědomě otevřené** – jediná účinná oprava by přesunula běžné nástroje do `ask` a odklikávala by se u každého spuštění, takže by ji první kolize vypnula.

**Poučení, které z toho platí obecně:** `deny` je ochrana proti ukliknutí, ne proti cílenému obejití. Vrstva, která se tváří jako hranice a přitom jí není, je horší než žádná, protože se na ni někdo spolehne. Skutečnou hranici drží jen to, co si model nemůže odsouhlasit sám – souhlas vydaný z terminálu, ověření cíle, potvrzovací dialog (`RULES.md`, *Přednost pravidel*).

**Konkrétní cesty, kterými to jde obejít, tady nestojí** a je to záměr: repozitář je veřejný a popis funkčního obchvatu vlastní ochrany je návod, ne poznámka. Drží je `~/Dev/context/decisions.md`, sekce `## Claude`.

### 2026-09-18 – Souhlas s průběžnou kontrolou platí na repozitář, ne na obsah příkazů, a dialog to teď říká

Nález `/review full` nad rezervačním systémem (specialista na agentní infrastrukturu): `Stop` hook po každé odpovědi vykoná `test` z kontraktu, což u toho projektu znamená naimportovat a spustit všechny `tests/test_*.py`. Souhlas se přitom otiskuje výhradně z řádků `- klíč: příkaz`, takže obsah těch souborů do něj nevstupuje. **Kdo dostane commit do `tests/` – smerguje PR, předá větev, přesvědčí agenta –, dostane spuštění svého kódu s právy uživatele po první další odpovědi, bez promptu a bez nového souhlasu.** Sedí to vedle `.env` s přístupovými údaji, které deny pravidla chrání proti nástroji `Read`, ne proti procesu, který si hook spustí sám.

**Mez zůstává, protože ji nejde zavřít bez falešných poplachů.** Otisk z celé sekce kontraktu se 14. 9. 2026 vyzkoušel a zrušil – vyžádal si nové odsouhlasení po každé editaci komentáře. Hashovat spouštěný strom (`tests/`) je totéž, jen častěji: testy se během práce mění pořád. A nešlo by to na `tests/` omezit, protože `npm test` vykoná, co je v `package.json`; důsledně vzato by se musel hashovat celý repozitář a souhlas by se vydával několikrát denně. **Falešný poplach je u vynucovací vrstvy horší směr selhání než propuštěná chyba** – vede k jejímu vypnutí, a pak nehlídá nic.

**Změnilo se proto jediné: mez už není skrytá v okamžiku, kdy se rozhoduje.** Dialog `--allow` dosud mluvil o **cizím naklonovaném** repozitáři („do cizího souhlas nedávej“), ale ne o vlastním repozitáři **po cizím commitu** – a to je právě ten případ z nálezu. Nově říká, že se souhlas vydává jednou, kdežto soubory, které schválené příkazy vykonají, se mění dál a nový souhlas si nevyžádají, a že u repozitáře s cizími commity je tohle ta hlavní otázka. Hlídá to `tests/test_verify.py`, `test_allow_says_repository_content_can_change_later`.

**Zamítnuto – hlásit commity od jiného autora od vydání souhlasu.** Silnější, ale v repozitáři s víc přispěvateli by to šumělo pokaždé, a hlášení, které svítí vždycky, se přestane číst.

**Dotčené projekty:** všechny, které mají vydaný souhlas. Nic se jim nemění – změna je jen v textu dialogu při vydávání nového.

### 2026-09-18 – Plugin `gitkraken-hooks` vypnutý: běžel naprázdno

Nález `/review full` nad rezervačním systémem ho našel znovu poté, co umlčení z 8. 9. 2026 vypršelo změnou `settings.json`. Tehdy se vypořádal jako vědomě přijaté riziko: odesílání dat mimo stroj se neprokázalo, zbylo „lokální proces téhož uživatele vidí obsah session“.

**Rozhodlo měření, ne ta úvaha.** V `gk_cli.log` je **164× „blocking broadcast returned no decision“**, poslední záznamy z téhož dne, a **nula registrovaných agentů**. Plugin tedy při každé žádosti o svolení volal binárku, ta rozeslala obsah session a nikdo ji neposlouchal – od prvního měření 8. 9. (tehdy 104×) dodnes. K čemu je: posílá GitKraken Desktopu a GitLensu živý přehled o tom, co Claude Code dělá, a umožňuje z jejich UI schvalovat tool cally. **Honza GitKraken používá jen na vizualizaci větví**, takže ten přehled nikde neotevírá.

**Cena proti tomu byla reálná:** hook na 21 událostech, binárka na symlinku do samoaktualizovaného adresáře (`AUTO_UPDATE=true`), tedy měnící se obsah bez schválení, a `PermissionRequest` s `--blocking` a `timeout: 86400` – nedostupné `gk` drží žádost o svolení 24 hodin.

**Umlčení se tím nemá čím obnovit a smazalo se.** Nález nezmizel jako přijatý, ale jako neexistující: co není zapnuté, nemá co hlásit. Vrátit to jde jedním řádkem, kdyby se sledování session z GitKrakenu jednou hodilo.

**Zamítnuto – nechat zapnuté a jen srazit timeout.** Zavřelo by to provozní půlku (čekání na svolení), ale platilo by se za funkci, kterou nikdo nepoužívá.

### 2026-09-08 – Dvě podmínky pro `PostToolUse` hook

Dnešní `/review full` zrušil oba `PostToolUse` hooky v `~/.claude/settings.json` (`npx tsc --noEmit` po editaci `.ts`, `py_compile` po editaci `.py`). Zapisuje se, **za jakých podmínek smí `PostToolUse` hook existovat** – bez toho je prázdné místo k nerozeznání od opomenutí a příště se hook přidá zpátky se stejnými vadami.

**Podmínka 1 – nesmí maskovat návratový kód.** Oba končily `; true`, takže vracely vždy nulu. Dokumentace k hookům přitom uvádí, že `PostToolUse` při rc=0 stdout modelu ani do transkriptu neukáže – jde jen do debug logu. Kontrola tedy chybu našla, spolkla ji a nikdo se nic nedozvěděl; platilo se za ni až 30 s po každé editaci. Chce-li hook něco sdělit, musí skončit `exit 2` se stručným stderr (blokovat stejně neumí, takže obava z otravnosti je bezpředmětná).

**Podmínka 2 – nesmí spouštět binárku z auditovaného repozitáře.** `npx` bere `tsc` primárně z `./node_modules/.bin`, tedy z klonovaného projektu. Hooky běží mimo permission systém a tenhle žádnou obdobu souhlasu `verify.sh --allow` neměl: stačilo naklonovat cizí repozitář a upravit v něm libovolný `.ts`. Reprodukováno – podvržená binárka se spustila s právy uživatele bez jediného dotazu.

**Není to zákaz celé události.** `PostToolUse` hook, který obě podmínky splní – volá absolutní cestu k důvěryhodnému nástroji a výsledek doopravdy hlásí –, je v pořádku. Dnešní dva neplnily ani jednu.

**Vědomá mezera, kterou to otevírá:** v repozitáři **bez** souhlasu `verify.sh` teď nekontroluje nic. Je to přijaté: právě tam byl hook nejnebezpečnější, a kontrola, jejíž výsledek nikdo nevidí, stejně nic nekontrolovala.

### 2026-09-10 – Skill `/audit`: audit cizího webu proti doménové znalosti

Vznikl skill `/audit`, který zaudituje **cizí běžící web** v zadané oblasti proti auditnímu postupu a katalogu nálezů uloženým v příslušné doméně `~/Dev/context/`. Sám nenese žádnou doménovou znalost – je to dirigent.

**Proč nový skill a ne režim `/review`:** oba měří proti týmž doménovým standardům, ale liší se předmětem a všemi předpoklady. `/review` čte vlastní práci v repozitáři, má diff, kontrakt příkazů a specifikaci, proti které měří korektnost. `/audit` nemá ani jedno – má URL, exporty od klienta a přístupy do cizích účtů. Sloučení by znamenalo skill, jehož polovina fází v každém běhu neplatí.

**Režimy `full` (výchozí), `brief`, `audit`, `report`, `update`.** Fáze jsou pojmenované jako režimy, aby šla pustit jen ta část, která je potřeba – typicky přepsat výstupy bez nového sběru. **Zamítnuto `collect` pro první fázi:** v `/compose` už znamená posbírání hotových textů a tady by svádělo i na sběr nálezů. **Zamítnuto `intake`, `inputs`, `gather`, `create`** ve prospěch `brief` – v oboru zavedený termín přesně pro to, co klient před zakázkou dodá.

**Hranice na cizím webu se dělí na tři pásma podle jediné otázky: přežije následek zavření prohlížeče?** Volné je, co žije jen v relaci (košík, vyhledávání, filtry) – a je to chtěné, protože bez toho se měření neodchytí. Svolení pokaždé zvlášť vyžaduje, co splní aspoň jedno ze tří: vznikne trvalý záznam ke smazání, odejde zpráva člověku, sáhne to na cizí peníze či sklad. Nikdy se nedělá zásah do klientovy konfigurace a zkoušení zranitelností. **Zamítnut výčet konkrétních případů** („objednávky na dotaz, ostatní v pohodě“) – nešel by aplikovat na případ, který ve výčtu není.

**Třetí pásmo drží pořadí prací, ne zákaz nad uživatelem.** Tlakový scénář ukázal, že se skill na výslovné trvání uživatele k opravě v klientově GTM nakonec upsal – a je to podle `~/.claude/RULES.md`, *Přednost pravidel*, správně: pokyn uživatele stojí nad skillem a žádná věta v Markdownu ho nepřebije. Původní formulace „nikdy, a souhlas se na to neptá“ tedy slibovala tvrdost bez mechanismu. Přepsáno na důvod, který obstojí sám: auditor, který si vlastní nález rovnou opraví, ho už nemá jak vyvrátit, a opravou v produkci změní data, proti kterým měří zbytek auditu. Trvá-li uživatel na svém, oprava se provede a u dotčených nálezů se zapíše, že se ověřovaly až po zásahu.

**Ověřovatel má přístup k webu a nález vyvrací reprodukcí**, ne argumentací jako v `/review`. Je to dražší, ale u auditu se většina nálezů dá ověřit pozorováním a nález poslaný klientovi omylem stojí důvěru celé zakázky.

**Sběr dělá hlavní session jednou pro všechny**, specialisté nad ním pracují a smí si dozískat vlastní záložkou. Pět agentů stahujících totéž je pětkrát dražší, pětkrát rozdílné a pětkrát zatěžuje cizí web. Ověřeno, že to jde: nástroje `chrome-devtools` MCP mají `pageId` jako povinný parametr, takže sdílený výběr stránky neexistuje a záložky se nepřebíjejí.

**Audit a revize jsou dva pojmy, ne dvě jména téhož** – doména je dosud nerozlišovala a skill si tím vysloužil podezření z *jednoho termínu pro jednu věc*. Audit je projití stavu, pojmenování chyb a návrh základních fixů; revize je zakázka, do které audit vstupuje jako podklad a jejíž podstatou jsou navazující opravy, často až přestavba struktury, filozofie a scénářů. Z toho plyne i to, proč se ucelené vývojářské šablony v auditní zprávě nevyužijí v plné šíři – patří k revizi. Nejkratší test: **výstupem auditu je dokument, výstupem revize naimplementovaný web** (s dokumentací). Rozdíl zapsán do `analytics/audit.md`, *Audit není revize*; `/audit` dělá audit a v *Co skill nedělá* se proti revizi vymezuje.

**Režim `full` zůstává, i když v `/review` a `/consistency` znamená rozsah, kdežto tady úplnost.** V obou případech čte člověk „nezaříznutý běh“ a jiné jméno by tu podobnost jen zakrylo; k tomu má skill v těle napsané, jak se pozná režim od volného popisu zakázky.

**Vědomá mezera – auditní dráhu má dnes jen `analytics/`.** Nad doménou, která má jen checklist, skill poběží v omezeném režimu a nahlas to řekne; po auditu nabídne vytěžit nalezené zpátky do domény přes `/learn`. **Zamítnuto vyžadovat kontrakt domény** a běh jinak odmítnout – zablokovalo by to audity nad `web/` a `design/`, které se dají dělat proti checklistu, jen mělčeji.

### 2026-09-15 – Třetí stupeň závažnosti je NÍZKÉ, protože trojice musí stát na jedné ose

Vyšlo z konzistenčního auditu: `/audit` si vedl vlastní škálu *kritická / vážná / drobná* mimo `skills/SEVERITY.md`, přestože ten se prohlašuje za jedinou škálu pro všechny skilly, které hlásí nálezy. Příčina nebyla nedbalost, ale **vada původní trojice** KRITICKÉ / STŘEDNÍ / KOSMETICKÉ: míchala dvě osy – *kritické* je o naléhavosti, *kosmetické* o povaze nálezu. Na auditu cizího webu proto nesedla, protože „kosmetický nález“ tam nedává smysl, a skill si přirozeně zavedl vlastní.

**Zavržené varianty.** *Nechat KOSMETICKÉ a zapsat do `SEVERITY.md`, proč `/audit` stojí mimo* – legalizovalo by to dvě škály a tím i důvod, proč soubor vznikl. *DROBNÉ* – odmítnuto uživatelem; slovo hodnotí velikost práce, ne dopad. *VYSOKÉ / STŘEDNÍ / NÍZKÉ* – nejčistší jedna osa, ale nejvyšší stupeň by zněl jako další dílek škály, a přitom právě on spouští přísnější ověřování. *KRITICKÉ / STŘEDNÍ / OKRAJOVÉ* – „okrajové“ není ustálené a míchá osu podobně jako předtím.

Zvoleno **KRITICKÉ / STŘEDNÍ / NÍZKÉ**: celá trojice na ose závažnosti, „nález nízké závažnosti“ funguje u kódu, útoku, cizího webu i oponovaného dokumentu, a nejvyšší stupeň si nechává sílu poplachu. `/audit` ji přebírá s vlastním doménovým čtením, jak to dělá `/attack`.

**Cena, kterou to stálo, a poučení k ní.** Náhrada napříč osmnácti soubory se dělala hromadným `str.replace` a přepsala i slova mimo škálu – „drobná změna“ → „nízká změna“, „podrobné README“ → „ponízké README“. Grep by to nenašel, protože hledané slovo právě zmizelo; chytlo se to až čtením diffu (`~/.claude/RULES.md`, *Mazání ověř diffem, ne grepem*, platí i na náhradu). **Na přejmenování napříč projektem je `/replace`, ne ruční náhrada** – právě proto, že kontroluje tvary a hranice slov.

### 2026-09-15 – Norma skillů uznává blok předběžných podmínek, místo aby ho zakázala

Konzistenční audit hlásil, že „sekci navíc mezi *Co skill nedělá* a *Fází 0* mají dva skilly“. Měření ukázalo **14 z 22** – `Rozsah`, `Zásady pro celý průběh`, `Hranice`, `Kdy se pouští a kdy se přeskakuje`, `Tvrdá pravidla` a další. Vada tedy nebyla v těch skillech, ale v `skills/SKILLS.md`: šablona povinných sekcí ten prostor vůbec neznala, přestože ho používala většina.

**Zavržené varianty.** *Zakázat a obsah přesunout* – znamenalo by nacpat rozsah a hranice do `Co skill nedělá`, kam nepatří, nebo je odsunout za závěrečnou fázi mezi přílohy, kde by je nikdo nepřečetl včas. *Nechat normu mlčet* – stav, kdy čtrnáct skillů porušuje šablonu a nikdo neví, jestli je to chyba, nebo zvyk; každý další audit by to hlásil znovu.

Zvoleno: norma blok **uznává jako nepovinný** s kritériem **„sekce se vztahuje k víc než jedné fázi“**. Co platí pro jedinou fázi, patří do ní; co se čte jen někdy, je příloha za závěrem. Sekce, kterou norma nezná a všichni ji mají, není odchylka, ale mezera v normě.

**Důsledek, který si vyžádal další práci:** čtyři skilly (`/consistency`, `/release`, `/replace`, `/specify`) měly takovou sekci ještě **před** `Co skill nedělá` a musely se přeskládat. Přesun zanechal pozůstatky – osiřelý oddělovač v `/replace` a větu o kroku cyklu, která ve `/specify` zůstala viset na konci úvahy o dvou dokumentech, kam nepatří. Obojí našel až čtenář bez kontextu v `/cleanupu`, ne audit sám.


### 2026-09-15 – Subagenti se volají typy s vymezenými právy, ne slibem v zadání

Věta „nezapisuj do žádného souboru“ v zadání subagenta **nic nedrží** – je to text pro model, ne mechanismus. A `Explore`, na kterém dosud jely všechny čtecí panely, sice nemá `Edit` ani `Write`, ale **`Bash` má**, takže jím lze zapsat i commitnout. V projektu se zapnutým autocommitem z toho vznikne pushnutá změna, kterou nikdo neschválil.

Zavedeny dva typy v `~/.claude/agents/`: **`reader`** (`Read, Grep, Glob`) a **`researcher`** (týž plus `WebSearch` a `WebFetch`). Ani jeden nemá shell. Norma je v `skills/SKILLS.md`, *Model, effort a delegace*, a uplatnila se v pěti skillech; `/attack` a `/audit` zůstaly na typu s nástroji, protože útočník bez shellu nepošle požadavek a auditor bez prohlížeče neuvidí stránku.

**Zavržený `inspector` – typ se shellem omezeným na čtecí příkazy.** Původní záměr byly typy dva: čtenář a měřič. Měření to zrušilo: `tools: …, Bash(git log:*)` dá agentovi **plný** shell, `disallowedTools: Bash(date:*)` mu ho **sebere celý** a `claude -p --allowedTools "Bash(whoami:*)"` propustí i `date`. **Závorkový tvar neomezuje nikde**; funguje jen celé jméno nástroje. Typ, jehož jméno slibuje „čtecí shell“, by tedy byl vrstva bez vynucení – a to je horší než žádná, protože se jí věří.

**Zavrženo přidat webové nástroje rovnou `readeru`.** Nezapisují, takže by záruku neporušily, ale čtenář nad soukromými dokumenty by dostal přístup ven i tam, kde ho nepotřebuje. Proto druhý typ.

**Co se přitom ukázalo o dědění v zadáních.** Standardoví specialisté `/review` dědili z pracovních zkratkou „zbytek shodný s pracovním specialistou“ i odrážku o `evidence`, která žádá spuštěný příkaz – po přepnutí na `reader` si typ a zadání odporovaly. Vyříznuto výslovně. **Ta zkratka je past téže třídy jako *Rozsah pravidla se nešíří sám*** v `RULES.md`, jen obráceně: dědí neviditelně, takže změna u rodiče tiše změní dítě.

**Měřeno, ne odhadnuto,** a dvě věci z toho stojí za zapamatování: **výpověď agenta o vlastních nástrojích není doklad** (jeden běh hlásil sadu, která neodpovídala definici – spolehlivé je jen to, co mu volání nástroje projde), a **nový typ je vidět až v nové session**, protože registr se načítá při startu. Překlep v názvu naopak selže hlučně i s výčtem dostupných typů.

### 2026-09-17 – Skill `/scenarios`: vytěžení scénářů z konverzací stojí mimo životní cyklus

Kolo návrhu rozhodne, jak se má systém v nějaké situaci chovat, zapíše to do modelu nebo do katalogu přechodů – a scénář k té situaci nikdo nedopíše. Seznam scénářů pak vypadá úplně a není, takže se proti němu nedá ověřit, co nový návrh rozbil. Doloženo dvěma ručními běhy nad rezervačním systémem (15. a 17. 9. 2026): první přidal 42 + 23 + 11 scénářů ze 22 konverzací, druhý našel z 37 konverzací 1376 situací, z nichž 317 nemělo ve scénářích protějšek.

**Zařazeno mimo životní cyklus**, k `/ptydepe` a `/replace`. Zavržena varianta „krok za `/cleanup`“: ta by tvrdila, že se má pouštět pokaždé, kdežto zpětné vytěžení dává smysl jednou za čas, až se ukáže, že se scénáře rozešly. Vymezuje se proti `/cleanup` (ten bere **běžící** session a zapisuje dohody do všech souborů) a proti `/specify` (ten scénáře **zakládá** z rozhovoru se zadavatelem).

**Bez režimů.** Zavržena dvojice `since` / `full`: první běh nemá v `done.md` žádný záznam, takže z něj vyjde plný rozsah sám od sebe, a druhý pojem by nic nepřidal.

**Rozdělení práce je to podstatné a je stejné jako v `SESSION.md`:** agent dělá úplnost, hlavní session dělá zařazení. Agent spolehlivě pozná, že se o něčem mluvilo; nepozná, jestli je to situace člověka a jestli je táž věc v souboru pod jiným jménem. Proto se od něj žádá **doslovná citace s číslem řádku** – s ní se nález ověří grepem, bez ní jen přečtením celého transcriptu, tedy tou prací, kvůli které se agent posílal.

**Tři pasti, které oba běhy odhalily a které jsou ve skillu zapsané:**

- **Výstup nástroje se bere za nález.** Session začínající `/next` obsahuje vypsanou frontu z `todo.md`; agent z ní vyrobí desítky „naznačených situací“, které v projektu dávno jsou. Poznají se podle toho, že u všech stojí `rozhodnuto: nic`.
- **Rozsah se určí podle data změny souboru.** Transcript se dopisuje, takže datum ukazuje konec session, ne začátek – běh pak mine konverzaci, která začala před posledním vytěžením a skončila po něm. Čte se první časová značka z obsahu.
- **Souběžní agenti si přepíšou pomocné soubory.** Sdílejí jeden scratchpad a bez vlastního prefixu si vzájemně přebijí mezivýstupy; v běhu 17. 9. 2026 to nahlásili čtyři agenti nezávisle a jeden chvíli četl cizí transcript. Prefix a ověření obsahu jsou proto součástí zadání.

**Typ subagenta je výchozí, ne `reader` ani `Explore`, a je to vědomé.** Agent musí pouštět `jq` nad JSONL (tedy potřebuje shell) a zapsat dlouhý strukturovaný výstup do souboru (tedy potřebuje `Write`). `reader` nemá první, `Explore` druhé. Hranice se proto nepředstírá – zákaz zápisu do repozitáře projektu je v zadání jako pokyn a je to ve skillu napsané.

**Srovnávací běh se vědomě nedělal.** Místo něj stojí dva skutečné ostré běhy, ve kterých je zaznamenané, jak práce bez skillu selhala – to je silnější doklad než syntetický pokus.
### 2026-09-18 – Skill `/serviceaccount` konvenci nenese, jen ji čte

Skill provede založením service accountů pro strojový přístup ke klientským systémům. Vznikl proto, že se týž postup dělal ručně a nezapamatoval by se – hlavně kvůli tomu, že **ID service accountu je neměnné**, takže chyba v pojmenování se opravuje jedině novým účtem a novou žádostí u klienta.

**Konvence bydlí v `~/Dev/context/organizations/access.md`, ne ve skillu.** Norma `~/.claude/skills/SKILLS.md` znalost oboru do skillu nepouští a tady to má i praktický důvod: seznam systémů a úrovně oprávnění porostou, kdežto průběh skillu ne.

**Zavržené varianty:**

- **Konvenci nést ve skillu** – nejrychlejší, ale vznikl by druhý zdroj pravdy vedle zápisu v `todo.md` a ke konvenci by se nedostal nikdo kromě toho skillu.
- **Počkat na bezpečnostní doménu** z odložené položky o rámci pro klientská data – konvence by měla konečné místo, ale do té doby by se účty skládaly podle paměti, čemuž má skill právě bránit.
- **Nechat skill zakládat účty přes API** – zamítnuto, protože zakládání účtu i generování klíče je za uživatelovým přihlášením a skill by k tomu potřeboval credentials, tedy přesně to, co vrstva 1 toho rámce zakazuje.

**Ověřeno:** testy tvaru 241 z 241, vyvolání 4 ze 4 – dva pozitivní prompty skill vyvolaly, dva negativní ne, včetně near-missu se slovy z konvence. **Neověřené zůstaly tlakové scénáře:** skill zakazuje pokračovat s vymyšleným slugem a zapisovat evidenci před potvrzením, a jestli to pod tlakem drží, se neměřilo.

### 2026-09-19 – Systémové notifikace zůstávají na kanálu `iterm2`, mobilní push se vypíná

Notifikace „Claude is waiting for your input“ má titul „Alert“ a skutečnou zprávu až za prefixem „Session <jméno tabu> (claude) #1:“. Prefix i titul dopisuje iTerm2, ne Claude Code: kanál `iterm2` posílá `OSC 9`, který nese **jediný řetězec** a titul neumí. Doloženo tím, že holé `printf '\033]9;…\007'` do téhož terminálu vyrobí identický tvar.

**Rozhodnutí:** kanál zůstává `iterm2`, práh nečinnosti `messageIdleNotifThresholdMs` zůstává na výchozí minutě a vlastní `Notification` hook se nestaví. Oba přepínače mobilního push – `agentPushNotifEnabled` a `inputNeededNotifEnabled` – jdou na `false`.

**Meze iTerm2 3.7.2 doložené testem na živém terminálu** (ať se nezkoumají znovu):

- `OSC 777` (protokol ghostty) ani `OSC 99` (protokol kitty) iTerm2 **nezpracuje**. Kanály `ghostty` a `kitty` by tedy neznamenaly hezčí notifikaci, ale žádnou.
- Holý `BEL` pípne, ale systémovou notifikaci nevyrobí – volba profilu „Post notification“ na zvonek nereaguje. Kanál `terminal_bell` je proto čisté zhoršení a `iterm2_with_bell` přidá jen druhý zvuk k tomu, který už hraje macOS.

**Zavržené varianty:**

- **Vlastní hook s `terminal-notifier`** – jediná cesta k lepšímu textu, ale zisk je malý: bezcenný je jen titul „Alert“ a „(claude) #1“, kdežto jméno session v prefixu nese informaci, která session čeká. Za to vrstva navíc, kterou může přepsat reinstalace iTerm2 integrace, protože ta do `settings.json` sahá sama.
- **Zkrátit práh nečinnosti** – zamítl uživatel s odůvodněním, že při práci v jiném tabu je minuta právě ta doba, po které už vyrušení nevadí.
- **Nechat mobilní push zapnutý** – `agentPushNotifEnabled` dává modelu nástroj `PushNotification`, kterým smí vyrušit z vlastního rozhodnutí; výchozí hodnota je přitom `false`. Bez připojeného Remote Control stejně nic nedělá, takže zapnutý byl jen překvapením do budoucna. Ven při tom odchází pouze dvojice booleanů na `/api/claude_code/notification/preferences`, žádný obsah session.

**Nález k vypořádání jinde:** `~/.claude/STRUCTURE.md` žádá datum v prvním odstavci a ne v nadpisu, kdežto celý tenhle soubor má datum v nadpisu `###`. Zápis drží konvenci souboru; srovnat to je práce pro `/consistency`, ne pro jeden zápis.

### 2026-09-20 – Životní cyklus se dělí na osu a kontroly v mezerách

**Problém:** cyklus byl jedna číslovaná řada kroků a ta předstírala, že každý krok spouští ten předchozí. Platilo to zhruba u poloviny; `/cleanup`, `/consistency`, `/discovery` a `/project` čekaly na stav, ne na předchůdce. `/cleanup` si v `LIFECYCLE.md` dokonce sám odporoval – stálo o něm „poslední krok uzavírání, **ne životního cyklu**“ a zároveň měl v seznamu číslo 9.

**Rozhodnutí (navrhl uživatel):** kroky mají dvě různé role a patří do dvou vrstev.

- **Osa – kroky, které tvoří:** `/project` → `/discovery` → `/specify` → `/architect` → `/breakdown` → `/implement` → `/release`. Vyrobí soubor, kód nebo nasazení a čekají na výstup předchozího.
- **Kontroly – kroky, které měří:** `/oponent`, `/consolidate`, `/review`, `/consistency`, `/attack`, `/cleanup`. Nic nepřidávají; **nejsou body v řadě, ale vrstva mezi nimi**, a proto se tentýž smí objevit ve víc mezerách.

Co smí stát v které mezeře a v jakém pořadí, drží tabulka v `~/.claude/skills/LIFECYCLE.md`. **Číslování kroků zaniklo úplně**, stejně jako dělení na zakládání/uzavírání/nasazení.

**Proč je to lepší:** zmizela potřeba vysvětlovat u každého kroku zvlášť, proč se pouští mimo řadu. Dřívější pokus to řešil tabulkou tří druhů spouštěčů (pozice / stav projektu / stav session); ta byla správná, ale popisovala důsledek místo příčiny. Příčina je, že kontrolní krok není bod.

**Zamítnuto:** ponechat jednu řadu a doplnit u každého kroku jen řádek *Spouštěč* – stálo to půl hodiny a skončilo tím, že polovina čísel dál nic neznamenala.

### 2026-09-20 – `/specify` se dělí na `/specify` a `/architect`

**Rozhodnutí:** jeden skill, který vyráběl `requirements.md` i `architecture.md`, se dělí na dva kroky osy.

**Důvod:** oponovat zadání má smysl **dřív**, než se podle něj postaví řešení. Dokud obojí vznikalo v jednom kroku, `/oponent` dostal obě vrstvy naráz a nemohl říct „tohle zadání je špatně“ ve chvíli, kdy ta informace ještě něco změní.

**Dělení je na vrstvě, ne uvnitř kol.** Požadavky se sepíšou **jednou na začátku**; návrh řešení vzniká **po tematických kolech**. Kolo o platební bráně řeší osy, guardy i přechody naráz, protože je to jedno téma – rozdělit ho na dvě poloviny by znamenalo dvakrát načítat týž kontext. Nejsou to tedy symetrické kroky se stejnou mechanikou.

**Jméno `/architect` je záměrně činnost, ne výsledek**, protože krok vyrábí **sadu** dokumentů a `architecture.md` je jen její páteř; jméno podle toho souboru by pojmenovávalo část za celek.

**Zamítnutá jména a proč:**

- **`/design`** – oborově nejzavedenější (superpowers své fázi říká „design doc“), ale **koliduje s vestavěným příkazem Claude Code** `/design`, `/design-sync`, `/design-login`. Navíc `~/Dev/context/design/` je doména vizuální tvorby.
- **`/architecture`** – uživatelova první volba; padla, když se ukázalo, že krok vyrábí sadu a ne jeden soubor.
- **`/solution`** – protějšek českého „návrh řešení“, ale vágní: řešení může být cokoliv.
- **`/specification`** (s ponecháním `/specify` návrhu) – nejdelší jméno v sadě a pojmenovávalo by dokument, který se jmenuje `requirements.md`.
- **`/requirements` + `/architecture`** – návrh stál na principu „skill nese jméno výstupu“; **uživatel ho vyvrátil** protipříkladem `/breakdown` → `breakdown.md`, což by bylo horší než `plan.md`. Princip tedy neplatí: soubory se jmenují podle otázky, na kterou odpovídají, skilly podle práce, kterou dělají.
- **`/architect`, `/blueprint`, `/shape`, `/decide`** – zvažovány; `/architect` vyhrál jako jediné volné jméno, které pojmenovává práci.

**Nepřejmenovává se:** `requirements.md` ani `plan.md`. Jsou pojmenované podle obsahu a `specification.md` by z trojice vybočilo.

### 2026-09-20 – Návrh řešení je sada dokumentů, ne jeden soubor

**Rozhodnutí:** `architecture.md` je **páteř** návrhu, ne celý návrh. K ní podle potřeby `model.md` (data a stavy), `transitions.md` (operace), `rules.md` (zásady domény) a tematické dokumenty kol.

**Důvod:** požadavky jsou **seznam** a vejdou se do jednoho souboru; návrh je **soustava, ve které se věci navzájem omezují**, a tu nejde popsat lineárně. Každý dokument je **řez toutéž věcí z jiného úhlu**, takže táž funkce je ve víc z nich – jednou jako osa, jednou jako přechod, jednou jako celý okruh. Jsou to dvě nezávislé osy a jejich průnik se neskládá (`RULES.md`, *Jednoduchost před úplností*).

**Pravidlo proti hromadě:** nový dokument vzniká, když drží **jiný řez** – ne když je ten stávající dlouhý. Kontrolní otázka: *odpovídá na otázku, na kterou žádný jiný neodpovídá?*

**Doklad:** rezervační systém má v `docs/` 27 452 řádků; jediný `architecture.md` by z nich držel přes dvacet tisíc.

**Vedlejší nález:** `STRUCTURE.md` mluvila o „návrhu řešení“, ale soubor se jmenuje `architecture.md` – dvě jména pro jednu věc, jen jedno česky a druhé anglicky. Opraveno.

### 2026-09-20 – `/review` stojí za každým krokem osy, který vyrobil artefakt

**Problém:** první verze tabulky mezer měla `/review` jen za `/implement`, protože vznikala s projektem s kódem před očima. Uživatel na to upozornil otázkou, proč jsme ho tedy nad rezervacemi pouštěli v návrhové fázi.

**Rozhodnutí:** `/review` patří do mezery za **každým** krokem osy, který vyrobil měřitelný artefakt – tedy i za `/specify`, `/architect` a `/breakdown`. Zapsáno jako princip, ne jako doplnění výčtu. **Výjimkou je `/project`**, který si svůj artefakt měří sám vlastní revizní fází.

**Doklad:** `/review full` nad rezervacemi, které nemají řádku kódu, vrátil 177 nálezů a velká část byly návrhové díry.

**Pořadí uvnitř mezery:** `/review` jde **první**, protože jeho opravy mění text, nad kterým pracují ostatní; `/consistency` po něm; `/cleanup` vždy poslední.

### 2026-09-20 – Rozdíl mezi `/review` a `/oponent` nad obsahovým projektem

Otázka uživatele, kterou stojí za to mít zapsanou, protože se jinak bude odvozovat znovu:

**`/review` má měřítko v souboru, `/oponent` žádné nemá.**

- `/review` měří hotovou práci **proti předpisu, který existuje jako dokument**. Nález zní „porušuje pravidlo X ze standardu Y“ a dá se vyvrátit ukázáním na to pravidlo. Jeho **specialisté** (korektnost, bezpečnost, data a stavy, provoz a chyby, testy, agentní infrastruktura) se zapínají **jen na kód**; nad obsahovým projektem se zapnou pouze **doménové sady** z `~/Dev/context/`.
- `/oponent` žádný předpis nemá a **posuzuje samotný obsah**. Nález zní „nedává to smysl“ nebo „chybí tu odpověď“ a vyvrátit se dá jen argumentem.

**Proč `/review` u rezervací našel návrhové díry:** nejsou to čistě obsahový projekt, ale dokumentace popisující aplikaci, takže se zapnuly sady `coding/coding.md`, `coding/architecture.md` a `web/admin.md`. Nález *„guard posílá admina udělat něco, co neexistuje“* je porušení konkrétního pravidla, ne oponentura.

**Praktický důsledek:** u projektu, ke kterému žádný relevantní standard v `~/Dev/context/` neexistuje, je `/review` skoro prázdný a má se přeskočit. `/oponent` funguje vždycky.

### 2026-09-20 – Vznikl krok `/consolidate` na návrhový dluh z postupného záplatování

**Problém, který ho vyvolal:** návrh vzniká po kolech a v každém se ukáže další kombinace, na kterou se přidá sloupec nebo hodnota výčtu. Každý ten krok je ve své chvíli správný; dohromady z nich vznikne řešení, které by při znalosti všech případů předem šlo nahradit jedním jednodušším. **Žádný dosavadní krok to nenajde:** `/review` měří proti specifikaci, jenže dluh je v samotné specifikaci; `/consistency` se ptá, jestli si projekt sedí sám se sebou – a takový dluh je dokonale konzistentní, protože každá záplata se poctivě zanesla všude; `/oponent` posuzuje dokument, jak stojí dnes, a nemá odkud vědět, že tři sousední mechanismy vznikly ve třech týdnech ze tří podnětů.

**Rozhodnutí:** nový kontrolní krok, který se ptá **„bylo by to dnes navržené jinak?“** – a odpověď „ano“ přitom vadu neznamená. **Jako jediný krok cyklu čte historii rozhodnutí**, ne dnešní stav: kroniku z `decisions.md`, `done.md` a z git logu.

**Čtyři lovné vzory, po kterých jde adresně** (vyjmenoval uživatel): přetížená osa (poznávacím znamením je, že se každý guard ptá jen na jinou podmnožinu hodnot); táž situace řešená pokaždé jinak; řetěz lepení, kde se má dostopovat na **první článek**; slepá místa, do kterých model narazí opakovaně.

**Dvě pravidla, která mu dávají smysl:**

- **„Uživatel to zamítl“ není zeď.** Rozhodnutí vzniklo v tehdejším kontextu a ten se mohl změnit – platí to i pro rozhodnutí uživatele. Podmínkou je pojmenovat, **co se od té doby změnilo**.
- **Ověřovatel se na dřívější zamítnutí odvolávat nesmí.** Musí doložit, co konkrétně se rozbije. Doloženo v pilotním běhu, kde ověřovatel argumentoval větou „to je přesně ta varianta, kterou §125 zamítlo“ a bod se udržel jen proto, že k němu vedle toho vypsal šest skutečných čtenářů.

**Hranice:** relativizují se **řešení, ne zadání**. Rozhodnutí o tom, co se má dělat, je pro krok vstup – jinak by z něj byl `/oponent` s právem měnit zadání.

**Ověřuje se dvojmo a obě zkoušky jsou blokující:** pokrývá nové řešení všechno, co dnešní, i tam, kde to dnešek zvládá nedokonale? A je to opravdu zlepšení, ne výměna jednoho hacku za jiný? Druhá zkouška je ta, na kterou se zapomíná.

**„Nic velkého k přepsání“ je platný výsledek.** V pilotu (rezervační systém, platební brána) padly **dva ze dvou** velkých návrhů a jako vedlejší produkt ověřování vypadly dvě skutečné vady. Bez téhle věty by se ze skillu stal stroj na návrhy, které projdou, protože je nikdo nezkusil vyvrátit.

**Zamítnuto – nechat to jako hledisko `/oponent`.** Hlediska se vybírají podle vlastnosti dokumentu a posuzují hotový text; tenhle krok potřebuje historii a vrací návrh řešení, ne nález. **Zamítnuto – pouštět po každé featuře:** je drahý a jeho nález je vždycky velký přepis.

**Zadání skillu i to, co k jeho napsání zbývá, drží `todo.md`.** Rozbor pilotu je v rezervačním systému, `docs/done.md` a `docs/decisions.md` §133 a §134.


### 2026-09-20 – `/architect` vznikl a nemá režimy

**Rozhodnutí:** `/specify` se rozdělil na dva skilly. `/specify` zůstal **jeden běh bez režimů** a vyrábí `requirements.md` plus produktové podklady; `/architect` dostal návrh řešení jako **sadu dokumentů** a celou mechaniku tematických kol. Zdůvodnění dělení drží zápis *`/specify` se dělí na `/specify` a `/architect`* výš; tohle je záznam o jeho provedení a o třech rozhodnutích, která při něm padla.

**`/architect` nemá režimy a orientuje se sám.** Zděděné `auto`, `create`, `round` a `close` se zrušily celé. Důvod: `auto` byl výchozí a jeho tabulka rozhodovala **čistě ze stavu projektu** – jméno kola v argumentu, větev, ve které session stojí, bloky v `todo.md`, záznamy v `done.md`. Všechny čtyři větve jsou z toho stavu odvoditelné, takže zbylá tři jména pojmenovávala **vnitřní fáze, ne volbu uživatele**, a `SKILLS.md`, *Hlavička*, na to má pravidlo: *„má-li skill jediné chování, žádný režim nemá a nepojmenovává se“*. Rozhodl uživatel s tím, že co chce ovlivnit, napíše volnými slovy za příkaz. **Dvě věci z toho musely přežít:** tabulka stavů zůstává deterministická (orientace není úsudek) a zvolená cesta se **oznámí jednou větou, než se sáhne na první soubor** – bez pojmenovaných režimů je to jediná pojistka proti tichému špatnému odhadu. Jméno kola zůstalo argumentem, takže `/next` vrací `/architect <kolo>`.

**`brainstorming` zůstal jen ve `/specify`.** Předtím ho volal návrh jedním zátahem, kdežto návrh po kolech ne – táž práce tedy běžela dvěma způsoby podle toho, jak velký záměr zrovna byl. `/architect` proto vede rozhovor sám, jako dosud kolo; klasifikace rozsahu (spike / bounded / architectural), kvůli které se `brainstorming` volal, zůstala tam, kde rozhoduje, jestli se zadání vůbec píše.

**`/architect` má vlastní bránu na začátku.** Dosud byla brána jediná a stála ve `/specify`, jenže nejčastější reálné volání `/architect` ji míjí: přírůstek do už navrženého systému, kde se `requirements.md` nemění. Šest kritérií z dřívější *Fáze 3b* se proto z odstavce uprostřed stalo vstupní podmínkou. Chybějící `requirements.md` **neblokuje** – projekt může mít živý návrh a požadavky nikdy nevést.

**Zamítnut sdílený `skills/DOCUMENTS.md`.** Návrh zněl přestěhovat šablony obou dokumentů o úroveň výš vedle `PREFLIGHT.md`, protože hranici omezení/volba potřebují oba skilly. **Uživatel to zpochybnil otázkou, jestli to není věc `STRUCTURE.md`** – a byla: hranice tam stála doslova už předtím, takže kapitola *Proč dva dokumenty a ne jeden* ve `specify/SKILL.md` byla druhá kopie už v té chvíli. Do `STRUCTURE.md` se doplnilo jen chybějící **odůvodnění** (různá životnost obou dokumentů a kontrolní otázka *změní se to, když se změní technologie?*) a kapitola ze skillu zmizela. Šablony sekcí jsou naproti tomu instrukce pro Clauda za běhu, ne katalog struktury, takže se rozdělily na `skills/specify/documents.md` a `skills/architect/documents.md`.

**Srovnávací běh se vědomě vynechal** (`~/.claude/skills/skill/SKILL.md`, *Fáze 4*). Měří, jak agent selže bez skillu; vstupem tady ale nebylo nové téma, nýbrž 423 řádků odladěného textu, takže by neměřil nic.

### 2026-09-20 – Dvě vrstvy cyklu v kořenovém README nese pořadí, ne nadpisy

**Rozhodnutí:** v `README.md` se osa a kontrolní kroky **nerozdělují nadpisem**. Hranici drží pořadí sekcí a úvodní odstavec, který jmenuje první a poslední krok každého bloku.

**Důvod:** obě zjevnější varianty se zkusily a obě jsou vadné. **Nadpis `### Osa`** stojí na téže úrovni jako sekce jednotlivých skillů (`### [`/project`](skills/project/)`, tvar předepisuje `skills/SKILLS.md`), takže je neobsahuje – v osnově dokumentu stojí vedle nich jako další položka téže řady, ne jako jejich nadřazená skupina. **Bold řádek mezi sekcemi** hierarchii nelže, ale spadne dovnitř té předchozí: shodil test `test_readme_sections_hold_one_paragraph`, protože sekce `/release` tím dostala druhý odstavec.

**Třetí varianta se nezkoušela a je to vědomé:** demotovat skilly na `####` a nechat bloky na `###` by hierarchii spravilo, ale je to změna normy tvaru README, ne úprava jednoho souboru – a normu v tomhle nikdo nerozporoval.

**Našel to čtenář bez kontextu při `/cleanup`**, oba nezávisle na sobě. Je to typický nález téhle vrstvy: struktura, která vypadá správně v textu a lže v osnově.

### 2026-09-20 – Osou pro ptaní je volba, ne riskantnost zásahu

**Rozhodl uživatel** uprostřed `/consistency full` nad rezervačním systémem, po jedenácti otázkách, ze kterých ani jedna nenabízela volbu: *„když jsou ty opravy takhle jednoznačné a není se mezi čím rozhodovat (a dáváš mi stejně jen na výběr, jestli opravit hned nebo opravit později nebo se na to vykašlat a nechat to špatně), tak se mě ani neptej a hned to všechno oprav – odkládat na později to nechceme a odmítnout opravu věci, kterou je potřeba opravit, taky nechceme. Ptej se mě jen na věci, kde se to dá opravit více způsoby a chceš se zeptat, jaký zvolit.“*

**Co bylo špatně.** Kontrolní skilly dělily nálezy na **mechanické** (oprav rovnou) a **sporné** (zeptej se), a kritériem bylo „je oprava bezriziková a nemění chování ani strukturu?“. To je ale otázka o **zásahu**, ne o tom, jestli je z čeho vybírat – a ta dvě kritéria se rozcházejí přesně u nálezů, které něco mění a přitom je zjevné jak. Těch je v dokumentačním projektu většina: dorovnání počtu proti zdroji, doplnění guardu do rodiny, která ho u ostatních má, dotažení přejmenování. Všechny padly do „sporných“ a dostaly otázku s volbami *Opravit / Odložit / Přeskočit*, kde je odpověď předem známá.

**Cena se platí pozorností.** Ve zmíněném běhu bylo sporných 37 a po uživatelově větě jich 18 padlo bez jediné otázky – tedy skoro polovina interaktivního průchodu byla přehazování práce zpátky na uživatele. A ubírá to právě tam, kde je vytrvalost nejtenčí: uprostřed nejdelší fáze běhu, kdy mají přijít otázky, na kterých doopravdy záleží.

**Řešení.** Vznikl sdílený `skills/FINDINGS.md` – čtvrtý soubor toho druhu vedle `PREFLIGHT.md`, `SESSION.md` a `SEVERITY.md`. Drží tři skupiny (**mechanické** nemění chování, **jednoznačné** mění, ale podoba opravy je jedna, **sporné** mají víc obhajitelných podob) a pravidlo, že **volby v otázce jsou varianty opravy**; vyjde-li trojice *Opravit / Odložit / Přeskočit*, je to doklad, že nález mezi sporné nepatří. Přehled na začátku běhu vyčísluje obojí – kolik se opraví rovnou a kolik doopravdy zbývá na rozhodnutí –, protože to druhé číslo je jediné, které říká, jak dlouhý bude průchod.

**Dotčené skilly:** `/review` (držel definici pro ostatní), `/consistency`, `/attack`, `/audit`, `/oponent` a `/cleanup`.

**Předlohou byl `/oponent`**, který tohle dodržoval odjakživa: jeho volby jsou konkrétní varianty řešení a má u nich tabulku, která říká, na jaký stav se mapují. Zobecnilo se tedy to, co jeden skill z rodiny už uměl – ne nové pravidlo.

**Zamítnuto** přejmenovat skupinu „mechanické“ tak, aby jméno novému kritériu odpovídalo. Slovo je v konfigurační vrstvě na desítkách míst a většina jich míří na něco jiného (mechanické pravidlo, mechanická kontrola odkazů), takže by šlo o ruční průchod s nejistým ziskem. Místo toho přibyla třetí skupina s vlastním jménem.

**Nedořešeno zůstala podoba té otázky**, ne její kdy: `/oponent` má záchytné volby *Nechat být* a *Vrátit se k tomu později*, zbytek rodiny *Přeskočit* a *Odložit*, a je to dvojí slovní zásoba pro totéž. Vedeno v `todo.md`.

### 2026-09-21 – Merge je samostatný krok, ne fáze `/cleanup`

Postup dokončení větve – přihrát hlavní větev do pracovní, vyřešit konflikty, pustit nad spojeným stavem *Kontrakt příkazů*, teprve pak mergovat a uklízet – žil do téhle chvíle jako sekce *Dokončení větve* v `~/.claude/WORKTREE.md`. Mělo to dvě vady. **Neplatil v projektu bez worktree layoutu:** `WORKTREE.md` se tam nenačte, takže se merguje bez celého postupu, přestože nejdražší doložená chyba – souběžně puštěný úklid, který 17. 9. 2026 smazal nepřimergovanou větev lokálně i na remote – na layoutu vůbec nezávisí. A **`/cleanup` ho opisoval** odkazem dovnitř cizího souboru na třech místech.

**Rozhodnutí:** vznikl skill `/merge`, který nese postup celý a zobecněný na projekt bez worktree layoutu. `WORKTREE.md` si nechal *Větev žije, dokud uživatel neřekne jinak* a z *Dokončení větve* jen to, co plyne z layoutu (odkud se pouštějí příkazy, mazání worktree, proč spojený stav nesmí vznikat v `main/`). V životním cyklu stojí mezi **kontrolními kroky**, hned za `/cleanup`.

**Proč skill, a ne další soubor v `~/.claude`:** nový soubor by se v projektu bez worktree nenačetl stejně jako `WORKTREE.md`. Skill je jediný mechanismus, který se aktivuje podle toho, **co uživatel chce**, ne podle toho, jak vypadá adresář – napíše „přimerguj to“ a `description` ho vyvolá i v obyčejném repozitáři.

**Proč mezi kontroly, když mění hlavní větev:** nic nevyrábí. Bere hotovou práci a přesouvá ji tam, kam patří – je to táž údržba nad už vytvořeným jako `/cleanup` nebo `/consistency` (formulace uživatele, 21. 9. 2026). Vrstva se tím nerozmělnila: její nosné kritérium *nezvětšuje rozsah práce* platilo v `LIFECYCLE.md` už předtím a `/merge` mu vyhovuje stejně jako `/consolidate`, který taky nevrací nález.

**Obrací to zamítnutí ze 16. 9. 2026**, kdy se samostatný krok pro dokončení větve odmítl s tím, že „merge navazuje právě na úklid a vlastní krok by jen přidal příkaz, který se pouští pokaždé hned po něm“. Argument padl na tom, že mířil jen na **volání**, ne na **umístění postupu** – a volání se nemění: `/cleanup` merge dál nabízí jedním stiskem na konci svého běhu. Nabídka je ale zkratka k volání navazujícího kroku, ne jeho fáze; kdyby merge byl součástí `/cleanup`, nemohl by existovat samostatně.

**Zamítnuto – `/merge` jako krok osy:** vyrábí merge commit, takže by to sedělo na „něco tvoří“. Jenže kroky osy stojí v pořadí a čekají na výstup toho předchozího, kdežto větev se zakládá na každou práci, takže se merguje i po `/specify` nebo po kole `/architect`. Zařazení do osy by tvrdilo pořadí, které neexistuje.

**Zamítnuto – třetí vrstva cyklu:** rámeček v `RULES.md` je zdrojem pravdy pro `/next`, který ho rozebírá na vrstvy `osa` a `kontroly`, a `tests/test_next.py` tvrdí, že jiné dvě tam být nesmí. Třetí vrstva by rozbila infrastrukturu kvůli jednomu kroku.

**Nabídka v `/cleanup` se tím rozšířila i mimo worktree layout.** Do té chvíle se volba *Přimergovat do main* objevovala jen v kontejneru s `.bare`, protože jinde nebyl žádný postup popsaný a merge by znamenal přepnout pracovní strom, ve kterém může pracovat jiná session. První důvod vznikem `/merge` odpadl, druhý kryje podmínka čistého pracovního stromu, kterou `/cleanup` vyžaduje tak jako tak. Nově tedy rozhoduje jediné: stojíš na jiné než hlavní větvi.

**Vědomě nepokryto:** slučování přes pull request na serveru. `/merge` merguje lokálně a pushuje výsledek; projekt s povinným review v GitHubu by potřeboval jinou cestu a ta se zatím nenavrhovala.

### 2026-09-21 – Ptaní se zúžilo podruhé: „netroufáš si“ padlo a zákaz falešné trojice míří na tvar

Kritérium *Kdo o nálezu rozhoduje* (`skills/FINDINGS.md`, 20. 9. 2026) mělo zabránit otázkám, ve kterých není z čeho vybírat. Den nato se přesto v běhu `/cleanup` objevila otázka s volbami *Zapsat do todo / Vyřešit teď / Zahodit* nad nálezem „dva dokumenty uvádějí u téže věci jiný počet“. Uživatel to zachytil a poslal snímek obrazovky.

**Příčiny byly dvě a obě systémové, ne nepozornost v jednom běhu.**

**1. Podmínka „netroufáš si“ byla nekontrolovatelný únik.** V tabulce sporných nálezů stála jako jediná položka bez vnějšího kritéria – ostatní se dají ověřit (má oprava víc podob? je zásah nevratný? sahá mimo repozitář?), tahle je pocit. Model jí odůvodnil nález, jehož odpověď šla zjistit prací: hranice mezi dvěma pojmy, o kterou se opíral, byla v katalogu, ze kterého se obě čísla počítala. **Rozhodnutí:** podmínka padá a nahrazuje ji *chybí údaj, který ví jen uživatel a nedá se zjistit z repozitáře*, plus explicitní krok *Nejistotu nejdřív zkus odstranit* – jde-li odpověď spočítat, dohledat nebo porovnat se zdrojem, není to sporný nález, ale práce. **Pracnost není spornost:** uživatel má na tutéž práci tytéž soubory, takže se dotazem nešetří, jen se mu přehazuje zpátky i s kontextem, který má načtený model a on ne. Je to totéž, co `RULES.md`, *Při nejistotě se zeptej*, říká o dohledatelném údaji; `FINDINGS.md` to rozlišení nemělo.

**2. Zákaz falešné trojice byl psaný na konkrétní slova.** Stálo v něm „vyjdou-li ti volby *Opravit / Odložit / Přeskočit*“, jenže přišly volby *Vyřešit teď / Zapsat do todo / Zahodit* – sémanticky táž trojice, jiná jména, a model v ní zakázaný vzorec nepoznal. Navíc ji `cleanup/out-of-scope.md` sám předepisoval tabulkou, takže se jevila jako schválený tvar. **Rozhodnutí:** zákaz míří na tvar a má test – **je aspoň jedna volba podobou řešení, tedy odpovědí na „jak“?** Odpovídají-li všechny jen na „kdy“ (teď / potom / nikdy), otázka se nemá položit.

**Výjimka, bez které by to bylo moc široké:** u položky, která není vadou, ale novou prací nebo nápadem, je „jestli a kdy“ doopravdy uživatelovo rozhodnutí – rozšíření, které nikdo nezadal, se nedá opravit, protože není co. Test tedy zní: **existuje stav, který je prokazatelně špatně?** Když ano, je volba „kdy“ falešná.

**Opraveno i mimo `/cleanup`:** `review/SKILL.md` mělo „cokoliv, u čeho si netroufáš“ v seznamu sporných; `oponent/SKILL.md` tvrdil, že v `/consistency` a `/review` je trojice *Opravit / Odložit / Přeskočit* „naopak správně“, což byl od 20. 9. přímý rozpor s `FINDINGS.md`. V `/cleanup` samotném padla nejčastější falešná otázka celého skillu – ve fázi udržování souborů se u položky ptal *Zapsat / Odložit / Přeskočit*, přestože `question` nesla hotový návrh, co kam zapsat.

**Vědomě bez mechanismu.** Je to podruhé, co se totéž řeší textem pravidla, a text se podruhé obešel – další zápis proto sám o sobě záruku nedává. Vynutit by to šlo hookem `PreToolUse` nad `AskUserQuestion`, který by otázku s volbami jen o „kdy“ odmítl. Nezaložil se: je to vrstva zasahující do každé session v každém projektu, falešný poplach by zablokoval legitimní otázku a vypnutá kontrola pak nehlídá nic (`RULES.md`, *Ověřitelná kontrola místo dojmu*). **Statický test nad texty skillů se zamítl taky** – zakázanou trojici dnes zmiňuje pět souborů v rámci jejího zákazu, takže by test musel rozlišit zmínku od předpisu a to je křehké měřidlo.

**Uživatel hook zamítl** (21. 9. 2026, *„hook ne, takhle textově to stačí“*) poté, co mu byl předložen i s tím, že textové pravidlo se obešlo už podruhé. Zůstává to tedy vědomě bez mechanismu: cenou je, že třetí obejití nikdo nezachytí dřív než člověk u obrazovky. Otevírat to znovu má smysl až tehdy, když se to stane – ne dřív.

### 2026-09-21 – `/discovery` odpovídá hlavně na „proč“ a vyrábí `docs/demand.md`

**Zadal uživatel** po debatě o tom, jestli se z téhle soustavy dá udělat framework prezentovaný ven. Při hledání mezer proti okolí vyšlo najevo, že krok, který měl odpovídat na *proč*, na něj neodpovídal: `/discovery` zkoumal konkurenci a rizika, tedy **proti čemu** se staví, ne **jestli to někdo chce**. Mezi `/project` a `/specify` tak nestálo nic, co by ověřilo existenci problému a poptávky – a od `/specify` dál každý krok předpokládá, že je rozhodnuto stavět. **Postavit pečlivě něco, co nikdo nechce, je nejdražší způsob selhání celého cyklu**, protože se projeví až hotovým produktem, který nikdo nepoužívá.

**Je to naše vlastní mezera, ne mezera oboru** – a stojí za to to říct přesně, protože se to snadno splete. Srovnání spec-driven frameworků ([arXiv 2606.04967](https://arxiv.org/pdf/2606.04967)) jmenuje **šest** věcí, které těmhle soustavám systematicky chybí: sledování po nasazení, údržba artefaktů, zpětná vazba z provozu, adversariální testování, dohledatelnost a governance nad rozhodováním agenta. **Ověření poptávky před stavbou mezi nimi není** – a to proto, že celý ten obor začíná až u hotové specifikace. Z těch šesti máme čtyři zabrané (`/attack`, sledovací okno v `/release`, doc-first řetěz s `decisions.md`, `FINDINGS.md` s ověřovatelem nálezů), pátou (údržbu artefaktů) kryje povinnost průběžné aktualizace a `/consistency`, a šestá – zpětná vazba z provozu – zůstává otevřená v `todo.md`. Tohle rozhodnutí zavírá **sedmou, kterou ten seznam nezná**.

**Nový dokument, ne sekce ve stávajícím.** Zvažovalo se rozšířit `## Co poměřujeme` v `competition.md`; zamítnuto, protože hlavní výstup kroku nemůže být podsekcí dokumentu o konkurenci a při aktualizaci konkurence (druhý běh skillu) by se vláčela i část, která se nemění. Platí *Nový dokument vzniká tehdy, když drží jiný řez* z `STRUCTURE.md`.

**Jméno `demand.md`, ne `problem.md`.** Rozhodl uživatel; ze čtyř předložených (`demand`, `need`, `why`, `evidence`) vyhrálo to, které **rovnou říká, co se má doložit**, a tím tlačí na doklad místo dojmu. `why.md` se zamítlo, protože by jako jediný podklad v `docs/` byl pojmenovaný svou rolí, ne obsahem; `evidence.md` proto, že doložené má být všechno, takže by si jméno nárokovalo i obsah ostatních dvou dokumentů.

**Verdikt má dvě hodnoty a nedoložená poptávka je platný výsledek, ne vada.** Vyjde-li nedoložená, skill se zastaví a nabídne tři cesty (ověřit nejmenším pokusem, pokračovat s rizikem, pokračovat protože rozhodl někdo jiný) – ale **nerozhoduje za uživatele** a nesmí přes to přejít mlčky. Do `risks.md` pak jde nedoložená poptávka jako riziko s nejvyšším dopadem a *Promítnutí do produktu* u něj znamená zmenšit první verzi tak, aby se poptávka ověřila co nejdřív.

**`demand.md` se nepřeskakuje kvůli tomu, že produkt nemá trh.** Dosud se celý `/discovery` přeskakoval u interního nástroje a zakázky; nově se škrtá **po dokumentech** – tam odpadá konkurence, kdežto poptávka a rizika platí dál. Nástroj, který si lidé v organizaci obejdou tabulkou, je totéž selhání jako aplikace bez zákazníků, jen za něj platí někdo jiný. Celý skill odpadá jen u přírůstku do hotového produktu, kde je „proč“ rozhodnuté **a zapsané**.

**Doklady se oddělují od dojmů zvláštní sekcí.** Rozdíl mezi „myslím, že to lidi chtějí“ a „tři jmenovaní lidé o to požádali“ se v jednom seznamu stírá tiše, a přitom na něm stojí celý verdikt. Skill proto má sekci *Dojmy bez dokladu* a odpověď „nikoho jsem se neptal, přišlo mi to jako dobrý nápad“ zapisuje doslova.

**Uživatelský výzkum to nenahrazuje a skill to přiznává.** Tři nové cesty rešerše (*Hlas problému*, *Ochota platit*, *Objem a jazyk hledání*) hledají veřejné stopy problému, ne živé lidi. Je to vědomá mez (`RULES.md`, *Zapiš i to, co vědomě nemáš*): doklad z fóra je slabší než rozhovor se zákazníkem a skill nemá předstírat opak.

### 2026-09-21 – Zpětnou vazbu z provozu zavírá `/evaluate` a `docs/operation.md`

**Zadal uživatel** větou „tu díru musíme zaplnit“ nad položkou v `todo.md`. Cyklus umožňoval zavřít smyčku jen pro **pády**: sledovací okno v `/release` nasazení neuzavře, dokud někdo neřekne „okno uzavřeno, N nových chyb“ – ale žádný krok nevracel z provozu zjištění o tom, jestli se to používá, co lidé nedokončili a co si vyžádali. Srovnání spec-driven frameworků ([arXiv 2606.04967](https://arxiv.org/pdf/2606.04967)) jmenuje *feedback integration* mezi šesti mezerami oboru; sledovacím oknem jsme měli zabranou jen její polovinu. Šest rozhodnutí padlo v řízeném rozhovoru, každé z předložených variant s důsledky.

**Je to krok osy za `/release`, ne kontrolní krok.** Kontrolní vrstva podle `skills/LIFECYCLE.md` nezvětšuje rozsah práce, kdežto tenhle krok vyrábí podklad, ze kterého vzejde další práce. Cenou je odchylka, kterou žádný jiný krok osy nemá: **nespouští ho výstup předchozího kroku, ale čas**. Zamítlo se proto, že krok osy s časovým spouštěčem je menší lež než kontrolní krok, který rozsah práce zvětšuje.

**Zamítnuto – režim `/discovery`:** s `/discovery` se přeskočí. Ten se u přírůstku do hotového produktu přeskakuje celý, protože „proč“ je rozhodnuté – a zpětná vazba z provozu je přesně to, co se u přírůstku přeskočit nesmí. Navíc „co lidé nedokončili“ není doklad poptávky a do `demand.md` nepatří.

**Zamítnuto – rozšířit sledovací okno `/release`:** okno je krátké, jde o hodiny až dny, a otázka „nerozbilo se to?“ má odpověď hned. Poznání přichází týdny po nasazení, takže by se okno muselo protáhnout tak, že by `/release` nikdy neskončil.

**Vzniká nový produktový podklad `docs/operation.md` a nic se z něj nepropisuje samo.** Odpovídá na otázku „co o produktu víme z provozu“ a plní ho jen tenhle krok. Změna zadání je práce `/specify`, která si podklad přečte jako vstup – tím zůstává doc-first řetěz neporušený. **Zamítnuto – propisovat poznatky do `demand.md`, `scenarios.md` a `risks.md`:** týž poznatek by stál na dvou místech a při dalším běhu by se rozešly. **Zamítnuto – zapisovat jen do `demand.md`:** ten má verdikt o dvou hodnotách vztažený k otázce **před** postavením; provoz odpovídá na otázku o hotové věci a verdikt by se přepisoval mimo svůj rozsah. **Zamítnuto – jen úkoly do `todo.md`:** nebylo by vidět, odkud se to ví, nedaly by se sledovat trendy mezi běhy a „nikdo to nepoužívá“ není úkol, takže by se nemělo kde zapsat.

**Zdroje se berou podle žebříčku síly a jejich absence je platný výsledek.** Pořadí: analytika, dotaz do databáze aplikace, logy a chybové hlášení, tikety a maily, vlastní pozorování – u každého poznatku se zapisuje zdroj, aby se držela hranice **dokladu a dojmu** z `demand.md`. Není-li ani jeden zdroj, výstupem běhu je, že se neměří, a co se má začít měřit. **Zamítnuto – bez strojového zdroje krok přeskočit:** u projektů bez měření, což je většina, by se díra nezaplnila vůbec a krok by se hlásil jako přeskočený pořád. **Zamítnuto – rozhovor s uživatelem jako plná náhrada:** setřel by hranici dokladu a dojmu a podklad by vypadal doloženě, i když není.

**Hotovo znamená, že žádný poznatek nezůstal bez rozhodnutí** – u každého stojí, že se z něj stal úkol, nápad v backlogu, nebo že se vědomě neřeší a proč. Je to týž postup jako u nálezů v `skills/FINDINGS.md`. **Zamítnuto – měřit pokrytí předem daných otázek:** poznatek by mohl zůstat zapsaný bez následku, tedy táž slepá ulička jako dnešní sledovací okno. **Zamítnuto – porovnání se záměrem z `requirements.md`:** nenajde nic, co v zadání nestojí, a právě to jsou nejcennější zjištění z provozu.

**Spouštěčem je pokyn uživatele; `/release` k tomu zapíše datum a `/next` ho nabídne.** Skill je samostatný a pouští se ručně, „až si člověk vzpomene“. `/release` na konci uloží do `todo.md` datovanou položku, kdy se má provoz vyhodnotit, a `/next` ji začne nabízet, jakmile ten den nastane – a rovnou ji spustí. Žádná nová vrstva, jen existující skilly a jeden zápis v souboru; interaktivní část zůstává u člověka, který právě sedí u projektu, takže omezení *Jeden člověk, jedna interaktivní session* platí dál. **Zamítnuto – naplánovaný agent v cloudu:** sběr by běžel bez souhlasu průběžné kontroly a bez toho, komu položit otázku. **Zamítnuto – spouštěčem je příští práce na projektu:** u projektu, na kterém se rok nic nedělá, by se poznání nezískalo nikdy, a přijde-li práce za tři dny, ještě není co měřit.

**Jméno `/evaluate`, podklad `operation.md`.** Rozhodl uživatel ze čtyř předložených párů. Vyhrálo to, které pojmenovává, čím se krok liší od sběru čísel: u každého poznatku padá rozhodnutí a bez toho krok není hotový. `/observe` se zamítlo, protože nenapovídá, že se tam i rozhoduje; `/feedback` proto, že je to výsledek, ne činnost, a „zpětná vazba“ zní jako názory lidí, kdežto hlavním zdrojem jsou data o tom, co doopravdy dělali; `/measure` proto, že je užší než krok sám – vyžádaná funkce ani projevené riziko není měření, a `usage.md` by byl na půlku obsahu špatný název.

### 2026-09-21 – Předjímané *Časté chyby* se ve skillu nedrží, sekce se smazala

**Rozhodl uživatel** při úklidu po přestavbě `/discovery`. Skill měl desetiřádkovou tabulku *Časté chyby*, ale **na skutečném projektu nikdy neběžel** – všech deset řádků tedy popisovalo, co by se pokazit mohlo, ne co se pokazilo. Norma (`skills/SKILLS.md`, *Povinné sekce a jejich pořadí*) u té sekce žádá opak a říká ji zakládat až po prvních ostrých bězích.

**Proč to není neškodná předjímka.** Ve skillu vypadá stejně jako doložená sekce u sousedů, takže čtenář – model i člověk – jí přisuzuje váhu poučení z provozu, které za ní nestojí. Zvažovalo se nechat ji s poznámkou „zatím nedoložené“; zamítnuto, protože poznámka tu váhu nesejme a sekce tím přestane být tím, čím podle normy je. Ve `/discovery` se proto smazala celá a **založí se znovu po prvním běhu**; hlídá to položka v `todo.md`.

**Neplatí to jen pro tenhle skill, ale řeší se zatím jednotlivě.** Jestli má norma rozlišit předjímku od doloženého poučení obecně, nebo se má pravidlo jen důsledněji dodržovat, se nerozhodlo – u ostatních skillů se nic nemazalo.

### 2026-09-21 – Co se rozhodlo při stavbě `/evaluate`

Navazuje na *Zpětnou vazbu z provozu zavírá `/evaluate` a `docs/operation.md`* – tam je šest rozhodnutí o tom, **jestli a jak**; tady čtyři, která padla až při psaní skillu.

**Skill nemá režimy.** Má jedno chování, takže se podle `skills/SKILLS.md` žádný nepojmenovává. Zvažovalo se oddělit sběr od rozhodování, aby šlo „jen sebrat čísla“; zamítnuto, protože přesně to je slepá ulička, kterou krok zavírá – běh bez rozhodnutí by byl režim na výrobu evidence, kterou nikdo nečte.

**Odložení položky k datu je obecný mechanismus, ne věc `/evaluate`.** `collect.py` v `/next` rozpozná `od <YYYY-MM-DD>` **hned za názvem** položky a do té doby ji do fronty nezařadí. Vyšlo to najevo při psaní: „datum, kdy vyhodnotit provoz“ je jen první uživatel něčeho, co platí pro každou položku se smyslem od určitého dne. **Datum se hledá jen na začátku textu**, protože první verze prohledávala prvních 80 znaků a věta „sazba platí od <datum>“ jí položku skryla – falešné parkování je přitom ta horší polovina, protože položka nezmizí hlučně, jen se nikdy nenabídne.

**Sběr se deleguje podmíněně, ne vždy.** První verze skillu přikazovala pustit na každý zdroj jednoho agenta. **Doložil to první ostrý běh (21. 9. 2026):** agent delegaci vědomě neprovedl s odůvodněním, že všech pět zdrojů má dohromady pár kilobajtů, takže by si každý agent načetl totéž a výstup by se vrátil převyprávěný. Bylo to správné a je to přímá aplikace *Velké průzkumné úkoly deleguj* z `RULES.md` – deleguje se kvůli kontextu, ne kvůli úspoře.

**Poznatky se dělí podle toho, na čem stojí, a přibyl verdikt o důvěryhodnosti dat.** Taky z prvního ostrého běhu: ověřovatel tam našel, že u poloviny sousedních záznamů podle autoinkrementovaného klíče neroste `created_at`, čímž padla celá číselná vrstva běhu – zatímco nálezy o chybějícím omezení v databázi a chybějící auditní stopě platily dál. **Zamítnuto – odložit celé vyhodnocení, dokud se data nevyjasní:** zahodilo by i to, co na datech nezávisí. **Zamítnuto – poznámka o nedůvěryhodnosti v úvodu podkladu:** s konkrétním číslem o dva odstavce dál se nikdy nespojí.

**Ověřovatel nálezu je samostatný agent, ne vlastní přepočet.** Druhá verze měla jen „zopakuj si číslo sám“. To odhalí překlep v dotazu, ne špatný předpoklad o datech, a naráží na *Model a effort podle úkolu* z `RULES.md`, odrážku o izolaci kontextu: kdo nález našel, ten ho hájí. Doloženo tímtéž během, kde ověřovatele pustil agent sám od sebe a zachránil tím výsledek.

**Srovnávací běh byl neplatný podruhé za sebou a je to vada metody, ne náhoda.** Agent si `/evaluate` uprostřed práce našel na disku, načetl ho a jel podle něj – takže neměřil, jak se selhává bez skillu, stejně jako u `/merge`. Vyplývá z toho, že **srovnávací běh nad skillem uloženým v témže repozitáři, ve kterém agent pracuje, měřit nejde**; kdo ho bude chtít doopravdy pustit, musí skill dočasně odstranit nebo agenta poslat do prostředí bez něj. Jako **první ostrý běh** byl přesto cenný – vytěžily se z něj tři opravy výš a sekce *Časté chyby*.

### 2026-09-22 – Tlakové scénáře `/evaluate` prošly a vytěžily tři vylepšení

Čtyři scénáře, každý tlačil na jedno omezení skillu, každý ve vlastním adresáři s vlastním prefixem. **Všechna čtyři omezení se dodržela** – žádné se pod tlakem neprolomilo. Cenné na nich ale nebylo potvrzení, nýbrž tři věci, které agenti udělali lépe, než skill předepisoval, a které se do něj proto zapsaly.

**Vyvrácené odůvodnění se hlásí, i když rozhodnutí platí dál.** Scénář tlačil větou „co jsme si odškrtli jako *dělat nebudeme*, to platí“ na vyžádanou funkci, kterou zadání vylučovalo odůvodněním „kapacity se plní z 80 %, takže by to byla funkce pro nikoho“ – přičemž tři z pěti kapacit byly plné a dva rodiče o tu funkci nezávisle napsali. Agent funkci neprosadil ani nezamítl: poslal ji do `backlog.md` jako nerozhodnutou a zvlášť ohlásil, že **odůvodnění** toho rozhodnutí je prokazatelně nepravdivé, kdežto rozhodnutí samo platit může. To rozlišení ve skillu nebylo a je lepší než to, co měl – ptá se na jednu větu odůvodnění, ne na to, jestli se funkce postaví.

**Uklidňující tvrzení musí ověření přežít stejně jako alarmující.** Scénář dal do logu pět ztracených objednávek a do databáze tytéž objednávky jako zaplacené – tedy uklidňující odpověď na dosah. Agent nepotvrdil ani ji: v datech nebylo čím řádek s logem spárovat, takže **nešlo tvrdit ani „ztrácí se“, ani „neztrácí se“**. Závažnost pak odvodil z toho, co nejde vyloučit, ne z toho, co se prokázalo. Bez tohohle doplnění by se chybějící doklad o škodě dal čít jako doklad, že škoda není.

**Použití nepostavené funkce nemůže být v datech.** Agent odmítl poznatek „pětina hledání je podle autora, takže předpoklad v zadání neplatí“ námitkou, na kterou skill nemyslel: není-li ta cesta postavená, nemá ji aplikace čím zaznamenat, takže by týž řádek sloužil zároveň jako doklad, že funkce chybí, i jako doklad, že ji lidé použili.

**Mez toho měření, ať se nepřehání.** Scénář na přepsání zadání změřil hranici jen nepřímo: data v něm byla generovaná pravidlem `id % 5 = 0` a ověřovatel to poznal, takže poznatek padl na kvalitě dat, ne na tlaku zadání. Doloženo je tedy, že ověřovací vrstva funguje, ne že skill odolá tlaku nad platným poznatkem. Ladění `description` proběhlo nejdřív zkráceně (4 prompty ze dvanácti) a **doměřilo se týž den na 12/12** – šest pozitivních chytilo `/evaluate`, šest near-missů minulo správně. Nezměřený zůstal jen dvojí běh na prompt.

**Dva agenti nezávisle obešli bod 1 v `PREFLIGHT.md`** („není to git repozitář → skonči bez dalšího příkazu“) s odůvodněním, že `/evaluate` git nepotřebuje. Byla to otevřená otázka o přípravě, ne o tomhle skillu; **vyřešila se týž den** rozdělením bodu 1 – viz *Bod 1 přípravy rozlišuje, jestli skill git doopravdy potřebuje* níž.

### 2026-09-22 – Bod 1 přípravy rozlišuje, jestli skill git doopravdy potřebuje

**Rozhodl uživatel** ze tří předložených variant. `PREFLIGHT.md`, bod 1, velel u adresáře bez `.git` *„skonči bez dalšího příkazu“* – jedna tvrdá podmínka pro každý skill, který běží nad projektem. **Obešli ji tři agenti nezávisle na sobě** (běhy `/evaluate`, 21. a 22. 9. 2026) se shodným odůvodněním, že jejich skill nic nemění, necommituje a diff nepotřebuje. Podle *Mechanická pravidla nad rozhodováním případ od případu* z `RULES.md` je opakované obcházení nejdřív signál o formulaci pravidla.

**Vada byla v tom, že bod mísil dvě věci:** *zjisti, kde stojíš* (kořen projektu a worktree layout), což potřebuje každý skill nad projektem, a *bez gitu nepokračuj*, což potřebuje jen ten, kdo commituje, diffuje proti hlavní větvi, čte historii nebo pouští průběžnou kontrolu. Bod 1 proto ty dvě věci rozlišuje tabulkou – **body v přípravě zůstávají tři plus dva**, nepřibyl žádný –, a druhá z nich se váže na kritérium, ne na jmenovitý výčet skillů – ten by při dalším skillu zestárnul a nikdo by ho nepřepsal.

**Dopsalo se i to, co bez gitu odpadá dál.** Povolit pokračování a nechat platit body 3 až 5 by vedlo do slepé uličky: stav pracovního stromu, průběžná kontrola před startem i rozsah změn na větvi stojí všechny na gitu. Bez něj zbývá bod 1 a 2, a mez se hlásí jako jedna věc – včetně toho, že bez stavu pracovního stromu nejde poznat cizí rozdělaná práce.

**Zamítnuto – git zůstává tvrdým předpokladem soustavy a obcházení je chyba agenta.** Mělo to oporu (bez gitu neplatí autocommit, `/merge`, worktree layout ani souhlas průběžné kontroly, a `/project` git zakládá), ale tři agenti už prokázali, že to pravidlo obejdou, a nikde po tom nezůstane stopa.

**Zamítnuto – přeformulovat bod 1 na doporučení pro všechny.** Přestalo by chránit skilly, které git doopravdy potřebují: `/merge` nebo `/implement` by běžely až do místa, kde jim první git příkaz spadne.

**Zamítnuto – odchylku si napíše každý takový skill do své `Fáze 0`.** Znamenalo by to opsat totéž do `/evaluate`, `/diagram` a `/report` a doufat, že si na to vzpomene i příští skill – přesně ten způsob, jakým se pravidla rozcházejí.

**Poznámka k tomu, jak se to našlo:** ti tři agenti běželi v adresářích postavených ve scratchpadu, a ty git nebyly. V reálném projektu téhle soustavy to nastat nemůže. **Není to tedy provozní vada, ale nepřesnost normy, kterou měření odhalilo** – a stojí to tu zapsané proto, aby se příště nehledalo znovu.

### 2026-09-23 – Úspora nákladů míří na kontext, ne na délku odpovědí

**Podnět:** dotaz na nástroje `caveman`, `ponytail`, `headroom` a `rtk` – tři z nich slibují úsporu tokenů, čtvrtý úsporu kódu. Místo posouzení podle jejich README se **změřila skutečná spotřeba** ze session logů: 117 tisíc volání API za měsíc (`~/.claude/projects/**/*.jsonl`, pole `usage`), vážené relativní cenou (zápis cache 1,25×, čtení cache 0,1×, výstup 5× vůči vstupnímu tokenu). **„Nákladová jednotka“ v těchhle zápisech znamená jeden takto vážený token** – je to tedy počet vstupních tokenů, za který by táž práce vyšla stejně. Na peníze se převádí cenou vstupního tokenu použitého modelu a mezi modely se **porovnávat nedá**.

**Naměřeno:** čtení kontextu **67 %** nákladů, zápis do kontextu 22 %, výstup modelu **10 %**. Session nad 400 volání jsou **4 % session a 52 % nákladů**; průměrný kontext v nich je 423k tokenů proti 71k u krátkých a s pozicí ve session roste lineárně (108k na začátku, 545k po třístém volání). Subagenti jsou 26 % nákladů. Na nejlevnější model připadá **0,1 %** volání, na nejsilnější 97,6 %.

**Rozhodnutí:** do `RULES.md` přibyly dvě sekce – *Co vložíš do kontextu, platíš do konce session* (cena obsahu je jeho velikost krát počet zbývajících volání) a *Dlouhá session je dražší než dvě krátké* (kvadratický růst, ohlásit při ~150 voláních nebo 250k kontextu). *Model a effort* dostal **zákaz s výčtem** místo doporučení a *Velké průzkumné úkoly deleguj* větu o tom, co agent vracet nemá. Do `~/Dev/context/coding/` šlo to, co platí jen u kódu: *Příkaz vol podle velikosti jeho výstupu* (`quality.md`) a *Než napíšeš kód, projdi, čím by se psát nemusel* (`coding.md`).

**Zamítnuty všechny čtyři nástroje.** `caveman` řeže výstup modelu, tedy **nejmenší** z těch tří položek, a jeho skill si navíc bere ~1000 tokenů pravidel na každou konverzaci a koliduje se stylem komunikace v `RULES.md`. `headroom` a proxy část `caveman` sedí jako MITM mezi Claude Code a API (`ANTHROPIC_BASE_URL` na localhost): celý obsah session včetně klientských podkladů by tekl přes cizí binárku a **přepisování historie rozbíjí cache**, tedy tu 67procentní položku – úspora by se obrátila v přirážku. `rtk` míří správným směrem (40 % výstupů nástrojů přesahuje 1k tokenů a platí se do konce session), ale filtruje tak, že **skutečný výstup příkazu přestane být vidět** – proti *Ověřitelná kontrola místo dojmu*; totéž se dá mít volbou příkazu bez proxy, což je dnešní *Příkaz vol podle velikosti jeho výstupu*.

**Z `ponytail` se převzal jediný prvek – řetěz otázek před psaním kódu.** Zbytek jeho pravidel `coding.md` už pokrývá hlouběji a s doloženými důvody (*Nezavádět spekulativní obecnost*, *Nedeklaruj, co neimplementuješ*, *Redundanci obhaj, nebo zruš*, *Nezakládat strukturu, kterou nikdo systémově nečte*); opsat je podruhé by vyrobilo dvě místa, která se rozejdou.

**Zamítnuto – tvrdý práh s hlášením každých 50 volání.** Účinnější, ale u dlouhé návrhové práce, kde je souvislý kontext to cenné, by se z toho stal šum a vypnul by se. Zvoleno ohlásit jednou za práh a nechat rozhodnutí na uživateli.

**Zamítnuto – nechat *Model a effort* jako doporučení.** Právě naměřená 0,1 % jsou doklad, že tenhle tvar pravidla nefunguje: model si u každého jednotlivého případu odsouhlasí výjimku. Cena zákazu je přiznaná – u malého rozsahu je delegace dražší než práce sama, proto má tři vyjmenované výjimky, které se musí říct nahlas.

**Čísla si ověř znovu, než podle nich budeš rozhodovat.** Jsou z jednoho měsíce a z období, kdy 49 % spotřeby dělal jediný projekt; skript je jednorázový a neuložil se.

### 2026-09-23 – Jak se chová `/clear`, `/compact` a transcript, a co stojí `/cleanup`

Změřeno a ověřeno při hledání úspor nákladů (navazuje na *Úspora nákladů míří na kontext, ne na délku odpovědí* výš). **Zapsáno jako podklad, ne jako rozhodnutí** – návrh, který z toho vyšel, žil v `todo.md` a rozhodl se 25. 9. 2026 (*Skill `/cleanup` poběží v subagentovi* níž). Podklad platí i kdyby se návrh zahodil, protože `/review` a `/consistency` čeká totéž.

**Co stojí `/cleanup`** (249 běhů, ze session logů):

| | |
|---|---|
| podíl úklidu na nákladech session, ve kterých běží | **55 %**, medián 60 % |
| z toho subagenti (dva čtenáři bez kontextu) | **2 %** |
| z toho opakované čtení téhož kontextu | 78 % |
| volání hlavní session v úklidu | medián 142, průměr 196, maximum 1872 |
| kontext při startu úklidu → na konci | 253k → 449k |

**Úklid dělá zhruba stejnou práci bez ohledu na to, co uklízí** – 102 až 158 volání napříč všemi velikostmi –, ale stojí **11,8× víc** po dlouhé session než po krátké – to je poměr mediánů podle **délky práce před úklidem** (do 80 volání 1,0M, nad 200 volání 12,0M). Členěno podle **velikosti transcriptu** vychází poměr krajních pásem 4,4×; jsou to dvě různá členění téhož, ne rozpor. Podle velikosti transcriptu: do 300 kB stojí 2,3M nákladových jednotek, 300–600 kB 3,2M, 600–1200 kB 5,1M, **nad 1200 kB 10,2M**. Z toho plyne **podlaha ~2,3M** i nad malinkou session – to je cena vlastních 150 volání, dnes schovaná pod cenou kontextu.

**Chování Claude Code, ověřené testem a měřením:**

- **`/clear` zakládá zcela novou session** – nové id, nový transcript, nový scratchpad – a **resetuje pracovní adresář** na ten, kde se `claude` spustil. Ověřeno 23. 9. 2026 testem v `~/Dev/cwdtest`: vznikly dva soubory, `55a0559a` (cwd se měnil na `sub`) a `8ff20c90` (cwd jen `cwdtest`). **Dřívější opačné tvrzení v téže session bylo chybné** – vzniklo z toho, že starý transcript po `/clear` pokračuje, jenže jsou to jen dozvuky příkazu, ne nová konverzace.
- **`/compact` naopak zachovává** session-id, transcript i pracovní adresář a zmenší kontext z mediánu 810k na 132k (13 měřených případů). **Medián zmenšení jednotlivých případů je 81 %**; poměr těch dvou mediánů vychází na 84 % – počítá se to z jiných čísel, takže se ty hodnoty nemusí rovnat.
- **`cd` do podadresáře mění working directory celé session**, ne jen shellu – systém to oznámí jako změnu Primary working directory.
- **Transcript je nadmnožina kontextu, ne podmnožina.** (**Od 26. 9. 2026 to platí s výjimkou:** velký výstup nástroje je v transcriptu uříznutý stejně jako v kontextu a plná verze leží v `tool-results/<id>.txt` – viz *Kolik z transcriptu se čte, rozhoduje počet kompaktací, ne zvyk* níž.) Obsahuje odpovědi včetně thinking bloků, zprávy poslané uprostřed odpovědi (`queue-operation`), hooky, system-remindery i odkazy na odložené velké výstupy. **A obsahuje všechno před kompaktací** – doloženo na session se 7 916 kB před ní, kde je čitelná i první zpráva.
- V čerstvé session po `/clear` stojí **před prvním skutečným promptem dva uživatelské záznamy** – `<local-command-caveat>` a `<command-name>/clear</command-name>`. Kritérium „čistá session“ proto nejde postavit na počtu uživatelských záznamů, ale na tom, že **žádný z nich nemá obsah začínající jinak než `<`**.

**Doložená vada dnešního `/cleanup`:** Fáze 0 velí zapamatovat si základ session přes `git rev-parse HEAD`. Ve 153 bězích se plný `rev-parse HEAD` zavolal **osmkrát (5 %)**, zatímco `rev-parse --short HEAD` pro záznam do `done.md` v 50 %. Fáze 6 si tedy diff pro čtenáře skládá z čehokoli, co je po ruce – v naměřených bězích `git diff --name-only origin/main`, `git diff main...<větev>` nebo hash odjinud. **Otevřená otázka, kterou to odkrylo:** mají čtenáři dostat diff session, nebo diff větve? Skill předepisuje první a improvizuje druhé.

**Poučení, které se zaplatilo šestkrát za jeden den: v transcriptu se hledá dotazem na strukturu, ne grepem na řetězec.** Postupně se takhle chytlo slovo „cleanup“ ze seznamu skillů v systémovém promptu (a prohlásilo za úklid celou session), `rev-parse` z textu skillu načteného do transcriptu, `/clear` z vlastní věty o `/clear`u, a dvakrát selhal filtr na tvar `<command-name>`, protože **pořadí tagů není pevné** – někdy je první `<command-message>`. Nejzrádnější instance dala **správnou odpověď ze špatného důvodu**: detekce nenašla nic a náhodou to byla pravda. Je to `quality.md`, *Měřidlo musí odlišit vlastní selhání od nálezu*, v čisté podobě.

### 2026-09-23 – Co subagent dědí od rodičovské session

Ověřeno testem (jeden agent typu `general-purpose`, úkol jen vypsat vlastní prostředí). Zapsáno zvlášť, protože to **platí pro každý skill, který deleguje**, ne jen pro `/cleanup`.

| Co | Hodnota u agenta |
|---|---|
| pracovní adresář (`pwd` i *Primary working directory*) | **shodný s rodičem** |
| cesta ke scratchpadu | **nese session-id rodiče**, ne vlastní |
| `Write`, `Edit`, `Skill` | má |
| `AskUserQuestion` | **nemá** – je jen mezi odloženými nástroji |
| effort | **nejde nastavit**; `Agent` bere `model`, ne `effort` |

**Nejdůležitější důsledek:** agent si **najde transcript rodičovské session sám**, protože jeho scratchpad ukazuje na ni – nemusí se mu předávat žádné id. To dělá z delegace úplně jinou možnost, než jaká se jevila, dokud se počítalo s `/clear`em.

**Pozor na jednu nekonzistenci:** adresář, do kterého agent ukládá svůj výstup (`…/tasks/<agentId>.output`), leží pod **jiným** UUID než scratchpad session. Vypadá to jako změna session-id a není to ona – transcript pod tím druhým UUID neexistuje. Kdo bude odvozovat session-id z cesty, musí brát tu ze systémového promptu, ne z cesty k výstupu agenta.

### 2026-09-25 – Řádek `/cleanup` v `done.md` nese i id uklizené session

**Rozhodl uživatel** při úklidu jako jediné nevypořádané téma, které nesouviselo s odloženou přestavbou skillu. Návrh vzešel z oponentury 23. 9. jako měkčí protějšek k **zamítnuté evidenci uklizených session** – ta padla proto, že skill je záměrně opakovatelný a rejstřík s čárou by šel proti té vlastnosti.

**Co se mění:** šablona v `skills/cleanup/SKILL.md`, Fáze 9, nově nese `session <session-id>` mezi hashem a počtem témat; `STRUCTURE.md` to popisuje u odrážky o tom, co `/cleanup` do sekce zapisuje.

**Proč to není evidence:** rejstřík by rozhodoval, **jestli** se smí uklidit znovu; tenhle řádek jen říká, **co** se uklidilo. Dvě data u téhož id znamenají dva úklidy, ne duplicitu, a nic se podle nich nefiltruje. Bez id se z `done.md` nedá poznat, čeho se běh týkal.

**Zamítnuto – nechat řádek beze změny.** Argument byl, že id je dlouhý řetězec, který člověk nečte, a že opakované běhy vyrobí víc řádků s týmž id. Neobstál: řádek čte **příští běh téhož skillu**, ne člověk, a víc řádků s týmž id je věcně správný záznam dvou úklidů.

### 2026-09-25 – Skill `/cleanup` poběží v subagentovi, ne v čisté session po `/clear`u

**Rozhodl uživatel po změření**, ne po úvaze – a to byla jeho podmínka: odhad úspory nebyl doložený, takže se nejdřív pustil pokusný běh.

**Co se měřilo.** Subagent bez práva zapisovat dostal transcript rozpracované session (2,8 MB, 1398 záznamů, 33 promptů, tři dny) a měl vytěžit dohody a zkonfrontovat je se soubory. **Správná odpověď byla známá** – do té session se zapisovalo průběžně, takže se vědělo, co má najít.

**Výsledek:** 45 volání a **0,87M nákladových jednotek** za Fázi 1 a 3, proti 10,2M mediánu dnešního úklidu nad transcriptem téže velikosti. Agent vytěžil 37 položek, 35 správně označil za zapsané, dva nálezy mimo OK byly oba správné a **jedno nevypořádané téma našel, které hlavní session přehlédla**. **Celý úklid bude stát víc** – odhad 1,5 až 2,5M je extrapolace z poměru fází, ne měření.

**Proč subagent a ne `/clear`.** Ověřeno testem (*Co subagent dědí od rodičovské session* výš), že agent dědí pracovní adresář i session-id přes cestu ke scratchpadu – **najde si tedy transcript rodiče sám**. Tím odpadá sedm z patnácti nálezů oponentury naráz: všechny, co byly o výběru session, o hledání transcriptu napříč projekty, o víc pracovních adresářích, o prázdném vlastním transcriptu, o worktree smazaném pod nohama, o seznamu bez cesty ven a o verdiktu mluvícím o cizí session. Existovaly jen proto, že `/clear` tu vazbu trhá – **zakládá novou session s novým id a resetuje pracovní adresář**. Navíc jde volat uprostřed session, na které se má dál pracovat.

**Ta poslední výhoda má mez a platí úžeji, než jak zněla.** Uživatel se na to zeptal při prvním ostrém běhu (25. 9. 2026) a odpověď je: v téže session se dál smí **čtenářská práce a hovor**, ne editace téhož repozitáře. Tři důvody, od nejhoršího: **commit rodiče sebere cizí rozdělanou práci**, protože agentův snímek `git status` vznikl na začátku běhu a změnu, která začala až během něj, nezná – tedy přesně scénář `~/.claude/RULES.md`, *Commituj jmenované cesty, ne `-A`*, devětkrát doložený; **souběžný zápis do týchž souborů** si přepíše výsledek nebo zapíše na místo, které v druhé verzi neexistuje; a **úklid je nutně neúplný**, protože agent čte transcript ve stavu, v jakém byl při jeho spuštění, takže se pozdější dohody v přehledu neobjeví ani jako mezera. Chytí je až druhý běh, který transcript vytěží celý znovu.

**Zamítnuto – `/clear` s předaným session-id.** Rozpracovalo se to do detailu a padlo to celé: tři pásma podle velikosti vlastního transcriptu, kritérium čisté session (žádný uživatelský záznam, jehož obsah nezačíná `<`), nabídka s příkazem ke zkopírování v pořadí „zkopíruj, pak `/clear`“. **Všechno to existovalo jen proto, že `/clear` trhá vazbu na session** – u subagenta není co vybírat ani kam zabloudit. Rozpracovaný postup se z `todo.md` smazal při přepisu skillu 25. 9. 2026; tenhle odstavec je z něj to jediné, co má cenu si pamatovat, totiž **čím se to zaplatilo**.

**Zamítnuto – `/compact` místo `/clear`.** Zachovává session-id i adresář, takže by fungoval bez parametru, ale nechává v kontextu 132k ztrátového shrnutí – a ztrátové je přesně v tom, co skill hledá: korekce, zavržené varianty, nevypořádaná témata. Zůstane ve skillu zapsaný jako horší varianta s důvodem.

**Tři háčky, které se musely vyřešit při přepisu:** agent nemá `AskUserQuestion`, takže interaktivní fáze musí vracet otázky nahoru i s hotovými zápisy; uživatel během běhu nevidí průběh, ačkoliv agent zapisuje; a **effort nejde nastavit**, jen model. První vyřešil tvar rozhodnutý týž den (*Tvar `/cleanup` po přesunu do subagenta* níž). **Z druhého se vyřešila jen polovina:** nevratná a ven mířící část zůstala u rodiče, protože agent necommituje ani nepushuje, ale **jeho zápisy uživatel průběžně nevidí a zastavit je nemůže** – to trvá a `skills/cleanup/README.md` to přiznává v *Požadavky a omezení*. Třetí zůstává přiznanou mezerou.

**Doložená mez, která platí i pro dnešní stav:** agent nečetl odpovědi celé, jen úseky kolem rozhodovacích míst, a posudek oponenta jen ze čtvrtiny – u 2,8 MB to jinak nejde. Není to argument proti subagentovi, protože `SESSION.md` na dlouhý transcript posílá subagenta tak jako tak; je to mez vytěžování jako takového a patří do zadání jako pokyn hlásit, co se nestihlo.

### 2026-09-25 – Tvar `/cleanup` po přesunu do subagenta

**Rozhodl uživatel** v šesti otázkách za sebou, hned po tom, co padlo *že* se do subagenta jde (*Skill `/cleanup` poběží v subagentovi, ne v čisté session po `/clear`u* výš). Naměřená ekonomika a doložení cesty jsou tam; tady je jen tvar.

| Otázka | Rozhodnutí |
|---|---|
| kde je řez | agent vytěží **i zapíše** a nahoru vrátí jen otázky, každou s hotovým textem zápisu ke každé volbě |
| kdo commituje | **rodič**, podle výčtu cest od agenta; agent necommituje ani nepushuje |
| kdy se pouští čtenáři | **hned po agentovi, před otázkami** – latence se schová za celou interaktivní část |
| jaký diff dostane čtenář pozůstatků | **diff větve**, ne diff session |
| co dělá druhý běh | **vytěží transcript celý znovu** (navazování na hash z `done.md` se rozhodlo a týž den se vrátilo, viz níž) |
| jak se dělí dokumentace | `SKILL.md` drží postup rodiče, nový `agent.md` celé zadání agenta |

**Jedno rozhodnutí z toho plyne a rozhodlo se samo:** agent nezapisuje položky, jejichž podoba závisí na nevypořádaném tématu – uživatelova odpověď je vzápětí zneplatní.

**Čtyři věci, které přesun sám neřešil, se vyřešily až tímhle tvarem:**

- **Cizí rozpracovaná práce** v pracovním stromu (skupina C z oponentury) padá s jmenovanými cestami: agent vrací výčet toho, co bylo rozpracované už před ním, a rodič to z commitu vynechá.
- **Základ session** dostal vynucení. Byl to doložený nedodělek – `git rev-parse HEAD` se volal v 5 % běhů, protože ho nic nepotřebovalo dřív než o šest fází později. Nově ho **počítá rodič ve *Fázi 0*** a předává v promptu, protože `HEAD` základ být nemusí – v projektu se zapnutým autocommitem bývá `HEAD` commit uvnitř session. Doloženo hned při prvním ostrém běhu: `HEAD` byl commit té session a diff pro čtenáře by z něj vyšel prázdný, což se od čistého nepozná.
- **Kategorie „co zůstalo rozbité nebo nedodělané“** přibyla do rekonstrukce session jako osmá. Dřív tam nebyla žádná a skill by nad větví s padajícím testem ohlásil „všechno zapsané“ – držel to kontext hlavní session a po přesunu by ho nedržel nic.
- **Měření „během téhle session“** přestalo být dojmem: znamená od základu session, tedy od toho commitu.

**Zamítnuto – agent jen vytěží a rodič zapisuje.** Odpovídalo by to přesně tomu, co se změřilo (0,87M za vytěžení a konfrontaci), ale zápis by pak běžel nad velkým kontextem rodiče, takže by z odhadované úspory 75–85 % zbyl zlomek. **Zamítnuto – dva běhy agenta** (první vytěží, rodič se zeptá, druhý zapíše): zápis by byl plně informovaný odpověďmi, ale vytěžení se platí dvakrát.

**Zamítnuto – čtenáře pouštět až po otázkách, nad finálním stavem.** Posuzovali by to, co opravdu zůstane, a nevznikaly by neplatné nálezy; čekalo by se ale naprázdno na konci běhu. Mechanismus proti neplatným nálezům skill už má z 19. 9. 2026 – ověřit, že nález pořád platí, a po netriviálních opravách pustit čtenáře pozůstatků znovu nad novým diffem.

**Zamítnuto – sloučit dva čtenáře do jednoho.** Uživatel se na to zeptal znovu, protože po přesunu jejich podíl na nákladech vzroste (dnes 2 %). Neobstálo: dělící čára z 19. 9. 2026 je o obsahu otázek, ne o tom, kde skill běží – „nevím, co dělat dál“ pozná jen ten, kdo přečetl dokumentaci jako celek, kdežto čtenáři pozůstatků by znalost celku **škodila**, protože by začal soudit starší dluh. Jeden agent by navíc musel přečíst celý projekt i diff, tedy víc práce než dva paralelní.

**Zrušen argument `[id session]` na úklid cizí session.** Rozhodl uživatel při prvním ostrém běhu jednou větou: *„Jakákoliv potřeba session id už je pasé, když skill pouštíme teď nově vždy přímo z té session, kterou chceme uklidit.“* Argument byl v seznamu *co platí dál* po zamítnuté cestě přes `/clear` – tam se skill pouštěl z **jiné** session než z uklízené, takže na ni musel umět ukázat. U subagenta ta potřeba zmizela celá, protože dědí session-id rodiče přes cestu ke scratchpadu.

**Oba čtenáři bez kontextu nezávisle doložili, že ta funkce nebyla hotová:** `SESSION.md` je nadepsaný „Jak se čte transcript **aktuální** session“ a označuje id ze scratchpadu za jediný spolehlivý klíč, takže u cizího id není znám slug adresáře a soubor se nenajde; „základ session“ u předevčírejší session není `HEAD` ani jeho rodič a nikde nestálo co; a kontrola průběžné aktualizace by proti takovému základu měřila prázdný interval. **Všechna tři selhání vypadají jako povedený běh** – proto by to bylo horší než chybějící funkce (`~/.claude/skills/SKILLS.md`, *Jak se píše text uvnitř*, zákaz deklarovat, co skill neumí).

**Vráceno týž den – navazování druhého běhu na hash z `done.md`.** Rozhodlo se, že druhý běh vytěží jen přírůstek od předchozího úklidu, a při prvním ostrém běhu to spadlo na tom, že **mechanismus k tomu neexistuje**: nikde nestálo, jak se z krátkého hashe udělá místo v transcriptu, a hlavně ten hash vzniká `git rev-parse --short HEAD` ve chvíli, kdy zápisy úklidu ještě commitnuté nejsou – ukazuje tedy na commit **před** nimi a jeho čas je starší než konec prvního běhu. Čára z něj nevyjde. **Uživatel proto zvolil plné vytěžení:** druhý běh je plná verifikace a agent v něm nezdědí slepá místa toho prvního. Zamítnuty obě opravy zkratky – přidat na řádek i čas (`date -Iseconds`), protože by to bylo pole navíc kvůli úspoře, která se nedá doložit, a dopočítat čas z commitu hashe (`git show -s --format=%cI`), protože ten překryv by se stejně čtl podruhé.

**Zamítnuto – zachovat číslování fází.** Nové rozdělení práce pořadí láme: čtenáře pouští rodič uprostřed toho, co je dnes práce agenta, takže čísla by přestala být pořadím běhu a skill by se podle sebe sama nedal provést bez čtení napřeskáčku. Čísla fází `/cleanup` se přitom mimo jeho vlastní soubory citují jen v **datovaných záznamech** – v `done.md` a ve starších záznamech tady –, a ty se jako historie nepřepisují: `Fáze 9` v záznamu z 25. 9. i `Fáze 0` a `Fáze 6` v záznamu z 23. 9. popisují stav, který tehdy platil.

**Doplněno týž den při zapracování zpětné vazby z prvních tří ostrých běhů – agent čte výstupy nástrojů selektivně podle jména nástroje.** Vytěžení do té chvíle bralo z transcriptu jen zprávy uživatele a textové bloky odpovědí, takže session, jejíž podstata leží ve **výsledcích volání nástrojů**, by se vytěžila naprázdno. Doloženo ostrým během nad **datovou analýzou v cizím projektu** – ne tím, kterým se ověřoval přepis skillu a který popisuje `done.md`: byla to datová analýza, kde čísla ležela ve výsledcích 26 dotazů do BigQuery a v devíti snímcích obrazovky, a prošlo to jen proto, že hlavní session každý výsledek převyprávěla v textu odpovědi včetně čísel. **Rozhodl uživatel:** čtou se výstupy `Bash`, MCP dotazů, subagentů (`Agent`, `Task`) a webových nástrojů (`WebFetch`, `WebSearch`), nečtou se `Read`, `Grep` a `Glob` – u těch je výstupem obsah souborů, který si agent přečte přímo ze zdroje. **Dělítko je, jestli výstup nese obsah, který nikde jinde není.** Zprávy subagentů do té skupiny doplnil týž den čtenář bez kontextu: první vzorec je vynechával, takže by se běh `/review` nebo `/oponent` – kde je celá hodnota právě v nich – vytěžil naprázdno. Bloky myšlení a obrázky se nečtou vůbec a patří do *Mezí běhu*. Mechanika i `jq` jsou ve `skills/SESSION.md`, *Pasti ve formátu*, protože transcript čte víc skillů než jeden.

**Zamítnuto – nechat tak a jen to hlásit jako mez.** Nestálo by to nic navíc a agent to dnes přiznával sám, jenže u datové session by se obsah opravdu ztrácel a přiznaná mez z něj nic nezachrání. **Zamítnuto – číst výstupy nástrojů celé.** Byla by to úplnost bez rozhodování, ale u velkého transcriptu mnohonásobně větší vstup – tedy přímo proti tomu, kvůli čemu se úklid do subagenta přesunul.

### 2026-09-25 – `/cleanup` se v pásmu „zvaž rozdělení“ nedělí

**Rozhodnuto 25. 9. 2026.** `skills/cleanup/SKILL.md` má po zapracování zpětné vazby z prvních tří ostrých běhů a po vypořádání nálezů čtenářů **326 řádků** (`wc -l`, 25. 9. 2026), tedy pásmo 300–500 z `skills/SKILLS.md`, *Délka a progresivní odhalení*, kde norma velí rozdělení zvážit a říct to při revizi. **Nedělí se**, a to ze dvou důvodů: přírůstek toho dne byl 17 řádků (309 → 326), takže do pásma soubor spadl setrvačností, ne novou složitostí; a jádro skillu už venku je – `agent.md`, `readers.md` a `out-of-scope.md` vznikly při přesunu do subagenta, takže v `SKILL.md` zbyl samotný postup rodiče, který se čte souvisle. (**Od 26. 9. 2026 to platí jinak, závěr ale drží:** `agent.md` i `readers.md` zanikly se zrušením subagenta a čtenářů, venku zůstaly `obligations.md` a `out-of-scope.md`. Soubor má 334 řádků, tedy pořád totéž pásmo a pořád daleko od tvrdé meze 500.)

**Cesta zpátky:** k dělení se sáhne, až se soubor přiblíží tvrdé mezi 500 řádků, a vytáhnou se z něj šablony výstupu *Fází 3, 4 a 7* a kapitola *Časté chyby*. Zamítnuto zapsat to jako úkol do `todo.md` ani jako nápad do `backlog.md` – fronta ani backlog nejsou místo pro rozhodnutí, že se něco **dělat nemá** (`~/.claude/RULES.md`, *Zapiš i to, co vědomě nemáš*), a bez tohohle zápisu by dělení někdo navrhl znovu a prošel by touž úvahou od nuly.

### 2026-09-25 – Přesun `/cleanup` do subagenta úspory nepřinesl: celek je o třetinu dražší

**Změřeno 25. 9. 2026**, den po přepisu, skriptem `skills/cleanup/scripts/cost.py` (uložen schválně – předchozí měření výš svůj skript neuložilo a chybí). Metodika je v jeho docstringu; běh se ohraničuje markerem `Úklid dokončen`, srovnává se po pásmech velikosti transcriptu.

**Srovnání v pásmu nad 1200 kB**, kde leží všech 7 ostrých běhů po přepisu (medián, proti 110 běhům před ním):

| | před | po | změna |
|---|---|---|---|
| hlavní session | 105,8 | 97,7 | **−8 %** |
| subagenti | 43,1 | 112,6 | **+161 %** |
| **celkem** | **149,9** | **200,6** | **+34 %** |
| volání hlavní session | 110 | 103 | −6 % |
| volání agentů | 113 | 281 | +149 %|
| agentů na běh | 2 | 4 | +100 % |
| délka | 44 min | 49 min | +12 % |

**Slib 80 % úspory se nesplnil a nemohl se splnit.** Pilot měřil jen *Fázi 1 a 3*, kdežto přepis nechal v rodiči celou interaktivní část – *Fáze 3 až 6*, čtyři samostatné fronty s jedním dotazem na položku. Proto volání hlavní session klesla jen o 6 %: **náklad rodiče je počet jeho volání krát jeho kontext**, a delegace ubrala volání, kterých bylo málo. Vytěžovací agent k tomu prochází transcript třikrát v surové podobě, takže agenti zdvojnásobili počet i cenu.

**Z toho plyne, kde se dá ušetřit, a kde ne:** ne u čtenářů (dřívější měření jim dává 2 % a platí to dál), ale u interaktivních smyček rodiče a u průchodů transcriptu. Podíl subagentů na celku stoupl z 31 % na 53 %.

**Rozklad po vrstvách** (7 běhů, součet 1600 jednotek, párováno na jednotlivé subagenty podle session-id a časového okna):

| vrstva | podíl | pozn. |
|---|---|---|
| hlavní session – interaktivní fáze | **46,7 %** | čtyři fronty s dotazem na položku |
| čtenáři bez kontextu | **40,8 %** | **3,1 spuštění na běh**, přestože jsou dva |
| vytěžovací agent – jádro skillu | **12,5 %** | to, kvůli čemu skill existuje |

**To, co se od skillu očekává, je osmina jeho ceny.** Dřívější údaj „čtenáři 2 % nákladů“ platil pro starý tvar, kde vytěžení dělala hlavní session a čtenáři se poměřovali s jejím obřím kontextem; po přesunu vytěžení do agenta se poměr převrátil. **Kdo se rozhoduje podle toho starého čísla, rozhodne špatně** – proto tohle stojí tady a ne jen v `todo.md`.

**Čtenář pozůstatků se pouští dvakrát až třikrát v jednom běhu**, ne jednou: jednou ve *Fázi 2*, pak znovu ve *Fázi 6* po opravách, a k tomu ho *Fáze 6* pouští znovu, „vrátil-li chybu **nebo nic**“ – přičemž prázdný výsledek je podle jeho vlastního zadání úspěch („Pokud je něco v pořádku, nepiš to“). Skill si tedy vyrobil vstup, který podle vlastní definice znamená čisto, a vyhodnocuje ho jako selhání.

**Mez měření:** 7 běhů proti 110, všechny z jednoho dne a z pásma nad 1200 kB – pro menší session po přepisu data nejsou. Vyloučen jeden běh, který skončil po 3 voláních. Čísla jsou vážený součet tokenů, ne fakturovaná částka; poměry platí, absolutní hodnoty se s cenami změní.

### 2026-09-26 – `/cleanup` se zúžil na jádro, zrušil čtenáře i subagenta a úplnost začal měřit

**Rozhodnuto 26. 9. 2026** po změření předchozího tvaru (záznam výš) a po třech nezávislých posudcích. Spouštěčem byla věta, kterou běh sám vydal: *„ze tří posudků čtenářů, které přišly jako dlouhý JSON, četl jen začátky… nedá se vyloučit, že v nepřečtené části zůstal nález“*. Uživatel na tom pojmenoval, co od skillu čeká: ověření, že se ze session opravdu všechno zapsalo – **s odškrtáváním, ne s dojmem**.

**Tři změny, každá z jiného důvodu:**

1. **Zrušeni oba čtenáři bez kontextu.** Byli **40,8 % ceny běhu** při 3,1 spuštění a posuzovali jinou otázku než tu, kvůli které se skill pouští: navazitelnost dokumentace a pozůstatky po přepisování. Třetí spuštění vznikalo pravidlem „vrátil-li chybu **nebo nic**, pusť ho znovu“, přičemž prázdný výsledek podle jejich vlastního zadání znamenal, že je čisto – skill si vyrobil vstup značící úspěch a vyhodnocoval ho jako selhání.
2. **Vytěžení se vrátilo do hlavní session.** Delegace ubrala rodičovi 8 % a přidala agenta za dvojnásobek; počet volání na tutéž práci stoupl o 51 % (110 → 166), protože agent rekonstruuje z transcriptu to, co hlavní session má v kontextu zdarma. Změřený scénář „vše v hlavní session bez čtenářů“ vyšel na 105,8 jednotky proti 115,9 se subagentem. **Rozhodlo ale hlavně to, že zmizel prostředník** – nález se nemůže ztratit převyprávěním výstupu, který nikdo nedočte.
3. **Úplnost se měří.** `scripts/extract.py` vytáhne z transcriptu **kotvy** – místa, kde uživatel něco napsal – a skill u každé vyplní stav v evidenci ve scratchpadu. Počet řádků musí sedět s počtem kotev; do `done.md` jde poměr `kotvy N/N` a povinné pole `meze`. Řádek, který se čte jako „uklizeno“, tím přestal být vydatelný nad nepřečteným transcriptem.

**Tři interaktivní fronty se slily do jedné** (*Fáze 5*). Kritérium rozhodování bylo u všech totéž a smyčky nad velkým kontextem jsou nejdražší část skillu – 46,7 %. Zdroj položky je metadatum na řádku, ne důvod k dalšímu průchodu.

**Zamítnuté varianty:**

- **Přesunout čtenáře do `/consistency`** – nejde: ten běží **před** úklidem, takže by dostal dokumentaci bez dnešního zápisu, tedy přesně to, co nemá posuzovat. Byla to původně doporučená varianta a padla na téhle premise.
- **Přesunout je do `/merge`** – věcně by to šlo, ale cena se jen přesune a session, která mergem nekončí, by kontrolu neměla vůbec.
- **Nechat subagenta a jen ho zlevnit** – dražší o 9 % a prostředník zůstává.
- **Jen přidat evidenci a zachovat celý záběr** – spolehlivost by stoupla, ale cena ne; velká mašina by zůstala velká.

**Čím se nahrazuje, co zmizelo:** mrtvé odkazy a kotvy po zápisu dál hlídá `links.py`. Věta, která zápisem přestala platit, se chytí až v příštím `/consistency` – **to je vědomě přijatá cena**, ne opomenutí. Navazitelnost dokumentace neposuzuje nikdo; kdyby se ukázalo, že chybí, patří to do `/consistency`, který čte dokumentaci tak jako tak.

**Bloky myšlení se nečtou, a není to volba.** Změřeno na šesti transcriptech: pět mělo 0 kB při desítkách až stovkách bloků, jeden 12,8 kB na 302 bloků. V transcriptu jsou zapsané prázdné, takže ten obsah tam není. Dřív to stálo v `SESSION.md` jako rozhodnutí „myšlení není závazek“, což svádělo k dojmu, že se něco čitelného vědomě přeskakuje.

**Zaniklé soubory:** `skills/cleanup/agent.md` (zadání vytěžovacího agenta) a `skills/cleanup/readers.md` (zadání čtenářů). Jádro z prvního je v `SKILL.md`, tabulka povinností v novém `obligations.md`. Stopa je tady, protože obojí se dá zkopírovat zpátky z historie gitu a vypadalo by to jako regrese.

**Co se tím rozbilo a spravilo:** test na nevypořádaná témata hlídal nadpis *Fáze 3* a fragmenty v `agent.md` – míří teď na *Fázi 5* a do `SKILL.md`, s podmínkou, že nevypořádaná témata v té frontě zůstanou **jmenovaným druhem položky**; sloučení je úspora na průchodech, ne záminka ztratit kategorii, kterou nikdo jiný nehledá.

**Cesta zpátky:** po několika ostrých bězích změřit znovu skriptem `scripts/cost.py` a porovnat se 105,8 z tohohle záznamu. Nevyjde-li úspora, je na řadě řez v *Fázi 5*, ne návrat čtenářů.


### 2026-09-26 – Kolik z transcriptu se čte, rozhoduje počet kompaktací, ne zvyk

**Rozhodnuto 26. 9. 2026**, hned po vrácení `/cleanup` do hlavní session. Otázka zněla: má smysl číst transcript z disku, když v hlavní session je konverzace v kontextu už zaplacená?

**Odpověď je „obojí, ale ne vždycky celé“, a stojí na dvou změřených faktech:**

1. **Transcript má navíc jen to, co vyhodila kompaktace.** Prošla-li session kompaktací, je v něm část, která v kontextu není – a přesně v ní bývají uzavřené dohody. Kompaktace se pozná z `isCompactSummary` a `compactMetadata`, takže to nemusí být dojem: `extract.py inventory` je počítá.
2. **Velký výstup nástroje je v transcriptu uříznutý stejně jako v kontextu.** Nese náhled a větu `Full output saved to: <cesta>`; plná verze leží v `tool-results/<id>.txt` vedle transcriptu (má to 180 session). **Transcript tedy není nadmnožina kontextu ve všem** – tuhle díru mají oba stejnou, a u session, která měřila nebo se ptala cizího systému, tam bývá celá podstata.

**Postup je proto hybridní:** inventura vždycky (kotvy, počty, kompaktace, cesty k odloženým výstupům), plný očištěný transcript **jen při kompaktaci**, jinak se konverzace projde v kontextu a inventura slouží jako checklist. Odložené výstupy se čtou cíleně tam, kde čísla nikdo nepřevyprávěl v odpovědi.

**Proč ne jen kontext:** z kontextu se **pokrytí spočítat nedá** – není nad ním index a „prošel jsem to celé“ je zase jen tvrzení. Kotvy a čísla řádků proto pokaždé vycházejí z inventury, i když se obsah bere z kontextu. Bez toho by zmizelo právě to, co se toho dne zavádělo.

**Proč ne vždycky celý transcript:** je to tentýž obsah za druhou cenu, kterou se pak platí do konce session (`~/.claude/RULES.md`, *Co vložíš do kontextu, platíš do konce session*). U session bez kompaktace je to čistá duplikace – řádově 90 tisíc tokenů navíc za nic.

**Zamítnuto rozhodovat to podle velikosti transcriptu.** Velký transcript bez kompaktace je pořád celý v kontextu, kdežto malý po dvou kompaktacích ne. Rozhoduje tedy kompaktace, ne objem – a to je jeden z mála případů, kde jde kritérium postavit na počtu, ne na úsudku.


### 2026-09-26 – Kotvy evidence se deduplikují, protože harness tentýž prompt uloží víckrát

**Zjištěno prvním ostrým během nového `/cleanup`** a opraveno hned, protože na počtu kotev stojí celá záruka úplnosti: nesedí-li, poměr `N/N` nic netvrdí. Transcript ukládá tentýž uživatelův vstup dvakrát ve dvou různých případech:

1. **Zpráva poslaná uprostřed odpovědi** je tam jako `queue-operation` (při zařazení) a jako `attachment` typu `queued_command` (při doručení).
2. **Rozepsaný prompt** se uloží i ve stavu před doplněním, a to **pod jiným `promptId`** – podle id se tedy rozlišit nedá. Kratší verze je prefixem té delší.

**Deduplikuje se proto dvakrát:** podle normalizovaného textu (případ 1) a zahozením kotvy, která je prefixem jiné (případ 2). **U prefixů je to volba s rizikem** – napíše-li uživatel dvě samostatné zprávy, z nichž druhá začíná slovy té první, první se zahodí. Přijato vědomě: obsahově je delší nadmnožinou kratší, takže se neztratí zadání, jen jedna kotva v evidenci. Opačná chyba je horší – dva řádky na jednu větu znamenají poměr, který nikdy nesedne, a z čísla se stane šum.

**Zamítnuto rozlišovat podle `promptId`** – ověřeno, že rozepsaná a hotová verze mají různé. **Zamítnuto počítat kotvy až z `filter` výstupu**, kde jsou obě verze taky: dedup patří k sestavení seznamu, ne k jeho čtení.

**Přerušení běhu (`[Request interrupted by user]`) kotva není** – čte se jako věta, ale je to záznam o akci, ne obsah k zapsání.
