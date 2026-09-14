# Jak se čte transcript aktuální session

Mechanika hledání a čtení nahrané konverzace. Stojí mimo jednotlivé skilly, protože ji potřebuje víc než jeden – `/cleanup` z ní vytěžuje dohody, `/skill` to, co se při ladění skillu vyladilo. Co se z transcriptu **vytěžuje**, drží každý z nich sám; tady je jen to, jak se k němu vůbec dostat.

**Nepracuj jen s tím, co máš právě v kontextu.** Prošla-li session kompaktací, je první polovina konverzace pryč – a přesně v ní bývá to, co hledáš.

## 1. Najdi soubor

Leží v `~/.claude/projects/<slug-pracovního-adresáře>/<session-id>.jsonl`, kde slug vznikne z absolutní cesty nahrazením `/` a `.` pomlčkami (`/Users/honza/Dev/score` → `-Users-honza-Dev-score`).

**`<session-id>` si vezmi z cesty ke scratchpadu**, kterou máš v systémovém promptu – je v ní jako poslední adresář. To je jediný spolehlivý klíč.

**Nesahej po naposledy modifikovaném `.jsonl` v tom adresáři.** Nad jedním projektem běžívají dvě session naráz a ta druhá do svého souboru zapisuje taky – heuristika pak ukáže na cizí konverzaci, kterou vytěžíš místo své vlastní. Doloženo 10. 9. 2026: nad `~/.claude` běžela souběžná session a „nejnovější soubor“ byl její. Zbude-li ti opravdu jen tahle cesta, **ověř obsah** proti tomu, co si z konverzace pamatuješ, dřív než z něj cokoliv vytěžíš.

## 2. Přečti ho od úplného začátku

Zajímají tě uživatelovy prompty i tvoje odpovědi.

U dlouhé session (řádově stovky kB a víc) na to pošli subagenta, ať ti kontext nesnědla surová data – předej mu cestu k souboru a to, co hledáš, a nech si vrátit strukturovaný výtah. Pošli ho na **výchozím modelu session s `medium`** (`~/.claude/RULES.md`, *Model a effort podle úkolu*), **ne na nejlevnějším**. Vypadá to jako výtah podle seznamu, ale není: agent musí poznat, která dohoda později přestala platit, odlišit rozhodnutí od nápadu a korekci od zaváhání. Levný model tohle splete a **jeho chybu nepoznáš, aniž bys přečetl celý transcript sám** – tedy přesně tu práci, kvůli které jsi ho poslal.

## 3. Pasti ve formátu

**Zprávy poslané uprostřed rozepsané odpovědi nejsou uložené jako `type: "user"`**, ale jako `type: "queue-operation"` s `operation: "enqueue"` a textem v poli `content`. Kdo filtruje jen `type=="user"`, tiše o ně přijde – a přitom to bývají důležité dovětky („ještě ať to udělá i…“). Vytáhni je vždy taky:

```
jq -r 'select(.type=="queue-operation" and .operation=="enqueue") | .content' <transcript>
```

Stejná past hrozí u `type: "attachment"`. Nejsi-li si jistý, že máš všechno, projdi si rozložení `.type` v souboru a ověř, že jsi nic nevynechal:

```
grep -o '"type":"[a-z_-]*"' <transcript> | sort | uniq -c
```
