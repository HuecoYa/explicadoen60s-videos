# «Así escribe ChatGPT»: una pantalla de chat genérica donde la respuesta aparece trozo a trozo y se queda esperando;
# la pregunta se trocea en bloques (tokens); un estante se llena con los trozos del diccionario; cada trozo se vuelve
# una columna de números; los números entran en una red y sale un «?»; barras de probabilidad (playa 40, cama 20,
# oficina 10); el trozo elegido salta al final de la frase y el bucle se acelera; la aguja a veces elige una barra de
# abajo y tres respuestas salen distintas; un dato falso encaja en la frase y se marca en rojo.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("chatgpt")
BG = (0.07, 0.08, 0.11); BODY = (0.16, 0.17, 0.2); SCREEN = (0.1, 0.11, 0.14); USER = (0.25, 0.5, 1.0)
INK = (0.06, 0.06, 0.08); WHITE = (0.96, 0.96, 0.98); GREY = (0.5, 0.52, 0.56); RED = (0.95, 0.25, 0.25); YEL = (1.0, 0.85, 0.3)
PAL = [(0.45, 0.65, 1.0), (1.0, 0.6, 0.4), (0.45, 0.88, 0.6), (0.9, 0.55, 0.95), (1.0, 0.85, 0.4), (0.4, 0.88, 0.95)]
NODE = (0.55, 0.6, 0.75); WIRE = (0.3, 0.33, 0.42); PULSE = (1.0, 0.85, 0.3)
LEJOS = (0, 0, -200)
ROWZ = 3.6
FONT = None
for p in (os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "fuentes", "Poppins-Bold.ttf"),
          os.path.expanduser("~/.fonts/Poppins-Bold.ttf")):
    if os.path.exists(p): FONT = p; break

# ---------- textos ----------
RESP = ["Me", " voy", " a", " la", " playa", " con", " mis", " amigos", " este", " finde.", " ¿Te", " apuntas?"]
PROMPT = ["Recom", "iénd", "ame", " una", " peli"]
CTX = ["me", " voy", " a", " la"]
APP = [" playa", " con", " mis", " amigos", " este", " verano", "."]
CICLOS = [  # candidatos (texto, %) de cada vuelta; el primero es el elegido
    [(" playa", 40), (" cama", 20), (" oficina", 10)],
    [(" con", 35), (" mañana", 25), (".", 15)],
    [(" mis", 45), (" mi", 30), (" los", 10)],
    [(" amigos", 50), (" primos", 20), (" tíos", 10)],
    [(" este", 40), (" el", 30), (",", 10)],
    [(" verano", 60), (" finde", 25), (" mes", 5)],
    [(".", 70), (" y", 15), ("!", 10)],
]
VAR = ["playa", "cama", "oficina"]
FAKE_CTX = ["La", " Luna", " está", " a"]
FAKE = [(" 38.000 km", 35), (" 384.400 km", 30), (" 350.000 km", 10)]

def font(o):
    if FONT:
        try: o.data.font = bpy.data.fonts.load(FONT, check_existing=True)
        except Exception: pass

def token(txt, col, size=0.55, thick=0.3, parent=None, tcol=INK):
    e = empty(LEJOS, parent)
    t = text3d(txt.strip() or txt, (0, -thick - 0.01, -size * 0.06), size, tcol, parent=e, extrude=0.01, rot=(math.pi / 2, 0, 0), unique=True)
    font(t); bpy.context.view_layer.update()
    w = max(t.dimensions.x, size * 0.4) + size * 0.75; h = size * 1.45
    s = rounded_slab(w, h, min(0.18, h / 3), thick, (0, 0, 0), col, parent=e, unique=True); s.rotation_euler = (math.pi / 2, 0, 0)
    return {"e": e, "t": t, "s": s, "w": w, "col": col}

