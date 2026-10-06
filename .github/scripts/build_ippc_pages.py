"""Generates the IPPC Ledger product pages in German and English from one structure, so both languages always carry
the same information. Edit the content here, then run:

    python .github/scripts/build_ippc_pages.py

Writes: de/ippc-ledger/, en/ippc-ledger/, de/ippc-ledger/erste-schritte/, en/ippc-ledger/getting-started/, and the
redirect at ippc-ledger/. Every statement describes behaviour that exists in IPPC Ledger (checked against the
product); screenshots are real screens with fictional demo data. Not published (dot directory).
"""

from __future__ import annotations

from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = "https://app.logicalknight.com"
STAFF = "https://staff.logicalknight.com"
# False until https://app.logicalknight.com and https://staff.logicalknight.com answer: the pages then offer the pilot by
# e-mail and show no login links (nothing points at an address that does not exist). When the application is online,
# set True and rebuild; the site check (--live) then verifies every application link before the pages can be published.
APP_ONLINE = False
EMAIL = "logicalknight0@gmail.com"
SUBJECT = {"de": "Pilot%20IPPC%20Ledger", "en": "IPPC%20Ledger%20pilot"}


def pilot_href(lang: str) -> str:
    return f"{APP}/pilot?lang={lang}" if APP_ONLINE else f"mailto:{EMAIL}?subject={SUBJECT[lang]}"


def legal_links(c: dict) -> str:
    """Only pages that exist: the Impressum appears once the owner's details are in (impressum/index.html)."""
    items = [(h, t) for h, t in c["legal"] if h != "/impressum/" or (ROOT / "impressum" / "index.html").exists()]
    staff = f'<li><a href="{STAFF}/login">{c["staff"]}</a></li>' if APP_ONLINE else ""
    return "".join(f'<li><a href="{h}">{t}</a></li>' for h, t in items) + staff

LK = '<span translate="no" class="notranslate">Logical Knight</span>'
SAMPLE = {"de": "/assets/samples/ippc-ledger-beispiel-export.zip", "en": "/assets/samples/ippc-ledger-sample-export.zip"}
IP = '<span translate="no" class="notranslate">IPPC Ledger</span>'


def e(s: str) -> str:
    """Escaped visible text with the brand names protected from page translation."""
    return escape(s).replace("IPPC Ledger", IP).replace("Logical Knight", LK)


def img_size(path: str) -> tuple[int, int]:
    data = (ROOT / path.lstrip("/")).read_bytes()
    return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")  # PNG IHDR


def figure(name: str, alt: str, caption: str, lang: str) -> str:
    """A real screen of the application in the page's language (fictional demo data)."""
    src = f"/assets/img/ippc/{lang}/{name}"
    w, h = img_size(src)
    return (f'<figure class="shot" data-reveal><a href="{src}"><img src="{src}" width="{w}" '
            f'height="{h}" loading="lazy" alt="{escape(alt)}"></a><figcaption>{caption}</figcaption></figure>')


