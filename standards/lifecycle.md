# Životní cyklus projektu

Rozhraní kroků životního cyklu: co který krok dělá, co po něm platí, proč stojí v tom pořadí a co rozhoduje o jeho přeskočení. Načítá se v kroku cyklu nebo při rozhodování, který krok je na řadě. Rámeček s pořadím a obecné pravidlo o přeskakování drží `~/.claude/standards/rules.md`, *Životní cyklus projektu* – je zdrojem pravdy a rozejde-li se s tímhle souborem, platí on. Vnitřek kroku – fáze, šablony, zadání pro agenty – sem nepatří ani zmínkou; drží ho skill. Celé pořadí stojí tady, ne ve skillech, protože každý skill zná jen svoje sousedy. Tvar záznamu, který si kontrolní kroky zapisují do `done.md`, drží `~/.claude/skills/passes.md` – čte ho jen ten, kdo zapisuje nebo z něj čte.

------

## Kroky cyklu a jejich uspořádání

Uvnitř `/implement` běží u **každého úkolu** smyčka test → kód → průběžná kontrola → commit; s tím stavem repozitáře počítá `/review`.

V životním cyklu smí stát **vlastní skilly a vestavěné skilly Claude Code**. **Externí skilly z pluginů** (`superpowers:*` a podobné) v něm nikdy nestojí – krok si je volá jako svůj vnitřek, protože jejich rozhraní se může kdykoliv změnit.

Kontrolní krok není bod v řadě, ale **vrstva mezi dvěma kroky osy** – proto se v cyklu objevuje vícekrát, aniž je to opakování nebo výjimka.

### Hlavní osa – kroky, které tvoří

- **`/project`** – u nového projektu, a **znovu nad dávno nastaveným, kdykoliv se posunuly standardy nebo konfigurační vrstva**. Musí být první: bez založených souborů není kam průběžně zapisovat rozhodnutí. Zakládá i *Kontrakt příkazů*; ten sám průběžnou kontrolu **nezapne** – hook spouští příkazy jen v repozitáři, pro který člověk vydal souhlas (`~/.claude/hooks/verify.sh --allow`).
- **`/discovery`** – **proč se to má stavět**: doklady poptávky s verdiktem (`docs/demand.md`), konkurence a naše pozice proti ní (`docs/competition.md`), produktová a tržní rizika s mitigacemi (`docs/risks.md`). **Hlavní je poptávka** – nedoložená se projeví až jako hotový produkt, který nikdo nepoužívá; **tenhle krok je jediné místo, kde ta otázka zazní**, od `/specify` dál je rozhodnuto stavět. Stojí před `/specify`, protože co produkt musí umět a co v něm musí být jinak, je vstup do specifikace. Problém, jeho nositele, dnešní řešení, kategorii a zamýšlené odlišení zapíše sám, takže `/specify` se na ně neptá podruhé. **Je opakovatelný samostatně.** **Přeskakuje se po dokumentech:** u toho, co nemá trh (interní nástroj, zakázka pro jednoho klienta), odpadá jen konkurence; celý odpadá jen u přírůstku do hotového produktu, kde je „proč“ rozhodnuté a **zapsané**.
- **`/specify`** – požadavky, co stavíme a proč: **jeden dokument** `docs/requirements.md`, volitelně scénáře (`docs/scenarios.md`), glosář a cenový model. Sám rozhodne, jestli je zadání na specifikaci; když ne, odpadá i všechno pod ním.
- **`/architect`** – návrh řešení jako **sada dokumentů**: páteř `docs/architecture.md`, podle potřeby `model.md`, `transitions.md` a tematické dokumenty kol. **Větší záměr dělí na tematická kola uvnitř sebe**, ne jako krok cyklu; `/oponent`, `/review`, `/consistency` a `/cleanup` se nad koly pouštějí podle doporučení v závěru kola a `/breakdown` přichází až po uzavření všech kol nad sešitým celkem. Od `/specify` je oddělený, protože oponovat zadání má smysl dřív, než se podle něj něco postaví: požadavky se sepíšou **jednou na začátku**, návrh vzniká **po tématech**.
- **`/breakdown`** – implementační plán (`docs/plan.md`), až po schválení zadání – změna specifikace pod hotovým plánem znamená plán přepsat. Každý úkol dostane **ověřitelné akceptační kritérium**.
- **`/implement`** – odpracování plánu, úkol po úkolu, každý do průběžné kontroly a do commitu.
- **`/release`** – nasazení do produkce. **Stojí za všemi kontrolami toho, co se nasazuje**, protože ty mění repozitář a nasazení svět; kontrolní kroky za ním uklízejí po vyhodnocení provozu. Je to **poslední krok, který mění svět**. Nikdy se nespouští jako pokračování jiného kroku a vždy se potvrzuje zvlášť. **Končí až uzavřením sledovacího okna** (*Cyklus nekončí nasazením*).
- **`/evaluate`** – vyhodnocení provozu, výstupem `docs/operation.md`. **Spouští ho čas, ne výstup předchozího kroku:** pouští se na pokyn uživatele; `/release` zapíše do `todo.md` datum, kdy to má smysl, a `/next` tu položku v ten den nabídne. **Je to krok osy, protože rozsah práce zvětšuje** – z podkladu vzejde další průchod. **Do `requirements.md` nepropisuje nic** – poznatek je vstup pro `/specify`, ne rozhodnutí. **Přeskakuje se u toho, co provoz nemá** (knihovna, konfigurace, jednorázový skript), a u nenasazené věci; **ne kvůli tomu, že se neměří** – výstupem je pak, co začít měřit.

