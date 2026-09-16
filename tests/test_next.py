"""Regresní testy skriptu `/next`, který zjišťuje živé session a jejich větve.

`/next` podle výstupu rozhoduje, jestli úkol v rozdělané větvi **nabídne**
(větev je opuštěná), nebo ho **skryje** (ve vedlejším okně nad ní běží session).
Obě chyby jsou tiché: mrtvá session vydávaná za živou schová zapomenutou práci
navždy, a živá vydávaná za mrtvou nabídne druhé session úkol, na kterém už dělá
první – a jejich větve se srazí.

Testují se proto oba směry: záznam po spadlém procesu se nesmí počítat, živý
proces ano, a větev se bere z **posledního** záznamu transcriptu, ne z prvního –
session ve worktree layoutu startuje v kořeni kontejneru a do větve přechází až
během práce. Chybějící registr musí skončit kódem 2, ne prázdným seznamem:
prázdný seznam by tvrdil, že žádná session neběží.

K větvím projektu skript hledá i **poslední opuštěnou session**, kterou `/next`
nabídne k obnovení přes `/resume`. Tady je tvrdý zákaz: session, která běží –
i obnovená v jiném okně –, se mezi opuštěné nesmí dostat nikdy, jinak by se
jedna konverzace otevřela dvakrát.

Spouští se: python3 -m unittest discover -s tests -q
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills" / "next" / "sessions.py"
COLLECT = ROOT / "skills" / "next" / "collect.py"


class ZiveSessionAJejichVetve(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name)
        self.claude = self.home / ".claude"
        (self.claude / "sessions").mkdir(parents=True)
        # Živý proces, který není předkem skriptu – jako session ve vedlejším okně.
        self.sleeper = subprocess.Popen(["sleep", "60"])

    def tearDown(self):
        self.sleeper.kill()
        self.sleeper.wait()
        self.tmp.cleanup()

    def registruj(self, pid, sid, transcript_lines=None):
        (self.claude / "sessions" / f"{pid}.json").write_text(json.dumps(
            {"pid": pid, "sessionId": sid, "cwd": "/projekt", "name": sid, "status": "waiting"}))
        if transcript_lines is not None:
            adr = self.claude / "projects" / "-projekt"
            adr.mkdir(parents=True, exist_ok=True)
            (adr / f"{sid}.jsonl").write_text(
                "\n".join(json.dumps(r) for r in transcript_lines) + "\n")

    def spust(self, *args):
        env = dict(os.environ, HOME=str(self.home))
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True,
                              text=True, env=env)

    def idle(self):
        run = self.spust("--project", "/projekt")
        self.assertEqual(run.returncode, 0, run.stderr)
        return {s["branch"]: s["session_id"] for s in json.loads(run.stdout)["idle"]}

    def mrtvy_pid(self):
        p = subprocess.Popen(["true"])
        p.wait()
        return p.pid

    def test_vetev_se_bere_z_posledniho_zaznamu(self):
        self.registruj(self.sleeper.pid, "ziva", [
            {"type": "user", "cwd": "/projekt/main", "gitBranch": "main"},
            {"type": "assistant", "cwd": "/projekt/dph", "gitBranch": "specify-dph"},
            {"type": "attachment"},
        ])
        run = self.spust()
        self.assertEqual(run.returncode, 0, run.stderr)
        [s] = json.loads(run.stdout)["sessions"]
        self.assertEqual((s["cwd"], s["branch"], s["self"]),
                         ("/projekt/dph", "specify-dph", False))

    def test_zaznam_po_spadlem_procesu_se_nepocita(self):
        self.registruj(self.mrtvy_pid(), "mrtva", [{"cwd": "/projekt/x", "gitBranch": "x"}])
        run = self.spust()
        self.assertEqual(json.loads(run.stdout)["sessions"], [])

    def test_ziva_session_bez_transcriptu_ma_neznamou_vetev(self):
        self.registruj(self.sleeper.pid, "bez-transcriptu")
        [s] = json.loads(self.spust().stdout)["sessions"]
        self.assertIsNone(s["branch"])

    def test_vlastni_session_je_oznacena(self):
        # Předek skriptu je i tenhle testovací proces.
        self.registruj(os.getpid(), "ja", [{"cwd": "/projekt", "gitBranch": "main"}])
        [s] = json.loads(self.spust().stdout)["sessions"]
        self.assertTrue(s["self"])

    def test_opustena_session_se_nabidne_k_obnoveni(self):
        self.registruj(self.mrtvy_pid(), "stara", [{"cwd": "/projekt/dph", "gitBranch": "specify-dph"}])
        self.assertEqual(self.idle(), {"specify-dph": "stara"})

    def test_ziva_session_neni_nikdy_opustena(self):
        # Táž session je i živá (obnovená v jiném okně) – mezi opuštěné nepatří,
        # ani když má v registru i starý záznam po spadlém procesu.
        self.registruj(self.mrtvy_pid(), "obnovena", [{"cwd": "/projekt/dph", "gitBranch": "specify-dph"}])
        self.registruj(self.sleeper.pid, "obnovena")
        self.assertEqual(self.idle(), {})

    def test_session_z_jineho_projektu_se_nepocita(self):
        self.registruj(self.mrtvy_pid(), "cizi", [{"cwd": "/jiny/dph", "gitBranch": "specify-dph"}])
        self.assertEqual(self.idle(), {})

    def test_necitelny_zaznam_registru_neni_prazdny_seznam(self):
        # Nečitelný záznam může patřit běžící session – kdyby se přeskočil,
        # nabídla by se její konverzace k obnovení podruhé.
        self.registruj(self.mrtvy_pid(), "stara", [{"cwd": "/projekt/dph", "gitBranch": "specify-dph"}])
        (self.claude / "sessions" / "rozbity.json").write_text("{nedopsano")
        run = self.spust("--project", "/projekt")
        self.assertEqual(run.returncode, 2)
        self.assertEqual(run.stdout, "")

    def test_cizi_projekt_neni_in_project(self):
        (self.claude / "sessions" / f"{self.sleeper.pid}.json").write_text(json.dumps(
            {"pid": self.sleeper.pid, "sessionId": "cizi", "cwd": "/jiny"}))
        [s] = json.loads(self.spust("--project", "/projekt").stdout)["sessions"]
        self.assertFalse(s["in_project"])

    def test_opustena_session_nese_adresar_startu(self):
        self.registruj(self.mrtvy_pid(), "stara", [
            {"cwd": "/projekt", "gitBranch": "main"},
            {"cwd": "/projekt/dph", "gitBranch": "specify-dph"},
        ])
        run = self.spust("--project", "/projekt")
        [s] = json.loads(run.stdout)["idle"]
        self.assertEqual((s["start_cwd"], s["cwd"]), ("/projekt", "/projekt/dph"))

    def test_chybejici_registr_neni_prazdny_seznam(self):
        (self.claude / "sessions").rmdir()
        run = self.spust()
        self.assertEqual(run.returncode, 2)
        self.assertEqual(run.stdout, "")


TODO = """# TODO

