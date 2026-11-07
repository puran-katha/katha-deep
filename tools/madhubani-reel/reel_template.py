"""Madhubani reel: Diwali kyon manate hain. Usage: python3 diwali.py out.mp4 [t0 t1]"""
import sys, math, random, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import madhu as M
from madhu import Pen, INK, PAPER, RED, YEL, ORA, GRN, LGRN, BLU, SKY, PINK, MAROON, WHITE

W, H, FPS = 1080, 1920, 30
import os
GF = os.environ.get("GF", os.path.expanduser("~/gf/ofl/"))  # Google Fonts checkout; needs yatraone/YatraOne-Regular.ttf
F_Y = GF + "yatraone/YatraOne-Regular.ttf"
_fc = {}
def font(s):
    if s not in _fc: _fc[s] = ImageFont.truetype(F_Y, s, layout_engine=ImageFont.Layout.RAQM)
    return _fc[s]
def ease(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)
def eout(x): x = min(1, max(0, x)); return 1 - (1 - x) ** 3

import json as _j
LEAD = 1.0; _vs = [(a + LEAD, b + LEAD) for a, b in _j.load(open("dv_spans.json"))]
_st = [0.0] + [round(a - 0.1, 2) for a, b in _vs[1:]]; TOTAL = round(_vs[-1][1] + 5.0, 2); BANNER = _vs[-1][1] + 0.4
SC = list(zip(["title", "vanvas", "haran", "hanuman", "vijay", "viman", "deep", "darbar"], _st, _st[1:] + [TOTAL]))
XF = 1.0
CAP = dict(title=None, vanvas=("राम, सीता और लक्ष्मण", "14 वर्ष का वनवास"), haran=("रावण छल से", "सीता को लंका ले गया"),
           hanuman=("हनुमान ने समुद्र लांघकर", "सीता को खोज निकाला"), vijay=("दशहरे के दिन", "राम ने रावण को हराया"),
           viman=("पुष्पक विमान से", "सब अयोध्या लौटे"), deep=("अमावस्या की अँधेरी रात,", "अयोध्या ने दीप जलाए"),
           darbar=("इसीलिए हम", "दिवाली मनाते हैं"))

# ---------------------------------------------------------------- sprites
print("drawing figures…", flush=True)
SPR = {k: M.figure(k, f, h, pose) for k, f, h, pose in [
    ("ram", 1, 820, "stand"), ("sita", 1, 760, "stand"), ("lakshman", 1, 800, "stand"), ("hanuman", 1, 880, "stand"), ("ravana", -1, 1000, "stand")]}
SPR["ram_r"] = SPR["ram"]; SPR["lak_v"] = M.figure("lakshman", 1, 800); SPR["ram_v"] = M.figure("ram", 1, 1000)
SPR["ram_seat"] = M.figure("ram", 1, 760, "seated"); SPR["sita_seat"] = M.figure("sita", -1, 720, "seated")
SPR["hanu_small"] = M.figure("hanuman", -1, 640); SPR["hanu_fly"] = M.figure("hanuman", 1, 620); SPR["lak_small"] = M.figure("lakshman", 1, 800)
SPR["sita_l"] = M.figure("sita", 1, 760); SPR["ravana_s"] = M.figure("ravana", -1, 760)

def put(c, im, cx, base, alpha=1.0, rot=0.0):
    if rot: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 1: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    x, y = int(cx - im.width / 2), int(base - im.height)
    if x >= W or y >= H or x + im.width <= 0 or y + im.height <= 0: return
    c.alpha_composite(im, (max(0, x), max(0, y)), (max(0, -x), max(0, -y)))

