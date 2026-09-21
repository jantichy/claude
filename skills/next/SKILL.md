---
name: next
description: Skill se použije, když uživatel zadá "/next", nebo se na začátku session v projektu ptá, s čím pokračovat, co ho čeká a do čeho se může pustit – chce vidět seznam dalších úkolů seřazený podle důležitosti a závislostí a z nabídky si vybrat. Sestaví frontu z todo.md, implementačního plánu, kol návrhu, rozdělané práce v gitu a místa v životním cyklu, zvlášť vypíše, na čem se právě pracuje v jiné session, nabídne pokračování v opuštěných větvích, u každé položky řekne, v čem spočívá a jak je velká, nejaktuálnější nabídne k výběru a do vybrané se rovnou pustí. Na rozdíl od /cleanup, který dohledává, co se v session domluvilo, a zapisuje to, tenhle skill nic nezapisuje ani nepřeřazuje – jen čte, co už zapsané je. Nápady z backlogu vypíše až tehdy, když je fronta prázdná.
argument-hint: [zúžení]
allowed-tools: [Read, Glob, Grep, Bash, AskUserQuestion, Skill]
---

# Next

## Co skill dělá

Na začátku session v rozdělaném projektu odpoví na otázku **„s čím můžeme pokračovat?“** – rychle. Posbírá práci, která je rozhodnutá a nehotová, oddělí od ní to, na čem se právě pracuje v jiné session, zbytek seřadí podle toho, co je na stole nejvíc, vypíše ho kompaktně a několik nejaktuálnějších položek nabídne přes `AskUserQuestion`. Po výběru se do úkolu rovnou pustí, nebo – je-li to opuštěná session – řekne, jak ji obnovit.

Režimy nemá. Argument je **volné zúžení** – `/next review`, `/next DPH`, `/next Kola návrhu` – a omezí celý výpis včetně práce ve větvích na položky, v jejichž názvu, textu nebo nadpisu sekce se výraz vyskytuje, bez ohledu na velikost písmen; položka *sešít návrh po kolech* patří k zúžení `Kola návrhu` vždy. Bez argumentu jde o celou frontu. **Na zúžení `Kola návrhu` spoléhá `/architect` bez jména kola** – nabídku kol si přenechává sem, takže sekce *Kola návrhu* níž je rozhraní mezi oběma skilly, ne vnitřek, který se smí tiše změnit.

## Co skill nedělá

- **Nic nezapisuje ani nepřeřazuje.** Zjistí-li, že je `todo.md` zastaralé (hotová položka, která se nepřesunula), řekne to jako poznámku; úklid souborů po session drží `/cleanup`. Jediné, co mění, jsou vzdálené reference po `git fetch`.
- **Nerozkládá práci na úkoly.** Položka, která je na jednu session moc velká, se nabídne celá; rozpad do plánu dělá `/breakdown`.
- **Nerozhoduje o nápadech z backlogu.** Vypíše je, když fronta dojde, a přesun do `todo.md` nechá na uživateli.
- **Nevybírá za uživatele.** Doporučí, ale začne až po výběru.
- **Neodjede kolo návrhu ani ho nesešije.** Vybrané kolo i sešití předá `/architect`; tenhle skill jen drží, jak se kola nabízejí.
- **Nesahá do práce jiné session.** Co právě běží jinde, jen ohlásí – nepřepíná se do toho, nemerguje to a nenabízí to.
- **Neobnoví session sám.** `/resume` je příkaz, který píše uživatel; skill mu dá přesné znění a skončí.

## Jak je to postavené uvnitř

**Všechno, co jde zjistit mechanicky, posbírá jedním během skript `collect.py`** v adresáři skillu a vrátí to jako JSON: kořen a uspořádání projektu, hlavní větev po `git fetch`, položky `todo.md` rozdělené podle sekcí, bloky kol se stavem z jejich větví, stav plánu, návrhové dokumenty, poslední průchody cyklem, rámeček cyklu z `RULES.md`, necommitnuté změny a nesloučené větve i s tím, jestli nad nimi běží session. **Živé a opuštěné session zjišťuje `sessions.py`**, který `collect.py` volá – čte registr běžících session Claude Code (`~/.claude/sessions/`), ověří, že proces žije, a větev bere z posledního záznamu transcriptu, protože session ve worktree layoutu startuje v kořeni kontejneru.

