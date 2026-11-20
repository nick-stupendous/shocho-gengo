"""chains.py: builds the stages shown for every library item. ONE file, save next to library.py.

Stage order, the same on every shelf:
    etymology -> meaning drawing -> real glyph -> (man'yogana -> kana | slang origin) -> literal translation (last)

Sections:  1 drawing helpers | 2 data (DRAW, LATIN, GLOSS, ROMAJI, PARTICLE) | 3 stage constructors
           4 one builder per shelf (kana, latin, kanji, particle, grammar, slang) | 5 build(), called by library.py
Self-test: python3 chains.py あ ア 安 A
"""
import math, sys, unicodedata


# ================================================================ 1. drawing helpers (100x100 box)
def C(cx, cy, r, n=20):
    return [[round(cx + r * math.cos(2 * math.pi * i / n), 1), round(cy + r * math.sin(2 * math.pi * i / n), 1)] for i in range(n + 1)]
def ell(cx, cy, rx, ry, n=24):
    return [[round(cx + rx * math.cos(2 * math.pi * i / n), 1), round(cy + ry * math.sin(2 * math.pi * i / n), 1)] for i in range(n + 1)]
def box(x0, y0, x1, y1): return [[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]]
def arc(cx, cy, r, a0, a1, n=14):
    return [[round(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), 1),
             round(cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)), 1)] for i in range(n + 1)]
def wave(x0, x1, y, amp, per=2, n=28):
    return [[round(x0 + (x1 - x0) * i / n, 1), round(y + amp * math.sin(2 * math.pi * per * i / n), 1)] for i in range(n + 1)]
def vwave(x, y0, y1, amp, per=2, n=28):
    return [[round(x + amp * math.sin(2 * math.pi * per * i / n), 1), round(y0 + (y1 - y0) * i / n, 1)] for i in range(n + 1)]
def arrow(x0, y0, x1, y1, h=7):
    a = math.atan2(y1 - y0, x1 - x0)
    return [[[x0, y0], [x1, y1]],
            [[x1, y1], [round(x1 - h * math.cos(a - .5), 1), round(y1 - h * math.sin(a - .5), 1)]],
            [[x1, y1], [round(x1 - h * math.cos(a + .5), 1), round(y1 - h * math.sin(a + .5), 1)]]]
def dashed(strokes, d=6, g=5):
    out = []
    for pl in strokes:
        pos, on, cur = 0.0, True, [pl[0]]
        for (x0, y0), (x1, y1) in zip(pl, pl[1:]):
            L = math.hypot(x1 - x0, y1 - y0); t = 0.0
            while t < L:
                step = min((d if on else g) - pos, L - t)
                t += step; pos += step
                p = [round(x0 + (x1 - x0) * t / L, 1), round(y0 + (y1 - y0) * t / L, 1)]
                if on: cur.append(p)
                if pos >= (d if on else g) - 1e-9:
                    if on: out.append(cur)
                    on = not on; pos = 0.0; cur = [p]
        if on and len(cur) > 1: out.append(cur)
    return out

ARM = {"down": [(.2, .27)], "up": [(.25, -.2)], "out": [(.3, .02)], "fwd": [(.3, .06)],
       "self": [(.15, .1), (.02, .2)], "cross": [(.16, .1), (-.12, .2)], "none": None}
def fig(cx, top, h, arms=("down", "down")):
    r = .13 * h; neck = top + 2 * r; sh = neck + .05 * h; hip = top + .62 * h; ft = top + h
    s = [C(cx, top + r, r, 14), [[cx, neck], [cx, hip]], [[cx, hip], [cx - .17 * h, ft]], [[cx, hip], [cx + .17 * h, ft]]]
    for side, a in zip((-1, 1), arms):
        if ARM[a]: s.append([[cx, sh]] + [[round(cx + side * dx * h, 1), round(sh + dy * h, 1)] for dx, dy in ARM[a]])
    return s
def hand(x=50, y=50, k=1.0):
    p = lambda a, b: [round(x + (a - 50) * k, 1), round(y + (b - 50) * k, 1)]
    return ([[p(30, 52), p(70, 52), p(70, 88), p(30, 88), p(30, 52)]]
            + [[p(34, 52), p(34, 24)], [p(44, 52), p(44, 16)], [p(54, 52), p(54, 20)], [p(64, 52), p(64, 30)]]
            + [[p(70, 70), p(88, 50)]])
GROUND = [[4, 93], [96, 93]]

# ================================================================ 2a. DATA: meaning drawings for the 62 source kanji
DRAW = {}
def d(ch, strokes, note): DRAW[ch] = (strokes, note)

d("安", [[[18, 26], [50, 4], [82, 26], [18, 26]], C(50, 37, 7), [[50, 47], [34, 80], [66, 80], [50, 47]],
        [[43, 80], [43, 96]], [[57, 80], [57, 96]], [[44, 51], [35, 58], [58, 63]], [[56, 51], [65, 58], [42, 63]]],
  "a woman hugging herself under a roof: peace")
