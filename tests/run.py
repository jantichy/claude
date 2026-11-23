"""Pustí testovací moduly souběžně, každý ve vlastním procesu.

Sada za sebou trvá přes strop průběžné kontroly (90 s na příkaz), takže by
kontrola v tomhle repozitáři nedoběhla nikdy. Moduly si staví vlastní dočasné
adresáře a přesměrovaný HOME, takže souběh nemění, co měří.

Každý modul se pouští přes `discover -p`, ne jako `tests.<modul>`: importy pak
platí stejně jako u `python3 -m unittest discover -s tests`, které jde dál pustit
ručně. Výstup se vypisuje jen u modulu, který neprošel.

Spouští se: python3 tests/run.py
"""

import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(module):
    r = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", module],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return module, r.returncode, r.stdout + r.stderr


def main():
    modules = sorted(p.name for p in (ROOT / "tests").glob("test_*.py"))
    if not modules:
        print("V tests/ není žádný test_*.py – nespustil jsem nic.")
        return 1
    with ThreadPoolExecutor(max_workers=min(8, os.cpu_count() or 4)) as pool:
        results = list(pool.map(run, modules))
    failed = [r for r in results if r[1] != 0]
    for module, code, output in failed:
        print(f"--- {module} (exit {code}) ---\n{output}")
    total = sum(
        int(m.group(1))
        for _, _, output in results
        for m in re.finditer(r"^Ran (\d+) tests?", output, re.M)
    )
    print(f"Testů: {total}, modulů: {len(modules)}, neprošlo modulů: {len(failed)}.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
