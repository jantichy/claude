# /architect – rozhodnout, jak se to postaví

> **Součást životního cyklu projektu.** Tenhle skill patří do ucelené sady skillů, které vedou práci od založení projektu až po vyhodnocení provozu. Jedny tvoří, druhé se starají o to, co už vzniklo – a žádný nedělá práci toho vedle:
>
> **Osa** [`/project`](../project/README.md) → [`/discovery`](../discovery/README.md) → [`/specify`](../specify/README.md) → **`/architect`** → [`/breakdown`](../breakdown/README.md) → [`/implement`](../implement/README.md) → [`/release`](../release/README.md) → [`/evaluate`](../evaluate/README.md)
>
> **Kontroly** [`/oponent`](../oponent/README.md) · `/consolidate` · [`/review`](../review/README.md) · [`/consistency`](../consistency/README.md) · [`/attack`](../attack/README.md) · [`/cleanup`](../cleanup/README.md) · [`/merge`](../merge/README.md) – stojí v mezerách mezi kroky osy, některé z nich ve víc mezerách
>
> Projít se nemusí celý – u drobné změny odpadá zadání i plán, u projektu bez kódu nasazení i vyhodnocení provozu.

Zadání říká, **co** se staví a proč. Tenhle skill rozhodne **jak** – architekturu, data, stavy a přechody, rozhraní, napojení na cizí systémy a bezpečnost – a zapíše to tak, aby se podle toho dal napsat plán a pak kód. Větší záměr přitom nejdřív rozdělí na tematická kola a každé rozhodne do posledního detailu. Dokud není návrh hotový a schválený, nesmí vzniknout ani řádek kódu; to je tvrdé pravidlo, ne doporučení.

## Co umí

1. **Sám se zorientuje.** Nemá žádné režimy ani přepínače – napíšete `/architect` a skill ze stavu projektu pozná, co je na řadě: jestli se má teprve mapovat, jestli běží nějaké kolo, nebo jestli je čas kola sešít. Vždycky jednou větou oznámí, co bude dělat, **než sáhne na první soubor**, takže to stihnete opravit. Chcete-li to ovlivnit, napište mu to volnými slovy za příkaz.
2. **Nejdřív se zeptá, jestli je vůbec co navrhovat.** Šest kritérií – nový podsystém, změna datového modelu, nové rozhraní, cizí systém, stavový prostor, víc rozumných cest. Neplatí-li ani jedno, řekne to a zastaví se, místo aby vyrobil dokument, který nikdo nečetl.
3. **Návrh řešení** – zvolený přístup i zamítnuté varianty, architektura, transakce a souběh, datový model, stavy a přechody, datové toky, rozhraní, cizí systémy, chybové stavy, bezpečnostní model, technologie, testovací strategie a rizika.
4. **Návrh je sada dokumentů, ne jeden nafouklý soubor.** Páteř drží stavbu, vedle ní vzniká dokument o datech, o operacích, o zásadách domény – ale jen tehdy, když odpovídá na otázku, na kterou žádný jiný neodpovídá. Ne proto, že je ten stávající dlouhý.
5. **Větší záměr rozdělí na tematická kola.** Zmapuje ho na okruhy – třeba daně, upomínání, administraci, platební bránu – a každý zapíše jako samostatný úkol se vším, co k němu patří. Kola pak řešíte jedno po druhém, nebo – má-li projekt pracovní adresář pro každou větev zvlášť – klidně v pěti souběžných sessions. Každé po sobě nechá záznam, co rozhodlo a na co nesáhlo. Nakonec je skill sešije a teprve nad celkem navrhne řešení.
6. **Ptá se postupně**, jednu otázku za druhou, ne dotazníkem na deset položek. A nic si nevymýšlí – technický název, parametr ani cenu, kterou nemá odkud znát.
7. **Kontroluje návrh proti zadání.** U každého scénáře a každého rizika ukáže, co v návrhu ho pokrývá. Nepokryté je nález, ne detail.
8. **Dá se spustit i uprostřed** – navázat na hotové požadavky, rozšířit stávající návrh o novou funkci, nebo pokračovat rozdělaným kolem.

## Proč zrovna tenhle

