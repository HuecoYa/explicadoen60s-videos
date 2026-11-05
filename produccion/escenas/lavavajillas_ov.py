# Capa 2D de «Si tuvieras que inventar el lavavajillas…»
from _ovbase import *
from marcas import cargar
T, DUR = cargar("lavavajillas")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"lavavajillas", "platos", "caja", "agua", "diez", "litros", "sesenta", "bomba", "brazos", "agujeritos", "inclinados",
            "chorro", "brazo", "aspersor", "grasa", "resistencia", "grados", "filtro", "cal", "manchas", "resina", "sal", "bolitas",
            "gotas", "marcas", "abrillantador", "capa", "aire", "evaporan", "condensa", "paredes", "frías"}

def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def keyed(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if a <= t <= b: return va + (vb - va) * ss((t - a) / max(b - a, 1e-4))
    return keys[-1][1]

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.75, 1.0)
    Yb = H * 0.265
    # litros: lavavajillas frente a fregar a mano
    a0, a1 = T("solo unos"), T("pero el agua quieta")
    if a0 - 0.2 <= t < a1:
        v = keyed(t, [(a0, 0), (T("litros", fin=True), 10)])
        C.badge(ctx, f"LAVAVAJILLAS {int(round(v))} L", W / 2, Yb, win(t, a0 - 0.2, a1), B, size=74)
    a0 = T("fregando")
    if a0 <= t < T("pero el agua quieta"):
        v = keyed(t, [(a0, 0), (T("sesenta", fin=True), 60)])
        C.badge(ctx, f"A MANO {int(round(v))} L", W / 2, Yb + 125, win(t, a0, T("pero el agua quieta")), R, size=74)
    label(C, ctx, t, T("pero el agua quieta") + 0.3, T("así que pones"), "SUCIO", A, "plato", dx=0, dy=-230, size=62)
    label(C, ctx, t, T("bomba") - 0.1, T("y fíjate"), "BOMBA", A, "bomba", dx=0, dy=230, size=62)
    label(C, ctx, t, T("brazos"), T("y fíjate"), "BRAZO", A, "brazo", dx=-60, dy=-130, size=58)
    badge(C, ctx, t, T("nadie"), T("los agujeros"), "0 MOTORES", Y, size=80)
    label(C, ctx, t, T("los agujeros") + 0.3, T("pero el agua fría"), "CHORRO", A, "noz", dx=0, dy=-150, size=58)
    label(C, ctx, t, T("empuja") + 0.2, T("pero el agua fría"), "EMPUJE", A, "noz2", dx=0, dy=-150, size=58)
    # temperatura
    a0, a1 = T("pero el agua fría"), T("y la misma")
    if a0 <= t < a1:
        v = keyed(t, [(a0, 20), (T("hasta sesenta") - 0.4, 20), (T("grados", fin=True), 65)])
        col = tuple(b + (r - b) * (v - 20) / 45 for b, r in zip(B, R))
        C.badge(ctx, f"{int(round(v))} °C", W / 2, Yb, win(t, a0, a1), col, size=96)
    label(C, ctx, t, T("no quita") , T("así que una"), "GRASA", A, "plato", dx=-230, dy=-60, size=60)
    label(C, ctx, t, T("resistencia") - 0.1, T("y la misma"), "RESISTENCIA", A, "resist", dx=0, dy=130, size=56)
    a0 = T("más de lo")
    if a0 <= t < T("y la misma"):
        C.badge(ctx, "TUS MANOS ~45 °C", W / 2, Yb + 135, win(t, a0, T("y la misma")), Y, size=62)
    # recirculación
    a0, a1 = T("y la misma"), T("pero el agua del")
    if a0 <= t < a1:
        n = 1 + int(max(0, t - a0) / 0.8)
        C.badge(ctx, f"VUELTA {n}", W / 2, Yb, win(t, a0, a1), B, size=80)
    label(C, ctx, t, T("pasando"), T("pero el agua del"), "FILTRO", A, "filtro", dx=60, dy=130, size=58)
    # cal y resina
    label(C, ctx, t, T("lleva cal") - 0.1, T("así que añades"), "CAL", A, "tubo", dx=150, dy=-90, size=64)
    label(C, ctx, t, T("y deja") + 0.2, T("así que añades"), "MANCHAS", A, "manchas", dx=40, dy=-200, size=56)
    label(C, ctx, t, T("resina") - 0.1, T("y la sal"), "RESINA", A, "tanque", dx=230, dy=0, size=60)
    a0, a1 = T("bolitas") + 0.2, T("pero al secarse")
    if a0 <= t < a1:
        v = keyed(t, [(a0, 0), (a0 + 2.2, 100), (T("sirve") + 0.4, 100), (T("sirve") + 2.0, 0)])
        C.badge(ctx, f"CAL ATRAPADA {int(round(v))} %", W / 2, Yb, win(t, a0, a1), Y, size=70)
    label(C, ctx, t, T("y la sal"), T("pero al secarse"), "SAL", A, "sal", dx=-230, dy=140, size=62)
    # gotas y abrillantador
    label(C, ctx, t, T("las gotas"), T("así que en el"), "GOTAS", A, "plato", dx=0, dy=-240, size=60)
    label(C, ctx, t, T("abrillantador") - 0.1, T("hace que"), "ABRILLANTADOR", A, "dosif", dx=-120, dy=-110, size=54)
    badge(C, ctx, t, T("sin formar"), T("y por último"), "✓ SIN MARCAS", G, size=78)
    # secado
    badge(C, ctx, t, T("muchos"), T("los platos calientes"), "✗ VENTILADOR", R, size=78)
    label(C, ctx, t, T("los platos calientes"), T("y se condensa"), "VAPOR", A, "plato", dx=0, dy=-250, size=60)
    label(C, ctx, t, T("y se condensa") + 0.4, DUR + 1, "GOTAS", A, "pared", dx=170, dy=-60, size=58)

def sfx_events(C):
    E = [(0.05, C.s_whoosh(), 0.4), (0.1, C.s_buzz(4.5), 0.25)]
    E += [(T("lo primero"), C.s_whoosh(), 0.45), (T("una caja"), C.s_thud(), 0.45), (T("solo unos"), C.s_coin(), 0.4),
          (T("fregando"), C.s_coin(), 0.4), (T("no limpia"), C.s_fail(), 0.4), (T("bomba"), C.s_clank(), 0.45),
          (T("lanza"), C.s_buzz(3.0), 0.25), (T("brazos"), C.s_pop(), 0.4), (T("los agujeros"), C.s_whoosh(), 0.35),
          (T("gira solo"), C.s_buzz(1.8), 0.3), (T("no quita"), C.s_fail(), 0.4), (T("resistencia"), C.s_pop(), 0.4),
          (T("grados"), C.s_coin(), 0.45), (T("y la misma"), C.s_whoosh(), 0.35), (T("pasando"), C.s_pop(), 0.4),
          (T("y deja"), C.s_fail(), 0.4), (T("resina"), C.s_pop(), 0.45), (T("atrapan"), C.s_coin(), 0.4),
          (T("y la sal"), C.s_whoosh(), 0.4), (T("vuelvan"), C.s_win(), 0.4), (T("dejan marcas"), C.s_fail(), 0.4),
          (T("abrillantador"), C.s_pop(), 0.4), (T("sin formar"), C.s_win(), 0.4), (T("muchos"), C.s_fail(), 0.35),
          (T("evaporan"), C.s_whoosh(), 0.35), (T("y se condensa"), C.s_pop(), 0.4), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
