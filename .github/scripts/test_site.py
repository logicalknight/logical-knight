"""Focused site tests (stdlib only): python .github/scripts/test_site.py

Routes and EN/DE parity, the language switch, internal links and assets, the approved crest, the watermark, page
metadata, forms, external links, and copy rules (brand name, no retired positioning, no hype words)."""

from __future__ import annotations

import hashlib
import re
import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_site as site  # noqa: E402

ROOT = site.ROOT
CREST_SHA256 = "eecf11b45128edef585e8aeeae73c20e3b85112d66a6991f0aafa7e03c839fde"
ALLOWED_EMAILS = {"hello@logicalknight.com", "support@logicalknight.com", "mailbox@datenschutz.hamburg.de"}
HYPE = ("leverage", "empower", "transformative", "cutting-edge", "next-generation", "ecosystem", "seamless",
        "innovative", "unlock", "revolution", "world-class", "best-in-class", "ai-powered", "synergy")
STALE = ("Logical Knights", "Applied technology", "angewandte Technik", "Private development", "AI, automation",
         "Agent Research", "x402", "mark-64.png", "og.png", "instrument-sans", "logo_clean")


class Doc(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags: list[tuple[str, dict]] = []
        self.text: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))
        if tag in ("script", "style", "title"):
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "title") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip:
            self.text.append(data)

    def all(self, tag):
        return [a for t, a in self.tags if t == tag]


def html_files() -> list[Path]:
    return sorted(p for p in ROOT.rglob("*.html")
                  if not any(part.startswith((".", "_")) or part in ("var", "node_modules") for part in p.relative_to(ROOT).parts))


def parse(p: Path) -> Doc:
    d = Doc()
    d.feed(p.read_text(encoding="utf-8"))
    return d


def resolve(url: str) -> Path | None:
    """Local file a site-relative URL is served from (GitHub Pages rules), or None if it does not exist."""
    url = url.split("#")[0].split("?")[0]
    if not url:
        return None
    p = ROOT / url.lstrip("/")
    if url.endswith("/"):
        p = p / "index.html"
    return p if p.is_file() else None


def page_file(route: str) -> Path:
    return ROOT / route.lstrip("/") / "index.html"


REDIRECT_FILES = {page_file(p) for p in site.REDIRECTS}
CONTENT = [p for p in html_files() if p not in REDIRECT_FILES]


class Build(unittest.TestCase):
    def test_committed_pages_match_the_source(self):
        for rel, text in site.outputs().items():
            with self.subTest(rel):
                self.assertEqual((ROOT / rel).read_text(encoding="utf-8"), text, "run build_site.py and commit")

    def test_legal_text_is_wrapped_verbatim(self):
        for name, p in site.LEGAL.items():
            body = (site.LEGAL_SRC / f"{name}.html").read_text(encoding="utf-8").strip()
            self.assertIn(body, page_file(p).read_text(encoding="utf-8"))


