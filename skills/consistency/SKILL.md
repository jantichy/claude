---
name: consistency
description: Audit projektu – konzistence pojmenování, patternů, typů, konfigurace a dokumentace. Problémy řeší interaktivně jeden po druhém.
allowed-tools: [Read, Grep, Glob, Bash, Edit, Write, Agent]
---

# Consistency audit

## Úvodní hláška (vždy jako první)

Než začneš cokoliv dělat, vypiš uživateli přesně tento jeden řádek:

Autor skillu: **Jan Tichý** · jantichy@jantichy.cz · Celá konfigurace Claude vč. všech skillů: https://github.com/jantichy/claude

Teprve pak pokračuj plněním skillu.

## Účel

Proveď kompletní audit vnitřní konzistence aktuálního projektu. Cíl: najít vše, co si v projektu vzájemně odporuje, je redundantní, špatně zatříděné nebo nekonsistentní — a opravit to spolu s uživatelem.

## Fáze 1: Pre-flight — kontext a baseline

Před spuštěním Explore agenta nasbírej baseline. Tam, kde jsou nezávislé čtecí operace, používej paralelní tool calls.

### 1.1 Načti dokumentaci konvencí

Pokud existují, přečti:
- Projektový `CLAUDE.md` (zejména kapitolu `## Consistency`, viz Fáze 5)
- `README.md`, `CONTRIBUTING.md`, `STYLEGUIDE.md`
- `eslint.config.*`, `.eslintrc*`, `prettier.config.*`, `.prettierrc*`, `biome.json`
- `tsconfig.json` (zejména `strict`, `target`, `lib`, paths)
- `.editorconfig`
- `package.json` (engines, scripts, workspaces)

Z těchto souborů sestav **baseline konvencí** — co je v projektu explicitně dohodnuto. Co projekt sám aktivně dodržuje, nehlas jako kosmetickou odchylku; naopak rozpor s baseline hlas důsledněji.

### 1.2 Načti seznam ignorovaných položek

Pokud projektový `CLAUDE.md` obsahuje kapitolu `## Consistency`, přečti ji. Položky tam uvedené (s důvodem) **vůbec neuváděj** v nálezech — uživatel je dříve označil jako "won't fix".

### 1.3 Spusť existující nástroje

Pokud jsou v projektu k dispozici (zjisti z `package.json` scripts a devDeps), spusť — paralelně:
- `tsc --noEmit` (jen u TypeScript projektů)
- linter v `--quiet` módu (eslint, biome apod.)
- `knip` nebo `depcheck`, pokud jsou nainstalované

Výstupy si zapamatuj a předej Explore agentovi. Pokud nástroj selže nebo není dostupný, pokračuj a poznamenej to. Nálezy z toolchainu se v dalších fázích označí tagem `[toolchain]`.

## Fáze 2: Průzkum projektu

Spusť Explore subagenta s tímto zadáním (předej mu absolutní cestu k projektu, baseline z 1.1, seznam ignorovaných z 1.2 a výstupy nástrojů z 1.3):

