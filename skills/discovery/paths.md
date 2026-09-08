# Cesty rešerše

Katalog cest, kterými `/discovery` hledá, a šablony zadání pro agenty. Vybírá se z něj ve *Fázi 2 – Rešerše*; pravidla, kolik cest pustit a co je povinné, jsou tam.

## Katalog cest

Sloupec *Živí* říká, do kterého dokumentu ta cesta ústí – cesta, jejíž dokument projekt nevede, má menší cenu. Sloupec *Vrací* určuje tvar výstupu, viz *Zadání pro agenta* níž.

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

- **Vyber čtyři až šest cest.** Pod čtyři se nepokryjí bloky, nad šest se nálezy začnou opakovat.
- **Výběr předlož uživateli přes `AskUserQuestion`** dřív, než kohokoliv pustíš. Agenti na `low` jsou levní, ale čas na jejich doběhnutí ne.
- **Náhradní řešení je povinná cesta**, ať je produkt jakýkoliv. Je to ta, na kterou se vždycky zapomene, a bývá za ní největší konkurent. Druhá povinná schválně není – dva pevné sloty ze čtyř by z volby udělaly ozdobu.
- **Vyber aspoň jednu cestu z každého bloku.** Samé produkty dají přehled trhu a nula požadavků; samá zjištění dají seznam přání bez opory v tom, co existuje.
- **Cestu nerozšiřuj, aby jich stačilo pustit míň.** Kapacitu neurčuje šířka zadání, ale výstup agenta – vrátí podobný počet nálezů, ať má zadání úzké, nebo široké. Rozšířením se počet nezvedne, jen se rozptýlí jejich původ.
- **Vede-li projekt dokument ze sloupce *Živí*, ber jeho cestu přednostně.** Nevede-li žádný, na který cesta ústí, je to nejslabší kandidát z celého katalogu.
- **Volbu dolož** – u každé zvolené cesty jednou větou, co k ní vedlo, a jmenuj **jednu, kterou jsi vědomě nevzal, a proč**. Nevybraná cesta nevrátí nula nálezů, ale neexistenci, a ta neprojde žádným počítadlem v závěru (`~/.claude/RULES.md`, *Zapiš i to, co vědomě nemáš*).
- **Běžel-li `/discovery` už dřív** (Fáze 0 to zjistila), začni panelem toho běhu. Nález, který se vrátí v téže cestě, znamená, že se nezměnil; nález, který zmizel s vyměněnou cestou, neznamená nic.

## Zadání pro agenta

Doplň pole hledání z Fáze 1 a cestu. **Tvar výstupu se řídí sloupcem *Vrací*** – cesta, která hledá povinnosti nebo pojmy, nemá co dát do pole „cena“, a kdyby ho měla vyplnit, vymyslí si ho.

Společná hlavička:

```
Hledáš podklady pro produkt, který se teprve staví. Nemáš žádný kontext z předchozích
rozhovorů – máš jen tohle zadání.

CO SE STAVÍ: <shrnutí Fáze 1 – problém, pro koho, kategorie>
TVOJE CESTA: <jméno cesty a celý její popis ze sloupce „Co hledá“>

Prohledej web. Vrať JSON, nic jiného.

PRAVIDLA:
- Údaj, který nemáš z konkrétní stránky, NEUVÁDĚJ. Prázdné pole je lepší než odhad.
- Ceny a znění předpisů opisuj doslova. Nepřepočítávej, nezaokrouhluj, neparafrázuj.
- "jistota" dej nízkou všude, kde jsi údaj odvodil místo přečetl.
- Nehodnoť a nedoporučuj. Sbíráš fakta, závěry dělá někdo jiný.
- Vrať nejvýš 8 nálezů – ty nejrelevantnější. Ne seznam všeho, co existuje.
```

**Vrací produkty:**

```
U každého nálezu zjisti: jméno, URL, co to umí (konkrétně, ne marketingově), cenový model
a konkrétní ceny, na koho to cílí, v jakém je stavu, čím je to omezené.

[{"jmeno": "...", "url": "...", "co_umi": ["..."], "cena": "...", "cili_na": "...",
  "stav": "aktivní | zaniklý <kdy a proč>", "omezeni": ["..."],
  "basis": ["URL, ze které to je"], "jistota": "vysoká|střední|nízká"}]

U zaniklého produktu je pole "stav" to nejdůležitější, co vracíš – uveď doložený důvod
konce, ne domněnku. Nenajdeš-li ho, napiš "zaniklý, důvod neznámý".
```

**Vrací zjištění:**

```
U každého nálezu zjisti: co jsi zjistil, jakého je to druhu a co z toho plyne pro produkt,
který se staví.

[{"zjisteni": "...", "typ": "stížnost | očekávaná funkce | povinnost | pojem | cenový model",
  "co_z_toho_plyne": "jednou větou, co by produkt měl umět nebo splnit",
  "basis": ["URL, ze které to je"], "jistota": "vysoká|střední|nízká"}]

Pole "co_z_toho_plyne" musí být konkrétní a ověřitelné. "Musí to být jednoduché" není
zjištění; "uživatelé si stěžují, že export nejde spustit bez administrátora" je.
```
