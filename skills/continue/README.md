# /continue – navázat na přerušenou práci hned, bez přehledu všeho ostatního

Když dlouhou session přerušíte skillem `/break`, zapíše rozdělanou práci do seznamu úkolů projektu. V nové session pak chcete jediné: pokračovat přesně tam, kde se skončilo. Tenhle skill zápis najde, přejde do adresáře, kde práce leží, krátce shrne, kde se stojí, a rovnou pokračuje. Hodí se každému, kdo práci přerušuje uprostřed a nechce v nové session čekat, než se sestaví přehled úplně všeho, co v projektu čeká.

## Co umí

- **Najde zápis přerušené práce kdekoliv v repozitáři** – i v jiné větvi, když každá větev leží ve vlastním adresáři.
- **Přejde tam, kde práce leží**, a řekne to.
- **Zkontroluje, co mělo předcházet** – chystali jste před pokračováním nějakou změnu? Zeptá se, jestli proběhla.
- **Hned pokračuje první akcí ze zápisu** – spustí skill, kterým se má navázat, nebo se pustí do první zbývající položky i s variantami a doporučením, jak je zapsané.
- **Je-li přerušení víc**, zeptá se, kterým začít. Když žádné není, řekne to a pošle vás na přehled všeho rozdělaného.

## Proč zrovna tenhle

- **Je rychlý.** Jeden dotaz do repozitáře, žádný sběr dat, žádná síť, žádné čtení pravidel – za pár vteřin pracuje.
- **Nic nedomýšlí.** Čím začít, rozhodla už předchozí session, když práci přerušovala; tenhle skill to jen provede.
- **Rozumí si s `/break`.** Oba stojí na stejném tvaru zápisu a test hlídá, aby se nerozešly.

## Jak se to používá

```
/continue
```

Zavolá se jako první věc v nové session po `/break`. `/break` ho sám doporučí na konci.

## Co nedělá

- Nic nezapisuje – rozdělanou práci ukládá `/break`.
- Nesestavuje přehled všeho, co v projektu čeká – na to je `/next`.
- Zápis po dokončení nemaže sám; kdy se smaže, říká zápis.

## Jak si ho nainstalovat

> Jdi na https://github.com/jantichy/claude/tree/main/skills/continue
> a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.

Bez skillu `/break` ze stejného repozitáře nemá na co navázat – nainstalujte si oba.

---

### Požadavky a omezení

- Claude Code, projekt v Gitu.
- Čte jen zápis ve tvaru, který píše `/break`; ručně psanou poznámku o rozdělané práci nenajde.
