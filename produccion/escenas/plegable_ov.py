# Capa 2D de «Así funciona una pantalla plegable»
from _ovbase import *
from marcas import cargar
T, DUR = cargar("plegable")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"cristal", "móvil", "dobla", "pelo", "rompe", "grieta", "fino", "finísimo", "treinta", "micras", "setenta", "sales",
            "calientes", "átomos", "grandes", "aprietan", "grietas", "pantalla", "lucecitas", "flexible", "plástico", "golpes",
            "bisagra", "recto", "partiría", "gota", "espacio", "máquina", "doscientos", "mil", "pliegues", "cien", "cinco", "años", "marca"}


def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def keyed(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if a <= t <= b: return va + (vb - va) * ss((t - a) / max(b - a, 1e-4))
    return keys[-1][1]
def miles(v): return f"{int(round(v)):,}".replace(",", ".")


def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.75, 1.0)
    Y1 = H * 0.265
    # cristal doblándose
    label(C, ctx, t, T("por fuera"), T("pero cuanto") - 0.1, "TRACCIÓN", A, "fuera", dx=0, dy=-120, size=58)
    label(C, ctx, t, T("por dentro"), T("pero cuanto") - 0.1, "COMPRESIÓN", A, "dentro", dx=0, dy=150, size=58)
    badge(C, ctx, t, T("y aparece") + 0.2, T("pero cuanto") - 0.1, "✗ ROTO", R, size=86)
    a0, a1 = T("pero cuanto"), T("para que aguante")
    if a0 <= t < a1:
        v = keyed(t, [(a0, 500), (T("menos se estira") + 0.4, 150), (T("así que lo hacen") + 0.4, 150), (T("treinta") + 0.6, 30)])
        C.badge(ctx, f"GROSOR {int(round(v))} µm", W / 2, Y1, win(t, a0, a1), Y, size=82)
    label(C, ctx, t, T("un pelo mide"), T("para que aguante"), "PELO 70 µm", A, "pelo", dx=60, dy=-280, size=56)
    label(C, ctx, t, T("un pelo mide") + 0.4, T("para que aguante"), "30 µm", A, "vidrio", dx=-230, dy=230, size=56)
    # baño y iones
    badge(C, ctx, t, T("lo bañan") + 0.3, T("los átomos") - 0.1, "≈ 400 °C", R, size=90)
    label(C, ctx, t, T("los átomos") + 0.1, T("se cambian") + 0.6, "SODIO", A, "na", dx=-60, dy=-150, size=56)
    label(C, ctx, t, T("por otros"), T("que aprietan") + 0.8, "POTASIO", A, "k", dx=60, dy=-170, size=56)
    a0, a1 = T("los átomos"), T("así las grietas")
    if a0 <= t < a1:
        n = int(max(0, min(30, (t - a0 - 0.5) / 2.7 * 30)))
        C.badge(ctx, f"CAMBIADOS {n}/30", W / 2, Y1, win(t, a0, a1), K_COL, size=76)
    badge(C, ctx, t, T("así las grietas") + 1.6, T("debajo va") - 0.1, "✓ CERRADA", G, size=84)
    # capas
    label(C, ctx, t, T("debajo va") + 0.6, T("y la bisagra") - 0.1, "PANTALLA", A, "pant", dx=-230, dy=-60, size=54)
    label(C, ctx, t, T("debajo va") + 0.2, T("y la bisagra") - 0.1, "CRISTAL", A, "cris", dx=-260, dy=-190, size=54)
    label(C, ctx, t, T("y encima") + 0.6, T("y la bisagra") - 0.1, "PLÁSTICO", A, "plas", dx=-220, dy=-330, size=54)
    # bisagra
    badge(C, ctx, t, T("se partiría"), T("así que la bisagra") - 0.05, "✗ 90°", R, size=92)
    label(C, ctx, t, T("en forma"), T("por eso al") - 0.1, "GOTA", A, "gota", dx=-40, dy=-200, size=58)
    badge(C, ctx, t, T("sin aplastarse") - 0.4, T("por eso al") - 0.1, "✓ SIN DAÑO", G, size=80)
    label(C, ctx, t, T("queda un"), T("y ahora") - 0.1, "HUECO", A, "hueco", dx=60, dy=-170, size=58)
    # pruebas
    a0, a1 = T("antes de venderlos") + 0.6, T("y aun así")
    if a0 <= t < a1:
        v = keyed(t, [(a0, 0), (T("pliegues", fin=True), 200000)])
        C.badge(ctx, f"{miles(v)} PLIEGUES", W / 2, Y1, win(t, a0, a1), Y, size=78)
    badge2 = lambda a, b, s, col, k: C.badge(ctx, s, W / 2, Y1 + 145 * k, win(t, a, b), col, size=74) if a <= t < b else None
    badge2(T("si lo abres") + 0.2, T("y aun así"), "100 / DÍA", B, 1)
    a0 = T("son más")
    if a0 <= t < T("y aun así"):
        v = keyed(t, [(a0, 0.0), (T("años", fin=True), 5.5)])
        badge2(a0, T("y aun así"), ("%.1f AÑOS" % v).replace(".", ","), G, 2)
    label(C, ctx, t, T("se nota") + 0.3, DUR + 1, "MARCA", A, "marca", dx=0, dy=-200, size=62)


K_COL = (0.75, 0.55, 1.0)


def sfx_events(C):
    E = [(0.05, C.s_whoosh(), 0.45), (1.9, C.s_clank(), 0.35), (4.4, C.s_clank(), 0.35)]
    E += [(T("un cristal normal"), C.s_whoosh(), 0.4), (T("por fuera"), C.s_pop(), 0.4), (T("por dentro"), C.s_pop(), 0.4),
          (T("y aparece") + 0.2, C.s_fail(), 0.45), (T("pero cuanto"), C.s_whoosh(), 0.35), (T("treinta"), C.s_coin(), 0.4),
          (T("un pelo mide"), C.s_pop(), 0.4), (T("para que aguante"), C.s_whoosh(), 0.4), (T("lo bañan") + 0.7, C.s_thud(), 0.4),
          (T("los átomos"), C.s_whoosh(), 0.4), (T("que aprietan"), C.s_buzz(1.0), 0.3), (T("así las grietas") + 1.6, C.s_win(), 0.4),
          (T("debajo va"), C.s_whoosh(), 0.4), (T("con sus millones"), C.s_pop(), 0.4), (T("y encima") + 0.6, C.s_thud(), 0.4),
          (T("de los golpes"), C.s_clank(), 0.4), (T("y la bisagra"), C.s_whoosh(), 0.4), (T("se partiría"), C.s_fail(), 0.5),
          (T("así que la bisagra"), C.s_whoosh(), 0.35), (T("sin aplastarse"), C.s_win(), 0.4), (T("y ahora"), C.s_whoosh(), 0.4),
          (T("doscientos"), C.s_coin(), 0.4), (T("son más"), C.s_coin(), 0.4), (T("se nota"), C.s_pop(), 0.4), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
