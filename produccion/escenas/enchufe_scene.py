# «Si tuvieras que inventar el enchufe…»: una clavija entra en el enchufe en primer plano; luego se construye pieza a pieza
# en corte: dos agujeros con sus contactos y la corriente que va y vuelve, la clavija a medio meter con un dedo, el hueco,
# la lavadora con un cable suelto, las láminas de tierra y el cable hasta la pica enterrada, el diferencial del cuadro
# y las tapas de seguridad frente a un clip.
import bpy, bmesh, math, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("enchufe")
WALL = (0.82, 0.8, 0.76); WALLIN = (0.62, 0.58, 0.54); PLATE = (0.96, 0.96, 0.95); PLATEIN = (0.8, 0.8, 0.8)
BRASS = (0.88, 0.7, 0.3); STEEL = (0.75, 0.77, 0.8); BROWN = (0.55, 0.32, 0.16); BLUE = (0.2, 0.45, 0.9); EARTH = (0.35, 0.8, 0.3)
YEL = (1.0, 0.85, 0.2); HOT = (1.0, 0.35, 0.2); SKIN = (0.93, 0.72, 0.6); FLOOR = (0.62, 0.48, 0.34); SOIL = (0.4, 0.3, 0.22)
SOIL2 = (0.33, 0.25, 0.18); COPPER = (0.85, 0.5, 0.3); WASH = (0.94, 0.95, 0.97); DARK = (0.1, 0.11, 0.14); PLUGC = (0.18, 0.19, 0.22)
ZS = 0.35                                  # altura del centro del enchufe
HX = 0.019                                 # medio paso entre agujeros (19 mm entre ejes)
RREC = 0.02                                # radio del hueco
LEJOS = (0, 0, -40)

def tubo(r_out, r_in, color, n=40, unique=False):
    """cilindro hueco a lo largo de +Y, de y=0 a y=1 (se escala en Y)"""
    me = bpy.data.meshes.new("tubo"); bm = bmesh.new(); vs = []
    for y in (0.0, 1.0):
        fila = []
        for k in range(n):
            a = math.tau * k / n; c, s_ = math.cos(a), math.sin(a)
            fila.append((bm.verts.new((r_out * c, y, r_out * s_)), bm.verts.new((r_in * c, y, r_in * s_))))
        vs.append(fila)
    for k in range(n):
        j = (k + 1) % n; o0, i0 = vs[0][k]; o1, i1 = vs[0][j]; O0, I0 = vs[1][k]; O1, I1 = vs[1][j]
        bm.faces.new((o0, O0, O1, o1)); bm.faces.new((i0, i1, I1, I0)); bm.faces.new((o0, o1, i1, i0)); bm.faces.new((O0, I0, I1, O1))
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("tubo", me); bpy.context.collection.objects.link(ob)
    for p in ob.data.polygons: p.use_smooth = True
    return setup(ob, color, unique=unique)

def boolean(o, cutter, nombre="b"):
    m = o.modifiers.new(nombre, "BOOLEAN"); m.operation = "DIFFERENCE"; m.object = cutter; m.solver = "EXACT"; return m

def poly_bars(pts, color, r, unique=True):
    bs = []
    for a, b in zip(pts, pts[1:]):
        o = bar_obj(color, r, unique=unique); bar_set(o, a, b); bs.append(o)
    return bs

def along(pts, s):
    """punto a fracción s (0..1) de una polilínea"""
    L = [(Vector(b) - Vector(a)).length for a, b in zip(pts, pts[1:])]; tot = sum(L); d = max(0.0, min(1.0, s)) * tot
    for (a, b), l in zip(zip(pts, pts[1:]), L):
        if d <= l: return Vector(a).lerp(Vector(b), d / max(l, 1e-6))
        d -= l
    return Vector(pts[-1])

# caminos de la corriente
FASE = [(-HX, 0.035, ZS + 0.3), (-HX, 0.035, ZS), (-HX, 0.016, ZS)]
NEUT = [(HX, 0.016, ZS), (HX, 0.035, ZS), (HX, 0.035, ZS + 0.3)]
TIERRA = [(0, 0.0, ZS - RREC), (0, 0.05, ZS - RREC), (0.06, 0.05, ZS - RREC), (0.06, 0.05, 0.0), (0.06, -0.006, 0.0), (0.06, -0.006, -0.45),
          (1.25, -0.006, -0.45), (1.25, -0.006, -0.55)]
