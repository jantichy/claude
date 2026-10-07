# Kola návrhu

Jak se v souborech projektu zapisuje návrh rozdělený na tematická kola. Co je kolo, kdy vzniká a jak běží, drží `~/.claude/skills/architect/SKILL.md`; tenhle soubor drží **tvar zápisů**, protože je kromě `/architect` čtou i `/next`, `/breakdown`, `/merge` a `/cleanup`. **Odkaz, ne import** – načítá se, když se sahá na sekci `## Kola návrhu` v `todo.md` nebo `done.md` nebo na kapitolu kola v `decisions.md`.

## V `todo.md`

**Sekce `## Kola návrhu`** je mapa kol, na která `/architect` rozdělil větší návrh. Co je kolo, kdy vzniká a jak běží, drží `~/.claude/skills/architect/SKILL.md`; jak se kola čtou a nabízejí, `~/.claude/skills/next/SKILL.md`, *Kola návrhu*. Na každé kolo připadá jeden blok v tomhle tvaru:

```markdown
### Kolo o <tématu>

- **Stav:** čeká | rozhoduje se | rozhodnuto
- **Větev:** `<větev podle zvyku projektu>`
- **Dokument:** `docs/<topic>.md`
- **Čeká na:** <kola, bez jejichž výsledku nejde začít, nebo „nic“>
- **Sahá na:** <sdílené dokumenty, do kterých kolo nejspíš zapíše>

**Co rozhodnout.** <otázky, na které má kolo odpovědět – zadání, ne odpověď>

**Podklady.** <co si před kolem přečíst>

**Odložené otázky.** <otázky odložené na tohle kolo odjinud, každá s tím, kde vznikla>
```

- **Blok musí stačit čisté session.** Kolo se typicky otevírá v jiné session a jiné větvi, takže blok nese celé zadání a neodkazuje na konverzaci, ve které vznikl.
- **Otázka odložená na kolo se zapisuje do jeho bloku**, ne jako samostatná položka s poznámkou „patří ke kolu o …“. Jinak se ztratí, jakmile kolo proběhne bez ní: položka dál čeká na něco, co už se nestane, a nerozezná se od fronty.
- **O pořadí rozhoduje řádek *Čeká na*, ne pořadí bloků.** Kola bez nesplněné závislosti smí běžet souběžně; řádek *Sahá na* říká, kde se jejich větve můžou srazit.
- **Hotové kolo se přesune do stejnojmenné sekce `done.md`**, v tvaru popsaném tam. Blok se maže až tímhle přesunem, a ten proběhne ve větvi kola těsně před sloučením.
- Sekce žije jen po dobu návrhu po kolech; po posledním kole do ní `/architect` zapíše řádek *Návrh sešitý* a při dočištění ji zruší – kromě bloků kol puštěných až za sešití, které zůstanou jako další várka. Chybějící sekce znamená totéž co sekce bez bloků.

## V `done.md`

**Sekce `## Kola návrhu`** zrcadlí stejnojmennou sekci `todo.md` a drží jeden záznam za každé dokončené kolo návrhu:

```markdown
- **Kolo o <tématu> (2026-09-14)** · větev `<branch>` · `docs/<topic>.md` · [rozhodnutí](../docs/decisions.md#<anchor>)
  - **Rozhodlo:** <co padlo, věcně, včetně zamítnutého hlavního směru>
  - **Uzavřelo:** <odložené otázky, které kolo vyřešilo, nebo „nic“>
  - **Neotevřelo:** <odložené otázky, které kolo nechalo být, a kam se přesunuly, nebo „nic“>
  - **Nová kola:** <kola, která z tohohle vzešla, nebo „žádná“>
```

Datum vyrob `date +%F`. Po posledním kole připíše `/architect` řádek `- **Návrh uzavřen (<datum>)** – <počet> kol` – podle něj se pozná, že doběhla celá várka kol; zůstaly-li v `todo.md` bloky další várky, návrh uzavřený celý není.

**Nejcennější je pole *Neotevřelo*** – odliší **nerozhodnuté** od **rozhodnutého jinak**, což z dokumentace vyčíst nejde; proto je povinné i jako „nic“. Pevný tvar má proto, že ho čte `/architect` při rozhodování, co je na řadě.

## V `decisions.md`

**Kapitola kola návrhu se píše bez čísla**, i když ho ostatní kapitoly mají; číslo dostane těsně před sloučením větve kola (`~/.claude/skills/architect/SKILL.md`), protože souběžná kola by si jinak vzala totéž.

## Tematické dokumenty

**Návrh po kolech přidává tematické dokumenty** `docs/<topic>.md` (například `gateway.md`, `emails.md`, `admin.md`), jeden na kolo. Tematický dokument drží celý okruh do detailu. Do `requirements.md` a dalších sdílených dokumentů (glosář, scénáře, model) zapisuje kolo jen to, co z tématu plyne pro celek, a odkazuje se na něj. **`architecture.md` kola nepíšou** – vzniká až nad výsledky všech kol, při sešití v `/architect`. Technickou volbu, kterou téma rozhodnout musí (třeba dodavatele), zapíše kolo do technické části svého dokumentu a `architecture.md` na ni pak odkáže. Hranice požadavků a návrhu tedy platí i uvnitř tematického dokumentu: omezení a volba se nemíchají, jen stojí u sebe. **Proč samostatný soubor:** kola běží souběžně v různých větvích a psaní do týchž kapitol sdílených dokumentů by je srazilo.
