---
name: discovery
description: Skill se použije, když uživatel zadá "/discovery", nebo chce před psaním zadání zjistit, do jakého světa produkt vstupuje – kdo je konkurence, co umí a za kolik, čím se proti nim vymezíme a co je na tom rizikové. Vyrábí docs/competition.md a docs/risks.md a předává do specifikace. Na rozdíl od /specify, který popisuje náš produkt, tenhle skill zkoumá svět venku a je opakovatelný sám o sobě, protože konkurence se hne bez ohledu na zadání. Nedělá obchodní ani marketingový plán – sbírá jen to, z čeho pak plynou požadavky na produkt.
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, WebSearch, WebFetch]
---

# Discovery

## Co skill dělá

Než se začne psát zadání, zjistí, do čeho produkt vstupuje. Sepíše **dva dokumenty**:

| Dokument | Odpovídá na otázku | K čemu je |
|---|---|---|
| **`docs/competition.md`** | Kdo to už dělá, co umí, za kolik – a jaká je proti nim naše pozice | Z toho plyne, co produkt musí umět, aby ho někdo vzal, a čím se má lišit |
| **`docs/risks.md`** | Co je na tom rizikové a čím to v produktu mitigujeme | Z toho plyne, co musí být postavené jinak, než by se stavělo bez toho |

V *Životním cyklu projektu* (`~/.claude/RULES.md`) je to druhý krok zakládání: navazuje na `/project` a předává na `/specify`.

**Je opakovatelný sám o sobě.** Druhý běh nad hotovými dokumenty je aktualizace, ne nový začátek – konkurence se hne bez ohledu na to, jestli se zrovna mění zadání.

## Co skill nedělá

- **Nepíše zadání.** Co náš produkt je, pro koho a co má umět, sepisuje `/specify` do `docs/requirements.md`. Tenhle skill mu dodává vstup, ne závěr.
- **Nezakládá projekt.** Strukturu, git a doménové importy dělá `/project`. Chybí-li, upozorní a nabídne ho.
- **Nedělá obchodní ani marketingový plán.** Žádná finanční projekce, žádný kanálový mix, žádná komunikační strategie. Sbírá jen to, z čeho plynou požadavky na produkt.
- **Nedělá osobní brand ani pozicování autora.** To drží `~/Dev/context/brand/brand.md`; tady jde o pozici produktu proti konkurenčním produktům.
- **Neoponuje výsledek.** Posudek čerstvýma očima dělá `/oponent`, kterému se dokumenty předávají stejně jako zadání.
- **Nedělá analytický report z dat.** Na to je `/report`; tady se sbírají fakta o cizích produktech, ne čísla z měření.

## Kdy se přeskakuje

Přeskoč **u všeho, co nemá trh**: interní nástroj, přírůstek do hotového produktu, aplikace na zakázku pro jednoho klienta, konfigurační repozitář, znalostní báze pro sebe. Řekni to nahlas i s důvodem.

**Hraniční případ je zakázka pro klienta**, která bude mít vlastní uživatele. Konkurence tam nerozhoduje o tom, jestli se to postaví – to už je rozhodnuté –, ale pořád rozhoduje o tom, co lidé od takového produktu čekají. Zeptej se, jestli má smysl; nerozhoduj to za uživatele.

**Rizika mají smysl i bez trhu.** Nedává-li konkurenční analýza smysl, ale projekt je netriviální, nabídni běh **jen na `risks.md`** a Fázi 2 a 3 vynech.

## Zásady pro celý průběh

- **Ptej se postupně a přes tool `AskUserQuestion`** – viz `~/.claude/RULES.md`, *Ptej se postupně, ne všechno najednou*.
- **Žádný údaj bez doložení.** Cena, funkce ani počet zákazníků se nezapisuje bez URL a data zjištění. Viz *Ověření*.
- **Nic si nevymýšlej** – ani jméno konkurenta, ani tarif. Viz `~/.claude/RULES.md`, *Při nejistotě se zeptej*.
- **Zapisuj průběžně**, ve chvíli, kdy fakt dorazí, ne až na konci.
- **Nic neprogramuje.** Zákaz implementace z `/specify` platí tím spíš tady – ještě není ani zadání.

------

## Fáze 0 – Pre-flight

Postupuj podle `~/.claude/skills/PREFLIGHT.md`. Navíc:

1. **Zjisti, co v projektu už je** – `docs/competition.md`, `docs/risks.md`, `docs/requirements.md`, `docs/research/`, `README.md`. Z toho urči vstupní bod:

   | Stav | Kde začít |
   |---|---|
   | Ani jeden dokument neexistuje | Fáze 1, celý běh |
   | `competition.md` existuje | Aktualizace: **nepřepisuj**, ověř dosavadní údaje a doplň nové. Sekci *Co poměřujeme* jen potvrď. |
   | `requirements.md` už existuje | Zadání se psalo dřív – **Fázi 1 vynech** a pole hledání odvoď z něj. Řekni, co sis odvodil, a nech to potvrdit. |
   | Existuje jen `risks.md` | Zeptej se, jestli se má doplnit i konkurence, nebo jde jen o revizi rizik. |

