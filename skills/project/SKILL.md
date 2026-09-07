---
name: project
description: Skill se použije, když uživatel zadá "/project", nebo chce založit nový projekt v čistém adresáři, přenastavit už existující projekt (metadata projektu a jejich propsání do Repository details na GitHubu, git, worktree layout, standardní struktura docs/, autocommit, paměťová politika, typ projektu, doménové checklisty), anebo dorovnat dřív nastavený projekt na aktuální podobu standardů a konfigurační vrstvy – revize souladu struktury, dokumentace, sekcí CLAUDE.md, kontraktů a importů. Interaktivní wizard, který se ptá krok po kroku.
argument-hint: [create|adopt|update]
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion]
---

# Project

## Co skill dělá

Interaktivně nastaví projekt v aktuálním adresáři a zapíše vše do projektového `CLAUDE.md`. Funguje ve třech režimech:

- **`create`** *(nový projekt)* – čistý adresář, všechno se zakládá od nuly.
- **`adopt`** *(existující projekt)* – adresář, ve kterém už něco je, ale chybí v něm otisk `/project` (blok metadat v `CLAUDE.md`) – ať proto, že skill v něm nikdy neběžel, nebo proto, že ho nastavovala starší verze. Zjistí se aktuální stav a nabídne se, co dorovnat na zvolené preference; nakonec proběhne i krok 14. Nic se nepřepisuje naslepo.
- **`update`** *(revize)* – projekt, který `/project` už jednou nastavil. Neptá se znovu na volby, které padly; místo toho **projde celý projekt proti aktuální podobě standardů** (`~/Dev/context/structure/structure.md`, `~/.claude/RULES.md`, doménové znalosti, konfigurační vrstva) a dorovná, co se mezitím rozešlo. Viz krok 14.

Režim **`update` je hlavní důvod, proč je skill opakovatelný.** Standardy a skilly se vyvíjejí dál, kdežto projekty založené za starého nastavení zůstávají stát – a rozdíl se z projektu sám nepozná. Druhý běh je tedy plnohodnotná kontrola, ne jen verifikace, že se nic nezměnilo.

## Co skill nedělá

- **Nepíše zadání ani plán.** Je první článek *Životního cyklu projektu* (`~/.claude/RULES.md`) a předává na `/discovery`, který zkoumá svět venku. Co se staví, řeší `/specify`, rozpad na úkoly `/breakdown`. `docs/requirements.md`, `docs/architecture.md` ani `docs/plan.md` proto nezakládá.
- **Neprogramuje.** Ani scaffold, ani závislosti. Nastavuje projekt, ne aplikaci.
- **Nepřepisuje nic naslepo.** U existujícího projektu se na každý rozpor ptá.
- **Nenaplňuje soubory obsahem.** `docs/` zakládá prázdné, jen s nadpisem.
- **Nerediguje obsah dokumentace.** `update` hlídá **tvar** – kde soubor leží, jak se jmenuje, jak je uvnitř seřazený, jestli položka sedí do souboru, ve kterém je. Jestli je zapsané rozhodnutí správné nebo úkol dobře napsaný, neřeší; od toho jsou `/consistency` a `/review`.

## Zásady pro celý průběh

- **Postup se tu člení na kroky, ne na fáze** – jako v jediném skillu životního cyklu. Kritérium normy (`~/.claude/skills/SKILLS.md`, *Číslování a názvosloví*) zní, čí odpovědi tvoří výsledek: tady je výsledkem to, co uživatel naodpovídal, takže postup je sled otázek. Ostatní skilly něco samy najdou nebo vyrobí a ptají se až na nálezy – ty mají fáze, i když se ptají stejně často. Číslují se **plochou vzestupnou řadou bez písmen** (`~/.claude/skills/SKILLS.md`, *Číslování a názvosloví*). Kroky 5–8 zakládají standardní strukturu a byly kdysi jedním krokem s podkroky `6a`–`6c`; kritériu normy pro písmennou podfázi ale nevyhověly – jsou to fáze jedné volby, ne samostatné výstupy –, tak se z nich staly samostatné kroky.
- **Otázky pokládej jednu po druhé**, ne všechny najednou. U pevné sady možností použij **AskUserQuestion**, u otevřených otázek (popis projektu, URL remote) se ptej v chatu a počkej na odpověď.
- **Dvourychlostní režim.** Mechanické a jednoznačné věci udělej rovnou a jen je vypiš (založení chybějícího souboru, doplnění chybějící sekce). Sporné předlož uživateli – zejména cokoliv, co **přepisuje nebo maže existující obsah**.
- **Nikdy nepřepiš existující soubor bez zeptání.** Chybí-li soubor, založ ho. Existuje-li a je v rozporu se zvolenou preferencí, ukaž rozdíl a zeptej se.
- **V režimu `update` se na hotové volby neptej znovu.** Co je v `CLAUDE.md` zapsané a dává smysl, platí. Otázka se pokládá jen tam, kde `update` našel rozpor nebo mezeru – a klade se o tom rozporu, ne o celém kroku.
- Konvenci standardní struktury **neopisuj z hlavy** – řiď se `~/Dev/context/structure/structure.md`, který ji definuje. Tenhle skill je jen instalátor.

------

## Krok 0 – Zjisti režim a stav

Pomocí **Glob** (ne Bash `git`, aby nenaskočila zbytečná chybová hláška) zjisti, co v adresáři je: `.git`, `.bare`, `CLAUDE.md` **i `main/CLAUDE.md`** (ve worktree layoutu je v kořeni jen stub bez bloku metadat, takže otisk hledej v `main/` – viz krok 4), `README.md`, `.gitignore`; standardní soubory **na obou možných místech** – `docs/todo.md` i kořenový `todo.md`, totéž pro `backlog.md`, `decisions.md`, `done.md` a `rules.md` (podle toho se v kroku 5 pozná režim); starší pojmenování `TODO.md` v kořeni; zdrojové soubory.

- **Prázdný nebo skoro prázdný adresář** → režim `create`.
- **Projekt, kterým už `/project` prošel** → režim `update`. Poznáš ho podle **bloku metadat na začátku projektového `CLAUDE.md`** – řádku `- **Slug:**`. Ten blok nezakládá nic jiného, takže je to spolehlivý otisk. Pokračuj krokem 14.
- **Cokoliv jiného** → režim `adopt`.

