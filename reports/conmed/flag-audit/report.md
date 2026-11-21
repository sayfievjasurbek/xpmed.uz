# CONMED flag audit and local publication

Final status: all 11 systems published locally; zero open flags. All 257 existing catalog-number occurrences are unchanged. Historical review decisions below are retained for audit.

## Published

- camera-systems
- conmed-arthroscopes
- hd-laparoscopes
- light-sources-and-light-guides
- medical-monitors
- sheath-and-bridge-systems
- sterilization-trays
- surgical-video-carts-and-accessories
- uhd-laparoscopes

- looking-glass
- cannulas

## Historical real issues — subsequently resolved

### Канюли — PDF page 13

Missing inner-cannula code for the 5.0" (127 mm) row.

- visual: Inner Cannula column blank; Inflow Adapter column 83234
- 600dpi-psm3: No inner-cannula code; 83234 at the right (inflow adapter)
- 600dpi-psm11: No inner-cannula code; 83234 at the right (inflow adapter)

### Система Looking Glass — PDF page 8

Unclear adapter designation for verified code AVELG52; no inferred expansion applied.

- visual: ELG Adapter A cml
- 600dpi-psm3: ELG Adapter A CMI
- 600dpi-psm11: ELG Adapter A cml

Unconfirmed interpretation: ACMI (not substituted) (not substituted).

## Initial flag decisions (final resolutions follow below)

