---
name: compose
description: Skill se použije, když uživatel zadá "/compose" (volitelně s režimem collect nebo profile), nebo chce napsat článek, příspěvek na sociální sítě či vlákno vlastním hlasem a stylem. Výchozí režim píše text podle znalostní báze autorova psaní. Režim "collect" provede shromážděním všech jeho dosavadních textů do archivu – exporty ze sociálních sítí, články z webů, lokální zálohy. Režim "profile" nad tím archivem vydestiluje znalostní bázi, nebo ji aktualizuje o texty, které mezitím přibyly. Na rozdíl od /transcript, který přepisuje nahrávky, tenhle skill píše nový text. Autorovy názory a pointy si nikdy nevymýšlí – bez nich se nerozjede.
argument-hint: [collect|profile]
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent, WebFetch, AskUserQuestion]
---

# Compose

## Co skill dělá

Píše text hlasem konkrétního autora – ne obecnou češtinou, kterou dnes pozná každý. Opírá se o **znalostní bázi** (odvozená pravidla: styl, profily formátů, zlatý fond ukázek) a o **archiv** (korpus všeho, co autor kdy napsal). Tři režimy:

- **`/compose`** – **psaní textu**. Článek, příspěvek na sociální sítě, vlákno.
- **`/compose collect`** – **shromáždění archivu**. Provede vyžádáním exportů ze sítí, stažením článků z webů a převodem do jednotné podoby. Pouští se opakovaně, kdykoliv přibude nový zdroj nebo nový export.
- **`/compose profile`** – **destilace báze** nad archivem. Neexistuje-li báze, postaví ji celou; existuje-li, zapracuje jen to, co v archivu přibylo od minule.

**Hlas ani cesty nejsou v tomhle souboru.** Skill neví, komu píše – čte to z báze, na kterou je nastavený. Bez ní neumí nic; první běh je proto vždycky `collect` a `profile`.

## Co skill nedělá

- **Nevymýšlí autorovy názory a pointy.** Zná jeho *jak*, ne jeho *co*. Když k tématu nezná postoj, doptá se – odhadnutý názor je horší než žádný text.
- **Nespravuje archiv jako korpus.** Konvence pojmenování, metadata a tematické štítky jsou věc toho archivu, ne skillu. `collect` je do něj plní podle jeho pravidel; kde žádná nejsou, založí je.
- **Nepřepisuje mluvené slovo.** Na nahrávky, schůzky a jejich shrnutí je `/transcript`. Tenhle skill vyrábí nový text.
- **Nedělá redakční korekturu cizího textu.** Kontrola proti redakčnímu standardu je `~/Dev/context/text/text.md`; tady se standard uplatňuje při psaní, ne jako samostatná služba.
- **Nepublikuje.** Výstupem je text, ne příspěvek někde venku.

## Jak je to postavené uvnitř

Převodníky exportů ze sociálních sítí leží ve `scripts/` vedle tohohle souboru:

| Skript | Vstup | Co dělá |
|---|---|---|
| `scripts/gen_twitter_md.py` | adresář `data/` z rozbaleného exportu X | tweety po letech, expanduje t.co, slučuje vlákna |
| `scripts/gen_facebook_md.py` | `your_posts__…_1.json` | příspěvky po letech, opravuje mojibake |
| `scripts/gen_linkedin_md.py` | adresář s `Shares_*.csv` a `Comments_*.csv` | příspěvky a komentáře po letech |
| `scripts/parse_bluesky.py` | `repo.car` | posty z AT Protocol repozitáře do JSON (žádá `cbor2`) |
| `scripts/gen_bluesky_md.py` | JSON z předchozího kroku | posty po letech |
| `scripts/extract_wpress.py` | archiv `.wpress` | rozbalí zálohu All-in-One WP Migration |

**Skripty jsou implementační detail, ne rozhraní.** Smí se přepsat i vyhodit. Závazné je, co po nich zbude: **jednotný Markdown v archivu**, ze kterého `profile` čte, a **idempotence** – druhý běh nad týmž exportem vyrobí týž soubor, takže rozdíl je vidět v gitu.

**Všechny berou cíl argumentem**, nikdy si ho neodvozují ze svého umístění. Skill se instaluje jinam, než leží archiv.

------

## Fáze 0 – Pre-flight

Společný začátek je v `~/.claude/skills/PREFLIGHT.md`. **Body 1 až 3 z něj neplatí** – skill neběží nad projektem, ale nad archivem a bází, které leží mimo něj. Nahrazuje je tohle:

