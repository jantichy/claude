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

    def test_chybejici_registr_neni_prazdny_seznam(self):
        (self.claude / "sessions").rmdir()
        run = self.spust()
        self.assertEqual(run.returncode, 2)
        self.assertEqual(run.stdout, "")


if __name__ == "__main__":
    unittest.main()
