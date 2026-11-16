---
name: package
description: Skill se použije, když uživatel zadá "/package" se jménem skillu, víc skillů nebo domény z ~/Context, nebo chce něco z toho dát jinému člověku – "udělej z toho balíček", "exportuj ten skill, ať ho můžu poslat", "připrav to manželce na flashku", "instalační balíček pro kolegu". Sestaví samostatný přenositelný balíček: všechno, na co zadané soubory odkazují, sebere do jednoho adresáře nebo zipu, sdílené soubory vepíše nebo přibalí, vlastní typy agentů nahradí vestavěnými, všechny cesty převede na relativní a odstraní autorovy cesty a osobní věci. Přiloží INSTALL.md, podle kterého Claude příjemce balíček nainstaluje – zeptá se, kam co uložit, a doinstaluje nástroje pro Windows, macOS i Linux. Na rozdíl od instalačního promptu v README skillu, který stahuje z GitHubu jen veřejné soubory, nese balíček i soukromé doménové znalosti a funguje offline. Na rozdíl od /skill skilly nezakládá ani neupravuje; zdroj nechává beze změny.
argument-hint: <skill nebo doména…>
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, WebSearch, WebFetch]
---

# Package

## Co skill dělá

Ze zadaných věcí – jednoho nebo víc skillů, domény z `~/Context/` nebo jejich kombinace – udělá **autonomní přenositelný balíček**: adresář nebo zip, který se pošle komukoliv a jeho Claude ho nainstaluje podle přiloženého `INSTALL.md`. Balíček nic nevyžaduje z autorova disku a žádnou jeho cestu nenese. Kam se co nainstaluje, rozhoduje až příjemce.

Režimy nemá: chová se vždycky stejně a argumentem je jen seznam toho, co zabalit.

## Co skill nedělá

- **Nezakládá ani neupravuje skilly.** Na to je `/skill`. Tenhle skill zdroj jen čte a všechny úpravy dělá na kopii v balíčku.
- **Nenahrazuje instalaci z GitHubu.** Instalační prompt v README skillu stahuje veřejné soubory i se sdílenými závislostmi; balíček je offline kopie pro konkrétního člověka a nese i soukromou znalost, která v repozitáři není.
- **Neposílá.** Balíček nese kopii soukromé znalosti; komu ho dát, rozhoduje uživatel.
- **Nebalí nástroje mimo Clauda.** Programy z Homebrew a podobných správců, pluginy, MCP konektory a balíčky Pythonu do balíčku nejdou – `INSTALL.md` místo nich řekne, jak je doinstalovat.

## Jak je to postavené uvnitř

| Krok | Kdo | Proč zrovna on |
|---|---|---|
| Mapa odkazů a kontrola hotového balíčku | `refs.py` v adresáři skillu | Deterministické hledání: grep z hlavy minul odkaz schovaný za jiným vzorem a zbytek po úpravě nenašel. |
| Co vepsat, co přibalit, co odstranit | vlastní | Úsudek nad každým odkazem; nikdo jiný neví, co z cizího souboru skill opravdu potřebuje. |
| Úpravy kopií a `INSTALL.md` | vlastní | Text musí po zásahu dávat smysl a držet pravidla psaní. |
| Čtení balíčku jako Claude příjemce | agent typu `reader` | Nezná session ani autorův disk, takže uvidí, co příjemce; zápis mu chybí schválně. |
| Ověření instalačních příkazů | `WebSearch` | Jméno balíčku ve `winget` nebo `apt` se nehádá. |

**Skript a agent jsou implementační detail, ne rozhraní.** Závazné je: zdroj se nemění; v balíčku nezůstane žádná absolutní ani autorova cesta; každý odkaz vede dovnitř balíčku; `INSTALL.md` nechá příjemce rozhodnout, kam co uložit; sporné osobní věci se bez schválení nevynesou.

Zadání pro čtenáře drží [`briefs.md`](briefs.md), kostru `INSTALL.md` [`template.md`](template.md). Načti si je ve fázi, která je potřebuje.

