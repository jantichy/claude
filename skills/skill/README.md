# /skill – skilly, které se samy udržují

Zakládá nové vlastní skilly, vytěží skill z rozdělané konverzace, prožene ty existující revizí proti dnešní podobě normy a umí je i zrušit včetně všech stop. Revize je ten důvod, proč vznikl: norma se posouvá dál, ale hotové skilly zůstanou stát a samy o tom neřeknou. Vedle toho klade otázku, kterou nepoloží nikdo jiný – *nevzniklo mezitím něco, co tenhle skill dělá ručně?*

## Co umí

1. **`/skill create`** (výchozí) – **založení nového skillu.** Doptá se na zadání, ověří inventurou, jestli by to neuměl už někdo jiný, změří, jak si agent bez skillu poradí, sepíše ho a napojí na okolí.
2. **`/skill extract`** – **vytěžení konverzace.** Vstupem není zadání, ale to, co se v sezení vyladilo. Umí si přitom načíst i tu část rozhovoru, kterou už z paměti vytlačila kompaktace.
3. **`/skill update [jméno]`** – **dorovnání na dnešní normu.** Jeden skill, nebo bez jména všechny.
4. **`/skill delete <jméno>`** – **odstranění i se stopami** ze všech míst, kde skill zanechal zmínku: z přehledu, z životního cyklu, z testů, z odkazů jiných skillů, z nastavení i z instrukcí jednotlivých projektů.
5. **Zastaví se, když by skill vůbec neměl vzniknout.** Co chytne test, linter nebo automatická brána, se má řešit tam. Co platí pro každou práci, patří mezi obecná pravidla. Co je znalost oboru, patří do doménového souboru.
6. **Tři vrstvy ověření** – tvar, spolehlivost vyvolání a dodržení pravidla pod tlakem. Co ověřit nešlo, se vypíše jako nezkontrolované.

## Proč zrovna tenhle

- **Revize je opakovatelná.** Konfigurace se vyvíjí dál a starší skilly v ní zůstanou stát; tohle je způsob, jak je dorovnat jedním zavoláním.
- **Ptá se na možnosti, které dřív neexistovaly.** Přibyl mezitím nástroj, který by nahradil kus postupu ručně napsaného ve skillu? Tenhle druh zastarávání jinak nikdo neměří.
- **Nezaloží alias.** Zbylo-li po odečtení všeho, co umí někdo jiný, prázdno, řekne to rovnou – a ušetří vám skill, který nic nepřidává.
- **Změří, jak agent selže bez skillu**, a píše proti tomu, ne proti představě. Konkrétní výmluvy, kterými si agent zvolí jinou cestu, jsou pak přesně ta místa, kde má být pravidlo formulované tvrději.
- **Cizí nástroje nerozhodují o tvaru.** Skill si od nich bere měření a vytěžení, ale podobu výsledku si drží sám – jinak by si každý nástroj prosadil svou vlastní.
- **Revize nic nepřepíše bez zeptání.** Co je mechanické, opraví a vypíše; co maže nebo přepisuje obsah, předloží.
- **Přes všechny skilly nepředkládá nález po nálezu.** Padesát otázek se neodklikává, jen odsouhlasí naslepo – tak ukáže vzorec, počet a tři příklady.
- **Zrušení je opravdu zrušení.** Skill se buď používá, nebo neexistuje; vypnutý skill dál nabízí funkci, kterou nikdo nemá zapnout. Po smazání běží kontrolní průchod na jeho jméno, který musí vrátit nulu.

## Jak se to používá

```
/skill                    # založení nového
/skill extract            # vytěžení z probíhající konverzace
/skill update             # revize všech skillů proti normě
/skill delete autoprompt  # zrušení i se stopami
```

## Ukázka výstupu

```
## Skill hotový

**Soubor:** skills/transcript/SKILL.md – 450 řádků
**Delegace:** whisper.cpp, dataviz

**Ověřeno**
- Tvar: python3 -m unittest discover -s tests → OK
- Vyvolání: 9/10 zásahů, 0 falešných
- Tlakové scénáře: neměřeno – skill nic nezakazuje

**Okolí**
- README.md · RULES.md · tests/ – dorovnáno
```

## Co nedělá

- **Nedefinuje tvar skillu.** Ten drží samostatná norma; skill ji čte, neopisuje a nerozšiřuje.
- **Neaudituje konfiguraci.** Rozpory mezi soubory a mrtvé zbytky řeší `/consistency`.
- **Neprověřuje kvalitu práce skillu za běhu.** Měří, jestli se **vyvolá** a jestli se pod tlakem **dodrží**.
- **Nesahá na cizí skilly.** Ty z pluginů se používají, ne udržují.

## Jak si ho nainstalovat

Nechte to na Claudovi. Otevřete si Claude Code a napište mu:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/skill a nainstaluj mi ten skill k sobě do `~/.claude/skills/`. Vezmi k němu i soubor `skills/SKILLS.md`, na kterém stojí.

**Norma tvaru v `SKILLS.md` je povinná součást** – bez ní nemá skill proti čemu revidovat. Volitelně navíc: nástroj `skill-creator` od Anthropicu (bez něj odpadne vytěžení konverzace a celá měřicí část – skill si na to sám posvítí a řekne, co se tím neověřilo) a plugin [superpowers](https://github.com/obra/superpowers) kvůli tlakovým scénářům.

---

### Požadavky a omezení

Skill spravuje **vlastní skilly v jednom konkrétním umístění**; není to obecný nástroj na skilly kdekoliv. Předpokládá, že u sebe máte normu tvaru a testy nad konfigurací – obojí je v tomhle repozitáři. Měřicí část potřebuje Python.
