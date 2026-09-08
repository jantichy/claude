# /transcript – nahrávky na přepis a chytré shrnutí

Ze zvukových i obrazových nahrávek udělá pořádek: přepíše je do čitelného textu, rozliší mluvčí a napíše strukturované shrnutí se soupisem domluv a úkolů na konci. **Přepis běží kompletně na vašem počítači a offline** – nahrávka nikam neodchází. Než začne, projde s vámi krátkého průvodce a podstrčí rozpoznávači jména a názvy, které v nahrávce padnou, takže pak nekomolí lidi ani firmy.

## Co umí

1. **Přepis do čitelného textu** – ne syrový výstup rozpoznávače, ale vyčištěný text: bez „ehm“, bez zamotaných formulací, rozdělený do kapitol s nadpisy a odstavců, s vyznačenými pojmy.
2. **Strukturované shrnutí** celé nahrávky – uspořádané logicky, ne chronologicky, a **na konci soupis domluv, úkolů a dalších kroků**.
3. **Rozlišení mluvčích** – kdo kdy mluví. Skill se pak zeptá, kdo je kdo, a jména propíše i do úkolů ve shrnutí, takže místo „dodat seznam“ stojí „**Tomáš** dodá seznam“.
4. **Titulky s časovými značkami**, na dohledání místa v nahrávce – volitelně i ve variantě, která nese jméno mluvčího.
5. **Zvládne zvuk i video.** Záznam hovoru se dnes stahuje jako video, tak se z něj prostě vytáhne zvuk – není to výjimka, ale běžný případ.
6. **Pozná jazyk sám** a všechno – přepis, opravy pravopisu i shrnutí – udělá v něm. Anglicky mluvená schůzka nemá české shrnutí.
7. **Zvládne víc nahrávek naráz** a napíše k nim jedno společné shrnutí.
8. **Vyberete si, co má vzniknout** – přepis, shrnutí, titulky, rozlišení mluvčích, nebo jen některé z toho.
9. **A jak přesně to má rozpoznávat** – rychlejší varianta stačí na běžnou mluvu, přesnější se hodí na špatný zvuk a překřikování. U obou vám dopředu řekne, jak dlouho to potrvá, ať se rozhodujete podle čísla, ne podle pocitu.

## Proč zrovna tenhle

- **Nahrávka neopustí počítač.** Žádná cloudová služba, žádné nahrávání citlivé schůzky někam ven.
- **Připraví si seznam relevantních jmen, značek a odborných termínů a předá ho rozpoznávači předem** – ten je pak zapíše správně už při poslechu. Opravovat je dodatečně je principiálně slabší: vymyšlená oprava vypadá stejně věrohodně jako správná. Návrhy si přitom vytáhne z toho, co jste napsali, z projektu, ve kterém stojíte, i z předchozí konverzace, a nechá si je odsouhlasit.
- **Rešerši dělá naplno, ale rozpoznávači předává výběr.** Ten má tvrdý strop na to, kolik toho unese, a při překročení tiše zahodí začátek – takže se zůstává bezpečně pod ním. Zbytek slovníku se použije při čištění, kde naopak platí, čím víc kontextu, tím líp.
- **Ví, kde jsou meze slovníku, a přiznává je.** Že seznam jmen zabere, není samozřejmost – změřeno na sedmi bězích nad touž nahrávkou, a proto skill říká, že u důležitých jmen se výsledek má zkontrolovat.
- **Odstraní halucinace rozpoznávače** – opakující se nesmyslné řádky i vsunuté věty typu „Titulky vytvořil…“.
- **Titulky se dají číst.** Nezalomí se uprostřed slova a nemají délku odstavce – nejdelší vyjde na necelou stovku znaků místo půltisíce. Text je přitom slovo za slovem tentýž, mění se jen zalomení; kratší úseky navíc zpřesňují, komu se replika přiřadí.
- **Opraví přeslechy podle tématu**, ale **neopravuje to, čemu jen nerozumí**: co model dává opakovaně a konzistentně, je nejspíš váš interní žargon, ne chyba. Na konec pak vypíše seznam termínů, které nechal být, ať víte, co ověřit.
- **Opraví pravopis, ale nechá vaši mluvu být.** Čárky, shodu a velká písmena spraví, protože to zapsal špatně stroj – ale „bysme“ a „vokno“ zůstanou, protože tak lidé mluví.
- **České jméno v anglické nahrávce vrátí do českého tvaru** i s diakritikou, přestože přepsané slovo v angličtině zdánlivě dává smysl.
- **Nikdy nehádá, kdo mluvil.** Replika, kterou nelze spolehlivě přiřadit, zůstane bez jména – špatné přiřazení se totiž propíše až do úkolů, kde je z něj tvrzení, kdo co slíbil.
- **Odhad času umí a učí se.** Řekne dopředu, jak dlouho to potrvá, a po každém běhu si tempo srovná podle vašeho počítače. Nezapočítává přitom běhy, které selhaly, ani krátké vzorky, které by odhad zkreslily.
- **Zkontroluje, kolik zvuku se vlastně přepsalo**, a když vyjde podezřele málo, řekne to a nabídne, co s tím – nerozhoduje o tom sám.
- **Umí nahrávku dopřepsat, i když se rozpoznávač uprostřed zakousne.** Na vyžádání ji zpracuje po úsecích: problémový kus přeskočí a o zbytek nepřijdete. Totéž je záchrana, kdyby se přece jen objevila smyčka opakujícího se nesmyslu.
- **Pozná dvojjazyčnou nahrávku** a zeptá se, jak s ní naložit, místo aby polovinu tiše zkomolila.
- **Doinstaluje si chybějící součásti** – ale rozlišení mluvčích nikdy samo od sebe, protože to po vás chce účet i souhlas s licencí, a to za vás nikdo neudělá.
- **Uklidí po sobě** všechny mezivýsledky a nechá jen to, co jste si vybrali.