d("阿", [[[4, 92], [24, 64], [42, 42], [58, 42], [76, 64], [96, 92]]] + fig(50, 4, 36, ("up", "up")), "a hill with a bend: slope, corner")
d("以", fig(28, 12, 64, ("down", "fwd")) + [[[47, 36], [80, 88]], [[80, 88], [94, 82]], [[80, 88], [94, 94]], GROUND], "a person using a tool: 'by means of'")
d("伊", fig(32, 10, 68, ("down", "fwd")) + [[[55, 8], [55, 94]]] + [C(55, 8, 5)], "a person with a staff of authority: 'that one'")
d("宇", [[[8, 46], [50, 14], [92, 46]], [[8, 46], [8, 54]], [[92, 46], [92, 54]]] + arrow(50, 68, 12, 68) + arrow(50, 68, 88, 68) + arrow(50, 68, 50, 92), "a roof with the space spreading out under its eaves")
d("衣", [[[38, 12], [50, 28], [62, 12], [88, 26], [80, 46], [70, 40], [70, 92], [30, 92], [30, 40], [20, 46], [12, 26], [38, 12]],
         [[38, 12], [56, 60]], [[62, 12], [44, 70]]], "a robe with a collar and overlapping lapels")
d("江", [[[4, 22], [96, 22]], [[4, 78], [96, 78]]] + [wave(4, 96, 38, 4), wave(4, 96, 50, 4), wave(4, 96, 62, 4)], "a wide river between two banks")
d("於", [[[34, 44], [50, 80], [66, 44]], C(50, 34, 18), C(50, 34, 6), [[26, 90], [74, 90]]], "a pin on the ground: 'at, in'")
d("加", [C(50, 50, 40), [[50, 24], [50, 76]], [[24, 50], [76, 50]]], "a plus sign: 'add'")
d("幾", [vwave(14, 6, 94, 4), vwave(86, 6, 94, 4), [[36, 32], [38, 20], [50, 14], [62, 20], [64, 32], [50, 46], [50, 58]], C(50, 72, 3.5)], "two threads and a question mark: 'how many?'")
d("久", [[[28, 10], [72, 10], [50, 48], [72, 90], [28, 90], [50, 48], [28, 10]], [[22, 10], [78, 10]], [[22, 90], [78, 90]], [[40, 80], [60, 80]]], "an hourglass: 'a long time'")
d("計", [box(8, 16, 92, 84), [[8, 44], [92, 44]]] + [[[x, 16], [x, 84]] for x in (28, 50, 72)]
        + [C(28, 32, 5), C(50, 32, 5), C(72, 32, 5), C(28, 58, 5), C(28, 70, 5), C(50, 58, 5), C(72, 58, 5), C(72, 70, 5)], "an abacus: 'to count, to plan'")
d("介", fig(50, 14, 70) + [box(16, 30, 28, 72), box(72, 30, 84, 72)], "a person between two armor plates: 'between'")
d("己", fig(50, 10, 76, ("down", "self")) + [C(50, 50, 8)], "a person pointing to their own chest: 'self'")
d("左", hand(50, 52, 1.0) + arrow(60, 8, 20, 8), "a left hand with an arrow pointing left")
d("散", [C(50, 50, 6)] + [[[round(50 + 14 * math.cos(math.radians(a)), 1), round(50 + 14 * math.sin(math.radians(a)), 1)],
                          [round(50 + 36 * math.cos(math.radians(a)), 1), round(50 + 36 * math.sin(math.radians(a)), 1)]] for a in range(0, 360, 36)]
        + [C(round(50 + 42 * math.cos(math.radians(a)), 1), round(50 + 42 * math.sin(math.radians(a)), 1), 3, 8) for a in range(0, 360, 36)], "a burst scattering outward: 'to scatter'")
d("之", [ell(36, 62, 12, 20)] + [C(x, y, 3, 8) for x, y in ((26, 34), (33, 30), (41, 30), (48, 34), (51, 40))] + arrow(62, 56, 94, 56), "a footprint stepping forward: 'to go'")
d("寸", [box(8, 38, 92, 62)] + [[[x, 38], [x, 48]] for x in range(16, 90, 8)] + [[[60, 38], [60, 58]]] + [C(60, 72, 5)], "a ruler with one mark: 'an inch, to measure'")
d("須", [C(50, 36, 22), C(42, 32, 2, 8), C(58, 32, 2, 8), [[44, 48], [56, 48]], [[30, 50], [34, 80], [50, 92], [66, 80], [70, 50]],
         [[40, 60], [40, 76]], [[50, 62], [50, 84]], [[60, 60], [60, 76]]], "a face with a long beard: 'must, necessary'")
d("世", [C(50, 50, 40), [[10, 50], [90, 50]], ell(50, 50, 18, 40), [[15.4, 30], [84.6, 30]], [[15.4, 70], [84.6, 70]]], "a globe: 'the world, a generation'")
d("曽", [box(32, 22, 68, 36), box(28, 36, 72, 52), box(24, 52, 76, 68), [[20, 68], [80, 68], [72, 92], [28, 92], [20, 68]],
         vwave(40, 2, 18, 2, 1.5, 14), vwave(50, 2, 18, 2, 1.5, 14), vwave(60, 2, 18, 2, 1.5, 14)], "a steamer of stacked layers: 'layer, formerly'")
d("太", [C(50, 20, 12), ell(50, 62, 30, 26), [[24, 58], [12, 74]], [[76, 58], [88, 74]], [[40, 86], [38, 96]], [[60, 86], [62, 96]]], "a big round person: 'thick, great'")
d("多", [C(x, y, 3.2, 8) for x in range(18, 90, 16) for y in range(18, 90, 16)], "a crowd of dots: 'many'")
d("知", [ell(50, 78, 18, 16)] + [C(50, 30, 13), [[44, 43], [56, 43]], [[45, 47], [55, 47]]]
        + [[[round(50 + 18 * math.cos(math.radians(a)), 1), round(30 + 18 * math.sin(math.radians(a)), 1)],
            [round(50 + 26 * math.cos(math.radians(a)), 1), round(30 + 26 * math.sin(math.radians(a)), 1)]] for a in (-160, -125, -90, -55, -20)], "a lightbulb over a head: 'to know'")