## Zásady pro celý průběh

**Zdroj je jen ke čtení.** Všechno se kopíruje do balíčku a upravuje tam. Úprava zdroje by tiše změnila autorovu instalaci.

**Autorova cesta se nepřenáší nikam** – ani do odkazu, ani do `INSTALL.md` jako informace, odkud soubor pochází. Výjimkou jsou jen obecná místa Claude Code v `INSTALL.md` (složka se skilly, s agenty, uživatelský `CLAUDE.md`), protože jsou u každého příjemce stejná. Cokoliv jiného prozrazuje, jak má autor uspořádaný disk, a u příjemce stejně nevede nikam.

**Odkazy jsou relativní k souboru, ve kterém stojí.** Napevno zapsaná cesta do cílové instalace (`~/.claude/skills/<jméno>/…`) by rozhodla za příjemce, kam co patří. Claude příjemce odkazy přepíše jen tehdy, když části balíčku rozdělí jinam.

**Rozhodnutí podle druhu odkazu:**

| Odkaz vede na | Co s ním |
|---|---|
| soubor, který zadaná věc čte celý – pravidla, zadání agentů, šablony, skripty | **přibal** a pusť na něj mapu odkazů znovu |
| sdílený soubor, ze kterého je potřeba věta nebo sekce – příprava skillu, škála závažnosti, model a effort, styl odpovědí | **vepiš** to podstatné na místo odkazu a soubor nepřibaluj; stojí-li pravidlo ve větě už samo, odkaz jen smaž |
| vymezení vůči jinému skillu nebo doméně, která v balíčku není | **smaž**, nebo převeď na prostou zmínku bez cesty; věta musí dávat smysl i bez ní |
| autorův hlas a korpus – `Compose/`, `Archive/`, `Brand/`, `Organizations/`, `Speaking/`, klientské složky | **nepřibaluj nikdy**; zmínku přepiš obecně („autorský hlas“) |
| historie a rozvaha – `decisions.md`, `done.md`, `todo.md` | **nepřibaluj**; za běhu se nečtou a jsou plné cest, které u příjemce nevedou nikam |
| vlastní typ agenta | **nahraď vestavěným `general-purpose`** a pravidla z jeho definice přesuň do zadání jako společný úvod; hranici, kterou typ držel nástroji, teď drží zadání a kopie vstupu, ne originál |
| zdroj nebo citace s cestou k soukromé kopii | zdroj ponech, cestu smaž |
| nástroj mimo Clauda – program, plugin, konektor, balíček Pythonu | **nepřibaluj**; zapiš ho do závislostí v `INSTALL.md` |

**Jednoznačně osobní odstraň rovnou, sporné předlož.** Jméno autora, jeho soukromá cesta a odkaz na jeho hlas jsou jednoznačné. Sporné je všechno, co o autorovi prozrazuje příklad v pravidle: osobní preference vydávaná za obecnou, firmy, ve kterých pracoval, jeho produkty, kurzy a ceny, klienti, adresa sídla nebo bydliště, interní údaje firmy. Rozhoduje uživatel, protože jen on ví, co smí k příjemci. **Dokud nerozhodne, sporný úsek v balíčku není** – nahraď ho neutrálním příkladem se stejným pravidlem, nebo ho odstraň, a v předložení řekni, co jsi udělal; vrátit ho jde, odeslaný balíček ne.

**Žádný soubor v balíčku se nejmenuje jako instrukce jiného nástroje** (`AGENTS.md`, `GEMINI.md` a obdoby, bez ohledu na velikost písmen). Jiný AI nástroj u příjemce by ho četl jako svoje pokyny. Má-li ho zdroj, přejmenuj ho v balíčku a odkazy srovnej.

## Fáze 0 – Příprava

Společný začátek je v `~/.claude/skills/preflight.md`. **Body 1 až 3 vynechávám:** skill nad projektem neběží, nic necommituje a zapisuje jen do `~/Downloads`. Předpoklady místo nich:

1. **Rozpoznej vstup.** Každou položku argumentu najdi: skill v `~/.claude/skills/<jméno>/`, doménu nebo soubor v `~/Context/`. Neexistuje-li, nabídni nejbližší jména, místo hlášky o chybě. Bez argumentu se zeptej, co zabalit.
2. **Zeptej se na tvar** přes `AskUserQuestion`: adresář `~/Downloads/<jméno>/`, nebo jeden zip `~/Downloads/<jméno>.zip`. Jméno balíčku je jméno jediné položky, u víc položek se na něj zeptej v textu.
3. **Existuje-li cíl už, nepřepisuj ho** – ukaž, co v něm je, a zeptej se, jestli ho nahradit, nebo zvolit jiné jméno.
4. **Ověř skript:** `python3 -I ~/.claude/skills/package/refs.py --help`. Selže-li, řekni to a skonči – bez mapy odkazů by se balilo podle dojmu.

## Fáze 1 – Mapa odkazů

1. `python3 -I ~/.claude/skills/package/refs.py scan <položky>` – odchozí odkazy všech souborů vstupu.
2. Ke každému odkazu urči podle tabulky v *Zásadách* jeho osud: přibalit, vepsat, smazat, přepsat obecně, závislost.
3. Na každý soubor, který přibalíš, pusť `scan` znovu – i on má odkazy. Opakuj, dokud nepřibude nic nového.
4. **Projdi i text, nejen odkazy:** jméno autora ve všech tvarech, přivlastnění autorovi („jeho hlas“, „moje preference“), jména klientů. Skript je najde až při kontrole, ale rozhodnout o nich patří sem.
5. **Předlož mapu** jedním přehledem v běžném Markdownu: co se přibalí, co se vepíše a kam, co se odstraní, jaké jsou závislosti. Sporné osobní věci k tomu **dávkou** k rozhodnutí:

   ```
   **Ke schválení** – odpověz „vše“, nebo vyjmenuj čísla, která chceš jinak.

   1. „<úsek>“ (<soubor>) – <proč je sporný> → <návrh: odstranit / ponechat / přepsat na …>
   ```

   Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo. Nejsou-li sporné věci, jen oznam mapu a pokračuj.

## Fáze 2 – Sestavení

1. **Rozvrh balíčku:** v kořeni `INSTALL.md`, každý skill ve vlastním podadresáři. Soubor, který čte jen jeden skill, leží v jeho adresáři (u pravidel `rules/`), aby se skill nainstaloval jako jeden celek. Soubor, který čtou dva a víc skillů, nebo doména zadaná sama, leží v kořeni balíčku pod vlastním jménem – jen jednou.
2. **Zkopíruj** soubory podle mapy. Skripty a vedlejší soubory skillu jdou celé, `__pycache__` a podobné ne.
3. **Uprav kopie** podle mapy: vepiš, smaž, přepiš odkazy na relativní, nahraď typy agentů. Ve hlavičce skillu vyřaď z `description` sousedy, kteří v balíčku nejsou – popis rozhoduje o vyvolání a cizí jména by u příjemce mátla.
4. **Po každém smazání přečti okolí**: věta, která na smazané místo navazovala („viz výš“, výčet, úvod sekce), se musí opravit hned.
5. **README skillu:** sekci o instalaci nahraď odkazem na `INSTALL.md` – prompt na GitHub u příjemce nedává smysl.
6. **Napiš `INSTALL.md`** podle [`template.md`](template.md). Česky podle `~/Context/Text/text.md` a `~/Context/Text/typography.md`; čte ho Claude, ale rozhoduje podle něj člověk. Instalační příkazy nástrojů ověř přes `WebSearch`, nehádej je.

## Fáze 3 – Kontrola skriptem