# ---------------------------------------------------------------- static backgrounds
def border_layer():
    p = Pen(W, H, 0, 0, 1.0)
    p.d.rectangle([0, 0, W * 2, H * 2], outline=None)
    m = Image.new("L", p.img.size, 255); ImageDraw.Draw(m).rectangle([80 * 2, 80 * 2, (W - 80) * 2, (H - 80) * 2], fill=0)
    band = Image.new("RGBA", p.img.size, RED + (255,)); bd = ImageDraw.Draw(band)
    for x in range(0, W * 2, 60): bd.polygon([(x, 0), (x + 30, 60), (x + 60, 0)], fill=YEL + (255,)); bd.polygon([(x, H * 2), (x + 30, H * 2 - 60), (x + 60, H * 2)], fill=YEL + (255,))
    for y in range(0, H * 2, 60): bd.polygon([(0, y), (60, y + 30), (0, y + 60)], fill=YEL + (255,)); bd.polygon([(W * 2, y), (W * 2 - 60, y + 30), (W * 2, y + 60)], fill=YEL + (255,))
    for x in range(140, W * 2 - 100, 120):
        for yy in (110, H * 2 - 110): bd.ellipse([x - 16, yy - 16, x + 16, yy + 16], fill=GRN + (255,), outline=INK + (255,), width=4)
    for y in range(140, H * 2 - 100, 120):
        for xx in (110, W * 2 - 110): bd.ellipse([xx - 16, y - 16, xx + 16, y + 16], fill=GRN + (255,), outline=INK + (255,), width=4)
    p.img.paste(band, (0, 0), m)
    for mrg, wd in ((6, 10), (74, 8), (82, 3)): p.d.rectangle([mrg * 2, mrg * 2, (W - mrg) * 2, (H - mrg) * 2], outline=INK + (255,), width=wd)
    return p.done()
BORDER = border_layer()

def paper(col=PAPER):
    im = Image.new("RGB", (W, H), col); a = np.asarray(im).astype(np.int16)
    a = a + np.random.default_rng(1).normal(0, 4, a.shape[:2])[..., None].astype(np.int16)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")

def sun(p, x, y, r=90, moon=False):
    if moon:
        p.circle(x, y, r, WHITE); p.circle(x + r * 0.4, y - r * 0.15, r * 0.85, (40, 50, 110), outline=False); return
    for k in range(16):
        a = k * math.pi / 8; p.shape([(x + (r + 8) * math.cos(a - 0.13), y + (r + 8) * math.sin(a - 0.13)), (x + (r + 55) * math.cos(a), y + (r + 55) * math.sin(a)), (x + (r + 8) * math.cos(a + 0.13), y + (r + 8) * math.sin(a + 0.13))], YEL, None, inner=False, width=3)
    p.circle(x, y, r, RED, w=5); p.circle(x, y, r * 0.55, YEL, w=3)

def ground(p, y, col=LGRN, pat="dots"):
    p.shape([(80, y)] + M.bez((80, y), (540, y - 40), (1000, y)) + [(1000, 1840), (80, 1840)], col, pat, GRN, 26, inner=False)

def palace(p, x, base, sc=1.0, lit=False):
    s = sc
    p.shape([(x - 170 * s, base), (x + 170 * s, base), (x + 170 * s, base - 160 * s), (x - 170 * s, base - 160 * s)], RED, "checks", YEL, 22)
    p.shape([(x - 120 * s, base - 160 * s), (x + 120 * s, base - 160 * s), (x + 90 * s, base - 260 * s), (x - 90 * s, base - 260 * s)], YEL, "scales", RED, 18)
    p.shape([(x - 60 * s, base - 260 * s), (x, base - 420 * s), (x + 60 * s, base - 260 * s)], RED, "stripes", YEL, 14)
    for dx in (-150, 150): p.shape([(x + dx * s - 40 * s, base - 160 * s), (x + dx * s, base - 260 * s), (x + dx * s + 40 * s, base - 160 * s)], ORA, None)
    p.line([(x, base - 420 * s), (x, base - 480 * s)], INK, 5); p.shape([(x, base - 480 * s), (x + 50 * s, base - 465 * s), (x, base - 450 * s)], ORA, None, inner=False, width=3)
    for k in range(5):
        wx = x - 130 * s + k * 65 * s; p.shape([(wx, base - 30 * s), (wx + 34 * s, base - 30 * s), (wx + 34 * s, base - 100 * s), (wx + 17 * s, base - 120 * s), (wx, base - 100 * s)], YEL if lit else INK, None, inner=False, width=3)

