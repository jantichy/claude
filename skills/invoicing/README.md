# /invoicing – faktury na konci měsíce bez ručního sčítání

Konec měsíce znamenal pokaždé totéž: projít timetracking, sečíst hodiny po klientech, přepsat je do fakturačního systému, stáhnout dvě PDF a napsat ke každému mail. Tenhle skill to udělá za vás – a u každého klienta se zastaví dřív, než něco vystaví: ukáže, co napočítal, co vyřadil a co je mu podezřelé. Končí rozepsaným draftem s fakturou a výkazem hodin v příloze. **Odeslat ho musíte vždycky vy.**

## Co umí

1. **`/invoicing full`** (výchozí) – celý průběh: součet hodin, kontrola s vámi, vystavení dokladů, přílohy a rozepsané drafty.
2. **`/invoicing preview`** – náhled toho, co by se vystavilo. Nic nevystaví, nic nezapíše, nikam nesáhne. Hodí se před koncem měsíce zjistit, jestli hodiny sedí.
3. **`/invoicing recover`** – **dohledá čas, který jste si zapomněli natrackovat.** Projde mail, kalendář, chat, hovory, commity, historii prohlížeče, porovná to s timetrackingem a ukáže tipy i s doložením, na základě čeho k nim došel.
4. **Omezení na jednoho klienta** – za režimem smí stát jeho jméno; bez něj jede přes všechny.
5. **U dohledávání i volba období**, takže jde zpětně zjistit, kolik času systematicky uniká.
6. **Umí navázat na přerušený běh** – klienta s hotovou fakturou, ale bez draftu, dokončí, nezaloží znovu.
7. **Vede deník dohod.** Co se u klienta dohodne odchylně, zapíše se datovaně, aby se za rok nevedl spor proti paměti.

## Proč zrovna tenhle

- **Hranici „odkud počítat" nikdy neodhaduje.** Čte ji z poslední vystavené faktury, takže se nerozejde ani tehdy, když jste mezitím fakturovali ručně. A do staré faktury zpětně nic nedopisuje.
- **Mail neodešle nikdy.** Ani když ho o to uprostřed běhu sami poprosíte. Je to tvrdá stopka nastavená předem a s chladnou hlavou – právě proto přebíjí pobídku „pošli to, spěchám".
- **Nic nevystaví bez potvrzení.** U každého klienta ukáže hodiny, sazbu, částku, všechna tři data i **text, který se doopravdy vytiskne na doklad**.
- **Podezřelé záznamy neřeší potichu.** Záznam bez popisu, běžící časovač, položka delší než dvanáct hodin, čas mimo období, projekt bez klienta – to všechno odloží a nechá rozhodnout vás.
- **Nezaokrouhluje jednotlivé záznamy**, jen výsledný součet. Zaokrouhlené čtvrthodinky nafouknou měsíc o hodiny a klient si toho všimne dřív než vy.
- **Hlídá zákonnou lhůtu na vystavení dokladu** i pořadí v číselné řadě, a když by faktura vyšla už propadlá, nevystaví ji a zeptá se.
- **Ověří doklad zpětně ze systému** – číslo, částku, odběratele i všechna data. Nespoléhá na to, že zápis prošel.
- **Ověří i přílohy**, než je přiloží: že nejsou prázdné a že období ve výkazu sedí se skutečně fakturovaným. A přejmenuje je tak, aby si je klient našel v účetnictví.
- **Dohledaný čas nikdy nezapíše do timetrackingu.** Odhad postavený na úsudku o cizích datech je návrh, ne zjištění – doplnit ho je vaše rozhodnutí.
- **Nefakturovatelný čas dohledá taky**, jen ho nepočítá do součtu – protože je užitečné vědět, kolik práce se do klienta doopravdy vlilo.

## Jak se to používá

```
/invoicing preview          # co by se vystavilo
/invoicing full             # ostrý běh přes všechny klienty
/invoicing recover FAVI     # dohledání zapomenutého času u jednoho klienta
```

## Ukázka výstupu

Kontrola před vystavením, klient po klientovi:

```
FAVI   2026-08-01 – 2026-08-31   18,5 h × <sazba> = <částka>
Doklad:    vystavení 2026-08-31, DUZP 2026-08-31, splatnost 2026-09-14
Položka:   Konzultace a implementace webové analytiky – 18,5 h
Vyřazeno:  2 záznamy označené jako nefakturovatelné (1,25 h)
K rozhodnutí: záznam 12. 8. bez popisu (2 h)
```

## Co nedělá

- **Neodesílá maily. Nikdy.** Končí draftem.
- **Neúčtuje.** Nehlídá úhrady, upomínky ani daňové termíny. Vystaví doklad a tím jeho práce končí.
- **Netrackuje čas.** Dohledá ho a ukáže, zapsat si ho musíte sami.
- **Nedrží evidenci faktur** – zdrojem pravdy je fakturační systém, ne soubor v repozitáři.

## Jak si ho nainstalovat

Nechte to na Claudovi. Otevřete si Claude Code a napište mu:

> Jdi na https://github.com/jantichy/claude/tree/main/skills/invoicing a nainstaluj mi ten skill k sobě do `~/.claude/skills/`.

Tím to ale nekončí: **sám o sobě skill neběží**, je to rámec bez pravidel. Sazby, daňový režim, dohody s jednotlivými klienty, šablonu mailu i to, jak se sahá do vašich systémů, drží samostatná soukromá knowledge base, která v tomhle repozitáři není – bez ní skill nemá podle čeho fakturovat a rovnou to řekne. Vzít si odsud jde postup a pojistky, ne hotová konfigurace; **nechte si od Clauda tu svou bázi založit podle toho, jak fakturujete vy**.

---

### Požadavky a omezení

Přístup k timetrackingu, k fakturačnímu systému a k mailu – ideálně přes jejich napojení na Clauda, jinak přes jejich rozhraní. Vlastní knowledge base s pravidly fakturace. Skill je psaný pro český daňový režim (datum uskutečnění plnění, lhůta na vystavení dokladu, náležitosti podle zákona o DPH). Součástí je pomocný program pro čtení kalendáře, který funguje jen na macOS.