T = {
    "de": {
        "path": "/de/ippc-ledger/", "other": "/en/ippc-ledger/", "gs": "/de/ippc-ledger/erste-schritte/", "gs_other": "/en/ippc-ledger/getting-started/",
        "home": "/de/", "switch": "English", "switch_lang": "en",
        "title": "IPPC Ledger: Wareneingänge und ISPM-15-Nachweise an einem Ort · Logical Knight",
        "desc": "Für Holzverpackungsbetriebe, die behandeltes Holz zukaufen: Lieferungen mit Lieferantennachweisen verknüpfen, fehlende Unterlagen sehen und die Dokumentation für einen Zeitraum exportieren. Pilotphase.",
        "nav": [("#ablauf", "Ablauf"), ("#beispiel", "Beispiel"), ("#pilot", "Pilot"), ("#faq", "Fragen")],
        "login": "Anmelden", "skip": "Zum Inhalt", "pilot_btn": "Pilot anfragen", "example_btn": "Beispiel ansehen",
        "eyebrow": "Pilotphase",
        "h1": 'Wareneingänge und ISPM-15-Nachweise <span class="serif">an einem Ort.</span>',
        "lede": "Für Holzverpackungsbetriebe, die behandeltes Holz zukaufen: Verknüpfen Sie Lieferungen mit Lieferantennachweisen, behalten Sie fehlende Unterlagen im Blick und stellen Sie die Dokumentation für einen ausgewählten Zeitraum zusammen.",
        "status": "Pilotphase: noch nicht allgemein verfügbar. Kein Behördendienst, keine Bescheinigung, keine rechtliche Bewertung.",
        "problem_eyebrow": "Das Problem",
        "problem_h": "Die Nachweise gibt es. <span class=\"serif gold\">Nur nicht an einer Stelle.</span>",
        "problem": [
            ("Lieferscheine im Ordner", "Wann kam welches Holz, von wem, wie viel? Die Antwort steht auf Papier oder in einem Scan irgendwo auf dem Laufwerk."),
            ("Ermächtigungen im Postfach", "Die Ermächtigung des Behandlungsbetriebs kam als PDF per E-Mail. Gilt sie noch, und für welche Lieferungen?"),
            ("Behandlungsangaben in Tabellen", "Verfahren, Dauer, Charge: in einer Tabelle, die nur eine Person versteht."),
            ("Und dann die Frage", "Welches Holz steckt in diesem Auftrag, und wo sind die Belege dafür? Das Zusammensuchen kostet Zeit, und Lücken fallen spät auf."),
        ],
        "flow_eyebrow": "Ablauf",
        "flow_h": "Fünf Schritte, <span class=\"serif gold\">vom Wareneingang zum Export.</span>",
        "flow": [
            ("Holz empfangen", "Wareneingang erfassen: Empfangsdatum, Lieferant, Absender laut Lieferschein, Holzart, Menge mit Einheit oder Masse in kg, Behandlungsverfahren und -angaben."),
            ("Nachweise verknüpfen", "Lieferschein, Rechnung und Behandlungsnachweis als PDF oder Foto an die Lieferung hängen; die Ermächtigung des Lieferanten mit Nummer, Behörde und Gültigkeit laut Dokument."),
            ("Material dem Auftrag zuordnen", "Welches Material in welchem Verpackungsauftrag steckt, in der Einheit der Lieferung. Es wird nichts umgerechnet, und mehr als geliefert lässt sich nicht zuordnen."),
            ("Fehlendes prüfen", "Jede Lücke erscheint mit ihrem Grund, etwa „Kein Behandlungsnachweis angehängt“. Dokumente werden von einer Person geprüft; ein abgelehntes Dokument zählt nicht mehr."),
            ("Auswahl exportieren", "Für einen Auftrag, einen Lieferanten oder einen Zeitraum: ein ZIP mit den Originaldateien, Übersicht als PDF und CSV, Zuordnung jeder Datei und Verlauf."),
        ],
        "ex_eyebrow": "Beispiel mit fiktiven Daten",
        "ex_h": "So sieht es in <span class=\"serif gold\">IPPC Ledger</span> aus.",
        "ex_lede": "Echte Bildschirme der Anwendung mit erfundenen Firmen und Musterdokumenten. Die Anwendung gibt es auf Deutsch und Englisch; diese Bilder zeigen die deutsche Oberfläche.",
        "shots": [
            ("app-delivery-incomplete.png", "Lieferung WE-DEMO-002 mit Status Unvollständig: kein Behandlungsnachweis angehängt",
             "<strong>Fehlende Nachweise mit Grund.</strong> Die fiktive Lieferung WE-DEMO-002 ist unvollständig: Der Behandlungsnachweis fehlt. Sobald er angehängt ist, wechselt der Status."),
            ("app-documents-review.png", "Dokumententabelle mit geprüftem Lieferschein, abgelehnter und neuer Version des Behandlungsnachweises",
             "<strong>Vorhanden, geprüft, abgelehnt: getrennt.</strong> Ein falscher Behandlungsnachweis wurde mit Grund abgelehnt und bleibt als ersetzte Version im Verlauf; die neue Version wurde geprüft."),
            ("app-job-trace.png", "Auftrag AUF-DEMO-101 mit verknüpftem Material und Nachweiskette",
             "<strong>Vom Auftrag zum Beleg.</strong> Auftrag AUF-DEMO-101 nutzt 120 Stk aus WE-DEMO-001 und 200 Stk aus WE-DEMO-003; darunter Lieferant, Ermächtigung und alle Dokumente."),
            ("app-history-correction.png", "Verlauf einer Lieferung mit Korrektur der Lieferscheinnummer und Grund",
             "<strong>Korrekturen mit Grund.</strong> Die Lieferscheinnummer wurde korrigiert: alter Wert, neuer Wert, Person, Zeitpunkt und Grund bleiben sichtbar."),
            ("app-missing-evidence.png", "Liste „Fehlende Nachweise“ mit allen offenen Lücken",
             "<strong>Alle Lücken auf einen Blick.</strong> „Fehlende Nachweise“ listet jede offene Lücke über alle Wareneingänge und Aufträge."),
            ("app-supplier-authorisation.png", "Lieferant mit Ermächtigung ohne Ablaufdatum und interner Prüferinnerung",
             "<strong>Erinnerung ist kein Ablaufdatum.</strong> Diese Ermächtigung nennt kein Ende; die interne Erinnerung zur erneuten Prüfung ist getrennt davon."),
        ],
        "pack_eyebrow": "Der Export",
        "pack_h": "Was im <span class=\"serif gold\">Export</span> steckt.",
        "pack_lede": "Ein Export für einen Zeitraum, einen Lieferanten oder einen Auftrag ist ein ZIP-Archiv. Das Beispiel enthält die fiktiven Lieferungen der letzten 60 Tage.",
        "pack": [
            ("documents/", "Die Originaldateien, unverändert und per Prüfsumme (SHA-256) kontrolliert, auch ersetzte Versionen."),
            ("summary.pdf", "Eine druckbare Übersicht: Aufträge und Lieferungen mit Status und jeder offenen Lücke."),
            ("manifest.csv", "Zu jeder Datei: Lieferung, Lieferant, Material, Auftrag, Prüfstatus und Prüfsumme."),
            ("deliveries.csv, material.csv, jobs.csv, suppliers.csv", "Die Datensätze als Tabelle, sicher gegen Formel-Einschleusung in Tabellenkalkulationen."),
            ("completeness.csv", "Jede fehlende oder nicht feststellbare Angabe mit Regel und Grund."),
            ("audit.csv", "Der Verlauf der enthaltenen Datensätze, mit dem Grund jeder Korrektur."),
        ],
        "pack_note": "Unvollständiges wird nicht versteckt: Es steht mit Grund in der Übersicht und in completeness.csv. Ein Zeitraum ohne Lieferungen ergibt keinen leeren Export, sondern einen Hinweis.",
        "pack_dl": "Beispiel-Export herunterladen (ZIP, fiktive Daten)",
        "feat_eyebrow": "Was Sie damit tun",
        "feat_h": "Nach Aufgaben, <span class=\"serif gold\">nicht nach Technik.</span>",
        "features": [
            ("Lieferanten und Ermächtigungen führen", "Ermächtigung mit Nummer, Behörde und Dokument. Ein Ablaufdatum nur, wenn das Dokument eines nennt; die Übersicht zeigt gültig, läuft ab oder abgelaufen."),
            ("Wareneingänge erfassen", "Eine Lieferung mit allen Materialpositionen in einem Schritt, Dokumente gleich dazu. Fehler beim Speichern verlieren keine Eingaben."),
            ("Dokumente prüfen", "Prüfen, ablehnen mit Grund, Abgleich mit der Quelle vermerken. Hochladen allein bestätigt nichts."),
            ("Aufträge nachvollziehen", "Material mit Menge und Einheit dem Auftrag zuordnen; der Auftrag zeigt die vollständige Nachweiskette."),
            ("Lücken schließen", "Unvollständig, Hinweis, nicht feststellbar: jeweils mit dem genauen Grund und einer Übersicht über alles Offene."),
            ("Korrigieren mit Verlauf", "Erfasste Werte ändern nur mit Grund. Dokumente werden nie überschrieben; jede Version bleibt."),
            ("Bestehende Tabellen übernehmen", "Lieferanten, Wareneingänge und Aufträge aus CSV oder Excel, mit Vorlage, Vorschau jeder Zeile und Bestätigung."),
            ("Mit Rollen arbeiten", "Inhaber, Verwaltung, Bearbeitung, nur Lesen. Jeder Betrieb sieht nur seine eigenen Daten."),
        ],
        "gs_eyebrow": "Einstieg",
        "gs_h": "Was Sie <span class=\"serif gold\">mitbringen.</span>",
        "gs_items": [
            ("Die Ermächtigungen Ihrer Lieferanten", "als PDF oder Foto, mit Nummer und Behörde."),
            ("Lieferscheine und Behandlungsnachweise", "der Lieferungen, die Sie erfassen möchten."),
            ("Ihre laufenden Aufträge", "mit Auftragsnummer, optional Kunde und Kundenreferenz."),
            ("Vorhandene Tabellen, falls es sie gibt", "Lieferanten, Wareneingänge oder Aufträge als CSV/Excel; Vorlagen stehen in der Anwendung bereit."),
        ],
        "gs_text": "Sie erfassen in der Anwendung oder importieren Tabellen. PDFs werden angehängt, nicht automatisch ausgelesen. Eine Checkliste auf der Startseite führt durch die ersten Schritte; die <a href=\"{gs}\">Anleitung</a> zeigt Erfassen, Anhängen, Korrigieren und Exportieren. Fragen per E-Mail an <a href=\"mailto:logicalknight0@gmail.com\">logicalknight0@gmail.com</a>.",
        "data_eyebrow": "Daten und Zugriff",
        "data_h": "Ihre Daten bleiben <span class=\"serif gold\">Ihre Daten.</span>",
        "data": [
            ("Getrennt", "Jeder Betrieb hat einen eigenen Bereich. Die Trennung ist zusätzlich in der Datenbank selbst durchgesetzt, nicht nur in der Anwendung."),
            ("Mit Anmeldung", "Zugang nur mit persönlichem Konto und Rolle; Konten legt der Inhaber des Betriebs an. Keine öffentliche Registrierung."),
            ("Originale bleiben Originale", "Hochgeladene Dateien werden nicht verändert; eine Prüfsumme belegt das im Export."),
            ("Nachvollziehbar", "Jede Änderung mit Person und Zeitpunkt, jede Korrektur mit Grund."),
            ("Jederzeit exportierbar", "Inhaber und Verwaltung können den gesamten Datenbestand jederzeit exportieren, auch beim Abschied."),
            ("Speicherort und Sicherung", "Wo die Anwendung im Pilotbetrieb läuft und wie Datenbank und Dateien gesichert werden, teilen wir vor dem Start schriftlich mit. Wir nennen hier nichts, was noch nicht eingerichtet ist."),
        ],
        "pilot_eyebrow": "Pilot",
        "pilot_h": "Mit Ihren eigenen <span class=\"serif gold\">Lieferungen testen.</span>",
        "pilot_scope": "Ein Pilot umfasst einen Standort und Ihre eigenen Lieferungen und Aufträge. Er ist unverbindlich; Konditionen nach dem Pilot besprechen wir offen, bevor etwas gilt.",
        "pilot_steps": [
            ("Anfrage", "Sie schreiben uns eine E-Mail (Pilot anfragen). Wir antworten per E-Mail." if not APP_ONLINE else "Sie schicken das Formular. Wir melden uns per E-Mail."),
            ("Gespräch", "Wir klären, wie Sie heute arbeiten und was Sie erfassen möchten."),
            ("Zugang", "Sie erhalten eine Einladung per E-Mail und legen Ihr Passwort selbst fest."),
            ("Erfassen", "Lieferanten, Wareneingänge und Aufträge, per Hand oder per Import."),
            ("Auswertung", "Gemeinsam: Was hat es gebracht, was fehlt?"),
        ],
        "faq_eyebrow": "Fragen",
        "faq_h": "Häufige <span class=\"serif gold\">Fragen.</span>",
        "faq": [
            ("Für wen ist IPPC Ledger?", "Für Betriebe, die Verpackungen aus Holz nach ISPM 15 herstellen oder reparieren und dafür behandeltes Holz zukaufen. Es ordnet Nachweise; es steuert keine Behandlungsanlage und ist kein ERP- oder Buchhaltungssystem."),
            ("Was müssen wir eingeben?", "Lieferanten mit ihren Ermächtigungen, je Wareneingang Empfangsdatum, Lieferant, Holzart, Menge mit Einheit oder Masse und die Behandlungsangaben, dazu die Dokumente. Für Aufträge die Auftragsnummer und das verwendete Material."),
            ("Können wir vorhandene Tabellen und PDFs mitbringen?", "Ja. Lieferanten, Wareneingänge und Aufträge lassen sich aus CSV oder Excel importieren, mit Vorschau und Bestätigung; doppelte Einträge werden erkannt, nichts wird überschrieben. PDFs und Fotos werden an die Datensätze angehängt, aber nicht automatisch ausgelesen."),
            ("Bestätigt das Hochladen ein Dokument?", "Nein. Hochgeladen heißt nur: vorhanden. Ob es das richtige, lesbare Dokument ist, vermerkt eine Person als geprüft; einen Abgleich mit der Quelle vermerkt sie getrennt davon. Es gibt keine automatische Echtheitsprüfung."),
            ("Was passiert, wenn ein Nachweis fehlt oder abgelehnt wird?", "Die Lieferung und jeder Auftrag, der ihr Material nutzt, werden als unvollständig mit dem genauen Grund angezeigt. Ein abgelehntes Dokument zählt nicht mehr als Nachweis; es bleibt im Verlauf, bis eine neue Version hochgeladen ist."),
            ("Was enthält der Export?", "Die Originaldateien, eine PDF-Übersicht, die Datensätze als CSV, die Zuordnung jeder Datei, alle offenen Lücken und den Verlauf mit Korrekturgründen. Den Inhalt zeigt der Beispiel-Export oben."),
            ("Wer kann unsere Daten sehen?", "Die Personen, die der Inhaber Ihres Betriebs einlädt, jeweils mit ihrer Rolle. Andere Betriebe sehen nichts davon. Logical Knight richtet Zugänge ein, liest Ihre Dokumente aber nicht."),
            ("Können wir unsere Daten mitnehmen, wenn wir aufhören?", "Ja. Der vollständige Export enthält alle Datensätze, alle Dokumentversionen und den gesamten Verlauf. Nach einer Kündigung bleibt der Zugang 30 Tage bestehen, danach werden die Daten gelöscht."),
            ("Wie fragen wir einen Pilot an?", ("Per E-Mail an logicalknight0@gmail.com („Pilot anfragen“)." if not APP_ONLINE else "Über das Formular „Pilot anfragen“.") + " Wir antworten per E-Mail; danach erhalten Sie eine Einladung zu Ihrem eigenen Bereich."),
        ],
        "final_h": "Lieber selbst ansehen?",
        "final_text": "Schauen Sie sich den Beispiel-Export an, oder fragen Sie einen Pilot an. Fragen gern an <a href=\"mailto:logicalknight0@gmail.com\">logicalknight0@gmail.com</a>.",
        "staff": "Mitarbeiterzugang", "legal": [("/impressum/", "Impressum"), ("/datenschutz/", "Datenschutz"), ("/kontakt/", "Kontakt")],
        "fictional": "Alle Beispiele, Firmen und Dokumente auf dieser Seite sind erfunden.",
    },
    "en": {
        "path": "/en/ippc-ledger/", "other": "/de/ippc-ledger/", "gs": "/en/ippc-ledger/getting-started/", "gs_other": "/de/ippc-ledger/erste-schritte/",
        "home": "/", "switch": "Deutsch", "switch_lang": "de",
        "title": "IPPC Ledger: keep timber deliveries and ISPM 15 records together · Logical Knight",
        "desc": "For wood-packaging businesses that buy treated timber: connect deliveries with supplier evidence, see which documents are missing and export the records for a selected period. Pilot phase.",
        "nav": [("#how", "How it works"), ("#example", "Example"), ("#pilot", "Pilot"), ("#faq", "FAQ")],
        "login": "Log in", "skip": "Skip to content", "pilot_btn": "Request a pilot", "example_btn": "See an example",
        "eyebrow": "Pilot phase",
        "h1": 'Keep timber deliveries and ISPM 15 records <span class="serif">together.</span>',
        "lede": "For wood-packaging businesses that buy treated timber. Connect deliveries with supplier evidence, see which documents are missing and export the records for a selected period.",
        "status": "Pilot phase: not generally available yet. Not an authority, no certificates, no legal assessment.",
        "problem_eyebrow": "The problem",
        "problem_h": "The evidence exists. <span class=\"serif gold\">Just not in one place.</span>",
        "problem": [
            ("Delivery notes in binders", "Which timber arrived when, from whom, how much? The answer is on paper or in a scan somewhere on a drive."),
            ("Authorisations in the inbox", "The treatment provider's authorisation came as a PDF by e-mail. Is it still valid, and for which deliveries?"),
            ("Treatment details in spreadsheets", "Method, duration, batch: in a spreadsheet only one person understands."),
            ("And then the question", "Which timber went into this job, and where is the evidence? Collecting it takes time, and gaps show up late."),
        ],
        "flow_eyebrow": "How it works",
        "flow_h": "Five steps, <span class=\"serif gold\">from delivery to export.</span>",
        "flow": [
            ("Receive timber", "Record the delivery: receipt date, supplier, sender as on the delivery note, wood type, quantity with its unit or mass in kg, treatment method and details."),
            ("Link the evidence", "Attach delivery note, invoice and treatment evidence as PDF or photo; record the supplier's authorisation with number, authority and validity as stated in the document."),
            ("Link material to a job", "Which material went into which packaging job, in the delivery's unit. Nothing is converted, and you cannot assign more than was delivered."),
            ("Review what is missing", "Each gap appears with its reason, such as “No treatment evidence is attached”. A person reviews documents; a rejected document no longer counts."),
            ("Export a selection", "For a job, a supplier or a period: a ZIP with the original files, a PDF and CSV summary, where each file belongs, and the history."),
        ],
        "ex_eyebrow": "Example with fictional data",
        "ex_h": "What it looks like in <span class=\"serif gold\">IPPC Ledger</span>.",
        "ex_lede": "Real screens of the application with invented companies and sample documents. The application is available in German and English; these images show the English interface.",
        "shots": [
            ("app-delivery-incomplete.png", "Delivery WE-DEMO-002 marked incomplete: no treatment evidence attached",
             "<strong>Missing evidence, with the reason.</strong> The fictional delivery WE-DEMO-002 is incomplete because its treatment evidence is missing. Once it is attached, the status changes."),
            ("app-documents-review.png", "Document table with a reviewed delivery note, a rejected and a new version of the treatment evidence",
             "<strong>Present, reviewed, rejected: kept apart.</strong> A wrong treatment record was rejected with a reason and stays in the history as a superseded version; the new version was reviewed."),
            ("app-job-trace.png", "Job AUF-DEMO-101 with linked material and its evidence chain",
             "<strong>From the job to the evidence.</strong> Job AUF-DEMO-101 uses 120 pieces from WE-DEMO-001 and 200 from WE-DEMO-003; below are the supplier, authorisation and every document."),
            ("app-history-correction.png", "Delivery history with a corrected delivery-note number and its reason",
             "<strong>Corrections with a reason.</strong> The delivery-note number was corrected: old value, new value, person, time and reason stay visible."),
            ("app-missing-evidence.png", "Missing Evidence list with every open gap",
             "<strong>Every gap at a glance.</strong> “Missing Evidence” lists each open gap across deliveries and jobs."),
            ("app-supplier-authorisation.png", "Supplier with an authorisation without end date and an internal review reminder",
             "<strong>A reminder is not an expiry.</strong> This authorisation states no end date; the internal reminder to look at it again is kept separate."),
        ],
        "pack_eyebrow": "The export",
        "pack_h": "What is in an <span class=\"serif gold\">export.</span>",
        "pack_lede": "An export for a period, a supplier or a job is a ZIP archive. The example holds the fictional deliveries of the last 60 days.",
        "pack": [
            ("documents/", "The original files, unchanged and checked by checksum (SHA-256), including superseded versions."),
            ("summary.pdf", "A printable overview: jobs and deliveries with their status and every open gap."),
            ("manifest.csv", "For each file: delivery, supplier, material, job, review status and checksum."),
            ("deliveries.csv, material.csv, jobs.csv, suppliers.csv", "The records as tables, safe against formula injection in spreadsheets."),
            ("completeness.csv", "Every missing or unestablished item with its rule and reason."),
            ("audit.csv", "The history of the included records, with the reason for each correction."),
        ],
        "pack_note": "Incomplete items are not hidden: they appear with their reason in the summary and in completeness.csv. A period without deliveries gives a message, not an empty archive.",
        "pack_dl": "Download the sample export (ZIP, fictional data)",
        "feat_eyebrow": "What you can do",
        "feat_h": "Grouped by task, <span class=\"serif gold\">not by technology.</span>",
        "features": [
            ("Keep suppliers and authorisations", "Authorisation with number, authority and document. An end date only if the document states one; the overview shows valid, expiring or expired."),
            ("Record incoming deliveries", "One delivery with all its material lines in one step, documents included. A validation error never loses what you typed."),
            ("Review documents", "Review, reject with a reason, record a check against the source. Uploading alone confirms nothing."),
            ("Trace jobs", "Link material to a job with quantity and unit; the job shows its complete evidence chain."),
            ("Close the gaps", "Incomplete, needs attention, not establishable: each with its exact reason, plus one list of everything open."),
            ("Correct with history", "Recorded values change only with a reason. Documents are never overwritten; every version stays."),
            ("Bring your spreadsheets", "Suppliers, deliveries and jobs from CSV or Excel, with a template, a preview of every row and your confirmation."),
            ("Work with roles", "Owner, admin, worker, read only. Each business sees only its own data."),
        ],
        "gs_eyebrow": "Getting started",
        "gs_h": "What to <span class=\"serif gold\">bring.</span>",
        "gs_items": [
            ("Your suppliers' authorisations", "as PDF or photo, with number and authority."),
            ("Delivery notes and treatment evidence", "for the deliveries you want to record."),
            ("Your current jobs", "with job number, optionally customer and customer reference."),
            ("Existing spreadsheets, if you have them", "suppliers, deliveries or jobs as CSV/Excel; templates are in the application."),
        ],
        "gs_text": "You enter records in the application or import spreadsheets. PDFs are attached, not read automatically. A checklist on the start page leads through the first steps; the <a href=\"{gs}\">guide</a> shows entering, attaching, correcting and exporting. Questions by e-mail to <a href=\"mailto:logicalknight0@gmail.com\">logicalknight0@gmail.com</a>.",
        "data_eyebrow": "Data and access",
        "data_h": "Your data stays <span class=\"serif gold\">your data.</span>",
        "data": [
            ("Separated", "Each business has its own area. The separation is also enforced in the database itself, not only in the application."),
            ("Behind a login", "Access only with a personal account and role; accounts are created by the business's owner. No public sign-up."),
            ("Originals stay originals", "Uploaded files are not changed; a checksum proves it in the export."),
            ("Traceable", "Every change with person and time, every correction with its reason."),
            ("Exportable at any time", "Owners and admins can export everything at any time, also when leaving."),
            ("Location and backups", "Where the application runs during the pilot and how the database and files are backed up, we confirm in writing before you start. We do not state anything here that is not set up yet."),
        ],
        "pilot_eyebrow": "Pilot",
        "pilot_h": "Test it with your own <span class=\"serif gold\">deliveries.</span>",
        "pilot_scope": "A pilot covers one site and your own deliveries and jobs. It is without obligation; terms after the pilot are discussed openly before anything applies.",
        "pilot_steps": [
            ("Request", "You e-mail us (Request a pilot). We reply by e-mail." if not APP_ONLINE else "You send the form. We reply by e-mail."),
            ("Conversation", "We clarify how you work today and what you want to record."),
            ("Access", "You receive an invitation by e-mail and set your own password."),
            ("Record", "Suppliers, deliveries and jobs, by hand or by import."),
            ("Review", "Together: what did it bring, what is missing?"),
        ],
        "faq_eyebrow": "FAQ",
        "faq_h": "Frequently asked <span class=\"serif gold\">questions.</span>",
        "faq": [
            ("Who is IPPC Ledger for?", "For businesses that make or repair ISPM 15 wooden packaging and buy treated timber for it. It organises evidence; it does not control a treatment kiln and is not an ERP or accounting system."),
            ("What must we enter?", "Suppliers with their authorisations; for each delivery the receipt date, supplier, wood type, quantity with unit or mass, and the treatment details, plus the documents. For jobs the job number and the material used."),
            ("Can we bring existing spreadsheets and PDFs?", "Yes. Suppliers, deliveries and jobs can be imported from CSV or Excel with a preview and your confirmation; duplicates are detected and nothing is overwritten. PDFs and photos are attached to records but not read automatically."),
            ("Does uploading a file verify it?", "No. Uploaded only means present. A person marks whether it is the right, legible document; a check against the source is recorded separately. There is no automatic authenticity check."),
            ("What happens when evidence is missing or rejected?", "The delivery, and every job that uses its material, is shown as incomplete with the exact reason. A rejected document no longer counts as evidence; it stays in the history until a new version is uploaded."),
            ("What does the export contain?", "The original files, a PDF summary, the records as CSV, where each file belongs, every open gap and the history with correction reasons. The sample export above shows the contents."),
            ("Who can access our records?", "The people your business's owner invites, each with their role. Other businesses see none of it. Logical Knight sets up access but does not read your documents."),
            ("Can we export our records when leaving?", "Yes. The complete export holds every record, every document version and the full history. After you close the account, access stays for 30 days; then the data is deleted."),
            ("How do we request and start a pilot?", ("By e-mail to logicalknight0@gmail.com (“Request a pilot”)." if not APP_ONLINE else "With the “Request a pilot” form.") + " We reply by e-mail; then you receive an invitation to your own area."),
        ],
        "final_h": "Rather see for yourself?",
        "final_text": "Look at the sample export, or request a pilot. Questions to <a href=\"mailto:logicalknight0@gmail.com\">logicalknight0@gmail.com</a>.",
        "staff": "Staff access", "legal": [("/impressum/", "Legal notice"), ("/datenschutz/", "Privacy"), ("/kontakt/", "Contact")],
        "fictional": "All examples, companies and documents on this page are invented.",
    },
}


