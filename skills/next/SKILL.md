---
name: next
description: Skill se použije, když uživatel zadá "/next", nebo se na začátku session v projektu ptá, s čím pokračovat, co ho čeká a do čeho se může pustit – chce vidět seznam dalších úkolů seřazený podle důležitosti a závislostí a z nabídky si vybrat. Sestaví frontu z todo.md, implementačního plánu, kol návrhu, rozdělané práce v gitu a místa v životním cyklu, zvlášť vypíše, na čem se už pracuje v jiných větvích, u každé položky řekne, v čem spočívá a jak je velká, nejaktuálnější nabídne k výběru a do vybrané se rovnou pustí. Na rozdíl od /cleanup, který dohledává, co se v session domluvilo, a zapisuje to, tenhle skill nic nezapisuje ani nepřeřazuje – jen čte, co už zapsané je. Nápady z backlogu vypíše až tehdy, když je fronta prázdná.
argument-hint: [zúžení]
allowed-tools: [Read, Glob, Grep, Bash, AskUserQuestion, Skill]
---

# Next

## Co skill dělá

Na začátku session v rozdělaném projektu odpoví na otázku **„s čím můžeme pokračovat?“**. Posbírá práci, která je rozhodnutá a nehotová, oddělí od ní to, na čem se už pracuje v jiné větvi, zbytek seřadí podle toho, co je na stole nejvíc, u každé položky řekne, v čem spočívá a jak je velká, a několik nejaktuálnějších nabídne přes `AskUserQuestion`. Po výběru se do úkolu rovnou pustí.

Režimy nemá. Argument je **volné zúžení** – `/next review`, `/next DPH`, `/next Kola návrhu` – a omezí frontu na položky, v jejichž názvu, textu nebo nadpisu sekce se výraz vyskytuje, bez ohledu na velikost písmen. Bez argumentu jde o celou frontu. **Na zúžení `Kola návrhu` spoléhá `/specify round` bez jména kola** – nabídku kol si přenechává sem, takže sekce *Kola návrhu* níž je rozhraní mezi oběma skilly, ne vnitřek, který se smí tiše změnit.

## Co skill nedělá

- **Nic nezapisuje ani nepřeřazuje.** Zjistí-li, že je `todo.md` zastaralé (hotová položka, která se nepřesunula), řekne to jako poznámku; úklid souborů po session drží `/cleanup`.
- **Nerozkládá práci na úkoly.** Položka, která je na jednu session moc velká, se nabídne celá; rozpad do plánu dělá `/breakdown`.
- **Nerozhoduje o nápadech z backlogu.** Vypíše je, když fronta dojde, a přesun do `todo.md` nechá na uživateli.
- **Nevybírá za uživatele.** Doporučí, ale začne až po výběru.
- **Neodjede kolo návrhu ani ho nesešije.** Vybrané kolo předá `/specify round <kolo>`, sešití `/specify`; tenhle skill jen drží, jak se kola nabízejí.
- **Nesahá do cizích větví.** Práci rozběhnutou jinde jen ohlásí – nepřepíná se do ní, nemerguje ji a nenabízí ji znovu.

------

## Fáze 0 – Příprava

Společný začátek je v `~/.claude/skills/PREFLIGHT.md`. Odchylky:

- **Bod 3 blokovat nemá.** Skill nic nemění, takže rozpracované změny nejsou překážka, ale **položka fronty** – viz *Fáze 1*.
- **Body 4 a 5 odpadají.** Nic se nespouští a nepracuje se nad rozsahem větve.
- **Načti si `~/.claude/STRUCTURE.md`**, sekce `todo.md`, `backlog.md` a `done.md`. Tvar souborů, ze kterých se čte, drží on; bez něj nepoznáš blok kola od běžné položky ani odložený bod od úkolu.
- **Urči hlavní větev**: `origin/main`, má-li repozitář remote, jinak `main`; jmenuje-li se hlavní větev jinak, postupuj podle `PREFLIGHT.md`, bod 5. V textu níž je to `<hlavní>`.
- **Urči cestu k `todo.md`, `plan.md`, `done.md` a `backlog.md`** podle režimu umístění (`STRUCTURE.md`, *Dva režimy umístění*). Cesty `docs/…` níž, i uvnitř příkazů, myslí tuhle cestu.

## Fáze 1 – Sběr

Nezávislá čtení pusť paralelně.

**Odkud se čte fronta:** ve worktree layoutu z `<hlavní>` (`git show <hlavní>:docs/todo.md`) – pracovní adresář session může být stará nebo cizí větev. Bez worktree layoutu z pracovního stromu, ať se započtou i necommitnuté úpravy `todo.md`.