```
Prohledej celý projekt a najdi všechny případy vnitřní nekonzistence. Procházej systematicky.

PŘED HLÁŠENÍM PROBLÉMU vždy zkontroluj, že:
- Není uveden v sekci "Ignorované položky" (předané v zadání) — pokud ano, neuváděj ho
- Není přímo nad řádkem komentář `consistency-ignore: <důvod>` — pokud ano, respektuj ho
- Soubor není v cestě označené jako legacy/vendored/generated (`*.gen.*`, `vendor/`, `legacy/`, `generated/`, `node_modules/`, `dist/`, `build/`) — pokud ano, neuváděj ho
- Pokud baseline projektu (předaný v zadání) explicitně dovoluje to, co bys hlásil jako odchylku, neuváděj to

KRITICKÉ (mohou rozbít funkčnost):
- Typové nesrovnalosti: stejný koncept/entita definovaná různými typy v různých souborech
- Duplicitní konfigurace s různými hodnotami (tsconfig, package.json, env soubory)
- Env proměnné použité v kódu ale chybějící v .env.example / dokumentaci
- Interface/schéma deklarované jinak než je skutečně používáno
- Import cest, které nesedí se skutečnou strukturou souborů
- Cross-layer kontrakty: rozdíly mezi DB schématem ↔ ORM modelem ↔ TypeScript typy ↔ validačním schématem (Zod/Yup); API endpoint ↔ klientský volání (request/response, query params); GraphQL/OpenAPI specifikace ↔ implementace; form schéma ↔ submit payload ↔ serverový endpoint
- Bezpečnostní konzistence: tabulky/endpointy někde chráněné (RLS, auth middleware), jinde podobné ne; chybějící input sanitizace / parametrizace na endpointech, které ji jinde mají; nekonzistentní CORS / rate-limiting pravidla
- Verzování runtime: různé verze stejné lib v monorepo packages; rozjetá Node verze napříč `engines` / `.nvmrc` / `.tool-versions` / CI config / hosting config; TS `target` vs browserslist drift; lockfile vs manifest drift

STŘEDNÍ (technický dluh):
- Duplicitní logika na více místech (stejná funkce implementovaná vícekrát)
- Různé patterny k stejnému problému (např. async/await vs. .then())
- Behaviorální konzistence: stejný typ chyby řešený různě (throw vs. Result vs. silent vs. null); různé loggery/úrovně/formáty pro stejný typ události; podobné endpointy validují vstup jen někdy; auth/authz mechanismy se liší napříč podobnými endpointy bez důvodu; data fetching / state management řeší stejný use-case různě (lokální state vs. global store, fetch vs. React Query vs. SWR)
- Špatně zatříděné soubory (utilita v komponentách, komponenta v utils/)
- README nebo dokumentace popisující funkce, které neexistují nebo fungují jinak
- Nepoužívané exporty, funkce, proměnné (dead code)
- Zapomenuté zbytky po odstranění: když se v minulosti odstraňoval kód, feature nebo komponenta, mohly na dalších místech zůstat pozapomenuté části — importy smazaného modulu, konfigurace pro zrušenou funkci, typy/interfacy pro odstraněnou entitu, registrace odebrané route nebo pluginu, zmínky v dokumentaci nebo komentářích, testy odstraněné funkcionality, env proměnné pro mrtvou feature, reference v package.json apod.
- Závislosti v package.json které nejsou použity (nebo naopak)
- i18n a UI texty: chybějící překladové klíče (použité v kódu, nejsou ve slovníku); nepoužité klíče (ve slovníku, nikde nereferencované); stejný UI koncept různě pojmenovaný napříč obrazovkami ("Smazat" vs "Odstranit" vs "Vymazat"); nesystematický mix jazyků v UI textech
- Časový drift: TODO/FIXME starší než ~6 měsíců (zjistitelné `git blame`); komentáře s deadlinem v minulosti ("remove after 2025-01"); feature flagy s trvale stejnou hodnotou na všech check-pointech (ready to inline/remove); pozastavené migrace (částečná DB migrace bez follow-upu)

KOSMETICKÉ (konzistence stylu):
- Mixing naming conventions ve stejném kontextu (camelCase vs snake_case u proměnných, kebab-case vs PascalCase u souborů)
- Inconsistent export styly (named vs default export bez zjevného důvodu)
- Komentáře které nepopisují kód pod nimi (zastaralé, mylné)
- Inconsistentní formátování nebo struktura podobných souborů (např. různá struktura API route handlerů)
- Naming napříč boundaries: stejná entita s různými názvy v různých vrstvách (`User` v DB / `UserAccount` v API / `userObj` v UI); inkonzistentní pluralizace v adresářích a routes (`users/user`, `items/item`); stejný koncept různými slovy v komentářích / UI / kódu (mix čeština/angličtina bez systému)

SKUPINY SOUBORŮ SE SDÍLENOU STRUKTUROU (kontroluj vždy samostatně):
Aktivně hledej adresáře, kde více souborů stejného typu (MD, JSON, YAML, TS...) zřejmě reprezentuje instance stejného konceptu — každý soubor = jeden systém, jedna entita, jeden modul apod. Typické signály: soubory mají podobné názvy, leží v jednom adresáři, obsahují podobné sekce nebo klíče.

Pro každou takovou skupinu:
1. Urči společnou strukturu (průnik sekcí/klíčů přítomných ve většině souborů)
2. Zkontroluj, zda ji mají opravdu VŠECHNY soubory skupiny
3. Odchylky, které jsou zřejmě záměrné (daný soubor má navíc sekci pro specifickou vlastnost té entity), jsou v pořádku a nehlásit je
4. Hlásit pouze: chybějící sekce ze společného průniku, sekce přítomné jen v podmnožině souborů bez zjevného důvodu, strukturální rozdíly (u jednoho je seznam, u jiného volný text pro stejnou informaci)

Závažnost: obvykle STŘEDNÍ — výjimkou je případ, kdy chybějící sekce způsobuje neúplnost dat (pak KRITICKÉ).

GROUPING (povinné):
- Pokud má víc nálezů stejný root cause (jedno přejmenování → desítky souborů, jeden chybný typ → mnoho dotčených míst), seskup je do jedné položky s podproblémy a v poli `related_root` u následků uveď title root položky.
- Pokud má jeden problém >20 výskytů, neuváděj jednotlivé řádky — uveď pattern, počet výskytů, příklad 3 lokací a navrhni hromadnou změnu (codemod / find-replace). Označ tagem `batch`.
- Nálezy, které pocházejí z toolchain výstupů předaných v zadání (tsc/lint/knip), uveď, ale označ tagem `toolchain` — uživatel může chtít řešit přes nástroj, ne ručně.

Pro každý nalezený problém uveď:
- Kategorie (KRITICKÉ / STŘEDNÍ / KOSMETICKÉ)
- Stručný popis problému (1-2 věty)
- Konkrétní soubory a řádky (file:line); u batch uveď root + počet + 3 příklady
- Navrhované nejlepší řešení (konkrétní akce, ne vágní "refaktoruj to")
- Tagy `toolchain` / `batch`, pokud se hodí
- `related_root` — title jiného problému, jehož je tento následkem (volitelné)

Výstup strukturuj jako JSON pole objektů:
[
  {
    "severity": "KRITICKÉ" | "STŘEDNÍ" | "KOSMETICKÉ",
    "title": "krátký název problému",
    "description": "popis problému",
    "locations": ["soubor:řádek", ...],
    "suggested_fix": "konkrétní navrhované řešení",
    "tags": ["toolchain"?, "batch"?],
    "related_root": "title jiného problému, jehož je tento následkem (volitelné)"
  }
]
```

