"""Builds every page of logicalknight.com from one source, so English and German always carry the same information and
the same layout. Edit the content here (company pages) or in content_ippc.py (IPPC Ledger), then run:

    python .github/scripts/build_site.py

The output is plain static HTML for GitHub Pages; there is no build step at publish time, so the generated files are
committed. CI rebuilds and fails if the committed pages differ from this source. Legal texts (Impressum,
Datenschutz) are kept verbatim in .github/site/legal/ and only wrapped in the site layout here. Not published (dot
directory). Standard library only.
"""

from __future__ import annotations

import math
import re
from html import escape
from pathlib import Path

from content_ippc import APP, GS, SAMPLE, T as IPPC

ROOT = Path(__file__).resolve().parents[2]
SITE = "https://logicalknight.com"
LEGAL_SRC = ROOT / ".github" / "site" / "legal"

# The approved Logical Knight crest, byte-for-byte as supplied (138 x 134 px, transparent PNG). Never edited, resized
# or re-encoded: all presentation (lockup, persistent seal) is HTML/CSS/SVG around this file. Tests pin the SHA-256.
CREST = "/assets/img/logical-knight-logo.png"
CREST_W, CREST_H = 138, 134

HELLO = "hello@logicalknight.com"
SUPPORT = "support@logicalknight.com"
WB = "https://workbench.logicalknight.com"
WB_EARLY = f"{WB}/early-access"
WB_LOGIN = f"{WB}/login"

BRANDS = ("Logical Knight", "IPPC Ledger", "Data Workbench")

# Opt-in reach measurement with Umami, run by us on the company server (Growth Desk reads it; Datenschutz section
# 3a). Pages load only assets/js/consent.js: it asks first and loads the tracker only after "Allow"; rejecting or
# ignoring the notice loads nothing. The website id is public by design. The query string and fragment are stripped
# before anything is sent; assets/js/umami-campaign.js then lets through only the campaign codes listed here (the
# same list as Growth Desk's UMAMI_CAMPAIGN_CODES; 1-40 of a-z 0-9 - _). Empty = no campaign code is ever sent.
UMAMI_SCRIPT = "https://stats.logicalknight.com/script.js"
UMAMI_WEBSITE_ID = "45510b01-dd9d-4f28-a8f1-5f013c924c58"
CAMPAIGN_CODES = {"utm-source": "", "utm-medium": "", "utm-campaign": ""}


def analytics_tags() -> str:
    codes = "".join(f' data-{k}="{escape(v)}"' for k, v in CAMPAIGN_CODES.items() if v)
    return (f'\n  <script defer src="/assets/js/consent.js" data-umami-src="{UMAMI_SCRIPT}"'
            f' data-website-id="{UMAMI_WEBSITE_ID}" data-domains="logicalknight.com"{codes}></script>')

# Every page that exists in both languages: key -> (English path, German path). The language switch always leads to
# the same page in the other language.
ROUTES = {
    "home": ("/", "/de/"),
    "company": ("/en/company/", "/de/unternehmen/"),
    "products": ("/en/products/", "/de/produkte/"),
    "dw": ("/en/data-workbench/", "/de/data-workbench/"),
    "ippc": ("/en/ippc-ledger/", "/de/ippc-ledger/"),
    "ippc_gs": ("/en/ippc-ledger/getting-started/", "/de/ippc-ledger/erste-schritte/"),
    "contact": ("/en/contact/", "/de/kontakt/"),
}
LEGAL = {"impressum": "/impressum/", "datenschutz": "/datenschutz/"}
# Older or shorter addresses that must keep working: path -> target.
REDIRECTS = {
    "/en/": "/",
    "/ippc-ledger/": "/de/ippc-ledger/",
    "/kontakt/": "/de/kontakt/",
    "/contact/": "/en/contact/",
}
HOW_ANCHOR = {"en": "how-we-build", "de": "so-arbeiten-wir"}


def path(key: str, lang: str) -> str:
    return ROUTES[key][0 if lang == "en" else 1]


def b(html: str) -> str:
    """Trusted HTML with the brand names protected from page translation."""
    for name in BRANDS:
        html = html.replace(name, f'<span translate="no" class="notranslate">{name}</span>')
    return html


def e(text: str) -> str:
    """Plain text: escaped, brand names protected."""
    return b(escape(text, quote=False))


def img_size(src: str) -> tuple[int, int]:
    data = (ROOT / src.lstrip("/")).read_bytes()
    return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")  # PNG IHDR


# --------------------------------------------------------------------------------------------------------------------
# Shared words
# --------------------------------------------------------------------------------------------------------------------

UI = {
    "en": {
        "skip": "Skip to content", "home": "home", "primary": "Main", "menu": "Menu", "lang_label": "Language",
        "nav": [("company", "Company"), ("products", "Products"), ("how", "How we build"), ("contact", "Contact")],
        "cta": "See our products", "tagline": "Hard problems. Simple software.",
        "f_company": "Company", "f_products": "Products", "f_legal": "Legal", "privacy": "Privacy",
        "impressum_href": "/impressum/#legal-notice", "privacy_href": "/datenschutz/#privacy-policy",
        "rights": "All rights reserved.", "privacy_settings": "Privacy settings", "footer_label": "Footer",
        "learn": "Learn more", "status": "Status", "problem": "The problem", "solution": "What it does",
    },
    "de": {
        "skip": "Zum Inhalt", "home": "Startseite", "primary": "Hauptnavigation", "menu": "Menü", "lang_label": "Sprache",
        "nav": [("company", "Unternehmen"), ("products", "Produkte"), ("how", "So arbeiten wir"), ("contact", "Kontakt")],
        "cta": "Unsere Produkte", "tagline": "Schwierige Probleme. Einfache Software.",
        "f_company": "Unternehmen", "f_products": "Produkte", "f_legal": "Rechtliches", "privacy": "Datenschutz",
        "impressum_href": "/impressum/", "privacy_href": "/datenschutz/",
        "rights": "Alle Rechte vorbehalten.", "privacy_settings": "Datenschutz-Einstellungen", "footer_label": "Fußbereich",
        "learn": "Mehr erfahren", "status": "Stand", "problem": "Das Problem", "solution": "Was es tut",
    },
}

# One line per product, used on the homepage, the products page and in the footer. Status only where verified:
# IPPC Ledger runs as a pilot (app.logicalknight.com, pilot request form); Data Workbench is in Free Early Access
# (workbench.logicalknight.com/early-access).
PRODUCTS = {
    "en": [
        {"key": "ippc", "name": "IPPC Ledger", "status": "Pilot phase",
         "for": "For wood-packaging businesses",
         "problem": "Delivery notes, supplier authorisations and treatment records sit in binders, inboxes and spreadsheets, so gaps show up late.",
         "solution": "IPPC Ledger keeps timber deliveries and their ISPM 15 evidence together, shows what is missing and why, and exports the records for a job or a period.",
         "shot": ("app-dashboard.png", "IPPC Ledger dashboard with counts of deliveries, open jobs and incomplete records")},
        {"key": "dw", "name": "Data Workbench", "status": "Free Early Access",
         "for": "For teams that work with CSV and Excel files",
         "problem": "Business data arrives as messy CSV and Excel files, and after fixing it by hand nobody can say exactly what changed.",
         "solution": "Data Workbench checks and prepares those files, shows every change before and after, and only moves on with data a person has approved.",
         "shot": None},
    ],
    "de": [
        {"key": "ippc", "name": "IPPC Ledger", "status": "Pilotphase",
         "for": "Für Holzverpackungsbetriebe",
         "problem": "Lieferscheine, Ermächtigungen und Behandlungsangaben liegen in Ordnern, Postfächern und Tabellen. Lücken fallen deshalb spät auf.",
         "solution": "IPPC Ledger hält Wareneingänge und ihre ISPM-15-Nachweise zusammen, zeigt, was fehlt und warum, und exportiert die Dokumentation für einen Auftrag oder Zeitraum.",
         "shot": ("app-dashboard.png", "Startseite von IPPC Ledger mit Kennzahlen zu Wareneingängen, offenen Aufträgen und unvollständigen Datensätzen")},
        {"key": "dw", "name": "Data Workbench", "status": "Kostenloser Vorabzugang",
         "for": "Für Teams, die mit CSV- und Excel-Dateien arbeiten",
         "problem": "Geschäftsdaten kommen als unordentliche CSV- und Excel-Dateien. Nach dem Bereinigen von Hand weiß niemand mehr genau, was sich geändert hat.",
         "solution": "Data Workbench prüft und bereitet diese Dateien auf, zeigt jede Änderung vorher und nachher und arbeitet nur mit Daten weiter, die eine Person freigegeben hat.",
         "shot": None},
    ],
}


# --------------------------------------------------------------------------------------------------------------------
# Layout
# --------------------------------------------------------------------------------------------------------------------

