# «Así funciona el GPS»: tu móvil con el mapa y el punto azul recibe señales que caen del cielo (no envía nada);
# la Tierra con 31 satélites en 6 órbitas a 20.000 km; un satélite con su reloj atómico emite la hora; la señal baja hasta
# ti; con el retraso sale la distancia: una esfera, dos esferas (un círculo), tres (dos puntos, uno en el espacio);
# el reloj del móvil no es atómico: cuarto satélite; un error de una millonésima = 300 m en el mapa; los relojes de arriba
# se adelantan 38 millonésimas al día (relatividad); el punto se desvía 10 km; se ajustan antes de lanzarlos.
# Tres decorados: P (móvil, en el origen), E (espacio, en EO) y D (dos relojes, en DO). Se cambia de uno a otro por corte.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector, Matrix

T, DUR = cargar("gps")
BG = (0.05, 0.06, 0.1); BODY = (0.16, 0.17, 0.21); MAPC = (0.9, 0.88, 0.82); STREET = (1.0, 1.0, 1.0); PARK = (0.62, 0.82, 0.55)
WATER = (0.55, 0.75, 0.95); BLUE = (0.18, 0.5, 1.0); HALO = (0.62, 0.78, 1.0); YEL = (1.0, 0.82, 0.25); RED = (0.95, 0.3, 0.3)
EARTH = (0.2, 0.42, 0.85); LAND = (0.36, 0.7, 0.38); GOLD = (0.95, 0.72, 0.25); PANEL = (0.2, 0.32, 0.7); WHITE = (0.96, 0.96, 0.98)
INK = (0.08, 0.09, 0.12); ORB = (0.32, 0.38, 0.55); CYAN = (0.3, 0.9, 1.0); MAG = (1.0, 0.4, 0.85); GRN = (0.35, 0.95, 0.5)
LEJOS = Vector((0, 0, -3000))
FONT = os.path.expanduser("~/.fonts/Poppins-Bold.ttf")
EO = Vector((1000, 0, 0)); DO = Vector((-1000, 0, 0))
RE = 4.0; RS = 9.0
def nv(*a): return Vector(a).normalized()
PIN = EO + nv(0.12, -1, 0.28) * RE
SATS = [EO + nv(-0.75, -0.6, 0.45) * RS, EO + nv(0.75, -0.55, 0.5) * RS, EO + nv(-0.05, -0.45, 1.0) * RS, EO + nv(0.55, -0.75, -0.55) * RS]
SCOL = [YEL, CYAN, MAG, GRN]

def mirror_point():
    S1, S2, S3 = SATS[:3]; n = (S2 - S1).cross(S3 - S1).normalized()
    return PIN - 2 * (PIN - S1).dot(n) * n
PSPACE = mirror_point()

def font(o):
    if os.path.exists(FONT):
        try: o.data.font = bpy.data.fonts.load(FONT, check_existing=True)
        except Exception: pass

def put(o, p, s=1.0):
    o.location = p; o.scale = (s, s, s) if isinstance(s, (int, float)) else s
def hide(o): o.location = LEJOS

# ---------------- construcción ----------------
def satellite(parent_loc, scale=1.0, clock=False):
    e = empty(parent_loc)
    box((0.7, 0.7, 0.8), (0, 0, 0), GOLD, parent=e)
    for sx in (-1, 1):
        box((0.08, 0.08, 0.08), (sx * 0.42, 0, 0), (0.6, 0.6, 0.65), parent=e)
        p = box((1.3, 0.05, 0.55), (sx * 1.15, 0, 0), PANEL, parent=e)
        for k in range(3): box((0.02, 0.07, 0.56), (sx * (0.72 + 0.43 * k), 0, 0), (0.55, 0.6, 0.75), parent=e)
    cyl(0.22, 0.12, (0, 0, -0.46), (0.85, 0.85, 0.88), parent=e)        # antena hacia la Tierra
    hand = None
    if clock:
        cyl(0.27, 0.04, (0, -0.37, 0.05), WHITE, parent=e, rot=(math.pi / 2, 0, 0))
        hand = empty((0, -0.4, 0.05), parent=e)
        box((0.035, 0.02, 0.22), (0, 0, 0.1), INK, parent=hand)
        sph(0.04, (0, -0.4, 0.05), RED, parent=e, seg=8)
    e.scale = (scale,) * 3
    return e, hand

