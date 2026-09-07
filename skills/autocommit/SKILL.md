---
name: autocommit
description: Skill se použije, když uživatel zadá "/autocommit", "/autocommit on", "/autocommit off", "/autocommit status", nebo zadá "zapnout autocommit", "vypnout autocommit", "zkontrolovat autocommit". Spravuje nastavení autocommitu pro daný projekt uložené v CLAUDE.md.
argument-hint: [on|off|status]
allowed-tools: [Read, Write, Edit, Glob]
---

# Autocommit

## Co skill dělá

Zapíná/vypíná autocommit pro aktuální projekt – Claude pak v průběhu práce automaticky commituje a pushuje změny. Pravidla autocommitu (kdy commit, kdy push) jsou v `~/.claude/CLAUDE.md`, sekce *Autocommit v projektech*.

Stav v projektu = přítomnost nadpisu `## Autocommit` v projektovém `CLAUDE.md`. Projektový `CLAUDE.md` může být `<PROJECT_ROOT>/CLAUDE.md` **nebo** `<PROJECT_ROOT>/.claude/CLAUDE.md` – zkontroluj obě místa. Nadpis `## Autocommit v projektech` v globálním `~/.claude/CLAUDE.md` je definice mechanismu, **ne** přepínač – ten se nikdy nepočítá, ani když pracuješ přímo v repozitáři `~/.claude`. Hledá se tedy nadpis znějící přesně `## Autocommit`. Najdeš-li sekci `Autocommit` na jiné úrovni nebo zanořenou pod jiným nadpisem – typicky pod zaniklou sekcí `## Automatické akce`, která zastřešovala jediný podnadpis –, je to chyba v tom souboru: ohlas ji a nabídni srovnání na kanonický tvar. **To platí pro projektový `CLAUDE.md`** – ten patří projektu a přepisovat v něm mimochodem cizí sekce skillu nepřísluší. **Globální `~/.claude/CLAUDE.md` je jiný případ:** definici mechanismu do něj zapisuje sám, takže starý tvar srovná rovnou a jen to oznámí (viz režim `on`).

## Postup

### Zjisti projekt root

Najdi `.git` pomocí **Glob** (NIKDY nespouštěj `git` přes Bash – červená chyba při nenulovém exit kódu by uživatele zbytečně vyděsila). Zkus patterny `.git`, pak `../.git`, `../../.git`, `../../../.git` (max 3 úrovně výš). Projekt root = adresář obsahující `.git`.

**Pozor na worktree layout.** Najdeš-li vedle `.git` také `.bare/`, stojíš v kořeni kontejneru, který není pracovní strom – projektový `CLAUDE.md` je pak `<kontejner>/main/CLAUDE.md`, ne ten v kořeni. Ten v kořeni je jen stub s popisem layoutu a sekce `## Autocommit` do něj **nepatří**. Pravidlo i s tabulkou je v `~/Dev/context/worktree/worktree.md`, sekce *Jak si skill najde projektový adresář*.

Pokud `.git` nenajdeš, oznam „Aktuální adresář není git repozitář.“ a skonči **bez jakéhokoliv dalšího příkazu**.

### Zjisti stav

Stav zjisti podle definice v *Co skill dělá* výš – **obě možná umístění projektového `CLAUDE.md`**, kanonické místo nadpisu i to, že nadpis v globálním souboru se nepočítá. Nalezeno → zapnutý. Nenalezeno (nebo soubor neexistuje) → vypnutý.

**Přečti si i text pod nadpisem a ověř, že netvrdí opak.** Stav nese nadpis, ne ta věta – sekce s tělem „Autocommit je vypnutý.“ tedy znamená **zapnuto**, což je přesně to nedorozumění, které stojí za ověření. Najdeš-li rozpor, **nepokračuj mlčky**: ohlas ho, řekni, jak ho čteš, a nech uživatele rozhodnout, co má platit. Sekci sice píše skill, ale ruční zásah do `CLAUDE.md` je běžný a zrovna tenhle je tichý – autocommit by se choval opačně, než co si člověk v souboru přečte.

### `status` (nebo žádný argument)

Vypiš stav (zapnutý/vypnutý).

### `on`

Pokud je už zapnutý → jen oznam, nic neměň. Jinak:

1. **Zkontroluj globální `~/.claude/CLAUDE.md`** – pokud neobsahuje nadpis `## Autocommit v projektech`, doplň ho s tímto textem. **Stojí-li tam starý tvar** – `### Autocommit v projektech`, typicky pod zastřešující sekcí `## Automatické akce` –, druhou sekci nepřidávej: povyš nadpis na druhou úroveň, text srovnej podle šablony níž a **oznam to**. Zastřešující sekci pak zruš, ale jen **nezbyl-li pod ní jiný podnadpis** – v cizí instalaci tam může viset něco dalšího. Ptát se tu na svolení netřeba: je to sekce, kterou skill sám zapisuje, a dvě definice téhož mechanismu vedle sebe si dřív nebo později začnou odporovat.

   ```
   ## Autocommit v projektech

   Stav autocommitu pro projekt poznáš podle přítomnosti nadpisu `## Autocommit` v projektovém `CLAUDE.md`. Nadpis téhle sekce se od něj schválně liší, aby ji detekce nebrala jako přepínač – tenhle soubor mechanismus definuje, nezapíná ho. Kdykoli je v projektu zapnutý autocommit, commituj po každé zásadní ucelené změně (ne po každém dílčím kroku, ale po každém logickém celku). Pokud má repo nastavený nějaký git remote, po commitu hned pushuj.
   ```

2. **Přidej sekci `## Autocommit` do projektového `CLAUDE.md`** (vytvoř soubor s minimální hlavičkou, pokud neexistuje):

   ```
   ## Autocommit

   Autocommit je zapnutý.
   ```

### `off`

Pokud je už vypnutý → jen oznam, nic neměň. Jinak odstraň sekci `## Autocommit` z projektového `CLAUDE.md`.

## Po dokončení

Oznam výsledný stav.
