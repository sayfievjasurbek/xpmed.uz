# CONMED Arthroscopy import report

**52 systems: 52 published, 0 drafts.** 1252 catalog-number cells, 1252 source-verified, 1252 corroborated on conmed.com. 333 native product images enhanced 2x with Real-ESRGAN before rembg.

Counts include repeated printed cells; duplicate products were not created.

| Section | Created / Published / Drafts | Codes / Verified / CONMED | Existing overlaps |
|---|---:|---:|---:|
| Shoulder Arthroscopy | 9 / 9 / 0 | 286 / 286 / 286 | 2 |
| Knee Arthroscopy | 11 / 11 / 0 | 325 / 325 / 325 | 0 |
| Hip Arthroscopy | 8 / 8 / 0 | 123 / 123 / 123 | 15 |
| Small Joint Arthroscopy | 6 / 6 / 0 | 63 / 63 / 63 | 0 |
| Arthroscopy Manual Instruments | 6 / 6 / 0 | 204 / 204 / 204 | 0 |
| Resection Products | 7 / 7 / 0 | 220 / 220 / 220 | 0 |
| Fluid Management | 3 / 3 / 0 | 16 / 16 / 16 | 0 |
| ESA Electrosurgical Arthroscopy | 2 / 2 / 0 | 15 / 15 / 15 | 0 |

## Open real flags

None.

## Source catalog corrections (internal)

- p.16 Y1802 → Y1802A (blue suture), confirm with XPMED sales — confirmed in CONMED brochure; https://www.conmed.com/-/media/conmed/documents/literature/y-knotflex_productbrochure.ashx
- p.94 missing footnote: * / ** are footnote markers, not part of the catalog numbers. Add a legend for EL9299U (concave) and EL9299D (convex); no footnote was printed. — confirmed on conmed.com; https://www.conmed.com/en/products/resection-fluid-management-and-ablation/resection/conmed-arthroscopic-resection

## Existing-system overlaps

- conmed/sheath-and-bridge-systems: DL1008, DL1009, DL1010, DLH100, DLH200, DLH460, DLH461, DLH462, DLH463, DLH580, DLH581, DLH582, DLH583, HPS-H46, HPS-H58, T4906, T4907

## Within-PDF duplicates / merges

- PDF p. 50: Positioning Devices — All catalog numbers already imported; duplicate page not created
- PDF p. 83: MASTER Arthroscopy Shoulder Instrument Set — All catalog numbers already imported; duplicate page not created
- PDF p. 91, 92: Hip Blades and Burs — All catalog numbers already imported; duplicate page not created
- PDF p. 85: Shutt Small Joint Sets — Repeated Shutt small-joint set page merged into the original family; its additional 35.60017 row is retained

## Random 20-row sample (seed 20261119)

| System | PDF page | Description | Catalog number |
|---|---:|---|---|
| Rotator Cuff Repair | 11 | 4.5mm GENESYS CrossFT Suture Anchor w/Three #2 Hi-Fi Sutures (17mm length) w/ needles | CFBC-4503NB |
| Cruciate Reconstruction Accessories | 37 | Microfracture Awl, 45°, 190.5mm length | 7202 |
| Hi-Fi Suture | 23 | Hi-Fi Passing Loop | HL7000 |
| Cruciate Reconstruction Accessories | 41 | Tunnel Dilator Sterilization Case | TD8504 |
| Instability Repair | 16 | Drill Guide, Fishmouth | Y-G001 |
| Rotator Cuff Repair | 9 | Y-Knot RC Drill Guide | Y-DGRC |
| OCD Repair | 46 | 1.5mm Arthroscopic Tip (Green) | AT1500 |
| Large Hub Shaver Blades | 96 | 5.5mm, Large Hub, Sterling, Shaver, Gator | 9260A |
| Rotator Cuff Repair | 14 | ThRevo® FT Suture Anchor, 5.0mm O.D. 18.0mm length, w/Three #2 Hi-Fi Sutures, | CF6160H |
| 24k Pump System | 106 | 24kTIPS Tube Set | 24kTIPS |
| Micro Hub Blades | 102 | 4.2mm, Micro Hub, Merlin®, Blade, Full-Radius Resector, Pre-Bent 15° | MP9249 |
| Femoral Fixation Implants | 33 | GraftMax Flex XACTPIN® | KS-FGP24 |
| Hi-Fi Suture | 23 | #2 Hi-Fi Suture, 12/Box, Single 36" Strand, White-Green Co-Braid, No Needle | H5140 |
| Biocomposite Interference Screws | 29 | GENESYS Matryx 7.0 x 25.0mm Interference Screw | 237025M5 |
| Hip Suture Passers | 57 | Spectrum MVP, Medium Crecent Hook, Extended Length, Disposable, Packaged Sterile, 3 per Box | C6400EL |
| Suture Passing | 19 | Seahawk Suture Passer (right, up) | GU2001 |
| Concept | 82 | Retriever, 15° Upswept | C6801 |
| Micro Hub Burs and Routers | 104 | 6.0mm, Micro Hub, Sterling, Bur, Oval | MH9102 |
| OCD Repair | 46 | Wrench | AA1520-05 |
| Concept | 81 | Straight | C6700 |

## Validation after source corrections

- Full suite: 68 passed (49 JavaScript + 19 Python), 0 skipped.
- Static build: 104 published systems; drafts/admin excluded.
- Both corrected systems published with 0 open flags; RU/EN public pages exclude internal correction notes.
