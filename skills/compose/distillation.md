# Destilace znalostní báze

Postup pro režim `profile`: jak se z archivu textů udělá popis hlasu, který se dá použít při psaní. Pouští se s tím `/compose profile`.

- [Co z archivu vzniká](#co-z-archivu-vzniká)
- [Pravidlo dokladu](#pravidlo-dokladu)
- [Analýza korpusu](#analýza-korpusu)
- [Syntéza](#syntéza)
- [Zlatý fond](#zlatý-fond)
- [Slepý test](#slepý-test)
- [Přírůstková profilace](#přírůstková-profilace)

------

## Co z archivu vzniká

Tři vrstvy. **Archiv je korpus – co bylo napsáno. Báze je norma – jak se píše.** Norma se opravuje, kdykoliv ji doklad vyvrátí; korpus se neopravuje nikdy.

```
báze/
  style.md              jádro: co platí napříč formáty
  article.md            profil formátu: dlouhý text
  post.md               profil formátu: příspěvek na sítě
  thread.md             profil formátu: vlákno
  article-examples.md   zlatý fond: odkazy do archivu
  post-examples.md      zlatý fond: celé texty
  thread-examples.md    zlatý fond: celá vlákna
  _analysis/            pracovní analýzy a záznam profilací
```

**Formáty si nevymýšlej.** Vycházejí z toho, co autor opravdu píše – kdo nikdy nepsal vlákno, profil vlákna nepotřebuje. Profil bez korpusu je vymyšlený.

**Cesty k dokladům se počítají od archivu.** Je to vnitřní konvence báze; odkaz mimo archiv se píše plnou cestou.

## Pravidlo dokladu

**Každé stylistické tvrzení nese cestu k souboru a doslovný úryvek.** Tvrzení bez dokladu je dojem a do báze nesmí.

Je to jediná pojistka proti tomu, aby destilace popsala obecnou představu o „dobrém psaní" místo tohohle autora. Model umí napsat věrohodný odstavec o něčím stylu, aniž by ten styl četl – a pozná se to až na hotovém textu, který zní jako každý jiný.

**Doklad musí být z archivu**, ne z paměti a ne z toho, co autor o sobě řekl v zadání.

## Analýza korpusu

Korpus se do kontextu nevejde. Rozděl ho **podle formátu**, ne podle let – ročníky téhož formátu se čtou pohromadě, protože vývoj v čase je jedno z toho, co se hledá. Části jsou na sobě nezávislé a **jedou souběžně**.

Každá vyrobí do `_analysis/` soubor s touhle strukturou:

```markdown
## Korpus
   co se přečetlo celé, co se vzorkovalo, co se vynechalo a proč
## Tone of voice a jazyk
   slovník, rytmus vět, typické obraty, humor a ironie
## Myšlenkové postupy
   jak autor vykládá, co předjímá, jak zjednodušuje bez ztráty korektnosti
## Formátová specifika
   stavba textu, délky, práce s odkazy, čísly a příklady
## Tematické režimy
   čím se liší odborný text od popularizace a od osobního
## Vývoj v čase
   čím se liší dnešní hlas od staršího a co už se nepoužívá
## Anti-patterny
   co autor nikdy nedělá, a kontrast vůči typickým AI manýrám
## Kandidáti do zlatého fondu
   texty s cestou, datem, tématem a jednou větou, čím jsou vzorové
```

**Nevejde-li se ani jedna část**, vzorkuj rovnoměrně napříč obdobím – nikdy ne první polovinu souboru. Začátky ročníků čtené dokola vyrobí obraz jednoho ročního období.

## Syntéza

Z analýz vzniká styl a profily formátů. Dělicí čára je ostrá:

| Patří do stylu | Patří do profilu formátu |
|---|---|
| slovník, rytmus, humor, vztah ke čtenáři | stavba textu, typické délky, členění |
| myšlenkové postupy a to, co autor předjímá | jak vypadá první věta a jak pointa |
| tematické režimy a jejich publikum | zvyklosti kanálu: odkazy, emoji, číslování |
| anti-patterny | ukázky formátu |

**Profil styl neopisuje, odkazuje na něj.** Dvě verze téhož pravidla se rozejdou a nikdo pak nepozná, která platí.

**Časové vážení promítni do normy, ne do průměru.** Normou je hlas posledních let; starší vrstvy slouží k doložení vývoje a jejich odložené polohy patří mezi anti-patterny. Bez toho vznikne průměr dvaceti let, kterým autor nikdy nepsal.

**Anti-patterny piš kontrolovatelně.** „Nezačíná text řečnickou otázkou" jde při self-checku ověřit; „píše autenticky" ne.

**Zapiš i horní mez.** Ustálené obraty a expresiva jsou to první, co se při napodobování přežene: v hotovém textu smí být každý nanejvýš jednou. Bez zapsané meze vznikne parodie – text hustší na charakteristické obraty, než jakýkoliv skutečný.

## Zlatý fond

Kurátorovaný výběr textů, které se při psaní čtou jako živý vzor. Ne „nejlepší texty", ale **nejvzorovější pro daný formát a téma**.

- **Dlouhé texty odkazem**, ne celé – cesta do archivu, datum, téma a věta, čím je text vzorový. Do kontextu se natáhne až ten, který se hodí k zadání.
- **Krátké texty a vlákna celé** přímo v souboru, včetně všech dílů vlákna. Načítat je jednotlivě z archivu se nevyplatí.
- **Rozsah:** desítky textů napříč formáty a tématy, vážené k poslední době.
- **Cesty ověř**, že existují. Zlatý fond, který ukazuje na přejmenovaný soubor, selže tiše: model si vzor prostě nenačte a napíše text bez něj.

## Slepý test

Báze bez slepého testu je hypotéza. Napiš podle ní tři texty – po jednom v každém formátu, různá témata – a nech autora u každého říct **„zní / nezní jako já"** s konkrétní výhradou: co přesně nesedí, jestli slovo, rytmus, stavba, nebo tón.

**Zadání i pointy musí přijít od autora.** Text s vymyšleným názorem test znehodnotí – autor bude odmítat obsah a bude to vypadat jako vada stylu.

Každou výhradu přelož na úpravu:

| Výhrada k | Míří do |
|---|---|
| hlasu, slovníku, rytmu | stylu – typicky nový anti-pattern nebo upřesnění |
| stavbě nebo délce | profilu formátu |
| tomu, že vzor sedí špatně | výměně textu ve zlatém fondu |

Opakuj, dokud autor neschválí všechny tři formáty. Průběh zapiš – příští profilace tím zjistí, co už se jednou zkoušelo.

## Přírůstková profilace

Druhý a další běh nestaví bázi znovu. Čte, co v archivu přibylo od poslední profilace, a ptá se u každého pozorování na jednu věc: **je to nové pravidlo, nebo protidoklad k tomu, které tam už je?**

- **Nové pravidlo** se přidá – s dokladem jako každé jiné.
- **Protidoklad** je cennější. Norma se opravuje, kdykoliv ji doklad vyvrátí; přepsané pravidlo ale **nemaž bez zeptání**, protože mohlo vzniknout z výhrady autora ve slepém testu, a ta v archivu nikde není. **Platí v obou režimech profilace – přírůstkové i celé.**
- **Jednorázová odchylka není pravidlo.** Jeden text napsaný jinak je doklad o jednom textu. Pravidlo se mění, až se odchylka opakuje.

**Přírůstek se nebere jen z archivu.** Připomínky, které autor rozdal k jednotlivým textům od minula, jsou taky vstup – a bývají přesnější než cokoliv, co jde vyčíst z korpusu.

**Na závěr zapiš do `_analysis/` záznam profilace:** datum, rozsah korpusu, ze kterého vyšla, a u každého zdroje počet zpracovaných textů. Je to jediné, podle čeho příští běh pozná, co je nové – bez něj zbývá jen celá destilace znovu, nebo hádání.
