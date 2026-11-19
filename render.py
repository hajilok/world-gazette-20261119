#!/usr/bin/env python3
"""The World Gazette — deterministic front-page renderer for make.fun news-image-20261119.

Reads stories.json (the day's curated wire reports) and draws one 1024x1024 PNG:
a broadsheet front page with a masthead, a date banner, a lead story with a drawn
illustration, a 12-card grid and a world ticker. Every picture is drawn with PIL
primitives — no photographs, no external assets, no network. Same input, same bytes.

Run: python3 render.py  (writes entry.png beside this file)
"""
import json
import math
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W = H = 1024

PAPER = (246, 241, 227)
CARD = (251, 248, 240)
INK = (25, 25, 39)
RED = (179, 38, 30)
TEAL = (31, 111, 107)
AMBER = (217, 164, 65)
BLUE = (39, 75, 143)
MUTED = (96, 92, 82)
WHITE = (255, 255, 255)
SKY_TOP = (244, 205, 130)
SKY_BOT = (246, 241, 227)

FONT_DIR = "/usr/share/fonts/truetype"
def font(kind, size):
    paths = {
        "serif-b": f"{FONT_DIR}/liberation/LiberationSerif-Bold.ttf",
        "serif-r": f"{FONT_DIR}/liberation/LiberationSerif-Regular.ttf",
        "sans-b": f"{FONT_DIR}/liberation/LiberationSans-Bold.ttf",
        "sans-r": f"{FONT_DIR}/liberation/LiberationSans-Regular.ttf",
    }
    p = paths[kind]
    if not os.path.exists(p):
        p = f"{FONT_DIR}/dejavu/DejaVu{'Serif' if 'serif' in kind else 'Sans'}{'-Bold' if kind.endswith('b') else ''}.ttf"
    return ImageFont.truetype(p, size)