d("千", sum([fig(x, y, 24, ("down", "down")) for x in (20, 50, 80) for y in (4, 36, 68)], []), "a big crowd: 'a thousand'")
d("川", [vwave(22, 6, 94, 5), vwave(50, 6, 94, 5), vwave(78, 6, 94, 5)], "flowing water: 'river'")
d("天", [C(50, 14, 9)] + fig(50, 36, 58, ("up", "up")) + [[[4, 30], [20, 22]], [[80, 22], [96, 30]]], "a person under the sun and sky: 'heaven'")
d("止", [[[round(50 + 40 * math.cos(math.radians(22.5 + 45 * k)), 1), round(50 + 40 * math.sin(math.radians(22.5 + 45 * k)), 1)] for k in range(9)],
         [[28, 50], [72, 50]]], "a stop sign: 'to stop'")
d("奈", [[[46, 92], [46, 58]], [[54, 92], [54, 58]], C(50, 36, 26), C(40, 32, 4, 10), C(58, 28, 4, 10), C(52, 46, 4, 10), C(34, 46, 4, 10), C(66, 44, 4, 10)], "an apple tree: 'crabapple' (used for its sound)")
d("仁", fig(32, 28, 64, ("down", "fwd")) + fig(68, 28, 64, ("fwd", "down")) + [[[50, 26], [38, 14], [38, 8], [44, 5], [50, 10], [56, 5], [62, 8], [62, 14], [50, 26]]], "two people with a heart: 'benevolence'")
d("二", [[[18, 34], [82, 34]], [[10, 66], [90, 66]]], "two bars: 'two'")
d("奴", fig(36, 24, 70, ("down", "down")) + [box(52, 30, 86, 62), [[52, 46], [86, 46]]], "a person carrying a heavy bundle: 'servant'")
d("祢", [[[16, 50], [84, 50]], [[24, 50], [24, 92]], [[76, 50], [76, 92]], box(32, 32, 38, 50), box(62, 32, 68, 50),
         [[35, 32], [31, 24], [35, 16], [39, 24], [35, 32]], [[65, 32], [61, 24], [65, 16], [69, 24], [65, 32]], [[42, 48], [46, 40], [54, 40], [58, 48]]], "an altar with candles: 'ancestral shrine'")
d("乃", [C(20, 24, 5)] + [[[26, 26], [60, 26], [60, 72]], [[54, 64], [60, 72], [66, 64]], C(60, 84, 7)], "an arrow from here to there: 'namely'")
d("波", [wave(6, 94, 30, 8, 3), wave(6, 94, 52, 8, 3), wave(6, 94, 74, 8, 3)], "rolling waves: 'wave'")
d("八", [[[50, 16], [20, 86]], [[50, 16], [80, 86]], [[26, 70], [20, 86], [36, 80]], [[74, 70], [80, 86], [64, 80]]], "a line splitting in two: 'eight, divide'")
d("比", [[[50, 90], [50, 24]], [[34, 90], [66, 90]], [[14, 30], [86, 30]], C(50, 24, 4, 10), [[14, 30], [6, 56]], [[14, 30], [26, 56]], [[4, 56], [28, 56]],
         [[86, 30], [74, 56]], [[86, 30], [94, 56]], [[72, 56], [96, 56]]], "a balance scale: 'to compare'")
d("不", [C(50, 50, 38), [[24, 76], [76, 24]]], "a crossed-out circle: 'not'")
d("部", [box(14, 14, 86, 86), [[14, 50], [86, 50]], [[50, 14], [50, 86]], [[56, 56], [80, 80]], [[56, 68], [68, 80]], [[68, 56], [80, 68]]], "a whole divided into parts: 'section'")
d("保", fig(34, 10, 76, ("down", "down")) + fig(66, 34, 40, ("down", "down")) + [[[34, 36], [50, 44]]], "an adult carrying a child on the back: 'to protect'")
d("末", [[[46, 92], [46, 22]], [[54, 92], [54, 22]], [[50, 36], [30, 22]], [[50, 36], [70, 22]], [[50, 52], [28, 40]], [[50, 52], [72, 40]], C(50, 14, 7)] + arrow(86, 6, 62, 12), "the very tip of a tree: 'end, tip'")
d("万", [ell(50, 64, 12, 18), C(50, 40, 6), [[44, 38], [30, 28], [22, 34]], [[22, 34], [16, 24]], [[22, 34], [30, 40]], [[56, 38], [70, 28], [78, 34]], [[78, 34], [84, 24]],
         [[78, 34], [70, 40]], [[50, 82], [50, 90], [62, 94], [76, 84], [80, 66], [74, 52], [66, 50]], [[66, 50], [62, 44]],
         [[40, 58], [26, 58]], [[40, 66], [26, 72]], [[60, 58], [74, 58]], [[60, 66], [74, 72]]], "a scorpion (the old form 萬): 'ten thousand'")
