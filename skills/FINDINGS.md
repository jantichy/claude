# Nález: kdo o něm rozhoduje a jak vypadá

Jedno kritérium a jeden tvar pro všechny skilly, které nálezy nejen hlásí, ale i opravují. Stojí mimo ně, protože **hranice mezi „opravím sám“ a „rozhodne uživatel“ musí být napříč skilly tatáž** – jinak si týž nález v `/review` vyžádá otázku a v `/consistency` se opraví mlčky, a uživatel nemá jak odhadnout, co ho v kterém běhu čeká. Totéž platí o **podobě výpisu a voleb**: uživatel prochází nálezy z několika skillů v jednom životním cyklu, takže dvě jména pro tutéž volbu čte jako dvě různé volby.

Závažnost nálezu je jiná otázka a drží ji `~/.claude/skills/SEVERITY.md`. **Stupeň neurčuje, kdo rozhoduje:** kritický nález s jedinou zjevnou opravou se opraví rovnou, nízký s dvěma obhajitelnými podobami jde k uživateli.

## Osa není „jak riskantní“, ale „je z čeho vybírat“

**Ptej se jedině tehdy, když má oprava víc obhajitelných podob a volba mezi nimi je uživatelova.** Nic jiného otázku neodůvodňuje – ani to, že zásah mění strukturu, ani že je ho hodně, ani že se ti do něj nechce.

| Skupina | Kritérium | Co s ní |
|---|---|---|
| **Mechanické** | oprava nemění chování ani strukturu: překlep, typografie, mrtvý odkaz, zastaralý počet proti jednoznačnému zdroji, pozůstatek po dokončeném přejmenování | oprav rovnou, vypiš jedním řádkem na nález |
| **Jednoznačné** | oprava chování nebo strukturu mění, ale má **právě jednu zjevně správnou podobu** – dorovnání toho, co už je rozhodnuté jinde, doplnění chybějícího kusu, jehož tvar určuje okolí | oprav rovnou, vypiš **i s tím, co se změnilo a proč** |
| **Sporné** | oprava má víc obhajitelných podob; nebo chybí údaj, který ví jen uživatel a **nedá se zjistit z repozitáře**; nebo je zásah nevratný, sahá mimo repozitář či do cizího systému | zeptej se, jeden nález = jedna otázka |

**Váhání je odpověď.** Nepřemlouvej se, že nález do prvních dvou skupin „nejspíš patří“ – patří tam jen to, u čeho je to zřejmé na první pohled.

### Nejistotu nejdřív zkus odstranit

**Než nález prohlásíš za sporný, zjisti, jestli je odpověď vůbec zjistitelná.** Dá se spočítat, dohledat, porovnat se zdrojem, který v repozitáři je? Pak to není sporný nález, ale **práce** – a ta se dělá (`~/.claude/RULES.md`, *Při nejistotě se zeptej*: údaj, který jde dohledat, si ověř sám; ptej se na to, co ví jen uživatel).

**Pracnost není spornost.** „Tohle bych musel projít celé a přepočítat“ je popis práce, ne důvod k otázce. Uživatel má na tutéž práci tytéž soubory, takže ho dotazem nešetříš – jen mu ji přehazuješ zpátky i s kontextem, který máš načtený ty a on ne.

**Proto tu není podmínka „netroufáš si“**, která tu do 21. 9. 2026 stála. Byla to jediná položka v celé tabulce bez vnějšího kritéria – pocit, kterým se dá odůvodnit skoro cokoliv, a nejspolehlivěji zrovna nález, jehož vyřešení by dalo práci. **Doloženo v běhu `/cleanup` (21. 9. 2026):** dva dokumenty uváděly různý počet akcí u téže věci a skill se na to zeptal s odůvodněním, že si netroufá určit hranici mezi dvěma pojmy bez uživatelova výkladu. Ta hranice přitom byla v katalogu, ze kterého se obě čísla počítala – šlo o půlhodinu počítání, ne o rozhodnutí. **Zbylo-li ti po téhle zkoušce „nevím“, formuluj, co přesně nevíš**; nejde-li to napsat jednou větou, je to nedodělaná rešerše, ne sporný nález.

