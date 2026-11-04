# «Si tuvieras que inventar los auriculares»: altavoz de auricular en corte, con el sonido hacia arriba.
# Aire que va y viene (bolitas), membrana, bobina de cobre, imán; la corriente cambia de sentido y la membrana vibra
# (lenta para los graves, muy rápida para los agudos); el sonido de atrás anula el de delante; carcasa, agujeritos
# con tela y almohadilla.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("auriculares")
MEMC = (0.92, 0.92, 0.95); CU = (0.9, 0.5, 0.25); STEEL = (0.35, 0.37, 0.42); MAG = (0.55, 0.57, 0.62); CASE = (0.2, 0.21, 0.25)
INNER = (0.4, 0.42, 0.48); PAD = (0.12, 0.12, 0.14); AIR = (0.55, 0.8, 1.0); BACK = (1.0, 0.6, 0.3); NRED = (0.95, 0.3, 0.3); SBLU = (0.3, 0.55, 1.0)

def alpha(o, a):
    m = o.active_material; m.diffuse_color = (*m.diffuse_color[:3], a); m.surface_render_method = 'BLENDED'

def vaso(r, h, loc, color, v=64):
    """cilindro abierto por arriba (para que el SOLIDIFY y el corte funcionen bien)"""
    import bmesh
    me = bpy.data.meshes.new("vaso"); bm = bmesh.new()
    a = [bm.verts.new((r * math.cos(0.01 + 2 * math.pi * k / v), r * math.sin(0.01 + 2 * math.pi * k / v), 0)) for k in range(v)]
    b = [bm.verts.new((r * math.cos(0.01 + 2 * math.pi * k / v), r * math.sin(0.01 + 2 * math.pi * k / v), h)) for k in range(v)]
    for k in range(v): j = (k + 1) % v; bm.faces.new((a[k], a[j], b[j], b[k]))
    bm.faces.new(list(reversed(a))); bm.normal_update(); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("vaso", me); bpy.context.collection.objects.link(o); o.location = loc
    return setup(o, color, unique=True)

def build():
    sc, cam = scene_setup(world=(0.1, 0.11, 0.15), shadow=0.25)
    S = {"cam": cam}
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.013, -4.987, 0.011)); cutter = bpy.context.object; cutter.scale = (14, 10, 20); cutter.hide_render = True
    def cortar(o, th=None, inner=INNER):
        if th:
            o.data.materials.append(mat(inner, unique=True))
            m = o.modifiers.new("sol", "SOLIDIFY"); m.thickness = th; m.offset = -1; m.material_offset = 1; m.material_offset_rim = 1
        b = o.modifiers.new("cut", "BOOLEAN"); b.operation = 'DIFFERENCE'; b.object = cutter; return o
    # membrana + bobina (se mueven juntas)
    S["mem"] = mem = empty((0, 0, 0))
    S["memb"] = sph(1.6, (0, 0, 0), MEMC, parent=mem, scale=(1, 1, 0.12), seg=40, unique=True)
    S["cupula"] = sph(0.6, (0, 0, 0.1), (0.85, 0.86, 0.9), parent=mem, scale=(1, 1, 0.45), seg=24, unique=True)
    S["bob"] = bob = empty((0, 0, 0), parent=mem)
    S["vueltas"] = [torus(0.55, 0.055, (0, 0, -0.25 - 0.11 * k), CU, parent=bob, unique=True) for k in range(6)]
    # imán (fijo) cortado
    S["iman"] = iman = empty((0, 0, 0))
    o = cyl(0.42, 1.1, (0, 0, -0.95), STEEL, v=32, unique=True); o.parent = iman
    o = cortar(cyl(1.3, 0.6, (0, 0, -0.95), MAG, v=48, unique=True)); o.parent = iman
    hole = cyl(0.66, 2.0, (0, 0, -0.95), (0, 0, 0)); hole.hide_render = True; hole.parent = iman
    b = o.modifiers.new("hole", "BOOLEAN"); b.operation = 'DIFFERENCE'; b.object = hole; o.modifiers.move(1, 0)
    S["anillo"] = o
    o = cortar(cyl(1.3, 0.18, (0, 0, -1.34), STEEL, v=48, unique=True)); o.parent = iman
    S["polo"] = cyl(0.43, 0.04, (0, 0, -0.39), NRED, v=32, unique=True); S["polo"].parent = iman
    # cables con corriente
    S["cab"] = [bar_obj((0.85, 0.5, 0.25), 0.03, unique=True) for _ in range(2)]
    S["els"] = [sph(0.05, (0, 0, -30), (0.4, 0.85, 1.0), seg=8) for _ in range(12)]
    # carcasa trasera (vaso abierto por arriba), agujeritos y tela
    S["car"] = car = empty((0, 0, 0))
    o = cortar(vaso(1.95, 2.0, (0, 0, -2.05), CASE), th=0.12)
    o.parent = car; S["carcasa"] = o
    S["aguj"] = []
    for k in range(5):
        x = -1.2 + 0.6 * k; S["aguj"].append(cyl(0.1, 0.36, (x, 0.0, -2.0), (0.03, 0.03, 0.04), v=12, unique=True))
    S["tela"] = cyl(1.5, 0.05, (0, 0, -2.2), (0.6, 0.62, 0.68), v=48, unique=True)
    S["almo"] = torus(1.85, 0.38, (0, 0, 0.35), PAD, unique=True); S["almo"].scale = (1, 1, 0.75)
    # aire: rejilla de bolitas delante; ondas delante y detrás; soplidos por los agujeros
    S["aire"] = []
    for i in range(9):
        for j in range(16):
            S["aire"].append((sph(0.06, (0, 0, -30), AIR, seg=8), -2.0 + 0.5 * i, 0.55 + 0.33 * j))
    S["ondas"] = [torus(1.0, 0.04, (0, 0, -30), AIR, unique=True) for _ in range(4)]
    S["ondasB"] = [torus(1.0, 0.04, (0, 0, -30), BACK, unique=True) for _ in range(4)]
    S["soplo"] = [sph(0.08, (0, 0, -30), AIR, seg=8) for _ in range(10)]
    join_static([cam, cutter, mem, iman, S["cab"], S["els"], car, S["aguj"], S["tela"], S["almo"], [a for a, _, _ in S["aire"]],
                 S["ondas"], S["ondasB"], S["soplo"]])
    return sc, S

