---
name: cleanup
description: Skill se použije, když uživatel zadá "/cleanup", nebo chce před koncem či kompaktací session zapsat všechno, co se v ní domluvilo a zjistilo, do souborů – aby nová session navázala bez ztráty kontextu a nevycházela z něčeho, co už neplatí. Zároveň dohledá témata, která v konverzaci zůstala bez vypořádání, a probere je.
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, Skill]
---

# Cleanup

## Co skill dělá

Uživatel je na konci nějakého problému a chystá se session opustit nebo zkompaktovat. Tvým jediným úkolem je zajistit, že **nic z téhle session nezůstane jen v konverzaci**:

1. **Nic se neztratí** – vše, co se řešilo, na čem jste se dohodli a k čemu jste došli, je zapsané v souborech. Nová session nesmí přijít o žádnou informaci, dohodu, princip, výstup ani závěr.
2. **Nic nezůstalo viset** – žádná otázka, návrh ani upozornění z konverzace nezapadlo bez vypořádání. Co viselo, se probere s uživatelem – ne odloží do závěru jako výčet bez vypořádání.
3. **Nic není nepravdivé** – nová session nesmí vycházet z něčeho, co v průběhu session přestalo platit.
4. **Je to commitnuté** – práce není hotová, dokud sedí jen v pracovním stromu.

**Vytěžení, konfrontaci se soubory a zápis dělá subagent, ne ty.** Transcript session leží na disku a k té práci není potřeba kontext hlavní session – běžela by nad největším kontextem, jaký ta session kdy má, a to je 55 % jejích nákladů. Ty zůstáváš u toho, co agent udělat nemůže: ptáš se, pouštíš čtenáře bez kontextu, commituješ a vydáváš verdikt.

Skill je **opakovatelný**. Spustí-li ho uživatel podruhé, druhý průchod slouží jako verifikace a **vytěžuje transcript celý znovu** – to je záměr, ne opomenutí: agent druhého běhu tak nezdědí slepá místa toho prvního. Zkratka přes zapsaný hash předchozího úklidu se zamítla 25. 9. 2026, rozbor v `decisions.md`.

**Uklízí se vždycky ta session, ve které stojíš, a jinak to nejde.** Agent dědí od rodiče pracovní adresář i session-id přes cestu ke scratchpadu, takže si transcript najde sám a není co vybírat. Argument s cizím id tu do 25. 9. 2026 byl – zbyl po zamítnuté cestě přes `/clear`, kde se skill pouštěl z jiné session než z uklízené; rozbor v `decisions.md`.

V *Životním cyklu projektu* (`~/.claude/RULES.md`) je to kontrolní krok, ne bod na ose: **stojí v každé mezeře a vždycky jako poslední**, protože jako jediný odolá kompaktaci – co zapíše, přežije ztrátu kontextu. Jeho spouštěčem není pozice, ale konec session, takže běží i uprostřed rozdělané práce. V poslední mezeře stojí dvakrát, před `/attackem` i za ním.

## Co skill nedělá

**Neopakuje, co udělal `/consistency`.** Ten proběhl o krok dřív a prošel soubory dotčené větví (v režimu `full` celý projekt) – jiná otázka, jiný skill; čtenáři bez kontextu se tady ptají na jinou věc – *dá se na dnešní práci navázat?* – a rozpory hledají jen v tom, co na větvi přibylo.

Tohle **není** audit projektu ani technická kontrola. Nespouštěj `/consistency`, `/code-review` ani `/code-review ultra` – uživatel je volá zvlášť a před tímhle skillem. **Ani `/attack`**, ten přijde naopak až po tomhle a jako jediný aplikaci spouští, aby ji rozbil. Nespouštěj testy, lint, typecheck ani build a nedělej obecnou revizi souborů nad rámec toho, co ze session vzešlo. **Kontrola odkazů, kterou pouští agent, výjimkou není** – neposuzuje projekt, ale to, co se právě zapsalo, a běží zlomek vteřiny.

**Výjimka pro dokončení větve:** vybere-li uživatel v závěru *Přimergovat do main*, zavoláš `/merge` nástrojem `Skill` a necháš ho proběhnout celý, i s kontrolami, které předepisuje. **Merge sám neprovádíš ani nepopisuješ** – nabídka je zkratka k volání navazujícího kroku, ne jeho součást.

Druhá výjimka: to, co ze session zůstalo rozbité (padající test, nedodělaná změna), vrací agent jako samostatnou kategorii a ty ho vezmeš do *Fáze 5*, kde o tom rozhodne uživatel. Netvrď, že je hotovo, když není – ale sám to neověřuj a neopravuj, dokud si to uživatel nevyžádá.

