# /evaluate – co provoz říká o hotové věci

> **Součást životního cyklu projektu.** Tenhle skill patří do ucelené sady skillů, které vedou práci od založení projektu až po nasazení. Jedny tvoří, druhé se starají o to, co už vzniklo – a žádný nedělá práci toho vedle:
>
> **Osa** [`/project`](../project/README.md) → [`/discovery`](../discovery/README.md) → [`/specify`](../specify/README.md) → [`/architect`](../architect/README.md) → [`/breakdown`](../breakdown/README.md) → [`/implement`](../implement/README.md) → [`/release`](../release/README.md) → **`/evaluate`**
>
> **Kontroly** [`/oponent`](../oponent/README.md) · `/consolidate` · [`/review`](../review/README.md) · [`/consistency`](../consistency/README.md) · [`/attack`](../attack/README.md) · [`/cleanup`](../cleanup/README.md) · [`/merge`](../merge/README.md) – stojí v mezerách mezi kroky osy, některé z nich ve víc mezerách
>
> Projít se nemusí celý – u drobné změny odpadá zadání i plán, u projektu bez kódu nasazení.

Nasadit a jít dál je nejběžnější konec práce. Za pár týdnů nikdo neví, jestli tu věc někdo používá, kde lidé odpadli, ani že si dvakrát napsali o totéž – a nová funkce se plánuje z hlavy místo z toho, co provoz ukázal. Tenhle skill sebere čísla ze zdrojů, které projekt doopravdy má, u každého poznatku zapíše, odkud se to ví, a **nepustí vás dřív, než se o každém rozhodne**. Hodí se každému, kdo něco nasadil a nemá na to analytické oddělení.

## Co umí

1. **Odpoví na šest otázek**, na které se po nasazení nikdo neptá: používá se to, kde to lidé nedokončili, co si vyžádali, co jim systém odmítl, co z rizik se projevilo a co nepoužil nikdo.
2. **Vezme zdroje, které máte** – analytiku, vlastní databázi, logy, maily a tikety, vaše vlastní pozorování – a u každého poznatku napíše, odkud se ví a jak se to dá přepočítat. Nemíchá tím „naměřili jsme“ a „mám dojem“.
3. **Najde i to, co nespadlo.** Odmítnutá akce, vypršelý limit, zrušení, které systém nedovolil – to nejsou chyby, takže o nich nikdo neví, a přitom je to nejpřesnější seznam míst, kde návrh nesouhlasí se životem.
4. **Nedovolí skončit u čísel.** U každého poznatku padne rozhodnutí: stane se z něj úkol, nápad na později, nebo vědomé „tohle dělat nebudeme“ i s důvodem.
5. **Vede historii, ne jednorázový report.** Každý další běh přidá nové období nad starší a čísla stará nechá stát, takže je vidět trend.
6. **Zjistí-li, že se neměří nic, je to výsledek, ne selhání** – napíše, co začít měřit, a nejmenším možným krokem, obvykle jedním dotazem do databáze.
7. **Připomene se sám.** Nasazení si zapíše datum, odkdy má vyhodnocení smysl, a průvodce další prací ho v ten den nabídne.

## Proč zrovna tenhle

- **Ptá se na hodnotu, ne na chyby.** Hlášení chyb vám řekne, že něco spadlo. Tohle řekne, že to nespadlo a stejně to nikdo nepoužívá.
- **Nepředstírá data, která nemáte.** Zdroje bere v pořadí podle toho, kolik si u nich musíte domyslet – čísla z databáze nejsou totéž co dojem z jednoho mailu, a skill to u každého poznatku napíše.
- **Nejsilnější zjištění nechá zkusit vyvrátit někomu jinému.** Kdo nález našel, ten ho hájí, ne prověřuje – a stav v databázi znamená v každé aplikaci něco jiného. Co ověření nepřežije, se do podkladu vůbec nedostane.
- **Poradí si i s rozbitými daty.** Ukáže-li se, že čísla nejsou důvěryhodná, neskončí – oddělí zjištění, která na číslech nestojí (chybějící omezení v databázi, chybějící historie změn), a u zbytku řekne, že se z nich argumentovat nemá.
- **Končí rozhodnutím, ne přehledem.** Bez toho je to další soubor, který nikdo nečte.
- **Zadání nepřepisuje.** Poznatek je podklad, ne rozkaz – co se z něj postaví, rozhodnete vy v dalším kole.
- **Bere v potaz, že se lidé ozývají výběrově.** Kdo napíše, bývá ten nejnaštvanější nebo nejvěrnější; dvě nezávislé žádosti o totéž jsou proto doklad, ne anekdota.

