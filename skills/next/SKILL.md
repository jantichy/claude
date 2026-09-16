---
name: next
description: Skill se použije, když uživatel zadá "/next", nebo se na začátku session v projektu ptá, s čím pokračovat, co ho čeká a do čeho se může pustit – chce vidět seznam dalších úkolů seřazený podle důležitosti a závislostí a z nabídky si vybrat. Sestaví frontu z todo.md, implementačního plánu, kol návrhu, rozdělané práce v gitu a místa v životním cyklu, zvlášť vypíše, na čem se právě pracuje v jiné session, nabídne pokračování v opuštěných větvích, u každé položky řekne, v čem spočívá a jak je velká, nejaktuálnější nabídne k výběru a do vybrané se rovnou pustí. Na rozdíl od /cleanup, který dohledává, co se v session domluvilo, a zapisuje to, tenhle skill nic nezapisuje ani nepřeřazuje – jen čte, co už zapsané je. Nápady z backlogu vypíše až tehdy, když je fronta prázdná.
argument-hint: [zúžení]
allowed-tools: [Read, Glob, Grep, Bash, AskUserQuestion, Skill]
---

# Next

## Co skill dělá

Na začátku session v rozdělaném projektu odpoví na otázku **„s čím můžeme pokračovat?“**. Posbírá práci, která je rozhodnutá a nehotová, oddělí od ní to, na čem se právě pracuje v jiné session, zbytek seřadí podle toho, co je na stole nejvíc, u každé položky řekne, v čem spočívá a jak je velká, a několik nejaktuálnějších nabídne přes `AskUserQuestion`. Po výběru se do úkolu rovnou pustí, nebo – je-li to opuštěná session – řekne, jak ji obnovit.

Režimy nemá. Argument je **volné zúžení** – `/next review`, `/next DPH`, `/next Kola návrhu` – a omezí celý výpis včetně práce v jiných větvích na položky, v jejichž názvu, textu nebo nadpisu sekce se výraz vyskytuje, bez ohledu na velikost písmen; položka *sešít návrh po kolech* patří k zúžení `Kola návrhu` vždy. Bez argumentu jde o celou frontu. **Na zúžení `Kola návrhu` spoléhá `/specify round` bez jména kola** – nabídku kol si přenechává sem, takže sekce *Kola návrhu* níž je rozhraní mezi oběma skilly, ne vnitřek, který se smí tiše změnit.

## Co skill nedělá

- **Nic nezapisuje ani nepřeřazuje.** Zjistí-li, že je `todo.md` zastaralé (hotová položka, která se nepřesunula), řekne to jako poznámku; úklid souborů po session drží `/cleanup`. Jediné, co mění, jsou vzdálené reference po `git fetch`.
- **Nerozkládá práci na úkoly.** Položka, která je na jednu session moc velká, se nabídne celá; rozpad do plánu dělá `/breakdown`.
- **Nerozhoduje o nápadech z backlogu.** Vypíše je, když fronta dojde, a přesun do `todo.md` nechá na uživateli.
- **Nevybírá za uživatele.** Doporučí, ale začne až po výběru.
- **Neodjede kolo návrhu ani ho nesešije.** Vybrané kolo předá `/specify round <kolo>`, sešití `/specify`; tenhle skill jen drží, jak se kola nabízejí.
- **Nesahá do práce jiné session.** Co právě běží jinde, jen ohlásí – nepřepíná se do toho, nemerguje to a nenabízí to.
- **Neobnoví session sám.** `/resume` je příkaz, který píše uživatel; skill mu dá přesné znění a skončí.

## Jak je to postavené uvnitř

**Které session právě běží, v jaké větvi a která opuštěná session patří ke které větvi, zjišťuje skript `sessions.py`** v adresáři skillu. Čte registr běžících session Claude Code (`~/.claude/sessions/`), ověří, že proces opravdu žije, a z konce transcriptu každé session vezme pracovní adresář a větev poslední zprávy – session ve worktree layoutu startuje v kořeni kontejneru, takže adresář procesu větev neprozradí. **Registr i transcript jsou vnitřní formát Claude Code bez dokumentace**, a to je důvod, proč je to skript s testem (`tests/test_next.py`), a ne pokyn v textu: když se formát změní, pozná se to na testu, ne na tiše špatné nabídce.

