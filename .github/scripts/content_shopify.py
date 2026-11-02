"""Data Workbench and Shopify: the shop files Data Workbench writes today, and the Shopify app (in development).

Rules (docs/company-site.md): describe only behaviour that exists; no price; the app is in development and not on
the Shopify App Store, so the page never says otherwise. The app page is also the app's help, support and data page.
"""

SHOP_FILES = {
    "en": {
        "h": "Files for your shop.",
        "lede": "From an approved result, Data Workbench can write a product file for Shopify's own product import.",
        "items": [
            "New products or updates of existing products, chosen explicitly. Products can be kept as drafts.",
            "Product codes keep their leading zeros. Prices are written in the store currency you set; amounts are never converted.",
            "An update replaces each product's variants in Shopify. Data Workbench lists the variants an update would remove, compared with earlier approved files, and asks you to confirm the complete variant set first.",
            "A file for the Matrixify app is available as an option.",
        ],
        "app_link": "The Logical Knight Workbench app for Shopify is in development.",
    },
    "de": {
        "h": "Dateien für Ihren Shop.",
        "lede": "Aus einem freigegebenen Ergebnis schreibt Data Workbench eine Produktdatei für den Produktimport von Shopify.",
        "items": [
            "Neue Produkte oder Aktualisierungen bestehender Produkte, ausdrücklich gewählt. Produkte können als Entwurf bleiben.",
            "Artikelnummern behalten ihre führenden Nullen. Preise stehen in der von Ihnen festgelegten Shop-Währung; Beträge werden nie umgerechnet.",
            "Eine Aktualisierung ersetzt in Shopify die Varianten jedes Produkts. Data Workbench zeigt die Varianten, die eine Aktualisierung entfernen würde, im Vergleich mit früher freigegebenen Dateien, und lässt Sie zuerst den vollständigen Variantensatz bestätigen.",
            "Eine Datei für die App Matrixify gibt es als Option.",
        ],
        "app_link": "Die App Logical Knight Workbench für Shopify ist in Entwicklung.",
    },
}

