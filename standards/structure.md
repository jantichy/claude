# Standardní struktura projektu

Konvence pro každý projekt, kde se něco průběžně rozhoduje a vyvíjí; jednorázový scratch ani cizí repozitář, do kterého jen nahlížíš, ji nepotřebuje. Zakládá a udržuje ji `/project`. Tenhle soubor konvenci **definuje**; projektový `CLAUDE.md` jen deklaruje, že ji projekt drží, a popisuje odchylky.

## Dva režimy umístění

Standardní soubory jsou vždycky tytéž. **Kde leží, je volba ze dvou rovnocenných režimů:**

```
režim  docs/                       režim  root
<project>/                         <project>/
├── CLAUDE.md                      ├── CLAUDE.md
├── README.md                      ├── README.md
└── docs/                          ├── todo.md
    ├── todo.md                    ├── backlog.md
    ├── backlog.md                 ├── done.md
    ├── done.md                    ├── decisions.md
    ├── decisions.md               └── rules.md
    └── rules.md
```

**Výchozí je `docs/`**, který odděluje meta-vrstvu od vlastní práce; `root` sedí na knowledge base a malé projekty, kde by `docs/` byl prázdný obal. Režim se volí jednou při `/project` a pak se drží – míchat obojí je nepořádek.

**Konvence zápisu.** Obecné texty (tenhle soubor, `~/.claude/standards/rules.md`, skilly) píšou cesty v podobě `docs/todo.md` a myslí tím soubor na místě podle režimu projektu. Texty o jednom projektu – jeho `CLAUDE.md` a `README.md` – píšou skutečnou cestu.

### Deklarace režimu

Režim říká řádek v bloku metadat projektového `CLAUDE.md`:

```
- **Struktura:** docs/
```

Bez něj se režim odvodí z umístění souborů; deklarace je ale závazná – podle ní se zakládá další soubor.

### Které soubory vůbec vzniknou

Povinný je jen **`CLAUDE.md`**. Zbytek:

| Soubor | Zakládá se |
|---|---|
| `README.md`, `decisions.md`, `rules.md` | výběrem při `/project` (výchozí ano) |
| `todo.md` + `backlog.md` + `done.md` | výběrem při `/project`, **jen jako trojice** |
| `requirements.md`, `architecture.md`, `plan.md`, tematické dokumenty kol, produktové podklady (`demand.md`, `competition.md`, `risks.md`, `scenarios.md`, `glossary.md`, `pricing.md`, `operation.md`) | až prací – co v nich smí stát, drží **`~/.claude/standards/product.md`**; načti si ho, než do některého z nich zapíšeš |
| `research/` | až je co uložit |
| testy | s první kontrolou – kam patří, drží `~/Dev/context/coding/quality.md`, *Vrstvy kontroly a co do které patří* |

Nezaložený soubor **není odchylka** – prázdný `decisions.md` u projektu, kde se nic nerozhoduje, je horší než žádný. Běhový stav skillů v `.claude/run/` standardní soubor není (`~/.claude/skills/skills.md`, *Běhový stav*).

**Ve worktree layoutu** (`~/.claude/standards/worktree.md`) je projekt pracovní adresář větve, takže celá struktura žije v `main/` – i v režimu `root`. Kořen kontejneru není pracovní strom a nese jen rozcestník.

---

## Co patří do kterého souboru

### `CLAUDE.md`

Instrukce pro Clauda v tomhle projektu. **Začíná blokem metadat**, kterým se projekt představuje navenek:

```
# Rezervační systém

Rezervační systém pro školení, konference a webináře – správa událostí, účastníků, objednávek a faktur.

- **Slug:** `rezervace`
- **Struktura:** docs/
- **Web:** https://rezervace.example.cz
- **Repozitář:** https://github.com/jantichy/rezervace
```

Nadpis je **lidský název** („Rezervační systém“, ne `rezervace`), odstavec pod ním **popisek** – jedna věta bez odkazů a formátování do 350 znaků (limit GitHub description). Slug je adresář a název repozitáře, Struktura režim umístění. Web a Repozitář se uvádějí, jen když existují – jinak řádek vynech, nepiš „zatím není“.

Blok je **kanonický zdroj** názvu a popisku. Odvozují se z něj nadpis a první odstavec `README.md` (tam se popisek smí rozvést) a Repository details na GitHubu (`gh repo edit <owner>/<slug> -d "<description>" -h "<web>"`). **Změní-li se název, popisek nebo URL, propiš to hned na všechna tři místa.**

**Import musí stát holý, ne v apostrofech.** `@~/cesta/soubor.md` uvnitř code spanu se nenačte, a to tiše. Chceš-li cestu vysázet jako kód, napiš ji dvakrát; odkaz, který se importovat nemá, naopak v apostrofech nech.

