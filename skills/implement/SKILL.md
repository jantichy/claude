---
name: implement
description: Skill se použije, když uživatel zadá "/implement", nebo chce podle hotového implementačního plánu v docs/plan.md odpracovat úkoly jeden po druhém – včetně testů, ověření a commitů. Umí navázat na rozpracovaný plán.
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, Skill]
---

# Implement

## Co skill dělá

Vezme **`docs/plan.md`** a odpracuje ho úkol po úkolu – u každého test, implementace, ověření a commit. V ose *Životního cyklu práce* (`~/.claude/RULES.md`) navazuje na `/breakdown` a předává na uzavírání.

## Co skill nedělá

- **Nemění plán.** Ukáže-li se, že je plán špatně, zastaví se – viz *Když plán neplatí*.
- **Nedodělává, co v plánu není.** Nápad nad rámec plánu jde do `docs/todo.md`, ne do kódu.
- **Neuzavírá feature.** Review, audit konzistence a úklid jsou samostatné kroky po tomhle – viz *Životní cyklus práce* v `~/.claude/RULES.md`, druhá půlka osy.

## Jak je to postavené uvnitř

Skill dnes řídí **`superpowers:subagent-driven-development`** nebo **`superpowers:executing-plans`**. To je **implementační detail, ne rozhraní** – vnitřek se může kdykoliv změnit, aniž se změní, jak se skill volá.

Co je závazné: vstupem je `docs/plan.md`, pracuje se úkol po úkolu, každý úkol končí ověřeným a commitnutým stavem, a po posledním úkolu se feature neuzavírá automaticky.

------

## Fáze 0 – Pre-flight

1. **Kořen projektu.** Ve worktree layoutu (`~/Dev/context/worktree/worktree.md`) pracuj v adresáři větve, ne v kořeni kontejneru.
2. **Přečti projektový `CLAUDE.md`** – `## Příkazy` (*Kontrakt příkazů*), `### Autocommit`, paměťovou politiku, importované doménové standardy, výjimky.
   **Chybí-li `## Příkazy` a projekt má kód, zastav se a doplň je** – bez nich nemá zelená linka co spouštět a realizace by běžela bez brány. Zjisti je z `package.json`, `composer.json`, `Makefile` nebo obdoby, ukaž návrh a nech ho potvrdit.
   **Ověř, že je linka zelená ještě před startem.** Dědíš-li červený stav z dřívějška, ohlas to a zeptej se – jinak nepůjde poznat, co jsi rozbil ty.
3. **Najdi plán.**

   | Stav | Co dělat |
   |---|---|
   | `docs/plan.md` neexistuje | **Zastav se.** Nabídni `/breakdown`, a pokud chybí i zadání, `/specify`. |
   | Existuje, nic není odškrtnuté | Normální běh od prvního úkolu. |
   | Existuje, část odškrtnutá | **Naváž na prvním neodškrtnutém úkolu.** Nejdřív ale ověř, že odškrtnuté opravdu hotové jsou – viz bod 5. |
   | Vše odškrtnuté | Řekni to a nabídni uzavírání podle *Životního cyklu práce*. Nehledej si práci navíc. |

4. **Zkontroluj git.** Rozpracované změny v pracovním stromu **před** startem jsou riziko: smíchají se s prací podle plánu a přestane být poznat, co je čí. Vypiš je a zeptej se, jestli je commitnout, odložit, nebo pokračovat i tak.
5. **Ověř skutečný stav proti plánu.** U navazování nevěř zaškrtávátkům – podívej se, jestli soubory a testy z odškrtnutých úkolů opravdu existují a procházejí. Plán mohl zůstat odškrtnutý po přerušené session, kde se práce nedokončila. Nesedí-li to, ohlas to a zeptej se, než začneš.
6. **Izolace větve.** Má-li projekt worktree layout, pracuje se v už existující větvi – **nezakládej další worktree**. Nemá-li ho a jde o větší práci, nabídni izolaci; pokud ji uživatel chce, použij `superpowers:using-git-worktrees`.

Zjištěné shrň do tří až pěti řádků.

------

## Fáze 1 – Volba režimu

Zeptej se **přes `AskUserQuestion`** – jedna otázka, dvě volby, v lidské řeči:

- **Po úkolech se čtením mezi nimi** *(doporuč tuhle)* – na každý úkol jde čerstvý pracovník, který nevidí předchozí konverzaci, a mezi úkoly se výsledek zkontroluje. Chytá to, když se plán někde rozejde se skutečností, a nehromadí se kontext. Vhodné na cokoliv delšího než pár úkolů.
- **V jednom kuse s kontrolními body** – rychlejší, méně režie, ale chyba se odhalí až o několik úkolů dál. Vhodné na krátký plán a na práci, kterou dobře znáš.

