#!/usr/bin/env python3
"""Posbírá pro `/next` všechno, co jde o nabídce práce zjistit mechanicky – jedním během.

Dřív to skill dělal přes desítky volání gitu a čtení souborů, každé s čekáním na model,
a k tomu si pokaždé načítal `structure.md` a `lifecycle.md`, aby věděl, jak soubory
vypadají. Běh trval přes minutu. Tenhle skript z toho nechává modelu jen úsudek:
popis, velikost a co je na stole nejvíc. Rozhodnutí o obsazenosti větve je tady,
v testovaném kódu, ne v úvaze modelu.

Použití: `collect.py [adresář]` – výchozí je aktuální adresář; smí to být kořen
worktree kontejneru, jeho pracovní adresář i běžný repozitář.

Výstup: jeden řádek JSON na stdout. Klíče:

- `layout` – `worktree` nebo `plain`; `main` – hlavní větev; `fetch` – výsledek `git fetch`
- `layout` – u operativního projektu bez gitu `none`
- `docs` – `docs/`, `root`, `CLAUDE.md` u operativního projektu (nabídka se pak staví jen ze sekcí
  `## Přerušený běh` a `## Otevřené body` jeho `CLAUDE.md`), nebo null, když projekt `todo.md` nemá
- `current` – větev a necommitnuté soubory tam, kde session stojí (null v kořeni kontejneru)
- `todo` – sekce `todo.md`, v každé položky (`title`, `text` zkrácený, `done`, `size`);
  u srovnaného souboru jen vrchol pásem práce a u sekce, ze které se nevešlo, počet v `more`; sekce
  `Přerušený běh` nese i bloky z `todo.md` ostatních worktree a podprojektů, u nich
  s větví v `branch` a u podprojektu s cestou v `project`
- `projects` – fronty podprojektů v `todo.md` pod worktree, kde session stojí: podprojekt,
  ve kterém session stojí, s `current` a vrcholem fronty v `todo` (a `legacy`) jako u kořene,
  ostatní jen počet otevřených položek v `open`, první připravenou v `first` a v `due`
  položky odložené k datu, které už nastalo; přerušené běhy z nich nesou `todo` výš
- `rounds` – bloky kol návrhu s poli a stavem ve větvi kola; `stitch_pending` – čeká sešití
- `plan` – počet otevřených a hotových úkolů a první otevřené; `artifacts` – které návrhové dokumenty existují
- `passes` – posledních pět záznamů `## Průchody životním cyklem`; `lifecycle` – kroky cyklu z `~/.claude/standards/rules.md` po vrstvách (`osa`, `kontroly`)
- `branches` – nesloučené větve a větve živých session: `state` (`occupied`, `abandoned`,
  `uncertain`, `empty`), session, commity, změny `todo.md`/`plan.md`/`done.md` a přiřazená kola
- `sessions_error` – proč se živé session nedaly zjistit (pak jsou všechny větve `uncertain`)
- `legacy` – proč `todo.md` není ve srovnaném tvaru, nebo null; pak `todo` nese celou frontu
- `backlog` – názvy nápadů, jen když je nabídka prázdná
- `text_limit` – na kolik znaků se popisy položek dokrátily, aby se výstup vešel
  do kontextu; `null` znamená, že se krátit nemuselo, `0` že popisy odpadly celé

Pravidla, podle kterých se tu rozhoduje, drží `SKILL.md`; tenhle docstring jen popisuje výstup.
"""

import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# `sessions.py` leží vedle; Python adresář spuštěného skriptu do cest přidává sám.
import sessions

TEXT_LIMIT = 300
# Výstup nad ~30 kB harness do kontextu nevloží – uloží ho do souboru a modelu dá
# jen náhled. Skill pak data dolovává zpátky dalšími voláními a celá úspora padne
# (změřeno 29. 9. 2026 na frontě o 74 položkách: 39 kB, useknuto, běh 4:30).
# Rozpočet je proto tvrdý a `fit_budget` pod něj popisy položek dokrátí.
BUDGET = 25000
TEXT_STEPS = (200, 160, 120, 80, 40, 0)
# Kolik položek srovnané fronty jde do výpisu. Pořadí i velikost nese `todo.md`
# sám (`~/.claude/standards/structure.md`, *`todo.md`*), takže zbytek fronty
# model nepotřebuje číst – a na délce výpisu stojí většina času běhu.
TOP = 10
SIZE = re.compile(r"([○◐●])\s*")
# Sekce s vlastním tvarem a pořadím (`structure.md`, *`todo.md`*): do vrcholu
# se nepočítají, vracejí se celé, velikost u nich chybět smí a položkou je
# i holá odrážka – `## Rozhodnuto k zapracování` zaškrtávátka nemá.
SPECIAL = {
    "Přerušený běh",
    "Parkované v session",
    "Rozhodnuto k zapracování",
    "Otázky dalšího kola",
}
# Nadpis části `todo.md`, jejíž sekce se neřadí (`~/.claude/standards/structure.md`, *`todo.md`*).
OUTSIDE = "Mimo frontu"
DIFF_LINES = 12
# Složky, do kterých hledání `todo.md` podprojektů nesestupuje – stejně jako příkaz *Fáze 1* v `SKILL.md`.
SKIP_DIRS = {"node_modules", "vendor"}
RULES = Path.home() / ".claude" / "standards" / "rules.md"


