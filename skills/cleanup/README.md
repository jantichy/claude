# /cleanup – ať po mně zůstane čisto a jasno

> **Součást životního cyklu projektu.** Tenhle skill patří do ucelené sady skillů, které vedou práci od založení projektu až po vyhodnocení provozu. Jedny tvoří, druhé se starají o to, co už vzniklo – a žádný nedělá práci toho vedle:
>
> **Osa** [`/project`](../project/README.md) → [`/discovery`](../discovery/README.md) → [`/specify`](../specify/README.md) → [`/architect`](../architect/README.md) → [`/breakdown`](../breakdown/README.md) → [`/implement`](../implement/README.md) → [`/release`](../release/README.md) → [`/evaluate`](../evaluate/README.md)
>
> **Kontroly** [`/oponent`](../oponent/README.md) · `/consolidate` · [`/review`](../review/README.md) · [`/consistency`](../consistency/README.md) · [`/attack`](../attack/README.md) · **`/cleanup`** · [`/merge`](../merge/README.md) – stojí v mezerách mezi kroky osy, některé z nich ve víc mezerách
>
> Projít se nemusí celý – u drobné změny odpadá zadání i plán, u projektu bez kódu nasazení i vyhodnocení provozu.

Když je práce u konce a chystáte se sezení opustit nebo nechat zkompaktovat, tíží vás pokaždé totéž: neztratí se něco? Tenhle skill to vyřeší. Přečte si **celý záznam konverzace** – tedy včetně části, kterou už kompaktace z paměti vyhodila –, vytáhne z něj všechno, co se domluvilo, a zapíše to tam, kam to patří. Pak si otočí pohled a hledá druhou věc: co v konverzaci zůstalo viset bez vypořádání.

**Hlavní rozdíl proti ručnímu úklidu je v tom, že si vede evidenci.** Ze záznamu si vytáhne seznam všech míst, kde jste něco napsali, a u každého odškrtne, co se s tím stalo: zapsáno tam a tam, později přebito jiným rozhodnutím, nebo čeká na vaše rozhodnutí. Na konci vám řekne poměr – odškrtnuto 23 z 23. Není to tedy tvrzení „přečetl jsem to celé“, ale číslo, které jde ověřit.

## Co umí

1. **Vytěží konverzaci celou** – i tu část, kterou už kompaktace vyhodila z paměti. Nejdřív si ji očistí od technického balastu: v záznamu je ho devět desetin, takže čtení pak stojí zlomek.
2. **Vede evidenci s odškrtáváním.** Každé místo, kde jste něco napsali, dostane řádek a stav. Nevyplněný řádek znamená nehotový úklid – a to se pozná, protože poměr je v závěru vidět.
3. **Vytáhne ze záznamu osm věcí** – dohody a rozhodnutí (vždy i s důvodem a zavrženými variantami), nová pravidla a konvence, odvedenou práci, vědomě odložené úkoly, postřehy mimo hlavní téma, korekce (platí poslední verze, ne první), nevypořádaná témata a to, co zůstalo rozbité nebo nedodělané.
4. **Dohledá, co propadlo.** Nejčastější ztráta v dlouhé konverzaci není zapomenutý zápis, ale nevypořádané téma: přišla dlouhá odpověď s několika body, vy jste se chytili poloviny a zbytek zůstal bez vypořádání. Nikdo to nezavrhl ani neschválil – jen se to nikdy nedořešilo.
5. **Ověří, že se soubory udržovaly průběžně.** Prochází to z obou stran naráz: od nalezené položky k souboru, kam patří, i od souboru k otázce, co do něj mělo přibýt, i když se o tom nikdo nezmínil. Co chybí, doplní zpětně ve stejné kvalitě, jako by to bylo zapsané v okamžiku, kdy to padlo.
6. **Ptá se i na produktové podklady**, vede-li je projekt – jestli přibyl doklad poptávky, jestli se změnilo, co víme o konkurenci, jestli přibylo riziko, jestli se posunul některý scénář nebo pojem. Jsou to soubory, na které se při běžné práci nesahá, takže tiše zastarávají jako první.
7. **Ptá se na jednu frontu, ne na čtyři.** Všechno, co potřebuje vaše rozhodnutí, projde jedním seznamem seřazeným podle váhy – ať je to nevypořádané téma, nejasné zařazení zápisu, nebo starší dluh, na který u toho narazil.
8. **Uklidí Git** a ověří výsledek, ne že ho předpokládá.

## Proč zrovna tenhle

