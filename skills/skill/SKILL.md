---
name: skill
description: Skill se použije, když uživatel zadá "/skill" (volitelně s režimem create, extract, update nebo delete), nebo chce založit nový vlastní skill, vytěžit rozdělanou konverzaci do skillu, prohnat existující skilly revizí proti dnešní podobě normy, anebo skill zrušit i se všemi jeho stopami. Norma tvaru je v ~/.claude/skills/SKILLS.md; tenhle skill je proti ní instalátor a revizor, měření a vytěžení deleguje na skill-creator a superpowers:writing-skills.
argument-hint: [create|extract|update|delete] [jméno]
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion, Skill]
---

# Skill

## Co skill dělá

Spravuje vlastní skilly v `~/.claude/skills/` proti normě v `~/.claude/skills/SKILLS.md`. Čtyři režimy:

- **`/skill`** nebo **`/skill create`** – **založení**. Debrief, tabulka švů, baseline, sepsání, ověření, napojení na okolí.
- **`/skill extract`** – **vytěžení konverzace**. Vstupem není zadání, ale to, co se v session vyladilo. Od sepsání dál je dráha stejná jako u založení.
- **`/skill update [jméno]`** – **dorovnání na dnešní normu**. Jeden skill, nebo bez jména všechny. Hlavní důvod, proč je skill opakovatelný.
- **`/skill delete <jméno>`** – **odstranění i se stopami**.

Režim **`update` je to, co neumí nikdo jiný.** Norma se posouvá dál, patnáct souborů zůstává stát a samy o tom neřeknou – stejná vlastnost, kvůli které má `/project` svůj revizní krok.

## Co skill nedělá

- **Nedefinuje tvar skillu.** Ten je v `~/.claude/skills/SKILLS.md`. Tenhle skill ho čte, neopisuje a nerozšiřuje. Ukáže-li se, že norma je špatně, opraví se norma – ne že se udělá výjimka tady.
- **Neaudituje konfiguraci.** Rozpory mezi soubory, mrtvé zbytky a drift mezi vrstvami řeší `/consistency`; tenhle skill se dívá jen na skilly a jen proti normě.
- **Neprověřuje kvalitu práce skillu za běhu.** Že skill dělá dobrou práci, ukáže jeho použití a `/review`. Tady se měří, jestli se **vyvolá** a jestli se pod tlakem **dodrží**.
- **Nesahá na cizí skilly.** Pluginy a vestavěné skilly se používají, ne udržují.
- **Nemigruje patnáct skillů mimochodem.** Převod na novou normu je vědomý běh režimu `update`, ne vedlejší efekt jiné práce.

## Jak je to postavené uvnitř

Skill **skládá**, nepíše vše sám – je to první uplatnění pravidla *Skládej, nepiš znovu* z normy. Švy:

| Krok | Kdo | Proč zrovna on |
|---|---|---|
| Debrief zadání | **vlastní** | Ptá se na věci, které plynou z normy – kde to stojí v ose, proti kterému sousedovi se to vymezuje, má to režimy. Cizí nástroj se na to nezeptá. |
| Vytěžení z konverzace | `skill-creator` | Má na to hotový postup zachycení záměru. |
| Baseline – jak agent selže bez skillu | `superpowers:writing-skills` | Je to jádro jeho metody. |
| **Sepsání `SKILL.md`** | **vlastní** | Jádro normy. Jediné místo, kudy by prosákl cizí tvar. |
| Evaluace výstupu | `skill-creator` | Má na to skripty, ne prózu. |
| Tlakové scénáře | `superpowers:writing-skills` | Měří dodržení pravidla pod tlakem, ne kvalitu výstupu. |
| Ladění `description` | `skill-creator` | Umí spolehlivost vyvolání proměřit, ne odhadnout. |
| Okolí, revize, rušení | **vlastní** | Neumí to nikdo. |

**Volání cizích nástrojů je implementační detail, ne rozhraní.** Vyměnit se smí kdykoliv. Závazné je: tvar výstupu podle `SKILLS.md`, že se skill nezaloží bez odsouhlaseného zadání, že revize nic nepřepíše bez zeptání a že se po dokončení dorovná okolí.

