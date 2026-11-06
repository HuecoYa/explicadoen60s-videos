# «Si tuvieras que inventar WhatsApp…»: un pulgar pulsa enviar y el mensaje vuela de tu móvil al servidor y al de tu amigo;
# riada de mensajes; candado y llave (el texto se convierte en letras sin sentido); la llave enviada se puede copiar; cada
# móvil crea una llave pública (va al servidor, la ve todo el mundo) y una privada (se queda dentro); cada móvil mezcla su
# privada con la pública del otro y sale el mismo número; el servidor solo ve basura; el número de 78 cifras; un ladrón
# roba una llave y abre lo anterior… hasta que la llave cambia con cada mensaje; el servidor sigue viendo quién y cuándo.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("whatsapp")
BG = (0.07, 0.08, 0.11); BODY = (0.2, 0.22, 0.27); SCREEN = (0.1, 0.13, 0.2); GREEN = (0.25, 0.8, 0.45); BUB = (0.88, 0.96, 0.9)
INK = (0.08, 0.1, 0.12); SRV = (0.26, 0.28, 0.34); LED = (0.3, 0.95, 0.5); GOLD = (1.0, 0.78, 0.25); PUB = (0.3, 0.75, 1.0)
PRIV = (0.75, 0.4, 1.0); RED = (0.95, 0.28, 0.28); SKIN = (0.93, 0.7, 0.58); GLOVE = (0.15, 0.15, 0.17); WHITE = (0.95, 0.95, 0.97)
LEJOS = (0, 60, -300)
FONT = os.path.expanduser("~/.fonts/Poppins-Bold.ttf")
PZ = -0.2; AX, BX = -3.0, 3.0
A_TOP = Vector((AX, -0.6, 4.3)); B_TOP = Vector((BX, -0.6, 4.3)); SRVP = Vector((0, -1.4, 5.0))
SC = Vector((0, 1.0, 5.0))       # centro del servidor
GIB = ["X#7QK!P", "9$ZW@L", "Q&8RT%", "#M4!VX", "K@2$PZ", "7!QX#R"]
MSGS = ["HOLA", "¿CENAMOS?", "VALE", "A LAS 9"]
rng0 = random.Random(78); BIG = "".join(str(rng0.randint(1 if i == 0 else 0, 9)) for i in range(78))

def font(o):
    if os.path.exists(FONT):
        try: o.data.font = bpy.data.fonts.load(FONT, check_existing=True)
        except Exception: pass

def txt(s, loc, size, col, parent=None, align='CENTER'):
    o = text3d(s, loc, size, col, parent=parent, extrude=0.01, rot=(math.pi / 2, 0, 0), align=align, unique=True); font(o); return o

def bubble(text, w=1.9, h=0.75, col=BUB, tcol=INK, size=0.34):
    e = empty(LEJOS)
    s = rounded_slab(w, h, 0.25, 0.2, (0, 0.1, 0), col, parent=e, unique=True); s.rotation_euler = (math.pi / 2, 0, 0)
    t = txt(text, (0, -0.12, -size * 0.35), size, tcol, parent=e)
    return {"e": e, "s": s, "t": t}

def key3d(col, label=None):
    e = empty(LEJOS)
    torus(0.48, 0.13, (-0.8, 0, 0), col, parent=e, rot=(math.pi / 2, 0, 0))
    box((1.5, 0.18, 0.21), (0.3, 0, 0), col, parent=e)
    for x in (0.68, 0.93): box((0.13, 0.18, 0.36), (x, 0, -0.24), col, parent=e)
    lab = txt(label, (-0.8, -0.2, 0.7), 0.42, WHITE, parent=e) if label is not None else None
    return {"e": e, "lab": lab}

