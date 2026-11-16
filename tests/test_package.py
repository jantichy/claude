"""Testy skriptu `/package`, který hledá odkazy ven z balíčku.

Balíček odchází k cizímu člověku a odkaz, který vede na autorův disk, se tam projeví
až při instalaci – nebo vůbec ne, když Claude příjemce cestu potichu přeskočí. Kontrola
proto musí hlásit každou absolutní cestu, každý relativní odkaz bez cíle uvnitř balíčku
a soubor s vyhrazeným jménem, a zároveň propustit čistý balíček, jinak ji skill začne
obcházet jako falešný poplach.

Spouští se: python3 -m unittest discover -s tests -q
"""

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills" / "package" / "refs.py"


def load():
    spec = importlib.util.spec_from_file_location("package_refs", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Check(unittest.TestCase):
    def setUp(self):
        self.refs = load()
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name) / "home"
        (self.home / ".claude" / "skills" / "compose").mkdir(parents=True)
        (self.home / ".claude" / "skills" / "compose" / "SKILL.md").write_text("x")
        (self.home / ".claude" / "agents").mkdir()
        (self.home / ".claude" / "agents" / "reader.md").write_text("x")
        self.refs.HOME = self.home
        self.refs.CLAUDE = self.home / ".claude"
        self.pkg = Path(self.tmp.name) / "pkg"
        (self.pkg / "skill" / "rules").mkdir(parents=True)
        (self.pkg / "skill" / "rules" / "text.md").write_text("# Pravidla\n")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, text, name="skill/SKILL.md"):
        (self.pkg / name).write_text(text, encoding="utf-8")

    def kinds(self, terms=()):
        return {
            (f["kind"], f["target"]) for f in self.refs.check(self.pkg, list(terms))
        }

    def test_cisty_balicek_projde(self):
        self.write(
            "Pravidla jsou v [`rules/text.md`](rules/text.md) a v `rules/text.md`.\n"
        )
        self.assertEqual(self.kinds(), set())

    def test_absolutni_cesta_se_hlasi_v_kazdem_tvaru(self):
        self.write(
            "Čti `~/Context/Text/text.md`.\n"
            "Nebo /Users/honza/Context/x.md a C:\\Users\\jana\\.claude\\skills\\.\n"
            "Případně %USERPROFILE%\\.claude\\agents\\.\n"
        )
        targets = {t for k, t in self.kinds() if k == "absolute"}
        self.assertIn("~/Context/Text/text.md", targets)
        self.assertTrue(any(t.startswith("/Users/honza/") for t in targets))
        self.assertTrue(any(t.startswith("C:\\Users\\jana") for t in targets))
        self.assertTrue(any(t.startswith("%USERPROFILE%") for t in targets))

    def test_install_smi_jmenovat_obecna_mista_claude_code(self):
        self.write(
            "Skill patří do `~/.claude/skills/`, na Windows `%USERPROFILE%\\.claude\\skills\\`.\n",
            name="INSTALL.md",
        )
        self.assertEqual(self.kinds(), set())

    def test_install_nesmi_jmenovat_konkretni_cestu(self):
        self.write(
            "U autora to leží v `~/Context/Text/` a `~/.claude/skills/proofread/rules/`.\n",
            name="INSTALL.md",
        )
        self.assertEqual(
            {t for k, t in self.kinds() if k == "absolute"},
            {"~/Context/Text/", "~/.claude/skills/proofread/rules/"},
        )

    def test_obecne_misto_mimo_install_se_hlasi(self):
        self.write("Pravidla jsou v `~/.claude/skills/`.\n")
        self.assertIn(("absolute", "~/.claude/skills/"), self.kinds())

    def test_relativni_odkaz_bez_cile_se_hlasi(self):
        self.write("Viz [`briefs.md`](briefs.md) a `rules/copy.md`.\n")
        self.assertEqual(
            self.kinds(),
            {("unresolved", "briefs.md"), ("unresolved", "rules/copy.md")},
        )

    def test_odkaz_mimo_balicek_se_hlasi_i_kdyz_cil_existuje(self):
        outside = Path(self.tmp.name) / "outside.md"
        outside.write_text("x")
        self.write("Viz [tam](../../outside.md).\n")
        self.assertIn(("unresolved", "../../outside.md"), self.kinds())

    def test_webovy_odkaz_a_kotva_se_nehlasi(self):
        self.write("Viz [web](https://example.com/a.md) a [sekci](#pravidla).\n")
        self.assertEqual(self.kinds(), set())

    def test_skill_mimo_balicek_se_hlasi_zabaleny_ne(self):
        self.write("Hlas drží `/compose`, korekturu `/skill-v-baliku`.\n")
        (self.pkg / "skill-v-baliku").mkdir()
        (self.pkg / "skill-v-baliku" / "SKILL.md").write_text("x")
        self.assertEqual(self.kinds(), {("skill", "compose")})

    def test_zabaleny_skill_se_nehlasi(self):
        (self.pkg / "compose").mkdir()
        (self.pkg / "compose" / "SKILL.md").write_text("x")
        self.write("Hlas drží `/compose`.\n")
        self.assertEqual(self.kinds(), set())

    def test_vlastni_typ_agenta_se_hlasi(self):
        self.write("Pusť agenta typu `reader`.\n")
        self.assertEqual(self.kinds(), {("agent", "reader")})

    def test_vyhrazene_jmeno_souboru_se_hlasi_bez_ohledu_na_velikost(self):
        self.write("x", name="skill/agents.md")
        self.assertIn(("reserved", "agents.md"), self.kinds())

    def test_zadane_slovo_se_hleda_jen_na_zacatku_slova(self):
        self.write("Firma prohlašuje, že Rohlík doručuje.\n")
        found = [f for f in self.refs.check(self.pkg, ["rohl"]) if f["kind"] == "term"]
        self.assertEqual(len(found), 1)

    def test_zadane_slovo_se_hlasi_bez_ohledu_na_velikost(self):
        self.write("Psaní Honzovým hlasem.\n")
        self.assertEqual(self.kinds(["honz"]), {("term", "honz")})


class Scan(unittest.TestCase):
    def setUp(self):
        self.refs = load()
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name)
        self.refs.HOME = self.home
        self.refs.CLAUDE = self.home / ".claude"
        (self.home / "Context" / "Text").mkdir(parents=True)
        (self.home / "Context" / "Text" / "text.md").write_text("x")
        self.src = self.home / ".claude" / "skills" / "demo"
        self.src.mkdir(parents=True)
        (self.src / "briefs.md").write_text("x")

    def tearDown(self):
        self.tmp.cleanup()

    def test_najde_absolutni_i_relativni_odkaz_a_pozna_existenci(self):
        (self.src / "SKILL.md").write_text(
            "Pravidla `~/Context/Text/text.md`, chybí `~/Context/Nic/x.md`.\n"
            "Zadání [`briefs.md`](briefs.md), chybí `missing.md`.\n",
            encoding="utf-8",
        )
        found = {
            (r["kind"], r["target"], r["exists"]) for r in self.refs.scan([self.src])
        }
        self.assertLessEqual(
            {
                ("path", "~/Context/Text/text.md", True),
                ("path", "~/Context/Nic/x.md", False),
                ("relative", "briefs.md", True),
                ("relative", "missing.md", False),
            },
            found,
        )


if __name__ == "__main__":
    unittest.main()
