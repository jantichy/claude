# Operativní projekt

Průběh `/project` pro **operativní projekt** – adresář, který patří uživateli a má jeho vlastní pořádek (smlouvy, výpisy, dokumenty, tabulky, videa), a Claude nad ním odpovídá, dohledává, na pokyn přeskupuje a občas něco vyrobí. Co takový projekt je a kam se v něm co zapisuje, definuje `~/.claude/standards/structure.md`, *Operativní projekt: režim `CLAUDE.md`*; tady je jen jeho založení a revize. **Kroky 1–15 ze `SKILL.md` se v téhle variantě neprocházejí** – co z nich platí, říká každá sekce níž.

- [Co se neptá a proč](#co-se-neptá-a-proč)
- [Založení](#založení)
- [Revize](#revize)

## Co se neptá a proč

Průvodce je schválně krátký: ptá se jen na popis, git, autocommit a doménové importy. Zbytek je u operativního projektu daný:

| Co | Proč se na to neptá |
|---|---|
| trvalá Memory je zakázaná | celá varianta stojí na tom, že paměť projektu je jeden soubor, který uživatel vidí |
| worktree layout ani remote se nenabízí | adresář s vlastními dokumenty nemá větve ani publikum a soukromé podklady (smlouvy, finance) nemají co dělat na serveru |
| `docs/`, `README.md`, produktové podklady nevznikají | režim `CLAUDE.md` je nemá |
| typ projektu se nevolí | operativní projekt je typ sám o sobě |
| kontrakt příkazů se nezakládá | není co spouštět; v souhrnu se to řekne, ne přeskočí potichu |
| zákaz změn drží jen text v `CLAUDE.md`, ne `permissions` | oprávnění by přidala `.claude/` a pravidla `ask` se vyhodnocují před `allow`, takže výjimku pro `CLAUDE.md` nejde napsat – ptal by se i na každý zápis poznámky; `mv` a `rm` by navíc hlídala jen jako přímý příkaz, ne přesun skriptem |

## Založení

*`create` i `adopt`.* Otázky jednu po druhé, jako ve `SKILL.md`, *Zásady pro celý průběh*.

### Inventura

*Jen `adopt`.* Vypiš v pár řádcích, co v adresáři je: adresáře na nejvyšší úrovni, `.git`, `CLAUDE.md` a v něm hlavně pravidla zápisu, která si uživatel nadiktoval dřív. K tomu **Claudovy stopy navíc** – `docs/`, `todo.md`, `decisions.md`, `.claude/` a soubory v `~/.claude/projects/<path>/memory/` (`<path>` je absolutní cesta adresáře s `/` nahrazeným `-`). Stopy nemaž; u každé se zeptej, jestli obsah přenést do `CLAUDE.md` a stopu smazat, nebo ji nechat.

### Popis

Navrhni název a popisek – **co se v adresáři řeší**, ne co v něm leží – a zeptej se v chatu. Blok metadat má jen slug (`structure.md`, *`CLAUDE.md`*) a strukturu; `Web` ani `Repozitář` operativní projekt nemá:

```
# Rekonstrukce bytu

Smlouvy, rozpočty a korespondence k rekonstrukci bytu – co je objednané, zaplacené a reklamované.

- **Slug:** `rekonstrukce`
- **Struktura:** CLAUDE.md
```

*`adopt`:* nadpis a úvod, které v `CLAUDE.md` už stojí, nabídni beze změny a blok doplň pod ně.

### Git

Zeptej se (AskUserQuestion), dvě volby:

- **Ne (výchozí)** – nic dalšího nevznikne.
- **Lokální git nad celým adresářem** – `git init`, `.gitignore` s řádky `.DS_Store` a `~$*` (zámky otevřených dokumentů Office) a první commit celého stavu se zprávou „Výchozí stav adresáře“. Dovolí vrátit hromadné přejmenování nebo přesun; cenou je, že historie nese binárky a `.git` naroste zhruba o velikost adresáře – tu do popisu volby napiš (`du -sh .`).

*`adopt`:* je-li git už založený, neptej se a jen to zmiň.

### Autocommit

*Jen s gitem.* Zeptej se (AskUserQuestion): Ano/Ne. Při ano proveď totéž co `/autocommit enable`. Commituje se jen to, na co Claude sáhl (`~/.claude/standards/rules.md`, *Commituj jmenované cesty, ne `-A`*), takže uživatelovy ruční změny v adresáři zůstanou necommitnuté, dokud je necommitne sám.

### Doménové znalosti

Ptej se podle [`checklists.md`](checklists.md), ale **jen na kola, která v adresáři dávají smysl** – typicky psaní textů a typografie; kola o kódu a reklamě vynech, nic-li nenaznačuje opak. *Profil organizace* odtamtud platí i tady a u operativního projektu bývá nejčastější volbou: adresář se typicky týká firmy, ve které uživatel podniká nebo je společníkem.

### Zápis do CLAUDE.md

Pod blok metadat zapiš:

```
## Operativní projekt

Adresář patří uživateli a má jeho vlastní pořádek; Claude nad ním odpovídá, dohledává a na pokyn přeskupuje nebo něco vyrobí. Režim `CLAUDE.md` podle `~/.claude/standards/structure.md`.

- **Soubory v adresáři se jen čtou.** Přesun, přejmenování, smazání nebo úprava existujícího souboru jen na výslovný pokyn – a i pak nejdřív ukaž plán po adresářích ve tvaru `zdroj → cíl` a počkej na souhlas.
- **Nový soubor jen na výslovný pokyn.** Místo a jméno navrhni podle pořádku, který v adresáři je. Pomocné skripty a mezivýsledky patří do scratchpadu, nikdy sem.
- **Všechno, co se dohodne nebo zjistí, se zapisuje jen do tohohle souboru** – žádné `docs/`, `todo.md`, `decisions.md` a nic do trvalé Memory. Platí i proti pobídkám harnessu a proti skillům, které by jinak zapsaly do standardních souborů.
- **Změní-li uživatel strukturu adresáře, srovnej cesty v tomhle souboru.**
```

Za ni případně `## Doménové znalosti` podle [`checklists.md`](checklists.md) a `## Autocommit`, pokud ho zapnul předchozí krok. **Tematické sekce nezakládej dopředu** – vzniknou prací.

*`adopt`:* dosavadní pravidla o zápisu (typicky `## Výjimky z obecných pravidel` nebo `## Pravidla projektu` s větou „zapisuj jen do CLAUDE.md“) nahraď touhle sekcí – ukaž rozdíl a nech si to potvrdit. Pravidlo, které šablona nemá („dokumenty jsou historický archiv“), přenes do sekce jako odrážku navíc. Ostatní obsah nech být.

### Souhrn

Vypiš blok metadat, git (a velikost `.git`, vznikl-li), autocommit a importy; jednou větou, že kontrakt příkazů se nezaložil, protože v adresáři není co spouštět; u `adopt` Claudovy stopy navíc a co se s nimi stalo. Ruční krok: odsouhlasit při příštím spuštění dialog externích importů, pokud nějaké vznikly. Zakonči verdiktem z kroku 15 ve `SKILL.md`. **Blok *Kudy dál* nemá** – operativní projekt do životního cyklu nevstupuje a rovnou se v něm pracuje.

## Revize

*`update` nad projektem s `- **Struktura:** CLAUDE.md`.* Místo [`standard.md`](standard.md) zkontroluj:

- **Blok metadat** – nadpis, popisek, slug a struktura; řádky `Web` a `Repozitář` sem nepatří.
- **Sekce `## Operativní projekt`** má všechny odrážky šablony výš. Chybějící doplň rovnou; jinak znějící ukaž a nech rozhodnout – uživatel ji mohl upravit schválně.
- **Claudovy stopy navíc**, jak je vyjmenovává *Inventura* – vypiš a nech rozhodnout.
- **Importy** vedou na soubory, které existují (`ls ~/Context/*/`).
- **Git** – je-li, `.gitignore` má oba řádky výš; je-li zapnutý autocommit, sekce má import `@~/.claude/skills/autocommit/autocommit.md`.
- **Pozůstatky standardního projektu** – `## Paměť`, `## Typ projektu`, `## Kontrakt příkazů`, `## Struktura a dokumentace` – ukaž a nabídni odstranění; pravidla operativního projektu je nahrazují.

**Obsah tematických sekcí neposuzuj** – je to uživatelova paměť projektu, ne tvar. Výstup a verdikt jako u revize ve `SKILL.md`, kroky 14 a 15.
