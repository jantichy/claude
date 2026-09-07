# Standardní struktura projektu

Konvence platná pro **každý projekt, kde dává smysl** – tedy všude, kde se něco průběžně rozhoduje a vyvíjí. Jednorázový scratch adresář nebo cizí repozitář, do kterého jen nahlížíš, ji nepotřebuje.

Zakládá a udržuje ji skill `/project`. Tenhle soubor konvenci **definuje**; projektový `CLAUDE.md` jen deklaruje, že ji projekt drží, a popisuje odchylky.

## Dva režimy umístění

Standardní soubory jsou vždycky tytéž. **Kde leží, je volba ze dvou rovnocenných režimů** – ne výjimka z pravidla:

```
režim  docs/                       režim  root
<projekt>/                         <projekt>/
├── CLAUDE.md                      ├── CLAUDE.md
├── README.md                      ├── README.md
└── docs/                          ├── todo.md
    ├── todo.md                    ├── backlog.md
    ├── backlog.md                 ├── done.md
    ├── done.md                    ├── decisions.md
    ├── decisions.md               └── rules.md
    └── rules.md
```

| | `docs/` | `root` |
|---|---|---|
| Sedí na | projekt s kódem nebo obsahem, kde `docs/` odděluje meta-vrstvu od vlastní práce | knowledge base a malé projekty, kde by `docs/` byl prázdný obal nad dvěma soubory |
| Kořen | zůstává čistý | nese o pár souborů víc |

**Výchozí je `docs/`.** Režim se volí jednou při `/project` a pak se drží; míchat obojí v jednom projektu není třetí varianta, ale nepořádek.

**Konvence zápisu.** Texty, které popisují konvenci obecně – tenhle soubor, `~/.claude/RULES.md` a skilly – píšou cesty v podobě pro režim `docs/`: `docs/todo.md`, `docs/decisions.md`. **Myslí se tím soubor na místě podle režimu daného projektu**, ne doslovná cesta; rozepisovat u každé zmínky obě varianty by texty jen zahltilo.

Naopak texty, které mluví o **jednom konkrétním projektu** – jeho `CLAUDE.md` a `README.md` – píšou **skutečnou cestu**. Projekt svůj režim zná a jeho čtenář ne.

### Deklarace režimu

Který režim projekt používá, říká řádek v bloku metadat projektového `CLAUDE.md`:

```
- **Struktura:** docs/
```

Bez toho řádku se režim odvodí ze skutečného umístění souborů – ale deklarace je závazná: podle ní se rozhoduje, kam se zakládá další soubor.

### Které soubory vůbec vzniknou

Povinný je jediný soubor – **`CLAUDE.md`**, bez něj projekt není projekt. Zbytek se vybírá při `/project`:

| Soubor | Zakládá se |
|---|---|
| `README.md`, `decisions.md`, `rules.md` | volitelně, výběrem při `/project` (výchozí ano) |
| `todo.md` + `backlog.md` + `done.md` | volitelně, ale **jen jako trojice** – jedna volba pro všechny tři |
| `requirements.md`, `architecture.md`, `plan.md` | až prací, přes `/specify` a `/breakdown` |
| `competition.md`, `risks.md`, `scenarios.md`, `glossary.md`, `pricing.md` | **vybírá se** při `/project` (výchozí ne), zakládá se až prací – viz *Produktové podklady* |
| `research/` | až je co uložit |
| `.claude/run/` | samo, přerušitelným během skillu – není to standardní soubor, viz *Běhový stav skillů* |

Nezaložený soubor **není odchylka** – u projektu, kde se nic nerozhoduje, je prázdný `decisions.md` horší než žádný. Vznikne, až bude potřeba.

**Ve worktree layoutu** (`~/.claude/WORKTREE.md`) je „projekt“ pracovní adresář větve, ne kontejner. Celá struktura tedy žije v `main/` a odtud se s větví kopíruje – **i v režimu `root`, kde „kořen projektu“ znamená `main/`, ne kořen kontejneru.** Ten není pracovní strom a nic z něj by nešlo commitnout; je v něm jen tenký `CLAUDE.md` s popisem layoutu a importem `@main/CLAUDE.md`.

---

## Co patří do kterého souboru

### `CLAUDE.md`

