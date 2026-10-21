# /project – projekt nastavený na pár kliknutí

> **Součást životního cyklu projektu.** Tenhle skill patří do ucelené sady skillů, které vedou práci od založení projektu až po vyhodnocení provozu. Jedny tvoří, druhé se starají o to, co už vzniklo, třetími každá session začíná a končí – a žádný nedělá práci toho vedle:
>
> **Osa** **`/project`** → [`/discovery`](../discovery/README.md) → [`/specify`](../specify/README.md) → [`/architect`](../architect/README.md) → [`/breakdown`](../breakdown/README.md) → [`/implement`](../implement/README.md) → [`/release`](../release/README.md) → [`/evaluate`](../evaluate/README.md)
>
> **Kontroly** [`/oponent`](../oponent/README.md) · [`/consolidate`](../consolidate/README.md) · [`/review`](../review/README.md) · [`/consistency`](../consistency/README.md) · [`/attack`](../attack/README.md)
>
> **Session** [`/next`](../next/README.md) · [`/continue`](../continue/README.md) · [`/end`](../end/README.md) · [`/merge`](../merge/README.md) · [`/break`](../break/README.md)
>
> Projít se nemusí celý – u drobné změny odpadá zadání i plán, u projektu bez kódu nasazení i vyhodnocení provozu.

Postupně se zeptá na všechno, co se u nového projektu řeší pokaždé znovu – jak se jmenuje a čím je, Git a vzdálený repozitář, uspořádání na disku, dokumentační strukturu, automatické commity, typ projektu, spouštěcí příkazy, doménové checklisty – a rovnou to nastaví. Umí ale i projekty, které už existují: udělá inventuru a dorovná je, aniž by cokoliv přepsal bez zeptání. A **umí se vrátit ke stejnému projektu za rok**, kdy se standardy mezitím posunuly a projekt v nich zůstal stát.

## Co umí

1. **`create`** – nový projekt v prázdném adresáři, všechno se zakládá od nuly.
2. **`adopt`** – existující projekt, ve kterém už něco je. Zjistí aktuální stav, nabídne, co dorovnat, a nic nepřepisuje naslepo.
3. **`update`** – projekt, kterým skill už jednou prošel. Neptá se znovu na volby, které padly, ale **projde celý projekt proti tomu, jak standardy vypadají dnes**, a dorovná, co se rozešlo.
4. **Režim pozná sám** podle otisku, který si v projektu nechává – nemusíte ho zadávat.
5. **Nastaví Git** včetně založení vzdáleného repozitáře a propíše do jeho popisku a odkazu totéž, co je v projektu, aby na obou místech nestálo něco jiného.
6. **Zvládne i uspořádání s jedním pracovním adresářem na větev**, takže nad projektem může běžet víc sezení naráz, aniž si přepisují soubory. Přijde-li do projektu, který tak už uspořádaný je, **hlavní větev nechá být** a vlastní si založí, teprve až se má opravdu něco změnit; merge nechává na vás.
7. **Založí dokumentační strukturu** – co je odložené, co je jen nezávazný nápad, co hotové, co se rozhodlo a proč, jaké principy platí – a nechá vás vybrat, jestli má ležet ve vlastní složce, nebo v kořeni.
8. **Nabídne produktové podklady** – doklady poptávky, analýzu konkurence, registr rizik, scénáře, glosář, ceník. Nezakládá je prázdné; jen si zapíše, které z nich projekt vede, aby se pak poznal chybějící dokument od nechtěného.
9. **Zapne kontroly kvality** – zapíše, čím se v projektu pouštějí testy, typová kontrola, linter, build a formátovač, a řekne, co se tím nebude kontrolovat, když projekt některý z nich nemá. K tomu language server pro jazyk projektu a zákazy, které model nesmí obejít – u převzatého kódu bez testů jako první úkol testy, které zachytí jeho dnešní chování.
10. **Napojí doménové checklisty** podle povahy projektu.
11. **Drží pohromadě všechno pro jednoho klienta.** Ve složce klienta založí kromě běžného projektu i profil klienta – kdo to je, kdo tam rozhoduje, jak se s nimi pracuje – a fakturační dohodu, profil napojí tak, aby ho znal každý projekt pro toho klienta, a klienta vedeného dřív jinde do složky převede.

## Proč zrovna tenhle

