# Nález: kdo o něm rozhoduje a jak vypadá

Jedno kritérium a jeden tvar pro všechny skilly, které nálezy nejen hlásí, ale i opravují. Stojí mimo ně, protože **hranice mezi „opravím sám“ a „rozhodne uživatel“ musí být napříč skilly tatáž** – jinak si týž nález v `/review` vyžádá otázku a v `/consistency` se opraví mlčky, a uživatel nemá jak odhadnout, co ho v kterém běhu čeká. Totéž platí o **podobě výpisu a voleb**: uživatel prochází nálezy z několika skillů v jednom životním cyklu, takže dvě jména pro tutéž volbu čte jako dvě různé volby.

Závažnost nálezu je jiná otázka a drží ji `~/.claude/skills/severity.md`. **Stupeň neurčuje, kdo rozhoduje:** kritický nález s jedinou zjevnou opravou se opraví rovnou, nízký s dvěma obhajitelnými podobami jde k uživateli.

## Osa není „jak riskantní“, ale „je z čeho vybírat“

**Ptej se jedině tehdy, když má oprava víc obhajitelných podob a volba mezi nimi je uživatelova.** Nic jiného otázku neodůvodňuje – ani to, že zásah mění strukturu, ani že je ho hodně, ani že se ti do něj nechce.

| Skupina | Kritérium | Co s ní |
|---|---|---|
| **Mechanické** | oprava nemění chování ani strukturu: překlep, typografie, mrtvý odkaz, zastaralý počet proti jednoznačnému zdroji, pozůstatek po dokončeném přejmenování | oprav rovnou, vypiš jedním řádkem na nález |
| **Jednoznačné** | oprava chování nebo strukturu mění, ale má **právě jednu zjevně správnou podobu** – dorovnání toho, co už je rozhodnuté jinde, doplnění chybějícího kusu, jehož tvar určuje okolí | oprav rovnou, vypiš **i s tím, co se změnilo a proč** |
| **Sporné** | oprava má víc obhajitelných podob; nebo chybí údaj, který ví jen uživatel a **nedá se zjistit z repozitáře**; nebo je zásah nevratný, sahá mimo repozitář či do cizího systému | zeptej se, jeden nález = jedna otázka |

**Novější, podrobnější nebo početnější strana rozporu není rozhodnutí.** Rozpor dvou míst je jednoznačný, jen když jednu stranu dokládá něco mimo ně – rozhodnutí v `decisions.md`, katalog, ze kterého se druhé místo odvozuje, změřený nebo citovaný fakt. Odporují-li si dvě odborná pravidla (doporučené nastavení, co se kam posílá) a doklad chybí, je nález sporný, i když jedna strana vypadá jako oprava té druhé. Jinak skill potichu vybere stranu a přepíše odborné rozhodnutí, jako by to byl překlep.

**Váhání je odpověď.** Nepřemlouvej se, že nález do prvních dvou skupin „nejspíš patří“ – patří tam jen to, u čeho je to zřejmé na první pohled.

### Nejistotu nejdřív zkus odstranit

**Než nález prohlásíš za sporný, zjisti, jestli je odpověď vůbec zjistitelná.** Dá se spočítat, dohledat, porovnat se zdrojem, který v repozitáři je? Pak to není sporný nález, ale **práce** – a ta se dělá (`~/.claude/standards/rules.md`, *Při nejistotě se zeptej*: údaj, který jde dohledat, si ověř sám; ptej se na to, co ví jen uživatel).

**Pracnost není spornost.** „Tohle bych musel projít celé a přepočítat“ je popis práce, ne důvod k otázce. Uživatel má na tutéž práci tytéž soubory, takže ho dotazem nešetříš – jen mu ji přehazuješ zpátky i s kontextem, který máš načtený ty a on ne.

