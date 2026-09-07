---
name: worktree
description: Skill se použije, když uživatel zadá "/worktree", "/worktree enable", "/worktree disable", "/worktree status", nebo chce v projektu zapnout či zrušit worktree layout – uspořádání, kde adresář projektu není pracovní adresář, ale kontejner s holým repozitářem a jedním pracovním adresářem na každou rozdělanou větev, aby nad projektem šlo běžet ve víc sessions naráz. Na rozdíl od /autocommit, který přepíná řádek v instrukcích projektu, tenhle skill přeskládá adresář a hýbe s .git. Větve nezakládá ani nemerguje – to je běžná práce podle pravidel, která skill do projektu nainstaluje.
argument-hint: [enable|disable|status]
allowed-tools: [Read, Write, Edit, Glob, Bash, AskUserQuestion]
---

# Worktree

## Co skill dělá

Zapíná a ruší **worktree layout** projektu – uspořádání, ve kterém adresář projektu není pracovní adresář, ale kontejner s jedním holým repozitářem (`.bare`) a několika pracovními adresáři, jeden na každou rozdělanou větev. Díky tomu může nad projektem běžet víc Claude sessions naráz, aniž si přepisují soubory.

| Režim | Co udělá |
|---|---|
| `status` (výchozí) | řekne, jestli layout je, a co je v něm rozdělané |
| `enable` | zřídí kontejner – u nového projektu i konverzí existujícího repozitáře |
| `disable` | převede projekt zpátky na obyčejný pracovní adresář |

**Pravidla provozu layoutu drží `~/.claude/WORKTREE.md`** – kde co leží, jak se zakládá a dokončuje větev, proč se v `main/` nepracuje a proč v kořeni kontejneru nefunguje git. Skill je **nevlastní**, jen si je importuje do stubu v kořeni kontejneru, aby platila v každé session projektu. Stojí v kořeni `~/.claude` vedle `RULES.md` a `STRUCTURE.md` schválně: čte je dvanáct skillů a `PREFLIGHT.md`, tedy i ten, kdo tenhle skill nainstalovaný nemá. Ta cesta je závazné rozhraní a nesmí se měnit tiše.

## Co skill nedělá

- **Nezakládá větve a nemerguje.** Zakládání větve, převzetí lokálního stavu a dokončení větve jsou běžná práce podle pravidel v `~/.claude/WORKTREE.md`, ne režim skillu. Skill, který bys musel volat pokaždé, když zakládáš větev, by byl horší než pravidlo, které prostě platí.
- **Nezakládá projekt.** Celé nastavení projektu včetně volby layoutu vede `/project`, který si tenhle skill volá jako jeden ze svých kroků. Tenhle skill je přepínač pro adresář, který už existuje.
- **Nerozhoduje, jestli se layout hodí.** To je volba uživatele; `/project` se na ni ptá, skill ji jen provede.
- **Necommituje.** Kontejner není pracovní strom a nic v něm ve gitu není. Změny v `main/` po konverzi zůstanou tak, jak byly.

## Fáze 0 – Pre-flight

Společný začátek je v `~/.claude/skills/PREFLIGHT.md`; platí z něj **bod 1** – kořen projektu. Body 3 až 5 neplatí: skill nesahá na kód a stav pracovního stromu ani zelená linka jeho běh neovlivní.

Tři vlastní odchylky:

- **Detekci dělej výhradně přes Glob**, ne `git` přes Bash – nenulový návratový kód by vyrobil červenou chybu a zbytečně vyděsil uživatele. Vlastní přeskládání pak Bashem.
- **Chybějící `.git` není důvod skončit.** Pre-flight u ostatních skillů říká „není-li to repozitář, skonči"; tady je prázdný adresář legitimní vstup režimu `enable`, který v něm založí nový projekt.
- **Bod 2 – projektový `CLAUDE.md` – neplatí.** Skill do něj nezapisuje a nic z něj nepotřebuje; hlavně by ale jeho blokující pokyn *„chybí-li `## Příkazy` a projekt má kód, zastav se"* zastavil `enable` nad prázdným adresářem, kde žádný projektový soubor ještě není. Stub v kořeni kontejneru je jiný soubor a zapisuje se až v fázi 2.

## Fáze 1 – Zjisti stav

