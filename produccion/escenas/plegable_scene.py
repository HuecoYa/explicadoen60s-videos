# «Así funciona una pantalla plegable»: el móvil plegable abriéndose en primer plano; un cristal grueso se dobla en corte
# (tracción fuera, compresión dentro) y se agrieta; se adelgaza hasta 30 micras junto a un pelo de 70; baño de sales
# calientes; los iones pequeños se cambian por otros grandes que aprietan la superficie y cierran la grieta; capas
# pantalla + cristal + plástico que se doblan juntas; bisagra en corte: pliegue en ángulo recto que se parte frente a
# pliegue en gota; máquina de pruebas abriendo y cerrando el móvil; marca en el centro.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("plegable")
BG = (0.07, 0.08, 0.11); BODY = (0.2, 0.21, 0.25); SCR = (0.12, 0.3, 0.62); HINGE = (0.32, 0.33, 0.37)
GLS = (0.6, 0.86, 0.97); RED = (0.95, 0.22, 0.2); BLUE = (0.25, 0.55, 1.0); HAIR = (0.35, 0.2, 0.1)
NA = (1.0, 0.85, 0.3); K = (0.68, 0.42, 0.98); NET = (0.55, 0.62, 0.7); SALT = (1.0, 0.55, 0.18); STRIP = (0.3, 0.62, 1.0)
LEJOS = (0, 0, -900)
LB = 30.0                         # longitud del cristal en corte
ICON = [(0.95, 0.4, 0.35), (0.35, 0.8, 0.45), (1.0, 0.8, 0.3), (0.55, 0.45, 0.95), (0.3, 0.75, 0.95), (0.95, 0.55, 0.8)]


def alpha(o, a):
    for m in o.data.materials:
        m.diffuse_color = (*m.diffuse_color[:3], a); m.surface_render_method = 'BLENDED'


def arrow(color):
    e = empty(LEJOS)
    cyl(0.5, 0.72, (0.36, 0, 0), color, parent=e, rot=(0, math.pi / 2, 0), v=16)
    bpy.ops.mesh.primitive_cone_add(radius1=1.15, radius2=0, depth=0.32, location=(0.86, 0, 0), rotation=(0, math.pi / 2, 0), vertices=16)
    setup(bpy.context.object, color, e, True)
    return e


def set_arrow(a, p, ang, L, w=0.5):
    a.location = p; a.rotation_euler = (0, -ang, 0); a.scale = (max(L, 0.01), w, w)


def chain(n, color, unique=False): return [box((1, 1, 1), LEJOS, color, unique=unique) for _ in range(n)]


def hide(objs):
    for o in objs: o.location = LEJOS


def resample(pts, n):
    d = [0.0]
    for a, b in zip(pts, pts[1:]): d.append(d[-1] + math.dist(a, b))
    tot = d[-1]; out = []; j = 0
    for i in range(n + 1):
        s = tot * i / n
        while j < len(pts) - 2 and d[j + 1] < s: j += 1
        u = (s - d[j]) / max(d[j + 1] - d[j], 1e-9)
        out.append((mix(pts[j][0], pts[j + 1][0], u), mix(pts[j][1], pts[j + 1][1], u)))
    return out


def chain_set(objs, pts, th, depth, y=0.0, gap_at=None):
    q = resample(pts, len(objs))
    for k, o in enumerate(objs):
        (x0, z0), (x1, z1) = q[k], q[k + 1]
        L = math.hypot(x1 - x0, z1 - z0)
        o.location = ((x0 + x1) / 2, y, (z0 + z1) / 2); o.rotation_euler = (0, -math.atan2(z1 - z0, x1 - x0), 0)
        o.scale = (L * 1.12, depth, th)


def rotY(p, b):  # rotación alrededor de Y en el plano xz (igual que Blender)
    x, z = p; return (x * math.cos(b) + z * math.sin(b), -x * math.sin(b) + z * math.cos(b))


