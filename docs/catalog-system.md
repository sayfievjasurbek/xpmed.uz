# XPMED automatic system catalog

## Source of truth and hierarchy

`content/products/<brand>/<system-slug>.json` is authoritative. Brand → category → subcategory → system → components → sizes/variants. Names, descriptions, feature titles/text, table titles and legends use `{ "ru": "…", "en": "…" }`. Dimensions and reference codes are never translated. `variants` is an optional array with its own gallery, features, hotspots and specTables. Components may contain sizes/variants and reference codes; they never generate independent pages.

`node build.mjs` validates all system files, selects only `status: "published"`, generates RU/EN pages at `/catalog/<brand>/<system>/` and `/en/catalog/<brand>/<system>/`, and generates `dist/catalog-index.json`. Listings/search use that compact index shape, including reference codes and component names, without serializing full spec tables. It has no admin routes. Draft scans, PDFs, extraction reports, draft assets and JSON are excluded. Generated output is recreated to remove previously published pages after unpublishing.

The 16 existing listings migrated into 13 families, retaining every component: Synicem cements and CrossFT anchors are grouped; all other legacy entries remain their own families. `content/legacy-products.snapshot.json` is an archival migration input, not a runtime data source. Existing IDs and filter labels remain supported by a small compatibility adapter.

## Generic tables

`specTables: [{ id, title: {ru,en}, unit: "mm" | null, image: "/catalogs/...", columns: [cell,…], rows: [[cell,…],…], legend: {ru,en} | null, sourcePages: [1,…] }]`.

Any number of columns/rows is supported. Cells can be strings, numbers, null, bilingual labels or lists. Every row must have the same width as `columns`. Empty printed/merged cells are `""`; an unreadable value is `null` and must have a review flag. Keep `●`, `○`, ranges and decimal strings exactly. Do not infer units or the meaning of symbols.

## Import

Install Python dependencies into a virtual environment:

```
python3 -m venv .venv-catalog
.venv-catalog/bin/pip install -r scripts/requirements-catalog.txt
.venv-catalog/bin/python scripts/import-catalog.py catalogs-source/double-medical/cynthia-knee-system.pdf
```

`.venv-catalog/` is the project environment and the only supported one. It is gitignored, so every machine creates its own. Never put it in `/tmp`: periodic cleanup there deletes `pyvenv.cfg`, after which the environment still looks present but silently stops resolving its own packages.

rembg caches its segmentation weights in `U2NET_HOME`. Keep that inside the project too, so the cache survives and the ~170 MB model downloads only once:

```
U2NET_HOME="$PWD/.rembg-models" OMP_NUM_THREADS=1 .venv-catalog/bin/python scripts/import-catalog.py catalogs-source/double-medical/cynthia-knee-system.pdf
```

The script accepts exactly one PDF; it never scans/imports other PDFs. Input must be in `catalogs-source/<brand>/`. PyMuPDF extracts text, native raster objects/soft masks and reference page scans; pdfplumber extracts ruled tables. Every import produces draft JSON and both JSON/Markdown reports in `reports/<brand>/`. Original PDF, page scans, raw text and extracted table/crop references stay under `public/catalogs/<brand>/<pdf-name>/` for local inspection. WebPs, transparent PNGs, rembg candidates and an extraction manifest are under `public/images/products/<brand>/<system>/`. Native pixels are never upscaled.

Original alpha masks are preferred over AI segmentation where supplied by the manufacturer. Opaque scenes are retained and flagged for visual review; rembg candidates are saved separately. Automatic segmentation cannot certify that an implant is anatomically complete.

### What is and is not automatic

For new layouts, family detection and callout grouping use font-aware heading heuristics and are explicitly flagged. Multiple systems may share a source page; assigning tables/images to families requires review. No claim is made that arbitrary catalogs can be correctly interpreted without inspection. Unreadable text is not reconstructed; empty translations, units, categories and uncertain symbols are flagged. Image-only PDFs need OCR/transcription by a reviewer; no OCR numbers are silently trusted.

Cynthia uses a SHA-256 matched, reviewed extraction profile in `scripts/profiles/cynthia-2025-09.json`, with verified numeric tables and professional bilingual prose. It runs through the same PDF/image pipeline. A changed PDF cannot accidentally reuse that profile. Profiles are data, not individual page templates.

For every import run, Codex reads the extracted source and translates the prose itself into professional Russian medical terminology, preserving English, all numbers, reference codes, units, ranges and symbols. No external translation service or translation adapter is used. The Python extractor cannot itself invoke the assistant: it leaves unfamiliar Russian text empty and records a translation task rather than fabricating it. The import task is not complete until Codex has filled every required translation in the system JSON and run:

```
python scripts/finalize-translation.py content/products/<brand>/<system>.json
```

