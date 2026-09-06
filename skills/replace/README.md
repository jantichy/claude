# /replace – přejmenovat něco a opravdu všude

Přejmenování napříč projektem vypadá jako práce pro hledání a nahrazení, ale nikdy jí není. Vždycky někde zůstane starý tvar – v názvu souboru, ve skloňované české variantě, v hodnotě uvnitř datového souboru, v odkazu, který se rozbije, aniž se změní text. A vrací se pak měsíce jako záhada. Tenhle skill projde všechny roviny, ve kterých se pojem může vyskytovat, ukáže nález ke schválení, změnu provede a **na konci ověří, že starý tvar v projektu opravdu nikde nezůstal**.

## Co umí

1. **Odvodí všechny tvary**, ve kterých pojem žije – množné číslo, spojení slov velkými písmeny, podtržítka, pomlčky, verzálky, konstanty a **české skloňované varianty**, které hledání na základní tvar nenajde.
2. **Hledá i tam, kam se nekouká** – v názvech souborů a adresářů, v hodnotách uvnitř dat a konfigurací, v komentářích a dokumentaci, v odkazech a kotvách, v nastavení repozitáře.
3. **Ukáže inventuru ke schválení** – kolik výskytů, ve kolika souborech, co vědomě vynechává a proč. Nad dvacet výskytů je nepředkládá po jednom, ale jako vzor s ukázkami.
4. **Vytřídí falešné shody** – cizí termín, který se náhodou jmenuje stejně, citaci, historický záznam. Ty předloží zvlášť.
5. **Provede změnu ve správném pořadí** – nejdřív obsah, pak názvy, delší tvary před kratšími, přesuny s podrženou historií.
6. **Kontrolní průchod na závěr** – hledání starého tvaru musí vrátit nulu; kontrolují se i odkazy, součty a přehledové tabulky, které se aktualizovat zapomínají.
7. Funguje i na změny, které nejsou přejmenování: jiná hodnota, jiná konvence, jiný způsob zápisu.

## Proč zrovna tenhle

- **Česká skloňovaná varianta.** Zrádnost, kterou anglicky psané nástroje neřeší vůbec – a v dokumentaci jí bývá nejvíc.
- **Pořadí náhrad je promyšlené.** Delší tvary jdou první, takže z přejmenování nevznikne komolenina.
- **Soubory se přesouvají tak, aby nezmizela historie.**
- **Kontrolní průchod je povinný, ne volitelný.** Skill neskončí větou „mělo by to být hotové" – buď starý tvar nikde není, nebo řekne, kde zůstal.
- **Vypíše, na co vědomě nesáhl** – archivy, cizí podklady, historické záznamy. Takže víte, co je záměr a co opomenutí.
- **Nezačne nad rozdělanou prací.** Neuložené změny by se s přejmenováním smíchaly a přestalo by být poznat, co je čí.

## Jak se to používá

```
/replace market → site
```

Skill si nechá odsouhlasit tvary a rozsah, ukáže inventuru, provede změnu a doloží kontrolní průchod.

## Ukázka výstupu

```
## Nalezeno

Tvar              Výskytů   Souborů
market              47        12
markets              8         4
marketId            23         6
„trh" (skloňované)  15         3
market.md            1         –  (název souboru)

Celkem: 95 výskytů v 18 souborech + 2 přejmenování
Nesahám na: docs/research/ (12 výskytů), CHANGELOG.md (31 výskytů)
```

## Co nedělá

- **Nerozhoduje, jestli se má přejmenovat.** To je vaše rozhodnutí, skill ho provede.
- **Nesahá mimo projekt** ani do archivů cizích podkladů.
- **Nemění chování.** Ukáže-li se, že přejmenování vyžaduje i migraci dat nebo přesměrování adres, zastaví se a řekne to.

## Jak si ho nainstalovat

Nechte to na Claudovi. Otevřete si Claude Code a napište mu:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/replace a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.

Nic dalšího potřeba není. Skill se odkazuje na moje soukromé konvence pro projekty s víc pracovními adresáři a na místo, kam se zapisují rozhodnutí – **řekněte Claudovi, ať ty odkazy nahradí vašimi, nebo je smaže**; na jádro nemají vliv.

---

### Požadavky a omezení

Git (kvůli přesunům se zachovanou historií) a běžné nástroje pro hledání v souborech. Přejmenovává-li se celý projekt, hodí se i příkazová řádka GitHubu kvůli názvu repozitáře a jeho popisku.
