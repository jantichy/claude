# Worktree layout projektu

Adresář projektu není pracovní adresář, ale **kontejner** s jedním git repozitářem a pracovním adresářem pro každou rozdělanou větev – aby nad projektem mohlo běžet víc session naráz, aniž si přepisují soubory a commitují cizí práci.

```
<container>/                    KONTEJNER – není ve gitu, nic se odsud neverzuje
├── .bare/                    holý git repozitář – jediné místo s daty; nikdy do něj nesahej
├── .git                      soubor "gitdir: ./.bare"
├── CLAUDE.md                 tenký rozcestník: popis layoutu + @main/CLAUDE.md
├── .claude/
│   └── settings.local.json   hooky a povolení – čte se odsud, protože session startuje tady
├── main/                     trvalý pracovní adresář hlavní větve
│   ├── CLAUDE.md             PROJEKTOVÝ CLAUDE.md – všechna skutečná pravidla projektu
│   ├── README.md
│   └── docs/                 todo.md, backlog.md, done.md, decisions.md, rules.md
└── <branch>/                  dočasné pracovní adresáře rozdělaných větví
```

Hlavní větev je `main`; jmenuje-li se ve starším projektu jinak, platí tohle pro ni. Soubor drží provoz layoutu; zřízení a zrušení kontejneru vede `/worktree` (`~/.claude/skills/worktree/SKILL.md`).

## Na začátku session

Session se pouští z **kořene kontejneru**, aby `/resume` nabízel session ze všech větví na jednom místě. Pak se přesuň:

| Uživatel chce | Kam |
|---|---|
| dělat změny – featuru, opravu, refactoring | nová větev + nový worktree |
| jen se zeptat, vysvětlit, najít, přečíst | `main/`, bez zakládání čehokoliv |
| pokračovat v rozdělané práci | do příslušného existujícího podadresáře |

Nejsi-li si kategorií jistý, zeptej se dřív, než založíš větev.

## Co žije v kontejneru a co v pracovním adresáři

Kontejner není ve gitu – co v něm leží, nejde commitnout. Claude Code při startu načítá `CLAUDE.md` z adresáře spuštění a nad ním, z podadresářů až při čtení. Z toho plyne rozdělení, které se nesmí prohodit:

| Soubor | Kde |
|---|---|
| `CLAUDE.md` s pravidly projektu, `README.md`, `docs/*` | `main/` (a tím v každém worktree) – patří do gitu |
| `CLAUDE.md` kontejneru | kořen – jen rozcestník, aby se projektový načetl při startu |
| `.claude/settings.local.json` | kořen – Claude Code ho čte z adresáře spuštění |
| `.env`, `node_modules/` | `main/`, odtud se přebírá |

### Rozcestník v kořeni kontejneru

`<container>/CLAUDE.md` nese jen popis layoutu, odchylky, import tohohle souboru a `@main/CLAUDE.md`; znění drží `/worktree`, režim `enable`. Relativní import se resolvuje vůči souboru, který ho obsahuje; řetěz importů smí mít nejvýš 4 úrovně. Ve worktree `<branch>/` se `<branch>/CLAUDE.md` načte při čtení z větve, takže platí pravidla té větve. **Pravidla projektu do rozcestníku nikdy nekopíruj** – načetly by se obě kopie.

## Založení větve

```bash
git -C <container> fetch
git -C <container> worktree add <container>/<directory> -b <branch>
git -C <container>/<directory> merge --ff-only origin/main
```

- **Před založením `git fetch`, po něm `merge --ff-only origin/main`** – ne lokální `main`, ten fetch neposune. Opakuj to při každém zakládání, ne jednou za session: vedlejší session mohla mezitím něco rozhodnout.
- Větev pojmenuj `feat/`, `fix/` nebo `docs/` podle povahy práce; **adresář plochým jménem bez lomítka** (`feat/payments` → `payments/`).
- Lokální stav z `main/` převezme hook sám (viz níž); jednou větou řekni, co jsi založil a co hook převzal.
- **Návrat do existující větve** (worktree byl smazán) jde bez `-b`; nejdřív se podívej do `git branch -a`.
- **Tutéž větev nelze mít ve dvou worktree** – dvě varianty téhož jsou dvě větve.

## Lokální stav se bere z `main/`

`main/` je kanonický zdroj netrackovaného lokálního stavu. **Symlinkuje se, co má zůstat sdílené, klonuje se, co se smí rozejít:**

| Co | Jak |
|---|---|
| `.env`, `.env.*` | symlink `../main/<soubor>` |
| `.env.local` | kopie – je to soubor pro odchylky jedné instance (`PORT`), přes symlink by se změna propsala do `main/` i do ostatních větví |
| `node_modules/` | `cp -c -R` (APFS clone) – symlink by `npm install` ve větvi přepsal balíčky v `main/`; kde klon nejde, vynechá se a závislosti se ve větvi nainstalují |
| build cache (`.next/`, `dist/`, `build/`, `out/`) | nepřebírat |
| soubor, který už ve větvi je (trackovaný `.env.example`) | nechat být |

