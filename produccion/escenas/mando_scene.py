# «Si tuvieras que inventar el mando de la tele…»: un pulgar pulsa y el LED de la punta destella (visto por la cámara);
# a simple vista no se ve; el mando se queda en hueco y se coloca el LED; luz normal con destellos hacia la tele;
# infrarrojo invisible; el sol de la ventana, la bombilla y la estufa también mandan infrarrojo al receptor;
# el LED parpadea muy rápido y el receptor ignora lo demás; ráfagas largas y cortas (unos y ceros) viajan a la tele;
# la tele cambia de canal o ignora el código; la luz rebota en la pared pero no atraviesa el sofá.
import bpy, math, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("mando")
BG = (0.07, 0.075, 0.1); WALL = (0.25, 0.27, 0.34); FLOOR = (0.34, 0.27, 0.21); RUG = (0.32, 0.22, 0.2)
SOFA = (0.3, 0.37, 0.5); SOFA2 = (0.26, 0.32, 0.44); BODY = (0.2, 0.2, 0.23); BTN = (0.38, 0.39, 0.43)
PCB = (0.1, 0.4, 0.25); SKIN = (0.93, 0.7, 0.56); TVB = (0.06, 0.06, 0.07); METAL = (0.7, 0.72, 0.76)
IR = (0.78, 0.45, 1.0); IRD = (0.5, 0.25, 0.8); VIS = (1.0, 0.95, 0.7); HOTC = (1.0, 0.45, 0.22); GRIS = (0.45, 0.45, 0.5)
CANALES = [(0.2, 0.5, 0.9), (0.95, 0.55, 0.2), (0.3, 0.75, 0.45), (0.85, 0.3, 0.45), (0.95, 0.85, 0.3), (0.35, 0.8, 0.9)]
LEJOS = (0, 0, -300)
RM0 = Vector((0, 0, 7.0))              # mando en la mano
RMS = Vector((0, -11.6, 4.6))          # mando detrás del respaldo del sofá
RX = Vector((4.5, 29.65, 5.75))        # receptor de la tele
WB = Vector((16.6, 15.0, 7.0))         # punto de rebote en la pared
SOL = Vector((-11.0, 31.6, 15.0)); BOMB = Vector((10.5, 25.5, 13.0)); ESTU = Vector((-9.0, 26.3, 1.9))
LED_L = Vector((0, 1.05, 0.085))
SPEED = 16.0

def alpha(o, a):
    m = o.active_material; m.diffuse_color = (*m.diffuse_color[:3], a); m.surface_render_method = 'BLENDED'

def poly(pts):
    pts = [Vector(p) for p in pts]; L = [0.0]
    for a, b in zip(pts, pts[1:]): L.append(L[-1] + (b - a).length)
    return pts, L
def at(path, s):
    pts, L = path; s = max(0.0, min(L[-1], s))
    for i in range(len(pts) - 1):
        if L[i] <= s <= L[i + 1]: return pts[i].lerp(pts[i + 1], (s - L[i]) / max(L[i + 1] - L[i], 1e-6))
    return pts[-1]

# ---------- tiempos ----------
def TT():
    d = {}
    for k in ("ves esa", "a simple", "vamos a inventar", "quieres cambiar", "así que usas luz", "una bombillita", "pero si fuera",
              "así que usas infrarrojo", "tus ojos", "pero muchas", "pero hay un problema", "el sol", "las bombillas", "y la estufa",
              "cómo distingue", "así que haces", "treinta y ocho", "el receptor", "e ignora", "pero ahora tienes", "así que mandas",
              "ráfaga larga", "ráfaga corta", "y aquí viene", "cada pulsación", "ocho dicen", "y las otras", "para comprobar",
              "si algo", "la tele lo", "por eso tienes", "la luz rebota", "pero no atraviesa", "sígueme"):
        d[k] = T(k)
    d["ocho2"] = T("ocho dicen", 2)
    return d
TM = TT()