**Objem důvod k dotazu není.** Zdlouhavá, ale jednoznačná oprava se dělá, ne předkládá; naopak jednořádková změna pravidla se předkládá, i když trvá vteřinu. Rozhoduje, čí je to rozhodnutí, ne kolik je s ním práce.

## Volby v otázce jsou varianty řešení, ne „teď nebo později“

**Vyjdou-li ti volby *Opravit / Odložit / Přeskočit*, je to doklad, že nález mezi sporné nepatří.** U takové trojice je odpověď předem známá – odložit opravu, kterou umíš udělat hned, nechce nikdo, a nechat vadu vyhnít taky ne. Otázka tedy nic nerozhoduje a stojí pozornost, kterou pak uživatel nemá na otázky, kde na jeho odpovědi opravdu záleží.

**Zákaz míří na tvar, ne na ta tři slova.** Přejmenovat volby nic nemění: *Vyřešit teď / Zapsat do todo / Zahodit* je přesně táž trojice jako *Opravit / Odložit / Přeskočit*, jen jinak pojmenovaná, a projde i tam, kde ji skill sám předepisuje tabulkou. **Test před každým voláním `AskUserQuestion`: je aspoň jedna volba podobou řešení – tedy odpovědí na otázku „jak“?** Odpovídají-li všechny jen na „kdy“ (teď / potom / nikdy), otázka nerozhoduje o ničem, co bys nerozhodl sám, a nemá se položit. Doplněno 21. 9. 2026, protože verze psaná na konkrétní slova tenhle případ nechytila.

**Jediná výjimka: položka, která není vadou, ale novou prací nebo nápadem.** Tam je „jestli a kdy“ doopravdy uživatelovo rozhodnutí – rozšíření, které nikdo nezadal, se nedá „opravit“, protože není co. Test tedy zní: **existuje stav, který je prokazatelně špatně?** Když ano (dvě místa si odporují, odkaz nikam nevede, číslo nesedí se zdrojem), je to vada a volba „kdy“ je falešná. Když ne, je to návrh a trojice je na místě.

**Sporný nález se proto ptá na podobu opravy:** „nese to pole API, nebo si to widget bere z vlastního kontextu?“, „loguje se to do `UserLogu`, nebo se ta mez pojmenuje?“. Volby jsou konkrétní a u každé stojí, co se stane.

**Záchytné volby zůstávají**, ale vedle variant, ne místo nich – a odložení se nabízí u nálezu, který se odložit doopravdy může, protože závisí na něčem nehotovém. Jak se jmenují a co znamenají, drží *Dvě záchytné volby a co znamenají* níž.

## Jak nález vypadá

**Odstavcem, ne mřížkou popisků.** Začne tučným názvem, za kterým hned pokračuje normální věta:

```
**[N/celkem] 🔴/🟡/🔵 NÁZEV NÁLEZU.** <plynulý text: čeho se to týká, jak to je dnes a proč to nestačí – kde to je a čím je to doložené řekni uvnitř věty, ne na zvláštním řádku>

**Varianty řešení**
- **A)** <…> – <důsledek>
- **B)** <…> – <důsledek>

**Doporučuji:** <jedna z nich a proč>
```

Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo (`~/.claude/RULES.md`, *Styl odpovědí*).

**Tučný je jen název, zbytek ne.** Odstavec, ve kterém svítí tučně každý druhý popisek, se nedá číst – oko skáče po zvýrazněních místo aby četlo větu.

**Platí to na každou položku, o které se uživatel rozhoduje**, ne jen na nález: nevypořádané téma, položka mimo rozsah, poznatek z provozu i návrh alternativy. Liší se jen slovo v titulním řádku (`NÁZEV NÁLEZU`, `NÁZEV POLOŽKY`), ne tvar.

**Seznam popisků typu `Kde` / `Co` / `Problém` / `Proč to vadí` / `Podklad` se nepoužívá.** Do 28. 9. 2026 ho měly tři kontrolní skilly, každý jinou sadu, a **uživatel je označil za nečitelné**. Heslo za dvojtečkou vypadá úplně a přitom vynechá právě to, proč na tom záleží; kde nález je a čím je doložený, se řekne uvnitř věty a odkazy se dávají do textu.

