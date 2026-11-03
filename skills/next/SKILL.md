---
name: next
description: Skill se použije, když uživatel zadá "/next", nebo se na začátku session v projektu ptá, s čím pokračovat a do čeho se může pustit, anebo chce navázat na práci přerušenou při ukončení session – "pokračuj, kde jsme skončili", "naváž na přerušenou práci". Nejdřív hledá zápis přerušené práce, který nechal /end; najde-li ho, rovnou podle něj pokračuje a nic dalšího nesbírá. Jinak sestaví frontu z todo.md, implementačního plánu, kol návrhu, rozdělané práce v gitu a místa v životním cyklu, zvlášť vypíše, na čem se právě pracuje v jiné session, nabídne pokračování v opuštěných větvích, u každé položky řekne, v čem spočívá a jak je velká, nejaktuálnější nabídne k výběru a do vybrané se pustí. Na rozdíl od /end, který dohledává, co se v session domluvilo, a zapisuje to, tenhle skill nic nezapisuje ani nepřeřazuje – jen čte, co už zapsané je. Nápady z backlogu vypíše až tehdy, když je fronta prázdná.
argument-hint: [zúžení]
allowed-tools: [Read, Glob, Grep, Bash, AskUserQuestion, Skill]
---

# Next

## Co skill dělá

Na začátku session v rozdělaném projektu odpoví na otázku **„s čím můžeme pokračovat?“** – rychle. Posbírá práci, která je rozhodnutá a nehotová, oddělí od ní to, na čem se právě pracuje v jiné session, zbytek seřadí podle toho, co je na stole nejvíc, vypíše ho kompaktně a několik nejaktuálnějších položek nabídne přes `AskUserQuestion`. Po výběru se do úkolu rovnou pustí, nebo – je-li to opuštěná session – řekne, jak ji obnovit.

**Zbyla-li po předchozí session přerušená práce, nabídka se nestaví.** `/end` ji při ukončení session zapsal do sekce `## Přerušený běh` i s tím, čím se pokračuje, takže skill ji najde jedním příkazem, přepne se tam, kde leží, a okamžitě v ní pokračuje – sběr celé fronty by jen zdržel. Teprve když přerušené nic není, staví nabídku.

Režimy nemá. Argument je **volné zúžení** – `/next review`, `/next DPH`, `/next Kola návrhu` – a omezí celý výpis včetně práce ve větvích na položky, v jejichž názvu, textu nebo nadpisu sekce se výraz vyskytuje, bez ohledu na velikost písmen; položka *sešít návrh po kolech* patří k zúžení `Kola návrhu` vždy. Bez argumentu jde o celou frontu. **Zúžení přerušenou práci nepřeskakuje do vedení**: kdo zužuje, chce vidět frontu, takže se nabídka staví vždycky a přerušený blok v ní stojí jako položka, odpovídá-li zúžení. **Na zúžení `Kola návrhu` spoléhá `/architect` bez jména kola** – nabídku kol si přenechává sem, takže sekce *Kola návrhu* níž je rozhraní mezi oběma skilly, ne vnitřek, který se smí tiše změnit.

## Co skill nedělá

- **Nic nezapisuje ani nepřeřazuje.** Zjistí-li, že je `todo.md` zastaralé (hotová položka, která se nepřesunula), řekne to jako poznámku; úklid souborů po session drží `/end`. Jediné, co mění, jsou vzdálené reference po `git fetch`.
- **Nerozkládá práci na úkoly.** Položka, která je na jednu session moc velká, se nabídne celá; rozpad do plánu dělá `/breakdown`.
- **Nerozhoduje o nápadech z backlogu.** Vypíše je, když fronta dojde, a přesun do `todo.md` nechá na uživateli.
- **Nevybírá za uživatele.** Doporučí, ale začne až po výběru.
- **Neodjede kolo návrhu ani ho nesešije.** Vybrané kolo i sešití předá `/architect`; tenhle skill jen drží, jak se kola nabízejí.
- **Nesahá do práce jiné session.** Co právě běží jinde, jen ohlásí – nepřepíná se do toho, nemerguje to a nenabízí to.
- **Nemaže zápis přerušení.** Kdy se sekce `## Přerušený běh` smaže, říká *Jak pokračovat* v zápisu; dělá to až práce, která frontu dojde. Chybí-li zápis nebo je neúplný, nedomýšlí ho z hlavy.
- **Nehlídá, jestli nad přerušenou prací běží jiná session.** Přerušení končí řetězem `/end` → `/clear` v téže session, takže by kontrola hlásila jako obsazenou právě tu, která má pokračovat – a byla by nejpomalejší částí cesty, která má být rychlá. Druhé okno nad týmž worktree je věc uživatele.
- **Neobnoví session sám.** `/resume` je příkaz, který píše uživatel; skill mu dá přesné znění a skončí.

