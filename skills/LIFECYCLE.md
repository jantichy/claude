# Životní cyklus projektu

Od nápadu k nasazené feature vede jeden životní cyklus. Tenhle soubor drží **rozhraní jeho kroků**: co který krok dělá, co po něm platí, proč stojí zrovna v tom pořadí a co u něj rozhoduje o přeskočení. Obecné pravidlo *kdy se krok přeskakuje* drží `~/.claude/RULES.md` – platí i mimo cyklus, takže musí stát v paušálním kontextu. Vnitřek kroku – jeho fáze, šablony, zadání pro agenty – sem nepatří ani zmínkou; ten drží příslušný skill.

**Neimportuje se paušálně.** Načti si ho, když stojíš v některém kroku cyklu nebo když rozhoduješ, který krok přijde na řadu. Rámeček s pořadím a pravidlo o přeskakování jsou v `~/.claude/RULES.md`, *Životní cyklus projektu* – tolik stačí každé session, zbytek potřebuje jen ten, kdo cyklus zrovna vede.

**Proč to nestojí v jednotlivých skillech:** každý zná jen svoje sousedy, takže celé pořadí by v nich nikdo nenašel. A proč to nestojí v `RULES.md`: je to deset kilobajtů, které se jinak načítají do každé session v každém projektu, i tam, kde se žádný krok cyklu nepouští.

------

## Kroky a jejich pořadí

Rámeček s celým pořadím drží `~/.claude/RULES.md`, *Životní cyklus projektu*, a je zdrojem pravdy – tady stojí, **co ty kroky dělají**. Rozejde-li se jedno s druhým, platí `RULES.md`.

**Proč v tomhle pořadí:** každý krok vyrábí vstup pro další, obráceně bys uklízel nad stavem, který se ještě změní. Korektnost jde před soulad s předpisem, protože oprava korektnosti přepisuje strukturu a zahodila by povrchové úpravy – proto jsou obě uvnitř jednoho `/review`, kde se pořadí řídí samo. A `/cleanup` je poslední i proto, že jako jediný odolá kompaktaci.

Uvnitř `/implement` běží u **každého úkolu** vlastní smyčka: test → kód → průběžná kontrola → commit. (Je to rozhraní kroku, ne jeho vnitřek: určuje, co po `/implement` platí o stavu repozitáře, a tím i s čím počítá `/review`.)

V životním cyklu smí stát **vlastní skilly a vestavěné skilly Claude Code** – u obojího je rozhraní stabilní. **Externí skilly z pluginů** (`superpowers:*` a podobné) v životním cyklu nikdy nestojí; krok si je volá jako svůj vnitřek. Ten se může kdykoliv změnit, aniž se změní, jak se krok volá.

**Zakládání (1–6)**

