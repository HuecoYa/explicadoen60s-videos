# "Inventa la tarjeta del banco": una mesa, la tarjeta va ganando piezas (relieve, banda, chip, antena).
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from mathutils import Vector

BLUE = (0.18, 0.42, 0.92); WHITE = (0.95, 0.95, 0.97); SILVER = (0.86, 0.87, 0.9); GOLD = (1.0, 0.78, 0.28)
COPPER = (0.95, 0.52, 0.22); DARK = (0.2, 0.22, 0.26); WOOD = (1.0, 0.8, 0.58); RED = (0.92, 0.3, 0.32)
IMP = Vector((-15, 2, 0)); SW = Vector((14, -9, 0)); TM = Vector((14, 4, 0))
CW, CH = 8.56, 5.4

def card_model(color, number=True, chip=True, antenna=True, stripe=True, label="BANCO", unique=False):
    root = empty(); S = {"root": root}
    base = rounded_slab(CW, CH, 0.35, 0.04, (0, 0, 0), WHITE, root)
    S["base"] = base
    if antenna:
        ant = []
        for k in range(4):
            ins = 0.35 + k * 0.17; w, h = CW - 2 * ins, CH - 2 * ins
            for (sx, sy, lx, ly) in ((w, 0.07, 0, h / 2), (w, 0.07, 0, -h / 2), (0.07, h, w / 2, 0), (0.07, h, -w / 2, 0)):
                ant.append(box((sx, sy, 0.008), (lx, ly, 0.045), COPPER, root, unique=False))
        ant.append(box((1.8, 0.07, 0.008), (-2.6 - 1.2, 0.0, 0.045), COPPER, root))
        S["ant"] = ant
    hinge = empty((-CW / 2, 0, 0.05), root); S["hinge"] = hinge
    skin = rounded_slab(CW, CH, 0.35, 0.035, (CW / 2, 0, 0), color, hinge, unique=unique); S["skin"] = skin
    text3d(label, (CW / 2 - 3.1, 1.85, 0.036), 0.5, WHITE, hinge, extrude=0.0)
    for k in range(3):
        box((CW - 0.7, 0.05, 0.004), (CW / 2, -0.25 - 0.0 + k * 0.0 - 1.95, 0.037), tuple(min(1, c + 0.12) for c in color), hinge) if k == 0 else None
    if number:
        nums = []
        for g, s in enumerate(["4000", "1234", "5678", "9010"]):
            o = text3d(s, (CW / 2 - 2.85 + g * 1.9, -0.55, 0.035), 0.62, SILVER, hinge, extrude=0.03); nums.append(o)
        o = text3d("TU NOMBRE", (CW / 2 - 3.6, -1.75, 0.035), 0.34, SILVER, hinge, extrude=0.02, align='LEFT'); nums.append(o)
        S["nums"] = nums
    if chip:
        die = empty((CW / 2 - 2.6, 0.45, 0.035), hinge); S["die"] = die
        box((1.0, 0.78, 0.03), (0, 0, 0.015), (0.08, 0.09, 0.1), die)
        for k in range(4):
            box((0.85, 0.025, 0.006), (0, -0.28 + k * 0.18, 0.033), (0.25, 0.85, 0.45), die)
        key = empty((0, 0, 0.12), die); S["key"] = key
        torus(0.12, 0.035, (-0.22, 0, 0), GOLD, key, rot=(math.pi / 2, 0, 0))
        box((0.38, 0.06, 0.06), (0.05, 0, 0), GOLD, key); box((0.05, 0.06, 0.09), (0.16, 0, -0.06), GOLD, key); box((0.05, 0.06, 0.07), (0.07, 0, -0.05), GOLD, key)
        lid_h = empty((CW / 2 - 2.6 - 0.6, 0.45, 0.035), hinge); S["lid_h"] = lid_h
        lid = rounded_slab(1.2, 0.95, 0.15, 0.03, (0.6, 0, 0), GOLD, lid_h)
        for (sx, sy, lx, ly) in ((1.2, 0.03, 0.6, 0.16), (1.2, 0.03, 0.6, -0.16), (0.03, 0.3, 0.35, 0.33), (0.03, 0.3, 0.85, 0.33), (0.03, 0.3, 0.35, -0.33), (0.03, 0.3, 0.85, -0.33)):
            box((sx, sy, 0.01), (lx, ly, 0.032), (0.78, 0.55, 0.15), lid_h)
        S["chip_all"] = [die, lid_h]
    if stripe:
        sp = empty((-CW / 2, 1.45, -0.004), root); S["stripe"] = sp
        box((CW, 1.0, 0.008), (CW / 2, 0, 0), (0.08, 0.08, 0.09), sp)
        bits = []
        rng = random.Random(3)
        for k in range(26):
            x = 0.5 + k * 0.29
            if rng.random() < 0.55: bits.append(box((0.12, 0.6, 0.004), (x, 0, -0.005), (0.85, 0.85, 0.9), sp))
        S["bits"] = bits
        box((CW * 0.45, 0.6, 0.006), (CW * 0.32, -2.6, 0.0), (0.98, 0.98, 0.95), sp)   # banda de firma
    return S