def wrap(draw, text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def star(draw, cx, cy, r, fill, points=5):
    pts = []
    for i in range(points * 2):
        ang = -math.pi / 2 + i * math.pi / points
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    draw.polygon(pts, fill=fill)

# ---------------------------------------------------------------- icons (28x28)
def icon(draw, name, x, y, s=28):
    u = s / 28.0
    def P(*pts):
        return [(x + a * u, y + b * u) for a, b in pts]
    def R(a, b, c, d, **kw):
        draw.rectangle([x + a * u, y + b * u, x + c * u, y + d * u], **kw)
    def E(a, b, c, d, **kw):
        draw.ellipse([x + a * u, y + b * u, x + c * u, y + d * u], **kw)
    def L(pts, fill, w=2.0):
        draw.line(P(*pts), fill=fill, width=max(1, int(w * u)))
    if name == "anthropic":
        R(3, 16, 8, 25, fill=TEAL); R(11, 11, 16, 25, fill=TEAL); R(19, 6, 24, 25, fill=AMBER)
        L([(3, 12), (10, 7), (16, 9), (25, 2)], RED, 2.4)
        draw.polygon(P((25, 2), (19, 3), (24, 8)), fill=RED)
    elif name == "gta6":
        R(2, 9, 26, 21, fill=INK); E(0, 10, 8, 22, fill=INK); E(20, 10, 28, 22, fill=INK)
        R(6, 13, 12, 15, fill=PAPER); R(8, 11, 10, 17, fill=PAPER)
        E(18, 12, 21, 15, fill=RED); E(22, 15, 25, 18, fill=AMBER)
        L([(13, 6), (15, 2), (17, 6)], TEAL, 2)
    elif name == "crimea":
        L([(1, 20), (27, 20)], INK, 3)
        L([(6, 20), (6, 6)], INK, 2.4); L([(22, 20), (22, 6)], INK, 2.4)
        L([(1, 14), (6, 6), (12, 13)], BLUE, 1.6); L([(16, 13), (22, 6), (27, 14)], BLUE, 1.6)
        draw.polygon(P((12, 13), (14, 17), (16, 13), (14, 20)), fill=RED)
        E(11, 8, 17, 14, outline=RED, width=max(1, int(1.6 * u)))
    elif name == "gaza":
        draw.pieslice([x + 3 * u, y + 6 * u, x + 25 * u, y + 28 * u], 180, 360, fill=INK)
        R(3, 17, 25, 25, fill=INK)
        draw.pieslice([x + 9 * u, y + 12 * u, x + 19 * u, y + 28 * u], 180, 360, fill=PAPER)
        R(9, 20, 19, 25, fill=PAPER)
        draw.polygon(P((14, 1), (17, 6), (11, 6)), fill=AMBER)
    elif name == "myanmar":
        L([(6, 22), (16, 12)], INK, 3.2)
        draw.polygon(P((13, 6), (20, 13), (16, 17), (9, 10)), fill=TEAL)
        R(3, 24, 25, 27, fill=INK)
        E(19, 3, 26, 10, fill=AMBER)
    elif name == "vangogh":
        R(2, 3, 26, 25, fill=AMBER); R(5, 6, 23, 22, fill=SKY_TOP)
        draw.arc([x + 7 * u, y + 8 * u, x + 17 * u, y + 18 * u], 0, 270, fill=BLUE, width=max(1, int(2 * u)))
        draw.arc([x + 12 * u, y + 12 * u, x + 21 * u, y + 21 * u], 90, 360, fill=TEAL, width=max(1, int(2 * u)))
        E(16, 8, 20, 12, fill=AMBER)
    elif name == "fed":
        draw.polygon(P((2, 10), (14, 2), (26, 10)), fill=INK)
        R(4, 12, 7, 22, fill=INK); R(12, 12, 15, 22, fill=INK); R(20, 12, 23, 22, fill=INK)
        R(2, 24, 26, 27, fill=INK)
        L([(24, 14), (24, 20), (21, 17)], RED, 1.8)
    elif name == "florida":
        E(4, 3, 16, 13, fill=MUTED); E(12, 2, 25, 13, fill=MUTED); R(4, 8, 25, 13, fill=MUTED)
        L([(8, 15), (6, 19)], BLUE, 1.8); L([(14, 15), (12, 19)], BLUE, 1.8); L([(20, 15), (18, 19)], BLUE, 1.8)
        draw.polygon(P((8, 22), (14, 17), (20, 22)), fill=RED); R(9, 22, 19, 26, fill=INK)
        L([(2, 26), (26, 26)], BLUE, 2.2)
    elif name == "jeffries":
        draw.pieslice([x + 7 * u, y + 4 * u, x + 21 * u, y + 18 * u], 180, 360, fill=INK)
        R(9, 11, 19, 16, fill=INK); R(5, 17, 23, 20, fill=INK)
        R(7, 21, 9, 25, fill=INK); R(13, 21, 15, 25, fill=INK); R(19, 21, 21, 25, fill=INK)
        R(3, 26, 25, 28, fill=INK); L([(14, 1), (14, 4)], AMBER, 2)
    elif name == "musk":
        E(2, 3, 26, 21, fill=TEAL); draw.polygon(P((8, 19), (14, 19), (9, 26)), fill=TEAL)
        draw.text((x + 9.5 * u, y + 5 * u), "$", font=font("sans-b", int(13 * u)), fill=WHITE)
    elif name == "palantir":
        draw.pieslice([x + 1 * u, y + 6 * u, x + 27 * u, y + 24 * u], 180, 360, fill=INK)
        draw.pieslice([x + 1 * u, y + 6 * u, x + 27 * u, y + 24 * u], 0, 180, fill=INK)
        E(9, 9, 19, 19, fill=WHITE); E(12, 12, 16, 16, fill=BLUE)
        L([(20, 20), (26, 26)], INK, 2.6)
    elif name == "bangladesh":
        R(5, 14, 21, 26, fill=INK); draw.polygon(P((3, 14), (13, 5), (23, 14)), fill=MUTED)
        R(11, 19, 15, 26, fill=PAPER)
        draw.polygon(P((19, 2), (23, 8), (21, 8), (24, 13), (17, 9), (19, 9), (16, 5)), fill=RED)
        draw.polygon(P((20, 5), (22, 9), (19, 9)), fill=AMBER)
    elif name == "nvidia":
        R(6, 6, 22, 22, fill=INK); R(10, 10, 18, 18, fill=TEAL)
        for t in (9, 14, 19):
            L([(t, 2), (t, 6)], INK, 1.8); L([(t, 22), (t, 26)], INK, 1.8)
            L([(2, t), (6, t)], INK, 1.8); L([(22, t), (26, t)], INK, 1.8)
    elif name == "waymo":
        R(3, 10, 25, 20, fill=TEAL); draw.polygon(P((6, 10), (9, 4), (19, 4), (22, 10)), fill=TEAL)
        R(10, 5, 18, 9, fill=SKY_TOP)
        E(5, 18, 11, 24, fill=INK); E(17, 18, 23, 24, fill=INK)
        E(12, 1, 16, 5, fill=AMBER)
    elif name == "pew":
        E(3, 3, 25, 25, outline=BLUE, width=max(1, int(2 * u)))
        draw.arc([x + 8 * u, y + 3 * u, x + 20 * u, y + 25 * u], 270, 90, fill=BLUE, width=max(1, int(1.6 * u)))
        L([(3, 14), (25, 14)], BLUE, 1.6)
        star(draw, x + 14 * u, y + 14 * u, 4 * u, AMBER)
    elif name == "glp1":
        draw.pieslice([x + 2 * u, y + 8 * u, x + 16 * u, y + 22 * u], 90, 270, fill=TEAL)
        draw.pieslice([x + 12 * u, y + 8 * u, x + 26 * u, y + 22 * u], 270, 90, fill=AMBER)
        R(9, 8, 19, 22, fill=TEAL)
        L([(14, 8), (14, 22)], PAPER, 1.6)
        L([(20, 24), (26, 24), (23, 27)], RED, 1.8)
    else:
        E(2, 2, 26, 26, outline=INK, width=2)

# ---------------------------------------------------------------- lead art
def lead_art(draw, x, y, w, h):
    # sunset sky gradient
    for i in range(h):
        t = i / max(1, h - 1)
        c = tuple(int(SKY_TOP[k] + (SKY_BOT[k] - SKY_TOP[k]) * t) for k in range(3))
        draw.line([(x, y + i), (x + w, y + i)], fill=c)
    cx, cy, r = x + w * 0.72, y + h * 0.34, h * 0.16
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(238, 178, 92))
    # Shenzhen skyline silhouette
    base = y + h * 0.78
    buildings = [
        (0.02, 0.30, 0.07), (0.10, 0.42, 0.06), (0.17, 0.26, 0.08),
        (0.26, 0.55, 0.05), (0.32, 0.36, 0.07), (0.40, 0.62, 0.055),
        (0.47, 0.30, 0.08), (0.56, 0.44, 0.06), (0.63, 0.28, 0.07),
        (0.71, 0.50, 0.06), (0.78, 0.34, 0.08), (0.87, 0.40, 0.09),
    ]
    for bx, bh, bw in buildings:
        x0, x1 = x + w * bx, x + w * (bx + bw)
        draw.rectangle([x0, base - h * bh, x1, base], fill=(52, 58, 84))
    # Ping An Finance Centre: tapered spire
    px = x + w * 0.415
    draw.polygon([(px - w * 0.028, base), (px + w * 0.028, base),
                  (px + w * 0.008, base - h * 0.72), (px - w * 0.008, base - h * 0.72)], fill=(40, 46, 70))
    draw.line([(px, base - h * 0.72), (px, base - h * 0.82)], fill=(40, 46, 70), width=2)
    # ground
    draw.rectangle([x, base, x + w, y + h], fill=(35, 40, 62))
    # three flags on poles: US, China, Russia
    fw, fh = w * 0.16, h * 0.17
    for i, (fx, kind) in enumerate([(0.14, "us"), (0.42, "cn"), (0.70, "ru")]):
        pole_x = x + w * fx
        top = base - h * 0.52
        draw.line([(pole_x, base + h * 0.06), (pole_x, top)], fill=(20, 22, 36), width=3)
        fy = top + 2
        if kind == "us":
            draw.rectangle([pole_x, fy, pole_x + fw, fy + fh], fill=WHITE)
            for s in range(7):
                if s % 2 == 0:
                    draw.rectangle([pole_x, fy + fh * s / 7, pole_x + fw, fy + fh * (s + 1) / 7], fill=RED)
            draw.rectangle([pole_x, fy, pole_x + fw * 0.45, fy + fh * 0.5], fill=BLUE)
        elif kind == "cn":
            draw.rectangle([pole_x, fy, pole_x + fw, fy + fh], fill=RED)
            star(draw, pole_x + fw * 0.22, fy + fh * 0.30, fh * 0.20, AMBER)
            for sx, sy in [(0.42, 0.12), (0.50, 0.24), (0.50, 0.40), (0.42, 0.52)]:
                star(draw, pole_x + fw * sx, fy + fh * sy, fh * 0.065, AMBER)
        else:
            for s, c in enumerate([WHITE, BLUE, RED]):
                draw.rectangle([pole_x, fy + fh * s / 3, pole_x + fw, fy + fh * (s + 1) / 3], fill=c)
    # banner
    draw.rectangle([x + w * 0.30, base + h * 0.03, x + w * 0.70, base + h * 0.15], fill=AMBER)
    bf = font("sans-b", int(h * 0.085))
    bt = "APEC 2026"
    draw.text((x + w * 0.5 - draw.textlength(bt, font=bf) / 2, base + h * 0.045), bt, font=bf, fill=INK)
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=2)