class Routes(unittest.TestCase):
    def test_every_route_exists_in_both_languages(self):
        for key, (en, de) in site.ROUTES.items():
            for lang, route in (("en", en), ("de", de)):
                with self.subTest(key=key, lang=lang):
                    f = page_file(route)
                    self.assertTrue(f.is_file(), route)
                    self.assertIn(f'<html lang="{lang}">', f.read_text(encoding="utf-8"))

    def test_hreflang_and_language_switch_point_to_the_same_page(self):
        for key, (en, de) in site.ROUTES.items():
            for lang, route, other, other_lang in (("en", en, de, "de"), ("de", de, en, "en")):
                with self.subTest(route):
                    doc = parse(page_file(route))
                    alts = {a.get("hreflang"): a.get("href") for a in doc.all("link") if a.get("rel") == "alternate"}
                    self.assertEqual(alts.get(other_lang), site.SITE + other)
                    self.assertEqual(alts.get(lang), site.SITE + route)
                    switch = [a["href"] for a in doc.all("a") if "lang__item" in (a.get("class") or "")]
                    self.assertTrue(switch and all(h == other for h in switch), switch)
                    canon = [a["href"] for a in doc.all("link") if a.get("rel") == "canonical"]
                    self.assertEqual(canon, [site.SITE + route])

    def test_old_addresses_still_lead_somewhere(self):
        for old, target in {**site.REDIRECTS, "/impressum/": None, "/datenschutz/": None}.items():
            with self.subTest(old):
                f = page_file(old)
                self.assertTrue(f.is_file())
                if target:
                    self.assertIn(f'url={target}"', f.read_text(encoding="utf-8"))
                    self.assertIsNotNone(resolve(target))

    def test_old_addresses_keep_only_the_approved_campaign_codes(self):
        # the redirect page loads the campaign filter with exactly the analytics tag's list, then redirect.js
        tag = parse(page_file("/en/ippc-ledger/")).all("script")
        consent = next(t for t in tag if t.get("src") == "/assets/js/consent.js")
        for old, target in site.REDIRECTS.items():
            with self.subTest(old):
                scripts = parse(page_file(old)).all("script")
                self.assertEqual([t.get("src") for t in scripts], ["/assets/js/umami-campaign.js", "/assets/js/redirect.js"])
                for k in ("data-utm-source", "data-utm-medium", "data-utm-campaign"):
                    self.assertEqual(scripts[0].get(k), consent.get(k), k)
                self.assertEqual(scripts[1].get("data-target"), target)
                self.assertFalse(any("defer" in t or "async" in t for t in scripts))  # both run before the refresh
        js = (ROOT / "assets/js/redirect.js").read_text(encoding="utf-8")
        self.assertEqual(js.count("location.search"), 1)  # read once, only through the approved-codes filter
        self.assertIn("filter(location.search)", js)

    def test_sitemap_lists_every_page(self):
        sm = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        for en, de in site.ROUTES.values():
            self.assertIn(f"<loc>{site.SITE}{en}</loc>", sm)
            self.assertIn(f"<loc>{site.SITE}{de}</loc>", sm)
        for p in site.LEGAL.values():
            self.assertIn(f"<loc>{site.SITE}{p}</loc>", sm)
        for old in site.REDIRECTS:
            self.assertNotIn(f"<loc>{site.SITE}{old}</loc>", sm)

    def test_navigation_reaches_company_products_and_contact(self):
        for lang in ("en", "de"):
            hrefs = {a.get("href") for a in parse(page_file(site.path("home", lang))).all("a")}
            for key in ("company", "products", "contact", "ippc", "dw"):
                self.assertIn(site.path(key, lang), hrefs, (lang, key))
            self.assertIn("/impressum/" if lang == "de" else "/impressum/#legal-notice", hrefs)


class Links(unittest.TestCase):
    def test_internal_links_and_assets_exist(self):
        for f in html_files():
            doc = parse(f)
            urls = [a.get("href") for a in doc.all("a")] + [a.get("href") for a in doc.all("link")] + \
                   [a.get("src") for a in doc.all("img")] + [a.get("src") for a in doc.all("script")]
            for u in filter(None, urls):
                if u.startswith("/") and not u.startswith("//"):
                    with self.subTest(page=str(f.relative_to(ROOT)), url=u):
                        self.assertIsNotNone(resolve(u), u)

    def test_anchors_exist(self):
        for f in CONTENT:
            doc = parse(f)
            ids = {a.get("id") for _, a in doc.tags if a.get("id")}
            for a in doc.all("a"):
                h = a.get("href") or ""
                target = None
                if h.startswith("#") and len(h) > 1:
                    target = f, h[1:]
                elif h.startswith("/") and "#" in h:
                    target = resolve(h), h.split("#", 1)[1]
                if target and target[0]:
                    tid = {x.get("id") for _, x in parse(target[0]).tags if x.get("id")} if target[0] != f else ids
                    with self.subTest(page=str(f.relative_to(ROOT)), href=h):
                        self.assertIn(target[1], tid)

    def test_css_urls_exist(self):
        css = (ROOT / "assets/css/site.css").read_text(encoding="utf-8")
        for u in re.findall(r'url\("?(/[^")]+)"?\)', css):
            self.assertIsNotNone(resolve(u), u)

    def test_external_links_are_https_and_safe(self):
        for f in html_files():
            for _, a in parse(f).tags:
                for attr in ("href", "src"):
                    v = a.get(attr) or ""
                    with self.subTest(page=str(f.relative_to(ROOT)), url=v):
                        self.assertFalse(v.startswith("http://"), v)
                if a.get("target") == "_blank":
                    self.assertIn("noopener", a.get("rel") or "")


