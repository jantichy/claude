---
name: autocommit
description: Skill se použije, když uživatel zadá "/autocommit", "/autocommit enable", "/autocommit disable", "/autocommit status", nebo zadá "zapnout autocommit", "vypnout autocommit", "zkontrolovat autocommit". Spravuje nastavení autocommitu pro daný projekt uložené v jeho CLAUDE.md.
argument-hint: [enable|disable|status]
allowed-tools: [Read, Write, Edit, Glob]
---

# Autocommit

## Co skill dělá

Zapíná a vypíná autocommit pro aktuální projekt – Claude pak v průběhu práce automaticky commituje a pushuje změny. **Vlastní pravidla drží `~/.claude/skills/autocommit/autocommit.md`**: kdy commit, kdy push. Skill ten soubor **importuje do projektu**, takže platí v každé jeho session, aniž ho kdo vyvolá. Ta cesta je závazné rozhraní, importují ji projektové `CLAUDE.md` – nesmí se měnit tiše.

Stav v projektu = přítomnost nadpisu `## Autocommit` v projektovém `CLAUDE.md`. Projektový `CLAUDE.md` může být `<project_root>/CLAUDE.md` **nebo** `<project_root>/.claude/CLAUDE.md` – zkontroluj obě místa. **Globální `~/.claude/CLAUDE.md` se nepočítá nikdy**, a pozná se to **podle cesty, ne podle nadpisu**: hledá se výhradně v projektovém souboru, který sis našel v přípravě. Pracuješ-li přímo v repozitáři `~/.claude`, je projektovým souborem `~/.claude/.claude/CLAUDE.md` – ten kořenový je uživatelský a rozbaluje se do každé session v každém projektu, takže přepínač v něm by zapnul autocommit všude.

**Stav nese nadpis, ne text pod ním.** Sekce s tělem „Autocommit je vypnutý.“ tedy znamená **zapnuto** – a je to přesně to nedorozumění, které stojí za ověření. Najdeš-li rozpor, **nepokračuj mlčky**: ohlas ho, řekni, jak ho čteš, a nech uživatele rozhodnout, co má platit. Sekci sice píše skill, ale ruční zásah do `CLAUDE.md` je běžný a zrovna tenhle je tichý.

## Co skill nedělá

- **Necommituje ani nepushuje.** Zapisuje přepínač; commituje pak Claude při běžné práci podle pravidel v `~/.claude/skills/autocommit/autocommit.md`.
- **Nezakládá projekt ani nenastavuje git.** Celé nastavení projektu včetně autocommitu vede `/project`, který se na něj ptá jako na jeden ze svých kroků. Tenhle skill je přepínač pro projekt, který už existuje.
- **Nedorovnává projekt na dnešní standardy.** Doplní jen chybějící import ve vlastní sekci (viz *Sekce bez importu* níž), nic dalšího nemigruje – od toho je `/project` v režimu `adopt`.

## Fáze 0 – Příprava

Společný začátek je v `~/.claude/skills/preflight.md`; platí z něj **body 1 a 2** – kořen projektu (včetně worktree layoutu) a projektový `CLAUDE.md`. **Bod 3 a dál neplatí**: skill nic nespouští, necommituje a na kód nesahá, takže stav pracovního stromu ani kontrakt příkazů jeho běh neovlivní.

**Vlastní odchylka:** `.git` hledej **výhradně přes Glob**, nikdy `git` přes Bash – nenulový návratový kód by vyrobil červenou chybu a zbytečně vyděsil uživatele.

## Fáze 1 – Zjisti stav

**Ve worktree layoutu sekce do kořene kontejneru nepatří** – ten je jen rozcestník s popisem layoutu, přepínač patří do `<container>/main/CLAUDE.md`. Tabulka je v `~/.claude/standards/worktree.md`, sekce *Jak si skill najde projektový adresář*.

Stav zjisti podle definice v *Co skill dělá* výš – **obě možná umístění projektového `CLAUDE.md`**, kanonické místo nadpisu i to, že nadpis v globálním souboru se nepočítá. Nalezeno → zapnutý. Nenalezeno (nebo soubor neexistuje) → vypnutý.

Je-li zapnutý, podívej se rovnou i na to, jestli sekce nese import – viz *Sekce bez importu* níž.

## Fáze 2 – Proveď režim

### `status` (nebo žádný argument)

Vypiš stav (zapnutý/vypnutý). Je-li zapnutý starým tvarem, řekni to a nabídni srovnání.

### `enable`

Je-li už zapnutý → jen oznam a zkontroluj tvar zápisu, nic dalšího neměň. Jinak přidej do projektového `CLAUDE.md` tuhle sekci (soubor s minimální hlavičkou vytvoř, pokud neexistuje):

```
## Autocommit

Autocommit je zapnutý.

@~/.claude/skills/autocommit/autocommit.md
```

Import je **nutná část zápisu**, ne ozdoba: bez něj má projekt přepínač, ale Claude v něm nemá pravidlo, podle kterého by se choval.

### `disable`

Je-li už vypnutý → jen oznam, nic neměň. Jinak odstraň celou sekci `## Autocommit` z projektového `CLAUDE.md` – tedy včetně řádku s importem.

### Sekce bez importu

Najdeš-li zapnutou sekci `## Autocommit` bez řádku s importem, doplň ho bez ptaní na svolení a oznam to: je to zápis, který skill sám vyrábí, a bez importu je to přepínač, který nic nespíná. Do zbytku projektového `CLAUDE.md` se nesahá – ten patří projektu a přepisovat v něm mimochodem cizí sekce skillu nepřísluší.

## Fáze 3 – Závěr

Oznam výsledný stav a co jsi kvůli němu změnil – u `enable` a `disable` konkrétní soubor a sekci, u `status` nic. Doplnil-li jsi cestou import nebo ohlásil rozpor mezi nadpisem a textem pod ním, zopakuj to i tady; jinak to zapadne mezi ostatní výpisy.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Autocommit je v projektu <jméno> <zapnutý|vypnutý> a zapsaný v <soubor>, můžeš pracovat dál.`
- `Nastavení hotové není – brání tomu: <konkrétní seznam>.`
