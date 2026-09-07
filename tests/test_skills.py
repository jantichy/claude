"""Meta-testy nad konfigurační vrstvou.

Skilly jsou text, který nikdo nespouští, takže se jejich vady projeví až za běhu
a obvykle tiše: režim popsaný v těle, který chybí v `argument-hint`, nebo odkaz
na soubor, který mezitím zmizel. Tohle je nejlevnější vrstva, která je chytí –
stojí nula tokenů a běží v průběžné kontrole.

Spouští se: python3 -m unittest discover -s tests -q

Schválně jen stdlib: kontrola, která si nejdřív žádá instalaci balíčku, se v cizím
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
        bez kontroly a muselo se ověřovat jednorázovým skriptem. Součástí jsou i rozsahy
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

    def test_odkazuje_na_kroky_cyklu_ne_na_jejich_vnitrek(self):
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


class KanonickyTvarAutocommitu(unittest.TestCase):
    """Přepínač autocommitu se pozná jen podle nadpisu, takže na jeho tvaru stojí funkce.

    `/autocommit` hledá nadpis znějící přesně `## Autocommit`; zanořený nebo
    o úroveň nižší nenajde a projekt pak hlásí jako vypnutý, přestože zapnutý je.
    Hlídají se obě strany mechanismu, ale jen v tomhle repozitáři – projekty
    venku žádná kontrola nečte, o ty se stará `/project` v režimu `adopt`.
    """

    def test_projektovy_claude_md_ma_prepinac_i_import(self):
        """Nadpis bez importu je přepínač, který nic nespíná.

        Pravidla autocommitu žijí ve skillu a do projektu se dostanou jedině
        tím importem. Sekce bez něj tedy vypadá zapnutě, ale Claude v takovém
        projektu nemá podle čeho commitovat – a pozná se to až tím, že se
        nic neděje.
        """
        projektovy = (ROOT / ".claude/CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("\n## Autocommit\n", projektovy,
            "projektový CLAUDE.md nemá přepínač na kanonickém místě")
        self.assertIn("@~/.claude/skills/autocommit/autocommit.md", projektovy,
            "sekce Autocommit neimportuje pravidla ze skillu")
        self.assertNotIn("## Automatické akce", projektovy,
            "zastřešující sekce nad jediným podnadpisem se vrátila")

    def test_globalni_claude_md_autocommit_nedefinuje(self):
        """Druhá strana mechanismu: definice se do globálního souboru nesmí vrátit.

        Dokud tam sekce *Autocommit v projektech* stála, rozbalovala se do každé
        session v každém projektu – tedy i tam, kde je autocommit vypnutý.
        Pravidla dnes drží `skills/autocommit/autocommit.md` a importuje si je
        projekt, který je zapnul. Kopie v globálním souboru by ten import
        obcházela a platila všude.
        """
        globalni = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertNotIn("## Autocommit v projektech", globalni,
            "definice autocommitu se vrátila do globálního CLAUDE.md")


class NosneCasti(unittest.TestCase):
    """Ne že skill má správný tvar, ale že v něm je to, co nese jeho funkci.

    Dosavadní testy hlídají hlavičky, odkazy a nadpisy – tedy tvar. Z `/review` šlo
    smazat celou fázi ověřování nálezů, tu, o které skill sám píše, že na ní stojí
    jeho použitelnost, a průběžná kontrola zůstala zelená. Kontrola, která nemůže spadnout
    na věcné vadě, je horší než chybějící kontrola: uspokojuje pravidlo *Ověřitelná
    kontrola místo dojmu*, aniž cokoliv doloží.

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

    def test_cleanup_hleda_nevyporadana_temata(self):
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
        nadpis = "## Fáze 2 – Nevypořádaná témata"
        self.assertIn(nadpis, text, "/cleanup přišel o fázi na nevypořádaná témata")
        faze = text[text.index(nadpis):]
        faze = faze[:faze.index("\n## ")]
        for kus in ("Jak ověřit, že to opravdu není vypořádané", "Práh důležitosti",
                    "AskUserQuestion", "Bezpředmětné"):
            self.assertIn(kus, faze,
                          f"/cleanup, Fáze 2 přišla o {kus!r} – zbyl jen nadpis")

    def test_importy_v_claude_md_nestoji_v_apostrofech(self):
        """Import uvnitř code spanu se nerozbalí a selže to tiše.

        Řádek `@~/cesta/soubor.md` Claude Code vyhodnotí jen tehdy, když `@`
        nestojí uvnitř zpětných apostrofů; jinak je to ukázka cesty, ne import.
        Soubor se pak nenačte, ale `CLAUDE.md` dál vypadá, jako by ta pravidla
        platila – pozná se to jedině tak, že se modelu zeptáš, co má v kontextu.

        Přesně takhle byl rozbitý uživatelský `~/.claude/CLAUDE.md`: RULES.md,
        STRUCTURE.md i PTYDEPE.md v něm byly zapsané jako `` `@~/.claude/RULES.md` ``
        a nenačetl je nikdy nikdo. Nejdražší tichá vada, jaká tu byla – tři
        soubory označené za závazná pravidla, které do session nikdy nedošly.

        `WORKTREE.md` se schválně **neimportuje** a v apostrofech stát smí; test
        proto hlídá jen řádky, kde `@` opravdu je.
        """
        vzor = re.compile(r"`[^`]*@~?[/\w.-]+\.md[^`]*`")
        for soubor in (ROOT / "CLAUDE.md", ROOT / ".claude/CLAUDE.md"):
            if not soubor.exists():
                continue
            for cislo, radek in enumerate(soubor.read_text().splitlines(), 1):
                self.assertFalse(
                    vzor.search(radek),
                    f"{soubor.name}:{cislo} má @import uvnitř apostrofů, "
                    f"takže se tiše nenačte: {radek.strip()[:90]}")

    def test_ptydepe_cte_jen_verzovane_soubory(self):
        """Nejdražší chyba, jakou tenhle skill umí udělat, a stala se.

        Náhrada termínu pouštěná rekurzivně přes adresář přepsala v `~/.claude`
        1 120 souborů mimo verzování – transkripty starých session, `history.jsonl`,
        cache i `file-history/`. V `.gitignore` jsou všechny, jenže rekurzivnímu
        průchodu to nevadí, a protože je git nezná, nešlo to vrátit.

        `git ls-files` ten problém neřeší náhodou, ale z definice: vrací výhradně
        to, co je ve verzování, takže se skript k ignorovaným souborům nedostane
        ani omylem. Zákaz `rglob`/`find` je tedy nosná část skillu, ne styl zápisu –
        proto se hlídá jmenovitě a uvnitř té fáze, ne kdekoliv v souboru.
        """
        text = body(ROOT / "skills/ptydepe/SKILL.md")
        nadpis = "## Fáze 4 – Inventura a vyloučení"
        self.assertIn(nadpis, text, "/ptydepe přišel o fázi inventury a vyloučení")
        faze = text[text.index(nadpis):]
        faze = faze[:faze.index("\n## ")]
        self.assertIn("git ls-files", faze,
                      "/ptydepe, Fáze 4 už nepředepisuje git ls-files")
        for zakazane in ("rglob", "find"):
            self.assertIn(zakazane, faze,
                          f"/ptydepe, Fáze 4 přestala jmenovat {zakazane!r} jako zakázaný průchod")

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

        `~/.claude/STRUCTURE.md`, *Běhový stav skillů*. Skill, který
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

    `WORKTREE.md` má v ukázce stubu `## Odchylky`; brát to jako nadpis dokumentu
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