The finalizer refuses missing translations or changed numeric tokens, and marks every translated field for human medical review via `review.translatedFields`. The review page lists these fields and highlights the corresponding preview text in yellow. Publishing rejects missing bilingual prose. Existing verified profile text still receives translation-review metadata.

Real-ESRGAN enhancement can be run with `scripts/enhance-catalog-images.py --system <system-json> --binary <official-ncnn-binary>`. It preserves originals in `_originals`, processes low-resolution images with the general model, and produces exact 2× output with the original alpha masks. The generic renderer and listing tiles cap images at their recorded final pixel dimensions. Originals and processing manifests are not shipped in the public build.

An import refuses to overwrite published content or a manually edited draft. Unedited drafts can be regenerated. Reports retain source page numbers and field paths.

## Local review

```
node build.mjs
python3 scripts/review-server.py --port 4180
```

Open `http://127.0.0.1:4180/admin/review`. The server binds **only** to loopback. The preview on the left uses the same generic renderer as published pages. On the right are yellow field flags and original page images; click any page for the full-size reference. RU/EN switch, JSON editor, save, skip and publish controls are provided. Skipped drafts can be restored to the list with the checkbox. Publishing requires an explicit user click and acknowledgment of flags, validates the JSON, then rebuilds locally. It never deploys to hosting. The JSON editor preserves system identity, makes edits drafts, and checks a content hash to prevent overwriting concurrent changes.

Mutation endpoints require both a process-random token and exact localhost Origin. Invalid JSON, path traversal and arbitrary file paths are rejected. The server and admin files are not bundled in the public build. Deploy only `dist/`, never the repository or `public/` wholesale.

## Validation

```
node build.mjs
npm test
```

`npm test` runs every `tests/*.test.mjs` JavaScript file and every `tests/test_*.py` Python file, including review-server tests. It uses `.venv-catalog/bin/python` when installed, otherwise `python3`; set `PYTHON` to select another catalog environment. With `.venv-catalog/` installed, plain `npm test` needs no prefix. Missing Python dependencies fail the suite rather than silently skipping OCR tests. `npm run test:js` is the explicitly JavaScript-only shortcut.

Cynthia publication is authorized after the user-approved review decisions. Do not process another PDF without user confirmation.

## Universal system page

Every published system uses `src/system-page.mjs`, `src/system.css` and `src/system.js`; the build emits both language routes. Optional content defaults to empty arrays/text via `normalizeSystem()`. A minimal entry needs its identity, bilingual name, hero image, status, and any tables it contains; absent sections and navigation tabs disappear. Source PDFs, cover thumbnails, editions and file sizes are prepared at build time and in the local review preview.

Variants are optional array entries with `id`, bilingual `name`, and overrides for heroImage, description and gallery. Root features/tables are shared, then variant-specific arrays are added. Root components are shared unless `variant.componentIds` selects a subset, with `variant.components` optionally adding more. `?variant=<id>` survives reload/back/forward and language changes. All panels are generated statically; switching needs no server request. Without JavaScript, the initial variant and its data remain readable.

Table `componentId` connects a table to existing component artwork; `componentImage` can provide an explicit thumbnail. `sourcePages` links to the actual PDF page with `#page=N`; the PDF crop is never presented as a component cutout. Clean circle markers preserve the exact ●/○ semantics and legends.

For interactive features, each hotspot has `image`, `x`, `y` (percent) and `featureId`. Optional alternate images are shown as viewing-angle buttons. Features without hotspots use a three-column card grid. `exploded: true` opts components into a one-time separation animation; `component.explodedOffset: {x,y}` can set the separation offset in pixels, and `explodedImage` can add the actual exploded assembly artwork. No assembly relationships or dimensions are inferred from the animation.

Related systems use published entries with the same non-empty subcategory, up to four; the section is omitted if no matches exist. Never add unrelated or fictional recommendations to fill the row.

The quote form is intentionally a local demonstration: it validates input, logs the current system/variant and form fields to the browser console, then displays a thank-you state. It sends no email or network request. Entry animations run once and respect reduced-motion preferences. Images remain capped at their native dimensions; the hero is prioritized and remaining WebP images lazy-load. Legacy PNG/JPEG renders were losslessly converted to WebP; original source assets are retained.

## Catalog library, discovery and listing scale

Run `npm ci` once, then `npm run build`. The build emits `/catalogs/` and `/en/catalogs/`, `catalog-library-index.json`, and a prebuilt Fuse search index (`search-index.json`). Only published systems contribute. Unique `sourcePdf` values create catalog cards automatically, with exact PDF page counts, byte sizes, first-page WebP covers, edition and links to their published families. A system may provide bilingual `catalogTitle` to name a shared multi-system brochure; otherwise its bilingual system name is used. No unrelated source PDFs are imported or exposed by scanning the source folder.