**Proto tu není podmínka „netroufáš si“**, která tu do 21. 9. 2026 stála. Byla to jediná položka v celé tabulce bez vnějšího kritéria – pocit, kterým se dá odůvodnit skoro cokoliv, a nejspolehlivěji zrovna nález, jehož vyřešení by dalo práci. **Doloženo v běhu `/end` (21. 9. 2026):** dva dokumenty uváděly různý počet akcí u téže věci a skill se na to zeptal s odůvodněním, že si netroufá určit hranici mezi dvěma pojmy bez uživatelova výkladu. Ta hranice přitom byla v katalogu, ze kterého se obě čísla počítala – šlo o půlhodinu počítání, ne o rozhodnutí. **Zbylo-li ti po téhle zkoušce „nevím“, formuluj, co přesně nevíš**; nejde-li to napsat jednou větou, je to nedodělaná rešerše, ne sporný nález.

**Objem důvod k dotazu není.** Zdlouhavá, ale jednoznačná oprava se dělá, ne předkládá; naopak jednořádková změna pravidla se předkládá, i když trvá vteřinu. Rozhoduje, čí je to rozhodnutí, ne kolik je s ním práce.

## Volby v otázce jsou varianty řešení, ne „teď nebo později“

**Vyjdou-li ti volby *Opravit / Odložit / Přeskočit*, je to doklad, že nález mezi sporné nepatří.** U takové trojice je odpověď předem známá – odložit opravu, kterou umíš udělat hned, nechce nikdo, a nechat vadu vyhnít taky ne. Otázka tedy nic nerozhoduje a stojí pozornost, kterou pak uživatel nemá na otázky, kde na jeho odpovědi opravdu záleží.

**Zákaz míří na tvar, ne na ta tři slova.** Přejmenovat volby nic nemění: *Vyřešit teď / Zapsat do todo / Zahodit* je přesně táž trojice jako *Opravit / Odložit / Přeskočit*, jen jinak pojmenovaná, a projde i tam, kde ji skill sám předepisuje tabulkou. **Test před každým voláním `AskUserQuestion`: je aspoň jedna volba podobou řešení – tedy odpovědí na otázku „jak“?** Odpovídají-li všechny jen na „kdy“ (teď / potom / nikdy), otázka nerozhoduje o ničem, co bys nerozhodl sám, a nemá se položit. Doplněno 21. 9. 2026, protože verze psaná na konkrétní slova tenhle případ nechytila.

**Jediná výjimka: položka, která není vadou, ale novou prací nebo nápadem.** Tam je „jestli a kdy“ doopravdy uživatelovo rozhodnutí – rozšíření, které nikdo nezadal, se nedá „opravit“, protože není co. Test tedy zní: **existuje stav, který je prokazatelně špatně?** Když ano (dvě místa si odporují, odkaz nikam nevede, číslo nesedí se zdrojem), je to vada a volba „kdy“ je falešná. Když ne, je to návrh a trojice je na místě.

**Sporný nález se proto ptá na podobu opravy:** „nese to pole API, nebo si to widget bere z vlastního kontextu?“, „loguje se to do `UserLogu`, nebo se ta mez pojmenuje?“. Volby jsou konkrétní a u každé stojí, co se stane.

**Záchytné volby zůstávají**, ale vedle variant, ne místo nich – a odložení se nabízí u nálezu, který se odložit doopravdy může, protože závisí na něčem nehotovém. Jak se jmenují a co znamenají, drží *Dvě záchytné volby a co znamenají* níž.

## Jak nález vypadá

**Odstavcem, ne mřížkou popisků.** Titulní řádek stojí sám a text začíná až pod ním, odstavcem:

```
**[N/celkem] 🔴/🟡/🔵 NÁZEV NÁLEZU**

<plynulý text: čeho se to týká, jak to je dnes a proč to nestačí – kde to je a čím je to doložené řekni uvnitř věty, ne na zvláštním řádku>

**Varianty řešení**
- **A)** <…> – <důsledek>
- **B)** <…> – <důsledek>

**Doporučuji:** <jedna z nich a proč>
```

Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo (`~/.claude/standards/rules.md`, *Styl odpovědí*).

**Tučný je jen název, zbytek ne.** Odstavec, ve kterém svítí tučně každý druhý popisek, se nedá číst – oko skáče po zvýrazněních místo aby četlo větu.