1. **`/project`** – u nového projektu, nebo když je potřeba dorovnat nastavení stávajícího. **Volá se znovu i nad dávno nastaveným projektem, kdykoliv se posunuly standardy nebo konfigurační vrstva** – pozná podle bloku metadat, že už jednou běžel, a místo ptání projde projekt proti dnešní podobě standardu. Projekt bez toho otisku projde nejdřív průvodcem a revizi dostane na jeho konci. Musí být první: bez založených souborů není kam průběžně zapisovat rozhodnutí, a doplňovat je zpětně znamená rekonstruovat je z paměti. Zakládá i *Kontrakt příkazů*. Ten sám o sobě průběžnou kontrolu **nezapne** – hook spouští příkazy jen v repozitáři, pro který člověk vydal souhlas (`~/.claude/verify.sh --allow`), protože kontrakt je kód z repozitáře a hooky se na povolení neptají.
2. **`/discovery`** – podklady o světě venku, ze kterých se pak staví produkt: analýza konkurence a naše pozice proti ní (`docs/competition.md`), registr produktových a tržních rizik s mitigacemi (`docs/risks.md`). **Stojí před `/specify` schválně:** z konkurence vzejde, co produkt musí umět, aby ho někdo vzal, a z rizik to, co v něm musí být jinak – obojí je vstup do specifikace, ne komentář k ní. Sám si na začátku vymezí pole hledání čtyřmi otázkami (jaký problém, komu, v jaké kategorii soutěžíme, čím se to má lišit) a zapíše ho, takže `/specify` se na totéž neptá podruhé. **Je opakovatelný samostatně** – konkurence se hne bez ohledu na to, jestli se právě mění zadání. Přeskakuje se u všeho, co nemá trh: interní nástroj, přírůstek do hotového produktu, projekt pro jednoho klienta na zakázku.
3. **`/specify`** – produktová specifikace (`docs/requirements.md`) a návrh řešení (`docs/architecture.md`), volitelně scénáře (`docs/scenarios.md`), glosář a cenový model. Sám rozhodne, jestli je zadání na specifikaci; když ne, kroky 4 a 5 odpadají, protože bez plánu není co odpracovat.
4. **`/oponent`** – nezávislý posudek zadání čerstvýma očima, subagenty bez kontextu session. **Do životního cyklu patří proto, že jinak návrh neměří nikdo:** specialista na korektnost v `/review` ověřuje kód proti specifikaci, ale samotnou specifikaci nikdo proti ničemu – vada v ní tedy projde celým životním cyklem jako korektní, protože kód poslušně dělá to, co je v ní napsané. Je to zároveň jediná vrstva, kde se chyba násobí do všeho pod ní: `~/Dev/context/coding/quality.md` tvrdí, že *„bezpečnost se dělá strukturou, ne kontrolou na konci“*, a ta struktura vzniká právě tady. Přeskakuje se stejným pravidlem jako každý jiný krok – drobná změna uvnitř navrženého systému posudek nepotřebuje, nový systém nebo nový podsystém ano.
5. **`/breakdown`** – implementační plán (`docs/plan.md`). Až po schválení zadání: plán argumentuje ze specifikace, takže měnit specifikaci pod hotovým plánem znamená plán přepsat. Každý úkol dostane **ověřitelné akceptační kritérium**, ne popis souvislým textem.
6. **`/implement`** – odpracování plánu, úkol po úkolu, každý do průběžné kontroly a do commitu.

**Uzavírání (7–9)**

7. **`/review`** – paralelní panel specialistů nad změnami: korektnost, bezpečnost, data a stavy, provoz, testy a doménové standardy z `~/Dev/context/`. Specialisté se vybírají podle toho, čeho se změny týkají, takže nad obsahovým projektem poběží jen textové. Vlastní skill; uvnitř si volá vestavěné `/code-review` a `/security-review` jako dva ze specialistů.
8. **`/consistency`** – audit vnitřní konzistence. Ptá se „sedí si projekt sám se sebou?“, což je jiná otázka než všichni specialisté v `/review`, a uklidí i to, co nastřílel krok 7. Výchozí rozsah jsou soubory dotčené větví a ty, které na ně odkazují; `full` projede celý projekt a pouští se zřídka – kompletní audit po každé feature znovu předkládá tentýž starý dluh, a umlčet ho je pak levnější než odklikat.
9. **`/cleanup`** – poslední krok **uzavírání**, ne životního cyklu. Ověří, že je všechno dohodnuté zapsané, a doplní, co průběžnému zápisu uniklo – včetně rozhodnutí z uzavíracích kroků (co bylo odmítnuto a proč). Zároveň dohledá témata, která v konverzaci zůstala bez vypořádání – otázku, na kterou se neodpovědělo, návrh, který nikdo nepřijal ani nezamítl –, a probere je s uživatelem, dokud je koho se ptát. Běží-li po něm ještě `/attack` nebo `/release`, ty si své zápisy dělají samy a na konci se `/cleanup` **pouští znovu** – je opakovatelný a druhý průchod slouží jako verifikace.

**Nasazení (10–11)**