class Crest(unittest.TestCase):
    def test_approved_crest_is_unchanged(self):
        data = (ROOT / site.CREST.lstrip("/")).read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(), CREST_SHA256)

    def test_no_other_logo_files(self):
        imgs = {p.name for p in (ROOT / "assets/img").glob("*.png")} | {p.name for p in ROOT.glob("*.png")}
        self.assertEqual(imgs, {"logical-knight-logo.png"})

    def test_lockup_and_one_persistent_seal_on_every_real_page(self):
        for f in CONTENT:
            text = f.read_text(encoding="utf-8")
            doc = parse(f)
            with self.subTest(str(f.relative_to(ROOT))):
                brand = [a for a in doc.all("a") if "brand" in (a.get("class") or "").split()]
                self.assertTrue(brand, "header lockup")
                icons = [a["href"] for a in doc.all("link") if a.get("rel") in ("icon", "apple-touch-icon")]
                self.assertEqual(set(icons), {site.CREST})
                self.assertEqual(text.count('<div class="brand-seal" aria-hidden="true">'), 1)
                self.assertEqual(text.count('class="brand-seal__crest" src="/assets/img/logical-knight-logo.png"'), 1)
                self.assertEqual(len([e for e in doc.all("img") if e.get("class") == "brand-seal__crest"][0].get("alt")), 0)
        for f in REDIRECT_FILES:
            with self.subTest(str(f.relative_to(ROOT))):
                self.assertNotIn("brand-seal", f.read_text(encoding="utf-8"))

    def test_old_hero_crest_and_watermark_are_gone(self):
        css = (ROOT / "assets/css/site.css").read_text(encoding="utf-8")
        for f in html_files():
            text = f.read_text(encoding="utf-8")
            with self.subTest(str(f.relative_to(ROOT))):
                for old in ('class="seal"', 'class="seal__crest"', "seal__rings", 'class="watermark"', "notfound__crest"):
                    self.assertNotIn(old, text)
        for old in (".watermark", "\n.seal {", ".seal__rings", "\n.seal__crest"):
            self.assertNotIn(old, css)

    def test_seal_inscriptions(self):
        words = {"en": ("WE BUILD WITH CARE", "SIMPLE SOFTWARE", "REAL PROBLEMS", "CLEAR SYSTEMS"),
                 "de": ("MIT SORGFALT GEBAUT", "EINFACHE SOFTWARE", "ECHTE PROBLEME", "KLARE SYSTEME")}
        for f in CONTENT:
            text = f.read_text(encoding="utf-8")
            lang = re.search(r'<html lang="(\w+)">', text).group(1)
            with self.subTest(str(f.relative_to(ROOT))):
                for w in words[lang]:
                    self.assertIn(w, text)
                for w in ("CURA", "CLARITAS", "OPUS", "FIDES"):
                    self.assertIn(w, text)
                self.assertEqual(text.count('<textPath href="#lk-seal-ring"'), 1)
                self.assertEqual(text.count('id="lk-seal-ring"'), 1)

    def test_seal_is_fixed_centred_and_never_interactive(self):
        css = (ROOT / "assets/css/site.css").read_text(encoding="utf-8")
        rule = re.search(r"\.brand-seal \{([^}]*)\}", css).group(1)
        for decl in ("position: fixed", "left: 50%", "top: 50%", "transform: translate(-50%, -50%)", "pointer-events: none",
                     "z-index: 0"):
            self.assertIn(decl, rule)
        self.assertRegex(css, r"main, \.site-footer \{[^}]*z-index: 1")
        self.assertRegex(css, r"\.site-header \{[^}]*z-index: 50")

    def test_seal_motion_rings_turn_crest_stays_still(self):
        css = (ROOT / "assets/css/site.css").read_text(encoding="utf-8")
        ring = re.search(r"\.seal__ring \{ animation: turn (\d+)s linear infinite; \}", css)
        outer = re.search(r"\.seal__outer \{ animation: turn-back (\d+)s linear infinite; \}", css)
        self.assertTrue(ring and outer)
        self.assertTrue(38 <= int(ring.group(1)) <= 50, ring.group(1))
        self.assertTrue(55 <= int(outer.group(1)) <= 75, outer.group(1))
        self.assertIn("@keyframes turn { to { transform: rotate(360deg); } }", css)
        self.assertIn("@keyframes turn-back { to { transform: rotate(-360deg); } }", css)
        crest_rules = re.findall(r"\.brand-seal__crest \{([^}]*)\}", css)
        self.assertTrue(crest_rules)
        for r in crest_rules:
            self.assertNotIn("animation", r)
        reduced = css[css.index("@media (prefers-reduced-motion: reduce)"):]
        self.assertIn(".seal__ring, .seal__outer { animation: none; }", reduced)
        self.assertIn("@media (prefers-reduced-motion: no-preference)", css[:css.index(".seal__ring { animation")][-2000:])


