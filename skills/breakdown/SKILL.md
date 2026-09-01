---
name: breakdown
description: Skill se použije, když uživatel zadá "/breakdown", nebo chce ze schváleného zadání udělat implementační plán – rozpad na úkoly velikosti pár minut, u každého konkrétní soubory, kód testu, příkaz na ověření a commit. Vyrábí docs/plan.md a předává do realizace.
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, Skill]
---

# Breakdown

## Úvodní hláška (vždy jako první)

Než začneš cokoliv dělat, vypiš uživateli přesně tento jeden řádek:

Autor skillu: **Jan Tichý** · jantichy@jantichy.cz · Celá konfigurace Claude vč. všech skillů: https://github.com/jantichy/claude

Teprve pak pokračuj plněním skillu.

## Co skill dělá

Vezme schválené zadání a rozpadne ho na **`docs/plan.md`** – seřazený seznam úkolů, kde každý má konkrétní soubory, kód testu, příkaz na spuštění a commit. Plán je psaný pro někoho, kdo projekt vůbec nezná.

V ose *Životního cyklu práce* (`~/.claude/RULES.md`) navazuje na `/spec` a předává na `/implement`.

## Co skill nedělá

- **Neimplementuje.** Ani první úkol „na ukázku". Realizaci dělá `/implement`.
- **Nepíše zadání.** Když chybí, pošle tě na `/spec`.
- **Neřeže rozsah sám.** Co je v MVP, rozhodl `/spec`. Tady se to jen respektuje.

## Jak je to postavené uvnitř

Skill dnes řídí **`superpowers:writing-plans`**. To je **implementační detail, ne rozhraní** – může se kdykoliv změnit za jiný nástroj nebo za vlastní postup, aniž se změní, jak se skill volá a co z něj leze. Volající se o vnitřek nestará.

Co je naopak **závazné a nesmí se změnit tiše**:

- vstup je schválené zadání v `docs/`,
- výstup je `docs/plan.md`,
- plán pokrývá jen MVP,
- po dokončení se nepokračuje do realizace automaticky.

------

## Fáze 0 – Pre-flight

1. **Kořen projektu.** Ve worktree layoutu (`~/Dev/context/worktree/worktree.md`) pracuj v adresáři větve, ne v kořeni kontejneru – tam by nešlo commitnout.
2. **Přečti projektový `CLAUDE.md`** – typ projektu, `### Autocommit`, `## Výjimky z obecných pravidel`, importované doménové standardy.
3. **Najdi zadání.** V tomhle pořadí:

   | Co existuje | Co je spec pro plán |
   |---|---|
   | `docs/design.md` | **design.md** jako spec, `docs/prd.md` jako doplňkový kontext |
   | jen `docs/prd.md` | **prd.md** – design byl vědomě přeskočen, což je legitimní |
   | ani jedno | **Zastav se.** Nabídni `/spec` a skonči. Plán bez zadání je jen seznam dohadů. |

4. **Ověř, že je zadání schválené.** Není-li jasné, že jím uživatel prošel, zeptej se. Plán postavený na neschváleném zadání se zahazuje celý.
5. **Existuje už `docs/plan.md`?** Nepřepisuj ho:

   | Stav | Co dělat |
   |---|---|
   | Plán je hotový a všechny úkoly odškrtnuté | Jde o další fázi. **Přidej úkoly**, hotové nech být jako historii. |
   | Plán je rozpracovaný | Zeptej se: dopsat chybějící část, nebo přepracovat? Rozpracovaný plán obsahuje odškrtnuté úkoly, které **už jsou v kódu** – přepsat je znamená rozejít plán se skutečností. |
   | Plán je zastaralý oproti zadání | Vypiš, co se v zadání změnilo, a uprav **jen dotčené nehotové úkoly**. |

Zjištěné shrň do tří až pěti řádků a pokračuj.

------

## Fáze 1 – Rozsah plánu