Další sekce:

- **`## Kontrakt příkazů`** – **má ho každý projekt, ve kterém se něco spouští**: čím se tam spouštějí abstraktní kroky (`test`, `typecheck`, `lint`, `build`…). Zakládá ho `/project`, čte průběžná kontrola a skilly, které pouštějí testy; seznam klíčů drží `~/Dev/context/coding/quality.md`, *Kontrakt příkazů*. Projekt bez kódu ho nemá.
- **`## Zákazy`** – na co model nesahá nebo co nedělá bez ptaní, a proč. **Hranici drží `permissions` v `.claude/settings.json`** – co se nesmí vůbec, do `deny`, co jen bez ptaní, do `ask`; sekce je seznam s důvody a zákaz bez mechanismu se v ní označí jako jen napsaný. Zakládá ji `/project`, a jen má-li projekt co zakázat.
- **`## Nasazení`** – jak se projekt dostane do produkce, hlavně která větev je nasazovací. Zakládá ji `/project` nebo první `/release`.
- **`## Review` a `## Consistency`** – nálezy vyhodnocené jako „neopravovat“, aby se nehlásily znovu. Do první píší `/review` i `/attack` (formát drží `~/.claude/skills/review/SKILL.md`, *Kapitola `## Review`*), do druhé `/consistency`. Píší je skilly, ne člověk.

Zbytek – autocommit, paměťová politika, typ projektu, doménové importy – zakládá `/project`.

### `README.md`

**Pro člověka, který sem přijde poprvé, ne pro Clauda.** Krátký úvod: co projekt je a k čemu slouží, co kde najde, jak se používá a spouští a jak se s ním jako celkem pracuje. Nadpis a první odstavec jsou z bloku metadat v `CLAUDE.md`. Musí vždy odpovídat skutečnému stavu.

**Každá součást představená vlastním nadpisem dostane právě jeden odstavec** – co to je a k čemu je. Platí pro každý druh součásti: skill, modul, nástroj, skript, hook, adresář **i dokument**. Obrázek nebo ukázka výstupu pod odstavcem je jediná výjimka.

Test: **jde ta věta škrtnout, aniž čtenář přestane vědět, k čemu ta věc je?** Pak tam nepatří. Nepatří tam tedy:

- příběh vzniku a čísla dokládající užitečnost,
- zdůvodnění a obhajoba návrhu → `docs/decisions.md`,
- výčet fází, parametrů a vnitřních kroků → dokumentace té věci,
- instrukce pro Clauda (pravidla práce, konvence, povinnosti) → `CLAUDE.md`, **ani odkazem** na ně,
- principy → `docs/rules.md`, co zbývá → `docs/todo.md`.

Postup, který potřebuje znát člověk pracující v projektu sám (jak to spustit, kam uložit podklad), do README patří, i když ho pak vykonává Claude – většina takových vět je ale ve skutečnosti pokyn pro Clauda a patří jinam.

### `todo.md`

Co padne mimo aktuální rozsah, ale **je rozhodnuté, že se to udělá** – úkol, otázka, kterou je nutné zodpovědět, rozhodnutí, které padnout musí. **S celou úvahou**, ne jako holá odrážka. Odklad po termín („až po spuštění“, „ve druhé fázi“) z úkolu nápad nedělá; nápad, o kterém nikdo nerozhodl, patří do `backlog.md`.

- **Má-li položka smysl až od určitého dne**, napiš **hned za název** `od <YYYY-MM-DD>` – `/next` ji do té doby nenabídne, jen zmíní. Datum uvnitř popisu odklad nezakládá. Je to odstup, ne termín.
- **Drží jen nehotové položky.** Hotové **přesuň hned do `done.md`**.
- **`## Parkované v session`** – bod odložený v rámci session; po vyřešení se maže, prázdná sekce se ruší.
- **`## Přerušený běh`** – zbytek fronty běhu přerušeného kvůli nabytému kontextu (nálezy, úkoly). Stojí první v souboru a `/next` ji nabízí přednostně; tvar položky drží `~/.claude/skills/handoff.md`, *Přerušení dlouhého průchodu*. Vypořádaná položka jde do `done.md`, jen je-li to odvedená práce, jinak se maže; prázdná sekce se ruší.
- **`## Kola návrhu`** – mapa kol návrhu; tvar drží `~/.claude/skills/architect/rounds.md`.

### `backlog.md`

**Zásobník nezávazných nápadů** – co by s produktem někdy šlo udělat, ale **nikdo se nerozhodl**. Hranice proti `todo.md` jde po rozhodnutí, ne po termínu.

