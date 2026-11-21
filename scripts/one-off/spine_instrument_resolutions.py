"""Owner-confirmed source corrections; raw OCR readings and REF codes stay intact."""
from copy import deepcopy

NAMES = {
    '111781400': {'ru': 'Кюретка, прямоугольная, угловая, левая, байонетная',
                  'en': 'Curette, rectangular, angled, left, bayoneted'},
    '111781500': {'ru': 'Кюретка, прямоугольная, угловая, правая, байонетная',
                  'en': 'Curette, rectangular, angled, right, bayoneted'},
    '110042500': {'ru': 'Удерживающая втулка для индикации крутящего момента…',
                  'en': 'Holding Sleeve for Torque Indicating…'},
}
REMOVED_IMAGES = {f'/images/products/double-medical/spine-instruments/art-214-{n:02}.webp'
                  for n in (5, 6, 7)}
RESOLVED = {'111840000': {'source-caption-truncated'},
            '113294600': {'source-caption-image-conflict'}}


def resolve_row(row):
    if row['pdfPage'] not in (214, 344):
        return row
    if row['value'] in NAMES:
        row['description'] = NAMES[row['value']]['en']
        if 'name' in row:
            row['name'] = deepcopy(NAMES[row['value']])
    flags = row.get('realFlags', [])
    resolved = [f for f in flags if f['code'] in RESOLVED.get(row.get('setCode',
                 '111840000' if row['pdfPage'] == 344 else '113294600'), set())]
    if resolved:
        row['resolvedSourceFlags'] = resolved
        row['realFlags'] = [f for f in flags if f not in resolved]
    return row


def resolve_system(system):
    code = system.get('setCode')
    if code not in RESOLVED:
        return system
    for table in system['specTables']:
        for i, row in enumerate(table['rows']):
            if row[1] in NAMES:
                row[0] = deepcopy(NAMES[row[1]])
            image = table.get('rowImages', [None] * len(table['rows']))[i]
            if image and image['src'] in REMOVED_IMAGES:
                table['rowImages'][i] = None
            elif image and row[1] in NAMES:
                image['imageCaption'] = deepcopy(NAMES[row[1]])
    system['gallery'] = [g for g in system.get('gallery', []) if g['src'] not in REMOVED_IMAGES]
    for image in system['gallery']:
        if image['src'].endswith('/art-214-04.webp'):
            image['imageCaption'] = deepcopy(NAMES['110042500'])
    for src in REMOVED_IMAGES:
        system.get('imageDimensions', {}).pop(src, None)
    if 'reviewFlags' in system:
        system['reviewFlags'] = [f for f in system['reviewFlags'] if f['code'] not in RESOLVED[code]]
    if 'review' in system:
        review = system['review']
        resolved = [f for f in review.get('flags', []) if f['code'] in RESOLVED[code]]
        for flag in resolved:
            saved = dict(flag, status='resolved', resolution='Owner-confirmed source correction; see sourceCatalogCorrections in the import report.')
            if saved not in review.setdefault('resolvedFlags', []):
                review['resolvedFlags'].append(saved)
        review['flags'] = [f for f in review.get('flags', []) if f not in resolved]
        if not review['flags']:
            review['status'] = 'source-reviewed'
    return system
