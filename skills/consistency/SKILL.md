---
name: consistency
description: Skill se použije, když uživatel zadá "/consistency", nebo chce audit projektu – konzistence pojmenování, patternů, typů, konfigurace a dokumentace. Mechanické opravy provede rovnou, sporné řeší interaktivně jeden po druhém.
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion]
---

# Consistency

## Co skill dělá

Proveď kompletní audit vnitřní konzistence aktuálního projektu. Cíl: najít vše, co si v projektu vzájemně odporuje, je redundantní, špatně zatříděné nebo nekonsistentní – a opravit to spolu s uživatelem.

## Co skill nedělá

- **Nehledá chyby v kódu.** Na korektnost provedených změn je `/code-review`.
- **Nekontroluje soulad s doménovými standardy.** Na odchylky od předpisů v `~/Dev/context/` je `/review`. Tenhle skill se ptá „sedí si projekt sám se sebou?“, ne „drží předpis?“ – projekt může být dokonale konzistentní a přitom konzistentně porušovat standard.
- **Neposuzuje, jestli je návrh dobrý.** Na to je `/oponent`.
- **Nevytěžuje session.** Zápis dohod do souborů dělá `/cleanup`, který běží až po tomhle.
- **Nemění chování.** Nálezy, které by ho změnily, jsou vždy sporné a jdou přes uživatele.
- **Neopakuje, co udělal `/review`.** Typecheck, linter, testy, audit závislostí ani scan tajemství tu neběží – proběhly o krok dřív a od té doby se nic nezměnilo. Tenhle skill dorovnává jen ten konzistenční zbytek přes celý projekt, který předchozí kroky osy nepokrývají.

## Fáze 0 – Pre-flight: kontext a baseline

Před spuštěním Explore agenta nasbírej baseline. Tam, kde jsou nezávislé čtecí operace, používej paralelní tool calls.

### 0.1 Načti dokumentaci konvencí

*Worktree layout* (`~/Dev/context/worktree/worktree.md`): auditovaný projekt je **pracovní adresář jedné větve**, ne kontejner. Stojíš-li v kořeni kontejneru, přesuň se nejdřív do adresáře té větve – jinak bys projel všechny větve naráz a hlásil rozdíly mezi nimi jako nekonzistence. „Projektový `CLAUDE.md`“ je pak ten ve worktree, ne stub v kořeni.

Pokud existují, přečti:
- Projektový `CLAUDE.md`
- `README.md`, `CONTRIBUTING.md`, `STYLEGUIDE.md`
- `eslint.config.*`, `.eslintrc*`, `prettier.config.*`, `.prettierrc*`, `biome.json`
- `tsconfig.json` (zejména `strict`, `target`, `lib`, paths)
- `.editorconfig`
- `package.json` (engines, scripts, workspaces)

Z těchto souborů sestav **baseline konvencí** – co je v projektu explicitně dohodnuto. Co projekt sám aktivně dodržuje, nehlas jako kosmetickou odchylku; naopak rozpor s baseline hlas důsledněji.

### 0.2 Načti seznam ignorovaných položek

Pokud projektový `CLAUDE.md` obsahuje kapitolu `## Consistency`, přečti ji. Položky tam uvedené (s důvodem) **vůbec neuváděj** v nálezech – uživatel je dříve označil jako „won't fix“.

### 0.3 Spusť nástroje, které předchozí kroky osy nedělají

**Typecheck ani linter tady nespouštěj.** Pustil je `/review` o krok dřív a po každé své opravě je pustil znovu, takže stav, se kterým sem přicházíš, byl naposledy ověřený jím – opakovat je znamená platit časem i tokeny za tentýž výsledek. Viz `~/.claude/RULES.md`, *Životní cyklus práce*.

Spusť jen to, co je vlastní téhle otázce – hledání mrtvého kódu a nepoužitých závislostí, tedy „sedí si projekt sám se sebou?“, na což se `/review` neptá:

- `knip` nebo `depcheck`, jsou-li v projektu nainstalované (zjisti z `package.json`)

Nemá-li je projekt (nebo nemá `package.json` vůbec, což je u obsahového či znalostního projektu normální), **krok přeskoč a řekni to** – i s tím, co se tím nezkontrolovalo. Audit v dalších fázích běží stejně, jen bez téhle vrstvy.

Výstupy si zapamatuj a předej Explore agentovi. Nálezy z toolchainu se označí tagem `[toolchain]`.

**Běží-li `/consistency` samostatně mimo osu** (tedy bez předchozího `/review`) a projekt má *Kontrakt příkazů*, řekni uživateli jednou větou, že zelená linka teď prověřená není a že `/review` se dělá dřív.

## Fáze 1 – Průzkum projektu

