# /specify – z nápadu zadání, než se sáhne na kód

> **Součást životního cyklu projektu.** Tenhle skill patří do ucelené sady skillů, které vedou práci od založení projektu až po vyhodnocení provozu. Jedny tvoří, druhé se starají o to, co už vzniklo – a žádný nedělá práci toho vedle:
>
> **Osa** [`/project`](../project/README.md) → [`/discovery`](../discovery/README.md) → **`/specify`** → [`/architect`](../architect/README.md) → [`/breakdown`](../breakdown/README.md) → [`/implement`](../implement/README.md) → [`/release`](../release/README.md) → [`/evaluate`](../evaluate/README.md)
>
> **Kontroly** [`/oponent`](../oponent/README.md) · `/consolidate` · [`/review`](../review/README.md) · [`/consistency`](../consistency/README.md) · [`/attack`](../attack/README.md) · [`/cleanup`](../cleanup/README.md) · [`/merge`](../merge/README.md) – stojí v mezerách mezi kroky osy, některé z nich ve víc mezerách
>
> Projít se nemusí celý – u drobné změny odpadá zadání i plán, u projektu bez kódu nasazení i vyhodnocení provozu.

Máte nápad a chcete z něj něco, podle čeho se dá rozhodovat. Skill vás provede vyptáváním otázku po otázce a udělá z toho **zadání**: dokument, který odpovídá na otázku *co stavíme a proč* – a k němu scénáře, glosář a ceník, vede-li je projekt. Jak se to postaví, nerozhoduje; to je práce navazujícího [`/architect`](../architect/README.md). Dokud není zadání hotové a schválené, nesmí vzniknout ani řádek kódu – a to je tvrdé pravidlo, ne doporučení.

## Co umí

1. **Vytěží nejdřív to, co už máte** – včetně zásobníku nápadů, který si projekt vede. Nabídne z něj, co se do právě psaného zadání hodí vzít rovnou s sebou. Než se na cokoliv zeptá, vyzve vás, ať přiložíte poznámky, zápis ze schůzky, mail od klienta, starý dokument, screenshoty – i nestrukturovaně. Co si z toho odvodí, se pak už neptá; jen vám ukáže souhrn k potvrzení.
2. **Ptá se postupně**, jednu otázku za druhou, ne dotazníkem na deset položek.
3. **Produktová specifikace** – proč to děláme, pro koho, varianty a rozhodovací větve, omezení, nefunkční požadavky, seznam toho, co musí umět první verze, co vědomě neděláme a podle čeho se za rok pozná, že to vyšlo.
4. **Sepíše i scénáře, glosář a ceník**, vede-li je projekt. Scénáře jsou taxativní seznam toho, co uživatel s produktem dělá, krok za krokem – slouží pak i testování, nápovědě a FAQ. Glosář drží pojmenování domény, ceník to, co z tarifů a limitů plyne pro produkt.
5. **Pozná, kdy specifikace nedává smysl.** Je-li to změna v existujícím kódu nebo jednorázová otázka, řekne to a zastaví se – nenechá se zatlačit do psaní specifikace na jednosouborovou změnu.
6. **Zvládne i projekt bez kódu** – kurz, pozicování, evidenci. Tam napíše zadání a místo návrhu řešení nabídne rozpis kroků.
7. **Dá se spustit i uprostřed** – rozšířit hotové zadání o novou funkci, nebo ho revidovat.
8. **Vlastní kontrola po každém dokumentu.** Nezávislou oponenturu a další kroky nespouští sám, jen v závěru řekne, co pustit a v jakém pořadí.

## Proč zrovna tenhle

