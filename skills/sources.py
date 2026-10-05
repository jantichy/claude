#!/usr/bin/env python3
"""Ověří, že citovaný zdroj jde přečíst a že na něm citovaný úryvek opravdu je.

Adresa, kterou vrátí model, je tvrzení, dokud se na stránku nepodívá něco, co
model není. Tenhle skript je to něco: stáhne syrové HTML, projde přesměrování,
zapíše, kam skončil, hledá v textu citovaný úryvek a roztřídí, co se vrátilo.
O významu nerozhoduje nikdy – ten zůstává modelu, a jen u zdroje, který skript
ohlásil jako přečtený.

**Proč skript, a ne model.** Paywall, přihlašovací stěna i měkká 404 odpovídají
HTTP 200 s vlastní stránkou. Model, který takovou stránku čte, pak tvrzení
prohlásí za nepodložené, přestože zdroj nikdo neviděl. Pevná sada pravidel je
levnější než volání modelu na každý odkaz a dává pokaždé stejnou odpověď.

**Co se počítá za přečtený text:** text stránky složený tak, jak ho vidí
čtenář (řádková značka jako `<b>` slovo nerozdělí), bez HTML komentářů,
`<script>`, `<style>`, `<template>`, `<noscript>` a `<head>` a bez všeho, co
skrývá samo značkování: atribut `hidden` (kromě `hidden="until-found"`, který
odhalí hledání na stránce), `aria-hidden="true"` a inline styl s `display:none`
nebo `visibility:hidden`. Syrové ani skryté značkování se nepočítá, takže
úryvek v komentáři nebo ve skrytém bloku není doklad, že se stránka přečetla.
Je to vytažení textu z HTML, ne prohlížeč: skrytí třídou ze stylopisu nebo
skriptem skript nevidí, takový text se počítá.

Verdikty (strojové identifikátory, proto anglicky):

- `REACHED` – stránka přečtena a úryvek na ní je doslova; nebo úryvek nebyl
  zadán a stránka má čitelný hlavní text. Binární obsah (PDF) je `REACHED`
  s `quote_found` null: dovnitř skript nevidí.
- `REACHED_QUOTE_FUZZY` – stránka přečtena, úryvek na ní doslova není, ale
  některá pasáž se mu blízce podobá (`FUZZY_THRESHOLD`): přeformátovaná nebo
  lehce parafrázovaná kopie. Nikdy se nehlásí jako přesná shoda.
- `REACHED_QUOTE_MISSING` – přečetla se celá stránka a úryvek v jejím
  čitelném textu není.
- `TRUNCATED` – přečetla se jen část (limit velikosti, času nebo dekomprese)
  a úryvek v ní není, takže jeho absence nic nedokazuje.
- `PAYWALLED` – `isAccessibleForFree` false v JSON-LD nebo mikrodatech,
  přesměrování na předplatné, nebo text, že článek je jen pro předplatitele.
- `LOGIN_WALL` – HTTP 401, přesměrování na přihlášení, nebo stránce
  dominuje přihlašovací formulář.
- `CONSENT_WALL` – přesměrování na souhlas s cookies, nebo krátká stránka,
  která je jen dialogem souhlasu.
- `SOFT_404` – hluboká adresa přesměrovaná na kořen webu nebo nadřazenou
  sekci, nebo stránka s HTTP 200, která říká „nenalezeno“.
- `BLOCKED` – HTTP 403 / 429 / 451 nebo stránka s ověřením proti robotům.
- `NO_CONTENT` – po odečtení navigace, hlavičky, patičky, skriptů a komentářů
  zbývá málo hlavního textu (obvykle stránka vykreslená JavaScriptem), nebo
  tělo v kódování, které skript neumí rozbalit.
- `UNREACHABLE` – síťová chyba, vypršený čas, 404, 410, 5xx, smyčka
  přesměrování, adresa, která není http(s), nebo adresa, kterou skript
  odmítá stáhnout (viz *Politika adres*).

Stránku znamenají přečtenou jen `REACHED`, `REACHED_QUOTE_FUZZY`
a `REACHED_QUOTE_MISSING`. Každý jiný verdikt je „neověřeno (důvod)“ a nikdy
se nesmí vydávat za „zdroj to neříká“.

Použití:

    sources.py --batch SOUBOR [--compact]

SOUBOR drží JSON pole `{"id": ..., "url": ..., "quote": ...}`. Adresa ani
text stránky nikdy nejdou na příkazovou řádku, kde shell spouští `$(...)`
a zpětné apostrofy i uvnitř uvozovek: pole se zapíše do souboru nástrojem
Write a skriptu se předá jen cesta. `-` čte pole ze stdin – pro program,
který ho posílá rourou (test, skript); z hlavní session se nepoužívá, protože
heredoc vrací text stránky zpátky na příkazovou řádku.

Přepínače:

- `--compact` – vypíše jen to, o čem rozhodl skript (`COMPACT_FIELDS`): žádný
  titulek stránky, žádný seznam přesměrování, nic jiného, co ovládá stránka.
  Jeden JSON objekt na řádek, v pořadí vstupu. Chrání kontext před textem
  stránky.
- `--timeout SEKUNDY` (výchozí 15), `--max-bytes N` (výchozí 2000000),
  `--workers N` (výchozí 8).
- `--allow-private` – povolí neveřejné adresy; potřebují ho testy nad
  `127.0.0.1`.

**Politika adres:** odmítá se každá adresa, která není veřejně směrovatelná
(loopback, privátní, link-local, CGNAT 100.64.0.0/10, kde žije tailnet
Tailscale, multicast, rezervované a IPv6 tvary, které některou z nich nesou),
a každé jméno `*.ts.net`. Kontrola běží uvnitř samotného spojení: socket se
připojí přesně na adresu, která prošla kontrolou, a to na každém skoku
přesměrování, zatímco hlavička Host a ověření TLS certifikátu drží jméno.
DNS odpověď, která se mezi dvěma dotazy změní (rebinding), tak na vnitřní
službu nedosáhne. Proxy z prostředí se ze stejného důvodu ignoruje.

Výstup je JSON na stdout: pole v pořadí vstupu, s `--compact` JSON Lines.
Návratový kód: 0, kdykoliv kontrola proběhla, ať jsou verdikty jakékoliv;
2 chyba volání nebo nečitelný vstup. Jen standardní knihovna.

Přepsáno z `check_source.py` v repozitáři hradniai/claude-starter-pack
(licence MIT).
"""

import argparse
import html
import http.client
import http.cookiejar
import ipaddress
import json
import re
import socket
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import zlib
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from difflib import SequenceMatcher
from heapq import nlargest
from html.parser import HTMLParser

VERDICTS = (
    "REACHED",
    "REACHED_QUOTE_FUZZY",
    "REACHED_QUOTE_MISSING",
    "TRUNCATED",
    "PAYWALLED",
    "LOGIN_WALL",
    "CONSENT_WALL",
    "SOFT_404",
    "BLOCKED",
    "NO_CONTENT",
    "UNREACHABLE",
)
READ_VERDICTS = ("REACHED", "REACHED_QUOTE_FUZZY", "REACHED_QUOTE_MISSING")

