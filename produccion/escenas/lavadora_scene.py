# «Si tuvieras que inventar la lavadora…»: primer plano del ojo de buey con la ropa centrifugando y la lavadora que
# tiembla y anda; desaparece la carcasa y se construye pieza a pieza: tambor con agua y detergente, paletas que levantan
# y dejan caer la ropa, centrifugado (agujeros, el agua sale disparada, la ropa pegada a la pared, fuerza ×400), la ropa
# se amontona y todo vibra, cuba colgada de muelles con amortiguadores, bloques de hormigón (25 kg) que frenan la vibración,
# vuelve la carcasa, y el motor gira despacio a un lado y a otro para repartir la ropa (si no, centrifuga más lento).
import bpy, bmesh, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T0, DUR = cargar("lavadora")
_TC = {}
def T(k, n=1, fin=False):
    key = (k, n, fin)
    if key not in _TC: _TC[key] = T0(k, n, fin)
    return _TC[key]

WHITE = (0.93, 0.94, 0.96); STEEL = (0.7, 0.73, 0.78); STEEL_IN = (0.84, 0.86, 0.9); DARK = (0.12, 0.13, 0.16)
TUB = (0.4, 0.43, 0.5); TUB_IN = (0.55, 0.58, 0.64); WATER = (0.3, 0.6, 0.95); FOAM = (0.97, 0.98, 1.0)
CONC = (0.62, 0.62, 0.6); SPRING = (0.95, 0.75, 0.25); DAMP = (0.25, 0.27, 0.32); ROD = (0.85, 0.87, 0.9); RED = (0.95, 0.3, 0.28)
FLOOR_A = (0.24, 0.25, 0.29); FLOOR_B = (0.2, 0.21, 0.25); WALLC = (0.13, 0.14, 0.18)
CLOTH = [(0.95, 0.35, 0.35), (0.3, 0.6, 0.95), (0.98, 0.8, 0.25), (0.4, 0.8, 0.5), (0.85, 0.5, 0.9), (0.98, 0.6, 0.3),
         (0.35, 0.85, 0.85), (0.95, 0.95, 0.95), (0.55, 0.45, 0.9), (0.95, 0.45, 0.65), (0.6, 0.8, 0.3), (0.3, 0.4, 0.75)]
D = Vector((0, 0.3, 4.3))          # centro del tambor
R = 2.3; DEP = 3.4                 # radio y fondo del tambor
NB = 12
LEJOS = Vector((0, 300, -300))
rng = random.Random(12)
BDEP = [rng.uniform(-1.1, 1.1) for _ in range(NB)]
BSZ = [rng.uniform(0.42, 0.6) for _ in range(NB)]
PILE = [Vector((rng.uniform(-1.9, 0.3), rng.uniform(-5.4, -4.4), 0.35 + 0.35 * (k % 3))) for k in range(NB)]

def tube(r, depth, loc, color, inner, th, parent=None, v=48):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, rotation=(math.pi / 2, 0, 0), vertices=v, end_fill_type='NOTHING')
    o = bpy.context.object; setup(o, color, parent, True, unique=False)
    m = o.modifiers.new("sol", "SOLIDIFY"); m.thickness = th; m.offset = 1
    o.data.materials.append(mat(inner)); m.material_offset = 1; m.material_offset_rim = 1
    return o

def cone(r, h, loc, color, parent=None):
    bpy.ops.mesh.primitive_cone_add(radius1=r, radius2=0, depth=h, location=loc, vertices=16); o = bpy.context.object
    for vv in o.data.vertices: vv.co.z += h / 2
    o.location = loc; return setup(o, color, parent, True, True)

# ---------- velocidad del tambor (vueltas por segundo «visuales») y ángulo acumulado ----------
def omega(t):
    if t < T("vamos a inventarla"): return 0.9
    if t < T("así que la metes"): return 0.0
    if t < T("así que haces"): return 0.3
    if t < T("pero hay un"): return mix(0.3, 0.9, seg(t, T("así que haces"), T("el tambor tiene")))
    if t < T("así que antes"): return 0.75
    if t < T("si no lo consigue"): return 0.0
    if t < T("o no centrifuga"): return mix(0.75, 0.4, seg(t, T("centrifuga más"), T("lento", fin=True)))
    if t < T("sígueme"): return mix(0.4, 0.0, seg(t, T("o no centrifuga"), T("o no centrifuga") + 0.8))
    return 0.35
