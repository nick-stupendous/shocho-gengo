"""N5 kanji scenes. 100x100 box, y points down. Every scene is provenance 'designed'.
kind = 'pictograph'  -> drawing follows the attested/traditional origin of the character
kind = 'mnemonic'    -> my invention to aid memory; NOT etymology"""
import math
from geometry import circle, rect, arrow, star, fig, dashed

S = {}
def add(ch, kind, note, strokes): S[ch] = (kind, note, strokes)

def P(*pts): return [[float(x), float(y)] for x, y in pts]
def poly(*pts): s = P(*pts); return s + [s[0]]
def dot(x, y, r=2.6): return circle(x, y, r, 8)
def arc(cx, cy, r, a0, a1, n=18, ry=None):
    ry = r if ry is None else ry
    return [[cx + r*math.cos(math.radians(a0+(a1-a0)*i/n)), cy + ry*math.sin(math.radians(a0+(a1-a0)*i/n))] for i in range(n+1)]
def tree(x, b, h, w=None):
    w = w or h*.32
    return [P((x,b),(x,b-h)), P((x,b-h*.62),(x-w,b-h*.88)), P((x,b-h*.62),(x+w,b-h*.88)),
            P((x,b),(x-w*.7,b+h*.2)), P((x,b),(x+w*.7,b+h*.2))]
def sun(cx, cy, r, rays=8, ra=1.35, rb=1.85):
    s = [circle(cx, cy, r, 18)]
    for i in range(rays):
        a = 2*math.pi*i/rays
        s.append(P((cx+r*ra*math.cos(a), cy+r*ra*math.sin(a)), (cx+r*rb*math.cos(a), cy+r*rb*math.sin(a))))
    return s
def crescent(cx, cy, r, w=.45):
    return [arc(cx, cy, r, 90, 270, 16) + arc(cx, cy, w*r, 270, 90, 16, ry=r)]
def cloud(cx, cy, s=1.0):
    pts = [(-34,12),(-38,0),(-26,-10),(-14,-8),(-4,-18),(12,-14),(18,-4),(32,-4),(38,6),(32,12),(-34,12)]
    return [P(*[(cx+x*s, cy+y*s) for x, y in pts])]
def eye(cx, cy, w=60, iris=True):
    h = w*.32; up, lo = [], []
    for i in range(17):
        t = i/16; x = cx-w/2+w*t; k = 1-(2*t-1)**2
        up.append([x, cy-h*k]); lo.append([x, cy+h*k*.8])
    s = [up, lo]
    if iris: s += [circle(cx, cy, h*.62, 12), circle(cx, cy, h*.25, 8)]
    return s
def ear(cx, cy, s=1.0):
    pts = [(0,-38),(26,-26),(30,0),(16,22),(10,38),(-6,42),(-14,28)]
    inner = [(6,-20),(16,-8),(10,8),(0,14)]
    f = lambda L: [[cx+x*s, cy+y*s] for x, y in L]
    return [f(pts), f(inner)]
def woman(x, by, s=1.0):
    p = lambda dx, dy: (x+dx*s, by+dy*s)
    return [circle(*p(0,-62), 7*s, 10), P(p(0,-55), p(3,-24)),
            P(p(-15,-45), p(10,-33)), P(p(15,-47), p(-9,-33)),
            P(p(3,-24), p(20,-10), p(-14,-4))]
def road(pts, w0, w1):
    n = len(pts)-1; L, R = [], []
    for i, (x, y) in enumerate(pts):
        w = w0+(w1-w0)*i/n; L.append([x-w, y]); R.append([x+w, y])
    return [L, R]
def wave(x0, y0, y1, amp=4, n=20, ph=0):
    return [[x0+amp*math.sin(ph+i*.9), y0+(y1-y0)*i/n] for i in range(n+1)]
def bubble(x, y, w, h, tail='l'):
    t = [(x+w*.25, y+h), (x+w*.15, y+h+14), (x+w*.45, y+h)] if tail == 'l' else [(x+w*.75, y+h), (x+w*.85, y+h+14), (x+w*.55, y+h)]
    return [P((x, y), (x+w, y), (x+w, y+h), t[2], t[1], t[0], (x, y+h), (x, y))]