## Jak je to postavené uvnitř

- **[`agent.md`](agent.md)** – zadání vytěžovacího subagenta. Nese celé jádro skillu: rekonstrukci session, konfrontaci se soubory, ověření průběžné aktualizace, zápis a kontrolu odkazů. **Neopisuj ho do promptu** – agent má `Read` a načte si ho sám z cesty, kterou mu předáš.
- **[`readers.md`](readers.md)** – zadání dvou čtenářů bez kontextu. **Závazné je, že jsou dva a že nemají shell**, ne konkrétní znění otázek.
- **[`out-of-scope.md`](out-of-scope.md)** – jak se naloží s položkami mimo rozsah úklidu. Body 2 a 3 plní agent, body 4 až 6 ty.
- **`scripts/links.py`** – ověří, že relativní odkazy ve změněných Markdownech vedou na existující soubor a kotvy na existující nadpis. Pouští ho agent. Je to **implementační detail, ne rozhraní** – jeho přepínače, výstup i samotná existence se smí změnit bez ohlášení. Co se změnit nesmí tiše, je **pravidlo za ním**: mechanické vady hledá deterministický nástroj, ne model (`~/.claude/RULES.md`, *Model a effort podle úkolu*, pravidlo nula), a jeho nálezy se opravují **před** spuštěním čtenářů. Vynucovací vrstvu k němu drží `tests/test_cleanup.py` – testuje oba směry selhání včetně mutačního testu, který vyřadí vynechávání bloků kódu a ověří, že falešný poplach opravdu vznikne.

**Dělítko mezi agentem a tebou:** do agenta patří práce, jejímž výstupem je **nález nebo jednoznačná oprava**; u tebe zůstává to, co potřebuje **uživatelovo rozhodnutí**, a to, co je **nevratné**. Agent proto nemá právo se ptát, commitovat ani pushovat, a ty zase nečteš transcript – jinak je delegace k ničemu.

**Agenta pouštěj na výchozím typu s plnou sadou nástrojů** (`subagent_type: "general-purpose"`): zapisuje do souborů a potřebuje shell na git i na skript. **Model nepředávej** – zdědí tvůj, a je to posouzení, ne sběr. **Effort předat nejde**, `Agent` ten parametr nebere; je to přiznaná mezera, ne pokyn. **Hloubka delegace je jedna**, takže agent už dalšího agenta nespouští – čtenáře bez kontextu pouštíš ty.

## Rozsah

**Session se vytěžuje vždycky celá** – to je smysl skillu a nedá se to zúžit ani rozšířit. Čtenáři bez kontextu se soustředí na to, co přibylo na větvi; starší dluh v dokumentaci sami neopravují – putuje do *Fáze 6*, kde se podle kritéria z [`out-of-scope.md`](out-of-scope.md) buď rovnou vyřeší, nebo o něm rozhodne uživatel.

**Audit celé dokumentace sem nepatří** – je to jiná otázka („sedí si projekt sám se sebou?“) a dělá ho `/consistency full` o krok dřív. Dřív tu byl režim `full`, který rozšiřoval čtenáře bez kontextu na celou dokumentaci; zrušen 6. 9. 2026, protože jméno svádělo ke čtení „bez `full` se session neprojde celá“ – a to je přesně naopak.

## Zásady pro celý průběh

- **Sporné věci předkládej uživateli jeden po druhém, nikdy víc najednou.** Co má jedinou zjevně správnou podobu, vyřešil už agent; dostane-li se k tobě položka, u které to platí taky, vyřeš ji sám a jen ji vypiš. Hranici drží `~/.claude/skills/FINDINGS.md`. **Restrukturalizace ani přesun souboru sem sám o sobě nepatří** – rozhoduje, jestli je z čeho vybírat, ne jak velký ten zásah je.
- **Ptej se vždy přes tool `AskUserQuestion`** – mechanika toolu viz `~/.claude/RULES.md`, *Ptej se postupně, ne všechno najednou*.
- **Výstup agenta předávej dál doslova, neparafrázuj.** Nález se vrací celý i s doložením; parafráze je přesně to místo, kde se ztratí detail, kvůli kterému agent běžel.
- Řiď se `~/.claude/RULES.md` (zejména *Pravda v souborech, ne v konverzaci*, *Single source of truth*, *K pravidlům ukládej i „proč“*, *Živá struktura*).
- Tam, kde jsou nezávislé čtecí operace, používej paralelní tool calls.

------

## Fáze 0 – Příprava

