# /next – s čím pokračovat, když se k projektu vrátíte

Otevřete novou session nad rozdělaným projektem a první otázka je pokaždé stejná: co nás čeká a do čeho se můžu pustit? Odpověď je rozházená po několika místech – v seznamu úkolů, v implementačním plánu, v rozpracovaných větvích, v necommitnutých změnách, v tom, který krok po poslední práci ještě neproběhl. Tenhle skill to všechno posbírá, seřadí podle toho, co je na stole nejvíc a co na čem závisí, a nejaktuálnější úkoly vám nabídne k výběru. Vyberete – a rovnou se jede.

## Co umí

1. **Hned nahoře ukáže, na čem se už pracuje jinde** – projde rozdělané větve, pozná, kterého úkolu se týkají, a podívá se, jestli nad nimi zrovna běží Claude v jiném okně terminálu. Takové úkoly nenabízí, aby se nerozjely podruhé. **Větev, ve které se začalo a pak se na ni zapomnělo, naopak nabídne jako první** – a když k ní najde i starou konverzaci, řekne vám přesný příkaz, kterým ji obnovíte i s celým kontextem. Konverzaci, kterou máte otevřenou v jiném okně, nenabídne nikdy.
2. **Posbírá celou frontu práce** – úkoly a odložené body ze seznamu úkolů, zbytek implementačního plánu, tematická kola rozpracovaného návrhu, necommitnuté změny a krok životního cyklu, který po poslední práci chybí.
3. **Seřadí ji podle závislostí**: nejdřív zapomenuté a rozdělané věci, pak to, na co nic nečeká, a mezi tím hlavně úkoly, které odblokují nejvíc dalších. Co na něco čeká, vypíše zvlášť i s tím, na co.
4. **U každého úkolu řekne, v čem spočívá**, jestli je to drobnost, práce na jednu session, nebo velký úkol, a čím se začíná.
5. **Tři až čtyři nejaktuálnější nabídne k výběru** – a pořád můžete napsat, že chcete jít úplně jinudy.
6. **Po výběru se do toho rovnou pustí** – má-li úkol vlastní skill, zavolá ho, jinak načte podklady a začne.
7. **Zúžení** – `/next review` nebo `/next DPH` ukáže jen to, co se tématu týká. Tímhle způsobem si nabídku zbývajících kol návrhu bere i skill `/specify`.

## Proč zrovna tenhle

- **Místo dlouhého promptu jedno slovo** – a pokaždé stejně důkladně, ne podle toho, jak moc se vám zrovna chtělo psát.
- **Rychlý.** Všechno, co jde zjistit mechanicky – seznam úkolů, větve, běžící konverzace –, posbírá jeden skript zhruba za vteřinu. Claude pak jen posoudí a nabídne, místo aby se sám proklikával desítkami souborů a příkazů, a výpis drží na jednom řádku na úkol.
- **Dívá se i do gitu.** Neuložené změny a rozdělaná práce v seznamu úkolů nejsou, a přitom jsou to první věci, ke kterým je potřeba se vrátit. A když souběžně běží víc sessions v různých větvích, nenabídne vám úkol, na kterém už dělá jiná.
- **Pořadí podle závislostí, ne podle toho, co je v seznamu nahoře.** Závislosti bere jen ze zápisu; tušenou závislost řekne jako domněnku.
- **U každého úkolu velikost.** Když máte hodinu, vidíte hned, co se do ní vejde.
- **Nemíchá rozhodnutou práci s nápady.** Nezávazné nápady ukáže až tehdy, když skutečné úkoly dojdou.
- **Nic nepřepisuje.** Jen čte; zastaralý seznam úkolů ohlásí, ale neuklízí.

## Jak se to používá

```
/next           # celá fronta a nabídka
/next review    # jen to, co se týká revize
```

## Ukázka výstupu

**Už se na tom pracuje jinde**
- **Kolo o upomínkách** – větev `specify-upominky`, běží v ní session ve vedlejším okně; rozhodnuto, čeká zápis před sloučením

**Opuštěné**
1. **Export faktur do účetnictví** · střední – větev `export-faktur`, nikdo na ní nepracuje; zbývá napojit formát a testy, naposledy předevčírem. · začíná se: `/resume` té konverzace

**Rozdělané tady**
2. **Validace formuláře objednávky** · střední – dopsat kontroly vstupu a testy, ve větvi zbývají tři úkoly z plánu. · začíná se: `/implement`

**Připravené**
3. **Kolo o DPH** · střední – rozhodnout sazby, zaokrouhlení a doklady pro zahraniční zákazníky. Odblokuje: kolo o fakturaci. · začíná se: `/specify round DPH`
4. **Přejmenovat „rezervace“ na „objednávka“ v administraci** · drobnost – sjednotit termín v rozhraní a dokumentaci. · začíná se: `/replace`

**Čekají na něco**
5. **Kolo o fakturaci** – čeká na: kolo o DPH

## Co nedělá

- **Nerozkládá velký úkol na menší** – od toho je implementační plán.
- **Neuklízí seznam úkolů** a nic do něj nezapisuje.
- **Nevybírá za vás.** Doporučí, ale začne až po vašem výběru.
- **Nesahá do cizích větví** – práci rozběhnutou jinde jen ohlásí.

## Jak si ho nainstalovat

Nechte to na Claudovi. Otevřete si Claude Code a napište mu:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/next a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.

Skill počítá s mojí strukturou projektu – seznam úkolů, nápadů a hotové práce v `docs/`, implementační plán a kola návrhu ze skillu `/specify`. **Máte-li úkoly jinde, řekněte Claudovi, ať skillu cesty upraví**; jádro – sběr, řazení a nabídka – na tom nezávisí.

---

### Požadavky a omezení

Projekt v gitu a macOS nebo Linux (zjišťování běžících session čte procesy a vnitřní záznamy Claude Code; kde to nejde nebo je výsledek nejistý, skill rozdělané větve bere jako obsazené a řekne to). Bez seznamu úkolů nebo plánu skill najde jen rozdělanou práci v gitu; nemá-li ani tu, řekne, že vybírat není z čeho.