def hexpts(cx, cy, r, n, a0=-90): return [(cx+r*math.cos(math.radians(a0+360*i/n)), cy+r*math.sin(math.radians(a0+360*i/n))) for i in range(n)]

# ---------------- row 1: numbers ----------------
add("一","pictograph","one counting rod", [rect(8,43,84,14)])
add("二","pictograph","two counting rods", [rect(14,26,72,14), rect(8,62,84,14)])
add("三","pictograph","three counting rods", [rect(18,14,64,13), rect(12,43,76,13), rect(6,72,88,13)])
add("四","mnemonic","a window with four panes", [rect(16,16,68,68), P((50,16),(50,84)), P((16,50),(84,50))])
pt = hexpts(50, 54, 36, 5)
add("五","mnemonic","a pentagon: five corners, five dots", [poly(*pt)] + [dot(x, y, 4) for x, y in pt])
pt = hexpts(50, 50, 38, 6, 0)
add("六","mnemonic","a hexagon: six sides", [poly(*pt), dot(50, 50, 3)])
H = [(6,24),(24,30),(42,38),(56,40),(84,42),(78,64),(46,58)]
add("七","mnemonic","the seven stars of the Big Dipper", [P(*H[:4]), P(H[3], H[4], H[5], H[6], H[3])] + [dot(x, y, 3.5) for x, y in H])
add("八","pictograph","something splitting apart (八 = divide)", [P((46,16),(28,50),(12,86)), P((54,16),(72,50),(88,86)), arrow(40,60,26,60,5), arrow(60,60,74,60,5)])
add("九","mnemonic","nine dots in a 3x3 grid", [dot(x, y, 5) for x in (24,50,76) for y in (24,50,76)])
add("十","pictograph","a crossing: the set is complete", [P((50,8),(50,92)), P((8,50),(92,50)), circle(50,50,7,10)])

# ---------------- row 2 ----------------
add("百","mnemonic","a bar over a bright sun-disc: one hundred suns", [P((22,16),(78,16)), circle(50,56,26,16), dot(50,56,3)])
add("千","mnemonic","a swarm of a thousand specks", [dot(14+14*i, 18+13*j, 1.8) for i in range(6) for j in range(6)])
add("万","pictograph","a scorpion; 萬 was borrowed for 'ten thousand'", [
    circle(38,62,11,10), circle(22,62,6,8), P((18,58),(10,46),(5,56)), P((18,68),(10,78)),
    P((49,58),(64,56),(76,42),(72,26),(60,20),(52,28)), P((52,28),(47,36)),
    P((34,72),(30,86)), P((40,73),(40,88)), P((46,72),(50,86))])
add("日","pictograph","the sun (original: a disc with a dot)", sun(50,50,20) + [dot(50,50,3)])
add("月","pictograph","the crescent moon", crescent(56,50,38) + [dot(76,28,2.5), dot(84,56,2.5), dot(70,80,2.5)])
add("火","pictograph","flames", [poly((50,92),(24,72),(30,46),(42,58),(46,22),(58,48),(68,34),(78,72)), P((50,86),(40,72),(50,54),(60,72),(50,86))])
add("水","pictograph","a flowing stream with spray", [wave(50,8,92,3,22), P((50,40),(30,60),(16,74)), P((50,40),(70,60),(84,74)), dot(26,28,3), dot(74,28,3)])
add("木","pictograph","a tree: trunk, branches, roots", tree(50,74,62,22))
add("金","mnemonic","gold nuggets buried under a lid of earth", [P((50,10),(14,40)), P((50,10),(86,40)), P((24,50),(76,50)), dot(36,64,4), dot(64,64,4), dot(50,80,4), star(50,28,6)])
add("土","pictograph","a mound of earth with a sprout", [P((8,76),(92,76)), arc(50,76,26,180,360,14,ry=18), P((50,58),(50,36)), P((50,44),(38,34)), P((50,44),(62,34))])

