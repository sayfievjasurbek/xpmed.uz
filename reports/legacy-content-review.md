# Legacy XPMED content review

Retrieved 2026-11-18 from the exact original XPMED product URLs retained in the migration snapshot. All 32 RU/EN requests returned HTTP 200 and contained product content, not bot-verification pages. The web text extractor initially returned a cached bot page for Sequent EN; the direct official page was successfully retrieved and inspected.

Scope: 16 original product listings grouped into 13 migrated system JSON files. Cynthia was not edited. No PDFs or other manufacturer catalogs were processed.

## Outcome

- Enriched nine families with full bilingual descriptions and source-supported characteristics; added 17 bilingual feature cards across PBG, TINA, UHN and the anterior cervical cage.
- Added 12 generic characteristic/specification tables derived only from explicit source prose and product titles. The original pages contain no structured HTML specification tables. No REF/article numbers were inferred from names, sizes or suture gauges.
- Downloaded three additional manufacturer product illustrations served by XPMED. Original JPEGs are retained in the corresponding product `_originals` directories. They were processed with rembg, trimmed, padded evenly, converted to WebP and visually inspected. No material implant parts appeared missing; no broken cutouts were retained. TINA alternate art is individually marked as a cutout while its main render remains a scene.
- Four families had only a title and the already-migrated image: DISTAL reconstruction stem, Cemented Liner/Cup, GÉO System and OEC Elite. Existing descriptions were preserved; no characteristics were invented.

## Uncertainties retained

- **CrossFT 4.75 mm:** its original page describes a CUFF LINK double-row rotator-cuff system. The source wording is explicitly attributed in RU/EN and the mismatch is stored as a review warning. No assumption that CrossFT and CUFF LINK are the same product was made.
- **Anterior cervical cage:** RU and EN short introductions differ. Both meanings are retained with source-language attribution; the shared feature and screw information is imported consistently.
- **Synicem:** legacy CE/ISO and clinical-performance claims were imported as statements from the old descriptions, not independently re-certified. Awkward source translations were normalized into professional medical terminology without adding new indications or measurements.
- **Additional illustrations:** they are native low-resolution product renders on the old site. They were not upscaled and their final pixel dimensions are recorded for native-size display caps.

## Products and exact sources

### Modular reconstruction stem

`content/products/biotechni/distal-locking-modular-reconstruction-stem.json`

No additional product prose, tables or images. Existing content retained.