10. **`/attack`** – explorativní útok: aplikace se **spustí** a zkouší se rozbít vstupy, pořadím kroků, cizími identitami a nesmyslnými daty. Je to třetí druh záruky vedle deterministických kontrol a posouzení modelem, a ani jedna ho nenahrazuje – `/review` kód čte, tenhle ho spouští. **Stojí až tady schválně:** je drahý a nad rozestavěnou prací by hlásil hlavně nedodělanost, kdežto `/review` je levný a běží po každé feature. Projekt bez spustitelné aplikace ho nemá.
11. **`/release`** – nasazení do produkce. **Stojí mimo uzavírání schválně:** uzavírání mění repozitář, nasazení mění svět, kde jsou cizí data a živí uživatelé. Nikdy se nespouští jako pokračování jiného kroku a vždy se potvrzuje zvlášť. **Končí až uzavřením sledovacího okna**, ne nasazením – viz níž.

## Cyklus nekončí nasazením

`/release` má poslední fází **sledovací okno**: nasazení se nepovažuje za hotové, dokud okno neuplyne a někdo ho výslovně neuzavře větou *„okno uzavřeno, N nových chyb“*. Bez toho se nasazení uzavře tichem a scénář „spadlo to o dvě hodiny později“ – migrace s backfillem, cache, chyba, která se projeví až na produkčním objemu – nemá vlastníka.

## Hotfix

**Jde týmž životním cyklem, jen zkráceně.** Není to jiný postup, ale tentýž s vědomě přeskočenými kroky: `/specify`, `/oponent` a `/breakdown` odpadají (opravuje se to, co je navržené, ne co se navrhuje), `/consistency` a `/attack` taky. **Nepřeskakuje se `/review` ani průběžná kontrola** – oprava dělaná ve spěchu je přesně ten případ, kdy je kontrola nejcennější. Přeskočení se hlásí nahlas i s důvodem, jako u každého jiného kroku.

## Povolená opakování

**Žádný krok neopakuje, co udělal krok před ním.** Každý má v *Co skill nedělá* jmenovitě napsané, čí práci nepřebírá. Duplicita stojí čas i tokeny a hlavně rozmazává odpovědnost: u věci, kterou hlídají tři kroky, ji nakonec neudělá pořádně žádný.

**Test zní: vrací ten krok nad TÝMŽ vstupem tutéž odpověď?** Když ano, je to duplicita. Opakovat se smí jen to, čemu se mezitím **mohl změnit vstup** – stav pracovního stromu, databáze zranitelností, obsah repozitáře. Starší formulace („kdyby ten krok neproběhl, zjistil by to někdo jiný?“) tenhle rozdíl nedělala a označila za duplicitu i případy, které životní cyklus sám obhajuje.

**Povolená opakování jsou čtyři a jmenují se**, aby se seznam nedal rozšiřovat mlčky:

| Co se opakuje | Kde | Co se mezitím mohlo změnit |
|---|---|---|
| průběžná kontrola | `/implement` → `/review` | hook ji vynutil po poslední odpovědi, `/review` ji pouští nad celým rozsahem větve |
| audit závislostí | `/review` → `/release` | databáze zranitelností se mění bez ohledu na projekt |
| scan tajemství | `/review` → `/release` | mezi oběma kroky přibyly commity z `/consistency`, `/cleanup` i `/attack` |
| produkční build | `/review` → `/release` | uzavírání i útok mezitím commitují, a `/release` ho navíc pouští **na čistém stromu** – „prošlo to při uzavírání“ a „projde to jako to, co posíláme ven“ jsou dvě tvrzení |

## Jeden člověk, jedna interaktivní session

Celý životní cyklus je nástroj pro **jednu interaktivní session jednoho člověka**. Je to vědomé omezení, ne opomenutí: skoro celý stojí na `AskUserQuestion` a na souhlasu průběžné kontroly vydaném lokálně pro jednoho uživatele. V CI ani u druhého člověka neplatí ani jedno – hook nespustí nic, protože souhlas je vázaný na `$HOME`, a interaktivní průchod nálezy nemá komu položit otázku.

Prakticky to znamená: **v CI a u spolupracovníka platí z celé soustavy jen deterministická vrstva** – typecheck, lint, test, audit, scan tajemství, statická analýza. Ty běží kdekoliv a nepotřebují nikoho, kdo by odpovídal. Panel specialistů, průchod nálezy, útok ani nasazení se v neinteraktivním prostředí nepouštějí; kdo je chce, pustí je u sebe.