def bezier(p0, p1, p2, p3, n=40):
    out = []
    for i in range(n + 1):
        u = i / n; a, b, c, d = (1 - u) ** 3, 3 * u * (1 - u) ** 2, 3 * u * u * (1 - u), u ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def fold_pts(psi, x0, L, g, hx, hz):
    """pantalla en la bisagra: cara interior de la mitad de abajo -> curva -> cara interior de la de arriba"""
    bb, bt = psi / 2, -psi / 2; zi = g / 2 - 0.35
    bot = lambda x: rotY((x, -zi), bb); top = lambda x: rotY((x, zi), bt)
    P0, P3 = bot(x0), top(x0)
    d0 = rotY((-hx, -hz), bb); d3 = rotY((-hx, hz), bt)
    P1 = (P0[0] + d0[0], P0[1] + d0[1]); P2 = (P3[0] + d3[0], P3[1] + d3[1])
    pts = [bot(x0 + L - 1 - i * (L - 1) / 6) for i in range(7)][:-1] + bezier(P0, P1, P2, P3) + [top(x0 + i * (L - 1) / 6) for i in range(1, 7)]
    return pts


def build():
    sc, cam = scene_setup(world=BG, shadow=0.35)
    S = {"cam": cam}
    # ---------- móvil plegable (mm) ----------
    S["movil"] = empty((0, 0, 0)); S["mL"] = empty((0, 0, 0), S["movil"]); S["mR"] = empty((0, 0, 0), S["movil"])
    for e, sx in ((S["mL"], -1), (S["mR"], 1)):
        rounded_slab(70, 150, 7, 5, (sx * 36, 0, -5.6), BODY, parent=e)
        rounded_slab(68, 146, 6, 0.5, (sx * 36, 0, -0.6), SCR, parent=e)
        for i in range(3):
            for j in range(5):
                box((10, 10, 0.3), (sx * (14 + 18 * i), 48 - 22 * j, 0.0), ICON[(i + 2 * j + (sx > 0)) % 6], parent=e)
    cyl(2.6, 146, (0, 0, -3.2), HINGE, parent=S["movil"], rot=(math.pi / 2, 0, 0))
    S["marca"] = box((1.2, 140, 0.12), LEJOS, SCR, unique=True)
    S["pelo"] = cyl(0.8, 90, LEJOS, HAIR, rot=(0, math.pi / 2, 0))
    # máquina de pruebas
    S["maq"] = empty(LEJOS)
    box((90, 170, 14), (-40, 0, -14), (0.35, 0.37, 0.42), parent=S["maq"])
    box((6, 170, 8), (-80, 0, -3), (0.95, 0.6, 0.2), parent=S["maq"])
    S["pinza"] = empty(LEJOS)
    box((8, 40, 12), (0, 0, 0), (0.95, 0.6, 0.2), parent=S["pinza"])
    cyl(2, 60, (0, 0, 30), (0.6, 0.62, 0.66), parent=S["pinza"])
    # ---------- cristal en corte ----------
    S["vid"] = chain(40, GLS, unique=True)
    S["fuera"] = [arrow(RED) for _ in range(2)]; S["dentro"] = [arrow(BLUE) for _ in range(2)]
    S["grieta"] = box((1, 1, 1), LEJOS, (0.15, 0.05, 0.05))
    S["pelo2"] = cyl(0.35, 14, LEJOS, HAIR, rot=(math.pi / 2, 0, 0))
    # baño de sales
    S["tanque"] = empty(LEJOS)
    for (sx, sy, sz), loc in (((1, 16, 18), (-21, 0, -10)), ((1, 16, 18), (21, 0, -10)), ((42, 1, 18), (0, 8.5, -10)), ((44, 18, 1), (0, 0, -19.5))):
        box((sx, sy, sz), loc, (0.4, 0.42, 0.46), parent=S["tanque"])
    S["liq"] = box((41, 16, 16), (0, 0, -11), SALT, parent=S["tanque"], unique=True); alpha(S["liq"], 0.5)
    S["burbujas"] = [sph(0.6, LEJOS, (1.0, 0.8, 0.55), seg=8) for _ in range(14)]
    # red del cristal e iones
    S["red"] = empty(LEJOS)
    blk = box((22, 8, 5), (0, 0, -2.6), GLS, parent=S["red"], unique=True); alpha(blk, 0.3)
    for i in range(11):
        for j in range(4):
            for z in (-1.4, -3.2):
                sph(0.45, (-10 + 2 * i + (1 if z < -2 else 0), -3 + 2 * j, z), NET, parent=S["red"], seg=10)
    S["liq2"] = box((22, 8, 9), LEJOS, SALT, unique=True); alpha(S["liq2"], 0.3)
    rnd = random.Random(5); S["ionpos"] = [(-9 + 2 * i, -2 + 2 * j) for i in range(10) for j in range(3)]
    S["orden"] = list(range(30)); rnd.shuffle(S["orden"])
    S["na"] = [sph(0.42, LEJOS, NA, seg=12) for _ in range(30)]
    S["k"] = [sph(0.88, LEJOS, K, seg=12) for _ in range(30)]
    S["comp"] = [arrow(BLUE) for _ in range(4)]
    S["grieta2"] = box((1, 1, 1), LEJOS, (0.15, 0.05, 0.05))
    # capas: pantalla (con leds), cristal y plástico, en tiras para poder doblarlas
    S["capas"] = []
    for col, th in (((0.1, 0.1, 0.14), 1.4), (GLS, 0.6), ((0.93, 0.93, 0.96), 0.8)):
        tiras = []
        for i in range(10):
            o = box((3.7, 24, th), LEJOS, col, unique=True)
            if col != (0.1, 0.1, 0.14): alpha(o, 0.55 if col == GLS else 0.45)
            tiras.append(o)
        S["capas"].append(tiras)
    S["leds"] = []
    for i, tira in enumerate(S["capas"][0]):
        for j in range(6):
            o = box((0.24, 0.05, 0.4), (0, (-10 + 4 * j) / 24, 0.55), (0.1, 0.1, 0.1), parent=tira, unique=True)  # local (escala de la tira)
            S["leds"].append((o, (i + j) % 3))
    S["bola"] = sph(2, LEJOS, (0.6, 0.62, 0.68))
    # bisagra en corte
    S["hT"] = empty(LEJOS); S["hB"] = empty(LEJOS)
    S["cT"] = box((50, 20, 5), (0, 0, 0), BODY, parent=S["hT"]); S["cB"] = box((50, 20, 5), (0, 0, 0), BODY, parent=S["hB"])
    S["eje"] = cyl(9, 1, LEJOS, HINGE, rot=(math.pi / 2, 0, 0))
    S["tira"] = chain(80, STRIP, unique=True)
    S["trozos"] = [box((0.9, 6, 0.5), LEJOS, RED) for _ in range(8)]
    dyn = [cam, S["movil"], S["marca"], S["pelo"], S["maq"], S["pinza"], S["vid"], S["fuera"], S["dentro"], S["grieta"], S["pelo2"],
           S["tanque"], S["burbujas"], S["red"], S["liq2"], S["na"], S["k"], S["comp"], S["grieta2"], S["capas"], S["bola"],
           S["hT"], S["hB"], S["eje"], S["tira"], S["trozos"]]
    join_static(dyn)
    return sc, S