## Jak je to postavené uvnitř

**Přerušenou práci hledá jeden příkaz shellu** ve *Fázi 1* – projde `todo.md` a `CLAUDE.md` všech worktree a vypíše sekci `## Přerušený běh`. Najde-li ji, víc se nepouští nic. Nenajde-li, pustí v témže volání `collect.py`, takže ani nabídka nečeká na kolo navíc.

**Všechno ostatní, co jde zjistit mechanicky, posbírá jedním během skript `collect.py`** v adresáři skillu a vrátí to jako JSON: kořen a uspořádání projektu, hlavní větev po `git fetch`, položky `todo.md` rozdělené podle sekcí, bloky kol se stavem z jejich větví, stav plánu, návrhové dokumenty, poslední průchody cyklem, rámeček cyklu z `~/.claude/standards/rules.md`, necommitnuté změny a nesloučené větve i s tím, jestli nad nimi běží session. **Živé a opuštěné session zjišťuje `sessions.py`**, který `collect.py` volá – čte registr běžících session Claude Code (`~/.claude/sessions/`), ověří, že proces žije, a větev bere z posledního záznamu transcriptu, protože session ve worktree layoutu startuje v kořeni kontejneru.

**Nástroj `ListAgents` je nenahradí** – nevrací větev ani adresář projektu, a právě na větvi stojí rozhodnutí *nabídnout, nebo skrýt*.

**Skripty jsou implementační detail.** Závazné je jen to, co z nich plyne pro nabídku: úkol ve větvi, nad kterou běží živá session, se nenabízí; **session, která běží – i obnovená v jiném okně –, se k obnovení nenabízí nikdy**; opuštěná větev se nabídne jako první; a **nedá-li se to zjistit, bere se větev jako obsazená** a řekne se to nahlas.

------

## Fáze 0 – Příprava

`~/.claude/skills/preflight.md` se **nenačítá**, ani `structure.md` a `lifecycle.md`. Co z nich skill potřebuje – kořen projektu a worktree layout, hlavní větev, stav pracovního stromu, režim umístění souborů, tvar bloku kola a pořadí kroků cyklu – zjistí nebo vyčte `collect.py`. Stav pracovního stromu neblokuje: rozpracované změny jsou položka fronty. **Rychlost je tu celé zadání:** každé čtení navíc je čekání, a u navázání na přerušenou práci by to bylo čekání na nic.

## Fáze 1 – Přerušený běh

**Bez argumentu** pusť z adresáře session **přesně tenhle příkaz**, nic předtím a nic dalšího:

```bash
out=$({ git worktree list --porcelain 2>/dev/null | sed -n 's/^worktree //p' | grep . || pwd; } | while read -r d; do find "$d" -maxdepth 3 \( -path "$d/.*" -o -name node_modules -o -name vendor \) -prune -o \( -name todo.md -o -name CLAUDE.md \) -type f -print; done | while read -r f; do awk -v f="$f" '/^## Přerušený běh/{print "==> " f; s=1; next} s && /^## /{exit} s' "$f"; done); if [ -n "$out" ]; then printf '%s\n' "$out"; else python3 ~/.claude/skills/next/collect.py; fi
```

