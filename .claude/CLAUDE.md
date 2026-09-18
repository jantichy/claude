# Konfigurace Claude Code

Moje osobní konfigurace Claude Code – pravidla, skilly, hooky a status line, sdílená pro inspiraci.

- **Slug:** `claude`
- **Repozitář:** https://github.com/jantichy/claude

## Výjimky z obecných pravidel

- **Blok metadat je tady, ne v kořenovém `CLAUDE.md`**, jak jinak velí `~/.claude/STRUCTURE.md`. Kořenový soubor je uživatelský a rozbaluje se do každé session v každém projektu – metadata tohohle repozitáře tam nepatří, mátla by v cizím projektu.
- **`/attack` ani `/release` se tu nikdy nepouštějí.** Repozitář je konfigurace, ne aplikace – není co spustit ani kam nasadit. Životní cyklus tady končí `/cleanupem`. Zapsáno schválně, ne odvozeno (`~/.claude/RULES.md`, *Zapiš i to, co vědomě nemáš*).
- **Tenhle repozitář má `todo.md`, `backlog.md`, `done.md` i `decisions.md` v `~/Dev/context/`**, ne u sebe. Platí to pro každý skill, který do nich zapisuje a zároveň se tu pouští – `/review`, `/oponent`, `/consistency`, `/cleanup`, `/implement` a `/skill`. (`/attack` a `/release` se tu nepouštějí vůbec, viz výš.) **U `/skill` to platí bezvýhradně**, protože jako jediný nikde jinde běžet nemůže – spravuje skilly, a ty jsou jen tady. A **neptej se na to pokaždé znovu**:

  | Co | Kam | Jak |
  |---|---|---|
  | odložený nález, zaparkovaný bod | `~/Dev/context/todo.md` | **do sekce `## Claude`** – ta je tam právě pro tenhle repozitář |
  | nezávazný nápad, o kterém se nerozhodlo | `~/Dev/context/backlog.md` | tamtéž do `## Claude`; hranici proti todo drží `~/.claude/STRUCTURE.md`, *`backlog.md`* |
  | rozhodnutí, zamítnutá varianta, vědomá mezera | `~/Dev/context/decisions.md` | tamtéž do `## Claude`; týká-li se rozhodnutí **jednoho skillu**, patří rovnou do jeho `SKILL.md` k místu, kde platí – tam ho příště najde ten, kdo ho potřebuje |
  | záznam dokončeného průchodu (`## Průchody životním cyklem`) | `~/Dev/context/done.md` | **vždy**, bez odchylky – čtenáře i důvod drží `~/.claude/STRUCTURE.md`, *`done.md`*. Dřívější výjimka „u `/review` jen když má smysl ho pak číst“ padla 8. 9. 2026 |

  **První tři řádky jdou do sekce `## Claude`**, ne do doménových – ty patří tématům knowledge base (analytics, text, brand…), kdežto tohle je práce na konfigurační vrstvě. Ta sekce má v záhlaví napsáno, že hashe commitů v ní pocházejí odsud, takže se u jednotlivých položek neopakuje.

  **Záznam průchodu je výjimka:** jde do `## Průchody životním cyklem`, což je samostatná sekce vedle `## Claude`, a hash v něm se kvalifikuje (`~/.claude@2acbdbd`). Sdílí ji totiž oba repozitáře, takže holý hash by tam nešlo přiřadit ke stromu – `~/.claude/STRUCTURE.md`, *`done.md`*, to označuje za horší než hash žádný.

  Je to jediné místo, kde struktura tohohle repozitáře sahá ven; důvod je, že fronta rozdělané práce a deník rozhodnutí do **veřejného** repozitáře nepatří, a konfigurační vrstva je zároveň téma, které ta znalostní báze už drží. **Pozor: platí to jen pro tenhle repozitář** – proto to stojí tady v projektovém souboru, a ne v kořenovém `CLAUDE.md`, který se rozbaluje do každé session v každém projektu.