d("美", [[[50, 6], [58, 42], [94, 50], [58, 58], [50, 94], [42, 58], [6, 50], [42, 42], [50, 6]], [[12, 12], [12, 24]], [[6, 18], [18, 18]], [[88, 80], [88, 92]], [[82, 86], [94, 86]]], "a sparkle: 'beautiful'")
d("三", [[[22, 22], [78, 22]], [[16, 50], [84, 50]], [[10, 78], [90, 78]]], "three bars: 'three'")
d("武", [[[34, 94], [34, 10]], [[34, 12], [70, 22], [58, 34], [34, 34]], ell(70, 72, 9, 15)] + [C(x, y, 2.5, 8) for x, y in ((63, 50), (69, 47), (75, 49), (79, 54))], "a halberd and a footprint: 'martial'")
d("牟", [[[30, 40], [38, 28], [62, 28], [70, 40], [66, 74], [50, 84], [34, 74], [30, 40]], [[38, 28], [26, 14], [18, 20]], [[62, 28], [74, 14], [82, 20]],
         C(42, 48, 3, 8), C(58, 48, 3, 8), [[42, 70], [58, 70]], arc(84, 50, 8, -60, 60), arc(86, 50, 14, -60, 60)], "an ox mooing: 'a lowing sound'")
d("女", [C(50, 18, 9), [[50, 28], [32, 72], [68, 72], [50, 28]], [[43, 72], [43, 94]], [[57, 72], [57, 94]], [[47, 32], [38, 42], [58, 48]], [[53, 32], [62, 42], [42, 48]]], "a woman with crossed arms: 'woman'")
d("毛", [[[6, 88], [94, 88]]] + [[[x, 88], [x - 4, 66], [x + 4, 46], [x - 2, 22]] for x in (16, 34, 52, 70, 88)], "strands of hair: 'hair, fur'")
d("也", [[[round(8 + i * 4.8, 1), round(60 + 14 * math.sin(i * .62), 1)] for i in range(18)], C(92, 56, 6, 12)], "a snake: 'to be, also'")
d("由", [[[34, 42], [28, 54], [26, 74], [36, 92], [64, 92], [74, 74], [72, 54], [66, 42], [34, 42]], [[50, 42], [50, 18]], [[50, 28], [32, 16], [38, 32], [50, 28]], [[50, 22], [68, 10], [64, 26], [50, 22]]], "a seed sprouting from a jar: 'reason, from'")
d("与", [[[2, 62], [30, 54], [42, 54]], [[98, 62], [70, 54], [58, 54]], box(42, 38, 58, 54), C(38, 56, 4, 8), C(62, 56, 4, 8)], "two hands passing a box: 'to give'")
d("良", [C(50, 50, 40), [[28, 52], [44, 68], [74, 32]]], "a check mark: 'good'")
d("利", [[[34, 94], [34, 14]], [[34, 26], [24, 18]], [[34, 26], [44, 18]], [[34, 40], [24, 32]], [[34, 40], [44, 32]], [[34, 54], [24, 46]], [[34, 54], [44, 46]],
         [[62, 90], [70, 62]], [[68, 60], [88, 14], [80, 58], [68, 60]]], "a knife cutting grain: 'sharp, profit'")
d("留", [C(50, 14, 7), [[38, 28], [62, 28]], [[50, 21], [50, 84]], arc(50, 62, 34, 20, 160), [[18, 62], [14, 74]], [[82, 62], [86, 74]]], "an anchor: 'to stay'")
d("流", [wave(6, 94, 32, 6, 2), wave(6, 94, 66, 6, 2)] + arrow(8, 50, 92, 50), "water flowing along: 'to flow'")
d("礼", [C(30, 54, 9), [[38, 60], [64, 62]], [[64, 62], [60, 94]], [[64, 62], [76, 94]], [[44, 62], [34, 78]], GROUND], "a person bowing: 'bow, etiquette'")
d("呂", [box(26, 14, 74, 42), box(26, 58, 74, 86), [[42, 42], [42, 58]], [[58, 42], [58, 58]], [[34, 28], [66, 28]], [[34, 72], [66, 72]]], "two linked vertebrae: 'backbone'")
d("和", [C(50, 50, 40), arc(50, 30, 20, -90, 90), arc(50, 70, 20, -90, -270), C(40, 30, 3, 8), C(60, 70, 3, 8)], "two halves fitting together: 'harmony'")
d("遠", [[[10, 94], [46, 40]], [[90, 94], [54, 40]], [[50, 94], [50, 86]], [[50, 78], [50, 68]], [[50, 60], [50, 52]], [[4, 40], [96, 40]],
         [[24, 40], [36, 26], [48, 40]], [[44, 40], [58, 24], [74, 40]]], "a road running to the far horizon: 'far'")
d("乎", [[[50, 8], [50, 62]], C(50, 80, 5), [[30, 28], [24, 40], [30, 52]], [[20, 22], [12, 40], [20, 58]], [[70, 28], [76, 40], [70, 52]], [[80, 22], [88, 40], [80, 58]]], "an exclamation: a spoken particle")
d("无", dashed([box(14, 14, 86, 86)]), "an empty dashed box: 'nothing'")
d("尓", fig(70, 14, 72, ("down", "down")) + arrow(4, 50, 44, 50), "an arrow pointing at someone: 'you'")

