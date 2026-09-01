---
name: project
description: Skill se použije, když uživatel zadá "/project", nebo chce založit nový projekt v čistém adresáři či přenastavit už existující projekt (metadata projektu a jejich propsání do Repository details na GitHubu, git, worktree layout, standardní struktura docs/, autocommit, autoprompt, paměťová politika, typ projektu, doménové checklisty). Interaktivní wizard, který se ptá krok po kroku.
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion]
---

# Project

## Co skill dělá

Interaktivně nastaví projekt v aktuálním adresáři a zapíše vše do projektového `CLAUDE.md`. Funguje ve dvou režimech:

- **Nový projekt** – čistý adresář, všechno se zakládá od nuly.
- **Existující projekt** – zjistí se aktuální stav a nabídne se, co dorovnat na zvolené preference. Nic se nepřepisuje naslepo.

Skill je **opakovatelný**. Druhý běh nad hotovým projektem má projít bez zásahu a slouží jako verifikace.

## Co skill nedělá

- **Nepíše zadání ani plán.** Je první článek osy *Životního cyklu práce* (`~/.claude/RULES.md`); co se staví, řeší `/spec`, rozpad na úkoly `/breakdown`. `docs/prd.md`, `docs/design.md` ani `docs/plan.md` proto nezakládá.
- **Neprogramuje.** Ani scaffold, ani závislosti. Nastavuje projekt, ne aplikaci.
- **Nepřepisuje nic naslepo.** U existujícího projektu se na každý rozpor ptá.
- **Nenaplňuje soubory obsahem.** `docs/` zakládá prázdné, jen s nadpisem.

## Zásady pro celý průběh

- **Otázky pokládej jednu po druhé**, ne všechny najednou. U pevné sady možností použij **AskUserQuestion**, u otevřených otázek (popis projektu, URL remote) se ptej v chatu a počkej na odpověď.
- **Dvourychlostní režim.** Mechanické a jednoznačné věci udělej rovnou a jen je vypiš (založení chybějícího souboru, doplnění chybějící sekce). Sporné předlož uživateli – zejména cokoliv, co **přepisuje nebo maže existující obsah**.
- **Nikdy nepřepiš existující soubor bez zeptání.** Chybí-li soubor, založ ho. Existuje-li a je v rozporu se zvolenou preferencí, ukaž rozdíl a zeptej se.
- Konvenci standardní struktury **neopisuj z hlavy** – řiď se `~/Dev/context/structure/structure.md`, který ji definuje. Tenhle skill je jen instalátor.

------

## Krok 0 – Zjisti režim a stav

Pomocí **Glob** (ne Bash `git`, aby nenaskočila zbytečná chybová hláška) zjisti, co v adresáři je: `.git`, `.bare`, `CLAUDE.md`, `README.md`, `docs/`, `TODO.md`, `docs/prompts.md` (příp. starší `PROMPTS.md` v rootu), `.gitignore`, zdrojové soubory.

- **Prázdný nebo skoro prázdný adresář** → režim *nový projekt*.
- **Cokoliv jiného** → režim *existující projekt*.

V režimu *existující projekt* si nejdřív udělej inventuru a **vypiš ji uživateli v pár řádcích**, ať oba víte, z čeho se vychází:

| Co zjistit | Jak |
|---|---|
| Git a jeho podoba | je `.git` adresář (běžný), nebo `.bare` + `.git` soubor (worktree layout)? má remote? |
| Projektový `CLAUDE.md` | existuje? co v něm už je (autocommit, autoprompt, paměť, typ, importy)? |
| Standardní struktura | existuje `README.md`, `todo.md`, `done.md`, `decisions.md`, `rules.md` – a **kde**, v `docs/` nebo v kořeni? (určuje režim, viz krok 4a) |
| *(worktree layout)* rozdělení souborů | leží projektové soubory v `main/`, nebo omylem v kořeni kontejneru? je v kořeni stub s `@main/CLAUDE.md`? |
| Starší pojmenování | existuje `TODO.md` v rootu, `docs/rozhodnuti.md`, `docs/zasady.md`? (viz Krok 4) |
| Typ projektu | odvoď z obsahu – `package.json`, zdrojové adresáře, převaha MD souborů |

