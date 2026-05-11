# Standardy kódu a bezpečnosti

Závazná pravidla pro psaní kódu a bezpečnostní praktiky platná napříč všemi projekty.

## Obecné principy

### Standardy kódu

- Před implementací používej MCP `context7` pro načtení aktuální dokumentace knihoven, frameworků a SDK.
- Používej nejnovější stabilní verze závislostí. Žádné beta/alpha/RC verze, pokud nejsou explicitně vyžadovány.
- Při úpravách existujících aplikací nebo webů zachovávej konzistenci se zavedeným vizuálním stylem, tónem textů a vzory v kódu. Nejdřív se přizpůsob tomu, co tam je.

### Naming v kódu

Pravidla pro pojmenování tříd, entit, polí, proměnných a funkcí. Cíl: krátký sémantický název, který nese význam bez redundantního obalu — kontext schématu, FK, typu a domény předpokládej, nezdvojuj ho v názvu. Doplňuje obecné naming pravidlo z `~/.claude/RULES.md` (které pokrývá soubory a adresáře).

**Jednoslovné názvy tříd a entit, kde to jde.** Preferuj `Version` před `LessonVersion`, `Domain` před `OrgDomain`, `Membership` před `OrgMembership`. Vztah k jiné entitě patří do FK (`lesson_id`), ne do názvu třídy. Víceslovné jen tehdy, kdy jedno slovo skutečně nestačí.

**Drop redundantní suffixy a prefixy u polí:**

- `_at` u timestamp polí: `created`, `published`, `verified`, `sent`, `purchased`. Past participle implicitně nese „kdy se stalo".
- Jednotkové/formátové suffixy: typ patří do schématu, ne názvu. `duration` ne `duration_s`, `value` ne `amount_czk`, `content` ne `content_md`, `path` ne `r2_key`.
- `is_` u booleanů: `current`, `public`, `verified` — bez prefixu.
- Prefix konkrétní implementace v FK: `video_id` ne `bunny_video_id` (poskytovatel se může změnit; název pole má popisovat doménu, ne dnešní vendor).
- Doménově implikované kvalifikátory: `position` ne `last_pos` v entitě „aktuální stav uživatele". Co je z kontextu tabulky zjevné, do názvu nedávej.

**Stav ⟶ podstatné jméno před slovesem.** Pro pole nesoucí stav nebo datum použij podstatné jméno: `expiration` před `expires`. Sloveso popisuje událost, podstatné jméno popisuje datum/stav, a u datumových polí stav vyhrává.

**Slučovat redundantní pole.** Když lze jedno pole odvodit z druhého, neudržuj obě — derivaci dělej v query. Klasický příklad: `fee_paid_until + frozen_at` → jen `expiration` (frozen je computed `expiration < now()`).

**Vodítko, ne dogma.** Když jednoslovný název způsobí kolizi nebo ztrátu významu, doplň druhé slovo. Ale vždy se nejdřív ptej: nese už kontext (tabulka, FK, typ sloupce) ten význam? Pokud ano, prefix/suffix je redundance.

### Git

- Používej feature větve a otevírej Pull Requesty před mergem do `main`.
- Commit messages: stručné, rozkazovací způsob (imperativ).
- Necommituj ani nepushuj automaticky. Jen na explicitní žádost nebo v projektech s autocommitem.

### Bezpečnost

Tato pravidla platí pro všechny projekty. Na výjimky explicitně upozorňuj a dokumentuj je v PR pod **Security Exception**.

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
