# /autopilot – Claude odpracuje z úkolů všechno, k čemu vás nepotřebuje

V seznamu úkolů projektu se vždycky nasbírá směs: něco čeká na vaše rozhodnutí, něco potřebuje přístup nebo text, který máte jen vy, a hodně věcí jde prostě udělat. Tenhle skill si z toho vybere jen to poslední a odpracuje to beze vás – úkol po úkolu, každý celý až po commit, bez jediné otázky. Kde narazí na rozhodnutí, nic neodhaduje: otázku vám zapíše k úkolu a jede dál. Hodí se na chvíle, kdy od počítače odcházíte a chcete, aby se mezitím odvedla práce, která na vás nečeká.

## Co umí

- **Vybere jen úkoly, které nepotřebují vás** – žádné rozhodování mezi variantami, žádné přístupy, údaje ani text vaším hlasem, nic nevratného nebo mířícího ven, žádná změna pravidel. Při pochybnosti úkol přeskočí.
- **Každý úkol dotáhne celý:** udělá ho, pustí kontroly projektu, přesune ho mezi hotové, commitne a pushne.
- **Neptá se.** Všechno, co by potřeboval vědět, si vyjasní při spuštění, pak už jede sám.
- **Zaseknutý úkol vrátí** a k úkolu zapíše otázku i s variantami a doporučením, takže pak všechny otázky najdete na jednom místě.
- **Hlídá si délku session.** Když se kontext naplní, dokončí rozdělaný úkol, další nezačne a řekne vám, jak pokračovat v nové session.
- **Dá se zúžit** na úkoly s určitým slovem.

## Proč zrovna tenhle

- **Místo dlouhého promptu jeden příkaz** – a pokaždé se stejnými pravidly, ne podle toho, jak ho zrovna napíšete.
- **Nerozhoduje za vás potichu.** Drobná výjimka z pravidla, kterou by si jinak odsouhlasil sám, u něj skončí jako otázka.
- **Ví, kdy přestat.** Obecný prompt jede, dokud nedojde fronta nebo kontext; tenhle skončí na hranici úkolu, kdy je všechno zapsané a commitnuté.
- **Nic se neztratí ani při přerušení** – otázky, hotová práce i zbytek fronty jsou v souborech projektu, ne jen v konverzaci.

## Jak se to používá

```
/autopilot
/autopilot dokumentace
```

Na začátku vypíše, co odpracuje a co přeskočí a proč, a hned se do toho pustí. Na konci shrne, co je hotové a co čeká na vás.

## Co nedělá

- Nevybírá z úkolů za vás tam, kde je z čeho vybírat – k tomu je `/next`.
- Neodpracovává implementační plán; na ten je `/implement`.
- Nenavazuje na přerušenou práci; to dělá `/continue`.
- Nedělá revizi vlastní práce – tu doporučí pustit v nové session.

## Jak si ho nainstalovat

Je to snadné, zadejte do svého Claude Code tenhle prompt:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/autopilot a nainstaluj mi ten skill k sobě do `~/.claude/skills/` – celý adresář i s podadresáři. Stáhni k němu z téhož repozitáře na odpovídající místo pod `~/.claude/` i sdílené soubory ze `skills/` a `standards/`, na které jeho soubory odkazují, a definice typů subagentů, které pouští, z `agents/` do `~/.claude/agents/`. Co už u sebe mám, nepřepisuj a ukaž mi rozdíl. Odkazuje-li na jiný skill, zeptej se mě, jestli ho chci taky. Odkazy na soubory, které v repozitáři nejsou, mi vypiš a u každého se zeptej, jestli ho napojit na můj vlastní soubor, nebo odkaz smazat. Stáhni i hook `hooks/handoff.py` do `~/.claude/hooks/`, ze kterého skill bere měření délky session, a skill `next`, jehož skript čte seznam úkolů. Nakonec mi řekni, co musím doplnit sám.

---

### Požadavky a omezení

- Claude Code a Python 3.
- Projekt v gitu se seznamem úkolů v `docs/todo.md`.
- Commituje po každém úkolu i v projektu, kde automatické commity zapnuté nejsou – spuštěním skillu se o tom rozhoduje.
- Kompaktaci nepoužívá: po naplnění kontextu skončí a pokračuje se novou session. Spustit ji automaticky znovu sám neumí.