THETA = [0.0]
for f in range(1, int((DUR + 2) * FPS) + 2): THETA.append(THETA[-1] + omega(f / FPS) * math.tau / FPS)
def theta(t):
    f = max(0, min(len(THETA) - 1, int(t * FPS)))
    th = THETA[f]
    a0, a1 = T("así que antes"), T("si no lo consigue")
    if a0 <= t < a1: th += 1.1 * math.sin((t - a0) * 2.4) * seg(t, a0, a0 + 0.5) * (1 - seg(t, a1 - 0.4, a1))
    return th

def wobble_amp(t):
    a = 0.0
    a += 0.45 * seg(t, T("la ropa nunca"), T("y todo empieza") + 0.4) * (1 - seg(t, T("así que cuelgas"), T("como un coche")) * 0.4)
    a *= 1 - 0.85 * seg(t, T("ese peso"), T("se mueva mucho", fin=True))
    a += 0.38 * seg(t, T("si la ropa está"), T("amontonada", fin=True)) * (1 - seg(t, T("el motor gira"), T("para repartirla")))
    if t >= T("si no lo consigue"): a = 0.1 * (1 - seg(t, T("o no"), T("o no") + 0.8))
    if t < T("vamos a inventarla"): a = 0.0
    return a

def blob_world(i, t, th, Dc):
    """posición de la prenda i (centro del tambor Dc, ángulo del tambor th)"""
    y = BDEP[i]; rr = R - 0.32 - 0.12 * (i % 3)
    def polar(phi, r=rr): return Dc + Vector((r * math.cos(phi), y, r * math.sin(phi)))
    # 1) caída por el ojo de buey en el gancho: pegada a la pared girando
    wall = polar(i / NB * math.tau - th)
    # 2) volteo: sube con la paleta y cae
    u = (t * 0.55 + i / NB) % 1.0
    if u < 0.6:
        phi = -math.pi / 2 - (u / 0.6) * math.radians(150); tum = polar(phi)
    else:
        top = polar(-math.pi / 2 - math.radians(150)); w = (u - 0.6) / 0.4
        bot = polar(-math.pi / 2 - 0.15)
        tum = Vector((mix(top.x, bot.x, w), top.y, top.z - (top.z - bot.z) * w * w))
    rest = polar(-math.pi / 2 + (i / NB - 0.5) * 1.6, R - 0.4 - 0.25 * (i % 2))
    clump_w = polar(math.radians(20) + (i / NB - 0.5) * 0.9 - th, rr)
    a = T("así que la metes"); b = a + 0.9
    if t < T("vamos a inventarla") + 0.2: return wall
    if t < a: return PILE[i] if t >= T("quieres lavar") - 0.3 else LEJOS
    if t < b:
        w = seg(t, a + i * 0.04, b); p = PILE[i].lerp(rest, w); p.z += 2.5 * math.sin(math.pi * w); return p
    if t < T("al girar"): return rest
    if t < T("así que haces"):
        return rest.lerp(tum, seg(t, T("al girar"), T("al girar") + 0.6))
    if t < T("la ropa nunca"):
        return tum.lerp(wall, seg(t, T("así que haces"), T("así que haces") + 1.0))
    if t < T("así que antes"):
        return wall.lerp(clump_w, seg(t, T("la ropa nunca"), T("nunca se reparte", fin=True)))
    if t < T("si no lo consigue"):
        sp = seg(t, T("el motor gira") + 0.3, T("para repartirla"))
        clump_rest = polar(-math.pi / 2 + (i / NB - 0.5) * 0.7 + 1.1 * math.sin((t - T("así que antes")) * 2.4) * 0.6, rr)
        even = polar(i / NB * math.tau - th, rr)
        if sp < 1: return clump_rest.lerp(even, sp)
        return even
    if t < T("sígueme"):
        return polar(i / NB * math.tau * 0.75 - th, rr)
    return wall

