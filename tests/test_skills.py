"""Meta-testy nad konfigurační vrstvou.

Skilly jsou text, který nikdo nespouští, takže se jejich vady projeví až za běhu
a obvykle tiše: režim popsaný v těle, který chybí v `argument-hint`, nebo odkaz
na soubor, který mezitím zmizel. Tohle je nejlevnější vrstva, která je chytí –
stojí nula tokenů a běží v průběžné kontrole.

Spouští se: python3 -m unittest discover -s tests -q

Schválně jen stdlib: kontrola, která si nejdřív žádá instalaci balíčku, se v cizím
prostředí neprojeví jako nález, ale jako rozbitý nástroj – a ten se obchází.
"""
import os
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
    def test_required_fields(self):
        """Bez `name` a `description` se skill nenabídne k vyvolání."""
        for skill in SKILLS:
            with self.subTest(skill=skill.parent.name):
                fm = frontmatter(skill)
                self.assertTrue(fm.get("name"), f"{skill}: chybí `name` v hlavičce")
                self.assertTrue(fm.get("description"), f"{skill}: chybí `description`")
                self.assertEqual(fm["name"], skill.parent.name,
                    f"{skill}: `name: {fm.get('name')}` nesedí s adresářem")

    def test_auxiliary_files_do_not_link_into_foreign_skill(self):
        """Zákaz odkazu dovnitř cizí fáze platí i mimo `SKILL.md`.

        Kontrolovala se jen těla skillů, takže vedlejší soubory z něj tiše
        vypadávaly – `skills/ptydepe/terms.md` jich nasbíral 8. Přečíslovaná
        fáze souseda pak ukazuje jinam a nic to nehlásí.

        Odkaz na **vlastní** fázi je v pořádku a pozná se podle jména adresáře;
        bez téhle výjimky by kontrola hlásila i legitimní vnitroskillové odkazy.
        """
        defects = []
        for file in sorted((ROOT / "skills").glob("*/*.md")):
            if file.name in ("SKILL.md", "README.md"):
                continue
            own = file.parent.name
            for m in StandardCompliance.FOREIGN_PHASE.finditer(body(file)):
                if f"`/{own}`" in m.group(0):
                    continue
                defects.append(f"{file.relative_to(ROOT)}: {m.group(0)!r}")
        self.assertFalse(defects, "odkazy dovnitř fáze cizího skillu:\n  " + "\n  ".join(defects))

    def test_usage_line_has_uniform_form(self):
        """Kde se spotřeba agentů vypisuje, musí mít všude týž tvar.

        `~/.claude/RULES.md`, *Model a effort podle úkolu*, žádá „kolik jich
        bylo, na jakém modelu a effortu“ jako jednu trojici. Pravidlo vzniklo
        14. 9. 2026 a zapsalo se nejdřív do dvou skillů, které byly po ruce –
        navíc každý jinak: jeden uváděl model a effort, druhý ne. Je to
        učebnicový případ pravidla *Rozsah pravidla se nešíří sám*.

        **Kdo ten řádek má mít, se schválně netestuje.** Panel se od jednoho
        agenta strojově nepozná – zkoušené heuristiky (slovo „panel“, „paralelně“
        poblíž „agenta“) hlásily `/transcript` s jedním subagentem a míjely
        `/audit`, který panel má. Falešný poplach je u kontroly horší směr
        selhání než mezera, takže se měří jen to, co změřit jde: tvar.
        """
        defects = []
        for skill in SKILLS:
            for row in body(skill).splitlines():
                if "**Spotřeba:**" not in row:
                    continue
                if "na jakém modelu a effortu" not in row:
                    defects.append(f"{skill.parent.name}: chybí model a effort")
                if "agentů:" not in row:
                    defects.append(f"{skill.parent.name}: nezačíná počtem agentů")
        self.assertFalse(defects, "řádek spotřeby se rozešel v tvaru:\n  " + "\n  ".join(defects))

    def test_listed_mcp_tools_exist(self):
        """Ruční výčet MCP nástrojů v `allowed-tools` musí sedět se skutečností.

        Výčet je tu schválně, ne z lenosti: oficiální plugin `plugin-dev`
        označuje `mcp__…__*` za anti-pattern a žádá vyjmenovat jen potřebné
        nástroje. Cenou za minimální oprávnění je ale křehkost – překlep nebo
        přejmenovaný nástroj se neprojeví při načtení skillu, ale až uprostřed
        běhu, kdy si `/attack` nebo `/audit` sáhne po něčem, co nedostal.

        Jména se čtou z telemetrie pluginu na disku, protože definice nástrojů
        ve zdrojácích chodí přes konstanty (`LIST_CONSOLE_MESSAGES_TOOL_NAME`)
        a hledání `name: '…'` je mine – doloženo pokusem, který nahlásil dva
        falešné nálezy. Zdroje mimo běžící server jsou tři a liší se: `cli-options`
        nezná `fill_form`, telemetrie je nadmnožina včetně historických jmen.
        Bere se telemetrie ze **všech** nainstalovaných verzí, takže test chytí
        překlep a jméno, které nikdy neexistovalo; nástroj odstraněný v nové
        verzi nechytí, dokud stará leží na disku. To je vědomá mez, ne opomenutí:
        falešný poplach z nesouladu verzí by vedl k vypnutí testu.

        Chybí-li plugin na disku, test se přeskočí – nad cizím strojem nebo v CI
        není proti čemu měřit.
        """
        import json as _json
        cache = ROOT / "plugins" / "cache"
        available = set()
        for f in cache.glob("*/chrome-devtools-mcp/*/src/telemetry/tool_call_metrics.json"):
            available |= {t["name"] for t in _json.loads(f.read_text(encoding="utf-8"))}
        if not available:
            self.skipTest("plugin chrome-devtools-mcp není na disku, není proti čemu měřit")

        pattern = re.compile(r"mcp__plugin_chrome-devtools-mcp_chrome-devtools__([a-z_0-9]+)")
        for skill in SKILLS:
            listed = set(pattern.findall(skill.read_text(encoding="utf-8")))
            if not listed:
                continue
            with self.subTest(skill=skill.parent.name):
                absent = sorted(listed - available)
                self.assertFalse(absent,
                    f"{skill.parent.name} jmenuje MCP nástroje, které plugin nenabízí: {absent}")

    def test_allowed_tools_is_filled(self):
        """Skill bez `allowed-tools` běží s celou sadou nástrojů session.

        To znamená i připojené MCP servery – u tří skillů to byl Gmail, Kalendář
        a Drive, tedy dosah na cizí poštu a soubory ze skillu, který přepisuje
        nahrávky. Norma (`skills/SKILLS.md`, *Hlavička*) žádá minimální sadu;
        chybějící pole je nejširší možná, ne „neurčeno“.
        """
        for skill in SKILLS:
            with self.subTest(skill=skill.parent.name):
                self.assertTrue(frontmatter(skill).get("allowed-tools"),
                    f"{skill}: chybí `allowed-tools` – skill běží s celou sadou včetně MCP")

    def test_description_says_when_to_use(self):
        """Popis rozhoduje, jestli se skill vyvolá – musí říct, kdy se použije."""
        for skill in SKILLS:
            with self.subTest(skill=skill.parent.name):
                desc = frontmatter(skill).get("description", "")
                self.assertIn("použije", desc, f"{skill}: `description` neříká, kdy se použije")

    def test_flags_from_body_are_in_argument_hint(self):
        """Režim popsaný v těle, ale chybějící v hintu, uživatel nikdy neuvidí.

        Hledá se ve všech tvarech, kterými skilly režimy dokumentují: tučný
        code span s lomítkem, nadpis `## Režim x`, `### x` i samotný tučný span.
        Dřív se hledal jen ten první, takže u /project, /autocommit a /worktree
        vracel vzor prázdnou množinu a assert nad ní procházel vždycky.
        """
        for skill in SKILLS:
            with self.subTest(skill=skill.parent.name):
                hint = frontmatter(skill).get("argument-hint", "")
                name = skill.parent.name
                skill_body = body(skill)
                documented = set()
                for pattern in (rf"\*\*`/{name} ([a-z-]+)`\*\*",
                             r"^#{2,4} Režim\s+`?([a-z-]+)`?",
                             r"^#{3,4} `([a-z-]+)`",
                             # Odrážka `- **`x`** *(popisek)*` – tvar /project.
                             # Vzor NESMÍ vycházet z hintu: pak by nemohl najít
                             # právě ten režim, který v hintu chybí, a test by
                             # měřil kruhem. Ověřeno mutací.
                             r"^- \*\*`([a-z-]+)`\*\*\s*\*\("):
                    documented |= set(re.findall(pattern, skill_body, re.M))
                missing = sorted(f for f in documented if f not in hint)
                self.assertFalse(missing,
                    f"{skill}: režimy {missing} jsou v těle, ale ne v argument-hint {hint!r}")

    def test_hint_modes_are_described_in_body(self):
        """Opačný směr, a ten slepou skvrnu nemá.

        Předchozí test hledá režimy v těle a porovnává je s hintem – když je
        nenajde, projde nad prázdnou množinou, ať je hint jakýkoliv. Tenhle
        vychází z hintu, který je strojově čitelný vždycky, takže hint
        slibující nezdokumentovaný režim se pozná i u skillu, jehož konvenci
        zápisu vzory výš neznají.

        Norma (SKILLS.md, *Hlavička*): má-li skill režimy dva a víc, musí být
        pojmenované všechny včetně výchozího.
        """
        for skill in SKILLS:
            hint = frontmatter(skill).get("argument-hint", "")
            # Jen první hranatá skupina a jen tokeny oddělené |: `[a-z]+` by
            # rozsekalo české placeholdery (<větev> → "tev") a hlásilo nesmysly.
            first = re.match(r"\s*\[([^\]]+)\]", hint)
            if not first:
                continue
            modes = [r.strip() for r in first.group(1).split("|")]
            modes = [r for r in modes if re.fullmatch(r"[a-z][a-z-]*", r)]
            if len(modes) < 2:
                continue
            skill_body = body(skill)
            name = skill.parent.name
            with self.subTest(skill=name):
                # Režim se smí zmínit i jako `/skill mode`, ne jen samostatně.
                # Uznává se i `/skill mode` a `<mode>`: hint některých skillů
                # nejmenuje režimy, ale typy argumentu (/release [větev|tag|hash]),
                # a ty se v těle píšou v ostrých závorkách.
                absent = [r for r in modes
                         if f"`{r}`" not in skill_body
                         and f"/{name} {r}`" not in skill_body
                         and f"<{r}" not in skill_body]
                self.assertFalse(absent,
                    f"{skill}: argument-hint slibuje režimy {absent}, ale tělo je nepopisuje")


def _own_phases(skill) -> set:
    """Čísla fází a kroků, které skill doopravdy má."""
    own = {re.match(r"(?:Fáze|Krok) (\S+)", n).group(1)
               for n in without_code_blocks(skill)
               if n.startswith(("Fáze ", "Krok "))}
    # písmenné podkroky mají vlastní nadpis úrovně ###, např. „6a – Režim“
    own |= {m.group(1) for m in
                (re.match(r"(\d+[a-c]) – ", n) for n in without_code_blocks(skill)) if m}
    return own


def _bad_links(skill, pattern, own: set, foreign: set) -> list:
    """Odkazy na vlastní fázi, která ve skillu není."""
    bad = []
    in_fence = False
    for row in body(skill).splitlines():
        if row.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if in_fence:
            continue                  # šablona pro subagenta není odkaz
        for m in pattern.finditer(row):
            window = row[max(0, m.start() - 60):m.start()]
            if "SKILL.md" in window or any(f"/{j}" in window for j in foreign):
                continue              # odkaz do cizího skillu
            # „krok 8 životního cyklu“ v RULES.md není vlastní fáze, ale krok
            # *Životního cyklu projektu* – ty se číslují nezávisle
            if "RULES.md" in window or "Životní cyklus" in window:
                continue
            if re.match(r"\s*os[ay]\b", row[m.end():m.end() + 8]):
                continue
            for number in re.findall(r"\d+(?:\.\d+)?[a-c]?", m.group(2)):
                if number not in own:
                    bad.append(f"{m.group(1)} {number}")
    return bad


#: Odkazy se píšou domovskou cestou (`~/.claude/RULES.md`), ale míří na dvě různá
#: místa: do **tohohle repozitáře**, nebo do privátní knowledge base mimo něj.
LINK_PATTERN = r"`(~/(?:\.claude|Dev)/[^`\s]+\.(?:md|sh|json|py))`"

#: Kotva na sekci: `soubor`, *Sekce*. Stojí tady, a ne jen u testu, který ji hlídá,
#: protože z ní počítá i ohlašovací test – jinak by hlásil menší rozsah přeskočené
#: kontroly, než jaký doopravdy je.
ANCHOR_PATTERN = (r"`(~/(?:\.claude|Dev)/[^`\s]+\.md)`,\s*(?:kapitola\s+|sekce\s+)?"
              r"\*([^*\n]{3,80})\*")
KNOWLEDGE_BASE = Path.home() / "Dev" / "context"


def link_target(ref: str):
    """Soubor, na který odkaz míří, nebo None, když se to tady nedá ověřit.

    `~/.claude/…` se resolvuje proti **kořeni repozitáře**, ne proti `$HOME`.
    Na autorově stroji je to totéž, jinde ne – a testovat se má soubor, který
    je právě v pracovním stromu, ne kopie náhodou nainstalovaná v domovském
    adresáři. Původní verze resolvovala přes `$HOME` a v CI i po cizím klonu
    hlásila všech 27 souborů jako plných rozbitých odkazů.

    `~/Dev/…` je knowledge base mimo repozitář. Kde není, není co ověřovat –
    kolik odkazů tím zůstalo nezkontrolovaných, hlásí vlastní test.
    """
    if ref.startswith("~/.claude/"):
        return ROOT / ref[len("~/.claude/"):]
    if not KNOWLEDGE_BASE.exists():
        return None
    return Path(ref.replace("~", str(Path.home()), 1))