**Skript je implementační detail.** Závazné je jen to, co z něj plyne pro nabídku: úkol ve větvi, nad kterou běží živá session, se nenabízí; **session, která běží – i obnovená v jiném okně –, se k obnovení nenabízí nikdy**; opuštěná větev se nabídne k pokračování; a **nedá-li se to zjistit, bere se větev jako obsazená** a řekne se to nahlas.

------

## Fáze 0 – Příprava

Společný začátek je v `~/.claude/skills/PREFLIGHT.md`. Odchylky:

- **Bod 3 blokovat nemá.** Skill nic nemění, takže rozpracované změny nejsou překážka, ale **položka fronty** – viz *Fáze 1*.
- **Bod 4 odpadá** – nic se nespouští. **Z bodu 5 platí jen určení hlavní větve**, ne rozsah diffu. Hlavní větev je tam popsaná jako cíl `merge-base`; v textu níž je to `<hlavní>`. **Bez remote** je to lokální `main` (nebo jak se hlavní větev jmenuje).
- **Má-li repozitář remote, pusť `git fetch --quiet`** dřív, než cokoliv čteš z `<hlavní>`. Bez toho vidíš stav z doby posledního stažení: nabídneš kolo, které jiná session mezitím zapsala a sloučila, nebo schováš práci, která už je hotová.
- **Načti si `~/.claude/STRUCTURE.md`**, sekce `todo.md`, `backlog.md` a `done.md`. Tvar souborů, ze kterých se čte, drží on; bez něj nepoznáš blok kola od běžné položky ani odložený bod od úkolu.
- **Urči cestu k `todo.md`, `plan.md`, `done.md` a `backlog.md`** podle režimu umístění (`STRUCTURE.md`, *Dva režimy umístění*). Cesty `docs/…` níž, i uvnitř příkazů, myslí tuhle cestu.

## Fáze 1 – Sběr

Nezávislá čtení pusť paralelně.

**Odkud se čte:** ve worktree layoutu **všechny soubory projektu** – fronta, plán, `done.md`, kola i artefakty pro místo v cyklu – z `<hlavní>` (`git show <hlavní>:<cesta>`); pracovní adresář session může být stará nebo cizí větev. Bez worktree layoutu z pracovního stromu, ať se započtou i necommitnuté úpravy. Stav jednotlivých větví se pak čte z nich samých – viz níž.

| Zdroj | Co z něj je položka |
|---|---|
| `git status --porcelain` | necommitnuté změny – rozdělaná práce **tady** |
| `git worktree list`, `git branch --no-merged <hlavní>` | práce ve větvích – viz *Práce ve větvích* níž |
| `docs/todo.md` | každá nehotová položka ve všech sekcích včetně `## Parkované v session`; sekce `## Kola návrhu` podle *Kola návrhu* níž |
| `docs/plan.md` | neodpracované úkoly – jedna položka „dokončit plán“ s počtem zbývajících, ne každý úkol zvlášť |
| místo v životním cyklu | krok, který po poslední práci chybí – viz *Místo v cyklu* níž |
| `docs/backlog.md` | **nic, dokud je fronta neprázdná** – viz *Fáze 2* |

**Závislosti ber jen ze zápisu**, ne z odhadu: řádek *Čeká na*, pořadí v `plan.md`, výslovná zmínka v položce. Tuší-li se závislost, která zapsaná není, řekni ji u položky jako domněnku.

**Nenašel-li se žádný zdroj** – projekt nemá `todo.md`, `plan.md`, rozdělanou práci v gitu ani stopu v cyklu –, řekni to a skonči závěrečným verdiktem.

### Práce ve větvích

**Úkol, na kterém se právě pracuje v jiné session, se nenabízí** – druhá session by ho rozjela podruhé a větve by se srazily. Ohlásí se ale hned nahoře, ať je vidět, co je rozebrané a kde. **Úkol v rozdělané větvi, nad kterou žádná session neběží, se naopak nabídne jako první** – je to zapomenutá práce, ke které se patří vrátit dřív, než se začne nová.

