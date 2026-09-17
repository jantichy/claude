---
name: diagram
description: Skill se použije, když uživatel zadá "/diagram", nebo chce z navrženého datového modelu projektu nakreslit interaktivní vizualizaci – ER diagram všech tabulek se sloupci a constrainty, stavový prostor s přechody, ortogonální osy – jako artefakt, případně už existující artefakt s mapou modelu překreslit na aktuální stav dokumentace nebo jiné větve. Čte dokumentaci modelu v projektu a nic do projektu nezapisuje. Na rozdíl od /report, který kreslí grafy z naměřených dat, tenhle skill kreslí strukturu návrhu; na rozdíl od /consistency dokumentaci neaudituje, rozpory jen ohlásí.
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Skill, AskUserQuestion, Artifact]
---

# Diagram

## Co skill dělá

Z dokumentace datového modelu projektu postaví **interaktivní stránku jako artefakt** a při dalším volání **tentýž artefakt aktualizuje** na stejném odkazu. Na stránce je:

- **jádro modelu** – malý ER diagram hlavních entit, ze kterého je vidět, kde se potkávají,
- **celé schéma** – všechny tabulky a cizí klíče; po kliknutí na tabulku lidský popis, vazby oběma směry, sloupce, constrainty, invarianty a indexy,
- **stavový prostor** – klikací diagram stavů, kde přechody nesou jméno funkce a rozlišení spouštěče,
- **ortogonální osy a vedlejší automaty**, pokud je model má.

Skill nemá režimy. Jestli vzniká nový artefakt, nebo se aktualizuje existující, pozná sám.

## Co skill nedělá

- **Nezapisuje do projektu.** Žádný diagram do `docs/`, žádná větev, žádný commit. Diagram v repozitáři by byl druhá kopie modelu vedle textu a rozešel by se s ním; kdyby ho projekt jednou chtěl mít, je to rozhodnutí projektu, ne vedlejší efekt tohohle skillu.
- **Neaudituje dokumentaci.** Narazí-li na rozpor nebo mezeru (hrana, kterou katalog nejmenuje, klíč bez cíle), ohlásí ji v závěru. Opravuje a hledá soustavně `/consistency`.
- **Nekreslí grafy z dat.** Report z exportů a měření je `/report`; tenhle skill kreslí strukturu návrhu, ne čísla.
- **Nečte schéma z kódu.** Zatím jen z dokumentace modelu. Projekt, který model v dokumentaci nemá, dostane odpověď, že není z čeho kreslit – viz *Fáze 1*.

## Jak je to postavené uvnitř

| Krok | Kdo | Proč zrovna on |
|---|---|---|
| Vizuální návrh stránky a témata | skill `artifact-design` | drží pravidla pro artefakty – barvy, typografii, světlý a tmavý režim |
| Kreslení diagramů v SVG | skill `artifact-diagramming` | drží mechaniku inline SVG a to, co má diagram ukazovat |
| Hledání a publikace artefaktu | nástroj `Artifact` | jediný kanál, kudy artefakt vzniká a aktualizuje se |
| Vytěžení modelu z dokumentace | **vlastní** – jednorázový skript ve scratchpadu | formát dokumentace je v každém projektu jiný; skript se píše na míru a zahazuje |
| Co kreslit, co přiznat jako nejisté, popisy entit | **vlastní** | úsudek nad konkrétním modelem, neumí to nikdo jiný |

**Volané skilly, nástroj i skripty jsou implementační detail, ne rozhraní.** Závazné je: projekt zůstane netknutý, na stránce není hrana ani vazba, kterou dokumentace neuvádí, bez přiznání, čísla na stránce se počítají z dat a zdroj (větev, commit, datum) je na stránce vidět.

## Fáze 0 – Příprava

Společný začátek drží `~/.claude/skills/PREFLIGHT.md`. **Body 1 a 2 platí, bod 3 jen zmínit** – skill nic nemění, takže rozpracované změny ve stromu neblokují, jen se řekne, že se kreslí i z nich. **Body 4 a 5 odpadají**, skill nesahá na kód ani na diff větve.

Navíc:

1. **Stojíš-li v kořeni kontejneru worktree layoutu, zeptej se, ze kterého worktree kreslit** – nabídni výpis `git worktree list`. Uživatel mohl mluvit o větvi, která mezitím byla sloučená a smazaná; v tom případě to řekni a nabídni hlavní větev, **nekresli potichu z jiného místa, než o jakém mluvil**.
2. **Zdroj vyrob příkazy, ne z hlavy:** `git -C <worktree> branch --show-current`, `git -C <worktree> rev-parse --short HEAD`, `date +%F`. Jdou na stránku a do závěru.
3. **Načti skilly `artifact-design` a `artifact-diagramming`** dřív, než napíšeš první řádek stránky.
4. **Načti `~/Dev/context/text/typography.md`** – popisy a titulky jsou český text.