def build():
    sc, cam = scene_setup(world=(0.62, 0.82, 0.98))
    S = {"cam": cam}
    # mesa de madera con tablones y cielo con nubes (estilo de los ejemplos)
    box((120, 60, 1.0), (0, 5, -0.5), WOOD)
    for k in range(-12, 13):
        box((120, 0.12, 0.02), (0, 5 + k * 2.4, 0.0), (0.86, 0.62, 0.4))
    rng = random.Random(5)
    for k in range(9):
        cx, cz = rng.uniform(-70, 70), rng.uniform(18, 40)
        for j in range(5):
            sph(rng.uniform(4, 7), (cx + j * 4.5 - 9, 90, cz + rng.uniform(-1.5, 1.5)), (1, 1, 1), scale=(1.3, 0.5, 0.8))
    # dinero del principio
    coins = []
    for k in range(6):
        coins.append(cyl(1.15, 0.22, (-8 + k * 0.1, -4.5 + k * 0.05, 0.11 + k * 0.23), (0.98, 0.8, 0.35)))
    bill = box((7.0, 3.6, 0.03), (8.5, -5.0, 0.02), (0.55, 0.82, 0.6), rot=(0, 0, 0.2))
    S["money"] = coins + [bill]; S["money_home"] = [Vector(o.location) for o in S["money"]]
    # máquina de calco
    box((12, 9, 0.8), IMP + Vector((0, 0, 0.4)), (0.55, 0.58, 0.64)); box((10.4, 7.2, 0.1), IMP + Vector((0, 0, 0.85)), (0.4, 0.43, 0.48))
    box((12, 0.5, 0.5), IMP + Vector((0, 4.3, 1.05)), (0.45, 0.48, 0.54)); box((12, 0.5, 0.5), IMP + Vector((0, -4.3, 1.05)), (0.45, 0.48, 0.54))
    paper = empty(); S["paper"] = paper
    box((9.4, 6.0, 0.02), (0, 0, 0), (0.99, 0.98, 0.9), paper)
    S["print"] = text3d("4000 1234 5678 9010", (0, -0.55, 0.016), 0.62, (0.2, 0.25, 0.65), paper, extrude=0.0)
    cover = box((1, 5.0, 0.004), (0, 0, 0.022), (0.99, 0.98, 0.9), unique=True); S["cover"] = cover
    roller = empty(); S["roller"] = roller
    cyl(0.55, 7.6, (0, 0, 0), (0.28, 0.3, 0.34), roller, rot=(math.pi / 2, 0, 0))
    box((0.3, 0.3, 3.0), (0, 0, 1.5), (0.6, 0.62, 0.66), roller); sph(0.5, (0, 0, 3.1), RED, roller)
    # lector de banda
    box((11, 2.6, 0.4), SW + Vector((0, 0, 0.2)), (0.3, 0.32, 0.36))
    box((11, 1.0, 3.0), SW + Vector((0, -0.8, 1.5)), (0.36, 0.38, 0.43)); box((11, 1.0, 3.0), SW + Vector((0, 0.8, 1.5)), (0.36, 0.38, 0.43))
    S["sw_led"] = sph(0.3, SW + Vector((4.5, -0.8, 3.1)), (0.3, 0.3, 0.3), unique=True)
    sk = empty(); S["skimmer"] = sk
    box((2.6, 0.9, 3.4), (0, -0.78, 1.7), (0.06, 0.06, 0.07), sk); box((2.6, 0.9, 3.4), (0, 0.78, 1.7), (0.06, 0.06, 0.07), sk)
    sph(0.22, (0.6, -0.78, 3.45), (1, 0.15, 0.1), sk)
    # datáfono
    rounded_slab(7, 13, 0.9, 2.0, TM, (0.22, 0.24, 0.28))
    S["screen"] = rounded_slab(5.4, 4.0, 0.3, 0.06, TM + Vector((0, 3.4, 2.0)), (0.14, 0.17, 0.22), unique=True)
    keys = []
    for r in range(4):
        for c in range(3):
            col = (0.86, 0.87, 0.9)
            if r == 3: col = [(0.95, 0.3, 0.3), (0.98, 0.8, 0.25), (0.3, 0.85, 0.45)][c]
            keys.append(rounded_slab(1.4, 0.9, 0.2, 0.25, TM + Vector((-1.85 + c * 1.85, -0.3 - r * 1.25, 2.0)), col))
    S["keys"] = keys; S["keys_home"] = [Vector(k.location) for k in keys]
    box((6.0, 0.4, 0.35), TM + Vector((0, -6.45, 1.15)), (0.05, 0.05, 0.06))
    rings = [torus(1.0, 0.07, TM + Vector((0, 3.4, 2.1)), (0.45, 0.78, 1.0)) for _ in range(4)]; S["rings"] = rings
    # pila
    bat = empty(); S["bat"] = bat
    cyl(0.75, 2.6, (0, 0, 0), (0.25, 0.75, 0.45), bat, rot=(0, math.pi / 2, 0)); cyl(0.3, 0.3, (1.45, 0, 0), SILVER, bat, rot=(0, math.pi / 2, 0))
    cyl(0.76, 0.6, (-1.0, 0, 0), DARK, bat, rot=(0, math.pi / 2, 0))
    # tarjetas
    S["card"] = card_model(BLUE)
    S["clone1"] = card_model((0.9, 0.35, 0.4), chip=False, antenna=False, stripe=False, label="COPIA")
    S["clone2"] = card_model((0.25, 0.26, 0.3), chip=False, antenna=False, label="???")
    S["ant_mat"] = None
    join_static([cam, S["money"], paper, cover, roller, S["sw_led"], sk, S["screen"], keys, rings, bat,
                 S["card"]["root"], S["clone1"]["root"], S["clone2"]["root"]])
    # material propio para la antena (para que brille)
    m = mat(COPPER, unique=True)
    for o in S["card"]["ant"]: o.data.materials[0] = m
    S["ant_mat"] = m
    return sc, S

