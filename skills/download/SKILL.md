---
name: download
description: Skill se použije, když uživatel zadá "/download" a k tomu odkazy, nebo chce něco zařadit ke stažení na pozadí – přidat soubor či celou složku z Google Drive nebo jinou adresu do fronty, "stáhni mi tuhle složku z Drive", "dej to do stahování". Plní seznam ~/Downloads/downloads.md, který odbavuje autorův nástroj clockwork: složky na Google Drive rozbalí přes konektor Google Drive i s podsložkami, určí cílovou podsložku v ~/Downloads, vynechá adresy, které v seznamu už jsou, a dokumenty Google i složky mimo Drive, které stáhnout nejdou, jen vypíše. Sám nic nestahuje. Na rozdíl od /depot, který už stažené soubory zařazuje a zpracovává, tenhle skill jen plní frontu ke stažení.
argument-hint: <odkazy> [složka]
allowed-tools: [Bash, Read, AskUserQuestion, mcp__claude_ai_Google_Drive__search_files, mcp__claude_ai_Google_Drive__get_file_metadata]
---

# Download

## Co skill dělá

Doplní do `~/Downloads/downloads.md` položky ke stažení. Ten seznam na pozadí odbavuje clockwork: stahuje po jedné, navazuje po výpadku sítě a hotové řádky odškrtává. Skill převede to, co uživatel dá, na řádky, kterým clockwork rozumí. Rozbalí složku na Google Drive na jednotlivé soubory, určí, do které podsložky `~/Downloads` co patří, a pohlídá, aby se nic nestáhlo dvakrát.

Režimy nemá. Argument tvoří odkazy a volitelně cílová složka – všechno, co není adresa, je složka (`/download https://drive.google.com/drive/folders/… Kosmologie 2024`). Požadované jméno souboru se píše jen tehdy, když ho uživatel sám řekne.

**Formát seznamu je rozhraní clockworku, ne tohohle skillu.** Drží ho `~/Projects/Clockwork/docs/architecture.md`, sekce *Úloha `download`*. Skript `add.py` z něj přebírá tvar řádku i normalizaci adres a `tests/test_download.py` ověřuje, že zapsaný seznam přečte parser clockworku stejně.

## Co skill nedělá

- **Nestahuje.** Stahování, navazování, kontrolu velikosti a odškrtnutí dělá clockwork. Skill do seznamu jen připisuje a hotové řádky nemění.
- **Nezařazuje stažené.** Kam soubor z `~/Downloads` patří a co se s ním dál udělá, rozhoduje `/depot`. Cílová podsložka tady je jen místo v `~/Downloads`, ne zařazení.
- **Nepřejmenovává podle obsahu.** Jméno za šipkou zapíše jen na výslovný pokyn. Jinak ho clockwork vezme ze zdroje, takže se jméno určuje na jednom místě.
- **Nerozbaluje složky mimo Google Drive.** Dropbox, OneDrive ani výpis adresáře na webu nerozbaluje, takový odkaz jen vypíše jako odmítnutý.

## Jak je to postavené uvnitř

| Krok | Kdo | Proč zrovna on |
|---|---|---|
| Výpis složky a metadata souboru na Drive | konektor Google Drive (`mcp__claude_ai_Google_Drive__search_files`, `mcp__claude_ai_Google_Drive__get_file_metadata`) | vidí soubory pod týmž účtem, pod kterým stahuje clockwork |
| Normalizace adres, duplicity, zařazení pod nadpis, atomický zápis, kontrola zapsaného | skript `add.py` v adresáři skillu | jediná správná cesta bez odboček; testuje ji `tests/test_download.py` |
| Rozpoznání odkazu, cílová složka, co vynechat, výpis | vlastní | tady se rozhoduje |

**Konektor i skript jsou implementační detail.** Závazné je: do seznamu jde jen řádek ve tvaru clockworku, nic se nepřidá dvakrát, soubor se nikdy nezapíše napůl (clockwork ho čte souběžně) a výpis jmenuje každou vynechanou položku i s důvodem.

## Fáze 0 – Příprava

Skill nad projektem neběží – pouští se odkudkoliv a pracuje se seznamem v `~/Downloads`, takže **body 1 až 3 z `~/.claude/skills/preflight.md` se vynechávají**. Kořen projektu, `CLAUDE.md` ani stav gitu ho nezajímají. Vlastní předpoklady:

1. **Argument.** Bez jediné adresy se zeptej, co zařadit, a nic nespouštěj.
2. **Konektor Google Drive** je potřeba jen u odkazu na Drive. Chybí-li, řekni to a odkazy na Drive vypiš jako nezpracované. Ostatní adresy zapiš i tak.
3. **Seznam leží mimo repozitář a nic se necommituje.** Neexistuje-li, skript ho založí.

## Fáze 1 – Rozbor vstupu

Rozděl argument na adresy a cílovou složku (`folder`): složka je všechno, co adresou není, spojené do jedné cesty. Jméno, které uživatel výslovně přiřadí k souboru („ten první ulož jako *Úvod*“), je `name` té položky.