**Proč skript, a ne pokyny:** dřív skill vedl model přes desítky volání gitu a čtení souborů, každé s čekáním na model, a k tomu si pokaždé načítal `STRUCTURE.md`, `PREFLIGHT.md` a `LIFECYCLE.md`. Běh trval přes minutu, přestože uživatel chce jen rychlý návrh. Skript běží kolem vteřiny a model dělá jen úsudek. Druhý důvod je spolehlivost: **registr i transcript jsou vnitřní formát Claude Code bez dokumentace** a o obsazenosti větve rozhoduje testovaný kód (`tests/test_next.py`), ne úvaha modelu.

**Nástroj `ListAgents` je nenahradí, ověřeno 20. 9. 2026.** Vypisuje sice běžící session na stroji, ale jen jejich jméno, stav a stáří – ne větev ani adresář projektu. Rozhodnutí *nabídnout, nebo skrýt* stojí právě na větvi, takže registr i transcript se čtou dál vlastním skriptem.

**Skripty jsou implementační detail.** Závazné je jen to, co z nich plyne pro nabídku: úkol ve větvi, nad kterou běží živá session, se nenabízí; **session, která běží – i obnovená v jiném okně –, se k obnovení nenabízí nikdy**; opuštěná větev se nabídne jako první; a **nedá-li se to zjistit, bere se větev jako obsazená** a řekne se to nahlas.

------

## Fáze 0 – Příprava

`~/.claude/skills/PREFLIGHT.md` se **nenačítá**, ani `STRUCTURE.md` a `LIFECYCLE.md`. Co z nich skill potřebuje – kořen projektu a worktree layout, hlavní větev, stav pracovního stromu, režim umístění souborů, tvar bloku kola a pořadí kroků cyklu – zjistí nebo vyčte `collect.py`. Stav pracovního stromu neblokuje: rozpracované změny jsou položka fronty.

## Fáze 1 – Sběr

Pusť `python3 ~/.claude/skills/next/collect.py` z adresáře session. Nic dalšího nečti – **každé další volání stojí vteřiny čekání**, a výstup skriptu na nabídku stačí. Soubor otevři jen tehdy, když bez něj položku opravdu nejde popsat.

- **Skript skončil chybou** (není to git repozitář, nejde určit hlavní větev) → řekni to a skonči závěrečným verdiktem.
- **`docs` je null a nic dalšího nenašel** → projekt frontu nevede; řekni to a skonči.
- **`fetch` je `failed`** → pokračuj, ale v poznámkách řekni, že hlavní větev může být stará.

Co z výstupu je položka fronty:

| Klíč | Položka |
|---|---|
| `current.uncommitted` | necommitnuté změny tam, kde session stojí – rozdělaná práce tady |
| `todo` | každá položka ze všech sekcí (hotové skript vynechal) |
| `rounds` | kolo návrhu – viz *Kola návrhu* |
| `stitch_pending` | položka *sešít návrh po kolech*, spouštěč `/architect` |
| `plan.open` | jedna položka „dokončit plán“ s počtem zbývajících, spouštěč `/implement` |
| `artifacts`, `passes`, `lifecycle` | chybějící krok cyklu – viz *Místo v cyklu*; `lifecycle` je `{"osa": [...], "kontroly": [...]}` |
| `branches` | práce ve větvi – viz *Práce ve větvích* |
| `backlog` | skript ho vrací jen při prázdné frontě – viz *Fáze 2* |

### Položka odložená k datu

Položka, která nese hned za názvem `od <datum>`, má smysl až od toho dne – typicky *vyhodnotit provoz přes `/evaluate`*, kterou tam zapsal `/release`. Skript to rozhodl za tebe, pole `not_before` a `waiting`:

| `waiting` | S položkou |
|---|---|
| `true` | **do fronty nevstupuje** – jen ji zmiň v poznámkách i s datem, aby bylo vidět, že se na ni nezapomnělo |
| `false` | den nastal, řadí se jako každá jiná |

**Datum nepočítej sám a nepřepisuj ho.** Dnešní den zná skript a porovnal ho; položka, u které si termín přepočítáš z hlavy, se nabídne ve špatný den (`~/.claude/RULES.md`, *Hodnotu, kterou čte stroj, nepiš*).

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

**Větev s `current: true`** je ta, ve které session stojí: je-li `abandoned`, je to rozdělaná práce tady; je-li `occupied`, pracuje nad ní ještě jiné okno a platí totéž co pro jiné obsazené větve – **i když je to hlavní větev** (`main: true`). Hlavní větev skript vypíše jen tehdy, když na ní někdo pracuje nebo v jejím worktree leží neuložené změny.

### Kola návrhu

