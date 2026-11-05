# «Así ve la cámara de tu móvil»: la cámara del móvil disparando en primer plano; el móvil desaparece y queda el módulo en corte
# (lentes sobre el sensor); la lente se aparta y se ven los píxeles; la luz cae y cada píxel llena su columna de electrones;
# filtros rojo/verde/azul (la mitad verdes); el chip calcula los colores y aparece la foto; enfoque con muelles, bobina e
# imanes; la lente sube y baja; el estabilizador compensa el temblor.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("camara")
BG = (0.08, 0.09, 0.12); BODY = (0.17, 0.18, 0.22); BUMP = (0.24, 0.25, 0.3); GLASS = (0.1, 0.12, 0.18); RING = (0.6, 0.62, 0.66)
CHIP = (0.12, 0.13, 0.15); PIX = (0.55, 0.57, 0.6); GOLD = (0.88, 0.7, 0.3); LENS = (0.7, 0.85, 1.0); COPPER = (0.9, 0.5, 0.25)
YEL = (1.0, 0.9, 0.35); ELEC = (0.3, 0.7, 1.0); RF = (0.95, 0.25, 0.25); GF = (0.25, 0.85, 0.35); BF = (0.25, 0.45, 1.0)
LEJOS = (0, 0, -90)
NX, NY, PS = 12, 9, 0.6                     # píxeles (estilizados) y paso en mm
ZS = 1.5                                     # superficie del sensor
LZ = 3.2                                     # altura base del barril de la lente

def alpha(o, a):
    m = o.active_material; m.diffuse_color = (*m.diffuse_color[:3], a); m.surface_render_method = 'BLENDED'

def px(i, j): return ((i - (NX - 1) / 2) * PS, (j - (NY - 1) / 2) * PS)
def bayer(i, j):
    if (i + j) % 2 == 0: return GF
    return RF if j % 2 == 0 else BF
def foto(i, j):
    """color final de cada píxel: cielo, sol y campo"""
    u, v = i / (NX - 1), j / (NY - 1)
    if v < 0.34: return (0.3 + 0.15 * u, 0.7 - 0.2 * v, 0.25)
    d = math.hypot(u - 0.7, v - 0.72)
    if d < 0.17: return (1.0, 0.85, 0.3)
    return (0.95 - 0.5 * v, 0.55 + 0.1 * v, 0.35 + 0.55 * v)
def luz(i, j):
    c = foto(i, j); return (0.3 * c[0] + 0.55 * c[1] + 0.15 * c[2])

