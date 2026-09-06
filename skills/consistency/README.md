# /consistency – audit proti bordelu v projektu

> **Součást životního cyklu projektu.** Tenhle skill patří do ucelené sady skillů, které vedou práci od založení projektu až po nasazení. Každý má svůj krok a žádný nedělá práci toho vedle:
>
> [`/project`](../project/README.md) → [`/discovery`](../discovery/README.md) → [`/specify`](../specify/README.md) → [`/oponent`](../oponent/README.md) → [`/breakdown`](../breakdown/README.md) → [`/implement`](../implement/README.md) → [`/review`](../review/README.md) → **`/consistency`** → [`/cleanup`](../cleanup/README.md) → [`/attack`](../attack/README.md) → [`/release`](../release/README.md)
>
> Projít se nemusí celý – u drobné změny odpadá zadání i plán, u projektu bez kódu nasazení.

Projde projekt a najde všechno, co si v něm navzájem odporuje, opakuje se, je špatně zatříděné nebo zbylo po něčem, co se dávno smazalo. Neptá se „je ten kód správně?", ale **„sedí si projekt sám se sebou?"** – což je jiná otázka a nikdo jiný si ji neklade. Jednoznačné opravy udělá rovnou a jen je vypíše; o sporných se s vámi baví jednu po druhé.

## Co umí

1. **`/consistency`**, případně **`/consistency branch`** (výchozí) – projde soubory dotčené prací na aktuální větvi **a soubory, které na ně odkazují**. Ten druhý půlkruh je podstatný: nekonzistence skoro nikdy nežije v jednom souboru, ale mezi změněným a tím, co o něm mluví.
2. **`/consistency full`** – projde celý projekt bez ohledu na to, co se měnilo. Vyplatí se jednou za čas a před nasazením, ne po každé funkci. U velkého projektu se předem zeptá, jestli opravdu.
3. **Hledá v pěti rovinách** – od kritických věcí, které můžou rozbít funkčnost (rozjeté typy, konfigurace s různými hodnotami, chybějící proměnné prostředí, rozhraní deklarované jinak, než se používá), přes technický dluh (duplicitní logika, různé postupy k témuž problému, mrtvý kód, dokumentace popisující něco, co neexistuje) až po kosmetiku (nejednotné pojmenování, jedna entita pod třemi jmény v různých vrstvách).
4. **Zvlášť kontroluje skupiny souborů, které mají mít stejnou stavbu** – adresáře, kde každý soubor reprezentuje jednu instanci téhož konceptu. Chybějící sekce v jednom z nich se jinak nenajde.
5. **Hlídá i to, co stárne** – poznámky „doplnit později" starší než půl roku, komentáře s termínem v minulosti, přepínače funkcí, které mají všude stejnou hodnotu, nedokončené migrace.
6. **Seskupuje nálezy podle příčiny.** Jedno přejmenování, které zasáhlo padesát souborů, je jedna položka, ne padesát.
7. **Pamatuje si, co jste rozhodli neopravovat** – a příště se na to už neptá, dokud se ten kód nezmění.

## Proč zrovna tenhle

- **Umlčení má datum spotřeby.** Rozhodnutí „tohle neopravovat" se zapíše i se stavem repozitáře; jakmile se dotčený kód změní, nález se předloží znovu i s původním odůvodněním. Bez toho by z výjimek postupně vznikl seznam, kterým se dá umlčet cokoliv.
- **Neptá se na každou drobnost.** Bezriziková oprava se udělá rovnou a jen se vypíše; ptá se jen na to, kde se dá rozhodnout jinak.
- **Nesmaže kód jen proto, že vypadá mrtvý.** Může se volat dynamicky, z konfigurace nebo z jiného repozitáře – proto je to vždycky sporné.
- **U hromadných nálezů neodklikáváte padesát otázek.** Ukáže vzorec, počet a tři příklady a nabídne to udělat najednou.
- **Po každé své opravě si ověří, že nic nerozbil**, a pouští k tomu jen ty příkazy, které projekt sám deklaruje. Co spustit nemohl, vypíše jako nezkontrolované.
- **Neopakuje práci, která už proběhla.** Testy a linter běžely o krok dřív, takže se před auditem nespouštějí znovu – jen po vlastních opravách.
- **Řekne, kdy se vyplatí pustit ho znovu.** Po rozsáhlé opravě má čerstvě napsaný text vad nejvíc; po drobných opravách by další běh hledal hlavně sám sebe.

## Jak se to používá

```
/consistency          # co se dotklo větve a co na to odkazuje (totéž co /consistency branch)
/consistency full     # celý projekt
```

## Ukázka výstupu

```
## Výsledky konzistenčního auditu

Nalezeno 23 problémů celkem:
- 🔴 Kritické: 2    🟡 Střední: 14    🔵 Kosmetické: 7

Mechanických (jednoznačná bezriziková oprava): 9 – ty opravím rovnou a jen je vypíšu.
Sporných: 14 – ty projdeme spolu od nejzávažnějších.
```

## Co nedělá

- **Nehledá chyby v kódu.** Na korektnost je `/review`.
- **Nekontroluje soulad se standardy.** Projekt může být dokonale konzistentní a přitom konzistentně porušovat předpis – to je otázka pro `/review`.
- **Neposuzuje, jestli je návrh dobrý.** Na to je `/oponent`.
- **Nemění chování.** Nálezy, které by ho změnily, jdou vždycky přes vás.

## Jak si ho nainstalovat

Nechte to na Claudovi. Otevřete si Claude Code a napište mu:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/consistency a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.

Skill sdílí část postupu se `/review` (určení rozsahu, tvar interaktivního průchodu), takže si **nechte nainstalovat rovnou oba**. Odkazuje se i na moje soukromé standardy pro strukturu projektu – ty odkazy ať Claude nahradí vašimi, nebo je smaže.


**Nebo celou sadu naráz.** Chcete-li místo jednoho skillu rovnou celý životní cyklus, napište mu tohle:

> Jdi na https://github.com/jantichy/claude/tree/main/skills a nainstaluj mi do `~/.claude/skills/` celý životní cyklus: project, discovery, specify, oponent, breakdown, implement, review, consistency, cleanup, attack a release. U každého si přečti README a řekni mi, co k nim potřebuju doplnit.

---

### Požadavky a omezení

Git kvůli určení rozsahu. Hledání mrtvého kódu a nepoužitých závislostí se opírá o nástroje `knip` nebo `depcheck`, má-li je projekt nainstalované – nemá-li je, ta vrstva odpadne a skill to řekne. Ověření po opravách potřebuje, aby měl projekt v instrukcích zapsané, čím se u něj pouštějí testy, typová kontrola a linter.