Stav nese **tvar adresáře**, ne zápis v souboru – nemůže se tedy rozejít s realitou a nic dalšího se ověřovat nemusí:

| Nález | Stav |
|---|---|
| `.git` soubor **a** vedle něj `.bare/` | layout je zapnutý |
| `.git` adresář | layout není, je to obyčejný repozitář |
| ani jedno | není to repozitář – pro `enable` je to větev *nový projekt*, jinak to řekni a skonči |

**Stojíš-li v podadresáři**, jdi po `~/.claude/WORKTREE.md`, *Jak si skill najde projektový adresář*, nahoru ke kontejneru – jinak bys layout zapínal uvnitř layoutu.

## Fáze 2 – Proveď režim

### `status` (nebo žádný argument)

Vypiš, jestli je layout zapnutý. Je-li, vypiš i `git -C <kontejner> worktree list` a `git -C <kontejner> branch -a` – tedy co je rozdělané a jaké větve existují. Worktree, o kterém uživatel nejspíš neví, zmiň zvlášť; nemaž ho.

### `enable`

Je-li layout už zapnutý → jen to oznam, nic neměň. Jinak podle nálezu z fáze 1:

**Nový projekt** (adresář bez `.git`):

```bash
git init --bare .bare
printf 'gitdir: ./.bare\n' > .git
git worktree add main -b main
```

**Konverze existujícího repozitáře.** Přeskládává se `.git`, takže dva kroky před tím jsou povinné a žádný se nevynechává:

1. Ověř `git status` – necommitnuté nebo nepushnuté změny **nejdřív vyřeš**.
2. **Řekni nahlas, že jde o přeskládání adresáře, a nech si to potvrdit** (AskUserQuestion).

Zálohou je tu **přejmenovaný původní adresář** – `mv` na `.migrating` nechá všechny pracovní soubory na místě a bere si z něj jen `.git`, takže se nekopíruje nic navíc:

```bash
mv <projekt> <projekt>.migrating
mkdir <projekt>
mv <projekt>.migrating/.git <projekt>/.bare
git --git-dir=<projekt>/.bare config core.bare true
printf 'gitdir: ./.bare\n' > <projekt>/.git
git -C <projekt> worktree add main main
rm -f <projekt>/.bare/index <projekt>/.bare/COMMIT_EDITMSG
```

Ten `rm -f` není kosmetika: bare repo svůj `index` nikdy nepoužívá, ale po původním pracovním adresáři tam zůstane zamrzlý na posledním commitu před konverzí a `git diff --cached` z něj pak trvale hlásí smyšlené změny.

**Ověř, že se nic neztratilo**, a teprve pak smaž zálohu:

```bash
diff -r <projekt>.migrating <projekt>/main --exclude=.git   # musí být prázdné
rm -rf <projekt>.migrating
```

Netrackované a gitignorované soubory (`.env`, `node_modules`) přesuň do `main/` – je to jejich kanonické místo. `CLAUDE.md`, `README.md` a `docs/` v konverzi zůstávají v `main/`, kde jsou po `worktree add` už samy od sebe.

**V obou případech nakonec** zapiš do kořene kontejneru stub `CLAUDE.md` – a nic víc:

```
# <Název projektu>

Tenhle adresář není projekt, ale kontejner s worktree layoutem. Pravidla práce s ním:

@~/.claude/WORKTREE.md

Vlastní pravidla projektu jsou v `main/CLAUDE.md` a importují se odsud:

@main/CLAUDE.md

## Odchylky

- <odchylky konkrétního projektu od postupu výše, nebo že žádné nejsou>
```

U konverze je typický omyl nechat v kořeni původní `CLAUDE.md` – ten se přesunul do `main/` spolu se zbytkem repozitáře a **je správně tam**; v kořeni vzniká nový, netrackovaný stub. Pravidla projektu do stubu **nikdy nekopíruj**: dvě kopie se rozejdou a načtou se obě.

### `disable`

Není-li layout zapnutý → jen to oznam, nic neměň. Jinak nejdřív dvě zastávky, obě blokující:

1. **`git -C <kontejner>/main worktree list` musí hlásit jen `main`.** Zbyla-li rozdělaná větev, **skonči a řekni to** – slití nebo zahození větve je rozhodnutí uživatele, ne skillu.
2. **`git -C <kontejner>/main status --porcelain` musí být prázdný.**

