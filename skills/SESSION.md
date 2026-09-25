# Jak se čte transcript aktuální session

Mechanika hledání a čtení nahrané konverzace. Stojí mimo jednotlivé skilly, protože ji potřebuje víc než jeden – `/cleanup` z ní vytěžuje dohody, `/skill` to, co se při ladění skillu vyladilo. Co se z transcriptu **vytěžuje**, drží každý z nich sám; tady je jen to, jak se k němu vůbec dostat.

**Nepracuj jen s tím, co máš právě v kontextu.** Prošla-li session kompaktací, je první polovina konverzace pryč – a přesně v ní bývá to, co hledáš.

## 1. Najdi soubor

Leží v `~/.claude/projects/<working-directory-slug>/<session-id>.jsonl`, kde slug vznikne z absolutní cesty nahrazením `/` a `.` pomlčkami (`/Users/honza/Dev/score` → `-Users-honza-Dev-score`).

**`<session-id>` si vezmi z cesty ke scratchpadu**, kterou máš v systémovém promptu – je v ní jako **předposlední** komponenta – cesta končí na `/scratchpad`, takže id je adresář nad ním (`…/-Users-honza-Dev/<session-id>/scratchpad`). To je jediný spolehlivý klíč.

**Platí jedině cesta ke scratchpadu, ne libovolná cesta pod `/private/tmp` s podobným tvarem.** Vedle scratchpadu tam leží i adresář s výstupy subagentů (`…/<session-id>/tasks/…`) a ten může nést **id předchozí session** téhož projektu. Kdo id vezme odtamtud, sáhne po cizím transcriptu a nic mu to neřekne – oba soubory existují a oba se parsují. Doloženo 25. 9. 2026.

**Nesahej po naposledy modifikovaném `.jsonl` v tom adresáři.** Nad jedním projektem běžívají dvě session naráz a ta druhá do svého souboru zapisuje taky – heuristika pak ukáže na cizí konverzaci, kterou vytěžíš místo své vlastní. Doloženo 10. 9. 2026: nad `~/.claude` běžela souběžná session a „nejnovější soubor“ byl její. Zbude-li ti opravdu jen tahle cesta, **ověř obsah** proti tomu, co si z konverzace pamatuješ, dřív než z něj cokoliv vytěžíš.

## 2. Přečti ho od úplného začátku

Zajímají tě uživatelovy prompty i tvoje odpovědi – a k nim **výstupy volání nástrojů**, ve kterých u měřicí nebo datové session leží celá podstata; které a proč, drží bod 3.

U dlouhé session (řádově stovky kB a víc) na to pošli subagenta, ať ti kontext nesnědla surová data – předej mu cestu k souboru a to, co hledáš, a nech si vrátit strukturovaný výtah. Pošli ho na **výchozím modelu session s `medium`** (`~/.claude/RULES.md`, *Model a effort podle úkolu*), **ne na nejlevnějším**. Vypadá to jako výtah podle seznamu, ale není: agent musí poznat, která dohoda později přestala platit, odlišit rozhodnutí od nápadu a korekci od zaváhání. Levný model tohle splete a **jeho chybu nepoznáš, aniž bys přečetl celý transcript sám** – tedy přesně tu práci, kvůli které jsi ho poslal.

**Rozděl práci tak, aby se chyba agenta poznala levně: agent dělá úplnost, ty děláš ověření.** Nech si od něj vrátit **každou** položku, kterou najde, a k ní doslovnou citaci s číslem řádku – a filtrování, zařazení i ověření proti dokumentaci si nech v hlavní session. Agent totiž spolehlivě pozná, že se o něčem mluvilo; nepozná ale, jestli je to skutečně ta věc, kterou hledáš, a jestli to pořád platí. S doložením se obojí ověří grepem; bez něj jen tím, že si ten transcript přečteš.

**Jsi-li sám ten subagent, nedeleguj dál a ověření si nech.** Dělení „agent dělá úplnost, ty děláš ověření“ platí pro hlavní session, která transcript nemá v ruce. Poběží-li celý úklid nebo celá revize v subagentovi – tak to od 25. 9. 2026 dělá `/cleanup` –, je ten agent zároveň čtenář i ověřovatel: vnuk by načítal totéž co on a jeho nález by šel nahoru přes prostředníka (`~/.claude/RULES.md`, *Velké průzkumné úkoly deleguj*). **Citace s číslem řádku u každé položky zůstává povinná i tehdy** – rodičovská session podle nich ověřuje grepem, aniž transcript sama čte.

