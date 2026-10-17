# logicalknight.com: company site rules

Internal. Kept under `.github/` so GitHub Pages does not publish it.

## Positioning

Logical Knight is the **company**: a small, focused software company that builds practical software for small and
growing businesses. It works as a compact team that keeps decisions close to the work and moves quickly from a useful
idea to a working version. It looks for real business problems and builds focused tools around them. Products sit under the
company story, never in place of it.

- Name: **Logical Knight**, singular, always. Protected from page translation (`translate="no"`).
- Core line: **Hard problems. Simple software.** / **Schwierige Probleme. Einfache Software.**
- Current products: **IPPC Ledger** (status: Pilot phase / Pilotphase) and **Data Workbench** (status: Free Early
  Access / Kostenloser Vorabzugang). Show nothing else as a product.
- No invented size, team, offices, clients, partners, numbers, testimonials, awards or founding year. The founding
  year is not recorded anywhere; add it only after the owner confirms it.
- No founder-centred marketing: never "founder-led", "run by its founder", "inhabergeführt" or "gründergeführt",
  and nothing that reads as a one-person business ("we review every request personally"). Say "small, focused
  software company", "compact team", "Kleines Team. Kurze Wege." `test_site.py` checks this. The provider's name in
  the Impressum and Datenschutz is legal information, not marketing, and stays.

## Voice

Short sentences, normal words, concrete examples. Warm and direct; understandable at B1/B2. No hype words (leverage,
empower, transformative, cutting-edge, ecosystem, seamless, innovative, unlock, world-class...); `test_site.py` checks
for them. German is written, not translated: natural, simple, "Sie", few English words ("Vorabzugang", not
"Early Access"; the Data Workbench page explains that the app itself is English and
calls the programme "Free Early Access").

## Information architecture

| Page | English | German |
|---|---|---|
| Home | `/` | `/de/` |
| Company (with "How we build" at `#how-we-build` / `#so-arbeiten-wir`) | `/en/company/` | `/de/unternehmen/` |
| Products | `/en/products/` | `/de/produkte/` |
| Data Workbench | `/en/data-workbench/` | `/de/data-workbench/` |
| IPPC Ledger | `/en/ippc-ledger/` | `/de/ippc-ledger/` |
| IPPC Ledger guide | `/en/ippc-ledger/getting-started/` | `/de/ippc-ledger/erste-schritte/` |
| Contact | `/en/contact/` | `/de/kontakt/` |
| Impressum, Datenschutz | `/impressum/`, `/datenschutz/` (German with an English section) | |

Redirects: `/en/` → `/`, `/ippc-ledger/` → `/de/ippc-ledger/`, `/kontakt/` → `/de/kontakt/`, `/contact/` →
`/en/contact/`. Company pages stay on logicalknight.com. Applications run on their own subdomains
(`app.` IPPC Ledger, `workbench.` Data Workbench); this site explains them and links to them, it never copies them.

