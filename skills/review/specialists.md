# Katalog specialistů

Kdo se v panelu `/review` zapíná a kdy. Vytažené ze `SKILL.md`, protože je to referenční katalog k nahlédnutí při sestavování panelu, ne text, který se čte v každém běhu. Texty zadání pro agenty drží [`agents.md`](agents.md) – s jedinou výjimkou, zadáním pro *Agentní infrastrukturu*, které stojí tady; proč, je napsané u něj.

- [Pracovní specialisté](#pracovní-specialisté)
- [Standardoví specialisté](#standardoví-specialisté)
- [Zadání pro Agentní infrastrukturu](#zadání-pro-agentní-infrastrukturu)

Specialisté se vybírají **podle toho, čeho se soubory v rozsahu týkají**, ne podle typu projektu. Obsahový projekt tedy nedostane specialisty na kód, web dostane obojí. Neposílej agenta na hledisko, ke kterému v rozsahu není co prověřovat.

## Pracovní specialisté

Ptají se, jestli je to správně:

| Specialista | Ptá se | Zapíná se, když v rozsahu je | Typ |
|---|---|---|---|
| **Korektnost** | dělá to, co má, scénář po scénáři? | jakýkoliv kód | – (vestavěné `/code-review`) |
| **Bezpečnost** | dá se to zneužít? | kód, který zpracovává vstup, autorizuje, pracuje s daty uživatelů nebo sahá ven, **a vždy změna manifestu nebo lockfile závislostí** | – (vestavěné `/security-review`); vlastní agent navíc `Explore` |
| **Data a stavy** | migrace, konzistence, souběh, idempotence | datový model, migrace, stavový automat, fronta, plánované úlohy | `Explore` |
| **Provoz a chyby** | co se stane, když to spadne? | volání cizích systémů, I/O, dlouhé operace, cokoliv s timeoutem | `Explore` |
| **Testy** | co není pokryté a které testy jsou falešně zelené? | jakýkoliv kód, u kterého projekt má `test` v kontraktu příkazů | `Explore` |
| **Agentní infrastruktura** | co běží mimo permission systém a co si to pouští? | `.claude/settings*.json`, hooky, `.mcp.json`, `allowed-tools` ve skillech, `.semgrep/`, cokoliv v `.claude/` | `Explore` |

## Standardoví specialisté

Ptají se, jestli to drží předpis. Každý je jedna sada z `~/Dev/context/`:

**Většina jich nic nespouští** – měří text proti textu, takže jedou na `reader` a odrážka o `evidence` pro ně neplatí (viz [`agents.md`](agents.md)). Tři výjimky mají `Explore`, protože jejich předmět leží mimo čtení souborů: `coding/quality.md` ověřuje kontrakt příkazů a CI, `analytics/` a `advertising/` sahají na běžící měření a na cizí reklamní účty.

| Sada | Kdy se aplikuje | Typ |
|---|---|---|
| `coding/coding.md` | jakýkoliv kód, datový model, migrace, konfigurace, CI | `reader` |
| `coding/architecture.md` | vrstvy a jejich hranice, cesta k datům, transakce kolem cizích volání, souběh, běhy na pozadí – a u projektu, který je v `CLAUDE.md` vedený jako **aplikace**, i kontrolní seznam *Minimum hotové aplikace* (**navíc** k `coding/coding.md`) | `reader` |
| `coding/quality.md` | kontroly kvality, kontrakt příkazů, CI, testovací infrastruktura, závislosti (**navíc** k `coding/coding.md`) | `Explore` |
| `web/web.md` | webové rozhraní – šablony, komponenty, styly, stránky | `reader` |
| `web/admin.md` | administrace, backoffice, interní nástroj (**navíc** k `web/web.md`, ne místo něj) | `reader` |
| `analytics/` | implementace měření – GTM kontejnery a jejich export, dataLayer pushe, měřicí kódy v šablonách, CMP a consent (**navíc** k `web/web.md`) | `Explore` |
| `advertising/` | vedení placených kampaní – struktura účtu, biddovací strategie, konverzní akce jako vstup pro bidding, kreativy a cesta po prokliku (měřicí stranu téhož drží `analytics/`) | `Explore` |
| `text/text.md` | souvislé české texty – dokumentace, obsah stránek, články, newslettery (o textech v rozhraní rozhoduje `web/web.md`) | `reader` |
| `text/typography.md` | česká sazba čehokoliv psaného česky – interpunkce, mezery, čísla, data, výčty (**navíc** k `text/text.md`, ale platí i tam, kde souvislý text nevzniká) | `reader` |
| `design/design.md` | vizuální výstupy – grafika, barevné systémy, práce s písmem, cokoliv, u čeho se rozhoduje o čitelnosti a kontrastu (sazbu znaků drží `text/typography.md`) | `reader` |
| `design/slides.md` | promítané prezentace (**navíc** k `design/design.md`) | `reader` |
| `training/training.md` | obsah školení a kurzů – osnovy, lekce, cvičení, materiály (**navíc** k `text/text.md`: text řeší, jak je to napsané, training to, jak je to postavené) | `reader` |

`~/.claude/WORKTREE.md` mezi sadami schválně není – popisuje layout repozitáře, ne pravidla pro zdrojové soubory. Ze stejného důvodu tu není `organizations/` ani `brand/`: **je to korpus, ne standard.** Korpus říká, jak to je (kdo Honza je, s kým pracuje), ne jak se to má dělat – nedá se proti němu auditovat, protože nemá prověřitelná pravidla. Soulad textu s brandem je posouzení, ne kontrola; na to je `/oponent`.

## Zadání pro Agentní infrastrukturu

Tenhle specialista má **vlastní zadání**, protože proti němu nestojí žádný standard v `~/Dev/context/`, a tedy ani nic, proti čemu by měřil standardový specialista:

```
Prověř konfiguraci agentní vrstvy projektu. Ptáš se na jedinou věc: co z tohohle
běží mimo permission systém a co si to pouští?

Hooky se totiž na povolení neptají – spustí se samy, s právy uživatele, a jejich
obsah nikdo neschvaluje. Zatímco na příkazy projektu existuje souhlasový
mechanismus (`~/.claude/verify.sh --allow`), na tenhle adresář žádný není.

U KAŽDÉ POLOŽKY ODPOVĚZ:
- Hook: kdy se spouští, co spouští, odkud bere binárku (PATH? node_modules
  z tohohle repa? absolutní cesta?), s jakým cwd, a co se stane, když selže –
  maskuje si návratový kód (`; true`, `|| true`)?
- MCP server: kam posílá data, čím se autentizuje, kde má tajemství.
- `allowed-tools` skillu: potřebuje opravdu všechny, které jmenuje? Má Bash
  nebo zápis tam, kde stačí čtení?
- Nastavení oprávnění: co je povolené plošně a co by povolené být nemělo.
- Cokoliv, co se spouští automaticky nad obsahem, který přišel zvenčí.

Nález musí mít konkrétní zneužití: kdo co udělá → co se stane. „Hook by mohl být
nebezpečný“ není nález; „soubor .claude/settings.local.json spouští po každé
editaci npx z node_modules tohohle repa, takže kdokoliv s právem zápisu do
package.json spustí libovolný kód“ nález je.
```