# código: 8 bits de aparato + 8 de tecla + los 16 al revés
ADDR = [1, 0, 1, 1, 0, 0, 1, 0]; CMD = [0, 1, 1, 0, 1, 0, 0, 0]
BITS = ADDR + CMD + [1 - b for b in ADDR] + [1 - b for b in CMD]
LONG, SHORT, GAP = 0.42, 0.16, 0.2
def code_on(te, t0):
    """¿está encendido el LED en te para una trama que empieza en t0? (se repite)"""
    tot = sum((LONG if b else SHORT) + GAP for b in BITS)
    x = (te - t0) % tot
    for b in BITS:
        d = LONG if b else SHORT
        if x < d: return True
        x -= d
        if x < GAP: return False
        x -= GAP
    return False

PRESS = [-0.5, 1.35, 2.5, 3.45, 4.55, 5.6]
def pressed(t):
    m = TM
    if any(p <= t < p + (0.9 if p < 0 else 0.38) for p in PRESS): return True
    for p in (m["pero si fuera"] + 0.5, m["pero si fuera"] + 1.9, m["pero si fuera"] + 3.2):
        if p <= t < p + 0.45: return True
    for k in range(6):
        p = m["así que usas infrarrojo"] + 0.6 + 1.05 * k
        if p <= t < p + 0.4: return True
    if m["así que haces"] + 0.3 <= t < m["pero ahora tienes"]: return True
    if m["así que mandas"] - 0.2 <= t < m["si algo"] + 2.3: return True
    if m["por eso tienes"] + 0.2 <= t < m["sígueme"] - 0.2: return True
    if t > m["sígueme"] + 0.2 and (t - m["sígueme"]) % 0.9 < 0.4: return True
    return False

def led_on(te):
    """el LED emite en te (patrón de parpadeo según la fase)"""
    m = TM
    if not pressed(te): return False
    if m["así que haces"] <= te < m["pero ahora tienes"]: return math.sin(math.tau * 5.0 * te) > 0
    if m["así que mandas"] - 0.2 <= te < m["sígueme"] - 0.2 and te >= m["así que mandas"] - 0.2:
        if te < m["por eso tienes"]: return code_on(te, m["así que mandas"])
        return code_on(te, m["por eso tienes"] + 0.2)
    return True

