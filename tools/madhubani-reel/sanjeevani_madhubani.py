"""Madhubani sample: Hanuman brings Sanjeevani (~30 s). Usage: python3 sanj_m.py out.mp4 [t0 t1]"""
import sys, math, random, subprocess
import numpy as np
from PIL import Image, ImageDraw
import reel_template as D, madhu as M
from madhu import Pen, INK, PAPER, RED, YEL, ORA, GRN, LGRN, BLU, SKY, PINK, WHITE, MAROON
W, H, FPS = 1080, 1920, 30
ease, eout, put, font = D.ease, D.eout, D.put, D.font

SC = [("s1", 0, 5.5), ("s2", 5.5, 10.5), ("s3", 10.5, 15.5), ("s4", 15.5, 21), ("s5", 21, 26), ("s6", 26, 30.5)]
TOTAL = 30.5; XF = 0.8
CAP = dict(s1=("युद्ध में मेघनाद के शक्ति बाण से", "लक्ष्मण मूर्छित हो गए"), s2=("वैद्य सुषेण बोले —", "सूर्योदय से पहले संजीवनी लाओ"),
           s3=("हनुमान उड़ चले", "हिमालय के द्रोणगिरि की ओर"), s4=("बूटी पहचान न सके…", "तो पूरा पर्वत ही उठा लिया!"),
           s5=("सूर्योदय से पहले लौटे,", "लक्ष्मण जी उठ खड़े हुए"))

S = dict(ram=M.figure("ram", 1, 800), lak=M.figure("lakshman", 1, 760), hanu=M.figure("hanuman", -1, 760),
         hanu_big=M.figure("hanuman", 1, 1100), hanu_fly=M.figure("hanuman", 1, 520), lak_l=M.figure("lakshman", 1, 700))

def mountain(sc=1.0, t=0.0):
    w, h = int(620 * sc), int(520 * sc); p = Pen(w, h, w / 2, h - 10, 1.0, K=1)
    s = sc
    p.shape([(-300 * s, 0), (-170 * s, -300 * s), (-90 * s, -230 * s), (0, -480 * s), (110 * s, -260 * s), (190 * s, -340 * s), (300 * s, 0)], (120, 150, 90), "diag", GRN, 22 * s)
    p.shape([(-40 * s, -400 * s), (0, -480 * s), (50 * s, -380 * s), (20 * s, -360 * s)], WHITE, None, inner=False, width=3)
    r = random.Random(7)
    for k in range(16):
        x, y = r.uniform(-220, 220) * s, r.uniform(-260, -30) * s
        g = 0.6 + 0.4 * math.sin(t * 6 + k)
        p.circle(x, y, (16 + 6 * g) * s, YEL); p.circle(x, y, 7 * s, ORA, outline=False)
    return p.img

def bg(kind):
    if kind == "battle":
        c = D.paper((70, 30, 40)); p = Pen(W, H, 0, 0, 1.0)
        D.sun(p, 820, 700, 70, moon=True); D.ground(p, 1450, (150, 80, 50), "diag")
        for x in (180, 900):
            p.line([(x, 1450), (x, 1150)], INK, 6); p.shape([(x, 1150), (x + 80, 1175), (x, 1200)], RED, "stripes", YEL, 10)
        c.alpha_composite(p.done()); return c
    if kind == "camp":
        c = D.paper((32, 40, 92)); p = Pen(W, H, 0, 0, 1.0); r = random.Random(3)
        for _ in range(60): p.circle(r.uniform(100, 980), r.uniform(560, 1000), r.uniform(2, 5), YEL, outline=False)
        D.sun(p, 830, 640, 60, moon=True); D.ground(p, 1500, (70, 90, 60), "dots")
        c.alpha_composite(p.done()); return c
    if kind == "sky":
        c = D.paper((32, 40, 92)); p = Pen(W, H, 0, 0, 1.0); r = random.Random(5)
        for _ in range(70): p.circle(r.uniform(100, 980), r.uniform(560, 1300), r.uniform(2, 5), YEL, outline=False)
        for k in range(5):
            x = 80 + k * 220; p.shape([(x - 160, 1840), (x, 1520 - (k % 2) * 120), (x + 160, 1840)], (90, 110, 150), "diag", (120, 140, 180), 24)
            p.shape([(x - 40, 1620 - (k % 2) * 120), (x, 1520 - (k % 2) * 120), (x + 40, 1620 - (k % 2) * 120)], WHITE, None, inner=False, width=3)
        c.alpha_composite(p.done()); return c
    if kind == "himalaya":
        c = D.paper((40, 50, 100)); p = Pen(W, H, 0, 0, 1.0); D.sun(p, 220, 640, 55, moon=True)
        D.ground(p, 1560, (90, 110, 150), "diag"); c.alpha_composite(p.done()); return c
    if kind == "dawn":
        c = D.paper((250, 200, 150)); p = Pen(W, H, 0, 0, 1.0)
        D.ground(p, 1480, LGRN); c.alpha_composite(p.done()); return c
    c = D.paper(); p = Pen(W, H, 0, 0, 1.0); D.sun(p, 540, 1000, 330); D.ground(p, 1600, LGRN)
    c.alpha_composite(p.done()); return c
print("backgrounds…", flush=True)
BG = dict(s1=bg("battle"), s2=bg("camp"), s3=bg("sky"), s4=bg("himalaya"), s5=bg("dawn"), s6=bg("glory"))

