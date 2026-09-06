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
    # nejvíc odkazů ze všech a netestovaly se vůbec. Projektový .claude/CLAUDE.md
    # nese kontrakt příkazů a odkazy na sekce v jiném repozitáři, takže patří sem taky.
    # `SKILLS.md` nese po zavedení normy nejvíc odkazů na sekce ze všech souborů
    # a byl jediný mimo kontrolu – uříznutá kotva v něm prošla všemi testy.
    ODKAZUJICI = SKILLS + [ROOT / "RULES.md", ROOT / "CLAUDE.md", ROOT / "README.md",
                           ROOT / ".claude/CLAUDE.md",
                           ROOT / "skills/SKILLS.md", ROOT / "skills/PREFLIGHT.md"]

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

    def test_vnitroskillove_odkazy_na_faze_miri_na_existujici_nadpis(self):
        """Odkaz „vezmi to do Fáze 7“ uvnitř skillu musí trefit jeho vlastní nadpis.

        Tuhle vadu soustava reálně dostává: přečíslovat fáze je jedna dávka náhrad,
        po které tři odkazy z téhož souboru ukazují jinam. Test na sekce ji nechytí –
        ten matchuje jen odkazy s uvedenou cestou k souboru, kdežto vnitroskillový
        odkaz cestu nemá. Doloženo mutací: `Fáze 7` přepsaná na `Fáze 77` prošla.

        **Cizí odkaz se pozná z okna před samotným odkazem**, ne z celého řádku.
        První verze přeskakovala řádek, kdykoliv se na něm kdekoliv objevilo jméno
        jiného skillu – a protože se skilly zmiňují průběžně, vypadlo z kontroly
        dvanáct odkazů v pěti nejrozsáhlejších skillech. Doloženo mutací: `Fáze 4`
        v `/consistency` šla přepsat na `Fáze 44`, protože se o dvě věty dál mluvilo
        o `/review`.

        Tvar `` `/review`, Fáze 0.1 `` nehlídá ani tenhle test (je cizí), ani test
        na sekce (nemá cestu k souboru). Je to známá díra, ne předpoklad pokrytí.

        **Hlídá se „Fáze“ i „Krok“.** `/project` se člení na kroky, ne na fáze, takže
        ho původní vzor míjel celý – jeho přečíslování na plochou řadu 0–13 prošlo
        bez brány a muselo se ověřovat jednorázovým skriptem. Součástí jsou i rozsahy
        („v krocích 2–12“), protože ty se při přečíslování posouvají zvlášť a první
        dávka náhrad je nechala být.
        """
        # Za jedním „krok“ může stát celý výčet („kroky 3, 4, 6, 8–12“). Vzor proto
        # bere všechna čísla až do konce výčtu, ne jen to první. Bez toho zůstala
        # třída chyb, která reálně nastala: dávka náhrad při přečíslování `/project`
        # přepsala jen první číslo řádku a zbytek nechala ve starém číslování –
        # včetně kroku `8b`, který týž commit rušil. Ověřovací skript měl tutéž
        # slepou skvrnu jako test, takže to prohlásil za v pořádku.
        vzor = re.compile(r"(Fáz[eií]|[Kk]roc?[íkyů]?\w*)\s+"
                          r"((?:\d+(?:\.\d+)?[a-c]?)(?:\s*(?:,|a|–|až)\s*\d+(?:\.\d+)?[a-c]?)*)")
        jmena = {s.parent.name for s in SKILLS}
        for skill in SKILLS:
            with self.subTest(skill=skill.parent.name):
                cizi = jmena - {skill.parent.name}
                vlastni = {re.match(r"(?:Fáze|Krok) (\S+)", n).group(1)
                           for n in bez_bloku_kodu(skill)
                           if n.startswith(("Fáze ", "Krok "))}
                # písmenné podkroky mají vlastní nadpis úrovně ###, např. „6a – Režim“
                vlastni |= {m.group(1) for m in
                            (re.match(r"(\d+[a-c]) – ", n) for n in bez_bloku_kodu(skill)) if m}
                if not vlastni:
                    continue          # skill fáze ani kroky nepoužívá
                spatne = []
                ve_bloku = False
                for radek in body(skill).splitlines():
                    if radek.lstrip().startswith(("```", "~~~")):
                        ve_bloku = not ve_bloku
                        continue
                    if ve_bloku:
                        continue      # šablona pro subagenta není odkaz
                    for m in vzor.finditer(radek):
                        okno = radek[max(0, m.start() - 60):m.start()]
                        if "SKILL.md" in okno or any(f"/{j}" in okno for j in cizi):
                            continue  # odkaz do cizího skillu
                        # „krok 8 životního cyklu“ v RULES.md není vlastní fáze, ale krok
                        # *Životního cyklu projektu* – ty se číslují nezávisle
                        if "RULES.md" in okno or "Životní cyklus" in okno:
                            continue
                        if re.match(r"\s*os[ay]\b", radek[m.end():m.end() + 8]):
                            continue
                        for cislo in re.findall(r"\d+(?:\.\d+)?[a-c]?", m.group(2)):
                            if cislo not in vlastni:
                                spatne.append(f"{m.group(1)} {cislo}")
                self.assertFalse(sorted(set(spatne)),
                    f"{skill}: odkaz na vlastní fázi, která tam není: "
                    f"{sorted(set(spatne))} (má {sorted(vlastni)})")

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

    def test_cleanup_hleda_zamluvena_temata(self):
        """Skill sám tvrdí, že tohle je nejčastější ztráta v dlouhé konverzaci.

        Je to druhá ze čtyř záruk v *Co skill dělá*, a jako jediná z nich nestojí
        na zápisu do souborů – kdyby fáze vypadla, úklid by navenek proběhl stejně
        a chyběl by jen dotaz, který nikdo nepostrádá, protože o něm neví.

        **Hledá se uvnitř té fáze, ne kdekoliv v souboru.** První verze ověřovala
        `AskUserQuestion` nad celým tělem skillu, kde se ten řetězec vyskytuje
        pětkrát – šlo tedy smazat celou sekci *Jak to probrat* a testy zůstaly
        zelené. Způsob dotazování je přitom to podstatné: kdyby se položky jen
        vypsaly do závěru, uživatel session zavře a zmizí s ní.
        """
        text = body(ROOT / "skills/cleanup/SKILL.md")
        nadpis = "## Fáze 2 – Zamluvená a nevypořádaná témata"
        self.assertIn(nadpis, text, "/cleanup přišel o fázi na zamluvená témata")
        faze = text[text.index(nadpis):]
        faze = faze[:faze.index("\n## ")]
        for kus in ("Jak ověřit, že to opravdu visí", "Práh důležitosti",
                    "AskUserQuestion", "Bezpředmětné"):
            self.assertIn(kus, faze,
                          f"/cleanup, Fáze 2 přišla o {kus!r} – zbyl jen nadpis")

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