def build():
    sc, cam = scene_setup(world=BG, shadow=0.38, light_rot=60)
    S = {"cam": cam}
    # habitación
    box((70, 90, 0.2), (0, 5, -0.1), FLOOR)
    box((30, 22, 0.08), (0, 12, 0.04), RUG)
    box((40, 0.4, 30), (0, 32.2, 15), WALL)
    for sx in (-1, 1): box((0.4, 60, 30), (sx * 17.2, 2, 15), WALL)
    # ventana con el sol
    box((9.0, 0.2, 8.0), (-11, 31.95, 15), (0.5, 0.62, 0.78))
    for dx in (-4.5, 0, 4.5): box((0.35, 0.3, 8.3), (-11 + dx, 31.85, 15), (0.85, 0.85, 0.88))
    for dz in (-4, 0, 4): box((9.3, 0.3, 0.35), (-11, 31.85, 15 + dz), (0.85, 0.85, 0.88))
    sph(1.6, SOL, (1.0, 0.86, 0.3), scale=(1, 0.2, 1))
    # lámpara de pie
    cyl(1.4, 0.2, (BOMB.x, BOMB.y, 0.1), METAL, v=24); cyl(0.12, 12.0, (BOMB.x, BOMB.y, 6.0), METAL, v=12)
    sph(0.85, BOMB, (1.0, 0.93, 0.55))
    bpy.ops.mesh.primitive_cone_add(radius1=2.0, radius2=1.0, depth=2.0, location=(BOMB.x, BOMB.y, BOMB.z + 1.3), vertices=32)
    setup(bpy.context.object, (0.92, 0.88, 0.8))
    # estufa
    box((5.0, 1.4, 3.6), (ESTU.x, ESTU.y + 0.6, 1.8), (0.88, 0.88, 0.9))
    S["estu"] = [cyl(0.22, 4.4, (ESTU.x, ESTU.y - 0.15, 0.9 + 0.9 * k), HOTC, rot=(0, math.pi / 2, 0), v=12, unique=True) for k in range(3)]
    # mueble y tele
    box((16, 3.0, 3.2), (0, 30.2, 1.6), (0.35, 0.27, 0.22))
    box((13.0, 0.6, 7.6), (0, 30.4, 8.6), TVB)
    S["screen"] = box((12.2, 0.1, 6.8), (0, 30.07, 8.65), CANALES[0], unique=True)
    box((1.0, 0.25, 0.25), (RX.x, RX.y - 0.05, RX.z), (0.25, 0.05, 0.08))
    S["rxled"] = sph(0.12, (RX.x - 0.8, RX.y - 0.12, RX.z), (0.2, 0.2, 0.2), seg=10, unique=True)
    box((4, 2.0, 0.3), (0, 30.4, 3.35), TVB); box((0.8, 0.5, 1.5), (0, 30.5, 4.2), TVB)
    # sofá
    box((15, 8, 3.2), (0, -5.2, 2.0), SOFA); box((15, 2.0, 9.0), (0, -9.2, 4.5), SOFA2)
    for sx in (-1, 1): box((1.6, 9, 6.0), (sx * 8.3, -5.0, 3.0), SOFA2)
    for sx in (-3.5, 3.5): box((6.8, 6.8, 1.2), (sx, -4.8, 4.1), (0.36, 0.43, 0.56))
    # mando (todo cuelga de RM)
    S["RM"] = RM = empty(RM0)
    S["shell"] = rounded_slab(0.62, 2.1, 0.22, 0.2, (0, 0, -0.1), BODY, parent=RM, unique=True)
    box((0.5, 1.9, 0.03), (0, 0, -0.02), PCB, parent=RM)
    box((0.2, 0.25, 0.04), (0, -0.4, 0.01), (0.08, 0.08, 0.09), parent=RM)
    S["power"] = cyl(0.07, 0.06, (0.17, 0.82, 0.12), (0.85, 0.2, 0.2), parent=RM, v=16)
    for i in range(3):
        for j in range(4):
            cyl(0.06, 0.06, (-0.17 + 0.17 * i, 0.15 - 0.22 * j, 0.12), BTN, parent=RM, v=16)
    S["boton"] = cyl(0.1, 0.06, (0, 0.47, 0.12), (0.5, 0.52, 0.58), parent=RM, v=20)
    # LED (se coloca)
    S["led"] = led = empty(LEJOS, parent=RM)
    cyl(0.065, 0.2, (0, -0.1, 0), (0.55, 0.5, 0.65), parent=led, rot=(math.pi / 2, 0, 0), v=16)
    sph(0.066, (0, 0, 0), (0.6, 0.55, 0.72), parent=led, seg=12)
    for sx in (-0.03, 0.03): box((0.015, 0.25, 0.015), (sx, -0.25, -0.03), METAL, parent=led)
    S["glow"] = sph(0.12, LEJOS, IR, seg=32, unique=True); alpha(S["glow"], 0.45)
    S["core"] = sph(0.075, LEJOS, (1, 1, 1), seg=12, unique=True)
    # mano: palma y pulgar
    sph(0.5, (0.0, -0.45, -0.34), SKIN, parent=RM, scale=(0.85, 1.5, 0.5), seg=28)
    for k in range(3): sph(0.12, (0.36, 0.05 - 0.3 * k, -0.08), SKIN, parent=RM, scale=(0.8, 1.2, 1.0), seg=14)
    S["pulgar"] = bar_obj(SKIN, 0.105)
    S["yema"] = sph(0.11, LEJOS, SKIN, seg=14)
    # fotones
    S["fot"] = [sph(0.15, LEJOS, IR, seg=8, unique=True) for _ in range(110)]
    dyn = [cam, RM, S["screen"], S["rxled"], S["estu"], S["glow"], S["core"], S["pulgar"], S["yema"], S["fot"]]
    join_static(dyn)
    return sc, S