### Kontrolní kroky – údržba nad tím, co už je

Žádný z nich nezvětšuje rozsah práce – ani `/consolidate`, který jako jediný vrací návrh řešení, ale jen hledá náhradu hotového, ani `/merge`, který jako jediný mění hlavní větev, ale nic nevyrábí.

- **`/oponent`** – nezávislý posudek subagenty bez kontextu session. **Stojí v cyklu třikrát** – po `/discovery`, po `/specify` a po `/architect`; po požadavcích proto, že `/review` měří kód proti specifikaci, ale specifikaci nikdo, a vada v ní se násobí do všeho pod ní. **Přeskakuje se stejným pravidlem jako každý jiný krok** – drobná změna uvnitř navrženého systému posudek nepotřebuje, nový systém nebo podsystém ano.
- **`/consolidate`** – návrhový dluh z postupného záplatování: „bylo by to dnes navržené **jinak**?“ **Jako jediný krok čte historii rozhodnutí**, ne dnešní stav. **V prvním průchodu se přeskakuje** – dluh nabíhá až s druhým a dalším kolem. **Relativizuje řešení, ne zadání.**
- **`/review`** – paralelní panel specialistů nad změnami: korektnost, bezpečnost, data a stavy, provoz a chyby, testy, agentní infrastruktura a doménové znalosti z `~/Dev/context/`. Specialisty vybírá podle toho, čeho se změny týkají.
- **`/consistency`** – „sedí si projekt sám se sebou?“; uklidí i to, co nastřílel `/review`. Výchozí rozsah jsou soubory dotčené větví a ty, které na ně odkazují; `full` se pouští zřídka, protože po každé feature by znovu předkládal tentýž starý dluh.
- **`/attack`** – aplikace se **spustí** a zkouší se rozbít; `/review` kód čte, tenhle ho spouští. **Stojí až v poslední mezeře schválně:** je drahý a nad rozestavěnou prací by hlásil hlavně nedodělanost. Projekt bez spustitelné aplikace ho nemá.
- **`/cleanup`** – **poslední krok každé mezery**; spouští ho konec session, ne pozice, takže běží i uprostřed rozdělaného `/implement`. Zapíše i rozhodnutí z kontrolních kroků (co bylo odmítnuto a proč). Běží-li po něm ještě `/attack` nebo `/release`, ty si zápisy dělají samy a `/cleanup` se **pouští znovu** jako verifikace. **Po úspěšném zápisu nabídne `/merge`**, stojí-li session mimo hlavní větev – i před `/attack` – útok pak běží nad hlavní větví a nasazuje se až vědomým povýšením do `production`; **u projektu, který nasazuje přímo z hlavní větve, merge nenabízí**.
- **`/merge`** – dokončení větve: sloučení do hlavní větve a úklid. Spojený stav vzniká a ověřuje se ve větvi, takže do hlavní větve jde jen to, co prošlo *Kontraktem příkazů*. **Jediným spouštěčem je výslovný pokyn uživatele** (`~/.claude/standards/worktree.md`, *Větev žije, dokud uživatel neřekne jinak*). **U projektu, který nasazuje přímo z hlavní větve, se nepouští vůbec** – merge je tam nasazení a patří `/release`. Odpadá u projektu bez větví.