Řekni nahlas, který režim to je a podle čeho jsi to poznal. Trvá-li uživatel na plném průchodu průvodcem i nad nastaveným projektem, ber to jako pokyn a jeď režim `adopt`.

V režimech `adopt` i `update` si nejdřív udělej inventuru a **vypiš ji uživateli v pár řádcích**, ať oba víte, z čeho se vychází:

| Co zjistit | Jak |
|---|---|
| Git a jeho podoba | je `.git` adresář (běžný), nebo `.bare` + `.git` soubor (worktree layout)? má remote? |
| Projektový `CLAUDE.md` | existuje? co v něm už je (autocommit, paměť, typ, importy)? |
| Standardní struktura | existuje `README.md`, `todo.md`, `backlog.md`, `done.md`, `decisions.md`, `rules.md` – a **kde**, v `docs/` nebo v kořeni? (určuje režim, viz krok 5) |
| *(worktree layout)* rozdělení souborů | leží projektové soubory v `main/`, nebo omylem v kořeni kontejneru? je v kořeni stub s `@main/CLAUDE.md`? |
| Starší pojmenování | existuje `TODO.md` v rootu, `rozhodnuti.md`, `zasady.md` (na místě podle režimu z kroku 5)? (viz krok 5) |
| Typ projektu | odvoď z obsahu – `package.json`, zdrojové adresáře, převaha MD souborů |

*`adopt`:* pak řekni, že se teď budeš ptát postupně, a pokračuj krokem 1. V dalších krocích platí: **co už je nastavené a odpovídá volbě, nech být a jen to zmiň.** *`update`:* neptej se na nic a pokračuj krokem 14.

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

*`adopt`:* najdeš-li v `CLAUDE.md` nebo `README.md` popis, který už platí, nabídni ho beze změny. Rozcházejí-li se popisy v `CLAUDE.md` a `README.md`, ukaž oba a nech rozhodnout, který je pravda.

## Krok 2 – Založení nebo doplnění CLAUDE.md

**Existuje-li už worktree layout** (z inventury v kroku 0, nebo protože ho zvolíš v kroku 4), je „projektový `CLAUDE.md`“ vždy `main/CLAUDE.md` – viz krok 4. U nového projektu, kde se o layoutu rozhoduje až v kroku 4, zapiš zatím do kořene; krok 4 soubor přesune.

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

*`adopt`:* nezakládej znovu, doplňuj do stávajícího. Má-li soubor generický nadpis (`# CLAUDE.md`) nebo popis rozsypaný v sekci `## Projekt`, **navrhni jeho nahrazení blokem metadat** – ukaž rozdíl a nech si to potvrdit. Sekce, které přidávají další kroky, vkládej za stávající obsah; existující sekce téhož jména neduplikuj, ale aktualizuj.

## Krok 3 – Git

Zeptej se (AskUserQuestion), 4 možnosti:

- **Nic** – git se neřeší, přeskoč i kroky 4 a 7.
- **Jen lokální** – `git init`, žádný remote.
- **Remote (napojit na existující)** – `git init`, pak se v chatu zeptej na URL a spusť `git remote add origin <url>`.
- **Remote (založit nový)** – `git init`, pak AskUserQuestion na hostitele (GitHub / GitLab). U GitHubu s dostupným `gh` (`which gh`) se zeptej na viditelnost a spusť `gh repo create <název-adresáře> --private|--public --source=. --remote=origin`. Jinak vypiš instrukci „Založ prázdné repo na <platforma>, pak mi dej URL“ a počkej.

*`adopt`:* je-li git už inicializovaný, `git init` nespouštěj. **Ověř remote přes `git remote get-url origin`**, ne jen `git remote -v` – remote může existovat s prázdnou URL a `-v` to nepozná. Chybí-li nebo je-li rozbitý, nabídni doplnění.

### Propsání metadat do Repository details

*Jen u GitHubu s dostupným `gh`.* Description a website repozitáře nejdou nastavit souborem v repu – jsou to metadata na straně GitHubu. Propiš tam popisek a URL z kroku 1:

```bash
gh repo edit <owner>/<slug> -d "<popisek>" -h "<web>"
```

Nejdřív si přes `gh repo view <owner>/<slug> --json description,homepageUrl` **zjisti současný stav**. Liší-li se od popisku z kroku 1, ukaž rozdíl a přepiš. Je-li shodný, nech být a jen to zmiň. Web se nepředává, když projekt žádný nemá – prázdné `-h ""` existující hodnotu smaže.

Do bloku metadat v `CLAUDE.md` zároveň doplň řádek `Repozitář` s URL remote.

U GitLabu a jiných hostitelů tenhle krok přeskoč a řekni uživateli, že popisek si tam musí nastavit ručně.

## Krok 4 – Layout repozitáře

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
| `<projekt>/CLAUDE.md` (kontejner) | jen popis layoutu, odchylky a import toho druhého | pouze tenhle krok 4 |
| `<projekt>/main/CLAUDE.md` (**projektový**) | všechno ostatní – metadata, struktura, autocommit, paměť, typ, doménové importy | kroky 2, 4, 6, 8, 9, 10, 11, 12 |

**Kdykoli dál v tomhle skillu čteš „projektový `CLAUDE.md`“, myslí se `main/CLAUDE.md`.** Totéž platí pro `README.md`, `docs/*` a `.gitignore` – všechny patří do `main/`. Jedinou výjimkou je `.claude/settings.local.json`: ten patří do **kořene kontejneru**, protože odtud se pouští session a odtud si ho Claude Code čte. Tenhle skill ho **nezakládá** – vznikal v kroku, který zmizel se zrušeným autopromptem –, ale existuje-li, patří tam.

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

*`create`:* krok 2 už `CLAUDE.md` založil v kořeni, protože tehdy ještě nebylo rozhodnuto o layoutu. **Přesuň ho teď do `main/`** (`mv <projekt>/CLAUDE.md <projekt>/main/CLAUDE.md`) a v kořeni na jeho místo napiš stub. Totéž udělej s čímkoli dalším, co v kořeni mezitím vzniklo a patří do projektu.

*Konverze existujícího projektu:* původní `CLAUDE.md` se přesunul do `main/` spolu se zbytkem repozitáře a **je správně tam** – nech ho být, jen do něj dál doplňuj. V kořeni založ nový, prázdný stub.