def rm_pose(t):
    m = TM
    loc = keyed(t, [(0, RM0), (m["pero no atraviesa"] - 0.35, RM0), (m["pero no atraviesa"] + 0.15, RMS),
                    (m["sígueme"] - 0.2, RMS), (m["sígueme"] + 0.4, RM0), (DUR + 2, RM0)])
    rz = keyed(t, [(0, 0.0), (m["por eso tienes"], 0.0), (m["por eso tienes"] + 0.6, -0.55), (m["pero no atraviesa"] - 0.35, -0.55),
                   (m["pero no atraviesa"] + 0.15, 0.0), (DUR + 2, 0.0)])
    return Vector(loc), rz

def to_world(loc, rz, v):
    c, s = math.cos(rz), math.sin(rz)
    return loc + Vector((c * v.x - s * v.y, s * v.x + c * v.y, v.z))

def h(k, n=1.0):
    return ((math.sin(k * 12.9898 + n * 78.233) * 43758.5453) % 1.0)

def photons(t, led_w):
    """lista de (pos, color, escala)"""
    m = TM; out = []
    def stream(a, b, path, on, col, dt=0.045, speed=SPEED, sc=1.0, stop=None, jit=0.0, fade_end=None):
        L = path[1][-1]; tr = L / speed
        k0 = math.ceil(max(a, t - tr) / dt); k1 = math.floor(min(b, t) / dt)
        for k in range(k0, k1 + 1):
            te = k * dt
            if not on(te): continue
            s = speed * (t - te)
            if stop is not None and s > stop: continue
            p = at(path, s)
            if jit:
                p = p + Vector((h(k) - 0.5, h(k, 2) - 0.5, h(k, 3) - 0.5)) * jit * min(1, s / 3)
            c = col(te) if callable(col) else col
            g = sc
            if fade_end is not None and s > L - fade_end: g *= max(0.0, (L - s) / fade_end)
            out.append((p, c, g))
    direct = poly([led_w, RX])
    # luz normal (visible) con destellos
    stream(m["pero si fuera"], m["así que usas infrarrojo"], direct, led_on, VIS, sc=1.3)
    # infrarrojo
    stream(m["así que usas infrarrojo"], m["pero hay un problema"], direct, led_on, IRD, sc=1.1)
    # otras fuentes
    a0, a1 = m["el sol"] - 0.3, m["pero ahora tienes"] - 0.2
    ign = m["e ignora"]
    def col_o(te): return GRIS if t > ign + 0.2 else HOTC
    for src, dt, sgn in ((SOL, 0.13, 1), (BOMB, 0.17, 2), (ESTU + Vector((0, -0.4, 0.9)), 0.15, 3)):
        start = a0 + (0.0 if sgn == 1 else (m["las bombillas"] - m["el sol"] if sgn == 2 else m["y la estufa"] - m["el sol"]))
        stream(start, a1, poly([src, RX]), lambda te: True, col_o, dt=dt, speed=9.0, sc=1.0, jit=1.6,
               fade_end=(4.0 if t > ign else 0.6))
    # parpadeo rápido
    stream(m["así que haces"], m["pero ahora tienes"], direct, led_on, IR, dt=0.03, sc=1.1)
    # código
    stream(m["así que mandas"] - 0.2, m["por eso tienes"], direct, led_on, IR, dt=0.03, sc=1.15)
    # rebote en la pared
    rb = poly([led_w, WB, RX])
    stream(m["por eso tienes"] + 0.2, m["pero no atraviesa"] - 0.4, rb, led_on, IR, dt=0.03, sc=1.25, speed=20.0)
    # contra el sofá (se para en el respaldo)
    if t > m["pero no atraviesa"] - 0.2:
        stop = (led_w.y - (-10.25)) if led_w.y < -10.2 else 0.0
        stream(m["pero no atraviesa"] + 0.15, m["sígueme"] - 0.2, direct, led_on, IR, dt=0.03, sc=1.25, speed=10.0, stop=stop)
    return out

