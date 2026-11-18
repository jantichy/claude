# Výstupy

Co `/legal` zapisuje, jak se to jmenuje a co v tom smí stát. Všechno leží **ve složce posuzovaného dokumentu**. `<stem>` je jméno dokumentu bez přípony, u protinávrhu jméno dokumentu z prvního kola, aby všechna kola zůstala u jednoho pracovního souboru.

| Soubor | Co to je | Čte ho |
|---|---|---|
| `<stem>.legal.md` | interní pracovní soubor | jen naše strana |
| `<stem>-pripominky.docx`, u anglické smlouvy `<stem>-comments.docx` | kopie dokumentu s revizemi a komentáři | protistrana |
| `<stem>-pripominky.md` | tabulka připomínek, není-li dokument `.docx` | protistrana |
| `<stem>.mail.md` | koncept průvodního mailu | protistrana, až ho uživatel odešle |

V režimu `counter` dostane revize i mail číslo kola (`<stem>-pripominky-2.docx`, `<stem>.mail-2.md`), aby se nepřepsalo, co už odešlo.

## Pracovní soubor

```
# <název dokumentu> – interní posudek

> **Interní.** Nesmí jít protistraně ani nikomu mimo naši stranu: nese naše meze,
> záložní znění a pasti.

## Rámec

- **Dokument:** <cesta k prvnímu kolu>
- **Naše strana:** <kdo>
- **Protistrana:** <kdo, podnikatel / spotřebitel, odkud>
- **Rozhodné právo:** <právo>
- **Rozhodný den:** <datum>
- **Autor revizí:** <jméno>
- **Mantinely:** <cesty>
- **Vědomě zamítnuté:** <výčet i s důvody>

## Deník kol

- **<YYYY-MM-DD>** · kolo 1 · `review` · posouzeno: <soubor> · hlediska: <seznam> · <N nálezů> · výstupy: <soubory> · připraveno
- **<YYYY-MM-DD>** · kolo 1 · odesláno <komu>

## Kolo <N> – nálezy

### <číslo>. <název nálezu> · <hledisko> · <🔴 / 🟡 / 🔵>

<V čem je pro naši stranu problém a jaký má důsledek, souvislým textem. Na čem nález stojí:
pramen s doslovnou citací, odkud je a ke kterému dni platí, a míra jistoty; nebo obvyklá
praxe; nebo jen úvaha.>

- **Znění dnes:** <článek, doslovná citace>
- **Navržené znění:** <celé>
- **Záložní znění:** <celé>
- **Past:** <co protistrana může vrátit nebo jak to obrátit proti nám>
- **Souvislosti:** <čísla nálezů a druh vazby – podmiňuje / vylučuje / směna>
- **Ověření:** <ověřeno / neověřeno a proč>
- **Stav:** <open / accepted / rejected / deferred> – <co uživatel rozhodl: navržené znění / záložní znění / beze změny / odloženo, a proč>

## Kolo <N> – porovnání verzí

*Jen v režimu `counter`.* Každý rozdíl s třídou z `SKILL.md`, *Fáze 2*, a odkazem na nález, který z něj vznikl.

## Mapa souvislostí

<skupiny souvisejících nálezů a vyjednávací linie: co požadujeme, co jsme ochotni vyměnit za co>

## Odloženo

<nálezy odložené bez projektu s `docs/todo.md`>
```

**Stav nálezu se zapisuje hned po odpovědi uživatele.** Pracovní soubor je zároveň ověřený seznam běhu (`~/.claude/skills/panel.md`, *Ověřený seznam na disku*). Otevřený nález v něm znamená přerušený průchod.

Datum do deníku vyrob `date +%F`.

## Revize ve Wordu

- **Kopie, nikdy originál.** Originál zůstává, jak přišel, protože se proti němu v příštím kole porovnává.
- **Každá změna je revize** (`w:ins`, `w:del`) pod autorem z rámce. Změna bez revize je tichá změna, tedy přesně to, co skill protistraně v `counter` vytýká.
- **Komentář patří k textu, kterého se týká**, a zdůvodňuje změnu pro protistranu: věcný argument, případně odkaz na předpis. Nikdy v něm nesmí být naše záložní znění, meze, pořadí ústupků ani interní úvaha.
- **Jazyk komentářů je jazyk smlouvy.**

## Tabulka připomínek

Pro dokument, který není `.docx`:

```
| Článek | Dnešní znění | Navržené znění | Zdůvodnění |
|---|---|---|---|
```

Zdůvodnění se řídí stejným pravidlem jako komentář ve Wordu.

## Koncept průvodního mailu

- **Shrne hlavní požadované změny a jejich důvody**, nejzávažnější první, a odkáže na revize v příloze.
- **Neprozradí** záložní znění, ochotu ustoupit ani to, které body jsou pro nás nejdůležitější.
- V `counter` navíc řekne, co přijímáme, a pojmenuje rozpory mezi jejich mailem a textem jako dotaz, ne jako obvinění.
- Je v jazyce korespondence s protistranou a končí podpisem autora revizí.
- **Neodesílá se.** Je to koncept k úpravě a odeslání uživatelem.
