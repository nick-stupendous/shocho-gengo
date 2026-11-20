"""Writes glyphs/diagrams/<category>.json. All provenance: designed (mnemonic, not etymology)."""
import json
from pathlib import Path
from geometry import circle, rect, arrow, star, dashed, fig

def key(cx, cy):
    return [circle(cx - 8, cy, 6), [[cx - 2, cy], [cx + 18, cy]], [[cx + 12, cy], [cx + 12, cy + 7]], [[cx + 18, cy], [cx + 18, cy + 7]]]

D = {}
D["particles"] = (["from", "to"], arrow(5, 50, 90, 50) + [[[30, 38], [30, 62]], [[30, 38], [46, 44]], [[46, 44], [30, 50]]])
D["comparison"] = (["A", "B", "C"], [rect(12, 60, 18, 30), rect(41, 40, 18, 50), rect(70, 15, 18, 75), [[70, 8], [88, 8]]])
D["conditionals"] = (["if", "then"], [[[8, 50], [40, 50]], [[40, 50], [70, 25]], [[40, 50], [70, 75]]] + arrow(70, 25, 95, 25))
D["cause"] = (["A", "B"], [rect(4, 35, 26, 30), rect(70, 35, 26, 30)] + arrow(30, 50, 70, 50) + [rect(43, 44, 14, 12)])
D["contrast"] = (["A", "B"], arrow(5, 50, 45, 50) + arrow(95, 50, 55, 50) + [[[50, 22], [50, 78]]])
D["purpose"] = (["action", "goal"], arrow(5, 50, 62, 50) + [circle(80, 50, 18), circle(80, 50, 8)])
gate = lambda: [[[25, 20], [25, 90]], [[75, 20], [75, 90]], [[18, 20], [82, 20]]]
D["obligation"] = (["action"], None, {
  "must_not": {"kw": ["must not", "prohibit", "not allowed", "forbid"], "strokes": gate() + [[[25, 55], [75, 55]], [[20, 35], [80, 80]], [[80, 35], [20, 80]]]},
  "may": {"kw": ["may", "permission", "allowed"], "strokes": gate() + [[[25, 55], [25, 55]], [[75, 55], [60, 40]]]},
  "must": {"kw": ["must", "have to", "need to"], "strokes": gate() + [[[25, 55], [75, 55]], [[25, 70], [75, 70]]]}})
D["desire"] = (["person", "goal"], fig(30, 90, 1.1, arms=((-12, 12), (22, -22))) + [star(75, 22, 14)])
D["suggestion"] = (["person", "other"], fig(35, 90, 1.1, arms=((-12, 12), (28, 4))) + [[[68, 40], [78, 36]], [[68, 46], [80, 46]], [[68, 52], [78, 56]]])
D["conjecture"] = (["thing"], dashed(fig(50, 92, 1.1)) + [[[25, 16], [33, 8], [45, 10], [53, 4], [67, 8], [73, 16], [25, 16]]])
D["time"] = (["before", "now", "after"], [[[5, 60], [95, 60]]] + [[[x, 52], [x, 68]] for x in (20, 80)] + [[[50, 40], [50, 80]], [[44, 34], [50, 40], [56, 34]]])
D["quantity"] = (["amount", "limit"], [rect(10, 40, 80, 20), [[10, 50], [62, 50]], [[70, 25], [70, 75]]])
D["giving"] = (["giver", "receiver", "thing"], fig(18, 80, 0.9) + fig(82, 80, 0.9) + [rect(42, 32, 16, 16)] + arrow(30, 62, 70, 62))
D["voice"] = (["actor", "target"], None, {
  "causative": {"kw": ["causative", "make", "let"], "strokes": fig(70, 90, 1) + arrow(5, 55, 45, 55)},
  "potential": {"kw": ["potential", "can", "able", "ability"], "strokes": fig(35, 90, 1.1, arms=((-12, 12), (20, 6))) + key(75, 52)},
  "passive":   {"kw": ["passive"], "strokes": arrow(90, 50, 10, 50)}})
D["honorific"] = (["speaker", "other"], None, {
  "humble": {"kw": ["humble", "polite request"], "strokes": fig(50, 90, 1.1, arms=((-10, 14), (10, 14)), lean=22, drop=16)},
  "honorific": {"kw": ["honorific", "respectful"], "strokes": fig(50, 62, 1.1) + [[[25, 64], [75, 64]], [[32, 64], [32, 90]], [[68, 64], [68, 90]]]}})
D["quotation"] = (["quoted"], [[[32, 15], [15, 15], [15, 88], [32, 88]], [[68, 15], [85, 15], [85, 88], [68, 88]]] + fig(50, 82, 0.9))
D["emphasis"] = (["focus"], [circle(50, 50, 8)] + [[[50 + 18 * c, 50 + 18 * s], [50 + 40 * c, 50 + 40 * s]]
   for c, s in [(1, 0), (.7, .7), (0, 1), (-.7, .7), (-1, 0), (-.7, -.7), (0, -1), (.7, -.7)]])
D["sentence_ending"] = (["sentence"], [[[8, 50], [24, 50]], [[30, 50], [46, 50]], [[52, 50], [68, 50]], [[74, 50], [86, 50]], [[86, 50], [94, 38]]])
D["forms"] = (["before", "after"], fig(22, 85, 0.9) + arrow(40, 58, 60, 58) + fig(78, 85, 0.9, arms=((-14, -14), (14, -14))))
D["other"] = (["a", "b"], arrow(8, 50, 92, 50))

out = Path(__file__).resolve().parent / "glyphs/diagrams"; out.mkdir(parents=True, exist_ok=True)
for cat, t in D.items():
    slots, strokes = t[0], t[1]
    d = {"category": cat, "slots": slots, "provenance": "designed", "strokes": strokes or list(t[2].values())[0]["strokes"]}
    if len(t) > 2: d["variants"] = t[2]
    (out / f"{cat}.json").write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
print(len(D), "diagrams written")
