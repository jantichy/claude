# /clauding – kolik času doopravdy trávím v Claude Code

Po pár měsících s Claude Code se člověk začne ptát, kolik času mu to vlastně bere. Odhad od oka nefunguje: jednou pracujete ve třech oknech naráz, jindy deset minut čekáte, až Claude doběhne, a pak odejdete na oběd a necháte okno otevřené. Tenhle skill to spočítá z toho, co Claude Code na disku sám zaznamenává, a vypíše hodiny po dnech, týdnech nebo měsících, s průměrem na den a s pár zajímavostmi navíc. Hodí se každému, kdo s Claudem pracuje denně a chce mít číslo, ne dojem.

## Co umí

- **`/clauding`** nebo **`/clauding month`** – hodiny po měsících za celou dobu, kterou data pokrývají.
- **`/clauding week`** – po týdnech od pondělí do neděle.
- **`/clauding day`** – po dnech.
- **Libovolné období česky** za režimem: „září“, „posledních 14 dní“, „minulý týden“, „od 1. 9.“.
- **U každého období** součet hodin, průměr na kalendářní den, průměr na den, kdy jste s Claudem opravdu pracovali, kolik takových dnů bylo a v kolika sessions a projektech se pracovalo.
- **Kolik vaší pozornosti Claude spotřebuje** – na kolik jeho otázek s nabídnutými variantami jste odpověděli, kolikrát jste ho zastavili klávesou Esc a kolikrát jste mu zamítli akci, každé zvlášť i dohromady na hodinu práce.
- **Kolik práce za tím je** – počet commitů, kolik znaků jste do promptů napsali a jak dlouhý je průměrný prompt.
- **Které skilly používáte** – tabulka vlastních skillů seřazená podle počtu spuštění, u každého zvlášť, kolikrát jste ho zadali příkazem, kolikrát ho Claude spustil na pokyn slovy („přimerguj to“) a kolikrát ho pustil jiný skill – když `/merge` pouští `/end`, připíše se čárka i k `/end`.
- **Kolik času jste strávili v kterém projektu** – každý projekt zvlášť, i když jste jich měli otevřených víc naráz. Hodina ve třech projektech souběžně se připíše každému z nich, takže z toho vyjde i to, kolik projektů máte v průměru rozdělaných naráz, kolik času běží víc projektů zároveň a kolik jich nejvíc bylo najednou. Totéž spočítá i pro jednotlivé sessions – kolik oken s Claudem máte otevřených naráz.
- **Seznam zajímavostí ke sdílení** – souhrn, nejsilnější měsíc, rekordy a extrémy jako hotové věty v první osobě, které můžete rovnou vykopírovat na LinkedIn nebo jinam.
- **Hříčky navíc**: kolikrát vám Claude řekl „máš pravdu“, co mu píšete nejčastěji, nejdelší prompt, který jste kdy napsali, a v kolik jste nejpozději šli od rozdělané práce spát.
- **Zajímavosti**: nejdelší den, nejdelší blok v kuse, nejdelší řada dnů po sobě, kolik dnů jste strávili kolika hodinami, které dny v týdnu a hodiny dne jsou nejsilnější.
- **Starší období dopočítá odhadem**, když se podrobné záznamy už smazaly, a takové údaje označí. Rozhodnutí, přerušení a zamítnutí se odhadnout nedají, u takového období je počet jen spodní hranice, nebo chybí.

## Proč zrovna tenhle

