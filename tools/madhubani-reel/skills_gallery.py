import math, random, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
import styles as S
TW, TH = 360, 640
GF = S.GF
def font(sz, bold=True): return ImageFont.truetype(GF + ("mukta/Mukta-ExtraBold.ttf" if bold else "mukta/Mukta-Regular.ttf"), sz)
REPO = "/home/claude/katha-deep/assets/posters/"
HAN = S.pad(S.HANU)
def han_mask(h=380):
    m = HAN.getchannel("A"); r = h / m.height; return m.resize((int(m.width * r), h), Image.LANCZOS)
def cover(path):
    im = Image.open(path).convert("RGB"); r = max(TW / im.width, TH / im.height)
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS); x, y = (im.width - TW) // 2, (im.height - TH) // 2
    return im.crop((x, y, x + TW, y + TH))
def frame(fn, t=3.2): return fn(t).convert("RGB").resize((TW, TH), Image.LANCZOS)
def paste_mask(c, m, col, x, y):
    c.paste(Image.new("RGB", m.size, col), (x, y), m)

def isometric():
    c = Image.new("RGB", (TW, TH), (238, 242, 248)); d = ImageDraw.Draw(c)
    def cube(x, y, s, h, col):
        top = [(x, y - h), (x + s, y - h - s / 2), (x + 2 * s, y - h), (x + s, y - h + s / 2)]
        d.polygon(top, fill=col); d.polygon([(x, y - h), (x + s, y - h + s / 2), (x + s, y + s / 2), (x, y)], fill=tuple(int(v * .75) for v in col))
        d.polygon([(x + s, y - h + s / 2), (x + 2 * s, y - h), (x + 2 * s, y), (x + s, y + s / 2)], fill=tuple(int(v * .55) for v in col))
    for i, (x, y, h, col) in enumerate([(60, 470, 60, (120, 170, 250)), (150, 430, 140, (250, 150, 90)), (110, 520, 30, (130, 210, 160)), (200, 500, 90, (240, 200, 90))]): cube(x, y, 45, h, col)
    return c
def papercut():
    c = Image.new("RGB", (TW, TH), (255, 236, 200)); d = ImageDraw.Draw(c)
    for k, col in enumerate([(250, 200, 140), (240, 160, 100), (200, 110, 80), (140, 70, 70), (70, 40, 60)]):
        base = 300 + k * 75; pts = [(0, TH)] + [(x, base + 30 * math.sin(x / 50 + k)) for x in range(0, TW + 10, 10)] + [(TW, TH)]
        sh = [(x, y + 8) for x, y in pts]; d.polygon(sh, fill=(0, 0, 0)); d.polygon(pts, fill=col)
    c = c.filter(ImageFilter.SMOOTH); return c
