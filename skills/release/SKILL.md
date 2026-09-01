---
name: release
description: Skill se použije, když uživatel zadá "/release", nebo chce nasadit hotovou práci do produkce – projít brány před nasazením, ošetřit migrace databáze, nasadit, ověřit smoke testem a vědět, jak se vrátit zpátky. Nikdy se nespouští sám ani jako pokračování jiného skillu.
allowed-tools: [Read, Grep, Glob, Bash, Edit, Write, AskUserQuestion, Skill]
---

# Release

## Co skill dělá

Nasadí hotovou práci do produkce – s branami před, s plánem návratu a s ověřením po.

V ose *Životního cyklu práce* (`~/.claude/RULES.md`) stojí **mimo uzavírání, až za ním**. To není kosmetika: uzavírání mění repozitář, nasazení mění svět, kde jsou cizí data a živí uživatelé. Chyba v repozitáři se opraví commitem, chyba v produkci se opravuje před lidmi, kteří na to koukají.

## Tvrdá pravidla

Tahle pětice platí bez výjimky a bez ohledu na to, jak triviální změna to je:

1. **Nikdy se nespouští sám.** Ani jako pokračování `/implement`, `/review` nebo `/cleanup`. Ani když uživatel řekl „a nasaď to“ na začátku dlouhé session – to byl záměr, ne potvrzení. Potvrzení se dává **teď a k tomuhle konkrétnímu nasazení**.
2. **Nasazuje se jen zelený, prověřený stav.** Neproběhlo `/review`? Řekni to a zeptej se, jestli opravdu chce nasadit neprověřenou práci.
3. **Návrat musí existovat dřív, než se nasadí.** Když neumíš odpovědět na otázku „jak se vrátíme za deset minut zpátky“, nenasazuj a vyřeš nejdřív ji.
4. **Migrace dat se nikdy nemíchá s nasazením kódu do jednoho nevratného kroku.** Viz *Migrace*.
5. **Do produkční větve se nemerguje mimo tenhle skill.** Nasazuje-li platforma automaticky (a to je výchozí chování), je merge do `main` **totéž co nasazení**. Kdo mergne mimo `/release`, nasadil bez bran – a nevěděl o tom.

## Když nasazuje platforma sama

Vercel, Netlify i Cloudflare Pages nasazují **pushnutím do produkční větve**. Nedá se to obejít tím, že se „nasadí až potom“ – žádné potom není. Z toho plynou dva důsledky, které si stojí za to přečíst dvakrát:

- **`/release` je brána *před* mergem, ne krok po něm.** Všechny kontroly z Fáze 1 a 2 běží na větvi. Merge je poslední úkon skillu, ne jeho předpoklad.
- **Na produkční větvi se nepracuje.** Nikdy na ni necommituj přímo. Ve worktree layoutu to vychází samo (`~/Dev/context/worktree/worktree.md`), jinde založ větev. Commit do `main` „jen na opravu překlepu“ je nasazení bez jediné brány.

**Pojistky, které stojí za zvážení** – nabídni je, když projekt žádnou nemá, ale nevnucuj je:

| Pojistka | Co dělá | Cena |
|---|---|---|
| Ochrana větve na GitHubu | `main` jde měnit jen přes pull request | u sólo projektu trochu obřadné, ale funguje |
| Produkční deploy jen z tagu | platforma nasazuje na tag, ne na push | rozbije preview workflow, nastavuje se jednou |
| `pre-push` hook | odmítne push do `main` bez značky od `/release` | lokální, snadno obejitelné, ale chytí zapomnětlivost |

Zjistíš-li v Pre-flightu, že projekt má auto-deploy a **žádnou pojistku**, řekni to nahlas jednou větou. Ne jako výtku – jako informaci, že jediná brána mezi rozpracovanou prací a produkcí je tenhle skill.

## Co skill nedělá

- **Neopravuje.** Najde-li brána problém, skill **skončí** a pošle to zpátky do `/implement` nebo `/review`. Neopravuj v předvečer nasazení – změna, která neprošla review, je přesně ta, která spadne.
- **Nerozhoduje o obsahu vydání.** Co se nasazuje, je to, co je na větvi. Vybírat commity na poslední chvíli je cesta k tomu nasadit půlku feature.
- **Nezakládá infrastrukturu.** Nastavení prostředí, domén a proměnných je jednorázová práce, ne součást každého vydání.