def head(lang: str, title: str, desc: str, canonical: str, alternates: dict[str, str] | None, body_class: str,
         robots: str | None = None) -> str:
    alt = ""
    if alternates:
        alt = "".join(f'\n  <link rel="alternate" hreflang="{l}" href="{SITE}{p}">' for l, p in alternates.items())
        if "en" in alternates:
            alt += f'\n  <link rel="alternate" hreflang="x-default" href="{SITE}{alternates["en"]}">'
    robots_meta = f'\n  <meta name="robots" content="{robots}">' if robots else ""
    canonical_link = "" if robots else f'\n  <link rel="canonical" href="{SITE}{canonical}">'
    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(desc)}">{robots_meta}{canonical_link}{alt}
  <meta name="theme-color" content="#FFFFFF">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Logical Knight">
  <meta property="og:title" content="{escape(title)}">
  <meta property="og:description" content="{escape(desc)}">
  <meta property="og:url" content="{SITE}{canonical}">
  <meta property="og:image" content="{SITE}{CREST}">
  <meta property="og:locale" content="{'de_DE' if lang == 'de' else 'en_GB'}">
  <meta name="twitter:card" content="summary">
  <link rel="icon" type="image/png" href="{CREST}">
  <link rel="apple-touch-icon" href="{CREST}">
  <link rel="stylesheet" href="/assets/css/tokens.css">
  <link rel="stylesheet" href="/assets/css/site.css">
  <script>document.documentElement.classList.add("js")</script>{analytics_tags()}
</head>
<body class="{body_class}">
<!--email_off-->
  <a class="skip-link" href="#main">{UI[lang]["skip"]}</a>
'''


def lang_switch(lang: str, en_href: str, de_href: str) -> str:
    def item(code: str, href: str, name: str) -> str:
        if code == lang:
            return f'<span class="lang__item" aria-current="true" lang="{code}" title="{name}">{code.upper()}</span>'
        return f'<a class="lang__item" href="{href}" hreflang="{code}" lang="{code}" aria-label="{name}">{code.upper()}</a>'
    return (f'<div class="lang" role="group" aria-label="{UI[lang]["lang_label"]}">'
            f'{item("en", en_href, "English")}{item("de", de_href, "Deutsch")}</div>')


def brand(lang: str) -> str:
    return (f'<a translate="no" class="brand notranslate" href="{path("home", lang)}" aria-label="Logical Knight, {UI[lang]["home"]}">'
            f'<img src="{CREST}" width="{CREST_W}" height="{CREST_H}" alt=""><span>Logical Knight</span></a>')


def nav_href(key: str, lang: str) -> str:
    if key == "how":
        return f'{path("company", lang)}#{HOW_ANCHOR[lang]}'
    return path(key, lang)


def header(lang: str, current: str | None, en_href: str, de_href: str, cta: tuple[str, str] | None = None) -> str:
    u = UI[lang]
    links = []
    for key, label in u["nav"]:
        cur = ' aria-current="page"' if key == current else ""
        links.append(f'<li><a href="{nav_href(key, lang)}"{cur}>{label}</a></li>')
    cta_label, cta_href = cta or (u["cta"], path("products", lang))
    return f'''  <header class="site-header">
    <div class="container site-header__inner">
      {brand(lang)}
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav"><span class="nav-toggle__bars" aria-hidden="true"></span><span class="nav-toggle__label">{u["menu"]}</span></button>
      <nav class="site-nav" id="site-nav" aria-label="{u["primary"]}">
        <ul class="site-nav__links">{"".join(links)}</ul>
        {lang_switch(lang, en_href, de_href)}
        <a class="btn btn--primary btn--sm site-nav__cta" href="{cta_href}">{b(cta_label)}</a>
      </nav>
    </div>
  </header>
'''


def footer(lang: str, en_href: str, de_href: str) -> str:
    u = UI[lang]
    company = [(path("company", lang), u["nav"][0][1]), (path("products", lang), u["nav"][1][1]),
               (nav_href("how", lang), u["nav"][2][1]), (path("contact", lang), u["nav"][3][1])]
    products = [(path("ippc", lang), "IPPC Ledger"), (path("dw", lang), "Data Workbench")]
    legal = [(u["impressum_href"], "Impressum"), (u["privacy_href"], u["privacy"])]

    def group(title: str, items: list[tuple[str, str]]) -> str:
        return f'<div><h2>{title}</h2><ul>' + "".join(f'<li><a href="{h}">{b(t)}</a></li>' for h, t in items) + "</ul></div>"

    return f'''  <footer class="site-footer">
    <div class="container">
      <div class="site-footer__grid">
        <div class="site-footer__brand">
          {brand(lang)}
          <p>{u["tagline"]}</p>
          <p><a href="mailto:{HELLO}">{HELLO}</a></p>
        </div>
        <nav class="site-footer__nav" aria-label="{u["footer_label"]}">
          {group(u["f_company"], company)}
          {group(u["f_products"], products)}
          {group(u["f_legal"], legal)}
        </nav>
      </div>
      <div class="site-footer__bottom">
        <p>© <span data-year>2026</span> {b("Logical Knight")}. {u["rights"]} <button type="button" class="linkish js-only" data-privacy-settings>{u["privacy_settings"]}</button></p>
        {lang_switch(lang, en_href, de_href)}
      </div>
    </div>
  </footer>
  <script src="/assets/js/site.js" defer></script>
<!--/email_off-->
</body>
</html>
'''


# The persistent brand seal: one fixed layer in the middle of the viewport on every real page. The approved crest sits
# still in the centre; the inscription ring turns slowly clockwise and the outer geometry slower the other way (CSS).
# Decorative only: hidden from assistive technology, never focusable, never takes pointer events.
SEAL_TEXT = {
    "en": "WE BUILD WITH CARE \u2022 SIMPLE SOFTWARE \u2022 REAL PROBLEMS \u2022 CLEAR SYSTEMS \u2022",
    "de": "MIT SORGFALT GEBAUT \u2022 EINFACHE SOFTWARE \u2022 ECHTE PROBLEME \u2022 KLARE SYSTEME \u2022",
}
# Classical Latin, used decoratively: care, clarity, work, trust.
SEAL_MICRO = "CURA \u2022 CLARITAS \u2022 OPUS \u2022 FIDES \u2022 CURA \u2022 CLARITAS \u2022 OPUS \u2022 FIDES \u2022"


def _seal_geometry() -> str:
    """Static SVG pieces in a 400 x 400 view box centred on (200, 200)."""
    def at(r: float, deg: float) -> tuple[float, float]:
        a = math.radians(deg - 90)
        return round(200 + r * math.cos(a), 2), round(200 + r * math.sin(a), 2)

    def ticks(r1: float, r2: float, step: float) -> str:
        return "".join(f'M{x1} {y1}L{x2} {y2}' for d in range(0, 360, int(step))
                       for (x1, y1), (x2, y2) in [(at(r1, d), at(r2, d))])

    def diamond(deg: float) -> str:
        (cx, cy), (ox, oy), (ix, iy) = at(186, deg), at(194, deg), at(178, deg)
        (lx, ly), (rx, ry) = at(186, deg - 1.9), at(186, deg + 1.9)
        return f'M{ox} {oy}L{rx} {ry}L{ix} {iy}L{lx} {ly}Z'

    outer = (f'<path class="seal__arc" d="M{at(197, 20)[0]} {at(197, 20)[1]}A197 197 0 0 1 {at(197, 70)[0]} {at(197, 70)[1]}'
             f'M{at(197, 200)[0]} {at(197, 200)[1]}A197 197 0 0 1 {at(197, 250)[0]} {at(197, 250)[1]}"/>'
             '<circle class="seal__dots" cx="200" cy="200" r="186" pathLength="360"/>'
             f'<path class="seal__fine" d="{ticks(176, 181, 10)}"/>'
             f'<path class="seal__mark" d="{"".join(diamond(d) for d in (0, 90, 180, 270))}"/>')
    inner = (f'<path class="seal__fine" d="{ticks(110, 117, 6)}"/>'
             f'<path class="seal__fine seal__fine--strong" d="{ticks(108, 118, 30)}"/>')
    return outer, inner


def seal(lang: str) -> str:
    outer, inner = _seal_geometry()
    return f'''  <div class="brand-seal" aria-hidden="true">
    <svg class="brand-seal__svg" viewBox="0 0 400 400" focusable="false">
      <defs>
        <path id="lk-seal-ring" d="M200 44a156 156 0 1 1 0 312a156 156 0 1 1 0-312"/>
        <path id="lk-seal-micro" d="M200 75a125 125 0 1 1 0 250a125 125 0 1 1 0-250"/>
      </defs>
      <path class="seal__guide" d="M200 8V392M8 200H392"/>
      <g class="seal__outer">{outer}</g>
      <g class="seal__ring">
        <circle class="seal__line" cx="200" cy="200" r="172"/>
        <circle class="seal__line" cx="200" cy="200" r="143"/>
        <text class="seal__text"><textPath href="#lk-seal-ring" textLength="975" lengthAdjust="spacing">{SEAL_TEXT[lang]}</textPath></text>
        <text class="seal__micro"><textPath href="#lk-seal-micro" textLength="780" lengthAdjust="spacing">{SEAL_MICRO}</textPath></text>
      </g>
      <circle class="seal__disc" cx="200" cy="200" r="104"/>
      <g class="seal__inner">{inner}</g>
    </svg>
    <img class="brand-seal__crest" src="{CREST}" width="{CREST_W}" height="{CREST_H}" alt="">
  </div>
'''


def page(lang: str, key: str, title: str, desc: str, main: str, current: str | None, cta=None) -> str:
    en_href, de_href = ROUTES[key]
    body_class = "page-home" if key == "home" else "page-inner"
    return (head(lang, title, desc, path(key, lang), {"en": en_href, "de": de_href}, body_class)
            + header(lang, current, en_href, de_href, cta) + seal(lang)
            + main + footer(lang, en_href, de_href))


def page_head(eyebrow: str, h1: str, lede: str, extra: str = "") -> str:
    return f'''    <section class="page-head">
      <div class="container">
        <p class="eyebrow">{eyebrow}</p>
        <h1>{h1}</h1>
        <p class="lede">{lede}</p>{extra}
      </div>
    </section>