**Vykonává to git hook `~/.claude/githooks/post-checkout`** nasazený globálně přes `core.hooksPath`, při každém `git worktree add` v kontejneru; co převzal, vypíše. Ručně to nedělej: deny pravidla na `.env` v `settings.json` zastaví i `ln -s`, takže by větev vznikla bez něj. Chybí-li po založení něco z tabulky, je hook rozbitý nebo odpojený – ohlas to, neobcházej. Výjimku z kontroly tajemství eviduje `~/.claude/BYPASS.md`.

Běží-li dev server ve víc větvích, potřebuje každý worktree vlastní port v `.env.local`. Model ho tam zapsat nesmí (deny na `.env.*`), takže to ohlásí a nabídne uživateli příkaz s `!` prefixem; přidělení portu hookem je rozhodnuté, ale zatím neudělané. `.claude/settings.local.json` se nepřebírá – žije v kořeni kontejneru, je nepovinný a vzniká sám s prvním povolením; nezakládej ho ručně.

## `main/` se nemaže a nepracuje se v něm

1. **Nikdy nemaž `main/`** – drží lokální stav, který není v gitu.
2. **Nedělej v `main/` změny** – slouží ke čtení, sdílení lokálního stavu a mergování.

**Jediná výjimka je hromadná migrace konfigurační vrstvy** – týž jednořádkový zápis do všech projektů naráz. Podmínky: strom je před zásahem čistý, commituje se jmenovitě ten soubor a diff se před commitem ověří řádek po řádku. Jakmile u projektu přemýšlíš, co napsat, je to práce a patří na větev.

## Větev žije, dokud uživatel neřekne jinak

**Nikdy nemerguj sám od sebe.** Po dokončení zadání commitni (má-li projekt autocommit), řekni, co je hotové, a zůstaň ve worktree – větev žije napříč prompty i session. Merguje se jen na výslovný pokyn („přimerguj to“, „ukliď tu větev“, volba v `/cleanup`); nejednoznačný pokyn si ověř. Jiná věc = další worktree vedle, ne merge té rozdělané.

## Dokončení větve

*Jen na výslovný pokyn.* Postup drží `/merge` (`~/.claude/skills/merge/SKILL.md`); z layoutu plyne navíc:

- **Příkazy nad hlavní větví pouštěj z `<container>/main`** – worktree dokončované větve se na konci maže.
- **`git worktree remove <container>/<directory>` až po ověřeném mergi**; odmítne-li kvůli neuloženému obsahu, `--force` jen po dotazu.
- **Rozpracovaný `main/` merge zastaví** – ohlas to.
- **Spojený stav vzniká ve worktree větve, ne v `main/`**, na kterém stojí ostatní session.

Bez `/merge`: hlavní větev nejdřív natáhni do pracovní, ověř tam kontraktem příkazů, pak merguj a ukliď.

## Kontrola stavu

```bash
git -C <container> worktree list    # co je rozdělané
git -C <container> branch -a        # jaké větve existují
```

Neznámý nebo opuštěný worktree ohlas, ale nemaž bez ptaní.

## V kořeni kontejneru git nefunguje

Kořen není pracovní adresář: `git status` a `git diff` skončí `fatal: this operation must be run in a work tree`, **`git diff --cached` vrátí smyšlený seznam** z indexu bare repa (po konverzi existujícího repa ho `/worktree enable` maže) a `git rev-parse --git-dir` uspěje, takže jako detekce nestačí. Nástroje, které pouštějí git nad adresářem projektu, musí bare repo přeskočit – nejlépe počítat nad `cwd`:

```bash
[ "$(git -C "$dir" rev-parse --is-bare-repository 2>/dev/null)" = "false" ] || exit
```

## Jak si skill najde projektový adresář

Jdi nahoru od `cwd` k `.git`; v kontejneru je `.git` soubor v kořeni i v každém worktree, rozhoduje `.bare`:

| Nález | Kde jsi | Co je projektový adresář |
|---|---|---|
| `.git` adresář | běžný projekt | ten adresář |
| `.git` soubor **a** vedle něj `.bare/` | kořen kontejneru | `<container>/main` |
| `.git` soubor **bez** `.bare/` vedle | worktree větve | ten adresář |

Projektové soubory čti a zapisuj v projektovém adresáři; do kořene patří jen `.claude/settings.local.json` a rozcestník. Jmenuje-li se hlavní větev jinak, najdi její worktree přes `git --git-dir=<container>/.bare worktree list`.
