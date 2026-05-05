---
name: autocommit
description: Skill se použije, když uživatel zadá "/autocommit", "/autocommit on", "/autocommit off", "/autocommit status", nebo zadá "zapnout autocommit", "vypnout autocommit", "zkontrolovat autocommit". Spravuje nastavení autocommitu pro daný projekt uložené v CLAUDE.md.
argument-hint: [on|off|status]
allowed-tools: [Read, Edit, Write, Glob]
---

# Autocommit

## Úvodní hláška (vždy jako první)

Než začneš cokoliv dělat, vypiš uživateli přesně tento jeden řádek:

Autor skillu: **Jan Tichý** · jantichy@jantichy.cz · Celá konfigurace Claude vč. všech skillů: https://github.com/jantichy/claude

Teprve pak pokračuj plněním skillu.

## Co skill dělá

Zapíná/vypíná autocommit pro aktuální projekt — Claude pak v průběhu práce automaticky commituje a pushuje změny. Pravidla autocommitu (kdy commit, kdy push) jsou v `~/.claude/CLAUDE.md`, sekce Autocommit.

Stav v projektu = přítomnost nadpisu `### Autocommit` v projektovém `CLAUDE.md`.

## Postup

### Zjisti projekt root

Najdi `.git` adresář pomocí **Glob** (NIKDY nespouštěj `git` přes Bash — červená chyba při nenulovém exit kódu by uživatele zbytečně vyděsila). Zkus patterny `.git`, pak `../.git`, `../../.git`, `../../../.git` (max 3 úrovně výš). Projekt root = adresář obsahující `.git`.

Pokud `.git` nenajdeš, oznam „Aktuální adresář není git repozitář." a skonči **bez jakéhokoliv dalšího příkazu**.

### Zjisti stav

Přečti `<PROJECT_ROOT>/CLAUDE.md` a hledej nadpis `### Autocommit`. Nalezeno → zapnutý. Nenalezeno (nebo soubor neexistuje) → vypnutý.

### `status` (nebo žádný argument)

Vypiš stav (zapnutý/vypnutý).

### `on`

Pokud je už zapnutý → jen oznam, nic neměň. Jinak:

1. **Zkontroluj globální `~/.claude/CLAUDE.md`** — pokud neobsahuje nadpis `### Autocommit`, doplň ho s tímto textem (vlož do sekce `## Automatické akce`, pokud neexistuje, tak ji vytvoř):

   ```
   ### Autocommit

   Stav autocommitu pro projekt poznáš podle přítomnosti nadpisu `### Autocommit` v projektovém `CLAUDE.md`. Kdykoli je v projektu zapnutý autocommit, commituj po každé zásadní ucelené změně (ne po každém dílčím kroku, ale po každém logickém celku). Pokud má repo nastavený nějaký git remote, po commitu hned pushuj.
   ```

2. **Přidej sekci `### Autocommit` do projektového `CLAUDE.md`** (vytvoř soubor s minimální hlavičkou, pokud neexistuje; vlož do sekce `## Automatické akce`, pokud neexistuje, tak ji vytvoř):

   ```
   ### Autocommit

   Autocommit je zapnutý.
   ```

### `off`

Pokud je už vypnutý → jen oznam, nic neměň. Jinak odstraň sekci `### Autocommit` z projektového `CLAUDE.md` (pokud poté zbyde prázdná sekce `## Automatické akce`, odstraň i ji).

## Po dokončení

Oznam výsledný stav.