| Zdroj | Co z něj je položka |
|---|---|
| `git status --porcelain` | necommitnuté změny – rozdělaná práce **tady** |
| `git worktree list`, `git branch --no-merged <hlavní>` | práce rozběhnutá v jiné větvi – viz *Práce v jiných větvích* níž |
| `docs/todo.md` | každá nehotová položka ve všech sekcích včetně `## Parkované v session`; sekce `## Kola návrhu` podle *Kola návrhu* níž |
| `docs/plan.md` | neodpracované úkoly – jedna položka „dokončit plán“ s počtem zbývajících, ne každý úkol zvlášť |
| místo v životním cyklu | krok, který po poslední práci chybí – viz *Místo v cyklu* níž |
| `docs/backlog.md` | **nic, dokud je fronta neprázdná** – viz *Fáze 2* |

**Závislosti ber jen ze zápisu**, ne z odhadu: řádek *Čeká na*, pořadí v `plan.md`, výslovná zmínka v položce. Tuší-li se závislost, která zapsaná není, řekni ji u položky jako domněnku.

**Nenašel-li se žádný zdroj** – projekt nemá `todo.md`, `plan.md`, rozdělanou práci v gitu ani stopu v cyklu –, řekni to a skonči závěrečným verdiktem.

### Práce v jiných větvích

**Úkol, na kterém se už pracuje v jiné větvi, se nenabízí** – druhá session by ho rozjela podruhé a větve by se srazily. Ohlásí se ale hned nahoře, ať je vidět, co je rozebrané a kde.

Pro každou nesloučenou větev kromě té, ve které session stojí, zjisti, **na které položce se v ní pracuje**:

1. **Změny `todo.md` a `plan.md` ve větvi proti `<hlavní>`** (`git diff <hlavní>...<větev> -- docs/todo.md docs/plan.md`) – položka, blok kola nebo úkol, který větev mění, odškrtává nebo přesouvá do `done.md`, je její.
2. **Řádek *Větev*** v blocích kol – kolo patří té větvi, i když se v ní zatím nic nezměnilo.
3. **Jméno větve a zprávy commitů** (`git log --oneline <hlavní>..<větev>`) proti názvům položek. Shoda jen tady je **domněnka** – vypiš ji s tím, že je odvozená ze jména, a položku přesto nenabízej; omylem skrytý úkol je levnější než rozjetý dvakrát.

**Ve worktree layoutu** (`~/.claude/WORKTREE.md`) je každý pracovní adresář větve otevřená práce; u něj uveď i cestu, ať je jasné, kam se za ní jít podívat. Větev bez worktree je rozdělaná, ale odložená – ohlas ji stejně, jen bez cesty.

Větev, u které se nepodařilo žádnou položku přiřadit, vypiš taky, s tím, co v ní podle commitů je.

**Session stojí ve větvi sama** – její položka není „jinde“, ale **rozdělaná tady** a nabízí se jako pokračování.

### Kola návrhu

Blok ze sekce `## Kola návrhu` je položka jako každá jiná, ale jeho stav leží jinde než na hlavní větvi:

- **Mapa se čte z `<hlavní>`** i bez worktree layoutu – blok v pracovní větvi může být neaktuální nebo nesloučený. Nemá-li hlavní větev mapu, ale pracovní větev ano, řekni, že je potřeba nejdřív sloučit `/specify create`.
- **Stav rozběhnutého kola leží v jeho větvi.** Existuje-li větev z řádku *Větev*, přečti řádek *Stav* odtud (`git show <větev>:docs/todo.md`). **Bez worktree layoutu** čti *Stav* rovnou z pracovního stromu.
- **Kolo ve stavu `rozhoduje se` nebo `rozhodnuto` patří do *Práce v jiných větvích*** – nenabízí se, ať se nerozjede podruhé. Ze stavu řekni, co v jeho větvi čeká: rozhodování, nebo zápis před sloučením.
- **Blok, který ve větvi kola zmizel**, znamená kolo zapsané a čekající na sloučení; větev ohlas stejně, se stavem „čeká na sloučení“.
- **U nabízeného kola řekni, do kterých sdílených dokumentů sahá** (řádek *Sahá na*) a jestli se to kříží s rozběhnutým kolem. **Souběh tím neblokuj, jen na něj upozorni.**
- **Sešití návrhu:** nemá-li sekce už žádný blok, ale `done.md` má v `## Kola návrhu` záznamy kol a za posledním z nich nestojí řádek *Návrh uzavřen* – nebo v `todo.md` stojí řádek *Návrh sešitý* –, je položkou **„sešít návrh po kolech“** se spouštěčem `/specify`. Který běh sešití to je, pozná `/specify` sám; neurčuj to tady.

### Místo v cyklu