PICA_X = 1.25
WX0, WX1, WY0, WY1, WZ1 = 0.45, 1.05, -0.66, -0.06, 0.86    # lavadora
FUGA = [(0.75, WY0 + 0.15, 0.55), (WX0 + 0.01, -0.3, 0.45), (WX0 + 0.01, -0.12, 0.2), (0.3, -0.1, 0.06), (0.1, -0.09, ZS - 0.04),
        (0.0, -0.05, ZS - RREC)] + TIERRA[1:] + [(PICA_X, -0.006, -2.3)]
CUADRO = (-0.75, 0.0, 1.45)                              # centro del cuadro en la pared
DIF_X = CUADRO[0] - 0.05
DSALE = [(DIF_X - 0.012, -0.03, CUADRO[2] - 0.06), (DIF_X - 0.012, -0.03, CUADRO[2] - 0.32), (DIF_X - 0.012, 0.03, CUADRO[2] - 0.32)]
DVUELVE = [(DIF_X + 0.012, 0.03, CUADRO[2] - 0.32), (DIF_X + 0.012, -0.03, CUADRO[2] - 0.32), (DIF_X + 0.012, -0.03, CUADRO[2] - 0.06)]

def build():
    sc, cam = scene_setup(world=(0.08, 0.09, 0.12), shadow=0.32)
    S = {"cam": cam}
    # cortador común: muesca sobre la mitad de arriba del enchufe y ranura hasta el suelo (por donde baja la tierra)
    c1 = box((0.13, 0.2, 0.09), (0, -0.02, ZS + 0.045), None); c2 = box((0.03, 0.2, ZS + 0.02), (0.06, -0.02, ZS / 2 - 0.005), None)
    cut = c1
    for c in (c1, c2): c.hide_render = True; c.hide_viewport = True
    S["cut"] = cut; S["cut0"] = cut.location.copy(); S["cut2"] = c2; S["cut20"] = c2.location.copy()
    # habitación en corte y terreno
    box((5, 1.25, 0.15), (0.5, -0.625, -0.075), FLOOR)
    box((5, 1.0, 3.0), (0.5, 0.5, -1.5 - 0.15), SOIL)                 # terreno detrás (cara de corte en y=0)
    box((1.7, 1.25, 3.0), (-1.15, -0.625, -1.65), SOIL2); box((1.6, 1.25, 3.0), (2.2, -0.625, -1.65), SOIL2)
    for k in range(14):
        sph(0.03 + 0.02 * (k % 3), (-0.2 + 0.13 * k, -0.01, -0.4 - 0.15 * ((k * 7) % 11)), (0.5, 0.4, 0.3), scale=(1.4, 0.3, 1))
    S["pared"] = box((5, 0.12, 2.6), (0.5, 0.06, 1.3), WALL, unique=True); boolean(S["pared"], cut); boolean(S["pared"], c2, "ranura")
    box((5, 0.02, 0.08), (0.5, -0.01, 0.04), (0.95, 0.95, 0.95))       # rodapié
    # pica de tierra
    S["pica"] = cyl(0.014, 1.9, (PICA_X, -0.006, -0.55 - 0.95), COPPER, unique=True)
    # ---- enchufe ----
    hole = cyl(RREC + 0.0005, 0.08, (0, -0.02, ZS), None, rot=(math.pi / 2, 0, 0)); hole.hide_render = hole.hide_viewport = True
    S["hole"] = hole
    pl = rounded_slab(0.082, 0.082, 0.012, 0.025, (0, 0, ZS), PLATE, unique=True); pl.rotation_euler = (math.pi / 2, 0, 0)
    boolean(pl, hole, "hueco"); boolean(pl, cut, "corte"); S["placa"] = pl
    S["tubo"] = tubo(RREC + 0.0015, RREC, PLATEIN, unique=True); S["tubo"].location = (0, -0.025, ZS); boolean(S["tubo"], cut)
    S["disco"] = cyl(RREC + 0.0004, 0.003, (0, 0, ZS), PLATEIN, rot=(math.pi / 2, 0, 0), unique=True)
    S["agujeros"] = []
    for sx in (-1, 1):
        h = cyl(0.0027, 0.02, (sx * HX, 0, ZS), None, rot=(math.pi / 2, 0, 0)); h.hide_render = h.hide_viewport = True; S["agujeros"].append(h)
        boolean(S["disco"], h, "a%d" % sx)
    boolean(S["disco"], cut, "corte")
    S["contactos"] = [cyl(0.0045, 0.02, LEJOS, BRASS, rot=(math.pi / 2, 0, 0), unique=True) for _ in (0, 1)]
    S["hilos"] = [poly_bars(FASE, BROWN, 0.0028), poly_bars(NEUT, BLUE, 0.0028)]
    S["tapas"] = [box((0.011, 0.0015, 0.012), LEJOS, (0.9, 0.55, 0.2), unique=True) for _ in (0, 1)]
    S["laminas"] = []
    for sz in (1, -1):
        o = box((0.006, 0.012, 0.0016), (0, -0.016, ZS + sz * (RREC - 0.0008)), STEEL, unique=True); boolean(o, cut); S["laminas"].append(o)
    S["hilo_tierra"] = poly_bars(TIERRA[:-1], EARTH, 0.0045)
    # ---- clavija ----
    S["clav"] = empty(LEJOS)
    cyl(0.0185, 0.022, (0, -0.011, 0), PLUGC, parent=S["clav"], rot=(math.pi / 2, 0, 0))
    cyl(0.021, 0.03, (0, -0.037, 0), PLUGC, parent=S["clav"], rot=(math.pi / 2, 0, 0))
    cyl(0.012, 0.03, (0, -0.066, 0), PLUGC, parent=S["clav"], rot=(math.pi / 2, 0, 0))
    S["patas"] = [cyl(0.0024, 0.019, (sx * HX, 0.0095, 0), STEEL, parent=S["clav"], rot=(math.pi / 2, 0, 0), unique=True) for sx in (-1, 1)]
    S["tiras"] = [box((0.005, 0.014, 0.0012), (0, -0.009, sz * 0.0186), STEEL, parent=S["clav"], unique=True) for sz in (1, -1)]
    S["cable"] = [bar_obj(PLUGC, 0.0045) for _ in range(5)]
    # ---- dedo (clavija a medio meter) ----
    S["dedo"] = empty(LEJOS)
    cyl(0.0085, 0.06, (0, -0.03, 0), SKIN, parent=S["dedo"], rot=(math.pi / 2, 0, 0)); sph(0.0085, (0, 0, 0), SKIN, parent=S["dedo"])
    sph(0.006, (0, -0.004, 0.006), (0.97, 0.82, 0.78), parent=S["dedo"], scale=(1, 1.3, 0.3))
    sph(0.04, (0.01, -0.09, -0.02), SKIN, parent=S["dedo"], scale=(1, 0.8, 0.9))
    # ---- clip ----
    S["clip"] = empty(LEJOS)
    for a, b in (((0, 0, 0), (0, -0.04, 0)), ((0, -0.04, 0), (0, -0.04, 0.006)), ((0, -0.04, 0.006), (0, -0.008, 0.006)),
                 ((0, -0.008, 0.006), (0, -0.008, 0.0115)), ((0, -0.008, 0.0115), (0, -0.05, 0.0115))):
        o = bar_obj(STEEL, 0.0007); o.parent = S["clip"]; bar_set(o, a, b)
    # ---- lavadora (sin el lateral izquierdo, para ver dentro) ----
    S["carcasa"] = []
    for sz, loc in (((WX1 - WX0, 0.012, WZ1 - 0.02), ((WX0 + WX1) / 2, WY0 + 0.006, (WZ1 + 0.02) / 2)),
                    ((WX1 - WX0, WY1 - WY0, 0.012), ((WX0 + WX1) / 2, (WY0 + WY1) / 2, WZ1)),
                    ((0.012, WY1 - WY0, WZ1 - 0.02), (WX1 - 0.006, (WY0 + WY1) / 2, (WZ1 + 0.02) / 2)),
                    ((WX1 - WX0, 0.012, WZ1 - 0.02), ((WX0 + WX1) / 2, WY1 - 0.006, (WZ1 + 0.02) / 2))):
        S["carcasa"].append(box(sz, loc, WASH, unique=True))
    box((0.012, WY1 - WY0, 0.03), (WX0 + 0.006, (WY0 + WY1) / 2, 0.035), (0.8, 0.8, 0.82))
    torus(0.17, 0.025, (0.75, WY0 - 0.008, 0.45), (0.7, 0.72, 0.76), rot=(math.pi / 2, 0, 0))
    cyl(0.16, 0.01, (0.75, WY0 - 0.004, 0.45), (0.25, 0.32, 0.4), rot=(math.pi / 2, 0, 0))
    box((0.5, 0.01, 0.1), (0.75, WY0 - 0.005, 0.79), (0.85, 0.86, 0.88)); cyl(0.025, 0.012, (0.95, WY0 - 0.01, 0.79), (0.6, 0.62, 0.66), rot=(math.pi / 2, 0, 0))
    cyl(0.22, 0.42, (0.75, (WY0 + WY1) / 2, 0.45), (0.7, 0.72, 0.75), rot=(math.pi / 2, 0, 0))   # tambor
    cyl(0.06, 0.16, (0.62, -0.25, 0.13), (0.4, 0.42, 0.45), rot=(0, math.pi / 2, 0))             # motor
    box((0.05, 0.03, 0.04), (0.55, -0.2, 0.75), (0.25, 0.25, 0.28))                               # regleta
    S["suelto"] = [bar_obj(BROWN, 0.004) for _ in range(3)]
    S["chispas"] = [sph(0.006, LEJOS, YEL, seg=8) for _ in range(8)]
    # ---- mano ----
    S["mano"] = empty(LEJOS)
    sph(0.045, (0, 0, 0), SKIN, parent=S["mano"], scale=(1, 0.35, 1.1))
    for k in range(4): cyl(0.0085, 0.065, (-0.03 + 0.02 * k, 0, 0.075 - 0.006 * abs(k - 1.5)), SKIN, parent=S["mano"])
    cyl(0.009, 0.05, (0.05, -0.004, 0.0), SKIN, parent=S["mano"], rot=(0, -0.9, 0))
    cyl(0.03, 0.2, (0, -0.02, -0.12), SKIN, parent=S["mano"], rot=(0.3, 0, 0))
    S["mano_luz"] = sph(0.05, (0, 0.01, 0), YEL, parent=S["mano"], scale=(1.15, 0.2, 1.2), unique=True)
    # ---- cuadro eléctrico ----
    cx, _, cz = CUADRO
    box((0.36, 0.05, 0.28), (cx, -0.025, cz), (0.9, 0.9, 0.92)); box((0.33, 0.004, 0.25), (cx, -0.051, cz), (0.82, 0.83, 0.86))
    box((0.32, 0.01, 0.03), (cx, -0.057, cz), (0.6, 0.62, 0.65))
    for k, w in enumerate((0.036, 0.018, 0.018, 0.018)):
        x = cx + 0.06 + 0.024 * k if k else cx - 0.12
        box((w, 0.03, 0.09), (x, -0.07, cz), (0.96, 0.96, 0.96)); box((0.008, 0.02, 0.016), (x, -0.09, cz + 0.008), DARK)
    box((0.07, 0.03, 0.09), (DIF_X, -0.07, cz), (0.96, 0.96, 0.96))
    S["palanca"] = box((0.012, 0.022, 0.02), (DIF_X - 0.015, -0.092, cz + 0.012), BLUE, unique=True)
    box((0.012, 0.004, 0.012), (DIF_X + 0.02, -0.087, cz + 0.02), YEL)
    S["dif_luz"] = box((0.05, 0.004, 0.008), (DIF_X, -0.0865, cz - 0.03), (0.3, 0.3, 0.32), unique=True)
    S["dhilos"] = [poly_bars(DSALE, BROWN, 0.004), poly_bars(DVUELVE, BLUE, 0.004)]
    # ---- partículas de corriente ----
    S["pf"] = [sph(0.0032, LEJOS, YEL, seg=10) for _ in range(9)]
    S["pn"] = [sph(0.0032, LEJOS, YEL, seg=10) for _ in range(9)]
    S["pt"] = [sph(0.02, LEJOS, YEL, seg=10) for _ in range(30)]
    S["pd"] = [sph(0.006, LEJOS, YEL, seg=10) for _ in range(16)]
    S["pfuga"] = [sph(0.006, LEJOS, HOT, seg=10) for _ in range(5)]
    dyn = [cam, cut, c2, hole, S["pared"], S["pica"], S["placa"], S["tubo"], S["disco"], S["agujeros"], S["contactos"], S["hilos"], S["tapas"],
           S["laminas"], S["hilo_tierra"], S["clav"], S["cable"], S["dedo"], S["clip"], S["carcasa"], S["suelto"], S["chispas"], S["mano"],
           S["palanca"], S["dif_luz"], S["dhilos"], S["pf"], S["pn"], S["pt"], S["pd"], S["pfuga"]]
    join_static(dyn)
    return sc, S