- **Kolo s `branch_state`, jehož větev je v `branches` jako `occupied`, `uncertain` nebo `abandoned`,** je práce ve větvi – řídí se *Prací ve větvích*, **nikdy se nenabízí jako nové kolo**. Chybí-li jeho větev v `branches` nebo je `empty`, nic v ní není a kolo se nabízí jako každé jiné. `branch_state` říká, co ve větvi čeká: hodnota řádku *Stav* z `todo.md` ve větvi (`rozhoduje se` = rozhodování, `rozhodnuto` = zápis před sloučením), nebo `merge_pending` (zbývá sloučit, provede `/merge`), když blok kola ve větvi už chybí a zbývá jen sloučení.
- **Kolo bez větve** se nabízí se spouštěčem `/architect <kolo>`; u něj řekni, do kterých dokumentů sahá (*Sahá na*) a jestli se to kříží s rozběhnutým kolem. **Souběh neblokuj, jen na něj upozorni.**
- **Bez worktree layoutu** větve kol nevznikají; kolo ve stavu `rozhoduje se` nebo `rozhodnuto` ber jako rozdělanou práci tady.

### Místo v cyklu

Chybějící krok odvoď z `artifacts` a `passes` proti `lifecycle`, a **jen pro osu** – `lifecycle["osa"]` je řada, ve které každý krok čeká na výstup toho předchozího, takže díra v ní je nález. Rozhodují přitom dokumenty, ne průchody: kroky osy do `## Průchodů životním cyklem` nepíšou, takže „chybí `/architect`“ poznáš z toho, že je `requirements.md` a není `architecture.md`, a „chybí `/breakdown`“ z návrhu bez plánu.

**Z `lifecycle["kontroly"]` chybějící krok neodvozuj.** Kontrolní kroky nejsou řada, stojí v mezerách a některé ve víc naráz, takže „ještě nepřišel na řadu“ u nich nic neznamená. Jediné, co se o nich dá z `passes` říct, je, že po odpracovaném plánu není zapsaný průchod `/review` – a to hlas jako domněnku.

**Nejsi-li si jistý, že krok opravdu chybí, řekni to u položky jako domněnku** – vědomě přeskočený krok se ze souborů pozná jen tehdy, když ho někdo zapsal.

## Fáze 2 – Řazení

Obsazené a nejisté větve ani položky s `waiting: true` do řazení nevstupují. Zbytek seřaď:

1. **Opuštěné větve** – od nejčerstvější (`last_ts`). Větev bez session k obnovení, na kterou nikdo nesáhl déle než měsíc, nedávej na první místo – je to spíš zapomenutý pokus než rozdělaná práce; nabídni ji mezi ostatními a řekni její stáří.
2. **Rozdělaná práce tady** – necommitnuté změny, rozpracovaný plán.
3. **Položky bez nesplněné závislosti** před těmi, které na něco čekají.
4. Mezi nimi ty, **na které čeká nejvíc dalších**.
5. Pak **pořadí v `todo.md`**.

Položky, které čekají na nesplněnou závislost, nevynechávej – vypiš je na konci.

**Je-li fronta prázdná a volání není zúžené**, vypiš `backlog` odděleně jako nezávazné nápady s upozorněním, že výběr znamená nejdřív rozhodnout o přesunu do `todo.md`. Do nabídky je nedávej.

## Fáze 3 – Nabídka

**Výpis je kompaktní: jeden řádek na položku.** Podrobnosti – co se bude dělat a čím se začne – nese až `description` u nabízených položek v `AskUserQuestion`. Generování textu je nejpomalejší část běhu a totéž dvakrát je čekání navíc.

```
<zastaralá položka, kříž kol, domnělá závislost, selhaný fetch – nebo že nic rozdělaného ani běžícího jinde není>

**Pracuje se jinde:** <název> (`<branch>`, <session / nejisté: proč>) · …

**Čeká na něco:** <název> (na <co>) · …

**S čím můžeme pokračovat**

1. <kolečko> <název> <(jen je-li co: čeká na …, opuštěná větev `<branch>`, rozdělané tady)>
2. …

○ drobnost · ◐ střední · ● velký
```

Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo – `~/.claude/RULES.md`, *Styl odpovědí*. Prázdnou část vynech.

