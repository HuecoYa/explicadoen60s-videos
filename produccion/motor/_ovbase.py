W, H = 1080, 1920
def clampx(x, m=260): return max(m, min(W - m, x))
def clampy(y, lo=330, hi=1150): return max(lo, min(hi, y))
def win(t, a, b, fade=0.15):
    if t < a or t > b: return 0.0
    return min(1.0, (t - a) / 0.22) * min(1.0, (b - t) / fade)
def label(C, ctx, t, a, b, text, A, key, dx=0, dy=-220, size=68):
    p = win(t, a, b)
    if p:
        x, y = A(key); C.callout(ctx, text, clampx(x + dx), clampy(y + dy), p, size=size)
def badge(C, ctx, t, a, b, text, col, size=70):
    p = win(t, a, b)
    if p: C.badge(ctx, text, W / 2, H * 0.165, p, col, size=size)
