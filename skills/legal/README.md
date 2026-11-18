# /legal – připomínky ke smlouvě za jednu stranu, ne za obě

Dostali jste k podpisu smlouvu, NDA nebo obchodní podmínky, nebo jste sami sepsali návrh a chcete vědět, kde vás protistrana nachytá. Obecný dotaz „podívej se na tu smlouvu“ dá seznam rozumných poznámek, ale nikoho nehájí, nic z toho neověří a vaše požadavky často sám zmírní, aby to „nebylo konfrontační“. Tenhle skill posuzuje text **výslovně za vás**: pošle na něj několik nezávislých posuzovatelů, mezi nimi advokáta protistrany, každou závažnou námitku nechá zkusit vyvrátit, s vámi ji probere a teprve pak připraví revize do Wordu a koncept mailu. Hodí se každému, kdo smlouvy připomínkuje sám a advokáta volá jen tehdy, když to opravdu stojí za to.

## Co umí

1. **Nejdřív určí rámec:** za koho posuzuje, kdo je protistrana, jakým právem se smlouva řídí a k jakému dni. Bez toho by každý posuzovatel hájil někoho jiného.
2. **První kolo** (`review`) nad cizím i vlastním návrhem. Posoudí celý text a připraví připomínky.
3. **Protinávrh** (`counter`). Když protistrana smlouvu vrátí, porovná ji s verzí, kterou jste odeslali, a roztřídí rozdíly: co převzali, co jde za vaše meze, kde vrátili past, kterou jste odstranili, co je nového a kde jejich mail tvrdí něco jiného než text. Chytí i změnu, kterou provedli potichu, bez revize. Posuzuje pak jen to nové a změněné.
4. **Vybere hlediska podle smlouvy:** co chybí, definice a rozpory, jestli to vůbec dokážete dodržet, jak by vypadal spor, odpovědnost a pokuty, peníze, ukončení, duševní vlastnictví, mlčenlivost, osobní údaje, spotřebitelské právo, omezení podnikání, cizí právo, forma a podpis, regulace. Panel vám ukáže dřív, než začne pracovat.
5. **Každou závažnou námitku ověří.** Námitku, která stojí na zákoně, ověřuje proti doslovnému znění předpisu staženému z úředního zdroje, ne proti paměti.
6. **Probere s vámi nálezy jeden po druhém.** Ke každému nabídne celé znění, které požadovat, a záložní znění pro případ, že budete chtít ustoupit. Rozhodnutí o ústupku je vždycky vaše.
7. **Připraví výstupy:** kopii dokumentu s revizemi a komentáři pod vaším jménem, interní pracovní soubor s vašimi mezemi a pastmi a koncept průvodního mailu. Mail neprozradí, kam jste ochotni ustoupit.

## Proč zrovna tenhle

- **Hájí jednu stranu.** Každé hledisko hledá, na čem prodělá vaše strana, i to, které čte text očima protistrany. Jeho úkolem je předpovědět jejich tahy.
- **Nezmírňuje vaši linii.** Silnější varianta stojí vždycky první a měkčí znění jen nabídne jako záložní.
- **Ověřuje proti zákonu, ne proti dojmu.** Nález opřený o paragraf, jehož znění nikdo nečetl, se vám ukáže jako neověřený, ne jako jistota.
- **Interní věci zůstávají uvnitř.** Komentáře ve Wordu a mail čte protistrana, a proto v nich nejsou vaše meze, záložní znění ani pořadí ústupků.
- **Pamatuje si kola.** Pracovní soubor vedle smlouvy drží, co jste požadovali, co jste pustili a proč, takže další kolo naváže tam, kde jste skončili.
- **Řekne, kdy volat advokáta.** U vysoké hodnoty, cizího práva nebo klíčového bodu bez ověřeného pramene to verdikt napíše výslovně.

## Jak se to používá