Pak řekni, že se teď budeš ptát postupně, a pokračuj. V dalších krocích platí: **co už je nastavené a odpovídá volbě, nech být a jen to zmiň.**

## Krok 1 – Metadata projektu

Formát bloku metadat definuje `~/Dev/context/structure/structure.md`, sekce *`CLAUDE.md`* – **neopisuj ho z hlavy, přečti si ho.** Řeší se čtyři údaje: **slug**, **lidský název**, **popisek** a **URL projektu**.

Slug je daný adresářem. Zbylé tři **navrhni sám** – u nového projektu z toho, co ti uživatel řekl, u existujícího z toho, co v repozitáři najdeš (`CLAUDE.md`, `README.md`, `package.json`, obsah). Předlož návrh k odsouhlasení, ať ho uživatel může jen potvrdit, nebo přepsat:

```
Slug:     rezervace
Název:    Rezervační systém
Popisek:  Rezervační systém pro školení, konference a webináře – správa událostí, účastníků, objednávek a faktur.
Web:      (žádný)
```

Zeptej se v chatu (ne AskUserQuestion – jde o volný text) a počkej na odpověď. **Nic si nevymýšlej**: nevíš-li, jestli projekt má veřejnou URL, zeptej se místo hádání.

*Existující projekt:* najdeš-li v `CLAUDE.md` nebo `README.md` popis, který už platí, nabídni ho beze změny. Rozcházejí-li se popisy v `CLAUDE.md` a `README.md`, ukaž oba a nech rozhodnout, který je pravda.

## Krok 2 – Založení nebo doplnění CLAUDE.md

**Existuje-li už worktree layout** (z inventury v kroku 0, nebo protože ho zvolíš v kroku 3b), je „projektový `CLAUDE.md`“ vždy `main/CLAUDE.md` – viz krok 3b. U nového projektu, kde se o layoutu rozhoduje až v kroku 3b, zapiš zatím do kořene; krok 3b soubor přesune.

Zapiš blok metadat na **začátek** `CLAUDE.md`, ve formátu podle `structure.md`:

```
# Rezervační systém

Rezervační systém pro školení, konference a webináře – správa událostí, účastníků, objednávek a faktur.

- **Slug:** `rezervace`
- **Struktura:** docs/
- **Web:** https://rezervace.example.cz
- **Repozitář:** https://github.com/jantichy/rezervace
```

Řádky `Web` a `Repozitář` vynech, pokud neexistují. `Repozitář` doplň v kroku 3, jakmile je remote známý.

*Existující projekt:* nezakládej znovu, doplňuj do stávajícího. Má-li soubor generický nadpis (`# CLAUDE.md`) nebo popis rozsypaný v sekci `## Projekt`, **navrhni jeho nahrazení blokem metadat** – ukaž rozdíl a nech si to potvrdit. Sekce, které přidávají další kroky, vkládej za stávající obsah; existující sekce téhož jména neduplikuj, ale aktualizuj.

## Krok 3 – Git

Zeptej se (AskUserQuestion), 4 možnosti:

- **Nic** – git se neřeší, přeskoč i kroky 3b a 5.
- **Jen lokální** – `git init`, žádný remote.
- **Remote (napojit na existující)** – `git init`, pak se v chatu zeptej na URL a spusť `git remote add origin <url>`.
- **Remote (založit nový)** – `git init`, pak AskUserQuestion na hostitele (GitHub / GitLab). U GitHubu s dostupným `gh` (`which gh`) se zeptej na viditelnost a spusť `gh repo create <název-adresáře> --private|--public --source=. --remote=origin`. Jinak vypiš instrukci „Založ prázdné repo na <platforma>, pak mi dej URL“ a počkej.