# ---------------- animación ----------------
P2 = math.pi / 2
HOME = Vector((0, 0, 0)); HOMEF = Vector((0, 0, 0.09)); HERO = Vector((0, 0, 3.5))
IMP_C = IMP + Vector((0, 0, 0.9)); INS_OUT = TM + Vector((0, -12.0, 1.0)); INS_IN = TM + Vector((0, -6.5 - 4.28 + 3.0, 1.0))
ABOVE = TM + Vector((0, 3.4, 6.0)); FAR = TM + Vector((0, 3.4, 16.0))
SW_A = SW + Vector((-12, 0, 3.1)); SW_B = SW + Vector((9.5, 0, 3.1)); SW_0 = SW + Vector((-8.5, 0, 3.1))

CARD_POS = [(0, HERO), (2.2, HERO), (4.6, HOME), (8.9, HOME), (9.6, IMP_C), (12.6, IMP_C), (13.6, HOME), (16.8, HOME),
            (17.0, HOME + Vector((0, 0, 3))), (17.5, HOMEF), (19.4, HOMEF), (20.2, SW_0), (20.6, SW_0), (21.6, SW_B), (22.1, SW_B),
            (22.8, HOMEF), (26.6, HOMEF), (27.0, SW_A), (27.3, SW_A), (28.4, SW_B), (29.0, SW_B), (30.4, HOME + Vector((0, 0, 2))),
            (30.9, HOME), (40.0, HOME), (40.3, INS_OUT), (40.8, INS_IN), (44.4, INS_IN), (44.9, INS_OUT + Vector((-9, 0, -1))),
            (46.6, INS_OUT + Vector((-9, 0, -1))), (47.0, INS_OUT), (47.6, INS_IN), (50.4, INS_IN), (50.8, INS_OUT), (51.4, HOME),
            (56.9, HOME), (58.0, ABOVE), (63.9, ABOVE), (64.5, FAR), (65.0, FAR), (65.5, ABOVE), (66.2, ABOVE), (67.0, HOME),
            (71.0, HOME), (71.8, HERO), (80, HERO)]