def cyklus_z_rules() -> set:
    """Kroky životního cyklu se čtou z `RULES.md`, ne z konstanty v testu.

    Ručně opsaný seznam je druhá kopie pravdy: přejmenovaný nebo přidaný krok by
    testem prošel, a naopak zmizelý krok by ho shodil z jiného důvodu, než je ten
    skutečný.
    """
    text = (ROOT / "RULES.md").read_text(encoding="utf-8")
    i = text.index("### Životní cyklus projektu")
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
    CYKLUS = cyklus_z_rules()

    def test_cyklus_se_precetl(self):
        """Kdyby se blok v RULES.md přeformátoval, testy životního cyklu by tiše zmlkly."""
        self.assertGreaterEqual(len(self.CYKLUS), 8,
            f"z RULES.md se přečetlo jen {len(self.CYKLUS)} kroků životního cyklu: {sorted(self.CYKLUS)}")
        chybi = sorted(self.CYKLUS - {s.parent.name for s in SKILLS})
        self.assertFalse(chybi, f"životní cyklus jmenuje kroky, které nemají skill: {chybi}")

    def test_kroky_cyklu_maji_sekci_co_nedela(self):
        """Bez vymezení vůči sousedům se práce buď zdvojí, nebo neudělá vůbec."""
        chybi = [s.parent.name for s in SKILLS
                 if s.parent.name in self.CYKLUS and "Co skill nedělá" not in body(s)]
        self.assertFalse(chybi, f"skilly životního cyklu bez sekce `Co skill nedělá`: {chybi}")

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