def build():
    sc, cam = scene_setup(world=(0.09, 0.1, 0.13), shadow=0.35)
    S = {"cam": cam}
    # cocina: suelo en damero y pared
    box((40, 40, 0.4), (0, 4, -0.2), FLOOR_A)
    for i in range(-10, 10):
        for j in range(-6, 12):
            if (i + j) % 2 == 0: box((2.0, 2.0, 0.02), (i * 2 + 1, j * 2 + 1, 0.01), FLOOR_B)
    box((40, 0.4, 20), (0, 6.5, 10), WALLC)
    # ---- grupo suspendido (cuba + tambor + hormigón) ----
    sus = empty(D); S["sus"] = sus
    drum = empty((0, 0, 0), sus); S["drum"] = drum
    tube(R, DEP, (0, 0, 0), STEEL, STEEL_IN, 0.09, drum)
    cyl(R + 0.05, 0.12, (0, DEP / 2 + 0.06, 0), STEEL, drum, rot=(math.pi / 2, 0, 0), v=48)
    torus(R + 0.02, 0.1, (0, -DEP / 2, 0), STEEL, drum, rot=(math.pi / 2, 0, 0))
    cyl(0.35, 0.2, (0, DEP / 2 - 0.05, 0), STEEL_IN, drum, rot=(math.pi / 2, 0, 0))
    for k in range(3):                                         # paletas
        a = k / 3 * math.tau
        p = box((0.35, DEP * 0.9, 0.55), (0, 0, 0), STEEL_IN, drum)
        p.location = ((R - 0.27) * math.cos(a), 0, (R - 0.27) * math.sin(a)); p.rotation_euler = (0, -a, 0)
    S["holes"] = []
    for ring in range(6):                                       # agujeros (por dentro)
        yy = -DEP / 2 + 0.45 + ring * (DEP - 0.9) / 5
        for k in range(12):
            a = (k + 0.5 * (ring % 2)) / 12 * math.tau + 0.13
            h = cyl(0.09, 0.03, ((R - 0.035) * math.cos(a), yy, (R - 0.035) * math.sin(a)), DARK, drum, rot=(0, math.pi / 2 - a, 0), v=10)
    # agua dentro del tambor
    S["water"] = cyl(R - 0.14, DEP * 0.85, (0, 0, 0), WATER, sus, rot=(math.pi / 2, 0, 0), v=40)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 5.0)); wc = bpy.context.object; wc.scale = (8, 8, 10); wc.hide_render = True; wc.parent = sus
    m = S["water"].modifiers.new("cut", "BOOLEAN"); m.operation = 'DIFFERENCE'; m.object = wc; S["wcut"] = wc
    S["foam"] = [sph(0.16 + 0.05 * (k % 3), (0, 0, 0), FOAM, sus) for k in range(10)]
    # cuba (cortada) con soportes para muelles
    bpy.ops.mesh.primitive_cube_add(size=1, location=(3.0, -3.0, 3.0)); cutter = bpy.context.object; cutter.scale = (6, 8, 6); cutter.hide_render = True
    tub = tube(R + 0.35, DEP + 0.3, (0, 0.05, 0), TUB, TUB_IN, 0.12, sus)
    m = tub.modifiers.new("cut", "BOOLEAN"); m.operation = 'DIFFERENCE'; m.object = cutter
    S["tub"] = tub; S["cutter"] = cutter
    cutter.parent = sus
    # hormigón
    conc = empty((0, 0, 0), sus); S["conc"] = conc
    cb1 = box((3.4, 2.2, 0.75), (0, 0.6, R + 0.85), CONC, conc)
    cb2 = box((3.6, 0.6, 1.0), (0, -DEP / 2 - 0.5, -R - 0.2), CONC, conc)
    for k in range(26):
        b = cb1 if k < 14 else cb2
        p = Vector(b.location) + Vector((rng.uniform(-1.6, 1.6), -b.scale.y / 2 - 0.005, rng.uniform(-0.3, 0.3)))
        box((0.12, 0.02, 0.1), p, (0.48, 0.48, 0.46), conc)
    # ropa
    S["blobs"] = [sph(BSZ[i], LEJOS, CLOTH[i % len(CLOTH)], scale=(1.0, 0.8, 0.55), unique=True) for i in range(NB)]
    # gotas
    S["drops"] = [sph(0.09, LEJOS, WATER) for _ in range(24)]
    # flecha de fuerza
    S["farr"] = bar_obj(RED, r=0.11); S["ftip"] = cone(0.28, 0.5, LEJOS, RED)
    # bastidor: base, travesaño, muelles y amortiguadores
    frame = empty(LEJOS); S["frame"] = frame
    box((5.8, 5.6, 0.25), (0, 0.3, 0.15), DARK, frame)
    for x in (-2.75, 2.75):
        box((0.25, 0.25, 8.2), (x, 3.0, 4.2), DARK, frame)
    box((5.8, 0.4, 0.3), (0, 0.3, 8.35), DARK, frame)
    box((5.8, 5.4, 0.15), (0, 0.3, 8.55), DARK, frame)
    S["springs"] = []
    for x in (-1.7, 1.7):
        e = empty(LEJOS)
        for k in range(12): torus(0.24, 0.05, (0, 0, (k + 0.5) / 12), SPRING, e)
        S["springs"].append((x, e))
    S["dampers"] = []
    for x in (-1.5, 1.5):
        sl = bar_obj(DAMP, r=0.2); rod = bar_obj(ROD, r=0.08)
        S["dampers"].append((x, sl, rod))
    # carcasa
    cab = empty(LEJOS); S["cab"] = cab
    box((6.0, 5.6, 0.2), (0, 0.3, 8.5), WHITE, cab)
    for x in (-2.95, 2.95): box((0.1, 5.6, 8.5), (x, 0.3, 4.25), WHITE, cab)
    box((6.0, 0.1, 8.5), (0, 3.05, 4.25), WHITE, cab)
    box((6.0, 0.25, 1.0), (0, -2.45, 7.9), (0.85, 0.87, 0.9), cab)
    cyl(0.38, 0.2, (1.8, -2.62, 7.9), (0.55, 0.58, 0.64), cab, rot=(math.pi / 2, 0, 0))
    box((1.6, 0.05, 0.45), (-0.8, -2.6, 7.9), (0.15, 0.25, 0.35), cab)
    box((6.0, 0.25, 0.6), (0, -2.45, 0.3), (0.85, 0.87, 0.9), cab)
    # frontal con el ojo de buey
    bpy.ops.mesh.primitive_cylinder_add(radius=1.85, depth=3, location=(D.x, -2.5, D.z), rotation=(math.pi / 2, 0, 0)); hc = bpy.context.object; hc.hide_render = True; hc.parent = cab
    front = box((6.0, 0.15, 7.0), (0, -2.55, 4.1), WHITE, cab)
    m = front.modifiers.new("hole", "BOOLEAN"); m.operation = 'DIFFERENCE'; m.object = hc
    S["front"] = front
    torus(1.95, 0.2, (D.x, -2.68, D.z), (0.75, 0.78, 0.84), cab, rot=(math.pi / 2, 0, 0))
    torus(1.7, 0.12, (D.x, -2.75, D.z), (0.3, 0.33, 0.4), cab, rot=(math.pi / 2, 0, 0))
    join_static([cam, sus, S["blobs"], S["drops"], S["farr"], S["ftip"], frame, [e for _, e in S["springs"]],
                 [o for _, a, b in S["dampers"] for o in (a, b)], cab, cutter, hc, S["water"], wc])
    return sc, S

