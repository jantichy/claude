# /diagram – mapa datového modelu, na kterou se dá kliknout

Z dokumentace navrženého datového modelu nakreslí interaktivní stránku: ER diagram všech tabulek, stavy a přechody mezi nimi a to, co se se stavy jen kombinuje. Hodí se ve chvíli, kdy model narostl na desítky tabulek a stovky sloupců a z textu už ho v hlavě neudržíte. Stránka žije jako soukromý artefakt na claude.ai a při dalším zavolání se překreslí na stejném odkazu, takže záložka zůstává platná.

## Co umí

- **Celé schéma** – po kliknutí na tabulku popis lidskými slovy, k čemu je, vazby oběma směry, všechny sloupce, constrainty, invarianty a indexy.
- **Jádro modelu** – malý diagram hlavních entit, ze kterého je vidět, kde se nabídka potkává s prodejem nebo co drží co.
- **Stavový prostor** – po kliknutí na stav ukáže, kam a jakou funkcí se z něj dá odejít, kdo ten přechod spouští a co stav nemění.
- **Aktualizace** – najde svou dřívější stránku, zjistí, co se v modelu od té doby změnilo, a promítne to včetně přejmenování.
- **Jinou větev** – ve worktree layoutu se zeptá, ze které rozdělané větve kreslit.

## Proč zrovna tenhle

- **Nic si nedomýšlí.** Přechod, který dokumentace nejmenuje, se nenakreslí – a řekne to.
- **Data nepřepisuje ručně.** Vytáhne je skriptem a čísla ověří proti zdroji, než je ukáže.
- **Nesahá do projektu.** Žádný diagram v repozitáři, který by se tiše rozešel s textem.
- **Je vidět, odkud to je** – větev, commit a datum stojí na stránce.
- **Na konci řekne, co zkontrolovat** – co je odvozené, co vynechal a kde narazil na rozpor v dokumentaci.

## Jak se to používá

```
/diagram
```

V projektu s popsaným modelem stačí zavolat. Poprvé vznikne nová stránka, příště se aktualizuje ta stávající.

## Ukázka výstupu

```
Mapa modelu rezervací · větev main · commit 94027a3

Celé schéma: 29 tabulek, 60 cizích klíčů
  [part] → Partie – část objednávky s vlastním dokladem a platbou…
           Sloupce (31) · Constrainty (1) · Invarianty (16) · Indexy (3)

Stavy partie: 13 stavů, 44 přechodů
  [NEW] → issueProforma → PROFORMA_UNPAID
          payFree → FREE_PAID
          …
```

## Co nedělá

- **Nečte schéma z kódu** – zatím jen z dokumentace modelu.
- **Neopravuje dokumentaci**, rozpory jen ohlásí.
- **Nekreslí grafy z dat** – na to je jiný skill.

## Jak si ho nainstalovat

Nechte to na Claudovi. Otevřete si Claude Code a napište mu:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/diagram a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.

Skill si načítá **moji soukromou českou typografii**, která v tomhle repozitáři není; bez ní funguje, jen si ji nepohlídá. Stránku publikuje jako artefakt na claude.ai, takže potřebuje Claude Code s dostupnými artefakty.

---

### Požadavky a omezení

Claude Code s nástrojem pro artefakty, Git a Node pro kontrolu skriptů stránky. Model musí být v projektu popsaný v dokumentaci (bloky schématu, katalog přechodů) – z migrací ani ORM zatím nekreslí. Stránka je soukromá, dokud ji nesdílíte.