**Společný začátek drží `~/.claude/skills/PREFLIGHT.md`** – načti si ho a řiď se jím. **V bodu 1 patří `/cleanup` na řádek *Ne*, a tedy bez gitu pokračuje.** Jeho jádro je čtení transcriptu a zápis do dokumentace, což na gitu nestojí – a znalostní projekt bez verzování by jinak o zápis session přišel úplně, tedy o to nejcennější, co skill umí. **Ohlas nahlas, co tím odpadá:** základ session, diff pro čtenáře, commit i push, a s nimi **čtvrtá záruka** z *Co skill dělá*. **Čtenáře pozůstatků nepouštěj** – nemá z čeho mít podklad –, čtenář navazitelnosti běží normálně, a verdikt to musí říct místo tvrzení, že je hotovo.

**Bod 4 odpadá** – tenhle skill nesahá na kód, takže není co zkontrolovat před prvním zápisem. **Bod 5 naopak platí**, i když se session vytěžuje celá: diff větve je podklad pro čtenáře bez kontextu ve *Fázi 2*, takže hlavní větev hledej přes `merge-base` a `origin/HEAD`, jak ten bod předepisuje, ne doslovným `main`. U gitu tě navíc zajímá remote, a ten zjišťuj `git remote get-url origin`, ne `git remote` – to druhé vypíše jméno, ne adresu.

Navíc si zjisti tohle – všechno to předáš agentovi, ať to nezjišťuje znovu:

1. **Id session a cesta k jejímu transcriptu** – id si vezmi z cesty ke scratchpadu (`~/.claude/skills/SESSION.md`), je v ní jako předposlední komponenta. **Ověř, že soubor existuje**, a přečti si z něj čas prvního záznamu; potřebuješ ho na základ session v bodu 2.
2. **Základ session** – commit, na kterém session stála, **než cokoliv zapsala**. Z něj se skládá diff pro čtenáře bez kontextu, takže na něm visí celá *Fáze 2*.

   **`git rev-parse HEAD` to není**, má-li projekt zapnutý autocommit: session mohla commitnout dávno předtím, než se úklid spustil, a `HEAD` je pak commit **uvnitř** session. Najdi proto nejstarší commit novější než začátek session a vezmi jeho **rodiče**; není-li takový commit, je základ `HEAD`.

   ```sh
   git log --format='%H %cI' | awk -v start='<čas prvního záznamu transcriptu>' '$2 > start {h=$1} END {print h}'
   git rev-parse <ten hash>^
   ```

   **Nepřeskakuj to s tím, že se to pozná později.** Prázdný diff se od čistého nepozná: čtenáři ohlásí „nic jsem nenašel“ a vypadá to jako úspěch. Doloženo při prvním ostrém běhu 25. 9. 2026, kdy `HEAD` byl commit té session – zachránilo to jen to, že si toho agent všiml sám.

------

## Fáze 1 – Vytěžovací agent

Pusť jednoho subagenta a v promptu mu předej **jen cestu k zadání a fakta, která už máš**:

```
Načti si ~/.claude/skills/cleanup/agent.md a řiď se jím celým. Je to tvoje zadání.

Transcript: <cesta k .jsonl>
Session: <id>
Kořen projektu: <absolutní cesta> · větev: <jméno> · autocommit: <zapnutý/vypnutý> · paměťová politika: <co platí>
Standardní struktura: <v docs/, nebo v kořeni repozitáře> · pracovní adresář session: <cesta, a je-li mimo projekt, řekni to>
Základ session: <hash z Fáze 0>
Rozpracováno už před začátkem: <výčet z git status, nebo „nic“>
```

Tenhle blok se posílá agentovi jako prompt, ne do konverzace.

**Kde struktura leží, řekni agentovi i tehdy, když je to z kořene vidět.** [`agent.md`](agent.md) píše cesty v podobě pro režim `docs/` (`~/.claude/STRUCTURE.md`, *Dva režimy umístění*), takže v projektu s kořenovým režimem musí agent vědět, že se ten zápis překládá. A **pracovní adresář session nemusí být kořen projektu** – nemusí to být ani git repozitář, takže co si agent odvodí z prostředí, může mířit úplně jinam.

**Nečti transcript sám** – ani kvůli ověření jednoho nálezu. Agent vrací doslovné citace s čísly řádků právě proto, aby se dalo ověřit grepem.

**Než budeš pokračovat, projdi jeho výstup a rozhodni tři věci:** platí meze běhu, které přiznal (co nestihl přečíst)? Je mezi cestami k commitu něco, co podle *Fáze 0* rozpracoval někdo jiný? A vypsal u každé položky k rozhodnutí hotový text zápisu, nebo bys ho musel psát ty? **Chybí-li to poslední, vrať mu to** – jedním dotazem na tu položku, ne novým během.