def cmix(a, b, u): return tuple(mix(x, y, u) for x, y in zip(a, b))
def sc3(o, s): s = max(s, 0.001); o.scale = (s, s, s)

def amp_f(t):
    """amplitud y frecuencia (visual) de la membrana"""
    t_son = T("el sonido es")
    if t < t_son - 0.4: return 0.14, 3.0
    if t < T("una membrana"): return 0.0, 1.5
    a, f = 0.15, 1.5
    if T("pero cómo la") <= t < T("cuando llega") + 0.4: a = 0.0
    if T("una nota grave") <= t < T("una aguda"): a, f = 0.28, 1.0
    if T("una aguda") <= t < T("justo lo que"): a, f = 0.05, 9.0
    if T("pero el aire encerrado") <= t < T("así que le haces") + 0.6: a = 0.04 + 0.11 * (1 - seg(t, T("pero el aire encerrado"), T("pero el aire encerrado") + 0.8))
    return a, f

FASE = {}
def fase(t):
    """fase acumulada (para que la frecuencia cambie sin saltos)"""
    k = round(t * 30)
    if k in FASE: return FASE[k]
    ph, x = 0.0, 0.0
    while x < t: ph += 2 * math.pi * amp_f(x)[1] * min(0.02, t - x); x += 0.02
    FASE[k] = ph; return ph