Po tomhle kroku si **ověř výsledek** a vypiš ho uživateli: v kořeni smí být jen `.bare/`, `.git`, `CLAUDE.md` (stub) a `.claude/`; `README.md`, `docs/` a projektový `CLAUDE.md` musí být v `main/`.

Upozorni uživatele, že **při příštím spuštění dostane dialog na schválení externího importu a musí ho odsouhlasit** – při odmítnutí se importy pro ten projekt trvale vypnou a dialog se už neukáže.

### Náprava špatně rozděleného kontejneru

*`adopt`, kde worktree layout už je.* Najdeš-li v kořeni kontejneru projektové soubory, které tam nepatří – plnohodnotný `CLAUDE.md` s pravidly místo stubu, `README.md`, `docs/` – nabídni nápravu: přesun do `main/` a nahrazení kořenového `CLAUDE.md` stubem. Ukaž konkrétní seznam souborů a nech si to potvrdit, protože jde o přesouvání obsahu.

Existují-li oba `CLAUDE.md` a mají překrývající se sekce, **obsah slouč do `main/CLAUDE.md`** a v kořeni nech jen stub; nikdy jeden z nich mlčky nepřepiš.

Přesun je `git mv` jen tehdy, je-li zdroj verzovaný – v kořeni kontejneru **nikdy není**, takže tam jde o obyčejný `mv`. Po přesunu soubory v `main/` commitni.

## Krok 5 – Standardní struktura: režim umístění

Kroky 5 až 8 zakládají standardní strukturu. **Řiď se `~/Dev/context/structure/structure.md`** – ten je autoritativní, tyhle tři kroky jsou jen provedení.

Standardní soubory leží buď v `docs/`, nebo přímo v kořeni projektu. Obojí je rovnocenné.

*`create`:* zeptej se (AskUserQuestion, jedna otázka):

| Volba | Popis pro uživatele |
|---|---|
| `docs/` (výchozí) | Meta-vrstva odděleně od vlastní práce. Sedí na projekt s kódem nebo obsahem. |
| `root` | Soubory přímo v kořeni. Sedí na knowledge base a malé projekty, kde by `docs/` byl prázdný obal. |

*`adopt`:* režim **detekuj a rovnou zapiš**, neptej se. Leží-li `todo.md` nebo `decisions.md` v kořeni → `root`; leží-li v `docs/` → `docs/`; nenajdeš-li ani jedno → `docs/`. Co jsi zjistil a zapsal, **řekni nahlas** v závěrečném souhrnu. Najdeš-li soubory na obou místech, je to nepořádek, ne třetí režim – vypiš, co je kde, a nech si vybrat, na který režim to srovnat.

**Ve worktree layoutu** je kořen projektu `main/`, ne kořen kontejneru (viz krok 4).

Zapiš do bloku metadat v `CLAUDE.md`, za řádek `Slug`:

```
- **Struktura:** docs/
```

## Krok 6 – Standardní struktura: které soubory založit

Povinný je jen `CLAUDE.md`. U zbytku se zeptej (AskUserQuestion, `multiSelect: true`, vše předvybrané):

| Soubor | Popis pro uživatele |
|---|---|
| `README.md` | Co projekt je, pro člověka. U privátního projektu bez publika nemusí být. |
| `todo.md` + `backlog.md` + `done.md` | Fronta rozhodnutých úkolů, zásobník nezávazných nápadů a záznam hotového. **Jedna volba pro všechny tři** – samostatně nedávají smysl. |
| `decisions.md` | Co jsme rozhodli a proč, včetně zamítnutých variant. |
| `rules.md` | Principy, ve kterých se projekt pohybuje. |

Nezaložený soubor **není odchylka** – vznikne, až bude potřeba. Do `CLAUDE.md` (krok 7, *Zápis*) vypiš jen ty, které vznikly.

`requirements.md`, `architecture.md` a `plan.md` **nezakládej**, vznikají prací přes `/specify` a `/breakdown`.

### Produktové podklady

Druhá otázka, **jen u projektu, kde se staví produkt** – ne u konfiguračního repozitáře, znalostní báze pro sebe ani jednorázového nástroje. Definici všech pěti drží `~/Dev/context/structure/structure.md`, *Produktové podklady*; tady se jen vybírá.

`AskUserQuestion`, `multiSelect: true`, **nic předvybrané** – opačně než u standardních souborů. Většina projektů nemá ani jeden a předvybraný seznam by je odklikl všechny:

| Soubor | Popis pro uživatele |
|---|---|
| `competition.md` | Kdo je konkurence, co umí, za kolik – a čím se proti nim vymezíme. Nemá smysl u interního nástroje ani zakázky. |
| `risks.md` | Co je na produktu rizikové a co se kvůli tomu v návrhu změní. |
| `scenarios.md` | Co s produktem uživatel dělá, krok za krokem. Slouží i testování, nápovědě a FAQ. |
| `glossary.md` | Jak se v téhle doméně čemu říká. Vyplatí se, plete-li se víc entit naráz. |
| `pricing.md` | Tarify, limity, trial, co po expiraci – jen u produktu, který se prodává. |

**Soubory nezakládej.** Prázdný `competition.md` předstírá úvahu, která se nestala. Vybrané jen **zapiš do `CLAUDE.md`** (krok 7, *Zápis*) jako závazek; vzniknou prací v `/discovery` a `/specify`, a `/cleanup` pak podle toho seznamu pozná chybějící dokument od nechtěného.

*`adopt` a `update`:* co už existuje, ber jako zvolené. Existuje-li soubor, který v `CLAUDE.md` zapsaný není, doplň zápis; je-li zapsaný a nevznikl, zmiň to a nech rozhodnout, jestli se čeká, nebo se závazek ruší.

*`adopt`:* co už existuje, ber jako zvolené; ptej se jen na to, co chybí.

## Krok 7 – Standardní struktura: obsah

`README.md` u nového projektu: nadpis s **lidským názvem** a popiskem z kroku 1 jako prvním odstavcem – tam se popisek smí rozvést do víc vět. U existujícího projektu zkontroluj, že nadpis a první odstavec sedí s blokem metadat v `CLAUDE.md`; rozcházejí-li se, srovnej je. Soubory v `docs/` zakládej **prázdné, jen s nadpisem** – obsah nevymýšlej dopředu.

