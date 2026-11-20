"""Symbolism chains: etymology -> language (the real character) -> symbolic drawing.
python3 symbolism.py 安      prints the stages as ASCII.   library.py uses chain() for single characters.

Add a character by adding an entry to SYMBOLS (strokes are polylines in a 100x100 box).
Every stage carries a role (etymology / language / symbol) and a provenance, so an invented drawing
is never shown as history."""
import math, sys
import resolver as R
from geometry import unit

def circle(cx, cy, r, n=18):
    return [[round(cx + r * math.cos(2 * math.pi * i / n), 1), round(cy + r * math.sin(2 * math.pi * i / n), 1)] for i in range(n + 1)]

def stage(role, label, strokes, prov, note):
    return {"role": role, "label": label, "sticks": unit(strokes), "provenance": prov, "note": note}

SYMBOLS = {
 "安": {
  "etymology": ("kneeling woman, arms crossed, under a roof",
    [[[10, 36], [50, 10], [90, 36]], [[10, 36], [10, 46]], [[90, 36], [90, 46]]]            # roof 宀
    + [circle(50, 52, 6)]                                                                     # head
    + [[[50, 58], [50, 76]], [[42, 62], [58, 70]], [[58, 62], [42, 70]]]                      # torso, crossed arms
    + [[[50, 76], [34, 84], [34, 94], [66, 94], [66, 84], [50, 76]]],                         # folded knees (oracle-bone 女)
    "authored",
    "Traditional account: roof 宀 + woman 女 (the old 女 is a kneeling person with crossed arms) = a woman "
    "at rest indoors = peace, safe. Widely cited, but treat it as the standard explanation, not proof."),
  "drawing": ("woman hugging herself under a roof",
    [[[18, 26], [50, 4], [82, 26], [18, 26]]]                                                 # triangle roof
    + [circle(50, 37, 7)]                                                                      # head
    + [[[50, 47], [34, 80], [66, 80], [50, 47]]]                                              # dress (restroom-sign woman)
    + [[[43, 80], [43, 96]], [[57, 80], [57, 96]]]                                            # legs
    + [[[47, 50], [35, 58], [58, 63]], [[53, 50], [65, 58], [42, 63]]],                       # arms wrapped across chest
    "designed",
    "Invented mnemonic, NOT etymology: a restroom-sign woman hugging herself under a roof, feeling safe."),
 },
}


HIRA = ("あ安 い以 う宇 え衣 お於 か加 き幾 く久 け計 こ己 さ左 し之 す寸 せ世 そ曽 た太 ち知 つ川 て天 と止 "
        "な奈 に仁 ぬ奴 ね祢 の乃 は波 ひ比 ふ不 へ部 ほ保 ま末 み美 む武 め女 も毛 や也 ゆ由 よ与 "
        "ら良 り利 る留 れ礼 ろ呂 わ和 を遠 ん无")
KATA = ("ア阿 イ伊 ウ宇 エ江 オ於 カ加 キ幾 ク久 ケ介 コ己 サ散 シ之 ス須 セ世 ソ曽 タ多 チ千 ツ川 テ天 ト止 "
        "ナ奈 ニ二 ヌ奴 ネ祢 ノ乃 ハ八 ヒ比 フ不 ヘ部 ホ保 マ万 ミ三 ム牟 メ女 モ毛 ヤ也 ユ由 ヨ与 "
        "ラ良 リ利 ル流 レ礼 ロ呂 ワ和 ヲ乎 ン尓")
ORIGIN = {w[0]: w[1] for w in (HIRA + " " + KATA).split()}
IS_KATA = {w[0] for w in KATA.split()}
DISPUTED = {"ケ": "ケ is usually traced to 介 (some sources say 計)", "ン": "ン is usually traced to 尓 (some sources say 无)",
            "ヲ": "ヲ is traced to 乎; sources differ on details"}

try:
    from kanji_etymology import ETYM
except Exception:
    ETYM = {}

def _annotate(stages, ch):
    e = ETYM.get(ch)
    if not e: return stages
    for s in stages:
        if s.get("role") in ("kanji", "character") and "Etymology:" not in (s.get("note") or ""):
            s["note"] = ((s.get("note") or "") + " Etymology: " + e[0]).strip()
            s["source"] = "list you supplied, not independently verified"
            if e[1] == "disputed": s["confidence"] = "disputed"
    return stages

def _rank(s):
    n = s.get("note") or ""
    if s["provenance"] == "traced": return 1
    if "[pictograph-based]" in n or s["provenance"] in ("authored", "composed"): return 0
    return 2

def _kanji_chain(k):
    if k in SYMBOLS:
        e = SYMBOLS[k]; t = R.traced(k)
        return [stage("etymology", e["etymology"][0], e["etymology"][1], e["etymology"][2], e["etymology"][3]),
                {**t, "role": "kanji", "label": k},
                stage("symbol", e["drawing"][0], e["drawing"][1], e["drawing"][2], e["drawing"][3])]
    st = [dict(s) for s in sorted(R.chain(k), key=_rank)]
    for s in st: s["role"] = {0: "etymology", 1: "kanji", 2: "symbol"}[_rank(s)]
    return _annotate(st, k)

def chain(ch):
    if ch in ORIGIN:                                 # every kana: its source kanji first, then the kana
        k = ORIGIN[ch]; t = dict(R.traced(ch))
        how = ("katakana: a fragment or shorthand taken from the kanji" if ch in IS_KATA
               else "hiragana: the cursive (sosho) form of the whole kanji")
        t.update(role="kana", label=ch, note=f"{ch} comes from {k}. {how}. " + DISPUTED.get(ch, ""))
        return _kanji_chain(k) + [t]
    if ch in SYMBOLS: return _kanji_chain(ch)
    st = [dict(s) for s in sorted(R.chain(ch), key=_rank)]   # existing scenes: pictograph, real glyph, invented last
    for s in st: s["role"] = {0: "etymology", 1: "character", 2: "symbol"}[_rank(s)]
    return _annotate(st, ch)

if __name__ == "__main__":
    from app import ascii_art
    for i, s in enumerate(chain(sys.argv[1])):
        print(f"--- {i + 1}. {s['role'].upper()}  {s['label']}  <{s['provenance']}>\n    {s.get('note', '')}")
        print(ascii_art(s["sticks"], cols=48))
