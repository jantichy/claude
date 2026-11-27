"""Sestaví soubory design systému a startovního decku na claude.ai ze zdroje v gitu.

Zdroj (výchozí ~/Context/Brand/design/):
  tokens.json        tokeny – barvy, písma, typové styly, mezery, zaoblení
  brandbook.md       brand book, publikuje se jako project/README.md design systému
  layout.css         rozvržení slajdů jt-* (část 3 deck.css i bundle.css)
  components.json    podtitulek náhledu každé komponenty
  components/<Typ>/README.md, components/Cover/preview.html
  fonts/             soubory písem, které tokens.json jmenuje v type.fonts
  starter/deck.json, starter/slides/<id>.html   startovní deck, vzorový slajd na typ
                     (deck.json bez faces – ty skript vyrobí z type.fonts)

Výstup do <out>/system/ a <out>/starter/ se stromem project/… přesně tak, jak se
publikuje (Artifact s `files` a `root` na tyhle adresáře). Sám nic nepublikuje.

    python3 -I design.py <out> [--source <adresář>]

Náhled komponenty je vzorový slajd startovního decku bez poznámek, takže vzorová sada
je jedna. Tokeny a typové styly v deck.css vznikají z tokens.json, ne opisem.
"""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

STARTER_URL = "https://claude.ai/artifact/DtgiJayMbTa5DZezovegdH"
SYSTEM_URL = "https://claude.ai/artifact/Bh1v7u2ikt54CM52MxGESW"
NAMESPACE = "jantichy"
TOKEN_KINDS = ("color", "spacing", "radius", "stroke")


def token_vars(tokens):
    """Část 1: proměnné CSS ze všech tokenů v pořadí, jak stojí v tokens.json."""
    lines = []
    for kind in TOKEN_KINDS[:1]:
        lines += [f"  --{t['name']}: {t['value']};" for t in tokens[kind]["tokens"]]
    lines.append("")
    lines += [f"  --font-{k}: {v};" for k, v in tokens["type"]["families"].items()]
    lines.append("")
    for kind in TOKEN_KINDS[1:]:
        lines += [f"  --{t['name']}: {t['value']};" for t in tokens[kind]["tokens"]]
    return ":root {\n" + "\n".join(lines) + "\n}\n"


def type_styles(tokens):
    """Část 2: třída na každý typový styl; rodinu jen tam, kde není bezpatková."""
    lines = []
    for group in tokens["type"]["groups"]:
        for style in group["styles"]:
            family = style.get("family", group.get("family", "sans"))
            font = "" if family == "sans" else f"font-family: var(--font-{family}); "
            lines.append(
                f".{style['name']} {{ {font}font-size: {style['fontSize']}; "
                f"line-height: {style['lineHeight']}; font-weight: {style['fontWeight']}; }}"
            )
    return "\n".join(lines) + "\n"


def deck_css(tokens, layout):
    return (
        "/* Jan Tichý – sdílené styly decku.\n"
        "   Vygenerované skriptem design.py skillu /deck ze zdroje ~/Context/Brand/design/\n"
        "   (tokens.json a layout.css). Neupravuj tady ani v žádném decku: změna patří do zdroje\n"
        "   a nové publikace. Nový deck tenhle soubor kopíruje beze změny ze startovního decku\n"
        f"   ({STARTER_URL}). */\n\n"
        "/* 1. Tokeny – hodnoty z tokens.json */\n" + token_vars(tokens) + "\n"
        "/* 2. Typové styly – velikost, řádkování, řez a rodina; barvu dává rozvržení */\n"
        + type_styles(tokens)
        + "\n"
        "/* 3. " + layout.removeprefix("/* ")
    )


def faces(tokens):
    """Písma decku: na rodinu jeden soubor, nainstalovaný z design systému pod project/ds/."""
    return {
        f["family"].lower().replace(" ", "-"): {
            "family": f["family"],
            "src": f"project/ds/{NAMESPACE}/{f['file']}",
        }
        for f in tokens["type"]["fonts"]
    }


def deck_json(deck, tokens):
    """Index startovního decku: zdroj bez písem, `faces` se doplní z tokens.json."""
    result = {}
    for key, value in deck.items():
        if key == "designSystems":
            result["faces"] = faces(tokens)
        result[key] = value
    return json.dumps(result, ensure_ascii=False, indent=2) + "\n"


def bundle_css(layout):
    return (
        "/* Jan Tichý – slajdy. Písma načítá design systém z tokens.json (type.fonts). Barvy, mezery a typové styly jdou z tokens.json (tokens.css); tady je\n"
        "   jen rozvržení. Vygenerované skriptem design.py skillu /deck ze zdroje\n"
        "   ~/Context/Brand/design/layout.css, stejně jako část 3 deck.css startovního decku\n"
        f"   ({STARTER_URL}). Neupravuj tady, ale ve zdroji. */\n\n"
        "/* Jen pro náhledy: slajd v prohlížeči nemá plátno decku a x-shape nezná */\n"
        ".jt-slide { position: relative; width: 1920px; height: 1080px; overflow: hidden; }\n"
        "x-shape { display: block; }\n\n"
        "/* 3. " + layout.removeprefix("/* ")
    )


