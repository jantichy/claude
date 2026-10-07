# Produktové a návrhové dokumenty

Co smí stát v dokumentech, ze kterých se staví produkt – zadání, návrh řešení, plán a produktové podklady. Doplňuje `~/.claude/standards/structure.md`, který drží standardní soubory každého projektu. **Odkaz, ne import:** načítá ho skill, který tyhle dokumenty zakládá nebo do nich zapisuje (`/project`, `/discovery`, `/specify`, `/architect`, `/breakdown`, `/evaluate`); spouštěč drží `structure.md`, *Které soubory vůbec vzniknou*.

## `requirements.md`, `architecture.md`, `plan.md`

**Zadání a plán.** Nevznikají u každého projektu a nezakládá je `/project` – přibudou, až se v projektu něco staví:

| Soubor | Odpovídá na otázku | Zakládá |
|---|---|---|
| `requirements.md` | Co stavíme a proč | `/specify` |
| `architecture.md` | Jak to postavíme – **páteř návrhu řešení, ne celý návrh** | `/architect` |
| `plan.md` | Kdo co udělá v jakém pořadí, s ověřitelným akceptačním kritériem u každého úkolu | `/breakdown` |

Hranice mezi požadavky a návrhem řešení je tvrdá: do požadavků patří **omezení**, do návrhu řešení **volba**. „Musí to běžet na běžném sdíleném hostingu bez placených závislostí“ je omezení; „použijeme SQLite, protože…“ je volba. Kontrolní otázka, když si nejsi jistý, kam věta patří: *změní se, když se změní technologie?* Ano → návrh, ne → požadavky.

**Dva soubory, protože mají jinou životnost** – záměr se mění zřídka, řešení s každou technologickou volbou. **Nepřekrývají se:** `requirements.md` nesmí obsahovat architekturu ani „nejspíš to bude na Vercelu“, `architecture.md` nesmí obsahovat zdůvodnění produktu – na požadavky odkazuje a neopisuje je.

**Návrh řešení je sada dokumentů, ne jeden soubor**, a `architecture.md` je jeho páteř. Požadavky jsou seznam a vejdou se do jednoho dokumentu; návrh je soustava, ve které se věci navzájem omezují, a každý dokument je **řez toutéž věcí z jiného úhlu**: stavba (`architecture.md`), data a stavy (`model.md`), operace (`transitions.md`), zásady domény (`rules.md`), jednotlivé okruhy (tematické dokumenty kol). Táž funkce tak stojí ve víc z nich, a je to správně (`~/.claude/standards/rules.md`, *Jednoduchost před úplností*).

**Nový dokument vzniká tehdy, když drží jiný řez – ne když je ten stávající dlouhý.** Kontrolní otázka: *odpovídá na otázku, na kterou žádný jiný neodpovídá?* Když ne, je to kapitola. `model.md` se nedělí kvůli délce a katalog operací se nevlévá do dokumentu o stavbě.

**Kolik jich vznikne, rozhoduje projekt.** Malému stačí `architecture.md` samotný a víc jich zakládat se nemá; `model.md` a `transitions.md` jsou pojmenované, aby si je každá aplikace nevymýšlela jinak, ne protože jsou povinné.

Podrobně v `~/.claude/skills/specify/SKILL.md` a `~/.claude/skills/architect/SKILL.md`.

Změna teče **shora dolů**: `requirements.md` → `architecture.md` → `plan.md` → kód. Nikdy obráceně – ukáže-li se při implementaci, že návrh nefunguje, opraví se návrh, ne potichu kód.

Projekt bez kódu (znalostní, obsahový, obchodní) má smysluplně jen `requirements.md`; místo plánu se kroky rozepíšou do `todo.md`.

**Návrh po kolech** přidává tematické dokumenty `docs/<topic>.md`, jeden na kolo – co v nich smí stát a co kola zapisují do sdílených dokumentů, drží `~/.claude/skills/architect/rounds.md`, *Tematické dokumenty*.

## Produktové podklady

**Podklady, ze kterých se staví produkt** – ne obchodní plán a ne marketing. Vybírají se při `/project`, který je **nezakládá**, jen si zapíše, které z nich projekt vede. Vznikají prací. **Výjimkou je `operation.md`** – ten se nevybírá, protože dokud není co nasadit, není o čem rozhodovat; zakládá ho až první běh `/evaluate`:

| Soubor | Odpovídá na otázku | Plní |
|---|---|---|
| `demand.md` | Proč to vůbec stavět – kdo má ten problém, jak ho dnes řeší, co ho to stojí a čím je doložené, že ho chce řešit jinak | `/discovery` |
| `competition.md` | Kdo je konkurence, co umí, za kolik – a jaká je proti nim naše pozice | `/discovery` |
| `risks.md` | Co je na produktu rizikové a čím to v návrhu mitigujeme | `/discovery` |
| `scenarios.md` | Co s produktem uživatel dělá, krok za krokem, taxativně | `/specify` |
| `glossary.md` | Jak se v téhle doméně čemu říká | `/specify` |
| `pricing.md` | Tarify, limity, trial, upgrade, co se stane po expiraci | `/specify` |
| `operation.md` | Co o produktu víme z provozu – jestli se používá, kde to lidé nedokončili, co si vyžádali | `/evaluate` |

**Žádný z nich není povinný a většina projektů nevede ani jeden** – nestaví se v nich produkt pro lidi zvenčí. Interní nástroj nemá konkurenci ani ceník; jednoduchá aplikace nepotřebuje glosář. Prázdný podklad je horší než žádný, protože předstírá, že se ta úvaha udělala.