*Existující projekt:* je-li git už inicializovaný, `git init` nespouštěj. **Ověř remote přes `git remote get-url origin`**, ne jen `git remote -v` – remote může existovat s prázdnou URL a `-v` to nepozná. Chybí-li nebo je-li rozbitý, nabídni doplnění.

### Propsání metadat do Repository details

*Jen u GitHubu s dostupným `gh`.* Description a website repozitáře nejdou nastavit souborem v repu – jsou to metadata na straně GitHubu. Propiš tam popisek a URL z kroku 1:

```bash
gh repo edit <owner>/<slug> -d "<popisek>" -h "<web>"
```

Nejdřív si přes `gh repo view <owner>/<slug> --json description,homepageUrl` **zjisti současný stav**. Liší-li se od popisku z kroku 1, ukaž rozdíl a přepiš. Je-li shodný, nech být a jen to zmiň. Web se nepředává, když projekt žádný nemá – prázdné `-h ""` existující hodnotu smaže.

Do bloku metadat v `CLAUDE.md` zároveň doplň řádek `Repozitář` s URL remote.

U GitLabu a jiných hostitelů tenhle krok přeskoč a řekni uživateli, že popisek si tam musí nastavit ručně.

## Krok 3b – Layout repozitáře

*Jen pokud v kroku 3 padla jiná volba než „Nic“.*

Zeptej se (AskUserQuestion): jak má být projekt rozbalený na disku?

- **Jeden pracovní adresář (jednoduché)** – klasika: `.git` a rozbalený projekt přímo v adresáři. Vhodné, když nad projektem pracuješ vždy v jedné session.
- **Worktree layout (paralelní práce)** – kontejner s `.bare` a jedním pracovním podadresářem na větev. Vhodné, když chceš nad projektem běžet ve víc Claude sessions naráz, aniž si přepisují soubory. Popis viz `~/Dev/context/worktree/worktree.md`.

### Když padne worktree layout

**Postup zřízení kontejneru neopisuj z hlavy** – řiď se `~/Dev/context/worktree/worktree.md`, sekce *Zřízení kontejneru*. Má variantu pro nový projekt i pro konverzi existujícího repozitáře, včetně povinné zálohy, ověření diffem a úklidu zamrzlého `.bare/index`.

U existujícího projektu jde o **přeskládání adresáře** – řekni to nahlas a nech si ho potvrdit, než začneš.

### Dva `CLAUDE.md` – tohle si přečti pozorně

Ve worktree layoutu jsou `CLAUDE.md` **dva** a mají různý účel. Zaměnit je je nejčastější chyba tohohle skillu, protože kořen kontejneru **není pracovní strom** – nic v něm není ve gitu a nikdy to nepůjde commitnout.

| Soubor | Co v něm je | Píší do něj kroky |
|---|---|---|
| `<projekt>/CLAUDE.md` (kontejner) | jen popis layoutu, odchylky a import toho druhého | pouze tenhle krok 3b |
| `<projekt>/main/CLAUDE.md` (**projektový**) | všechno ostatní – metadata, struktura, autocommit, autoprompt, paměť, typ, doménové importy | kroky 2, 4, 6, 7, 8, 9, 10 |

**Kdykoli dál v tomhle skillu čteš „projektový `CLAUDE.md`“, myslí se `main/CLAUDE.md`.** Totéž platí pro `README.md`, `docs/*` a `.gitignore` – všechny patří do `main/`. Jedinou výjimkou je `.claude/settings.local.json` (krok 7), který naopak musí být v **kořeni kontejneru**, protože odtud se pouští session a odtud si ho Claude Code čte.

Do `<projekt>/CLAUDE.md` (do **kontejneru**) zapiš tenhle stub a nic víc:

```
# <Lidský název projektu>

Tenhle adresář není projekt, ale kontejner s worktree layoutem. Pravidla práce s ním:

@~/Dev/context/worktree/worktree.md

Vlastní pravidla projektu jsou v `main/CLAUDE.md` a importují se odsud:

@main/CLAUDE.md

## Odchylky

- <odchylka v pojmenování hlavní větve – uveď jen u staršího projektu, kde se nejmenuje `main`>
- <co konkrétně se přebírá z main/, nebo že zatím není co>
```

Import `@main/CLAUDE.md` je nutný: `CLAUDE.md` z podadresáře se načte až on-demand, když z něj něco čteš, kdežto session startuje v kontejneru. Bez importu by pravidla projektu na začátku session vůbec nebyla v kontextu. Relativní cesta se resolvuje vůči souboru, který import obsahuje.

**Pravidla projektu do stubu nekopíruj.** Dvě kopie se rozejdou a načtou se pak obě.

*Nový projekt:* krok 2 už `CLAUDE.md` založil v kořeni, protože tehdy ještě nebylo rozhodnuto o layoutu. **Přesuň ho teď do `main/`** (`mv <projekt>/CLAUDE.md <projekt>/main/CLAUDE.md`) a v kořeni na jeho místo napiš stub. Totéž udělej s čímkoli dalším, co v kořeni mezitím vzniklo a patří do projektu.

*Konverze existujícího projektu:* původní `CLAUDE.md` se přesunul do `main/` spolu se zbytkem repozitáře a **je správně tam** – nech ho být, jen do něj dál doplňuj. V kořeni založ nový, prázdný stub.

Po tomhle kroku si **ověř výsledek** a vypiš ho uživateli: v kořeni smí být jen `.bare/`, `.git`, `CLAUDE.md` (stub) a `.claude/`; `README.md`, `docs/` a projektový `CLAUDE.md` musí být v `main/`.

Upozorni uživatele, že **při příštím spuštění dostane dialog na schválení externího importu a musí ho odsouhlasit** – při odmítnutí se importy pro ten projekt trvale vypnou a dialog se už neukáže.

### Náprava špatně rozděleného kontejneru

*Existující projekt, kde worktree layout už je.* Najdeš-li v kořeni kontejneru projektové soubory, které tam nepatří – plnohodnotný `CLAUDE.md` s pravidly místo stubu, `README.md`, `docs/` – nabídni nápravu: přesun do `main/` a nahrazení kořenového `CLAUDE.md` stubem. Ukaž konkrétní seznam souborů a nech si to potvrdit, protože jde o přesouvání obsahu.

Existují-li oba `CLAUDE.md` a mají překrývající se sekce, **obsah slouč do `main/CLAUDE.md`** a v kořeni nech jen stub; nikdy jeden z nich mlčky nepřepiš.

Přesun je `git mv` jen tehdy, je-li zdroj verzovaný – v kořeni kontejneru **nikdy není**, takže tam jde o obyčejný `mv`. Po přesunu soubory v `main/` commitni.

## Krok 4 – Standardní struktura

Řiď se `~/Dev/context/structure/structure.md` – ten je autoritativní, tenhle krok je jen provedení.

### 4a – Režim umístění

Standardní soubory leží buď v `docs/`, nebo přímo v kořeni projektu. Obojí je rovnocenné.

*Nový projekt:* zeptej se (AskUserQuestion, jedna otázka):

| Volba | Popis pro uživatele |
|---|---|
| `docs/` (výchozí) | Meta-vrstva odděleně od vlastní práce. Sedí na projekt s kódem nebo obsahem. |
| `root` | Soubory přímo v kořeni. Sedí na knowledge base a malé projekty, kde by `docs/` byl prázdný obal. |