class Repo:
    """Volání gitu nad kontejnerem (přes `.bare`) i nad běžným repozitářem."""

    def __init__(self, start: Path):
        start = start.resolve()
        self.start, self.worktree = start, None
        # Kontejner se hledá mezi všemi předky, ne jen o úroveň výš: session stojí
        # klidně v `main/docs/` a jako běžný repozitář by pak minula ostatní worktree.
        container = next(
            (p for p in [start, *start.parents] if (p / ".bare").is_dir()), None
        )
        if container is not None:
            self.root, self.layout = container, "worktree"
            if start != container:
                self.worktree = container / start.relative_to(container).parts[0]
        else:
            top = run(["git", "-C", str(start), "rev-parse", "--show-toplevel"])
            if top is not None:
                self.root, self.layout, self.worktree = Path(top), "plain", Path(top)
            else:
                # Operativní projekt git mít nemusí – výchozí volba v `/project` je bez něj.
                # Gitová volání pak vracejí None a fronta se čte jen z `CLAUDE.md`.
                self.root = next(
                    (p for p in [start, *start.parents] if operative(p / "CLAUDE.md")),
                    None,
                )
                if self.root is None:
                    raise SystemExit(f"{start} není git repozitář")
                self.layout = "none"
        self.base = (
            ["git", "--git-dir", str(self.root / ".bare")]
            if self.layout == "worktree"
            else ["git", "-C", str(self.root)]
        )

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


OPERATIVE = re.compile(r"^- \*\*Struktura:\*\* `?CLAUDE\.md`?\s*$", re.M)
# Sekce `CLAUDE.md` operativního projektu, které jsou frontou (`structure.md`, *Operativní
# projekt*). Otevřené body u témat se nesbírají – jsou součástí zápisu o tématu.
OPERATIVE_SECTIONS = ("Přerušený běh", "Otevřené body")


def operative(path: Path):
    return path.is_file() and OPERATIVE.search(path.read_text(errors="replace"))


def operative_queue(text):
    """Z `CLAUDE.md` operativního projektu jen sekce, které jsou frontou, jako `todo.md`."""
    return "\n".join(
        f"## {t}\n" + "\n".join(b) for t, b in sections(text) if t in OPERATIVE_SECTIONS
    )


def docs_prefix(read):
    if read("docs/todo.md") is not None:
        return "docs/"
    if read("todo.md") is not None:
        return ""
    return None


def short(text):
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= TEXT_LIMIT else text[: TEXT_LIMIT - 1] + "…"


def item_title(first_line):
    """Tučný začátek položky, jinak její začátek; vrací (název, zbytek textu)."""
    m = re.match(r"\*\*(.+?)\*\*\s*", first_line)
    if m:
        return m.group(1).rstrip("."), first_line[m.end() :]
    return short(first_line)[:120], first_line


def parse_items(lines, checkbox_only=False):
    """Položky na nejvyšší úrovni seznamu (`- `, `- [ ]`, `1.`) i s pokračováním.

    S `checkbox_only=True` je položkou jen zaškrtávátko a ostatní seznamy jsou
    komentář k nim – výčet kandidátů, pořadí, v jakém se mají dělat. Rozhoduje
    se to nad celým souborem, ne nad sekcí, protože výklad odrážky se uvnitř
    jednoho `todo.md` měnit nesmí.
    """
    items, cur = [], None
    for line in lines:
        m = re.match(r"(?:[-*]|\d+\.) (?:\[( |x|X)\] )?(.*)", line)
        if m and (m.group(1) is not None or not checkbox_only):
            cur = {
                "done": (m.group(1) or " ").lower() == "x",
                "first": m.group(2),
                "rest": [],
            }
            items.append(cur)
        elif cur is not None and line.startswith((" ", "\t")):
            cur["rest"].append(line)
    out = []
    for i in items:
        size = SIZE.match(i["first"])
        title, rest = item_title(i["first"][size.end() :] if size else i["first"])
        full = " ".join([rest] + i["rest"])
        entry = {"title": title, "text": short(full), "done": i["done"]}
        if size:
            entry["size"] = size.group(1)
        # Závislost bývá na konci dlouhého popisu, který `short` ořízne – vytáhne se zvlášť.
        waits = find_waits(full)
        if waits and not NO_WAIT.match(waits.group(1).strip("* ")):
            entry["waits"] = short(waits.group(1))
        # Položka odložená k datu se do té doby nemá nabízet. Datum musí stát hned
        # za názvem – uvnitř popisu bývá datum ze zdůvodnění, které odklad neznamená.
        not_before = NOT_BEFORE.match(full.lstrip())
        if not_before:
            entry["not_before"] = not_before.group(1)
            entry["waiting"] = not_before.group(1) > datetime.date.today().isoformat()
        out.append(entry)
    return out