# ================================================================ 2b. DATA: Latin letters (Phoenician origins)
LATIN = {}
def L_(ch, strokes, name, meaning, conf="standard"): LATIN[ch] = (strokes, name, meaning, conf)
L_("A", [[[50, 88], [26, 36], [74, 36], [50, 88]], [[26, 36], [12, 30], [10, 12]], [[74, 36], [88, 30], [90, 12]], C(40, 50, 3, 8), C(60, 50, 3, 8)], "aleph", "ox")
L_("B", [[[14, 90], [14, 44], [50, 12], [86, 44], [86, 90], [14, 90]], [[42, 90], [42, 62], [58, 62], [58, 90]]], "beth", "house")
L_("C", [[[16, 20], [34, 72], [84, 90]], arc(66, 30, 14, 200, 340)], "gimel", "throwing stick (or camel)", "disputed")
L_("D", [box(24, 10, 76, 90), [[24, 50], [76, 50]], C(64, 70, 3, 8)], "daleth", "door")
L_("E", [box(18, 18, 82, 82), [[50, 18], [50, 82]], [[18, 50], [82, 50]]], "he", "window (or a man with raised arms)", "disputed")
L_("F", [[[50, 10], [50, 70], [36, 86], [22, 74]], [[50, 10], [70, 22]]], "waw", "hook or peg")
L_("G", [[[14, 64], [14, 46], [28, 38], [38, 48], [48, 38], [62, 44], [66, 30], [80, 18], [90, 20], [88, 30], [78, 34], [76, 50], [76, 86], [68, 86], [66, 60], [30, 60], [28, 86], [20, 86], [14, 64]]], "gimel", "camel (or throwing stick)", "disputed")
L_("H", [[[24, 12], [24, 90]], [[76, 12], [76, 90]], [[24, 34], [76, 34]], [[24, 66], [76, 66]]], "heth", "fence")
L_("I", hand(50, 50, 1.0), "yodh", "hand or arm")
L_("J", [[[62, 10], [62, 66], [48, 88], [30, 78]], [[30, 78], [30, 66]]], "(a late variant of I)", "a hook", "disputed")
L_("K", hand(50, 50, 1.0) + [[[40, 64], [60, 64]], [[40, 74], [60, 74]]], "kaph", "palm of the hand")
L_("L", [[[84, 10], [20, 84]], [[20, 84], [12, 94], [26, 90], [20, 84]], [[84, 10], [92, 18]]], "lamedh", "ox goad")
L_("M", [wave(6, 94, 34, 9, 3), wave(6, 94, 64, 9, 3)], "mem", "water")
L_("N", [ell(46, 50, 32, 17), [[78, 50], [96, 34], [96, 66], [78, 50]], C(26, 46, 2.5, 8)], "nun", "fish or snake")
L_("O", [[[8, 50], [30, 28], [70, 28], [92, 50], [70, 72], [30, 72], [8, 50]], C(50, 50, 14), C(50, 50, 5, 10)], "ayin", "eye")
L_("P", [[[10, 50], [30, 36], [50, 42], [70, 36], [90, 50], [70, 66], [50, 70], [30, 66], [10, 50]], [[14, 50], [50, 56], [86, 50]]], "pe", "mouth")
L_("Q", [C(44, 46, 24), [[66, 40], [86, 26], [92, 40], [84, 54]]], "qoph", "back of the head, or a monkey", "disputed")
L_("R", [C(50, 36, 24), [[44, 60], [40, 92]], [[58, 60], [62, 92]], [[44, 14], [50, 6], [58, 14]]], "resh", "head")
L_("S", [[[24, 14], [76, 14], [78, 50], [66, 92], [56, 56], [44, 56], [34, 92], [22, 50], [24, 14]]], "shin", "tooth")
L_("T", [[[50, 14], [50, 90]], [[26, 36], [74, 36]]], "taw", "a mark or cross")
L_("U", [[[22, 18], [22, 62], [50, 86], [78, 62], [78, 18]]], "waw", "hook or peg (U split off from V)", "disputed")
L_("V", [[[50, 92], [22, 14]], [[50, 92], [78, 14]]], "waw", "hook or peg")
L_("W", [[[6, 14], [26, 92], [50, 34], [74, 92], [94, 14]]], "(double V)", "two pegs", "disputed")
L_("X", [[[18, 18], [82, 82]], [[82, 18], [18, 82]]], "samekh (disputed)", "a prop or a crossing", "disputed")
L_("Y", [[[50, 92], [50, 56]], [[50, 56], [24, 14]], [[50, 56], [76, 14]]], "waw", "a fork of the peg", "disputed")
L_("Z", [[[40, 94], [60, 10]], [[60, 10], [82, 18], [78, 40], [56, 30]]], "zayin", "weapon or axe", "disputed")

# ================================================================ 2c. DATA: glosses, romaji, particles
GLOSS = {}
for w in ("安 peace, safety|阿 hill, corner|以 by means of|伊 that one|宇 eaves, universe|衣 clothing|江 large river|於 at, in|加 to add|幾 how many|久 a long time|計 to measure, plan|"
          "介 between, mediate|己 self|左 left|散 to scatter|之 of, this|寸 inch|須 must, necessary|世 world, generation|曽 formerly|太 thick, great|多 many|知 to know|千 thousand|川 river|"
          "天 heaven, sky|止 to stop|奈 crabapple (sound only)|仁 benevolence|二 two|奴 servant, fellow|祢 ancestral shrine|乃 namely, of|波 wave|八 eight|比 to compare|不 not|部 section|"
          "保 to protect|末 end, tip|万 ten thousand|美 beautiful|三 three|武 martial|牟 lowing of an ox (sound only)|女 woman|毛 hair, fur|也 also, to be|由 reason, from|与 to give|良 good|"
          "利 benefit, sharp|留 to stay|流 to flow|礼 bow, etiquette|呂 spine, backbone|和 harmony|遠 far|乎 exclamation particle|无 nothing|尓 you, thus").split("|"):
    k, g = w.split(" ", 1); GLOSS[k] = g
