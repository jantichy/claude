# /// script
# requires-python = ">=3.11"
# dependencies = ["python-pptx>=1.0.2", "segno>=1.6"]
# ///
"""Sestaví prezentaci z Markdownu nad šablonou z ~/Context/Brand/template.pptx.

Spuštění: uv run build.py <Prezentace.md> [<výstup>.pptx]
Bez výstupu zapíše <jméno adresáře zdroje>.pptx vedle zdroje. Formát zdroje drží format.md.

Vzhled slajdů se nekreslí od nuly: každý typ má v šabloně vzorový slajd, jehož tvary
se naklonují a vymění se v nich jen text. Odrážky, okraje a písmo tak sedí se šablonou.
Typ slajdu, který tenhle skript nezná, si načte ze stejnojmenného <typ>.py vedle zdroje:
modul má funkci render(slide, args) a kreslí pod nadpis, který už na slajdu stojí.
"""
import copy
import importlib.util
import io
import re
import sys
from pathlib import Path

import segno
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.util import Inches, Pt

NAVY = "#1F3A51"
CARD = "#F5F7FA"
ALIGN = {"CENTER": PP_ALIGN.CENTER, "START": PP_ALIGN.LEFT, "END": PP_ALIGN.RIGHT}
VALIGN = {"MIDDLE": MSO_ANCHOR.MIDDLE, "TOP": MSO_ANCHOR.TOP}

TEMPLATE = Path.home() / "Context/Brand/template.pptx"
KIND = re.compile(r"[a-z][a-z0-9_]*")   # jméno typu slajdu je zároveň jméno modulu s kresbou

# vzorové slajdy v šabloně (číslováno od 1) a které jejich tvary se berou
SAMPLES = {
    "title": 1,     # titulek, linka, podtitulek
    "cards": 2,     # karta světlá, karta tmavá, nadpis, linka, text světlé, text tmavé
    "grid": 3,      # čtyři karty, nadpis, linka, text 1, text 2, pointa, text 3, text 4
    "bullets": 4,   # nadpis, linka, odrážky
    "section": 7,   # nadpis, linka
    "cards_text": 8,  # karty s textem místo odrážek – berou se z něj jen styly odstavců
    "numbers": 21,  # nadpis, linka, číslo, popisek, číslo, popisek, prázdný box, pruh, text pruhu
    "end": 24,      # titulek, linka, odkazy
}

SECTION_SUB_Y = 3.5                   # podtitulek mezislajdu pod linkou (ta je na 3,33″)
QR_BOX = (7.75, 3.3, 1.9)             # levý horní roh a strana QR kódu na mezislajdu; podtitulek končí před ním
IMAGE_BOX = (0.42, 2.0, 9.15, 3.3)    # plocha pro obrázek pod linkou nadpisu: levý horní roh, šířka, výška

# odhad výšky karty: znaků na řádek, výška řádku a mezery v palcích, meze výšky
CARD_CHARS, CARD_LINE, CARD_GAP, CARD_HEAD, CARD_PAD = 26, 0.36, 0.09, 0.45, 0.45
CARD_MIN, CARD_MAX = 1.6, 3.15
CARD_TEXT_INSET = 0.275              # o kolik je textové pole nižší než karta

# krátké předložky a spojky a číslo před slovem nesmí zůstat na konci řádku
# (Honzova volba pro vlastní výstupy, ~/Context/Text/typography.md, Mezery)
SHORT = "k s v z o u a i na do od po za ze ve se ke ku pro při pod nad bez než ale ani aby či jak že"
NBSP = re.compile(r"(?<![\w\xa0])(" + "|".join(SHORT.split()) + r"|\d+) ", re.IGNORECASE)


def nbsp(text):
    return NBSP.sub("\\1\xa0", text)


# ---------- zdroj prezentace ----------

def parse(path):
    """Slajd začíná `## typ argumenty`; `#` řádky nadpisu, `###` blok, `-` odrážka, `=` pruh nebo pointa, `>` poznámky."""
    slides = []
    for raw in Path(path).read_text().splitlines():
        line = raw.rstrip()
        if line.startswith("## "):
            kind, *args = line[3:].split()
            slides.append({"type": kind, "args": args, "title": [], "body": [], "blocks": [], "banner": [], "notes": []})
            continue
        if not line or not slides:
            continue
        s = slides[-1]
        if line.startswith("> ") or line == ">":
            s["notes"].append(line[2:])
        elif line.startswith("### "):
            s["blocks"].append({"head": line[4:], "items": []})
        elif line.startswith("# "):
            s["title"].append(line[2:])
        elif line.startswith("= "):
            s["banner"].append(line[2:])
        else:
            item = ("bullet", line[2:]) if line.startswith("- ") else ("text", line)
            (s["blocks"][-1]["items"] if s["blocks"] else s["body"]).append(item)
    return slides