**Zadávej vnitřku kontrakt výstupu, ne kroky.** „Potřebuju tři testovací prompty a vyhodnocení, jestli se skill vyvolal" přežije upgrade pluginu; „udělej svůj krok 3" ne.

**Cizí nástroj nesmí rozhodovat o tvaru.** Předej mu výslovně: sekce a jejich pořadí podle `SKILLS.md`, čeština, cíl `skills/<jméno>/SKILL.md` v tomhle repozitáři. Bez toho si prosadí vlastní výchozí volbu – `skill-creator` i `writing-skills` mají každý svou a obě se od téhle normy liší.

------

## Fáze 0 – Pre-flight

Společný začátek je v `~/.claude/skills/PREFLIGHT.md`. Kořenem projektu je tady vždycky `~/.claude`. Navíc:

1. **Přečti `~/.claude/skills/SKILLS.md` celou.** Neopírej se o paměť – tvoje představa o tvaru je zrovna to, co může být zastaralé.
2. **Udělej inventuru toho, co je k dispozici.** `ls ~/.claude/skills/`, seznam nainstalovaných pluginů a jejich skillů, vestavěné skilly. Je to vstup pro *Fázi 3* a zároveň se tím ověří, že cizí nástroje, na které skill deleguje, opravdu existují.
3. **Sonda na závislosti měřicí části.** Skripty `skill-creatoru` potřebují Python a svoje okolí. Ověř to dřív, než na ně pošleš práci. **Chybí-li, neselhávej** – řekni to, pokračuj bez měřicí části a zapiš do závěru, co se tím neověřilo.
4. **Zjisti, na kterém skillu se pracuje**, je-li v argumentu. Neexistuje-li a jde o jiný režim než `create`, nabídni nejbližší jména z inventury místo hlášky o chybě.

## Fáze 1 – Volba režimu

Je-li režim v argumentu, jeď podle něj a jen ho oznam. Není-li, zeptej se přes `AskUserQuestion`.

| Režim | Pokračuj |
|---|---|
| `create` | Fáze 2 |
| `extract` | Fáze 2, varianta pro session |
| `update` | *Režim `update`* níž |
| `delete` | *Režim `delete`* níž |

## Fáze 2 – Zadání

**Ptej se postupně, jednu otázku za druhou** (`~/.claude/RULES.md`, *Ptej se postupně, ne všechno najednou*).

Nejdřív otázka, která rozhoduje, jestli se vůbec pokračuje:

1. **Má to být skill?** Projdi zadání čtyřmi možnostmi z normy, *Kdy vzniká skill – a kdy ne*. Vyjde-li, že to patří do brány, do `RULES.md`, do domény nebo do projektového `CLAUDE.md`, **řekni to a skonči.** Skill, který měl být pravidlem, se pak nikdy nevyvolá ve chvíli, kdy je potřeba.

Pak zbytek:

2. **Co skill dělá a kdy se má vyvolat.** Doslovné spouštěče i situace.
3. **Stojí v ose *Životního cyklu práce*** (`~/.claude/RULES.md`)? Pokud ano, **proti kterým dvěma sousedům se vymezuje** – to je vstup pro *Co skill nedělá* a bez něj sekce vznikne jako prázdná negace.
4. **Má režimy?** Určuje `argument-hint`.
5. **Co je jeho výstup** a podle čeho se pozná, že je hotový. Vstup pro dvě koncové věty.
6. **Které doménové znalosti** z `~/Dev/context/` se na něj vztahují.

**V režimu `extract`** body 2 až 6 nevymýšlej – vytěž je z konverzace.

**Prošla-li session kompaktací, nestačí to, co máš v kontextu** – první polovina konverzace je pryč a bývá v ní zrovna to, co se vyladilo. Načti nejdřív transcript ze souboru; postup i pasti (zprávy poslané uprostřed tahu se ukládají jako `queue-operation`, ne jako `user`) má hotové `/cleanup`, *Fáze 1 – Rekonstrukce session*. Neopisuj ho sem, řiď se jím.

Pak **vyvolej `skill-creator`** a nech ho vytěžit záměr: použité nástroje, sled kroků, opravy, kterými uživatel průběžně měnil směr. Výsledek předlož k potvrzení a doplň jen to, co v konverzaci nezaznělo.

