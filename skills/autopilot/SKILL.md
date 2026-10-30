---
name: autopilot
description: Skill se použije, když uživatel zadá "/autopilot" (volitelně se zúžením), nebo chce, aby Claude pracoval sám beze něj a bez přerušování – "pracuj beze mě", "odpracuj z todo, co zvládneš sám", "jeď úkoly z todo bez ptaní", "vezmi úkoly, které nepotřebují moje rozhodnutí". Z docs/todo.md projektu vybere jen úkoly, které nepotřebují rozhodnutí ani vstup uživatele, a odpracuje je jeden po druhém celé – průběžná kontrola, přesun do done.md, commit a push – bez jediné otázky. Narazí-li uprostřed úkolu na rozhodnutí, vrátí svoje změny, otázku i s variantami zapíše k položce a jede dál. Po každém úkolu si změří kontext; nad prahem rozdělaný úkol dokončí a skončí s pokynem pokračovat v nové session. Na rozdíl od /next, který frontu nabídne a nechá uživatele vybrat, tenhle skill vybírá sám a jen to, kde není co vybírat; na rozdíl od /implement nebere úkoly z implementačního plánu.
argument-hint: [zúžení]
allowed-tools: [Read, Edit, Write, Glob, Grep, Bash, Agent, AskUserQuestion]
---

# Autopilot

## Co skill dělá

Odpracuje z `docs/todo.md` všechno, co jde udělat **bez uživatele**: vybere úkoly, které nepotřebují jeho rozhodnutí ani vstup, a jeden po druhém je vyřeší celé – od práce přes průběžnou kontrolu a přesun do `done.md` po commit a push. Mezi úkoly se neptá a nezastavuje. Běh končí, když samostatné úkoly dojdou, nebo když kontext přeleze práh – rozdělaný úkol pak ještě dokončí a nový nezačne.

Režimy nemá. Argument je **volné zúžení** jako u `/next` – `/autopilot review` vezme jen položky, v jejichž názvu, textu nebo nadpisu sekce se výraz vyskytuje, bez ohledu na velikost písmen. Bez argumentu jde o celou frontu.

## Co skill nedělá

- **Nenabízí a nenechává vybírat.** Seřadit všechno rozdělané a nechat uživatele zvolit je `/next`; tenhle skill bere jen to, u čeho volit není co, a zbytek přeskočí.
- **Neodpracovává implementační plán.** Úkoly z `docs/plan.md` s jejich akceptačními kritérii drží `/implement`.
- **Nenavazuje na přerušený běh.** Sekce `## Přerušený běh` patří `/continue`, i když by její položky splnily kritéria – nesou kontext, podle kterého se má navázat, a ten čte on.
- **Nezapisuje zbytek práce k navázání.** Přerušení dlouhého průchodu s frontou, která se má zapsat, je `/break`; tady se nic nepřerušuje – běh končí na hranici úkolu a fronta zůstává v `todo.md`, kde byla.
- **Neuklízí session.** Řetěz konce session drží `/end` a pouští ho uživatel.
- **Nedělá revizi vlastní práce.** Průběžná kontrola je povinná po každém úkolu; posudek toho, co běh vyrobil, je `/review` v nové session.

## Jak je to postavené uvnitř

| Krok | Kdo | Proč zrovna on |
|---|---|---|
| Rozparsování `todo.md` po sekcích a obsazené větve | `~/.claude/skills/next/collect.py` | Umí to už pro `/next` a ví, nad kterou větví běží živá session. |
| Třídění na samostatné a nesamostatné | **vlastní** | Jádro skillu – úsudek nad kritérii v *Hranicích*. |
| Práce na úkolu | **vlastní**, podle pravidel projektu | Úkol se dělá tak, jako by ho zadal uživatel; mechanickou práci deleguje podle `~/.claude/standards/delegation.md`. |
| Průběžná kontrola po úkolu | kontrakt příkazů projektu | Hook `verify.sh` se spustí až na konci odpovědi, ne mezi úkoly uvnitř ní. |
| Měření kontextu | `context.py` v adresáři skillu nad funkcí `measure` z `~/.claude/hooks/handoff.py` | Hook `handoff.py` se ozve jen při zprávě uživatele, a ta v autonomním běhu nepřijde. |

**Skripty jsou implementační detail.** Závazné je: práh je týž jako doporučení přerušení v `~/.claude/skills/handoff.md`, *Práh kontextu*; nejde-li kontext změřit, běh se nerozjede; nový úkol se nezačne nad prahem.

## Hranice

Platí pro celý běh od *Fáze 1* dál.