Projde všechny worktree repozitáře – ve worktree layoutu tedy i větve vedle té, kde session stojí, a funguje i z kořene kontejneru – a v každém i podsložky do třetí úrovně, aby našel zápis v podprojektu klientské složky (`zakazka/docs/todo.md`, `~/.claude/skills/project/client.md`, *Podprojekt*), i když má podprojekt vlastní repozitář ignorovaný gitem; `/end` zapisuje do `todo.md` projektu, ve kterém session stojí. Skryté složky, `node_modules` a `vendor` přeskakuje, aby hledání zůstalo pod vteřinou. **Čte i `CLAUDE.md`**, protože operativní projekt `todo.md` nemá a `/end` v něm zapisuje do projektového `CLAUDE.md` (`~/.claude/standards/structure.md`, *Operativní projekt: režim `CLAUDE.md`*); mimo git hledá od adresáře session.

| Výstup | Co dál |
|---|---|
| řádky `==> <cesta>` se sekcí | přerušená práce – *Navázání* níž; `collect.py` neběžel a nepouští se |
| jeden řádek JSON | přerušené nic není a je to rovnou výstup `collect.py` – pokračuj *Fází 2* bez dalšího volání |

**S argumentem** příkaz nepouštěj a jdi rovnou na *Fázi 2*. Zúžení znamená, že uživatel chce frontu – a `/architect` volá `/next Kola návrhu`, takže by jinak místo nabídky kol skončil v cizí přerušené práci.

### Navázání

**Víc bloků `### `**, v jedné sekci i napříč worktree → zeptej se přes `AskUserQuestion`, kterým začít: nadpis bloku jako `label`, první věta *Jak pokračovat* jako `description`, v pořadí výpisu. Žádný neoznačuj za doporučený, pořadí nerozhodl nikdo. **Blok se stejným nadpisem z víc worktree je jeden zápis**, který zdědil pomocný worktree odbočený z větve (`~/.claude/skills/findings.md`, *Zapracování*); nabídni ho jednou, s worktree, které blok sám jmenuje jako pracovní adresář, a nejmenuje-li žádné, s prvním ve výpisu. **Chybí-li `**Jak pokračovat:**` úplně**, nehádej – vypiš, co v bloku je, a zeptej se, čím začít.

U jednoho bloku, nebo toho vybraného:

1. **Přepni se do projektu, kde zápis leží** – adresář nad `docs/todo.md` z řádku `==>` (nad `todo.md` u projektu bez `docs/`, nad `CLAUDE.md` u operativního projektu); u podprojektu je to jeho podsložka, ne kořen worktree. Stojí-li session jinde, přejdi tam a řekni to jednou větou; ve worktree layoutu je to jediná věc, kterou nová session jinak nemá odkud vědět.
2. **Přečti blok celý** – výstup příkazu ho už obsahuje, soubor se zápisem znovu neotevírej. Mimo *Jak pokračovat* nese úvodní větu s tím, **co musí předcházet**: stojí-li tam krok, který se ještě neudělal (uživatel chystal změnu rozhodnutí), zeptej se, jestli proběhl, dřív než začneš – fronta nad neplatným stavem je práce nazmar.
3. **Shrň ve třech až pěti řádcích:** co se přerušilo a kdy, kde to leží, kolik položek zbývá, co předchází a čím se teď pokračuje.
4. **Řekni první závěrečnou větu z *Fáze 5* a proveď první akci z *Jak pokračovat*:**
   - **Je to skill** (`/review branch`, `/implement`) → vyvolej ho přes nástroj `Skill` s argumentem ze zápisu. Blok mu neopakuj jako zadání – zbývající položky si přečte z `todo.md` sám, a říká-li zápis, že se s nimi má porovnat výsledek, stojí to v *Jak pokračovat*, ne v tvém shrnutí.
   - **Je to položka nebo krok práce** → načti soubory, na které ta položka odkazuje, a pusť se do ní. Další položky ber v pořadí zápisu; každá nese varianty a doporučení, takže je předkládej tak, jak jsou zapsané, ne od nuly.
   - **Je to zapracování sekce `## Rozhodnuto k zapracování`** → zapracuj ji podle `~/.claude/skills/findings.md`, *Zapracování* – odpovědi tam už padly, takže se na ně neptej znovu.

