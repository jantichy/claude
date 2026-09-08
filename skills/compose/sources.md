# Zdroje textů

Katalog pro režim `collect`: odkud se dají dostat autorovy texty, jak je převést do archivu a čeho se v jednotlivých exportech chytit. Pouští se s tím `/compose collect`.

- [Jak archiv vypadá](#jak-archiv-vypadá)
- [Sociální sítě](#sociální-sítě)
- [Weby, které ještě běží](#weby-které-ještě-běží)
- [Weby, které zanikly](#weby-které-zanikly)
- [Tištěná média a ostatní](#tištěná-média-a-ostatní)
- [Pasti, které stály čas](#pasti-které-stály-čas)

------

## Jak archiv vypadá

Není to jedna hromada textů. Archiv se člení **podle média**, protože kontext vydání je součástí dokladu – týž autor píše na svůj blog jinak než do odborného magazínu.

```
archiv/
  <doména nebo médium>/     YYYYMMDD - Titulek.md   (jeden text = jeden soubor)
  <síť>/                    Síť YYYY.md             (příspěvky po letech)
```

**Každý článek nese v hlavičce** datum publikace, médium, 1–3 tematické štítky a URL, je-li text online. **Ročníkové soubory sítí** nesou médium, období, počet příspěvků a cestu ke zdrojovému exportu.

**Příspěvek v ročníkovém souboru** má mezinadpis `### D. M. RRRR HH:MM UTC` a pod ním odrážky s URL, u odpovědí `- Odpověď na:`, u citací `- Citace postu:`. Navazující vlákna se slučují pod jeden mezinadpis.

Dvě věci, na kterých záleží víc, než vypadají:

- **Autorství.** Výchozí stav je autorský text. Cokoliv jiného – spoluautorství, text psaný AI – má vlastní řádek v metadatech. Bez něj se z archivu nedá vyfiltrovat to, co se nemá učit.
- **Přetisky.** Autoři si texty stěhují mezi weby, takže týž text existuje víckrát a mladší kopie tvrdí, že vznikl později. Soubor dokládá konkrétní publikaci; první výskyt patří na vlastní řádek.

## Sociální sítě

Exporty se připravují **hodiny až dva dny**. Vyžádej je na začátku, ne až budou potřeba.

| Síť | Kde se vyžádá | Co z toho zpracovat |
|---|---|---|
| X / Twitter | `https://x.com/settings/download_your_data` | `data/tweets.js`, dlouhé texty z `data/note-tweet.js`, identita z `data/account.js` |
| Facebook | `https://accountscenter.facebook.com/info_and_permissions/dyi` (formát **JSON**, rozsah „od začátku“) | `your_facebook_activity/posts/your_posts__…_1.json` |
| LinkedIn | `https://www.linkedin.com/mypreferences/d/download-my-data` | `Shares_*.csv` a `Comments_*.csv` z **kompletního** archivu |
| Bluesky | export repozitáře přes AT Protocol (`repo.car`) | všechny záznamy `app.bsky.feed.post` |

Převod dělají skripty ze `scripts/`; jejich volání i argumenty jsou v `SKILL.md`, *Jak je to postavené uvnitř*.

Berou cíl argumentem a **jsou idempotentní** – po novém exportu stačí pustit je znovu a rozdíl je vidět v gitu.

**Závislosti ověř dřív, než začneš stahovat.** Jediná je `cbor2` pro Bluesky (`python3 -c "import cbor2"`); chybí-li, řekni to hned a nabídni doinstalování – jinak se to pozná až po hodinách čekání na export.

**Co se vynechává:** reposty a sdílení bez vlastního komentáře, položky bez textu, lajky. Nejsou to autorovy texty.

**Co se naopak vyplatí vzít:** odpovědi v diskusích. Bývá jich násobně víc než vlastních příspěvků a nesou hlas v nejsyrovější podobě – jak autor reaguje, když nepíše „text“.

**Jiné sítě než tyhle čtyři** (Mastodon, Threads, Instagram) skript nemají. Postup je pořád stejný: vyžádat oficiální export, najít v něm soubor s vlastními příspěvky, převést do téhož tvaru ročníkových souborů. Vzniklý převodník patří do `scripts/`.

## Weby, které ještě běží

**Napřed zjisti, jestli web běží na WordPressu** – většina blogů a magazínů ano a pak je to otázka jednoho volání.

1. **WordPress REST API:** `https://<doména>/wp-json/wp/v2/posts?per_page=100&status=publish`. Vrací titulek, datum, URL i celý HTML obsah. Cizí web se filtruje autorem: `&author=<ID>`.
2. **ID autora**, když je endpoint `users` zablokovaný: oklikou přes známý článek – `posts?slug=<slug>` vrátí v odpovědi `author`.
3. **HTML na Markdown** přes `markdownify`. Relativní odkazy převeď na absolutní, jinak po přesunu ukazují nikam.
4. **Je-li API zablokované** (bezpečnostní plugin vrací 401), zbývá scraping: obsah bývá v `.entry-content`, datum v meta `article:published_time`, titulek v `<h1>`.

**Úplnost ověř proti datům, ne proti výpisu na webu.** Hlavička `X-WP-Total` říká, kolik textů dotaz opravdu má; `post-sitemap.xml` odhalí i to, co ve výpisu autora nefiguruje. Autorské výpisy bývají stránkované nebo donačítané JavaScriptem a **poslední stránka tiše chybí**.

## Weby, které zanikly

Zaniklý web bývá v archivu ta nejcennější vrstva – jsou v něm rané texty, které jinde nejsou. Zdroje podle toho, co po něm zbylo:

| Co zbylo | Jak z toho ven |
|---|---|
| Export WordPressu (WXR, `.xml`) | items podle `dc:creator`, `post_type=post`, `status=publish` |
| Záloha All-in-One WP Migration (`.wpress`) | `scripts/extract_wpress.py`; uvnitř je i databáze na ověření autorů |
| SQL dump databáze | `wp_posts` spojené přes `wp_users`; pozor na neveřejné statusy |
| Uložené stránky z prohlížeče | původní URL bývá v komentáři `saved from url=(…)` na začátku souboru |

**Web.archive.org je možnost, ne samozřejmost.** U některých archivů je to vědomě zamítnutá cesta. Zeptej se, než po něm sáhneš, a odpověď zapiš do konvencí archivu – jinak ji bude příští běh řešit znovu.

## Tištěná média a ostatní

- **`.docx` a `.pdf`** převeď přes `pandoc -t markdown`.
- **Chybí-li přesný den vydání** (typicky u měsíčníků), použij v názvu souboru první den měsíce a do metadat napiš, že přesné datum není známé. Domýšlet se nemá nic.
- **Netextové formáty do archivu nepatří.** Video ani podcast bez textové podoby není doklad o psaní.

## Pasti, které stály čas

Každá z nich už jednou vyrobila tichou chybu, která se poznala až o kus dál:

- **Facebook kóduje UTF-8 jako latin-1 escapy.** Bez opravy (`s.encode("latin-1").decode("utf-8")`) je celý export rozsypaný na mojibake. Rozpozná se to na první diakritice.
- **LinkedIn escapuje uvozovky zpětným lomítkem** (`escapechar="\\"`) a víceřádková pole balí do uvozovek řádek po řádku. Bez očištění zůstanou uvozovky uprostřed textu.
- **První stažení z LinkedInu bývá prázdné.** „Basic“ archiv příspěvky neobsahuje – čeká se na druhý, kompletní, a na mail o jeho připravení.
- **Vlastníka účtu nikdy nečti z prvního výskytu.** Exporty jsou plné cizích identifikátorů z odpovědí a sledovaných účtů. Ber ho z místa, které ho autoritativně definuje – `account.js` u X, commit blok u AT Protocol, `wp_users` u WordPressu – a ověř druhým signálem.
- **Názvy souborů na macOS jsou v NFD.** Před porovnáváním normalizuj na NFC, jinak se dva shodné názvy neshodnou.
- **Export WordPressu nerozhoduje o místě první publikace.** Import zachovává datum postu i komentářů, takže přenesený text vypadá jako původní. Datum ověřuj podle komentářů: přijdou-li první v řádu hodin, sedí; přijdou-li o měsíce později, je to přetisk.
- **Duplicitní titulky napříč médii** jsou nejlevnější způsob, jak přetisky najít. Projeď je před uzavřením sběru.