**Práci, která v téhle session vznikne až za běhu, nekryje nic.** Agentův snímek `git status` z *Fáze 0* zná jen to, co bylo rozpracované **před** ním. Pokračuje-li uživatel v práci nad týmž repozitářem, zeptej se ho, čeho se dotkl, a ty cesty z commitu vyjmi – jinak je zatáhneš pod zprávu o úklidu a po pushi se to neopravuje. Nad jiným repozitářem ani při čtení a hovoru to riziko nevzniká; rozbor drží `decisions.md`, *Skill `/cleanup` poběží v subagentovi, ne v čisté session po `/clear`u*.

**Vrátil-li agent chybějící soubory** ze standardní struktury, vypiš je a **nabídni spuštění `/project`**, který ji doplní celou a konzistentně – nezakládej je po jednom. Výjimkou je soubor, který si vyžádá zvolená odpověď: zvolí-li uživatel *Zapsat do backlogu* a projekt `docs/backlog.md` nemá, založ ho a řekni to ([`out-of-scope.md`](out-of-scope.md), bod 5) – nezávazný nápad do fronty úkolů nepatří a jinam ho zapsat nelze. Agent má zakázáno je zakládat sám právě proto, že tohle je rozhodnutí, ne dorovnání; jedinou výjimku měl u souboru, do kterého ze session jednoznačně něco patřilo, a tu ti vypsal mezi zápisy.

------

## Fáze 2 – Čtenáři bez kontextu

Ověř, že to, co agent zapsal, **dává smysl někomu bez kontextu téhle session**. Pusť čtenáře **hned**, ještě než se začneš ptát: běží na pozadí a jejich latence se schová za celou interaktivní část. Vypořádají se v *Fázi 6*.

Zadání obou drží [`readers.md`](readers.md) – *Čtenář navazitelnosti* čte dokumentaci od obecného ke konkrétnímu, *Čtenář pozůstatků* dostane diff. Tamtéž stojí, proč jsou dva, jaký model mají a co dělat, když typ `reader` v instalaci není. **Shrnutí, co se řešilo a kam se to zapsalo, vezmi z výstupu agenta** ze seznamu *Zapsáno* – ne z vlastní paměti, tu o té práci nemáš.

Čtenář pozůstatků nemá shell, takže si diff nevyrobí – **připrav mu ho do souboru** ve scratchpadu a v zadání mu předej cestu:

```sh
git diff "$(git merge-base HEAD origin/HEAD 2>/dev/null || git merge-base HEAD main)" -- '*.md' > <scratchpad>/cleanup-diff.txt
```

**Diffuj proti pracovnímu stromu, ne mezi dvěma revizemi.** Agent své zápisy **necommituje**, takže `main...<větev>` ani `<základ>..HEAD` je neobsahuje – čtenář by dostal podklad bez toho, kvůli čemu se pouští. Jeden hash bez `..` znamená „od tam po pracovní strom“ a to je správný rozsah.

**Podkladem je diff větve, ne jen diff session.** Pozůstatek, který na větvi zůstal po předevčerejší session, dnes nenajde nikdo: `/consistency` běží před úklidem, ne za ním. Nálezy mimo dnešní práci pak projdou kritériem z [`out-of-scope.md`](out-of-scope.md) jako cokoliv jiného mimo rozsah. **Stojíš-li na hlavní větvi**, diff větve neexistuje – vezmi `git diff <základ session> -- '*.md'` se základem z *Fáze 0*.

**Spusť oba jedním blokem** jako podagenty typu `reader`, tedy `subagent_type: "reader"`, a **nečekej na ně**. Nenastavuje se pro to nic zvláštního: `Agent` vrací řízení sám od sebe, jakmile agenta předá, a výsledek dorazí později jako notifikace o dokončení úlohy. Stačí tedy po zavolání pokračovat další prací – rovnou *Fází 3*. Ověřeno 19. 9. 2026.

**Jedeš-li náhradní cestou** ze [`readers.md`](readers.md) (samostatný proces `claude -p`), tenhle krok neplatí – ta blokuje, takže by se čekalo tady i v *Fázi 6*. Pusť čtenáře až na začátku *Fáze 6* a interaktivní fáze odbav bez nich.

**Dva čtenáři nejsou panel agentů ve smyslu `~/.claude/skills/SKILLS.md`, *Ověřovací vrstva*, a ověřovatele proto nemají.** Norma míří na panel specialistů, kde ověřit nález znamená zopakovat jeho práci. Zdejší nálezy mají tvar „na tomhle místě stojí X, na tamtom Y“, takže je ověříš u zdroje jedním čtením, a to i musíš (*Fáze 6*). **Přibude-li sem třetí agent, je potřeba tohle posoudit znovu**; rozhodnuto 19. 9. 2026.

