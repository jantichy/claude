---
name: replace
description: Skill se použije, když uživatel zadá "/replace", nebo chce něco přejmenovat či změnit napříč celým projektem – termín, název souboru, adresáře, klíče, eventu, hodnoty – a promítnout to důsledně do všech míst, kde se to zmiňuje, včetně dokumentace, JSONů a názvů souborů.
argument-hint: [starý → nový]
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion]
---

# Replace

## Co skill dělá

Uživatel chce něco přejmenovat nebo změnit **všude**. Skill najde úplně všechny výskyty, ukáže je ke schválení, provede změnu a **ověří, že nikde nezůstal starý tvar**.

Nejde jen o přejmenování. Stejný postup platí pro jakoukoliv změnu, která se má promítnout napříč projektem: jiná hodnota, jiná konvence, jiná struktura zápisu.

## Proč to není obyčejný find-replace

Protože se to pokaždé někde zapomene. Typicky:

- **v názvech souborů a adresářů**, ne jen uvnitř nich,
- v **odvozených tvarech** – jednotné a množné číslo, camelCase, snake_case, kebab-case, slug, česká skloňovaná varianta,
- v **JSONech, konfiguracích a datech**, kde je to hodnota, ne text,
- v **dokumentaci a komentářích**, které nikdo negrepuje,
- v **odkazech a kotvách**, které se rozbijí, i když se text nezmění,
- v **git remote a názvu repozitáře**, když se přejmenovává projekt.

Zapomenutý výskyt se pak vrací měsíce jako záhada. Proto se tenhle skill vždycky končí **kontrolním průchodem na starý tvar**.

## Co skill nedělá

- **Nerozhoduje, jestli se má přejmenovat.** To je rozhodnutí uživatele; skill ho provede.
- **Nesahá mimo projekt.** Cizí podklady a read-only adresáře se nepřepisují.
- **Nemění chování.** Ukáže-li se, že přejmenování vyžaduje i změnu logiky (migrace dat, přesměrování URL), zastaví se a řekne to.
- **Neaudituje projekt.** Na vnitřní konzistenci je `/consistency`.

------

## Fáze 0 – Pre-flight

1. **Kořen projektu.** Ve worktree layoutu (`~/Dev/context/worktree/worktree.md`) pracuj v adresáři větve, ne v kořeni kontejneru.
2. **Přečti projektový `CLAUDE.md`** – `### Autocommit`, konvence pojmenování, `## Výjimky z obecných pravidel`.
3. **Git musí být čistý.** Rozpracované změny před startem se smíchají s přejmenováním a přestane být poznat, co je čí. Vypiš je a zeptej se, jestli je commitnout, odložit, nebo pokračovat i tak.
4. **Zjisti zadání.** Uživatel ho obvykle dá jako argument (`/replace market → site`). Když ne, zeptej se na starý a nový tvar.

------

## Fáze 1 – Rozsah a tvary

**Odvoď všechny tvary**, ve kterých se to může vyskytovat, a **nech si je odsouhlasit**. Nehledej jen doslovný řetězec.

| Rovina | Příklad pro `market` → `site` |
|---|---|
| Základní tvar | `market` → `site` |
| Množné číslo | `markets` → `sites` |
| camelCase | `marketId`, `perMarket` → `siteId`, `perSite` |
| snake_case / kebab | `market_id`, `market-config` → `site_id`, `site-config` |
| Verzálky a konstanty | `MARKET`, `Market` → `SITE`, `Site` |
| Česky, i skloňovaně | „trh“, „trhu“, „trhy“ → „web“, „webu“, „weby“ |
| Názvy souborů a adresářů | `market.md`, `markets/` → `site.md`, `sites/` |
| Hodnoty v datech | `"type": "market"` v JSONu |

**Česká skloňovaná varianta je nejzrádnější** – grep na základní tvar ji nenajde a v dokumentaci jí bývá nejvíc.

Zeptej se přes `AskUserQuestion`, které tvary zahrnout, jsou-li sporné. Rozhodni sám tam, kde je to jednoznačné.

**Vymez, kam se nesahá:** `.git/`, `node_modules/`, `dist/`, generované soubory, `docs/prompts.md` (log promptů se needituje), `docs/research/` a jiné archivy cizích podkladů, historické záznamy, které mají zůstat v původním znění.

------

## Fáze 2 – Inventura