## Probíhá

- [ ] **Export faktur.** Napojit formát.
- [x] **Hotová věc.** Už je.

## Kola návrhu

### Kolo o DPH

- **Stav:** čeká
- **Větev:** `specify-dph`
- **Čeká na:** nic

### Kolo o fakturaci

- **Stav:** čeká
- **Větev:** `specify-faktury`
- **Čeká na:** Kolo o DPH
"""


class SberFronty(unittest.TestCase):
    """`collect.py` nad skutečným gitem: worktree kontejner, větve a živé session.

    Hlídá to, kvůli čemu sběr vznikl: obsazená větev se musí poznat i tehdy, když
    ji `--no-merged` nevypíše (čerstvá větev bez commitu), fronta se čte z hlavní
    větve, ne z pracovního adresáře, a kolo s rozběhnutou větví nese stav z ní.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.home = base / "home"
        (self.home / ".claude" / "sessions").mkdir(parents=True)
        self.env = dict(os.environ, HOME=str(self.home), GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
                        GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        self.box = base / "projekt"
        src = base / "src"
        self.git("init", "-q", "-b", "main", str(src))
        (src / "docs").mkdir()
        (src / "docs" / "todo.md").write_text(TODO)
        self.git("-C", str(src), "add", "-A")
        self.git("-C", str(src), "commit", "-q", "-m", "start")
        self.box.mkdir()
        self.git("clone", "-q", "--bare", str(src), str(self.box / ".bare"))
        self.bare = ["--git-dir", str(self.box / ".bare")]
        self.git(*self.bare, "worktree", "add", "-q", str(self.box / "main"), "main")
        # Kolo o DPH se rozhoduje ve větvi s worktree, fakturace má větev bez commitu.
        self.git(*self.bare, "worktree", "add", "-q", "-b", "specify-dph", str(self.box / "dph"), "main")
        dph = self.box / "dph" / "docs" / "todo.md"
        dph.write_text(TODO.replace("- **Stav:** čeká\n- **Větev:** `specify-dph`",
                                    "- **Stav:** rozhoduje se\n- **Větev:** `specify-dph`"))
        self.git("-C", str(self.box / "dph"), "commit", "-qam", "DPH rozhoduje se")
        self.git(*self.bare, "branch", "specify-faktury", "main")
        self.sleeper = subprocess.Popen(["sleep", "60"])

    def tearDown(self):
        self.sleeper.kill()
        self.sleeper.wait()
        self.tmp.cleanup()

    def git(self, *args):
        subprocess.run(["git", *args], check=True, env=getattr(self, "env", None), capture_output=True)

    def session(self, pid, sid, cwd, branch):
        claude = self.home / ".claude"
        (claude / "sessions" / f"{pid}.json").write_text(json.dumps(
            {"pid": pid, "sessionId": sid, "cwd": str(self.box), "name": sid}))
        adr = claude / "projects" / "-projekt"
        adr.mkdir(parents=True, exist_ok=True)
        (adr / f"{sid}.jsonl").write_text(
            json.dumps({"cwd": str(self.box)}) + "\n" + json.dumps({"cwd": cwd, "gitBranch": branch}) + "\n")

    def collect(self):
        run = subprocess.run([sys.executable, str(COLLECT), str(self.box)],
                             capture_output=True, text=True, env=self.env)
        self.assertEqual(run.returncode, 0, run.stderr)
        return json.loads(run.stdout)

    def branches(self):
        return {b["branch"]: b for b in self.collect()["branches"]}

    def mrtvy_pid(self):
        p = subprocess.Popen(["true"])
        p.wait()
        return p.pid

    def test_fronta_se_cte_z_hlavni_vetve_bez_hotovych(self):
        data = self.collect()
        [part] = data["todo"][0]["parts"]
        self.assertEqual([i["title"] for i in part["items"]], ["Export faktur"])
        self.assertEqual([r["Stav"] for r in data["rounds"]], ["čeká", "čeká"])

    def test_kolo_nese_stav_ze_sve_vetve(self):
        dph = self.collect()["rounds"][0]
        self.assertEqual(dph["branch_state"], "rozhoduje se")

    def test_opustena_vetev_se_session_k_obnoveni(self):
        self.session(self.mrtvy_pid(), "stara", str(self.box / "dph"), "specify-dph")
        b = self.branches()["specify-dph"]
        self.assertEqual((b["state"], b["resume"]["session_id"], b["resume"]["start_cwd"]),
                         ("abandoned", "stara", str(self.box)))
        self.assertEqual(b["rounds"], ["Kolo o DPH"])

    def test_obsazena_vetev_bez_commitu(self):
        # `--no-merged` větev bez commitu nevypíše; živá session nad ní ji musí přidat.
        self.session(self.sleeper.pid, "ziva", str(self.box / "faktury"), "specify-faktury")
        b = self.branches()["specify-faktury"]
        self.assertEqual((b["state"], b["session"]), ("occupied", "ziva"))

    def test_session_bez_vetve_zneisti_vsechny_vetve(self):
        (self.home / ".claude" / "sessions" / f"{self.sleeper.pid}.json").write_text(json.dumps(
            {"pid": self.sleeper.pid, "sessionId": "nova", "cwd": str(self.box)}))
        self.assertEqual({b["state"] for b in self.branches().values()}, {"uncertain"})


if __name__ == "__main__":
    unittest.main()