**Výjimka je `demand.md`** – ten dává smysl všude, kde se staví něco pro lidi, **i tam, kde produkt nemá trh**. Interní nástroj, který si lidé obejdou tabulkou, je totéž selhání jako aplikace bez zákazníků. Povinný přesto není: u přírůstku do hotového produktu je „proč“ rozhodnuté, a je-li zapsané, nepřepisuje se.

**`demand.md`** drží problém, jeho nositele, dnešní řešení a jeho cenu, **doklady poptávky odděleně od dojmů**, sekci *Co by verdikt vyvrátilo* a **verdikt o dvou hodnotách** – poptávka doložená, nebo nedoložená; nic mezi tím. Doklad má zdroj (jmenovaný člověk, URL diskuse), dojem ne. **Nedoložená poptávka není vada dokumentu**, ale jeho platný výsledek – a patří pak do `risks.md` jako riziko s nejvyšším dopadem.

Hranice proti `requirements.md` je táž jako u ostatních podkladů: sem **doklady a verdikt**, tam **rozhodnutí, co se z toho postaví**. Hranice proti `competition.md` vede po tom, o kom nález mluví: článek o nástrojích patří ke konkurenci, člověk popisující, jak problém dnes obchází, k poptávce.

**`competition.md`** drží data o trhu i jejich závěr. Začíná sekcí `## Co poměřujeme` – jaký problém řešíme, komu, v jaké kategorii produktu tedy soutěžíme a čím se to má hrubě lišit. **Je to vymezení pole hledání, ne specifikace**; `/specify` ho čte jako hotový vstup. Pak následuje analýza sama (kdo, co, za kolik, co umí) a závěrečná sekce `## Naše pozice a odlišení`: co musíme mít, protože to má každý, co děláme jinak a kde vědomě zaostáváme.

**Závěr žije tady, ne zvlášť** (*Vše o jedné věci pohromadě u ní*); samostatný soubor na odlišení (USP) se nezakládá – byl by třetím místem vedle *MVP* v `requirements.md` a `scenarios.md`, kde se tvrdí, co produkt musí umět.

**`risks.md`** je **registr rizik, ne SWOT analýza silných a slabých stránek.** U každého rizika: čeho se týká, jaký by mělo dopad, jak je pravděpodobné, čím ho mitigujeme a **co se kvůli němu v produktu změnilo nebo přibylo**. Bez toho posledního pole je to seznam obav, který nikoho nezavazuje. Silné stránky a příležitosti drží *Naše pozice a odlišení* v `competition.md`.

Hranice proti sekci *Rizika* v `architecture.md`: sem patří **rizika produktu a trhu** (nikdo to nebude používat, konkurence to udělá dřív, data se nedají získat, legislativa se změní), do návrhu **technická rizika zvoleného řešení** (nezvládne to zátěž, ta knihovna může skončit).

**`scenarios.md`** je **taxativní seznam toho, co uživatel s produktem dělá**, každý scénář krok za krokem od začátku do konce, včetně okrajových a chybových cest. Čte ho ten, kdo ověřuje, že produkt umí, co má, kdo píše nápovědu a odpovědi na časté dotazy, a testování na skutečných lidech.

**Má-li projekt `scenarios.md`, sekce *Hlavní scénáře* v `requirements.md` zaniká** a nahradí ji odkaz (*Single source of truth*). V požadavcích zůstává **proč a pro koho** – persony, user stories, varianty jako produktová rozhodnutí; ve scénářích **jak to člověk provede**. Odkazuje se sem odjinud: *Testovací strategie* v `architecture.md` měří pokrytí proti tomuhle seznamu, stejně jako `plan.md` a `/attack`.

**`glossary.md`** dává *Jednomu termínu pro jednu věc* z `~/.claude/standards/rules.md` místo, kde ten termín stojí zapsaný. U každého pojmu: jak se jmenuje česky, jak v kódu, co znamená a **čím se liší od pojmu, se kterým se plete**. Zakládá se u projektu s netriviální doménou, kde se plete víc entit naráz. **Termíny platné napříč projekty sem nepatří** – ty drží `~/.claude/standards/ptydepe.md` a spravuje je `/ptydepe`.

**`pricing.md`** má smysl jen u produktu, který se prodává. Není to ceník pro web, ale **soupis toho, co z cenového modelu plyne pro produkt**: co který tarif smí, kde jsou limity a co se stane při jejich dosažení, jak vypadá trial a co po něm, jak se přechází nahoru a dolů, co se stane po expiraci a co s daty.

**`operation.md`** drží **poznatky z provozu, ne měsíční report**. Zakládá ho první běh `/evaluate` a každý další **přidává nové období nad starší, aniž maže čísla stará** – trend je důvod, proč ten soubor existuje. U každého poznatku: čeho se týká, číslo, **odkud se to ví**, jak se to dá zopakovat, a **jak se o něm rozhodlo**. Hlavička nese datum běhu a období, za které se měří. **Vyjde-li z ověření, že se zdroji není něco v pořádku**, přibude k tomu **verdikt o důvěryhodnosti dat**: poznatky stojící na číslech se tím označí a nesmí se z nich argumentovat, kdežto ty stojící na struktuře (chybějící omezení, chybějící auditní stopa) platí dál.

**Hranice proti `demand.md` je v čase, ne v tématu.** Tam doklady o tom, že problém existuje, **než** se něco postavilo; sem doklady o tom, co lidé dělají s hotovou věcí. Verdikt v `demand.md` se čísly z provozu nepřepisuje – odpovídá na jinou otázku. Proti `requirements.md` jako u ostatních podkladů: sem doklady a rozhodnutí o poznatku, tam co se z toho postaví (`/specify`).

**Sekce *Rizika* se sem nekopíruje.** Projeví-li se riziko z `risks.md`, zapíše se to jako poznatek s číslem a `risks.md` zůstává tím, čím je – registrem s mitigacemi.
