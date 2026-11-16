# /package – skill, který se dá dát do ruky komukoliv

Vezme vlastní skill, víc skillů nebo kus znalostní báze a udělá z nich jeden samostatný balíček – adresář nebo zip, který pošlete mailem nebo dáte na flashku. Příjemce řekne svému Claudovi „udělej, co je v INSTALL.md“ a ten si balíček nainstaluje. Hodí se, když chcete svůj skill dát kolegovi nebo někomu doma a on nemá vaši strukturu souborů, vaše sdílená pravidla ani přístup k vašim soukromým poznámkám.

## Co umí

- **Zabalí cokoliv zadaného** – jeden skill, několik skillů naráz, znalostní bázi bez skillu, nebo jejich kombinaci. Co mají společné, dá do balíčku jen jednou.
- **Dohledá všechno, na co soubory odkazují**, a rozhodne, co s tím: soubor, který skill čte celý, přibalí; ze sdíleného souboru, ze kterého potřebuje jednu větu, ji vepíše přímo do skillu; odkaz na něco, co příjemce mít nebude, smaže tak, aby věta dávala smysl.
- **Odstraní, co je vaše** – cesty z vašeho disku, vaše jméno, odkazy na váš vlastní styl psaní. Co je sporné, třeba osobní preference zapsaná v pravidle nebo jméno klienta v příkladu, předloží ke schválení.
- **Nic nenechá napevno.** Odkazy mezi soubory jsou relativní, takže si příjemce zvolí, kam co uložit, a balíček funguje.
- **Napíše návod pro Clauda příjemce** – co v balíčku je, na co se má zeptat, kam co uložit, a jak doinstalovat programy, které skill potřebuje, pro Windows, macOS i Linux.
- **Na konci ho přečte cizíma očima** a hledá, co by u příjemce nefungovalo.

## Proč zrovna tenhle

- **Balíček je opravdu samostatný.** Instalace z GitHubu stáhne jen to, co je veřejné; soukromá pravidla, o která se skill opírá, chybí a skill se u příjemce nerozjede. Balíček je nese s sebou.
- **Vaše cesty a jména neodejdou.** Hlídá to strojová kontrola, ne oko – absolutní cesta nebo jméno v kterémkoliv souboru balíček zastaví.
- **Příjemce nemusí nic upravovat.** Přizpůsobení je hotové předem; Claude příjemce rozhoduje jen o tom, kam co dá.
- **Funguje na jakémkoliv počítači.** Návod nepočítá s vaší platformou ani s vaším nastavením.

## Jak se to používá

```
/package proofread
/package proofread compose Text
```

Skill se zeptá, jestli chcete adresář, nebo zip, ukáže, co přibalí, co vepíše a co odstraní, nechá schválit sporné věci a balíček uloží do `~/Downloads`.

## Co nedělá

- **Nemění originál.** Všechny úpravy dělá na kopii.
- **Neposílá.** Balíček obsahuje kopii vaší soukromé znalosti; komu ho dáte, je na vás.
- **Nepřibaluje programy.** Co se instaluje mimo Clauda, popíše návod, ale v balíčku to není.

## Jak si ho nainstalovat

Je to snadné, zadejte do svého Claude Code tenhle prompt:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/package a nainstaluj mi ten skill k sobě do `~/.claude/skills/` – celý adresář i s podadresáři. Stáhni k němu z téhož repozitáře na odpovídající místo pod `~/.claude/` i sdílené soubory ze `skills/` a `standards/`, na které jeho soubory odkazují, a definice typů subagentů, které pouští, z `agents/` do `~/.claude/agents/`. Co už u sebe mám, nepřepisuj a ukaž mi rozdíl. Odkazuje-li na jiný skill, zeptej se mě, jestli ho chci taky. Odkazy na soubory, které v repozitáři nejsou, mi vypiš a u každého se zeptej, jestli ho napojit na můj vlastní soubor, nebo odkaz smazat. Skill rozlišuje osobní obsah podle mé struktury znalostí – zeptej se mě, kde mám soukromé poznámky, svůj styl psaní a podklady o klientech, a cesty, které skill jmenuje, na ně napoj. Nakonec mi řekni, co musím doplnit sám.

Skill počítá se znalostní bází v samostatné složce vedle `~/.claude`; bez ní zabalí jen skilly.

---

### Požadavky a omezení

Claude Code a Python 3 (skript na hledání odkazů používá jen standardní knihovnu). Balí textové soubory – skilly, pravidla, šablony, skripty –, ne binárky ani nainstalované programy. Zip se vytváří modulem Pythonu, takže nepotřebuje žádný další program.
