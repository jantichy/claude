# Škála závažnosti nálezu

Jedna škála pro všechny skilly, které hlásí nálezy. Stojí mimo ně, protože **stupeň musí napříč skilly měřit totéž** – jinak zpětně nejde poznat, čím byl odůvodněný, a nálezy z různých běhů se nedají porovnat ani seřadit. U `/review` a `/attack` to platí dvojnásob, protože jejich nálezy končí v jedné a téže kapitole `## Review` v projektovém `CLAUDE.md`.

## Stupně

- **KRITICKÉ** – bezpečnost, ztráta dat, nepřístupnost pro část uživatelů, nevratná akce bez pojistky
- **STŘEDNÍ** – reálný dopad na správnost, použitelnost nebo udržovatelnost
- **NÍZKÉ** – bez praktického dopadu

## Proč na stupni záleží víc, než se zdá

**Závažnost si přiděluje agent sám, ale rozhoduje o tom, kolik kontroly nález dostane.** Čím výš, tím víc pozornosti: kritický jde na ověření a k uživateli jednotlivě, nejnižší stupeň se ověřuje jako poslední, vypořádává hromadně, nebo se k ověření vůbec nedostane. **Čím přesně se to liší, si každý skill určuje sám** – `/review` nízké nálezy neověřuje a část z nich opraví bez ptaní, `/oponent` je předkládá jedním blokem k rozhodnutí, `/audit` je ověřuje až za těmi závažnějšími. Společné je, že nejnižší stupeň nese nejmenší jistotu.

Z toho plyne pravidlo, které platí všude: **u nálezu nejnižšího stupně musí být čím ho podložit** – konkrétní pravidlo, bod standardu nebo položka katalogu, ne dojem. Skilly, které vedou u nálezu pole `basis`, to zapisují do něj. Není-li čím podložit, je to STŘEDNÍ, nebo se nehlásí vůbec. Bez toho je nejnižší stupeň dírou, kterou projde neověřená změna.

**Stupeň se nenafukuje ani nesnižuje podle toho, kolik práce oprava dá.** To je vlastnost řešení, ne nálezu, a promítat ji do závažnosti znamená rozhodnout za uživatele, že se něco neopraví.

## Kdo ji používá

`/review`, `/attack`, `/consistency`, `/oponent` a `/audit`. První dva zapisují do téže kapitoly `## Review`, `/consistency` do `## Consistency` a `/oponent` do oponovaného dokumentu a podle výsledku do `docs/decisions.md` nebo `docs/todo.md`, a `/audit` do registru nálezů pro klienta – **sdílená kapitola tedy není podmínkou**, sdílené měřítko ano. Každý z nich si nad obecnými stupni podává vlastní doménové čtení (útok jinak než oponentura), ale **stavět vlastní taxonomii vedle téhle se nesmí**. Přibude-li další skill, který hlásí nálezy, odkáže sem taky; **neopisuje si ji** (`~/.claude/RULES.md`, *Single source of truth*).

**Výjimka pro zadání subagentů:** text, který jde agentovi bez kontextu session, si stupně **opisuje celé**, protože odkaz do souboru, který nemá načtený, je mrtvý. Platí to jen na zadání, ne na tělo skillu.