- **Úplnost se měří, ne tvrdí.** Poměr odškrtnutých míst je číslo, které jde ověřit – a nevyplněný řádek nejde vydat za hotovo.
- **Čte záznam, ne paměť.** Právě v té části, kterou kompaktace vyhodila, bývají uzavřené dohody, o které jde.
- **Nenechá si utéct zprávy poslané uprostřed běhu.** Ty se ukládají jinak než ostatní a kdo je nezná, tiše o ně přijde – a přitom to bývají důležité dovětky.
- **Nevypořádaná témata se probírají hned, ne v závěru.** Kdyby se ptal až nakonec, jste už duchem pryč a odpovíte „to je jedno“. A u každého kandidáta si napřed ověří, jestli se to mezitím nevyřešilo jinudy, protože falešný nález nutí rozhodovat znovu něco, co už rozhodnuté je.
- **Ptá se věcně.** U nevypořádané otázky nabídne skutečné odpovědi, které tehdy byly ve hře, ne obecné „zapsat / odložit“.
- **Nic nezůstane jen ve výpisu.** Co by jinak skončilo jako „mimo rozsah úklidu“, se vyřídí – vypsat to a nechat být je nepřijatelné, protože sezení vzápětí zavřete a položky zmizí s ním.
- **Co je zjevné, opraví rovnou a bez ptaní.** Hotový úkol visící mezi nedodělanými nebo přejmenování, které minulo dvě místa, prostě opraví a vypíše jednou řádkou. Rozhodovat nechává vás jen tam, kde je z čeho vybírat.
- **Zapisuje i důvody.** Samotný závěr bez zdůvodnění je pro příští práci málo – nebude vědět, proč to tak je, a hraniční případy vyhodnotí špatně.
- **Přizná, co nepřečetl.** Do trvalého záznamu o úklidu jde i to, co zůstalo mimo – takže příští sezení nedostane řádek, který se čte jako „uklizeno“, ačkoliv část záznamu nikdo neviděl.
- **Hlásí i čistý výsledek.** Že se nic nedoplňovalo, se řekne nahlas – a bez komentáře k tomu.
- **Verdikt je jednoznačný.** Buď je zapsané všechno a můžete pokračovat, zkompaktovat i odejít, nebo se jmenuje, co tomu brání. Hned potom se zeptá, co dál: pokračovat v práci, a stojíte-li na jiné než hlavní větvi, i přimergovat ji – to pak vyřídí [`/merge`](../merge/README.md).

## Jak se to používá

```
/cleanup        # vytěží sezení, ve kterém stojíte
```

## Ukázka výstupu

```
## Úklid dokončen

**Pokrytí:** kotvy 23/23 odškrtnuto · přečteno 312 kB z 3,0 MB záznamu

**Zapsáno** – 12 zápisů
- decisions.md – rozhodnutí o řezu skillu i se dvěma zamítnutými variantami
- todo.md – tři odložené body s celým kontextem

**Fronta rozhodnutí** – 4 položky: 2 rozhodnuty, 1 do todo, 1 bezpředmětná

**Mimo rozsah úklidu** – hotový úkol visící mezi nedodělanými (přesunut)

**Kontrola odkazů:** 0 · dvě mrtvé kotvy opraveny
**Kontrakt příkazů:** test → 0
**Git:** 4 commity · pushnuto · cizí rozdělaná práce: žádná

**Meze běhu:** 68 bloků vnitřního přemýšlení (v záznamu jsou prázdné), 41 výpisů
ze čtení souborů (obsah je v souborech samotných)
```

## Co nedělá

- **Neposuzuje kvalitu dokumentace.** Ptá se, jestli je v souborech všechno z konverzace – ne jestli se v projektu někdo vyzná. Na to je [`/consistency`](../consistency/README.md), který běží o krok dřív.
- **Nedělá revizi projektu.** Testy, linter ani build nepouští proto, aby prověřil cizí práci. To, co sám zapsal, si naopak ověřit musí – pustí na to tu kontrolu projektu, která na zapsané soubory doopravdy sahá, a její výsledek vypíše.
- **Nezakládá potichu chybějící soubory.** Vypíše, které chybí, a nabídne `/project`.
- **Nemerguje větev sám od sebe.** Nabídne to a vyberete-li to, předá práci skillu [`/merge`](../merge/README.md).

## Jak si ho nainstalovat

Nechte to na Claudovi. Otevřete si Claude Code a napište mu:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/cleanup a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.

**Nabídku merge na konci provádí skill [`/merge`](../merge/README.md)** – nainstalujte si ho k tomu, jinak se nabídne, ale nebude ho kdo vyřídit. Pracujete-li v uspořádání, kde má každá větev vlastní adresář, vezměte k tomu ještě [`WORKTREE.md`](../../WORKTREE.md) do `~/.claude/`.

Skill předpokládá, že má projekt ustálenou dokumentační strukturu – ví, co patří do instrukcí, co mezi rozhodnutí, co mezi odložené věci. **Řekněte Claudovi, ať to přizpůsobí tomu, jak máte soubory uspořádané vy**; sada, kterou používám já, je v tomhle repozitáři popsaná jen odkazem do soukromých standardů.

**Nebo celou sadu naráz.** Chcete-li místo jednoho skillu rovnou celý životní cyklus, napište mu tohle:

> Jdi na https://github.com/jantichy/claude/tree/main/skills a nainstaluj mi do `~/.claude/skills/` celý životní cyklus: project, discovery, specify, architect, breakdown, implement, release, evaluate, oponent, review, consistency, attack, cleanup a merge. Z https://github.com/jantichy/claude/tree/main/agents k tomu vezmi i definice typů subagentů do `~/.claude/agents/`. U každého si přečti README a řekni mi, co k nim potřebuju doplnit.

---

### Požadavky a omezení

**Python 3** na očištění záznamu a na kontrolu odkazů – bez něj skill nemá čím měřit pokrytí ani hledat mrtvé odkazy, takže z něj zbude jen ruční vytěžení.

**Git** – bez něj to proběhne, ale odpadne závěrečný úklid repozitáře i porovnání, co se během sezení skutečně změnilo. Sezení se zapíše, ověřitelná stopa po něm nezůstane.

**Z vnitřního přemýšlení a ze snímků obrazovky nepřečte nic.** U přemýšlení to není volba: v záznamu je uložené prázdné, takže tam ten obsah není. Kde na něm něco viselo, přizná to jako mez místo dopočítání. Výpisy ze čtení souborů taky nečte – jejich obsah je v souborech samotných, kde je navíc aktuální.