**Zákaz míří na tvar, ne na těch pět jmen.** Přejmenovat popisky nic nemění – `Druh` / `O co jde` / `Doložení` / `Prověřeno` je táž mřížka jako `Kde` / `Co` / `Problém`, jen jinak nadepsaná, a projde i tam, kde si ji skill předepisuje vlastní šablonou. **Test před každým výpisem: stojí pod titulním řádkem dvě a víc odrážek tvaru `- **Popisek:** …`?** Pak je to mřížka, ať se popisky jmenují jakkoliv. Doplněno 28. 9. 2026, protože verze psaná na konkrétní slova dvě místa v `/cleanup` nechytila a uživatel je dostal do rozhraní hned první běh po sjednocení.

**Delší nález smí mít druhý odstavec** – typicky tam, kde je potřeba dodat, proč navrhované cesty nejsou rovnocenné. Pořád je to souvislý text.

**Není to převyprávěný název.** „Chybí kontrola vlastníka“ → „Kontrola vlastníka chybí“ je vata. Text říká, co ta věc v projektu dělá a co se stane, když zůstane, jak je.

**Zrádné je, že tobě ten kontext nechybí.** Máš před sebou soubor, ve kterém jsi nález právě našel, takže heslovitý výpis vypadá úplně; uživatel má v hlavě celý projekt, ne řádek, na kterém stojíš ty.

**Varianty musí sedět s volbami v otázce** – otázka je jejich zrcadlo, ne druhá sada. Vypsat jedno řešení a pak se zeptat na tři je rozpor, který uživatele donutí číst obojí a hledat, čím se to liší.

**Pole ve schématu nálezu tím dotčená nejsou.** Závažnost, lokace a doložení, které vracejí agenti, zůstávají – stojí na nich ověřování a zápis do `CLAUDE.md`. Mění se jen to, **jak se nález ukazuje člověku**: pole jsou vstup, odstavec je výstup.

**Proč zrovna tenhle tvar:** změřeno 28. 9. 2026 při sjednocování. Uživatel označil za srozumitelný výpis nálezu, který **nevyrobil žádný skill** – vznikl v běžné rozpravě, kde žádná šablona neplatila. Tři tehdejší šablony se proti němu lišily jen tím, že souvislý text nahradily popisky. **Šablona tedy výsledek nezlepšovala, ale zhoršovala**, protože svedla k heslům tam, kde se má vysvětlovat.

## Dvě záchytné volby a co znamenají

Za věcnými variantami stojí vždy tytéž dvě volby, v tomhle pořadí a s tímhle pojmenováním:

| Volba | Co se stane | Stav |
|---|---|---|
| **Neopravovat** | zeptej se na důvod a zapiš ho do kapitoly `## Review` (u `/consistency` `## Consistency`) v projektovém `CLAUDE.md`; umlčení vyprší změnou kódu, kterého se týká | zamítnuto |
| **Zapsat do todo** | zapiš do `docs/todo.md` i s úvahou a doložením, ať se na to dá navázat bez téhle session | odloženo |

**Popisek říká, co se stane** (`~/Dev/context/text/copy.md`, *Popisky akcí*). Proto ne *Přeskočit* – to se čte jako „teď ne“, přestože to znamená natrvalo a se zápisem –, a ne *Nechat být* ani *Vrátit se k tomu později*, které mlčí o tom, že se nález někam zapíše. Sjednoceno 28. 9. 2026; do té doby měly kontrolní skilly tři různé slovníky pro tytéž dva konce.

**Věcné varianty jsou nejvýš dvě.** Tool má strop čtyři volby a dvě z nich patří záchytným. Je-li rozumných cest víc, vyber dvě nejsilnější a ostatní zmiň v `Kontextu`. U hromadného nálezu smí jednu záchytnou volbu nahradit **Rozbalit** (vypíšu všechny lokace a projdeme je jednotlivě).

**`header` má napříč skilly týž tvar:** `Nález N/celkem`, u položky, která nálezem není, `Položka N/celkem`.