1. **Najdi bázi a archiv.** Cesty stojí v `~/.claude/CLAUDE.md` na řádku začínajícím `- **Znalostní báze psaní:**`. **Chybí-li ten řádek**, zeptej se přes `AskUserQuestion`, kde mají obě věci ležet, a řádek doplň – jinak se bude ptát každá session znovu. Neexistuje-li ani jedna cesta, řekni to a nabídni `collect`.
2. **Ověř, že báze není prázdná.** Chybí-li soubor stylu, skill nemá podle čeho psát: řekni to a nabídni `profile`. Nepokoušej se hlas odvodit za běhu z archivu – vznikne z toho průměr, ne styl.
3. **Zjisti, jestli archiv i báze leží v gitu a jestli je pracovní strom čistý.** Oboje se při běhu mění a autocommit cizí session by tvoje rozpracované změny posbíral s něčím nesouvisejícím. Je-li tam něco rozpracovaného, vypiš to a zeptej se.

**Zapisuje se do dvou repozitářů** – archivu a báze. Ani jeden z nich nemusí být ten, ve kterém session běží. Co v nich změníš, commituj sám a řekni to; v cizím pracovním stromu nikdy nenechávej nedokončený zápis.

## Fáze 1 – Zadání

Je-li v argumentu režim, jeď podle něj a jen ho oznam. Jinak piš text a **ptej se postupně, jednu otázku za druhou** (`~/.claude/RULES.md`, *Ptej se postupně, ne všechno najednou*):

1. **Formát** – článek, příspěvek, vlákno. Určuje, který profil se načte.
2. **Téma, publikum, kanál.**
3. **Autorův postoj a pointa.** Tohle je jádro. Autor smí dodat cokoliv od holého tématu přes osnovu po hrubý draft – ale postoj musí přijít od něj. **Nezná-li ho ani on, ani ty, doptej se a bez odpovědi nepiš.**

## Fáze 2 – Kontext

Načti z báze **soubor stylu**, **profil zvoleného formátu** a **odpovídající zlatý fond ukázek**.

K tomu dohledej v archivu **3 až 5 textů nejpodobnějších tématem a formátem** – přes zlatý fond a grep – a **přečti je celé**. Pravidla popisují hlas, ukázky ho nesou; bez nich vzniká text, který popis stylu splňuje a přesto zní cize.

## Fáze 3 – Draft

Napiš text podle stylu a profilu formátu. Platí i redakční standard `~/Dev/context/text/text.md`, existuje-li – báze řeší hlas, standard řemeslo.

## Fáze 4 – Self-check

Před odevzdáním projdi:

- **Výklad od A k B.** Mluví-li text o B, které plyne z A, stojí A dřív.
- **Šťouralové předjati.** Detail vynechaný pro jednoduchost je v textu zmíněný a zdůvodněný.
- **Srozumitelnost pro dané publikum**, bez ztráty odborné korektnosti.
- **Anti-patterny ze stylu.** Zní to jako autor, ne jako AI?
- **Horní mez.** Charakteristické obraty a expresiva smí být v textu **nanejvýš jednou** – víc už je parodie na vlastní styl. Klidně žádný.

## Fáze 5 – Předání

Předlož draft a zapracuj připomínky.

**Připomínku obecné platnosti nabídni promítnout do báze** – do stylu, profilu formátu, nebo výměnou ukázky ve zlatém fondu. Bez toho se táž oprava dělá při každém dalším textu znovu. Zapisuj až po odsouhlasení a **řekni, do kterého souboru to šlo**.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Text je hotový a prošel self-checkem, můžeš ho publikovat.`
- `Text hotový není – brání tomu: <konkrétní seznam>.`

------

## Režim `collect`

Shromáždí texty do archivu. **Katalog zdrojů, postupy stahování a pasti jednotlivých exportů jsou v [`sources.md`](sources.md)** – načti si ho, neopisuj odsud.

### 1. Soupis zdrojů

Zeptej se, kde všude autor kdy psal: vlastní blogy, cizí weby a magazíny, tištěná média, sociální sítě, zaniklé weby, lokální zálohy. **Ptej se postupně** a u každého zdroje zjisti, jestli je ještě online.

**Odhad počtu od autora není zdroj pravdy.** „Bude jich přes sto" opakovaně neodpovídalo ničemu. Úplnost se ověřuje proti datům – `X-WP-Total`, sitemapa, databáze exportu – a platí ta.

### 2. Vyžádání exportů

Exporty ze sítí se připravují **hodiny až dva dny**. Vyžádej je jako první věc, ať čekání běží na pozadí, a řekni autorovi, že mu přijde mail. Odkazy jsou v `sources.md`.

### 3. Rozhodnutí o rozsahu

Než se začne stahovat, nech potvrdit tři věci – každá pak platí pro celý archiv:

| Co | Proč se to rozhoduje předem |
|---|---|
| **Co je autorský text** | Rozhovor, kde autor jen odpovídal, napsal někdo jiný. Doklad o autorovi to je, jeho dílo ne. Dělicí čára je autorství, ne formát. |
| **Co se vyřazuje** | Mrtvé žánry, cizí zadání, texty psané pod cizí redakcí. Vyřazené se **nemaže, jen označí** – pořád dokládá vývoj. |
| **Časové vážení** | Které roky jsou norma a které už jen historie. Bez toho vznikne průměr dvaceti let, kterým autor nikdy nepsal. |

### 4. Stažení a převod

Jeď zdroj po zdroji podle `sources.md`. Skripty ze `scripts/` berou cíl argumentem.

**Texty psané AI se do archivu značí** řádkem v metadatech. Bez toho se příští `profile` učí z vlastního výstupu a hlas se stočí sám do sebe.

**Ověř úplnost každého zdroje proti datům**, ne proti dojmu, a zapiš k němu, jak se to ověřilo. Zdroj, u kterého se to neví, se v archivu označí jako neúplný.

### 5. Zápis konvencí

Archiv potřebuje vlastní popis: struktura adresářů, pojmenování souborů, povinná metadata, odkud se co bere a jak se to aktualizuje. Založ ho, nebo doplň, a **commitni**.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Archiv je shromážděný a úplnost každého zdroje ověřená, můžeš pustit /compose profile.`
- `Archiv shromážděný není – brání tomu: <konkrétní seznam>.`

