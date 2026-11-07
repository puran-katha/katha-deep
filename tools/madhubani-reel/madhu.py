"""Madhubani drawing kit: patterned fills, double outlines, profile figures (Ram, Sita, Lakshman, Hanuman, Ravana)."""
import math, random
import numpy as np
from PIL import Image, ImageDraw

INK = (28, 16, 10)
PAPER = (244, 228, 194)
RED = (200, 45, 38); MAROON = (140, 30, 30); YEL = (240, 180, 30); ORA = (236, 120, 40)
GRN = (70, 140, 60); LGRN = (140, 190, 80); BLU = (50, 100, 190); SKY = (90, 160, 220); PINK = (235, 120, 150)
RAMBLUE = (60, 120, 200); SKIN = (240, 190, 140); HANU = (225, 110, 40); WHITE = (250, 245, 230)


class Pen:
    """Supersampled RGBA canvas in local coordinates; origin (ox, oy), scale s."""
    def __init__(self, w, h, ox, oy, s=1.0, K=2):
        self.w, self.h, self.K, self.s = w, h, K, s
        self.ox, self.oy = ox, oy
        self.img = Image.new("RGBA", (w * K, h * K), (0, 0, 0, 0)); self.d = ImageDraw.Draw(self.img)
    def P(self, pts): return [((self.ox + x * self.s) * self.K, (self.oy + y * self.s) * self.K) for x, y in pts]
    def lw(self, v): return max(1, int(v * self.s * self.K))
    def shape(self, pts, fill, pattern=None, pcol=INK, step=14, outline=True, inner=True, width=4.5):
        pp = self.P(pts)
        if pattern:
            m = Image.new("L", self.img.size, 0); ImageDraw.Draw(m).polygon(pp, fill=255)
            lay = Image.new("RGBA", self.img.size, fill + (255,)); ld = ImageDraw.Draw(lay); st = max(4, int(step * self.s * self.K))
            xs = [p[0] for p in pp]; ys = [p[1] for p in pp]; x0, x1, y0, y1 = int(min(xs)), int(max(xs)), int(min(ys)), int(max(ys))
            lw2 = max(1, int(2 * self.s * self.K))
            if pattern == "stripes":
                for x in range(x0, x1, st): ld.line([(x, y0), (x, y1)], fill=pcol, width=lw2)
            elif pattern == "hstripes":
                for y in range(y0, y1, st): ld.line([(x0, y), (x1, y)], fill=pcol, width=lw2)
            elif pattern == "diag":
                for x in range(x0 - (y1 - y0), x1, st): ld.line([(x, y0), (x + (y1 - y0), y1)], fill=pcol, width=lw2)
            elif pattern == "dots":
                for y in range(y0, y1, st):
                    for x in range(x0 + ((y - y0) // st % 2) * st // 2, x1, st):
                        r = max(1, int(2.2 * self.s * self.K)); ld.ellipse([x - r, y - r, x + r, y + r], fill=pcol)
            elif pattern == "scales":
                for y in range(y0, y1, st):
                    for x in range(x0 + ((y - y0) // st % 2) * st // 2, x1, st): ld.arc([x - st // 2, y - st // 2, x + st // 2, y + st // 2], 0, 180, fill=pcol, width=lw2)
            elif pattern == "checks":
                for y in range(y0, y1, st):
                    for x in range(x0, x1, st):
                        if ((x - x0) // st + (y - y0) // st) % 2 == 0: ld.rectangle([x, y, x + st // 2, y + st // 2], fill=pcol)
            elif pattern == "waves":
                for y in range(y0, y1, st): ld.line([(x, y + st * 0.25 * math.sin(x / st * 2)) for x in range(x0, x1, max(2, st // 4))], fill=pcol, width=lw2)
            self.img.paste(lay, (0, 0), m)
        else:
            self.d.polygon(pp, fill=fill + (255,))
        if outline:
            self.d.line(pp + [pp[0]], fill=INK + (255,), width=self.lw(width), joint="curve")
            if inner and len(pts) > 2:
                cx = sum(p[0] for p in pts) / len(pts); cy = sum(p[1] for p in pts) / len(pts)
                q = [(cx + (x - cx) * 0.93, cy + (y - cy) * 0.93) for x, y in pts]
                self.d.line(self.P(q + [q[0]]), fill=INK + (200,), width=self.lw(1.6), joint="curve")
    def line(self, pts, col=INK, w=4.0): self.d.line(self.P(pts), fill=col + (255,), width=self.lw(w), joint="curve")
    def circle(self, x, y, r, fill, outline=True, w=4.0):
        (a, b), (c, d_) = self.P([(x - r, y - r), (x + r, y + r)])
        self.d.ellipse([a, b, c, d_], fill=(fill + (255,)) if fill else None, outline=INK + (255,) if outline else None, width=self.lw(w) if outline else 0)
    def arc(self, x, y, rx, ry, a0, a1, col=INK, w=4.0):
        (a, b), (c, d_) = self.P([(x - rx, y - ry), (x + rx, y + ry)]); self.d.arc([a, b, c, d_], a0, a1, fill=col + (255,), width=self.lw(w))
    def done(self): return self.img.resize((self.w, self.h), Image.LANCZOS)


def bez(p0, p1, p2, n=14):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in np.linspace(0, 1, n)]

def flip(pts, f): return [(x * f, y) for x, y in pts]

# ---------------------------------------------------------------- head (profile facing +x when f=1)
def head(p, x, y, f, skin, kind="man", crown=True, crown_col=YEL):
    F = lambda pts: [(x + px * f, y + py) for px, py in pts]
    if kind == "sita":
        p.shape(F([(-70, -40), (-20, -78), (30, -70), (10, 10), (-60, 70), (-95, 40)]), INK, None)    # hair
    elif kind != "hanu":
        p.shape(F([(-62, -30), (-40, -66), (10, -70), (0, 30), (-50, 40)]), INK, None)
    if kind == "hanu":
        face = [(-45, -55), (15, -62), (52, -38), (66, -6), (88, 4), (92, 22), (70, 40), (35, 52), (-5, 55), (-40, 35)]
        p.shape(F(face), HANU, None)
        p.shape(F([(40, 4), (88, 4), (92, 22), (70, 40), (38, 36)]), (245, 200, 150), None, inner=False, width=3)   # muzzle
        p.line(F([(52, 26), (84, 24)]), w=3)
        p.circle(x + 22 * f, y - 20, 13, WHITE, w=3); p.circle(x + 26 * f, y - 20, 7, INK, outline=False)
        p.line(F([(2, -38), (48, -40)]), w=3.5)
        p.circle(x - 30 * f, y - 2, 16, HANU, w=3)                                                             # ear
    else:
        face = [(-40, -62), (20, -68), (48, -44), (54, -24), (82, 4), (60, 10), (66, 20), (56, 26), (62, 34), (44, 52), (6, 60), (-34, 40)]
        p.shape(F(face), skin, None)
        # big fish-shaped Madhubani eye
        eye = [(4, -20), (24, -32), (48, -22), (26, -12)]
        p.shape(F(eye + [(4, -20), (-12, -26)]), WHITE, None, inner=False, width=3)
        p.circle(x + 28 * f, y - 22, 7, INK, outline=False)
        p.line(F([(-2, -40), (26, -46), (52, -36)]), w=3.5)                                              # brow
        p.line(F([(60, 22), (50, 26)]), RED, 4)                                                          # lips
        p.circle(x + 30 * f, y - 52, 5, RED, outline=False)                                             # tilak
        p.arc(x - 12 * f, y + 4, 10, 16, 0, 360, INK, 3)                                                 # ear
        p.circle(x - 12 * f, y + 30, 9, YEL, w=2.5)                                                       # earring
        if kind == "sita":
            p.circle(x + 30 * f, y - 52, 6, RED, outline=False); p.circle(x + 68 * f, y + 12, 7, None, w=2.5)   # bindi, nose ring
    if crown and kind != "sita":
        cr = [(-48, -60), (40, -66), (34, -110), (20, -150), (0, -190), (-20, -150), (-36, -110)]
        p.shape(F(cr), crown_col, "scales", RED, 16)
        for k in range(3): p.circle(x + (-6 + k * 12) * f, y - 92 - k * 22, 7, RED, w=2)
        p.shape(F([(-6, -190), (0, -224), (6, -190)]), RED, None, inner=False, width=3)
    if kind == "sita":
        p.shape(F([(-70, -78), (40, -86), (24, -60), (-80, 20), (-110, 110), (-130, 60)]), RED, "dots", YEL, 16)   # veil
        p.shape(F([(-30, -84), (20, -88), (10, -112), (-20, -112)]), YEL, None, inner=False, width=3)              # tikka crown

# ---------------------------------------------------------------- full figure
def figure(kind, f=1, h=900, pose="stand"):
    """returns RGBA sprite, ground at bottom centre. kind: ram, lakshman, sita, hanuman, ravana"""
    s = h / 900; W_, H_ = int(760 * s), int(1100 * s)
    p = Pen(W_, H_, W_ / 2 / s * 1.0 if False else 380, 1060, s)
    p.ox, p.oy = 380, 1060   # local origin at feet centre (in unscaled units → Pen handles scale)
    p.ox, p.oy = 380 * s, 1060 * s
    F = lambda pts: [(px * f, py) for px, py in pts]
    skin = dict(ram=RAMBLUE, lakshman=SKIN, sita=SKIN, hanuman=HANU, ravana=(90, 60, 110))[kind]
    seated = pose == "seated"
    if kind == "hanuman":   # tail behind
        tail = bez((-60, -380), (-260, -300), (-230, -620), 18) + [(-200, -640)] + list(reversed(bez((-80, -390), (-225, -320), (-205, -610), 18)))
        p.shape(F(tail), HANU, "hstripes", MAROON, 16, inner=False)
    if seated:
        p.shape(F([(-150, 0), (170, 0), (150, -150), (-120, -160)]), RED if kind == "ram" else YEL, "stripes", INK, 18)   # lap/dhoti seated
        p.shape(F([(120, -20), (210, -20), (200, 0), (110, 0)]), skin, None)                                                # foot
        top = -160
    else:
        # legs + dhoti
        dcol = dict(ram=YEL, lakshman=RED, sita=RED, hanuman=RED, ravana=MAROON)[kind]
        if kind == "sita":
            p.shape(F([(-120, 0), (130, 0), (80, -420), (-70, -420)]), RED, "dots", YEL, 18)
            p.shape(F([(-120, 0), (130, 0), (126, -40), (-116, -40)]), YEL, "checks", RED, 14)
            p.shape(F([(40, 0), (130, 0), (126, -24), (40, -24)]), SKIN, None, inner=False, width=3)
        else:
            p.shape(F([(-30, 0), (-60, -260), (-20, -260), (0, 0)]), skin, None, inner=False)
            p.shape(F([(10, 0), (40, -260), (80, -260), (40, 0)]), skin, None, inner=False)
            for fx in (-15, 25): p.shape(F([(fx, 0), (fx + 70, 0), (fx + 66, -18), (fx, -26)]), skin, None, inner=False, width=3)
            p.shape(F([(-90, -150), (110, -150), (80, -430), (-70, -430)]), dcol, "stripes" if kind != "hanuman" else "diag", INK if kind != "ravana" else YEL, 18)
            p.shape(F([(-90, -150), (110, -150), (108, -180), (-88, -180)]), YEL if dcol != YEL else RED, "checks", INK, 12)
        top = -420
    # torso
    T = top
    torso = [(-80, T), (90, T), (110, T - 260), (60, T - 300), (-60, T - 300), (-100, T - 260)]
    p.shape(F(torso), skin, None)
    if kind == "sita":
        p.shape(F([(-80, T), (90, T), (100, T - 200), (-90, T - 210)]), RED, "dots", YEL, 16)
        p.shape(F([(-100, T - 260), (60, T - 300), (110, T - 200), (-40, T - 60), (-90, T - 40)]), YEL, "diag", RED, 16)   # pallu
    else:
        p.arc(0, T - 230, 70, 60, 20, 160, YEL, 9); p.arc(0, T - 220, 54, 66, 20, 160, RED, 5)      # necklaces
        p.line(F([(-70, T - 270), (80, T - 30)]), WHITE, 4)                                            # sacred thread
        p.shape(F([(-80, T - 10), (90, T - 10), (92, T + 20), (-82, T + 20)]), YEL, "checks", RED, 12)  # belt
    # arms
    def arm(sx, sy, ex, ey, hx, hy, col=skin):
        p.line(F([(sx, sy), (ex, ey), (hx, hy)]), INK, 34); p.line(F([(sx, sy), (ex, ey), (hx, hy)]), col, 26)
        p.circle(hx * f, hy, 18, col, w=3.5); mx, my = (ex + hx) / 2, (ey + hy) / 2
        for k in range(3): p.circle((mx + (hx - ex) * 0.12 * k) * f, my + (hy - ey) * 0.12 * k, 13, YEL, w=2)
    if kind in ("ram", "lakshman") and not seated:
        arm(-70, T - 270, -110, T - 130, -60, T - 40)
        arm(90, T - 270, 170, T - 180, 220, T - 260)
        # bow held upright in the front hand
        bow = bez((150, T - 560), (290, T - 260), (150, T + 40), 22)
        p.line(F(bow), INK, 16); p.line(F(bow), (150, 80, 35), 10); p.line(F([bow[0], bow[-1]]), INK, 3)
        p.shape(F([(-120, T - 310), (-80, T - 330), (-40, T - 60), (-80, T - 40)]), MAROON, "hstripes", YEL, 14)   # quiver
        for k in range(4): p.line(F([(-100 + k * 10, T - 320), (-110 + k * 10, T - 380)]), INK, 4)
    elif kind == "sita":
        arm(-70, T - 260, -60, T - 140, 20, T - 120); arm(80, T - 260, 120, T - 150, 40, T - 120)
        for k in range(5):   # lotus held
            a = -math.pi / 2 + (k - 2) * 0.45
            p.shape(F([(30, T - 130), (30 + 50 * math.cos(a - 0.25), T - 130 + 50 * math.sin(a - 0.25)), (30 + 70 * math.cos(a), T - 130 + 70 * math.sin(a)), (30 + 50 * math.cos(a + 0.25), T - 130 + 50 * math.sin(a + 0.25))]), PINK, None, inner=False, width=3)
    elif kind == "hanuman":
        mace = [(170, T + 60), (170, T - 420)]
        p.line(F(mace), INK, 22); p.line(F(mace), YEL, 15); p.circle(170 * f, T - 460, 58, YEL); p.circle(170 * f, T - 460, 28, RED, w=3)
        for k in range(8):
            a = k * math.pi / 4; p.circle((170 + 62 * math.cos(a)) * f, T - 460 + 62 * math.sin(a), 9, RED, w=2)
        arm(-70, T - 270, -40, T - 140, 30, T - 160)
        arm(90, T - 270, 150, T - 170, 170, T - 120)
    elif kind == "ravana":
        for side in (-1, 1):
            for k in range(5):   # many arms fanned on both sides
                a = math.radians(-30 + k * 28); ex, ey = side * (150 + 170 * math.cos(a)), T - 230 - 170 * math.sin(a)
                p.line([(side * 90, T - 240), (ex, ey)], INK, 30); p.line([(side * 90, T - 240), (ex, ey)], skin, 22); p.circle(ex, ey, 20, skin, w=3)
                if k == 2: p.line([(ex, ey + 60), (ex, ey - 120)], INK, 10); p.shape([(ex - 18, ey - 120), (ex, ey - 170), (ex + 18, ey - 120)], (200, 200, 210), None, inner=False, width=3)
    elif seated:
        arm(-70, T - 270, -100, T - 140, -40, T - 90); arm(90, T - 270, 150, T - 150, 120, T - 300)   # blessing hand
    # head(s)
    hy = T - 360
    if kind in ("ram", "sita", "lakshman", "hanuman"):   # golden halo behind the head
        p.circle(0, hy - 30, 150, YEL, w=5); p.circle(0, hy - 30, 128, ORA, w=3)
        for k in range(24):
            a = k * math.pi / 12; p.circle(139 * math.cos(a), hy - 30 + 139 * math.sin(a), 6, RED, outline=False)
    if kind == "ravana":
        for k in range(-4, 6):
            head(p, k * 64 * f, hy + abs(k - 0.5) * 6, f, skin, "man", crown=True, crown_col=YEL)
    else:
        head(p, 0, hy, f, skin, dict(ram="man", lakshman="man", sita="sita", hanuman="hanu")[kind], crown=True)
    return p.done()


def diya(p, x, y, sc=1.0, flame=1.0, t=0.0):
    p.shape([(x - 60 * sc, y), (x + 60 * sc, y), (x + 36 * sc, y + 34 * sc), (x - 36 * sc, y + 34 * sc)], ORA, "hstripes", RED, 9)
    p.shape([(x - 66 * sc, y - 6 * sc), (x + 66 * sc, y - 6 * sc), (x + 60 * sc, y + 4 * sc), (x - 60 * sc, y + 4 * sc)], YEL, None, inner=False, width=3)
    if flame > 0:
        wob = 6 * math.sin(t * 9 + x)
        fl = [(x - 18 * sc * flame, y - 10 * sc), (x + wob * sc, y - 90 * sc * flame), (x + 18 * sc * flame, y - 10 * sc)]
        p.shape(fl, YEL, None, inner=False, width=3); p.shape([(x - 8 * sc, y - 12 * sc), (x + wob * 0.5 * sc, y - 50 * sc * flame), (x + 8 * sc, y - 12 * sc)], RED, None, outline=False)

def fish(p, x, y, sc=1.0, f=1):
    body = [(x - 70 * sc * f, y), (x - 10 * sc * f, y - 34 * sc), (x + 50 * sc * f, y), (x - 10 * sc * f, y + 34 * sc)]
    p.shape(body, YEL, "scales", RED, 12); p.shape([(x + 46 * sc * f, y), (x + 90 * sc * f, y - 30 * sc), (x + 90 * sc * f, y + 30 * sc)], RED, None)
    p.circle(x - 46 * sc * f, y - 6 * sc, 7 * sc, WHITE, w=2); p.circle(x - 46 * sc * f, y - 6 * sc, 3 * sc, INK, outline=False)

def peacock(p, x, y, sc=1.0, f=1):
    R = 260 * sc; ths = [-0.25 + k * 0.17 for k in range(12)]
    fan = [(x - 30 * sc * f, y)] + [(x - 30 * sc * f - f * R * math.cos(t), y - R * math.sin(t)) for t in ths]
    p.shape(fan, GRN, "diag", LGRN, 16)
    for t in ths:
        ex, ey = x - 30 * sc * f - f * R * math.cos(t), y - R * math.sin(t)
        p.line([(x - 30 * sc * f, y), (ex, ey)], INK, 3)
        p.circle(ex, ey, 26 * sc, BLU, w=3); p.circle(ex, ey, 14 * sc, YEL, outline=False); p.circle(ex, ey, 6 * sc, INK, outline=False)
    body = [(x - 70 * sc * f, y + 10 * sc), (x - 20 * sc * f, y - 50 * sc), (x + 50 * sc * f, y - 60 * sc), (x + 80 * sc * f, y - 10 * sc), (x + 40 * sc * f, y + 40 * sc), (x - 30 * sc * f, y + 45 * sc)]
    p.shape(body, BLU, "scales", SKY, 14)
    neck = [(x + 40 * sc * f, y - 50 * sc), (x + 70 * sc * f, y - 170 * sc), (x + 100 * sc * f, y - 170 * sc), (x + 80 * sc * f, y - 20 * sc)]
    p.shape(neck, BLU, "dots", SKY, 10)
    p.circle(x + 88 * sc * f, y - 182 * sc, 22 * sc, BLU, w=3); p.circle(x + 94 * sc * f, y - 186 * sc, 5 * sc, WHITE, outline=False)
    p.shape([(x + 106 * sc * f, y - 190 * sc), (x + 140 * sc * f, y - 180 * sc), (x + 106 * sc * f, y - 172 * sc)], YEL, None, inner=False, width=2)
    for k in range(3):
        tx, ty = x + (80 + k * 8) * sc * f, y - 228 * sc
        p.line([(x + 88 * sc * f, y - 202 * sc), (tx, ty)], INK, 3); p.circle(tx, ty, 6 * sc, BLU, outline=False)
    for dx in (-10, 30):
        p.line([(x + dx * sc * f, y + 42 * sc), (x + dx * sc * f, y + 110 * sc)], INK, 5)
        for a in (-0.6, 0, 0.6): p.line([(x + dx * sc * f, y + 110 * sc), (x + dx * sc * f + 26 * sc * math.sin(a), y + 110 * sc + 16 * sc * math.cos(a))], INK, 4)

def tree(p, x, y, sc=1.0):
    p.shape([(x - 22 * sc, y), (x + 22 * sc, y), (x + 14 * sc, y - 300 * sc), (x - 14 * sc, y - 300 * sc)], (120, 60, 30), "hstripes", INK, 14)
    for k in range(9):
        a = -math.pi / 2 + (k - 4) * 0.36; cx, cy = x + 150 * sc * math.cos(a), y - 300 * sc + 150 * sc * math.sin(a)
        lf = [(cx - 50 * sc, cy), (cx, cy - 34 * sc), (cx + 50 * sc, cy), (cx, cy + 34 * sc)]
        p.shape(lf, GRN if k % 2 else LGRN, "diag", INK, 10)
