# /scenarios – vytáhne z dřívějších konverzací scénáře, které se zapomněly zapsat

Když se nad projektem denně přemýšlí v Claudovi, rozhodne se v konverzacích spousta věcí o tom, jak se má systém v konkrétních situacích chovat. Většina z nich skončí v datovém modelu nebo v katalogu operací – ale seznam situací, proti kterému se ten model ověřuje, je nikdo nedopíše. Ten seznam pak vypadá úplně a není. Tenhle skill projde uzavřené konverzace a chybějící situace do něj doplní.

## Co umí

- Zjistí, které konverzace se od minule nevytěžily, a vypíše jejich rozsah dřív, než se do nich pustí. První běh vezme všechny, každý další jen ty nové.
- Na každou konverzaci pošle vlastní pomocníka, který ji přečte celou a vypíše z ní **každou** situaci – vyslovenou, naznačenou, jen předpokládanou i tu, o které padlo, že se řešit nebude.
- Ke každé situaci žádá doslovný úryvek z konverzace, takže se dá ověřit, že si ji nevymyslel.
- Hlásí, co se v konverzaci rozhodlo dvakrát a podruhé jinak – to je nejčastější způsob, jak se do dokumentace dostane tvrzení, které už neplatí.
- Vyfiltrovat, co je opravdu nové, a zařadit to na správné místo si nechává na sobě. Pomocníci dodávají úplnost, rozhodnutí zůstává nad nimi.
- Po zápisu si spočítá, o kolik seznam narostl, a ověří, že to sedí s tím, co zapsal.

## Proč zrovna tenhle

- **Hledá to, co chybí, ne to, co je.** Nekontroluje zapsané scénáře proti skutečnosti – hledá situace, ke kterým se nikdy žádný scénář nenapsal.
- **Nespoléhá na to, co má zrovna v paměti.** Čte konverzace ze souborů, takže se dostane i k tomu, co z kontextu dávno vypadlo.
- **Rozděluje práci tak, aby se chyba poznala levně.** Pomocník má za úkol nevynechat nic; posoudit, jestli je nález nový a jestli je to vůbec situace člověka, zůstává na jednom místě, kde se to dá ověřit proti dokumentaci.
- **Nevymýšlí.** Bez doslovného doložení se situace nevypisuje a co v konverzaci nezaznělo, se nedoplňuje.
- **Pamatuje si, kam došel.** Zapíše záznam o běhu, takže příště nejede odznova.

## Jak se to používá

```
/scenarios
```

Vypíše, kolik konverzací se bude vytěžovat, projde je, ukáže seznam toho, co chybí, a po zápisu řekne, o kolik scénářů seznam narostl.

## Co nedělá

- Nevytěžuje právě běžící konverzaci ani nezapisuje dohody a rozhodnutí – na to je úklid na konci práce.
- Nezakládá seznam scénářů; ten vzniká při psaní zadání. Tenhle skill do něj jen dopisuje.
- Nekontroluje, jestli si scénáře odporují s návrhem – to je práce auditu konzistence.
- Nerozhoduje o produktu. Narazí-li na situaci bez odpovědi, zapíše ji i s tím, že pokrytá není.

## Jak si ho nainstalovat

> Jdi na https://github.com/jantichy/claude/tree/main/skills/scenarios
> a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.

Skill počítá s tím, že projekt vede seznam scénářů v `docs/scenarios.md` a že v jeho úvodu stojí, co se do něj pouští a jak se zapisuje. Bez toho úvodu se nerozjede – nemá podle čeho rozhodnout, co je scénář.

---

### Požadavky a omezení

- Čte konverzace z `~/.claude/projects/`, takže vytěží jen to, co proběhlo na tomhle stroji.
- Rozesílá na každou konverzaci vlastního pomocníka. U desítek konverzací je to běh na desítky minut a odpovídající spotřeba.
- Zapisuje do jednoho souboru projektu. Změny patří na vlastní větev.
