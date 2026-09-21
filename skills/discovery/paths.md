# Cesty rešerše

Katalog cest, kterými `/discovery` hledá, a šablony zadání pro agenty. Vybírá se z něj dvakrát: blok **Poptávka** ve *Fázi 2 – Doklady poptávky*, zbylé tři bloky ve *Fázi 3 – Rešerše konkurence*. Každý z těch dvou výběrů má vlastní rozpočet cest, viz *Pravidla výběru*.

- [Katalog cest](#katalog-cest)
- [Pravidla výběru](#pravidla-výběru)
- [Zadání pro agenta](#zadání-pro-agenta)

## Katalog cest

Sloupec *Živí* říká, do kterého dokumentu ta cesta ústí – cesta, jejíž dokument projekt nevede, má menší cenu. Sloupec *Vrací* určuje tvar výstupu, viz *Zadání pro agenta* níž.

**Poptávka** – hledá lidi s problémem, ne produkty. Pouští se ve Fázi 2 a živí `demand.md`.

| Cesta | Co hledá | Živí | Vrací |
|---|---|---|---|
| **Hlas problému** | Kde lidé ten problém sami popisují – diskuse, fóra, dotazy, recenze, skupiny, komentáře pod články. Hledá **popis potíže, ne poptávku po nástroji**. **Povinná cesta**, viz pravidla níž. | demand | zjištění |
| **Ochota platit** | Platí za tenhle problém dnes někdo, a kolik – placené služby, agentury, lidská práce, doplňky a šablony, kurzy o tom, jak to obejít. Útrata je nejtvrdší doklad poptávky, jaký se dá zvenčí zjistit. | demand, pricing | zjištění |
| **Objem a jazyk hledání** | Kolik lidí to hledá a jakými slovy – a jestli jich přibývá, nebo ubývá. Slouží zároveň jako korektiv: problém, který nikdo nehledá, může být neexistující, nebo jen nepojmenovaný, a to jsou dva velmi různé závěry. | demand, glossary | zjištění |

**Kdo to dělá** – hledá produkty a služby.

| Cesta | Co hledá | Živí | Vrací |
|---|---|---|---|
| **Přímí konkurenti** | Produkty ve stejné kategorii, které řeší týž problém týmž způsobem. | competition | produkty |
| **Náhradní řešení** | Čím to lidé řeší, aniž by na to měli nástroj – tabulka, mail, papír, obecný nástroj ohnutý k tomuhle. **Povinná cesta**, viz pravidla níž. | competition | produkty |
| **Sousední kategorie** | Produkty, které dělají něco jiného, ale mohly by to pohltit jako funkci. Odpovídá na otázku, co se stane, když se o kategorii začne zajímat někdo velký. | competition, risks | produkty |
| **Otevřený a self-hosted software** | Bezplatné a provozovatelné u sebe. Nekonkuruje cenou, ale existencí, a u technického publika rozhoduje víc než placené produkty. | competition | produkty |
| **Kdo to zkusil a skončil** | Zaniklé produkty a zrušené služby v kategorii – a **proč skončily**. Cizí post-mortem je nejlevnější zdroj rizik, jaký existuje: ta rizika už někdo zaplatil. | risks | produkty |
| **Lokální trh** | Je-li produkt vázaný na jazyk, legislativu nebo měnu, hledej zvlášť česká a evropská řešení. Globální hledání je přehluší. | competition | produkty |

**Co lidé chtějí** – hledá potřeby a očekávání.

| Cesta | Co hledá | Živí | Vrací |
|---|---|---|---|
| **Hlas zákazníka** | Recenze, diskuse, fóra, issue trackery. Na co si lidé u stávajících řešení stěžují a co jim chybí. Říká, kde je díra – tedy kde má smysl se odlišit. | competition, scenarios | zjištění |
| **Migrace odjinud** | Jak lidé přecházejí od stávajícího řešení a co si nesou: formáty exportu, historická data, zvyky. Je to zároveň požadavek („import z X“) a bariéra vstupu. | competition, scenarios | zjištění |
| **Integrace a ekosystém** | Na co se v téhle kategorii běžně napojuje – účetnictví, platby, kalendáře, přihlašování, marketplace. **Čekaná integrace, kterou nemáš, je důvod k odmítnutí** a z landing page konkurence se nedozví. | competition | zjištění |
| **Terminologie oboru** | Jak se v kategorii čemu říká – v produktech, v dokumentaci, v řeči zákazníků. Produkt pojmenovaný po svém lidé nenajdou a nepochopí. | glossary | zjištění |

**Co se musí** – hledá omezení, která nevzejdou od konkurence ani od uživatele.

| Cesta | Co hledá | Živí | Vrací |
|---|---|---|---|
| **Regulace a povinnosti** | Co v téhle kategorii ukládá právo: osobní údaje, účetnictví a doklady, přístupnost, spotřebitelské právo, oborová regulace. **Tvrdé požadavky, na které se nikdo neptá, dokud nepřijdou pozdě.** | risks, competition | zjištění |
| **Cenové modely kategorie** | Jak se v tomhle oboru vůbec účtuje – za uživatele, za transakci, paušálem, freemium, jednorázově – a co z toho plyne za limity a tarify. Jiná otázka než „kolik stojí konkurent X“: ta patří k *Přímým konkurentům*. | pricing | zjištění |

## Pravidla výběru

- **Ve Fázi 2 vyber 2 až 3 cesty z bloku *Poptávka*.** Blok má tři cesty a pouští se celý jen tam, kde na verdiktu hodně záleží; dvě stačí, když jedna z nich vrátí tvrdý doklad (zaplacené řešení, jmenovaní lidé s problémem).
- **Ve Fázi 3 vyber 4 až 6 cest ze zbylých tří bloků.** Pod čtyři se nepokryjí bloky, nad šest se nálezy začnou opakovat. **Rozpočty se nesčítají ani nepůjčují**: cesta k poptávce se nedá nahradit cestou ke konkurenci, protože odpovídá na jinou otázku.
- **Výběr předlož uživateli přes `AskUserQuestion`** dřív, než kohokoliv pustíš. Agenti na `low` jsou levní, ale čas na jejich doběhnutí ne.
- **Povinná je v každém výběru právě jedna cesta:** *Hlas problému* ve Fázi 2 a *Náhradní řešení* ve Fázi 3. Obě jsou ty, na které se zapomene – za první je odpověď na „chce to někdo“, za druhou největší konkurent. **Druhá povinná v témže výběru schválně není**: při čtyřech cestách by dva pevné sloty udělaly z volby ozdobu a při dvou by z ní nezbylo nic.
- **Ve Fázi 3 vyber aspoň jednu cestu z každého ze svých tří bloků** – *Poptávka* mezi ně nepatří, ta se pouští ve Fázi 2. Samé produkty dají přehled trhu a nula požadavků; samá zjištění dají seznam přání bez opory v tom, co existuje.
- **Cestu nerozšiřuj, aby jich stačilo pustit míň.** Kapacitu neurčuje šířka zadání, ale výstup agenta – vrátí podobný počet nálezů, ať má zadání úzké, nebo široké. Rozšířením se počet nezvedne, jen se rozptýlí jejich původ.
- **Vede-li projekt dokument ze sloupce *Živí*, ber jeho cestu přednostně.** Nevede-li žádný, na který cesta ústí, je to nejslabší kandidát z celého katalogu.
- **Volbu dolož** – u každé zvolené cesty jednou větou, co k ní vedlo, a jmenuj **jednu, kterou jsi vědomě nevzal, a proč**. Nevybraná cesta nevrátí nula nálezů, ale neexistenci, a ta neprojde žádným počítadlem v závěru (`~/.claude/RULES.md`, *Zapiš i to, co vědomě nemáš*).
- **Doklad poptávky se nezapočítává mezi nálezy konkurence.** Cesty bloku *Poptávka* mají vlastní přísnější měřítko: doklad musí mluvit o problému, ne o kategorii produktu. Nález, který mluví o nástrojích, patří do `competition.md`, ne do `demand.md`.
- **Běžel-li `/discovery` už dřív** (Fáze 0 to zjistila), začni panelem toho běhu. Nález, který se vrátí v téže cestě, znamená, že se nezměnil; nález, který zmizel s vyměněnou cestou, neznamená nic.

## Zadání pro agenta

Doplň pole hledání z Fáze 1 a cestu. **Tvar výstupu se řídí sloupcem *Vrací*** – cesta, která hledá povinnosti nebo pojmy, nemá co dát do pole `pricing`, a kdyby ho měla vyplnit, vymyslí si ho.

Společná hlavička:

```
Hledáš podklady pro produkt, který se teprve staví. Nemáš žádný kontext z předchozích
rozhovorů – máš jen tohle zadání.

CO SE STAVÍ: <shrnutí Fáze 1 – problém, pro koho, čím to dnes řeší, kategorie>
TVOJE CESTA: <jméno cesty a celý její popis ze sloupce „Co hledá“>

Prohledej web. Vrať JSON, nic jiného.

PRAVIDLA:
- Údaj, který nemáš z konkrétní stránky, NEUVÁDĚJ. Prázdné pole je lepší než odhad.
- Ceny a znění předpisů opisuj doslova. Nepřepočítávej, nezaokrouhluj, neparafrázuj.
- "confidence" dej nízkou všude, kde jsi údaj odvodil místo přečetl.
- Nehodnoť a nedoporučuj. Sbíráš fakta, závěry dělá někdo jiný.
- Vrať nejvýš 8 nálezů – ty nejrelevantnější. Ne seznam všeho, co existuje.
```

**Vrací produkty:**

```
U každého nálezu zjisti: jméno, URL, co to umí (konkrétně, ne marketingově), cenový model
a konkrétní ceny, na koho to cílí, v jakém je stavu, čím je to omezené.

[{"name": "...", "url": "...", "features": ["..."], "pricing": "...", "target_audience": "...",
  "status": "aktivní | zaniklý <kdy a proč>", "limitations": ["..."],
  "basis": ["URL, ze které to je"], "confidence": "vysoká|střední|nízká"}]

U zaniklého produktu je pole "status" to nejdůležitější, co vracíš – uveď doložený důvod
konce, ne domněnku. Nenajdeš-li ho, napiš "zaniklý, důvod neznámý".
```

**Vrací zjištění:**

```
U každého nálezu zjisti: co jsi zjistil, jakého je to druhu a co z toho plyne pro produkt,
který se staví.

[{"finding": "...", "type": "stížnost | očekávaná funkce | povinnost | pojem | cenový model",
  "implication": "jednou větou, co by produkt měl umět nebo splnit",
  "basis": ["URL, ze které to je"], "confidence": "vysoká|střední|nízká"}]

Pole "implication" musí být konkrétní a ověřitelné. "Musí to být jednoduché" není
zjištění; "uživatelé si stěžují, že export nejde spustit bez administrátora" je.
```
