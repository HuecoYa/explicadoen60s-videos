"""Voces de los guiones aprobados (estado «aprobado» → «voz»). Lo ejecuta GitHub al aprobar en el panel.
  python3 voces.py lista                → ids aprobados (JSON)
  python3 voces.py generar <id>         → escribe escenas/<id>.txt y escenas/<id>.mp3
  python3 voces.py marcar <id> [<id>…]  → pone en «voz» los que tengan mp3 (y anota error en los demás)
"""
import json, sys, traceback
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
EST = RAIZ / "estado.json"


def leer():
    return json.loads(EST.read_text(encoding="utf-8"))


def guardar(est):
    EST.write_text(json.dumps(est, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


acc = sys.argv[1] if len(sys.argv) > 1 else "todo"
if acc == "lista":
    print(json.dumps([v["id"] for v in leer()["videos"] if v.get("estado") == "aprobado"]))
elif acc == "generar":
    import voz
    vid = sys.argv[2]
    v = next(x for x in leer()["videos"] if x["id"] == vid)
    (voz.ESCENAS / f"{vid}.txt").write_text(v["guion"].strip() + "\n", encoding="utf-8")
    voz.generar(vid)
elif acc == "marcar":
    est = leer()
    for v in est["videos"]:
        if v["id"] in sys.argv[2:] and v.get("estado") == "aprobado":
            if (RAIZ / "escenas" / f"{v['id']}.mp3").exists():
                v["estado"] = "voz"; v.pop("error", None)
            else:
                v["error"] = "Voz: falló la generación (ver Actions → Generar voces)"
    guardar(est)
