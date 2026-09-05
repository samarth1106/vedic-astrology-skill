# roispends — sample logo concepts

Three sample logo concepts for **roispends** (roispends.com), prepared for company
registration paperwork. Each concept ships as a light-background SVG, a
dark-background SVG, and a 3x PNG export of each.

All wordmark text is converted to vector outlines, so the SVGs render identically
on any machine without the source font installed.

| # | File | Concept |
|---|------|---------|
| 1 | `roispends-logo-1-growth-mark.svg` | Rounded-square mark with rising bars and a growth arrow, next to the wordmark. Best general-purpose logo. |
| 2 | `roispends-logo-2-monogram-stacked.svg` | Circular "R" monogram with an upward arrow, wordmark and domain stacked below. Suits stamps, seals, and square placements. |
| 3 | `roispends-logo-3-wordmark.svg` | Pure typographic wordmark; the dot of the "i" becomes a growth arrow, with an accent underline. Cleanest for letterheads and invoices. |

`*-dark.svg` / `*-dark.png` are the same concepts on the navy background.
`roispends-logo-preview-sheet.png` shows all six side by side.

## Colours

| Role | Hex |
|------|-----|
| Navy (primary) | `#0B1F3A` |
| Green (accent, "roi") | `#12B76A` |
| White | `#FFFFFF` |
| Muted grey (domain line, light) | `#5B6B7F` |
| Muted grey (domain line, dark) | `#9FB3C8` |

## Typeface

Wordmark outlines are derived from Liberation Sans Bold (SIL Open Font Licence),
a metric-compatible equivalent of Arial/Helvetica Bold. Outlines are embedded as
paths, so no font licence obligations attach to the SVG files themselves.

## Regenerating

The generator script lives at `branding/roispends/gen_logos.py` and needs
`fonttools` (`pip install fonttools`). PNGs were exported with headless Chromium.