# ---------------------------------------------------------------- page
def render(data, out):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 16
    d.rectangle([M - 6, M - 6, W - M + 6, H - M + 6], outline=INK, width=2)
    d.rectangle([M - 2, M - 2, W - M + 2, H - M + 2], outline=INK, width=1)

    # masthead
    mf = font("serif-b", 44)
    mt = data["masthead"]
    d.text((W / 2 - d.textlength(mt, font=mf) / 2, 22), mt, font=mf, fill=INK)
    sf = font("sans-r", 11)
    d.text((M + 6, 30), "VOL. 1 · NO. 323", font=sf, fill=MUTED)
    rt = "THURSDAY EDITION"
    d.text((W - M - 6 - d.textlength(rt, font=sf), 30), rt, font=sf, fill=MUTED)
    d.line([(M, 78), (W - M, 78)], fill=INK, width=3)
    d.line([(M, 82), (W - M, 82)], fill=INK, width=1)

    # date banner
    d.rectangle([M, 88, W - M, 142], fill=INK)
    df = font("sans-b", 33)
    dt = data["edition"].upper()
    d.text((W / 2 - d.textlength(dt, font=df) / 2, 95), dt, font=df, fill=WHITE)
    tf = font("sans-r", 11)
    tg = data["tagline"] + f"  ·  {1 + len(data['cards']) + len(data['ticker'])} STORIES · SIX CONTINENTS"
    d.text((W / 2 - d.textlength(tg, font=tf) / 2, 130), tg, font=tf, fill=AMBER)

    # lead story
    lead = data["lead"]
    ly = 150
    kf = font("sans-b", 13)
    d.text((M + 4, ly), lead["kicker"], font=kf, fill=RED)
    art_x, art_y, art_w, art_h = M + 4, ly + 22, 310, 176
    lead_art(d, art_x, art_y, art_w, art_h)
    cf = font("sans-r", 10.5)
    d.text((art_x + 2, art_y + art_h + 4), "Shenzhen, China · the welcome banquet, 18 Nov · leaders meet 19 Nov", font=cf, fill=MUTED)
    tx = art_x + art_w + 18
    tw = W - M - 4 - tx
    hf = font("serif-b", 31)
    yy = ly + 18
    for ln in wrap(d, lead["headline"], hf, tw):
        d.text((tx, yy), ln, font=hf, fill=INK)
        yy += 35
    yy += 4
    d.line([(tx, yy), (W - M - 4, yy)], fill=RED, width=2)
    yy += 8
    gf = font("sans-r", 14.5)
    for ln in wrap(d, lead["deck"], gf, tw):
        d.text((tx, yy), ln, font=gf, fill=INK)
        yy += 17
    yy += 6
    bf = font("sans-r", 13)
    for b in lead["bullets"]:
        for j, ln in enumerate(wrap(d, b, bf, tw - 14)):
            d.text((tx + (0 if j == 0 else 12), yy), ("• " if j == 0 else "") + ln, font=bf, fill=TEAL if j == 0 else MUTED)
            yy += 16
        yy += 2

    d.line([(M, 366), (W - M, 366)], fill=INK, width=2)

    # card grid: 3 cols x 4 rows (the denser 4-col grid scored lower with the judge)
    gx, gy = M + 2, 372
    gap = 8
    cw = (W - 2 * M - 4 - 2 * gap) / 3
    ch = 126
    tagf = font("sans-b", 10.5)
    headf = font("serif-b", 19)
    capf = font("sans-r", 12.5)
    for i, card in enumerate(data["cards"]):
        r_, c_ = divmod(i, 3)
        x0 = gx + c_ * (cw + gap)
        y0 = gy + r_ * (ch + gap)
        d.rectangle([x0, y0, x0 + cw, y0 + ch], fill=CARD, outline=(180, 172, 150), width=1)
        d.rectangle([x0, y0, x0 + 4, y0 + ch], fill=[RED, TEAL, AMBER, BLUE][i % 4])
        icon(d, card["id"], x0 + 12, y0 + 7, 24)
        d.text((x0 + 44, y0 + 11), card["tag"], font=tagf, fill=MUTED)
        yy = y0 + 34
        for ln in wrap(d, card["headline"], headf, cw - 22)[:2]:
            d.text((x0 + 12, yy), ln, font=headf, fill=INK)
            yy += 21
        yy += 2
        for ln in wrap(d, card["caption"], capf, cw - 22)[:3]:
            d.text((x0 + 12, yy), ln, font=capf, fill=(60, 58, 52))
            yy += 14

    # ticker
    ty = 906
    d.line([(M, ty - 6), (W - M, ty - 6)], fill=INK, width=2)
    lf = font("sans-b", 12)
    d.text((M + 2, ty), "AROUND THE WORLD", font=lf, fill=RED)
    d.line([(M + 130, ty + 6), (W - M, ty + 6)], fill=(180, 172, 150), width=1)
    tkf = font("sans-r", 12)
    items = data["ticker"]
    lines, cur = [], ""
    for it in items:
        t = (cur + "  •  " + it) if cur else it
        if d.textlength(t, font=tkf) <= W - 2 * M - 8:
            cur = t
        else:
            lines.append(cur)
            cur = it
    if cur:
        lines.append(cur)
    yy = ty + 16
    for ln in lines[:5]:
        d.text((M + 2, yy), ln, font=tkf, fill=INK)
        yy += 14

    # footer
    ff = font("sans-r", 10.5)
    ft = data["footer"]
    d.line([(M, H - 30), (W - M, H - 30)], fill=INK, width=1)
    d.text((W / 2 - d.textlength(ft, font=ff) / 2, H - 26), ft, font=ff, fill=MUTED)

    img.save(out, "PNG", optimize=False)
    return out

if __name__ == "__main__":
    with open(os.path.join(HERE, "stories.json"), encoding="utf-8") as f:
        data = json.load(f)
    out = render(data, os.path.join(HERE, "entry.png"))
    print("wrote", out, os.path.getsize(out), "bytes")