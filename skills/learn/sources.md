# Netextové zdroje

Postup pro zdroje, které nejsou text – nahrávku, video, obrázek, PDF. Čte se z `SKILL.md`, *Fáze 1*, a platí jen tehdy, když takový zdroj na vstupu opravdu je.

## Obsah

- [Když je zdrojem nahrávka](#když-je-zdrojem-nahrávka)
- [Když je zdrojem obrázek nebo PDF](#když-je-zdrojem-obrázek-nebo-pdf)

## Když je zdrojem nahrávka

Zvukový i obrazový záznam je **platný vstup, ne důvod k odmítnutí** – všechny formáty, které bere `/transcript`. Nech si ho přepsat a dál pracuj s přepisem jako s kterýmkoliv jiným textem.

**Cíl urči dřív, než nahrávku pošleš na přepis.** Z cílové domény vytáhni jména, značky, nástroje a odborné termíny, které v záznamu nejspíš zazní, a předej je jako popis nahrávky – rozpoznávání pak nekomolí právě to, co báze už zná. **Vybírej, nesypej všechno:** slovník má technický strop daný modelem – jeho výši drží `/transcript`, který ho měřil – a při přetečení se uříznou termíny na začátku, a to tiše. Ber tedy to, co v nahrávce opravdu zazní a co se snadno komolí.

**Tři otázky průvodce `/transcriptu` si zodpověz sám a nahlas to oznam.** Je to jediné místo, kde tenhle skill mluví za uživatele, a smí to proto, že odpovědi plynou ze zadání, se kterým `/learn` běží – uživatel by na nich neměl co rozhodovat:

- **Vyčištěný doslovný přepis a nic dalšího.** Není to jen úspora času: shrnutí je tu škodlivé, protože co z hovoru vypustí, je přesně to, co má *Fáze 2* najít. **Řekni si o to výslovně** – bez volby vzniknou i shrnutí a časované titulky.
- **Rychlejší model rozpoznávání**, tedy výchozí volbu `/transcriptu`. Slovník z domény řeší právě to, kvůli čemu se po pomalejším sahá – komolená vlastní jména –, takže výrazně delší běh nemá co vyvážit.
- **Bez rozlišení mluvčích.** Samo se nezapne, ale ani o něj nežádej: vytěžuje se tvrzení, ne kdo je řekl, a do báze se poznatek stejně zapisuje bez identifikace osob (*Fáze 7*). Ušetří to minuty výpočtu i doinstalování závislostí.

**Je-li zdrojem video, zeptej se na obraz dřív, než pošleš zvuk na přepis.** `/transcript` bere jen zvukovou stopu, takže obsah, který zazněl jenom na slajdech, by propadl tiše. Jedna otázka přes `AskUserQuestion`, tři volby:

- **Přiložím slajdy** – vyžádej si cestu. Jsou to obrázky nebo PDF a vytěží se spolu s přepisem v jednom běhu; nedodá-li je hned, nech přepis běžet a počkej na ně před *Fází 2*.
- **Vytáhni je z videa** – vyřízni snímky při změně obrazu do **vlastního čerstvého adresáře** a přečti je jako obrázky:

  ```bash
  tmp=$(mktemp -d) && ffmpeg -i "<video>" -vf "select='gt(scene,0.3)'" -vsync vfr "$tmp/snimek-%03d.jpg"
  ```

  **Cesta ke zdroji je cizí vstup a uvozovkuje se vždy.** Jméno souboru pochází od toho, kdo ti nahrávku poslal – neuvozovkovaná cesta se zpětnými apostrofy nebo `$(…)` se v shellu rozvine dřív, než ffmpeg vůbec nastartuje. Ze stejného důvodu adresář **vyrob**, ne zvol: do cizího by ffmpeg přepsal stejnojmenné soubory a úklid by je pak vzal s sebou.

  Nevrátí-li to skoro nic, přepni na pevný interval (`fps=1/30`). **Vyjde-li snímků víc než pár desítek, nejdřív je prolistuj a zahoď opakované** – prezentace se vrací na tentýž slajd a číst ho popáté nepřidá nic, jen sní kontext. Po vytěžení smaž **celý ten adresář** (`rm -rf "$tmp"`), nikdy obsah adresáře, který jsi nevytvořil; na rozdíl od přepisu se ke snímkům nikdo nevrací.
- **Stačí zvuk** – vědomé rozhodnutí obraz zahodit. Zapiš ho do evidence zdroje (*Fáze 8*) jako nevytěženou část, ať je za rok vidět, že záznam nebyl vytěžený celý.

**Na cokoliv dalšího ať se `/transcript` ptá uživatele** – na jazyk, na hranici u dvojjazyčné nahrávky, na kolizi jmen i na existující přepis v adresáři. Ty odpovědi ze zadání `/learn` neplynou a tichá volba by u existujícího přepisu přepsala starší práci.

**Chybí-li nástroje, není to konec** – `/transcript` umí říct, co doinstalovat. **Přepis, který se nezdaří, ale konec je:** nevytěžuj z toho, co se přepsat podařilo, protože neúplný zdroj vypadá jako úplný a *Fáze 2* nemá jak poznat, že jí kus chybí. Je-li nahrávek víc a selže jen jedna, pokračuj ostatními a **řekni jmenovitě, která vypadla**.

**Přepis zůstane ležet vedle nahrávky** pod jejím jménem; mazat ho není co. Druhé vytěžení téhož záznamu, až doména vyroste, je nad textem zadarmo a nad audiem stojí celý přepis znovu.

**Leží-li nahrávka uvnitř cílové báze, nech si commit přepisu potvrdit.** Je to doslovný záznam hovoru se jmény, klientskými specifiky a osobními údaji, a v gitu zůstane natrvalo i po smazání souboru – řekni to nahlas a nabídni nechat přepis mimo bázi. Mnohá báze má navíc vlastní pravidlo, že syrové záznamy do repozitáře nepatří; **to má přednost** a pak se nepřesouvá ani necommituje nic.

Až po potvrzení přepis **commitni samostatně, ještě než sáhneš na obsah báze**. Tím zůstane v platnosti záruka z *Fáze 0*: cesta zpátky přes `git checkout` musí vést ke stavu před zásahem do znalostí, ne před přepisem.

## Když je zdrojem obrázek nebo PDF

**Obrázek i PDF jsou plnohodnotný zdroj** – ať přijdou samy (nafocený flipchart, screenshot, oskenovaný leták, slajdy v PDF), nebo jako příloha textového zdroje (slajdy ke školení, schéma v článku). **Přečti je a vytěž z nich poznatky stejně jako z textu** – přeskočit je znamená ztratit to, co je jenom v nich. Vytěžení samo se ničím neliší a řídí ho *Fáze 2* včetně kontroly úplnosti.

**Dlouhé PDF ber po blocích, ne namátkou.** Čtecí nástroj má strop na počet stran v jednom volání, takže dlouhý dokument se musí projít po částech a **je na tobě, aby se prošel celý** – měj u poznatků po ruce, ze které strany který je. Vzít z osmdesátistránkového dokumentu prvních pár desítek stran a tvářit se, že je vytěžený, je nejhorší možná varianta: chybějící znalost nemá kdo poznat, protože zdroj se tváří jako zpracovaný. Totéž platí pro kontrolu úplnosti – agentovi v *Fázi 2* předej celý rozsah, ne první blok.

**Do báze se ale nekopírují.** Znalostní báze je text: grepuje se, vytěžuje dalším během a přestavuje se v ní struktura – příloha, na kterou vede cesta, se při první přestavbě rozejde a její obsah nenajde nikdo. Nese-li obrázek nebo stránka vztah, který věta nezastane – schéma, tok, matice –, **překresli ho do Markdownu**: tabulkou, odrážkovou hierarchií nebo diagramem v `mermaid`.

**Co se překreslit nedá, se popíše a zdroj se ocituje.** Fotka obrazovky, graf s daty, sken rozhraní – z takového obrázku vytěž, co z něj plyne, a do evidence zdroje (*Fáze 8*) zapiš cestu k souboru, ať se dá dohledat. Do báze pak jde závěr, ne obrázek: kdo bude potřebovat originál, najde ho přes evidenci.