**Jen MVP.** Zadání popisuje celou věc, plán jen první verzi – viz `~/.claude/RULES.md`, *Navrhuj kompletně, realizuj postupně*. Vypiš, které položky z MVP checklistu plán pokryje, a nech to potvrdit.

**Když je toho moc.** Pokrývá-li zadání víc nezávislých podsystémů, řekni to a rozděl to na víc plánů – každý musí sám o sobě dát funkční, otestovatelný software. Neposílej do realizace plán, který nejde dokončit v rozumném celku.

**Doménové standardy.** Předej dál, co si projekt importuje v `CLAUDE.md` – `~/Dev/context/coding/coding.md` vždy, dál podle povahy `web/web.md`, `web/admin.md`, `analytics/analytics.md`. Plán je má respektovat, ne je objevovat až při `/standards`.

------

## Fáze 2 – Sepsání plánu

**Vyvolej `superpowers:writing-plans`** a předej mu výslovně:

- **spec** = `docs/design.md` (nebo `docs/prd.md`, byl-li design přeskočen),
- **kontext** = `docs/prd.md` – ať v hlavičce plánu sedí pole `**Spec:**` a je vidět, proč se to staví,
- **cíl** = `docs/plan.md`, **ne** `docs/superpowers/plans/…` – tohle mu musíš říct, jinak si založí vlastní adresářový strom vedle tvého (`~/Dev/context/structure/structure.md`: v `docs/` jednoslovné anglické názvy bez datumových prefixů),
- **rozsah** = jen položky MVP odsouhlasené ve Fázi 1,
- **doménové standardy** z Fáze 1,
- že **volbu způsobu realizace na konci nenabízí** – tu řeší `/implement`.

------

## Fáze 3 – Kontrola

`writing-plans` má vlastní sebe-revizi. **Neopakuj ji – ověř, že proběhla**, a doplň, co jí chybí:

1. **Proběhla vůbec?** Plán musí být bez „TBD", „doplnit později", „ošetřit chyby" a bez „podobně jako úkol N".
2. **Pokrytí MVP.** Projdi MVP checklist ze zadání položku po položce a ukaž, který úkol ji plní. Nepokrytá položka je nález, ne detail.
3. **Nic navíc.** Obráceně: je v plánu úkol, který v MVP není? Buď patří do další fáze, nebo se zapomnělo aktualizovat zadání. Zeptej se, neřeš to sám.
4. **Konzistence názvů.** Funkce, typy a parametry použité v pozdějších úkolech musí sedět s tím, co definují dřívější. `clearLayers()` v úkolu 3 a `clearFullLayers()` v úkolu 7 je chyba.
5. **Zadání se nezměnilo pod rukama.** Sáhl-li někdo během psaní plánu do `prd.md` nebo `design.md`, ohlas to.

Nálezy oprav rovnou. Sporné předlož uživateli po jednom přes `AskUserQuestion`.

**Commitni**, má-li projekt zapnutý autocommit.

------

## Fáze 4 – Předání

**Nepokračuj do realizace sám.** Plán se schvaluje, než se podle něj začne psát kód – to je poslední levné místo, kde se dá otočit.

> Plán je hotový a commitnutý v `docs/plan.md` – <N> úkolů. Přečti si ho prosím; až ho odsouhlasíš, pustíme realizaci přes `/implement`.

Nabídni před tím ještě `/oponent docs/plan.md` s úhly *technická proveditelnost* a *hraniční případy*, je-li plán rozsáhlý.

```
## Plán hotový

**Soubor:** docs/plan.md – <N> úkolů, <M> kroků
**Spec:** <design.md / prd.md>
**Rozsah:** <které položky MVP>

**Nepokryto vědomě**
- [co zůstalo na další fázi, nebo „nic"]

**Další krok:** /implement
```

Zakonči jednou z těchto vět:

- `Plán je hotový, můžeš ho projít a pak spustit /implement.`
- `Plán hotový není – brání tomu: <konkrétní seznam>.`