def tiempos():
    return dict(t1=T("un cristal normal"), fuera=T("por fuera"), dentro=T("por dentro"), grieta=T("y aparece"), fino=T("pero cuanto"),
                menos=T("menos se estira"), fin2=T("así que lo hacen"), t30=T("treinta"), pelo=T("un pelo mide"), bano=T("para que aguante"),
                sales=T("lo bañan"), atom=T("los átomos"), aprie=T("que aprietan"), grietas=T("así las grietas"), pant=T("debajo va"),
                luces=T("con sus millones"), flex=T("que también"), encima=T("y encima"), golpes=T("de los golpes"), bis=T("y la bisagra"),
                recto=T("si la pantalla"), part=T("se partiría"), gota=T("así que la bisagra"), forma=T("en forma"), curva=T("la pantalla se curva"),
                aplas=T("sin aplastarse"), poreso=T("por eso al"), ahora=T("y ahora"), antes=T("antes de venderlos"), dosc=T("doscientos"),
                cien=T("si lo abres"), cinco=T("son más"), aun=T("y aun así"), marca=T("se nota"))


def seccion(t, k):
    if t < k["t1"] - 0.15: return 0
    if t < k["bano"]: return 1
    if t < k["atom"] - 0.1: return 3
    if t < k["pant"] - 0.1: return 4
    if t < k["bis"] - 0.1: return 5
    if t < k["ahora"]: return 6
    return 7


