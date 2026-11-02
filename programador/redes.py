"""Conexión y publicación en YouTube, Instagram y TikTok mediante sus APIs oficiales."""
import json, time, urllib.parse, datetime as dt

import requests

from comun import secreto, descargar_video, url_directa, texto_completo, ahora

CALLBACK = "https://huecoya.github.io/explicadoen60s-videos/callback.html"
IG_VERSION = "v23.0"


def _ok(r):
    if r.status_code >= 400:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:500]}")
    return r


def _caduca(segundos):
    return (ahora() + dt.timedelta(seconds=int(segundos) - 120)).isoformat()


def _vigente(tok):
    return tok.get("access_token") and tok.get("caduca", "") > ahora().isoformat()


# ───────────────────────────── YouTube ─────────────────────────────
class YouTube:
    nombre = "youtube"

    def conectar(self, code):
        r = _ok(requests.post("https://oauth2.googleapis.com/token", data={
            "code": code, "client_id": secreto("YT_CLIENT_ID"), "client_secret": secreto("YT_CLIENT_SECRET"),
            "redirect_uri": CALLBACK, "grant_type": "authorization_code"}, timeout=60)).json()
        if "refresh_token" not in r:
            raise RuntimeError("Google no devolvió refresh_token; vuelve a conectar (el enlace ya pide prompt=consent)")
        return {"refresh_token": r["refresh_token"], "access_token": r["access_token"], "caduca": _caduca(r["expires_in"])}

    def refrescar(self, tok):
        if _vigente(tok):
            return tok
        r = _ok(requests.post("https://oauth2.googleapis.com/token", data={
            "refresh_token": tok["refresh_token"], "client_id": secreto("YT_CLIENT_ID"),
            "client_secret": secreto("YT_CLIENT_SECRET"), "grant_type": "refresh_token"}, timeout=60)).json()
        return {**tok, "access_token": r["access_token"], "caduca": _caduca(r["expires_in"])}

    def publicar(self, post, tok):
        ruta = descargar_video(post["video"])
        cuerpo = {
            "snippet": {"title": post["titulo"][:100], "description": texto_completo(post, ("#shorts",)),
                        "tags": post.get("tags", []), "categoryId": "27", "defaultLanguage": "es"},
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False},
        }
        tam = ruta.stat().st_size
        r = _ok(requests.post(
            "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
            headers={"Authorization": f"Bearer {tok['access_token']}", "Content-Type": "application/json; charset=UTF-8",
                     "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(tam)},
            data=json.dumps(cuerpo), timeout=60))
        destino = r.headers["Location"]
        with open(ruta, "rb") as f:
            r = _ok(requests.put(destino, data=f, headers={"Content-Type": "video/mp4", "Content-Length": str(tam)}, timeout=900))
        vid = r.json()["id"]
        return {"id": vid, "url": f"https://youtube.com/shorts/{vid}"}


# ───────────────────────────── Instagram ─────────────────────────────
class Instagram:
    nombre = "instagram"
    G = f"https://graph.instagram.com/{IG_VERSION}"

    def conectar(self, code):
        code = code.split("#")[0]
        r = _ok(requests.post("https://api.instagram.com/oauth/access_token", data={
            "client_id": secreto("IG_APP_ID"), "client_secret": secreto("IG_APP_SECRET"),
            "grant_type": "authorization_code", "redirect_uri": CALLBACK, "code": code}, timeout=60)).json()
        corto = r["access_token"]
        r = _ok(requests.get("https://graph.instagram.com/access_token", params={
            "grant_type": "ig_exchange_token", "client_secret": secreto("IG_APP_SECRET"), "access_token": corto}, timeout=60)).json()
        largo = r["access_token"]
        yo = _ok(requests.get(f"{self.G}/me", params={"fields": "user_id,username", "access_token": largo}, timeout=60)).json()
        return {"access_token": largo, "caduca": _caduca(r["expires_in"]), "user_id": yo["user_id"],
                "usuario": yo.get("username"), "renovado": ahora().isoformat()}

    def refrescar(self, tok):
        # El token dura 60 días; se renueva cada semana para que nunca caduque.
        hace = ahora() - dt.datetime.fromisoformat(tok.get("renovado", "2000-01-01T00:00:00+00:00"))
        if hace < dt.timedelta(days=7):
            return tok
        r = _ok(requests.get("https://graph.instagram.com/refresh_access_token", params={
            "grant_type": "ig_refresh_token", "access_token": tok["access_token"]}, timeout=60)).json()
        return {**tok, "access_token": r["access_token"], "caduca": _caduca(r["expires_in"]), "renovado": ahora().isoformat()}

    def publicar(self, post, tok):
        uid, at = tok["user_id"], tok["access_token"]
        base = {"media_type": "REELS", "caption": texto_completo(post), "share_to_feed": "true", "access_token": at}
        # 1º: subida directa del archivo (no depende de URLs externas); si falla, por URL.
        try:
            r = _ok(requests.post(f"{self.G}/{uid}/media", data={**base, "upload_type": "resumable"}, timeout=120)).json()
            ruta = descargar_video(post["video"]); tam = ruta.stat().st_size
            with open(ruta, "rb") as f:
                _ok(requests.post(r["uri"], data=f, timeout=900, headers={
                    "Authorization": f"OAuth {at}", "offset": "0", "file_size": str(tam)}))
        except Exception as e:
            print("Instagram: subida directa no disponible, uso URL:", str(e)[:200])
            r = _ok(requests.post(f"{self.G}/{uid}/media", data={**base, "video_url": url_directa(post["video"])},
                                  timeout=120)).json()
        cid = r["id"]
        for _ in range(60):  # hasta 10 minutos procesando
            time.sleep(10)
            st = _ok(requests.get(f"{self.G}/{cid}", params={"fields": "status_code,status", "access_token": at}, timeout=60)).json()
            if st.get("status_code") == "FINISHED":
                break
            if st.get("status_code") in ("ERROR", "EXPIRED"):
                raise RuntimeError(f"Instagram no pudo procesar el vídeo: {st}")
        else:
            raise RuntimeError("Instagram tardó demasiado en procesar el vídeo")
        r = _ok(requests.post(f"{self.G}/{uid}/media_publish", data={"creation_id": cid, "access_token": at}, timeout=120)).json()
        info = requests.get(f"{self.G}/{r['id']}", params={"fields": "permalink", "access_token": at}, timeout=60).json()
        return {"id": r["id"], "url": info.get("permalink", "")}


# ───────────────────────────── TikTok ─────────────────────────────
class TikTok:
    """Sube el vídeo a la bandeja de TikTok (borrador). Con la app auditada, cambiar a publicación directa."""
    nombre = "tiktok"

    def _token(self, data):
        r = _ok(requests.post("https://open.tiktokapis.com/v2/oauth/token/", data={
            "client_key": secreto("TT_CLIENT_KEY"), "client_secret": secreto("TT_CLIENT_SECRET"), **data},
            headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=60)).json()
        if "access_token" not in r:
            raise RuntimeError(f"TikTok rechazó el token: {r}")
        return {"access_token": r["access_token"], "caduca": _caduca(r["expires_in"]),
                "refresh_token": r["refresh_token"], "open_id": r.get("open_id")}

    def conectar(self, code):
        return self._token({"code": urllib.parse.unquote(code), "grant_type": "authorization_code", "redirect_uri": CALLBACK})

    def refrescar(self, tok):
        if _vigente(tok):
            return tok
        return {**tok, **self._token({"grant_type": "refresh_token", "refresh_token": tok["refresh_token"]})}

    def publicar(self, post, tok):
        ruta = descargar_video(post["video"])
        tam = ruta.stat().st_size
        h = {"Authorization": f"Bearer {tok['access_token']}", "Content-Type": "application/json; charset=UTF-8"}
        r = _ok(requests.post("https://open.tiktokapis.com/v2/post/publish/inbox/video/init/", headers=h, json={
            "source_info": {"source": "FILE_UPLOAD", "video_size": tam, "chunk_size": tam, "total_chunk_count": 1}},
            timeout=60)).json()
        if r.get("error", {}).get("code", "ok") != "ok":
            raise RuntimeError(f"TikTok: {r['error']}")
        pid, subida = r["data"]["publish_id"], r["data"]["upload_url"]
        with open(ruta, "rb") as f:
            _ok(requests.put(subida, data=f, headers={"Content-Type": "video/mp4", "Content-Length": str(tam),
                                                       "Content-Range": f"bytes 0-{tam - 1}/{tam}"}, timeout=900))
        estado = ""
        for _ in range(30):
            time.sleep(5)
            s = requests.post("https://open.tiktokapis.com/v2/post/publish/status/fetch/", headers=h,
                              json={"publish_id": pid}, timeout=60).json()
            estado = s.get("data", {}).get("status", "")
            if estado in ("SEND_TO_USER_INBOX", "PUBLISH_COMPLETE"):
                break
            if estado == "FAILED":
                raise RuntimeError(f"TikTok falló al procesar: {s.get('data')}")
        return {"id": pid, "estado": estado, "borrador": True}


REDES = {c.nombre: c() for c in (YouTube, Instagram, TikTok)}