DEFAULT_TIMEOUT = 15.0
DEFAULT_MAX_BYTES = 2_000_000
DEFAULT_WORKERS = 8
MAX_REDIRECTS = 10
MAX_META_REFRESH = 2
# Prostý text kratší než tohle se počítá za prázdný.
MIN_CONTENT_CHARS = 50
# HTML stránka, jejíž hlavní text (bez navigace, hlavičky, patičky a postranních
# panelů) je kratší, se nepřečetla: javascriptová skořápka typicky servíruje menu,
# patičku a prázdný kořenový div.
MIN_MAIN_CHARS = 200
# Přihlašovací formulář na stránce kratší než tohle ji ovládá; na delší je to
# widget v hlavičce.
LOGIN_PAGE_MAX_CHARS = 1500
# Dialog souhlasu je celou stránkou jen tehdy, když je hlavní text takhle krátký.
CONSENT_PAGE_MAX_CHARS = 1500
# Titulek „nenalezeno“ platí jen na takhle krátké stránce, nebo když totéž říká h1.
NOT_FOUND_PAGE_MAX_CHARS = 3000
# Přibližná shoda. Každý úsek úryvku se zarovná v pořadí slov proti nejlepšímu
# oknu stránky a dostane skóre 2 * shodná_slova / (slova_úryvku + slova_okna).
# 0,85 pustí jedno změněné slovo ze sedmi (0,857) a zastaví dvě z deseti (0,80):
# snese přeformátovanou nebo lehce parafrázovanou kopii a zastaví jinou větu na
# stejné téma. Úseky kratší než FUZZY_MIN_WORDS slov platí jen celé a v pořadí.
FUZZY_THRESHOLD = 0.85
FUZZY_MIN_WORDS = 6
FUZZY_CANDIDATES = 10
READ_CHUNK = 65536

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0 Safari/537.36"
)
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en;q=0.9,*;q=0.5",
    "Accept-Encoding": "gzip, deflate",
}

TEXT_TYPES = (
    "text/",
    "application/json",
    "application/xml",
    "application/xhtml+xml",
    "application/rss+xml",
    "application/atom+xml",
    "application/ld+json",
)

LOGIN_SEGMENTS = {
    "login",
    "log-in",
    "logon",
    "signin",
    "sign-in",
    "sign_in",
    "signon",
    "sso",
    "auth",
    "authenticate",
    "authorize",
    "oauth",
    "oauth2",
    "authwall",
    "wp-login.php",
    "uas",
}
LOGIN_HOST_LABELS = {"login", "signin", "auth", "sso", "accounts", "idp"}
PAYWALL_SEGMENTS = {"subscribe", "subscription", "subscriptions", "paywall", "premium"}
CONSENT_HOST_LABELS = {"consent", "cmp", "guce", "myprivacy"}
CONSENT_SEGMENTS = {
    "consent",
    "cookie-consent",
    "cookies-consent",
    "privacy-consent",
    "gdpr-consent",
    "collectconsent",
    "cookiewall",
    "cookie-wall",
    "nastaveni-souhlasu",
    "souhlas",
}
NOT_FOUND_SEGMENTS = {
    "404",
    "404.html",
    "404.php",
    "not-found",
    "notfound",
    "page-not-found",
    "pagenotfound",
    "error-404",
}
ROOT_LIKE_SEGMENTS = {"index.html", "index.htm", "index.php", "home", "default.aspx"}
# Koncový segment, který jmenuje tutéž stránku v jiné podobě: /x/index.html je /x/,
# /x/amp je /x.
SAME_PAGE_TAILS = {"index.html", "index.htm", "index.php", "default.aspx", "amp"}
# Jazykový kořen jako /en/ nebo /cs-cz/ je taky kořen webu. Uzavřený seznam, protože
# holý dvoupísmenný vzor by spolkl i skutečné sekce jako /ai/ nebo /go/.
LANGUAGES = {
    "en", "cs", "sk", "de", "fr", "es", "it", "pl", "pt", "nl", "ru", "uk", "ja", "zh",
    "ko", "sv", "da", "fi", "nb", "hu", "ro", "tr", "el", "he", "ar", "bg", "hr", "sl",
}  # fmt: skip
LOCALE_SEGMENT = re.compile(r"^(" + "|".join(sorted(LANGUAGES)) + r")([-_][a-z]{2})?$")

# Úsek titulku, který JE výzvou k přihlášení („Sign in - Portal“, „Log in or sign
# up“), porovnávaný nad složeným textem (bez velikosti písmen a diakritiky).
# Titulek, který přihlášení jen zmiňuje („Sign in with passkeys: a guide“), je
# článek o něm a nepočítá se.
LOGIN_TITLE_SEGMENT = re.compile(
    r"^(please )?(log ?in|sign ?in|signin|login|log on|anmelden|connexion|iniciar sesion|"
    r"prihlaseni|prihlasit se|prihlaste se)( (or|and|to|with your) .{0,40})?$"
)
TITLE_SEPARATORS = re.compile(r"\s[-|:·–]\s|\s?[|·]\s?")
NOT_FOUND_TEXT = re.compile(
    r"(^\s*(error\s*)?404\b|\bpage not found\b|^\s*not found\b|\bnot found\s*$|"
    r"\b(page|article|post|file)\b[^.]{0,40}\b(does not|doesn\'t|could not|couldn\'t|cannot|can\'t) "
    r"(exist|be found)|nenalezen|stránka neexistuje|nicht gefunden|introuvable|no encontrada|"
    r"non trovata|nie znaleziono)",
    re.I,
)
CHALLENGE_TITLE = re.compile(
    r"(just a moment|attention required|access denied|security check|checking your browser|"
    r"ddos-guard|robot check|are you a robot|verifying you are human|human verification|"
    r"pardon our interruption|request blocked|you have been blocked|bot verification|captcha|"
    r"access to this page has been denied|^\s*403 forbidden)",
    re.I,
)
CHALLENGE_MARKERS = (
    "cf_chl_opt",
    "cf-browser-verification",
    "_incapsula_resource",
    "px-captcha",
    "ddos-guard",
    "captcha-delivery.com",
)
ACCESS_FALSE = re.compile(r'"isAccessibleForFree"\s*:\s*"?(false|no)"?', re.I)