# Závislost je vlastní zápis položky: velké „Čeká na“, holé nebo tučné. Malé
# „čeká na“ je vedlejší věta a kurzíva či uvozovky citace (`měl *Čeká na: nic*`) –
# obojí popisuje něco jiného než tuhle položku.
WAITS = re.compile(
    r"(?<!\w)(?<![^*]\*)(?<!„)Ček(?:á|ají)\s+na\b[:\s]*\**\s*([^.;\n]{1,160})"
)
CODE_SPAN = re.compile(r"`[^`\n]*`")


def find_waits(text):
    """První závislost mimo úsek kódu – `**Čeká na:**` v apostrofech je citace tvaru."""
    spans = [m.span() for m in CODE_SPAN.finditer(text)]
    for m in WAITS.finditer(text):
        if not any(a <= m.start() < b for a, b in spans):
            return m
    return None


# Hodnota, která říká, že položka na nic nečeká.
NO_WAIT = re.compile(r"(?:nic|–|-)\W*$")
NOT_BEFORE = re.compile(r"[–—:-]?\s*od\s+\**(\d{4}-\d{2}-\d{2})")
# Jen zaškrtávátko první úrovně dělá z fronty frontu zaškrtávátek – odsazený
# checklist uvnitř položky by jinak zahodil všechny holé odrážky nad ním.
CHECKBOX = re.compile(r"[-*] \[( |x|X)\]")
# V plánu bývají kroky úkolu vnořené, tam se počítá i odsazené zaškrtávátko.
PLAN_BOX = re.compile(r"\s*[-*] \[( |x|X)\]")


def sections(text, level="## ", preamble=False):
    """Rozdělí Markdown na sekce dané úrovně: [(nadpis, řádky)].

    Řádky před prvním nadpisem jsou bezejmenná sekce a ve výchozím nastavení
    se zahodí. S `preamble=True` se vrátí s `None` místo nadpisu – fronta psaná
    bez `## ` nadpisů by se jinak ztratila celá a `/next` by nad ní tvrdil, že
    projekt nemá co dělat.
    """
    out, title, buf = [], None, []
    for line in text.splitlines():
        if line.startswith(level):
            out.append((title, buf))
            title, buf = line[len(level) :].strip(), []
        else:
            buf.append(line)
    out.append((title, buf))
    return [
        (t, b)
        for t, b in out
        if t is not None or (preamble and any(x.strip() for x in b))
    ]


def todo_sections(text):
    """Sekce `## ` souboru `todo.md` jako [(nadpis, řádky, mimo frontu)].

    Část pod `# Mimo frontu` se čte zvlášť: jinak by se pásmo zapsané omylem
    tam počítalo jako práce a text před jejím prvním `## ` by se přilepil
    k poslednímu pásmu fronty.
    """
    out = []
    for top, chunk in sections(text, "# ", preamble=True):
        outside = top == OUTSIDE
        for title, body in sections("\n".join(chunk), preamble=not outside):
            out.append((title, body, outside))
    return out


def ranked(section):
    """Je sekce pásmem práce, jehož pořadí je priorita?"""
    return section["section"] not in SPECIAL and not section.get("outside")


# Pole bloku kola: popisek v Markdownu je česky, klíč ve výstupu anglicky.
FIELD_KEYS = {
    "Stav": "status",
    "Větev": "branch",
    "Dokument": "document",
    "Čeká na": "waits",
    "Sahá na": "touches",
}
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


CONTINUE_MARK = "**Jak pokračovat:**"
SENTENCE = re.compile(r"(.+?[.!?])(?=\s+[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ*`]|\s*$)", re.S)