Instrukce pro Clauda v tomhle projektu. **Začíná blokem základních metadat projektu** – tím, čím se projekt představuje navenek:

```
# Rezervační systém

Rezervační systém pro školení, konference a webináře – správa událostí, účastníků, objednávek a faktur.

- **Slug:** `rezervace`
- **Struktura:** docs/
- **Web:** https://rezervace.example.cz
- **Repozitář:** https://github.com/jantichy/rezervace
```

| Údaj | Co to je |
|---|---|
| Nadpis | **Lidský název** projektu, jak se o něm mluví – „Rezervační systém“, ne `rezervace`. |
| Odstavec pod ním | **Popisek** – jedna věta, co projekt je. Vejde se do GitHub description (limit 350 znaků), takže bez odkazů a formátování. |
| Slug | Technický název: adresář na disku, název repozitáře. |
| Struktura | Režim umístění standardních souborů: `docs/` nebo `root`. Viz *Dva režimy umístění* výš. |
| Web | Veřejná URL projektu, pokud existuje. Neexistuje-li, řádek vynech – nepiš „zatím není“. |
| Repozitář | URL remote, pokud existuje. Jinak řádek vynech. |

Tenhle blok je **kanonický zdroj** názvu a popisku. Odvozují se z něj dvě další místa a obě se musí držet s ním v souladu:

- **`README.md`** – týž lidský název v nadpisu, popisek jako první odstavec (tam se smí rozvést do víc vět).
- **Repository details na GitHubu** – description a website. Nastavují se z terminálu, ne v UI:

  ```bash
  gh repo edit <owner>/<slug> -d "<popisek>" -h "<web>"
  ```

**Změní-li se název, popisek nebo URL, propiš to hned na všechna tři místa** – jinak zůstane na GitHubu viset popisek, který už neplatí, a nikdo si toho nevšimne, protože ho v repozitáři není vidět.

Zbytek `CLAUDE.md` – autocommit, paměťová politika, typ projektu, doménové importy – zakládá `/project`.

**Kontrakt příkazů.** Projekt, ve kterém se něco spouští, má v `CLAUDE.md` sekci `## Příkazy` – překlad abstraktních kroků (`test`, `typecheck`, `lint`, `build`, `e2e`, `audit`, `mutation`) na to, čím se v tomhle projektu doopravdy spouštějí. Díky ní nemusí žádné pravidlo ani skill vědět, jestli je za projektem Node, PHP nebo Python. Zakládá ji `/project` a čtou ji brány kvality – zelená linka i skilly, které před svou prací pouštějí testy. **Projekt bez kódu ji nemá a nic tím neporušuje.**

**Sekce `## Nasazení`** popisuje, jak se projekt dostane do produkce – u platformy s automatickým nasazením zejména to, která větev je nasazovací. Zakládá ji `/project` nebo první běh `/release`.

**Sekce `## Review` a `## Consistency`** sbírají nálezy vyhodnocené jako „neopravovat“, aby je příště nehlásily znovu. Do `## Review` píší **`/review` i `/attack`** (u nálezu z útoku se řádek doplní o `(útok)`), do `## Consistency` píše `/consistency`. Píší je skilly, ne člověk; kapitoly jsou dvě, protože se ptají na jinou otázku – ne tři, protože `/review` a `/attack` se ptají na tutéž.

### `README.md`

**Pro člověka, který sem přijde poprvé.** Ne pro Clauda. To je jediné kritérium, podle kterého se rozhoduje, co do souboru patří.

Krátký popisný nebo odrážkový úvod, ze kterého se čtenář rychle zorientuje:

- co to je za projekt a k čemu slouží,
- co kde najde – mapa hlavních adresářů a dokumentů,
- jak se to používá, spouští, nasazuje,
- jak se s projektem jako celkem pracuje.

Nadpis je lidský název projektu a první odstavec popisek – oboje z bloku metadat v `CLAUDE.md`, viz výš. V README se popisek smí rozvést do víc vět.

Průběžně aktualizuj podle vývoje – má vždy odpovídat skutečnému stavu.

**Popisuj, nevyprávěj. Jeden odstavec na jednu věc.**

