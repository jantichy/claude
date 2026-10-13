"""Regresní testy kontroly pořadí datovaných záznamů (`skills/order.py`).

Kontrola existuje proto, že norma *Nejstarší nahoře* se sama nedodržuje.
`~/.claude/standards/structure.md` ji žádá u `done.md` i `decisions.md`, ruční srovnání
se od 6. 9. 2026 dělalo **třikrát** a pokaždé se to vrátilo – zapisují tam
skilly samy a každý se řídí tím, co v souboru zrovna vidí, takže jeden
obrácený zápis stačí, aby ho další napodobily.

Testují se **oba směry selhání**. Že kontrola nález ohlásí, je ta zjevná
polovina; falešný poplach je ta horší, protože se neprojeví jako díra, ale
jako překážka v běžné práci – a překážku si člověk při první kolizi vypne.
Proto se hlídá, že datum ve vnořené poznámce, v bloku kódu ani pokles mezi
dvěma sekcemi nálezem není.

Nad tím stojí **vynucení nad skutečnými soubory** tohohle repozitáře: bez něj
by kontrola existovala, ale nikdo by ji nepouštěl, a pořadí by se rozpadlo
počtvrté úplně stejně.

Spouští se: python3 -m unittest discover -s tests -q
"""

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills" / "order.py"


def load():
    spec = importlib.util.spec_from_file_location("order", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RepositoryFilesStayOrdered(unittest.TestCase):
    """Vrstva, která to vynucuje. Kontrola bez tohohle testu nehlídá nic."""

    def test_done_and_decisions_are_ascending(self):
        run = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(ROOT / "docs" / "done.md"),
                str(ROOT / "docs" / "decisions.md"),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)


