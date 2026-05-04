---
name: autoprompt
description: This skill should be used when the user invokes "/autoprompt", "/autoprompt on", "/autoprompt off", "/autoprompt status", or asks to "zapnout autoprompt", "vypnout autoprompt", "zkontrolovat autoprompt". Manages per-project automatic logging of user prompts to PROMPTS.md.
argument-hint: [on|off|status]
allowed-tools: [Read, Edit, Write, Bash, Glob]
---

# Autoprompt

Tento skill spravuje autoprompt nastavení pro aktuální projekt.

## Co je autoprompt

Autoprompt = každý prompt uživatele se v projektu automaticky zaloguje do `PROMPTS.md` v rootu projektu (chronologicky, číslovaně). Mechanika:

- `UserPromptSubmit` hook spouští `~/.claude/save-prompt.sh`
- Skript připíše každý nový prompt na konec `PROMPTS.md` jako `**N.**\n<prompt>`
- Tool resulty a další systémové zprávy se neukládají — jen skutečné prompty od uživatele

Stav autopromptu pro projekt poznáš podle přítomnosti nadpisu `## Autoprompt` v projektovém `CLAUDE.md`.

## Argumenty

Uživatel zavolal skill s argumenty: $ARGUMENTS

## Postup

### 1. Zjisti projekt root

**DŮLEŽITÉ:** Bash tool zobrazuje červenou chybu pro jakýkoliv nenulový exit kód. Proto NIKDY nespouštěj `git` přímo pro detekci repozitáře — vždy použij Glob tool.

Pro autoprompt nemusí projekt být git repozitář — stačí, že existuje rozumná pracovní složka. Použij `pwd` přes Bash a tu cestu považuj za projekt root. Pokud uživatel pracuje v podadresáři, doporuč přejít do rootu.

### 2. Zjisti aktuální stav

Prohledej `<PROJECT_ROOT>/CLAUDE.md` pro výskyt nadpisu `## Autoprompt`.

- Nalezeno → autoprompt je **zapnutý**
- Nenalezeno (nebo soubor neexistuje) → autoprompt je **vypnutý**

### 3. Proved akci

#### Žádný argument nebo "status"

Vypiš stav: zapnutý / vypnutý. Pokud zapnutý, řekni i kolik promptů už `PROMPTS.md` obsahuje (počet `**N.**` záznamů).

#### "on", "yes", "enable", "zapnout", "zapni"

Pokud je již zapnutý → řekni to, nic neměň.

Pokud je vypnutý, proveď v tomto pořadí:

**a) Přidej sekci `## Autoprompt` do `CLAUDE.md`**

Pokud `CLAUDE.md` neexistuje → vytvoř ho s minimální hlavičkou.

Přidej na konec souboru (s prázdným řádkem před tím):

```
## Autoprompt

Autoprompt je zapnutý.
```

**b) Přidej hook do `.claude/settings.local.json`**

Pokud `.claude/` neexistuje → vytvoř.
Pokud `.claude/settings.local.json` neexistuje → vytvoř s minimální strukturou.

Hook přidat do `hooks.UserPromptSubmit`. Příklad výsledné struktury (pokud žádný `UserPromptSubmit` hook ještě neexistuje):

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash /Users/honza/.claude/save-prompt.sh"
          }
        ]
      }
    ]
  }
}
```

Pokud už existuje pole `UserPromptSubmit`, přidej nový objekt do něj (zachovej ostatní hooky beze změny). Pokud už `save-prompt.sh` v hookech je, neduplikuj.

**c) Založ `PROMPTS.md`, pokud neexistuje**

Pokud `<PROJECT_ROOT>/PROMPTS.md` neexistuje, vytvoř ho s touto hlavičkou:

```
# Prompty

Chronologický záznam všech promptů v tomto projektu.

---
```

**d) Backfill historie**

Najdi adresář s historickými session JSONL soubory:

1. Vezmi absolutní cestu k projekt rootu (např. `/Users/honza/Dev/myproj`).
2. Encoded path = nahraď `/` za `-` (vč. počátečního). Příklad: `/Users/honza/Dev/myproj` → `-Users-honza-Dev-myproj`.
3. Adresář se sessions: `~/.claude/projects/<encoded-path>/`. Pokud neexistuje, žádná historie není — přeskoč backfill.

Z každého `*.jsonl` souboru v tom adresáři extrahuj user prompty. **Filtr je důležitý:**

- Bere jen řádky s `type: "user"` (ne `assistant`, ne `system`)
- A jen ty, kde `message.content` je **textový string** (ne `tool_result` blok ani array s `tool_use_id`)
- A jen ty, kde `message.content` nezačíná `<command-` nebo `<local-command-` (to jsou interní příkazy z UI, ne uživatelské prompty)
- Pokud existuje pole `isMeta: true`, přeskoč

Tj. **jen skutečné prompty od uživatele, které dál mění a posouvají projekt** — ne tool resulty, ne UI pomocné zprávy.

Sesbírej páry `(timestamp, prompt_text)` ze všech souborů, **deduplikuj** (občas se stejný prompt objeví ve víc resumed sessions) a seřaď chronologicky podle `timestamp`.

**Diff oproti existujícímu obsahu:** Načti aktuální `PROMPTS.md` a vytáhni z něj texty stávajících promptů (ty pod `**N.**` markery). Z extrahovaného seznamu odstraň ty, jejichž text už v `PROMPTS.md` je. Zbylé prompty přidej na konec, pokračuj číslováním od `N+1`.

Pro robustní extrakci a zápis použij Bash s python3 inline skriptem (zpracování JSONL, dedup, diff, append).

#### "off", "no", "disable", "vypnout", "vypni"

Pokud je již vypnutý → řekni to, nic neměň.

Pokud je zapnutý, proveď:

**a)** Odstraň sekci `## Autoprompt` z `CLAUDE.md` (od nadpisu po konec sekce nebo konec souboru — analogicky jako `/autocommit off`).

**b)** Odstraň hook z `.claude/settings.local.json`. Konkrétně: ze všech objektů v `hooks.UserPromptSubmit[*].hooks[*]` odstraň ty, kde `command` obsahuje `save-prompt.sh`. Pokud po odstranění zůstane prázdné `hooks` pole nebo prázdný `UserPromptSubmit` array, vyčisti i ty (čistý JSON, žádné prázdné kontejnery).

**c)** `PROMPTS.md` **nemaž** — historie zůstane, jen se do ní přestane dál psát.

### 4. Potvrď výsledek

Oznam uživateli nový (nebo beze-změnový) stav. Při zapnutí uveď, kolik promptů se backfillem doplnilo.
