# /download – složku z Google Drive do fronty ke stažení jedním příkazem

Velké soubory, třeba záznamy přednášek, se nestahují v prohlížeči. Stahuje je můj vlastní nástroj clockwork na pozadí: po jednom, s navázáním po výpadku sítě a jen tehdy, když to počítači nevadí. Clockwork bere práci ze seznamu adres v souboru `~/Downloads/downloads.md`. Tenhle skill ten seznam plní. Dáte mu odkaz na složku na Google Drive a on z ní udělá řádek pro každý soubor, i z podsložek, pod správným nadpisem a bez toho, co už ve frontě je. Hodí se každému, kdo stahuje velké dávky souborů a nechce kvůli tomu nechat otevřený prohlížeč.

## Co umí

- **Rozbalí složku na Google Drive** na jednotlivé soubory, i s podsložkami, a zachová jejich strukturu v `~/Downloads`.
- **Určí cílovou složku**: tu, kterou mu řeknete, jinak podle jména složky na Drive. Samostatný soubor jde rovnou do `~/Downloads`.
- **Nic nezařadí dvakrát.** Adresu, která už v seznamu stojí, čekající i staženou, přeskočí a řekne, kde ji našel. Pozná ji i v jiném tvaru odkazu.
- **Vynechá, co stáhnout nejde** – dokumenty Google a složky jinde než na Drive – a vypíše je, ať víte, co zbývá udělat ručně.
- **Přijme i obyčejnou webovou adresu** souboru a na požádání i jméno, pod kterým se má uložit.

## Proč zrovna tenhle

- **Složka se stovkou souborů je jeden příkaz**, ne stovka zkopírovaných odkazů.
- **Seznam se nerozbije.** Zápis do souboru, který zrovna čte a odškrtává jiný program, se dělá tak, aby ten program nikdy neviděl napůl zapsaný soubor.
- **Nestáhne se nic podruhé** jen proto, že jste tutéž složku vložili dvakrát.
- **Pořadí sedí.** Soubory jdou do fronty seřazené podle jména tak, jak je čte člověk (2 před 10).

## Jak se to používá

```
/download https://drive.google.com/drive/folders/… Kosmologie 2024
```

Skill složku rozbalí, zapíše řádky do seznamu a vypíše, kolik čeho přidal a co přeskočil. Stahování pak běží samo.

## Ukázka výstupu

**Do stahování přidáno 14 položek** – Kosmologie 2024: 12, Kosmologie 2024/Cvičení: 2

**Přeskočeno**
- 01 Úvod do kosmologie.mp4 – už v seznamu ve složce Kosmologie 2024, staženo
- Osnova kurzu – dokument Google, stáhněte ho exportem ručně

## Co nedělá

- Sám nic nestahuje – to dělá program, který seznam odbavuje.
- Stažené soubory nezařazuje dál; na to je [`/depot`](../depot/README.md).
- Nepřejmenovává soubory podle obsahu; jméno dá jen tam, kde mu ho řeknete.
- Nerozbaluje složky na Dropboxu, OneDrivu ani jinde mimo Google Drive.

## Jak si ho nainstalovat

Je to snadné, zadejte do svého Claude Code tenhle prompt:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/download a nainstaluj mi ten skill k sobě do `~/.claude/skills/` – celý adresář i s podadresáři. Stáhni k němu z téhož repozitáře na odpovídající místo pod `~/.claude/` i sdílené soubory ze `skills/` a `standards/`, na které jeho soubory odkazují, a definice typů subagentů, které pouští, z `agents/` do `~/.claude/agents/`. Co už u sebe mám, nepřepisuj a ukaž mi rozdíl. Odkazuje-li na jiný skill, zeptej se mě, jestli ho chci taky. Odkazy na soubory, které v repozitáři nejsou, mi vypiš a u každého se zeptej, jestli ho napojit na můj vlastní soubor, nebo odkaz smazat. Ověř, že mám v Claude Code připojený konektor Google Drive, a když ne, řekni mi, jak ho připojit. Zeptej se mě, čím seznam ke stažení odbavuji, a cestu k seznamu ve skillu uprav podle toho. Nakonec mi řekni, co musím doplnit sám.

Clockwork, který seznam stahuje, je soukromý nástroj a v repozitáři není. Bez něj skill seznam naplní, ale nikdo ho neodbaví – potřebujete vlastní stahovač, který čte tentýž formát; popis formátu je v adresáři skillu.

---

### Požadavky a omezení

- Claude Code s konektorem Google Drive (jen pro odkazy na Drive) a Python 3.10 a novější.
- Program, který seznam `~/Downloads/downloads.md` odbavuje; skill sám nestahuje.
- Vidí jen to, k čemu má přístup účet připojený ke konektoru, Sdílené disky včetně; složku jiného účtu je potřeba nejdřív nasdílet.
- Velkou složku (nad 50 souborů) zapíše až po potvrzení.
