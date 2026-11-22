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
BLACK = 24                    # ... and at or below this, "black"


def background_alpha(rgb: np.ndarray) -> np.ndarray:
    """Border-connected flat background becomes transparent.

    prepare-brand-assets.py keys white only, because the client scans are on
    white. Partner logos arrive as whatever the partner had: Bojin came as a
    white disc on black, so plain white keying would have kept the black
    corners. Here white and black are treated as one background region, which
    also takes the disc with the corners it touches, and anything the artwork
    encloses is still kept.
    """
    flat = (rgb >= WHITE).all(axis=2) | (rgb <= BLACK).all(axis=2)
    labels, count = ndimage.label(flat)
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


def coloured_alpha(rgb: np.ndarray) -> np.ndarray:
    """Alpha from colourfulness: the artwork is coloured, the backing is not.

    For a logo that does not sit on plain white - Bojin arrived as a white
    disc on black - keying the background by colour cannot work: white keying
    leaves the disc, and taking white and black together still leaves the
    soft grey ring between them, so the mark ends up adrift in a pale circle.
    What the artwork has and the backing does not is chroma. The edge keeps a
    soft alpha because a half-blended pixel has half the chroma.
    """
    values = rgb.astype(np.int16)
    chroma = values.max(axis=2) - values.min(axis=2)
    return np.clip((chroma - 10) * 9, 0, 255).astype(np.uint8)


def border_is_white(rgb: np.ndarray) -> bool:
    edges = np.concatenate([rgb[0, :], rgb[-1, :], rgb[:, 0], rgb[:, -1]])
    return bool(((edges >= WHITE).all(axis=1)).mean() > 0.9)


def logo(source: Path, target: Path) -> str:
    image = Image.open(source).convert('RGBA')
    # A PNG's own transparency is flattened onto white, not onto the black
    # that convert('RGB') would leave behind.
    flat = Image.new('RGB', image.size, (255, 255, 255))
    flat.paste(image, (0, 0), image)
    array = np.asarray(flat)
    on_white = border_is_white(array)
    alpha = background_alpha(array) if on_white else coloured_alpha(array)
    rgba = Image.fromarray(np.dstack([array, alpha]), 'RGBA')
    box = rgba.getbbox()
    if box:
        rgba = rgba.crop(box)
    rgba.thumbnail(LOGO_BOX, Image.LANCZOS)
    target.parent.mkdir(parents=True, exist_ok=True)
    rgba.save(target, 'WEBP', quality=94, method=6)
    transparent = int((np.asarray(rgba)[:, :, 3] == 0).sum())
    keyed = 'white keyed' if on_white else 'chroma keyed'
    return f'{image.width}x{image.height} -> {rgba.width}x{rgba.height}, {keyed}, {transparent / (rgba.width * rgba.height) * 100:.0f}% transparent'


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