Od té chvíle běží běžná práce podle pravidel projektu, ne tenhle skill. **Řekne-li uživatel, že chce místo navázání vidět frontu**, pusť `python3 ~/.claude/skills/next/collect.py` a pokračuj *Fází 2*; přerušený blok v ní stojí jako položka.

## Fáze 2 – Sběr

Výstup `collect.py` máš z *Fáze 1*; se zúžením ho pusť z adresáře session jako `python3 ~/.claude/skills/next/collect.py --all` – `--all` vrátí celou frontu, protože zúžení filtruje i to, co by se do vrcholu nevešlo. Bez `head` a bez dalšího zpracování v shellu, výstup je jeden řádek JSON a skript si jeho velikost hlídá sám. Nic dalšího nečti – **každé další volání stojí vteřiny čekání**, a výstup skriptu na nabídku stačí. Soubor otevři jen tehdy, když bez něj položku opravdu nejde popsat.

- **Skript skončil chybou** (není to git repozitář ani operativní projekt, nejde určit hlavní větev) → řekni to a skonči závěrečným verdiktem.
- **`docs` je `CLAUDE.md`** → operativní projekt (`~/.claude/standards/structure.md`, *Operativní projekt: režim `CLAUDE.md`*): fronta jsou jen sekce `## Přerušený běh` a `## Otevřené body` jeho `CLAUDE.md`. Otevřené body zapsané u témat skript nesbírá – řekni to v poznámkách. Místo v cyklu neodvozuj, operativní projekt do cyklu nevstupuje; `layout` `none` znamená, že nemá git, takže práce ve větvích odpadá.
- **`docs` je null a nic dalšího nenašel** → projekt frontu nevede; řekni to a skonči.
- **`fetch` je `failed`** → pokračuj, ale v poznámkách řekni, že hlavní větev může být stará.

**Srovnaný `todo.md` čti mechanicky.** V pásmech práce (`Teď`, `Potom`, `Později` pod `# Fronta`) je pořadí priorita a velikost nese každá položka v poli `size` (`~/.claude/standards/structure.md`, *`todo.md`*), takže skript vrátil jen vrchol fronty – nejvýš deset připravených položek v pořadí souboru – a u sekce, ze které se něco nevešlo, počet v `more`. Pořadí ani velikost neposuzuj znovu; právě to je úsudek, který se přesunul k zápisu položky.

**`legacy` není `null`** → `todo.md` srovnaný není: skript vrátil celou frontu jako dřív a v `legacy` důvody. Seřaď ji podle *Fáze 3* a velikosti odhadni podle `structure.md`, *`todo.md`* a do poznámek napiš jednu větu: fronta není srovnaná (důvody z `legacy`), takže pořadí i velikosti jsou odhad, a srovnat ji jde dorovnáním projektu přes `/project`. Nic víc – nesrovnaný soubor je okolnost, ne práce, kterou by se mělo začít.

Co z výstupu je položka fronty:

| Klíč | Položka |
|---|---|
| `current.uncommitted` | necommitnuté změny tam, kde session stojí – rozdělaná práce tady |
| `todo` | položka ze sekcí – u srovnaného souboru jen vrchol a `more`, jinak všechny; hotové skript vynechal |
| `rounds` | kolo návrhu – viz *Kola návrhu* |
| `stitch_pending` | položka *sešít návrh po kolech*, spouštěč `/architect` |
| `plan.open` | jedna položka „dokončit plán“ s počtem zbývajících, spouštěč `/implement` |
| `artifacts`, `passes`, `lifecycle` | chybějící krok cyklu – viz *Místo v cyklu*; `lifecycle` je `{"osa": [...], "kontroly": [...]}` |
| `branches` | práce ve větvi – viz *Práce ve větvích* |
| `backlog` | skript ho vrací jen při prázdné frontě – viz *Fáze 3* |

