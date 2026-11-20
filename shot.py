"""Render library screens to PNG without Tk:  python3 shot.py   (needs Pillow)"""
import sys
from PIL import Image, ImageDraw, ImageFont
import library as L

FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-%s.ttc"
class PilGfx:
    def __init__(s):
        s.im = Image.new("RGBA", (L.W, L.H), "#000"); s.d = ImageDraw.Draw(s.im); s.fonts = {}
    def F(s, size, bold):
        k = (int(size), bold)
        if k not in s.fonts: s.fonts[k] = ImageFont.truetype(FONT % ("Bold" if bold else "Regular"), k[0])
        return s.fonts[k]
    def rect(s, x0, y0, x1, y1, fill="", outline="", w=1): s.d.rectangle([x0, y0, x1, y1], fill=fill or None, outline=outline or None, width=int(w))
    def oval(s, x0, y0, x1, y1, fill="", outline="", w=1): s.d.ellipse([x0, y0, x1, y1], fill=fill or None, outline=outline or None, width=int(w))
    def line(s, pts, fill, w=1): s.d.line(pts, fill=fill, width=int(w), joint="curve")
    def text(s, x, y, t, fill, size, bold=False, anchor="c"):
        s.d.text((x, y), t, fill=fill, font=s.F(size, bold), anchor={"c": "mm", "l": "lm", "r": "rm"}[anchor])
    def _ov(s, box, col, ell=False):
        ov = Image.new("RGBA", s.im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        (d.ellipse if ell else d.rectangle)(box, fill=col); s.im.alpha_composite(ov); s.d = ImageDraw.Draw(s.im)
    def dim(s, x0, y0, x1, y1): s._ov([x0, y0, x1, y1], (0, 0, 0, 140))
    def glow(s, cx, cy, rx, ry): s._ov([cx - rx, cy - ry, cx + rx, cy + ry], (255, 243, 176, 90), True)
    def strokes(s, u, x0, y0, x1, y1, col, w):
        k = min((x1 - x0) / max(u["w"], 1), (y1 - y0) / max(u["h"], 1))
        ox = x0 + ((x1 - x0) - u["w"] * k) / 2; oy = y0 + ((y1 - y0) - u["h"] * k) / 2
        for st in u["s"]:
            if len(st) > 1: s.line([(ox + x * k, oy + y * k) for x, y in st], col, w)

def snap(lib, name):
    g = PilGfx(); lib.draw(g); g.im.convert("RGB").save(f"{name}.png")

if __name__ == "__main__":
    lib = L.Lib(); snap(lib, "lib_1_start")
    for _ in range(4): lib.key("Down", 0)
    for _ in range(3): lib.key("Right", 0)
    snap(lib, "lib_2_kanji"); lib.key("Tab", 0); snap(lib, "lib_3_inspect"); lib.key("Tab", 0)
    lib.key("Enter", 0); lib.service(); lib.key("Tab", 0); snap(lib, "lib_4_view")