def layout(ws, x0, z0, maxw, gap=0.14, lh=1.15):
    pos = []; x = x0; z = z0
    for w in ws:
        if x + w > x0 + maxw and x > x0: x = x0; z -= lh
        pos.append(Vector((x + w / 2, 0, z))); x += w + gap
    return pos

def build():
    sc, cam = scene_setup(world=BG, shadow=0.3)
    S = {"cam": cam}
    # ---------- móvil con un chat genérico ----------
    S["movil"] = m = empty(LEJOS)
    o = rounded_slab(7.3, 15.4, 1.0, 0.75, (0, 0.75, 0), BODY, parent=m); o.rotation_euler = (math.pi / 2, 0, 0)
    o = rounded_slab(6.9, 15.0, 0.85, 0.05, (0, 0, 0), SCREEN, parent=m); o.rotation_euler = (math.pi / 2, 0, 0)
    o = rounded_slab(1.8, 0.45, 0.22, 0.03, (0, -0.05, 6.9), (0.02, 0.02, 0.03), parent=m); o.rotation_euler = (math.pi / 2, 0, 0)
    u = token("¿Plan para el finde?", USER, size=0.42, thick=0.05, parent=m, tcol=WHITE); u["e"].location = (2.7 - u["w"] / 2, -0.05, 5.4)
    o = rounded_slab(6.0, 1.0, 0.45, 0.05, (0, -0.05, -6.2), (0.2, 0.21, 0.25), parent=m); o.rotation_euler = (math.pi / 2, 0, 0)
    cyl(0.38, 0.06, (2.4, -0.12, -6.2), USER, parent=m, rot=(math.pi / 2, 0, 0))
    S["resp"] = [token(w, PAL[k % 6], size=0.55, thick=0.05, parent=m) for k, w in enumerate(RESP)]
    S["resp_pos"] = layout([d["w"] for d in S["resp"]], -2.7, 4.0, 5.4, gap=0.12, lh=1.05)
    S["cursor"] = box((0.14, 0.05, 0.75), LEJOS, WHITE, parent=m, unique=True)
    # ---------- escenario principal ----------
    S["prompt"] = [token(w, PAL[k % 6]) for k, w in enumerate(PROMPT)]
    S["dic"] = []
    rng = random.Random(5)
    for j in range(10):
        for i in range(12):
            S["dic"].append((box((0.46, 0.25, 0.46), LEJOS, PAL[rng.randrange(6)], unique=True), Vector((-3.6 + 0.6 * i, 0, 1.9 - 0.6 * j))))
    S["vec"] = []
    for k in range(len(PROMPT)):
        col = []
        for j in range(6):
            v = rng.uniform(-1, 1)
            col.append((box((1, 0.2, 0.26), LEJOS, (0.4, 0.65, 1.0) if v > 0 else (1.0, 0.45, 0.4), unique=True), v))
        S["vec"].append(col)
    # red: 4 capas de 5 nodos
    S["red"] = r = empty(LEJOS)
    S["nodos"] = []
    for li, x in enumerate((-3.8, -2.1, -0.4, 1.3)):
        for ni in range(5):
            S["nodos"].append(Vector((x, 0, -0.6 - 1.0 * ni)))
            sph(0.28, (x, 0, -0.6 - 1.0 * ni), NODE, parent=r, seg=16)
    S["cables"] = []
    for li in range(3):
        for a in range(5):
            for b in range(5):
                p0 = S["nodos"][li * 5 + a]; p1 = S["nodos"][(li + 1) * 5 + b]
                o = bar_obj(WIRE, 0.03, parent=r); bar_set(o, p0 + Vector((0, 0.05, 0)), p1 + Vector((0, 0.05, 0))); S["cables"].append((p0, p1))
    S["pulsos"] = [sph(0.13, LEJOS, PULSE, seg=8) for _ in range(18)]
    S["q"] = token("?", YEL, size=0.8)
    # contexto + trozos añadidos
    S["ctx"] = [token(w, PAL[k % 6]) for k, w in enumerate(CTX)]
    S["app"] = [token(w, PAL[(k + 4) % 6]) for k, w in enumerate(APP)]
    S["seq_pos"] = layout([d["w"] for d in S["ctx"] + S["app"]], -4.0, ROWZ, 7.4)
    # barras de probabilidad (3 filas, textos que cambian)
    S["bars"] = []
    for k in range(3):
        lab = text3d("x", LEJOS, 0.68, WHITE, extrude=0.01, rot=(math.pi / 2, 0, 0), align='RIGHT', unique=True); font(lab)
        bar = box((1, 0.3, 0.7), LEJOS, PAL[k * 2], unique=True)
        pct = text3d("0 %", LEJOS, 0.6, WHITE, extrude=0.01, rot=(math.pi / 2, 0, 0), align='LEFT', unique=True); font(pct)
        S["bars"].append((lab, bar, pct))
    S["aguja"] = empty(LEJOS)
    bpy.ops.mesh.primitive_cone_add(radius1=0.35, radius2=0, depth=0.8, location=(0, 0, 0), rotation=(0, math.pi / 2, 0), vertices=3)
    setup(bpy.context.object, YEL, parent=S["aguja"])
    # tres respuestas (robot / distintas)
    S["filas"] = []
    for f in range(3):
        base = [token(w, GREY) for w in CTX]
        fin = {w: token(" " + w, GREY) for w in VAR}
        S["filas"].append((base, fin))
    # dato falso
    S["fctx"] = [token(w, PAL[k % 6]) for k, w in enumerate(FAKE_CTX)]
    S["fake"] = token(FAKE[0][0], YEL)
    S["fake_pos"] = layout([d["w"] for d in S["fctx"]] + [S["fake"]["w"]], -4.0, ROWZ, 7.4)
    S["cruz"] = empty(LEJOS)
    for a in (45, -45): box((1.6, 0.1, 0.22), (0, 0, 0), RED, parent=S["cruz"], rot=(0, math.radians(a), 0))
    def toks(L): return [d["e"] for d in L]
    dyn = [cam, m, toks(S["prompt"]), [d for d, _ in S["dic"]], [b for c in S["vec"] for b, _ in c], r, S["pulsos"], S["q"]["e"],
           toks(S["ctx"]), toks(S["app"]), [x for b in S["bars"] for x in b], S["aguja"], toks(S["fctx"]), S["fake"]["e"], S["cruz"]]
    for base, fin in S["filas"]: dyn += toks(base) + toks(list(fin.values()))
    join_static(dyn)
    return sc, S

