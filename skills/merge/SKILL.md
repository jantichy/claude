---
name: merge
description: Skill se použije, když uživatel zadá "/merge", nebo chce dokončit hotovou větev a sloučit ji do hlavní – "přimerguj to", "tahle větev je hotová", "ukliď tu větev". Nejdřív pustí /end, aby do hlavní větve šlo i to, co se v session domluvilo – před ním se proto psát nemusí –, pak natáhne hlavní větev do pracovní, nechá vyřešit konflikty a nad spojeným stavem pustí kontrakt příkazů, teprve pak merguje a uklidí větev i její worktree. Funguje ve worktree layoutu i v obyčejném repozitáři s jednou pracovní kopií. Sám od sebe se nespouští – merguje se jen na výslovný pokyn uživatele. U projektu, který se z hlavní větve automaticky nasazuje, je merge samotné nasazení a patří /release.
argument-hint: [větev]
allowed-tools: [Bash, Read, Edit, Grep, Glob, AskUserQuestion, Skill]
---

# Merge

## Co skill dělá

Dokončí hotovou větev: sloučí ji do hlavní a uklidí po ní. Není to jeden příkaz – mezi „větev je hotová“ a „práce je v `main`“ stojí postup, který brání tomu nejdražšímu selhání celého cyklu: ztrátě práce a rozbité hlavní větvi, na které stojí ostatní.

Jádrem je **pořadí**: spojený stav vzniká a ověřuje se **ve větvi**, ne v hlavní větvi. Do ní jde až to, co prošlo kontrolou.

V *Životním cyklu projektu* (`~/.claude/standards/rules.md`) je to kontrolní krok: nic nevyrábí, jen převádí hotovou práci tam, kam patří. Stojí v mezerách mezi kroky osy na místě `/end`, který uzavírá větev – a pouští ho sám jako první krok, takže uživatel při dokončení větve píše jen `/merge` (`~/.claude/skills/handoff.md`, *Řetěz, který nepatří do téhle session*).

Bez argumentu pracuje s větví, na které stojíš; se jménem větve v argumentu s ní. Funguje ve worktree layoutu (`~/.claude/standards/worktree.md`) i v obyčejném repozitáři s jednou pracovní kopií.

## Co skill nedělá

- **Nerozhoduje, že se má mergovat.** Merguje se jen na výslovný pokyn uživatele – `~/.claude/standards/worktree.md`, *Větev žije, dokud uživatel neřekne jinak*. Vyvolání skillu tím pokynem je; nic jiného ne.
- **Nevytěžuje session sám.** To dělá `/end`, kterého na začátku zavolá a jehož práci nepřebírá. Sám zapisuje jedině rozhodnutí o obsahu, které padne při řešení konfliktu (*Fáze 4*) – vzniká až po úklidu session a jinak by se nezapsalo nikam.
- **Nenasazuje.** Stojí-li v `## Nasazení` projektového `CLAUDE.md`, že se z hlavní větve automaticky nasazuje, je merge samotné nasazení a patří `/release`. Skill to pozná a zastaví.
- **Nekontroluje kvalitu práce ve větvi.** Že je práce správná, měří `/review`, `/consistency` a `/attack`. Tenhle skill pouští jen *Kontrakt příkazů* nad spojeným stavem – tedy ověřuje spojení, ne obsah.
- **Nezakládá větve a nepřepíná layout.** Zakládání drží `~/.claude/standards/worktree.md`, zřízení a zrušení kontejneru `/worktree`.

## Zásady pro celý průběh

- **Jak se merguje, rozhoduješ sám a neptáš se.** Pokyn „přimerguj“ míří na výsledek, ne na postup. Ptáš se jen tam, kde to níž výslovně stojí – tedy na konflikt, kde obě strany rozhodly tutéž věc jinak.
- **Průběžně hlas, co se povedlo.** Merge nemá proběhnout mlčky; uživatel musí vidět, ve které fázi jsi a co prošlo.
- **Vrátí-li příkaz jiný návratový kód, než s jakým fáze počítá, zastav a ohlas to.** Nic neobcházej `--force` a větev nemaž.
- **Hlavní větev se tu píše `main`.** Jmenuje-li se v projektu jinak, platí všechno níž pro ni; ve worktree layoutu zjistíš její pracovní adresář z `git --git-dir=<container>/.bare worktree list`.