class Pages(unittest.TestCase):
    def test_titles_descriptions_and_one_h1(self):
        seen_titles, seen_desc = {}, {}
        for f in CONTENT:
            text = f.read_text(encoding="utf-8")
            doc = parse(f)
            with self.subTest(str(f.relative_to(ROOT))):
                title = re.search(r"<title>(.*?)</title>", text).group(1)
                desc = [a["content"] for a in doc.all("meta") if a.get("name") == "description"]
                self.assertEqual(len(desc), 1)
                self.assertEqual(len(doc.all("h1")), 1)
                self.assertNotIn(title, seen_titles, seen_titles.get(title))
                self.assertNotIn(desc[0], seen_desc, seen_desc.get(desc[0]))
                seen_titles[title] = seen_desc[desc[0]] = f
                self.assertIn('class="skip-link" href="#main"', text)
                self.assertIn('id="main"', text)

    def test_images_have_alt_and_form_fields_have_labels(self):
        for f in CONTENT:
            doc = parse(f)
            labels = {a.get("for") for a in doc.all("label")}
            for img in doc.all("img"):
                self.assertIn("alt", img, f)
            for tag in ("input", "textarea", "select"):
                for field in doc.all(tag):
                    self.assertIn(field.get("id"), labels, (f, field))

    def test_status_badges_only_where_verified(self):
        for lang, statuses in (("en", {"Pilot phase", "Free Early Access"}), ("de", {"Pilotphase", "Kostenloser Vorabzugang"})):
            self.assertEqual({p["status"] for p in site.PRODUCTS[lang]}, statuses)
            self.assertEqual([p["name"] for p in site.PRODUCTS[lang]], ["IPPC Ledger", "Data Workbench"])

    def test_data_workbench_targets(self):
        for lang in ("en", "de"):
            hrefs = {a.get("href") for a in parse(page_file(site.path("dw", lang))).all("a")}
            self.assertIn("https://workbench.logicalknight.com/early-access", hrefs)
            self.assertIn("https://workbench.logicalknight.com/login", hrefs)

    def test_german_data_workbench_page_explains_english_interface(self):
        self.assertIn("nur auf Englisch", page_file("/de/data-workbench/").read_text(encoding="utf-8"))


class ProductOverview(unittest.TestCase):
    """The owner replaced the public example-export ZIP with one product-overview PDF per language."""

    def test_no_public_export_archive(self):
        self.assertEqual(list(ROOT.glob("assets/**/*.zip")), [])
        for f in html_files():
            with self.subTest(str(f.relative_to(ROOT))):
                self.assertNotRegex(f.read_text(encoding="utf-8"), r'href="[^"]+\.zip"|assets/samples/')

    def test_each_language_links_its_one_overview_pdf(self):
        for lang, other in (("de", "en"), ("en", "de")):
            text = page_file(f"/{lang}/ippc-ledger/").read_text(encoding="utf-8")
            own, foreign = site.OVERVIEW[lang], site.OVERVIEW[other]
            with self.subTest(lang):
                self.assertEqual(text.count(f'href="{own}" type="application/pdf"'), 2)  # hero and closing
                self.assertNotIn(foreign, text)
                pdf = (ROOT / own.lstrip("/")).read_bytes()
                self.assertTrue(pdf.startswith(b"%PDF-") and len(pdf) < 1_000_000)