def pose(t, S):
    t_son = T("el sonido es"); t_mem = T("una membrana"); t_bob = T("le pegas detrás"); t_iman = T("y la colocas")
    t_mus = T("cuando llega"); t_car = T("así que cierras"); t_agu = T("así que le haces"); t_tela = T("tapados con"); t_alm = T("la almohadilla")
    sale = seg(t, t_son - 0.4, t_son + 0.3)      # al principio todo montado; luego se desmonta
    a, f = amp_f(t); ph = fase(t); zm = a * math.sin(ph) if a > 0 else 0.0
    # membrana
    s_mem = (1 - sale) if t < t_son + 0.5 else seg(t, t_mem - 0.2, t_mem + 0.5)
    S["mem"].location = (0, 0, zm); sc3(S["memb"], s_mem); S["memb"].scale.z = 0.12 * max(s_mem, 0.001); sc3(S["cupula"], s_mem); S["cupula"].scale.z = 0.45 * max(s_mem, 0.001)
    # bobina: entra por debajo
    yb = 0.0 if t < t_son else (1 - seg(t, t_bob, t_bob + 0.8)) * -6.0
    S["bob"].location = (0, 0, mix(0, -8, sale) if t < t_son + 0.5 else yb)
    # imán: sube desde abajo
    zi = mix(0, -9, sale) if t < t_son + 0.5 else -8 * (1 - seg(t, t_iman, t_iman + 0.9))
    S["iman"].location = (0, 0, zi)
    # polaridad de la bobina cuando hay música: roja (norte arriba) o azul
    on = seg(t, t_mus, t_mus + 0.4) if t > t_son else 1.0
    pol = math.cos(ph) if a > 0 else 0.0
    for v in S["vueltas"]:
        set_color(v, cmix(CU, NRED if pol > 0 else SBLU, on * min(1, abs(pol) * 1.5) * win01(t, T("y cada vez"), T("una nota grave"), 0.3, 0.3)))
    # cables
    p_base = Vector((0, 0, zm - 0.6)) + Vector(S["bob"].location)
    vis_cab = (t < t_son) or (t > t_mus - 0.2)
    for k, c in enumerate(S["cab"]):
        sx = -1 if k == 0 else 1
        if vis_cab and t > t_bob + 0.5 or t < t_son: bar_set(c, p_base + Vector((sx * 0.55, 0, 0)), Vector((sx * 2.6, -0.2, -1.6)))
        else: bar_set(c, (0, 0, -30), (0, 0, -30.1))
        c.scale.x = c.scale.y = 0.03
    corr = win01(t, t_mus, T("una nota grave"), 0.3, 0.3)
    dirc = 1 if pol >= 0 else -1
    for k, e in enumerate(S["els"]):
        if corr < 0.05: e.location = (0, 0, -30); continue
        u = (k / 12 + dirc * t * 0.6) % 1.0
        if u < 0.5: e.location = Vector((-2.6, -0.2, -1.6)).lerp(p_base + Vector((-0.55, 0, 0)), u * 2)
        else: e.location = (p_base + Vector((0.55, 0, 0))).lerp(Vector((2.6, -0.2, -1.6)), u * 2 - 1)
    # carcasa
    zc = mix(0, -9, sale) if t < t_son + 0.5 else -8 * (1 - seg(t, t_car, t_car + 0.9))
    S["car"].location = (0, 0, zc)
    hol = seg(t, t_agu, t_agu + 0.6) if t > t_son else 1.0
    for h in S["aguj"]: h.location.z = -2.0 + zc if hol > 0.5 else -30
    S["tela"].location.z = (-2.2 + zc) if (t < t_son or t > t_tela) else -30
    sc3(S["tela"], 1 if t < t_son else seg(t, t_tela, t_tela + 0.5)); S["tela"].scale.z = max(S["tela"].scale.z, 0.001)
    za = mix(0.35, 7, sale) if t < t_son + 0.5 else 0.35 + 7 * (1 - seg(t, t_alm, t_alm + 0.9))
    S["almo"].location.z = za
    # aire delante: ondas longitudinales que salen de la membrana
    a_air = a if t > t_mem or t < t_son - 0.4 else (0.12 if t > t_son else 0.0)
    ph_air = ph if t > t_mem or t < t_son - 0.4 else 2 * math.pi * 1.3 * t
    for o, x, z in S["aire"]:
        k = 2.4
        dz = a_air * 1.4 * math.sin(ph_air - k * (z - 0.4)) * (1.0 if abs(x) < 2.1 else 0.5)
        zz = z + dz + (0 if t > t_son else 0.4)
        o.location = (x, 0.3, zz)
    # ondas (anillos): delante hacia arriba; detrás, en la fase de «se anula»
    vol = a > 0.06
    canc = win01(t, T("pero la membrana también"), t_car + 0.5, 0.3, 0.3)
    for k, r in enumerate(S["ondas"]):
        u = (t * 0.6 + k / 4) % 1.0
        if not vol or (t_son - 0.3 < t < t_mem + 0.5): r.location = (0, 0, -30); continue
        r.location = (0, 0, 0.4 + 3.5 * u); sc3(r, 1.0 + 1.2 * u)
        if canc > 0.3 and t > T("y ese sonido"): sc3(r, (1.0 + 1.2 * u) * (1 - seg(t, T("lo anula") - 0.4, T("lo anula") + 0.3)))
    for k, r in enumerate(S["ondasB"]):
        u = (t * 0.6 + k / 4) % 1.0
        if canc < 0.05: r.location = (0, 0, -30); continue
        # sale por detrás, rodea el borde y sube hacia delante
        if u < 0.5: z = -0.6 - 2.0 * u; s = 1.1 + 1.6 * u
        else: z = mix(-1.6, 2.5, (u - 0.5) * 2); s = 1.9 + 0.4 * (u - 0.5)
        r.location = (0, 0, z); sc3(r, s * canc)
        if t > T("y ese sonido"): sc3(r, s * canc * (1 - seg(t, T("lo anula") - 0.4, T("lo anula") + 0.3)))
    # soplidos por los agujeritos
    for k, sp in enumerate(S["soplo"]):
        if T("para que respire") - 0.8 < t < t_alm and hol > 0.5:
            u = (t * 0.9 + k / 10) % 1.0; x = -1.2 + 0.6 * (k % 5)
            sp.location = (x, 0.3, -2.1 - 1.3 * u); sc3(sp, (1 - u) * 1.3)
        else: sp.location = (0, 0, -30)
    apply_cam(S["cam"], *cam_state(t, CAM(), drift=0.02))