# ---------------- tiempos ----------------
def clavija_y(t):
    """posición de la cara frontal de la clavija (y); None = fuera"""
    t_med, t_hueco, t_cl = T("pero si alguien"), T("hundes"), T("la clavija")
    t_tercer, t_tierra, t_tapas, t_nino = T("añades un tercer"), T("es la toma"), T("muchos enchufes"), T("así un niño")
    return keyed(t, [(0, -0.07), (0.9, -0.0095), (2.0, -0.0095), (2.6, -0.04), (3.2, -0.0095), (T("lo primero"), -0.0095),
                     (T("lo primero") + 0.5, -0.2), (t_med - 0.3, -0.2), (t_med + 0.6, -0.038), (t_hueco - 0.2, -0.038), (t_hueco + 0.3, -0.2),
                     (t_cl, -0.12), (t_cl + 1.4, -0.03), (t_cl + 2.2, -0.0095), (t_tercer - 0.2, -0.0095), (t_tercer + 0.5, -0.15),
                     (t_tierra - 0.6, -0.15), (t_tierra + 0.6, -0.0095), (t_tapas - 0.3, -0.0095), (t_tapas + 0.4, -0.12),
                     (T("solo se abren"), -0.12), (T("si entran") + 0.6, -0.0095), (t_nino - 0.4, -0.0095), (t_nino + 0.2, -0.2), (DUR + 2, -0.2)])

