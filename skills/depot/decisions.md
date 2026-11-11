# Rozhodnutí – /depot

Soubor drží rozvahu a doklady skillu `/depot`; za běhu skillu se nečte.

### Zdroj drží ochranu rozsahu jiným nástrojem než výčet cest

**Rozhodnuto 22. 9. 2026.** Do té doby nesl ochranu rozsahu výčet cest a skill do žádného adresáře sám nesměl. Se zdrojem jako proudem ji nesou výčet míst v doméně, interval a čára. Pět tisíc položek z původního srovnávacího běhu (agent bez skillu si rozsah rozšířil ze dvou předaných souborů na celé `~/Downloads`) leží v podsložkách, které doména nejmenuje, a pod čárou – do rozsahu se tedy nedostanou. **Nejde o zmírnění pravidla:** kdo by ho při revizi vracel k výčtu cest, zruší zdroj, ne díru.

### Připojení dokumentu do uloženého souboru je výjimka z „nesahá na uložené“, ne kolize

**Rozhodnuto 11. 11. 2026.** Doména může chtít, aby víc dokumentů k jedné věci leželo v jednom souboru – typicky objednávka, zálohovka a faktura k jednomu nákupu, které přicházejí s odstupem dní. Skill dřív na uložený soubor nesahal a do koše posílal jen ověřený duplikát, takže pozdější doklad šel buď vedle jako druhý soubor, nebo se každý běh zastavil na kolizi. **Zavrženo:** ukládat pozdější doklad vedle s příponou v názvu – rozpadne se tím to, co doména chce mít pohromadě; a nechat to jako obyčejnou kolizi s dotazem – ptal by se pokaždé na věc, kterou pravidlo už rozhodlo. **Pojistky místo zákazu:** připojení musí stát v potvrzeném plánu, cíl musí být verzovaný a spojený soubor se před nahrazením ověří proti všem dokumentům; připojený originál jde do koše, ne přes `rm`.