def clock(loc, r, parent=None, face=WHITE):
    e = empty(loc, parent)
    cyl(r, 0.12, (0, 0, 0), face, parent=e, rot=(math.pi / 2, 0, 0))
    torus(r, 0.07 * r, (0, -0.02, 0), (0.2, 0.22, 0.28), parent=e, rot=(math.pi / 2, 0, 0))
    for k in range(12):
        a = k * math.tau / 12
        box((0.05 * r, 0.02, 0.16 * r), (0.82 * r * math.sin(a), -0.08, 0.82 * r * math.cos(a)), INK, parent=e, rot=(0, a, 0))
    hand = empty((0, -0.1, 0), parent=e)
    box((0.06 * r, 0.03, 0.75 * r), (0, 0, 0.32 * r), RED, parent=hand)
    sph(0.07 * r, (0, -0.12, 0), INK, parent=e, seg=10)
    return e, hand

def build():
    sc, cam = scene_setup(world=BG, shadow=0.35)
    S = {"cam": cam}; dyn = [cam]
    rng = random.Random(7)
    # ===== P: el móvil con el mapa =====
    ph = empty((0, 0, 0)); S["ph"] = ph; dyn.append(ph)
    rounded_slab(3.4, 7.0, 0.5, 0.4, (0, 0, -0.42), BODY, parent=ph)
    rounded_slab(3.2, 6.8, 0.42, 0.03, (0, 0, -0.02), MAPC, parent=ph)
    rounded_slab(0.9, 0.22, 0.11, 0.02, (0, 3.2, 0.03), INK, parent=ph)           # isla de la cámara
    cyl(0.3, 0.08, (1.1, 1.5, -0.47), (0.1, 0.1, 0.12), parent=ph, rot=(math.pi, 0, 0))
    S["streets"] = []
    for x in (-1.05, 0.25, 1.25):
        box((0.2, 6.6, 0.01), (x, 0, 0.02), STREET, parent=ph)
    for k in range(6):
        o = box((3.1, 0.2, 0.012), (0, 0, 0.025), STREET, parent=ph); S["streets"].append((o, k * 1.35, "h"))
    for k, (x, w) in enumerate(((-0.4, 0.95), (0.75, 0.7), (-1.45, 0.4), (0.75, 0.7))):
        o = box((w, 0.9, 0.011), (x, 0, 0.022), PARK, parent=ph); S["streets"].append((o, 0.6 + k * 2.1, "p"))
    o = box((3.15, 0.45, 0.011), (0, 0, 0.021), WATER, parent=ph); S["streets"].append((o, 4.0, "r"))
    S["halo"] = cyl(1.0, 0.01, (0, 0, 0.04), HALO, parent=ph, unique=True)
    S["dotw"] = cyl(0.27, 0.03, (0, 0, 0.05), WHITE, parent=ph)
    S["dot"] = cyl(0.2, 0.04, (0, 0, 0.06), BLUE, parent=ph)
    S["ghostw"] = cyl(0.27, 0.03, (0, 0, 0.05), WHITE, parent=ph)
    S["ghost"] = cyl(0.2, 0.04, (0, 0, 0.065), RED, parent=ph, unique=True)
    # panel de hora del móvil
    S["clk"] = ce = empty((0, 0, 0), parent=ph)
    rounded_slab(2.9, 1.1, 0.25, 0.04, (0, 0, 0.06), INK, parent=ce)
    S["clkt"] = text3d("12:00:00,000", (0, -0.03, 0.11), 0.42, WHITE, parent=ce, extrude=0.005, unique=True); font(S["clkt"])
    # señales que caen del cielo
    S["rings"] = [torus(1.0, 0.06, LEJOS, YEL, unique=True) for _ in range(4)]
    dyn += S["rings"]
    # ===== E: la Tierra y los satélites =====
    S["earth"] = ea = empty(EO); dyn.append(ea)
    sph(RE, (0, 0, 0), EARTH, parent=ea, seg=48)
    for _ in range(11):
        d = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-0.8, 0.8))).normalized()
        s = rng.uniform(0.7, 1.5)
        o = sph(s, d * (RE - s * 0.12), LAND, parent=ea, scale=(1, 1, 0.22), seg=16)
        o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d)
    for _ in range(140):
        d = Vector((rng.uniform(-1, 1), rng.uniform(0.2, 1), rng.uniform(-1, 1))).normalized()
        sph(rng.uniform(0.06, 0.16), EO + d * rng.uniform(70, 90), (0.8, 0.82, 0.95), seg=6)
    S["planes"] = []
    for j in range(6):
        M = (Matrix.Rotation(j * math.tau / 6, 3, 'Z') @ Matrix.Rotation(math.radians(55), 3, 'X'))
        S["planes"].append(M)
        o = torus(RS, 0.03, EO, ORB, unique=True); o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = M.to_quaternion()
        o.scale = (0.001,) * 3; S.setdefault("orbits", []).append(o)
    dyn += S["orbits"]
    S["const"] = []
    for i in range(31):
        e, _ = satellite(LEJOS, 0.45); S["const"].append((e, i % 6, (i // 6) * math.tau / 5.2 + (i % 6) * 0.5)); dyn.append(e)
    S["alt"] = bar_obj(YEL, 0.13, unique=True); dyn.append(S["alt"])
    S["sp"] = []
    for k in range(4):
        e, hand = satellite(LEJOS, 0.9, clock=(k == 0)); S["sp"].append(e); dyn.append(e)
        if k == 0: S["s1hand"] = hand
    S["srings"] = [torus(1.0, 0.035, LEJOS, YEL, unique=True) for _ in range(3)]; dyn += S["srings"]
    S["pulse"] = sph(0.32, LEJOS, YEL, seg=16, unique=True); S["trail"] = bar_obj(YEL, 0.05, unique=True)
    S["pin"] = pe = empty(LEJOS)
    sph(0.32, (0, 0, 0), BLUE, parent=pe, seg=16); torus(0.42, 0.07, (0, 0, 0), WHITE, parent=pe, rot=(math.pi / 2, 0, 0))
    dyn += [S["pulse"], S["trail"], pe]
    S["wires"] = []
    for k in range(4):
        o = sph(1.0, LEJOS, SCOL[k], seg=22, unique=True)
        m = o.modifiers.new("w", 'WIREFRAME'); m.thickness = 0.022; m.use_replace = True
        S["wires"].append(o)
    dyn += S["wires"]
    S["circle"] = torus(1.0, 0.035, LEJOS, WHITE, unique=True); dyn.append(S["circle"])
    S["pts"] = [sph(0.36, LEJOS, WHITE, seg=16, unique=True) for _ in range(2)]; dyn += S["pts"]
    S["lines"] = [bar_obj(SCOL[k], 0.04, unique=True) for k in range(4)]; dyn += S["lines"]
    # ===== D: dos relojes =====
    sph(30, DO + Vector((0, 4, -31.5)), LAND, seg=64)
    for k in range(7): box((0.6, 0.6, rng.uniform(0.6, 1.8)), DO + Vector((-5 + 1.6 * k, 6, -1.0)), (0.3, 0.33, 0.4))
    cyl(0.12, 2.6, DO + Vector((-1.7, 0.3, -0.4)), (0.4, 0.42, 0.48))
    S["ckE"], S["hE"] = clock(DO + Vector((-1.7, 0, 2.0)), 1.15)
    S["dsat"], _ = satellite(DO + Vector((1.5, 0.6, 5.0)), 1.6)
    S["ckS"], S["hS"] = clock(DO + Vector((2.0, -0.5, 5.0)), 1.15)
    S["pad"] = box((2.4, 2.4, 0.3), DO + Vector((1.5, 0.6, -1.2)), (0.35, 0.36, 0.42))
    S["flame"] = sph(0.5, LEJOS, (1.0, 0.55, 0.15), scale=(1, 1, 2.4), seg=16)
    S["dorb"] = torus(16, 0.05, DO + Vector((0, 3, -11.5)), ORB, rot=(math.pi / 2, 0, 0))
    dyn += [S["ckE"], S["dsat"], S["ckS"], S["flame"], S["pad"]]
    join_static(dyn)
    return sc, S

# ---------------- animación ----------------
def K():
    return dict(solo=T("solo escucha"), mira=T("mira hacia"), veinte=T("veinte mil"), treinta=T("treinta y un"), cada=T("cada uno"),
                soy=T("soy este"), senal=T("esa señal"), tarda=T("y tarda"), compara=T("tu móvil compara"), retraso=T("con el retraso"),
                calc=T("calcula"), uno=T("con un satélite"), esfera=T("una esfera"), dos=T("con dos"), circ=T("en un círculo"),
                tres=T("con tres"), dosp=T("en dos puntos"), espacio=T("y uno de ellos"), prob=T("pero hay un"), reloj=T("el reloj de tu"),
                cuarto=T("así que usas"), corrige=T("que corrige"), cuatro=T("por eso necesitas"), prec=T("y la precisión"),
                error=T("un error de"), tres00=T("son trescientos"), curioso=T("y aquí viene"), alli=T("allí arriba"),
                rapido=T("el tiempo pasa"), adel=T("los relojes de los"), einstein=T("lo predijo"), nadie=T("si nadie"),
                mapa=T("tu mapa"), ajust=T("así que los relojes"), todo=T("y todo esto"), sig=T("sígueme"))

def orbit_pt(M, a):
    return EO + M @ Vector((RS * math.cos(a), RS * math.sin(a), 0))

def phase(t):
    # la constelación gira deprisa, pero se calma mientras se explica la señal
    return 0.22 * min(t, 18.5) + 0.02 * max(0, min(t, 46) - 18.5) + 0.22 * max(0, t - 46)

def set_phone(t, S, k):
    ph = S["ph"]
    ph.location = Vector((0, 0, 0)); ph.rotation_euler = (math.pi / 2 - 0.22, 0, 0.18 + 0.05 * math.sin(t * 0.8))
    # desplazamiento del mapa y del punto
    scroll = 0.9 * t
    drift = Vector((0, 0, 0)); ghost = None
    if k["prec"] - 0.3 < t < k["curioso"]:                # error de 1 µs: el punto calculado salta dos calles
        g = seg(t, k["tres00"] - 0.4, k["tres00"] + 0.5)
        ghost = Vector((0.9 * g, 1.6 * g, 0))
    if k["nadie"] - 0.3 < t < k["ajust"]:                 # deriva de 10 km: el mapa corre, el punto se va
        u = seg(t, k["mapa"] - 0.3, k["mapa"] + 2.4)
        scroll += 14 * u
        drift = Vector((0.0, 0, 0))
        ghost = Vector((0.9 * u, 2.4 * u, 0))
    for o, y0, kind in S["streets"]:
        y = ((y0 - scroll) % 8.1) - 4.05
        o.location = Vector((o.location.x, y, o.location.z))
        vis = abs(y) < 3.15 - (0.4 if kind == "p" else 0.2)
        o.hide_render = not vis
    pul = 1 + 0.25 * math.sin(t * 5)
    S["halo"].scale = (0.5 * pul, 0.5 * pul, 1)
    for o in (S["dot"], S["dotw"]): o.location.x, o.location.y = drift.x, drift.y
    S["halo"].location.x, S["halo"].location.y = drift.x, drift.y
    if ghost is not None:
        S["ghost"].location = Vector((ghost.x, ghost.y, 0.065)); S["ghostw"].location = Vector((ghost.x, ghost.y, 0.05))
        S["ghost"].hide_render = S["ghostw"].hide_render = ghost.length < 0.05
    else:
        S["ghost"].hide_render = S["ghostw"].hide_render = True
    # panel de hora (reloj del móvil, no atómico)
    if k["reloj"] - 0.2 < t < k["cuarto"] + 0.2:
        S["clkt"].hide_render = False
        a = seg(t, k["reloj"] - 0.2, k["reloj"] + 0.2)
        S["clk"].location = Vector((0, -1.6, 0)); S["clk"].scale = (a + 0.001,) * 3
        r = random.Random(int(t * 10)); S["clkt"].data.body = "12:00:00,%03d" % (r.randint(0, 999))
        S["clkt"].hide_render = False
    else:
        S["clk"].scale = (0.001,) * 3; S["clkt"].hide_render = True
    # anillos de señal que bajan al móvil
    on = t < k["mira"] or k["todo"] - 0.2 < t
    top = Vector((0, -0.9, 3.4))
    for i, r in enumerate(S["rings"]):
        if not on: hide(r); continue
        u = ((t * 0.7 + i / 4) % 1.0)
        put(r, top + Vector((0.6 * math.sin(i * 2.1), 0, 6.0 * (1 - u))), (0.4 + 1.6 * (1 - u)))
        r.rotation_euler = (0.25, 0, 0)

def set_space(t, S, k):
    ea = S["earth"]; ea.rotation_euler = (0, 0, 0.12 * min(t, 18.5) - 1.2)
    ph_ = phase(t)
    # órbitas y constelación
    for j, o in enumerate(S["orbits"]):
        g = seg(t, k["treinta"] - 0.6 + 0.12 * j, k["treinta"] + 0.2 + 0.12 * j)
        o.scale = (max(g, 0.001),) * 3
    n_on = int(31 * seg(t, k["treinta"] + 0.1, k["treinta"] + 2.4)) if t < k["cada"] else 31
    dim = t > k["cada"] - 0.3
    for i, (e, j, a0) in enumerate(S["const"]):
        M = S["planes"][j]
        if i < n_on or (t < k["treinta"] and False):
            put(e, orbit_pt(M, a0 + ph_ * (1 + 0.03 * j)), 0.45 * (0.6 if dim else 1.0))
        else: hide(e)
    # cota de altura (20.000 km)
    if k["veinte"] - 0.2 < t < k["treinta"] + 0.5:
        d = nv(-0.75, -0.55, 0.38)
        u = seg(t, k["veinte"], k["veinte"] + 1.8)
        bar_set(S["alt"], EO + d * RE, EO + d * (RE + (RS - RE) * u + 0.001))
    else: hide(S["alt"]); S["alt"].scale = (0.001,) * 3
    # satélites destacados
    shows = [(k["cada"] - 0.4, 99), (k["dos"] - 0.4, 99), (k["tres"] - 0.4, 99), (k["cuarto"], 99)]
    for i, e in enumerate(S["sp"]):
        a, b = shows[i]
        if t > a:
            g = seg(t, a, a + 0.5); put(e, SATS[i] + Vector((0, 0, 0.12 * math.sin(t * 1.5 + i))), 0.9 * g + 0.001)
            e.rotation_euler = (0, 0, 0.15 * math.sin(t * 0.7 + i))
        else: hide(e)
    S["s1hand"].rotation_euler = (0, -t * 25, 0)          # reloj atómico: gira sin parar
    # anillos de la señal del satélite 1 («soy este satélite…»)
    for i, r in enumerate(S["srings"]):
        if k["cada"] + 1.0 < t < k["senal"] + 0.3:
            u = ((t * 0.9 + i / 3) % 1.0)
            put(r, SATS[0] + Vector((0, 0, 0)), 0.5 + 2.6 * u); r.rotation_euler = (math.pi / 2, 0, 0)
        else: hide(r)
    # la señal viaja hasta ti
    if k["senal"] < t < k["compara"] + 0.5:
        u = seg(t, k["senal"] + 0.2, k["compara"] - 0.4)
        p = SATS[0].lerp(PIN, u)
        put(S["pulse"], p, 1 + 0.2 * math.sin(t * 12)); bar_set(S["trail"], SATS[0], p + Vector((0, 0, 0.0001)))
        if u >= 1: hide(S["pulse"])
    else: hide(S["pulse"]); hide(S["trail"]); S["trail"].scale = (0.001,) * 3
    if t > k["senal"] - 0.3:
        put(S["pin"], PIN + (PIN - EO).normalized() * 0.3, 1.5 * seg(t, k["senal"] - 0.3, k["senal"] + 0.2) * (1 + 0.15 * math.sin(t * 6)) + 0.001)
        S["pin"].rotation_euler = (0, 0, 0)
    else: hide(S["pin"])
    # esferas de distancia
    starts = [k["uno"] + 0.3, k["dos"] + 0.1, k["tres"] + 0.1, k["cuarto"] + 0.6]
    for i, w in enumerate(S["wires"]):
        if starts[i] < t:
            r = (SATS[i] - PIN).length
            g = seg(t, starts[i], starts[i] + 1.3)
            g2 = 1 - seg(t, k["corrige"] + 0.8, k["cuatro"] + 0.3)          # al final se recogen y quedan las 4 líneas
            put(w, SATS[i], r * g * g2 + 0.001)
            # la del móvil no cuadra hasta que llega el cuarto satélite
            if k["reloj"] < t < k["corrige"] + 0.6 and i < 3:
                wob = 0.35 * (1 - seg(t, k["corrige"], k["corrige"] + 0.6)) * math.sin(t * 7 + i * 2)
                w.scale = ((r + wob) * g2 + 0.001,) * 3
            bar_set(S["lines"][i], SATS[i], SATS[i].lerp(PIN, g) + Vector((0, 0, 0.0001)))
        else: hide(w); hide(S["lines"][i]); S["lines"][i].scale = (0.001,) * 3
    # círculo de dos esferas
    if k["circ"] - 0.4 < t < k["prob"]:
        S1, S2 = SATS[0], SATS[1]; r1 = (S1 - PIN).length; r2 = (S2 - PIN).length; d = (S2 - S1).length; u = (S2 - S1) / d
        a = (r1 * r1 - r2 * r2 + d * d) / (2 * d); h = math.sqrt(max(r1 * r1 - a * a, 0.01))
        put(S["circle"], S1 + a * u, h * seg(t, k["circ"] - 0.4, k["circ"] + 0.3) + 0.001)
        S["circle"].rotation_mode = 'QUATERNION'; S["circle"].rotation_quaternion = Vector((0, 0, 1)).rotation_difference(u)
    else: hide(S["circle"])
    # dos puntos: tú y uno en el espacio
    if k["dosp"] - 0.3 < t < k["prob"] + 0.5:
        g = seg(t, k["dosp"] - 0.3, k["dosp"] + 0.2)
        put(S["pts"][0], PIN, 0.9 * g + 0.001)
        bad = seg(t, k["espacio"] + 0.6, k["espacio"] + 1.2)
        put(S["pts"][1], PSPACE, (0.9 * g) * (1 - bad) + 0.001 + 0.25 * math.sin(t * 8) * g * (1 - bad))
        set_color(S["pts"][1], RED if t > k["espacio"] else WHITE)
    else: hide(S["pts"][0]); hide(S["pts"][1])

def set_clocks(t, S, k):
    base = -t * 2.2
    lead = 0.0
    if t < k["ajust"]:
        lead = -1.6 * seg(t, k["rapido"], k["adel"] + 4.0) - 0.4 * seg(t, k["adel"] + 4.0, k["nadie"])
        sat = DO + Vector((1.5, 0.6, 5.0)); S["pad"].hide_render = True; hide(S["flame"])
    else:
        lift = seg(t, k["ajust"] + 1.4, k["todo"] + 0.6)
        lead = -2.0 * (1 - seg(t, k["ajust"] + 0.3, k["ajust"] + 1.2))
        sat = DO + Vector((1.5, 0.6, mix(0.6, 5.0, lift)))
        S["pad"].hide_render = False
        if lift > 0.01: put(S["flame"], sat + Vector((0, -0.6, -2.1)), 0.9 + 0.15 * math.sin(t * 30))
        else: hide(S["flame"])
    S["dsat"].location = sat; S["ckS"].location = sat + Vector((0, -1.1, 0))
    S["hE"].rotation_euler = (0, base, 0)
    S["hS"].rotation_euler = (0, base + lead, 0)

def V_(at, off, lens=38):
    return (tuple(Vector(at) + Vector(off)), tuple(at), lens)

def cams(k):
    P, E, D = Vector((0, 0, 0)), EO, DO
    segs = []
    # P1: móvil, primer plano que se mueve
    segs.append((0, k["mira"], [(-1,) + V_(P + Vector((0, 0, 2.0)), (2.4, -8.0, 1.6), 40), (0,) + V_(P + Vector((0, 0, 2.0)), (2.2, -7.6, 1.5), 40),
                                (k["solo"],) + V_(P + Vector((0, 0, 2.4)), (1.0, -9.5, 1.8), 40),
                                (k["mira"],) + V_(P + Vector((0, 0, 3.0)), (0.2, -7.5, 1.0), 40), (k["mira"] + 1,) + V_(P + Vector((0, 0, 4)), (0, -7, 0), 40)]))
    # E1..E3: espacio
    segs.append((k["mira"], k["reloj"], [
        (k["mira"] - 1,) + V_(E + Vector((0, 0, 0)), (0, -16, 3), 38), (k["mira"],) + V_(E, (0, -16, 3), 38),
        (k["veinte"] + 1.0,) + V_(E + Vector((-1.5, 0, 0.8)), (-3, -26, 5), 38),
        (k["treinta"] + 1.5,) + V_(E, (2, -36, 8), 38),
        (k["cada"] - 0.3,) + V_(E, (3, -35, 9), 38),
        (k["cada"] + 0.9,) + V_(SATS[0], (0.6, -5.4, 0.3), 38),
        (k["senal"] - 0.6,) + V_(SATS[0] + Vector((0.2, 0, -0.3)), (1.4, -5.5, -0.4), 38),
        (k["senal"] + 1.5,) + V_(SATS[0].lerp(PIN, 0.5), (2, -17, 2), 38),
        (k["compara"],) + V_(SATS[0].lerp(PIN, 0.5), (3, -17, 2.5), 38),
        (k["calc"],) + V_(SATS[0].lerp(PIN, 0.6), (2, -19, 2), 38),
        (k["uno"] + 0.6,) + V_(PIN + Vector((0, 0, 1.5)), (-2, -40, 5), 38),
        (k["dos"] + 0.5,) + V_(PIN + Vector((0.5, 0, 1.5)), (3, -42, 5), 38),
        (k["tres"] + 0.3,) + V_(PIN + Vector((0, 0, 1.5)), (-2, -44, 6), 38),
        (k["espacio"] + 0.5,) + V_(PIN.lerp(PSPACE, 0.5) + Vector((0, 0, 0.5)), (-3, -36, 4), 38),
        (k["prob"] + 0.5,) + V_(PIN.lerp(PSPACE, 0.5) + Vector((0, 0, 0.5)), (-3, -37, 4), 38),
        (k["reloj"] + 1,) + V_(PIN.lerp(PSPACE, 0.5), (-3, -37, 4), 38)]))
    # P2: la hora del móvil
    segs.append((k["reloj"], k["cuarto"], [(k["reloj"] - 1,) + V_(P + Vector((0, 0, 0.5)), (-1.5, -8, 1.5), 40),
                                          (k["reloj"],) + V_(P + Vector((0, 0, 0.5)), (-1.2, -7.5, 1.5), 40),
                                          (k["cuarto"],) + V_(P + Vector((0, 0, 0.3)), (0.5, -6.2, 1.0), 40), (k["cuarto"] + 1,) + V_(P, (0.6, -6, 1), 40)]))
    # E4: cuarto satélite
    segs.append((k["cuarto"], k["prec"], [(k["cuarto"] - 1,) + V_(PIN + Vector((1, 0, 0.5)), (4, -44, 3), 38),
                                         (k["cuarto"],) + V_(PIN + Vector((1, 0, 0.5)), (4, -44, 3), 38),
                                         (k["corrige"] + 0.5,) + V_(PIN + Vector((0.5, 0, 1.0)), (-2, -42, 4), 38),
                                         (k["cuatro"] + 0.4,) + V_(EO + Vector((0, -1, 0.5)), (0, -30, 3), 38), (k["prec"] + 1,) + V_(EO, (0, -29, 3), 38)]))
    # P3: el error de 300 m en el mapa
    segs.append((k["prec"], k["curioso"], [(k["prec"] - 1,) + V_(P + Vector((0, 0, 0.5)), (0, -7.8, 2.6), 40),
                                          (k["prec"],) + V_(P + Vector((0, 0, 0.5)), (0.3, -7.5, 2.5), 40),
                                          (k["tres00"],) + V_(P + Vector((0.3, 0, 1.0)), (0.6, -6.6, 2.1), 40),
                                          (k["curioso"],) + V_(P + Vector((0.3, 0, 1.0)), (0.9, -6.8, 2.0), 40), (k["curioso"] + 1,) + V_(P, (1, -7, 2), 40)]))
    # D1: relojes
    segs.append((k["curioso"], k["nadie"], [(k["curioso"] - 1,) + V_(DO + Vector((0, 0, 3.0)), (0, -16, 0.5), 38),
                                           (k["curioso"],) + V_(DO + Vector((0, 0, 3.0)), (0.5, -16, 0.5), 38),
                                           (k["alli"] + 0.5,) + V_(DO + Vector((1.5, 0, 4.0)), (0.5, -12, 0.5), 38),
                                           (k["adel"],) + V_(DO + Vector((0, 0, 4.4)), (0, -17, -0.8), 38),
                                           (k["einstein"],) + V_(DO + Vector((0, 0, 4.4)), (-0.6, -16.5, -0.8), 38),
                                           (k["nadie"],) + V_(DO + Vector((0, 0, 4.4)), (-1, -16, -0.8), 38), (k["nadie"] + 1,) + V_(DO, (-1, -14, 0), 38)]))
    # P4: deriva de 10 km
    segs.append((k["nadie"], k["ajust"], [(k["nadie"] - 1,) + V_(P + Vector((0, 0, 0.8)), (-1, -8, 2.5), 40),
                                         (k["nadie"],) + V_(P + Vector((0, 0, 0.8)), (-1, -8, 2.5), 40),
                                         (k["ajust"],) + V_(P + Vector((0, 0, 1.0)), (0.4, -7.2, 2.4), 40), (k["ajust"] + 1,) + V_(P, (0.5, -7, 2), 40)]))
    # D2: ajuste y lanzamiento
    segs.append((k["ajust"], k["todo"], [(k["ajust"] - 1,) + V_(DO + Vector((0, 0, 1.0)), (0.5, -13, 0.5), 38),
                                        (k["ajust"],) + V_(DO + Vector((0, 0, 1.0)), (0.5, -13, 0.5), 38),
                                        (k["todo"],) + V_(DO + Vector((0.5, 0, 3.0)), (0, -15, -0.3), 38), (k["todo"] + 1,) + V_(DO, (0, -15, 0), 38)]))
    # P5: final
    segs.append((k["todo"], DUR + 5, [(k["todo"] - 1,) + V_(P + Vector((0, 0, 1.0)), (2, -8, 2), 40),
                                      (k["todo"],) + V_(P + Vector((0, 0, 2.2)), (1.8, -9.0, 1.6), 40),
                                      (k["sig"],) + V_(P + Vector((0, 0, 2.4)), (0.8, -10.5, 1.8), 40),
                                      (DUR + 5,) + V_(P + Vector((0, 0, 1.6)), (0.6, -11, 2.4), 40)]))
    return segs

def where(t, k):
    for i, (a, b, ks) in enumerate(cams(k)):
        if a <= t < b: return i, ks
    return len(cams(k)) - 1, cams(k)[-1][2]

def pose(t, S):
    k = K()
    set_phone(t, S, k); set_space(t, S, k); set_clocks(t, S, k)
    i, ks = where(t, k)
    apply_cam(S["cam"], *cam_state(t, ks, drift=0.03))
    S["_seg"] = i

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    ph = S["ph"].matrix_world
    return {"dot": Pj(ph @ S["dot"].location), "ghost": Pj(ph @ S["ghost"].location), "clk": Pj(ph @ Vector((0, -1.6, 0.1))),
            "phone": Pj(ph @ Vector((0, 3.4, 0))), "sat1": Pj(SATS[0]), "sat4": Pj(SATS[3]), "pin": Pj(PIN), "space": Pj(PSPACE),
            "earth": Pj(EO), "altmid": Pj(EO + nv(-0.75, -0.55, 0.38) * (RE + RS) / 2),
            "ckE": Pj(DO + Vector((-1.7, 0, 2.0))), "ckS": Pj(S["ckS"].location), "seg": [S["_seg"], 0, 0]}

if __name__ == "__main__":
    run("gps", build, pose, anchors)