## Fáze 0 – Příprava

Společný začátek je v `~/.claude/skills/preflight.md`. Navíc:

1. **Načti si `~/.claude/standards/worktree.md`**, stojíš-li v kontejneru s `.bare/`. Rozhoduje o tom, odkud se pouštějí příkazy nad hlavní větví a co se po mergi maže.
2. **Zjisti, kterou větev dokončuješ** – z argumentu, jinak `git branch --show-current`. Jsi-li na hlavní větvi a argument není, řekni to a skonči: není co dokončovat.
3. **Bod 4 přípravy vynech** – průběžnou kontrolu nad rozdělaným stavem nepouštěj. Kontrakt příkazů se tu pouští až nad **spojeným** stavem ve *Fázi 4*, a to je jiné tvrzení.
4. **Bod 3 přípravy se u rozpracovaných změn neptá.** Patří-li k práci větve, commitni je – je to *Fáze 2* a u dokončení větve není z čeho vybírat. Zeptej se jen na soubor, který jsi nezměnil ty.

## Fáze 1 – Úklid session

**Pusť `/end` nástrojem `Skill` a nech ho proběhnout celý, ještě než na větev sáhneš.** Do hlavní větve má jít i to, co se v session domluvilo, a uživatel `/end` před `/merge` nepíše. Stojí první, ne až po natažení `main`: je dlouhý a ptá se, takže uprostřed by roztáhl okno mezi natažením `main` a mergem do něj a skoro jistě vynutil další kolo – kdežto co zapíše na začátku, projde stejným řešením konfliktů jako zbytek práce.

**Přeskoč ho a řekni to jednou větou, když:**

- **slučuješ jinou větev, než na které session stojí** – argument se liší od `git branch --show-current`. Ta větev měla úklid ve vlastní session a tahle s ní nemá nic společného.
- **tahle session už úklid má** – v `docs/done.md`, sekce `## Průchody životním cyklem`, stojí řádek `/end` s jejím session-id (vezmi ho z cesty ke scratchpadu) a od toho běhu se v session nepracovalo, jen padl pokyn k mergi. Pracovalo-li se, pusť ho znovu.

**Pokračuj jen po hotovém verdiktu `/end`.** Skončí-li druhým zněním – zapsané to není celé –, merge zastav a vydej nehotový verdikt s tím, co `/end` brání. Do hlavní větve by jinak šla práce s nedopsanou dokumentací.

## Fáze 2 – Co merge zastaví

Projdi všechny čtyři, než uděláš první `merge`. Kterákoliv z nich znamená zastavit a ohlásit, ne obejít.

- **Necommitnuté změny ve větvi** – commitni je, patří-li k práci větve; soubor, který jsi nezměnil ty, nech být a ohlas ho (`~/.claude/standards/rules.md`, *Commituj jmenované cesty, ne `-A`*).
- **Rozpracovaná hlavní větev** – ve worktree layoutu rozpracovaný `main/`, jinak necommitnuté změny, které by přepnutí vzalo s sebou. Je to cizí práce a merge by se s ní promíchal.
- **`main` je nasazovací větev** – stojí-li to v `## Nasazení` projektového `CLAUDE.md`, zastav a pošli na `/release` (`~/.claude/skills/release/SKILL.md`, *Nasazovací větev není integrační větev*).
- **Větev kola návrhu** – pozná se podle toho, že ji jmenuje blok kola v `docs/todo.md` nebo záznam v `docs/done.md`, sekce `## Kola návrhu`. Neproběhl-li v ní zápis před sloučením (blok v `todo.md` ještě je), pusť v ní nejdřív `/architect`. Proběhl-li, pokračuj – ale *Fázi 4* dělej podle zápisu před sloučením ve `~/.claude/skills/architect/SKILL.md`, protože po natažení se kolu přiděluje číslo znovu.

## Fáze 3 – Posunul se `main` od odbočení větve?

```bash
git pull --ff-only                                   # v pracovní kopii main; jen má-li repozitář remote
git merge-base --is-ancestor main <branch>           # 0 = neposunul, 1 = posunul
```