def put(d, p, s=1.0):
    d["e"].location = p if s > 0.01 else LEJOS; d["e"].scale = (s, s, s)

def pop(t, a, d=0.25):
    if t < a: return 0.0
    u = min(1, (t - a) / d); return u * (1 + 0.35 * math.sin(u * math.pi))

def recolor(d, c): set_color(d["s"], c)

def ciclos():
    """tiempos (inicio, elección) de cada vuelta del bucle"""
    a = T("por ejemplo"); el = T("elige una"); t1 = T("otra vez"); t2 = T("y otra"); t3 = T("trozo a trozo")
    out = [(a + 0.4, el + 0.35), (T("la pega", fin=True) + 0.9, t1 + 0.35), (t1 + 0.45, t2 + 0.3)]
    s = t2 + 0.4; dt = 0.55
    for k in range(4):
        out.append((s, s + dt * 0.75)); s += dt; dt *= 0.8
    return out

def pose(t, S):
    # ---------- móvil ----------
    t_esc, t_ves, t_cur = T("cómo escribe"), T("por eso ves"), T("y aquí viene")
    fase1 = t < t_esc + 1.6; fase2 = t_ves - 0.6 < t < t_cur + 0.6
    if fase1: S["movil"].location = (0, 0, -24 * seg(t, t_esc + 0.2, t_esc + 1.5))
    elif fase2: S["movil"].location = (0, -3.0, -26 * (1 - seg(t, t_ves - 0.6, t_ves + 0.1)) - 26 * seg(t, t_cur - 0.1, t_cur + 0.6))
    else: S["movil"].location = LEJOS
    t0 = -0.55 if fase1 else t_ves - 0.1; dk = 0.35 if fase1 else 0.17
    nmax = 7 if fase1 else len(RESP)
    for k, d in enumerate(S["resp"]):
        s = pop(t, t0 + dk * k) if k < nmax else 0.0
        if fase1 and k >= nmax: s = 0.0
        p = S["resp_pos"][k]; d["e"].location = (p.x, -0.06, p.z) if s > 0.01 else LEJOS; d["e"].scale = (s, s, s)
    # cursor parpadeando tras el último trozo
    nvis = max(1, min(nmax, sum(1 for k in range(nmax) if t >= t0 + dk * k)))
    last = S["resp_pos"][nvis - 1]; lw = S["resp"][nvis - 1]["w"]
    blink = (t * 2.2) % 1 < 0.6
    on_c = (fase1 and t > t0 + dk * (nmax - 1) + 0.2 and blink) or (fase2 and blink and t < t_ves + 2.2)
    S["cursor"].location = (last.x + lw / 2 + 0.2, -0.08, last.z) if on_c else LEJOS
    # ---------- pregunta troceada ----------
    t_tro, t_ent, t_tro2 = T("trocea"), T("a veces es"), T("a veces solo")
    t_dic, t_lis, t_red, t_adi = T("su diccionario"), T("cada trozo se"), T("una red"), T("adivinar")
    t_cal, t_ej = T("calcula"), T("por ejemplo")
    vis_p = T("primero") - 0.2 < t < t_ej - 0.2
    gap = 0.02 + 0.3 * seg(t, t_tro + 0.6, T("tokens"))
    ws = [d["w"] for d in S["prompt"]]; tot = sum(ws) + gap * (len(ws) - 1); x = -tot / 2 - 0.3
    zrow = ROWZ
    rise = 1 - seg(t, T("primero") - 0.2, T("primero") + 0.4)
    for k, d in enumerate(S["prompt"]):
        xc = x + ws[k] / 2; x += ws[k] + gap
        lift = 0.35 * (win01(t, t_ent + 0.6, t_tro2, 0.2, 0.2) if k == 3 or k == 4 else 0) + \
               0.35 * (win01(t, t_tro2 + 0.3, t_dic, 0.2, 0.2) if k <= 2 else 0)
        leave = seg(t, t_cal + 0.6, t_ej - 0.3)
        put(d, Vector((xc, 0, zrow + lift - 6 * rise + 8 * leave)), 1.0 if vis_p else 0)
        uni = seg(t, t_tro + 0.3, t_tro + 1.0)
        recolor(d, tuple(mix(a, b, uni) for a, b in zip(PAL[0], PAL[k % 6])))
    # diccionario: el estante se llena
    nd = len(S["dic"]); fill = seg(t, t_dic + 0.2, T("distintos", fin=True)) * nd
    gone = seg(t, t_lis - 0.3, t_lis + 0.4)
    for k, (o, p) in enumerate(S["dic"]):
        if k < fill and gone < 1:
            o.location = p + Vector((0, 0, -10 * gone * (0.5 + (k % 7) / 7))); s = min(1, (fill - k) / 6) * (1 - gone); o.scale = (0.46 * s, 0.25, 0.46 * s)
        else: o.location = LEJOS
    # columnas de números bajo cada trozo
    xs = []; x = -tot / 2 - 0.3
    for w in ws: xs.append(x + w / 2); x += w + gap
    into = seg(t, T("y con esos") + 0.1, t_red + 0.3)
    for k, col in enumerate(S["vec"]):
        for j, (o, v) in enumerate(col):
            a = t_lis + 0.6 + 0.12 * k + 0.08 * j
            if t > a and into < 1 and vis_p:
                s = min(1, (t - a) / 0.25); L = 0.25 + 0.75 * abs(v) * (0.8 + 0.2 * math.sin(t * 3 + j))
                p0 = Vector((xs[k], -0.1, ROWZ - 1.1 - 0.4 * j)); p1 = S["nodos"][j % 5] + Vector((0, -0.2, 0))
                o.location = p0.lerp(p1, into); o.scale = (L * s * (1 - into), 0.2, 0.26 * (1 - 0.5 * into))
            else: o.location = LEJOS
    # red, pulsos y el «?»
    red_on = t_red - 0.3 < t < t_ej - 0.2
    rs = seg(t, t_red - 0.3, t_red + 0.4) * (1 - seg(t, t_ej - 0.8, t_ej - 0.2))
    S["red"].location = (0, 0, 0) if rs > 0.01 else LEJOS; S["red"].scale = (1, 1, max(rs, 0.01))
    for k, pz in enumerate(S["pulsos"]):
        if red_on and rs > 0.9:
            u = (t * 0.9 + k / 18) % 1.0; li = min(2, int(u * 3)); fu = u * 3 - li
            rr = random.Random(k * 31 + int(t * 0.9 + k / 18)); a = rr.randrange(5); b = rr.randrange(5)
            p0 = S["nodos"][li * 5 + (a + li) % 5]; p1 = S["nodos"][(li + 1) * 5 + (b + li) % 5]
            pz.location = p0.lerp(p1, fu) + Vector((0, -0.15, 0))
        else: pz.location = LEJOS
    qs = pop(t, t_adi + 0.5, 0.3) * (1 - seg(t, t_ej - 0.6, t_ej - 0.2))
    wob = 0.3 * math.sin(t * 9) * win01(t, T("no sabe", 2), t_cal, 0.1, 0.2)
    put(S["q"], Vector((2.9 + wob, -0.1, -2.6)), qs)
    # ---------- barras de probabilidad y bucle ----------
    t_rob, t_aba, t_dist, t_inv = T("no siempre"), T("así que a veces"), T("y cada respuesta"), T("y por qué")
    C = ciclos(); seq = S["ctx"] + S["app"]; SP = S["seq_pos"]
    show_seq = t_ej - 0.3 < t < t_ves
    BZ = (0.0, -1.5, -3.0); BX = -0.4; BL = 3.2
    cands = None; grow = 0.0; pick = -1; hl = 0.0
    if t_ej < t < t_ves - 0.5:
        kc = 0
        for i, (a, b) in enumerate(C):
            if t >= a: kc = i
        a, b = C[kc]; cands = CICLOS[kc]
        if kc == 0:
            ks = [T("playa"), T("cama"), T("oficina")]
            grow = [seg(t, ks[i], ks[i] + 1.0) for i in range(3)]
        else:
            grow = [seg(t, a, a + (b - a) * 0.8)] * 3
        hl = seg(t, b - 0.25, b)
    elif t_cur + 0.4 < t < t_inv:
        cands = CICLOS[0]; grow = [seg(t, t_cur + 0.4, t_rob + 0.6)] * 3; hl = 0
    elif T("solo busca") - 0.2 < t < DUR + 1:
        cands = FAKE; grow = [seg(t, T("solo busca"), T("probable", 2, fin=True) + 0.3)] * 3; hl = seg(t, T("si un dato"), T("si un dato") + 0.4)
    for i, (lab, bar, pct) in enumerate(S["bars"]):
        if cands is None: lab.location = bar.location = pct.location = LEJOS; continue
        w, p = cands[i]; g = grow[i]
        lab.data.body = w.strip(); lab.location = (BX - 0.3, -0.15, BZ[i] - 0.2)
        L = max(0.02, BL * p / 70 * g); bar.location = (BX + L / 2, 0, BZ[i]); bar.scale = (L, 0.3, 0.7)
        pct.data.body = f"{int(round(p * g))} %"; pct.location = (BX + L + 0.25, -0.15, BZ[i] - 0.2)
        c = PAL[i * 2]
        if i == 0 and hl > 0: c = tuple(mix(a, b, hl * (0.6 + 0.4 * math.sin(t * 14))) for a, b in zip(c, (1, 1, 1)))
        set_color(bar, c)
    # frase que crece
    for k, d in enumerate(seq):
        if not show_seq: put(d, LEJOS, 0); continue
        if k < len(CTX):
            put(d, SP[k] + Vector((0, 0, 0)), pop(t, t_ej + 0.1 + 0.15 * k)); continue
        a, b = C[k - len(CTX)]
        if t < b: put(d, LEJOS, 0); continue
        u = seg(t, b, b + (0.45 if k - len(CTX) < 3 else 0.25))
        p0 = Vector((BX - 0.3 - d["w"] / 2, -0.4, BZ[0])); put(d, p0.lerp(SP[k], u) + Vector((0, -1.2 * math.sin(u * math.pi), 0)), 1.0)
    # aguja
    if t_cur + 0.4 < t < t_inv:
        zi = keyed(t, [(t_rob, BZ[0]), (t_aba + 0.6, BZ[0]), (T("de abajo") - 0.2, BZ[1]), (T("de abajo") + 0.6, BZ[2]), (t_dist + 0.3, BZ[2]), (t_dist + 0.8, BZ[0])])
        S["aguja"].location = (BX - 3.9 + 0.15 * math.sin(t * 8), -0.2, zi)
    elif cands is not None and hl > 0 and t < t_ves:
        S["aguja"].location = (BX - 3.9, -0.2, BZ[0])
    else: S["aguja"].location = LEJOS
    # tres respuestas: iguales (robot) y luego distintas
    t_hic = T("si lo hiciera")
    for f, (base, fin) in enumerate(S["filas"]):
        on = t_hic - 0.2 < t < t_inv - 0.1
        z = ROWZ - 1.15 * f
        ws2 = [d["w"] for d in base]
        if f == 0: cho = "playa"
        elif f == 1: cho = "cama" if t > T("de abajo") - 0.1 else "playa"
        else: cho = "oficina" if t > T("de abajo") + 0.6 else "playa"
        pos = layout(ws2 + [fin[cho]["w"]], -4.0, z, 12)
        s = pop(t, t_hic + 0.35 * f) if on else 0
        colorido = seg(t, t_dist - 0.2, t_dist + 0.4)
        for k, d in enumerate(base):
            put(d, pos[k], s); recolor(d, tuple(mix(a, b, colorido) for a, b in zip(GREY, PAL[k % 6])))
        for w, d in fin.items():
            if w == cho:
                put(d, pos[-1], s * (1 if f == 0 or t > T("de abajo") + 0.0 else 1))
                recolor(d, tuple(mix(a, b, max(colorido, 1.0 if w != "playa" else 0)) for a, b in zip(GREY, YEL)))
            else: put(d, LEJOS, 0)
    # dato falso
    t_fal, t_seg, t_comp = T("si un dato"), T("seguridad"), T("así que compruébalo")
    on = t_inv - 0.1 < t
    for k, d in enumerate(S["fctx"]): put(d, S["fake_pos"][k], pop(t, t_inv + 0.1 + 0.18 * k) if on else 0)
    fk = S["fake"]
    if t > t_fal + 0.3:
        u = seg(t, t_fal + 0.3, t_fal + 0.8)
        p0 = Vector((BX - 0.3 - fk["w"] / 2, -0.4, BZ[0])); put(fk, p0.lerp(S["fake_pos"][-1], u) + Vector((0, -1.2 * math.sin(u * math.pi), 0)),
                                                                 1.0 + 0.12 * win01(t, t_seg - 0.2, t_comp, 0.2, 0.3))
        recolor(fk, tuple(mix(a, b, seg(t, t_comp - 0.1, t_comp + 0.3)) for a, b in zip(YEL, RED)))
    else: put(fk, LEJOS, 0)
    cs = pop(t, t_comp + 0.2, 0.25)
    S["cruz"].location = S["fake_pos"][-1] + Vector((0, -0.6, 0)) if cs > 0.01 else LEJOS; S["cruz"].scale = (cs, cs, cs)
    apply_cam(S["cam"], *cam_state(t, CAM(), drift=0.12))

