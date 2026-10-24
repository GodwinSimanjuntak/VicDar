#!/usr/bin/env python3
"""Generate VicDar's drawn theme assets into overlay/.

- overlay/usr/share/backgrounds/vicdar/vicdar-contours.svg  (seeded contour wallpaper)
- overlay/usr/share/themes/VicDar/xfwm4/*                  (window frame: themerc + XPM)

Standard library only. Same seed, same output:  python3 tools/gen-theme-assets.py
"""
import math
import os
import random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = 3108  # change to draw a different terrain

# Palette (see DESIGN.md)
RAIL = "#1C1F21"      # title bars, rail
WINDOW = "#26292C"    # window ground, inactive title bars
RULE = "#3A4045"      # 1px rules, active
RULE_DIM = "#33383C"  # 1px rules, inactive
BONE = "#E9E6DF"      # primary text
GLYPH = "#C9C5BD"     # button glyphs, active
GLYPH_DIM = "#6B737A" # button glyphs, inactive
HOVER = "#33383C"
PRESS = "#3A4045"
ORANGE = "#FF6B1A"    # reserved: whatever is live
DANGER = "#E5534B"
DANGER_PRESS = "#C9443D"
FIELD = "#31373C"     # wallpaper ground
CONTOUR = "#383F44"
CONTOUR_INDEX = "#414950"


# ---------------------------------------------------------------- wallpaper

def value_noise(rng, cells_x, cells_y):
    grid = [[rng.random() for _ in range(cells_x + 2)] for _ in range(cells_y + 2)]

    def sample(u, v):  # u, v in lattice units
        x0, y0 = int(u), int(v)
        fx, fy = u - x0, v - y0
        sx, sy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
        a = grid[y0][x0] + (grid[y0][x0 + 1] - grid[y0][x0]) * sx
        b = grid[y0 + 1][x0] + (grid[y0 + 1][x0 + 1] - grid[y0 + 1][x0]) * sx
        return a + (b - a) * sy

    return sample


def height_field(w, h, step, seed):
    rng = random.Random(seed)
    octaves = []
    for i in range(4):  # a fifth octave makes the lines jagged
        cells = 3 * 2 ** i
        octaves.append((value_noise(rng, cells + 2, int(cells * h / w) + 3), cells, 0.45 ** i))
    nx, ny = w // step + 1, h // step + 1
    field = []
    for j in range(ny):
        row = []
        for i in range(nx):
            x, y = i / (nx - 1), j / (ny - 1)
            z = 0.0
            for noise, cells, amp in octaves:
                z += amp * noise(x * cells, y * cells * h / w)
            row.append(z)
        field.append(row)
    return field


def march(field, level, step):
    """Marching squares: return line segments where field == level."""
    segs = []
    ny, nx = len(field), len(field[0])
    for j in range(ny - 1):
        for i in range(nx - 1):
            c = [field[j][i], field[j][i + 1], field[j + 1][i + 1], field[j + 1][i]]
            idx = sum(1 << k for k in range(4) if c[k] > level)
            if idx in (0, 15):
                continue
            corners = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]

            def edge(a, b):
                # interpolate from the same corner whichever cell asks, so shared edges match exactly
                if (corners[a][1], corners[a][0]) > (corners[b][1], corners[b][0]):
                    a, b = b, a
                (xa, ya), (xb, yb) = corners[a], corners[b]
                t = (level - c[a]) / (c[b] - c[a])
                return ((xa + (xb - xa) * t) * step, (ya + (yb - ya) * t) * step)

            e = {0: lambda: edge(0, 1), 1: lambda: edge(1, 2), 2: lambda: edge(2, 3), 3: lambda: edge(3, 0)}
            table = {1: [(3, 0)], 2: [(0, 1)], 3: [(3, 1)], 4: [(1, 2)], 6: [(0, 2)], 7: [(3, 2)],
                     8: [(2, 3)], 9: [(0, 2)], 11: [(1, 2)], 12: [(1, 3)], 13: [(0, 1)], 14: [(3, 0)]}
            if idx in (5, 10):  # saddle: the cell centre decides which corners stay joined
                centre = sum(c) / 4 > level
                if idx == 5:
                    pairs = [(3, 2), (0, 1)] if centre else [(3, 0), (1, 2)]
                else:
                    pairs = [(3, 0), (1, 2)] if centre else [(0, 1), (2, 3)]
            else:
                pairs = table[idx]
            for a, b in pairs:
                segs.append((e[a](), e[b]()))
    return segs


def chain(segs):
    """Join segments into polylines by shared endpoints."""
    key = lambda p: (round(p[0], 3), round(p[1], 3))
    ends = {}
    for n, (a, b) in enumerate(segs):
        ends.setdefault(key(a), []).append((n, 0))
        ends.setdefault(key(b), []).append((n, 1))
    used = [False] * len(segs)
    lines = []
    for n in range(len(segs)):
        if used[n]:
            continue
        used[n] = True
        line = [segs[n][0], segs[n][1]]
        for forward in (True, False):
            while True:
                tip = line[-1] if forward else line[0]
                nxt = None
                for m, side in ends.get(key(tip), []):
                    if not used[m]:
                        nxt = (m, side)
                        break
                if nxt is None:
                    break
                m, side = nxt
                used[m] = True
                other = segs[m][1 - side]
                if forward:
                    line.append(other)
                else:
                    line.insert(0, other)
        lines.append(line)
    return lines