## Fáze 3: Zpracování výsledků

Z JSON výstupu Explore agenta sestav interní seznam problémů. Seřaď: KRITICKÉ první, pak STŘEDNÍ, pak KOSMETICKÉ. V rámci každé kategorie umísti root položky před jejich následky (přes `related_root`), aby se opravou rootu mohlo automaticky vyřešit víc následných.

## Fáze 4: Přehled

Zobraz uživateli přehled před tím, než začneš procházet problémy:

```
## Výsledky konzistenčního auditu

Nalezeno X problémů celkem:
- 🔴 Kritické: N
- 🟡 Střední: N
- 🔵 Kosmetické: N

Z toho:
- [toolchain] hlášeno již existujícím nástrojem: N
- [batch] hromadné (>20 výskytů): N

Problémy budu procházet od nejzávažnějších. U každého navrhnu řešení a zeptám se co s ním udělat.
```

Pokud nebyly nalezeny žádné problémy, řekni to a skonči.

## Fáze 5: Interaktivní průchod

Pro KAŽDÝ problém (jeden po druhém, nikdy víc najednou):

1. Zobraz problém v tomto formátu:
```
---
[N/celkem] 🔴/🟡/🔵 [tagy] NÁZEV PROBLÉMU

Problém: [popis]
Kde: [soubory:řádky, nebo "X výskytů, např. ..." u batch]

Navrhované řešení:
[konkrétní popis co přesně změnit — ne vágní "refaktoruj to", ale "přesuň funkci X ze souboru A do B a aktualizuj import v C"]
```

