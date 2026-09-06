# /cleanup – ať po mně zůstane čisto a jasno

> **Součást životního cyklu projektu.** Tenhle skill patří do ucelené sady jedenácti skillů, které vedou práci od založení projektu až po nasazení. Každý má svůj krok a žádný nedělá práci toho vedle:
>
> [`/project`](../project/README.md) → [`/discovery`](../discovery/README.md) → [`/specify`](../specify/README.md) → [`/oponent`](../oponent/README.md) → [`/breakdown`](../breakdown/README.md) → [`/implement`](../implement/README.md) → [`/review`](../review/README.md) → [`/consistency`](../consistency/README.md) → **`/cleanup`** → [`/attack`](../attack/README.md) → [`/release`](../release/README.md)
>
> Projít se nemusí celá – u drobné změny odpadá zadání i plán, u projektu bez kódu nasazení.

Když je práce u konce a chystáte se sezení opustit nebo nechat zkompaktovat, tíží vás pokaždé totéž: neztratí se něco? Tenhle skill to vyřeší. Přečte si **celý surový záznam konverzace** – tedy včetně části, kterou už kompaktace z paměti vyhodila –, vytáhne z něj všechno, co se domluvilo, a zapíše to tam, kam to patří. Pak si otočí pohled a hledá druhou věc: co v konverzaci zůstalo viset bez vypořádání. Na konec pošle na projekt někoho, kdo o něm nic neví, a nechá si od něj říct, jestli se na dnešní práci dá navázat.

## Co umí

1. **`/cleanup`** (výchozí) – vytěží konverzaci celou a závěrečná kontrola se soustředí na to, čeho se dnešní práce dotkla.
2. **`/cleanup full`** – vytěžení je stejné, ale závěrečná kontrola projde celou dokumentaci projektu.
3. **Vytáhne ze záznamu sedm věcí** – dohody a rozhodnutí (vždy i s důvodem a zavrženými variantami), nová pravidla a konvence, odvedenou práci, vědomě odložené úkoly, postřehy mimo hlavní téma, korekce (platí poslední verze, ne první) a zamluvená témata.
4. **Dohledá, co propadlo.** Nejčastější ztráta v dlouhé konverzaci není zapomenutý zápis, ale zamluvené téma: přišla dlouhá odpověď s několika body, vy jste se chytili poloviny a zbytek zůstal bez vypořádání. Nikdo to nezavrhl ani neschválil – jen se to nikdy nedořešilo.
5. **Ověří, že se soubory udržovaly průběžně.** Projde záznam znovu a u každého souboru se ptá, co do něj během práce mělo přibýt – a co chybí, doplní zpětně ve stejné kvalitě, jako by to bylo zapsané v okamžiku, kdy to padlo.
6. **Pošle na projekt čerstvé oči** – někoho, kdo nemá žádný kontext a čte jenom repozitář, jako by se do projektu zaučoval. Ten řekne, jestli je jasné, co dělat dál, kde by musel hádat a co si protiřečí.
7. **Uklidí Git** a ověří výsledek, ne že ho předpokládá.
8. **Je opakovatelný.** Druhý průchod slouží jako ověření – co je zapsané a v pořádku, projde bez zásahu.

## Proč zrovna tenhle

- **Čte surový záznam, ne paměť.** Právě v té části, kterou kompaktace vyhodila, bývají uzavřené dohody, o které jde.
- **Nenechá si utéct zprávy poslané uprostřed běhu.** Ty se ukládají jinak než ostatní a kdo je nezná, tiše o ně přijde – a přitom to bývají důležité dovětky.
- **Zamluvená témata se probírají hned, ne v závěru.** Kdyby se ptal až nakonec, jste už duchem pryč a odpovíte „to je jedno". A u každého kandidáta si napřed ověří, jestli se to mezitím nevyřešilo jinudy, protože falešný nález nutí rozhodovat znovu něco, co už rozhodnuté je.
- **Ptá se věcně.** U visící otázky nabídne skutečné odpovědi, které tehdy byly ve hře, ne obecné „zapsat / odložit".
- **Nic nezůstane jen ve výpisu.** Co by jinak skončilo jako „mimo rozsah úklidu", se s vámi projde a rozhodne – vypsat to a nechat být je nepřijatelné, protože sezení vzápětí zavřete a položky zmizí s ním.
- **Zapisuje i důvody.** Samotný závěr bez zdůvodnění je pro příští práci málo – nebude vědět, proč to tak je, a hraniční případy vyhodnotí špatně.
- **Hlásí i čistý výsledek.** Že se nic nedoplňovalo, se řekne nahlas – a bez komentáře k tomu.
- **Verdikt je jednoznačný.** Buď je zapsané všechno a můžete pokračovat, zkompaktovat i odejít, nebo se jmenuje, co tomu brání. Pracujete-li v odděleném adresáři větve, řekne navíc rovnou, že větev jde bez obav sloučit – ale sám nic neslučuje ani nepřipravuje.

## Jak se to používá

```
/cleanup        # vytěží sezení, kontrola se drží dnešní práce
/cleanup full   # závěrečná kontrola projde celou dokumentaci
```

## Ukázka výstupu

```
## Úklid dokončen

**Zapsáno ze session**
- 9 položek doplněno / 2 přepsány / 1 přesunuta

**Zamluvená témata**
- 3 probrána: 1 rozhodnuto, 1 do todo, 1 bezpředmětné

**Fresh-reader**
- z dokumentace jde navázat; 2 nálezy opraveny (rozbitý odkaz, počet v tabulce)

**Git**
- Pracovní strom: čistý · Commity: 4, push: ano
```

## Co nedělá

- **Neopakuje audit konzistence.** Ptá se na jinou věc – *dá se na dnešní práci navázat?* – a rozpory hledá jen v tom, co dnes přibylo.
- **Nespouští testy, linter ani build** a nedělá obecnou revizi souborů nad rámec toho, co z konverzace vzešlo.
- **Nezakládá potichu chybějící soubory.** Vypíše, které chybí, a nabídne `/project`.
- **Nesloučí větev.** Řekne, že to jde bez rizika; kdy se to stane, je na vás.

## Jak si ho nainstalovat

Nechte to na Claudovi. Otevřete si Claude Code a napište mu:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/cleanup a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.

Skill předpokládá, že má projekt ustálenou dokumentační strukturu – ví, co patří do instrukcí, co mezi rozhodnutí, co mezi odložené věci. **Řekněte Claudovi, ať to přizpůsobí tomu, jak máte soubory uspořádané vy**; sada, kterou používám já, je v tomhle repozitáři popsaná jen odkazem do soukromých standardů.


**Nebo celou sadu naráz.** Chcete-li místo jednoho skillu rovnou celý životní cyklus, napište mu tohle:

> Jdi na https://github.com/jantichy/claude/tree/main/skills a nainstaluj mi do `~/.claude/skills/` celý životní cyklus: project, discovery, specify, oponent, breakdown, implement, review, consistency, cleanup, attack a release. U každého si přečti README a řekni mi, co k nim potřebuju doplnit.

---

### Požadavky a omezení

Git (bez něj funguje, jen odpadne závěrečný úklid repozitáře). Vytěžení dlouhé konverzace se deleguje na pomocníka, takže u opravdu dlouhého sezení to není nejlevnější běh – zato je to jediný krok, který odolá kompaktaci: co zapíše, přežije ztrátu kontextu.
