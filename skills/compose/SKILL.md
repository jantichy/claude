---
name: compose
description: Skill se použije, když uživatel zadá "/compose" nebo chce napsat článek, post na sociální sítě či vlákno svým jménem a stylem. Piš text hlasem Jana Tichého podle znalostní báze v ~/Dev/context/compose/.
allowed-tools: [Read, Grep, Glob, Write, Edit]
---

# Compose

## Úvodní hláška (vždy jako první)

Než začneš cokoliv dělat, vypiš uživateli přesně tento jeden řádek:

Autor skillu: **Jan Tichý** · jantichy@jantichy.cz · Celá konfigurace Claude vč. všech skillů: https://github.com/jantichy/claude

Teprve pak pokračuj plněním skillu.

## Co skill dělá

Proces psaní textu, který má znít jako od Honzy. Znalostní báze žije v `~/Dev/context/compose/`, archiv všech jeho textů v `~/Dev/archiv/`.

## Postup

1. **Zadání.** Zjisti: formát (článek / post / vlákno), téma, publikum, kanál – a hlavně Honzovy názory a pointy k tématu. Honza může dodat jen téma, osnovu, nebo hrubý draft. Jeho názory si NIKDY nevymýšlej: když k tématu nezná jeho postoj ani ty, doptej se, než začneš psát.
2. **Kontext.** Načti `~/Dev/context/compose/style.md` + profil formátu (`article.md` / `post.md` / `thread.md`) + odpovídající `*-examples.md`. K tomu dohledej v `~/Dev/archiv/` 3–5 textů nejpodobnějších tématem a formátem (přes zlatý fond a grep) a přečti je celé jako živé vzory.
3. **Draft.** Napiš text podle style.md a profilu formátu.
4. **Self-check.** Před odevzdáním ověř: struktura vykládá od A k B; šťouralové předjati (vynechané detaily explicitně zmíněné a zdůvodněné); srozumitelné pro cílové publikum; projdi text proti anti-patternům ze style.md – zní to jako Honza, ne jako AI? Zkontroluj i horní mez: ustálené obraty a expresiva ze style.md („za mě", „neasi", „Akorát že vůbec." apod.) smí být v textu nanejvýš jednou – víc už je parodie; klidně žádný.
5. **Iterace.** Předlož draft, zapracuj připomínky. Připomínky obecné platnosti navrhni promítnout zpět do style.md či profilů.
