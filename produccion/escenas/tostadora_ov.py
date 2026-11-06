# Capa 2D de «Si tuvieras que inventar la tostadora…»
from _ovbase import *
from marcas import cargar
T, DUR = cargar("tostadora")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"palanca", "tostada", "salta", "calor", "fuego", "peligroso", "electricidad", "nicrom", "corriente", "rojo", "mil",
            "cuatrocientos", "contacto", "infrarrojo", "invisible", "ciento", "cuarenta", "seca", "lados", "bandeja", "muelle",
            "imán", "desenchufada", "parar", "reloj", "lámina", "metales", "dobla", "suelta", "ruedecita"}

def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def keyed(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if a <= t <= b: return va + (vb - va) * ss((t - a) / max(b - a, 1e-4))
    return keys[-1][1]
def miles(v): return f"{int(round(v)):,}".replace(",", ".")

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.75, 1.0)
    BY = H * 0.265; O = (1.0, 0.55, 0.2)
    badge(C, ctx, t, T("pero el fuego") + 0.3, T("así que usas"), "✗ FUEGO", R, size=90)
    label(C, ctx, t, T("el nicrom") - 0.1, T("así que se calienta"), "NICROM", A, "hilo", dx=0, dy=-140, size=64)
    # temperatura del hilo
    a0, a1 = T("así que se calienta"), T("pero el pan")
    if a0 <= t < a1:
        v = keyed(t, [(a0, 20), (T("y se pone", fin=True) + 0.4, 900), (T("cuatrocientos", fin=True), 1400)])
        C.badge(ctx, miles(v) + " °C", W / 2, BY, win(t, a0, a1), R if v > 600 else O, size=96)
        if t > T("sin fundirse"): C.badge(ctx, "✓ NO SE FUNDE", W / 2, BY + 150, win(t, T("sin fundirse"), a1), G, size=70)
    badge(C, ctx, t, T("pero el pan") + 0.3, T("ese hilo"), "✗ CONTACTO", R, size=86)
    # temperatura del pan
    a0, a1 = T("pero solo"), T("pero ahora")
    if a0 <= t < a1:
        v = keyed(t, [(a0 + 0.3, 20), (T("por debajo"), 125), (T("así que pones hilos"), 125), (T("muy cerca", fin=True), 165)])
        C.badge(ctx, f"PAN {int(v)} °C", W / 2, BY, win(t, a0, a1), O if v >= 140 else B, size=88)
        C.badge(ctx, "MÍN. 140 °C", W / 2, BY + 145, win(t, a0 + 0.6, a1), Y, size=58)
    label(C, ctx, t, T("una bandeja") , T("al bajar"), "BANDEJA", A, "band", dx=-120, dy=170, size=60)
    label(C, ctx, t, T("un muelle") - 0.1, T("al bajar") + 0.6, "MUELLE", A, "muelle", dx=150, dy=-60, size=60)
    label(C, ctx, t, T("y un imán") + 0.3, T("y aquí viene"), "IMÁN", A, "iman", dx=-170, dy=-110, size=64)
    a0, a1 = T("ese imán"), T("por eso")
    if a0 <= t < a1: C.badge(ctx, "ON", W / 2, BY, win(t, a0, a1), G, size=88)
    a0, a1 = T("si la tostadora"), T("pero falta")
    if a0 <= t < a1: C.badge(ctx, "OFF", W / 2, BY, win(t, a0, a1), R, size=96)
    label(C, ctx, t, T("si la tostadora") + 0.3, T("la palanca no"), "DESENCHUFADA", A, "clavija", dx=60, dy=-150, size=54)
    a0, a1 = T("saber cuándo"), T("así que añades")
    if a0 <= t < a1: C.badge(ctx, "?", W / 2, BY, win(t, a0, a1), Y, size=110)
    label(C, ctx, t, T("un reloj"), T("o una lámina") + 0.3, "RELOJ", A, "reloj", dx=0, dy=-150, size=60)
    a0, a1 = T("o una lámina") + 0.3, T("al calentarse")
    if a0 <= t < a1:
        label(C, ctx, t, a0, a1, "METAL 1", A, "lamina", dx=-60, dy=-160, size=56)
        label(C, ctx, t, a0 + 0.3, a1, "METAL 2", A, "lamina", dx=60, dy=150, size=56)
    a0, a1 = T("al calentarse"), T("corta la")
    if a0 <= t < a1:
        v = keyed(t, [(a0, 0), (T("y la lámina") + 0.8, 55), (T("cuando se dobla") + 0.6, 100)])
        C.badge(ctx, f"DOBLADO {int(v)} %", W / 2, BY, win(t, a0, a1), O, size=80)
    a0, a1 = T("corta la"), T("el muelle tira")
    if a0 <= t < a1: C.badge(ctx, "OFF", W / 2, BY, win(t, a0, a1), R, size=96)
    a0, a1 = T("si giras"), DUR - 0.8
    if a0 <= t < a1:
        n = int(keyed(t, [(a0 + 0.2, 2), (T("cambias") + 0.6, 5)]))
        C.badge(ctx, f"NIVEL {n}", W / 2, BY, win(t, a0, a1), Y, size=90)

def sfx_events(C):
    E = [(0.05, C.s_clank(), 0.5), (T("y la tostada") + 0.5, C.s_clank(), 0.55), (T("y la tostada") + 0.55, C.s_whoosh(), 0.4),
         (T("vamos a"), C.s_whoosh(), 0.4), (T("pero el fuego"), C.s_buzz(1.5), 0.3), (T("pero el fuego") + 0.3, C.s_fail(), 0.35),
         (T("el nicrom"), C.s_pop(), 0.4), (T("le cuesta"), C.s_buzz(2.5), 0.25), (T("y se pone"), C.s_coin(), 0.35),
         (T("sin fundirse"), C.s_win(), 0.35), (T("pero el pan") + 0.3, C.s_fail(), 0.3), (T("ese hilo"), C.s_whoosh(), 0.35),
         (T("así que pones hilos") + 0.2, C.s_pop(), 0.4), (T("así que pones una") + 0.3, C.s_thud(), 0.45), (T("un muelle"), C.s_pop(), 0.35),
         (T("estiras"), C.s_clank(), 0.5), (T("y un imán") + 0.3, C.s_clank(), 0.45), (T("ese imán"), C.s_buzz(2.0), 0.25),
         (T("si la tostadora") + 0.3, C.s_pop(), 0.4), (T("la palanca no"), C.s_clank(), 0.5), (T("pero falta") + 1.2, C.s_clank(), 0.45),
         (T("un reloj"), C.s_pop(), 0.35), (T("o una lámina") + 0.2, C.s_pop(), 0.35), (T("corta la"), C.s_buzz(0.3), 0.4),
         (T("el imán se"), C.s_fail(), 0.3), (T("el muelle tira"), C.s_clank(), 0.55), (T("y la tostada", 2), C.s_whoosh(), 0.45),
         (T("y la tostada", 2) + 0.2, C.s_win(), 0.4), (T("si giras"), C.s_pop(), 0.35), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