**README je pro člověka, ne pro Clauda.** Definici, co do něj patří a co ne, má `~/Dev/context/structure/structure.md`, sekce `README.md`; drž se jí doslova. U existujícího projektu README **projdi celé** a co je normativní pokyn pro Clauda – pravidla práce v repozitáři, konvence pojmenování, povinnost něco udržovat, odkaz na to, čím se má Claude řídit – přesuň do `CLAUDE.md`, `docs/rules.md` nebo `docs/decisions.md` podle povahy. Nekopíruj, přesouvej: informace má žít na jednom místě.

### Migrace staršího pojmenování

*`adopt`:* najdeš-li starší varianty, nabídni přejmenování přes AskUserQuestion (jedna otázka na všechny nálezy dohromady, protože jde o jedno rozhodnutí):

| Staré | Nové |
|---|---|
| `TODO.md` v rootu | `todo.md` na místě podle režimu |
| `rozhodnuti.md` | `decisions.md` |
| `zasady.md` | `rules.md` |
| `prd.md` | `requirements.md` |
| `design.md` | `architecture.md` |

Cílové umístění se řídí režimem z kroku 5. `TODO.md` velkými písmeny v kořeni **není** režim `root` – je to staré pojmenování, které se migruje tak jako tak.

Přejmenovávej přes `git mv`, ať se zachová historie. Po přejmenování **projdi celý repozitář a aktualizuj všechny odkazy** na staré názvy – v `CLAUDE.md`, `README.md`, dokumentaci i komentářích. Existuje-li cílový soubor už také, obsah **slouč** a na sloučení upozorni; nikdy nepřepisuj.

### Zápis do CLAUDE.md

Přidej sekci – konkrétní deklaraci, ne opis konvence:

Vypiš **jen soubory, které v projektu opravdu jsou**, s cestou podle zvoleného režimu:

```
## Struktura a dokumentace

Projekt drží standardní strukturu podle `~/Dev/context/structure/structure.md`:

- `README.md` – co projekt je, pro člověka (ne instrukce pro Clauda)
- `docs/todo.md` – co je odložené na později, ale rozhodnuté, že se to udělá
- `docs/backlog.md` – nezávazné nápady, o kterých se nerozhodlo; vybírá se z nich, když se řeší, co dál
- `docs/done.md` – co je hotové
- `docs/decisions.md` – co jsme rozhodli a proč, včetně zamítnutých variant
- `docs/rules.md` – principy, ve kterých se projekt pohybuje

Všechny tyhle soubory **aktualizuj průběžně sám a bez vyžádání**, ve chvíli, kdy rozhodnutí padne, princip se vybrousí nebo se něco odloží. Nečekej na konec session ani na `/cleanup`.
```

Vybral-li uživatel v kroku 6 nějaké **produktové podklady**, připoj pod ten seznam druhý – i u těch, které ještě nevznikly. Je to závazek, ne inventura:

```
**Produktové podklady**, které tenhle projekt vede (zakládají se prací, ne dopředu):

- `docs/competition.md` – kdo je konkurence, co umí a jaká je proti nim naše pozice (`/discovery`)
- `docs/risks.md` – co je na produktu rizikové a co se kvůli tomu v návrhu změnilo (`/discovery`)
- `docs/scenarios.md` – co s produktem uživatel dělá, krok za krokem (`/specify`)

Platí pro ně táž povinnost průběžné aktualizace jako pro soubory výš.
```

Nevybral-li žádný, **sekci nezakládej** – prázdný nadpis tvrdí, že se na to zapomnělo.

## Krok 8 – .gitignore

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
.claude/run/
```

`.claude/run/` je běhový stav přerušitelných skillů (`~/Dev/context/structure/structure.md`, *Běhový stav skillů*). **Řádek doplň i do existujícího `.gitignore`**, který ho ještě nemá – mění se po každém tahu, takže v projektu se zapnutým autocommitem by se donekonečna commitoval. Zbytek existujícího souboru nech být.

Existuje-li, **nepřepisuj ho** – jen doplň chybějící řádky z jádra a vypiš, co jsi přidal.

## Krok 9 – Autocommit

Zeptej se (AskUserQuestion): zapnout autocommit? Ano/Ne. Při ano proveď totéž co `/autocommit on` (viz `~/.claude/skills/autocommit/SKILL.md`).

*`adopt`:* nejdřív **zjisti aktuální stav** – hledej sekci `Autocommit` v projektovém `CLAUDE.md` **bez ohledu na úroveň nadpisu** (`##` i `###`) a bez ohledu na to, pod čím je zanořená. Aktuální stav uveď v otázce, ať uživatel ví, co mění. Je-li zapnutý, ale zapsaný jinak než nadpisem `## Autocommit` v nejvyšší úrovni – typicky podnadpisem pod zaniklou sekcí `## Automatické akce` –, **srovnej ho na dnešní tvar** a řekni to; jinak ho `/autocommit` příště nenajde a bude ho hlásit jako vypnutý.

## Krok 10 – Paměťová politika

Zeptej se (AskUserQuestion): „Má Claude v tomto projektu ukládat poznatky do trvalé Memory, nebo vše explicitně do lokálních .md souborů?“ Možnosti: **Jen lokální .md soubory (doporučeno)** / **Normální chování (Memory povolena)**.

Při první volbě přidej do `CLAUDE.md`:

```
## Paměť

Neukládej nic do trvalé Memory (`~/.claude/projects/.../memory/`). Vše, na čem se domluvíme – rozhodnutí, kontext, poznámky – ukládej explicitně do souborů projektu podle `~/Dev/context/structure/structure.md`. Ty jsou jediný zdroj pravdy pro tento projekt, i když harness bude nabádat k zápisu do Memory.
```

## Krok 11 – Typ projektu

**Kroky životního cyklu do popisu typu nevypisuj**, odkaz na *Životní cyklus projektu* v `~/.claude/RULES.md` stačí. Je to zvláštní případ obecného pravidla *Neopisuj seznam, který má vlastní zdroj pravdy* (`~/.claude/skills/SKILLS.md`, *Jak se píše text uvnitř*), kde stojí i to, čím se vykoupilo.

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