def phi_movil(t, k):
    if t < k["t1"]:
        return keyed(t, [(0, 55), (2.1, 180), (3.9, 178), (4.9, 45), (5.3, 35)])
    if t < k["antes"]:
        return keyed(t, [(k["ahora"], 60), (k["ahora"] + 1.4, 180), (k["antes"], 175)])
    if t < k["aun"]:
        u = t - k["antes"]; ph = 0.6 * u + 0.9 * max(0, u - 1.0) ** 2   # cada vez más rápido
        return 92 + 86 * math.cos(ph * math.tau)
    return keyed(t, [(k["aun"], 92 + 86 * math.cos(math.tau * (0.6 * (k["aun"] - k["antes"]) + 0.9 * (k["aun"] - k["antes"] - 1) ** 2))),
                     (k["aun"] + 0.8, 180), (DUR + 2, 180)])


def strip_bend(k_, th, gap=0.0):
    if k_ < 1e-4: return [(-LB / 2 + LB * i / 40, 0.0) for i in range(41)]
    R = 1 / k_; pts = []
    for i in range(41):
        s = -LB / 2 + LB * i / 40; a = s * k_
        pts.append((R * math.sin(a), R * math.cos(a) - R))
    return pts


def pose(t, S):
    k = tiempos(); sec = seccion(t, k)
    # ---------- móvil ----------
    if sec in (0, 7):
        S["movil"].location = (0, 0, 0)
        b = math.radians((180 - phi_movil(t, k)) / 2); S["mL"].rotation_euler = (0, b, 0); S["mR"].rotation_euler = (0, -b, 0)
    else: S["movil"].location = LEJOS
    S["pelo"].location = (0, -40, 0.75) if (sec == 0 and k["t1"] - 2.7 < t < 4.15) else LEJOS
    if sec == 7:
        S["maq"].location = (0, 0, 0)
        b = math.radians((180 - phi_movil(t, k)) / 2); p = rotY((66, 4), -b)
        S["pinza"].location = (p[0], 0, p[1]); S["pinza"].rotation_euler = (0, -b, 0)
        mk = seg(t, k["marca"] - 0.3, k["marca"] + 0.6)
        S["marca"].location = (0, 0, 0.05) if t > k["aun"] + 0.6 else LEJOS
        set_color(S["marca"], tuple(mix(a, c, mk) for a, c in zip(SCR, (0.62, 0.78, 1.0))))
    else: S["maq"].location = LEJOS; S["pinza"].location = LEJOS; S["marca"].location = LEJOS
    # ---------- cristal doblándose ----------
    if sec == 1:
        kk = keyed(t, [(k["t1"] - 0.2, 0.0), (k["t1"] + 1.2, 0.075), (k["fin2"], 0.075), (k["fin2"] + 1.2, 0.0)])
        th = keyed(t, [(k["fino"], 5.0), (k["menos"] + 0.4, 1.5), (k["fin2"] + 0.4, 1.5), (k["t30"] + 0.6, 0.3)])
        rota = seg(t, k["grieta"], k["grieta"] + 0.35) * (1 - seg(t, k["fino"] - 0.1, k["fino"] + 0.2))
        pts = strip_bend(kk, th)
        chain_set(S["vid"], pts, th, 8)
        for i, o in enumerate(S["vid"]):
            sgn = 1 if i >= 20 else -1
            if rota > 0:
                o.location.x += sgn * 0.9 * rota; o.location.z -= 0.6 * rota * (1 - abs(i - 19.5) / 20)
            near = max(0, 1 - abs(i - 19.5) / 5)
            set_color(o, tuple(mix(a, c, rota * near) for a, c in zip(GLS, RED)))
        # flechas: tracción arriba (hacia fuera), compresión abajo (hacia dentro)
        strain = th * kk
        for n, (grp, t0, side) in enumerate(((S["fuera"], k["fuera"], 1), (S["dentro"], k["dentro"], -1))):
            vis = t0 - 0.1 < t < k["fin2"] + 0.8 and rota < 0.5
            for j, a in enumerate(grp):
                if not vis: a.location = LEJOS; continue
                s = (1 if j else -1) * LB * 0.22; ang = s * kk
                R = 1 / max(kk, 1e-4); c = Vector((R * math.sin(ang), 0, R * math.cos(ang) - R)) if kk > 1e-4 else Vector((s, 0, 0))
                nrm = Vector((math.sin(ang), 0, math.cos(ang)))
                tan = Vector((math.cos(ang), 0, -math.sin(ang))) * (1 if j else -1)
                L = (2.0 + 26 * strain) * seg(t, t0 - 0.1, t0 + 0.3) * (1 + 0.08 * math.sin(t * 7))
                if side < 0: tan = -tan
                p = c + nrm * side * (th / 2 + 1.3) - (tan * L if side < 0 else Vector((0, 0, 0))) + Vector((0, -4.5, 0))
                set_arrow(a, p, math.atan2(tan.z, tan.x), L, 0.55)
        if rota > 0.02:
            S["grieta"].location = (0, -0.5, pts[20][1] + th / 2 - 1.6 * rota); S["grieta"].scale = (0.6 * rota + 0.1, 9, 3.4 * rota)
        else: S["grieta"].location = LEJOS
        S["pelo2"].location = (LB / 2 + 0.9, 0, 0) if t > k["pelo"] - 0.2 else LEJOS
    else:
        hide(S["fuera"] + S["dentro"]); S["grieta"].location = LEJOS; S["pelo2"].location = LEJOS
        if sec != 3: hide(S["vid"])
    # ---------- baño de sales ----------
    if sec == 3:
        S["tanque"].location = (0, 0, 0)
        z = keyed(t, [(k["bano"], 15.0), (k["sales"] + 0.9, -10.0)])
        chain_set(S["vid"], [(-LB / 2 + LB * i / 40, z) for i in range(41)], 0.8, 8)
        for o in S["vid"]: set_color(o, GLS)
        for i, b in enumerate(S["burbujas"]):
            u = (t * 0.6 + i / 14) % 1.0
            b.location = (-17 + 34 * ((i * 0.37) % 1), -4 + 8 * ((i * 0.61) % 1), -18 + 15 * u)
    else: S["tanque"].location = LEJOS; hide(S["burbujas"])
    # ---------- iones ----------
    if sec == 4:
        S["red"].location = (0, 0, 0)
        lq = 1 - seg(t, k["aprie"] - 0.4, k["aprie"] + 0.2)
        S["liq2"].location = (0, 0, 4.6) if lq > 0.05 else LEJOS
        for n, idx in enumerate(S["orden"]):
            x, y = S["ionpos"][idx]; tt = k["atom"] + 0.2 + n / 30 * 2.7
            up = seg(t, tt, tt + 0.7)
            S["na"][idx].location = (x, y, 0.45 + 11 * up) if up < 0.98 else LEJOS
            dn = seg(t, tt + 0.25, tt + 0.85)
            S["k"][idx].location = (x, y, 13 - 12.3 * dn) if dn > 0.01 else LEJOS
        for j, a in enumerate(S["comp"]):
            if t > k["aprie"] - 0.1:
                sx = 1 if j < 2 else -1; y = -2 + 4 * (j % 2)
                L = 4 * seg(t, k["aprie"] - 0.1, k["aprie"] + 0.4) * (1 + 0.12 * math.sin(t * 8))
                set_arrow(a, (sx * (11 + L + 0.6), y - 4, 0.4), math.pi if sx > 0 else 0.0, L, 0.6)
            else: a.location = LEJOS
        g = seg(t, k["grietas"], k["grietas"] + 0.5) * (1 - seg(t, k["grietas"] + 0.9, k["grietas"] + 1.9))
        if g > 0.02: S["grieta2"].location = (0, 0, 1.0 - 2.4 * g); S["grieta2"].scale = (0.15 + 0.6 * g, 8.4, 4.8 * g)
        else: S["grieta2"].location = LEJOS
    else:
        S["red"].location = LEJOS; S["liq2"].location = LEJOS; hide(S["na"] + S["k"] + S["comp"]); S["grieta2"].location = LEJOS
    # ---------- capas ----------
    if sec == 5:
        flex = win01(t, k["flex"] - 0.3, k["golpes"], 0.5, 0.6)
        zs = [keyed(t, [(k["pant"], -30.0), (k["pant"] + 0.8, 0.0)]), 3.5, keyed(t, [(k["encima"], 34.0), (k["encima"] + 0.7, 6.8)])]
        for L_, (tiras, z0) in enumerate(zip(S["capas"], zs)):
            if L_ == 2 and t < k["encima"] - 0.05:
                hide(tiras); continue
            for i, o in enumerate(tiras):
                x = -16.65 + 3.7 * i; u = x / 18.5; amp = 4 * flex * math.sin(t * 2.6)
                dz = amp * u * u; slope = amp * 2 * u / 18.5
                o.location = (x, 0, z0 + dz); o.rotation_euler = (0, -math.atan(slope), 0); o.scale = (3.75, 24, o.scale.z if o.scale.z < 5 else 1)
        for i, o in enumerate(S["capas"][0]): o.scale.z = 1.4
        for i, o in enumerate(S["capas"][1]): o.scale.z = 0.6
        for i, o in enumerate(S["capas"][2]): o.scale.z = 0.8
        on = seg(t, k["luces"] - 0.2, k["luces"] + 1.4)
        for n, (o, c) in enumerate(S["leds"]):
            lit = on > (n * 0.37 % 1)
            base = ((1, 0.3, 0.3), (0.3, 1, 0.4), (0.35, 0.55, 1))[c]
            set_color(o, base if lit else (0.12, 0.12, 0.14))
        tg = k["golpes"]
        if tg - 0.7 < t < tg + 1.6:
            zb = 7.6 + 2 + (30 * (1 - seg(t, tg - 0.7, tg)) if t < tg else 9 * math.sin(min(1, (t - tg) / 0.9) * math.pi))
            S["bola"].location = (4, 0, zb)
        else: S["bola"].location = LEJOS
    else:
        for tiras in S["capas"]: hide(tiras)
        S["bola"].location = LEJOS
    # ---------- bisagra en corte ----------
    if sec == 6:
        gota = t > k["gota"]
        if not gota:
            psi = keyed(t, [(k["bis"], 110.0), (k["recto"] + 0.2, 110.0), (k["part"] - 0.05, 0.0)]); x0, g = 0.6, 1.6
            hx, hz = 0.5, 0.0
        else:
            psi = keyed(t, [(k["gota"], 110.0), (k["forma"], 25.0), (k["forma"] + 0.6, 0.0), (k["curva"], 0.0), (k["curva"] + 0.7, 60.0),
                            (k["aplas"] + 0.2, 0.0), (DUR, 0.0)]); x0, g = 7.0, 2.4
            c = 1 - min(1, psi / 110)
            hx, hz = mix(x0 * 0.6, 9.0, c), mix(0.0, 8.5, c)
        ps = math.radians(psi)
        S["hT"].location = (0, 0, 0); S["hB"].location = (0, 0, 0)
        S["hT"].rotation_euler = (0, -ps / 2, 0); S["hB"].rotation_euler = (0, ps / 2, 0)
        S["cT"].location = (x0 + 25, 0, g / 2 + 2.5); S["cB"].location = (x0 + 25, 0, -g / 2 - 2.5)
        S["eje"].location = (1.5, 10, 0) if gota else LEJOS
        chain_set(S["tira"], fold_pts(ps, x0, 50, g, hx, hz), 0.7, 18)
        rot = seg(t, k["part"] - 0.05, k["part"] + 0.15) * (not gota)
        for i, o in enumerate(S["tira"]):
            mid = abs(i - 39.5) < 6
            set_color(o, RED if (rot > 0.5 and mid) else STRIP)
        for j, o in enumerate(S["trozos"]):
            if rot > 0 and not gota:
                u = t - k["part"]; a = math.pi * (0.55 + 0.9 * j / 7)
                o.location = (-0.5 + 9 * u * math.cos(a), -2 + j * 0.3, 7 * u * math.sin(a) - 9 * u * u); o.rotation_euler = (0, u * 6 + j, 0)
            else: o.location = LEJOS
    else:
        S["hT"].location = LEJOS; S["hB"].location = LEJOS; S["eje"].location = LEJOS; hide(S["tira"] + S["trozos"])
    apply_cam(S["cam"], *cam_now(t, k))