2. **Ověř, že projekt má trh.** Platí-li *Kdy se přeskakuje*, řekni to a skonči – nezakládej prázdné dokumenty.

------

## Fáze 1 – Vymezení pole

**Bez tohohle kroku nejde hledat.** Nevíš-li, v jaké kategorii produkt soutěží, najdeš buď všechno, nebo nic.

Zeptej se **na čtyři věci, jednu po druhé**:

1. **Jaký problém to řeší** a komu ho řeší – čí je to dnes bolest.
2. **Co ten člověk dělá dneska**, když to nemá. To je nejdůležitější otázka celého skillu: nejsilnější konkurent bývá tabulka, papír nebo zvyk, ne jiná aplikace.
3. **V jaké kategorii produktu tedy soutěžíme** – jak by to člověk hledal, kdyby to hledal.
4. **Čím se to má hrubě lišit**, pokud už uživatel představu má. Nemá-li, je to v pořádku – od toho je zbytek skillu.

**Je to vymezení pole hledání, ne specifikace.** Neptej se na persony, funkce, MVP ani technologii – to je práce `/specify` a dělá se **až po** tomhle skillu schválně, aby ji analýza mohla ovlivnit.

Zapiš do `docs/competition.md` jako úvodní sekci `## Co poměřujeme`. `/specify` ji pak čte jako hotový vstup a na totéž se neptá podruhé.

------

## Fáze 2 – Rešerše

**Pusť subagenty paralelně, jedním voláním s víc tool calls.** Každý dostane jinou cestu hledání – redundantní agenti najdou tolikrát totéž, kolik jich pustíš.

**Výchozí model, `low`** (`~/.claude/RULES.md`, *Model a effort podle úkolu*). Je to sběr s vynuceným tvarem výstupu a jeho chyba se pozná levně: údaj bez URL se ve Fázi 3 zahodí. Na `xhigh` běží až syntéza a rizika, kde se chyba násobí do zadání.

**Cesty, pravidla výběru i zadání pro agenty drží `~/.claude/skills/discovery/paths.md`.** Přečti si ho celý a řiď se jím: je v něm katalog dvanácti cest ve třech blocích, pravidla, kolik jich pustit a která je povinná, a dvě šablony zadání podle toho, jestli cesta vrací produkty, nebo zjištění.

### Ověření

**Nálezy se nezapisují rovnou.** Projdi je a zahoď:

- co nemá `basis` s funkční URL,
- co má `jistota: nízká` u ceny nebo klíčové funkce – buď údaj ověř sám přes `WebFetch`, nebo ho zapiš jako neznámý,
- duplicity mezi agenty – týž produkt našlo víc cest, sloučí se do jednoho záznamu.

**Co ověření nepřežije, se do dokumentu nedostane.** Vymyšlený konkurent nebo cena o řád vedle je horší než prázdné místo: postaví se na tom rozhodnutí o produktu a nikdo ho nezpochybní, protože vypadá doloženě.

Zapiš do `docs/competition.md` a **u každého údaje nech datum zjištění** (`date +%F`, ne z hlavy – `~/.claude/RULES.md`, *Hodnotu, kterou čte stroj, nepiš*). Ceny stárnou a bez data se nepozná, co je čerstvé.

------

## Fáze 3 – Pozice a odlišení

**Nejsilnější model, `xhigh`.** Tady se z dat stává rozhodnutí, které se propíše do MVP a do každého úkolu pod ním – přesně ten případ, kdy se na úsudku nešetří.

Projdi nálezy s uživatelem a sepiš závěr do sekce `## Naše pozice a odlišení` v témž souboru. Tři skupiny, každá jako seznam:

- **Co musíme mít**, protože to má každý a bez toho nás nikdo nevezme vážně. Tohle je nejcennější výstup celého skillu – jsou to požadavky, na které by se jinak přišlo až po spuštění.
- **Co děláme jinak** a proč si kvůli tomu někdo vybere nás. U každého bodu **řekni, čím je to doložené** – co v rešerši ukazuje, že to konkurence nemá nebo dělá špatně. Odlišení bez opory v datech je přání, ne pozice.
- **Kde vědomě zaostáváme** a proč nám to nevadí. Neprázdné: prázdná skupina znamená, že se tvrdí „budeme lepší ve všem“, což neplatí nikdy.

**Nepiš marketingové claimy.** „Nejjednodušší nástroj na trhu“ není pozice; „jako jediný umí vystavit fakturu bez toho, aby si zákazník založil účet“ je pozice, protože se dá ověřit.

**Sporná místa předlož uživateli**, ne aby je odklikl, ale aby rozhodl. Ptáš se na volbu, ne na potvrzení.

------

## Fáze 4 – Registr rizik

Sepiš `docs/risks.md`. **Není to SWOT** – silné stránky a příležitosti už drží *Naše pozice a odlišení*, tady jsou slabiny a hrozby.

**Odkud rizika brát** – projdi všechny čtyři zdroje, ne jen ten první:

1. **Z rešerše** – konkurent, který to umí líp; nízká bariéra vstupu; velký hráč, který to může přidat jako funkci.
2. **Z povahy produktu** – na čem stojí, co musí platit, aby to fungovalo, kde závisí na někom cizím.
3. **Z pole hledání** – co jsme ve Fázi 1 předpokládali a co se stane, když ten předpoklad neplatí.
4. **Z toho, co uživatel sám ví** a zatím neřekl. Zeptej se: *čeho se na tom projektu bojíš?* Odpověď bývá přesnější než cokoliv, co se dá vyhledat.

U každého rizika:

```markdown
### <Riziko jednou větou>

- **Dopad:** co se stane, když nastane – konkrétně, ne „bylo by to špatné“
- **Pravděpodobnost:** vysoká / střední / nízká, i s tím, z čeho to soudíme
- **Mitigace:** čím tomu čelíme
- **Promítnutí do produktu:** co se kvůli tomu v návrhu změnilo nebo přibylo
```

**Pole *Promítnutí do produktu* je smysl celého souboru.** Bez něj je to seznam obav, který nikoho nezavazuje a nikdo ho nečte. Vyjde-li prázdné, jsou dvě možnosti a obě se musí napsat: buď se produkt kvůli tomu riziku změní – pak to patří do zadání a `/specify` to tam ponese –, nebo riziko **vědomě přijímáme** a napíše se proč (`~/.claude/RULES.md`, *Zapiš i to, co vědomě nemáš*).

**Rizika technického řešení sem nepatří** – „nezvládne to zátěž“, „ta knihovna může skončit“. Ta jdou do sekce *Rizika* v `docs/architecture.md`, protože závisí na zvolené technologii, a ta se ještě nevybrala. Hranice je táž jako mezi požadavky a návrhem: sem produkt a trh, tam řešení.

**Seřaď podle dopadu**, ne podle pořadí, v jakém tě napadla.

------

## Fáze 5 – Předání

**Sebe-revize** – projdi oba dokumenty:

1. **Doložení** – má každý faktický údaj URL a datum? Údaj bez opory přesuň mezi otevřené otázky, nebo smaž.
2. **Prosakování hranice** – není v `competition.md` popis našeho produktu? Není v `risks.md` technické riziko? Přesuň.
3. **Neprázdnost** – má *Kde vědomě zaostáváme* aspoň jednu položku? Má každé riziko vyplněné *Promítnutí do produktu*?
4. **Vymyšlené věci** – je tam jméno, číslo nebo tvrzení, které jsi neměl od uživatele ani ze zdroje? To je nález.

**Oponentura.** Nabídni `/oponent docs/competition.md` – rešerši psal ten, kdo si zároveň přeje, aby produkt vyšel, a to je přesně ta zaujatost, kterou má posudek chytat. Panel hledisek si sestaví sám.

**Předání.** Po schválení nabídni `/specify`. Ten si dokumenty najde sám a **nebude se ptát na to, co je v nich** – zejména sekci *Co poměřujeme* bere jako hotový vstup.

------

## Časté chyby

| Chyba | Proč je to chyba |
|---|---|
| Hledat jen přímé konkurenty | Nejsilnější konkurent je zvyk. Cesta *Náhradní řešení* existuje právě proto. |
| Opsat marketingové sliby z webu konkurenta jako fakta o funkcích | Web říká, co chtějí prodat, ne co produkt umí. Doloženo je to, co jde ověřit v dokumentaci, ceníku nebo recenzi. |
| Napsat pozici jako claim | „Jednodušší a rychlejší“ se nedá ověřit ani vyvrátit, takže z toho neplyne žádný požadavek. |
| Nechat *Promítnutí do produktu* prázdné | Riziko, které nic nemění, je poznámka. Buď se promítne, nebo se výslovně přijme. |
| Sepsat rizika technického řešení | Technologie se ještě nevybrala, takže riziko její volby je dohad. Patří do `architecture.md`, až volba padne. |
| Pustit skill na interní nástroj | Nemá trh. Prázdná analýza konkurence předstírá úvahu, která se nestala. |

------

## Fáze 6 – Závěr

```
## Discovery hotová

**Dokumenty**
- docs/competition.md – <počet> konkurentů, <počet> ověřených údajů
- docs/risks.md – <počet> rizik (<počet> promítnutých do produktu, <počet> přijatých)

**Co z toho plyne pro produkt**
- Musíme mít: <počet> položek
- Odlišujeme se: <počet> položek
- Vědomě zaostáváme: <počet> položek

**Zahozeno při ověření**
- <počet> nálezů bez doložení

**Otevřené otázky**
- [seznam, nebo „žádné“]

**Další krok**
- [/oponent nad competition.md / /specify]
```

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Podklady jsou hotové a ověřené, můžeme na zadání.`
- `Podklady hotové nejsou – brání tomu: <konkrétní seznam>.`

Nedávala-li analýza konkurence smysl a běželo se jen na rizika, platí druhá dvojice:

- `Registr rizik je hotový a ověřený, konkurenci jsme vynechali – <důvod>. Můžeme na zadání.`
- `Registr rizik hotový není – brání tomu: <konkrétní seznam>.`
