"""python app.py gui | show <text> [--ascii] | needs | ids | prefetch
<text> can be: あ, 寿司, 寿司が好きです。, g:12 (grammar index), or a key of data/slang.json"""
import sys, json, math, argparse, urllib.request
from pathlib import Path
import resolver as R
from geometry import unit

COL = {"authored": "#2e9e4f", "composed": "#2f6fd1", "traced": "#666666", "designed": "#d98a1c", "placeholder": "#cc3333"}

def ascii_art(u, cols=64):
    w, h = max(u["w"], 1), max(u["h"], 1)
    rows = max(2, int(cols * h / w / 2)); g = [[" "] * cols for _ in range(rows)]
    def pt(x, y): return int(x * (cols - 1) / w), int(y * (rows - 1) / h)
    for st in u["s"]:
        for a, b in zip(st, st[1:]):
            (x1, y1), (x2, y2) = pt(*a), pt(*b)
            n = max(abs(x2 - x1), abs(y2 - y1), 1)
            for i in range(n + 1):
                x, y = x1 + (x2 - x1) * i // n, y1 + (y2 - y1) * i // n
                if 0 <= y < rows and 0 <= x < cols: g[y][x] = "#"
    return "\n".join("".join(r).rstrip() for r in g)

def show(text):
    kind, stages = R.resolve(text)
    print(f"[{kind}] {text}")
    for i, s in enumerate(stages):
        extra = f" confidence={s['confidence']}" if s.get("confidence") else ""
        warn = "  !! DISPUTED etymology" if s.get("confidence") == "disputed" else ""
        print(f"\n--- stage {i}: {s['label']}  <{s['provenance']}>{extra}{warn}")
        if s.get("note"): print("    " + s["note"])
        print(ascii_art(s["sticks"]))

def gui():
    import tkinter as tk
    root = tk.Tk(); root.title("Etym glyphs")
    ent = tk.Entry(root, font=("Noto Sans CJK JP", 16)); ent.pack(fill="x", padx=6, pady=6); ent.focus_set()
    cv = tk.Canvas(root, width=760, height=420, bg="white"); cv.pack(fill="both", expand=True)
    info = tk.Label(root, justify="left", anchor="w", font=("monospace", 10)); info.pack(fill="x")
    S = {"stages": [], "i": 0, "inspect": True}
    def draw():
        cv.delete("all")
        if not S["stages"]: return
        s = S["stages"][S["i"]]; u = s["sticks"]
        W, H = cv.winfo_width() - 40, cv.winfo_height() - 70
        k = min(W / max(u["w"], 1), H / max(u["h"], 1)); ox = (W - u["w"] * k) / 2 + 20; oy = (H - u["h"] * k) / 2 + 40
        for st in u["s"]:
            cv.create_line(*[c for x, y in st for c in (ox + x * k, oy + y * k)], width=4, capstyle="round",
                           joinstyle="round", fill=COL.get(s["provenance"], "#000")) if len(st) > 1 else None
        cv.create_text(10, 10, anchor="nw", font=("Noto Sans CJK JP", 14), text=f"{S['i']+1}/{len(S['stages'])}  {s['label']}")
        if S["inspect"]:
            t = f"provenance: {s['provenance']}\n{s.get('note','')}"
            if s.get("confidence"): t += f"\nconfidence: {s['confidence']}  source: {s.get('source')}"
            if s.get("confidence") == "disputed": t += "\nWARNING: disputed etymology, not settled"
            info.config(text=t)
        else: info.config(text="")
    def go(_=None):
        kind, S["stages"] = R.resolve(ent.get()); S["i"] = 0; root.focus_set(); draw()
    def step(d):
        if S["stages"]: S["i"] = (S["i"] + d) % len(S["stages"]); draw()
    def tab(_):
        S["inspect"] = not S["inspect"]; draw(); return "break"
    ent.bind("<Return>", go)
    root.bind("<Right>", lambda e: step(1) if root.focus_get() is not ent else None)
    root.bind("<Left>", lambda e: step(-1) if root.focus_get() is not ent else None)
    root.bind("<space>", lambda e: step(1) if root.focus_get() is not ent else None)
    root.bind("<Escape>", lambda e: ent.focus_set())
    root.bind_all("<Tab>", tab); cv.bind("<Configure>", lambda e: draw())
    root.mainloop()

def needs(top=40):
    from collections import Counter
    need = Counter()
    for gp in R.grammar_points():
        for ch in gp["ja"] + "".join(c for c in gp["pattern"] if R._kind(c) != "other"):
            if R._kind(ch) == "han":
                for leaf in R.leaves(ch):
                    if leaf not in R.LIB: need[leaf] += 1
    for leaf, n in need.most_common(top): print(n, leaf)

def fetch_ids():
    """Downloads cjkvi-ids (verify its license before redistributing)."""
    url = "https://raw.githubusercontent.com/cjkvi/cjkvi-ids/master/ids.txt"
    out = {}
    for line in urllib.request.urlopen(url, timeout=30).read().decode("utf-8").splitlines():
        p = line.split("\t")
        if len(p) < 3 or p[0].startswith("#"): continue
        import re
        ids = re.sub(r"\[[A-Z]+\]|[\^$]", "", p[2]).strip()
        if ids and ids != p[1]: out[p[1]] = ids
    Path("data").mkdir(exist_ok=True)
    Path("data/ids.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print(len(out), "IDS entries -> data/ids.json")

def prefetch():
    from kvg import kvg_sticks
    chars = {c for gp in R.grammar_points() for c in gp["ja"] + gp["pattern"] if R._kind(c) in ("han", "hira", "kata")}
    for c in sorted(chars): kvg_sticks(c)
    print("cached", len(chars), "characters (misses stay placeholders)")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("text", nargs="?")
    a = ap.parse_args()
    {"gui": gui, "show": lambda: show(a.text), "needs": needs, "ids": fetch_ids, "prefetch": prefetch}[a.cmd]() \
        if a.cmd != "gui" else gui()
