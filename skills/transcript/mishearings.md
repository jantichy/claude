# Soustavné zkomoleniny

Zkomoleniny, které whisper dělá **opakovaně u kohokoliv**, kdo mluví o daném oboru. Čte se v kroku 3 při stavbě slovníku a doplňuje v kroku 10, než se pracovní slovník smaže.

**Proč to existuje:** slovník `.transcript-glossary.md` se staví pro každý běh znovu z promptu a kontextu projektu, a po dokončení se maže. Zkomolenina, kterou rozpoznávač dělá systematicky, se tak objevuje pořád dokola a pokaždé se na ni přijde znovu – nebo taky ne.

## Jak se to používá

- **Při stavbě slovníku (krok 3)** vezmi jen oddíl, který odpovídá oboru a jazyku nahrávky. Správné tvary z něj patří do `WHISPER_PROMPT` podle téhož klíče jako ostatní termíny: jak často zazní × jak snadno se komolí. **Do promptu jde správný tvar, nikdy zkomolenina** – té by se whisper naučil.
- **Při čištění (krok 9)** slouží jako seznam míst, kde se vyplatí dívat pozorně.
- **Při úklidu (krok 10)**, než smažeš pracovní slovník, sem přenes zkomoleniny, které se v běhu ukázaly jako **soustavné**, a řekni uživateli, že jsi to udělal.

## Co sem nepatří

- **Jednorázový přeslech.** Sem jde jen to, co rozpoznávač dělá systematicky, ne co se jednou nepovedlo kvůli šumu nebo přeřeknutí.
- **Interní žargon a jména konkrétní firmy.** Ta patří do slovníku jednoho běhu; tady by tahala cizí názvy do cizích přepisů.
- **Cokoliv, co se nedá rozhodnout bez kontextu.** Tabulka není seznam náhrad k mechanickému spuštění – rozhoduje vždy věta, ve které slovo stojí. Zvlášť u zkratek, kde se správný tvar liší podle oboru.

## PPC a webová analytika, čeština

Změřeno na hodinové konzultaci o PPC (14. 9. 2026).

| Whisper píše | Správně | Poznámka |
|---|---|---|
| T-Maxka, T-Max | PMax, PMaxka | Performance Max; skloňuje se česky |
| DSPčka | DSAčka | Dynamic Search Ads. **Rozhoduje kontext:** DSP je programatický nákup a existuje taky |
| TPC | CPC | cena za proklik |
| target CPI | target CPA | CPI (cena za instalaci) je z mobilních aplikací, v lead genu nedává smysl |
| nepíklíčíčkář, pípíčkář | PPCčkař | |
| PPTčkám | PPC | |
| výdy | leady | |
| food chase | purchase | konverzní akce v Google Ads |
| kůkino | cookie | |
| srč, sreč | search | vyhledávací kampaně |
| dispely, dispeje | display | displejová síť |
| ESP | USP | unique selling proposition |
| na slepot | naslepo | |
| kampáň | kampaň | |