def chaikin(pts, rounds=2):
    for _ in range(rounds):
        out = [pts[0]]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            out += [(0.75 * x0 + 0.25 * x1, 0.75 * y0 + 0.25 * y1), (0.25 * x0 + 0.75 * x1, 0.25 * y0 + 0.75 * y1)]
        out.append(pts[-1])
        pts = out
    return pts


def simplify(pts, eps):
    """Ramer-Douglas-Peucker."""
    if len(pts) < 3:
        return pts
    (x0, y0), (x1, y1) = pts[0], pts[-1]
    dx, dy = x1 - x0, y1 - y0
    norm = math.hypot(dx, dy) or 1e-9
    far, idx = 0.0, 0
    for k in range(1, len(pts) - 1):
        d = abs(dy * pts[k][0] - dx * pts[k][1] + x1 * y0 - y1 * x0) / norm
        if d > far:
            far, idx = d, k
    if far <= eps:
        return [pts[0], pts[-1]]
    return simplify(pts[: idx + 1], eps)[:-1] + simplify(pts[idx:], eps)


def wallpaper():
    w, h, step = 1920, 1080, 8
    field = height_field(w, h, step, SEED)
    values = sorted(v for row in field for v in row)
    lo, hi = values[len(values) // 20], values[-len(values) // 20]
    levels = 26
    paths = {False: [], True: []}
    for k in range(1, levels):
        level = lo + (hi - lo) * k / levels
        for line in chain(march(field, level, step)):
            if len(line) < 6:
                continue
            pts = simplify(chaikin(line), 0.35)
            d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
            paths[k % 5 == 0].append(d)
    svg = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<!-- VicDar wallpaper, drawn by tools/gen-theme-assets.py (seed {SEED}). GPL-3.0. -->',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid slice">',
        f'<rect width="{w}" height="{h}" fill="{FIELD}"/>',
        f'<path fill="none" stroke="{CONTOUR}" stroke-width="1.1" stroke-linejoin="round" d="{" ".join(paths[False])}"/>',
        f'<path fill="none" stroke="{CONTOUR_INDEX}" stroke-width="1.7" stroke-linejoin="round" d="{" ".join(paths[True])}"/>',
        "</svg>",
    ]
    out = os.path.join(ROOT, "overlay/usr/share/backgrounds/vicdar/vicdar-contours.svg")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", newline="\n") as f:
        f.write("\n".join(svg) + "\n")
    return out, len(paths[False]) + len(paths[True])


# ------------------------------------------------------------- xfwm4 frame

TH = 28  # title bar height
BW = 2   # side and bottom border width


