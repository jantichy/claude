# Naložení s tím, co by zůstalo mimo rozsah

Postup *Fáze 7* skillu `/cleanup`: jak se naloží s položkami, které do rozsahu úklidu nepatří, ale zmizely by se session. Stojí mimo `SKILL.md`, protože se čte až ve chvíli, kdy se v té fázi opravdu stojí.

------
**Patří sem i to, co jsi během skillu sám odložil jako „mimo rozsah“** – vymezení fáze drží `SKILL.md`, *Fáze 7 – Naložení s tím, co by zůstalo mimo rozsah*.

**Vyřídit ale neznamená zeptat se.** Položka mimo rozsah je nález zadarmo – všiml sis jí jen proto, že jsi u toho zrovna byl, a příště u toho nebude nikdo. Co umíš opravit jednoznačně, **oprav proto rovnou a bez ptaní, i když je to mimo rozsah úklidu**. Otázka, u které je předem jasné, jak zní jediná rozumná odpověď, nic nerozhoduje a stojí uživatele pozornost, kterou pak nemá na otázky, kde na jeho odpovědi opravdu záleží. Ptej se jen na to, co rozhodnout neumíš.

1. **Nemáš-li nic**, fázi přeskoč a v přehledu uveď „žádné“.

2. **Rozděl položky na ty, které vyřešíš sám, a ty, na které se zeptáš.** Hranice je táž jako u nálezů kontrolních skillů a drží ji `~/.claude/skills/FINDINGS.md`; tady k ní patří dvě podmínky navíc, protože položka mimo rozsah se nevypořádává ve fázi, která na ni má čas.

   | | Podmínka |
   |---|---|
   | **Vyřeš sám** – musí platit všechno | řešení má právě jednu zjevně správnou podobu, ne volbu mezi variantami; je to oprava nebo dorovnání toho, co už je rozhodnuté, ne nová práce ani nové rozhodnutí; **zásah celý vidíš a umíš ho po sobě ověřit**; **je vratný** – mění verzované soubory, nic nemaže nenávratně a nesahá mimo repozitář |
   | **Zeptej se** – stačí jedna | řešení má víc obhajitelných podob a volba mezi nimi je uživatelova; je to nová práce, změna pravidla, rozhodnutí nebo struktury; chybí ti údaj, který ví jen uživatel a **nedá se zjistit z repozitáře**; zásah je nevratný, sahá mimo repozitář nebo do cizího systému |

   **Takhle vypadají položky, u kterých se nemá co ptát** – všechny tři jsou z jednoho běhu (18. 9. 2026) a u všech uživatel odpověděl „vyřešit teď“:

   - Úkol je v `done.md` jako hotový a v `todo.md` pořád visí. Dva soubory tvrdí opak, jeden z nich se dá ověřit – a pak se ta odrážka smaže.
   - Záznam v `done.md` cituje čísla rozhodnutí posunutá o deset. Správná čísla jsou v `decisions.md`, oprava je přepsat je.
   - Přejmenování minulo dvě místa. Nové jméno je rozhodnuté, zbytek je grep a náhrada.

   Společné mají to, že se nerozhoduje **jestli**, ani **jak** – jen to někdo musí udělat. Otázka nad takovou položkou není opatrnost, ale přehazování práce zpátky na uživatele.

   **Nejistotu nejdřív zkus odstranit** (`~/.claude/skills/FINDINGS.md`, *Nejistotu nejdřív zkus odstranit*): jde-li odpověď spočítat, dohledat nebo porovnat se zdrojem v repozitáři, není to položka k rozhodnutí, ale práce – a ta se dělá. **Pracnost sem nepatří**; „musel bych projít celý katalog a přepočítat to“ je popis práce, ne důvod k otázce.

   **Váhání je odpověď.** Nepřemlouvej se, že položka do první skupiny „nejspíš patří“ – patří tam jen to, u čeho je to zřejmé na první pohled. Toho, co uživatel nezadal a tys to přesto změnil, se nesmí nakupit tolik, aby to nešlo přečíst.

   **Objem důvod k dotazu není.** Zdlouhavá, ale jednoznačná oprava se dělá, ne předkládá; naopak jednořádková změna pravidla se předkládá, i když trvá vteřinu. Rozhoduje, čí je to rozhodnutí, ne kolik je s ním práce.

3. **Vyřeš první skupinu rovnou**, celou, ještě než se začneš ptát na druhou – a vypiš, cos udělal – **výpisem ale odpověď nekonči**, bod 4 i první otázka bodu 5 patří do téže odpovědi (`~/.claude/skills/FINDINGS.md`, *Ohlášená akce patří do téže odpovědi*):

   ```
   **Mimo rozsah, vyřešeno rovnou:**

   1. [položka] – [co jsi změnil a ve kterém souboru]
   2. …
   ```

   Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo – `~/.claude/RULES.md`, *Styl odpovědí*.

   **Nic z toho nezamlč, ale ani to nedramatizuj.** Uživatel tu práci nezadal, takže musí vidět, co se v jeho projektu změnilo, a mít možnost to vrátit – tichá oprava mimo rozsah je zásah do jeho domény bez jeho vědomí (`~/.claude/RULES.md`, *Nerozhoduj potichu nad rámec zadání*). Řádka na položku ale stačí: **žádné rozepisování, čeho se týkala, proč byla mimo rozsah a co by se stalo, kdyby se neopravila.** Ten rozbor patří jen k položkám, o kterých se uživatel rozhoduje; u opravené věci je to hlášení nálezu, který už neexistuje.

