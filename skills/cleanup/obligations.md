# Co v session zakládá povinnost zápisu

Referenční tabulka pro *Fázi 3* skillu [`/cleanup`](SKILL.md). Je to **obrácený pohled** proti běžnému vytěžování: tam se ptáš, kam patří to, co jsi v session našel, tady jestli nezůstala nesplněná povinnost, o které v session nikdo nemluvil. Neber jako samozřejmé, že průběžná aktualizace proběhla – **empiricky se na ni zapomíná**, a proto tenhle pohled existuje.

Obsah jednotlivých souborů definuje `~/.claude/STRUCTURE.md`; tahle tabulka není druhá definice, ale spouštěč.

**Cesty jsou psané pro režim `docs/`.** V projektu s kořenovým režimem (`~/.claude/STRUCTURE.md`, *Dva režimy umístění*) se překládají do kořene repozitáře.

## Které soubory prověřit

Vždycky: `CLAUDE.md`, `README.md`, `docs/todo.md`, `docs/backlog.md`, `docs/done.md`, `docs/decisions.md`, `docs/rules.md`.

Má-li projekt zadání, k tomu `docs/requirements.md`, `docs/architecture.md` a `docs/plan.md`. **Vede-li produktové podklady** – poznáš z `## Struktura a dokumentace` v `CLAUDE.md` – ještě `docs/demand.md`, `docs/competition.md`, `docs/risks.md`, `docs/scenarios.md`, `docs/glossary.md` a `docs/pricing.md`.

**`docs/operation.md` posuzuj podle toho, jestli soubor existuje, ne podle seznamu v `CLAUDE.md`** – ten se při `/project` nevybírá, protože ho zakládá až první běh `/evaluate`. V seznamu by tedy nestál nikdy a jeho řádek v tabulce níž by se neuplatnil.

**Neexistující soubory přeskoč, nezakládají se tady.** A **zapsaný podklad, který dosud nevznikl, není nález** – je to závazek čekající na svůj krok cyklu. Nález je podklad, kterému se během session rozešel obsah se skutečností.

## Tabulka

| Soubor | Co v session zakládá povinnost zápisu |
|---|---|
| `CLAUDE.md` | vzniklo nebo se změnilo pravidlo, konvence, způsob práce v projektu |
| `README.md` | změnilo se, co projekt je, umí nebo jak se spouští; zároveň ověř, že v něm nezůstal normativní pokyn pro Clauda – ten patří do `CLAUDE.md` nebo `docs/`, viz `~/.claude/STRUCTURE.md` |
| `docs/todo.md` | něco se odložilo, zaparkovalo, označilo „později“ – a je rozhodnuto, že se to udělá |
| `docs/backlog.md` | padl nápad, o kterém se nerozhodlo, že se udělá; **zvlášť ověř, že takový nápad neskončil v `todo.md`** |
| `docs/done.md` | ověř, že v `todo.md` nezbylo nic hotového – přesouvá se průběžně, tohle je jen záchranná síť |
| `docs/decisions.md` | padlo rozhodnutí, zvolila se varianta, něco se zamítlo, změnil se názor |
| `docs/rules.md` | vybrousil se princip, hranice, „takhle to v tomhle projektu děláme vždycky“ |
| `docs/requirements.md` | změnil se produktový záměr – co se staví, pro koho, co je v MVP a co mimo rozsah |
| `docs/architecture.md` | změnil se návrh řešení – architektura, datový model, stavy, technologie, bezpečnostní model |
| `docs/demand.md` | přibyl doklad poptávky nebo dojem o ní, nebo se objevilo zjištění, které zpochybňuje verdikt |
| `docs/competition.md` | zjistilo se něco o konkurenci nebo se posunulo, čím se proti ní vymezujeme |
| `docs/risks.md` | objevilo se riziko, nebo se změnilo, čím mu čelíme; **zvlášť ověř pole *Promítnutí do produktu*** – rozhodlo-li se v session něco kvůli riziku, patří to tam |
| `docs/scenarios.md` | přibyla, změnila se nebo zanikla cesta, kterou uživatel produktem projde – včetně chybové |
| `docs/glossary.md` | zavedl se, přejmenoval nebo upřesnil pojem; **pozor i na pojem, který se v session začal používat mimoděk** |
| `docs/pricing.md` | změnil se tarif, limit, chování po expiraci nebo cokoliv, co z toho plyne pro produkt |
| `docs/operation.md` | padlo rozhodnutí o poznatku z provozu, nebo se ukázalo, že poznatek z minulého běhu neplatí; **čísla starších období se nepřepisují** – přidává se nové období nad ně |
| `CLAUDE.md` → `## Kontrakt příkazů` | přibyl nebo se změnil příkaz na testy, lint, build nebo audit |
| `docs/plan.md` | odpracovaly se úkoly (odškrtnout), nebo se plán rozešel se skutečností |

## Kam co patří, když položku vytěžíš

Druhý směr téže otázky – od nalezené položky k souboru:

| Typ položky | Cílové místo |
|---|---|
| Pravidla, konvence, jak se v projektu pracuje | projektový `CLAUDE.md` |
| Rozhodnutí a jejich zdůvodnění, zavržené varianty | `docs/decisions.md` |
| Obecné principy a hranice, ve kterých se projekt pohybuje | `docs/rules.md` |
| Úkoly a odložené věci, u kterých je rozhodnuto, že se udělají | `docs/todo.md` |
| Nezávazný nápad, o kterém se nerozhodlo | `docs/backlog.md` |
| Hotové úkoly | `docs/done.md` |
| Otevřené otázky čekající na rozhodnutí uživatele | `docs/todo.md` jako běžná položka |
| Změny dotýkající se toho, co projekt je, umí a jak se používá – **popis pro člověka**, nikdy pokyn pro Clauda | `README.md` |
| Doménová specifika (model, procesy, katalogy) | příslušný soubor v `docs/` |
| Cokoliv v Memory | **přesuň do projektového `CLAUDE.md`**, pokud projekt nemá explicitně povolenou Memory |

## Stavy, ve kterých položku najdeš

- **OK** – je zapsaná na správném místě a ve správném znění → neřeš
- **Chybí** – nikde není → zapiš
- **Zastaralá** – je zapsaná ve znění, které už neplatí → přepiš
- **Špatné místo** – je jinde, než kam podle struktury patří → přesuň
- **Duplicitní** – je na víc místech → nech na jednom, ostatní ať odkazují

**Chybějící zápis doplň zpětně v plné kvalitě**, ne jako holou odrážku: u rozhodnutí i proč a jaké varianty padly, u odložených věcí celou úvahu, u principů obecnou formulaci místo popisu jednoho případu. Zároveň přeformuluj, co bylo zapsáno ve spěchu nebo se od té doby posunulo.

**Chybí-li některý ze standardních souborů úplně, nezakládej ho** – vypiš, které chybí, a nabídni `/project`, který strukturu doplní celou a konzistentně. Výjimka: má-li session obsah, který do chybějícího souboru jednoznačně patří, soubor založ a obsah zapiš – jinak by se ztratil. Nedává-li standardní struktura pro tenhle projekt smysl (jednorázový scratch, cizí read-only repozitář), konstatuj to jednou větou a přeskoč to.
