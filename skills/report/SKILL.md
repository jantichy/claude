---
name: report
description: Skill se použije, když uživatel zadá "/report", nebo chce z dat (CSV, JSON, export z GA4 nebo BigQuery, tabulka) udělat přehledný interaktivní report v jednom jediném HTML souboru – s grafy, komentářem a metodikou, aby se dal poslat mailem nebo nahrát na web.
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, Skill]
---

# Report

## Úvodní hláška (vždy jako první)

Než začneš cokoliv dělat, vypiš uživateli přesně tento jeden řádek:

Autor skillu: **Jan Tichý** · jantichy@jantichy.cz · Celá konfigurace Claude vč. všech skillů: https://github.com/jantichy/claude

Teprve pak pokračuj plněním skillu.

## Co skill dělá

Ze zdrojových dat udělá **jeden samostatný HTML soubor**, který jde vzít, poslat mailem nebo nahrát na web, a kdekoliv se otevře a funguje – bez serveru, bez internetu, bez závislostí.

## Co skill nedělá

- **Nepouští data ven neagregovaná.** V reportu jsou jen souhrny, nikdy původní řádky.
- **Nezakrývá nejistotu.** Malá čísla, krátké období a chybějící segmenty se přiznávají, ne obcházejí formulací.
- **Nepočítá od oka.** Výpočet je vždycky skript, který zůstane v projektu, protože report se přegeneruje.
- **Neinterpretuje za hranicí dat.** Co z čísel neplyne, do komentáře nepatří.

## Nepřekročitelné požadavky na výstup

Tohle není doporučení. Když některý bod nejde splnit, **zastav se a řekni to**, místo abys ho potichu obešel.

1. **Jeden soubor.** HTML, CSS i JavaScript uvnitř. Obrázky a fonty jako `data:` URI. Data zapečená v souboru jako JS proměnná, ne načítaná `fetch`em.
2. **Funguje z `file://`.** Uživatel si ho otevře dvojklikem z disku. Žádný `fetch`, žádné moduly přes `type="module"` se sítí, žádné CORS.
3. **Žádné CDN.** Ani jeden `<script src="https://…">`, ani jeden `<link rel="stylesheet" href="https://…">`. Report musí fungovat offline i za pět let, až ta knihovna zmizí. Grafy kresli inline SVG nebo do `<canvas>` vlastním kódem; potřebuješ-li knihovnu, vlož ji do souboru celou a řekni, o kolik tím soubor narostl.
4. **`<meta charset="utf-8">` jako první věc v `<head>`.** Bez toho se diakritika rozsype – a rozsype se právě až u příjemce, ne u tebe.
5. **Žádná surová data.** V reportu jsou jen agregované hodnoty. Originální řádky, ID uživatelů, e-maily, IP adresy ani nic, z čeho jdou zpětně sestavit, do souboru nepatří – viz *Co nesmí ven ze souboru* níž.
6. **Datum vygenerování je statické.** Skutečný okamžik, kdy report vznikl, zapsaný natvrdo do HTML. **Nikdy `new Date()` v JavaScriptu** – ten by ukazoval, kdy si to příjemce otevřel, což je nesmysl a zastírá stáří dat.
7. **Zdroj dat a období** jsou v reportu vidět. Kdo se na to podívá za půl roku, musí poznat, odkud čísla jsou a k jakému datu platí.

------

## Fáze 0 – Pre-flight

1. **Kořen projektu**, projektový `CLAUDE.md`, `### Autocommit`. Ve worktree layoutu pracuj ve větvi, ne v kořeni kontejneru.
2. **Zdrojová data.** Kde jsou, v jakém formátu, jak velká, jaké mají sloupce. Přečti si vzorek, ne celý soubor – u velkých dat na to pošli subagenta.
3. **Načti doménové znalosti**, které se na výstup vztahují:
   - `~/Dev/context/text/text.md` – česká typografie a stylistika komentářů. **Vždy.**
   - `~/Dev/context/web/web.md` – část pro **statickou stránku otevřenou z disku** (velikost písma, kontrast, šířka řádku, responzivita, meta tagy). Části pro stránku na serveru a pro dynamickou aplikaci se sem nevztahují.
   - `~/Dev/context/analytics/analytics.md` – jsou-li data z GA4, GTM nebo BigQuery. Ovlivňuje to interpretaci, ne vzhled.