**Interaktivní fáze jim mění stav pod rukama** – zápisy z odpovědí a opravy mimo rozsah, takže nález, který dorazí, může být mezitím vyřízený. Než ho v *Fázi 6* předložíš, ověř, že pořád platí; neplatné zahoď mlčky a nepiš o nich.

------

## Fáze 3 – Nevypořádaná témata

Nejčastější ztráta v dlouhé konverzaci není zapomenutý zápis, ale **nevypořádané téma**: dlouhá odpověď s několika body, uživatel se chytil poloviny, zbytek zůstal bez vypořádání. Nikdo to nezavrhl ani neschválil. Agent je vytěžil a prosil sítem – jeho zdůvodnění, co prověřil, přebíráš a **transcript kvůli tomu nečteš podruhé**.

Proto se tahle fáze ptá **první**: rozhodnutí, která tady padnou, mění, co se zapíše, a agent proto zápisy závislé na nich vědomě neprovedl. Kdyby se ptala až v závěru, uživatel už je duchem pryč a odpoví „to je jedno“.

Nejdřív uživateli řekni, kolik toho viselo (nebo že nic – to je taky výsledek, nemlč o tom). Pak **jednu položku po druhé**, nikdy víc najednou:

```
**[N/celkem] O ČEM TO BYLO**

- **Kdy:** [zhruba kde v konverzaci – čeho se to týkalo]
- **Nevypořádáno:** [citace nebo věrné shrnutí toho, co zůstalo bez odpovědi]
- **Proč není vypořádané:** [co agent prověřil a proč to nepovažuje za vyřešené jinudy]
```

Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo – `~/.claude/RULES.md`, *Styl odpovědí*.

Pak se zeptej **přes tool `AskUserQuestion`** – jedno volání na jednu položku, `header` `Téma N/celkem`. Volby dej **věcné, tedy skutečné odpovědi na tu konkrétní otázku** (varianty, které tehdy byly ve hře), ne obecné „zapsat / odložit“; text zápisu ke každé z nich máš od agenta. Ke každé položce vždy přidej volbu **„Bezpředmětné“** pro případ, že to uživatel mezitím vyřešil v hlavě nebo o to už nestojí.

| Odpověď znamená | Co uděláš |
|---|---|
| rozhodnutí | zapiš ho – i se zdůvodněním, které tady padlo – tou editací, kterou agent připravil |
| „vrátíme se k tomu“ | do `docs/todo.md` s celým kontextem, ne jako holá odrážka |
| „někdy by šlo“, nezávazný nápad | do `docs/backlog.md` – **ne do todo**; hranici drží `~/.claude/STRUCTURE.md`, *`backlog.md`* |
| bezpředmětné | nic nezapisuj; v přehledu v *Fázi 7* to ale uveď, ať je vidět, že se to probralo |
| práce navíc (dodělat kód, přepsat návrh) | to je nad rámec úklidu. Udělej to **jen na výslovný pokyn** a pak pokračuj skillem dál; jinak do `docs/todo.md` (tamtéž) |

------

## Fáze 4 – Sporné zápisy

Sem patří položky, u kterých agent zápis neprovedl, protože **je z čeho vybírat**: nejasné zařazení mezi dvěma soubory, dvě obhajitelné podoby téhož textu, dvě protichůdné informace bez zjevného vítěze. Nejdřív položku vypiš:

```
**[N/celkem] NÁZEV POLOŽKY**

- **Z session:** [co v session padlo, případně citace]
- **Stav:** [chybí / zastaralé / špatné místo / duplicita / nejasné zařazení]
- **Návrh:** [konkrétně co kam zapsat nebo jak přepsat – ne vágně „doplnit dokumentaci“]
```

Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo – `~/.claude/RULES.md`, *Styl odpovědí*.

**Přišla-li sem položka, u které je návrh jednoznačný, zapiš ho rovnou a neptej se** – a řekni to, protože je to nález na agentovi: měl ji vyřešit sám.

Ptej se voláním `AskUserQuestion`, jedno volání na jednu položku, `header` `Položka N/celkem`, `question` shrnuje položku jednou větou. **Volbami jsou konkrétní cílové soubory** u položky s nejasným zařazením, nebo **konkrétní podoby zápisu** tam, kde se text dá napsat dvěma obhajitelnými způsoby.

**Trojici *Zapsat / Odložit / Přeskočit* nenabízej** – žádná z nich není podobou řešení a odpověď je u ní předem známá (`~/.claude/skills/FINDINGS.md`, *Volby v otázce jsou varianty řešení, ne „teď nebo později“*). Stála tu do 21. 9. 2026 a byla to nejčastější falešná otázka celého skillu: `question` nesla hotový návrh, co kam zapsat, a přesto se ptala, jestli ho provést.

