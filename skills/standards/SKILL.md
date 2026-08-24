---
name: standards
description: Skill se použije, když uživatel zadá "/standards" nebo "/standards full", nebo chce prověřit kód, rozhraní a texty proti doménovým standardům (coding.md, web.md, admin.md, analytics.md, text.md). Výchozí rozsah jsou změny na větvi, "full" projede celý projekt. Mechanické opravy provede rovnou, sporné řeší interaktivně jeden po druhém.
allowed-tools: [Read, Grep, Glob, Bash, Edit, Write, Agent, AskUserQuestion]
---

# Standards

## Úvodní hláška (vždy jako první)

Než začneš cokoliv dělat, vypiš uživateli přesně tento jeden řádek:

Autor skillu: **Jan Tichý** · jantichy@jantichy.cz · Celá konfigurace Claude vč. všech skillů: https://github.com/jantichy/claude

Teprve pak pokračuj plněním skillu.

## Co skill dělá

Prověří kód, rozhraní a texty proti **doménovým standardům** v `~/Dev/context/` a nálezy opraví spolu s uživatelem.

Kontroluje soulad s **explicitně sepsanými pravidly** – jedno pravidlo, jeden nález. Tím se liší od sousedních skillů:

- `/code-review` hledá **chyby** v provedených změnách (korektnost, bugy).
- `/consistency` hledá **vnitřní rozpory** projektu se sebou samým.
- `/standards` hledá **odchylky od vnějšího předpisu**, i když je projekt dodržuje konzistentně špatně všude.

Když nález sedí do víc kategorií, patří sem jen tehdy, když ho lze opřít o konkrétní bod ze standardů. Jinak ho nehlas.

## Rozsah

- **`/standards`** (výchozí) – jen změny na aktuální větvi, tedy diff proti hlavní větvi plus necommitnuté změny. Rychlé, sedí do postupu uzavírání feature.
- **`/standards full`** – celý projekt. Použij, když uživatel napíše `full`, jinak nikdy.

U `full` na starším projektu počítej s tím, že vyplave existující dluh. **Předem uživatele upozorni**, kolik souborů se bude procházet, a pokud jich je hodně (řádově stovky), zeptej se přes `AskUserQuestion`, jestli chce pokračovat, nebo omezit rozsah na konkrétní adresář.

------

## Fáze 1 – Pre-flight

Tam, kde jsou nezávislé čtecí operace, používej paralelní tool calls.

### 1.1 Urči rozsah souborů

**Výchozí režim (změny):**

```
git merge-base HEAD origin/HEAD 2>/dev/null || git merge-base HEAD main 2>/dev/null || git merge-base HEAD master
git diff --name-only <merge-base>...HEAD
git status --porcelain
```

Sjednoť commitnuté změny na větvi s necommitnutými. Vynech smazané soubory. Když jsi na hlavní větvi a diff je prázdný, vezmi necommitnuté změny; když nejsou ani ty, řekni to a nabídni `full`.

**Režim `full`:** všechny zdrojové soubory projektu. Vynech `node_modules/`, `dist/`, `build/`, `vendor/`, `generated/`, `*.gen.*` a cokoliv v `.gitignore`.

### 1.2 Vyber sady standardů

Podle toho, čeho se soubory v rozsahu týkají. Aplikuj jen ty relevantní – neposílej agenta na sadu, ke které v rozsahu není co kontrolovat.

| Sada | Kdy se aplikuje |
|---|---|
| `~/Dev/context/coding.md` | jakýkoliv kód, datový model, migrace, konfigurace, CI |
| `~/Dev/context/web.md` | webové rozhraní – šablony, komponenty, styly, stránky |
| `~/Dev/context/admin.md` | administrace, backoffice, interní nástroj (**navíc** k `web.md`, ne místo něj) |
| `~/Dev/context/analytics.md` | implementace měření – GTM kontejnery a jejich export, dataLayer pushe, měřicí kódy v šablonách, CMP a consent (**navíc** k `web.md`, ne místo něj) |
| `~/Dev/context/text.md` | souvislé české texty – dokumentace, obsah stránek, články, newslettery (o textech v rozhraní rozhoduje `web.md`) |

