#!/usr/bin/env python3
"""Re-cut three catalog photos that still shipped as white rectangles.

HALL Osteon, G-Ring and the Knotless Syndesmosis CFLoop Button were extracted
from catalog pages as opaque crops, so on the product pages they read as white
boxes. This upscales each one before segmentation (rembg is far better on a
larger input, and the G-Ring source is only 324px), writes an RGBA candidate,
and also writes the fallback treatment: the photo flattened onto the site grey
#EEF0F2 with a soft feathered edge.

Nothing is applied automatically. Both candidates go to
reports/conmed/white-background-cutouts/ for visual review, because automatic
segmentation cannot be trusted on thin cables and wires.

Usage:
  U2NET_HOME="$PWD/.rembg-models" OMP_NUM_THREADS=1 \
    .venv-catalog/bin/python scripts/one-off/refresh-white-background-cutouts.py
"""
import sys
from pathlib import Path

from PIL import Image, ImageFilter
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / 'reports/conmed/white-background-cutouts'
SITE_GREY = (238, 240, 242)   # --light / #EEF0F2
UPSCALE = 3

TARGETS = {
    'hall-osteon': 'public/images/products/conmed/hall/page-076-xref-1104.webp',
    'g-ring': 'public/images/products/double-medical/g-ring/page-558-art-02.webp',
    'cfloop-button': 'public/images/products/double-medical/sports-medicine-catalogue/page-016-composite.webp',
}


def cutout(image: Image.Image, session) -> Image.Image:
    from rembg import remove
    big = image.resize((image.width * UPSCALE, image.height * UPSCALE), Image.LANCZOS)
    cut = remove(big, session=session, alpha_matting=True,
                 alpha_matting_foreground_threshold=250,
                 alpha_matting_background_threshold=12,
                 alpha_matting_erode_size=3)
    return cut.resize(image.size, Image.LANCZOS)


def on_site_grey(image: Image.Image) -> Image.Image:
    """Fallback: keep the photo, lose the hard white rectangle."""
    rgb = np.asarray(image.convert('RGB')).astype(np.int16)
    # How far each pixel is from white, used as a soft matte.
    distance = np.clip(255 - rgb.min(axis=2), 0, 255).astype(np.uint8)
    matte = Image.fromarray(distance).filter(ImageFilter.GaussianBlur(1.2)).point(lambda v: min(255, int(v * 4)))
    canvas = Image.new('RGB', image.size, SITE_GREY)
    canvas.paste(image.convert('RGB'), (0, 0), matte)
    out = canvas.convert('RGBA')
    # Feather the outer frame so the crop does not end on a hard edge.
    frame = Image.new('L', image.size, 0)
    inset = max(2, min(image.size) // 40)
    frame.paste(255, (inset, inset, image.width - inset, image.height - inset))
    out.putalpha(frame.filter(ImageFilter.GaussianBlur(inset / 1.6)))
    return out


def main() -> int:
    from rembg import new_session
    session = new_session('u2net')
    REVIEW.mkdir(parents=True, exist_ok=True)
    for name, relative in TARGETS.items():
        source = ROOT / relative
        image = Image.open(source)
        print(f'{name:<16} {image.size}')

        cut = cutout(image, session)
        cut.save(REVIEW / f'{name}-cutout.webp', 'WEBP', quality=92, method=6)
        opaque = int((np.asarray(cut)[:, :, 3] > 24).sum())
        print(f'   cutout   kept {opaque / (image.width * image.height) * 100:5.1f}% of the frame')

        grey = on_site_grey(image)
        grey.save(REVIEW / f'{name}-on-grey.webp', 'WEBP', quality=92, method=6)
        print(f'   on-grey  written')
    print(f'\nCandidates in {REVIEW.relative_to(ROOT)} — review before applying.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
