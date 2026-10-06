#!/usr/bin/env python3
"""PreToolUse hook: zastaví Bash příkaz, který čte soubor s tajemstvím.

Deny pravidla `Read(//**/.env)` a spol. v `settings.json` hlídají jen nástroj
Read. Shell kolem nich projde bez povšimnutí – `. ./.env`, `grep KEY .env`,
`cat`, `cp` i `python3 -c "open('.env')"` –, a hodnota pak skončí v kontextu
a v transcriptu, kdykoliv ji příkaz nebo chybová hláška vypíše.

Seznam tajemství se **nečte z výčtu tady**, ale z těch deny pravidel: jsou
jediný zdroj pravdy, a co se do nich přidá, hlídá hook od té chvíle taky.

Zastaví se příkaz, jehož slovo se jménem shoduje se vzorem **a zároveň odkazuje
na existující soubor** – vůči `cwd`, cílům `cd` a adresářům předaným příkazu.
Bez té druhé podmínky by padal `grep '\\.env' worktree.md` nad dokumentací
i zpráva commitu, která `.env` jen zmiňuje; falešný poplach u hooku, který běží
před každým příkazem, znamená, že si ho někdo vypne. Tělo heredocu se proto čte
jen tehdy, když ho dostává interpret – jinak je to text, ne cesta.

Propouští se, co obsah nečte: `ls`, `stat`, `test` a git podpříkazy, které
soubor jen evidují. Co hook nevidí – proměnnou, glob, rekurzivní `grep -r` –,
eviduje `bypass.md`.

Vrací 2 a důvod na stderr, což je pro PreToolUse zastavení nástroje.
"""

import fnmatch
import json
import os
import re
import shlex
import sys
from pathlib import Path

BLOCK = 2
PASS = 0

SETTINGS = Path(__file__).resolve().parent.parent / "settings.json"
# Jediný program, který smí tajemství číst, protože z nich vypíše jen jména klíčů.
ENVKEYS = Path(__file__).resolve().parent / "envkeys.py"

SEPARATORS = {";", "&&", "||", "|", "&", "(", ")", "\n"}
PREFIXES = {"sudo", "command", "env", "time", "nohup", "exec"}
# Příkazy, které se souboru dotknou nebo ho jmenují, ale obsah nečtou.
NO_READ = {"ls", "stat", "test", "[", "[[", "echo", "printf"}
GIT_METADATA_ONLY = {"add", "rm", "mv", "status", "check-ignore", "ls-files"}
INTERPRETERS = {
    "python",
    "python3",
    "node",
    "ruby",
    "perl",
    "php",
    "sh",
    "bash",
    "zsh",
    "osascript",
}

HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1")
PATHLIKE = re.compile(r"[\w./~-]+")


def secret_patterns():
    """Vzory z `Read(//**/…)` v deny seznamu – jediný zdroj pravdy."""
    try:
        deny = json.loads(SETTINGS.read_text(encoding="utf-8"))["permissions"]["deny"]
    except (OSError, ValueError, KeyError, TypeError):
        return []
    out = []
    for rule in deny:
        m = re.fullmatch(r"Read\(//\*\*/(.+)\)", rule)
        if m:
            out.append(m.group(1))
    return out


def matches(word, patterns):
    """Odpovídá slovo některému vzoru? Vzor s lomítkem se bere jako konec cesty."""
    word = word.rstrip("/")
    name = os.path.basename(word)
    for p in patterns:
        if "/" in p:
            if fnmatch.fnmatch(word, "*/" + p) or fnmatch.fnmatch(word, p):
                return True
        elif name and fnmatch.fnmatch(name, p):
            return True
    return False