# ---------- klonování a text ----------

def sample_shapes(prs):
    """Hluboké kopie pozadí a tvarů vzorových slajdů, dokud šablona ještě slajdy má."""
    out = {}
    for kind, n in SAMPLES.items():
        el = prs.slides[n - 1]._element
        bg = el.cSld.bg
        out[kind] = {"bg": copy.deepcopy(bg) if bg is not None else None,
                     "shapes": [copy.deepcopy(sp) for sp in el.cSld.spTree.iterchildren()
                                if sp.tag in (qn("p:sp"), qn("p:cxnSp"))]}
    return out


def drop_all_slides(prs):
    ids = prs.slides._sldIdLst
    for sld in list(ids):
        prs.part.drop_rel(sld.rId)
        ids.remove(sld)


def new_slide(prs, sample, keep):
    slide = prs.slides.add_slide(prs.slide_layouts.get_by_name("BLANK"))
    if sample["bg"] is not None:
        slide._element.cSld.insert(0, copy.deepcopy(sample["bg"]))
    tree = slide.shapes._spTree
    shapes = []
    for i in keep:
        sp = copy.deepcopy(sample["shapes"][i])
        tree.append(sp)
        shapes.append(sp)
    return slide, shapes


def paragraphs(sp):
    return sp.find(qn("p:txBody")).findall(qn("a:p"))


def set_text(sp, items, protos):
    """Nahradí odstavce tvaru; items jsou (druh, text), protos druh -> vzorový odstavec.

    Text v `zpětných apostrofech` se sází písmem Roboto Mono, jako na slajdech decku.
    Znak `|` ručně zalamuje řádek uvnitř odstavce.
    """
    body = sp.find(qn("p:txBody"))
    for p in body.findall(qn("a:p")):
        body.remove(p)
    for kind, text in items:
        body.append(paragraph(protos[kind], text))


def paragraph(proto, text):
    """Odstavec podle vzoru s textem; `|` zalamuje řádek, `kód` jde písmem Roboto Mono."""
    p = copy.deepcopy(proto)
    run_proto = p.find(qn("a:r"))
    for child in list(p):
        if child.tag in (qn("a:r"), qn("a:br"), qn("a:fld")):
            p.remove(child)
    end = p.find(qn("a:endParaRPr"))

    def add(el):
        if end is not None:
            end.addprevious(el)
        else:
            p.append(el)

    for n, segment in enumerate(text.split("|")):
        if n:
            br = p.makeelement(qn("a:br"), {})
            br.append(copy.deepcopy(run_proto.find(qn("a:rPr"))))
            add(br)
        for i, part in enumerate(nbsp(segment.strip()).split("`")):
            if part:
                add(text_run(run_proto, part, mono=i % 2))
    return p


def text_run(proto, text, mono):
    r = copy.deepcopy(proto)
    r.find(qn("a:t")).text = text
    if mono:
        rpr = r.find(qn("a:rPr"))
        latin = rpr.find(qn("a:latin"))
        if latin is None:
            latin = rpr.makeelement(qn("a:latin"), {})
            rpr.append(latin)
        latin.set("typeface", "Roboto Mono")
    return r


# ---------- kreslení tabulky ----------

def rgb(hex_color):
    return RGBColor.from_string(hex_color.lstrip("#"))


def plain(shape):
    """Odstraní výchozí styl tvaru z motivu (stín, barvy), ať platí jen to, co nastavíme."""
    style = shape._element.find(qn("p:style"))
    if style is not None:
        shape._element.remove(style)


def write(shape, lines, size, bold, color, align="CENTER", valign="MIDDLE", inset=0.04):
    """Vepíše řádky textu písmem Roboto."""
    tf = shape.text_frame
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.vertical_anchor = VALIGN[valign]
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Inches(inset)
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = ALIGN[align]
        p.space_before = p.space_after = Pt(0)
        p.line_spacing = 1.0
        run = p.add_run()
        run.text = line
        run.font.name = "Roboto"
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = rgb(color)


def table(slide, rows):
    """Tabulka z karet: první řádek záhlaví, první sloupec štítky řádků."""
    x0, y0, first_w, col_w, row_h, gap = 0.525, 1.95, 2.55, 2.1, 0.5, 0.06
    for r, row in enumerate(rows):
        for c, cell in enumerate(row):
            x = x0 if c == 0 else x0 + first_w + gap + (c - 1) * (col_w + gap)
            w = first_w if c == 0 else col_w
            sp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y0 + r * (row_h + gap)),
                                        Inches(w), Inches(row_h))
            plain(sp)
            header = r == 0 or c == 0
            if header:
                sp.fill.background()
            else:
                sp.fill.solid()
                sp.fill.fore_color.rgb = rgb(CARD)
            sp.line.fill.background()
            write(sp, [nbsp(cell)], 16, header, NAVY, align="START" if c == 0 else "CENTER", inset=0.08)