Má-li projekt víc součástí, které se v README představují jednotlivě – skilly, moduly, nástroje, balíčky – dostane každá **jeden odstavec**: co to je a k čemu je, případně velmi stručně co dělá. Ne dva, ne tři. Čtenář README hledá orientaci, ne výklad.

Do toho odstavce **nepatří**:

- příběh, jak věc vznikla, ani co se při jejím prvním použití stalo („když jsem to poprvé pustil, ze 43 nálezů…“),
- čísla dokládající užitečnost („ruční párování by vyšlo na 300 hodin“),
- obhajoba návrhu a poučky, proč je to udělané takhle („agent, který má hledat všechno, nenajde nic“) → to je `docs/decisions.md`,
- výčet fází, parametrů a vnitřních kroků → ten patří do dokumentace té věci, ne do rozcestníku.

Test: **jde ta věta škrtnout, aniž čtenář přestane vědět, k čemu ta věc je?** Pak tam nepatří. Zdůvodnění je cenné, ale patří do `docs/decisions.md`, kde ho někdo hledá – v README ho čtenář musí přeskakovat, aby našel, co potřebuje.

**Co do README nepatří:**

- Normativní instrukce pro Clauda – pravidla práce v repozitáři, konvence pojmenování, „adresář je vždycky doména“, povinnost něco aktualizovat, výčty interních značek a prefixů. To je `CLAUDE.md`.
- Principy, proti kterým se v projektu rozhoduje → `docs/rules.md`.
- Zdůvodnění voleb a zamítnuté varianty → `docs/decisions.md`.
- Co zbývá udělat → `docs/todo.md`.

**Ani odkazem.** Věta „pravidla pro práci s adresářem jsou v `CLAUDE.md`“ v README nemá co dělat – čtenáři README k ničemu nejsou a Claude si `CLAUDE.md` načte sám. Odkazuj z README jen na to, co má číst člověk.

Hraniční případ: konkrétní instrukce nebo popis postupu **nezbytný pro toho čtoucího člověka** (jak si to spustit, jak přidat novou položku, kam uložit podklad) do README patří, i když ho pak vykonává Claude. Rozhodující je, jestli by to potřeboval vědět člověk, který v projektu pracuje sám. Buď s tím ale opatrný – většina takových vět je ve skutečnosti procesní pokyn pro Clauda a patří jinam.

### `todo.md`

Všechno, co padne mimo aktuální rozsah, ale **je rozhodnuté, že se to udělá**: úkol do další fáze, otázka, kterou je potřeba zodpovědět, věc čekající na rozhodnutí, které padnout musí. **S celou úvahou a zdůvodněním**, ne jako holá odrážka – účel je mít téma připravené, ne ho teprve vymýšlet.

**Otevřená otázka sem patří tehdy, když se zodpovědět musí** – pak je jejím úkolem to rozhodnutí. Nepatří sem otázka typu „nemělo by se někdy…“, u které nikdo neřekl, že se jí budeme zabývat; ta je nápad a patří do `backlog.md`.

**Odložení po termín ani po MVP z položky nedělá nápad.** „Až po spuštění“, „ve druhé fázi“, „až budou data“ je nalajnovaný plán a patří sem; nezávazný nápad, o kterém se nikdo nerozhodl, patří do `backlog.md` – viz níž.

**Drží jen nehotové položky.** Jakmile je něco hotové, **přesuň to hned do `done.md`** – ne až při úklidu na konci session. `todo.md` tak na první pohled ukazuje, co zbývá.

Parkovaný bod v rámci session („teď přeskoč“) patří do sekce **`## Parkované v session`** a po vyřešení se **smaže** – do `done.md` nepatří, není to odvedená práce projektu. Sekce je dočasná: prázdná se ruší.

### `backlog.md`

**Zásobník nezávazných nápadů** – co by s produktem někdy šlo udělat, kdyby se chtěl rozšiřovat a nevědělo se kam. Nic z toho není odsouhlasené, rozpracované ani naplánované; je to materiál k výběru, ne fronta.

Hranice proti `todo.md` je tvrdá a jde po **rozhodnutí, ne po termínu**:

| | `todo.md` | `backlog.md` |
|---|---|---|
| Stav | rozhodnuto, že se to udělá | nikdo se nerozhodl |
| Čte se | průběžně, položky ubývají | když se vybírá, co dál |
| „Až po MVP“ | **sem** – je to nalajnovaný plán | ne |
| Osud položky | přesune se do `done.md` | buď se vytáhne do `todo.md` či do specifikace, nebo se smaže |

