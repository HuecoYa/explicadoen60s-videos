# Capa 2D de «¿Y si construyes un tanque de tormentas?»
from _ovbase import *
from marcas import cargar
T, DUR = cargar("tormentas")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"llueve", "agua", "rejilla", "alcantarilla", "sucia", "tubo", "tormenta", "cabe", "inunda", "grandes", "ciudad",
            "depósito", "gigante", "excavas", "hormigón", "empuja", "pilares", "techo", "parque", "compuerta", "tanque",
            "basura", "rejas", "madrid", "cinco", "seis", "cuatrocientos", "pudre", "bombas", "depuradora", "catorce", "río"}

def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def keyed(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if a <= t <= b: return va + (vb - va) * ss((t - a) / max(b - a, 1e-4))
    return keys[-1][1]
def miles(v): return f"{int(round(v)):,}".replace(",", ".")

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.75, 1.0)
    BY = H * 0.265
    label(C, ctx, t, T("la rejilla") - 0.1, T("pero en muchas"), "REJILLA", A, "rejilla", dx=0, dy=-140, size=60)
    label(C, ctx, t, T("van por") - 0.3, T("y en una"), "COLECTOR", A, "colector", dx=0, dy=150, size=60)
    # el colector se llena: % de capacidad
    a0, a1 = T("y en una"), T("podrías")
    if a0 <= t < a1:
        v = keyed(t, [(a0, 45), (T("cae más") + 0.8, 100), (T("así que el agua"), 100), (T("y la calle", fin=True), 130)])
        C.badge(ctx, f"{int(v)} %", W / 2, BY, win(t, a0, a1), R if v >= 100 else B, size=96)
        if t > T("y la calle"):
            cm = keyed(t, [(T("y la calle"), 0), (T("y la calle") + 1.2, 30)])
            C.badge(ctx, f"+{int(cm)} cm", W / 2, BY + 150, win(t, T("y la calle"), a1), Y, size=78)
    label(C, ctx, t, T("podrías") + 0.3, T("pero tendrías"), "×2", A, "tubo", dx=0, dy=60, size=90)
    badge(C, ctx, t, T("pero tendrías") + 0.4, T("así que construyes"), "✗ OBRAS EN TODAS LAS CALLES", R, size=62)
    label(C, ctx, t, T("bajo tierra") - 0.2, T("excavas"), "TANQUE", A, "tanque", dx=0, dy=-120, size=66)
    label(C, ctx, t, T("de hormigón") - 0.2, T("pero la tierra"), "HORMIGÓN", A, "muro", dx=60, dy=-130, size=58)
    label(C, ctx, t, T("pero la tierra") + 0.2, T("así que llenas") + 0.5, "TIERRA", A, "tierra", dx=-20, dy=-130, size=60)
    label(C, ctx, t, T("de pilares") - 0.1, T("encima"), "PILARES", A, "pilar", dx=0, dy=-260, size=62)
    label(C, ctx, t, T("una compuerta") + 0.3, T("pero esa agua"), "COMPUERTA", A, "comp", dx=150, dy=-120, size=58)
    a0, a1 = T("una compuerta") + 0.8, T("pero esa agua") + 0.2
    if a0 <= t < a1:
        v = keyed(t, [(a0, 0), (T("y se va", fin=True) + 0.3, 75000)])
        C.badge(ctx, miles(v) + " m³", W / 2, BY, win(t, a0, a1), B, size=90)
    label(C, ctx, t, T("rejas") + 0.3, T("y aquí viene"), "REJAS", A, "rejas", dx=-60, dy=-170, size=62)
    badge(C, ctx, t, T("el más grande"), T("ocupa"), "Nº 1 DEL MUNDO", Y, size=86)
    a0, a1 = T("ocupa"), T("es tan")
    if a0 <= t < a1:
        n = 0
        for k in range(5):
            if t > a0 + 0.45 + 0.32 * k: n = k + 1
        if n: C.badge(ctx, f"× {n}", W / 2, BY, win(t, a0 + 0.4, a1), G, size=100)
    a0, a1 = T("es tan"), T("y le caben") + 0.6
    if a0 + 0.3 <= t < a1:
        n = max(1, min(6, 1 + int((t - a0 - 0.3) / 0.3)))
        label(C, ctx, t, a0 + 0.3, a1, f"PLANTA {n}", A, "plantas", dx=-60, dy=-90, size=60)
    a0, a1 = T("y le caben"), T("pero si el")
    if a0 <= t < a1:
        v = keyed(t, [(a0, 75000), (T("cúbicos", fin=True), 400000)])
        C.badge(ctx, miles(v) + " m³", W / 2, BY, win(t, a0, a1), B, size=96)
    a0, a1 = T("pero si el"), T("cuando pasa")
    if a0 <= t < a1:
        d = 1 + int(min(6, 7 * (t - a0) / max(0.5, T("se pudre", fin=True) - a0)))
        C.badge(ctx, f"DÍA {d}", W / 2, BY, win(t, a0, a1), (0.75, 0.8, 0.3), size=88)
    label(C, ctx, t, T("unas bombas") + 0.2, T("el de madrid"), "BOMBAS", A, "bombas", dx=-150, dy=-120, size=60)
    label(C, ctx, t, T("depuradora") - 0.2, T("el de madrid") + 0.5, "DEPURADORA", A, "depu", dx=-150, dy=170, size=54)
    a0, a1 = T("el de madrid"), T("así el") + 0.3
    if a0 <= t < a1:
        h = keyed(t, [(a0 + 0.5, 14.5), (T("y media", fin=True), 0.0)])
        v = keyed(t, [(a0 + 0.5, 400000), (T("y media", fin=True), 0)])
        C.badge(ctx, (f"{h:.1f} h").replace(".", ","), W / 2, BY, win(t, a0, a1), Y, size=96)
        C.badge(ctx, miles(v) + " m³", W / 2, BY + 150, win(t, a0 + 0.2, a1), B, size=76)
    a0, a1 = T("así el"), DUR - 0.8
    if a0 <= t < a1:
        label(C, ctx, t, a0 + 0.3, a1, "RÍO", A, "rio", dx=-60, dy=-200, size=64)
        badge(C, ctx, t, T("no acaba"), a1, "✓ LIMPIO", G, size=86)