------

## Režim `profile`

Vydestiluje z archivu znalostní bázi. **Postup destilace, struktura analýz a slepý test jsou v [`distillation.md`](distillation.md)** – načti si ho, neopisuj odsud.

### 1. Zjisti, co se profiluje

Podívej se do báze na záznam poslední profilace:

| Stav | Co dělat |
|---|---|
| Báze neexistuje | **Celá destilace** podle `distillation.md`. |
| Báze i záznam existují | **Přírůstek**: jen texty, které v archivu přibyly od zapsaného data a rozsahu. |
| Báze existuje, záznam ne | Řekni to a **zeptej se**: buď celá destilace znovu, nebo datum, od kterého se má brát přírůstek. Nehádej. |

**Nikdy nepřepisuj bázi bez přečtení.** Obsahuje ruční úpravy, které vznikly z připomínek k jednotlivým textům, a ty v archivu nikde nejsou.

### 2. Analýza korpusu po částech

Korpus se do kontextu nevejde. Rozděl ho na části podle formátu – dlouhé texty, střední příspěvky, mikroblog a vlákna – a **každou nech projít samostatně**; jsou na sobě nezávislé.

**Každé stylistické tvrzení musí mít doklad**: cestu k souboru a doslovný úryvek. Tvrzení bez dokladu je dojem a do báze nesmí. Formát analýz je v `distillation.md`.

**Model a effort** (delta proti `~/.claude/RULES.md`, *Model a effort podle úkolu*): analýzy jedou na výchozím modelu session, protože jde o čtení proti zadané struktuře a chyba je vidět v dokladu. **Syntéza do stylu jede na nejsilnějším modelu a `xhigh`** – je vstupem každého budoucího textu, takže se její chyba násobí do všeho, co po ní přijde.

### 3. Syntéza

Z analýz sestav bázi: **styl** (co platí napříč formáty), **profil každého formátu** (co je jeho vlastní) a **zlatý fond** ukázek.

**Profil neopisuje styl, odkazuje na něj.** Dvě verze téhož pravidla se rozejdou a nikdo nepozná, která platí.

**Anti-patterny piš kontrolovatelně.** „Nezačíná text řečnickou otázkou" jde ověřit; „píše autenticky" ne.

### 4. Slepý test

Napiš podle nové báze tři texty – po jednom v každém formátu – a nech autora říct **„zní / nezní jako já"** s konkrétní výhradou. Bez toho se neví, jestli báze zachytila hlas, nebo jen popis hlasu.

**Zadání musí přijít od autora**, včetně jeho pointy. Text s vymyšleným názorem test znehodnotí – autor bude odmítat obsah a bude to vypadat jako vada stylu.

Každou výhradu přelož na úpravu báze a **opakuj, dokud autor neschválí všechny tři formáty.**

### 5. Záznam

Zapiš do báze datum profilace a rozsah korpusu, ze kterého vyšla – počty a poslední zpracovaný soubor u každého zdroje. To je jediné, podle čeho příští běh pozná, co je nové. **Commitni** archiv i bázi.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Báze je hotová a prošla slepým testem, můžeš psát /compose.`
- `Báze hotová není – brání tomu: <konkrétní seznam>.`

------

## Časté chyby

- **Píše se bez načtených ukázek.** Podle pravidel vznikne text, který je splňuje a přesto zní cize. Hlas nesou ukázky, pravidla ho jen popisují.
- **Charakteristický obrat se použije třikrát.** Jednou je to podpis, potřetí parodie. Platí na celý text, ne na odstavec.
- **Autorův názor se odhadne z jeho starších textů.** Archiv říká, jak píše, ne co si myslí o dnešním tématu.
- **Připomínka obecné platnosti se opraví jen v draftu.** Za týden se objeví znovu, protože v bázi o ní nic není.
- **Úplnost zdroje se odhadne.** Ověřuje se proti datům; odhad se opakovaně ukázal jako smyšlený.
- **Vlastník účtu se přečte z prvního identifikátoru v exportu.** Exporty jsou plné cizích ID – první `did:plc:` v Bluesky exportu patřil sledovanému účtu, ne autorovi.
