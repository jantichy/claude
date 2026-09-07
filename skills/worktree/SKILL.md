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

**Pravidla provozu layoutu drží `~/.claude/skills/worktree/worktree.md`** – kde co leží, jak se zakládá a dokončuje větev, proč se v `main/` nepracuje a proč v kořeni kontejneru nefunguje git. Skill ten soubor **importuje do projektu**, takže platí v každé session, aniž ho kdo vyvolá. Ta cesta je závazné rozhraní: importují ji stuby v kontejnerech a odkazuje na ni `~/.claude/skills/PREFLIGHT.md`, takže se nesmí měnit tiše.

## Co skill nedělá

- **Nezakládá větve a nemerguje.** Zakládání větve, převzetí lokálního stavu a dokončení větve jsou běžná práce podle pravidel v `worktree.md`, ne režim skillu. Skill, který bys musel volat pokaždé, když zakládáš větev, by byl horší než pravidlo, které prostě platí.
- **Nezakládá projekt.** Celé nastavení projektu včetně volby layoutu vede `/project`, který si tenhle skill volá jako jeden ze svých kroků. Tenhle skill je přepínač pro adresář, který už existuje.
- **Nerozhoduje, jestli se layout hodí.** To je volba uživatele; `/project` se na ni ptá, skill ji jen provede.
- **Necommituje.** Kontejner není pracovní strom a nic v něm ve gitu není. Změny v `main/` po konverzi zůstanou tak, jak byly.

## Fáze 0 – Pre-flight

Společný začátek je v `~/.claude/skills/PREFLIGHT.md`; platí z něj **body 1 a 2**. Body 3 až 5 neplatí: skill nesahá na kód a kontrakt příkazů jeho běh neovlivní.

Dvě vlastní odchylky:

- **Detekci dělej výhradně přes Glob**, ne `git` přes Bash – nenulový návratový kód by vyrobil červenou chybu a zbytečně vyděsil uživatele. Vlastní přeskládání pak Bashem.
- **Chybějící `.git` není důvod skončit.** Pre-flight u ostatních skillů říká „není-li to repozitář, skonči"; tady je prázdný adresář legitimní vstup režimu `enable`, který v něm založí nový projekt.

## Fáze 1 – Zjisti stav

Stav nese **tvar adresáře**, ne zápis v souboru – nemůže se tedy rozejít s realitou a nic dalšího se ověřovat nemusí:

| Nález | Stav |
|---|---|
| `.git` soubor **a** vedle něj `.bare/` | layout je zapnutý |
| `.git` adresář | layout není, je to obyčejný repozitář |
| ani jedno | není to repozitář – pro `enable` je to větev *nový projekt*, jinak to řekni a skonči |

**Stojíš-li v podadresáři**, jdi po `~/.claude/skills/worktree/worktree.md`, *Jak si skill najde projektový adresář*, nahoru ke kontejneru – jinak bys layout zapínal uvnitř layoutu.

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

**Konverze existujícího repozitáře.** Přeskládává se `.git`, takže tři kroky před tím jsou povinné a žádný se nevynechává:

1. Ověř `git status` – necommitnuté nebo nepushnuté změny **nejdřív vyřeš**.
2. Zálohuj celý adresář. Na macOS je `cp -c -R` (APFS clone) instantní a nezabírá místo navíc.
3. **Řekni nahlas, že jde o přeskládání adresáře, a nech si to potvrdit** (AskUserQuestion).

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

@~/.claude/skills/worktree/worktree.md

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

Pak si zapamatuj větev (`git -C <kontejner>/main rev-parse --abbrev-ref HEAD`), nech si přeskládání potvrdit a proveď ho tak, že se z `main/` stane projekt:

```bash
mv <kontejner> <kontejner>.migrating
mv <kontejner>.migrating/main <kontejner>
rm -f <kontejner>/.git                                  # soubor "gitdir: …", má absolutní cestu
mv <kontejner>.migrating/.bare <kontejner>/.git
git -C <kontejner> config core.bare false
git -C <kontejner> symbolic-ref HEAD refs/heads/<vetev>
git -C <kontejner> worktree prune                       # zapomeň registraci zrušeného worktree
git -C <kontejner> reset                                # obnov index z HEAD, pracovní strom nech být
```

`.git` v `main/` je **soubor s absolutní cestou** do `.bare/worktrees/main`, takže přesun ho rozbije – proto se maže a nahrazuje adresářem. `symbolic-ref` je nutný, protože HEAD bare repozitáře ukazuje jinam než HEAD zrušeného worktree.

Zbývá lokální stav z kořene kontejneru, který ve gitu nikdy nebyl:

- `.claude/settings.local.json` přesuň do `<kontejner>/.claude/` – nově je kořen pracovní adresář, takže tam sedí,
- stub `CLAUDE.md` **zahoď**; pravidla projektu přišla s `main/` a jsou na místě.

**Ověř a teprve pak uklízej:**

```bash
git -C <kontejner> status                                    # čistý strom, správná větev
diff -r <kontejner>.migrating/main <kontejner> --exclude=.git # musí být prázdné
rm -rf <kontejner>.migrating
```

## Časté chyby

- **Zapnout layout uvnitř layoutu.** Stojíš-li ve worktree větve, `.git` je soubor a `.bare` vedle něj není – vypadá to jako obyčejný repozitář. Proto se ve fázi 1 jde nahoru ke kontejneru, ne jen do prvního adresáře s `.git`.
- **Nechat pravidla projektu v kořeni kontejneru.** Kontejner není pracovní strom: nic v něm není ve gitu, nikdy to nepůjde commitnout a zmizí to s adresářem.
- **Smazat zálohu před `diff -r`.** Přeskládání `.git` je jediná operace tohohle skillu, která se nedá vzít zpátky jinak než ze zálohy.

## Fáze 3 – Závěr

Oznam výsledný stav a co jsi kvůli němu změnil – u `enable` a `disable` i to, kde leží záloha a že jsi ji po ověření smazal. Zůstala-li záloha ležet, protože ověření neprošlo, **řekni to jako první**, ne až na konci výpisu.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Worktree layout je v projektu <jméno> <zapnutý|vypnutý> a ověřený, můžeš pracovat dál.`
- `Přepnutí hotové není – brání tomu: <konkrétní seznam>.`
