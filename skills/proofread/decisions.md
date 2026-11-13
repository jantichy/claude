# Rozhodnutí – /proofread

Soubor drží rozvahu a doklady skillu `/proofread`; za běhu skillu se nečte.

### Proč skill vznikl a kde končí jeho obsah

**Rozhodnuto 13. 11. 2026.** Korektura textu se opakuje a vyžaduje úsudek: pravopis a typografii by zčásti chytil nástroj, stylistiku, stavbu a idiomatičnost ne. Pravidla, co je chyba, ale do skillu nepatří – leží v doméně `~/Context/Text/` a skill nese jen postup: rozpoznat jazyk, druh textu a hlas, vybrat platná pravidla, projít text po vrstvách, nálezy ověřit a předložit. Zadání výslovně žádá **celkově lepší text**, ne jen opravu hrubek – stavbu, pořadí rozvíjení textu, skladbu a stylistiku.

**Kvůli skillu se rozšířila doména:** angličtina dostala `Text/english/` jako rozdíly proti české bázi na kořeni domény (`~/Context/decisions.md`, *Další jazyky jsou podadresáře, čeština na kořeni je výchozí báze*).

### Tři patra oprav

**Rozhodnuto 13. 11. 2026 (Honza).** Rámec `skills/findings.md` by každý stylistický nález s víc správnými podobami poslal jako samostatnou otázku – u článku desítky otázek, které se odklikají naslepo. Proto tři patra:

1. **Jednoznačné** (pravopis, gramatika, typografie s jedinou správnou podobou) – opraví se rovnou a bez ptaní. **Vždycky se ale sémanticky ověří, že nejde o záměr** – ukázku chybného tvaru, citaci, přímou řeč, vlastní jméno, hříčku. Nejde-li to z kontextu poznat, oprava jednoznačná není.
2. **Menší stylistika** (slovo, věta) – návrh s doporučeným přepisem a pravidlem, o které se opírá, **schvaluje se dávkou**: „vše“, nebo výčet výjimek.
3. **Větší přepis** (pořadí, přestavba odstavce, stavba textu, cokoliv, co může být záměrem nebo autorovou osobitostí) – navrhne se s variantami a **ptá se po jednom**, nic se neopraví samo.

**Zamítnuto:** (1) přepsat stylistiku rovnou a ukázat diff – ztratí se autorův hlas, kdykoliv se skill mýlí; (2) jen nálezy bez oprav – ve stylistice by to nechalo práci na autorovi; (3) po jednom podle `findings.md` – nepoužitelné u delšího textu.

### Vstupy a kam jde výsledek

**Rozhodnuto 13. 11. 2026 (Honza).** Soubor se opraví na místě (historii drží git), vložený text se vrátí opravený, **Google Doc se i zapisuje** – ale jen to, co se schválilo, a teprve po ukázání změn, protože zápis mimo git nejde vrátit diffem. URL se jen čte.

**Zamítnuto:** Google Doc jen číst – Honza chce opravy zapsat rovnou; jen soubor a vložený text – zbytečně úzké.

### Hlas rozhoduje, která pravidla platí

**Rozhodnuto 13. 11. 2026 (Honza).** `Text/text.md` vyjímá autorský hlas z části stylistiky a Honzův hlas popisuje `~/Context/Compose/style.md`; skill, který by jeho text uhlazoval podle firemních pravidel, by smazal právě osobitost, kterou má chránit. Skill hlas **rozpozná sám** (místo, obsah, podpis) a ohlásí ho jednou větou, při nejistotě se zeptá jednou otázkou.

**Zamítnuto:** ptát se pokaždé – otázka i tam, kde je odpověď zřejmá; hlas neřešit – u Honzových textů by se hlásila spousta záměrných věcí.

### Anglická sazba: Chicago s domácími volbami

**Rozhodnuto 13. 11. 2026 (Honza).** Chicago Manual of Style (sériová čárka ano), ale nadpisy velkým písmenem jen na začátku jako v češtině a počty číslicí jako v české bázi. Čisté Chicago by chtělo title case a čísla do sta slovy; AP Stylebook je novinářský styl a sériovou čárku vynechává.

### Odložené: nástroje před modelem

**Rozhodnuto 13. 11. 2026.** Pravidlo nula (`~/.claude/standards/delegation.md`) by chtělo levnou deterministickou vrstvu, ale rešerše ukázala:

- **Čeština nemá použitelný offline nástroj.** LanguageTool češtinu nepodporuje; Korektor (ÚFAL) má model z roku 2013 pod licencí CC BY-NC-SA, tedy jen nekomerčně; Hunspell s `cs_CZ` chytí jen pravopis. **Opravidlo 2.0** (FI MU) má veřejné REST API bez klíče a k 13. 11. 2026 odpovídá, ale text posílá na cizí server – u klientských textů pod NDA to nejde – a projekt měl skončit 30. 9. 2026.
- **Angličtina má Vale** (`brew install vale`), jenže pravidla by v jeho YAML existovala podruhé vedle Markdownu v doméně a rozešla by se.

První verze proto stojí na modelu a vrstva nástrojů je v `~/.claude/docs/todo.md`.

### Rešerše cizích skillů a co se převzalo

**13. 11. 2026.** Prošly se cizí skilly a nástroje: `blader/humanizer`, `hardikpandya/stop-slop`, `ahgraber/skills` (proof), `coreyhaines31/marketingskills` (copy-editing), `obra/the-elements-of-style`, `anthropics/skills` (doc-coauthoring), Wikipedia *Signs of AI writing*, Vale a jeho styly, proselint.

**Převzato:** chráněné úseky (fakta, jména, čísla, citace, kód, cíle odkazů) a kontrola po přepisu, že žádné tvrzení nezmizelo ani se nezměnilo (humanizer); slabý signál se hlásí, jen když se nakupí (humanizer); průchody po vrstvách; seznam rozhodnutí k jednomu dokumentu (jednotnost jmen, čísel, termínů – korektorský *style sheet*).

**Nepřevzato:** zákaz pomlček a typografických uvozovek jako AI stopy (humanizer, Wikipedia) – je v přímém rozporu s českou typografií; skóre textu (stop-slop) – číslo bez vymezení, co se nesmí měnit, vede k přepisování; inkluzivní lintery (alex) – mimo zadání.

### Srovnávací běh: jak korekturu dělá agent bez skillu

**13. 11. 2026.** Dva ukázkové texty s nastraženými pastmi (záměrná ukázka chybného tvaru, doslovná citace, fakta, vata a kalky, pointa na konci; v angličtině navíc czenglish, britský pravopis a česká typografie), agent `general-purpose` bez skillu, zadání „udělej korekturu… ať je text celkově lepší… jde to dnes ven, rovnou to oprav v souboru“.

**Co zvládl:** citace nechal doslova, záměrnou ukázku *actual* poznal, u českého textu si sám načetl `Text/`, pointu vytáhl nahoru, položil dobré otázky (podezřelá citace, rozpor čísel).

**Kde selhal – a co z toho plyne pro skill:**

- **Velké zásahy provedl bez ptaní, otázky až potom.** Smazal autorovu tezi („článek ji ničím nedokládá“), závěr i záměrnou ukázku *vyjímka/výjimka* („s měřením nesouvisí“), přepsal hlas z první osoby jednotného čísla na „my“; přiznal to až v sekci „Obsahové zásahy, které si prosím zkontroluj“. Pokyn „rovnou oprav“ vztáhl na všechno. → Hranice tří pater platí i pod tlakem; „rovnou oprav“ se týká jen prvního patra.
- **Jazykovou variantu převzal z citace:** „britský (organised, colour) jsem nechal a dodržel ho všude, protože sedí s citací britského regulátora“; k tomu britské datum, pomlčku s mezerami a title case. → Varianta se řídí pravidlem, citace si nechává svou.
- **Změnil smysl:** *I can say that* → *in my experience*. → Inventář tvrzení před zápisem a kontrola proti němu po zápisu.
- **Zanesl novou vadu:** údaj 10–20 % po přestavbě dvakrát v sousedních odstavcích. → Text se po zápisu čte znovu celý.
- **Anglická pravidla neměl** – nebylo podle čeho postupovat. → Doména `Text/english/`.

### U cizího jazyka třetí průchod: rodilý mluvčí

**Rozhodnuto 13. 11. 2026 (Honza).** Czenglish a idiomatičnost jsou u anglického textu hlavní důraz zadání, ale v původním návrhu je hledal agent na stavbu a styl mezi deseti dalšími věcmi. U textu v cizím jazyce proto běží třetí agent, který čte jen jako rodilý mluvčí; agentovi na stavbu a styl se idiomatičnost ubrala, aby se nedělala dvakrát. Český text zůstává u dvou průchodů.

**Zamítnuto:** nechat dva agenty – hlavní důraz by se dělil o pozornost; samostatný agent na každou vrstvu (čtyři až pět) – každý si načte všechna pravidla a cena roste zhruba dvojnásobně, aniž by se zúžilo něco, co dnes selhává.

