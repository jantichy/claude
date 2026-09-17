# Formát výstupů

Pravidla pro to, jak má vypadat hotový přepis a shrnutí. Vytažené ze `SKILL.md`, protože se čtou až ve chvíli, kdy se výstup opravdu píše – tedy v posledních dvou krocích, ne během průvodce ani přepisu.

- [Pravidla doslovného přepisu](#pravidla-doslovného-přepisu)
- [Formát souhrnného MD](#formát-souhrnného-md)
- [Pravidla shrnutí](#pravidla-shrnutí)

## Pravidla doslovného přepisu

Platí pro `<name>.md` každé nahrávky i pro sekci „Doslovný přepis“ v souhrnu. Připrav doslovný přepis v jazyce nahrávky:

- Uprav jen **stylistiku a slovosled** tam, kde je to potřeba, aby se text dal plynule a smysluplně číst.
- **Oprav pravopis a gramatiku** podle pravidel jazyka nahrávky. Rozpoznávač neumí i/y ve shodě přísudku s podmětem, plete si tvary, které znějí stejně, a sází interpunkci od oka. Mluvčí to neřekl špatně – špatně to zapsal model, takže to není zásah do jeho projevu, ale oprava chyby přepisu. Typicky: „mrtvoli“ místo **mrtvoly**, čárky ve vedlejších větách, velká písmena u vlastních jmen. **Které pravidlo použít, řekne jazyk zjištěný v kroku 1**, ne domněnka, že jde o češtinu. U češtiny platí `~/Dev/context/text/text.md`, sekce *Gramatika a pravopis*, a celý `~/Dev/context/text/typography.md`; u jiného jazyka jeho vlastní konvence – anglický text má anglické uvozovky a anglickou interpunkci, ne české.
- **Nespisovné tvary a hovorovou mluvu ale nech být.** „Bysme“, „vokno“, „dycky“ nebo „démoni“ místo demonstrátorů jsou to, jak lidé mluví, a do doslovného přepisu patří. Opravuje se chyba zápisu, ne mluvčí.
- Odstraň **výplňová slova** (hesitační výplně) a **opakovaná slova** / místa, kde se řečník zamotal při hledání formulace.
- **Odstraň halucinace ASR** – i s VAD se občas objeví nesmyslné opakující se řádky (dokola tatáž věta, „Titulky vytvořil …“). Takové smyčky celé smaž.
- Rozděl text do **ucelených kapitol** s výstižnými mezinadpisy (`##`).
- Každou kapitolu rozděl do **kratších odstavců** – žádné dlouhé bloky.
- Nosné pojmy a důležitá sdělení vyznač **tučně**.
- Výčty uveď jako **odrážkový/číslovaný seznam**, kde to dává smysl.
- **Oprava přeslechů:** podle tématu a kontextu najdi a oprav slova, kterým rozpoznávač rozuměl špatně – tak, jak jsou, nedávají smysl, ale pravděpodobně jde o zkomoleninu jiného slova, které by v daném kontextu smysl dávalo.
- **Vlastní jména a názvy:** stejně oprav jména a názvy zkomolené špatnou výslovností nebo cizím přízvukem. Slovník z kroku 3 je pro tuhle opravu závazný zdroj správných tvarů.
- **České jméno v cizojazyčné nahrávce piš česky.** Když v anglicky mluveném záznamu zazní české jméno, firma nebo místo, rozpoznávač ho přepíše foneticky tak, jak to vyslovil cizinec – „Novak“, „Yarda“, „Brno“ jako „Burno“, „Škoda“ jako „Skoda“. Vrať mu **původní český tvar i s diakritikou**, i když je zbytek věty anglicky. Platí to oběma směry a je to jediná oprava, kterou děláš i tam, kde přepsané slovo dává v cizím jazyce zdánlivě smysl.
- **Neopravuj to, čemu jen nerozumíš.** Když stejné podivné slovo dává model opakovaně a konzistentně, je to nejspíš interní žargon, ne přeslech. Nech ho být, případně se zeptej.
- U dialogu **nepřehazuj pořadí** myšlenek; kde je zřejmé, kdo mluví, můžeš mluvčí odlišit, ale nevymýšlej jména.
- **Mluvčího nehádej.** S diarizací ber nálepky z `<name>.json` a repliku, která tam mluvčího nemá, nech bez jména. Bez diarizace mluvčí rozlišuj jen tam, kde to plyne přímo z textu. Špatné přiřazení je horší než chyba ve slově – překlep čtenář pozná, „Tomáš slíbil, že to dodá“ ne.

## Formát souhrnného MD

**Celý souhrnný dokument piš v jazyce nahrávky**, který jsi zjistil v kroku 1 – včetně nadpisu, anotace a názvů sekcí. Anglicky mluvená schůzka nemá mít české shrnutí.

Soubor `YYYYMMDD - Výstižný název.md` má tuto strukturu:

1. **Hlavní nadpis (H1):** `Výstižný název`.
2. **Úvodní odstavec (anotace):** do jednoho odstavce základní charakteristika celé nahrávky – o co jde, jednotlivé strany a účastníci.
3. **`## Shrnutí`:** stručné, logické, strukturované shrnutí dle [Pravidel shrnutí](#pravidla-shrnutí).
4. **`## Doslovný přepis`:** doslovné přepisy všech nahrávek dle [Pravidel doslovného přepisu](#pravidla-doslovného-přepisu), za sebou; u každého je zřejmé, ze které nahrávky pochází. U schůzky spojené v kroku 1 je přepis **jeden souvislý** a nedělí se zpátky podle původních částí – ty už nejsou předěl v obsahu, ale jen stopa po tom, kde se zastavil diktafon. Tuhle sekci vynech, když si uživatel doslovný přepis nevybral.

**Body 1 až 3 jsou tvůj vlastní text**, ne přepis. Platí pro ně [Pravidla shrnutí](#pravidla-shrnutí), ne [Pravidla doslovného přepisu](#pravidla-doslovného-přepisu) – ta se vztahují jen na bod 4.

## Pravidla shrnutí

Platí pro sekci „Shrnutí“. Připrav stručné, logické, strukturované shrnutí celé nahrávky – důležitých témat, poznatků a klíčových informací:

- Využij **přehledné formátování** – mezinadpisy, odstavce, odrážky, **tučný** text pro důležité pojmy.
- **Nedodržuj chronologické pořadí**, ve kterém informace zazněly. Uspořádej vše do logických sekcí a skupin tak, aby to dávalo při čtení smysl.
- Pokud to není nezbytné pro kontext nebo pochopení, **neopakuj** jednu informaci na více místech.
- Na **úplném konci** přehledně shrň vzájemné **domluvy, vyplývající úkoly a další kroky**.
- **Relativní časové údaje převeď na konkrétní data podle data nahrávky.** „Do konce týdne“, „příští čtvrtek“ nebo „za čtrnáct dní“ se v seznamu úkolů čtou špatně, protože čtenář neví, odkdy se počítají. **Konkrétní datum, které v hovoru zaznělo, ale platí tak, jak zaznělo** – i když s tvým přepočtem nesedí. Rozpor mezi obojím je signál, že je špatně datum nahrávky, ne hovor; vrať se ke kroku 1 a ověř ho. **Datum, které nezaznělo a nedá se odvodit, nedoplňuj** – termín u úkolu vypadá stejně věrohodně, ať je spočítaný, nebo vymyšlený.
- **Když běžela diarizace, piš ke každému úkolu majitele.** Je to hlavní důvod, proč se rozlišení mluvčích vůbec zapíná: bez něj se dá napsat „dodat seznam“, s ním „**Tomáš** dodá seznam“. U rozhodnutí stejně tak uveď, kdo co navrhl a kdo souhlasil, když to z přepisu plyne. Kde mluvčí chybí nebo je nejistý, majitele **nedoplňuj odhadem** – radši úkol bez majitele než přisouzený špatnému člověku.
- **Jazykový standard platí i tady, a v plném rozsahu.** Shrnutí není doslovný přepis, ale tvůj vlastní souvislý text, takže se na něj pravidla z [Pravidel doslovného přepisu](#pravidla-doslovného-přepisu) nevztahují sama od sebe – drž je vědomě. U češtiny navíc platí **celý** `~/Dev/context/text/text.md`, ne jen *Gramatika a pravopis* jako u přepisu: i stavba textu, zakázané obraty a stylistika. `~/Dev/context/text/typography.md` platí v obou případech stejně. U jiného jazyka jeho vlastní konvence, protože souhrn se píše v jazyce nahrávky. Pozor hlavně na termíny přebrané z přepisu: chybu opravenou v přepisu snadno zopakuješ ve shrnutí, protože ho píšeš z téhož podkladu. Přesně takhle v ostrém běhu prošly „mrtvoli“ do souhrnného dokumentu, zatímco v přepisu už byly opravené.

(Základní charakteristika a účastníci jsou už v úvodním odstavci – viz [Formát souhrnného MD](#formát-souhrnného-md).)

---