*Existující projekt:* režim **detekuj a rovnou zapiš**, neptej se. Leží-li `todo.md` nebo `decisions.md` v kořeni → `root`; leží-li v `docs/` → `docs/`; nenajdeš-li ani jedno → `docs/`. Co jsi zjistil a zapsal, **řekni nahlas** v závěrečném souhrnu. Najdeš-li soubory na obou místech, je to nepořádek, ne třetí režim – vypiš, co je kde, a nech si vybrat, na který režim to srovnat.

**Ve worktree layoutu** je kořen projektu `main/`, ne kořen kontejneru (viz krok 3b).

Zapiš do bloku metadat v `CLAUDE.md`, za řádek `Slug`:

```
- **Struktura:** docs/
```

### 4b – Které soubory založit

Povinný je jen `CLAUDE.md`. U zbytku se zeptej (AskUserQuestion, `multiSelect: true`, vše předvybrané):

| Soubor | Popis pro uživatele |
|---|---|
| `README.md` | Co projekt je, pro člověka. U privátního projektu bez publika nemusí být. |
| `todo.md` + `done.md` | Co je odložené na později, a záznam hotového. **Jedna volba pro obojí** – samostatně nedávají smysl. |
| `decisions.md` | Co jsme rozhodli a proč, včetně zamítnutých variant. |
| `rules.md` | Principy, ve kterých se projekt pohybuje. |

Nezaložený soubor **není odchylka** – vznikne, až bude potřeba. Do `CLAUDE.md` (krok 4, *Zápis*) vypiš jen ty, které vznikly.

`prompts.md` sem nepatří – zakládá ho autoprompt v kroku 7. `prd.md`, `design.md` a `plan.md` **nezakládej**, vznikají prací přes `/spec` a `/breakdown`.

*Existující projekt:* co už existuje, ber jako zvolené; ptej se jen na to, co chybí.

### 4c – Obsah

`README.md` u nového projektu: nadpis s **lidským názvem** a popiskem z kroku 1 jako prvním odstavcem – tam se popisek smí rozvést do víc vět. U existujícího projektu zkontroluj, že nadpis a první odstavec sedí s blokem metadat v `CLAUDE.md`; rozcházejí-li se, srovnej je. Soubory v `docs/` zakládej **prázdné, jen s nadpisem** – obsah nevymýšlej dopředu.

**README je pro člověka, ne pro Clauda.** Definici, co do něj patří a co ne, má `~/Dev/context/structure/structure.md`, sekce `README.md`; drž se jí doslova. U existujícího projektu README **projdi celé** a co je normativní pokyn pro Clauda – pravidla práce v repozitáři, konvence pojmenování, povinnost něco udržovat, odkaz na to, čím se má Claude řídit – přesuň do `CLAUDE.md`, `docs/rules.md` nebo `docs/decisions.md` podle povahy. Nekopíruj, přesouvej: informace má žít na jednom místě.

### Migrace staršího pojmenování

*Existující projekt:* najdeš-li starší varianty, nabídni přejmenování přes AskUserQuestion (jedna otázka na všechny nálezy dohromady, protože jde o jedno rozhodnutí):

| Staré | Nové |
|---|---|
| `TODO.md` v rootu | `todo.md` na místě podle režimu |
| `rozhodnuti.md` | `decisions.md` |
| `zasady.md` | `rules.md` |

Cílové umístění se řídí režimem z kroku 4a. `TODO.md` velkými písmeny v kořeni **není** režim `root` – je to staré pojmenování, které se migruje tak jako tak.

Přejmenovávej přes `git mv`, ať se zachová historie. Po přejmenování **projdi celý repozitář a aktualizuj všechny odkazy** na staré názvy – v `CLAUDE.md`, `README.md`, dokumentaci i komentářích. Existuje-li cílový soubor už také, obsah **slouč** a na sloučení upozorni; nikdy nepřepisuj.

### Zápis do CLAUDE.md

Přidej sekci – konkrétní deklaraci, ne opis konvence:

Vypiš **jen soubory, které v projektu opravdu jsou**, s cestou podle zvoleného režimu:

```
## Struktura a dokumentace

Projekt drží standardní strukturu podle `~/Dev/context/structure/structure.md`:

- `README.md` – co projekt je, pro člověka (ne instrukce pro Clauda)
- `docs/todo.md` – co je odložené na později
- `docs/done.md` – co je hotové
- `docs/decisions.md` – co jsme rozhodli a proč, včetně zamítnutých variant
- `docs/rules.md` – principy, ve kterých se projekt pohybuje

Všechny tyhle soubory **aktualizuj průběžně sám a bez vyžádání**, ve chvíli, kdy rozhodnutí padne, princip se vybrousí nebo se něco odloží. Nečekej na konec session ani na `/cleanup`.
```

## Krok 5 – .gitignore

*Jen pokud v kroku 3 padla jiná volba než „Nic“.* Chybí-li `.gitignore`, založ ho s tímto jádrem a dopiš podle zjevného stacku:

```
.DS_Store
.env
.env.local
node_modules/
dist/
build/
.next/
out/
.vercel
*.log
.idea/
.vscode/
```

Existuje-li, **nepřepisuj ho** – jen doplň chybějící řádky z jádra a vypiš, co jsi přidal.

## Krok 6 – Autocommit

Zeptej se (AskUserQuestion): zapnout autocommit? Ano/Ne. Při ano proveď totéž co `/autocommit on` (viz `~/.claude/skills/autocommit/SKILL.md`).

*Existující projekt:* nejdřív **zjisti aktuální stav** – hledej sekci `Autocommit` v projektovém `CLAUDE.md` **bez ohledu na úroveň nadpisu** (`##` i `###`). Aktuální stav uveď v otázce, ať uživatel ví, co mění.

## Krok 7 – Autoprompt

Zeptej se (AskUserQuestion): zapnout autoprompt? Ano/Ne. Při ano proveď totéž co `/autoprompt on` (viz `~/.claude/skills/autoprompt/SKILL.md`): globální `CLAUDE.md`, projektová sekce, hook do `.claude/settings.local.json`, založení `docs/prompts.md`.

*Worktree layout:* `.claude/settings.local.json` patří do **kořene kontejneru**, `docs/prompts.md` do **`main/`**. Hook si worktree hlavní větve najde sám, takže se nikde nemusí konfigurovat cesta.

*Nový projekt:* backfill historie přeskoč, není co dohledávat.
*Existující projekt:* zjisti stav stejně jako u autocommitu a backfill nabídni.

## Krok 8 – Paměťová politika

Zeptej se (AskUserQuestion): „Má Claude v tomto projektu ukládat poznatky do trvalé Memory, nebo vše explicitně do lokálních .md souborů?“ Možnosti: **Jen lokální .md soubory (doporučeno)** / **Normální chování (Memory povolena)**.

Při první volbě přidej do `CLAUDE.md`:

```
## Paměť

Neukládej nic do trvalé Memory (`~/.claude/projects/.../memory/`). Vše, na čem se domluvíme – rozhodnutí, kontext, poznámky – ukládej explicitně do souborů projektu podle `~/Dev/context/structure/structure.md`. Ty jsou jediný zdroj pravdy pro tento projekt, i když harness bude nabádat k zápisu do Memory.
```

## Krok 9 – Typ projektu

Typů je šest, ale AskUserQuestion bere najednou nejvýš čtyři volby. Ptej se proto ve dvou úrovních – nejdřív na oblast, pak na typ uvnitř ní. Uživatel klikne nejvýš dvakrát a žádný typ se neztratí.

**První otázka** (AskUserQuestion): „Čeho se projekt hlavně týká?“ Tři volby:

| Volba | Co následuje |
|---|---|
| Vývoj software a webů | druhá otázka: **Vývoj** / **Web** |
| Analytika | druhá otázka: **Nasazení webové analytiky** / **Data a výzkum** |
| Obsah | typ je rovnou **Psaní a obsah**, druhá otázka odpadá |