def _blok_zivotniho_cyklu() -> str:
    """Blok s životním cyklem z `RULES.md`.

    Obě funkce níž ho potřebují a měly to zdvojené. Dvě kopie téhož parsování se
    v hraničním případě rozejdou – a rozešly se: jedna četla kroky bez ohledu na
    tvar šipky, druhá jen z řádků s doslovným „→“, takže po záměně za `->` viděla
    každá jiný počet kroků a nic to nehlásilo.
    """
    text = (ROOT / "RULES.md").read_text(encoding="utf-8")
    i = text.index("### Životní cyklus projektu")
    blok = text[text.index("```", i) + 3:]
    return blok[:blok.index("```")]


def cyklus_z_rules() -> set:
    """Kroky životního cyklu se čtou z `RULES.md`, ne z konstanty v testu.

    Ručně opsaný seznam je druhá kopie pravdy: přejmenovaný nebo přidaný krok by
    testem prošel, a naopak zmizelý krok by ho shodil z jiného důvodu, než je ten
    skutečný.
    """
    return set(re.findall(r"/([a-z][a-z-]*)", _blok_zivotniho_cyklu()))


def cyklus_s_poradim() -> dict:
    """Kroky životního cyklu i s pořadím a fází, ne jen jako množina.

    `cyklus_z_rules()` vrací set, takže na tvrzení „je to třetí krok zakládání“
    nestačí. Zdrojem je týž blok v `RULES.md`, jen se z něj čte i pořadí řádků.

    Vrací {skill: (fáze, index v rámci fáze od 1, předchůdce, následník)};
    předchůdce a následník jdou napříč fázemi, protože `/review` navazuje na
    `/implement` z předchozí fáze.
    """
    poradi, faze_radku = [], []
    for radek in _blok_zivotniho_cyklu().splitlines():
        # Řádek fáze pozná podle toho, že na něm jsou kroky – ne podle šipky mezi
        # nimi. Záměna „→“ za „->“ by jinak celou fázi tiše vyhodila.
        kroky = re.findall(r"/([a-z][a-z-]*)", radek)
        if not kroky:
            continue
        faze = radek.split()[0].lower()
        faze_radku.append((faze, kroky))
        poradi.extend(kroky)

    out = {}
    for faze, kroky in faze_radku:
        for n, krok in enumerate(kroky, start=1):
            g = poradi.index(krok)
            out[krok] = (faze, n,
                         poradi[g - 1] if g > 0 else None,
                         poradi[g + 1] if g + 1 < len(poradi) else None)
    return out


#: Řetěz tří a víc kroků životního cyklu spojených šipkami. Dva sousedi jsou
#: popis vazby („navazuje na `/specify`, předává `/breakdown`“), tři a víc už
#: je opsané pořadí celého cyklu – tedy druhý zdroj pravdy vedle `RULES.md`.
#: Řetěz kroků: šipka, nebo próza. **První spojka musí být silná** (šipka nebo
#: „pak“) a teprve druhá smí být slabá („a“, čárka) – vzorec „A, pak B a C“.
#: Samotné „a“ mezi dvěma skilly je totiž běžný výčet, ne posloupnost:
#: „vzniknou prací v `/discovery` a `/specify`, a `/cleanup` pak…“ posloupnost
#: netvrdí a hlásit ho jako opsaný cyklus by kontrolu shodilo na falešném nálezu.
#: Mezera se schválně bere bez konce řádku (`[^\S\n]`): se `\s` by vzor spojil
#: tři nesouvisející zmínky ob několik odstavců.
_M = r"[^\S\n]*"
_KROK = r"`?/([a-z][a-z-]*)`?"
_SILNA = rf"{_M}(?:→|->|,?{_M}(?:pak|potom)){_M}"
_SLABA = rf"{_M}(?:→|->|,|{_M}(?:pak|potom|a)){_M}"
_SIPKA = re.compile(rf"{_KROK}{_SILNA}{_KROK}{_SLABA}{_KROK}")