# ---------------- row 3 ----------------
add("本","pictograph","a tree with its root marked: the origin", tree(50,66,56,20) + [P((34,90),(66,90))])
add("語","mnemonic","a speech bubble full of lines of text", bubble(10,12,80,46,'l') + [P((22,26),(78,26)), P((22,36),(70,36)), P((22,46),(56,46))])
add("人","pictograph","a person seen from the side", fig(50,92,1.7,arms=((-14,14),(14,14))))
add("女","pictograph","a kneeling woman with crossed arms", woman(46,90,1.1))
add("男","pictograph","a rice field and a plough: the man who works it", [rect(8,14,40,40), P((28,14),(28,54)), P((8,34),(48,34)), P((66,14),(66,74)), P((66,74),(84,90)), P((66,74),(48,90)), P((56,14),(76,14))])
add("子","pictograph","a swaddled child with arms up", [circle(50,24,13,12), P((50,37),(50,72)), P((50,48),(24,36)), P((50,48),(76,36)), P((50,72),(40,90)), P((50,72),(60,90)), P((42,12),(46,6)), P((54,12),(58,6))])
add("友","pictograph","two hands joined: a friend", fig(24,92,1.0,arms=((-8,12),(22,14))) + fig(76,92,1.0,arms=((-22,14),(8,12))))
add("国","pictograph","a walled territory with a flag at its centre", [rect(8,8,84,84), P((44,76),(44,26)), poly((44,26),(70,36),(44,46)), P((26,76),(66,76))])
add("学","pictograph","a child studying under a roof", [P((12,40),(50,10),(88,40)), P((30,32),(26,24)), P((70,32),(74,24))] + fig(50,92,0.95,arms=((-12,-8),(12,-8))))
add("校","mnemonic","a schoolhouse with a flag", [poly((10,44),(50,16),(90,44)), rect(18,44,64,44), rect(42,60,16,28), rect(24,54,12,12), rect(64,54,12,12), P((50,16),(50,4)), poly((50,4),(62,8),(50,12))])

# ---------------- row 4 ----------------
add("小","pictograph","three tiny grains", [dot(50,30,3.5), dot(34,62,3.5), dot(66,62,3.5)])
add("大","pictograph","a person with arms stretched wide", [circle(50,14,8,10), P((50,22),(50,62)), P((10,40),(90,40)), P((50,62),(24,94)), P((50,62),(76,94))])
add("少","mnemonic","few grains left; one blows away", [P((16,80),(84,80)), dot(30,70,3.5), dot(44,70,3.5), dot(62,52,3), dot(72,38,2.5), dot(78,26,2)])
add("多","mnemonic","evenings piled on evenings: many", crescent(36,28,18) + crescent(60,66,22))
add("時","mnemonic","a clock face", [circle(50,50,36,24), P((50,50),(50,24)), P((50,50),(68,60))] + [P((50+30*math.cos(a), 50+30*math.sin(a)), (50+35*math.cos(a), 50+35*math.sin(a))) for a in [math.pi/6*i for i in range(12)]])
add("分","mnemonic","a disc divided in two, halves drifting apart", [arc(44,50,32,90,270,16)+[[44,18]], arc(56,50,32,-90,90,16)+[[56,82]]])
add("年","mnemonic","a ripe grain stalk: one harvest, one year", [P((50,92),(50,12))] + [P((50,y),(50-16,y-10)) for y in (74,54,34)] + [P((50,y),(50+16,y-10)) for y in (74,54,34)])
add("名","mnemonic","a name tag", [poly((14,26),(70,26),(88,50),(70,74),(14,74)), dot(72,50,3), P((24,42),(56,42)), P((24,56),(48,56))])
add("前","mnemonic","a queue; the front figure walks ahead", fig(26,92,0.8) + fig(62,92,1.1) + arrow(78,40,96,40,6))
add("後","mnemonic","footprints trailing behind a walker", fig(72,92,1.2) + dashed([P((6,88),(50,88))], 5, 5))