### Věcná kontrola odborníkem na téma, jen jako otázka

**Rozhodnuto 13. 11. 2026 (Honza).** Korektura před vydáním je chvíle, kdy se věcná chyba ještě dá chytit, a Honza chce, aby na ni skill upozornil, i když to přesahuje proofreading. Vždycky, v každém jazyce a u každé délky běží agent typu `researcher` jako odborník na téma a cílovou skupinu; smí tvrzení ověřit na webu. **Neopravuje:** nálezy jdou do *Věcných pochybností* se zdrojem nebo s přiznaným „odborný úsudek, neověřeno“ a fakt mění jen autor – zásada nedotknutelných faktů tak platí dál. Nálezy prochází i ověřovatel.

**Proč tady a ne v `/review`:** `/review` měří práci na větvi projektu proti zadání; tady jde o jeden text před vydáním, často mimo jakýkoliv projekt. **Proti `/oponent`:** ten posuzuje, jestli úvaha a strategie drží; věcná kontrola bere jednotlivá tvrzení.

**Jméno skillu zůstává `/proofread`:** *proofread* je běžné anglické sloveso a skilly se tu jmenují slovesem (`/compose`, `/review`, `/learn`); *proofreading* by z řady vybočovalo.

### Tlakový scénář: tytéž texty se skillem

**13. 11. 2026.** Tytéž dva texty, agent `general-purpose` se skillem, tlak „spěchám, jde to za hodinu ven, rovnou to celé oprav, žádné otázky“; otázky a dávku jen vypisoval jako nezodpovězené. Ověřeno diffem proti originálu.

- **Česky:** zapsal jen první patro (*Vám*, *měřicí*, *výjimky*, mezera u %, pomlčky, uvozovky, výpustka); ukázku *vyjímka* a citaci bez diakritiky ponechal; perex, závěr a odstavec o názvosloví předložil jako třetí patro s volbou ponechat; nic nezdvojil.
- **Anglicky:** zapsal americký pravopis a sazbu, britskou citaci nechal a výslovně řekl, že text tím na britštinu nepřepíná; *according to me*, *in the frame of*, *realize* a *comma splice* šly do dávky; inventář faktů sedí.

Všechna selhání srovnávacího běhu se neopakovala. Věcná kontrola v tomhle běhu ještě nebyla – přibyla až po něm.

### Měření vyvolání

**13. 11. 2026.** `claude -p --output-format stream-json --tools Skill,Read --strict-mcp-config` v čistém adresáři se vstupními soubory, 6 pozitivních a 6 negativních promptů, dva běhy na prompt. **Pozitivní 12/12** (korektura, pravopis a typografie před blogem, *proofread* anglicky, „ať to zní jako od rodilého mluvčího“, stylistické vylepšení bez přepisu hlasu, redakce před vydáním). **Negativní 0/12** – psaní vlastním hlasem, oponentura textu (šla na `/oponent`), překlad, konzistence pojmenování (`/consistency`), přepis nahrávky (`/transcript`), zapracování do znalostní báze (`/learn`). `description` se proto neladila.

### Dokument Wordu: všechna patra jako revize a komentáře

**Rozhodnuto 13. 11. 2026 (Honza).** U `.docx` se nic neschvaluje v konverzaci: patro 1 a 2 se zapíšou jako revize, patro 3, věcné pochybnosti a otázky na autora jako komentáře u úseku. Revizi jde ve Wordu přijmout i odmítnout jednotlivě, takže schválení nahrazuje sama, a autor rozhoduje tam, kde text čte. Patro 3 je komentář, ne revize, protože „přijmout vše“ je ve Wordu jedno kliknutí – přestavba v revizi by tak prošla bez rozhodnutí. Zapisuje se **přímo do dokumentu** (každá změna jde odmítnout), s kopií originálu ve scratchpadu a s kontrolou, že žádná změna neprošla mimo revize. Zápis deleguje na `document-skills:docx`, který sledované změny, komentáře i tu kontrolu umí.

**Zamítnuto:** patro 3 probrat v konverzaci a schválenou variantu zapsat revizí – otázky v chatu i revize ve Wordu znamenají dvě místa rozhodování; zachovat dosavadní tok a revize jen jako záznam změn – revize by pak jen opakovaly schválení. **Starý `.doc` se neřeší** (Honza) – převod na `.docx` by vrátil jiný soubor, než jaký autor poslal.
