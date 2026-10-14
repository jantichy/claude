# /clauding – kolik času doopravdy trávím v Claude Code

Po pár měsících s Claude Code se člověk začne ptát, kolik času mu to vlastně bere. Odhad od oka nefunguje: jednou pracujete ve třech oknech naráz, jindy deset minut čekáte, až Claude doběhne, a pak odejdete na oběd a necháte okno otevřené. Tenhle skill to spočítá z toho, co Claude Code na disku sám zaznamenává, a vypíše hodiny po dnech, týdnech nebo měsících, s průměrem na den a s pár zajímavostmi navíc. Hodí se každému, kdo s Claudem pracuje denně a chce mít číslo, ne dojem.

## Co umí

- **`/clauding`** nebo **`/clauding month`** – hodiny po měsících za celou dobu, kterou data pokrývají.
- **`/clauding week`** – po týdnech od pondělí do neděle.
- **`/clauding day`** – po dnech.
- **Libovolné období česky** za režimem: „září“, „posledních 14 dní“, „minulý týden“, „od 1. 9.“.
- **U každého období** součet hodin, průměr na kalendářní den, průměr na den, kdy jste s Claudem opravdu pracovali, a kolik takových dnů bylo.
- **Zajímavosti**: nejdelší den, nejdelší blok v kuse, nejdelší řada dnů po sobě, kolik dnů jste strávili kolika hodinami, které dny v týdnu a hodiny dne jsou nejsilnější.
- **Starší období dopočítá odhadem**, když se podrobné záznamy už smazaly, a takové údaje označí.

## Proč zrovna tenhle

- **Souběžná okna se nesčítají.** Dvě hodiny ve dvou oknech naráz jsou pořád dvě hodiny, ne čtyři – a přechod z jednoho okna do druhého se nepočítá jako pauza.
- **Čekání na Clauda se počítá.** Když Claude dvacet minut pracuje a vy se díváte, je to čas strávený s ním.
- **Odchod se nepočítá.** Otázka, na kterou odpovíte až druhý den, ani příkaz, který přes noc čekal na vaše schválení, si nepřipíšou noc práce.
- **Commity se započtou, jen když vznikly při práci s Claudem**, ne ruční práce v repozitáři mimo něj.
- **Odhad se kalibruje na vašich datech.** Kde podrobné záznamy chybí, změří si na dnech, kde jsou, jak moc se hrubý výpočet z promptů liší od plného, a tím poměrem ho opraví.
- **Každé číslo vzniká skriptem**, ne odhadem modelu – stejná data dají pokaždé stejný výsledek.

## Jak se to používá

```
/clauding
/clauding week září
/clauding day posledních 14 dní
```

Stačí se i zeptat „kolik jsem tento měsíc strávil s Claudem?“.

## Ukázka výstupu

| Období | Hodiny | Ø na kalendářní den | Ø na aktivní den | Aktivní dny |
|---|---:|---:|---:|---:|
| červenec 2026 | ~14,9 | ~0,5 | ~1,5 | 10 z 31 |
| srpen 2026 | ~108,8 | ~3,5 | ~4,5 | 24 z 31 |
| září 2026 | ~269,4 | ~9,0 | ~9,0 | 30 z 30 |
| říjen 2026 | 92,3 | 7,1 | 7,1 | 13 z 13 |

- **Nejdelší den:** st 2. 9. 2026 – 17,0 h
- **Nejdelší blok v kuse:** 7. 9. 2026 07:45–17:45 – 10,0 h
- **Nejdelší řada dnů po sobě:** 44 (31. 8. – 13. 10. 2026)

Pod tím následuje rozložení dnů podle počtu hodin, dnů v týdnu a hodin dne jako malé sloupcové grafy.

## Co nedělá

- Neměří čas u klávesnice obecně, jen čas v Claude Code.
- Nefakturuje a nehledá zapomenutý čas pro klienta – na to je [`/invoicing`](../invoicing/README.md).
- Nepočítá, kolik vás to stojí peněz nebo tokenů.
- Nic nikam nezapisuje.

## Jak si ho nainstalovat

Je to snadné, zadejte do svého Claude Code tenhle prompt:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/clauding a nainstaluj mi ten skill k sobě do `~/.claude/skills/` – celý adresář i s podadresáři. Stáhni k němu z téhož repozitáře na odpovídající místo pod `~/.claude/` i sdílené soubory ze `skills/` a `standards/`, na které jeho soubory odkazují, a definice typů subagentů, které pouští, z `agents/` do `~/.claude/agents/`. Co už u sebe mám, nepřepisuj a ukaž mi rozdíl. Odkazuje-li na jiný skill, zeptej se mě, jestli ho chci taky. Odkazy na soubory, které v repozitáři nejsou, mi vypiš a u každého se zeptej, jestli ho napojit na můj vlastní soubor, nebo odkaz smazat. Nakonec mi řekni, co musím doplnit sám.

Výpočet stojí na sdíleném souboru `skills/timeline.py`, který prompt stáhne spolu se skillem; bez něj skript nespustí.

---

### Požadavky a omezení

- Claude Code a Python 3.9 nebo novější, nic dalšího se neinstaluje.
- Podrobné záznamy sessions Claude Code ve výchozím nastavení po 30 dnech maže; starší období pak skill jen odhaduje. Chcete-li přesná čísla i zpětně, zvyšte v nastavení `cleanupPeriodDays`.
- Čas se dělí do dnů podle pražského času.
- Čte všechny záznamy na disku, takže výpočet trvá desítky sekund.