**Najdi všechny výskyty, než cokoliv změníš.** Hledej odděleně:

1. **V obsahu souborů** – grep přes všechny tvary z Fáze 1, case-insensitive tam, kde to dává smysl.
2. **V názvech souborů a adresářů** – `find`. Na tohle se zapomíná nejčastěji.
3. **V gitu** – název větve, remote, popis repozitáře na GitHubu (`gh repo view`).

**Vypiš přehled ke schválení:**

```
## Nalezeno

Tvar              Výskytů   Souborů
market              47        12
markets              8         4
marketId            23         6
„trh" (skloňované)  15         3
market.md            1         –  (název souboru)
markets/             1         –  (název adresáře)

Celkem: 95 výskytů ve 18 souborech + 2 přejmenování

Nesahám na: docs/research/ (12 výskytů), docs/prompts.md (31 výskytů)
```

**Projdi podezřelé výskyty ručně.** Grep najde i to, co se přejmenovat nemá – cizí termín, který se náhodou jmenuje stejně, citaci, historický záznam. Vypiš je zvlášť a zeptej se.

**Nad ~20 výskytů to nepředkládej po jednom** – ukaž pattern, počet a tři příklady, a proveď to hromadně. Po jednom se to nedá odklikat a stejně se to udělá špatně.

------

## Fáze 3 – Provedení

**Pořadí je důležité:**

1. **Nejdřív obsah souborů**, pak teprve názvy souborů a adresářů. Obráceně se rozbijí odkazy, které ještě míří na staré cesty.
2. **Soubory přesouvej přes `git mv`**, ne mazáním a zakládáním – historie se jinak ztratí.
3. **Delší tvary před kratšími.** `marketId` musí projít dřív než `market`, jinak z něj vznikne `siteId` omylem jako `siteid` nebo `site` + `Id`.
4. **Hromadně, ne po jednom** – skript nebo `sed`, ne desítky volání Edit.

Po každém kroku ověř, že se změnilo přesně to, co mělo.

------

## Fáze 4 – Kontrolní průchod

**Tohle je důvod, proč skill existuje.** Nikdy ho nepřeskakuj.

1. **Grep na všechny staré tvary znovu.** Musí vrátit nulu – kromě míst vědomě vyloučených ve Fázi 1, ta vypiš zvlášť.
2. **Grep na nový tvar.** Sedí počet s tím, co jsi měnil? Nevzniklo dvojité přejmenování (`sitesite`, `siteId` z `marketId` už přejmenovaného)?
3. **Rozbité odkazy.** Ověř, že každý odkaz na přejmenovaný soubor, sekci nebo kotvu míří někam, co existuje.
4. **Odvozené údaje.** Souhrnné počty, přehledové tabulky a seznamy na začátku dokumentů – viz `~/.claude/RULES.md`, *Propagace změny*, kde se přehlížejí nejčastěji.
5. **Vnější místa.** Byl-li přejmenovaný celý projekt: remote, popis repozitáře, odkazy z jiných projektů v `~/Dev`.
6. **Testy a build**, existují-li a jde-li to rychle.

Nesedí-li něco, **oprav a projdi znovu** – ne že to jen ohlásíš.

------

## Fáze 5 – Závěr

**Zapiš:**

- `docs/decisions.md` – proč se přejmenovávalo, zvlášť když je nový název méně zřejmý než starý. Za rok to nikdo nezrekonstruuje.
- Existuje-li v projektu místo pro odstraněné a přejmenované věci, **nech tam stopu** – starý název se rád vrací kopírováním odjinud (*Při odstranění nechej stopu* v `~/.claude/RULES.md`).

**Commitni** jako jeden commit, má-li projekt zapnutý autocommit. Přejmenování rozsekané do deseti commitů se špatně čte i vrací.

```
## Přejmenováno

<starý tvar> → <nový tvar>

- Obsah: N výskytů v M souborech
- Názvy: N souborů, M adresářů (git mv)
- Vnější: [remote / popis repozitáře / nic]

**Vědomě nezměněno**
- [cesty a důvod, nebo „nic"]

**Kontrolní průchod**
- Starý tvar: 0 výskytů mimo vyloučené
- Odkazy: [ověřeno / co nesedělo a jak opraveno]
```

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Přejmenováno všude, starý tvar se v projektu nevyskytuje.`
- `Hotové to není – zbývá: <konkrétní seznam>.`
