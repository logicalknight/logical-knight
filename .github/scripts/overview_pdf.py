"""IPPC Ledger product overview: one PDF per language (assets/docs/ippc-ledger-produktueberblick.pdf, -product-overview.pdf).

The PDF is what a visitor downloads from the product page: a short explanation of the product, not an export.
Content follows the approved product overview (ippc-ledger docs/demo/produktueberblick.md) and describes only what is
live; the supplier document request is labelled as a preview until its release is verified live. Screens are the
site's own app screenshots (fictional demo data). Brand: the site's tokens and crest.

Run on a Windows admin PC (Microsoft Edge prints the PDF; CI does not run this):
    python .github/scripts/overview_pdf.py
The committed PDFs are the output; rerun after changing the text below.
"""

from __future__ import annotations

import html
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
OUT = {"de": ROOT / "assets/docs/ippc-ledger-produktueberblick.pdf",
       "en": ROOT / "assets/docs/ippc-ledger-product-overview.pdf"}
SOCIAL = [("LinkedIn", "https://www.linkedin.com/company/logicalknight/", "linkedin.com/company/logicalknight"),
          ("YouTube", "https://www.youtube.com/@LogicalKnightIPPCledger", "youtube.com/@LogicalKnightIPPCledger"),
          ("Facebook", "https://www.facebook.com/profile.php?id=61595424884104",
           "facebook.com/profile.php?id=61595424884104")]
SHOTS = ("app-delivery-incomplete.png", "app-missing-evidence.png", "app-exports.png")