def pose(t, S):
    th = theta(t)
    amp = wobble_amp(t)
    wph = th
    off = Vector((amp * math.cos(wph), 0, amp * math.sin(wph) * 0.6))
    # gancho: la lavadora tiembla y «anda»
    walk = Vector((0, 0, 0))
    if t < T("vamos a inventarla"):
        j = 0.05 + 0.1 * seg(t, T("y por qué"), T("cocina", fin=True))
        walk = Vector((j * math.sin(t * 47), 0, abs(j * math.sin(t * 31)) * 0.7)) + Vector((0.9 * seg(t, T("y por qué"), T("cocina", fin=True)), 0, 0))
    Dc = D + off + walk
    S["sus"].location = Dc
    S["drum"].rotation_euler = (0, th, 0)
    # carcasa
    cab_on = t < T("vamos a inventarla") + 0.4 or T("por eso cuesta") <= t < T("si la ropa está")
    if t < T("vamos a inventarla") + 0.4:
        dz = 12 * seg(t, T("vamos a inventarla"), T("vamos a inventarla") + 0.4)
        S["cab"].location = walk + Vector((0, 0, dz))
    elif cab_on:
        S["cab"].location = Vector((0, 0, 10 * (1 - seg(t, T("por eso cuesta"), T("por eso cuesta") + 0.5))))
        S["cab"].location.x += 0.25 * seg(t, T("moverla") - 0.4, T("moverla") + 0.2) * (1 - seg(t, T("moverla") + 0.3, T("moverla") + 0.9))
    else: S["cab"].location = LEJOS
    # cuba (aparece con los muelles), hormigón
    tub_on = t >= T("así que cuelgas") - 0.2
    S["tub"].scale = (1, 1, 1) if tub_on else (1e-3,) * 3
    S["cutter"].scale = (6, 8, 6)
    cs = seg(t, T("tu lavadora lleva") + 0.6, T("hormigón", fin=True))
    S["conc"].location = Vector((0, 0, 9 * (1 - cs)))
    S["conc"].scale = (1, 1, 1) if cs > 0.001 else (1e-3,) * 3
    # agua y espuma
    lvl = seg(t, T("con agua"), T("detergente", fin=True)) * (1 - seg(t, T("el agua sale"), T("ellos", fin=True)))
    if t < T("con agua") - 0.1 or lvl < 0.02: S["water"].location = LEJOS
    else:
        h = 1.1 * lvl; S["water"].location = Vector((0, 0, 0)); S["wcut"].location = Vector((0, 0, -R + 0.14 + h + 5.0))
    for k, f in enumerate(S["foam"]):
        fo = seg(t, T("detergente"), T("detergente", fin=True) + 0.3) * (1 - seg(t, T("pero la ropa"), T("pero la ropa") + 0.6))
        if fo < 0.02: f.location = LEJOS
        else:
            f.location = Vector((-1.2 + 0.27 * k + 0.1 * math.sin(t * 3 + k), -1.2 + 0.25 * (k % 9), -R + 0.14 + 1.1 * lvl + 0.08 * math.sin(t * 4 + k)))
            f.scale = (fo,) * 3
    # prendas
    for i, b in enumerate(S["blobs"]):
        p = blob_world(i, t, th, Dc); b.location = p
        b.rotation_euler = (0, -th if t > T("así que haces") else 0.4 * i, 0)
        col = CLOTH[i % len(CLOTH)]
        if T("pero la ropa") <= t < T("así que haces") + 0.5: col = tuple(c * 0.65 for c in col)      # empapada
        set_color(b, col)
    # gotas: escurren (empapada) y salen disparadas (centrifugado)
    for k, d in enumerate(S["drops"]):
        a0, a1 = T("pero la ropa"), T("así que haces")
        b0, b1 = T("el agua sale") - 0.1, T("y la ropa se queda") + 1.2
        if a0 <= t < a1:
            src = blob_world(k % NB, t, th, Dc); u = ((t - a0) * 1.4 + k * 0.37) % 1.0
            d.location = src + Vector((0.1 * (k % 3 - 1), 0, -0.4 - 2.2 * u * u))
        elif b0 <= t < b1:
            u = ((t - b0) * 1.3 + k / 24) % 1.0; a = k * 2.399 - th * 0.2
            r = R + 0.1 + 5.0 * u
            d.location = Dc + Vector((r * math.cos(a), BDEP[k % NB] * 0.8, r * math.sin(a) - 1.5 * u * u))
        else: d.location = LEJOS
    # flecha de fuerza (×400)
    a0, a1 = T("a mil doscientas"), T("pero hay un")
    if a0 <= t < a1:
        ang = math.radians(-55); dirv = Vector((math.cos(ang), 0, math.sin(ang))); p = Dc + dirv * (R - 0.35) + Vector((0, -DEP / 2 + 0.3, 0))
        L = 0.2 + 1.8 * seg(t, a0 + 0.3, T("cuatrocientas", fin=True))
        base = p + dirv * 0.45; tip = base + dirv * L
        bar_set(S["farr"], base, tip); S["ftip"].location = tip
        S["ftip"].rotation_mode = 'QUATERNION'; S["ftip"].rotation_quaternion = Vector((0, 0, 1)).rotation_difference(dirv)
    else:
        bar_set(S["farr"], LEJOS, LEJOS + Vector((0, 0, 0.01))); S["ftip"].location = LEJOS
    # bastidor, muelles y amortiguadores
    f_on = t >= T("así que cuelgas") - 0.3
    fz = 10 * (1 - seg(t, T("así que cuelgas") - 0.3, T("así que cuelgas") + 0.4)) if f_on else 0
    S["frame"].location = Vector((0, 0, fz)) if f_on and not cab_on else (Vector((0, 0, 0)) if cab_on and f_on else LEJOS)
    for x, e in S["springs"]:
        if not f_on: e.location = LEJOS; continue
        top = Vector((x, 0.3, 8.2 + fz)); bot = Dc + Vector((x, 0, R + 0.35))
        sp = seg(t, T("de muelles") - 0.3, T("de muelles") + 0.3)
        if sp < 0.01: e.location = LEJOS; continue
        e.location = bot; v = top - bot
        e.rotation_mode = 'QUATERNION'; e.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(v.normalized())
        e.scale = (1, 1, v.length * sp)
    for x, sl, rod in S["dampers"]:
        dp = seg(t, T("amortiguadores") - 0.3, T("amortiguadores") + 0.4)
        if not f_on or dp < 0.01:
            bar_set(sl, LEJOS, LEJOS + Vector((0, 0, 0.01))); bar_set(rod, LEJOS, LEJOS + Vector((0, 0, 0.01))); continue
        b = Vector((x * 1.45, 0.3, 0.3)); top = Dc + Vector((x, 0, -R - 0.3))
        top = b.lerp(top, dp)
        mid = b.lerp(top, 0.55)
        bar_set(sl, b, mid); bar_set(rod, mid - (top - b).normalized() * 0.4, top)
    apply_cam(S["cam"], *cam_state(t, CAM(), drift=0.04))

