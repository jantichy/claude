# Rozhodnutí – /discovery

Soubor drží rozvahu a doklady skillu `/discovery`; za běhu skillu se nečte.

### Stav „máme to, nebo ne“ se v *Co musíme mít* ověřuje proti návrhu

**Rozhodnuto 25. 9. 2026.** Celý krok se dívá ven a jeho vstupem jsou podklady o trhu, ne dokumentace vlastního řešení. Nález tvaru *„tohle systém nemá“* proto vzniká z toho, co skill nevidí, a vypadá doloženě, protože doložená je ta půlka o konkurenci. Vymyšlený požadavek stojí víc než vynechaný: dostane se do fronty jako práce, projde řezem MVP a rozhoduje se o něm znovu, přestože je hotový.

Doloženo v rezervačním systému: z osmi řádků se stavem **nemá** byly dva neplatné – volba mezi zálohovkou a daňovým dokladem, kterou drží zděděné nastavení `document`, a vynechání platebního kroku u nulové ceny, které řeší `payFree` a stav `FREE_PAID`. Obojí bylo rozhodnuté měsíce předtím a našlo se až při práci na té položce. Zbylé nálezy platily, takže to není argument proti kroku, ale proti psaní stavu zpaměti.
