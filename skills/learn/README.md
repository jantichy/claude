# /learn – nová znalost se vpraví do té staré, ne vedle ní

Máte vlastní knihovnu know-how – metodiky, standardy, postupy – a pořád do ní něco přibývá: přepis školení, na kterém jste hodinu něco vysvětlovali, článek, cizí dokumentace, poznámky z hovoru. Problém není ten materiál získat, ale dostat ho **dovnitř**. Založit vedle další soubor umí každý; tenhle skill zdroj rozebere na jednotlivé poznatky a zapracuje je na místa, kam věcně patří – doplní, prohloubí, opraví a když je potřeba, přestaví i strukturu textu kolem.

## Co umí

- **Vytěží zdroj do posledního detailu.** Nejen hlavní myšlenky, ale i prahy, čísla, výjimky, pořadí kroků a hlavně **důvody** – ty se ztrácejí první. Hotový seznam pak nechá zkontrolovat druhým, nezávislým průchodem, který hledá jen to, co v něm chybí. Počítá se s tím, že zdroj potom zmizí.
- **Pozná, co je skutečný rozpor.** Školení říká věci hruběji než metodika a rozebírá jen jednu variantu – to není chyba, to je jiná hloubka. Skill rozliší zjednodušení, zúžení, prohloubení a zastarání od případu, kdy dvě tvrzení opravdu nemohou platit obě.
- **Rozpory předloží po jednom.** Vysvětlí, v čem je spor, ocituje obě verze a nabídne hotová řešení včetně toho nejčastějšího: obojí platí, jen za jiných podmínek – tak se to zapíše.
- **Nesahá na to, na co se sahat nemá.** Návod a metodiku přepisuje volně. Profily, ceníky a texty psané ručně jen doplňuje. Doslovné přetisky, citace a datované záznamy nepřepisuje vůbec – pozná je podle toho, na co odpovídají, ne podle jména složky.
- **Celý plán ukáže předem.** Kolik poznatků, kam půjdou, co se přepíše, o čem se bude rozhodovat a co se nezapracuje. Teprve po odsouhlasení píše.
- **Přestavbu struktury si vyžádá zvlášť.** Zakládat, přesouvat nebo rušit soubory smí až poté, co vysvětlí, jak to má vypadat a proč se nová znalost do stávající struktury nevejde. Platí to i pro krajní případ: když pro znalost není v knihovně místo vůbec, navrhne založit celou novou tematickou oblast – necpe ji tam, kam nepatří.

## Proč zrovna tenhle

- Cílem není soubor navíc, ale **lepší knihovna**. Po doběhnutí není poznat, že něco přibylo zvenčí.
- Ptá se jen tam, kde opravdu neví. Falešný rozpor stojí rozhodnutí, které nemá co rozhodovat – a po třetím takovém nikdo odpovědi nečte.
- Na konci vypíše, kam šel který poznatek a co se nezapracovalo a proč. Rozdíl mezi „posoudil jsem a nepatří to tam“ a „přehlédl jsem to“ je vidět.
- Není vázaný na žádnou konkrétní knihovnu ani strukturu. Jak hluboko se smí sáhnout, odvozuje z povahy textu, ne z konfigurace, kterou byste museli udržovat.

## Jak se to používá

Zavolá se cestou ke zdroji a volným popisem, kam to má jít:

```
/learn vezmi ~/Desktop/skoleni.md a zakomponuj to do znalostí v analytics
```

Když cíl neurčíte přesně, skill si ho vybere sám a nechá si ho potvrdit. Když ho určíte, bere to jako svolení a už se neptá.

## Ukázka výstupu

```
## Plán zapracování – skoleni.md → analytics

Poznatků: 47 · nové 12 · doplnění 21 · prohloubení 8 · zastarání 2 · rozpory 3 · nezapracováno 1

Zásahy do obsahu
- consent.md › Souhlas před načtením – přestavba sekce, poznatky 3, 7–11
- events.md › Pojmenování – doplnění, poznatky 22, 24

K rozhodnutí
- 3 rozpory – proberu je po jednom v další fázi

Nezapracuje se
- poznatek 31 – specifikum klientova systému, není přenositelná znalost
```

## Co nedělá

- Nepřepisuje nahrávky – to je práce pro přepisovací skill, jehož výstup je sem typický vstup.
- Nepíše nové texty vaším hlasem; formuluje stylem cílové knihovny.
- Nedělá audit celé knihovny, dívá se jen na místa, kterých se zdroj dotkl.
- Nepřejmenovává termíny napříč knihovnou – jen na to upozorní.
- Nesahá na zdrojový soubor, zůstane, kde je.

## Jak si ho nainstalovat

Řekněte svému Claudovi:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/learn
> a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.

Nic dalšího doplňovat nemusíte – skill nemá žádné závislosti a nepotřebuje vědět, kde vaše knihovna leží. Řeknete mu to při každém zavolání.

---

### Požadavky a omezení

- Cílová knihovna by měla být **verzovaná v gitu**. Skill přepisuje existující texty a bez historie není kam se vrátit; před prací proto kontroluje, že v ní nemáte rozpracované změny.
- Zdroj musí být **text** – přepis, článek, poznámky. Nahrávku je potřeba nejdřív přepsat.
- Počítá s tím, že knihovna už nějakou strukturu má. Do prázdného adresáře nemá co zapracovávat.
- U velmi rozsáhlého zdroje běh trvá – vytěžení jde do detailu a úplnost se ověřuje opakovaně, dokud kontrola nevrátí prázdno.