------

## Fáze 5 – Naložení s tím, co by zůstalo mimo rozsah

Sem patří, co agent vrátil jako položky mimo rozsah a nerozhodl sám: rozbité a nedodělané věci známé ze session, starší dluh, na který narazil při zápisu. **Vypsat a nechat být je nepřijatelné** – uživatel session vzápětí zavře a položky zmizí s ní. **Nálezy čtenářů sem nepatří**, ti v tuhle chvíli teprve běží a vypořádají se v *Fázi 6* podle téhož kritéria.

**Celý postup drží [`out-of-scope.md`](out-of-scope.md)** – na tebe z něj patří **body 4 až 6**: přehled, průchod položka po položce a zápis osudu do souhrnu. Body 2 a 3 už provedl agent, takže první skupinu – co má jedinou zjevně správnou podobu – máš vyřešenou a vypsanou od něj. Přečti si ten soubor a řiď se jím.

------

## Fáze 6 – Vypořádání nálezů čtenářů

Sem dorazí, co našli čtenáři z *Fáze 2*. **Nedorazili-li ještě, počkej na ně** – bez nich nemá fáze co vypořádat a přeskočit ji znamená zahodit celý smysl *Fáze 2*. **Vrátil-li některý chybu nebo nic**, pusť ho jednou znovu; selže-li podruhé, napiš do přehledu, že jeho část zůstala nezkontrolovaná, a pokračuj – netvrď, že kontrola proběhla.

**Než s nálezem cokoliv uděláš, ověř, že pořád platí** – interaktivní fáze mezitím sahaly na soubory a část nálezů mohly vyřešit. Neplatné zahoď mlčky; hlásit nález, který už neexistuje, je totéž jako hlásit falešný poplach.

- **Nálezy, které se týkají dnešní práce**, oprav – **co má jednu zjevně správnou podobu, sám a bez ptaní**, i když to mění strukturu; předlož jen to, u čeho je z čeho vybírat (`~/.claude/skills/FINDINGS.md`). Je to táž hranice jako u položek mimo rozsah, ne mírnější.
- **Nálezy mimo rozsah session** (starší dluh, včetně toho, co na větvi zbylo z předchozích session) projdi kritériem z [`out-of-scope.md`](out-of-scope.md), bodu 2: co má jednu zjevně správnou podobu, oprav rovnou a vypiš; o zbytku nech rozhodnout uživatele. *Fáze 5* už proběhla, takže se rozhoduje tady a stejným způsobem – a **do přehledu jdou tyhle položky do téhož seznamu** *Mimo rozsah úklidu*, ne stranou.
- **Byly-li opravy netriviální** (přepisovala se struktura, měnil se obsah více souborů), pusť **znovu čtenáře pozůstatků** – jen jeho, ne oba, a **vyrob mu nový diff**: ten z *Fáze 2* pozdější opravy neobsahuje, takže by hledal v zastaralém podkladu. Opravy samy zanechávají nové pozůstatky, ale navazitelnost se jimi nemění, takže druhý průchod celou dokumentací by byl čekání bez zisku. Tenhle běh už na pozadí schovat nejde, protože po něm nic dalšího nezbývá; proto se pouští jen tehdy, když opravy opravdu byly netriviální.

------

## Fáze 7 – Git a závěr

**Zapiš průchod do `docs/done.md`, sekce `## Průchody životním cyklem`** (`~/.claude/STRUCTURE.md`, *`done.md`*). Čtenářem je **příští `/cleanup`**, který jinak nepozná, co zůstalo mimo rozsah úklidu a jak se s tím naložilo – a bude se na totéž ptát znovu.

```
- **YYYY-MM-DD** · `/cleanup` · `<short HEAD>` · session `<session-id>` · N nevypořádaných témat (X rozhodnuto, Y bezpředmětných) · mimo rozsah: <co a jak se s tím naložilo>
```

Datum vyrob `date +%F` a hash `git rev-parse --short HEAD`. **Id session** vezmi z cesty ke scratchpadu, stejně jako v *Fázi 0*. **Nemá-li projekt `done.md`, krok přeskoč nahlas** – nezakládá se kvůli jednomu řádku.

**Id session není evidence uklizených session ani čára.** Opakovaný běh nad toutéž session je legitimní použití a tenhle řádek mu nijak nebrání – dvě data u téhož id znamenají dva úklidy, ne duplicitu. Zapisuje se proto, že jinak z `done.md` nejde poznat, **co** se uklidilo; rozhodnuto 25. 9. 2026, rozbor v `decisions.md`.

**Git:**