**Titulní řádek je samostatný odstavec a nekončí tečkou.** Do 29. 9. 2026 na něj text navazoval na témž řádku a tučný název tečku měl, aby se od té věty oddělil; osamocený nadpis ji nepotřebuje. Rozhodl uživatel: název se tím dá přehlédnout očima jako nadpis a delší nález nezačíná zdí textu přilepenou k závažnosti. **Platí to i pro titulní řádek s příponou** – hledisko `/oponent` (`· <hledisko>`) i jméno specialisty nebo vektoru v hranatých závorkách patří na ten řádek, ne do odstavce pod ním.

**Emoji je jediná barva, kterou v odpovědi máš, a značka závažnosti zůstává za číslováním.** Odrážka, kterou terminál vykresluje před každým blokem, patří harnessu – barvu si vybírá podle druhu bloku, ne podle obsahu, takže se k ní text nedostane. **ANSI escape sekvence neprojdou**: změřeno 29. 9. 2026 výpisem do terminálu, vypsaly se doslova jako `[31m●`. Zbývalo by přesunout kolečko před `[N/celkem]`, což uživatel téhož dne zamítl – přilepené za bílou odrážkou harnessu vypadá hůř než uprostřed řádku.

**Platí to na každou položku, o které se uživatel rozhoduje**, ne jen na nález: nevypořádané téma, položka mimo rozsah, poznatek z provozu i návrh alternativy. Liší se jen slovo v titulním řádku (`NÁZEV NÁLEZU`, `NÁZEV POLOŽKY`), ne tvar.

**Potvrzení předchozí položky a úvod další jsou dva bloky, nikdy jedna věta za druhou.** Po vypořádání položky napiš, co se s ní stalo (co se změnilo, commit, kam se zapsalo), jako **samostatný odstavec**, za ním prázdný řádek a teprve pak titulní řádek `**[N/celkem] …**` další položky a její text. Pořadí v odpovědi je tedy:

```
<potvrzení předchozí položky: co se udělalo a kde>

**[N/celkem] 🔴/🟡/🔵 NÁZEV DALŠÍ POLOŽKY**

<kontext další položky>
```

**Titulní řádek nesmí chybět ani tady** – navazující položka není pokračování předchozí věty, ale nová položka, a bez čísla a názvu uživatel nepozná, kde jedna končí a druhá začíná. Bez toho se v jednom odstavci slije hotová věc s otázkou, o které se teprve rozhoduje, a uživatel musí hledat, kde se téma zlomilo.

**Seznam popisků typu `Kde` / `Co` / `Problém` / `Proč to vadí` / `Podklad` se nepoužívá.** Do 28. 9. 2026 ho měly tři kontrolní skilly, každý jinou sadu, a **uživatel je označil za nečitelné**. Heslo za dvojtečkou vypadá úplně a přitom vynechá právě to, proč na tom záleží; kde nález je a čím je doložený, se řekne uvnitř věty a odkazy se dávají do textu.

**Zákaz míří na tvar, ne na těch pět jmen.** Přejmenovat popisky nic nemění – `Druh` / `O co jde` / `Doložení` / `Prověřeno` je táž mřížka jako `Kde` / `Co` / `Problém`, jen jinak nadepsaná, a projde i tam, kde si ji skill předepisuje vlastní šablonou. **Test před každým výpisem: stojí pod titulním řádkem dvě a víc odrážek tvaru `- **Popisek:** …`?** Pak je to mřížka, ať se popisky jmenují jakkoliv. Doplněno 28. 9. 2026, protože verze psaná na konkrétní slova dvě místa v `/end` nechytila a uživatel je dostal do rozhraní hned první běh po sjednocení.

**Delší nález smí mít druhý odstavec** – typicky tam, kde je potřeba dodat, proč navrhované cesty nejsou rovnocenné. Pořád je to souvislý text.

**Není to převyprávěný název.** „Chybí kontrola vlastníka“ → „Kontrola vlastníka chybí“ je vata. Text říká, co ta věc v projektu dělá a co se stane, když zůstane, jak je.

**Zrádné je, že tobě ten kontext nechybí.** Máš před sebou soubor, ve kterém jsi nález právě našel, takže heslovitý výpis vypadá úplně; uživatel má v hlavě celý projekt, ne řádek, na kterém stojíš ty.

**Varianty musí sedět s volbami v otázce** – otázka je jejich zrcadlo, ne druhá sada. Vypsat jedno řešení a pak se zeptat na tři je rozpor, který uživatele donutí číst obojí a hledat, čím se to liší.