def pose(t, S):
    m = TM
    loc, rz = rm_pose(t)
    RM = S["RM"]; RM.location = loc; RM.rotation_euler = (0, 0, rz)
    led_w = to_world(loc, rz, LED_L + Vector((0, 0.06, 0)))
    # carcasa: opaca, en hueco mientras se inventa, vuelve al final
    hue = seg(t, m["vamos a inventar"], m["vamos a inventar"] + 1.0) * (1 - seg(t, m["sígueme"] - 0.6, m["sígueme"] + 0.3))
    alpha(S["shell"], 1 - 0.8 * hue)
    # LED: está al principio, desaparece al inventar, cae en su sitio
    t_led = m["una bombillita"] + 0.2
    if t < m["vamos a inventar"] + 0.5:
        S["led"].location = LED_L
    elif t < t_led:
        S["led"].location = LEJOS
    else:
        u = seg(t, t_led, t_led + 0.7)
        S["led"].location = LED_L + Vector((0, 0.0, 1.6 * (1 - u))) + Vector((0, 0, 0.1 * math.sin(math.pi * u)))
    led_present = (t < m["vamos a inventar"] + 0.5) or (t > t_led + 0.7)
    # pulgar
    pr = 1.0 if pressed(t) else 0.0
    tip = to_world(loc, rz, Vector((0, 0.47, 0.32 - 0.12 * pr)))
    root = to_world(loc, rz, Vector((-0.5, -0.75, 0.05)))
    bar_set(S["pulgar"], root, tip); S["yema"].location = tip
    S["boton"].location = (0, 0.47, 0.12 - 0.025 * pr)
    # brillo del LED
    vista_cam = t < m["a simple"] - 0.15 or (m["pero muchas"] - 0.1 < t < m["pero hay un problema"]) or t > m["sígueme"] + 0.3
    on = led_present and led_on(t)
    g, c = S["glow"], S["core"]
    if on:
        if m["pero si fuera"] <= t < m["así que usas infrarrojo"]:
            col, r, a = VIS, 0.4, 0.5
        elif vista_cam:
            col, r, a = (0.85, 0.55, 1.0), 0.16 + 0.015 * math.sin(t * 40), 0.6
        elif m["a simple"] - 0.15 <= t < m["vamos a inventar"]:
            col, r, a = (0, 0, 0), 0, 0
        else:
            col, r, a = IR, 0.2, 0.35
        if r > 0:
            g.location = led_w; g.scale = (r / 0.12,) * 3; set_color(g, col); alpha(g, a)
            c.location = led_w; set_color(c, (1, 1, 1) if col != IR else (0.92, 0.8, 1.0))
        else: g.location = c.location = LEJOS
    else:
        g.location = c.location = LEJOS
    # fotones
    cpos = cam_state(t, CAM(), drift=0.04)[0]
    ph = [x for x in photons(t, led_w) if (x[0] - cpos).length > 3.5]
    for k, o in enumerate(S["fot"]):
        if k < len(ph):
            p, col, s = ph[k]; o.location = p; o.scale = (s,) * 3; set_color(o, col)
        else: o.location = LEJOS
    # estufa al rojo
    for k, o in enumerate(S["estu"]):
        set_color(o, tuple(mix(a, b, 0.5 + 0.5 * math.sin(t * 3 + k)) for a, b in zip((0.9, 0.3, 0.15), (1.0, 0.55, 0.25))))
    # receptor y canal
    ok_times = [m["pero si fuera"] + 2.4, m["el receptor"] + 0.4, m["y aquí viene"] + 0.4, m["para comprobar"] + 1.3,
                m["la luz rebota"] + 0.6]
    ch = sum(1 for x in ok_times if t > x)
    set_color(S["screen"], CANALES[ch % len(CANALES)])
    rec = any(x - 0.5 < t < x for x in ok_times) or (m["si algo"] + 0.2 < t < m["la tele lo"] + 0.6 and int(t * 8) % 2)
    set_color(S["rxled"], (1.0, 0.3, 0.3) if rec else (0.2, 0.2, 0.2))
    apply_cam(S["cam"], *cam_state(t, CAM(), drift=0.04))