CARD_ROT = [(0, (P2, 0, -0.6)), (2.2, (P2, 0, 0.3)), (4.6, (0, 0, 0)), (16.8, (0, 0, 0)), (17.5, (math.pi, 0, 0)), (19.4, (math.pi, 0, 0)),
            (20.2, (-P2, 0, 0)), (22.1, (-P2, 0, 0)), (22.8, (math.pi, 0, 0)), (26.6, (math.pi, 0, 0)), (27.0, (-P2, 0, 0)),
            (29.0, (-P2, 0, 0)), (30.9, (0, 0, 0)), (40.0, (0, 0, 0)), (40.3, (0, 0, -P2)), (44.4, (0, 0, -P2)), (44.9, (0, 0, -P2 + 0.3)),
            (46.6, (0, 0, -P2 + 0.3)), (47.0, (0, 0, -P2)), (50.8, (0, 0, -P2)), (51.4, (0, 0, 0)), (66.2, (0, 0, 0)), (67.0, (0, 0, 0)),
            (71.0, (0, 0, 0)), (71.8, (P2, 0, -0.5)), (80, (P2, 0, 0.9))]

def pose_card(C, pos, rot):
    C["root"].location = pos; C["root"].rotation_euler = rot

def pose(t, S):
    C = S["card"]
    pose_card(C, keyed(t, CARD_POS), keyed(t, [(a, Vector(r)) for a, r in CARD_ROT]))
    # números en relieve
    for k, o in enumerate(C["nums"]):
        u = seg(t, 5.7 + k * 0.35, 6.1 + k * 0.35); o.scale = (u, u, u)
    # chip
    u = seg(t, 31.5, 31.95); bounce = 1 + 0.25 * math.sin(min(1, max(0, (t - 31.95) / 0.3)) * math.pi)
    for o in C["chip_all"]: o.scale = (u * bounce,) * 3
    C["lid_h"].rotation_euler = (0, -1.9 * (seg(t, 34.8, 35.5) - seg(t, 39.2, 39.8)), 0)
    C["key"].rotation_euler = (0, 0, t * 2.0); ks = seg(t, 35.3, 35.8) * (1 - seg(t, 39.1, 39.5)); C["key"].scale = (ks * 1.6,) * 3
    C["key"].location = (0, 0, 0.12 + 0.35 * ks)
    # banda magnética y bits
    C["stripe"].scale = (max(1e-3, seg(t, 17.6, 18.5)), 1, 1)
    for k, b in enumerate(C["bits"]):
        u = seg(t, 23.2 + k * 0.05, 23.5 + k * 0.05); b.scale.z = 0.004 * u if False else b.scale.z; b.scale.x = 0.12 * u if u > 0 else 1e-4
    # piel levantada para enseñar la antena
    C["hinge"].rotation_euler = (0, -1.25 * (seg(t, 51.6, 52.4) - seg(t, 63.9, 64.6)), 0)
    glow = 0.5 + 0.5 * math.sin(t * 9)
    if 59.3 <= t < 63.9 or 65.5 <= t < 66.5:
        c = tuple(mix(a, b, glow) for a, b in zip(COPPER, (1.0, 0.95, 0.5)))
    else: c = COPPER
    S["ant_mat"].diffuse_color = (*lin(c), 1)
    # dinero
    for o, h in zip(S["money"], S["money_home"]):
        drop = seg(t, 2.6, 3.3); gone = seg(t, 4.2, 4.7)
        o.location = h + Vector((0, 0, 8 * (1 - drop))); s = max(1e-3, (drop > 0) * (1 - gone)); o.scale = o.scale if False else o.scale
        o.hide_render = not (2.6 <= t < 4.7)
    # máquina de calco: papel, rodillo, tapa del texto
    pin = seg(t, 9.6, 10.2); pout = seg(t, 12.7, 13.3)
    S["paper"].location = IMP + Vector((0, -9 * (1 - pin) - 9.5 * pout, 1.03 - 1.0 * pout)) if t > 9.5 else Vector((0, 0, -50))
    rx = IMP.x - 4.9 + 9.8 * seg(t, 10.4, 12.3)
    S["roller"].location = Vector((rx if t < 12.4 else IMP.x + 4.9, IMP.y, 1.03 + 0.58))
    cov = S["cover"]; right = IMP.x + 4.7
    if 9.5 < t < 12.35:
        w = max(0.01, right - rx); cov.scale = (w, 5.0, 0.004); cov.location = S["paper"].location + Vector((rx - IMP.x + w / 2, 0, 0.022))
    else: cov.location = (0, 0, -50)
    # copias
    c1 = S["clone1"]; u1 = seg(t, 14.6, 15.4); g1 = seg(t, 16.4, 16.9)
    pose_card(c1, Vector((9.6 * u1, 1.0 * u1, 0.0)) if (14.55 < t and g1 < 1) else Vector((0, 0, -50)), (0, 0, 0.15 * u1))
    c1["root"].scale = (1 - g1 + 1e-3,) * 3
    c2 = S["clone2"]
    if t < 29.2: pose_card(c2, Vector((0, 0, -50)), (0, 0, 0))
    else:
        cl = keyed(t, [(29.2, SW + Vector((-7, -3, 4))), (30.0, Vector((5, -15, 4))), (30.4, Vector((5.5, -15, 0.09))), (44.3, Vector((5.5, -15, 0.09))),
                       (44.6, INS_OUT), (45.1, INS_IN), (45.9, INS_IN), (46.4, INS_OUT), (46.9, Vector((5.5, -15, 0.09))), (80, Vector((5.5, -15, 0.09)))])
        cr = keyed(t, [(29.2, Vector((-P2, 0, 0))), (30.4, Vector((math.pi, 0, 0.3))), (44.3, Vector((math.pi, 0, 0.3))), (44.6, Vector((0, 0, -P2))),
                       (46.4, Vector((0, 0, -P2))), (46.9, Vector((math.pi, 0, 0.3))), (80, Vector((math.pi, 0, 0.3)))])
        pose_card(c2, cl, cr)
    # skimmer
    S["skimmer"].location = keyed(t, [(26.0, SW + Vector((-7.2, 0, 40))), (26.8, SW + Vector((-7.2, 0, 0))), (29.6, SW + Vector((-7.2, 0, 0))),
                                      (30.4, SW + Vector((-7.2, 0, 40))), (80, SW + Vector((-7.2, 0, 40)))])
    # led del lector y pantalla del datáfono
    set_color(S["sw_led"], (0.3, 0.95, 0.4) if (21.6 <= t < 22.6 or 28.4 <= t < 29.2) else (0.3, 0.3, 0.3))
    scr = (0.14, 0.17, 0.22)
    for a in (41.0, 42.0, 43.0, 50.0, 62.6, 65.5):
        if a <= t < a + 0.6: scr = (0.3, 0.88, 0.45)
    if 45.4 <= t < 46.3: scr = (0.95, 0.3, 0.3)
    set_color(S["screen"], scr)
    for k, (o, h) in enumerate(zip(S["keys"], S["keys_home"])):
        d = 0
        for a, kk in ((48.2, 0), (48.6, 4), (49.0, 8), (49.4, 1), (50.0, 11)):
            if kk == k and a <= t < a + 0.18: d = -0.15
        o.location = h + Vector((0, 0, d))
    # ondas del datáfono
    act = 58.0 <= t < 66.2
    for k, r in enumerate(S["rings"]):
        if not act: r.location = (0, 0, -50); continue
        ph = ((t - 58.0) * 0.8 + k / 4) % 1.0
        top = 5.6 if not (64.3 <= t < 65.2) else 9.0
        r.location = TM + Vector((0, 3.4, 2.15 + ph * top)); r.scale = (1 + 2.6 * ph,) * 3
    # pila
    b = seg(t, 55.1, 55.5) * (1 - seg(t, 56.5, 56.9))
    S["bat"].location = Vector((-1.5, -6.0, 0.75)) if b > 0 else Vector((0, 0, -50)); S["bat"].scale = (max(b, 1e-3),) * 3
    apply_cam(S["cam"], *cam_state(t, CAM, drift=0.06))

