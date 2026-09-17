# Worktree layout projektu

Uspořádání, ve kterém adresář projektu není pracovní adresář, ale **kontejner** s jedním git repozitářem a několika jeho pracovními adresáři – jeden na každou rozdělanou větev.

```
<projekt>/                    KONTEJNER – není ve gitu, nic se odsud neverzuje
├── .bare/                    holý git repozitář – jediné místo s daty; nikdy do něj nesahej
├── .git                      soubor "gitdir: ./.bare"
├── CLAUDE.md                 tenký rozcestník: popis layoutu + @main/CLAUDE.md
├── .claude/
│   └── settings.local.json   hooky a povolení – čte se odsud, protože session startuje tady
├── main/                     trvalý pracovní adresář hlavní větve
│   ├── CLAUDE.md             PROJEKTOVÝ CLAUDE.md – všechna skutečná pravidla projektu
│   ├── README.md
│   └── docs/                 todo.md, backlog.md, done.md, decisions.md, rules.md
└── <vetev>/                  dočasné pracovní adresáře rozdělaných větví
```

**Proč:** nad projektem běží typicky několik Claude session najednou, každá na jiné featuře. Ve sdíleném pracovním adresáři by si přepisovaly soubory a commitovaly si navzájem rozdělanou práci. Oddělený worktree na větev je jediná skutečná izolace; sdílejí přitom jeden `.bare`, takže to nestojí ani místo, ani čas.

Hlavní větev se jmenuje `main`. Narazíš-li na starší projekt, kde se jmenuje jinak, platí níž psané pro jeho hlavní větev bez ohledu na jméno.

**Tenhle soubor drží provoz layoutu** – co kde leží a jak se v tom pracuje. Platí pro každou session nad projektem s tímhle uspořádáním a čte ho `~/.claude/skills/PREFLIGHT.md` i skilly, které nad projektem běží. **Zřízení kontejneru a jeho zrušení sem nepatří** – to vede `/worktree` (`~/.claude/skills/worktree/SKILL.md`), který si tenhle soubor zároveň importuje do rozcestníku v kořeni kontejneru.

Leží v kořeni `~/.claude` vedle `RULES.md` a `STRUCTURE.md`, ne uvnitř skillu, **protože ho čte většina skillů i příprava** – tedy i ten, kdo `/worktree` nainstalovaný nemá.

## Obsah