def parse_interrupted(body):
    """Bloky `### ` sekce `## Přerušený běh`, každý jako jedna položka.

    `/end` píše přerušení jako blok s nadpisem a odstavcem `**Jak pokračovat:**`,
    ne jako odrážky – obecný parser by v něm viděl podsekci se seznamy uvnitř
    a položky vyrobil z výčtu zbývající práce, nebo žádnou. Textem položky je
    první věta *Jak pokračovat*, protože ta je jediná první akce navázání.
    """
    items = []
    for title, lines in sections("\n".join(body), "### "):
        start = next((i for i, x in enumerate(lines) if CONTINUE_MARK in x), None)
        text = ""
        if start is not None:
            para = [lines[start].split(CONTINUE_MARK, 1)[1]]
            for line in lines[start + 1 :]:
                if not line.strip():
                    break
                para.append(line)
            m = SENTENCE.match(" ".join(x.strip() for x in para).strip())
            text = m.group(1) if m else " ".join(para).strip()
        items.append({"title": title, "text": short(text), "done": False})
    return items


def parse_todo(text):
    out, rounds, stitched = [], [], False
    # Nese-li fronta zaškrtávátka, jsou položkami jen ona; holý seznam je pak
    # komentář k nim. Fronta psaná bez zaškrtávátek si ponechá starý výklad.
    boxed = work_boxed(text)
    for title, body, outside in todo_sections(text):
        boxed_here = boxed and not outside and title not in SPECIAL
        if title == "Kola návrhu":
            rounds = parse_rounds(body)
            stitched = any("Návrh sešitý" in line for line in body)
            continue
        # Sekce bez bloků `### ` je zápis ve starém tvaru odrážkami – ten
        # zvládne obecný parser níž.
        interrupted = parse_interrupted(body) if title == "Přerušený běh" else []
        if interrupted:
            out.append(
                {
                    "section": title,
                    "parts": [{"subsection": None, "items": interrupted}],
                }
            )
            continue
        subs = [(None, body)] + sections("\n".join(body), "### ")
        head = body[
            : next((i for i, x in enumerate(body) if x.startswith("### ")), len(body))
        ]
        entries = [
            {
                "subsection": None,
                "items": [i for i in parse_items(head, boxed_here) if not i["done"]],
            }
        ]
        entries += [
            {
                "subsection": t,
                "items": [i for i in parse_items(b, boxed_here) if not i["done"]],
            }
            for t, b in subs[1:]
        ]
        parts = [e for e in entries if e["items"]]
        # Bezejmenná preambule se vypisuje jen tehdy, když v ní opravdu něco čeká –
        # jinak by každá fronta s úvodním odstavcem začínala prázdnou sekcí.
        if parts or title is not None:
            entry = {"section": title, "parts": parts}
            if outside:
                entry["outside"] = True
            out.append(entry)
    return out, rounds, stitched


def work_boxed(text):
    """Nese některé pásmo práce zaškrtávátko první úrovně?

    Rozhoduje se jen nad pásmy práce: zaškrtávátko v parkovaných bodech nebo
    v sekci mimo frontu by jinak přepnulo výklad celého souboru a holé položky
    pásem by zmizely bez varování.
    """
    return any(
        CHECKBOX.match(line)
        for title, body, outside in todo_sections(text)
        if not outside and title not in SPECIAL and title != "Kola návrhu"
        for line in body
    )


def queue_items(todo):
    """Otevřené položky pásem priority, v pořadí souboru."""
    return [i for s in todo if ranked(s) for p in s["parts"] for i in p["items"]]


def legacy_shape(todo, text):
    """Proč `todo.md` není ve srovnaném tvaru, nebo `None`, když je.

    Srovnaný tvar nese velikost u každé položky a položky jsou zaškrtávátka,
    takže skript vrchol fronty určí sám. Rozhoduje se v témže průchodu, kterým
    se soubor parsuje – srovnanou frontu kontrola nesmí zdržet ani o volání.
    """
    reasons = []
    items = queue_items(todo)
    if items and not work_boxed(text):
        reasons.append("položky nejsou zaškrtávátka")
    if items and not re.search(r"(?m)^# Fronta\s*$", text):
        reasons.append("chybí nadpis `# Fronta`")
    unsized = sum("size" not in i for i in items)
    if unsized:
        reasons.append(f"{unsized} z {len(items)} položek bez velikosti")
    return reasons or None


def top_of_queue(todo, limit=TOP):
    """Nechá ve frontě jen prvních `limit` připravených položek v pořadí souboru.

    Přerušený běh, parkované body a sekce mimo frontu zůstávají celé a položka, která na něco čeká, se do limitu
    nepočítá – vypisuje se zvlášť a stačí jí název a závislost. Co se nevešlo,
    nese sekce jako počet v `more`.
    """
    left = limit
    for s in todo:
        more = 0
        for p in s["parts"]:
            keep = []
            for i in p["items"]:
                if not ranked(s):
                    keep.append(i)
                elif i.get("waits") or i.get("waiting"):
                    i.pop("text", None)
                    keep.append(i)
                elif left > 0:
                    keep.append(i)
                    left -= 1
                else:
                    more += 1
            p["items"] = keep
        s["parts"] = [p for p in s["parts"] if p["items"]]
        if more:
            s["more"] = more
    return todo


