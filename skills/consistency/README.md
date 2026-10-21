# /consistency – audit proti bordelu v projektu

> **Součást životního cyklu projektu.** Tenhle skill patří do ucelené sady skillů, které vedou práci od založení projektu až po vyhodnocení provozu. Jedny tvoří, druhé se starají o to, co už vzniklo – a žádný nedělá práci toho vedle:
>
> **Osa** [`/project`](../project/README.md) → [`/discovery`](../discovery/README.md) → [`/specify`](../specify/README.md) → [`/architect`](../architect/README.md) → [`/breakdown`](../breakdown/README.md) → [`/implement`](../implement/README.md) → [`/release`](../release/README.md) → [`/evaluate`](../evaluate/README.md)
>
> **Kontroly** [`/oponent`](../oponent/README.md) · [`/consolidate`](../consolidate/README.md) · [`/review`](../review/README.md) · **`/consistency`** · [`/attack`](../attack/README.md)
>
> Projít se nemusí celý – u drobné změny odpadá zadání i plán, u projektu bez kódu nasazení i vyhodnocení provozu.

Projde projekt a najde všechno, co si v něm navzájem odporuje, opakuje se, je špatně zatříděné nebo zbylo po něčem, co se dávno smazalo. Neptá se „je ten kód správně?“, ale **„sedí si projekt sám se sebou?“** – což je jiná otázka a nikdo jiný si ji neklade. Jednoznačné opravy udělá rovnou a jen je vypíše; o sporných se s vámi baví jednu po druhé.

## Co umí

1. **`/consistency`**, případně **`/consistency branch`** (výchozí) – projde soubory dotčené prací na aktuální větvi **a soubory, které na ně odkazují**. Ten druhý půlkruh je podstatný: nekonzistence skoro nikdy nežije v jednom souboru, ale mezi změněným a tím, co o něm mluví.
2. **`/consistency full`** – projde celý projekt bez ohledu na to, co se měnilo. Vyplatí se jednou za čas a před nasazením, ne po každé funkci. U velkého projektu se předem zeptá, jestli opravdu.
3. **Hledá v pěti rovinách** – od kritických věcí, které můžou rozbít funkčnost (rozjeté typy, konfigurace s různými hodnotami, chybějící proměnné prostředí, rozhraní deklarované jinak, než se používá), přes technický dluh (duplicitní logika, různé postupy k témuž problému, mrtvý kód, dokumentace popisující něco, co neexistuje) až po nálezy nízké závažnosti (nejednotné pojmenování, jedna entita pod třemi jmény v různých vrstvách).
4. **Zvlášť kontroluje skupiny souborů, které mají mít stejnou stavbu** – adresáře, kde každý soubor reprezentuje jednu instanci téhož konceptu. Chybějící sekce v jednom z nich se jinak nenajde.
5. **Hlídá i to, co stárne** – poznámky „doplnit později“ starší než půl roku, komentáře s termínem v minulosti, přepínače funkcí, které mají všude stejnou hodnotu, nedokončené migrace.
6. **Seskupuje nálezy podle příčiny.** Jedno přejmenování, které zasáhlo padesát souborů, je jedna položka, ne padesát.
7. **Mrtvé odkazy a kotvy v textech hledá nástrojem, ne čtením** – dostane je tedy úplné a zdarma, kdežto při čtení se odkaz na přejmenovanou sekci přehlédne snadno, protože vypadá správně.
8. **Pamatuje si, co jste rozhodli neopravovat** – a příště se na to už neptá, dokud se ten kód nezmění.
9. **Nedojde-li seznam do konce, nabídne přerušení.** Roste-li konverzace do velikosti, ve které už se pracuje pomalu a nepřesně, řekne to a zbývající položky i s tím, co je u nich potřeba rozhodnout, uloží do seznamu úkolů – další session pak pokračuje přesně tam, kde jste skončili, a s čistou hlavou.

## Proč zrovna tenhle