4. **Zbytek vypiš najednou** jako číslovaný seznam **seřazený od nejdůležitější** – u každé položky jednou větou, čeho se týká a proč je mimo rozsah úklidu. **Práh důležitosti tady neplatí**, na rozdíl od Fáze 2: tohle je poslední místo, kde se o starším dluhu a o rozbitých věcech ze session dá rozhodnout, a co se nezeptá, zmizí se session. Řadí se proto jen proto, aby uživatel narazil na podstatné dřív, ne aby se zbytek zahodil. **Není to nabídka, ale přehled:** uživatel má vidět celý rozsah dřív, než se začne rozhodovat o jednotlivostech, aby věděl, kolik otázek ho čeká a jak spolu položky souvisí.

   ```
   **Mimo rozsah úklidu zůstává:**

   1. [položka] – [proč je mimo rozsah]
   2. …
   ```

   Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo – `~/.claude/RULES.md`, *Styl odpovědí*.

5. **Projdi je jednu po druhé.** U každé ji nejdřív vypiš:

   ```
   **[N/celkem] NÁZEV POLOŽKY**

   - **Čeho se týká:** [co to je, jednou dvěma větami]
   - **Proč je mimo rozsah:** [co ji drží mimo dnešní úklid]
   - **Proč se ptám:** [která podmínka z bodu 2 na ni sedí]
   - **Co se stane, když se to nevyřeší:** [konkrétní důsledek, ne „bylo by to lepší“]
   ```

   Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo – `~/.claude/RULES.md`, *Styl odpovědí*.

   Pak se zeptej samostatným voláním `AskUserQuestion` – jedno volání na jednu položku, `header` `Mimo rozsah` (`~/.claude/RULES.md`, *Ptej se postupně, ne všechno najednou*, dovoluje 12 znaků, takže se číslo položky do hlavičky nevejde – nese ho výpis nad otázkou). Volby:

   **Ty volby platí pro položku, která je novou prací nebo nápadem** – tam je „jestli a kdy“ doopravdy uživatelovo rozhodnutí. **Je-li položka vadou** – dvě místa si odporují, odkaz nikam nevede, číslo nesedí se zdrojem –, je volba „kdy“ falešná a položka patřila do bodu 3 (`~/.claude/skills/FINDINGS.md`, *Volby v otázce jsou varianty řešení, ne „teď nebo později“*). **Objeví-li se v nabídce *Vyřešit teď*, ověř si proto ještě jednou, proč ji tam dáváš**: u vady, kterou umíš opravit, je to doklad, že se nemáš ptát.

   | Volba | Co uděláš |
   |---|---|
   | **Vyřešit teď** | Vyřeš položku **hned**, ještě než se zeptáš na další – ne až po posledním dotazu. Rozhodnutí odložené na konec ztratí kontext, ve kterém padlo. |
   | **Zapsat do todo** | Zapiš ji do `docs/todo.md` – ne jako holou odrážku, ale s kontextem a odůvodněním, aby se na ni dalo navázat bez téhle session. Volí se u položky, o které je rozhodnuto, že se udělá. |
   | **Zapsat do backlogu** | Totéž, ale do `docs/backlog.md` – u nápadu, který nikdo neschválil ani nezamítl. **Nenabízej obě volby jako totéž**: rozhoduje se tím, jestli položka bude v seznamu, který se odpracovává. Nemá-li projekt `backlog.md`, **založ ho** a řekni to – nezávazný nápad do fronty úkolů nepatří a jinam ho zapsat nelze (`~/.claude/STRUCTURE.md`, *`backlog.md`*; totéž říká `SKILL.md`, *Když soubory neexistují*). |
   | **Zahodit** | Nic s ní nedělej. Volí se vědomě, ne mlčením. |

   Když jsi vyřídil poslední položku, pokračuj Fází 8 – tam na tebe čekají nálezy čtenářů z Fáze 6.

   **Neptej se předtím hromadně**, co s celou skupinou. Dřív tady stála meziotázka, jestli položky vyřešit všechny naráz, zapsat všechny do todo, nebo je projít po jedné – a v provozu z ní vždycky vyšlo „po jedné“, protože položky se povahou liší skoro vždycky; zrušena 7. 9. 2026. Volba, která má jediný reálný výsledek, stojí jednu odpověď navíc a nic nerozhoduje. **Platí to na tuhle skupinu, ne obecně:** kde jsou položky stejnorodé, je hromadná volba na místě a jinde ve skillech se schválně používá.

6. Ať se rozhodne jakkoli, v přehledu ve Fázi 9 pak u sekce *Mimo rozsah úklidu* uveď, **jak se s položkami naložilo** – nikdy jen jejich výčet bez osudu. **Vyřešené z bodu 3 patří do téhož seznamu**, ne stranou: uživatel má na jednom místě vidět všechno, co bylo mimo rozsah, a u každé položky, kdo o ní rozhodl.

**Proč se dnes část řeší bez ptaní:** dřív se tady vypisovalo všechno a nedělalo nic, pak se skill začal ptát na každou položku zvlášť. Druhá podoba vyřešila mizení položek se session, ale u jednoznačných oprav se ptala zbytečně – uživatel měl odklikávat, že se má opravit rozbitý odkaz, kterého si model všiml jen náhodou. Rozhodnuto 18. 9. 2026.
