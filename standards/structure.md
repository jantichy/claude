# Standardní struktura projektu

Konvence pro každý projekt, kde se něco průběžně rozhoduje a vyvíjí; jednorázový scratch ani cizí repozitář, do kterého jen nahlížíš, ji nepotřebuje. Zakládá a udržuje ji `/project`. Tenhle soubor konvenci **definuje**; projektový `CLAUDE.md` jen deklaruje, že ji projekt drží, a popisuje odchylky.

## Režimy umístění

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

**Výchozí je `docs/`**, který odděluje meta-vrstvu od vlastní práce; `root` sedí na knowledge base a malé projekty. Režim se volí jednou při `/project` a pak se drží.

**Konvence zápisu.** Obecné texty (tenhle soubor, `~/.claude/standards/rules.md`, skilly) píšou cesty v podobě `docs/todo.md` a myslí tím soubor na místě podle režimu projektu. Texty o jednom projektu – jeho `CLAUDE.md` a `README.md` – píšou skutečnou cestu.

### Operativní projekt: režim `CLAUDE.md`

Jiný druh projektu: **adresář, který patří uživateli a má jeho pořádek** (smlouvy, dokumenty), a Claude nad ním odpovídá, dohledává a na pokyn přeskupuje. Standardní soubory ani `README.md` nevznikají, Claudovy jsou jen soubory `CLAUDE.md`. **Vše ostatní je uživatelovo, i jeho poznámky v Markdownu:** dopíše se do nich jen, co uživatel řekne nebo co se dohodne, v jejich tvaru a stylu, nikdy Claudovy instrukce. Pointa: obojí zůstane jeho.

Claudova paměť jde do `CLAUDE.md` **ve složce tématu**, který si založí sám – k čemu složka je, postupy, šablony, rozhodnutí, otevřené body; data z poznámky neopisuje. Kořenový drží, co platí celému adresáři, a `## Otevřené body` bez tématu. Hotové se nevede, jen stav u tématu. **Skill, který zapisuje do `docs/…`, píše tady do `CLAUDE.md`**, `## Přerušený běh` do kořenového. Do trvalé Memory nic.

### Deklarace režimu

Režim říká řádek v bloku metadat projektového `CLAUDE.md`:

```
- **Struktura:** docs/
```

Hodnoty jsou `docs/`, `root` a `CLAUDE.md`.

Bez něj se režim odvodí z umístění souborů; deklarace je ale závazná – podle ní se zakládá další soubor.

### Které soubory vůbec vzniknou

Povinný je jen **`CLAUDE.md`**. Zbytek:

| Soubor | Zakládá se |
|---|---|
| `README.md`, `decisions.md`, `rules.md` | výběrem při `/project` (výchozí ano) |
| `todo.md` + `backlog.md` + `done.md` | výběrem při `/project`, **jen jako trojice** |
| `requirements.md`, `architecture.md`, `plan.md`, tematické dokumenty kol, produktové podklady | až prací – co v nich smí stát, drží **`~/.claude/standards/product.md`**; načti si ho, než do některého z nich zapíšeš |
| `research/` | až je co uložit |
| testy | s první kontrolou – kam patří, drží `~/Context/Coding/quality.md`, *Vrstvy kontroly a co do které patří* |

Nezaložený soubor **není odchylka** – prázdný `decisions.md` u projektu, kde se nic nerozhoduje, je horší než žádný. Běhový stav skillů v `.claude/run/` standardní soubor není (`~/.claude/skills/skills.md`, *Běhový stav*).

**Ve worktree layoutu** (`~/.claude/standards/worktree.md`) je projekt pracovní adresář větve, takže celá struktura žije v `main/` – i v režimu `root`. Kořen kontejneru nese jen rozcestník.

---

## Co patří do kterého souboru

**Zápis ve špatném souboru přesuň** tam, kam patří – podle tohoto oddílu, u produktových dokumentů podle `~/.claude/standards/product.md`.

### `CLAUDE.md`

Instrukce pro Clauda v tomhle projektu. **Začíná blokem metadat**, kterým se projekt představuje navenek:

```
# Rezervační systém

Rezervační systém pro školení a konference.

- **Slug:** `rezervace`
- **Struktura:** docs/
- **Web:** https://rezervace.example.cz
- **Repozitář:** https://github.com/jantichy/rezervace
```

Nadpis je **lidský název** („Rezervační systém“, ne `rezervace`), odstavec pod ním **popisek** – jedna věta bez odkazů a formátování do 350 znaků (limit GitHubu). Slug je jméno malými se spojovníky a nese ho repozitář, ne adresář; Struktura režim umístění. Web a Repozitář vynech, nejsou-li – nepiš „zatím není“.

Blok je **kanonický zdroj** názvu a popisku. Odvozují se z něj nadpis a první odstavec `README.md` (tam se popisek smí rozvést) a Repository details na GitHubu (`gh repo edit <owner>/<slug> -d "<description>" -h "<web>"`). **Změní-li se název, popisek nebo URL, propiš to hned na všechna tři místa.**

**Import musí stát holý, ne v apostrofech** – v code spanu se tiše nenačte. Chceš-li cestu ukázat i jako kód, napiš ji dvakrát; odkaz, který se importovat nemá, v apostrofech nech.

Další sekce:

- **`## Kontrakt příkazů`** – **má ho každý projekt, ve kterém se něco spouští**: čím se spouštějí kroky (`test`, `lint`…). Zakládá ho `/project`, klíče drží `~/Context/Coding/quality.md`, *Kontrakt příkazů*.
- **`## Zákazy`** – na co model nesahá nebo co nedělá bez ptaní, a proč. **Hranici drží `permissions` v `.claude/settings.json`** (co se nesmí → `deny`, co jen s dotazem → `ask`); zákaz bez mechanismu se v sekci označí jako jen napsaný. Zakládá ji `/project`, jen má-li projekt co zakázat.
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

Postup, který potřebuje znát člověk pracující v projektu sám (jak to spustit, kam uložit podklad), do README patří, i když ho vykonává Claude.

### `todo.md`

Co padne mimo aktuální rozsah, ale **je rozhodnuté, že se to udělá** – úkol, otázka, kterou je nutné zodpovědět, rozhodnutí, které padnout musí. **S celou úvahou**, ne jako holá odrážka. **Jen jednorázové** – trvalý kontrolní seznam patří k testům, pravidlo stavby do návrhu. **Jen nehotové** – hotové přesuň hned do `done.md`.

**`todo.md` má dvě části.** Pod `# Fronta` (nadpis souboru) stojí pásma; v pásmech práce je pořadí priorita a spolu s velikostí ho určuje ten, kdo položku zapisuje – `/next` vypíše jen vrchol. Pod `# Mimo frontu` stojí sekce, které se neřadí: `## Rozhodnuto k zapracování` (nezapracované odpovědi průchodu nálezy, `~/.claude/skills/findings.md`) a `## Kola návrhu` (tvar, pořadí i život drží `~/.claude/skills/architect/rounds.md`).

- **Pásma `##`** jsou v pořadí naléhavosti: `## Přerušený běh` a `## Parkované v session` (pořadí zápisu, vlastní tvar), pak pásma práce (`Teď`, `Potom`, `Později`), ne témata. **Prázdné pásmo i sekce se ruší** (kromě kol) a s první položkou vznikne znovu, `# Mimo frontu` taky. **`Později` je rozhodnutá práce s nízkou prioritou**, ne nápad – ten patří do `backlog.md`.
- **Položka pásma práce je řádek první úrovně `- [ ] ◐ **Název.** …`** – velikost ○ drobnost, ◐ střední (session), ● velký (víc sessions). Nová jde nad první méně naléhavou. Co patří neoddělitelně k sobě, jsou její podbody; zaškrtávátko má jen podúkol, a záleží-li na pořadí, číslují se.
- **Má-li položka smysl až od určitého dne**, napiš **hned za název** `od <YYYY-MM-DD>` – `/next` ji do té doby nenabídne, jen zmíní. Datum uvnitř popisu odklad nezakládá.
- **`## Přerušený běh`** – přerušená fronta skillu i práce mimo skill; `/next` na něj rovnou naváže, tvar drží `/end`. Vypořádaná položka jde do `done.md`, jen je-li to odvedená práce, jinak se maže.
- **`## Parkované v session`** – bod odložený v rámci session; po vyřešení se maže.

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
- **Datum patří do prvního odstavce kapitoly, ne do nadpisu** (`**Rozhodnuto 15. 9. 2026.**`) – nadpis je kotva a datum v ní se při opravě tiše rozbije. Počet v nadpisu katalogu se toho netýká.
- **`## Co proklouzlo`** – defekty, které prošly všemi kontrolami; tvar drží `~/.claude/skills/release/SKILL.md`, *Když chyba projde vším*.
- **Kapitola kola návrhu** se píše bez čísla – `~/.claude/skills/architect/rounds.md`, *V `decisions.md`*.

### `done.md`

**Hotové položky přesunuté z `todo.md`. Nikdy se nemažou.**

- Přesouvej **průběžně**, ve chvíli, kdy je položka hotová.
- **Nejstarší nahoře**, nové na konec sekce; **datum dokončení** za názvem `(2026-08-28)`, vyrobené `date +%F`.
- **Sekce `todo.md` nezrcadlí** (kromě kol) – jsou to pásma priority, hotová práce leží pod `## Odvedená práce`.
- **Přesouvá se úkol, ne odškrtnutý krok uvnitř něj** – odškrtnuté řádky checklistu zůstávají u nedokončené položky.
- **`## Průchody životním cyklem`** – záznamy běhů kontrolních kroků; tvar a kdo zapisuje drží `~/.claude/skills/passes.md`. **`## Kola návrhu`** – `~/.claude/skills/architect/rounds.md`. Běhový stav skillů sem nepatří.

Existuje jen spolu s `todo.md`.

### `research/`

**Cizí podklady, ze kterých projekt vychází** – brief, zápis, export, PDF od klienta. Zakládá se, až je co uložit. Originály se sem **kopírují a dál nemění** (`~/.claude/standards/rules.md`, *Cizí podklady jsou read-only*); vytěžené žije jinde. Smysl je dohledatelnost.

### `rules.md`

**Obecné principy tohoto projektu** – věty, které rozhodují, ne popis systému. Vznikají z konkrétních rozhodnutí, ale zapisují se obecně jako rámec, proti kterému se rozhoduje; rozhodnutí drží `decisions.md`. Patří sem **jen to, co je specifické pro projekt** – obecná pravidla jsou v `~/.claude/standards/rules.md`, doménové znalosti v importované doméně, provoz worktree v `~/.claude/standards/worktree.md`.

---

## Prázdný soubor je v pořádku

Nový projekt má `todo.md`, `backlog.md`, `done.md`, `decisions.md` a `rules.md` založené jen s nadpisem. Nevymýšlej do nich obsah dopředu.