**Pořadí je schválně od kontextu k výběru** (vyžádal si ho uživatel 16. 9. 2026): poznámky, práce jinde a čekající položky jsou okolnosti, které je dobré znát dřív, než se čte nabídka – a nabídka stojí poslední, těsně nad otázkou, ze které se vybírá. **Poznámky jsou holý odstavec bez popisku** a stojí úplně nahoře; **práce jinde a čekající položky jsou každá jeden odstavec** s tučným popiskem, položky za sebou oddělené `·`, ne seznam – jsou to informace, ze kterých se nevybírá.

**Tučný je jen nadpis a popisky částí, položky ne.** Položka je kolečko velikosti a název, nic víc – **stav „připravené“ ani velikost slovem se nepíšou**. Do závorky za název patří jen to, co mění rozhodnutí: nesplněná závislost, opuštěná větev, rozdělaná práce tady. Připravená položka bez závislosti závorku nemá. Tvar si výslovně vyžádal uživatel (16. 9. 2026): výpis se čte očima, ne jako tabulka, a slova navíc na každém řádku ho zahlcovala.

**Velikost** je kolečko hned za číslem – obyčejný textový znak, ne barevné emoji: přebírá barvu textu terminálu, takže nesvítí, a napůl plné kolečko se čte jako napůl velký úkol. Barevné kuličky uživatel odmítl jako moc křiklavé. Velikost odhaduj podle toho, co práce obnáší, ne podle délky zápisu:

| Kolečko | Velikost |
|---|---|
| ○ | drobnost – jedna, dvě odpovědi |
| ◐ | střední – session, jedno kolo, pár úkolů z plánu |
| ● | velký – víc sessions nebo celý krok cyklu |

**Spouštěč** je skill, když ho položka jmenuje nebo když jde o krok cyklu, kolo či plán; u opuštěné větve obnovení session nebo pokračování ve větvi; jinak první konkrétní krok. Skill si nevymýšlej k položce, se kterou nemá nic společného.

Pak přes `AskUserQuestion` nabídni **tři až čtyři** položky v pořadí z *Fáze 2*; první označ jako doporučenou. `description` začíná **kolečkem velikosti** a nese, **co se bude dělat a čím se začne** – jednou, dvěma větami. Volbu *Other* doplňuje nástroj sám – vybere-li ji uživatel, jde o jiný směr, ne o odmítnutí. **Nabízet není co** – všechno běží jinde nebo na něco čeká –, výběr nepokládej a skonči druhou závěrečnou větou.

## Fáze 4 – Předání

**Před předáním opuštěné větve – se session i bez ní – pusť `python3 ~/.claude/skills/next/sessions.py --project <root>`** (`root` z výstupu `collect.py`) a ověř obojí: že vybraná session není mezi živými **a** že nad větví nezačala pracovat jiná session nad projektem. Mezi výpisem a výběrem uběhla chvíle. Je-li obsazená, řekni to a nabídni zbytek fronty znovu.

**Opuštěná větev se session k obnovení.** Obnovit session neumíš – `/resume` píše uživatel. Dej mu oba tvary a skonči:

- v téhle session: `/resume <session_id>`,
- v novém okně terminálu: `cd <start_cwd> && claude --resume <session_id>` – `start_cwd` z `resume`: session se obnovuje z adresáře, kde startovala, a ve worktree layoutu to je kořen kontejneru.

**Opuštěná větev bez session.** Ve worktree layoutu přejdi do jejího pracovního adresáře podle `~/.claude/WORKTREE.md`; bez worktree layoutu se na větev přepni jen s čistým pracovním stromem, jinak se nejdřív zeptej, co s rozdělanými změnami.

**Je-li spouštěčem skill, vyvolej ho** přes nástroj `Skill` s argumentem, který položku určuje. Nic z toho, co jsi posbíral, mu neopakuj jako zadání.

**Jinak** načti podklady, na které položka odkazuje, shrň ve třech až pěti řádcích výchozí stav a pusť se do práce. Od té chvíle běží běžná práce podle pravidel projektu, ne tenhle skill.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím. U vybrané položky ji řekni **před** vyvoláním skillu nebo začátkem práce – potom už běh tohohle skillu nekončí, ale přechází:

- `Vybráno: <položka>, pokračuju <skillem / prací na ní / obnovením session – napiš /resume <session_id>>.`
- `Vybrat není z čeho – brání tomu: <konkrétní seznam>.`

Prázdná fronta i fronta, kde všechno běží jinde nebo na něco čeká, patří do druhé věty i s tím, co se prošlo: *„v `todo.md` ani v plánu nic nečeká, v gitu není nic rozdělaného, backlog je prázdný“*, nebo *„kolo o DPH běží ve větvi `architect-vat`, kolo o fakturaci čeká na něj“*.