### Co smí stát v které mezeře

Mezera je prostor, ve kterém se kontrolní kroky pouštějí v uvedeném pořadí – a jen ty, na jejichž spouštěč došlo.

| Mezera | Co v ní může stát |
|---|---|
| `/project` → `/discovery` | `/cleanup` → `/merge` |
| `/discovery` → `/specify` | `/review` → `/oponent` → `/cleanup` → `/merge` |
| `/specify` → `/architect` | `/review` → `/oponent` → `/cleanup` → `/merge` |
| `/architect` → `/breakdown` | `/review` → `/oponent` → `/consolidate` → `/consistency` → `/cleanup` → `/merge` |
| `/breakdown` → `/implement` | `/review` → `/cleanup` → `/merge` |
| `/implement` → `/release` | `/review` → `/consistency` → `/cleanup` → `/merge` → `/attack` → `/cleanup` |
| `/release` → `/evaluate` | `/cleanup` |
| za `/evaluate` | `/review` → `/cleanup` → `/merge` |

**`/review` stojí za každým krokem osy, který vyrobil artefakt** – u projektu bez kódu je hotovou prací dokumentace návrhu. **Jedinou výjimkou je `/project`**, který si artefakt měří sám revizí souladu se standardem.

**`/review` měří proti předpisu v souboru, `/oponent` posuzuje obsah bez předpisu.** Nález `/review` se vyvrací ukázáním na pravidlo doménové znalosti, nález `/oponent` argumentem. Specialisté na korektnost, bezpečnost a testy se zapínají jen na kód, takže u projektu bez kódu, ke kterému žádná relevantní doménová znalost neexistuje, je `/review` skoro prázdný a má se přeskočit; `/oponent` funguje vždycky (`decisions.md`, *Rozdíl mezi `/review` a `/oponent` nad obsahovým projektem*).

**Pořadí uvnitř mezery:** `/review` první, protože jeho opravy mění text, nad kterým pracují ostatní; `/consistency` po něm, protože uklízí i to, co `/review` nastřílel; `/cleanup` poslední, protože jako jediný odolá kompaktaci.

**`/merge` stojí jen za tím `/cleanup`, kterým se uzavírá větev.** Zůstává-li větev otevřená přes víc mezer (typicky během `/implement`), na řadu nepřijde. V poslední mezeře stojí **před** `/attack`, protože útok běží nad hlavní větví. **Za `/release` chybí schválně** – žádná větev k uzavření tam není. **Za `/evaluate` stát může**, protože ten zapisuje jako každá jiná práce.

**Poslední mezera se točí:** `/implement` a `/review` se v ní střídají po každé hotové featuře, dokud je co dělat.

**Spouštěč rozhoduje, jestli se na krok dojde.** Kroky osy čekají na výstup předchozího, kromě `/evaluate`. Z kontrolních čekají na pozici jen `/oponent`, `/review` a `/attack`; `/consolidate` a `/consistency` se pouštějí, až se nasbírá, co měří – dost kol, respektive dost změn –, `/cleanup` podle konce session a `/merge` jen na pokyn uživatele, takže se na něj nedojde nikdy samovolně. **Přeskočení se hlásí nahlas i s důvodem.**

