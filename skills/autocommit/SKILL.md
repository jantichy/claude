---
name: autocommit
description: Skill se použije, když uživatel zadá "/autocommit", "/autocommit on", "/autocommit off", "/autocommit status", nebo zadá "zapnout autocommit", "vypnout autocommit", "zkontrolovat autocommit". Spravuje nastavení autocommitu pro daný projekt uložené v CLAUDE.md.
argument-hint: [on|off|status]
allowed-tools: [Read, Write, Edit, Glob]
---

# Autocommit

## Co skill dělá

Zapíná/vypíná autocommit pro aktuální projekt – Claude pak v průběhu práce automaticky commituje a pushuje změny. Pravidla autocommitu (kdy commit, kdy push) jsou v `~/.claude/CLAUDE.md`, sekce *Autocommit v projektech*.

Stav v projektu = přítomnost nadpisu `## Autocommit` v projektovém `CLAUDE.md`. Projektový `CLAUDE.md` může být `<PROJECT_ROOT>/CLAUDE.md` **nebo** `<PROJECT_ROOT>/.claude/CLAUDE.md` – zkontroluj obě místa. **Globální `~/.claude/CLAUDE.md` se nepočítá nikdy**, a pozná se to **podle cesty, ne podle nadpisu**: hledá se výhradně v projektovém souboru, který sis našel v pre-flightu. Pracuješ-li přímo v repozitáři `~/.claude`, je projektovým souborem `~/.claude/.claude/CLAUDE.md` – ten kořenový je uživatelský a rozbaluje se do každé session v každém projektu, takže přepínač v něm by zapnul autocommit všude. Nadpis `## Autocommit v projektech` se od přepínače navíc schválně liší a hledá se tvar znějící přesně `## Autocommit`, ale to je jen druhá pojistka; nese to cesta. Najdeš-li sekci `Autocommit` na jiné úrovni nebo zanořenou pod jiným nadpisem – typicky pod zaniklou sekcí `## Automatické akce`, která zastřešovala jediný podnadpis –, je to chyba v tom souboru: ohlas ji a nabídni srovnání na kanonický tvar. **To platí pro projektový `CLAUDE.md`** – ten patří projektu a přepisovat v něm mimochodem cizí sekce skillu nepřísluší. **Globální `~/.claude/CLAUDE.md` je jiný případ:** definici mechanismu do něj zapisuje sám, takže starý tvar srovná rovnou a jen to oznámí (viz režim `on`).

## Co skill nedělá

- **Necommituje ani nepushuje.** Zapisuje přepínač; commituje pak Claude při běžné práci podle pravidla v `~/.claude/CLAUDE.md`, *Autocommit v projektech*.
- **Nezakládá projekt ani nenastavuje git.** Celé nastavení projektu včetně autocommitu vede `/project`, který se na něj ptá jako na jeden ze svých kroků. Tenhle skill je přepínač pro projekt, který už existuje.
- **Nedorovnává projekt na dnešní standardy.** Starý tvar sekce v projektovém `CLAUDE.md` ohlásí a srovnání nabídne, ale sám nic nemigruje – od toho je `/project` v režimu `adopt`.

## Fáze 0 – Pre-flight

Společný začátek je v `~/.claude/skills/PREFLIGHT.md`; platí z něj **body 1 a 2** – kořen projektu (včetně worktree layoutu) a projektový `CLAUDE.md`. **Bod 3 a dál neplatí**: skill nic nespouští, necommituje a na kód nesahá, takže stav pracovního stromu ani kontrakt příkazů jeho běh neovlivní.

**Vlastní odchylka:** `.git` hledej **výhradně přes Glob**, nikdy `git` přes Bash – nenulový návratový kód by vyrobil červenou chybu a zbytečně vyděsil uživatele.

## Fáze 1 – Zjisti stav

**Ve worktree layoutu sekce do kořene kontejneru nepatří** – ten je jen stub s popisem layoutu, přepínač patří do `<kontejner>/main/CLAUDE.md`. Tabulka je v `~/.claude/skills/worktree/worktree.md`, sekce *Jak si skill najde projektový adresář*.

Stav zjisti podle definice v *Co skill dělá* výš – **obě možná umístění projektového `CLAUDE.md`**, kanonické místo nadpisu i to, že nadpis v globálním souboru se nepočítá. Nalezeno → zapnutý. Nenalezeno (nebo soubor neexistuje) → vypnutý.

**Přečti si i text pod nadpisem a ověř, že netvrdí opak.** Stav nese nadpis, ne ta věta – sekce s tělem „Autocommit je vypnutý.“ tedy znamená **zapnuto**, což je přesně to nedorozumění, které stojí za ověření. Najdeš-li rozpor, **nepokračuj mlčky**: ohlas ho, řekni, jak ho čteš, a nech uživatele rozhodnout, co má platit. Sekci sice píše skill, ale ruční zásah do `CLAUDE.md` je běžný a zrovna tenhle je tichý – autocommit by se choval opačně, než co si člověk v souboru přečte.

## Fáze 2 – Proveď režim

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

## Fáze 3 – Závěr

Oznam výsledný stav a co jsi kvůli němu změnil – u `on` obě sekce, u `off` odstraněnou sekci, u `status` nic. Ohlásil-li jsi cestou starý tvar nebo rozpor mezi nadpisem a textem pod ním, zopakuj to i tady; jinak to zapadne mezi ostatní výpisy.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Autocommit je v projektu <jméno> <zapnutý|vypnutý> a zapsaný v <soubor>, můžeš pracovat dál.`
- `Nastavení hotové není – brání tomu: <konkrétní seznam>.`
