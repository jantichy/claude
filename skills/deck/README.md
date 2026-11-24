# /deck – prezentace z Markdownu ve vlastní šabloně

Prezentace k přednášce nebo školení se obvykle klikají ručně a s každou další akcí se rozcházejí: tady se opravil údaj, jinde ne, a za rok nikdo neví, která verze platí. Tenhle skill drží prezentaci jako obyčejný textový soubor – nadpisy, odrážky, karty, tabulky a poznámky řečníka – a PowerPoint z něj pokaždé sestaví znovu ve vaší šabloně. Obsah přitom staví z toho, co o tématu máte sepsané, a sám si zkontroluje, jak slajdy vypadají. Hodí se každému, kdo přednáší opakovaně a má vlastní vizuální styl.

## Co umí

- **Napíše prezentaci** z popisu přednášky (pro koho, jak dlouhá, které části), z toho, jak téma učíte, a ze znalostí, které k němu máte sepsané.
- **Upraví existující prezentaci** – přeskládá slajdy, zkrátí přetékající text, doplní poznámky řečníka – vždycky ve zdrojovém souboru, ne v PowerPointu.
- **Sestaví PowerPoint ve vaší šabloně.** Typy slajdů – titulní, mezislajd s QR kódem, odrážky, dvě karty, mřížka, velká čísla, tabulka, obrázek, závěr – se skládají ze vzorových slajdů šablony, takže vypadají přesně jako ona.
- **Zvládne i schéma na míru.** Kresbu, kterou z typů slajdů poskládat nejde, si přednáška nese u sebe jako malý skript.
- **Vykreslí náhledy a zkontroluje je:** přetékající text, kontrast, a jestli slajd řekne, o čem je řeč, i tomu, kdo chvíli neposlouchal.

## Proč zrovna tenhle

- **Jeden zdroj pravdy.** Úprava jde do textu a PowerPoint je jen výstup – nic se nerozejde a staré verze jdou porovnat jako text.
- **Vzhled se nekreslí, ale klonuje.** Generátor nebere obecné rozvržení, ale vaše vzorové slajdy, takže písma, okraje a barvy sedí do bodu.
- **Nevymýšlí si.** Údaj, který v podkladech není, nechá v poznámkách k dohledání, místo aby ho na slajd napsal jako fakt.
- **Kontroluje to, co vidí publikum.** Neohlásí hotovo podle toho, že se soubor uložil, ale podle náhledů.

## Jak se to používá

```
/deck Školení/Claude Code
```

Najde přednášku, napíše nebo upraví její prezentaci, sestaví PowerPoint vedle ní, projde náhledy a opraví, co na nich nesedí. Na konci řekne, kde prezentace leží a co zbývá dohledat.

## Ukázka výstupu

Zdroj prezentace:

```markdown
## cards
# Dva přístupy
### Server
- data jdou přes vlastní doménu
- `sGTM` před GA4
### Prohlížeč
- data jdou rovnou do GA4
> DOHLEDAT: podíl blokovaných požadavků
```

Z toho vznikne slajd se světlou a tmavou kartou vedle sebe, kódem v neproporcionálním písmu a poznámkou řečníka, že jeden údaj ještě chybí.

## Co nedělá

- **Nepíše za vás látku.** Co o tématu nemáte sepsané, musí nejdřív vzniknout jinde.
- **Nestaví v Google Slides** a do hotového PowerPointu nesahá – každá úprava jde přes textový zdroj.
- **Nepíše články ani pozvánky** vaším hlasem; na to je [`/compose`](../compose/README.md).
- **Nedělá korekturu** hotových textů; na to je [`/proofread`](../proofread/README.md).

## Jak si ho nainstalovat

Je to snadné, zadejte do svého Claude Code tenhle prompt:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/deck a nainstaluj mi ten skill k sobě do `~/.claude/skills/` – celý adresář i s podadresáři. Stáhni k němu z téhož repozitáře na odpovídající místo pod `~/.claude/` i sdílené soubory ze `skills/` a `standards/`, na které jeho soubory odkazují, a definice typů subagentů, které pouští, z `agents/` do `~/.claude/agents/`. Co už u sebe mám, nepřepisuj a ukaž mi rozdíl. Odkazuje-li na jiný skill, zeptej se mě, jestli ho chci taky. Odkazy na soubory, které v repozitáři nejsou, mi vypiš a u každého se zeptej, jestli ho napojit na můj vlastní soubor, nebo odkaz smazat. Doinstaluj mi i to, co skill potřebuje ke svému běhu. Šablona prezentace v repozitáři není – zeptej se mě na cestu k mé vlastní šabloně v PowerPointu, nastav ji v generátoru a porovnej vzorové slajdy, které generátor čte, s tím, co v mé šabloně je. Nakonec mi řekni, co musím doplnit sám.

**Šablonu musíte mít vlastní.** Skill čte vzorové slajdy autorovy šablony, která je soukromá; s vaší bude fungovat, až generátor ukáže na ty její slajdy, které jednotlivým typům odpovídají. Stejně tak předpokládá složku s přednáškami a sepsané znalosti, ze kterých obsah staví.

---

### Požadavky a omezení

macOS; vyvinuto a testováno tam. Sestavení potřebuje [uv](https://docs.astral.sh/uv/) (knihovny si stáhne samo), náhledy LibreOffice, Poppler a ImageMagick. Písma šablony si náhled bere z nainstalovaných a chybějící stáhne z Google Fonts. Kontrola náhledů je úsudek modelu nad obrázky, ne měření – drobné přetečení o pár bodů může minout.
