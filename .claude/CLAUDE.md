# Konfigurace Claude Code

Moje osobní konfigurace Claude Code – pravidla, skilly, hooky a status line, sdílená pro inspiraci.

- **Slug:** `claude`
- **Struktura:** root
- **Repozitář:** https://github.com/jantichy/claude

## Výjimky z obecných pravidel

- **Blok metadat je tady, ne v kořenovém `CLAUDE.md`**, jak jinak velí `~/.claude/STRUCTURE.md`. Kořenový soubor je uživatelský a rozbaluje se do každé session v každém projektu – metadata tohohle repozitáře tam nepatří, mátla by v cizím projektu.
- **`/attack`, `/release` ani `/evaluate` se tu nikdy nepouštějí.** Repozitář je konfigurace, ne aplikace – není co spustit, kam nasadit, a tedy ani žádný provoz, který by šlo vyhodnotit. **Posledním krokem osy, na který se tu dojde, je `/implement`**; kontrolní kroky se pouštějí dál a běh uzavírá `/cleanup` a po něm `/merge`, stojí-li práce na větvi – spouštěčem obou není pozice v cyklu, ale konec session, respektive pokyn uživatele. Zapsáno schválně, ne odvozeno (`~/.claude/RULES.md`, *Zapiš i to, co vědomě nemáš*).
- **Standardní soubory leží v kořeni, ne v `docs/`** – režim `root` podle `~/.claude/STRUCTURE.md`, *Dva režimy umístění*. Repozitář není vyvíjený projekt, ale konfigurace, takže by `docs/` byl prázdný obal nad čtyřmi soubory. `rules.md` tu není a nezakládá se: pravidla téhle vrstvy jsou samy jejím obsahem, ne meta-vrstvou nad ním.
- **Repozitář je veřejný, takže `todo.md`, `backlog.md`, `done.md` a `decisions.md` píšeš pro cizí oči.** Do konce září 2026 ležely v soukromém `~/Dev/context/` právě proto; od 20. 9. 2026 jsou tady a tu ochranu musí nahradit pravidlo. **Hranice vede mezi strukturou a obsahem.** Struktura veřejná je a `README.md` ji sám píše – že analytické know-how leží v `context/analytics/`, autorovy články v `context/archive/` a jeho styl psaní v `context/compose/`, se smí napsat a odkazovat se na to. **Konkrétní obsah veřejný není:** jméno klienta nebo organizace (tedy i to, že `context/organizations/` drží zrovna tenhle profil), sazba a obchodní údaj, osobní údaj, detail přístupu ke klientskému systému, jméno klientského projektu nebo domény a know-how, které se prodává.

  **Platí to na každý zápis, ne na ten první.** Úkol vzniklý při práci pro klienta se zapisuje tak, aby popsal *co* se má v konfigurační vrstvě udělat, ne *u koho* se to ukázalo: „u jednoho projektu chyběl kontrakt příkazů“, ne jméno toho projektu. Potřebuje-li položka konkrétní klientský kontext, aby dávala smysl, patří celá do `~/Dev/context/todo.md` – tam se nic nezveřejňuje.

## Instrukce pro tenhle repozitář

Projektové instrukce pro práci **v tomhle repozitáři**. Načítají se jen tady, na rozdíl od `~/.claude/CLAUDE.md`, který je uživatelský a jde do každé session v každém projektu.

**Norma tvaru skillů je `~/.claude/skills/SKILLS.md` – odkaz, ne import.** Načti si ji, jakmile se chystáš sáhnout na kterýkoliv `SKILL.md` nebo `README.md` skillu, nebo nějaký zakládat či rušit; neopírej se o paměť. Paušálně se neimportuje, protože je to 42 kB, která by šla do každé session v tomhle repozitáři včetně těch, kde se žádného skillu nedotkneme (`~/.claude/RULES.md`, *Co vložíš do kontextu, platíš do konce session*). Odkaz drží dvě vrstvy: `/skill` si normu čte celou ve své přípravě a `tests/test_skills.py` ji vynucuje strojem, takže skill, který se od ní odchýlí, neprojde průběžnou kontrolou.