- **Vývoj** – „Vývojářský projekt – postupuj podle *Životního cyklu projektu* v `~/.claude/RULES.md`, celého a v pořadí, které tam stojí.“ Navíc přidej pravidlo: „Před implementací nové funkce nejdřív aktualizuj příslušný dokument v `docs/` (doc-first).“
- **Web** – „Webové rozhraní – obsah, struktura, šablony, ne proces zadání a plánu.“
- **Nasazení webové analytiky** – „Implementace měření na cizím webu – revize existujícího nastavení, měřicí plán, GTM, GA4, consent, reklamní systémy. Výstupem je funkční a doložitelné měření plus dokumentace, ne aplikační kód.“ Navíc přidej pravidlo: „Každá změna v měření musí být před publikováním ověřená v Preview/DebugView a po nasazení znovu na produkci; do `docs/decisions.md` patří i to, co se měřit záměrně nebude a proč.“
- **Psaní a obsah** – „Projekt zaměřený na psaní a obsah, ne na vývoj software – bez procesu zadání a plánu.“
- **Data a výzkum** – „Jednorázová datová/výzkumná analýza – výstupem jsou zjištění a report, ne nasazovaný kód.“
- **Ostatní** – „Projekt mimo výše uvedené kategorie.“

## Krok 12 – Kontrakt příkazů a zelená linka

**Jen u projektu, ve kterém se něco spouští** – tedy typ *Vývoj*, *Web*, nebo kdekoliv, kde v repozitáři najdeš `package.json`, `composer.json`, `Makefile`, `pyproject.toml` a podobně. U obsahového, znalostního nebo výzkumného projektu **krok přeskoč a řekni to jednou větou**; kontrakt tam nemá co dělat.

**Návrh napiš sám, uživatel ho jen potvrdí.** Přečti `package.json` (`scripts`), `composer.json`, `Makefile` nebo obdobu a vyplň, co projekt opravdu má. **Nevymýšlej příkazy, které v projektu nejsou** – řádek, který nikam nevede, je horší než chybějící řádek.

Zapiš do projektového `CLAUDE.md` sekci `## Příkazy`:

```markdown
## Příkazy

- test:      npm test
- typecheck: npm run typecheck
- lint:      npm run lint
- build:     npm run build
- dev:       npm run dev
- e2e:       npx playwright test
- coverage:  npm run coverage
- audit:     npm audit --omit=dev
- mutation:  npx stryker run
```

Zapisuj **jen ty klíče, které projekt opravdu umí spustit** – vymyšlený příkaz je horší než chybějící. U klíče, který chybí, napiš pod seznam, co tím odpadne: bez `dev` nemá `/attack` co spustit, bez `e2e` neproběhne průchod aplikací před nasazením, bez `coverage` neporovná `/review` pokrytí s prahem.

Chybí-li projektu něco z toho úplně (typicky testy u nového projektu), **řádek vynech a řekni to** – ať je vidět, co se nebude kontrolovat. Doplní se, až to vznikne.

**Co tím vzniká.** Globální `Stop` hook `~/.claude/green-line.sh` od téhle chvíle po každém tahu spustí `typecheck`, `lint` a `test` a **nepustí Clauda ukončit práci nad červeným stavem**. Hook je registrovaný jednou v `~/.claude/settings.json`, takže se nikde nic dalšího **neinstaluje** – ale spustit se v projektu ještě nesmí: chybí mu souhlas, viz níž. Vypnout se dá souborem `.claude/no-green-line` v projektu nebo proměnnou `CLAUDE_NO_GREEN_LINE=1`.

**Uživatel musí vydat souhlas, jinak linka neběží.** Kontrakt je kód v repozitáři a hook běží mimo permission systém, takže se souhlas dává jednou za projekt. Vypiš uživateli příkaz, ať ho spustí sám – **nespouštěj ho za něj**, tím by celá brána ztratila smysl:

```
~/.claude/green-line.sh --allow <kořen projektu>
```

Řekni mu u toho pravdu o tom, co schvaluje: souhlas platí **pro repozitář, ne pro ty konkrétní řádky**. `npm test` spustí, co je v `package.json`, a to se neschvaluje. Do cizího naklonovaného repozitáře souhlas nepatří.

Definice a prahy jednotlivých bran jsou v `~/Dev/context/coding/coding.md`, *Ověřování a brány kvality*. Řekni uživateli jednou větou, co se právě zapnulo – ne aby ho to překvapilo, až mu hook poprvé zablokuje konec tahu.

**Zapni i brány, které se nespouštějí příkazem, ale konfigurací.** Kontrakt říká, *čím* se kontroluje; tyhle určují, *jak přísně*. Bez nich zůstanou prahy z `coding.md` jen napsané a nikdo je neměří:

1. **Přísnost překladače.** Ověř, že konfigurace projektu drží řádek *Přísnost překladače* z tabulky bran – u TypeScriptu je to `tsconfig.json`, u ostatních jazyků odpovídající přepínač (Python `mypy --strict`, Go `go vet`, PHP `declare(strict_types=1)` a maximální úroveň statické analýzy). Chybí-li, **navrhni změnu a nech ji potvrdit** – u staršího projektu může zapnutí `strict` vyrobit stovky chyb naráz, takže to nikdy neprováděj rovnou.
2. **Metriky složitosti v lintru.** Prahy z řádku *Metriky složitosti* přenes do konfigurace lintru – v ESLintu jsou to pravidla `complexity`, `max-lines-per-function`, `max-depth`, `max-params`. **Hodnoty opisuj z tabulky, ne odsud:** kdyby stály na dvou místech, rozejdou se. U existujícího projektu jich naráz vyplavou stovky, takže se nabízí nastavit je jako varování – jenže **varování `lint` neshodí, a brána se tím vypne**. Je to změkčení prahu, které podle `coding.md` smí schválit **jen člověk a s důvodem zapsaným do `docs/decisions.md`**, a to i s termínem, kdy se přitvrdí. Zeptej se tedy a rozhodnutí nech zapsat; sám to nezměkčuj.
3. **Vlastní pravidla statické analýzy.** Ptej se, jestli projekt má pravidlo, které by šlo zakódovat: do `.semgrep/` patří **projektová znalost, kterou model nemá** – „tenhle ORM pattern u nás nepoužíváme, dělá N+1“, „sem se nesmí volat přímo, jde se přes službu“. **Existuje-li takové pravidlo, adresář založ a rovnou ho tam zapiš** i s poznámkou, k čemu je. Neexistuje-li, nezakládej nic – prázdný adresář pro jistotu je jen další nepořádek.