**Proč v tomhle pořadí:** každý krok osy vyrábí vstup pro další; obráceně by se uklízelo nad stavem, který se ještě změní.

## Cyklus nekončí nasazením

**Zavírají se dvě smyčky a každá jinak dlouhá.**

**Pro pády** je to sledovací okno – poslední fáze `/release`, měří se v hodinách až dnech. Nasazení není hotové, dokud okno neuplyne a někdo ho výslovně neuzavře větou *„okno uzavřeno, N nových chyb“*; jinak chyba, která se projeví až o hodiny později, nemá vlastníka.

**Pro poznání** je to `/evaluate`: „je to k něčemu?“ se pozná za týdny, a protáhnout na ně sledovací okno by znamenalo, že `/release` nikdy neskončí. Jeho `docs/operation.md` čte `/specify`, když se rozhoduje, co se bude stavět dál – tím se cyklus uzavírá do kruhu.

## Hotfix

**Jde týmž životním cyklem, jen s vědomě přeskočenými kroky:** `/specify`, `/architect`, všechny běhy `/oponent`, `/consolidate` a `/breakdown` odpadají (opravuje se navržené, nic se nenavrhuje), `/consistency` a `/attack` taky. **`/evaluate` se nepřeskakuje ani nezdvojuje:** `/release` mu zapíše datum i u hotfixu, ale vyhodnocuje se provoz, ne vydání – běží-li už položka z předchozího nasazení, druhá nepřibude. **Nepřeskakuje se `/review`, průběžná kontrola ani `/merge`** – oprava ve spěchu je ten případ, kdy je kontrola nejcennější, a hotfix na větvi je pořád větev. Přeskočení se hlásí nahlas i s důvodem.

## Povolená opakování

**Žádný krok neopakuje, co udělal krok před ním.** Každý má v *Co skill nedělá* jmenovitě napsané, čí práci nepřebírá; u věci, kterou hlídají tři kroky, ji nakonec neudělá pořádně žádný.

**Test: vrací ten krok nad *týmž* vstupem tutéž odpověď?** Když ano, je to duplicita. Opakovat se smí jen to, čemu se mezitím **mohl změnit vstup**.

**Kontrolní krok ve víc mezerách sem nepatří** – vstup je pokaždé jiný; jejich seznamem je tabulka mezer.

**Povolená opakování jsou čtyři a jmenují se**, aby se seznam nedal rozšiřovat mlčky:

| Co se opakuje | Kde | Co se mezitím mohlo změnit |
|---|---|---|
| průběžná kontrola | `/implement` → `/review` | hook ji vynutil po poslední odpovědi, `/review` ji pouští nad celým rozsahem větve |
| audit závislostí | `/review` → `/release` | databáze zranitelností se mění bez ohledu na projekt |
| scan tajemství | `/review` → `/release` | mezi oběma kroky přibyly commity z `/consistency`, `/cleanup` i `/attack` |
| produkční build | `/review` → `/release` | kontrolní kroky i útok mezitím commitují, a `/release` ho navíc pouští **na čistém stromu** – „prošlo to při kontrolách“ a „projde to jako to, co posíláme ven“ jsou dvě tvrzení |

## Jeden člověk, jedna interaktivní session

Celý cyklus je vědomě nástroj pro **jednu interaktivní session jednoho člověka**: stojí na `AskUserQuestion` a na souhlasu průběžné kontroly vázaném na `$HOME`. **V CI a u spolupracovníka platí jen deterministická vrstva** – typecheck, lint, test, audit, scan tajemství, statická analýza. Panel specialistů, průchod nálezy, útok ani nasazení se v neinteraktivním prostředí nepouštějí.

Proto ani `/evaluate` nesbírá data naplánovaným agentem: připomenutí je záznam v souboru, který nic nespouští, a běh samotný je interaktivní.