------

## Fáze 0 – Pre-flight

1. **Kořen projektu.** Ve worktree layoutu (`~/Dev/context/worktree/worktree.md`) pracuj v adresáři té větve, která se nasazuje.
2. **Přečti projektový `CLAUDE.md`** – `## Příkazy` (*Kontrakt příkazů*), `## Nasazení`, pokud existuje, a `## Výjimky z obecných pravidel`.
3. **Zjisti, jak se projekt nasazuje.** V tomhle pořadí:

   | Kde hledat | Co z toho plyne |
   |---|---|
   | `## Nasazení` v `CLAUDE.md` | hotový popis – použij ho |
   | `vercel.json`, `netlify.toml`, `wrangler.toml`, `.github/workflows/` | nasazuje platforma sama po pushnutí do větve |
   | `Dockerfile`, `compose.yml`, deploy skript | nasazuje se příkazem |
   | nic z toho | **Zeptej se** přes `AskUserQuestion` a odpověď rovnou zapiš do `## Nasazení` v `CLAUDE.md`, ať se příště neptáš |

4. **Zjisti, co se vlastně nasazuje.** Diff proti tomu, co je v produkci – nejlépe proti tagu posledního vydání. Vypiš: kolik commitů, které oblasti, jestli jsou mezi nimi **migrace**, změny **konfigurace nebo proměnných prostředí** a změny v **citlivých oblastech** ze seznamu v `docs/architecture.md`.

Zjištěné shrň do tří až pěti řádků. **Ještě nenasazuj.**

------

## Fáze 1 – Brány před nasazením

Všechny běží proti **čistému stromu**, ne proti tomu, co máš rozpracované. Neprojde-li kterákoliv, **skonči** a řekni, co je potřeba dodělat.

1. **Pracovní strom je čistý** a větev je pushnutá. Necommitnutá změna při nasazení znamená, že v produkci bude něco jiného, než co je v gitu – a to se hledá měsíce.
2. **Zelená linka na čistém buildu.** Nikoliv „běželo to ráno“. Produkční `build` zvlášť, i když ho testy nepotřebují: „běží to v devu“ a „projde produkční build“ jsou dvě různá tvrzení a druhé padá na typech, tree-shakingu a proměnných prostředí.
3. **Proběhlo `/review`?** Nevíš-li, zeptej se. U změny v citlivé oblasti je to **podmínka**, ne doporučení.
4. **Audit závislostí** – `audit` z kontraktu. `HIGH` a `CRITICAL` blokují.
5. **Tajemství v repu** – `gitleaks detect`, je-li k dispozici. Nález blokuje vždy; a co bylo commitnuté, patří **rotovat**, ne jen smazat.
6. **Proměnné prostředí.** Přibyla-li v kódu nová, **ověř, že je nastavená v produkci**, ne jen lokálně v `.env`. Tohle je nejčastější příčina toho, že build projde a aplikace spadne až na produkci.

------

## Fáze 2 – Migrace

**Přeskoč, nejsou-li v rozsahu žádné migrace.** Jsou-li, platí:

**Dopředu kompatibilně (expand/contract).** Nasazení se rozděluje na kroky, mezi kterými funguje stará i nová verze kódu:

1. **Expand** – přidej nové (sloupec jako nullable, nová tabulka, nový klíč). Stará verze si toho nevšimne.
2. **Nasaď kód**, který umí obojí – čte staré i nové.
3. **Backfill** dat, odděleně a měřitelně.
4. **Contract** – teprve v dalším vydání odeber, co už nikdo nečte.

**Během okna, kdy se dá vrátit zpátky, se nic neodstraňuje ani nepřejmenovává.** Odebraný sloupec znamená, že rollback kódu shodí aplikaci na datech, která nová verze zapsala – a máš rozbito na obou stranách.

**Před migrací záloha, která je ověřená.** Ne „hosting to nějak zálohuje“ – konkrétní soubor nebo snapshot, o kterém víš, kdy vznikl a jak se z něj obnovuje. U nevratné migrace to řekni nahlas a nech si to zvlášť potvrdit; platí `~/.claude/RULES.md`, *Před nevratnou akcí ověř skutečný stav*.

