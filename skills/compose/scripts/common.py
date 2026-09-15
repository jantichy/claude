"""Pomocné funkce sdílené generátory archivu.

Leží vedle generátorů, takže si je naimportují bez ohledu na to, odkud se
spouštějí – `sys.path[0]` je vždycky adresář spouštěného skriptu.
"""


def plural(n, one, few, many):
    """České skloňování podle počtu: 1 / 2–4 / 0 a 5 a víc."""
    if n == 1:
        return f"{n} {one}"
    if 2 <= n <= 4:
        return f"{n} {few}"
    return f"{n} {many}"