**Od *Fáze 1* se neptá na nic – ani když to vypadá, že je uživatel u počítače.** `AskUserQuestion` patří jen do *Fáze 0*. Skill nemá jak ověřit, že uživatel odpoví hned, a otázka, na kterou neodpoví, zastaví celý běh do jeho návratu – přesně to, čemu má skill zabránit. Kde by se jinak ptal, platí *Zaseknutí* ve *Fázi 2*.

**Práh kontextu posouvá jen číslo zadané ve *Fázi 0*.** „Dodělej co nejvíc“ ani „nespěchej“ neposouvá mez, kritéria výš ani neopravňuje k odchylce od pravidla projektu – je to přání o rozsahu, ne pokyn.

**Úkol je samostatný, jen když splní všechna kritéria naráz. Při pochybnosti propadá** – přeskočený úkol nic nestojí, úkol rozhodnutý jinak, než by rozhodl uživatel, se musí najít a vrátit.

1. **Je to úkol, ne otázka.** Položka, která má něco rozhodnout, zvážit nebo vybrat mezi variantami, které nikdo nevybral, propadá. Položky sekce `## Rozhodnuto k zapracování` toto kritérium splňují a jdou první; ostatní kritéria musí splnit jako každá jiná. **Souhlas zapsaný v textu položky** („rozhodnuto, klidně smaž“) **kritérium 3 ani 4 nenahrazuje** – v autonomním běhu ho nikdo nepotvrdí, že platí i dnes.
2. **Hotovost jde poznat z textu a ze souborů.** Z položky a z projektu je jasné, jak vypadá výsledek a čím se ověří. „Vylepšit výkon výpisu, je pomalý“ propadá – o tom, co je dost rychlé, by rozhodl skill.
3. **Nepotřebuje nic, co zná jen uživatel** – přístupy, účty, údaje, souhlas, text jeho hlasem, klientský kontext, který v projektu není.
4. **Nemá nevratný ani vnější dopad** – nasazení, mail, platba, zápis do cizího systému, mazání nebo přepis dat, která nejsou v gitu – včetně všeho, co pokrývá `.gitignore` –, globální pravidlo propagované do jiných projektů. Commit a push vnějším dopadem nejsou, o těch uživatel rozhodl spuštěním skillu.
5. **Nemění princip, pravidlo ani rozsah** – úkol, který přepisuje `docs/rules.md`, rozhodnutí v `docs/decisions.md` nebo zadání, propadá (`~/.claude/standards/rules.md`, *Nerozhoduj potichu nad rámec zadání*).
6. **Je na řadě** – nemá za názvem `od <YYYY-MM-DD>` s datem po dnešku (`date +%F`), neleží ve větvi, nad kterou podle `collect.py` běží jiná session, nestojí v `## Přerušený běh`, `## Kola návrhu` ani `## Parkované v session` a nenese odstavec `**Čeká na rozhodnutí:**`.

**Technika provedení rozhodnutím není** – jak pojmenovat proměnnou, kam do sekce zařadit odstavec, jak formulovat větu –, **ale jen dokud existuje varianta, která neporuší žádné pravidlo ani konvenci projektu.** Tu je třeba nejdřív hledat; nejde-li najít, je to *Zaseknutí*. **Odchylka od pravidla projektu rozhodnutím je, i drobná.** „Příkaz z kontraktu zopakuju v README, protože ho čte člověk zvenčí“ je výjimka ze *Single source of truth*, kterou si skill odsouhlasil sám – patří do *Zaseknutí*, ne do provedení. **Totéž platí pro obejití odkazem:** jde-li úkol splnit jen tak, že se jedno ze dvou pravidel ohne – opis proti *Single source of truth*, nebo odkaz tam, kde má čtenář dostat obsah –, je to *Zaseknutí*.

**Kód mimo rozsah položky se nemění.** Oprava cizí chyby, i jednořádková, je vedlejší nález, ne součást úkolu. **Přeskočit, vypnout nebo oslabit test či jinou kontrolu nejde nikdy** – ani dočasně, ani u testu, na který skill nesáhl.

**Fronta je pevná od *Fáze 1*.** Položka, která během běhu do `todo.md` přibude – vedlejší nález, odložený krok –, se v tomhle běhu nebere. Vznikla z vlastní práce běhu a skill, který si frontu sám plní, nemá konec. Nápady a vedlejší nálezy zapisuje podle `~/.claude/standards/rules.md`, *Kam co zapsat*, a nepouští se do nich.

------

## Fáze 0 – Příprava

