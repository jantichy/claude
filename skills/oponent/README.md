# /oponent – oponentura na to, co nejde otestovat

> **Součást životního cyklu projektu.** Tenhle skill patří do ucelené sady skillů, které vedou práci od založení projektu až po vyhodnocení provozu. Jedny tvoří, druhé se starají o to, co už vzniklo, třetími každá session začíná a končí – a žádný nedělá práci toho vedle:
>
> **Osa** [`/project`](../project/README.md) → [`/discovery`](../discovery/README.md) → [`/specify`](../specify/README.md) → [`/architect`](../architect/README.md) → [`/breakdown`](../breakdown/README.md) → [`/implement`](../implement/README.md) → [`/release`](../release/README.md) → [`/evaluate`](../evaluate/README.md)
>
> **Kontroly** **`/oponent`** · [`/consolidate`](../consolidate/README.md) · [`/review`](../review/README.md) · [`/consistency`](../consistency/README.md) · [`/attack`](../attack/README.md)
>
> **Session** [`/next`](../next/README.md) · [`/continue`](../continue/README.md) · [`/end`](../end/README.md) · [`/merge`](../merge/README.md) · [`/break`](../break/README.md)
>
> Projít se nemusí celý – u drobné změny odpadá zadání i plán, u projektu bez kódu nasazení i vyhodnocení provozu.

Máte hotovou strategii, pozicování, produktovou specifikaci, cenotvorbu, datový model nebo koncepci – dokument, na kterém jste s Claudem dlouho pracovali. **Právě proto na něj ani jeden z vás nemá nezávislý pohled:** spoluautor nevidí, co v dokumentu chybí, protože to má v hlavě, a nevidí, co je slabé, protože si to sám odsouhlasil. Tenhle skill pošle na dokument několik oponentů, kteří **nevědí nic z vaší konverzace** a čtou jenom soubory, každého z jiného hlediska. Jejich námitky pak projde s vámi jednu po druhé.

## Co umí

1. **Vybere hlediska z katalogu sedmnácti** – a vybírá je podle **vlastnosti dokumentu**, ne podle jeho typu: „slibuje výsledek“, „sbírají se údaje o lidech“, „stojí to na cizí službě“. Výběr vám předloží ke schválení dřív, než kdokoliv začne pracovat.
2. **Katalog má dvě poloviny.** *Metody* říkají, jak se dívat – vnitřní rozpor, co chybí, nevyslovené předpoklady, pohled zpětně z budoucího selhání, alternativy, měřitelnost cíle, zneužití, nevratnost, čtenář bez kontextu. *Domény* říkají, na co se dívat – ekonomika provozu, osobní údaje, závazky vůči druhé straně, data a proveditelnost, nepřítomní dotčení, závislosti, konkurence, cílová skupina.
3. **Každou závažnou námitku pošle ověřit** někomu dalšímu, kdo má jediný úkol: **vyvrátit ji**. Co ověření nepřežije, se vám vůbec nezobrazí.
4. **Projde s vámi nálezy jeden po druhém**, od nejzávažnějšího, a u každého nabídne konkrétní varianty řešení – ne jen „opravit“. Drobnosti nakonec schválíte jedním kliknutím a zapracuje se to až po poslední otázce.
5. **Zapíše i to, co jste zamítli**, i s důvodem, aby to příští oponentura nenašla znovu jako nový nález.
6. **Umí navázat na přerušený běh.** Ověřený seznam nálezů se ukládá na disk, takže se nejdražší část práce neplatí dvakrát.
7. **Je určený k opakování.** Nález, který se vrátí, znamená, že se neopravil, jen přeformuloval – a skill to řekne výslovně.
8. **Nedojde-li seznam do konce, nabídne přerušení.** Roste-li konverzace do velikosti, ve které už se pracuje pomalu a nepřesně, řekne to a zbývající položky i s tím, co je u nich potřeba rozhodnout, uloží do seznamu úkolů – další session pak pokračuje přesně tam, kde jste skončili, a s čistou hlavou.

## Proč zrovna tenhle

