# /next – s čím pokračovat, když se k projektu vrátíte

Otevřete novou session nad rozdělaným projektem a první otázka je pokaždé stejná: co nás čeká a do čeho se můžu pustit? Odpověď je rozházená po několika místech – v seznamu úkolů, v implementačním plánu, v rozpracovaných větvích, v necommitnutých změnách, v tom, který krok po poslední práci ještě neproběhl. Tenhle skill to všechno posbírá, seřadí podle toho, co je na stole nejvíc a co na čem závisí, a nejaktuálnější úkoly vám nabídne k výběru. Vyberete – a rovnou se jede. A skončila-li minulá session uprostřed rozdělané práce, nic nenabízí a rovnou v ní pokračuje.

## Co umí

1. **Naváže na přerušenou práci** – když ji `/end` při ukončení session zapsal, najde ten zápis i ve vedlejší větvi nebo v podprojektu, přejde tam, kde práce leží, krátce shrne, kde se stojí, a pokračuje tím, co zápis určil jako první krok. Nic dalšího přitom nesbírá, takže navázání trvá jen pár vteřin. Zbylo-li přerušených prací víc, zeptá se, kterou začít.
2. **Hned nahoře ukáže, na čem se už pracuje jinde** – projde rozdělané větve, pozná, kterého úkolu se týkají, a podívá se, jestli nad nimi zrovna běží Claude v jiném okně terminálu. Takové úkoly nenabízí, aby se nerozjely podruhé. **Větev, ve které se začalo a pak se na ni zapomnělo, naopak nabídne jako první** – a když k ní najde i starou konverzaci, řekne vám přesný příkaz, kterým ji obnovíte i s celým kontextem. Konverzaci, kterou máte otevřenou v jiném okně, nenabídne nikdy.
3. **Posbírá celou frontu práce** – úkoly a odložené body ze seznamu úkolů, zbytek implementačního plánu, tematická kola rozpracovaného návrhu, necommitnuté změny a krok životního cyklu, který po poslední práci chybí.
4. **Bere pořadí ze seznamu úkolů** – pořadí v něm je priorita a velikost má každý úkol zapsanou u sebe, takže je nemusí pokaždé odhadovat. Nejdřív dá zapomenuté a rozdělané věci, pak úkoly v pořadí seznamu; co na něco čeká, vypíše zvlášť i s tím, na co. Vypíše jen vrchol fronty a zbytek jako počet – celou frontu na požádání. Seznam úkolů ve starém tvaru přečte taky, jen pořadí a velikosti odhadne a nabídne jeho srovnání.
5. **U každého úkolu ukáže, jak je velký** – drobnost, práce na jednu session, nebo velký úkol –, a u těch nabízených řekne i to, v čem spočívá a čím se začíná.
6. **Tři až čtyři nejaktuálnější nabídne k výběru** – a pořád můžete napsat, že chcete jít úplně jinudy.
7. **Po výběru se do toho rovnou pustí** – má-li úkol vlastní skill, zavolá ho, jinak načte podklady a začne.
8. **Zúžení** – `/next review` nebo `/next DPH` ukáže jen to, co se tématu týká, a nabídku postaví i tehdy, když leží přerušená práce; ta je v ní pak první položkou. Tímhle způsobem si nabídku zbývajících kol návrhu bere i skill `/architect`.

## Proč zrovna tenhle

