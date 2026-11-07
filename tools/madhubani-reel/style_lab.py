"""Same 4-second moment (Hanuman lifts the Sanjeevani mountain) in 10 styles. python3 styles.py <style|all>"""
import sys, math, random, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops, ImageOps
import reel_template as D, madhu as M
from madhu import Pen, INK, PAPER, RED, YEL, ORA, GRN, LGRN, BLU, SKY, PINK, WHITE
W, H, FPS, DUR = 1080, 1920, 30, 4.0
ease, eout, put = D.ease, D.eout, D.put
GF = D.GF
def F(name, size):
    path = dict(yatra=GF + "yatraone/YatraOne-Regular.ttf", rozha=GF + "rozhaone/RozhaOne-Regular.ttf", mukta=GF + "mukta/Mukta-ExtraBold.ttf",
                noto=GF + "notoserifdevanagari/NotoSerifDevanagari[wdth,wght].ttf", tiro=GF + "tirodevanagarihindi/TiroDevanagariHindi-Italic.ttf")[name]
    f = ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)
    if name == "noto":
        try: f.set_variation_by_axes([100, 700])
        except Exception: pass
    return f
def text_c(d, y, txt, f, fill, stroke=0, sfill=None):
    tw = f.getlength(txt, language="hi"); d.text((W / 2 - tw / 2, y), txt, font=f, fill=fill, language="hi", stroke_width=stroke, stroke_fill=sfill)

# ---- shared sprites & motion
HANU = M.figure("hanuman", 1, 1100); HANU = HANU.resize((560, int(HANU.height * 560 / HANU.width)), Image.LANCZOS)
import sanjeevani_madhubani as sanj_m
MT = sanj_m.mountain(1.15, 0.0)
def lift(t): return ease((t - 0.7) / 2.3)
def place(t, hn, mt):
    l = lift(t); hb = 1640 - 60 * l
    return (540, 1640 - 20 + (-(hn.height * 0.86) + 20) * l), (540, hb)
def mask(im): return im.getchannel("A")
def solid(im, col):
    o = Image.new("RGBA", im.size, col + (255,)); o.putalpha(mask(im)); return o
def compose(c, hn, mt, t):
    (mx, my), (hx, hy) = place(t, hn, mt); put(c, mt, mx, my); put(c, hn, hx, hy); return c

def label(c, n, name):
    d = ImageDraw.Draw(c); f = F("mukta", 44); t = f"{n} · {name}"; tw = f.getlength(t)
    d.rounded_rectangle([W / 2 - tw / 2 - 30, 60, W / 2 + tw / 2 + 30, 130], 35, fill=(0, 0, 0, 170)); d.text((W / 2 - tw / 2, 66), t, font=f, fill=(255, 255, 255))

def outline(im, px, col=INK):
    m = mask(im).filter(ImageFilter.MaxFilter(px * 2 + 1))
    o = Image.new("RGBA", im.size, col + (0,)); o.putalpha(m); o.alpha_composite(im); return o
def quantize(im, pal):
    a = np.asarray(im).astype(float); rgb = a[..., :3]; P = np.array(pal, float)
    idx = ((rgb[..., None, :] - P[None, None]) ** 2).sum(-1).argmin(-1)
    out = np.concatenate([P[idx], a[..., 3:]], -1).astype(np.uint8); return Image.fromarray(out, "RGBA")
def pad(im, p=24):
    o = Image.new("RGBA", (im.width + 2 * p, im.height + 2 * p), (0, 0, 0, 0)); o.paste(im, (p, p)); return o

# ---------------------------------------------------------------- styles
def s_madhubani(t): return Image.fromarray(sanj_m.frame(16.0 + t)).convert("RGBA")