'''


def figure(src: str, alt: str, caption: str, cls: str = "shot", lazy: bool = True) -> str:
    w, h = img_size(src)
    loading = ' loading="lazy"' if lazy else ""
    return (f'<figure class="{cls}"><a href="{src}"><img src="{src}" width="{w}" height="{h}"{loading} '
            f'alt="{escape(alt)}"></a><figcaption>{caption}</figcaption></figure>')


def status_pill(text: str) -> str:
    return f'<span class="pill">{b(escape(text))}</span>'


# --------------------------------------------------------------------------------------------------------------------
# Data Workbench illustration (not a screenshot: example values, labelled as such)
# --------------------------------------------------------------------------------------------------------------------

DW_ILLUSTRATION = {
    "en": {"title": "Review changes", "cols": ("Field", "Original", "Prepared", "Status"),
           "rows": [("sku", "00123", "00123", "Kept as text", "ok"), ("price", "12,50", "12.50", "Decimal comma", "ok"),
                    ("title", "␣Oak box␣", "Oak box", "Spaces trimmed", "ok"), ("price", "twelve", "—", "Needs your decision", "ask")],
           "caption": "Illustration of the review step with example values. Not a screenshot, not customer data."},
    "de": {"title": "Änderungen prüfen", "cols": ("Feld", "Original", "Vorbereitet", "Status"),
           "rows": [("sku", "00123", "00123", "Als Text behalten", "ok"), ("price", "12,50", "12.50", "Dezimalkomma", "ok"),
                    ("title", "␣Oak box␣", "Oak box", "Leerzeichen entfernt", "ok"), ("price", "twelve", "—", "Ihre Entscheidung nötig", "ask")],
           "caption": "Darstellung des Prüfschritts mit Beispielwerten. Kein Bildschirmfoto, keine Kundendaten."},
}


def dw_illustration(lang: str) -> str:
    d = DW_ILLUSTRATION[lang]
    head_row = "".join(f"<th scope=\"col\">{c}</th>" for c in d["cols"])
    rows = "".join(
        f'<tr><td><code>{f}</code></td><td><code>{escape(o)}</code></td><td><code>{escape(p)}</code></td>'
        f'<td><span class="tag tag--{k}">{"!" if k == "ask" else "✓"} {s}</span></td></tr>'
        for f, o, p, s, k in d["rows"])
    return f'''<figure class="illus">
          <div class="illus__frame">
            <p class="illus__title">{d["title"]}</p>
            <table class="illus__table"><thead><tr>{head_row}</tr></thead><tbody>{rows}</tbody></table>
          </div>
          <figcaption>{d["caption"]}</figcaption>
        </figure>'''


def product_visual(p: dict, lang: str) -> str:
    if p["shot"]:
        name, alt = p["shot"]
        cap = "Real screen, invented data." if lang == "en" else "Echter Bildschirm, erfundene Daten."
        return figure(f"/assets/img/ippc/{lang}/{name}", alt, cap)
    return dw_illustration(lang)


# --------------------------------------------------------------------------------------------------------------------
# Homepage
# --------------------------------------------------------------------------------------------------------------------

HOME = {
    "en": {
        "title": "Logical Knight: hard problems, simple software",
        "desc": "Logical Knight is a small software company building practical tools for small and growing businesses, including IPPC Ledger and Data Workbench.",
        "h1": "Hard problems.<br>Simple software.",
        "lede": "Logical Knight builds practical software for small and growing businesses. We take slow, messy work and turn it into tools that are easier to understand, easier to use, and easier to trust.",
        "cta1": "See our products", "cta2": "Tell us your problem",
        "real_h": "We build for real work.",
        "real": ["Businesses deal with problems that big software does not always solve well. They are too specific for a large product, but too important to ignore.",
                 "That is where we come in. We build focused tools that solve one problem properly."],
        "real_examples_label": "The kind of work we mean",
        "real_examples": ["Records that have to be right, and easy to show when someone asks.",
                          "Information spread across binders, inboxes and spreadsheets.",
                          "Files that need checking before anyone can trust them."],
        "build_h": "What we are building.",
        "build_lede": "Two products so far. Each one started with a single, real problem.",
        "more_h": "More to come.",
        "more": "We keep looking for real problems worth solving. When we find one, we build for it.",
        "how_h": "How we build.",
        "how_lede": "Products start small, go to real users early, and get better from what we learn.",
        "steps": [("Listen", "We start with the people who have the problem, and how the work is done today."),
                  ("Build", "We build the smallest version that really helps. Nothing extra."),
                  ("Test", "Real users try it with real work. That is where we learn the most."),
                  ("Improve", "We fix what is confusing, keep what works, and grow from there.")],
        "users_h": "Built with real users.",
        "users": ["Some products start with free early access. It gives businesses a chance to use the software while we learn what works, what is confusing and what actually helps.",
                  "Free early access is for a limited time. It is not a promise that a product will always be free."],
        "users_now": "Right now: <a href=\"{dw}\">Data Workbench</a> is in Free Early Access, and <a href=\"{ippc}\">IPPC Ledger</a> runs as a pilot.",
        "problem_h": "Have a problem that software should solve?",
        "problem_lines": ["Maybe your team still does something by hand.", "Maybe one job needs five spreadsheets.",
                          "Maybe important information keeps getting lost."],
        "problem_ask": "Tell us about it.",
        "problem_text": "We may already be working on something similar. Sometimes the best product ideas start with one real problem. We cannot build everything, but we will tell you honestly whether we can help.",
        "problem_also": "Specialists, consultants and possible partners are welcome to write too.",
        "problem_cta": "Tell us what is not working",
        "company_h": "Small company. Big care.",
        "company": ["Logical Knight is a small, focused software company. We work as a compact team, keep decisions close to the work and move quickly from a useful idea to a working version.",
                    "Moving quickly does not mean rushing. We test what we build and pay attention to the details.",
                    "We do not build software just because it sounds impressive. We build it because someone needs it."],
        "company_cta": "More about the company",
    },
    "de": {
        "title": "Logical Knight: schwierige Probleme, einfache Software",
        "desc": "Logical Knight ist ein kleines Softwareunternehmen und entwickelt praktische Werkzeuge für kleine und wachsende Unternehmen, darunter IPPC Ledger und Data Workbench.",
        "h1": "Schwierige Probleme.<br>Einfache Software.",
        "lede": "Logical Knight entwickelt praktische Software für kleine und wachsende Unternehmen. Aus langsamer, mühsamer Arbeit machen wir Werkzeuge, die verständlich sind, sich einfach bedienen lassen und denen man vertrauen kann.",
        "cta1": "Unsere Produkte ansehen", "cta2": "Problem schildern",
        "real_h": "Wir bauen Software für echte Arbeit.",
        "real": ["Viele Unternehmen haben Probleme, die große Software nicht gut löst. Für ein großes Produkt sind sie zu speziell, aber zu wichtig, um sie liegen zu lassen.",
                 "Genau hier setzen wir an. Wir bauen gezielte Werkzeuge, die ein Problem richtig lösen."],
        "real_examples_label": "Welche Arbeit wir meinen",
        "real_examples": ["Nachweise, die stimmen müssen und sich auf Nachfrage schnell zeigen lassen.",
                          "Informationen, verteilt auf Ordner, Postfächer und Tabellen.",
                          "Dateien, die man erst prüfen muss, bevor man ihnen trauen kann."],
        "build_h": "Was wir bauen.",
        "build_lede": "Bisher zwei Produkte. Jedes hat mit einem einzigen, echten Problem angefangen.",
        "more_h": "Weitere folgen.",
        "more": "Wir suchen weiter nach echten Problemen, die sich zu lösen lohnen. Wenn wir eins finden, bauen wir dafür.",
        "how_h": "So arbeiten wir.",
        "how_lede": "Produkte fangen klein an, kommen früh zu echten Nutzern und werden mit dem besser, was wir dabei lernen.",
        "steps": [("Zuhören", "Wir beginnen bei den Menschen, die das Problem haben, und bei der Arbeit, wie sie heute läuft."),
                  ("Bauen", "Wir bauen die kleinste Version, die wirklich hilft. Nichts darüber hinaus."),
                  ("Testen", "Echte Nutzer probieren es mit echter Arbeit aus. Dabei lernen wir am meisten."),
                  ("Verbessern", "Wir beheben, was unklar ist, behalten, was funktioniert, und bauen darauf auf.")],
        "users_h": "Mit echten Nutzern gebaut.",
        "users": ["Manche Produkte starten mit einem kostenlosen Vorabzugang. So können Unternehmen die Software schon nutzen, während wir lernen, was funktioniert, was unklar ist und was wirklich hilft.",
                  "Der kostenlose Vorabzugang ist zeitlich begrenzt. Er ist kein Versprechen, dass ein Produkt immer kostenlos bleibt."],
        "users_now": "Derzeit: <a href=\"{dw}\">Data Workbench</a> ist im kostenlosen Vorabzugang, <a href=\"{ippc}\">IPPC Ledger</a> läuft als Pilot.",
        "problem_h": "Haben Sie ein Problem, das Software lösen sollte?",
        "problem_lines": ["Vielleicht erledigt Ihr Team etwas noch von Hand.", "Vielleicht braucht eine Aufgabe fünf Tabellen.",
                          "Vielleicht gehen wichtige Informationen immer wieder verloren."],
        "problem_ask": "Erzählen Sie uns davon.",
        "problem_text": "Vielleicht arbeiten wir schon an etwas Ähnlichem. Manchmal beginnen die besten Produktideen mit einem echten Problem. Wir können nicht alles bauen, aber wir sagen Ihnen ehrlich, ob wir helfen können.",
        "problem_also": "Auch Fachleute, Beraterinnen und Berater und mögliche Partner sind willkommen.",
        "problem_cta": "Schildern Sie, was nicht funktioniert",
        "company_h": "Kleines Unternehmen. Große Sorgfalt.",
        "company": ["Logical Knight ist ein kleines, fokussiertes Softwareunternehmen. Wir arbeiten als kompaktes Team, halten Entscheidungen nah an der Arbeit und machen aus einer guten Idee schnell eine funktionierende Version.",
                    "Schnell zu arbeiten heißt für uns nicht, nachlässig zu arbeiten. Wir testen, was wir bauen, und achten auf die Details.",
                    "Wir bauen keine Software, nur weil sie beeindruckend klingt. Wir bauen sie, weil jemand sie braucht."],
        "company_cta": "Mehr über das Unternehmen",
    },
}


def product_rows(lang: str, heading_level: str = "h3") -> str:
    u = UI[lang]
    rows = []
    for p in PRODUCTS[lang]:
        rows.append(f'''        <article class="product" data-reveal>
          <div class="product__text">
            <p class="product__meta">{status_pill(p["status"])}<span>{e(p["for"])}</span></p>
            <{heading_level} class="product__name"><a href="{path(p["key"], lang)}">{e(p["name"])}</a></{heading_level}>
            <dl class="product__facts">
              <div><dt>{u["problem"]}</dt><dd>{e(p["problem"])}</dd></div>
              <div><dt>{u["solution"]}</dt><dd>{e(p["solution"])}</dd></div>
            </dl>
            <p><a class="link-arrow" href="{path(p["key"], lang)}">{u["learn"]}<span class="sr-only">: {e(p["name"])}</span></a></p>
          </div>
          <div class="product__visual">{product_visual(p, lang)}</div>
        </article>''')
    return "\n".join(rows)


def steps_list(steps: list[tuple[str, str]], cls: str = "steps") -> str:
    return f'<ol class="{cls}">' + "".join(
        f'<li><span class="steps__n" aria-hidden="true">{i + 1:02d}</span><h3>{e(h)}</h3><p>{e(p)}</p></li>'
        for i, (h, p) in enumerate(steps)) + "</ol>"


def home(lang: str) -> str:
    c = HOME[lang]
    paras = lambda items: "".join(f"<p>{b(x)}</p>" for x in items)  # noqa: E731
    users_now = c["users_now"].format(dw=path("dw", lang), ippc=path("ippc", lang))
    main = f'''  <main id="main">
    <section class="hero" aria-labelledby="hero-title">
      <div class="hero__bg" aria-hidden="true"></div>
      <div class="container hero__inner">
        <p class="hero__word notranslate" translate="no">Logical Knight</p>
        <h1 id="hero-title">{c["h1"]}</h1>
        <p class="lede">{b(c["lede"])}</p>
        <p class="btn-row btn-row--center">
          <a class="btn btn--primary" href="{path("products", lang)}">{c["cta1"]}</a>
          <a class="btn btn--secondary" href="{path("contact", lang)}">{c["cta2"]}</a>
        </p>
      </div>
    </section>

    <section class="section" aria-labelledby="real-title">
      <div class="container split">
        <h2 id="real-title" class="h-xl" data-reveal>{c["real_h"]}</h2>
        <div class="split__body" data-reveal>
          <div class="prose prose--lg">{paras(c["real"])}</div>
          <p class="mini-label">{c["real_examples_label"]}</p>
          <ul class="ticks">{"".join(f"<li>{e(x)}</li>" for x in c["real_examples"])}</ul>
        </div>
      </div>
    </section>

    <section class="section section--tint" aria-labelledby="build-title">
      <div class="container">
        <div class="section-intro" data-reveal>
          <h2 id="build-title" class="h-xl">{c["build_h"]}</h2>
          <p class="lede">{c["build_lede"]}</p>
        </div>
        <div class="products">
{product_rows(lang)}
        </div>
        <div class="more" data-reveal>
          <h3>{c["more_h"]}</h3>
          <p>{c["more"]}</p>
        </div>
      </div>
    </section>

    <section class="section" aria-labelledby="how-title">
      <div class="container">
        <div class="section-intro" data-reveal>
          <h2 id="how-title" class="h-xl">{c["how_h"]}</h2>
          <p class="lede">{c["how_lede"]}</p>
        </div>
        <div data-reveal>{steps_list(c["steps"])}</div>
      </div>
    </section>

    <section class="section section--soft" aria-labelledby="users-title">
      <div class="container split">
        <h2 id="users-title" class="h-xl" data-reveal>{c["users_h"]}</h2>
        <div class="split__body prose prose--lg" data-reveal>{paras(c["users"])}<p class="note">{b(users_now)}</p></div>
      </div>
    </section>

    <section class="section ask" aria-labelledby="ask-title">
      <div class="container ask__inner" data-reveal>
        <h2 id="ask-title" class="h-xl">{c["problem_h"]}</h2>
        <ul class="ask__lines">{"".join(f"<li>{x}</li>" for x in c["problem_lines"])}</ul>
        <p class="ask__say">{c["problem_ask"]}</p>
        <p class="ask__text">{c["problem_text"]}</p>
        <p class="ask__also">{c["problem_also"]}</p>
        <p class="btn-row btn-row--center"><a class="btn btn--primary" href="{path("contact", lang)}">{c["problem_cta"]}</a></p>
      </div>
    </section>

    <section class="section company-band" aria-labelledby="company-title">
      <div class="container company-band__inner" data-reveal>
        <h2 id="company-title" class="h-xl">{c["company_h"]}</h2>
        <div class="prose prose--lg">{paras(c["company"])}</div>
        <p><a class="link-arrow" href="{path("company", lang)}">{c["company_cta"]}</a></p>
      </div>
    </section>
  </main>
