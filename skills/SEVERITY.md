# Škála závažnosti nálezu

Jedna škála pro všechny skilly, které hlásí nálezy. Stojí mimo ně, protože ji sdílí víc než jeden a nálezy z nich končí ve **společné** kapitole `## Review` v projektovém `CLAUDE.md` – podle dvou různých škál by pak zpětně nešlo poznat, čím byl stupeň odůvodněný.

## Stupně

- **KRITICKÉ** – bezpečnost, ztráta dat, nepřístupnost pro část uživatelů, nevratná akce bez pojistky
- **STŘEDNÍ** – reálný dopad na správnost, použitelnost nebo udržovatelnost
- **KOSMETICKÉ** – bez praktického dopadu

## Proč na stupni záleží víc, než se zdá

**Závažnost si přiděluje agent sám, ale rozhoduje o tom, kolik kontroly nález dostane.** Kosmetický se neověřuje a část se jich opraví bez ptaní; kritický jde na ověřovatele a k uživateli.

Z toho plyne pravidlo, které platí všude: **u kosmetického nálezu musí `basis` nést konkrétní pravidlo nebo bod standardu, o který se nález opírá** – ne dojem. Není-li čím ho podložit, je to STŘEDNÍ, nebo se nehlásí vůbec. Bez toho je nejnižší stupeň dírou, kterou projde neověřená změna kódu.

**Stupeň se nenafukuje ani nesnižuje podle toho, kolik práce oprava dá.** To je vlastnost řešení, ne nálezu, a promítat ji do závažnosti znamená rozhodnout za uživatele, že se něco neopraví.

## Kdo ji používá

`/review` a `/attack` – oba zapisují do téže kapitoly `## Review`. Přibude-li další skill, který hlásí nálezy, odkáže sem taky; **neopisuje si ji** (`~/.claude/RULES.md`, *Single source of truth*).

**Výjimka pro zadání subagentů:** text, který jde agentovi bez kontextu session, si stupně **opisuje celé**, protože odkaz do souboru, který nemá načtený, je mrtvý. Platí to jen na zadání, ne na tělo skillu.
