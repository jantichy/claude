---
name: review
description: Skill se použije, když uživatel zadá "/review" nebo "/review full", nebo chce prověřit hotovou práci před uzavřením – korektnost, bezpečnost, data a stavy, provoz, testy a soulad s doménovými standardy (coding, web, admin, analytics, text, design). Pouští deterministické nástroje, pak paralelní panel rolí, nálezy nechá ověřit a projde je s uživatelem. Výchozí rozsah jsou změny na větvi, "full" projede celý projekt.
allowed-tools: [Read, Grep, Glob, Bash, Edit, Write, Agent, AskUserQuestion, Skill]
---

# Review

## Co skill dělá

Prověří hotovou práci **z několika nezávislých úhlů naráz** a nálezy projde s uživatelem.

Stojí na třech vrstvách, které se liší cenou i spolehlivostí – a pouštějí se v tomhle pořadí, protože každá další je dražší a méně jistá než ta před ní:

| Vrstva | Čím se dělá | Cena | Spolehlivost |
|---|---|---|---|
| **1. Deterministická** | nástroje projektu (typecheck, lint, audit závislostí, scan tajemství, statická analýza, mutation testing) | nula tokenů | absolutní, výsledek se nedá rozporovat |
| **2. Panel rolí** | paralelní subagenti, každý s jedním úhlem pohledu | vysoká | dobrá, ale hlásí i to, co není |
| **3. Ověření nálezů** | nezávislý skeptik, který se nález snaží vyvrátit | střední | tohle je to, co dělá výstup použitelným |

**Bez třetí vrstvy je panel k ničemu** – zavalí tě pravděpodobně znějícími nálezy, po třetím falešném ho začneš ignorovat a čtvrtý, pravý, přehlédneš.

V ose *Životního cyklu práce* (`~/.claude/RULES.md`) je to první krok uzavírání: navazuje na `/implement` a předává na `/consistency`.

## Co skill nedělá

- **Nenahrazuje zelenou linku.** Ta běží průběžně u každého úkolu (viz `~/.claude/RULES.md`, *Ověřitelná brána místo dojmu*, a `~/Dev/context/coding/coding.md`, *Ověřování a brány kvality*). Sem se přichází se stavem, který už je zelený; není-li, skill se zastaví a pošle tě to dodělat.
- **Neaudituje vnitřní konzistenci projektu.** Ptá se „je to správně a drží to předpis?“, ne „sedí si projekt sám se sebou?“ – na to je `/consistency`, který běží až po tomhle.
- **Neposuzuje, jestli je záměr dobrý.** Na to je `/oponent`.
- **Nevytěžuje session ani nepíše dokumentaci projektu.** To je `/cleanup`.
- **Nenasazuje.** To je `/release`, a ten se pouští vědomě a zvlášť.

## Rozsah

- **`/review`** (výchozí) – jen změny na aktuální větvi, tedy diff proti hlavní větvi plus necommitnuté změny.
- **`/review full`** – celý projekt. Použij, když uživatel napíše `full`, jinak nikdy.

U `full` na starším projektu počítej s tím, že vyplave existující dluh. **Předem uživatele upozorni**, kolik souborů se bude procházet, a pokud jich je hodně (řádově stovky), zeptej se přes `AskUserQuestion`, jestli chce pokračovat, nebo omezit rozsah na konkrétní adresář.

------

## Fáze 0 – Pre-flight

Tam, kde jsou nezávislé čtecí operace, používej paralelní tool calls.

### 0.1 Urči rozsah souborů

```
git merge-base HEAD origin/HEAD 2>/dev/null || git merge-base HEAD main 2>/dev/null || git merge-base HEAD master
git diff --name-only <merge-base>...HEAD
git status --porcelain
```

Sjednoť commitnuté změny na větvi s necommitnutými. Vynech smazané soubory. Když jsi na hlavní větvi a diff je prázdný, vezmi necommitnuté změny; když nejsou ani ty, řekni to a nabídni `full`.

*Worktree layout* (`~/Dev/context/worktree/worktree.md`): pouštěj to ve **worktree větve**. V kořeni kontejneru `git diff` spadne a `git status` taky – kořen není pracovní strom. Stojíš-li tam, přesuň se nejdřív do adresáře té větve, kterou máš prověřit, a rozsah `full` počítej rovněž jen nad ním, ne nad celým kontejnerem.