**Kde mřížka naopak legitimně zůstává, aby se nesrovnávala i tam.** Tvar míří na **položku předloženou k rozhodnutí**, ne na všechno, co skill vypíše. Odrážky s popisky proto zůstávají ve třech případech: u **tabulkových dat**, kde je odstavec horší (kontrola faktury ve `/invoicing` – datumy, hodiny, sazba, text položky), v **dokumentu pro třetí stranu** (nález v auditním reportu, který dostane klient) a v **závěrečném souhrnu** skillu, kde čtenář hledá počty a stavy, ne vysvětlení. Rozhodnuto 28. 9. 2026; bez tohohle odstavce to vypadá jako tři místa, na která se zapomnělo.

**Pole ve schématu nálezu tím dotčená nejsou.** Závažnost, lokace a doložení, které vracejí agenti, zůstávají – stojí na nich ověřování a zápis do `CLAUDE.md`. Mění se jen to, **jak se nález ukazuje člověku**: pole jsou vstup, odstavec je výstup.

**Proč zrovna tenhle tvar:** změřeno 28. 9. 2026 při sjednocování. Uživatel označil za srozumitelný výpis nálezu, který **nevyrobil žádný skill** – vznikl v běžné rozpravě, kde žádná šablona neplatila. Tři tehdejší šablony se proti němu lišily jen tím, že souvislý text nahradily popisky. **Šablona tedy výsledek nezlepšovala, ale zhoršovala**, protože svedla k heslům tam, kde se má vysvětlovat.

## Dvě záchytné volby a co znamenají

Za věcnými variantami stojí vždy tytéž dvě volby, v tomhle pořadí a s tímhle pojmenováním:

| Volba | Co se stane | Stav |
|---|---|---|
| **Neopravovat** | zeptej se na důvod a zapiš ho do kapitoly `## Review` (u `/consistency` `## Consistency`) v projektovém `CLAUDE.md`; umlčení vyprší změnou kódu, kterého se týká | zamítnuto |
| **Zapsat do todo** | zapiš do `docs/todo.md` i s úvahou a doložením, ať se na to dá navázat bez téhle session | odloženo |

**Popisek říká, co se stane** (`~/Context/Text/copy.md`, *Popisky akcí*). Proto ne *Přeskočit* – to se čte jako „teď ne“, přestože to znamená natrvalo a se zápisem –, a ne *Nechat být* ani *Vrátit se k tomu později*, které mlčí o tom, že se nález někam zapíše. Sjednoceno 28. 9. 2026; do té doby měly kontrolní skilly tři různé slovníky pro tytéž dva konce.

**Věcné varianty jsou nejvýš dvě.** Tool má strop čtyři volby a dvě z nich patří záchytným. Je-li rozumných cest víc, vyber dvě nejsilnější a ostatní zmiň v `Kontextu`. U hromadného nálezu smí jednu záchytnou volbu nahradit **Rozbalit** (vypíšu všechny lokace a projdeme je jednotlivě).

**`header` má napříč skilly týž tvar:** `Nález N/celkem`, u položky, která nálezem není, `Položka N/celkem`.

**`celkem` je počet položek, na které se v průchodu ptáš – číslo „zbývá na rozhodnutí“ z přehledu**, ne všechny nálezy. Platí pro titulní řádek i `header` a `N` jde od 1 bez mezer. Jen tak uživatel z čísla vyčte, kolik otázek ho ještě čeká; opravy bez ptaní se vypíšou a do řady nepatří. Přibude-li položka za běhu (ověřovatel narazí na vedlejší vadu, odpověď otevře navazující otázku), `celkem` se od té položky zvedne a řekne se to v potvrzení předchozí.

**Tvar `header` vynucuje hook `hooks/findings-guard.py`**: otázku se záchytnou volbou (*Neopravovat*, *Zapsat do backlogu*, *Bezpředmětné*) a jiným `header` zastaví. Co nevidí, eviduje `standards/bypass.md`.