class Findings(unittest.TestCase):
    def setUp(self):
        self.order = load()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def write(self, text):
        path = Path(self.tmp.name) / "soubor.md"
        path.write_text(text, encoding="utf-8")
        return str(path)

    def test_descending_records_are_reported(self):
        path = self.write(
            "## Hotovo\n\n- **2026-09-28** · nové\n- **2026-09-27** · starší\n"
        )
        [finding] = self.order.check([path])
        self.assertIn("Hotovo", finding)
        self.assertIn("2026-09-27", finding)

    def test_ascending_records_are_clean(self):
        path = self.write(
            "## Hotovo\n\n- **2026-09-27** · starší\n- **2026-09-28** · nové\n"
        )
        self.assertEqual(self.order.check([path]), [])

    def test_same_date_twice_is_not_a_finding(self):
        """Za den vznikne víc zápisů a jejich vzájemné pořadí norma neřeší."""
        path = self.write(
            "## Hotovo\n\n- **2026-09-28** · první\n- **2026-09-28** · druhý\n"
        )
        self.assertEqual(self.order.check([path]), [])

    def test_date_below_a_record_is_not_a_record(self):
        """Vnořená poznámka pod záznamem nese datum toho, co se stalo, ne zápisu.

        Sekce *Odvedená práce* má pod záznamy odstavce, které odkazují na
        starší události. Kdyby se braly za záznamy, hlásila by kontrola
        prakticky každý blok a nikdo by ji nedočetl.
        """
        path = self.write(
            "## Hotovo\n\n- **2026-09-27** · starší\n\n  Navazuje na 2026-09-02.\n\n"
            "- **2026-09-28** · nové\n"
        )
        self.assertEqual(self.order.check([path]), [])

    def test_code_fence_is_ignored(self):
        """Ukázka zápisu v bloku kódu není záznam – šablony skillů je mají."""
        path = self.write(
            "## Hotovo\n\n- **2026-09-27** · starší\n\n```\n- **2026-09-01** · ukázka\n```\n\n"
            "- **2026-09-28** · nové\n"
        )
        self.assertEqual(self.order.check([path]), [])

    def test_sections_are_counted_apart(self):
        """Každá sekce má vlastní řadu; pokles na hranici sekcí není vada."""
        path = self.write(
            "## První\n\n- **2026-09-28** · nové\n\n## Druhá\n\n- **2026-09-02** · staré\n"
        )
        self.assertEqual(self.order.check([path]), [])

    def test_headings_are_records_too(self):
        """Nadpis s ISO datem je záznam – tak píše `skills/ptydepe/terms.md`."""
        path = self.write(
            "### 2026-09-28 – nové\n\ntext\n\n### 2026-09-27 – starší\n\ntext\n"
        )
        self.assertEqual(len(self.order.check([path])), 1)

    def test_decided_date_under_heading_counts(self):
        """Datum patří do prvního odstavce (`structure.md`, *`decisions.md`*), ne do nadpisu.

        Bez čtení úvodního `**Rozhodnuto …**` by se nadpis bez data přeskočil
        a kontrola nad takovým `decisions.md` tiše nehlídala nic.
        """
        path = self.write(
            "### Nové\n\n**Rozhodnuto 28. 9. 2026.** text\n\n"
            "### Starší\n\n**Rozhodnuto 27. 9. 2026.** text\n"
        )
        self.assertEqual(len(self.order.check([path])), 1)

    def test_decided_date_in_order_passes(self):
        path = self.write(
            "### Starší\n\n**Rozhodnuto 2. 9. 2026.** text\n\n"
            "### Nové\n\n**Rozhodnuto 15. 9. 2026.** text\n"
        )
        self.assertEqual(self.order.check([path]), [])

    def test_czech_date_elsewhere_is_ignored(self):
        """České datum mimo úvod záznamu dál nic neznamená – odkazuje na událost, ne na zápis."""
        path = self.write(
            "- **2026-09-01** · úvodní záznam, ať soubor není bez dat\n\n"
            "### Nové\n\nText, který zmiňuje 28. 9. 2026.\n\n"
            "### Starší\n\n**Upřesněno 27. 9. 2026.** text\n"
        )
        self.assertEqual(self.order.check([path]), [])

    def test_level_two_heading_with_italic_date_is_a_record(self):
        """Rozhodnutí jako `## ` s `*D. M. RRRR*` pod sebou je záznam, ne sekce.

        Bez toho měl každý takový nadpis sekci sám pro sebe a dva nové zápisy
        na začátku souboru před staršími prošly jako „v pořádku“.
        """
        path = self.write(
            "# Rozhodnutí\n\n## Nové\n\n*3. 10. 2026*\n\ntext\n\n"
            "## Také nové\n\n*3. 10. 2026*\n\ntext\n\n"
            "## Starší\n\n*27. 8. 2026*\n\ntext\n\n"
            "## Nejnovější\n\n*5. 10. 2026*\n\ntext\n"
        )
        [finding] = self.order.check([path])
        self.assertIn("2026-08-27", finding)
        self.assertIn("1 ×", finding)

    def test_level_two_headings_with_italic_date_in_order_pass(self):
        path = self.write(
            "# Rozhodnutí\n\n## Starší\n\n*27. 8. 2026*\n\ntext\n\n"
            "## Nové\n\n*3. 10. 2026*\n\ntext\n"
        )
        self.assertEqual(self.order.check([path]), [])

    def test_undated_subheading_of_a_record_does_not_split_the_scale(self):
        """Podnadpis uvnitř rozhodnutí (`### Zamítnuto`) nesmí oddělit rozhodnutí od sebe.

        Kolize obou oprav: `## ` s datem je záznam, nedatovaný `### ` hranice
        škály – ale jen tematická podsekce s datovanými záznamy pod sebou.
        """
        path = self.write(
            "## Nové\n\n*3. 10. 2026*\n\ntext\n\n### Zamítnuto\n\n- varianta\n\n"
            "## Starší\n\n*27. 8. 2026*\n\ntext\n"
        )
        self.assertEqual(len(self.order.check([path])), 1)

    def test_undated_record_does_not_split_the_scale(self):
        """Jeden zapomenutý `**Rozhodnuto …**` nesmí vyřadit z kontroly zbytek souboru."""
        path = self.write(
            "### Nové\n\n**Rozhodnuto 28. 9. 2026.** text\n\n"
            "### Bez data\n\ntext\n\n- **Zamítnuto:** varianta\n\n"
            "### Starší\n\n**Rozhodnuto 27. 9. 2026.** text\n"
        )
        self.assertEqual(len(self.order.check([path])), 1)

    def test_undated_subsections_are_separate_scales(self):
        """Tematické podsekce mají každá vlastní řadu; pokles přes jejich hranici není vada."""
        path = self.write(
            "## Hotovo\n\n- **2026-09-20** · nové\n- **2026-09-28** · novější\n\n"
            "### Archiv\n\n- **2026-08-01** · staré\n- **2026-08-15** · méně staré\n\n"
            "### Starší archiv\n\n- **2026-06-01** · nejstarší\n"
        )
        self.assertEqual(self.order.check([path]), [])

    def test_descending_inside_a_subsection_is_reported(self):
        path = self.write(
            "## Hotovo\n\n- **2026-09-28** · nové\n\n"
            "### Archiv\n\n- **2026-08-15** · méně staré\n- **2026-08-01** · staré\n"
        )
        [finding] = self.order.check([path])
        self.assertIn("podsekce *Archiv*", finding)
        self.assertIn("2026-08-01", finding)

    def test_file_without_dated_records_is_a_finding(self):
        """Nula záznamů znamená, že skript tvar nezná – mlčky projít nesmí."""
        path = self.write("# Rozhodnutí\n\n## Něco\n\n3. 10. 2026\n\ntext\n")
        [finding] = self.order.check([path])
        self.assertIn("žádný datovaný záznam", finding)

    def test_one_finding_per_section(self):
        """Jeden obrácený zápis nahoře nesmí vypsat celý soubor.

        Hlásit každý záznam pod dosud nejvyšším datem dá u padesátiřádkové
        sekce padesát nálezů – takový výstup nikdo nedočte a kontrola se
        přestane pouštět, čímž nehlídá nic.
        """
        path = self.write(
            "## Hotovo\n\n- **2026-09-28** · nové\n"
            + "".join(f"- **2026-09-{d:02}** · starší\n" for d in range(1, 20))
        )
        findings = self.order.check([path])
        self.assertEqual(len(findings), 1)
        self.assertIn("1 ×", findings[0])

    def test_unreadable_file_is_a_finding_not_a_crash(self):
        findings = self.order.check([str(Path(self.tmp.name) / "není.md")])
        self.assertEqual(len(findings), 1)
        self.assertIn("nelze přečíst", findings[0])