# Pattachitra: deep red ground, ochre/white/black palette, heavy black line, leaf-scroll border
PAT_PAL = [(180, 30, 25), (225, 160, 40), (245, 235, 210), (25, 18, 15), (30, 110, 70), (40, 60, 140), (235, 120, 40)]
P_H = outline(quantize(pad(HANU), PAT_PAL), 6); P_M = outline(quantize(pad(MT), PAT_PAL), 6)
def pat_border():
    p = Pen(W, H, 0, 0, 1.0)
    p.d.rectangle([0, 0, W * 2, H * 2], fill=(25, 18, 15, 255))
    p.d.rectangle([60, 60, W * 2 - 60, H * 2 - 60], fill=(225, 160, 40, 255)); p.d.rectangle([120, 120, W * 2 - 120, H * 2 - 120], fill=(180, 30, 25, 255))
    for x in range(140, W * 2 - 100, 90):
        for y in (90, H * 2 - 90): p.d.ellipse([x - 22, y - 12, x + 22, y + 12], fill=(30, 110, 70, 255), outline=(25, 18, 15, 255), width=4)
    for y in range(140, H * 2 - 100, 90):
        for x in (90, W * 2 - 90): p.d.ellipse([x - 12, y - 22, x + 12, y + 22], fill=(30, 110, 70, 255), outline=(25, 18, 15, 255), width=4)
    p.d.rectangle([150, 150, W * 2 - 150, H * 2 - 150], outline=(245, 235, 210, 255), width=8)
    r = random.Random(2)
    for _ in range(26):   # floral motifs in the ground
        x, y = r.uniform(220, W * 2 - 220), r.uniform(1000, 1700)
        for k in range(5): a = k * 1.2566; p.d.ellipse([x + 26 * math.cos(a) - 12, y + 26 * math.sin(a) - 12, x + 26 * math.cos(a) + 12, y + 26 * math.sin(a) + 12], fill=(245, 235, 210, 255), outline=(25, 18, 15, 255), width=3)
    return p.done().resize((W, H), Image.LANCZOS)
PAT_BG = pat_border()
def s_pattachitra(t):
    c = PAT_BG.copy(); compose(c, P_H, P_M, t)
    d = ImageDraw.Draw(c); text_c(d, 190, "पूरा पर्वत उठा लिया!", F("yatra", 92), (245, 235, 210), 4, (25, 18, 15)); return c

# Kalamkari / Pichwai: indigo cloth, gold lotus pond, earth-tone figure with gold line
def tint(im, col, k=0.55):
    a = np.asarray(im).astype(float); g = a[..., :3].mean(-1, keepdims=True)
    rgb = (a[..., :3] * (1 - k) + g / 255 * np.array(col) * k); return Image.fromarray(np.concatenate([rgb, a[..., 3:]], -1).astype(np.uint8), "RGBA")