'''
    return page(lang, "home", c["title"], c["desc"], main, None)


# --------------------------------------------------------------------------------------------------------------------
# Company
# --------------------------------------------------------------------------------------------------------------------

COMPANY = {
    "en": {
        "title": "Company · Logical Knight",
        "desc": "Who Logical Knight is, why the company exists and how it builds focused software for real business problems.",
        "eyebrow": "Company",
        "h1": "A small software company for real work.",
        "lede": "Logical Knight builds practical software for small and growing businesses. We look for real problems and build focused tools around them.",
        "why_h": "Why we exist",
        "why": ["A lot of important work still runs on spreadsheets, e-mail and memory. Large software is often too broad, too expensive or too hard to change for one specific job. So people end up working around their tools instead of with them.",
                "We think there is room for software that does one job well, explains itself, and is honest about what it does and does not do."],
        "care_h": "Problems we care about",
        "care": ["Work that is done by hand, again and again.", "Information spread over files, inboxes and binders.",
                 "Records that must be right, and must be easy to show.", "Data that nobody fully trusts yet."],
        "team_h": "Small team. Short paths.",
        "team": ["We work as a small, focused team. The people shaping a product stay close to the problem and to the work, so decisions can be made quickly and useful ideas can become working software without layers of delay.",
                 "We move quickly, but not carelessly. We keep the scope clear, test what we build and improve what matters."],
        "principles_h": "What good software should do",
        "principles": [("Useful before impressive", "A tool should save time or prevent mistakes from the first week. Features that only look good in a demo can wait."),
                       ("Clear over complicated", "Plain words, clear screens, no surprises. If something needs a manual to understand, we have more work to do."),
                       ("Human control where it matters", "Software can check, sort and point things out. Important decisions stay with people, and changes stay visible."),
                       ("Build, test, learn", "Early versions go to real users. We listen, and the product grows from real use, not from guesses.")],
        "how_h": "How we build",
        "how_lede": "Products start small, go to real users early, and get better from what we learn.",
        "early_h": "Pilots and early access",
        "early": "IPPC Ledger runs as a pilot. Data Workbench is in Free Early Access. Both mean the same thing for us: real businesses use the software with their own work, and we improve it from what they tell us. Early access is not a permanent free plan.",
        "details_h": "Company details",
        "details": "Logical Knight is based in Hamburg, Germany. The full provider details are in the <a href=\"/impressum/#legal-notice\">legal notice</a>.",
        "cta_h": "Have a problem worth solving?",
        "cta_text": "Tell us what is not working. We read every message and reply by e-mail.",
        "cta": "Tell us your problem", "cta2": "See our products",
    },
    "de": {
        "title": "Unternehmen · Logical Knight",
        "desc": "Wer Logical Knight ist, warum es das Unternehmen gibt und wie daraus gezielte Software für echte Probleme im Arbeitsalltag entsteht.",
        "eyebrow": "Unternehmen",
        "h1": "Ein kleines Softwareunternehmen für echte Arbeit.",
        "lede": "Logical Knight entwickelt praktische Software für kleine und wachsende Unternehmen. Wir suchen echte Probleme und bauen gezielte Werkzeuge dafür.",
        "why_h": "Warum es uns gibt",
        "why": ["Viel wichtige Arbeit läuft noch über Tabellen, E-Mails und das Gedächtnis einzelner Menschen. Große Software ist für eine bestimmte Aufgabe oft zu breit, zu teuer oder zu schwer anzupassen. Also arbeiten viele um ihre Werkzeuge herum statt mit ihnen.",
                "Wir glauben: Es gibt Platz für Software, die eine Aufgabe gut erledigt, sich selbst erklärt und ehrlich sagt, was sie kann und was nicht."],
        "care_h": "Probleme, die uns interessieren",
        "care": ["Arbeit, die immer wieder von Hand erledigt wird.", "Informationen, verteilt auf Dateien, Postfächer und Ordner.",
                 "Nachweise, die stimmen müssen und sich leicht vorzeigen lassen sollen.", "Daten, denen noch niemand ganz traut."],
        "team_h": "Kleines Team. Kurze Wege.",
        "team": ["Wir arbeiten als kleines, fokussiertes Team. Die Menschen, die ein Produkt gestalten, bleiben nah am Problem und an der täglichen Arbeit. So können wir schnell entscheiden und aus guten Ideen ohne lange Wege funktionierende Software machen.",
                 "Wir arbeiten schnell, aber nicht nachlässig. Wir halten den Umfang klar, testen, was wir bauen, und verbessern, was wirklich zählt."],
        "principles_h": "Was gute Software leisten sollte",
        "principles": [("Nützlich vor beeindruckend", "Ein Werkzeug soll ab der ersten Woche Zeit sparen oder Fehler verhindern. Was nur in einer Vorführung gut aussieht, kann warten."),
                       ("Klar statt kompliziert", "Einfache Worte, klare Bildschirme, keine Überraschungen. Braucht etwas ein Handbuch, haben wir noch Arbeit vor uns."),
                       ("Der Mensch entscheidet, wo es darauf ankommt", "Software kann prüfen, sortieren und auf etwas hinweisen. Wichtige Entscheidungen bleiben bei Menschen, und Änderungen bleiben sichtbar."),
                       ("Bauen, testen, lernen", "Frühe Versionen gehen an echte Nutzer. Wir hören zu, und das Produkt wächst aus echter Nutzung, nicht aus Vermutungen.")],
        "how_h": "So arbeiten wir",
        "how_lede": "Produkte fangen klein an, kommen früh zu echten Nutzern und werden mit dem besser, was wir dabei lernen.",
        "early_h": "Pilot und Vorabzugang",
        "early": "IPPC Ledger läuft als Pilot. Data Workbench ist im kostenlosen Vorabzugang. Für uns heißt beides dasselbe: Echte Unternehmen nutzen die Software für ihre eigene Arbeit, und wir verbessern sie mit dem, was sie uns sagen. Der Vorabzugang ist kein dauerhaft kostenloses Angebot.",
        "details_h": "Angaben zum Unternehmen",
        "details": "Logical Knight hat seinen Sitz in Hamburg. Alle Angaben zum Anbieter stehen im <a href=\"/impressum/\">Impressum</a>.",
        "cta_h": "Haben Sie ein Problem, das sich zu lösen lohnt?",
        "cta_text": "Schildern Sie uns, was nicht funktioniert. Wir lesen jede Nachricht und antworten per E-Mail.",
        "cta": "Problem schildern", "cta2": "Unsere Produkte ansehen",
    },
}


def company(lang: str) -> str:
    c = COMPANY[lang]
    paras = lambda items: "".join(f"<p>{b(x)}</p>" for x in items)  # noqa: E731
    principles = '<ul class="ruled">' + "".join(f"<li><h3>{h}</h3><p>{p}</p></li>" for h, p in c["principles"]) + "</ul>"
    main = f'''  <main id="main">
{page_head(c["eyebrow"], c["h1"], b(c["lede"]))}
    <section class="section section--flush" aria-labelledby="why-title">
      <div class="container split">
        <h2 id="why-title" class="h-lg">{c["why_h"]}</h2>
        <div class="split__body prose prose--lg">{paras(c["why"])}</div>
      </div>
    </section>

    <section class="section" aria-labelledby="care-title">
      <div class="container split">
        <h2 id="care-title" class="h-lg">{c["care_h"]}</h2>
        <ul class="split__body ticks ticks--lg">{"".join(f"<li>{x}</li>" for x in c["care"])}</ul>
      </div>
    </section>

    <section class="section" aria-labelledby="team-title">
      <div class="container split">
        <h2 id="team-title" class="h-lg">{c["team_h"]}</h2>
        <div class="split__body prose prose--lg">{paras(c["team"])}</div>
      </div>
    </section>

    <section class="section" aria-labelledby="principles-title">
      <div class="container">
        <h2 id="principles-title" class="h-lg section-title">{c["principles_h"]}</h2>
        {principles}
      </div>
    </section>

    <section class="section" id="{HOW_ANCHOR[lang]}" aria-labelledby="how-title">
      <div class="container">
        <div class="section-intro">
          <h2 id="how-title" class="h-lg">{c["how_h"]}</h2>
          <p class="lede">{c["how_lede"]}</p>
        </div>
        {steps_list(HOME[lang]["steps"])}
        <div class="split split--note">
          <h3>{c["early_h"]}</h3>
          <p class="split__body">{b(c["early"])}</p>
        </div>
      </div>
    </section>

    <section class="section" aria-labelledby="details-title">
      <div class="container split">
        <h2 id="details-title" class="h-lg">{c["details_h"]}</h2>
        <p class="split__body prose prose--lg">{b(c["details"])}</p>
      </div>
    </section>

