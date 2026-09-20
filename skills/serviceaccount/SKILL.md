---
name: serviceaccount
description: Skill se použije, když uživatel zadá "/serviceaccount", nebo chce založit service account pro strojový přístup ke klientským systémům – do Google Analytics, Tag Manageru nebo reklamních účtů. Z kontextu projektu odvodí, o kterého klienta a které weby jde, nabídne jména účtů podle konvence, ke každému složí lidský popis, připraví příkaz pro bezpečné uložení klíčů a text žádosti o přístupy pro klienta, a nakonec vzniklé účty zapíše do profilu organizace. Konvenci pojmenování a úrovně oprávnění drží ~/Dev/context/organizations/access.md; skill sám žádné pravidlo nenese. Účty ani klíče nezakládá, protože to je za přihlášením uživatele, a do administrace klientských systémů nevolá.
argument-hint: [klient]
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion]
---

# Service account

## Co skill dělá

Provede založením service accountů pro strojový přístup ke klientským systémům. Odvodí z kontextu projektu, o koho jde, nabídne jména podle konvence, vypíše vše k rozkopírování do Google Cloud konzole a nakonec zapíše vzniklé účty do evidence.

Jediné chování, žádné režimy. Volitelný argument je slug klienta pro případ, že se skill pouští mimo adresář projektu.

## Co skill nedělá

- **Nezakládá účty ani klíče.** Obojí je za uživatelovým přihlášením do Google Cloudu; skill připraví hodnoty a kroky, provedení je na člověku.
- **Nevolá do klientských systémů.** Přístupy uděluje klient ve své administraci, skill k tomu jen sepíše žádost.
- **Nenese konvenci.** Tvar jmen, seznam systémů, úrovně oprávnění a limity drží `~/Dev/context/organizations/access.md`. Ukáže-li se konvence jako špatná, opraví se tam, ne tady.
- **Nesahá na obsah klíče.** Klíč projde jen příkazem, který skill složí; do konverzace se z něj vrací výhradně `client_email` a `client_id`, což jsou veřejné identifikátory.
- **Neřeší přístupy, které už existují.** Skill zakládá nové; revizi toho, kdo kam vidí, dělá člověk v administraci každého systému.

## Fáze 0 – Příprava

Společný začátek je v `~/.claude/skills/PREFLIGHT.md`. Odchylky:

1. **Načti `~/Dev/context/organizations/access.md` celou.** Bez ní skill nemá podle čeho jednat a **nesmí si tvar jména domyslet** – vymyšlené jméno je neměnné a opravuje se jedině novým účtem.
2. **Průběžná kontrola odpadá**, protože skill nemění kód. Řekni to nahlas.
3. **Zápis míří do cizího repozitáře.** Evidence se zapisuje do `~/Dev/context`, který má zapnutý autocommit – skill ho tedy sám commitne a pushne, a nic tam nenechává rozdělané.
4. **Zjisti, o který projekt jde:** projektový `CLAUDE.md` (řádek *Slug*, importovaný profil organizace), jméno adresáře. Nestojíš-li v projektu a argument nedorazil, zeptej se rovnou v *Fázi 1*.

## Fáze 1 – Koho se to týká

Z toho, co jsi zjistil v přípravě, sestav **návrhy vlastníka a úrovní zpřesnění**. Zdroje v pořadí spolehlivosti:

| Zdroj | Co z něj bereš |
|---|---|
| importovaný profil v projektovém `CLAUDE.md` | slug organizace – nejspolehlivější, protože je to táž konvence |
| `~/Dev/context/organizations/` | weby klienta z tabulky v sekci *Co to je* |
| řádek *Slug* v projektovém `CLAUDE.md` | jméno projektu, když organizace není jmenovaná |
| jméno adresáře | poslední záchrana |

**Nabídni varianty přes `AskUserQuestion`** – typicky samotný slug klienta proti slugu se zpřesněním na web. U klienta s jediným webem je správně kratší tvar; u klienta s víc weby rozhoduje, jestli má účet vidět do všech, nebo do jednoho.

**Nepokračuj s vymyšleným slugem.** Nenajdeš-li oporu v profilu organizace, zeptej se; druhá sada jmen pro tytéž organizace je přesně to, čemu konvence brání.