def V(at, off, lens=40): at = Vector(at); return (tuple(at + Vector(off)), tuple(at), lens)


def shots(k):
    return [
        (0, k["t1"] - 0.15, [(0.0,) + V((0, -25, 12), (30, -95, 55), 32), (2.2,) + V((0, -35, 2), (22, -80, 42), 36),
                              (3.8,) + V((0, -40, 2), (10, -42, 22), 40), (k["t1"],) + V((0, -10, 25), (55, -150, 70), 32)]),
        (k["t1"] - 0.15, k["bano"], [(k["t1"] - 0.2,) + V((0, 0, -1), (6, -66, 10), 40), (k["grieta"],) + V((0, 0, 0), (4, -55, 8), 40),
                                     (k["fino"] + 0.5,) + V((0, 0, -1), (-6, -62, 10), 40), (k["fin2"] + 0.8,) + V((6, 0, 0), (-2, -40, 6), 40),
                                     (k["t30"] + 0.5,) + V((14.6, 0, 0), (-2.0, -10, 2.0), 50), (k["bano"],) + V((15, 0, 0), (-3.0, -11, 3.0), 50)]),
        (k["bano"], k["atom"] - 0.1, [(k["bano"],) + V((0, 0, 0), (8, -70, 18), 35), (k["atom"],) + V((0, 0, -6), (4, -62, 8), 35)]),
        (k["atom"] - 0.1, k["pant"] - 0.1, [(k["atom"] - 0.1,) + V((0, 0, 1), (4, -30, 16), 32), (k["aprie"],) + V((0, 0, 0), (-3, -31, 11), 32),
                                            (k["grietas"],) + V((0, 0, -0.5), (1, -22, 6), 34), (k["pant"],) + V((0, 0, -0.5), (3, -21, 6), 34)]),
        (k["pant"] - 0.1, k["bis"] - 0.1, [(k["pant"] - 0.1,) + V((0, 0, 0), (22, -52, 26), 34), (k["flex"],) + V((0, 0, 1), (28, -64, 22), 34),
                                           (k["encima"] + 0.5,) + V((0, 0, 4), (24, -58, 30), 34), (k["bis"],) + V((0, 0, 4), (18, -55, 24), 34)]),
        (k["bis"] - 0.1, k["ahora"], [(k["bis"] - 0.1,) + V((14, 0, 10), (8, -95, 14), 36), (k["recto"] + 0.6,) + V((6, 0, 4), (4, -60, 6), 38),
                                      (k["part"] + 0.3,) + V((2, 0, 0), (2, -38, 4), 40), (k["gota"] + 0.3,) + V((10, 0, 8), (6, -80, 10), 36),
                                      (k["forma"] + 0.6,) + V((4, 0, 0), (3, -48, 5), 40), (k["curva"] + 0.5,) + V((8, 0, 6), (5, -70, 8), 38),
                                      (k["poreso"],) + V((6, 0, 0), (2, -42, 4), 40), (k["ahora"],) + V((8, 0, 0), (-2, -34, 3), 42)]),
        (k["ahora"], DUR + 2, [(k["ahora"],) + V((-10, 0, 20), (90, -190, 120), 34), (k["dosc"],) + V((-10, 0, 25), (110, -200, 110), 34),
                               (k["aun"],) + V((-5, 0, 15), (80, -170, 90), 34), (k["marca"],) + V((0, -10, 0), (-28, -115, 26), 42),
                               (DUR + 2,) + V((0, -10, 0), (-20, -95, 20), 44)]),
    ]


