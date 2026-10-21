# /merge – dokončení větve, ne jeden příkaz

> **Součást životního cyklu projektu.** Tenhle skill patří do ucelené sady skillů, které vedou práci od založení projektu až po vyhodnocení provozu. Jedny tvoří, druhé se starají o to, co už vzniklo – a žádný nedělá práci toho vedle:
>
> **Osa** [`/project`](../project/README.md) → [`/discovery`](../discovery/README.md) → [`/specify`](../specify/README.md) → [`/architect`](../architect/README.md) → [`/breakdown`](../breakdown/README.md) → [`/implement`](../implement/README.md) → [`/release`](../release/README.md) → [`/evaluate`](../evaluate/README.md)
>
> **Kontroly** [`/oponent`](../oponent/README.md) · [`/consolidate`](../consolidate/README.md) · [`/review`](../review/README.md) · [`/consistency`](../consistency/README.md) · [`/attack`](../attack/README.md) · [`/end`](../end/README.md) · **`/merge`** – stojí v mezerách mezi kroky osy, některé z nich ve víc mezerách
>
> Projít se nemusí celý – u drobné změny odpadá zadání i plán, u projektu bez kódu nasazení i vyhodnocení provozu.

„Přimerguj to“ vypadá jako jeden příkaz. Ve skutečnosti je to postup, ve kterém se dá přijít o práci – a nejčastěji se to stane tak, že se dvě větve rozejdou obsahově, ne textově: jedna přejmenuje funkci, druhá ji nově volá, merge projde bez konfliktu a rozbitý stav vznikne poprvé až na hlavní větvi, kde na něm stojí všichni ostatní. Tenhle skill to dělá obráceně: spojený stav nechá vzniknout a ověřit **ve vaší větvi**, a do hlavní pustí až to, co prošlo.

## Co umí

1. **Nejdřív uklidí session** – pustí [`/end`](../end/README.md), aby do hlavní větve šlo i to, co se domluvilo, a pokračuje jen tehdy, když je zapsané všechno. Před `/merge` ho tedy psát nemusíte.
2. **Zastaví merge, který nemá proběhnout** – necommitnutá práce, rozdělaná hlavní větev, nebo projekt, který se z hlavní větve automaticky nasazuje (tam je merge samotné nasazení a patří jinam).
3. **Zjistí, jestli se hlavní větev mezitím posunula.** Pokud ne, merguje rovnou; stav už jednou prošel kontrolou.
4. **Přihraje hlavní větev do té vaší a ověří ji tam** – včetně konfliktů. Mechanické spojí sám, ptá se jen tam, kde obě strany rozhodly tutéž věc jinak – a co rozhodnete, rovnou zapíše.
5. **Pustí nad spojeným stavem kontroly projektu** – testy, lint, typecheck, podle toho, co projekt deklaruje. Nemá-li co pustit, řekne to nahlas místo aby mlčel.
6. **Zopakuje to, posunula-li se hlavní větev znovu** – a po třetím kole se zastaví a zeptá, místo aby donekonečna doháněl.
7. **Slučuje se shrnující zprávou**, která říká, co větev přinesla, ne jak se jmenovala. V historii hlavní větve je to jediný řádek za celou práci.
8. **Uklidí až po ověřeném mergi** – větev, její pracovní adresář i větev na serveru, a jen když merge opravdu prošel.

## Proč zrovna tenhle

- **Rozbitý stav nevznikne na hlavní větvi.** Spojení se zkouší a opravuje u vás, kde nikomu nepřekáží.
- **Textově čistý merge se nepovažuje za hotovou věc.** Zrovna ten je nejnebezpečnější, protože nic nekřičí.
- **Úklid nikdy neběží souběžně s mergem.** Selže-li merge a mazání se pustí vedle něj, zmizí nepřimergovaná větev lokálně i ze serveru – a `git branch -d` to nezastaví.
- **Zpráva merge commitu je čitelná i za rok.** Ne „Merge branch feat/payments“, ale věta o tom, co přibylo.
- **Merguje se jen na vyžádání.** Skill si nikdy neodsouhlasí sám, že je práce hotová.
- **Funguje i v obyčejném repozitáři.** Nepotřebuje žádné zvláštní uspořádání adresářů.

## Jak se to používá

Když je větev hotová, napíšete `/merge` (nebo prostě „přimerguj to“). Skill projde postup od kontroly překážek po úklid a průběžně hlásí, co prošlo. Chcete-li dokončit jinou větev, než na které stojíte, přidáte její jméno: `/merge feat/payments`.

## Ukázka výstupu

```
## Větev dokončená

- Větev: feat/payments → main
- Merge commit: 4f2a1c9 · Zaveď platby kartou přes platební bránu
- Natažení main do větve: proběhlo, 1 konflikt v docs/done.md (obě strany přidaly, ponecháno za sebou)

Ověřeno
- Kontrakt příkazů nad spojeným stavem: npm test → 0, npm run lint → 0

Úklid
- Smazán pracovní adresář větve, lokální větev i feat/payments na originu
```

## Co nedělá

- **Nerozhoduje, že je práce hotová.** To říkáte vy; bez pokynu se nespustí.
- **Nekontroluje kvalitu toho, co jste napsali.** Ověřuje spojení, ne obsah – na obsah jsou jiné skilly ze sady.
- **Nenasazuje.** U projektu, který se z hlavní větve nasazuje automaticky, merge odmítne a pošle vás na nasazovací krok.
- **Nezakládá větve.**

## Jak si ho nainstalovat

Je to snadné, zadejte do svého Claude Code tenhle prompt:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/merge a nainstaluj mi ten skill k sobě do `~/.claude/skills/` – celý adresář i s podadresáři. Stáhni k němu z téhož repozitáře na odpovídající místo pod `~/.claude/` i sdílené soubory ze `skills/` a `standards/`, na které jeho soubory odkazují, a definice typů subagentů, které pouští, z `agents/` do `~/.claude/agents/`. Co už u sebe mám, nepřepisuj a ukaž mi rozdíl. Odkazuje-li na jiný skill, zeptej se mě, jestli ho chci taky. Odkazy na soubory, které v repozitáři nejsou, mi vypiš a u každého se zeptej, jestli ho napojit na můj vlastní soubor, nebo odkaz smazat. Nakonec mi řekni, co musím doplnit sám.

Ověřování spojeného stavu se opírá o sekci `## Kontrakt příkazů` v projektových instrukcích; nemáte-li ji, skill to řekne a mergne bez ní.

**Nebo celou sadu naráz.** Chcete-li místo jednoho skillu rovnou celý životní cyklus, zadejte do svého Claude Code tenhle prompt:

> Jdi na https://github.com/jantichy/claude/tree/main/skills a nainstaluj mi do `~/.claude/skills/` celý životní cyklus: project, discovery, specify, architect, breakdown, implement, release, evaluate, oponent, consolidate, review, consistency, attack, end a merge. Každý z nich nainstaluj přesně podle promptu v sekci „Jak si ho nainstalovat“ v jeho README; na skilly z téhle sady se mě při tom neptej, beru je všechny.

---

### Požadavky a omezení

Git. Nic dalšího se neinstaluje. Skill předpokládá jednu hlavní větev, do které se slučuje (typicky `main`); jmenuje-li se jinak, pozná ji sám. Slučování přes pull request na serveru neumí – merguje lokálně a pushuje výsledek.