def build():
    sc, cam = scene_setup(world=BG, shadow=0.35)
    S = {"cam": cam}
    # móvil (por detrás) con el módulo de cámaras
    S["movil"] = empty((0, 0, 0)); m = S["movil"]
    rounded_slab(75, 155, 9, 8, (25.5, -62.5, -6.5), BODY, parent=m)
    rounded_slab(30, 46, 7, 1.5, (6, -12, 1.5), BUMP, parent=m)
    for y in (0, -20):
        cyl(6.5, 1.0, (0, y, 3.4), RING, parent=m); cyl(5.6, 1.1, (0, y, 3.5), GLASS, parent=m); cyl(2.6, 1.15, (0, y, 3.52), (0.18, 0.22, 0.32), parent=m)
    S["flash"] = cyl(2.2, 0.6, (14, -10, 3.1), (0.95, 0.9, 0.7), parent=m, unique=True)
    S["rayos"] = [bar_obj(YEL, 0.25, unique=True) for _ in range(6)]
    # sensor y píxeles
    box((NX * PS + 1.2, NY * PS + 1.2, 0.6), (0, 0, ZS - 0.3), CHIP)
    box((NX * PS + 3.4, NY * PS + 3.4, 0.4), (0, 0, ZS - 0.8), (0.2, 0.45, 0.3))
    for k in range(10):
        for sx in (-1, 1): box((0.3, 0.5, 0.15), (sx * (NX * PS / 2 + 1.3), -2.4 + 0.53 * k, ZS - 0.55), GOLD)
    S["pix"] = {}; S["filt"] = {}; S["pozo"] = {}
    for i in range(NX):
        for j in range(NY):
            x, y = px(i, j)
            S["pix"][(i, j)] = box((PS * 0.86, PS * 0.86, 0.06), (x, y, ZS + 0.03), PIX, unique=True)
            S["filt"][(i, j)] = box((PS * 0.86, PS * 0.86, 0.08), LEJOS, bayer(i, j), unique=True)
            S["pozo"][(i, j)] = box((PS * 0.36, PS * 0.36, 1), LEJOS, ELEC, unique=True)
    S["fotones"] = [sph(0.09, LEJOS, YEL, seg=8, unique=True) for _ in range(30)]
    S["vecinos"] = torus(PS * 1.55, 0.05, LEJOS, (1, 1, 1), unique=True)
    S["uña"] = empty(LEJOS)
    sph(5.5, (0, 0, 0), (0.93, 0.72, 0.6), parent=S["uña"], scale=(1, 1.5, 0.55))
    sph(4.6, (0, 1.5, 1.6), (0.97, 0.84, 0.8), parent=S["uña"], scale=(1, 1.2, 0.2))
    # lente: barril (translúcido), elementos, muelles, bobina, imanes
    S["lente"] = empty((0, 0, LZ))
    S["barril"] = cyl(3.3, 6.0, (0, 0, 3.0), (0.3, 0.32, 0.36), parent=S["lente"], unique=True); alpha(S["barril"], 0.35)
    for k, (r, z) in enumerate(((3.0, 0.6), (2.7, 1.9), (2.4, 3.2), (2.2, 4.4), (2.0, 5.6))):
        o = sph(r, (0, 0, z), LENS, parent=S["lente"], scale=(1, 1, 0.18), unique=True); alpha(o, 0.75)
    S["bobina"] = [torus(3.55, 0.18, (0, 0, 1.2 + 0.4 * k), COPPER, parent=S["lente"], unique=True) for k in range(4)]
    S["marco"] = empty((0, 0, 0))
    for sx, col in ((-1, RF), (1, BF)):
        box((1.2, 5.0, 3.0), (sx * 4.9, 0, LZ + 2.0), col, parent=S["marco"])
    box((11.4, 7.4, 0.5), (0, 0, LZ + 7.6), (0.3, 0.32, 0.36), parent=S["marco"])
    S["muelles"] = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            S["muelles"].append([bar_obj((0.85, 0.87, 0.9), 0.08, unique=True) for _ in range(6)])
    S["corriente"] = [sph(0.16, LEJOS, YEL, seg=8) for _ in range(12)]
    # objetos enfocados (cerca: flor; lejos: montaña), al fondo, para el cambio de enfoque
    S["cerca"] = empty(LEJOS)
    cyl(0.25, 6, (0, 0, 3), (0.3, 0.6, 0.3), parent=S["cerca"])
    for k in range(6): sph(1.2, (1.4 * math.cos(k), 0, 6 + 1.4 * math.sin(k)), (0.95, 0.4, 0.6), parent=S["cerca"], scale=(1, 0.3, 1))
    sph(0.9, (0, -0.2, 6), YEL, parent=S["cerca"], scale=(1, 0.4, 1))
    S["lejos"] = empty(LEJOS)
    bpy.ops.mesh.primitive_cone_add(radius1=14, radius2=0, depth=16, location=(0, 0, 8), vertices=5); o = bpy.context.object; setup(o, (0.45, 0.5, 0.6), parent=S["lejos"])
    bpy.ops.mesh.primitive_cone_add(radius1=4.5, radius2=0, depth=5, location=(0, -1.5, 13.5), vertices=5); o = bpy.context.object; setup(o, (0.95, 0.95, 1.0), parent=S["lejos"])
    dyn = [cam, S["movil"], S["rayos"], list(S["pix"].values()), list(S["filt"].values()), list(S["pozo"].values()), S["fotones"], S["vecinos"],
           S["uña"], S["lente"], S["marco"], S["muelles"], S["corriente"], S["cerca"], S["lejos"]]
    join_static(dyn)
    return sc, S