CAM = [
    (0.0, (0, -16, 5), (0, 0, 3.3), 35), (2.2, (2, -14, 7), (0, 0, 2.2), 35), (4.6, (0, -11, 12), (0, -0.3, 0), 35), (8.3, (-1, -10, 11), (0, -0.3, 0), 35),
    (9.8, (-13, -8.5, 11), (-15, 1.5, 1), 35), (12.6, (-12.5, -9, 10.5), (-15, 0, 1), 35), (13.9, (4.8, -11, 17), (4.8, 0.3, 0), 35),
    (16.4, (4.6, -10.5, 16), (4.8, 0.3, 0), 35), (17.7, (0, -10, 9), (0, 0, 0), 35), (19.9, (9, -22, 8), (14, -9, 2.6), 35), (22.0, (8, -21, 8), (13, -9, 2.6), 35),
    (22.8, (0, -9.5, 9), (0, 0, 0), 35), (25.8, (0, -9, 8), (0, 0.3, 0), 35), (26.6, (6, -24, 9), (10, -9, 2.6), 35), (29.2, (5, -24, 9), (9, -9, 2.6), 35),
    (30.4, (3, -25, 10), (5, -13, 1), 35), (31.4, (0, -10, 10), (0, 0, 0), 35), (33.4, (-2.6, -4.6, 5.2), (-2.6, 0.45, 0.1), 35),
    (39.6, (-2.4, -4.2, 4.6), (-2.6, 0.45, 0.1), 35), (40.4, (6, -15, 11), (13.5, -2.5, 1.5), 35), (44.2, (7, -15, 11), (13.5, -2.5, 1.5), 35),
    (46.8, (6, -16, 12), (11, -4, 1.5), 35), (47.6, (14, -9, 13), (14, -0.5, 1.8), 35), (50.4, (14, -8, 12), (14, -0.5, 1.8), 35),
    (51.4, (3, -10, 10), (0, 0, 0.6), 35), (54.8, (1, -9, 9), (0, 0, 0.8), 35), (56.6, (0, -12, 9), (-0.5, -1.5, 0.6), 35),
    (58.2, (5, -12, 10), (14, 3.5, 5.0), 35), (63.6, (7, -11, 9), (14, 3.5, 5.0), 35), (65.6, (6, -13, 13), (14, 3.5, 9), 35),
    (67.4, (1, -12, 10), (0, 0, 0.5), 35), (70.9, (1, -15, 8), (0, 0, 2.5), 35), (74.5, (0, -16, 5), (0, 0, 3.3), 35), (80, (0, -16, 5), (0, 0, 3.3), 35),
]

