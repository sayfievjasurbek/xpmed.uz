# HALL import audit

The supplied 80-page PDF is `catalogs-source/conmed/hall-powered-instruments.pdf`. Physical PDF page numbers are used throughout. Its contents page and several inserted pages use different printed pagination; grouping follows the contents entries and actual page headings.

## Evidence

- `verification.json`: independent 600-DPI OCR readings, isolated reads, Codex visual readings, coordinates, excluded OCR aliases/compatibility references, and exact-code confirmation in the official CONMED catalog.
- `official/hall-powered-instruments.pdf`: downloaded official manufacturer document. `official/logical.pdf` splits its spreads for position matching. The newer manufacturer's extra items are not imported.
- `bur-matrix-review.json`: column-position mapping for adjacent bur grids, including compatible guards, diameters, lengths, flutes and grit. Grit ranges are parameters, never ordering codes.
- `coating-review.json`: printed bold-code chromium-coating review for the three HALL Pro matrix pages. Row drawings retain their source gray shading.
- `source-catalog-corrections.json`: internal source conflicts and corrections. These notes are not public.
- `report.md` / `report.json`: final counts, open real flags, overlaps and the random sample.
- `random-20-rows.csv`: reproducible 20-row sample (seed 20261119), selected from rows with printed width, length and thickness.

## Import recipe

The reviewed, SHA-bound recipe is `scripts/profiles/conmed-hall-powered-instruments.json`. The actual import was run with:

```sh
python scripts/import-catalog.py catalogs-source/conmed/hall-powered-instruments.pdf --ocr --dpi 600 --workers 4
python scripts/finalize-hall-import.py
npm run build
```

The importer creates drafts; the finalizer publishes systems with no open review flags. The owner subsequently approved the remaining five HALL systems and explicitly requested clearing their flags; this source-specific decision is recorded in `publication-decision.json`. The importer intentionally refuses to overwrite a published system. Do not remove that guard to rerun an import.

The preparation scripts are source-specific: `map-hall-source.py`, `parse-hall-layout.py`, `refine-hall-codes.py`, `prepare-hall-assets.py`, `prepare-hall-missed-assets.py`, `prepare-hall-attachment-assets.py`, and `review-hall-images.py`. Human visual readings and exclusions remain in the evidence files rather than being guessed again. Real-ESRGAN outputs are downsampled to exact 2x before rembg. PDF opacity masks are restored where segmentation would lose instrument parts. Native and enhanced originals remain under `public/images/products/conmed/hall/_originals/`.

`build-hall-profile.py` composes the source recipe. `hall_reviewed_context.py` contains Codex-authored medical Russian and caption/photo matches; `hall_bur_review.py` reconciles adjacent matrices; `hall_source_notes.py` retains compatibility notes; `hall_source_review.py` assigns canonical code owners and preserves real source conflicts. There is no external translation adapter.

## Validation

The full suite contains the original 73 tests plus 7 HALL regressions. Browser checks covered RU and EN, desktop and mobile, combined dimension filters, row search, clickable full-resolution drawings, native image-size limits, the generated mega-menu category and horizontal table scrolling without page overflow. The user's existing request selection was preserved.