class ExitCodes(unittest.TestCase):
    """Skill se podle kódu rozhoduje, takže `2` se nesmí dát splést s čistotou."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def run_script(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args], capture_output=True, text=True
        )

    def test_no_arguments_is_usage_error(self):
        self.assertEqual(self.run_script().returncode, 2)

    def test_findings_return_one(self):
        path = Path(self.tmp.name) / "a.md"
        path.write_text(
            "## H\n\n- **2026-09-28** · a\n- **2026-09-01** · b\n", encoding="utf-8"
        )
        self.assertEqual(self.run_script(str(path)).returncode, 1)

    def test_no_dated_record_returns_one(self):
        """`/end` bere za čisto jedině `0`; soubor, který skript nepřečetl, čistý není."""
        path = Path(self.tmp.name) / "a.md"
        path.write_text("# H\n\n## Bez data\n\ntext\n", encoding="utf-8")
        run = self.run_script(str(path))
        self.assertEqual(run.returncode, 1)
        self.assertNotIn("v pořádku", run.stdout)

    def test_clean_returns_zero(self):
        path = Path(self.tmp.name) / "a.md"
        path.write_text(
            "## H\n\n- **2026-09-01** · a\n- **2026-09-28** · b\n", encoding="utf-8"
        )
        run = self.run_script(str(path))
        self.assertEqual(run.returncode, 0)
        self.assertIn("v pořádku", run.stdout)


class Mutation(unittest.TestCase):
    """Poškodí kontrolu a ověří, že nález opravdu vznikne z hlídaného důvodu.

    Bez toho by testy výš zůstaly zelené i tehdy, kdyby čisto vycházelo z docela
    jiné příčiny – třeba že se záznam nerozpozná vůbec.
    """

    def setUp(self):
        self.order = load()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_without_fence_skipping_the_code_block_becomes_a_finding(self):
        text = (
            "## Hotovo\n\n- **2026-09-27** · starší\n\n```\n- **2026-09-01** · ukázka\n```\n\n"
            "- **2026-09-28** · nové\n"
        )
        path = Path(self.tmp.name) / "a.md"
        path.write_text(text, encoding="utf-8")
        self.assertEqual(self.order.check([str(path)]), [])
        self.order.outside_fences = lambda t: list(enumerate(t.splitlines(), 1))
        self.assertEqual(len(self.order.check([str(path)])), 1)

    def test_without_scales_the_archive_becomes_a_finding(self):
        """Čisto u členěné sekce musí plynout z hranice škály, ne z nerozpoznání záznamů."""
        text = (
            "## Hotovo\n\n- **2026-09-28** · nové\n\n"
            "### Archiv\n\n- **2026-08-01** · staré\n"
        )
        path = Path(self.tmp.name) / "a.md"
        path.write_text(text, encoding="utf-8")
        self.assertEqual(self.order.check([str(path)]), [])
        self.order.opens_scale = lambda rows, start: False
        self.assertEqual(len(self.order.check([str(path)])), 1)


if __name__ == "__main__":
    unittest.main()