def bg_title():
    c = paper(); p = Pen(W, H, 0, 0, 1.0)
    for x in range(150, 960, 70): p.circle(x, 760, 10, (RED, YEL, GRN)[(x // 70) % 3], w=2)
    M.peacock(p, 330, 1480, 0.8, 1); M.peacock(p, 750, 1480, 0.8, -1)
    ground(p, 1600)
    c.alpha_composite(p.done()); return c

def bg_forest():
    c = paper(); p = Pen(W, H, 0, 0, 1.0); sun(p, 820, 560, 80)
    for x, s in [(200, 1.1), (520, 0.8), (880, 1.15)]: M.tree(p, x, 1350, s)
    ground(p, 1330); c.alpha_composite(p.done()); return c

def bg_lanka(night=False):
    c = paper((60, 40, 70) if night else PAPER); p = Pen(W, H, 0, 0, 1.0)
    M.tree(p, 250, 1340, 1.2)
    for k in range(8): p.circle(170 + k * 25, 900 + (k % 3) * 40, 14, RED)       # ashoka flowers
    p.shape([(560, 1330), (1000, 1330), (1000, 760), (940, 700), (880, 760), (820, 700), (760, 760), (700, 700), (640, 760), (560, 760)], YEL, "checks", RED, 30)  # golden fort
    ground(p, 1330, (200, 120, 60), "diag"); c.alpha_composite(p.done()); return c

def bg_sea():
    c = paper(); p = Pen(W, H, 0, 0, 1.0); sun(p, 860, 620, 60)
    p.shape([(700, 1200), (1000, 1200), (1000, 820), (960, 780), (920, 820), (880, 780), (840, 820), (800, 780), (760, 820), (700, 820)], YEL, "checks", RED, 26)
    p.shape([(80, 1200), (1000, 1200), (1000, 1840), (80, 1840)], BLU, "waves", SKY, 34, inner=False)
    for x, y, f in [(240, 1400, 1), (600, 1560, -1), (360, 1720, 1), (820, 1420, -1)]: M.fish(p, x, y, 0.9, f)
    p.shape([(80, 1220), (300, 1180), (300, 1260), (80, 1300)], (200, 140, 70), "dots", INK, 20)
    c.alpha_composite(p.done()); return c

def bg_battle():
    c = paper(); p = Pen(W, H, 0, 0, 1.0); sun(p, 540, 520, 120)
    ground(p, 1500, (200, 140, 70), "diag"); c.alpha_composite(p.done()); return c

def bg_sky():
    c = paper(); p = Pen(W, H, 0, 0, 1.0); sun(p, 850, 470, 70)
    for x, y in [(250, 700), (650, 600), (420, 860)]:
        for k in range(4): p.circle(x + k * 45, y - (k % 2) * 20, 38, WHITE, w=3)
    palace(p, 540, 1700, 0.9); ground(p, 1700, LGRN); c.alpha_composite(p.done()); return c

def bg_night():
    c = paper((32, 40, 92)); p = Pen(W, H, 0, 0, 1.0)
    r = random.Random(3)
    for _ in range(80): p.circle(r.uniform(100, 980), r.uniform(120, 1000), r.uniform(2, 5), YEL, outline=False)
    palace(p, 540, 1350, 1.05, lit=True)
    p.shape([(80, 1350), (1000, 1350), (1000, 1840), (80, 1840)], (130, 60, 50), "checks", (160, 80, 60), 40, inner=False)
    for k, (x, y) in enumerate([(320, 1650), (540, 1700), (760, 1650)]):   # rangoli
        for j in range(8):
            a = j * math.pi / 4; p.shape([(x, y), (x + 70 * math.cos(a - 0.3), y + 40 * math.sin(a - 0.3)), (x + 110 * math.cos(a), y + 64 * math.sin(a)), (x + 70 * math.cos(a + 0.3), y + 40 * math.sin(a + 0.3))], (PINK, YEL, ORA)[j % 3], None, inner=False, width=3)
    c.alpha_composite(p.done()); return c

def bg_darbar():
    c = paper(); p = Pen(W, H, 0, 0, 1.0)
    p.shape([(140, 560), (940, 560), (900, 640), (180, 640)], RED, "scales", YEL, 20)            # canopy
    for x in (190, 890): p.shape([(x - 22, 640), (x + 22, 640), (x + 22, 1560), (x - 22, 1560)], YEL, "hstripes", RED, 18)
    for k in range(9): p.shape([(180 + k * 90, 640), (225 + k * 90, 700), (270 + k * 90, 640)], ORA, None, inner=False, width=3)
    p.shape([(250, 1560), (830, 1560), (800, 1400), (280, 1400)], YEL, "checks", RED, 26)       # throne base
    p.shape([(300, 1400), (780, 1400), (760, 900), (320, 900)], (230, 160, 60), "scales", RED, 26)  # throne back
    ground(p, 1560, LGRN); c.alpha_composite(p.done()); return c

print("painting backgrounds…", flush=True)
BG = dict(title=bg_title(), vanvas=bg_forest(), haran=bg_lanka(), hanuman=bg_sea(), vijay=bg_battle(), viman=bg_sky(), deep=bg_night(), darbar=bg_darbar())

# ---------------------------------------------------------------- dynamic layers
def diyas_layer(t, pts, sc=0.8, light_from=None, gap=0.12):
    p = Pen(W, H, 0, 0, 1.0, K=1)
    for i, (x, y) in enumerate(pts):
        fl = 1.0 if light_from is None else eout((t - light_from - i * gap) / 0.25)
        M.diya(p, x, y, sc, fl * (0.9 + 0.1 * math.sin(t * 11 + i)), t)
    return p.img

def viman(t, x, y):
    p = Pen(760, 520, 380, 300, 1.0, K=1)
    p.shape([(-300, 40), (300, 40), (240, 120), (-240, 120)], YEL, "scales", RED, 18)
    p.shape([(300, 40), (380, -40), (360, 60), (300, 100)], RED, None)                       # peacock prow
    p.circle(372, -50, 22, BLU); p.shape([(-300, 40), (-370, -60), (-330, 70)], GRN, "diag", INK, 12)
    for wx in (-200, 160):
        flap = 30 * math.sin(t * 6)
        p.shape([(wx, 60), (wx + 80, 60), (wx + 40, -40 - flap)], WHITE, "stripes", SKY, 12)
    p.shape([(-260, 40), (260, 40), (220, -10), (-220, -10)], RED, "checks", YEL, 16)
    return p.img

def caption(c, key, t, s):
    cap = CAP.get(key)
    if not cap: return
    a = eout((t - s - 0.35) / 0.4)
    if a <= 0: return
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([110, 150, 970, 470], 30, fill=PAPER + (int(240 * a),), outline=RED + (int(255 * a),), width=8)
    d.rounded_rectangle([126, 166, 954, 454], 22, outline=INK + (int(255 * a),), width=3)
    for k, (txt, col, size) in enumerate([(cap[0], INK, 70), (cap[1], RED, 84)]):
        f = font(size); tw = f.getlength(txt, language="hi"); ka = eout((t - s - 0.35 - k * 0.3) / 0.4)
        d.text((W / 2 - tw / 2, 182 + k * 120 + 18 * (1 - ka)), txt, font=f, fill=col + (int(255 * ka * a),), language="hi")
    c.alpha_composite(lay)

def scene(key, t):
    s, e = next((a, b) for k, a, b in SC if k == key); lt = t - s
    c = BG[key].copy()
    if key == "title":
        p = Pen(W, H, 0, 0, 1.0, K=1); M.diya(p, 540, 1130, 2.6, 1.0 * (0.92 + 0.08 * math.sin(t * 8)), t); c.alpha_composite(p.img)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        for k, (txt, col, size, y) in enumerate([("दिवाली", RED, 210, 250), ("क्यों मनाते हैं?", INK, 96, 540)]):
            ka = eout((t - 0.3 - k * 0.5) / 0.5); f = font(size); tw = f.getlength(txt, language="hi")
            d.text((W / 2 - tw / 2, y + 30 * (1 - ka)), txt, font=f, fill=col + (int(255 * ka),), language="hi", stroke_width=4, stroke_fill=PAPER + (int(255 * ka),))
        c.alpha_composite(lay)
    elif key == "vanvas":
        for k, (sp, x0) in enumerate([("ram", 300), ("sita", 560), ("lakshman", 820)]):
            x = x0 - 520 + 520 * eout((lt - k * 0.25) / 2.6) + 12 * lt; bob = 10 * abs(math.sin(lt * 4 + k))
            put(c, SPR[sp], x - 60, 1800 - bob)
    elif key == "haran":
        put(c, SPR["sita_l"], 330, 1790, rot=0)
        rx = 1400 - 620 * eout(lt / 1.6); put(c, SPR["ravana_s"], rx, 1800)
    elif key == "hanuman":
        k = (lt - 0.5) / 4.8; k = min(1, max(0, k)); x = 200 + 620 * k; y = 1250 - 380 * math.sin(math.pi * k)
        put(c, SPR["hanu_fly"], x, y + 250, rot=-30 + 45 * k)
        p = Pen(W, H, 0, 0, 1.0, K=1)
        for j in range(6): p.line([(80 + ((lt * 60 + j * 160) % 920), 1260 + j * 90), (140 + ((lt * 60 + j * 160) % 920), 1260 + j * 90)], WHITE, 5)
        c.alpha_composite(p.img)
    elif key == "vijay":
        put(c, SPR["ram_v"], 330, 1840); put(c, SPR["lak_v"], 140, 1760, alpha=0.95)
        fade = 1 - ease((lt - 3.0) / 1.2); put(c, SPR["ravana_s"], 860, 1780, alpha=max(0, fade))
        if lt > 1.0:
            k = eout((lt - 1.0) / 1.6); ax = 480 + 300 * k; ay = 1150
            p = Pen(W, H, 0, 0, 1.0, K=1); p.line([(ax - 160, ay), (ax, ay)], INK, 8)
            p.shape([(ax, ay - 22), (ax + 50, ay), (ax, ay + 22)], RED, None, inner=False, width=3)
            for f in range(3): p.line([(ax - 160 - f * 12, ay - 16), (ax - 140 - f * 12, ay)], RED, 4)
            c.alpha_composite(p.img)
            if lt > 2.6:
                d = ImageDraw.Draw(c); r = 140 * eout((lt - 2.6) / 0.6)
                for j in range(12):
                    a = j * math.pi / 6; d.line([(800 + r * 0.4 * math.cos(a), 1150 + r * 0.4 * math.sin(a)), (800 + r * math.cos(a), 1150 + r * math.sin(a))], fill=YEL + (230,), width=8)
    elif key == "viman":
        x = -350 + 1700 * (lt / (e - s)); y = 900 + 30 * math.sin(lt * 2)
        v = viman(t, x, y); c.alpha_composite(v, (int(x - 380), int(y - 300)))
        for k, (sp, dx) in enumerate([("hanu_small", -200), ("lak_small", -70), ("sita_l", 60), ("ram", 190)]):
            im = SPR[sp].resize((int(SPR[sp].width * 0.5), int(SPR[sp].height * 0.5)), Image.LANCZOS)
            put(c, im, x + dx, y + 70)
        v2 = Pen(W, H, 0, 0, 1.0, K=1); v2.d.rectangle([(x - 300), (y + 40), (x + 300), (y + 120)], fill=None)
    elif key == "deep":
        rows = [(x, 1450) for x in range(170, 960, 95)] + [(x, 1780) for x in range(170, 960, 95)] + [(x, 1350) for x in (230, 850)]
        c.alpha_composite(diyas_layer(t, rows, 0.6, s + 0.8, 0.18))
        put(c, SPR["sita_l"].resize((340, int(SPR["sita_l"].height * 340 / SPR["sita_l"].width))), 170, 1660, alpha=eout(lt / 0.8))
    elif key == "darbar":
        put(c, SPR["ram_seat"], 460, 1440); put(c, SPR["sita_seat"], 660, 1450)
        put(c, SPR["lak_small"], 220, 1600); put(c, SPR["hanu_small"], 880, 1620)
        c.alpha_composite(diyas_layer(t, [(x, 1760) for x in range(170, 960, 110)], 0.55))
        d = ImageDraw.Draw(c); r = random.Random(4)
        for i in range(40):
            x0, sp, ph = r.uniform(100, 980), r.uniform(80, 150), r.uniform(0, 6.3); y = (r.uniform(-1500, 0) + lt * sp) % 1700 + 100
            x = x0 + 30 * math.sin(lt + ph); col = (PINK, ORA, YEL)[i % 3]; d.ellipse([x - 9, y - 6, x + 9, y + 6], fill=col + (255,), outline=INK + (255,))
        if t > BANNER:
            ka = eout((t - BANNER) / 0.6); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
            ld.rounded_rectangle([140, 150, 940, 470], 30, fill=RED + (int(245 * ka),), outline=YEL + (int(255 * ka),), width=10)
            f = font(150); txt = "शुभ दीपावली"; tw = f.getlength(txt, language="hi")
            ld.text((W / 2 - tw / 2, 205), txt, font=f, fill=YEL + (int(255 * ka),), language="hi", stroke_width=3, stroke_fill=INK + (int(255 * ka),))
            c.alpha_composite(lay); return c
    caption(c, key, t, s)
    return c

# ---------------------------------------------------------------- wipe + compose
_n = np.random.default_rng(5).random((H // 8, W // 8))
_n = np.asarray(Image.fromarray((_n * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(14))).astype(np.float32) / 255
_dg = (np.arange(W)[None, :] / W * 0.55 + np.arange(H)[:, None] / H * 0.45).astype(np.float32)
def wipe(k): return Image.fromarray((np.clip((k * 1.5 - (_dg + (_n - 0.5) * 0.35)) / 0.12, 0, 1) * 255).astype(np.uint8))

def frame(t):
    i = next((j for j, (k, a, b) in enumerate(SC) if a <= t < b), len(SC) - 1); key, s, e = SC[i]
    c = scene(key, t)
    if i > 0 and t - s < XF: c = Image.composite(c, scene(SC[i - 1][0], t), wipe((t - s) / XF))
    c.alpha_composite(BORDER)
    a = np.asarray(c.convert("RGB")).astype(np.float32)
    if t < 0.3: a *= t / 0.3
    if t > TOTAL - 0.8: a *= max(0, (TOTAL - t) / 0.8)
    return np.clip(a, 0, 255).astype(np.uint8)

if __name__ == "__main__":
    out = sys.argv[1]; t0 = float(sys.argv[2]) if len(sys.argv) > 2 else 0; t1 = float(sys.argv[3]) if len(sys.argv) > 3 else TOTAL
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(int(t0 * FPS), int(t1 * FPS)):
        ff.stdin.write(frame(i / FPS).tobytes())
        if i % 150 == 0: print(out, i, flush=True)
    ff.stdin.close(); ff.wait()