for w in ("一 one|七 seven|上 up, above|下 down, below|中 middle, inside|九 nine|五 five|人 person|今 now|休 rest|何 what|入 enter|六 six|円 yen, circle|出 go out|"
          "分 minute, part|前 before, front|北 north|十 ten|午 noon|半 half|南 south|友 friend|口 mouth|古 old|右 right|名 name|四 four|国 country|土 earth, soil|外 outside|大 big|"
          "子 child|学 study|小 small|少 few|山 mountain|年 year|店 shop|後 after, behind|手 hand|新 new|日 sun, day|時 time, hour|書 to write|月 moon, month|"
          "木 tree|本 book, origin|来 to come|東 east|校 school|母 mother|毎 every|気 spirit, energy|水 water|火 fire|父 father|生 life, birth|男 man|白 white|百 hundred|目 eye|社 company, shrine|"
          "空 sky, empty|立 to stand|耳 ear|聞 to hear, ask|花 flower|行 to go|西 west|見 to see|言 to say|話 to talk|語 language, word|読 to read|買 to buy|足 foot, leg|車 car, vehicle|週 week|"
          "道 road, way|金 gold, money|長 long|間 interval, between|雨 rain|電 electricity|食 to eat, food|飲 to drink|駅 station|高 tall, expensive|魚 fish").split("|"):
    k, g = w.split(" ", 1); GLOSS.setdefault(k, g)

ROMAJI = ("a i u e o ka ki ku ke ko sa shi su se so ta chi tsu te to na ni nu ne no ha hi fu he ho ma mi mu me mo ya yu yo ra ri ru re ro wa wo n").split()
PARTICLE = {"は": "topic marker ('as for')", "が": "subject marker", "を": "object marker", "に": "to, at, in (target or time)", "で": "at, by means of",
            "の": "of, possessive", "と": "and, with, quotation", "も": "also, too", "へ": "toward", "から": "from, because", "まで": "until, up to",
            "や": "and (a partial list)", "か": "question marker", "ね": "right? (seeking agreement)", "よ": "emphasis ('you know')", "ばかり": "only, just"}

# ================================================================ 3. stage constructors
RES = None                                  # the project's resolver module (set by build)
SRC = "Wikipedia (kana pages), Wiktionary, EBSCO Research Starters: kana syllabary"

# ONE ordering rule for every shelf. Stages are sorted by this rank (stable), so the order never differs:
#   etymology -> meaning drawing -> real glyph -> man'yogana -> kana -> literal translation (always last)
RANK = {"etymology": 0, "symbol": 1, "language": 2, "kanji": 2, "letter": 2, "slang": 2.5, "manyogana": 3, "kana": 4, "translation": 9}

def blank(): return {"w": 100, "h": 100, "s": []}

def stg(role, label, sticks=None, prov="designed", note="", text=None, conf=None, source=None):
    x = {"role": role, "label": label, "sticks": sticks or blank(), "provenance": prov, "note": note}
    if text: x["text"] = text
    if conf: x["confidence"] = conf
    if source: x["source"] = source
    return x

def drawing(strokes, label, note, conf=None, kind="mnemonic"):
    """kind='mnemonic': invented picture of the meaning (role symbol, labelled NOT etymology).
       kind='origin'  : stylized picture of a traditional origin (role etymology)."""
    box_ = {"w": 100, "h": 100, "s": strokes}
    if kind == "origin":
        return stg("etymology", label, box_, "authored", note, conf=conf)
    if kind == "slang":
        return stg("slang", label, box_, "authored", note, conf=conf)
    return stg("symbol", label, box_, "designed", "Invented mnemonic, NOT etymology: " + note, conf=conf)

def translation(label, text, note=""):
    return stg("translation", label, None, "designed", note or "Literal translation.", text=text)

def traced_stage(ch, role, label, note, conf=None, source=None):
    try:
        return stg(role, label, RES.traced(ch)["sticks"], "traced", note, conf=conf, source=source)
    except Exception:
        return stg(role, label, None, "traced", note, text=ch, conf=conf, source=source)

def ordered(stages):
    out = []
    for s in stages:
        s.setdefault("provenance", "designed"); s.setdefault("label", "")
        if not s.get("sticks"): s["sticks"] = blank()
        out.append(s)
    return sorted(out, key=lambda s: RANK.get(s.get("role"), 2))

# ================================================================ 4a. kana (hiragana + katakana, voiced too)
BASE = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん"
RO = dict(zip(BASE, ROMAJI))
VOICE = {"k": "g", "s": "z", "t": "d", "h": "b"}

def kana_info(ch):
    """-> (base hiragana, romaji, is_katakana, has_voicing_mark)"""
    kata = "\u30A1" <= ch <= "\u30F6"
    c = chr(ord(ch) - 0x60) if kata else ch
    nf = unicodedata.normalize("NFD", c); base, mark = nf[0], nf[1:]
    r = RO.get(base)
    if r and mark:
        if r in ("shi", "chi"): r = "ji"
        elif r == "tsu": r = "zu"
        elif r == "fu": r = "bu" if mark == "\u3099" else "pu"
        elif mark == "\u3099": r = VOICE.get(r[0], r[0]) + r[1:]
        else: r = "p" + r[1:]
    return base, r or "?", kata, bool(mark)