**Nasazuje se projekt někam?** Zjisti to (`vercel.json`, `netlify.toml`, `.github/workflows/`) a najdeš-li automatické nasazení z produkční větve, zapiš to do `## Nasazení` v `CLAUDE.md` i s upozorněním, že **merge do produkční větve je samotné nasazení** – detail řeší `/release`.

## Krok 13 – Doménové checklisty

Checklistů je devět a `AskUserQuestion` bere najednou nejvýš čtyři volby (týž strop jako v kroku 11). Ptej se **ve třech kolech**, všechna s `multiSelect: true`. **Kola se dělí tematicky, ne aby byla plná** – uživatel odpovídá na otázku, ne na seznam, a otázka musí jít položit jednou větou. Volby předvyplň podle typu z kroku 11, ale nech uživatele rozhodnout – vývojářský projekt bývá zároveň web, web bývá zároveň administrace.

| Kolo | Otázka | Volby |
|---|---|---|
| 1 | „Co všechno se v projektu bude dělat s kódem a rozhraním? Když nic, nic nezaškrtávej.“ | Psaní kódu · Webové rozhraní · Administrace / backoffice · Webová analytika a měření |
| 2 | „A co se v něm bude psát a učit? Když nic, nic nezaškrtávej.“ | Psaní českých textů · Česká typografie · Školení a kurzy |
| 3 | „A bude se v něm něco kreslit nebo promítat? Když nic, nic nezaškrtávej.“ | Vizuální tvorba a grafika · Prezentace a slajdy |

Volbu **Žádný** nikam nedávej – prázdný výběr v `multiSelect` ji nahrazuje. **Nový checklist zařaď do kola, kam tematicky patří**; teprve nevejde-li se do žádného pod strop čtyř voleb, přidej další kolo. Pátá volba do existujícího kola nepatří nikdy.

**Česká typografie je samostatná volba, ne přívažek k psaní textů.** Projekt s českým rozhraním nebo se slajdy sází česky, i když v něm žádný souvislý text nevzniká – a naopak by ho nemělo nic nutit brát si kvůli sazbě celý redakční standard.

Přehled všech devíti i s cílem importu:

| Volba | Import |
|---|---|
| Psaní kódu | `@~/Dev/context/coding/coding.md` |
| Webové rozhraní | `@~/Dev/context/web/web.md` |
| Administrace / backoffice | `@~/Dev/context/web/admin.md` |
| Webová analytika a měření | `@~/Dev/context/analytics/analytics.md` |
| Psaní českých textů | `@~/Dev/context/text/text.md` |
| Česká typografie | `@~/Dev/context/text/typography.md` |
| Školení a kurzy | `@~/Dev/context/training/training.md` |
| Vizuální tvorba a grafika | `@~/Dev/context/design/design.md` |
| Prezentace a slajdy | `@~/Dev/context/design/slides.md` |

U typu **Nasazení webové analytiky** přihraj napevno `analytics/analytics.md` a `web/web.md` (analytika se nasazuje do webu a překrývá se s ním v consentu a GDPR) a předvyplň `text/text.md` i `text/typography.md`, protože výstupem bývá auditní report nebo dokumentace pro klienta. `coding/coding.md` nabídni jen tehdy, když se v projektu opravdu píše kód – šablony, serverový endpoint, vlastní CMP.

U typu projektu, kde se připravuje **školení, kurz nebo workshop**, předvyplň `training/training.md` spolu s `text/text.md` a `text/typography.md` – materiály pro účastníky jsou text a řídí se vším trojím. Přihoď i `design/slides.md`, pokud k tomu vzniká promítaná prezentace.

`design/slides.md` nabízej i mimo školení – všude, kde se dělá deck: konferenční přednáška, prodejní pitch, prezentace výsledků klientovi. Importuje se **navíc** k `design/design.md`, ne místo něj.

`worktree.md` se tu nenabízí schválně – importuje se už v kroku 4, když si uživatel zvolí worktree layout.

`brand/brand.md` se tu nenabízí taky schválně, ale z jiného důvodu: je to **korpus, ne checklist**. Neříká, jak se něco dělá, ale jak to je – a projekt, který píše ven, si ho načte podle potřeby přes `~/.claude/CLAUDE.md`, kde je vedený mezi podmíněnými doménovými znalostmi. Importovat ho natvrdo do každého takového projektu by znamenalo vozit korpus tam, kde stačí sáhnout.

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

**Tímhle krok 13 končí. V režimu `adopt` teď jdi do kroku 14** a projekt zreviduj proti aktuálnímu standardu; teprve po něm následuje souhrn. V režimu `update` se sem nedojde – krok 14 tam proběhl místo průchodu otázkami.

## Krok 14 – Soulad se standardem

*Ve všech režimech kromě `create`.* Projde se **celý projekt proti tomu, jak standardy vypadají dnes**, a co se rozešlo, se dorovná. Kdy se krok dělá:

| Režim | Kdy |
|---|---|
| `update` | **místo** průchodu otázkami – volby, které kdysi padly, se znovu nepokládají |
| `adopt` | **po** krocích 1–13, těsně před souhrnem – teprve tam je ustaveno, jak má projekt vypadat |
| `create` | vůbec; v adresáři, který právě vznikl, není co revidovat |

**Proč i u existujícího projektu:** otisk `/project` (blok metadat) v něm chybí i tehdy, když ho nastavovala starší verze skillu, která blok ještě nezakládala. Takový projekt vypadá jako neošetřený, ale dokumentaci má z doby, kdy platil jiný standard – a to je zrovna ten případ, na který je tenhle krok.

**Standard si načti, neopisuj ho z hlavy.** Rozdíl mezi projektem a tvou pamětí není nález – tvoje paměť je zrovna to, co je zastaralé. Než začneš kontrolovat, přečti si:

- `~/Dev/context/structure/structure.md` **celý** – definuje, které soubory jsou, co do kterého patří a jak je uvnitř seřazený;
- `~/.claude/RULES.md` – zejména *Životní cyklus projektu* (jaké kroky životního cyklu dnes existují) a *Co do tohoto souboru nepatří* (kam co patří);
- `~/Dev/context/coding/coding.md`, *Ověřování a brány kvality* – jen u projektu, ve kterém se něco spouští;
- `~/Dev/context/worktree/worktree.md` – jen u worktree layoutu;
- výpisy `ls ~/.claude/skills/` a `ls ~/Dev/context/*/` – aktuální inventář skillů a doménových znalostí, proti kterému se ověřují odkazy a importy.

