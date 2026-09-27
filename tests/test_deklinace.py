"""Kontrolní sada vět pro převod pádů v `/replace`.

Sada vznikla z revize jednoho velkého českého přejmenování: jsou to věty, které
tehdy vyšly špatně, takže hlídá, že se úpravy pravidel navzájem neruší.

**Leží tady, a ne u skriptů ve skillu, protože kontrakt `test` pouští jen
`tests/`.** Do 28. 9. 2026 stála uvnitř `/replace` a nespouštěl ji nikdo – dvě
věty v ní padaly a nikdo se to nedozvěděl. Že tam žádná znovu nevznikne, hlídá
`test_skills.py`.

**Dvě věty rozhodnout nejdou a stojí proto ve `LIMITS`**, ne v pádu testu.
Nejednoznačné jsou i pro člověka: *partie* má shodný tvar v 1. pádě jednotného
i množného čísla a *partii* ve 4. i 6. pádě, takže věta sama o tvaru informaci
nenese. V textu se opravily ručně. Seznam se **porovnává se skutečností
v obou směrech**: věta, která mez přežila a dnes prochází, shodí testy stejně
jako nová vada – jinak by seznam jen narůstal a „schválně červený“ test nechrání
nic, protože nemůže zezelenat.

Jen stdlib.
"""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULE = ROOT / "skills" / "replace" / "deklinace" / "deklinace.py"

SPEC = importlib.util.spec_from_file_location("deklinace", MODULE)
D = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(D)

CASES = [
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

LIMITS = {
    # 1. pád j. č. i mn. č. mají shodný tvar a `neplatí` taky – číslo z věty nejde
    'partie v předregistraci nebo na čekací listině se neplatí',
    # `na partii` je 4. i 6. pád; rozhodla by tabulka vazeb sloves (`ozvat se na`)
    'ozvala by se až na první partii',
}


class Cases(unittest.TestCase):
    """Převod pádů na kontrolní sadě vět, mimo dvě doložené meze."""

    def results(self):
        return [(sentence, expected, expected in D.convert(sentence))
                for sentence, expected in CASES]

    def test_sentences_outside_limits_convert(self):
        wrong = [f'{sentence!r}\n   čekáno {expected!r}, vyšlo: {D.convert(sentence)!r}'
                 for sentence, expected, ok in self.results()
                 if not ok and sentence not in LIMITS]
        if wrong:
            self.fail(f'{len(wrong)} z {len(CASES)} vět špatně:\n' + '\n'.join(wrong))

    def test_limits_still_fail(self):
        """Mez, která přežila svůj důvod, je horší než žádná – seznam musí sedět."""
        stale = [sentence for sentence, _, ok in self.results()
                 if ok and sentence in LIMITS]
        self.assertEqual(stale, [], 'tyhle věty už procházejí – vyškrtni je z LIMITS')

    def test_limits_name_real_sentences(self):
        known = {sentence for sentence, _ in CASES}
        self.assertEqual(LIMITS - known, set(),
                         'LIMITS jmenuje věty, které v sadě nejsou')


if __name__ == '__main__':
    unittest.main(verbosity=2)
