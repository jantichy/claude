# /specify – z nápadu zadání, než se sáhne na kód

> **Součást životního cyklu projektu.** Tenhle skill patří do ucelené sady jedenácti skillů, které vedou práci od založení projektu až po nasazení. Každý má svůj krok a žádný nedělá práci toho vedle:
>
> [`/project`](../project/README.md) → [`/discovery`](../discovery/README.md) → **`/specify`** → [`/oponent`](../oponent/README.md) → [`/breakdown`](../breakdown/README.md) → [`/implement`](../implement/README.md) → [`/review`](../review/README.md) → [`/consistency`](../consistency/README.md) → [`/cleanup`](../cleanup/README.md) → [`/attack`](../attack/README.md) → [`/release`](../release/README.md)
>
> Projít se nemusí celá – u drobné změny odpadá zadání i plán, u projektu bez kódu nasazení.

Máte nápad a chcete z něj něco, podle čeho se dá stavět. Skill vás provede vyptáváním otázku po otázce a udělá z toho **dvě zadání**: jedno odpovídá na otázku *co stavíme a proč*, druhé na otázku *jak*. Dokud nejsou hotová a schválená, nesmí vzniknout ani řádek kódu – a to je tvrdé pravidlo, ne doporučení.

## Co umí

1. **Vytěží nejdřív to, co už máte.** Než se na cokoliv zeptá, vyzve vás, ať přiložíte poznámky, zápis ze schůzky, mail od klienta, starý dokument, screenshoty – i nestrukturovaně. Co si z toho odvodí, se pak už neptá; jen vám ukáže souhrn k potvrzení.
2. **Ptá se postupně**, jednu otázku za druhou, ne dotazníkem na deset položek.
3. **Produktová specifikace** – proč to děláme, pro koho, hlavní scénáře, varianty a rozhodovací větve, omezení, nefunkční požadavky, seznam toho, co musí umět první verze, co vědomě neděláme a podle čeho se za rok pozná, že to vyšlo.
4. **Návrh řešení** – zvolený přístup i zamítnuté varianty, architektura, datový model, stavy a přechody, datové toky, rozhraní, cizí systémy, chybové stavy, bezpečnostní model, technologie, testovací strategie a rizika.
5. **Pozná, kdy specifikace nedává smysl.** Je-li to změna v existujícím kódu nebo jednorázová otázka, řekne to a zastaví se – nenechá se zatlačit do psaní specifikace na jednosouborovou změnu.
6. **Zvládne i projekt bez kódu** – kurz, pozicování, evidenci. Tam napíše produktovou část a místo návrhu řešení nabídne rozpis kroků.
7. **Dá se spustit i uprostřed** – navázat návrhem na hotové požadavky, rozšířit stávající návrh o novou funkci, nebo zadání revidovat.
8. **Vlastní kontrola po každém dokumentu** a pak nezávislá oponentura.

## Proč zrovna tenhle

- **Dva dokumenty, protože mají jinou životnost.** Produktový záměr se mění zřídka, technické řešení s každým rozhodnutím o technologii. V jednom souboru by se při výměně databáze editoval tentýž text, ve kterém stojí popis cílové skupiny, a produktová část by se tím postupně obrušovala.
- **Hranice mezi nimi je ostrá a má test.** *Změní se ta věta, když vyměním databázi?* Ano → návrh. Ne → požadavky. „Musí to běžet na běžném hostingu" je omezení a patří do požadavků; „použijeme SQLite, protože…" je volba a patří do návrhu.
- **Zákaz implementace je brána, ne rada.** Žádný scaffold, žádné „jen si ověřím, že to jde" – scaffold zamkne technologie dřív, než se o nich rozhodlo. Jediná výjimka je krátká ověřovací sonda, jejíž kód se pak zahodí.
- **Nic si nevymýšlí.** Technický název, identifikátor, parametr, cizí rozhraní ani cena se nedomýšlejí – co není známé, jde do otevřených otázek i s tím, kdo to má rozhodnout.
- **Žádné placeholdery.** „Rychlé načítání" je nic; požadavek má číslo, práh a podmínku.
- **Sekce „co vědomě neděláme" nesmí být prázdná.** Prázdná znamená, že se nic neřezalo – a co se vyhodí, se tam zapíše, aby to nikdo nevymyslel znovu.
- **Bezpečnost se navrhuje, neaudituje.** Návrh má vlastní sekci s modelem oprávnění a jmenným seznamem citlivých míst; „ošetříme to při implementaci" v ní stát nesmí.
- **Návrh se čte proti požadavkům položku po položce.** Nepokrytý scénář je nález, ne detail.
- **Na návrhu se nešetří.** Špatný návrh se dobrou implementací nezachrání – špatná věc se jen udělá pořádně.

## Jak se to používá

```
/specify
```

Skill se zeptá, co už máte, provede vás vyptáváním, sepíše požadavky, nechá si je schválit, pak sepíše návrh, nechá si schválit i ten a předá to do implementačního plánu.

## Ukázka výstupu

```
## Zadání hotové

**Dokumenty**
- docs/requirements.md – 12 sekcí
- docs/architecture.md – 14 sekcí

**Zapsáno mimo ně**
- docs/decisions.md: 7 rozhodnutí
- docs/todo.md: 3 odložené položky

**Otevřené otázky**
- kdo schvaluje ceník před spuštěním

**Další krok:** /breakdown
```

## Co nedělá

- **Nic neprogramuje.** Ani scaffold, ani „jen rychle rozjedu projekt".
- **Nezakládá projekt.** Strukturu, git a nastavení dělá `/project`; když chybí, skill na to upozorní.
- **Nepíše implementační plán.** Ten dělá `/breakdown` a má vlastní pravidla i vlastní schvalovací bránu.

## Jak si ho nainstalovat

Nechte to na Claudovi. Otevřete si Claude Code a napište mu:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/specify a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.

Skill je z části **obálka nad pluginem [superpowers](https://github.com/obra/superpowers)** – ten potřebujete mít nainstalovaný, klidně o to Clauda požádejte zároveň. Sám k němu přidává produktový rámec, rozdělení na dvě zadání, tvar obou dokumentů a vynucené umístění. Odkazuje se i na moje soukromé standardy pro psaní textů a pro kód – **řekněte Claudovi, ať ty odkazy nahradí vašimi, nebo je smaže**.


**Nebo celou sadu naráz.** Chcete-li místo jednoho skillu rovnou celý životní cyklus, napište mu tohle:

> Jdi na https://github.com/jantichy/claude/tree/main/skills a nainstaluj mi do `~/.claude/skills/` celý životní cyklus: project, discovery, specify, oponent, breakdown, implement, review, consistency, cleanup, attack a release. U každého si přečti README a řekni mi, co k nim potřebuju doplnit.

---

### Požadavky a omezení

Plugin superpowers. Skill předpokládá, že má projekt kam zapisovat rozhodnutí a odložené věci – chybí-li ta místa, nezaloží je potichu, ale upozorní. Návrhová část běží na nejsilnějším modelu, takže není z nejlevnějších.
