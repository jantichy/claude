# /worktree – několik rozdělaných větví vedle sebe, každá ve svém adresáři

Přepne projekt do uspořádání, ve kterém má každá rozdělaná větev vlastní adresář na disku. Můžete pak nad jedním projektem pustit několik Claude sessions naráz – každou na jiné věci – a nestane se, že by si navzájem přepisovaly soubory nebo commitovaly rozdělanou práci té druhé. Přepnutí i návrat zpátky jsou jeden příkaz, včetně zálohy a kontroly, že se cestou nic neztratilo. Hodí se všude, kde běžně přepínáte mezi dvěma třemi rozdělanými věcmi a `git stash` vás už unavuje.

## Co umí

- **`/worktree enable`** – zřídí uspořádání. V prázdném adresáři založí nový projekt, u existujícího repozitáře ho převede: nejdřív zálohuje, pak přeskládá, nakonec porovná starý a nový obsah a teprve pak zálohu smaže.
- **`/worktree disable`** – převede projekt zpátky na obyčejný adresář. Zbývá-li rozdělaná větev, odmítne to a řekne která – slití nebo zahození větve nechává na vás.
- **`/worktree status`** (nebo `/worktree` bez ničeho) – řekne, jestli je uspořádání zapnuté, co je rozdělané a jaké větve existují.
- Pravidla, jak se v tom uspořádání pracuje, si při zapnutí **nainstaluje rovnou do projektu**, takže je Claude zná od začátku každé session, aniž byste skill volali.

## Proč zrovna tenhle

- **Stav se nikam nezapisuje, pozná se z disku.** Nemůže se tedy stát, že by nastavení tvrdilo něco jiného, než jak to doopravdy je.
- **Přeskládání je odzálohované a ověřené.** Sahá se na `.git`, což je ta nejcitlivější věc v repozitáři – proto se nejdřív pořídí kopie, na konci se obojí porovná a záloha zmizí, až když porovnání vyjde.
- **Návrat zpátky je plnohodnotná funkce**, ne jen poznámka v dokumentaci. Uspořádání se dá zkusit a zase opustit.
- **Zná pasti, které si jinak najdete sami** – třeba že v hlavním adresáři projektu přestane fungovat `git status`, kdežto `git diff` tam projde a vrátí smyšlený seznam změn.

## Jak se to používá

```
/worktree enable
```

Claude si najde projekt, zeptá se na potvrzení, přeskládá adresář a napíše, kde je záloha a jestli kontrola prošla. Od té chvíle si pro každou novou práci zakládá vlastní adresář.

## Ukázka výstupu

Z obyčejného adresáře projektu se stane tohle:

```
rezervace/
├── .bare/          samotný repozitář – jedna kopie dat pro všechny větve
├── main/           hlavní větev, tady se čte a merguje
├── platby/         rozdělaná větev, vlastní adresář
└── export/         další rozdělaná větev, vedle ní
```

Sessions v `platby/` a `export/` na sebe nevidí a nešlapou si po souborech.

## Co nedělá

- **Nezakládá větve ani nemerguje.** To je běžná práce – Claude ji dělá podle pravidel, která skill do projektu nainstaluje, ne voláním skillu.
- **Nezakládá projekt.** Celé nastavení projektu vede `/project`, který se na tohle uspořádání ptá jako na jeden ze svých kroků.
- **Neradí, jestli se vám to hodí.** Nad projektem, kde děláte vždycky jednu věc, je to zbytečná složitost.

## Jak si ho nainstalovat

Nechte to na Claudovi. Otevřete si Claude Code a napište mu:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/worktree
> a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.

Nic dalšího potřeba není. Pravidla provozu jsou součástí skillu a instalují se s ním.

---

### Požadavky a omezení

Git a jakákoli platforma. Zrychlené kopírování záloh (`cp -c`) využívá souborový systém APFS, tedy macOS; jinde se zálohuje běžnou kopií, což trvá déle a zabere místo. Uspořádání předpokládá, že projekt má jednu hlavní větev, ze které ostatní vycházejí.