**Zadání nech odsouhlasit, než začneš psát.** Skill postavený na nedomluveném zadání se zahazuje celý.

## Fáze 3 – Tabulka švů

**Povinná inventura.** Ke každému kroku navrženého postupu odpověz: *umí to už něco?* Prohledej vlastní skilly, pluginy, vestavěné skilly, hooky a deterministické nástroje z inventury ve *Fázi 0*.

Výstupem je tabulka, která jde rovnou do sekce *Jak je to postavené uvnitř*:

```
Krok                        Kdo         Proč zrovna on
<krok>                      vlastní     <co je na tom naše>
<krok>                      <nástroj>   <co už umí>
```

**Zbylo-li po odečtení delegací jádro, pokračuj.** Nezbylo-li, řekni to: je to alias, ne skill, a má se napsat jako alias.

## Fáze 4 – Baseline

**Změř, jak agent selže bez skillu.** Bez toho se skill píše proti představě, ne proti skutečnosti – a naučí něco jiného, než je potřeba.

**Vyvolej `superpowers:writing-skills`** a předej mu úlohu: pustit agenta bez skillu na ukázkový úkol ze zadání a **zapsat konkrétní racionalizace**, kterými si zvolil jinou cestu. Ty jsou vstup pro *Časté chyby* a pro místa, kde má být pravidlo formulované tvrději.

**Tvar mu nezadávej** a jeho doporučení k tvaru ignoruj – ten je z normy.

Nejde-li baseline udělat (skill je čistě mechanický, nebo prostředí není k dispozici), **řekni to a pokračuj** – vědomá mezera se přiznává, ne obchází.

## Fáze 5 – Sepsání

**Nejsilnější model, `xhigh`** (`~/.claude/RULES.md`, *Model a effort podle úkolu*). Skill řídí veškerou práci, která pod ním poběží; vada v něm se násobí do každého běhu a projeví se až u posledního.

**Piš sám, proti normě.** Tenhle krok se nedeleguje – je to jediné místo, kudy by prosákl cizí tvar.

Projdi `SKILLS.md` sekci po sekci a splň každou. Zvlášť hlídej to, co se odbývá nejčastěji:

- **`Co skill nedělá` jmenuje souseda**, ne obecnou činnost.
- **`Fáze 0` odkazuje na `PREFLIGHT.md`** a obsahuje jen odchylky.
- **Dvě koncové věty** splňují vzorec z normy a jsou v těle uvedené doslovně.
- **Délka** pod měkkou mezí; co ji přetahuje, jde do vedlejšího souboru v adresáři skillu.
- **`description`** má spouštěč i popis situace a vejde se do 1024 znaků.
- **`argument-hint` sedí s režimy** popsanými v těle.

## Fáze 6 – Ověření

Tři vrstvy, každá měří něco jiného. Chybí-li nástroj pro některou, vynech ji a **zapiš to do závěru jako nezkontrolované**.

1. **Tvar** – pusť `python3 -m unittest discover -s tests` z `~/.claude`. Je to nejlevnější brána a stojí nula tokenů.
2. **Vyvolání** – `skill-creator`, ladění `description`. Měří, jestli se skill chytí na situace, pro které vznikl, a nechytá se na cizí. **U skillu, jehož jméno se překrývá s cizím skillem, je tenhle krok povinný.**
3. **Dodržení pod tlakem** – `superpowers:writing-skills`, tlakové scénáře. **Povinné u skillu, který něco zakazuje nebo vynucuje** (nesahat na testy, nepokračovat bez potvrzení, nespouštět proti produkci). U takového skillu je totiž funkce právě to omezení, a ta se tvarem ověřit nedá.

Nálezy oprav a **projeď znovu** – ne že je jen ohlásíš.

## Fáze 7 – Okolí

Skill nežije sám. Tohle je jediné místo, kde je to napsané, takže se to jinak neudělá:

| Kam | Co |
|---|---|
| `~/.claude/README.md` | vlastní sekce ve stylu ostatních – osobní, věcná, s konkrétním přínosem; do části *Skilly, jak jdou po sobě*, nebo *Skilly mimo osu* |
| `~/.claude/RULES.md` | zařazení do osy *Životního cyklu práce*, stojí-li v ní – a doplnění u sousedů, čí práci nepřebírá |
| `~/.claude/tests/test_skills.py` | nese-li skill něco, co má hlídat stroj, přidej test na **nosnou část**, ne na tvar hlavičky. U nového skillu ověř, že normu splňuje – do `MIGRACE` se **nedoplňuje**, ten seznam se jen zkracuje |
| `~/.claude/skills/<jméno>/` | vedlejší soubory, skripty, jejich sonda na závislosti |
| `/project` | nabízí-li se skill při zakládání projektu, doplň ho do jeho doménových voleb |
| `docs/decisions.md` | proč vznikl, jaké varianty byly zavrženy, co se vědomě nepokrylo |

**Commitni**, má-li repozitář zapnutý autocommit.

## Fáze 8 – Závěr

```
## Skill hotový

**Soubor:** skills/<jméno>/SKILL.md – <N> řádků
**Režim:** <create / extract>
**Delegace:** <na co, nebo „na nic">

**Ověřeno**
- Tvar: <výstup testů a návratový kód>
- Vyvolání: <výsledek, nebo „neměřeno – proč">
- Tlakové scénáře: <výsledek, nebo „nepoužito – proč">

**Okolí**
- README.md · RULES.md · tests/ · /project · decisions.md – co se dorovnalo

**Nezkontrolováno**
- [co a proč, nebo „nic"]
```

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Skill je hotový a ověřený, můžeš ho pustit.`
- `Skill hotový není – brání tomu: <konkrétní seznam>.`

------

## Režim `update`

Projde skilly proti **dnešní** podobě normy a dorovná, co se rozešlo. Bez jména v argumentu jede přes všechny.

**Normu si načti, neopisuj ji z hlavy.** Rozdíl mezi skillem a tvou pamětí není nález – tvoje paměť je zrovna to, co je zastaralé.

### Co se kontroluje

| Oblast | Co ověřit |
|---|---|
| Hlavička | `name` sedí s adresářem; `description` má spouštěč i situaci a vejde se do 1024 znaků; `argument-hint` sedí s režimy v těle; `allowed-tools` nemá nástroje, které skill nepoužívá |
| Povinné sekce | jsou tam všechny a v pořadí z normy; žádná zaniklá nepřebývá |
| *Co skill nedělá* | jmenuje souseda, ne obecnou činnost; u kroku osy jsou to sousedé z obou stran |
| Pre-flight | odkazuje na `PREFLIGHT.md` a neopisuje jeho obsah |
| Koncové věty | jsou tam obě a ve tvaru z normy |
| Délka | proti mezím z normy; nad měkkou mez navrhni, co vytáhnout |
| Odkazy | každá cesta a každý zmíněný skill existuje; **žádný odkaz nemíří dovnitř fáze jiného skillu** |
| Názvosloví | „Fáze" vs. „Krok"; jeden termín pro jednu věc |
| Delegace | volané nástroje existují; sekce *Jak je to postavené uvnitř* je tam, kde se deleguje, a označuje vnitřek za vyměnitelný |
| **Nové možnosti v okolí** | *nevzniklo mezitím něco, co tenhle skill dělá ručně?* Přibyl vestavěný skill, plugin, MCP server nebo vlastní skill, který by nahradil kus jeho postupu? |

Poslední řádek je druhý druh driftu vedle rozejití s normou a **neklade ho nikdo jiný**. Konfigurační vrstva roste pod nohama a starší skill o ní neví.

### Jak to proběhne

**Napřed vypiš nálezy, pak teprve jednej.** Uživatel musí vidět rozsah dřív, než se sáhne na soubory.

```
<skill>   <N> nálezů:  <závažnost> <jednou větou>   [opravím / potřebuju rozhodnout]
```

**Dvourychlostní režim.** Mechanické a jednoznačné oprav rovnou a jen vypiš – chybějící odkaz na `PREFLIGHT.md`, chybějící koncová věta, `argument-hint` bez opory. Co **přepisuje nebo maže existující obsah** – rozdělení dlouhého skillu, přeformulování sekce, nahrazení kroku delegací – předlož a nech potvrdit, přes `AskUserQuestion` a **po jednom**.

**Přes všechny skilly nepředkládej nález po nálezu.** Ukaž vzorec, počet a tři příklady, a proveď to hromadně. Padesát otázek se neodklikává, jen odsouhlasí naslepo.

**Nenajdeš-li nic, řekni to a skonči.** Běh bez zásahu je platný výsledek revize.

**Vyškrtni ze seznamu `MIGRACE`** skill, u kterého jsi vypořádal **všechny** jeho nálezy – ráčna je per skill, ne per nález, takže skill s jedním zbylým nálezem v seznamu zůstává v `~/.claude/tests/test_skills.py`. Ten seznam je **ráčna**: množina skillů mimo normu se musí *rovnat* jeho obsahu, takže opravený skill, který v něm zůstane, shodí testy stejně jako regrese. Je to schválně – bez toho by výjimka tiše přežila dokončenou migraci a přestala cokoliv měřit.

Pak pokračuj *Fází 7* – i `update` sahá na `README.md` a testy.

### Proč se nikam neukládá, proti čemu se revidovalo naposledy

Nabízí se zapsat datum poslední revize a příště projít jen to, co se od té doby v normě změnilo. **Vědomě se to nedělá.** Stav skillu je odvoditelný z toho, jak vypadá teď, kdežto zapsaný otisk je tvrzení, které nikdo neověřuje. Hlavně by ale zúžil revizi na diff normy, a tím minul přesně ten případ, kvůli kterému vznikla – drift, který se nikdy nepropsal, protože ho tehdy nikdo nezpropagoval.

------

## Režim `delete`

**Skill se buď používá, nebo neexistuje.** Vypnutý skill dál nabízí funkci, kterou nikdo nemá zapnout – proto se ruší celý, ne že se odstaví.

Nejdřív **vypiš, co všechno se najde**, a nech to potvrdit. Teprve pak maž.

| Kde hledat | Co |
|---|---|
| `~/.claude/skills/<jméno>/` | celý adresář včetně vedlejších souborů a skriptů |
| `~/.claude/README.md` | jeho sekce |
| `~/.claude/RULES.md` | osa *Životního cyklu práce* a zmínky u sousedů |
| `~/.claude/tests/` | testy, které se ho týkají – **a jeho jméno v seznamu `MIGRACE`**, je-li tam; jinak `test_migrace_jmenuje_jen_existujici_skilly` spadne na výjimku pro nikoho |
| ostatní skilly | odkazy a předávání práce – „další krok: `/<jméno>`" |
| `~/.claude/settings.json` | hooky a oprávnění, které existovaly kvůli němu |
| projektové `CLAUDE.md` v `~/Dev` | sekce, které skill zakládal |
| Memory | záznamy, které ho vyžadují |

Hledej **grepem přes všechny ty kořeny**, ne z paměti. Po smazání **projeď kontrolní průchod na jméno skillu** – musí vrátit nulu mimo místa vědomě ponechaná.

**Nech stopu.** Do `docs/decisions.md` zapiš, co bylo zrušeno a proč, i co se tím vědomě ztratilo. Bez toho se zrušený mechanismus vrátí za půl roku jako „to by šlo udělat".

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Skill je zrušený, jeho jméno se v konfiguraci nevyskytuje.`
- `Skill zrušený není – brání tomu: <konkrétní seznam>.`

------

## Časté chyby

- **Norma se opíše do skillu.** Pak se rozejde a nikdo neví, která verze platí. Norma se **čte**, ne cituje.
- **Cizímu nástroji se zapomene říct tvar.** Prosadí vlastní – `skill-creator` i `writing-skills` mají každý svou představu o sekcích. Vždycky mu ho předej výslovně.
- **Revize se pustí bez načtení normy.** Pak měří proti paměti, tedy proti stavu, který je zrovna zastaralý.
- **Přes patnáct skillů se nálezy předkládají po jednom.** Neodklikatelné; odsouhlasí se naslepo a revize ztratí smysl.
- **Skill vznikne na věc, kterou chytne test nebo hook.** Mechanické omezení v próze se dodržuje hůř a stojí tokeny při každém běhu.
