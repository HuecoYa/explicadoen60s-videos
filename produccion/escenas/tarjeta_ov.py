# Elementos gráficos puntuales: "Inventa la tarjeta del banco"
SUB_Y = 0.63
KEYWORDS = {"tarjeta", "relieve", "copiarlo", "banda", "magnética", "clonada", "chip", "ingenioso", "ordenador", "clave", "secreta",
            "código", "nuevo", "nada", "pin", "antena", "pila", "energía", "centímetros", "pequeños", "ladrón"}
W, H = 1080, 1920

def clampx(x, m=260): return max(m, min(W - m, x))
def clampy(y, lo=330, hi=1060): return max(lo, min(hi, y))
def win(t, a, b, fade=0.15):
    if t < a or t > b: return 0.0
    return min(1.0, (t - a) / 0.22) * min(1.0, (b - t) / fade)

def label(C, ctx, t, a, b, text, A, key, dx=0, dy=-220, size=68):
    p = win(t, a, b)
    if p:
        x, y = A(key); C.callout(ctx, text, clampx(x + dx), clampy(y + dy), p, size=size)

def strike(ctx, cx, cy, w, p):
    ctx.save(); ctx.set_line_width(10); ctx.set_source_rgba(0.95, 0.2, 0.2, p)
    ctx.move_to(cx - w / 2, cy + 18); ctx.line_to(cx + w / 2, cy - 18); ctx.stroke(); ctx.restore()

def overlay(ctx, t, A, C):
    G, R, Wt, Y = C.GREEN, C.RED, (1, 1, 1), C.YL
    label(C, ctx, t, 6.0, 8.7, "RELIEVE", A, "nums", dy=-200)
    label(C, ctx, t, 11.0, 12.9, "PAPEL DE CALCO", A, "paper", dy=-260, size=60)
    label(C, ctx, t, 15.3, 16.6, "COPIA", A, "clone1", dy=-170)
    label(C, ctx, t, 18.0, 20.0, "BANDA\nMAGNÉTICA", A, "stripe", dy=-230, size=64)
    label(C, ctx, t, 29.9, 31.2, "CLONADA", A, "clone2", dy=-190)
    label(C, ctx, t, 31.9, 33.6, "CHIP", A, "chip", dy=-190, size=80)
    label(C, ctx, t, 36.4, 39.5, "CLAVE\nSECRETA", A, "key", dx=120, dy=-330, size=70)
    label(C, ctx, t, 52.3, 55.0, "ANTENA", A, "ant", dy=-260, size=76)
    # códigos de cada compra
    codes = [(40.9, "7F3A9"), (41.9, "K2Q8D"), (42.9, "M91XZ")]
    if 40.9 <= t < 44.4:
        cur = [c for a, c in codes if t >= a][-1]
        C.badge(ctx, f"CÓDIGO {cur}", W / 2, H * 0.165, win(t, 40.9, 44.4), G)
    p = win(t, 44.7, 46.9)
    if p:
        C.badge(ctx, "CÓDIGO 7F3A9", W / 2, H * 0.165, p, R)
        if t > 45.4: strike(ctx, W / 2, H * 0.165, 520, min(1, (t - 45.4) / 0.2))
    # PIN
    if 48.0 <= t < 50.6:
        n = sum(1 for a in (48.2, 48.6, 49.0, 49.4) if t >= a)
        C.badge(ctx, "PIN " + " ".join(["•"] * n + ["_"] * (4 - n)), W / 2, H * 0.165, win(t, 48.0, 50.6), G if t >= 50.0 else Wt)
    # sin pila
    p = win(t, 55.4, 56.6)
    if p:
        x, y = A("bat"); ctx.save(); ctx.set_line_width(18); ctx.set_source_rgba(0.95, 0.2, 0.2, p); ctx.set_line_cap(1)
        for d in (1, -1):
            ctx.move_to(x - 110, y - 110 * d); ctx.line_to(x + 110, y + 110 * d)
        ctx.stroke(); ctx.restore()
    # distancia
    p = win(t, 61.4, 63.8)
    if p: C.badge(ctx, "≈ 4 cm", W / 2, H * 0.165, p, Y, size=80)
    p = win(t, 68.3, 71.2)
    if p: C.badge(ctx, "SIN PIN: HASTA 50 €", W / 2, H * 0.165, p, Y)

def sfx_events(C):
    E = []
    for t in (2.2, 8.9, 13.0, 16.8, 19.9, 22.3, 26.6, 30.6, 33.0, 39.9, 46.8, 50.8, 56.9, 63.9, 66.4, 71.0):
        E.append((t, C.s_whoosh(), 0.45))
    for k in range(6): E.append((2.75 + k * 0.07, C.s_coin(), 0.3))
    E.append((4.55, C.s_thud(), 0.5)); E.append((31.6, C.s_pop(), 0.8))
    for t in (6.0, 11.0, 15.3, 18.0, 29.9, 31.9, 36.4, 52.3, 61.4, 68.3):
        E.append((t, C.s_pop(), 0.5))
    E.append((10.4, C.s_buzz(1.9), 0.6))
    for t in (21.65, 28.45, 41.0, 42.0, 43.0, 50.0, 62.6, 65.5):
        E.append((t, C.s_bleep(1568), 3.0))
    E.append((45.45, C.s_fail(), 1.0))
    for t in (48.2, 48.6, 49.0, 49.4):
        E.append((t, C.s_bleep(880), 1.5))
    E.append((58.0, C.s_buzz(5.8), 0.5))
    E.append((62.65, C.s_win(), 0.7))
    return E
