# /report – data do jednoho souboru, který jde poslat komukoliv

Z exportu z Google Analytics, CSV, JSON nebo výsledku databázového dotazu udělá **jeden jediný soubor HTML** – s grafy, komentářem a metodikou. Otevře se dvojklikem z disku, funguje bez internetu a bez serveru, jde ho poslat mailem, nahrát na web nebo vytisknout do PDF. A hlavně odpovídá na otázku, kvůli které vznikl; není to přehlídka grafů, ze které si nikdo nic neodnese.

## Co umí

1. **Zeptá se nejdřív na to podstatné** – na jakou otázku má report odpovědět, kdo ho bude číst, za jaké období a **na co se to vlastně počítá** (na řádky, uživatele, návštěvy, dny). Právě tahle poslední otázka je nejčastější zdroj chybných čísel.
2. **Nechá si odsouhlasit osnovu**, než začne stavět. Přestavovat hotový report je dražší než přepsat osnovu.
3. **Počítá skriptem, který zůstane v projektu.** Report se skoro vždycky přegeneruje – s novými daty, opravenou metodikou, dalším obdobím.
4. **Zkontroluje si čísla** – sedí součty, sedí poměry, odpovídá celek zdroji. Když ne, hledá příčinu; nezaokrouhlí to potichu.
5. **Napíše komentář, který interpretuje.** „Návštěvnost vzrostla pětkrát" je popisek grafu; „nárůst je organický z vyhledávání značky, ne z odkazů v médiích" je komentář.
6. **Metodika a limity dat jsou součástí reportu**, ne dodatek. Čemu se nedá věřit a proč, se přiznává.
7. **Na požádání dvě verze** – podrobnou a stručnou, přičemž stručná je samostatně napsaný text, ne zkrácená kopie.
8. **Ověří hotový soubor v prohlížeči** – diakritiku, grafy, konzoli, tisk, chování na úzkém okně – a namátkou přepočítá pár čísel zpátky proti zdroji.

## Proč zrovna tenhle

- **Opravdu jeden soubor.** Žádné externí knihovny, žádné načítání ze sítě. Report funguje offline i za pět let, až ta knihovna zmizí z internetu.
- **Datum vygenerování je zapsané natvrdo.** Ne datum, kdy si to příjemce otevřel – to by zastíralo stáří dat.
- **Zdroj dat a období jsou vidět v reportu.** Kdo se na to podívá za půl roku, pozná, odkud čísla jsou.
- **Ven jdou jen souhrny, nikdy původní řádky.** Osobní údaje v reportu nemají co dělat, a segment o třech lidech je taky osobní údaj.
- **Před předáním projde hotový soubor kontrolou na úniky.** Nejen na osobní údaje, ale i na přístupové – ty se do reportu nedostanou vědomě, ale protečou samy z výpočetního skriptu, z konfigurace nebo ze screenshotu administrace. Když se něco najde, skill se zastaví a řekne i to, že údaj je nejspíš i ve zdrojích a je potřeba ho vyměnit.
- **Počítá s tiskem.** Co je jen v bublině nad grafem, v PDF neexistuje – tak to tam podstatné není.
- **Nezakrývá nejistotu.** Radši „na tohle jsou data příliš malá" než opatrná formulace, která vypadá jako závěr.

## Jak se to používá

```
/report
```

Skill se doptá na otázku, publikum, období a jednotku, předloží osnovu, spočítá to skriptem, postaví soubor a ověří ho v prohlížeči.

## Ukázka výstupu

Struktura, kterou report dostane:

```
Záhlaví     název, období, zdroj dat, datum vygenerování
Shrnutí     3–5 vět, co z toho plyne – čte se první a často jako jediné
Sekce 1..N  graf nebo tabulka + komentář, co v tom vidím
Metodika    jak se počítalo, co se vyloučilo, jak se normalizovalo
Limity dat  čemu se nedá věřit a proč
```

## Co nedělá

- **Nepouští ven neagregovaná data.**
- **Nepočítá od oka** – výpočet je vždycky skript, který jde zopakovat a zkontrolovat.
- **Neinterpretuje za hranicí dat.** Co z čísel neplyne, do komentáře nepatří.
- **Nedopočítává, co neví.** Chybějící den je v grafu mezera, nebo označený odhad – nikdy tiše dopsaná hodnota.

## Jak si ho nainstalovat

Nechte to na Claudovi. Otevřete si Claude Code a napište mu:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/report a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.

Skill si načítá **moje soukromé standardy** pro českou typografii, pro webové rozhraní a pro analytiku – ty v tomhle repozitáři nejsou. Bez nich funguje, jen si nepohlídá tonalitu a typografii; **řekněte Claudovi, ať ty odkazy nahradí vašimi, nebo je smaže**.

---

### Požadavky a omezení

Python na výpočet a prohlížeč Chrome na ověření hotového souboru. Vkládá-li se do reportu knihovna, roste tím velikost souboru – skill řekne o kolik.