Oblasti jsou schválně dělené podle **povahy práce, ne podle použité technologie** – vývoj software a webů je stavění, analytika je měření a vyhodnocování, obsah je psaní. Až přibude další typ, patří do té oblasti, jejíž povahu sdílí; pokud do žádné, je to signál, že chybí čtvrtá oblast, ne že se má nacpat do nejbližší.

**Až se oblasti zaplní.** Dvouúrovňová otázka má strop 16 typů (4 oblasti × 4 typy). Až na něj narazíš, nepřidávej třetí úroveň – přejdi na **N kol po čtyřech**: jedno kolo na každou oblast, `multiSelect: true`, uvozené „Co všechno z oblasti <oblast> pro tenhle projekt platí? Když nic, nic nezaškrtávej.“ Kol může být libovolně mnoho, takže limit AskUserQuestion přestane omezovat.

Ta změna má důsledek, který je potřeba unést vědomě: projekt tím přestane mít jeden typ a bude mít **sadu typů** – klidně prázdnou (= **Ostatní**), klidně **Vývoj** i **Web** zároveň. Do `CLAUDE.md` pak nelep popisy pod sebe mechanicky: slož je do jednoho odstavce a **vyřeš rozpory**. „Vývoj“ předepisuje proces zadání a plánu, „Web“ ho výslovně nechce – když padnou oba, rozhodni podle hlavní náplně projektu a napiš jen to, co platí.

Volbu „Ostatní“ mezi možnosti **nedávej** – AskUserQuestion ji nabízí sám jako „Other“. Když ji uživatel použije, typ je **Ostatní** a druhá otázka odpadá.

Do `CLAUDE.md` přidej sekci `## Typ projektu` s krátkým popisem:

- **Vývoj** – „Vývojářský projekt – postupuj podle *Životního cyklu práce* v `~/.claude/RULES.md`: `/spec` → `/breakdown` → `/implement`.“ Navíc přidej pravidlo: „Před implementací nové funkce nejdřív aktualizuj příslušný dokument v `docs/` (doc-first).“
- **Web** – „Webové rozhraní – obsah, struktura, šablony, ne proces zadání a plánu.“
- **Nasazení webové analytiky** – „Implementace měření na cizím webu – revize existujícího nastavení, měřicí plán, GTM, GA4, consent, reklamní systémy. Výstupem je funkční a doložitelné měření plus dokumentace, ne aplikační kód.“ Navíc přidej pravidlo: „Každá změna v měření musí být před publikováním ověřená v Preview/DebugView a po nasazení znovu na produkci; do `docs/decisions.md` patří i to, co se měřit záměrně nebude a proč.“
- **Psaní a obsah** – „Projekt zaměřený na psaní a obsah, ne na vývoj software – bez procesu zadání a plánu.“
- **Data a výzkum** – „Jednorázová datová/výzkumná analýza – výstupem jsou zjištění a report, ne nasazovaný kód.“
- **Ostatní** – „Projekt mimo výše uvedené kategorie.“

## Krok 10 – Doménové checklisty

Zeptej se (AskUserQuestion, **`multiSelect: true`**): „Které doménové checklisty jsou pro tenhle projekt relevantní?“ Volby předvyplň podle typu z kroku 9, ale nech uživatele rozhodnout – vývojářský projekt bývá zároveň web, web bývá zároveň administrace.

U typu **Nasazení webové analytiky** přihraj napevno `analytics/analytics.md` a `web/web.md` (analytika se nasazuje do webu a překrývá se s ním v consentu a GDPR) a předvyplň `text/text.md`, protože výstupem bývá auditní report nebo dokumentace pro klienta. `coding/coding.md` nabídni jen tehdy, když se v projektu opravdu píše kód – šablony, serverový endpoint, vlastní CMP.

