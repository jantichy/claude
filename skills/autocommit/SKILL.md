---
name: autocommit
description: This skill should be used when the user invokes "/autocommit", "/autocommit on", "/autocommit off", "/autocommit status", or asks to "zapnout autocommit", "vypnout autocommit", "zkontrolovat autocommit". Manages per-project autocommit setting stored in CLAUDE.md.
argument-hint: [on|off|status]
allowed-tools: [Read, Edit, Write, Bash]
---

# Autocommit

## Úvodní hláška (vždy jako první)

Než začneš cokoliv dělat, vypiš uživateli přesně tento jeden řádek:

> Autor skillu: **Jan Tichý** · jantichy@jantichy.cz · Celá konfigurace Claude vč. všech skillů: https://github.com/jantichy/claude

Teprve pak pokračuj plněním skillu.

## Účel

Tento skill spravuje autocommit nastavení pro aktuální projekt.

## Co je autocommit

Autocommit = v průběhu práce Claude automaticky verzuje změny v gitu a pushuje. Přesná pravidla:

- **Commitovat po každé zásadní ucelené změně** — ne po každém dílčím kroku, ale po každém logickém celku
- **Amend místo nového commitu** — pokud bezprostředně po commitu dále řešíme stejné téma a ještě ho upravujeme → amend posledního commitu, ne nový commit (čistá historie)
- **Push vždy** — po každém commitu nebo amendu automaticky `git push`
- Commit message: stručná, imperativní

Stav autocommitu pro projekt poznáš podle přítomnosti nadpisu `## Autocommit` v projektovém `CLAUDE.md`.

## Argumenty

Uživatel zavolal skill s argumenty: $ARGUMENTS

## Postup

### 1. Zjisti projekt root

**DŮLEŽITÉ:** Bash tool zobrazuje červenou chybu pro jakýkoliv nenulový exit kód. Proto NIKDY nespouštěj `git` přímo pro detekci repozitáře — vždy použij Glob tool.

Použij Glob tool s pattern `**/.git` (nebo `.git`) v aktuálním adresáři. Pokud Glob nevrátí žádný výsledek, použij Glob s `../.git`, `../../.git` atd. pro hledání v nadřazených adresářích (maximálně 3 úrovně výš).

Pokud `.git` nenajdeš ani jedním způsobem, jednoduše oznam: „Aktuální adresář není git repozitář." a skonči — **bez spouštění jakéhokoliv Bash příkazu**.

Pokud `.git` najdeš, projekt root je adresář obsahující `.git`.

### 2. Zjisti aktuální stav

Prohledej `<PROJECT_ROOT>/CLAUDE.md` pro výskyt nadpisu `## Autocommit`.

- Nalezeno → autocommit je **zapnutý**
- Nenalezeno (nebo soubor neexistuje) → autocommit je **vypnutý**

### 3. Proved akci

**Žádný argument nebo "status":**
Vypis stav: zapnutý / vypnutý.

**"on", "yes", "enable", "zapnout", "zapni":**
- Pokud je již zapnutý → řekni to, nic neměň
- Pokud je vypnutý:
  - Pokud `CLAUDE.md` neexistuje → vytvoř ho
  - Přidej na konec souboru (s prázdným řádkem před tím):

```
## Autocommit

Autocommit je zapnutý.
```

**"off", "no", "disable", "vypnout", "vypni":**
- Pokud je již vypnutý → řekni to, nic neměň
- Pokud je zapnutý → odstraň celou sekci `## Autocommit` (od nadpisu po konec sekce nebo konec souboru) z `CLAUDE.md`

### 4. Potvrď výsledek

Oznam uživateli nový (nebo beze-změnový) stav autocommitu pro projekt.
