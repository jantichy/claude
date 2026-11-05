#!/usr/bin/env python3
"""Kopie projektu pro ověřovatele `/review` – bez zápisů o předchozích nálezech.

Ověřovatel má nález posoudit z kódu, ne podle toho, jak ho kdo hodnotil dřív.
Sekce `## Přerušený běh`, `## Rozhodnuto k zapracování` a `## Otázky dalšího
kola` v `todo.md` a běhová fronta v `.claude/run/` přitom nesou právě starší nálezy i s verdikty, a zákaz
číst je v zadání nedrží. Kopie bez nich je hranice, kterou ověřovatel obejít
nemůže, protože o originálu neví.

Kopíruje se jen to, co patří do rozsahu: soubory pod gitem a nové neignorované,
v tom stavu, v jakém leží v pracovním stromu. Adresáře se závislostmi se jen
nalinkují – kopírovat je by stálo řádově víc a bez nich by nešlo přehrát `cmd`
z nálezu.

Použití: snapshot.py <kořen projektu> <cílový adresář>
Cílový adresář nesmí existovat. Na stdout vypíše jeho cestu.
Návratový kód: 0 hotovo, 2 chyba volání.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

#: Sekce se staršími nálezy a jejich vypořádáním.
HIDDEN_SECTIONS = (
    "## Přerušený běh",
    "## Rozhodnuto k zapracování",
    "## Otázky dalšího kola",
)
#: Soubory, ve kterých ty sekce stojí – `todo.md` podle režimu umístění,
#: `CLAUDE.md` u operativního projektu.
HIDDEN_IN = ("todo.md", "CLAUDE.md")
#: Běhový stav skillů, mezi nímž je `review.json` s frontou nálezů.
RUN_DIR = Path(".claude") / "run"
#: Ignorované adresáře se závislostmi, bez kterých nejde nic spustit.
DEPENDENCIES = (".venv", "venv", "node_modules", "vendor")


def files(root):
    """Soubory pod gitem a nové neignorované, relativně ke kořeni."""
    out = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-co", "--exclude-standard", "-z"],
        capture_output=True,
        check=True,
    ).stdout
    return [Path(p.decode()) for p in out.split(b"\0") if p]


def strip_sections(text):
    """Vypustí skryté sekce od nadpisu po další nadpis první nebo druhé úrovně.

    Bloky `###` uvnitř sekce k ní patří, takže řez končí až nadpisem `#` nebo
    `##`. Nadpis v bloku kódu hranicí není.
    """
    kept, hiding, fence = [], False, None
    for line in text.splitlines(keepends=True):
        stripped = line.lstrip()
        marker = stripped[:3]
        if marker in ("```", "~~~"):
            fence = None if fence == marker else (fence or marker)
        elif fence is None and stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            if level <= 2:
                hiding = line.rstrip().startswith(HIDDEN_SECTIONS)
        if not hiding:
            kept.append(line)
    return "".join(kept)


def snapshot(root, dest):
    root, dest = Path(root).resolve(), Path(dest)
    dest.mkdir(parents=True)
    for rel in files(root):
        source = root / rel
        if rel.parts[:2] == RUN_DIR.parts or not source.is_file():
            continue
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if rel.name in HIDDEN_IN:
            text = source.read_text(encoding="utf-8", errors="replace")
            target.write_text(strip_sections(text), encoding="utf-8")
        else:
            shutil.copy2(source, target)
    for name in DEPENDENCIES:
        if (root / name).is_dir() and not (dest / name).exists():
            os.symlink(root / name, dest / name)
    return dest


def main(argv):
    if len(argv) != 3:
        print("Použití: snapshot.py <kořen projektu> <cílový adresář>", file=sys.stderr)
        return 2
    try:
        print(snapshot(argv[1], argv[2]))
    except (FileExistsError, subprocess.CalledProcessError) as error:
        print(f"snapshot.py: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