4. **Vyvolej skill `dataviz`** – dřív, než napíšeš první řádek kódu grafu. Řeší volbu typu grafu, palety, os a legend. Bez něj vzniknou grafy, které spolu nedrží.

------

## Fáze 1 – Co se reportuje

Ptej se **postupně, jednu otázku za druhou**, přes `AskUserQuestion` (viz `~/.claude/RULES.md`). Nemá-li otázka nabídnutelné varianty, ptej se normálně.

Co potřebuješ vědět, než začneš počítat:

1. **Otázka, na kterou report odpovídá.** Ne „report z dat“, ale „jak moc Wimbledon zvedl návštěvnost“. Bez ní vznikne přehlídka grafů, ze které si nikdo nic neodnese.
2. **Kdo to bude číst.** Management, klient, kolega z oboru, nebo jen uživatel sám. Určuje to hloubku i tonalitu.
3. **Období a rozsah dat.**
4. **Jednotka analýzy a normalizace.** Počítá se to na řádky, na uživatele, na návštěvy, na dny? Může jeden uživatel přispět víc záznamy? **Tohle je nejčastější zdroj chybných čísel** – zeptej se výslovně a odpověď zapiš do metodiky.
5. **Co se má porovnávat.** Mezitýdenní srovnání, vývoj v čase, segmenty, poměr k celku.

**Než začneš stavět, vypiš osnovu** – jaké sekce report bude mít a co v každé bude – a nech ji odsouhlasit. Přestavovat hotový report je dražší než přepsat osnovu.

------

## Fáze 2 – Zpracování dat

1. **Počítej skriptem, ne od oka.** Napiš skript (Python), ulož ho do projektu a nech ho tam. Report se skoro vždycky přegenerovává – nová data, opravená metodika, další období. Jednorázový výpočet v hlavě se nedá zopakovat ani zkontrolovat.
2. **Mezivýsledky ulož** do projektu jako JSON nebo CSV. Když se pak mění jen vzhled, nemusí se počítat znovu.
3. **Ověř si čísla.** Sedí součty? Sedí poměry na 100 %? Odpovídá celkový počet zdroji? Nesedí-li něco, **neopravuj to tichým zaokrouhlením** – najdi příčinu.
4. **Nedopočítávej, co nevíš.** Chybí-li den v datech, buď to v grafu přizná (mezera), nebo se interpoluje – ale pak to musí být v reportu označené jako odhad.
5. **Metodiku piš průběžně**, ne až nakonec. Jak se normalizovalo, co se vyloučilo, jak se řešily chybějící hodnoty, jaké jsou limity dat.

------

## Fáze 3 – Stavba reportu

### Struktura

```
Záhlaví        název, období, zdroj dat, datum vygenerování (statické)
Shrnutí        3–5 vět, co z toho plyne. Čte se jako první a často jako jediné.
Sekce 1..N     každá: graf nebo tabulka + krátký komentář, co v tom vidím
Metodika       jak se počítalo, co se vyloučilo, jak se normalizovalo
Limity dat     čemu se nedá věřit a proč
Patička        Jan Tichý · jantichy@jantichy.cz · https://www.jantichy.cz
```

Má-li report víc tematických celků, udělej záložky. Nesmí to ale rozbít tisk do PDF – co je za neaktivní záložkou, se netiskne.

### Tonalita komentářů

Tohle je místo, kde se reporty nejčastěji kazí. Platí `~/Dev/context/text/text.md` a k tomu:

- **Věcně a krátce.** Co se stalo, o kolik, oproti čemu.
- **Žádné nadšení.** Ne „skvělý nárůst!“, ne „úžasný výsledek“, ne vykřičníky. Konstatuj číslo a jeho význam.
- **Žádná klišé a agenturní žargon.** Píše se to pro člověka, který nemá čas a nemusí rozumět analytice.
- **Interpretuj, nepopisuj.** „Návštěvnost vzrostla 5×“ je popisek grafu. „Nárůst je organický z Googlu, tedy zvýšené vyhledávání značky – ne odkazy z médií“ je komentář.
- **Nejistotu přiznej.** Malá čísla, krátké období, chybějící segment. Radši „na tohle jsou data příliš malá“ než opatrná formulace, která vypadá jako závěr.

### Grafy

Kromě toho, co říká `dataviz`:

- **Konzistentní barvy napříč celým reportem.** Jedna veličina = jedna barva všude.
- **Osa Y u procent od 0 do 100**, pokud není výslovný důvod jinak.
- **Nemíchej v jednom grafu absolutní čísla a procenta.** Jsou to dva grafy pod sebou se sdílenou osou X.
- **Legenda bez balastu** – žádné hodnoty a roky v závorkách.
- **Přímý tisk.** Report se často tiskne do PDF. Ověř, že se grafy vejdou na šířku stránky a že se nerozpadnou.
- **Tooltipy a interaktivita jsou bonus**, ne nosič informace. Co je jen v tooltipu, v PDF neexistuje.

### Dvě verze

U rozsáhlejších analýz udělej **podrobnou i stručnou verzi**. Stručná je zhruba pětina rozsahu, jen to podstatné, bez opakování – ne zkrácená kopie, ale samostatně napsaný text. Pojmenuj `report.html` (stručná, ta se používá častěji) a `report-podrobny.html`.

Zeptej se, jestli je chce obě, ne že to uděláš automaticky.

### Co nesmí ven ze souboru

Report je soubor, který se posílá dál – e-mailem, do Slacku, klientovi – a jednou venku už ho nevezmeš zpátky. Proto se **kontroluje až hotový vygenerovaný soubor**, ne zdroje. Únik vzniká přesně v tom kroku, kdy se do HTML něco zapeče.

Hledej dvě skupiny.

**1. Osobní údaje.** `user_id`, `user_pseudo_id`, `client_id`, e-maily, jména, telefony, adresy, IP adresy, ID objednávek a faktur, cokoliv, z čeho jde identifikovat konkrétního člověka. Pozor i na nepřímou identifikaci: segment o třech lidech je taky osobní údaj.

**2. Přístupové a autentizační údaje.** Tohle je zrádnější, protože to do reportu nikdo vědomě nedává – proteče to tam samo z výpočetního skriptu, konfigurace nebo odkazu:

- API klíče a tokeny (`api_key`, `api_secret`, `access_token`, `refresh_token`, `bearer`, `client_secret`, měřicí API secret GA4, tokeny MCP serverů)
- hesla, connection stringy k databázi, přihlašovací údaje v jakékoliv podobě
- privátní klíče a certifikáty (`BEGIN … PRIVATE KEY`, `.pem`, `.p12`)
- session cookies a hodnoty hlaviček `Authorization`
- **autentizace v URL** – podepsané odkazy (presigned S3 a GCS, token auth Bunny, sdílecí odkazy Google Drive) a query parametry typu `?token=`, `?key=`, `?sig=`, `?signature=`, `?auth=`. Odkaz do zdroje dat vypadá nevinně, dokud si nevšimneš, že v sobě nese platný podpis.
- interní věci, které nikomu venku nic nedají a jen prozrazují prostředí: absolutní cesty `/Users/honza/…`, interní hostnames a IP, názvy projektů a datasetů, poznámky v komentářích

**Kde hledat.** Ne jen v textu, který je vidět:

- zapečená datová proměnná
- inlinovaný JavaScript a jeho komentáře
- HTML komentáře
- **`data:` URI obrázků** – screenshot z administrace může mít token přímo na obrazovce; když do reportu vkládáš obrázek, který jsi sám nevyrobil z dat, podívej se na něj
- atributy odkazů a `<iframe src>`

**Jak.** Nejdřív mechanicky – grep přes celý soubor na výše uvedené řetězce a na typické tvary (`sk-`, `ghp_`, `AIza`, `eyJ` na začátku JWT, `-----BEGIN`, dlouhé náhodné řetězce v query stringu). Pak si soubor přečti; grep nechytí to, co se jmenuje jinak.

**Když něco najdeš, zastav se.** Neodmazávej to potichu a nepokračuj – nález u druhé skupiny znamená dvě věci, ne jednu:

1. Ten údaj je i **ve zdroji, ze kterého report vznikl** – ve výpočetním skriptu, konfiguraci nebo mezidatech. A ty jsou nejspíš commitnuté v gitu, kde zůstanou i po smazání ze souboru.
2. Unikl-li ven i jen do rozpracované verze, kterou už někdo viděl, **je potřeba ho rotovat**. Řekni to výslovně; to není tvoje rozhodnutí, ale uživatel to musí vědět.

U osobních údajů, které jsou pro smysl reportu opravdu nutné, upozorni výslovně a nech si to potvrdit. **Nikdy to nezamlčuj a nikdy si to neodsouhlas sám.**

------

## Fáze 4 – Ověření

Nespoléhej na to, že to vypadá dobře ve zdrojáku.

1. **Otevři to v Chrome a projdi bod po bodu.** Nalezené chyby oprav, znovu zkontroluj, a takhle dokola, dokud to nebude sedět. Sám cyklus ukonči nejpozději po pátém kole a řekni, co zbývá – nezacyklit se je taky součást práce.
2. **Kontrolní seznam:**
   - Diakritika je všude v pořádku (záhlaví, legendy, tooltipy, tisk).
   - Report funguje otevřený z `file://`, ne jen přes lokální server.
   - V konzoli nejsou chyby.
   - Žádný požadavek do sítě – ověř v záložce Network, že po načtení nejde ven nic.
   - Grafy se vykreslily a mají data. Prázdný nebo `undefined` graf je nejčastější tichá chyba.
   - Čísla v textu komentářů sedí s čísly v grafech a tabulkách.
   - Stránka se nerozpadne na úzkém okně a v tisku do PDF.
3. **Přepočítej namátkou** dva tři údaje z reportu zpátky proti zdrojovým datům.
4. **Projdi hotový soubor na úniky** podle *Co nesmí ven ze souboru* výš. Tohle je poslední krok před předáním, protože až teď je soubor v podobě, ve které odejde – a všechny předchozí opravy do něj mohly něco vnést zpátky.

------

## Fáze 5 – Uzavření

**Zapiš do projektu:**

- **`docs/decisions.md`** – metodická rozhodnutí a proč (jak se definoval uživatel, co se vyloučilo, proč zrovna tahle normalizace). U reportu je metodika to jediné, co se za půl roku nedá zrekonstruovat.
- **`docs/todo.md`** – co se nestihlo, co by šlo doplnit při příští aktualizaci.
- **`CLAUDE.md`** – jak se report přegeneruje, když přijdou nová data. Vždycky přijdou.

**Commitni**, má-li projekt zapnutý autocommit.

**Závěr:**

```
## Report hotový

**Soubory**
- <cesta> – <velikost>, <počet sekcí>
- <skript a mezidata>

**Data**
- Zdroj: <…>   Období: <…>   Vygenerováno: <datum>

**Ověřeno v prohlížeči**
- [seznam kontrol, které prošly]

**Na co upozorňuji**
- [limity dat, osobní údaje, nedopočítané věci – nebo „nic"]
```

Zakonči jednou z těchto vět:

- `Report je hotový a ověřený, můžeš ho poslat dál.`
- `Report hotový není – brání tomu: <konkrétní seznam>.`
