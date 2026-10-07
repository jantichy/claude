# Záznam průchodu v `done.md`

Tvar a pravidla řádku, který si kontrolní kroky životního cyklu zapisují do `docs/done.md` po dokončeném běhu. Načítá ho skill, který záznam zapisuje (odkazuje sem v místě zápisu), a `/release`, který z něj čte, jestli kontroly proběhly. Ostatní kroky cyklu ho nepotřebují, proto nestojí v `~/.claude/standards/lifecycle.md`.

**Sekce `## Průchody životním cyklem`** v `done.md` drží po jednom řádku za dokončený běh těch kroků cyklu, **které mají svého čtenáře**. Zapisují si ho skilly samy, ne člověk; koho záznam slouží, říká každý skill u svého zápisu.

- **`/review` a `/attack`** – zapisují se i tam, kam se nenasazuje. **Hash je tu kvůli `/release`:** o dny později z paměti nepozná, jestli kontrola běžela nad *tímhle*.
- **`/oponent`** – se seznamem hledisek, bez kterého příští běh nepozná, s čím srovnávat počty nálezů.
- **`/consolidate`** – **i po běhu bez přijatého návrhu** a s **počty, ze kterých se dá časem dofitovat práh** „dost kol“.
- **`/consistency` a `/cleanup`** – **`/cleanup` uvádí i id uklizené session**; dvě data u téhož id znamenají dva úklidy. **Hash je stopa, ne čára:** druhý běh vytěžuje transcript vždy celý, protože hash vzniká před commitem zápisů úklidu.

**`/evaluate` sem vědomě nezapisuje** – datum běhu nese hlavička `operation.md`. **`/merge` taky ne** – záznamem je merge commit.

**Kritérium je „má to svého čtenáře“, ne „je to krok cyklu“** – jinak sekce zbytní a přestane se číst. **Rozšiřovat výčet mlčky se nesmí** – skill, který do sekce začne zapisovat, se do něj nejdřív dopíše.

```
- **2026-09-02** · `/review` · `ff0f765` · změny na větvi (14 souborů) · 12 nálezů (3 opraveno, 7 odloženo, 2 won't fix)
```

Datum vyrob `date +%F`, hash `git rev-parse --short HEAD` – obojí příkazem, ne z kontextu (`~/.claude/standards/rules.md`, *Hodnotu, kterou čte stroj, nepiš – nech ji vyrobit příkazem*).

**Běžel-li krok nad jiným repozitářem, než ve kterém záznam leží, uveď u hashe i zdroj:** `` `~/.claude@574dade` `` – typicky když repozitář bez vlastního `done.md` odkládá záznamy do sousedního. **Holý hash z cizího repozitáře je horší než žádný:** příští běh ho hledá ve špatném stromu a `git log <hash>..HEAD` tam selže, nebo tiše vrátí něco jiného.

**Výjimka z pravidla o zrcadlení:** jako jediná sekce `done.md` nemá protějšek v `todo.md` – průchod není odložený úkol.