- **Položka odejde jen dvěma cestami:** rozhodne-li se, že se udělá, **přesune se do `todo.md`** nebo do zadání; rozhodne-li se, že ne, **smaže se** – a bylo-li zamítnuté s odůvodněním, jde to do `decisions.md`. Neodškrtává se, nestárne a podle stáří se neuklízí.
- **Nepatří sem nález kontroly** (`/review`, `/attack`, `/consistency`, `/oponent`) – odložený jde do `todo.md`, zamítnutý do `## Review` v `CLAUDE.md`; třetí možnost není – „nepálí nás to“ je zamítnutí, ne odklad. Nepatří sem ani parkovaný bod session.
- **Nápad smí být rozepsaný do detailu** i se zavrženými cestami. Jeho vnitřní závěry **nejsou rozhodnutí projektu** – platí jen *kdyby* se dělal; do `decisions.md` patří jen závěr, který váže **dnešní** návrh.
- **Vybírá z něj jen `/specify`** před novým zadáním; `/next` ho při prázdné frontě jen vypíše. O přesunu každé položky rozhoduje uživatel.
- Člení se podle témat; pořadí nic neurčuje.
- **Chybí-li a je co zapsat, založ ho** a řekni to. Existuje jen spolu s `todo.md`.

### `decisions.md`

**Konkrétní rozhodnutí a cesta k nim:** problém, varianty, proč vyhrála tahle a proč padly ostatní. Zapisuj hned, jak rozhodnutí padne. Změna názoru se nepřepisuje – přibude revize s odůvodněním.

- **Nejstarší nahoře, nový zápis na konec** své sekce – i bez dat (pořadí vzniku); kapitoly tematicky členěného souboru drží svou logiku.
- **Datum patří do prvního odstavce kapitoly, ne do nadpisu** (`**Rozhodnuto 15. 9. 2026.**`) – nadpis je kotva a datum v ní se při opravě tiše rozbije. Počet v nadpisu katalogu („Akce nad objednávkou (9)“) se toho netýká.
- **`## Co proklouzlo`** – defekty, které prošly všemi kontrolami; tvar drží `~/.claude/skills/release/SKILL.md`, *Když chyba projde vším*.
- **Kapitola kola návrhu** se píše bez čísla – `~/.claude/skills/architect/rounds.md`, *V `decisions.md`*.

### `done.md`

**Hotové položky přesunuté z `todo.md`. Nikdy se nemažou.**

- Přesouvej **průběžně**, ve chvíli, kdy je položka hotová.
- **Nejstarší nahoře**, nové na konec sekce; **datum dokončení** za názvem `(2026-08-28)`, vyrobené `date +%F`.
- **Zrcadlí sekce `todo.md`** – položka jde do sekce, do které patřila.
- **Přesouvá se úkol, ne odškrtnutý krok uvnitř něj** – odškrtnuté řádky checklistu zůstávají u nedokončené položky.
- **`## Průchody životním cyklem`** – záznamy běhů kontrolních kroků; tvar a kdo zapisuje drží `~/.claude/standards/lifecycle.md`, *Záznam průchodu v `done.md`*. **`## Kola návrhu`** – `~/.claude/skills/architect/rounds.md`. Běhový stav skillů sem nepatří.

Existuje jen spolu s `todo.md`.

### `research/`

**Cizí podklady, ze kterých projekt vychází** – brief, zápis, export, PDF od klienta. Zakládá se, až je co uložit. Originály se sem **kopírují a dál nemění** (`~/.claude/standards/rules.md`, *Cizí podklady jsou read-only*); vytěžené žije jinde. Smysl je dohledatelnost.

### `rules.md`

**Obecné principy tohoto projektu** – věty, které rozhodují, ne popis systému. Vznikají z konkrétních rozhodnutí, ale zapisují se obecně; `decisions.md` drží konkrétní rozhodnutí, tady je rámec, proti kterému se rozhoduje. Patří sem **jen to, co je specifické pro projekt** – obecná pravidla jsou v `~/.claude/standards/rules.md`, doménové standardy v importované doméně, provoz worktree v `~/.claude/standards/worktree.md`.

---

## Průběžná aktualizace je povinná

Tyhle soubory doplňuj **sám, průběžně a bez vyžádání**, ve chvíli, kdy rozhodnutí padne, princip se vybrousí nebo se něco odloží – nečekej na `/cleanup` (`~/.claude/standards/rules.md`, *Pravda v souborech, ne v konverzaci*); kam zápis míří, drží tamtéž *Kam co zapsat*. Patří-li zápis jinam, přesuň ho (*Živá struktura*).

## Prázdný soubor je v pořádku

Nový projekt má `todo.md`, `backlog.md`, `done.md`, `decisions.md` a `rules.md` založené jen s nadpisem. Nevymýšlej do nich obsah dopředu.