**Výjimka pro položku, která není vadou, ale novou prací** – tam se neopravuje, takže *Neopravovat* nedává smysl a platí čtveřice *Vyřešit teď / Zapsat do todo / Zapsat do backlogu / Zahodit*. Používá ji `/cleanup` u položek mimo rozsah a `/evaluate` u vyžádaných funkcí; podmínku, kdy je legitimní, drží *Volby v otázce jsou varianty řešení* výš.

## Přehled na začátku vyčísluje obojí

**Kolik se opraví rovnou a kolik doopravdy zbývá na rozhodnutí** – to druhé číslo je jediné, které uživateli říká, jak dlouhý bude interaktivní průchod. Report, který vypíše „mechanických 12, sporných 40“ a pak se u třiceti z těch čtyřiceti nemá na co ptát, to číslo nadsazuje a průchod působí dráž, než je.

## Ohlášená akce patří do téže odpovědi

**Přehled nálezů není konec odpovědi** (`~/.claude/RULES.md`, *Co ohlásíš, udělej hned v téže odpovědi*). Vypsal-li jsi, že se N nálezů opraví rovnou a M zbývá na rozhodnutí, **pokračuj hned v téže odpovědi**: oprav, co se opravuje bez ptaní, vypiš to, a rovnou polož první otázku na sporné. Věta „pouštím se do oprav bez ptaní“ místo oprav samotných je přesně to, co pravidlo zakazuje – běh se o ni prodlouží o jednu odpověď uživatele a nic se za ni neudělá.

## Kdo ji používá

`/review`, `/consistency`, `/attack`, `/audit`, `/evaluate`, `/cleanup` a `/consolidate` – `/evaluate` u poznatků z provozu, kde zvlášť platí výjimka o nové práci, protože vyžádaná funkce není vada; `/cleanup` u položek mimo rozsah i u nálezů čtenářů, kde platí táž hranice jako u vlastních nálezů; `/consolidate` u vedlejších vad od ověřovatelů, a **u svých návrhů taky podle výjimky o nové práci** – dnešní řešení funguje, takže *Neopravovat* u něj nedává smysl a „jestli a kdy“ je doopravdy rozhodnutí uživatele. `/oponent` se k ní hlásí taky, i když ji dodržoval odjakživa: jeho volby jsou varianty řešení už od začátku.

**Skill si nad tímhle kritériem podává vlastní doménové čtení** – `/attack` má sporných skoro všechno, protože každý jeho nález mění chování běžící aplikace, kdežto `/consistency` má většinu jednoznačnou, protože srovnává dvě místa, z nichž jedno je zdroj. **Stavět vlastní hranici vedle téhle se ale nesmí**; přibude-li další skill, který nálezy opravuje, odkáže sem taky a **neopisuje si ji** (`~/.claude/RULES.md`, *Single source of truth*).

**Výjimka pro zadání subagentů:** text, který jde agentovi bez kontextu session, si potřebné části **opisuje celé**, protože odkaz do souboru, který nemá načtený, je mrtvý. Platí to jen na zadání, ne na tělo skillu – a u tohohle kritéria to bude potřeba zřídka, protože rozhoduje hlavní session, ne agent.

## Proč to vzniklo

**Zadal uživatel 20. 9. 2026** uprostřed `/consistency full`, po jedenácti otázkách, ze kterých ani jedna nenabízela volbu: *„když jsou ty opravy takhle jednoznačné a není se mezi čím rozhodovat (a dáváš mi stejně jen na výběr, jestli opravit hned nebo opravit později nebo se na to vykašlat a nechat to špatně), tak se mě ani neptej a hned to všechno oprav“*. Ze 37 nálezů označených za sporné jich 18 po té větě padlo bez jediné otázky.

**Chyba byla v ose, ne v pečlivosti.** Dosavadní kritérium znělo „je oprava bezriziková a nemění chování?“, což je otázka o **zásahu**. Ptát se má ale podle toho, jestli existuje **volba** – a ta dvě kritéria se rozcházejí přesně u nálezů, které něco mění a přitom je jasné jak. Těch je v dokumentačním projektu většina.
