# Capa 2D de «¿Por qué no revientan las ruedas de un avión?»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("ruedas")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"avión", "ruedas", "cero", "doscientos", "cincuenta", "segundo", "revientan", "presión", "coche", "dos", "catorce",
            "seis", "aire", "nitrógeno", "oxígeno", "humedad", "arder", "congela", "nailon", "cesta", "llantas", "explotaría",
            "tapones", "funden", "desinfla", "quinientos", "banda", "nueva"}

def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def keyed(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if a <= t <= b: return va + (vb - va) * ss((t - a) / max(b - a, 1e-4))
    return keys[-1][1]
def coma(v, d=1): return (f"%.{d}f" % v).replace(".", ",")

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.75, 1.0)
    BY = H * 0.265
    TD = T("cero") - 0.1
    # 0 → 250 km/h en 1 s
    a0, a1 = 0.25, T("por qué no")
    if a0 <= t < a1:
        v = keyed(t, [(TD, 0), (TD + 1.0, 250)])
        C.badge(ctx, f"{int(v)} km/h", W / 2, BY, win(t, a0, a1), Y, size=96)
        if t > TD:
            s = min(1.0, t - TD)
            C.badge(ctx, coma(s) + " s", W / 2, BY + 150, win(t, TD, a1), (1, 1, 1), size=70)
    # coche 2 bar / avión 14 bar
    a0, a1 = T("la rueda de tu"), T("pero no está")
    if a0 <= t < a1:
        p = win(t, a0 + 0.3, a1)
        x, y = A("coche"); v = keyed(t, [(T("unos dos") - 0.2, 0), (T("unos dos") + 0.6, 2)])
        C.callout(ctx, f"COCHE\n{int(round(v))} BAR", clampx(x, 200), clampy(y - 140), p, size=58)
        if t > T("la de un") - 0.2:
            x, y = A("rueda"); v = keyed(t, [(T("unos catorce") - 0.3, 0), (T("unos catorce") + 0.7, 14)])
            C.callout(ctx, f"AVIÓN\n{int(round(v))} BAR", clampx(x + 60, 260), clampy(y - 110), win(t, T("la de un") - 0.2, a1), size=62)
    # aire → nitrógeno
    label(C, ctx, t, T("pero no está"), T("está llena de nitrógeno"), "AIRE", A, "cav", dx=120, dy=-60, size=62)
    label(C, ctx, t, T("está llena de nitrógeno") + 0.2, T("el aire tiene"), "N2", A, "cav", dx=120, dy=-60, size=72)
    label(C, ctx, t, T("el aire tiene") + 0.3, T("y el agua"), "O2", A, "o2", dx=0, dy=-90, size=60)
    label(C, ctx, t, T("humedad") , T("el nitrógeno no"), "H2O", A, "h2o", dx=0, dy=-90, size=60)
    a0, a1 = T("a diez mil") - 0.1, T("el nitrógeno no") + 0.3
    if a0 <= t < a1:
        C.badge(ctx, "10.000 m", W / 2, BY, win(t, a0, a1), (1, 1, 1), size=86)
        if t > T("se congela") - 0.3:
            C.badge(ctx, "-50 °C", W / 2, BY + 145, win(t, T("se congela") - 0.3, a1), B, size=80)
    a0, a1 = T("así que la presión"), T("pero la goma")
    if a0 <= t < a1:
        C.badge(ctx, "✓ 14 BAR", W / 2, BY, win(t, a0, a1), G, size=90)
    label(C, ctx, t, T("tejido de nailon") - 0.2, T("y aquí viene"), "NAILON", A, "nyl", dx=-60, dy=-80, size=64)
    # al frenar: la presión sube
    a0, a1 = T("al frenar"), T("y cuánto")
    if a0 <= t < a1:
        v = keyed(t, [(a0, 14), (T("explotaría") + 0.3, 21), (T("sueltan el gas"), 21), (T("en vez de reventar") + 0.3, 0)])
        col = R if v > 17 else (Y if v > 2 else G)
        C.badge(ctx, f"{int(round(v))} BAR", W / 2, BY, win(t, a0, a1), col, size=96)
        if T("la rueda explotaría") - 0.1 < t < T("así que la llanta"):
            C.badge(ctx, "✗ REVIENTA", W / 2, BY + 150, win(t, T("la rueda explotaría") - 0.1, T("así que la llanta")), R, size=74)
    label(C, ctx, t, T("las llantas se") , T("si la presión"), "LLANTA", A, "llanta", dx=-160, dy=60, size=62)
    label(C, ctx, t, T("unos tapones") - 0.1, T("y la rueda se"), "TAPÓN", A, "tapon", dx=60, dy=-160, size=62)
    # 500 aterrizajes
    a0, a1 = T("unos quinientos") - 0.2, T("le quitan")
    if a0 <= t < a1:
        n = keyed(t, [(a0, 0), (T("aterrizajes", fin=True) + 0.3, 500)])
        C.badge(ctx, f"× {int(n)}", W / 2, BY, win(t, a0, a1), Y, size=96)
    label(C, ctx, t, T("le quitan") + 0.1, T("le pegan"), "GASTADA", A, "banda", dx=-80, dy=-130, size=60)
    label(C, ctx, t, T("le pegan") + 0.7, DUR - 0.6, "NUEVA", A, "banda", dx=-60, dy=-130, size=64)

def sfx_events(C):
    TD = T("cero") - 0.1
    E = [(0.0, C.s_whoosh(), 0.45), (TD, C.s_thud(), 0.6), (TD + 0.05, C.s_buzz(1.0), 0.25), (T("en un segundo"), C.s_pop(), 0.4),
         (T("vamos a mirar"), C.s_whoosh(), 0.45), (T("vamos a mirar") + 0.9, C.s_clank(), 0.45),
         (T("unos dos"), C.s_pop(), 0.4), (T("unos catorce"), C.s_pop(), 0.45), (T("está llena de nitrógeno"), C.s_coin(), 0.4),
         (T("el oxígeno puede"), C.s_buzz(1.2), 0.3), (T("se congela"), C.s_clank(), 0.35), (T("así que la presión"), C.s_win(), 0.35)]
    for k in range(4): E.append((T("capas y capas") - 0.6 + 0.45 * k, C.s_thud(), 0.35))
    E += [(T("cruzadas"), C.s_whoosh(), 0.35), (T("al frenar"), C.s_buzz(2.0), 0.3), (T("la rueda explotaría"), C.s_fail(), 0.4),
          (T("que se funden"), C.s_buzz(1.2), 0.25), (T("sueltan el gas"), C.s_whoosh(1.2), 0.4), (T("en vez de reventar"), C.s_win(), 0.4),
          (T("unos quinientos"), C.s_coin(), 0.35), (T("le quitan"), C.s_whoosh(), 0.4), (T("le pegan") + 0.8, C.s_thud(), 0.45),
          (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