**1. Přiřaď položky větvím.** Pro každou nesloučenou větev – i tu, ve které session stojí – zjisti, na které položce se v ní pracuje:

- **Změny `todo.md`, `plan.md` a `done.md` ve větvi proti `<hlavní>`** (`git diff <hlavní>...<větev> -- docs/todo.md docs/plan.md docs/done.md`) – položka, blok kola nebo úkol, který větev mění, odškrtává nebo přesouvá do `done.md`, je její. **Přidává-li větev do `todo.md` řádek *Návrh sešitý*, nebo do `done.md` řádek *Návrh uzavřen*, patří jí položka *sešít návrh po kolech*.**
- **Řádek *Větev*** v blocích kol – kolo patří té větvi, **jakmile větev existuje**, i když v ní *Stav* ještě zůstal `čeká`.
- **Jméno větve a zprávy commitů** (`git log --oneline <hlavní>..<větev>`) proti názvům položek. Shoda jen tady je **domněnka** – řekni u položky, že je odvozená ze jména.

**Ber i větve, které `--no-merged` nevypíše:** čerstvě založená větev bez commitu ukazuje na commit hlavní větve, a přitom nad ní už může pracovat session z bodu 2 – přidej proto každou větev živé session nad projektem (kromě hlavní).

Větev, u které se žádnou položku přiřadit nepodařilo, vypiš taky, s tím, co v ní podle commitů je. **Větev, ve které session stojí, je rozdělaná práce tady** – ale i na ni se vztahuje bod 2: běží-li nad ní jiná session než tahle, je obsazená.

**2. Zjisti, nad kterými větvemi běží session a kde je opuštěná.** Pusť `python3 ~/.claude/skills/next/sessions.py --project <kořen projektu>` – ve worktree layoutu kořen kontejneru. Session s `self: true` je tahle a nepočítá se; počítají se jen session s `in_project: true` – stejně pojmenovaná větev v cizím repozitáři obsazenost nezakládá.

| Výsledek | Větev je | S položkou |
|---|---|---|
| v `sessions` je živá session nad projektem s touhle `branch` | **obsazená** | do *Už se na tom pracuje jinde* i se jménem session (`name`); nenabízí se |
| skript skončil kódem 2 (chybí registr nebo nejde přečíst některý jeho záznam), nebo má živá session nad projektem `branch: null` | **nejistá – všechny větve projektu** | do *Už se na tom pracuje jinde* s poznámkou, že se to zjistit nepodařilo a proč; nenabízí se. `branch: null` mívá čerstvě otevřené okno, ve kterém ještě nic nepadlo – řekni to, ať ho uživatel může zavřít nebo v něm začít, a pusť `/next` znovu |
| nic z toho | **opuštěná** | do *Opuštěné*; má-li v `idle` session, spouštěč je obnovení té session, jinak pokračování ve větvi |

**Proč nejistá větev padá na stranu obsazené:** nenabídnutá opuštěná větev stojí jeden řádek, který uživatel přečte a sám se rozhodne; nabídnutá obsazená větev stojí dvě session, které si přepisují tutéž práci, a pozná se to až při slučování.

**Z `idle` ber jen větve, které jsou nesloučené.** Skript vrací poslední session pro každou větev, kterou kdy projekt viděl, včetně dávno sloučených a `main`.

### Kola návrhu

Blok ze sekce `## Kola návrhu` je položka jako každá jiná, ale jeho stav leží jinde:

- **Mapa se čte tam, odkud se čte fronta** (*Fáze 1*). Nemá-li ji hlavní větev ve worktree layoutu, ale pracovní větev ano, řekni, že je potřeba nejdřív sloučit `/specify create`.
- **Kolo, jehož větev z řádku *Větev* existuje, je práce ve větvi** a řídí se *Prací ve větvích*: nad obsazenou větví se nenabízí, nad opuštěnou se nabídne pokračování – nikdy ne jako nové kolo. Z řádku *Stav* ve větvi (`git show <větev>:docs/todo.md`) řekni, co v ní čeká: rozhodování, nebo zápis před sloučením; **blok, který ve větvi zmizel**, znamená kolo zapsané a čekající na sloučení.
- **Bez worktree layoutu** větve kol nevznikají; *Stav* čti rovnou z pracovního stromu a kolo ve stavu `rozhoduje se` nebo `rozhodnuto` ber jako rozdělanou práci tady.
- **U nabízeného kola řekni, do kterých sdílených dokumentů sahá** (řádek *Sahá na*) a jestli se to kříží s rozběhnutým kolem. **Souběh tím neblokuj, jen na něj upozorni.**
- **Sešití návrhu:** nemá-li sekce už žádný blok, ale `done.md` má v `## Kola návrhu` záznamy kol a za posledním z nich nestojí řádek *Návrh uzavřen*, je položkou **„sešít návrh po kolech“** se spouštěčem `/specify`. Patří-li podle *Práce ve větvích* nějaké větvi, řídí se její obsazeností. Který běh sešití to je, pozná `/specify` sám; neurčuj to tady.

### Místo v cyklu

Chybějící krok cyklu odvoď z toho, **co v projektu leží**, ne jen ze záznamů – zakládací kroky do `## Průchody životním cyklem` nepíšou. Co po kterém kroku přichází, drží `~/.claude/skills/LIFECYCLE.md`; opírej se o něj, ne o paměť. Typicky: schválené `requirements.md` bez `architecture.md`, návrh bez `plan.md`, odpracovaný plán bez záznamu `/review` v *Průchodech*. **Nejsi-li si jistý, že krok opravdu chybí, řekni to u položky jako domněnku** – vědomě přeskočený krok se ze souborů pozná jen tehdy, když ho někdo zapsal.

## Fáze 2 – Řazení

Obsazené a nejisté větve do řazení nevstupují. Zbytek seřaď v tomhle pořadí; uvnitř skupiny platí další kritérium:

1. **Opuštěné větve** – od nejčerstvější session. Rozdělaná práce, na kterou se zapomnělo, se před novou nabízí vždy.
2. **Rozdělaná práce tady** – necommitnuté změny, položka větve, ve které session stojí, rozpracovaný plán.
3. **Položky bez nesplněné závislosti** před těmi, které na něco čekají.
4. Mezi nimi ty, **na které čeká nejvíc dalších** položek, kol nebo odložených otázek.
5. Pak **pořadí a priorita, jak je drží `todo.md`**.

Položky, které čekají na nesplněnou závislost, **nevynechávej** – vypiš je na konci s tím, na co čekají. Uživatel má vidět celou frontu, ne jen tu dostupnou.

**Je-li fronta prázdná a volání není zúžené**, řekni to a teprve teď přečti `docs/backlog.md`. Nápady **jen vypiš**, odděleně a jako nezávazné, s upozorněním, že výběr znamená nejdřív rozhodnout o přesunu do `todo.md` (`STRUCTURE.md`, *`backlog.md`*). Do nabídky je nedávej. Při zúženém volání backlog nečti – zúžení se ptá na konkrétní frontu, ne na nápady.

## Fáze 3 – Nabídka

Nejdřív vypiš celou frontu, pak teprve nabídni výběr. Nabízená položka nese **pět údajů**: název, velikost, v čem spočívá, na co čeká nebo co odblokuje, a čím se začíná. Bez velikosti a spouštěče se z výpisu nedá vybrat.

```
## S čím můžeme pokračovat

**Už se na tom pracuje jinde**
- **<název>** – větev `<větev>`, session `<name>`<, worktree `<cesta>`>; <co v ní čeká><, přiřazeno podle jména větve><, nejisté: proč>

**Opuštěné**
1. **<název>** · <velikost> – <co ve větvi zbývá>; naposledy <kdy>. · začíná se: <obnovit session / pokračovat ve větvi `<větev>`>

**Rozdělané tady**
2. **<název>** · <drobnost / střední / velký> – <v čem úkol spočívá a co budeme dělat, jednou až dvěma větami>. <Odblokuje: … / Čeká na: …> · začíná se: <`/skill argument` nebo první krok>

**Připravené**
3. …

**Čekají na něco**
7. **<název>** – čeká na: <co>

**Poznámky**
- <zastaralá položka v todo.md, kříž kol nad týmž dokumentem, domnělá nezapsaná závislost>
```

Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo – `~/.claude/RULES.md`, *Styl odpovědí*. Prázdnou skupinu vynech. Sekce *Už se na tom pracuje jinde* stojí **vždy první**, i když má jediný řádek.