def cam_now(t, k):
    for a, b, ks in shots(k):
        if a <= t < b: return cam_state(t, ks, drift=0.15)
    return cam_state(t, shots(k)[-1][2], drift=0.15)


def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v); k = tiempos()
    kk = 0.075; s = LB * 0.22; a = s * kk; R = 1 / kk
    na0 = S["ionpos"][S["orden"][-1]]; k0 = S["ionpos"][S["orden"][0]]
    return {"fuera": Pj((R * math.sin(a), -4, R * math.cos(a) - R + 4)), "dentro": Pj((-R * math.sin(a), -4, R * math.cos(a) - R - 4)),
            "grieta": Pj((0, -4, 3)), "vidrio": Pj((LB / 2 - 0.4, -4, 0)), "pelo": Pj((LB / 2 + 0.9, -4, 0)),
            "liq": Pj((14, -8, -6)), "na": Pj((na0[0], na0[1], 0.9)), "k": Pj((k0[0], k0[1], 1.2)), "comp": Pj((-13, -4, 0.5)),
            "pant": Pj((18, -12, 0)), "cris": Pj((18, -12, 3.5)), "plas": Pj((18, -12, 7)),
            "pliegue": Pj((-0.5, -9, 0)), "gota": Pj((-3, -9, 0)), "hueco": Pj((14, -9, 0)), "marca": Pj((0, -55, 0)), "movil": Pj((0, -40, 30))}


if __name__ == "__main__":
    run("plegable", build, pose, anchors)
