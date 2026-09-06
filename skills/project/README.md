# /project – projekt nastavený na pár kliknutí

> **Součást životního cyklu projektu.** Tenhle skill patří do ucelené sady deseti skillů, které vedou práci od založení projektu až po nasazení. Každý má svůj krok a žádný nedělá práci toho vedle:
>
> **`/project`** → [`/specify`](../specify/README.md) → [`/oponent`](../oponent/README.md) → [`/breakdown`](../breakdown/README.md) → [`/implement`](../implement/README.md) → [`/review`](../review/README.md) → [`/consistency`](../consistency/README.md) → [`/cleanup`](../cleanup/README.md) → [`/attack`](../attack/README.md) → [`/release`](../release/README.md)
>
> Projít se nemusí celá – u drobné změny odpadá zadání i plán, u projektu bez kódu nasazení.

Postupně se zeptá na všechno, co se u nového projektu řeší pokaždé znovu – jak se jmenuje a čím je, Git a vzdálený repozitář, uspořádání na disku, dokumentační strukturu, automatické commity, typ projektu, spouštěcí příkazy, doménové checklisty – a rovnou to nastaví. Umí ale i projekty, které už existují: udělá inventuru a dorovná je, aniž by cokoliv přepsal bez zeptání. A **umí se vrátit ke stejnému projektu za rok**, kdy se standardy mezitím posunuly a projekt v nich zůstal stát.

## Co umí

1. **`create`** – nový projekt v prázdném adresáři, všechno se zakládá od nuly.
2. **`adopt`** – existující projekt, ve kterém už něco je. Zjistí aktuální stav, nabídne, co dorovnat, a nic nepřepisuje naslepo.
3. **`update`** – projekt, kterým skill už jednou prošel. Neptá se znovu na volby, které padly, ale **projde celý projekt proti tomu, jak standardy vypadají dnes**, a dorovná, co se rozešlo.
4. **Režim pozná sám** podle otisku, který si v projektu nechává – nemusíte ho zadávat.
5. **Nastaví Git** včetně založení vzdáleného repozitáře a propíše do jeho popisku a odkazu totéž, co je v projektu, aby na obou místech nestálo něco jiného.
6. **Zvládne i uspořádání s jedním pracovním adresářem na větev**, takže nad projektem může běžet víc sezení naráz, aniž si přepisují soubory.
7. **Založí dokumentační strukturu** – co je odložené, co hotové, co se rozhodlo a proč, jaké principy platí – a nechá vás vybrat, jestli má ležet ve vlastní složce, nebo v kořeni.
8. **Zmigruje starší pojmenování souborů** a projde celý repozitář, aby nezůstal rozbitý odkaz.
9. **Zapne brány kvality** – zapíše, čím se v projektu pouštějí testy, typová kontrola, linter a build, a řekne, co se tím nebude kontrolovat, když projekt některý z nich nemá.
10. **Napojí doménové checklisty** podle povahy projektu.

## Proč zrovna tenhle

- **Revize je hlavní důvod, proč existuje.** Standardy se vyvíjejí dál, kdežto projekt založený loni zůstane stát – a rozdíl se z něj sám nepozná. Tohle je způsob, jak ho dorovnat jedním zavoláním.
- **Nepřepisuje nic naslepo.** Chybějící soubor založí; u rozporu ukáže rozdíl a zeptá se.
- **Nevymýšlí příkazy, které projekt neumí.** Řádek, který nikam nevede, je horší než chybějící řádek – a co chybí, se výslovně vypíše i s tím, co se tím nebude kontrolovat.
- **Brány kvality nezměkčuje sám.** Zapnutí přísného režimu u staršího projektu vyplaví stovky chyb naráz; snížit laťku smí jen člověk a s důvodem zapsaným do projektu, včetně termínu, kdy se přitvrdí.
- **Nespouští za vás souhlas s automatickou kontrolou.** Vypíše příkaz, který si spustíte sami – jinak by celá brána ztratila smysl – a řekne pravdu o tom, co tím schvalujete.
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

Nechte to na Claudovi. Otevřete si Claude Code a napište mu:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/project a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.

Skill je **instalátor cizího standardu, ne jeho definice** – strukturu projektu, tvar dokumentace a doménové checklisty drží moje soukromá knowledge base, která v tomhle repozitáři není. **Řekněte proto Claudovi, ať ho napojí na vaši vlastní představu o tom, jak má projekt vypadat**; postup a pojistky zůstanou, obsah bude váš.


**Nebo celou sadu naráz.** Chcete-li místo jednoho skillu rovnou celý životní cyklus, napište mu tohle:

> Jdi na https://github.com/jantichy/claude/tree/main/skills a nainstaluj mi do `~/.claude/skills/` celý životní cyklus: project, specify, oponent, breakdown, implement, review, consistency, cleanup, attack a release. U každého si přečti README a řekni mi, co k nim potřebuju doplnit.

---

### Požadavky a omezení

Git, a chcete-li zakládat repozitáře rovnou z terminálu, i příkazová řádka GitHubu (u jiných hostitelů si popisek repozitáře nastavíte ručně – skill to řekne). Automatická kontrola po každém tahu se opírá o skript `green-line.sh` z tohohle repozitáře; bez něj se jen zapíše, čím se co spouští.