def padlock(col):
    e = empty(LEJOS)
    b = rounded_slab(0.87, 0.7, 0.14, 0.36, (0, 0.18, 0), col, parent=e, unique=True); b.rotation_euler = (math.pi / 2, 0, 0)
    sh = torus(0.28, 0.077, (0, 0, 0.42), (0.75, 0.77, 0.8), parent=e, rot=(math.pi / 2, 0, 0))
    cyl(0.085, 0.17, (0, -0.2, -0.03), INK, parent=e, rot=(math.pi / 2, 0, 0), v=12)
    return {"e": e, "sh": sh, "b": b}

def phone(x):
    e = empty((x, 0, PZ)); e.rotation_euler = (math.pi / 2, 0, 0)
    rounded_slab(3.4, 7.0, 0.5, 0.4, (0, 0, -0.4), BODY, parent=e)
    rounded_slab(3.2, 6.8, 0.42, 0.03, (0, 0, 0.0), SCREEN, parent=e)
    return e

def build():
    sc, cam = scene_setup(world=BG, shadow=0.35)
    S = {"cam": cam}
    rng = random.Random(5)
    box((60, 0.2, 60), (0, 4, 0), (0.1, 0.11, 0.15))
    # móviles con conversación en pantalla
    S["pa"] = phone(AX); S["pb"] = phone(BX)
    for e, side in ((S["pa"], 1), (S["pb"], -1)):
        for k, (w, y) in enumerate(((1.8, 2.2), (1.4, 1.3), (2.0, 0.4))):
            c = GREEN if (k + (side < 0)) % 2 == 0 else (0.3, 0.33, 0.4)
            xx = side * (0.55 if c == GREEN else -0.45) * (1 if side > 0 else -1)
            rounded_slab(w, 0.6, 0.2, 0.02, (xx, y, 0.04), c, parent=e)
        rounded_slab(2.4, 0.55, 0.25, 0.02, (-0.35, -2.9, 0.04), (0.25, 0.28, 0.34), parent=e)
    S["send"] = cyl(0.36, 0.06, (AX + 1.15, -0.06, PZ - 2.9), GREEN, rot=(math.pi / 2, 0, 0), unique=True)
    # servidor
    box((2.8, 2.0, 2.6), SC, SRV)
    for r in range(3): box((2.4, 0.05, 0.12), SC + Vector((0, -1.02, 0.85 - 0.35 * r)), (0.18, 0.19, 0.23))
    S["leds"] = [sph(0.06, SC + Vector((-1.05 + 0.18 * k, -1.04, 0.85 - 0.35 * (k % 3))), LED, seg=8, unique=True) for k in range(12)]
    box((2.2, 0.04, 0.9), SC + Vector((0, -1.02, -0.6)), (0.05, 0.07, 0.1))
    S["log1"] = txt(" ", SC + Vector((0, -1.06, -0.45)), 0.24, GREEN); S["log2"] = txt(" ", SC + Vector((0, -1.06, -0.82)), 0.24, GREEN)
    # mensaje principal, candado, llaves
    S["msg"] = bubble("HOLA", w=2.5, h=0.95, size=0.44)
    S["lock"] = padlock(GOLD)
    S["kshare"] = key3d(GOLD, "4821"); S["kcopy"] = key3d(RED, "4821")
    S["pubA"] = key3d(PUB); S["privA"] = key3d(PRIV); S["pubB"] = key3d(PUB); S["privB"] = key3d(PRIV)
    S["pubA2"] = key3d(PUB); S["pubB2"] = key3d(PUB)
    S["mixA"] = sph(0.42, LEJOS, GOLD, unique=True); S["mixB"] = sph(0.42, LEJOS, GOLD, unique=True)
    S["numA"] = txt("58204", LEJOS, 0.8, GOLD); S["numB"] = txt("58204", LEJOS, 0.8, GOLD)
    # riada de mensajes
    S["swarm"] = [bubble("", w=0.8, h=0.36) for _ in range(14)]
    S["swp"] = [(rng.uniform(-6, 6), rng.uniform(0, 1)) for _ in range(14)]
    # mensajes viejos guardados en el servidor
    S["old"] = [bubble(GIB[k], w=2.6, h=0.8, size=0.38) for k in range(4)]
    # número de 78 cifras
    S["big"] = txt(" ", LEJOS, 0.42, WHITE)
    S["bigbg"] = rounded_slab(7.6, 2.4, 0.4, 0.1, LEJOS, (0.13, 0.15, 0.2), unique=True); S["bigbg"].rotation_euler = (math.pi / 2, 0, 0)
    # pulgar y guante del ladrón
    S["thumb"] = th = empty(LEJOS)
    d = Vector((0.55, -0.35, -0.75)).normalized()
    sph(0.5, (0, 0, 0), SKIN, parent=th)
    o = cyl(0.5, 5, d * 2.5, SKIN, parent=th); o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d)
    n = sph(0.34, (-0.05, -0.32, 0.12), (0.97, 0.82, 0.78), parent=th, scale=(1, 0.3, 1.2))
    S["glove"] = gl = empty(LEJOS)
    sph(0.55, (0, 0, 0), GLOVE, parent=gl, scale=(1, 0.6, 1.1))
    for k in range(4): cyl(0.13, 0.7, (-0.36 + 0.24 * k, 0, -0.75), GLOVE, parent=gl)
    cyl(0.45, 3, (0, 0, 2.0), (0.25, 0.1, 0.1), parent=gl)
    dyn = [cam, S["send"], S["leds"], S["log1"], S["log2"], S["msg"]["e"], S["lock"]["e"], S["mixA"], S["mixB"], S["numA"], S["numB"],
           S["big"], S["bigbg"], S["thumb"], S["glove"]]
    for k in ("kshare", "kcopy", "pubA", "privA", "pubB", "privB", "pubA2", "pubB2"): dyn.append(S[k]["e"])
    dyn += [b["e"] for b in S["swarm"]] + [b["e"] for b in S["old"]]
    join_static(dyn)
    return sc, S