| Volba | Import |
|---|---|
| Psaní kódu | `@~/Dev/context/coding/coding.md` |
| Webové rozhraní | `@~/Dev/context/web/web.md` |
| Administrace / backoffice | `@~/Dev/context/web/admin.md` |
| Webová analytika a měření | `@~/Dev/context/analytics/analytics.md` |
| Psaní českých textů | `@~/Dev/context/text/text.md` |
| Školení a kurzy | `@~/Dev/context/training/training.md` |
| Vizuální tvorba a grafika | `@~/Dev/context/design/design.md` |
| Prezentace a slajdy | `@~/Dev/context/design/slides.md` |
| Žádný | – |

U typu projektu, kde se připravuje **školení, kurz nebo workshop**, předvyplň `training/training.md` spolu s `text/text.md` – materiály pro účastníky jsou text a řídí se obojím. Přihoď i `design/slides.md`, pokud k tomu vzniká promítaná prezentace.

`design/slides.md` nabízej i mimo školení – všude, kde se dělá deck: konferenční přednáška, prodejní pitch, prezentace výsledků klientovi. Importuje se **navíc** k `design/design.md`, ne místo něj.

`worktree.md` se tu nenabízí schválně – importuje se už v kroku 3b, když si uživatel zvolí worktree layout.

### Profil organizace

Když projekt vzniká **pro konkrétní organizaci**, zeptej se, jestli má profil v `~/Dev/context/organizations/`, a když ano, přidej ho do importů:

```
@~/Dev/context/organizations/planetum.md
```

**Není to doménový standard, ale korpus** – kdo v organizaci sedí, kdo co schvaluje, jaké mají systémy. Profil zůstává v knowledge base a projekt na něj jen odkazuje; jedna organizace může mít víc projektů a všechny sdílejí týž profil. Když profil neexistuje a jde o **opakovaný vztah, u kterého je potřeba znát vnitřek organizace**, navrhni jeho založení – kritérium je v `~/Dev/context/organizations/organizations.md`, sekce *Kdo dostane profil*.

Vybrané zapiš do `CLAUDE.md` jako **tvrdé `@import`y**, ne jako prozaické odkazy:

```
## Doménové standardy

Závazné pro tenhle projekt:

@~/Dev/context/coding/coding.md
@~/Dev/context/web/web.md
```

**Proč `@import` a ne odkaz:** `@import` Claude Code při startu session textově rozbalí do kontextu, takže obsah platí vždy. Prozaický odkaz („řiď se souborem X“) je jen instrukce, kterou si model musí sám všimnout a sám se rozhodnout ji splnit – to se v praxi dodržuje nespolehlivě.

Platí to **pro projekt**, kde je doména relevantní pořád. Globální `~/.claude/CLAUDE.md` naopak odkazuje prozaicky schválně – tam se domény střídají a import všech by stál kontext v každé session.

Importuj **jen to, co je pro projekt opravdu relevantní.** Každý import stojí kontext v každé session; `web/web.md` a `web/admin.md` mají dohromady skoro 500 řádků.

Upozorni uživatele, že při příštím spuštění dostane dialog na schválení externího importu a **musí ho odsouhlasit**.

## Krok 11 – Závěrečný souhrn

Vypiš přehledně:

- **Co bylo založeno** (nový projekt) nebo **co se změnilo a co zůstalo** (existující projekt).
- Metadata projektu (název, popisek, web) a kam všude se propsala, git a remote, layout repozitáře, standardní struktura, provedené migrace názvů, autocommit, autoprompt, paměťová politika, typ, importované checklisty.
- **Co uživatel musí udělat ručně** – zejména odsouhlasení dialogu externích importů při příštím spuštění.

U existujícího projektu vypiš i **co jsi záměrně nechal být a proč** – ať je vidět, že to nebylo opomenutí.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Projekt je nastavený, můžeš v něm začít pracovat.`
- `Nastavený úplně není – zbývá: <konkrétní seznam>.`
