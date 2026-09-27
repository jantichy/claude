"""Regresní testy měřidla `skills/cost.py`.

Měřidlo existuje proto, aby se o stavbě skillů rozhodovalo čísly, ne dojmem –
`/cleanup` se podle dojmu dvakrát přepsal špatně a stálo to dva dny práce.
Tím se z něj ale stala vrstva, na které rozhodnutí stojí, a **měřidlo, které
lže, je horší než žádné**: čísla vypadají stejně věrohodně, ať jsou z celého
vzorku, nebo z jeho poloviny (`~/Dev/context/coding/quality.md`, *Měřidlo musí
odlišit vlastní selhání od nálezu*).

Testují se proto oba směry selhání:

- **započítá, co nemá** – běh se ohraničí příliš široko a sebere cenu práce,
  která k němu nepatří. To je ta zrádnější polovina: číslo vyjde vyšší a nikdo
  nepozná, že v něm sedí cizí práce, takže se podle něj zamítne změna, která
  ve skutečnosti ušetřila.
- **nezapočítá, co má** – běh se tiše zahodí a medián se spočítá z menšího
  vzorku. Proto se počet zahozených **hlásí**, ne mlčí; starý jednorázový
  skript ho zahazoval tiše.

Nad hlavním scénářem stojí **mutační test**: vyřadí uzavření hranice na cizím
skillu a ověří, že se cena běhu opravdu nafoukne. Bez něj by hlavní test
zůstal zelený i tehdy, kdyby správné číslo vznikalo z jiného důvodu.

Odvození markeru konce ze `SKILL.md` se testuje zvlášť, protože je to jediné
místo, kde měřidlo závisí na tvaru cizího souboru: kdyby se přestal odvozovat,
neohlásí se nula běhů, ale skript se zastaví s návratovým kódem 2.

Spouští se: python3 -m unittest discover -s tests -q

Jen stdlib.
"""
import importlib.util
import json
import os
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COST = ROOT / "skills" / "cost.py"


def load(path, name):
    """Naimportuje modul z cesty – používá se i pro zmutovanou kopii skriptu."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def user(text):
    return {"type": "user", "timestamp": "2026-09-27T10:00:00Z",
            "message": {"role": "user", "content": text}}


def call(text, tokens, ts="2026-09-27T10:01:00Z"):
    """Odpověď modelu, která něco stála – `tokens` jsou výstupní tokeny."""
    return {"type": "assistant", "timestamp": ts,
            "message": {"role": "assistant", "content": [{"type": "text", "text": text}],
                        "usage": {"input_tokens": 0, "cache_creation_input_tokens": 0,
                                  "cache_read_input_tokens": 0, "output_tokens": tokens}}}


class Fixture(unittest.TestCase):
    """Dočasný adresář se session logy, ať se měří nad vyrobeným vzorkem."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "projects"
        (self.root / "proj").mkdir(parents=True)
        self.addCleanup(self.tmp.cleanup)
        self.cost = load(COST, "cost_under_test")

    def session(self, records, name="sess"):
        path = self.root / "proj" / f"{name}.jsonl"
        with open(path, "w", encoding="utf-8") as fh:
            for r in records:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        return path

    def scan(self, skill="demo", markers=("## Hotovo",), module=None):
        module = module or self.cost
        return module.scan(skill, list(markers), root=str(self.root))


class Ohraniceni(Fixture):
    """Co se do běhu započítá a co ne."""

    def test_beh_konci_markerem_a_dalsi_praci_nebere(self):
        """Práce za markerem konce do ceny běhu nepatří."""
        self.session([
            user("<command-name>/demo</command-name>"),
            call("pracuju", 100),
            call("## Hotovo\nvše hotovo", 10),
            user("ještě něco jiného"),
            call("tohle už není součást běhu", 9000),
        ])
        runs, dropped = self.scan()
        self.assertEqual(len(runs), 1)
        self.assertEqual(dropped, 0)
        # 110 výstupních tokenů × 75 / 1e6; kdyby se vzalo i 9000, číslo je 60×větší
        self.assertAlmostEqual(runs[0]["tot"], 110 * 75 / 1e6, places=9)

    def test_beh_bez_markeru_se_zahodi_a_spocita(self):
        """Nedokončený běh se nepočítá – a ohlásí se, místo aby zmizel."""
        self.session([
            user("<command-name>/demo</command-name>"),
            call("pracuju a nikdy nedojdu k závěru", 100),
        ])
        runs, dropped = self.scan()
        self.assertEqual(runs, [])
        self.assertEqual(dropped, 1)

    def test_cizi_skill_ukonci_hranici(self):
        """Marker za vyvoláním jiného skillu už tomuhle běhu nepatří."""
        self.session([
            user("<command-name>/demo</command-name>"),
            call("pracuju", 100),
            user("<command-name>/jiny</command-name>"),
            call("## Hotovo\nzávěr jiného skillu", 9000),
        ])
        runs, dropped = self.scan()
        self.assertEqual(runs, [])
        self.assertEqual(dropped, 1)

    def test_harnessovy_prikaz_hranici_neukonci(self):
        """`/compact` uprostřed dlouhého běhu je běžný, ne konec běhu."""
        self.session([
            user("<command-name>/demo</command-name>"),
            call("pracuju", 100),
            user("<command-name>/compact</command-name>"),
            call("## Hotovo\nzávěr", 10),
        ])
        runs, dropped = self.scan()
        self.assertEqual(len(runs), 1)
        self.assertEqual(dropped, 0)

    def test_dva_behy_v_jedne_session_se_nespletou(self):
        """Druhé vyvolání uzavírá první běh, i když ten marker neměl."""
        self.session([
            user("<command-name>/demo</command-name>"),
            call("první běh se nedokončil", 100),
            user("<command-name>/demo</command-name>"),
            call("druhý běh", 20),
            call("## Hotovo", 10),
        ])
        runs, dropped = self.scan()
        self.assertEqual(len(runs), 1)
        self.assertEqual(dropped, 1)
        self.assertAlmostEqual(runs[0]["tot"], 30 * 75 / 1e6, places=9)