**Do zadání patří pokyn hlásit, co se v session rozhodlo dvakrát.** Dlouhá session totéž často rozhodne podruhé jinak a agent vytáhne to první. Nech si u položky vracet **poslední platný stav** v rámci té session a k tomu značku, že k obratu došlo, i s tím, co platilo dřív – a nejde-li to rozhodnout, ať to napíše, místo aby jednu verzi vybral. Doloženo 15. 9. 2026: agent vrátil rozhodnutí „do země bez vyplněné sazby DPH se neprodá“, které bylo **ještě týž den** přebito na opak. Zapsalo se do dokumentace jako platné a odhalilo to až ověření proti zdrojovým souborům. V téže dávce jiný agent naopak označil dvakrát rozhodnutou věc sám a ušetřil tím zastaralý zápis.

## 3. Pasti ve formátu

**První řádek nemusí mít `timestamp`.** Na začátku souboru stojí meta záznamy (`last-prompt`, `mode`, `permission-mode`, `atis-latch`), které to pole nenesou, takže `head -1 | .timestamp` vrátí `None` – a kdo z toho času počítá základ session, počítá z ničeho. **Ber proto první řádek, který ho vyplněný má:**

```sh
jq -r 'select(.timestamp) | .timestamp' <transcript> | head -1
```

Doloženo 25. 9. 2026 dvakrát v jednom dni, ve dvou ze tří ostrých běhů `/cleanup`.

**Podstata může ležet ve výstupech nástrojů, ne v textu odpovědi.** Uživatelovy prompty a textové bloky odpovědí jsou jen část konverzace: naměřená čísla, odpovědi cizích systémů a výsledky dotazů se vracejí jako **výsledky volání nástrojů**, uložené v záznamech `type: "user"` jako blok `tool_result`, kde jméno nástroje nese odpovídající `tool_use` v předchozí odpovědi. Session, která dělala datovou analýzu, má tedy podstatu tam – doloženo 25. 9. 2026, kdy vytěžení prošlo jen proto, že hlavní session každý výsledek dotazu převyprávěla v textu včetně čísel.

**Čti je selektivně podle jména nástroje.** Dělítko je, jestli výstup nese obsah, který nikde jinde není: `Bash`, MCP dotazy, **zprávy subagentů (`Agent`, `Task`) a stažené stránky (`WebFetch`, `WebSearch`)** ano – u session s panelem specialistů leží podstata právě ve zprávách agentů. `Read`, `Grep` a `Glob` ne: jejich výstupem je obsah souborů, který si přečteš přímo ze zdroje, a číst ho z transcriptu by u velkého souboru nafouklo vstup mnohonásobně.

```sh
jq -rs '(map(select(.type=="assistant") | .message.content[]? | select(.type=="tool_use") | select(.name|test("^(Bash|Agent|Task|WebFetch|WebSearch|mcp__)")) | .id) | unique) as $ids
  | map(select(.type=="user") | .message.content[]? | select(.type=="tool_result") | select(.tool_use_id as $i | $ids | index($i)) | .content)
  | .[] | if type=="string" then . else (.[]? | .text? // empty) end' <transcript>
```

**Bloky myšlení (`thinking`) a obrázky se nečtou vůbec** – myšlení není závazek a snímek obrazovky se z transcriptu vytěžit nedá. Kde na nich něco viselo, je to **mez vytěžení a musí se přiznat**, ne dopočítat.

**Zprávy poslané uprostřed rozepsané odpovědi nejsou uložené jako `type: "user"`**, ale jako `type: "queue-operation"` s `operation: "enqueue"` a textem v poli `content`. Kdo filtruje jen `type=="user"`, tiše o ně přijde – a přitom to bývají důležité dovětky („ještě ať to udělá i…“). Vytáhni je vždy taky:

```
jq -r 'select(.type=="queue-operation" and .operation=="enqueue") | .content' <transcript>
```

Stejná past hrozí u `type: "attachment"`. Nejsi-li si jistý, že máš všechno, projdi si rozložení `.type` v souboru a ověř, že jsi nic nevynechal:

```
grep -o '"type":"[a-z_-]*"' <transcript> | sort | uniq -c
```
