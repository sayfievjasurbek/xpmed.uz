#!/usr/bin/env python3
"""Normalise XPMED Academy photographs and logos for the /academy/ page.

Sources live in content/academy/ (see the README there). Photographs are
resized and saved as WebP; club and partner logos get the same white-keying as
the client logos, so a scan on white becomes a transparent mark. Everything is
optional: whatever is present is converted, whatever is absent falls back in
src/academy-media.mjs.

Usage: .venv-catalog/bin/python scripts/prepare-academy-assets.py
"""
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'content/academy'
TARGET = ROOT / 'public/images/academy'
PHOTO_WIDTH = 1600            # wide enough for the hero on a 2x display
LOGO_BOX = (420, 200)         # club and partner marks are contained in this
SUFFIXES = ('.jpg', '.jpeg', '.png', '.webp')
WHITE = 243                   # a pixel at or above this on every channel is "white"


def background_alpha(rgb: np.ndarray) -> np.ndarray:
    """Border-connected white becomes transparent, enclosed white is kept.

    The same keying prepare-brand-assets.py uses; that file's name has hyphens
    in it, so it cannot be imported, and eight lines are not worth a shim.
    """
    near_white = (rgb >= WHITE).all(axis=2)
    labels, count = ndimage.label(near_white)
    if count == 0:
        return np.full(rgb.shape[:2], 255, np.uint8)
    border = set(labels[0, :]) | set(labels[-1, :]) | set(labels[:, 0]) | set(labels[:, -1])
    border.discard(0)
    return np.where(np.isin(labels, list(border)), 0, 255).astype(np.uint8)


def photograph(source: Path, target: Path) -> str:
    image = Image.open(source).convert('RGB')
    scaled = image.copy()
    scaled.thumbnail((PHOTO_WIDTH, PHOTO_WIDTH), Image.LANCZOS)
    target.parent.mkdir(parents=True, exist_ok=True)
    scaled.save(target, 'WEBP', quality=86, method=6)
    return f'{image.width}x{image.height} -> {scaled.width}x{scaled.height}, {target.stat().st_size // 1024} KB'


def logo(source: Path, target: Path) -> str:
    image = Image.open(source).convert('RGBA')
    flat = Image.new('RGB', image.size, (255, 255, 255))
    flat.paste(image, (0, 0), image)
    rgba = Image.fromarray(np.dstack([np.asarray(flat), background_alpha(np.asarray(flat))]), 'RGBA')
    box = rgba.getbbox()
    if box:
        rgba = rgba.crop(box)
    rgba.thumbnail(LOGO_BOX, Image.LANCZOS)
    target.parent.mkdir(parents=True, exist_ok=True)
    rgba.save(target, 'WEBP', quality=94, method=6)
    return f'{image.width}x{image.height} -> {rgba.width}x{rgba.height}'


def convert(folder: Path, out: Path, handler) -> int:
    done = 0
    if not folder.is_dir():
        return 0
    for source in sorted(folder.iterdir()):
        if source.suffix.lower() not in SUFFIXES or not source.is_file():
            continue
        target = out / f'{source.stem}.webp'
        print(f'  {source.relative_to(SOURCE)!s:<36} {handler(source, target)}')
        done += 1
    return done


def main() -> int:
    if not SOURCE.is_dir():
        print(f'Nothing to do: {SOURCE} does not exist')
        return 0
    print('Photographs:')
    total = convert(SOURCE, TARGET, photograph)
    print('Club logos:')
    total += convert(SOURCE / 'clubs', TARGET / 'clubs', logo)
    print('Partner logos:')
    total += convert(SOURCE / 'partners', TARGET / 'partners', logo)
    print(f'\n{total} file(s) written to {TARGET.relative_to(ROOT)}' if total else '\nNo sources found yet.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
