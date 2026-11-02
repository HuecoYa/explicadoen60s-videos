"""Lo ejecuta GitHub Actions cada 10 minutos: publica lo que toca y actualiza el calendario."""
import os, sys, traceback, datetime as dt

import requests

from comun import (leer_calendario, guardar_calendario, leer_tokens, guardar_tokens, ahora, MADRID,
                   texto_completo, url_video, REPO, RAIZ)
from redes import REDES

ADELANTO = dt.timedelta(minutes=3)      # puede salir hasta 3 min antes de la hora
MAX_RETRASO = dt.timedelta(hours=12)    # si se pasó más de esto, no se publica (avisa)
MAX_INTENTOS = 3
AVISAR_A = "@HuecoYa"


def issue(titulo, cuerpo):
    tk = os.environ.get("GITHUB_TOKEN")
    if not tk:
        print("(sin GITHUB_TOKEN, aviso no enviado)", titulo); return
    requests.post(f"https://api.github.com/repos/{REPO}/issues", timeout=60,
                  headers={"Authorization": f"Bearer {tk}", "Accept": "application/vnd.github+json"},
                  json={"title": titulo, "body": cuerpo})


def hora_local(p):
    return dt.datetime.fromisoformat(p["hora"]).astimezone(MADRID)


def escribir_resumen(cal):
    fil = ["# 📅 Calendario de publicaciones", "",
           "_Horas de Madrid. Se actualiza solo cuando algo cambia._", "",
           "| Fecha | Hora | Red | Vídeo | Estado |", "|---|---|---|---|---|"]
    iconos = {"pendiente": "⏳ pendiente", "publicado": "✅ publicado", "borrador": "📲 en tu bandeja de TikTok",
              "error": "❌ error", "caducado": "⚠️ no se publicó a tiempo"}
    limite = ahora() - dt.timedelta(days=3)
    for p in cal["posts"]:
        h = hora_local(p)
        if h < limite and p["estado"] != "pendiente":
            continue
        est = iconos.get(p["estado"], p["estado"])
        url = (p.get("resultado") or {}).get("url")
        if url:
            est = f"[{est}]({url})"
        dia = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"][h.weekday()]
        fil.append(f"| {dia} {h:%d/%m} | {h:%H:%M} | {p['red']} | {p['titulo'][:60]} | {est} |")
    (RAIZ.parent / "CALENDARIO.md").write_text("\n".join(fil) + "\n", encoding="utf-8")


def main():
    cal = leer_calendario()
    tokens = leer_tokens()
    cambios_tokens = False
    t = ahora()
    for p in cal["posts"]:
        if p["estado"] != "pendiente":
            continue
        h = dt.datetime.fromisoformat(p["hora"])
        if h - ADELANTO > t:
            continue
        if t - h > MAX_RETRASO:
            p["estado"] = "caducado"
            issue(f"⚠️ No se publicó: {p['titulo']} ({p['red']})",
                  f"{AVISAR_A} La publicación de las {hora_local(p):%d/%m %H:%M} no salió a tiempo. Reprográmala.")
            continue
        red = REDES[p["red"]]
        try:
            if hasattr(red, "preparar") and p["red"] not in tokens:
                tokens[p["red"]] = red.preparar()  # en memoria; el token vive en el secreto IG_TOKEN
            if p["red"] not in tokens:
                raise RuntimeError(f"{p['red']} no está conectado (ver programador/LEEME.md)")
            nuevo = red.refrescar(tokens[p["red"]])
            if nuevo != tokens[p["red"]]:
                tokens[p["red"]] = nuevo; cambios_tokens = True
            res = red.publicar(p, nuevo)
            p["resultado"] = res
            p["publicado"] = ahora().isoformat()
            if res.get("borrador"):
                p["estado"] = "borrador"
                issue(f"📲 TikTok listo para publicar: {p['titulo']}",
                      f"{AVISAR_A} El vídeo ya está en tu bandeja de TikTok (notificaciones → borradores).\n"
                      f"Ábrelo, pega este texto y publica:\n\n```\n{texto_completo(p)}\n```\n\n"
                      f"Vídeo: {url_video(p['video'])}\n\nCierra este aviso cuando lo hayas publicado.")
            else:
                p["estado"] = "publicado"
            print(f"OK {p['red']} {p['titulo']}: {res}")
        except Exception as e:
            p["intentos"] = p.get("intentos", 0) + 1
            p["ultimo_error"] = str(e)[:400]
            traceback.print_exc()
            if p["intentos"] >= MAX_INTENTOS:
                p["estado"] = "error"
                issue(f"❌ Error publicando en {p['red']}: {p['titulo']}",
                      f"{AVISAR_A} Tras {MAX_INTENTOS} intentos no se pudo publicar.\n\n```\n{p['ultimo_error']}\n```")
    # el token de Instagram caduca a los 60 días: se renueva aunque no haya publicaciones
    for nombre, tok in [(n, t) for n, t in tokens.items() if n == "instagram"]:
        try:
            nuevo = REDES[nombre].refrescar(tok)
            if nuevo != tok:
                tokens[nombre] = nuevo; cambios_tokens = True
        except Exception as e:
            print(f"No se pudo renovar {nombre}: {e}", file=sys.stderr)
    if cambios_tokens:
        guardar_tokens({n: t for n, t in tokens.items() if not hasattr(REDES[n], "preparar")})
    guardar_calendario(cal)
    escribir_resumen(cal)


def probar():
    """Comprueba cada red sin publicar nada y deja el resultado en CONEXIONES.md."""
    tokens = leer_tokens()
    lineas = ["# Estado de las conexiones", "", f"_Comprobado: {ahora().astimezone(MADRID):%d/%m/%Y %H:%M}_", ""]
    for nombre, red in REDES.items():
        try:
            if hasattr(red, "preparar"):
                tok = red.preparar(); extra = f"cuenta @{tok.get('usuario')}"
            elif nombre in tokens:
                tok = red.refrescar(tokens[nombre]); tokens[nombre] = tok; extra = "permiso válido"
            else:
                raise RuntimeError("no conectado")
            lineas.append(f"- ✅ **{nombre}**: {extra}")
        except Exception as e:
            lineas.append(f"- ❌ **{nombre}**: {str(e)[:300]}")
    guardar_tokens({n: t for n, t in tokens.items() if not hasattr(REDES[n], "preparar")})
    (RAIZ.parent / "CONEXIONES.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print("\n".join(lineas))


if __name__ == "__main__":
    probar() if "--probar" in sys.argv else main()