## Fáze 2 – Které systémy

**Zeptej se přes `AskUserQuestion` se zaškrtáváním** (`multiSelect: true`) na systémy ze seznamu v `access.md`. Nabídku ber odtamtud, ne z paměti – přibude-li systém, přibude tam řádek a skill se nemění.

Nevejdou-li se všechny do jedné otázky, rozděl je na dvě; víc než jedna otázka na jednu věc je v pořádku, jen když se jinak nabídka nevejde.

## Fáze 3 – Výpis účtů

Slož adresy a ke každé **display name a description**. Vypiš je jako tabulku, ať se dá rovnou kopírovat do formuláře v konzoli:

```
| Service account ID | Display name | Description |
|---|---|---|
| `<id>` | <lidský název> | <k čemu a ke které property nebo kontejneru> |
```

Vypiš ji jako Markdown, ne jako blok kódu – zpětné apostrofy tady jen oddělují šablonu od textu.

**Ověř každé ID proti limitu třiceti znaků** a délku vypiš u každého. Nevejde-li se, zkrať mezilehlé úrovně podle `access.md` a řekni, co jsi zkrátil – nikdy nezkracuj vlastníka ani systém.

**Display name a description píšeš česky** a počítej s tím, že je uvidí i klient ve výpisu uživatelů svého systému. Žádné interní přezdívky ani poznámky.

## Fáze 4 – Kroky k provedení

Vypiš **čtyři kroky pod sebou**, nic mezi ně nevkládej a mluvnicky je přizpůsob počtu účtů:

**1. Založit účty** na `https://console.cloud.google.com/iam-admin/serviceaccounts?project=jantichy` – bez jediné IAM role a bez principals, jak říká `access.md`.

**2. Vygenerovat klíče** na záložce *Keys* každého účtu, typ JSON. Stáhnou se do složky stažených souborů pod náhodnými jmény.

**3. Uložit klíče a smazat soubory.** Skript vezmi z `access.md` a **vypiš do něj jmenovitě účty, které se právě zakládají**. Nikdy nezpracovávej všechno, co matchuje maska – ve složce stažených souborů leží i klíče k jiným účtům a hvězdička je slije do jedné položky. Doloženo 18. 9. 2026, kdy se takhle sešly čtyři klíče v jedné položce a tři patřily cizím účtům.

**Řekni u toho, co ten příkaz dělá s tajemstvím:** klíč jde do Keychainu a soubor se maže, na výstup jdou jen `client_email` a `client_id`. **A řekni i mez** – Keychain není hranice proti modelu a klientské klíče se podle něj neukládají, dokud nepadne rozhodnutí popsané v `access.md`.

**Nabídni, že příkaz spustíš**, ale nech volbu na uživateli. Pustí-li ho sám, vyžádej si zpátky vypsané dvojice.

**4. Požádat klienta o přístupy.** Sestav text podle tabulky *O co se žádá klienta* v `access.md` – pro každý systém úroveň pro osobní účet i pro service account. Text piš tak, aby se dal poslat beze změn.

## Fáze 5 – Zápis a závěr

**Počkej na potvrzení, že účty vznikly**, a vyžádej si interní ID. Bez nich zápis nedělej – evidence, ve které stojí účet, co nikdy nevznikl, je horší než žádná.

Pak zapiš do **profilu organizace** v `~/Dev/context/organizations/` – do souboru toho klienta, sekce *Systémy* – u každého účtu adresu, k čemu má přístup, interní ID a proklik na detail účtu. Vlastní a pokusné účty patří do tabulky na konci `access.md`. Commitni a pushni.

Výpis na závěr:

```
## Service accounty hotové

- **Vlastník:** <slug>
- **Účty:** <kolik a jaké>
- **Klíče:** <v Keychainu / spustil uživatel / nezaloženy>
- **Evidence:** <soubor a commit>

**Zbývá udělat**
- <co čeká na klienta, nebo „nic">
```

Vypiš ho jako Markdown, ne jako blok kódu, a řádky nezalamuj natvrdo.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Účty jsou založené a zapsané, můžeš požádat klienta o přístupy.`
- `Účty hotové nejsou – brání tomu: <konkrétní seznam>.`
