# Převod pádů při českém přejmenování

Nástroj, který vznikl 19. 9. 2026 při přejmenování „partie“ na „podobjednávka“ v rezervačním systému – 3 821 výskytů v 18 dokumentech. Leží tady jako **východisko a doklad metody**, ne jako hotový nástroj: pravidla i slovní zásoba jsou psané na jednu dvojici slov a pro jinou dvojici se musí přepsat.

## Proč to nešlo hromadnou náhradou

České podstatné jméno má v textu sedm pádů a dvě čísla, ale **tvarů je míň než kombinací** – `partii` je 3., 4. i 6. pád. Druhé slovo je skloňuje jinak, takže `sed` by tiše vyrobil chybu v každé druhé větě.

## Na čem to stojí

1. **Rod obou slov.** Shodují-li se, nemění se přívlastky, příčestí ani shoda – mění se jen samotné podstatné jméno. Liší-li se rod, je tahle metoda k ničemu a přejmenování je řádově větší práce.
2. **Tvary se slévají.** U dvojice partie → podobjednávka zbyla tři binární rozhodnutí místo šesti pádů: `podobjednávka`/`podobjednávky`, `podobjednávce`/`podobjednávku`, `podobjednávkou`/`podobjednávek`.
3. **Uzavřený seznam funkčních slov.** Seznam podstatných jmen, po kterých následuje 2. pád, je principiálně otevřený; seznam spojek, částic a pomocných sloves není. Stojí-li vlevo něco mimo ten seznam, je to skoro vždy podstatné jméno – a tedy 2. pád jednotného čísla.
4. **Přívlastek vlevo je silnější signál než přísudek vpravo.** Opačné pořadí znamená, že „u zaplacené partie **je** doklad“ dostane 1. pád; projevilo se to na 80 místech naráz.

## Soubory

| Soubor | Co dělá |
|---|---|
| `deklinace.py` | pravidla převodu; `convert(text, report, path)` vrací text a do `report` seznam rozhodnutí s příznakem jistoty |
| `prepis.py` | průchod soubory s **chráněnými úseky** (místa, kde je slovo předmětem řeči) a zdrojem z `git show HEAD:`, takže běh jde opakovat bez zahazování rozdělané práce |
| `test_deklinace.py` | kontrolní sada vět vytažených z revize; hlídá, že se úpravy pravidel navzájem neruší |

## Doložená mez, kvůli které tu tenhle text je

Převod označil 3 294 míst za jistá a 528 za nejistá. **Nejistá se přečetla ručně, jistá ne** – a právě mezi nimi zůstalo 16 chyb jediné třídy, které našel až čtenář bez kontextu v `/cleanup`: tvar 7. pádu jednotného čísla („nad existující partií“) se převedl na 2. pád množného.

**Poučení tedy nezní „číst pozorněji“.** U převodu, kde se rozhoduje mezi dvěma tvary, se musí **prohledat obě strany každého rozhodnutí** – tedy i to, co nástroj prohlásil za jisté. Kontrolní sada vět to nechytí, protože testuje jen věty, na které někdo pomyslel; hledání nesouhlasu přívlastku napříč dokumentací ano.

Rozbor konkrétního běhu drží `~/Dev/rezervace/main/docs/decisions.md`, §121.