**Položka se z backlogu neodškrtává.** Rozhodne-li se, že se nápad udělá, **přesune se do `todo.md`** (nebo rovnou do zadání) – v backlogu po něm nezbude nic. Do `done.md` z backlogu nevede cesta přímo; hotová položka se tam dostane až přes `todo.md`, aby záznam odvedené práce zůstal jedním seznamem.

Jediná výjimka je **dorovnání staršího projektu**, kde se hotová věc do backlogu dostala omylem – ta jde rovnou do `done.md` a přesun se vypíše. Není to druhá cesta, ale úklid po chybném zařazení.

**Zamítnutý nápad se maže**, ale byl-li zamítnutý s odůvodněním, patří to odůvodnění do `decisions.md` (`~/.claude/RULES.md`, *Zapiš i to, co vědomě nemáš*). Backlog není hřbitov – co v něm leží, je pořád ve hře.

**Co sem nepatří:**

- **Nález prověřovacího kroku.** Co našel `/review`, `/attack`, `/consistency` nebo `/oponent`, je vada nebo dluh, ne nápad. **Odložit ho znamená rozhodnout, že se opraví později** – jde tedy do `todo.md`; zamítnutý jde do `## Review` v `CLAUDE.md`. Třetí možnost není: nález, u kterého se řekne „to nás nepálí“, je zamítnutý, ne odložený.
- **Parkovaný bod session** („teď přeskoč“) – ten patří do `## Parkované v session` v `todo.md` a po vyřešení se maže.
- **Rozhodnutí o dnešním návrhu a jeho zdůvodnění** → `decisions.md`. Netýká se to úvahy uvnitř nápadu – viz *Nápad smí být rozepsaný do detailu* níž.

**Vybírá z něj jediný skill – `/specify`**: než se začne psát nové zadání, projde ho a nabídne, co se hodí vytáhnout rovnou do něj. Bez toho by se nápady zapisovaly navěky a nikdy nečetly.

**Zapisují do něj `/implement` a `/cleanup`**, každý jinak. `/implement` sám a bez ptaní – nápad nad rámec plánu je jeho vlastní a zapsat ho je levnější než se na to ptát uprostřed práce. `/cleanup` se ptá vždycky, protože třídí, co v konverzaci padlo, a jestli za tím uživatel stojí jako za nápadem, ví jen on. **Přesouvá-li se položka z jednoho seznamu do druhého** (`/project` nad starým `todo.md`, `/specify` při výběru do zadání), rozhoduje uživatel o každé zvlášť.

**Chybí-li soubor a je co do něj zapsat, založ ho** a řekni to – jinak nápad spadne do `todo.md` a zaplevelí frontu, nebo se ztratí úplně. Je to táž výjimka, jakou má `/cleanup` pro každý standardní soubor: *nezakládat potichu* platí na zakládání do zásoby, ne na zápis, který jinak nemá kam.

**Nápad smí být rozepsaný do detailu a hloubka rozpisu o rozhodnutosti neříká nic.** Nápad, o kterém se ví jen jméno, tu má dvě věty; nápad, nad kterým už jednou někdo přemýšlel, tu má celý rozbor – datový model, algoritmus, okrajové případy, **i cesty, které se při té úvaze zavrhly a proč**. Je to levnější než tu úvahu za rok dělat znovu, a je to jediné místo, kde se dá udržet pohromadě s nápadem, ke kterému patří.

**Ty vnitřní závěry nejsou rozhodnutí projektu** a do `decisions.md` nepatří: platí podmíněně, tedy *kdyby* se ten nápad dělal, a spolu s ním zaniknou. Rozhodnutí do `decisions.md` patří teprve tehdy, když se dotýká **dnešního** návrhu – tedy když se podle něj už teď něco dělá nebo nedělá. Hranice je v tom, jestli závěr něco váže dnes, ne jak jistě zní.