- **Umlčení má datum spotřeby.** Rozhodnutí „tohle neopravovat“ se zapíše i se stavem repozitáře; jakmile se dotčený kód změní, nález se předloží znovu i s původním odůvodněním. Bez toho by z výjimek postupně vznikl seznam, kterým se dá umlčet cokoliv.
- **Neptá se na každou drobnost.** Bezriziková oprava se udělá rovnou a jen se vypíše; ptá se jen na to, kde se dá rozhodnout jinak.
- **Nesmaže kód jen proto, že vypadá mrtvý.** Může se volat dynamicky, z konfigurace nebo z jiného repozitáře – proto je to vždycky sporné.
- **U hromadných nálezů neodklikáváte padesát otázek.** Ukáže vzorec, počet a tři příklady a nabídne to udělat najednou.
- **Po každé své opravě si ověří, že nic nerozbil**, a pouští k tomu jen ty příkazy, které projekt sám deklaruje. Co spustit nemohl, vypíše jako nezkontrolované.
- **Neopakuje práci, která už proběhla.** Kde testy a linter pouští po každé odpovědi průběžná kontrola, před auditem je znovu nespouští – jen po vlastních opravách.
- **Co se dá změřit, neodhaduje.** Mechanické vady hledá nástroj a jejich výčet je úplný; posuzování zbývá jen na to, co změřit nejde. Ušetřené místo padne na vlastní úsudek.
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
- 🔴 Kritické: 2    🟡 Střední: 14    🔵 Nízké: 7

Mechanických (jednoznačná bezriziková oprava): 9 – ty opravím rovnou a jen je vypíšu.
Sporných: 14 – ty projdeme spolu od nejzávažnějších.
```

## Co nedělá

- **Nehledá chyby v kódu.** Na korektnost je `/review`.
- **Nekontroluje soulad s doménovými znalostmi.** Projekt může být dokonale konzistentní a přitom konzistentně porušovat předpis – to je otázka pro `/review`.
- **Neposuzuje, jestli je návrh dobrý.** Na to je `/oponent`.
- **Nemění chování.** Nálezy, které by ho změnily, jdou vždycky přes vás.

## Jak si ho nainstalovat

Je to snadné, zadejte do svého Claude Code tenhle prompt:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/consistency a nainstaluj mi ten skill k sobě do `~/.claude/skills/` – celý adresář i s podadresáři. Stáhni k němu z téhož repozitáře na odpovídající místo pod `~/.claude/` i sdílené soubory ze `skills/` a `standards/`, na které jeho soubory odkazují, a definice typů subagentů, které pouští, z `agents/` do `~/.claude/agents/`. Co už u sebe mám, nepřepisuj a ukaž mi rozdíl. Odkazuje-li na jiný skill, zeptej se mě, jestli ho chci taky. Odkazy na soubory, které v repozitáři nejsou, mi vypiš a u každého se zeptej, jestli ho napojit na můj vlastní soubor, nebo odkaz smazat. Nainstaluj mi k tomu i skill `/review`, sdílí s ním část postupu. Nakonec mi řekni, co musím doplnit sám.

**Nebo celou sadu naráz.** Chcete-li místo jednoho skillu rovnou celý životní cyklus, zadejte do svého Claude Code tenhle prompt:

> Jdi na https://github.com/jantichy/claude/tree/main/skills a nainstaluj mi do `~/.claude/skills/` celý životní cyklus: project, discovery, specify, architect, breakdown, implement, release, evaluate, oponent, consolidate, review, consistency a attack, a k nim skilly, kterými se session uzavírá: end, merge a break. Každý z nich nainstaluj přesně podle promptu v sekci „Jak si ho nainstalovat“ v jeho README; na skilly z téhle sady se mě při tom neptej, beru je všechny.

---

### Požadavky a omezení

Git kvůli určení rozsahu. Hledání mrtvého kódu a nepoužitých závislostí se opírá o nástroje `knip` nebo `depcheck`, má-li je projekt nainstalované – nemá-li je, ta vrstva odpadne a skill to řekne. Ověření po opravách potřebuje, aby měl projekt v instrukcích zapsané, čím se u něj pouštějí testy, typová kontrola a linter.
