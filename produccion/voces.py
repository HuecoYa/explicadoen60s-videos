"""Genera la voz de todos los guiones aprobados (estado «aprobado» → «voz»). Lo ejecuta GitHub al aprobar en el panel."""
import json, sys, traceback
from pathlib import Path
import voz

EST = Path(__file__).resolve().parent / "estado.json"
est = json.loads(EST.read_text(encoding="utf-8"))
hechos = 0
for v in est["videos"]:
    if v.get("estado") != "aprobado":
        continue
    try:
        (voz.ESCENAS / f"{v['id']}.txt").write_text(v["guion"].strip() + "\n", encoding="utf-8")
        voz.generar(v["id"])
        v["estado"] = "voz"; v.pop("error", None); hechos += 1
    except Exception as e:
        traceback.print_exc(); v["error"] = f"Voz: {str(e)[:300]}"
EST.write_text(json.dumps(est, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("voces generadas:", hechos)