def retezy_kroku_cyklu(text: str, cyklus: set) -> list:
    """Vrátí opsané řetězy kroků životního cyklu nalezené v textu.

    Vada, kterou to chytá, je tichá a drahá: `/project` psal do každého
    vývojářského `CLAUDE.md` cestu `/specify → /oponent → /breakdown →
    /implement`. Když do cyklu přibyl `/discovery`, řetěz zůstal formálně
    správný – jen neúplný –, takže ho žádná kontrola na existenci ani na
    pořadí neodhalila a projekty ho četly jako úplný seznam.
    """
    return ["/" + " → /".join(trojice) for trojice in _SIPKA.findall(text)
            if all(krok in cyklus for krok in trojice)]


class KontraktPrikazu(unittest.TestCase):
    """Formát kontraktu je závazný, protože ho čte skript – a to se neověřovalo.

    `coding.md` říká „jeden řádek na klíč, `- klíč: příkaz`, a za příkazem už nic“.
    Změna formátu (komentář za příkazem, jiné odsazení, hodnota v bloku kódu)
    vypne kontrolu **tiše**: `sed` v `verify.sh` prostě nic nenajde a hook se
    zachová, jako by ten krok projekt neměl.
    """

    KONTRAKT = ROOT / ".claude/CLAUDE.md"

    def _sekce(self) -> str:
        """Sekce ## Příkazy z těla bez bloků kódu – stejně jako `md_body`
        a `contract_section` v `verify.sh`."""
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
        """Týž výraz jako `cmd_for` v verify.sh."""
        m = re.search(rf"^[ \t]*[-*][ \t]*{klic}:[ \t]+(.*?)[ \t]*$",
                      self._sekce(), re.M)
        return m.group(1) if m else None

    def test_kontrakt_se_da_precist(self):
        """Kdyby se sekce rozešla s formátem, průběžná kontrola by tu tiše neběžela."""
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
        # Obě funkce čtou týž blok. Rozejdou-li se, jedna z nich přestala vidět
        # celý cyklus – a volný práh výš to sám neodhalí, protože výpadek dvou
        # kroků z cyklu nechá pořád dost na to, aby práh nesplnil.
        self.assertEqual(self.CYKLUS, set(cyklus_s_poradim()),
            "cyklus_z_rules() a cyklus_s_poradim() čtou z RULES.md jinou množinu kroků")
        chybi = sorted(self.CYKLUS - {s.parent.name for s in SKILLS})
        self.assertFalse(chybi, f"životní cyklus jmenuje kroky, které nemají skill: {chybi}")


    def test_skill_neopisuje_retez_kroku_cyklu(self):
        """Pořadí kroků cyklu se odkazuje, neopisuje.

        Opsaný řetěz se při přidání kroku rozejde se zdrojem a vypadá přitom
        pořád platně – v `SKILL.md` i v každém `CLAUDE.md`, do kterého ho ten
        skill jako šablonu zapsal. Zdrojem pravdy je blok v `RULES.md`.
        """
        for skill in SKILLS:
            with self.subTest(skill=skill.parent.name):
                nalezy = retezy_kroku_cyklu(body(skill), self.CYKLUS)
                self.assertFalse(nalezy,
                    f"{skill.parent.name} opisuje pořadí kroků cyklu: {nalezy}; "
                    "odkaž se na *Životní cyklus projektu* v RULES.md")

    CISLOVKY = {"první": 1, "druhý": 2, "třetí": 3, "čtvrtý": 4,
                "pátý": 5, "šestý": 6, "sedmý": 7}

    def test_veta_o_poradi_kroku_sedi_s_rules(self):
        """Skill tvrdí, kolikátý je a na koho navazuje – nic to neměřilo.

        Vložení kroku doprostřed životního cyklu posune čísla všem za ním, jenže
        ta čísla stojí prózou v `Co skill dělá` každého skillu.
        `test_vnitroskillove_odkazy_na_faze_miri_na_existujici_nadpis` je schválně
        vynechává (míří mimo vlastní číslování skillu), takže regrese prošla tiše
        a našel ji až audit. Zdrojem pravdy je `RULES.md`.
        """
        cyklus = cyklus_s_poradim()
        self.assertEqual(set(cyklus), self.CYKLUS,
            f"cyklus_s_poradim() vrátil jinou množinu kroků než cyklus_z_rules(): {sorted(cyklus)}")

        vzor = re.compile(
            r"je to \*{0,2}(\w+) krok (zakládání|uzavírání|nasazení)\*{0,2}"
            r"(?:[:\s–-]+navazuje na `/([a-z-]+)`)?"
            r"(?:\s+a předává na `/([a-z-]+)`)?")
        chyby, nalezeno = [], 0
        for skill in SKILLS:
            jmeno = skill.parent.name
            if jmeno not in cyklus:
                continue
            text = body(skill)
            m = vzor.search(text)
            if not m:
                # Skill, který o svém pořadí mluví, ale vzor na tvar té věty
                # nesedne, se dřív tiše přeskočil – a jeho tvrzení pak neověřil
                # nikdo. Přeformulovat větu se smí, ale ne potichu.
                # Bez tečky ve vyloučení: tvar „3. krok“ ji obsahuje, a právě ten
                # se dřív přeskočil, protože detekce sama na něj nesedla.
                if re.search(r"je to [^\n]{0,25}krok (?:zakládání|uzavírání|nasazení)", text):
                    chyby.append(f"{jmeno}: mluví o svém pořadí, ale vzor na tvar té věty nesedne "
                                 f"– přeformuluj ji, nebo uprav vzor v testu")
                continue
            nalezeno += 1
            cislovka, faze, predchudce, naslednik = m.groups()
            ocek_faze, ocek_n, ocek_pred, ocek_nasl = cyklus[jmeno]

            if faze != ocek_faze:
                chyby.append(f"{jmeno}: tvrdí fázi `{faze}`, RULES.md má `{ocek_faze}`")
            if cislovka == "poslední":
                # „Poslední“ se ověřuje jen proti počtu kroků ve fázi. Následník
                # se posuzuje níž stejně jako u číslovaných kroků: poslední krok
                # fáze ho legitimně má – `/cleanup` uzavírá uzavírání a přitom
                # správně předává na `/attack` z nasazení.
                kroku_ve_fazi = len([k for k, v in cyklus.items() if v[0] == ocek_faze])
                if ocek_n != kroku_ve_fazi:
                    chyby.append(f"{jmeno}: tvrdí, že je poslední ve fázi `{faze}`, "
                                 f"ale je {ocek_n}. z {kroku_ve_fazi}")
            elif self.CISLOVKY.get(cislovka) != ocek_n:
                chyby.append(f"{jmeno}: tvrdí `{cislovka} krok`, podle RULES.md je {ocek_n}.")
            if predchudce and predchudce != ocek_pred:
                chyby.append(f"{jmeno}: tvrdí, že navazuje na `/{predchudce}`, RULES.md má `/{ocek_pred}`")
            if naslednik and naslednik != ocek_nasl:
                chyby.append(f"{jmeno}: tvrdí, že předává na `/{naslednik}`, RULES.md má `/{ocek_nasl}`")

        # Druhý tvar téhož tvrzení: `/project` píše „Je první článek Životního
        # cyklu projektu“. Vzor výš ho nepoznal, takže se skill tiše přeskakoval
        # – a právě on nesl vadu, kvůli které tenhle test vznikl (posílal na
        # `/specify`, ačkoli jeho následník je `/discovery`).
        poradi = [k for k, v in sorted(cyklus.items(), key=lambda x: (x[1][0], x[1][1]))]
        for skill in SKILLS:
            jmeno = skill.parent.name
            if jmeno not in cyklus:
                continue
            m = re.search(r"Je (první|poslední) článek \*Životního cyklu projektu\*", body(skill))
            if not m:
                continue
            nalezeno += 1
            ma_byt = cyklus[jmeno][2] is None if m.group(1) == "první" else cyklus[jmeno][3] is None
            if not ma_byt:
                chyby.append(f"{jmeno}: tvrdí, že je {m.group(1)} článek cyklu, "
                             f"ale RULES.md má na tom místě `/{poradi[0 if m.group(1) == 'první' else -1]}`")

        # Přesný počet, ne práh: při volném prahu propadne skill, jehož větu vzor
        # přestal poznávat, protože ostatní ho vyváží. Zvedne-li se počet skillů,
        # které tu větu nesou, číslo se tu vědomě upraví. Jde do téhož seznamu
        # jako ostatní chyby, aby se konkrétní nález nezakryl souhrnným číslem.
        # Zbylé kroky své pořadí netvrdí vůbec, takže tady není co měřit –
        # že jmenují oba sousedy, hlídá `test_co_skill_nedela_jmenuje_oba_sousedy`.
        if nalezeno != 7:
            chyby.append(f"větu o pořadí kroku nese {nalezeno} skillů, čekalo se 7 "
                         f"– změnil se její tvar, nebo ji získal či ztratil další skill?")
        self.assertFalse(chyby, "věty o pořadí kroku nesedí s RULES.md:\n  " + "\n  ".join(chyby))

    def test_kroky_cyklu_maji_sekci_co_nedela(self):
        """Bez vymezení vůči sousedům se práce buď zdvojí, nebo neudělá vůbec."""
        chybi = [s.parent.name for s in SKILLS
                 if s.parent.name in self.CYKLUS and "Co skill nedělá" not in body(s)]
        self.assertFalse(chybi, f"skilly životního cyklu bez sekce `Co skill nedělá`: {chybi}")

    def test_co_skill_nedela_jmenuje_oba_sousedy(self):
        """Norma žádá jmenované sousedy, měřila se ale jen existence nadpisu.

        Vada, kterou to propustilo: `/project` roky posílal na `/specify`
        a o svém skutečném následníkovi `/discovery` nevěděl, přestože
        `SKILLS.md`, *Povinné sekce a jejich pořadí*, jmenované sousedy
        z obou stran u kroků cyklu vyžaduje.

        **Hledá se jen v úvodních sekcích**, ne v celém těle. Nad celým tělem
        kontrola nic neměří: `/project` jmenuje `/discovery` i v tabulce
        produktových podkladů, takže by prošel, i kdyby se o svém sousedovi
        nezmínil ani slovem – doloženo mutací, která tu vadu vrátila a testem
        prošla. Vymezení patří do `Co skill dělá` a `Co skill nedělá`, tedy do
        textu před první fází.
        """
        cyklus = cyklus_s_poradim()
        chybi = []
        for skill in SKILLS:
            jmeno = skill.parent.name
            if jmeno not in cyklus:
                continue
            text = body(skill)
            konec = text.find("\n## Fáze")
            if konec == -1:
                konec = text.find("\n## Krok")
            text = text[:konec] if konec != -1 else text
            _, _, pred, nasl = cyklus[jmeno]
            for soused in (pred, nasl):
                if soused and f"/{soused}" not in text:
                    chybi.append(f"{jmeno} nejmenuje souseda /{soused}")
        self.assertFalse(chybi, "kroky cyklu se nevymezují vůči sousedům:\n  " + "\n  ".join(chybi))

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

    Norma vznikla později než skilly, takže třináct z nich ji zatím nesplňuje.
    Převod je vědomý běh `/skill update`, ne vedlejší efekt jiné práce – proto
    seznam `MIGRACE` místo třinácti padajících testů.

    Seznam ale neumlčuje – **musí přesně sedět se skutečností** a test to hlídá
    v obou směrech. Skill, který se opraví a nezmizí ze seznamu, test shodí
    stejně jako skill, který se rozbije. Bez toho by seznam tiše zůstal i po dokončení migrace a přestal by
    cokoliv měřit.
    """

    NORMA = ROOT / "skills" / "SKILLS.md"
    PREFLIGHT = ROOT / "skills" / "PREFLIGHT.md"

    #: Skilly, které ještě neprošly `/skill update`. Zkracuje se, nikdy nedoplňuje.
    MIGRACE = {
        "attack", "breakdown", "cleanup", "consistency",
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
            out.append("chybí závěrečný verdikt")
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
        kontrola chytit nemohla.
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
        """Seznam MIGRACE musí přesně sedět: skill mimo normu nechybí ani nepřebývá."""
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
        # a závěrečný verdikt dvakrát, takže mutace jednoho výskytu nic nezmění
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


    def test_opsany_retez_kroku_cyklu_se_nahlasi(self):
        """Kontrola opsaného cyklu bez mutace nedokazuje nic – žádný skill ho dnes nemá."""
        cyklus = cyklus_z_rules()
        cisty = self.VZOR.read_text(encoding="utf-8")
        self.assertFalse(retezy_kroku_cyklu(cisty, cyklus), "vzor už řetěz obsahuje")
        for text in ("postupuj takhle: `/specify` → `/oponent` → `/breakdown`",
                     "cesta /specify -> /oponent -> /breakdown"):
            with self.subTest(text=text):
                self.assertTrue(retezy_kroku_cyklu(cisty + "\n" + text, cyklus),
                                f"kontrola nechytila opsaný řetěz: {text!r}")
        # Dva sousedi se hlásit nesmějí, jinak by pravidlo zakázalo popis vazby
        self.assertFalse(retezy_kroku_cyklu("`/specify` → `/breakdown`", cyklus))

    def test_chybejici_odkaz_na_preflight_se_nahlasi(self):
        vady = self.mutuj(("PREFLIGHT.md", "JINY.md"))
        self.assertIn("pre-flight neodkazuje na `skills/PREFLIGHT.md`", vady, vady)

    def test_chybejici_zaverecny_verdikt_se_nahlasi(self):
        vady = self.mutuj(("Zakonči jednou z těchto vět", "Skonči nějak"))
        self.assertIn("chybí závěrečný verdikt", vady, vady)

    def test_odkaz_dovnitr_ciziho_skillu_se_nahlasi(self):
        vady = self.mutuj(("## Fáze 3 – Tabulka švů",
                           "## Fáze 3 – Tabulka švů\n\nPostupem z `/review`, Fáze 0.1."))
        self.assertIn("odkazuje dovnitř fáze jiného skillu", vady, vady)

    def test_spatne_poradi_sekci_se_nahlasi(self):
        """`Časté chyby` u skillu s přílohami musí stát naposled."""
        import shutil, tempfile
        text = self.VZOR.read_text(encoding="utf-8")
        i = text.index("\n## Časté chyby")
        # Poslední fáze se hledá jako poslední nadpis `## Fáze …`, ne jménem:
        # závěr se podle normy jmenovat nemusí („Úklid a shrnutí“, „Předání“)
        # a přečíslování by test shodilo hláškou o chybějícím podřetězci
        # místo nálezem. Týmž kritériem pozná závěr i kontrola samotná.
        j = max(m.start() for m in re.finditer(r"\n## Fáze [0-9]", text))
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


def povinne_sekce_readme() -> tuple:
    """Nadpisy, které norma žádá po každé vizitce – čtené ze `SKILLS.md`.

    Schválně ne z konstanty v testu. Kontrola měřená vlastní konfigurací
    nehlídá nic: dokud tenhle seznam stál natvrdo, dalo se ho zkrátit na
    polovinu a mutační testy prošly, protože iterovaly přes tutéž zkrácenou
    n-tici. Zdrojem pravdy je norma; test z ní jen čte.

    Sekce označené šipkou (`← jen má-li skill…`) jsou podmíněné a vypadnou.
    """
    text = (ROOT / "skills/SKILLS.md").read_text(encoding="utf-8")
    zacatek = text.index("### Struktura")
    blok = text[text.index("```", zacatek) + 3:]
    blok = blok[:blok.index("```")]
    sekce = tuple(r.strip() for r in blok.splitlines()
                  if r.startswith(("## ", "### ")) and "←" not in r)
    if len(sekce) < 5:
        raise AssertionError(f"ze `SKILLS.md` se přečetlo jen {len(sekce)} sekcí: {sekce}")
    return sekce


#: Nadpisy, které norma žádá po každém README skillu – v pořadí z normy.
POVINNE_README = povinne_sekce_readme()

#: Mez z normy: zhruba dvě obrazovky.
MEZ_README = 120

REPO_URL = "https://github.com/jantichy/claude/tree/main/skills/"

RAMECEK = "**Součást životního cyklu projektu.**"
HROMADNA = "Nebo celou sadu naráz."


def vady_readme(text: str, jmeno: str, v_cyklu: bool) -> list:
    """Vrátí vady jednoho README proti normě *README skillu*.

    Čistá funkce nad textem, ne nad diskem – jedině tak se dá předložit
    poškozený vstup a ověřit, že kontrola nález opravdu nahlásí
    (`KontrolyOpravduChytaji`). Kontroly, které potřebují hlavičku skillu
    nebo souborový systém, mají vlastní testy.
    """
    vady = []

    # Přítomnost i pořadí. Pořadí sem patří proto, že ho norma žádá a `/skill`
    # při revizi kontroluje – bez kontroly je to pravidlo, které drží jen ten,
    # kdo si na ně vzpomene.
    pozice = []
    for nadpis in POVINNE_README:
        i = text.find(f"\n{nadpis}")
        if i < 0:
            vady.append(f"chybí sekce `{nadpis}`")
        else:
            pozice.append((i, nadpis))
    poradi = [n for _, n in sorted(pozice)]
    ocekavane = [n for n in POVINNE_README if n in poradi]
    if poradi != ocekavane:
        vady.append(f"sekce nejdou v pořadí z normy: {poradi} místo {ocekavane}")

    # Instalace musí být pokyn pro Clauda uvnitř své sekce, ne URL kdekoliv.
    zacatek = text.find("## Jak si ho nainstalovat")
    if zacatek < 0:
        pass                                  # hlásí kontrola sekcí výš
    else:
        konec = text.find("\n---", zacatek)
        sekce = text[zacatek:konec if konec > 0 else len(text)]
        url = REPO_URL + jmeno
        citace = [r for r in sekce.splitlines() if r.lstrip().startswith(">")]
        if url not in sekce:
            vady.append(f"instalační sekce neodkazuje na {url}")
        elif not any(url in r for r in citace):
            vady.append("odkaz na repozitář není v citovaném pokynu pro Clauda")

    # Rámeček a hromadná instalace: povinné v cyklu, zakázané mimo něj.
    if v_cyklu:
        if RAMECEK not in text:
            vady.append("chybí rámeček s celým životním cyklem")
        if HROMADNA not in text:
            vady.append("chybí hromadná instalace celého životního cyklu")
    else:
        if RAMECEK in text:
            vady.append("skill mimo životní cyklus má rámeček životního cyklu")
        if HROMADNA in text:
            vady.append("skill mimo životní cyklus nabízí hromadnou instalaci sady")

    radku = len(text.splitlines())
    if radku > MEZ_README:
        vady.append(f"README má {radku} řádků, mez je {MEZ_README}")

    return vady


class ReadmeSkillu(unittest.TestCase):
    """README skillu proti `skills/SKILLS.md`, *README skillu*.

    Je to jediná část skillu psaná **pro člověka zvenčí** – text, na který
    se posílá odkaz. Právě proto se rozpadá tiše: chybějící sekce nikoho za
    běhu neomezí a pozná se až ve chvíli, kdy si ji někdo cizí přečte.
    """

    CYKLUS = cyklus_z_rules()

    def _readme(self, skill: Path) -> Path:
        return skill.parent / "README.md"

    def test_kazdy_skill_ma_readme(self):
        """Skill bez README nejde nikomu doporučit odkazem."""
        chybi = [s.parent.name for s in SKILLS if not self._readme(s).exists()]
        self.assertFalse(chybi, f"skilly bez vlastního README: {chybi}")

    def test_readme_odpovida_norme(self):
        """Sekce a jejich pořadí, tvar instalace, rámeček a mez délky.

        Jedna kontrola místo pěti, protože všechny měří týž text proti téže
        sekci normy – a hlavně proto, že se pak dá mutovat jako celek
        (`KontrolyOpravduChytaji`).
        """
        for skill in SKILLS:
            readme = self._readme(skill)
            if not readme.exists():
                continue
            with self.subTest(skill=skill.parent.name):
                vady = vady_readme(readme.read_text(encoding="utf-8"),
                                   skill.parent.name,
                                   skill.parent.name in self.CYKLUS)
                self.assertFalse(vady, f"{readme}: {vady}")

    def test_readme_skillu_z_cyklu_odkazuje_na_ostatni_kroky(self):
        """Čtenář, kterému přišel odkaz na jeden skill, jinak neví o těch ostatních."""
        for skill in SKILLS:
            if skill.parent.name not in self.CYKLUS:
                continue
            readme = self._readme(skill)
            if not readme.exists():
                continue
            with self.subTest(skill=skill.parent.name):
                text = readme.read_text(encoding="utf-8")
                vlastni = skill.parent.name
                self.assertTrue(f"**`/{vlastni}`**" in text,
                    f"{readme}: vlastní krok není v rámečku tučně")
                self.assertFalse(f"(../{vlastni}/README.md)" in text,
                    f"{readme}: rámeček odkazuje sám na sebe – vlastní krok je bez odkazu")
                for krok in sorted(self.CYKLUS):
                    if krok == vlastni:
                        continue
                    self.assertTrue(f"(../{krok}/README.md)" in text,
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
            # Do konce odstavce, ne pevným oknem: výčet kroků roste s cyklem
            # a u `/attack` už dnes měří přesně 800 znaků. Uříznuté jméno by
            # test nahlásil jako chybějící, přestože v README je.
            # Konec sekce, ne konec odstavce: samotný prompt stojí v citaci pod
            # úvodní větou, takže první prázdný řádek by usekl právě ten výčet.
            konce = [text.find(z, i) for z in ("\n---", "\n## ")]
            konce = [k for k in konce if k > 0]
            odstavec = text[i:min(konce) if konce else len(text)]
            with self.subTest(skill=skill.parent.name):
                for krok in sorted(self.CYKLUS):
                    self.assertRegex(odstavec, rf"\b{krok}\b",
                        f"{readme}: hromadná instalace nejmenuje `{krok}`")

    def test_readme_jmenuje_vsechny_rezimy(self):
        """Režim, který README zamlčí, uživatel nikdy nepoužije.

        Bere se první skupina `argument-hint` a jen tehdy, když je to výčet
        jmen režimů (`[create|adopt|update]`), ne zástupný text (`[dokument]`,
        `[větev|tag|hash]`). Výchozí režim se jmenuje taky – bez toho ho nejde
        napsat explicitně.
        """
        for skill in SKILLS:
            hint = frontmatter(skill).get("argument-hint", "")
            skupina = re.match(r"\[([^\]]+)\]", hint)
            if not skupina or "|" not in skupina.group(1):
                continue
            rezimy = skupina.group(1).split("|")
            if not all(re.fullmatch(r"[a-z]+", r) for r in rezimy):
                continue
            readme = self._readme(skill)
            if not readme.exists():
                continue
            text = readme.read_text(encoding="utf-8")
            for rezim in rezimy:
                with self.subTest(skill=skill.parent.name, rezim=rezim):
                    # Stačí jméno režimu v kódové značce – ať už s lomítkem
                    # (`/skill update`), nebo samo (`update`) tam, kde README
                    # režimy vypisuje jako seznam.
                    self.assertTrue(
                        f"`{rezim}`" in text or f"/{skill.parent.name} {rezim}" in text,
                        f"{readme}: režim `{rezim}` z argument-hint není v README")

    def test_relativni_odkazy_v_readme_miri_na_existujici_soubor(self):
        """Rozbitý odkaz mezi README uvidí ten, komu se skill doporučuje.

        Kontrola `test_odkazy_na_soubory_existuji` na tohle nestačí – ta hledá
        cesty v obrácených apostrofech (`~/.claude/…`), kdežto README používají
        markdownové odkazy s relativní cestou. Rámečkové odkazy sice kryje
        `test_readme_skillu_z_cyklu_odkazuje_na_ostatni_kroky`, ale jen
        ty – odkaz kamkoliv jinam procházel tiše.
        """
        odkaz = re.compile(r"\]\(([^)\s#]+\.(?:md|sh|py|png|json))\)")
        soubory = [s.parent / "README.md" for s in SKILLS] + [ROOT / "README.md"]
        for readme in soubory:
            if not readme.exists():
                continue
            with self.subTest(readme=readme.parent.name):
                chybi = sorted({
                    cil for cil in odkaz.findall(readme.read_text(encoding="utf-8"))
                    if not cil.startswith(("http://", "https://", "~/"))
                    and not (readme.parent / cil).resolve().exists()
                })
                self.assertFalse(chybi, f"{readme}: odkaz na neexistující soubor: {chybi}")

    def test_sablona_v_norme_jmenuje_vsechny_kroky(self):
        """README hlídá test, normu samotnou dosud nic.

        Šablona hromadné instalace v `SKILLS.md` vyjmenovává kroky cyklu
        jménem – přidaný krok by ji tiše rozešel, tedy přesně to riziko,
        kvůli kterému norma o kus výš zakazuje uvádět v rámečku počet.
        """
        norma = (ROOT / "skills/SKILLS.md").read_text(encoding="utf-8")
        i = norma.find(HROMADNA)
        self.assertGreater(i, 0, "v normě chybí šablona hromadné instalace")
        konec = norma.find("```", norma.find("```", i) + 3)
        sablona = norma[i:konec if konec > 0 else len(norma)]
        for krok in sorted(self.CYKLUS):
            with self.subTest(krok=krok):
                self.assertRegex(sablona, rf"\b{krok}\b",
                    f"šablona hromadné instalace v SKILLS.md nejmenuje `{krok}`")

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
    """Skripty ve skillech nečte žádná jiná kontrola.

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


