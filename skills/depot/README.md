# /depot – stažený soubor doputuje tam, kam patří, a rovnou se zpracuje

Stáhnete nahrávku ze schůzky, prezentaci z konference, cizí studii nebo podklad od klienta – a ono to všechno zůstane ležet v Downloads, protože zařadit to a něco s tím udělat je na deset minut, které zrovna nemáte. Tenhle skill ty dvě věci spojí do jednoho příkazu: řeknete mu soubor, on pozná, co to je, uloží to na správné místo pod správným názvem a hned spustí, co po tom má následovat – přepis, vytěžení do vaší knowledge base, zápis do evidence.

Podstatné je, že **sám nerozhoduje podle ničeho vlastního.** Všechna pravidla – co se jak pozná, kam to jde, co se s tím pak stane – si čte z vašeho vlastního souboru, který si napíšete podle svého. Skill je mechanika, pravidla jsou vaše.

## Co umí

- **`/depot <soubory>`** (výchozí) – rozpozná, ukáže plán celé dávky, po odsouhlasení přesune a spustí navazující zpracování.
- **`/depot store <soubory>`** – jen zařadí a skončí. Na vyklizení Downloads, když na zpracování není čas.
- **`/depot workflow`** – otázku po otázce s vámi založí nové pravidlo, nebo upraví stávající.
- Zvládne jeden soubor, víc souborů, masku i adresář. Soubory z jedné události uloží do jednoho místa pohromadě.
- Nepozná-li, o co jde, nebo sedí-li pravidel víc, **nabídne varianty k výběru** – a u každé rovnou říká, kam by soubor šel a co by se spustilo.
- Novým pravidlem si rozšíří vlastní tabulku rovnou za běhu, takže se totéž příště neptá.

## Proč zrovna tenhle

- **Zařazení a zpracování je jeden úkon, ne dva.** Rozdělené na dvě chvíle se ta druhá nekoná.
- **Rozsah je přesně to, co zadáte.** Nesáhne na okolní soubory, nezačne uklízet celou složku a nerozbalí podadresáře bez zeptání – tohle je přesně to, na čem obecný asistent selže a proslulé „když už jsem tady“ skončí nevratným hromadným přesunem.
- **Nic nepřepíše a nic nesmaže.** Při kolizi se zastaví a zeptá, místo aby přilepil `(1)` a vyrobil duplikát, o kterém pak nikdo neví.
- **Neptá se v půlce práce.** Všechna rozhodnutí padnou nad plánem, než se hne první soubor.
- **Citlivé věci nesměruje sám.** Přístupové kódy, smlouvy a osobní doklady vypíše a nechá rozhodnout vás – a kvůli rozpoznání je ani neotevře.
- **Roste používáním.** Každý neznámý podklad je příležitost doplnit pravidlo, ne otrava navíc.

## Jak se to používá

```
/depot ~/Downloads/prednaska-measurecamp.m4a
/depot store ~/Downloads/*.pdf
/depot workflow
```

Skill ukáže tabulku „soubor → co to je → kam to jde → co se pak spustí“, počká na odsouhlasení a pak to provede.

## Ukázka výstupu

```
Plán – 3 soubory

| Soubor | Workflow | Kam | Pak |
|---|---|---|---|
| prednaska.m4a | Přepsat nahrávku a vytěžit ji | ~/Depot/20260912 - MeasureCamp - Konverzační analytika/ | /transcript, pak /learn |
| slajdy.pdf | Vytěžit cizí materiál z akce | tamtéž – jedna událost, jeden adresář | /learn |
| export-ga4.csv | Uložit ke klientovi | ~/Dev/favi/research/ | nespouští se nic |

Mimo směrování: recovery-codes.txt – přístupové údaje, rozhoduje člověk
```

## Co nedělá

- **Neuklízí složku.** Zařadí to, co mu dáte, a nic kolem.
- **Nevytěžuje znalost sám** – volá na to `/learn`, který ji rozpouští do existujících textů.
- **Nepřepisuje nahrávky sám** – to dělá `/transcript`.
- **Nesahá na to, co už je uložené.** Nepřejmenovává, nepřesouvá podruhé, nemaže.

## Jak si ho nainstalovat

> Jdi na https://github.com/jantichy/claude/tree/main/skills/depot
> a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.

**Pak mu ještě musíte napsat pravidla** – skill sám žádná nemá a bez nich se vědomě nerozjede. Je to jeden Markdownový soubor s tabulkou, kde má každý řádek čtyři sloupce: *jak se podklad pozná · kam se uloží · co se s ním pak stane · jak se pojmenuje cílové místo*. Nejjednodušší je nechat si ho založit skillem samotným – pusťte `/depot workflow` a projde to s vámi otázku po otázce. Kam ten soubor uložit a jak se k němu má skill dostat, si řekněte s Claudem podle toho, jak máte uspořádané vlastní poznámky.

---

### Požadavky a omezení

Běží kdekoliv, kde běží Claude Code, a nepotřebuje žádnou instalaci navíc. Navazující zpracování je ale jen tak schopné, jako jsou nástroje, na které ukážete: přepis nahrávek předává skillu `/transcript` (lokální whisper.cpp, macOS i Linux), vytěžení do knowledge base skillu `/learn`. Bez nich zůstane u zařazení souborů, což je pořád polovina užitku. Pravidla si píšete sami a jsou vaše – v repozitáři žádná nejsou a být nemůžou, protože jsou to vaše složky a váš způsob práce.