Společný začátek je v `~/.claude/skills/preflight.md`, **včetně bodu 4** – skill mění soubory a dědit červený stav nesmí. Bod 5 odpadá, skill pracuje nad frontou, ne nad diffem větve. Navíc:

1. **Všechny otázky běhu padnou tady.** Rozpracované změny z bodu 3 i červená kontrola z bodu 4 se řeší teď, dokud je uživatel u toho; běh se nerozjede, dokud nejsou vyřešené.
2. **Změř kontext:** `python3 ~/.claude/skills/autopilot/context.py`. Vrátí-li chybu, **skonči nehotovým verdiktem** – bez měření by běh neměl mez a přelezl by celé okno. Je-li `over` už teď `true`, skonči taky: doporuč `/end` → `/clear` → `/autopilot` v nové session.
3. **Commituje se vždycky**, i v projektu bez `## Autocommit`, a pushuje se, vrací-li `git remote get-url origin` adresu. Spuštění skillu je rozhodnutí commitovat a bez commitu po úkolu nejde úkol vrátit ani oddělit od dalšího. Bez autocommitu to řekni jednou větou.
4. **Projekt bez `docs/todo.md`** frontu nevede – řekni to a skonči nehotovým verdiktem.

## Fáze 1 – Fronta

Pusť `python3 ~/.claude/skills/next/collect.py` z adresáře session. Ze všech jeho klíčů tě zajímá jen `todo` a `branches`; nic jiného nečti.

Projdi každou položku proti kritériím z *Hranic*, po zúžení z argumentu. Popisy jsou ve výstupu zkrácené – je-li to pro rozhodnutí potřeba, dočti položku ze souboru. **Pořadí:** `## Rozhodnuto k zapracování`, pak ostatní v pořadí souboru.

Vypiš frontu a **hned pokračuj *Fází 2*** – bez otázky, výpis je informace, ne návrh ke schválení:

```
**Fronta autopilota** – <N> k odpracování, <M> přeskočeno

**Odpracuju**
1. <název položky>

**Přeskakuju**
- <název položky> – <které kritérium a proč, jednou větou>
```

Vypisuj to jako Markdown, ne jako blok kódu, a řádky nezalamuj natvrdo. Počty spočítej z obou seznamů, ne z hlavy.

Je-li seznam *Odpracuju* prázdný, přejdi rovnou na *Fázi 3*.

## Fáze 2 – Úkol

Pro každou položku seznamu *Odpracuju*, v jeho pořadí:

1. **Načti položku celou ze souboru** a soubory, na které odkazuje. Je-li teprve teď vidět, že kritérium nesplňuje, je to *Zaseknutí* – bez změn k vrácení.
2. **Odpracuj ji celou** podle pravidel projektu a `~/.claude/standards/rules.md`, jako by ji zadal uživatel: doc-first, průběžné zápisy do `decisions.md`, propagace změny. Pamatuj si každou cestu, na kterou sáhneš – podle nich se commituje i vrací.
3. **Pusť průběžnou kontrolu** podle *Kontraktu příkazů* projektu. Červená, kterou způsobila tvoje změna, se opravuje; nejde-li opravit bez zásahu, který kritéria vylučují, je to *Zaseknutí*.
4. **Přesuň položku do `docs/done.md`** do zrcadlové sekce s datem z `date +%F` (`~/.claude/standards/structure.md`, *`done.md`*).
5. **Commitni jmenované cesty** – jen se zelenou kontrolou z kroku 3 – zprávou předanou heredocem a pushni, má-li projekt remote (`~/.claude/standards/rules.md`, *Commituj jmenované cesty, ne `-A`*). Selže-li push, zkus ho ještě jednou po `git pull --rebase`; selže-li znovu, je to důvod nehotového verdiktu a běh končí – další commity by se jen hromadily lokálně.
6. **Pokračuj *Fází 3*.**

### Zaseknutí

Ukáže-li se uprostřed úkolu, že potřebuje rozhodnutí nebo vstup uživatele – dvě platná pravidla si odporují, rozumných řešení je víc, kontrola nejde dostat do zelené bez vyloučeného zásahu –, **netipuj**:

1. **Vrať vlastní necommitnuté změny té položky** – `git restore --staged --worktree` nad cestami, na které jsi sáhl, a smazání souborů a adresářů, které jsi založil. Zapsala-li do týchž cest mezitím jiná session (`git diff` ukazuje změny, které nejsou tvoje), nevracej nic a skonči nehotovým verdiktem – vrácení by smazalo cizí práci.
2. **K položce v `todo.md` připiš odstavec** `**Čeká na rozhodnutí:**` – otázku, varianty i s důsledkem každé, doporučení a co se už zjistilo, ať příští běh nezačíná od nuly. Tvar varianty drží `~/.claude/standards/rules.md`, *Ptej se postupně, ne všechno najednou*.
3. **Commitni jen `todo.md`** a pushni stejně jako u hotového úkolu.
4. **Pokračuj *Fází 3*.**

