# Capa 2D de «¿Y si construyes una piscina?»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("piscina")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"piscina", "excavas", "agujero", "ocho", "cuatro", "metro", "desmorona", "malla", "acero", "hormigón", "presión",
            "cuarenta", "litros", "toneladas", "verde", "circular", "sumidero", "ventanitas", "bomba", "arena", "suciedad",
            "boquillas", "filtro", "bacterias", "cloro", "medidor", "flotando", "llueve", "empuja", "peso", "levantarse",
            "romperse", "válvula"}

def miles(v): return f"{int(round(v)):,}".replace(",", ".")

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.75, 1.0)
    a0 = T("de ocho")
    if a0 - 0.2 <= t < T("pero la tierra"):
        p = win(t, a0 - 0.2, T("pero la tierra"))
        txt = "8 m"
        if t > T("por cuatro"): txt += " × 4 m"
        if t > T("y metro y medio"): txt += " × 1,5 m"
        C.badge(ctx, txt, W / 2, H * 0.265, p, Y, size=84)
    badge(C, ctx, t, T("se desmorona"), T("así que pones"), "✗ SE DERRUMBA", R, size=84)
    label(C, ctx, t, T("una malla") + 0.2, T("proyectas"), "ACERO", A, "malla", dx=0, dy=-160, size=62)
    label(C, ctx, t, T("proyectas") + 0.2, T("ahora tienes"), "HORMIGÓN", A, "fondo", dx=120, dy=150, size=60)
    badge(C, ctx, t, T("una sola pieza") - 0.2, T("la llenas"), "✓ SIN JUNTAS", G, size=80)
    a0, a1 = T("la llenas"), T("pero el agua quieta")
    if a0 <= t < a1:
        p = win(t, a0, a1); v = 48000 * min(1, max(0, (t - a0) / (T("son cuarenta") - a0)))
        C.badge(ctx, miles(v) + " L", W / 2, H * 0.265, p, B, size=96)
        if t > T("son cuarenta"):
            q = win(t, T("son cuarenta"), a1); C.badge(ctx, "= 48 t", W / 2, H * 0.265 + 150, q, Y, size=88)
    a0, a1 = T("en pocos días"), T("así que la haces")
    if a0 <= t < a1:
        d = 1 + int(min(4, 5 * (t - a0) / max(0.5, T("se vuelve verde", fin=True) - a0)))
        C.badge(ctx, f"DÍA {d}", W / 2, H * 0.265, win(t, a0, a1), G, size=90)
    label(C, ctx, t, T("un sumidero"), T("una bomba"), "SUMIDERO", A, "sumidero", dx=0, dy=160, size=56)
    label(C, ctx, t, T("esas ventanitas"), T("una bomba"), "SKIMMER", A, "skimmer", dx=-40, dy=-150, size=56)
    label(C, ctx, t, T("una bomba"), T("lleno de arena"), "BOMBA", A, "bomba", dx=-60, dy=-160, size=58)
    label(C, ctx, t, T("lleno de arena"), T("y vuelve limpia"), "ARENA", A, "filtro", dx=-40, dy=-120, size=58)
    label(C, ctx, t, T("las boquillas") - 0.2, T("cada día"), "BOQUILLAS", A, "boquilla", dx=170, dy=-130, size=54)
    a0, a1 = T("cada día"), T("pero la arena")
    if a0 <= t < a1:
        v = 1 + int(min(3, 4 * (t - a0) / 2.6)); C.badge(ctx, f"× {v} AL DÍA", W / 2, H * 0.265, win(t, a0, a1), B, size=90)
    badge(C, ctx, t, T("no mata") - 0.2, T("así que añades"), "✗ BACTERIAS", R, size=84)
    a0, a1 = T("así que añades"), T("y ahora")
    if a0 <= t < a1:
        v = 0.2 + 0.8 * min(1, max(0, (t - a0) / 1.6)); s = ("%.1f" % v).replace(".", ",")
        C.badge(ctx, f"CLORO {s} mg/L", W / 2, H * 0.265, win(t, a0, a1), G if v > 0.95 else Y, size=80)
    label(C, ctx, t, T("y un medidor") - 0.2, T("y ahora"), "CLORADOR", A, "cloro", dx=-150, dy=0, size=54)
    label(C, ctx, t, T("el agua bajo"), T("con la piscina"), "AGUA\nDEL SUBSUELO", A, "freatico", dx=60, dy=-150, size=54)
    badge(C, ctx, t, T("con la piscina llena") + 0.3, T("pero si la vacías"), "✓ 48 t LA SUJETAN", G, size=74)
    badge(C, ctx, t, T("y romperse"), T("así que en el"), "✗ SE ROMPE", R, size=90)
    label(C, ctx, t, T("pones una válvula"), T("por eso nunca"), "VÁLVULA", A, "valvula", dx=60, dy=-170, size=62)
    badge(C, ctx, t, T("se abre") + 0.3, T("por eso nunca") + 0.3, "✓ PRESIÓN IGUALADA", G, size=72)

def sfx_events(C):
    E = [(0.05, C.s_thud(), 0.5), (1.4, C.s_thud(), 0.45), (T("excavas"), C.s_whoosh(), 0.4), (T("se desmorona"), C.s_fail(), 0.5),
         (T("una malla"), C.s_clank(), 0.5), (T("proyectas"), C.s_buzz(2.5), 0.4), (T("una sola pieza"), C.s_pop(), 0.4),
         (T("la llenas"), C.s_whoosh(1.4), 0.5), (T("son cuarenta"), C.s_pop(), 0.5), (T("se vuelve verde"), C.s_fail(), 0.4),
         (T("una bomba"), C.s_buzz(2.0), 0.35), (T("y vuelve limpia"), C.s_whoosh(), 0.4), (T("añades cloro"), C.s_pop(), 0.45),
         (T("el dato curioso"), C.s_whoosh(), 0.4), (T("si llueve"), C.s_whoosh(1.5), 0.4), (T("y romperse"), C.s_clank(), 0.6),
         (T("pones una válvula"), C.s_pop(), 0.45), (T("se abre"), C.s_clank(), 0.5), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