------

## Fáze 3 – Potvrzení

Teprve teď se ptáš, a ptáš se **jednou otázkou přes `AskUserQuestion`** nad kompletním přehledem:

```
## Připraveno k nasazení

**Co:** <N commitů> · <oblasti> · <verze/tag>
**Kam:** <prostředí a URL>
**Brány:** zelená linka ✅ · build ✅ · review ✅/❓ · audit ✅ · tajemství ✅
**Migrace:** <žádné / expand krok N, záloha z HH:MM>
**Citlivé oblasti:** <které se mění, nebo „žádné">
**Návrat:** <konkrétně – revert commitu a redeploy / promote předchozí verze / obnovení ze zálohy>
**Po nasazení sleduji:** <co konkrétně a jak dlouho>
```

Volby: **Nasadit** / **Nejdřív na preview** / **Zrušit**.

Bez výslovné odpovědi se nenasazuje. Ticho není souhlas.

------

## Fáze 4 – Nasazení

**Platforma s auto-deployem** (Vercel, Netlify, Cloudflare Pages) – nasazuje se pushnutím, ne příkazem:

1. **Nejdřív preview.** Push do větve vyrobí preview URL. Otevři ji a projdi na ní smoke test z Fáze 5, **než** cokoliv půjde do hlavní větve. Preview je zdarma a je to jediné místo, kde se chyba dá najít bez následků.
2. **Merge do produkční větve** teprve po zeleném preview. **Tenhle merge je samotné nasazení** – od jeho provedení je změna venku, takže se dělá vědomě a jako poslední, ne mimochodem uprostřed jiné práce.
3. **Sleduj build na platformě** a jeho log. Build padá jinak než lokální – kvůli proměnným, verzi Node a cache.
4. **Tag.** Označ vydání tagem, ať je co vrátit a proti čemu příště diffovat.

**Jiné prostředí** (VPS, kontejner, klasický hosting) – použij příkaz z `## Nasazení`; chybí-li, vyžádej si ho a zapiš. Nikdy nevymýšlej deploy příkaz sám: špatně odhadnutý cíl přepíše cizí web.

Během nasazení **nic jiného neděl**. Žádné „ještě rychle opravím“.

------

## Fáze 5 – Ověření po nasazení

Nasazeno neznamená funguje. Ověř, a ověř na **produkční URL**, ne na localhostu:

1. **Načte se to.** Stavový kód, žádná chyba v konzoli, statické soubory sedí.
2. **Projde hlavní scénář.** Ten první z `docs/requirements.md` – klidně ručně přes prohlížeč (`chrome-devtools`), ale projdi ho celý, včetně odeslání formuláře nebo přihlášení.
3. **Data sedí.** Proběhla-li migrace, ověř na produkčních datech, že se čtou a zapisují správně.
4. **Chyby.** Podívej se do logu nebo monitoringu, jestli po nasazení nepřibyla nová třída chyb.

**Když je zle:** vrať se cestou z Fáze 3, hned. Neladí se to v produkci pod tlakem – nejdřív návrat, potom hledání příčiny.

------

## Fáze 6 – Zápis a shrnutí

Zapiš do `docs/decisions.md` jen to, co má trvalou hodnotu (změna postupu nasazení, potíž, která se bude opakovat), a do `docs/done.md` samotné vydání. Rutinní nasazení nikam zapisovat netřeba – to je v gitu.

```
## Nasazeno

**Verze:** <tag> · **Kdy:** <čas> · **Kam:** <prostředí>
**Obsah:** <N commitů, oblasti>
**Migrace:** <co proběhlo, nebo „žádné">
**Ověřeno:** <co konkrétně jsi prošel>
**Návrat:** <jak se vrátit, dokud je to aktuální>

**Zbývá dokončit:** [contract krok migrace v příštím vydání / nic]
```

Zakonči jednou z těchto vět, nikdy ničím vágním mezi tím:

- `Nasazeno a ověřeno na produkci.`
- `Nasazeno není – brání tomu: <konkrétní seznam>.`
- `Nasazeno bylo, ale ověření selhalo – vrátil jsem to zpátky, protože: <důvod>.`
