"""Meta-testy nad konfigurační vrstvou.

Skilly jsou text, který nikdo nespouští, takže se jejich vady projeví až za běhu
a obvykle tiše: režim popsaný v těle, který chybí v `argument-hint`, nebo odkaz
na soubor, který mezitím zmizel. Tohle je nejlevnější vrstva, která je chytí –
stojí nula tokenů a běží v zelené lince.

Spouští se: python3 -m unittest discover -s tests -q

Schválně jen stdlib: brána, která si nejdřív žádá instalaci balíčku, se v cizím
prostředí neprojeví jako nález, ale jako rozbitý nástroj – a ten se obchází.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = sorted(p for p in (ROOT / "skills").glob("*/SKILL.md"))


def frontmatter(path: Path) -> dict:
    """Minimální parser YAML hlavičky – jen klíč: hodnota na první úrovni."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    end = text.index("\n---", 4)
    out = {}
    for line in text[4:end].splitlines():
        if line.startswith((" ", "\t")) or ":" not in line:
            continue
        key, _, value = line.partition(":")
        out[key.strip()] = value.strip()
    return out


def body(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if text.startswith("---\n"):
        return text[text.index("\n---", 4) + 4:]
    return text


class SkillFrontmatter(unittest.TestCase):
    def test_povinna_pole(self):
        """Bez `name` a `description` se skill nenabídne k vyvolání."""
        for skill in SKILLS:
            with self.subTest(skill=skill.parent.name):
                fm = frontmatter(skill)
                self.assertTrue(fm.get("name"), f"{skill}: chybí `name` v hlavičce")
                self.assertTrue(fm.get("description"), f"{skill}: chybí `description`")
                self.assertEqual(fm["name"], skill.parent.name,
                    f"{skill}: `name: {fm.get('name')}` nesedí s adresářem")

    def test_description_rika_kdy_se_pouzije(self):
        """Popis rozhoduje, jestli se skill vyvolá – musí říct, kdy se použije."""
        for skill in SKILLS:
            with self.subTest(skill=skill.parent.name):
                desc = frontmatter(skill).get("description", "")
                self.assertIn("použije", desc, f"{skill}: `description` neříká, kdy se použije")

    def test_flagy_z_tela_jsou_v_argument_hint(self):
        """Režim popsaný v těle, ale chybějící v hintu, uživatel nikdy neuvidí."""
        for skill in SKILLS:
            with self.subTest(skill=skill.parent.name):
                hint = frontmatter(skill).get("argument-hint", "")
                documented = set(re.findall(
                    r"\*\*`/" + skill.parent.name + r" ([a-z-]+)`\*\*", body(skill)))
                missing = sorted(f for f in documented if f not in hint)
                self.assertFalse(missing,
                    f"{skill}: režimy {missing} jsou v těle, ale ne v argument-hint {hint!r}")


class SkillOdkazy(unittest.TestCase):
    def test_odkazy_na_soubory_existuji(self):
        """Odkaz na neexistující soubor pošle Clauda hledat něco, co tam není."""
        for skill in SKILLS:
            with self.subTest(skill=skill.parent.name):
                broken = []
                for ref in set(re.findall(
                        r"`(~/(?:\.claude|Dev)/[^`\s]+\.(?:md|sh|json|py))`", body(skill))):
                    if not Path(ref.replace("~", str(Path.home()), 1)).exists():
                        broken.append(ref)
                self.assertFalse(sorted(broken), f"{skill}: neexistující odkazy: {sorted(broken)}")

    def test_odkazuje_na_kroky_osy_ne_na_jejich_vnitrek(self):
        """`/code-review` je vnitřek `/review`; poslat tam uživatele ho připraví o panel.

        Vlastní vyvolání je v pořádku – tam ho skill volá jako nástroj a musí u něj
        uvést úroveň (`low`/`high`/`ultra`), protože bez ní se použije naposledy
        zadaná. Chyba je poslat *uživatele*, aby si `/code-review` pustil místo
        `/review`: dostal by jednu roli z panelu bez ověření nálezů.
        """
        povoleno = ("vyvolej", "volá", "uvnitř", "vestavěn", "Korektnost", "Bezpečnost",
                    "/code-review low", "/code-review high", "/code-review ultra")
        for skill in SKILLS:
            with self.subTest(skill=skill.parent.name):
                for line in body(skill).splitlines():
                    if "/code-review" not in line and "/security-review" not in line:
                        continue
                    if any(w in line for w in povoleno):
                        continue
                    self.fail(f"{skill}: odkaz na vnitřek `/review` mimo kontext volání:\n  {line.strip()}")


class SablonyProtiOriginalu(unittest.TestCase):
    """Text, který skill zapisuje jinam, se nesmí rozejít se svým originálem.

    `/autoprompt` a `/autocommit` nesou opsané znění sekce, kterou mají zapsat do
    globálního `CLAUDE.md`. Duplicitu nelze odstranit – skill ten text musí umět
    zapsat i tam, kde ještě není –, takže ji aspoň hlídáme. Rozejít se umí tiše:
    přeformuluje se originál a kopie ve skillu zůstane stará.
    """

    def _odstavec_pod_nadpisem(self, text, nadpis):
        i = text.index(nadpis)
        return text[i:].split("\n\n")[1].strip()

    def test_sablona_autopromptu_sedi_s_claude_md(self):
        claude_md = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        original = self._odstavec_pod_nadpisem(claude_md, "### Autoprompt v projektech")
        skill = (ROOT / "skills/autoprompt/SKILL.md").read_text(encoding="utf-8")
        # ve skillu je text odsazený uvnitř bloku, proto porovnáváme bez odsazení
        self.assertIn(original, "\n".join(l.strip() for l in skill.splitlines()),
            "šablona v /autoprompt se rozešla se zněním v CLAUDE.md, *Autoprompt v projektech*")


class Struktura(unittest.TestCase):
    OSA = {"project", "specify", "breakdown", "implement",
           "review", "consistency", "cleanup", "attack", "release"}

    def test_kroky_osy_maji_sekci_co_nedela(self):
        """Bez vymezení vůči sousedům se práce buď zdvojí, nebo neudělá vůbec."""
        chybi = [s.parent.name for s in SKILLS
                 if s.parent.name in self.OSA and "Co skill nedělá" not in body(s)]
        self.assertFalse(chybi, f"skilly osy bez sekce `Co skill nedělá`: {chybi}")

    def test_readme_zna_kazdy_skill(self):
        """README je rozcestník; skill, který v něm není, nikdo nenajde."""
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        chybi = [s.parent.name for s in SKILLS if f"skills/{s.parent.name}/" not in readme]
        self.assertFalse(chybi, f"skilly chybějící v README: {chybi}")


if __name__ == "__main__":
    unittest.main()