2. Zeptej se uživatele jednou otázkou ve formátu:
   `Opravit (A) / Odložit (B) / Přeskočit (C)?` — u batch problémů přidej `/ Rozbalit (D)`
   Přijímej jak celá slova, tak samotná písmena (bez ohledu na velikost):
   - **A / Opravit** — proveď změnu hned (krok 3)
   - **B / Odložit** — zapiš do interního seznamu odložených, neřeš teď
   - **C / Přeskočit** — zeptej se na krátký důvod ("Proč to neopravovat?") a zapiš do projektového `CLAUDE.md` do kapitoly `## Consistency` (krok 6). Pokud uživatel nechce uvést důvod, zapiš `(bez uvedeného důvodu)`.
   - **D / Rozbalit** (jen u batch) — vypiš všechny lokace a začni je řešit jednotlivě jako samostatné podproblémy

3. Pokud uživatel zvolí **A / Opravit**:
   a. Proveď změnu. U batch problému (>20 výskytů) řeš hromadně — find-replace, codemod, scripted edit přes Bash; **ne** desítky Edit volání po jednom.
   b. **Verifikace po opravě — vždy, ne občas.** Spusť relevantní kontroly:
      - U TS projektu: `tsc --noEmit`
      - Pokud projekt má build script a oprava se týká buildovaného kódu a build je rychlý (~30s): `<package manager> run build`
      - Pokud existují relevantní testy pro upravený soubor a jdou rychle pustit: pusť je
   c. Pokud kontrola selže: **zastav se**, ukaž uživateli chybu a diff a zeptej se jak pokračovat. Nepokračuj automaticky na další problém.
   d. Po úspěšné opravě KRITICKÉHO problému přepočítej zbývající seznam — projdi položky s `related_root === <title opraveného>` a krátce ověř (Read/Grep), zda už nejsou neaktuální. Ty, co se vyřešily samy, vyhoď z fronty a započítej je do "vyřešeno automaticky" v závěrečném shrnutí.
   e. Commit dle autocommit nastavení projektu — pokud projektový `CLAUDE.md` obsahuje sekci `## Autocommit`, commituj a pushni hned po každé opravě s výstižnou commit message.

4. Pokud uživatel napíše cokoli jiného než volbu (A/B/C/D nebo celé slovo), interpretuj to jako doplňující instrukci k aktuálnímu problému (uprav navrhované řešení nebo odpověz na dotaz) — NEdávej to jako "přeskočeno".

5. Pokračuj na další problém.

6. Zápis do `## Consistency` v projektovém CLAUDE.md (krok 2 — Přeskočit):
   - Pokud projektový `CLAUDE.md` neexistuje, vytvoř ho s minimálním obsahem (hlavička + kapitola `## Consistency`)
   - Pokud kapitola `## Consistency` neexistuje, doplň ji na konec souboru
   - Formát záznamu (přidávat na konec kapitoly):
   ```
   ## Consistency

   Položky vyhodnocené při /consistency auditu jako "neopravovat". Při dalším auditu se neuvádějí.

   - **YYYY-MM-DD** — *<title>*: <důvod>
     - Lokace: <soubor:řádek, ...>
   ```
   - Datum vezmi z `Today's date is ...` v system-reminderu.

## Fáze 6: Závěrečné shrnutí

Po projití všech problémů zobraz:

```
## Hotovo

- ✅ Opraveno: N problémů
- 🪄 Vyřešeno automaticky (následek root opravy): N problémů
- 📌 Odloženo: N problémů
- ⏭️ Přeskočeno (zapsáno do CLAUDE.md → Consistency): N problémů

[Pokud jsou odložené: seznam odložených s jejich popisy]
```