## Fáze 1 – Co je v projektu k nakreslení

Najdi dokumentaci modelu: podle `CLAUDE.md` projektu (seznam dokumentů návrhu), jinak globem na `docs/*model*`, `docs/*schema*`, `docs/*transitions*`, `docs/*state*`.

- **Model v dokumentaci není** → řekni to a skonči závěrečným verdiktem „není hotová“. Schéma z migrací nebo ORM se zatím nečte.
- **Je** → zjisti, v jaké podobě: bloky schématu (tabulka, sloupce, `NULL`/`NOT NULL`, komentář), SQL bloky s constrainty, tabulky invariantů a indexů, katalog stavů a přechodů. **Podoba určuje, co stránka ponese** – sekce, pro kterou dokumentace nemá podklad, na stránku nepatří.

## Fáze 2 – Existující artefakt

Název stránky je **stálý a odvozený od projektu**: `Mapa modelu <projekt>` s projektem v 2. pádě podle jeho názvu nebo slugu v `CLAUDE.md` (`Mapa modelu rezervací`). Podle něj se artefakt hledá.

1. `Artifact` s `action: "list"` a hledej ten název.
2. **Jeden** → přečti ho (`action: "read"`) a z hlavičky stránky zjisti, z jaké větve a commitu vznikl. Porovnej s dneškem: `git diff --stat <starý>..HEAD -- docs/` a u změněných dokumentů přečti diff. **Přejmenování entit a přesuny polí promítni do celé stránky** – do popisků, titulků, popisů, nápověd, ne jen do dat.
3. **Žádný** → vznikne nový.
4. **Víc než jeden** nebo si nejsi jistý → zeptej se přes `AskUserQuestion`, který aktualizovat, a nabídni i založení nového.

Starý commit už v historii být nemusí (větev sloučená přes squash, smazaná). Pak diff nedělej, řekni to a stránku postav celou znovu.

## Fáze 3 – Vytěžení modelu skriptem

**Data do stránky se tahají skriptem, nikdy ručním opisem.** Ruční opis tří set sloupců vypadá hotově a chyba v něm se nepozná. Skript piš do scratchpadu, na míru formátu dokumentace, a výstup ulož jako JSON.

Co vytáhnout, má-li to dokumentace:

- **Tabulky a sloupce** – jméno, nullabilita, komentář. Komentář společný pro skupinu polí (závorky `─┐ │ ─┘`) spoj do jednoho a znaky závorek odstraň.
- **Constrainty** – `CHECK`, `UNIQUE`, `EXCLUDE`, `CREATE … INDEX`. Víceřádkový zápis dočti do konce podle závorek. SQL blok přiřaď podle nadpisu nad ním („Nad `Placeholder`:“) nebo podle `ON <tabulka>`, teprve pak k předchozímu bloku schématu.
- **Cizí klíče** – kde je dokumentace jmenuje výslovně, převezmi je; kde je odvozuješ z názvu sloupce (`*_id`, `*_by`), **označ je na stránce jako odvozené**. Identifikátory u cizích dodavatelů (`proforma_id`, `gateway_id`) vazbou nejsou.
- **Invarianty a indexy** – s přiřazením k tabulkám. Kde dokumentace tabulku neuvádí, přiřaď podle obsahu a **zapamatuj si to pro závěr**.
- **Stavy a přechody** – z katalogu. Tabulky přechodů bývají volným textem, ty smíš převést ručně do seznamu hran, ale jen **doslova podle katalogu**.

**Hrany kresli jen tam, kde je dokumentace jmenuje.** Obecný zápis („`*_PAID` s přijatou platbou → `*_UNPAID`“, „obnoví do původního stavu“) se nerozepisuje odhadem do konkrétních hran. Buď ho rozepiš jen tam, kde to katalog jinde výslovně dokládá, nebo hranu nenakresli a uveď to v popisku diagramu. Odhadnutá hrana s poznámkou „nejisté“ se čte jako hrana.

**Ortogonální osa není stav.** Smazání, dobropis, výmaz osobních údajů nebo stav platby kartou se nekreslí jako uzel v mřížce stavů; patří do panelu stavu („bez změny stavu“) a do vlastní sekce os.

**Ověř výstup skriptu proti zdroji dřív, než ho použiješ:**

- počet tabulek proti výpisu entit v dokumentaci,
- počet constraintů proti grepu řádků začínajících `CHECK`, `UNIQUE`, `CREATE`, `EXCLUDE`,
- počet přechodů proti číslu v nadpisu katalogu, má-li ho („Přechody partie (44)“),
- u 3 tabulek s nejvíc sloupci počet sloupců ručně proti bloku.

