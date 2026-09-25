"""Regresní testy deterministických skriptů `/cleanup`.

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

Druhý skript, `extract.py`, existuje z téhož důvodu a nese k tomu ještě jeden:
transcript je z devíti desetin technický balast, takže jeho očištění je úspora
řádu, ne procent. Jeho tiché selhání je ale dražší než u odkazů – **vynechá-li
kategorii, která obsah nese, nikdo to nepozná**, protože výsledek vypadá
úplně. Testuje se proto obojí: že se vynechává jen to, co se vynechávat má,
a že kotvy evidence nesou jen to, co uživatel skutečně napsal.

Spouští se: python3 -m unittest discover -s tests -q

Jen stdlib.
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINKS = ROOT / "skills" / "cleanup" / "scripts" / "links.py"
EXTRACT = ROOT / "skills" / "cleanup" / "scripts" / "extract.py"


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


class PredfiltrBase(unittest.TestCase):
    """Dočasný transcript a pomocníci; sama netestuje nic, aby se testy nedědily."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        self.extract = load(EXTRACT, "extract_module")

    def transcript(self, records):
        path = self.dir / "t.jsonl"
        path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records), encoding="utf-8")
        return path

    def user(self, text, **extra):
        return {"type": "user", "message": {"role": "user", "content": [{"type": "text", "text": text}]}, **extra}

    def tool(self, name, output):
        use = {"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "tool_use", "id": f"id-{name}", "name": name}]}}
        result = {"type": "user", "message": {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": f"id-{name}", "content": output}]}}
        return [use, result]

    def kept(self, records):
        rows = self.extract.load(str(self.transcript(records)))
        kept, _, _ = self.extract.walk(rows)
        return {label: text for _, label, text in kept}


class Predfiltr(PredfiltrBase):
    """Očištění transcriptu: co se vynechá, co zůstane a čím se to doloží."""

    def test_vystup_ctecich_nastroju_se_vynecha(self):
        """Obsah souborů se čte ze zdroje, kde je navíc aktuální."""
        kept = self.kept(self.tool("Read", "OBSAH SOUBORU") + self.tool("Grep", "SHODA"))
        self.assertNotIn("výstup Read", kept)
        self.assertNotIn("výstup Grep", kept)

    def test_vystup_nesouci_obsah_zustane(self):
        """Výstup shellu a zpráva subagenta nikde jinde nejsou – zmizí se session."""
        kept = self.kept(self.tool("Bash", "NAMĚŘENO 42") + self.tool("Agent", "NÁLEZ AGENTA"))
        self.assertEqual(kept.get("výstup Bash"), "NAMĚŘENO 42")
        self.assertEqual(kept.get("výstup Agent"), "NÁLEZ AGENTA")

    def test_mysleni_se_vynecha_ale_spocita(self):
        """Bloky myšlení jsou v transcriptu prázdné, takže se čtou naprázdno."""
        records = [{"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "thinking", "thinking": ""}]}}]
        rows = self.extract.load(str(self.transcript(records)))
        kept, counts, _ = self.extract.walk(rows)
        self.assertEqual(kept, [])
        self.assertEqual(counts["myšlení"], 1, "myšlení musí být vidět v inventuře jako mez běhu")

    def test_cislo_radku_odpovida_zdroji(self):
        """Bez pravého čísla řádku se citace nedá ověřit a padá doložitelnost."""
        records = [{"type": "meta"}, {"type": "meta"}, self.user("TŘETÍ ŘÁDEK")]
        rows = self.extract.load(str(self.transcript(records)))
        kept, _, _ = self.extract.walk(rows)
        self.assertEqual([(n, t) for n, _, t in kept], [(3, "TŘETÍ ŘÁDEK")])

    def test_zprava_z_fronty_se_neztrati(self):
        """Dovětek poslaný uprostřed odpovědi jde jinou cestou než prompt."""
        records = [{"type": "queue-operation", "operation": "enqueue", "content": "JEŠTĚ DODĚLEJ TOHLE"}]
        self.assertEqual(self.kept(records).get("ve frontě"), "JEŠTĚ DODĚLEJ TOHLE")


class KotvyEvidence(PredfiltrBase):
    """Kotvy jsou to, co uživatel napsal – ne všechno s rolí uživatele."""

    def anchors(self, records):
        rows = self.extract.load(str(self.transcript(records)))
        return [t for _, t in self.extract.prompts(rows)]

    def test_skutecny_prompt_je_kotva(self):
        self.assertEqual(self.anchors([self.user("ZAPIŠ TO DO TODA")]), ["ZAPIŠ TO DO TODA"])

    def test_vsuvka_harnessu_kotva_neni(self):
        """Výpis skillu a zpráva subagenta mají roli uživatele, ale nenapsal je on."""
        self.assertEqual(self.anchors([self.user("Base directory for this skill: …", isMeta=True)]), [])

    def test_notifikace_z_fronty_kotva_neni(self):
        """Do fronty padají i hlášky systému; odškrtávat se nemají."""
        records = [
            {"type": "queue-operation", "operation": "enqueue", "content": "<task-notification>hotovo</task-notification>"},
            {"type": "queue-operation", "operation": "enqueue", "content": "[SYSTEM NOTIFICATION] nic"},
        ]
        self.assertEqual(self.anchors(records), [])

    def test_prikaz_skillu_kotva_neni(self):
        self.assertEqual(self.anchors([self.user("<command-name>/cleanup</command-name>")]), [])

    def test_vsuvka_se_ale_cte(self):
        """Nález subagenta je obsah, který zmizí se session – čte se, jen není kotva."""
        kept = self.kept([self.user("NÁLEZ OD AGENTA", isMeta=True)])
        self.assertEqual(kept.get("vsuvka"), "NÁLEZ OD AGENTA")


class RozhraniPredfiltru(PredfiltrBase):
    """Návratové kódy – podle nich se skill rozhoduje."""

    def run_script(self, *args):
        return subprocess.run([sys.executable, str(EXTRACT), *args], capture_output=True, text=True)

    def test_hotovo_vraci_nulu(self):
        path = self.transcript([self.user("ahoj")])
        for mode in ("filter", "inventory"):
            self.assertEqual(self.run_script(mode, str(path)).returncode, 0, mode)

    def test_neznamy_rezim_vraci_dvojku(self):
        path = self.transcript([self.user("ahoj")])
        self.assertEqual(self.run_script("neco", str(path)).returncode, 2)

    def test_chybejici_soubor_vraci_dvojku(self):
        self.assertEqual(self.run_script("filter", str(self.dir / "není.jsonl")).returncode, 2)

    def test_prazdny_transcript_vraci_dvojku(self):
        """Prázdný výsledek se nesmí tvářit jako čistý úklid."""
        path = self.dir / "prazdny.jsonl"
        path.write_text("", encoding="utf-8")
        self.assertEqual(self.run_script("filter", str(path)).returncode, 2)

    def test_inventura_vypise_necteny_zbytek(self):
        """Co se nečte, musí být vidět – jinak se mez běhu nepřizná."""
        records = self.tool("Read", "OBSAH")
        out = self.run_script("inventory", str(self.transcript(records))).stdout
        self.assertIn("NEČTE SE", out)
        self.assertIn("výstup Read", out.split("NEČTE SE")[1])


class MutacePredfiltru(PredfiltrBase):
    """Ověří, že vynechávání vsuvek z kotev drží `isMeta`, ne náhoda."""

    def test_bez_ismeta_se_vsuvka_stane_kotvou(self):
        source = EXTRACT.read_text(encoding="utf-8").replace(
            'if (record.get("message") or {}).get("role") != "user" or record.get("isMeta"):',
            'if (record.get("message") or {}).get("role") != "user":',
            1,
        )
        mutant = self.dir / "extract_mutant.py"
        mutant.write_text(source, encoding="utf-8")
        module = load(mutant, "extract_mutant")
        rows = module.load(str(self.transcript([self.user("VSUVKA", isMeta=True)])))
        self.assertTrue(module.prompts(rows),
                        "vyřazení isMeta nic nezměnilo – test na vsuvky tedy neměří to, co tvrdí")


if __name__ == "__main__":
    unittest.main()