def split_heredocs(command):
    """Vrátí příkaz bez těl heredoců a seznam (příkaz, který tělo dostává, tělo)."""
    lines = command.split("\n")
    kept, bodies, i = [], [], 0
    while i < len(lines):
        line = lines[i]
        kept.append(line)
        i += 1
        for m in HEREDOC.finditer(line):
            owner = re.split(r"&&|\|\||[;|(]", line[: m.start()])[-1].split()
            body = []
            while i < len(lines) and lines[i].strip() != m.group(2):
                body.append(lines[i])
                i += 1
            i += 1
            bodies.append((owner[0] if owner else "", "\n".join(body)))
    return "\n".join(kept), bodies


def segments(words):
    part = []
    for w in words:
        if w in SEPARATORS or w.startswith(("&", "|", ";")):
            if part:
                yield part
            part = []
        else:
            part.append(w)
    if part:
        yield part


def strip_prefixes(part):
    while part and (part[0] in PREFIXES or re.fullmatch(r"\w+=.*", part[0])):
        part = part[1:]
    return part


def reads_content(part):
    """Čte tenhle úsek obsah souborů, nebo je jen eviduje?"""
    if not part or part[0] in NO_READ:
        return False
    if part[0] == "git":
        args = [a for a in part[1:] if not a.startswith("-")]
        return not (args and args[0] in GIT_METADATA_ONLY)
    return True


def runs_envkeys(part, cwd):
    """Spouští úsek `envkeys.py` z tohohle adresáře – a ne soubor stejného jména?"""
    if part and os.path.basename(part[0]) in INTERPRETERS:
        part = part[1:]
    if not part:
        return False
    script = Path(cwd) / os.path.expanduser(part[0])
    try:
        return script.resolve() == ENVKEYS
    except OSError:
        return False


def candidates(part):
    """Slova úseku, která můžou být cestou; u interpretu i kusy jeho kódu."""
    out = list(part)
    if os.path.basename(part[0]) in INTERPRETERS:
        for w in part[1:]:
            out += PATHLIKE.findall(w)
    return out


def bases(cwd, words):
    """Adresáře, vůči kterým se relativní cesta může vyhodnotit."""
    out = [Path(cwd)]
    for w in words:
        p = Path(os.path.expanduser(w))
        if not p.is_absolute():
            p = Path(cwd) / p
        if w not in SEPARATORS and p.is_dir():
            out.append(p)
    return out


def existing(word, dirs):
    p = Path(os.path.expanduser(word))
    if p.is_absolute():
        return p.is_file()
    return any((d / p).is_file() for d in dirs)


def offending(command, cwd, patterns):
    """Vrátí slovo, které čte existující tajemství, nebo None."""
    text, bodies = split_heredocs(command)
    try:
        lexer = shlex.shlex(text, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        words = list(lexer)
    except ValueError:
        words = text.split()
    dirs = bases(cwd, words)
    found = []
    for part in segments(words):
        part = strip_prefixes(part)
        if reads_content(part) and not runs_envkeys(part, cwd):
            found += [w for w in candidates(part) if matches(w, patterns)]
    for owner, body in bodies:
        if os.path.basename(owner) in INTERPRETERS:
            found += [w for w in PATHLIKE.findall(body) if matches(w, patterns)]
    return next((w for w in found if existing(w, dirs)), None)


def main():
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return PASS
    if event.get("tool_name") != "Bash":
        return PASS
    command = (event.get("tool_input") or {}).get("command") or ""
    word = offending(command, event.get("cwd") or os.getcwd(), secret_patterns())
    if not word:
        return PASS
    sys.stderr.write(
        f"Zastaveno hookem `secret-guard.py`: příkaz čte `{word}`, který je na seznamu "
        "tajemství (deny `Read(...)` v settings.json). Hodnota by se mohla dostat do "
        "kontextu a transcriptu – i chybovou hláškou. Potřebuje-li úkol tajemství použít, "
        "napiš uživateli celý příkaz a nech ho spustit přes `!`. Stačí-li vědět, "
        f"jaké klíče v souboru jsou a jestli jsou vyplněné: `python3 {ENVKEYS} {word}`.\n"
    )
    return BLOCK


if __name__ == "__main__":
    sys.exit(main())