def V(at, off, lens=40): at = Vector(at); return (tuple(at + Vector(off)), tuple(at), lens)
def CAM():
    k = []
    def add(t, v): k.append((t,) + v)
    add(0.0, V((0, 0, 2.7), (0.6, -12.0, 0.8)))
    add(T("no sabe"), V((0, 0, 2.5), (-0.4, -13.0, 0.8)))
    add(T("cómo escribe") + 0.3, V((0, 0, 1.6), (-0.5, -16, 1.0)))
    add(T("primero") + 0.3, V((-0.3, 0, 1.4), (-1.6, -17.5, 1.5)))
    add(T("a veces solo"), V((-0.3, 0, 2.2), (1.0, -16, 1.2)))
    add(T("su diccionario") + 0.5, V((-0.3, 0, 0.6), (-1.3, -18, 1.5)))
    add(T("cada trozo se") + 1.0, V((-0.3, 0, 1.4), (1.0, -16.5, 1.0)))
    add(T("una red") + 0.5, V((-0.5, 0, -0.3), (-1.6, -17.8, 2.0)))
    add(T("calcula"), V((-0.2, 0, -0.5), (1.3, -17, 1.2)))
    add(T("por ejemplo") + 0.5, V((-0.3, 0, 0.9), (-1.3, -17.5, 1.5)))
    add(T("oficina") + 0.5, V((-0.3, 0, 0.7), (0.9, -16.8, 1.0)))
    add(T("trozo a trozo"), V((-0.3, 0, 0.9), (-1.0, -17.8, 1.5)))
    add(T("por eso ves") + 0.2, V((0, -3, 1.8), (0.0, -16.0, 1.0)))
    add(T("y aquí viene") + 0.4, V((0, -3, 1.5), (-0.3, -17, 1.0)))
    add(T("no siempre") + 0.3, V((-0.3, 0, 0.8), (-1.3, -17.5, 1.5)))
    add(T("y cada respuesta") + 0.5, V((-0.3, 0, 1.0), (1.0, -17.2, 1.2)))
    add(T("y por qué") + 0.5, V((-0.3, 0, 0.8), (-1.0, -17.5, 1.2)))
    add(T("si un dato"), V((-0.3, 0, 1.4), (0.4, -17.0, 1.0)))
    add(T("así que compruébalo"), V((-0.3, 0, 1.8), (0.0, -16.3, 1.0)))
    add(DUR + 2, V((-0.3, 0, 0.9), (-0.8, -18, 1.2)))
    return k

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    m = S["movil"].location
    cur = S["cursor"].location if S["cursor"].location.z > -100 else Vector((0, 0, 0))
    return {"cursor": Pj(Vector(m) + Vector(cur)), "prompt": Pj((0, 0, ROWZ + 0.8)), "vec": Pj((-0.3, 0, ROWZ - 3.6)), "dic": Pj((0, 0, 2.2)), "red": Pj((-1.25, 0, -0.1)),
            "q": Pj((3.7, 0, -1.7)), "bar0": Pj((-1.0, 0, 0.5)), "fila": Pj((0, 0, 5.1)), "fake": Pj(S["fake_pos"][-1] + Vector((0, 0, 0.6))),
            "aguja": Pj((-5.2, 0, -1.2))}

if __name__ == "__main__":
    run("chatgpt", build, pose, anchors)
