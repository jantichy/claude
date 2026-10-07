# Katalog zásahů

Co `/slim` v souboru hledá, jak to pozná a co s tím. Čte se ve *Fázi 2* a *Fázi 3*.

## Obsah

- [Kdy text smí z paušálu pryč](#kdy-text-smí-z-paušálu-pryč)
- [Soubory čtené odkazem](#soubory-čtené-odkazem)
- [Rozdělení podle čtenáře](#rozdělení-podle-čtenáře)
- [Redukce na jádro](#redukce-na-jádro)
- [Duplicity mezi soubory načítanými spolu](#duplicity-mezi-soubory-načítanými-spolu)
- [Kategorie zásahů](#kategorie-zásahů)
- [Slabé pravidlo](#slabé-pravidlo)
- [Pravidla, která nabobtnání vyrábějí](#pravidla-která-nabobtnání-vyrábějí)
- [Co se při kompresi ztrácí](#co-se-při-kompresi-ztrácí)
- [Co se vyčísluje a jak](#co-se-vyčísluje-a-jak)

## Kdy text smí z paušálu pryč

Paušál je to, co se načte do každé session bez ptaní – soubory, které Claude Code najde sám, a jejich `@` importy. Rozhodující otázka u každé sekce: **kdo ten text čte a kdy.**

- **Zůstává, co se uplatní v každé odpovědi** nebo co model potřebuje, aniž ví, že to potřebuje – prevence. Tabulka zakázaných termínů pryč nesmí, protože model neví, že sahá po nezavedeném slově; smí ale ztenčit na „místo X piš Y, platí na Z“.
- **Pryč smí, co se uplatní jen při určité činnosti** – zakládání projektu, zápis do `docs/`, pouštění agentů, měření, návrh modelu –, ale jen když **tu činnost opravdu něco spustí**: skill si soubor přečte v přípravě, test ho vynucuje, nebo v paušálu zůstane jednořádkový spouštěč („než pustíš agenta, načti si `delegation.md`“). Odkaz bez mechanismu je přání.
- **Nejvýš jeden krok od místa, které se čte pokaždé.** Soubor, na který odkazuje soubor načítaný odkazem, se v praxi nenačte. Spouštěč proto stojí v paušálu nebo v souboru, který si čte každý skill (`~/.claude/skills/preflight.md`).
- **Kde je cena nedodržení vysoká a spouštěč nejistý, pravidlo zůstává** (typicky git: `add -A`, heredoc, řetězení za blokovatelný příkaz) – jen zkrácené.
- **Čte-li soubor jediný skill, patří k němu**; čte-li ho víc skillů, do sdíleného místa (`~/.claude/`, `~/.claude/skills/`), ne dovnitř cizího skillu.
- **Veřejné × soukromé:** obecné pravidlo patří do veřejného `~/.claude/`, know-how a klientský obsah do `~/Dev/context/`. Přesun nesmí zveřejnit, co veřejné být nemá.

## Soubory čtené odkazem

**Soubor mimo paušál není mimo rozsah.** Neimportovaný soubor, který si čte skoro každý skill (`structure.md` přes přípravu), stojí kontext skoro v každé práci – jen ne hned na startu. Rozhoduje **velikost × jak často se čte**, ne to, jestli ho najde `tree`.

- **Jak často se čte, ukáže `measure.py refs`** – kdo dává pokyn „načti si `…`“. Počet je vodítko, ne četnost: pokyn v `preflight.md` platí pro skoro každý skill, pokyn v jednom `SKILL.md` jen pro ten běh.
- **Často čtený soubor se rozebírá stejně důkladně jako paušál** – rozdělením podle čtenáře a redukcí na jádro, ne jen kompresí. Komprese sama dá kolem desetiny; zbytek leží v textu, který v typické situaci nikdo nepotřebuje.

## Rozdělení podle čtenáře

U každé sekce: **v kolika situacích, kdy se soubor čte, se doopravdy uplatní?** Uplatní-li se jen v části z nich – u některých typů projektů, u jednoho nebo několika skillů –, je kandidátem na přesun do **podmíněně čteného dítěte**: nového souboru, existujícího souboru, který čte jen ta skupina, nebo do skillu, který to jediný dělá.

- **Kam:** jediný skill → do jeho adresáře; víc skillů → sdílený soubor (`~/.claude/rules/`, `~/.claude/skills/`); skupina projektů → soubor, který si načítají jen ony. Existující soubor, který ten čtenář už čte, má přednost před novým.
- **Cíl se musí číst ve všech situacích, kde pravidlo platí.** Ověř spouštěč cíle, ne jeho jméno: soubor v doméně `coding/` se může načítat i u dokumentačních projektů (a naopak). Nesedí-li to, pravidlo zůstává, nebo jde jinam.
- **Nový soubor potřebuje čtyři věci**, jinak je to přání: **spouštěč** v místě, které se čte pokaždé, když je potřeba (paušál nebo `preflight.md`); **test**, že spouštěč nezmizí (vzor `test_preflight_requires_loading_unimported_files`); **úvod**, který říká, kdo ho načítá a kdy; **řádek v rozřazovací sekci** („co sem nepatří“) zdrojového souboru i repozitáře, jinak se příští pravidlo vrátí do rodiče. Plus odstavec v `README.md`, má-li repozitář jeho soupis.
- **V rodiči zůstane řádek**, kde to stojí a kdy se to čte – ne kopie.

## Redukce na jádro

Komprese zkrátí větu; redukce se ptá, **jestli ta věta má být vůbec**. U každého pravidla: *co by model udělal špatně, kdyby tu nestálo?* Nic → pryč.

**Zůstává:** zákaz a jeho síla (*nesmí* × *stačí*), podmínka a spouštěč (*kdy*, *jen když*, *nečekej na*), rozsah a výjimka, povinné pole a tvar, kdo co zapisuje, kritérium, podle kterého se rozhodne hraniční případ, a **jedna věta pointy**.

**Jde pryč:** rozvedené zdůvodnění, příklad, který neurčuje tvar, popis vnitřku skillu („`/implement` zapisuje sám, protože…“) – ten drží skill –, výklad mechanismu, ze kterého neplyne pokyn, opakování pravidla z jiného souboru a rétorika („Uživatel na to nesmí muset upozorňovat“, „Backlog není hřbitov“).

**Předkládá se jako varianta s čísly**, vedle konzervativní komprese: u často čteného souboru bývá rozdíl trojnásobný. Je to rozhodnutí uživatele, protože škrtá i věty, které nejsou vata.

## Duplicity mezi soubory načítanými spolu

Dvě kopie téhož pravidla ve dvou souborech, které se **vždy načtou spolu**, jsou čistá ztráta. Nejdřív urči vztah načítání – z `tree`, z `refs` a ze znění spouštěčů, ne z dojmu:

- **Paušál** je načtený vždy, takže je „rodičem“ každého souboru.
- **Rodič → dítě:** dítě se načítá jen v situacích, kdy je načtený i rodič (oba spouští týž `preflight.md`, nebo spouštěč dítěte stojí v rodiči). Opačně to neplatí – rodič se čte i bez dítěte.
- **Sdílený soubor → skill**, který si ho v přípravě čte.

| Pravidlo stojí | Uplatní se | Co s ním | Rozhoduje |
|---|---|---|---|
| v paušálu i jinde | kdekoliv | smazat mimo paušál, nechat odkaz jen tam, kde pomáhá najít kontext | rovnou, je-li znění totožné |
| v rodiči i v dítěti | i mimo situace dítěte | smazat z dítěte | rovnou, je-li znění totožné |
| v rodiči i v dítěti | **jen v situacích dítěte** | **přesunout do dítěte, z rodiče smazat** | uživatel |
| jen v rodiči | jen v situacích dítěte | přesunout do dítěte – viz *Rozdělení podle čtenáře* | uživatel |
| ve sdíleném souboru i ve skillu | jen v tom skillu | do skillu, ze sdíleného souboru smazat | rovnou, je-li ve skillu celé |
| ve sdíleném souboru i ve skillu | ve víc skillech | ve sdíleném souboru, skill odkazuje | rovnou |

**Hledej po pravidlech, ne po řetězcích.** Totéž pravidlo bývá v každém souboru formulované jinak; vezmi tučné úvody a klíčová slova pravidla a hledej jejich smysl v rodiči, dítěti i ve skillech, které text popisuje. **Kopie vnitřku skillu ve sdíleném souboru** (šablona záznamu, kterou zapisuje jediný skill) je nejčastější případ.

**Liší-li se kopie obsahem**, není to duplicita s vítězem, ale dvě verze pravidla – předlož je uživateli jako *duplicitu bez vítěze*.

## Kategorie zásahů

| Kategorie | Jak se pozná | Co s tím | Rozhoduje |
|---|---|---|---|
| **Přesun na odkaz** | sekce paušálu platí jen při jedné činnosti | přesun celé sekce do souboru načítaného odkazem, v paušálu spouštěč | uživatel |
| **Rozdělení podle čtenáře** | sekce často čteného souboru platí jen v části situací | přesun do podmíněně čteného dítěte, viz výš | uživatel |
| **Redukce na jádro** | pravidlo nese výklad, příklady, popis vnitřku skillů | ponechat jen to, bez čeho by model jednal špatně | uživatel |
| **Tenké jádro + výklad stranou** | soubor nese pravidlo i jeho rozvahu; roste s každým záznamem | v paušálu jen tabulka nebo pravidla, výklad do souboru ke správci | uživatel |
| **Jiný čtenář** | text je dokumentace, ne instrukce – co která kontrola hlídá, historie kontraktu | do souboru pro toho čtenáře (`tests/README.md`), v paušálu odkaz | uživatel |
| **Doklad** | datum, incident, citace, jméno projektu, historie pravidla („do té doby tu stálo“, „upřesněno …“), měření sloužící jen jako důkaz | škrt; pointa zůstane jednou větou, doklad nese commit | rovnou |
| **Slabé pravidlo** | viz níž | zrušení | uživatel |
| **Duplicita s jasným vítězem** | totéž na dvou místech, jedno je zjevně domov – včetně dvojic podle *Duplicit mezi soubory načítanými spolu* | ve druhém odkaz nebo nic | rovnou |
| **Duplicita bez vítěze** | dvě místa, obě obhajitelná, nebo se liší obsahem | sloučení; které místo vyhraje | uživatel |
| **Překryv se systémovým promptem** | pravidlo říká totéž co Claude Code sám (jazyk odpovědí, stručnost, git) | škrt, pokud nepřidává nic navíc | uživatel |
| **Komprese** | esejistické odstavce, kontrastní páry, „**Proč:**“ nad rámec věty, opakování teze | přepis na kratší bez změny významu | rovnou |
| **Nabobtnávací pravidlo** | viz níž | zrušení nebo přepis | uživatel |

**„Rovnou“ platí jen tehdy, když se nemění význam.** Jakmile škrt nebo komprese ubere podmínku, výjimku nebo rozsah pravidla, je to rozhodnutí uživatele.

**Dřívější zamítnutí je vstup, ne zákaz.** Zamítl-li minulý běh přesun nebo škrt (stojí v `decisions.md`), nabídni ho znovu, jestliže je mezi největšími pákami nebo se od té doby změnila jeho cena – i se zněním dřívějšího důvodu, ať uživatel rozhoduje s ním. Mlčky ho nepřeskakuj.

## Slabé pravidlo

Pravidlo, které nic nerozhoduje, zabírá místo každé session a navíc ředí ta, která rozhodují. Kandidát na zrušení je, když platí aspoň jedno:

- **Model to dělá i bez něj** – „piš srozumitelně“, „buď pečlivý“, „ověř si, že kód funguje“.
- **Je vágní** – nejde podle něj rozhodnout konkrétní případ; test: dala by se podle něj zamítnout konkrétní změna?
- **Opakuje hranici vynucenou jinde** – kontrolou, hookem, souhlasem z terminálu. Věta v kontextu je druhá kopie téže hranice.
- **Míří na situaci, která už nenastává** – odstraněný nástroj, zrušený skill, vyřešený incident.
- **Popisuje místo předepisování** – vysvětluje, jak něco funguje, a z výkladu neplyne žádný pokyn.
- **Je výjimka pro jeden projekt** v souboru, který platí pro všechny.

Pravidlo se neruší proto, že je dlouhé, ale proto, že nic nerozhoduje. Dlouhé a nosné se komprimuje.

## Pravidla, která nabobtnání vyrábějí

Soubor nenaroste sám – narostl, protože nějaké pravidlo žádá ke každému zápisu text navíc. Bez revize takového pravidla se úklid do měsíce vrátí. Hledej ve stromu načítání i v normách, podle kterých se do něj píše (`structure.md`, `skills.md`, rozřazovací sekce „co sem nepatří“):

- povinnost psát ke každému pravidlu zdůvodnění, a to v tomtéž souboru,
- povinnost zapisovat doklad, datum, incident nebo počet výskytů k pravidlu,
- povinnost zapisovat zamítnuté varianty a historii přímo k pravidlu, ne do `decisions.md`,
- povinnost „zapsat i to, co se vědomě nemá“ do souboru, který se načítá pokaždé,
- rozřazovací test, jehož reziduální větev („nic z toho → sem“) posílá do paušálu všechno, co jinam nepasuje,
- zvyk bez pravidla – poznáš ho z historie: `git log -p` největšího rostoucího souboru za poslední týdny a co v přírůstcích převažuje.

Návrh zní vždy konkrétně: zrušit, nebo přepsat na verzi, která text navíc posílá do commitu nebo `decisions.md`, a doplnit rozřazovací test o větev „platí jen při činnosti X → podmíněný soubor“.

## Co se při kompresi ztrácí

Ověřovací čtenář našel při kompresi a redukci opakovaně tyhle posuny – hlídej je už při psaní a dej je čtenáři do zadání:

- **zákaz → doporučení** („víc jich zakládat se nemá“ → „stačí“),
- **podmíněné → povinné** („byl-li zamítnutý s odůvodněním, jde to do `decisions.md`“ → „jde to do `decisions.md`“),
- **vypadlý spouštěč nebo čas** („nečekej na `/cleanup`“, „prázdná sekce se ruší“, „datum patří na začátek“),
- **vypadlá uzávěra** („třetí možnost není“) a kritérium, podle kterého se hraniční případ pozná,
- **výčet pod úvodní větou, která na všechny položky nesedí** („Další sekce, které zakládá `/project`:“ nad sekcí, kterou zakládá jiný skill),
- **rozšířený rozsah** – konkrétní výčet souborů nahrazený obecným „standardní soubory“,
- **ztracené čtení** – pravidlo přesunuté do souboru, jehož spouštěč nepokrývá situaci, kde se uplatní.

## Co se vyčísluje a jak

- **Úspora se počítá z textu, který se opravdu odstraní**, ne z celé sekce nebo odstavce, ve kterém stojí značka. Počet značek z `measure.py sections` je vodítko, kde hledat, ne velikost úspory – odstavec s „Doloženo“ nese většinou i nosné pravidlo.
- **Znaky, ne bajty.** Limit je ve znacích; `wc -c` dá u češtiny zhruba o desetinu víc.
- **Přesun ušetří v kontextu, ne v součtu.** Soubor stranou smí narůst; vyčísluje se paušál, u souboru čteného odkazem to, co se přečte v typické situaci.
- **Spouštěč a nový úvod vracejí část úspory** – u přesunu sekce počítej s tím, že v paušálu zůstane pár set znaků.