Ve worktree layoutu pouštěj `pull` z `<container>/main`, jinak si nejdřív ověř, že přepnutí na hlavní větev nevezme rozdělanou práci s sebou (*Fáze 2*).

**Neposunul** → *Fáze 5*. Obsah `main` po mergi bude přesně ten, který už ve větvi prošel průběžnou kontrolou.

**Posunul** → *Fáze 4*, **i když merge konflikt nemá**. Textově čistý merge ještě neznamená funkční kód: dvě větve se můžou rozejít obsahově – jedna přejmenuje funkci, druhá ji nově volá – a ten stav by jinak poprvé vznikl až na hlavní větvi, kde na něm stojí ostatní.

## Fáze 4 – Přihraj `main` do větve a ověř tam

Ve větvi, ne v hlavní větvi:

1. **`git merge --no-commit main`** – bez `--no-commit` by git čistý merge commitnul hned a kontrola by přišla až po něm.
2. **Vyřeš konflikty.** Mechanické jsou ty, kde obě strany jen přidaly – typicky nové záznamy na konci `done.md`, `decisions.md` nebo `todo.md`: ponech oba za sebou. **Ptej se jen na konflikt, kde obě strany rozhodly tutéž věc jinak** – to je rozhodnutí o obsahu, ne postup mergování. **To rozhodnutí zapiš do `docs/decisions.md` ve větvi** i s variantou, která neprošla, ještě než pustíš kontrakt: úklid session proběhl ve *Fázi 1*, takže by se jinak nezapsalo nikam.
3. **Pusť příkazy z *Kontraktu příkazů*** projektu (`~/Context/coding/quality.md`). Nemá-li projekt kontrakt, **řekni nahlas, že spojený stav nic neověřilo** – a pokračuj. Padne-li kontrola, oprav to v rozpracovaném mergi a pusť znovu; do `main` nejde nic, co neprošlo.
4. **Commitni a pushni**, má-li repozitář remote. Zpráva merge commitu do větve omezená není – hook hlídá jen hlavní větev.
5. **Vrať se na *Fázi 3*.** Během řešení se `main` mohl posunout znovu; nad projektem běží souběžné session. **Po třetím kole zastav a ohlas to**: `main` se hýbe rychleji, než se dá dohnat, a o dalším postupu rozhodne uživatel.

**Proč ve větvi, a ne rovnou v `main`:** konflikty jsou tytéž, liší se jen místo, a to místo rozhoduje o třech věcech.

- **`main` není ani chvíli napůl mergnutý.** Stojí na něm ostatní session; rozdělané řešení konfliktů by viděly a zaseklé by ho tam nechalo.
- **Spojený stav projde kontrolou dřív, než dorazí do `main`.**
- **Řešení konfliktů zůstane dohledatelné** v merge commitu na větvi, ne rozpuštěné v merge commitu do `main`, který nese shrnutí celé práce.

## Fáze 5 – Merge do `main` a úklid větve

```bash
git checkout main                     # ve worktree layoutu místo toho: cd <container>/main
git merge --no-ff <branch> -F <file>  # <file> = zpráva zapsaná předem do souboru ve scratchpadu
git push                              # jen má-li repozitář remote
git branch -d <branch>
git push origin --delete <branch>     # jen byla-li pushnutá
```

**Zprávu zapiš nejdřív do souboru ve scratchpadu a předej ji `-F <file>`, nikdy heredocem.** `git merge` zprávu ze standardního vstupu nebere, takže `-F -` i heredoc spadnou; pravidlo o heredocu z `~/.claude/standards/rules.md` (*Commituj jmenované cesty, ne `-A`*) platí jen pro `git commit`. Soubor místo `-m`, protože zpráva má víc odstavců a řádek autorství.

Ve worktree layoutu předchází mazání větve ještě `git worktree remove <container>/<directory>` – a příkazy nad hlavní větví pouštěj z `<container>/main`, ne z worktree větve, protože ten adresář mizí pod nohama session, která v něm stojí.