class Subagenti(Fixture):
    """Cena delegované práce se přičítá jen tomu běhu, ve kterém běžela."""

    def subagent(self, sess, ts, tokens, name="agent-1"):
        directory = self.root / "proj" / sess / "subagents"
        directory.mkdir(parents=True, exist_ok=True)
        with open(directory / f"{name}.jsonl", "w", encoding="utf-8") as fh:
            fh.write(json.dumps(call("posudek", tokens, ts)) + "\n")

    def test_agent_v_okne_behu_se_pricte(self):
        self.session([
            user("<command-name>/demo</command-name>"),
            call("pouštím agenta", 100, "2026-09-27T10:00:00Z"),
            call("## Hotovo", 10, "2026-09-27T10:05:00Z"),
        ])
        self.subagent("sess", "2026-09-27T10:02:00Z", 400)
        runs, _ = self.scan()
        self.assertEqual(runs[0]["na"], 1)
        self.assertAlmostEqual(runs[0]["sc"], 400 * 75 / 1e6, places=9)
        self.assertAlmostEqual(runs[0]["tot"], 510 * 75 / 1e6, places=9)

    def test_agent_mimo_okno_behu_se_nepricte(self):
        """Agent puštěný po skončení běhu jeho cenu nezvedá."""
        self.session([
            user("<command-name>/demo</command-name>"),
            call("pracuju", 100, "2026-09-27T10:00:00Z"),
            call("## Hotovo", 10, "2026-09-27T10:05:00Z"),
        ])
        self.subagent("sess", "2026-09-27T11:00:00Z", 9000)
        runs, _ = self.scan()
        self.assertEqual(runs[0]["na"], 0)
        self.assertAlmostEqual(runs[0]["tot"], 110 * 75 / 1e6, places=9)


class Marker(Fixture):
    """Odvození markeru konce ze `SKILL.md`."""

    def skill(self, body):
        home = Path(self.tmp.name) / "home"
        (home / ".claude" / "skills" / "demo").mkdir(parents=True, exist_ok=True)
        (home / ".claude" / "skills" / "demo" / "SKILL.md").write_text(
            textwrap.dedent(body), encoding="utf-8")
        old = os.environ.get("HOME")
        os.environ["HOME"] = str(home)
        self.addCleanup(lambda: os.environ.__setitem__("HOME", old) if old else None)

    def test_bere_posledni_sablonu_s_nadpisem(self):
        self.skill("""
            ## Fáze 1

            ```
            ## Průběžný výpis
            ```

            ## Fáze 2 – Závěr

            ```
            ## Úklid dokončen
            - položek: N
            ```
            """)
        self.assertEqual(self.cost.end_markers("demo"), ["## Úklid dokončen"])

    def test_blok_bez_nadpisu_markerem_neni(self):
        """Za šablonou závěru bývá příkaz shellu – ten koncem běhu není."""
        self.skill("""
            ## Fáze 2 – Závěr

            ```
            ## Oponentura hotová
            ```

            ```sh
            git rev-parse --short HEAD
            ```
            """)
        self.assertEqual(self.cost.end_markers("demo"), ["## Oponentura hotová"])

    def test_priloha_za_zaverem_marker_neprebije(self):
        """Norma staví přílohy za závěrečnou fázi – marker je z fáze, ne z konce.

        Doložená vada: `/review` má za závěrem šablonu kapitoly `## Review`,
        která se v konverzaci vyskytne kdekoliv. Bral-li se poslední blok
        v souboru, ohraničil běh na cizím textu a cena vyšla nafouknutá.
        """
        self.skill("""
            ## Fáze 8 – Shrnutí

            ```
            ## Hotovo
            - nálezů: N
            ```

            ## Kapitola `## Review`

            Zamítnuté nálezy se zapisují takhle:

            ```
            ## Review
            - **DATUM** · `hash` · *nález*
            ```
            """)
        self.assertEqual(self.cost.end_markers("demo"), ["## Hotovo"])

    def test_blok_kodu_nadpis_faze_nepredstira(self):
        """Nadpis fáze uvnitř bloku kódu je ukázka, ne skutečná fáze."""
        self.skill("""
            ## Fáze 1 – Závěr

            ```
            ## Skutečný závěr
            ```

            ## Časté chyby

            Nepiš do šablony nadpis fáze:

            ```
            ## Fáze 9 – tohle je ukázka chyby
            ## Falešný závěr
            ```
            """)
        self.assertEqual(self.cost.end_markers("demo"), ["## Skutečný závěr"])

    def test_chybejici_skill_vrati_prazdno(self):
        """Neexistující skill nesmí vrátit marker, který by měřil cokoliv."""
        self.assertEqual(self.cost.end_markers("neexistuje-takovy-skill"), [])


