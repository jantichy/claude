# Dokumenty zadání

Šablony a pravidla psaní pro dokumenty, které vyrábí `/specify`. Průběh – kdy se který píše, co ho spouští, kde jsou schvalovací kontroly – drží `SKILL.md`; tady je jen to, co má vzniknout. Návrh řešení tady není: jeho šablonu drží `~/.claude/skills/architect/documents.md`.

- [Jak se píše](#jak-se-píše) – platí pro všechny dokumenty
- [`docs/requirements.md`](#docsrequirementsmd) – produktová specifikace
- [Scénáře, glosář a ceník](#scénáře-glosář-a-ceník) – tři z *Produktových podkladů*

------

## Jak se píše

Česky, věcně, bez omáčky, podle `~/Dev/context/text/text.md` a `~/Dev/context/text/typography.md`. Konkrétně – „rychlé načítání“ je nic, „LCP pod 2,5 s na 4G“ je požadavek. **Bez placeholderů**; co nevíš, patří do *Otevřených otázek* s tím, kdo to má rozhodnout.

------

## `docs/requirements.md`

Sekci, která pro projekt nedává smysl, vynech – ale **řekni, že jsi ji vynechal a proč**.

```markdown
# <Lidský název> – produktová specifikace

<Jedna věta, co to je. Shodná s popiskem v CLAUDE.md.>

## Proč to děláme
Jaký problém to řeší, čí, a co se stane, když to neuděláme.

## Pro koho to je
Persony. U každé: kdo to je, co od toho čeká, čeho se bojí, co ji odradí.
Sekundární persony odděl a řekni, čím jsou omezené.

## Co to je
Popis produktu ze strany uživatele.

## Hlavní scénáře
Co člověk s produktem reálně dělá, od začátku do konce. Čitelně, jako příběh.
Hlavní scénáře nahoře, okrajové pod čarou – ale popsané.
**Vede-li projekt `scenarios.md`, tahle sekce zaniká** a nahradí ji odkaz na něj.

## User stories
Jako <persona> chci <co>, abych <proč>. Seskupené podle oblastí.

## Varianty a rozhodovací větve
Kde má scénář víc podob, vypiš je taxativně a řekni, čím se mezi nimi volí.
Tohle je nejčastější místo, kde se zadání později rozpadne.

## Omezení
Co návrh nesmí porušit: rozpočet, provozní prostředí, závislosti, které
nejsou přípustné, jazyky, legislativa, termín. Omezení, ne volby řešení.

## Nefunkční požadavky
Výkon, dostupnost, bezpečnost, osobní údaje a GDPR, přístupnost,
lokalizace, provoz a zálohy. Jen to, co má reálné důsledky.

## MVP
Zaškrtávací seznam toho, co musí být v první verzi. Řež agresivně.
Každá položka je ověřitelná – ne „hotová registrace“, ale co konkrétně umí.

## Mimo rozsah
Co vědomě neděláme a proč. Musí být neprázdné.
Sem patří i to, co bylo v návrhu a vyhodilo se – ať to nikdo nevymyslí znovu.

## Jak poznáme, že to funguje
Success metrics. Konkrétní, měřitelné, s cílovou hodnotou a termínem.

## Otevřené otázky
Co ještě není rozhodnuté a co to blokuje.
```

------

## Scénáře, glosář a ceník

Tři ze sedmi *Produktových podkladů*, které projekt vede volitelně – `demand.md`, `competition.md` a `risks.md` píše `/discovery`, `operation.md` až `/evaluate` po nasazení; šablonu tady nemají. Kdy se píšou a podle čeho se pozná, že je projekt vede, říká `SKILL.md`; **co který dokument je a k čemu slouží, drží `~/.claude/STRUCTURE.md`, *Produktové podklady***. Tady je jen tvar a to, co platí při psaní.

**`docs/scenarios.md`** – jeden scénář na tenhle tvar, včetně okrajových a chybových cest:

```markdown
## <Číslo a jméno scénáře>

**Kdo:** <persona z requirements.md>
**Kdy a proč:** <spouštěč – co se stalo, že to člověk dělá>
**Předpoklady:** <co musí platit, aby mohl začít>

1. <krok – co udělá uživatel>
2. <krok – co na to systém>
...

**Konec:** <jak pozná, že je hotovo>
**Kde to může selhat:** <odbočky a chybové cesty, každá s tím, co se stane>
```

**Píše se jako postup, ne jako příběh**, a nešetří se okrajovými cestami – čte to i ten, kdo podle toho testuje nebo píše nápovědu. **Zaniká tím sekce *Hlavní scénáře* v `requirements.md`** a nahradí ji odkaz; v požadavcích zůstává **proč a pro koho**, tady **jak to člověk provede**.

**`docs/glossary.md`** – u každého pojmu český název, název v kódu, význam a **čím se liší od pojmu, se kterým se plete**. To poslední je hlavní obsah, ne doplněk. **Rozšiřuje se ještě při návrhu řešení** – entita, která v něm dostane jméno, ho má mít i tady.

**`docs/pricing.md`** – každá věta v něm je funkce, kterou pak někdo musí naprogramovat, takže **každý tarif i limit patří zároveň do *MVP*, nebo do *Mimo rozsah***. Zůstane-li jen tady, nikdo ho nepostaví.