## Jak se to používá

```
/evaluate
```

Zjistí, kdy se nasazovalo a za jaké období se tedy měří, projde zdroje, které projekt má, sebere z nich čísla a citace, ověří je, zapíše do `docs/operation.md` – a pak s vámi projde poznatek po poznatku, dokud každý nemá rozhodnutí. Nejdřív ale řekne, kolik jich je a kolik z nich doopravdy potřebuje vaši odpověď.

## Ukázka výstupu

```
## Provoz vyhodnocený

- Období: 14. 8. – 21. 9. 2026, 38 dní provozu
- Podklad: docs/operation.md – 9 poznatků, 1. běh
- Zdroje: databáze aplikace, logy, výpis z mailu. Analytika není –
  nejde tedy zjistit, kolik lidí odešlo, než se zaregistrovali.

Poznatky
- Vady: 2 – platba spadne a rezervace zůstane rozdělaná (46 % z 323), obojí do todo
- Nová práce: 3 – opakovaná rezervace (2 nezávislé žádosti) do todo, výpis
  odehraných hodin do backlogu, ruční zrušení do 24 h vědomě neděláme
- Zjištění bez akce: 4

Nepotvrzeno
- „Kurt C se nepoužívá“ – čísla šla z jiného období, po přepočtu rozdíl zmizel
```

## Co nedělá

- **Neměří pády po nasazení.** To je věc sledovacího okna, které běží hodiny po vydání; tenhle skill přichází za týdny.
- **Nezavádí měření.** Řekne, co začít měřit; naprogramuje se to pak jako každá jiná práce.
- **Nepřepisuje zadání ani nic neopravuje.** Vyrábí podklad a úkoly, do kódu nesahá.
- **Nenahrazuje rozhovor se zákazníkem.** Čte stopy, které po sobě lidé nechali, a nepředstírá, že je to totéž.

## Jak si ho nainstalovat

Řekněte svému Claudovi tohle:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/evaluate
> a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.

Skill se opírá o tři soubory, které v tom adresáři nejsou: sdílený začátek běhu, pravidlo o tom, kdo rozhoduje o nálezu, a škálu jeho závažnosti. Leží v [`skills/`](../) jako `PREFLIGHT.md`, `FINDINGS.md` a `SEVERITY.md` – vezměte je k tomu, jinak si skill bude stěžovat na chybějící odkazy.

**Nebo celou sadu naráz.** Chcete-li místo jednoho skillu rovnou celý životní cyklus, napište mu tohle:

> Jdi na https://github.com/jantichy/claude/tree/main/skills a nainstaluj mi do `~/.claude/skills/` celý životní cyklus: project, discovery, specify, architect, breakdown, implement, release, evaluate, oponent, review, consistency, attack, cleanup a merge. Z https://github.com/jantichy/claude/tree/main/agents k tomu vezmi i definice typů subagentů do `~/.claude/agents/`. U každého si přečti README a řekni mi, co k nim potřebuju doplnit.

---

### Požadavky a omezení

Nic se neinstaluje. Čte to, co projekt má – databázi, logy, exporty, výpisy –, takže dostupnost zdrojů je celá jeho mez: bez jediného zdroje skončí zjištěním, že se neměří, a návrhem, čím začít. Do analytických a mailových služeb sám nevolá; co je za přihlášením, mu musíte podstrčit jako export nebo výpis. Měří období od posledního nasazení, takže potřebuje vědět, kdy se nasazovalo – z tagu, z historie gitu nebo ze zápisu o vydání.
