# /autocommit – ať se práce průběžně ukládá do Gitu sama

Zapíná pro jeden konkrétní projekt režim, ve kterém Claude po každém dokončeném celku sám commitne a – má-li projekt remote – rovnou pushne. Nemusíte to připomínat a nestane se, že by hodina práce zůstala viset v neuloženém stavu. Volí se to projekt po projektu, protože nikde nechcete totéž: v repozitáři, kde se iteruje rychle, to ušetří desítky pokynů denně, v repozitáři, kde se commituje uváženě, by to překáželo.

## Co umí

- **`/autocommit enable`** – zapne autocommit pro projekt, ve kterém právě stojíte.
- **`/autocommit disable`** – vypne ho a přepínač z instrukcí projektu zase odstraní.
- **`/autocommit status`** (nebo `/autocommit` bez ničeho) – řekne, jak na tom projekt je.
- Narazí-li na zápis ve starším tvaru, srovná ho na dnešní a řekne to.
- Rozpozná i projekty, které mají instrukce ve složce `.claude/`, a nenechá se zmást uspořádáním, kde má každá větev vlastní pracovní adresář.

## Proč zrovna tenhle

- **Přepínač je vidět přímo v projektu**, ne v nějaké skryté konfiguraci – kdokoli si otevře projekt, hned ví, jaký režim tam platí.
- **Stav se ukládá i zjišťuje týmž zápisem**, takže se nemůže rozejít to, co je nastavené, s tím, co se opravdu děje.
- **Nezapne se omylem globálně.** Pravidla se do projektu vkládají spolu s přepínačem, takže platí jen tam, kde jste je zapnuli – ne všude.
- **Když najde nastavení na nesprávném místě**, srovná ho a řekne to – jinak by v projektu zůstal přepínač, který nic nespíná. Zbytku vašich instrukcí se nedotkne.

## Jak se to používá

```
/autocommit enable
```

Claude si najde kořen projektu, zapíše přepínač do jeho instrukcí a od té chvíle commituje po každém logickém celku.

## Co nedělá

- **Necommituje sám o sobě** – jen zapíná režim, ve kterém to dělá Claude při běžné práci.
- **Nenastavuje Git ani remote** a nezakládá projekt. Není-li adresář repozitář, řekne to a skončí; celé nastavení projektu vede `/project`, který se na autocommit ptá jako na jeden ze svých kroků.
- **Nerozhoduje, kde se to hodí.** To je vaše volba; skill ji jen provede.

## Jak si ho nainstalovat

Je to snadné, zadejte do svého Claude Code tenhle prompt:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/autocommit a nainstaluj mi ten skill k sobě do `~/.claude/skills/` – celý adresář i s podadresáři. Stáhni k němu z téhož repozitáře na odpovídající místo pod `~/.claude/` i sdílené soubory ze `skills/` a `standards/`, na které jeho soubory odkazují, a definice typů subagentů, které pouští, z `agents/` do `~/.claude/agents/`. Co už u sebe mám, nepřepisuj a ukaž mi rozdíl. Odkazuje-li na jiný skill, zeptej se mě, jestli ho chci taky. Odkazy na soubory, které v repozitáři nejsou, mi vypiš a u každého se zeptej, jestli ho napojit na můj vlastní soubor, nebo odkaz smazat. Nakonec mi řekni, co musím doplnit sám.

Pravidla jsou součástí skillu a do projektu si je vloží sám při prvním zapnutí.

---

### Požadavky a omezení

Nic navíc. Funguje v jakémkoli gitovém projektu, na jakékoli platformě.