def CAM():
    O = (0, -2.6, 4.3)
    return [
        (0.0, (0.4, -7.6, 4.6), O, 34), (T("gira el tambor") + 0.5, (0.2, -8.6, 4.6), O, 34),
        (T("y por qué"), (1.5, -14.0, 6.0), (0.3, 0, 4.0), 34), (T("cocina", fin=True), (2.5, -18.0, 6.5), (0.6, 0, 4.0), 34),
        (T("vamos a inventarla") + 0.3, (-3.5, -16.5, 7.5), (0, -1, 3.5), 34),
        (T("quieres lavar"), (-3.0, -15.0, 6.0), (0, -2.5, 3.0), 34),
        (T("con agua"), (-2.2, -12.5, 6.8), (0, 0, 4.0), 34),
        (T("al girar"), (-1.2, -11.0, 5.4), (0, 0, 4.2), 34),
        (T("ese golpe"), (-0.8, -10.6, 5.2), (0, 0, 4.2), 34),
        (T("así que haces"), (-1.4, -11.0, 5.6), (0, 0, 4.2), 34),
        (T("el agua sale"), (-2.6, -14.0, 6.4), (0, 0, 4.0), 34),
        (T("a mil doscientas"), (-0.8, -10.8, 5.2), (0.3, 0, 4.0), 34),
        (T("pero hay un"), (-2.0, -12.0, 5.8), (0, 0, 4.3), 34),
        (T("así que cuelgas"), (-3.8, -16.0, 7.0), (0, 0, 4.6), 34),
        (T("como un coche"), (-4.0, -17.0, 4.5), (0, 0, 3.8), 34),
        (T("tu lavadora lleva"), (-3.8, -15.5, 8.6), (0, 0, 4.8), 34),
        (T("ese peso"), (-3.5, -17.5, 7.0), (0, 0, 4.4), 34),
        (T("por eso cuesta"), (3.0, -18.0, 6.5), (0, 0, 4.2), 34),
        (T("si la ropa está"), (-3.5, -15.5, 6.9), (0, 0, 5.1), 34),
        (T("el motor gira"), (-1.8, -13.6, 6.2), (0, 0, 5.0), 34),
        (T("si no lo consigue"), (-3.0, -16.0, 6.9), (0, 0, 5.1), 34),
        (DUR + 1, (-3.6, -17.0, 7.2), (0, 0, 5.1), 34),
    ]

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    Dc = S["sus"].location
    return {"drum": Pj(Dc + Vector((0, -DEP / 2, 0))), "top": Pj(Dc + Vector((0, -DEP / 2, R))), "conc": Pj(Dc + Vector((0, 0, R + 1.3))),
            "conc2": Pj(Dc + Vector((0, -DEP / 2 - 0.8, -R - 0.2))), "spring": Pj(Vector((1.7, 0.3, 7.3))), "damp": Pj(Vector((-2.0, 0.3, 1.0))),
            "hole": Pj(Dc + Vector((R * 0.7, 0, R * 0.7))), "blob0": Pj(S["blobs"][0].location), "cab": Pj(Vector((0, -2.6, 8.6)))}

if __name__ == "__main__":
    run("lavadora", build, pose, anchors)
