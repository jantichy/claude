"""Regresní testy kontroly odkazů, kterou `/cleanup` pouští před čtenáři bez kontextu.

Skript `skills/cleanup/scripts/links.py` existuje kvůli pravidlu nula
(`~/.claude/RULES.md`, *Model a effort podle úkolu*): rozbitý odkaz a mrtvá kotva
jsou mechanické vady a hledat je čtením přes model je ta nejdražší možná cesta.
Skript je tedy **zrychlení** – část práce, kterou dřív dělal agent, se udělá
za zlomek vteřiny a agentovi zbude úsudek.

Testují se oba směry selhání, protože u vynucovací vrstvy je ten druhý horší:

- **propustí, co nemá** – rozbitý odkaz nebo mrtvá kotva projde a `/cleanup`
  ohlásí čisto, které neplatí;
- **zastaví, co nemá** – falešný poplach nad správným textem. Ten se neprojeví
  jako díra, ale jako otrava při běžné práci, a otravnou kontrolu si člověk
  vypne. Nejbohatší zdroj falešných poplachů jsou **bloky kódu**: skilly v tomhle
  repozitáři nesou šablony výstupu, které začínají řádkem `## Úklid dokončen`,
  a ukázky odkazů se zástupnými symboly. Nadpis uvnitř bloku kódu nadpis
  dokumentu není a odkaz uvnitř něj není odkaz.

Nad hlavním scénářem stojí **mutační test**: vyřadí vynechávání bloků kódu
a ověří, že falešný poplach opravdu vznikne. Bez něj by hlavní test zůstal
zelený i tehdy, kdyby ticho nad blokem kódu vznikalo z docela jiného důvodu.

Spouští se: python3 -m unittest discover -s tests -q

Jen stdlib.
"""
import importlib.util
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINKS = ROOT / "skills" / "cleanup" / "scripts" / "links.py"


def load(path, name):
    """Naimportuje modul z cesty – používá se i pro zmutovanou kopii skriptu."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Fixture(unittest.TestCase):
    """Dočasný projekt se dvěma Markdowny; `a.md` se v každém testu přepisuje."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        (self.dir / "b.md").write_text("# Béčko\n\n## Druhý nadpis\n", encoding="utf-8")
        self.addCleanup(self.tmp.cleanup)

    def write(self, body):
        path = self.dir / "a.md"
        path.write_text(textwrap.dedent(body), encoding="utf-8")
        return path

    def findings(self, body):
        """Nálezy nad `a.md` jako jeden řetězec, ať se dá hledat podřetězec."""
        module = load(LINKS, "links_under_test")
        return "\n".join(module.check([str(self.write(body))]))


class NajdeVady(Fixture):
    """Směr „propustí, co nemá“ – bez tohohle je zelený výsledek bezcenný."""

    def test_rozbity_odkaz_na_soubor(self):
        self.assertIn("neexistuje", self.findings("[x](chybi.md)\n"))

    def test_mrtva_kotva_v_cizim_souboru(self):
        self.assertIn("není nadpis", self.findings("[x](b.md#takovy-neni)\n"))

    def test_mrtva_kotva_ve_vlastnim_souboru(self):
        body = "# Nadpis\n\n[x](#takovy-neni)\n"
        self.assertIn("není nadpis", self.findings(body))

    def test_nadpis_v_bloku_kodu_neni_kotva(self):
        body = """\
            # Nadpis

            ```
            ## Šablona výstupu
            ```

            [x](#šablona-výstupu)
            """
        self.assertIn("není nadpis", self.findings(body))

    def test_hlasi_cislo_radku(self):
        body = "# Nadpis\n\nprvní\n\n[x](chybi.md)\n"
        self.assertIn(":5:", self.findings(body))