class SouladSNormou(unittest.TestCase):
    """Skilly proti `skills/SKILLS.md`. Jediné místo, kde se norma vynucuje strojem.

    Norma vznikla později než skilly, takže čtrnáct z nich ji zatím nesplňuje.
    Převod je vědomý běh `/skill update`, ne vedlejší efekt jiné práce – proto
    seznam `MIGRACE` místo patnácti padajících testů.

    Je to **ráčna, ne umlčení**: test porovnává množiny na rovnost. Skill, který
    se opraví a nezmizí ze seznamu, test shodí stejně jako skill, který se
    rozbije. Bez toho by seznam tiše zůstal i po dokončení migrace a přestal by
    cokoliv měřit.
    """

    NORMA = ROOT / "skills" / "SKILLS.md"
    PREFLIGHT = ROOT / "skills" / "PREFLIGHT.md"

    #: Skilly, které ještě neprošly `/skill update`. Zkracuje se, nikdy nedoplňuje.
    MIGRACE = {
        "attack", "autocommit", "breakdown", "cleanup", "consistency",
        "implement", "oponent", "project", "release", "replace", "report",
        "review", "specify", "transcript",
    }

    #: Odkaz dovnitř fáze jiného skillu. Cizí fáze se přečíslují a odkaz pak
    #: tiše ukazuje jinam – proto to má být v PREFLIGHT.md, ne v odkazu.
    CIZI_FAZE = re.compile(
        r"`/(?:[a-z-]+)`,\s*(?:Fáze|Krok)|skills/\w+/SKILL\.md`,\s*\*(?:Fáze|Krok)")

    def vady(self, skill: Path) -> list:
        text = body(skill)
        out = []
        if "\n## Co skill dělá" not in text:
            out.append("chybí `## Co skill dělá`")
        if "\n## Co skill nedělá" not in text:
            out.append("chybí `## Co skill nedělá`")
        # Pre-flight je povinná sekce a pozná se podle **čísla**, ne podle názvu:
        # `/oponent` ho má jako „Fáze 0 – Co se oponuje“ a `/project` jako
        # „Krok 0 – Zjisti režim a stav“. Dřív se odkaz na PREFLIGHT.md hledal
        # jen tehdy, když se v textu vyskytlo slovo „Pre-flight“ – oba tyhle
        # skilly z kontroly tiše vypadávaly i se svým opsaným pre-flightem.
        ma_preflight = re.search(r"\n## (?:Fáze|Krok) 0\b", text)
        if not ma_preflight:
            out.append("chybí `## Fáze 0 – Pre-flight`")
        elif "PREFLIGHT.md" not in text:
            out.append("pre-flight neodkazuje na `skills/PREFLIGHT.md`")

        radku = len(text.splitlines())
        if radku > 500:
            out.append(f"tělo má {radku} řádků, tvrdá mez je 500")
        if "Zakonči jednou z těchto vět" not in text:
            out.append("chybí dvě koncové věty")
        if self.CIZI_FAZE.search(text):
            out.append("odkazuje dovnitř fáze jiného skillu")
        out += self.vady_poradi(skill)
        return out

    def vady_poradi(self, skill: Path) -> list:
        """Pořadí sekcí podle normy, *Povinné sekce a jejich pořadí*.

        Norma řadí hlavní průběh, za něj přílohové sekce (samostatné režimy,
        katalogy) a `## Časté chyby` úplně naposled. Kontroluje se jen relativní
        pořadí sekcí, které skill opravdu má – nepovinné se nedoplňují.

        Proč zvlášť: bez téhle kontroly tvrdila norma víc, než uměla vynutit.
        Doloženo – pravidlo o přílohových sekcích do ní přibylo 4. 9. 2026 z auditu
        `/consistency`, a týž audit ho našel porušené v `/skill`, protože ho žádná
        brána chytit nemohla.
        """
        nadpisy = [n for n in bez_bloku_kodu(skill) if not n.startswith("#")]
        poradi = {n: i for i, n in enumerate(nadpisy)}

        def kde(*zacatky):
            for n, i in poradi.items():
                if n.startswith(zacatky):
                    return i
            return None

        dela, nedela = kde("Co skill dělá"), kde("Co skill nedělá")
        uvnitr = kde("Jak je to postavené uvnitř")
        prvni_faze = kde("Fáze 0", "Krok 0")
        chyby = kde("Časté chyby")
        # Závěr = **poslední** fáze či krok, ne fáze pojmenovaná „Závěr“. Devět
        # skillů ji má pod vlastním názvem (`Úklid a shrnutí`, `Uzavření`,
        # `Předání`) a norma jméno nepředepisuje – vázat kontrolu na slovo
        # „Závěr“ znamenalo, že přejmenování závěru celou kontrolu pořadí tiše
        # vypnulo. Doloženo mutací: `Fáze 8 – Závěr` → `Fáze 8 – Uzavření`
        # zneškodnilo jedinou vadu, kterou uměla najít.
        zaver = max((i for n, i in poradi.items()
                     if n.startswith(("Fáze", "Krok"))), default=None)

        out = []
        for driv, pozdej, popis in (
                (dela, nedela, "`Co skill nedělá` musí být za `Co skill dělá`"),
                (nedela, uvnitr, "`Jak je to postavené uvnitř` patří za `Co skill nedělá`"),
                (uvnitr, prvni_faze, "postup začíná až za `Jak je to postavené uvnitř`"),
                (nedela, prvni_faze, "postup začíná až za `Co skill nedělá`"),
        ):
            if driv is not None and pozdej is not None and driv > pozdej:
                out.append(f"pořadí sekcí: {popis}")

        # `Časté chyby` mají v normě dvě legitimní místa podle toho, jestli skill
        # má přílohy: u lineárního těsně před závěrem, u skillu s přílohovými
        # sekcemi úplně naposled. Kontrolovat jen jedno z nich by shodilo polovinu
        # skillů, které normu splňují.
        if chyby is not None and zaver is not None:
            prilohy = [n for n, i in poradi.items()
                       if i > zaver and not n.startswith("Časté chyby")]
            if prilohy and chyby != max(poradi.values()):
                out.append("pořadí sekcí: skill má přílohové sekce, "
                           "takže `Časté chyby` musí stát úplně naposled")
            if not prilohy and chyby > zaver:
                out.append("pořadí sekcí: skill nemá přílohy, "
                           "takže `Časté chyby` patří před závěrečnou fázi")
        return out

    def test_norma_a_preflight_existuji(self):
        """Bez nich nemá `/skill` co číst a odkazy ze skillů míří nikam."""
        for soubor in (self.NORMA, self.PREFLIGHT):
            self.assertTrue(soubor.exists(), f"chybí {soubor}")
        self.assertFalse((self.NORMA.parent / "SKILLS.md" / "SKILL.md").exists(),
            "norma se nesmí tvářit jako skill")

    def test_description_se_vejde_do_limitu(self):
        """Delší popis se nemusí přenést celý – a pak se skill nevyvolá vůbec.

        Bez výjimky pro migraci: limit platí pro všechny a dnes ho nikdo neporušuje.
        """
        for skill in SKILLS:
            with self.subTest(skill=skill.parent.name):
                popis = frontmatter(skill).get("description", "")
                self.assertLessEqual(len(popis), 1024,
                    f"{skill.parent.name}: description má {len(popis)} znaků")

    def test_migrace_jmenuje_jen_existujici_skilly(self):
        """Zmizelý skill v seznamu by tiše držel výjimku pro nikoho."""
        navic = sorted(self.MIGRACE - {s.parent.name for s in SKILLS})
        self.assertFalse(navic, f"MIGRACE jmenuje neexistující skilly: {navic}")

    def test_skilly_odpovidaji_norme(self):
        """Ráčna: množina nesouladných skillů se musí rovnat seznamu MIGRACE."""
        nesoulad = {s.parent.name: self.vady(s) for s in SKILLS if self.vady(s)}

        rozbite = sorted(set(nesoulad) - self.MIGRACE)
        self.assertFalse(rozbite, "skilly mimo normu, které v MIGRACE nejsou: "
            + "; ".join(f"{n}: {', '.join(nesoulad[n])}" for n in rozbite))

        hotove = sorted(self.MIGRACE - set(nesoulad))
        self.assertFalse(hotove,
            f"tyhle skilly už normu splňují – vyškrtni je z MIGRACE: {hotove}")


