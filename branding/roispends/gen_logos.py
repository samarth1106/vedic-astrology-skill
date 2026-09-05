"""Generate three roispends logo concepts as self-contained SVGs.
Wordmark text is converted to outlines (paths), so no font is required to render."""
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
import os

OUT = os.path.dirname(os.path.abspath(__file__))
FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_REG  = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

NAVY  = "#0B1F3A"
GREEN = "#12B76A"
TEAL  = "#0E9F6E"
WHITE = "#FFFFFF"


import math
def arrow_head(ex, ey, dx, dy, length=16, half=10, fill=GREEN):
    """Triangle arrowhead whose tip is `length` beyond (ex,ey) along (dx,dy)."""
    n = math.hypot(dx, dy); dx, dy = dx / n, dy / n
    px, py = -dy, dx
    tipx, tipy = ex + dx * length, ey + dy * length
    b1x, b1y = ex - dx * 2 + px * half, ey - dy * 2 + py * half
    b2x, b2y = ex - dx * 2 - px * half, ey - dy * 2 - py * half
    return f'<path d="M{tipx:.1f} {tipy:.1f} L{b1x:.1f} {b1y:.1f} L{b2x:.1f} {b2y:.1f} Z" fill="{fill}"/>'

_fonts = {}
def font(path):
    if path not in _fonts:
        _fonts[path] = TTFont(path)
    return _fonts[path]

def text_paths(txt, x, y, size, path=FONT_BOLD, fill=NAVY, tracking=0.0):
    """Return (svg_group, width). Baseline at y. tracking in em units."""
    f = font(path)
    gs = f.getGlyphSet()
    cmap = f.getBestCmap()
    upm = f["head"].unitsPerEm
    s = size / upm
    parts = []
    cx = x
    for ch in txt:
        gname = cmap[ord(ch)]
        pen = SVGPathPen(gs)
        tpen = TransformPen(pen, (s, 0, 0, -s, cx, y))
        gs[gname].draw(tpen)
        d = pen.getCommands()
        if d:
            parts.append(f'<path d="{d}"/>')
        cx += gs[gname].width * s + tracking * size
    g = f'<g fill="{fill}">' + "".join(parts) + "</g>"
    return g, cx - x

def text_width(txt, size, path=FONT_BOLD, tracking=0.0):
    return text_paths(txt, 0, 0, size, path, tracking=tracking)[1]

def svg(w, h, body, name, bg=None):
    bgrect = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    doc = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="roispends logo">\n'
           f'<title>roispends</title>\n{bgrect}\n{body}\n</svg>\n')
    with open(os.path.join(OUT, name), "w") as fh:
        fh.write(doc)
    print("wrote", name)

# ---------- Concept 1: Growth-bars mark + horizontal wordmark ----------
def concept1(dark=False):
    fg_txt = WHITE if dark else NAVY
    size = 84
    tr = -0.02
    w_roi = text_width("roi", size, tracking=tr)
    w_sp  = text_width("spends", size, tracking=tr)
    mark_w = 110
    gap = 28
    total_w = mark_w + gap + w_roi + w_sp
    pad = 40
    W = total_w + 2 * pad
    H = 190
    cy = H / 2
    # Mark: rounded square, three rising bars, arrow on top
    mx, my = pad, cy - mark_w / 2
    mark = f'''<g transform="translate({mx},{my})">
  <rect width="{mark_w}" height="{mark_w}" rx="24" fill="{NAVY}"/>
  <rect x="22" y="62" width="14" height="26" rx="3" fill="{WHITE}" opacity="0.55"/>
  <rect x="44" y="48" width="14" height="40" rx="3" fill="{WHITE}" opacity="0.75"/>
  <rect x="66" y="34" width="14" height="54" rx="3" fill="{WHITE}"/>
  <path d="M24 44 L52 30 L68 38 L92 20" fill="none" stroke="{GREEN}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M78 18 L94 18 L94 34 Z" fill="{GREEN}"/>
</g>'''
    baseline = cy + size * 0.36
    tx = mx + mark_w + gap
    g1, _ = text_paths("roi", tx, baseline, size, fill=GREEN, tracking=tr)
    g2, _ = text_paths("spends", tx + w_roi, baseline, size, fill=fg_txt, tracking=tr)
    svg(round(W), H, mark + g1 + g2, "roispends-logo-1-growth-mark" + ("-dark" if dark else "") + ".svg",
        bg=NAVY if dark else None)

