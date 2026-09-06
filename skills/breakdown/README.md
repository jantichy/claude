# /breakdown – ze schváleného zadání implementační plán

> **Součást životního cyklu projektu.** Tenhle skill patří do ucelené sady deseti skillů, které vedou práci od založení projektu až po nasazení. Každý má svůj krok a žádný nedělá práci toho vedle:
>
> [`/project`](../project/README.md) → [`/specify`](../specify/README.md) → [`/oponent`](../oponent/README.md) → **`/breakdown`** → [`/implement`](../implement/README.md) → [`/review`](../review/README.md) → [`/consistency`](../consistency/README.md) → [`/cleanup`](../cleanup/README.md) → [`/attack`](../attack/README.md) → [`/release`](../release/README.md)
>
> Projít se nemusí celá – u drobné změny odpadá zadání i plán, u projektu bez kódu nasazení.

Udělá ze zadání seřazený seznam úkolů velikosti pár minut. U každého konkrétní soubory, hotový kód testu, příkaz, kterým se ověří, že je úkol hotový, a commit. Plán je psaný pro někoho, kdo projekt vůbec nezná – a to je celý smysl: dokud práce nemá takhle nařezanou podobu, není nad čím se domluvit a chyba v rozvrhu se pozná až u posledního úkolu. Plán se předkládá ke schválení; je to poslední levné místo, kde se dá otočit.

## Co umí

1. **Rozpadne zadání na úkoly**, které mají konkrétní soubory, testy a jednoznačné kritérium hotovosti.
2. **Plánuje jen první použitelnou verzi.** Zadání popisuje celou věc, plán jen to, co se staví teď – a co pokrývá, si nechá potvrdit.
3. **Rozdělí příliš velkou práci na víc plánů**, z nichž každý sám o sobě dá funkční, otestovatelný výsledek.
4. **Neplánuje naslepo.** Chybí-li zadání, pošle vás nejdřív napsat ho a skončí.
5. **Umí navázat na existující plán** – doplnit další fázi, dopsat chybějící část, nebo promítnout změnu zadání jen do nehotových úkolů. Nikdy nepřepíše to, co už je v kódu.
6. **Zkontroluje se sám** – že plán pokrývá všechno, co pokrýt měl, že nedělá nic navíc, že se v pozdějších úkolech nepoužívají jiné názvy než v dřívějších a že se zadání během psaní nezměnilo pod rukama.
7. **Ověří pokrytí scénářů testem**, ne pokrytí řádků.

## Proč zrovna tenhle

- **Kritérium hotovosti musí být rozsouditelné.** Ne „funguje přihlášení", ale zaškrtávací seznam a u kódu příkaz, který dá jednoznačnou odpověď. Kritérium, které neumí rozsoudit stroj ani jednoznačně člověk, je nedopsaný úkol.
- **Testy se píší dřív, než existuje kód** – plán je jediné místo, kde si je člověk přečte nezaujatě. Potom už bude posuzovat, jestli procházejí, ne jestli měří správnou věc.
- **Na plánování se nešetří.** Špatně nařezaný úkol rozsévá chyby do všeho, co po něm přijde, takže sem jde nejsilnější nastavení, i když samo sepsání vypadá mechanicky.
- **Nedovolí „doplnit později".** Plán s nedořečeným místem se do realizace nepustí.
- **Nepokračuje do realizace sám.** Konec je předání ke schválení, ne rozjetá práce.

## Jak se to používá

```
/breakdown
```

Skill si najde schválené zadání, nechá si potvrdit rozsah, sepíše plán, zkontroluje ho a předá vám ho ke čtení.

## Ukázka výstupu

```
## Plán hotový

**Soubor:** docs/plan.md – 14 úkolů
**Spec:** architecture.md
**Rozsah:** MVP body 1–6
**Pokrytí scénářů:** 9 z 9 scénářů má test

**Nepokryto vědomě**
- export do PDF zůstává na další fázi

**Další krok:** /implement
```

## Co nedělá

- **Neimplementuje** – ani první úkol na ukázku.
- **Nepíše zadání.** Když chybí, řekne to a pošle vás ho napsat.
- **Neřeže rozsah sám.** Co je v první verzi, rozhodlo zadání; tady se to jen respektuje.

## Jak si ho nainstalovat

Nechte to na Claudovi. Otevřete si Claude Code a napište mu:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/breakdown a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.

Skill je **obálka nad pluginem [superpowers](https://github.com/obra/superpowers)** – ten potřebujete mít nainstalovaný, klidně o to Clauda požádejte zároveň. Sám k němu přidává to, co plugin neřeší: vynucené umístění plánu, odmítnutí spustit se bez schváleného zadání, kontrolu pokrytí a bezpečné navázání na rozdělaný plán.


**Nebo celou sadu naráz.** Chcete-li místo jednoho skillu rovnou celý životní cyklus, napište mu tohle:

> Jdi na https://github.com/jantichy/claude/tree/main/skills a nainstaluj mi do `~/.claude/skills/` celý životní cyklus: project, specify, oponent, breakdown, implement, review, consistency, cleanup, attack a release. U každého si přečti README a řekni mi, co k nim potřebuju doplnit.

---

### Požadavky a omezení

Plugin superpowers. Projekt, ve kterém se spouští kód, potřebuje mít v instrukcích zapsané, čím se u něj pouštějí testy, typová kontrola a linter – bez toho nemá plán co napsat do kroku ověření a skill to řekne.