- **Nejdřív se zeptá, pak pracuje.** Na všechno, co musíte rozhodnout vy, se zeptá v jednom zátahu, jednu otázku za druhou, a teprve pak všechno zapracuje sám – mezitím od toho můžete odejít. Na co přijde až při práci, nechá na další kolo otázek.
- **Oponenti nemají váš kontext.** To není omezení, ale celý smysl: nezávislost se nedá nasimulovat u někoho, kdo u vzniku dokumentu byl.
- **Vždycky dostanou i seznam toho, co jste vědomě zamítli** – i s důvody. Bez toho by první běh přinesl námitky, které umíte vyvrátit z hlavy, a druhý byste už nepustili.
- **Rozdílná hlediska, ne víc stejných kritiků.** Redundantní oponenti najdou tolikrát totéž, kolik jich pustíte.
- **Metoda se nikdy nepouští bez domény.** „Podívej se na to kriticky“ je slepé; „udělej pohled zpětně z budoucího selhání na ten cenový model“ je zadání.
- **Ověřovatel je záměrně v jiné situaci než oponent.** Oponent, který nic nenajde, vypadá jako selhání běhu; ověřovatel, který nález vyvrátí, odvedl práci. Ta asymetrie je celý mechanismus.
- **Každý oponent vykáže, kterými částmi předmětu opravdu prošel.** Posudek, který přečetl třetinu, vypadá stejně věrohodně jako úplný – nálezy v něm jsou pravé, chybí jen ty ostatní. Skill proto poměr měří a hledisko s nejmenším pokrytím jmenuje.
- **Filtrovat nálezy nesmí spoluautor.** Kdyby se falešné vyřazovaly až v diskuzi, dělal by to přesně ten člověk, jehož slepotu má skill obcházet.
- **Řekne, které hledisko vědomě nevzal a proč.** Nevybrané hledisko totiž nevrátí nula nálezů, ale neexistenci – a ta by žádným počítadlem neprošla.
- **Nechválí.** Věci, které jsou v pořádku, se nevypisují, a závěr nikdy nezní „dokument je v dobrém stavu“ – to není verdikt oponenta, ale autora.

## Jak se to používá

```
/oponent docs/requirements.md
/oponent pozicování
/oponent                       # nabídne, co našel
```

## Ukázka výstupu

```
[3/11] 🔴 Ceník nemá odpověď na souběh dvou slev · 2 oponenti nezávisle

Ceník v sekci „Slevy" slibuje, že se sleva uplatní automaticky, ale neříká,
co se stane, když má zákazník nárok na dvě zároveň. U tří dnes existujících
slev jsou to tři možné kombinace a systém vybere podle pořadí v databázi,
tedy nahodile – reklamaci pak nejde rozsoudit ani jedním směrem.

Varianty řešení:
A) Slevy se nesčítají, uplatní se nejvyšší – jednoduché, zákazník neztrácí
B) Slevy se sčítají do stropu 40 % – vstřícnější, ale nutné hlídat marži

Doporučuji A: u tří slev je souběh okrajový a pravidlo se vysvětlí jednou větou.
```

## Co nedělá

- **Není to kontrola kódu** ani kontrola proti předpisu – zadání nebo doménovým znalostem. Na to je `/review`; oponent se opírá o argument, ne o pravidlo, a proto funguje i tam, kde žádný předpis není.
- **Není to audit vnitřní konzistence.** Ptá se „je to dobře vymyšlené?“, ne „sedí to na sebe?“ – na druhou otázku je `/consistency`.
- **Nic sám nemění.** Změny až po schválení jednotlivých námitek.
- **Nemá cenu nad torzem.** Posudek na kostru vygeneruje hlavně nálezy „chybí obsah“, což víte i bez něj – skill se na to zeptá předem.

## Jak si ho nainstalovat

Je to snadné, zadejte do svého Claude Code tenhle prompt:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/oponent a nainstaluj mi ten skill k sobě do `~/.claude/skills/` – celý adresář i s podadresáři. Stáhni k němu z téhož repozitáře na odpovídající místo pod `~/.claude/` i sdílené soubory ze `skills/` a `standards/`, na které jeho soubory odkazují, a definice typů subagentů, které pouští, z `agents/` do `~/.claude/agents/`. Co už u sebe mám, nepřepisuj a ukaž mi rozdíl. Odkazuje-li na jiný skill, zeptej se mě, jestli ho chci taky. Odkazy na soubory, které v repozitáři nejsou, mi vypiš a u každého se zeptej, jestli ho napojit na můj vlastní soubor, nebo odkaz smazat. Zeptej se mě, jak mám uspořádanou dokumentaci projektu – kam zapisuju rozhodnutí a odložené věci –, a odkazy ve skillu tomu přizpůsob. Nakonec mi řekni, co musím doplnit sám.

**Nebo celou sadu naráz.** Chcete-li místo jednoho skillu rovnou celý životní cyklus, zadejte do svého Claude Code tenhle prompt:

> Jdi na https://github.com/jantichy/claude/tree/main/skills a nainstaluj mi do `~/.claude/skills/` celý životní cyklus: project, discovery, specify, architect, breakdown, implement, release, evaluate, oponent, consolidate, review, consistency a attack, a k nim skilly, kterými session začíná a končí: next, continue, end, merge a break. Každý z nich nainstaluj přesně podle promptu v sekci „Jak si ho nainstalovat“ v jeho README; na skilly z téhle sady se mě při tom neptej, beru je všechny.

---

### Požadavky a omezení

Běží nad textem, ne nad kódem. Rozumný rozsah předmětu je zhruba do pěti dokumentů; nad tím se posudek rozmělní a skill se zeptá, co je jádro. Panel i ověřování běží na nejsilnějším modelu – je to **z celé sady nejdražší běh**, a proto se u drobné změny přeskakuje. Část hledisek si podle potřeby dohledává informace na webu.
