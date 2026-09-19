# -*- coding: utf-8 -*-
"""Kontrolní sada vět, které při revizi převodu vyšly špatně."""
import sys, unittest
sys.path.insert(0, '/private/tmp/claude-501/-Users-honza-Dev-rezervace/ddbf121e-d275-4737-82cc-8e7489edcb16/scratchpad')
import deklinace as D

PRIPADY = [
    ('Partie, které se rovnou potvrzují, dostanou zvolenou kartu.', 'Podobjednávky'),
    ('partie v předregistraci nebo na čekací listině se neplatí', 'podobjednávky'),
    ('plnění jedné její partie bylo v režimu OSS', 'podobjednávky'),
    ('Tady se navíc partie nevrací do NEW', 'podobjednávka'),
    ('a teprve pak jde partie obnovit', 'podobjednávka'),
    ('jinak by partie ukazovala na doklad', 'podobjednávka'),
    ('Nově je partie jedna, takže se to rozhodnutí nekoná', 'podobjednávka'),
    ('skutečnosti, ve které se partie nachází', 'podobjednávka'),
    ('zálohovka nebo faktura, nejen partie bez dokladu', 'podobjednávka'),
    ('Založí objednávku a její partie.', 'podobjednávky'),
    ('Platí pro každý seznam – partie, účastníky, akce i další', 'podobjednávky'),
    ('zmizí s objektem | partie, jejich doklady, dobropisy a účastníci', 'podobjednávky'),
    ('Partie, které se kvůli zrušení nemají vymáhat, patří do seznamu', 'Podobjednávky'),
    ('které mají navržené schéma – partie, účastníky, akce, kategorie', 'podobjednávky'),
    ('Vstupní stav každé partie určuje server', 'podobjednávky'),
    ('Partie a doklad mají každý své číslo', 'Podobjednávka'),
    ('Partie bez položek podmínku nesplňuje', 'Podobjednávka'),
    ('partie s mixem režimů se při vzniku rozdělí', 'podobjednávka'),
    ('protože partie bez dokladu už zákazníkovi ukázala cenu', 'podobjednávka'),
    ('od první partie. Do počitadla se nepočítá', 'podobjednávky'),
    ('za všechny její partie: stránka objednávky, doklady', 'podobjednávky'),
    ('Do kterého stavu spadnou její partie', 'podobjednávky'),
    ('Pořadatel má partie. Zahodit jde jen prázdný', 'podobjednávky'),
    ('cena partie je vyšší', 'podobjednávky'),
    ('u partie 12345/1 chybí doklad', 'podobjednávky'),
    ('Smazaná partie je pryč', 'podobjednávka'),
    ('tím by partie znovu dostala tytéž osy', 'podobjednávka'),
    ('takže partie přes víc akcí se sčítá', 'podobjednávka'),
    ('Kdyby se sčítaly celé partie, dostal by se do prahu', 'podobjednávky'),
    ('návodem, jak založit první partii', 'podobjednávku'),
    ('ozvala by se až na první partii', 'podobjednávku'),
    ('nechat ji na partii – táž hodnota', 'podobjednávce'),
    ('Mail patří objednávce, ne partii', 'podobjednávce'),
    ('rozdělit existující partii znamená rozhodnout', 'podobjednávku'),
    ('Vezme partii a zamkne ji', 'podobjednávku'),
    ('Na partii leží doklad', 'podobjednávce'),
    ('Mail za víc partií', 'podobjednávek'),
    ('Se smazanou partií nic', 'podobjednávkou'),
    ('Nad partiemi stojí objednávka', 'podobjednávkami'),
    ('Ve třech partiích', 'podobjednávkách'),
    ('Objednávka se skládá z partií', 'podobjednávek'),
    ('Guard se nastaví všem partiím', 'podobjednávkám'),
    ('Partiový kontext placeholderů', 'Podobjednávkový'),
    ('16 partiových, 4 objednávkové', 'podobjednávkových'),
]

class PrevodPadu(unittest.TestCase):
    def test_pady(self):
        chyby = []
        for veta, ocekavano in PRIPADY:
            vysledek = D.convert(veta)
            if ocekavano not in vysledek:
                chyby.append(f'{veta!r}\n   čekáno {ocekavano!r}, vyšlo: {vysledek!r}')
        if chyby:
            self.fail(f'{len(chyby)} z {len(PRIPADY)} vět špatně:\n' + '\n'.join(chyby))

if __name__ == '__main__':
    unittest.main(verbosity=2)