class KontrolyOpravduChytaji(unittest.TestCase):
    """Mutační testy: poškoď vstup a ověř, že kontrola nález nahlásí.

    Zápisy v `decisions.md` i docstringy výš se opakovaně odvolávají na to,
    že kontrola byla „ověřena mutací“. Ta mutace se ale dělala ručně jako
    jednorázový skript a nikde nezůstala – bylo to tvrzení o důkazu, ne důkaz.
    A přesně takový doklad jednou selhal: ověřovací skript u přečíslování
    `/project` měl tutéž slepou skvrnu jako kontrola, kterou zastupoval,
    a prohlásil za v pořádku čtyři rozbité odkazy.

    Kontrola, která nic nechytá, projde stejně tiše jako kontrola, která
    funguje – rozdíl je vidět jedině tak, že se jí předloží rozbitý vstup.
    """

    #: Vzorový skill, na kterém se mutuje. `/skill` je jediný, který dnes
    #: normu splňuje celou, takže každý nález nad ním pochází z mutace.
    VZOR = ROOT / "skills/skill/SKILL.md"

    def mutuj(self, nahrada: tuple) -> list:
        """Vrátí vady, které kontroly najdou nad poškozenou kopií vzoru."""
        import shutil, tempfile
        puvodni = self.VZOR.read_text(encoding="utf-8")
        stary, novy = nahrada
        self.assertIn(stary, puvodni, f"mutace se nemá čeho chytit: {stary!r}")
        # nahrazuje se KAŽDÝ výskyt: `PREFLIGHT.md` je ve vzoru čtyřikrát
        # a koncové věty dvakrát, takže mutace jednoho výskytu nic nezmění
        # a test by prošel, i kdyby kontrola nefungovala
        poskozeny = puvodni.replace(stary, novy)
        self.assertNotEqual(poskozeny, puvodni, "mutace nic nezměnila")
        docasny = Path(tempfile.mkdtemp())
        try:
            (docasny / "skill").mkdir()
            kopie = docasny / "skill" / "SKILL.md"
            kopie.write_text(poskozeny, encoding="utf-8")
            return SouladSNormou("test_skilly_odpovidaji_norme").vady(kopie)
        finally:
            shutil.rmtree(docasny)

    def test_chybejici_sekce_se_nahlasi(self):
        for nadpis, cekam in (
                ("## Co skill dělá", "chybí `## Co skill dělá`"),
                ("## Co skill nedělá", "chybí `## Co skill nedělá`"),
                ("## Fáze 0 – Pre-flight", "chybí `## Fáze 0 – Pre-flight`"),
        ):
            with self.subTest(nadpis=nadpis):
                vady = self.mutuj((nadpis, "## Něco jiného"))
                self.assertIn(cekam, vady, f"kontrola nechytila smazané {nadpis!r}: {vady}")

    def test_chybejici_odkaz_na_preflight_se_nahlasi(self):
        vady = self.mutuj(("PREFLIGHT.md", "JINY.md"))
        self.assertIn("pre-flight neodkazuje na `skills/PREFLIGHT.md`", vady, vady)

    def test_chybejici_koncove_vety_se_nahlasi(self):
        vady = self.mutuj(("Zakonči jednou z těchto vět", "Skonči nějak"))
        self.assertIn("chybí dvě koncové věty", vady, vady)

    def test_odkaz_dovnitr_ciziho_skillu_se_nahlasi(self):
        vady = self.mutuj(("## Fáze 3 – Tabulka švů",
                           "## Fáze 3 – Tabulka švů\n\nPostupem z `/review`, Fáze 0.1."))
        self.assertIn("odkazuje dovnitř fáze jiného skillu", vady, vady)

    def test_spatne_poradi_sekci_se_nahlasi(self):
        """`Časté chyby` u skillu s přílohami musí stát naposled."""
        import shutil, tempfile
        text = self.VZOR.read_text(encoding="utf-8")
        i = text.index("\n## Časté chyby")
        j = text.index("\n## Fáze 8 – Závěr")
        prehozeny = text[:j] + text[i:].rstrip() + "\n" + text[j:i]
        docasny = Path(tempfile.mkdtemp())
        try:
            (docasny / "skill").mkdir()
            kopie = docasny / "skill" / "SKILL.md"
            kopie.write_text(prehozeny, encoding="utf-8")
            vady = SouladSNormou("test_skilly_odpovidaji_norme").vady(kopie)
        finally:
            shutil.rmtree(docasny)
        self.assertTrue(any("Časté chyby" in v for v in vady),
                        f"kontrola nechytila přesunuté `Časté chyby`: {vady}")

    def test_visici_odkaz_na_vlastni_fazi_se_nahlasi(self):
        """Tohle je ta třída chyb, kterou ruční ověření jednou minulo."""
        import shutil, tempfile
        puvodni = self.VZOR.read_text(encoding="utf-8")
        docasny = Path(tempfile.mkdtemp())
        try:
            (docasny / "skill").mkdir()
            kopie = docasny / "skill" / "SKILL.md"
            kopie.write_text(puvodni.replace("*Fázi 3*", "*Fázi 33*", 1), encoding="utf-8")
            puvodni_seznam = SKILLS[:]
            SKILLS[:] = [kopie]
            try:
                with self.assertRaises(AssertionError):
                    SkillOdkazy(
                        "test_vnitroskillove_odkazy_na_faze_miri_na_existujici_nadpis"
                    ).test_vnitroskillove_odkazy_na_faze_miri_na_existujici_nadpis()
            finally:
                SKILLS[:] = puvodni_seznam
        finally:
            shutil.rmtree(docasny)