def hex2rgb(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


def mix(a, b, t):
    ra, rb = hex2rgb(a), hex2rgb(b)
    return "#%02X%02X%02X" % tuple(round(x + (y - x) * t) for x, y in zip(ra, rb))


def write_xpm(path, pixels):
    """pixels: rows of hex colours."""
    colours = sorted({c for row in pixels for c in row})
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    code = dict(zip(colours, chars))
    name = os.path.basename(path).replace("-", "_").replace(".", "_")
    lines = ["/* XPM */", "/* VicDar xfwm4 theme, drawn by tools/gen-theme-assets.py */",
             f"static char * {name}[] = {{", f'"{len(pixels[0])} {len(pixels)} {len(colours)} 1",']
    lines += [f'"{code[c]} c {c}",' for c in colours]
    lines += [f'"{"".join(code[c] for c in row)}",' for row in pixels]
    lines[-1] = lines[-1].rstrip(",")
    lines.append("};")
    with open(path, "w", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


def solid(w, h, c):
    return [[c] * w for _ in range(h)]


def seg_dist(px, py, x0, y0, x1, y1):
    dx, dy = x1 - x0, y1 - y0
    t = max(0.0, min(1.0, ((px - x0) * dx + (py - y0) * dy) / (dx * dx + dy * dy or 1e-9)))
    return math.hypot(px - (x0 + t * dx), py - (y0 + t * dy))


GLYPHS = {  # 28x28 boxes, centre (14, 14.5); (segments, stroke width)
    "close": ([(10, 10.5, 18, 18.5), (18, 10.5, 10, 18.5)], 1.6),
    "maximize": ([(10, 10.5, 18, 10.5), (18, 10.5, 18, 18.5), (18, 18.5, 10, 18.5), (10, 18.5, 10, 10.5)], 1.4),
    "maximize-toggled": ([(10, 12.5, 16, 12.5), (16, 12.5, 16, 18.5), (16, 18.5, 10, 18.5), (10, 18.5, 10, 12.5),
                          (12, 10.5, 18, 10.5), (18, 10.5, 18, 16.5)], 1.3),
    "hide": ([(10, 18, 18, 18)], 1.6),
    "menu": ([(10, 11, 18, 11), (10, 14.5, 18, 14.5), (10, 18, 18, 18)], 1.3),
    "shade": ([(10, 16.5, 14, 12.5), (14, 12.5, 18, 16.5)], 1.5),
    "shade-toggled": ([(10, 12.5, 14, 16.5), (14, 16.5, 18, 12.5)], 1.5),
    "stick": ([(14, 14.5, 14, 14.5)], 4.4),
    "stick-toggled": ([(11, 14.5, 17, 14.5), (14, 11.5, 14, 17.5)], 1.6),
}


def button(kind, bg, fg, rule, tag=False):
    segs, width = GLYPHS[kind]
    ss = 4
    rows = [[rule] * TH]
    for y in range(1, TH):
        row = []
        for x in range(TH):
            if tag and x < 4:  # xfwm clips the top-left corner to the border width, so the
                row.append(ORANGE)  # focused-window tag lives in the leftmost (menu) button
                continue
            hit = 0
            for sy in range(ss):
                for sx in range(ss):
                    px, py = x + (sx + 0.5) / ss, y + (sy + 0.5) / ss
                    if any(seg_dist(px, py, *s) <= width / 2 for s in segs):
                        hit += 1
            row.append(mix(bg, fg, round(hit / (ss * ss) * 6) / 6))
        rows.append(row)
    return rows


def frame():
    d = os.path.join(ROOT, "overlay/usr/share/themes/VicDar/xfwm4")
    os.makedirs(d, exist_ok=True)
    for state, bg, rule in (("active", RAIL, RULE), ("inactive", WINDOW, RULE_DIM)):
        # title strip pieces: 1px rule on top, title ground below
        for n in range(1, 6):
            write_xpm(f"{d}/title-{n}-{state}.xpm", [[rule]] + solid(1, TH - 1, bg))
        # top-left: the focused window wears the orange tag
        tl = [[rule] * 6]
        for _ in range(TH - 1):
            tl.append([rule] + ([ORANGE] * 4 if state == "active" else [bg] * 4) + [bg])
        write_xpm(f"{d}/top-left-{state}.xpm", tl)
        write_xpm(f"{d}/top-right-{state}.xpm", [[rule] * BW] + [[bg] * (BW - 1) + [rule] for _ in range(TH - 1)])
        write_xpm(f"{d}/left-{state}.xpm", [[rule] + [bg] * (BW - 1)])
        write_xpm(f"{d}/right-{state}.xpm", [[bg] * (BW - 1) + [rule]])
        write_xpm(f"{d}/bottom-{state}.xpm", [[bg]] * (BW - 1) + [[rule]])
        corner_l = [[rule] + [bg] * (BW - 1) for _ in range(BW - 1)] + [[rule] * BW]
        corner_r = [[bg] * (BW - 1) + [rule] for _ in range(BW - 1)] + [[rule] * BW]
        write_xpm(f"{d}/bottom-left-{state}.xpm", corner_l)
        write_xpm(f"{d}/bottom-right-{state}.xpm", corner_r)
    for kind in GLYPHS:
        hover_bg, press_bg, hover_fg = (DANGER, DANGER_PRESS, RAIL) if kind == "close" else (HOVER, PRESS, BONE)
        tag = kind == "menu"  # leftmost in the O|HMC layout set in xfwm4.xml
        write_xpm(f"{d}/{kind}-active.xpm", button(kind, RAIL, GLYPH, RULE, tag))
        write_xpm(f"{d}/{kind}-inactive.xpm", button(kind, WINDOW, GLYPH_DIM, RULE_DIM))
        write_xpm(f"{d}/{kind}-prelight.xpm", button(kind, hover_bg, hover_fg, RULE, tag))
        write_xpm(f"{d}/{kind}-pressed.xpm", button(kind, press_bg, hover_fg, RULE, tag))
    with open(f"{d}/themerc", "w", newline="\n") as f:
        f.write(
            "# VicDar xfwm4 theme, drawn by tools/gen-theme-assets.py\n"
            f"active_text_color={BONE}\n"
            "inactive_text_color=#8A9198\n"
            "title_shadow_active=false\n"
            "title_shadow_inactive=false\n"
            "full_width_title=true\n"
            "title_horizontal_offset=8\n"
            "title_vertical_offset_active=1\n"
            "title_vertical_offset_inactive=1\n"
            "button_offset=0\n"
            "button_spacing=0\n"
            "maximized_offset=0\n"
        )
    return d


if __name__ == "__main__":
    path, count = wallpaper()
    assert os.path.getsize(path) < 1_500_000, "wallpaper too heavy for old laptops"
    assert count > 40, "terrain came out flat; try another SEED"
    print(f"wallpaper: {path} ({count} contour lines, {os.path.getsize(path) // 1024} KB)")
    d = frame()
    xpms = [n for n in os.listdir(d) if n.endswith(".xpm")]
    assert len(xpms) == 12 * 2 + len(GLYPHS) * 4, len(xpms)  # 12 frame pieces per state
    print(f"xfwm4: {d} ({len(xpms)} XPM files + themerc)")
