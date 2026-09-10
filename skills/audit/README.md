# /audit – audit cizího webu proti vaší vlastní metodice

Zaudituje cizí web v oblasti, kterou zadáte – analytiku, měření, SEO, použitelnost –, a napíše nálezy i podklady pro klienta. Neměří to proti obecným „best practices“ z internetu, ale proti **vaší vlastní znalostní bázi**: postupu auditu a katalogu typických nálezů, které máte sepsané. Sám žádnou odbornou znalost nenese, jen celý audit řídí. Hodí se každému, kdo audity dělá opakovaně a nechce pokaždé znovu vymýšlet, na co se podívat a v jakém pořadí.

## Co umí

- **`/audit analytiky na www.example.com`** – celý audit od převzetí podkladů po hotové výstupy. Je to výchozí režim a jmenuje se `full`. Kdykoliv se dá přerušit a příště navázat tam, kde skončil.
- **`brief`** – jen převezme podklady a vypíše, co má k dispozici, co chybí a co se kvůli tomu nedá ověřit.
- **`audit`** – jen ohledá web a sesbírá nálezy.
- **`report`** – jen sepíše výstupy z hotových nálezů, když je potřeba je přepsat jinak.
- **`update`** – přeběhne dřív auditovaný web znovu a řekne, co klient opravil, co trvá a co přibylo.
- Web opravdu **spustí v prohlížeči**: prochází ho, sleduje, co si posílá po síti, jak se chová před souhlasem se sledováním a po něm, a dělá snímky obrazovky.
- Práci rozdělí několika nezávislým pohledům naráz a **každou námitku pak nechá někoho jiného zkusit vyvrátit** tím, že projde tutéž cestu znovu.
- Vyrobí až tři výstupy podle toho, co zaškrtnete: pracovní seznam nálezů pro vás, dokument pro klienta a rozpad na úkoly podle toho, kdo je má provést.

## Proč zrovna tenhle

- **Měří proti vašemu know-how, ne proti obecným radám.** Katalog toho, co se na cizích webech typicky najde, si píšete vy – skill ho jen používá a po auditu nabídne, že do něj doplní, co se našlo nového.
- **Nález, který neobstojí při druhém průchodu, se vám vůbec neukáže.** Poslat klientovi problém, který neexistuje, stojí důvěru celé zakázky.
- **U každého nálezu je adresa, čas a konkrétní pozorování**, takže se dá reprodukovat před klientovým vývojářem, ne jen tvrdit.
- **Má napsáno, kde končí.** Na cizím produkčním webu je rozdíl mezi „prohlédnu si košík“ a „odešlu objednávku“; to druhé se nikdy nestane bez vašeho výslovného odkliknutí.
- **Řekne, co neověřil.** Chybějící přístup do systému není důvod audit neudělat, ale je důvod to mít napsané.

## Jak se to používá

Postavte se do složky toho klienta a napište:

> /audit analytiky na www.example.com

Skill se doptá na podklady a přístupy, projde web, ukáže nálezy a zeptá se, které výstupy má sepsat.

## Ukázka výstupu

```
### Konverze se hlásí ve špatný okamžik

- **závažnost:** kritická (škodí to teď)
- **dopad:** fiktivní tržby v analytice a falešné konverze v reklamě; systém
  se učí na signálu, který nemá vztah ke skutečným objednávkám
- **doložení:** /kosik, 14:03, purchase se odesílá při zobrazení stránky
- **stav ověření:** potvrzeno
- **co s tím:** přesunout na potvrzení platby
- **majitel:** vývojář e-shopu
```

## Co nedělá

- **Neopravuje, co našel.** Nesahá na klientovo nastavení, kód ani účty – jen čte.
- **Není bezpečnostní test.** Nezkouší zranitelnosti a nedělá nic, co by web mohlo shodit.
- **Neprověřuje vaši vlastní práci** v repozitáři; na to jsou jiné nástroje.
- **Nedělá odbornou znalost za vás.** Bez sepsané metodiky pro danou oblast pojede jen v omezené hloubce a řekne vám to.

## Jak si ho nainstalovat

> Jdi na https://github.com/jantichy/claude/tree/main/skills/audit
> a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.

**Sám o sobě nestačí.** Skill je jen dirigent – odbornou část si musíte přinést: pro každou oblast, kterou chcete auditovat, potřebujete vlastní sepsaný postup auditu a katalog typických nálezů. Skill je hledá v `~/Dev/context/<oblast>/`. Bez nich se rozjede jen v omezeném režimu proti obecnému standardu a upozorní vás na to.

---

### Požadavky a omezení

- macOS, Linux i Windows – skill sám nic neinstaluje.
- Pro průchod webem je potřeba plugin **chrome-devtools-mcp** a nainstalovaný Chrome. Bez něj audit poběží jen nad dodanými podklady a řekne, co se tím neověřilo.
- Vlastní znalostní báze v `~/Dev/context/` – viz výš. Cestu lze změnit úpravou skillu.
- Přístupy do klientových systémů jsou volitelné; bez nich se část nálezů nedá ověřit a skill to vypíše.
- Běží proti veřejně dostupnému webu. Web za přihlášením vyžaduje, abyste přihlášení zařídili sami.