Podle volby vyvolej `superpowers:subagent-driven-development`, respektive `superpowers:executing-plans`, a předej mu cestu k plánu, kořen projektu a doménové standardy z `CLAUDE.md`.

------

## Fáze 2 – Průběh

Během realizace hlídej šest věcí, které se z plánu samy neuhlídají:

**Zelená linka po každém úkolu.** Úkol není hotový, když je napsaný kód – je hotový, když projde `typecheck`, `lint`, `test` a případně `build` podle *Kontraktu příkazů* v projektovém `CLAUDE.md`. Teprve pak commit a další úkol. Podrobně `~/Dev/context/coding/coding.md`, *Ověřování a brány kvality*.

**Netvrď, že to prošlo, bez výstupu.** Do shrnutí patří příkaz a jeho návratový kód, ne věta „testy procházejí“. Nemá-li projekt příkaz v kontraktu, řekni, co se tím nezkontrolovalo.

**Testy jsou jen ke čtení.** Plán je napsal a uživatel je schválil dřív, než vznikl kód – v tom je jejich cena. Nesedí-li test s implementací, **první hypotéza je, že je špatně kód**. Ukáže-li se, že je špatně test, je jeho změna **samostatný zásah, který ohlásíš a necháš schválit**, ne tichá součást úkolu. Přidání `skip`, zeslabení `assert` nebo smazání testu je vždycky chyba, i když je pak zeleno.

**Commity.** Plán má commit jako poslední krok každého úkolu. Má-li projekt zapnutý autocommit, **necommituj dvakrát** – řiď se plánem a autocommit nech na změny mimo úkoly. Commit message piš česky a věcně: co se změnilo, ne které soubory.

**Doménové standardy.** Kód se má psát podle nich rovnou, ne se k nim vracet až v `/review`. Neznamená to duplikovat kontrolu – znamená to je respektovat.

**Nápady nad rámec plánu.** Cokoliv, co tě při psaní napadne a v plánu to není, jde do `docs/todo.md` s celou úvahou. Do kódu ne. *Nerozhoduj potichu nad rámec zadání.*

**Průběžné zápisy.** Padne-li během realizace rozhodnutí (a padá), jde do `docs/decisions.md` hned, i se zavrženými variantami. Vybroušený princip do `docs/rules.md`. Nečekej na `/cleanup`.

**Po každém větším celku levné review.** Po skupině souvisejících úkolů (ne po každém) spusť `/code-review` na nízké úrovni. Běží v čerstvém kontextu, takže vidí, co ty už nevidíš, a chyba nalezená teď stojí minuty. Plný panel je až `/review` při uzavírání.

------

## Když plán neplatí

Při realizaci se pravidelně ukáže, že plán někde nesedí. **Neopravuj to potichu v kódu** – tím se plán rozejde se skutečností a přestane být k čemu.

Podle toho, jak hluboko problém sahá:

| Kam sahá | Co udělat |
|---|---|
| Jen úkol – špatný název souboru, chybějící krok | Oprav plán i kód, řekni to v jedné větě a pokračuj. |
| Návrh – takhle postavené to nefunguje | **Zastav se.** Vrať se do `docs/architecture.md`, uprav ho a nech přepsat dotčené nehotové úkoly. |
| Zadání – ukázalo se, že chceme něco jiného | **Zastav se a zeptej se.** Změna produktového záměru není tvoje rozhodnutí; teče shora dolů, viz `structure.md`. |

**Nikdy neškrtej úkol jako hotový, aby se dalo pokračovat.** Zablokovaný úkol nech neodškrtnutý, zapiš proč, a zeptej se.

------

## Fáze 3 – Závěr

Po posledním úkolu **feature neuzavírej**. Vypiš stav a předej to na řetěz uzavírání:

```
## Realizace hotová

**Plán:** docs/plan.md – <hotovo>/<celkem> úkolů
**Režim:** <po úkolech / v jednom kuse>
**Commity:** <N>

**Odchylky od plánu**
- [co se muselo změnit a proč, nebo „žádné"]

**Nedokončeno**
- [zablokované úkoly i s důvodem, nebo „nic"]

**Zapsáno mimo kód**
- docs/decisions.md: N
- docs/done.md: N   docs/todo.md: N   docs/rules.md: N

**Zelená linka:** <výstup posledního běhu – příkaz a návratový kód>

**Další krok:** `/review`, pak `/consistency` a `/cleanup` (RULES.md, *Životní cyklus práce*)
```

Zakonči jednou z těchto vět:

- `Plán je odpracovaný a linka je zelená, můžeš jít na /review.`
- `Odpracovaný není – zbývá: <konkrétní seznam>.`