- **Zadání a návrh jsou oddělené, protože mají jinou životnost.** Produktový záměr se mění zřídka, technické řešení s každým rozhodnutím o technologii. V jednom souboru by se při výměně databáze editoval tentýž text, ve kterém stojí popis cílové skupiny, a produktová část by se tím postupně obrušovala.
- **Hranice mezi nimi je ostrá a má test.** *Změní se ta věta, když vyměním databázi?* Ano → návrh. Ne → požadavky. „Musí to běžet na běžném hostingu“ je omezení a patří do požadavků; „použijeme SQLite, protože…“ je volba a patří do návrhu.
- **Zákaz implementace je kontrola, ne rada.** Žádný scaffold, žádné „jen si ověřím, že to jde“ – scaffold zamkne technologie dřív, než se o nich rozhodlo. Jediná výjimka je krátký ověřovací pokus, jehož kód se pak zahodí.
- **Nic si nevymýšlí.** Technický název, identifikátor, parametr, cizí rozhraní ani cena se nedomýšlejí – co není známé, jde do otevřených otázek i s tím, kdo to má rozhodnout.
- **Žádné placeholdery.** „Rychlé načítání“ je nic; požadavek má číslo, práh a podmínku.
- **Sekce „co vědomě neděláme“ nesmí být prázdná.** Prázdná znamená, že se nic neřezalo – a co se vyhodí, se tam zapíše, aby to nikdo nevymyslel znovu.
- **Vytěží i zásobník nápadů.** Co v něm leží k tématu, vám nabídne zařadit rovnou do zadání – jinak by tam leželo dál a nikdy se nepřipomnělo.

## Jak se to používá

Napíšete `/specify` a skill se zeptá, co už máte, provede vás vyptáváním a sepíše zadání. Žádné režimy nemá; téma můžete přidat za příkaz (`/specify rezervace školení`). Existuje-li zadání už, rozšíří ho nebo zreviduje – nezaloží druhé.

## Ukázka výstupu

```
## Zadání hotové

**Dokumenty**
- docs/requirements.md – 12 sekcí
- docs/scenarios.md – 9 scénářů
- docs/glossary.md – 23 pojmů

**Zapsáno mimo ně**
- docs/decisions.md: 7 rozhodnutí
- docs/todo.md: 3 odložené položky
- docs/backlog.md: 2 nápady vytaženy do zadání, 5 ponecháno

**Otevřené otázky**
- kdo schvaluje ceník před spuštěním

**Další krok:** /oponent docs/requirements.md, /cleanup, pak /architect
```

## Co nedělá

- **Nic neprogramuje.** Ani scaffold, ani „jen rychle rozjedu projekt“.
- **Nerozhoduje, jak se to postaví.** Architekturu, data, technologie a bezpečnostní model má `/architect`.
- **Nezakládá projekt.** Strukturu, git a nastavení dělá `/project`; když chybí, skill na to upozorní.
- **Nepouští další kroky.** Posudek, úklid ani návrh nespustí sám – jen v závěru řekne, co pustit a v jakém pořadí.

## Jak si ho nainstalovat

Nechte to na Claudovi. Otevřete si Claude Code a napište mu:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/specify a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.

Skill je z části **obálka nad pluginem [superpowers](https://github.com/obra/superpowers)** – ten potřebujete mít nainstalovaný, klidně o to Clauda požádejte zároveň. Sám k němu přidává produktový rámec, tvar dokumentů a vynucené umístění. Odkazuje se i na moje soukromé standardy pro psaní textů – **řekněte Claudovi, ať ty odkazy nahradí vašimi, nebo je smaže**.


**Nebo celou sadu naráz.** Chcete-li místo jednoho skillu rovnou celý životní cyklus, napište mu tohle:

> Jdi na https://github.com/jantichy/claude/tree/main/skills a nainstaluj mi do `~/.claude/skills/` celý životní cyklus: project, discovery, specify, architect, breakdown, implement, release, evaluate, oponent, review, consistency, attack, cleanup a merge. Z https://github.com/jantichy/claude/tree/main/agents k tomu vezmi i definice typů subagentů do `~/.claude/agents/`. U každého si přečti README a řekni mi, co k nim potřebuju doplnit.

---

### Požadavky a omezení

Plugin superpowers. Skill předpokládá, že má projekt kam zapisovat rozhodnutí a odložené věci – chybí-li ta místa, nezaloží je potichu, ale upozorní. Sám o sobě nestačí: návrh řešení, který z výsledku vzniká, dělá [`/architect`](../architect/README.md).