def sfx_events(C):
    E = [(0.0, C.s_buzz(1.2), 0.25), (0.1, C.s_whoosh(), 0.35), (T("la rejilla"), C.s_pop(), 0.35), (T("van por"), C.s_pop(), 0.35),
         (T("cae más"), C.s_buzz(1.5), 0.3), (T("y la calle"), C.s_fail(), 0.4), (T("podrías"), C.s_whoosh(), 0.35),
         (T("pero tendrías") + 0.3, C.s_clank(), 0.45), (T("así que construyes"), C.s_whoosh(), 0.4), (T("excavas"), C.s_thud(), 0.5),
         (T("y levantas"), C.s_clank(), 0.45), (T("pero la tierra"), C.s_thud(), 0.45), (T("así que llenas") + 0.6, C.s_clank(), 0.4),
         (T("el techo"), C.s_thud(), 0.45), (T("encima"), C.s_pop(), 0.4), (T("una compuerta") + 0.3, C.s_clank(), 0.5),
         (T("así que a la") + 0.5, C.s_clank(), 0.45), (T("el más grande"), C.s_coin(), 0.4)]
    for k in range(5): E.append((T("ocupa") + 0.45 + 0.32 * k, C.s_pop(), 0.35))
    for k in range(6): E.append((T("es tan") + 0.3 + 0.3 * k, C.s_pop(), 0.3))
    E += [(T("cúbicos"), C.s_win(), 0.4), (T("se pudre"), C.s_fail(), 0.35), (T("unas bombas"), C.s_buzz(2.0), 0.3),
          (T("y media"), C.s_coin(), 0.4), (T("no acaba"), C.s_win(), 0.4), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
