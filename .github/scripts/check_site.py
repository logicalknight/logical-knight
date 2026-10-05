"""Site checks (stdlib only): python .github/scripts/check_site.py  -> exit 1 on any finding.

1. Brand translation: every *visible* occurrence of "Logical Knight" and "Agent Research" in page text is inside an
   element with translate="no" (and class "notranslate", which some translators use instead). Head metadata, scripts,
   styles and attribute values are not text a translator can be told to skip, so they are not checked.
2. The rest of the site stays translatable: no page-wide opt-out (<meta name="google" content="notranslate">, or
   translate="no" on <html>/<body>), and most visible text is outside protected elements.
3. Logo: the mark inside a brand link is decorative (alt=""), since the link text names the brand; the link is protected.
4. No unreleased product names anywhere in the published files. They are compared as SHA-256 hashes of each word, so
   this public file does not contain them.
5. Retired product: no links to its pages or API, no payment protocol, and its name only on the retirement notice and
   the privacy policy.
"""

from __future__ import annotations

import hashlib
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BRANDS = ("Logical Knight", "Agent Research")
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
NOT_TEXT = {"head", "script", "style", "title", "noscript", "template", "svg"}
PRIVATE_NAME_HASHES = {
    "3c13cd09a004096bd44d33c9a222a36f04d17367631f38a7b8aef55ec27f49f6",
    "86509897805419e3074775f6b6cf966499f32f580ddb18b558f36312e29e068a",
    "d7a91fac271d7f3e7faf65f736831ff615dba65480dfbb6f95a963b1f88f392c",
    "88cf0d202345600f228548d4279e8b56004892b34502ca718262982a6e2f3e8e",
    "b1d5af756b6365e6f75499362c9239e64a4454dd2af87e028519789ca6255673",
    "184fd1b6c3b4da04918ff221a4ac99377be084f75ea4e196341ce0980312b614",
}
PUBLISHED = {".html", ".js", ".css", ".xml", ".txt", ".json", ".webmanifest", ".md"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, bool]] = []  # (tag, protected)
        self.findings: list[str] = []
        self.protected_chars = self.open_chars = 0
        self.brand_link = False

    def protected(self) -> bool:
        return bool(self.stack) and self.stack[-1][1]

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        translate = a.get("translate")
        protected = (translate == "no") or (translate != "yes" and self.protected())
        classes = (a.get("class") or "").split()
        if translate == "no" and "notranslate" not in classes:
            self.findings.append(f'line {self.getpos()[0]}: <{tag} translate="no"> without class "notranslate"')
        if tag in ("html", "body") and translate == "no":
            self.findings.append(f"line {self.getpos()[0]}: the whole page opts out of translation (<{tag} translate=no>)")
        if tag == "meta" and (a.get("name") or "").lower() in ("google", "googlebot") and "notranslate" in (a.get("content") or ""):
            self.findings.append(f"line {self.getpos()[0]}: page-wide notranslate meta")
        if tag == "a" and "brand" in classes:
            self.brand_link = True
            if not protected:
                self.findings.append(f"line {self.getpos()[0]}: brand link (logo) is not protected from translation")
        if tag == "img" and self.brand_link and a.get("alt") != "":
            self.findings.append(f'line {self.getpos()[0]}: logo mark must be decorative (alt=""); the link already names the brand')
        if tag not in VOID:
            self.stack.append((tag, protected))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.stack.pop()

    def handle_endtag(self, tag):
        if tag == "a":
            self.brand_link = False
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        if any(t in NOT_TEXT for t, _ in self.stack) or not data.strip():
            return
        if self.protected():
            self.protected_chars += len(data.strip())
            return
        self.open_chars += len(data.strip())
        for brand in BRANDS:
            if brand in data:
                self.findings.append(f"line {self.getpos()[0]}: unprotected visible brand name {brand!r}: {data.strip()[:80]!r}")


def check_page(path: Path) -> list[str]:
    page = Page()
    page.feed(path.read_text(encoding="utf-8"))
    page.close()
    findings = [f"{path.relative_to(ROOT)}: {f}" for f in page.findings]
    total = page.open_chars + page.protected_chars
    if total >= 500 and page.open_chars / total < 0.8:  # tiny pages (404) are mostly the brand itself
        findings.append(f"{path.relative_to(ROOT)}: only {page.open_chars / total:.0%} of visible text is translatable")
    return findings


def check_private_names(path: Path) -> list[str]:
    words = re.findall(r"[A-Za-z0-9]+", path.read_text(encoding="utf-8", errors="replace"))
    hits = {w for w in words if hashlib.sha256(w.casefold().encode()).hexdigest() in PRIVATE_NAME_HASHES}
    return [f"{path.relative_to(ROOT)}: unreleased product name present ({len(hits)} distinct)"] if hits else []


RETIRED_ALLOWED = {"agent-research/index.html", "datenschutz/index.html"}
RETIRED_TERMS = ("api.logicalknight.com", "x402", 'href="/agent-research/', "og-agent-research", "Agent Research")


def check_retired(path: Path) -> list[str]:
    rel = path.relative_to(ROOT).as_posix()
    text = path.read_text(encoding="utf-8", errors="replace")
    terms = RETIRED_TERMS[:-1] if rel in RETIRED_ALLOWED else RETIRED_TERMS
    return [f"{rel}: retired product reference {t!r}" for t in terms if t in text]


def main() -> int:
    files = [p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.relative_to(ROOT).parts[:1] and not any(
        part.startswith((".", "_")) for part in p.relative_to(ROOT).parts)]  # what GitHub Pages (Jekyll) publishes
    findings = []
    for path in files:
        if path.suffix == ".html":
            findings += check_page(path)
        if path.suffix in PUBLISHED:
            findings += check_private_names(path)
        if path.suffix in PUBLISHED and path.name != "check_site.py":
            findings += check_retired(path)
    for f in findings:
        print(f)
    pages = sum(p.suffix == ".html" for p in files)
    print(f"checked {pages} pages and {sum(p.suffix in PUBLISHED for p in files)} published text files: "
          f"{'OK' if not findings else f'{len(findings)} finding(s)'}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
