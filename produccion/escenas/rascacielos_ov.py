# Capa 2D de «¿Y si construyes un rascacielos?»
from _ovbase import *
from marcas import cargar
T, DUR = cargar("rascacielos")
SUB_Y = 0.72
KEYWORDS = {"rascacielos", "hormigón", "hunde", "pilotes", "roca", "núcleo", "ascensores", "vertebral", "viento", "balancea",
            "bola", "péndulo", "inercia", "frena", "taipéi", "toneladas", "agua", "depósitos", "bombas", "cristal"}

def overlay(ctx, t, A, C):
    Y, R, G = C.YL, C.RED, C.GREEN
    badge(C, ctx, t, 0.3, T("empiezas") - 0.1, "400 m", Y, size=110)
    badge(C, ctx, t, T("hunde") + 0.3, T("así que excavas"), "✗ SE HUNDE", R, size=86)
    label(C, ctx, t, T("pilotes"), T("ahora el peso") + 1.0, "PILOTES", A, "pilotes", dx=-150, dy=-120, size=64)
    label(C, ctx, t, T("roca dura") - 0.2, T("subes plantas"), "ROCA", A, "roca", dy=-60, size=64)
    label(C, ctx, t, T("núcleo"), T("pero a esa") - 0.1, "NÚCLEO", A, "nucleo", dx=140, dy=-60, size=64)
    badge(C, ctx, t, T("se balancea") + 0.2, T("así que haces") - 0.1, "≈ 1 m DE BALANCEO", R, size=62)
    label(C, ctx, t, T("una bola"), T("taipéi") - 0.2, "PÉNDULO", A, "bola", dy=-300, size=66)
    badge(C, ctx, t, T("taipéi"), T("seiscientas") - 0.05, "TAIPEI 101", Y, size=86)
    badge(C, ctx, t, T("seiscientas"), T("y se puede"), "660 t", Y, size=120)
    badge(C, ctx, t, T("y se puede"), T("aún queda") - 0.1, "PLANTAS 87-92", Y, size=76)
    label(C, ctx, t, T("pones depósitos"), T("y por fuera") - 0.1, "DEPÓSITO + BOMBA", A, "tanque", dx=-160, dy=-120, size=54)
    badge(C, ctx, t, T("piel de cristal"), T("sígueme") - 0.1, "PIEL DE CRISTAL", (0.55, 0.8, 0.95), size=74)

def sfx_events(C):
    E = [(0.2, C.s_whoosh(), 0.4)]
    for k in range(6): E.append((T("apilando") + 0.25 * k, C.s_clank(), 0.25))
    E.append((T("hunde") + 0.3, C.s_thud(), 0.8)); E.append((T("pilotes"), C.s_thud(), 0.6)); E.append((T("pilotes") + 0.5, C.s_thud(), 0.5))
    E.append((T("subes plantas"), C.s_whoosh(1.6), 0.6)); E.append((T("núcleo"), C.s_pop(), 0.5))
    E.append((T("el viento"), C.s_whoosh(2.0), 0.7)); E.append((T("cuelgas"), C.s_clank(), 0.5)); E.append((T("frena"), C.s_win(), 0.5))
    E.append((T("seiscientas"), C.s_pop(), 0.6)); E.append((T("pones depósitos"), C.s_pop(), 0.45)); E.append((T("piel de cristal"), C.s_whoosh(), 0.5))
    E.append((T("sígueme"), C.s_whoosh(), 0.4))
    return E
