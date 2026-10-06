"""Hlídá velikost souborů, které se načítají do každé session.

`~/.claude/rules/rules.md` za dvacet dní zdvojnásobil velikost a spolu s doménovými znalostmi
přetáhl limit, nad kterým Claude Code varuje, že instrukce zabírají příliš
kontextu. Pravidlo v textu růst nezastavilo, proto je mez tady. Spadne-li test,
uvolni místo nebo pravidlo přesuň do podmíněně načítaného souboru
(`.claude/CLAUDE.md`, *Co do `~/.claude/rules/rules.md` nepatří*); mez se nezvedá mimochodem.
"""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: Počítají se znaky, ne bajty – stejně jako limit v Claude Code.
RULES_LIMIT = 35_000

#: Soubory, které jdou do každé session: uživatelský `CLAUDE.md` a jeho `@` importy.
ALWAYS_LOADED = ["CLAUDE.md", "rules/rules.md", "rules/ptydepe.md"]
ALWAYS_LOADED_LIMIT = 50_000


def chars(name: str) -> int:
    return len((ROOT / name).read_text(encoding="utf-8"))


class InstructionSize(unittest.TestCase):
    def test_rules_within_limit(self):
        """`~/.claude/rules/rules.md` nesmí přerůst mez."""
        size = chars("rules/rules.md")
        self.assertLessEqual(
            size,
            RULES_LIMIT,
            f"~/.claude/rules/rules.md má {size} znaků, mez je {RULES_LIMIT}. Zkrať ho nebo přesuň "
            "pravidlo do podmíněně načítaného souboru.",
        )

    def test_always_loaded_within_limit(self):
        """Součet všeho, co jde do každé session, nesmí přerůst mez."""
        sizes = {name: chars(name) for name in ALWAYS_LOADED}
        total = sum(sizes.values())
        self.assertLessEqual(
            total,
            ALWAYS_LOADED_LIMIT,
            f"Paušálně načítané soubory mají dohromady {total} znaků, mez je "
            f"{ALWAYS_LOADED_LIMIT}: {sizes}",
        )

    def test_always_loaded_list_matches_imports(self):
        """Seznam paušálních souborů musí sedět s `@` importy v `CLAUDE.md`.

        Přibude-li import a seznam tady ne, test součtu by nový soubor tiše
        nepočítal.
        """
        text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        imported = {
            line.split()[1][len("@~/.claude/") :]
            for line in text.splitlines()
            if line.startswith("- @~/.claude/")
        }
        self.assertEqual(imported, set(ALWAYS_LOADED) - {"CLAUDE.md"})


if __name__ == "__main__":
    unittest.main()