APP = {
    "en": {
        "title": "Logical Knight Workbench for Shopify (in development) · Data Workbench · Logical Knight",
        "desc": "A Shopify app in development: approved Data Workbench results become product changes that you see against your live catalogue and approve before anything is written. Not yet on the Shopify App Store.",
        "status": "In development",
        "h1": "See every catalogue change before it reaches your shop.",
        "lede": "Logical Knight Workbench is a Shopify app in development. It takes a result you approved in Data Workbench, compares it with your live catalogue and writes only the changes you approve.",
        "how_h": "How it works",
        "how": [
            ("Approved data only", "Supplier files are checked, mapped and reviewed in Data Workbench. Only an approved result can become a change for your shop."),
            ("A preview against your shop", "New products, changed fields and prices with old and new values, added variants and images, and variants that stay in your shop."),
            ("Your approval", "Nothing is written until you approve the exact preview. A variant is deleted only if you tick it."),
            ("Changes in between", "If your catalogue changed after the preview, the change is refused and you preview again."),
            ("A record of every step", "Each change is recorded with the previous values. Field changes can be reverted from them."),
        ],
        "never_h": "What the app never does",
        "never": [
            "Publish products or change their status. New products are created as drafts.",
            "Delete products or images.",
            "Delete variants you did not tick.",
            "Read customers or orders. It asks only for access to products.",
            "Write on a schedule unless you authorise the schedule and the exact actions it may apply.",
        ],
        "data_h": "Data and privacy",
        "data": [
            "Stored: your shop's address, encrypted access keys, copies of the products in a preview, previews, the changes made with their previous values, and a log of who linked and approved (the Shopify staff user number).",
            "Not stored: customer or order data. Shopify's customer privacy requests are acknowledged; there is nothing to return or delete.",
            "Uninstalling deletes the access keys at once. When Shopify asks for the shop's data to be erased, 48 hours after uninstalling, every record of the shop is deleted.",
            "Linking a shop to a Data Workbench organisation needs a single-use code from an owner of that organisation. E-mail addresses are never used to link accounts.",
        ],
        "status_h": "Status",
        "status_text": [
            "The app is in development and tested on Logical Knight's own development store with fictional products. It is not on the Shopify App Store and cannot be installed by merchants yet.",
            "There is no price yet. We will state the terms before the app is offered.",
        ],
        "cta_h": "Questions or support",
        "cta": "Questions to {hello}; if you already use Data Workbench, {support}.",
        "back": "Data Workbench",
    },
    "de": {
        "title": "Logical Knight Workbench für Shopify (in Entwicklung) · Data Workbench · Logical Knight",
        "desc": "Eine Shopify-App in Entwicklung: Freigegebene Ergebnisse aus Data Workbench werden zu Produktänderungen, die Sie gegen Ihren aktuellen Katalog sehen und freigeben, bevor etwas geschrieben wird. Noch nicht im Shopify App Store.",
        "status": "In Entwicklung",
        "h1": "Jede Katalogänderung sehen, bevor sie Ihren Shop erreicht.",
        "lede": "Logical Knight Workbench ist eine Shopify-App in Entwicklung. Sie nimmt ein Ergebnis, das Sie in Data Workbench freigegeben haben, vergleicht es mit Ihrem aktuellen Katalog und schreibt nur die Änderungen, die Sie freigeben.",
        "how_h": "So funktioniert es",
        "how": [
            ("Nur freigegebene Daten", "Lieferantendateien werden in Data Workbench geprüft, zugeordnet und durchgesehen. Nur ein freigegebenes Ergebnis kann zu einer Änderung für Ihren Shop werden."),
            ("Eine Vorschau gegen Ihren Shop", "Neue Produkte, geänderte Felder und Preise mit altem und neuem Wert, hinzugefügte Varianten und Bilder sowie Varianten, die in Ihrem Shop bleiben."),
            ("Ihre Freigabe", "Geschrieben wird erst, wenn Sie genau diese Vorschau freigeben. Eine Variante wird nur gelöscht, wenn Sie sie ankreuzen."),
            ("Änderungen dazwischen", "Hat sich Ihr Katalog nach der Vorschau geändert, wird die Änderung abgelehnt und Sie erstellen eine neue Vorschau."),
            ("Jeder Schritt festgehalten", "Jede Änderung wird mit den vorherigen Werten gespeichert. Feldänderungen lassen sich damit zurücknehmen."),
        ],
        "never_h": "Was die App nie tut",
        "never": [
            "Produkte veröffentlichen oder ihren Status ändern. Neue Produkte werden als Entwurf angelegt.",
            "Produkte oder Bilder löschen.",
            "Varianten löschen, die Sie nicht angekreuzt haben.",
            "Kunden oder Bestellungen lesen. Sie fragt nur Zugriff auf Produkte an.",
            "Nach Zeitplan schreiben, außer Sie geben den Zeitplan und die erlaubten Aktionen ausdrücklich frei.",
        ],
        "data_h": "Daten und Datenschutz",
        "data": [
            "Gespeichert werden: die Adresse Ihres Shops, verschlüsselte Zugriffsschlüssel, Kopien der Produkte einer Vorschau, Vorschauen, die vorgenommenen Änderungen mit den vorherigen Werten und ein Protokoll, wer verknüpft und freigegeben hat (die Benutzernummer des Shopify-Mitarbeiters).",
            "Nicht gespeichert werden: Kunden- oder Bestelldaten. Die Datenschutzanfragen von Shopify zu Kunden werden bestätigt; es gibt nichts herauszugeben oder zu löschen.",
            "Beim Deinstallieren werden die Zugriffsschlüssel sofort gelöscht. Wenn Shopify 48 Stunden nach der Deinstallation die Löschung der Shopdaten anfordert, wird jeder Datensatz des Shops gelöscht.",
            "Für die Verknüpfung eines Shops mit einem Data-Workbench-Bereich braucht es einen Einmalcode von einem Inhaber dieses Bereichs. E-Mail-Adressen werden nie zur Verknüpfung verwendet.",
        ],
        "status_h": "Stand",
        "status_text": [
            "Die App ist in Entwicklung und wird im eigenen Entwicklungsshop von Logical Knight mit erfundenen Produkten getestet. Sie ist nicht im Shopify App Store und kann von Händlern noch nicht installiert werden.",
            "Einen Preis gibt es noch nicht. Die Bedingungen nennen wir, bevor die App angeboten wird.",
        ],
        "cta_h": "Fragen und Support",
        "cta": "Fragen an {hello}; wenn Sie Data Workbench schon nutzen, an {support}.",
        "back": "Data Workbench",
    },
}
