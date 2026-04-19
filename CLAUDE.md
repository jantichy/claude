# Globální konfigurace Claude Code

## Jazyk
- S uživatelem komunikuj **česky**
- Obsah MD dokumentů piš **česky**, pokud není v daném projektu nebo situaci řečeno jinak
- Kód piš **anglicky** (proměnné, funkce, třídy, soubory)
- Komentáře v kódu piš **česky**, pokud není v daném projektu nebo situaci řečeno jinak

## Styl odpovědí
- Odpovědi krátké a věcné — nepřepisuj co uživatel řekl, rovnou jednej
- Nepoužívej emoji, pokud o ně uživatel nepožádá
- Nepiš trailing shrnutí ("Hotovo, udělal jsem X, Y, Z") — diff mluví za sebe

## Bezpečnost
Tato pravidla platí pro všechny projekty. Výjimky dokumentuj v PR pod **Security Exception**.

- **Žádné tajné hodnoty v kódu ani v gitu.** Žádné API klíče, tokeny, hesla ani přihlašovací údaje ve zdrojovém kódu, konfiguračních souborech ani v git historii. Výhradně proměnné prostředí a `.env` soubory. Vždy ověř, že `.env` je v `.gitignore`. Platí i pro frontend — nikdy nedávej klíče do `VITE_` ani `NEXT_PUBLIC_` proměnných, pokud nejsou skutečně veřejné.
- **RLS jako výchozí**: Zapínej Row-Level Security. Definuj jen minimální, nezbytné politiky (žádný plošný přístup „ALL").
- **Princip nejmenšího oprávnění**: Role a klíče mají mít pouze nutná oprávnění. Nikdy nevystavuj service role klientovi.
- **Validace vstupu**: Vždy na serveru (schéma-based). Nikdy nespoléhej jen na klientskou validaci. Pouze parametrizované dotazy. Escapování výstupu pro XSS.
- **CORS**: V produkci nikdy wildcard `*`. Explicitně whitelistuj povolené origins.
- **Ochrana na úrovni aplikace**: Rate limiting na write endpointech. Bezpečné nahrávání souborů (velikost, typ, úložiště mimo public root).
- Proaktivně navrhuj `/security-review` při práci na autentizaci, platbách, uživatelských datech, API endpointech nebo jiných bezpečnostně citlivých funkcích.

## Standardy kódu
- V TypeScriptu nikdy `type: any`. Používej striktní typování, generiky nebo `unknown`.
- Používej nejnovější stabilní verze závislostí. Žádné beta/alpha/RC verze, pokud nejsou explicitně vyžadovány.
- Před implementací používej MCP `context7` pro načtení aktuální dokumentace.
- Při úpravách existujících aplikací nebo webů zachovávej konzistenci se zavedeným vizuálním stylem, tónem textů a vzory v kódu. Nejdřív se přizpůsob tomu, co tam je.

## Verzování a nasazení
- Git autor email: `jantichy@jantichy.cz` (Vercel odmítá commity bez něj).
- **Defaultně necommituj ani nepushuj automaticky.** Jen na explicitní žádost. Výjimkou jsou projekty s autocommitem — viz sekce Autocommit níže.
- Používej feature větve a otevírej Pull Requesty před mergem do `main`.
- Commit messages: stručné, rozkazovací způsob (imperativ).
- Deploy strategie: Git → GitHub → Vercel (auto-deploy). Pro logy a debugování používej `vercel` CLI (`vercel logs`, `vercel inspect`, `vercel env`).

## Autocommit

**Definice pojmu:** Kdykoli v projektu řeknu „zapni autocommit" (nebo použiji `/autocommit on`), platí: na konci každého promptu, kde dojde k jakékoli změně verzovaného souboru nebo přidání nového souboru, proveď automaticky `git add`, `git commit` (krátká imperativní zpráva) a `git push`. Vypnutý autocommit (`/autocommit off`) vrací výchozí chování (commit jen na explicitní žádost).

Stav autocommitu pro projekt poznáš podle přítomnosti `<!-- autocommit: on -->` v projektovém `CLAUDE.md`.

**Globální pravidlo pro `~/.claude`:** Tento repozitář má autocommit **trvale zapnutý**. Kdykoli v průběhu konverzace upravíš nebo přidáš soubor v `~/.claude`, proveď na konci promptu: `git -C ~/.claude add -A`, commit s výstižnou zprávou, `git -C ~/.claude push`.