K_H = outline(tint(pad(HANU), (235, 170, 90), 0.5), 3, (230, 190, 90)); K_M = outline(tint(pad(MT), (120, 160, 110), 0.5), 3, (230, 190, 90))
def kal_bg():
    c = Image.new("RGBA", (W, H), (22, 30, 78, 255)); p = Pen(W, H, 0, 0, 1.0)
    GOLD = (225, 185, 90)
    for x in range(40, W, 80):
        p.line([(x, 0), (x, H)], (32, 42, 96), 2)
    for y in range(1500, 1860, 90):
        for x in range(90 + (y // 90 % 2) * 60, 1000, 140):
            for k in range(6):
                a = math.pi + k * math.pi / 5; p.shape([(x, y), (x + 34 * math.cos(a - 0.25), y + 34 * math.sin(a - 0.25)), (x + 60 * math.cos(a), y + 60 * math.sin(a)), (x + 34 * math.cos(a + 0.25), y + 34 * math.sin(a + 0.25))], (230, 140, 150), None, inner=False, width=2)
            p.circle(x, y, 12, GOLD, outline=False)
    for x in range(60, W, 60): p.circle(x, 60, 14, GOLD, outline=False); p.circle(x, H - 60, 14, GOLD, outline=False)
    r = random.Random(1)
    for _ in range(40): p.circle(r.uniform(80, 1000), r.uniform(200, 900), r.uniform(3, 7), GOLD, outline=False)
    c.alpha_composite(p.done()); return c
K_BG = kal_bg()
def s_kalamkari(t):
    c = K_BG.copy(); compose(c, K_H, K_M, t)
    d = ImageDraw.Draw(c); text_c(d, 180, "संजीवनी पर्वत", F("yatra", 110), (225, 185, 90)); return c

# Gond: cream ground, bright flat fills packed with dots and dashes
def gondify(im, cols):
    q = quantize(im, [(240, 120, 40), (220, 50, 60), (40, 150, 200), (60, 160, 80), (250, 200, 40), (30, 20, 20)])
    p = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(p); r = random.Random(3); a = np.asarray(q)
    for y in range(6, im.height - 6, 14):
        for x in range(6 + (y // 14 % 2) * 7, im.width - 6, 14):
            if a[y, x, 3] > 200 and a[y, x, :3].sum() > 120:
                if (x // 40 + y // 40) % 2: d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(250, 245, 230, 255))
                else: d.line([(x - 5, y + 3), (x + 5, y - 3)], fill=(30, 20, 20, 255), width=3)
    q.alpha_composite(p); return outline(q, 4, (30, 20, 20))
G_H = gondify(pad(HANU), None); G_M = gondify(pad(MT), None)
def gond_bg():
    c = Image.new("RGBA", (W, H), (245, 236, 215, 255)); p = Pen(W, H, 0, 0, 1.0)
    for x, s in ((150, 1.0), (930, 0.9)):
        p.shape([(x - 20 * s, 1840), (x + 20 * s, 1840), (x + 12 * s, 1100), (x - 12 * s, 1100)], (120, 70, 40), "hstripes", INK, 12)
        for k in range(7):
            a = -math.pi / 2 + (k - 3) * 0.45; cx, cy = x + 170 * s * math.cos(a), 1100 + 170 * s * math.sin(a)
            p.shape([(cx - 60 * s, cy), (cx, cy - 40 * s), (cx + 60 * s, cy), (cx, cy + 40 * s)], (60, 160, 80) if k % 2 else (250, 200, 40), "diag", INK, 10)
    M.peacock(p, 230, 1800, 0.55, 1)
    c.alpha_composite(p.done()); return c
G_BG = gond_bg()
def s_gond(t):
    c = G_BG.copy(); compose(c, G_H, G_M, t)
    d = ImageDraw.Draw(c); text_c(d, 190, "जय हनुमान", F("yatra", 120), (220, 50, 60), 4, (30, 20, 20)); return c

# Warli: terracotta wall, white stick figures
def s_warli(t):
    c = Image.new("RGBA", (W, H), (150, 72, 42, 255)); d = ImageDraw.Draw(c); WH = (245, 238, 225, 255)
    r = random.Random(6)
    for _ in range(4000): x, y = r.uniform(0, W), r.uniform(0, H); d.point((x, y), fill=(130, 60, 34, 255))
    for k in range(9):   # dancing circle of villagers at the bottom
        x = 160 + k * 95; y = 1760; ph = t * 6 + k
        d.polygon([(x - 18, y - 90), (x + 18, y - 90), (x, y - 60)], fill=WH); d.polygon([(x - 18, y - 30), (x + 18, y - 30), (x, y - 60)], fill=WH)
        d.ellipse([x - 11, y - 118, x + 11, y - 96], fill=WH)
        d.line([(x - 10, y - 30), (x - 22 - 6 * math.sin(ph), y)], fill=WH, width=5); d.line([(x + 10, y - 30), (x + 22 + 6 * math.sin(ph), y)], fill=WH, width=5)
        d.line([(x - 14, y - 82), (x - 48, y - 60 - 14 * math.sin(ph))], fill=WH, width=5); d.line([(x + 14, y - 82), (x + 48, y - 60 + 14 * math.sin(ph))], fill=WH, width=5)
    l = lift(t); s = 2.6; hx, hb = 540, 1560 - 60 * l
    tri = lambda pts: d.polygon([(hx + px * s, hb + py * s) for px, py in pts], fill=WH)
    tri([(-40, -170), (40, -170), (0, -110)]); tri([(-36, -50), (36, -50), (0, -110)])
    d.ellipse([hx - 22 * s, hb - 220 * s, hx + 22 * s, hb - 176 * s], fill=WH)
    for a, b in (((-30, -50), (-46, 0)), ((30, -50), (46, 0))): d.line([(hx + a[0] * s, hb + a[1] * s), (hx + b[0] * s, hb + b[1] * s)], fill=WH, width=12)
    ay = -170 - 60 * l
    for sx in (-1, 1): d.line([(hx + sx * 36 * s, hb - 165 * s), (hx + sx * 58 * s, hb + (ay + 10) * s), (hx + sx * 30 * s, hb + (ay - 30) * s)], fill=WH, width=12, joint="curve")
    d.line([(hx - 30 * s, hb - 60 * s), (hx - 80 * s, hb - 120 * s), (hx - 60 * s, hb - 180 * s), (hx - 85 * s, hb - 200 * s)], fill=WH, width=10, joint="curve")   # tail
    mb = hb + (ay - 30) * s if l > 0.05 else 1600
    mb = 1600 + (hb + (ay - 30) * s - 1600) * ease(l * 1.3)
    d.polygon([(hx - 300, mb), (hx, mb - 380), (hx + 300, mb)], outline=WH, width=10)
    for k in range(5):
        for j in range(k + 1): d.ellipse([hx - k * 46 + j * 92 - 9, mb - 300 + k * 60 - 9, hx - k * 46 + j * 92 + 9, mb - 300 + k * 60 + 9], fill=WH)
    text_c(d, 190, "पर्वत उठा लिया", F("kalam", 110) if False else F("yatra", 110), WH)
    return c

# Comic: posterised figure, halftone, speed burst, panels, bubble, SFX
C_H = outline(quantize(pad(HANU), [(240, 130, 40), (200, 40, 40), (250, 210, 60), (30, 30, 30), (240, 240, 230), (60, 120, 200)]), 7, (10, 10, 10))
C_M = outline(quantize(pad(MT), [(80, 160, 80), (250, 210, 60), (240, 240, 230), (30, 30, 30)]), 7, (10, 10, 10))
def s_comic(t):
    c = Image.new("RGBA", (W, H), (250, 245, 230, 255)); d = ImageDraw.Draw(c)
    cx, cy = 540, 1100
    for k in range(48):
        a = k * math.pi / 24; d.polygon([(cx, cy), (cx + 1600 * math.cos(a), cy + 1600 * math.sin(a)), (cx + 1600 * math.cos(a + 0.065), cy + 1600 * math.sin(a + 0.065))], fill=(255, 205, 60, 255) if k % 2 else (255, 170, 40, 255))
    for y in range(0, H, 22):
        for x in range((y // 22 % 2) * 11, W, 22):
            rr = 2 + 5 * (y / H); d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(230, 120, 30, 90))
    compose(c, C_H, C_M, t)
    d = ImageDraw.Draw(c)
    d.rectangle([30, 30, W - 30, H - 30], outline=(10, 10, 10), width=14); d.line([(30, 520), (W - 30, 470)], fill=(10, 10, 10), width=14)
    d.rectangle([44, 44, W - 44, 505], fill=(250, 245, 230)); d.polygon([(44, 505), (W - 44, 456), (W - 44, 470), (44, 520)], fill=(10, 10, 10))
    text_c(d, 120, "द्रोणगिरि पर्वत…", F("mukta", 96), (20, 20, 20))
    text_c(d, 260, "बूटी कौन सी है?", F("mukta", 80), (200, 40, 40))
    if t > 0.9:
        k = eout((t - 0.9) / 0.35); f = F("mukta", int(170 * (0.6 + 0.4 * k)))
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.text((620, 1350), "धड़ाम!", font=f, fill=(220, 40, 40, 255), language="hi", stroke_width=10, stroke_fill=(10, 10, 10, 255))
        c.alpha_composite(lay.rotate(12, center=(800, 1450)))
    if t > 2.2:
        d.ellipse([90, 600, 640, 860], fill=(255, 255, 255), outline=(10, 10, 10), width=8); d.polygon([(400, 840), (470, 980), (470, 850)], fill=(255, 255, 255), outline=(10, 10, 10))
        d.text((150, 660), "जय श्री राम!", font=F("mukta", 82), fill=(10, 10, 10), language="hi")
    return c

# Temple stone relief: carved from the figure masks, lit by a moving diya
def relief(im, depth=18):
    m = np.asarray(mask(im).filter(ImageFilter.GaussianBlur(10))).astype(float) / 255
    inner = np.asarray(ImageOps.grayscale(im.convert("RGB"))).astype(float) / 255 * 0.35 * (m > 0.5)
    return m * depth + inner * depth
STONE = np.random.default_rng(3).normal(0, 1, (H, W)); STONE = np.asarray(Image.fromarray(((STONE - STONE.min()) / np.ptp(STONE) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5))).astype(float) / 255
R_H = relief(pad(HANU)); R_M = relief(pad(MT), 14)
def s_stone(t):
    hm = np.zeros((H, W)); (mx, my), (hx, hy) = place(t, pad(HANU), None)
    def stamp(r, cx, base):
        h_, w_ = r.shape; x0, y0 = int(cx - w_ / 2), int(base - h_)
        xs, ys = max(0, x0), max(0, y0); xe, ye = min(W, x0 + w_), min(H, y0 + h_)
        if xe > xs and ye > ys: np.maximum(hm[ys:ye, xs:xe], r[ys - y0:ye - y0, xs - x0:xe - x0], out=hm[ys:ye, xs:xe])
    stamp(R_M, mx, my); stamp(R_H, hx, hy)
    hm += STONE * 3
    gy, gx = np.gradient(hm); lx, ly = math.cos(1.0 + 0.6 * math.sin(t * 1.3)), -0.8
    sh = np.clip(0.55 + (gx * lx + gy * ly) * 0.45, 0, 1.2)
    yy, xx = np.mgrid[0:H, 0:W]; fl = 1 + 0.04 * math.sin(t * 17)
    glow = np.exp(-(((xx - 540) / 900) ** 2 + ((yy - 1500) / 1300) ** 2)) * fl
    base = np.array([168, 150, 125]) / 255
    img = (sh * glow)[..., None] * base * 255 * (0.85 + 0.3 * STONE[..., None])
    c = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(c); text_c(d, 190, "संजीवनी", F("yatra", 150), (95, 80, 62), 2, (200, 185, 160)); return c

# Ink & gold silhouette
SIL_H = solid(pad(HANU), (18, 10, 6)); SIL_M = solid(pad(MT), (18, 10, 6))
def s_silhouette(t):
    yy = np.linspace(0, 1, H)[:, None, None]
    top, bot = np.array([60, 20, 10]), np.array([250, 190, 80])
    sky = (top * (1 - yy) + bot * yy) * np.ones((1, W, 1))
    c = Image.fromarray(sky.astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(c)
    d.ellipse([540 - 330, 1250 - 330 - 40 * t, 540 + 330, 1250 + 330 - 40 * t], fill=(255, 225, 140))
    compose(c, SIL_H, SIL_M, t)
    d = ImageDraw.Draw(c); d.rectangle([0, 1640, W, H], fill=(18, 10, 6))
    r = random.Random(9)
    for i in range(30):
        x = r.uniform(0, W); y = 1640 - ((r.uniform(0, 1500) + t * 90) % 1500); d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(255, 220, 140))
    text_c(d, 200, "पवनपुत्र", F("yatra", 150), (255, 230, 160)); return c

# Kinetic Hindi text
def s_kinetic(t):
    c = Image.new("RGBA", (W, H), (14, 10, 22, 255)); d = ImageDraw.Draw(c)
    put(c, solid(pad(MT), (90, 40, 25)), 540, 1760 - 300 * lift(t))
    for k, (word, col, t0, y, size) in enumerate([("हनुमान", (255, 140, 40), 0.0, 520, 190), ("ने उठाया", (240, 240, 240), 0.9, 800, 140), ("पूरा", (255, 220, 80), 1.8, 1030, 220), ("पर्वत!", (255, 80, 60), 2.4, 1300, 260)]):
        if t < t0: continue
        k2 = eout((t - t0) / 0.35); s = int(size * (1.6 - 0.6 * k2)); f = F("mukta", s)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        tw = f.getlength(word, language="hi"); ld.text((W / 2 - tw / 2, y - s * 0.3), word, font=f, fill=col + (int(255 * min(1, k2 * 1.5)),), language="hi")
        c.alpha_composite(lay)
    if 2.4 < t < 2.6: c = ImageChops.offset(c, int(14 * math.sin(t * 90)), 0)
    return c

# Shadow puppet: lamp light through a cloth, translucent dyed hide with carved holes (multiply)
def hide(im, dye):
    m = np.asarray(mask(im)).astype(float) / 255
    a = np.ones(m.shape + (3,)); col = np.array(dye) / 255
    r = np.random.default_rng(4).normal(0, 0.08, m.shape)
    piece = col * (0.85 + r[..., None])
    hole = np.zeros(m.shape, bool); hole[::26, ::26] = True
    hole = np.asarray(Image.fromarray(hole.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(7))) > 0
    er = np.asarray(mask(im).filter(ImageFilter.MinFilter(25))) > 128
    piece[hole & er] = 1.0
    edge = (m > 0.5) & ~(np.asarray(mask(im).filter(ImageFilter.MinFilter(7))) > 128)
    piece[edge] = np.array([0.17, 0.06, 0.02])
    trans = a * (1 - m[..., None]) + piece * m[..., None]
    return trans
PU_H = hide(pad(HANU), (200, 80, 30)); PU_M = hide(pad(MT), (90, 110, 40))
def s_puppet(t):
    yy, xx = np.mgrid[0:H, 0:W]; fl = 1 + 0.03 * math.sin(t * 13) + 0.02 * math.sin(t * 7.3)
    light = np.exp(-(((xx - 540) / 700) ** 2 + ((yy - 950) / 1000) ** 2)) * fl
    img = light[..., None] * np.array([255, 196, 120]) * 1.25
    weave = 0.93 + 0.07 * ((xx // 3 + yy // 3) % 2)
    img *= weave[..., None]
    (mx, my), (hx, hy) = place(t, pad(HANU), None)
    def mul(tr, cx, base):
        h_, w_ = tr.shape[:2]; x0, y0 = int(cx - w_ / 2), int(base - h_)
        xs, ys = max(0, x0), max(0, y0); xe, ye = min(W, x0 + w_), min(H, y0 + h_)
        img[ys:ye, xs:xe] *= tr[ys - y0:ye - y0, xs - x0:xe - x0]
    mul(PU_M, mx, my); mul(PU_H, hx, hy)
    vig = 1 - 0.55 * np.clip(((xx - 540) / 620) ** 2 + ((yy - 960) / 1050) ** 2, 0, 1)
    img *= vig[..., None]
    c = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(c)
    d.rectangle([0, 1600, W, H], fill=(40, 16, 8)); d.rectangle([20, 1620, W - 20, H - 40], outline=(150, 90, 40), width=4)
    f = F("noto", 70); text_c(d, 1650, "पूरा पर्वत ही उठा लाए", f, (255, 225, 150), 3, (60, 25, 10))
    text_c(d, 1770, "He carried the whole mountain", F("tiro", 40), (220, 190, 140)); return c

STY = [("madhubani", "Madhubani", s_madhubani), ("pattachitra", "Pattachitra", s_pattachitra), ("kalamkari", "Kalamkari / Pichwai", s_kalamkari),
       ("gond", "Gond", s_gond), ("warli", "Warli", s_warli), ("puppet", "Shadow puppet", s_puppet), ("comic", "Comic book", s_comic),
       ("stone", "Temple stone relief", s_stone), ("silhouette", "Ink & gold silhouette", s_silhouette), ("kinetic", "Kinetic text", s_kinetic)]

def render(key, out):
    n, (k, name, fn) = next((i + 1, s) for i, s in enumerate(STY) if s[0] == key)
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)):
        c = fn(i / FPS); label(c, n, name); ff.stdin.write(np.asarray(c.convert("RGB")).tobytes())
    ff.stdin.close(); ff.wait()

if __name__ == "__main__":
    a = sys.argv[1]
    if a == "sheet":
        ims = []
        for i, (k, name, fn) in enumerate(STY):
            c = fn(3.2); label(c, i + 1, name); ims.append(c.convert("RGB").resize((270, 480)))
        s = Image.new("RGB", (270 * 5, 960))
        for i, im in enumerate(ims): s.paste(im, ((i % 5) * 270, (i // 5) * 480))
        s.save("styles_sheet.jpg", quality=88)
    else: render(a, f"st_{a}.mp4")
