# Katalog zásahů

Co `/slim` v souboru hledá, jak to pozná a co s tím. Čte se ve *Fázi 2* a *Fázi 3*.

## Obsah

- [Kdy text smí z paušálu pryč](#kdy-text-smí-z-paušálu-pryč)
- [Kategorie zásahů](#kategorie-zásahů)
- [Slabé pravidlo](#slabé-pravidlo)
- [Pravidla, která nabobtnání vyrábějí](#pravidla-která-nabobtnání-vyrábějí)
- [Co se vyčísluje a jak](#co-se-vyčísluje-a-jak)

## Kdy text smí z paušálu pryč

Paušál je to, co se načte do každé session bez ptaní – soubory, které Claude Code najde sám, a jejich `@` importy. Rozhodující otázka u každé sekce: **kdo ten text čte a kdy.**

- **Zůstává, co se uplatní v každé odpovědi** nebo co model potřebuje, aniž ví, že to potřebuje – prevence. Tabulka zakázaných termínů pryč nesmí, protože model neví, že sahá po nezavedeném slově; smí ale ztenčit na „místo X piš Y, platí na Z“.
- **Pryč smí, co se uplatní jen při určité činnosti** – zakládání projektu, zápis do `docs/`, pouštění agentů, měření, návrh modelu –, ale jen když **tu činnost opravdu něco spustí**: skill si soubor přečte v přípravě, test ho vynucuje, nebo v paušálu zůstane jednořádkový spouštěč („než pustíš agenta, načti si `delegation.md`“). Odkaz bez mechanismu je přání.
- **Nejvýš jeden krok od paušálu.** Soubor, na který odkazuje soubor načítaný odkazem, se v praxi nenačte. Spouštěč proto stojí vždy v souboru, který se čte pokaždé.
- **Kde je cena nedodržení vysoká a spouštěč nejistý, pravidlo zůstává** (typicky git: `add -A`, heredoc, řetězení za blokovatelný příkaz) – jen zkrácené.
- **Čte-li soubor jediný skill, patří k němu**; čte-li ho víc skillů, do sdíleného místa (`~/.claude/`, `~/.claude/skills/`), ne dovnitř cizího skillu.
- **Veřejné × soukromé:** obecné pravidlo patří do veřejného `~/.claude/`, know-how a klientský obsah do `~/Dev/context/`. Přesun nesmí zveřejnit, co veřejné být nemá.

## Kategorie zásahů

| Kategorie | Jak se pozná | Co s tím | Rozhoduje |
|---|---|---|---|
| **Přesun na odkaz** | sekce platí jen při jedné činnosti | přesun celé sekce do souboru načítaného odkazem, v paušálu spouštěč | uživatel |
| **Tenké jádro + výklad stranou** | soubor nese pravidlo i jeho rozvahu; roste s každým záznamem | v paušálu jen tabulka nebo pravidla, výklad do souboru ke správci | uživatel |
| **Jiný čtenář** | text je dokumentace, ne instrukce – co která kontrola hlídá, historie kontraktu | do souboru pro toho čtenáře (`tests/README.md`), v paušálu odkaz | uživatel |
| **Doklad** | datum, incident, citace, jméno projektu, historie pravidla („do té doby tu stálo“, „upřesněno …“), měření sloužící jen jako důkaz | škrt; pointa zůstane jednou větou, doklad nese commit | rovnou |
| **Slabé pravidlo** | viz níž | zrušení | uživatel |
| **Duplicita s jasným vítězem** | totéž na dvou místech, jedno je zjevně domov | ve druhém odkaz nebo nic | rovnou |
| **Duplicita bez vítěze** | dvě místa, obě obhajitelná, nebo se liší obsahem | sloučení; které místo vyhraje | uživatel |
| **Překryv se systémovým promptem** | pravidlo říká totéž co Claude Code sám (jazyk odpovědí, stručnost, git) | škrt, pokud nepřidává nic navíc | uživatel |
| **Komprese** | esejistické odstavce, kontrastní páry, „**Proč:**“ nad rámec věty, opakování teze | přepis na kratší bez změny významu | rovnou |
| **Nabobtnávací pravidlo** | viz níž | zrušení nebo přepis | uživatel |

**„Rovnou“ platí jen tehdy, když se nemění význam.** Jakmile škrt nebo komprese ubere podmínku, výjimku nebo rozsah pravidla, je to rozhodnutí uživatele.

## Slabé pravidlo

Pravidlo, které nic nerozhoduje, zabírá místo každé session a navíc ředí ta, která rozhodují. Kandidát na zrušení je, když platí aspoň jedno:

- **Model to dělá i bez něj** – „piš srozumitelně“, „buď pečlivý“, „ověř si, že kód funguje“.
- **Je vágní** – nejde podle něj rozhodnout konkrétní případ; test: dala by se podle něj zamítnout konkrétní změna?
- **Opakuje hranici vynucenou jinde** – kontrolou, hookem, souhlasem z terminálu. Věta v kontextu je druhá kopie téže hranice.
- **Míří na situaci, která už nenastává** – odstraněný nástroj, zrušený skill, vyřešený incident.
- **Popisuje místo předepisování** – vysvětluje, jak něco funguje, a z výkladu neplyne žádný pokyn.
- **Je výjimka pro jeden projekt** v souboru, který platí pro všechny.

Pravidlo se neruší proto, že je dlouhé, ale proto, že nic nerozhoduje. Dlouhé a nosné se komprimuje.

## Pravidla, která nabobtnání vyrábějí

Soubor nenaroste sám – narostl, protože nějaké pravidlo žádá ke každému zápisu text navíc. Bez revize takového pravidla se úklid do měsíce vrátí. Hledej ve stromu načítání i v normách, podle kterých se do něj píše (`structure.md`, `skills.md`, rozřazovací sekce „co sem nepatří“):

- povinnost psát ke každému pravidlu zdůvodnění, a to v tomtéž souboru,
- povinnost zapisovat doklad, datum, incident nebo počet výskytů k pravidlu,
- povinnost zapisovat zamítnuté varianty a historii přímo k pravidlu, ne do `decisions.md`,
- povinnost „zapsat i to, co se vědomě nemá“ do souboru, který se načítá pokaždé,
- rozřazovací test, jehož reziduální větev („nic z toho → sem“) posílá do paušálu všechno, co jinam nepasuje,
- zvyk bez pravidla – poznáš ho z historie: `git log -p` největšího rostoucího souboru za poslední týdny a co v přírůstcích převažuje.

Návrh zní vždy konkrétně: zrušit, nebo přepsat na verzi, která text navíc posílá do commitu nebo `decisions.md`, a doplnit rozřazovací test o větev „platí jen při činnosti X → podmíněný soubor“.

## Co se vyčísluje a jak

- **Úspora se počítá z textu, který se opravdu odstraní**, ne z celé sekce nebo odstavce, ve kterém stojí značka. Počet značek z `measure.py sections` je vodítko, kde hledat, ne velikost úspory – odstavec s „Doloženo“ nese většinou i nosné pravidlo.
- **Znaky, ne bajty.** Limit je ve znacích; `wc -c` dá u češtiny zhruba o desetinu víc.
- **Přesun ušetří v kontextu, ne v součtu.** Soubor stranou smí narůst; vyčísluje se paušál.
- **Spouštěč a nový úvod vracejí část úspory** – u přesunu sekce počítej s tím, že v paušálu zůstane pár set znaků.
