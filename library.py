"""Library browser for Japanese-Epiphany.   python3 library.py        (Tk window)
                                           python3 library.py cli    (terminal)

Only these keys do anything:
  Left / Right   browse along a shelf  (in the viewer: previous / next stage)
  Up / Down      change shelf          (in the viewer: previous / next item on the shelf)
  Enter          open the selected book (in the viewer: next stage)
  Shift          go back               (terminal: Shift+Tab, terminals cannot see Shift alone)
  Esc            go back;  Esc twice quickly = exit
  Tab            inspect (provenance, note, confidence)
"""
import sys, os, json, time, textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import resolver as R
try:
    import symbolism as SY           # etymology -> language -> symbol chains for single characters
except Exception:
    SY = None

try:
    from app import COL
except Exception:
    COL = {"authored": "#2e9e4f", "composed": "#2f6fd1", "traced": "#888888",
           "designed": "#d98a1c", "placeholder": "#cc3333"}

W, H = 1280, 720
DOUBLE_ESC = 1.2
HELP = "←→ browse    ↑↓ shelf    Enter open    Tab inspect    Shift / Esc back    Esc Esc exit"
HELP_VIEW = "←→ stage    ↑↓ prev / next book    Enter next stage    Tab inspect    Shift / Esc back    Esc Esc exit"


# ------------------------------------------------------------------ data
def _json(p, default):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception: return default