def groups(deck):
    """Skupina náhledu je název oddílu startovního decku (text popisu před dvojtečkou)."""
    result, current = {}, None
    starts = {
        s["start"]: s["description"].split(":")[0] for s in deck["sections"].values()
    }
    for slide_id in deck["order"]:
        current = starts.get(slide_id, current)
        result[slide_id] = current
    return result


def preview(slide, name, group, subtitle):
    body = re.sub(r"<aside>.*?</aside>\n", "", slide, flags=re.S)
    body = re.sub(r'<section id="[^"]+" ', "<section ", body, count=1)
    return (
        f'<!-- @dsCard group="{group}" width=1920 height=1080 subtitle="{subtitle}" -->\n'
        '<!doctype html>\n<html lang="cs">\n'
        f'<head><meta charset="utf-8"><title>{name} – náhled</title></head>\n'
        f"<body>\n{body}</body>\n</html>\n"
    )


def check(src, deck, subtitles, slides):
    """Vrátí seznam rozporů mezi pořadím decku, slajdy a komponentami."""
    errors = []
    order = deck["order"]
    names = {i: i.capitalize() for i in order}
    if set(slides) != set(order):
        errors.append(
            f"slajdy {sorted(set(slides) ^ set(order))} nesedí s pořadím v deck.json"
        )
    if set(subtitles) != set(names.values()):
        errors.append(
            f"components.json {sorted(set(subtitles) ^ set(names.values()))} nesedí s typy"
        )
    for slide_id, html in slides.items():
        if not html.startswith(f'<section id="{slide_id}" '):
            errors.append(
                f'slides/{slide_id}.html nezačíná <section id="{slide_id}" …>'
            )
    for name in list(names.values()) + ["Cover"]:
        needed = "preview.html" if name == "Cover" else "README.md"
        if not (src / "components" / name / needed).is_file():
            errors.append(f"chybí components/{name}/{needed}")
    return errors


def check_fonts(src, tokens, deck):
    """Každé písmo z tokens.json má soubor a zdrojový deck.json písma neopisuje."""
    errors = [
        f"chybí {f['file']} z tokens.json"
        for f in tokens["type"]["fonts"]
        if not (src / f["file"]).is_file()
    ]
    if "faces" in deck:
        errors.append("starter/deck.json nese faces – ty skript vyrábí z tokens.json")
    return errors


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build(src, out):
    tokens_text = (src / "tokens.json").read_text(encoding="utf-8")
    tokens = json.loads(tokens_text)
    layout = (src / "layout.css").read_text(encoding="utf-8")
    deck_text = (src / "starter/deck.json").read_text(encoding="utf-8")
    deck = json.loads(deck_text)
    subtitles = json.loads((src / "components.json").read_text(encoding="utf-8"))
    slides = {
        p.stem: p.read_text(encoding="utf-8")
        for p in (src / "starter/slides").glob("*.html")
    }
    errors = check(src, deck, subtitles, slides) + check_fonts(src, tokens, deck)
    if errors:
        sys.exit("Zdroj nesedí:\n- " + "\n- ".join(errors))

    for part in ("system", "starter"):
        shutil.rmtree(out / part, ignore_errors=True)
    system, starter = out / "system/project", out / "starter/project"

    write(system / "tokens.json", tokens_text)
    write(system / "README.md", (src / "brandbook.md").read_text(encoding="utf-8"))
    write(system / "components/bundle.css", bundle_css(layout))
    for font in tokens["type"]["fonts"]:
        for target in (
            system / font["file"],
            starter / "ds" / NAMESPACE / font["file"],
        ):
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src / font["file"], target)
    write(
        system / "components/Cover/preview.html",
        (src / "components/Cover/preview.html").read_text(encoding="utf-8"),
    )
    group = groups(deck)
    for slide_id in deck["order"]:
        name = slide_id.capitalize()
        component = src / "components" / name
        write(
            system / "components" / name / "README.md",
            (component / "README.md").read_text(encoding="utf-8"),
        )
        write(
            system / "components" / name / "preview.html",
            preview(slides[slide_id], name, group[slide_id], subtitles[name]),
        )

    write(starter / "deck.css", deck_css(tokens, layout))
    write(starter / "deck.json", deck_json(deck, tokens))
    write(starter / "ds" / NAMESPACE / "tokens.json", tokens_text)
    for slide_id, html in slides.items():
        write(starter / "slides" / f"{slide_id}.html", html)

    count = sum(1 for p in out.rglob("*") if p.is_file())
    print(
        f"{count} souborů: design systém {SYSTEM_URL} ← {out / 'system'}, startovní deck {STARTER_URL} ← {out / 'starter'}"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("out", type=Path)
    parser.add_argument(
        "--source", type=Path, default=Path.home() / "Context/Brand/design"
    )
    args = parser.parse_args()
    build(args.source, args.out)


if __name__ == "__main__":
    main()