def pose(t, S):
    t_det, t_sen, t_pix, t_cin, t_mil = T("detrás de las"), T("el sensor"), T("está lleno"), T("muchos móviles"), T("y cada uno mide")
    t_luz, t_mas, t_cien, t_pero, t_nosabe = T("cuando entra"), T("más luz"), T("cien"), T("pero un píxel"), T("no sabe")
    t_filt, t_cur, t_mitad, t_ojos, t_chip = T("así que encima"), T("y aquí viene"), T("la mitad"), T("porque tus ojos"), T("luego")
    t_sal, t_enf, t_muel, t_bob, t_corr = T("así salen"), T("y el enfoque"), T("la lente va"), T("rodeada"), T("cuando pasa")
    t_aleja, t_acerca, t_todo, t_est = T("si se aleja"), T("si se acerca"), T("todo"), T("y el estabilizador")
    # móvil: dispara y desaparece
    mov = t < t_det + 0.3
    S["movil"].location = (0, 0, 0) if mov else LEJOS
    set_color(S["flash"], (1.0, 1.0, 0.85) if (mov and (t % 1.2) < 0.15) else (0.75, 0.7, 0.55))
    for k, r in enumerate(S["rayos"]):
        if t < t_det + 0.8:
            a = k * math.tau / 6 + t * 0.4; u = (t * 1.5 + k / 6) % 1.0
            p0 = Vector((9 * math.cos(a), 9 * math.sin(a), 60)); p1 = Vector((1.5 * math.cos(a), 1.5 * math.sin(a), ZS + 5 if not mov else 4.5))
            bar_set(r, p0.lerp(p1, max(0, u - 0.35)), p0.lerp(p1, u))
        else: bar_set(r, LEJOS, Vector(LEJOS) + Vector((0, 0, 0.1)))
    # lente: en su sitio, se aparta para ver los píxeles, vuelve para el enfoque
    sube = seg(t, t_pix - 0.3, t_pix + 0.8) * (1 - seg(t, t_enf - 0.4, t_enf + 0.6))
    enf = keyed(t, [(0, 0.0), (t_corr, 0.0), (t_corr + 1.2, 0.6), (t_aleja, 0.6), (t_aleja + 0.6, 0.9), (t_acerca, 0.9), (t_acerca + 0.5, 0.05),
                    (t_todo, 0.05), (t_todo + 0.4, 0.5), (t_todo + 0.8, 0.2), (DUR + 2, 0.3)])
    estab = t > t_est
    shake = (math.sin(t * 17) * 0.35 + math.sin(t * 11) * 0.25) * seg(t, t_est, t_est + 0.6) if estab else 0.0
    comp = -shake * seg(t, T("mueve la lente") - 0.2, T("mueve la lente") + 0.4)
    S["marco"].location = (shake, 0, 0) if t > t_enf - 0.2 else LEJOS
    S["lente"].location = (shake + comp, 0, LZ + 16 * sube + enf) if (sube < 0.97 and not mov) else LEJOS
    for b in S["bobina"]: b.hide_render = t < t_bob - 0.2
    corr = t_corr - 0.1 < t < t_todo + 1.2 or estab
    for k, c in enumerate(S["corriente"]):
        if corr and t > t_bob:
            a = -t * 5 + k * math.tau / 12; z = LZ + enf + 1.2 + 0.4 * (k % 4)
            c.location = (shake + comp + 3.55 * math.cos(a), 3.55 * math.sin(a), z)
        else: c.location = LEJOS
    for (sx, sy), ms in zip(((-1, -1), (-1, 1), (1, -1), (1, 1)), S["muelles"]):
        top = Vector((sx * 4.2 + shake, sy * 2.6, LZ + 7.35)); bot = Vector((sx * 2.9 + shake + comp, sy * 2.0, LZ + enf + 6.0))
        vis = t > t_muel - 0.2
        for k, b in enumerate(ms):
            if vis:
                a = top.lerp(bot, k / 6) + Vector((0.35 * (1 if k % 2 else -1) * sx, 0, 0)); c = top.lerp(bot, (k + 1) / 6) + Vector((0.35 * (-1 if k % 2 else 1) * sx, 0, 0))
                bar_set(b, a, c)
            else: bar_set(b, LEJOS, Vector(LEJOS) + Vector((0, 0, 0.1)))
    # uña al lado del sensor (comparación de tamaño)
    S["uña"].location = (NX * PS / 2 + 7.5, -1, ZS + 1.0) if t_det + 0.8 < t < t_pix + 0.3 else LEJOS
    # píxel resaltado
    hi = (7, 4)
    # fotones y pozos de electrones
    cae = t > t_luz - 0.2 and t < t_filt + 3.5
    col_foton = t > t_pero and t < t_filt + 3.5
    rng = random.Random(3)
    for k, f in enumerate(S["fotones"]):
        i, j = rng.randrange(NX), rng.randrange(NY); x, y = px(i, j)
        if cae:
            u = (t * 1.3 + k / 30) % 1.0; f.location = (x, y, ZS + 0.15 + 4.5 * (1 - u))
            c = (RF, GF, BF)[k % 3] if col_foton else YEL; set_color(f, c)
        else: f.location = LEJOS
    llen = seg(t, t_luz + 0.5, t_mas) * 0.5 + 0.5 * seg(t, t_cien - 0.3, T("mil", fin=True))
    pozos = t_luz < t < t_filt + 0.3
    filtros = seg(t, t_filt + 0.3, T("rojo", fin=True) + 1.2)
    mitad = win01(t, t_mitad, t_chip, 0.2, 0.3)
    demo = seg(t, T("calcula"), T("le faltan", fin=True))
    vec = T("mira a los") - 0.1 < t < T("calcula") + 0.3
    S["vecinos"].location = (*px(*hi), ZS + 0.2) if vec else LEJOS
    for (i, j), p in S["pix"].items():
        x, y = px(i, j); w = S["pozo"][(i, j)]; fl = S["filt"][(i, j)]
        if pozos:
            h = 0.05 + 1.6 * llen * luz(i, j) * (1.6 if (i, j) == hi else 1.0)
            w.location = (x, y, ZS + 0.06 + h / 2); w.scale = (PS * 0.36, PS * 0.36, h)
            set_color(w, (1.0, 0.9, 0.3) if (i, j) == hi else ELEC)
        else: w.location = LEJOS
        on = filtros > (i + j * NX) / (NX * NY)
        if on and t < DUR + 1:
            fl.location = (x, y, ZS + 0.11)
            base = bayer(i, j)
            if mitad > 0 and base != GF: base = tuple(mix(c, 0.25, 0.75 * mitad) for c in base)
            if mitad > 0 and base == GF: base = tuple(mix(c, 1.0, 0.25 * mitad * (0.5 + 0.5 * math.sin(t * 6))) for c in GF)
            if vec and (i, j) != hi and abs(i - hi[0]) <= 1 and abs(j - hi[1]) <= 1: base = tuple(mix(c, 1.0, 0.35) for c in base)
            d = demo * (1 if (abs(i - hi[0]) + abs(j - hi[1])) / 10 < demo * 1.5 else 0)
            set_color(fl, tuple(mix(a, b, d) for a, b in zip(base, foto(i, j))))
        else: fl.location = LEJOS
        set_color(p, (0.95, 0.9, 0.5) if (t_mil - 0.1 < t < t_luz + 0.3 and (i, j) == hi) else PIX)
    # cerca / lejos
    S["cerca"].location = LEJOS; S["lejos"].location = LEJOS
    apply_cam(S["cam"], *cam_state(t, CAM(), drift=0.08))