**Popis položky může být zkrácený a dolovat ho zpátky se nesmí.** Výstup nad ~30 kB harness do kontextu nevloží – uloží ho do souboru a dá jen náhled –, takže skript si sám hlídá rozpočet a popisy položek dokrátí. Na kolik, říká `text_limit`: `null` znamená celé popisy, číslo zkrácení na tolik znaků, `0` popisy zahozené a zbylý název. **Jednořádkový výpis *Fáze 4* vystačí se jménem a velikostí vždycky**; teprve u tří čtyř položek, které jdou do nabídky, otevři `todo.md` na jejím místě – a jen tehdy, když se z názvu `description` napsat nedá. Číst kvůli tomu celou frontu znovu je přesně ta ztráta, kvůli které skript vznikl.

### Položka odložená k datu

Položka, která nese hned za názvem `od <datum>`, má smysl až od toho dne – typicky *vyhodnotit provoz přes `/evaluate`*, kterou tam zapsal `/release`. Skript to rozhodl za tebe, pole `not_before` a `waiting`:

| `waiting` | S položkou |
|---|---|
| `true` | **do fronty nevstupuje** – jen ji zmiň v poznámkách i s datem, aby bylo vidět, že se na ni nezapomnělo |
| `false` | den nastal, řadí se jako každá jiná |

**Datum nepočítej sám a nepřepisuj ho.** Dnešní den zná skript a porovnal ho; položka, u které si termín přepočítáš z hlavy, se nabídne ve špatný den (`~/.claude/standards/rules.md`, *Hodnotu, kterou čte stroj, nepiš*).

**Závislosti ber jen ze zápisu**, ne z odhadu: řádek *Čeká na*, pole `waits` u položky (skript ho vytáhne i z konce dlouhého popisu, který `text` ořízne), pořadí v plánu, výslovná zmínka v položce. Tuší-li se závislost, která zapsaná není, řekni ji u položky jako domněnku.

### Práce ve větvích

**Úkol, na kterém se právě pracuje v jiné session, se nenabízí** – druhá session by ho rozjela podruhé a větve by se srazily. **Úkol v opuštěné větvi se naopak nabídne jako první** – je to zapomenutá práce, ke které se patří vrátit dřív, než se začne nová.

Obsazenost už rozhodl skript, pole `state`:

| `state` | S větví |
|---|---|
| `occupied` | do *Pracuje se jinde* i se jménem session (`session`); nenabízí se |
| `uncertain` | do *Pracuje se jinde* s důvodem z `why`; nenabízí se. Je-li důvodem čerstvě otevřené okno, řekni to – uživatel ho může zavřít nebo v něm začít a pustit `/next` znovu |
| `abandoned` | větev s prací (`ahead` commitů nebo `uncommitted` neuložených souborů) a bez živé session; do nabídky se závorkou *opuštěná větev*, spouštěč je obnovení session z `resume`, a není-li, pokračování ve větvi |
| `empty` | větev nebo worktree bez práce – typicky zůstatek po sloučení; nenabízí se, stačí zmínka v poznámkách |

**Na položku z fronty větev přiřaď** podle pole `rounds` (kola s řádkem *Větev*), podle `changes` (které položky větev v `todo.md` a `plan.md` mění nebo odškrtává; `adds_stitch` znamená sešití návrhu) a nakonec podle jména větve a `commits` – shoda jen podle jména je **domněnka** a řekni to. Položka přiřazená obsazené nebo nejisté větvi se **z fronty vyřadí**; větev bez přiřazené položky se vypíše sama, s tím, co v ní podle commitů je.

**Větev s `current: true`** je ta, ve které session stojí: je-li `abandoned`, je to rozdělaná práce tady; je-li `occupied`, pracuje nad ní ještě jiné okno a platí totéž co pro jiné obsazené větve – **i když je to hlavní větev** (`main: true`). **Hlavní větev skript vypíše jedině tehdy, když v ní opravdu něco leží** – commit nad hlavní referencí, nebo neuložená změna v jejím worktree. **Živá session to nestačí:** session, která ve worktree layoutu startuje v kořeni kontejneru a vlastní větev si ještě nezaložila, hlásí jako svou hlavní větev – a stačilo by druhé otevřené okno nad projektem, aby práce mířící do hlavní větve zmizela z nabídky.