- **`docs/` neexistuje.** Repozitář není vyvíjený projekt, ale konfigurace; `todo.md`, `backlog.md`, `done.md`, `decisions.md` ani `rules.md` nemá a nezakládají se.

## Instrukce pro tenhle repozitář

Projektové instrukce pro práci **v tomhle repozitáři**. Načítají se jen tady, na rozdíl od `~/.claude/CLAUDE.md`, který je uživatelský a jde do každé session v každém projektu.

@~/.claude/skills/SKILLS.md

- **Norma výš platí pro každou cestu ke změně skillu:** ruční úpravu, `/skill` i cizí nástroj typu `skill-creator` nebo `superpowers:writing-skills`. Ty mají vlastní představu o tvaru a prosadí ji, když jim nic neřekneš; tenhle řádek je to, co jim ji přebíjí (`~/.claude/RULES.md`, *Přednost pravidel*). Postup zakládání, revize a rušení drží `/skill`, ne norma.
- **Každý skill má dvě README.** Vlastní `skills/<name>/README.md` psané pro člověka zvenčí, na které se posílá odkaz, a k tomu jeden odstavec v kořenovém `README.md`, jehož nadpis na ně odkazuje. Tvar obojího drží `skills/SKILLS.md`, *README skillu*, a vynucují ho testy. Když skill přidáš nebo zásadně změníš jeho chování, aktualizuj obojí rovnou jako součást té změny – nečekej na vyžádání.

## Kontrakt příkazů

Kontrakt příkazů (`~/Dev/context/coding/quality.md`). Průběžná kontrola ho tady najde v `.claude/CLAUDE.md` a příkazy spouští v kořeni repozitáře.

