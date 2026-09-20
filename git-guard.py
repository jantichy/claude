#!/usr/bin/env python3
"""PreToolUse hook: zastaví git příkaz, který nevratně přepisuje historii.

Deny seznam v `settings.json` porovnává **prefix celého příkazu**, takže
`git push --force` zachytí, ale `git push origin main --force` ne – a přitom
je to tvar, který člověk napíše častěji. Týž problém mají aliasy: `git cc`
deny seznam nevidí, protože v něm není řetězec `push`.

Tenhle hook proto čte **celý příkaz**, rozloží ho na slova, přeskočí globální
přepínače (`-C <cesta>`, `-c k=v`) a teprve pak se ptá, co se volá a s čím.
Alias rozbalí z konfigurace gitu, takže nový alias nepotřebuje zápis nikam.

Oba směry selhání jsou nebezpečné a testuje je `tests/test_hooks.py`:
propuštěné přepsání historie znamená ztracenou práci cizí session, kdežto
falešný poplach nad běžným příkazem znamená, že si hook někdo vypne – a pak
nehlídá nic. Proto se přepínač poznává jako **celé slovo** a ne podřetězec:
`git log --grep=force` ani commit se slovem „--force“ ve zprávě nesmí spadnout.

Vrací 2 a důvod na stderr, což je pro PreToolUse zastavení nástroje.
"""
import json
import re
import shlex
import subprocess
import sys

BLOCK = 2
PASS = 0

SEPARATORS = {";", "&&", "||", "|", "&", "\n"}

# podpříkaz → (přepínače, které zastavují, věta pro člověka)
FORBIDDEN = {
    "push": ({"--force", "-f", "--force-with-lease", "--force-if-includes"},
             "přepsal by vzdálenou historii, na které může stát jiná session"),
    "reset": ({"--hard"},
              "zahodil by necommitnuté změny, včetně cizích"),
    "filter-branch": (None,
                      "přepisuje celou historii větve"),
    "clean": ({"-f", "--force", "-fd", "-fdx", "-xdf", "-df"},
              "smaže netrackované soubory, které nikde jinde nejsou"),
}

# podpříkaz + první argument → věta
FORBIDDEN_PAIRS = {
    ("branch", "-D"): "smaže větev bez ohledu na to, jestli je přimergovaná",
    ("update-ref", "-d"): "smaže referenci, a tím i poslední cestu k commitům",
    ("update-ref", "--delete"): "smaže referenci, a tím i poslední cestu k commitům",
    ("reflog", "expire"): "zahodí reflog, tedy záchrannou síť pro obnovu commitů",
    ("stash", "clear"): "smaže celý zásobník, který je sdílený mezi worktree",
    ("stash", "drop"): "smaže položku zásobníku, kterou mohla odložit jiná session",
}

GLOBAL_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}


def segments(words):
    """Rozdělí příkaz na části oddělené operátory shellu."""
    out, cur = [], []
    for w in words:
        if w in SEPARATORS:
            if cur:
                out.append(cur)
            cur = []
        else:
            cur.append(w)
    if cur:
        out.append(cur)
    return out


def strip_global(words):
    """Odstraní globální přepínače gitu a vrátí zbytek od podpříkazu dál."""
    i = 0
    while i < len(words):
        w = words[i]
        if w in GLOBAL_WITH_VALUE:
            i += 2
        elif w.startswith("-"):
            i += 1
        else:
            return words[i:]
    return []


def expand_alias(name):
    done = subprocess.run(["git", "config", "--get", f"alias.{name}"],
                          capture_output=True, text=True, check=False)
    if done.returncode != 0:
        return None
    value = done.stdout.strip()
    if not value or value.startswith("!"):
        # Shellový alias rozebírat neumíme; radši ho zastavíme, než pustíme naslepo.
        return ["opaque.alias"] if value else None
    try:
        return shlex.split(value)
    except ValueError:
        return None


def verdict(words, depth=0):
    """Vrátí důvod zastavení, nebo None."""
    rest = strip_global(words)
    if not rest:
        return None
    sub, args = rest[0], rest[1:]

    if sub == "opaque.alias":
        return "je to shellový alias, u kterého nejde poznat, co spustí"

    if depth < 3:
        expanded = expand_alias(sub)
        if expanded is not None:
            return verdict(expanded + args, depth + 1)

    if sub in FORBIDDEN:
        flags, reason = FORBIDDEN[sub]
        if flags is None:
            return reason
        if flags & set(args):
            return reason
        if sub == "push" and any(len(a) > 1 and a.startswith("+") for a in args):
            return "refspec s `+` přepíše vzdálenou větev stejně jako `--force`"

    for (s, a), reason in FORBIDDEN_PAIRS.items():
        if sub == s and a in args:
            return reason

    if sub == "branch" and {"--delete", "-d"} & set(args) and {"--force", "-f"} & set(args):
        return "smaže větev bez ohledu na to, jestli je přimergovaná"
    if sub == "worktree" and "remove" in args and {"--force", "-f"} & set(args):
        return "smaže worktree i s neuloženým obsahem"
    if sub == "gc" and any(a == "--prune" or a.startswith("--prune=") for a in args):
        return "nenávratně zahodí commity, na které nevede reference"

    return None


def main():
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return PASS
    if event.get("tool_name") != "Bash":
        return PASS
    command = (event.get("tool_input") or {}).get("command") or ""
    if not re.search(r"\bgit\b", command):
        return PASS
    try:
        words = shlex.split(command, comments=True)
    except ValueError:
        return PASS

    for part in segments(words):
        while part and part[0] in {"sudo", "command", "env", "time", "nohup"}:
            part = part[1:]
        if not part or part[0] != "git":
            continue
        reason = verdict(part[1:])
        if reason:
            sys.stderr.write(
                f"Zastaveno hookem `git-guard.py`: {reason}.\n"
                "Deny seznam v settings.json tenhle tvar nezachytí, protože porovnává prefix "
                "celého příkazu. Potřebuje-li to situace opravdu, musí to spustit člověk "
                "z terminálu.\n")
            return BLOCK
    return PASS


if __name__ == "__main__":
    sys.exit(main())
