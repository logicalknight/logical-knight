"""The bow-making records module of the IPPC Ledger application: a module page under IPPC Ledger, not a product card.

Rules (docs/company-site.md): describe only behaviour that exists; no price; pilot status only, never general
availability; the module never certifies lawful origin or authenticates a bow. Published on 28 October 2026 by the
owner's decision, linked from the IPPC Ledger page.
"""

BOW = {
    "en": {
        "title": "Bow-making records (pilot) · IPPC Ledger · Logical Knight",
        "desc": "A module for bow makers: wood origin, stock, every processing step with waste, documents and a selected handover per bow. Pilot phase with selected workshops. No price yet.",
        "eyebrow": "IPPC Ledger · module in pilot phase",
        "status": "Pilot phase",
        "h1": "Records from the wood to each bow.",
        "lede": "For bow makers who must show where the wood in a bow came from. You record the origin of your wood, your stock and each processing step. For each bow you hand over only the evidence you choose.",
        "problem_h": "The problem",
        "problem": [
            ("The proof must fit the wood actually used.", "For pernambuco, proof must relate to the wood in the bow, from raw wood to the finished bow. An invoice alone is often not enough."),
            ("Books grow over years.", "Boards become blanks, blanks become sticks and bows, and some pieces break. Paper books and spreadsheets lose this chain."),
            ("Old stock has gaps.", "Historical stock or bought blanks often have no complete history. That must stay visible, not be filled in."),
        ],
        "how_h": "What the module does today",
        "how": [
            ("Wood origins", "Species, origin, harvest period, acquisition and documents. Unknown facts stay marked as unknown."),
            ("Stock", "Each piece with your own code, an optional stamp or identification mark and photos. Pieces, weight and volume are separate values; nothing is converted."),
            ("Processing steps", "Split a board into individually identified blanks, shape, make a bow, record breakage and waste. Each piece can be used only once. A wrong step is reversed with a reason, not deleted."),
            ("Corrections", "Changes need a reason and are kept with old and new values. Stated history such as “historical stock” is never changed silently."),
            ("Your existing books", "Import a CSV or Excel inventory. You see a preview first; every row is checked; nothing is saved until you confirm."),
            ("Inventory report", "Counts, weight and volume as recorded, per kind and status. It is an internal report, not an official or regulatory format."),
            ("Handover", "Per bow: a package with the documents you select, a readable summary and checksums. Private notes and the rest of your stock stay out."),
        ],
        "limits_h": "What it does not do",
        "limits": [
            "It does not certify lawful origin and it does not authenticate a bow.",
            "It does not fill in missing history or guess conversions between pieces, weight and volume.",
            "It does not replace the authorities, a lawyer or an expert opinion.",
        ],
        "status_h": "Status and access",
        "status_text": [
            "The module runs in IPPC Ledger. It is open only to pilot workshops that we set up together with them; it is not generally available.",
            "We are looking for a small number of bow-making workshops that want to try it with their own records, together with us.",
            "Access is set up per workshop by us; there is no self sign-up. It runs in the same application as IPPC Ledger, with its own access.",
            "There is no price yet. We will tell you the terms before you commit to anything.",
        ],
        "cta_h": "Interested in trying it?",
        "cta": "Write to {mail} and tell us how you keep your records today. We reply by e-mail.",
        "subject": "Bow-making records",
        "back": "IPPC Ledger",
        "ippc_link": "For bow makers: a module for wood origin, stock and bow records is in a pilot phase.",
    },
    "de": {
        "title": "Aufzeichnungen für den Bogenbau (Pilot) · IPPC Ledger · Logical Knight",
        "desc": "Ein Modul für Bogenbauer: Herkunft des Holzes, Bestand, jeder Arbeitsschritt mit Verschnitt, Dokumente und eine ausgewählte Übergabe pro Bogen. Pilotphase mit ausgewählten Werkstätten. Noch kein Preis.",
        "eyebrow": "IPPC Ledger · Modul in der Pilotphase",
        "status": "Pilotphase",
        "h1": "Aufzeichnungen vom Holz bis zu jedem Bogen.",
        "lede": "Für Bogenbauer, die zeigen müssen, woher das Holz in einem Bogen stammt. Sie erfassen die Herkunft Ihres Holzes, Ihren Bestand und jeden Arbeitsschritt. Pro Bogen geben Sie nur die Nachweise weiter, die Sie auswählen.",
        "problem_h": "Das Problem",
        "problem": [
            ("Der Nachweis muss zum verwendeten Holz passen.", "Bei Fernambuk muss sich der Nachweis auf das Holz im Bogen beziehen, vom Rohholz bis zum fertigen Bogen. Eine Rechnung allein reicht oft nicht."),
            ("Bücher wachsen über Jahre.", "Aus Brettern werden Rohlinge, aus Rohlingen Stangen und Bögen, und manche Teile brechen. In Papierbüchern und Tabellen geht diese Kette verloren."),
            ("Alter Bestand hat Lücken.", "Altbestand oder gekaufte Rohlinge haben oft keine vollständige Geschichte. Das muss sichtbar bleiben und darf nicht ergänzt werden."),
        ],
        "how_h": "Was das Modul heute kann",
        "how": [
            ("Herkunft des Holzes", "Holzart, Herkunft, Einschlagzeitraum, Erwerb und Dokumente. Unbekanntes bleibt als unbekannt markiert."),
            ("Bestand", "Jedes Teil mit Ihrer eigenen Kennung, einem optionalen Stempel oder Kennzeichen und Fotos. Stückzahl, Gewicht und Volumen sind getrennte Werte; nichts wird umgerechnet."),
            ("Arbeitsschritte", "Ein Brett in einzeln gekennzeichnete Rohlinge teilen, formen, einen Bogen bauen, Bruch und Verschnitt erfassen. Jedes Teil kann nur einmal verwendet werden. Ein falscher Schritt wird mit Grund rückgängig gemacht, nicht gelöscht."),
            ("Korrekturen", "Änderungen brauchen einen Grund und bleiben mit altem und neuem Wert erhalten. Angaben wie „Altbestand“ werden nie stillschweigend geändert."),
            ("Ihre bisherigen Bücher", "Einen Bestand aus CSV oder Excel übernehmen. Sie sehen zuerst eine Vorschau; jede Zeile wird geprüft; gespeichert wird erst nach Ihrer Bestätigung."),
            ("Bestandsbericht", "Stückzahl, Gewicht und Volumen wie erfasst, nach Art und Status. Es ist ein interner Bericht, kein amtliches Format."),
            ("Übergabe", "Pro Bogen: ein Paket mit den Dokumenten, die Sie auswählen, einer lesbaren Zusammenfassung und Prüfsummen. Private Notizen und Ihr übriger Bestand bleiben draußen."),
        ],
        "limits_h": "Was es nicht tut",
        "limits": [
            "Es bestätigt weder die rechtmäßige Herkunft noch die Echtheit eines Bogens.",
            "Es ergänzt keine fehlende Geschichte und rechnet nicht zwischen Stückzahl, Gewicht und Volumen um.",
            "Es ersetzt weder Behörden noch Rechtsberatung oder ein Gutachten.",
        ],
        "status_h": "Stand und Zugang",
        "status_text": [
            "Das Modul läuft in IPPC Ledger. Es ist nur für Pilot-Werkstätten geöffnet, die wir gemeinsam mit ihnen einrichten; allgemein verfügbar ist es nicht.",
            "Wir suchen einige Bogenbau-Werkstätten, die es gemeinsam mit uns an ihren eigenen Aufzeichnungen ausprobieren möchten.",
            "Den Zugang richten wir für jede Werkstatt ein; eine eigene Anmeldung gibt es nicht. Das Modul läuft in derselben Anwendung wie IPPC Ledger, mit eigenem Zugang.",
            "Einen Preis gibt es noch nicht. Die Bedingungen nennen wir Ihnen, bevor Sie sich auf etwas festlegen.",
        ],
        "cta_h": "Möchten Sie es ausprobieren?",
        "cta": "Schreiben Sie an {mail} und erzählen Sie uns, wie Sie Ihre Aufzeichnungen heute führen. Wir antworten per E-Mail.",
        "subject": "Aufzeichnungen Bogenbau",
        "back": "IPPC Ledger",
        "ippc_link": "Für Bogenbauer: Ein Modul für Holzherkunft, Bestand und Bogen-Aufzeichnungen ist in der Pilotphase.",
    },
}