# ---------- Concept 2: Circular "R" monogram + stacked wordmark ----------
def concept2(dark=False):
    fg_txt = WHITE if dark else NAVY
    W, H = 360, 400
    cx = W / 2
    r = 92
    cy = 40 + r
    # Monogram: R built from Liberation Bold, with upward arrow swoosh
    rsize = 118
    rw = text_width("R", rsize)
    rg, _ = text_paths("R", cx - rw / 2 - 6, cy + rsize * 0.36, rsize, fill=WHITE)
    mark = f'''<circle cx="{cx}" cy="{cy}" r="{r}" fill="{NAVY}"/>
<circle cx="{cx}" cy="{cy}" r="{r-9}" fill="none" stroke="{GREEN}" stroke-width="3" opacity="0.9"/>
{rg}
<path d="M{cx+18} {cy+38} Q{cx+46} {cy+30} {cx+56} {cy+2}" fill="none" stroke="{GREEN}" stroke-width="9" stroke-linecap="round"/>
{arrow_head(cx+56, cy+2, 10, -28, length=15, half=10)}'''
    size = 62
    tr = -0.015
    w_roi = text_width("roi", size, tracking=tr)
    w_sp  = text_width("spends", size, tracking=tr)
    tx = cx - (w_roi + w_sp) / 2
    baseline = cy + r + 78
    g1, _ = text_paths("roi", tx, baseline, size, fill=GREEN, tracking=tr)
    g2, _ = text_paths("spends", tx + w_roi, baseline, size, fill=fg_txt, tracking=tr)
    # tagline: domain, small caps-ish regular
    tsize = 20
    dom = "roispends.com"
    dw = text_width(dom, tsize, path=FONT_REG, tracking=0.12)
    g3, _ = text_paths(dom, cx - dw / 2, baseline + 42, tsize, path=FONT_REG,
                       fill=("#9FB3C8" if dark else "#5B6B7F"), tracking=0.12)
    svg(W, H, mark + g1 + g2 + g3, "roispends-logo-2-monogram-stacked" + ("-dark" if dark else "") + ".svg",
        bg=NAVY if dark else None)

# ---------- Concept 3: Typographic wordmark, arrow replaces the dot of "i" ----------
def concept3(dark=False):
    fg_txt = WHITE if dark else NAVY
    size = 96
    tr = -0.025
    w_ro = text_width("ro", size, tracking=tr)
    w_i  = text_width("i", size, tracking=tr)
    w_sp = text_width("spends", size, tracking=tr)
    pad = 40
    W = w_ro + w_i + w_sp + 2 * pad
    H = 180
    baseline = H / 2 + size * 0.36
    x0 = pad
    g_ro, _ = text_paths("ro", x0, baseline, size, fill=GREEN, tracking=tr)
    # dotless i: draw only the stem by using glyph "dotlessi" if present, else "i" with cover
    f = font(FONT_BOLD); cmap = f.getBestCmap()
    i_txt = "ı" if 0x131 in cmap else "i"
    g_i, _ = text_paths(i_txt, x0 + w_ro, baseline, size, fill=GREEN, tracking=tr)
    g_sp, _ = text_paths("spends", x0 + w_ro + w_i, baseline, size, fill=fg_txt, tracking=tr)
    # arrow replacing i-dot: rising arrow above the stem
    ix = x0 + w_ro + w_i / 2
    top = baseline - size * 0.72
    ax0, ay0 = ix - 20, top + 12
    ax1, ay1 = ix + 4, top - 10
    arrow = (f'<path d="M{ax0} {ay0} L{ax1} {ay1}" fill="none" stroke="{GREEN}" stroke-width="9" stroke-linecap="round"/>'
             + arrow_head(ax1, ay1, ax1 - ax0, ay1 - ay0, length=14, half=11))
    # underline accent bar under "spends"
    ux = x0 + w_ro + w_i
    bar = f'<rect x="{ux}" y="{baseline + 22}" width="{w_sp}" height="6" rx="3" fill="{GREEN}" opacity="0.9"/>'
    svg(round(W), H, g_ro + g_i + g_sp + arrow + bar, "roispends-logo-3-wordmark" + ("-dark" if dark else "") + ".svg",
        bg=NAVY if dark else None)

for fn in (concept1, concept2, concept3):
    fn(False)
    fn(True)
