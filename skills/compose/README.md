# /compose – texty, které znějí jako já, ne jako AI

Napíše článek, příspěvek na sociální sítě nebo vlákno mým hlasem a mým stylem. Ne obecnou generickou češtinou, kterou dnes pozná každý, ale tak, jak píšu já – včetně ustálených obratů, stavby vět a toho, čemu se naopak vyhýbám. Tahá to ze znalostní báze mého psaní a k tématu si navíc dohledá pár nejpodobnějších starších textů, které použije jako živý vzor. **Moje názory a pointy si přitom nikdy nevymýšlí** – ty musím dodat sám.

## Co umí

- **Tři formáty** – článek, příspěvek na sociální sítě, vlákno. Každý má vlastní profil, protože se liší stavbou i tempem, ne jen délkou.
- **Doptá se na to, co si nemá vymýšlet** – téma, publikum, kanál a hlavně můj postoj a pointu. Když ho nezná, ptá se, místo aby ho odhadl.
- **Vezme si za vzor konkrétní starší texty**, ne jen abstraktní popis stylu.
- **Zvládne vstup v jakékoli fázi** – od holého tématu přes osnovu až po hrubý draft k přepsání.
- **Vlastní kontrola před odevzdáním** – jestli text vykládá od A do B, jestli jsou předjatí šťouralové, jestli je srozumitelný pro dané publikum a jestli neklouže do obratů, které v mém stylu nemají co dělat.
- **Hlídá i horní mez.** Charakteristické obraty smí v textu být nanejvýš jednou; víc už je parodie na vlastní styl.
- **Připomínky obecné platnosti navrhne promítnout zpátky** do znalostní báze, aby se táž oprava nemusela dělat podruhé.

## Proč zrovna tenhle

- **Styl je popsaný i doložený.** Vedle pravidel dostane model skutečné texty, takže nenapodobuje popis stylu, ale styl sám.
- **Zákaz vymýšlení názorů je tvrdý.** Text může znít jako já jen tehdy, když v něm nestojí nic, co jsem si nemyslel.
- **Ví, čemu se vyhnout.** Znalostní báze drží i seznam obratů, které text okamžitě prozradí jako strojový.
- **Nezastaví se u prvního draftu** – počítá s iterací a s tím, že se z připomínek učí i báze samotná.

## Jak se to používá

```
/compose
```

Skill se doptá na formát, téma, publikum a moje pointy, načte si styl a vzory a předloží draft k připomínkám.

## Co nedělá

- **Nevymýšlí obsah ani stanoviska.** Bez mého vstupu k tématu se nerozjede.
- **Nepublikuje.** Výstupem je text, ne příspěvek někde venku.
- **Nezná můj styl automaticky** – potřebuje znalostní bázi, viz níž.

## Jak si ho nainstalovat

Nechte to na Claudovi. Otevřete si Claude Code a napište mu:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/compose a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.

Tím to ale nekončí: **sám o sobě skill nic neumí**, je to jen rámec nad znalostní bází. Aby psal vaším hlasem a ne mým, musíte si postavit vlastní – popis svého stylu, profil každého formátu, ukázky a archiv vlastních textů. Claudovi řekněte, ať vám s jejím založením pomůže; skill pak sáhne po ní.

---

### Požadavky a omezení

Vlastní znalostní báze psaní v samostatném adresáři (ten můj je soukromý a v tomhle repozitáři není). Bez ní je skill prázdný obal.