def head(c: dict, lang: str, title: str, desc: str, path: str, other: str) -> str:
    alt_lang = c["switch_lang"]
    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(desc)}">
  <link rel="canonical" href="https://logicalknight.com{path}">
  <link rel="alternate" hreflang="{lang}" href="https://logicalknight.com{path}">
  <link rel="alternate" hreflang="{alt_lang}" href="https://logicalknight.com{other}">
  <meta name="theme-color" content="#0a0a0b">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Logical Knight">
  <meta property="og:title" content="{escape(title)}">
  <meta property="og:description" content="{escape(desc)}">
  <meta property="og:url" content="https://logicalknight.com{path}">
  <meta property="og:image" content="https://logicalknight.com/assets/img/og.png">
  <meta property="og:locale" content="{'de_DE' if lang == 'de' else 'en_GB'}">
  <link rel="icon" type="image/png" sizes="32x32" href="/assets/img/favicon-32.png">
  <link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
  <link rel="preload" href="/assets/fonts/instrument-sans.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="/assets/fonts/instrument-serif-italic.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="/assets/css/site.css">
  <script>document.documentElement.classList.add("js")</script>
</head>
<body>
  <a class="skip-link" href="#main">{c["skip"]}</a>
'''


def nav(c: dict, lang: str, other: str, items: list[tuple[str, str]]) -> str:
    login = f'<a href="{APP}/login?lang={lang}">{c["login"]}</a>' if APP_ONLINE else ""
    links = "\n".join(f'        <a href="{h}">{e(t)}</a>' for h, t in items)
    mobile = "\n".join(f'    <a href="{h}">{e(t)} <span>0{i + 1}</span></a>' for i, (h, t) in enumerate(items))
    return f'''  <header class="nav">
    <div class="container nav__inner">
      <a translate="no" class="brand notranslate" href="{c["home"]}" aria-label="Logical Knight — home">
        <img src="/assets/img/mark-64.png" width="30" height="30" alt="">
        <span>Logical Knight</span>
      </a>
      <nav class="nav__links" aria-label="{'Hauptnavigation' if lang == 'de' else 'Primary'}">
{links}
        <a href="{other}" hreflang="{c["switch_lang"]}" lang="{c["switch_lang"]}">{c["switch"]}</a>
        {login}
      </nav>
      <a class="btn btn--primary btn--sm nav__cta" href="{pilot_href(lang)}">{c["pilot_btn"]}</a>
      <button class="nav__toggle" type="button" aria-expanded="false" aria-controls="mobile-menu" aria-label="Menu"><span></span></button>
    </div>
  </header>
  <div class="mobile-menu" id="mobile-menu">
{mobile}
    <a href="{other}" hreflang="{c["switch_lang"]}" lang="{c["switch_lang"]}">{c["switch"]}</a>
    {login}
    <a class="btn btn--primary" href="{pilot_href(lang)}">{c["pilot_btn"]}</a>
  </div>