def todo_files(top: Path):
    """`todo.md` podprojektů pod `top`, do téže hloubky a se stejnými výjimkami jako příkaz *Fáze 1* v `SKILL.md`.

    Soubor smí ležet nejvýš o tři úrovně níž (`zakazka/docs/todo.md`), skryté
    složky, `node_modules` a `vendor` se nenavštěvují – sběr musí zůstat rychlý.
    Vlastní `todo.md` projektu (`todo.md`, `docs/todo.md`) se vynechává, to čte
    `main` z hlavní větve.
    """
    found = []
    for path, dirs, files in os.walk(top):
        rel = Path(path).relative_to(top)
        depth = len(rel.parts)
        dirs[:] = sorted(
            d
            for d in dirs
            if depth < 2 and not d.startswith(".") and d not in SKIP_DIRS
        )
        if "todo.md" in files and rel.parts not in ((), ("docs",)):
            found.append(rel / "todo.md")
    return found


def nested_interrupted(repo: Repo, base, known):
    """Bloky `## Přerušený běh` ze všech worktree repozitáře, které fronta hlavní větve nemá.

    `/end` zapisuje do `todo.md` projektu, ve kterém session stojí – u podprojektu
    klientské složky tedy do podsložky, ve worktree layoutu do `todo.md` větve.
    Hlavní větev ani jedno nevidí. Zbytek fronty podprojektu nese
    `subproject_queues`. Položka nese v `branch` větev worktree a u
    podprojektu v `project` jeho cestu vůči kořeni worktree; blok, který už je
    ve frontě hlavní větve (`known`) nebo v jiném worktree, se počítá jednou.
    """
    own = Path(f"{base}todo.md")
    items, seen = [], {(".", t) for t in known}
    for top, branch in worktree_branches(repo).items():
        if not (top / ".git").exists():
            continue
        for rel in [own, *todo_files(top)]:
            if not (top / rel).is_file():
                continue
            project = Path(".") if rel == own else rel.parent
            if project.name == "docs":
                project = project.parent
            for item in interrupted_in(top / rel):
                key = (str(project), item["title"])
                if key in seen:
                    continue
                seen.add(key)
                item["branch"] = branch
                if rel != own:
                    item["project"] = str(project)
                items.append(item)
    return items


def subproject_dir(rel: Path):
    """Složka podprojektu, jehož je `rel` frontou (`zakazka/docs/todo.md` → `zakazka`)."""
    return rel.parent.parent if rel.parent.name == "docs" else rel.parent


def subproject_queues(top: Path, start: Path, whole=False):
    """Fronty podprojektů pod `top` (`todo.md` z `todo_files`).

    Podprojekt, ve kterém session stojí (`own_subproject`), je její vlastní
    projekt a vrací se vrchol jeho fronty jako u kořene. Ostatní patří k jinému projektu: stačí počet, první položka
    a odložené položky, jejichž den nastal – ty by se jinak nepřipomněly nikde.
    Sekce `Přerušený běh` se vynechává, tu přidává `nested_interrupted`.
    """
    files = {}
    # Projekt s `docs/todo.md` i `todo.md` čte frontu z `docs/`, jako `docs_prefix`.
    for rel in todo_files(top):
        project = subproject_dir(rel)
        if project not in files or rel.parent.name == "docs":
            files[project] = rel
    here = own_subproject(list(files), top, start)
    out = []
    for project, rel in sorted(files.items()):
        text = (top / rel).read_text(encoding="utf-8", errors="replace")
        todo, _, _ = parse_todo(text)
        todo = [s for s in todo if s["section"] != "Přerušený běh"]
        if project == here:
            legacy = legacy_shape(todo, text)
            if not legacy and not whole:
                todo = top_of_queue(todo)
            if any(p["items"] for s in todo for p in s["parts"]):
                out.append(
                    {
                        "project": str(project),
                        "current": True,
                        "todo": todo,
                        "legacy": legacy,
                    }
                )
            continue
        items = queue_items(todo)
        if not items:
            continue
        ready = [i for i in items if not i.get("waits") and not i.get("waiting")]
        brief = ("title", "size", "not_before")
        out.append(
            {
                "project": str(project),
                "open": len(items),
                "first": {k: ready[0][k] for k in brief if k in ready[0]}
                if ready
                else None,
                "due": [
                    {k: i[k] for k in brief if k in i}
                    for i in items
                    if i.get("not_before") and not i["waiting"]
                ],
            }
        )
    return out