def origin(base, kata):
    """source kanji of a kana, looked up in your tables (HIRA_ORIGIN / KATA_ORIGIN)"""
    key = chr(ord(base) + 0x60) if kata else base
    for modname in ("symbolism", "kanji_etymology", "tables"):
        try:
            t = getattr(__import__(modname), "KATA_ORIGIN" if kata else "HIRA_ORIGIN", None)
            if t and key in t: return t[key]
        except Exception:
            pass
    return getattr(RES, "KANA_ORIGIN", {}).get(key)

def source_stages(src, SY):
    """etymology + drawing + real glyph of the source kanji, without duplicates"""
    try: st = list(SY.chain(src)) if SY else []
    except Exception: st = []
    if not any(s.get("role") == "symbol" for s in st) and src in DRAW:
        s, n = DRAW[src]; st.append(drawing(s, f"{src}: {n}", n))
    if not any(s.get("role") in ("language", "kanji") for s in st):
        st.append(traced_stage(src, "language", src, f"The kanji {src}."))
    return st

def kana(ch, SY):
    base, rom, kata, marked = kana_info(ch)
    src = origin(base, kata); st = []
    if src:
        st += source_stages(src, SY)
        st.append(traced_stage(src, "manyogana", f"{src} used for its SOUND only (man'yogana)",
            f"Man'yogana: kanji used for their sounds, not their meanings. {src} ({GLOSS.get(src, '?')}) "
            f"was borrowed for the sound; the meaning is ignored. Kana developed from these in the Heian period.",
            "standard", SRC))
    how = ("a fragment of the kanji, taken as shorthand (katakana)" if kata
           else "the whole kanji written in flowing cursive (hiragana)")
    extra = " The voicing mark changes the consonant." if marked else ""
    st.append(traced_stage(ch, "kana", f"{src or '?'} \u2192 {ch}", f"{ch} is {how}.{extra}", "standard", SRC))
    st.append(translation(f"{ch} = the sound '{rom}'",
        f"{ch}\n= the sound \"{rom}\"\nnot a word, only a sound\nborrowed from {src or '?'} ({GLOSS.get(src, '?')})"))
    return st

# ================================================================ 4b. Latin letters
def latin(ch):
    s, name, meaning, conf = LATIN[ch]
    return [drawing(s, f"{ch}: {name} = {meaning}",
                    f"Stylized drawing of the traditional origin: Phoenician '{name}', {meaning}.", conf, kind="origin"),
            stg("letter", ch, None, "traced", f"The Latin letter {ch}.", text=ch),
            translation(f"{ch} = {name}: {meaning}", f"{ch}\nfrom {name}\nliterally: {meaning}")]

# ================================================================ 4c. kanji
def kanji(key, SY):
    try: st = list(SY.chain(key)) if SY else list(RES.resolve(key)[1])
    except Exception: st = [traced_stage(key, "language", key, f"The kanji {key}.")]
    if key in DRAW and not any(s.get("role") == "symbol" for s in st):
        s, n = DRAW[key]; st.append(drawing(s, f"{key}: {n}", n))
    g = GLOSS.get(key, "no gloss yet")
    st.append(translation(f"{key} = {g}", f"{key}\n{g}"))
    return st

# ================================================================ 4d. particles
def particle(key):
    try: st = list(RES.resolve(key)[1])
    except Exception: st = []
    g = PARTICLE.get(key, "no gloss yet")
    st.append(translation(f"{key} = {g}", f"{key}\n{g}"))
    return st

# ================================================================ 4e. grammar points and slang
def fmt(rec):
    """text of a data record: meaning/english fields first"""
    if isinstance(rec, str): return rec
    if not isinstance(rec, dict): return str(rec)
    keys = [k for k, v in rec.items() if v and not isinstance(v, (dict, list)) and k not in ("pattern", "level", "label")]
    keys.sort(key=lambda k: 0 if ("mean" in k.lower() or "english" in k.lower() or k.lower() in ("en", "gloss")) else 1)
    return "\n".join(f"{k}: {rec[k]}" for k in keys)

def grammar_or_slang(item):
    try: st = list(RES.resolve(item["key"])[1])
    except Exception: st = []
    st.append(translation(f"meaning: {item['label'][:40]}", fmt(item.get("rec")) or "no translation on file"))
    return st

# ================================================================ 4f. slang: the gloss is the slang meaning, but the ORIGIN differs from the kanji's own
SLANG_SRC = "common account of Japanese internet slang (not independently verified here)"

def _laughing_man():
    """ONE design: a laughing man whose mouth is the letter w (笑 -> w), grass growing from his head (-> 草)"""
    cx, cy, r = 50, 50, 28
    s = [C(cx, cy, r),                                                        # head
         arc(38, 44, 6, 200, 340), arc(62, 44, 6, 200, 340),                  # eyes squeezed shut with laughter
         [[34, 56], [42, 72], [50, 60], [58, 72], [66, 56]],                  # the mouth IS a w
         [[31, 49], [28, 58]], [[69, 49], [72, 58]],                          # tears of laughter
         [[8, 98], [18, 86], [36, 80]], [[92, 98], [82, 86], [64, 80]]]       # shoulders
    for x, lean in ((36, -8), (43, -3), (50, 2), (57, 6), (64, 9)):           # grass growing from the head
        y0 = round(cy - math.sqrt(r * r - (x - cx) ** 2), 1)
        s.append([[x, y0], [round(x + lean * .4, 1), y0 - 9], [x + lean, y0 - 17]])
    return s