**Uvnitř se člení podle sebe, ne podle `todo.md`.** Zrcadlení sekcí platí mezi `todo.md` a `done.md`, protože tam jde o tutéž položku ve dvou stavech; nápady se sdružují podle toho, čeho se týkají. Pořadí uvnitř nic neurčuje – backlog není fronta, takže „nejstarší nahoře“ by tvrdilo přednost, která neexistuje.

**Nápad v backlogu nestárne a sám nevyprchá.** Neuklízí se odtud podle stáří – že si ho rok nikdo nevybral, neznamená, že je špatný. Maže se jen tehdy, když se rozhodne, že se dělat nebude, a to rozhodnutí jde do `decisions.md`.

Existuje **jen spolu s `todo.md`** – bez fronty, proti které se vymezuje, by z něj byla druhá fronta.

### `decisions.md`

**Konkrétní rozhodnutí** tohoto projektu a cesta k nim: jaký problém to řešilo, jaké varianty byly ve hře, proč vyhrála tahle a proč padly ostatní. Patří sem i místa, kde jsme názor v průběhu změnili – ta se nepřepisují, přibude k nim revize s odůvodněním.

Zapisuj hned, jak rozhodnutí padne. Z odstupu se zdůvodnění rekonstruuje špatně nebo vůbec.

**Sekce `## Co proklouzlo`** drží jeden řádek na každý produkční defekt, který nechytila žádná vrstva – ani nástroj, ani panel v `/review`, ani útok, ani sledovací okno po nasazení:

```
- **2026-09-02** – *dvojité odeslání objednávky při rychlém dvojkliku*: měl to chytit panel (role Data a stavy), nechytil, protože v rozsahu nebyl frontend → doplněn regresní test a položka do checklistu
```

Zapisuje ji `/release` (viz jeho *Když chyba projde vším*). **Pole „doplněno“ nesmí být prázdné:** buď z defektu vzejde nová brána, nebo výslovné rozhodnutí, že se ta třída chyb hlídat nebude a proč. Bez toho se soustava učí jen z chyb, které sama našla – tedy z té množiny, kterou už chytat umí.

**Nejstarší nahoře. Nový zápis se připojuje na konec** – své sekce, je-li soubor členěný. Důvod je provozní: připsat na konec je jediný způsob zápisu, který nejde udělat špatně, protože nevyžaduje hledat správné místo. Opačné pravidlo se v praxi nedodrží. Navíc se soubor čte jako vývoj uvažování a revize stojí **za** původním rozhodnutím, ne před ním.

Platí to i tam, kde položky nemají datum – pořadí je prostě pořadí vzniku. A platí to i uvnitř tematicky členěného souboru: řadí se v rámci kapitoly, kapitoly samotné drží svou logiku.

### `done.md`

**Hotové položky přesunuté z `todo.md`.** Nikdy se nemažou – je to záznam odvedené práce, ze kterého jde zpětně říct, co se kdy udělalo a proč.

- **Přesouvej průběžně**, ve chvíli, kdy je položka hotová. Ne dávkově na konci.
- **Nejstarší nahoře, nové položky na konec** sekce – stejné pravidlo i důvod jako v `decisions.md` výš.
- **Datum dokončení** za názvem položky ve tvaru `(2026-08-28)`.
- Je-li `todo.md` členěné na sekce, **`done.md` je zrcadlí** – hotová položka jde do sekce, do které patřila.
- **Přesouvá se úkol, ne odškrtnutý krok uvnitř něj.** Má-li nedokončená položka vnořený checklist, jeho odškrtnuté řádky zůstávají u ní – dávají jí kontext a bez nich není vidět, co z úkolu už je hotové.

Existuje **jen spolu s `todo.md`**: jeden bez druhého nedává smysl, tak se taky zakládají a vybírají – jednou volbou pro celou trojici `todo.md`, `backlog.md`, `done.md`.

**Sekce `## Průchody životním cyklem`** drží po jednom řádku za dokončený běh těch kroků *Životního cyklu projektu* (`~/.claude/RULES.md`), které mají svého čtenáře – dnes `/review` a `/attack` (čte je `/release`, aby se neptal z paměti) a `/oponent` (čte ho příští `/oponent`). Ostatní kroky sem nezapisují a nemají proč – včetně `/oponent`, který je od 2. 9. 2026 krokem životního cyklu. Zapisují si ho skilly samy, ne člověk:

```
- **2026-09-02** · `/review` · `ff0f765` · změny na větvi (14 souborů) · 12 nálezů (3 opraveno, 7 odloženo, 2 won't fix)
```

Datum vyrob `date +%F`, hash `git rev-parse --short HEAD` – obojí příkazem, ne z kontextu (`~/.claude/RULES.md`, *Hodnotu, kterou čte stroj, nepiš – nech ji vyrobit příkazem*).

**Proč se zapisuje i `/oponent`:** je **opakovatelný nad týmž dokumentem** – a druhý běh potřebuje vědět, s jakým panelem úhlů běžel ten první, jinak počty nálezů mezi běhy nic neříkají. Řádek tedy neslouží `/release` jako u `/review` a `/attack`, ale příštímu běhu téhož skillu.

**Proč to tu je:** `/release` se před nasazením ptá, jestli nad tímhle rozsahem proběhl `/review` a `/attack`. Nasazuje se ale v jiné session a o dny později, takže odpověď z paměti je odhad – člověk si vzpomene, že *někdy* běžely, ne že běžely nad *tímhle*. Obě odpovědi jsou pak špatné: „ano“ pustí ven nezkontrolovanou práci, „radši znovu“ stojí desítky minut a plný běh agentů. S hashem se to porovnat dá.

**Výjimka z pravidla o zrcadlení:** tahle sekce žádnou sekci v `todo.md` nezrcadlí, protože průchod životním cyklem není odložený úkol, který by se dokončil. Je to jediná sekce `done.md`, která vzniká bez protějšku.

**Běhový stav kroku sem nepatří** – rozpracovaná fronta nálezů `/review` ani seznam toho, co zvedl `/attack`, viz *Běhový stav* níž.

### `requirements.md`, `architecture.md`, `plan.md`

**Zadání a plán.** Nevznikají u každého projektu a nezakládá je `/project` – přibudou, až se v projektu něco staví:

| Soubor | Odpovídá na otázku | Zakládá |
|---|---|---|
| `requirements.md` | Co stavíme a proč | `/specify` |
| `architecture.md` | Jak to postavíme | `/specify` |
| `plan.md` | Kdo co udělá v jakém pořadí, s ověřitelným akceptačním kritériem u každého úkolu | `/breakdown` |

Hranice mezi `requirements.md` a `architecture.md` je tvrdá: do požadavků patří **omezení**, do návrhu řešení **volba**. Podrobně v `~/.claude/skills/specify/SKILL.md`.

Změna teče **shora dolů**: `requirements.md` → `architecture.md` → `plan.md` → kód. Nikdy obráceně – ukáže-li se při implementaci, že návrh nefunguje, opraví se návrh, ne potichu kód.

Projekt bez kódu (znalostní, obsahový, obchodní) má smysluplně jen `requirements.md`; místo plánu se kroky rozepíšou do `todo.md`.

### Produktové podklady

**Podklady, ze kterých se staví produkt** – ne obchodní plán a ne marketing. Vybírají se při `/project`, který je **nezakládá**, jen si zapíše, které z nich projekt vede. Vznikají prací:

| Soubor | Odpovídá na otázku | Plní |
|---|---|---|
| `competition.md` | Kdo je konkurence, co umí, za kolik – a jaká je proti nim naše pozice | `/discovery` |
| `risks.md` | Co je na produktu rizikové a čím to v návrhu mitigujeme | `/discovery` |
| `scenarios.md` | Co s produktem uživatel dělá, krok za krokem, taxativně | `/specify` |
| `glossary.md` | Jak se v téhle doméně čemu říká | `/specify` |
| `pricing.md` | Tarify, limity, trial, upgrade, co se stane po expiraci | `/specify` |

**Žádný z nich není povinný a většina projektů má nanejvýš dva.** Interní nástroj nemá konkurenci ani ceník; jednoduchá aplikace nepotřebuje glosář. Prázdný podklad je horší než žádný, protože předstírá, že se ta úvaha udělala.