# ---------------- row 5 ----------------
add("山","pictograph","three peaks", [P((6,88),(28,42),(40,58),(52,12),(66,50),(76,34),(94,88)), P((6,88),(94,88))])
add("川","pictograph","three flowing streams", [wave(24,8,92,3,22), wave(50,8,92,3,22,1.2), wave(76,8,92,3,22,2.4)])
add("花","mnemonic","a flower on its stem", [circle(50,32,7,10)] + [circle(50+17*math.cos(math.radians(a)), 32+17*math.sin(math.radians(a)), 10, 10) for a in (-90,-18,54,126,198)] + [P((50,50),(50,92)), P((50,80),(34,68),(50,72)), P((50,68),(66,58),(50,62))])
add("魚","pictograph","a fish", [poly((12,50),(32,32),(60,32),(76,50),(60,68),(32,68)), dot(26,46,2.5), P((76,50),(94,34),(94,66),(76,50)), P((40,36),(36,64)), P((50,34),(46,66))])
add("上","pictograph","a mark above the line", [P((10,68),(90,68)), circle(50,42,11,12), arrow(50,26,50,6,5)])
add("中","pictograph","an arrow through the centre of a target", [rect(16,28,68,44), P((50,6),(50,94))])
add("下","pictograph","a mark below the line", [P((10,32),(90,32)), circle(50,58,11,12), arrow(50,74,50,94,5)])
add("左","mnemonic","L for Left, arrow pointing left", [P((26,22),(26,78),(62,78)), arrow(94,50,50,50,6)])
add("右","mnemonic","a tick: the right answer, arrow pointing right", [P((22,40),(34,54),(58,24)), arrow(8,78,92,78,6)])
add("外","mnemonic","a figure left outside the house", [rect(8,26,46,50), poly((4,26),(31,8),(58,26)), rect(24,50,14,26)] + fig(80,92,0.85))

# ---------------- row 6 ----------------
add("雨","pictograph","a cloud shedding raindrops", cloud(50,24,1.1) + [P((24+17*i, 48), (20+17*i, 62)) for i in range(5)] + [P((34+17*i, 68), (30+17*i, 82)) for i in range(3)])
add("電","pictograph","lightning from a rain cloud", cloud(50,20,1.1) + [poly((56,36),(38,64),(52,64),(42,92),(68,54),(54,54),(64,36))])
add("天","pictograph","the sky as a bar above a person", [P((12,18),(88,18)), circle(50,38,7,10), P((50,45),(50,70)), P((20,56),(80,56)), P((50,70),(30,92)), P((50,70),(70,92))])
add("店","mnemonic","a shop with a striped awning and door", [P((8,40),(18,22),(82,22),(92,40)), rect(14,40,72,50), rect(42,58,16,32), rect(20,50,16,14), rect(64,50,16,14), P((34,22),(30,40)), P((50,22),(50,40)), P((66,22),(70,40))])
add("手","pictograph","an open hand with fingers and thumb", [P((30,92),(30,54)), P((70,92),(70,54)), P((30,54),(70,54)), P((34,54),(34,22)), P((44,54),(44,10)), P((54,54),(54,8)), P((64,54),(64,18)), P((30,70),(12,50))])
add("古","mnemonic","an old weathered gravestone", [P((26,90),(26,38),(32,22),(50,14),(68,22),(74,38),(74,90),(26,90)), P((50,38),(50,68)), P((38,50),(62,50)), P((8,90),(92,90))])
add("新","mnemonic","an axe striking a tree: fresh cut", tree(30,78,54,16) + [P((66,16),(84,72)), poly((60,24),(72,12),(78,34)), star(80,22,5)])
add("買","mnemonic","a coin traded into a shopping bag", [circle(28,40,14,14), rect(22,34,12,12), arrow(46,40,60,40,5), P((62,46),(60,90),(90,90),(88,46),(62,46)), P((68,46),(72,30),(82,30),(84,46))])
add("生","pictograph","a sprout rising from the ground", [P((8,76),(92,76)), P((50,76),(50,34)), P((50,56),(32,54),(22,38),(40,38),(50,56)), P((50,42),(68,40),(78,24),(60,24),(50,42)), P((50,76),(40,90)), P((50,76),(60,90))])
add("午","mnemonic","noon: the sun overhead, a stick casting almost no shadow", sun(50,24,10) + [P((8,92),(92,92)), P((50,92),(50,56)), P((50,92),(58,92))])