- **Úklid až po ověřeném mergi, nikdy souběžně s ním.** Mazání pouštěj teprve tehdy, když merge skončil nulou a `git log --oneline -1` ukazuje merge commit. **Nespouštěj je jako paralelní volání nástroje ani za `;`** – selže-li merge, úklid proběhne stejně a smaže nepřimergovanou větev lokálně i na remote. `git branch -d` to nezastaví, pokud je větev pushnutá: za přimergovanou ji považuje podle `origin/<branch>`, ne podle `main`, a skončí jen varováním.
- **Merge narazí na konflikt** (`main` se posunul mezi *Fází 3* a *Fází 5*) → `git merge --abort` a zpátky na *Fázi 3*. V hlavní větvi se konflikt neřeší.
- **Push odmítne remote** → zastav před úklidem větve a ohlas to; merge commit zůstává lokálně a větev se nemaže, dokud není `main` venku.
- **`worktree remove` odmítne kvůli neuloženému obsahu** → nepoužívej `--force`, dokud se nezeptáš.

### Zpráva merge commitu shrnuje práci, ne jméno větve

Historie hlavní větve se čte přes `git log --first-parent`, který do větví nevstupuje. Merge commit je tam **jediný řádek za celou odvedenou práci**. Dílčí commity se tím nikam neztrácejí (`git log <merge>^2`, `git show <merge>`), jen nepřeplácají hlavní linku.

Cenou za to je, že výchozí zpráva `Merge větve docs/znamky` je o té větvi jediné, co bude vidět – a neříká nic než jméno adresáře.

**Zprávu proto napiš jako běžný commit** a předej ji souborem (výš): co větev přinesla, ne jak se jmenovala. Ne `Merge branch 'feat/payments'`, ale `Zaveď platby kartou přes platební bránu`. Nese-li větev víc věcí, patří výčet do druhého odstavce zprávy, ne do prvního řádku.

Vynucuje to git hook `~/.claude/githooks/commit-msg` nasazený globálně přes `core.hooksPath`; odmítne zprávu, kterou si git vygeneroval sám. Platí jen na hlavní větvi, takže aktualizace rozdělané větve z `main` ve *Fázi 4* projde beze změny.

## Časté chyby

- **Merge se provede bez pokynu.** Založit větev, udělat práci a hned ji mergnout je chyba – větev je pracovní prostor, ne obálka na jeden příkaz.
- **Spojený stav se ověří až v `main`.** Textově čistý merge se bere za hotovou věc a kontrola se pustí až nad hlavní větví, kde už selhání vadí všem.
- **Úklid se pustí souběžně s mergem.** Merge spadl a souběžně puštěný úklid smazal worktree i nepřimergovanou větev.
- **Do merge commitu se svezou cizí soubory.** `git add -A` před mergem sebere i to, co v pracovním stromu nechala jiná session.
- **Zpráva merge commitu zůstane výchozí.** Hook ji na hlavní větvi odmítne, ale spolehnout se na to znamená narazit až na konci celého postupu.

## Fáze 6 – Závěr

```
## Větev dokončená

- **Větev:** <jméno> → main
- **Merge commit:** <hash> · <první řádek zprávy>
- **Úklid session:** <verdikt `/end` / přeskočen a proč>
- **Natažení main do větve:** <proběhlo a s čím / nebylo potřeba, main se neposunul>

**Ověřeno**
- Kontrakt příkazů nad spojeným stavem: <příkaz a návratový kód, nebo „projekt kontrakt nemá – spojený stav nic neověřilo">

**Úklid**
- <co se smazalo: worktree, lokální větev, větev na remote – nebo co zůstalo a proč>
```

Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo – `~/.claude/standards/rules.md`, *Styl odpovědí*.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Větev je přimergovaná a ověřená, můžeš pokračovat v main.`
- `Větev přimergovaná není – brání tomu: <konkrétní seznam>.`

**Kudy dál** je poslední blok odpovědi, za verdiktem – tvar a pravidla, kdy odrážka musí vypsat celý řetěz včetně ukončení session, drží `~/.claude/skills/handoff.md`. Odtud vede:

- `/clear`, a `/next` v `<container>/main`, respektive v hlavní větvi – fronta práce nad sloučeným stavem; úklid session proběhl na začátku mergi
- zbývá-li k témuž záměru další větev, pojmenuj ji
