# /compose – texty, které znějí jako vy, ne jako AI

Napíše článek, příspěvek na sociální sítě nebo vlákno vaším hlasem a stylem. Ne obecnou češtinou, kterou dnes pozná každý, ale tak, jak píšete vy – včetně obratů, které používáte, stavby vět i toho, čemu se naopak vyhýbáte. Neumí to sám od sebe: opírá se o znalostní bázi vašeho psaní, a tu s vámi umí od nuly postavit – posbírat všechno, co jste kdy napsali, a vydestilovat z toho popis vašeho hlasu. **Vaše názory a pointy si přitom nikdy nevymýšlí**, ty musíte dodat sami.

## Co umí

- **Napíše text ve třech formátech** – článek, příspěvek na sítě, vlákno. Každý má vlastní profil, protože se liší stavbou i tempem, ne jen délkou.
- **Posbírá archiv vašich textů** (`/compose collect`) – provede vás vyžádáním exportů z Facebooku, LinkedInu, X a Bluesky, stažením článků z webů, na které jste psali, i vytěžením záloh po webech, které už neexistují. Exporty převede do jednotné podoby sám.
- **Vydestiluje z archivu popis vašeho hlasu** (`/compose profile`) – slovník, rytmus, myšlenkové postupy, rozdíly mezi tím, jak píšete odborně a jak osobně, a hlavně seznam obratů, které do vašich textů nepatří.
- **Umí se doučit.** Když přibudou nové texty nebo nový postřeh, `/compose profile` je zapracuje do hotové báze, místo aby ji stavěl znovu.
- **Ověří sám sebe slepým testem.** Napíše tři zkušební texty a ptá se u každého „zní, nebo nezní jako vy" – a z každé výhrady udělá opravu v bázi.
- **Doptá se na to, co si nemá vymýšlet** – téma, publikum, kanál a hlavně váš postoj a pointu.
- **Vezme si za vzor konkrétní starší texty**, ne jen abstraktní popis stylu.
- **Zvládne vstup v jakékoli fázi** – od holého tématu přes osnovu až po hrubý draft k přepsání.
- **Hlídá horní mez.** Charakteristický obrat smí v textu být nanejvýš jednou; víc už je parodie na vlastní styl.

## Proč zrovna tenhle

- **Styl je popsaný i doložený.** Vedle pravidel dostane model skutečné texty, takže nenapodobuje popis stylu, ale styl sám.
- **Každé tvrzení o vašem psaní má doklad** – konkrétní text a doslovný úryvek. Bez toho vzniká věrohodně znějící popis „dobrého psaní", který ale není váš.
- **Zákaz vymýšlení názorů je tvrdý.** Text může znít jako vy jen tehdy, když v něm nestojí nic, co jste si nemysleli.
- **Ví, čemu se vyhnout.** Báze drží i seznam obratů, které text okamžitě prozradí jako strojový.
- **Počítá s tím, že se hlas vyvíjí.** Normou jsou poslední roky, starší vrstvy slouží jako doklad vývoje – ne jako průměr dvaceti let, kterým jste nikdy nepsali.
- **Nezastaví se u prvního draftu.** Připomínku, která platí obecně, nabídne promítnout zpátky do báze, aby se táž oprava nedělala podruhé.

## Jak se to používá

```
/compose collect     # jednou na začátku: posbírá všechny vaše dosavadní texty
/compose profile     # vydestiluje z nich bázi – a později ji aktualizuje
/compose             # píše text
```

Napoprvé jděte po řadě. Sbírání archivu je běh na několik dní, protože exporty ze sociálních sítí se připravují klidně dva dny – skill si o ně řekne hned na začátku a mezitím stahuje zbytek.

## Ukázka výstupu

Co po prvních dvou bězích zůstane na disku:

```
archiv/                      korpus – co bylo napsáno
  jantichy.cz/               YYYYMMDD - Titulek.md
  digichef.cz/
  facebook/                  Facebook 2024.md, Facebook 2025.md …
  twitter/  linkedin/  bluesky/

báze/                        norma – jak se píše
  style.md                   slovník, rytmus, myšlenkové postupy, anti-patterny
  article.md  post.md  thread.md          profily formátů
  article-examples.md  post-examples.md   zlatý fond ukázek
  _analysis/                 podklady a záznam, kdy se profilovalo a z čeho
```

Archiv se nikdy nepřepisuje, jen doplňuje. Báze naopak ano – opravuje se pokaždé, když ji nový text nebo vaše výhrada vyvrátí.

## Co nedělá

- **Nevymýšlí obsah ani stanoviska.** Bez vašeho vstupu k tématu se nerozjede.
- **Nepřepisuje nahrávky.** Na mluvené slovo je `/transcript`.
- **Nedělá korekturu cizích textů.** Uplatňuje styl při psaní, není to redakční služba.
- **Nepublikuje.** Výstupem je text, ne příspěvek někde venku.

## Jak si ho nainstalovat

Nechte to na Claudovi. Otevřete si Claude Code a napište mu:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/compose
> a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.

Ať vezme i podadresář `scripts/` – bez něj se exporty ze sociálních sítí nemají čím převést. Znalostní bázi v repozitáři nenajdete, ta je u každého vlastní a soukromá; postaví se prvním během `/compose collect` a `/compose profile`. Cestu k ní i k archivu si skill zapíše do vašeho `~/.claude/CLAUDE.md`, aby ji příště našel sám.

---

### Požadavky a omezení

Python 3 na převod exportů (u Bluesky navíc balíček `cbor2`). Účty, ze kterých chcete texty vytáhnout, musíte mít po ruce – exporty se stahují ze svého profilu a připravují se hodiny až dva dny. Archiv i báze zabírají jednotky až desítky MB textu; syrové exporty ze sítí mívají stovky MB až gigabajty a do repozitáře nepatří. Vlastní psaní počítá s tím, že texty jsou česky.