- **Žádné přepínače k zapamatování.** Co je na řadě, plyne ze stavu projektu, ne z toho, jestli si vzpomenete na správné slovo. A protože se rozhoduje z tabulky stavů, ne odhadem, chová se to pokaždé stejně.
- **Bezpečnost se navrhuje, neaudituje.** Zhruba polovina kódu psaného modely obsahuje bezpečnostní chybu a je to předvídatelná množina. Nejúčinnější obrana není kontrola na konci, ale struktura, ve které díra nejde udělat – proto má návrh vlastní kapitolu a nesmí v ní stát „ošetříme to při implementaci“.
- **Rozhodování po tématech, ne po kapitolách.** Témata se prolínají, takže průchod po dokumentech otevře každý z nich pětkrát a pokaždé s jiným kusem znalosti v hlavě. Průchod po tématech ho otevře stejněkrát, ale pokaždé s uzavřenou otázkou.
- **Zákaz implementace je kontrola, ne rada.** Žádný scaffold, žádné „jen si ověřím, že to jde“ – scaffold zamkne technologie dřív, než se o nich rozhodlo. Jediná výjimka je krátký ověřovací pokus, jehož kód se pak zahodí.
- **Běží na nejsilnějším modelu.** Špatný návrh se dobrou implementací nezachrání – špatná věc se jen udělá pořádně.

## Jak se to používá

Napíšete `/architect` a skill řekne, co je podle stavu projektu na řadě. Chcete-li konkrétní kolo, přidáte jeho jméno: `/architect platební brána`. Cokoliv jiného za příkazem bere jako pokyn, který jeho volbu přebije.

## Ukázka výstupu

```
Návrh je po kolech, všechna jsou sloučená a čeká se na sešití – jdu tedy
vyrobit návrh nad celkem.

Dokumenty
- docs/architecture.md – 13 sekcí
- docs/model.md – entity, vztahy a izolace nájemců
- docs/transitions.md – 41 operací se vstupními podmínkami
- 5 tematických dokumentů kol

Otevřené otázky
- Limit velikosti přílohy u hromadného mailingu – čeká na odpověď dodavatele

Další krok
- /oponent docs/architecture.md, pak /consistency, /cleanup a /breakdown
```

## Co nedělá

- **Nepíše požadavky.** Co se staví a proč, pro koho to je a jaké jsou scénáře, drží `/specify`.
- **Nic neprogramuje** a **nepíše implementační plán** – ten dělá `/breakdown` a má vlastní pravidla.
- **Neposuzuje vlastní návrh a neslučuje větve.** Posudek, úklid ani sloučení kola nespustí sám – jen v závěru řekne, co pustit a v jakém pořadí.
- **Nehledá, jestli by to dnes šlo navrhnout jednodušeji.** To je otázka na `/consolidate`; tenhle skill rozhoduje dopředu, ne zpětně.

## Jak si ho nainstalovat

Nechte to na Claudovi. Otevřete si Claude Code a napište mu:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/architect a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.

Skill se odkazuje na moje soukromé standardy pro psaní textů a pro kód – **řekněte Claudovi, ať ty odkazy nahradí vašimi, nebo je smaže**. Nabídku rozdělaných kol si vyžádá od skillu `/next`; bez něj funguje všechno ostatní a kolo se vybírá jménem.

**Nebo celou sadu naráz.** Chcete-li místo jednoho skillu rovnou celý životní cyklus, napište mu tohle:

> Jdi na https://github.com/jantichy/claude/tree/main/skills a nainstaluj mi do `~/.claude/skills/` celý životní cyklus: project, discovery, specify, architect, breakdown, implement, release, evaluate, oponent, review, consistency, attack, cleanup a merge. Z https://github.com/jantichy/claude/tree/main/agents k tomu vezmi i definice typů subagentů do `~/.claude/agents/`. U každého si přečti README a řekni mi, co k nim potřebuju doplnit.

---

### Požadavky a omezení

Souběžná kola potřebují projekt rozložený na pracovní adresáře po větvích (git worktree); bez toho se kola řeší postupně. Skill předpokládá, že má projekt kam zapisovat rozhodnutí a odložené věci – chybí-li ta místa, nezaloží je potichu, ale upozorní. Běží na nejsilnějším modelu, takže není z nejlevnějších. U projektu bez kódu se nepouští vůbec.
