# Double Medical Trauma Catalogue — Part 3

New systems: 138; published: 138; drafts: 0; additive merges: 1.
Implant/component families: 125; instrument sets: 10; instrument/case collections: 3.
Printed REF occurrences found / verified: 946 / 946; 884 distinct codes. Verification confirms what is printed; source duplicate handling is documented below.
Images: 426. Original native photos retained; Real-ESRGAN exact 2x before rembg; two original scene photos retained after failed ring-interior masks.

## Source ranges
- Section 9 External Fixator Set: PDF 530–578; index 529 excluded.
- Section 10 Pediatric System: PDF 582–608; index 581 excluded.
- Section 11 Patella Pin System: PDF 612–617; index 611 excluded.
- Section 12 General Instruments: PDF 620–628; index 619 excluded.
- Section 13 Implant Case and Optional Instrument: PDF 632–643; index 631 excluded.

## Existing systems merged
- Cable / Серкляжный трос: PDF [612], matched by name; earlier descriptions, material tables, hero and publication preserved. New material/dimension rows remain separate from the old rows.

All earlier system JSON files are byte-identical except the documented additive Cable merge. No sections 1–8 were re-imported.

## Open real issues
None.

## Source corrections / source index issues
- PDF 585: Source prints REF 020940003 for 150° / 3 holes / 89 mm and again for 140° / 4 holes / 105 mm. Owner directed retention of one best-supported row. Retained the 150° row: it follows the 02091/02092/02093/02094 angle series; omitted the second row from the product table. Original evidence remains in the internal OCR audit. The manufacturer has not confirmed the omitted row’s REF.
- PDF 611: Index places Patella Pin Instrument Set at 11/4; actual set pages are 11/6–11/7 (PDF 616–617). Actual source pages imported; no product values changed.

## Random sample of 20 rows

| System | PDF page | REF | Size / description |
|---|---:|---|---|
| 3.0mm Cannulated Screw for 3.0mm Epiphyseal Plate, self-tapping | 591 | 060980014 | 3.0mm Cannulated Screw for 3.0mm Epiphyseal Plate, self-tapping · Length: 14 |
| Angulation of Joint Device | 549 | 108873100 | Angulation of Joint Device · Length: 150 |
| Support Shaft, of 3-D External Fixator | 559 | 100155500 | Support Shaft, of 3-D External Fixator · Length: 130-185 |
| 6.0mm Cancellous Bone Screw | 563 | 100240120 / 105220002S | 6.0mm Cancellous Bone Screw · Size: Ø6.0/Ø5.0*120/50 |
| Instrument Set for Removal of Damaged Screws | 626 | 110392300 | Spare Centering Pin for Hollow Reamer, Ø4.5 |
| Large External Fixation Modular Rod Instrument Set | 574 | 111910600 | Drill Guide, for Bone Screws, Ø5.0/pØ8.0, long |
| Carbon Fiber Rod | 542 | 100390125 | Carbon Fiber Rod · Diameter: 11, Length: 125 |
| 6.0mm Cortex Bone Screw | 562 | 100230100 / 105210001S | 6.0mm Cortex Bone Screw · Size: Ø6.0/Ø5.0*100/40 |
| Carbon Fiber Rod | 542 | 100380065 | Carbon Fiber Rod · Diameter: 8, Length: 65 |
| External Fixator for Hand II | 531 | 101350100 | External Fixator for Hand II |
| Threaded Rod | 550 | 108870807 | Threaded Rod · Size: M6*160 |
| U-Ring | 549 | 108870406 | U-Ring · Diameter: 180 |
| 6.0mm Taper Bone Screw | 563 | 101210001 | 6.0mm Taper Bone Screw · Size: Ø6.0/Ø5.0*100/30 |
| 6.0mm Cancellous Bone Screw | 563 | 100240200 / 105220004S | 6.0mm Cancellous Bone Screw · Size: Ø6.0/Ø5.0*200/50 |
| U-Ring, long | 549 | 108870504 | U-Ring, long · Diameter: 140 |
| U-Ring | 558 | 100154704 | U-Ring · Diameter: 140 |
| Small External Fixation Modular Rod System Instrument Set | 571 | 111910500 | Drill Guide for Bone Screws, Ø4.0/Ø8.0 |
| 6.0mm Taper Bone Screw | 563 | 101210003 | 6.0mm Taper Bone Screw · Size: Ø6.0/Ø5.0*130/35 |
| 2.0mm Kirschner Wire, with olive head | 565 | 102710200 | 2.0mm Kirschner Wire, with olive head · Size: Ø2.0*350/200 |
| 6.0mm Taper Bone Screw | 563 | 100870001 / 105230001S | 6.0mm Taper Bone Screw · Size: Ø6.0*130/40 |

