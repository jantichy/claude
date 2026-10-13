# /explain – když Claude mluví v náznacích, řekne to znovu a srozumitelně

Při dlouhé práci si Claude nasbírá kontext, který vy nemáte: přečetl soubory, viděl nálezy, něco si promyslel. A pak se zeptá „jak bys vyřešil rozpor z kapitoly 13?“ nebo „volíš variantu A, nebo B?“, aniž by řekl, o jaký rozpor jde a co ty varianty jsou. Tenhle skill je zkratka pro „nerozumím, vysvětli mi to“. Claude tu věc podá znovu, krátce a na jednom konkrétním příběhu, a otázku pak položí znovu. Hodí se hlavně při procházení nálezů z revizí a oponentur, ale funguje na cokoliv, čemu jste nerozuměli.

## Co umí

- **Vysvětlí poslední otázku nebo tvrzení**, nebo tu věc, kterou mu napíšete za příkaz.
- **Řekne, čeho se to týká, jak je to dnes a proč to nestačí** – ne jen to, na co se ptá.
- **Ukáže to na jednom konkrétním případu** se jmény, daty a částkami z vašeho projektu a na témže případu přehraje každou variantu, takže jdou porovnat.
- **Rozvede zkratky a interní výrazy** a místo odkazů na věci, které jste neviděli, řekne jejich obsah.
- **Přizná, když předtím něco přehnal** – fakta si před vysvětlením ověří ve zdroji.
- **Pak otázku položí znovu** jako výběr z možností, tentokrát srozumitelný.

## Proč zrovna tenhle

- **Krátké.** Jeden až dva odstavce, ne přednáška.
- **Konkrétní.** Příběh místo obecné formulace – z něj je hned vidět, co která varianta znamená v praxi.
- **Vysvětlení je opravdu napsané.** Nestane se, že Claude tvrdí „vysvětlil jsem“, ale vysvětlení proběhlo jen v jeho hlavě.
- **Jeden příkaz** místo psaní „nechápu, mluvíš moc stručně, co je to…“ pokaždé znovu.

## Jak se to používá

```
/explain
/explain variantu B
```

Stačí i napsat „nechápu, vysvětli mi to“.

## Co nedělá

- Nehledá nové problémy ani nepřehodnocuje nálezy – jen zpřístupní to, co už padlo.
- Nerozhoduje za vás; doporučí, ale otázku vrátí.
- Nic nezapisuje do souborů.

## Jak si ho nainstalovat

> Jdi na https://github.com/jantichy/claude/tree/main/skills/explain
> a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.

Nic dalšího nepotřebuje.

---

### Požadavky a omezení

- Claude Code.
- Pracuje s tím, co padlo v konverzaci a co si může dohledat v souborech projektu; co se nikde neříká, nevysvětlí – řekne, co chybí.