{closing(c["cta_h"], c["cta_text"], (c["cta"], path("contact", lang)), (c["cta2"], path("products", lang)))}
  </main>
'''
    return page(lang, "company", c["title"], c["desc"], main, "company")


def closing(h: str, text: str, primary: tuple[str, str], secondary: tuple[str, str] | None = None) -> str:
    sec = f' <a class="btn btn--secondary" href="{secondary[1]}">{b(secondary[0])}</a>' if secondary else ""
    return f'''    <section class="section closing" aria-labelledby="closing-title">
      <div class="container closing__inner">
        <h2 id="closing-title" class="h-lg">{h}</h2>
        <p class="lede">{b(text)}</p>
        <p class="btn-row btn-row--center"><a class="btn btn--primary" href="{primary[1]}">{b(primary[0])}</a>{sec}</p>
      </div>
    </section>'''


# --------------------------------------------------------------------------------------------------------------------
# Products index
# --------------------------------------------------------------------------------------------------------------------

PRODUCTS_PAGE = {
    "en": {"title": "Products · Logical Knight",
           "desc": "Logical Knight products: IPPC Ledger for timber deliveries and ISPM 15 records, and Data Workbench for checked, understandable data from CSV and Excel files.",
           "eyebrow": "Products", "h1": "Software for one problem at a time.",
           "lede": "Each Logical Knight product starts with one real problem and tries to solve it properly. This is what we have built so far.",
           "more_h": "More to come.",
           "more": "We keep looking for real problems worth solving. If you have one, we would like to hear about it.",
           "more_cta": "Tell us your problem",
           "apps_h": "Already using a product?",
           "apps": [("IPPC Ledger", f"{APP}/login?lang=en", "Log in to IPPC Ledger"), ("Data Workbench", WB_LOGIN, "Sign in to Data Workbench")]},
    "de": {"title": "Produkte · Logical Knight",
           "desc": "Die Produkte von Logical Knight: IPPC Ledger für Wareneingänge und ISPM-15-Nachweise, und Data Workbench für geprüfte, verständliche Daten aus CSV- und Excel-Dateien.",
           "eyebrow": "Produkte", "h1": "Software für jeweils ein Problem.",
           "lede": "Jedes Produkt von Logical Knight beginnt mit einem echten Problem und versucht, es richtig zu lösen. Das haben wir bisher gebaut.",
           "more_h": "Weitere folgen.",
           "more": "Wir suchen weiter nach echten Problemen, die sich zu lösen lohnen. Wenn Sie eins haben, hören wir gern davon.",
           "more_cta": "Problem schildern",
           "apps_h": "Sie nutzen schon ein Produkt?",
           "apps": [("IPPC Ledger", f"{APP}/login?lang=de", "Bei IPPC Ledger anmelden"), ("Data Workbench", WB_LOGIN, "Bei Data Workbench anmelden (englisch)")]},
}


def products(lang: str) -> str:
    c = PRODUCTS_PAGE[lang]
    apps = "".join(f'<li><a href="{h}">{e(label)}</a></li>' for _, h, label in c["apps"])
    main = f'''  <main id="main">
{page_head(c["eyebrow"], c["h1"], b(c["lede"]))}
    <section class="section section--flush" aria-label="{c["eyebrow"]}">
      <div class="container">
        <div class="products">
{product_rows(lang, "h2")}
        </div>
        <div class="more">
          <h2 class="h-md">{c["more_h"]}</h2>
          <p>{c["more"]}</p>
          <p><a class="link-arrow" href="{path("contact", lang)}">{c["more_cta"]}</a></p>
        </div>
        <div class="signin-links">
          <h2 class="h-sm">{c["apps_h"]}</h2>
          <ul>{apps}</ul>
        </div>
      </div>
    </section>
  </main>