### Kola návrhu

- **Kolo s `branch_state`, jehož větev je v `branches` jako `occupied`, `uncertain` nebo `abandoned`,** je práce ve větvi – řídí se *Prací ve větvích*, **nikdy se nenabízí jako nové kolo**. Chybí-li jeho větev v `branches` nebo je `empty`, nic v ní není a kolo se nabízí jako každé jiné. `branch_state` říká, co ve větvi čeká: hodnota řádku *Stav* z `todo.md` ve větvi (`rozhoduje se` = rozhodování, `rozhodnuto` = zápis před sloučením), nebo `merge_pending` (zbývá sloučit, provede `/merge`), když blok kola ve větvi už chybí a zbývá jen sloučení.
- **Kolo bez větve** se nabízí se spouštěčem `/architect <kolo>`; u něj řekni, do kterých dokumentů sahá (*Sahá na*) a jestli se to kříží s rozběhnutým kolem. **Souběh neblokuj, jen na něj upozorni.**
- **Bez worktree layoutu** větve kol nevznikají; kolo ve stavu `rozhoduje se` nebo `rozhodnuto` ber jako rozdělanou práci tady.

### Místo v cyklu

Chybějící krok odvoď z `artifacts` a `passes` proti `lifecycle`, a **jen pro osu** – `lifecycle["osa"]` je řada, ve které každý krok čeká na výstup toho předchozího, takže díra v ní je nález. Rozhodují přitom dokumenty, ne průchody: kroky osy do `## Průchodů životním cyklem` nepíšou, takže „chybí `/architect`“ poznáš z toho, že je `requirements.md` a není `architecture.md`, a „chybí `/breakdown`“ z návrhu bez plánu.

**Z `lifecycle["kontroly"]` chybějící krok neodvozuj.** Kontrolní kroky nejsou řada, stojí v mezerách a některé ve víc naráz, takže „ještě nepřišel na řadu“ u nich nic neznamená. Jediné, co se o nich dá z `passes` říct, je, že po odpracovaném plánu není zapsaný průchod `/review` – a to hlas jako domněnku.

**`/evaluate` a `/release` se z artefaktů neodvozují nikdy.** Chybějící `operation.md` neznamená, že se má vyhodnotit provoz – znamená obvykle, že se ještě nenasazovalo, a z repozitáře se to nepozná. Oba kroky mají vlastní spouštěč: `/release` výslovný pokyn uživatele a `/evaluate` **datovanou položku v `todo.md`**, kterou tam `/release` zapsal (viz *Položka odložená k datu* výš). Nabízí se tedy jako ta položka, ne jako díra v ose.

**Nejsi-li si jistý, že krok opravdu chybí, řekni to u položky jako domněnku** – vědomě přeskočený krok se ze souborů pozná jen tehdy, když ho někdo zapsal.

## Fáze 3 – Řazení

Obsazené a nejisté větve ani položky s `waiting: true` do řazení nevstupují. Zbytek seřaď:

0. **Položky ze sekce `## Přerušený běh`** – zbytek práce, kterou předchozí session nedokončila, protože jí nabyl kontext nebo ji uživatel přerušil (zapisuje ji `/end`, podnět drží `~/.claude/skills/handoff.md`, *Přerušení dlouhého průchodu*). Jdou **první, před opuštěnými větvemi**, a v pořadí, ve kterém je ta session zapsala. Je to práce rozdělaná do půlky, u které navíc nikdo nedrží kontext – čím dýl leží, tím spíš se přestane rozumět tomu, proč nález nálezem je. **Položkou je celý blok `### `**, ne jednotlivé nálezy v něm: název je nadpis bloku, `text` první věta *Jak pokračovat* a spouštěč je *Navázání* z *Fáze 1*, které na blok naváže i se vším, co v něm leží. Do fronty se dostane jen se zúžením, nebo když uživatel navázání odmítl. **Položka s `branch` leží v `todo.md` worktree té větve**, ne v hlavní větvi – `/end` zapisuje tam, kde session stála; přiřaď ji větvi podle *Práce ve větvích*, takže u obsazené větve se nenabízí a opuštěná větev se nabídne jako tenhle blok, ne podruhé. **Položka s `project` leží v podprojektu** – `/end` zapisuje do `todo.md` projektu, kde session stála, takže z kořene klientské složky by se na ni jinak nedošlo. `collect.py` ji hledá stejně hluboko jako příkaz *Fáze 1* a u položky řekni, ve kterém podprojektu leží; zbytek fronty podprojektu skript nebere, patří k jinému projektu.
1. **Opuštěné větve** – od nejčerstvější (`last_ts`). Větev bez session k obnovení, na kterou nikdo nesáhl déle než měsíc, nedávej na první místo – je to spíš zapomenutý pokus než rozdělaná práce; nabídni ji mezi ostatními a řekni její stáří.
2. **Rozdělaná práce tady** – necommitnuté změny, rozpracovaný plán, `## Parkované v session` a `## Rozhodnuto k zapracování`; obě sekce skript vrací celé.
3. **Kola návrhu** v pořadí podle *Čeká na* a chybějící krok cyklu.
4. **Položky pásem v pořadí `todo.md`** – pořadí je priorita a nepřeřazuje se.
5. **Jen u nesrovnaného `todo.md`** (`legacy`) pořadí souboru nestačí: položky bez nesplněné závislosti dej před ty, které na něco čekají, mezi nimi ty, na které čeká nejvíc dalších, a pak pořadí v souboru.

Položky, které čekají na nesplněnou závislost (`waits`), nevynechávej – patří do *Čeká na něco*.

**Je-li fronta prázdná a volání není zúžené**, vypiš `backlog` odděleně jako nezávazné nápady s upozorněním, že výběr znamená nejdřív rozhodnout o přesunu do `todo.md`. Do nabídky je nedávej.

## Fáze 4 – Nabídka

**Výpis je kompaktní: jeden řádek na položku.** Podrobnosti – co se bude dělat a čím se začne – nese až `description` u nabízených položek v `AskUserQuestion`. Generování textu je nejpomalejší část běhu a totéž dvakrát je čekání navíc.

```
<zastaralá položka, kříž kol, domnělá závislost, položka odložená k datu i s tím datem, selhaný fetch – nebo že nic rozdělaného ani běžícího jinde není>

**Pracuje se jinde:** <název> (`<branch>`, <session / nejisté: proč>) · …

**Čeká na něco:** <název> (na <co>) · …

**S čím můžeme pokračovat**

1. <kolečko> <název> <(jen je-li co: čeká na …, opuštěná větev `<branch>`, rozdělané tady)>
2. …

<jen je-li co: + N dalších v `todo.md` – celou frontu vypíšu na požádání>

○ drobnost · ◐ střední · ● velký
```

Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo – `~/.claude/standards/rules.md`, *Styl odpovědí*. Prázdnou část vynech.

**Pořadí je schválně od kontextu k výběru:** poznámky, práce jinde a čekající položky jsou okolnosti, které je dobré znát dřív, než se čte nabídka – a nabídka stojí poslední, těsně nad otázkou, ze které se vybírá. **Poznámky jsou holý odstavec bez popisku** a stojí úplně nahoře; **práce jinde a čekající položky jsou každá jeden odstavec** s tučným popiskem, položky za sebou oddělené `·`, ne seznam – jsou to informace, ze kterých se nevybírá.

**Tučný je jen nadpis a popisky částí, položky ne.** Položka je kolečko velikosti a název, nic víc – **stav „připravené“ ani velikost slovem se nepíšou**. Do závorky za název patří jen to, co mění rozhodnutí: nesplněná závislost, opuštěná větev, rozdělaná práce tady. Připravená položka bez závislosti závorku nemá. Výpis se čte očima, ne jako tabulka, a slova navíc na každém řádku ho zahlcují.

