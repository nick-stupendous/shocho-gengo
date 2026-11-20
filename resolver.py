"""Resolver: every unit gets a stick scene, tagged with provenance."""
import json, re, unicodedata
from pathlib import Path
from geometry import unit, layout_row, place
from latin import LATIN
from tables import ARITY, PARTICLES, HIRA_ORIGIN, KATA_ORIGIN, IDS_SEED
import kvg

ROOT = Path(__file__).resolve().parent
PRIORITY = ["placeholder", "designed", "traced", "composed", "authored"]  # weakest first
CONTENT = ("noun", "verb", "adjective", "adverb")

def _json(p, default):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception: return default

# ---------- data ----------
LIB = {}       # authored glyphs/components/<char>.json  {"strokes": [...], "note": ""}
for f in (ROOT / "glyphs/components").glob("*.json"):
    d = _json(f, None)
    if d and d.get("strokes"): LIB[f.stem] = d
IDS = {**IDS_SEED, **_json(ROOT / "data/ids.json", {})}
KANA_ORIGIN = {**HIRA_ORIGIN, **KATA_ORIGIN}
CHAINS = {}    # authored whole chains glyphs/chains/<char>.json: [{"label","strokes","provenance","note"}]
for f in (ROOT / "glyphs/chains").glob("*.json"):
    d = _json(f, None)
    if isinstance(d, list):
        CHAINS[f.stem] = [{"label": s.get("label", ""), "sticks": unit(s["strokes"]),
                           "provenance": s.get("provenance", "authored"), "note": s.get("note", "")} for s in d]
DIAGRAMS = {f.stem: _json(f, {}) for f in (ROOT / "glyphs/diagrams").glob("*.json")}
SLANG = _json(ROOT / "data/slang.json", {})

def grammar_points():
    out = []
    for f in sorted((ROOT / "data/grammar").glob("*.json")):
        out += _json(f, [])
    return out

def _glyphy(c):
    return not unicodedata.category(c).startswith(("P", "Z", "C")) and c not in "～〜"

def weakest(provs):
    return min(provs, key=PRIORITY.index)

# ---------- glyph stages ----------
def traced(ch):
    s = kvg.kvg_sticks(ch)
    if s: return {"label": ch, "sticks": unit(s), "provenance": "traced",
                  "note": "KanjiVG (CC BY-SA 3.0) strokes reduced to sticks"}
    if ch.upper() in LATIN:
        return {"label": ch, "sticks": unit(LATIN[ch.upper()]), "provenance": "designed",
                "note": "built-in stick letter"}
    box = [[[10, 10], [90, 10], [90, 90], [10, 90], [10, 10]]]
    return {"label": ch, "sticks": unit(box), "provenance": "placeholder",
            "note": "no stroke data (run with network once, or author this glyph)"}

# --- IDS parsing / layout ---
INNER = {"⿴": (.2, .2, .6, .6), "⿵": (.2, .3, .6, .7), "⿶": (.2, 0, .6, .7), "⿷": (.3, .2, .7, .6),
         "⿸": (.3, .3, .7, .7), "⿹": (0, .3, .7, .7), "⿺": (.3, 0, .7, .7)}

def _parse(s, i=0):
    c = s[i]
    if c in ARITY:
        kids, i = [], i + 1
        for _ in range(ARITY[c]):
            k, i = _parse(s, i); kids.append(k)
        return (c, kids), i
    return c, i + 1

class _Missing(Exception): pass

def _layout(node, x, y, w, h, depth=0):
    if isinstance(node, str):
        if node in LIB: return place(LIB[node]["strokes"], x, y, w, h)
        if node in IDS and depth < 6:
            n, _ = _parse(IDS[node]); return _layout(n, x, y, w, h, depth + 1)
        raise _Missing(node)
    op, k = node
    if op == "⿰": return _layout(k[0], x, y, w/2, h, depth) + _layout(k[1], x+w/2, y, w/2, h, depth)
    if op == "⿱": return _layout(k[0], x, y, w, h/2, depth) + _layout(k[1], x, y+h/2, w, h/2, depth)
    if op == "⿲": return sum((_layout(k[i], x+w*i/3, y, w/3, h, depth) for i in range(3)), [])
    if op == "⿳": return sum((_layout(k[i], x, y+h*i/3, w, h/3, depth) for i in range(3)), [])
    if op == "⿻": return _layout(k[0], x, y, w, h, depth) + _layout(k[1], x, y, w, h, depth)
    fx, fy, fw, fh = INNER[op]
    return _layout(k[0], x, y, w, h, depth) + _layout(k[1], x+fx*w, y+fy*h, fw*w, fh*h, depth)

def compose(ids):
    """Strokes composed from authored leaves, or None if any leaf is not authored."""
    try:
        n, _ = _parse(ids); return _layout(n, 0, 0, 100, 100)
    except (_Missing, IndexError, KeyError):
        return None

def leaves(ch, depth=0):
    """IDS leaves of ch, expanded recursively."""
    if ch not in IDS or depth > 6: return [ch]
    out = []
    for c in IDS[ch]:
        if c in ARITY: continue
        out += [c] if c in LIB else (leaves(c, depth + 1) if c != ch else [c])
    return out

def glyph_stages(ch):
    st = [traced(ch)]
    if ch in IDS:
        s = compose(IDS[ch])
        if s: st.append({"label": IDS[ch], "sticks": unit(s), "provenance": "composed",
                         "note": "authored components laid out by IDS"})
    if ch in LIB:
        st.append({"label": "pictograph", "sticks": unit(LIB[ch]["strokes"]), "provenance": "authored",
                   "note": LIB[ch].get("note", "")})
    return st

