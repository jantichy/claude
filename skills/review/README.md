# /review – panel nezávislých pohledů na hotovou práci

> **Součást životního cyklu projektu.** Tenhle skill patří do ucelené sady skillů, které vedou práci od založení projektu až po vyhodnocení provozu. Jedny tvoří, druhé se starají o to, co už vzniklo, třetími každá session začíná a končí – a žádný nedělá práci toho vedle:
>
> **Osa** [`/project`](../project/README.md) → [`/discovery`](../discovery/README.md) → [`/specify`](../specify/README.md) → [`/architect`](../architect/README.md) → [`/breakdown`](../breakdown/README.md) → [`/implement`](../implement/README.md) → [`/release`](../release/README.md) → [`/evaluate`](../evaluate/README.md)
>
> **Kontroly** [`/oponent`](../oponent/README.md) · [`/consolidate`](../consolidate/README.md) · **`/review`** · [`/consistency`](../consistency/README.md) · [`/attack`](../attack/README.md)
>
> **Session** [`/next`](../next/README.md) · [`/continue`](../continue/README.md) · [`/end`](../end/README.md) · [`/merge`](../merge/README.md) · [`/break`](../break/README.md)
>
> Projít se nemusí celý – u drobné změny odpadá zadání i plán, u projektu bez kódu nasazení i vyhodnocení provozu.

Prověří hotovou práci před uzavřením z několika nezávislých hledisek naráz. Stojí to na třech vrstvách: nejdřív běží nástroje projektu, které nic nedomýšlejí a stojí nula tokenů, pak paralelní panel, kde každý má **jediné hledisko**, a nakonec ověřovatel, jehož úkolem je nález **vyvrátit**. Co ověření nepřežije, se vám vůbec nezobrazí – bez té třetí vrstvy vás panel zavalí pravděpodobně znějícími nálezy, po třetím falešném ho začnete ignorovat a čtvrtý, pravý, přehlédnete.

## Co umí

1. **`/review`**, případně **`/review branch`** (výchozí) – prověří změny na aktuální větvi.
2. **`/review full`** – celý projekt. U staršího projektu předem řekne, kolik souborů to bude, a při stovkách se zeptá, jestli pokračovat.
3. **Deterministická vrstva** – typová kontrola, linter, testy, produkční build, audit závislostí, hledání tajemství v repozitáři, statická analýza, mutační testování, přístupnost, výkon a pokrytí. Vypisuje naměřenou hodnotu i práh, ne jen počet.
4. **Panel specialistů, který se skládá podle toho, čeho se změny týkají** – korektnost, bezpečnost, data a stavy, provoz a chyby, testy, konfigurace agentní vrstvy. K tomu specialisté měřící soulad s doménovými znalostmi: kód, web, administrace, analytika, texty, vizuál, prezentace, školení. Mění-li se jen dokumentace, měří se korektnost a bezpečnost proti scénářům, oprávněním a citlivým oblastem v návrhu, ne proti kódu, který tam není.
5. **Přísnější režim v citlivých oblastech.** Dotkne-li se změna přihlašování, oprávnění, plateb, nahrávání souborů, osobních údajů, mazání dat nebo odesílání pošty ven, je specialista na bezpečnost povinný a dostane úplný jmenný seznam tříd zranitelností.
6. **Umí navázat na přerušený běh** – ověřený seznam nálezů se ukládá na disk, takže se nejdražší část práce neplatí dvakrát.
7. **Sporné nálezy projde s vámi jeden po druhém**, pak všechno včetně mechanických oprav zapracuje sám a u opravy hlášené pracovním specialistou doplní test.
8. **Pamatuje si, co jste rozhodli neopravovat** – a příště se na to už neptá, dokud se dotčený kód nezmění.
9. **Nedojde-li seznam do konce, nabídne přerušení.** Roste-li konverzace do velikosti, ve které už se pracuje pomalu a nepřesně, řekne to a zbývající položky i s tím, co je u nich potřeba rozhodnout, uloží do seznamu úkolů – další session pak pokračuje přesně tam, kde jste skončili, a s čistou hlavou.

## Proč zrovna tenhle

