"""Collect three independent 600-DPI readings for each Sports Medicine REF row."""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OCR = ROOT / 'public/catalogs/double-medical/sports-medicine-catalogue/ocr'
VISION = ROOT / 'reports/double-medical/sports-medicine-catalogue/vision'
OUT = ROOT / 'reports/double-medical/sports-medicine-catalogue'
CODE = re.compile(r'(?<!\d)(\d{9}(?:S|58|8|5)?)(?!\d)')

def raw_readings(page):
    source = json.loads((OCR / f'{page:03}.json').read_text())
    vision = json.loads((VISION / f'{page:03}.json').read_text())
    readers = {}
    for mode in ('3', '11'):
        rows = []
        for line in source['passes'][mode]['lines']:
            match = CODE.search(line.get('text', ''))
            if match:
                rows.append({'reader': f'PSM{mode}', 'raw': match.group(1),
                             'text': line['text'], 'bounds': line['bounds']})
        readers[f'PSM{mode}'] = rows
    readers['Vision'] = [
        {'reader': 'Vision', 'raw': match.group(1), 'text': line['text'],
         'bounds': line['bounds']}
        for line in vision if (match := CODE.search(line['text']))
    ]
    return readers

def norm(code, page):
    if code and page <= 18:
        m = re.fullmatch(r'(\d{9})(?:S|58|8|5)?', code)
        if m:
            return m.group(1) + 'S'
    return code

def run():
    rows, uncertain = [], []
    for page in range(4, 39):
        readings = raw_readings(page)
        all_items = sorted((item for seq in readings.values() for item in seq),
                           key=lambda item: (item['bounds'][1], item['bounds'][0]))
        clusters = []
        for item in all_items:
            y = item['bounds'][1]
            group = next((g for g in clusters if abs(g['y'] - y) <= .008
                          and item['reader'] not in g['readings']), None)
            if group is None:
                group = {'page': page, 'y': y, 'readings': {}}
                clusters.append(group)
            group['readings'][item['reader']] = item
        for group in clusters:
            normalized = {reader: norm(item['raw'], page)
                          for reader, item in group['readings'].items()}
            counts = {code: list(normalized.values()).count(code)
                      for code in normalized.values()}
            candidate = max(counts, key=counts.get)
            group['code'] = candidate if counts[candidate] >= 2 else None
            group['allAgree'] = len(normalized) == 3 and len(counts) == 1
            group['verification'] = ('verified (three readers compared)'
                                     if group['allAgree'] else 'visual review required')
            group['normalizedReadings'] = normalized
            if not group['allAgree']:
                uncertain.append({'page': page, 'y': round(group['y'], 5),
                                  'candidate': group['code'], 'readings': normalized})
            rows.append(group)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'row-evidence.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2)+'\n')
    (OUT/'code-review.json').write_text(json.dumps(uncertain, ensure_ascii=False, indent=2)+'\n')
    print(f'{len(rows)} REF occurrences, {len(uncertain)} requiring direct visual reading')

if __name__ == '__main__':
    run()