- **Souběžná okna se nesčítají.** Dvě hodiny ve dvou oknech naráz jsou pořád dvě hodiny, ne čtyři – a přechod z jednoho okna do druhého se nepočítá jako pauza.
- **Čekání na Clauda se počítá.** Když Claude dvacet minut pracuje a vy se díváte, je to čas strávený s ním.
- **Odchod se nepočítá.** Otázka, na kterou odpovíte až druhý den, ani příkaz, který přes noc čekal na vaše schválení, si nepřipíšou noc práce.
- **Commity se započtou, jen když vznikly při práci s Claudem**, ne ruční práce v repozitáři mimo něj.
- **Rozhodnutí se počítají přesně, nebo vůbec.** Počítá se jen odpověď v dialogu s variantami, zastavení a zamítnutí, které Claude Code zapíše, a zamítnutí několika souběžných akcí jedním klikem je jedno zamítnutí. Otázku v běžném textu odpovědi by šlo jen hádat, a odhad smíchaný s přesným počtem by znehodnotil oboje.
- **Odhad se kalibruje na vašich datech.** Kde podrobné záznamy chybí, změří si na dnech, kde jsou, jak moc se hrubý výpočet z promptů liší od plného, a tím poměrem ho opraví.
- **Přejmenovaný skill se počítá pod dnešním jménem**, zrušený nebo sloučený do jiného zůstává pod svým. Spuštění příkazem pozná i v nejstarších datech, spuštění Claudem jen tam, kde jsou podrobné záznamy, a jinde ho označí jako spodní hranici.
- **Projekt pozná i po přestěhování.** Worktrees a podprojekty jednoho klienta spojí do jednoho projektu, a když se projekt přestěhoval do jiné složky pod týmž jménem, starší čas mu připíše taky. Běhy Clauda, které si pustila jiná session, připíše projektu, ze kterého vzešly.
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
| červenec 2026 | ~15,2 | ~0,5 | ~1,5 | 10 z 31 |
| srpen 2026 | ~115,7 | ~3,7 | ~4,8 | 24 z 31 |
| září 2026 | ~272,7 | ~9,1 | ~9,1 | 30 z 30 |
| říjen 2026 | 198,8 | 6,4 | 6,9 | 29 z 31 |

| Období | Rozhodnutí | Přerušení | Zamítnutí | Zásahů na hodinu | Commity | Napsaných znaků | Ø znaků na prompt |
|---|---:|---:|---:|---:|---:|---:|---:|
| září 2026 | ≥3 236 | ≥97 | ≥150 | 13,0 | 2 433 | 677 929 | 223 |
| říjen 2026 | 1 877 | 61 | 78 | 10,1 | 1 834 | 414 011 | 176 |

| Skill | Celkem | Zadáno příkazem | Na pokyn slovy | Z jiného skillu nebo agenta |
|---|---:|---:|---:|---:|
| /end | ≥677 | 575 | ≥60 | ≥42 |
| /next | ≥149 | 116 | ≥30 | ≥3 |
| /merge | ≥101 | 71 | ≥14 | ≥16 |

### Zajímavosti

- V Claude Code mám za sebou zhruba 797,5 h za 221 dní (2. 4. 2026 – 8. 11. 2026): v průměru 3,6 h denně včetně víkendů, ve dnech s prací (138 z 221) 5,8 h.
- Nejsilnější měsíc: září 2026 – zhruba 272,7 h, tedy 9,1 h denně včetně víkendů.
- 47 dní v řadě bez jediného volného dne (31. 8. – 16. 10. 2026).
- 6 319+ rozhodnutí – odpovědí na Claudovy otázky s nabídnutými variantami, tedy 11,0 za hodinu práce.
- Nejčastější skilly podle počtu spuštění: /end (677+), /next (149+), /consistency (118+); z dnešních 37 skillů přišlo na řadu 36.
- V průměru mám naráz rozdělaných 1,4 projektu, víc projektů zároveň běží 37 % času a nejvíc jich naráz bylo 6 (12. 9. 2026, 11:39).
- Sessions mám za sebou 660; v průměru mi jich naráz běží 1,8, víc sessions zároveň běží 49 % času a nejvíc jich naráz bylo 8 (17. 9. 2026, 17:10).
- „Máš pravdu“ mi Claude řekl 339+ krát, zhruba jednou za 2,0 h práce.
- Nejčastější prompty: „ano“ (106×), „pokračuj“ (80×), „a“ (53×).

Tabulka skillů pokračuje všemi skilly, které se v období spustily, a za ní je stejně stavěná tabulka projektů s hodinami, aktivními dny a podílem času v Claude Code. Nad zajímavostmi je rozložení dnů podle počtu hodin, dnů v týdnu a hodin dne jako malé sloupcové grafy; každá tabulka končí součtovým řádkem.

## Co nedělá

- Neměří čas u klávesnice obecně, jen čas v Claude Code.
- Nefakturuje a nehledá zapomenutý čas pro klienta – na to je [`/invoicing`](../invoicing/README.md).
- Nepočítá, kolik vás to stojí peněz nebo tokenů.
- Nepočítá úhozy do klávesnice – jen napsaný text, takže opravy se nezapočtou a krátké vložení textu se od psaní nerozliší.
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