## All new system names
- Mini External Fixator I / Мини-аппарат внешней фиксации I — published; PDF 530
- Mini External Fixator II / Мини-аппарат внешней фиксации II — published; PDF 530
- Mini External Fixator III / Мини-аппарат внешней фиксации III — published; PDF 530
- External Fixator for Hand I / Аппарат внешней фиксации для кисти I — published; PDF 531
- External Fixator for Hand II / Аппарат внешней фиксации для кисти II — published; PDF 531
- Threaded Shaft / Резьбовой стержень — published; PDF 531
- Threaded Shaft with Ball Joint / Резьбовой стержень с шаровым шарниром — published; PDF 531
- Pin Clamp / Зажим для стержня — published; PDF 531, 532
- L-Pin Clamp / L-образный зажим для стержня — published; PDF 531
- External Fixator for Wrist and Forearm I / Аппарат внешней фиксации для лучезапястного сустава и предплечья I — published; PDF 532
- External Fixator for Wrist and Forearm III / Аппарат внешней фиксации для лучезапястного сустава и предплечья III — published; PDF 532
- External Fixator for Wrist and Forearm IV / Аппарат внешней фиксации для лучезапястного сустава и предплечья IV — published; PDF 532
- Ulnar Clamp / Локтевой зажим — published; PDF 532
- External Fixator for Elbow / Аппарат внешней фиксации для локтевого сустава — published; PDF 533
- Regulator / Регулировочный узел — published; PDF 533, 544, 545
- External Fixator for Calcaneus / Аппарат внешней фиксации для пяточной кости — published; PDF 534
- Drill Sleeve for Calcaneus External Fixator / Сверлильная втулка для аппарата внешней фиксации пяточной кости — published; PDF 534
- External Fixator for Pelvis / Аппарат внешней фиксации для таза — published; PDF 535
- Post / Опорная стойка — published; PDF 536, 537
- Post to Pin Coupling / Соединитель стойки и стержня — published; PDF 536, 538
- Rod to Pin Coupling / Соединитель штанги и стержня — published; PDF 536, 538, 540
- Rod Clamp / Зажим для штанги — published; PDF 536, 538, 541
- Connecting Rod for Elbow Joint / Соединительная штанга для локтевого сустава — published; PDF 536
- Circular Connecting Rod / Дугообразная соединительная штанга — published; PDF 537
- Curved Rod / Изогнутая штанга — published; PDF 537
- Post, 0°, Ø11.0 / Опорная стойка, 0°, Ø11.0 — published; PDF 539
- Post, 30°, Ø11.0 / Опорная стойка, 30°, Ø11.0 — published; PDF 539
- Post to Pin Coupling, 5 Holes, Ø11.0–Ø6.0 / Соединитель стойки и стержня, 5 отверстий, Ø11.0–Ø6.0 — published; PDF 539
- Rod to Pin Coupling, Ø11.0/Ø8.0–Ø6.0/Ø5.0 / Соединитель штанги и стержня, Ø11.0/Ø8.0–Ø6.0/Ø5.0 — published; PDF 539
- Pin Coupling / Соединитель стержней — published; PDF 540
- Carbon Fiber Rod / Углепластиковая штанга — published; PDF 541, 542
- 3.0mm Titanium Alloy Rod / Штанга из титанового сплава 3.0 мм — published; PDF 541
- Rail / Рейка — published; PDF 543, 545, 546
- Bone Screw Clamp I / Зажим для костных винтов I — published; PDF 543, 545, 546
- Bone Screw Clamp II / Зажим для костных винтов II — published; PDF 543, 545, 546
- Bone Screw Clamp III / Зажим для костных винтов III — published; PDF 543, 545
- Bone Screw Spacer / Проставка для костных винтов — published; PDF 543, 545
- Dynamic-Clamp / Динамический зажим — published; PDF 544
- T-Clamp / T-образный зажим — published; PDF 544
- Multiplanar-Clamp / Многоплоскостной зажим — published; PDF 544
- T-Clamp, II / T-образный зажим, II — published; PDF 544
- Threaded Regulator / Резьбовой регулировочный узел — published; PDF 546
- Horizontal Transport / Узел поперечного перемещения — published; PDF 547
- Full Ring / Полное кольцо — published; PDF 548, 558
- Semi-Ring / Полукольцо — published; PDF 548
- C-Ring / C-образное кольцо — published; PDF 548
- U-Ring / U-образное кольцо — published; PDF 549, 558
- U-Ring, long / Удлинённое U-образное кольцо — published; PDF 549
- Angulation of Joint Device / Шарнирное угловое устройство — published; PDF 549
- Threaded Rod / Резьбовая штанга — published; PDF 550
- S-Threaded Rod / S-образная резьбовая штанга — published; PDF 550
- Connector Plate / Соединительная пластина — published; PDF 550
- Angle Plate, of Round External Fixator / Угловая пластина для кольцевого аппарата внешней фиксации — published; PDF 550
- Twisted Plate / Изогнутая соединительная пластина — published; PDF 551
- Retangular Column Connector with Internal Thread / Прямоугольный соединитель с внутренней резьбой — published; PDF 551
- Universal Hinge / Универсальный шарнир — published; PDF 551
- Tube Hinge / Трубчатый шарнир — published; PDF 551
- Tube-Screw Hinge / Трубчато-винтовой шарнир — published; PDF 552
- Tube-Screw Hinge and Shaft, of Round External Fixator / Трубчато-винтовой шарнир со стержнем для кольцевого аппарата внешней фиксации — published; PDF 552
- Wire Clamp, of Round External Fixator / Спицефиксатор для кольцевого аппарата внешней фиксации — published; PDF 552
- Hexagonal Nut / Шестигранная гайка — published; PDF 553
- Hexagonal Screw / Винт с шестигранной головкой — published; PDF 553
- Protection Sleeve / Защитная втулка — published; PDF 553
- Spring / Пружина — published; PDF 553
- Oblique Buttress Device / Косая опорная стойка — published; PDF 553
- Screw Clamp / Винтовой зажим — published; PDF 553
- Wire Clamp / Спицефиксатор — published; PDF 554
- Extender / Удлинитель — published; PDF 554
- Extension Plate / Удлинительная пластина — published; PDF 554
- Extension Plate II / Удлинительная пластина II — published; PDF 555
- Washer / Шайба — published; PDF 555
- Variable Angle Washer, of Round External Fixator / Шайба с переменным углом для кольцевого аппарата внешней фиксации — published; PDF 555
- Compression Nut / Компрессионная гайка — published; PDF 555
- Complex Hinge / Комбинированный шарнир — published; PDF 556
- Hinge with External Thread / Шарнир с наружной резьбой — published; PDF 556
- Connecting Bolt I / Соединительный болт I — published; PDF 556
- Hinge with Internal Thread / Шарнир с внутренней резьбой — published; PDF 557
- Retangular Column Connector with Internal Thread, of Round External Fixator / Прямоугольный соединитель с внутренней резьбой для кольцевого аппарата внешней фиксации — published; PDF 557
- Connecting Bolt II / Соединительный болт II — published; PDF 557
- Square Nut / Квадратная гайка — published; PDF 557
- Silicone Cap / Силиконовый колпачок — published; PDF 557
- G-Ring / G-образное кольцо — published; PDF 558
- Buttress Shaft / Опорный стержень — published; PDF 559
- Support Shaft / Поддерживающий стержень — published; PDF 559
- Support Shaft, of 3-D External Fixator / Поддерживающий стержень для 3D-аппарата внешней фиксации — published; PDF 559
- Buttress Shaft, of 3-D External Fixator / Опорный стержень для 3D-аппарата внешней фиксации — published; PDF 559
- Numbered Ring / Маркировочное кольцо с номером — published; PDF 560
- Direction Indication Ring / Кольцо-указатель направления — published; PDF 560
- 2.5mm Cortex Bone Screw I / Кортикальный стержень-винт I 2.5 мм — published; PDF 560
- 2.5mm Cortex Bone Screw II / Кортикальный стержень-винт II 2.5 мм — published; PDF 560
- 4.0mm Cortex Bone Screw / Кортикальный стержень-винт 4.0 мм — published; PDF 561
- 4.0mm Cancellous Bone Screw / Спонгиозный стержень-винт 4.0 мм — published; PDF 561
- 5.0mm Cortex Bone Screw / Кортикальный стержень-винт 5.0 мм — published; PDF 562
- 5.0mm Cancellous Bone Screw / Спонгиозный стержень-винт 5.0 мм — published; PDF 562
- 6.0mm Cortex Bone Screw / Кортикальный стержень-винт 6.0 мм — published; PDF 562
- 6.0mm Cancellous Bone Screw / Спонгиозный стержень-винт 6.0 мм — published; PDF 563
- 6.0mm Taper Bone Screw / Конический стержень-винт 6.0 мм — published; PDF 563, 564
- 6.0mm Reduction Bone Screw, Thread / Репозиционный стержень-винт с резьбой 6.0 мм — published; PDF 564
- 4mm Threaded Bone Pin / Резьбовая костная спица 4 мм — published; PDF 564
- 3.0mm Calcaneus Bone Screw / Стержень-винт для пяточной кости 3.0 мм — published; PDF 565
- 3.0mm Cortex Bone Screw II / Кортикальный стержень-винт II 3.0 мм — published; PDF 565
- 2.0mm Kirschner Wire, with olive head / Спица Киршнера 2.0 мм с оливой — published; PDF 565
- 2.0mm Kirschner Wire / Спица Киршнера 2.0 мм — published; PDF 565
- Pediatric Hip Locking Plate 2.7, head 2 holes / Детская блокируемая пластина для проксимального отдела бедренной кости 2.7 — 2 отверстия в головной части — published; PDF 582
- Pediatric Hip Locking Plate 2.7, head 3 holes / Детская блокируемая пластина для проксимального отдела бедренной кости 2.7 — 3 отверстия в головной части — published; PDF 582
- Pediatric Hip Locking Plate 3.5 / Детская блокируемая пластина для проксимального отдела бедренной кости 3.5 — published; PDF 583, 584
- Pediatric Hip Locking Plate 5.0 / Детская блокируемая пластина для проксимального отдела бедренной кости 5.0 — published; PDF 585
- 4.5mm Epiphyseal Plate, arc-bridge shape / Дугообразная эпифизарная пластина 4.5 мм — published; PDF 586
- 4.5mm Epiphyseal Plate, terrace shape / Ступенчатая эпифизарная пластина 4.5 мм — published; PDF 586
- 4.5mm Epiphyseal Hinge Plate / Шарнирная эпифизарная пластина 4.5 мм — published; PDF 586
- 3.0mm Epiphyseal Plate, arc-bridge shape / Дугообразная эпифизарная пластина 3.0 мм — published; PDF 587
- 4.5mm Epiphyseal Plate, butterfly shape / Эпифизарная пластина в форме бабочки 4.5 мм — published; PDF 587
- 3.5mm Pediatric Femoral Sliding Barrel Locking Plate / Детская скользящая углостабильная пластина с втулкой для бедренной кости 3.5 мм — published; PDF 588
- 3.5mm Pediatric Femoral Sliding Straight Locking Plate / Детская скользящая прямая блокируемая пластина для бедренной кости 3.5 мм — published; PDF 588
- 3.5mm Pediatric Tibia Sliding Barrel Locking Plate / Детская скользящая углостабильная пластина с втулкой для большеберцовой кости 3.5 мм — published; PDF 589
- 3.5mm Pediatric Tibia Sliding Straight Locking Plate / Детская скользящая прямая блокируемая пластина для большеберцовой кости 3.5 мм — published; PDF 589
- 5.0mm Pediatric Femoral Sliding Barrel Locking Plate / Детская скользящая углостабильная пластина с втулкой для бедренной кости 5.0 мм — published; PDF 590
- 5.0mm Pediatric Femoral Sliding Straight Locking Plate / Детская скользящая прямая блокируемая пластина для бедренной кости 5.0 мм — published; PDF 590
- 4.5mm Cannulated Screw for 4.5mm Epiphyseal Plate, self-tapping / Самонарезающий канюлированный винт 4.5 мм для эпифизарной пластины 4.5 мм — published; PDF 591
- 3.0mm Cannulated Screw for 3.0mm Epiphyseal Plate, self-tapping / Самонарезающий канюлированный винт 3.0 мм для эпифизарной пластины 3.0 мм — published; PDF 591
- Patella Pin / Спица для фиксации надколенника — published; PDF 612
- Clasp / Обжимной фиксатор — published; PDF 613
- Patella Locking Plate / Блокируемая пластина для надколенника — published; PDF 613
- Ø1.0 Clasp / Обжимной фиксатор Ø1.0 — published; PDF 613, 614
- Ø1.0 Cable / Серкляжный трос Ø1.0 — published; PDF 615
- External Fixator for Wrist and Forearm Instrument Set / Набор инструментов для аппарата внешней фиксации кисти и предплечья — published; PDF 566, 567
- Mini External Fixator Instrument Set / Набор инструментов для мини-аппарата внешней фиксации — published; PDF 568, 569
- Small External Fixation Modular Rod System Instrument Set / Набор инструментов для малой модульной стержневой системы внешней фиксации — published; PDF 570, 571, 572, 573
- Large External Fixation Modular Rod Instrument Set / Набор инструментов для большой модульной стержневой системы внешней фиксации — published; PDF 574, 575, 576, 577, 578
- Pediatric Hip Locking Plate 3.5/5.0 Instrument Set / Набор инструментов для детских блокируемых пластин тазобедренного сустава 3.5/5.0 — published; PDF 592, 593, 594, 595, 596, 597
- Pediatric Hip Locking Plate 2.7/3.5 Instrument Set / Набор инструментов для детских блокируемых пластин тазобедренного сустава 2.7/3.5 — published; PDF 598, 599, 600, 601, 602, 603
- 3.0/4.5 Epiphyseal Plate Instrument Set / Набор инструментов для эпифизарных пластин 3.0/4.5 — published; PDF 604, 605, 606, 607, 608
- Patella Pin Instrument Set / Набор инструментов для фиксации надколенника — published; PDF 616, 617
- Instrument Set for Medium Distractors / Набор инструментов для средних дистракторов — published; PDF 620, 621, 622, 623
- Instrument Set for Removal of Damaged Screws / Набор инструментов для удаления повреждённых винтов — published; PDF 624, 625, 626, 627, 628
- Locking Plate/Screw Case Set / Контейнеры для блокируемых пластин и винтов — published; PDF 632, 633, 634
- Intramedullary Nail/Reamer Case Set / Контейнеры для интрамедуллярных штифтов и римеров — published; PDF 635, 636, 637, 638, 639, 640
- Other Accessories and Optional Instruments / Дополнительные принадлежности и инструменты — published; PDF 641, 642, 643
