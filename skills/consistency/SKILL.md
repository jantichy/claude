---
name: consistency
description: Audit projektu – konzistence pojmenování, patternů, typů, konfigurace a dokumentace. Problémy řeší interaktivně jeden po druhém.
allowed-tools: [Read, Grep, Glob, Bash, Edit, Write, Agent]
---

# Consistency audit

Proveď kompletní audit vnitřní konzistence aktuálního projektu. Cíl: najít vše, co si v projektu vzájemně odporuje, je redundantní, špatně zatříděné nebo nekonsistentní — a opravit to spolu s uživatelem.

## Fáze 1: Průzkum projektu

Spusť Explore subagenta s tímto zadáním (předej mu absolutní cestu k projektu):

```
Prohledej celý projekt a najdi všechny případy vnitřní nekonzistence. Procházej systematicky a hledej:

KRITICKÉ (mohou rozbít funkčnost):
- Typové nesrovnalosti: stejný koncept/entita definovaná různými typy v různých souborech
- Duplicitní konfigurace s různými hodnotami (tsconfig, package.json, env soubory)
- Env proměnné použité v kódu ale chybějící v .env.example / dokumentaci
- Interface/schéma deklarované jinak než je skutečně používáno
- Import cest, které nesedí se skutečnou strukturou souborů

STŘEDNÍ (technický dluh):
- Duplicitní logika na více místech (stejná funkce implementovaná vícekrát)
- Různé patterny k stejnému problému (např. část kódu používá async/await, část .then())
- Špatně zatříděné soubory (utilita v komponentách, komponenta v utils/)
- README nebo dokumentace popisující funkce, které neexistují nebo fungují jinak
- Nepoužívané exporty, funkce, proměnné (dead code)
- Závislosti v package.json které nejsou použity (nebo naopak)

KOSMETICKÉ (konzistence stylu):
- Mixing naming conventions ve stejném kontextu (camelCase vs snake_case u proměnných, kebab-case vs PascalCase u souborů)
- Inconsistent export styly (named vs default export bez zjevného důvodu)
- Komentáře které nepopisují kód pod nimi (zastaralé, mylné)
- Inconsistentní formátování nebo struktura podobných souborů (např. různá struktura API route handlerů)

SKUPINY SOUBORŮ SE SDÍLENOU STRUKTUROU (kontroluj vždy samostatně):
Aktivně hledej adresáře, kde více souborů stejného typu (MD, JSON, YAML, TS...) zřejmě reprezentuje instance stejného konceptu — každý soubor = jeden systém, jedna entita, jeden modul apod. Typické signály: soubory mají podobné názvy, leží v jednom adresáři, obsahují podobné sekce nebo klíče.

Pro každou takovou skupinu:
1. Urči společnou strukturu (průnik sekcí/klíčů přítomných ve většině souborů)
2. Zkontroluj, zda ji mají opravdu VŠECHNY soubory skupiny
3. Odchylky, které jsou zřejmě záměrné (daný soubor má navíc sekci pro specifickou vlastnost té entity), jsou v pořádku a nehlásit je
4. Hlásit pouze: chybějící sekce ze společného průniku, sekce přítomné jen v podmnožině souborů bez zjevného důvodu, strukturální rozdíly (u jednoho je seznam, u jiného volný text pro stejnou informaci)

Závažnost: obvykle STŘEDNÍ — výjimkou je případ, kdy chybějící sekce způsobuje neúplnost dat (pak KRITICKÉ).

Pro každý nalezený problém uveď:
- Kategorie (KRITICKÉ / STŘEDNÍ / KOSMETICKÉ)
- Stručný popis problému (1-2 věty)
- Konkrétní soubory a řádky (file:line)
- Navrhované nejlepší řešení

Výstup strukturuj jako JSON pole objektů:
[
  {
    "severity": "KRITICKÉ" | "STŘEDNÍ" | "KOSMETICKÉ",
    "title": "krátký název problému",
    "description": "popis problému",
    "locations": ["soubor:řádek", ...],
    "suggested_fix": "konkrétní navrhované řešení"
  }
]
```

## Fáze 2: Zpracování výsledků

Ze JSON výstupu Explore agenta sestavíš interní seznam problémů. Seřaď je: KRITICKÉ první, pak STŘEDNÍ, pak KOSMETICKÉ. V rámci každé kategorie seřaď od nejjednodušší opravy.

## Fáze 3: Přehled

Zobraz uživateli přehled před tím, než začneš procházet problémy:

```
## Výsledky konzistenčního auditu

Nalezeno X problémů celkem:
- 🔴 Kritické: N
- 🟡 Střední: N  
- 🔵 Kosmetické: N

Problémy budu procházet od nejzávažnějších. U každého navrhnu řešení a zeptám se co s ním udělat.
```

Pokud nebyly nalezeny žádné problémy, řekni to a skonči.

## Fáze 4: Interaktivní průchod

Pro KAŽDÝ problém (jeden po druhém, nikdy víc najednou):

1. Zobraz problém v tomto formátu:
```
---
[N/celkem] 🔴/🟡/🔵 NÁZEV PROBLÉMU

Problém: [popis]
Kde: [soubory:řádky]

Navrhované řešení:
[konkrétní popis co přesně změnit — ne vágní "refaktoruj to", ale "přesuň funkci X ze souboru A do B a aktualizuj import v C"]
```

2. Zeptej se uživatele jednou otázkou:
   - **Opravit** — proveď změnu hned
   - **Přeskočit** — zapiš si to a jdi dál (nebude v závěrečném přehledu jako "odloženo")
   - **Odložit** — zapiš si to jako odloženou položku

3. Pokud uživatel zvolí **Opravit**: proveď změnu, ověř že funguje (Bash pro kompilaci/testy pokud jsou k dispozici). Commituj dle autocommit nastavení projektu (zjistíš ho přečtením projektového CLAUDE.md — pokud obsahuje sekci `## Autocommit`, commituj a pushni hned po každé opravě s výstižnou commit message).

4. Pokud uživatel napíše cokoli jiného než volbu, interpretuj to jako doplňující instrukci k aktuálnímu problému (upravi navrhované řešení nebo odpověz na dotaz) — NEdávej to jako "přeskočeno".

5. Pokračuj na další problém.

## Fáze 5: Závěrečné shrnutí

Po projití všech problémů zobraz:

```
## Hotovo

- ✅ Opraveno: N problémů
- ⏭️ Přeskočeno: N problémů
- 📌 Odloženo: N problémů

[Pokud jsou odložené: seznam odložených s jejich popisy]
```