- camera-systems / source-association-review / components: A — Generic import reminder superseded by per-cell verified OCR/visual evidence, reviewed subgroup migration and caption-free embedded PDF image extraction. Any specific unresolved issues retain separate open flags.
- cannulas / source-note / componentGroups.bridge-cannulas: A — Historical O/0 prefix ambiguity resolved by stored 600-DPI OCR plus visual verification. All bridge-cannula catalog codes have verified cell-level evidence.
- cannulas / source-note / componentGroups.pressure-sensing-cannula: B — Missing inner-cannula code for the 5.0" (127 mm) row.
- cannulas / source-association-review / components: A — Generic import reminder superseded by per-cell verified OCR/visual evidence, reviewed subgroup migration and caption-free embedded PDF image extraction. Any specific unresolved issues retain separate open flags.
- conmed-arthroscopes / source-note / componentGroups.bridge-cannulas: A — Stale flag copied during the system split: this subgroup is absent here. The actual missing-code issue remains open only on cannulas.
- conmed-arthroscopes / source-note / componentGroups.pressure-sensing-cannula: A — Stale flag copied during the system split: this subgroup is absent here. The actual missing-code issue remains open only on cannulas.
- conmed-arthroscopes / source-association-review / components: A — Generic import reminder superseded by per-cell verified OCR/visual evidence, reviewed subgroup migration and caption-free embedded PDF image extraction. Any specific unresolved issues retain separate open flags.
- conmed-arthroscopes / source-association-review / components: A — Generic import reminder superseded by per-cell verified OCR/visual evidence, reviewed subgroup migration and caption-free embedded PDF image extraction. Any specific unresolved issues retain separate open flags.
- hd-laparoscopes / image-association-review / componentGroups.hd-5-5mm-laparoscope: A — The warned-about rectangular page crops were replaced by isolated original embedded PDF photos. Visually compared all four current images/captions with PDF page 15: each matches its subgroup, with no neighboring shaft or printed caption.
- hd-laparoscopes / image-association-review / componentGroups.hd-5-5mm-extended-laparoscope: A — The warned-about rectangular page crops were replaced by isolated original embedded PDF photos. Visually compared all four current images/captions with PDF page 15: each matches its subgroup, with no neighboring shaft or printed caption.
- hd-laparoscopes / image-association-review / componentGroups.hd-10mm-laparoscope: A — The warned-about rectangular page crops were replaced by isolated original embedded PDF photos. Visually compared all four current images/captions with PDF page 15: each matches its subgroup, with no neighboring shaft or printed caption.
- hd-laparoscopes / image-association-review / componentGroups.2dhd-laparoscope: A — The warned-about rectangular page crops were replaced by isolated original embedded PDF photos. Visually compared all four current images/captions with PDF page 15: each matches its subgroup, with no neighboring shaft or printed caption.
- hd-laparoscopes / source-association-review / components: A — Generic import reminder superseded by per-cell verified OCR/visual evidence, reviewed subgroup migration and caption-free embedded PDF image extraction. Any specific unresolved issues retain separate open flags.
- light-sources-and-light-guides / source-association-review / components: A — Generic import reminder superseded by per-cell verified OCR/visual evidence, reviewed subgroup migration and caption-free embedded PDF image extraction. Any specific unresolved issues retain separate open flags.
- looking-glass / source-prose-review / componentGroups.looking-glass-light-source: B — Unclear adapter designation for verified code AVELG52; no inferred expansion applied.
- looking-glass / source-association-review / components: A — Generic import reminder superseded by per-cell verified OCR/visual evidence, reviewed subgroup migration and caption-free embedded PDF image extraction. Any specific unresolved issues retain separate open flags.
- medical-monitors / source-association-review / components: A — Generic import reminder superseded by per-cell verified OCR/visual evidence, reviewed subgroup migration and caption-free embedded PDF image extraction. Any specific unresolved issues retain separate open flags.
- sheath-and-bridge-systems / source-note / componentGroups.bridge-cannulas: A — Stale flag copied during the system split: this subgroup is absent here. The actual missing-code issue remains open only on cannulas.
- sheath-and-bridge-systems / source-note / componentGroups.pressure-sensing-cannula: A — Stale flag copied during the system split: this subgroup is absent here. The actual missing-code issue remains open only on cannulas.
- sheath-and-bridge-systems / source-association-review / components: A — Generic import reminder superseded by per-cell verified OCR/visual evidence, reviewed subgroup migration and caption-free embedded PDF image extraction. Any specific unresolved issues retain separate open flags.
- sheath-and-bridge-systems / source-association-review / components: A — Generic import reminder superseded by per-cell verified OCR/visual evidence, reviewed subgroup migration and caption-free embedded PDF image extraction. Any specific unresolved issues retain separate open flags.
- sterilization-trays / source-association-review / components: A — Generic import reminder superseded by per-cell verified OCR/visual evidence, reviewed subgroup migration and caption-free embedded PDF image extraction. Any specific unresolved issues retain separate open flags.
- surgical-video-carts-and-accessories / source-association-review / components: A — Generic import reminder superseded by per-cell verified OCR/visual evidence, reviewed subgroup migration and caption-free embedded PDF image extraction. Any specific unresolved issues retain separate open flags.
- uhd-laparoscopes / source-association-review / components: A — Generic import reminder superseded by per-cell verified OCR/visual evidence, reviewed subgroup migration and caption-free embedded PDF image extraction. Any specific unresolved issues retain separate open flags.

## Source catalog corrections

1. **Looking Glass — source PDF page 8, AVELG52.** Replace `ELG Adapter A cml` with `ELG ACMI Adapter` / `Адаптер ELG ACMI`. Keep `AVELG52`. Internal note: "Source PDF typo 'A cml' corrected to ACMI". This note is not shown publicly.
2. **Cannulas — source PDF page 13, 5.1 mm O.D., 5.0″ (127 mm) inner cannula.** The source omits its catalog number. Official CONMED imaging catalog, PDF page 18 (printed 16), repeats the omission. No official code confirmed; do not substitute the unconfirmed third-party candidate 83225. The site displays `—` and `Каталожный номер уточняйте у менеджера` / `Please confirm the catalog number with your account manager`. Keep `83234` only in the Inflow Adapter column. **Designer action:** obtain the missing inner-cannula code from CONMED and print it in the correct column.

Official source checked: https://www.conmed.com/-/media/conmed/documents/catalog/surgicalimaging_catalog.ashx#page=18
