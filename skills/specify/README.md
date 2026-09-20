# /specify – z nápadu zadání, než se sáhne na kód

> **Součást životního cyklu projektu.** Tenhle skill patří do ucelené sady skillů, které vedou práci od založení projektu až po nasazení. Jedny tvoří, druhé měří, co už je – a žádný nedělá práci toho vedle:
>
> **Osa** [`/project`](../project/README.md) → [`/discovery`](../discovery/README.md) → **`/specify`** → `/architect` → [`/breakdown`](../breakdown/README.md) → [`/implement`](../implement/README.md) → [`/release`](../release/README.md)
>
> **Kontroly** [`/oponent`](../oponent/README.md) · `/consolidate` · [`/review`](../review/README.md) · [`/consistency`](../consistency/README.md) · [`/attack`](../attack/README.md) · [`/cleanup`](../cleanup/README.md) – stojí v mezerách mezi kroky osy, některé z nich ve víc mezerách
>
> Projít se nemusí celý – u drobné změny odpadá zadání i plán, u projektu bez kódu nasazení.

Máte nápad a chcete z něj něco, podle čeho se dá stavět. Skill vás provede vyptáváním otázku po otázce a udělá z toho **dvě zadání**: jedno odpovídá na otázku *co stavíme a proč*, druhé na otázku *jak*. Větší záměr přitom nejdřív rozdělí na tematická kola a druhé zadání napíše až nad jejich výsledkem. Dokud nejsou hotová a schválená, nesmí vzniknout ani řádek kódu – a to je tvrdé pravidlo, ne doporučení.

## Co umí

1. **Vytěží nejdřív to, co už máte** – včetně zásobníku nápadů, který si projekt vede. Nabídne z něj, co se do právě psaného zadání hodí vzít rovnou s sebou. Než se na cokoliv zeptá, vyzve vás, ať přiložíte poznámky, zápis ze schůzky, mail od klienta, starý dokument, screenshoty – i nestrukturovaně. Co si z toho odvodí, se pak už neptá; jen vám ukáže souhrn k potvrzení.
2. **Ptá se postupně**, jednu otázku za druhou, ne dotazníkem na deset položek.
3. **Produktová specifikace** – proč to děláme, pro koho, varianty a rozhodovací větve, omezení, nefunkční požadavky, seznam toho, co musí umět první verze, co vědomě neděláme a podle čeho se za rok pozná, že to vyšlo.
4. **Návrh řešení** – zvolený přístup i zamítnuté varianty, architektura, datový model, stavy a přechody, datové toky, rozhraní, cizí systémy, chybové stavy, bezpečnostní model, technologie, testovací strategie a rizika.
5. **Sepíše i scénáře, glosář a ceník**, vede-li je projekt. Scénáře jsou taxativní seznam toho, co uživatel s produktem dělá, krok za krokem – slouží pak i testování, nápovědě a FAQ. Glosář drží pojmenování domény, ceník to, co z tarifů a limitů plyne pro produkt.
6. **Pozná, kdy specifikace nedává smysl.** Je-li to změna v existujícím kódu nebo jednorázová otázka, řekne to a zastaví se – nenechá se zatlačit do psaní specifikace na jednosouborovou změnu.
7. **Zvládne i projekt bez kódu** – kurz, pozicování, evidenci. Tam napíše produktovou část a místo návrhu řešení nabídne rozpis kroků.
8. **Větší záměr rozdělí na tematická kola.** Nejdřív zmapuje celý záměr a rozdělí ho na okruhy – třeba daně, upomínání, administraci, platební bránu – a každý zapíše jako samostatný úkol se vším, co k němu patří. Kola pak můžete řešit jedno po druhém, nebo – má-li projekt pracovní adresář pro každou větev zvlášť – klidně v pěti souběžných sessions a větvích. Každé kolo se rozhodne do posledního detailu a zanechá po sobě záznam, co rozhodlo a na co nesáhlo. Nakonec skill kola sešije a teprve nad celkem navrhne řešení.
9. **Dá se spustit i uprostřed** – navázat návrhem na hotové požadavky, rozšířit stávající návrh o novou funkci, nebo zadání revidovat.
10. **Vlastní kontrola po každém dokumentu.** Nezávislou oponenturu a další kroky nespouští sám, jen v závěru řekne, co pustit a v jakém pořadí.

## Proč zrovna tenhle