class SkillLinks(unittest.TestCase):
    # Kontroluje se i to, co skilly samy odkazují – RULES.md a CLAUDE.md nesou
    # nejvíc odkazů ze všech a netestovaly se vůbec. Projektový .claude/CLAUDE.md
    # nese kontrakt příkazů a odkazy na sekce v jiném repozitáři, takže patří sem taky.
    # `SKILLS.md` nese po zavedení normy nejvíc odkazů na sekce ze všech souborů
    # a byl jediný mimo kontrolu – uříznutá kotva v něm prošla všemi testy.
    REFERRING = SKILLS + [ROOT / "RULES.md", ROOT / "CLAUDE.md", ROOT / "README.md",
                           ROOT / ".claude/CLAUDE.md",
                           ROOT / "skills/SKILLS.md", ROOT / "skills/PREFLIGHT.md"]

    def test_file_links_exist(self):
        """Odkaz na neexistující soubor pošle Clauda hledat něco, co tam není."""
        for file in self.REFERRING:
            with self.subTest(file=file.name if file.parent == ROOT else file.parent.name):
                broken = []
                for ref in set(re.findall(LINK_PATTERN, body(file))):
                    target = link_target(ref)
                    if target is not None and not target.exists():
                        broken.append(ref)
                self.assertFalse(sorted(broken), f"{file}: neexistující odkazy: {sorted(broken)}")

    def test_knowledge_base_links_are_verifiable(self):
        """Kolik odkazů ven z repozitáře zůstalo nezkontrolovaných, se řekne nahlas.

        Bez tohohle testu by se přeskočení tvářilo jako pokrytí: kontrola by mlčela
        stejně, ať knowledge base existuje, nebo ne (`~/.claude/skills/SKILLS.md`,
        *Jak se píše text uvnitř* – žádné tiché ořezání rozsahu).

        **Počítá se obojí – odkazy na soubory i kotvy na sekce.** Kotvy přeskakuje
        `test_section_links_point_to_existing_heading` mlčky (`continue` nad
        neexistujícím cílem), takže dokud se nezapočítaly sem, hlásilo se menší
        číslo než skutečný rozsah přeskočené kontroly – a to je táž vada, jaké má
        tenhle test bránit.
        """
        external, anchors = set(), set()
        for file in self.REFERRING:
            skill_body = body(file)
            external |= {r for r in re.findall(LINK_PATTERN, skill_body) if not r.startswith("~/.claude/")}
            anchors |= {(c, s) for c, s in re.findall(ANCHOR_PATTERN, skill_body)
                      if not c.startswith("~/.claude/")}
        if not KNOWLEDGE_BASE.exists():
            self.skipTest(f"{KNOWLEDGE_BASE} tu není, takže zůstalo neověřeno "
                          f"{len(external)} odkazů na soubory a {len(anchors)} kotev na sekce")
        absent = sorted(ref for ref in external if not link_target(ref).exists())
        self.assertFalse(absent, f"neexistující odkazy do knowledge base: {absent}")

    def test_section_links_point_to_existing_heading(self):
        """Odkaz ve tvaru `soubor`, *Sekce* musí v tom souboru najít nadpis.

        Tohle je vada, kterou tahle konfigurace reálně dostává: přečíslovat fáze uvnitř
        skillu je jednořádková změna, po které pět odkazů z jiného souboru tiše
        ukazuje jinam. Kontrola existence souboru to nechytí – ten pořád existuje.

        Kotva se hledá jako *podřetězec* nadpisu, aby prošly i tvary typu
        *Fáze 1*, bod 6 nebo *`done.md`*.
        """
        # Kotva se pozná podle tvaru `soubor`, *Sekce* – tedy čárka hned za
        # zpětným apostrofem. Volnější vzor bral i běžné zvýraznění v okolní
        # větě ("`RULES.md`) stojí **před `/release`**") a hlásil samé nesmysly.
        pattern = re.compile(ANCHOR_PATTERN)
        for file in self.REFERRING:
            with self.subTest(file=file.name if file.parent == ROOT else file.parent.name):
                bad = []
                for file_path, section in set(pattern.findall(body(file))):
                    target = link_target(file_path)
                    if target is None or not target.exists():
                        continue          # hlásí předchozí test
                    headings = "\n".join(without_code_blocks(target))
                    anchor = section.strip().strip("`*")
                    if anchor not in headings:
                        bad.append(f"{file_path} -> *{anchor}*")
                self.assertFalse(sorted(bad),
                    f"{file}: odkaz na sekci, která tam není: {sorted(bad)}")

    def test_intra_skill_phase_links_point_to_existing_heading(self):
        """Odkaz „vezmi to do Fáze 7“ uvnitř skillu musí trefit jeho vlastní nadpis.

        Tuhle vadu tahle konfigurace reálně dostává: přečíslovat fáze je jedna dávka náhrad,
        po které tři odkazy z téhož souboru ukazují jinam. Test na sekce ji nechytí –
        ten matchuje jen odkazy s uvedenou cestou k souboru, kdežto vnitroskillový
        odkaz cestu nemá. Doloženo mutačním testem: `Fáze 7` přepsaná na `Fáze 77` prošla.

        **Cizí odkaz se pozná z okna před samotným odkazem**, ne z celého řádku.
        První verze přeskakovala řádek, kdykoliv se na něm kdekoliv objevilo jméno
        jiného skillu – a protože se skilly zmiňují průběžně, vypadlo z kontroly
        dvanáct odkazů v pěti nejrozsáhlejších skillech. Doloženo mutačním testem: `Fáze 4`
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
        pattern = re.compile(r"(Fáz[eií]|[Kk]roc?[íkyů]?\w*)\s+"
                          r"((?:\d+(?:\.\d+)?[a-c]?)(?:\s*(?:,|a|–|až)\s*\d+(?:\.\d+)?[a-c]?)*)")
        names = {s.parent.name for s in SKILLS}
        for skill in SKILLS:
            with self.subTest(skill=skill.parent.name):
                own = _own_phases(skill)
                if not own:
                    continue          # skill fáze ani kroky nepoužívá
                bad = _bad_links(skill, pattern, own,
                                        names - {skill.parent.name})
                self.assertFalse(sorted(set(bad)),
                    f"{skill}: odkaz na vlastní fázi, která tam není: "
                    f"{sorted(set(bad))} (má {sorted(own)})")

    def test_links_to_cycle_steps_not_their_internals(self):
        """`/code-review` je vnitřek `/review`; poslat tam uživatele ho připraví o panel.

        Vlastní vyvolání je v pořádku – tam ho skill volá jako nástroj a musí u něj
        uvést úroveň (`low`/`high`/`ultra`), protože bez ní se použije naposledy
        zadaná. Chyba je poslat *uživatele*, aby si `/code-review` pustil místo
        `/review`: dostal by jednoho specialistu z panelu bez ověření nálezů.
        """
        allowed = ("vyvolej", "volá", "uvnitř", "vestavěn", "Korektnost", "Bezpečnost",
                    "/code-review low", "/code-review high", "/code-review ultra")
        for skill in SKILLS:
            with self.subTest(skill=skill.parent.name):
                for line in body(skill).splitlines():
                    if "/code-review" not in line and "/security-review" not in line:
                        continue
                    if any(w in line for w in allowed):
                        continue
                    self.fail(f"{skill}: odkaz na vnitřek `/review` mimo kontext volání:\n  {line.strip()}")


class CanonicalAutocommitForm(unittest.TestCase):
    """Přepínač autocommitu se pozná jen podle nadpisu, takže na jeho tvaru stojí funkce.

    `/autocommit` hledá nadpis znějící přesně `## Autocommit`; zanořený nebo
    o úroveň nižší nenajde a projekt pak hlásí jako vypnutý, přestože zapnutý je.
    Hlídají se obě strany mechanismu, ale jen v tomhle repozitáři – projekty
    venku žádná kontrola nečte, o ty se stará `/project` v režimu `adopt`.
    """

    def test_project_claude_md_has_switch_and_import(self):
        """Nadpis bez importu je přepínač, který nic nespíná.

        Pravidla autocommitu žijí ve skillu a do projektu se dostanou jedině
        tím importem. Sekce bez něj tedy vypadá zapnutě, ale Claude v takovém
        projektu nemá podle čeho commitovat – a pozná se to až tím, že se
        nic neděje.
        """
        project_md = (ROOT / ".claude/CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("\n## Autocommit\n", project_md,
            "projektový CLAUDE.md nemá přepínač na kanonickém místě")
        self.assertIn("@~/.claude/skills/autocommit/autocommit.md", project_md,
            "sekce Autocommit neimportuje pravidla ze skillu")
        self.assertNotIn("## Automatické akce", project_md,
            "zastřešující sekce nad jediným podnadpisem se vrátila")

    def test_global_claude_md_does_not_define_autocommit(self):
        """Druhá strana mechanismu: definice se do globálního souboru nesmí vrátit.

        Dokud tam sekce *Autocommit v projektech* stála, rozbalovala se do každé
        session v každém projektu – tedy i tam, kde je autocommit vypnutý.
        Pravidla dnes drží `skills/autocommit/autocommit.md` a importuje si je
        projekt, který je zapnul. Kopie v globálním souboru by ten import
        obcházela a platila všude.
        """
        global_md = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertNotIn("## Autocommit v projektech", global_md,
            "definice autocommitu se vrátila do globálního CLAUDE.md")


class CoreParts(unittest.TestCase):
    """Ne že skill má správný tvar, ale že v něm je to, co nese jeho funkci.

    Dosavadní testy hlídají hlavičky, odkazy a nadpisy – tedy tvar. Z `/review` šlo
    smazat celou fázi ověřování nálezů, tu, o které skill sám píše, že na ní stojí
    jeho použitelnost, a průběžná kontrola zůstala zelená. Kontrola, která nemůže spadnout
    na věcné vadě, je horší než chybějící kontrola: uspokojuje pravidlo *Ověřitelná
    kontrola místo dojmu*, aniž cokoliv doloží.

    Pořád je to jen tvar – text se nespouští a nic tu neověřuje, že instrukce
    fungují. Je to ale tvar toho, co funkci nese, a to je rozdíl, na kterém záleží.
    """

    def test_review_has_finding_verification(self):
        """Panel bez ověřovatele je generátor pravděpodobně znějících nálezů.

        Skill to o sobě píše sám: „bez třetí vrstvy je panel k ničemu“. Kdyby ta
        fáze vypadla, výstup by se navenek nezměnil – jen by přestal být pravdivý.

        **Měří se dvě věci zvlášť a to rozdělení je nosné.** Fáze musí stát
        ve `SKILL.md`, protože ta nese průběh skillu; text zadání pro agenta smí
        žít i ve vedlejším souboru, kam ho posílá `SKILLS.md`, *Délka a progresivní
        odhalení*. Sloučit obojí do jednoho hledání nad všemi soubory skillu nejde:
        řetězce z fáze se vyskytují i v zadání, takže smazání celé `Fáze 3` ze
        `SKILL.md` by prošlo. Doloženo mutačně 15. 9. 2026 – právě tahle díra
        vznikla při přesunu zadání do `agents.md` a test ji nechytil.
        """
        skill = body(ROOT / "skills/review/SKILL.md")
        for fragment in ("Fáze 3 – Ověření nálezů", "refuted"):
            self.assertIn(fragment, skill, f"/review přišel o fázi ověřování: chybí {fragment!r}")

        auxiliary = "\n".join(body(p) for p in sorted((ROOT / "skills/review").glob("*.md")))
        self.assertIn("Tenhle nález se snaž VYVRÁTIT", auxiliary,
                      "/review přišel o zadání pro ověřovatele")

    def test_cleanup_looks_for_unresolved_topics(self):
        """Skill sám tvrdí, že tohle je nejčastější ztráta v dlouhé konverzaci.

        Je to druhá ze čtyř záruk v *Co skill dělá*, a jako jediná z nich nestojí
        na zápisu do souborů – kdyby fáze vypadla, úklid by navenek proběhl stejně
        a chyběl by jen dotaz, který nikdo nepostrádá, protože o něm neví.

        **Hledá se uvnitř té fáze, ne kdekoliv v souboru.** První verze ověřovala
        `AskUserQuestion` nad celým tělem skillu, kde se ten řetězec vyskytuje
        pětkrát – šlo tedy smazat celou sekci *Jak to probrat* a testy zůstaly
        zelené. Způsob dotazování je přitom to podstatné: kdyby se položky jen
        vypsaly do závěru, uživatel session zavře a zmizí s ní.

        Od 26. 9. 2026 jsou tři interaktivní fronty sloučené do jedné, protože
        kritérium rozhodování bylo u všech totéž a smyčky nad velkým kontextem
        byly nejdražší část skillu. Nevypořádaná témata v ní ale musí zůstat
        **jmenovaným druhem položky** – sloučení je úspora na průchodech, ne
        záminka ztratit kategorii, kterou nikdo jiný nehledá.
        """
        text = body(ROOT / "skills/cleanup/SKILL.md")
        heading = "## Fáze 5 – Fronta rozhodnutí"
        self.assertIn(heading, text, "/cleanup přišel o fázi, ve které se fronta probírá")
        phase = text[text.index(heading):]
        phase = phase[:phase.index("\n## ")]
        for fragment in ("AskUserQuestion", "Bezpředmětné", "nevypořádan"):
            self.assertIn(fragment, phase,
                          f"/cleanup, Fáze 5 přišla o {fragment!r} – zbyl jen nadpis")

        # Síto – ověření kandidáta proti zbytku transcriptu a práh důležitosti –
        # se od 26. 9. 2026 dělá zase v hlavní session, protože vytěžovací agent
        # zanikl (delegace stála víc, než ušetřila; rozbor v decisions.md).
        # Bez síta by se do fronty dostali hrubí kandidáti a uživatel by
        # rozhodoval o něčem, co se mezitím vyřešilo jinudy.
        for fragment in ("Jak ověřit, že to opravdu není vypořádané", "Práh důležitosti"):
            self.assertIn(fragment, text,
                          f"/cleanup přišel o {fragment!r}")

    def test_evaluate_decides_about_every_finding(self):
        """Krok, který sebere čísla a nerozhodne o nich, je evidence bez čtenáře.

        Je to celý důvod, proč `/evaluate` vznikl: sledovací okno v `/release`
        končí větou „N nových chyb“ a tím to končí – číslo se zapíše a nikdo
        s ním nemá povinnost nic udělat. Kdyby tahle fáze vypadla, běh by navenek
        vypadal stejně (podklad se zapíše, souhrn se vypíše) a druhá smyčka by se
        tiše přestala zavírat.

        **Hledá se uvnitř té fáze, ne kdekoliv v souboru.** Odkaz na `FINDINGS.md`
        a rozdělení na vadu a novou práci stojí i ve *Fázi 3*, takže hledání nad
        celým tělem by propustilo smazání celé *Fáze 5*.
        """
        text = body(ROOT / "skills/evaluate/SKILL.md")
        heading = "## Fáze 5 – Rozhodnutí u každého poznatku"
        self.assertIn(heading, text, "/evaluate přišel o fázi rozhodování o poznatcích")
        phase = text[text.index(heading):]
        phase = phase[:phase.index("\n## ")]
        for fragment in ("FINDINGS.md", "backlog.md", "vědomě neděláme", "todo.md"):
            self.assertIn(fragment, phase,
                          f"/evaluate, Fáze 5 přišla o {fragment!r} – zbyl jen nadpis")

    def test_evaluate_grades_its_sources(self):
        """Žebříček zdrojů je to, čím se poznatek odlišuje od dojmu.

        Bez pořadí by skill bral mail stejně vážně jako dotaz do databáze, a
        podklad by vypadal doloženě, i když stojí na tom, co kdo napsal. Hlídá se
        proto, že žebříček má oba krajní stupně a že u každého poznatku stojí,
        čím se doloží.
        """
        text = body(ROOT / "skills/evaluate/SKILL.md")
        for fragment in ("Analytika", "Databáze aplikace", "Vlastní pozorování",
                         "Čím se doloží", "kolik si člověk musí domyslet"):
            self.assertIn(fragment, text, f"/evaluate přišel o {fragment!r} ze žebříčku zdrojů")

    def test_claude_md_imports_are_not_in_backticks(self):
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
        pattern = re.compile(r"`[^`]*@~?[/\w.-]+\.md[^`]*`")
        for file in (ROOT / "CLAUDE.md", ROOT / ".claude/CLAUDE.md"):
            if not file.exists():
                continue
            for number, row in enumerate(file.read_text().splitlines(), 1):
                self.assertFalse(
                    pattern.search(row),
                    f"{file.name}:{number} má @import uvnitř apostrofů, "
                    f"takže se tiše nenačte: {row.strip()[:90]}")

    def test_ptydepe_reads_only_tracked_files(self):
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
        heading = "## Fáze 4 – Inventura a vyloučení"
        self.assertIn(heading, text, "/ptydepe přišel o fázi inventury a vyloučení")
        phase = text[text.index(heading):]
        phase = phase[:phase.index("\n## ")]
        self.assertIn("git ls-files", phase,
                      "/ptydepe, Fáze 4 už nepředepisuje git ls-files")
        for forbidden in ("rglob", "find"):
            self.assertIn(forbidden, phase,
                          f"/ptydepe, Fáze 4 přestala jmenovat {forbidden!r} jako zakázaný průchod")

    def test_agent_prompts_have_required_fields(self):
        """Nález bez `basis` a `severity` nejde ani ověřit, ani zařadit.

        `severity` rozhoduje, jestli nález půjde na ověření; `basis` je to, o co se
        opírá. Bez nich je výstup panelu souvislý text, ne data.

        Hledá se v celém adresáři skillu, ne jen v `SKILL.md`: norma velí vytáhnout
        dlouhá zadání pro agenty do vedlejšího souboru, takže kontrola vázaná na
        tělo by po takovém přesunu hlásila ztrátu pole, které se jen přestěhovalo.
        """
        def all_text(name):
            return "\n".join(body(f) for f in sorted((ROOT / "skills" / name).glob("*.md")))

        for name in ("review", "attack"):
            with self.subTest(skill=name):
                self.assertIn('"severity"', all_text(name), f"/{name}: zadání agentů nemá pole severity")
        self.assertIn('"basis"', all_text("review"),
                      "/review: zadání specialistů nemá pole basis")

    def test_date_is_produced_by_command(self):
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

    def test_runtime_state_is_gitignored(self):
        """Stav, který se mění po každé odpovědi, nesmí skončit v gitu.

        `~/.claude/STRUCTURE.md`, *Běhový stav skillů*. Skill, který
        do `.claude/run/` zapisuje, spoléhá na to, že `/project` ten řádek do
        `.gitignore` doplní – jinak ho v projektu s autocommitem začne commitovat.
        """
        writers = [s.parent.name for s in SKILLS if ".claude/run/" in body(s)]
        if not writers:
            self.skipTest("do .claude/run/ zatím nikdo nezapisuje")
        self.assertIn(".claude/run/", body(ROOT / "skills/project/SKILL.md"),
            f"skilly {writers} zapisují do .claude/run/, ale /project ho nedává do .gitignore")


def without_code_blocks(path: Path):
    """Nadpisy souboru, ale jen skutečné – ne ty uvnitř bloků kódu.

    `WORKTREE.md` má v ukázce rozcestníku `## Odchylky`; brát to jako nadpis dokumentu
    znamená, že by odkaz na neexistující sekci prošel, kdyby se náhodou jmenovala
    stejně jako něco v příkladu.
    """
    in_fence = False
    for row in path.read_text(encoding="utf-8").splitlines():
        if row.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if not in_fence and row.startswith("#"):
            yield row.lstrip("# ").strip()


def _lifecycle_block() -> str:
    """Blok s životním cyklem z `RULES.md`.

    Obě funkce níž ho potřebují a měly to zdvojené. Dvě kopie téhož parsování se
    v hraničním případě rozejdou – a rozešly se: jedna četla kroky bez ohledu na
    tvar šipky, druhá jen z řádků s doslovným „→“, takže po záměně za `->` viděla
    každá jiný počet kroků a nic to nehlásilo.
    """
    text = (ROOT / "RULES.md").read_text(encoding="utf-8")
    i = text.index("### Životní cyklus projektu")
    block = text[text.index("```", i) + 3:]
    return block[:block.index("```")]


def cycle_from_rules() -> set:
    """Kroky životního cyklu se čtou z `RULES.md`, ne z konstanty v testu.

    Ručně opsaný seznam je druhá kopie pravdy: přejmenovaný nebo přidaný krok by
    testem prošel, a naopak zmizelý krok by ho shodil z jiného důvodu, než je ten
    skutečný.
    """
    return set(re.findall(r"/([a-z][a-z-]*)", _lifecycle_block()))


def cycle_with_order() -> dict:
    """Kroky životního cyklu i s vrstvou a pořadím, ne jen jako množina.

    `cycle_from_rules()` vrací set, takže na tvrzení „je to třetí krok osy“
    nestačí. Zdrojem je týž blok v `RULES.md`, jen se z něj čte i pořadí řádků.

    Vrací {skill: (vrstva, index v rámci vrstvy od 1, předchůdce, následník)}.
    **Sousedy i pořadí má jen osa.** Kontrolní kroky nejsou řada, ale vrstva
    v mezerách mezi kroky osy, takže u nich je index i oba sousedi `None` –
    tvrdit o `/oponent`, že je čtvrtý a navazuje na `/release`, je nesmysl,
    který z jednořadého čtení vycházel jako platný údaj.
    """
    layers, layer = [], None
    for row in _lifecycle_block().splitlines():
        # Řádek s kroky se pozná podle nich, ne podle šipky mezi nimi: záměna
        # „→“ za „->“ by jinak celou vrstvu tiše vyhodila. Řádek bez kroků je
        # komentář pod rámečkem a vrstvu nezakládá ani neukončuje.
        steps = re.findall(r"/([a-z][a-z-]*)", row)
        if not steps:
            continue
        # Novou vrstvu zakládá jen řádek, který začíná jejím jménem. Odsazené
        # pokračování začíná krokem, takže patří pod tu předchozí – bez toho
        # `row.split()[0]` na zalomené ose vyrobí vrstvu jménem `/breakdown`,
        # tedy nesmyslná data, se kterými se pak dál počítá.
        head = row.split()[0]
        if not head.startswith("/"):
            layer = head.lower()
            layers.append((layer, []))
        if layer is None:
            raise AssertionError(f"rámeček začíná krokem bez jména vrstvy: {row!r}")
        layers[-1][1].extend(steps)

    out = {}
    for layer, steps in layers:
        for n, step in enumerate(steps, start=1):
            if step in out:
                raise AssertionError(
                    f"krok `/{step}` stojí v rámečku dvakrát; slovník klíčovaný "
                    "jménem skillu by jeden z výskytů tiše přepsal")
            if layer == "osa":
                out[step] = (layer, n,
                             steps[n - 2] if n > 1 else None,
                             steps[n] if n < len(steps) else None)
            else:
                out[step] = (layer, None, None, None)
    return out


def cycle_missing_skills() -> set:
    """Kroky, které rámeček jmenuje, ale skill k nim ještě nevznikl.

    `LIFECYCLE.md` je přiznává v jednom odstavci a slibuje, že zmizí, jakmile
    skilly vzniknou. Bez měření je to jen slib: odstavec přežije svůj důvod
    a bude o hotovém skillu tvrdit, že neexistuje. Čte se proto odtamtud
    a `test_cycle_was_read` ho porovná se skutečností v obou směrech.
    """
    text = (ROOT / "skills" / "LIFECYCLE.md").read_text(encoding="utf-8")
    declared = set()
    for row in text.splitlines():
        m = re.search(r"zatím neexistuj\w* jako skill", row)
        if m:
            declared |= set(re.findall(r"`/([a-z][a-z-]*)`", row[:m.start()]))
    return declared


#: Řetěz tří a víc kroků životního cyklu spojených šipkami. Dva sousedi jsou
#: popis vazby („navazuje na `/specify`, předává `/breakdown`“), tři a víc už
#: je opsané pořadí celého cyklu – tedy druhý zdroj pravdy vedle `RULES.md`.
#: Řetěz kroků: šipka, nebo souvislý text. **První spojka musí být silná** (šipka nebo
#: „pak“) a teprve druhá smí být slabá („a“, čárka) – vzorec „A, pak B a C“.
#: Samotné „a“ mezi dvěma skilly je totiž běžný výčet, ne posloupnost:
#: „vzniknou prací v `/discovery` a `/specify`, a `/cleanup` pak…“ posloupnost
#: netvrdí a hlásit ho jako opsaný cyklus by kontrolu shodilo na falešném nálezu.
#: Mezera se schválně bere bez konce řádku (`[^\S\n]`): se `\s` by vzor spojil
#: tři nesouvisející zmínky ob několik odstavců.
_SPACE = r"[^\S\n]*"
_STEP = r"`?/([a-z][a-z-]*)`?"
_STRONG = rf"{_SPACE}(?:→|->|,?{_SPACE}(?:pak|potom)){_SPACE}"
_WEAK = rf"{_SPACE}(?:→|->|,|{_SPACE}(?:pak|potom|a)){_SPACE}"
_ARROW = re.compile(rf"{_STEP}{_STRONG}{_STEP}{_WEAK}{_STEP}")


def cycle_step_chains(text: str, cycle: set) -> list:
    """Vrátí opsané řetězy kroků životního cyklu nalezené v textu.

    Vada, kterou to chytá, je tichá a drahá: `/project` psal do každého
    vývojářského `CLAUDE.md` cestu `/specify → /oponent → /breakdown →
    /implement`. Když do cyklu přibyl `/discovery`, řetěz zůstal formálně
    správný – jen neúplný –, takže ho žádná kontrola na existenci ani na
    pořadí neodhalila a projekty ho četly jako úplný seznam.
    """
    return ["/" + " → /".join(triple) for triple in _ARROW.findall(text)
            if all(step in cycle for step in triple)]


class CommandContract(unittest.TestCase):
    """Formát kontraktu je závazný, protože ho čte skript – a to se neověřovalo.

    `coding.md` říká „jeden řádek na klíč, `- klíč: příkaz`, a za příkazem už nic“.
    Změna formátu (komentář za příkazem, jiné odsazení, hodnota v bloku kódu)
    vypne kontrolu **tiše**: `sed` v `verify.sh` prostě nic nenajde a hook se
    zachová, jako by ten krok projekt neměl.
    """

    CONTRACT = ROOT / ".claude/CLAUDE.md"

    def _section(self) -> str:
        """Sekce ## Kontrakt příkazů z těla bez bloků kódu – stejně jako `md_body`
        a `contract_section` v `verify.sh`."""
        rows, in_fence, inside, out = self.CONTRACT.read_text(encoding="utf-8").splitlines(), False, False, []
        for r in rows:
            if r.lstrip().startswith(("```", "~~~")):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if r.startswith("## Kontrakt příkazů"):
                inside = True
            elif inside and r.startswith("## "):
                break
            if inside:
                out.append(r)
        return "\n".join(out)

    def _value(self, key: str):
        """Týž výraz jako `cmd_for` v verify.sh."""
        m = re.search(rf"^[ \t]*[-*][ \t]*{key}:[ \t]+(.*?)[ \t]*$",
                      self._section(), re.M)
        return m.group(1) if m else None

    def test_contract_is_readable(self):
        """Kdyby se sekce rozešla s formátem, průběžná kontrola by tu tiše neběžela."""
        self.assertTrue(self._section().strip(), "sekci ## Kontrakt příkazů se nepodařilo přečíst")
        for key in ("typecheck", "lint", "test"):
            with self.subTest(key=key):
                self.assertIsNotNone(self._value(key),
                    f"klíč {key} se z kontraktu nepřečetl – změnil se formát?")

    def test_contract_patterns_cover_repo(self):
        """Soubor, na který nesedí žádný vzor, nečte žádná kontrola – a nikdo se to nedozví.

        Přesně tak vypadly čtyři Python skripty /transcript: lint měl glob
        `skills/*/scripts/*.py`, jenže ony leží přímo v adresáři skillu. Mutace
        s nedefinovaným jménem prošla celým kontraktem zeleně. Hook přitom mlčí
        správně – klíč v kontraktu je a příkaz vrací nulu –, takže tuhle třídu
        nemá kdo chytit než test, který obě množiny porovná.

        Kontroluje se jen to, co některý vzor zachytit MÁ: přípony, které se
        v kontraktu vyskytují. Nový jazyk bez řádku v kontraktu je jiný nález.
        """
        import fnmatch
        import subprocess
        tracked = subprocess.run(["git", "ls-files"], cwd=ROOT,
                                   capture_output=True, text=True).stdout.split()
        self.assertTrue(tracked, "git ls-files nic nevrátil – měří se vůbec něco?")

        patterns = []
        for key in ("typecheck", "lint", "test"):
            value = self._value(key)
            if value in (None, "-"):
                continue
            # ./*.sh a *.sh jsou týž vzor: shell si `./` rozbalí, ale fnmatch ne.
            patterns += [t[2:] if t.startswith("./") else t
                      for t in value.split()
                      if "*" in t or t.endswith((".py", ".sh", ".swift"))]

        # Přípony, pro které kontrola existovat MÁ. Odvozovat je jen z kontraktu
        # nestačí: vypadl-li by odtud celý shellcheck, zmizela by s ním i přípona
        # .sh a test by mlčel právě o té kontrole, která se ztratila. Ověřeno
        # mutací – proto stojí seznam tady a rozšiřuje se vědomě.
        WATCHED = {".py", ".sh", ".swift"}
        extensions = {os.path.splitext(v)[1] for v in patterns if os.path.splitext(v)[1]}
        in_repo = {os.path.splitext(c)[1] for c in tracked} & WATCHED
        self.assertFalse(in_repo - extensions,
            "v repozitáři jsou soubory s příponou, kterou kontrakt vůbec neřeší: "
            f"{sorted(in_repo - extensions)}")

        uncovered = [c for c in tracked
                     if os.path.splitext(c)[1] in extensions
                     and not any(fnmatch.fnmatch(c, v) for v in patterns)]
        self.assertFalse(uncovered,
            "tyhle soubory nezachytí žádný vzor z kontraktu, takže je nečte "
            f"žádná kontrola: {uncovered}")

    def test_contract_commands_are_runnable(self):
        """Pomlčka je vědomé rozhodnutí, ale příkaz musí existovat.

        Jinak hook po každé odpovědi hlásí nespustitelný krok – a to je šum, ne nález.
        """
        import shutil
        for key in ("typecheck", "lint", "test"):
            value = self._value(key)
            if value in (None, "-"):
                continue
            # Rozložit na dílčí příkazy: `lint` je dnes `shellcheck ... && ruff ...`
            # a kontrola jen prvního tokenu by chybějící ruff nenahlásila,
            # přestože hook by po každé odpovědi hlásil nespustitelný krok.
            for part in re.split(r"&&|\|\||;|\|", value):
                tokens = part.split()
                if not tokens:
                    continue
                binary = tokens[0]
                with self.subTest(key=key, binary=binary):
                    self.assertTrue(shutil.which(binary),
                        f"kontrakt má {key}: {value}, ale {binary} není na PATH")


def root_readme_defects(text: str) -> list:
    """Vrátí sekce kořenového README, které mají víc než jeden odstavec.

    Norma je `~/.claude/STRUCTURE.md`, *`README.md`*: každá součást
    představená vlastním nadpisem dostane právě jeden odstavec. Mez je
    mechanická, takže ji nemá hledat model čtením – a dřív ji neměřil nikdo,
    takže pět sekcí nabralo dva až čtyři odstavce s příběhem vzniku,
    obhajobou návrhu a výčtem vnitřních kroků, než si toho někdo všiml.

    Obrázek a ukázka výstupu jsou jediná výjimka normy, takže se nepočítají.
    Čistá funkce nad textem kvůli mutacím, stejně jako `readme_defects()`.
    """
    defects, heading, paragraphs, open_block, in_code = [], None, 0, False, False
    for row in text.splitlines() + ["## konec"]:
        if not in_code and row.startswith("#"):
            if heading and paragraphs > 1:
                defects.append(f"{heading}: odstavců je {paragraphs}, norma žádá jeden")
            heading = row.strip() if row.startswith("### ") else None
            paragraphs, open_block = 0, False
            continue
        if row.lstrip().startswith("```"):
            in_code, open_block = not in_code, False
            continue
        if in_code or heading is None:
            continue
        if not row.strip():
            open_block = False
        elif not open_block:
            open_block = True
            if not row.lstrip().startswith("!["):
                paragraphs += 1
    return defects


class Structure(unittest.TestCase):
    CYCLE = cycle_from_rules()

    def test_cycle_was_read(self):
        """Kdyby se blok v RULES.md přeformátoval, testy životního cyklu by tiše zmlkly."""
        self.assertGreaterEqual(len(self.CYCLE), 8,
            f"z RULES.md se přečetlo jen {len(self.CYCLE)} kroků životního cyklu: {sorted(self.CYCLE)}")
        # Obě funkce čtou týž blok. Rozejdou-li se, jedna z nich přestala vidět
        # celý cyklus – a volný práh výš to sám neodhalí, protože výpadek dvou
        # kroků z cyklu nechá pořád dost na to, aby práh nesplnil.
        self.assertEqual(self.CYCLE, set(cycle_with_order()),
            "cyklus_z_rules() a cyklus_s_poradim() čtou z RULES.md jinou množinu kroků")
        # Krok bez skillu se nezakazuje, ale musí být přiznaný: `LIFECYCLE.md`
        # ho jmenuje a slibuje, že odstavec zmizí, jakmile skill vznikne.
        # Porovnává se v obou směrech – nepřiznaný chybějící krok je slib bez
        # krytí, přiznaný existující je naopak text, který přežil svůj důvod.
        absent = self.CYCLE - {s.parent.name for s in SKILLS}
        self.assertEqual(absent, cycle_missing_skills(),
            "kroky bez skillu nesedí s tím, co přiznává LIFECYCLE.md; "
            f"bez skillu: {sorted(absent)}, přiznané: {sorted(cycle_missing_skills())}")


    def test_lifecycle_describes_same_steps_as_rules(self):
        """Rozhraní kroků se odstěhovalo z `RULES.md` do `skills/LIFECYCLE.md`.

        Rámeček s pořadím zůstal v `RULES.md` a je zdrojem pravdy; výklad kroků
        stojí v `LIFECYCLE.md`. Jsou to dva soubory o téže věci, takže se rozejdou
        přesně tím způsobem, který nikdo nezpozoruje: přibude krok do rámečku a
        nikdo mu nedopíše, co dělá – nebo naopak zmizí ze seznamu a rámeček ho
        dál slibuje. Ani jedno není z jednoho souboru vidět.
        """
        lifecycle = ROOT / "skills" / "LIFECYCLE.md"
        self.assertTrue(lifecycle.exists(), "chybí skills/LIFECYCLE.md")
        text = lifecycle.read_text(encoding="utf-8")
        # Krok je vyložený tehdy, když ho jmenuje odrážka: `- **`/project`**`.
        # Číslovaná řada to být nemůže – cyklus má dvě vrstvy a kontrolní kroky
        # v žádném pořadí nestojí.
        explained = set(re.findall(r"^- \*\*`/([a-z][a-z-]*)`\*\*", text, re.M))
        self.assertEqual(explained, self.CYCLE,
            "LIFECYCLE.md a rámeček v RULES.md jmenují jiné kroky; "
            f"jen v LIFECYCLE: {sorted(explained - self.CYCLE)}, "
            f"jen v RULES: {sorted(self.CYCLE - explained)}")

    def test_unimported_files_are_not_imported(self):
        """`STRUCTURE.md` a `LIFECYCLE.md` se schválně neimportují.

        Držet je mimo paušální kontext je celý smysl toho, že jsou zvlášť: dohromady
        je to přes 40 kB, které by jinak šly do každé session v každém projektu.
        Vrátit `@` před cestu je jednoznaková změna, kterou nic jiného nehlásí –
        a projeví se jen tím, že je kontext o něco plnější, čehož si nikdo nevšimne.
        """
        text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        for file_path in ("~/.claude/STRUCTURE.md", "~/.claude/skills/LIFECYCLE.md"):
            with self.subTest(file_path=file_path):
                self.assertNotIn(f"@{file_path}", text,
                    f"{file_path} se importuje, přestože má být jen odkaz")
                self.assertIn(f"`{file_path}`", text,
                    f"{file_path} není v CLAUDE.md ani zmíněný jako odkaz")

    def test_preflight_requires_loading_unimported_files(self):
        """Odkaz bez mechanismu je přání.

        `STRUCTURE.md` a `LIFECYCLE.md` se přestaly importovat výměnou za to, že
        si je skill načte, když je potřebuje. Jediné místo, kde se ta povinnost
        dá vynutit napříč skilly, je společná příprava – zmizí-li odsud, zbude
        z celé úspory jen chybějící znalost.
        """
        text = (ROOT / "skills" / "PREFLIGHT.md").read_text(encoding="utf-8")
        for file_path in ("~/.claude/STRUCTURE.md", "~/.claude/skills/LIFECYCLE.md"):
            with self.subTest(file_path=file_path):
                self.assertIn(file_path, text,
                    f"příprava neříká, kdy si načíst {file_path}")

    def test_skill_does_not_copy_cycle_step_chain(self):
        """Pořadí kroků cyklu se odkazuje, neopisuje.

        Opsaný řetěz se při přidání kroku rozejde se zdrojem a vypadá přitom
        pořád platně – v `SKILL.md` i v každém `CLAUDE.md`, do kterého ho ten
        skill jako šablonu zapsal. Zdrojem pravdy je blok v `RULES.md`.
        """
        for skill in SKILLS:
            with self.subTest(skill=skill.parent.name):
                findings = cycle_step_chains(body(skill), self.CYCLE)
                self.assertFalse(findings,
                    f"{skill.parent.name} opisuje pořadí kroků cyklu: {findings}; "
                    "odkaž se na *Životní cyklus projektu* v RULES.md")

    ORDINALS = {"první": 1, "druhý": 2, "třetí": 3, "čtvrtý": 4,
                "pátý": 5, "šestý": 6, "sedmý": 7}

    def _compare_sentence(self, name, sentence_groups, cycle) -> list:
        """Jedna věta o pořadí proti RULES.md."""
        ordinal, phase, predecessor, successor = sentence_groups
        exp_phase, exp_n, exp_pred, exp_succ = cycle[name]
        errors = []

        # `osy` ve větě proti `osa` v rámečku: skloňuje se, protože to je česká
        # věta („je to třetí krok osy“), ne jméno klíče.
        if {"osy": "osa", "kontroly": "kontroly"}.get(phase) != exp_phase:
            errors.append(f"{name}: tvrdí vrstvu `{phase}`, RULES.md má `{exp_phase}`")
        if exp_n is None:
            # Kontrolní krok není bod v řadě, takže nemá co tvrdit o pořadí ani
            # o sousedech – stojí v mezerách a v několika naráz.
            errors.append(f"{name}: je kontrolní krok, ale tvrdí pořadí v cyklu "
                         "– nahraď to větou o tom, ve kterých mezerách stojí")
            return errors
        if ordinal == "poslední":
            # „Poslední“ se ověřuje jen proti počtu kroků ve fázi. Následník
            # se posuzuje níž stejně jako u číslovaných kroků: poslední krok
            # fáze ho legitimně má – `/cleanup` uzavírá uzavírání a přitom
            # správně předává na `/attack` z nasazení.
            steps_in_phase = len([k for k, v in cycle.items() if v[0] == exp_phase])
            if exp_n != steps_in_phase:
                errors.append(f"{name}: tvrdí, že je poslední ve fázi `{phase}`, "
                             f"ale je {exp_n}. z {steps_in_phase}")
        elif self.ORDINALS.get(ordinal) != exp_n:
            errors.append(f"{name}: tvrdí `{ordinal} krok`, podle RULES.md je {exp_n}.")
        if predecessor and predecessor != exp_pred:
            errors.append(f"{name}: tvrdí, že navazuje na `/{predecessor}`, RULES.md má `/{exp_pred}`")
        if successor and successor != exp_succ:
            errors.append(f"{name}: tvrdí, že předává na `/{successor}`, RULES.md má `/{exp_succ}`")
        return errors

    def _one_step_sentence(self, name, text, cycle, pattern) -> tuple:
        """Věta o pořadí jednoho skillu. Vrací (počet poznaných vět, chyby).

        Osa a kontrolní vrstva se měří jinak, a proto to stojí zvlášť: kontrolní
        krok nemá pořadí ani sousedy, takže se u něj ověřuje opak – že o svém
        místě v cyklu mluví a že to nedělá větou o pořadí.
        """
        names_cycle = bool(re.search(r"V \*Životním cyklu projektu\*", text))
        m = pattern.search(text)
        if cycle[name][0] != "osa":
            defects = [] if names_cycle else [f"{name}: kontrolní krok neříká, kde v cyklu stojí"]
            return 0, defects + (self._compare_sentence(name, m.groups(), cycle) if m else [])
        if m:
            return 1, self._compare_sentence(name, m.groups(), cycle)
        # Skill, který o svém pořadí mluví, ale vzor na tvar té věty nesedne, se
        # dřív tiše přeskočil – a jeho tvrzení pak neověřil nikdo. Přeformulovat
        # větu se smí, ale ne potichu. Kotvou je proto odkaz na cyklus, ne znění
        # věty za ním: vzor psaný podle dnešního znění mlčí přesně nad tím, co se
        # přepisuje – po přestavbě cyklu zůstalo v šesti skillech „krok zakládání“
        # a všech šest se tiše přeskočilo, protože na nový vzor nesedlo.
        if names_cycle and not re.search(r"Je (?:první|poslední) článek", text):
            return 0, [f"{name}: mluví o svém pořadí, ale vzor na tvar té věty nesedne "
                      "– přeformuluj ji, nebo uprav vzor v testu"]
        return 0, []

    def test_step_order_sentence_matches_rules(self):
        """Skill tvrdí, kolikátý je a na koho navazuje – nic to neměřilo.

        Vložení kroku doprostřed životního cyklu posune čísla všem za ním, jenže
        ta čísla stojí běžným textem v `Co skill dělá` každého skillu.
        `test_intra_skill_phase_links_point_to_existing_heading` je schválně
        vynechává (míří mimo vlastní číslování skillu), takže regrese prošla tiše
        a našel ji až audit. Zdrojem pravdy je `RULES.md`.
        """
        cycle = cycle_with_order()
        self.assertEqual(set(cycle), self.CYCLE,
            f"cyklus_s_poradim() vrátil jinou množinu kroků než cyklus_z_rules(): {sorted(cycle)}")

        live = {s.parent.name for s in SKILLS}
        pattern = re.compile(
            r"je to \*{0,2}(\w+) krok (osy|kontroly)\*{0,2}"
            r"(?:[:\s–-]+navazuje na `/([a-z-]+)`)?"
            r"(?:\s+a předává na `/([a-z-]+)`)?")
        errors, matched = [], 0
        for skill in SKILLS:
            name = skill.parent.name
            if name not in cycle:
                continue
            found, defects = self._one_step_sentence(name, body(skill), cycle, pattern)
            matched += found
            errors += defects

        # Druhý tvar téhož tvrzení: `/project` píše „Je první článek Životního
        # cyklu projektu“. Vzor výš ho nepoznal, takže se skill tiše přeskakoval
        # – a právě on nesl vadu, kvůli které tenhle test vznikl (posílal na
        # `/specify`, ačkoli jeho následník je `/discovery`).
        # Jen osa: kontrolní kroky v žádném pořadí nestojí, takže „první“
        # a „poslední“ článek se hledá mezi tím, co řadu tvoří.
        order = [k for k, v in sorted(cycle.items(), key=lambda x: x[1][1] or 0)
                if v[0] == "osa"]
        for skill in SKILLS:
            name = skill.parent.name
            if name not in cycle:
                continue
            m = re.search(r"Je (první|poslední) článek \*Životního cyklu projektu\*", body(skill))
            if not m:
                continue
            matched += 1
            should_be = cycle[name][2] is None if m.group(1) == "první" else cycle[name][3] is None
            if not should_be:
                errors.append(f"{name}: tvrdí, že je {m.group(1)} článek cyklu, "
                             f"ale RULES.md má na tom místě `/{order[0 if m.group(1) == 'první' else -1]}`")

        # Přesný počet, ne práh: při volném prahu propadne skill, jehož větu vzor
        # přestal poznávat, protože ostatní ho vyváží. Zvedne-li se počet skillů,
        # které tu větu nesou, číslo se tu vědomě upraví. Jde do téhož seznamu
        # jako ostatní chyby, aby se konkrétní nález nezakryl souhrnným číslem.
        # Počet se odvozuje, ne fixuje: větu o pořadí nese každý existující krok
        # osy. Že ji kontrolní kroky nést nesmějí, hlídá `_one_step_sentence`;
        # že se kroky osy vymezují vůči sousedům, hlídá
        # `test_what_skill_does_not_names_both_neighbours`.
        expected = len([n for n, v in cycle.items() if v[0] == "osa" and n in live])
        if matched != expected:
            errors.append(f"větu o pořadí kroku nese {matched} skillů, čekalo se {expected} "
                         f"– změnil se její tvar, nebo ji získal či ztratil další skill?")
        self.assertFalse(errors, "věty o pořadí kroku nesedí s RULES.md:\n  " + "\n  ".join(errors))

    def test_cycle_steps_have_does_not_section(self):
        """Bez vymezení vůči sousedům se práce buď zdvojí, nebo neudělá vůbec."""
        absent = [s.parent.name for s in SKILLS
                 if s.parent.name in self.CYCLE and "Co skill nedělá" not in body(s)]
        self.assertFalse(absent, f"skilly životního cyklu bez sekce `Co skill nedělá`: {absent}")

    def test_what_skill_does_not_names_both_neighbours(self):
        """Norma žádá jmenované sousedy, měřila se ale jen existence nadpisu.

        Platí to **jen pro kroky osy**; kontrolní kroky místo sousedů jmenují,
        čí práci nepřebírají.

        Vada, kterou to propustilo: `/project` roky posílal na `/specify`
        a o svém skutečném následníkovi `/discovery` nevěděl, přestože
        `SKILLS.md`, *Povinné sekce a jejich pořadí*, jmenované sousedy
        z obou stran u kroků cyklu vyžaduje.

        **Hledá se jen v úvodních sekcích**, ne v celém těle. Nad celým tělem
        kontrola nic neměří: `/project` jmenuje `/discovery` i v tabulce
        produktových podkladů, takže by prošel, i kdyby se o svém sousedovi
        nezmínil ani slovem – doloženo mutačním testem, která tu vadu vrátila a testem
        prošla. Vymezení patří do `Co skill dělá` a `Co skill nedělá`, tedy do
        textu před první fází.
        """
        cycle = cycle_with_order()
        absent = []
        for skill in SKILLS:
            name = skill.parent.name
            # Jen osa. Kontrolní krok sousedy nemá – `/cleanup` stojí ve všech
            # mezerách a `/review` ve dvou, takže „soused z obou stran“ u nich
            # není definovaný; norma v `SKILLS.md` tu výjimku má a měla ji dřív
            # než tenhle test, který ji vynucoval na všech.
            if cycle.get(name, (None,))[0] != "osa":
                continue
            text = body(skill)
            stop = text.find("\n## Fáze")
            if stop == -1:
                stop = text.find("\n## Krok")
            text = text[:stop] if stop != -1 else text
            _, _, pred, succ = cycle[name]
            for neighbour in (pred, succ):
                if neighbour and f"/{neighbour}" not in text:
                    absent.append(f"{name} nejmenuje souseda /{neighbour}")
        self.assertFalse(absent, "kroky cyklu se nevymezují vůči sousedům:\n  " + "\n  ".join(absent))

    def _skills_in_readme(self) -> set:
        """Skilly jmenované v nadpisech README. Jeden nadpis jich může nést víc –
        `/breakdown` a `/implement` mají společný, protože jeden předává druhému."""
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        out = set()
        for row in readme.splitlines():
            if row.startswith("#"):
                out |= set(re.findall(r"\[`/([a-z-]+)`\]", row))
        return out

    def test_readme_knows_every_skill(self):
        """README je rozcestník; skill, který v něm není, nikdo nenajde.

        Kontroluje se nadpis, ne výskyt řetězce: `skills/foo/` se v README může
        objevit i v ukázce adresářové struktury, a test by pak byl spokojený
        i bez sekce o skillu.
        """
        absent = sorted({s.parent.name for s in SKILLS} - self._skills_in_readme())
        self.assertFalse(absent, f"skilly bez vlastní sekce v README: {absent}")

    def test_readme_does_not_link_vanished_skill(self):
        """Opačný směr: po smazání skillu zůstane v README mrtvá sekce."""
        extra = sorted(self._skills_in_readme() - {s.parent.name for s in SKILLS})
        self.assertFalse(extra, f"README má sekci pro skill, který neexistuje: {extra}")

    def test_readme_sections_hold_one_paragraph(self):
        """Rozcestník, ve kterém se jedna položka rozroste ve výklad, přestane
        být rozcestníkem – čtenář hledající orientaci ho přestane číst."""
        defects = root_readme_defects((ROOT / "README.md").read_text(encoding="utf-8"))
        self.assertFalse(defects, "sekce README nad mez jednoho odstavce:\n  "
            + "\n  ".join(defects))

    def test_second_paragraph_is_reported(self):
        """Mutace: kontrola, která nic nechytá, mlčí stejně jako ta funkční."""
        self.assertTrue(root_readme_defects(
            "### [`x`](x) – popis\n\nPrvní odstavec.\n\nDruhý odstavec.\n"))

    def test_image_and_sample_are_not_a_paragraph(self):
        """Druhý směr – falešný poplach je ta horší polovina: obrázek a ukázku
        výstupu norma povoluje a kontrola, která křičí na správný text, se vypne."""
        self.assertFalse(root_readme_defects(
            "### [`x`](x) – popis\n\nJediný odstavec.\n\n![Náhled](x.png)\n\n"
            "```\nukázka výstupu\n\nse dvěma odstavci\n```\n"))


def _appendix_defects(order: dict, first_phase, conclusion) -> list:
    """Přílohová sekce patří ZA závěrečnou fázi.

    Norma to žádá, ale nikdo to neměřil, takže v `/review` stála
    *Kapitola `## Review`* mezi Fází 7 a Fází 8 a testy mlčely.

    Hlídají se jen sekce, které norma jako přílohy jmenuje. Širší kontrola
    („cokoliv nefázového mezi fázemi“) by hlásila `Časté chyby` u skillu bez
    příloh, kam je norma výslovně staví, a odbočky průběhu typu
    `Když plán neplatí` v `/implement`.
    """
    if first_phase is None or conclusion is None:
        return []
    return [f"pořadí sekcí: přílohová sekce `{n}` stojí mezi fázemi, "
            "patří za závěrečnou fázi"
            for n, i in order.items()
            if n.startswith(("Režim ", "Katalog", "Kapitola")) and first_phase < i < conclusion]


class StandardCompliance(unittest.TestCase):
    """Skilly proti `skills/SKILLS.md`. Jediné místo, kde se norma vynucuje strojem.

    Norma vznikla později než skilly, takže je bylo potřeba na ni převést.
    Převod je vědomý běh `/skill update`, ne vedlejší efekt jiné práce – proto
    seznam `MIGRATION` místo hromady padajících testů. **Kolik skillů ještě čeká,
    se tu schválně nepíše** – zmizelo by to s prvním převedeným a docstring by
    lhal o tom, co sám hlídá; aktuální stav drží `MIGRATION` níž.

    Seznam ale neumlčuje – **musí přesně sedět se skutečností** a test to hlídá
    v obou směrech. Skill, který se opraví a nezmizí ze seznamu, test shodí
    stejně jako skill, který se rozbije. Bez toho by seznam tiše zůstal i po dokončení migrace a přestal by
    cokoliv měřit.
    """

    STANDARD = ROOT / "skills" / "SKILLS.md"
    PREFLIGHT = ROOT / "skills" / "PREFLIGHT.md"

    #: Skilly, které ještě neprošly `/skill update`. Zkracuje se, nikdy nedoplňuje.
    #: Skilly, které ještě neprošly `/skill update`. Zkracuje se, nikdy nedoplňuje.
    #: Prázdný od 15. 9. 2026 – celá sada je na normě. Zůstává schválně:
    #: až norma přituhne znovu, je kam zapsat, co ještě nedorovnalo, a test
    #: pořád hlídá oba směry (skill mimo normu i skill, který ji už splňuje).
    MIGRATION = set()

    #: Odkaz dovnitř fáze jiného skillu. Cizí fáze se přečíslují a odkaz pak
    #: tiše ukazuje jinam – proto to má být v PREFLIGHT.md, ne v odkazu.
    FOREIGN_PHASE = re.compile(
        # `\*{0,2}` schválně: odkaz se běžně píše kurzívou (`/cleanup`, *Fáze 1 – …*)
        # a dřív ho vzor kvůli hvězdičce minul. Právě v té podobě byl v repozitáři
        # skutečný odkaz dovnitř cizí fáze, který kontrola neviděla.
        r"(?:`/[a-z-]+`|skills/\w+/SKILL\.md`),\s*\*{0,2}(?:Fáze|Krok)")
    #
    # Zkoušelo se to rozšířit i na odkaz do **vedlejšího souboru** cizího skillu
    # (`/attack` → `skills/review/agents.md`), ale širší vzor hlásil falešné
    # poplachy na šesti skillech naráz: chytal odkazy na **jména sekcí**, které
    # jsou legitimní a dnes se právě zaváděly jako náprava odkazů na čísla fází.
    #
    # Rozhoduje totiž křehkost, ne cizost: **číslo fáze se přečísluje**, jméno
    # sekce ne. Odkaz na jméno je proto v pořádku, ať míří kamkoliv. Duplicitu
    # sdíleného obsahu řeší jiné pravidlo (*Single source of truth*) a jinými
    # prostředky – sdíleným souborem v `skills/`, jako je `SEVERITY.md`.

    #: Přípony, které v adresáři skillu znamenají spustitelný vnitřek.
    SCRIPTS = ("*.sh", "*.py", "*.swift")

    def has_scripts(self, skill: Path) -> bool:
        """Má skill v adresáři vlastní skripty? Hledá i jednu úroveň hlouběji.

        Norma dovoluje `scripts/`, takže `/compose` má skripty tam a `/transcript`
        rovnou vedle `SKILL.md`; kontrola musí vidět obojí.
        """
        skill_dir = skill.parent
        return any(p.is_file() for pattern in self.SCRIPTS
                   for p in list(skill_dir.glob(pattern)) + list(skill_dir.glob(f"*/{pattern}")))

    def defects(self, skill: Path) -> list:
        text = body(skill)
        out = []
        if "\n## Co skill dělá" not in text:
            out.append("chybí `## Co skill dělá`")
        if "\n## Co skill nedělá" not in text:
            out.append("chybí `## Co skill nedělá`")
        # Příprava je povinná sekce a pozná se podle **čísla**, ne podle názvu:
        # `/oponent` ho má jako „Fáze 0 – Co se oponuje“ a `/project` jako
        # „Krok 0 – Zjisti režim a stav“. Dřív se odkaz na PREFLIGHT.md hledal
        # jen tehdy, když se v textu vyskytlo slovo „Příprava“ – oba tyhle
        # skilly z kontroly tiše vypadávaly i se svým opsanou přípravou.
        has_preflight = re.search(r"\n## (?:Fáze|Krok) 0\b", text)
        if not has_preflight:
            out.append("chybí `## Fáze 0 – Příprava`")
        elif "PREFLIGHT.md" not in text:
            out.append("příprava neodkazuje na `skills/PREFLIGHT.md`")

        row_count = len(text.splitlines())
        if row_count > 500:
            out.append(f"tělo má {row_count} řádků, tvrdá mez je 500")
        if "Zakonči jednou z těchto vět" not in text:
            out.append("chybí závěrečný verdikt")
        if self.FOREIGN_PHASE.search(text):
            out.append("odkazuje dovnitř fáze jiného skillu")
        # Skill s vlastním spustitelným vnitřkem musí přiznat, co je detail a co
        # rozhraní. Bez toho si někdo zvykne na jméno skriptu nebo proměnné jako
        # na kontrakt a příští výměna nástroje se stane rozbitím. Kritérium je
        # schválně jen na skripty: delegaci na cizí skill strojově nepoznám
        # spolehlivě, a kontrola, která hádá, hlásí falešné poplachy.
        if self.has_scripts(skill) and "\n## Jak je to postavené uvnitř" not in text:
            out.append("má vlastní skripty a chybí `## Jak je to postavené uvnitř`")
        out += self.order_defects(skill)
        return out

    def order_defects(self, skill: Path) -> list:
        """Pořadí sekcí podle normy, *Povinné sekce a jejich pořadí*.

        Norma řadí hlavní průběh, za něj přílohové sekce (samostatné režimy,
        katalogy) a `## Časté chyby` úplně naposled. Kontroluje se jen relativní
        pořadí sekcí, které skill opravdu má – nepovinné se nedoplňují.

        Proč zvlášť: bez téhle kontroly tvrdila norma víc, než uměla vynutit.
        Doloženo – pravidlo o přílohových sekcích do ní přibylo 4. 9. 2026 z auditu
        `/consistency`, a týž audit ho našel porušené v `/skill`, protože ho žádná
        kontrola chytit nemohla.
        """
        headings = [n for n in without_code_blocks(skill) if not n.startswith("#")]
        order = {n: i for i, n in enumerate(headings)}

        def position(*prefixes):
            for n, i in order.items():
                if n.startswith(prefixes):
                    return i
            return None

        does, does_not = position("Co skill dělá"), position("Co skill nedělá")
        inside = position("Jak je to postavené uvnitř")
        first_phase = position("Fáze 0", "Krok 0")
        errors = position("Časté chyby")
        # Závěr = **poslední** fáze či krok, ne fáze pojmenovaná „Závěr“. Většina
        # skillů ji má pod vlastním názvem (`Úklid a shrnutí`, `Uzavření`,
        # `Předání`) a norma jméno nepředepisuje – vázat kontrolu na slovo
        # „Závěr“ znamenalo, že přejmenování závěru celou kontrolu pořadí tiše
        # vypnulo. Doloženo mutačním testem: `Fáze 8 – Závěr` → `Fáze 8 – Uzavření`
        # zneškodnilo jedinou vadu, kterou uměla najít.
        conclusion = max((i for n, i in order.items()
                     if n.startswith(("Fáze", "Krok"))), default=None)

        out = []
        for earlier, later, description in (
                (does, does_not, "`Co skill nedělá` musí být za `Co skill dělá`"),
                (does_not, inside, "`Jak je to postavené uvnitř` patří za `Co skill nedělá`"),
                (inside, first_phase, "postup začíná až za `Jak je to postavené uvnitř`"),
                (does_not, first_phase, "postup začíná až za `Co skill nedělá`"),
        ):
            if earlier is not None and later is not None and earlier > later:
                out.append(f"pořadí sekcí: {description}")

        # `Časté chyby` mají v normě dvě legitimní místa podle toho, jestli skill
        # má přílohy: u lineárního těsně před závěrem, u skillu s přílohovými
        # sekcemi úplně naposled. Kontrolovat jen jedno z nich by shodilo polovinu
        # skillů, které normu splňují.
        out += _appendix_defects(order, first_phase, conclusion)

        if errors is not None and conclusion is not None:
            appendices = [n for n, i in order.items()
                       if i > conclusion and not n.startswith("Časté chyby")]
            if appendices and errors != max(order.values()):
                out.append("pořadí sekcí: skill má přílohové sekce, "
                           "takže `Časté chyby` musí stát úplně naposled")
            if not appendices and errors > conclusion:
                out.append("pořadí sekcí: skill nemá přílohy, "
                           "takže `Časté chyby` patří před závěrečnou fázi")
        return out

    def test_standard_and_preflight_exist(self):
        """Bez nich nemá `/skill` co číst a odkazy ze skillů míří nikam."""
        for file in (self.STANDARD, self.PREFLIGHT):
            self.assertTrue(file.exists(), f"chybí {file}")
        self.assertFalse((self.STANDARD.parent / "SKILLS.md" / "SKILL.md").exists(),
            "norma se nesmí tvářit jako skill")

    def test_description_fits_limit(self):
        """Delší popis se nemusí přenést celý – a pak se skill nevyvolá vůbec.

        Bez výjimky pro migraci: limit platí pro všechny a dnes ho nikdo neporušuje.
        """
        for skill in SKILLS:
            with self.subTest(skill=skill.parent.name):
                description = frontmatter(skill).get("description", "")
                self.assertLessEqual(len(description), 1024,
                    f"{skill.parent.name}: description má {len(description)} znaků")

    def test_migration_names_only_existing_skills(self):
        """Zmizelý skill v seznamu by tiše držel výjimku pro nikoho."""
        extra = sorted(self.MIGRATION - {s.parent.name for s in SKILLS})
        self.assertFalse(extra, f"MIGRATION jmenuje neexistující skilly: {extra}")

    def test_skills_match_standard(self):
        """Seznam MIGRATION musí přesně sedět: skill mimo normu nechybí ani nepřebývá."""
        noncompliant = {s.parent.name: self.defects(s) for s in SKILLS if self.defects(s)}

        regressed = sorted(set(noncompliant) - self.MIGRATION)
        self.assertFalse(regressed, "skilly mimo normu, které v MIGRATION nejsou: "
            + "; ".join(f"{n}: {', '.join(noncompliant[n])}" for n in regressed))

        fixed = sorted(self.MIGRATION - set(noncompliant))
        self.assertFalse(fixed,
            f"tyhle skilly už normu splňují – vyškrtni je z MIGRATION: {fixed}")


#: Blok kódu ve skillu, jehož obsah se vypisuje do konverzace. Pozná se podle
#: prvního neprázdného řádku: nadpis, výpis položky `[N/celkem]`, tučný popisek
#: nebo řádek tabulky. Zadání pro subagenta začíná oslovením („Jsi…“, „Prověř…“),
#: příkaz shellu má u fence jazyk – ani jedno sem tedy nespadne.
CONVERSATION_TEMPLATE = re.compile(
    r"^(?:## |\*\*\[N/celkem\]|- \*\*[^*]+:\*\*|\*\*[^*]+:\*\*|\*\*[A-ZČŘŽŠ][^*]*\*\*$|\| )")

#: Věta, kterou musí šablona do konverzace nést pod sebou.
MARKDOWN_INSTRUCTION = "ne jako blok kódu"


def templates(text: str):
    """Vrátí (číslo řádku, první řádek, má pokyn) pro každý blok kódu bez jazyka.

    Yielduje jen bloky, které vyhoví `CONVERSATION_TEMPLATE`.
    """
    lines = text.split("\n")
    in_block = False
    block: list = []
    block_start = 0
    for i, l in enumerate(lines):
        s = l.strip()
        if s.startswith("```"):
            if not in_block:
                in_block, block, block_start, lang = True, [], i + 1, s[3:].strip()
            else:
                in_block = False
                first = next((b.strip() for b in block if b.strip()), "")
                if not lang and CONVERSATION_TEMPLATE.match(first):
                    surroundings = "\n".join(lines[i + 1:i + 3])
                    yield block_start, first, MARKDOWN_INSTRUCTION in surroundings
        elif in_block:
            block.append(l)


class TemplatesPrintMarkdown(unittest.TestCase):
    """Šablona výstupu v bloku kódu se reprodukuje jako blok kódu.

    Trojice zpětných apostrofů kolem šablony v `SKILL.md` má oddělit šablonu
    od okolního textu, ale model ji čte jako pokyn k formátu: vypíše
    předformátovaný text, zalomí si ho kolem šedesáti znaků a hodnoty zarovná
    mezerami pod sebe. V širokém okně z toho je úzká nudle uprostřed obrazovky.
    Proto `skills/SKILLS.md`, *Jak se píše text uvnitř*, žádá u každé takové
    šablony výslovný pokyn – a proto ho hlídá test.

    Bez něj to zelený běh nechytí: 7. 9. 2026 se šablony přepisovaly dvakrát
    po sobě a pokaždé zůstalo osm respektive sedm míst neopravených, přičemž
    testy prošly. Horší než chybějící pokyn je přitom to, že podle
    `~/.claude/RULES.md`, *Přednost pravidel*, stojí výstupní šablona skillu
    **nad** `RULES.md` – šablona bez pokynu tedy nové pravidlo přebíjí, ne
    jen neopakuje.
    """

    #: Bloky, které kritériu vyhoví, ale do konverzace nejdou – jejich obsah
    #: se **zapisuje do souboru** (sekce do `CLAUDE.md`, blok metadat projektu,
    #: tabulka do `SKILL.md`). Markdownem už jsou; pokyn by tu lhal o tom,
    #: kam text míří. Seznam musí přesně sedět: zmizelá výjimka shodí testy
    #: stejně jako nová šablona bez pokynu.
    WRITTEN_TO_FILE = {
        ("autocommit/SKILL.md", "## Autocommit"),
        ("cleanup/SKILL.md", "| # | řádek | co uživatel napsal (zkráceně) | stav | kde |"),
        ("consistency/SKILL.md", "## Consistency"),
        ("project/SKILL.md", "- **Struktura:** docs/"),
        ("project/SKILL.md", "## Struktura a dokumentace"),
        ("project/SKILL.md", "## Paměť"),
        ("project/checklists.md", "## Doménové standardy"),
        ("review/SKILL.md", "## Review"),
        ("skill/SKILL.md", "| Krok | Kdo | Proč zrovna on |"),
    }

    def found_blocks(self):
        """Vrátí (bez pokynu, výjimky nalezené ve skillech)."""
        absent, seen = [], set()
        for p in sorted((ROOT / "skills").glob("*/*.md")):
            if p.name == "README.md":
                continue
            file_key = f"{p.parent.name}/{p.name}"
            for row, first, has_instruction in templates(p.read_text(encoding="utf-8")):
                key = (file_key, first)
                if key in self.WRITTEN_TO_FILE:
                    seen.add(key)
                elif not has_instruction:
                    absent.append(f"{file_key}:{row} – {first[:60]}")
        return absent, seen

    def test_templates_carry_instruction(self):
        absent, _ = self.found_blocks()
        self.assertFalse(absent, "šablony do konverzace bez pokynu na Markdown:\n"
                         + "\n".join(absent))

    def test_exceptions_match_reality(self):
        """Výjimka pro blok, který zmizel nebo se přejmenoval, kryje nikoho."""
        _, seen = self.found_blocks()
        vanished = sorted(self.WRITTEN_TO_FILE - seen)
        self.assertFalse(vanished, f"výjimky, které nic nekryjí – vyškrtni je: {vanished}")

    def test_check_catches_template_without_instruction(self):
        """Mutace: šablona s pokynem, kterému se pokyn odebere, musí spadnout."""
        pattern = "```\n## Hotovo\n\n- **Rozsah:** …\n```\n\n" + MARKDOWN_INSTRUCTION + "\n"
        self.assertTrue(all(has_instruction for _, _, has_instruction in templates(pattern)),
                        "kontrola nevidí pokyn ani tam, kde stojí")
        without = pattern.replace(MARKDOWN_INSTRUCTION, "a je to")
        self.assertTrue(any(not has_instruction for _, _, has_instruction in templates(without)),
                        "kontrola neohlásí šablonu, které pokyn chybí")

    def test_check_ignores_subagent_prompt(self):
        """Prompt pro agenta pokyn nepotřebuje – nevypisuje se, předává se."""
        prompt = "```\nJsi nezávislý oponent. DOKUMENT: <cesta>\n```\n\nSpusť agenta.\n"
        self.assertEqual(list(templates(prompt)), [],
                         "kontrola bere zadání pro subagenta jako šablonu výstupu")


class ChecksActuallyCatch(unittest.TestCase):
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
    SAMPLE = ROOT / "skills/skill/SKILL.md"

    def mutate(self, replacement: tuple) -> list:
        """Vrátí vady, které kontroly najdou nad poškozenou kopií vzoru."""
        import shutil, tempfile
        original = self.SAMPLE.read_text(encoding="utf-8")
        old, new = replacement
        self.assertIn(old, original, f"mutace se nemá čeho chytit: {old!r}")
        # nahrazuje se KAŽDÝ výskyt: `PREFLIGHT.md` je ve vzoru čtyřikrát
        # a závěrečný verdikt dvakrát, takže mutace jednoho výskytu nic nezmění
        # a test by prošel, i kdyby kontrola nefungovala
        damaged = original.replace(old, new)
        self.assertNotEqual(damaged, original, "mutace nic nezměnila")
        temp_dir = Path(tempfile.mkdtemp())
        try:
            (temp_dir / "skill").mkdir()
            copy = temp_dir / "skill" / "SKILL.md"
            copy.write_text(damaged, encoding="utf-8")
            return StandardCompliance("test_skills_match_standard").defects(copy)
        finally:
            shutil.rmtree(temp_dir)

    def test_missing_section_is_reported(self):
        for heading, expected_defect in (
                ("## Co skill dělá", "chybí `## Co skill dělá`"),
                ("## Co skill nedělá", "chybí `## Co skill nedělá`"),
                ("## Fáze 0 – Příprava", "chybí `## Fáze 0 – Příprava`"),
        ):
            with self.subTest(heading=heading):
                defects = self.mutate((heading, "## Něco jiného"))
                self.assertIn(expected_defect, defects, f"kontrola nechytila smazané {heading!r}: {defects}")


    def test_copied_cycle_step_chain_is_reported(self):
        """Kontrola opsaného cyklu bez mutace nedokazuje nic – žádný skill ho dnes nemá."""
        cycle = cycle_from_rules()
        clean = self.SAMPLE.read_text(encoding="utf-8")
        self.assertFalse(cycle_step_chains(clean, cycle), "vzor už řetěz obsahuje")
        for text in ("postupuj takhle: `/specify` → `/oponent` → `/breakdown`",
                     "cesta /specify -> /oponent -> /breakdown"):
            with self.subTest(text=text):
                self.assertTrue(cycle_step_chains(clean + "\n" + text, cycle),
                                f"kontrola nechytila opsaný řetěz: {text!r}")
        # Dva sousedi se hlásit nesmějí, jinak by pravidlo zakázalo popis vazby
        self.assertFalse(cycle_step_chains("`/specify` → `/breakdown`", cycle))

    def test_missing_preflight_link_is_reported(self):
        defects = self.mutate(("PREFLIGHT.md", "JINY.md"))
        self.assertIn("příprava neodkazuje na `skills/PREFLIGHT.md`", defects, defects)

    def test_missing_final_verdict_is_reported(self):
        defects = self.mutate(("Zakonči jednou z těchto vět", "Skonči nějak"))
        self.assertIn("chybí závěrečný verdikt", defects, defects)

    def test_link_into_foreign_skill_is_reported(self):
        defects = self.mutate(("## Fáze 3 – Tabulka delegací",
                           "## Fáze 3 – Tabulka delegací\n\nPostupem z `/review`, Fáze 0.1."))
        self.assertIn("odkazuje dovnitř fáze jiného skillu", defects, defects)

    def test_wrong_section_order_is_reported(self):
        """`Časté chyby` u skillu s přílohami musí stát naposled."""
        import shutil, tempfile
        text = self.SAMPLE.read_text(encoding="utf-8")
        i = text.index("\n## Časté chyby")
        # Poslední fáze se hledá jako poslední nadpis `## Fáze …`, ne jménem:
        # závěr se podle normy jmenovat nemusí („Úklid a shrnutí“, „Předání“)
        # a přečíslování by test shodilo hláškou o chybějícím podřetězci
        # místo nálezem. Týmž kritériem pozná závěr i kontrola samotná.
        j = max(m.start() for m in re.finditer(r"\n## Fáze [0-9]", text))
        moved = text[:j] + text[i:].rstrip() + "\n" + text[j:i]
        temp_dir = Path(tempfile.mkdtemp())
        try:
            (temp_dir / "skill").mkdir()
            copy = temp_dir / "skill" / "SKILL.md"
            copy.write_text(moved, encoding="utf-8")
            defects = StandardCompliance("test_skills_match_standard").defects(copy)
        finally:
            shutil.rmtree(temp_dir)
        self.assertTrue(any("Časté chyby" in v for v in defects),
                        f"kontrola nechytila přesunuté `Časté chyby`: {defects}")

    def test_dangling_link_to_own_phase_is_reported(self):
        """Tohle je ta třída chyb, kterou ruční ověření jednou minulo."""
        import shutil, tempfile
        original = self.SAMPLE.read_text(encoding="utf-8")
        temp_dir = Path(tempfile.mkdtemp())
        try:
            (temp_dir / "skill").mkdir()
            copy = temp_dir / "skill" / "SKILL.md"
            copy.write_text(original.replace("*Fázi 3*", "*Fázi 33*", 1), encoding="utf-8")
            original_list = SKILLS[:]
            SKILLS[:] = [copy]
            try:
                with self.assertRaises(AssertionError):
                    SkillLinks(
                        "test_intra_skill_phase_links_point_to_existing_heading"
                    ).test_intra_skill_phase_links_point_to_existing_heading()
            finally:
                SKILLS[:] = original_list
        finally:
            shutil.rmtree(temp_dir)


def required_readme_sections() -> tuple:
    """Nadpisy, které norma žádá po každé vizitce – čtené ze `SKILLS.md`.

    Schválně ne z konstanty v testu. Kontrola měřená vlastní konfigurací
    nehlídá nic: dokud tenhle seznam stál natvrdo, dalo se ho zkrátit na
    polovinu a mutační testy prošly, protože iterovaly přes tutéž zkrácenou
    n-tici. Zdrojem pravdy je norma; test z ní jen čte.

    Sekce označené šipkou (`← jen má-li skill…`) jsou podmíněné a vypadnou.
    """
    text = (ROOT / "skills/SKILLS.md").read_text(encoding="utf-8")
    begin = text.index("### Struktura")
    block = text[text.index("```", begin) + 3:]
    block = block[:block.index("```")]
    section = tuple(r.strip() for r in block.splitlines()
                  if r.startswith(("## ", "### ")) and "←" not in r)
    if len(section) < 5:
        raise AssertionError(f"ze `SKILLS.md` se přečetlo jen {len(section)} sekcí: {section}")
    return section


#: Nadpisy, které norma žádá po každém README skillu – v pořadí z normy.
REQUIRED_README = required_readme_sections()

#: Mez z normy: zhruba dvě obrazovky.
README_LIMIT = 120

REPO_URL = "https://github.com/jantichy/claude/tree/main/skills/"

FRAME = "**Součást životního cyklu projektu.**"
BULK_INSTALL = "Nebo celou sadu naráz."


def readme_defects(text: str, name: str, in_cycle: bool) -> list:
    """Vrátí vady jednoho README proti normě *README skillu*.

    Čistá funkce nad textem, ne nad diskem – jedině tak se dá předložit
    poškozený vstup a ověřit, že kontrola nález opravdu nahlásí
    (`ChecksActuallyCatch`). Kontroly, které potřebují hlavičku skillu
    nebo souborový systém, mají vlastní testy.
    """
    defects = _section_defects(text)
    defects += _install_defects(text, name)
    defects += _frame_defects(text, in_cycle)

    row_count = len(text.splitlines())
    if row_count > README_LIMIT:
        defects.append(f"README má {row_count} řádků, mez je {README_LIMIT}")

    return defects


def _section_defects(text: str) -> list:
    """Přítomnost i pořadí povinných sekcí.

    Pořadí se hlídá proto, že ho norma žádá a `/skill` při revizi kontroluje –
    bez kontroly je to pravidlo, které drží jen ten, kdo si na ně vzpomene.
    """
    defects, positions = [], []
    for heading in REQUIRED_README:
        i = text.find(f"\n{heading}")
        if i < 0:
            defects.append(f"chybí sekce `{heading}`")
        else:
            positions.append((i, heading))
    order = [n for _, n in sorted(positions)]
    expected = [n for n in REQUIRED_README if n in order]
    if order != expected:
        defects.append(f"sekce nejdou v pořadí z normy: {order} místo {expected}")
    return defects


def _install_defects(text: str, name: str) -> list:
    """Instalace musí být pokyn pro Clauda uvnitř své sekce, ne URL kdekoliv."""
    begin = text.find("## Jak si ho nainstalovat")
    if begin < 0:
        return []                             # hlásí kontrola sekcí
    stop = text.find("\n---", begin)
    section = text[begin:stop if stop > 0 else len(text)]
    url = REPO_URL + name
    quotes = [r for r in section.splitlines() if r.lstrip().startswith(">")]
    if url not in section:
        return [f"instalační sekce neodkazuje na {url}"]
    if not any(url in r for r in quotes):
        return ["odkaz na repozitář není v citovaném pokynu pro Clauda"]
    return []


def _frame_defects(text: str, in_cycle: bool) -> list:
    """Rámeček a hromadná instalace: povinné v cyklu, zakázané mimo něj."""
    if in_cycle:
        return ([] if FRAME in text else ["chybí rámeček s celým životním cyklem"]) + \
               ([] if BULK_INSTALL in text else ["chybí hromadná instalace celého životního cyklu"])
    return ([] if FRAME not in text else ["skill mimo životní cyklus má rámeček životního cyklu"]) + \
           ([] if BULK_INSTALL not in text else ["skill mimo životní cyklus nabízí hromadnou instalaci sady"])


class SkillReadme(unittest.TestCase):
    """README skillu proti `skills/SKILLS.md`, *README skillu*.

    Je to jediná část skillu psaná **pro člověka zvenčí** – text, na který
    se posílá odkaz. Právě proto se rozpadá tiše: chybějící sekce nikoho za
    běhu neomezí a pozná se až ve chvíli, kdy si ji někdo cizí přečte.
    """

    CYCLE = cycle_from_rules()
    #: Kroky, které rámeček jmenuje, ale skill k nim ještě nevznikl. V rámečku
    #: stojí jen kódem bez odkazu (norma, *Skill ze životního cyklu*) a do
    #: hromadné instalace nepatří vůbec – pokyn, který si vyžádá neexistující
    #: adresář, se nepovede celý, takže by chybějící krok shodil i instalaci
    #: těch hotových.
    MISSING = cycle_missing_skills()

    def _readme(self, skill: Path) -> Path:
        return skill.parent / "README.md"

    def test_every_skill_has_readme(self):
        """Skill bez README nejde nikomu doporučit odkazem."""
        absent = [s.parent.name for s in SKILLS if not self._readme(s).exists()]
        self.assertFalse(absent, f"skilly bez vlastního README: {absent}")

    def test_readme_matches_standard(self):
        """Sekce a jejich pořadí, tvar instalace, rámeček a mez délky.

        Jedna kontrola místo pěti, protože všechny měří týž text proti téže
        sekci normy – a hlavně proto, že se pak dá mutovat jako celek
        (`ChecksActuallyCatch`).
        """
        for skill in SKILLS:
            readme = self._readme(skill)
            if not readme.exists():
                continue
            with self.subTest(skill=skill.parent.name):
                defects = readme_defects(readme.read_text(encoding="utf-8"),
                                   skill.parent.name,
                                   skill.parent.name in self.CYCLE)
                self.assertFalse(defects, f"{readme}: {defects}")

    def test_cycle_skill_readme_links_other_steps(self):
        """Čtenář, kterému přišel odkaz na jeden skill, jinak neví o těch ostatních."""
        for skill in SKILLS:
            if skill.parent.name not in self.CYCLE:
                continue
            readme = self._readme(skill)
            if not readme.exists():
                continue
            with self.subTest(skill=skill.parent.name):
                text = readme.read_text(encoding="utf-8")
                own = skill.parent.name
                self.assertTrue(f"**`/{own}`**" in text,
                    f"{readme}: vlastní krok není v rámečku tučně")
                self.assertFalse(f"(../{own}/README.md)" in text,
                    f"{readme}: rámeček odkazuje sám na sebe – vlastní krok je bez odkazu")
                for step in sorted(self.CYCLE):
                    if step == own:
                        continue
                    if step in self.MISSING:
                        self.assertIn(f"`/{step}`", text,
                            f"{readme}: rámeček nejmenuje `/{step}`")
                        self.assertNotIn(f"(../{step}/README.md)", text,
                            f"{readme}: rámeček odkazuje na README, které neexistuje: `/{step}`")
                        continue
                    self.assertTrue(f"(../{step}/README.md)" in text,
                        f"{readme}: rámeček neodkazuje na `/{step}`")

    def test_bulk_install_names_all_steps(self):
        """Přibude-li krok, musí ho vyjmenovat i pokyn na instalaci celé sady.

        Rámeček výš hlídají odkazy, ale seznam jmen v instalačním promptu je
        prostý text – ten by přidaný krok tiše minul a lidé by si nainstalovali
        neúplnou sadu."""
        for skill in SKILLS:
            if skill.parent.name not in self.CYCLE:
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
            ends = [text.find(delimiter, i) for delimiter in ("\n---", "\n## ")]
            ends = [k for k in ends if k > 0]
            paragraph = text[i:min(ends) if ends else len(text)]
            with self.subTest(skill=skill.parent.name):
                for step in sorted(self.CYCLE):
                    if step in self.MISSING:
                        self.assertNotRegex(paragraph, rf"\b{step}\b",
                            f"{readme}: hromadná instalace slibuje `{step}`, který zatím není skill")
                        continue
                    self.assertRegex(paragraph, rf"\b{step}\b",
                        f"{readme}: hromadná instalace nejmenuje `{step}`")

    def test_readme_names_all_modes(self):
        """Režim, který README zamlčí, uživatel nikdy nepoužije.

        Bere se první skupina `argument-hint` a jen tehdy, když je to výčet
        jmen režimů (`[create|adopt|update]`), ne zástupný text (`[dokument]`,
        `[větev|tag|hash]`). Výchozí režim se jmenuje taky – bez toho ho nejde
        napsat explicitně.
        """
        for skill in SKILLS:
            hint = frontmatter(skill).get("argument-hint", "")
            group_match = re.match(r"\[([^\]]+)\]", hint)
            if not group_match or "|" not in group_match.group(1):
                continue
            modes = group_match.group(1).split("|")
            if not all(re.fullmatch(r"[a-z]+", r) for r in modes):
                continue
            readme = self._readme(skill)
            if not readme.exists():
                continue
            text = readme.read_text(encoding="utf-8")
            for mode in modes:
                with self.subTest(skill=skill.parent.name, mode=mode):
                    # Stačí jméno režimu v kódové značce – ať už s lomítkem
                    # (`/skill update`), nebo samo (`update`) tam, kde README
                    # režimy vypisuje jako seznam.
                    self.assertTrue(
                        f"`{mode}`" in text or f"/{skill.parent.name} {mode}" in text,
                        f"{readme}: režim `{mode}` z argument-hint není v README")

    def test_relative_readme_links_point_to_existing_file(self):
        """Rozbitý odkaz mezi README uvidí ten, komu se skill doporučuje.

        Kontrola `test_file_links_exist` na tohle nestačí – ta hledá
        cesty v obrácených apostrofech (`~/.claude/…`), kdežto README používají
        markdownové odkazy s relativní cestou. Rámečkové odkazy sice kryje
        `test_cycle_skill_readme_links_other_steps`, ale jen
        ty – odkaz kamkoliv jinam procházel tiše.
        """
        link = re.compile(r"\]\(([^)\s#]+\.(?:md|sh|py|png|json))\)")
        files = [s.parent / "README.md" for s in SKILLS] + [ROOT / "README.md"]
        for readme in files:
            if not readme.exists():
                continue
            with self.subTest(readme=readme.parent.name):
                absent = sorted({
                    target for target in link.findall(readme.read_text(encoding="utf-8"))
                    if not target.startswith(("http://", "https://", "~/"))
                    and not (readme.parent / target).resolve().exists()
                })
                self.assertFalse(absent, f"{readme}: odkaz na neexistující soubor: {absent}")

    def test_standard_template_names_all_steps(self):
        """README hlídá test, normu samotnou dosud nic.

        Šablona hromadné instalace v `SKILLS.md` vyjmenovává kroky cyklu
        jménem – přidaný krok by ji tiše rozešel, tedy přesně to riziko,
        kvůli kterému norma o kus výš zakazuje uvádět v rámečku počet.
        """
        standard = (ROOT / "skills/SKILLS.md").read_text(encoding="utf-8")
        i = standard.find(BULK_INSTALL)
        self.assertGreater(i, 0, "v normě chybí šablona hromadné instalace")
        stop = standard.find("```", standard.find("```", i) + 3)
        template = standard[i:stop if stop > 0 else len(standard)]
        for step in sorted(self.CYCLE):
            with self.subTest(step=step):
                if step in self.MISSING:
                    self.assertNotRegex(template, rf"\b{step}\b",
                        f"šablona hromadné instalace v SKILLS.md slibuje `{step}`, "
                        "který zatím není skill")
                    continue
                self.assertRegex(template, rf"\b{step}\b",
                    f"šablona hromadné instalace v SKILLS.md nejmenuje `{step}`")

    def test_main_readme_links_to_skill_dir(self):
        """Bez odkazu je podrobné README neviditelné.

        Míří se na adresář, ne na soubor: GitHub v adresáři `README.md` rovnou
        vypíše, takže druhý odkaz na totéž místo by byl navíc.
        """
        main_readme = (ROOT / "README.md").read_text(encoding="utf-8")
        absent = [s.parent.name for s in SKILLS
                 if f"(skills/{s.parent.name}/)" not in main_readme]
        self.assertFalse(absent, f"hlavní README neodkazuje na adresář skillu: {absent}")


class SkillScripts(unittest.TestCase):
    """Skripty ve skillech nečte žádná jiná kontrola.

    `typecheck` pouští `swiftc` a `lint` shellcheck; Python ve `skills/*/scripts/`
    by tedy zůstal bez kontroly a překlep by se poznal až za ostrého běhu.
    """

    # Bere i skripty ležící přímo v adresáři skillu, ne jen ve scripts/: /transcript
    # je má tam a dřívější glob je míjel, takže je nečetla žádná kontrola.
    SCRIPTS = sorted(set((ROOT / "skills").glob("*/scripts/*.py"))
                     | set((ROOT / "skills").glob("*/*.py")))

    def test_scripts_were_found(self):
        """Prázdný glob projde oběma testy níž a nikdo se nedozví, že se nic neměří.

        Přejmenuje-li se adresář nebo se skripty přesunou (u /transcript se to
        fakticky stalo), glob přestane vracet cokoliv a assert nad prázdným
        seznamem uspěje vždycky. Ověřeno mutací: rozbití globu SKILLS shodí pět
        testů, rozbití SKRIPTY dřív neshodilo ani jeden.
        """
        self.assertGreaterEqual(len(self.SCRIPTS), 10,
            f"glob našel jen {len(self.SCRIPTS)} skriptů – přesunuly se, nebo se rozbil vzor?")

    def test_scripts_compile(self):
        """Syntaktická vada ve skriptu se jinak pozná až uprostřed sběru dat."""
        import py_compile
        import tempfile
        for script in self.SCRIPTS:
            with self.subTest(script=str(script.relative_to(ROOT))):
                with tempfile.TemporaryDirectory() as tmp:
                    try:
                        py_compile.compile(str(script), cfile=f"{tmp}/out.pyc",
                                           doraise=True)
                    except py_compile.PyCompileError as error:
                        self.fail(str(error))

    def test_extract_wpress_does_not_write_outside_target(self):
        """Cesta v .wpress hlavičce jsou data z archivu, ne argument skriptu.

        Bez kontroly si archiv určí, kam se zapisuje: `../..` vyleze z cílového
        adresáře a absolutní cesta ho zahodí úplně, protože `Path("/a") / "/b"`
        je `/b`. Cílem bývá vlastní záloha, jenže ta se často tahá ze starého
        hostingu, kde ji roky nikdo nehlídal.
        """
        import subprocess
        import tempfile
        script = ROOT / "skills/compose/scripts/extract_wpress.py"
        if not script.exists():
            self.skipTest("extract_wpress.py v repozitáři není")

        def archive(file_path: str, name: str, content: bytes = b"x") -> bytes:
            h = name.encode().ljust(255, b"\x00")
            h += str(len(content)).encode().ljust(14, b"\x00")
            h += b"0".ljust(12, b"\x00")
            h += file_path.encode().ljust(4096, b"\x00")
            return h + content + b"\x00" * 4377

        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            target = tmp / "out"
            for description, file_path in (("relativní", "../../UNIK"), ("absolutní", str(tmp / "ABS"))):
                with self.subTest(file_path=description):
                    archive_path = tmp / "a.wpress"
                    archive_path.write_bytes(archive(file_path, "evil.txt"))
                    r = subprocess.run(["python3", str(script), str(archive_path), str(target)],
                                       capture_output=True, text=True)
                    self.assertNotEqual(r.returncode, 0,
                        f"archiv s {description} cestou ven se rozbalil bez odmítnutí")
                    self.assertFalse((tmp / "UNIK").exists() or (tmp / "ABS").exists(),
                        "soubor z archivu se zapsal mimo výstupní adresář")

            # Poctivý archiv se musí rozbalit dál – ať oprava nezakáže i běžný běh.
            archive_path = tmp / "ok.wpress"
            archive_path.write_bytes(archive("wp-content/posts", "clanek.txt"))
            r = subprocess.run(["python3", str(script), str(archive_path), str(target)],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, f"poctivý archiv se nerozbalil: {r.stderr}")
            self.assertTrue((target / "wp-content/posts/clanek.txt").exists())

    def test_scripts_do_not_derive_target_from_location(self):
        """Cíl patří do argumentu, jinak skript nepřežije přesun.

        Generátory archivu si výstup odvozovaly z `__file__` a při stěhování
        do skillu by tiše zapisovaly vedle něj – ne do archivu.
        """
        failing = [str(s.relative_to(ROOT)) for s in self.SCRIPTS
                 if "__file__" in s.read_text(encoding="utf-8")]
        self.assertFalse(failing, f"skripty odvozují cestu z vlastního umístění: {failing}")


class ReadmeChecksActuallyCatch(unittest.TestCase):
    """Mutační testy nad `readme_defects()`.

    Vrstva vizitek přibyla jako poslední a byla jediná bez důkazu, že něco
    chytá – `.claude/CLAUDE.md` přitom o mutacích mluvil tak, že je zahrnoval.
    Platí tu totéž co o mutacích nad `SKILL.md`: kontrola, která nic nechytá,
    projde stejně tiše jako ta funkční.

    Mutuje se nad skutečnými README: `/attack` je v životním cyklu,
    `/report` mimo něj, takže pokrývají obě větve funkce.
    """

    IN_CYCLE = ROOT / "skills/attack/README.md"
    OUTSIDE = ROOT / "skills/report/README.md"

    def defects(self, sample: Path, name: str, in_cycle: bool, replacement=None) -> list:
        text = sample.read_text(encoding="utf-8")
        if replacement is not None:
            old, new = replacement
            self.assertIn(old, text, f"mutace se nemá čeho chytit: {old!r}")
            text = text.replace(old, new)
        return readme_defects(text, name, in_cycle)

    def test_samples_are_clean(self):
        """Bez tohohle by mutace nedokazovaly nic – vady by mohly být původní."""
        self.assertFalse(self.defects(self.IN_CYCLE, "attack", True))
        self.assertFalse(self.defects(self.OUTSIDE, "report", False))

    def test_missing_section_is_reported(self):
        """Každá povinná sekce zvlášť – jinak jde tři z šesti přestat vynucovat.

        Doloženo: dokud se mutovala jen `## Co nedělá`, prošlo zkrácení
        `REQUIRED_README` na polovinu bez jediného padlého testu.
        """
        for heading in REQUIRED_README:
            with self.subTest(section=heading):
                # Nadpis musí zmizet, ne se prodloužit: `## Co umí jinak`
                # pořád obsahuje `## Co umí` a kontrola by ho našla dál.
                defects = self.defects(self.OUTSIDE, "report", False,
                                 ("\n" + heading, "\n" + heading.replace("#", "@", 1)))
                self.assertTrue(any(f"chybí sekce `{heading}`" in v for v in defects), defects)

    def test_swapped_section_order_is_reported(self):
        text = self.OUTSIDE.read_text(encoding="utf-8")
        i, j = text.index("\n## Co umí"), text.index("\n## Proč zrovna tenhle")
        swapped = (text[:i] + text[j:j + len("\n## Proč zrovna tenhle")]
                     + text[i + len("\n## Co umí"):j]
                     + "\n## Co umí" + text[j + len("\n## Proč zrovna tenhle"):])
        defects = readme_defects(swapped, "report", False)
        self.assertTrue(any("pořadí" in v for v in defects), defects)

    def test_missing_frame_in_cycle_skill_is_reported(self):
        defects = self.defects(self.IN_CYCLE, "attack", True,
                         ("**Součást životního cyklu projektu.**", "**Poznámka.**"))
        self.assertTrue(any("rámeček" in v for v in defects), defects)

    def test_frame_outside_cycle_is_reported(self):
        text = self.OUTSIDE.read_text(encoding="utf-8")
        rows = text.split("\n")
        rows.insert(2, "> **Součást životního cyklu projektu.** …")
        defects = readme_defects("\n".join(rows), "report", False)
        self.assertTrue(any("má rámeček" in v for v in defects), defects)

    def test_missing_bulk_install_is_reported(self):
        defects = self.defects(self.IN_CYCLE, "attack", True, (BULK_INSTALL, "Nebo taky ne."))
        self.assertTrue(any("hromadná instalace" in v for v in defects), defects)

    def test_bulk_install_outside_cycle_is_reported(self):
        """Předstírat sadu u skillu, který se pouští samostatně, by mátlo."""
        text = self.OUTSIDE.read_text(encoding="utf-8").replace(
            "## Jak si ho nainstalovat", "## Jak si ho nainstalovat\n\n" + BULK_INSTALL, 1)
        defects = readme_defects(text, "report", False)
        self.assertTrue(any("hromadnou instalaci" in v for v in defects), defects)

    def test_install_outside_quoted_instruction_is_reported(self):
        """URL kdekoliv v souboru nestačí – musí být v pokynu pro Clauda."""
        defects = self.defects(self.OUTSIDE, "report", False,
                         ("> Jdi na " + REPO_URL + "report", "Jdi na " + REPO_URL + "report"))
        self.assertTrue(any("citovaném pokynu" in v for v in defects), defects)

    def test_missing_repo_link_is_reported(self):
        defects = self.defects(self.OUTSIDE, "report", False, (REPO_URL + "report", "https://example.com"))
        self.assertTrue(any("neodkazuje" in v for v in defects), defects)

    def test_exceeded_length_limit_is_reported(self):
        """Těsně o jeden řádek – jinak by mutace dokazovala jen řádovou nerovnost."""
        text = self.OUTSIDE.read_text(encoding="utf-8")
        absent = README_LIMIT - len(text.splitlines()) + 1
        self.assertGreater(absent, 0, "vzor už mez přetahuje, mutace by nic nedokázala")
        defects = readme_defects(text + "\n" * absent, "report", False)
        self.assertTrue(any("mez je" in v for v in defects), defects)
        self.assertFalse(readme_defects(text + "\n" * (absent - 1), "report", False),
                         "kontrola hlásí vadu ještě před překročením meze")


if __name__ == "__main__":
    unittest.main()


def _section(text: str, heading: str) -> str:
    """Tělo sekce od nadpisu po nejbližší nadpis stejné nebo vyšší úrovně."""
    begin = text.index(heading) + len(heading)
    rest = text[begin:]
    following = re.search(r"^#{1,2} ", rest, re.M)
    return rest[: following.start()] if following else rest


class DepotCoreParts(unittest.TestCase):
    """Dvě pravidla, na kterých /depot stojí a která se obě už jednou porušila.

    Skill přesouvá soubory po disku, takže jeho vada není špatná odpověď, ale
    nevratně přemístěný nebo přepsaný podklad. Obecné kontroly tvaru výš hlídají
    hlavičku, sekce a verdikt – tyhle dvě věci ne, a přitom obě dnes selhaly:

    *Rozsah* vznikl z měření. Agent puštěný na tentýž úkol bez skillu si rozšířil
    rozsah ze dvou předaných souborů na celý ~/Downloads. Zmizí-li ta sekce při
    nějakém pozdějším zkracování, vrátí se i to chování a pozná se to až podle
    hromadného přesunu.

    *Hranice* si původně zakazovala přepis absolutně, tedy větou nad uživatelem –
    a `RULES.md`, *Přednost pravidel*, říká, že žádná věta v Markdownu živý pokyn
    nepřebije. Hranice, která se tváří jako zákaz, se při první kolizi buď obejde,
    nebo vyrobí odmítnutí práce, o kterou si uživatel vědomě řekl. Odkaz na to
    pravidlo je tedy doklad, že hranici drží důvod, ne příkaz.
    """

    def setUp(self):
        file_path = ROOT / "skills" / "depot" / "SKILL.md"
        if not file_path.exists():
            self.skipTest("/depot v repozitáři není")
        self.skill_body = body(file_path)

    def test_scope_is_limited_to_argument(self):
        self.assertIn("## Rozsah", self.skill_body, "/depot přišel o sekci Rozsah")
        scope = _section(self.skill_body, "## Rozsah")
        self.assertIn(
            "v argumentu", scope,
            "Rozsah neváže práci na to, co stojí v argumentu – bez toho se běh rozlije na okolí",
        )

    def test_boundaries_are_not_ban_over_user(self):
        self.assertIn("## Hranice", self.skill_body, "/depot přišel o sekci Hranice")
        boundaries = _section(self.skill_body, "## Hranice")
        self.assertIn(
            "Přednost pravidel", boundaries,
            "Hranice se tváří jako zákaz nad uživatelem – chybí odkaz na RULES.md, Přednost pravidel",
        )


class DepotCorePartsActuallyCatch(unittest.TestCase):
    """Mutační test: bez něj by kontrola výš prošla i nad prázdným souborem."""

    def _reports(self, skill_body):
        case = DepotCoreParts("test_scope_is_limited_to_argument")
        case.skill_body = skill_body
        failures = []
        for name in ("test_scope_is_limited_to_argument", "test_boundaries_are_not_ban_over_user"):
            case = DepotCoreParts(name)
            case.skill_body = skill_body
            try:
                getattr(case, name)()
            except AssertionError as error:
                failures.append(str(error))
        return failures

    def test_vanished_scope_is_reported(self):
        skill_body = body(ROOT / "skills" / "depot" / "SKILL.md").replace("## Rozsah", "## Něco jiného")
        self.assertTrue(self._reports(skill_body), "vyříznutý Rozsah neshodil kontrolu")

    def test_boundaries_without_rule_precedence_link_are_reported(self):
        skill_body = body(ROOT / "skills" / "depot" / "SKILL.md").replace("Přednost pravidel", "něco")
        self.assertTrue(self._reports(skill_body), "hranice bez opory v RULES.md neshodila kontrolu")