# Add a slang word by adding an entry here. Without an entry, the builder reads an 'etymology' / 'origin'
# field from your data/slang.json record (and says so if there is none).
SLANG = {
 "草": {"literal": "grass",
        "gloss": "lol, that's funny",
        "kanji": ("艹 (plant) + 早 (gives the sound)", "Standard dictionary analysis: the plant radical on top, 早 as the sound part."),
        "chain": "笑 (warai) \u2192 w \u2192 wwww \u2192 草",
        "origin": "笑 (warai, 'laugh') is shortened to the letter w when typing. A long row of w's (wwww) "
                  "looks like grass growing in a field, and grass is 草 (kusa). So 草 came to mean 'lol'.",
        "strokes": _laughing_man(),
        "drawnote": "A laughing man whose mouth is the letter w (笑 \u2192 w), with grass growing from his head (\u2192 草).",
        "conf": "standard"},
}

def _field(rec, names):
    if isinstance(rec, dict):
        for k, v in rec.items():
            if k.lower() in names and isinstance(v, str) and v.strip(): return v.strip()
    return ""

def slang(item, SY):
    key, rec = item["key"], item.get("rec")
    info = SLANG.get(key, {})
    st = []
    # 1. the word's own kanji: normal etymology + real glyph (this is what the word LITERALLY is)
    if len(key) == 1 and "\u4e00" <= key <= "\u9fff":
        try: st += list(SY.chain(key)) if SY else []
        except Exception: pass
        if not any(s.get("role") in ("language", "kanji") for s in st):
            st.append(traced_stage(key, "language", key, f"The kanji {key}."))
        if info.get("kanji") and not any(s.get("role") == "etymology" for s in st):
            a, b = info["kanji"]
            st.append(stg("etymology", f"{key}: {a}", None, "authored", b, text=f"{a}\n{b}", conf="standard", source=SLANG_SRC))
    # 2. your existing scenes for the entry (no duplicates)
    try:
        seen = {(s.get("label"), s.get("provenance")) for s in st}
        st += [s for s in RES.resolve(key)[1] if (s.get("label"), s.get("provenance")) not in seen]
    except Exception:
        pass
    # 3. the SLANG origin: different from the kanji's own etymology
    origin = info.get("origin") or _field(rec, ("etymology", "origin", "etym", "why", "note"))
    chain = info.get("chain") or "slang origin"
    conf = info.get("conf")
    if origin:
        st.append(stg("slang", f"slang origin: {chain}", None, "authored",
                      "Why the word means this as slang. It is NOT the kanji's own etymology.",
                      text=f"{chain}\n{origin}", conf=conf, source=SLANG_SRC if info else "your data/slang.json"))
    else:
        st.append(stg("slang", "slang origin: none on file yet", None, "placeholder",
                      "No slang etymology recorded for this entry.",
                      text="no slang etymology on file yet\nadd an 'etymology' field to this entry in data/slang.json"))
    if info.get("strokes"):
        st.append(drawing(info["strokes"], f"{key}: {chain}", info.get("drawnote") or ("Drawing of the slang's real origin: " + chain), conf, kind="slang"))
    # 4. literal translation, last: the slang gloss, and the literal word
    gloss = info.get("gloss") or _field(rec, ("meaning", "gloss", "english", "en", "translation", "definition")) or fmt(rec).split("\n")[0]
    literal = info.get("literal") or GLOSS.get(key)
    lines = [key, f"SLANG meaning: {gloss or 'no gloss on file'}"]
    if literal: lines.append(f"literal word: {literal}")
    lines.append("the slang meaning comes from the slang origin, not from the kanji's etymology")
    if not info and isinstance(rec, dict):             # any other fields of the record, minus the gloss already shown
        more = {k: v for k, v in rec.items() if k.lower() not in ("meaning", "gloss", "english", "en", "translation", "definition", "etymology", "origin", "etym", "why", "note")}
        if fmt(more): lines.append(fmt(more))
    st.append(translation(f"{key} = {gloss}"[:70], "\n".join(lines)))
    return st

# ================================================================ 5. entry point used by library.py
def build(shelf, item, resolver, SY):
    global RES; RES = resolver
    key = item["key"]
    if shelf in ("Hiragana", "Katakana"): st = kana(key, SY)
    elif shelf == "Latin letters": st = latin(key)
    elif shelf == "Particles": st = particle(key)
    elif shelf.startswith("Kanji"): st = kanji(key, SY)
    elif shelf == "Slang": st = slang(item, SY)
    else: st = grammar_or_slang(item)
    return ordered(st)

if __name__ == "__main__":                  # python3 chains.py あ 安 A   -> prints the stage order for each
    import resolver as _R
    try: import symbolism as _S
    except Exception: _S = None
    for ch in sys.argv[1:] or ["あ"]:
        shelf = ("Hiragana" if "\u3041" <= ch <= "\u3096" else "Katakana" if "\u30A1" <= ch <= "\u30F6"
                 else "Latin letters" if ch.isascii() and ch.isalpha() else "Kanji N5")
        print(f"== {ch} ({shelf})")
        for i, s in enumerate(build(shelf, {"key": ch, "label": ch}, _R, _S), 1):
            print(f"  {i}. {(s.get('role') or 'scene').upper():<12} {s['label']}")