def _scale_cam(ks, f=1.38, keep=(33.4, 39.6)):
    out = []
    for t, p, g, l in ks:
        if t in keep: out.append((t, p, g, l)); continue
        P, G = Vector(p), Vector(g); out.append((t, tuple(G + (P - G) * f), g, l))
    return out
CAM = _scale_cam(CAM)

def anchors(sc, S, t):
    cam = S["cam"]; P = lambda v: proj(sc, cam, v)
    C = S["card"]; M = C["root"].matrix_world
    return {"card": P(M.translation), "nums": P(M @ Vector((0, -0.55, 0.1))), "stripe": P(M @ Vector((0, 1.45, -0.01))),
            "chip": P(M @ Vector((-2.6, 0.45, 0.1))), "key": P(C["key"].matrix_world.translation), "ant": P(M @ Vector((3.0, -2.2, 0.05))),
            "clone1": P(S["clone1"]["root"].matrix_world.translation), "clone2": P(S["clone2"]["root"].matrix_world.translation),
            "screen": P(TM + Vector((0, 3.4, 2.1))), "keys": P(TM + Vector((0, -2, 2.2))), "bat": P(S["bat"].matrix_world.translation),
            "card_bot": P(M.translation + Vector((0, 0, -0.05))), "paper": P(S["paper"].matrix_world.translation), "sw": P(SW + Vector((0, 0, 3.2)))}

if __name__ == "__main__":
    run("tarjeta", build, pose, anchors)