- [Na začátku session](#na-začátku-session)
- [Co žije v kontejneru a co v pracovním adresáři](#co-žije-v-kontejneru-a-co-v-pracovním-adresáři)
- [Založení větve](#založení-větve)
- [Lokální stav se bere z `main/`](#lokální-stav-se-bere-z-main)
- [`main/` se nemaže a nepracuje se v něm](#main-se-nemaže-a-nepracuje-se-v-něm)
- [Větev žije, dokud uživatel neřekne jinak](#větev-žije-dokud-uživatel-neřekne-jinak)
- [Dokončení větve](#dokončení-větve)
- [Kontrola stavu](#kontrola-stavu)
- [V kořeni kontejneru git nefunguje](#v-kořeni-kontejneru-git-nefunguje)
- [Jak si skill najde projektový adresář](#jak-si-skill-najde-projektový-adresář)

---

## Na začátku session

Session se pouští z **kořene kontejneru**, ne z podadresáře – session se ukládají podle adresáře spuštění, takže `/resume` díky tomu nabídne session ze všech větví na jednom místě.

Stojíš tedy v kontejneru, ne v projektu. Prvním úkolem je přesunout se podle toho, co uživatel chce:

| Uživatel chce | Kam |
|---|---|
| dělat změny – featuru, opravu, refactoring | nová větev + nový worktree |
| jen se zeptat, vysvětlit, najít, přečíst | `main/`, bez zakládání čehokoliv |
| pokračovat v rozdělané práci | do příslušného existujícího podadresáře |

Když si nejsi jistý kategorií, **zeptej se**, než založíš větev – zbytečně založená větev je odpad, který pak někdo musí uklidit.

## Co žije v kontejneru a co v pracovním adresáři

Kontejner **není pracovní strom**: nic, co v něm leží, není ve gitu, nikdy se to nedá commitnout a zmizí to s adresářem. Zároveň Claude Code načítá při startu session `CLAUDE.md` z aktuálního adresáře a **z adresářů nad ním** – `CLAUDE.md` z podadresáře se načte až on-demand, když z něj něco čteš. Session přitom startuje v kontejneru.

Z těch dvou faktů plyne rozdělení, které se **nesmí prohodit**:

| Soubor | Kde | Proč |
|---|---|---|
| `CLAUDE.md` s pravidly projektu | `main/` (a tím ve všech worktree) | je to projektový soubor – patří do gitu a má se s větví vyvíjet |
| `CLAUDE.md` kontejneru | kořen kontejneru | jen tenký rozcestník, viz níž – existuje čistě proto, aby se ten projektový načetl při startu |
| `README.md`, `docs/*` | `main/` | projektové soubory, patří do gitu |
| `.claude/settings.local.json` | kořen kontejneru | hooky a povolení čte Claude Code z adresáře, ze kterého session startuje |
| `.env`, `node_modules/` | `main/`, odtud se přebírá | netrackovaný lokální stav, viz níž |

### Rozcestník v kořeni kontejneru

`<projekt>/CLAUDE.md` neobsahuje žádná pravidla projektu. Obsahuje popis layoutu, odchylky, **import tohohle souboru** a **import projektového `CLAUDE.md`** (`@main/CLAUDE.md`). Zakládá ho `/worktree` a jeho doslovné znění drží `~/.claude/skills/worktree/SKILL.md`, režim `enable`.

Relativní cesta v importu se resolvuje vůči souboru, který import obsahuje – `@main/CLAUDE.md` tedy míří na `<projekt>/main/CLAUDE.md`. Řetěz importů smí být hluboký nejvýš **4 úrovně**, takže kontejner → `main` → doménový standard se pohodlně vejde.

Když pracuješ ve worktree `<vetev>/`, načte se `<vetev>/CLAUDE.md` on-demand, jakmile v té větvi něco čteš. Pravidla té větve tedy platí, i když rozcestník v kořeni importuje verzi z `main`.

**Nikdy nekopíruj pravidla projektu do rozcestníku.** Dvě kopie se rozejdou a Claude pak dostane do kontextu obě, protože se načítají obě.

## Založení větve

```bash
git -C <projekt> worktree add <projekt>/<adresar> -b <vetev>
```

- Větev pojmenuj `feat/`, `fix/` nebo `docs/` podle povahy práce; zbytek názvu česky nebo anglicky podle toho, co je v projektu zvykem.
- **Adresář pojmenuj plochým jménem bez lomítka** – větev `feat/platby` patří do `platby/`, ne `feat/platby/`.
- Převezmi lokální stav z `main/` (viz níž) a řekni uživateli jednou větou, co jsi založil.

**Nejdřív si natáhni aktuální `main`.** Kontejner existuje právě proto, že nad projektem běží víc session naráz – takže `main` se mohl posunout od chvíle, kdy tahle session začala, a to i o práci, na kterou tvoje větev staví. Před založením proto `git fetch` a hned po založení `git merge --ff-only origin/main`; teprve pak začni pracovat. **Musí to být `origin/main`, ne `main`:** `git fetch` posune remote-tracking referenci, kdežto lokální `main` zůstane tam, kde byl – merge lokální větve by tedy nepřinesl nic a celý ten krok by tiše nedělal nic.

**Nestačí to udělat jednou na začátku session.** Zakládáš-li větev po delší práci, zopakuj to – jinak stavíš na stavu, který byl aktuální před hodinou. Pozná se to pozdě: konflikt nevznikne, jen se tiše rozhodne podruhé něco, co už rozhodla vedlejší session.

**Návrat do větve, která už existuje** (její worktree byl mezitím smazán) – bez `-b`:

```bash
git -C <projekt> worktree add <projekt>/<adresar> <vetev>
```

S `-b` by to spadlo na `branch already exists`. Nejdřív se proto podívej do `git branch -a`, jestli větev není.

**Tutéž větev nelze mít ve dvou worktree najednou.** Git to odmítne (`is already checked out at …`) a je to záměr – dva pracovní adresáře nad jednou větví by si přepisovaly commity. Chceš-li vedle sebe dvě varianty téhož, jsou to dvě větve. Je to i důvod, proč kontejner stojí na **holém** repozitáři: kdyby jeho kořen byl obyčejný pracovní adresář s checkoutnutým `main`, nešel by `main` rozbalit do podadresáře.

## Lokální stav se bere z `main/`

`main/` je **kanonickým zdrojem netrackovaného lokálního stavu**. Co není v gitu, ale je potřeba k práci, žije tam a odtud se přebírá.

| Co | Jak | Proč |
|---|---|---|
| `.env`, `.env.local` | symlink | jeden zdroj pravdy, tajemství na disku jednou, nová proměnná platí všude |
| `node_modules/` | `cp -c -R` (APFS clone) | instantní, nula místa navíc, ale vlastní kopie – větev si smí doinstalovat balíček, aniž rozbije ostatní |
| build cache (`.next/`, `dist/`, `build/`, `out/`) | nepřebírat | sdílená cache mezi větvemi je zdroj záhadných chyb |

Pravidlo: **symlinkuje se, co má zůstat sdílené, klonuje se, co se smí rozejít.** Symlinknuté `node_modules` je past – `npm install` v jedné větvi by přepsal balíčky v masteru.

Když dev server poběží ve víc větvích, poperou se o port. Řeš `.env.local` ve worktree s vlastním `PORT` – přebíjí symlinknutý `.env`.

`.claude/settings.local.json` se **z `main/` nepřebírá** – žije v kořeni kontejneru, protože odtud se pouští session a odtud si ho Claude Code čte. Do `main/` ani do větví nepatří vůbec.

**Je nepovinný a vzniká sám**, až když se v projektu udělí první povolení; v tabulce výš stojí kvůli umístění, ne proto, že by tam musel být. **Jeho absence tedy není vada** – znamená, že se nic projektového neudělilo a platí globální nastavení z `~/.claude/settings.json`. Nezakládej ho ručně jen proto, že chybí.

## `main/` se nemaže a nepracuje se v něm

1. **Nikdy nemaž `main/`** – žije v něm netrackovaný lokální stav, který v gitu není a nikde se nezálohuje.
2. **Nedělej v `main/` změny** – slouží ke čtení, ke sdílení lokálního stavu a k mergování. Práce patří do vlastní větve.

**Jediná výjimka je hromadná migrace konfigurační vrstvy** – týž jednořádkový zápis do všech projektů naráz, typicky přepis odkazu po přesunu standardu nebo doplnění přepínače do `CLAUDE.md`. Zakládat kvůli jednomu řádku větev ve dvaceti projektech stojí víc, než kolik izolace přinese. Platí pro ni tři podmínky a všechny tři se ověřují, ne předpokládají:

- pracovní strom je před zásahem **čistý** – jinak nevíš, co je čí,
- commituje se **jmenovitě ten jeden soubor**, ne `git add -A`,
- před commitem se **řádek po řádku ověří**, že v diffu není nic než ta migrace.

**Nerozšiřuj to na běžnou práci.** Kritérium je, že tentýž zápis jde do všech projektů a nikdo nad ním nerozhoduje projekt po projektu; jakmile se u některého zastavíš a přemýšlíš, co tam napsat, je to práce a patří na větev.

## Větev žije, dokud uživatel neřekne jinak

**Nikdy nemerguj sám od sebe.** Založit větev, udělat práci a hned ji mergnout zpátky je chyba – větev je pracovní prostor, ne obálka na jeden příkaz.

Po dokončení zadání tedy: commitni (má-li projekt autocommit), řekni, co je hotové, a **zůstaň ve worktree**. Větev zůstává otevřená napříč prompty i napříč session, klidně týden. Na další zadání ve stejném tématu prostě pokračuj ve stejné větvi.

Merguje se **jen na výslovný pokyn** – „tohle je hotové“, „přimerguj to“, „ukliď tu větev“, nebo volba *Přimergovat do main* v závěrečné otázce `/cleanup`. Není-li pokyn jednoznačný, zeptej se; předčasný merge se odestává hůř než pozdní.

Chce-li uživatel začít **jinou** věc, nemerguj tu rozdělanou – založ vedle ní další worktree. Právě proto to takhle je.

## Dokončení větve

*Až na výslovný pokyn uživatele.* **Jak se merguje, rozhoduješ sám a neptáš se** – pokyn „přimerguj“ míří na výsledek, ne na postup. Ptáš se jen tam, kde to níž výslovně stojí.

**Hlavní větev** se tu píše `main`; jmenuje-li se v projektu jinak, platí to pro ni (viz úvod). **Příkazy nad `main/` pouštěj z `<projekt>/main`, ne z worktree větve:** krok 4 ten worktree maže, a session, která v něm stojí, by přišla o pracovní adresář.

Celý postup proveď najednou a **průběžně hlas, co se povedlo** – merge nemá proběhnout mlčky. Vrátí-li příkaz jiný návratový kód, než s jakým krok počítá, nebo selže-li `pull`/`push`, zastav a ohlas to – nic neobcházej `--force` a větev nemaž.

### 1. Co merge zastaví

- **Necommitnuté změny ve worktree větve** – commitni je, patří-li k práci větve; soubor, který jsi nezměnil ty, nech být a ohlas ho (`~/.claude/RULES.md`, *Commituj jmenované cesty, ne `-A`*).
- **Rozpracovaný `main/`** – je to cizí práce a merge by se s ní promíchal; ohlas to a zastav.
- **`main` je nasazovací větev.** Stojí-li v `## Nasazení` projektového `CLAUDE.md`, že se z `main` automaticky nasazuje, je merge samotné nasazení a patří `/release` (`~/.claude/skills/release/SKILL.md`, *Nasazovací větev není integrační větev*). Zastav a řekni to.
- **Větev kola návrhu** (`/specify`) – pozná se podle toho, že ji jmenuje blok kola v `docs/todo.md` nebo záznam v `docs/done.md`, sekce `## Kola návrhu`. Neproběhl-li v ní zápis před sloučením (blok v `todo.md` ještě je), pusť v ní nejdřív `/specify`. Proběhl-li, pokračuj – ale krok 3 dělej podle *Zápisu před sloučením*, bod 6, ve `~/.claude/skills/specify/SKILL.md`, protože po natažení se kolu přiděluje číslo znovu.

### 2. Posunul se `main` od odbočení větve?

```bash
git -C <projekt>/main pull --ff-only                        # jen má-li repozitář remote
git -C <projekt> merge-base --is-ancestor main <vetev>      # 0 = neposunul, 1 = posunul
```

**Neposunul** → krok 4. Obsah `main` po merge bude přesně ten, který už ve větvi prošel průběžnou kontrolou.

**Posunul** → krok 3, **i když merge konflikt nemá**. Textově čistý merge ještě neznamená funkční kód: dvě větve se můžou rozejít obsahově (jedna přejmenuje funkci, druhá ji nově volá) a ten stav by jinak poprvé vznikl až na hlavní větvi.

### 3. Přihraj `main` do větve a ověř tam

Ve worktree větve:

1. `git merge --no-commit main` – bez `--no-commit` by git čistý merge commitnul hned a kontrola by přišla až po něm.
2. **Vyřeš konflikty.** Mechanické jsou ty, kde obě strany jen přidaly – typicky nové záznamy na konci `done.md`, `decisions.md` nebo `todo.md`: ponech oba za sebou. **Ptej se jen na konflikt, kde obě strany rozhodly tutéž věc jinak** – to je rozhodnutí o obsahu, ne postup mergování.
3. **Pusť příkazy z *Kontraktu příkazů* projektu** (`~/Dev/context/coding/quality.md`). Nemá-li projekt kontrakt, řekni nahlas, že spojený stav nic neověřilo. Padne-li kontrola, oprav to v rozpracovaném merge a pusť znovu; do `main` nejde nic, co neprošlo.
4. Commitni (zpráva merge commitu do větve není omezená – hook hlídá jen hlavní větev) a pushni, má-li repozitář remote.
5. **Vrať se na krok 2.** Během řešení se `main` mohl posunout znovu – nad projektem běží souběžné session. **Po třetím kole zastav a ohlas to**: `main` se hýbe rychleji, než se dá dohnat, a o dalším postupu rozhodne uživatel.

Konflikty jsou tytéž, jako by se řešily přímo v `main/`; liší se místo:

- **`main` není ani chvíli napůl mergnutý.** Stojí na něm ostatní session; rozdělané řešení konfliktů v `main/` by viděly a zaseklé by ho tam nechalo.
- **Spojený stav projde kontrolou dřív, než dorazí do `main`.**
- **Řešení konfliktů zůstane dohledatelné** v merge commitu na větvi, ne rozpuštěné v merge commitu do `main`, který nese shrnutí celé práce.

### 4. Merge do `main` a úklid větve

```bash
cd <projekt>/main                    # adresář, který po úklidu zůstane
git merge --no-ff <vetev> -m "<shrnutí toho, co větev přinesla>"
git push                             # jen má-li repozitář remote
git worktree remove <projekt>/<adresar>
git branch -d <vetev>
git push origin --delete <vetev>     # jen pokud byla pushnutá
```

- **Merge v `main/` narazí na konflikt** (`main` se posunul mezi krokem 2 a 4) → `git merge --abort` a zpátky na krok 2. Konflikt se v `main/` neřeší.
- **Push odmítne remote** → zastav před úklidem větve a ohlas to; merge commit zůstává lokálně a větev se nemaže, dokud není `main` venku.
- **`worktree remove` odmítne kvůli neuloženému obsahu** → nepoužívej `--force`, dokud se nezeptáš.

### Zpráva merge commitu shrnuje práci, ne jméno větve

Historie hlavní větve se čte přes `git log --first-parent`, který do větví nevstupuje. Merge commit je tam **jediný řádek za celou odvedenou práci**. Dílčí commity se tím nikam neztrácejí a jsou pořád k dispozici (`git log <merge>^2`, `git show <merge>`), jen nepřeplácají hlavní linku.

Cenou za to je, že výchozí zpráva `Merge větve docs/znamky` je o té větvi jediné, co bude vidět. A neříká nic než jméno adresáře.

**Zprávu proto předej `-m` a napiš ji jako běžný commit:** co větev přinesla, ne jak se jmenovala. Ne `Merge branch 'feat/platby'`, ale `Zaveď platby kartou přes platební bránu`. Nese-li větev víc věcí, patří výčet do druhého odstavce zprávy, ne do prvního řádku.

**Vynucuje to git hook `~/.claude/githooks/commit-msg`**, nasazený globálně přes `core.hooksPath`. Odmítne commit, jehož zpráva je některá z těch, které git generuje sám: `Merge branch`, `Merge branches`, `Merge remote-tracking branch`, `Merge tag`, `Merge commit`, `Merge větve` a `Squashed commit of the following:`.

Platí to **jen na hlavní větvi**, takže aktualizace rozdělané větve z `main` projde beze změny. Projde i merge po `git pull` nad toutéž větví, tedy synchronizace; `git pull origin <cizí větev>` na `main` je naopak dokončení práce a hook ho zastaví.

Hook volá lokální `.git/hooks/commit-msg` repozitáře, existuje-li, protože globální `core.hooksPath` by ho jinak vypnul. **Ostatní typy lokálních hooků tím ale nasazené nejsou.** Potřebuje-li je nějaký projekt, nastaví si vlastní `core.hooksPath`, který globální nastavení přebije.

## Kontrola stavu

```bash
git -C <projekt> worktree list    # co je rozdělané
git -C <projekt> branch -a        # jaké větve existují
```

Worktree, o kterém uživatel neví nebo který zůstal po nedokončené session, ohlas – ale nemaž bez ptaní.

## V kořeni kontejneru git nefunguje

Kořen kontejneru **není pracovní adresář** – `.git` v něm míří na holé `.bare`. Každý příkaz, který potřebuje working tree nebo index, tam dá nesmysl, ne chybu:

| Příkaz v kořeni | Co udělá |
|---|---|
| `git status`, `git diff` | `fatal: this operation must be run in a work tree` |
| `git diff --cached` | **projde a vrátí smyšlený seznam** – porovná HEAD proti indexu bare repa, který k ničemu nepatří |
| `git rev-parse --git-dir` | uspěje, takže jako detekce repa nestačí |

Bare repo svůj `index` nikdy nepoužívá – každý worktree má vlastní v `.bare/worktrees/<adresar>/index`. Vznikl-li kontejner konverzí existujícího repa, zůstane po původním pracovním adresáři ležet `.bare/index` zamrzlý na posledním commitu před konverzí a `git diff --cached` z něj hlásí trvale stejný počet „změn“, které nikdo neudělal. Proto ho `/worktree enable` po konverzi maže.

**Nástroje, které si samy pouštějí git nad adresářem projektu** (statusline, editor, skripty), musí bare repo přeskočit – `rev-parse --git-dir` na to nestačí:

```bash
[ "$(git -C "$dir" rev-parse --is-bare-repository 2>/dev/null)" = "false" ] || exit
```

Lepší je počítat rovnou nad adresářem, ve kterém se pracuje (`cwd`), ne nad kořenem projektu – v kontejneru se pracuje vždy ve worktree.

## Jak si skill najde projektový adresář

Skilly hledají projekt tak, že jdou nahoru od `cwd`, dokud nenajdou `.git`. V kontejneru je `.git` **soubor**, ne adresář – a to v kořeni i v každém worktree, takže samotný nález `.git` nerozliší, kde jsi. Rozhodni podle přítomnosti `.bare`:

| Nález | Kde jsi | Co je projektový adresář |
|---|---|---|
| `.git` adresář | běžný projekt | ten adresář |
| `.git` soubor **a** vedle něj `.bare/` | kořen kontejneru | `<kontejner>/main` |
| `.git` soubor **bez** `.bare/` vedle | worktree větve | ten adresář |

Projektové soubory – `CLAUDE.md`, `README.md`, `docs/` – čti a zapisuj vždy v **projektovém adresáři**, nikdy v kořeni kontejneru. Výjimkou je `.claude/settings.local.json` a rozcestník `CLAUDE.md`, které patří do kořene.

Jmenuje-li se hlavní větev jinak než `main`, zjisti její worktree z `git --git-dir=<kontejner>/.bare worktree list`.