**`competition.md`** drží data o trhu i jejich závěr. Začíná sekcí `## Co poměřujeme` – jaký problém řešíme, komu, v jaké kategorii produktu tedy soutěžíme a čím se to má hrubě lišit. **Je to vymezení pole hledání, ne specifikace**: bez něj by se nedalo rozhodnout, kdo vůbec je konkurence, a `/specify` ho pak čte jako hotový vstup, místo aby se na totéž ptal podruhé. Pak následuje analýza sama (kdo, co, za kolik, co umí) a závěrečná sekce `## Naše pozice a odlišení`: co musíme mít, protože to má každý; co děláme jinak; kde vědomě zaostáváme. **Závěr žije tady, ne zvlášť** – analýza bez závěru se nečte a závěr bez analýzy se nedá ověřit (*Vše o jedné věci pohromadě u ní*). Samostatný soubor na USP se nezakládá; byl by třetím místem, kde se tvrdí, co produkt musí umět, vedle *MVP* v `requirements.md` a `scenarios.md`.

**`risks.md`** je **registr, ne SWOT.** U každého rizika: čeho se týká, jaký by mělo dopad, jak je pravděpodobné, čím ho mitigujeme a **co se kvůli němu v produktu změnilo nebo přibylo**. To poslední pole je smysl celého souboru – bez něj je to seznam obav, který nikoho nezavazuje. SWOT se nedělá: silné stránky a příležitosti už drží *Naše pozice a odlišení* v `competition.md`, slabiny a hrozby jsou právě tenhle registr.

Hranice proti sekci *Rizika* v `architecture.md` je tvrdá a jde po téže čáře jako hranice požadavků a návrhu: sem patří **rizika produktu a trhu** (nikdo to nebude používat, konkurence to udělá dřív, data se nedají získat, legislativa se změní), do návrhu **technická rizika zvoleného řešení** (nezvládne to zátěž, ta knihovna může skončit).

**`scenarios.md`** je **taxativní seznam toho, co uživatel s produktem dělá**, každý scénář krok za krokem od začátku do konce, včetně okrajových a chybových cest. Má tři čtenáře, které `requirements.md` neobsluhuje: toho, kdo ověřuje, že produkt umí, co má; toho, kdo z toho píše nápovědu a FAQ; a testování na skutečných lidech po dokončení.

**Má-li projekt `scenarios.md`, sekce *Hlavní scénáře* v `requirements.md` zaniká** a nahradí ji odkaz. Dva seznamy scénářů se rozejdou při první změně rozsahu (*Single source of truth*). V požadavcích zůstává **proč a pro koho** – persony, user stories, varianty jako produktová rozhodnutí; ve scénářích **jak to člověk provede**. Odkazuje se sem odjinud: *Testovací strategie* v `architecture.md` měří pokrytí proti tomuhle seznamu, stejně jako `plan.md` a `/attack`.

**`glossary.md`** dává *Jednomu termínu pro jednu věc* z `~/.claude/RULES.md` místo, kde ten termín stojí zapsaný. U každého pojmu: jak se jmenuje česky, jak v kódu, co znamená a **čím se liší od pojmu, se kterým se plete**. To poslední je hlavní obsah – slovník bez rozlišení blízkých pojmů nic neřeší. Zakládá se u projektu s netriviální doménou, kde se plete víc entit naráz.

**`pricing.md`** má smysl jen u produktu, který se prodává. Není to ceník pro web, ale **soupis toho, co z cenového modelu plyne pro produkt**: co který tarif smí, kde jsou limity a co se stane při jejich dosažení, jak vypadá trial a co po něm, jak se přechází nahoru a dolů, co se stane po expiraci a co s daty. Každá z těch vět je funkce, kterou někdo musí naprogramovat.

### `research/`

**Cizí podklady, ze kterých projekt vychází** – brief, zápis ze schůzky, export, dump, PDF od klienta, screenshoty. Zakládá se, až je co uložit; `/project` ho nevytváří.

Platí pro něj *Cizí podklady jsou read-only* z `~/.claude/RULES.md`: originály se sem **kopírují a dál nemění**. Co se z nich vytěží, žije v ostatních souborech projektu, ne tady.

Smysl je dohledatelnost – aby šlo za rok ověřit, odkud se rozhodnutí vzalo.

### `rules.md`

**Obecné principy tohoto projektu** – věty, které rozhodují, ne popis toho, co systém dělá. Vznikají z konkrétních rozhodnutí, ale zapisují se obecně, aby platily i tam, kam se ještě nedošlo.