Pak si zapamatuj větev (`git -C <kontejner>/main rev-parse --abbrev-ref HEAD`), nech si přeskládání potvrdit a **pořiď zálohu, kterou už dál nerozebereš** – na rozdíl od `enable`, kde zálohou je přejmenovaný původní adresář, se tady hýbe vším naráz:

```bash
cp -c -R <kontejner> <kontejner>.backup           # na APFS instantní; jinde bez -c

# 1) z main/ udělej samostatný repozitář
rm -f <kontejner>/main/.git                       # soubor "gitdir: …", má absolutní cestu
mv <kontejner>/.bare <kontejner>/main/.git
git -C <kontejner>/main config core.bare false
git -C <kontejner>/main symbolic-ref HEAD refs/heads/<vetev>
git -C <kontejner>/main worktree prune            # zapomeň registraci zrušeného worktree
git -C <kontejner>/main reset                     # obnov index z HEAD, pracovní strom nech být

# 2) přenes lokální stav kontejneru dovnitř
mv <kontejner>/.claude/* <kontejner>/main/.claude/   # cíl nejdřív vyrob: mkdir -p
rm -f <kontejner>/CLAUDE.md <kontejner>/.git      # stub a ukazatel na .bare

# 3) povyš main/ na projekt
mv <kontejner>/main <kontejner>.novy
rmdir <kontejner>                                 # musí projít – zbylo-li něco, zastav se
mv <kontejner>.novy <kontejner>
```

**`rmdir` je pojistka, ne úklid.** Projde jen nad prázdným adresářem, takže selže právě tehdy, když v kontejneru zbylo něco, o čem tenhle postup neví – nepoužívej místo něj `rm -rf` a **zastav se a ukaž uživateli, co tam leží**.

`.git` v `main/` je **soubor s absolutní cestou** do `.bare/worktrees/main`, takže přesun ho rozbije – proto se maže a nahrazuje adresářem. `symbolic-ref` je nutný, protože HEAD bare repozitáře ukazuje jinam než HEAD zrušeného worktree.

`.claude/settings.local.json` se stěhuje **z kořene kontejneru**, kde dosud žil; kdyby zůstal, zmizel by s ním – jsou v něm hooky a povolení, tedy netrackovaný stav, který nikde jinde není. **Přesouvej obsah, ne adresář:** projekt může mít vlastní trackované `main/.claude/CLAUDE.md`, a `mv` celého adresáře by v tom případě tiše vyrobil `main/.claude/.claude/` a uspěl.

**Ověř a teprve pak uklízej:**

```bash
git -C <kontejner> status                         # správná větev; jediný netrackovaný
                                                  # přírůstek smí být .claude/, který
                                                  # jsi tam právě přenesl
diff -r <kontejner>.backup/main <kontejner> --exclude=.git --exclude=.claude
rm -rf <kontejner>.backup
```

Záloha se během přeskládání nerozebírala, takže `diff -r` má proti čemu běžet. `.claude` se z porovnání vynechává schválně – v záloze leží v kořeni, v novém projektu uvnitř.

## Časté chyby

- **Zapnout layout uvnitř layoutu.** Stojíš-li ve worktree větve, `.git` je soubor a `.bare` vedle něj není – vypadá to jako obyčejný repozitář. Proto se ve fázi 1 jde nahoru ke kontejneru, ne jen do prvního adresáře s `.git`.
- **Nechat pravidla projektu v kořeni kontejneru.** Kontejner není pracovní strom: nic v něm není ve gitu, nikdy to nepůjde commitnout a zmizí to s adresářem.
- **Smazat zálohu před `diff -r`.** U `disable` je záloha jediná cesta zpátky – hýbe se vším naráz. U `enable` je to jinak: git data leží v novém `.bare` a pracovní soubory v `.migrating`, takže se dá obnovit obojí i bez kopie navíc.

## Fáze 3 – Závěr

Oznam výsledný stav a co jsi kvůli němu změnil – u `enable` a `disable` i to, kde leží záloha a že jsi ji po ověření smazal. Zůstala-li záloha ležet, protože ověření neprošlo, **řekni to jako první**, ne až na konci výpisu.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Worktree layout je v projektu <jméno> <zapnutý|vypnutý> a ověřený, můžeš pracovat dál.`
- `Přepnutí hotové není – brání tomu: <konkrétní seznam>.`