Každou adresu zařaď:

| Adresa | Co s ní |
|---|---|
| `drive.google.com/drive/folders/<id>` (i `/drive/u/0/folders/…`) | složka na Drive → *Fáze 2* |
| `drive.google.com/file/d/<id>/…`, `open?id=`, `uc?id=` | soubor na Drive → rovnou do *Fáze 3* |
| `docs.google.com/document/…`, `/spreadsheets/…`, `/presentation/…` | dokument Google → vynechat, clockwork ho stáhnout neumí |
| jiná `http` nebo `https` | soubor → rovnou do *Fáze 3* |
| cokoliv jiného, i složka na Dropboxu či OneDrive | vynechat s důvodem |

Neodmítej ručně to, co odmítne skript – třídění z tabulky je jen kvůli tomu, co se má rozbalit. Poslední slovo o zápisu má `add.py`.

## Fáze 2 – Rozbalení složky na Drive

1. **Jméno složky** zjisti přes `mcp__claude_ai_Google_Drive__get_file_metadata` s `excludeContentSnippets: true`. Cílová složka položek je `folder` z argumentu, a není-li, právě tohle jméno. Z jména odstraň `/` a `:` – na Drive v názvu být smějí, v cestě ne.
2. **Obsah** vypiš přes `mcp__claude_ai_Google_Drive__search_files` s dotazem `parentId = '<id>'`, `excludeContentSnippets: true` a s `pageToken` až do prázdné stránky. Stránky se mohou překrývat, takže soubory deduplikuj podle id.
3. **Podsložku** (`mimeType` `application/vnd.google-apps.folder`) rozbal stejně a její soubory dej pod `<cílová složka>/<jméno podsložky>`. Struktura na Drive se tím zrcadlí v `~/Downloads`.
4. **Dokument Google** (jiný `mimeType` začínající `application/vnd.google-apps.`) vynech a zapamatuj si ho do výpisu.
5. **Pořadí** uvnitř každé složky je přirozené řazení podle jména (`2` před `10`), protože clockwork stahuje v pořadí řádků.
6. **Adresa souboru** je `https://drive.google.com/file/d/<id>/view`.

**Nad 50 souborů v rozbalené složce se před zápisem zeptej**, jestli to opravdu chce celé. Clockwork se pustí do stahování bez dalšího ptaní a omylem vložená velká složka zabere disk i linku na hodiny.

**Nenajde-li konektor složku**, nehádej. Konektor je připojený k jednomu Google účtu a do Sdílených disků vidí, takže skoro vždycky jde o složku jiného účtu – odkaz s `/u/<číslo>/` ukazuje na jiný účet přihlášený v prohlížeči. Řekni to a nabídni nejjednodušší cestu: nasdílet složku účtu, ke kterému je připojený konektor a přihlášený clockwork. Položku vypiš jako nezpracovanou.

## Fáze 3 – Zápis

Pošli všechny položky naráz skriptu, ať se seznam čte i zapisuje jen jednou:

```bash
python3 ~/.claude/skills/download/add.py <<'EOF'
{"items": [{"url": "https://drive.google.com/file/d/1AbC/view", "folder": "Kosmologie 2024"},
           {"url": "https://example.org/uvod.pdf", "folder": "", "name": "01 Úvod"}]}
EOF
```

`force: true` dej položce jen tehdy, když uživatel výslovně chce znovu stáhnout adresu, která v seznamu už je. Výchozí chování je duplicitu přeskočit, i když je už stažená.

Výstup je jeden řádek JSON:

| Klíč | Co znamená |
|---|---|
| `added` | zapsané položky |
| `skipped` | duplicity – `folder`, kde adresa už stojí, a `done`, jestli je stažená |
| `rejected` | co skript nezapsal, i s důvodem |
| `verified` | každá přidaná položka se v zapsaném souboru opravdu našla |
| `error` | zápis selhal – soubor se mezitím pořád měnil, nebo nejde číst |

**Kód 1 nebo `verified: false` znamená, že seznam doplněný není.** Neopravuj ho ručně nástrojem pro úpravu souborů – ten nezapisuje atomicky a clockwork by mohl přečíst napůl zapsaný soubor. Řekni, co skript vrátil, a skonči druhou závěrečnou větou.

## Fáze 4 – Závěr

```
**Do stahování přidáno N položek** – <složka>: N, <složka>: N, kořen ~/Downloads: N

**Přeskočeno**
- <adresa nebo jméno> – už v seznamu ve složce <složka>, <čeká / staženo>
- <jméno> – dokument Google, stáhni ho exportem ručně
- <adresa> – <důvod>
```

Vypisuj to jako **Markdown, ne jako blok kódu**, a řádky nezalamuj natvrdo – `~/.claude/standards/rules.md`, *Styl odpovědí*. Prázdnou část vynech; u složky s desítkami souborů je stačí sečíst, jednotlivá jména nevypisuj.

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Seznam je doplněný a ověřený, clockwork položky stáhne v příštím běhu.`
- `Seznam doplněný není – brání tomu: <konkrétní seznam>.`
