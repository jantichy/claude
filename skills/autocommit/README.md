# /autocommit – ať se práce průběžně ukládá do Gitu sama

Zapíná pro jeden konkrétní projekt režim, ve kterém Claude po každém dokončeném celku sám commitne a – má-li projekt remote – rovnou pushne. Nemusíte to připomínat a nestane se, že by hodina práce zůstala viset v neuloženém stavu. Volí se to projekt po projektu, protože nikde nechcete totéž: v repozitáři, kde se iteruje rychle, to ušetří desítky pokynů denně, v repozitáři, kde se commituje uváženě, by to překáželo.

## Co umí

- **`/autocommit on`** – zapne autocommit pro projekt, ve kterém právě stojíte.
- **`/autocommit off`** – vypne ho a přepínač z instrukcí projektu zase odstraní.
- **`/autocommit status`** (nebo `/autocommit` bez ničeho) – řekne, jak na tom projekt je.
- Rozpozná i projekty, které mají instrukce ve složce `.claude/`, a nenechá se zmást uspořádáním s víc pracovními adresáři na větev.

## Proč zrovna tenhle

- **Přepínač je vidět přímo v projektu**, ne v nějaké skryté konfiguraci – kdokoli si otevře projekt, hned ví, jaký režim tam platí.
- **Stav se ukládá i zjišťuje týmž zápisem**, takže se nemůže rozejít to, co je nastavené, s tím, co se opravdu děje.
- **Nezapne se omylem globálně.** Popis mechanismu a přepínač jsou schválně dvě různé věci, takže se nestane, že by se autocommit choval jako zapnutý všude.
- **Když najde nastavení na nesprávném místě**, řekne to a nabídne srovnání – do instrukcí projektu tiše nesáhne. Vlastní sekci ve vašich globálních instrukcích si srovná sám a oznámí to.

## Jak se to používá

```
/autocommit on
```

Claude si najde kořen projektu, zapíše přepínač do jeho instrukcí a od té chvíle commituje po každém logickém celku.

## Co nedělá

- **Necommituje sám o sobě** – jen zapíná režim, ve kterém to dělá Claude při běžné práci.
- **Nenastavuje Git ani remote.** Není-li adresář repozitář, řekne to a skončí.
- **Nerozhoduje, kde se to hodí.** To je vaše volba; skill ji jen provede.

## Jak si ho nainstalovat

Nechte to na Claudovi. Otevřete si Claude Code a napište mu:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/autocommit a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.

Nic dalšího potřeba není. Aby přepínač něco znamenal, musí být pravidlo autocommitu i ve vašich globálních instrukcích – **skill si ho při prvním zapnutí doplní sám**, takže stačí spustit `/autocommit on`.

---

### Požadavky a omezení

Nic navíc. Funguje v jakémkoli gitovém projektu, na jakékoli platformě.