def CAM():
    m = TM; k = []
    def add(t, p, g, l): k.append((t, p, g, l))
    F1 = ((1.5, 2.8, 8.0), (0, 0.6, 7.05), 40)
    add(0.0, *F1)
    add(m["ves esa"], (1.1, 2.3, 7.75), (0, 0.6, 7.05), 40)
    add(m["a simple"] + 0.6, (1.3, 2.5, 7.9), (0, 0.5, 7.05), 40)
    add(m["vamos a inventar"] + 0.4, (3.0, -2.6, 9.5), (0, 0.3, 7.0), 36)
    add(m["quieres cambiar"] + 0.5, (7, -19, 17), (0, 13, 6), 28)
    add(m["así que usas luz"], (5, -15.5, 15), (0, 10, 7), 28)
    add(m["una bombillita"] + 0.3, (2.4, -1.5, 8.7), (0, 0.9, 7.05), 38)
    add(m["pero si fuera"] - 0.1, (2.6, -1.8, 8.9), (0, 1.0, 7.05), 38)
    add(m["pero si fuera"] + 1.0, (9, -7, 12), (0.5, 12, 7), 30)
    add(m["así que usas infrarrojo"], (8, -8, 12), (0.5, 13, 7), 30)
    add(m["tus ojos"], (6, -4, 10), (0, 8, 7), 32)
    add(m["tus ojos"] + 0.7, (4.6, 0.8, 9.2), (0, 1.0, 7.05), 38)
    add(m["pero muchas"] - 0.1, *F1)
    add(m["pero muchas"] + 0.3, *F1)
    add(m["pero hay un problema"] - 0.2, *F1)
    add(m["pero hay un problema"] + 0.3, (4.6, 0.6, 9.4), (0, 2.0, 7.0), 36)
    add(m["pero hay un problema"] + 0.9, (1.5, -21, 21), (-1, 18, 7), 26)
    add(m["cómo distingue"], (2, -18, 19), (0, 19, 7), 26)
    add(m["cómo distingue"] + 1.3, (7, 12, 10), (3.5, 29.6, 5.7), 32)
    add(m["así que haces"] + 0.6, (2.8, -1.4, 8.5), (0, 1.6, 7.0), 36)
    add(m["treinta y ocho"] + 0.4, (7, -6, 11), (1, 12, 6.5), 30)
    add(m["el receptor"] + 0.6, (8.5, 18, 8.5), (4, 29.5, 5.8), 32)
    add(m["e ignora"] + 0.3, (3, 3, 16), (-1, 24, 5), 28)
    add(m["pero ahora tienes"] + 0.8, (3.0, -2.4, 9.3), (0, 0.6, 7.0), 36)
    add(m["así que mandas"] + 0.8, (5, -4.5, 9.8), (1.5, 14, 6.4), 32)
    add(m["y aquí viene"], (5.5, -1, 9.6), (2, 17, 6.3), 32)
    add(m["ocho dicen"], (6, 5, 9.4), (2.5, 21, 6.2), 32)
    add(m["para comprobar"], (6.5, 12, 9), (3, 27, 6), 32)
    add(m["si algo"] + 0.3, (2, 14, 10), (1, 30, 7.5), 30)
    add(m["por eso tienes"] - 0.1, (2, 14.5, 10), (1, 30, 7.5), 30)
    add(m["por eso tienes"] + 1.0, (2, -11, 30), (6, 11, 3), 28)
    add(m["pero no atraviesa"] - 0.3, (2, -12, 28), (5, 9, 3), 28)
    add(m["pero no atraviesa"] + 0.4, (5, -21, 13), (0, -8, 5.5), 32)
    add(m["sígueme"] + 0.2, (5, -21.5, 13), (0, -8, 5.5), 32)
    add(m["sígueme"] + 0.9, *F1)
    add(DUR + 2, (1.3, 2.4, 7.9), (0, 0.4, 7.05), 40)
    return k

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    loc, rz = rm_pose(t)
    return {"led": Pj(to_world(loc, rz, LED_L + Vector((0, 0.05, 0.1)))), "rx": Pj(RX + Vector((0, -0.2, 0.3))),
            "sol": Pj(SOL + Vector((0, -0.4, 2.0))), "bomb": Pj(BOMB + Vector((0, 0, 2.6))), "estu": Pj(ESTU + Vector((0, 0, 2.2))),
            "wb": Pj(WB), "sofa": Pj((0, -10.3, 6.5)), "tv": Pj((0, 30, 12.6))}

if __name__ == "__main__":
    run("mando", build, pose, anchors)
