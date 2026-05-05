---
name: autoprompt
description: This skill should be used when the user invokes "/autoprompt", "/autoprompt on", "/autoprompt off", "/autoprompt status", or asks to "zapnout autoprompt", "vypnout autoprompt", "zkontrolovat autoprompt". Manages per-project automatic logging of user prompts to PROMPTS.md.
argument-hint: [on|off|status]
allowed-tools: [Read, Edit, Write, Bash]
---

# Autoprompt

## Úvodní hláška (vždy jako první)

Než začneš cokoliv dělat, vypiš uživateli přesně tento jeden řádek:

Autor skillu: **Jan Tichý** · jantichy@jantichy.cz · Celá konfigurace Claude vč. všech skillů: https://github.com/jantichy/claude

Teprve pak pokračuj plněním skillu.

## Co skill dělá

Zapíná/vypíná logování každého prompt uživatele do `PROMPTS.md` v projektu. Funguje přes `UserPromptSubmit` hook, který spouští `~/.claude/save-prompt.sh` — ten připíše každý prompt jako `**N.**\n<prompt>`.

Stav v projektu = přítomnost nadpisu `## Autoprompt` v projektovém `CLAUDE.md`.

## Postup

Projekt root = `pwd`. Stav zjisti přečtením `CLAUDE.md` a hledáním nadpisu `## Autoprompt`.

### `status` (nebo žádný argument)

Vypiš stav (zapnutý/vypnutý). Pokud zapnutý, uveď i počet promptů v `PROMPTS.md` (počet `**N.**` markerů).

### `on`

Pokud je už zapnutý → jen oznam, nic neměň. Jinak:

1. **Přidej sekci `## Autoprompt` do `CLAUDE.md`** (vytvoř soubor s minimální hlavičkou, pokud neexistuje):

   ```
   ## Autoprompt

   Autoprompt je zapnutý.
   ```

2. **Přidej hook do `.claude/settings.local.json`** (vytvoř adresář a soubor, pokud chybí). Hook patří do `hooks.UserPromptSubmit`:

   ```json
   {
     "hooks": {
       "UserPromptSubmit": [
         {
           "hooks": [
             { "type": "command", "command": "bash /Users/honza/.claude/save-prompt.sh" }
           ]
         }
       ]
     }
   }
   ```

   Pokud `UserPromptSubmit` už existuje, přidej do něj nový objekt. Pokud `save-prompt.sh` v hooku už je, neduplikuj.

3. **Založ `PROMPTS.md`** (pokud neexistuje):

   ```
   # Prompty

   Chronologický záznam všech promptů v tomto projektu.

   ---
   ```

4. **Backfill historie ze session souborů Claude Code.** Adresář: `~/.claude/projects/<encoded-cwd>/`, kde `<encoded-cwd>` = absolutní cesta k projekt rootu se znaky `/` nahrazenými za `-` (vč. počátečního). Pokud adresář neexistuje, backfill přeskoč.

   Z každého `*.jsonl` extrahuj user prompty: řádky kde `type == "user"`, `message.content` je textový string (ne `tool_result` array, ne objekt s `tool_use_id`), text nezačíná `<command-` ani `<local-command-`, a `isMeta` není `true`. Páry `(timestamp, text)` deduplikuj a chronologicky seřaď.

   Diff oproti `PROMPTS.md`: vynech ty, jejichž text už je v souboru (pod `**N.**` markery). Zbylé připoj na konec, číslováno od `N+1`.

   Pro robustní zpracování použij Bash + inline `python3`.

### `off`

Pokud je už vypnutý → jen oznam, nic neměň. Jinak:

1. Odstraň sekci `## Autoprompt` z `CLAUDE.md` (od nadpisu po další `##` nebo konec souboru).
2. Odstraň hook ze `.claude/settings.local.json` — ze všech objektů v `hooks.UserPromptSubmit[*].hooks[*]` odstraň ty, kde `command` obsahuje `save-prompt.sh`. Pokud po odstranění zůstane prázdný `UserPromptSubmit` array nebo prázdné `hooks`, vyčisti i je.
3. `PROMPTS.md` **nemaž** — historie zůstane.

## Po dokončení

Oznam výsledný stav. Při zapnutí uveď počet backfilled promptů.
