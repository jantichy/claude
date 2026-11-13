# /proofread – korektura, po které je text lepší, ne jen bez chyb

Projde hotový text – článek, dokumentaci, mail, post – a udělá z něj lepší text: opraví pravopis, gramatiku a typografii, ale hlavně se podívá na stavbu, pořadí, ve kterém se text rozvíjí, na věty a styl. Umí češtinu i angličtinu; u angličtiny psané Čechem hledá místa, která by rodilý mluvčí řekl jinak. Hodí se každému, kdo píše do světa a nemá po ruce redaktora – a nechce, aby mu redaktor přepsal hlas.

## Co umí

- **Opraví, co má jedinou správnou podobu** – překlepy, čárky, uvozovky, pomlčky, mezery u čísel – rovnou a bez ptaní. Předtím ale ověří, že nejde o záměr, třeba o ukázku chybného slova nebo o citaci.
- **Navrhne menší stylistické úpravy** – vatu, úřední obraty, kalky z angličtiny, převlečená slovesa – a nechá je schválit naráz: „vše“, nebo „vše kromě 3 a 7“.
- **Větší přepisy předloží po jednom** – přesunutí pointy nahoru, přestavbu odstavce, škrt – vždycky s variantami a s možností nechat to, jak to je.
- **U angličtiny hledá czenglish** – falešné přátele, české předložky, chybějící členy, slovosled a věty, které vznikly překladem v hlavě –, a drží americkou angličtinu i americkou sazbu.
- **Nechá text přečíst odborníkem na téma**, který hledá věcné chyby – zastaralý údaj, chybně popsaný nástroj, číslo, které nesedí – a ověří je u zdroje. Nic z toho neopraví, jen se zeptá.
- **Pozná, čí a pro koho text je.** U vlastního textu autora nehlásí jako vadu to, co je pro jeho styl typické, a v odborném textu neopravuje oborový slovník – termín nebo anglicismus, který je v oboru běžný, nechá být.
- **Bere text odkudkoliv** – soubor, Google Doc (do něj i zapíše, co se schválilo), webovou stránku, nebo text vložený do konverzace.
- **Do dokumentu Wordu píše revize.** Opravy a menší úpravy vloží jako sledované změny, větší přepisy, věcné pochybnosti a otázky jako komentáře u textu – o všem pak rozhodnete ve Wordu, bez otázek v konverzaci.

## Proč zrovna tenhle

- **Fakta se nemění.** Před korekturou si sepíše čísla, jména, citace a tvrzení a po ní ověří, že všechny zůstaly a znamenají totéž.
- **Hlas autora je hodnota, ne chyba.** Co může být záměr, se jen navrhne – nic většího než oprava překlepu se nezapíše bez souhlasu, ani když spěcháte.
- **Pravidla jsou vaše, ne obecný vkus modelu.** Skill sám žádné nenese: čte je z vaší vlastní znalostní báze o psaní, takže se dají doplnit a opravit na jednom místě.
- **Každý návrh má zdůvodnění** – pravidlo, o které se opírá, a co je na původním znění špatně.
- **Návrhy prochází nezávislá kontrola**, která je zkouší vyvrátit – hlavně jako možný záměr autora. Co neobstojí, ani neuvidíte.
- **Po zápisu text přečte znovu** a hledá vady, které zanesla sama korektura – třeba údaj, který po přestavbě zůstal dvakrát.

## Jak se to používá

```
/proofread clanek.md
/proofread https://docs.google.com/document/d/…
```

Nebo prostě „udělej korekturu tohohle textu“ a vložit ho. Skill řekne, jaký jazyk, druh textu a hlas rozpoznal, opraví jednoznačné, zeptá se na větší přepisy, předloží dávku menších úprav a nakonec shrne, co změnil.

## Co nedělá

- **Nepíše nový text.** Na psaní vlastním hlasem je `/compose`.
- **Fakta neopravuje.** Věcně podezřelé tvrzení i rozpor dvou údajů jen nahlásí jako otázku; argumentaci a strategii neposuzuje, na to je `/oponent`.
- **Nezveřejňuje.** Text opraví tam, kde leží, nebo ho vrátí.

## Jak si ho nainstalovat

Je to snadné, zadejte do svého Claude Code tenhle prompt:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/proofread a nainstaluj mi ten skill k sobě do `~/.claude/skills/` – celý adresář i s podadresáři. Stáhni k němu z téhož repozitáře na odpovídající místo pod `~/.claude/` i sdílené soubory ze `skills/` a `standards/`, na které jeho soubory odkazují, a definice typů subagentů, které pouští, z `agents/` do `~/.claude/agents/`. Co už u sebe mám, nepřepisuj a ukaž mi rozdíl. Odkazuje-li na jiný skill, zeptej se mě, jestli ho chci taky. Odkazy na soubory, které v repozitáři nejsou, mi vypiš a u každého se zeptej, jestli ho napojit na můj vlastní soubor, nebo odkaz smazat. Skill čte pravidla psaní ze souborů v `~/Context/Text/`, které v repozitáři nejsou – zeptej se mě, jestli mám vlastní pravidla, na která ho napojit, nebo jestli mi mám založit kostru s výchozí češtinou a podadresářem pro angličtinu. Nakonec mi řekni, co musím doplnit sám.

Pravidla psaní v repozitáři nenajdete – leží v soukromé znalostní bázi. Bez nich skill nemá podle čeho opravovat a nerozjede se.

---

### Požadavky a omezení

Claude Code; pro Google Doc připojený konektor Google Docs, pro dokument Wordu (`.docx`) skill `docx` z oficiálního balíčku document-skills. Jazyky jsou ty, pro které máte pravidla – dnes čeština a angličtina. Text z webu prochází převodem, takže drobnosti sazby u něj nemusí sedět s originálem.