Navigation: Company · Products · How we build · Contact, EN/DE switch, one primary button (default "See our
products"; product pages use their own action). Nothing internal (marketing, staff tools) in public navigation.
Footer: brand and hello@, Company / Products / Legal, language.

## Languages

Every page exists in both languages with the same content (`ROUTES` in `build_site.py`). The switch leads to the
same page in the other language; `hreflang` pairs and the sitemap list both. Legal pages are one bilingual page each.

## Products

A product page explains the problem, how the product works, what stays under human control, the honest status and
limits, and what it does **not** do. Only describe behaviour that exists. Screenshots must be real screens of the
product (invented demo data is fine and is labelled); never mock a screenshot. The Data Workbench review table is an
illustration and says so.

Adding a product: add its page builder and content, its `ROUTES` entry (both languages), an entry in `PRODUCTS`
(name, status only if verified, one-line problem, one-line solution, a real screenshot or none), and its footer link.
The homepage, products page and footer then list it; the layout needs no change. Do not show placeholder or "coming
soon" product cards; "More to come" stays a sentence.

## Crest

Only the approved crest, `assets/img/logical-knight-logo.png` (138 x 134, SHA-256
`eecf11b45128edef585e8aeeae73c20e3b85112d66a6991f0aafa7e03c839fde`, the same file as Data Workbench). Never edit,
resize, recolour, trace or regenerate it; tests pin the hash and refuse any other PNG logo. All presentation is CSS:

- **Lockup** in header and footer: crest in a 40 px box + "Logical Knight".
- **Persistent seal** (`seal()` in `build_site.py`): part of Logical Knight's identity. Exactly one per real page
  (all content pages, legal pages, 404; not redirect stubs), inserted by the shared page builders, so every future
  page gets it too. A fixed layer centred in the viewport (`position: fixed; left: 50%; top: 50%; translate(-50%,
  -50%)`); it does not scroll with the content. Behind the content (`z-index: 0`; `main` and the footer at 1, the
  header and its mobile menu at 50), `pointer-events: none`, `aria-hidden="true"`, never focusable, hidden in print.
  Full-width bands use translucent tints so it shows through; cards, forms and screenshots stay opaque.
- Structure (inline SVG, 400 x 400 view box): faint partial outer arcs, a dotted ring, four small diamond cardinal
  marks and outer ticks; the main inscription between two fine circles; a Latin micro-inscription; fine inner radial
  ticks; a near-white central disc; faint compass guide lines; the exact crest (`<img>`) in the centre.
- Inscriptions (SVG `textPath`, Georgia/Times serif, regular weight, spaced capitals, low opacity):
  English "WE BUILD WITH CARE • SIMPLE SOFTWARE • REAL PROBLEMS • CLEAR SYSTEMS •",
  German "MIT SORGFALT GEBAUT • EINFACHE SOFTWARE • ECHTE PROBLEME • KLARE SYSTEME •",
  micro ring "CURA • CLARITAS • OPUS • FIDES •" (care, clarity, work, trust). Only real words.
- Motion: **the crest never moves**. The inscription ring turns clockwise once every 44 s; the outer geometry turns
  the other way once every 64 s. CSS only, linear, no scroll or pointer effects. Under `prefers-reduced-motion:
  reduce` all rotation stops and the whole seal stays visible.
- Size: 400 px on desktop, 330 px below 1100 px, 250 px below 600 px. Crest at 34 % of the seal (136 px on desktop,
  below its own 138 px). Opacity is set per layer: crest 0.32 (0.28 on phones), inscription 0.4, micro inscription
  0.24, fine geometry 0.1 to 0.34. Never one opacity on the whole seal.
- The homepage hero has no separate crest; it opens with "LOGICAL KNIGHT" and the core line. There is no separate
  watermark any more.
- Favicon, touch icon and social preview image use the same file.

## Visual system

`assets/css/tokens.css` is copied unchanged from Data Workbench; `site.css` only lays pages out. White and
near-white canvas, ink type, cyan for atmosphere and links, violet only for the primary action. System fonts, no
downloads. Lists and hairline-ruled grids instead of card grids. No dark theme, gradients-as-decoration, robots,
stock photos or AI-looking illustration.

## Contact

There is no form backend (GitHub Pages is static). The contact page prepares an e-mail in the visitor's own mail app
(name, company, problem, today's workaround; no e-mail field needed) and sends nothing itself; without JavaScript it
shows the address. General: hello@logicalknight.com. Support for existing users: support@logicalknight.com. A real
form would need a server-side endpoint, spam protection and a privacy-policy update first.

## Build and checks

```
python .github/scripts/build_site.py     # writes every page from the source
python .github/scripts/test_site.py      # routes, parity, links, crest, seal, metadata, copy rules
python .github/scripts/check_site.py     # translation protection, retired names, owner markers (--live: app links)
python .github/scripts/preview.py        # local preview at http://127.0.0.1:8766/
```

CI rebuilds and fails if the committed pages differ from the source. Legal texts live verbatim in
`.github/site/legal/`; change them there only with owner-approved wording.