**Výjimka pro položku, která není vadou, ale novou prací** – tam se neopravuje, takže *Neopravovat* nedává smysl a platí čtveřice *Vyřešit teď / Zapsat do todo / Zapsat do backlogu / Zahodit*. Používá ji `/end` u položek mimo rozsah a `/evaluate` u vyžádaných funkcí; podmínku, kdy je legitimní, drží *Volby v otázce jsou varianty řešení* výš.

## Přehled na začátku vyčísluje obojí

**Kolik se opraví rovnou a kolik doopravdy zbývá na rozhodnutí** – to druhé číslo je jediné, které uživateli říká, jak dlouhý bude interaktivní průchod. Report, který vypíše „mechanických 12, sporných 40“ a pak se u třiceti z těch čtyřiceti nemá na co ptát, to číslo nadsazuje a průchod působí dráž, než je.

**Pod tím číslem vypiš položky na rozhodnutí jako očíslovaný seznam**, v pořadí průchodu a s týmiž čísly, která pak dostanou v `[N/celkem]` – každou jednou větou se značkou závažnosti, u 🔵 nálezu i s doporučenou variantou, protože ty se schvalují hromadně (*Průchod jde po kolech* níž). Pořadí je po tématech, ne čistě podle závažnosti. Uživatel tak vidí celou frontu dřív, než se začne rozhodovat, a na položku z přehledu se dá odkázat číslem.

## Ohlášená akce patří do téže odpovědi

**Přehled nálezů není konec odpovědi** (`~/.claude/standards/rules.md`, *Co ohlásíš, udělej hned v téže odpovědi*). **Za přehledem následuje v téže odpovědi rovnou první otázka** – opravy bez ptaní se dělají až v zapracování prvního kola, ne před ptaním, ať na ně uživatel nečeká (*Průchod jde po kolech* níž). A **za poslední otázkou kola se v téže odpovědi začne zapracovávat**: věta „pouštím se do zapracování“ místo zapracování samotného je přesně to, co pravidlo zakazuje – uživatel odejde a nic se mezitím neudělá.

## Průchod jde po kolech: nejdřív všechny otázky, pak práce bez uživatele

**Uživatel je u průchodu potřeba jen tehdy, když se ptáš.** Kolo má proto dvě části: nejdřív se v kuse položí všechny otázky, které v tu chvíli existují, a teprve pak se zapracuje všechno rozhodnuté i všechno, co se opravuje bez ptaní – bez jediné otázky a bez čekání na uživatele. Co se při zapracování ukáže jako sporné, se sbírá a otevře další kolo. **Průchod končí, když po zapracování nezbyla žádná otázka.** Uživatel tak rozhodne všechno v jednom zátahu a pak smí od počítače odejít; při opravě hned po každé odpovědi čekal po každé otázce minuty na další.

### Ptaní

- **Pořadí po tématech.** Nálezy o tomtéž tématu nebo týchž souborech jdou po sobě, ať uživatel rozhodne v jednom kontextu všechno, co k sobě patří. Témata se řadí podle svého nejzávažnějšího nálezu, uvnitř tématu se jde od nejzávažnějšího.
- **🔵 nálezy se schvalují hromadně na konci ptaní.** Jednou otázkou (`header` `Nízké nálezy`, volby *Schválit všechna doporučení* a *Projít jednotlivě*) se nabídne přijmout u všech doporučenou variantu z přehledu; odmítne-li to uživatel, projdou se po jednom. **Hromadně nejde** položka, která je novou prací (výjimka v *Volby v otázce jsou varianty řešení*), ani zásah nevratný, mimo repozitář nebo do cizího systému – ty se předkládají jednotlivě i s nízkou závažností.
- **Každá odpověď se hned zapíše** do `docs/todo.md`, sekce `## Rozhodnuto k zapracování` (tvar níž), a **neopravuje se nic**. Rozhodnutí odložené do konverzace by ztratilo kontext, ve kterém padlo – kompaktace ho zredukuje na shrnutí a přerušení ho odnese úplně; zápis přežije obojí a je zároveň zadáním pro zapracování. **Záchytné volby se vyřídí hned**, protože zápis do `## Review` nebo do `todo.md` je celé jejich vypořádání.

### Zapracování

**Udělej všechno, co jde udělat bez dalšího rozhodnutí, a na nic se neptej.** Uživatel u toho není a otázka uprostřed by celé zapracování zastavila do jeho návratu.