Spusť Explore subagenta s tímto zadáním (předej mu absolutní cestu k projektu, baseline z 0.1, seznam ignorovaných z 0.2 a výstupy nástrojů z 0.3):

```
Prohledej celý projekt a najdi všechny případy vnitřní nekonzistence. Procházej systematicky.

PŘED HLÁŠENÍM PROBLÉMU vždy zkontroluj, že:
- Není uveden v kapitole `## Consistency` projektového `CLAUDE.md` (předané v zadání) – pokud ano, neuváděj ho
- Není přímo nad řádkem komentář `consistency-ignore: <důvod>` – pokud ano, respektuj ho
- Soubor není v cestě označené jako legacy/vendored/generated (`*.gen.*`, `vendor/`, `legacy/`, `generated/`, `node_modules/`, `dist/`, `build/`) – pokud ano, neuváděj ho
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
- Obsah ve špatném souboru podle cílového čtenáře: `README.md` je popis projektu **pro člověka**, takže normativní pokyny pro Clauda (pravidla práce v repozitáři, konvence, povinnost něco udržovat) v něm nemají co dělat ani odkazem – patří do `CLAUDE.md`, `docs/rules.md` nebo `docs/decisions.md`. Definice je v `~/Dev/context/structure/structure.md`
- Nepoužívané exporty, funkce, proměnné (dead code)
- Zapomenuté zbytky po odstranění: když se v minulosti odstraňoval kód, feature nebo komponenta, mohly na dalších místech zůstat pozapomenuté části – importy smazaného modulu, konfigurace pro zrušenou funkci, typy/interfacy pro odstraněnou entitu, registrace odebrané route nebo pluginu, zmínky v dokumentaci nebo komentářích, testy odstraněné funkcionality, env proměnné pro mrtvou feature, reference v package.json apod.
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
Aktivně hledej adresáře, kde více souborů stejného typu (MD, JSON, YAML, TS...) zřejmě reprezentuje instance stejného konceptu – každý soubor = jeden systém, jedna entita, jeden modul apod. Typické signály: soubory mají podobné názvy, leží v jednom adresáři, obsahují podobné sekce nebo klíče.

Pro každou takovou skupinu:
1. Urči společnou strukturu (průnik sekcí/klíčů přítomných ve většině souborů)
2. Zkontroluj, zda ji mají opravdu VŠECHNY soubory skupiny
3. Odchylky, které jsou zřejmě záměrné (daný soubor má navíc sekci pro specifickou vlastnost té entity), jsou v pořádku a nehlásit je
4. Hlásit pouze: chybějící sekce ze společného průniku, sekce přítomné jen v podmnožině souborů bez zjevného důvodu, strukturální rozdíly (u jednoho je seznam, u jiného volný text pro stejnou informaci)

Závažnost: obvykle STŘEDNÍ – výjimkou je případ, kdy chybějící sekce způsobuje neúplnost dat (pak KRITICKÉ).

GROUPING (povinné):
- Pokud má víc nálezů stejný root cause (jedno přejmenování → desítky souborů, jeden chybný typ → mnoho dotčených míst), seskup je do jedné položky s podproblémy a v poli `related_root` u následků uveď title root položky.
- Pokud má jeden problém >20 výskytů, neuváděj jednotlivé řádky – uveď pattern, počet výskytů, příklad 3 lokací a navrhni hromadnou změnu (codemod / find-replace). Označ tagem `batch`.
- Nálezy, které pocházejí z toolchain výstupů předaných v zadání (tsc/lint/knip), uveď, ale označ tagem `toolchain` – uživatel může chtít řešit přes nástroj, ne ručně.

Pro každý nalezený problém uveď:
- Kategorie (KRITICKÉ / STŘEDNÍ / KOSMETICKÉ)
- Stručný popis problému (1-2 věty)
- Konkrétní soubory a řádky (file:line); u batch uveď root + počet + 3 příklady
- Navrhované nejlepší řešení (konkrétní akce, ne vágní "refaktoruj to")
- Tagy `toolchain` / `batch`, pokud se hodí
- `related_root` – title jiného problému, jehož je tento následkem (volitelné)

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

## Fáze 2 – Zpracování výsledků

Z JSON výstupu Explore agenta sestav interní seznam problémů. Seřaď: KRITICKÉ první, pak STŘEDNÍ, pak KOSMETICKÉ. V rámci každé kategorie umísti root položky před jejich následky (přes `related_root`), aby se opravou rootu mohlo automaticky vyřešit víc následných.

### Rozdělení na mechanické a sporné

**Kritérium je společné s `/review`** – plná definice obou skupin i s výčtem typických případů je v `~/.claude/skills/review/SKILL.md`, *Fáze 4 – Zpracování výsledků*. Neopisuj ji sem; drž se jí a přidej jen to, co platí navíc tady:

- Nálezy s tagem **`toolchain`** (z `knip`/`depcheck`) posuzuj stejně jako ostatní – nástroj ukazuje, že se něco nepoužívá, ne že se to má smazat.
- **Mazání kódu, který vypadá mrtvý, je vždy sporné.** Může být volaný dynamicky, z konfigurace nebo z jiného repozitáře.
- Práh pro `batch` je **>20 výskytů** (shodně s `/review`), a `batch` nález je vždy sporný.

## Fáze 3 – Přehled

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

Mechanických (jednoznačná bezriziková oprava): N – ty opravím rovnou a jen je vypíšu.
Sporných: M – ty projdeme spolu od nejzávažnějších, u každého navrhnu řešení a zeptám se.
```

Pokud nebyly nalezeny žádné problémy, řekni to a skonči.

## Fáze 4 – Mechanické opravy

Mechanické nálezy (viz Fáze 2) oprav **rovnou, bez ptaní**. Pak:

1. **Ověř, že jsi nic nerozbil.** Spouštěj **jen příkazy z `## Příkazy` v projektovém `CLAUDE.md`** (*Kontrakt příkazů*, viz `~/Dev/context/coding/coding.md`): `typecheck` a `test` po každé opravě, která se dotkla kódu, `build` jen když je rychlý a oprava se ho týká. Chybí-li řádek, krok **přeskoč nahlas** a napiš, co se tím neověřilo; nevymýšlej příkazy, které jsi neověřil. Nemá-li projekt kontrakt vůbec (obsahový, znalostní), verifikace odpadá – ale u opravy, která sáhla do odkazů nebo cest, si aspoň ověř čtením, že cíl existuje. Když kontrola selže, **zastav se**, ukaž chybu a diff a zeptej se, jak pokračovat.
2. Vypiš, co jsi opravil – jeden řádek na nález:
   ```
   ## Opraveno rovnou (N mechanických)
   - 🔵 [název] – soubor:řádek – [co konkrétně změněno]
   ```
3. Commit dle autocommit nastavení projektu. Mechanické opravy commituj **jedním commitem** dohromady, ne po jedné.

Pokud uživatel na některou z těchto oprav zareaguje nesouhlasem, vrať ji a zařaď mezi sporné.

Pokud nejsou žádné sporné nálezy, přeskoč Fázi 5 rovnou na závěrečné shrnutí.

## Fáze 5 – Interaktivní průchod

**Postup je společný s `/review`** – tvar výpisu nálezu, volání `AskUserQuestion` (jeden nález = jedna otázka, volby *Opravit / Odložit / Přeskočit*, u `batch` navíc *Rozbalit*), zpracování odpovědí i pravidla pro hromadné opravy jsou v `~/.claude/skills/review/SKILL.md`, *Fáze 7 – Interaktivní průchod*. Řiď se jím a lišíš se jen v těchhle bodech:

**Kam se zapisuje „won't fix“.** Do kapitoly `## Consistency` v projektovém `CLAUDE.md`, ne `## Review` – jsou to odpovědi na jinou otázku a nemají se míchat. Kapitolu založ, když chybí, a zapisuj na její konec:

```
## Consistency

Položky vyhodnocené při /consistency auditu jako „neopravovat". Při dalším auditu se neuvádějí.

- **YYYY-MM-DD** – *<title>*: <důvod>
  - Lokace: <soubor:řádek, ...>
```

Datum vezmi z `Today's date is …` v system-reminderu.

**Verifikace po opravě.** Po každé odsouhlasené opravě platí bod 1 z *Fáze 4* – příkazy z *Kontraktu příkazů*, chybějící krok přeskočit nahlas, u projektu bez kontraktu ověřit aspoň čtením, že cíl opravovaného odkazu existuje.

**Co tu nehrozí.** `/consistency` nemění chování, takže odpadá pravidlo z `/review` o doplnění testu k opravě – nálezy, které by chování měnily, jsou tu vždy sporné a jdou přes uživatele.

## Fáze 6 – Závěrečné shrnutí

Po projití všech problémů zobraz:

```
## Hotovo

- ⚡ Opraveno rovnou (mechanické): N problémů
- ✅ Opraveno po odsouhlasení: N problémů
- 🪄 Vyřešeno automaticky (následek root opravy): N problémů
- 📌 Odloženo: N problémů
- ⏭️ Přeskočeno (zapsáno do CLAUDE.md → Consistency): N problémů

[Pokud jsou odložené: seznam odložených s jejich popisy]
```

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Projekt je konzistentní, všechny nálezy jsou vypořádané.`
- `Konzistentní zatím není – zbývá: <konkrétní seznam>.`
