---
name: autocommit
description: This skill should be used when the user invokes "/autocommit", "/autocommit on", "/autocommit off", "/autocommit status", or asks to "zapnout autocommit", "vypnout autocommit", "zkontrolovat autocommit". Manages per-project autocommit setting stored in CLAUDE.md.
argument-hint: [on|off|status]
allowed-tools: [Read, Edit, Write, Bash]
---

# Autocommit

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

Použij Glob tool k hledání souboru `.git` nebo adresáře `.git` v aktuálním a nadřazených adresářích — nebo spusť příkaz přesměrováním stderr na `/dev/null`, aby se žádná chybová hláška neukázala uživateli:

```bash
git rev-parse --show-toplevel 2>/dev/null
```

Pokud příkaz vrátí prázdný výstup nebo exit code != 0, **bez spouštění dalších příkazů** jednoduše oznam: „Aktuální adresář není git repozitář." a skonči.

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