Postupuj po oblastech níž. U každé platí **dvourychlostní režim** ze *Zásad*: co je mechanické a jednoznačné, oprav rovnou a jen to vypiš; co přepisuje nebo maže existující obsah, předlož a nech potvrdit. **Vyžaduje-li nález volbu**, kterou umí jen některý z dalších kroků (typ projektu, doménové importy, kontrakt příkazů), udělej ten krok – v režimu `adopt` je to návrat, v `update` se otevírá jen kvůli tomu nálezu – tady je popsané, *co se kontroluje*, tam *jak se to nastavuje*.

| Oblast | Co ověřit | Kde je pravda |
|---|---|---|
| Blok metadat | Je na začátku projektového `CLAUDE.md`, má dnešní tvar a pořadí řádků, slug sedí s adresářem, `Struktura` sedí se skutečným umístěním souborů, řádky `Web` a `Repozitář` jsou jen tam, kde mají hodnotu. | `structure.md`, *`CLAUDE.md`* (krok 1 a 3) |
| Tři místa téhož údaje | Lidský název a popisek sedí v `CLAUDE.md`, v `README.md` a v Repository details na GitHubu (`gh repo view <owner>/<slug> --json description,homepageUrl`). Rozejít se smějí jen v tom, že README popisek rozvádí. | `structure.md`, *`CLAUDE.md`* (krok 3) |
| Sekce v `CLAUDE.md` | Každá sekce, kterou projekt má mít, tam je (struktura a dokumentace, příkazy, nasazení, autocommit, paměť, typ projektu, doménové standardy) – a **žádná zaniklá nepřebývá**. Seznam ber z `structure.md` a z kroků 5–13, ne z paměti. | `structure.md` (kroky 5–7 a 9–13) |
| Znění generovaných sekcí | **Nestačí, že sekce existuje – přečti, co v ní stojí, a porovnej s dnešní šablonou** v krocích 5–13. Sekce se zapsala jednou a od té doby zamrzla, kdežto šablona se vyvíjí. Zvlášť hlídej **citované seznamy, které mají vlastní zdroj pravdy**: kroky životního cyklu (`RULES.md`), jména skillů, prahy bran (`coding.md`), cesty do konfigurační vrstvy. Zastaralé znění **přepiš** a přepis vypiš – není to redakce obsahu, ale dorovnání šablony. Přibyl-li mezitím **typ projektu nebo doménový checklist**, který na projekt sedí líp než ten zapsaný, volbu za uživatele neměň – nabídni ji. | kroky 5–13 a jejich zdroje |
| Deklarace struktury | Seznam souborů v sekci *Struktura a dokumentace* sedí **přesně** na to, co v projektu opravdu je: nic nechybí, nic nepřebývá, cesty odpovídají režimu umístění. | krok 5, *Zápis do CLAUDE.md* |
| Soubory, které standard mezitím zavedl | **Projdi dnešní výčet standardních souborů ve `structure.md` proti tomu, co projekt má.** Chybí-li soubor, který projekt podle svých voleb mít má – typicky proto, že v době jeho založení ještě neexistoval –, **nabídni jeho doplnění** a zapiš ho do deklarace struktury. Neptej se, jestli o něm projekt „ví“; projekt neví nic, ví to jen standard. Volitelný soubor, který projekt vědomě nevede, se nezakládá – ale řekni, že se nabízel. | `structure.md`, *Které soubory vůbec vzniknou* |
| Umístění a názvy souborů | Standardní soubory leží všechny v jednom režimu (ne půl v `docs/`, půl v kořeni), nikde nezůstalo starší pojmenování. | krok 5 a *Migrace staršího pojmenování* |
| Vnitřní tvar dokumentace | Viz *Obsah dokumentačních souborů* níž – nejdražší část revize. | `structure.md`, sekce jednotlivých souborů |
| Kontrakt příkazů a brány | Každý řádek `## Příkazy` jde opravdu spustit (ověř proti `package.json`, `Makefile`, `composer.json`), nechybí klíč, který projekt umí, vědomě neaplikovaný má pomlčku. Souhlas se zelenou linkou ověř `~/.claude/green-line.sh --list`. | krok 12, `coding.md` |
| Odkazy ven z projektu | Každá cesta do `~/.claude/` nebo `~/Dev/context/` a každý zmíněný skill **existuje**. Vygrepuj je z `CLAUDE.md`, `README.md` i dokumentace a ověř proti inventáři výš. Tohle chytá přejmenované a zrušené věci v konfigurační vrstvě, aniž bys musel vědět, co se změnilo. | inventář z výpisů výš |
| Doménové importy | Cíle `@import`ů existují. Nepřibyla doménová znalost, která na projekt sedí a chybí mu? Nezůstal import, který už neplatí, protože se povaha projektu posunula? Přidání ani odebrání **nedělej sám** – nabídni v kroku 13. | krok 13, `~/.claude/CLAUDE.md` |
| Layout a `.gitignore` | Ve worktree layoutu leží projektové soubory v `main/` a v kořeni je jen stub. `.gitignore` má řádky z jádra včetně `.claude/run/`. | kroky 4 a 7 |

### Obsah dokumentačních souborů

Tohle je ta část, kterou žádný jiný skill neudělá: standard se mezitím posunul (rozdělení `todo.md` a `done.md`, oddělení `backlog.md`, nové sekce, pravidlo o řazení) a projekt v něm zůstal na starém. Projdi `todo.md`, `backlog.md`, `done.md`, `decisions.md` a `rules.md` **obsahem, ne jen existencí**, a ověř proti jejich sekcím v `structure.md`:

- **Hotové položky v `todo.md`.** Odškrtnuté a zjevně dokončené věci patří do `done.md` s datem dokončení. Seznam vypiš a **zeptej se přes AskUserQuestion** (*Přesunout všechny* / *Projít po jedné* / *Nechat být*) – jestli je něco hotové, ví uživatel, ne ty. Odškrtnutý krok uvnitř nedokončené položky se nepřesouvá.
- **Řazení.** Nejstarší nahoře, nové na konec – v `decisions.md` i `done.md`, i uvnitř kapitol. Obrácené pořadí **neotáčej sám**: je to přeskládání celého souboru. Ukaž, čeho se to týká, a zeptej se přes AskUserQuestion (*Srovnat podle standardu* / *Nechat, jak to je*).
- **Nezávazné nápady v `todo.md`.** Projekt založený dřív, než standard zavedl `backlog.md`, je má promíchané s frontou. Vyber položky, u kterých není rozhodnuto, že se udělají – poznáš je podle formulace („někdy by šlo“, „stálo by za úvahu“, „nápad do budoucna“). **Nerozhoduje, jestli je u položky termín nebo postup** – rozhoduje, jestli někdo řekl, že se to udělá. Odložení po MVP je plán a zůstává; otázka, kterou je potřeba zodpovědět, zůstává taky, protože zodpovědět ji někdo musí. Seznam vypiš a **zeptej se přes AskUserQuestion** (*Přesunout všechny do backlogu* / *Projít po jedné* / *Nechat být*) – co je závazek a co nápad, ví uživatel.
- **Zrcadlení sekcí.** Je-li `todo.md` členěné, `done.md` drží tytéž sekce. `backlog.md` je nezrcadlí – nápady se člení podle sebe, ne podle fronty.
- **Tvar záznamů.** Datum u hotové položky jako `(2026-08-28)`, řádky v *Průchody životním cyklem* a *Co proklouzlo* podle šablony v `structure.md`.
- **Sekce, které standard mezitím zavedl.** Prázdné je nezakládej. Ověř jen, že záznamy, které v souboru jsou, leží ve správné sekci – typicky že záznam o průchodu životním cyklem nesedí volně v `done.md` mimo *Průchody životním cyklem*.
- **Položka v nesprávném souboru.** Rozhodnutí zapsané v `todo.md`, princip v `decisions.md`, běhový stav skillu v `done.md`, hotová věc v `backlog.md` – přesuň tam, kam podle `structure.md` patří, a přesun vypiš. (Hotová položka z backlogu jde rovnou do `done.md`; je to úklid po chybném zařazení, ne druhá cesta – viz `structure.md`, *`backlog.md`*.)
- **Prázdná sekce `## Parkované v session`** se ruší.
- **`README.md` je pro člověka, ne pro Clauda.** Zůstal-li v něm normativní pokyn – pravidlo práce v repozitáři, konvence pojmenování, povinnost něco udržovat, odkaz na to, čím se má Claude řídit –, přesuň ho do `CLAUDE.md`, `rules.md` nebo `decisions.md` podle povahy. Postup i kritérium má krok 7 a `~/Dev/context/structure/structure.md`, sekce *`README.md`*. U staršího projektu je to častý nález: pravidla se tehdy psala do README, protože jiné místo nebylo.

### Výstup

Než začneš cokoliv měnit, **vypiš nálezy jako seznam** – co je v pořádku shrň jednou větou, každý rozpor uveď zvlášť s tím, co se s ním stane (opravím rovnou / potřebuju rozhodnout). Teprve pak jednej. Uživatel tak vidí rozsah dřív, než se sáhne na soubory.

Otázky pokládej **přes AskUserQuestion**, kdykoliv jde o volbu z pevné sady – tedy skoro vždy, protože nález má typicky dvě až tři možná vyústění (opravit / nechat být / rozhodnout jinak). Volný text si nech na to, co se z možností vybrat nedá.

**Nenajdeš-li nic, řekni to a skonči** – běh bez zásahu je platný výsledek revize, ne důvod něco vymýšlet.

**V režimu `update` tímhle běh končí – pokračuj rovnou krokem 15.** Kroky 1–13 se přeskakují celé; otevírá se z nich jen ten, který si vyžádal konkrétní nález. V režimu `adopt` se sem naopak přichází až od konce kroku 13 a souhrn následuje stejně.

### Proč se nikam neukládá, proti čemu se revidovalo naposledy

Nabízí se do projektu zapsat otisk – datum posledního běhu nebo hash `~/Dev/context` – a příště projít jen to, co se od té doby změnilo. **Vědomě se to nedělá.** Soulad se standardem je odvoditelný z toho, jak soubory vypadají teď, kdežto zapsaný otisk je tvrzení, které nikdo neověřuje: rozejde se se skutečností a vypadá přitom pořád stejně. Hlavně by ale zúžil kontrolu na diff standardu, a tím minul přesně ten případ, kvůli kterému skill vznikl – drift, který se do projektu nikdy nepropsal, protože ho tehdy nikdo nezpropagoval. Ten v žádném diffu od posledního běhu není.

## Krok 15 – Závěrečný souhrn

Vypiš přehledně:

- **Co bylo založeno** (`create`) nebo **co se změnilo a co zůstalo** (`adopt`).
- Metadata projektu (název, popisek, web) a kam všude se propsala, git a remote, layout repozitáře, standardní struktura, provedené migrace názvů, **kontrakt příkazů a zda se tím zapnula zelená linka, konfigurační brány (přísnost překladače, metriky složitosti, `.semgrep/`) – co se změnilo, co se jen navrhlo a co čeká na potvrzení**, autocommit, paměťová politika, typ, importované checklisty.
- **Co uživatel musí udělat ručně** – zejména odsouhlasení dialogu externích importů při příštím spuštění.

V režimu `adopt` vypiš i **co jsi záměrně nechal být a proč** – ať je vidět, že to nebylo opomenutí. A protože v tomhle režimu proběhl těsně předtím krok 14, **připoj za souhrn i jeho tři skupiny** (dorovnáno / čeká na rozhodnutí / vědomě nechal být) – jinak revize proběhne, ale její výsledek se nikde neukáže.

*Režim `update`:* souhrn je jiný – nevypisuje nastavení, ale **rozdíl proti standardu**. Tři skupiny: co bylo dorovnáno, co čeká na rozhodnutí uživatele a co jsi vědomě nechal být i s důvodem. Oblasti, které vyšly čistě, shrň jednou větou; jejich výčet nikoho nezajímá.

**Další krok:** /discovery, staví-li se produkt pro trh, jinak rovnou /specify – u dorovnaného projektu se rovnou pracuje

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Projekt je nastavený, můžeš v něm začít pracovat.`
- `Nastavený úplně není – zbývá: <konkrétní seznam>.`

V režimu `update` jednou z těchto:

- `Projekt je v souladu s aktuálním standardem.`
- `V souladu úplně není – zbývá: <konkrétní seznam>.`