def quad(p0, c, p1, u):
    u = max(0.0, min(1.0, u)); return p0 * (1 - u) ** 2 + c * 2 * u * (1 - u) + p1 * u * u

def path(u):
    """A → servidor → B, u en 0..1"""
    if u < 0.5: return quad(A_TOP, Vector((-2.4, -1.0, 5.6)), SRVP, u * 2)
    return quad(SRVP, Vector((2.4, -1.0, 5.6)), B_TOP, u * 2 - 1)

def K():
    return dict(nadie=T("cómo harías"), cien=T("cada día"), todos=T("y todos pasan"), cand=T("un candado"), antes=T("antes de salir"),
                mezcla=T("el mensaje se mezcla"), llave=T("la llave"), sale=T("sale convertido"), prob=T("pero hay un problema"),
                amigo=T("tu amigo necesita"), mandas=T("y si se la mandas"), copiar=T("alguien podría"), dos=T("así que cada móvil"),
                pub=T("una pública"), todo=T("que puede ver"), priv=T("y una privada"), nunca=T("que nunca sale"),
                mixa=T("tu móvil mezcla"), mixb=T("su móvil hace"), mismo=T("y los dos llegan"), sin=T("sin habérselo"),
                srv=T("y el servidor"), solo=T("solo ve pasar"), ninguna=T("no tiene ninguna"), curioso=T("y aquí viene"),
                n78=T("esa llave es"), prob2=T("probando millones"), univ=T("tardarías"), falta=T("pero aún falta"),
                robara=T("si un día alguien"), leer=T("podría leer"), cambia=T("así que la llave cambia"), cada=T("cada mensaje tiene"),
                eso=T("eso sí"), quien=T("el servidor sigue"), sig=T("sígueme"))

def put(o, p, s=1.0):
    o.location = p; o.scale = (s, s, s)

def hide(o): o.location = LEJOS

def scramble(t, base, k=0):
    r = random.Random(int(t * 12) + k * 101); return "".join(r.choice("#$%&@!?QXZKW7948") for _ in base)