def V(at, off, lens=40): at = Vector(at); return (tuple(at + Vector(off)), tuple(at), lens)
def CAM():
    k = []
    def add(t, v, hold=0.0):
        k.append((t,) + v)
        if hold: k.append((t + hold,) + v)
    add(0.0, V((0, -1, 3.5), (-10, -18, 14), 40))
    add(2.5, V((0, -3, 3.5), (-14, -30, 22), 40))
    add(T("y cada uno cuenta"), V((0, -3, 3.5), (-12, -24, 18), 40))
    add(T("detrás de las") + 0.8, V((2, 0, 4.5), (-8, -17, 6), 40))
    add(T("el sensor"), V((4, 0, 2.5), (-6, -16, 7), 40))
    add(T("está lleno") + 0.8, V((0, 0, ZS), (-2.5, -7.0, 6.0), 45))
    add(T("y cada uno mide"), V((1.0, 0.0, ZS), (-1.5, -4.0, 3.2), 50))
    add(T("cuando entra"), V((0.8, 0.0, ZS + 0.5), (-2.5, -6.5, 4.0), 45))
    add(T("cien"), V((1.2, 0.0, ZS + 0.6), (-1.6, -4.5, 2.8), 45))
    add(T("pero un píxel"), V((0, 0, ZS + 0.5), (-2.8, -7.0, 4.5), 45))
    add(T("así que encima") + 0.6, V((0, 0, ZS), (-2.0, -6.5, 5.5), 45))
    add(T("y aquí viene"), V((0, 0, ZS), (-1.0, -5.0, 7.0), 45))
    add(T("la mitad") + 1.0, V((0, 0, ZS), (-0.5, -4.0, 8.0), 45), 1.5)
    add(T("luego") + 0.3, V((1.2, 0.0, ZS), (-1.5, -4.0, 5.0), 45))
    add(T("calcula") + 1.0, V((0.5, 0, ZS), (-0.5, -4.5, 7.5), 45))
    add(T("así salen") + 0.8, V((0, 0, ZS), (0.0, -3.0, 9.0), 45))
    add(T("y el enfoque") + 0.5, V((0, 0, LZ + 3.5), (-7, -25, 7), 40))
    add(T("rodeada") + 0.5, V((0, 0, LZ + 2.5), (-5, -21, 5), 40), 1.0)
    add(T("cuando pasa") + 1.0, V((0, 0, LZ + 3.0), (-4, -21, 5), 40))
    add(T("si se aleja"), V((0, 0, LZ + 3.5), (-6, -21, 5), 40))
    add(T("si se acerca"), V((0, 0, LZ + 3.0), (5, -21, 4.5), 40))
    add(T("todo") + 0.5, V((0, 0, LZ + 3.0), (-5, -22, 6), 40))
    add(T("y el estabilizador") + 0.5, V((0, 0, LZ + 3.5), (-4, -23, 8), 40))
    add(DUR + 2, V((0, 0, LZ + 3.5), (4, -24, 9), 40))
    return k

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v); L = S["lente"].location
    return {"lente": Pj((0, 0, 9.5)), "sensor": Pj((0, -NY * PS / 2 - 0.6, ZS)), "pix": Pj((*px(7, 4), ZS + 0.2)), "una": Pj((NX * PS / 2 + 7.5, -1, ZS + 4)),
            "muelle": Pj((4.2 + L.x, -2.6, LZ + 7.4)), "bobina": Pj((L.x - 3.6, 0, L.z + 1.8)), "iman": Pj((-4.9, -2.5, LZ + 3.5)),
            "iman2": Pj((4.9, -2.5, LZ + 3.5)), "lente2": Pj((L.x, -3.3, L.z + 3)), "sensor2": Pj((0, -3.3, ZS))}

if __name__ == "__main__":
    run("camara", build, pose, anchors)
