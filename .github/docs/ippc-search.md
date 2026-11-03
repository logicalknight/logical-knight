# Logical Knight product search setup

Internal. This file stays under `.github/` and is not part of the public site.

## Pages and purpose

Improve the existing pages instead of creating duplicate landing pages for variations of a keyword.

| Audience | German | English |
| --- | --- | --- |
| Businesses that make or repair wood packaging and buy treated timber | `/de/ippc-ledger/` | `/en/ippc-ledger/` |
| Bow-making workshops | `/de/ippc-ledger/bogenbau/` | `/en/ippc-ledger/bow-making/` |
| Teams checking and cleaning CSV and Excel files | `/de/data-workbench/` | `/en/data-workbench/` |
| Shopify product-data workflows and app information | `/de/data-workbench/shopify/` | `/en/data-workbench/shopify/` |

The packaging page describes ISPM 15 records and links directly to its real application examples. The bow-making
page describes wood-origin and stock records, answers practical workshop questions and offers a pilot by email.
The Data Workbench page explains CSV and Excel quality checks, review and approval before export, and the available
shop-file workflow. The Shopify page separates those file exports from the app that is still in development.
Both Data Workbench page pairs have practical questions and answers and a relevant next step. The main page links
to the existing, labelled illustration of reviewing changes. No new video or customer result is claimed.

Titles, descriptions and headings describe each audience's task. The existing canonical URLs, language alternates,
robots.txt and sitemap are retained. Do not add prices, review ratings, certification claims or automatic PDF
reading. Search themes such as ISPM-15 documentation, treatment evidence, wood inventory for bow making, CSV and
Excel data quality, leading zeros in product codes and reviewing Shopify product changes are hypotheses until
actual search data is available; no search volume or ranking has been established.

The Data Workbench application is in English. Its website pages are in German and English. Keep this distinction
clear. Free Early Access is currently free, not a permanent free plan. Do not describe the Shopify app as available
to install or link to an invented App Store listing. The eight existing product-page URLs above cover both products;
there is no separate Search Console property to create for Data Workbench.

## Connect Google Search Console

This requires the owner's Google account and access to the domain's DNS. Website code alone cannot verify ownership.

1. Open <https://search.google.com/search-console/> with the account that should own the property.
2. Check whether the domain property `logicalknight.com` already exists. Reuse it if it does.
3. Otherwise add a **Domain** property for `logicalknight.com`, without `https://` or a path.
4. Copy the exact TXT verification value supplied by Google. In Cloudflare DNS, add that TXT record at the domain
   root (`@`) with automatic TTL. Do not replace existing TXT records. The verification value must come from Google;
   there is no placeholder value to deploy from this repository.
5. Return to Search Console and verify. Leave the verification record in place.
6. In Sitemaps, submit `https://logicalknight.com/sitemap.xml` once. Fix reported fetch or parse errors before retrying.
7. Inspect the eight product URLs above with URL Inspection. Use the live test to check accessibility. After this
   change is published, request indexing for the changed canonical pages if needed. A request is not a guarantee
   that a page will be indexed or ranked.

No Search Console verification or sitemap submission has been performed by this change. Do not report them as done
until the account confirms them. Domain verification does not require adding a visitor-tracking script.

## Measure results

Use Search Console's Performance report to review queries, pages, countries, impressions and clicks. Start with
Germany and the German product pages, then inspect the English pages separately. Separate IPPC Ledger and Data
Workbench by page URL when assessing enquiries and search performance. Early data may be sparse; some
queries are withheld for privacy. Do not treat missing query rows as proof that nobody searches for the topic.

Review after enough data has accumulated, usually several weeks. Compare periods and focus on relevant enquiries,
not only the number of visits. Record actual pilot requests separately from button clicks. Search performance can
change and no ranking or lead volume is promised.

The existing consent-controlled analytics can record these button events without extra event properties:

- `ippc_pilot_click`: existing packaging pilot link.
- `ippc_example_click`: link to the packaging page's real product examples.
- `ippc_bow_pilot_click`: bow-making pilot email link.
- `dw_early_access_click`: existing Data Workbench access-request link.
- `dw_example_click`: Data Workbench link to the change-review illustration.
- `dw_shopify_question_click`: email link for questions about the Shopify app.

These events measure clicks, not form submissions or emails sent. They are subject to the visitor's analytics
choice; Search Console and analytics totals will not match exactly. No analytics configuration was changed here.

## Official references

- <https://developers.google.com/search/docs/fundamentals/seo-starter-guide>
- <https://developers.google.com/search/docs/monitor-debug/search-console-start>
- <https://support.google.com/webmasters/answer/9008080>

Run the normal build and both checks before publishing:

```sh
python .github/scripts/build_site.py
python .github/scripts/test_site.py
python .github/scripts/check_site.py
```