# Hlášky paywallu nad složeným textem stránky (bez velikosti písmen a diakritiky).
# Každá je zněním stěny, ne propagace, protože zásah mění „úryvek chybí“
# na „neověřeno“.
PAYWALL_TEXT = re.compile(
    "|".join(
        [
            r"\bsubscribe (now )?to (continue|keep) reading\b",
            r"\bsubscribe to (read|unlock|access) (the |this )?(full |whole |rest of the )?(article|story|post)\b",
            r"\b(this|the) (article|story|content|post) is (only )?(available )?(for|to) (paying |paid )?"
            r"(subscribers|members)\b",
            r"\bto (continue|keep) reading,? (please )?(subscribe|become a (paid )?(subscriber|member))\b",
            r"\byou('ve| have) (reached|used) (your|all your|the) (free article|article|monthly) limit",
            r"\byou('ve| have) (reached|used) (your|all your) free articles\b",
            r"\b(create|register for) a free account to (continue|keep) reading\b",
            r"\bthe rest of (this|the) (article|story) is (available|reserved) (only )?(for|to) (subscribers|members)\b",
            r"\bunlock (this|the full) (article|story)\b",
            r"\b(clanek|obsah|text|cely clanek) je (dostupny|urcen|k dispozici) (pouze|jen|vyhradne) (pro|predplatitelum)\b",
            r"\b(pouze|jen|vyhradne) pro predplatitele\b",
            r"\bcely (clanek|text) (si )?(prectete|ctete|je dostupny)\b.{0,40}\bpredplat",
            r"\b(zbytek|zbyvajici cast|pokracovani) (clanku|textu)\b.{0,40}\b(predplat|premium)",
            r"\bpro (dalsi |pokracovani ve )?cteni (se )?(prihlaste|si kupte|si predplat|kupte si)",
            r"\bodemknete si (cely )?(clanek|text)\b",
        ]
    )
)
# Znění dialogu souhlasu nad složeným textem krátké stránky. Potřeba jsou dva
# různé zásahy, protože jeden řádek o cookies stojí i na běžných stránkách.
CONSENT_TEXT = [
    re.compile(p)
    for p in (
        r"\b(accept|reject|allow|refuse|decline) all( cookies)?\b",
        r"\bmanage (cookie |privacy |your )?(preferences|settings|options|choices)\b",
        r"\bwe (and our (\d+ )?(partners|vendors) )?(use|store|process) cookies\b",
        r"\bbefore you continue\b",
        r"\byour privacy choices\b",
        r"\bpart of the \w+ family of brands\b",
        r"\b(prijmout|odmitnout|povolit) vse\b",
        r"\bnastaveni (souhlasu|cookies|soukromi)\b",
        r"\bsouhlas(im| s (pouzitim|vyuzitim|zpracovanim))\b",
        r"\b(pouzivame|vyuzivame|potrebujeme) (soubory |vas souhlas s vyuzitim )?cookies\b",
        r"\bnez budete pokracovat\b",
    )
]

SKIP_TEXT_TAGS = {
    "script",
    "style",
    "noscript",
    "template",
    "svg",
    "head",
    "iframe",
    "object",
}
# Inline styl, který prvek skryje, porovnávaný bez bílých znaků a malými písmeny,
# takže „Display : None !important“ platí; sedí jen celá deklarace, nikdy delší
# jméno vlastnosti.
HIDING_STYLE = re.compile(r"(^|;)(display:none|visibility:hidden)(!important)?(;|$)")
VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param",
    "source", "track", "wbr",
}  # fmt: skip
# Značky, které nerozdělí slovo: „<b>A</b>I“ se čte „AI“. Každá jiná začne nové slovo.
INLINE_TAGS = {
    "a", "abbr", "b", "bdi", "bdo", "cite", "code", "data", "del", "dfn", "em", "font",
    "i", "img", "ins", "kbd", "label", "mark", "q", "rp", "rt", "ruby", "s", "samp",
    "small", "span", "strike", "strong", "sub", "sup", "time", "tt", "u", "var", "wbr",
}  # fmt: skip
# Vybavení stránky: vypadává z míry hlavního textu (nikdy z textu, kde se hledá úryvek).
BOILERPLATE_TAGS = {"nav", "header", "footer", "aside"}
BOILERPLATE_ROLES = {"navigation", "banner", "contentinfo", "complementary", "search"}
BOILERPLATE_NAMES = {
    "nav",
    "navbar",
    "navigation",
    "menu",
    "header",
    "site-header",
    "footer",
    "site-footer",
    "masthead",
    "sidebar",
    "breadcrumb",
    "breadcrumbs",
    "cookie-banner",
    "cookie-consent",
}
# Uvnitř <article> nebo <main> zůstávají hlavička i patička jejich: bydlí tam
# titulek a autor.
CONTENT_TAGS = ("article", "main")

DASHES = dict.fromkeys(map(ord, "‐‑‒–—―−"), "-")
QUOTES = {
    ord("‘"): "'",
    ord("’"): "'",
    ord("‚"): "'",
    ord("‛"): "'",
    ord("“"): '"',
    ord("”"): '"',
    ord("„"): '"',
    ord("‟"): '"',
    ord("«"): '"',
    ord("»"): '"',
    ord("‹"): "'",
    ord("›"): "'",
}
# Měkké dělení, nulová mezera, nespojovač, spojovač, word joiner, BOM.
INVISIBLE = dict.fromkeys(map(ord, "­​‌‍⁠﻿"), None)
# Markdown, který přidá nástroj převádějící stránku na text: zvýraznění, kód, odkazy.
MARKDOWN_MARKS = dict.fromkeys(map(ord, "*`_"), None)
MARKDOWN_LINK = re.compile(r"!?\[([^\]]*)\]\([^)\s]*\)")
MARKDOWN_BLOCK = re.compile(r"^\s*(#{1,6}|>|[-+*]|\d+[.)])\s+")
WORD = re.compile(r"\w+")

NAT64 = ipaddress.ip_network("64:ff9b::/96")

COMPACT_FIELDS = (
    "id",
    "url",
    "final_url",
    "verdict",
    "reason",
    "http_status",
    "quote_found",
    "quote_match",
    "quote_similarity",
    "truncated",
    "signals",
)


class RefusedAddress(Exception):
    """Adresa se jmenuje nebo překládá na adresu, kterou skript nestáhne."""


# ---- čtení HTML ---------------------------------------------------------------


