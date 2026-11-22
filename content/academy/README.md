# XPMED Academy artwork

Drop the originals here, then run:

    .venv-catalog/bin/python scripts/prepare-academy-assets.py

The script writes `public/images/academy/`, which `build.mjs` copies into the
site. Any file that is missing simply falls back: a photograph to an existing
XPMED photograph, a club logo to the club's initials, a partner logo to the
partner's name set in type. The page builds either way, so these can arrive one
at a time.

## Photographs (`.jpg`, `.jpeg` or `.png`)

| File          | Where it appears                        | Falls back to |
| ------------- | --------------------------------------- | ------------- |
| `hero`        | hero background, behind the navy overlay | `operating-room.webp` |
| `about`       | portrait beside the About text          | `mission-clinicians.webp` |
| `course-1`    | upper photo in the cadaver-course block | `surgery-suite.webp` |
| `course-2`    | lower photo in the cadaver-course block | `hero-devices.webp` |
| `mission`     | gloves photo beside the purpose block   | `surgery-suite.webp` |

Landscape originals at 1600px wide or more; `about` and `mission` are cropped
to 4:5, so a portrait original suits them best.

## Logos (`.png`, transparent or on white)

    clubs/joints-club.png
    clubs/traumedy-club.png
    clubs/arthro-meet.png
    clubs/spinendos-club.png
    partners/bojin.png
    partners/bns-neo-science.png

A logo on white has that white keyed out, keeping any white the artwork
encloses. A logo on anything else - Bojin arrived as a white disc on black -
is keyed by colour instead, which keeps the coloured artwork and drops the
backing with it; a logo whose artwork is itself grey or black should
therefore be supplied on white. The club logos sit on the dark section, so
light artwork reads best.

Double Medical, CONMED, Synimed and SPINENDOS are not listed: the partner row
reuses the wordmarks the rest of the site already has.
