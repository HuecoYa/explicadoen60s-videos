"""Utilidades compartidas: calendario, tokens cifrados y descarga de vídeos."""
import json, os, base64, hashlib, datetime as dt
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from cryptography.fernet import Fernet

RAIZ = Path(__file__).resolve().parent
CALENDARIO = RAIZ / "calendario.json"
TOKENS = RAIZ / "tokens.enc"
MADRID = ZoneInfo("Europe/Madrid")
REPO = os.environ.get("GITHUB_REPOSITORY", "explicadoen60s/explicadoen60s.github.io")
TAG_VIDEOS = "videos"
HASHTAG_CUENTA = "#explicadoen60s"


def ahora():
    return dt.datetime.now(dt.timezone.utc)


def leer_calendario():
    if not CALENDARIO.exists():
        return {"posts": []}
    return json.loads(CALENDARIO.read_text(encoding="utf-8"))


def guardar_calendario(cal):
    cal["posts"].sort(key=lambda p: (p["hora"], p["red"]))
    CALENDARIO.write_text(json.dumps(cal, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def _fernet():
    clave = os.environ.get("CLAVE_TOKENS")
    if not clave:
        raise SystemExit("Falta el secreto CLAVE_TOKENS")
    # Cualquier contraseña larga sirve: se convierte en una clave de cifrado.
    return Fernet(base64.urlsafe_b64encode(hashlib.sha256(clave.encode()).digest()))


def leer_tokens():
    if not TOKENS.exists():
        return {}
    return json.loads(_fernet().decrypt(TOKENS.read_bytes()))


def guardar_tokens(tok):
    TOKENS.write_bytes(_fernet().encrypt(json.dumps(tok).encode()))


def secreto(nombre):
    v = os.environ.get(nombre, "").strip()
    if not v:
        raise RuntimeError(f"Falta el secreto {nombre} en GitHub")
    return v


def url_video(nombre):
    """URL pública del vídeo (asset del release 'videos', o URL completa)."""
    if nombre.startswith("http"):
        return nombre
    return f"https://github.com/{REPO}/releases/download/{TAG_VIDEOS}/{nombre}"


def url_directa(nombre):
    """Sigue las redirecciones de GitHub y devuelve la URL final descargable (para Instagram)."""
    r = requests.get(url_video(nombre), allow_redirects=False, timeout=60)
    if r.status_code in (301, 302, 303, 307, 308):
        return r.headers["Location"]
    r.raise_for_status()
    return url_video(nombre)


def descargar_video(nombre, destino="/tmp"):
    ruta = Path(destino) / Path(nombre).name
    if ruta.exists():
        return ruta
    with requests.get(url_video(nombre), stream=True, timeout=300) as r:
        r.raise_for_status()
        with open(ruta, "wb") as f:
            for trozo in r.iter_content(1 << 20):
                f.write(trozo)
    return ruta


def hashtags(tags, extra=()):
    out = ["#" + t.replace(" ", "") for t in tags] + [HASHTAG_CUENTA, *extra]
    vistos, res = set(), []
    for h in out:
        if h.lower() not in vistos:
            vistos.add(h.lower()); res.append(h)
    return " ".join(res)


def texto_completo(post, extra=()):
    return f"{post['texto']}\n\n{hashtags(post.get('tags', []), extra)}".strip()