Rozdíl proti `docs/decisions.md`: tam je konkrétní rozhodnutí (občas i výjimka z principu), tady rámec, proti kterému se rozhoduje. Každou další otázku validuj proti principům odsud, ne od nuly.

**Hranice – co sem nepatří:**

- Pravidla platná napříč všemi projekty → `~/.claude/RULES.md`
- Doménové standardy a checklisty (kód, web, administrace, analytika, psaní textů, typografie) → do příslušného doménového standardu, který si projekt importuje ve svém `CLAUDE.md`, sekce *Doménové standardy*
- Pravidla provozu worktree layoutu → `~/.claude/WORKTREE.md`, které si projekt s tímhle layoutem importuje do stubu v kořeni kontejneru
- Sem patří **jen to, co je specifické pro tenhle projekt.** Duplikovat sem obecné pravidlo je chyba.

---

## Běhový stav skillů

Skilly, které běží dlouho a dají se přerušit, si odkládají **stav jednoho běhu** – rozpracovanou frontu nálezů `/review` a `/oponent`, seznam portů a kontejnerů, které zvedl `/attack`. Ten stav žije v **`.claude/run/`** v projektu a **patří do `.gitignore`** (řádek zakládá `/project`).

**Není to standardní soubor a do výčtu výš nepatří.** Všechno ostatní v tomhle dokumentu je znalost, kterou čte člověk a verzuje git; běhový stav není ani jedno – je strojový, platí jeden běh a za týden je to škodlivý odpad. Do gitu nesmí ze zcela provozního důvodu: mění se po každém tahu, takže v projektu se zapnutým autocommitem by se donekonečna commitoval.

**Proč vůbec existuje:** bez něj žije nejdražší část běhu jen v kontextu session. `/review` po panelu a ověřovatelích začne dlouze interagovat s uživatelem právě ve chvíli, kdy kontext dochází nejrychleji – a kompaktace uprostřed průchodu znamená zaplatit celý běh znovu. `/attack` zase přerušením ztratí seznam toho, co zvedl, a nechá na stroji běžet server a kontejnery, o kterých už nikdo neví.

**Do `.claude/run/`, ne mimo repozitář:** je to per pracovní adresář, tedy ve worktree layoutu přirozeně per větev – a fronta nálezů k větvi patří. (Souhlas a běhový stav zelené linky naopak leží mimo repozitář a klíčují se sdíleným `.git`, protože odpovídají na otázku o repozitáři, ne o větvi.)

**Nikdy se z něj nečte jako z pravdy o projektu.** Říká jen, kde skončil přerušený běh; co z toho má trvalou platnost, se zapíše do `todo.md`, `decisions.md` nebo `done.md` jako všechno ostatní.

---

## Průběžná aktualizace je povinná

Tyhle soubory jsou **živé**, ne zakládací formalita. Doplňuj je **sám, průběžně, bez vyžádání** – ve chvíli, kdy rozhodnutí padne, princip se vybrousí nebo se něco odloží. Nečekej na `/cleanup` ani na konec session.

Uživatel na to nesmí muset upozorňovat. Když si nejsi jistý, do kterého souboru zápis patří, rozhodni podle otázky, na kterou odpovídá:

| Otázka | Soubor |
|---|---|
| Co ten projekt je a jak se používá? | `README.md` |
| Co ještě není hotové? | `todo.md` |
| Co bychom někdy možná mohli, ale nikdo to nerozhodl? | `backlog.md` |
| Co je hotové? | `done.md` |
| Proč jsme to udělali takhle? | `decisions.md` |
| Jak se v tomhle projektu rozhoduje? | `rules.md` |
| Co stavíme a proč? | `requirements.md` |
| Jak to postavíme? | `architecture.md` |
| Kdo co udělá v jakém pořadí? | `plan.md` |
| Odkud to máme? | `research/` |

Když se ukáže, že zápis patří jinam, přesuň ho – princip *Živá struktura* z `~/.claude/RULES.md` platí i tady.

## Prázdný soubor je v pořádku

Nový projekt má `todo.md`, `backlog.md`, `done.md`, `decisions.md` i `rules.md` založené a prázdné, jen s nadpisem. Nevymýšlej do nich obsah dopředu; naplní se prací.