Nesedí-li něco, oprav skript a pusť znovu. **Nepokračuj s čísly, o kterých víš, že nesedí.**

## Fáze 4 – Popisy entit

Ke každé tabulce napiš **jeden až dva odstavce pro člověka**: co to je, k čemu slouží, proč v modelu je a co zajišťuje. Piš z výkladu v dokumentaci u té entity, ne z hlavy.

- Doménovým slovům dej přednost před jmény sloupců; identifikátor jen tam, kde je potřeba.
- **Kde si pomáháš vlastními slovy nebo příkladem, který v dokumentaci není, zapamatuj si to** – jde to do závěru ke kontrole.
- Česká typografie podle `typography.md`.

## Fáze 5 – Stavba stránky

Stránku stav podle `artifact-design` a `artifact-diagramming`. Obsah:

| Sekce | Co na ní je |
|---|---|
| Hlavička | název projektu, větev, commit, datum – z *Fáze 0* |
| Jádro modelu | malý statický ER diagram hlavních entit; tvrzení v nadpisu, co z něj plyne |
| Celé schéma | všechny tabulky ve skupinách podle oblastí; vazby na tenanta skryté přepínačem, značka u tabulek, které tenanta nesou přímo; po kliknutí popis, vazby, sloupce, constrainty, invarianty, indexy |
| Stavový prostor | klikací mřížka stavů; po kliknutí přechody ven s názvem funkce, slabě přechody dovnitř, panel se vším, co stav nemění |
| Osy a vedlejší automaty | jen má-li je dokumentace |

- **Počty na stránce počítej z vložených dat** (`FK.length`), nepiš je do textu natvrdo.
- **Rozlišení spouštěče** (člověk, vnější systém, periodický běh) kóduj tvarem čáry i barvou a dej k tomu legendu.
- Data vlož jako JSON do stránky; před vložením nahraď `</` za `<\/`.
- Soubor ulož do scratchpadu jako `diagram-<slug>.html` – stejná cesta během session znamená stejný odkaz.

## Fáze 6 – Ověření a publikace

1. **Syntaxe skriptů stránky:** vytáhni obsah `<script>` do souborů a pusť `node --check`. Selže-li, oprav a pusť znovu.
2. **Jeden pohled** na vykreslenou stránku, je-li k dispozici prohlížeč (Chrome DevTools); jinak to v závěru přiznej.
3. **Publikuj:** nový artefakt s `favicon` a popisem, existující přes `url` z *Fáze 2* a bez `favicon`.

## Časté chyby

- **Kreslí se z jiného místa, než o jakém uživatel mluvil.** Větev byla sloučená a worktree zmizel; agent vezme hlavní větev a řekne to až na konci. Zeptej se na začátku.
- **Obecný zápis přechodu se rozepíše odhadem.** `restore*` „do všech stavů, ze kterých mohla být smazána“ nebo `unpayCard` do všech `*_PAID` – na stránce pak jsou hrany, které katalog netvrdí.
- **Smazání jako uzel mezi stavy.** Diagram tím tvrdí, že je to stav, a model říká opak.
- **Počet napsaný z hlavy.** „46 cizích klíčů“ bylo 46 bez vazeb na tenanta a 59 s nimi. Čísla se na stránce počítají, v závěru opisují z výstupu.
- **Parser přiřadí SQL blok předchozí tabulce.** Constrainty placeholderu skončily u hodnot placeholderu, protože blok „Nad `Placeholder`:“ stál až za oběma schématy.
- **Useknutý víceřádkový `CHECK`** se přilepí jako komentář k poslednímu sloupci.
- **Přejmenování se promítne jen do dat.** Nadpisy a popisky dál mluví o košíku, když model už zná objednávku.

## Fáze 7 – Závěr

```
## Mapa modelu hotová

- **Artefakt:** <odkaz> – <nový / aktualizovaný>
- **Zdroj:** <větev> @ <commit>, <datum>
- **Obsah:** <tabulek>, <vazeb> (z toho <na tenanta>), <sloupců>, <constraintů>, <stavů>, <přechodů> – čísla z výstupu skriptu

**Změny oproti minulé verzi**
- <co se v modelu změnilo a jak se to promítlo, nebo „nová stránka“>

**Ke kontrole**
- <hrany a vazby vynechané nebo odvozené, přiřazení invariantů podle obsahu, vlastní slova v popisech>

**Rozpory v dokumentaci**
- <co skill cestou našel, nebo „žádné“>

**Nezkontrolováno**
- <vykreslení, úzká obrazovka, …, nebo „nic“>
```

Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo – `~/.claude/RULES.md`, *Styl odpovědí*.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Mapa modelu je hotová a ověřená, můžeš ji otevřít.`
- `Mapa modelu hotová není – brání tomu: <konkrétní seznam>.`