# ---------------- row 7 ----------------
add("口","pictograph","an open mouth", [poly((12,48),(32,34),(50,40),(68,34),(88,48),(68,66),(32,66)), P((12,48),(88,48))])
add("入","pictograph","walking in through a gap", [P((62,8),(62,38)), P((62,62),(62,92)), arrow(8,50,84,50,7)])
add("出","pictograph","rising out of a pit", [P((16,60),(16,90),(84,90),(84,60)), arrow(50,78,50,8,8)])
add("長","pictograph","a long-haired elder with a staff", fig(38,92,1.5,arms=((-12,16),(14,14))) + [P((46,24),(64,30),(72,52),(76,82)), P((18,34),(18,92))])
add("高","mnemonic","a tall tower", [rect(34,24,32,68), P((30,24),(50,6),(70,24)), rect(42,36,16,10), rect(42,54,16,10), rect(42,72,16,10)])
add("円","mnemonic","a round coin with a square hole", [circle(50,50,38,24), rect(38,38,24,24)])
add("北","pictograph","two people back to back; also the compass needle north", [circle(50,50,38,24), poly((50,16),(40,50),(60,50)), P((50,50),(50,84)), P((12,50),(18,50)), P((82,50),(88,50))])
add("南","mnemonic","compass needle pointing south", [circle(50,50,38,24), poly((50,84),(40,50),(60,50)), P((50,50),(50,16)), P((12,50),(18,50)), P((82,50),(88,50))])
add("東","pictograph","the sun rising behind a tree", tree(50,76,60,24) + sun(50,32,10, 8, 1.4, 1.9))
add("西","pictograph","the sun sinking below the horizon", [P((6,66),(94,66))] + [arc(50,66,22,180,360,14)] + [P((50+30*math.cos(math.radians(a)), 66+30*math.sin(math.radians(a))), (50+42*math.cos(math.radians(a)), 66+42*math.sin(math.radians(a)))) for a in (200,230,270,310,340)])

# ---------------- row 8 ----------------
add("食","mnemonic","a bowl of steaming food and chopsticks", [arc(50,52,30,0,180,16,ry=30), P((20,52),(80,52)), wave(36,10,40,3,10), wave(50,6,40,3,10,1), wave(64,10,40,3,10,2), P((70,20),(88,60)), P((78,18),(94,56))])
add("飲","mnemonic","a cup with a straw", [P((28,30),(34,90),(66,90),(72,30)), P((28,30),(72,30)), P((34,56),(66,56)), P((58,6),(54,70))])
add("駅","mnemonic","a train at the platform", [rect(20,20,60,56), rect(28,28,18,16), rect(54,28,18,16), circle(34,84,7,10), circle(66,84,7,10), P((4,94),(96,94)), dot(32,62,3), dot(68,62,3)])
add("目","pictograph","an eye", eye(50,50,80))
add("見","mnemonic","an eye with its line of sight reaching an object", eye(26,40,44) + dashed([P((50,40),(76,40))],4,3) + [circle(84,40,7,10), P((34,70),(34,92)), P((20,70),(20,92))])
add("耳","pictograph","an ear", ear(50,50,1.15))
add("聞","mnemonic","an ear pressed to a door", [rect(8,10,38,82), dot(38,52,2.5)] + ear(72,50,0.9) + dashed([arc(46,52,16,-60,60,6)],3,3))
add("足","pictograph","a footprint with toes", [P((34,28),(60,28),(64,52),(72,72),(70,90),(40,92),(30,72),(34,52),(34,28)), dot(36,18,4), dot(46,14,4), dot(56,14,4), dot(66,18,4)])
add("行","pictograph","a crossroads; setting off along the road", [P((34,8),(34,92)), P((66,8),(66,92)), P((8,34),(92,34)), P((8,66),(92,66)), arrow(50,88,50,40,7)])
add("来","pictograph","a wheat plant (borrowed for 'come')", [P((50,92),(50,10))] + [P((50,y),(50-14,y-12)) for y in (70,50,30)] + [P((50,y),(50+14,y-12)) for y in (70,50,30)] + [P((50,10),(44,2)), P((50,10),(56,2))])

