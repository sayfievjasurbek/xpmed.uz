#!/usr/bin/env python3
"""Normalise client logos and certificate scans for the About page.

Sources live beside their records in content/clients/ and content/certificates/,
so replacing a logo or a certificate is: drop the new file in, re-run this.

Client logos: the source scans are JPEGs on white. White that is connected to
the border becomes transparent; white enclosed by the artwork is kept, because
several of these logos use white as a foreground colour (the figure inside the
Medion shield, the Akfa wordmark, the ShTYoIM lettering). Keying every white
pixel would punch holes through them. The result is trimmed to its artwork and
centred on one canvas size, so every card shows the logo at the same scale.

Certificates: a WebP thumbnail for the card, plus a single-page PDF so the
existing PDF viewer can open it full screen with its own zoom controls.

Usage: .venv-catalog/bin/python scripts/prepare-brand-assets.py
"""
import sys
from pathlib import Path

from PIL import Image
import numpy as np
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
LOGO_CANVAS = (360, 150)      # every client card gets the same frame
LOGO_CONTENT = (300, 112)     # artwork is contained inside this
CERT_THUMB_WIDTH = 720        # portrait card thumbnail
WHITE = 243                   # a pixel at or above this on every channel is "white"


def background_alpha(rgb: np.ndarray) -> np.ndarray:
    """Alpha channel with border-connected white removed, interior white kept."""
    near_white = (rgb >= WHITE).all(axis=2)
    labels, count = ndimage.label(near_white)
    if count == 0:
        return np.full(rgb.shape[:2], 255, np.uint8)
    border = set(labels[0, :]) | set(labels[-1, :]) | set(labels[:, 0]) | set(labels[:, -1])
    border.discard(0)
    background = np.isin(labels, list(border))
    return np.where(background, 0, 255).astype(np.uint8)


def normalise_logo(source: Path, target: Path) -> str:
    image = Image.open(source).convert('RGB')
    rgb = np.asarray(image)
    alpha = background_alpha(rgb)
    rgba = Image.fromarray(np.dstack([rgb, alpha]), 'RGBA')

    box = rgba.getbbox()
    if box:
        rgba = rgba.crop(box)
    rgba.thumbnail(LOGO_CONTENT, Image.LANCZOS)

    canvas = Image.new('RGBA', LOGO_CANVAS, (255, 255, 255, 0))
    canvas.paste(rgba, ((LOGO_CANVAS[0] - rgba.width) // 2, (LOGO_CANVAS[1] - rgba.height) // 2), rgba)
    target.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(target, 'WEBP', quality=92, method=6)
    transparent = int((np.asarray(canvas)[:, :, 3] == 0).sum())
    share = transparent / (LOGO_CANVAS[0] * LOGO_CANVAS[1]) * 100
    return f'{image.width}x{image.height} -> {rgba.width}x{rgba.height} in {LOGO_CANVAS[0]}x{LOGO_CANVAS[1]}, {share:.0f}% transparent'


def prepare_certificate(source: Path, thumb: Path, document: Path) -> str:
    image = Image.open(source).convert('RGB')
    thumb.parent.mkdir(parents=True, exist_ok=True)
    scaled = image.copy()
    scaled.thumbnail((CERT_THUMB_WIDTH, CERT_THUMB_WIDTH * 4), Image.LANCZOS)
    scaled.save(thumb, 'WEBP', quality=88, method=6)
    document.parent.mkdir(parents=True, exist_ok=True)
    image.save(document, 'PDF', resolution=150.0)
    return f'{image.width}x{image.height} -> thumb {scaled.width}x{scaled.height}, pdf {document.stat().st_size // 1024} KB'


def main() -> int:
    logos = sorted((ROOT / 'content/clients').glob('*.jpg'))
    certificates = sorted((ROOT / 'content/certificates').glob('*.jpg'))
    if not logos or not certificates:
        print('No sources found in content/clients or content/certificates', file=sys.stderr)
        return 1

    print(f'Client logos ({len(logos)}):')
    for source in logos:
        target = ROOT / 'public/images/clients' / f'{source.stem}.webp'
        print(f'  {source.stem:<42} {normalise_logo(source, target)}')

    print(f'\nCertificates ({len(certificates)}):')
    for source in certificates:
        thumb = ROOT / 'public/images/certificates' / f'{source.stem}.webp'
        document = ROOT / 'public/catalogs/certificates' / source.stem / 'source.pdf'
        print(f'  {source.stem:<42} {prepare_certificate(source, thumb, document)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