**Režim `full`:** všechny zdrojové soubory projektu. Vynech `node_modules/`, `dist/`, `build/`, `vendor/`, `generated/`, `*.gen.*` a cokoliv v `.gitignore`.

### 0.2 Načti kontext projektu

- Projektový `CLAUDE.md` – zejména `## Příkazy` (*Kontrakt příkazů*), `### Autocommit`, `## Výjimky z obecných pravidel` a kapitolu `## Review`, pokud existuje.
- **Kapitola `## Review`** obsahuje dříve zamítnuté nálezy (won't fix). Ty se **vůbec neuvádějí** – ani v tomhle běhu, ani v žádném dalším. U staršího projektu může mít ještě starý název `## Standards`; přečti obojí a při prvním zápisu ji přejmenuj.
- **`## Výjimky z obecných pravidel`** – vědomé odchylky projektu. Co je tam popsané jako výjimka, není nález.
- **`docs/requirements.md` a `docs/architecture.md`**, existují-li. Role *Korektnost* a *Data a stavy* bez nich nemají proti čemu měřit.

### 0.3 Vyber role panelu

Role se vybírají **podle toho, čeho se soubory v rozsahu týkají**, ne podle typu projektu. Obsahový projekt tedy nedostane role pro kód, web dostane obojí. Neposílej agenta na roli, ke které v rozsahu není co prověřovat.

**Pracovní role** – ptají se, jestli je to správně:

| Role | Ptá se | Zapíná se, když v rozsahu je |
|---|---|---|
| **Korektnost** | dělá to, co má, scénář po scénáři? | jakýkoliv kód |
| **Bezpečnost** | dá se to zneužít? | kód, který zpracovává vstup, autorizuje, pracuje s daty uživatelů nebo sahá ven |
| **Data a stavy** | migrace, konzistence, souběh, idempotence | datový model, migrace, stavový automat, fronta, plánované úlohy |
| **Provoz a chyby** | co se stane, když to spadne? | volání cizích systémů, I/O, dlouhé operace, cokoliv s timeoutem |
| **Testy** | co není pokryté a které testy jsou falešně zelené? | jakýkoliv kód, u kterého projekt má `test` v kontraktu příkazů |

**Standardové role** – ptají se, jestli to drží předpis. Každá je jedna sada z `~/Dev/context/`:

| Sada | Kdy se aplikuje |
|---|---|
| `coding/coding.md` | jakýkoliv kód, datový model, migrace, konfigurace, CI |
| `web/web.md` | webové rozhraní – šablony, komponenty, styly, stránky |
| `web/admin.md` | administrace, backoffice, interní nástroj (**navíc** k `web/web.md`, ne místo něj) |
| `analytics/` | implementace měření – GTM kontejnery a jejich export, dataLayer pushe, měřicí kódy v šablonách, CMP a consent (**navíc** k `web/web.md`) |
| `text/text.md` | souvislé české texty – dokumentace, obsah stránek, články, newslettery (o textech v rozhraní rozhoduje `web/web.md`) |
| `design/design.md` | vizuální výstupy – grafika, barevné systémy, typografie, cokoliv, u čeho se rozhoduje o čitelnosti a kontrastu |
| `design/slides.md` | promítané prezentace (**navíc** k `design/design.md`) |
| `training/training.md` | obsah školení a kurzů – osnovy, lekce, cvičení, materiály (**navíc** k `text/text.md`: text řeší, jak je to napsané, training to, jak je to postavené) |

`worktree/worktree.md` mezi sadami schválně není – popisuje layout repozitáře, ne pravidla pro zdrojové soubory. Ze stejného důvodu tu není `organizations/`: **je to korpus, ne standard.**

Vypiš uživateli, které role a sady jsi vybral a proč. Když si u některé nejsi jistý, radši ji zahrň.

Nesedí-li **žádná** role, řekni to explicitně a skonči – nevymýšlej si vlastní kritéria. Pozor, čistě dokumentační projekt bez pokrytí není: na české texty sedí `text/text.md`.

------

## Fáze 1 – Deterministická vrstva

**Běží první a stojí nula tokenů.** Každý nález odsud je jistý a ušetří práci panelu.

Spouštěj **jen příkazy z `## Příkazy` v projektovém `CLAUDE.md`** (*Kontrakt příkazů*). Chybí-li řádek, krok se přeskočí a **do výstupu se napíše, co se tím nezkontrolovalo**. Nevymýšlej příkazy, které jsi neověřil.

1. **Zelená linka** – `typecheck`, `lint`, `test`. Není-li zelená, **zastav se**: review nad rozbitým stavem nemá smysl. Vypiš, co padá, a pošli to dodělat.
2. **Build** – `build`. Do zelené linky nepatří, protože je na běh po každém tahu moc pomalý – ale před uzavřením feature se ověřit musí.
3. **Audit závislostí** – `audit`. Nálezy `HIGH` a `CRITICAL` jsou automaticky kritické nálezy, nejdou přes panel.
4. **Tajemství v repu** – `gitleaks detect --no-banner` nebo `git log -p | grep`-heuristika, není-li nástroj po ruce. Nález je vždy kritický a **nikdy se neopravuje jen smazáním**: co bylo commitnuté, je v historii a patří rotovat.
5. **Statická analýza nad rámec lintu** – `semgrep --config p/owasp-top-ten`, je-li k dispozici.
6. **Mutation testing** – `mutation`, jen v rozsahu změn a jen když projekt příkaz má. Odpovídá na otázku, kterou pokrytí nezodpoví: *tvrdí ty testy vůbec něco?* Je pomalé; u `full` se ptej, jestli ho pouštět.

Výsledky si odlož – ve Fázi 4 se slijí s nálezy panelu, ale **neprocházejí ověřením ve Fázi 3**. Nástroj nehalucinuje.

------

## Fáze 2 – Panel rolí

Na **každou** vybranou roli pošli **samostatného subagenta** – všechny paralelně, jedním blokem tool callů. Každý si svůj podklad načte sám, ať ti jeho obsah nesní kontext.

**Dvě role nepiš sám – vyvolej vestavěné skilly Claude Code:**

- **Korektnost** → `/code-review`. Je na to postavený, běží v čerstvém kontextu a hledá přesně chyby v diffu.
- **Bezpečnost** → `/security-review`.

Vlastní zadání piš jen pro role, které vestavěný protějšek nemají.

**Model a effort podle role.** Levné a mechanické role (standardové sady, testy) nech na výchozím modelu. **Bezpečnost a Data a stavy pouštěj na nejsilnějším dostupném modelu s vysokým effortem** – tam přehlédnutí stojí nejvíc a levný model tam mlčí, místo aby hlásil.

### Zadání pro pracovní roli

```
Prověř zadané soubory z jediného úhlu: <ROLE – např. „co se stane, když volání
cizího systému selže nebo se zasekne">.

Nic jiného nehlas. Jiné úhly pokrývají jiní agenti; když nahlásíš nález mimo
svou roli, jen zdvojíš práci a zašumíš výstup.

PODKLAD:
- docs/requirements.md – scénáře a varianty, proti kterým se měří
- docs/architecture.md – jak to má být postavené
<u role Bezpečnost navíc: checklist OWASP ASVS / Top 10, ne vlastní úvaha o tom,
co by se mohlo pokazit>

SOUBORY K PROVĚŘENÍ:
<seznam absolutních cest>

VĚDOMÉ VÝJIMKY (nehlásit):
<obsah ## Výjimky z obecných pravidel a ## Review z projektového CLAUDE.md>

PRAVIDLA HLÁŠENÍ:
- Hlas jen to, co porušuje korektnost nebo zadání. Stylové preference a „šlo by to
  hezčí" nehlas vůbec – z toho vzniká over-engineering, ne lepší kód.
- Každý nález musí mít konkrétní selhání: vstupy nebo stav → co se stane špatně.
  „Mohla by tu být race condition" není nález. „Když dva požadavky dorazí mezi
  read a write v foo.ts:42, druhý přepíše první" nález je.
- Nehlas soubory v cestách legacy/vendored/generated.
- Když je totéž porušené na mnoha místech (>10 výskytů), neuváděj jednotlivé řádky –
  uveď pattern, počet, tři příklady a navrhni hromadnou opravu. Označ tagem `batch`.
- Když má víc nálezů společnou příčinu, seskup je: root nález + u následků vyplň
  `related_root` s titulkem rootu.

ZÁVAŽNOST:
- KRITICKÉ – bezpečnost, ztráta dat, nepřístupnost pro část uživatelů, nevratná akce bez pojistky
- STŘEDNÍ – reálný dopad na správnost, použitelnost nebo udržovatelnost
- KOSMETICKÉ – bez praktického dopadu

VÝSTUP: JSON pole, nic jiného. Prázdné pole, když je vše v pořádku.
[
  {
    "severity": "KRITICKÉ" | "STŘEDNÍ" | "KOSMETICKÉ",
    "role": "<název role>",
    "basis": "o co se nález opírá – scénář z requirements, bod ASVS, pravidlo standardu",
    "title": "krátký název nálezu",
    "description": "v čem konkrétně je problém",
    "failure": "konkrétní vstupy nebo stav → co se stane špatně",
    "locations": ["soubor:řádek", ...],
    "suggested_fix": "konkrétní akce, ne vágní doporučení",
    "tags": ["batch"?],
    "related_root": "title jiného nálezu, jehož je tento následkem (volitelné)"
  }
]

Nezapisuj do žádného souboru.
```

### Zadání pro standardovou roli

Stejné, s jediným rozdílem – měřítkem není úsudek, ale text:

```
Prověř soulad zadaných souborů se standardem v souboru <absolutní cesta k sadě>.

POSTUP:
1. Přečti celý soubor standardů. Sestav si z něj seznam konkrétních prověřitelných
   pravidel – včetně sekcí „Antipatterns", pokud existují.
2. Přečti zadané soubory.
3. Pro každé pravidlo ověř, jestli ho zadané soubory porušují.

Každý nález **musí být opřený o konkrétní bod standardu** – do pole `basis` uveď
název sekce a citaci nebo parafrázi pravidla. Nález, který takhle podložit neumíš,
nehlas: na obecné posouzení jsou pracovní role.

Nehlas chyby v logice ani bugy, pokud neporušují konkrétní pravidlo.

<zbytek – soubory, výjimky, pravidla hlášení, závažnost, formát – shodný s pracovní rolí>
```

------

## Fáze 3 – Ověření nálezů

**Tohle je krok, na kterém stojí použitelnost celého skillu.** Panel hlásí i to, co není – reviewer požádaný o hledání mezer nějaké najde vždycky, protože o to byl požádán.

Na každý nález ze závažností **KRITICKÉ a STŘEDNÍ** pošli **samostatného ověřovatele** – paralelně, v čerstvém kontextu, který nevidí ani panel, ani tvou konverzaci:

```
Tenhle nález se snaž VYVRÁTIT. Tvým úkolem není ho potvrdit.

NÁLEZ: <title>
TVRZENÍ: <description>
SELHÁNÍ, KTERÉ TVRDÍ: <failure>
KDE: <locations>

Přečti si dotčený kód i jeho okolí a odpověz na jedinou otázku: **nastane to
popsané selhání doopravdy?** Ověř zejména, jestli problém neošetřuje něco jinde –
guard o vrstvu výš, validace na vstupu, typový systém, omezení v databázi,
konfigurace.

Při pochybnosti odpovídej `refuted: true`. Nález, který neumíš doložit, škodí víc,
než užije.

VÝSTUP: JSON, nic jiného.
{"refuted": true|false, "reason": "čím konkrétně je vyvrácený nebo potvrzený"}
```

**Nález doložený reprodukovatelným experimentem ověřovatele nepotřebuje** – přehraj si ten experiment sám. Ověřuje se tvrzení, ne pozorování; skeptik nad doloženým pozorováním jen stojí čas.

**Deduplikuj ještě před ověřením**, ne až po něm. Role se překrývají schválně, takže tentýž problém přijde třikrát jinými slovy – posílat na něj tři ověřovatele je trojnásobná cena za tutéž odpověď.

**Vyvrácené nálezy zahoď** a jen je spočítej do souhrnu. KOSMETICKÉ nálezy se neověřují – ověření by stálo víc než jejich oprava.

U nálezů z deterministické vrstvy (Fáze 1) se ověření **nedělá**.

------

## Fáze 4 – Zpracování výsledků

Slož nálezy z deterministické vrstvy a z panelu (ty, které přežily ověření) do jednoho seznamu. Seřaď: KRITICKÉ, STŘEDNÍ, KOSMETICKÉ; v rámci kategorie root položky před jejich následky.

**Deduplikuj napříč rolemi.** Role se překrývají schválně – bezpečnost a `coding.md` najdou tutéž díru, `web/web.md` a `web/admin.md` totéž tlačítko, `web/web.md` a `text/text.md` tutéž typografii. Když dva agenti hlásí totéž na stejném místě, nech jeden nález a u něj uveď oba podklady.

Pak rozděl na dvě skupiny:

**Mechanické** – oprava je jednoznačná, bezriziková a nemění chování ani strukturu:
- chybějící `alt`, `aria-label`, `lang`, `type` u tlačítka, popisek k poli formuláře
- chybějící `rel="noopener"`, `autocomplete`, `inputmode`
- porušení naming konvence u nové, nikde jinde nereferencované věci
- chybějící metadata stránky, kde je jasné, co tam patří
- formulační a formátovací drobnosti podle standardu

**Sporné** – všechno ostatní, tedy vždy když existuje víc rozumných řešení nebo oprava zasahuje dál než na jedno místo:
- **cokoliv z pracovních rolí** – korektnost, bezpečnost, data, provoz a testy jsou vždy sporné, i když se oprava zdá triviální
- změny struktury, layoutu, informační architektury
- změny datového modelu, typů, API kontraktů, autorizace
- přejmenování čehokoliv, na co se odkazuje odjinud
- doplnění chybějícího stavu, guardu, potvrzovacího kroku nebo auditní stopy
- `batch` nálezy – vždy sporné
- cokoliv, co mění chování

Při pochybnosti patří nález mezi sporné.

------

## Fáze 5 – Přehled

```
## Výsledky review

Rozsah: [změny na větvi – N souborů / celý projekt – N souborů]
Role: [korektnost, bezpečnost, testy, coding, web – které běžely]

Deterministická vrstva:
- zelená linka: ✅ / ❌ [co padá]
- audit závislostí: N nálezů HIGH/CRITICAL
- tajemství v repu: N
- statická analýza: N
- mutation score: X %   [nebo „nespuštěno – projekt nemá příkaz"]
- nezkontrolováno: [co chybělo v kontraktu příkazů]

Panel: X nálezů, Y vyvráceno při ověření, zbývá Z:
- 🔴 Kritické: N
- 🟡 Střední: N
- 🔵 Kosmetické: N

Z toho [batch] hromadných (>10 výskytů): N

Mechanických (jednoznačná bezriziková oprava): N – ty opravím rovnou a jen je vypíšu.
Sporných: M – ty projdeme spolu od nejzávažnějších.
```

Když nálezy nejsou, řekni to a skonči.

------

## Fáze 6 – Mechanické opravy

Mechanické nálezy oprav **rovnou, bez ptaní**. Pak:

1. **Ověř** – spusť zelenou linku podle kontraktu příkazů. Když selže, zastav se, ukaž chybu a diff a zeptej se, jak pokračovat.
2. Vypiš, co jsi opravil – jeden řádek na nález:
   ```
   ## Opraveno rovnou (N mechanických)
   - 🔵 [název] – soubor:řádek – [co konkrétně změněno] (podklad: [basis])
   ```
3. Commit dle autocommit nastavení projektu – mechanické opravy **jedním commitem** dohromady.

Když uživatel na některou opravu zareaguje nesouhlasem, vrať ji a zařaď mezi sporné.

Nejsou-li žádné sporné nálezy, přeskoč Fázi 7 rovnou na shrnutí.

------

## Fáze 7 – Interaktivní průchod

Pro KAŽDÝ **sporný** nález, jeden po druhém, nikdy víc najednou:

1. Zobraz ho:

```
---
[N/celkem] 🔴/🟡/🔵 [role] [tagy] NÁZEV NÁLEZU

Podklad: [scénář z requirements / bod ASVS / sekce standardu]
Problém: [v čem konkrétně]
Selže takhle: [vstupy nebo stav → co se stane špatně]
Kde: [soubory:řádky, nebo "X výskytů, např. ..." u batch]

Navrhované řešení:
[konkrétně co změnit]
```

2. Zeptej se **vždy přes tool `AskUserQuestion`** – nikdy ne vypsáním voleb jako text. Jedno volání = jeden nález = jedna otázka (`multiSelect: false`):
   - `header`: `Nález N/celkem`, případně zkrácené na `N/celkem`
   - `question`: název nálezu a v čem je, jednou větou
   - `options` (v tomto pořadí, `description` u každé konkrétně popíše, co se stane):
     - **Opravit** – provedu navrhovanou změnu
     - **Odložit** – zapíšu do `docs/todo.md` i s úvahou, vrátíme se k tomu později
     - **Přeskočit** – neopravovat, zapíšu do `CLAUDE.md` jako „won't fix“
     - **Rozbalit** – *jen u `batch` nálezů*: vypíšu všechny lokace a projdeme je jednotlivě

   Tool má strop **4 volby** na otázku – tenhle výčet ho vyčerpává. Pátou volbu sem nepřidávej.

   Chování volby **Other** viz `~/.claude/RULES.md`, *Ptej se postupně, ne všechno najednou*.

3. Při volbě **Opravit**:
   a. Proveď změnu. U `batch` nálezu hromadně – find-replace, codemod, scripted edit přes Bash; **ne** desítky Edit volání po jednom.
   b. **Ověř – vždy, ne občas.** Zelená linka podle kontraktu příkazů. U opravy, kterou hlásila pracovní role, **doplň test, který ten případ pokrývá** – jinak se chyba vrátí a nikdo se to nedozví.
   c. Když kontrola selže: **zastav se**, ukaž chybu a diff a zeptej se, jak pokračovat. Nepokračuj automaticky na další nález.
   d. Po opravě rootu projdi položky s `related_root === <title opraveného>` a ověř (Read/Grep), jestli už nejsou neaktuální. Vyřešené vyhoď z fronty a započítej do „vyřešeno automaticky“.
   e. Commit dle autocommit nastavení projektu.

4. Zápis do `## Review` v projektovém `CLAUDE.md` (volba Přeskočit):
   - Když `CLAUDE.md` neexistuje, vytvoř ho s hlavičkou a kapitolou `## Review`.
   - Když kapitola neexistuje, doplň ji na konec souboru.
   - Formát (přidávat na konec kapitoly):
   ```
   ## Review

   Nálezy vyhodnocené při /review jako „neopravovat". Při dalším review se neuvádějí.

   - **YYYY-MM-DD** – *<title>* (role: <role>, podklad: <basis>): <důvod>
     - Lokace: <soubor:řádek, ...>
   ```
   - Datum vezmi z `Today's date is ...` v system-reminderu.
   - **Bezpečnostní nález sem nezapisuj bez výslovného potvrzení** a bez důvodu, který obstojí i za rok. „Zatím to nikdo nezneužil“ důvod není.

------

## Fáze 8 – Shrnutí

```
## Hotovo

Rozsah: [změny na větvi / celý projekt] · Role: [které]

- ⚡ Opraveno rovnou (mechanické): N
- ✅ Opraveno po odsouhlasení: N
- 🪄 Vyřešeno automaticky (následek root opravy): N
- 📌 Odloženo: N
- ⏭️ Přeskočeno (zapsáno do CLAUDE.md → Review): N
- 🚫 Vyvráceno při ověření (nezobrazeno): N

[Pokud jsou odložené: seznam s popisy]

**Nezkontrolováno:** [kroky přeskočené kvůli chybějícímu příkazu v kontraktu, nebo „nic"]

**Další krok:** /consistency
```

Když běžel jen výchozí rozsah a projekt je starší, připomeň, že `/review full` projede i to, čeho se tahle větev nedotkla.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `V prověřeném rozsahu je práce v pořádku.`
- `V pořádku není – zbývá: <konkrétní seznam>.`
