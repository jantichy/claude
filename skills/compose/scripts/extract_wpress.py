"""Rozbalí soubory z All-in-One WP Migration .wpress archivu.

Formát: opakující se bloky [header 4377 B][obsah souboru].
Header: 255 B jméno, 14 B velikost, 12 B mtime, 4096 B cesta (vše \x00-padded).
Konec: 4377 B samých \x00.
"""
import sys
from pathlib import Path

HEADER = 4377

if len(sys.argv) < 3:
    sys.exit("Použití: extract_wpress.py <archiv .wpress> <výstupní adresář> [filtr]")
src = Path(sys.argv[1])
out_dir = Path(sys.argv[2])
want = sys.argv[3] if len(sys.argv) > 3 else None  # jen soubory obsahující tento řetězec

with src.open("rb") as f:
    while True:
        header = f.read(HEADER)
        if len(header) < HEADER or header == b"\x00" * HEADER:
            break
        name = header[:255].split(b"\x00")[0].decode("utf-8", "replace")
        size = int(header[255:269].split(b"\x00")[0] or 0)
        path = header[281:].split(b"\x00")[0].decode("utf-8", "replace")
        full = f"{path}/{name}" if path and path != "." else name
        if want and want not in full:
            f.seek(size, 1)
            continue
        # Cesta pochází z archivu, tedy z dat – ne z argumentu. Bez téhle
        # kontroly si archiv určí, kam se zapisuje: `../../..` vyleze
        # z výstupního adresáře a absolutní cesta ho zahodí úplně, protože
        # `Path("/a") / "/etc/x"` je `/etc/x`. Cílem bývá vlastní záloha, ale
        # ta se často tahá ze starého hostingu, kde ji nikdo nehlídal.
        target = (out_dir / full).resolve()
        if not target.is_relative_to(out_dir.resolve()):
            sys.exit(f"archiv chce zapsat mimo výstupní adresář: {full!r}")
        target.parent.mkdir(parents=True, exist_ok=True)
        remaining = size
        with target.open("wb") as o:
            while remaining > 0:
                chunk = f.read(min(1 << 20, remaining))
                if not chunk:
                    break
                o.write(chunk)
                remaining -= len(chunk)
        print(f"{size:>12}  {full}")
