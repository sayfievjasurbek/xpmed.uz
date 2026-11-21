"""Partial catalogs must not render or OCR pages outside the authorized range."""
import unittest,tempfile,sys
from pathlib import Path
from unittest.mock import patch
import pymupdf as fitz
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from catalog_ocr import extract_ocr
class OCRPageScopeTests(unittest.TestCase):
 def test_only_explicit_pages_are_dispatched(self):
  with tempfile.TemporaryDirectory()as directory:
   base=Path(directory);pdf=base/'source.pdf';doc=fitz.open()
   for _ in range(5):doc.new_page()
   doc.save(pdf);doc.close();calls=[]
   def extract(task):calls.append(task[-1]);return {'page':task[-1]}
   with patch('catalog_ocr._extract_page',side_effect=extract),patch('catalog_ocr.subprocess.run')as run:
    run.return_value.stdout='tesseract test\n';result=extract_ocr(pdf,base/'reference',page_numbers=[4,3,3],workers=1)
   self.assertEqual(calls,[3,4]);self.assertEqual([r['page']for r in result],[3,4])
 def test_out_of_bounds_is_rejected_before_extraction(self):
  with tempfile.TemporaryDirectory()as directory:
   base=Path(directory);pdf=base/'source.pdf';doc=fitz.open();doc.new_page();doc.save(pdf);doc.close()
   with patch('catalog_ocr._extract_page')as extract,patch('catalog_ocr.subprocess.run')as run:
    run.return_value.stdout='tesseract test\n'
    with self.assertRaises(ValueError):extract_ocr(pdf,base/'reference',page_numbers=[2])
    extract.assert_not_called()