Chybějící krok cyklu odvoď z toho, **co v projektu leží**, ne jen ze záznamů – zakládací kroky do `## Průchody životním cyklem` nepíšou. Co po kterém kroku přichází, drží `~/.claude/skills/LIFECYCLE.md`; opírej se o něj, ne o paměť. Typicky: schválené `requirements.md` bez `architecture.md`, návrh bez `plan.md`, odpracovaný plán bez záznamu `/review` v *Průchodech*. **Nejsi-li si jistý, že krok opravdu chybí, řekni to u položky jako domněnku** – vědomě přeskočený krok se ze souborů pozná jen tehdy, když ho někdo zapsal.

## Fáze 2 – Řazení

Práce z *Práce v jiných větvích* do řazení nevstupuje. Zbytek seřaď v tomhle pořadí; uvnitř skupiny platí další kritérium:

1. **Rozdělaná práce tady** – necommitnuté změny, položka větve, ve které session stojí, rozpracovaný plán. Nechat ji ležet je dražší než cokoliv začít.
2. **Položky bez nesplněné závislosti** před těmi, které na něco čekají.
3. Mezi nimi ty, **na které čeká nejvíc dalších** položek, kol nebo odložených otázek.
4. Pak **pořadí a priorita, jak je drží `todo.md`**.

Položky, které čekají na nesplněnou závislost, **nevynechávej** – vypiš je na konci s tím, na co čekají. Uživatel má vidět celou frontu, ne jen tu dostupnou.

**Je-li fronta prázdná a volání není zúžené**, řekni to a teprve teď přečti `docs/backlog.md`. Nápady **jen vypiš**, odděleně a jako nezávazné, s upozorněním, že výběr znamená nejdřív rozhodnout o přesunu do `todo.md` (`STRUCTURE.md`, *`backlog.md`*). Do nabídky je nedávej. Při zúženém volání backlog nečti – zúžení se ptá na konkrétní frontu, ne na nápady.

## Fáze 3 – Nabídka

Nejdřív vypiš celou frontu, pak teprve nabídni výběr. Nabízená položka nese **pět údajů**: název, velikost, v čem spočívá, na co čeká nebo co odblokuje, a čím se začíná. Bez velikosti a spouštěče se z výpisu nedá vybrat.

```
## S čím můžeme pokračovat

**Už se na tom pracuje jinde**
- **<název>** – větev `<větev>`<, worktree `<cesta>`>; <co v ní čeká: rozhodování / zápis před sloučením / implementace …><, přiřazeno podle jména větve>

**Rozdělané tady**
1. **<název>** · <drobnost / střední / velký> – <v čem úkol spočívá a co budeme dělat, jednou až dvěma větami>. <Odblokuje: … / Čeká na: …> · začíná se: <`/skill argument` nebo první krok>

**Připravené**
2. …

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

**Spouštěč** je skill, když ho položka jmenuje nebo když jde o krok cyklu, kolo návrhu či plán (`/specify round <kolo>`, `/implement`, `/review`); jinak první konkrétní krok práce. Skill si nevymýšlej k položce, se kterou nemá nic společného.

Pak přes `AskUserQuestion` nabídni **tři až čtyři** nejvýš postavené položky z *Rozdělaných tady* a *Připravených*; první označ jako doporučenou a v `description` řekni velikost a čím se začne. Volbu *Other* doplňuje nástroj sám – vybere-li ji uživatel, jde o jiný směr, ne o odmítnutí: vyřeš, co napsal. **Nabízet není co** – všechno se dělá jinde nebo na něco čeká –, výběr nepokládej a skonči druhou závěrečnou větou.

## Fáze 4 – Předání

**Je-li spouštěčem skill, vyvolej ho** přes nástroj `Skill` s argumentem, který položku určuje. Skill si pak vede vlastní přípravu; nic z toho, co jsi posbíral, mu neopakuj jako zadání.

**Jinak** načti podklady, na které položka odkazuje, shrň ve třech až pěti řádcích výchozí stav a pusť se do práce. Od té chvíle běží běžná práce podle pravidel projektu, ne tenhle skill.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím. U vybrané položky ji řekni **před** vyvoláním skillu nebo začátkem práce – potom už běh tohohle skillu nekončí, ale přechází:

- `Vybráno: <položka>, pokračuju <skillem / prací na ní>.`
- `Vybrat není z čeho – brání tomu: <konkrétní seznam>.`

Prázdná fronta i fronta, kde všechno běží jinde nebo na něco čeká, patří do druhé věty i s tím, co se prošlo: *„v `todo.md` ani v plánu nic nečeká, v gitu není nic rozdělaného, backlog je prázdný“*, nebo *„kolo o DPH běží ve větvi `specify-dph`, kolo o fakturaci čeká na něj“*.