**Velikost** odhadni podle toho, co práce obnáší, ne podle délky zápisu:

| Velikost | Kdy |
|---|---|
| drobnost | vejde se do jedné, dvou odpovědí – oprava, doplnění, jedno rozhodnutí |
| střední | zabere session – jedno kolo návrhu, několik úkolů z plánu, jeden běh prověřovacího kroku |
| velký | víc sessions nebo celý krok cyklu – nová feature, zbytek plánu, návrh od nuly |

**Spouštěč** je skill, když ho položka jmenuje nebo když jde o krok cyklu, kolo návrhu či plán (`/specify round <kolo>`, `/implement`, `/review`); u opuštěné větve obnovení session nebo pokračování ve větvi; jinak první konkrétní krok práce. Skill si nevymýšlej k položce, se kterou nemá nic společného.

Pak přes `AskUserQuestion` nabídni **tři až čtyři** položky v pořadí z *Fáze 2* – **opuštěné větve jako první** –; první označ jako doporučenou a v `description` řekni velikost a čím se začne. Volbu *Other* doplňuje nástroj sám – vybere-li ji uživatel, jde o jiný směr, ne o odmítnutí: vyřeš, co napsal. **Nabízet není co** – všechno se dělá jinde nebo na něco čeká –, výběr nepokládej a skonči druhou závěrečnou větou.

## Fáze 4 – Předání

**Před předáním opuštěné větve – se session i bez ní – pusť `sessions.py` znovu** a ověř obojí: že vybraná session není mezi živými **a** že nad větví nezačala pracovat jiná, i nová session. Mezi výpisem a výběrem uběhla chvíle a uživatel mohl větev otevřít v jiném okně. Je-li obsazená, řekni to a nabídni zbytek fronty znovu.

**Opuštěná větev se session k obnovení.** Obnovit session neumíš – `/resume` je příkaz, který píše uživatel. Dej mu oba tvary a skonči:

- v téhle session: `/resume <session_id>`,
- v novém okně terminálu: `cd <start_cwd> && claude --resume <session_id>` – `start_cwd` z `idle`, ne `cwd`: session se obnovuje z adresáře, kde startovala, a ve worktree layoutu to je kořen kontejneru, ne worktree větve.

Obnovená session má celý kontext rozdělané práce, a proto má přednost před pokračováním tady.

**Opuštěná větev bez session.** Ve worktree layoutu přejdi do jejího pracovního adresáře podle `~/.claude/WORKTREE.md`; bez worktree layoutu se na větev přepni jen s čistým pracovním stromem, jinak se nejdřív zeptej, co s rozdělanými změnami. Pak pokračuj jako u ostatních položek.

**Je-li spouštěčem skill, vyvolej ho** přes nástroj `Skill` s argumentem, který položku určuje. Skill si pak vede vlastní přípravu; nic z toho, co jsi posbíral, mu neopakuj jako zadání.

**Jinak** načti podklady, na které položka odkazuje, shrň ve třech až pěti řádcích výchozí stav a pusť se do práce. Od té chvíle běží běžná práce podle pravidel projektu, ne tenhle skill.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím. U vybrané položky ji řekni **před** vyvoláním skillu nebo začátkem práce – potom už běh tohohle skillu nekončí, ale přechází:

- `Vybráno: <položka>, pokračuju <skillem / prací na ní / obnovením session – napiš /resume <session_id>>.`
- `Vybrat není z čeho – brání tomu: <konkrétní seznam>.`

Prázdná fronta i fronta, kde všechno běží jinde nebo na něco čeká, patří do druhé věty i s tím, co se prošlo: *„v `todo.md` ani v plánu nic nečeká, v gitu není nic rozdělaného, backlog je prázdný“*, nebo *„kolo o DPH běží ve větvi `specify-dph`, kolo o fakturaci čeká na něj“*.