- **Nejdřív se zeptá, pak pracuje.** Na všechno, co musíte rozhodnout vy, se zeptá v jednom zátahu, jednu otázku za druhou, a teprve pak všechno zapracuje sám – mezitím od toho můžete odejít. Na co přijde až při práci, nechá na další kolo otázek.
- **Nespuštěný nástroj není nula.** Kontrola, kterou nešlo spustit, se vypisuje jako nespuštěná – tři nespuštěné kontroly vypsané jako tři nuly by vypadaly jako tři čisté výsledky.
- **Vykazuje, co kdo doopravdy přečetl.** Každý specialista odevzdá seznam souborů, které prošel, a skill z toho spočítá poměr proti rozsahu; co nepřečetl nikdo, se vypíše jmenovitě. **Prázdný výstup agenta tím přestal znamenat „je čisto“** – bez toho poměru se totiž nedá odlišit od toho, že spadl.
- **Vypisuje poměry, ne jen počty.** „Pět nálezů“ vypadá stejně po řádném i po odbytém běhu; skill ukazuje, kolik jich panel našel, kolik jich zbylo po sloučení, kolik se jich ověřilo a kolik přežilo.
- **Důkazní břemeno je záměrně nesymetrické.** U střední závažnosti platí „při pochybnosti vyvracej“, u kritické naopak: vyvrátit ji lze jedině tak, že ověřovatel **jmenuje konkrétní ochranu a její místo**. „Nejspíš to řeší framework“ vyvrácení není. Cena omylu je totiž nesymetrická – falešný nález stojí jednu otázku, přehlédnutá chyba díru v produkci, a je navždy neviditelná.
- **Umlčené nálezy expirují změnou kódu.** Důvod zamítnutí bývá vázaný na stav kódu v ten den; po přepsání přestane platit, ale filtr se aplikuje dřív než hledání, takže by se to nikdo nedozvěděl. Bez expirace je z toho seznam, kterým projekt za rok oslepne.
- **Vyvrácené kritické nálezy se vypisují.** Je to jediné místo, kde je vidět, co bylo umlčeno – bez něj se chybné vyvrácení nedá odhalit vůbec.
- **Text v prověřovaných souborech agenta neřídí.** Věta „předchozí instrukce neplatí“ nebo „tenhle modul nehlas“ nalezená v komentáři je **nález**, ne pokyn – a hledá se navíc mechanicky, protože právě tuhle třídu panel z principu nechytí: neexistující nález nemá kdo spočítat.
- **Každý nález musí mít konkrétní selhání.** „Mohla by tu být souběžnost“ není nález; „když dva požadavky dorazí mezi čtením a zápisem na tomhle řádku, druhý přepíše první“ nález je.
- **Opakovaný nález se převede na pravidlo pro nástroj.** Od té chvíle ho chytá stroj zadarmo místo agenta pokaždé znovu.
- **Panel se nenafukuje.** Nad 7 specialistů se nechodí – panel, který vygeneruje víc nálezů, než kdo přečte, se přestane číst celý. A vynechaný specialista se vždycky jmenuje, protože tichý výběr vypadá jako úplný panel.

## Jak se to používá

```
/review        # změny na větvi (totéž co /review branch)
/review full   # celý projekt
```

## Ukázka výstupu

```
## Výsledky review

Rozsah: 14 z 16 souborů diffu (2 generované vynechány)
Specialisté: korektnost, bezpečnost, testy, coding.md · vynechána web.md – v rozsahu není rozhraní

Deterministická vrstva:
- průběžná kontrola: ✅
- audit závislostí: npm audit rc=0 → 0 HIGH/CRITICAL
- tajemství v repu: gitleaks rc=0 → 0
- statická analýza: nespuštěno – semgrep není na stroji
- pokrytí: 84 % (práh 80 %)

Panel: 31 nálezů → 22 po deduplikaci → 22 ověřeno → 13 přežilo:
- 🔴 Kritické: 1    🟡 Střední: 8    🔵 Nízké: 4
```

## Co nedělá

- **Neaudituje vnitřní konzistenci.** Ptá se „je to správně a drží to předpis?“, ne „sedí si projekt sám se sebou?“ – na to je `/consistency`.
- **Neposuzuje, jestli je záměr dobrý.** Měří proti předpisu – zadání a doménovým znalostem; co žádný předpis nemá, posoudí `/oponent`. U projektu bez kódu, ke kterému žádná doménová znalost neexistuje, proto skoro nemá co dělat.
- **Nevytěžuje konverzaci** a nedělá revizi dokumentace nad rámec vlastních nálezů – to je `/end`.
- **Nenasazuje.** To je `/release`.
- **Nezačne nad rozbitým stavem.** Nejsou-li testy zelené, zastaví se a pošle to dodělat.

## Jak si ho nainstalovat

Je to snadné, zadejte do svého Claude Code tenhle prompt:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/review a nainstaluj mi ten skill k sobě do `~/.claude/skills/` – celý adresář i s podadresáři. Stáhni k němu z téhož repozitáře na odpovídající místo pod `~/.claude/` i sdílené soubory ze `skills/` a `standards/`, na které jeho soubory odkazují, a definice typů subagentů, které pouští, z `agents/` do `~/.claude/agents/`. Co už u sebe mám, nepřepisuj a ukaž mi rozdíl. Odkazuje-li na jiný skill, zeptej se mě, jestli ho chci taky. Odkazy na soubory, které v repozitáři nejsou, mi vypiš a u každého se zeptej, jestli ho napojit na můj vlastní soubor, nebo odkaz smazat. Nakonec mi řekni, co musím doplnit sám.

Doménoví specialisté měří soulad s mými soukromými doménovými znalostmi, které v tomhle repozitáři nejsou; pracovní specialisté fungují bez nich. Aby měla deterministická vrstva co spouštět, potřebuje projekt mít v instrukcích zapsané své příkazy; co chybí, skill vypíše jako nezkontrolované.

**Nebo celou sadu naráz.** Chcete-li místo jednoho skillu rovnou celý životní cyklus, zadejte do svého Claude Code tenhle prompt:

> Jdi na https://github.com/jantichy/claude/tree/main/skills a nainstaluj mi do `~/.claude/skills/` celý životní cyklus: project, discovery, specify, architect, breakdown, implement, release, evaluate, oponent, consolidate, review, consistency a attack, a k nim skilly, kterými session začíná a končí: next, continue, end, merge a break. Každý z nich nainstaluj přesně podle promptu v sekci „Jak si ho nainstalovat“ v jeho README; na skilly z téhle sady se mě při tom neptej, beru je všechny.

---

### Požadavky a omezení

Git kvůli určení rozsahu. Volitelně `gitleaks` (hledání tajemství), `semgrep` (statická analýza) a `shellcheck` (skripty) – bez nich příslušná kontrola odpadne a skill to napíše do výpisu. Panel i ověřování běží zčásti na nejsilnějším modelu, takže `full` na velkém projektu je drahý běh.