class ReadmeSkillu(unittest.TestCase):
    """README skillu proti `skills/SKILLS.md`, *README skillu*.

    Je to jediná část skillu psaná **pro člověka zvenčí** – vizitka, na kterou
    se posílá odkaz. Právě proto se rozpadá tiše: chybějící sekce nikoho za
    běhu neomezí a pozná se až ve chvíli, kdy si ji někdo cizí přečte.
    """

    #: Nadpisy, které norma žádá po každém README skillu.
    POVINNE = ("## Co umí", "## Proč zrovna tenhle", "## Jak se to používá",
               "## Co nedělá", "## Jak si ho nainstalovat", "### Požadavky a omezení")

    #: Mez z normy. README delší než jeho `SKILL.md` přestalo být vizitkou.
    MEZ_RADKU = 120

    REPO = "https://github.com/jantichy/claude/tree/main/skills/"
    CYKLUS = cyklus_z_rules()

    def _readme(self, skill: Path) -> Path:
        return skill.parent / "README.md"

    def test_kazdy_skill_ma_readme(self):
        """Skill bez README nejde nikomu doporučit odkazem."""
        chybi = [s.parent.name for s in SKILLS if not self._readme(s).exists()]
        self.assertFalse(chybi, f"skilly bez vlastního README: {chybi}")

    def test_readme_ma_povinne_sekce(self):
        for skill in SKILLS:
            readme = self._readme(skill)
            if not readme.exists():
                continue
            text = readme.read_text(encoding="utf-8")
            for nadpis in self.POVINNE:
                with self.subTest(skill=skill.parent.name, sekce=nadpis):
                    self.assertIn(nadpis, text, f"{readme}: chybí sekce `{nadpis}`")

    def test_readme_instaluje_odkazem_na_repozitar(self):
        """Instalace se píše jako pokyn pro Clauda, ne jako ruční kopírování."""
        for skill in SKILLS:
            readme = self._readme(skill)
            if not readme.exists():
                continue
            with self.subTest(skill=skill.parent.name):
                text = readme.read_text(encoding="utf-8")
                self.assertIn(self.REPO + skill.parent.name, text,
                    f"{readme}: instalační sekce neodkazuje na {self.REPO}{skill.parent.name}")

    def test_readme_skillu_z_cyklu_ma_ramecek_a_hromadnou_instalaci(self):
        """Čtenář, kterému přišel odkaz na jeden skill, jinak neví o zbylých deseti."""
        for skill in SKILLS:
            if skill.parent.name not in self.CYKLUS:
                continue
            readme = self._readme(skill)
            if not readme.exists():
                continue
            with self.subTest(skill=skill.parent.name):
                text = readme.read_text(encoding="utf-8")
                self.assertIn("**Součást životního cyklu projektu.**", text,
                    f"{readme}: chybí rámeček s celým životním cyklem")
                self.assertIn("Nebo celou sadu naráz.", text,
                    f"{readme}: chybí hromadná instalace celého životního cyklu")
                for krok in sorted(self.CYKLUS):
                    if krok == skill.parent.name:
                        continue
                    self.assertIn(f"(../{krok}/README.md)", text,
                        f"{readme}: rámeček neodkazuje na `/{krok}`")

    def test_hromadna_instalace_jmenuje_vsechny_kroky(self):
        """Přibude-li krok, musí ho vyjmenovat i pokyn na instalaci celé sady.

        Rámeček výš hlídají odkazy, ale seznam jmen v instalačním promptu je
        prostý text – ten by přidaný krok tiše minul a lidé by si nainstalovali
        neúplnou sadu."""
        for skill in SKILLS:
            if skill.parent.name not in self.CYKLUS:
                continue
            readme = self._readme(skill)
            if not readme.exists():
                continue
            text = readme.read_text(encoding="utf-8")
            i = text.find("Nebo celou sadu naráz.")
            if i < 0:
                continue
            odstavec = text[i:i + 800]
            with self.subTest(skill=skill.parent.name):
                for krok in sorted(self.CYKLUS):
                    self.assertRegex(odstavec, rf"\b{krok}\b",
                        f"{readme}: hromadná instalace nejmenuje `{krok}`")

    def test_readme_skillu_mimo_cyklus_ramecek_nema(self):
        """Předstírat sadu u skillu, který se pouští samostatně, by mátlo."""
        navic = []
        for skill in SKILLS:
            if skill.parent.name in self.CYKLUS:
                continue
            readme = self._readme(skill)
            if readme.exists() and "**Součást životního cyklu projektu.**" in readme.read_text(encoding="utf-8"):
                navic.append(skill.parent.name)
        self.assertFalse(navic, f"skilly mimo životní cyklus s rámečkem osy: {navic}")

    def test_readme_se_vejde_do_meze(self):
        """Vizitka, kterou nikdo nedočte, svůj účel neplní."""
        dlouhe = []
        for skill in SKILLS:
            readme = self._readme(skill)
            if not readme.exists():
                continue
            radku = len(readme.read_text(encoding="utf-8").splitlines())
            if radku > self.MEZ_RADKU:
                dlouhe.append(f"{skill.parent.name} ({radku})")
        self.assertFalse(dlouhe, f"README nad mez {self.MEZ_RADKU} řádků: {dlouhe}")

    def test_hlavni_readme_odkazuje_na_adresar_skillu(self):
        """Bez odkazu je podrobné README neviditelné.

        Míří se na adresář, ne na soubor: GitHub v adresáři `README.md` rovnou
        vypíše, takže druhý odkaz na totéž místo by byl navíc.
        """
        hlavni = (ROOT / "README.md").read_text(encoding="utf-8")
        chybi = [s.parent.name for s in SKILLS
                 if f"(skills/{s.parent.name}/)" not in hlavni]
        self.assertFalse(chybi, f"hlavní README neodkazuje na adresář skillu: {chybi}")