- **Commituj jmenované cesty, které vrátil agent**, spolu s tím, co jsi zapsal ty – ne `git add -A` ani adresář. Soubor, který byl rozpracovaný už před začátkem běhu, nech být a ohlas ho (`~/.claude/RULES.md`, *Commituj jmenované cesty, ne `-A`*).
- `git status` musí být **čistý** – kromě té cizí rozdělané práce, kterou jsi vyňal a pojmenoval. Co tam být nemá, patří do `.gitignore`.
- *Worktree layout:* `git status` pouštěj ve worktree větve, ne v kořeni kontejneru – tam by spadl na `must be run in a work tree`. Navíc zkontroluj `git -C <container>/main status`: v `main/` nemá být nic rozpracovaného – když je, ohlas to.
- Když má repozitář remote (zjistil jsi ho ve *Fázi 0*), všechno **pushnuté**.
- Ověř výsledek znovu (`git status`, `git log origin/<branch>..HEAD`) – ne že to jen předpokládej.

**Přehled:**

```
## Úklid dokončen

**Zapsáno ze session**
- N položek doplněno / M přepsáno / K přesunuto
- [stručný seznam: co, kam]

**Nevypořádaná témata**
- [N probráno, s jakým výsledkem – nebo „žádná“]

**Kontrola odkazů a čtenáři bez kontextu**
- [nálezy skriptu, verdikt obou čtenářů a co z nich vzešlo]
- Čtenáři: 2 (`reader`, [model]), ověřeni čtením zdroje – [N nálezů, M vyvráceno]

**Git**
- Pracovní strom: [čistý / co zbývá / čí cizí práce se vynechala]
- Commity: N, push: [ano / repozitář nemá remote]

**Odložené položky**
- [co se odložilo z vlastního úklidu – Fáze 3 a 4 –, nebo „žádné“]

**Mimo rozsah úklidu**
- [seznam z Fází 5 a 6 a u každé položky, jak se s ní naložilo: vyřešeno rovnou / vyřešeno na přání / todo / backlog / zahozeno – nebo „žádné“]
- Položka z Fáze 5 nebo 6 patří sem, i když skončila v `todo.md`; do *Odložených položek* se nekopíruje.

**Meze běhu**
- [co agent nestihl přečíst celé a co se proto nedá tvrdit – nebo „žádné“]

**Další krok:** /merge, stojíš-li na větvi, pak /attack a /release, nasazuje-li se – co dál s větví a session, rozhodne otázka za verdiktem
```

Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo – `~/.claude/RULES.md`, *Styl odpovědí*.

**Meze běhu nezamlčuj.** U velkého transcriptu se odpovědi nedají přečíst celé a agent to přiznává; vydat to za úplné znamená tvrdit, že se nic neztratilo, aniž to někdo ověřil.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Ze session je všechno zapsané, můžeš pokračovat, zkompaktovat i odejít.`
- **Stojíš-li na jiné než hlavní větvi** – ve worktree layoutu (`~/.claude/WORKTREE.md`) tedy v kontejneru s `.bare` a mimo `main/`, v běžném repozitáři prostě podle `git branch --show-current`: `Ze session je všechno zapsané. Větev <jméno> zůstává otevřená – můžeš pokračovat, zkompaktovat, nebo ji přimergovat do main.` Je-li ze session známé něco rozbitého nebo nedodělaného, použij místo ní `Ze session je všechno zapsané. Větev <jméno> zůstává otevřená – merge zatím brání: <konkrétní seznam>.` a merge v otázce níž nenabízej. Totéž platí, zjistil-li Git výš rozpracovaný `main/`, nebo stojí-li v `## Nasazení` projektového `CLAUDE.md`, že se z `main` automaticky nasazuje – merge by tam byl nasazení a patří `/release`. **V běžném repozitáři merge navíc přepne pracovní strom**, takže se nabízí jen tehdy, je-li `git status` čistý; to Git výš stejně vyžaduje, takže nečistý strom zastaví běh dřív.
- **Není-li to git repozitář:** `Ze session je všechno zapsané do souborů. Commit odpadá, protože projekt není git repozitář – ohlásil jsem to na začátku běhu.`
- `Zapsané zatím není všechno – brání tomu: <konkrétní seznam>.`

**Nenabízej „opustit session“ jako jedinou cestu.** Zápis je hotový, ale to neznamená, že je hotová práce: uživatel klidně pokračuje dál v téže session a `/cleanup` mu jen zajistil, že ho kompaktace nepřipraví o kontext. Ve worktree layoutu to platí dvojnásob – „můžeš odejít“ tam neodpovídá na otázku, kterou má uživatel v hlavě, totiž co s tou větví.