def profundidad(t):
    """fondo del hueco (0 = plano, 1 = hundido)"""
    if t < T("lo primero"): return 1.0
    return seg(t, T("hundes") + 0.2, T("en un hueco", fin=True) + 0.3)

def corte_on(t): return T("lo primero") + 0.3 < t

def pose(t, S):
    t1, t_ag, t_llega = T("lo primero"), T("dos agujeros"), T("por uno llega")
    t_sent, t_dedos, t_metal, t_hueco = T("y cambia de"), T("pero si alguien"), T("podría tocar"), T("hundes")
    t_lav, t_toca, t_tu, t_tercer, t_lam = T("y si un cable"), T("y toca"), T("la que tocarías"), T("añades un tercer"), T("esas dos láminas")
    t_tierra, t_une, t_fuga, t_aun = T("es la toma"), T("une la carcasa"), T("si hay una fuga"), T("pero aún falta")
    t_cuad, t_mide, t_falt, t_corta, t_det = T("en tu cuadro"), T("mide sin parar"), T("si faltan"), T("y corta"), T("y un detalle")
    t_tapas, t_nino, t_clip = T("muchos enchufes"), T("así un niño"), T("meter un clip")
    # cortador fuera mientras se ve el enchufe entero
    S["cut"].location = S["cut0"] + Vector((0, 0, 0 if corte_on(t) else 9))
    S["cut2"].location = S["cut20"] + Vector((0, 0, 0 if corte_on(t) else 9))
    # fondo del hueco y agujeros
    d = profundidad(t); yf = mix(-0.025, -0.008, d)       # cara delantera del fondo
    S["disco"].location = (0, yf + 0.0015, ZS)
    S["tubo"].location = (0, -0.025, ZS); S["tubo"].scale = (1, max(0.0005, yf + 0.025), 1)
    S["hole"].scale = (1, 1, 1)
    ag = 1.0 if t < t1 else seg(t, t_ag, t_ag + 0.4)
    for h, sx in zip(S["agujeros"], (-1, 1)):
        h.scale = (max(0.001, ag), max(0.001, ag), 1); h.location = (sx * HX, yf, ZS)
    # contactos detrás del fondo
    yb = yf + 0.003
    con = 1.0 if t < t1 else seg(t, t_ag + 0.2, t_ag + 0.6)
    for c, sx in zip(S["contactos"], (-1, 1)):
        c.location = (sx * HX, yb + 0.0025 + 0.01, ZS) if con > 0.01 else LEJOS; c.scale = (con, con, 1)
    # tapas de seguridad
    tap_vis = t < t1 or t > t_tapas - 0.4
    abrir = 0.0
    if t < t1: abrir = seg(t, 0.55, 0.85) * (1 - seg(t, 2.25, 2.55)) + seg(t, 2.8, 3.05)
    else: abrir = seg(t, T("si entran") + 0.1, T("si entran") + 0.5) * (1 - seg(t, t_nino - 0.4, t_nino))
    for p, sx in zip(S["tapas"], (-1, 1)):
        p.location = (sx * (HX + 0.0095 * abrir), yb + 0.001, ZS) if tap_vis else LEJOS
    lam = 1.0 if (t < t1 or t > t_lam - 0.2) else 0.0
    for l in S["laminas"]: l.hide_render = lam < 0.5
    lam_col = EARTH if t_lam < t < t_une + 1 else STEEL
    for l in S["laminas"]: set_color(l, lam_col)
    tierra_vis = t > t_tierra - 0.2
    for b in S["hilo_tierra"]: b.hide_render = not tierra_vis
    # clavija y cable
    cy = clavija_y(t)
    S["clav"].location = (0, cy, ZS)
    caliente = t_dedos < t < t_hueco
    for p in S["patas"]: set_color(p, HOT if (caliente and t > t_metal - 0.3) else STEEL)
    for p in S["tiras"]: set_color(p, EARTH if t > t_lam else STEEL)
    pts = [Vector((0, cy - 0.08, ZS)), Vector((0.02, cy - 0.14, ZS - 0.06)), Vector((0.12, -0.2, 0.12)), Vector((0.3, -0.2, 0.03)),
           Vector((0.42, -0.22, 0.12)), Vector((WX0 + 0.02, -0.2, 0.2))]
    for b, a, c in zip(S["cable"], pts, pts[1:]): bar_set(b, a, c)
    # dedo que toca la pata a medio meter
    u = seg(t, t_dedos + 0.4, t_metal + 0.2) * (1 - seg(t, t_hueco - 0.6, t_hueco))
    tip = Vector((HX + 0.009, -0.031, ZS - 0.004))
    S["dedo"].location = tip.lerp(Vector((0.09, -0.16, ZS - 0.08)), 1 - u) if u > 0.001 else LEJOS
    S["dedo"].rotation_euler = (0, 0, 0.9)
    # clip contra una sola tapa
    uc = seg(t, t_nino + 0.2, t_clip + 0.3)
    S["clip"].location = Vector((HX, yf - 0.0005, ZS - 0.003)).lerp(Vector((HX + 0.02, -0.12, ZS - 0.02)), 1 - uc) if uc > 0.001 else LEJOS
    if uc > 0.95: S["clip"].location.y += 0.0012 * abs(math.sin(t * 18))
    # corriente fase / neutro en el enchufe
    cor = win01(t, t_llega - 0.2, t_dedos + 0.2) + win01(t, T("la clavija") + 2.0, t_lav - 0.3)
    alterna = t > t_sent - 0.1
    for k, (a, b) in enumerate(zip(S["pf"], S["pn"])):
        if cor > 0.05:
            if alterna: ph = 0.18 * math.sin(t * 7.0)
            else: ph = (t - t_llega) * 0.5
            s = (k / len(S["pf"]) + ph) % 1.0
            a.location = along(FASE, s); b.location = along(NEUT, s)
            a.scale = b.scale = (cor,) * 3
        else: a.location = b.location = LEJOS
    # lavadora: cable suelto que toca la carcasa
    us = seg(t, t_lav + 0.6, t_toca + 0.3)
    p0 = Vector((0.55, -0.2, 0.73)); p_reg = Vector((0.55, -0.19, 0.75)); p_car = Vector((0.75, WY0 + 0.016, 0.62))
    tipw = p_reg.lerp(p_car, us) + Vector((0, 0, -0.05 * math.sin(math.pi * us)))
    mid = p0.lerp(tipw, 0.5) + Vector((0.0, 0.02, -0.06))
    w0 = Vector((0.62, -0.25, 0.2))
    bar_set(S["suelto"][0], w0, Vector((0.6, -0.22, 0.5))); bar_set(S["suelto"][1], Vector((0.6, -0.22, 0.5)), mid); bar_set(S["suelto"][2], mid, tipw)
    viva = us > 0.98 and t < t_corta + 0.2
    for k, c in enumerate(S["chispas"]):
        if viva and (t_toca + 0.3 < t < t_toca + 1.6 or t_fuga < t < t_fuga + 1.2):
            a = t * 23 + k * 2.4; c.location = p_car + Vector((0.025 * math.cos(a), -0.01, 0.025 * math.sin(a * 1.3)))
        else: c.location = LEJOS
    rojo = viva and t < t_tierra - 0.3
    for p in S["carcasa"]: set_color(p, mix_col(WASH, (1.0, 0.45, 0.4), 0.25 + 0.25 * math.sin(t * 9)) if rojo else WASH)
    # mano que se acerca a la carcasa
    um = seg(t, t_tu - 0.2, t_tu + 0.8) * (1 - seg(t, t_tercer - 0.3, t_tercer + 0.2)) + seg(t, t_fuga - 0.4, t_fuga + 0.3) * (1 - seg(t, t_aun, t_aun + 0.5))
    hand_on = Vector((0.88, WY0 - 0.03, 0.62)); hand_off = Vector((0.95, WY0 - 0.45, 0.45))
    S["mano"].location = hand_off.lerp(hand_on, um) if um > 0.001 else LEJOS
    S["mano"].rotation_euler = (0, 0, 0)
    set_color(S["mano_luz"], HOT if (t < t_tercer and um > 0.9) else SKIN)
    S["mano_luz"].hide_render = not (t < t_tercer and um > 0.9)
    # fuga por la tierra hasta la pica
    pt_on = win01(t, t_fuga - 0.1, t_aun + 0.3) + 0.8 * win01(t, t_une + 0.4, t_fuga, 0.5, 0.2)
    for k, p in enumerate(S["pt"]):
        if pt_on > 0.05:
            s = (k / len(S["pt"]) + (t - t_une) * 0.22) % 1.0
            p.location = along(FUGA, s); p.scale = (pt_on,) * 3
        else: p.location = LEJOS
    set_color(S["pica"], YEL if t_une + 1.4 < t < t_aun else COPPER)
    # diferencial: sale y vuelve; al faltar 30 mA salta
    disp = t > T("tienen que", fin=True) and t < t_corta
    fuga_d = seg(t, t_falt, t_falt + 0.8) * (1 - seg(t, t_corta, t_corta + 0.1))
    on = t < t_corta + 0.05 or t > t_det + 0.5
    for k, (a, b) in enumerate(zip(S["pd"][:8], S["pd"][8:])):
        if t_cuad < t < t_det and on:
            s = (k / 8 + (t - t_cuad) * 0.6) % 1.0
            a.location = along(DSALE, s); b.location = along(DVUELVE, s)
            b.hide_render = fuga_d > 0.5 and k % 4 == 0
        else: a.location = b.location = LEJOS
    for k, p in enumerate(S["pfuga"]):
        if fuga_d > 0.3 and t_cuad < t < t_det and on:
            s = (k / 5 + t * 0.8) % 1.0; p.location = Vector(DSALE[1]).lerp(Vector(DSALE[1]) + Vector((-0.12, -0.05, -0.05)), s)
        else: p.location = LEJOS
    lev = seg(t, t_corta, t_corta + 0.12)
    S["palanca"].location = (DIF_X - 0.015, -0.092, CUADRO[2] + mix(0.012, -0.012, lev))
    set_color(S["dif_luz"], (0.3, 0.9, 0.4) if lev < 0.5 else (0.95, 0.25, 0.25))
    apply_cam(S["cam"], *cam_state(t, CAM(), drift=0.002))