`~/Dev/context/worktrees.md` mezi sadami schválně není. Popisuje layout repozitáře, ne pravidla pro zdrojové soubory, takže proti diffu se nedá auditovat.

Vypiš uživateli, které sady jsi vybral a proč. Když si u některé nejsi jistý, radši ji zahrň.

Pokud žádná sada nesedí, řekni to explicitně a skonči – nevymýšlej si vlastní standardy. Pozor, čistě dokumentační projekt sadou bez pokrytí není: na české texty sedí `text.md`.

### 1.3 Načti kontext projektu

- Projektový `CLAUDE.md` – zejména `### Autocommit`, `## Výjimky z obecných pravidel` a kapitolu `## Standards`, pokud existuje.
- **Kapitola `## Standards`** obsahuje dříve zamítnuté nálezy (won't fix). Ty se **vůbec neuvádějí** – ani v tomhle běhu, ani v žádném dalším.
- **`## Výjimky z obecných pravidel`** – vědomé odchylky projektu. Co je tam popsané jako výjimka, není nález.

------

## Fáze 2 – Audit

Na **každou** vybranou sadu pošli **samostatného subagenta** – všechny paralelně, jedním blokem tool callů. Každý agent si svou sadu načte sám, ať ti její obsah nesní kontext.

Zadání pro agenta (doplň sadu, seznam souborů, výjimky a won't-fix položky):

```
Prověř soulad zadaných souborů se standardem v souboru <absolutní cesta k sadě>.

POSTUP:
1. Přečti celý soubor standardů. Sestav si z něj seznam konkrétních prověřitelných pravidel – včetně sekcí "Antipatterns", pokud existují.
2. Přečti zadané soubory.
3. Pro každé pravidlo ověř, jestli ho zadané soubory porušují.

SOUBORY K PROVĚŘENÍ:
<seznam absolutních cest>

VĚDOMÉ VÝJIMKY (nehlásit):
<obsah ## Výjimky z obecných pravidel a ## Standards z projektového CLAUDE.md, nebo "žádné">

PRAVIDLA HLÁŠENÍ:
- Každý nález **musí být opřený o konkrétní bod standardu**. Uveď, o který jde (název sekce a citace nebo parafráze pravidla). Nález, který neumíš takhle podložit, nehlas – tenhle skill není obecný code review.
- Nehlas chyby v logice, bugy ani obecné návrhy na vylepšení, pokud neporušují konkrétní pravidlo.
- Nehlas věci, které jsou v seznamu vědomých výjimek.
- Nehlas soubory v cestách legacy/vendored/generated.
- Když je pravidlo porušené na mnoha místech stejným způsobem (>10 výskytů), neuváděj jednotlivé řádky – uveď pattern, počet, tři příklady a navrhni hromadnou opravu. Označ tagem `batch`.
- Když má víc nálezů společnou příčinu, seskup je: root nález + u následků vyplň `related_root` s titulkem rootu.

ZÁVAŽNOST:
- KRITICKÉ – bezpečnost, ztráta dat, nepřístupnost pro část uživatelů, nevratná akce bez pojistky
- STŘEDNÍ – porušení pravidla s reálným dopadem na použitelnost, udržovatelnost nebo správnost
- KOSMETICKÉ – porušení bez praktického dopadu

VÝSTUP: JSON pole, nic jiného. Prázdné pole, když je vše v pořádku.
[
  {
    "severity": "KRITICKÉ" | "STŘEDNÍ" | "KOSMETICKÉ",
    "rule": "sekce standardu + pravidlo, o které se nález opírá",
    "title": "krátký název nálezu",
    "description": "v čem konkrétně je porušení",
    "locations": ["soubor:řádek", ...],
    "suggested_fix": "konkrétní akce – ne vágní 'zlepši přístupnost', ale 'doplň aria-label=\"Zavřít\" na tlačítko v Modal.tsx:42'",
    "tags": ["batch"?],
    "related_root": "title jiného nálezu, jehož je tento následkem (volitelné)"
  }
]

Nezapisuj do žádného souboru.
```

------

## Fáze 3 – Zpracování výsledků

Slož nálezy ze všech agentů do jednoho seznamu. Seřaď: KRITICKÉ, STŘEDNÍ, KOSMETICKÉ; v rámci kategorie root položky před jejich následky.

**Deduplikuj napříč sadami.** `web.md` a `admin.md` se překrývají, stejně tak `web.md` a `text.md` v typografii a `web.md` a `analytics.md` v consentu a GDPR – když dva agenti hlásí totéž na stejném místě, nech jeden nález a u něj uveď oba dotčené body standardů.

Pak rozděl na dvě skupiny:

**Mechanické** – oprava je jednoznačná, bezriziková a nemění chování ani strukturu. Typicky:
- chybějící `alt`, `aria-label`, `lang`, `type` u tlačítka, popisek k poli formuláře
- chybějící `rel="noopener"`, `autocomplete`, `inputmode`
- porušení naming konvence u nové, nikde jinde nereferencované věci
- chybějící metadata stránky, kde je jasné, co tam patří
- formulační a formátovací drobnosti podle standardu

**Sporné** – všechno ostatní, tedy vždy když existuje víc rozumných řešení nebo oprava zasahuje dál než na jedno místo:
- změny struktury, layoutu, informační architektury
- změny datového modelu, typů, API kontraktů, autorizace
- přejmenování čehokoliv, na co se odkazuje odjinud
- doplnění chybějícího stavu, guardu, potvrzovacího kroku nebo auditní stopy
- `batch` nálezy – vždy sporné, i když je jednotlivá oprava triviální
- cokoliv, co mění chování

Při pochybnosti patří nález mezi sporné.

------

## Fáze 4 – Přehled

```
## Výsledky kontroly standardů

Rozsah: [změny na větvi – N souborů / celý projekt – N souborů]
Sady: [coding.md, web.md, admin.md, analytics.md, text.md – které se použily]

Nalezeno X nálezů celkem:
- 🔴 Kritické: N
- 🟡 Střední: N
- 🔵 Kosmetické: N

Z toho [batch] hromadných (>10 výskytů): N

Mechanických (jednoznačná bezriziková oprava): N – ty opravím rovnou a jen je vypíšu.
Sporných: M – ty projdeme spolu od nejzávažnějších.
```

Když nálezy nejsou, řekni to a skonči.

------

## Fáze 5 – Mechanické opravy

Mechanické nálezy oprav **rovnou, bez ptaní**. Pak:

1. **Ověř** – u TS projektu `tsc --noEmit`, jinak co je rychle po ruce (lint, build). Když selže, zastav se, ukaž chybu a diff a zeptej se, jak pokračovat.
2. Vypiš, co jsi opravil – jeden řádek na nález:
   ```
   ## Opraveno rovnou (N mechanických)
   - 🔵 [název] – soubor:řádek – [co konkrétně změněno] (pravidlo: [sekce standardu])
   ```
3. Commit dle autocommit nastavení projektu – mechanické opravy **jedním commitem** dohromady.

Když uživatel na některou opravu zareaguje nesouhlasem, vrať ji a zařaď mezi sporné.

Pokud nejsou žádné sporné nálezy, přeskoč Fázi 6 rovnou na shrnutí.

------

## Fáze 6 – Interaktivní průchod

Pro KAŽDÝ **sporný** nález, jeden po druhém, nikdy víc najednou:

1. Zobraz ho:

```
---
[N/celkem] 🔴/🟡/🔵 [tagy] NÁZEV NÁLEZU

Pravidlo: [sekce standardu] – [citace nebo parafráze]
Porušení: [v čem konkrétně]
Kde: [soubory:řádky, nebo "X výskytů, např. ..." u batch]

Navrhované řešení:
[konkrétně co změnit]
```

2. Zeptej se **vždy přes tool `AskUserQuestion`** – nikdy ne vypsáním voleb jako text v odpovědi. Uživatel si tak vybírá šipkami a Enterem, místo aby psal písmena.

   Jedno volání = jeden nález = jedna otázka (`multiSelect: false`):
   - `header`: `Nález N/celkem` (max 12 znaků, klidně zkrať na `N/celkem`)
   - `question`: název nálezu a v čem je, jednou větou
   - `options` (v tomto pořadí, `description` u každé konkrétně popíše, co se stane):
     - **Opravit** – provedu navrhovanou změnu
     - **Odložit** – nechám být, vrátíme se k tomu později
     - **Přeskočit** – neopravovat, zapíšu do `CLAUDE.md` jako „won't fix"
     - **Rozbalit** – *jen u `batch` nálezů*: vypíšu všechny lokace a projdeme je jednotlivě

   Tool má strop **4 volby** na otázku – tenhle výčet ho vyčerpává. Pátou volbu sem nepřidávej.

   Volbu **Other** doplňuje tool sám – uživatel přes ni napíše vlastní instrukci nebo se doptá. Ber to jako doplňující instrukci k aktuálnímu nálezu (uprav návrh nebo odpověz na dotaz) a pak se zeptej znovu. Nikdy to neber jako „přeskočeno".

   Zpracování odpovědí:
   - **Opravit** – proveď změnu hned (krok 3)
   - **Odložit** – zapiš do interního seznamu odložených
   - **Přeskočit** – zeptej se na krátký důvod a zapiš do `## Standards` v projektovém `CLAUDE.md` (krok 4)
   - **Rozbalit** – vypiš všechny lokace a řeš je jednotlivě jako samostatné podnálezy

3. Při volbě **Opravit**:
   a. Proveď změnu. U `batch` nálezu hromadně – find-replace, codemod, scripted edit přes Bash; **ne** desítky Edit volání po jednom.
   b. **Ověř – vždy, ne občas.** `tsc --noEmit` u TS projektu; build, pokud je rychlý a týká se ho to; relevantní testy, jdou-li rychle pustit.
   c. Když kontrola selže: **zastav se**, ukaž chybu a diff a zeptej se, jak pokračovat. Nepokračuj automaticky na další nález.
   d. Po opravě rootu projdi položky s `related_root === <title opraveného>` a ověř (Read/Grep), jestli už nejsou neaktuální. Ty vyřešené vyhoď z fronty a započítej do „vyřešeno automaticky".
   e. Commit dle autocommit nastavení projektu.

4. Zápis do `## Standards` v projektovém `CLAUDE.md` (volba Přeskočit):
   - Když `CLAUDE.md` neexistuje, vytvoř ho s hlavičkou a kapitolou `## Standards`.
   - Když kapitola neexistuje, doplň ji na konec souboru.
   - Formát (přidávat na konec kapitoly):
   ```
   ## Standards

   Nálezy vyhodnocené při /standards kontrole jako "neopravovat". Při další kontrole se neuvádějí.

   - **YYYY-MM-DD** – *<title>* (pravidlo: <sekce standardu>): <důvod>
     - Lokace: <soubor:řádek, ...>
   ```
   - Datum vezmi z `Today's date is ...` v system-reminderu.

------

## Fáze 7 – Shrnutí

```
## Hotovo

Rozsah: [změny na větvi / celý projekt] · Sady: [které]

- ⚡ Opraveno rovnou (mechanické): N
- ✅ Opraveno po odsouhlasení: N
- 🪄 Vyřešeno automaticky (následek root opravy): N
- 📌 Odloženo: N
- ⏭️ Přeskočeno (zapsáno do CLAUDE.md → Standards): N

[Pokud jsou odložené: seznam s popisy]
```

Když běžel jen výchozí rozsah a projekt je starší, připomeň, že `/standards full` projede i to, čeho se tahle větev nedotkla.