**Že merge přichází v úvahu, musí zaznít explicitně** – vedle pokračování a kompaktace. Věta ručí jen za zápis ze session; jestli merge smí projít (větev kola návrhu, rozpracovaný `main/`, konflikt), ověří až `/merge`, a proto v ní nestojí „bez obav“.

### Co dál

**Verdikt je poslední věta textu; hned za ním, skončil-li běh jednou z prvních dvou vět, polož otázku `AskUserQuestion`** s textem `Co dál? (/compact, /clear a /exit zadej sám)` a těmito volbami v tomhle pořadí – merge první, protože po úklidu ve větvi je nejčastější:

| Volba | Kdy se nabízí | Co se po ní stane |
|---|---|---|
| **Přimergovat do main** | jen stojíš-li na jiné než hlavní větvi – ve worktree layoutu v kontejneru s `.bare` a mimo `main/`, jinak podle `git branch --show-current` – a jen když verdikt nepojmenoval nic, co merge brání | zavoláš `/merge` nástrojem `Skill` |
| **Pokračovat v práci** | vždy | nic – čekáš na další zadání. **Další úklid bude potřeba**: co se od teď domluví, v souborech není |
| **Další kolo úklidu** | vždy | pustíš `/cleanup` znovu nástrojem `Skill` |

**Proč otázka, a ne rovnou merge:** `/cleanup` se pouští i před kompaktací uprostřed rozdělané větve, takže automatický merge by jednou poslal do `main` nedodělanou práci. Uživatel přitom po úklidu podle vlastních slov (16. 9. 2026) mergoval skoro vždycky, a ruční příkaz navíc byl jen tření. Zavržená varianta (16. 9. 2026): **režim `/cleanup merge`** – záměr by se řekl předem, ale uživatel by si režim musel pamatovat, kdežto otázka stojí jeden stisk. **Samostatný krok životního cyklu pro dokončení větve se tehdy zamítl taky, a 21. 9. 2026 se to obrátilo** – vznikl `/merge`. Nabídka tím nepadá, jen přestala být popisem postupu. Rozbor drží `decisions.md`, *Merge je samostatný krok, ne fáze `/cleanup`*. **Vybraná volba je výslovný pokyn** ve smyslu `~/.claude/WORKTREE.md`, *Větev žije, dokud uživatel neřekne jinak* – bez ní merge neprovádíš, nepřipravuješ ani nevypisuješ příkazy.

**Proč `/compact`, `/clear` a `/exit` nejsou volby:** jsou to vestavěné příkazy Claude Code a skill je spustit neumí. Volba, po které by následovalo jen „teď to napiš sám“, je krok navíc; stačí je jmenovat v textu otázky. Ukončit session natvrdo přes shell se nesmí – utrhla by se rozepsaná historie.

**Proč i mimo worktree layout:** postup dokončení větve drží od 21. 9. 2026 `/merge` a platí pro každý repozitář, ne jen pro kontejner s `.bare`. **Nabízí se jen tam, kde je co dokončovat** – na hlavní větvi ne.

**Merge se nikam dál nezapisuje.** Záznam průchodu v `done.md` vznikl před otázkou a nese hash úklidu; merge commit se zprávou shrnující práci je záznam sám o sobě.

**Skončil-li běh třetí větou** (zapsané není všechno), otázku nepokládej: další krok je odstranit to, co zápisu brání, a merge by šel přes nevypořádanou práci.

------

## Časté chyby

Z ostrých běhů, ne z toho, co by se pokazit mohlo.

- **`HEAD` se vydává za základ session.** V projektu se zapnutým autocommitem bývá `HEAD` commit **uvnitř** session, takže diff pro čtenáře vyjde prázdný – a prázdný diff se od čistého nepozná. Proto ho *Fáze 0* počítá z času session, ne z `HEAD`. Doloženo při prvním ostrém běhu 25. 9. 2026.
- **Agentovi se zapomene říct, kde struktura leží.** Píše cesty v podobě pro režim `docs/`; v projektu s kořenovým režimem nebo tam, kde pracovní adresář session není kořen projektu, si to bez pole v promptu odvodí špatně. Vyplň tedy celou šablonu, i to, co je z kořene vidět.
- **Diff pro čtenáře se skládá mezi dvěma revizemi.** Agent necommituje, takže `main...<větev>` ani `<základ>..HEAD` jeho zápisy neobsahuje a čtenář posuzuje podklad bez toho, kvůli čemu běží.
- **Fáze se přeskakuje, protože „nic nepřišlo“.** Nedorazili-li čtenáři, není to výsledek, ale čekání; a nemá-li agent položky k rozhodnutí, řekne se to nahlas, ne mlčením.
