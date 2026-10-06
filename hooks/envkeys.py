#!/usr/bin/env python3
"""Vypíše jména klíčů v souboru s tajemstvím a jejich stav – nikdy hodnotu.

`secret-guard.py` zastaví každý shellový příkaz, který čte `.env` a spol., a
správně: hodnota by skončila v kontextu a v transcriptu. Model ale často
potřebuje vědět jen to, **jaké klíče v souboru jsou a jestli jsou vyplněné** –
když ladí, proč aplikace nevidí konfiguraci, nebo chystá `.env.example`. Bez
povolené cesty stojí před zdí a zkouší ji obejít. Tenhle skript je ta cesta a
hook ho pouští – jen tenhle soubor, ne cokoliv stejného jména.

Hodnotu čte jen proto, aby určil stav, a nevypíše z ní nic: ani délku, ani
začátek, ani řádek, který se nepodařilo rozebrat (ten se hlásí jen číslem).

Stavy:
  prázdný    klíč bez hodnoty (`KEY=`, `KEY=""`)
  zástupný   hodnota, která tajemstvím zjevně není (`changeme`, `<token>`, `xxx`)
  vyplněný   cokoliv jiného

Použití: python3 ~/.claude/hooks/envkeys.py <soubor> [<soubor> …]
Návratový kód: 0 vypsáno, 2 chyba volání (soubor chybí nebo nejde přečíst).
"""

import re
import sys

LINE = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_.]*)\s*=\s*(.*)$")
PLACEHOLDER = re.compile(
    r"^(?:<.*>|\$\{.*\}|x{3,}|\*{3,}|\.{3,}|todo|tbd|changeme|change_me|"
    r"replace_?me|placeholder|example|dummy|secret|password|your[_-].*|.*[_-]here)$",
    re.IGNORECASE,
)


def unquote(raw):
    """Hodnota bez uvozovek a bez komentáře za ní."""
    raw = raw.strip()
    if raw[:1] in ("'", '"'):
        end = raw.find(raw[0], 1)
        return raw[1:end] if end > 0 else raw[1:]
    return re.split(r"\s+#", raw, maxsplit=1)[0].strip()


def state(raw):
    value = unquote(raw)
    if not value:
        return "prázdný"
    if PLACEHOLDER.match(value):
        return "zástupný"
    return "vyplněný"


def describe(text):
    """Řádky výstupu pro obsah jednoho souboru."""
    out = []
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = LINE.match(line)
        if m:
            out.append(f"{m.group(1)}\t{state(m.group(2))}")
        else:
            out.append(f"# řádek {number}: není ve tvaru KLÍČ=hodnota, vynechán")
    return out


def main(paths):
    if not paths:
        sys.stderr.write("Použití: envkeys.py <soubor> [<soubor> …]\n")
        return 2
    code = 0
    for path in paths:
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                text = f.read()
        except OSError as e:
            sys.stderr.write(f"{path}: nejde přečíst ({e.strerror})\n")
            code = 2
            continue
        if len(paths) > 1:
            print(f"== {path}")
        print("\n".join(describe(text)) or "# žádný klíč")
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
