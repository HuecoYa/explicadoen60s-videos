"""Gestiona la cola de publicaciones (se usa desde un ordenador con `gh` autenticado).

  python3 programador/cola.py nuevo termo --mp4 termo.mp4 --mp4-tiktok termo_tiktok.mp4 \
      --titulo "Así funciona un termo" --texto "Descripción…" --tags "termo,física" \
      --tiktok "2026-11-03 10:00" --instagram "2026-11-05 18:00" --youtube "2026-11-05 16:00"
  python3 programador/cola.py lista
  python3 programador/cola.py quitar termo-youtube
  python3 programador/cola.py mover termo-youtube "2026-11-06 12:00"
Después: git add/commit/push del calendario.
"""
import argparse, subprocess, datetime as dt, sys
from pathlib import Path

from comun import leer_calendario, guardar_calendario, MADRID, REPO, TAG_VIDEOS


def fecha(s):
    return dt.datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=MADRID).isoformat()


def gh(*args):
    return subprocess.run(["gh", *args, "-R", REPO], check=True, capture_output=True, text=True).stdout


def subir(ruta, nombre):
    if subprocess.run(["gh", "release", "view", TAG_VIDEOS, "-R", REPO], capture_output=True).returncode:
        gh("release", "create", TAG_VIDEOS, "--title", "Vídeos para publicar", "--notes",
           "Almacén de vídeos del programador. No borrar.")
    gh("release", "upload", TAG_VIDEOS, str(ruta), "--clobber")  # el asset toma el nombre del archivo
    return nombre


def nuevo(a):
    cal = leer_calendario()
    ids = {p["id"] for p in cal["posts"]}
    videos = {}
    for red in ("tiktok", "instagram", "youtube"):
        hora = getattr(a, red)
        if not hora:
            continue
        pid = f"{a.nombre}-{red}"
        if pid in ids and not a.reemplazar:
            sys.exit(f"{pid} ya existe (usa --reemplazar)")
        src = a.mp4_tiktok if (red == "tiktok" and a.mp4_tiktok) else a.mp4
        destino = f"{a.nombre}_tiktok.mp4" if (red == "tiktok" and a.mp4_tiktok) else f"{a.nombre}.mp4"
        if destino not in videos:
            ruta = Path(src)
            if ruta.name != destino:
                tmp = Path("/tmp") / destino
                tmp.write_bytes(ruta.read_bytes()); ruta = tmp
            videos[destino] = subir(ruta, destino)
        cal["posts"] = [p for p in cal["posts"] if p["id"] != pid]
        cal["posts"].append({"id": pid, "red": red, "hora": fecha(hora), "video": destino, "titulo": a.titulo,
                             "texto": a.texto, "tags": [t.strip() for t in a.tags.split(",") if t.strip()],
                             "estado": "pendiente", "intentos": 0})
        print("programado", pid, hora)
    guardar_calendario(cal)


def lista(_):
    ahora = dt.datetime.now(MADRID)
    for p in leer_calendario()["posts"]:
        h = dt.datetime.fromisoformat(p["hora"]).astimezone(MADRID)
        if p["estado"] == "pendiente" or h > ahora - dt.timedelta(days=2):
            print(f"{h:%a %d/%m %H:%M}  {p['red']:9}  {p['estado']:9}  {p['id']}")


def quitar(a):
    cal = leer_calendario(); n = len(cal["posts"])
    cal["posts"] = [p for p in cal["posts"] if p["id"] != a.id]
    guardar_calendario(cal); print("quitado" if len(cal["posts"]) < n else "no encontrado")


def mover(a):
    cal = leer_calendario()
    for p in cal["posts"]:
        if p["id"] == a.id:
            p["hora"] = fecha(a.hora); p["estado"] = "pendiente"; p["intentos"] = 0
            guardar_calendario(cal); print("movido"); return
    print("no encontrado")


ap = argparse.ArgumentParser()
sub = ap.add_subparsers(required=True)
n = sub.add_parser("nuevo"); n.set_defaults(f=nuevo)
n.add_argument("nombre"); n.add_argument("--mp4", required=True); n.add_argument("--mp4-tiktok")
n.add_argument("--titulo", required=True); n.add_argument("--texto", required=True); n.add_argument("--tags", default="")
for r in ("tiktok", "instagram", "youtube"):
    n.add_argument(f"--{r}", help="AAAA-MM-DD HH:MM (hora de Madrid)")
n.add_argument("--reemplazar", action="store_true")
sub.add_parser("lista").set_defaults(f=lista)
q = sub.add_parser("quitar"); q.add_argument("id"); q.set_defaults(f=quitar)
m = sub.add_parser("mover"); m.add_argument("id"); m.add_argument("hora"); m.set_defaults(f=mover)
a = ap.parse_args(); a.f(a)