def build_shelves():
    S = []
    def add(name, items, color):
        items = [i for i in items if i["label"]]
        if items: S.append({"name": name, "items": items, "color": color})
    hira = [chr(c) for c in range(0x3042, 0x3094) if chr(c) not in "ぁぃぅぇぉっゃゅょゎゐゑ"]
    kata = [chr(c) for c in range(0x30A2, 0x30F4) if chr(c) not in "ァィゥェォッャュョヮヰヱ"]
    add("Hiragana", [{"label": c, "key": c} for c in hira], "#8c3b4a")
    add("Katakana", [{"label": c, "key": c} for c in kata], "#3b5f8c")
    add("Latin letters", [{"label": c, "key": c} for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"], "#4a7a4a")
    try:
        from tables import PARTICLES
        add("Particles", [{"label": p, "key": p} for p in PARTICLES], "#7a5a2a")
    except Exception:
        pass
    n5 = sorted(f.stem for f in (ROOT / "glyphs/chains").glob("*.json") if len(f.stem) == 1 and "\u4e00" <= f.stem <= "\u9fff")
    add("Kanji N5", [{"label": c, "key": c} for c in n5], "#5a4a8c")
    n4 = ROOT / "data/kanji_n4.txt"       # optional: put the N4 kanji in this file, any spacing
    if n4.exists():
        add("Kanji N4", [{"label": c, "key": c} for c in n4.read_text(encoding="utf-8") if "\u4e00" <= c <= "\u9fff"], "#2f7a7a")
    gp, idx = {}, 0                       # global ids, same order as resolver.grammar_points()
    for f in sorted((ROOT / "data/grammar").glob("*.json")):
        for r in _json(f, []):
            gp.setdefault(r.get("level", f.stem), []).append({"label": r["pattern"], "key": f"g:{idx}", "rec": r}); idx += 1
    for lv in sorted(gp, reverse=True):   # N5 first
        add(f"Grammar {lv}", gp[lv], "#8c6a2f")
    sl = _json(ROOT / "data/slang.json", {})
    add("Slang", [{"label": k, "key": k, "rec": sl[k]} for k in sl], "#8c2f6a")
    return S


def _darken(hexcol, f=0.45):
    h = hexcol.lstrip("#"); r, g_, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % (int(r * f), int(g_ * f), int(b * f))


# ------------------------------------------------------------------ state machine (no drawing, no Tk)
class Lib:
    def __init__(s):
        s.shelves = build_shelves()
        s.si = 0; s.pos = [0] * len(s.shelves)
        s.mode = "shelf"; s.view = None; s.pending = None
        s.inspect = False; s.hint = ""; s.last_esc = -99.0

    def item(s): return s.shelves[s.si]["items"][s.pos[s.si]]

    def back(s):
        if s.mode == "view": s.mode = "shelf"; s.view = None; s.pending = None

    def key(s, k, now=None):
        """k: Left Right Up Down Enter Back Tab Esc. Returns 'quit' or None."""
        now = time.time() if now is None else now
        if not s.shelves: return "quit" if k == "Esc" else None
        if k == "Esc":
            dbl = now - s.last_esc < DOUBLE_ESC; s.last_esc = now
            if dbl: return "quit"
            if s.mode == "view": s.back(); s.hint = ""
            else: s.hint = "Press Esc again to exit"
            return None
        s.last_esc = -99.0; s.hint = ""
        if k == "Back": s.back()
        elif k == "Tab": s.inspect = not s.inspect
        elif s.mode == "shelf":
            n = len(s.shelves[s.si]["items"])
            if k == "Left": s.pos[s.si] = max(0, s.pos[s.si] - 1)
            elif k == "Right": s.pos[s.si] = min(n - 1, s.pos[s.si] + 1)
            elif k == "Up": s.si = max(0, s.si - 1)
            elif k == "Down": s.si = min(len(s.shelves) - 1, s.si + 1)
            elif k == "Enter": s.pending = (s.si, s.pos[s.si])
        elif s.view:
            st = s.view["stages"]; n = max(len(st), 1)
            if k == "Left": s.view["i"] = (s.view["i"] - 1) % n
            elif k in ("Right", "Enter"): s.view["i"] = (s.view["i"] + 1) % n
            elif k in ("Up", "Down"):
                m = len(s.shelves[s.si]["items"]); p = s.pos[s.si] + (1 if k == "Down" else -1)
                if 0 <= p < m: s.pos[s.si] = p; s.pending = (s.si, p)
        return None

    def service(s):
        """Does the slow part (resolve, which may download KanjiVG). Call after key() while pending."""
        if not s.pending: return
        si, i = s.pending; s.pending = None
        it = s.shelves[si]["items"][i]
        try:
            import chains
            kind, stages = "glyph", chains.build(s.shelves[si]["name"], it, R, SY)
            err = ""
        except Exception as e:
            kind, stages, err = "error", [], str(e)
        s.view = {"stages": stages, "i": 0, "item": it, "kind": kind, "err": err}
        s.mode = "view"

    # ---------------- drawing (g is a Gfx: Tk, PIL, ...)
    def draw(s, g):
        g.rect(0, 0, W, H, fill="#14100c")
        if not s.shelves:
            g.text(640, 340, "No shelves found. Run build_grammar.py and make_mnemonics.py first.", "#f1d9a8", 22); return
        if s.mode == "view" and s.view: s.draw_view(g)
        else: s.draw_shelves(g)
        if s.hint: g.text(640, 690, s.hint, "#ffe9a8", 18, True)
        if s.pending: g.text(640, 360, "Loading…", "#ffe9a8", 34, True)

    def draw_shelves(s, g):
        sh = s.shelves[s.si]; it = s.item()
        g.text(40, 30, "LIBRARY  ›  " + sh["name"], "#f1d9a8", 20, True, "l")
        g.text(640, 100, it["label"][:30], "#fff8e0", 38, True)
        g.text(640, 138, f"{s.pos[s.si] + 1} / {len(sh['items'])}", "#b89a6a", 15)
        for j in range(max(0, s.si - 1), min(len(s.shelves), s.si + 2)):
            base = 490 + (j - s.si) * 190
            s.draw_row(g, j, base)
        if s.inspect:
            g.rect(860, 48, 1250, 150, fill="#000", outline="#ffe9a8", w=2)
            g.text(875, 70, f"key: {it['key']}", "#ffe9a8", 14, False, "l")
            have = (ROOT / "glyphs/chains" / f"{it['key']}.json").exists()
            g.text(875, 96, "authored scene on disk" if have else "no authored scene", "#ddd", 13, False, "l")
            g.text(875, 122, "Enter opens it", "#aaa", 13, False, "l")
        g.text(640, 708, HELP, "#b89a6a", 12)

    def draw_row(s, g, j, base):
        sh = s.shelves[j]; n = len(sh["items"]); p = s.pos[j]; sel = (j == s.si)
        g.rect(0, base, W, base + 16, fill="#5a3a1f" if sel else "#33200f", outline="#2e1d0e")
        g.text(24, base + 8, f"{sh['name'].upper()}  ·  {n}", "#f1d9a8" if sel else "#8a7650", 11, True, "l")
        col = sh["color"] if sel else _darken(sh["color"])
        txt = "#fff8e0" if sel else "#8f836a"
        rng = range(max(0, p - 14), min(n, p + 15))
        if sel:                              # glow first so neighbours are never overpainted
            lab = sh["items"][p]["label"]; h = 110 + (sum(map(ord, lab)) % 5) * 10
            g.glow(640, base - 16 - h / 2, 50, h / 2 + 24)
        for i in rng:
            off = i - p
            cx = 640 + off * 49 + (0 if off == 0 else (11 if off > 0 else -11))
            lab = sh["items"][i]["label"]
            h = 110 + (sum(map(ord, lab)) % 5) * 10
            on = sel and off == 0
            b = base - (16 if on else 0)
            g.rect(cx - 21, b - h, cx + 21, b, fill=col, outline="#ffe9a8" if on else "#1a1208", w=3 if on else 1)
            g.rect(cx - 21, b - h + 10, cx + 21, b - h + 13, fill="#d8c08a")
            g.rect(cx - 21, b - 13, cx + 21, b - 10, fill="#d8c08a")
            chars = [c for c in lab if c != " "][:7]
            size = 26 if len(chars) == 1 else 16
            step = size + 2
            y0 = b - h / 2 - (len(chars) - 1) * step / 2
            for k, c in enumerate(chars):
                g.text(cx, y0 + k * step, c, txt, size, on)

    def draw_view(s, g):
        v = s.view; st = v["stages"]; sh = s.shelves[s.si]
        g.text(40, 30, f"LIBRARY  ›  {sh['name']}  ›  {v['item']['label'][:24]}", "#f1d9a8", 18, True, "l")
        if not st:
            g.text(640, 340, "Nothing to show" + (": " + v["err"][:80] if v["err"] else ""), "#e88", 22); return
        i = v["i"]; stg = st[i]; col = COL.get(stg.get("provenance", "designed"), "#fff")
        g.text(640, 76, f"{i + 1} / {len(st)}   {stg['label'][:70]}", "#fff8e0", 22, True)
        if stg.get("text") and not stg.get("sticks", {}).get("s"):
            t = stg["text"]
            if len(t) <= 3: g.text(640, 320, t, col, 220, True)
            else:
                ls = []
                for para in t.split("\n"): ls += textwrap.wrap(para, 44) or [""]
                for k, ln in enumerate(ls[:10]): g.text(640, 170 + k * 40, ln, "#fff8e0" if k == 0 else "#e8d9b0", 32 if k == 0 else 26, k == 0)
        else:
            g.strokes(stg["sticks"], 140, 110, 1140, 540, col, 6)
        for k in range(len(st)):
            x = 640 + (k - (len(st) - 1) / 2) * 22
            g.oval(x - 6, 566, x + 6, 578, fill="#ffe9a8" if k == i else "#4a3a28", outline="#ffe9a8")
        tag = (stg.get("role") or stg.get("provenance", "")).upper()
        g.text(640, 604, tag, col, 15, True)
        if s.inspect:
            g.rect(120, 618, 1160, 700, fill="#000", outline=col, w=2)
            head = f"provenance: {stg.get('provenance', 'designed')}"
            if stg.get("confidence"): head += f"   confidence: {stg['confidence']}"
            if stg.get("source"): head += f"   source: {stg['source']}"
            lines = [head]
            if stg.get("confidence") == "disputed": lines.append("WARNING: disputed etymology, not settled")
            if "invented" in (stg.get("note", "") or "").lower(): lines.append("invented mnemonic, NOT etymology")
            lines += textwrap.wrap(stg.get("note", "") or "", 110)
            for k, t in enumerate(lines[:4]): g.text(136, 632 + k * 19, t, "#eee", 14, False, "l")
        g.text(640, 708, HELP_VIEW, "#b89a6a", 12)


# ------------------------------------------------------------------ Tk backend
class TkGfx:
    def __init__(s, cv, family):
        s.cv, s.fam = cv, family
        w, h = max(cv.winfo_width(), 200), max(cv.winfo_height(), 120)
        s.f = min(w / W, h / H); s.ox = (w - W * s.f) / 2; s.oy = (h - H * s.f) / 2
        cv.delete("all"); cv.create_rectangle(0, 0, w, h, fill="#000", outline="")
    def X(s, x): return s.ox + x * s.f
    def Y(s, y): return s.oy + y * s.f
    def rect(s, x0, y0, x1, y1, fill="", outline="", w=1):
        s.cv.create_rectangle(s.X(x0), s.Y(y0), s.X(x1), s.Y(y1), fill=fill, outline=outline, width=w)
    def oval(s, x0, y0, x1, y1, fill="", outline="", w=1):
        s.cv.create_oval(s.X(x0), s.Y(y0), s.X(x1), s.Y(y1), fill=fill, outline=outline, width=w)
    def line(s, pts, fill, w=1):
        s.cv.create_line(*[c for x, y in pts for c in (s.X(x), s.Y(y))], fill=fill, width=max(1, w * s.f),
                         capstyle="round", joinstyle="round")
    def text(s, x, y, t, fill, size, bold=False, anchor="c"):
        s.cv.create_text(s.X(x), s.Y(y), text=t, fill=fill, anchor={"c": "center", "l": "w", "r": "e"}[anchor],
                         font=(s.fam, -max(6, int(size * s.f)), "bold" if bold else "normal"))
    def dim(s, x0, y0, x1, y1):
        s.cv.create_rectangle(s.X(x0), s.Y(y0), s.X(x1), s.Y(y1), fill="#000", stipple="gray50", outline="")
    def glow(s, cx, cy, rx, ry):
        s.cv.create_oval(s.X(cx - rx), s.Y(cy - ry), s.X(cx + rx), s.Y(cy + ry), fill="#fff3b0", stipple="gray25", outline="")
    def strokes(s, u, x0, y0, x1, y1, col, w):
        k = min((x1 - x0) / max(u["w"], 1), (y1 - y0) / max(u["h"], 1))
        ox = x0 + ((x1 - x0) - u["w"] * k) / 2; oy = y0 + ((y1 - y0) - u["h"] * k) / 2
        for st in u["s"]:
            if len(st) > 1: s.line([(ox + x * k, oy + y * k) for x, y in st], col, w)

def run_gui():
    import tkinter as tk, tkinter.font as tkf
    lib = Lib()
    root = tk.Tk(); root.title("Library"); root.geometry("1280x720"); root.configure(bg="#000")
    fams = set(tkf.families())
    fam = next((f for f in ("Noto Sans CJK JP", "Noto Sans JP", "Noto Sans CJK SC", "IPAexGothic", "TakaoGothic",
                            "DejaVu Sans") if f in fams), "TkDefaultFont")
    cv = tk.Canvas(root, bg="#000", highlightthickness=0); cv.pack(fill="both", expand=True)
    shift = {"down": False, "used": False}

    def redraw(): lib.draw(TkGfx(cv, fam))
    def service(): lib.service(); redraw()
    def act(k):
        if lib.key(k) == "quit": root.destroy(); return
        redraw()
        if lib.pending: root.after(30, service)

    MAP = {"Left": "Left", "Right": "Right", "Up": "Up", "Down": "Down", "Return": "Enter", "KP_Enter": "Enter",
           "Tab": "Tab", "ISO_Left_Tab": "Tab", "Escape": "Esc"}
    def press(e):
        if e.keysym in ("Shift_L", "Shift_R"):
            if not shift["down"]: shift["down"] = True; shift["used"] = False
            return "break"
        if shift["down"]: shift["used"] = True
        k = MAP.get(e.keysym)
        if k: act(k)
        return "break"                       # every other key does nothing
    def release(e):
        if e.keysym in ("Shift_L", "Shift_R"):
            if shift["down"] and not shift["used"]: act("Back")
            shift["down"] = False
        return "break"
    root.bind_all("<KeyPress>", press); root.bind_all("<KeyRelease>", release)
    cv.bind("<Configure>", lambda e: redraw())
    root.after(50, redraw); root.mainloop()


# ------------------------------------------------------------------ curses CLI
def run_cli():
    import curses
    os.environ.setdefault("ESCDELAY", "40")
    try:
        from app import ascii_art
    except Exception:
        ascii_art = lambda u, cols=64: "(app.py not found)"
    lib = Lib()
    KEYS = {curses.KEY_LEFT: "Left", curses.KEY_RIGHT: "Right", curses.KEY_UP: "Up", curses.KEY_DOWN: "Down",
            10: "Enter", 13: "Enter", curses.KEY_ENTER: "Enter", 9: "Tab", curses.KEY_BTAB: "Back", 27: "Esc"}

    def put(sc, y, x, t, a=0):
        h, w = sc.getmaxyx()
        if 0 <= y < h and x < w:
            try: sc.addstr(y, x, t[: max(0, w - x - 1)], a)
            except curses.error: pass

    def main(sc):
        curses.curs_set(0)
        while True:
            sc.erase(); h, w = sc.getmaxyx()
            if not lib.shelves: put(sc, 1, 1, "No shelves. Run build_grammar.py / make_mnemonics.py. Esc Esc quits.")
            elif lib.mode == "view" and lib.view:
                v = lib.view; st = v["stages"]
                put(sc, 0, 1, "LIBRARY › " + lib.shelves[lib.si]["name"] + " › " + v["item"]["label"], curses.A_BOLD)
                if st:
                    s_ = st[v["i"]]
                    put(sc, 1, 1, f"{v['i'] + 1}/{len(st)}  {s_['label']}  <{s_.get('provenance', '')}>")
                    if lib.inspect:
                        put(sc, 2, 1, (s_.get("note") or "")[: w - 3])
                        if s_.get("confidence") == "disputed": put(sc, 3, 1, "WARNING: disputed etymology", curses.A_BOLD)
                    for y, ln in enumerate((textwrap.fill(s_["text"], max(20, w - 4)) if (s_.get("text") and not s_["sticks"]["s"]) else ascii_art(s_["sticks"], cols=max(20, min(110, w - 3)))).splitlines()):
                        put(sc, 4 + y, 1, ln)
                else: put(sc, 2, 1, "Nothing to show " + v["err"])
                put(sc, h - 1, 1, "←→ stage  ↑↓ book  Enter next  Tab inspect  Shift+Tab/Esc back  Esc Esc exit")
            elif lib.shelves:
                put(sc, 0, 1, "LIBRARY", curses.A_BOLD)
                for j, sh in enumerate(lib.shelves):
                    p = lib.pos[j]; items = sh["items"]
                    lo = max(0, p - 8); row = ""
                    for i in range(lo, min(len(items), p + 9)):
                        l = items[i]["label"][:6]; row += f"[{l}] " if i == p else f"{l} "
                    sel = j == lib.si
                    put(sc, 2 + j, 1, ("▶ " if sel else "  ") + f"{sh['name']:<14}", curses.A_BOLD if sel else 0)
                    put(sc, 2 + j, 20, row, curses.A_REVERSE if sel else 0)
                it = lib.item()
                put(sc, 3 + len(lib.shelves), 1, f"{it['label']}   ({lib.pos[lib.si] + 1}/{len(lib.shelves[lib.si]['items'])})", curses.A_BOLD)
                if lib.inspect: put(sc, 4 + len(lib.shelves), 1, f"key: {it['key']}")
                put(sc, h - 1, 1, "←→ browse  ↑↓ shelf  Enter open  Tab inspect  Esc Esc exit")
            if lib.hint: put(sc, h - 2, 1, lib.hint, curses.A_BOLD)
            sc.refresh()
            c = sc.getch(); k = KEYS.get(c)
            if k and lib.key(k) == "quit": return
            if lib.pending:
                put(sc, h - 3, 1, "Loading…"); sc.refresh(); lib.service()
    curses.wrapper(main)


if __name__ == "__main__":
    run_cli() if "cli" in sys.argv[1:] else run_gui()