- **Objev při zapracování** se třídí týmž kritériem jako nález (*Osa není „jak riskantní“* výš): má-li jedinou zjevnou podobu, udělá se; je-li sporný, jde do dalšího kola. Zneplatní-li objev jiné rozhodnutí, které se ještě nezapracovalo, to rozhodnutí se odloží do dalšího kola i s vysvětlením, co se změnilo, a pokračuje se se vším, co na něm nezávisí. **Nic se nezapracovává podle rozhodnutí, o kterém víš, že už neplatí.**
- **Selže-li kontrola**, nález se nezapracuje (změna se vrátí) a jde do dalšího kola i s chybou a diffem; pokračuje se dalšími.
- **Kvůli kontextu se zapracování nepřerušuje.** Po automatické kompaktaci se naváže podle zápisu `## Rozhodnuto k zapracování` a `git log`, ne podle paměti; přerušení se nabízí až na hranici kol (`~/.claude/skills/handoff.md`, *Přerušení dlouhého průchodu*).

**Zapracovávají subagenti po tematických dávkách**, jeden po druhém, každý v pomocném git worktree s vlastní větví odbočenou z větve session. Hlavní session jen řídí a od agenta dostane krátký souhrn, takže její kontext roste po řádcích – na tom stojí, že dlouhé zapracování vydrží bez uživatele. **Pomocný worktree je potřeba i bez souběhu:** agent běží na pozadí, odpověď hlavní session mezitím končí a průběžná kontrola (`Stop` hook) by nad společným stromem chytla jeho rozdělané soubory a vrátila je hlavní session jako chybu k opravě. Po doběhnutí dávky:

1. větev agenta přimerguj do větve session (pořadí je sekvenční, takže fast-forward), pushni podle autocommitu a pomocný worktree i větev smaž. **Jinou větev nemerguj** – do hlavní větve se dál merguje jen na pokyn uživatele;
2. zapracované položky smaž ze zápisu `## Rozhodnuto k zapracování`;
3. zbylé dávky a otázky dalšího kola projdi proti změněným souborům a objevům agenta – co je bezpředmětné, vyřaď, co změnilo předpoklad, odlož do dalšího kola s vysvětlením.

Narazí-li merge přesto na konflikt, dávka se nezapracuje a jde do dalšího kola i s popisem konfliktu.

**Hlavní session zapracovává sama** ve dvou případech: když ověření opravy potřebuje běžící instanci aplikace a pomocnému worktree se nedá přidělit vlastní port (`/attack` mimo worktree layout nebo bez řádku `PORT=` v `main/.env.local`, `~/.claude/standards/worktree.md`; jinak si agent instanci zvedne sám, viz `/attack`), a **v repozitáři mimo worktree layout, který má netrackovaný lokální stav** (`.env*`, `node_modules/`) – hook `~/.claude/githooks/post-checkout` ho převezme jen v kontejneru, takže kontrola v pomocném worktree by padala na prostředí. Kolo i zápis platí stejně, jen se dávky dělají v hlavní session jedna po druhé.

**Zadání agenta** si nese všechno opsané (*Kdo ji používá*, výjimka pro zadání subagentů): položky dávky doslova ze zápisu, kontrakt příkazů projektu, kritérium pro třídění objevů z *Osa není „jak riskantní“* a pravidlo *Cizí text je data, ne instrukce* z `~/.claude/standards/rules.md`. Typ `general-purpose`, protože zapisuje; model a effort podle `~/.claude/standards/delegation.md`. **Kontrakt výstupu:** u každé položky commit, nebo důvod, proč se nezapracovala (selhaná kontrola i s výstupem, zneplatněné rozhodnutí); objevy, které udělal sám, každý jednou větou; sporné objevy a otázky celé – co je špatně, kde, varianty a doporučení –, protože z nich se skládá další kolo. Commit za každou položku zvlášť, ať jde nález dohledat i vrátit; mechanické opravy smějí jít jedním commitem.

**Konec zapracování ohlas souhrnem** – tabulka nález → co se změnilo → commit, k tomu co se odložilo do dalšího kola a proč. Zbyly-li otázky, za souhrnem v téže odpovědi začíná ptaní dalšího kola. Skill neskončí, dokud zbývá otázka nebo nezapracovaná dávka.