# ---------------- row 9 ----------------
add("社","pictograph","a shrine gate (社 = shrine; later 'company')", [P((10,24),(90,24)), P((20,36),(80,36)), P((30,24),(30,92)), P((70,24),(70,92)), P((4,18),(14,24)), P((96,18),(86,24))])
add("休","pictograph","a person resting against a tree", tree(72,84,64,24) + fig(32,92,1.2,arms=((-8,14),(28,6))))
add("車","pictograph","a cart seen from above: body, axle, two wheels", [rect(36,24,28,52), P((12,50),(88,50)), P((16,14),(16,86)), P((84,14),(84,86)), P((12,14),(20,14)), P((12,86),(20,86)), P((80,14),(88,14)), P((80,86),(88,86))])
add("道","pictograph","a road winding to the horizon", road([(50,94),(56,76),(40,60),(56,44),(50,26),(50,12)], 24, 3) + [P((8,94),(92,94))])
add("空","mnemonic","a bird crossing an empty sky", cloud(32,26,.65) + cloud(66,74,.7) + [P((30,52),(42,42),(50,54),(58,42),(70,52))])
add("言","pictograph","sound waves leaving a mouth", [poly((10,70),(26,60),(40,70),(26,80))] + [arc(30,70,r,-50,50,8) for r in (14,24,34)])
add("話","mnemonic","two speech bubbles: a conversation", bubble(6,10,52,30,'l') + bubble(42,54,52,30,'r') + [P((14,22),(48,22)), P((50,66),(84,66))])
add("読","mnemonic","an open book read aloud", [P((50,50),(50,90)), P((50,50),(22,42),(8,46),(8,86),(22,82),(50,90),(78,82),(92,86),(92,46),(78,42),(50,50))] + [arc(50,34,r,-140,-40,8) for r in (10,20,30)])
add("書","mnemonic","a brush writing on paper", [rect(10,34,52,56), P((18,50),(54,50)), P((18,62),(54,62)), P((18,74),(44,74)), P((92,8),(58,60)), P((58,60),(54,72))])
add("立","pictograph","a person standing firmly on the ground", [P((8,88),(92,88)), circle(50,22,8,10), P((50,30),(50,66)), P((20,46),(80,46)), P((50,66),(34,88)), P((50,66),(66,88))])

# ---------------- row 10 ----------------
add("母","pictograph","a woman with the two nursing marks", woman(46,90,1.1) + [dot(36,56,2.5), dot(54,60,2.5)])
add("父","pictograph","a hand gripping an axe: father", fig(34,92,1.5,arms=((-12,14),(26,-2))) + [P((72,14),(72,86)), poly((72,16),(92,10),(92,38),(72,34))])
add("毎","mnemonic","a cycle that repeats: every time", [arc(50,50,32,30,360,24), arrow(50+32*math.cos(math.radians(330))-6, 50+32*math.sin(math.radians(330))-8, 50+32*math.cos(math.radians(360)), 50+32*math.sin(math.radians(360))-2, 6)])
add("気","pictograph","steam rising from a rice bowl: vapour, spirit", [arc(50,62,30,0,180,16,ry=26), P((20,62),(80,62)), wave(38,52,16,3,10), wave(50,50,10,3,10,1), wave(62,52,16,3,10,2)])
add("白","mnemonic","a sun with its first ray of light", [circle(50,56,26,18), dot(50,56,3), P((50,26),(50,8))])
add("何","mnemonic","a person asking a question", fig(34,92,1.4) + [P((58,30),(58,22),(68,12),(82,16),(84,28),(72,38),(72,50)), dot(72,62,3)])
add("週","mnemonic","a week: seven boxes in a row", [rect(8,34,84,32)] + [P((8+12*i,34),(8+12*i,66)) for i in range(1,7)] + [circle(14,26,2.5,8), circle(86,26,2.5,8)])
add("間","mnemonic","the sun glimpsed between two gate doors", [P((8,12),(8,90)), P((92,12),(92,90)), P((8,12),(92,12)), P((8,12),(38,20),(38,84),(8,90)), P((92,12),(62,20),(62,84),(92,90))] + sun(50,50,8,8,1.4,1.9))
add("半","mnemonic","a circle cut in half, one half shaded", [circle(50,50,32,28), P((50,18),(50,82))] + [P((50-math.sqrt(32*32-(y-50)**2)+3, y), (46, y)) for y in (30,40,50,60,70)])
add("今","mnemonic","a map pin: you are here, now", [circle(50,34,16,14), dot(50,34,5), P((38,46),(50,82),(62,46)), arc(50,88,16,0,360,18,ry=5)])

