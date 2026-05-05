# Standardy kódu a bezpečnosti

Závazná pravidla pro psaní kódu a bezpečnostní praktiky platná napříč všemi projekty.

## Obecné principy

### Standardy kódu

- Před implementací používej MCP `context7` pro načtení aktuální dokumentace knihoven, frameworků a SDK.
- Používej nejnovější stabilní verze závislostí. Žádné beta/alpha/RC verze, pokud nejsou explicitně vyžadovány.
- Při úpravách existujících aplikací nebo webů zachovávej konzistenci se zavedeným vizuálním stylem, tónem textů a vzory v kódu. Nejdřív se přizpůsob tomu, co tam je.

### Bezpečnost

Tato pravidla platí pro všechny projekty. Výjimky dokumentuj v PR pod **Security Exception**.

- **Žádné tajné hodnoty v kódu ani v gitu.** Žádné API klíče, tokeny, hesla ani přihlašovací údaje ve zdrojovém kódu, konfiguračních souborech ani v git historii. Výhradně proměnné prostředí a `.env` soubory. Vždy ověř, že `.env` je v `.gitignore`.
- **Princip nejmenšího oprávnění**: Role, klíče a tokeny mají mít pouze nutná oprávnění.
- **Validace vstupu**: Vždy na serveru (schéma-based). Nikdy nespoléhej jen na klientskou validaci.
- **Ochrana na úrovni aplikace**: Rate limiting na write endpointech. Bezpečné nahrávání souborů (kontrola velikosti, typu, úložiště mimo public root).
- Proaktivně navrhuj `/security-review` při práci na autentizaci, platbách, uživatelských datech, API endpointech nebo jiných bezpečnostně citlivých funkcích.

------

## Platform-specific

### TypeScript

- Nikdy `type: any`. Používej striktní typování, generiky nebo `unknown`.

### SQL a databáze

- **Pouze parametrizované dotazy.** Nikdy neskládej SQL přes string interpolation.
- **Row-Level Security jako výchozí** (Postgres, Supabase): zapínej RLS na každé tabulce. Definuj jen minimální, nezbytné politiky — žádný plošný přístup „ALL".
- **Service role nikdy nevystavuj klientovi.** Service role klíče zůstávají server-side.

### Web a frontend

- **CORS**: V produkci nikdy wildcard `*`. Explicitně whitelistuj povolené origins.
- **Escapování výstupu pro XSS**: Spoléhej na escape mechanismy frameworku (React, Vue, ...) a ručně escapuj vše, co obchází (např. `dangerouslySetInnerHTML`).
- **Klíče v build-time proměnných**: Nikdy nedávej tajné klíče do `VITE_*` ani `NEXT_PUBLIC_*` proměnných, pokud nejsou skutečně veřejné — tyto proměnné se zapečou do bundle a doručí každému návštěvníkovi.
