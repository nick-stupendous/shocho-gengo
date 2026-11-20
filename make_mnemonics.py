"""python make_mnemonics.py [--sheet]  -> glyphs/chains/<char>.json  (+ previews/sheet_N.png)"""
import json, sys, importlib
from pathlib import Path
ROOT = Path(__file__).resolve().parent
MODULES = ["mn_n5"]

def flat(strokes):
    out = []
    for s in strokes:
        if s and isinstance(s[0][0], list): out += flat(s)
        else: out.append(s)
    return out          # add mn_n4, mn_kana ... here

def build():
    out = ROOT / "glyphs/chains"; out.mkdir(parents=True, exist_ok=True)
    allS = {}
    for m in MODULES: allS.update(importlib.import_module(m).S)
    for ch, (kind, note, strokes) in list(allS.items()):
        strokes = flat(strokes); allS[ch] = (kind, note, strokes)
        for st in strokes: assert len(st) >= 2 and all(0 <= v <= 100 for p in st for v in p), (ch, "out of box")
        tag = "pictograph-based" if kind == "pictograph" else "invented mnemonic, NOT etymology"
        (out / f"{ch}.json").write_text(json.dumps([{"label": f"{ch} scene", "strokes": strokes,
            "provenance": "designed", "note": f"[{tag}] {note}"}], ensure_ascii=False), encoding="utf-8")
    print(len(allS), "scenes written to glyphs/chains/")
    return allS

def sheet(allS, per=50, cols=10, cell=150):
    from PIL import Image, ImageDraw, ImageFont
    (ROOT / "previews").mkdir(exist_ok=True)
    try: font = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 18)
    except Exception: font = None
    items = list(allS.items())
    for n in range(0, len(items), per):
        part = items[n:n+per]; rows = (len(part) + cols - 1) // cols
        im = Image.new("RGB", (cols*cell, rows*cell), "white"); d = ImageDraw.Draw(im)
        for i, (ch, (kind, note, strokes)) in enumerate(part):
            ox, oy = (i % cols)*cell, (i // cols)*cell
            d.rectangle([ox, oy, ox+cell-1, oy+cell-1], outline="#ddd")
            k = (cell-40)/100; col = "#222" if kind == "pictograph" else "#b8620a"
            for st in strokes:
                d.line([(ox+20+x*k, oy+8+y*k) for x, y in st], fill=col, width=2, joint="curve")
            d.text((ox+4, oy+cell-24), ch, fill="#06c", font=font)
        im.save(ROOT / f"previews/sheet_{n//per+1}.png")
    print("sheets saved in previews/")

if __name__ == "__main__":
    a = build()
    if "--sheet" in sys.argv: sheet(a)