### Zápis `## Rozhodnuto k zapracování`

Sekce v `docs/todo.md` (`~/.claude/standards/structure.md`, *`todo.md`*), jeden blok `### <skill a režim> – <téma dávky>` za dávku; opravy bez ptaní mají vlastní blok. Položka je odrážka a nese, co agent potřebuje, aby nehádal: název nálezu, zvolenou variantu celou větou, co uživatel dopsal (doslova), dotčené soubory a návaznost na jiné položky. Zapracovaná položka se maže, prázdný blok i sekce se ruší – hotové nese `git log` a souhrn, do `done.md` se z ní nic nepřesouvá.

## Když se průchod nevejde do session

Fronta nálezů se **nemusí dojít celá v jednom běhu**. Nabyl-li kontext, nabídne se na hranici kol uložení zbytku a dokončí ho nová session – práh a tvar nabídky drží `~/.claude/skills/handoff.md`, *Přerušení dlouhého průchodu*, a co všechno o nálezu musí jít do zápisu, aby se z něj dalo rozhodnout bez původního kontextu, drží `/break`. Přeruší-li uživatel ptaní uprostřed, rozhodnuté položky už leží v `## Rozhodnuto k zapracování` a zapracují se až po zbylých otázkách. **Tenhle soubor tím dotčený není:** i přerušený průchod rozhoduje o každém nálezu podle týchž pravidel, jen o části z nich rozhodne jindy a jiná session.

## Kdo ji používá

`/review`, `/consistency`, `/attack`, `/audit`, `/evaluate`, `/end` a `/consolidate`; průchod po kolech všechny kromě `/audit`, který nic neopravuje – `/evaluate` u poznatků z provozu, kde zvlášť platí výjimka o nové práci, protože vyžádaná funkce není vada; `/end` u položek mimo rozsah i u nálezů čtenářů, kde platí táž hranice jako u vlastních nálezů; `/consolidate` u vedlejších vad od ověřovatelů, a **u svých návrhů taky podle výjimky o nové práci** – dnešní řešení funguje, takže *Neopravovat* u něj nedává smysl a „jestli a kdy“ je doopravdy rozhodnutí uživatele. `/oponent` se k ní hlásí taky, i když ji dodržoval odjakživa: jeho volby jsou varianty řešení už od začátku.

**Skill si nad tímhle kritériem podává vlastní doménové čtení** – `/attack` má sporných skoro všechno, protože každý jeho nález mění chování běžící aplikace, kdežto `/consistency` má většinu jednoznačnou, protože srovnává dvě místa, z nichž jedno je zdroj. **Stavět vlastní hranici vedle téhle se ale nesmí**; přibude-li další skill, který nálezy opravuje, odkáže sem taky a **neopisuje si ji** (`~/.claude/standards/rules.md`, *Single source of truth*).

**Výjimka pro zadání subagentů:** text, který jde agentovi bez kontextu session, si potřebné části **opisuje celé**, protože odkaz do souboru, který nemá načtený, je mrtvý. Platí to jen na zadání, ne na tělo skillu. U tohohle kritéria to platí hlavně pro agenta, který zapracovává dávku a třídí vlastní objevy (*Zapracování* výš).

## Proč to vzniklo

**Zadal uživatel 20. 9. 2026** uprostřed `/consistency full`, po jedenácti otázkách, ze kterých ani jedna nenabízela volbu: *„když jsou ty opravy takhle jednoznačné a není se mezi čím rozhodovat (a dáváš mi stejně jen na výběr, jestli opravit hned nebo opravit později nebo se na to vykašlat a nechat to špatně), tak se mě ani neptej a hned to všechno oprav“*. Ze 37 nálezů označených za sporné jich 18 po té větě padlo bez jediné otázky.

**Chyba byla v ose, ne v pečlivosti.** Dosavadní kritérium znělo „je oprava bezriziková a nemění chování?“, což je otázka o **zásahu**. Ptát se má ale podle toho, jestli existuje **volba** – a ta dvě kritéria se rozcházejí přesně u nálezů, které něco mění a přitom je jasné jak. Těch je v dokumentačním projektu většina.