def pose(t, S):
    k = K()
    # pulgar pulsa enviar (2 veces) al principio
    pr = abs(math.sin(math.pi * (t + 0.2) / 0.55)) if t < 0.9 else 0.0
    if t < 2.2:
        btn = Vector((AX + 1.15, -0.06, PZ - 2.9))
        S["thumb"].location = btn + Vector((0, -0.42 - 0.9 * (1 - pr), 0.1)) + Vector((0.55, -0.35, -0.75)) * 7 * seg(t, 0.9, 2.0)
    else: hide(S["thumb"])
    S["send"].scale = (1 - 0.25 * pr, 1, 1 - 0.25 * pr)
    # LEDs del servidor
    busy = k["cien"] < t < k["cand"] or k["srv"] < t < k["curioso"] or t > k["eso"] or 1.0 < t < 4.5
    for i, o in enumerate(S["leds"]):
        on = busy and math.sin(t * 17 + i * 2.3) > 0 or (i % 4 == 0)
        set_color(o, LED if on else (0.1, 0.25, 0.15))
    # ---- mensaje principal ----
    m = S["msg"]
    if t < k["cien"]:                              # HOLA viaja de A a B, legible
        u = seg(t, 0.45, k["nadie"] + 1.5)
        put(m["e"], path(u) if u > 0 else A_TOP + Vector((0, 0, -1.5)), 0.4 + 0.6 * seg(t, 0.4, 0.8))
        m["t"].data.body = "HOLA"; set_color(m["s"], BUB)
    elif t < k["cand"] - 0.3: hide(m["e"])
    elif t < k["sale"] + 1.0:                      # encima de tu móvil, se mezcla con la llave
        put(m["e"], A_TOP + Vector((0, 0, -1.6)), 1.25)
        if t > k["mezcla"] + 1.2: m["t"].data.body = scramble(t, "HOLAXYZ")
        else: m["t"].data.body = "HOLA"
        set_color(m["s"], BUB)
    elif t < k["mandas"]:                          # cifrado viaja hasta B
        u = seg(t, k["sale"] + 1.0, k["amigo"])
        put(m["e"], path(u) + Vector((0, 0, -1.6)) * (1 - seg(u, 0, 0.2)), 1.25 - 0.35 * seg(u, 0, 0.3))
        m["t"].data.body = GIB[0]
    elif k["solo"] - 0.6 < t < k["curioso"]:       # el servidor solo ve basura
        u = ((t - k["solo"] + 0.6) / 2.6) % 1.0
        put(m["e"], path(u), 0.9); m["t"].data.body = GIB[int(t * 2) % len(GIB)]
    elif k["cambia"] < t < k["eso"]:               # cada mensaje con su candado
        u = ((t - k["cambia"]) / 1.3) % 1.0
        put(m["e"], path(u), 0.9); m["t"].data.body = GIB[int((t - k["cambia"]) / 1.3) % len(GIB)]
    elif t > k["eso"]:
        u = ((t - k["eso"]) / 2.2) % 1.0
        put(m["e"], path(u), 0.9); m["t"].data.body = GIB[(int((t - k["eso"]) / 2.2) + 3) % len(GIB)]
    else: hide(m["e"])
    # candado sobre el mensaje
    L = S["lock"]
    lk_on = k["cand"] - 0.2 < t < k["mandas"] or k["solo"] - 0.6 < t < k["curioso"] or t > k["cambia"]
    if lk_on:
        drop = seg(t, k["cand"] - 0.2, k["cand"] + 0.4)
        put(L["e"], m["e"].location + Vector((1.25 * m["e"].scale.x, -0.25, 0.35 + 2.5 * (1 - drop))), m["e"].scale.x)
        closed = seg(t, k["sale"], k["sale"] + 0.4) if t < k["mandas"] else 1.0
        L["sh"].location = (0, 0, 0.59 - 0.17 * closed)
        col = GOLD
        if t > k["cambia"]: col = (GOLD, PUB, GREEN, RED, PRIV)[int((t - k["cambia"]) / 1.3) % 5]
        set_color(L["b"], col)
    else: hide(L["e"])
    # llave compartida (4821): se mezcla, viaja y la copian
    ks, kc = S["kshare"], S["kcopy"]
    if k["mezcla"] - 0.3 < t < k["sale"] + 0.3:
        u = seg(t, k["mezcla"] + 0.2, k["mezcla"] + 1.3)
        tgt = A_TOP + Vector((0, -0.3, -1.6))
        put(ks["e"], Vector((AX - 1.8, -1.0, 0.5)).lerp(tgt, u), 1.2 * (1 - 0.8 * u) * seg(t, k["mezcla"] - 0.3, k["mezcla"] + 0.1))
    elif k["mandas"] - 0.3 < t < k["dos"]:
        u = seg(t, k["mandas"], k["copiar"] + 0.6)
        put(ks["e"], path(u) + Vector((0, -0.2, 0.0)), 1.1)
    else: hide(ks["e"])
    if k["mandas"] + 0.7 < t < k["dos"]:
        u = seg(t, k["mandas"] + 0.7, k["copiar"] + 0.8)
        put(kc["e"], path(min(u, 0.5) if u < 0.5 else 0.5) + Vector((0, -0.4, 0.0)) + Vector((-1.5, -0.6, 2.2)) * max(0, (u - 0.45) / 0.55), 1.1)
    else: hide(kc["e"])
    # llaves pública y privada
    born = seg(t, k["dos"] + 0.3, k["dos"] + 1.0)
    up = seg(t, k["pub"], k["pub"] + 1.0); down = seg(t, k["priv"], k["priv"] + 1.0)
    end_keys = k["n78"]
    for side, X, pubk, privk in (("A", AX, S["pubA"], S["privA"]), ("B", BX, S["pubB"], S["privB"])):
        sgn = -1 if side == "A" else 1
        if k["dos"] < t < end_keys:
            p0 = Vector((X - 0.9, -1.2, 4.6)); p1 = SC + Vector((sgn * 2.05, -1.2, 0.1))
            put(pubk["e"], p0.lerp(p1, up), born * (1 - 0.15 * up)); pubk["e"].rotation_euler = (0, math.pi / 2 * up, 0)
            q0 = Vector((X + 0.9, -1.2, 4.6)); q1 = Vector((X, -0.6, PZ + 1.3))
            mixing = k["mixa"] if side == "A" else k["mixb"]
            pm = seg(t, mixing + 0.2, mixing + 1.4)
            q = q0.lerp(q1, down).lerp(Vector((X, -1.4, 4.4)), pm)
            put(privk["e"], q, born * (1 - 0.6 * seg(t, mixing + 1.0, mixing + 1.6)))
            if t > mixing + 1.6: hide(privk["e"])
        else: hide(pubk["e"]); hide(privk["e"])
    # copias de las públicas que bajan al otro móvil para mezclar
    for side, kk, mixing, X, srcsgn in (("A", S["pubB2"], k["mixa"], AX, 1), ("B", S["pubA2"], k["mixb"], BX, -1)):
        if mixing - 0.1 < t < mixing + 1.6:
            u = seg(t, mixing, mixing + 1.4)
            put(kk["e"], (SC + Vector((srcsgn * 2.05, -1.2, 0.1))).lerp(Vector((X, -1.4, 4.4)), u), 1.0 - 0.6 * seg(t, mixing + 1.0, mixing + 1.6))
        else: hide(kk["e"])
    for side, ball, num, mixing, X in (("A", S["mixA"], S["numA"], k["mixa"], AX), ("B", S["mixB"], S["numB"], k["mixb"], BX)):
        g = seg(t, mixing + 1.1, mixing + 1.6)
        if mixing + 1.1 < t < k["n78"]:
            pulse = 1 + 0.12 * math.sin(t * 9)
            put(ball, Vector((X, -1.4, 4.4)), (0.4 + 0.6 * g) * pulse * (1 - seg(t, mixing + 1.8, mixing + 2.3)) + 0.001)
            put(num, Vector((X, -1.6, 4.25)), seg(t, mixing + 1.8, mixing + 2.2) + 0.001)
        elif t > k["robara"] - 0.5 and t < k["eso"] and side == "A":
            put(ball, LEJOS)
            put(num, Vector((X, -1.6, 4.25)), 1.0)
        else: hide(ball); hide(num)
    # número de 78 cifras
    if k["n78"] - 0.2 < t < k["falta"]:
        a = seg(t, k["n78"] - 0.2, k["n78"] + 0.4)
        n = int(78 * seg(t, k["n78"], k["n78"] + 1.4))
        s = BIG[:n]
        if t > k["prob2"]:          # pruebas: las últimas cifras giran sin parar
            r = random.Random(int(t * 15)); s = BIG[:60] + "".join(str(r.randint(0, 9)) for _ in range(18))
        S["big"].data.body = "\n".join(s[i:i + 26] for i in range(0, max(len(s), 1), 26)) or " "
        S["big"].data.align_y = 'TOP'
        put(S["big"], Vector((0, -2.6, 3.1)), a); put(S["bigbg"], Vector((0, -2.45, 2.25)), a)
    else: hide(S["big"]); hide(S["bigbg"])
    # riada de mensajes hacia el servidor
    for i, (b, (x0, ph)) in enumerate(zip(S["swarm"], S["swp"])):
        if k["cien"] - 0.2 < t < k["cand"] - 0.3:
            u = ((t * 0.8 + ph) % 1.0); src = Vector((x0, -1.5, -4.5)); dst = SRVP + Vector((0.6 * math.sin(i), 0, 0))
            put(b["e"], quad(src, Vector((x0 * 0.6, -1.5, 3.0)), dst, u), 0.9 * (1 - 0.4 * u))
        else: hide(b["e"])
    # mensajes viejos en el servidor: el ladrón los abre; luego la llave cambia y ya no puede
    for i, b in enumerate(S["old"]):
        if k["robara"] - 0.3 < t < k["eso"]:
            put(b["e"], Vector((0, -1.6, 9.7 - 1.0 * i)), 0.85 * seg(t, k["robara"] - 0.3 + 0.1 * i, k["robara"] + 0.1 * i))
            open_ = seg(t, k["leer"] + 0.2 * i, k["leer"] + 0.2 * i + 0.3) * (1 - seg(t, k["cambia"] + 0.4 * i, k["cambia"] + 0.4 * i + 0.3))
            if i == 0 and t > k["cambia"]: open_ = 1.0       # solo el de su propia llave
            b["t"].data.body = MSGS[i] if open_ > 0.5 else GIB[i]
            set_color(b["s"], (0.7, 1.0, 0.75) if open_ > 0.5 else BUB)
        else: hide(b["e"])
    # guante del ladrón: coge la llave (58204) y la lleva a los mensajes viejos
    gl = S["glove"]
    if k["robara"] - 0.2 < t < k["cambia"] + 1.0:
        p_key = Vector((AX, -1.6, 4.4)); p_old = Vector((2.4, -1.8, 9.0))
        u1 = seg(t, k["robara"] - 0.2, k["robara"] + 0.6); u2 = seg(t, k["robara"] + 0.8, k["leer"] + 0.1)
        p = Vector((AX - 3, -2.5, 9)).lerp(p_key + Vector((0, -0.3, 0.9)), u1).lerp(p_old + Vector((0, -0.3, 0.9)), u2)
        put(gl, p + Vector((0, 0, 6 * seg(t, k["cambia"] + 0.2, k["cambia"] + 1.0))), 1.4)
        if u2 > 0: put(S["numA"], p + Vector((0, -0.2, -1.1)), 1.0)
    else: hide(gl)
    if k["cambia"] < t < k["eso"]:
        i = int((t - k["cambia"]) / 1.3); put(S["numA"], Vector((AX, -1.6, 4.25)), 1.0)
        S["numA"].data.body = ("58204", "91736", "30418", "77251", "16093", "48620")[i % 6]
    else: S["numA"].data.body = "58204"
    # registro del servidor: quién y cuándo
    if t > k["quien"] + 0.3:
        S["log1"].data.body = "TÚ → AMIGO"; S["log2"].data.body = "21:4%d" % (3 + int(max(0, t - k["quien"]) / 1.5) % 6)
    else: S["log1"].data.body = " "; S["log2"].data.body = " "
    apply_cam(S["cam"], *cam_state(t, CAM(k), drift=0.04))

