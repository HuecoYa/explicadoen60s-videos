"""Recoge señales de tendencia en España → tendencias_raw.json. Claude las analiza en su pasada diaria
(produccion/tendencias.json) y el panel lo enseña en «Tendencias».
Fuentes (todas públicas y gratis):
  · Google Trends: búsquedas que están subiendo hoy en España (RSS oficial).
  · Wikipedia en español: artículos más leídos ayer (la gente busca «cómo funciona…» ahí).
  · YouTube: vídeos más populares en España (general, ciencia y tecnología, educación).
  · Competencia en YouTube: canales que se vigilan (produccion/objetivos.json → "competencia").
Cada fuente es independiente: si una falla, las demás se guardan."""
import json, re, traceback, datetime as dt
import xml.etree.ElementTree as ET

import requests

from comun import RAIZ, ahora, leer_tokens, guardar_tokens
from redes import REDES

SALIDA = RAIZ / "tendencias_raw.json"
OBJETIVOS = RAIZ.parent / "produccion" / "objetivos.json"
UA = {"User-Agent": "explicadoen60s-panel/1.0 (tendencias; contacto: explicadoen60s.cxn@gmail.com)"}
NS = {"ht": "https://trends.google.com/trending/rss"}


def google_trends():
    r = requests.get("https://trends.google.com/trending/rss?geo=ES", headers=UA, timeout=60)
    r.raise_for_status()
    raiz = ET.fromstring(r.content)
    out = []
    for it in raiz.iter("item"):
        g = lambda tag: (it.findtext(tag, default="", namespaces=NS) or "").strip()
        noticias = [{"titulo": (n.findtext("ht:news_item_title", default="", namespaces=NS) or "").strip(),
                     "url": n.findtext("ht:news_item_url", default="", namespaces=NS),
                     "fuente": n.findtext("ht:news_item_source", default="", namespaces=NS)}
                    for n in it.findall("ht:news_item", NS)]
        trafico = g("ht:approx_traffic")
        out.append({"tema": it.findtext("title", default="").strip(), "busquedas": trafico,
                    "busquedas_n": int(re.sub(r"\D", "", trafico) or 0), "fecha": it.findtext("pubDate", default=""),
                    "imagen": g("ht:picture"), "noticias": noticias[:3]})
    return out


def wikipedia():
    ayer = (ahora() - dt.timedelta(days=1)).strftime("%Y/%m/%d")
    r = requests.get(f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/es.wikipedia/all-access/{ayer}", headers=UA, timeout=60)
    r.raise_for_status()
    fuera = ("Especial:", "Wikipedia:", "Anexo:", "Portal:", "Ayuda:", "Categoría:", "Archivo:")
    art = [a for a in r.json()["items"][0]["articles"] if not a["article"].startswith(fuera) and a["article"] not in ("Wikipedia", "Main_Page")]
    return [{"tema": a["article"].replace("_", " "), "lecturas": a["views"], "url": f"https://es.wikipedia.org/wiki/{a['article']}"} for a in art[:40]]


def youtube_populares(tok):
    h = {"Authorization": f"Bearer {tok['access_token']}"}
    out = {}
    for nombre, cat in (("general", None), ("ciencia_tecnologia", "28"), ("educacion", "27")):
        p = {"part": "snippet,statistics,contentDetails", "chart": "mostPopular", "regionCode": "ES", "maxResults": 25}
        if cat:
            p["videoCategoryId"] = cat
        r = requests.get("https://www.googleapis.com/youtube/v3/videos", headers=h, params=p, timeout=60)
        if r.status_code >= 400:
            out[nombre] = {"error": r.text[:200]}; continue
        out[nombre] = [{"titulo": v["snippet"]["title"], "canal": v["snippet"]["channelTitle"],
                        "vistas": int(v["statistics"].get("viewCount", 0)), "likes": int(v["statistics"].get("likeCount", 0) or 0),
                        "duracion": v["contentDetails"].get("duration"), "fecha": v["snippet"]["publishedAt"],
                        "url": f"https://www.youtube.com/watch?v={v['id']}"} for v in r.json().get("items", [])]
    return out


def competencia(tok, canales):
    h = {"Authorization": f"Bearer {tok['access_token']}"}
    out = []
    for c in canales:
        c = c.strip().lstrip("@")
        if not c:
            continue
        r = requests.get("https://www.googleapis.com/youtube/v3/channels", headers=h, timeout=60,
                         params={"part": "snippet,statistics,contentDetails", "forHandle": "@" + c})
        items = r.json().get("items", []) if r.ok else []
        if not items:
            out.append({"canal": c, "error": "no encontrado"}); continue
        ch = items[0]; st = ch["statistics"]
        up = ch["contentDetails"]["relatedPlaylists"]["uploads"]
        pl = requests.get("https://www.googleapis.com/youtube/v3/playlistItems", headers=h, timeout=60,
                          params={"part": "contentDetails", "playlistId": up, "maxResults": 10}).json()
        ids = [i["contentDetails"]["videoId"] for i in pl.get("items", [])]
        vids = []
        if ids:
            vr = requests.get("https://www.googleapis.com/youtube/v3/videos", headers=h, timeout=60,
                              params={"part": "snippet,statistics", "id": ",".join(ids)}).json()
            vids = [{"titulo": v["snippet"]["title"], "fecha": v["snippet"]["publishedAt"], "vistas": int(v["statistics"].get("viewCount", 0)),
                     "url": f"https://youtube.com/shorts/{v['id']}"} for v in vr.get("items", [])]
        out.append({"canal": "@" + c, "nombre": ch["snippet"]["title"], "seguidores": int(st.get("subscriberCount", 0)),
                    "vistas": int(st.get("viewCount", 0)), "videos": int(st.get("videoCount", 0)), "ultimos": vids})
    return out


def main():
    out = {"actualizado": ahora().isoformat(), "errores": {}}
    for nombre, fn in (("google_trends", google_trends), ("wikipedia", wikipedia)):
        try:
            out[nombre] = fn()
        except Exception as e:
            traceback.print_exc(); out["errores"][nombre] = str(e)[:300]
    try:
        tokens = leer_tokens()
        tok = REDES["youtube"].refrescar(tokens["youtube"])
        if tok != tokens["youtube"]:
            tokens["youtube"] = tok; guardar_tokens(tokens)
        out["youtube"] = youtube_populares(tok)
        canales = json.loads(OBJETIVOS.read_text(encoding="utf-8")).get("competencia", []) if OBJETIVOS.exists() else []
        if canales:
            out["competencia"] = competencia(tok, canales)
    except Exception as e:
        traceback.print_exc(); out["errores"]["youtube"] = str(e)[:300]
    SALIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print({k: len(v) if isinstance(v, list) else "ok" for k, v in out.items() if k != "errores"}, out["errores"])


if __name__ == "__main__":
    main()