- **Revize je hlavní důvod, proč existuje.** Standardy se vyvíjejí dál, kdežto projekt založený loni zůstane stát – a rozdíl se z něj sám nepozná. Tohle je způsob, jak ho dorovnat jedním zavoláním.
- **Nepřepisuje nic naslepo.** Chybějící soubor založí; u rozporu ukáže rozdíl a zeptá se.
- **Nevymýšlí příkazy, které projekt neumí.** Řádek, který nikam nevede, je horší než chybějící řádek – a co chybí, se výslovně vypíše i s tím, co se tím nebude kontrolovat.
- **Kontroly kvality nezměkčuje sám.** Zapnutí přísného režimu u staršího projektu vyplaví stovky chyb naráz; snížit laťku smí jen člověk a s důvodem zapsaným do projektu, včetně termínu, kdy se přitvrdí.
- **Nespouští za vás souhlas s automatickou kontrolou.** Vypíše příkaz, který si spustíte sami – jinak by celá kontrola ztratila smysl – a řekne pravdu o tom, co tím schvalujete.
- **Ptá se postupně**, jednu otázku za druhou, a to, co jde odvodit, navrhne rovnou k odsouhlasení.
- **Nezakládá soubory do zásoby.** U projektu, kde se nic nerozhoduje, je prázdný soubor pro rozhodnutí horší než žádný.
- **Hlídá, aby popis projektu nestál na třech místech různě** – v instrukcích, v přehledu pro lidi a v nastavení repozitáře.
- **Ověřuje, že odkazy vedou někam.** Každá zmíněná cesta i každý zmíněný skill musí existovat; tím se chytí přejmenované a zrušené věci, aniž byste museli vědět, co se změnilo.
- **Nenajde-li nic, řekne to.** Běh bez zásahu je platný výsledek revize, ne důvod něco vymýšlet.

## Jak se to používá

```
/project           # režim si pozná sám
/project update    # rovnou revize proti dnešnímu standardu
```

## Ukázka výstupu

```
## Revize proti standardu

Dorovnáno rovnou (6)
- blok metadat doplněn o řádek Repozitář
- docs/done.md: 3 hotové položky přesunuty z todo.md
- docs/backlog.md: založen, 2 nezávazné nápady vytaženy z todo.md
- .gitignore: doplněn .claude/run/

Čeká na rozhodnutí (2)
- decisions.md má obrácené řazení – srovnat, nebo nechat?
- README obsahuje pravidla práce pro Clauda – přesunout do CLAUDE.md?

Vědomě ponecháno (1)
- chybí příkaz na pokrytí testy – projekt zatím testy nemá
```

## Co nedělá

- **Nepíše zadání ani plán.** Co se staví, řeší `/specify`, rozpad na úkoly `/breakdown`.
- **Neprogramuje.** Ani scaffold, ani závislosti. Nastavuje projekt, ne aplikaci.
- **Nenaplňuje soubory obsahem.** Zakládá je prázdné, jen s nadpisem.
- **Nerediguje dokumentaci.** Hlídá tvar – kde soubor leží, jak se jmenuje, jak je seřazený. Jestli je zapsané rozhodnutí správné, řeší `/consistency` a `/review`.

## Jak si ho nainstalovat

Je to snadné, zadejte do svého Claude Code tenhle prompt:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/project a nainstaluj mi ten skill k sobě do `~/.claude/skills/` – celý adresář i s podadresáři. Stáhni k němu z téhož repozitáře na odpovídající místo pod `~/.claude/` i sdílené soubory ze `skills/` a `standards/`, na které jeho soubory odkazují, a definice typů subagentů, které pouští, z `agents/` do `~/.claude/agents/`. Co už u sebe mám, nepřepisuj a ukaž mi rozdíl. Odkazuje-li na jiný skill, zeptej se mě, jestli ho chci taky. Odkazy na soubory, které v repozitáři nejsou, mi vypiš a u každého se zeptej, jestli ho napojit na můj vlastní soubor, nebo odkaz smazat. Pak ho napoj na moji vlastní představu o tom, jak má projekt vypadat – zeptej se mě na ni. Nakonec mi řekni, co musím doplnit sám.

Skill je **instalátor cizího standardu, ne jeho definice** – doménové checklisty a část pravidel drží moje soukromá knowledge base, která v tomhle repozitáři není. Postup a pojistky zůstanou, obsah bude váš.

**Nebo celou sadu naráz.** Chcete-li místo jednoho skillu rovnou celý životní cyklus, zadejte do svého Claude Code tenhle prompt:

> Jdi na https://github.com/jantichy/claude/tree/main/skills a nainstaluj mi do `~/.claude/skills/` celý životní cyklus: project, discovery, specify, architect, breakdown, implement, release, evaluate, oponent, consolidate, review, consistency a attack, a k nim skilly, kterými session začíná a končí: next, continue, end, merge a break. Každý z nich nainstaluj přesně podle promptu v sekci „Jak si ho nainstalovat“ v jeho README; na skilly z téhle sady se mě při tom neptej, beru je všechny.

---

### Požadavky a omezení

Git, a chcete-li zakládat repozitáře rovnou z terminálu, i příkazová řádka GitHubu (u jiných hostitelů si popisek repozitáře nastavíte ručně – skill to řekne). Automatická kontrola po každé odpovědi potřebuje ještě kontrolní skript z tohohle repozitáře – řekněte si o něj Claudovi spolu se skillem; bez něj se jen zapíše, čím se co spouští.