class Duplikaty(Fixture):
    """Tentýž běh ve dvou transcriptech se nesmí počítat dvakrát."""

    def run_records(self):
        return [
            user("<command-name>/demo</command-name>"),
            call("pracuju", 100),
            call("## Hotovo", 10),
        ]

    def test_tyz_beh_ve_dvou_transcriptech_se_pocita_jednou(self):
        """`/resume` zkopíruje transcript; běh v něm je pořád jeden."""
        self.session(self.run_records(), name="puvodni")
        self.session([user("starší kontext, kvůli kterému je soubor delší")]
                     + self.run_records(), name="po-resume")
        runs, dropped = self.scan()
        self.assertEqual(len(runs), 1)
        self.assertEqual(dropped, 1, "duplikát se má nahlásit, ne zmizet")

    def test_dva_ruzne_behy_se_nesliji(self):
        """Opačný směr: běhy s jinou cenou jsou dva, i když jsou v jeden den."""
        self.session(self.run_records(), name="prvni")
        self.session([
            user("<command-name>/demo</command-name>"),
            call("pracuju jinak", 555),
            call("## Hotovo", 10),
        ], name="druhy")
        runs, dropped = self.scan()
        self.assertEqual(len(runs), 2)
        self.assertEqual(dropped, 0)

    def test_z_duplikatu_zustane_ten_s_agenty(self):
        """Kopie bez podadresáře subagentů by ztratila cenu delegované práce."""
        self.session(self.run_records(), name="bez-agenta")
        self.session(self.run_records(), name="s-agentem")
        directory = self.root / "proj" / "s-agentem" / "subagents"
        directory.mkdir(parents=True)
        with open(directory / "agent-1.jsonl", "w", encoding="utf-8") as fh:
            fh.write(json.dumps(call("posudek", 400, "2026-09-27T10:00:30Z")) + "\n")
        runs, _ = self.scan()
        self.assertEqual(len(runs), 1)
        self.assertEqual(runs[0]["na"], 1)
        self.assertAlmostEqual(runs[0]["sc"], 400 * 75 / 1e6, places=9)


class Mutace(Fixture):
    """Vyřazení hranice na cizím skillu musí cenu běhu nafouknout."""

    def test_bez_rezu_na_cizim_skillu_cena_naroste(self):
        records = [
            user("<command-name>/demo</command-name>"),
            call("pracuju", 100),
            user("<command-name>/jiny</command-name>"),
            call("## Hotovo\nzávěr jiného skillu", 9000),
        ]
        self.session(records)
        self.assertEqual(self.scan()[0], [])

        mutated = Path(self.tmp.name) / "cost_mutated.py"
        source = COST.read_text(encoding="utf-8")
        broken = source.replace(
            "        other = [c for c in commands(recs[j])\n"
            "                 if c != f'/{skill}' and c not in HARNESS]",
            "        other = []")
        self.assertNotEqual(source, broken, "mutace nenašla hlídaný řez")
        mutated.write_text(broken, encoding="utf-8")
        runs, _ = self.scan(module=load(mutated, "cost_mutated"))
        self.assertEqual(len(runs), 1, "bez řezu měl běh projít jako dokončený")
        self.assertAlmostEqual(runs[0]["tot"], 9100 * 75 / 1e6, places=9)

    def test_bez_deduplikace_se_tyz_beh_zdvoji(self):
        """Vyřazení dedupu musí vzorek zdvojit – jinak ho hlídá něco jiného."""
        records = [
            user("<command-name>/demo</command-name>"),
            call("pracuju", 100),
            call("## Hotovo", 10),
        ]
        self.session(records, name="a")
        self.session(records, name="b")
        self.assertEqual(len(self.scan()[0]), 1)

        mutated = Path(self.tmp.name) / "cost_nodedup.py"
        source = COST.read_text(encoding="utf-8")
        broken = source.replace(
            "    runs, duplicates = dedup(runs)",
            "    duplicates = 0")
        self.assertNotEqual(source, broken, "mutace nenašla volání dedupu")
        mutated.write_text(broken, encoding="utf-8")
        runs, _ = self.scan(module=load(mutated, "cost_nodedup"))
        self.assertEqual(len(runs), 2, "bez dedupu měl týž běh projít dvakrát")


if __name__ == "__main__":
    unittest.main()