```
/legal ~/Documents/smlouvy/nda-dodavatel.docx
/legal counter ~/Documents/smlouvy/nda-dodavatel-v2.docx
/legal                         # nabídne nejnovější smlouvy
```

Režim se většinou pozná sám podle toho, jestli vedle smlouvy už leží pracovní soubor z minulého kola.

## Ukázka výstupu

```
[2/9] 🔴 Smluvní pokuta za porušení mlčenlivosti nemá strop · 2 hlediska nezávisle

Článek 7.2 ukládá pokutu 500 000 Kč „za každé jednotlivé porušení“ a vedle
ní plnou náhradu škody. Jeden e-mail poslaný třem lidem jsou podle textu tři
porušení. Advokát protistrany předpovídá, že strop odmítnou s argumentem
„u nás standard“, souhlasit ale můžou s pokutou za porušení jedné povinnosti.

Varianty:
A) Požadovat: pokuta 100 000 Kč za porušení povinnosti, celkem nejvýš výše
   odměny, a náhradu škody jen nad rámec pokuty
B) Ustoupit na: pokuta zůstává, ale „za každé porušení“ se nahradí
   „za porušení povinnosti podle odstavce 1“
```

## Co nedělá

- **Není to posudek advokáta** a nenahrazuje ho. Řekne, kdy se advokát vyplatí.
- **Nic neodesílá.** Revize vzniknou v kopii, mail zůstane konceptem a odešlete ho vy.
- **Neposuzuje, jestli je obchod dobrý nápad.** Na nezávislý posudek strategie nebo koncepce je oponentura.
- **Nedělá korekturu.** Jazyk a typografii opravuje jiný skill.

## Jak si ho nainstalovat

Je to snadné, zadejte do svého Claude Code tenhle prompt:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/legal a nainstaluj mi ten skill k sobě do `~/.claude/skills/` – celý adresář i s podadresáři. Stáhni k němu z téhož repozitáře na odpovídající místo pod `~/.claude/` i sdílené soubory ze `skills/` a `standards/`, na které jeho soubory odkazují, a definice typů subagentů, které pouští, z `agents/` do `~/.claude/agents/`. Co už u sebe mám, nepřepisuj a ukaž mi rozdíl. Odkazuje-li na jiný skill, zeptej se mě, jestli ho chci taky. Odkazy na soubory, které v repozitáři nejsou, mi vypiš a u každého se zeptej, jestli ho napojit na můj vlastní soubor, nebo odkaz smazat. Ověř, že mám nainstalovaný plugin `document-skills` z marketplace `anthropic-agent-skills`, a když ne, nainstaluj mi ho. Ověř, že mám `curl` a `pdftotext` z balíku poppler, a chybějící mi doinstaluj pro můj systém – Windows, macOS i Linux. Zeptej se mě, jestli mám sepsané vlastní zásady pro smlouvy – co nepodepíšu, kam jsem ochoten ustoupit –, a odkazy na ně ve skillu napoj na můj soubor. Nakonec mi řekni, co musím doplnit sám.

Skill se opírá o mou soukromou znalostní bázi s pravidly pro práci s právními prameny a s mými mezemi pro smlouvy. Ta v repozitáři není. Bez vlastních zásad skill funguje, jen nemá podle čeho měřit, kam až chcete jít.

---
### Požadavky a omezení

- Claude Code s pluginem `document-skills` pro revize a komentáře ve Wordu.
- `curl` a `pdftotext` pro stažení doslovného znění předpisů.
- Jeden běh stojí stovky tisíc tokenů, protože pracuje celý panel na nejsilnějším modelu a každou závažnou námitku ověřuje další agent.
- Doslovné znění dohledává u českého práva a u práva EU. U jiného rozhodného práva ověřuje jen to, co najde na webu, a verdikt to započítá jako důvod pro advokáta.
- Revize umí jen do `.docx`. U jiného formátu připraví tabulku připomínek.
