# Standardní struktura projektu

Konvence platná pro **každý projekt, kde dává smysl** – tedy všude, kde se něco průběžně rozhoduje a vyvíjí. Jednorázový scratch adresář nebo cizí repozitář, do kterého jen nahlížíš, ji nepotřebuje.

Zakládá a udržuje ji skill `/project`. Tenhle soubor konvenci **definuje**; projektový `CLAUDE.md` jen deklaruje, že ji projekt drží, a popisuje odchylky.

```
<projekt>/
├── CLAUDE.md          instrukce pro Clauda v tomhle projektu
├── README.md          co projekt je, pro člověka
└── docs/
    ├── todo.md        co je odložené na později
    ├── decisions.md   co jsme rozhodli a proč
    └── rules.md       principy, ve kterých se projekt pohybuje
```

------

## Co patří do kterého souboru

### `README.md`

Co projekt je, pro člověka, který sem přijde poprvé. Průběžně aktualizuj podle vývoje – má vždy odpovídat skutečnému stavu.

### `docs/todo.md`

Všechno, co padne mimo aktuální osu: nápad do další fáze, otevřená otázka, věc k pozdějšímu rozhodnutí. **S celou úvahou a zdůvodněním**, ne jako holá odrážka – účel je mít téma připravené, ne se k němu zavázat.

Nedokončené položky nahoře, hotové **přesouvej dolů do sekce `## Hotovo`** – nikdy nemaž.

### `docs/decisions.md`

**Konkrétní rozhodnutí** tohoto projektu a cesta k nim: jaký problém to řešilo, jaké varianty byly ve hře, proč vyhrála tahle a proč padly ostatní. Patří sem i místa, kde jsme názor v průběhu změnili – ta se nepřepisují, přibude k nim revize s odůvodněním.

Zapisuj hned, jak rozhodnutí padne. Z odstupu se zdůvodnění rekonstruuje špatně nebo vůbec.

### `docs/rules.md`

**Obecné principy tohoto projektu** – věty, které rozhodují, ne popis toho, co systém dělá. Vznikají z konkrétních rozhodnutí, ale zapisují se obecně, aby platily i tam, kam se ještě nedošlo.

Rozdíl proti `decisions.md`: tam je konkrétní rozhodnutí (občas i výjimka z principu), tady rámec, proti kterému se rozhoduje. Každou další otázku validuj proti principům odsud, ne od nuly.

**Hranice – co sem nepatří:**

- Pravidla platná napříč všemi projekty → `~/.claude/RULES.md`
- Doménové standardy a checklisty (kód, web, administrace) → `~/Dev/claude/CODING.md`, `WEB.md`, `ADMIN.md`
- Sem patří **jen to, co je specifické pro tenhle projekt.** Duplikovat sem obecné pravidlo je chyba.

------

## Průběžná aktualizace je povinná

Tyhle soubory jsou **živé**, ne zakládací formalita. Doplňuj je **sám, průběžně, bez vyžádání** – ve chvíli, kdy rozhodnutí padne, princip se vybrousí nebo se něco odloží. Nečekej na `/cleanup` ani na konec session.

Uživatel na to nesmí muset upozorňovat. Když si nejsi jistý, do kterého ze tří souborů zápis patří, rozhodni podle otázky, na kterou odpovídá:

| Otázka | Soubor |
|---|---|
| Co ještě není hotové? | `todo.md` |
| Proč jsme to udělali takhle? | `decisions.md` |
| Jak se v tomhle projektu rozhoduje? | `rules.md` |

Když se ukáže, že zápis patří jinam, přesuň ho – „Živá struktura" platí i tady.

## Prázdný soubor je v pořádku

Nový projekt má všechny tři soubory založené a prázdné, jen s nadpisem. Nevymýšlej do nich obsah dopředu; naplní se prací.