Search loads its local Fuse module and index on first opening. It indexes RU/EN names, descriptions, component names, reference codes and table values, including variant data. Results are grouped, with six initial results per group and a Show more button; arrow keys choose a result, Enter opens it, and Esc closes. Component links select the appropriate variant. Catalog links open the library viewer directly. All interface strings are in `src/i18n/discovery.mjs`.

The PDF viewer lazily loads the locally bundled PDF.js worker and uses byte-range requests with streaming/automatic prefetch disabled. It renders only the current page/spread at full size. Only visible/nearby thumbnail pages render, in sequence. Closing cancels page work and destroys the PDF worker. PDF bytes are fetched progressively when the hosting server supports `Accept-Ranges`; the local review server supports standard single-byte ranges and HEAD. A future production host must serve PDF byte ranges for equivalent behavior. Reduced-motion preferences disable page transitions.

`src/catalog-engine.js` provides shared filter/sort/pagination logic, tested with 1,000 synthetic systems. Facets are derived from the scoped published systems, including subcategory. Counts apply all other selected facet groups and the search query; selecting multiple values inside a group uses OR. Zero-count options disappear. Reset remains available even when active options become hidden. Results load 24 at a time. Filters, sort and query survive language changes and URL reloads. Header Products menus derive Brand → Category links and counts from published listings. Draft categories never appear.

## Presentation and taxonomy settings

`content/settings.json` stores `brandOrder` using canonical brand keys, for example `double-medical`, `conmed`, `synimed`. Remaining published brands sort alphabetically. The menu promo selects `isNew` systems by `publishedAt` or the review publication timestamp; undated migrated entries sort after dated publications, with a stable slug fallback. Brand menu links use their own generated listing pages.

Clinical `specialty` values are restricted at normalization to Orthopedics (`orthopedics`), Traumatology (`traumatology`), Spine surgery (`spine`), Sports medicine (`sports`), General surgery (`surgery`). Other legacy specialty terms move to the `subcategories` array; the singular `subcategory` retains its first value for compatibility. Knee/shoulder labels are translated as anatomical subcategories. Facet groups with at most one available option are hidden; Reset remains available.

Catalog cover settings persist per PDF in `content/catalogs/<brand>/<catalog-slug>.json`. `coverImage` is a web path to a local image, e.g. `/images/catalog-covers/example.webp`. The default generated cover uses `coverCrop` normalized page coordinates (`x`, `y`, `width`, `height`). Landscape pages default to the right half, or the right third for aspect ratios of 2.1 or wider. Cynthia uses the right third. Editing the crop regenerates the default image at build time; setting `coverImage` to a different existing image under `public/images/` or `src/assets/` overrides automatic cropping. The PDF viewer still shows complete original pages.

Migrated source content was reviewed on 2026-11-18. The complete per-product provenance and limitations are in `reports/legacy-content-review.md`, with fetched source text in `reports/legacy-content-source-audit.json`. Never import those audit files or `_originals` into the public build.

## Outlined / scanned PDF OCR mode

Tesseract 5+ with English traineddata is required (`brew install tesseract` on macOS), plus the catalog requirements. Run one authorized source PDF:

```
U2NET_HOME="$PWD/.rembg-models" OMP_NUM_THREADS=1 .venv-catalog/bin/python scripts/import-catalog.py catalogs-source/conmed/advanced-visualization-system.pdf --ocr
```

`--ocr-only` with `--ocr` caches evidence before drafting. The renderer uses 400 DPI; English Tesseract LSTM reads each page with PSM3 and PSM11 independently. PSM11 handles the brochure's sparse columns more reliably than single-block PSM6 (initial PSM6 TSVs remain diagnostic artifacts, not accepted code evidence). Each word stores raw text, confidence, normalized and pixel bounds, physical PDF page and printed page. No O/0, I/l/1, S/5 or B/8 substitution is allowed. Codes need exact agreement between the two independent readings, a match to the visually transcribed source candidate and confidence ≥90 in both passes. Otherwise the table cell is `null`, the code is absent from accepted REF arrays, and the report/review pane retain both readings plus the unconfirmed source candidate. A blank printed code cell stays an empty string, separately distinguished from uncertain OCR.

A SHA-matched layout recipe under `scripts/profiles/ocr/` binds the reviewed section/subgroup/table/image regions to the correct PDF. Source-profile parts contain Codex-authored professional Russian plus retained English. Unknown outlined catalogs stop after OCR until their section layout and translations are reviewed, rather than pretending font heuristics work without a text layer. The importer never publishes and refuses to overwrite published or manually edited content. Text-layer imports are unchanged; an empty text layer without `--ocr` stops explicitly.