## Jak se to používá

```
/transcript ~/Desktop/schuzka.m4a Přepiš mi schůzku s Janou Novákovou nad nastavením intranetu
```

Volný popis není dekorace – právě z něj se sestaví seznam jmen a názvů, takže **čím konkrétnější popis, tím míň zkomolených jmen.** Skill se pak zeptá na model, na slovník a na to, co má vzniknout, a jde na to.

## Ukázka výstupu

```markdown
## Životní cyklus člena

**Tomáš:** Jde o to, že když někdo přijde do prvního patra, tak je to jasné.

**Jana:** A potom to krystalizuje podle toho, jak vypadají prostory.
```

A na konci shrnutí:

```markdown
## Domluvy a úkoly

- **Tomáš** dodá seznam prostor do konce týdne.
- **Jana** ověří u dodavatele cenu za druhou variantu.
- Rozhodnutí o termínu se odkládá na příští schůzku.
```

## Co nedělá

- **Nepřepisuje v cloudu.** Všechno běží u vás, což znamená, že to chvíli trvá a potřebuje to místo na disku.
- **Neopravuje časované titulky ručně.** Ty nesou syrový text navázaný na čas; vyčištěná verze žije zvlášť.
- **Nedoplňuje mluvčí odhadem** a nedopisuje majitele k úkolům, u kterých si není jistý.
- **Nepřekládá.** Výstup je v jazyce nahrávky.

## Jak si ho nainstalovat

Nechte to na Claudovi. Otevřete si Claude Code a napište mu:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/transcript a nainstaluj mi ten skill k sobě do `~/.claude/skills/` a rovnou mi doinstaluj i to, co potřebuje ke svému běhu.

Skill si závislosti umí zkontrolovat i doinstalovat sám při prvním spuštění a přesně vypíše, co chybí. **Výjimkou je rozlišení mluvčích** – to po vás navíc chce založit účet na HuggingFace, vyrobit si přístupový token a **v prohlížeči ručně odsouhlasit licenci tří repozitářů**. To za vás nikdo neudělá; bez toho funguje všechno ostatní beze změny.

---

### Požadavky a omezení

macOS s [Homebrew](https://brew.sh); vyvinuto a testováno tam. Potřebuje `ffmpeg`, `python3`, [whisper.cpp](https://github.com/ggml-org/whisper.cpp) a stažený model (1,5 GB, nebo 2,9 GB u přesnější varianty). Rozlišení mluvčích navíc `pyannote.audio` ve vlastním prostředí (1,2 GB), účet a token na HuggingFace a ruční odsouhlasení tří licencí. Přepis běžnou schůzku zvládne zhruba pětkrát rychleji, než trvá; s rozlišením mluvčích počítejte zhruba s dvojnásobkem celkového času.
