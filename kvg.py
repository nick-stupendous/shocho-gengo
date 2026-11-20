"""KanjiVG -> stick reduction. KanjiVG is CC BY-SA 3.0 (credit Ulrich Apel): keep attribution."""
import os, re, math, urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

DIR = Path(__file__).resolve().parent / "data" / "kvg"
URL = "https://raw.githubusercontent.com/KanjiVG/kanjivg/master/kanji/{}.svg"
OFFLINE = bool(os.environ.get("ETYM_OFFLINE"))
_miss = set()

def _bez(p0, p1, p2, p3, n=8):
    out = []
    for i in range(1, n + 1):
        t = i / n; u = 1 - t
        out.append((u**3*p0[0]+3*u*u*t*p1[0]+3*u*t*t*p2[0]+t**3*p3[0],
                    u**3*p0[1]+3*u*u*t*p1[1]+3*u*t*t*p2[1]+t**3*p3[1]))
    return out

def parse_path(d):
    toks = re.findall(r"[MmCcSsLlHhVvZz]|-?\d*\.?\d+(?:[eE]-?\d+)?", d)
    i, cmd, cur, c2, pts = 0, None, (0.0, 0.0), None, []
    while i < len(toks):
        if re.match(r"[A-Za-z]", toks[i]):
            cmd = toks[i]; i += 1
            if cmd in "Zz": continue
        rel, C = cmd.islower(), cmd.upper()
        need = {"M":2,"L":2,"H":1,"V":1,"C":6,"S":4}[C]
        v = [float(t) for t in toks[i:i+need]]; i += need
        ox, oy = cur if rel else (0, 0)
        if C in "ML":
            cur = (v[0]+ox, v[1]+oy); pts.append(cur); c2 = None
            if C == "M": cmd = "l" if rel else "L"
        elif C == "H": cur = (v[0]+ox if rel else v[0], cur[1]); pts.append(cur); c2 = None
        elif C == "V": cur = (cur[0], v[0]+oy if rel else v[0]); pts.append(cur); c2 = None
        elif C == "C":
            p1, c2, e = (v[0]+ox, v[1]+oy), (v[2]+ox, v[3]+oy), (v[4]+ox, v[5]+oy)
            pts += _bez(cur, p1, c2, e); cur = e
        else:
            p1 = (2*cur[0]-c2[0], 2*cur[1]-c2[1]) if c2 else cur
            c2, e = (v[0]+ox, v[1]+oy), (v[2]+ox, v[3]+oy)
            pts += _bez(cur, p1, c2, e); cur = e
    return pts

def rdp(pts, eps=4.0):
    if len(pts) < 3: return list(pts)
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    L = math.hypot(x2-x1, y2-y1) or 1e-9
    dmax, idx = 0, 0
    for k in range(1, len(pts)-1):
        d = abs((x2-x1)*(y1-pts[k][1]) - (x1-pts[k][0])*(y2-y1)) / L
        if d > dmax: dmax, idx = d, k
    if dmax > eps: return rdp(pts[:idx+1], eps)[:-1] + rdp(pts[idx:], eps)
    return [pts[0], pts[-1]]

def kvg_sticks(ch, fetch=True):
    """Return strokes in a 100x100 box, or None if unavailable."""
    if ord(ch) < 0x3000 or ch in _miss: return None
    f = DIR / f"{ord(ch):05x}.svg"
    if not f.exists():
        if not fetch or OFFLINE: return None
        try:
            DIR.mkdir(parents=True, exist_ok=True)
            with urllib.request.urlopen(URL.format(f"{ord(ch):05x}"), timeout=8) as r:
                f.write_bytes(r.read())
        except Exception:
            _miss.add(ch); return None
    try:
        root = ET.parse(f).getroot()
    except ET.ParseError:
        return None
    strokes = []
    for el in root.iter():
        if el.tag.endswith("path") and re.search(r"-s\d+$", el.get("id", "")):
            p = parse_path(el.get("d", ""))
            if len(p) > 1:
                strokes.append([[x*100/109, y*100/109] for x, y in rdp(p)])
    return strokes or None