class KontrolyVizitekOpravduChytaji(unittest.TestCase):
    """Mutační testy nad `vady_readme()`.

    Vrstva vizitek přibyla jako poslední a byla jediná bez důkazu, že něco
    chytá – `.claude/CLAUDE.md` přitom o mutacích mluvil tak, že je zahrnoval.
    Platí tu totéž co o mutacích nad `SKILL.md`: kontrola, která nic nechytá,
    projde stejně tiše jako ta funkční.

    Mutuje se nad skutečnými README: `/attack` je v životním cyklu,
    `/report` mimo něj, takže pokrývají obě větve funkce.
    """

    V_CYKLU = ROOT / "skills/attack/README.md"
    MIMO = ROOT / "skills/report/README.md"

    def vady(self, vzor: Path, jmeno: str, v_cyklu: bool, nahrada=None) -> list:
        text = vzor.read_text(encoding="utf-8")
        if nahrada is not None:
            stary, novy = nahrada
            self.assertIn(stary, text, f"mutace se nemá čeho chytit: {stary!r}")
            text = text.replace(stary, novy)
        return vady_readme(text, jmeno, v_cyklu)

    def test_vzory_jsou_ciste(self):
        """Bez tohohle by mutace nedokazovaly nic – vady by mohly být původní."""
        self.assertFalse(self.vady(self.V_CYKLU, "attack", True))
        self.assertFalse(self.vady(self.MIMO, "report", False))

    def test_chybejici_sekce_se_nahlasi(self):
        """Každá povinná sekce zvlášť – jinak jde tři z šesti přestat vynucovat.

        Doloženo: dokud se mutovala jen `## Co nedělá`, prošlo zkrácení
        `POVINNE_README` na polovinu bez jediného padlého testu.
        """
        for nadpis in POVINNE_README:
            with self.subTest(sekce=nadpis):
                # Nadpis musí zmizet, ne se prodloužit: `## Co umí jinak`
                # pořád obsahuje `## Co umí` a kontrola by ho našla dál.
                vady = self.vady(self.MIMO, "report", False,
                                 ("\n" + nadpis, "\n" + nadpis.replace("#", "@", 1)))
                self.assertTrue(any(f"chybí sekce `{nadpis}`" in v for v in vady), vady)

    def test_prohozene_poradi_sekci_se_nahlasi(self):
        text = self.MIMO.read_text(encoding="utf-8")
        i, j = text.index("\n## Co umí"), text.index("\n## Proč zrovna tenhle")
        prohozeny = (text[:i] + text[j:j + len("\n## Proč zrovna tenhle")]
                     + text[i + len("\n## Co umí"):j]
                     + "\n## Co umí" + text[j + len("\n## Proč zrovna tenhle"):])
        vady = vady_readme(prohozeny, "report", False)
        self.assertTrue(any("pořadí" in v for v in vady), vady)

    def test_chybejici_ramecek_u_skillu_z_cyklu_se_nahlasi(self):
        vady = self.vady(self.V_CYKLU, "attack", True,
                         ("**Součást životního cyklu projektu.**", "**Poznámka.**"))
        self.assertTrue(any("rámeček" in v for v in vady), vady)

    def test_ramecek_u_skillu_mimo_cyklus_se_nahlasi(self):
        text = self.MIMO.read_text(encoding="utf-8")
        radky = text.split("\n")
        radky.insert(2, "> **Součást životního cyklu projektu.** …")
        vady = vady_readme("\n".join(radky), "report", False)
        self.assertTrue(any("má rámeček" in v for v in vady), vady)

    def test_chybejici_hromadna_instalace_se_nahlasi(self):
        vady = self.vady(self.V_CYKLU, "attack", True, (HROMADNA, "Nebo taky ne."))
        self.assertTrue(any("hromadná instalace" in v for v in vady), vady)

    def test_hromadna_instalace_u_skillu_mimo_cyklus_se_nahlasi(self):
        """Předstírat sadu u skillu, který se pouští samostatně, by mátlo."""
        text = self.MIMO.read_text(encoding="utf-8").replace(
            "## Jak si ho nainstalovat", "## Jak si ho nainstalovat\n\n" + HROMADNA, 1)
        vady = vady_readme(text, "report", False)
        self.assertTrue(any("hromadnou instalaci" in v for v in vady), vady)

    def test_instalace_mimo_citovany_pokyn_se_nahlasi(self):
        """URL kdekoliv v souboru nestačí – musí být v pokynu pro Clauda."""
        vady = self.vady(self.MIMO, "report", False,
                         ("> Jdi na " + REPO_URL + "report", "Jdi na " + REPO_URL + "report"))
        self.assertTrue(any("citovaném pokynu" in v for v in vady), vady)

    def test_chybejici_odkaz_na_repozitar_se_nahlasi(self):
        vady = self.vady(self.MIMO, "report", False, (REPO_URL + "report", "https://example.com"))
        self.assertTrue(any("neodkazuje" in v for v in vady), vady)

    def test_prekrocena_mez_delky_se_nahlasi(self):
        """Těsně o jeden řádek – jinak by mutace dokazovala jen řádovou nerovnost."""
        text = self.MIMO.read_text(encoding="utf-8")
        chybi = MEZ_README - len(text.splitlines()) + 1
        self.assertGreater(chybi, 0, "vzor už mez přetahuje, mutace by nic nedokázala")
        vady = vady_readme(text + "\n" * chybi, "report", False)
        self.assertTrue(any("mez je" in v for v in vady), vady)
        self.assertFalse(vady_readme(text + "\n" * (chybi - 1), "report", False),
                         "kontrola hlásí vadu ještě před překročením meze")


if __name__ == "__main__":
    unittest.main()