def caption(c, key, t, s):
    cap = CAP.get(key)
    if not cap: return
    a = eout((t - s - 0.3) / 0.4)
    if a <= 0: return
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([90, 150, 990, 470], 30, fill=PAPER + (int(240 * a),), outline=RED + (int(255 * a),), width=8)
    d.rounded_rectangle([106, 166, 974, 454], 22, outline=INK + (int(255 * a),), width=3)
    for k, (txt, col, size) in enumerate([(cap[0], INK, 64), (cap[1], RED, 78)]):
        f = font(size); tw = f.getlength(txt, language="hi")
        while tw > 820: size -= 2; f = font(size); tw = f.getlength(txt, language="hi")
        ka = eout((t - s - 0.3 - k * 0.3) / 0.4)
        d.text((W / 2 - tw / 2, 186 + k * 120 + 18 * (1 - ka)), txt, font=f, fill=col + (int(255 * ka * a),), language="hi")
    c.alpha_composite(lay)

def scene(key, t):
    s, e = next((a, b) for k, a, b in SC if k == key); lt = t - s; c = BG[key].copy()
    if key == "s1":
        put(c, S["ram"], 230, 1700 + 6 * math.sin(lt * 2)); put(c, S["hanu"], 900, 1720)
        put(c, S["lak_l"], 560, 1720, rot=90)
    elif key == "s2":
        k = ease((lt - 1.0) / 2.5); sc = 0.7 + 0.5 * k
        im = S["hanu_big"].resize((int(S["hanu_big"].width * sc), int(S["hanu_big"].height * sc)))
        put(c, im, 540, 1760)
        if lt > 3.2:
            d = ImageDraw.Draw(c); r = 60 + 300 * eout((lt - 3.2) / 0.6)
            for j in range(16):
                a = j * math.pi / 8; d.line([(540 + r * 0.6 * math.cos(a), 1250 + r * 0.6 * math.sin(a)), (540 + r * math.cos(a), 1250 + r * math.sin(a))], fill=YEL + (200,), width=6)
    elif key == "s3":
        x = -250 + 1600 * (lt / (e - s)); y = 1100 - 120 * math.sin(lt * 1.2)
        p = Pen(W, H, 0, 0, 1.0, K=1)
        for j in range(5): p.line([(x - 420 - j * 40, y - 280 + j * 60), (x - 200 - j * 30, y - 280 + j * 60)], WHITE, 5)
        c.alpha_composite(p.img); put(c, S["hanu_fly"], x, y, rot=-55)
    elif key == "s4":
        lift = ease((lt - 1.8) / 2.6); m = mountain(1.0, t)
        hx = 540; base = 1700
        hs = S["hanu_big"].resize((560, int(S["hanu_big"].height * 560 / S["hanu_big"].width)))
        m = mountain(1.15, t); hb = base - 60 * lift
        put(c, m, hx, base - 20 + (-(hs.height * 0.86) + 20) * lift)
        put(c, hs, hx, hb)
    elif key == "s5":
        p = Pen(W, H, 0, 0, 1.0); D.sun(p, 820, 1400 - 600 * eout(lt / 3.5), 90); c.alpha_composite(p.img)
        D.ground(Pen(W, H, 0, 0, 1.0), 1480)
        g = Pen(W, H, 0, 0, 1.0); D.ground(g, 1480); c.alpha_composite(g.img)
        mx = 1300 - 900 * eout(lt / 2.0); put(c, mountain(0.45, t), mx, 760)
        up = ease((lt - 1.8) / 1.4)
        if up < 1: put(c, S["lak_l"], 640, 1640, rot=90 * (1 - up))
        else: put(c, S["lak"], 640, 1760)
        put(c, S["ram"], 330, 1760)
    elif key == "s6":
        put(c, S["hanu_big"], 540, 1800)
        d = ImageDraw.Draw(c); r = random.Random(4)
        for i in range(40):
            x0, sp, ph = r.uniform(100, 980), r.uniform(80, 150), r.uniform(0, 6.3); y = (r.uniform(-1500, 0) + lt * sp) % 1700 + 100
            x = x0 + 30 * math.sin(lt + ph); d.ellipse([x - 9, y - 6, x + 9, y + 6], fill=(PINK, ORA, YEL)[i % 3] + (255,), outline=INK + (255,))
        ka = eout((lt - 0.4) / 0.6); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle([120, 150, 960, 470], 30, fill=RED + (int(245 * ka),), outline=YEL + (int(255 * ka),), width=10)
        f = font(132); txt = "जय बजरंगबली!"; tw = f.getlength(txt, language="hi")
        ld.text((W / 2 - tw / 2, 215), txt, font=f, fill=YEL + (int(255 * ka),), language="hi", stroke_width=3, stroke_fill=INK + (int(255 * ka),))
        c.alpha_composite(lay); return c
    caption(c, key, t, s); return c

def frame(t):
    i = next((j for j, (k, a, b) in enumerate(SC) if a <= t < b), len(SC) - 1); key, s, e = SC[i]
    c = scene(key, t)
    if i > 0 and t - s < XF: c = Image.composite(c, scene(SC[i - 1][0], t), D.wipe((t - s) / XF))
    c.alpha_composite(D.BORDER)
    a = np.asarray(c.convert("RGB")).astype(np.float32)
    if t < 0.3: a *= t / 0.3
    return np.clip(a, 0, 255).astype(np.uint8)

if __name__ == "__main__":
    out = sys.argv[1]; t0 = float(sys.argv[2]) if len(sys.argv) > 2 else 0; t1 = float(sys.argv[3]) if len(sys.argv) > 3 else TOTAL
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(int(t0 * FPS), int(t1 * FPS)): ff.stdin.write(frame(i / FPS).tobytes())
    ff.stdin.close(); ff.wait()
