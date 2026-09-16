---
name: next
description: Skill se použije, když uživatel zadá "/next", nebo se na začátku session v projektu ptá, s čím pokračovat, co ho čeká a do čeho se může pustit – chce vidět seznam dalších úkolů seřazený podle důležitosti a závislostí a z nabídky si vybrat. Sestaví frontu z todo.md, implementačního plánu, kol návrhu, rozdělané práce v gitu a místa v životním cyklu, u každé položky řekne, v čem spočívá a jak je velká, nejaktuálnější nabídne k výběru a do vybrané se rovnou pustí. Na rozdíl od /cleanup, který dohledává, co se v session domluvilo, a zapisuje to, tenhle skill nic nezapisuje ani nepřeřazuje – jen čte, co už zapsané je. Nápady z backlogu nabízí až tehdy, když je fronta prázdná.
argument-hint: [zúžení]
allowed-tools: [Read, Glob, Grep, Bash, AskUserQuestion, Skill]
---

# Next

## Co skill dělá

Na začátku session v rozdělaném projektu odpoví na otázku **„s čím můžeme pokračovat?“**. Posbírá práci, která je rozhodnutá a nehotová, seřadí ji podle toho, co je na stole nejvíc, u každé položky řekne, v čem spočívá a jak je velká, a několik nejaktuálnějších nabídne přes `AskUserQuestion`. Po výběru se do úkolu rovnou pustí.

Režimy nemá. Argument je **volné zúžení** – `/next kola`, `/next review`, `/next DPH` – a omezí frontu na položky, kterých se týká. Bez argumentu jde o celou frontu. **`kola` znamená jen sekci `## Kola návrhu`** – tak skill volá `/specify round` bez jména kola.

## Co skill nedělá

- **Nic nezapisuje ani nepřeřazuje.** Zjistí-li, že je `todo.md` zastaralé (hotová položka, která se nepřesunula), řekne to jako poznámku; úklid souborů po session drží `/cleanup`.
- **Nerozkládá práci na úkoly.** Položka, která je na jednu session moc velká, se nabídne celá; rozpad do plánu dělá `/breakdown`.
- **Nerozhoduje o nápadech z backlogu.** Ukáže je, když fronta dojde, a přesun do `todo.md` nechá na uživateli.
- **Nevybírá za uživatele.** Doporučí, ale začne až po výběru.
- **Neodjede kolo návrhu.** Vybrané kolo předá `/specify round <kolo>`; tenhle skill jen drží, jak se kola nabízejí.

------

## Fáze 0 – Příprava

Společný začátek je v `~/.claude/skills/PREFLIGHT.md`. Odchylky:

- **Bod 3 blokovat nemá.** Skill nic nemění, takže rozpracované změny nejsou překážka, ale **položka fronty** – viz *Fáze 1*.
- **Body 4 a 5 odpadají.** Nic se nespouští a nepracuje se nad rozsahem větve.
- **Načti si `~/.claude/STRUCTURE.md`**, sekce `todo.md`, `backlog.md` a `done.md`. Tvar souborů, ze kterých se čte, drží on; bez něj nepoznáš blok kola od běžné položky ani odložený bod od úkolu.
- **Není-li kde číst** – projekt nemá `todo.md`, `plan.md` ani rozdělanou práci v gitu –, řekni to a skonči závěrečným verdiktem pro prázdnou frontu.

## Fáze 1 – Sběr

Nezávislá čtení pusť paralelně. **Frontu čti z hlavní větve**, ne z větve, ve které session zrovna stojí – ta může být stará nebo nesloučená. V pracovní větvi navíc přečti, co se rozdělalo v ní.

| Zdroj | Co z něj je položka |
|---|---|
| `git status --porcelain` | necommitnuté změny – rozdělaná práce, ke které se patří vrátit |
| `git branch`, `git worktree list` | nesloučené větve a worktree; u každé zjisti z posledních commitů, co se v ní dělá |
| `docs/todo.md` | každá nehotová položka ve všech sekcích včetně `## Parkované v session`; sekce `## Kola návrhu` podle *Kola návrhu* níž |
| `docs/plan.md` | neodpracované úkoly – jedna položka „dokončit plán“ s počtem zbývajících, ne každý úkol zvlášť |
| `docs/done.md`, `## Průchody životním cyklem` | kde projekt v cyklu stojí a který krok po posledním průchodu chybí; co po kterém kroku přichází, drží `~/.claude/skills/LIFECYCLE.md` |
| `docs/backlog.md` | **nic, dokud je fronta neprázdná** – viz *Fáze 2* |

**Cesty `docs/…` myslí soubor na místě podle režimu projektu** (`STRUCTURE.md`, *Dva režimy umístění*).

**Závislosti ber jen ze zápisu**, ne z odhadu: řádek *Čeká na*, pořadí v `plan.md`, výslovná zmínka v položce. Tuší-li se závislost, která zapsaná není, řekni ji u položky jako domněnku.

### Kola návrhu

Blok ze sekce `## Kola návrhu` je položka jako každá jiná, ale jeho stav leží jinde než na hlavní větvi:

- **Mapa se čte z `origin/main`** (`git show origin/main:docs/todo.md`) – blok v aktuální větvi může být neaktuální nebo nesloučený. Nemá-li hlavní větev mapu, ale pracovní větev ano, řekni, že je potřeba nejdřív sloučit `/specify create`.
- **Stav rozběhnutého kola leží v jeho větvi.** Existuje-li větev z řádku *Větev*, přečti řádek *Stav* odtud (`git show <větev>:docs/todo.md`). **Bez worktree layoutu** čti *Stav* rovnou z pracovního stromu.
- **Kolo ve stavu `rozhoduje se` nebo `rozhodnuto` se nenabízí jako nové kolo**, ať se nerozjede podruhé. Je to rozdělaná práce: `rozhodnuto` znamená, že ve větvi kola čeká zápis před sloučením.
- **U každého kola řekni, do kterých sdílených dokumentů sahá** (řádek *Sahá na*) a jestli se to kříží s rozběhnutým kolem. **Souběh tím neblokuj, jen na něj upozorni.**

## Fáze 2 – Řazení

Seřaď frontu v tomhle pořadí; uvnitř skupiny platí další kritérium:

1. **Rozdělaná práce** – necommitnuté změny, rozběhnuté kolo, rozpracovaný plán, nesloučená větev. Nechat ji ležet je dražší než cokoliv začít.
2. **Položky bez nesplněné závislosti** před těmi, které na něco čekají.
3. Mezi nimi ty, **na které čeká nejvíc dalších** položek, kol nebo odložených otázek.
4. Pak **pořadí a priorita, jak je drží `todo.md`**.

Položky, které čekají na nesplněnou závislost, **nevynechávej** – vypiš je na konci s tím, na co čekají. Uživatel má vidět celou frontu, ne jen tu dostupnou.

**Je-li fronta prázdná**, řekni to a teprve teď přečti `docs/backlog.md`. Nápady vypiš **odděleně, jako nezávazné** a s upozorněním, že výběr znamená nejdřív rozhodnout o přesunu do `todo.md` (`STRUCTURE.md`, *`backlog.md`*). Do nabídky je nemíchej.

## Fáze 3 – Nabídka

Nejdřív vypiš celou frontu, pak teprve nabídni výběr. Každá položka nese všech pět údajů – bez velikosti a spouštěče se z výpisu nedá vybrat:

```
## S čím můžeme pokračovat

**Rozdělané**
1. **<název>** · <drobnost / střední / velký> – <v čem úkol spočívá a co budeme dělat, jednou až dvěma větami>. <Odblokuje: … / Čeká na: …> · začíná se: <`/skill argument` nebo první krok>

**Připravené**
2. …

**Čekají na něco**
7. **<název>** – čeká na: <co>

**Poznámky**
- <zastaralá položka v todo.md, kříž kol nad týmž dokumentem, domnělá nezapsaná závislost – nebo sekce vynechaná>
```

Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo – `~/.claude/RULES.md`, *Styl odpovědí*. Prázdnou skupinu vynech.

**Velikost** odhadni podle toho, co práce obnáší, ne podle délky zápisu:

| Velikost | Kdy |
|---|---|
| drobnost | vejde se do jedné, dvou odpovědí – oprava, doplnění, jedno rozhodnutí |
| střední | zabere session – jedno kolo návrhu, několik úkolů z plánu, jeden běh prověřovacího kroku |
| velký | víc sessions nebo celý krok cyklu – nová feature, zbytek plánu, návrh od nuly |

Pak přes `AskUserQuestion` nabídni **tři až čtyři** nejvýš postavené položky z *Rozdělaných* a *Připravených*; první označ jako doporučenou a v `description` řekni velikost a čím se začne. Volbu *Other* doplňuje nástroj sám – vybere-li ji uživatel, jde o jiný směr, ne o odmítnutí: vyřeš, co napsal.

## Fáze 4 – Předání

**Má-li vybraná položka svůj skill, vyvolej ho** přes nástroj `Skill` s argumentem, který položku určuje – kolo návrhu `/specify round <kolo>`, rozpracovaný plán `/implement`, chybějící krok cyklu tím krokem. Skill si pak vede vlastní přípravu; nic z toho, co jsi posbíral, mu neopakuj jako zadání.

**Nemá-li ho**, načti podklady, na které položka odkazuje, shrň ve třech až pěti řádcích výchozí stav a pusť se do práce. Od té chvíle běží běžná práce podle pravidel projektu, ne tenhle skill.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím. U vybrané položky ji řekni **před** vyvoláním skillu nebo začátkem práce – potom už běh tohohle skillu nekončí, ale přechází:

- `Vybráno: <položka>, pokračuju <skillem / prací na ní>.`
- `Vybrat není z čeho – brání tomu: <konkrétní seznam>.`

Prázdná fronta patří do druhé věty i s tím, co se prošlo: *„v `todo.md` ani v plánu nic nečeká, v gitu není nic rozdělaného, backlog je prázdný“*.