- **Místo dlouhého promptu jedno slovo** – a pokaždé stejně důkladně, ne podle toho, jak moc se vám zrovna chtělo psát.
- **Rychlý.** Všechno, co jde zjistit mechanicky – seznam úkolů, větve, běžící konverzace –, posbírá jeden skript za pár vteřin – a většinu z nich čeká na síť, když si stahuje aktuální stav větví. Claude pak jen posoudí a nabídne, místo aby se sám proklikával desítkami souborů a příkazů, a výpis drží na jednom řádku na úkol a jen na vrcholu fronty.
- **Dívá se i do gitu.** Neuložené změny a rozdělaná práce v seznamu úkolů nejsou, a přitom jsou to první věci, ke kterým je potřeba se vrátit. A když souběžně běží víc sessions v různých větvích, nenabídne vám úkol, na kterém už dělá jiná.
- **Priorita se rozhoduje jednou, při zápisu úkolu, ne při každém spuštění.** Proto je výpis rychlý i u dlouhé fronty a pořadí se mezi dvěma běhy nemění podle nálady. Závislosti bere jen ze zápisu; tušenou závislost řekne jako domněnku.
- **U každého úkolu velikost.** Když máte hodinu, vidíte hned, co se do ní vejde.
- **Nemíchá rozhodnutou práci s nápady.** Nezávazné nápady ukáže až tehdy, když skutečné úkoly dojdou.
- **Nic nepřepisuje.** Jen čte; zastaralý seznam úkolů ohlásí, ale neuklízí.

## Jak se to používá

```
/next           # naváže na přerušenou práci, jinak celá fronta a nabídka
/next review    # jen to, co se týká revize
```

## Ukázka výstupu

Že kolo o fakturaci navazuje na export faktur, je domněnka z textu úkolu, výslovně zapsané to není.

**Pracuje se jinde:** Kolo o upomínkách (`architect-reminders`, běží v jiném okně)

**Čeká na něco:** Kolo o fakturaci (na kolo o DPH) · Napojení na účetní systém (na odpověď podpory)

**S čím můžeme pokračovat**

1. ◐ Export faktur do účetnictví (opuštěná větev `invoice-export`)
2. ◐ Validace formuláře objednávky (rozdělané tady)
3. ◐ Kolo o DPH
4. ○ Přejmenovat „rezervace“ na „objednávka“ v administraci

+ 54 dalších v seznamu úkolů – celou frontu vypíšu na požádání

○ drobnost · ◐ střední · ● velký

Pod tím hned nabídka prvních položek k výběru, u každé jednou větou, co se bude dělat a čím se začne.

## Co nedělá

- **Nerozkládá velký úkol na menší** – od toho je implementační plán.
- **Neuklízí seznam úkolů** a nic do něj nezapisuje – ani zápis přerušené práce nemaže; ten zmizí, až se práce dodělá.
- **Nevybírá za vás.** Doporučí, ale začne až po vašem výběru.
- **Nesahá do cizích větví** – práci rozběhnutou jinde jen ohlásí.

## Jak si ho nainstalovat

Je to snadné, zadejte do svého Claude Code tenhle prompt:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/next a nainstaluj mi ten skill k sobě do `~/.claude/skills/` – celý adresář i s podadresáři. Stáhni k němu z téhož repozitáře na odpovídající místo pod `~/.claude/` i sdílené soubory ze `skills/` a `standards/`, na které jeho soubory odkazují, a definice typů subagentů, které pouští, z `agents/` do `~/.claude/agents/`. Co už u sebe mám, nepřepisuj a ukaž mi rozdíl. Odkazuje-li na jiný skill, zeptej se mě, jestli ho chci taky. Odkazy na soubory, které v repozitáři nejsou, mi vypiš a u každého se zeptej, jestli ho napojit na můj vlastní soubor, nebo odkaz smazat. Zeptej se mě, kde vedu úkoly, nápady a plán, a cesty ve skillu tomu přizpůsob. Nakonec mi řekni, co musím doplnit sám.

Skill počítá s mojí strukturou projektu – seznam úkolů, nápadů a hotové práce v `docs/`, implementační plán a kola návrhu ze skillu `/architect`. Jádro – sběr, řazení a nabídka – na tom nezávisí.

---

### Požadavky a omezení

Projekt v gitu – operativní projekt s vlastními dokumenty i bez něj – a macOS nebo Linux (zjišťování běžících session čte procesy a vnitřní záznamy Claude Code; kde to nejde nebo je výsledek nejistý, skill rozdělané větve bere jako obsazené a řekne to). Bez seznamu úkolů nebo plánu skill najde jen rozdělanou práci v gitu; nemá-li ani tu, řekne, že vybírat není z čeho.
