# Rozhodnutí – /invoicing

Rozvaha a doklady ke skillu `/invoicing`; za běhu skillu se nečte.

### Režim dohledání chybějícího času se jmenuje `recover`

**Rozhodnuto 6. 9. 2026.** Zvažovalo se `restore` a `rescue`; obojí zamítnuto, protože slibuje, že se něco opraví – a tenhle režim nic nezapisuje. `reconcile` je odborně přesnější, ale česky se o něm nedá mluvit, a `gaps` pojmenovává výstup místo akce.

### Co z kalendáře a prohlížeče vypadává dřív, než se z toho stane stopa

**Rozhodnuto 6. 9. 2026.** Všechny čtyři filtry kalendáře (celodenní události, odmítnuté schůzky, duplicitní záznamy na týž čas, zasedačky mezi účastníky) vyrobily při prvním ostrém běhu `recover` falešný nález, takže to nejsou hypotézy. Týž běh doložil i dvě další pasti: v reálných datech prohlížeče se našla návštěva dlouhá 58 hodin, a čas z kalendáře posunutý o časové pásmo udělal z potvrzené schůzky falešný nález chybějících hodin.

### Odesílací nástroje Gmailu drží `deny`, ne `allowed-tools`

**Rozhodnuto 8. 9. 2026.** Odesílací nástroje Gmailu (`send_message`, `reply`, `forward`, obojí `trash_*`) jsou od toho dne v `deny` v `~/.claude/settings.json`; do té doby slib, že skill mail neodešle, držel jen text skillu.

`allowed-tools` hranicí být nemůže. Podle dokumentace Claude Code to pole nástroje neomezuje, jen předschvaluje: *„It does not restrict which tools are available: every tool remains callable.“* Skill hlavičku s ním kdysi měl a commit `622fa4f` (5. 9. 2026) ji zrušil s odůvodněním, že „zakazovala Gmail MCP“ – jenže nic nezakazovala, skill se pak jen na `create_draft` doptával. Commit `c4108d4` (30. 10. 2026) do ní MCP nástroje vrátil jen proto, aby se skill na koncepty a čtení pošty a sdílených dokumentů neptal.

### Co ukázal druhý běh `recover` nad týmž klientem

**Rozhodnuto 11. 9. 2026.** Druhý běh `recover` nad klientem, nad kterým běžel o pět dnů dřív, doložil několik pravidel katalogu:

- **Vyvrácený nález z minula se vypisuje jmenovitě.** Dva nálezy z prvního běhu stály jen na vlastním bloku v kalendáři a oba padly – a bylo to užitečnější než celý zbytek běhu.
- **Vlastní blok v kalendáři potřebuje druhou stopu.** U téhož klienta se stalo obojí: blok bez druhé stopy i blok, v jehož čase ležela stopa soukromé aktivity, každé jednou.
- **Mailové notifikace z nástroje bez přístupu jsou doklad.** Ověřily schůzku, ke které jinak žádný záznam nebyl.
- **Shoda se jménem klienta se ověřuje v kontextu věty.** U krátkého jména se do shody trefilo běžné slovo a OAuth kód v URL, kde se jméno objevilo uvnitř náhodného řetězce.

### Příklad otázky k rozsahu je bez jména klienta a bez jeho čísel

**Rozhodnuto 11. 9. 2026.** `recover.md` je veřejný, takže konkrétní hodiny na konkrétní zakázce do něj nepatří ani jako ilustrace; příklad otázky na odevzdaný výstup je proto vymyšlený.

### Blok práce v Claudovi končí mezerou delší než 20 minut

**Rozhodnuto 30. 9. 2026.** Změřeno nad zářím u jednoho klienta: mez 10 minut dala 16,0 h, 20 minut 20,3 h a 30 minut 22,0 h. Pod 20 minut se blok trhá na pauzách, kdy Claude pracuje a uživatel čeká; nad 20 minut se slévají samostatná sezení.
