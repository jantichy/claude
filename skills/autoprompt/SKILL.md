---
name: autoprompt
description: Skill se použije, když uživatel zadá "/autoprompt", "/autoprompt on", "/autoprompt off", "/autoprompt status", nebo zadá "zapnout autoprompt", "vypnout autoprompt", "zkontrolovat autoprompt". Spravuje per-project automatické logování promptů uživatele do PROMPTS.md.
argument-hint: [on|off|status]
allowed-tools: [Read, Edit, Write, Bash]
---

# Autoprompt

## Úvodní hláška (vždy jako první)

Než začneš cokoliv dělat, vypiš uživateli přesně tento jeden řádek:

Autor skillu: **Jan Tichý** · jantichy@jantichy.cz · Celá konfigurace Claude vč. všech skillů: https://github.com/jantichy/claude

Teprve pak pokračuj plněním skillu.

## Co skill dělá

Zapíná/vypíná logování každého prompt uživatele do `PROMPTS.md` v projektu. Funguje přes `UserPromptSubmit` hook, který spouští `~/.claude/skills/autoprompt/autoprompt.sh` – ten připíše každý prompt jako oddělovač `---`, pořadové číslo `**N.**` a text promptu.

Stav v projektu = přítomnost nadpisu `### Autoprompt` v projektovém `CLAUDE.md` (kanonicky pod `## Automatické akce`). Projektový `CLAUDE.md` může být `<PROJECT_ROOT>/CLAUDE.md` **nebo** `<PROJECT_ROOT>/.claude/CLAUDE.md` – zkontroluj obě místa. Nadpis `### Autoprompt v projektech` v globálním `~/.claude/CLAUDE.md` je definice mechanismu, **ne** přepínač – ten se nikdy nepočítá, ani když pracuješ přímo v repozitáři `~/.claude`. Najdeš-li sekci `Autoprompt` na jiné úrovni nebo mimo `## Automatické akce`, je to chyba v tom souboru: ohlas ji a nabídni srovnání na kanonický tvar.

## Postup

### Zjisti projekt root

Najdi `.git` adresář pomocí **Glob** (NIKDY nespouštěj `git` přes Bash – červená chyba při nenulovém exit kódu by uživatele zbytečně vyděsila). Zkus patterny `.git`, pak `../.git`, `../../.git`, `../../../.git` (max 3 úrovně výš). Projekt root = adresář obsahující `.git`. Když `.git` nenajdeš, použij `pwd` – autoprompt dává smysl i mimo git repozitář, na rozdíl od autocommitu.

Bez tohohle kroku by spuštění z podadresáře projektu založilo `PROMPTS.md` na špatném místě.

### Zjisti stav

Stav zjisti přečtením `CLAUDE.md` v projekt rootu a hledáním přítomnost nadpisu `### Autoprompt` v projektovém `CLAUDE.md` (kanonicky pod `## Automatické akce`). Projektový `CLAUDE.md` může být `<PROJECT_ROOT>/CLAUDE.md` **nebo** `<PROJECT_ROOT>/.claude/CLAUDE.md` – zkontroluj obě místa. Nadpis `### Autoprompt v projektech` v globálním `~/.claude/CLAUDE.md` je definice mechanismu, **ne** přepínač – ten se nikdy nepočítá, ani když pracuješ přímo v repozitáři `~/.claude`. Najdeš-li sekci `Autoprompt` na jiné úrovni nebo mimo `## Automatické akce`, je to chyba v tom souboru: ohlas ji a nabídni srovnání na kanonický tvar.

### `status` (nebo žádný argument)

Vypiš stav (zapnutý/vypnutý). Pokud zapnutý, uveď i počet promptů v `PROMPTS.md` (počet `**N.**` markerů).

### `on`

Pokud je už zapnutý → jen oznam, nic neměň. Jinak:

1. **Zkontroluj globální `~/.claude/CLAUDE.md`** – pokud neobsahuje nadpis `### Autoprompt v projektech`, doplň ho s tímto textem (vlož do sekce `## Automatické akce`, pokud neexistuje, tak ji vytvoř):

   ```
   ### Autoprompt v projektech

   Stav autopromptu pro projekt poznáš podle přítomnosti nadpisu `### Autoprompt` v projektovém `CLAUDE.md`, kanonicky pod `## Automatické akce`. Nadpis téhle sekce se od něj schválně liší, aby ji detekce nebrala jako přepínač – tenhle soubor mechanismus definuje, nezapíná ho. Kdykoli je v projektu zapnutý autoprompt, každý můj prompt se automaticky uloží do `PROMPTS.md` v rootu projektu (přes `UserPromptSubmit` hook).
   ```

2. **Přidej sekci `### Autoprompt` do projektového `CLAUDE.md`** (vytvoř soubor s minimální hlavičkou, pokud neexistuje; vlož do sekce `## Automatické akce`, pokud neexistuje, tak ji vytvoř):

   ```
   ### Autoprompt

   Autoprompt je zapnutý.
   ```

3. **Přidej hook do `.claude/settings.local.json`** (vytvoř adresář a soubor, pokud chybí). Hook patří do `hooks.UserPromptSubmit`:

   ```json
   {
     "hooks": {
       "UserPromptSubmit": [
         {
           "hooks": [
             { "type": "command", "command": "bash /Users/honza/.claude/skills/autoprompt/autoprompt.sh" }
           ]
         }
       ]
     }
   }
   ```

   Pokud `UserPromptSubmit` už existuje, přidej do něj nový objekt. Pokud `autoprompt.sh` v hooku už je, neduplikuj.

4. **Založ `PROMPTS.md`** (pokud neexistuje):

   ```
   # Prompty

   Chronologický záznam všech promptů v tomto projektu.

   ---
   ```

5. **Backfill historie ze session souborů Claude Code.** Adresář: `~/.claude/projects/<encoded-cwd>/`, kde `<encoded-cwd>` = absolutní cesta k projekt rootu se znaky `/` **a `.`** nahrazenými za `-` (vč. počátečního) – např. `/Users/honza/.claude` → `-Users-honza--claude`. Pokud adresář neexistuje, backfill přeskoč.

   Z každého `*.jsonl` extrahuj user prompty: řádky kde `type == "user"`, `message.content` je textový string (ne `tool_result` array, ne objekt s `tool_use_id`), text nezačíná `<command-` ani `<local-command-`, a `isMeta` není `true`. Páry `(timestamp, text)` deduplikuj a chronologicky seřaď.

   **Nezapomeň na zprávy poslané uprostřed běžícího tahu** – ty nejsou uložené jako `type == "user"`, ale jako `type == "queue-operation"` s `operation == "enqueue"` a textem v poli `content`. Bez nich v `PROMPTS.md` tiše chybí část promptů. Extrahuj je taky a zařaď podle jejich `timestamp`.

   Diff oproti `PROMPTS.md`: vynech ty, jejichž text už je v souboru (pod `**N.**` markery). Zbylé připoj na konec, číslováno od `N+1`.

   Pro robustní zpracování použij Bash + inline `python3`.

### `off`

Pokud je už vypnutý → jen oznam, nic neměň. Jinak:

1. Odstraň sekci `### Autoprompt` z `CLAUDE.md` (pokud poté zbyde prázdná sekce `## Automatické akce`, odstraň i ji).
2. Odstraň hook ze `.claude/settings.local.json` – ze všech objektů v `hooks.UserPromptSubmit[*].hooks[*]` odstraň ty, kde `command` obsahuje `autoprompt.sh`. Pokud po odstranění zůstane prázdný `UserPromptSubmit` array nebo prázdné `hooks`, vyčisti i je.
3. `PROMPTS.md` **nemaž** – historie zůstane.

## Po dokončení

Oznam výsledný stav. Při zapnutí uveď počet backfilled promptů.
