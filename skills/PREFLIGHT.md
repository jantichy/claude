# Pre-flight skillu

Společný začátek běhu, který si skilly opisovaly. Odkazují se sem místo toho, aby ho měly každý svůj – změna se pak dělá na jednom místě, ne v deseti.

**Jak se to používá.** Skill má fázi `## Fáze 0 – Pre-flight`, v ní odkaz sem a **jen to, co má vlastního**: co dalšího si musí načíst, co ověřit, na co se zeptat. Nekopíruj sem nic zpátky a neopisuj odsud do skillu.

**Body 1 až 3 platí pro každý skill.** Body 4 a 5 jen tam, kde dávají smysl – u každého je napsané kde.

**Nezávislé čtecí operace pouštěj paralelně.** Zjišťování kořene, čtení `CLAUDE.md` a stav gitu na sobě nezávisí.

------

## 1. Kořen projektu a worktree layout

Kořen projektu je adresář s `.git`. Hledej ho **přes Glob, ne přes `git` v Bashi** – nenulový návratový kód by vyrobil červenou chybu, která uživatele zbytečně vyděsí. Zkus `.git`, pak `../.git`, `../../.git`, `../../../.git`.

**Najdeš-li vedle `.git` také `.bare/`, stojíš v kořeni kontejneru worktree layoutu** (`~/Dev/context/worktree/worktree.md`). Ten není pracovní strom: `git diff` ani `git status` v něm neprojdou a commitovat se tam nedá. Přesuň se do adresáře té větve, na které se má pracovat. Projektový `CLAUDE.md` je pak ten ve worktree, ne stub v kořeni kontejneru.

Není-li to git repozitář vůbec, řekni to a **skonči bez dalšího příkazu**.

## 2. Projektový `CLAUDE.md`

Leží buď v `<kořen>/CLAUDE.md`, nebo v `<kořen>/.claude/CLAUDE.md` – **zkontroluj obě místa**. Přečti si z něj:

| Co | Proč to potřebuješ |
|---|---|
| `## Příkazy` – *Kontrakt příkazů* | čím se ověřuje, čím se spouští, čím se staví |
| `### Autocommit` | jestli po ucelené změně commitovat a pushovat |
| `## Výjimky z obecných pravidel` | co je v tomhle projektu vědomá odchylka, a tedy **není nález** |
| Paměťová politika | píše se do Memory, nebo výhradně do souborů? |
| Doménové `@import`y | které standardy z `~/Dev/context/` v projektu platí |

**Chybí-li `## Příkazy` a projekt má kód**, zastav se a nabídni doplnění. Bez kontraktu nemá zelená linka co spouštět a práce by běžela bez brány. Podklad zjistíš z `package.json`, `composer.json`, `Makefile` nebo obdoby; návrh ukaž a nech potvrdit.

## 3. Stav pracovního stromu

Rozpracované změny **před** startem se smíchají s tím, co uděláš ty, a přestane být poznat, co je čí. Vypiš je (`git status --porcelain`) a zeptej se, jestli je commitnout, odložit, nebo pokračovat i tak.

U skillu, který nic nemění – čte, hlásí, radí – to stačí zmínit; blokovat kvůli tomu nemá smysl.

## 4. Zelená linka před startem

*Jen u skillů, které mění kód.*

Pusť příkazy z kontraktu dřív, než se dotkneš prvního souboru. **Dědíš-li červený stav z dřívějška, ohlas to a zeptej se** – jinak nepůjde poznat, co jsi rozbil ty. Podrobně `~/Dev/context/coding/coding.md`, *Ověřování a brány kvality*.

## 5. Rozsah změn na větvi

*Jen u skillů, které pracují nad tím, co se změnilo – ne nad celým projektem.*

```
git merge-base HEAD origin/HEAD 2>/dev/null || git merge-base HEAD main 2>/dev/null || git merge-base HEAD master
git diff --name-only <merge-base>...HEAD
git status --porcelain
```

Sjednoť commitnuté změny na větvi s necommitnutými a vynech smazané soubory. Jsi-li na hlavní větvi a diff je prázdný, vezmi necommitnuté změny; nejsou-li ani ty, řekni to a nabídni režim nad celým projektem, má-li ho skill.

**Zjisti, o kolik hlavní větev mezitím odskočila:**

```
git rev-list --count HEAD..origin/HEAD 2>/dev/null || git rev-list --count HEAD..main
```

Je-li výsledek nenulový, **řekni to a nabídni srovnání**. Rozsah se počítá proti bodu, ve kterém větev vznikla, takže cizí změna, která do hlavní větve přibyla mezitím, nespadá do rozsahu **ani jednoho** běhu – v tvém diffu není a v jejich zase není tvoje. Rozpor, kde jsou obě změny samy o sobě správné a dohromady rozbité (přejmenovaná funkce vs. nové volání, změněný default vs. nová větev, dvě migrace nad touž tabulkou), tak neprojde ničím.

**Neuspěje-li ani jeden `merge-base`, rozsah si nedomýšlej.** Nastává to ve třech běžných stavech: repozitář bez jediného commitu (`HEAD` neexistuje), hlavní větev pojmenovaná jinak než `main`/`master` bez nastaveného `origin/HEAD`, a čerstvý lokální repozitář bez remote. Ověř nejdřív `git rev-parse --verify HEAD` – selže-li, rozsahem jsou prostě necommitnuté změny a žádný diff se nedělá. Jinak zkus `git symbolic-ref --short refs/remotes/origin/HEAD`, a když ani to nevyjde, **zeptej se přes `AskUserQuestion`**, proti které větvi diffovat, s nabídkou z `git branch`. Špatně určený rozsah tiše prověří něco jiného, než si myslíš, a to je horší než se zeptat.

**Nad celým projektem** (režim `full` a obdoby) tenhle krok odpadá. Vynech `node_modules/`, `dist/`, `build/`, `vendor/`, `generated/`, `*.gen.*` a cokoliv v `.gitignore`.

------

## Na konci pre-flightu

**Shrň zjištěné do tří až pěti řádků** a pokračuj. Uživatel musí vidět, z čeho se vychází, dřív než se něco stane – ne až v závěrečném souhrnu, kdy už je pozdě to opravit.
