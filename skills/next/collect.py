#!/usr/bin/env python3
"""Posbírá pro `/next` všechno, co jde o frontě práce zjistit mechanicky – jedním během.

Dřív to skill dělal přes desítky volání gitu a čtení souborů, každé s čekáním na model,
a k tomu si pokaždé načítal `STRUCTURE.md` a `LIFECYCLE.md`, aby věděl, jak soubory
vypadají. Běh trval přes minutu. Tenhle skript z toho nechává modelu jen úsudek:
popis, velikost a co je na stole nejvíc. Rozhodnutí o obsazenosti větve je tady,
v testovaném kódu, ne v úvaze modelu.

Použití: `collect.py [adresář]` – výchozí je aktuální adresář; smí to být kořen
worktree kontejneru, jeho pracovní adresář i běžný repozitář.

Výstup: jeden řádek JSON na stdout. Klíče:

- `layout` – `worktree` nebo `plain`; `main` – hlavní větev; `fetch` – výsledek `git fetch`
- `docs` – `docs/`, `root`, nebo null, když projekt `todo.md` nemá
- `current` – větev a necommitnuté soubory tam, kde session stojí (null v kořeni kontejneru)
- `todo` – sekce `todo.md`, v každé položky (`title`, `text` zkrácený, `done`)
- `rounds` – bloky kol návrhu s poli a stavem ve větvi kola; `stitch_pending` – čeká sešití
- `plan` – počet otevřených a hotových úkolů a první otevřené; `artifacts` – které návrhové dokumenty existují
- `passes` – posledních pět záznamů `## Průchody životním cyklem`; `lifecycle` – rámeček cyklu z `RULES.md`
- `branches` – nesloučené větve a větve živých session: `state` (`occupied`, `abandoned`,
  `uncertain`, `empty`), session, commity, změny `todo.md`/`plan.md`/`done.md` a přiřazená kola
- `sessions_error` – proč se živé session nedaly zjistit (pak jsou všechny větve `uncertain`)
- `backlog` – názvy nápadů, jen když je fronta prázdná

Pravidla, podle kterých se tu rozhoduje, drží `SKILL.md`; tenhle docstring jen popisuje výstup.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

# `sessions.py` leží vedle; Python adresář spuštěného skriptu do cest přidává sám.
import sessions

TEXT_LIMIT = 300
DIFF_LINES = 12
RULES = Path.home() / ".claude" / "RULES.md"


class Repo:
    """Volání gitu nad kontejnerem (přes `.bare`) i nad běžným repozitářem."""

    def __init__(self, start: Path):
        start = start.resolve()
        self.worktree = None
        # Kontejner se hledá mezi všemi předky, ne jen o úroveň výš: session stojí
        # klidně v `main/docs/` a jako běžný repozitář by pak minula ostatní worktree.
        container = next((p for p in [start, *start.parents] if (p / ".bare").is_dir()), None)
        if container is not None:
            self.root, self.layout = container, "worktree"
            if start != container:
                self.worktree = container / start.relative_to(container).parts[0]
        else:
            top = run(["git", "-C", str(start), "rev-parse", "--show-toplevel"])
            if top is None:
                raise SystemExit(f"{start} není git repozitář")
            self.root, self.layout, self.worktree = Path(top), "plain", Path(top)
        self.base = (["git", "--git-dir", str(self.root / ".bare")] if self.layout == "worktree"
                     else ["git", "-C", str(self.root)])

    def git(self, *args):
        return run(self.base + list(args))


def run(cmd, timeout=20):
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except (subprocess.TimeoutExpired, OSError):
        return None
    return res.stdout.strip() if res.returncode == 0 else None


def main_branch(repo: Repo):
    if repo.git("remote", "get-url", "origin") is not None:
        head = repo.git("symbolic-ref", "--short", "refs/remotes/origin/HEAD")
        if head:
            return head, True
        if repo.git("rev-parse", "--verify", "--quiet", "origin/main") is not None:
            return "origin/main", True
    for name in ("main", "master"):
        if repo.git("rev-parse", "--verify", "--quiet", name) is not None:
            return name, False
    return None, False


def reader(repo: Repo, ref):
    """Vrátí funkci, která čte soubor projektu: ve worktree layoutu z hlavní větve."""
    if repo.layout == "worktree":
        return lambda path, r=ref: repo.git("show", f"{r}:{path}")

    def from_tree(path):
        f = repo.root / path
        return f.read_text(encoding="utf-8") if f.is_file() else None
    return from_tree


def docs_prefix(read):
    if read("docs/todo.md") is not None:
        return "docs/"
    if read("todo.md") is not None:
        return ""
    return None


def short(text):
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= TEXT_LIMIT else text[:TEXT_LIMIT - 1] + "…"


def item_title(first_line):
    """Tučný začátek položky, jinak její začátek; vrací (název, zbytek textu)."""
    m = re.match(r"\*\*(.+?)\*\*\s*", first_line)
    if m:
        return m.group(1).rstrip("."), first_line[m.end():]
    return short(first_line)[:120], first_line


def parse_items(lines):
    """Položky na nejvyšší úrovni seznamu (`- `, `- [ ]`, `1.`) i s pokračováním."""
    items, cur = [], None
    for line in lines:
        m = re.match(r"(?:[-*]|\d+\.) (?:\[( |x|X)\] )?(.*)", line)
        if m:
            cur = {"done": (m.group(1) or " ").lower() == "x", "first": m.group(2), "rest": []}
            items.append(cur)
        elif cur is not None and line.startswith((" ", "\t")):
            cur["rest"].append(line)
    out = []
    for i in items:
        title, rest = item_title(i["first"])
        full = " ".join([rest] + i["rest"])
        entry = {"title": title, "text": short(full), "done": i["done"]}
        # Závislost bývá na konci dlouhého popisu, který `short` ořízne – vytáhne se zvlášť.
        waits = WAITS.search(full)
        if waits:
            entry["waits"] = short(waits.group(1))
        out.append(entry)
    return out


WAITS = re.compile(r"\b[Čč]ek(?:á|ají)\s+na\b[:\s]*\**\s*([^.;\n]{3,160})")
CHECKBOX = re.compile(r"\s*[-*] \[( |x|X)\]")


def sections(text, level="## "):
    """Rozdělí Markdown na sekce dané úrovně: [(nadpis, řádky)]."""
    out, title, buf = [], None, []
    for line in text.splitlines():
        if line.startswith(level):
            out.append((title, buf))
            title, buf = line[len(level):].strip(), []
        else:
            buf.append(line)
    out.append((title, buf))
    return [(t, b) for t, b in out if t is not None]


# Pole bloku kola: popisek v Markdownu je česky, klíč ve výstupu anglicky.
FIELD_KEYS = {"Stav": "status", "Větev": "branch", "Dokument": "document", "Čeká na": "waits", "Sahá na": "touches"}
FIELD = re.compile(r"- \*\*(Stav|Větev|Dokument|Čeká na|Sahá na):\*\*\s*(.*)")


def parse_rounds(lines):
    rounds = []
    for title, body in sections("\n".join(lines), "### "):
        fields = {}
        for line in body:
            m = FIELD.match(line)
            if m:
                fields[FIELD_KEYS[m.group(1)]] = m.group(2).strip().strip("`")
        rounds.append({"title": title, **fields})
    return rounds


def parse_todo(text):
    out, rounds, stitched = [], [], False
    for title, body in sections(text):
        if title == "Kola návrhu":
            rounds = parse_rounds(body)
            stitched = any("Návrh sešitý" in line for line in body)
            continue
        subs = [(None, body)] + sections("\n".join(body), "### ")
        head = body[:next((i for i, x in enumerate(body) if x.startswith("### ")), len(body))]
        entries = [{"subsection": None, "items": [i for i in parse_items(head) if not i["done"]]}]
        entries += [{"subsection": t, "items": [i for i in parse_items(b) if not i["done"]]}
                    for t, b in subs[1:]]
        out.append({"section": title, "parts": [e for e in entries if e["items"]]})
    return out, rounds, stitched


def parse_done(text):
    passes, rounds_done, closed_after = [], False, True
    for title, body in sections(text or ""):
        if title == "Průchody životním cyklem":
            # Projekty řadí záznamy různě (nejnovější nahoře i dole) – rozhoduje datum.
            entries = [x for x in body if x.startswith("- ")]
            passes = [short(x) for x in sorted(entries, key=lambda x: re.findall(r"\d{4}-\d{2}-\d{2}", x)[:1])][-5:]
        if title == "Kola návrhu":
            for line in body:
                if line.startswith("- **Kolo o"):
                    rounds_done, closed_after = True, False
                elif line.startswith("- **Návrh uzavřen"):
                    closed_after = True
    return passes, rounds_done and not closed_after


def parse_plan(text):
    """Úkoly plánu: nadpis se zaškrtávacími kroky pod sebou, jinak samotná zaškrtávátka.

    Obyčejné odrážky (kritéria, poznámky) se nepočítají – plán s jedinou takovou
    by jinak nebyl nikdy hotový a skill by nikdy nedošel k `/review`.
    """
    if text is None:
        return None
    tasks, title, boxes = [], None, []
    for line in text.splitlines() + ["## "]:
        heading = re.match(r"#{2,4} (.*)", line)
        if heading:
            if title and boxes:
                tasks.append((title, all(boxes)))
            title, boxes = heading.group(1).strip(), []
        else:
            m = CHECKBOX.match(line)
            if m:
                boxes.append(m.group(1).lower() == "x")
    if not tasks:
        tasks = [(line.strip(), m.group(1).lower() == "x")
                 for line in text.splitlines() if (m := CHECKBOX.match(line))]
    open_ = [short(name)[:120] for name, done in tasks if not done]
    return {"open": len(open_), "done": len(tasks) - len(open_), "next": open_[:3]}


def lifecycle():
    text = RULES.read_text(encoding="utf-8") if RULES.is_file() else ""
    m = re.search(r"### Životní cyklus projektu.*?```\n(.*?)```", text, re.S)
    return [x.strip() for x in m.group(1).splitlines()] if m else []


def worktrees(repo: Repo):
    out, path = {}, None
    for line in (repo.git("worktree", "list", "--porcelain") or "").splitlines():
        if line.startswith("worktree "):
            path = line[9:]
        elif line.startswith("branch refs/heads/"):
            out[line[18:]] = path
    return out


def branch_diff(repo: Repo, ref, branch, prefix):
    paths = [f"{prefix}{n}" for n in ("todo.md", "plan.md", "done.md")]
    diff = repo.git("diff", f"{ref}...{branch}", "--", *paths) or ""
    changed = [short(x) for x in diff.splitlines()
               if x[:1] in "+-" and not x.startswith(("+++", "---")) and x[1:].strip()]
    return {"changes": changed[:DIFF_LINES], "changes_total": len(changed),
            "adds_stitch": any(x.startswith("+") and ("Návrh sešitý" in x or "Návrh uzavřen" in x)
                               for x in changed)}


def live_state(project: Path):
    try:
        if not (sessions.Path.home() / ".claude" / "sessions").is_dir():
            return [], [], "registr session neexistuje"
        home = Path.home() / ".claude"
        live = sessions.live_sessions(home)
        for s in live:
            s["in_project"] = sessions.inside(s["start_cwd"], project) or sessions.inside(s["cwd"], project)
        idle = sessions.idle_sessions(home, project, {s["session_id"] for s in live if s["session_id"]})
    except (sessions.Unreadable, OSError) as err:
        # Transcript, který zmizel mezi výpisem a čtením, nesmí shodit celý běh –
        # platí totéž co pro nečitelný registr: nejisté, tedy obsazené.
        return [], [], str(err)
    return live, idle, None


def branch_state(branch, others, idle, error, work):
    busy = [s for s in others if s["branch"] == branch]
    if busy:
        return {"state": "occupied", "session": busy[0]["name"]}
    if error or any(s["branch"] is None for s in others):
        why = error or "živá session nad projektem nemá zjistitelnou větev (čerstvě otevřené okno?)"
        return {"state": "uncertain", "why": why}
    if not work:
        # Sloučená nebo nezačatá větev bez neuložených změn není zapomenutá práce.
        return {"state": "empty"}
    match = next((s for s in idle if s["branch"] == branch), None)
    return {"state": "abandoned", "resume": match and {k: match[k] for k in ("session_id", "start_cwd", "updated")}}


def collect_branches(repo, ref, prefix, rounds, current_branch, project):
    local = ref.split("/", 1)[1] if ref.startswith("origin/") else ref
    live, idle, error = live_state(project)
    others = [s for s in live if s.get("in_project") and not s["self"]]
    trees = worktrees(repo)
    names = set((repo.git("branch", "--no-merged", ref, "--format=%(refname:short)") or "").split())
    names |= set(trees) | {s["branch"] for s in others if s["branch"]}
    if current_branch:
        names.add(current_branch)
    names -= {"HEAD"}
    out = []
    for b in sorted(names):
        if repo.git("rev-parse", "--verify", "--quiet", b) is None:
            continue
        info = branch_info(repo, ref, b, trees.get(b), prefix)
        info.update(current=b == current_branch, main=b in (local, "main", "master"),
                    rounds=[r["title"] for r in rounds if r.get("branch") == b])
        work = info["ahead"] or info["uncommitted"]
        info.update(branch_state(b, others, idle, error, work))
        # Hlavní větev se vypisuje jen tehdy, když v ní někdo pracuje nebo něco leží.
        if info["main"] and info["state"] in ("empty", "abandoned") and not info["uncommitted"]:
            continue
        out.append(info)
    return out, error


def branch_info(repo, ref, b, tree, prefix):
    status = (run(["git", "-C", tree, "status", "--porcelain"]) or "").splitlines() if tree else []
    info = {"branch": b, "worktree": tree, "uncommitted": len(status),
            "ahead": int(repo.git("rev-list", "--count", f"{ref}..{b}") or 0),
            "commits": (repo.git("log", "--format=%s", "-3", f"{ref}..{b}") or "").splitlines(),
            "last": repo.git("log", "-1", "--format=%cr", b),
            "last_ts": int(repo.git("log", "-1", "--format=%ct", b) or 0)}
    info.update(branch_diff(repo, ref, b, prefix))
    return info


def round_states(repo, rounds, prefix):
    for r in rounds:
        b = r.get("branch")
        if not b or repo.git("rev-parse", "--verify", "--quiet", b) is None:
            continue
        text = repo.git("show", f"{b}:{prefix}todo.md") or ""
        block = next((body for t, body in sections(text, "### ") if t == r["title"]), None)
        if block is None:
            r["branch_state"] = "zapsáno ve větvi, čeká na sloučení"
        else:
            m = next((FIELD.match(x) for x in block if FIELD.match(x) and "Stav" in x), None)
            r["branch_state"] = m.group(2).strip() if m else None


def current_info(repo: Repo):
    if repo.worktree is None:
        return None
    branch = run(["git", "-C", str(repo.worktree), "branch", "--show-current"])
    status = (run(["git", "-C", str(repo.worktree), "status", "--porcelain"]) or "").splitlines()
    return {"branch": branch, "uncommitted": status[:15], "uncommitted_total": len(status)}


def main() -> int:
    repo = Repo(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
    fetch = None
    if repo.git("remote", "get-url", "origin") is not None:
        fetch = "ok" if run(repo.base + ["fetch", "--quiet"], timeout=15) is not None else "failed"
    ref, _ = main_branch(repo)
    if ref is None:
        raise SystemExit("hlavní větev se nepodařilo určit")
    read = reader(repo, ref)
    prefix = docs_prefix(read)
    base = prefix or ""
    todo, rounds, stitched = parse_todo(read(f"{base}todo.md") or "")
    passes, rounds_open = parse_done(read(f"{base}done.md"))
    plan = parse_plan(read(f"{base}plan.md"))
    current = current_info(repo)
    round_states(repo, rounds, base)
    branches, error = collect_branches(repo, ref, base, rounds, current and current["branch"], repo.root)
    queue_empty = not any(p["items"] for s in todo for p in s["parts"]) and not rounds \
        and not (plan and plan["open"])
    result = {
        "root": str(repo.root), "layout": repo.layout, "main": ref, "fetch": fetch,
        "docs": None if prefix is None else (prefix or "root"),
        "current": current, "todo": todo, "rounds": rounds,
        "stitch_pending": (rounds_open or stitched) and not rounds,
        "plan": plan, "passes": passes, "lifecycle": lifecycle(),
        "artifacts": {n: read(f"{base}{n}.md") is not None for n in ("requirements", "architecture", "plan")},
        "branches": branches, "sessions_error": error,
        "backlog": ([i["title"] for i in parse_items((read(f"{base}backlog.md") or "").splitlines())]
                    if queue_empty else None),
    }
    json.dump(result, sys.stdout, ensure_ascii=False, separators=(",", ":"))
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