# ---------------- revisions after looking at the rendered sheets ----------------
def woman(x, by, s=1.0):
    p = lambda dx, dy: (x+dx*s, by+dy*s)
    return [circle(*p(0,-70), 9*s, 10), P(p(0,-61), p(2,-30)),
            P(p(-18,-50), p(16,-38)), P(p(18,-52), p(-16,-38)),
            P(p(2,-30), p(28,-14), p(-16,-4))]
add("女","pictograph","a kneeling woman with crossed arms", woman(40,94,1.15))
add("母","pictograph","the same kneeling woman, with the two nursing marks", woman(40,94,1.15) + [dot(34,52,2.4), dot(48,56,2.4)])
add("水","pictograph","a flowing stream with spray", [P((50,8),(50,66),(42,90)), P((50,34),(30,54),(16,62)), P((50,34),(70,54),(84,62)), dot(24,30,3), dot(76,30,3)])
add("男","pictograph","a rice field and a strong arm: the man who works it", [rect(8,14,40,40), P((28,14),(28,54)), P((8,34),(48,34)), P((56,90),(62,58),(84,44)), circle(88,42,6,10), arc(64,64,9,190,330,8)])
add("子","pictograph","a swaddled child with arms up", [circle(50,24,13,12), P((50,37),(50,72)), P((50,48),(24,36)), P((50,48),(76,36)), P((50,72),(40,90)), P((50,72),(60,90))])
add("友","pictograph","two hands joined: a friend", fig(24,92,1.0,arms=((-8,12),(26,14))) + fig(76,92,1.0,arms=((-26,14),(8,12))))
add("分","mnemonic","a disc divided in two, halves drifting apart", [(lambda a: a+[a[0]])(arc(42,50,32,90,270,16)), (lambda a: a+[a[0]])(arc(58,50,32,-90,90,16))])
rd = [(50+16*math.sin(i/14*5)*(1-i/14*.6), 94-82*i/14) for i in range(15)]
add("道","pictograph","a road winding to the horizon", [[[x-(22*(1-i/14)+2), y] for i,(x,y) in enumerate(rd)], [[x+(22*(1-i/14)+2), y] for i,(x,y) in enumerate(rd)]])
def ear(cx, cy, s=1.0):
    f = lambda L: [[cx+x*s, cy+y*s] for x, y in L]
    outer = [[34*math.cos(math.radians(a))-6, 42*math.sin(math.radians(a))] for a in range(-100, 101, 10)]
    outer += [[-6+34*math.cos(math.radians(100)), 42*math.sin(math.radians(100))], [-20,30], [-26,0], [-18,-30], [34*math.cos(math.radians(-100))-6, 42*math.sin(math.radians(-100))]]
    inner = [[18*math.cos(math.radians(a))-6, 26*math.sin(math.radians(a))] for a in range(-80, 91, 10)]
    return [f(outer), f(inner), f([[-8,0],[-2,6]])]
add("耳","pictograph","an ear", ear(48,50,1.05))
add("聞","mnemonic","an ear pressed to a door", [rect(8,10,38,82), dot(38,52,2.5)] + ear(72,50,0.9) + dashed([arc(46,52,16,-60,60,6)],3,3))
add("足","pictograph","a footprint with toes", [P((30,40),(32,28),(48,24),(66,28),(70,42),(64,60),(60,74),(54,90),(42,92),(36,78),(32,60),(30,40)), dot(32,14,4), dot(44,10,4.4), dot(56,10,4.4), dot(67,14,4)])