class PageParser(HTMLParser):
    """Sbírá těch pár věcí, které potřebuje třídění, a nic jiného.

    Otevřené značky se počítají v `Counter`, ne hledáním v zásobníku: nepárová
    koncová značka by jinak procházela celý zásobník a stránka se statisíci
    neuzavřených `<div>` by třídění zasekla v kvadratickém čase – za časovým
    limitem stahování, který na rozbor už nedosáhne.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.h1 = []
        self.text = []
        self.main = []
        self.ld_json = []
        self.meta = []
        self.canonical = ""
        self.refresh = ""
        self.password_inputs = 0
        self._stack = []  # (značka, skrývá text, je vybavení stránky)
        self._open = Counter()
        self._skip = 0
        self._boiler = 0
        self._capture = None  # "title", "h1", "ld" nebo None
        self._buffer = []

    def _break(self):
        if not self._skip:
            self.text.append(" ")
            self.main.append(" ")

    def _is_boilerplate(self, tag, attrs):
        if tag in ("header", "footer"):
            return not any(self._open[t] for t in CONTENT_TAGS)
        if (
            tag in BOILERPLATE_TAGS
            or attrs.get("role", "").lower() in BOILERPLATE_ROLES
        ):
            return True
        names = set(attrs.get("class", "").lower().split()) | {
            attrs.get("id", "").lower()
        }
        return bool(names & BOILERPLATE_NAMES)

    @staticmethod
    def _is_hidden(attrs):
        """Prvek před čtenářem skrývá samo značkování."""
        if "hidden" in attrs and attrs["hidden"].strip().lower() != "until-found":
            return True
        if attrs.get("aria-hidden", "").strip().lower() == "true":
            return True
        style = "".join(attrs.get("style", "").lower().split())
        return bool(HIDING_STYLE.search(style))

    def _collect(self, tag, attrs):
        """Metadata, která rozhodují o stěnách: meta, kanonická adresa, heslo."""
        if tag == "meta":
            self.meta.append(attrs)
            if attrs.get("http-equiv", "").lower() == "refresh":
                self.refresh = attrs.get("content", "")
        elif tag == "link" and "canonical" in attrs.get("rel", "").lower().split():
            self.canonical = attrs.get("href", "")
        elif tag == "input" and attrs.get("type", "").lower() == "password":
            self.password_inputs += 1

    def _start_capture(self, tag, attrs):
        if tag == "title" and not self.title:
            self._capture = "title"
        elif tag == "h1":
            self._capture = "h1"
        elif tag == "script" and "ld+json" in attrs.get("type", "").lower():
            self._capture = "ld"
        else:
            return
        self._buffer = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        attrs = {k.lower(): (v or "") for k, v in attrs}
        self._collect(tag, attrs)
        if tag not in INLINE_TAGS:
            self._break()
        if tag in VOID_TAGS:
            return
        skip = tag in SKIP_TEXT_TAGS or self._is_hidden(attrs)
        boiler = self._is_boilerplate(tag, attrs)
        self._stack.append((tag, skip, boiler))
        self._open[tag] += 1
        self._skip += skip
        self._boiler += boiler
        self._start_capture(tag, attrs)

    def _end_capture(self, tag):
        captured = " ".join("".join(self._buffer).split())
        if tag == "title" and self._capture == "title":
            self.title = captured
        elif tag == "h1" and self._capture == "h1":
            self.h1.append(captured)
        elif tag == "script" and self._capture == "ld":
            self.ld_json.append("".join(self._buffer))
        else:
            return
        self._capture = None

    def _close(self, tag):
        """Zavře značku i všechny neuzavřené uvnitř ní; nepárovou přeskočí."""
        if not self._open[tag]:
            return
        while self._stack:
            popped, skip, boiler = self._stack.pop()
            self._open[popped] -= 1
            self._skip -= skip
            self._boiler -= boiler
            if popped == tag:
                break

    def handle_endtag(self, tag):
        tag = tag.lower()
        self._end_capture(tag)
        self._close(tag)
        if tag not in INLINE_TAGS:
            self._break()

    def handle_data(self, data):
        if self._capture:
            self._buffer.append(data)
        if self._capture in ("title", "ld") or self._skip:
            return
        self.text.append(data)
        if not self._boiler:
            self.main.append(data)

    def visible_text(self):
        return " ".join("".join(self.text).split())

    def main_text(self):
        return " ".join("".join(self.main).split())


# ---- porovnání úryvku -----------------------------------------------------------


def normalize(text):
    """Srovná rozdíly, které si zkopírovaný úryvek nabere: entity, neviditelné
    znaky, velikost písmen, uvozovky, pomlčky, mezery a markdown z nástroje."""
    text = html.unescape(text or "").translate(INVISIBLE)
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(DASHES).translate(QUOTES).replace("…", "...")
    text = MARKDOWN_LINK.sub(r"\1", text).translate(MARKDOWN_MARKS)
    return " ".join(text.casefold().split())


def fold(text):
    """`normalize` a k tomu bez diakritiky: na pevné fráze, nikdy na úryvky."""
    decomposed = unicodedata.normalize("NFKD", normalize(text))
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def quote_fragments(quote):
    """Úryvek s výpustkou je několik úseků, které musí být všechny, a v pořadí."""
    normalized = normalize(MARKDOWN_BLOCK.sub("", quote or "")).strip("\"' ")
    parts = [p.strip("\"' ") for p in re.split(r"\[?\.\.\.\]?", normalized)]
    return [p for p in parts if len(p) >= 3]


def quote_present(quote, haystacks):
    """True, když jsou všechny úseky v některém textu doslova a v pořadí."""
    fragments = quote_fragments(quote)
    if not fragments:
        return None
    return any(_fragments_in_order(fragments, hay) for hay in haystacks)


def _fragments_in_order(fragments, hay):
    position = 0
    for fragment in fragments:
        found = hay.find(fragment, position)
        if found < 0:
            return False
        position = found + len(fragment)
    return True


def _find_words(words, page, start):
    first = words[0]
    for i in range(start, len(page) - len(words) + 1):
        if page[i] == first and page[i : i + len(words)] == words:
            return i
    return -1


def _window_candidates(words, page, start):
    """Začátky oken délky úryvku, která s ním sdílí aspoň 60 % slov."""
    n = len(words)
    need = Counter(words)
    window = Counter(w for w in page[start : start + n] if w in need)
    overlap = sum(min(c, window[w]) for w, c in need.items())
    floor = max(1, int(0.6 * n))
    candidates = [(overlap, start)] if overlap >= floor else []
    for i in range(start + 1, len(page) - n + 1):
        out, inn = page[i - 1], page[i + n - 1]
        if out in need:
            overlap -= window[out] <= need[out]
            window[out] -= 1
        if inn in need:
            overlap += window[inn] < need[inn]
            window[inn] += 1
        if overlap >= floor:
            candidates.append((overlap, i))
    return candidates


def _score_window(words, page, lo, hi):
    """Skóre zarovnání úryvku v pořadí proti page[lo:hi], jako (skóre, konec)."""
    matcher = SequenceMatcher(None, words, page[lo:hi], autojunk=False)
    blocks = [b for b in matcher.get_matching_blocks() if b.size]
    if not blocks:
        return 0.0, lo
    matched = sum(b.size for b in blocks)
    span = blocks[-1].b + blocks[-1].size - blocks[0].b
    return 2 * matched / (len(words) + span), lo + blocks[-1].b + blocks[-1].size


def _best_window(words, page, start):
    """Nejlepší zarovnání slov v pořadí proti oknu page[start:], jako (skóre, konec)."""
    n = len(words)
    if len(page) - start < 1:
        return 0.0, start
    slack = max(2, n // 4)
    best = (0.0, start)
    for _overlap, i in nlargest(
        FUZZY_CANDIDATES, _window_candidates(words, page, start)
    ):
        lo = max(start, i - slack)
        score = _score_window(words, page, lo, i + n + slack)
        if score[0] > best[0]:
            best = score
    return best


def fuzzy_similarity(quote, haystack):
    """0..1: skóre nejslabšího úseku, úseky v pořadí. None, když úryvek nemá
    použitelný úsek."""
    fragments = quote_fragments(quote)
    if not fragments:
        return None
    page = WORD.findall(haystack)
    position = 0
    scores = []
    for fragment in fragments:
        words = WORD.findall(fragment)
        if not words:
            continue
        if len(words) < FUZZY_MIN_WORDS:
            found = _find_words(words, page, position)
            if found < 0:
                return 0.0
            scores.append(1.0)
            position = found + len(words)
            continue
        score, position = _best_window(words, page, position)
        scores.append(score)
    return round(min(scores), 3) if scores else None


# ---- politika adres -------------------------------------------------------------


def _embedded_ipv4(address):
    if address.version != 6:
        return []
    inner = [a for a in (address.ipv4_mapped, address.sixtofour) if a]
    if address.teredo:
        inner.extend(address.teredo)
    if address in NAT64:
        inner.append(ipaddress.IPv4Address(int(address) & 0xFFFFFFFF))
    return inner


def _not_public(address):
    return any(
        (
            not address.is_global,
            address.is_private,
            address.is_loopback,
            address.is_link_local,
            address.is_multicast,
            address.is_reserved,
            address.is_unspecified,
        )
    )


def address_refused(ip_text):
    """True pro každou adresu, která není veřejně směrovatelná, i pro IPv6 tvar,
    který takovou nese."""
    address = ipaddress.ip_address(str(ip_text).split("%")[0])
    return any(_not_public(a) for a in [address] + _embedded_ipv4(address))


def host_refused(host):
    name = (host or "").lower().rstrip(".")
    return name == "ts.net" or name.endswith(".ts.net")


def _shown_host(host):
    """Jméno hostitele do hlášky: z přesměrování ho určuje stránka, takže bez mezer."""
    return urllib.parse.quote(str(host)[:100], safe=".-:[]")


def resolve_checked(host, port, allow_private):
    """Přeloží jméno jednou a ověří každou odpověď. Volající se připojí jen na to,
    co vrátí tahle funkce."""
    if not allow_private and host_refused(host):
        raise RefusedAddress(f"odmítnuto: {_shown_host(host)} je jméno v tailnetu")
    infos = socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM)
    if not allow_private and any(address_refused(info[4][0]) for info in infos):
        raise RefusedAddress(
            f"odmítnuto: {_shown_host(host)} se překládá na privátní nebo místní "
            "(neveřejnou) adresu"
        )
    return infos


def open_pinned_socket(address, timeout, source_address, allow_private):
    """Jako `socket.create_connection`, jenže se připojí na adresy, které právě
    ověřila, a jméno podruhé nepřekládá."""
    host, port = address
    error = None
    for family, socktype, proto, _canonical, sockaddr in resolve_checked(
        host, port, allow_private
    ):
        sock = socket.socket(family, socktype, proto)
        try:
            if isinstance(timeout, (int, float)):
                sock.settimeout(timeout)
            if source_address:
                sock.bind(source_address)
            sock.connect(sockaddr)
            return sock
        except OSError as exc:
            error = exc
            sock.close()
    raise error or OSError(f"pro {_shown_host(host)} se nenašla žádná adresa")


class PinnedHTTPConnection(http.client.HTTPConnection):
    def __init__(self, *args, allow_private=False, **kwargs):
        super().__init__(*args, **kwargs)
        self._create_connection = lambda address, timeout=None, source_address=None: (
            open_pinned_socket(address, timeout, source_address, allow_private)
        )


class PinnedHTTPSConnection(http.client.HTTPSConnection):
    # HTTPSConnection.connect obalí připnutý socket s server_hostname=self.host,
    # takže SNI i ověření certifikátu dál používají jméno, ne připnutou adresu.
    def __init__(self, *args, allow_private=False, **kwargs):
        super().__init__(*args, **kwargs)
        self._create_connection = lambda address, timeout=None, source_address=None: (
            open_pinned_socket(address, timeout, source_address, allow_private)
        )


class PinnedHTTPHandler(urllib.request.HTTPHandler):
    def __init__(self, allow_private):
        super().__init__()
        self._allow_private = allow_private

    def http_open(self, req):
        return self.do_open(
            PinnedHTTPConnection, req, allow_private=self._allow_private
        )


class PinnedHTTPSHandler(urllib.request.HTTPSHandler):
    def __init__(self, allow_private):
        super().__init__()
        self._allow_private = allow_private

    def https_open(self, req):
        return self.do_open(
            PinnedHTTPSConnection,
            req,
            context=self._context,
            allow_private=self._allow_private,
        )


def check_address(url, allow_private):
    """Levná odmítnutí bez DNS: schéma a jména v tailnetu. Adresy se ověřují tam,
    kde se socket připojuje (`open_pinned_socket`), na každém skoku."""
    parts = urllib.parse.urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        raise RefusedAddress(f"není to http(s) adresa: {safe_url(url, 200)}")
    if not allow_private and host_refused(parts.hostname):
        raise RefusedAddress(
            f"odmítnuto: {_shown_host(parts.hostname)} je jméno v tailnetu"
        )


def make_opener(hops, allow_private):
    class RecordingRedirect(urllib.request.HTTPRedirectHandler):
        max_redirections = MAX_REDIRECTS

        def http_error_302(self, req, fp, code, msg, headers):
            # urllib cíl s jiným schématem (javascript:, file:) odmítne vlastní
            # HTTPError 3xx ještě před redirect_request, a ta by se pak vydávala
            # za smyčku přesměrování. Proto se cíl kontroluje už tady.
            target = headers.get("location") or headers.get("uri")
            if target:
                check_address(urllib.parse.urljoin(req.full_url, target), allow_private)
            return super().http_error_302(req, fp, code, msg, headers)

        http_error_301 = http_error_303 = http_error_307 = http_error_308 = (
            http_error_302
        )

        def redirect_request(self, req, fp, code, msg, headers, newurl):
            check_address(newurl, allow_private)
            hops.append(newurl)
            return super().redirect_request(req, fp, code, msg, headers, newurl)

    return urllib.request.build_opener(
        urllib.request.ProxyHandler({}),
        PinnedHTTPHandler(allow_private),
        PinnedHTTPSHandler(allow_private),
        RecordingRedirect(),
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()),
    )


# ---- stažení ----------------------------------------------------------------------


def read_capped(response, max_bytes, deadline):
    """Čte tělo do limitu velikosti a času. Vrátí (bajty, uříznuto).

    Čte se po `read1`, ne `read(n)`: `read(n)` čeká, dokud nemá celých n bajtů,
    a server, který posílá bajt těsně pod časovým limitem socketu, by ho držel
    hodiny. `read1` vrátí, co právě přišlo, takže se celkový limit kontroluje
    po každém kousku.
    """
    reader = getattr(response, "read1", None) or response.read
    chunks = []
    total = 0
    while True:
        if time.monotonic() > deadline:
            return b"".join(chunks)[:max_bytes], True
        chunk = reader(READ_CHUNK)
        if not chunk:
            return b"".join(chunks), False
        chunks.append(chunk)
        total += len(chunk)
        if total > max_bytes:
            return b"".join(chunks)[:max_bytes], True


def _inflate(raw, encoding, max_bytes):
    """Rozbalí gzip nebo deflate. Vrátí (bajty, uříznuto, selhalo)."""
    encoding = (encoding or "").lower().strip()
    if encoding in ("", "identity"):
        return raw, False, False
    if encoding not in ("gzip", "x-gzip", "deflate"):
        return raw, False, True  # br, zstd a další se nežádaly a číst je tu nejde
    # MAX_WBITS | 32 bere hlavičku gzip i zlib; některé servery posílají holý
    # deflate, proto druhý pokus. max_length omezuje dekompresní bombu.
    for wbits in (zlib.MAX_WBITS | 32, -zlib.MAX_WBITS):
        try:
            inflater = zlib.decompressobj(wbits)
            out = inflater.decompress(raw, max_bytes)
        except zlib.error:
            continue
        truncated = bool(inflater.unconsumed_tail) or (
            len(out) >= max_bytes and not inflater.eof
        )
        return out, truncated, False
    return raw, False, True


def _charset(raw, content_type):
    match = re.search(r"charset=([\w-]+)", content_type or "", re.I)
    if match:
        return match.group(1)
    sniff = re.search(rb"<meta[^>]+charset=[\"']?([\w-]+)", raw[:4096], re.I)
    return sniff.group(1).decode("ascii", "ignore") if sniff else ""


def decode_body(raw, encoding, content_type, max_bytes):
    """Vrátí (text, uříznuto, selhalo). Uříznuto: dekomprese skončila na max_bytes,
    text je jen začátek. Selhalo: kódování obsahu, které skript nerozbalí, text je šum."""
    raw, truncated, failed = _inflate(raw, encoding, max_bytes)
    try:
        text = raw.decode(_charset(raw, content_type) or "utf-8", errors="replace")
    except LookupError:
        text = raw.decode("utf-8", errors="replace")
    return text, truncated, failed


# Chyby, které z jednoho stažení dělají UNREACHABLE. `http.client.HTTPException`
# v nich být musí: `BadStatusLine`, `LineTooLong` ani `IncompleteRead` nejsou
# `OSError`, a bez ní by jedna rozbitá odpověď shodila celou dávku.
FETCH_ERRORS = (
    urllib.error.URLError,
    socket.timeout,
    TimeoutError,
    ConnectionError,
    OSError,
    ValueError,
)


def _store_response(response, result, max_bytes, deadline):
    try:
        raw, truncated = read_capped(response, max_bytes, deadline)
    except AttributeError:
        raw, truncated = b"", False  # HTTPError bez těla
    finally:
        response.close()
    headers = response.headers or {}
    result["http_status"] = response.getcode()
    result["final_url"] = response.geturl() or result["final_url"]
    result["content_type"] = headers.get("Content-Type", "") or ""
    result["bytes_read"] += len(raw)
    body, decode_truncated, decode_failed = decode_body(
        raw, headers.get("Content-Encoding", ""), result["content_type"], max_bytes
    )
    result["truncated"] = truncated or decode_truncated
    result["decode_failed"] = decode_failed
    result["body"] = body


def _open_and_read(current, result, hops, limits):
    """Jedno GET s přesměrováními. True, když se odpověď přečetla."""
    timeout, max_bytes, allow_private, deadline = limits
    check_address(current, allow_private)
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise socket.timeout("timed out (celkový časový limit)")
    opener = make_opener(hops, allow_private)
    request = urllib.request.Request(current, headers=HEADERS)
    try:
        response = opener.open(request, timeout=min(timeout, remaining))
    except urllib.error.HTTPError as error:
        if not 300 <= error.code < 400:
            response = (
                error  # 4xx/5xx je taky odpověď; podle těla se pozná ověření robotů
            )
        else:
            # urllib vyhodí 3xx, jen když přestane sledovat: smyčka nebo moc skoků.
            error.close()
            result["http_status"] = error.code
            result["error"] = (
                f"HTTP {error.code}: smyčka přesměrování nebo víc než "
                f"{MAX_REDIRECTS} přesměrování"
            )
            return False
    result["final_url"] = current
    _store_response(response, result, max_bytes, deadline)
    return True


def _fetch_hop(current, result, limits):
    """Jeden průchod včetně přesměrování; chyby zapíše do result. True = přečteno."""
    hops = []
    try:
        return _open_and_read(current, result, hops, limits)
    except RefusedAddress as error:
        result["error"] = str(error)
    except http.client.HTTPException as error:
        # Text výjimky nese, co poslal server, takže do hlášky jde jen její typ.
        result["error"] = f"nečitelná odpověď serveru ({type(error).__name__})"
    except FETCH_ERRORS as error:
        reason = getattr(error, "reason", error)
        result["error"] = f"{type(error).__name__}: {reason}"[:300]
    finally:
        result["redirects"].extend(hops)
    return False


def fetch(url, timeout, max_bytes, allow_private):
    """Jedno GET s přesměrováními a nanejvýš dvěma meta refreshi. Nikdy nevyhodí."""
    result = {
        "url": url,
        "final_url": url,
        "http_status": None,
        "redirects": [],
        "error": None,
        "content_type": "",
        "body": "",
        "bytes_read": 0,
        "truncated": False,
        "meta_refresh": False,
        "decode_failed": False,
    }
    limits = (timeout, max_bytes, allow_private, time.monotonic() + timeout * 3)
    current = url
    for _refresh in range(MAX_META_REFRESH + 1):
        if not _fetch_hop(current, result, limits):
            return result
        refresh = meta_refresh_target(result)
        status = result["http_status"]
        if not refresh or status is None or not 200 <= status < 300:
            return result
        current = urllib.parse.urljoin(result["final_url"], refresh)
        result["redirects"].append(current)
        result["meta_refresh"] = True
    return result


def meta_refresh_target(result):
    body = result["body"]
    if "html" not in result["content_type"].lower() and not body.lstrip().startswith(
        "<"
    ):
        return ""
    match = re.search(
        r"<meta[^>]+http-equiv=[\"']?refresh[\"']?[^>]*>", body[:20000], re.I
    )
    if not match:
        return ""
    content = re.search(
        r"content=[\"']?\s*(\d+)\s*;\s*url\s*=\s*[\"']?([^\"'>]+)", match.group(0), re.I
    )
    if not content or int(content.group(1)) > 10:
        return ""
    return content.group(2).strip()


# ---- třídění ----------------------------------------------------------------------


def path_segments(url):
    return [s for s in urllib.parse.urlsplit(url).path.lower().split("/") if s]


def root_like(segments):
    if not segments:
        return True
    first_is_locale = bool(LOCALE_SEGMENT.match(segments[0]))
    if len(segments) == 1:
        return segments[0] in ROOT_LIKE_SEGMENTS or first_is_locale
    return len(segments) == 2 and first_is_locale and segments[1] in ROOT_LIKE_SEGMENTS


def same_page(orig_segments, final_segments):
    """/x/index.html na /x/ nebo /x/amp na /x je tatáž stránka, ne měkká 404."""
    return (
        bool(orig_segments)
        and orig_segments[-1] in SAME_PAGE_TAILS
        and orig_segments[:-1] == final_segments
    )


def _url_matches(url, host_labels, segments):
    parts = urllib.parse.urlsplit(url.lower())
    labels = (parts.hostname or "").split(".")
    if labels and labels[0] in host_labels:
        return True
    return any(s in segments for s in path_segments(url))


def is_login_url(url):
    return _url_matches(url, LOGIN_HOST_LABELS, LOGIN_SEGMENTS)


def is_consent_url(url):
    return _url_matches(url, CONSENT_HOST_LABELS, CONSENT_SEGMENTS)


def is_login_title(title):
    parts = (p.strip() for p in TITLE_SEPARATORS.split(fold(title)))
    return any(LOGIN_TITLE_SEGMENT.match(p) for p in parts if p)


def _marked_not_free(node):
    """Najde kdekoliv v JSON-LD `isAccessibleForFree` s hodnotou false."""
    if isinstance(node, list):
        return any(_marked_not_free(item) for item in node)
    if not isinstance(node, dict):
        return False
    value = node.get("isAccessibleForFree")
    if "isAccessibleForFree" in node and (
        value is False or str(value).strip().lower() in ("false", "no")
    ):
        return True
    return any(_marked_not_free(v) for v in node.values())


def ld_json_paywalled(blocks):
    for block in blocks:
        try:
            if _marked_not_free(json.loads(block)):
                return True
        except (ValueError, RecursionError):
            if ACCESS_FALSE.search(block):
                return True
    return False


def verdict(
    name, reason, quote_found=None, quote_match=None, quote_similarity=None, **base
):
    return {
        "verdict": name,
        "reason": reason,
        "quote_found": quote_found,
        "quote_match": quote_match,
        "quote_similarity": quote_similarity,
        **base,
    }


def read_page(page):
    """Rozebere tělo a spočítá všechno, podle čeho se dál rozhoduje."""
    content_type = page["content_type"].lower()
    body = page["body"]
    decode_failed = bool(page.get("decode_failed"))
    looks_html = not content_type and body.lstrip()[:1] == "<"
    is_html = not decode_failed and ("html" in content_type or looks_html)
    signals = []
    parser = PageParser()
    if is_html:
        try:
            parser.feed(body)
            parser.close()
        except Exception as error:  # rozbitá stránka musí dostat verdikt, ne pád
            signals.append(f"html_parse_error:{type(error).__name__}")
    if page["truncated"]:
        signals.append("truncated")
    if decode_failed:
        signals.append("decode_failed")
    title = parser.title[:150]
    text = parser.visible_text() if is_html else " ".join(body.split())
    lower_body = body[:200000].lower()
    original, final = page["url"], page["final_url"]
    return {
        "parser": parser,
        "is_html": is_html,
        "textual": not decode_failed
        and (is_html or content_type.startswith(TEXT_TYPES) or not content_type),
        "decode_failed": decode_failed,
        "truncated": bool(page["truncated"]),
        "title": title,
        "text": text,
        "main": parser.main_text() if is_html else text,
        "signals": signals,
        "challenge": bool(CHALLENGE_TITLE.search(title))
        or any(m in lower_body for m in CHALLENGE_MARKERS),
        "redirected": bool(page["redirects"]) and final != original,
        "orig_segments": path_segments(original),
        "final_segments": path_segments(final),
    }


def _status_verdict(status, challenge, base):
    """Verdikt, o kterém rozhodne už stavový kód. None u 2xx."""
    if status in (401, 407):
        return verdict("LOGIN_WALL", f"HTTP {status}: vyžaduje přihlášení", **base)
    if status in (403, 405, 406, 429, 451, 999) or (status == 503 and challenge):
        kind = "stránka s ověřením proti robotům" if challenge else "přístup odmítnut"
        return verdict("BLOCKED", f"HTTP {status}: {kind}", **base)
    if status in (404, 410):
        return verdict("UNREACHABLE", f"HTTP {status}: stránka neexistuje", **base)
    if status is None or not 200 <= status < 300:
        return verdict(
            "UNREACHABLE", f"HTTP {status}: žádná použitelná odpověď", **base
        )
    return None


def _redirect_wall(page, view, wall):
    if not view["redirected"]:
        return None
    original, final = page["url"], page["final_url"]
    if is_login_url(final) and not is_login_url(original):
        return verdict("LOGIN_WALL", "přesměrováno na přihlášení", **wall)
    if any(s in PAYWALL_SEGMENTS for s in view["final_segments"]):
        return verdict("PAYWALLED", "přesměrováno na stránku s předplatným", **wall)
    if is_consent_url(final) and not is_consent_url(original):
        return verdict("CONSENT_WALL", "přesměrováno na souhlas s cookies", **wall)
    return None


def _marked_paywall(page, view, wall):
    meta = view["parser"].meta
    access_false = any(
        m.get("itemprop", "").lower() == "isaccessibleforfree"
        and m.get("content", "").strip().lower() in ("false", "no")
        for m in meta
    )
    tier_locked = any(
        m.get("property", "").lower() == "article:content_tier"
        and m.get("content", "").lower() == "locked"
        for m in meta
    )
    if access_false or tier_locked or ld_json_paywalled(view["parser"].ld_json):
        return verdict(
            "PAYWALLED", "stránka svůj obsah označuje isAccessibleForFree false", **wall
        )
    return None


def _text_wall(page, view, wall):
    if not view["is_html"]:
        return None
    folded = fold(f"{view['title']} {view['text']}")
    short = len(view["main"])
    if PAYWALL_TEXT.search(folded):
        return verdict(
            "PAYWALLED", "text stránky říká, že článek je jen pro předplatitele", **wall
        )
    consent_hits = sum(1 for p in CONSENT_TEXT if p.search(folded))
    if short < CONSENT_PAGE_MAX_CHARS and consent_hits >= 2:
        return verdict(
            "CONSENT_WALL", "stránka je jen dialog souhlasu s cookies", **wall
        )
    login_dominates = short < LOGIN_PAGE_MAX_CHARS or is_login_title(view["title"])
    if view["parser"].password_inputs and login_dominates:
        return verdict("LOGIN_WALL", "stránce dominuje přihlašovací formulář", **wall)
    return None


def _redirect_soft_404(page, view, wall):
    if not view["redirected"]:
        return None
    orig, final = view["orig_segments"], view["final_segments"]
    deep = bool(orig) and not root_like(orig) and not same_page(orig, final)
    if deep and root_like(final):
        return verdict("SOFT_404", "hluboká adresa přesměrovaná na kořen webu", **wall)
    if deep and len(final) < len(orig) and orig[: len(final)] == final:
        return verdict(
            "SOFT_404", "hluboká adresa přesměrovaná na nadřazenou sekci", **wall
        )
    if final and final[-1] in NOT_FOUND_SEGMENTS:
        return verdict("SOFT_404", "přesměrováno na stránku „nenalezeno“", **wall)
    return None


def _page_soft_404(page, view, wall):
    if not view["is_html"]:
        return None
    parser = view["parser"]
    short = len(view["text"]) < NOT_FOUND_PAGE_MAX_CHARS
    h1_says = any(NOT_FOUND_TEXT.search(h) for h in parser.h1[:3])
    title_says = bool(NOT_FOUND_TEXT.search(view["title"]))
    if (title_says and (short or h1_says)) or (h1_says and short):
        return verdict("SOFT_404", "stránka s HTTP 200 říká, že nic nenašla", **wall)
    final = page["final_url"]
    canonical = (
        urllib.parse.urljoin(final, parser.canonical) if parser.canonical else ""
    )
    orig = view["orig_segments"]
    deep = bool(orig) and not root_like(orig)
    if canonical and deep and root_like(path_segments(canonical)):
        return verdict(
            "SOFT_404", "hluboká adresa, jejíž kanonická adresa je kořen webu", **wall
        )
    return None


WALL_RULES = (
    _redirect_wall,
    _marked_paywall,
    _text_wall,
    _redirect_soft_404,
    _page_soft_404,
)


def _content_verdict(view, quote, quote_found, haystack, base):
    """Stránka prošla stěnami: rozhodne, co se z ní přečetlo a jestli je na ní úryvek."""
    if view["decode_failed"]:
        return verdict(
            "NO_CONTENT",
            "tělo používá kódování obsahu, které skript neumí rozbalit",
            **base,
        )
    if not view["textual"]:
        return verdict("REACHED", "netextový obsah; úryvek se nekontroloval", **base)
    if len(view["main"]) < (MIN_MAIN_CHARS if view["is_html"] else MIN_CONTENT_CHARS):
        view["signals"].append("little_main_text")
        return verdict(
            "NO_CONTENT",
            "po odečtení navigace, hlavičky a patičky zbývá málo hlavního textu "
            "(stránku nejspíš vykresluje JavaScript)",
            quote_found=quote_found,
            **base,
        )
    if quote_found is None:
        return verdict("REACHED", "stránka přečtena; úryvek nezadán", **base)
    return _quote_verdict(view, quote, haystack, base)


def _quote_verdict(view, quote, haystack, base):
    similarity = fuzzy_similarity(quote, haystack)
    missing = {"quote_found": False, "quote_similarity": similarity, **base}
    if similarity is not None and similarity >= FUZZY_THRESHOLD:
        return verdict(
            "REACHED_QUOTE_FUZZY",
            "stránka přečtena; úryvku se blízce podobá pasáž, ale ne doslova",
            quote_match="fuzzy",
            **missing,
        )
    if view["truncated"]:
        return verdict(
            "TRUNCATED",
            "přečetla se jen část stránky a úryvek v ní není",
            quote_match="none",
            **missing,
        )
    return verdict(
        "REACHED_QUOTE_MISSING",
        "stránka přečtena; úryvek v jejím čitelném textu není",
        quote_match="none",
        **missing,
    )


def classify(page, quote):
    """Z jednoho stažení udělá verdikt. Čistá funkce bez I/O, takže pravidla jdou
    testovat bez sítě."""
    if page["error"]:
        return verdict("UNREACHABLE", page["error"], signals=[], title="")
    view = read_page(page)
    base = {"signals": view["signals"], "title": view["title"]}
    by_status = _status_verdict(page["http_status"], view["challenge"], base)
    if by_status:
        return by_status

    checked = bool(quote) and view["textual"]
    haystack = normalize(view["text"]) if checked else ""
    quote_found = quote_present(quote, [haystack]) if checked else None
    if quote_found is True:
        # Doslova v textu, který vidí čtenář: stránka úryvek nese, ať je jinak čímkoliv.
        return verdict(
            "REACHED",
            "citovaný úryvek je na stránce doslova",
            quote_found=True,
            quote_match="exact",
            quote_similarity=1.0,
            **base,
        )
    if view["challenge"] and len(view["text"]) < NOT_FOUND_PAGE_MAX_CHARS:
        status = page["http_status"]
        return verdict(
            "BLOCKED",
            f"HTTP {status}: stránka s ověřením proti robotům",
            quote_found=quote_found,
            **base,
        )

    # Odsud úryvek nalezen nebyl, nebo nebyl zadán: nejdřív se poznají stěny, aby
    # se z nepřečtené stránky nikdy nestalo „zdroj to neříká“.
    wall = {"quote_found": quote_found, **base}
    for rule in WALL_RULES:
        found = rule(page, view, wall)
        if found:
            return found
    orig, final = view["orig_segments"], view["final_segments"]
    if view["redirected"] and final != orig and not same_page(orig, final):
        view["signals"].append("redirected_to_different_path")
    return _content_verdict(view, quote, quote_found, haystack, base)


# ---- výstup -----------------------------------------------------------------------


def plain(value, limit):
    """Jeden řádek, bez řídicích znaků, zkrácený: na každý text, který čte model."""
    text = "".join(c if c.isprintable() else " " for c in str(value or ""))
    return " ".join(text.split())[:limit]


def safe_url(url, limit=500):
    return urllib.parse.quote(plain(url, 2000), safe=":/?#[]@!$&'()*+,;=%~-._")[:limit]


def report(page, quote):
    outcome = classify(page, quote)
    return {
        "url": page["url"],
        "final_url": page["final_url"],
        "http_status": page["http_status"],
        "redirects": page["redirects"],
        "verdict": outcome["verdict"],
        "reason": outcome["reason"],
        "quote_found": outcome["quote_found"],
        "quote_match": outcome["quote_match"],
        "quote_similarity": outcome["quote_similarity"],
        "title": outcome["title"],
        "content_type": page["content_type"].split(";")[0].strip(),
        "bytes_read": page["bytes_read"],
        "truncated": bool(page["truncated"]),
        "signals": outcome["signals"],
    }


def check(
    url,
    quote=None,
    timeout=DEFAULT_TIMEOUT,
    max_bytes=DEFAULT_MAX_BYTES,
    allow_private=False,
):
    url = (url or "").strip()
    return report(fetch(url, timeout, max_bytes, allow_private), quote)


def compact(entry):
    out = {key: entry.get(key) for key in COMPACT_FIELDS}
    out["final_url"] = safe_url(entry.get("final_url"))
    out["reason"] = plain(entry.get("reason"), 200)
    return out


def check_batch(
    items,
    timeout=DEFAULT_TIMEOUT,
    max_bytes=DEFAULT_MAX_BYTES,
    workers=DEFAULT_WORKERS,
    allow_private=False,
):
    """Každou různou adresu stáhne jednou, pak každou položku roztřídí proti jejímu úryvku."""
    urls = list(dict.fromkeys(str(item.get("url") or "").strip() for item in items))
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        fetched = pool.map(lambda u: fetch(u, timeout, max_bytes, allow_private), urls)
        pages = dict(zip(urls, fetched))
    results = []
    for index, item in enumerate(items):
        url = str(item.get("url") or "").strip()
        entry = report(pages[url], item.get("quote"))
        entry["id"] = str(item.get("id", index))
        results.append(entry)
    return results


def _positive(kind):
    def parse(value):
        number = kind(value)
        if number <= 0:
            raise argparse.ArgumentTypeError(f"musí být kladné číslo: {value}")
        return number

    return parse


def _arguments(argv):
    parser = argparse.ArgumentParser(
        description="Ověří, že citované zdroje jdou přečíst a nesou citovaný úryvek. "
        "Adresy a úryvky zapiš do JSON souboru a předej jen jeho cestu; text stránky "
        "nikdy nepatří na příkazovou řádku."
    )
    parser.add_argument(
        "--batch",
        metavar="FILE",
        required=True,
        help='JSON pole {id, url, quote}; "-" čte stdin (pro programy, ne pro session)',
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="jen pole, o kterých rozhodl skript; bez titulku a seznamu přesměrování",
    )
    parser.add_argument("--timeout", type=_positive(float), default=DEFAULT_TIMEOUT)
    parser.add_argument("--max-bytes", type=_positive(int), default=DEFAULT_MAX_BYTES)
    parser.add_argument("--workers", type=_positive(int), default=DEFAULT_WORKERS)
    parser.add_argument("--allow-private", action="store_true")
    return parser.parse_args(argv)


def _read_batch(path):
    """Načte dávku; ValueError nebo OSError, když to není pole objektů."""
    if path == "-":
        raw = sys.stdin.read()
    else:
        with open(path, encoding="utf-8") as handle:
            raw = handle.read()
    items = json.loads(raw)
    if not isinstance(items, list) or not all(isinstance(i, dict) for i in items):
        raise ValueError("dávka musí být JSON pole objektů")
    return items


def main(argv=None):
    args = _arguments(argv)
    try:
        items = _read_batch(args.batch)
    except (OSError, ValueError) as error:
        print(json.dumps({"error": f"nečitelná dávka: {error}"}, ensure_ascii=False))
        return 2
    results = check_batch(
        items,
        timeout=args.timeout,
        max_bytes=args.max_bytes,
        workers=args.workers,
        allow_private=args.allow_private,
    )
    if args.compact:
        for entry in results:
            print(json.dumps(compact(entry), ensure_ascii=False))
    else:
        print(json.dumps(results, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
