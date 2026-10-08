# /break – přerušit rozdělanou práci tak, aby se v ní dalo pokračovat bez ztráty čehokoliv

Dlouhá session jednou narazí na strop: konverzace je tak velká, že se v ní Claude začne ztrácet, nebo se k práci prostě musíte vrátit jindy. Jenže rozdělaná práce žije hlavně v konverzaci – co se už udělalo, co zbývá, proč je který bod problém, jaké jsou možnosti a co byste doporučili. Nová session z toho bez pomoci neví nic. Tenhle skill to všechno zapíše do seznamu úkolů projektu tak, aby nová session navázala, jako by ji nikdo nepřerušil.

## Co umí

- **Přeruší jakoukoliv rozdělanou práci** – průchod nálezy z kontroly, rozpracovaný plán úkolů i práci, která žádným skillem neběží: návrh v půli, rozpravu se zbývajícími otázkami.
- **Zapíše ji na místo, které se čte první** – na začátek seznamu úkolů projektu, s větou, že tohle je rozdělané a pokračuje se v tom před vším ostatním, i s tím, ve které větvi a v jakém adresáři to leží.
- **U každého zbývajícího bodu zapíše všechno**: v čem je problém, kde to je, čím je to doložené, jaké jsou varianty a co z každé plyne, co byste doporučili a proč.
- **Zapíše i to, co se vyřešilo a co se ukázalo jako mylné**, ať se nová session nevrací k tomu, co už je hotové nebo vyvrácené.
- **Zachytí, co musí přijít dřív** – když třeba chystáte změnu, která část bodů zneplatní.
- **Zápis ověří** – přečte ho zpátky, spočítá body, pustí kontroly projektu a commitne.

## Proč zrovna tenhle

- **Nic se neparafrázuje.** Zkracování je přesně místo, kde se ztratí detail, kvůli kterému bod vznikl – a pozná se to až za týden.
- **Nová session nemusí nic domýšlet.** Ví, kde práce leží, co předchází a co doporučit, bez jediného dotazu.
- **Neohlásí hotovo s polovinou zápisu.** Počet zapsaných bodů se porovná se zbytkem práce.
- **Na konci řekne, kudy dál**: úklid session, vyčištění a nová session, ve které se na rozdělanou práci rovnou naváže.
- **Zápis má pevný tvar**, kterému rozumí `/continue`: každé přerušení pod vlastním nadpisem a na konci jedna jasná první akce.

## Jak se to používá

```
/break
```

Zavolá se kdykoliv uprostřed práce, nebo ho nabídne skill, kterému dochází místo. Na konci doporučí `/cleanup`, `/clear` a v nové session `/continue`, který na zápis rovnou naváže.

## Co nedělá

- Nezapisuje dohody a poznatky z celé session – na to je `/cleanup`, který jde hned po něm.
- Sám v práci nepokračuje – to v nové session udělá `/continue`.
- Zbytek práce nedodělává ani nerozhoduje, jen ho uloží.

## Jak si ho nainstalovat

> Jdi na https://github.com/jantichy/claude/tree/main/skills/break
> a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.

Počítá se seznamem úkolů v `docs/todo.md` a s navazujícími skilly `/cleanup` a `/continue` ze stejného repozitáře; bez nich zápis vznikne, ale nikdo na něj v nové session sám nenaváže.

---

### Požadavky a omezení

- Claude Code, projekt v Gitu.
- Kontroly projektu pouští jen ty, které má projekt zapsané ve svých instrukcích.