def own_subproject(projects, top: Path, start: Path):
    """Podprojekt session: nejbližší, jehož složka je `start` nebo leží nad ním.

    Nestojí-li session v žádném, ale v mezilehlé složce pod `top`, je jejím
    projektem jediný nejbližší podprojekt pod ní. Leží-li jich v téže hloubce
    víc, není jak vybrat a všechny zůstanou souhrnem – stejně jako z kořene.
    """
    above = [p for p in projects if (top / p) == start or (top / p) in start.parents]
    if above:
        return max(above, key=lambda p: len(p.parts))
    if start == top or top not in start.parents:
        return None
    below = [p for p in projects if start in (top / p).parents]
    nearest = min((len(p.parts) for p in below), default=None)
    closest = [p for p in below if len(p.parts) == nearest]
    return closest[0] if len(closest) == 1 else None


def session_tree(repo: Repo, ref):
    """Worktree, jehož podprojekty se čtou: ten, kde session stojí, v kořeni kontejneru hlavní větev."""
    if repo.worktree is not None or repo.layout != "worktree":
        return repo.worktree
    main = (ref or "").removeprefix("origin/")
    return next((t for t, b in worktree_branches(repo).items() if b == main), None)


def worktree_branches(repo: Repo):
    """Kořen každého worktree a jeho větev (None u odpojené hlavy)."""
    out, top = {}, None
    for line in (repo.git("worktree", "list", "--porcelain") or "").splitlines():
        if line.startswith("worktree "):
            top = Path(line[9:])
            out[top] = None
        elif line.startswith("branch refs/heads/") and top:
            out[top] = line[18:]
    return out


def interrupted_in(path: Path):
    """Položky sekce `## Přerušený běh` jednoho `todo.md`."""
    text = path.read_text(encoding="utf-8", errors="replace")
    return [
        item
        for title, body in sections(text)
        if title == "Přerušený běh"
        for item in parse_interrupted(body)
    ]


def add_interrupted(todo, items):
    """Přidá přerušené běhy podprojektů do sekce `Přerušený běh`, případně ji založí."""
    if not items:
        return
    section = next((s for s in todo if s["section"] == "Přerušený běh"), None)
    if section is None:
        section = {"section": "Přerušený běh", "parts": []}
        todo.insert(0, section)
    section["parts"].append({"subsection": None, "items": items})


def parse_done(text):
    passes, rounds_done, closed_after = [], False, True
    for title, body in sections(text or ""):
        if title == "Průchody životním cyklem":
            # Projekty řadí záznamy různě (nejnovější nahoře i dole) – rozhoduje datum.
            entries = [x for x in body if x.startswith("- ")]
            passes = [
                short(x)
                for x in sorted(
                    entries, key=lambda x: re.findall(r"\d{4}-\d{2}-\d{2}", x)[:1]
                )
            ][-5:]
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
            m = PLAN_BOX.match(line)
            if m:
                boxes.append(m.group(1).lower() == "x")
    if not tasks:
        tasks = [
            (line.strip(), m.group(1).lower() == "x")
            for line in text.splitlines()
            if (m := PLAN_BOX.match(line))
        ]
    open_ = [short(name)[:120] for name, done in tasks if not done]
    return {"open": len(open_), "done": len(tasks) - len(open_), "next": open_[:3]}


def lifecycle():
    """Kroky cyklu z rámečku v `~/.claude/standards/rules.md`, rozdělené podle vrstev.

    Vrací {"osa": [...], "kontroly": [...]}. Vrstvu zakládá jen řádek, který
    začíná jejím jménem; odsazené pokračování patří pod tu předchozí. Dřív se
    vracely syrové řádky bloku – nad dvouvrstvým rámečkem z toho byly položky
    jako `"Kontroly   /oponent, …"` a věta pod nimi, tedy data, ze kterých
    „chybějící krok cyklu“ odvodit nejde.

    Kroky osy jsou řada a čekají na výstup toho předchozího; kontrolní kroky
    stojí v mezerách mezi nimi a některé ve víc naráz, takže pořadí nemají
    a odvozovat z nich chybějící krok nelze.
    """
    text = RULES.read_text(encoding="utf-8") if RULES.is_file() else ""
    m = re.search(r"### Životní cyklus projektu.*?```\n(.*?)```", text, re.S)
    out, layer = {}, None
    for row in m.group(1).splitlines() if m else []:
        steps = re.findall(r"/([a-z][a-z-]*)", row)
        if not steps:
            continue
        head = row.split()[0]
        if not head.startswith("/"):
            layer = head.lower()
        if layer is None:
            continue
        out.setdefault(layer, []).extend(steps)
    return out


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
    changed = [
        short(x)
        for x in diff.splitlines()
        if x[:1] in "+-" and not x.startswith(("+++", "---")) and x[1:].strip()
    ]
    return {
        "changes": changed[:DIFF_LINES],
        "changes_total": len(changed),
        "adds_stitch": any(
            x.startswith("+") and ("Návrh sešitý" in x or "Návrh uzavřen" in x)
            for x in changed
        ),
    }


