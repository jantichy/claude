# /oponent – oponentura na to, co nejde otestovat

> **Součást životního cyklu projektu.** Tenhle skill patří do ucelené sady skillů, které vedou práci od založení projektu až po nasazení. Každý má svůj krok a žádný nedělá práci toho vedle:
>
> [`/project`](../project/README.md) → [`/discovery`](../discovery/README.md) → [`/specify`](../specify/README.md) → **`/oponent`** → [`/breakdown`](../breakdown/README.md) → [`/implement`](../implement/README.md) → [`/review`](../review/README.md) → [`/consistency`](../consistency/README.md) → [`/cleanup`](../cleanup/README.md) → [`/attack`](../attack/README.md) → [`/release`](../release/README.md)
>
> Projít se nemusí celý – u drobné změny odpadá zadání i plán, u projektu bez kódu nasazení.

Máte hotovou strategii, pozicování, produktovou specifikaci, cenotvorbu, datový model nebo koncepci – dokument, na kterém jste s Claudem dlouho pracovali. **Právě proto na něj ani jeden z vás nemá nezávislý pohled:** spoluautor nevidí, co v dokumentu chybí, protože to má v hlavě, a nevidí, co je slabé, protože si to sám odsouhlasil. Tenhle skill pošle na dokument několik oponentů, kteří **nevědí nic z vaší konverzace** a čtou jenom soubory, každého z jiného hlediska. Jejich námitky pak projde s vámi jednu po druhé.

## Co umí

1. **Vybere hlediska z katalogu sedmnácti** – a vybírá je podle **vlastnosti dokumentu**, ne podle jeho typu: „slibuje výsledek“, „sbírají se údaje o lidech“, „stojí to na cizí službě“. Výběr vám předloží ke schválení dřív, než kdokoliv začne pracovat.
2. **Katalog má dvě poloviny.** *Metody* říkají, jak se dívat – vnitřní rozpor, co chybí, nevyslovené předpoklady, pohled zpětně z budoucího selhání, alternativy, měřitelnost cíle, zneužití, nevratnost, čtenář bez kontextu. *Domény* říkají, na co se dívat – ekonomika provozu, osobní údaje, závazky vůči druhé straně, data a proveditelnost, nepřítomní dotčení, závislosti, konkurence, cílová skupina.
3. **Každou závažnou námitku pošle ověřit** někomu dalšímu, kdo má jediný úkol: **vyvrátit ji**. Co ověření nepřežije, se vám vůbec nezobrazí.
4. **Projde s vámi nálezy jeden po druhém**, od nejzávažnějšího, a u každého nabídne konkrétní varianty řešení – ne jen „opravit“.
5. **Zapíše i to, co jste zamítli**, i s důvodem, aby to příští oponentura nenašla znovu jako nový nález.
6. **Umí navázat na přerušený běh.** Ověřený seznam nálezů se ukládá na disk, takže se nejdražší část práce neplatí dvakrát.
7. **Je určený k opakování.** Nález, který se vrátí, znamená, že se neopravil, jen přeformuloval – a skill to řekne výslovně.

## Proč zrovna tenhle

- **Oponenti nemají váš kontext.** To není omezení, ale celý smysl: nezávislost se nedá nasimulovat u někoho, kdo u vzniku dokumentu byl.
- **Vždycky dostanou i seznam toho, co jste vědomě zamítli** – i s důvody. Bez toho by první běh přinesl námitky, které umíte vyvrátit z hlavy, a druhý byste už nepustili.
- **Rozdílná hlediska, ne víc stejných kritiků.** Redundantní oponenti najdou tolikrát totéž, kolik jich pustíte.
- **Metoda se nikdy nepouští bez domény.** „Podívej se na to kriticky“ je slepé; „udělej pohled zpětně z budoucího selhání na ten cenový model“ je zadání.
- **Ověřovatel je záměrně v jiné situaci než oponent.** Oponent, který nic nenajde, vypadá jako selhání běhu; ověřovatel, který nález vyvrátí, odvedl práci. Ta asymetrie je celý mechanismus.
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
[3/11] 🔴 CENÍK NEMÁ ODPOVĚĎ NA SOUBĚH DVOU SLEV
Našel: 2 oponenti nezávisle

Kde: cenik.md, sekce „Slevy", věta „Sleva se uplatní automaticky."
Co: Není určeno, co se stane, když má zákazník nárok na dvě slevy zároveň.
Proč to vadí: U tří dnes existujících slev jsou tři možné kombinace; systém
  vybere podle pořadí v databázi, tedy nahodile, a reklamaci nelze rozsoudit.

Varianty řešení:
A) Slevy se nesčítají, uplatní se nejvyšší – jednoduché, zákazník neztrácí
B) Slevy se sčítají do stropu 40 % – vstřícnější, ale nutné hlídat marži
C) Nechat být – u tří slev je to okrajové
```

## Co nedělá

- **Není to kontrola kódu** ani kontrola proti standardům. Na to je `/review`.
- **Není to audit vnitřní konzistence.** Ptá se „je to dobře vymyšlené?“, ne „sedí to na sebe?“ – na druhou otázku je `/consistency`.
- **Nic sám nemění.** Změny až po schválení jednotlivých námitek.
- **Nemá cenu nad torzem.** Posudek na kostru vygeneruje hlavně nálezy „chybí obsah“, což víte i bez něj – skill se na to zeptá předem.

## Jak si ho nainstalovat

Nechte to na Claudovi. Otevřete si Claude Code a napište mu:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/oponent a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.

Skill se odkazuje na strukturu projektové dokumentace, kterou používám já – kam se zapisují rozhodnutí, odložené věci a záznamy o průchodech. **Řekněte Claudovi, ať to přizpůsobí tomu, jak máte dokumentaci uspořádanou vy**, nebo ty odkazy smaže; jádro na nich nestojí.


**Nebo celou sadu naráz.** Chcete-li místo jednoho skillu rovnou celý životní cyklus, napište mu tohle:

> Jdi na https://github.com/jantichy/claude/tree/main/skills a nainstaluj mi do `~/.claude/skills/` celý životní cyklus: project, discovery, specify, oponent, breakdown, implement, review, consistency, cleanup, attack a release. U každého si přečti README a řekni mi, co k nim potřebuju doplnit.

---

### Požadavky a omezení

Běží nad textem, ne nad kódem. Rozumný rozsah předmětu je zhruba do pěti dokumentů; nad tím se posudek rozmělní a skill se zeptá, co je jádro. Panel i ověřování běží na nejsilnějším modelu – je to **z celé sady nejdražší běh**, a proto se u drobné změny přeskakuje. Část hledisek si podle potřeby dohledává informace na webu.