T = {
    "de": {
        "title": "IPPC Ledger – Produktüberblick",
        "kicker": "Produktüberblick",
        "version": "Version 1.0 · Stand 23. Oktober 2026",
        "lead": "IPPC Ledger hält Holzlieferungen, Nachweise von Lieferanten und Behandlung, offene Lücken und Ihre "
                "Aufträge an einem Ort zusammen. So können Sie zu jedem Auftrag zeigen, woher das Holz kam, wie es "
                "behandelt wurde und welche Unterlagen dazu vorliegen.",
        "who_h": "Für wen",
        "who": "Für Betriebe, die Verpackungen aus Holz herstellen oder reparieren und dafür bereits behandeltes Holz "
               "zukaufen: Kistenbau, Paletten, Verpackungsdienstleister. IPPC Ledger ist ein Werkzeug für Ihre "
               "Dokumentation. Es ist keine Behörde, ersetzt keine amtliche Registrierung oder Zertifizierung und "
               "garantiert keine Konformität.",
        "how_h": "So arbeiten Sie damit",
        "steps": [
            ("Lieferanten anlegen", "mit Ermächtigungsnummer, Behörde, Gültigkeit und Dokument."),
            ("Wareneingang erfassen", "Material, Menge und Behandlungsangaben der Lieferung."),
            ("Nachweise anhängen", "Lieferschein, Rechnung und Behandlungsnachweis als Originaldatei."),
            ("Lücken sehen", "Jede fehlende oder widersprüchliche Angabe erscheint mit ihrem Grund."),
            ("Auftrag zuordnen", "Welches Material aus welcher Lieferung in welchen Auftrag ging."),
            ("Prüfen und exportieren", "Datensätze prüfen und für Ihren Kunden einen Export der Nachweise erstellen."),
        ],
        "screens_h": "So sieht es aus",
        "screens_note": "Bildschirme aus der Anwendung mit erfundenen Beispieldaten.",
        "captions": ["Eine Lieferung ist unvollständig: Der Behandlungsnachweis fehlt, mit Grund.",
                     "„Fehlende Nachweise“ zeigt alle offenen Lücken über Lieferungen und Aufträge.",
                     "Export für einen Auftrag, einen Lieferanten oder einen Zeitraum."],
        "status_h": "Stand und Grenzen",
        "status": [
            "Live: Lieferanten und Ermächtigungen, Wareneingänge mit Originalnachweisen, Aufträge mit Rückverfolgung, "
            "Vollständigkeitsprüfung mit Begründung, Prüfvermerke, Export, Deutsch und Englisch.",
            "Vorschau, noch nicht live: Dokumente direkt beim Lieferanten anfordern.",
            "„Vollständig“ heißt: Keine Regel hat eine Lücke gefunden. Es ist keine rechtliche Bewertung. Dateien "
            "ordnet ein Mensch zu, nicht die Software.",
        ],
        "pilot_h": "Pilot",
        "pilot": "IPPC Ledger ist in der Pilotphase und noch nicht allgemein verfügbar. Ein Pilot umfasst einen "
                 "Standort und Ihre eigenen Lieferungen und Aufträge und ist unverbindlich. Die Bedingungen danach "
                 "besprechen wir offen mit Ihnen.",
        "contact_h": "Kontakt",
        "site": "https://logicalknight.com/de/ippc-ledger/",
        "site_label": "Pilot anfragen: logicalknight.com/de/ippc-ledger",
        "follow": "Logical Knight im Netz",
        "footer": "Logical Knight · IPPC Ledger Produktüberblick · Version 1.0, 23.10.2026",
    },
    "en": {
        "title": "IPPC Ledger – Product overview",
        "kicker": "Product overview",
        "version": "Version 1.0 · 23 October 2026",
        "lead": "IPPC Ledger keeps timber deliveries, supplier and treatment evidence, open gaps and your packaging jobs "
                "in one place. For every job you can show where the timber came from, how it was treated and which "
                "documents support it.",
        "who_h": "Who it is for",
        "who": "Companies that make or repair wooden packaging and buy in already-treated timber: crate makers, pallet "
               "makers, packing services. IPPC Ledger is a tool for your own records. It is not an authority, does not "
               "replace an official registration or certification and does not guarantee compliance.",
        "how_h": "How you work with it",
        "steps": [
            ("Add suppliers", "with authorisation number, authority, validity and document."),
            ("Record deliveries", "material, quantity and treatment details of each delivery."),
            ("Attach evidence", "delivery note, invoice and treatment certificate as original files."),
            ("See the gaps", "every missing or conflicting detail is shown with its reason."),
            ("Link jobs", "which material from which delivery went into which job."),
            ("Review and export", "check the records and produce an evidence export for your customer."),
        ],
        "screens_h": "What it looks like",
        "screens_note": "Screens from the application with invented example data.",
        "captions": ["A delivery is incomplete: the treatment certificate is missing, with the reason.",
                     "“Missing evidence” lists every open gap across deliveries and jobs.",
                     "Export for a job, a supplier or a period."],
        "status_h": "Status and limits",
        "status": [
            "Live: suppliers and authorisations, deliveries with original evidence, jobs with traceability, "
            "completeness checks with reasons, review notes, export, German and English.",
            "Preview, not live yet: requesting documents directly from a supplier.",
            "“Complete” means no rule found a gap. It is not a legal assessment. A person matches files, not the "
            "software.",
        ],
        "pilot_h": "Pilot",
        "pilot": "IPPC Ledger is in its pilot phase and not generally available yet. A pilot covers one site and your "
                 "own deliveries and jobs and is non-binding. Terms after the pilot are discussed openly with you.",
        "contact_h": "Contact",
        "site": "https://logicalknight.com/en/ippc-ledger/",
        "site_label": "Request a pilot: logicalknight.com/en/ippc-ledger",
        "follow": "Logical Knight online",
        "footer": "Logical Knight · IPPC Ledger product overview · Version 1.0, 23 Oct 2026",
    },
}


def tokens() -> str:
    """The brand colour variables from the site's own tokens.css (single source)."""
    css = (ROOT / "assets/css/tokens.css").read_text(encoding="utf-8")
    return css[css.index(":root"): css.index("}", css.index(":root")) + 1]