def V_(at, off, lens=38):
    return (tuple(Vector(at) + Vector(off)), tuple(at), lens)

def CAM(k):
    c = []
    def add(t, v): c.append((t,) + v)
    W0 = (0.3, 0, 2.7)                         # plano general
    add(0.0, V_((AX + 0.9, 0, PZ - 2.0), (1.2, -6.5, 0.6), 38))
    add(0.8, V_((AX + 0.5, 0, 0.5), (1.5, -9.5, 1.0), 38))
    add(2.2, V_(W0, (0.5, -19, 2.5), 38))
    add(k["cien"], V_(W0, (0, -19.5, 2.0), 38))
    add(k["todos"] + 0.5, V_((0, 0, 3.5), (0, -14, 1.5), 38))
    add(k["cand"], V_((AX + 0.8, 0, 2.6), (1.5, -12, 1.5), 38))
    add(k["llave"], V_((AX + 0.6, 0, 2.6), (2.5, -11, 1.0), 38))
    add(k["sale"] + 1.0, V_((AX + 0.8, 0, 2.6), (1.5, -12, 1.2), 38))
    add(k["prob"] + 0.6, V_(W0, (0.5, -19, 2.0), 38))
    add(k["copiar"], V_((0, 0, 2.5), (-1, -18, 2.0), 38))
    add(k["dos"] + 0.6, V_(W0, (0.5, -19, 2.0), 38))
    add(k["mixa"], V_((AX + 1.2, 0, 3.3), (1.0, -15, 1.6), 38))
    add(k["mixb"] + 0.3, V_((BX - 1.2, 0, 3.3), (-1.0, -15, 1.6), 38))
    add(k["mismo"] + 0.3, V_(W0, (0.0, -18, 2.0), 38))
    add(k["srv"], V_((0, 0, 4.0), (0.3, -16, 1.0), 38))
    add(k["ninguna"] + 0.5, V_((0, 0, 3.8), (-0.3, -15, 1.0), 38))
    add(k["n78"], V_((0.3, 0, 2.6), (0, -14.5, 1.0), 38))
    add(k["falta"], V_((0.3, 0, 2.6), (0, -15, 1.0), 38))
    add(k["robara"] + 0.8, V_((0, 0, 6.0), (0.5, -19, 2.0), 38))
    add(k["cambia"] + 1.0, V_((0, 0, 6.0), (-0.5, -19, 2.0), 38))
    add(k["quien"], V_((0, 0, 4.4), (0.4, -14, 0.8), 38))
    add(k["sig"], V_(W0, (0, -19.5, 2.0), 38))
    add(DUR + 2, V_(W0, (0, -21, 2.0), 38))
    return c

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    return {"pa": Pj((AX, -0.3, PZ + 1.0)), "pb": Pj((BX, -0.3, PZ + 1.0)), "srv": Pj(SC + Vector((0, -1.0, 1.4))),
            "msg": Pj(S["msg"]["e"].location), "lock": Pj(S["lock"]["e"].location), "ks": Pj(S["kshare"]["e"].location),
            "kc": Pj(S["kcopy"]["e"].location), "pubA": Pj(S["pubA"]["e"].location), "privA": Pj(S["privA"]["e"].location),
            "pubB": Pj(S["pubB"]["e"].location), "privB": Pj(S["privB"]["e"].location), "numA": Pj(Vector((AX, -1.6, 4.3))),
            "numB": Pj(Vector((BX, -1.6, 4.3))), "big": Pj(Vector((0, -2.6, 3.3))), "old": Pj(Vector((0, -1.6, 9.0)))}

if __name__ == "__main__":
    run("whatsapp", build, pose, anchors)