def datachart():
    c = Image.new("RGB", (TW, TH), (16, 20, 34)); d = ImageDraw.Draw(c)
    for i, h in enumerate([120, 200, 160, 290, 230]):
        x = 40 + i * 60; y = 520; col = (90 + i * 30, 160, 255 - i * 30)
        d.polygon([(x, y), (x + 36, y), (x + 36, y - h), (x, y - h)], fill=col); d.polygon([(x + 36, y), (x + 50, y - 10), (x + 50, y - h - 10), (x + 36, y - h)], fill=tuple(v // 2 for v in col))
        d.polygon([(x, y - h), (x + 36, y - h), (x + 50, y - h - 10), (x + 14, y - h - 10)], fill=tuple(min(255, v + 40) for v in col))
    return c
def synthwave():
    c = Image.new("RGB", (TW, TH)); a = np.zeros((TH, TW, 3)); y = np.linspace(0, 1, TH)[:, None]
    a[:] = (np.array([20, 0, 50]) * (1 - y) + np.array([255, 60, 140]) * y)[:, None, :][:, 0][:, None, :]
    c = Image.fromarray(a.astype(np.uint8)); d = ImageDraw.Draw(c)
    d.ellipse([90, 180, 270, 360], fill=(255, 200, 60))
    for k in range(6): d.rectangle([80, 290 + k * 12, 280, 294 + k * 12], fill=(255, 60, 140))
    d.rectangle([0, 370, TW, TH], fill=(20, 0, 40))
    for k in range(12): yy = 370 + (k ** 1.7) * 3; d.line([(0, yy), (TW, yy)], fill=(0, 230, 255), width=2)
    for k in range(-8, 9): d.line([(180, 370), (180 + k * 70, TH)], fill=(0, 230, 255), width=2)
    return c
def explainer3d():
    yy, xx = np.mgrid[0:TH, 0:TW]; c = np.zeros((TH, TW, 3)) + np.array([235, 240, 245])
    r = np.sqrt((xx - 180) ** 2 + (yy - 330) ** 2); m = r < 120
    nz = np.sqrt(np.clip(1 - (r / 120) ** 2, 0, 1)); l = np.clip(((-(xx - 180) - (yy - 330)) / 120 * 0.5 + nz) * 0.8, 0.15, 1)
    c[m] = (np.array([80, 140, 255]) * l[..., None])[m]
    sh = ((xx - 200) / 120) ** 2 + ((yy - 480) / 25) ** 2 < 1; c[sh & ~m] = [190, 195, 205]
    return Image.fromarray(c.astype(np.uint8))
def maths():
    c = Image.new("RGB", (TW, TH), (252, 252, 245)); d = ImageDraw.Draw(c)
    for x in range(0, TW, 20): d.line([(x, 0), (x, TH)], fill=(210, 225, 240))
    for y in range(0, TH, 20): d.line([(0, y), (TW, y)], fill=(210, 225, 240))
    d.line([(30, 320), (330, 320)], fill=(30, 30, 30), width=3); d.line([(180, 120), (180, 520)], fill=(30, 30, 30), width=3)
    d.line([(x, 320 - 110 * math.sin((x - 30) / 40)) for x in range(30, 330, 3)], fill=(220, 50, 50), width=4)
    d.text((60, 140), "y = sin x", font=font(34), fill=(30, 30, 30)); return c
def cartoon():
    c = Image.new("RGB", (TW, TH), (120, 210, 250)); d = ImageDraw.Draw(c)
    d.ellipse([60, 420, 300, 700], fill=(110, 200, 90)); d.ellipse([100, 200, 260, 380], fill=(255, 190, 60), outline=(30, 30, 30), width=6)
    for x in (150, 210): d.ellipse([x - 16, 260, x + 16, 300], fill=(255, 255, 255), outline=(30, 30, 30), width=4); d.ellipse([x - 6, 274, x + 6, 290], fill=(30, 30, 30))
    d.arc([140, 290, 220, 350], 20, 160, fill=(30, 30, 30), width=5); return c
def domino():
    c = Image.new("RGB", (TW, TH), (245, 235, 220)); d = ImageDraw.Draw(c)
    for i in range(7):
        x = 30 + i * 46; ang = max(0, min(70, (5 - i) * 20)); im = Image.new("RGBA", (40, 120), (0, 0, 0, 0)); dd = ImageDraw.Draw(im)
        dd.rounded_rectangle([0, 0, 39, 119], 6, fill=(30, 30, 30)); dd.line([(4, 60), (36, 60)], fill=(240, 240, 240), width=3)
        for p in ((20, 30), (20, 90)): dd.ellipse([p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5], fill=(240, 240, 240))
        im = im.rotate(-ang, expand=True, resample=Image.BICUBIC); c.paste(im, (x, 460 - im.height), im)
    d.line([(0, 460), (TW, 460)], fill=(120, 90, 60), width=4); return c
def glowatom():
    a = np.zeros((TH, TW, 3)); yy, xx = np.mgrid[0:TH, 0:TW]
    im = Image.new("L", (TW, TH)); d = ImageDraw.Draw(im)
    for k in range(3):
        e = Image.new("L", (TW, TH)); ed = ImageDraw.Draw(e); ed.ellipse([40, 280, 320, 380], outline=255, width=4); im = Image.fromarray(np.maximum(np.asarray(im), np.asarray(e.rotate(k * 60, center=(180, 330)))))
    g = np.asarray(im.filter(ImageFilter.GaussianBlur(6))).astype(float) * 2.5 + np.asarray(im)
    core = np.exp(-(((xx - 180) ** 2 + (yy - 330) ** 2) / 600)) * 255
    a[..., 0] = g * 0.3 + core; a[..., 1] = g * 0.8 + core * 0.8; a[..., 2] = g + core
    return Image.fromarray(np.clip(a + np.array([8, 6, 20]), 0, 255).astype(np.uint8))
def pixel():
    c = frame(S.s_madhubani, 3.0); return c.resize((45, 80), Image.BILINEAR).quantize(16).convert("RGB").resize((TW, TH), Image.NEAREST)
def lowpoly():
    c = Image.new("RGB", (TW, TH), (180, 215, 240)); d = ImageDraw.Draw(c); r = random.Random(3)
    pts = [(0, 520), (60, 380), (120, 300), (180, 200), (240, 290), (300, 360), (360, 470)]
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]; m = ((a[0] + b[0]) / 2, 600)
        for tri in ((a, b, m),): sh = r.randint(-25, 25); d.polygon(tri, fill=(90 + sh, 140 + sh, 90 + sh))
    d.polygon([(150, 240), (180, 200), (210, 245)], fill=(250, 250, 250)); d.rectangle([0, 560, TW, TH], fill=(80, 120, 70)); return c
def riso():
    c = Image.new("RGB", (TW, TH), (245, 238, 225)); m = han_mask(420)
    def halftone(col, off, scale):
        lay = Image.new("L", (TW, TH)); dd = ImageDraw.Draw(lay); mm = np.asarray(m)
        for y in range(0, m.height, 8):
            for x in range(0, m.width, 8):
                if mm[y, x] > 128: rr = 3.2 * scale; dd.ellipse([x + 20 + off - rr, y + 120 + off - rr, x + 20 + off + rr, y + 120 + off + rr], fill=255)
        return lay
    a = np.asarray(c).astype(float)
    for col, off, sc in (((255, 80, 120), 0, 1.0), ((40, 90, 200), 6, 0.8)):
        l = np.asarray(halftone(col, off, sc)).astype(float)[..., None] / 255; a = a * (1 - l) + a * (np.array(col) / 255) * l
    return Image.fromarray(a.astype(np.uint8))
def hologram():
    c = Image.new("RGB", (TW, TH), (2, 10, 22)); m = han_mask(420); g = Image.new("RGB", m.size, (60, 230, 255))
    c.paste(g, (20, 110), m.point(lambda v: v * 0.6)); c = Image.blend(c, c.filter(ImageFilter.GaussianBlur(8)), 0.5); d = ImageDraw.Draw(c)
    for y in range(0, TH, 4): d.line([(0, y), (TW, y)], fill=(0, 0, 0))
    d.ellipse([60, 520, 300, 570], outline=(60, 230, 255), width=3); return c
def cyberpunk():
    c = Image.new("RGB", (TW, TH), (12, 6, 26)); d = ImageDraw.Draw(c); r = random.Random(4)
    for i in range(9):
        x = i * 42; h = r.randint(180, 420); d.rectangle([x, TH - h, x + 38, TH], fill=(24, 14, 48))
        for y in range(TH - h + 10, TH, 18):
            for xx in range(x + 6, x + 34, 10):
                if r.random() < 0.4: d.rectangle([xx, y, xx + 4, y + 6], fill=r.choice([(255, 40, 160), (0, 240, 255), (255, 220, 60)]))
    d.text((40, 120), "NEON", font=font(90), fill=(255, 40, 160)); return c
def blueprint():
    c = Image.new("RGB", (TW, TH), (20, 70, 150)); d = ImageDraw.Draw(c)
    for x in range(0, TW, 24): d.line([(x, 0), (x, TH)], fill=(40, 95, 175))
    for y in range(0, TH, 24): d.line([(0, y), (TW, y)], fill=(40, 95, 175))
    m = han_mask(420); e = m.filter(ImageFilter.FIND_EDGES).point(lambda v: 255 if v > 40 else 0)
    c.paste(Image.new("RGB", m.size, (235, 245, 255)), (20, 110), e); d.line([(30, 560), (330, 560)], fill=(235, 245, 255), width=2); return c
def thermal():
    m = np.asarray(han_mask(420).filter(ImageFilter.GaussianBlur(14))).astype(float) / 255
    v = np.zeros((TH, TW)); v[110:110 + m.shape[0], 20:20 + m.shape[1]] = m[:, :TW - 20]
    v = v * 0.9 + 0.08
    cmap = np.array([[10, 0, 40], [90, 0, 140], [220, 30, 60], [255, 160, 0], [255, 255, 200]], float)
    idx = v * 4; i0 = np.clip(idx.astype(int), 0, 3); f = (idx - i0)[..., None]
    return Image.fromarray((cmap[i0] * (1 - f) + cmap[i0 + 1] * f).astype(np.uint8))
def ascii_():
    c = Image.new("RGB", (TW, TH), (6, 14, 6)); d = ImageDraw.Draw(c); m = np.asarray(han_mask(460).resize((36, 46))).astype(int)
    f = ImageFont.truetype(GF + "spacemono/SpaceMono-Regular.ttf", 13) if os.path.exists(GF + "spacemono/SpaceMono-Regular.ttf") else font(12)
    chars = " .:-=+*#%@"
    for y in range(m.shape[0]):
        row = "".join(chars[min(9, m[y, x] * 10 // 256)] for x in range(m.shape[1])); d.text((20, 100 + y * 10), row, font=f, fill=(80, 255, 120))
    return c
def watercolor():
    c = frame(S.s_madhubani, 3.0).filter(ImageFilter.GaussianBlur(5)); a = np.asarray(c).astype(float)
    a = a * 0.7 + 255 * 0.3; n = np.random.default_rng(1).normal(0, 12, a.shape[:2])[..., None]
    return Image.fromarray(np.clip(a + n, 0, 255).astype(np.uint8)).filter(ImageFilter.SMOOTH_MORE)
def needs_images(kind):
    c = Image.new("RGB", (TW, TH), (40, 34, 30)); d = ImageDraw.Draw(c)
    d.rounded_rectangle([40, 150, 320, 390], 20, outline=(200, 180, 140), width=4)
    d.polygon([(70, 360), (150, 250), (210, 320), (250, 280), (300, 360)], fill=(120, 105, 85)); d.ellipse([240, 180, 280, 220], fill=(200, 180, 140))
    for i, line in enumerate(["Uses your", "ChatGPT images", kind]): d.text((40, 410 + i * 40), line, font=font(30), fill=(230, 215, 190))
    return c

TILES = [  # (number, skill, look, image)
    (1, "madhubani-reel-maker", "Madhubani", lambda: cover(REPO + "diwali-madhubani-ram-katha.jpg")),
    (2, "comic-reel-maker", "Comic book", lambda: frame(S.s_comic)),
    (3, "stone-relief-reel-maker", "Temple stone", lambda: frame(S.s_stone)),
    (4, "devotional-reel-maker", "Shadow puppet", lambda: cover(REPO + "ekalavya-guru-dakshina.jpg")),
    (5, "mythic-reel-storyteller", "Storyteller", lambda: cover(REPO + "prahlad-narasimha.jpg")),
    (6, "god-reel-explainer", "Collage explainer", lambda: cover("/mnt/user-data/uploads/Reels/07_Vamana/05.png")),
    (7, "cinematic-epic-reel", "Cinematic epic", lambda: needs_images("photoreal epic")),
    (8, "ai-image-styles-pack", "Clay / Brick / Anime", lambda: needs_images("clay, brick, anime")),
    (9, "remotion-reels", "Kinetic text", lambda: frame(S.s_kinetic)),
    (10, "code-animation-styles", "Isometric", isometric), (11, "code-animation-styles", "Paper-Cut", papercut),
    (12, "code-animation-styles", "3D Data Chart", datachart), (13, "code-animation-styles", "Synthwave", synthwave),
    (14, "code-animation-styles", "3D Explainer", explainer3d), (15, "code-animation-styles", "Maths Diagram", maths),
    (16, "code-animation-styles", "Cartoon", cartoon), (17, "code-animation-styles", "Domino Reveal", domino),
    (18, "code-animation-styles", "Glow Atom", glowatom), (19, "code-animation-styles-plus", "Pixel Art", pixel),
    (20, "code-animation-styles-plus", "Low-Poly 3D", lowpoly), (21, "code-animation-styles-plus", "Risograph", riso),
    (22, "code-animation-styles-fx", "Hologram", hologram), (23, "code-animation-styles-fx", "Cyberpunk Neon", cyberpunk),
    (24, "code-animation-styles-fx", "Blueprint", blueprint), (25, "code-animation-styles-fx", "Thermal Cam", thermal),
    (26, "code-animation-styles-fx", "ASCII Terminal", ascii_), (27, "code-animation-styles-fx", "Watercolor", watercolor)]

def tile(n, skill, look, fn):
    im = fn().convert("RGB"); d = ImageDraw.Draw(im)
    d.rectangle([0, TH - 110, TW, TH], fill=(15, 12, 10)); d.text((16, TH - 104), f"{n}. {look}", font=font(36), fill=(255, 230, 160))
    d.text((16, TH - 50), skill, font=font(22, False), fill=(200, 200, 200)); return im

if __name__ == "__main__":
    os.makedirs("gallery", exist_ok=True); ims = []
    for n, s, l, fn in TILES:
        im = tile(n, s, l, fn); im.save(f"gallery/{n:02d}.jpg", quality=88); ims.append(im)
    cols = 6; rows = math.ceil(len(ims) / cols); G = Image.new("RGB", (cols * TW + (cols + 1) * 12, rows * TH + (rows + 1) * 12 + 120), (25, 20, 18))
    d = ImageDraw.Draw(G); d.text((24, 26), "Your video styles — pick a number", font=font(70), fill=(255, 230, 160))
    for i, im in enumerate(ims): G.paste(im, (12 + (i % cols) * (TW + 12), 132 + (i // cols) * (TH + 12)))
    G.save("skills_gallery.jpg", quality=86); G.resize((G.width // 2, G.height // 2)).save("skills_gallery_small.jpg", quality=85)
