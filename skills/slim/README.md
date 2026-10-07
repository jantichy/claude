# /slim – zeštíhlení instrukcí, které se načítají do každé session

Claude Code načítá na začátku každé session váš `CLAUDE.md` a všechno, co importuje – pravidla, slovníky, doménové znalosti. Soubory tiše rostou: každé nové pravidlo si přinese zdůvodnění, doklad, zamítnuté varianty, a za pár týdnů Claude Code hlásí, že instrukce přesahují limit a zabírají kontext, který chybí na práci. Tenhle skill to změří, najde, co z toho smí pryč, co se dá říct kratší a co nemá být nikde – a po vašem odsouhlasení to udělá.

## Co umí

- **Změří celý strom načítání** – který soubor se načte, kdo ho importuje, jak hluboko, kolik zabírá a jak rychle rostl. Počítá jen importy, které Claude Code opravdu vyhodnotí.
- **Najde i soubory, které se neimportují, ale čte je skoro každá práce** – třeba normu, kterou si načítá každý skill – a bere je stejně vážně jako to, co se načítá na startu.
- **Rozdělí soubory podle toho, kdo je čte:** pravidla, která platí jen při určité práci nebo jen u některých projektů, přesune do souboru, který si načte jen ten, kdo je potřebuje, a zařídí, aby se na něj nezapomnělo.
- **Zredukuje pravidla na jádro** – nechá jen to, bez čeho by Claude jednal špatně – a předloží to vedle opatrnější varianty, obojí s čísly.
- **Škrtá vatu:** doklady, data, historii pravidel, rozvláčná zdůvodnění i to, co Claude Code ví sám.
- **Hledá duplicity mezi soubory, které se načítají spolu**, a rozhodne, kde má pravidlo zůstat – často to není smazat kopii, ale přesunout pravidlo tam, kde se jediné uplatní.
- **Navrhne zrušit pravidla, která nic nerozhodují**, a hlavně ta, **kvůli kterým soubory bobtnají** – jinak se úklid do měsíce vrátí.
- **Provede to napříč repozitáři** včetně přesměrování odkazů a ověří, že se po cestě neztratilo žádné pravidlo.
- `/slim` projde to, co se načítá v aktuálním projektu; `/slim ~/.claude/standards/rules.md` se soustředí na jeden soubor.

## Proč zrovna tenhle

- **Čísla, ne dojmy.** Každá úspora v návrhu je spočítaná z textu, který opravdu zmizí, a na konci porovnaná se skutečností.
- **Přesun jen tam, kde se text pak opravdu načte.** Pravidlo odsunuté příliš daleko od toho, co se čte pokaždé, se v praxi přestane dodržovat – skill to hlídá.
- **Nic nezmizí potichu.** Co je jen vata, škrtne sám; co mění význam, předloží po jednom k rozhodnutí. Na konci nezávislý čtenář porovná starou a novou verzi a hledá pravidlo, které se ztratilo.
- **Řeší příčinu, ne jen následek** – navrhne i pojistku, aby soubory znovu nenarostly.

## Jak se to používá

```
/slim              # celý strom načítání aktuálního projektu
/slim coding.md    # jen tenhle soubor
```

## Ukázka výstupu

| Soubor | Před | Po | Zásah |
|---|---|---|---|
| ~/.claude/standards/rules.md | 73 515 | 23 898 | pravidla o datech a delegaci na odkaz, doklady pryč |
| coding.md | 49 329 | 10 346 | návrh modelu do samostatného souboru |
| worktree.md | 14 325 | 7 109 | komprese |
| structure.md | 43 874 | 11 583 | produktové dokumenty, kola návrhu a průchody do souborů pro ty, kdo je píšou; zbytek na jádro |

**Součet:** 246 500 → 123 754 znaků ve 12 souborech · limit 150 000 · pod limitem

## Co nedělá

- **Neukazuje jen obsazení kontextu** – to dělá vestavěné `/context`, a skill ho k tomu i použije.
- **Nehledá rozpory v dokumentaci**, jen místo.
- **Nevypíná pluginy ani konektory sám** – navrhne to.

## Jak si ho nainstalovat

> Jdi na https://github.com/jantichy/claude/tree/main/skills/slim
> a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.

Skill si bere pomocné skripty ze sdílených souborů `skills/links.py` a `skills/order.py` a k ověření pouští typ subagenta `reader` – vezměte si proto z https://github.com/jantichy/claude/tree/main/skills i ty dva skripty a z https://github.com/jantichy/claude/tree/main/agents definice typů subagentů do `~/.claude/agents/`.

---

### Požadavky a omezení

Python 3 a git. Úsporu ukáže `/context` až v nové session – instrukce se načítají při startu. Konektory z účtu na claude.ai se lokální konfigurací vypnout nedají.