class SkriptySkillu(unittest.TestCase):
    """Skripty ve skillech nečte žádná jiná brána.

    `typecheck` pouští `swiftc` a `lint` shellcheck; Python ve `skills/*/scripts/`
    by tedy zůstal bez kontroly a překlep by se poznal až za ostrého běhu.
    """

    SKRIPTY = sorted((ROOT / "skills").glob("*/scripts/*.py"))

    def test_skripty_se_prelozi(self):
        """Syntaktická vada ve skriptu se jinak pozná až uprostřed sběru dat."""
        import py_compile
        import tempfile
        for skript in self.SKRIPTY:
            with self.subTest(skript=str(skript.relative_to(ROOT))):
                with tempfile.TemporaryDirectory() as tmp:
                    try:
                        py_compile.compile(str(skript), cfile=f"{tmp}/out.pyc",
                                           doraise=True)
                    except py_compile.PyCompileError as chyba:
                        self.fail(str(chyba))

    def test_skripty_neodvozuji_cil_ze_sveho_umisteni(self):
        """Cíl patří do argumentu, jinak skript nepřežije přesun.

        Generátory archivu si výstup odvozovaly z `__file__` a při stěhování
        do skillu by tiše zapisovaly vedle něj – ne do archivu.
        """
        vadne = [str(s.relative_to(ROOT)) for s in self.SKRIPTY
                 if "__file__" in s.read_text(encoding="utf-8")]
        self.assertFalse(vadne, f"skripty odvozují cestu z vlastního umístění: {vadne}")


if __name__ == "__main__":
    unittest.main()
