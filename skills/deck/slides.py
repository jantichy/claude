# Společná knihovna převodu obsahu na HTML slajdy decku na claude.ai – třídy jt-* ze stejného zdroje, ze kterého design.py vyrábí deck.css.
# Generátor decku se spouští přes python3 -I, takže si cestu sem přidává sám:
#   sys.path.insert(0, str(pathlib.Path.home() / '.claude/skills/deck')); from slides import *
# Grafy s měřítkem a popisky jednoho decku sem nepatří, zůstávají v jeho generátoru; patří sem jen to, co dostane všechno parametrem.
import re, html

SEP = "———"  # oddělovač řeči řečníka od zdroje v poznámkách slajdu

__all__ = [
    "SEP",
    "nb",
    "nb_text",
    "notes",
    "head",
    "ul",
    "bullets",
    "section",
    "table",
    "slide",
    "seg",
    "pair",
    "pair_abs",
]


# Nezlomitelné mezery v textu slajdu (~/Context/Text/typography.md, Mezery); nb() nechává značky HTML beze změny.
def nb_text(t):
    t = re.sub(
        r"(?<![\w])([kKsSvVzZoOuUaAiI]) ", "\\1\u00a0", t
    )  # jednopísmenné předložky a spojky
    t = re.sub(r"(\d) (?=\d{3}(?!\d))", "\\1\u00a0", t)  # řády
    t = re.sub(r"(\d\.) (?=\d)", "\\1\u00a0", t)  # data 2. 4. 2026
    t = re.sub(
        r"(\d) (?=[%‰]|Kč|mil\.|tis\.|px|s\b|dní|týdn|měsíc|zakáz|objedn|nákup|relac|prokl|verz|záznam|prohlíž|transakc|ze\b|z\b|proti\b)",
        "\\1\u00a0",
        t,
    )
    t = re.sub(r"(mil\.|tis\.) (?=Kč)", "\\1\u00a0", t)
    t = t.replace("→ ", "→\u00a0")  # šipka drží s následujícím slovem
    return t


def nb(html):
    parts = re.split(r"(<[^>]+>)", html)
    return "".join(p if p.startswith("<") else nb_text(p) for p in parts).replace(
        "\u00a0", "&nbsp;"
    )


# Kostra slajdu: poznámky řečníka, nadpis, odrážky a celé slajdy podle typu.
def notes(speaker, source, extra=""):
    t = (
        (speaker.strip() + "\n" if speaker else "")
        + SEP
        + "\nZdroj: "
        + source
        + (("\n" + extra) if extra else "")
    )
    return "<aside>" + html.escape(t, quote=False) + "</aside>"


def head(title):
    return (
        '<div class="jt-head">\n<h2 class="slide-title">'
        + nb(title).replace("\n", "<br>")
        + '</h2>\n</div>\n<div class="jt-rule"></div>\n'
    )


def ul(items, cls="jt-list list"):
    return (
        '<ul class="'
        + cls
        + '">\n'
        + "".join("<li>" + nb(i) + "</li>\n" for i in items)
        + "</ul>\n"
    )


def bullets(sid, title, items, speaker, source):
    return (
        f'<section id="{sid}" class="jt-slide">\n'
        + head(title)
        + '<div class="jt-body">\n'
        + ul(items)
        + "</div>\n"
        + notes(speaker, source)
        + "\n</section>\n"
    )


def section(sid, title, sub, note):
    return (
        f'<section id="{sid}" class="jt-slide is-dark jt-divider">\n<div class="jt-head">\n<h2 class="section-title">'
        + nb(title).replace("\n", "<br>")
        + '</h2>\n</div>\n<div class="jt-rule"></div>\n<p class="jt-sub subtitle">'
        + nb(sub)
        + "</p>\n<aside>"
        + html.escape(note, quote=False)
        + "</aside>\n</section>\n"
    )


def table(sid, title, header, rows, num_cols, speaker, source, first_w="980px"):
    def cell(tag, i, v, extra=""):
        cls = ' class="is-num"' if i in num_cols else ""
        st = f' style="width:{first_w}"' if (tag == "th" and i == 0) else ""
        return f"<{tag}{cls}{st}>{nb(v)}</{tag}>"

    t = (
        '<table class="jt-table">\n<tr>'
        + "".join(cell("th", i, v) for i, v in enumerate(header))
        + "</tr>\n"
    )
    for r in rows:
        t += (
            '<tr class="jt-row">'
            + "".join(cell("td", i, v) for i, v in enumerate(r))
            + "</tr>\n"
        )
    t += "</table>\n"
    return (
        f'<section id="{sid}" class="jt-slide">\n'
        + head(title)
        + '<div class="jt-body">\n'
        + t
        + "</div>\n"
        + notes(speaker, source)
        + "\n</section>\n"
    )


def slide(sid, title, body, speaker, source, extra=""):
    return (
        f'<section id="{sid}" class="jt-slide">\n'
        + head(title)
        + '<div class="jt-body">\n'
        + body
        + "</div>\n"
        + notes(speaker, source, extra)
        + "\n</section>\n"
    )


# Grafy z HTML bloků; výšku v px počítá volající z vlastního měřítka.
def seg(h, text, focus):
    cls = "jt-seg is-focus" if focus else "jt-seg"
    st = f"height:{h}px" + (
        "" if focus else ";background:var(--dim-line);color:var(--navy)"
    )
    return (
        f'<div class="{cls}" style="{st}"><p class="label">' + nb(text) + "</p></div>"
    )


def pair(cat, a, b, scale):
    ha, hb = round(a * scale), round(b * scale)
    fa, fb = f"{a:.1f}".replace(".", ","), f"{b:.1f}".replace(".", ",")
    return (
        '<div class="jt-group">'
        f'<div class="jt-col"><p class="label"><b>{fa}</b></p><div class="jt-bar" style="height:{ha}px"></div></div>'
        f'<div class="jt-col"><p class="label"><b>{fb}</b></p><div class="jt-bar is-focus" style="height:{hb}px"></div></div></div>\n'
    )


def pair_abs(a, b, scale, la, lb):
    return (
        '<div class="jt-group">'
        f'<div class="jt-col"><p class="label"><b>{nb(la)}</b></p><div class="jt-bar" style="height:{max(round(a * scale), 4)}px"></div></div>'
        f'<div class="jt-col"><p class="label"><b>{nb(lb)}</b></p><div class="jt-bar is-focus" style="height:{max(round(b * scale), 4)}px"></div></div></div>\n'
    )
