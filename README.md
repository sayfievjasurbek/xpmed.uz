# XPMED (xpmed.uz)

Static site for XPMED, exclusive distributor of medical equipment, implants and
consumables in Uzbekistan and Central Asia. Russian is the default language and
English is a full translation; every page exists in both.

`docs/catalog-system.md` is the detailed reference for the catalog, the import
pipeline and the review workflow. Read it before changing anything under
`content/` or `scripts/`.

## Running it

```
npm install
python3 -m venv .venv-catalog
.venv-catalog/bin/pip install -r scripts/requirements-catalog.txt
```

```
node build.mjs
```

```
npm test
```

```
python3 -m http.server 4190 --bind 127.0.0.1 --directory dist
```

`npm test` builds first, because most JavaScript tests assert against the files
in `dist/`; without that they could pass against a stale build. `npm run
test:js` and `npm run test:python` run one suite without rebuilding.

The admin review UI is a separate process: `python3 scripts/review-server.py
--port 4180`, then open `http://127.0.0.1:4180/admin/review`. It binds to
loopback only and is never part of the build.

## File naming: `.mjs` is build-time, `.js` is the browser

This is the single most important convention in `src/`.

- **`.mjs`** files run in Node during `node build.mjs` and never reach the
  browser. They generate HTML: `render.mjs`, `system-page.mjs`,
  `list-catalog.mjs`, `catalog.mjs`, `homepage.mjs`, `info-pages.mjs`,
  `contact-panel.mjs`, `clinical-taxonomy.mjs`, `catalog-data.mjs`.
- **`.js`** files are copied verbatim into `dist/` and shipped to the browser:
  `client.js`, `catalog.js`, `system.js`, `home.js`, `discovery.js`,
  `pdf-viewer.js`, `catalog-engine.js`, `catalog-selection.js`.

A `.js` file may be imported by a `.mjs` file (the build and the browser then
share one implementation — `catalog-engine.js` is the main example). The
reverse is never allowed: a `.js` file that imports a `.mjs` file would ask the
browser for a file the build never copies, and 404 at runtime. The list of
files copied to `dist/` is in `build.mjs`.

Stylesheets follow the pages that need them: `styles.css` (shell, every page),
`homepage.css`, `catalog.css` (catalog listings and the PDF library),
`system.css` (product pages only), `discovery.css` (global search, every page).

## Layout

| Path | What it is |
|---|---|
| `build.mjs` | The whole generator. Validates every system, renders both languages, writes `dist/`. |
| `src/` | Page templates (`.mjs`), browser code (`.js`), stylesheets, `i18n/`. |
| `content/products/<brand>/<slug>.json` | The authoritative product data, one file per system. |
| `content/catalogs/`, `content/system.schema.json` | Catalog manifests and the record schema. |
| `content/academy/` | XPMED Academy photographs and club logos. Drop files in, run `scripts/prepare-academy-assets.py`; see its `README.md`. |
| `catalogs-source/` | The manufacturer PDFs imports are made from. See its `AGENTS.md`. |
| `scripts/` | The reusable import pipeline, OCR, verification and the review server. |
| `scripts/one-off/` | Completed per-catalog import scripts, kept as a record. |
| `scripts/profiles/` | SHA-256 matched extraction profiles for reviewed catalogs. |
| `reports/` | Import, verification and correction reports, including `source-corrections.md`. |
| `tests/` | `*.test.mjs` (Node) and `test_*.py` (unittest), both run by `npm test`. |
| `dist/` | Build output. Regenerated from scratch every build; not in version control. |

## Rules that must not break

1. Product data and catalog numbers are never changed unless explicitly asked.
   Values must match the source PDFs exactly. An uncertain code is `null` in
   the data, renders as `—`, and cannot be selected for a quote.
2. Two manufacturer PDFs are withheld on purpose (the Cynthia brochure and the
   Revision knee surgical guide). Their imported content stays published; only
   the files are hidden. See `src/public-product-content.mjs`.
3. Contacts: Tashkent, Yakkasaray district, Solar street 12; info@xpmed.com;
   +998 95 476 66 60, +998 77 371 66 60, +998 99 022 66 60.
4. Everything in Russian and English, desktop and mobile. Animations are
   subtle, run once on enter, and respect `prefers-reduced-motion`. No AI or
   stock imagery for real products.
5. Run the full build and test suite after every change.

## No backend

The site is static and has no form endpoint. Nothing may appear to send a
message. Every "request" action opens the shared contact panel
(`src/contact-panel.mjs`) with real phone numbers and an email address. The
retired quote form is kept, unrendered, in `src/system-page.mjs` as
`retiredRequestForm`, with its inert submit handler at the end of
`src/system.js`, so a real endpoint can be added later.