class NehlasiSpravne(Fixture):
    """Směr „zastaví, co nemá“ – falešný poplach je ta horší polovina."""

    def test_existujici_soubor(self):
        self.assertEqual("", self.findings("[x](b.md)\n"))

    def test_platna_kotva(self):
        self.assertEqual("", self.findings("[x](b.md#druhý-nadpis)\n"))

    def test_kotva_do_sebe(self):
        self.assertEqual("", self.findings("# Živá sekce\n\n[x](#živá-sekce)\n"))

    def test_kotva_s_diakritikou_v_procentech(self):
        """Odkaz zkopírovaný z prohlížeče nese kotvu URL-enkódovanou."""
        self.assertEqual("", self.findings("[x](b.md#druh%C3%BD-nadpis)\n"))

    def test_kotva_z_nadpisu_se_znackami(self):
        """Nadpis se sází s kódem a tučným písmem; slug je ignoruje."""
        (self.dir / "b.md").write_text("## `docs/plan.md` – **plán**\n", encoding="utf-8")
        self.assertEqual("", self.findings("[x](b.md#docsplanmd--plán)\n"))

    def test_odkaz_v_bloku_kodu(self):
        body = """\
            ```
            [x](vubec-nic.md)
            ```
            """
        self.assertEqual("", self.findings(body))

    def test_odkaz_v_bloku_kodu_s_vlnovkami(self):
        body = "~~~\n[x](vubec-nic.md)\n~~~\n"
        self.assertEqual("", self.findings(body))

    def test_vnoreny_plot_neukonci_blok_predcasne(self):
        """Blok otevřený vlnovkami snese uvnitř ohraničení apostrofy."""
        body = "~~~\n```\n[x](vubec-nic.md)\n```\n~~~\n"
        self.assertEqual("", self.findings(body))

    def test_externi_a_absolutni_cile(self):
        body = (
            "[a](https://example.com/x.md) [b](mailto:kdo@example.com)\n"
            "[c](~/.claude/RULES.md) [d](/etc/hosts-neexistuje)\n"
        )
        self.assertEqual("", self.findings(body))

    def test_odkaz_na_adresar(self):
        (self.dir / "docs").mkdir()
        self.assertEqual("", self.findings("[x](docs)\n"))

    def test_kotva_do_neMarkdownu_se_neresi(self):
        """V HTML ani ve skriptu se nadpisy nehledají – jiná struktura."""
        (self.dir / "x.html").write_text("<h2>Cosi</h2>\n", encoding="utf-8")
        self.assertEqual("", self.findings("[x](x.html#cosi)\n"))


class Rozhrani(Fixture):
    """Návratové kódy – podle nich se skill rozhoduje, jestli pokračovat."""

    def run_script(self, *args):
        return subprocess.run(
            [sys.executable, str(LINKS), *args],
            capture_output=True, text=True, check=False,
        )

    def test_cisto_vraci_nulu(self):
        done = self.run_script(str(self.write("[x](b.md)\n")))
        self.assertEqual(0, done.returncode, done.stdout + done.stderr)
        self.assertIn("v pořádku", done.stdout)

    def test_nalez_vraci_jednicku(self):
        done = self.run_script(str(self.write("[x](chybi.md)\n")))
        self.assertEqual(1, done.returncode)
        self.assertIn("chybi.md", done.stdout)

    def test_bez_argumentu_vraci_dvojku(self):
        """Prázdné volání je chyba, ne „čisto“ – jinak by mlčky prošlo."""
        self.assertEqual(2, self.run_script().returncode)

    def test_neprecteny_soubor_je_nalez(self):
        done = self.run_script(str(self.dir / "takovy-neni.md"))
        self.assertEqual(1, done.returncode)
        self.assertIn("nelze přečíst", done.stdout)


class Mutace(Fixture):
    """Ověří, že ticho nad blokem kódu vzniká vynecháním bloků, ne náhodou."""

    def test_bez_vynechani_bloku_vznikne_falesny_poplach(self):
        source = LINKS.read_text(encoding="utf-8").replace(
            "        mark = FENCE.match(line)",
            "        mark = None",
            1,
        )
        mutant = self.dir / "links_mutant.py"
        mutant.write_text(source, encoding="utf-8")
        body = "```\n[x](vubec-nic.md)\n```\n"
        findings = load(mutant, "links_mutant").check([str(self.write(body))])
        self.assertTrue(findings, "vyřazení vynechávání bloků kódu nic nezměnilo – "
                                  "test nad blokem kódu tedy neměří to, co tvrdí")


if __name__ == "__main__":
    unittest.main()