def chain(ch):
    if ch in CHAINS: return CHAINS[ch] + [traced(ch)]   # designed scene, then the real glyph
    if ch in KANA_ORIGIN:   # あ -> 安 -> components -> pictograph
        s = glyph_stages(ch)[:1]
        s[0] = {**s[0], "note": f"kana derived from {KANA_ORIGIN[ch]}; " + s[0]["note"]}
        return s + chain(KANA_ORIGIN[ch])
    return glyph_stages(ch)

def word_chain(word):
    per = [chain(c) for c in word if _glyphy(c)]
    if not per: return []
    stages = []
    for k in range(max(len(p) for p in per)):
        row = [p[min(k, len(p) - 1)] for p in per]
        stages.append({"label": " ".join(r["label"] for r in row),
                       "sticks": layout_row([r["sticks"] for r in row]),
                       "provenance": weakest([r["provenance"] for r in row]),
                       "note": "weakest provenance in the row"})
    return stages

# ---------- tokenizing ----------
_tagger = None
POS = {"助詞": "particle", "名詞": "noun", "代名詞": "noun", "動詞": "verb", "形容詞": "adjective",
       "形状詞": "adjective", "副詞": "adverb"}

def _kind(c):
    if "\u4e00" <= c <= "\u9fff": return "han"
    if "\u30a0" <= c <= "\u30ff": return "kata"
    if "\u3040" <= c <= "\u309f": return "hira"
    return "other"

def _crude(text):
    toks, buf = [], ""
    def flush():
        nonlocal buf
        if buf: toks.append((buf, "noun" if _kind(buf[0]) != "hira" else "verb")); buf = ""
    for i, c in enumerate(text):
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if c in "はがをにでのともへ" and buf and _kind(buf[-1]) in ("han", "kata") \
                and (not nxt or _kind(nxt) in ("han", "kata") or nxt in "。、"):
            flush(); toks.append((c, "particle"))
        elif _kind(c) == "other": flush()
        else: buf += c
    flush(); return toks

def tokenize(text):
    """fugashi (MIT) + unidic-lite if installed, else a crude fallback. Check dictionary licenses."""
    global _tagger
    try:
        if _tagger is None:
            import fugashi; _tagger = fugashi.Tagger()
        return [(w.surface, POS.get(w.feature.pos1, "other")) for w in _tagger(text)]
    except Exception:
        return _crude(text)

def connector(surf):
    name, s = PARTICLES[surf]; return unit(s, 40, 20)

def sentence_scene(text):
    toks = tokenize(text)
    plain = [traced(c) for c in text if _glyphy(c)]
    parts = []
    for surf, pos in toks:
        if pos == "particle" and surf in PARTICLES: parts.append(connector(surf))
        elif pos in CONTENT and any(_glyphy(c) for c in surf):
            parts.append(layout_row([chain(c)[-1]["sticks"] for c in surf if _glyphy(c)]))
    return [
        {"label": text, "sticks": layout_row([p["sticks"] for p in plain]),
         "provenance": weakest([p["provenance"] for p in plain]) if plain else "placeholder",
         "note": "plain sentence row"},
        {"label": "scene", "sticks": layout_row(parts, gap=6),
         "provenance": "designed", "note": "content words as glyphs, particles as designed connectors"},
    ]

# ---------- grammar & slang ----------
def _variant(dia, text):
    for v in dia.get("variants", {}).values():
        if any(k in text for k in v["kw"]): return v
    vs = list(dia.get("variants", {}).values())
    return vs[0] if vs else dia

def grammar_chain(gp):
    dia = DIAGRAMS.get(gp["category"]) or DIAGRAMS.get("other") or {"strokes": [], "slots": []}
    v = _variant(dia, (gp["meaning"] + " " + gp["pattern"]).lower())
    row = [traced(c) for c in gp["pattern"] if _glyphy(c)]
    st = [{"label": gp["pattern"], "sticks": layout_row([r["sticks"] for r in row]) if row else unit([]),
           "provenance": weakest([r["provenance"] for r in row]) if row else "placeholder", "note": gp["meaning"]},
          {"label": gp["category"], "sticks": unit(v["strokes"]), "provenance": "designed",
           "note": "slots: " + ", ".join(dia.get("slots", []))}]
    return st + sentence_scene(gp["ja"])

def slang_chain(key):
    e = SLANG[key]; st = []
    for step in e["path"]:
        c = word_chain(step) or []
        last = c[-1] if c else traced("?")
        st.append({"label": step, "sticks": last["sticks"], "provenance": "designed",
                   "note": e.get("note", ""), "confidence": e.get("confidence"), "source": e.get("source")})
    return st

def resolve(text):
    text = text.strip()
    m = re.fullmatch(r"g:(\d+)", text)
    if m:
        gps = grammar_points(); i = int(m.group(1))
        return ("grammar", grammar_chain(gps[i])) if i < len(gps) else ("error", [])
    if text in SLANG: return "slang", slang_chain(text)
    if len([c for c in text if _glyphy(c)]) <= 1: return "glyph", chain(text[0]) if text else []
    toks = tokenize(text)
    if any(p == "particle" for _, p in toks) or re.search(r"[。！？!?]", text):
        return "sentence", sentence_scene(text)
    return "word", word_chain(text)