'''


def footer(c: dict) -> str:
    legal = legal_links(c)
    return f'''  <footer class="footer footer--legal">
    <div class="container">
      <nav aria-label="Rechtliches / Legal"><ul class="legal-links">{legal}</ul></nav>
      <div class="footer__bottom">
        <span>© <span data-year>2026</span> {LK} · Leo King</span>
        <span>{c["fictional"]}</span>
      </div>
    </div>
  </footer>
  <script src="/assets/js/site.js" defer></script>
</body>
</html>
'''


def product(lang: str) -> str:
    c = T[lang]
    pilot = pilot_href(lang)
    ids = dict(zip(("problem", "flow", "example", "export", "features", "start", "data", "pilot", "faq"),
                   {"de": ("problem", "ablauf", "beispiel", "export", "funktionen", "einstieg", "daten", "pilot", "faq"),
                    "en": ("problem", "how", "example", "export", "features", "start", "data", "pilot", "faq")}[lang]))
    n = iter(range(1, 10))

    def sec(key: str, eyebrow: str, h: str, body: str) -> str:
        sid = ids[key]
        return f"""    <section class="section" id="{sid}" aria-labelledby="{sid}-title">
      <div class="container">
        <div class="section-head"><p class="eyebrow"><span class="idx">0{next(n)}</span><span class="rule"></span>{eyebrow}</p>
          <h2 class="h1" id="{sid}-title" data-reveal>{h}</h2></div>
        {body}
      </div>
    </section>
"""

    cards = lambda items, cls="features": f'<ul class="{cls}">' + "".join(  # noqa: E731
        f'<li data-reveal><h3>{e(h)}</h3><p>{e(p)}</p></li>' for h, p in items) + "</ul>"
    steps = lambda items: '<ol class="steps steps--flow">' + "".join(  # noqa: E731
        f'<li class="step" data-reveal><span class="step__n">0{i + 1}</span><h3>{e(h)}</h3><p>{e(p)}</p></li>'
        for i, (h, p) in enumerate(items)) + "</ol>"
    sample = f'<a class="btn btn--ghost" href="{SAMPLE[lang]}" download>{c["pack_dl"]}</a>'
    main = f"""  <main id="main">
    <section class="hero" aria-labelledby="hero-title">
      <div class="gridbg" aria-hidden="true"></div>
      <div class="container">
        <div class="hero__top">
          <p class="eyebrow"><span translate="no" class="idx notranslate">IPPC Ledger</span><span class="rule"></span>{c["eyebrow"]}</p>
          <h1 class="display hero__title hero__title--product" id="hero-title">{c["h1"]}</h1>
          <div class="hero__row">
            <p class="lede">{e(c["lede"])}</p>
            <div class="btn-row">
              <a class="btn btn--primary" href="{pilot}">{c["pilot_btn"]}</a>
              <a class="btn btn--ghost" href="#{ids["example"]}">{c["example_btn"]}</a>
            </div>
          </div>
          <p class="product-status">{e(c["status"])}</p>
        </div>
      </div>
    </section>
{sec("problem", c["problem_eyebrow"], c["problem_h"], cards(c["problem"], "features features--plain"))}
{sec("flow", c["flow_eyebrow"], c["flow_h"], steps(c["flow"]))}
{sec("example", c["ex_eyebrow"], c["ex_h"], f'<p class="lede">{e(c["ex_lede"])}</p><div class="shots">' + "".join(figure(*s, lang) for s in c["shots"]) + "</div>")}
{sec("export", c["pack_eyebrow"], c["pack_h"], f'<p class="lede">{e(c["pack_lede"])}</p><ul class="pack" data-reveal>' + "".join(f"<li><code>{e(f)}</code><span>{e(d)}</span></li>" for f, d in c["pack"]) + f'</ul><p class="note">{e(c["pack_note"])}</p><p class="btn-row">{sample}</p>')}
{sec("features", c["feat_eyebrow"], c["feat_h"], cards(c["features"]))}
{sec("start", c["gs_eyebrow"], c["gs_h"], '<ul class="bring">' + "".join(f"<li><strong>{e(h)}</strong> {e(p)}</li>" for h, p in c["gs_items"]) + f'</ul><p class="lede">{c["gs_text"].format(gs=c["gs"])}</p>')}
{sec("data", c["data_eyebrow"], c["data_h"], cards(c["data"]))}
{sec("pilot", c["pilot_eyebrow"], c["pilot_h"], f'<p class="lede">{e(c["pilot_scope"])}</p>' + steps(c["pilot_steps"]) + f'<p class="btn-row"><a class="btn btn--primary" href="{pilot}">{c["pilot_btn"]}</a></p>')}
{sec("faq", c["faq_eyebrow"], c["faq_h"], '<div class="faq">' + "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in c["faq"]) + "</div>")}
    <section class="section section--tight" aria-labelledby="final-title">
      <div class="container final" data-reveal>
        <h2 class="h1" id="final-title">{c["final_h"]}</h2><p class="lede">{c["final_text"]}</p>
        <p class="btn-row"><a class="btn btn--primary" href="{pilot}">{c["pilot_btn"]}</a> {sample}</p>
      </div>
    </section>
  </main>
"""
    main = main.replace('<span class="serif gold">IPPC Ledger</span>', f'<span class="serif gold">{IP}</span>')
    nav_items = [("#" + ids[k], t) for k, t in zip(("flow", "example", "pilot", "faq"), [t for _, t in c["nav"]])]
    return head(c, lang, c["title"], c["desc"], c["path"], c["other"]) + nav(c, lang, c["other"], nav_items) + main + footer(c)


GS = {
    "de": {"title": "Erste Schritte mit IPPC Ledger · Logical Knight", "h1": "Erste Schritte mit " + IP,
           "lede": "Erfassen, anhängen, korrigieren, exportieren: so kommen Ihre ersten Datensätze in die Anwendung.",
           "steps": [
               ("Anmelden", "Sie erhalten eine Einladung per E-Mail. Über den Link legen Sie Ihr Passwort fest und melden sich mit Ihrer E-Mail-Adresse an. Die Startseite zeigt eine Checkliste der ersten Schritte."),
               ("Lieferant anlegen", "Lieferanten → Lieferant anlegen. Danach auf der Seite des Lieferanten „Ermächtigung erfassen“: Nummer und Behörde aus der Ermächtigung, Gültigkeit nur, wenn das Dokument sie nennt, und das PDF oder Foto.", "app-supplier-authorisation.png"),
               ("Wareneingang erfassen", "Wareneingänge → Wareneingang erfassen: Eingangsdatum, Lieferant, Lieferscheinnummer, Behandlungsverfahren und -angaben, je Materialposition Holzart, Menge mit Einheit und/oder Masse in kg. Lieferschein und Behandlungsnachweis gleich mit hochladen."),
               ("Fehlendes sehen und beheben", "Fehlt etwas, zeigt die Lieferung den Grund. „Fehlende Nachweise“ listet alles Offene. Unter „Prüfen / abgleichen“ markieren Sie Dokumente als geprüft oder abgelehnt.", "app-delivery-incomplete.png"),
               ("Korrigieren", "„Bearbeiten“ auf dem Wareneingang. Ändern Sie einen erfassten Wert, geben Sie den Grund an; der Verlauf zeigt alten und neuen Wert, Person, Zeit und Grund.", "app-history-correction.png"),
               ("Auftrag verknüpfen", "Aufträge → Auftrag anlegen, dann Material über die Wareneingangs-Nr. suchen und mit der verwendeten Menge in der Einheit der Lieferung verknüpfen.", "app-job-trace.png"),
               ("Exportieren", "„Nachweise exportieren“ auf einem Auftrag oder Exporte → Zeitraum. Ohne Lieferungen im Zeitraum gibt es einen Hinweis statt eines leeren Archivs.", "app-exports.png"),
               ("Tabellen übernehmen", "Einstellungen → Import: Vorlage herunterladen, ausfüllen, hochladen, Spalten prüfen, Vorschau ansehen, bestätigen. Daten mit Schrägstrich (05/03/2026) werden als mehrdeutig abgelehnt; schreiben Sie 05.03.2026."),
           ],
           "help": "Fragen? <a href=\"mailto:logicalknight0@gmail.com\">logicalknight0@gmail.com</a> · <a href=\"/de/ippc-ledger/\">Zurück zu " + IP + "</a>"},
    "en": {"title": "Getting started with IPPC Ledger · Logical Knight", "h1": "Getting started with " + IP,
           "lede": "Enter, attach, correct, export: how your first records get into the application.",
           "steps": [
               ("Log in", "You receive an invitation by e-mail. Its link lets you set your password; then log in with your e-mail address. The start page shows a checklist of the first steps."),
               ("Add a supplier", "Suppliers → Add supplier. Below, “Add authorisation evidence”: number and authority from the authorisation, a validity only if the document states one, and the PDF or photo.", "app-supplier-authorisation.png"),
               ("Record a delivery", "Deliveries → Add delivery: receipt date, supplier, delivery-note number, treatment method and details, and per material line the wood type, a quantity with its unit and/or the mass in kg. Upload the delivery note and treatment evidence right away."),
               ("See and fix what is missing", "If something is missing, the delivery shows the reason. “Missing Evidence” lists everything open. Under “Review / verify” you mark documents as reviewed or rejected.", "app-delivery-incomplete.png"),
               ("Correct", "Edit on the delivery. When you change a recorded value, give the reason; the history shows the old and new value, person, time and reason.", "app-history-correction.png"),
               ("Link to a job", "Jobs → Add job, then find material by delivery reference and link it with the quantity used, in the delivery's unit.", "app-job-trace.png"),
               ("Export", "“Export evidence” on a job, or Exports → a period. A period without deliveries gives a message instead of an empty archive.", "app-exports.png"),
               ("Bring spreadsheets", "Settings → Import: download a template, fill it in, upload, check the columns, review the preview, confirm. Dates with slashes (05/03/2026) are refused as ambiguous; write 05.03.2026."),
           ],
           "help": "Questions? <a href=\"mailto:logicalknight0@gmail.com\">logicalknight0@gmail.com</a> · <a href=\"/en/ippc-ledger/\">Back to " + IP + "</a>"},
}


def getting_started(lang: str) -> str:
    c, g = T[lang], GS[lang]
    items = []
    for i, step in enumerate(g["steps"]):
        h, p = step[0], step[1]
        pic = figure(step[2], h, "Beispiel mit fiktiven Daten" if lang == "de" else "Example with fictional data", lang) if len(step) > 2 else ""
        items.append(f'<li class="gs__step"><h2 class="h3"><span class="step__n">0{i + 1}</span> {e(h)}</h2><p>{e(p)}</p>{pic}</li>')
    body = f'''  <main id="main" class="legal product" lang="{lang}">
    <div class="container legal__inner legal__inner--wide">
      <h1>{g["h1"]}</h1>
      <p class="lede">{e(g["lede"])}</p>
      <ol class="gs">{"".join(items)}</ol>
      <p>{g["help"]}</p>
    </div>
  </main>
