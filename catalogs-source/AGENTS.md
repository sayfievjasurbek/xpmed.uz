# Catalog import workflow

Process only the PDF explicitly authorized by the user. Run `scripts/import-catalog.py` to extract draft systems and source references. Then read the source pages and translate the English prose yourself into professional Russian medical terminology, preserving the English and every numeric value, article number, unit, symbol and range. Do not use an external translation adapter or service. Leave unreadable values empty and flag them.

Complete translations in the system JSON, run `scripts/finalize-translation.py`, and keep translated fields marked for medical review. Show the import report before processing another PDF or publishing unless the user has explicitly authorized publication. Do not equate extraction heuristics with verified source data.
