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
    # Kontroluje se i to, co skilly samy odkazují – RULES.md a CLAUDE.md nesou
    # nejvíc odkazů ze všech a netestovaly se vůbec.
    ODKAZUJICI = SKILLS + [ROOT / "RULES.md", ROOT / "CLAUDE.md", ROOT / "README.md"]

    def test_odkazy_na_soubory_existuji(self):
        """Odkaz na neexistující soubor pošle Clauda hledat něco, co tam není."""
        for soubor in self.ODKAZUJICI:
            with self.subTest(soubor=soubor.name if soubor.parent == ROOT else soubor.parent.name):
                broken = []
                for ref in set(re.findall(
                        r"`(~/(?:\.claude|Dev)/[^`\s]+\.(?:md|sh|json|py))`", body(soubor))):
                    if not Path(ref.replace("~", str(Path.home()), 1)).exists():
                        broken.append(ref)
                self.assertFalse(sorted(broken), f"{soubor}: neexistující odkazy: {sorted(broken)}")

    def test_odkazy_na_sekce_miri_na_existujici_nadpis(self):
        """Odkaz ve tvaru `soubor`, *Sekce* musí v tom souboru najít nadpis.

        Tohle je vada, kterou soustava reálně dostává: přečíslovat fáze uvnitř
        skillu je jednořádková změna, po které pět odkazů z jiného souboru tiše
        ukazuje jinam. Kontrola existence souboru to nechytí – ten pořád existuje.

        Kotva se hledá jako *podřetězec* nadpisu, aby prošly i tvary typu
        *Fáze 1*, bod 6 nebo *`done.md`*.
        """
        # Kotva se pozná podle tvaru `soubor`, *Sekce* – tedy čárka hned za
        # zpětným apostrofem. Volnější vzor bral i běžné zvýraznění v okolní
        # větě ("`RULES.md`) stojí **před `/release`**") a hlásil samé nesmysly.
        vzor = re.compile(
            r"`(~/(?:\.claude|Dev)/[^`\s]+\.md)`,\s*(?:kapitola\s+|sekce\s+)?\*([^*\n]{3,80})\*")
        for soubor in self.ODKAZUJICI:
            with self.subTest(soubor=soubor.name if soubor.parent == ROOT else soubor.parent.name):
                spatne = []
                for cesta, sekce in set(vzor.findall(body(soubor))):
                    cil = Path(cesta.replace("~", str(Path.home()), 1))
                    if not cil.exists():
                        continue          # hlásí předchozí test
                    nadpisy = "\n".join(bez_bloku_kodu(cil))
                    kotva = sekce.strip().strip("`*")
                    if kotva not in nadpisy:
                        spatne.append(f"{cesta} -> *{kotva}*")
                self.assertFalse(sorted(spatne),
                    f"{soubor}: odkaz na sekci, která tam není: {sorted(spatne)}")

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

    `/autocommit` nese opsané znění sekce, kterou má zapsat do globálního
    `CLAUDE.md`. Duplicitu nelze odstranit – skill ten text musí umět zapsat
    i tam, kde ještě není –, takže ji aspoň hlídáme. Rozejít se umí tiše:
    přeformuluje se originál a kopie ve skillu zůstane stará.
    """

    def _odstavec_pod_nadpisem(self, text, nadpis):
        i = text.index(nadpis)
        return text[i:].split("\n\n")[1].strip()

    def test_sablona_autocommitu_sedi_s_claude_md(self):
        claude_md = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        original = self._odstavec_pod_nadpisem(claude_md, "### Autocommit v projektech")
        skill = (ROOT / "skills/autocommit/SKILL.md").read_text(encoding="utf-8")
        self.assertIn(original, "\n".join(l.strip() for l in skill.splitlines()),
            "šablona v /autocommit se rozešla se zněním v CLAUDE.md, *Autocommit v projektech*")

class NosneCasti(unittest.TestCase):
    """Ne že skill má správný tvar, ale že v něm je to, co nese jeho funkci.

    Dosavadní testy hlídají hlavičky, odkazy a nadpisy – tedy tvar. Z `/review` šlo
    smazat celou fázi ověřování nálezů, tu, o které skill sám píše, že na ní stojí
    jeho použitelnost, a zelená linka zůstala zelená. Brána, která nemůže spadnout
    na věcné vadě, je horší než chybějící brána: uspokojuje pravidlo *Ověřitelná
    brána místo dojmu*, aniž cokoliv doloží.

    Pořád je to jen tvar – text se nespouští a nic tu neověřuje, že instrukce
    fungují. Je to ale tvar toho, co funkci nese, a to je rozdíl, na kterém záleží.
    """

    def test_review_ma_overeni_nalezu(self):
        """Panel bez skeptika je generátor pravděpodobně znějících nálezů.

        Skill to o sobě píše sám: „bez třetí vrstvy je panel k ničemu“. Kdyby ta
        fáze vypadla, výstup by se navenek nezměnil – jen by přestal být pravdivý.
        """
        text = body(ROOT / "skills/review/SKILL.md")
        for kus in ("Ověření nálezů", "refuted", "Tenhle nález se snaž VYVRÁTIT"):
            self.assertIn(kus, text, f"/review přišel o ověřování nálezů: chybí {kus!r}")

    def test_zadani_pro_agenty_maji_povinna_pole(self):
        """Nález bez `basis` a `severity` nejde ani ověřit, ani zařadit.

        `severity` rozhoduje, jestli nález půjde na ověření; `basis` je to, o co se
        opírá. Bez nich je výstup panelu próza, ne data.
        """
        for jmeno in ("review", "attack"):
            with self.subTest(skill=jmeno):
                text = body(ROOT / f"skills/{jmeno}/SKILL.md")
                self.assertIn('"severity"', text, f"/{jmeno}: zadání agentů nemá pole severity")
        self.assertIn('"basis"', body(ROOT / "skills/review/SKILL.md"),
                      "/review: zadání rolí nemá pole basis")

    def test_datum_se_vyrabi_prikazem(self):
        """Zapamatované datum se tiše rozejde se skutečností a vypadá správně.

        `~/.claude/RULES.md`, *Hodnotu, kterou čte stroj, nepiš – nech ji vyrobit
        příkazem*. Skill, který někam zapisuje datovaný záznam, musí ten příkaz
        jmenovat, ne popisovat, co má být uvnitř.
        """
        # Hledá se tvar datovaného ZÁZNAMU (`- **YYYY-MM-DD** – …`), ne jakýkoli
        # výskyt masky: /specify jmenuje YYYY-MM-DD v cestě, kterou naopak přepisuje.
        for skill in SKILLS:
            text = body(skill)
            if "**YYYY-MM-DD**" not in text:
                continue
            with self.subTest(skill=skill.parent.name):
                self.assertIn("date +%F", text,
                    f"{skill.parent.name}: zapisuje datovaný záznam, ale nejmenuje `date +%F`")

    def test_behovy_stav_je_gitignorovany(self):
        """Stav, který se mění po každém tahu, nesmí skončit v gitu.

        `~/Dev/context/structure/structure.md`, *Běhový stav skillů*. Skill, který
        do `.claude/run/` zapisuje, spoléhá na to, že `/project` ten řádek do
        `.gitignore` doplní – jinak ho v projektu s autocommitem začne commitovat.
        """
        pisou = [s.parent.name for s in SKILLS if ".claude/run/" in body(s)]
        if not pisou:
            self.skipTest("do .claude/run/ zatím nikdo nezapisuje")
        self.assertIn(".claude/run/", body(ROOT / "skills/project/SKILL.md"),
            f"skilly {pisou} zapisují do .claude/run/, ale /project ho nedává do .gitignore")


def bez_bloku_kodu(path: Path):
    """Nadpisy souboru, ale jen skutečné – ne ty uvnitř bloků kódu.

    `worktree.md` má v ukázce stubu `## Odchylky`; brát to jako nadpis dokumentu
    znamená, že by odkaz na neexistující sekci prošel, kdyby se náhodou jmenovala
    stejně jako něco v příkladu.
    """
    ve_bloku = False
    for radek in path.read_text(encoding="utf-8").splitlines():
        if radek.lstrip().startswith(("```", "~~~")):
            ve_bloku = not ve_bloku
            continue
        if not ve_bloku and radek.startswith("#"):
            yield radek.lstrip("# ").strip()


def osa_z_rules() -> set:
    """Kroky osy se čtou z `RULES.md`, ne z konstanty v testu.

    Ručně opsaný seznam je druhá kopie pravdy: přejmenovaný nebo přidaný krok by
    testem prošel, a naopak zmizelý krok by ho shodil z jiného důvodu, než je ten
    skutečný.
    """
    text = (ROOT / "RULES.md").read_text(encoding="utf-8")
    i = text.index("### Životní cyklus práce")
    blok = text[text.index("```", i) + 3:]
    blok = blok[:blok.index("```")]
    return set(re.findall(r"/([a-z][a-z-]*)", blok))


class KontraktPrikazu(unittest.TestCase):
    """Formát kontraktu je závazný, protože ho čte skript – a to se neověřovalo.

    `coding.md` říká „jeden řádek na klíč, `- klíč: příkaz`, a za příkazem už nic“.
    Změna formátu (komentář za příkazem, jiné odsazení, hodnota v bloku kódu)
    vypne bránu **tiše**: `sed` v `green-line.sh` prostě nic nenajde a hook se
    zachová, jako by ten krok projekt neměl.
    """

    KONTRAKT = ROOT / ".claude/CLAUDE.md"

    def _sekce(self) -> str:
        """Sekce ## Příkazy z těla bez bloků kódu – stejně jako `md_body`
        a `contract_section` v `green-line.sh`."""
        radky, ve_bloku, uvnitr, out = self.KONTRAKT.read_text(encoding="utf-8").splitlines(), False, False, []
        for r in radky:
            if r.lstrip().startswith(("```", "~~~")):
                ve_bloku = not ve_bloku
                continue
            if ve_bloku:
                continue
            if r.startswith("## Příkazy"):
                uvnitr = True
            elif uvnitr and r.startswith("## "):
                break
            if uvnitr:
                out.append(r)
        return "\n".join(out)

    def _hodnota(self, klic: str):
        """Týž výraz jako `cmd_for` v green-line.sh."""
        m = re.search(rf"^[ \t]*[-*][ \t]*{klic}:[ \t]+(.*?)[ \t]*$",
                      self._sekce(), re.M)
        return m.group(1) if m else None

    def test_kontrakt_se_da_precist(self):
        """Kdyby se sekce rozešla s formátem, zelená linka by tu tiše neběžela."""
        self.assertTrue(self._sekce().strip(), "sekci ## Příkazy se nepodařilo přečíst")
        for klic in ("typecheck", "lint", "test"):
            with self.subTest(klic=klic):
                self.assertIsNotNone(self._hodnota(klic),
                    f"klíč {klic} se z kontraktu nepřečetl – změnil se formát?")

    def test_prikazy_z_kontraktu_jsou_spustitelne(self):
        """Pomlčka je vědomé rozhodnutí, ale příkaz musí existovat.

        Jinak hook po každém tahu hlásí nespustitelný krok – a to je šum, ne nález.
        """
        import shutil
        for klic in ("typecheck", "lint", "test"):
            hodnota = self._hodnota(klic)
            if hodnota in (None, "-"):
                continue
            with self.subTest(klic=klic):
                binarka = hodnota.split()[0]
                self.assertTrue(shutil.which(binarka),
                    f"kontrakt má {klic}: {hodnota}, ale {binarka} není na PATH")


class Struktura(unittest.TestCase):
    OSA = osa_z_rules()

    def test_osa_se_precetla(self):
        """Kdyby se blok v RULES.md přeformátoval, testy osy by tiše zmlkly."""
        self.assertGreaterEqual(len(self.OSA), 8,
            f"z RULES.md se přečetlo jen {len(self.OSA)} kroků osy: {sorted(self.OSA)}")
        chybi = sorted(self.OSA - {s.parent.name for s in SKILLS})
        self.assertFalse(chybi, f"osa jmenuje kroky, které nemají skill: {chybi}")

    def test_kroky_osy_maji_sekci_co_nedela(self):
        """Bez vymezení vůči sousedům se práce buď zdvojí, nebo neudělá vůbec."""
        chybi = [s.parent.name for s in SKILLS
                 if s.parent.name in self.OSA and "Co skill nedělá" not in body(s)]
        self.assertFalse(chybi, f"skilly osy bez sekce `Co skill nedělá`: {chybi}")

    def _skilly_v_readme(self) -> set:
        """Skilly jmenované v nadpisech README. Jeden nadpis jich může nést víc –
        `/breakdown` a `/implement` mají společný, protože jeden předává druhému."""
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        out = set()
        for radek in readme.splitlines():
            if radek.startswith("#"):
                out |= set(re.findall(r"\[`/([a-z-]+)`\]", radek))
        return out

    def test_readme_zna_kazdy_skill(self):
        """README je rozcestník; skill, který v něm není, nikdo nenajde.

        Kontroluje se nadpis, ne výskyt řetězce: `skills/foo/` se v README může
        objevit i v ukázce adresářové struktury, a test by pak byl spokojený
        i bez sekce o skillu.
        """
        chybi = sorted({s.parent.name for s in SKILLS} - self._skilly_v_readme())
        self.assertFalse(chybi, f"skilly bez vlastní sekce v README: {chybi}")

    def test_readme_neodkazuje_na_zmizely_skill(self):
        """Opačný směr: po smazání skillu zůstane v README mrtvá sekce."""
        navic = sorted(self._skilly_v_readme() - {s.parent.name for s in SKILLS})
        self.assertFalse(navic, f"README má sekci pro skill, který neexistuje: {navic}")


if __name__ == "__main__":
    unittest.main()