'''
    return page(lang, "products", c["title"], c["desc"], main, "products", cta=(
        ("Try Data Workbench" if lang == "en" else "Data Workbench testen"), WB_EARLY))


# --------------------------------------------------------------------------------------------------------------------
# Data Workbench
# --------------------------------------------------------------------------------------------------------------------

DW = {
    "en": {
        "title": "Data Workbench: checked, understandable data from CSV and Excel · Logical Knight",
        "desc": "Data Workbench turns CSV and Excel files into checked, understandable data. Important changes wait for a person's approval. Free Early Access.",
        "status": "Free Early Access",
        "h1": "Turn CSV and Excel files into checked, understandable data.",
        "lede": "Data Workbench helps small teams clean up messy spreadsheets without losing track of what changed. Your original file stays as it was. The changes that matter wait for you to approve them.",
        "cta1": "Request Free Early Access", "cta2": "Sign in",
        "hero_note": "Free for now, while we learn from real use. We review every request before granting access.",
        "lang_note": "",
        "problem_h": "Spreadsheets you cannot fully trust.",
        "problem": ["Files arrive from suppliers, shops and other systems. Prices use commas, product codes lose their leading zeros, and columns are empty or mean different things.",
                    "Fixing it by hand takes time. And afterwards, nobody can say exactly what was changed, or why."],
        "how_h": "How it works.",
        "how_lede": "From a raw file to an output you approved.",
        "steps": [("Upload", "A CSV or Excel file. The original is stored exactly as received."),
                  ("Check quality", "See types, gaps, duplicates and suspicious values, column by column."),
                  ("Prepare", "Choose how each column is read. Nothing is guessed."),
                  ("Review changes", "See every value before and after, and decide the open questions."),
                  ("Approve", "Approve the exact output, then download it."),
                  ("Analyse", "Run documented analysis on approved data, with methods and limits stated."),
                  ("Dashboard", "Build private dashboards for your organisation.")],
        "control_h": "Important changes wait for you.",
        "control_lede": "The review screen shows the original value, the prepared value and why it changed.",
        "control": ["Your original file is never changed.", "Every change is recorded.",
                    "Anything the rules cannot read waits for your decision instead of being guessed.",
                    "Nothing is approved automatically."],
        "limits_h": "What you can try now.",
        "limits": [("Formats", "CSV, XLSX"), ("File size", "up to 20 MB"), ("Rows per sheet", "up to 10,000"),
                   ("Columns", "up to 100"), ("Sheets per workbook", "up to 5"), ("Formulas", "shown, never run")],
        "not_included": "Data Workbench prepares and explains data. It does not do forecasting or train machine-learning models.",
        "early_h": "Free Early Access.",
        "early_lede": "Free while we learn from real use.",
        "early": ["Early Access is currently free. It is not a permanent free plan.",
                  "Access is controlled. We review requests and send invitations directly.",
                  "Each company gets its own private organisation.",
                  "Features may change as we learn.",
                  "You must have permission to upload the data you use."],
        "final_h": "Want to try it with your own files?",
        "final": f"Request access, and we will get back to you. Questions to <a href=\"mailto:{HELLO}\">{HELLO}</a>; if you already use Data Workbench, <a href=\"mailto:{SUPPORT}\">{SUPPORT}</a>.",
    },
    "de": {
        "title": "Data Workbench: geprüfte, verständliche Daten aus CSV und Excel · Logical Knight",
        "desc": "Data Workbench macht aus CSV- und Excel-Dateien geprüfte, verständliche Daten. Wichtige Änderungen warten auf die Freigabe durch eine Person. Kostenloser Vorabzugang.",
        "status": "Kostenloser Vorabzugang",
        "h1": "Aus CSV- und Excel-Dateien werden geprüfte, verständliche Daten.",
        "lede": "Data Workbench hilft kleinen Teams, unordentliche Tabellen zu bereinigen, ohne den Überblick über die Änderungen zu verlieren. Ihre Originaldatei bleibt, wie sie ist. Wichtige Änderungen warten auf Ihre Freigabe.",
        "cta1": "Kostenlosen Vorabzugang anfragen", "cta2": "Anmelden",
        "hero_note": "Derzeit kostenlos, solange wir aus der echten Nutzung lernen. Wir prüfen jede Anfrage, bevor wir Zugang gewähren.",
        "lang_note": "Die Anwendung ist derzeit nur auf Englisch verfügbar. Dort heißt der Vorabzugang „Free Early Access“.",
        "problem_h": "Tabellen, denen man nicht ganz traut.",
        "problem": ["Dateien kommen von Lieferanten, aus Shops und anderen Systemen. Preise stehen mit Komma, Artikelnummern verlieren ihre führenden Nullen, und Spalten sind leer oder bedeuten Unterschiedliches.",
                    "Das von Hand zu bereinigen kostet Zeit. Und danach kann niemand genau sagen, was geändert wurde und warum."],
        "how_h": "So funktioniert es.",
        "how_lede": "Von der Rohdatei zu einem Ergebnis, das Sie freigegeben haben.",
        "steps": [("Hochladen", "Eine CSV- oder Excel-Datei. Das Original wird unverändert gespeichert."),
                  ("Qualität prüfen", "Datentypen, Lücken, Dubletten und auffällige Werte, Spalte für Spalte."),
                  ("Vorbereiten", "Sie legen fest, wie jede Spalte gelesen wird. Nichts wird geraten."),
                  ("Änderungen prüfen", "Jeder Wert vorher und nachher. Offene Fragen entscheiden Sie."),
                  ("Freigeben", "Sie geben genau das Ergebnis frei und laden es herunter."),
                  ("Auswerten", "Dokumentierte Auswertungen auf freigegebenen Daten, mit Methode und Grenzen."),
                  ("Dashboard", "Private Dashboards für Ihr Unternehmen.")],
        "control_h": "Wichtige Änderungen warten auf Sie.",
        "control_lede": "Die Prüfansicht zeigt den ursprünglichen Wert, den vorbereiteten Wert und den Grund der Änderung.",
        "control": ["Ihre Originaldatei wird nie verändert.", "Jede Änderung wird festgehalten.",
                    "Was die Regeln nicht lesen können, wartet auf Ihre Entscheidung, statt geraten zu werden.",
                    "Nichts wird automatisch freigegeben."],
        "limits_h": "Was Sie jetzt ausprobieren können.",
        "limits": [("Formate", "CSV, XLSX"), ("Dateigröße", "bis 20 MB"), ("Zeilen je Blatt", "bis 10.000"),
                   ("Spalten", "bis 100"), ("Blätter je Arbeitsmappe", "bis 5"), ("Formeln", "angezeigt, nie ausgeführt")],
        "not_included": "Data Workbench bereitet Daten auf und macht sie verständlich. Es erstellt keine Prognosen und trainiert keine Modelle für maschinelles Lernen.",
        "early_h": "Kostenloser Vorabzugang.",
        "early_lede": "Kostenlos, solange wir aus der echten Nutzung lernen.",
        "early": ["Der Vorabzugang ist derzeit kostenlos. Er ist kein dauerhaft kostenloses Angebot.",
                  "Der Zugang ist begrenzt. Wir prüfen Anfragen und versenden die Einladungen direkt.",
                  "Jedes Unternehmen bekommt einen eigenen, privaten Bereich.",
                  "Funktionen können sich ändern, während wir lernen.",
                  "Sie dürfen nur Daten hochladen, für die Sie die Erlaubnis haben."],
        "final_h": "Mit Ihren eigenen Dateien ausprobieren?",
        "final": f"Fragen Sie den Zugang an, wir melden uns. Fragen an <a href=\"mailto:{HELLO}\">{HELLO}</a>; wenn Sie Data Workbench schon nutzen, an <a href=\"mailto:{SUPPORT}\">{SUPPORT}</a>.",
    },
}


def data_workbench(lang: str) -> str:
    c = DW[lang]
    paras = lambda items: "".join(f"<p>{b(x)}</p>" for x in items)  # noqa: E731
    lang_note = f'\n        <p class="note note--lang">{b(c["lang_note"])}</p>' if c["lang_note"] else ""
    extra = f'''
        <p class="btn-row">
          <a class="btn btn--primary" href="{WB_EARLY}" data-umami-event="dw_early_access_click">{c["cta1"]}</a>
          <a class="btn btn--secondary" href="{WB_LOGIN}">{c["cta2"]}</a>
        </p>
        <p class="hero-note">{c["hero_note"]}</p>{lang_note}'''
    limits = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in c["limits"])
    main = f'''  <main id="main">
{page_head(f'{b("Data Workbench")} {status_pill(c["status"])}', c["h1"], b(c["lede"]), extra)}
    <section class="section section--flush" aria-labelledby="problem-title">
      <div class="container split">
        <h2 id="problem-title" class="h-lg">{c["problem_h"]}</h2>
        <div class="split__body prose prose--lg">{paras(c["problem"])}</div>
      </div>
    </section>

    <section class="section" aria-labelledby="how-title">
      <div class="container">
        <div class="section-intro">
          <h2 id="how-title" class="h-lg">{c["how_h"]}</h2>
          <p class="lede">{c["how_lede"]}</p>
        </div>
        {steps_list(c["steps"], "steps steps--seven")}
      </div>
    </section>

    <section class="section" aria-labelledby="control-title">
      <div class="container split split--visual">
        <div>
          <h2 id="control-title" class="h-lg">{c["control_h"]}</h2>
          <p class="lede">{c["control_lede"]}</p>
          <ul class="ticks">{"".join(f"<li>{x}</li>" for x in c["control"])}</ul>
        </div>
        {dw_illustration(lang)}
      </div>
    </section>

    <section class="section" aria-labelledby="limits-title">
      <div class="container">
        <h2 id="limits-title" class="h-lg section-title">{c["limits_h"]}</h2>
        <dl class="facts">{limits}</dl>
        <p class="note">{b(c["not_included"])}</p>
      </div>
    </section>

    <section class="section" aria-labelledby="early-title">
      <div class="container split">
        <div>
          <h2 id="early-title" class="h-lg">{c["early_h"]}</h2>
          <p class="lede">{c["early_lede"]}</p>
        </div>
        <ul class="split__body ticks">{"".join(f"<li>{x}</li>" for x in c["early"])}</ul>
      </div>
    </section>