def orb(tg, d, el, az, lens=35, up=0.08):
    tg = Vector(tg); el, az = math.radians(el), math.radians(az)
    pos = tg + d * Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    return (tuple(pos), tuple(tg + Vector((0, 0, up * d))), lens)

def CAM():
    return [(0.0,) + orb((0, 0, 0.2), 6.0, 32, -22), (2.5,) + orb((0, 0, 0.0), 8.0, 26, -12), (T("el sonido es"),) + orb((0, 0, 1.5), 11.0, 12, -8),
            (T("así que necesitas"),) + orb((0, 0, 1.6), 10.0, 14, 6), (T("una membrana"),) + orb((0, 0, 0.6), 8.0, 18, -10),
            (T("le pegas detrás"),) + orb((0, 0, -0.6), 6.5, 10, -16), (T("y la colocas"),) + orb((0, 0, -0.7), 7.0, 14, 10),
            (T("cuando llega"),) + orb((0, 0, -0.4), 8.5, 12, -6), (T("y cada vez"),) + orb((0, 0, -0.5), 6.5, 10, -12),
            (T("una nota grave"),) + orb((0, 0, 0.8), 10.0, 12, -6), (T("una aguda"),) + orb((0, 0, 0.8), 9.0, 14, 8),
            (T("pero la membrana también"),) + orb((0, 0, 0.0), 12.5, 10, -8), (T("así que cierras"),) + orb((0, 0, -0.6), 11.0, 14, -12),
            (T("así que le haces"),) + orb((0, 0, -1.4), 9.5, 6, -6), (T("por último"),) + orb((0, 0, 0.0), 10.0, 16, -10),
            (T("y un dato"),) + orb((0, 0, 0.6), 11.0, 18, 8), (DUR + 2,) + orb((0, 0, 0.6), 12.0, 22, -16)]

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v); zm = S["mem"].location.z
    bz = S["bob"].location.z + zm; iz = S["iman"].location.z; cz = S["car"].location.z
    return {"aire": Pj((1.5, 0, 3.0)), "mem": Pj((1.2, 0, zm)), "bob": Pj((0.6, 0, bz - 0.5)), "iman": Pj((1.2, 0, iz - 0.95)),
            "cab": Pj((2.4, -0.2, -1.5)), "car": Pj((1.9, 0, cz - 1.2)), "aguj": Pj((0, 0, cz - 2.2)), "almo": Pj((1.9, 0, S["almo"].location.z + 0.3)),
            "front": Pj((0, 0, 2.6)), "back": Pj((0, 0, -2.4)), "polo": Pj((0, 0, bz - 0.2))}

if __name__ == "__main__":
    run("auriculares", build, pose, anchors)