def document(lang: str) -> str:
    t, e = T[lang], html.escape
    shot = lambda i, n: (f'<figure><img src="{(ROOT / "assets/img/ippc" / lang / n).as_uri()}" alt="{e(t["captions"][i])}">'  # noqa: E731
                         f'<figcaption>{e(t["captions"][i])}</figcaption></figure>')
    steps = "".join(f"<li><b>{e(h)}</b> {e(p)}</li>" for h, p in t["steps"])
    social = "".join(f'<li>{name}: <a href="{url}">{e(label)}</a></li>' for name, url, label in SOCIAL)
    return f'''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><title>{e(t["title"])}</title>
<style>
{tokens()}
@page {{ size: A4; margin: 12mm 15mm 13mm; }}
* {{ box-sizing: border-box; }}
body {{ font-family: "Segoe UI", system-ui, -apple-system, Roboto, Arial, sans-serif; color: var(--lk-ink);
        font-size: 10pt; line-height: 1.4; margin: 0; }}
a {{ color: var(--lk-cyan-deep); }}
header {{ display: flex; align-items: center; gap: 12px; border-bottom: 3px solid var(--lk-violet); padding-bottom: 8px; }}
header img {{ width: 46px; height: auto; }}
header .brand {{ font-weight: 700; font-size: 12pt; }}
header .kicker {{ color: var(--lk-text-secondary); font-size: 9.5pt; }}
header .ver {{ margin-left: auto; color: var(--lk-text-muted); font-size: 8.5pt; text-align: right; }}
h1 {{ font-size: 19pt; margin: 10px 0 4px; letter-spacing: -0.01em; }}
h2 {{ font-size: 12pt; color: var(--lk-violet-deep); margin: 10px 0 3px; }}
.lead {{ font-size: 11.5pt; color: var(--lk-charcoal); margin: 0 0 6px; }}
ol {{ margin: 4px 0 0; padding-left: 18px; }} ol li {{ margin: 3px 0; }}
.box {{ background: var(--lk-surface-cool); border-left: 4px solid var(--lk-cyan); padding: 8px 12px; margin-top: 10px; }}
figure {{ margin: 4px 0 8px; break-inside: avoid; }}
figure img {{ width: 100%; border: 1px solid var(--border); border-radius: 4px; }}
figcaption {{ font-size: 9pt; color: var(--lk-text-secondary); margin-top: 2px; }}
.note {{ font-size: 9pt; color: var(--lk-text-muted); margin: 0 0 4px; }}
ul {{ margin: 4px 0 0; padding-left: 18px; }} ul li {{ margin: 3px 0; }}
.page2 {{ break-before: page; }}
.contact {{ display: grid; grid-template-columns: 1fr 1fr; gap: 6px 18px; }}
footer {{ margin-top: 12px; border-top: 1px solid var(--border); padding-top: 6px; font-size: 8.5pt; color: var(--lk-text-muted); }}
</style></head>
<body>
<header><img src="{(ROOT / "assets/img/logical-knight-logo.png").as_uri()}" alt="Logical Knight">
  <div><div class="brand">Logical Knight</div><div class="kicker">IPPC Ledger · {e(t["kicker"])}</div></div>
  <div class="ver">{e(t["version"])}</div></header>
<h1>IPPC Ledger</h1>
<p class="lead">{e(t["lead"])}</p>
<h2>{e(t["who_h"])}</h2><p>{e(t["who"])}</p>
<h2>{e(t["how_h"])}</h2><ol>{steps}</ol>
<h2>{e(t["screens_h"])}</h2><p class="note">{e(t["screens_note"])}</p>
{shot(0, SHOTS[0])}
{shot(1, SHOTS[1])}
<section class="page2">
{shot(2, SHOTS[2])}
<h2>{e(t["status_h"])}</h2><ul>{"".join(f"<li>{e(s)}</li>" for s in t["status"])}</ul>
<div class="box"><h2 style="margin-top:0">{e(t["pilot_h"])}</h2><p style="margin:0">{e(t["pilot"])}</p></div>
<h2>{e(t["contact_h"])}</h2>
<div class="contact">
  <ul><li><a href="{t["site"]}">{e(t["site_label"])}</a></li>
      <li>E-Mail: <a href="mailto:hello@logicalknight.com">hello@logicalknight.com</a></li></ul>
  <div><b>{e(t["follow"])}</b><ul>{social}</ul></div>
</div>
<footer>{e(t["footer"])}</footer>
</section>
</body></html>'''


def main() -> None:
    if not EDGE.exists():
        raise SystemExit(f"Microsoft Edge not found at {EDGE}")
    with tempfile.TemporaryDirectory() as tmp:
        for lang, out in OUT.items():
            src = Path(tmp) / f"overview-{lang}.html"
            src.write_text(document(lang), encoding="utf-8")
            pdf = Path(tmp) / out.name
            subprocess.run([str(EDGE), "--headless", "--disable-gpu", "--no-pdf-header-footer",
                            "--allow-file-access-from-files", f"--user-data-dir={Path(tmp) / 'profile'}",
                            f"--print-to-pdf={pdf}", src.as_uri()], check=True, capture_output=True, timeout=120)
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(pdf, out)
            print(out.relative_to(ROOT), out.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