{closing(c["final_h"], c["final"], (c["cta1"], WB_EARLY), (c["cta2"], WB_LOGIN))}
  </main>
'''
    return page(lang, "dw", c["title"], c["desc"], main, "products", cta=("Try Data Workbench" if lang == "en" else "Data Workbench testen", WB_EARLY))


# --------------------------------------------------------------------------------------------------------------------
# IPPC Ledger
# --------------------------------------------------------------------------------------------------------------------

def ippc(lang: str) -> str:
    c = IPPC[lang]
    pilot = f"{APP}/pilot?lang={lang}"
    login = f"{APP}/login?lang={lang}"
    gs = path("ippc_gs", lang)
    ids = dict(zip(("problem", "flow", "example", "export", "features", "start", "data", "pilot", "faq"),
                   {"de": ("problem", "ablauf", "beispiel", "export", "funktionen", "einstieg", "daten", "pilot", "faq"),
                    "en": ("problem", "how", "example", "export", "features", "start", "data", "pilot", "faq")}[lang]))

    def sec(key: str, eyebrow: str, h: str, body: str) -> str:
        sid = ids[key]
        return f'''    <section class="section" id="{sid}" aria-labelledby="{sid}-title">
      <div class="container">
        <div class="section-intro"><p class="eyebrow">{eyebrow}</p><h2 class="h-lg" id="{sid}-title">{e(h)}</h2></div>
        {body}
      </div>
    </section>