`python3 -I ~/.claude/skills/package/refs.py check <balíček> --term <jméno> --term <příjmení> --term <login>` – za `--term` dej kmeny jména a příjmení autora (tak, aby chytily všechny pády), jeho login a jména klientů, která se v mapě objevila. Výstupem jsou absolutní cesty, odkazy bez cíle v balíčku, zmínky o vlastních skillech a typech agentů mimo balíček, zadaná slova a vyhrazená jména souborů.

Každý nález oprav a pusť kontrolu znovu. **Nález, který je správně** – obecné jméno souboru zmíněné jako pojem, ne jako odkaz –, ponech jen vědomě a vypiš ho v závěru.

## Fáze 4 – Čtenář

Pusť jednoho agenta typu `reader` se zadáním z [`briefs.md`](briefs.md) nad hotovým adresářem balíčku. Na výchozím modelu s `medium` – je to kontrola proti zadání, ne návrh.

**Každý nález ověř přečtením místa**, než ho opravíš; co se nepotvrdí, zahoď. Po opravách pusť znovu *Fázi 3*. Nález, který by změnil, co balíček obsahuje (přibalit další soubor, ponechat sporný úsek), předlož uživateli.

**Nemá-li instalace typ `reader`**, pusť `Explore` se stejným zadáním a do závěru zapiš, že čtenář měl shell.

## Fáze 5 – Výstup

- **Adresář:** nech, jak je.
- **Zip:** `python3 -m zipfile -c ~/Downloads/<jméno>.zip <adresář>` – modul je ve standardní knihovně, takže zip vznikne stejně na každé platformě. Ověř `python3 -m zipfile -l`, že v něm je `INSTALL.md` v kořeni a počet souborů sedí s adresářem; pak pracovní adresář smaž.

## Časté chyby

- **Přizpůsobení se nechá na Claudovi příjemce.** „To si adaptuje“ znamená, že příjemce dostane cizí cesty a odkazy na skilly, které nemá. Balíček se dodává hotový; Claude příjemce rozhoduje jen o umístění.
- **Do balíčku se napevno zapíše cesta cílové instalace.** Vypadá to jako hotová práce, ale rozhoduje to za příjemce a rozbije se to, jakmile zvolí jiné místo.
- **`INSTALL.md` popisuje, kde to leží u autora.** I jako „pro informaci“ je to autorova cesta.
- **Sdílený soubor se přibalí celý kvůli jedné větě.** Příjemce pak dostane autorova pravidla práce, která se skillem nesouvisí, a s nimi další odkazy ven.
- **Vlastní typy agentů se instalují zvlášť.** Balíček pak není jeden celek a instalace sahá mimo složku skillu.
- **Na platformu se zapomene.** Instalační příkaz jen pro `brew` na Windows nefunguje.
- **Přibalí se historie skillu.** `decisions.md` je za běhu k ničemu a je plný cest a jmen.
- **Grep s úzkým vzorem se vezme za kontrolu.** Odkaz zapsaný jinak, než čekal, projde. Kontrola je `refs.py check`, ne ruční hledání.

## Fáze 6 – Závěr

```
## Balíček hotový

- **Balíček:** <~/Downloads/jméno/ nebo .zip> – <N souborů>
- **Obsah:** <skilly a domény>

**Vepsáno místo přibalení**
- <soubor> → <kam a co>

**Odstraněno**
- <co a proč – osobní, mimo balíček, historie>

**Závislosti v INSTALL.md**
- <nástroj – pro které platformy, nebo „žádné“>

**Ověřeno**
- Kontrola skriptem: <příkaz a návratový kód>
- Čtenář: <počet nálezů, kolik opraveno, kolik zahozeno>

**Ponecháno vědomě**
- <nález kontroly, který je správně, nebo „nic“>
```

Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo – `~/.claude/standards/rules.md`, *Styl odpovědí*. Připomeň, že balíček nese kopii soukromé znalosti.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Balíček je hotový a ověřený, můžeš ho poslat.`
- `Balíček hotový není – brání tomu: <konkrétní seznam>.`