### Cizí červená kontrola

**Za cizí se počítá jen červená, která padá i na `HEAD` bez tvých změn** – ověř to kontrolou v dočasném worktree (`git worktree add --detach <scratchpad>/head HEAD`, po ověření `git worktree remove`), ne přes `git stash`, který by sebral i cizí rozdělanou práci. To, že jsi na padající místo nesáhl, nestačí: tvoje změna mohla změnit, co ono čte. Jinak je červená tvoje a platí krok 3.

U cizí červené **se body 2 a 3 *Zaseknutí* nedělají** – položka rozhodnutí nepotřebuje, zablokovalo ji prostředí. Pusť kontrolu ještě jednou:

- **Projde napodruhé** → nestabilní test zapiš jako vedlejší nález do `todo.md` a pokračuj krokem 4 *Fáze 2*.
- **Padá znovu** → vrať vlastní změny položky (bod 1 *Zaseknutí*), nic necommituj a přejdi na *Fázi 4* s nehotovým verdiktem, který jmenuje padající kontrolu. Zasekl by se na ní každý další úkol.

## Fáze 3 – Měření a další úkol

Po každém úkolu, hotovém i zaseknutém, pusť `python3 ~/.claude/skills/autopilot/context.py`.

- **`over` je `false` a seznam *Odpracuju* má další položku** → vrať se do *Fáze 2* s ní. Bez ohlášení a bez otázky.
- **`over` je `true`** → další úkol nezačínej a přejdi na *Fázi 4*. Nezačínej ani „malý“ úkol – odhad velikosti úkolu je to, co se u předchozích ukázalo jako nespolehlivé.
- **Seznam došel** → *Fáze 4*.
- **Skript vrátil chybu** → *Fáze 4* s nehotovým verdiktem; pokračovat bez meze nejde.

**Kompaktace se nepoužívá** a nečeká se na ni. `/compact` model spustit nemůže a automatická přijde kdykoliv, i uprostřed úkolu; konec na hranici úkolu je jediné místo, kde v souborech nic nechybí.

## Fáze 4 – Závěr

```
## Autopilot

- **Hotovo:** <N> úkolů · **Zaseknuto:** <M> · **Přeskočeno:** <K> · **Zbývá samostatných:** <L>
- **Kontext:** <N>k z prahu <P>k
- **Průběžná kontrola:** <poslední příkaz a návratový kód>

**Hotové**
- <název> – <commit hash z `git rev-parse --short HEAD` po commitu>

**Čeká na rozhodnutí**
- <název> – <otázka jednou větou>

**Přeskočené**
- <název> – <důvod>
```

Vypisuj to jako Markdown, ne jako blok kódu, a řádky nezalamuj natvrdo. Prázdnou skupinu vynech. Nešlo-li kontext změřit, napiš na jeho řádek místo čísla chybu z `context.py`.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Běh je hotový a ověřený – samostatné úkoly došly, zbytek fronty čeká na tvoje rozhodnutí.`
- `Běh je hotový a ověřený – kontext dosáhl prahu, zbylé samostatné úkoly odpracuje další běh v nové session.`
- `Běh hotový není – brání tomu: <konkrétní seznam>.`

Pak blok **Kudy dál** podle `~/.claude/skills/handoff.md`, *Blok Kudy dál*:

- **nad prahem:** `/end`, pak `/clear`, a `/autopilot` až v nové session – kontext je na <N>k, zbývá <L> samostatných úkolů
- **fronta došla a čeká něco na rozhodnutí:** `/next` – nabídne i zaseknuté položky; je-li kontext nad prahem nabídky přerušení (`~/.claude/skills/handoff.md`, *Práh kontextu*), `/end`, pak `/clear` a `/next` až v nové session
- **běh hotový není:** co musí uživatel udělat sám (opravit kontrolu, vyřešit push, rozsoudit souběžnou session), pak `/autopilot` znovu – je-li kontext nad prahem nabídky přerušení, `/end`, pak `/clear` a `/autopilot` až v nové session
- **volitelně:** `/end`, pak `/clear`, a `/review` až v nové session – posudek toho, co běh vyrobil, patří do session, která to nepsala