- typecheck: swiftc -typecheck -warnings-as-errors skills/*/*.swift
- lint: shellcheck -x --severity=info ./*.sh skills/*/*.sh githooks/* && ruff check --isolated --select F,E9,C901 --config 'lint.mccabe.max-complexity = 10' skills/*/*.py skills/*/scripts/*.py tests/*.py
- test: python3 -m unittest discover -s tests
- build: -
- e2e: -
- audit: -
- coverage: -
- mutation: -
- dev: -

**Pomlčky jsou rozhodnutí, ne díra.** `dev` mezi nimi stojí schválně: `/attack` se tu nikdy nepouští (viz *Výjimky z obecných pravidel* výš), takže není co zvedat – a chybějící klíč se od vědomé pomlčky nepozná. Repozitář nemá manifest závislostí, nic se z něj nebuildí ani nenasazuje a není tu aplikace, kterou by šlo projít; `coverage` a `mutation` nad sadou, která z devadesáti procent testuje Markdown, měří délku textu, ne sílu testů. Bez pomlčky by je `/review` i CI hlásily jako nezkontrolované kroky – tedy jako trvalý šum místo informace (`~/Dev/context/coding/quality.md`, *Kontrakt příkazů*).

`shellcheck` běží se `--severity=info`, ne se `--severity=style`: stylové nálezy jsou preference a kontrola, která padá na preferenci, se obchází. **Ze stejného důvodu má `ruff` jen `--select F,E9,C901`** – nedefinovaná jména, nepoužité importy, syntaktické chyby a cyklomatická složitost, tedy vady a jeden měřitelný práh, ne názory. `C901` je tu od 8. 9. 2026 s prahem 10 podle `~/Dev/context/coding/quality.md`. Do té doby se neměřila vůbec a 5 funkcí ho překračovalo, nejvíc `progress.py` s 19. Práh se **nesnižuje kvůli tomu, že překáží** – to smí jen člověk a se zápisem do rozhodnutí.

Výchozí sada by tu hlásila pořadí importů a závorky navíc. `--isolated` k tomu zajistí, že se nechytí cizí konfigurace odněkud z domovského adresáře. Python přibyl do repozitáře 6. 9. 2026 se skripty `/compose`.

**Od 7. 9. 2026 lint kryje i `tests/`** – je to největší Python v repozitáři a nekontroloval ho nikdo, přestože je to zároveň jediná vrstva, která tu něco doopravdy vynucuje. Běh testů sám chytí syntaktickou chybu, ale ne nepoužitý import ani překlep ve jménu uvnitř větve, která se zrovna nevykonala.

`test` pokrývá tyhle vrstvy. **Počty se tu schválně neuvádějí** – ani vrstev, ani testů: rozejdou se s prvním doplněným scénářem a nikdo je nepřepočítává. Kolik jich je, řekne `python3 -m unittest discover -s tests`:

- **`tests/test_skills.py` – meta-testy nad konfigurací.** Hlídají tyhle skupiny:

  - **Hlavičku a odkazy:** že hlavička parsuje a sedí s adresářem, že `description` říká, kdy se skill použije, a vejde se do 1024 znaků, že `allowed-tools` je vyplněné (chybějící pole není „neurčeno“, ale nejširší možná sada včetně připojených MCP serverů) a že vyjmenované MCP nástroje plugin na disku opravdu nabízí, že režim popsaný v těle je i v `argument-hint`, že odkazy na soubory vedou někam a odkaz na sekci míří na skutečný nadpis – včetně vnitroskillových odkazů na vlastní fáze i kroky, písmenných podkroků a celých výčtů čísel –, a že se skilly odkazují na kroky životního cyklu, ne na jejich vnitřky – **včetně vedlejších souborů skillu**, kde se to dřív nekontrolovalo vůbec a `skills/ptydepe/terms.md` jich nasbíral osm.
  - **Soulad s normou `skills/SKILLS.md`:** povinné sekce a jejich pořadí včetně toho, kde smí stát `Časté chyby`, odkaz na `skills/PREFLIGHT.md`, závěrečný verdikt, mez délky, zákaz odkazu dovnitř fáze jiného skillu a povinnou sekci `Jak je to postavené uvnitř` u skillu s vlastními skripty. Vynucuje se to tím, že **seznam `MIGRATION` musí přesně sedět se skutečností**, takže opravený a nevyškrtnutý skill shodí testy stejně jako regrese.
  - **Nosné části:** že `/review` má fázi ověřování nálezů, `/cleanup` fázi na nevypořádaná témata, že zadání specialistů `/review` nesou `severity` a `basis`, že datovaný záznam jmenuje `date +%F`, že žádný skill neopisuje pořadí kroků cyklu šipkami místo odkazu do `RULES.md` a že `.claude/run/` je v `.gitignore`.
  - **Hranici paušálního kontextu:** že se `STRUCTURE.md` ani `skills/LIFECYCLE.md` nevrátí mezi `@import`y v globálním `CLAUDE.md`, že příprava skillu říká, kdy si je načíst, a že číslované odrážky v `LIFECYCLE.md` jmenují tytéž kroky jako rámeček v `RULES.md`.
  - **Šablony výstupu:** že každý blok kódu, jehož obsah jde do konverzace, nese pokyn vypsat ho jako Markdown – s jmenovitým seznamem bloků, které se místo toho zapisují do souboru, a ten **musí přesně sedět**.
  - **README skillů:** že každý skill má `README.md` s povinnými sekcemi ve správném pořadí, instalací psanou jako pokyn pro Clauda, rámečkem cyklu a hromadnou instalací u kroků cyklu (a bez nich mimo něj), pojmenovanými všemi režimy z `argument-hint` včetně výchozího, dodrženou mezí délky a relativními odkazy, které vedou na existující soubor. Kořenové README zná každý skill a nezná žádný zmizelý.
  - **Kanonický tvar autocommitu:** že projektový `CLAUDE.md` tohohle repozitáře nese přepínač pod `## Autocommit` i s importem pravidel ze skillu, že nestojí pod zastřešující sekcí a že se definice mechanismu nevrátila do globálního `CLAUDE.md`.
  - **Skripty ve skillech** (`skills/*/*.py` i `skills/*/scripts/*.py`).

  Nad tím vším stojí **mutační testy**, které poškodí vzor a ověří, že kontrola nález opravdu nahlásí. Kroky životního cyklu se čtou z `RULES.md`, povinné sekce README z normy a kontrakt příkazů se parsuje týmž výrazem jako `verify.sh` – žádný z těch seznamů nestojí v testu natvrdo.

  **Proč která kontrola existuje, drží docstring toho testu, ne tenhle výčet.** Odůvodnění opsané na dvě místa se rozejde a ta trvanlivější kopie bývá ta horší: jedna oprava změní chování skillu a druhé místo dál vysvětluje kontrolu selháním, které už nastat nemůže. Zdejší popis proto říká jen *co* se hlídá; *proč* si přečti u testu.
- **`tests/test_verify.py` – regresní testy průběžné kontroly.** Scénáře nad dočasným repozitářem s přesměrovaným `HOME`:

  souhlas a jeho platnost pro celý repozitář včetně worktree i přes symlink v cestě, rozdíl mezi `exit 1` a `exit 2`, druhý pokus po zablokování, shoda otisku, chybějící nástroj, díra v kontraktu, pomlčka, vypnutá kontrola, otisk nad neverzovaným adresářem i nad rozpracovaným souborem, `## Kontrakt příkazů` v bloku kódu i v HTML komentáři, dvě sekce téhož jména, neuzavřené ohraničení, upovídaný úspěšný krok s uříznutým výstupem, kontrakt v `.claude/`, klíč `cwd` včetně cesty mimo projekt, zámek proti souběhu, `--revoke` s tečkou i lomítkem. Od 14. 9. 2026 k tomu vazba souhlasu na kontrakt (podadresář s vlastním `CLAUDE.md`, změněný kontrakt, starý formát bez otisku, worktree jiné větve), vydání souhlasu jen z terminálu, čtení Markdownu podle CommonMarku a pojistka, že stav běhu nejde přesměrovat přes `XDG_STATE_HOME`.

  Je to spolu s git hookem a CI jedno z míst konfigurace, která něco doopravdy vynucují, takže jeho tichá regrese je nejdražší, jaká tu může nastat. Používají jen stdlib – kontrola, která si žádá instalaci balíčku, se v cizím prostředí neprojeví jako nález, ale jako rozbitý nástroj, a ten se obchází.
- **`tests/test_hooks.py` – regresní testy vrstev, které něco vynucují mimo model.** Nad nimi stojí kontrola **registru obcházení** `BYPASS.md`: každá vrstva, která běží automaticky – hook ze `settings.json`, soubor v `githooks/`, workflow v `.github/` –, v něm musí mít řádek, a seznam se čte z disku, ne z výčtu v testu. Registr, který zestárne, je horší než žádný: tváří se jako úplná mapa, ale nová vrstva v něm chybí. Hlídá se i to, že u každého `accepted` stojí důvod, ne jen slovo. Scénáře nad dočasným repozitářem hlídají **git hook na zprávu merge commitu**: odmítnutí defaultní zprávy v české i anglické podobě, komentáře v `COMMIT_EDITMSG`, skutečný `git merge --no-ff`, a proti tomu všechno, co projít musí – vlastní zpráva, aktualizace rozdělané větve z `main`, merge po `git pull`, zpráva jen zmiňující slovo merge. K tomu delegace na lokální `.git/hooks/commit-msg`, kterou globální `core.hooksPath` jinak vypne. `githooks/commit-msg` běží nad **každým** repozitářem na stroji, takže falešný poplach tu neblokuje jeden skill, ale běžnou práci v cizím projektu – a člověk si ho pak vypne, čímž přestane hlídat cokoliv. Proto se testují oba nebezpečné směry, ne jen ten zjevný.

  K tomu testy nad **nasazením a CI**: že `core.hooksPath` na hook doopravdy míří (hook, který nikdo nevolá, funguje při přímém zavolání úplně stejně jako ten nasazený) a že workflow v `.github/` pouští klíče z *Kontraktu příkazů* a neopisuje si jejich příkazy. **Ne všechny** – `dev` je watch server, který nikdy neskončí, a `cwd` není příkaz; množinová rovnost s kontraktem by v prvním projektu s `dev` vyrobila falešný poplach, takže se kontroluje podmnožina. Od 14. 9. 2026 k tomu kontrola, že je `verify.sh` vůbec zaregistrovaný jako `Stop` hook v `settings.json` a že jeho timeout pokryje tři kroky – ztráta té registrace je nejtišší selhání celé vrstvy, protože nic nespadne, jen se přestane kontrolovat.

- **`tests/test_statusline.py` – regresní testy status line, tedy kódu, který běží nad cizím repozitářem bez souhlasu.** Status line se překresluje po každé odpovědi, permission systém na ni nesahá a stojí v adresáři, který si uživatel nevybral. Git přitom umí spustit program podle konfigurace toho repozitáře: `filter.<name>.clean` se volá pokaždé, když potřebuje obsah pracovního souboru – tedy i při `git diff --name-only`, kterým se počítaly změny –, a jméno filtru si volí ten, kdo config napsal, takže ho nejde přebít `-c` přepínačem. Doloženo 14. 9. 2026 spuštěním nad návnadou: status line vypsala normální řádek a zároveň spustila cizí příkaz.

  Testují se oba směry: že se program nespustí a že se nad běžným repozitářem nespustí falešný poplach, protože zmizelý počet změn je přesně ta funkce, kvůli které status line existuje. Nad tím stojí mutační test, který vyřízne filtry z blacklistu a ověří, že se pak cizí příkaz opravdu spustí – bez něj by hlavní test zůstal zelený i tehdy, kdyby marker nevznikal z docela jiného důvodu. K tomu od 14. 9. 2026 šířka pruhu využití v obou krajních hodnotách: BSD `seq 1 0` počítá dolů, takže se nula bloků kreslila jako dva.
- **`tests/test_compose.py` – regresní testy generátorů archivu.** Skripty `/compose` přepisují archiv textů v `~/Dev/context/archive/`, ze kterého se pak destiluje znalostní báze autorova psaní. Chyba v nich se neprojeví jako pád, ale jako archiv, který vypadá v pořádku a není: chybí příspěvky, je rozbitá diakritika, nebo tweet nese text jiného tweetu. Testují se proto tichá místa: oprava mojibake ve facebookovém exportu (oba směry, protože oprava, která zkazí správný text, je horší než neopravená), vynechávání čistých retweetů, párování plných textů dlouhých tweetů a od 14. 9. 2026 i chybějící `note-tweet.js` a bluesky post bez `createdAt` – dva vstupy, na kterých generátor spadl dřív, než zapsal první soubor, takže jeden vadný záznam zlikvidoval celý archiv.

  **Párování odhalilo skutečnou vadu** (14. 9. 2026): párování hledalo plný text v okně ±2 s a nekontrolovalo, komu patří, takže tweet bez vlastního dlouhého textu mohl sebrat sousedův. Ve stávajícím exportu se to neprojevilo – regenerace opraveným generátorem dala tělo shodné se všemi devatenácti ročníky archivu –, ale scénář je reálný a testem doložený. `parse_bluesky.py` se netestuje: potřebuje `cbor2`, a kontrola, která si žádá instalaci balíčku, se v cizím prostředí neprojeví jako nález, ale jako rozbitý nástroj.
- **`tests/test_transcript.py` – regresní testy skriptů `/transcript`, zatím jen tam, kde hrozí ztráta dat.** Vstupem téhle vrstvy jsou nahrávky, které většinou nejde pořídit znovu, takže chyba v ní neznamená vadu nástroje, ale ztracený podklad – a `ffmpeg -y` to udělá mlčky s návratovým kódem 0. Oba scénáře nastaly doopravdy 14. 9. 2026: pojistka proti přepsání vlastního vstupu porovnávala **řetězce cest**, takže `./rec.wav` a `rec.wav` prošly jako různé soubory a z třicetisekundové nahrávky zbylo 4,6 s; a kontrola „výstupy už existují“ neznala příponu `wav`, takže existující nahrávku přepsala i ve výchozím režimu `stop`. **Od 14. 9. 2026 se pojistka ověřuje na spuštěném skriptu, ne na opisu jeho podmínky.**

  Do té doby tu běžela kopie té podmínky plus kontrola, že ve skriptu zbyl řetězec `-ef` – a ta dvojice nechytila nic: vyřazení podmínky ve skriptu nechalo všech 6 testů zelených, protože hlídaný řetězec v souboru zůstal. Skutečný běh chce whisper a model o velikosti gigabajtu, takže se obojí podstrčí, a nad tím stojí mutační test, který pojistku vyřadí a ověří, že se zdroj opravdu zničí. `ffmpeg` se nevyžaduje – kde není, testy se přeskočí nahlas.

  **Od 14. 9. 2026 k tomu přibylo přiřazování mluvčích v `merge.py`** – nejtišší vada celého skillu, protože špatně přiřazená replika vypadá v přepisu stejně věrohodně jako správná. Skript ji řeší dvěma prahy a raději nechá mluvčího prázdného, než aby hádal; testy hlídají oba **zvlášť**. To rozlišení tam nebylo od začátku: první verze shazovala oba prahy naráz a scénář „55:45“ přičítala `MIN_MARGIN`, jenže ten padá na `MIN_RATIO` – druhý práh tak nehlídal nikdo a jeho vypnutí neshodilo jediný test.

- **`tests/test_cleanup.py` – regresní testy kontroly odkazů, kterou `/cleanup` pouští před čtenáři bez kontextu.** Skript `skills/cleanup/scripts/links.py` tam existuje kvůli pravidlu nula: rozbitý odkaz a kotva bez nadpisu jsou mechanické vady a hledat je modelem je nejdražší možná cesta. Testují se oba směry – že nález opravdu vznikne, i že nevznikne falešný poplach nad blokem kódu, protože šablony výstupu ve skillech začínají řádkem `## Úklid dokončen` a ukázky nesou zástupné symboly; kontrolu, která křičí na správný text, si člověk vypne. Nad tím stojí mutační test, který vyřadí vynechávání bloků kódu a ověří, že se falešný poplach opravdu dostaví.

- **`tests/test_next.py` – regresní testy skriptů `/next`, které zjišťují živé session a stav větví.** `/next` podle jejich výstupu rozhoduje, jestli úkol v rozdělané větvi nabídne, nebo skryje, a obě chyby jsou tiché: mrtvá session vydávaná za živou schová zapomenutou práci navždy, živá vydávaná za mrtvou nabídne druhé session úkol, na kterém už dělá první. Hlídá se proto záznam po spadlém procesu, větev z posledního záznamu transcriptu, chybějící registr jako chyba, ne prázdný seznam, stavy větve (`occupied`, `abandoned`, `uncertain`, `empty`) a čtení plánu a kol z `todo.md`.

`typecheck` tu **dlouho stála pomlčka** s odůvodněním, že repozitář je konfigurace, ne program. To přestalo platit ve chvíli, kdy k `/invoicing` přibyl `calendar.swift` – od té chvíle tu ležel program, který nečetla žádná kontrola, a překlep v něm by se poznal až uprostřed ostré fakturace. Dnes proto `typecheck` pouští `swiftc -typecheck -warnings-as-errors` nad všemi swiftovými skripty ve skillech – **`-warnings-as-errors` schválně**, protože `~/Dev/context/coding/quality.md` má u přísnosti překladače práh „žádné varování“ a bez toho přepínače ho nevynucoval nikdo: varování by prošlo a kontrola by zůstala zelená (na Python ve `skills/` je test v `tests/`, ne tahle kontrola); běží kolem dvou vteřin a nic neinstaluje, protože Swift je na macOS součástí vývojářských nástrojů.

**Kdyby Swift z repozitáře jednou zmizel, vrať pomlčku**, ne prázdný řádek: chybějící klíč hook po každé odpovědi hlásí jako nezkontrolovaný krok, a to je trvalý šum místo informace.

## Review

Nálezy vyhodnocené jako „neopravovat“. Při dalším běhu se neuvádějí, dokud se
nezmění kód, kterého se týkají.

- **2026-09-14** · `2ca14c5` · *Pyannote načítá diarizační modely jako pickle a ty nejdou připnout ani ověřit* (zdroj: review, podklad: OWASP – integrita dat, zranitelné závislosti): Riziko je skutečné – pickle znamená spuštění kódu při načtení –, ale zavřít ho nejde bez toho, aby kontrola přestala být ověřitelná. Modely stahuje `huggingface_hub` uvnitř pyannote, ne zdejší kód, a `Pipeline.from_pretrained` revizi jako parametr nenabízí; „oprava“ by tedy byla neověřená domněnka o cizím API. Čím se to nahrazuje: whisper modely **jsou** připnuté na revizi (`common.sh`) a jsou to data pro whisper.cpp, ne spustitelný kód, takže jejich podvržení dá špatný přepis, ne cizí kód. Diarizační repozitáře jsou gated – vyžadují ruční souhlas s licencí u známého autora – a celý diarizační průchod je volitelný, běží jen na výslovné přání. Zruší se, jakmile pyannote začne umět revizi předat, nebo jakmile modely přejdou na safetensors.
  - Lokace: skills/transcript/diarize.py (`Pipeline.from_pretrained`), skills/transcript/common.sh (`DIARIZE_MODEL`)

- **2026-09-14** · `2ca14c5` · *CI spouští kontrakt příkazů z cizího pull requestu* (zdroj: review, podklad: OWASP – integrita dat): Přesně to CI dělá a jinak by nekontrolovalo nic. Dopad je přitom omezený týmiž fakty jako u nálezu o nepřipnutých akcích: repozitář nemá jediný secret, `default_workflow_permissions` je `read`, `can_approve_pull_request_reviews` je `false` a runner je efemérní – cizí kód nemá co ukrást a může leda podvrhnout výsledek vlastní kontroly. Čím se to nahrazuje: `fork-pr-contributor-approval` je nastavené na `first_time_contributors`, takže první PR od cizího člověka nespustí nic bez ručního schválení. Zbývá vědomě přijaté riziko, že přispěvatel, který už jednou prošel, pustí workflow bez schválení. Zruší se zpřísněním na `all_external_contributors`, jakmile do repozitáře přijde první cizí PR – do té doby je to nastavení proti nikomu.
  - Lokace: .github/workflows/verify.yml (`on: pull_request`, krok „Spusť kontrakt příkazů“)

- **2026-09-14** · `fd75365` · *Parsery cizích exportů nemají limit na délku ani hloubku* (zdroj: review, podklad: OWASP – neošetřený vstup): Vstupem nejsou cizí data, ale **vlastní** exporty z účtů autora, které si sám stáhl. Nejhorší dopad je `RecursionError` nebo vyčerpaná paměť, tedy pád skriptu nad souborem, který si člověk právě vyexportoval – ne spuštění kódu ani únik dat. Čím se to nahrazuje: skripty se pouštějí ručně a jejich výstup se porovnává s archivem, takže se pád pozná okamžitě. Zruší se, jakmile by parser měl číst export od někoho jiného.
  - Lokace: skills/compose/scripts/gen_twitter_md.py, skills/compose/scripts/gen_bluesky_md.py (`json.loads`)

## Autocommit

Autocommit je zapnutý.

@~/.claude/skills/autocommit/autocommit.md