class Copy(unittest.TestCase):
    def test_no_stale_positioning_or_old_assets(self):
        files = html_files() + [ROOT / "assets/js/site.js", ROOT / "assets/css/site.css", ROOT / "sitemap.xml"]
        for f in files:
            text = f.read_text(encoding="utf-8")
            for term in STALE:
                with self.subTest(file=str(f.relative_to(ROOT)), term=term):
                    self.assertNotIn(term, text)

    def test_no_hype_words_in_visible_text(self):
        for f in CONTENT:
            if f.parent.name in ("impressum", "datenschutz"):
                continue
            words = " ".join(parse(f).text).lower()
            for w in HYPE:
                with self.subTest(file=str(f.relative_to(ROOT)), word=w):
                    self.assertNotIn(w, words)

    def test_only_company_addresses(self):
        for f in html_files() + [ROOT / "assets/js/site.js"]:
            found = set(re.findall(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", f.read_text(encoding="utf-8")))
            with self.subTest(str(f.relative_to(ROOT))):
                self.assertLessEqual(found, ALLOWED_EMAILS)

    def test_no_founder_marketing(self):
        terms = re.compile(r"founder|gründer|inhabergeführt|run by its founder|one-man", re.I)
        for f in CONTENT:
            if f.parent.name in ("impressum", "datenschutz"):
                continue
            with self.subTest(str(f.relative_to(ROOT))):
                self.assertIsNone(terms.search(f.read_text(encoding="utf-8")))

    def test_postal_address_only_in_legal_pages(self):
        street = "Große Holl 32"
        for route in site.LEGAL.values():
            with self.subTest(route):
                self.assertIn(street, page_file(route).read_text(encoding="utf-8"))
        for route in site.ROUTES["contact"]:
            with self.subTest(route):
                self.assertNotIn(street, page_file(route).read_text(encoding="utf-8"))

    def test_no_secrets_or_tracking(self):
        pattern = re.compile(r"(api[_-]?key|secret|token|password)\s*[:=]\s*['\"][^'\"]{8,}|googletagmanager|google-analytics|"
                             r"gtag\(|plausible|matomo|hotjar|facebook\.net|localStorage|sessionStorage|document\.cookie", re.I)
        for f in html_files() + [ROOT / "assets/js/site.js"]:
            with self.subTest(str(f.relative_to(ROOT))):
                self.assertIsNone(pattern.search(f.read_text(encoding="utf-8")))

    def test_no_env_files_published(self):
        bad = [p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts and
               (p.name.startswith(".env") or p.suffix in (".pem", ".key"))]
        self.assertEqual(bad, [])


class Analytics(unittest.TestCase):
    """Opt-in reach measurement (Datenschutz 3a): pages load only the consent script; the tracker is never in the HTML,
    so nothing is requested before "Allow". Redirect stubs load nothing (no double counting)."""

    def test_pages_load_only_the_consent_script(self):
        for f in CONTENT:
            with self.subTest(page=str(f.relative_to(ROOT))):
                doc = parse(f)
                srcs = [a.get("src") for a in doc.all("script") if a.get("src")]
                self.assertIn("/assets/js/consent.js", srcs)
                self.assertNotIn(site.UMAMI_SCRIPT, srcs)
                self.assertNotIn("/assets/js/umami-campaign.js", srcs)
                c = next(a for a in doc.all("script") if a.get("src") == "/assets/js/consent.js")
                self.assertEqual(c.get("data-umami-src"), site.UMAMI_SCRIPT)
                self.assertEqual(c.get("data-website-id"), site.UMAMI_WEBSITE_ID)
                self.assertTrue([a for a in doc.all("button") if "data-privacy-settings" in a], "footer privacy settings")
        for f in REDIRECT_FILES:
            self.assertNotIn("consent.js", f.read_text(encoding="utf-8"))

    def test_consent_script_strips_and_gates(self):
        js = (ROOT / "assets/js/consent.js").read_text(encoding="utf-8")
        for needle in ('"exclude-search": "true"', '"exclude-hash": "true"', '"do-not-track": "true"',
                       '"before-send": "gdConsentBeforeSend"', "MAX_AGE_DAYS = 365"):
            self.assertIn(needle, js)
        self.assertNotIn("identify", js)

    def test_campaign_codes_are_plain_codes(self):
        for v in site.CAMPAIGN_CODES.values():
            for code in filter(None, (c.strip() for c in v.split(","))):
                self.assertRegex(code, r"^[a-z0-9][a-z0-9_-]{0,39}$")

    def test_events_carry_only_a_name(self):
        for f in CONTENT:
            for _, a in parse(f).tags:
                if "data-umami-event" in a:
                    self.assertRegex(a["data-umami-event"], r"^[a-z0-9_]{1,40}$")
                    self.assertFalse([k for k in a if k.startswith("data-umami-event-")], "no event properties")


if __name__ == "__main__":
    unittest.main(verbosity=1)