CONMED Advanced Visualization creates 10 section drafts, 35 heading subgroups and 238 ordering components. Each subgroup has its original arbitrary-width table; explicit Eyecup/Cartridge columns and source blanks are preserved. Only explicitly associated illustrated components appear as cards; other ordering items remain in their tables. Component groups retain all photos and captions. Masks use rembg, preserve caption text, then conservatively restore non-white thin structures from original pixels while removing only edge-connected near-white paper. Original rendered crops are retained in `_originals`. Device pixels are never fabricated. Source overlaps and malformed wording remain flagged.

QR codes are decoded locally by ZXing-C++ from 400-DPI renders on every import (cached by source SHA). Only decoded conmed.com `/products/` URLs become manufacturer product-page links. Manufacturer literature and external videos remain separate source references in the report. Company/About text and exact printed contacts are reported without modifying site content. Physical pages1/2/3/17/18/19/20 generate no systems; the sheath section's printed pages8–11 are physical PDF pages10–13.

The local review pane supports source-position jumps: click an ordering-table cell, a component, a flagged-field source button or an item in the position list to highlight the corresponding rectangle on the original page. Source images lazy-load. This source interactivity and the yellow uncertainty flags are draft-only. A small market-availability note is retained on each imported system. Drafts, raw OCR, source reports and draft assets are excluded from `dist/`.

### Second-stage 600 DPI verification

For the CONMED test import, `scripts/verify-catalog-codes.py --prepare` renders physical product pages 4–16 at 600 DPI and caches PSM3/11 evidence. It also prepares full item-line crops/contact sheets for every originally flagged code. `scripts/prepare-code-ocr.py` adds isolated-code PSM7/13 readings; `--refine` adds tight ink crops with PSM7/8/13 at two scales. All raw characters, confidence values and crop coordinates are retained. These scripts do not generate visual readings.

An assistant must actually open every flagged item-line crop and independently record its reading in `reports/conmed/verification-600/visual-readings.json`. `scripts/verify-catalog-codes.py --verify` accepts only a clear visual reading matching an OCR token or a supported first-character-only table-pattern candidate. At least two distinct already-confirmed codes in the same table support each pattern; subsequent digits cannot be changed, added or removed. Confidence below the initial 90 threshold can be resolved by direct visual agreement. Manufacturer SKU/ordering-row matches are separate corroboration with exact source URLs, never a replacement for the source reading.

`--apply` updates only the 10 matching, SHA-checked drafts, their table cells, component REF arrays, source images and code flags. The original import report and JSON drafts are backed up before applying; the normal importer refuses to overwrite these code-verified drafts. Nothing in this verification workflow publishes content. The detailed report preserves all 257 occurrence audits, including 212 visual readings and every unresolved reading. Five genuinely blank source cells remain distinct from unresolved values.

## List-type catalogs

`catalogType: "list"` selects the catalog-number presentation. OCR list imports set it by default through `scripts/list_catalog_presentation.py`. Subgroups remain in `componentGroups` and `specTables`; table metadata supports bilingual `description`, `keyParameters: [{parameter,value}]`, `images` with `imageCaption`, and optional `compatibilityNotes`. Numerical callouts become subgroup key parameters; uncertain classifications remain internal review flags instead of duplicate feature cards. Source descriptions are not concatenated into the overview.

The universal renderer uses `src/list-catalog.mjs`. It provides desktop sticky subgroup navigation, a mobile jump selector, literal bilingual row search/highlighting, verbatim monospace reference codes, copy controls and row selection. The browser stores only selected catalog item names, codes and quantities in `xpmed.catalog-request.v1`. The request form includes those items and per-row quantities, preserves free-text additions, and remains a console-only demo. Selections persist across list systems and language changes. Clearing the selection is explicit.

Prefer original embedded PDF photo objects: `scripts/pdf_product_images.py` excludes separate vector caption artwork while keeping native source dimensions. Preserve originals, remove backgrounds with rembg, add padding, and render captions as HTML. Reviewed spatial caption masks remain a fallback for flattened images, with unreviewed removal flagged. Do not erase device markings or invent missing pixels.

The authorized CONMED regrouping creates 11 drafts from the previous 10: the old mixed arthroscopy draft and the page-9 UHD/HD draft are consolidated into Arthroscopes, Sheaths/Bridges and Cannulas. The mixed UHD ordering group is split between scopes and compatible sheaths/bridges without changing a single ordering cell. All 238 rows, 257 nonblank code occurrences, 5 source blanks and the internal T4907 correction survive. `reports/conmed/list-layout/before/` preserves the pre-layout drafts; `report.json` stores the original cell snapshot and migration result. Related drafts link through the local review page; public related links never expose drafts. Historical OCR verification cannot overwrite the reorganized files.