'''

    ruled = lambda items: '<ul class="ruled">' + "".join(f"<li><h3>{e(h)}</h3><p>{e(p)}</p></li>" for h, p in items) + "</ul>"  # noqa: E731
    sample = f'<a class="btn btn--secondary" href="{SAMPLE[lang]}" download>{c["pack_dl"]}</a>'
    shot_name, shot_alt, shot_cap = c["hero_shot"]
    shots = "".join(figure(f"/assets/img/ippc/{lang}/{n}", alt, cap) for n, alt, cap in c["shots"])
    extra = f'''
        <p class="btn-row">
          <a class="btn btn--primary" href="{pilot}" data-umami-event="ippc_pilot_click">{c["pilot_btn"]}</a>
          <a class="btn btn--secondary" href="#{ids["example"]}">{c["example_btn"]}</a>
        </p>
        <p class="hero-note">{c["login_note"]} <a href="{login}">{c["login"]}</a></p>'''
    main = f'''  <main id="main">
{page_head(f'{b("IPPC Ledger")} {status_pill(c["status"])}', e(c["h1"]), e(c["lede"]), extra)}
    <section class="section section--flush" aria-label="{escape(shot_alt)}">
      <div class="container">
        {figure(f"/assets/img/ippc/{lang}/{shot_name}", shot_alt, e(shot_cap), "shot shot--hero", lazy=False)}
        <p class="note">{e(c["status_note"])}</p>
      </div>
    </section>
{sec("problem", c["problem_eyebrow"], c["problem_h"], ruled(c["problem"]))}
{sec("flow", c["flow_eyebrow"], c["flow_h"], steps_list(c["flow"], "steps steps--five"))}
{sec("example", c["ex_eyebrow"], c["ex_h"], f'<p class="lede">{e(c["ex_lede"])}</p><div class="shots">{shots}</div>')}
{sec("export", c["pack_eyebrow"], c["pack_h"], f'<p class="lede">{e(c["pack_lede"])}</p><dl class="pack">' + "".join(f"<div><dt><code>{escape(f)}</code></dt><dd>{e(d)}</dd></div>" for f, d in c["pack"]) + f'</dl><p class="note">{e(c["pack_note"])}</p><p class="btn-row">{sample}</p>')}
{sec("features", c["feat_eyebrow"], c["feat_h"], ruled(c["features"]))}
{sec("start", c["gs_eyebrow"], c["gs_h"], '<ul class="ticks ticks--lg">' + "".join(f"<li><strong>{e(h)}</strong> {e(p)}</li>" for h, p in c["gs_items"]) + f'</ul><p class="prose">{b(c["gs_text"].format(gs=gs))}</p>')}
{sec("data", c["data_eyebrow"], c["data_h"], ruled(c["data"]))}
{sec("pilot", c["pilot_eyebrow"], c["pilot_h"], f'<p class="lede">{e(c["pilot_scope"])}</p>' + steps_list(c["pilot_steps"], "steps steps--five") + f'<p class="btn-row"><a class="btn btn--primary" href="{pilot}" data-umami-event="ippc_pilot_click">{c["pilot_btn"]}</a></p>')}
{sec("faq", c["faq_eyebrow"], c["faq_h"], '<div class="faq">' + "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in c["faq"]) + "</div>")}
    <section class="section closing" aria-labelledby="closing-title">
      <div class="container closing__inner">
        <h2 id="closing-title" class="h-lg">{c["final_h"]}</h2>
        <p class="lede">{b(c["final_text"])}</p>
        <p class="btn-row btn-row--center"><a class="btn btn--primary" href="{pilot}" data-umami-event="ippc_pilot_click">{c["pilot_btn"]}</a> {sample}</p>
        <p class="fineprint">{c["fictional"]}</p>
      </div>
    </section>
  </main>
'''
    return page(lang, "ippc", c["title"], c["desc"], main, "products", cta=(c["pilot_btn"], pilot))


def ippc_getting_started(lang: str) -> str:
    c, g = IPPC[lang], GS[lang]
    items = []
    for i, step in enumerate(g["steps"]):
        h, p = step[0], step[1]
        pic = figure(f"/assets/img/ippc/{lang}/{step[2]}", h, c["shot_label"]) if len(step) > 2 else ""
        items.append(f'<li class="guide__step"><h2 class="h-sm"><span class="steps__n" aria-hidden="true">{i + 1:02d}</span> {e(h)}</h2><p>{e(p)}</p>{pic}</li>')
    main = f'''  <main id="main">
{page_head(b("IPPC Ledger"), e(g["h1"]), e(g["lede"]))}
    <section class="section section--flush">
      <div class="container narrow">
        <ol class="guide">{"".join(items)}</ol>
        <p class="prose">{g["help"]} · <a href="{path("ippc", lang)}">{e(g["back"])}</a></p>
      </div>
    </section>
  </main>
'''
    return page(lang, "ippc_gs", g["title"], g["lede"], main, "products", cta=(c["pilot_btn"], f"{APP}/pilot?lang={lang}"))


# --------------------------------------------------------------------------------------------------------------------
# Contact
# --------------------------------------------------------------------------------------------------------------------

CONTACT = {
    "en": {
        "title": "Tell us what is not working · Logical Knight",
        "desc": "Tell Logical Knight about a business problem that software should solve: repetitive work, messy spreadsheets, missing information. Or write to hello@logicalknight.com.",
        "eyebrow": "Contact",
        "h1": "Tell us what is not working.",
        "lede": "We are always interested in real business problems. If your team is stuck with repetitive work, messy spreadsheets, missing information or a process that existing software handles badly, tell us about it.",
        "form_h": "Describe the problem",
        "name": "Your name", "company": "Company", "optional": "optional",
        "problem": "What is getting in the way?",
        "problem_hint": "For example: every week we copy delivery notes into three different spreadsheets.",
        "today": "What do you do today instead?",
        "submit": "Open in my e-mail app",
        "how": "This opens your e-mail app with your message filled in. Nothing is sent from this page; it reaches us only when you press send there. We reply to the address you send from.",
        "sent": "Your e-mail app should open now. If it does not, write to us directly at",
        "subject": "Problem worth solving", "subject_from": "from",
        "labels": {"name": "Name", "company": "Company", "problem": "What is getting in the way", "today": "What we do today instead"},
        "nojs": "Write to us at",
        "next_h": "What happens next",
        "next": ["We read your message and reply by e-mail.",
                 "If we can help, or are already building something similar, we say so.",
                 "If we cannot, we say that too."],
        "also_h": "Also welcome",
        "also": "Product ideas, specialist knowledge, consultants and possible partners. Write to the same address.",
        "direct_h": "Write to us directly",
        "direct": [("General enquiries", f'<a href="mailto:{HELLO}">{HELLO}</a>'),
                   ("Support for existing users", f'<a href="mailto:{SUPPORT}">{SUPPORT}</a>'),
                   ("IPPC Ledger pilot", f'<a href="{APP}/pilot?lang=en">Request a pilot</a>'),
                   ("Data Workbench", f'<a href="{WB_EARLY}">Request Free Early Access</a>')],
        "privacy": "How we handle e-mail is described in the <a href=\"/datenschutz/#contact\">privacy policy</a>.",
    },
    "de": {
        "title": "Schildern Sie uns, was nicht funktioniert · Logical Knight",
        "desc": "Erzählen Sie Logical Knight von einem Problem, das Software lösen sollte: wiederkehrende Handarbeit, unübersichtliche Tabellen, fehlende Informationen. Oder schreiben Sie an hello@logicalknight.com.",
        "eyebrow": "Kontakt",
        "h1": "Schildern Sie uns, was nicht funktioniert.",
        "lede": "Echte Probleme aus dem Arbeitsalltag interessieren uns immer. Wenn Ihr Team mit wiederkehrender Handarbeit, unübersichtlichen Tabellen, fehlenden Informationen oder einem Ablauf kämpft, den vorhandene Software schlecht abbildet, erzählen Sie uns davon.",
        "form_h": "Problem beschreiben",
        "name": "Ihr Name", "company": "Unternehmen", "optional": "optional",
        "problem": "Was steht Ihnen im Weg?",
        "problem_hint": "Zum Beispiel: Jede Woche tippen wir Lieferscheine in drei verschiedene Tabellen ab.",
        "today": "Wie lösen Sie es heute?",
        "submit": "In meinem E-Mail-Programm öffnen",
        "how": "Damit öffnet sich Ihr E-Mail-Programm mit Ihrer Nachricht. Von dieser Seite wird nichts gesendet; die Nachricht erreicht uns erst, wenn Sie dort auf Senden klicken. Wir antworten an die Adresse, von der Sie schreiben.",
        "sent": "Ihr E-Mail-Programm sollte sich jetzt öffnen. Falls nicht, schreiben Sie uns direkt an",
        "subject": "Ein Problem, das sich zu lösen lohnt", "subject_from": "von",
        "labels": {"name": "Name", "company": "Unternehmen", "problem": "Was uns im Weg steht", "today": "Wie wir es heute lösen"},
        "nojs": "Schreiben Sie uns an",
        "next_h": "Wie es weitergeht",
        "next": ["Wir lesen Ihre Nachricht und antworten per E-Mail.",
                 "Wenn wir helfen können oder schon an etwas Ähnlichem arbeiten, sagen wir es Ihnen.",
                 "Wenn nicht, sagen wir Ihnen das auch."],
        "also_h": "Ebenfalls willkommen",
        "also": "Produktideen, Fachwissen, Beraterinnen und Berater und mögliche Partner. Schreiben Sie an dieselbe Adresse.",
        "direct_h": "Direkt schreiben",
        "direct": [("Allgemeine Anfragen", f'<a href="mailto:{HELLO}">{HELLO}</a>'),
                   ("Support für bestehende Nutzer", f'<a href="mailto:{SUPPORT}">{SUPPORT}</a>'),
                   ("Pilot IPPC Ledger", f'<a href="{APP}/pilot?lang=de">Pilot anfragen</a>'),
                   ("Data Workbench", f'<a href="{WB_EARLY}">Kostenlosen Vorabzugang anfragen</a>')],
        "privacy": "Wie wir mit E-Mails umgehen, steht in der <a href=\"/datenschutz/#kontakt\">Datenschutzerklärung</a>.",
    },
}


def contact(lang: str) -> str:
    c = CONTACT[lang]
    opt = f' <span class="field__opt">({c["optional"]})</span>'
    data = (f'data-to="{HELLO}" data-subject="{escape(c["subject"])}" data-subject-from="{escape(c["subject_from"])}" '
            + " ".join(f'data-label-{k}="{escape(v)}"' for k, v in c["labels"].items()))
    direct = "".join(f"<div><dt>{b(k)}</dt><dd>{v}</dd></div>" for k, v in c["direct"])
    main = f'''  <main id="main">
{page_head(c["eyebrow"], c["h1"], b(c["lede"]))}
    <section class="section section--flush" aria-labelledby="form-title">
      <div class="container contact">
        <div class="contact__form">
          <h2 id="form-title" class="h-md">{c["form_h"]}</h2>
          <p class="nojs-only">{c["nojs"]} <a href="mailto:{HELLO}">{HELLO}</a>.</p>
          <form class="compose js-only" {data} novalidate>
            <div class="field">
              <label for="f-name">{c["name"]}{opt}</label>
              <input id="f-name" name="name" type="text" autocomplete="name" maxlength="120">
            </div>
            <div class="field">
              <label for="f-company">{c["company"]}{opt}</label>
              <input id="f-company" name="company" type="text" autocomplete="organization" maxlength="160">
            </div>
            <div class="field">
              <label for="f-problem">{c["problem"]}</label>
              <textarea id="f-problem" name="problem" rows="6" required maxlength="1500" aria-describedby="f-problem-hint"></textarea>
              <p class="field__hint" id="f-problem-hint">{c["problem_hint"]}</p>
            </div>
            <div class="field">
              <label for="f-today">{c["today"]}{opt}</label>
              <textarea id="f-today" name="today" rows="3" maxlength="600"></textarea>
            </div>
            <p class="field__error" role="alert" hidden></p>
            <p><button class="btn btn--primary" type="submit" data-umami-event="contact_compose_click">{c["submit"]}</button></p>
            <p class="field__hint">{c["how"]}</p>
            <p class="compose__sent" role="status" hidden>{c["sent"]} <a href="mailto:{HELLO}">{HELLO}</a>.</p>
          </form>
        </div>
        <div class="contact__side">
          <h2 class="h-sm">{c["next_h"]}</h2>
          <ul class="ticks">{"".join(f"<li>{x}</li>" for x in c["next"])}</ul>
          <h2 class="h-sm">{c["also_h"]}</h2>
          <p>{c["also"]}</p>
          <h2 class="h-sm">{c["direct_h"]}</h2>
          <dl class="contact__list">{direct}</dl>
          <p class="fineprint">{c["privacy"]}</p>
        </div>
      </div>
    </section>
  </main>
'''
    return page(lang, "contact", c["title"], c["desc"], main, "contact")


# --------------------------------------------------------------------------------------------------------------------
# Legal pages: verbatim content, new layout. German page with an English section, as before.
# --------------------------------------------------------------------------------------------------------------------

LEGAL_META = {
    "impressum": ("Impressum · Logical Knight", "Impressum (Anbieterkennzeichnung nach § 5 DDG) von Logical Knight.", "#legal-notice"),
    "datenschutz": ("Datenschutzerklärung · Logical Knight", "Datenschutzerklärung von Logical Knight (Deutsch, English).", "#privacy-policy"),
}


def legal(name: str) -> str:
    title, desc, en_anchor = LEGAL_META[name]
    p = LEGAL[name]
    body = (LEGAL_SRC / f"{name}.html").read_text(encoding="utf-8")
    en_href, de_href = p + en_anchor, p
    main = f'''  <main id="main">
    <section class="section legal">
      <div class="container narrow legal__body">
{body}      </div>
    </section>
  </main>
'''
    return (head("de", title, desc, p, None, "page-inner page-legal") + header("de", None, en_href, de_href)
            + seal("de") + main + footer("de", en_href, de_href))


# --------------------------------------------------------------------------------------------------------------------
# 404 and redirects
# --------------------------------------------------------------------------------------------------------------------

def not_found() -> str:
    main = f'''  <main id="main">
    <section class="section notfound">
      <div class="container narrow notfound__inner">
        <h1 class="h-lg">This page does not exist.</h1>
        <p class="lede">It may have moved. Try the <a href="/">homepage</a> or our <a href="/en/products/">products</a>.</p>
        <h2 class="h-md" lang="de">Diese Seite gibt es nicht.</h2>
        <p class="lede" lang="de">Vielleicht ist sie umgezogen. Zur <a href="/de/">Startseite</a> oder zu unseren <a href="/de/produkte/">Produkten</a>.</p>
      </div>
    </section>
  </main>
'''
    return (head("en", "Page not found · Logical Knight", "This page does not exist.", "/404.html", None, "page-inner",
                 robots="noindex") + header("en", None, "/", "/de/") + seal("en") + main + footer("en", "/", "/de/"))


def redirect(target: str) -> str:
    return f'''<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>Logical Knight</title><meta name="robots" content="noindex">
<link rel="canonical" href="{SITE}{target}"><meta http-equiv="refresh" content="0; url={target}"></head>
<body><p><a href="{target}"><span translate="no" class="notranslate">Logical Knight</span></a></p></body>
</html>
'''


def sitemap() -> str:
    urls = []
    for en, de in ROUTES.values():
        for p, other, lang, olang in ((en, de, "en", "de"), (de, en, "de", "en")):
            urls.append(f'  <url><loc>{SITE}{p}</loc>'
                        f'<xhtml:link rel="alternate" hreflang="{lang}" href="{SITE}{p}"/>'
                        f'<xhtml:link rel="alternate" hreflang="{olang}" href="{SITE}{other}"/></url>')
    urls += [f"  <url><loc>{SITE}{p}</loc></url>" for p in LEGAL.values()]
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + "\n".join(urls) + "\n</urlset>\n")


# --------------------------------------------------------------------------------------------------------------------

def outputs() -> dict[str, str]:
    """Every generated file: path relative to the site root -> content."""
    out: dict[str, str] = {}

    def at(p: str, html: str) -> None:
        out[(p.strip("/") + "/index.html").lstrip("/")] = html

    builders = {"home": home, "company": company, "products": products, "dw": data_workbench, "ippc": ippc,
                "ippc_gs": ippc_getting_started, "contact": contact}
    for key, build in builders.items():
        for lang in ("en", "de"):
            at(path(key, lang), build(lang))
    for name, p in LEGAL.items():
        at(p, legal(name))
    for p, target in REDIRECTS.items():
        at(p, redirect(target))
    out["404.html"] = not_found()
    out["sitemap.xml"] = sitemap()
    return {k: re.sub(r"[ \t]+\n", "\n", v) for k, v in out.items()}


def main() -> None:
    for rel, text in outputs().items():
        p = ROOT / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8", newline="\n")
        print("wrote", rel)


if __name__ == "__main__":
    main()
