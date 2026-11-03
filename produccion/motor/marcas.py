"""Tiempos de las palabras de la voz, para sincronizar escena y textos con lo que se dice.

    from marcas import cargar
    T, DUR = cargar("lata")
    T("aluminio")            # segundo en que empieza la primera vez que se dice «aluminio»
    T("la tapa", 2)          # segunda vez que se dice «la tapa»
    T("cúpula", fin=True)    # segundo en que termina la palabra
Las palabras se comparan sin tildes ni signos y por prefijo («hormig» encuentra «hormigón»).
"""
import json, os, re, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))


def _norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    return re.sub(r"[^a-z0-9ñ]", "", "".join(c for c in w if unicodedata.category(c) != "Mn"))


def cargar(nombre):
    d = json.load(open(os.path.join(HERE, f"{nombre}_words.json"), encoding="utf-8"))
    W = [(a, b, _norm(w)) for a, b, w in d["words"]]

    def T(clave, n=1, fin=False):
        k = [_norm(x) for x in clave.split() if _norm(x)]
        c = 0
        for i in range(len(W) - len(k) + 1):
            if all(W[i + j][2].startswith(k[j]) for j in range(len(k))):
                c += 1
                if c == n:
                    return W[i + len(k) - 1][1] if fin else W[i][0]
        raise KeyError(f"«{clave}» (vez {n}) no aparece en la voz de {nombre}")

    return T, d["dur"]