def mix_col(a, b, u): return tuple(mix(x, y, u) for x, y in zip(a, b))

def V(at, off, lens=38): at = Vector(at); return (tuple(at + Vector(off)), tuple(at), lens)
def CAM():
    E = (0, -0.01, ZS); C = (0, 0.0, ZS)
    lav = (0.68, -0.3, 0.5)
    k = []
    def add(t, v, hold=0.0):
        k.append((t,) + v)
        if hold: k.append((t + hold,) + v)
    add(0.0, V((0.0, -0.02, ZS - 0.005), (-0.07, -0.19, 0.035), 40))
    add(2.4, V((0.0, -0.02, ZS - 0.005), (0.06, -0.19, 0.05), 40))
    add(T("lo primero") + 0.3, V(E, (0.02, -0.17, 0.1), 40))
    add(T("dos agujeros") + 0.3, V(C, (-0.03, -0.12, 0.13), 40), 1.0)
    add(T("cambia de"), V((0, 0.01, ZS + 0.04), (-0.07, -0.17, 0.12), 38))
    add(T("pero si alguien") + 0.3, V((0.01, -0.025, ZS), (-0.09, -0.15, 0.08), 40), 1.5)
    add(T("hundes") + 0.3, V((0.0, -0.015, ZS), (-0.07, -0.14, 0.1), 40), 1.0)
    add(T("la clavija") + 1.2, V((0.0, -0.025, ZS), (-0.1, -0.15, 0.09), 38), 0.8)
    add(T("y si un cable") + 0.5, V((0.5, -0.25, 0.45), (-0.95, -1.2, 0.45), 30))
    add(T("lavadora") + 0.3, V(lav, (-0.6, -0.5, 0.3), 32), 1.6)
    add(T("la que tocarías"), V((0.8, -0.66, 0.58), (-0.4, -0.95, 0.12), 30), 0.5)
    add(T("añades un tercer") + 0.2, V((0, -0.01, ZS), (-0.05, -0.17, 0.1), 40), 1.2)
    add(T("es la toma") + 0.2, V((0, -0.02, ZS - 0.005), (-0.08, -0.16, 0.11), 40), 0.6)
    add(T("une la carcasa") + 0.6, V((0.55, 0, -0.45), (-0.2, -3.2, 0.45), 26), 2.0)
    add(T("pero aún falta"), V((0.55, 0, -0.4), (-0.1, -3.3, 0.5), 26))
    add(T("en tu cuadro") + 0.3, V((CUADRO[0], -0.05, CUADRO[2] - 0.05), (0.05, -0.6, 0.06), 34))
    add(T("mide sin parar"), V((DIF_X, -0.05, CUADRO[2] + 0.02), (0.03, -0.55, 0.05), 34), 2.0)
    add(T("y corta"), V((DIF_X, -0.05, CUADRO[2] + 0.03), (-0.02, -0.5, 0.05), 34))
    add(T("y un detalle") - 0.2, V((DIF_X, -0.05, CUADRO[2] + 0.03), (0.03, -0.52, 0.05), 34))
    add(T("y un detalle") + 0.5, V((-0.2, -0.05, 0.75), (0.0, -1.3, 0.1), 30))
    add(T("muchos enchufes") + 0.2, V((0.0, -0.005, ZS), (-0.04, -0.12, 0.12), 40), 1.0)
    add(T("así un niño"), V((0.01, -0.005, ZS), (0.04, -0.12, 0.12), 40))
    add(T("sígueme"), V((0.01, -0.01, ZS), (0.05, -0.14, 0.13), 38))
    add(DUR + 2, V((0.01, -0.01, ZS), (0.07, -0.17, 0.15), 38))
    return k

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    yf = mix(-0.025, -0.008, profundidad(t))
    return {"fase": Pj((-HX, 0.035, ZS + 0.04)), "neutro": Pj((HX, 0.035, ZS + 0.04)), "contacto": Pj((-HX, yf + 0.01, ZS + 0.005)),
            "hueco": Pj((0, -0.02, ZS - RREC)), "pata": Pj((HX, -0.03, ZS + 0.003)), "carcasa": Pj((0.75, WY0, 0.7)),
            "lamina": Pj((0, -0.016, ZS - RREC)), "pica": Pj((PICA_X, 0, -1.4)), "dif": Pj((DIF_X, -0.09, CUADRO[2] + 0.05)),
            "sale": Pj(DSALE[1]), "vuelve": Pj(DVUELVE[1]), "tapa": Pj((HX, yf, ZS + 0.008)), "clip": Pj((HX + 0.01, -0.03, ZS))}

if __name__ == "__main__":
    run("enchufe", build, pose, anchors)