**Velikost** je kolečko hned za číslem – obyčejný textový znak, ne barevné emoji: přebírá barvu textu terminálu, takže nesvítí, a napůl plné kolečko se čte jako napůl velký úkol. U položky `todo.md` ho ber z pole `size`; odhaduješ ho jen tam, kde chybí – u nesrovnaného souboru, sekce mimo pásma práce, kola, kroku cyklu nebo větve –, podle `~/.claude/standards/structure.md`, *`todo.md`*.

**Počet zbylých** je součet `more` přes sekce. **Řekne-li uživatel, že chce celou frontu**, pusť `python3 ~/.claude/skills/next/collect.py --all` a vypiš ji stejným tvarem.

**Spouštěč** je skill, když ho položka jmenuje nebo když jde o krok cyklu, kolo či plán; u opuštěné větve obnovení session nebo pokračování ve větvi; jinak první konkrétní krok. Skill si nevymýšlej k položce, se kterou nemá nic společného.

Pak přes `AskUserQuestion` nabídni **tři až čtyři** položky v pořadí z *Fáze 3*; první označ jako doporučenou. `description` začíná **kolečkem velikosti** a nese, **co se bude dělat a čím se začne** – jednou, dvěma větami. Volbu *Other* doplňuje nástroj sám – vybere-li ji uživatel, jde o jiný směr, ne o odmítnutí. **Nabízet není co** – všechno běží jinde nebo na něco čeká –, výběr nepokládej a skonči druhou závěrečnou větou.

## Fáze 5 – Předání

**Před předáním opuštěné větve – se session i bez ní – pusť `python3 ~/.claude/skills/next/sessions.py --project <root>`** (`root` z výstupu `collect.py`) a ověř obojí: že vybraná session není mezi živými **a** že nad větví nezačala pracovat jiná session nad projektem. Mezi výpisem a výběrem uběhla chvíle. Je-li obsazená, řekni to a nabídni zbytek fronty znovu.

**Opuštěná větev se session k obnovení.** Obnovit session neumíš – `/resume` píše uživatel. Dej mu oba tvary a skonči:

- v téhle session: `/resume <session_id>`,
- v novém okně terminálu: `cd <start_cwd> && claude --resume <session_id>` – `start_cwd` z `resume`: session se obnovuje z adresáře, kde startovala, a ve worktree layoutu to je kořen kontejneru.

**Opuštěná větev bez session.** Ve worktree layoutu přejdi do jejího pracovního adresáře podle `~/.claude/standards/worktree.md`; bez worktree layoutu se na větev přepni jen s čistým pracovním stromem, jinak se nejdřív zeptej, co s rozdělanými změnami.

**Je-li spouštěčem skill, vyvolej ho** přes nástroj `Skill` s argumentem, který položku určuje. Nic z toho, co jsi posbíral, mu neopakuj jako zadání.

**Jinak** načti podklady, na které položka odkazuje, shrň ve třech až pěti řádcích výchozí stav a pusť se do práce. Od té chvíle běží běžná práce podle pravidel projektu, ne tenhle skill.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím. U přerušené práce a vybrané položky ji řekni **před** vyvoláním skillu nebo začátkem práce – potom už běh tohohle skillu nekončí, ale přechází:

- `Navazuju na: <nadpis bloku>, pokračuju <skillem / položkou „…“> v <pracovní adresář>.`
- `Vybráno: <položka>, pokračuju <skillem / prací na ní / obnovením session – napiš /resume <session_id>>.`
- `Vybrat není z čeho – brání tomu: <konkrétní seznam>.`

Prázdná fronta i fronta, kde všechno běží jinde nebo na něco čeká, patří do druhé věty i s tím, co se prošlo: *„v `todo.md` ani v plánu nic nečeká, v gitu není nic rozdělaného, backlog je prázdný“*, nebo *„kolo o DPH běží ve větvi `architect-vat`, kolo o fakturaci čeká na něj“*.