def live_state(project: Path, trees: dict):
    try:
        if not (sessions.Path.home() / ".claude" / "sessions").is_dir():
            return [], [], "registr session neexistuje"
        home = Path.home() / ".claude"
        live = sessions.live_sessions(home, trees)
        for s in live:
            s["in_project"] = sessions.inside(
                s["start_cwd"], project
            ) or sessions.inside(s["cwd"], project)
        idle = sessions.idle_sessions(
            home, project, {s["session_id"] for s in live if s["session_id"]}, trees
        )
    except (sessions.Unreadable, OSError) as err:
        # Transcript, který zmizel mezi výpisem a čtením, nesmí shodit celý běh –
        # platí totéž co pro nečitelný registr: nejisté, tedy obsazené.
        return [], [], str(err)
    return live, idle, None


def classify_branch(branch, others, idle, error, work):
    busy = [s for s in others if s["branch"] == branch]
    if busy:
        return {"state": "occupied", "session": busy[0]["name"]}
    if error or any(s["branch"] is None for s in others):
        why = (
            error
            or "živá session nad projektem nemá zjistitelnou větev (čerstvě otevřené okno?)"
        )
        return {"state": "uncertain", "why": why}
    if not work:
        # Sloučená nebo nezačatá větev bez neuložených změn není zapomenutá práce.
        return {"state": "empty"}
    match = next((s for s in idle if s["branch"] == branch), None)
    return {
        "state": "abandoned",
        "resume": match
        and {k: match[k] for k in ("session_id", "start_cwd", "updated")},
    }


def collect_branches(repo, ref, prefix, rounds, current_branch, project):
    local = ref.split("/", 1)[1] if ref.startswith("origin/") else ref
    trees = worktrees(repo)
    live, idle, error = live_state(project, {p: b for b, p in trees.items()})
    others = [s for s in live if s.get("in_project") and not s["self"]]
    names = set(
        (
            repo.git("branch", "--no-merged", ref, "--format=%(refname:short)") or ""
        ).split()
    )
    names |= set(trees) | {s["branch"] for s in others if s["branch"]}
    if current_branch:
        names.add(current_branch)
    names -= {"HEAD"}
    out = []
    for b in sorted(names):
        if repo.git("rev-parse", "--verify", "--quiet", b) is None:
            continue
        info = branch_info(repo, ref, b, trees.get(b), prefix)
        info.update(
            current=b == current_branch,
            main=b in (local, "main", "master"),
            rounds=[r["title"] for r in rounds if r.get("branch") == b],
        )
        work = info["ahead"] or info["uncommitted"]
        info.update(classify_branch(b, others, idle, error, work))
        # Hlavní větev se vypisuje jen tehdy, když v ní opravdu něco leží – commit nad
        # hlavní referencí nebo neuložená změna. Na `state` se to neváže: session, která
        # startuje v kořeni kontejneru a vlastní větev si ještě nezaložila, hlásí hlavní
        # větev jako svou, takže by se vypsala jako `occupied` a `/next` by ji podle
        # vlastního pravidla přestal nabízet, přestože na ní nikdo nepracuje.
        if info["main"] and not work:
            continue
        out.append(info)
    return out, error


def branch_info(repo, ref, b, tree, prefix):
    status = (
        (run(["git", "-C", tree, "status", "--porcelain"]) or "").splitlines()
        if tree
        else []
    )
    info = {
        "branch": b,
        "worktree": tree,
        "uncommitted": len(status),
        "ahead": int(repo.git("rev-list", "--count", f"{ref}..{b}") or 0),
        "commits": (
            repo.git("log", "--format=%s", "-3", f"{ref}..{b}") or ""
        ).splitlines(),
        "last": repo.git("log", "-1", "--format=%cr", b),
        "last_ts": int(repo.git("log", "-1", "--format=%ct", b) or 0),
    }
    info.update(branch_diff(repo, ref, b, prefix))
    return info


def round_states(repo, rounds, prefix):
    for r in rounds:
        b = r.get("branch")
        if not b or repo.git("rev-parse", "--verify", "--quiet", b) is None:
            continue
        text = repo.git("show", f"{b}:{prefix}todo.md") or ""
        block = next(
            (body for t, body in sections(text, "### ") if t == r["title"]), None
        )
        if block is None:
            # Blok kola ve větvi chybí: rozhodnutí je zapsané v dokumentech a kolo
            # z todo.md zmizelo – zbývá sloučit. Token, ne věta, ať se podle něj dá
            # rozhodovat; ostatní hodnoty jsou řádek *Stav* z todo.md, jak ho kdo napsal.
            r["branch_state"] = "merge_pending"
        else:
            m = next(
                (FIELD.match(x) for x in block if FIELD.match(x) and "Stav" in x), None
            )
            r["branch_state"] = m.group(2).strip() if m else None