def set_height(sp, inches):
    sp.find(qn("p:spPr")).find(qn("a:xfrm")).find(qn("a:ext")).set("cy", str(int(inches * 914400)))


def card_height(block):
    """Odhad výšky karty podle délky textu; vzorová karta má 2,4″ a začíná na 2,24″."""
    def rows(text):
        return max(1, -(-len(text.replace("`", "")) // CARD_CHARS)) + text.count("|")
    h = CARD_PAD + CARD_HEAD + sum(rows(t) * CARD_LINE + CARD_GAP for _, t in block["items"])
    return min(max(h, CARD_MIN), CARD_MAX)


def lines(texts, kind="line"):
    return [(kind, t) for t in texts]


# ---------- typy slajdů ----------

def render(prs, samples, s, base):
    kind = s["type"]
    if kind in SLIDES:
        slide = SLIDES[kind](prs, samples, s, base)
    else:
        slide = slide_extension(prs, samples, s, base, kind)
    if s["notes"]:
        slide.notes_slide.notes_text_frame.text = "\n".join(s["notes"])


def slide_title(prs, samples, s, base):
    slide, (title, _, sub) = new_slide(prs, samples["title"], [0, 1, 2])
    set_text(title, lines(s["title"]), {"line": paragraphs(title)[0]})
    set_text(sub, lines(t for _, t in s["body"]), {"line": paragraphs(sub)[0]})
    return slide


def slide_section(prs, samples, s, base):
    slide, (title, _) = new_slide(prs, samples["section"], [0, 1])
    set_text(title, lines(s["title"]), {"line": paragraphs(title)[0]})
    if s["body"]:
        # podtitulek ze vzoru titulního slajdu, pod linku mezislajdu
        sub = copy.deepcopy(samples["title"]["shapes"][2])
        slide.shapes._spTree.append(sub)
        slide.shapes[-1].top = Inches(SECTION_SUB_Y)
        set_text(sub, lines(t for _, t in s["body"]), {"line": paragraphs(sub)[0]})
    qr = next((a[3:] for a in s["args"] if a.startswith("qr=")), None)
    if qr:
        # světlé okraje kolem kódu, aby se dal načíst i z tmavého pozadí
        x, y, size = QR_BOX
        png = io.BytesIO()
        segno.make(qr, error="m").save(png, kind="png", scale=20, border=2, dark=NAVY, light="#FFFFFF")
        png.seek(0)
        slide.shapes.add_picture(png, Inches(x), Inches(y), Inches(size), Inches(size))
        if s["body"]:
            sub = next(sh for sh in slide.shapes if sh.top == Inches(SECTION_SUB_Y))
            sub.width = Inches(x - 0.2) - sub.left
    return slide


def slide_grid(prs, samples, s, base):
    slide, shapes = new_slide(prs, samples["grid"], [0, 1, 2, 3, 4, 5, 6, 7, 9, 10] + ([8] if s["banner"] else []))
    title = shapes[4]
    set_text(title, lines(s["title"]), {"line": paragraphs(title)[0]})
    if len(s["blocks"]) != 4:
        sys.exit(f"Slajd „{' '.join(s['title'])}“: mřížka potřebuje čtyři bloky, má {len(s['blocks'])}")
    for box, block in zip(shapes[6:10], s["blocks"]):
        set_text(box, [("line", block["head"])], {"line": paragraphs(box)[0]})
    if s["banner"]:
        set_text(shapes[10], lines(s["banner"]), {"line": paragraphs(shapes[10])[0]})
    return slide


def slide_table(prs, samples, s, base):
    slide, (title, _) = new_slide(prs, samples["bullets"], [0, 1])
    set_text(title, lines(s["title"]), {"line": paragraphs(title)[0]})
    table(slide, [[c.strip() for c in t.split("|")] for _, t in s["body"]])
    return slide


def slide_bullets(prs, samples, s, base):
    slide, (title, _, body) = new_slide(prs, samples["bullets"], [0, 1, 2])
    set_text(title, lines(s["title"]), {"line": paragraphs(title)[0]})
    set_text(body, s["body"], {"bullet": paragraphs(body)[0], "text": paragraphs(body)[0]})
    return slide


def slide_cards(prs, samples, s, base):
    slide, (card_light, card_dark, title, _, light, dark) = new_slide(prs, samples["cards"], [0, 1, 2, 3, 4, 5])
    new_cards = (card_light, card_dark)
    set_text(title, lines(s["title"]), {"line": paragraphs(title)[0]})
    text_samples = samples["cards_text"]["shapes"]
    for box, block, text_sample in zip((light, dark), s["blocks"], (text_samples[4], text_samples[5])):
        protos = {"head": paragraphs(box)[0], "bullet": paragraphs(box)[1],
                  "text": paragraphs(text_sample)[1]}
        set_text(box, [("head", block["head"])] + block["items"], protos)
    h = max(card_height(b) for b in s["blocks"])
    for sp in new_cards:
        set_height(sp, h)
    for sp in (light, dark):
        set_height(sp, h - CARD_TEXT_INSET)
    return slide


def slide_numbers(prs, samples, s, base):
    keep = [0, 1, 2, 3, 4, 5] + ([7, 8] if s["banner"] else [])
    slide, shapes = new_slide(prs, samples["numbers"], keep)
    title = shapes[0]
    set_text(title, lines(s["title"]), {"line": paragraphs(title)[0]})
    for (num, cap), block in zip(((shapes[2], shapes[3]), (shapes[4], shapes[5])), s["blocks"]):
        set_text(num, [("line", block["head"])], {"line": paragraphs(num)[0]})
        set_text(cap, [("line", t) for _, t in block["items"]], {"line": paragraphs(cap)[0]})
    if s["banner"]:
        set_text(shapes[7], lines(s["banner"]), {"line": paragraphs(shapes[7])[0]})
    return slide


def slide_image(prs, samples, s, base):
    slide, (title, _) = new_slide(prs, samples["bullets"], [0, 1])
    set_text(title, lines(s["title"]), {"line": paragraphs(title)[0]})
    src = next((a[4:] for a in s["args"] if a.startswith("src=")), None)
    if not src or not (base / src).is_file():
        sys.exit(f"Slajd „{' '.join(s['title'])}“: obrázek potřebuje argument src= s existující cestou vůči {base}, má {src!r}")
    # obrázek se vejde do plochy celý a stojí uprostřed její šířky
    x, y, w, h = IMAGE_BOX
    pic = slide.shapes.add_picture(str(base / src), Inches(x), Inches(y), width=Inches(w))
    if pic.height > Inches(h):
        pic.width = int(pic.width * Inches(h) / pic.height)
        pic.height = Inches(h)
    pic.left = Inches(x) + (Inches(w) - pic.width) // 2
    pic.line.color.rgb = rgb("#D5DCE4")
    pic.line.width = Pt(0.75)
    return slide


def slide_end(prs, samples, s, base):
    slide, (title, _, links) = new_slide(prs, samples["end"], [0, 1, 2])
    set_text(title, lines(s["title"]), {"line": paragraphs(title)[0]})
    set_text(links, lines(t for _, t in s["body"]), {"line": paragraphs(links)[0]})
    return slide


def slide_extension(prs, samples, s, base, kind):
    drawing = extension(base, kind)
    slide, (title, _) = new_slide(prs, samples["bullets"], [0, 1])
    set_text(title, lines(s["title"]), {"line": paragraphs(title)[0]})
    drawing.render(slide, s["args"])
    return slide


SLIDES = {
    "title": slide_title,
    "section": slide_section,
    "grid": slide_grid,
    "table": slide_table,
    "bullets": slide_bullets,
    "cards": slide_cards,
    "numbers": slide_numbers,
    "image": slide_image,
    "end": slide_end,
}


EXTENSIONS = {}


def extension(base, kind):
    """Modul s kresbou jedné prezentace: <typ>.py vedle zdroje s funkcí render(slide, args)."""
    path = base / f"{kind}.py"
    if not KIND.fullmatch(kind) or not path.is_file():
        sys.exit(f"Neznámý typ slajdu: {kind} – vestavěný to není a {path} neexistuje")
    if path not in EXTENSIONS:
        spec = importlib.util.spec_from_file_location(f"deck_{kind}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if not callable(getattr(module, "render", None)):
            sys.exit(f"{path}: chybí funkce render(slide, args)")
        EXTENSIONS[path] = module
    return EXTENSIONS[path]


def main():
    if len(sys.argv) not in (2, 3):
        sys.exit("Použití: uv run build.py <Prezentace.md> [<výstup>.pptx]")
    src = Path(sys.argv[1]).resolve()
    if not src.is_file():
        sys.exit(f"Zdroj prezentace neexistuje: {src}")
    if not TEMPLATE.is_file():
        sys.exit(f"Šablona neexistuje: {TEMPLATE}")
    base = src.parent
    out = Path(sys.argv[2]) if len(sys.argv) == 3 else base / f"{base.name}.pptx"
    prs = Presentation(TEMPLATE)
    samples = sample_shapes(prs)
    drop_all_slides(prs)
    for s in parse(src):
        render(prs, samples, s, base)
    prs.save(out)
    print(out)


if __name__ == "__main__":
    main()