'''
    return head(c, lang, g["title"], g["lede"], c["gs"], c["gs_other"]) + nav(c, lang, c["gs_other"], [(c["path"], "IPPC Ledger")]) + body + footer(c)


def redirect(target: str) -> str:
    return f'''<!DOCTYPE html>
<html lang="de">
<head><meta charset="utf-8"><title>IPPC Ledger · Logical Knight</title><meta name="robots" content="noindex">
<link rel="canonical" href="https://logicalknight.com{target}"><meta http-equiv="refresh" content="0; url={target}"></head>
<body><p><a href="{target}">{IP}</a> · <a href="/en/ippc-ledger/">English</a></p></body>
</html>
'''


# The German homepage is index.html with every visible text translated. Each pair must match exactly, so a change to
# the English page fails the build here instead of leaving English text on the German page.
HOME_DE = [
    ('<html lang="en">', '<html lang="de">'),
    ("<title>Logical Knight — Technology for problems worth solving</title>", "<title>Logical Knight — Technik für Probleme, die es wert sind</title>"),
    ('content="Logical Knight builds practical software for difficult real-world problems, starting from how the work is actually done."',
     'content="Logical Knight entwickelt praktische Software für schwierige Probleme aus der Praxis, ausgehend davon, wie die Arbeit tatsächlich gemacht wird."'),
    ('<link rel="canonical" href="https://logicalknight.com/">', '<link rel="canonical" href="https://logicalknight.com/de/">'),
    ('<meta property="og:title" content="Logical Knight — Technology for problems worth solving">', '<meta property="og:title" content="Logical Knight — Technik für Probleme, die es wert sind">'),
    ('<meta property="og:description" content="Practical software for difficult real-world problems.">', '<meta property="og:description" content="Praktische Software für schwierige Probleme aus der Praxis.">'),
    ('<meta property="og:url" content="https://logicalknight.com/">', '<meta property="og:url" content="https://logicalknight.com/de/">'),
    (">Skip to content<", ">Zum Inhalt<"),
    ('href="/" aria-label="Logical Knight — home"', 'href="/de/" aria-label="Logical Knight — Startseite"'),
    ('aria-label="Primary"', 'aria-label="Hauptnavigation"'),
    ('<a href="#approach">Approach</a>', '<a href="#approach">Vorgehen</a>'),
    ('href="/en/ippc-ledger/"', 'href="/de/ippc-ledger/"'),
    ('<a href="#company">Company</a>', '<a href="#company">Unternehmen</a>'),
    ('<a href="#contact">Contact</a>', '<a href="#contact">Kontakt</a>'),
    ('<a href="/de/" hreflang="de" lang="de">Deutsch</a>', '<a href="/" hreflang="en" lang="en">English</a>'),
    (">Email us<", ">E-Mail schreiben<"),
    ('aria-label="Open menu"', 'aria-label="Menü öffnen"'),
    ("Approach <span>01</span>", "Vorgehen <span>01</span>"),
    ("Company <span>02</span>", "Unternehmen <span>02</span>"),
    ("Contact <span>04</span>", "Kontakt <span>04</span>"),
    ('<span class="rule"></span>Applied technology company</p>', '<span class="rule"></span>Unternehmen für angewandte Technik</p>'),
    ('aria-label="Company status"', 'aria-label="Stand"'),
    ('<span class="k">Status</span>', '<span class="k">Stand</span>'),
    ("<em>Pilot phase</em>", "<em>Pilotphase</em>"),
    ("<span>More products</span><em>Private development</em>", "<span>Weitere Produkte</span><em>In Entwicklung, nicht öffentlich</em>"),
    ('Technology for problems <span class="serif">worth solving.</span>', 'Technik für Probleme, <span class="serif">die es wert sind.</span>'),
    ("builds focused <strong>software</strong> for difficult real-world problems — where existing workflows are manual, fragmented, expensive or inadequate.",
     "entwickelt gezielte <strong>Software</strong> für schwierige Probleme aus der Praxis, dort, wo Abläufe heute von Hand, verstreut, teuer oder unzureichend sind."),
    ('<span>Explore <span translate="no" class="notranslate">IPPC Ledger</span></span>', '<span><span translate="no" class="notranslate">IPPC Ledger</span> ansehen</span>'),
    ('href="#approach">Our approach</a>', 'href="#approach">Unser Vorgehen</a>'),
    ('<span class="rule"></span>Pilot phase</p>', '<span class="rule"></span>Pilotphase</p>'),
    ('Keep timber deliveries and ISPM 15 records <span class="serif gold">together.</span>', 'Wareneingänge und ISPM-15-Nachweise <span class="serif gold">an einem Ort.</span>'),
    ("""For wood-packaging businesses that buy treated timber. Connect deliveries with supplier
            evidence, see which documents are missing and export the records for a selected period.""",
     """Für Holzverpackungsbetriebe, die behandeltes Holz zukaufen: Verknüpfen Sie Lieferungen mit
            Lieferantennachweisen, behalten Sie fehlende Unterlagen im Blick und stellen Sie die Dokumentation für einen ausgewählten Zeitraum zusammen."""),
    ("""<h3>Suppliers and authorisations</h3><p>Each treatment provider's authorisation with its document and
            validity. An end date only when the document states one; an internal review reminder is kept separate.</p>""",
     """<h3>Lieferanten und Ermächtigungen</h3><p>Die Ermächtigung jedes Behandlungsbetriebs mit Dokument und
            Gültigkeit. Ein Ablaufdatum nur, wenn das Dokument eines nennt; eine interne Prüferinnerung bleibt davon getrennt.</p>"""),
    ("""<h3>Deliveries and material</h3><p>Receipt date, sender, wood type, piece count or mass with its unit,
            treatment method and details.</p>""",
     """<h3>Wareneingänge und Material</h3><p>Empfangsdatum, Absender, Holzart, Stückzahl oder Masse mit Einheit,
            Behandlungsverfahren und -angaben.</p>"""),
    ("""<h3>Evidence documents</h3><p>Delivery notes, invoices and treatment evidence as PDF or image, with
            versions. Present, reviewed by a person and verified are recorded separately.</p>""",
     """<h3>Nachweisdokumente</h3><p>Lieferscheine, Rechnungen und Behandlungsnachweise als PDF oder Bild, mit
            Versionen. Vorhanden, von einer Person geprüft und mit der Quelle abgeglichen werden getrennt erfasst.</p>"""),
    ("""<h3>Jobs and traceability</h3><p>Which material went into which job, in the unit it was delivered in;
            nothing is converted, and a line cannot be used twice over.</p>""",
     """<h3>Aufträge und Rückverfolgung</h3><p>Welches Material in welchem Auftrag steckt, in der Einheit der Lieferung;
            es wird nichts umgerechnet, und eine Position lässt sich nicht doppelt verbrauchen.</p>"""),
    ("""<h3>Missing evidence</h3><p>A deterministic check names every gap and its reason. It describes the
            records; it is not a legal assessment.</p>""",
     """<h3>Fehlende Nachweise</h3><p>Eine feste Regelprüfung nennt jede Lücke mit Grund. Sie beschreibt die
            Datensätze; sie ist keine rechtliche Bewertung.</p>"""),
    ("""<h3>Corrections and export</h3><p>Every correction of a recorded value keeps its reason in the history.
            Exports for a job or period: original files, CSV records and a PDF summary.</p>""",
     """<h3>Korrekturen und Export</h3><p>Jede Korrektur eines erfassten Werts behält ihren Grund im Verlauf.
            Exporte für einen Auftrag oder Zeitraum: Originaldateien, Datensätze als CSV und eine PDF-Übersicht.</p>"""),
    ("""Honest status: <span translate="no" class="notranslate">IPPC Ledger</span> is in a pilot phase and not generally available. It is not an
          authority, issues no certificates and verifies nothing automatically. A pilot covers one site and your own records,
          and you can export everything at any time.""",
     """Ehrlicher Stand: <span translate="no" class="notranslate">IPPC Ledger</span> ist in der Pilotphase und noch nicht allgemein verfügbar. Es ist keine
          Behörde, stellt keine Bescheinigungen aus und prüft nichts automatisch. Ein Pilot umfasst einen Standort und Ihre eigenen
          Datensätze, und Sie können jederzeit alles exportieren."""),
    ('subject=IPPC%20Ledger%20pilot">Request a pilot</a>', 'subject=Pilot%20IPPC%20Ledger">Pilot anfragen</a>'),
    ('href="/en/ippc-ledger/#example">See an example</a>', 'href="/de/ippc-ledger/#beispiel">Beispiel ansehen</a>'),
    ('<span class="rule"></span>Our approach</p>', '<span class="rule"></span>Unser Vorgehen</p>'),
    ('We start with <span class="serif gold">the problem.</span>', 'Wir beginnen mit <span class="serif gold">dem Problem.</span>'),
    ("Not with a technology looking for a use. Each product begins as a real workflow that is slow, costly or unreliable today.",
     "Nicht mit einer Technik, die einen Zweck sucht. Jedes Produkt beginnt bei einem echten Ablauf, der heute langsam, teuer oder unzuverlässig ist."),
    ("<h3>Find a real problem</h3><p>Where existing workflows are manual, fragmented, expensive or inadequate.</p>",
     "<h3>Ein echtes Problem finden</h3><p>Wo Abläufe heute von Hand, verstreut, teuer oder unzureichend sind.</p>"),
    ("<h3>Understand the workflow</h3><p>Learn how the work is actually done before deciding what to build.</p>",
     "<h3>Den Ablauf verstehen</h3><p>Erst lernen, wie die Arbeit tatsächlich gemacht wird, dann entscheiden, was gebaut wird.</p>"),
    ("<h3>Build the smallest useful system</h3><p>Solve the core problem properly, without unnecessary scope.</p>",
     "<h3>Das kleinste nützliche System bauen</h3><p>Das Kernproblem richtig lösen, ohne unnötigen Umfang.</p>"),
    ("<h3>Validate it</h3><p>Test with the people who have the problem, and learn from real use.</p>",
     "<h3>Erproben</h3><p>Mit den Menschen testen, die das Problem haben, und aus der echten Nutzung lernen.</p>"),
    ("<h3>Turn it into a reliable product</h3><p>Harden what works into something people and systems can depend on.</p>",
     "<h3>Ein verlässliches Produkt daraus machen</h3><p>Was funktioniert, so festigen, dass Menschen und Systeme sich darauf verlassen können.</p>"),
    ("builds practical technology for difficult real-world problems.</p>", "entwickelt praktische Technik für schwierige Probleme aus der Praxis.</p>"),
    ('<span translate="no" class="notranslate">IPPC Ledger</span>: timber deliveries and ISPM 15 records in one place (pilot phase)',
     '<span translate="no" class="notranslate">IPPC Ledger</span>: Wareneingänge und ISPM-15-Nachweise an einem Ort (Pilotphase)'),
    ("More products are currently in private development.", "Weitere Produkte sind derzeit nicht öffentlich in Entwicklung."),
    ("<p>Practical technology for difficult real-world problems.</p>", "<p>Praktische Technik für schwierige Probleme aus der Praxis.</p>"),
    ("<h2>Company</h2>", "<h2>Unternehmen</h2>"),
    ('<li><a href="/#approach">Approach</a></li>', '<li><a href="/de/#approach">Vorgehen</a></li>'),
    ('<li><a href="/#company">Company</a></li>', '<li><a href="/de/#company">Unternehmen</a></li>'),
    ('<li><a href="/en/ippc-ledger/getting-started/">Getting started</a></li>', '<li><a href="/de/ippc-ledger/erste-schritte/">Erste Schritte</a></li>'),
    ("<h2>Contact</h2>", "<h2>Kontakt</h2>"),
    ('<li><a href="/kontakt/">Kontakt / Contact</a></li>', '<li><a href="/kontakt/">Kontakt</a></li>'),
    (". All rights reserved.</span>", ". Alle Rechte vorbehalten.</span>"),
]


def german_home() -> str:
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    for old, new in HOME_DE:
        assert old in html, f"index.html changed; update HOME_DE for {old[:60]!r}"
        html = html.replace(old, new)
    return html


def write(rel: str, html: str) -> None:
    p = ROOT / rel / "index.html"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(html, encoding="utf-8", newline="\n")
    print("wrote", p.relative_to(ROOT))


if __name__ == "__main__":
    write("de/ippc-ledger", product("de"))
    write("en/ippc-ledger", product("en"))
    write("de/ippc-ledger/erste-schritte", getting_started("de"))
    write("en/ippc-ledger/getting-started", getting_started("en"))
    write("ippc-ledger", redirect("/de/ippc-ledger/"))
    write("de", german_home())