def current_info(repo: Repo):
    if repo.worktree is None:
        return None
    branch = run(["git", "-C", str(repo.worktree), "branch", "--show-current"])
    status = (
        run(["git", "-C", str(repo.worktree), "status", "--porcelain"]) or ""
    ).splitlines()
    return {
        "branch": branch,
        "uncommitted": status[:15],
        "uncommitted_total": len(status),
    }


def encoded_size(result):
    return len(json.dumps(result, ensure_ascii=False, separators=(",", ":")).encode())


def fit_budget(result):
    """Dokrátí popisy položek `todo`, aby se výstup vešel do `BUDGET`.

    Krátí se jen `text` – na jednořádkový výpis stačí název, a celý popis skill
    potřebuje u tří čtyř položek, které jde nabídnout. Zvolený limit se vrací
    v `text_limit`, aby bylo vidět, že popis není celý.
    """
    if encoded_size(result) <= BUDGET:
        return None
    todos = [result["todo"]] + [
        p["todo"] for p in result.get("projects", []) if "todo" in p
    ]
    texts = [
        (item, item["text"])
        for todo in todos
        for section in todo
        for part in section["parts"]
        for item in part["items"]
        if item.get("text")
    ]
    for limit in TEXT_STEPS:
        for item, full in texts:
            if limit == 0:
                item.pop("text", None)
            else:
                item["text"] = (
                    full if len(full) <= limit else full[: limit - 1] + "\u2026"
                )
        if encoded_size(result) <= BUDGET:
            return limit
    return 0


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--all"]
    whole = "--all" in sys.argv[1:]
    repo = Repo(Path(args[0] if args else "."))
    fetch = None
    if repo.git("remote", "get-url", "origin") is not None:
        fetch = (
            "ok"
            if run(repo.base + ["fetch", "--quiet"], timeout=15) is not None
            else "failed"
        )
    ref, _ = main_branch(repo)
    if ref is None and repo.layout != "none":
        raise SystemExit("hlavní větev se nepodařilo určit")
    read = reader(repo, ref)
    claude = read("CLAUDE.md")
    is_operative = claude is not None and OPERATIVE.search(claude) is not None
    prefix = "CLAUDE.md" if is_operative else docs_prefix(read)
    base = "" if is_operative else prefix or ""
    queue_text = (
        operative_queue(claude) if is_operative else read(f"{base}todo.md") or ""
    )
    todo, rounds, stitched = parse_todo(queue_text)
    legacy = None if is_operative else legacy_shape(todo, queue_text)
    known = [
        i["title"]
        for s in todo
        if s["section"] == "Přerušený běh"
        for p in s["parts"]
        for i in p["items"]
    ]
    # Soubory v operativním projektu patří uživateli – `plan.md` nebo `done.md` mezi nimi
    # je jeho dokument, ne fronta. Podprojekty ani worktree takový projekt nemá.
    own = (lambda path: None) if is_operative else read
    if not is_operative:
        add_interrupted(todo, nested_interrupted(repo, base, known))
    passes, rounds_open = parse_done(own(f"{base}done.md"))
    plan = parse_plan(own(f"{base}plan.md"))
    current = current_info(repo)
    round_states(repo, rounds, base)
    branches, error = (
        ([], None)
        if repo.layout == "none"
        else collect_branches(
            repo, ref, base, rounds, current and current["branch"], repo.root
        )
    )
    if not legacy and not whole:
        todo = top_of_queue(todo)
    tree = None if is_operative else session_tree(repo, ref)
    projects = subproject_queues(tree, repo.start, whole) if tree else []
    queue_empty = (
        not any(p["items"] for s in todo for p in s["parts"])
        and not projects
        and not rounds
        and not (plan and plan["open"])
    )
    result = {
        "root": str(repo.root),
        "layout": repo.layout,
        "main": ref,
        "fetch": fetch,
        "docs": None if prefix is None else (prefix or "root"),
        "current": current,
        "todo": todo,
        "legacy": legacy,
        "projects": projects,
        "rounds": rounds,
        "stitch_pending": (rounds_open or stitched) and not rounds,
        "plan": plan,
        "passes": passes,
        "lifecycle": lifecycle(),
        "artifacts": {
            n: own(f"{base}{n}.md") is not None
            for n in ("requirements", "architecture", "plan")
        },
        "branches": branches,
        "sessions_error": error,
        "backlog": (
            [
                i["title"]
                for i in parse_items((own(f"{base}backlog.md") or "").splitlines())
            ]
            if queue_empty
            else None
        ),
    }
    result["text_limit"] = fit_budget(result)
    json.dump(result, sys.stdout, ensure_ascii=False, separators=(",", ":"))
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