- Modular reconstruction stem: [RU](https://xpmed.uz/product/novinki-2/distal-locking-modular-reconstruction-stem/) · [EN](https://xpmed.uz/product/new/distal-locking-modular-reconstruction-stem-2/)

### GÉO System

`content/products/biotechni/geo-system.json`

No additional product prose, tables or images. Existing content retained.

- GÉO System: [RU](https://xpmed.uz/product/novinki-2/geo-system/) · [EN](https://xpmed.uz/product/new/geo-system-2/)

### POPLOK 3.3 mm anchor

`content/products/conmed/anchor-3-3mm-poplok-single-strand-2-hifi.json`

Full description and PEEK/knotless/suture/diameter characteristics.

- POPLOK 3.3 mm anchor: [RU](https://xpmed.uz/product/conmed/plechevoj-sustav/yakor-33-mm-poplok-s-odnoj-nityu-2-hifi/) · [EN](https://xpmed.uz/product/conmed-en/shoulder-joint/anchor-3-3mm-poplok-single-strand-2-hifi/)

### CrossFT anchor system

`content/products/conmed/crossft-anchor-system.json`

Both CrossFT descriptions merged into the family overview, component characteristics table; source naming inconsistency flagged.

- CrossFT knotless anchor: [RU](https://xpmed.uz/product/conmed/implant/yakor-crossft-4-75-mm-bezuzlovoj/) · [EN](https://xpmed.uz/product/conmed-en/implant-en/anchor-crossft-4-75-mm-knotless/)
- CrossFT 4.5 mm anchor: [RU](https://xpmed.uz/product/conmed/plechevoj-sustav/yakor-crossft-4-5-mm-na-otvertke-s-2-mya-nityami-2-hi-fi/) · [EN](https://xpmed.uz/product/conmed-en/shoulder-joint/anchor-crossft-4-5-mm-on-a-screwdriver-with-2-threads-2-hi-fi/)

### Sequent instrument

`content/products/conmed/sequent-continuous-meniscus-suture-instrument-curved-4-and-7-charged-implants.json`

Full meniscal-repair description and exact implant/stitch-count characteristics.

- Sequent instrument: [RU](https://xpmed.uz/product/conmed/kolennyj-sustav/instrument-dlya-nepreryvnogo-shva-meniska-sequent-izognutyj-4-i-7-zaryazhennyh-implanta/) · [EN](https://xpmed.uz/product/conmed-en/knee-joint/sequent-continuous-meniscus-suture-instrument-curved-4-and-7-charged-implants/)

### PBG cementless stem

`content/products/double-medical/pbg-proximal-bone-growth-cementless-stem.json`

Full indications, six features, coating/taper characteristics; one alternate stem image.

- PBG cementless stem: [RU](https://xpmed.uz/product/double-medical/stenocostal-plate-ru/sistema-dlya-tazobedrennogo-sustava-joint/besczementnaya-tazobedrennaya-nozhka-pbg/) · [EN](https://xpmed.uz/product/double-medical-en/stenocostal-plate/hip-joint-system/pbg-proximal-bone-growth-cementless-stem/)

### TINA spine system

`content/products/double-medical/tina-spine-5-5-6-0-system.json`

Full description, indications, screw options and instruments; six features, characteristic table; one alternate screw-pair image.

- TINA spine system: [RU](https://xpmed.uz/product/double-medical/stenocostal-plate-ru/sistema-tina/sistema-transpedikulyarnyh-vintov-tina/) · [EN](https://xpmed.uz/product/double-medical-en/stenocostal-plate/tina-system/tina-spine-5-5-6-0-system/)

### UHN universal humeral nail

`content/products/double-medical/uhn-universal-humeral-nail.json`

Full description, indications, two features, screws, end cap and instrument-set details; locking-screw diameter table.

- UHN universal humeral nail: [RU](https://xpmed.uz/product/double-medical/trauma/universalnyj-shtift-dlya-plechevoj-kosti-uhn/) · [EN](https://xpmed.uz/product/double-medical-en/trauma-en/humeral/uhn-universal-humeral-nail/)

### Anterior cervical cage

`content/products/double-medical/zero-profile-anterior-cervical-intervertebral-locking-plate-and-cage-combination-system.json`

Both source introductions, indications, three material/surface features, locking-screw sizes and material/region table; one alternate cage image.

- Anterior cervical cage: [RU](https://xpmed.uz/product/double-medical/stenocostal-plate-ru/spinalnaya-sistema/perednij-shejnyj-blokirovannyj-kejdzh/) · [EN](https://xpmed.uz/product/double-medical-en/stenocostal-plate/spine-system/zero-profile-anterior-cervical-intervertebral-locking-plate-and-cage-combination-system/)

### OEC Elite

`content/products/ge-healthcare/oec-elite.json`

No additional product prose, tables or images. Existing content retained.

- OEC Elite: [RU](https://xpmed.uz/product/novinki-2/oec-elite/) · [EN](https://xpmed.uz/product/new/oec-elite-2/)

### Synicem bone cements

`content/products/synimed/synicem-bone-cements.json`

Full 1G, 3G and VTP descriptions; component-level descriptions retained; gentamicin dose and application tables.

- Synicem 1G bone cement: [RU](https://xpmed.uz/product/synimed/czement-2/synicem-1g-akrilovyj-czement-s-gentamiczinom-dlya-ruchnogo-naneseniya/) · [EN](https://xpmed.uz/product/synimed-en/cement/qolda-qollash-uchun-synicem-1g-gentamisinli-akrilik-tsement/)
- Synicem 3G bone cement: [RU](https://xpmed.uz/product/synimed/czement-2/synicem-3g-akrilovyj-czement-s-gentamiczinom-dlya-shpriczevogo-primeneniya/) · [EN](https://xpmed.uz/product/synimed-en/cement/synicem-3g-akrilik-tsement-shpritsni-qollash-uchun-gentamitsinli/)
- Synicem VTP bone cement: [RU](https://xpmed.uz/product/synimed/czement-2/synicem-vtp-hirurgicheskij-czement-dlya-vertebroplastiki/) · [EN](https://xpmed.uz/product/synimed-en/cement/vertebroplastiya-uchun-synicem-vtp-jaruriyat-sementi/)

### Synicem cannula

`content/products/synimed/vertebroplastiya-uchun-sinicem-steril-punching-kanulasi.json`

Full description, packaging/sterilization/material/connector details and exact three diameter–length combinations.

- Synicem cannula: [RU](https://xpmed.uz/product/synimed/igla/synicem-sterilnaya-punkczionnaya-kanyulya-dlya-vertebroplastiki/) · [EN](https://xpmed.uz/product/synimed-en/cement/vertebroplastiya-uchun-sinicem-steril-punching-kanulasi/)

### Cemented liner and cup

`content/products/unassigned/cemented-liner-cup.json`

No additional product prose, tables or images. Existing content retained.

- Cemented liner and cup: [RU](https://xpmed.uz/product/novinki-2/cemented-liner-cup/) · [EN](https://xpmed.uz/product/new/cemented-liner-cup-2/)

## New image files

- `public/images/products/double-medical/pbg-proximal-bone-growth-cementless-stem/pbg-legacy-alternate.webp` — 1009 × 769 px; [original XPMED image](https://xpmed.uz/wp-content/uploads/2022/03/99-min.jpg).
- `public/images/products/double-medical/tina-spine-5-5-6-0-system/tina-legacy-alternate.webp` — 450 × 636 px; [original XPMED image](https://xpmed.uz/wp-content/uploads/2022/03/72-min-scaled.jpg).
- `public/images/products/double-medical/zero-profile-anterior-cervical-intervertebral-locking-plate-and-cage-combination-system/cervical-legacy-alternate.webp` — 968 × 1093 px; [original XPMED image](https://xpmed.uz/wp-content/uploads/2022/03/88-min.jpg).