- **Dva dokumenty, protože mají jinou životnost.** Produktový záměr se mění zřídka, technické řešení s každým rozhodnutím o technologii. V jednom souboru by se při výměně databáze editoval tentýž text, ve kterém stojí popis cílové skupiny, a produktová část by se tím postupně obrušovala.
- **Hranice mezi nimi je ostrá a má test.** *Změní se ta věta, když vyměním databázi?* Ano → návrh. Ne → požadavky. „Musí to běžet na běžném hostingu“ je omezení a patří do požadavků; „použijeme SQLite, protože…“ je volba a patří do návrhu.
- **Zákaz implementace je kontrola, ne rada.** Žádný scaffold, žádné „jen si ověřím, že to jde“ – scaffold zamkne technologie dřív, než se o nich rozhodlo. Jediná výjimka je krátký ověřovací pokus, jehož kód se pak zahodí.
- **Nic si nevymýšlí.** Technický název, identifikátor, parametr, cizí rozhraní ani cena se nedomýšlejí – co není známé, jde do otevřených otázek i s tím, kdo to má rozhodnout.
- **Žádné placeholdery.** „Rychlé načítání“ je nic; požadavek má číslo, práh a podmínku.
- **Sekce „co vědomě neděláme“ nesmí být prázdná.** Prázdná znamená, že se nic neřezalo – a co se vyhodí, se tam zapíše, aby to nikdo nevymyslel znovu.
- **Bezpečnost se navrhuje, neaudituje.** Návrh má vlastní sekci s modelem oprávnění a jmenným seznamem citlivých míst; „ošetříme to při implementaci“ v ní stát nesmí.
- **Návrh se čte proti požadavkům položku po položce.** Nepokrytý scénář je nález, ne detail.
- **Kola nesplývají s hotovým návrhem.** Otevřená otázka se neodkládá na „později“, ale na jmenované kolo, a záznam kola říká i to, co nechalo být. Za půl roku se tak pozná, jestli je věc nerozhodnutá, nebo rozhodnutá jinak.
- **Na návrhu se nešetří.** Špatný návrh se dobrou implementací nezachrání – špatná věc se jen udělá pořádně.

## Jak se to používá

```
/specify
```

Skill se sám zorientuje, kde návrh je (režim `auto`). Na začátku (`create`) se zeptá, co už máte, provede vás vyptáváním a sepíše požadavky. Malý záměr dotáhne rovnou i s návrhem řešení, větší rozdělí na kola. Uprostřed nabídne kola, která jsou na řadě – nabídku za něj sestaví skill [`/next`](../next/README.md). Když jsou všechna kola hotová, sešije je (`close`).

```
/specify round DPH     # odjede kolo o DPH – totéž udělá i /specify DPH
/specify round         # přes /next vypíše zbývající kola a nabídne, čím pokračovat
/specify close         # po sloučení všech kol navrhne řešení nad celkem
```

## Ukázka výstupu

```
## Zadání hotové

**Dokumenty**
- docs/requirements.md – 12 sekcí
- docs/architecture.md – 13 sekcí

**Zapsáno mimo ně**
- docs/decisions.md: 7 rozhodnutí
- docs/todo.md: 3 odložené položky
- docs/backlog.md: 2 nápady vytaženy do zadání, 5 ponecháno

**Otevřené otázky**
- kdo schvaluje ceník před spuštěním

**Další krok:** /breakdown
```

## Co nedělá

- **Nic neprogramuje.** Ani scaffold, ani „jen rychle rozjedu projekt“.
- **Nezakládá projekt.** Strukturu, git a nastavení dělá `/project`; když chybí, skill na to upozorní.
- **Nepíše implementační plán.** Ten dělá `/breakdown` a má vlastní pravidla i vlastní schvalovací kontrolu.
- **Nepouští další kroky a neslučuje větve.** Posudek, úklid, plán ani sloučení kola nespustí sám (jedinou výjimkou je nabídka kol přes `/next`) – jen v závěru řekne, co pustit a v jakém pořadí.

## Jak si ho nainstalovat

Nechte to na Claudovi. Otevřete si Claude Code a napište mu:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/specify a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.

Skill je z části **obálka nad pluginem [superpowers](https://github.com/obra/superpowers)** – ten potřebujete mít nainstalovaný, klidně o to Clauda požádejte zároveň. Sám k němu přidává produktový rámec, rozdělení na dvě zadání, tvar obou dokumentů a vynucené umístění. Odkazuje se i na moje soukromé standardy pro psaní textů a pro kód – **řekněte Claudovi, ať ty odkazy nahradí vašimi, nebo je smaže**.


**Nebo celou sadu naráz.** Chcete-li místo jednoho skillu rovnou celý životní cyklus, napište mu tohle:

> Jdi na https://github.com/jantichy/claude/tree/main/skills a nainstaluj mi do `~/.claude/skills/` celý životní cyklus: project, discovery, specify, oponent, breakdown, implement, review, consistency, cleanup, attack a release. Z https://github.com/jantichy/claude/tree/main/agents k tomu vezmi i definice typů subagentů do `~/.claude/agents/`. U každého si přečti README a řekni mi, co k nim potřebuju doplnit.

---

### Požadavky a omezení

Plugin superpowers. Souběžná kola potřebují projekt rozložený na pracovní adresáře po větvích (git worktree); bez toho se kola řeší postupně. Skill předpokládá, že má projekt kam zapisovat rozhodnutí a odložené věci – chybí-li ta místa, nezaloží je potichu, ale upozorní. Návrhová část běží na nejsilnějším modelu, takže není z nejlevnějších.
