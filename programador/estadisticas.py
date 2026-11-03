"""Recoge estadísticas de las tres cuentas y de cada vídeo → estadisticas.json (lo lee el panel).
Lo ejecuta GitHub cada 6 horas. Cada red es independiente: si una falla, las demás se guardan igual."""
import json, os, traceback, datetime as dt
from pathlib import Path

import requests

from comun import leer_tokens, guardar_tokens, ahora, MADRID, RAIZ
from redes import REDES, IG_VERSION

SALIDA = RAIZ / "estadisticas.json"


def _ok(r):
    if r.status_code >= 400:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")
    return r.json()


# ── YouTube ──
def youtube(tok):
    h = {"Authorization": f"Bearer {tok['access_token']}"}
    ch = _ok(requests.get("https://www.googleapis.com/youtube/v3/channels", headers=h, timeout=60,
                          params={"part": "statistics,snippet,contentDetails", "mine": "true"}))["items"][0]
    st = ch["statistics"]
    cuenta = {"nombre": ch["snippet"]["title"], "seguidores": int(st.get("subscriberCount", 0)),
              "vistas": int(st.get("viewCount", 0)), "videos": int(st.get("videoCount", 0))}
    uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, token = [], None
    while len(ids) < 200:
        r = _ok(requests.get("https://www.googleapis.com/youtube/v3/playlistItems", headers=h, timeout=60,
                             params={"part": "contentDetails", "playlistId": uploads, "maxResults": 50, **({"pageToken": token} if token else {})}))
        ids += [i["contentDetails"]["videoId"] for i in r["items"]]
        token = r.get("nextPageToken")
        if not token:
            break
    videos = []
    for i in range(0, len(ids), 50):
        r = _ok(requests.get("https://www.googleapis.com/youtube/v3/videos", headers=h, timeout=60,
                             params={"part": "statistics,snippet", "id": ",".join(ids[i:i + 50])}))
        for v in r["items"]:
            s = v["statistics"]
            videos.append({"id": v["id"], "titulo": v["snippet"]["title"], "fecha": v["snippet"]["publishedAt"],
                           "url": f"https://youtube.com/shorts/{v['id']}", "vistas": int(s.get("viewCount", 0)),
                           "likes": int(s.get("likeCount", 0)), "comentarios": int(s.get("commentCount", 0))})
    return cuenta, videos


# ── Instagram ──
def instagram(tok):
    G, at, uid = f"https://graph.facebook.com/{IG_VERSION}", tok["access_token"], tok["user_id"]
    if "graph.instagram.com" in getattr(REDES["instagram"], "G", ""):
        G = f"https://graph.instagram.com/{IG_VERSION}"
    u = _ok(requests.get(f"{G}/{uid}", timeout=60, params={"fields": "username,followers_count,follows_count,media_count", "access_token": at}))
    cuenta = {"nombre": "@" + u.get("username", ""), "seguidores": u.get("followers_count", 0), "videos": u.get("media_count", 0)}
    videos, url = [], f"{G}/{uid}/media"
    params = {"fields": "id,caption,media_type,timestamp,permalink,like_count,comments_count", "limit": 50, "access_token": at}
    while url and len(videos) < 200:
        r = _ok(requests.get(url, params=params, timeout=60))
        for m in r.get("data", []):
            v = {"id": m["id"], "titulo": (m.get("caption") or "").split("\n")[0][:90], "fecha": m.get("timestamp"),
                 "url": m.get("permalink"), "likes": m.get("like_count", 0), "comentarios": m.get("comments_count", 0)}
            try:  # requiere el permiso instagram_manage_insights
                ins = _ok(requests.get(f"{G}/{m['id']}/insights", timeout=60,
                                       params={"metric": "views,reach,saved,shares", "access_token": at}))
                for x in ins.get("data", []):
                    v[{"views": "vistas", "reach": "alcance", "saved": "guardados", "shares": "compartidos"}[x["name"]]] = x["values"][0]["value"]
            except Exception:
                pass
            videos.append(v)
        url, params = r.get("paging", {}).get("next"), None
    cuenta["vistas"] = sum(v.get("vistas", 0) for v in videos)
    return cuenta, videos


# ── TikTok ──
def tiktok(tok):
    h = {"Authorization": f"Bearer {tok['access_token']}"}
    u = _ok(requests.get("https://open.tiktokapis.com/v2/user/info/", headers=h, timeout=60,
                         params={"fields": "display_name,follower_count,following_count,likes_count,video_count"}))["data"]["user"]
    cuenta = {"nombre": u.get("display_name", ""), "seguidores": u.get("follower_count", 0), "likes": u.get("likes_count", 0),
              "videos": u.get("video_count", 0)}
    videos, cursor = [], None
    campos = "id,title,video_description,create_time,share_url,view_count,like_count,comment_count,share_count"
    while len(videos) < 200:
        r = _ok(requests.post(f"https://open.tiktokapis.com/v2/video/list/?fields={campos}", headers=h, timeout=60,
                              json={"max_count": 20, **({"cursor": cursor} if cursor else {})}))["data"]
        for v in r.get("videos", []):
            videos.append({"id": v["id"], "titulo": (v.get("title") or v.get("video_description") or "")[:90],
                           "fecha": dt.datetime.fromtimestamp(v["create_time"], dt.timezone.utc).isoformat(), "url": v.get("share_url"),
                           "vistas": v.get("view_count", 0), "likes": v.get("like_count", 0),
                           "comentarios": v.get("comment_count", 0), "compartidos": v.get("share_count", 0)})
        if not r.get("has_more"):
            break
        cursor = r.get("cursor")
    cuenta["vistas"] = sum(v["vistas"] for v in videos)
    return cuenta, videos


RECOGER = {"youtube": youtube, "instagram": instagram, "tiktok": tiktok}


def main():
    previo = json.loads(SALIDA.read_text(encoding="utf-8")) if SALIDA.exists() else {}
    out = {"actualizado": ahora().isoformat(), "cuentas": {}, "videos": {}, "errores": {},
           "historial": previo.get("historial", [])}
    tokens, cambios = leer_tokens(), False
    for red, fn in RECOGER.items():
        try:
            r = REDES[red]
            if hasattr(r, "preparar"):
                tok = r.preparar()
            elif red in tokens:
                tok = r.refrescar(tokens[red])
                if tok != tokens[red]:
                    tokens[red] = tok; cambios = True
            else:
                raise RuntimeError("no conectado")
            out["cuentas"][red], out["videos"][red] = fn(tok)
        except Exception as e:
            traceback.print_exc()
            out["errores"][red] = str(e)[:300]
            if red in previo.get("cuentas", {}):  # conserva el último dato bueno
                out["cuentas"][red] = previo["cuentas"][red]; out["videos"][red] = previo.get("videos", {}).get(red, [])
    if cambios:
        guardar_tokens({n: t for n, t in tokens.items() if not hasattr(REDES[n], "preparar")})
    hoy = ahora().astimezone(MADRID).date().isoformat()
    foto = {"fecha": hoy, **{f"{r}_{k}": c.get(k, 0) for r, c in out["cuentas"].items() for k in ("seguidores", "vistas", "videos")}}
    out["historial"] = [h for h in out["historial"] if h["fecha"] != hoy][-179:] + [foto]
    SALIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({r: c for r, c in out["cuentas"].items()}, ensure_ascii=False), out["errores"])


if __name__ == "__main__":
    main()