- **Norma platí pro každou cestu ke změně skillu:** ruční úpravu, `/skill` i cizí nástroj typu `skill-creator` nebo `superpowers:writing-skills`. Ty mají vlastní představu o tvaru a prosadí ji, když jim nic neřekneš; tenhle řádek je to, co jim ji přebíjí (`~/.claude/RULES.md`, *Přednost pravidel*). Postup zakládání, revize a rušení drží `/skill`, ne norma.
- **Každý skill má dvě README.** Vlastní `skills/<name>/README.md` psané pro člověka zvenčí, na které se posílá odkaz, a k tomu jeden odstavec v kořenovém `README.md`, jehož nadpis na ně odkazuje. Tvar obojího drží `skills/SKILLS.md`, *README skillu*, a vynucují ho testy. Když skill přidáš nebo zásadně změníš jeho chování, aktualizuj obojí rovnou jako součást té změny – nečekej na vyžádání.

## Co do `RULES.md` nepatří

`~/.claude/RULES.md` drží **obecná pravidla práce** a jde do každé session, takže každá věta v něm stojí kontext všude. Než do něj něco zapíšeš, projdi test – vyhrává první kritérium, které sedí:

1. Říká, **co smí stát** v konkrétním souboru v `docs/`? → `~/.claude/STRUCTURE.md`
2. Platí obecně pro skilly? → `~/.claude/skills/SKILLS.md`
3. Popisuje **rozhraní kroku životního cyklu**? → `~/.claude/skills/LIFECYCLE.md`; obecné pravidlo o přeskakování zůstává v `RULES.md`
4. Jmenuje konkrétní skill nebo popisuje jeho vnitřek? → do toho skillu
5. Platí jen při určité činnosti – zjišťování z dat (`~/.claude/EVIDENCE.md`), delegaci na agenty (`~/.claude/DELEGATION.md`), kódu, webu, textu, vizuálu či měření (doména v `~/Dev/context/`)? → tam, a v `RULES.md` nanejvýš jednořádkový spouštěč
6. Platí jen v jednom repozitáři? → jeho `CLAUDE.md`, *Výjimky z obecných pravidel*
7. Nic z toho → `RULES.md`

**K pravidlu jen jedna věta pointy** (`~/.claude/RULES.md`, *K pravidlům ukládej i „proč“*); datum, incident a měření patří do commitu nebo `decisions.md`. Velikost `RULES.md` i součtu paušálně načítaných souborů hlídá test v `tests/test_size.py` – když spadne, uvolni místo nebo pravidlo přesuň, mez nezvedej mimochodem.

## Kontrakt příkazů

Kontrakt příkazů (`~/Dev/context/coding/quality.md`). Průběžná kontrola ho tady najde v `.claude/CLAUDE.md` a příkazy spouští v kořeni repozitáře.

- typecheck: swiftc -typecheck -warnings-as-errors skills/*/*.swift
- lint: shellcheck -x --severity=info ./*.sh skills/*/*.sh githooks/* && ruff check --isolated --select F,E9,C901 --config 'lint.mccabe.max-complexity = 10' ./*.py skills/*.py skills/*/*.py skills/*/*/*.py tests/*.py
- test: python3 -m unittest discover -s tests
- build: -
- e2e: -
- audit: -
- coverage: -
- mutation: -
- dev: -

**Pomlčky jsou rozhodnutí, ne díra.** `dev` mezi nimi stojí schválně: `/attack` se tu nikdy nepouští (viz *Výjimky z obecných pravidel* výš), takže není co zvedat – a chybějící klíč se od vědomé pomlčky nepozná. Repozitář nemá manifest závislostí, nic se z něj nebuildí ani nenasazuje a není tu aplikace, kterou by šlo projít; `coverage` a `mutation` nad sadou, která z devadesáti procent testuje Markdown, měří délku textu, ne sílu testů. Bez pomlčky by je `/review` i CI hlásily jako nezkontrolované kroky – tedy jako trvalý šum místo informace (`~/Dev/context/coding/quality.md`, *Kontrakt příkazů*).

**Co která vrstva hlídá, proč jsou prahy tam, kde jsou, a proč se nesnižují, drží [`tests/README.md`](../tests/README.md).** Sáhni tam, než změníš některý příkaz výš nebo než začneš snižovat práh, který překáží; při běžné práci ho nepotřebuješ. Změna příkazu v kontraktu si navíc vyžádá nový souhlas průběžné kontroly z terminálu, takže práh nejde snížit tiše.

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
